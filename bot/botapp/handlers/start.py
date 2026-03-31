"""
Хендлер /start и открытие WebApp-коммерческих предложений.

Вход:
- команда /start и payload Telegram deep-link.

Выход:
- приветствие, кнопки WebApp и обучающие видео.
"""

from __future__ import annotations

import urllib.parse
import requests

from aiogram import html, types
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.types import FSInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import phrases
from classes import replyButton
from env_settings import get_settings


SETTINGS = get_settings()


def register(router, *, workUser, api_url: str):
    """Вход: router, workUser и api_url. Выход: зарегистрированные start-хендлеры."""
    @router.message(CommandStart())
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
            await message.answer("Перейдите чтобы увидеть КП", reply_markup=kb.as_markup())
            return

        is_exists = await workUser.is_user_exists(user_id)

        if is_exists is False:
            if payload:
                try:
                    requests.get(f"{api_url}/shift_lock/{payload}", timeout=10)
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
