"""
Голосовой хендлер refactor-версии.

Вход:
- voice/audio сообщение Telegram.

Выход:
- transcript и передача результата в DialogService.
"""

from __future__ import annotations

from aiogram import F
from aiogram.types import Message

from recognition import transcribe_voice_message


def register(router, *, dialog_service, api_session_getter):
    """Вход: router, dialog_service и api_session_getter. Выход: зарегистрированный voice-хендлер."""
    @router.message(F.voice | F.audio)
    async def handle_voice_or_audio(message: Message) -> None:
        status_msg = await message.answer("Получаю файл для обработки…")
        transcript = await transcribe_voice_message(message.bot, message, status_msg)
        if not transcript:
            return
        try:
            await status_msg.delete()
        except Exception:
            pass

        await dialog_service.process_user_message(message, transcript, api_session_getter())
