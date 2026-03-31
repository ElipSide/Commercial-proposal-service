from pydantic import BaseModel
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import os
import routers.CaseChange as CaseChange
import routers.dadata_search as dadata_search
import routers.ReadCheckHtml as ReadCheckHtml
from routers.push_message import TgSendMess
from routers.html_to_pdf import PDFConverter
from pathlib import Path

templates = Jinja2Templates(directory="Front/templates")

# Unprotected router
router = APIRouter(prefix="/offer")
TgSend = TgSendMess()
# ---------------------------------------
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
async def home(request: Request, tg_id: str = '', tocen: str = ''):
    from main import user_repository, tech_work
    access_user = await user_repository.get_user_by_telegram_id_access_level(tg_id)
    language_code = await user_repository.get_user_by_telegram_id_language_code(tg_id)
    pagename = "botSortingKP.html"
    if access_user == 'manager':
        pagename = 'botSortingKP_manager.html'
    if access_user == 'admin':
        pagename = 'botSortingKP.html'
        # botSortingKP_admin
    print(f'{language_code}/{pagename}')
    if tech_work and tg_id != '5232657726':
        return templates.TemplateResponse(
            request=request, name=f'404.html', context= {'last_updated':dir_last_updated(MYDIR)}
        )
    
    return templates.TemplateResponse(
        request=request, name=f'{language_code}/{pagename}', context={'last_updated': dir_last_updated(MYDIR)}
    )

@router.get("/PDF")
async def home(request: Request, tg_id :str = '', tocen :str = ''):
    pagename = "botSortingKP_PDF.html"
    return templates.TemplateResponse(
        request=request, name=pagename,context= {'last_updated':dir_last_updated(MYDIR)}
    )
@router.post("/Sieve_CaseChange")
async def Sieve_CaseChange(request: Request):
    data = await request.json()
    response = CaseChange.StartCase(data['text'])
    return response

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

@router.post("/Save_NewCounter")
async def Save_NewCounter(request: Request):
    from main import user_repository
    dataList = await request.json()
    await user_repository.insert_row('contractor', dataList)
    return True


# ------------------------------------- Счет Рыжухи----------------------------
@router.post("/CSort_GetCheck")
async def CSort_GetCheck(request: Request):
    # from main import user_repository
    dataList = await request.json()
    # try:
    result = dadata_search.dadata_bic(str(dataList['buyer']['bic']))
    if result['kpp'] != None: dataList['buyer']['kpp'] = result['kpp']
    result = dadata_search.dadata_inn(dataList['buyer']['inn'] )

    dataList['buyer']['address'] = ''
    if result['address']['unrestricted_value']!= None: dataList['buyer']['address']  = result['address']['unrestricted_value']
    dataList['buyer']['organization_shortname'] = result['name']['short_with_opf']

    # # params = ('contracts', data['buyer']['user_id'], str(data['id_provider']), data['key'])
    dataList['number'] = dataList['buyer']['user_id']
    filename = await ReadCheckHtml.main(dataList)
    # result = TgSend.agrement_PDFSend(
    #     {'text': f'Счет {data["NameFile"]} №{data["number"]}\nна сумму {data["sum"]} рублей',
    #      'chatID': data['Chat_id'], 'key': data["key"], 'path_file': filename})
    return f'https://csort-news.ru/off_bot/static/document/check/PDF/{filename.replace(" ", "%20", len(filename.split(" "))).split("PDF/")[1]}'
    # except:
    #     return 'Проверьте ИНН и БИК, и повторите попытку'


