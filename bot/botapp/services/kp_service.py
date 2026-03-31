from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from aiogram import html, types
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder


CB_KP_GET = "kp_get"
CB_KP_CANCEL = "kp_cancel"


_CONFIRM = {
    "added": [
        "Записал 👍 Добавил в черновик КП: {item}",
        "Ок, добавил: {item}",
        "Принял. Внес в КП: {item}",
    ],
    "added_many": [
        "Записал 👍 Добавил в КП {count} позиций",
        "Ок, добавил {count} позиций в черновик",
    ],
    "updated_qty": [
        "Понял, ставлю {qty} шт. Обновил количество",
        "Ок, количество меняю на {qty} шт",
        "Принял. Кол-во теперь {qty} шт",
    ],
    "ask_model": [
        "Ок, по {what}. Какую модель берём?",
        "Понял, нужен {what}. Подскажи модель — выбери из списка ниже",
        "Договорились. Осталось уточнить модель {what} — выбери вариант ниже",
    ],
    "model_selected": [
        "Отлично, беру {model}. Добавляю в КП 👍",
        "Ок, фиксирую {model}. Сейчас добавлю в черновик",
        "Принял {model}. Вношу в КП",
    ],
    "already": [
        "Похоже, это уже в КП. Вот актуальный черновик 👇",
        "Эта позиция уже в черновике. Смотри 👇",
    ],
    "kp_cleared": [
        "Хорошо, отменяю. Черновик КП очистил",
        "Ок, начинаем заново — черновик очистил",
    ],
    "kp_generating": [
        "Принял. Генерирую КП…",
        "Ок, собираю КП…",
    ],
}


class KPService:
    def build_actions_keyboard(self) -> types.InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text="Получить КП", callback_data=CB_KP_GET)
        kb.button(text="Отменить КП", callback_data=CB_KP_CANCEL)
        kb.adjust(2)
        return kb.as_markup()

    def say(self, sess: Any, key: str, **kwargs) -> str:
        last = getattr(sess, "last_phrase", "") or ""
        variants = _CONFIRM.get(key, ["Ок."])
        for _ in range(3):
            txt = random.choice(variants).format(**kwargs)
            if txt != last:
                sess.last_phrase = txt
                return txt
        txt = variants[0].format(**kwargs)
        sess.last_phrase = txt
        return txt

    @staticmethod
    def fmt_item_brief(it: dict) -> str:
        name = (it.get("nomenclature_name") or it.get("name_ru") or "позиция").strip()
        model = (it.get("model") or "").strip()
        cfg = (it.get("configuration") or it.get("nomenclature_configuration") or "").strip()
        qty = it.get("qty") or 1

        parts = [name]
        if model and model.lower() not in name.lower():
            parts.append(model)
        if cfg and cfg.lower() not in name.lower():
            parts.append(cfg)
        return f"{' '.join(parts)} — {qty} шт"

    @staticmethod
    def _item_display_name(it: Dict[str, Any]) -> str:
        name = (it.get("nomenclature_name") or "").strip()
        if not name:
            base = (it.get("name_ru") or "Оборудование").strip()
            model = (it.get("model") or "").strip()
            name = f"{base} {model}".strip()

        cfg = (it.get("configuration") or it.get("nomenclature_configuration") or "").strip()
        if cfg and cfg.lower() not in name.lower():
            name = f"{name} {cfg}"

        return name.strip()

    def format_kp_table(self, sess: Any) -> str:
        items = sess.kp.items
        if not items:
            return (
                "<b>Коммерческое предложение</b>\n\n"
                "Черновик пока пуст.\n"
                "Напиши, что добавить (например: <b>фотосепаратор 2.2</b>)."
            )

        rows: List[Dict[str, str]] = []
        for idx, it in enumerate(items, start=1):
            name = self._item_display_name(it)
            qty = str(it.get("qty") or 1)
            rows.append({"n": str(idx), "name": name, "qty": qty})

        max_name_len = 44
        for r in rows:
            if len(r["name"]) > max_name_len:
                r["name"] = r["name"][: max_name_len - 1] + "…"

        header_n, header_name, header_qty = "№", "Наименование", "Кол-во"
        n_w = max(len(header_n), max(len(r["n"]) for r in rows))
        name_w = max(len(header_name), max(len(r["name"]) for r in rows))
        qty_w = max(len(header_qty), max(len(r["qty"]) for r in rows))

        def pad(s: str, w: int) -> str:
            return s + " " * max(0, w - len(s))

        lines = [f"{pad(header_n, n_w)}  {pad(header_name, name_w)}  {pad(header_qty, qty_w)}"]
        for r in rows:
            lines.append(f"{pad(r['n'], n_w)}  {pad(r['name'], name_w)}  {pad(r['qty'], qty_w)}")

        table_text = html.quote("\n".join(lines))
        return (
            "<b>Коммерческое предложение</b>\n\n"
            f"<pre>{table_text}</pre>\n"
            "Можешь добавить ещё позицию (например: <b>добавь фотосепаратор 3.3</b>) или нажать кнопку ниже."
        )

    async def send_kp_summary_to_chat(self, bot: Any, chat_id: int, sess: Any, lead: Optional[str] = None) -> None:
        text = self.format_kp_table(sess)
        if lead:
            text = f"{lead}\n\n{text}"

        last_id = sess.kp.last_msg_id

        if last_id:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=last_id)
            except Exception:
                pass

        sent = await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=self.build_actions_keyboard(),
            parse_mode=ParseMode.HTML,
        )
        sess.kp.last_msg_id = sent.message_id
