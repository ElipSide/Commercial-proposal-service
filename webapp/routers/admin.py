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
router = APIRouter(prefix="/main_admin")
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

@router.get("/get_tables_name")
async def get_tables_name():
    from main import user_repository
    result = {key: [] for key in ['List_name_table', 'extra_equipment', 'column_translations']}
    result['List_name_table'] = [{"id_row": item[0], "name_table_db": item[1], "name_table": item[2], 'access_level': item[3]} for item in
                      await user_repository.get_all_name_tables()]
    
    req = await user_repository.get_data_choice_table('additional_parameters')
    result['additional_parameters'] = req['data']

    result['column_translations'] = dict([(item[1], item[2]) for item in await user_repository.get_column_translations()])
    

    return result
   
@router.get("/get_choice_table/{name_table}")
async def get_tables_name(name_table:str):
    from main import user_repository
    result = {key: [] for key in ['List_table' , 'Info_table']}
    req = await user_repository.get_data_choice_table(name_table)
    result['List_table'] = req['data']
    result['Info_table'] = req['columns']
    return result



@router.post("/Update_row")
async def Update_row(request: Request):
    from main import user_repository
    data = await request.json()
    table_name = data['table_name']
    row = data['row']
    key = data['key']
    for field in row:
        if isinstance(row[field], (list, dict)):
            row[field] = json.dumps(row[field])
    await user_repository.update_row(table_name, key, row)
    return True

@router.post("/Update_rows")
async def Update_rows(request: Request):
    from main import user_repository
    data = await request.json()
    print(data)
    table_name = data['table_name']
    row = data['row']
    key = data['key']
    await user_repository.update_rows(table_name, key, row)
    return True

@router.post("/Insert_row")
async def Insert_row(request: Request):
    from main import user_repository
    data = await request.json()
    table_name = data['table_name']
    row = data['row']
    for field in row:
        if isinstance(row[field], (list, dict)):
            row[field] = json.dumps(row[field])

    await  user_repository.insert_row(table_name, row)
    return row


@router.post("/Delete_row")
async def Delete_row(request: Request):
    from main import user_repository
    data = await request.json()
    table_name = data['table_name']
    id_row = data['id_row']
    key = data['key']
    await  user_repository.delete_row(table_name,key, id_row)
    return True

@router.post("/Delete_row_arr")
async def Delete_row(request: Request):
    from main import user_repository
    data = await request.json()
    table_name = data['table_name']
    id_row = data['id_row']
    key = data['key']
    await  user_repository.delete_row_arr(table_name,key, id_row)
    return True

@router.post("/SavePhoto/{name}")
async def create_upload_file(name: str, file: UploadFile):
    filepath = f"Front/static/img_machine/{name}.png"
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)
    return f'{name}.png'
