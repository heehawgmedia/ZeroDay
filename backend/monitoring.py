"""
Monitoring tool implementations: health checks, PageSpeed, Search Console, Sentry.
These are called both by the background poller and by Claude tool-use.
"""

import json
import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

from backend.cache import cache
from backend.config import settings
from backend.sites import site_registry


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Health Check ──────────────────────────────────────────────────────────────

def _ssl_days_remaining(hostname: str) -> int | None:
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as sock:
            sock.settimeout(10)
            sock.connect((hostname, 443))
            cert = sock.getpeercert()
            expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
            return (expiry - datetime.utcnow()).days
    except Exception:
        return None


def check_site_health(url: str) -> dict:
    import time as _time
    start = _time.monotonic()
    result: dict = {"url": url, "checked_at": _utcnow()}
    try:
        resp = requests.get(
            url, timeout=15, allow_redirects=True,
            headers={"User-Agent": "Jarvis-Monitor/1.0"},
        )
        elapsed_ms = int((_time.monotonic() - start) * 1000)
        result.update({
            "status": "up" if resp.ok else "degraded",
            "status_code": resp.status_code,
            "response_ms": elapsed_ms,
            "redirect_count": len(resp.history),
            "final_url": resp.url if resp.url != url else None,
            "error": None,
        })
    except requests.exceptions.ConnectionError as exc:
        result.update({"status": "down", "error": f"Connection failed: {exc}", "response_ms": None})
    except requests.exceptions.Timeout:
        result.update({"status": "down", "error": "Request timed out", "response_ms": None})
    except Exception as exc:
        result.update({"status": "error", "error": str(exc), "response_ms": None})

    parsed = urlparse(url)
    if parsed.scheme == "https" and result.get("status") != "down":
        result["ssl_days"] = _ssl_days_remaining(parsed.hostname)
    else:
        result["ssl_days"] = None

    return result


def check_site_health_tool(url: str) -> str:
    result = check_site_health(url)
    cache.update(url, "health", result)
    return json.dumps(result, indent=2)


# ── PageSpeed ─────────────────────────────────────────────────────────────────

def _run_pagespeed(url: str, strategy: str) -> dict:
    params: dict = {"url": url, "strategy": strategy, "category": "performance"}
    if settings.pagespeed_api_key:
        params["key"] = settings.pagespeed_api_key
    resp = requests.get(
        "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
        params=params,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    lighthouse = data.get("lighthouseResult", {})
    categories = lighthouse.get("categories", {})
    audits = lighthouse.get("audits", {})

    def num(key: str) -> float | None:
        v = audits.get(key, {}).get("numericValue")
        return round(v / 1000, 2) if v is not None and key not in ("cumulative-layout-shift", "total-blocking-time") else (round(v, 3) if v is not None else None)

    score = int((categories.get("performance", {}).get("score") or 0) * 100)
    return {
        "score": score,
        "lcp_s": num("largest-contentful-paint"),
        "fcp_s": num("first-contentful-paint"),
        "tbt_ms": audits.get("total-blocking-time", {}).get("numericValue"),
        "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
        "speed_index_s": num("speed-index"),
    }


def get_pagespeed(url: str, strategy: str = "both") -> str:
    try:
        if strategy == "both":
            desktop = _run_pagespeed(url, "desktop")
            mobile = _run_pagespeed(url, "mobile")
            result = {"url": url, "desktop": desktop, "mobile": mobile, "checked_at": _utcnow()}
        else:
            scores = _run_pagespeed(url, strategy)
            result = {"url": url, strategy: scores, "checked_at": _utcnow()}
        cache.update(url, "pagespeed", result)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return f"PageSpeed check failed for {url}: {exc}"


# ── Google Search Console ─────────────────────────────────────────────────────

def get_search_console_data(
    site_url: str | None = None,
    start_date: str = "7daysAgo",
    end_date: str = "today",
) -> str:
    if not settings.search_console_credentials_path:
        return (
            "Google Search Console is not configured. "
            "Set SEARCH_CONSOLE_CREDENTIALS_PATH in .env."
        )
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
    except ImportError:
        return "google-api-python-client is not installed. Run: pip install google-api-python-client"

    creds = service_account.Credentials.from_service_account_file(
        settings.search_console_credentials_path,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
    )
    service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    # Resolve relative date strings to actual dates
    from datetime import timedelta, date
    def resolve_date(d: str) -> str:
        if d == "today":
            return date.today().isoformat()
        if d.endswith("daysAgo"):
            n = int(d.replace("daysAgo", ""))
            return (date.today() - timedelta(days=n)).isoformat()
        return d

    start = resolve_date(start_date)
    end = resolve_date(end_date)

    # Auto-detect site URL if not given
    if not site_url:
        if settings.search_console_site_url:
            site_url = settings.search_console_site_url
        else:
            sites_list = service.sites().list().execute()
            entries = sites_list.get("siteEntry", [])
            if not entries:
                return "No sites found in Search Console. Verify the service account has access."
            site_url = entries[0]["siteUrl"]

    def query(dimensions: list[str], row_limit: int = 10) -> list[dict]:
        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": dimensions,
            "rowLimit": row_limit,
        }
        resp = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
        rows = []
        for row in resp.get("rows", []):
            entry = {d: row["keys"][i] for i, d in enumerate(dimensions)}
            entry.update({
                "clicks": row.get("clicks"),
                "impressions": row.get("impressions"),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
            })
            rows.append(entry)
        return rows

    top_queries = query(["query"], 20)
    top_pages = query(["page"], 10)

    # Totals
    totals_body = {"startDate": start, "endDate": end, "dimensions": []}
    totals_resp = service.searchanalytics().query(siteUrl=site_url, body=totals_body).execute()
    totals: dict = {}
    if totals_resp.get("rows"):
        row = totals_resp["rows"][0]
        totals = {
            "clicks": row.get("clicks"),
            "impressions": row.get("impressions"),
            "avg_ctr": round(row.get("ctr", 0) * 100, 2),
            "avg_position": round(row.get("position", 0), 1),
        }

    return json.dumps({
        "site": site_url,
        "period": f"{start} → {end}",
        "totals": totals,
        "top_queries": top_queries,
        "top_pages": top_pages,
    }, indent=2)


# ── Sentry ────────────────────────────────────────────────────────────────────

def _sentry_headers() -> dict:
    return {"Authorization": f"Bearer {settings.sentry_auth_token}"}


def get_sentry_issues(
    org: str | None = None,
    project: str | None = None,
    limit: int = 10,
) -> str:
    if not settings.sentry_auth_token:
        return "Sentry is not configured. Set SENTRY_AUTH_TOKEN in .env."

    org = org or settings.sentry_org
    project = project or settings.sentry_project

    if not org:
        return "Set SENTRY_ORG in .env."

    base = "https://sentry.io/api/0"
    headers = _sentry_headers()

    # List projects if none specified
    if not project:
        proj_resp = requests.get(
            f"{base}/organizations/{org}/projects/",
            headers=headers, timeout=15,
        )
        proj_resp.raise_for_status()
        projects = proj_resp.json()
        results = []
        for p in projects:
            results.append(_fetch_project_issues(base, headers, org, p["slug"], limit))
        return json.dumps(results, indent=2)

    result = _fetch_project_issues(base, headers, org, project, limit)
    return json.dumps(result, indent=2)


def _fetch_project_issues(
    base: str, headers: dict, org: str, project: str, limit: int
) -> dict:
    issues_resp = requests.get(
        f"{base}/projects/{org}/{project}/issues/",
        headers=headers,
        params={"limit": limit, "query": "is:unresolved", "sort": "events"},
        timeout=15,
    )
    if not issues_resp.ok:
        return {"project": project, "error": issues_resp.text}

    issues = issues_resp.json()
    top = [
        {
            "title": i.get("title"),
            "culprit": i.get("culprit"),
            "level": i.get("level"),
            "events": i.get("count"),
            "users": i.get("userCount"),
            "first_seen": (i.get("firstSeen") or "")[:10],
            "last_seen": (i.get("lastSeen") or "")[:10],
            "url": f"https://sentry.io/organizations/{org}/issues/{i.get('id')}/",
        }
        for i in issues
    ]

    # Stats: errors in the last 24h
    stats_resp = requests.get(
        f"{base}/projects/{org}/{project}/stats/",
        headers=headers,
        params={"stat": "received", "resolution": "1h"},
        timeout=15,
    )
    total_24h = 0
    if stats_resp.ok:
        points = stats_resp.json()
        total_24h = sum(p[1] for p in points[-24:]) if points else 0

    return {
        "project": project,
        "unresolved_count": len(issues),
        "errors_last_24h": total_24h,
        "top_issues": top,
        "checked_at": _utcnow(),
    }


# ── Site management tool ──────────────────────────────────────────────────────

def manage_sites(
    action: str,
    url: str | None = None,
    name: str | None = None,
    sentry_project: str | None = None,
) -> str:
    if action == "list":
        sites = site_registry.list_sites()
        if not sites:
            return "No sites are being monitored yet. Use action='add' with a URL to start."
        return json.dumps(sites, indent=2)

    if action == "add":
        if not url:
            return "url is required for action='add'."
        result = site_registry.add_site(url, name=name, sentry_project=sentry_project)
        if "error" in result:
            return result["error"]
        return f"Added {result['url']} to monitoring."

    if action == "remove":
        if not url:
            return "url is required for action='remove'."
        removed = site_registry.remove_site(url.rstrip("/"))
        if removed:
            cache.remove_site(url.rstrip("/"))
            return f"Removed {url} from monitoring."
        return f"{url} was not found in the site list."

    return f"Unknown action '{action}'. Use: list, add, remove."


# ── Dashboard snapshot ────────────────────────────────────────────────────────

def get_monitoring_dashboard() -> str:
    sites = site_registry.list_sites()
    if not sites:
        return "No sites are being monitored. Add a site with manage_sites(action='add', url='...')."

    all_data = cache.read()
    rows = []
    for site in sites:
        url = site["url"]
        site_cache = all_data.get(url, {})
        rows.append({
            "url": url,
            "name": site["name"],
            "enabled": site.get("enabled", True),
            "health": site_cache.get("health"),
            "pagespeed": site_cache.get("pagespeed"),
            "sentry": site_cache.get("sentry"),
        })
    return json.dumps(rows, indent=2)
