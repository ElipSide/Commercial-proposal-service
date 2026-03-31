from fastapi import APIRouter, Request,  HTTPException
from pathlib import Path
import math
from .models import CompressorRequest, CompressorPerformance, CompressorInfo
from ..push_message import TgSendMess
from typing import Dict,List

router = APIRouter(prefix="/API_CALC")
TgSend = TgSendMess()

MYDIR = 'Front/static/js'
UPLOAD_DIR = Path("Front/static/img_manager/files")
CONVERTED_DIR = Path("Front/static/img_manager/files")

def remove_space(item):
    return ' '.join(item.split())

@router.post("/Result_air")
async def calculate_air(request: Request):
    data = await request.json()
    tray_params = data['El_choice']
    
    # Основные расчеты
    qual_normalized = data['qual'] / 100
    count_sor_before = (1000000 / ((tray_params['mass1000_per_gram'] / tray_params['k_masses']) / 1000)) * (data['sor'] / 100)
    count_sor_after = (1000000 / ((tray_params['mass1000_per_gram'] / tray_params['k_masses']) / 1000)) * (1 - qual_normalized)
    count_shots_sec = ((count_sor_before - count_sor_after) * data['performance']) / 3600
    air_flow_per_tray = (((tray_params['blow_per_m_sec'] / 1000) * count_shots_sec) * 170 * tray_params['pressure_per_bar']) / 6
    
    Result_air = data['Count_tray'] * air_flow_per_tray
    
    return {
        "Result_air": round(Result_air, 1),
        "Count_tray": data['Count_tray'],
        "air_flow_per_tray": round(air_flow_per_tray, 2)
    }
        
    

@router.post("/GetInfoSepar/{lang}")
async def calculate_air(request: Request, lang: str):
    
    # Получаем и валидируем входные данные
    data = await request.json()
    product = data.get('Product')
    purpose = data.get('Purpose')
    count_tray = data.get('Count_tray')
    performance = data.get('performance')
    choice_sorter = data.get('choice_sorter')
    
    from main import user_repository
    List_separ = [
        {"id_row": item[0], "bitrix_id": item[1], "id_erp": remove_space(item[2]), "name": item[3],
         "name_print": item[4], "model_series": item[5], "configuration": item[6],
         "id_provider": item[7], 'price': item[8], 'photo': item[9], 'height': item[10], 'width': item[11],
         'depth': item[12], 'additional_parameters': item[13], 'additional_equipment': item[14], 'tray':item[15]} for item in
        await user_repository.get_all_photo_separators_info(lang)]

    Separ_perf = [
        {"id_row": item[0], "product": item[1], "segment": item[2], "purpose": item[3],
            "mass1000_per_gram": item[4], "garbage": item[5], "garbage_percentage": item[6], "quality_percentage": item[7],
            "performance_tray_per_t_h": item[8], 'blow_per_m_sec': item[9], 'k_masses': item[10], 'pressure_per_bar': item[11],
        'sep_config': item[12]} for item in await user_repository.get_perfom_config_photoseparators_info(lang)]
    List_equipment = [
        {"id_bitrix": item[0], "id_erp": item[1], "name": item[2], "price": item[3], "photo": item[4],
         "id_row": item[5], "id_provider": item[6], "count_tray": item[9]} for item in
        await user_repository.get_all_extra_equipment_info(lang)]
        
    El_choice = next((item for item in Separ_perf if item['product'] == product and purpose in item['purpose']),None)
   
    # Расчеты
    result = {}
    loop = 2 if count_tray >= 8 else 1
    dop_equipment = {
        "Бункер":[],
        "Аспирация":[],
        "Сходы":[],
        "Доп оборудование":[]
    }



    if choice_sorter==None:
        for n in range(loop):

            count_separ = math.floor(count_tray / 8) if count_tray >= 8 else 1
            if count_tray >= 8:
                loop_tray = 8
                count_tray -= 8 * count_separ
            else:
                loop_tray = count_tray % 8
            if loop_tray <=0: continue


            # loop_tray = 8 if count_tray >= 8 else count_tray % 8
            
            Separators = [
                sep for sep in List_separ 
                if sep['tray'] == loop_tray and sep['configuration'] == El_choice['sep_config']
            ]

         
            if performance:
                El_choice['calculated_performance'] = round(
                    El_choice['performance_tray_per_t_h'] * loop_tray, 1
                )

            equipment = ''
            equipment = await calculate_equipment(product, {'count': count_separ, 'tray_count':loop_tray, 'model_series': Separators[0]['model_series']}, List_separ, List_equipment, lang)
            result[n] = {
                "El_choice": El_choice,
                "count_separ": count_separ,
                "loop_tray": loop_tray,
                "Separators": Separators,
                "dop_equipment" :equipment['items'],
                'group_info': {
                    'extra_equipment': equipment['dop_equipment_group_info']
                }
            }
    else:

        for key in choice_sorter.keys():

            count_separ = choice_sorter[key]
            Separators = []
            Separators = [
                sep for sep in List_separ 
                if sep['id_row'] == int(key)
            ]
            loop_tray = Separators[0]['tray']
            if performance:
                El_choice['calculated_performance'] = round(
                    El_choice['performance_tray_per_t_h'] * loop_tray, 1
                )

            equipment = ''
            equipment = await calculate_equipment(product, {'count': count_separ, 'tray_count':loop_tray, 'model_series': Separators[0]['model_series']}, List_separ, List_equipment, lang)
            result[list(choice_sorter.keys()).index(key)] = {
                "El_choice": El_choice,
                "count_separ": count_separ,
                "loop_tray": loop_tray,
                "Separators": Separators,
                "dop_equipment" :equipment['items'],
                'group_info': {
                    'extra_equipment': equipment['dop_equipment_group_info']
                }
            }

    return result

async def calculate_equipment(product, photo_sorter, separators, equipment_list, lang):

    if lang == 'ru':
        type_order = {"Бункер": 0, "Сходы": 1, "Аспирация": 2, "Доп оборудование": 3}
    if lang == 'en':
        type_order = {"Hopper": 0, "Chutes": 1, "Aspiration": 2, "Additional equipment": 3}

    type_keys = list(type_order.keys())   # ← ВАЖНО: теперь индексация работает

    count = photo_sorter['count']
    tray_count = photo_sorter['tray_count']
    model_series = photo_sorter['model_series'].split('.')[0]

    equipment_data = []
    equipment_ids = {}

    # === 1. КОФЕ + 1 лоток ===
    if (product in ('Кофе', 'Coffee')) and int(tray_count) == 1:

        # ---- Бункеры ----
        bunkers = [e for e in equipment_list if e['id_row'] in (76, 78)]
        if bunkers:
            b = bunkers[0]
            equipment_data.append({
                "type": type_keys[0],
                "model": b['name'],
                "count": count,
                "sort_order": type_order[type_keys[0]]
            })
            equipment_ids[str(b['id_row'])] = count

        # ---- Сходы ----
        sbodies = [e for e in equipment_list if e['id_row'] in (23, 48)]
        if sbodies:
            s = sbodies[0]
            equipment_data.append({
                "type": type_keys[1],
                "model": s['name'],
                "count": count,
                "sort_order": type_order[type_keys[1]]
            })
            equipment_ids[str(s['id_row'])] = count

    # === 2. ВСЕ ДРУГИЕ СЛУЧАИ ===
    else:
        # ---- Бункеры ----
        if (product in ('Кофе', 'Coffee') and tray_count == 1):
            bunkers = [e for e in equipment_list if e['id_row'] == 20]
        else:
            bunkers = [
                e for e in equipment_list
                if ('Бункер' in e['name'] and str(e['count_tray']) == str(tray_count))
            ]

        if bunkers:
            b = bunkers[0]
            equipment_data.append({
                "type": type_keys[0],
                "model": b['name'],
                "count": count,
                "sort_order": type_order[type_keys[0]]
            })
            equipment_ids[str(b['id_row'])] = count

        # ---- Сходы ----
        if (product in ('Кофе', 'Coffee') and tray_count == 1):
            sbodies = [e for e in equipment_list if e['id_row'] == 23]
        else:
            sbodies = [
                e for e in equipment_list
                if ('Комплект сходов' in e['name'] and str(e['count_tray']) == str(model_series))
            ]

        if sbodies:
            s = sbodies[0]
            equipment_data.append({
                "type": type_keys[1],
                "model": s['name'],
                "count": count,
                "sort_order": type_order[type_keys[1]]
            })
            equipment_ids[str(s['id_row'])] = count

    # === 3. Аспирация (НЕ для кофе) ===
    if product not in ('Кофе', 'Coffee'):
        aspirators = [
            e for e in equipment_list
            if ('Комплект аспирации' in e['name'] and str(e['count_tray']) == str(model_series))
        ]
        if aspirators:
            a = aspirators[0]
            equipment_data.append({
                "type": type_keys[2],
                "model": a['name'],
                "count": count,
                "sort_order": type_order[type_keys[2]]
            })
            equipment_ids[str(a['id_row'])] = count

    # === 4. Доп.оборудование (только кофе) ===
    if product in ('Кофе', 'Coffee'):
        platforms = [e for e in equipment_list if e['id_row'] in (77, 79)]
        if platforms:
            p = platforms[0]
            equipment_data.append({
                "type": type_keys[3],
                "model": p['name'],
                "count": count,
                "sort_order": type_order[type_keys[3]]
            })
            equipment_ids[str(p['id_row'])] = 1

        pneumatic_feed = [e for e in equipment_list if e['id_row'] in (80, 81)]
        if pneumatic_feed:
            p = pneumatic_feed[0]
            equipment_data.append({
                "type": type_keys[3],
                "model": p['name'],
                "count": count,
                "sort_order": type_order[type_keys[3]]
            })
            equipment_ids[str(p['id_row'])] = 1
            


    # === СОРТИРОВКА ===
    equipment_data.sort(key=lambda x: x['sort_order'])

    return {
        "items": [
            {"type": e["type"], "model": e["model"], "count": e["count"]}
            for e in equipment_data
        ],
        "dop_equipment_group_info": equipment_ids
    }



def find_compressor(list_compressor, selected_perf):
    return next(
        filter(lambda c: int(c.id_row) == int(selected_perf.id_row), list_compressor),
        None
    )




async def calculate_compressor(
    req: CompressorRequest,
    compressor_perf: List[CompressorPerformance],
    list_compressor: List[CompressorInfo],
    List_equipment,
    lang
) -> Dict:

    # Оставляем в compressor_perf только те строки, чьи id_row есть в list_compressor
    available_ids = {int(c.id_row) for c in list_compressor}
    compressor_perf = list(
        filter(lambda p: int(p.id_row) in available_ids, compressor_perf)
    )

    if lang == 'ru':
        type_order = {"Бункер": 0, "Сходы": 1, "Аспирация": 2, "Доп оборудование": 3}
    if lang == 'en':
        type_order = {"Hopper": 0, "Chutes": 1, "Aspiration": 2, "Additional equipment": 3}

    type_keys = list(type_order.keys()) 

    # Расчет воздуха
    min_def_air = 0 if req.Product.lower() in ('кофе', 'coffee') else 670
    min_comp_air = min_def_air * req.Count_tray
    result_air = max(req.Result_air, min_comp_air)

    max_air = max(item.max_perf for item in compressor_perf)
    max_perf_min = min(item.max_perf for item in compressor_perf)

    loop = 2 if (result_air >= max_air and result_air % max_air < max_perf_min) else 1

    compressors = []
    remaining_air = result_air
    equipment_ids = {}
    equipment_data = []

    for _ in range(loop):

        if remaining_air <= 0:
            break

        if remaining_air >= max_air:
            count = math.floor(remaining_air / max_air)
            loop_air = max_air
            remaining_air -= max_air * count
        else:
            count = 1
            loop_air = remaining_air
            remaining_air = 0

        if loop == 2 and remaining_air > max_perf_min:
            count += 1
            loop_air = remaining_air
            remaining_air = 0

        # Подбор производительности
        selected_perf = next(
            (p for p in compressor_perf if p.min_perf < loop_air <= p.max_perf),
            None
        )

        if not selected_perf:
            selected_perf = next(
                (p for p in compressor_perf if p.min_perf >= loop_air),
                None
            )

        if not selected_perf:
            raise ValueError("Не удалось подобрать компрессор с требуемыми параметрами")

        # Формируем имя

        if selected_perf.produced_by == '':
            compressor_name = f"{selected_perf.name}"
        else:
            compressor_name = f"{selected_perf.produced_by} {selected_perf.name}"

        print(selected_perf )

        selected_compressor = find_compressor(list_compressor, selected_perf)
        print(selected_compressor)

        if not selected_compressor:
            raise ValueError(f"Компрессор {compressor_name} не найден в списке доступных")

        compressors.append({
            "compressor": selected_compressor,
            "performance": selected_perf,
            "count": count,
            "air_flow": loop_air
        })

        # ---- ДОП оборудование (id_row = 20 → platform id 22)
        if selected_compressor.id_row == 20:
            platform = next((p for p in List_equipment if p['id_row'] == 22))

            equipment_data.append({
                "type": type_keys[3],                 # ← исправлено
                "model": platform['name'],
                "count": count,
            })

            equipment_ids[str(platform['id_row'])] = count

    warning = None

    return {
        "compressors": compressors,
        "total_air_flow": result_air,
        "min_required_air": min_comp_air,
        "warning": warning,
        "equipment_data": equipment_data,
        "equipment_ids": equipment_ids
    }


@router.post("/calculate_compressor/{lang}")
async def api_calculate_compressor(request: Request, lang: str):
    data = await request.json()
    req = CompressorRequest(**data)
    # Получаем данные из репозитория
    from main import user_repository
    compressor_data = await user_repository.get_compressor_perfomance_info()
    compressor_perf = [CompressorPerformance(
        id_row=item[0], name=item[1], produced_by=item[2], 
        id=item[3], min_perf=item[4], max_perf=item[5]
    ) for item in compressor_data]
    compressor_perf_sorted = sorted(compressor_perf, key=lambda x: x.max_perf)

    list_compressor_data = await user_repository.get_all_compressors_info(lang)
    list_compressor = [CompressorInfo(
        id_row=item[0], id_bitrix=item[1], id_erp=item[2], 
        name=remove_space(item[3]), name_print=item[4],
        produced_by=item[5], photo=item[6], price=item[7],
        addit_params=item[8], addit_equipment=item[9],
        height=item[10], width=item[11], depth=item[12],
        id_provider=item[13]
    ) for item in list_compressor_data]
    
    List_equipment = [
                {"id_bitrix": item[0], "id_erp": item[1], "name": item[2], "price": item[3], "photo": item[4],
                "id_row": item[5], "id_provider": item[6], "count_tray": item[9]} for item in
                await user_repository.get_all_extra_equipment_info(lang)]
    # Выполняем расчет
    return await calculate_compressor(req, compressor_perf_sorted, list_compressor, List_equipment, lang)
    

