import urllib
import requests
from time import sleep
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import urllib.request
from urllib.parse import unquote
import json
TOKEN = "7210907492:AAFPVOLHDn7u_CT1csL0bj6zX9T-FHbvgCk" #https://t.me/Csort_official_bot

URL = f"https://api.telegram.org/bot{TOKEN}/"

class resp():
    def __init__(self):
        self.WEB_APP = 'https://csort-news.ru/off_bot/Sorting/home'
        self.WEB_APPKP = 'https://csort-news.ru/off_bot/offer/home'
        self.WEB_APPService = 'https://csort-news.ru/off_bot/Service/home'


    def get_url(self, url):  #оформленный гет запрос
        response = requests.post(url)
        content = response.content.decode("utf8")
        return content
    def get_urlFiles(self, url,files):  #оформленный гет запрос
        response =  requests.post(url, files=files)
        content = json.loads(response.content.decode("utf8"))
        return content

    def send_message_markup(self, text, chat_id,reply_markup): 
        result = self.get_url(f"{URL}sendMessage?text={urllib.parse.quote_plus(text)}&parse_mode=HTML&chat_id={chat_id}&reply_markup={reply_markup}")
        return result
    def send_message(self, text, chat_id): 
        result = self.get_url(f"{URL}sendMessage?text={urllib.parse.quote_plus(text)}&parse_mode=HTML&chat_id={chat_id}")
        return result
    def send_messagePhoto_markup(self, text, chat_id,reply_markup, files):
        result = self.get_urlFiles(f"{URL}sendPhoto?caption={urllib.parse.quote_plus(text)}&parse_mode=HTML&chat_id={chat_id}&reply_markup={reply_markup}", files)
        
        return result
    def send_pdf(self, text, chat_id, reply_markup, files): 
        result = self.get_urlFiles(f"{URL}sendDocument?caption={urllib.parse.quote_plus(text)}&parse_mode=HTML&chat_id={chat_id}&reply_markup={reply_markup}", files)
        return result
class TgSendMess():
    def __init__(self):
        self.Req = resp()
        self.WEB_APP = 'https://csort-news.ru/off_bot/Sorting/home'
        self.WEB_APPKP = 'https://csort-news.ru/off_bot/offer/home'
        self.WEB_APPService = 'https://csort-news.ru/off_bot/Service/home'


    def ManagerGetMessage(self, data):
        tg_id = data['tg_id']
        UserName = data['UserName']
        if data['page']=='KP': 
            https= self.WEB_APPKP
            fileStr = 'Front/static/img/PhotoKPmess.png'
        if data['page']=='Service': 
            https= self.WEB_APPService
            fileStr = 'Front/static/img/PhotoServicemess.png'

        url = f'{https}?keyCP={data["keyCP"]}&amp;tg_id={str(tg_id)}'
        escaped_url = urllib.parse.quote(url, safe='')
        keyboard = {"inline_keyboard": [
            # [{"text": "Посмотреть КП", "web_app": {'url':escaped_url}}],
                [{"text": "Связаться с клиентом", "url": f'https://t.me/{UserName}'}]
                ]}
        reply_markup =json.dumps(keyboard)
        files = {'photo': open(fileStr, 'rb')}
        result = self.Req.send_messagePhoto_markup(data['text'], data['chatID'],reply_markup, files)
        return result
    
    def ManagerGetPDF(self, data):
        tg_id = 'id_tg'
        UserName = data['UserName']
        if data['page']=='KP': 
            https= self.WEB_APPKP
        if data['page']=='Service': 
            https= self.WEB_APPService

  
        keyboard = {"inline_keyboard": [
                [{"text": "Связаться с клиентом", "url": f'https://t.me/{UserName}'}]
                ]}
        reply_markup =json.dumps(keyboard)
        files = {'document': open(data['path_file'], 'rb')}
        result = self.Req.send_pdf(data['text'], data['chatID'],reply_markup, files)
        return result
    
    def sieveGetMessage(self, data):
        tg_id = data['tg_id']
        UserName = data['UserName']
        if data['page']=='KP': 
            https= self.WEB_APPKP
            fileStr = 'Front/static/img/PhotoKPmess.png'
        if data['page']=='Service': 
            https= self.WEB_APPService
            fileStr = 'Front/static/img/PhotoServicemess.png'


        url = f'{https}?keyCP={data["keyCP"]}&amp;tg_id={str(tg_id)}'
        escaped_url = urllib.parse.quote(url, safe='')
        keyboard = {"inline_keyboard": [[{"text": "Посмотреть КП", "web_app": {'url':escaped_url}}],
                # [{"text": "Связаться с менеджером", "url": f'https://t.me/{UserName}'}]
                ]}
        reply_markup =json.dumps(keyboard)
        files = {'photo': open(fileStr, 'rb')}
        result = self.Req.send_messagePhoto_markup(data['text'], data['chatID'],reply_markup, files)
        return result

        
    def agrement_PDFSend(self, data):
        print(data)
        tg_id = data['chatID']
        if data['service']=='КП': 
            https= self.WEB_APPKP
        if data['service']=='Сервис': 
            https= self.WEB_APPService
        files = {'document': open(data['path_file'], 'rb')}
        text = f'{data["text"]}'
        url = f'{https}?keyCP={data["keyCP"]}&amp;tg_id={str(tg_id)}'
        escaped_url = urllib.parse.quote(url, safe='')
        keyboard = {"inline_keyboard": [[{"text": "Посмотреть КП", "web_app": {'url':escaped_url}}],
                # [{"text": "Связаться с менеджером", "url": f'https://t.me/{UserName}'}]
                ]}
        reply_markup =json.dumps(keyboard)
        result = self.Req.send_pdf(text, tg_id, reply_markup, files)
        return result 
    
    def PDFSend(self, data):
        tg_id = data['chatID']
        if data['service']=='КП': 
            https= self.WEB_APPKP
        if data['service']=='Сервис': 
            https= self.WEB_APPService
        files = {'document': open(data['path_file'], 'rb')}
        text = f'Коммерческое предложение №{data["text"]}'
        url = f'{https}?keyCP={data["text"]}&amp;tg_id={str(tg_id)}'
        escaped_url = urllib.parse.quote(url, safe='')
        keyboard = {"inline_keyboard": [[{"text": "Посмотреть КП", "web_app": {'url':escaped_url}}],
                # [{"text": "Связаться с менеджером", "url": f'https://t.me/{UserName}'}]
                ]}

        reply_markup =json.dumps(keyboard)

        self.Req.send_pdf(text, tg_id, reply_markup, files)
    def Send_Text(self, data):
        self.Req.send_message(data['text'], data['chatID'])

    def Send_Text_markup(self, data):
        tg_id = data['chatID']
        https= self.WEB_APPKP

        url = f'{https}?keyCP={data["keyCP"]}&amp;tg_id={str(tg_id)}'
        escaped_url = urllib.parse.quote(url, safe='')
        keyboard = {"inline_keyboard": [[{"text": "Посмотреть КП", "web_app": {'url':escaped_url}}],
                ]}
        reply_markup =json.dumps(keyboard)
        self.Req.send_message_markup(data['text'], data['chatID'], reply_markup)

        
    def Send_Error(self, data):
        self.Req.send_message(data['text'], data['chatID'])

