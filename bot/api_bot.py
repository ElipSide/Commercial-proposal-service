"""
Работа с backend API по пользователям и статистике ссылок.

Вход:
- telegram user/message или идентификаторы пользователя.

Выход:
- JSON-ответы backend API в виде dict/list,
  пригодные для хендлеров Telegram-бота.
"""

import requests
from aiogram.types import Message
from datetime import datetime, timedelta
from translate import Translator
from typing import Any, Dict, List

from env_settings import get_settings


SETTINGS = get_settings()
API_URL = SETTINGS.api_url

class workingUsers():
    """Тонкий API-клиент для пользовательских и статистических операций."""

    def __init__(self):
        print("")

    async def is_user_exists(self, user_id: str) -> bool:
        """Вход: user_id. Выход: признак/объект существования пользователя в backend."""
        # try:
        response = requests.get(f"{API_URL}/users/{user_id}")
        print(response.json())
        return response.json()
        # except (httpx.HTTPStatusError, KeyError):
        #     return False
    async def is_users(self) -> bool:
        # try:
        response = requests.get(f"{API_URL}/users_id")
        return response.json()
        # except (httpx.HTTPStatusError, KeyError):
            #     return False
    async def is_user_write(self, message: Message) -> bool:
        """Вход: Telegram Message с contact. Выход: результат регистрации пользователя."""
        data= {
            'first_name': message.contact.first_name,
            'telegram_id':str(message.contact.user_id),
            'phone_number':message.contact.phone_number,
            'username':message.from_user.username,
            'id_max':''
        }
        headers = {'Content-Type': 'application/json'}
        response =  requests.post(f"{API_URL}/register", json= data, headers=headers)
        print(response)
        return response.json()
    
    async def is_id_manag(self, key: str) -> bool:
        headers = {'Content-Type': 'application/json'}
        response =  requests.post(f"{API_URL}/getID_manag/{key}", headers=headers)
        return response.json()
    
    async def is_company(self) -> bool:
        response = requests.get(f"{API_URL}/company_id")
        return response.json()
    
    async def company_stat(self, company) -> bool:
        print(f"{API_URL}/company_stat/{company}")
        response = requests.get(f"{API_URL}/company_stat/{company}")
        return response.json()
    
    async def get_link(self, id_tg) -> bool:
        response = requests.get(f"{API_URL}/get_AllLink/{str(id_tg)}")
        return response.json()
    
    async def create_link(self, data) -> bool:
        print(data)
        headers = {'Content-Type': 'application/json'}

        response = requests.post(f"{API_URL}/create_link", json=data, headers=headers)
        return response.json()
    

    def translate_to_english(self, text):

        translator = Translator(from_lang="ru", to_lang="en")
        translation = translator.translate(text)
       
        return translation
    
    
    def get_date_ranges(self) -> tuple[datetime.date, datetime.date]:
        """Возвращает даты начала недели и месяца."""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        return week_ago, month_ago

    def calculate_link_stats(
        self,
        stat: List[List[Any]],
        week_ago: datetime.date,
        month_ago: datetime.date
    ) -> Dict[str, Dict[str, Any]]:
        """
        Считает статистику переходов по каждой ссылке:
        - total (общее число переходов)
        - weekly (за неделю)
        - monthly (за месяц)
        """
        link_stats = {}
        
        for item in stat:
            link_name = item[2].strip()
            link_url = item[3]
            transitions = item[4]
            date_str = item[5]
            
            try:
                link_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                continue  # Пропускаем некорректные даты
            
            if link_url not in link_stats:
                link_stats[link_url] = {
                    "name": link_name,
                    "total": transitions,
                    "weekly": 0,
                    "monthly": 0
                }
            
            if link_date >= week_ago:
                link_stats[link_url]["weekly"] += transitions
            if link_date >= month_ago:
                link_stats[link_url]["monthly"] += transitions
        
        return link_stats

    def format_stats_message(self, link_stats: Dict[str, Dict[str, Any]]) -> str:
        if not link_stats:
            return "📭 Статистика переходов пуста"
        
        message = "📊 *Статистика переходов*\n\n"
        
        for url, data in link_stats.items():
            message += (
                f"🔗 *{data['name']}*\n"
                f"├ Ссылка: `{url}`\n"
                f"├ Всего: *{data['total']}*\n"
                f"├ Неделя: _{data['weekly']}_\n"
                f"└ Месяц: _{data['monthly']}_\n\n"
            )
        
        return message