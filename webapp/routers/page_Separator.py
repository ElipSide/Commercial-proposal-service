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
router = APIRouter(prefix="/Separator")
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
    from main import user_repository, tech_work
    language_code = await user_repository.get_user_by_telegram_id_language_code(tg_id)
    pagename = "Separator.html"
    if tech_work and tg_id != '5232657726':
        return templates.TemplateResponse(
            request=request, name=f'404.html', context= {'last_updated':dir_last_updated(MYDIR)}
        )
    return templates.TemplateResponse(
        request=request, name=f'{language_code}/{pagename}', context={'last_updated': dir_last_updated(MYDIR)}
    )
