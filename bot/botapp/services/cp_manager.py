from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import api_cp
from prompts import TYPE_MACHINE_TO_GROUP

# mapping type_key -> group_info key (Service differs)
GROUPINFO_KEY_MAP = {
    "service": "Service",
    # others match: photo_sorter, compressor, sep_machine, elevator, extra_equipment, Pneumatic_feed
}


class CPManager:
    def __init__(self) -> None:
        pass

    async def ensure_initialized(self, api_session: Any, user_id: str, sess: Any) -> None:
        if sess.cp.cp_key:
            return
        key, data_CP, List_CP = await api_cp.create_new_cp(api_session, user_id)
        sess.cp.cp_key = key
        sess.cp.data_CP = data_CP
        sess.cp.List_CP = List_CP

    def upsert_item_to_group_info(self, sess: Any, it: Dict[str, Any]) -> bool:
        data_CP = sess.cp.data_CP
        if not data_CP:
            return False

        id_row = it.get("nomenclature_id_row")
        if id_row is None:
            return False

        type_key = (it.get("type_key") or "").strip()
        if not type_key:
            return False

        group_key = GROUPINFO_KEY_MAP.get(type_key, type_key)
        qty = int(it.get("qty") or 1)

        gi = data_CP.setdefault("group_info", {})
        group = gi.setdefault(group_key, {})
        group[str(id_row)] = qty
        return True

    def delete_item_from_group_info(self, sess: Any, it: Dict[str, Any]) -> None:
        data_CP = sess.cp.data_CP
        if not data_CP:
            return

        id_row = it.get("nomenclature_id_row")
        type_key = (it.get("type_key") or "").strip()
        if id_row is None or not type_key:
            return

        group_key = GROUPINFO_KEY_MAP.get(type_key, type_key)
        group = (data_CP.get("group_info") or {}).get(group_key)
        if isinstance(group, dict):
            group.pop(str(id_row), None)

    @staticmethod
    def item_signature(it: Dict[str, Any]) -> str:
        keys = (
            "type_key",
            "type_key_db",
            "manufacturer",
            "model",
            "configuration",
            "nomenclature_name",
            "nomenclature_id_row",
            "nomenclature_id_erp",
            "nomenclature_id_bitrix",
        )
        payload = {k: it.get(k) for k in keys}
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)

    def add_items_to_kp(self, sess: Any, items: List[Dict[str, Any]]) -> tuple[int, int]:
        added = 0
        updated = 0

        for it in items:
            if not isinstance(it, dict):
                continue

            if (it.get("type_key") or "").strip() == "calc_params":
                continue
            if it.get("nomenclature_error") in ("model_not_found", "model_not_specified"):
                continue

            sig = self.item_signature(it)
            qty = it.get("qty")

            if sig in sess.kp.sig:
                if qty:
                    for ex in sess.kp.items:
                        if self.item_signature(ex) == sig:
                            ex["qty"] = qty
                            updated += 1
                            break
                self.upsert_item_to_group_info(sess, it)
                continue

            sess.kp.sig.add(sig)
            sess.kp.items.append(dict(it))
            added += 1

            self.upsert_item_to_group_info(sess, it)

        return added, updated

    @staticmethod
    def items_from_group_info(calc_gi: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not isinstance(calc_gi, dict) or not calc_gi:
            return []

        rev = {
            "photo_sorter": "photo_sorter",
            "compressor": "compressor",
            "sep_machine": "sep_machine",
            "elevator": "elevator",
            "extra_equipment": "extra_equipment",
            "Pneumatic_feed": "Pneumatic_feed",
            "Service": "service",
            "service": "service",
        }

        out: List[Dict[str, Any]] = []
        for group_key, ids in calc_gi.items():
            type_key = rev.get(group_key)
            if not type_key:
                continue
            if not isinstance(ids, dict):
                continue

            for id_row, qty in ids.items():
                try:
                    id_row_int = int(id_row)
                except Exception:
                    continue
                try:
                    qty_int = int(qty)
                except Exception:
                    qty_int = 1

                out.append({
                    "type_key": type_key,
                    "type_key_db": TYPE_MACHINE_TO_GROUP.get(type_key),
                    "name_ru": None,
                    "manufacturer": None,
                    "model": None,
                    "configuration": None,
                    "qty": qty_int,
                    "nomenclature_id_row": id_row_int,
                })
        return out
