from bs4 import BeautifulSoup
import asyncio
from weasyprint import HTML
from num2words import num2words
import pandas as pd
import qrcode
import requests
from routers.push_message import TgSendMess
import routers.json_to_xml as json_to_xml
from routers.ftp_client import FTPClient
import asyncio
import json
import os
import routers.ReadCheck as ReadCheck
from datetime import datetime, timedelta
import base64
from routers.ReadCheck import PluralForm

TgSend = TgSendMess()
server = '194.63.141.80'
username = 'user2824307'
password = 'Hj2dOu2agcj7'
HTML_DIR = 'Front/static/document/check/HTML'
PDF_DIR = 'Front/static/document/check/PDF'
QR_DIR = 'Front/static/document/check/Qr_code'
NDS = 22

class SupportFunc():
    def __init__(self, file_name: str):
        self.file_name = file_name

    def read_html_template(self):
        path = os.path.join(HTML_DIR, f'{self.file_name}.html')
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def replace_in_html(self, html_content: str, replacements: dict) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')

        for node in soup.find_all(string=True):
            text = node
            for key, value in replacements.items():
                if key in text:
                    text = text.replace(key, str(value))
            node.replace_with(text)

        for img_tag in soup.find_all('img', src=True):
            src = img_tag['src']
            for key, value in replacements.items():
                if key in src:
                    img_tag['src'] = src.replace(key, str(value))
                        
        return str(soup)

    def add_list_items_to_table(self, html_content, items):
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find_all('table')[2] 

        for item in items:
            if 'программа' in item['name_print']:
                continue
            row = soup.new_tag('tr')
            for key in ['number', 'name_print', 'count', 'price', 'sum']:
                cell = soup.new_tag('td', style='padding: 0; padding-left: 5px')
                cell.string = str(int(item[key])) if key == 'count' else str(item[key])
                row.append(cell)
            table.append(row)

        return str(soup)

    async def convert_html_to_pdf(self, html_content, output_filename):
        loop = asyncio.get_event_loop()
        html = HTML(string=html_content)
        await loop.run_in_executor(None, html.write_pdf, output_filename)
        
    async def qr_code(self, name_company_buyer_short: str, checking_account_buyer: str, corporate_account_buyer: str, bank_buyer: str,
        bik_buyer: str, inn_buyer: str, kpp_buyer: str, summ_user_point: str):
        
        data = (
            f"ST00012|Name={name_company_buyer_short}|PersonalAcc={checking_account_buyer}|BankName={bank_buyer}|BIC={bik_buyer}|"
            f"CorrespAcc={corporate_account_buyer}|PayeeINN={inn_buyer}|KPP={kpp_buyer}|Sum={summ_user_point}"
        )
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save(
            os.path.join(QR_DIR, f'qr_code_{inn_buyer}.png')
        )


def work_date_after(date_str: str, business_days: int = 5) -> str:
    date = pd.to_datetime(date_str, format='%d.%m.%Y') + pd.offsets.BDay(business_days)
    return date.strftime('%d.%m.%Y')


def compute_totals(items: list) -> tuple[str, str]:
    total = sum(item['sum'] for item in items)
    nds   = total * NDS / (100 + NDS)
    return f'{total:.2f}', f'{nds:.2f}'


def get_initials(last_name):
    if last_name:
        return last_name[0] + '.'
    return ''
       

def deep_get(d, keys, default=None):
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


def to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def GetJson_bitrix(data):
    new_json_data = json_to_xml.return_json(data)
    # print('new_json_data')

    # print(new_json_data)

    url = "https://csort-bitrix24.webtm.ru/api/v1/customer-order/"
    headers = {
        "Authorization": "Bearer 503FQAqSnvSMXf45w4gWokVP87lqsv",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    timeout = 60

    today_str = datetime.now().strftime("%d.%m.%Y")
    file_name = f"ПРЕДЛОЖЕНИЕ от {today_str} №{data['key']}.pdf"
    pdf_path = os.path.join("Front", "static", "document", "reports", file_name)

    pdf_base64 = file_to_base64(pdf_path)

    new_json_data["document"] = {
        "name": file_name,
        "mime": "application/pdf",
        "content_base64": pdf_base64,
    }
    response = requests.post(
        url,
        headers=headers,
        json=new_json_data,
        timeout=timeout,
    )

    code = response.status_code
    text = response.text

    content = None
    try:
        content = response.json()
    except ValueError:
        pos = text.find("{")
        if pos != -1:
            try:
                content = json.loads(text[pos:])
            except ValueError:
                content = None

    if content is None:
        return {
            "code": code,
            "id_deal": None,
            "text_code": "Bad response (not JSON)",
            "raw": text[:2000],
        }

    deal_id = to_int(deep_get(content, ["result", "original", "result", "deal_id"]))
    invoice_id = to_int(deep_get(content, ["result", "original", "result", "invoice_id"]))
    company_id = to_int(deep_get(content, ["result", "original", "result", "company_id"]))

    msg = content.get("message") or deep_get(content, ["result", "original", "messages"])
    err = content.get("error") or deep_get(content, ["result", "original", "error"])

    has_problem = bool(err) or (isinstance(msg, str) and msg and msg != "success")

    if has_problem:
        if deal_id is not None:
            return {
                "code": code,
                "id_deal": deal_id,
                "invoice_id": invoice_id,
                "company_id": company_id,
                "text_code": msg or err or "Conflict",
                "raw": content,
            }
        return {
            "code": code,
            "id_deal": None,
            "text_code": msg or err or "Unknown error",
            "raw": content,
        }

    return {
        "code": code,
        "id_deal": deal_id,
        "invoice_id": invoice_id,
        "company_id": company_id,
        "text_code": "",
        "raw": content,
    }


async def main(data: dict) -> str:
    support       = SupportFunc(data['NameFile'])
    html = support.read_html_template()

    seller = data['seller']
    buyer = data['buyer']
    number = data['number']
    date_str = datetime.today().strftime('%d.%m.%Y')

    total_sum_str, nds_total_str = compute_totals(data['List'])
    sum_propis = await PluralForm.sum_propis(total_sum_str)
    date_work_days = work_date_after(date_str)

    date_dict   = ReadCheck.DataFunc(data)
    seller_info = date_dict.seller
    buyer_info  = date_dict.buyer
    
    replacements = {
        # seller
        'bank_seller':                  seller['bank_info'],
        'bik_seller':                   seller['bic'],
        'checking_account_seller':      seller['checking_account'],
        'inn_seller':                   seller['inn'],
        'kpp_seller':                   seller['kpp'],
        'corporate_account_seller':     seller['corporate_account'],
        'organization_fullname_seller': seller['organization_fullname'],
        'organization_shortname_seller': seller['organization_shortname'],
        'index_seller':                 seller['index'],
        'address_seller':               seller['address'],
        'phone_number_seller':          seller['phone_number'],
        # buyer
        'organization_shortname_buyer': buyer['organization_shortname'],
        'inn_buyer':                    buyer['inn'],
        'kpp_buyer':                    buyer['kpp'],
        'address_buyer':                buyer['address'],
        'phone_number_buyer':           buyer['phone_number'],
        # document
        'date_create':                  date_str,
        'number':                       number,
        'total_sum_str':                total_sum_str,
        'nds_total_str':                nds_total_str,
        'sum_propis':                   sum_propis,
        'date_work_days':               date_work_days,
        'qr_code_png':                  f'qr_code_{seller["inn"]}',
        # signer
        'position_user_seller':         seller_info['position_user'],
        'middle_Name_seller':           seller_info['second_name'],
        'first_Name_cut_seller':        get_initials(seller_info['first_name']),
        'middle_Name_cut_seller':       get_initials(seller_info['surname']),
        'position_user_buyer':          buyer_info['position_user'],
        'middle_Name_buyer':            buyer_info['second_name'],
        'first_Name_cut_buyer':         get_initials(buyer_info['first_name']),
        'last_Name_cut_buyer':          get_initials(buyer_info['surname']),
    }

    support.qr_code(
        seller['organization_shortname'], seller['checking_account'], seller['corporate_account'], seller['bank_info'], seller['bic'],
        seller['inn'], seller['kpp'], total_sum_str,
    )

    html = support.replace_in_html(html, replacements)
    html = support.add_list_items_to_table(html, data['List'])

    pdfdirs = os.path.join("Front", "static", "document", "check", "PDF")
    os.makedirs(pdfdirs, exist_ok=True)
    output_filename = os.path.join(PDF_DIR, f'{data["NameFile"]} №{number}r.pdf')
    await support.convert_html_to_pdf(html, output_filename)

    notification_text = (
        f'Счет №{number} {buyer_info["organization_shortname"]} '
        f'на сумму {total_sum_str} от {date_str}'
    )
    base_payload = {
        'service':   'КП',
        'UserName':  data['UserName'],
        'page':      data['page'],
        'path_file': output_filename,
        'keyCP':     data['key'],
        'text':      notification_text,
    }

    TgSend.agrement_PDFSend({**base_payload, 'chatID': data['Chat_id']})

    if data.get('client'):
        TgSend.ManagerGetPDF({**base_payload, 'chatID': '-1002195710985'})

    return output_filename


