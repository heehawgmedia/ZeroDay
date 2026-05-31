#!/usr/bin/env python3
"""
Jarvis background poller — runs health checks, PageSpeed, and Sentry on all
monitored sites and writes results to data/poll_cache.json.

Run alongside the web server:
  python -m worker.poller

Schedule (defaults, configurable via .env):
  Health checks  — every POLL_INTERVAL_SECONDS     (default: 300s / 5 min)
  Sentry         — every SENTRY_INTERVAL_SECONDS   (default: 900s / 15 min)
  PageSpeed      — every PAGESPEED_INTERVAL_SECONDS (default: 3600s / 1 hr)
"""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Allow running as `python worker/poller.py` from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.cache import cache
from backend.config import settings
from backend.monitoring import (
    check_site_health,
    _fetch_project_issues,
    _run_pagespeed,
    _utcnow,
    _sentry_headers,
)
from backend.sites import site_registry


def _log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)


def _stale(url: str, check_type: str, interval: int) -> bool:
    """Return True if the cached data is older than interval seconds."""
    data = cache.get_site(url).get(check_type, {})
    last = data.get("checked_at")
    if not last:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
        elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
        return elapsed >= interval
    except ValueError:
        return True


def poll_health(site: dict) -> None:
    url = site["url"]
    try:
        result = check_site_health(url)
        cache.update(url, "health", result)
        status = result.get("status", "?").upper()
        ms = result.get("response_ms")
        ssl_days = result.get("ssl_days")
        details = f"{ms}ms" if ms is not None else "no response"
        if ssl_days is not None:
            details += f"  SSL {ssl_days}d"
        _log(f"  {status:8s} {url}  ({details})")
    except Exception as exc:
        _log(f"  ERROR    {url}  health check failed: {exc}")
        cache.update(url, "health", {"url": url, "status": "error", "error": str(exc), "checked_at": _utcnow()})


def poll_pagespeed(site: dict) -> None:
    url = site["url"]
    if not _stale(url, "pagespeed", settings.pagespeed_interval_seconds):
        return
    try:
        desktop = _run_pagespeed(url, "desktop")
        mobile = _run_pagespeed(url, "mobile")
        result = {
            "url": url,
            "desktop": desktop,
            "mobile": mobile,
            "checked_at": _utcnow(),
        }
        cache.update(url, "pagespeed", result)
        _log(f"  PageSpeed {url}  desktop={desktop['score']} mobile={mobile['score']}")
    except Exception as exc:
        _log(f"  PageSpeed {url}  failed: {exc}")


def poll_sentry(site: dict) -> None:
    if not settings.sentry_auth_token or not settings.sentry_org:
        return
    url = site["url"]
    project = site.get("sentry_project") or settings.sentry_project
    if not project:
        return
    if not _stale(url, "sentry", settings.sentry_interval_seconds):
        return
    try:
        import requests as _requests
        base = "https://sentry.io/api/0"
        headers = _sentry_headers()
        result = _fetch_project_issues(base, headers, settings.sentry_org, project, limit=10)
        cache.update(url, "sentry", result)
        _log(
            f"  Sentry   {url}  {result.get('unresolved_count', 0)} unresolved "
            f"/ {result.get('errors_last_24h', 0)} errors (24h)"
        )
    except Exception as exc:
        _log(f"  Sentry   {url}  failed: {exc}")


def run_cycle() -> None:
    sites = [s for s in site_registry.list_sites() if s.get("enabled", True)]
    if not sites:
        _log("No active sites. Add a site via the dashboard or chat.")
        return

    _log(f"Polling {len(sites)} site(s)…")
    for site in sites:
        poll_health(site)
        poll_pagespeed(site)
        poll_sentry(site)
    _log("Cycle complete.")


def main() -> None:
    interval = settings.poll_interval_seconds
    _log(
        f"Jarvis Poller started  "
        f"health={interval}s  "
        f"sentry={settings.sentry_interval_seconds}s  "
        f"pagespeed={settings.pagespeed_interval_seconds}s"
    )
    _log("First run starting now…")
    run_cycle()

    while True:
        _log(f"Sleeping {interval}s until next health poll…")
        time.sleep(interval)
        run_cycle()


if __name__ == "__main__":
    main()
