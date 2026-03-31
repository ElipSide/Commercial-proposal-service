from __future__ import annotations

from typing import Optional


def extract_qty(text: str) -> Optional[int]:
    import re
    t = (text or "").lower()
    m = re.search(r"\b(\d+)\s*(?:шт|штук)\b", t)
    if not m:
        return None
    try:
        q = int(m.group(1))
        return q if q > 0 else None
    except Exception:
        return None


def norm_model_input(s: str) -> str:
    x = (s or "").strip().lower().replace(",", ".")
    x = " ".join(x.split())
    return x


def guess_manufacturer_from_text(text: str) -> Optional[str]:
    t = (text or "").lower()
    if "соллант" in t or "sollant" in t:
        return "Sollant"
    if "кселерон" in t or "xeleron" in t:
        return "Xeleron"
    if "кросс" in t or "cross air" in t or "cross" in t:
        return "Cross Air"
    if "exelute" in t or "экселют" in t or "екселют" in t:
        return "EXELUTE"
    return None
