from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, Request, Form
from fastapi.templating import Jinja2Templates
import os
import base64
import requests

import json
templates = Jinja2Templates(directory="Front/templates")
MYDIR = 'Front/static/js'
# Unprotected router
router = APIRouter(prefix="/Sorting")
class LoginRequest(BaseModel):
    telegram_id: int
    phone_number: str

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

@router.get("/home")
async def home(request: Request, tg_id :str = '', tocen :str = ''):
    from main import user_repository, tech_work
    language_code = await user_repository.get_user_by_telegram_id_language_code(tg_id)

    pagename = "botSorting.html"
    if tech_work and tg_id != '5232657726':
        return templates.TemplateResponse(
            request=request, name=f'404.html', context= {'last_updated':dir_last_updated(MYDIR)}
        )
    return templates.TemplateResponse(
        request=request, name=f'{language_code}/{pagename}', context= {'last_updated':dir_last_updated(MYDIR)}
    )

def remove_space(item):
    return     ' '.join(item.split())


@router.post("/Sieve_PostPhoto/{id_tg}/{key}") 
async def Sieve_PostPhoto(id_tg:str,key:str, request: Request): 
    contents = await request.json()
    print(contents)
    el = contents['response'][0]
    image_path = f'Front/static/img_sieve/{key}/'
    from main import user_repository
    len_photo = len(el.keys()) - 3
    for i in range(len_photo):
        image_file = base64.b64decode(el[f'photo_{i}'])
        with open(f'{image_path}{key}_photo_{i}.png', "wb") as fh:
            fh.write(image_file)
    data = {
        'key': key,
        'id_tg': id_tg,
        'data_json': el['data_json'],
        'len_photo':len_photo,
        'product': el['product']
    }
    await user_repository.insert_data(data)
    return {"response": 'good'}

