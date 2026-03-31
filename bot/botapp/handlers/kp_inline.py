"""
Inline-кнопки черновика КП.

Вход:
- callback на кнопки Получить КП / Отменить КП.

Выход:
- формирование КП или сброс текущей пользовательской сессии.
"""

from __future__ import annotations

import logging
from aiogram import F, types

import api_cp
from botapp.services.kp_service import CB_KP_CANCEL, CB_KP_GET

logger = logging.getLogger(__name__)


def register(router, *, bot, session_mgr, kp_service, cp_manager, api_session_getter):
    """Вход: зависимости inline-хендлера. Выход: зарегистрированные callback-хендлеры."""
    @router.callback_query(F.data == CB_KP_GET)
    async def cb_kp_get(callback: types.CallbackQuery):
        user_id = int(callback.from_user.id)
        sess = session_mgr.get(user_id)
        await callback.answer()

        if not sess.kp.items:
            await bot.send_message(user_id, "Пока черновик пуст. Напиши, что добавить (например: <b>фотосепаратор 2.2</b>).")
            return

        api_session = api_session_getter()
        if api_session is None:
            await bot.send_message(user_id, "Не могу сформировать КП: не настроена сессия API.")
            return

        try:
            await cp_manager.ensure_initialized(api_session, str(user_id), sess)
        except Exception:
            logger.exception("ensure_initialized failed")
            await bot.send_message(user_id, "Не смог подготовить КП. Попробуй ещё раз.")
            return

        await bot.send_message(user_id, kp_service.say(sess, "kp_generating"))

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
            await bot.send_message(user_id, "Не получилось сформировать КП. Попробуй чуть позже.")
            return

        await bot.send_message(user_id, "КП сформировано. Если нужно — добавим ещё позиции или поправим количество.")
        await kp_service.send_kp_summary_to_chat(bot, user_id, sess)

    @router.callback_query(F.data == CB_KP_CANCEL)
    async def cb_kp_cancel(callback: types.CallbackQuery):
        user_id = int(callback.from_user.id)
        sess = session_mgr.get(user_id)
        await callback.answer()

        sess.kp.last_msg_id = None
        session_mgr.reset(user_id)
        sess = session_mgr.get(user_id)

        await bot.send_message(user_id, kp_service.say(sess, "kp_cleared") + "\nНапиши, что добавляем первым.")
