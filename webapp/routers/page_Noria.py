from pydantic import BaseModel
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
import os
import routers.CaseChange as CaseChange
import routers.dadata_search as dadata_search
import routers.ReadCheck as ReadCheck
import routers.ReadCheckHtml as ReadCheckHtml
import re
from routers.push_message import TgSendMess
from routers.html_to_pdf import PDFConverter
import json

templates = Jinja2Templates(directory="Front/templates")

# Unprotected router
router = APIRouter(prefix="/Noria")
TgSend = TgSendMess()

# ---------------------------------------
converter = PDFConverter()


class LoginRequest(BaseModel):
    telegram_id: int
    phone_number: str


MYDIR = 'Front/static/js'


def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

def remove_space(item):
    return ' '.join(item.split())

@router.get("/home")
async def home(request: Request, tg_id: str = '', tocen: str = ''):
    pagename = "ru/Noria.html"
    return templates.TemplateResponse(
        request=request, name=pagename, context={'last_updated': dir_last_updated(MYDIR)}
    )

# @router.get("/getListData")
# async def getListData_Calc():
#     from main import user_repository
#     result = {key: [] for key in ['Separ_perf', 'Compressor_perf', 'List_separ', 'List_compressor', 'List_equipment']}

#     result['Separ_perf'] = [
#         {"id_row": item[0], "product": item[1], "segment": item[2], "purpose": item[3],
#             "mass1000_per_gram": item[4], "garbage": item[5], "garbage_percentage": item[6], "quality_percentage": item[7],
#             "performance_tray_per_t_h": item[8], 'blow_per_m_sec': item[9], 'k_masses': item[10], 'pressure_per_bar': item[11],
#         'sep_config': item[12]} for item in await user_repository.get_perfom_config_photoseparators_info()]

#     result['Compressor_perf'] = [
#         {"id_row": item[0], "name": item[1], "produced_by": item[2], "id": item[3],
#          "min_perf": item[4], "max_perf": item[5]} for item in await user_repository.get_compressor_perfomance_info()]

#     result['List_separ'] = [
#         {"id_row": item[0], "bitrix_id": item[1], "id_erp": remove_space(item[2]), "name": item[3],
#          "name_print": item[4], "model_series": item[5], "configuration": item[6],
#          "id_provider": item[7], 'price': item[8], 'photo': item[9], 'height': item[10], 'width': item[11],
#          'depth': item[12], 'additional_parameters': item[13], 'additional_equipment': item[14], 'tray':item[15]} for item in
#         await user_repository.get_all_photo_separators_info()]
#     result['List_compressor'] = [{"id_row": item[0], "id_bitrix": item[1], "id_erp": item[2], "name": remove_space(item[3]),
#                              "name_print": item[4], "produced_by": item[5], "photo": item[6], "price": item[7],
#                              "addit_params": item[8], 'addit_equipment': item[9], 'height': item[10], 'width': item[11],
#                              'depth': item[12], "id_provider": item[13], } for item in
#                             await user_repository.get_all_compressors_info()]
#     result['List_equipment'] = [
#         {"id_bitrix": item[0], "id_erp": item[1], "name": item[2], "price": item[3], "photo": item[4],
#          "id_row": item[5], "id_provider": int(item[6]), "count_tray": item[9]} for item in
#         await user_repository.get_all_extra_equipment_info()]
    
#     result['sieve_size'] = [{"id_row": item[0], "size": item[1]} for item in await user_repository.get_all_sieve_size_info()]

#     return result

# @router.post("/Write_createdKP/{id}")
# async def Write_createdKP_Offer(request: Request, id: str):
#     from main import user_repository
#     data = await request.json()
#     List = data['List']

#     data['createKP']['group_info'] = json.dumps(data['createKP']['group_info'])
#     await user_repository.insert_row('struct_created_cp', data['createKP'])

#     access_user = await user_repository.select_row('user_info', 'access_level', {'id_tg' : id})
#     access_user = access_user[0][0]
#     if access_user != 'client':
#         List['manager_id_tg'] = id

#     await user_repository.insert_row('list_of_created_cp', List)
#     return List


# @router.post("/Update_createdKP/{key}")
# async def Update_createdKP_Calc(request: Request, key: str):
#     from main import user_repository
#     data = await request.json()

#     data['createKP']['group_info'] = json.dumps(data['createKP']['group_info'])
#     await user_repository.update_row('struct_created_cp', 'cp_key', data['createKP'])

#     await user_repository.update_row('list_of_created_cp', 'key_cp',data['List'])
#     return True