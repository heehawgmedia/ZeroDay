import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"
_CACHE_FILE = _DATA_DIR / "poll_cache.json"
_LOCK = threading.Lock()


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    try:
        return json.loads(_CACHE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict) -> None:
    _DATA_DIR.mkdir(exist_ok=True)
    # Atomic write via temp-file rename
    fd, tmp = tempfile.mkstemp(dir=_DATA_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp, _CACHE_FILE)
    except Exception:
        os.unlink(tmp)
        raise


class PollCache:
    """File-backed cache shared between the poller worker and FastAPI process."""

    def read(self) -> dict:
        with _LOCK:
            return _load()

    def get_site(self, url: str) -> dict:
        with _LOCK:
            return _load().get(url, {})

    def update(self, url: str, check_type: str, data: dict) -> None:
        with _LOCK:
            all_data = _load()
            site_data = all_data.setdefault(url, {})
            site_data[check_type] = data
            _save(all_data)

    def set_site(self, url: str, data: dict) -> None:
        with _LOCK:
            all_data = _load()
            all_data[url] = data
            _save(all_data)

    def remove_site(self, url: str) -> None:
        with _LOCK:
            all_data = _load()
            all_data.pop(url, None)
            _save(all_data)


cache = PollCache()
