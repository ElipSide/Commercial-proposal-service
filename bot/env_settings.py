"""
Централизованная конфигурация проекта.

Вход:
- файл creeds.env в корне проекта.

Выход:
- объект Settings со всеми токенами, URL, ID и шаблонами,
  которые не должны быть захардкожены в git.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import dotenv


ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / "creeds.env"
dotenv.load_dotenv(ENV_PATH)


def _require(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is required in {ENV_PATH}")
    return value


def _optional(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def _int(name: str, default: int | None = None) -> int:
    raw = _optional(name, str(default) if default is not None else "")
    if raw == "":
        raise RuntimeError(f"Environment variable {name} is required in {ENV_PATH}")
    return int(raw)


def _int_list(name: str) -> list[int]:
    raw = _require(name)
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    bot_token: str
    api_url: str
    allowed_chat_id: int
    command_ids: list[int]
    button_command_ids: list[int]
    update_bot_allowed_ids: list[int]
    update_bot_button_owner_id: int
    notify_admin_id: int
    default_lang: str
    api_base_url: str
    api_calc_base_url: str
    nomenclature_url_ru: str
    nom_ttl_sec: int
    web_app_sorting_url: str
    web_app_offer_url: str
    web_app_service_url: str
    web_app_separator_url: str
    voice_upload_url: str
    voice_ws_status_url_tpl: str
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_chat_model: str
    telegram_bot_username: str
    telegram_start_url_base: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Возвращает один кэшированный объект настроек для всего приложения."""
    telegram_bot_username = _require("TELEGRAM_BOT_USERNAME")
    return Settings(
        bot_token=_require("BOT_TOKEN"),
        api_url=_require("API_URL"),
        allowed_chat_id=_int("ALLOWED_CHAT_ID"),
        command_ids=_int_list("COMMAND_IDS"),
        button_command_ids=_int_list("BUTTON_COMMAND_IDS"),
        update_bot_allowed_ids=_int_list("UPDATE_BOT_ALLOWED_IDS"),
        update_bot_button_owner_id=_int("UPDATE_BOT_BUTTON_OWNER_ID"),
        notify_admin_id=_int("NOTIFY_ADMIN_ID"),
        default_lang=_require("DEFAULT_LANG"),
        api_base_url=_require("API_BASE_URL"),
        api_calc_base_url=_require("API_CALC_BASE_URL"),
        nomenclature_url_ru=_require("NOMENCLATURE_URL_RU"),
        nom_ttl_sec=_int("NOM_TTL_SEC", 3600),
        web_app_sorting_url=_require("WEB_APP_SORTING_URL"),
        web_app_offer_url=_require("WEB_APP_OFFER_URL"),
        web_app_service_url=_require("WEB_APP_SERVICE_URL"),
        web_app_separator_url=_require("WEB_APP_SEPARATOR_URL"),
        voice_upload_url=_require("VOICE_UPLOAD_URL"),
        voice_ws_status_url_tpl=_require("VOICE_WS_STATUS_URL_TPL"),
        deepseek_api_key=_optional("API_TOKEN_DEEPSEEK"),
        deepseek_base_url=_require("DEEPSEEK_BASE_URL"),
        deepseek_chat_model=_require("DEEPSEEK_CHAT_MODEL"),
        telegram_bot_username=telegram_bot_username,
        telegram_start_url_base=f"https://t.me/{telegram_bot_username}?start=",
    )
