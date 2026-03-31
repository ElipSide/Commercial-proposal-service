from pydantic import BaseModel
from fastapi import APIRouter, Request , UploadFile, File, Depends
from fastapi.templating import Jinja2Templates
import os
import routers.CaseChange as CaseChange
import routers.dadata_search as dadata_search
import routers.ReadCheck as ReadCheck
import routers.ReadCheckHtml as ReadCheckHtml
import aiohttp
import re
from routers.push_message import TgSendMess
from routers.html_to_pdf import PDFConverter

import json
from pathlib import Path
from PIL import Image
import shutil
from docx import Document
from routers.company_information import DocumentParser
from psycopg import IntegrityError

templates = Jinja2Templates(directory="Front/templates")

router = APIRouter(prefix="/Service")
TgSend = TgSendMess()



#---------------------------------------
converter = PDFConverter()

class LoginRequest(BaseModel):
    telegram_id: int
    phone_number: str
MYDIR = 'Front/static/js'
UPLOAD_DIR = Path("Front/static/img_manager/files")
CONVERTED_DIR = Path("Front/static/img_manager/files")

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

@router.get("/home")
async def home(request: Request, tg_id :str = '', tocen :str = ''):
    from main import user_repository, tech_work
    
    access_user = await user_repository.get_user_by_telegram_id_access_level(tg_id)
    language_code = await user_repository.get_user_by_telegram_id_language_code(tg_id)

    pagename = "officialService.html"
    if access_user =='manager':
        pagename = 'officialService_manager.html'

    if tech_work and tg_id != '5232657726':
        return templates.TemplateResponse(
            request=request, name=f'404.html', context= {'last_updated':dir_last_updated(MYDIR)}
        )
    
    return templates.TemplateResponse(
        request=request, name=f'{language_code}/{pagename}',context= {'last_updated':dir_last_updated(MYDIR)}
    )

@router.get("/PDF")
async def home(request: Request, tg_id :str = '', tocen :str = ''):
    pagename = "botSortingKP_PDF.html"
    return templates.TemplateResponse(
        request=request, name=pagename,context= {'last_updated':dir_last_updated(MYDIR)}
    )


@router.get("/UserInfo_Key/{key}")
async def UserInfo_Key_offer(key: str):
    from main import user_repository
    id_user =  await user_repository.select_row('list_of_created_cp', "user_id_tg", {"key_cp": key})
    result = {'user': []}
    result['user'] = [
        {"id_tg": item[0], "surname": item[1], "name": (item[2]), "middle_name": item[3], "phone_number": item[4],
         "mail": item[5], "language": item[6], "data_reg": item[7],
         "access_level": item[8], "photo": item[9], "company": item[10], "login": item[11], "description": item[12],
         "id_erp": item[13], "job_title": item[14]} for item in await user_repository.select_row('user_info',"*",{'id_tg':id_user[0][0]})]
    return result


@router.post("/Sieve_CaseChange")
async def Sieve_CaseChange(request: Request):
    data =  await request.json()
    response = CaseChange.StartCase(data['text'])
    return response

@router.post("/Save_NewCounter")
async def Save_NewCounter(request: Request):
    from main import user_repository
    dataList =  await request.json()
    await user_repository.insert_row('contractor', dataList)
    return True




async def send_request(id_user, key):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://localhost:7676/screenshot?id_user={id_user}&key={key}') as response:
            if response.status == 200:
                result = await response.text()
            else:
                print(f"ERRR: {response.status} - {await response.text()}")

