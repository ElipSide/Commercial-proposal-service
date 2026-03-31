"""
Функции работы с API коммерческих предложений и расчётов оборудования.

Вход:
- aiohttp session, user_id и словари form_data/data_list.

Выход:
- JSON-ответы backend API или None при ошибке.
"""

import json
import math

import aiohttp
import requests

from env_settings import get_settings


SETTINGS = get_settings()
BASE_URL_API = SETTINGS.api_base_url
API_CALC_BASE_URL = SETTINGS.api_calc_base_url
DEFAULT_LANG = SETTINGS.default_lang
SEPAR_URL_RU = f"{BASE_URL_API}/getListData_Separ/{DEFAULT_LANG}"
async def _make_post_request_async(session, url, data=None, error="POST"):
    try:
        async with session.post(url, data=data, headers={'Content-Type': 'application/json'}) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"ОШИБКА: {error}: ClientError для {url}: {e}")
    except json.JSONDecodeError as e:
        print(f"ОШИБКА: {error}: JSONDecodeError для {url}: {e}")
    return None

def _make_get_request(url, error="GET"):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"ОШИБКА: {error}: HTTPError для {url}: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"ОШИБКА: {error}: ConnectionError для {url}: {e}")
    except requests.exceptions.Timeout as e:
        print(f"ОШИБКА: {error}: Timeout для {url}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"ОШИБКА: {error}: RequestException для {url}: {e}")
    except json.JSONDecodeError as e:
        print(f"ОШИБКА: {error}:JSONDecodeError для {url}: {e}")
    return None


async def get_data_separ(lang: str = DEFAULT_LANG):
    """Вход: язык. Выход: справочник данных по сепараторам из backend API."""
    data_separ = _make_get_request(
        f"{BASE_URL_API}/getListData_Separ/{lang}",
        error="get_data_separ"
    )
    return data_separ


async def create_new_cp(session, id_tg: str, key_cp: str = 'null'):
    new_kp = await _make_post_request_async(
        session,
        f"{BASE_URL_API}/Write_new_cp/offer/{id_tg}/{key_cp}",
        error="create_new_cp"
    )

    if not new_kp:
        return None, None, None

    data_CP = new_kp.get("data_CP")
    List_CP = new_kp.get("List_CP")
    key = new_kp.get("key")

    # запись созданного КП
    write_created_kp_data = json.dumps({"createKP": data_CP, "List": List_CP})
    await _make_post_request_async(
        session,
        f"{BASE_URL_API}/Write_createdKP/offer/{id_tg}",
        data=write_created_kp_data,
        error="create_new_cp"
    )

    return key, data_CP, List_CP


async def update_created_kp(session, user_id: str, form_data: dict):
    update_response = await _make_post_request_async(
        session,
        f"{BASE_URL_API}/Update_createdKP/{user_id}",
        data=json.dumps(form_data),
        error=f"update_created_kp"
    )
    return update_response

async def save_sieve_pdf(session, user_id: str, key: str, data_list: dict):
    pdf_response = await _make_post_request_async(
        session,
        f"{BASE_URL_API}/Sieve_SavePDF/{user_id}/{key}",
        data=json.dumps(data_list),
        error="save_sieve_pdf"
    )
    return pdf_response


async def post_Result_air(session, form_data: dict):
    update_response = await _make_post_request_async(
        session,
        f"{API_CALC_BASE_URL}/Result_air",
        data=json.dumps(form_data),
        error=f"Result_air"
    )
    return update_response


async def post_GetInfoSepar(session, form_data: dict):
    update_response = await _make_post_request_async(
        session,
        f"{API_CALC_BASE_URL}/GetInfoSepar/{DEFAULT_LANG}",
        data=json.dumps(form_data),
        error=f"GetInfoSepar"
    )
    return update_response

async def post_calculate_compressor(session, form_data: dict):
    update_response = await _make_post_request_async(
        session,
        f"{API_CALC_BASE_URL}/calculate_compressor/{DEFAULT_LANG}",
        data=json.dumps(form_data),
        error=f"calculate_compressor"
    )
    return update_response


# =========================
# Scenario 2: расчет по продукту и производительности
# =========================
async def calculate_separator_by_product_capacity(
    session,
    product: str,
    capacity_tph: float,
    purpose: str | None = None,
    extra: dict | None = None,
):
    """Заглушка для расчёта подбора фотосепаратора по продукту и производительности.

    ВАЖНО: сюда нужно вставить вызов ТВОЕГО API, которое возвращает структуру вида:
    { "0": { "El_choice": {...}, "Separators":[...], "dop_equipment": {...}, "group_info": {...} } }

    Args:
        session: aiohttp.ClientSession
        product: продукт (например, "Пшеница")
        capacity_tph: требуемая производительность в т/ч (например, 6.0)
        purpose: назначение (например, "Семена"). Если None — будет дефолт "Семена"
        extra: любые дополнительные параметры (опционально)

    Returns:
        dict | None: json-ответ твоего API (или None, если пока не подключено/ошибка)
    """
    data_CP = {
        'Sieve': {},
        'elevator' :{},
        'sep_machine': {},
        'compressor': {},
        'photo_sorter': {},
        'extra_equipment':{},
        'Service': {},
        'attendance': {},
        'Pneumatic_feed' :{}

    }

    purpose = (purpose or "Семена").strip()
    extra = extra or {}
    req = await get_data_separ()
    Separ_perf = req['Separ_perf']


    El_choice = next(
        (
            f for f in Separ_perf
            if f.get("product") == product
            and purpose in (f.get("purpose") or [])
        ),
        None
    )


    sor = El_choice['garbage_percentage']
    qual = El_choice['quality_percentage']
    performance = capacity_tph

    Count_tray = math.ceil(performance / El_choice["performance_tray_per_t_h"])

    DataList = {
        'sor': sor,
        'qual' : qual,
        'performance' : performance,
        'Count_tray'  : Count_tray ,
        'El_choice' : El_choice
    }
    Result_air = await post_Result_air(session, DataList)

    DataList = {
        'Product': product,
        'Purpose': purpose,
        'Count_tray': Count_tray,
        'performance': performance,
        'choice_sorter' :None
    }

    InfoSepar = await post_GetInfoSepar(session, DataList)

    for key, item in InfoSepar.items():
        Count_tray = item["loop_tray"]
        air_flow_per_tray =  Result_air['air_flow_per_tray']

        DataList = {
            'Count_tray': Count_tray,
            'Result_air': round(Count_tray * round(air_flow_per_tray, 1), 1),
            'air_flow_per_tray': air_flow_per_tray,
            'Product': product,
        }
        calculate_compressor = await post_calculate_compressor(session, DataList)
        # print(calculate_compressor['compressors'])

    InfoSepar['compressors'] = calculate_compressor['compressors']

    #     count_separ = item["count_separ"]


    #     Separators = [
    #         f for f in List_separ
    #         if f.get("tray") == Count_tray
    #         and f.get("configuration") == item["El_choice"]["sep_config"]
    #     ]
    #     List_modelSep = [
    #         f for f in List_separ
    #         if f.get("configuration") == El_choice['sep_config']
    #     ]
        
    #     for n, model in enumerate(List_modelSep):
    #         model_name = model.get("name_print")
    #         # if(Separators.filter(...).length !== 0)
    #         has = any(s.get("name_print") == model_name for s in Separators)
    #         if has:
    #             def update_values():
    #                 data_CP['photo_sorter'][model.get("id_row")] = count_separ
    #                 # Number(count_separ.toFixed(0)) -> int(round(count_separ))
                  

    #                 # group[model.get("id_row")] = int(round(count_separ))

    #             if product == "Кофе" and performance <= 0.8:
    #                 if "L" in (model.get("model_series") or ""):
    #                     update_values()
    #             else:
    #                 update_values()
    # print(data_CP)

    return InfoSepar


async def create_cp(session, ID_USER: str, data_CP=None, List_CP=None, key=None, lang: str = DEFAULT_LANG) -> bool:
    """Вход: сессия, ID пользователя и накопленные данные КП. Выход: True/False по результату сборки КП."""
    if not (key and data_CP and List_CP):
        key, data_CP, List_CP = await create_new_cp(session, ID_USER)

    data_CP.setdefault("additional_info", {})
    data_CP["additional_info"]["nds"] = "22"

    List_CP['payment_method'] = '100% предоплата'
    data_CP['sale'] = 0

    formData = {'createKP': data_CP, 'List': List_CP}

    update_response = await update_created_kp(session, ID_USER, formData)
    if not update_response:
        return False

    FIO_manager = 'Алиса'
    client='manager'
    DataList_pdf = {
        'sum': data_CP['price'],
        'date': List_CP['creation_date'],
        'FIO': FIO_manager,
        'client': client
    }

    await save_sieve_pdf(session, ID_USER, key, DataList_pdf)
    return True




