"""
Клавиатуры и форматирование отображения статистики.

Вход:
- telegram id, username и данные статистики.

Выход:
- aiogram keyboard markup и готовые текстовые блоки для отправки пользователю.
"""

import re
from datetime import datetime, timedelta

from aiogram import html
from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from env_settings import get_settings


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: str


class replyButton:
    """Строит reply/inline-клавиатуры для меню, статистики и WebApp."""

    def __init__(self, tg_id, username):
        settings = get_settings()
        self.WEB_APP = settings.web_app_sorting_url
        self.WEB_APPKP = settings.web_app_offer_url
        self.WEB_APPService = settings.web_app_service_url
        self.WEB_APPphotosep = settings.web_app_separator_url
        self.commandID = [str(x) for x in settings.button_command_ids]
        self.update_bot_button_owner_id = str(settings.update_bot_button_owner_id)
        self.username = username
        self.tg_id = tg_id

    def auth(self):
        builder = ReplyKeyboardBuilder()
        builder.add(KeyboardButton(text="Поделиться контактом", request_contact=True))
        return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

    def delete(self):
        builder = ReplyKeyboardBuilder()
        builder.add(KeyboardButton(text="/start"))
        return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

    def visits(self, access_user):
        builder = ReplyKeyboardBuilder()

        builder.add(
            KeyboardButton(
                text="КП",
                web_app=WebAppInfo(
                    url=f"{self.WEB_APPKP}?&tg_id={str(self.tg_id)}&username={str(self.username)}"
                ),
            )
        )

        if access_user == "manager":
            builder.add(
                KeyboardButton(
                    text="Сервис",
                    web_app=WebAppInfo(
                        url=f"{self.WEB_APPService}?&tg_id={str(self.tg_id)}&username={str(self.username)}"
                    ),
                )
            )

        if self.tg_id == self.update_bot_button_owner_id:
            builder.add(KeyboardButton(text="Обновить бота"))
        if self.tg_id in self.commandID:
            builder.add(KeyboardButton(text="Статистика"))
        if self.tg_id in self.commandID:
            builder.add(KeyboardButton(text="Статистика переходов"))

        builder.adjust(3)
        return builder.as_markup(resize_keyboard=True)

    def statistics(self, company):
        builder = InlineKeyboardBuilder()
        for el in company:
            name = re.sub(r'["]', "", el[2])
            builder.button(
                text=name,
                callback_data=NumbersCallbackFactory(action="change", value=name),
            )
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    def choice_stat(self):
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Создать ссылку",
            callback_data=NumbersCallbackFactory(action="Create_linkStat", value="Создать ссылку"),
        )
        builder.button(
            text="Посмотреть статистику ссылок",
            callback_data=NumbersCallbackFactory(action="Views_linkStat", value="Посмотреть ссылки"),
        )
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    def Create_linkStat(self):
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="Вставить текст", switch_inline_query="Create_linkStat")
        keyboard.adjust(1)
        return keyboard.as_markup()

    def format_numbers(self, number):
        new_str = str(number)[::-1]
        return " ".join(new_str[i : i + 3] for i in range(0, len(new_str), 3))[::-1]

    def format_stat_manag(self, stat_manag):
        if len(stat_manag.keys()) == 0:
            return html.bold("Ничего не сделали")
        return "\n".join(f"{key}: {value['count']} шт" for key, value in stat_manag.items())

    def process_statistics(self, stat_data):
        result = {
            'КП':{
                'Счет':{'count': 0, 'sum': 0, 'stat_manag': {}},
                'Договор': {'count': 0, 'sum': 0, 'stat_manag': {}},
                'КП': {'count': 0, 'sum': 0, 'stat_manag': {}},
                'КП_клиент': {'count': 0, 'sum': 0},

            },
            'Сервис':{
                'Счет':{'count': 0, 'sum': 0, 'stat_manag': {}},
                'Договор': {'count': 0, 'sum': 0, 'stat_manag': {}},
            }
        }
        for el in stat_data:
            
            if str(el[5]) in self.commandID:
                continue
            type_key = el[2]
            category = el[1]
            amount = int(el[6])
            manager = el[9]
            
            result[category][type_key]['count'] += 1
            result[category][type_key]['sum'] += amount
            
            if manager:
                if type_key=='КП_клиент':continue
                if manager not in result[category][type_key]['stat_manag']:
                    result[category][type_key]['stat_manag'][manager] = {'count': 0, 'sum': 0}
                result[category][type_key]['stat_manag'][manager]['count'] += 1
                result[category][type_key]['stat_manag'][manager]['sum'] += amount
                

        return result

    def format_date_range(self, days):
        start_date = (datetime.now() - timedelta(days=days)).date().strftime("%d.%m.%Y")
        end_date = datetime.now().date().strftime("%d.%m.%Y")
        return f"{start_date}-{end_date}"
