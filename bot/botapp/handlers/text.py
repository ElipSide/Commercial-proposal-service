"""
Основной текстовый хендлер refactor-версии.

Вход:
- произвольный текст пользователя.

Выход:
- либо служебная ссылка статистики, либо передача текста в DialogService.
"""

from __future__ import annotations

from aiogram import F
from aiogram.types import Message

from env_settings import get_settings


SETTINGS = get_settings()


def register(router, *, dialog_service, workUser, command_ids: list[int], api_session_getter):
    """Вход: router, dialog_service, workUser и api_session_getter. Выход: зарегистрированный text-хендлер."""
    @router.message(F.text)
    async def handle_text(message: Message) -> None:
        txt = message.text or ""
        low = txt.strip().lower()

        # don't intercept menu buttons handled elsewhere
        if low in ("назад", "обновить бота", "статистика", "статистика переходов"):
            return

        # link stat create (as in old flow)
        if "Create_linkStat" in txt:
            if message.from_user.id not in command_ids:
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
                "link": f"{SETTINGS.telegram_start_url_base}{en_name_link}",
                "count_users": 0,
            }

            stat = await workUser.create_link(data)
            if stat == 403:
                await message.answer("У вас уже есть ссылка под таким названием")
                return

            await message.answer(f"Держите ссылку для отслеживания статистики:\n\n{data['link']}")
            return

        await dialog_service.process_user_message(message, txt, api_session_getter())
