from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from prompts import deepseek_extract_action, deepseek_extract_equipment
from recognition import enrich_ds_json_with_fallback, enrich_ds_json_with_nomenclature

from botapp.utils.text_parse import guess_manufacturer_from_text

logger = logging.getLogger(__name__)


class DeepSeekService:
    def __init__(self, nom_service: Any) -> None:
        self.nom_service = nom_service

    @staticmethod
    def _safe_json_load(s: str) -> Optional[Dict[str, Any]]:
        try:
            obj = json.loads(s)
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    async def extract_action(self, text: str, context: dict) -> Optional[dict]:
        try:
            return await deepseek_extract_action(text, context)
        except Exception:
            return None

    async def analyze_equipment(self, text: str, *, enrich_nomenclature: bool = True) -> Optional[Dict[str, Any]]:
        text = (text or "").strip()
        if not text:
            return None

        ds_raw = await deepseek_extract_equipment(text)
        if not ds_raw:
            logger.warning("DeepSeek equipment empty. text=%r", text)
            return None

        logger.info("DeepSeek equipment raw: %s", ds_raw)

        ds_after_fallback = ds_raw
        try:
            ds_after_fallback = enrich_ds_json_with_fallback(ds_after_fallback, text)
        except Exception:
            logger.exception("Fallback enrich failed")

        # manufacturer hint for compressors
        try:
            obj = self._safe_json_load(ds_after_fallback)
            hint_mfr = guess_manufacturer_from_text(text)
            if obj and hint_mfr and isinstance(obj.get("items"), list):
                for it in obj["items"]:
                    if isinstance(it, dict) and it.get("type_key") == "compressor" and not it.get("manufacturer"):
                        it["manufacturer"] = hint_mfr
                ds_after_fallback = json.dumps(obj, ensure_ascii=False)
        except Exception:
            pass

        ds_final = ds_after_fallback
        if enrich_nomenclature:
            try:
                nom = await self.nom_service.get_ru()
                if nom:
                    ds_final = enrich_ds_json_with_nomenclature(ds_final, nom)
            except Exception:
                logger.exception("Nomenclature enrich failed")

        logger.info("DeepSeek equipment final: %s", ds_final)

        try:
            return json.loads(ds_final)
        except Exception:
            return {"items": []}
