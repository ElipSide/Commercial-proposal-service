from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class KPSession:
    items: list[dict] = field(default_factory=list)
    sig: set[str] = field(default_factory=set)
    created_at: float = field(default_factory=lambda: time.time())
    last_msg_id: Optional[int] = None


@dataclass
class CPSession:
    cp_key: Optional[str] = None
    data_CP: Optional[dict] = None
    List_CP: Optional[dict] = None


@dataclass
class UserSession:
    kp: KPSession = field(default_factory=KPSession)
    cp: CPSession = field(default_factory=CPSession)
    awaiting_model: bool = False
    pending_data: Optional[dict] = None
    last_phrase: str = ""


class SessionManager:
    def __init__(self) -> None:
        self._sessions: Dict[int, UserSession] = {}

    def get(self, user_id: int) -> UserSession:
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession()
        return self._sessions[user_id]

    def reset(self, user_id: int) -> UserSession:
        self._sessions[user_id] = UserSession()
        return self._sessions[user_id]
