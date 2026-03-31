import requests
from pymorphy3 import MorphAnalyzer

morph = MorphAnalyzer()

def MR_country(motor_reductor: str | None) -> str | None:
    country = None
    if motor_reductor:
        mr = motor_reductor.lower()
        if "it" in mr:
            country = "Италия"
        elif "ch" in mr:
            country = "Китай"
    return country

def name_photo(model: str) -> str | None:
    if not model:
        return None
    if 'CSE' in model:
        return model[:3]
    return model[:4]

def product_name(dataElevator: dict, lang: str):
    product_link = 'https://csort-transport.ru/product_k'
    product_page = requests.get(product_link)
    product_json = product_page.json()
    product_result = product_json["result"]

    product_name_val = None
    product_coef = None
    for item in product_result:
        if dataElevator['id_product'] == item['ID']:
            product_coef = item['k']
            product_name_val = item['nameProduct'] if lang == 'ru' else item['nameProductEn']
            break
    return product_name_val, product_coef

def convert_case(words: str, case: str) -> str:
    if len(words.split()) > 1:
        return ' '.join(morph.parse(w)[0].inflect({case}).word for w in words.split())
    parsed = morph.parse(words)[0]
    return parsed.inflect({case}).word
