import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"
_SITES_FILE = _DATA_DIR / "sites.json"
_LOCK = threading.Lock()


def _load() -> list[dict]:
    try:
        data = json.loads(_SITES_FILE.read_text())
        return data.get("sites", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save(sites: list[dict]) -> None:
    _DATA_DIR.mkdir(exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=_DATA_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump({"sites": sites}, f, indent=2)
        os.replace(tmp, _SITES_FILE)
    except Exception:
        os.unlink(tmp)
        raise


class SiteRegistry:
    def list_sites(self) -> list[dict]:
        with _LOCK:
            return list(_load())

    def add_site(
        self,
        url: str,
        name: str | None = None,
        sentry_project: str | None = None,
        search_console_url: str | None = None,
    ) -> dict:
        url = url.rstrip("/")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        with _LOCK:
            sites = _load()
            if any(s["url"] == url for s in sites):
                return {"error": f"{url} is already being monitored."}
            site = {
                "url": url,
                "name": name or url.replace("https://", "").replace("http://", ""),
                "enabled": True,
                "sentry_project": sentry_project,
                "search_console_url": search_console_url or url + "/",
                "added_at": datetime.now(timezone.utc).isoformat(),
            }
            sites.append(site)
            _save(sites)
            return site

    def remove_site(self, url: str) -> bool:
        url = url.rstrip("/")
        with _LOCK:
            sites = _load()
            before = len(sites)
            sites = [s for s in sites if s["url"] != url]
            if len(sites) == before:
                return False
            _save(sites)
            return True

    def update_site(self, url: str, **kwargs) -> dict | None:
        with _LOCK:
            sites = _load()
            for site in sites:
                if site["url"] == url:
                    site.update({k: v for k, v in kwargs.items() if v is not None})
                    _save(sites)
                    return site
            return None

    def get_site(self, url: str) -> dict | None:
        with _LOCK:
            for site in _load():
                if site["url"] == url:
                    return site
            return None


site_registry = SiteRegistry()
