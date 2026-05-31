"""
Tool implementations and Claude tool-schema definitions for Jarvis.

Each integration is wrapped defensively — if a library isn't installed or
credentials are missing the tool returns a clear error string rather than
crashing the whole request.
"""

import json
import os
from pathlib import Path
from typing import Any

import requests

from backend.config import settings
from backend.monitoring import (
    check_site_health_tool,
    get_pagespeed,
    get_search_console_data,
    get_sentry_issues,
    manage_sites,
    get_monitoring_dashboard,
)

# ── Tool schema definitions ──────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "get_github_overview",
        "description": (
            "Get a summary of the authenticated user's GitHub repositories "
            "including name, description, open issues, stars, and last push date. "
            "Use this for a high-level project overview."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Max number of repos to return (default 20).",
                    "default": 20,
                }
            },
        },
    },
    {
        "name": "get_github_issues",
        "description": "Get open issues or pull requests for a specific GitHub repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in owner/repo format, e.g. 'octocat/hello-world'.",
                },
                "type": {
                    "type": "string",
                    "enum": ["issues", "pulls"],
                    "description": "Whether to fetch issues or pull requests.",
                    "default": "issues",
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "default": "open",
                },
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["repo"],
        },
    },
    {
        "name": "get_github_commits",
        "description": "Get recent commits for a GitHub repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in owner/repo format.",
                },
                "limit": {"type": "integer", "default": 10},
                "branch": {
                    "type": "string",
                    "description": "Branch name (defaults to default branch).",
                },
            },
            "required": ["repo"],
        },
    },
    {
        "name": "get_analytics_summary",
        "description": (
            "Get a Google Analytics (GA4) summary: active users, sessions, "
            "page views, top pages, and traffic sources for a date range."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD or relative format like '7daysAgo', '30daysAgo'.",
                    "default": "7daysAgo",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date, e.g. 'today' or 'YYYY-MM-DD'.",
                    "default": "today",
                },
            },
        },
    },
    {
        "name": "get_notion_tasks",
        "description": (
            "Get tasks from Notion databases. Returns tasks filtered by status "
            "so you can see what's in progress, todo, or blocked."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status_filter": {
                    "type": "string",
                    "description": "Filter by status value (e.g. 'In Progress', 'Todo'). Leave blank for all.",
                },
                "database_id": {
                    "type": "string",
                    "description": "Specific Notion database ID. Leave blank to query all configured databases.",
                },
            },
        },
    },
    {
        "name": "get_linear_issues",
        "description": (
            "Get issues from Linear. Returns assigned issues, active cycles, "
            "and blockers so you can track sprint progress."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "enum": ["assigned", "active", "all"],
                    "description": "Which issues to fetch.",
                    "default": "assigned",
                },
                "include_completed": {
                    "type": "boolean",
                    "default": False,
                },
            },
        },
    },
    {
        "name": "get_trello_cards",
        "description": (
            "Get cards (tasks) from Trello boards. Shows cards across all boards "
            "or a specific board, with due dates and assigned members."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "board_name": {
                    "type": "string",
                    "description": "Filter by board name (partial match). Leave blank for all boards.",
                },
                "overdue_only": {
                    "type": "boolean",
                    "description": "If true, only return cards with past-due dates.",
                    "default": False,
                },
            },
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a local file. Only paths within the allowed directories are accessible.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative file path to read.",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and directories at a given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list.",
                    "default": ".",
                },
                "show_hidden": {"type": "boolean", "default": False},
            },
        },
    },
    {
        "name": "check_site_health",
        "description": (
            "Check if a website is up. Returns HTTP status code, response time in ms, "
            "SSL certificate days remaining, and redirect info."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL to check, e.g. 'https://mysite.com'.",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "get_pagespeed",
        "description": (
            "Run Google PageSpeed Insights on a URL. Returns performance score (0-100), "
            "Core Web Vitals (LCP, CLS, FCP, TBT) for desktop and/or mobile."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to analyze."},
                "strategy": {
                    "type": "string",
                    "enum": ["both", "desktop", "mobile"],
                    "default": "both",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "get_search_console_data",
        "description": (
            "Get Google Search Console data: total clicks, impressions, average CTR, "
            "average position, top search queries, and top performing pages."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "site_url": {
                    "type": "string",
                    "description": "The site URL as registered in Search Console (e.g. 'https://mysite.com/'). Leave blank to use the default.",
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date: 'YYYY-MM-DD' or '7daysAgo', '30daysAgo'.",
                    "default": "7daysAgo",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date: 'YYYY-MM-DD' or 'today'.",
                    "default": "today",
                },
            },
        },
    },
    {
        "name": "get_sentry_issues",
        "description": (
            "Get unresolved errors from Sentry: top issues by event count, "
            "affected user counts, and total errors in the last 24 hours."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "org": {
                    "type": "string",
                    "description": "Sentry organization slug. Leave blank to use the default.",
                },
                "project": {
                    "type": "string",
                    "description": "Sentry project slug. Leave blank for all projects.",
                },
                "limit": {"type": "integer", "default": 10},
            },
        },
    },
    {
        "name": "manage_sites",
        "description": (
            "Add, remove, or list the websites Jarvis monitors. "
            "Use this when the user asks to start monitoring a new URL, "
            "stop monitoring a site, or see what sites are being watched."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "add", "remove"],
                    "description": "What to do.",
                },
                "url": {
                    "type": "string",
                    "description": "Site URL (required for add/remove).",
                },
                "name": {
                    "type": "string",
                    "description": "Friendly display name for the site (optional for add).",
                },
                "sentry_project": {
                    "type": "string",
                    "description": "Sentry project slug for this specific site (optional).",
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "get_monitoring_dashboard",
        "description": (
            "Get a full monitoring snapshot for all tracked websites: "
            "uptime status, response time, SSL days, PageSpeed scores, and Sentry error counts. "
            "Use this for an overview of all site health."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _gh_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _gh_get(url: str, params: dict | None = None) -> Any:
    r = requests.get(url, headers=_gh_headers(), params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def _require(integration: str, *fields) -> str | None:
    """Return an error string if any required field is falsy."""
    missing = [f for f in fields if not getattr(settings, f, None)]
    if missing:
        return (
            f"{integration} integration is not configured. "
            f"Missing: {', '.join(missing).upper()}. "
            f"Set these in your .env file."
        )
    return None


# ── Tool implementations ──────────────────────────────────────────────────────

def get_github_overview(limit: int = 20) -> str:
    err = _require("GitHub", "github_token")
    if err:
        return err
    username = settings.github_username or "me"
    if username == "me":
        user_data = _gh_get("https://api.github.com/user")
        username = user_data["login"]
    repos = _gh_get(
        f"https://api.github.com/users/{username}/repos",
        params={"per_page": limit, "sort": "pushed", "type": "owner"},
    )
    rows = []
    for r in repos[:limit]:
        rows.append({
            "name": r["full_name"],
            "description": r.get("description") or "",
            "open_issues": r["open_issues_count"],
            "stars": r["stargazers_count"],
            "language": r.get("language") or "–",
            "last_pushed": r["pushed_at"][:10] if r.get("pushed_at") else "–",
            "private": r["private"],
        })
    return json.dumps(rows, indent=2)


def get_github_issues(
    repo: str, type: str = "issues", state: str = "open", limit: int = 20
) -> str:
    err = _require("GitHub", "github_token")
    if err:
        return err
    endpoint = "pulls" if type == "pulls" else "issues"
    items = _gh_get(
        f"https://api.github.com/repos/{repo}/{endpoint}",
        params={"state": state, "per_page": limit, "sort": "updated"},
    )
    rows = []
    for i in items[:limit]:
        row = {
            "number": i["number"],
            "title": i["title"],
            "state": i["state"],
            "created_at": i["created_at"][:10],
            "updated_at": i["updated_at"][:10],
            "labels": [la["name"] for la in i.get("labels", [])],
            "assignees": [a["login"] for a in i.get("assignees", [])],
            "url": i["html_url"],
        }
        if type == "pulls":
            row["draft"] = i.get("draft", False)
        rows.append(row)
    return json.dumps(rows, indent=2)


def get_github_commits(repo: str, limit: int = 10, branch: str | None = None) -> str:
    err = _require("GitHub", "github_token")
    if err:
        return err
    params: dict = {"per_page": limit}
    if branch:
        params["sha"] = branch
    commits = _gh_get(f"https://api.github.com/repos/{repo}/commits", params=params)
    rows = []
    for c in commits[:limit]:
        rows.append({
            "sha": c["sha"][:7],
            "author": c["commit"]["author"]["name"],
            "date": c["commit"]["author"]["date"][:10],
            "message": c["commit"]["message"].splitlines()[0],
        })
    return json.dumps(rows, indent=2)


def get_analytics_summary(start_date: str = "7daysAgo", end_date: str = "today") -> str:
    err = _require("Google Analytics", "ga_property_id", "ga_credentials_path")
    if err:
        return err
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
    except ImportError:
        return (
            "google-analytics-data package is not installed. "
            "Run: pip install google-analytics-data"
        )

    creds_path = settings.ga_credentials_path
    client = BetaAnalyticsDataClient.from_service_account_file(creds_path)  # type: ignore[attr-defined]
    property_id = f"properties/{settings.ga_property_id}"

    date_range = DateRange(start_date=start_date, end_date=end_date)

    def run(dimensions, metrics):
        req = RunReportRequest(
            property=property_id,
            dimensions=[Dimension(name=d) for d in dimensions],
            metrics=[Metric(name=m) for m in metrics],
            date_ranges=[date_range],
        )
        return client.run_report(req)

    # Overall totals
    totals_resp = run([], ["activeUsers", "sessions", "screenPageViews", "bounceRate"])
    totals: dict = {}
    if totals_resp.rows:
        row = totals_resp.rows[0]
        names = ["activeUsers", "sessions", "pageViews", "bounceRate"]
        for name, val in zip(names, row.metric_values):
            totals[name] = val.value

    # Top pages
    pages_resp = run(["pagePath"], ["screenPageViews"])
    top_pages = [
        {"page": r.dimension_values[0].value, "views": r.metric_values[0].value}
        for r in pages_resp.rows[:10]
    ]

    # Traffic sources
    sources_resp = run(["sessionDefaultChannelGroup"], ["sessions"])
    sources = [
        {"channel": r.dimension_values[0].value, "sessions": r.metric_values[0].value}
        for r in sources_resp.rows[:8]
    ]

    return json.dumps(
        {
            "period": f"{start_date} → {end_date}",
            "totals": totals,
            "top_pages": top_pages,
            "traffic_sources": sources,
        },
        indent=2,
    )


def get_notion_tasks(
    status_filter: str | None = None, database_id: str | None = None
) -> str:
    err = _require("Notion", "notion_token")
    if err:
        return err
    try:
        from notion_client import Client
    except ImportError:
        return "notion-client package is not installed. Run: pip install notion-client"

    notion = Client(auth=settings.notion_token)

    db_ids: list[str] = []
    if database_id:
        db_ids = [database_id]
    elif settings.notion_database_ids:
        db_ids = [i.strip() for i in settings.notion_database_ids.split(",") if i.strip()]
    else:
        # Auto-discover databases the integration has access to
        search = notion.search(filter={"property": "object", "value": "database"})
        db_ids = [r["id"] for r in search.get("results", [])]

    if not db_ids:
        return "No Notion databases found. Check your integration permissions or set NOTION_DATABASE_IDS."

    all_tasks = []
    for db_id in db_ids[:5]:  # cap at 5 databases
        try:
            db_meta = notion.databases.retrieve(database_id=db_id)
            db_name = (
                db_meta.get("title", [{}])[0].get("plain_text", db_id)
                if db_meta.get("title")
                else db_id
            )
            query_params: dict = {"database_id": db_id, "page_size": 50}
            if status_filter:
                query_params["filter"] = {
                    "property": "Status",
                    "status": {"equals": status_filter},
                }
            pages = notion.databases.query(**query_params)
            for page in pages.get("results", []):
                props = page["properties"]
                task: dict = {"database": db_name, "id": page["id"]}
                # Title
                for key, val in props.items():
                    if val["type"] == "title" and val["title"]:
                        task["title"] = "".join(t["plain_text"] for t in val["title"])
                    elif val["type"] == "status" and val.get("status"):
                        task["status"] = val["status"]["name"]
                    elif val["type"] == "date" and val.get("date"):
                        task["due"] = val["date"].get("start")
                    elif val["type"] == "people" and val.get("people"):
                        task["assignees"] = [p.get("name") for p in val["people"]]
                all_tasks.append(task)
        except Exception as exc:
            all_tasks.append({"database": db_id, "error": str(exc)})

    return json.dumps(all_tasks, indent=2)


def get_linear_issues(filter: str = "assigned", include_completed: bool = False) -> str:
    err = _require("Linear", "linear_api_key")
    if err:
        return err

    state_filter = ""
    if not include_completed:
        state_filter = 'filter: { state: { type: { nin: ["completed", "cancelled"] } } }'

    if filter == "assigned":
        gql = f"""
        query {{
          viewer {{
            assignedIssues({state_filter}) {{
              nodes {{
                identifier title priority priorityLabel
                state {{ name type }}
                dueDate updatedAt
                project {{ name }}
                url
              }}
            }}
          }}
        }}
        """
    else:
        gql = f"""
        query {{
          issues({state_filter} first: 50) {{
            nodes {{
              identifier title priority priorityLabel
              state {{ name type }}
              dueDate updatedAt
              assignee {{ displayName }}
              project {{ name }}
              url
            }}
          }}
        }}
        """

    resp = requests.post(
        "https://api.linear.app/graphql",
        json={"query": gql},
        headers={"Authorization": settings.linear_api_key, "Content-Type": "application/json"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        return json.dumps(data["errors"])

    nodes = (
        data.get("data", {}).get("viewer", {}).get("assignedIssues", {}).get("nodes", [])
        or data.get("data", {}).get("issues", {}).get("nodes", [])
    )
    return json.dumps(nodes, indent=2)


def get_trello_cards(board_name: str | None = None, overdue_only: bool = False) -> str:
    err = _require("Trello", "trello_api_key", "trello_token")
    if err:
        return err

    auth = {"key": settings.trello_api_key, "token": settings.trello_token}

    boards_resp = requests.get(
        "https://api.trello.com/1/members/me/boards",
        params={**auth, "fields": "name,url,closed"},
        timeout=15,
    )
    boards_resp.raise_for_status()
    boards = [b for b in boards_resp.json() if not b.get("closed")]

    if board_name:
        boards = [b for b in boards if board_name.lower() in b["name"].lower()]

    all_cards: list[dict] = []
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    for board in boards[:10]:
        cards_resp = requests.get(
            f"https://api.trello.com/1/boards/{board['id']}/cards",
            params={**auth, "fields": "name,due,dueComplete,idMembers,labels,url,idList", "members": "true"},
            timeout=15,
        )
        if not cards_resp.ok:
            continue
        for card in cards_resp.json():
            due = card.get("due")
            is_overdue = False
            if due:
                due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
                is_overdue = due_dt < now and not card.get("dueComplete")
            if overdue_only and not is_overdue:
                continue
            all_cards.append({
                "board": board["name"],
                "title": card["name"],
                "due": due[:10] if due else None,
                "overdue": is_overdue,
                "labels": [la["name"] for la in card.get("labels", [])],
                "url": card["url"],
            })

    return json.dumps(all_cards, indent=2)


def _is_allowed_path(path: str) -> bool:
    resolved = Path(path).resolve()
    for allowed in settings.allowed_paths:
        try:
            resolved.relative_to(Path(allowed).resolve())
            return True
        except ValueError:
            continue
    return False


def read_file(path: str) -> str:
    if not _is_allowed_path(path):
        return (
            f"Access denied: '{path}' is outside the allowed directories. "
            f"Allowed paths: {settings.allowed_paths}"
        )
    p = Path(path)
    if not p.exists():
        return f"File not found: {path}"
    if not p.is_file():
        return f"Not a file: {path}"
    try:
        size = p.stat().st_size
        if size > 200_000:  # 200 KB cap
            return f"File too large ({size} bytes). Read a specific section or use a smaller file."
        return p.read_text(errors="replace")
    except Exception as exc:
        return f"Error reading file: {exc}"


def list_directory(path: str = ".", show_hidden: bool = False) -> str:
    if not _is_allowed_path(path):
        return f"Access denied: '{path}' is outside the allowed directories."
    p = Path(path)
    if not p.exists():
        return f"Path not found: {path}"
    if not p.is_dir():
        return f"Not a directory: {path}"
    entries = []
    for item in sorted(p.iterdir()):
        if not show_hidden and item.name.startswith("."):
            continue
        stat = item.stat()
        entries.append({
            "name": item.name,
            "type": "dir" if item.is_dir() else "file",
            "size": stat.st_size if item.is_file() else None,
        })
    return json.dumps(entries, indent=2)


# ── Dispatch ──────────────────────────────────────────────────────────────────

_TOOL_MAP = {
    "get_github_overview": get_github_overview,
    "get_github_issues": get_github_issues,
    "get_github_commits": get_github_commits,
    "get_analytics_summary": get_analytics_summary,
    "get_notion_tasks": get_notion_tasks,
    "get_linear_issues": get_linear_issues,
    "get_trello_cards": get_trello_cards,
    "read_file": read_file,
    "list_directory": list_directory,
    # Monitoring
    "check_site_health": check_site_health_tool,
    "get_pagespeed": get_pagespeed,
    "get_search_console_data": get_search_console_data,
    "get_sentry_issues": get_sentry_issues,
    "manage_sites": manage_sites,
    "get_monitoring_dashboard": get_monitoring_dashboard,
}


def execute_tool(name: str, inputs: dict) -> str:
    fn = _TOOL_MAP.get(name)
    if fn is None:
        return f"Unknown tool: {name}"
    try:
        return fn(**inputs)
    except Exception as exc:
        return f"Tool '{name}' error: {exc}"
