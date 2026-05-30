import threading
import uuid
from collections import defaultdict
from typing import Any


class ConversationMemory:
    """Thread-safe in-memory conversation store."""

    def __init__(self, max_messages: int = 60):
        self._sessions: dict[str, list[dict]] = defaultdict(list)
        self._lock = threading.Lock()
        self.max_messages = max_messages

    def new_session(self) -> str:
        sid = str(uuid.uuid4())
        with self._lock:
            self._sessions[sid] = []
        return sid

    def get_messages(self, session_id: str) -> list[dict]:
        with self._lock:
            return list(self._sessions[session_id])

    def append(self, session_id: str, role: str, content: Any) -> None:
        with self._lock:
            self._sessions[session_id].append({"role": role, "content": content})
            # Trim to keep the window manageable while preserving pairs
            msgs = self._sessions[session_id]
            if len(msgs) > self.max_messages:
                self._sessions[session_id] = msgs[-self.max_messages:]

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions[session_id] = []

    def list_sessions(self) -> list[str]:
        with self._lock:
            return list(self._sessions.keys())


memory = ConversationMemory()
