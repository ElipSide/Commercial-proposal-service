from typing import Any
import json

# --- помошники ---
def nds_prices(arr_price: int, discount: int, nds_now: int, count: int) -> tuple: 
    """возвращает цены для спец."""
    sum_price = arr_price * count
    discount_price = sum_price - (sum_price * (discount / 100))
    discount_sale = (discount / 100) * sum_price

    if nds_now:
        k = nds_now / (100 + nds_now)
        price_nds = float(arr_price) * k
        sum_price_nds = float(sum_price) * k
        discount_sum_nds = float(discount_price) * k
    else:
        price_nds, sum_price_nds, discount_sum_nds  = 0.0
    return price_nds,sum_price,sum_price_nds,discount_price,discount_sum_nds,discount_sale

def resolve_price(discount_price_List: dict, type_key:str, id_str: str, fallback_price: Any):
    """возвращаем цену из discount_price_List или fallback_price"""
    bucket = discount_price_List.get(type_key, {})
    raw = bucket.get(id_str, fallback_price)
    return float(raw) if raw else 0.0

def totals_zero() -> dict:
    return {k: 0.0 for k in ("sum", "discount_price","sum_nds","price_nds","discount_sum_nds","discount_total")}

def accumulate(totals: dict, values: tuple) -> None:
    price_nds, sum_price,sum_price_nds,discount_price,discount_sum_nds,discount_sale = values

    totals["sum"] += sum_price
    totals["discount_price"] += discount_price
    totals["sum_nds"] += sum_price_nds
    totals["price_nds"] += price_nds
    totals["discount_sum_nds"] += discount_sum_nds
    totals["discount_total"] += discount_sale

def format_totals(totals: dict, frt: str = ".1f") -> dict:
    return {
        "total_specification_sum": format(totals['sum'], frt),
        "total_specification_discount_price": format(totals['discount_price'], frt),
        "total_specification_sum_nds": format(totals['sum_nds'], frt),
        "total_specification_price_nds": format(totals['price_nds'], frt),
        "total_specification_discount_sum_nds": format(totals['discount_sum_nds'], frt),
        "total_med_discount": format(totals['discount_total'], frt),
    }

def effective_discount(check_sale_user: bool, sale_discount: float, sale_user: list[float], index: int) -> float:
    return sale_discount if check_sale_user else sale_user[index]

def photo_fn(item, url):
    photo = item.get("photo", "")
    if not photo or not photo.strip():
        return None
    return f"{url}/static/img_machine/{item['photo'].split()[0]}"
# --- общий движок спецификаций ---

MAPPING_TABLE_TYPE = {
    "photoMachine": "photo_sorter",
    "machine": "sep_machine",
    "kompressor": "compressor",
    "Sieve": "Sieve",
    "extra_equipment": "extra_equipment",
    "Service": "Service",
    "attendance": "attendance",
    "Elevator": "elevator",
    "laboratory_equipment": "laboratory_equipment",
}

async def get_specification(table_data: dict, id_row_user: list[str], count_user: list, sale_user: list[str], url: str, 
                        dop_info: list[dict], nds_now: str, sale_discount: float, table_key: str, discount_price_List: dict) -> dict:
    specification_dict = {}
    info_gabarit = {}
    totals = totals_zero()

    items = table_data[table_key]
    items_by_id = {str(item["id_row"]): item for item in items}
    check_sale_user = all(d==0 for d in sale_user)
    type_key = MAPPING_TABLE_TYPE.get(table_key, table_key)

    for i, id_row in enumerate(id_row_user):
        item = items_by_id.get(id_row)
        if item is None:
            continue

        count = int(count_user[i])
        discount = effective_discount(check_sale_user, sale_discount, sale_user, i)
        arr_price = int(resolve_price(discount_price_List, type_key, id_row, item.get("price") or 0))

        is_photo_separator = "Фотосепаратор" in (item.get("name_print") or "")
        photo_url = f"{url}/static/img_machine/{item['photo']}"

        info_gabarit[i] = {
            "height": item.get("height", ""),
            "width": item.get("width", ""),
            "depth": item.get("depth", ""),
            "desc_dop_info": item.get("description", ""),
            "photo": photo_url,
            "name": item.get("name", "") + " " + item["configuration"] if is_photo_separator else item["name"].lower(),
        }

        prices = nds_prices(arr_price, discount, nds_now, count)
        price_nds, sum_price, sum_price_nds, discount_price, discount_sum_nds, _ = prices
        accumulate(totals, prices)

        specification_name = (item["name"] + " " + item["configuration"]) if is_photo_separator else item['name']
        specification_dict[i] = {
            'specification_photo': photo_url,
            'specification_name': specification_name,
            'specification_count': count,
            'specification_price': arr_price,
            'specification_sum': sum_price,
            'specification_price_nds': price_nds,
            'specification_sum_nds': sum_price_nds,
            'specification_discount': discount,
            'specification_discount_price': discount_price,
            'specification_discount_sum_nds': discount_sum_nds
        }

        for info, gabarit in zip(dop_info, info_gabarit.values()):
            info.update(gabarit)

        return {"specification_dict": specification_dict, **format_totals(totals)}

# --- обертки для разных типов оборуд ---
async def getPhotoMachine(table_data, id_row_user, count_user, sale_user, url, dop_info, nds_now, sale_discount, discount_price_List):
    return await get_specification(table_data, id_row_user, count_user, sale_user, url, dop_info, nds_now, sale_discount, 'photoMachine', discount_price_List)

async def getMachine(table_data, id_row_user, count_user, sale_user, url, dop_info, nds_now, sale_discount, discount_price_List):
    return await get_specification(table_data, id_row_user, count_user, sale_user, url, dop_info, nds_now, sale_discount, 'machine', discount_price_List)

async def getKompressor(table_data, id_row_user, count_user, sale_user, url, dop_info, nds_now, sale_discount, discount_price_List):
    return await get_specification(table_data, id_row_user, count_user, sale_user, url, dop_info, nds_now, sale_discount, 'kompressor', discount_price_List)

async def getLaboratory(table_data, id_row_user, count_user, sale_user, url, dop_info, nds_now, sale_discount, discount_price_List):
    return await get_specification(table_data, id_row_user, count_user, sale_user, url, dop_info, nds_now, sale_discount, 'laboratory_equipment', discount_price_List)

# --- движок для списков (Sieve / Extra / Service / Attendance) ---
async def get_flat_specification(items: list[str], id_row_user: list[str], count_user: list, sale_user: list[float],  url: str,
    nds_now: float, sale_discount: float, type_key: str, discount_price_List: dict, *, name_fn, photo_fn, price_field: str = "price",
    fmt: str = ".2f",) -> dict:

    specification_dict = {}
    totals = totals_zero()
    check_sale_user = all(d==0 for d in sale_user)

    for n, item in enumerate(items):
        id_str = str(item.get("id_row") or item.get("id"))
        if id_str not in id_row_user:
            continue
        
        index = id_row_user.index(id_str)
        count = int(count_user[index])
        discount = effective_discount(check_sale_user, sale_discount, sale_user, index)
        arr_price = int(resolve_price(discount_price_List, type_key, id_str, item.get(price_field) or 0))
        
        prices = nds_prices(arr_price, discount, nds_now, count)
        price_nds, sum_price, sum_price_nds, discount_price, discount_sum_nds, _ = prices
        accumulate(totals, prices)

        specification_dict[n] = {
            "specification_name": name_fn(item),
            "specification_count": count,
            "specification_price": arr_price,
            "specification_sum": sum_price,
            "specification_price_nds": price_nds,
            "specification_sum_nds": sum_price_nds,
            "specification_discount": discount,
            "specification_discount_price": discount_price,
            "specification_discount_sum_nds": discount_sum_nds,
            "specification_photo": photo_fn(item, url),
        }

    return {"specification_dict": specification_dict, **format_totals(totals, fmt)}

async def getSieve(table_data, id_row_user, count_user, sale_user, nds_now, sale_discount, discount_price_List, url):
    def name_fn(item):
        return f"решето {str(item['Type']).lower()} {item['Count']}"

    return await get_flat_specification(
        table_data["ids"], id_row_user, count_user, sale_user, url,
        nds_now, sale_discount, "Sieve", discount_price_List,
        name_fn=name_fn, photo_fn=None, price_field="price",
    )

async def getExtra_equipment(table_data, id_row_user, count_user, sale_user, nds_now, sale_discount, discount_price_List, url):
    return await get_flat_specification(
        table_data["extra_equipment"], id_row_user, count_user, sale_user, url,
        nds_now, sale_discount, "extra_equipment", discount_price_List,
        name_fn=lambda item: item["name"], photo_fn=photo_fn,
    )

async def getService(table_data, id_row_user, count_user, sale_user, nds_now, sale_discount, discount_price_List, url):
    return await get_flat_specification(
        table_data["Service"], id_row_user, count_user, sale_user, url,
        nds_now, sale_discount, "Service", discount_price_List,
        name_fn=lambda item: item["name"], photo_fn=photo_fn,
    )

async def getAttendance(table_data, id_row_user, count_user, sale_user, nds_now, sale_discount, discount_price_List, url):
    return await get_flat_specification(
        table_data["attendance"], id_row_user, count_user, sale_user, url,
        nds_now, sale_discount, "attendance", discount_price_List,
        name_fn=lambda item: item["name"], photo_fn=None,
    )

# --- Нори ---
async def getElevator(
    table_data: dict,
    id_row_user: list[str],
    count_user: list,
    sale_user: list[float],
    nds_now: float,
    additional_info: dict,
    sale_discount: float,
    discount_price_List: dict,
    url: str,
) -> dict:
    specification_dict: dict = {}
    totals = totals_zero()

    elevators: list[dict] = table_data["Elevator"]
    check_sale_user = all(d == 0 for d in sale_user)
    type_key = "elevator"

    json_prices: dict[str, str] = additional_info.get("id_json", {}) 

    for n, item in enumerate(elevators):
        id_str = str(item["id_row"])
        if id_str not in id_row_user:
            continue

        index = id_row_user.index(id_str)
        count = int(count_user[index])
        discount = effective_discount(check_sale_user, sale_discount, sale_user, index)

        if id_str in json_prices:
            json_path = f"./Front/static/document/deal_elevator/{json_prices[id_str]}.json"
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            arr_price = float(data["modelPrice"]) * float(data["NDS"])
        else:
            arr_price = resolve_price(discount_price_List, type_key, id_str, item.get("price") or 0)

        prices = nds_prices(arr_price, discount, nds_now, count)
        price_nds, sum_price, sum_price_nds, discount_price, discount_sum_nds, _ = prices
        accumulate(totals, prices)

        photo_url = f"{url}/static/img_machine/{item['model'].split()[0]}"
        specification_dict[n] = {
            "specification_name": item["name_print"],
            "specification_count": count,
            "specification_price": format(arr_price, ".1f"),
            "specification_sum": format(sum_price, ".1f"),
            "specification_price_nds": format(price_nds, ".1f"),
            "specification_sum_nds": format(sum_price_nds, ".1f"),
            "specification_discount": format(discount, ".1f"),
            "specification_discount_price": format(discount_price, ".1f"),
            "specification_discount_sum_nds": format(discount_sum_nds, ".1f"),
            "specification_photo": photo_url,
        }

    return {
        "specification_dict": specification_dict,
        "total_specification_sum": int(totals["sum"]),
        "total_specification_discount_price": int(totals["discount_price"]),
        "total_specification_sum_nds": int(totals["sum_nds"]),
        "total_specification_price_nds": int(totals["price_nds"]),
        "total_specification_discount_sum_nds": int(totals["discount_sum_nds"]),
        "total_med_discount": int(totals["discount_total"]),
    }
