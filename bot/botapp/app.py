"""
Сборка refactor-версии приложения botapp.

Вход:
- BotConfig с токеном, URL и служебными ID.

Выход:
- AppState с готовым Bot/Dispatcher/сервисами/сессиями.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Router

import api_bot

from botapp.config import BotConfig
from botapp.services.nomenclature_service import NomenclatureService
from botapp.services.session_store import SessionManager
from botapp.services.cp_manager import CPManager
from botapp.services.kp_service import KPService
from botapp.services.deepseek_service import DeepSeekService
from botapp.services.dialog_service import DialogService

from botapp.handlers import start, voice, menu, stats, kp_inline, text


logger = logging.getLogger(__name__)


@dataclass
class AppState:
    bot: Bot
    dp: Dispatcher
    workUser: any
    api_session: Optional[aiohttp.ClientSession]
    session_mgr: SessionManager
    nom_service: NomenclatureService
    cp_manager: CPManager
    kp_service: KPService
    deepseek: DeepSeekService
    dialog: DialogService


async def create_app(config: BotConfig) -> AppState:
    """Вход: BotConfig. Выход: полностью собранный AppState."""
    dp = Dispatcher()
    bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    workUser = api_bot.workingUsers()

    api_session = aiohttp.ClientSession()

    session_mgr = SessionManager()
    nom_service = NomenclatureService(config.nomenclature_url_ru, ttl_sec=config.nom_ttl_sec)
    cp_manager = CPManager()
    kp_service = KPService()
    deepseek = DeepSeekService(nom_service)
    dialog = DialogService(
        session_mgr=session_mgr,
        nom_service=nom_service,
        deepseek=deepseek,
        kp=kp_service,
        cp=cp_manager,
        workUser=workUser,
    )

    router = Router()

    api_session_getter = lambda: api_session

    # register handlers
    start.register(router, workUser=workUser, api_url=config.api_url)
    voice.register(router, dialog_service=dialog, api_session_getter=api_session_getter)
    menu.register(
        router,
        bot=bot,
        workUser=workUser,
        command_ids=config.command_ids,
        api_url=config.api_url,
        allowed_chat_id=config.allowed_chat_id,
    )
    stats.register(router, bot=bot, workUser=workUser, command_ids=config.command_ids)
    kp_inline.register(
        router,
        bot=bot,
        session_mgr=session_mgr,
        kp_service=kp_service,
        cp_manager=cp_manager,
        api_session_getter=api_session_getter,
    )
    text.register(
        router,
        dialog_service=dialog,
        workUser=workUser,
        command_ids=config.command_ids,
        api_session_getter=api_session_getter,
    )

    dp.include_router(router)

    return AppState(
        bot=bot,
        dp=dp,
        workUser=workUser,
        api_session=api_session,
        session_mgr=session_mgr,
        nom_service=nom_service,
        cp_manager=cp_manager,
        kp_service=kp_service,
        deepseek=deepseek,
        dialog=dialog,
    )


async def shutdown(state: AppState) -> None:
    """Вход: AppState. Выход: закрытая aiohttp-сессия приложения."""
    if state.api_session:
        await state.api_session.close()
        state.api_session = None
