"""
Монолитная точка входа Telegram-бота для коммерческих предложений.

Вход:
- текст/голос пользователя, callback-и, контакт и команды Telegram.

Выход:
- обновление сессии пользователя, черновика КП и отправка сообщений/ссылок/PDF.
"""

import asyncio
import json
import logging
import random
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from aiogram import Bot, Dispatcher, F, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.command import Command, CommandObject
from aiogram.types import FSInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramForbiddenError

import api_cp
import api_bot
import phrases
from classes import NumbersCallbackFactory, replyButton
from prompts import deepseek_extract_action, deepseek_extract_equipment, TYPE_MACHINE_TO_GROUP
from env_settings import get_settings
from recognition import (
    enrich_ds_json_with_fallback,
    enrich_ds_json_with_nomenclature,
    transcribe_voice_message,
)

import aiohttp
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# ENV / CONFIG
SETTINGS = get_settings()

dp = Dispatcher()
workUser = api_bot.workingUsers()
bot = Bot(token=SETTINGS.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

commandID = SETTINGS.command_ids
ALLOWED_CHAT_ID = SETTINGS.allowed_chat_id
API_URL = SETTINGS.api_url
NOMENCLATURE_URL_RU = SETTINGS.nomenclature_url_ru
TELEGRAM_START_URL_BASE = SETTINGS.telegram_start_url_base
UPDATE_BOT_ALLOWED_IDS = SETTINGS.update_bot_allowed_ids
NOTIFY_ADMIN_ID = SETTINGS.notify_admin_id

_NOM_CACHE = {"ts": 0.0, "data": None}
_NOM_TTL_SEC = SETTINGS.nom_ttl_sec

# KP inline
CB_KP_GET = "kp_get"
CB_KP_CANCEL = "kp_cancel"


api_session: aiohttp.ClientSession | None = None

async def on_startup():
    """Вход: запуск приложения. Выход: инициализированная aiohttp API-сессия."""
    global api_session
    api_session = aiohttp.ClientSession()

async def on_shutdown():
    """Вход: остановка приложения. Выход: корректно закрытая aiohttp API-сессия."""
    global api_session
    if api_session:
        await api_session.close()
        api_session = None



def build_kp_actions_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Получить КП", callback_data=CB_KP_GET)
    kb.button(text="Отменить КП", callback_data=CB_KP_CANCEL)
    kb.adjust(2)
    return kb.as_markup()


# -----------------------------
# Session
# -----------------------------
USER_SESSIONS: Dict[int, Dict[str, Any]] = {}


def _get_session(user_id: int) -> Dict[str, Any]:
    s = USER_SESSIONS.get(user_id)
    if not s:
        s = {
            "kp": {"items": [], "sig": set(), "created_at": time.time(), "last_msg_id": None},
            "cp": {"cp_key": None, "data_CP": None, "List_CP": None},
            "awaiting_model": False,
            "pending_data": None,
            "last_phrase": "",
        }
        USER_SESSIONS[user_id] = s
    return s

# mapping type_key -> ключ group_info (на случай Service)
GROUPINFO_KEY_MAP = {
    "service": "Service",
    # остальные совпадают: photo_sorter, compressor, sep_machine, elevator, extra_equipment, Pneumatic_feed
}

async def ensure_cp_initialized(api_session, user_id: str, sess: Dict[str, Any]) -> None:
    """Вход: aiohttp session, user_id и сессия пользователя. Выход: заполненный cp_key/data_CP/List_CP."""
    if sess["cp"]["cp_key"]:
        return
    key, data_CP, List_CP = await api_cp.create_new_cp(api_session, user_id)
    sess["cp"]["cp_key"] = key
    sess["cp"]["data_CP"] = data_CP
    sess["cp"]["List_CP"] = List_CP



def upsert_item_to_group_info(sess: Dict[str, Any], it: Dict[str, Any]) -> bool:
    """Вход: сессия и item КП. Выход: True, если позиция синхронизирована в group_info backend-формата."""
    cp = sess["cp"]
    data_CP = cp.get("data_CP")
    if not data_CP:
        return False

    # Берём id_row из номенклатуры
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
    group[str(id_row)] = qty  # ✅ как у тебя: "13": 1
    return True


def delete_item_from_group_info(sess: Dict[str, Any], it: Dict[str, Any]) -> None:
    """Вход: сессия и удаляемая позиция. Выход: позиция удалена из group_info backend-формата."""
    cp = sess["cp"]
    data_CP = cp.get("data_CP")
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


def _reset_kp(user_id: int) -> None:
    USER_SESSIONS[user_id] = {
        "kp": {"items": [], "sig": set(), "created_at": time.time(), "last_msg_id": None},
        "cp": {"cp_key": None, "data_CP": None, "List_CP": None},
        "awaiting_model": False,
        "pending_data": None,
        "last_phrase": "",
    }




def _item_signature(it: Dict[str, Any]) -> str:
    # qty НЕ входит в сигнатуру: одинаковая позиция -> обновляем кол-во
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


def _add_items_to_kp(sess: Dict[str, Any], items: List[Dict[str, Any]]) -> Tuple[int, int]:
    """Вход: сессия и список новых items. Выход: кортеж (added, updated)."""
    kp = sess["kp"]
    added = 0
    updated = 0

    for it in items:
        if not isinstance(it, dict):
            continue

        # calc_params — это не позиция КП, а входные параметры для расчёта
        if (it.get("type_key") or "").strip() == "calc_params":
            continue
        if it.get("nomenclature_error") in ("model_not_found", "model_not_specified"):
            continue

        sig = _item_signature(it)
        qty = it.get("qty")

        if sig in kp["sig"]:
            if qty:
                for ex in kp["items"]:
                    if _item_signature(ex) == sig:
                        ex["qty"] = qty
                        updated += 1
                        break
            # ✅ синхронизируем group_info даже при апдейте qty
            upsert_item_to_group_info(sess, it)
            continue

        kp["sig"].add(sig)
        kp["items"].append(dict(it))
        added += 1

        # ✅ синхронизируем group_info при добавлении
        upsert_item_to_group_info(sess, it)

    return added, updated


# -----------------------------
# Friendly phrases
# -----------------------------
def _fmt_item_brief(it: dict) -> str:
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

def say(sess: dict, key: str, **kwargs) -> str:
    last = sess.get("last_phrase", "")
    variants = _CONFIRM.get(key, ["Ок."])
    for _ in range(3):
        txt = random.choice(variants).format(**kwargs)
        if txt != last:
            sess["last_phrase"] = txt
            return txt
    txt = variants[0].format(**kwargs)
    sess["last_phrase"] = txt
    return txt


# -----------------------------
# Nomenclature cache
# -----------------------------
def _load_local_ru_json() -> Optional[dict]:
    try:
        p = Path(__file__).with_name("ru.json")
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


async def get_nomenclature_ru() -> Optional[dict]:
    now = time.time()
    if _NOM_CACHE["data"] is not None and (now - _NOM_CACHE["ts"]) < _NOM_TTL_SEC:
        return _NOM_CACHE["data"]

    def _fetch():
        try:
            r = requests.get(NOMENCLATURE_URL_RU, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    data = await asyncio.to_thread(_fetch)
    if not data:
        data = _load_local_ru_json()

    if data:
        _NOM_CACHE["data"] = data
        _NOM_CACHE["ts"] = now

    return data


# -----------------------------
# Text parsing helpers (fallback)
# -----------------------------
def _extract_qty(text: str) -> Optional[int]:
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


def _norm_model_input(s: str) -> str:
    x = (s or "").strip().lower().replace(",", ".")
    x = " ".join(x.split())
    return x


def _guess_manufacturer_from_text(text: str) -> Optional[str]:
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

# -----------------------------
# Scenario 2: расчет по продукту и производительности
# -----------------------------
def _need_calc_scenario(items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Возвращает item фотосепаратора, если запрос похож на 'по продукту + т/ч' без явной модели."""
    for it in items or []:
        if not isinstance(it, dict):
            continue
        if it.get("type_key") != "photo_sorter":
            continue
        if it.get("product") and it.get("capacity_tph") is not None:
            # если модель уже указана — это обычный сценарий
            if not it.get("model"):
                return it
    return None

def _is_group_info_response(x: Any) -> bool:
    # ожидаем dict вида { "photo_sorter": {112:1}, ... }
    if not isinstance(x, dict) or not x:
        return False
    # эвристика: есть хотя бы один ключ из известных групп
    known = {"photo_sorter", "compressor", "sep_machine", "elevator", "extra_equipment", "Service", "Pneumatic_feed"}
    return any(k in x for k in known)


def _items_from_group_info(calc_gi: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Преобразует ответ вида group_info в items для КП.
    Каждый элемент = {type_key, nomenclature_id_row, qty}, дальше обогащаем номенклатурой.
    """
    if not isinstance(calc_gi, dict) or not calc_gi:
        return []

    # group_info ключ -> type_key (обратно)
    rev = {
        "photo_sorter": "photo_sorter",
        "compressor": "compressor",
        "sep_machine": "sep_machine",
        "elevator": "elevator",
        "extra_equipment": "extra_equipment",
        "Pneumatic_feed": "Pneumatic_feed",
        "Service": "service",
        "service": "service",
        # остальное (Sieve, attendance и т.п.) можно добавить позже при необходимости
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

def _index_by_id_row(records: list) -> dict[int, dict]:
    out = {}
    for r in records or []:
        if isinstance(r, dict) and r.get("id_row") is not None:
            try:
                out[int(r["id_row"])] = r
            except Exception:
                pass
    return out


def _items_from_calc_response(calc_json: dict, nom: dict | None = None) -> list[dict]:
    if not isinstance(calc_json, dict) or not calc_json:
        return []

    out: list[dict] = []
    block = calc_json.get("0")
    if not isinstance(block, dict):
        return out

    # --- photo_sorter (как у тебя уже сделано)
    seps = block.get("Separators") or []
    if isinstance(seps, list) and seps:
        chosen = seps[0]
        out.append({
            "type_key": "photo_sorter",
            "type_key_db": TYPE_MACHINE_TO_GROUP["photo_sorter"],
            "name_ru": "Фотосепараторы",
            "manufacturer": "Csort",
            "model": chosen.get("model_series"),
            "configuration": chosen.get("configuration"),
            "qty": int(block.get("count_separ") or 1),
            "nomenclature_id_row": chosen.get("id_row"),
            "nomenclature_id_erp": chosen.get("id_erp"),
            "nomenclature_id_bitrix": chosen.get("bitrix_id"),
            "nomenclature_name": chosen.get("name_print"),
        })

    # --- ✅ extra_equipment по group_info.extra_equipment
    extra_map = (block.get("group_info") or {}).get("extra_equipment") or {}
    extra_records = (nom or {}).get("extra_equipment") or []
    extra_by_id = _index_by_id_row(extra_records)

    if isinstance(extra_map, dict):
        for id_row, qty in extra_map.items():
            try:
                id_row_int = int(id_row)
            except Exception:
                continue
            rec = extra_by_id.get(id_row_int) or {}

            out.append({
                "type_key": "extra_equipment",
                "type_key_db": TYPE_MACHINE_TO_GROUP["extra_equipment"],
                "name_ru": "Дополнительное оборудование",
                "manufacturer": None,
                "model": None,
                "configuration": None,
                "qty": int(qty) if qty is not None else 1,

                # ✅ сразу номенклатура по id_row
                "nomenclature_id_row": id_row_int,
                "nomenclature_id_erp": rec.get("id_erp"),
                "nomenclature_id_bitrix": rec.get("id_bitrix") or rec.get("id_bitrix") or rec.get("bitrix_id") or rec.get("id_bitrix"),
                "nomenclature_name": rec.get("name_print") or rec.get("name"),
                "nomenclature_group": "extra_equipment",
            })

    # --- compressors (как у тебя уже сделано)
    compressors = calc_json.get("compressors")
    if isinstance(compressors, list):
        for c in compressors:
            comp = c.get("compressor") or {}
            out.append({
                "type_key": "compressor",
                "type_key_db": TYPE_MACHINE_TO_GROUP["compressor"],
                "name_ru": "Компрессоры",
                "manufacturer": comp.get("produced_by"),
                "model": comp.get("name_print") or comp.get("name"),
                "qty": int(c.get("count") or 1),
                "nomenclature_id_row": comp.get("id_row"),
                "nomenclature_id_erp": comp.get("id_erp"),
                "nomenclature_id_bitrix": comp.get("id_bitrix"),
                "nomenclature_name": comp.get("name_print"),
            })

    return out

# -----------------------------
# KP table formatting
# -----------------------------
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


def _format_kp_table(sess: Dict[str, Any]) -> str:
    items = sess["kp"]["items"]
    if not items:
        return (
            "<b>Коммерческое предложение</b>\n\n"
            "Черновик пока пуст.\n"
            "Напиши, что добавить (например: <b>фотосепаратор 2.2</b>)."
        )

    rows: List[Dict[str, str]] = []
    for idx, it in enumerate(items, start=1):
        name = _item_display_name(it)
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

async def send_kp_summary_to_chat(chat_id: int, sess: Dict[str, Any], lead: Optional[str] = None) -> None:
    text = _format_kp_table(sess)
    if lead:
        text = f"{lead}\n\n{text}"

    last_id = sess.get("kp", {}).get("last_msg_id")

    # ✅ обычное поведение: удаляем старое сообщение и отправляем новое
    if last_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=last_id)
        except Exception:
            pass

    sent = await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=build_kp_actions_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    sess["kp"]["last_msg_id"] = sent.message_id


async def send_kp_summary(message: Message, sess: Dict[str, Any], lead: Optional[str] = None) -> None:
    await send_kp_summary_to_chat(message.chat.id, sess, lead=lead)





# -----------------------------
# Model choice message
# -----------------------------
def _format_model_choice_request(it: Dict[str, Any]) -> str:
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


# -----------------------------
# DeepSeek equipment pipeline
# -----------------------------
def _safe_json_load(s: str) -> Optional[Dict[str, Any]]:
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


async def analyze_equipment(text: str, *, enrich_nomenclature: bool = True) -> Optional[Dict[str, Any]]:
    """Вход: текст пользователя. Выход: извлечённые позиции/параметры в JSON-словаре."""
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

    # подсказка производителя (если LLM не заполнил, а пользователь явно сказал)
    try:
        obj = _safe_json_load(ds_after_fallback)
        hint_mfr = _guess_manufacturer_from_text(text)
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
            nom = await get_nomenclature_ru()
            if nom:
                ds_final = enrich_ds_json_with_nomenclature(ds_final, nom)
        except Exception:
            logger.exception("Nomenclature enrich failed")

    logger.info("DeepSeek equipment final: %s", ds_final)

    try:
        return json.loads(ds_final)
    except Exception:
        return {"items": []}


def _find_pending_model_item(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    items = data.get("items") or []
    for it in items:
        if not isinstance(it, dict):
            continue
        if it.get("nomenclature_error") in ("model_not_found", "model_not_specified"):
            return it
    return None


# -----------------------------
# DeepSeek action router
# -----------------------------
def _kp_context_for_action(sess: Dict[str, Any]) -> Dict[str, Any]:
    items = sess["kp"]["items"]
    brief_list = []
    for it in items[:8]:
        brief_list.append(_fmt_item_brief(it))
    last = _fmt_item_brief(items[-1]) if items else ""
    return {"kp_items_brief": brief_list, "last_item_brief": last}


def _apply_set_qty(sess: Dict[str, Any], qty: int, target: Dict[str, Any]) -> bool:
    if qty <= 0:
        return False
    items = sess["kp"]["items"]
    if not items:
        return False

    scope = (target or {}).get("scope") or "last"

    if scope == "last":
        items[-1]["qty"] = qty
        return True

    if scope == "index":
        idx = target.get("index")
        if isinstance(idx, int) and 1 <= idx <= len(items):
            items[idx - 1]["qty"] = qty
            return True
        return False

    if scope == "type":
        tkey = target.get("type_key")
        if not tkey:
            return False
        changed = False
        for it in items:
            if it.get("type_key") == tkey:
                it["qty"] = qty
                changed = True
        return changed

    return False


# -----------------------------
# Model choice flow
# -----------------------------
async def handle_model_choice_flow(message: Message, sess: Dict[str, Any]) -> None:
    """
    Пользователь прислал модель после подсказок.
    - корректно игнорируем "шт"
    - сохраняем qty, если он был в исходном запросе или в ответе
    - прогоняем только номенклатуру (без DeepSeek)
    """
    import re

    pending = sess.get("pending_data")
    if not pending or not isinstance(pending, dict):
        sess["awaiting_model"] = False
        sess["pending_data"] = None
        await message.answer("Похоже, я потерял контекст. Напиши, что добавляем в КП (например: <b>компрессор Sollant</b>).")
        return

    pending_item = _find_pending_model_item(pending)
    if not pending_item or not isinstance(pending_item, dict):
        sess["awaiting_model"] = False
        sess["pending_data"] = None
        await message.answer("Ок. Напиши, что добавить в КП.")
        return

    # qty можно указать в ответе (например: "SLT-18.5V 5 шт")
    qty_reply = _extract_qty(message.text or "")
    if qty_reply:
        pending_item["qty"] = qty_reply

    type_key = (pending_item.get("type_key") or "").strip()
    user_text = (message.text or "").strip()

    # модель для компрессора — это "SLT-18.5V" / "Z40A" и т.п.
    if type_key == "compressor":
        # ищем токен, похожий на модель: содержит цифру или дефис
        tokens = re.findall(r"[A-Za-zА-Яа-я0-9][A-Za-zА-Яа-я0-9.,\-+/]*", user_text)
        stop = {"шт", "штук", "штуки"}
        cand = [t for t in tokens if t.lower() not in stop and (re.search(r"\d", t) or "-" in t)]
        chosen = cand[-1] if cand else (tokens[-1] if tokens else user_text)
        chosen_norm = _norm_model_input(chosen)
    else:
        m = re.search(r"\b\d+(?:\.\d+)?[a-zа-я]*\b", user_text, re.IGNORECASE)
        chosen_norm = _norm_model_input(m.group(0) if m else user_text)

    if not chosen_norm:
        await message.answer("Не понял выбранную модель. Пришли модель одним сообщением (например: <b>2.2</b> или <b>SLT-18.5V</b>).")
        return

    pending_item["model"] = chosen_norm

    for k in ("nomenclature_error", "nomenclature_model", "nomenclature_suggestions_models"):
        pending_item.pop(k, None)

    try:
        nom = await get_nomenclature_ru()
        if nom:
            ds_final = enrich_ds_json_with_nomenclature(json.dumps(pending, ensure_ascii=False), nom)
            pending_new = json.loads(ds_final)
        else:
            pending_new = pending
    except Exception:
        logger.exception("Failed to enrich pending data with nomenclature")
        pending_new = pending

    pending_item_new = _find_pending_model_item(pending_new)
    if pending_item_new and pending_item_new.get("nomenclature_error") in ("model_not_found", "model_not_specified"):
        sess["awaiting_model"] = True
        sess["pending_data"] = pending_new
        what = (pending_item_new.get("name_ru") or "оборудованию").lower()
        await message.answer(say(sess, "ask_model", what=what) + "\n\n" + _format_model_choice_request(pending_item_new))
        return

    # success
    sess["awaiting_model"] = False
    sess["pending_data"] = None

    items_new = [it for it in (pending_new.get("items") or []) if isinstance(it, dict)]

    # если qty был в pending_item, проставим его на финальный item
    qty_pending = pending_item.get("qty")
    if qty_pending:
        for it in items_new:
            if it.get("type_key") == type_key and not it.get("qty"):
                it["qty"] = qty_pending

    await message.answer(say(sess, "model_selected", model=html.quote(chosen_norm)))
    added, updated = _add_items_to_kp(sess, items_new)

    if added == 0 and updated == 0:
        await send_kp_summary(message, sess, lead=say(sess, "already"))
        return

    await send_kp_summary(message, sess)


# -----------------------------
# Main dialog
# -----------------------------
async def process_user_equipment_message(message: Message, text: str) -> None:
    """
    Главный роутер диалога "ИИ-менеджер КП".

    Хранение в сессии:
      sess["kp"]["items"]  — удобный список для показа пользователю (таблица)
      sess["cp"]["cp_key"], ["data_CP"], ["List_CP"] — ТВОЙ формат для бэка (group_info[type][id_row]=qty)

    Предполагается, что у тебя уже есть/добавлены:
      - deepseek_extract_action(text, context)
      - _kp_context_for_action(sess)
      - analyze_equipment(text)
      - _find_pending_model_item(data)
      - _format_model_choice_request(item)
      - handle_model_choice_flow(message, sess)
      - send_kp_summary(message, sess, lead=None)
      - say(sess, key, **kwargs)
      - _add_items_to_kp(sess, items) -> (added, updated)  (и внутри делает upsert_item_to_group_info)
      - ensure_cp_initialized(api_session, user_id_str, sess)
      - create_cp(api_session, user_id_str, key=..., data_CP=..., List_CP=...)
      - delete_item_from_group_info(sess, item)
      - _extract_qty(text) (если нужен fallback)
    """
    import re

    user_id = int(message.from_user.id)
    sess = _get_session(user_id)

    raw = (text or "").strip()
    low = raw.lower()

    # 1) Если ждём выбор модели — любое сообщение трактуем как выбор
    # ✅ если ждём выбор модели — но пользователь написал команду, а не модель
    if sess.get("awaiting_model"):
        t = (text or "").strip().lower()

        if "покажи кп" in t or t in ("кп", "черновик"):
            await send_kp_summary(message, sess, lead="Вот текущий черновик КП 👇")
            return

        if any(x in t for x in ("отменить кп", "очисти кп", "сброс кп", "начать заново")):
            sess["kp"]["last_msg_id"] = None
            _reset_kp(user_id)
            sess = _get_session(user_id)
            await message.answer(say(sess, "kp_cleared") + "\nНапиши, что добавляем первым.")
            return

        if any(x in t for x in ("получить кп", "сформируй кп", "сделай кп", "генерируй кп")):
            # просто переиспользуем текущий путь
            # (можно вынести в отдельную функцию)
            intent = "get_kp"
        else:
            await handle_model_choice_flow(message, sess)
            return


    # 2) DeepSeek ACTION (intent)
    action = None
    try:
        action = await deepseek_extract_action(raw, _kp_context_for_action(sess))
    except Exception:
        action = None

    intent = (action or {}).get("intent") if isinstance(action, dict) else None

    # ---------
    # Fallback intent (если DeepSeek не ответил)
    # ---------
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
            # "сделай 7" -> set_qty last
            m = re.match(r"^\s*(сделай|поставь|давай)\s+(\d+)\s*$", low)
            if m:
                intent = "set_qty"
                action = action or {}
                action["qty"] = int(m.group(2))
                action["target"] = {"scope": "last"}

    # 3) Обработка intent
    if intent == "show_kp":
        await send_kp_summary(message, sess, lead="Вот текущий черновик КП 👇")
        return

    if intent == "cancel_kp":
    # ✅ старое сообщение оставляем, но отвязываем его от сессии
        sess["kp"]["last_msg_id"] = None

        _reset_kp(user_id)           # сбросит данные КП и cp_key
        sess = _get_session(user_id) # обновим ссылку на сессию

        await message.answer(say(sess, "kp_cleared") + "\nНапиши, что добавляем первым.")
        return



    if intent == "remove":
        # индекс строки либо от DeepSeek, либо из текста
        idx = (action or {}).get("remove_index") if isinstance(action, dict) else None
        if not isinstance(idx, int):
            mm = re.match(r"^(убери|удали)\s+(\d+)\b", low)
            idx = int(mm.group(2)) if mm else None

        items_kp = sess["kp"]["items"]
        if not isinstance(idx, int) or idx < 1 or idx > len(items_kp):
            await message.answer("Не нашёл такую позицию. Напиши <b>покажи КП</b>, чтобы увидеть номера.")
            return

        removed_item = items_kp.pop(idx - 1)

        # пересобираем сигнатуры
        sess["kp"]["sig"] = {_item_signature(it) for it in items_kp if isinstance(it, dict)}

        # синхронизируем твой group_info
        try:
            delete_item_from_group_info(sess, removed_item)
        except Exception:
            logger.exception("delete_item_from_group_info failed")

        await send_kp_summary(message, sess, lead=f"Ок, убрал позицию №{idx}.")
        return

    if intent == "set_qty":
        qty = (action or {}).get("qty") if isinstance(action, dict) else None
        if not isinstance(qty, int):
            qty = _extract_qty(raw)

        if not qty or qty <= 0:
            await message.answer("Сколько штук поставить? Напиши, например: <b>7 шт</b>")
            return

        target = (action or {}).get("target") if isinstance(action, dict) else None
        if not isinstance(target, dict):
            target = {"scope": "last"}

        changed = False
        items_kp = sess["kp"]["items"]
        if not items_kp:
            await message.answer("Пока в КП пусто. Сначала добавь оборудование.")
            return

        scope = target.get("scope") or "last"

        if scope == "last":
            items_kp[-1]["qty"] = qty
            changed = True

            # sync group_info
            try:
                upsert_item_to_group_info(sess, items_kp[-1])
            except Exception:
                logger.exception("upsert_item_to_group_info failed")

        elif scope == "index":
            idx = target.get("index")
            if isinstance(idx, int) and 1 <= idx <= len(items_kp):
                items_kp[idx - 1]["qty"] = qty
                changed = True
                try:
                    upsert_item_to_group_info(sess, items_kp[idx - 1])
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
                            upsert_item_to_group_info(sess, it)
                        except Exception:
                            logger.exception("upsert_item_to_group_info failed")

        if not changed:
            await message.answer(
                "Понял, но не нашёл, к чему применить количество.\n"
                "Напиши <b>покажи КП</b> и укажи номер строки: например <b>поставь 7 для 2</b>."
            )
            return

        await send_kp_summary(message, sess, lead=say(sess, "updated_qty", qty=qty))
        return

    if intent == "get_kp":
        # КП можно получить даже если пользователь ничего не добавил — но смысла нет
        if not sess["kp"]["items"]:
            await message.answer("Пока в черновике пусто. Добавь оборудование, и я соберу КП.")
            return

        # нужен API session для create_new_cp/update_created_kp/save_sieve_pdf
        api_session = globals().get("api_session") or globals().get("session") or globals().get("cp_session")
        if api_session is None:
            logger.warning("No api_session/session/cp_session in globals() for create_cp")
            await message.answer("Не могу сформировать КП: не настроена сессия API.")
            return

        # гарантируем, что key уже создан и не потеряется
        try:
            await ensure_cp_initialized(api_session, str(user_id), sess)
        except Exception:
            logger.exception("ensure_cp_initialized failed")
            await message.answer("Не смог подготовить КП. Попробуй ещё раз.")
            return

        await message.answer(say(sess, "kp_generating"))

        try:
            ok = await api_cp.create_cp(
                api_session,
                str(user_id),
                key=sess["cp"]["cp_key"],
                data_CP=sess["cp"]["data_CP"],
                List_CP=sess["cp"]["List_CP"],
            )
        except Exception:
            logger.exception("create_cp failed")
            ok = False

        if not ok:
            await message.answer("Не получилось сформировать КП. Попробуй чуть позже.")
            return

        # Тут можно потом отправлять pdf/ссылку — пока просто подтверждение
        await message.answer("КП собрано. Если хочешь — добавим ещё позиции или поменяем количество.")
        return

    # 4) intent add/unknown -> пробуем как добавление оборудования
    data = await analyze_equipment(raw, enrich_nomenclature=False)
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

    # qty из текста — проставим всем извлечённым item'ам
    qty_text = _extract_qty(raw)
    if qty_text:
        for it in items:
            it["qty"] = qty_text


    # -----------------------------
    # Новый формат DeepSeek:
    # если type_key == "calc_params", это НЕ оборудование, а распознанные параметры (product/capacity/purpose).
    # В этом случае:
    #  1) показываем распознанные параметры
    #  2) если есть product + capacity_tph -> вызываем api_cp.calculate_separator_by_product_capacity(...)
    #  3) после расчёта добавляем номенклатуру и позиции в КП
    # -----------------------------
    calc_params = next((it for it in items if isinstance(it, dict) and it.get("type_key") == "calc_params"), None)
    if calc_params:
        product = calc_params.get("product")
        capacity = calc_params.get("capacity_tph")
        purpose = calc_params.get("purpose")

        if product and not purpose:
            purpose = "Семена"
            calc_params["purpose"] = purpose

        lines = []
        if product:
            lines.append(f"Продукт: <b>{html.quote(str(product))}</b>")
            lines.append(f"Назначение: <b>{html.quote(str(purpose))}</b>")
        if capacity is not None:
            lines.append(f"Производительность: <b>{html.quote(str(capacity))}</b> т/ч")

        if lines:
            await message.answer("✅ Распознал параметры:\n" + "\n".join(lines))

        # если не хватает данных — не подбираем оборудование и выходим
        if not product or capacity is None:
            return

        api_session = globals().get("api_session") or globals().get("session") or globals().get("cp_session")
        if api_session is None:
            await message.answer("Не могу сделать расчёт: не настроена сессия API.")
            return

        try:
            calc_json = await api_cp.calculate_separator_by_product_capacity(
                api_session,
                product,
                float(capacity),
                purpose or "Семена",
            )
        except Exception:
            logger.exception("calculate_separator_by_product_capacity failed")
            calc_json = None

        if not calc_json:
            # если твой API ещё не подключён/вернул пусто — просто выходим после показа параметров
            return

        nom = await get_nomenclature_ru()
        items_calc = _items_from_calc_response(calc_json, nom)

        # если пользователь указал "N шт" — применяем только к фотосепаратору
        if qty_text:
            for it in items_calc:
                if it.get("type_key") == "photo_sorter":
                    it["qty"] = qty_text

        # номенклатура после расчёта (включая доп. оборудование по id_row)
        try:
            nom = await get_nomenclature_ru()

            if nom:
                ds_final = enrich_ds_json_with_nomenclature(
                    json.dumps({"items": items_calc}, ensure_ascii=False),
                    nom
                )
                items_calc = [it for it in (json.loads(ds_final).get("items") or []) if isinstance(it, dict)]
        except Exception:
            logger.exception("Post-calc nomenclature enrich failed")

        try:
            await ensure_cp_initialized(api_session, str(user_id), sess)
        except Exception:
            logger.exception("ensure_cp_initialized failed (calc_params)")

        added, updated = _add_items_to_kp(sess, items_calc)

        if added == 0 and updated == 0:
            await send_kp_summary(message, sess, lead=say(sess, "already"))
            return

        if added == 1:
            await send_kp_summary(message, sess, lead=say(sess, "added", item=_fmt_item_brief(sess["kp"]["items"][-1])))
        else:
            await send_kp_summary(message, sess, lead=say(sess, "added_many", count=added))
        return


    # -----------------------------
    # Если пользователь указал продукт и/или производительность (т/ч),
    # но НЕ указал конкретную модель оборудования:
    #   - если есть И продукт, И производительность → считаем через API (Scenario 2 ниже)
    #   - иначе просто возвращаем распознанные параметры и выходим
    # -----------------------------
    has_product_or_capacity = any(
        (it.get("product") or it.get("capacity_tph") is not None)
        for it in items
        if isinstance(it, dict)
    )
    has_explicit_model = any(
        (it.get("model") not in (None, "", "null"))
        for it in items
        if isinstance(it, dict)
    )

    if has_product_or_capacity and not has_explicit_model:
        # берём первый item, где есть product/capacity
        seed = None
        for it in items:
            if not isinstance(it, dict):
                continue
            if it.get("product") or it.get("capacity_tph") is not None:
                seed = it
                break

        product = seed.get("product") if seed else None
        capacity = seed.get("capacity_tph") if seed else None
        purpose = seed.get("purpose") if seed else None

        # если назначение не уточнили — дефолт "Семена" (если продукт есть)
        if product and not purpose:
            purpose = "Семена"
            if seed is not None:
                seed["purpose"] = purpose

        # всегда сообщаем, что распознали (это полезно для пользователя/логов)
        parts = []
        if product:
            parts.append(f"Продукт: <b>{html.quote(str(product))}</b>")
        if product:
            parts.append(f"Назначение: <b>{html.quote(str(purpose))}</b>")
        if capacity is not None:
            parts.append(f"Производительность: <b>{html.quote(str(capacity))}</b> т/ч")

        if parts:
            await message.answer("✅ Распознал параметры:\n" + "\n".join(parts))

        # если не хватает данных для расчёта — выходим (не подбираем оборудование)
        if not product or capacity is None:
            if not parts:
                await message.answer("Не смог распознать продукт/производительность.")
            return


    # # -----------------------------
    # # Scenario 2: если в запросе есть продукт + производительность (т/ч),
    # # то сначала считаем через твой API, и только потом добавляем номенклатуру.
    # # -----------------------------
    # calc_seed = _need_calc_scenario(items)
    # if calc_seed:
    #     api_session = globals().get("api_session") or globals().get("session") or globals().get("cp_session")
    #     if api_session is not None:
    #         try:
    #             # ✅ МЕСТО ВЫЗОВА ТВОЕГО API:

    #             calc_json = await api_cp.calculate_separator_by_product_capacity(
    #                 api_session,
    #                 calc_seed["product"],
    #                 calc_seed["capacity_tph"],
    #                 calc_seed.get("purpose", "Семена"),
    #             )
    #         except Exception:
    #             logger.exception("calculate_separator_by_product_capacity failed")
    #             calc_json = None

    #         if calc_json:
    #             items_calc = _items_from_calc_response(calc_json)

    #             # проставим qty из текста (если пользователь указал "2 шт"), на фотосепаратор
    #             if qty_text:
    #                 for it in items_calc:
    #                     if it.get("type_key") == "photo_sorter":
    #                         it["qty"] = qty_text

    #             # номенклатуру добавляем ПОСЛЕ расчёта (в т.ч. для доп. оборудования по id_row)
    #             try:
    #                 nom = await get_nomenclature_ru()
    #                 if nom:
    #                     ds_final = enrich_ds_json_with_nomenclature(json.dumps({"items": items_calc}, ensure_ascii=False), nom)
    #                     items_calc = [it for it in (json.loads(ds_final).get("items") or []) if isinstance(it, dict)]
    #             except Exception:
    #                 logger.exception("Post-calc nomenclature enrich failed")

    #             # гарантируем CP key, чтобы синхронизировать group_info
    #             try:
    #                 await ensure_cp_initialized(api_session, str(user_id), sess)
    #             except Exception:
    #                 logger.exception("ensure_cp_initialized failed (calc scenario)")

    #             added, updated = _add_items_to_kp(sess, items_calc)

    #             if added == 0 and updated == 0:
    #                 await send_kp_summary(message, sess, lead=say(sess, "already"))
    #                 return

    #             await send_kp_summary(message, sess, lead=say(sess, "added_many", count=added) if added > 1 else say(sess, "added", item=_fmt_item_brief(sess["kp"]["items"][-1])))
    #             return

    # если нужна модель — уходим в режим выбора
    pending_item = _find_pending_model_item(data)
    if pending_item:
        # добавим то, что уже готово (pending пропустится внутри _add_items_to_kp)
        # CP инициализируем только если есть "готовые" позиции (с id_row)
        ready = [it for it in items if it.get("nomenclature_id_row") and not it.get("nomenclature_error")]
        if ready:
            api_session = globals().get("api_session") or globals().get("session") or globals().get("cp_session")
            if api_session is not None:
                try:
                    await ensure_cp_initialized(api_session, str(user_id), sess)
                except Exception:
                    logger.exception("ensure_cp_initialized failed (ready items)")

        _add_items_to_kp(sess, items)

        # qty запомним в pending_item (чтобы не потерялось)
        if qty_text and not pending_item.get("qty"):
            pending_item["qty"] = qty_text

        sess["awaiting_model"] = True
        sess["pending_data"] = data

        what = (pending_item.get("name_ru") or "оборудованию").lower()
        await message.answer(say(sess, "ask_model", what=what) + "\n\n" + _format_model_choice_request(pending_item))
        return

    # если items "готовые" — инициализируем CP один раз и добавляем
    ready = [it for it in items if it.get("nomenclature_id_row") and not it.get("nomenclature_error")]
    if ready:
        api_session = globals().get("api_session") or globals().get("session") or globals().get("cp_session")
        if api_session is not None:
            try:
                await ensure_cp_initialized(api_session, str(user_id), sess)
            except Exception:
                logger.exception("ensure_cp_initialized failed (ready items)")

    added, updated = _add_items_to_kp(sess, items)

    if added == 0 and updated == 0:
        await send_kp_summary(message, sess, lead=say(sess, "already"))
        return

    # “человеческое” подтверждение
    lead_parts = []
    if added == 1:
        new_item = sess["kp"]["items"][-1] if sess["kp"]["items"] else items[0]
        lead_parts.append(say(sess, "added", item=_fmt_item_brief(new_item)))
    elif added > 1:
        lead_parts.append(say(sess, "added_many", count=added))

    if updated and qty_text:
        lead_parts.append(say(sess, "updated_qty", qty=qty_text))

    lead = " ".join([p for p in lead_parts if p]).strip() if lead_parts else None
    await send_kp_summary(message, sess, lead=lead)

# -----------------------------
# Inline KP actions
# -----------------------------
@dp.callback_query(F.data == CB_KP_GET)
async def cb_kp_get(callback: types.CallbackQuery):
    user_id = int(callback.from_user.id)
    sess = _get_session(user_id)
    await callback.answer()

    if not sess["kp"]["items"]:
        await bot.send_message(user_id, "Пока черновик пуст. Напиши, что добавить (например: <b>фотосепаратор 2.2</b>).")
        return

    if api_session is None:
        logger.warning("api_session is None")
        await bot.send_message(user_id, "Не могу сформировать КП: не настроена сессия API.")
        return

    try:
        await ensure_cp_initialized(api_session, str(user_id), sess)
    except Exception:
        logger.exception("ensure_cp_initialized failed")
        await bot.send_message(user_id, "Не смог подготовить КП. Попробуй ещё раз.")
        return

    # статус (не технический)
    await bot.send_message(user_id, say(sess, "kp_generating"))

    try:
        ok = await api_cp.create_cp(
            api_session,
            str(user_id),
            key=sess["cp"]["cp_key"],
            data_CP=sess["cp"]["data_CP"],
            List_CP=sess["cp"]["List_CP"],
        )
    except Exception:
        logger.exception("create_cp failed")
        ok = False

    if not ok:
        await bot.send_message(user_id, "Не получилось сформировать КП. Попробуй чуть позже.")
        return

    await bot.send_message(user_id, "КП сформировано. Если нужно — добавим ещё позиции или поправим количество.")
    # показываем актуальный состав (обновит/заменит прошлое сообщение)
    await send_kp_summary_to_chat(user_id, sess)


@dp.callback_query(F.data == CB_KP_CANCEL)
async def cb_kp_cancel(callback: types.CallbackQuery):
    user_id = int(callback.from_user.id)
    sess = _get_session(user_id)
    await callback.answer()

    # ✅ оставляем старое сообщение с составом как “архив”
    sess["kp"]["last_msg_id"] = None

    _reset_kp(user_id)
    sess = _get_session(user_id)

    await bot.send_message(user_id, say(sess, "kp_cleared") + "\nНапиши, что добавляем первым.")




# -----------------------------
# /start
# -----------------------------
@dp.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        return

    user_id = str(message.from_user.id)
    username = message.from_user.username
    botCl = replyButton(user_id, username)

    if username is None:
        await message.answer(phrases.USERNAME_MESSAGE, reply_markup=botCl.delete())
        return

    payload = (command.args or "").strip()

    if payload.startswith("bt_"):
        deal_number = payload[3:].strip()
        base_url = SETTINGS.web_app_offer_url
        kp_url = (
            f"{base_url}"
            f"?deal={urllib.parse.quote(deal_number)}"
            f"&tg_id={urllib.parse.quote(user_id)}"
            f"&username={urllib.parse.quote(username)}"
        )
        kb = InlineKeyboardBuilder()
        kb.button(text="Создать КП", web_app={"url": kp_url})
        await message.answer("Перейдите чтобы увидеть КП", reply_markup=kb.as_markup())
        return

    if payload.startswith("kp_"):
        key_cp = payload[3:].strip()
        base_url = SETTINGS.web_app_offer_url
        kp_url = (
            f"{base_url}"
            f"?keyCP={urllib.parse.quote(key_cp)}"
            f"&tg_id={urllib.parse.quote(user_id)}"
            f"&username={urllib.parse.quote(username)}"
        )
        kb = InlineKeyboardBuilder()
        kb.button(text="Посмотреть КП", web_app={"url": kp_url})
        await message.answer(f"Перейдите чтобы увидеть КП", reply_markup=kb.as_markup())
        return

    is_exists = await workUser.is_user_exists(user_id)

    if is_exists is False:
        if payload:
            try:
                requests.get(f"{API_URL}/shift_lock/{payload}", timeout=10)
            except Exception:
                pass

        await message.answer(phrases.REQUEST_CONTACT_MESSAGE, reply_markup=botCl.auth())
        return

    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}!\n{phrases.OLD_USER}\nРады тебя видеть",
        reply_markup=botCl.visits(is_exists),
    )

    video1 = FSInputFile("Video/colorsorter.mp4")
    thumb1 = FSInputFile("Video/colorsorter.jpg")
    await message.answer_video(
        video=video1,
        caption="Инструкция 1: Как пользоваться ботом",
        thumb=thumb1,
        supports_streaming=True,
    )

    video2 = FSInputFile("Video/elevator.mp4")
    thumb2 = FSInputFile("Video/elevator.jpg")
    await message.answer_video(
        video=video2,
        caption="Инструкция 2: Калькулятор элеваторов",
        thumb=thumb2,
        supports_streaming=True,
    )


# -----------------------------
# Voice / Audio
# -----------------------------
@dp.message(F.voice | F.audio)
async def handle_voice_or_audio(message: Message) -> None:
    status_msg = await message.answer("Получаю файл для обработки…")
    transcript = await transcribe_voice_message(bot, message, status_msg)
    if not transcript:
        return
    try:
        await status_msg.delete()
    except Exception:
        pass

    await process_user_equipment_message(message, transcript)


@dp.message(F.contact)
async def contact_handler(message: Message) -> None:
    """
    Этот обработчик получает контактную информацию пользователя
    """
    contact = message.contact
    botCl = replyButton(str(message.from_user.id), message.from_user.username)
    if contact!= None:
        is_exists = await workUser.is_user_write(message)
        await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!\n{phrases.OLD_USER} \nРады тебя видеть" , reply_markup=botCl.visits(''))
    else:
        await message.answer(phrases.REQUEST_CONTACT_MESSAGE, reply_markup= botCl.auth())
# -----------------------------
# Text

# -----------------------------
# Legacy menu button handlers restored from old version
# -----------------------------
@dp.message(F.text.lower() == "назад")
async def with_puree(message: types.Message):
    if message.from_user.id not in commandID:
        await message.answer("Нет доступа к команде")
        return
    botCl = replyButton(str(message.from_user.id), message.from_user.username)
    await message.answer("Возврат в меню", reply_markup=botCl.visits("manager"))


@dp.message(F.text.lower() == "обновить бота")
async def update_bot_broadcast(message: types.Message):
    if message.from_user.id not in [769657026, 5232657726]:
        await message.answer("Нет доступа к команде")
        return

    # метод is_users мог быть переименован в новых версиях api_bot — пробуем безопасно
    try:
        users = await workUser.is_users()
    except Exception:
        logger.exception("workUser.is_users() failed")
        await message.answer("Не удалось получить список пользователей для рассылки (is_users недоступен).")
        return

    await message.answer(f"Начали рассылку по {len(users)} пользователям")
    for user in users:
        try:
            user_id = user[0]
            messag = (
                "Привет, мы обновили функционал.\n"
                "Чтобы не было проблем, нажми /start ещё раз"
            )
            await bot.send_message(user_id, messag, reply_markup=types.ReplyKeyboardRemove())
        except Exception:
            logger.exception("Broadcast failed for user")
            try:
                await bot.send_message(NOTIFY_ADMIN_ID, f"Чата с пользователем {user_id} не существует")
            except Exception:
                logger.exception("Failed to notify admin about missing chat")
        await asyncio.sleep(1)


@dp.message(F.text.lower() == "статистика")
async def show_company_statistics_menu(message: types.Message):
    if message.from_user.id not in commandID:
        await message.answer("Нет доступа к команде")
        return
    botCl = replyButton(str(message.from_user.id), message.from_user.username)

    company = await workUser.is_company()
    await message.answer("По какой компании прислать статистику", reply_markup=botCl.statistics(company))


@dp.message(F.text.lower() == "статистика переходов")
async def show_link_stats_menu(message: types.Message):
    if message.from_user.id not in commandID:
        await message.answer("Нет доступа к команде")
        return
    botCl = replyButton(str(message.from_user.id), message.from_user.username)
    await message.answer("Выберете действие", reply_markup=botCl.choice_stat())


# -----------------------------
# Link-stat callbacks restored from old version
# -----------------------------
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "Create_linkStat"))
async def callbacks_create_linkstat_hint(callback: types.CallbackQuery, callback_data: NumbersCallbackFactory):
    text = (
        "Введите название ссылки\n"
        "Чтобы система поняла что нужно сделать, припишите в начале\n\n"
        "Create_linkStat"
    )
    await bot.send_message(callback.from_user.id, text)


@dp.callback_query(NumbersCallbackFactory.filter(F.action == "Views_linkStat"))
async def callbacks_views_linkstat(callback: types.CallbackQuery, callback_data: NumbersCallbackFactory):
    """
    Старый обработчик просмотра статистики по ссылкам.
    В новых версиях api_bot некоторые методы могли быть изменены — поэтому сделано безопасно.
    """
    try:
        stat = await workUser.get_link(callback.from_user.id)
        week_ago, month_ago = workUser.get_date_ranges()
        link_stats = workUser.calculate_link_stats(stat, week_ago, month_ago)
        message = workUser.format_stats_message(link_stats)
        await callback.message.answer(message, parse_mode="Markdown")
    except Exception:
        logger.exception("Views_linkStat handler failed")
        await callback.message.answer(
            "Не удалось получить статистику по ссылкам (возможна несовместимость методов get_link/get_date_ranges)."
        )




@dp.message(Command(commands=["+"]))
async def cmd_add_mng_role(message: types.Message):
    print('Command "/+"')
    print("group chat id:", message.chat.id)

    if message.chat.id != ALLOWED_CHAT_ID:
        print("ALLOWED_CHAT_ID: INCORRECT")
        return

    user_id = message.from_user.id

    try:
        resp = requests.get(f"{API_URL}/reg_manger/{user_id}", timeout=10)
        resp.raise_for_status()
    except Exception as e:
        await message.answer(f"Не удалось выдать роль менеджера. Ошибка: {e}")
        return

    # Пишем пользователю в ЛС + убираем ReplyKeyboard
    try:
        await message.bot.send_message(
            chat_id=user_id,
            text="✅ Роль менеджера выдана.\n\nТеперь нажми /start ещё раз.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await message.answer("Готово ✅ Я написал тебе в личку.")
    except TelegramForbiddenError:
        # Пользователь не запускал бота в ЛС / запретил сообщения
        await message.answer(
            "✅ Роль менеджера выдана.\n\n"
            "Я не могу написать тебе в личку (ты ещё не открыл чат с ботом).\n"
            "Открой бота и нажми /start."
        )
# -----------------------------
@dp.message(F.text)
async def handle_text(message: Message) -> None:
    txt = message.text or ""

    # не мешаем кнопкам меню
    if txt.strip().lower() in ("назад", "обновить бота", "статистика", "статистика переходов"):
        return

    # link stat create (как было)
    if "Create_linkStat" in txt:
        if message.from_user.id not in commandID:
            await message.answer("Нет доступа к команде")
            return

        name_link = txt.replace("Create_linkStat", "", 1).strip()
        if not name_link:
            await message.answer("Напиши название после Create_linkStat, например:\nCreate_linkStat Моя ссылка")
            return

        en_name_link = workUser.translate_to_english(name_link)
        data = {
            "id_tg": message.from_user.id,
            "namelink": name_link,
            "link": f"https://t.me/Csort_official_bot?start={en_name_link}",
            "count_users": 0,
        }

        stat = await workUser.create_link(data)
        if stat == 403:
            await message.answer("У вас уже есть ссылка под таким названием")
            return

        await message.answer(f"Держите ссылку для отслеживания статистики:\n\n{data['link']}")
        return

    await process_user_equipment_message(message, txt)


# -----------------------------
# Other legacy handlers (stats etc.) — оставлены как есть
# -----------------------------



@dp.message(Command("numbers_fab"))
async def cmd_numbers_fab(message: Message):
    botCl = replyButton(str(message.from_user.id), message.from_user.username)
    company = await workUser.is_company()
    await message.answer("Выберете компанию", reply_markup=botCl.statistics(company))


@dp.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery, 
        callback_data: NumbersCallbackFactory):
    botCl = replyButton(str(callback.from_user.id), callback.from_user.username)
    print((callback_data.value).replace("'","''",len(callback_data.value.split("'"))-1))


    stat = await workUser.company_stat((callback_data.value).replace("'","''",len(callback_data.value.split("'"))-1))
    print(stat)

    stat_week = stat['week']
    stat_month = stat['month']
    result_week = botCl.process_statistics(stat_week)
    result_month = botCl.process_statistics(stat_month)
    
    date_week = botCl.format_date_range(7)
    date_month = botCl.format_date_range(31)

    text = (
        f"📊 {html.bold(f'Статистика компании {callback_data.value}')}\n\n"
        
        f"📈 {html.bold('Коммерческие предложения')}\n"
        f"  └ {html.bold(f'За неделю ({date_week})')}:\n"
        f"     • Договоров: {result_week['КП']['Договор']['count']} на сумму {botCl.format_numbers(result_week['КП']['Договор']['sum'])}\n"
        f"     • Счетов: {result_week['КП']['Счет']['count']} на сумму {botCl.format_numbers(result_week['КП']['Счет']['sum'])}\n"
        f"     • КП менеджеров: {result_week['КП']['КП']['count']} на сумму {botCl.format_numbers(result_week['КП']['КП']['sum'])}\n"
        f"     • КП клиентов: {result_week['КП']['КП_клиент']['count']} на сумму {botCl.format_numbers(result_week['КП']['КП_клиент']['sum'])}\n\n"

        f"  └ {html.bold(f'За месяц ({date_month})')}:\n"
        f"     • Договоров: {result_month['КП']['Договор']['count']} на сумму {botCl.format_numbers(result_month['КП']['Договор']['sum'])}\n"
        f"     • Счетов: {result_month['КП']['Счет']['count']} на сумму {botCl.format_numbers(result_month['КП']['Счет']['sum'])}\n"
        f"     • КП менеджеров: {result_month['КП']['КП']['count']} на сумму {botCl.format_numbers(result_month['КП']['КП']['sum'])}\n"
        f"     • КП клиентов: {result_week['КП']['КП_клиент']['count']} на сумму {botCl.format_numbers(result_week['КП']['КП_клиент']['sum'])}\n\n"

        f"  └ {html.italic('Менеджеры:')}\n"
        f"     • Договора: \n"
        f"       {botCl.format_stat_manag(result_month['КП']['Договор']['stat_manag']).replace(': ', ': ').replace(chr(10), chr(10) + '       ')}\n"
        f"     • Счета: \n"
        f"       {botCl.format_stat_manag(result_month['КП']['Счет']['stat_manag']).replace(': ', ': ').replace(chr(10), chr(10) + '       ')}\n"
        f"     • КП: \n"
        f"       {botCl.format_stat_manag(result_month['КП']['КП']['stat_manag']).replace(': ', ': ').replace(chr(10), chr(10) + '       ')}\n\n"
        
        "───────────────────────────────────\n\n"
        
        f"🔧 {html.bold('Сервисные услуги')}\n"
        f"  └ {html.bold(f'За неделю ({date_week})')}:\n"
        f"     • Договоров: {result_week['Сервис']['Договор']['count']} на сумму {botCl.format_numbers(result_week['Сервис']['Договор']['sum'])}\n"
        f"     • Счетов: {result_week['Сервис']['Счет']['count']} на сумму {botCl.format_numbers(result_week['Сервис']['Счет']['sum'])}\n"
        
        f"  └ {html.bold(f'За месяц ({date_month})')}:\n"
        f"     • Договоров: {result_month['Сервис']['Договор']['count']} на сумму {botCl.format_numbers(result_month['Сервис']['Договор']['sum'])}\n"
        f"     • Счетов: {result_month['Сервис']['Счет']['count']} на сумму {botCl.format_numbers(result_month['Сервис']['Счет']['sum'])}\n"
        
        f"  └ {html.italic('Менеджеры:')}\n"
        f"     • Договора: \n"
        f"       {botCl.format_stat_manag(result_month['Сервис']['Договор']['stat_manag']).replace(': ', ': ').replace(chr(10), chr(10) + '       ')}\n"
        f"     • Счета: \n"
        f"       {botCl.format_stat_manag(result_month['Сервис']['Счет']['stat_manag']).replace(': ', ': ').replace(chr(10), chr(10) + '       ')}\n"
       
    )
        
    await bot.send_message(callback.from_user.id, text) 



async def main() -> None:
    """Вход: запуск python main.py. Выход: старт long-polling aiogram."""
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()



if __name__ == "__main__":
    asyncio.run(main())
