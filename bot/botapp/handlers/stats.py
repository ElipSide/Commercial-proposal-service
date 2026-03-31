"""
Хендлеры статистики по компаниям и переходам по ссылкам.

Вход:
- callback-и и команды, связанные со статистикой.

Выход:
- красиво отформатированные отчёты для пользователя.
"""

from __future__ import annotations

import logging

from aiogram import F, html, types
from aiogram.filters import Command
from aiogram.types import Message

from classes import NumbersCallbackFactory, replyButton

logger = logging.getLogger(__name__)


def register(router, *, bot, workUser, command_ids: list[int]):
    """Вход: router, bot, workUser, command_ids. Выход: зарегистрированные stats-хендлеры."""
    @router.message(Command("numbers_fab"))
    async def cmd_numbers_fab(message: Message):
        botCl = replyButton(str(message.from_user.id), message.from_user.username)
        company = await workUser.is_company()
        await message.answer("Выберете компанию", reply_markup=botCl.statistics(company))

    @router.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
    async def callbacks_company_stat(callback: types.CallbackQuery, callback_data: NumbersCallbackFactory):
        botCl = replyButton(str(callback.from_user.id), callback.from_user.username)
        company_name = callback_data.value
        try:
            safe_company = company_name.replace("'", "''", len(company_name.split("'")) - 1)
        except Exception:
            safe_company = company_name

        stat = await workUser.company_stat(safe_company)

        stat_week = stat["week"]
        stat_month = stat["month"]
        result_week = botCl.process_statistics(stat_week)
        result_month = botCl.process_statistics(stat_month)

        date_week = botCl.format_date_range(7)
        date_month = botCl.format_date_range(31)

        text = (
            f"📊 {html.bold(f'Статистика компании {company_name}')}\n\n"
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

    @router.callback_query(NumbersCallbackFactory.filter(F.action == "Create_linkStat"))
    async def callbacks_create_linkstat_hint(callback: types.CallbackQuery, callback_data: NumbersCallbackFactory):
        text = (
            "Введите название ссылки\n"
            "Чтобы система поняла что нужно сделать, припишите в начале\n\n"
            "Create_linkStat"
        )
        await bot.send_message(callback.from_user.id, text)

    @router.callback_query(NumbersCallbackFactory.filter(F.action == "Views_linkStat"))
    async def callbacks_views_linkstat(callback: types.CallbackQuery, callback_data: NumbersCallbackFactory):
        try:
            stat = await workUser.get_link(callback.from_user.id)
            week_ago, month_ago = workUser.get_date_ranges()
            link_stats = workUser.calculate_link_stats(stat, week_ago, month_ago)
            msg = workUser.format_stats_message(link_stats)
            await callback.message.answer(msg, parse_mode="Markdown")
        except Exception:
            logger.exception("Views_linkStat handler failed")
            await callback.message.answer("Не удалось получить статистику по ссылкам.")
