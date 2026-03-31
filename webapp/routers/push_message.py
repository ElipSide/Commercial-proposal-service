from pathlib import Path
import json
import os
import urllib
import urllib.request
from urllib.parse import unquote

import dotenv
import requests
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# ==========================================
# ENV
# Вход:
#   - файл .env рядом с этим модулем
# Выход:
#   - загруженные значения конфигурации для Telegram API и ссылок web app
# ==========================================
current_dir = Path(__file__).resolve().parent
env_path = current_dir / ".env"
dotenv.load_dotenv(env_path)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()  # https://t.me/Csort_official_bot
TELEGRAM_API_BASE = os.getenv("TELEGRAM_API_BASE", "https://api.telegram.org").rstrip("/")
URL = f"{TELEGRAM_API_BASE}/bot{TOKEN}/"

WEB_APP_SORTING = os.getenv("WEB_APP_SORTING", "https://csort-news.ru/off_bot/Sorting/home")
WEB_APP_KP = os.getenv("WEB_APP_KP", "https://csort-news.ru/off_bot/offer/home")
WEB_APP_SERVICE = os.getenv("WEB_APP_SERVICE", "https://csort-news.ru/off_bot/Service/home")

PHOTO_KP_MESSAGE_PATH = os.getenv("PHOTO_KP_MESSAGE_PATH", "Front/static/img/PhotoKPmess.png")
PHOTO_SERVICE_MESSAGE_PATH = os.getenv("PHOTO_SERVICE_MESSAGE_PATH", "Front/static/img/PhotoServicemess.png")


# ==========================================
# Вспомогательные функции конфигурации
# Вход:
#   - page/service
# Выход:
#   - ссылка web app или путь к картинке
# ==========================================
def _get_web_app_url_by_page(page: str) -> str:
    if page == "Service" or page == "Сервис":
        return WEB_APP_SERVICE
    return WEB_APP_KP if page == "KP" or page == "КП" else WEB_APP_SORTING


def _get_message_photo_path_by_page(page: str) -> str:
    return PHOTO_SERVICE_MESSAGE_PATH if page == "Service" else PHOTO_KP_MESSAGE_PATH


class resp():
    def __init__(self):
        self.WEB_APP = WEB_APP_SORTING
        self.WEB_APPKP = WEB_APP_KP
        self.WEB_APPService = WEB_APP_SERVICE

    # ==========================================
    # Вход:
    #   - url: готовый URL Telegram Bot API
    # Выход:
    #   - str: текстовый ответ сервера
    # ==========================================
    def get_url(self, url):  # оформленный гет запрос
        response = requests.post(url)
        content = response.content.decode("utf8")
        return content

    # ==========================================
    # Вход:
    #   - url: готовый URL Telegram Bot API
    #   - files: dict с файлами для multipart запроса
    # Выход:
    #   - dict: json-ответ Telegram API
    # ==========================================
    def get_urlFiles(self, url, files):  # оформленный гет запрос
        response = requests.post(url, files=files)
        content = json.loads(response.content.decode("utf8"))
        return content

    # ==========================================
    # Вход:
    #   - text: текст сообщения
    #   - chat_id: id чата
    #   - reply_markup: json клавиатуры
    # Выход:
    #   - str: ответ Telegram API
    # ==========================================
    def send_message_markup(self, text, chat_id, reply_markup):
        result = self.get_url(
            f"{URL}sendMessage?text={urllib.parse.quote_plus(text)}&parse_mode=HTML&chat_id={chat_id}&reply_markup={reply_markup}"
        )
        return result

    # ==========================================
    # Вход:
    #   - text: текст сообщения
    #   - chat_id: id чата
    # Выход:
    #   - str: ответ Telegram API
    # ==========================================
    def send_message(self, text, chat_id):
        result = self.get_url(
            f"{URL}sendMessage?text={urllib.parse.quote_plus(text)}&parse_mode=HTML&chat_id={chat_id}"
        )
        return result

    # ==========================================
    # Вход:
    #   - text: подпись
    #   - chat_id: id чата
    #   - reply_markup: json клавиатуры
    #   - files: dict с фото
    # Выход:
    #   - dict: ответ Telegram API
    # ==========================================
    def send_messagePhoto_markup(self, text, chat_id, reply_markup, files):
        result = self.get_urlFiles(
            f"{URL}sendPhoto?caption={urllib.parse.quote_plus(text)}&parse_mode=HTML&chat_id={chat_id}&reply_markup={reply_markup}",
            files,
        )
        return result

    # ==========================================
    # Вход:
    #   - text: подпись документа
    #   - chat_id: id чата
    #   - reply_markup: json клавиатуры
    #   - files: dict с документом
    # Выход:
    #   - dict: ответ Telegram API
    # ==========================================
    def send_pdf(self, text, chat_id, reply_markup, files):
        result = self.get_urlFiles(
            f"{URL}sendDocument?caption={urllib.parse.quote_plus(text)}&parse_mode=HTML&chat_id={chat_id}&reply_markup={reply_markup}",
            files,
        )
        return result


class TgSendMess():
    def __init__(self):
        self.Req = resp()
        self.WEB_APP = WEB_APP_SORTING
        self.WEB_APPKP = WEB_APP_KP
        self.WEB_APPService = WEB_APP_SERVICE

    # ==========================================
    # Вход:
    #   - data: dict c tg_id, UserName, keyCP, text, chatID, page
    # Выход:
    #   - dict: ответ Telegram API на отправку фото менеджеру
    # ==========================================
    def ManagerGetMessage(self, data):
        tg_id = data['tg_id']
        UserName = data['UserName']
        https = _get_web_app_url_by_page(data['page'])
        fileStr = _get_message_photo_path_by_page(data['page'])

        url = f'{https}?keyCP={data["keyCP"]}&amp;tg_id={str(tg_id)}'
        escaped_url = urllib.parse.quote(url, safe='')
        keyboard = {
            "inline_keyboard": [[{"text": "Связаться с клиентом", "url": f'https://t.me/{UserName}'}]]
        }
        reply_markup = json.dumps(keyboard)
        with open(fileStr, 'rb') as photo_file:
            files = {'photo': photo_file}
            result = self.Req.send_messagePhoto_markup(data['text'], data['chatID'], reply_markup, files)
        return result

    # ==========================================
    # Вход:
    #   - data: dict c UserName, path_file, text, chatID, page
    # Выход:
    #   - dict: ответ Telegram API на отправку PDF менеджеру
    # ==========================================
    def ManagerGetPDF(self, data):
        UserName = data['UserName']
        keyboard = {
            "inline_keyboard": [[{"text": "Связаться с клиентом", "url": f'https://t.me/{UserName}'}]]
        }
        reply_markup = json.dumps(keyboard)
        with open(data['path_file'], 'rb') as document_file:
            files = {'document': document_file}
            result = self.Req.send_pdf(data['text'], data['chatID'], reply_markup, files)
        return result

    # ==========================================
    # Вход:
    #   - data: dict c tg_id, UserName, keyCP, text, chatID, page
    # Выход:
    #   - dict: ответ Telegram API на отправку фото клиенту
    # ==========================================
    def sieveGetMessage(self, data):
        tg_id = data['tg_id']
        https = _get_web_app_url_by_page(data['page'])
        fileStr = _get_message_photo_path_by_page(data['page'])

        url = f'{https}?keyCP={data["keyCP"]}&amp;tg_id={str(tg_id)}'
        escaped_url = urllib.parse.quote(url, safe='')
        keyboard = {
            "inline_keyboard": [[{"text": "Посмотреть КП", "web_app": {'url': escaped_url}}]]
        }
        reply_markup = json.dumps(keyboard)
        with open(fileStr, 'rb') as photo_file:
            files = {'photo': photo_file}
            result = self.Req.send_messagePhoto_markup(data['text'], data['chatID'], reply_markup, files)
        return result

    # ==========================================
    # Вход:
    #   - data: dict c service, path_file, text, keyCP, chatID
    # Выход:
    #   - dict: ответ Telegram API на отправку договора/PDF
    # ==========================================
    def agrement_PDFSend(self, data):
        print(data)
        tg_id = data['chatID']
        https = _get_web_app_url_by_page(data['service'])
        text = f'{data["text"]}'
        url = f'{https}?keyCP={data["keyCP"]}&amp;tg_id={str(tg_id)}'
        escaped_url = urllib.parse.quote(url, safe='')
        keyboard = {
            "inline_keyboard": [[{"text": "Посмотреть КП", "web_app": {'url': escaped_url}}]]
        }
        reply_markup = json.dumps(keyboard)
        with open(data['path_file'], 'rb') as document_file:
            files = {'document': document_file}
            result = self.Req.send_pdf(text, tg_id, reply_markup, files)
        return result

    # ==========================================
    # Вход:
    #   - data: dict c service, path_file, text, chatID
    # Выход:
    #   - None: отправляет PDF пользователю
    # ==========================================
    def PDFSend(self, data):
        tg_id = data['chatID']
        https = _get_web_app_url_by_page(data['service'])
        text = f'Коммерческое предложение №{data["text"]}'
        url = f'{https}?keyCP={data["text"]}&amp;tg_id={str(tg_id)}'
        escaped_url = urllib.parse.quote(url, safe='')
        keyboard = {
            "inline_keyboard": [[{"text": "Посмотреть КП", "web_app": {'url': escaped_url}}]]
        }
        reply_markup = json.dumps(keyboard)
        with open(data['path_file'], 'rb') as document_file:
            files = {'document': document_file}
            self.Req.send_pdf(text, tg_id, reply_markup, files)

    # ==========================================
    # Вход:
    #   - data: dict c text, chatID
    # Выход:
    #   - None: отправляет текстовое сообщение
    # ==========================================
    def Send_Text(self, data):
        self.Req.send_message(data['text'], data['chatID'])

    # ==========================================
    # Вход:
    #   - data: dict c text, chatID, keyCP
    # Выход:
    #   - None: отправляет сообщение с кнопкой web app
    # ==========================================
    def Send_Text_markup(self, data):
        tg_id = data['chatID']
        https = self.WEB_APPKP

        url = f'{https}?keyCP={data["keyCP"]}&amp;tg_id={str(tg_id)}'
        escaped_url = urllib.parse.quote(url, safe='')
        keyboard = {"inline_keyboard": [[{"text": "Посмотреть КП", "web_app": {'url': escaped_url}}]]}
        reply_markup = json.dumps(keyboard)
        self.Req.send_message_markup(data['text'], data['chatID'], reply_markup)

    # ==========================================
    # Вход:
    #   - data: dict c text, chatID
    # Выход:
    #   - None: отправляет сообщение об ошибке
    # ==========================================
    def Send_Error(self, data):
        self.Req.send_message(data['text'], data['chatID'])
