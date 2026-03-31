"""
Конфигурация refactor-версии botapp.

Вход:
- централизованные env-переменные из creeds.env.

Выход:
- dataclass BotConfig для сборки приложения.
"""
from __future__ import annotations

from dataclasses import dataclass

from env_settings import get_settings


@dataclass(frozen=True)
class BotConfig:
    token: str
    allowed_chat_id: int
    api_url: str
    nomenclature_url_ru: str
    nom_ttl_sec: int
    command_ids: list[int]


def load_config() -> BotConfig:
    """Вход: env-конфигурация. Выход: BotConfig для create_app()."""
    settings = get_settings()
    return BotConfig(
        token=settings.bot_token,
        allowed_chat_id=settings.allowed_chat_id,
        api_url=settings.api_url,
        nomenclature_url_ru=settings.nomenclature_url_ru,
        nom_ttl_sec=settings.nom_ttl_sec,
        command_ids=settings.command_ids,
    )
