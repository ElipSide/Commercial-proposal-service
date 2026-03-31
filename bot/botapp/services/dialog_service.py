from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from aiogram import html
from aiogram.types import Message

import api_cp

from botapp.utils.text_parse import extract_qty, norm_model_input
from botapp.services.kp_service import KPService
from botapp.services.cp_manager import CPManager

logger = logging.getLogger(__name__)


class DialogService:
    def __init__(
        self,
        *,
        session_mgr: Any,
        nom_service: Any,
        deepseek: Any,
        kp: KPService,
        cp: CPManager,
        workUser: Any,
    ) -> None:
        self.session_mgr = session_mgr
        self.nom_service = nom_service
        self.deepseek = deepseek
        self.kp = kp
        self.cp = cp
        self.workUser = workUser

    # ---------- model choice helpers ----------
    @staticmethod
    def find_pending_model_item(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        items = data.get("items") or []
        for it in items:
            if not isinstance(it, dict):
                continue
            if it.get("nomenclature_error") in ("model_not_found", "model_not_specified"):
                return it
        return None

    @staticmethod
    def format_model_choice_request(it: Dict[str, Any]) -> str:
        err = it.get("nomenclature_error")
        requested = it.get("nomenclature_model") or it.get("model") or ""
        suggestions = [str(x) for x in (it.get("nomenclature_suggestions_models") or []) if str(x).strip()]

        if err == "model_not_specified":
            head = "Какую модель берём?"
        else:
            head = f"Не нашёл модель <b>{html.quote(str(requested))}</b> в базе."

        if suggestions:
            return (
                f"{head}\n"
                f"Выбери вариант и отправь одним сообщением:\n\n"
                f"<b>{html.quote(', '.join(suggestions[:20]))}</b>"
            )

        return f"{head}\nПришли точную модель (например: <b>2.2l</b> / <b>SLT-18.5V</b>)."

    def kp_context_for_action(self, sess: Any) -> Dict[str, Any]:
        items = sess.kp.items
        brief_list = []
        for it in items[:8]:
            brief_list.append(self.kp.fmt_item_brief(it))
        last = self.kp.fmt_item_brief(items[-1]) if items else ""
        return {"kp_items_brief": brief_list, "last_item_brief": last}

    async def handle_model_choice_flow(self, message: Message, api_session: Any) -> None:
        import re

        user_id = int(message.from_user.id)
        sess = self.session_mgr.get(user_id)

        pending = sess.pending_data
        if not pending or not isinstance(pending, dict):
            sess.awaiting_model = False
            sess.pending_data = None
            await message.answer("Похоже, я потерял контекст. Напиши, что добавляем в КП (например: <b>компрессор Sollant</b>).")
            return

        pending_item = self.find_pending_model_item(pending)
        if not pending_item or not isinstance(pending_item, dict):
            sess.awaiting_model = False
            sess.pending_data = None
            await message.answer("Ок. Напиши, что добавить в КП.")
            return

        qty_reply = extract_qty(message.text or "")
        if qty_reply:
            pending_item["qty"] = qty_reply

        type_key = (pending_item.get("type_key") or "").strip()
        user_text = (message.text or "").strip()

        if type_key == "compressor":
            tokens = re.findall(r"[A-Za-zА-Яа-я0-9][A-Za-zА-Яа-я0-9.,\-+/]*", user_text)
            stop = {"шт", "штук", "штуки"}
            cand = [t for t in tokens if t.lower() not in stop and (re.search(r"\d", t) or "-" in t)]
            chosen = cand[-1] if cand else (tokens[-1] if tokens else user_text)
            chosen_norm = norm_model_input(chosen)
        else:
            m = re.search(r"\b\d+(?:\.\d+)?[a-zа-я]*\b", user_text, re.IGNORECASE)
            chosen_norm = norm_model_input(m.group(0) if m else user_text)

        if not chosen_norm:
            await message.answer("Не понял выбранную модель. Пришли модель одним сообщением (например: <b>2.2</b> или <b>SLT-18.5V</b>).")
            return

        pending_item["model"] = chosen_norm
        for k in ("nomenclature_error", "nomenclature_model", "nomenclature_suggestions_models"):
            pending_item.pop(k, None)

        # only nomenclature enrichment (no DeepSeek)
        try:
            nom = await self.nom_service.get_ru()
            if nom:
                from recognition import enrich_ds_json_with_nomenclature
                ds_final = enrich_ds_json_with_nomenclature(json.dumps(pending, ensure_ascii=False), nom)
                pending_new = json.loads(ds_final)
            else:
                pending_new = pending
        except Exception:
            logger.exception("Failed to enrich pending data with nomenclature")
            pending_new = pending

        pending_item_new = self.find_pending_model_item(pending_new)
        if pending_item_new and pending_item_new.get("nomenclature_error") in ("model_not_found", "model_not_specified"):
            sess.awaiting_model = True
            sess.pending_data = pending_new
            what = (pending_item_new.get("name_ru") or "оборудованию").lower()
            await message.answer(self.kp.say(sess, "ask_model", what=what) + "\n\n" + self.format_model_choice_request(pending_item_new))
            return

        sess.awaiting_model = False
        sess.pending_data = None

        items_new = [it for it in (pending_new.get("items") or []) if isinstance(it, dict)]
        qty_pending = pending_item.get("qty")
        if qty_pending:
            for it in items_new:
                if it.get("type_key") == type_key and not it.get("qty"):
                    it["qty"] = qty_pending

        await message.answer(self.kp.say(sess, "model_selected", model=html.quote(chosen_norm)))

        # ensure cp if there are ready items
        ready = [it for it in items_new if it.get("nomenclature_id_row") and not it.get("nomenclature_error")]
        if ready and api_session is not None:
            try:
                await self.cp.ensure_initialized(api_session, str(user_id), sess)
            except Exception:
                logger.exception("ensure_initialized failed (model flow ready items)")

        added, updated = self.cp.add_items_to_kp(sess, items_new)
        if added == 0 and updated == 0:
            await self.kp.send_kp_summary_to_chat(message.bot, message.chat.id, sess, lead=self.kp.say(sess, "already"))
            return

        await self.kp.send_kp_summary_to_chat(message.bot, message.chat.id, sess)

    # ---------- main dialog ----------
    async def process_user_message(self, message: Message, text: str, api_session: Any) -> None:
        import re

        user_id = int(message.from_user.id)
        sess = self.session_mgr.get(user_id)

        raw = (text or "").strip()
        low = raw.lower()

        # awaiting model
        if sess.awaiting_model:
            t = low.strip()
            if "покажи кп" in t or t in ("кп", "черновик"):
                await self.kp.send_kp_summary_to_chat(message.bot, message.chat.id, sess, lead="Вот текущий черновик КП 👇")
                return

            if any(x in t for x in ("отменить кп", "очисти кп", "сброс кп", "начать заново")):
                sess.kp.last_msg_id = None
                self.session_mgr.reset(user_id)
                sess = self.session_mgr.get(user_id)
                await message.answer(self.kp.say(sess, "kp_cleared") + "\nНапиши, что добавляем первым.")
                return

            if any(x in t for x in ("получить кп", "сформируй кп", "сделай кп", "генерируй кп")):
                intent = "get_kp"
            else:
                await self.handle_model_choice_flow(message, api_session)
                return
        else:
            intent = None

        action = await self.deepseek.extract_action(raw, self.kp_context_for_action(sess))
        if not intent:
            intent = (action or {}).get("intent") if isinstance(action, dict) else None

        # fallback intent
        if not intent:
            if "покажи кп" in low or low.strip() in ("кп", "черновик"):
                intent = "show_kp"
            elif any(x in low for x in ("отменить кп", "очисти кп", "сброс кп", "начать заново")):
                intent = "cancel_kp"
            elif any(x in low for x in ("получить кп", "сформируй кп", "сделай кп", "генерируй кп")):
                intent = "get_kp"
            elif re.match(r"^(убери|удали)\s+\d+\b", low):
                intent = "remove"
            else:
                m = re.match(r"^\s*(сделай|поставь|давай)\s+(\d+)\s*$", low)
                if m:
                    intent = "set_qty"
                    action = action or {}
                    action["qty"] = int(m.group(2))
                    action["target"] = {"scope": "last"}

        # ---- handle intents ----
        if intent == "show_kp":
            await self.kp.send_kp_summary_to_chat(message.bot, message.chat.id, sess, lead="Вот текущий черновик КП 👇")
            return

        if intent == "cancel_kp":
            sess.kp.last_msg_id = None
            self.session_mgr.reset(user_id)
            sess = self.session_mgr.get(user_id)
            await message.answer(self.kp.say(sess, "kp_cleared") + "\nНапиши, что добавляем первым.")
            return

        if intent == "remove":
            idx = (action or {}).get("remove_index") if isinstance(action, dict) else None
            if not isinstance(idx, int):
                mm = re.match(r"^(убери|удали)\s+(\d+)\b", low)
                idx = int(mm.group(2)) if mm else None

            items_kp = sess.kp.items
            if not isinstance(idx, int) or idx < 1 or idx > len(items_kp):
                await message.answer("Не нашёл такую позицию. Напиши <b>покажи КП</b>, чтобы увидеть номера.")
                return

            removed_item = items_kp.pop(idx - 1)
            sess.kp.sig = {self.cp.item_signature(it) for it in items_kp if isinstance(it, dict)}

            try:
                self.cp.delete_item_from_group_info(sess, removed_item)
            except Exception:
                logger.exception("delete_item_from_group_info failed")

            await self.kp.send_kp_summary_to_chat(message.bot, message.chat.id, sess, lead=f"Ок, убрал позицию №{idx}.")
            return

        if intent == "set_qty":
            qty = (action or {}).get("qty") if isinstance(action, dict) else None
            if not isinstance(qty, int):
                qty = extract_qty(raw)

            if not qty or qty <= 0:
                await message.answer("Сколько штук поставить? Напиши, например: <b>7 шт</b>")
                return

            target = (action or {}).get("target") if isinstance(action, dict) else None
            if not isinstance(target, dict):
                target = {"scope": "last"}

            items_kp = sess.kp.items
            if not items_kp:
                await message.answer("Пока в КП пусто. Сначала добавь оборудование.")
                return

            changed = False
            scope = target.get("scope") or "last"
            if scope == "last":
                items_kp[-1]["qty"] = qty
                changed = True
                try:
                    self.cp.upsert_item_to_group_info(sess, items_kp[-1])
                except Exception:
                    logger.exception("upsert_item_to_group_info failed")

            elif scope == "index":
                idx = target.get("index")
                if isinstance(idx, int) and 1 <= idx <= len(items_kp):
                    items_kp[idx - 1]["qty"] = qty
                    changed = True
                    try:
                        self.cp.upsert_item_to_group_info(sess, items_kp[idx - 1])
                    except Exception:
                        logger.exception("upsert_item_to_group_info failed")

            elif scope == "type":
                tkey = target.get("type_key")
                if tkey:
                    for it in items_kp:
                        if it.get("type_key") == tkey:
                            it["qty"] = qty
                            changed = True
                            try:
                                self.cp.upsert_item_to_group_info(sess, it)
                            except Exception:
                                logger.exception("upsert_item_to_group_info failed")

            if not changed:
                await message.answer(
                    "Понял, но не нашёл, к чему применить количество.\n"
                    "Напиши <b>покажи КП</b> и укажи номер строки: например <b>поставь 7 для 2</b>."
                )
                return

            await self.kp.send_kp_summary_to_chat(message.bot, message.chat.id, sess, lead=self.kp.say(sess, "updated_qty", qty=qty))
            return

        if intent == "get_kp":
            if not sess.kp.items:
                await message.answer("Пока в черновике пусто. Добавь оборудование, и я соберу КП.")
                return

            if api_session is None:
                await message.answer("Не могу сформировать КП: не настроена сессия API.")
                return

            try:
                await self.cp.ensure_initialized(api_session, str(user_id), sess)
            except Exception:
                logger.exception("ensure_initialized failed")
                await message.answer("Не смог подготовить КП. Попробуй ещё раз.")
                return

            await message.answer(self.kp.say(sess, "kp_generating"))

            try:
                ok = await api_cp.create_cp(
                    api_session,
                    str(user_id),
                    key=sess.cp.cp_key,
                    data_CP=sess.cp.data_CP,
                    List_CP=sess.cp.List_CP,
                )
            except Exception:
                logger.exception("create_cp failed")
                ok = False

            if not ok:
                await message.answer("Не получилось сформировать КП. Попробуй чуть позже.")
                return

            await message.answer("КП собрано. Если хочешь — добавим ещё позиции или поменяем количество.")
            return

        # default: treat as add equipment
        data = await self.deepseek.analyze_equipment(raw, enrich_nomenclature=False)
        if not data:
            await message.answer("Сейчас не могу обработать запрос. Попробуй ещё раз чуть позже.")
            return

        items = [it for it in (data.get("items") or []) if isinstance(it, dict)]
        if not items:
            await message.answer(
                "Не совсем понял, что добавить.\n"
                "Напиши, например: <b>фотосепаратор 2.2</b> или <b>компрессор Sollant</b>."
            )
            return

        qty_text = extract_qty(raw)
        if qty_text:
            for it in items:
                it["qty"] = qty_text

        # if model required
        pending_item = self.find_pending_model_item(data)
        if pending_item:
            ready = [it for it in items if it.get("nomenclature_id_row") and not it.get("nomenclature_error")]
            if ready and api_session is not None:
                try:
                    await self.cp.ensure_initialized(api_session, str(user_id), sess)
                except Exception:
                    logger.exception("ensure_initialized failed (ready items)")

            self.cp.add_items_to_kp(sess, items)

            if qty_text and not pending_item.get("qty"):
                pending_item["qty"] = qty_text

            sess.awaiting_model = True
            sess.pending_data = data

            what = (pending_item.get("name_ru") or "оборудованию").lower()
            await message.answer(self.kp.say(sess, "ask_model", what=what) + "\n\n" + self.format_model_choice_request(pending_item))
            return

        # ready items -> ensure cp once
        ready = [it for it in items if it.get("nomenclature_id_row") and not it.get("nomenclature_error")]
        if ready and api_session is not None:
            try:
                await self.cp.ensure_initialized(api_session, str(user_id), sess)
            except Exception:
                logger.exception("ensure_initialized failed (ready items)")

        added, updated = self.cp.add_items_to_kp(sess, items)

        if added == 0 and updated == 0:
            await self.kp.send_kp_summary_to_chat(message.bot, message.chat.id, sess, lead=self.kp.say(sess, "already"))
            return

        lead_parts = []
        if added == 1:
            new_item = sess.kp.items[-1] if sess.kp.items else items[0]
            lead_parts.append(self.kp.say(sess, "added", item=self.kp.fmt_item_brief(new_item)))
        elif added > 1:
            lead_parts.append(self.kp.say(sess, "added_many", count=added))

        if updated and qty_text:
            lead_parts.append(self.kp.say(sess, "updated_qty", qty=qty_text))

        lead = " ".join([p for p in lead_parts if p]).strip() if lead_parts else None
        await self.kp.send_kp_summary_to_chat(message.bot, message.chat.id, sess, lead=lead)
