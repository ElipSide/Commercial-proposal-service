import asyncio
import datetime
import json
import pymorphy3
import aiohttp
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from num2words import num2words
from weasyprint import HTML
from babel.dates import format_date
from PIL import Image
from io import BytesIO

from routers.push_message import TgSendMess
import routers.API.page_API as page_API
import routers.page_CalcKP as page_CalcKP

from .modules.dop_info_utils import (
    DopInfo_photo, DopInfo_machine, DopInfo_compressor, DopInfo_Elevator
)
morph = pymorphy3.MorphAnalyzer()

# server = '194.63.141.80'
# username = 'user2824307'
# password = 'Hj2dOu2agcj7'

# from routers.ftp_client import FTPClient
Date_create = datetime.datetime.today().strftime("%d.%m.%Y")
day = Date_create.split(".")[0]
month = Date_create.split(".")[1]
year = Date_create.split(".")[2]
date_object = datetime.datetime.strptime(Date_create, "%d.%m.%Y")
month_name = format_date(date_object, "MMMM", locale='ru')
TgSend = TgSendMess()

class ImageProcessor:
    def __init__(self, url: str):
        self.url = url

    async def _load_image(self):
        """загрузка изоб"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    content = await response.read()
            return Image.open(BytesIO(content))
        except Exception as e:
            print(f"Ошибка при получении изображения: {e}")
            return None

    async def get_image_size(self):
        """получение размера изображения"""
        img = await self._load_image()
        return img.size if img else None

    async def calculate_margin(self): 
        """рассчитываем маржу"""
        img = await self._load_image()
        return 100 + int(img.size[1]*0.05) if img else 100

class DataFunc:
    FIELDS = (
        'bank_info','bic','checking_account','inn','kpp','corporate_account','organization_shortname','index','address',
        'phone_number','position_user','first_name','surname','second_name','ogrn','email'
    )
    
    def __init__(self, data):
        self.seller = self._process_data(data.get('seller'))
        self.buyer = self._process_data(data.get('buyer'))

    def _process_data(self, data: dict) -> dict:
        """получение данных для покупателя и продавца"""
        return {field: data.get(field, '') for field in self.FIELDS}

class DocumentTemplate:
    def __init__(self, file_name: str):
        self.file_name = file_name
    
    async def read_html_template(self):
        with open(f'Front/static/document/agrement/HTML/{self.file_name}.html', 'r', encoding='utf-8') as file:
            return file.read()
        
class ContractTableBuilder:
    def __init__(self, html_content: str, items: list[dict]):
        self.items = items
        self.soup = BeautifulSoup(html_content, 'html.parser')

    # ========== HELPERS ==========
    def _find_table_after(self, text: str, offset: int = 1):
        tables = self.soup.find_all('table')
        for i, table in enumerate(tables):
            if text.lower() in table.get_text().lower():
                return tables[i + offset] if i + offset < len(tables) else None
        return None
    
    def _new_cell(self, text="", align="center", bold=False, colspan=None, rowspan=None):
        style = f"text-align: {align};"
        if bold:
            style += " font-weight: 600;"
        cell = self.soup.new_tag("td", style=style)
        if colspan:
            cell["colspan"] = str(colspan)
        if rowspan:
            cell["rowspan"] = str(rowspan)
        cell.string = str(text)
        return cell

    def _new_row(self):
        return self.soup.new_tag("tr", style="break-inside: avoid;")
    
    def GenerateAddTable(self, soup, item, row, add_table, row_counter):
        for key in ['number', 'name_print', 'count', 'price', 'sum', 'delivery_text']:
            cell = soup.new_tag('td', style='text-align: center')
            if key == 'name_print':
                cell = soup.new_tag('td', style='text-align: left')
            if key == 'number':
                cell.string = str(row_counter)
            else:
                cell.string = str(item[key])
            row.append(cell)
        
        add_table.append(row)
        
        return add_table

    async def replace_in_html(self, replacements):
        for key, value in replacements.items():
            for text_node in self.soup.find_all(string=lambda text: key in str(text)):
                new_content = re.sub(
                    rf"\b{re.escape(str(key))}\b",
                    str(value),
                    text_node
                )
                new_soup = BeautifulSoup(new_content, 'html.parser')
                text_node.replace_with(new_soup)

        return str(self.soup)

    # ========== TABLE ==========
    async def add_str_table_app_spec(self):
        table = self._find_table_after("спецификация", offset=2)
        if not table:
            return str(self.soup) 
        
        total_count = 0
        total_sum = 0
        counter = 1

        has_programm = any('программа' in item.get('name_print', '').lower() for item in self.items)

        for item in self.items:
            if item.get("ads") == "ads":
                continue

            name_print = item['name_print'].strip().lower()

            if has_programm and 'фотосепаратор' in name_print:
                continue

            total_count += int(item['count'])
            total_sum += int(item['sum'])
            row = self._new_row()
            table = self.GenerateAddTable(self.soup, item, row, table, counter)
            counter += 1
        
        total_row = self._new_row()
        total_row.append(self._new_cell("Итого по оборудованию", bold=True, colspan=2))
        total_row.append(self._new_cell(total_count, bold=True))
        total_row.append(self._new_cell())
        total_row.append(self._new_cell(total_sum, bold=True))
        total_row.append(self._new_cell())

        table.append(total_row)

        return str(self.soup)     

    async def add_str_table_app_823(self):
        table = self._find_table_after("спецификация")
        if not table:
            return str(self.soup) 
        
        total = 0
        counter = 1
        
        for item in self.items:
            if 'Фотосепаратор' not in item['name'].strip():
                continue
            
            row = self._new_row()
            fields = ["number","name","code_okpd","count","start_price","price_withDiscount","discont","discount_price",
                      "SumPrice_withDiscount","delivery_text"]

            total += int(item['count'])*int(item['SumPrice_withDiscount'])

            for value in fields:
                
                cell = self.soup.new_tag('td', style='text-align: center')
                cell.string = str(item[value])
                if value == 'number':
                    cell.string = str(counter)
                    counter += 1

                row.append(cell)

            table.append(row) 

        total_row = self._new_row()
        total_row.append(self._new_cell("Итого по оборудованию", bold=True, colspan=2))
        total_row.append(self._new_cell())
        total_row.append(self._new_cell())
        total_row.append(self._new_cell())
        total_row.append(self._new_cell())
        total_row.append(self._new_cell())
        total_row.append(self._new_cell())
        total_row.append(self._new_cell(total, bold=True))
        total_row.append(self._new_cell())

        table.append(total_row)
        return str(self.soup)

    async def add_str_table_app_tableAds(self, total_summ_services):  
        table = self._find_table_after("спецификация", offset=3)
        if not table:
            return str(self.soup)     

        counter = 0
        for item in self.items:
            if item.get('ads') != "ads":
                continue
            
            if 'Фотосепаратор' in item['name_print'].strip():
                photosep = item['name_print'].strip()
            
            row = self._new_row()
            name_print = item['name_print'].strip().lower()
            
            if 'программа' in name_print:
                continue

            counter += 1
            fields = ["number","name_print","count","price","sum","note"]

            for value in fields:
                cell = self.soup.new_tag('td', style='text-align: center')
                if value == 'name_print':
                    cell = self.soup.new_tag('td', style='text-align: left')
                if value == 'number':
                    cell.string = str(counter)
                elif value == 'note':
                    note_text = item['note'].get(item['name_print'].strip(), '')
                    if 'Для оборудования' in note_text:
                        note_text = note_text +' '+ photosep
                    cell.string = str(note_text)
                else:
                    cell.string = str(item[value])
                row.append(cell)
            table.append(row)

        total_row = self._new_row()
        total_row.append(self._new_cell("Итого по услугам", bold=True, colspan=2))
        total_row.append(self._new_cell(counter, bold=True))
        total_row.append(self._new_cell())
        total_row.append(self._new_cell(total_summ_services, bold=True))
        total_row.append(self._new_cell())

        table.append(total_row)
        return str(self.soup)

    async def add_str_table_app_2(self):
        table = self._find_table_after("Приложение № 2")
        if not table:
            return str(self.soup) 

        def get_equipment_type(item):
            name = item.get('name', '').strip()
            name_print = item.get('name_print', '').strip()

            if 'Фотосепаратор' in name:
                return 'photoseparator'
            if 'Компрессор винтовой' in name_print:
                return 'compressor'
            if 'CS' in name:
                return 'elevator'
            return None

        def get_photoseparator_subtype(name):
            if 'СмартСорт' in name:
                return 'smart'
            if 'MiniSort' in name:
                return 'minisort'
            return None
        
        for item in self.items:
            if item.get('ads') == 'ads':
                continue

            equipment_type = get_equipment_type(item)
            name = item.get('name', '').strip()

            row = self.soup.new_tag('tr', style='break-inside: avoid;')

            for key in ['number', 'name_print', 'guarantee', 'date_open', 'date_close', 'note']:
                cell = self.soup.new_tag('td', style='text-align: center')

                # --- GUARANTEE ---
                if key == 'guarantee' and equipment_type:
                    if equipment_type == 'photoseparator':
                        subtype = get_photoseparator_subtype(name)
                        guarantee_data = item.get('guarantee', {}).get('photoseparator', {})
                        value = guarantee_data.get(subtype, '-') if subtype else '-'
                        cell.string = str(value)
                    else:
                        value = item.get('guarantee', {}).get(equipment_type, '-')
                        cell.string = str(value)

                # --- DATE OPEN ---
                elif key == 'date_open' and equipment_type:
                    value = item.get('date_open', {}).get(equipment_type, '-')
                    cell.string = str(value)

                # --- DATE CLOSE ---
                elif key == 'date_close' and equipment_type:
                    value = item.get('date_close', {}).get(equipment_type, '-')
                    cell.string = str(value)

                # --- NOTE ---
                elif key == 'note' and equipment_type:
                    note_data = item.get('note', {}).get('Гарантия', {})
                    value = note_data.get(equipment_type, 'Гарантия не предоставляется')
                    cell.string = str(value)

                else:
                    cell.string = str(item.get(key, '-'))

                row.append(cell)
            table.append(row)
        return str(self.soup)        

    async def add_str_table_app_3(self):
        table = self._find_table_after("Приложение № 3")
        if not table:
            return str(self.soup) 
        
        for item in self.items:
            if item.get("ads") == "ads":
                continue
            
            if 'Фотосепаратор' not in item['name']:
                continue

            row = self._new_row()
            for value in ['date', 'name','product', 'sign']:
                cell = self.soup.new_tag('td', style='text-align: center')
                cell.string = str(item[value])
                row.append(cell)
            table.append(row)   

        # if total_count > 9:
        #     page_break = soup.new_tag('div', style='page-break-before: always;')
        #     add_table.insert_after(page_break)

        #     new_table = soup.new_tag('table', style='border-collapse: collapse; width: 100%;')
        #     headers = add_table.find_all('tr')[0].find_all('td')
        #     header_title = soup.new_tag('p', style="width: 100%; padding: 0; text-align: center; font-weight: 600; text-align: center;")
        #     header_title.append("Приложение № 5")
        #     header_title.append(soup.new_tag("br"))  # Добавляем <br>
        #     header_title.append(f"к Договору поставки оборудования № {nubmer_dogov} от « {day} » {month_name} {year} г.")
        #     header_title.append(soup.new_tag("br"))  # Добавляем <br>
        #     header_title.append("(продолжение)")
        #     new_table.append(header_title)
        #     header_row = soup.new_tag('tr')
        #     for header in headers:
        #         new_header = soup.new_tag('td', style=header.get('style', ''))
        #         new_header.string = header.string
        #         header_row.append(new_header)
        #     new_table.append(header_row)

        #     last_row = add_table.find_all('tr')[-1:]
        #     for row in last_row:
        #         row.extract()
        #         new_table.append(row)

        #     page_break.insert_after(new_table)

        return str(self.soup)

class PluralForm:
    """Склонение числительных"""

    def __init__():
        pass
    
    @staticmethod
    async def _plural_form(number: str, forms: tuple[str, str, str]) -> str:
        number = str(number)

        last_two = int(number[-2:]) if len(number) > 1 else int(number)
        last_one = int(number[-1])

        if 11 <= last_two <= 14:
            return forms[0]
        if last_one == 1:
            return forms[1]
        if 2 <= last_one <= 4:
            return forms[2]
        return forms[0]
    
    @classmethod
    async def rub(cls, number: str) -> str:
        return await cls._plural_form(number, ("рублей","рубль","рубля"))
    
    @classmethod
    async def kop(cls, number: str) -> str:
        return await cls._plural_form(number, ("копеек","копейка","копейки"))
    
    @classmethod
    async def sum_propis(cls, total_sum: str) -> str:

        sum_user = total_sum.replace(" ", "")
        parts = sum_user.split(".")
        sum_user_rub = parts[0]
        sum_user_kop = parts[1]

        sum_rub_str = await cls.rub(sum_user_rub)
        sum_kop_str = await cls.kop(sum_user_kop)

        sum_propis_rus = num2words(sum_user_rub, lang='ru')
        sum_rub = (sum_propis_rus + ' ' + sum_rub_str).capitalize()
        sum_kop = (str(sum_user_kop) + ' ' + sum_kop_str).capitalize()
        sum_propis = sum_rub + ' ' + sum_kop
        return sum_propis

class SpecElevatorBuilder:
    
    NAME_MAPPING = {
        'DefStretchSection':'Секция натяжная', 
        'DefDriveSection':'Секция приводная', 
        'DefCornerSection':'Секция угловая',
        'DefElevatorShoe':'Башмак элеватора',
        'DefElevatorHead':'Голова элеватора',
        'section_element': 'Секция удлинения',
        'bucketElement':'Лента с ковшами',
        'CSECountMotorReductorElement':'Привод элеватора',
        'controlBoxElement': 'Пульт управления',
        'sensorPodporBottomElement':'Датчик емкостной',
        'sensorSpeedElement':'Датчик индуктивный(датчики скорости)',
        'sensorBeltElement':'Датчик индуктивный(датчик схода ленты)',
        'chainElement':'Цепь', 
        'CSCCBucketElement':'Скребки',
        'CSZEBucketElement':'Ковши',
        'OneChainElement':'Лента',
        'motorReductorElement':'Мотор-Редуктор',
        'sensorPodporElement':'Датчик подпора',
        'CSCCsensorSpeedElement': 'Датчик РКС',
        'passportElement':'Паспорт',
        'manualElement':'Руководство по эксплуатации',
        'toolsElement':'Набор метизов для сборки',
        # 'DefSuctionConnect':'Загрузочный патрубок, шт.', ###
        # 'DefWindowB':'Ревизионное окно в нижней секции, шт.', 
        # 'CSCCDefSuctionConnect':'Аспирационный патрубок, шт.', ###
        # 'DefWindow':'Смотровое окно в нижней секции, шт.', ###
    }
    
    TYPE_FIELDS = {
        'общее':[
            'manualElement','toolsElement','controlBoxElement',
            'sensorPodporBottomElement','sensorSpeedElement','sensorBeltElement',
            'sensorPodporElement', 'passportElement', 'section_element'
        ],
        'Зерновой элеватор': [ # CSE
            'DefSuctionConnect', 'DefWindowB', 'DefElevatorHead', 
            'DefElevatorShoe','bucketElement','CSECountMotorReductorElement',
        ],
        'Конвейер цепной': [ # CSZE
            'DefStretchSection', 'DefDriveSection', 'DefCornerSection',
            'chainElement', 'CSZEBucketElement', 'motorReductorElement',
        ],
        'Конвейер скребковый': [ # CSCC
            'CSCCDefSuctionConnect','DefWindow','DefStretchSection',
            'DefDriveSection','chainElement','CSCCBucketElement',
            'motorReductorElement',
            
        ],
        'Конвейер ленточный': [ # CSBC
            'DefStretchSection','DefDriveSection','OneChainElement',
            'motorReductorElement',
        ]
    }

    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def load(self, elevator_name: str) -> dict:
        BASE_PATH = "./Front/static/document/deal_elevator/"
        path = f'{BASE_PATH}{elevator_name}.json'
        with open(path, encoding='utf-8') as f:
            return json.load(f)
        
    def _new_cell(self, text="", align="center", rowspan=None):
        style = f"text-align: {align};"
        cell = self.soup.new_tag("td", style=style)
        if rowspan:
            cell["rowspan"] = str(rowspan)
        cell.string = str(text)
        return cell

    async def add_str_table_app_spec_elevator(self, additional_info, count_table, name_print, equipment_type, id_row_elevator, lang):

        count_user_elevator = list(id_row_elevator.values())
        id_json_document_elevator = list(additional_info.get('id_json', {}).values())

        spec_div = self.soup.new_tag('div', id=f"spec_elevator_{count_table}", style='page-break-inside: avoid;')

        for elevator_name, modelCount in zip(id_json_document_elevator,count_user_elevator):
            dataElevator = self.load(elevator_name)
            nameModel = dataElevator['modelName']

            elevator_svg = None
            if nameModel.startswith(('CSZE','CZE')):
                elevator_svg = dataElevator['temporal_data']['svg']

            match = re.search(r'(CSZE|CZE|CSCC|CSBC)-(\d+)', name_print)
            modelNamePrint = match.group(1) + match.group(2) 

            if nameModel in modelNamePrint:
                dop_info_elevator = await DopInfo_Elevator([elevator_name],[modelCount], lang)
                
                for item in dop_info_elevator:
                    all_fields = self.TYPE_FIELDS.get(equipment_type, []) + self.TYPE_FIELDS['общее']
                    name_mapping_keys = list(self.NAME_MAPPING.keys())
                    all_fields = [key for key in name_mapping_keys if key in all_fields]
                    
                    # Словарь для группировки компонентов
                    components = {}
                    for field in all_fields:
                        if field in item and item[field]:
                            component_name = self.NAME_MAPPING.get(field, field)
                            components[component_name] = int(item[field])
                            
                    ordered_component_names = [
                        self.NAME_MAPPING[field]
                        for field in all_fields
                        if field in self.NAME_MAPPING and self.NAME_MAPPING[field] in components
                    ]
                    
                    row_datas = []
                    for i, name in enumerate(ordered_component_names, start=1):
                        row_datas.append({
                            'num': i,
                            'name': name,
                            'count': components[name]
                        })
                        
                    # Добавляем заголовок
                    title = self.soup.new_tag('p', style='padding: 0; margin: 0; margin-top: 10px;')
                    title.string = f'Комплектующие для {name_print}'
                    spec_div.append(title)
                    
                    # Создаем таблицу
                    table = self.soup.new_tag('table', style='border-collapse: collapse; width: 100%; color: black; page-break-inside: avoid;')
                    
                    # Добавляем заголовки столбцов
                    header_row = self.soup.new_tag('tr')
                    columns = [
                        ('№ п/п', 'width: 5%; padding: 5px; text-align: center; border: 1px solid black;'),
                        ('Наименование', 'padding: 5px; text-align: center; border: 1px solid black;'),
                        ('Кол-во', 'padding: 5px; text-align: center; border: 1px solid black;'),
                        ('Примечание', 'padding: 5px; text-align: center; border: 1px solid black;')
                    ]
                    
                    for text, style in columns:
                        th = self.soup.new_tag('td', style=style)
                        th.string = text
                        header_row.append(th)
                    
                    table.append(header_row)
                    spec_div.append(table)

                    for i, row_data in enumerate(row_datas):
                        row = self.soup.new_tag('tr', style='break-inside: avoid;')

                        # № п/п
                        num_cell = self._new_cell(text=row_data['num'])
                        row.append(num_cell)

                        # Наименование
                        name_cell = self._new_cell(align="left", text=row_data['name'])
                        row.append(name_cell)

                        # Количество
                        count_cell = self._new_cell(text=row_data['count'])
                        row.append(count_cell)

                        # Примечание
                        if i == 0:
                            note_cell = self._new_cell(rowspan=str(len(row_datas)),text="Входит в стоимость конвейера")
                            row.append(note_cell)
                            
                        table.append(row)

                    title_dxf = self.soup.new_tag('p', style='padding: 0; margin: 0; margin-top: 10px;')
                    title_dxf.string = f'Габаритные размеры {name_print}'
                    spec_div.append(title_dxf) # Габаритные размеры Конвейер цепной CSZE-5-7-В + img
                    
                    img_div = self.soup.new_tag('div', style='text-align: center;')
                    img_tag = self.soup.new_tag('img', style='width: 50%;', src=f'{elevator_svg}', alt='')
                    img_div.append(img_tag)
                    spec_div.append(img_div)

        return spec_div

class PaymentGenerator:
    def __init__(self):
        pass
    
    def GeneratePaymentMetod(data, total_summ_spec):
        if data['terms_payment'] == '100% предоплата':
            paymentMetod=  f'100% платы, что состовляет  {total_summ_spec} руб., вносится в течение 5 рабочих дней с момента подписания договора.'
        if data['terms_payment'] == '50%/50%':
            total_summ_str_polov_50 =  str("{:.2f}".format(float(total_summ_spec)/2) )
            paymentMetod=  f'''
                <p style="padding: 0 0 0 25px; margin: 0;">50% предоплата ({total_summ_str_polov_50} руб., включая НДС) — вносится в течение 5 рабочих дней с момента подписания Договора.</p><br>
                <p style="padding: 0 0 0 25px; margin: 0;">50% окончательный платеж ({total_summ_str_polov_50} руб., включая НДС) — вносится в течение 5 рабочих дней с момента получения уведомления о готовности оборудования к отгрузке/выборке со склада.</p>
            '''
        if data['terms_payment'] == '70%/30%':
            total_summ_str_polov_70 =  str("{:.2f}".format(float(total_summ_spec)*0,7) )
            total_summ_str_polov_30 =  str("{:.2f}".format(float(total_summ_spec)*0,3) )
            paymentMetod=  f'''
                70% предоплата ({total_summ_str_polov_70} руб., включая НДС) — вносится в течение 5 рабочих дней с момента подписания Договора.<br>
                30% окончательный платеж ({total_summ_str_polov_30} руб., включая НДС) — вносится в течение 5 рабочих дней с момента получения уведомления о готовности оборудования к отгрузке/выборке со склада.<br>
            '''
        if data['terms_payment'] == '30%/70%':
            total_summ_str_polov_70 =  str("{:.2f}".format(float(total_summ_spec)*0,7) )
            total_summ_str_polov_30 =  str("{:.2f}".format(float(total_summ_spec)*0,3) )
            paymentMetod=  f'''
                30% предоплата ({total_summ_str_polov_30} руб., включая НДС) — вносится в течение 5 рабочих дней с момента подписания Договора.<br>
                70% окончательный платеж ({total_summ_str_polov_70} руб., включая НДС) — вносится в течение 5 рабочих дней с момента получения уведомления о готовности оборудования к отгрузке/выборке со склада.<br>
            '''

        return paymentMetod

class DocumentCalculator:

    def calculate_totals(data):
        totals = {
            "total_sum": 0,
            "total_count": 0,
            "service_sum": 0,
            "service_count": 0,
            "machines_sum": 0,
            "machines_count": 0,
        }
                                       
        for item in data.get("List", []):
            sum = item["sum"]
            count = int(item["count"])
            is_service = item.get("ads") == "ads"
            table_str = str(item['number'])

            totals["total_sum"] += sum
            totals["total_count"] += count

            if is_service:
                totals["service_sum"] += sum
                totals["service_count"] += count
            else:
                totals["machines_sum"] += sum
                totals["machines_count"] += count
        
        return totals, table_str

class FileNameGenerator:

    def generate(data, has_ads, has_1432, has_823, has_transport):
        base = f'Front/static/document/agrement/PDF/{data["NameFile"]} N{data["number"]}'
        
        pdfdirs = os.path.join("Front", "static", "document", "agrement", "PDF")
        os.makedirs(pdfdirs, exist_ok=True)

        if has_823:
            suffix_parts = 'программа823'
        elif has_1432:
            suffix_parts = 'программа1432'
        elif has_ads:
            suffix_parts = 'доставка'
        elif has_transport:
            suffix_parts = 'транспорт'
        else:
            suffix_parts = 'выборка'

        if has_ads and (has_823 or has_1432):
            suffix_parts += ' с доставкой'
        if has_transport and (has_823 or has_1432 or has_ads):
            suffix_parts += ' с транспортом'
        
        return f'{base} {suffix_parts}.pdf'

class Utils:
    async def get_initials(value: str | None) -> str:
        return f"{value[0]}." if value else ""

class PdfService:

    async def convert_html_to_pdf(html_content: str, output_filename: str) -> str:
        loop = asyncio.get_event_loop()
        html = HTML(string=html_content)
        await loop.run_in_executor(None, html.write_pdf, output_filename)

class TransportUrlBuilder:
    BASE_URL = "https://csort-transport.ru/static/new_data/web_data"
    
    @staticmethod
    def build(cls, document_name: str, id_deal: str) -> str:

        if document_name in ("tg", "tst"):
            urlTransport = f"/TG_FOLDER/{document_name}"
        else:
            urlTransport = f"{document_name}"

        return f"{cls.BASE_URL}/{urlTransport}/{id_deal}.png"

class ServiceTextGenerator:

    def generate(data: dict, total_sum_services: str) -> str:
        for item in data.get("List", []):
            if item.get("ads") == "ads":
                return f"- цена услуг: {total_sum_services} рублей; <br>"
            else:
                return ""

# class HtmlProcessor:

#     EQUIPMENT_TYPES = {
#         'CSZE': 'Конвейер цепной',
#         'CSCC': 'Конвейер скребковый',
#         'CSE': 'Зерновой элеватор',
#     }

#     TRANSPORT_CODES = ('csze', 'cse', 'cscc', 'csbc')

#     def __init__(self, html_template: str):
#         self.soup = BeautifulSoup(html_template, 'html.parser')
#         self.spec_elevator = SpecElevatorBuilder(html_template)
#         self.elements = self._find_elements()
#         self.count_table = 1
#         self.last_spec_div = None

#     # ==========================================================
#     # Поиск элементов
#     # ==========================================================

#     def _find_elements(self) -> dict:
#         return {
#             'table823': self.soup.find("div", id="table823"),
#             'title823': self.soup.find("b", id="title823"),
#             'title1432': self.soup.find("b", id="title1432"),
#             'tableEquip': self.soup.find("div", id="tableEquip"),
#             'str823On': self.soup.find_all(class_="str823On"),
#             'ads_on': self.soup.find_all(class_="ads_on"),
#             'ads_off': self.soup.find_all(class_="ads_off"),
#             'ads_zero': self.soup.find("p", class_="ads_zero"),
#             'services_table': self.soup.find("div", id="tableAds"),
#             'SeparHaveDiv': self.soup.find_all(class_="SeparHaveDiv"),
#             'SeparHaveTd': self.soup.find_all(class_="SeparHaveTd"),
#             'SeparNoneDiv': self.soup.find("p", class_="SeparNoneDiv"),
#             'SeparNoneTd': self.soup.find_all(class_="SeparNoneTd"),
#             'CSHaveDiv': self.soup.find("div", class_="CSHaveDiv"),
#             'PackingList': self.soup.find("div", class_="PackingList"),
#         }

#     # ==========================================================
#     # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
#     # ==========================================================

#     def _set_style(self, element, style: str):
#         if element:
#             element["style"] = style

#     def _set_style_for_many(self, elements, style: str):
#         for el in elements or []:
#             el["style"] = style

#     def _add_paragraph(self, element, text: str, position: int = 0):
#         if not element:
#             return
#         tag = self.soup.new_tag(
#             'p',
#             style='display:block;padding:0;margin:0;font-weight:600;'
#         )
#         tag.string = text
#         element.insert(position, tag)

#     # ==========================================================
#     # ОБРАБОТКА ИЗОБРАЖЕНИЙ ТРАНСПОРТА
#     # ==========================================================

#     async def _process_transport_images(self, urls: list):
#         if not urls:
#             return

#         table_transport = self.soup.find(id='tableTransport')
#         if not table_transport:
#             return

#         for url in urls:
#             image = ImageProcessor(url)

#             margin = await image.calculate_margin()
#             size = await image.get_image_size()

#             style = self._build_image_style(size, margin)

#             wrapper = self.soup.new_tag(
#                 'p',
#                 style='width:100%;text-align:center;font-weight:600;text-transform:uppercase;'
#             )
#             wrapper.string = 'габаритные размеры'

#             img = self.soup.new_tag(
#                 'img',
#                 id=f"urlTransport_{self.count_table}",
#                 src=url,
#                 style=style
#             )

#             wrapper.append(img)
#             table_transport.insert_after(wrapper)

#             self.count_table += 1

#     def _build_image_style(self, size: tuple, margin: int) -> str:
#         if size[0] > size[1]:
#             return f"width:100%;transform:rotate(-90deg);margin-top:{margin}px;"
#         return "width:100%;margin-top:20px;"

#     # ==========================================================
#     # ОБОРУДОВАНИЕ
#     # ==========================================================

#     async def _process_equipment(
#         self,
#         item: dict,
#         additional_info: dict,
#         id_row_elevator: int,
#         lang: str
#     ) -> bool:

#         name = item.get("name", "").lower()
#         name_print = item.get("name_print", "")

#         has_transport = any(code in name for code in self.TRANSPORT_CODES)

#         if 'cs' not in name:
#             return has_transport

#         equipment_code = name_print.split()[2] if len(name_print.split()) > 2 else ""
#         equipment_code = equipment_code.split('-')[0]

#         equipment_type = self.EQUIPMENT_TYPES.get(
#             equipment_code,
#             'Конвейер ленточный'
#         )

#         spec_div = await self.spec_elevator.add_str_table_app_spec_elevator(
#             additional_info,
#             self.count_table,
#             name_print,
#             equipment_type,
#             id_row_elevator,
#             lang
#         )
        
#         self.last_spec_div = spec_div
#         self.count_table += 1
#         return has_transport

#     # ==========================================================
#     # СЕПАРАТОР
#     # ==========================================================

#     def _process_separator(self, name: str):
#         if 'фотосепаратор' not in name.strip():
#             return

#         self._set_style_for_many(
#             self.elements['SeparHaveDiv'],
#             "display:block;padding:0;margin:0;"
#         )

#         self._set_style_for_many(
#             self.elements['SeparHaveTd'],
#             "width:100%;padding:0;text-align:right;padding-bottom:10px;border:none;"
#         )

#         self._set_style(self.elements['SeparNoneDiv'], "display:none;")
#         self._set_style_for_many(self.elements['SeparNoneTd'], "display:none;")

#     # ==========================================================
#     # АНАЛИЗ ДАННЫХ
#     # ========================================================== 

#     async def _analyze_items(self, items, additional_info, id_row_elevator, lang):
#         flags = {
#             "has_ads": False,
#             "has_823": False,
#             "has_1432": False,
#             "ads_zero": False,
#             "has_other_service": False,
#             "has_transport": False,
#         }

#         for item in items:
#             name = item.get("name", "").lower()

#             flags["has_transport"] |= await self._process_equipment(
#                 item, additional_info, id_row_elevator, lang
#             )

#             self._process_separator(name)

#             # --- услуги
#             if item.get("ads") == "ads":
#                 if 'доставке' in name or 'программа' in name:
#                     flags["ads_zero"] |= item.get("sum", 0) < 1
#                     flags["has_ads"] |= item.get("sum", 0) >= 1
#                 else:
#                     flags["has_other_service"] = True

#             flags["has_823"] |= "823" in name
#             flags["has_1432"] |= "1432" in name

#         return flags

#     # ==========================================================
#     # ОБНОВЛЕНИЕ СЕКЦИЙ
#     # ==========================================================

#     def _update_sections(self, flags: dict):

#         has_services = flags["has_ads"] or flags["has_other_service"]
#         has_equipment = flags["has_823"] or flags["has_1432"]

#         if not has_services and not has_equipment:
#             self._add_paragraph(self.elements['tableEquip'], '1. ОБОРУДОВАНИЕ')
#             self._set_style_for_many(
#                 self.elements['ads_off'],
#                 "display:block;padding:0;margin:0;"
#             )
#             if self.elements['PackingList'] and self.last_spec_div:
#                 self.elements['PackingList'].insert_after(self.last_spec_div)
#             return

#         if has_equipment:
#             self._add_paragraph(self.elements['tableEquip'], '2. ОБОРУДОВАНИЕ')
#             self._set_style(self.elements['table823'], "display:block;margin-top:10px;")

#         if has_services:
#             self._add_paragraph(self.elements['services_table'], '3. УСЛУГИ')
#             self._set_style(self.elements['services_table'], "display:block;margin-top:10px;")
#             self._set_style_for_many(
#                 self.elements['ads_on'],
#                 "display:block;padding:0;margin:0;"
#             )

#         if flags["has_823"]:
#             self._set_style(self.elements['title823'], "display:block;margin-bottom:10px;")

#         if flags["has_1432"]:
#             self._set_style(self.elements['title1432'], "display:block;margin-bottom:10px;")

#     # ==========================================================
#     # ПУБЛИЧНЫЙ МЕТОД
#     # ==========================================================

#     async def process(self, replacements: dict, id_row_elevator: int, lang: str):

#         data = replacements.get("data", {})
#         additional_info = data.get("additional_info", {})
#         transport_urls = replacements.get("arrUrlTransport", [])

#         await self._process_transport_images(transport_urls)

#         flags = await self._analyze_items(
#             data.get("List", []),
#             additional_info,
#             id_row_elevator,
#             lang
#         )

#         self._update_sections(flags)

#         return (
#             str(self.soup),
#             flags["has_ads"],
#             flags["has_1432"],
#             flags["has_823"],
#             flags["has_transport"],
#         )

class ContractApplicationBuilder:

    def __init__(self, html: str, list_data: list):
        self.html = html
        self.list_data = list_data

    async def build(self, replacements: dict) -> str:
        builder = ContractTableBuilder(self.html, self.list_data)

        self.html = await builder.replace_in_html(replacements)
        self.html = await builder.add_str_table_app_spec()
        self.html = await builder.add_str_table_app_823()
        self.html = await builder.add_str_table_app_tableAds(replacements["total_summ_services"])
        self.html = await builder.add_str_table_app_2()
        self.html = await builder.add_str_table_app_3()

        return self.html

async def processHtmlTemplate(html_template, replacements, id_row_elevator, lang):
    soup = BeautifulSoup(html_template, 'html.parser')
    spec_elevator = SpecElevatorBuilder(html_template)

    elements = {
        'app': soup.find("table", id="app"),
        'table823': soup.find("div", id="table823"),
        'title823': soup.find("b", id="title823"),
        'title1432': soup.find("b", id="title1432"),
        'tableEquip': soup.find("div", id="tableEquip"),
        'str823On': soup.find_all(class_="str823On"),
        'ads_on': soup.find_all(class_="ads_on"),
        'ads_off': soup.find_all(class_="ads_off"),
        'ads_zero': soup.find("p", class_="ads_zero"),
        'services_table': soup.find("div", id="tableAds"),
        'SeparHaveDiv': soup.find_all(class_="SeparHaveDiv"),
        'SeparHaveTd': soup.find_all(class_="SeparHaveTd"),
        'SeparNoneDiv': soup.find("p", class_="SeparNoneDiv"),
        'SeparNoneTd': soup.find_all(class_="SeparNoneTd"),
        'CSHaveDiv': soup.find("div", class_="CSHaveDiv"),
        'PackingList':  soup.find("div", class_="PackingList"),
    }

    data = replacements.get("data", {})
    arrUrlTransport = replacements['arrUrlTransport']
    # PhotoSeparNone = replacements['PhotoseparName']
    additional_info = data['additional_info']

    count_table = 1
    if arrUrlTransport:
        tableTransport = soup.find(id='tableTransport')

        for urlTransport in arrUrlTransport:
            image_class = ImageProcessor(urlTransport)
            margin_top = await image_class.calculate_margin()
            img_size = await image_class.get_image_size() 

            style = "width: 100%;"
            style += f"transform: rotate(-90deg); margin-top: {margin_top}px;" if img_size[0] > img_size[1] else "margin-top: 20px"

            pageTage = soup.new_tag('p', style='width: 100%; padding: 0; text-align: center; font-weight: 600; text-align: center; text-transform: uppercase;')
            pageTage.string = 'габаритные размеры'
            imgTag = soup.new_tag('img', id=f"urlTransport_{count_table}", src=urlTransport, style=style)

            pageTage.append(imgTag)
            tableTransport.insert_after(pageTage)
            count_table += 1

    has_ads = False
    has_823 = False
    has_1432 = False
    ads_zero = False
    has_other_service = False
    has_transport= False

    for item in data.get('List', []):
        name = item.get('name','').lower()
        name_print = item.get('name_print','')

        if any(transport in name for transport in ['csze', 'cse', 'cscc', 'csbc']):
            has_transport = True

        if 'cs' in name:
            equipment_types = {
                'CSZE':'Конвейер цепной',
                'CSCC':'Конвейер скребковый',
                'CSE':'Зерновой элеватор',
            }

            equipment_code = name_print.split()[2]
            if '-' in equipment_code:
                equipment_code = equipment_code.split('-')[0]
            equipment_type = equipment_types.get(equipment_code, 'Конвейер ленточный')

            spec_div = await spec_elevator.add_str_table_app_spec_elevator(additional_info, count_table, name_print, 
                equipment_type, id_row_elevator, lang)

            elements['PackingList'].insert_after(spec_div)
            # elements['services_table'].insert_after(spec_div)
            # if 'csze' in name:
            #     elements['CSHaveDiv']["style"] = "display: block;"
                
            count_table += 1

        if 'фотосепаратор' in name.strip():
            for el in elements['SeparHaveDiv']:
                el["style"] = "display: block; padding: 0; margin: 0;"
            for el in elements['SeparHaveTd']:
                el["style"] = "width: 100%; padding: 0; text-align: right; padding-bottom: 10px; border: none;"

            elements['SeparNoneDiv']["style"] = "display: none;"
            for el in elements['SeparNoneTd']:
                el["style"] = "display: none;"
            
        if not has_ads and item.get('ads') == 'ads':
            if 'доставке' or 'программа' in name.strip():
                if item.get('sum') < 1:
                    ads_zero = True
                    has_ads = False
                else:
                    has_ads = True
            else:
                has_other_service = True    
        
        if not has_823 and '823' in name:
            has_823 = True
        if not has_1432 and '1432' in name:
            has_1432 = True

    if has_ads or has_other_service or has_823 or has_1432:
        if has_ads or has_other_service:
            if has_ads:
                for el in elements['ads_on']:
                    el["style"] = "display: block; padding: 0; margin: 0;"
                    elements['services_table']["style"] = "display: block; margin-top: 10px;"
                
            if has_other_service:
                new_paragraph = soup.new_tag('p', style='display: block; padding: 0; margin: 0; font-weight: 600;')
                new_paragraph.string = '2. УСЛУГИ'
                elements['services_table'].insert(0, new_paragraph)
                elements['services_table']["style"] = "display: block; margin-top: 10px;"
            if ads_zero:
                elements['ads_zero'] = "display: block; padding: 0; margin: 0;"

        if has_823 or has_1432:
            new_paragraph = soup.new_tag('p', style='display: block; padding: 0; margin: 0; font-weight: 600;')
            new_paragraph.string = '2. ОБОРУДОВАНИЕ'
            elements['tableEquip'].insert(0, new_paragraph)
            elements['table823']["style"] = "display: block; margin-top: 10px;"

            if has_ads or has_other_service:
                new_paragraph = soup.new_tag('p', style='display: block; padding: 0; margin: 0; font-weight: 600;')
                new_paragraph.string = '3. УСЛУГИ'
                elements['services_table'].insert(0, new_paragraph)
                for el in elements['str823On']:
                    el["style"] = "display: block; padding: 0; margin: 0;"
                for el in elements['ads_on']:
                        el["style"] = "display: none;"
            else:
                for el in elements['ads_on']: # если нет услуг, но есть программа
                    el["style"] = "display: block; padding: 0; margin: 0;"
                for el in elements['ads_off']:
                    el["style"] = "display: none;"

            if has_823:
                elements['title823']["style"] = "display: block; margin-bottom: 10px;"
            if has_1432:
                elements['title1432']["style"] = "display: block; margin-bottom: 10px;"


        if (has_ads or has_other_service) and not(has_823 or has_1432):
            new_paragraph = soup.new_tag('p', style='display: block; padding: 0; margin: 0; font-weight: 600;')
            new_paragraph.string = '1. ОБОРУДОВАНИЕ'
            elements['tableEquip'].insert(0, new_paragraph)
            new_paragraph = soup.new_tag('p', style='display: block; padding: 0; margin: 0; font-weight: 600;')
            new_paragraph.string = '2. УСЛУГИ'
            elements['services_table'].insert(0, new_paragraph)
    else:
        new_paragraph = soup.new_tag('p', style='display: block; padding: 0; margin: 0; font-weight: 600;')
        new_paragraph.string = '1. ОБОРУДОВАНИЕ'
        elements['tableEquip'].insert(0, new_paragraph)

        for el in elements['ads_off']:
            el["style"] = "display: block; padding: 0; margin: 0;"


    return str(soup), has_ads, has_1432, has_823, has_transport
 
async def main(data,key):
    start_price = 0
    discount_price = 0
    price_notNDS = 0
    price_withDiscount = 0
    SumPrice_withDiscount = 0
    document_name = None
    PhotoseparName = None
    PhotoseparModel = None

    arrUrlTransport = []
    
    info_users = await page_CalcKP.UserInfo_Key_offer(key)

    lang = info_users['user'][0]['language'] 
    terms_payment_split = data['terms_payment'].split()
    address_delivery = data['additional_info'].get('address_delivery', 'Адрес покупателя')
    pickup_place = 'проспект Калинина, 75, г.Барнаул, Россия, Алтайский край'

    data['note'] = {
        'Услуги по доставке': 'Доставка до адреса Покупателя',
        'Настройка оборудования на сортировку с выездом': 'Для оборудования',
        'Гарантия':{
            'photoseparator':'Гарантия не распространяется на ресурсные (расходные) материалы, требующие замены (лампы, щетки системы очистки отсеков обследования, фильтрующие элементы и прочие запасные части, подвергающиеся естественному износу в процессе использования оборудования, в том числе лотки подачи и эжектор)',
            'compressor': 'Гарантия не распространяется на ресурсные (расходные) материалы, требующие замены (компрессорное масло, фильтрующие элементы и прочие запасные части, подвергающиеся естественному износу в процессе использования оборудования)',
            'elevator': 'Гарантия не распространяется на расходные (быстро изнашиваемые) материалы, в том числе на  цепи и  ковши.',
        }
    }

    data['guarantee'] = {
        'photoseparator':{
            'smart': '26',
            'compact': '12',
            'minisort': '12',
        },
        'compressor': '12',
        'elevator': '12',
    }

    data['guarantee_start'] = {
        'photoseparator': 'С момента подписания сторонами Акта приема-передачи оборудования',
        'compressor': 'С момента подписания сторонами Акта приема-передачи оборудования',
        'elevator': 'С момента подписания сторонами Акта приема-передачи оборудования',
    }

    data['guarantee_end'] = {
        'photoseparator': 'При нарушении условий гарантии',
        'compressor': 'При нарушении условий гарантии',
        'elevator': 'При нарушении условий гарантии',
    }

    arr_kp_info, ConditionsData = await asyncio.gather(
        page_API.getKPInfo_Offer(key),
        page_API.getConditions_Offer(lang)
    )

    for item in data['List']:

        PhotoseparName = None
        PhotoseparModel = None
        if 'Фотосепаратор' in item['name'].strip():
            photosepar = item['name'].split('СмартСорт')
            PhotoseparName = photosepar[0] + 'СмартСорт'
            PhotoseparModel = photosepar[1].strip()
            start_price = item['sum'] / 1.22
            discount_price = "{:.0f}".format(int(start_price) * 0.05)
            price_notNDS = int(start_price) - int(discount_price)
            price_withDiscount = int(item['sum']) - int(discount_price)
            SumPrice_withDiscount = price_withDiscount * int(item['count'])


    dop_info = {
        'terms_payment_text': data.get('terms_payment_text', ''),
        'terms_payment_procent': terms_payment_split[0],
        'terms_payment_procent_text': 'Предоплата',
        'delivery_text': ConditionsData['delivery_terms'][0]['delivery_timeframe'],
        'delivery_place': address_delivery,
        'pickup_place': pickup_place,
        'export_conditions': 'В течение 5 рабочих дней после уведомления о готовности. Адрес: проспект Калинина, 75, г. Барнаул, Россия, Алтайский край',
        'guarantee': data.get('guarantee', ''),
        'date_open': data.get('guarantee_start', ''),
        'date_close': data.get('guarantee_end', ''),
        'note': data.get('note'),
        'product': data['additional_info'].get('prod', ''),
        'purpose': data['additional_info'].get('purpose', ''),
        'garbage': data['additional_info'].get('garbage', ''),
        'sign': '_____',
        'date': data.get('date', ''),
        'code_okpd': '28.93.2',
        'start_price': start_price,
        'price_notNDS': price_notNDS,
        'price_withDiscount': price_withDiscount,
        'discont': '5',
        'discount_price': discount_price,
        'SumPrice_withDiscount': SumPrice_withDiscount

    }

    for i in range(len(data['List'])):
        data['List'][i].update(dop_info)

    doc_template = DocumentTemplate(data["NameFile"])

    data_dict = DataFunc(data)
    seller_dict = data_dict.seller
    buyer_dict = data_dict.buyer
 
    html_template = await doc_template.read_html_template()
    # processor = HtmlProcessor(html_template)
    totals, table_str = DocumentCalculator.calculate_totals(data)
    
    total_sum_spec = str("{:.2f}".format(totals['total_sum']))
    total_sum_spec_services = str("{:.2f}".format(totals['service_sum']))
    total_sum_spec_machines = str("{:.2f}".format(totals['machines_sum']))

    nds_now = int(data['additional_info']['nds']) if data['additional_info']['nds'] else 22

    nds_total_sum = float(totals['total_sum']) * nds_now / (100+nds_now)
    nds_total_sum_spec = "{:.2f}".format(nds_total_sum)
    
    sum_propis_spec = await PluralForm.sum_propis(total_sum_spec)

    date_str = str(datetime.datetime.today().strftime("%d.%m.%Y"))
    date = pd.to_datetime(date_str, format='%d.%m.%Y')
    date = date + pd.offsets.BDay(5)
    date_work_days = str(date.strftime('%d.%m.%Y'))
    
    first_name_buyer_init = await Utils.get_initials(buyer_dict['first_name'])
    surname_buyer_init = await Utils.get_initials(buyer_dict['surname'])

    first_name_seller_init = await Utils.get_initials(seller_dict['first_name'])
    second_name_seller_init = await Utils.get_initials(seller_dict['surname'])
    
    kp_info = arr_kp_info['createKP'][0]['group_info']
    id_row_elevator = kp_info['elevator']
    id_json_document_elevator = list(data['additional_info'].get('id_json', {}).values())

    
    additional_info = arr_kp_info["createKP"][0]["additional_info"]
    count_user_elevator = list(id_row_elevator.values())
    dop_info_elevator_task = DopInfo_Elevator(
        list(additional_info.get("id_json", {}).values()), count_user_elevator, lang
    )
    dop_info_elevator = await asyncio.gather(dop_info_elevator_task)

    paymentMetod = PaymentGenerator.GeneratePaymentMetod(data, total_sum_spec)
    dogovor2_1 = ServiceTextGenerator.generate(data,total_sum_spec_services)
    for elevator_name in id_json_document_elevator:
        with open(f'./Front/static/document/deal_elevator/{elevator_name}.json', encoding='utf-8') as json_file:
            dataElevator = json.load(json_file)
            nameModel = dataElevator['modelName'].lower()
            if 'csze' in nameModel:
                if any(numberModel in nameModel for numberModel in ('10','20','35')):
                    documentSplit = elevator_name.split('.')
                    document_name = documentSplit[0]
                    id_deal = elevator_name 
                    urlTransport = TransportUrlBuilder.build(document_name, id_deal)
                    if urlTransport not in arrUrlTransport:
                        arrUrlTransport.append(urlTransport)

    seller_data = {
        "bank_seller": seller_dict['bank_info'],
        "bik_seller": seller_dict['bic'],
        "checking_account_seller": seller_dict['checking_account'],
        "inn_seller": seller_dict['inn'],
        "kpp_seller": seller_dict['kpp'],
        "corporate_account_seller": seller_dict['corporate_account'],
        "organization_shortname_seller": seller_dict['organization_shortname'],
        "index_seller": seller_dict['index'],
        "Phone_number_seller": seller_dict['phone_number'],
        "first_Name_seller": seller_dict['first_name'],
        "second_name_seller": seller_dict['surname'],
        "middle_Name_seller": seller_dict['second_name'],
        "position_user_seller": seller_dict['position_user'],
        "ogrn_seller": seller_dict['ogrn'],
        "address_seller": seller_dict['address'],
        "email_seller": seller_dict['email'],
        "first_Name_cut_seller": first_name_seller_init,
        "middle_Name_cut_seller": second_name_seller_init,
    }

    buyer_data = {
        "organization_shortname_buyer": buyer_dict['organization_shortname'],
        "corporate_account_buyer": buyer_dict['corporate_account'],
        "inn_buyer": buyer_dict['inn'],
        "kpp_buyer": buyer_dict['kpp'],
        "Phone_number_buyer": buyer_dict['phone_number'],
        "middle_Name_buyer": buyer_dict['second_name'],
        "position_user_buyer": buyer_dict['position_user'],
        "ogrn_buyer": buyer_dict['ogrn'],
        "address_buyer": buyer_dict['address'],
        "email_buyer": buyer_dict['email'],
        "Bank_info_buyer": buyer_dict['bank_info'],
        "first_Name_cut_buyer": first_name_buyer_init,
        "last_Name_cut_buyer": surname_buyer_init,
        "bik_buyer": buyer_dict['bic'],
        "checking_account_buyer": buyer_dict['checking_account'],
    }

    document_data = {
        "Preambula": data['Preambula'],
        "Date_create": Date_create,
        "total_summ_spec": total_sum_spec,
        "nds_total_summ_spec": nds_total_sum_spec,
        "table_str": table_str,
        "summ_propis_spec": sum_propis_spec,
        "date_work_days": date_work_days,
        "nubmer_dogov": data['number'],
        "city": data['city'],
        "day": day,
        "month_name": month_name,
        "month": month,
        "year": year,
        "nds_now": nds_now,
        "total_summ_spec_services":total_sum_spec_services,
        "total_summ_spec_machines":total_sum_spec_machines,
        "total_count_services": totals['service_count'],
        "total_summ_machines": totals['machines_sum'],
        "total_summ_services": totals['service_sum'],
        "total_count_machines": totals['machines_count'],
        "total_count": totals['total_count'],
        "dogovor2_1": dogovor2_1,
        "paymentMetod": paymentMetod,
        "data": data,
        "PhotoseparName": PhotoseparName,
        "PhotoseparModel": PhotoseparModel,
        "address_delivery": address_delivery,
        "pickup_place": pickup_place,
        "arrUrlTransport": arrUrlTransport,
        "dop_info_elevator": dop_info_elevator,
    }

    replacements = {
        **seller_data,
        **buyer_data,
        **document_data
    }
    
    # html_template, has_ads, has_1432, has_823, has_transport = await processor.process(replacements, id_row_elevator, lang)
    html_template, has_ads, has_1432, has_823, has_transport = await processHtmlTemplate(html_template, replacements, id_row_elevator, lang)
    contract_builder = ContractApplicationBuilder(html_template, data['List'])
    result_html = await contract_builder.build(replacements)
    
    pdf_filename = FileNameGenerator.generate(data, has_ads, has_1432, has_823, has_transport)

    await PdfService.convert_html_to_pdf(result_html, pdf_filename)

    data_send ={
        'service':'КП',
        'chatID':data['Chat_id'],
        'UserName': data['UserName'],
        'page': data['page'],
        'path_file': pdf_filename,
        'keyCP':data['key'],
        'text':f'Договор поставки оборудования №{data["number"]} {buyer_dict["organization_shortname"]} на сумму {total_sum_spec_machines} от {date_str}'
    } 
    TgSend.agrement_PDFSend(data_send)

    if(data['client']):
        data_send ={
            'chatID':'-1002195710985',
            'UserName': data['UserName'],
            'page': data['page'],
            'path_file': pdf_filename,
            'keyCP':data['key'],
            'text':f'Договор поставки оборудования №{data["number"]} {buyer_dict["organization_shortname"]} на сумму {total_sum_spec_machines} от {date_str}'
        }   
        TgSend.ManagerGetPDF(data_send)
        
  
    
    # if pdf_filename and os.path.exists(pdf_filename):
    #     os.remove(pdf_filename)
    #     print(f"Файл {pdf_filename} удалён в блоке finally.")

    # сюда сохранение договра на ftp



    # ftp_client = FTPClient(server, username, password)

    # ftp_client.upload_file(data["NameFile"], output_filename, f'/{data["NameFile"]}/Agrement')
    # ftp_client.close_connection()


    # return output_filename

