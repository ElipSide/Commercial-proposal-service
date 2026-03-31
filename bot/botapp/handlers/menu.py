"""
Меню- и админ-хендлеры refactor-версии.

Вход:
- текстовые команды меню и service-команды администратора.

Выход:
- клавиатуры меню, broadcast и служебные ответы пользователю.
"""

from __future__ import annotations

import asyncio
import logging
import requests

from aiogram import F, types
from aiogram.filters import Command
from aiogram.types import Message

import phrases
from classes import replyButton
from env_settings import get_settings


SETTINGS = get_settings()

logger = logging.getLogger(__name__)


def register(
    router,
    *,
    bot,
    workUser,
    command_ids: list[int],
    api_url: str,
    allowed_chat_id: int,
):
    @router.message(F.contact)
    async def contact_handler(message: Message) -> None:
        contact = message.contact
        botCl = replyButton(str(message.from_user.id), message.from_user.username)
        if contact is not None:
            await workUser.is_user_write(message)
            await message.answer(
                f"Привет, <b>{message.from_user.full_name}</b>!\n{phrases.OLD_USER} \nРады тебя видеть",
                reply_markup=botCl.visits(""),
            )
        else:
            await message.answer(phrases.REQUEST_CONTACT_MESSAGE, reply_markup=botCl.auth())

    @router.message(Command(commands=["+"]))
    async def cmd_add_mng_role(message: types.Message):
        print('Command "/+"')
        print(message.chat.id)

        if message.chat.id != allowed_chat_id:
            print("ALLOWED_CHAT_ID: INCORRECT")
            return

        user_id = message.from_user.id

        try:
            resp = requests.get(f"{api_url}/reg_manger/{user_id}", timeout=10)
            resp.raise_for_status()
        except Exception as e:
            await message.answer(f"Не удалось выдать роль менеджера. Ошибка: {e}")
            return

        # Удаляем кнопки у пользователя (убираем ReplyKeyboard)
        await message.answer(
            "✅ Роль менеджера выдана.\n\nТеперь нажми /start ещё раз.",
            reply_markup=types.ReplyKeyboardRemove()
    )
        
    @router.message(F.text.lower() == "назад")
    async def back_to_menu(message: types.Message):
        if message.from_user.id not in command_ids:
            await message.answer("Нет доступа к команде")
            return
        botCl = replyButton(str(message.from_user.id), message.from_user.username)
        await message.answer("Возврат в меню", reply_markup=botCl.visits("manager"))

    @router.message(F.text.lower() == "обновить бота")
    async def update_bot_broadcast(message: types.Message):
        if message.from_user.id not in SETTINGS.update_bot_allowed_ids:
            await message.answer("Нет доступа к команде")
            return

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
                    await bot.send_message(5232657726, f"Чата с пользователем {user_id} не существует")
                except Exception:
                    logger.exception("Failed to notify admin about missing chat")
            await asyncio.sleep(1)

    @router.message(F.text.lower() == "статистика")
    async def show_company_statistics_menu(message: types.Message):
        if message.from_user.id not in command_ids:
            await message.answer("Нет доступа к команде")
            return
        botCl = replyButton(str(message.from_user.id), message.from_user.username)
        company = await workUser.is_company()
        await message.answer("По какой компании прислать статистику", reply_markup=botCl.statistics(company))

    @router.message(F.text.lower() == "статистика переходов")
    async def show_link_stats_menu(message: types.Message):
        if message.from_user.id not in command_ids:
            await message.answer("Нет доступа к команде")
            return
        botCl = replyButton(str(message.from_user.id), message.from_user.username)
        await message.answer("Выберете действие", reply_markup=botCl.choice_stat())



