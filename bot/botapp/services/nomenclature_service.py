from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Optional

import requests


class NomenclatureService:
    def __init__(self, url_ru: str, ttl_sec: int = 3600) -> None:
        self.url_ru = url_ru
        self.ttl_sec = ttl_sec
        self._cache_ts: float = 0.0
        self._cache_data: Optional[dict] = None

    def _load_local_ru_json(self) -> Optional[dict]:
        try:
            p = Path(__file__).resolve().parent.parent / "ru.json"
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
        return None

    async def get_ru(self) -> Optional[dict]:
        now = time.time()
        if self._cache_data is not None and (now - self._cache_ts) < self.ttl_sec:
            return self._cache_data

        def _fetch():
            try:
                r = requests.get(self.url_ru, timeout=30)
                r.raise_for_status()
                return r.json()
            except Exception:
                return None

        data = await asyncio.to_thread(_fetch)
        if not data:
            data = self._load_local_ru_json()

        if data:
            self._cache_data = data
            self._cache_ts = now

        return data
