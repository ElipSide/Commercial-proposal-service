# uvicorn main:app --reload
import hashlib
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from passlib.hash import bcrypt

from db.db_ext import Database
from db.db_ext_func import UserRepository
from routers import (
    admin,
    auth,
    page_CalcKP,
    page_CalcSorting,
    page_Noria,
    page_Separator,
    page_Service,
    users,
)
from routers.API import calc_sorting, page_API


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _get_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise RuntimeError(f"Environment variable '{name}' is required")
    return value or ""


APP_ROOT_PATH = "/off_bot"
 
# Чувствительные значения оставляем в .env
DB_NAME = _get_env("DB_NAME", "")
DB_USER = _get_env("DB_USER", "")
DB_PASSWORD = _get_env("DB_PASSWORD", "")
DB_HOST = _get_env("DB_HOST", "")
DB_PORT = _get_env("DB_PORT", "")


conninfo = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

app = FastAPI(root_path=APP_ROOT_PATH, redirect_slashes=False)
manager = LoginManager("change-me-super-secret-key", token_url="/off_bot/login", use_cookie=True)
manager.cookie_name = "auth_token"

db_off = Database(conninfo)
user_repository = None
global tech_work
tech_work = False

templates = Jinja2Templates(directory="Front/templates")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Хэширование пароля ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# --- Получение пользователя из БД ---
@manager.user_loader()
async def load_user(login: str):
    query = "SELECT login, password_hash FROM admin_user WHERE login = %s"
    row = await db_off.fetchrow(query, login)
    return {"login": row[0], "password_hash": row[1]} if row else None


# --- Статика ---
app.mount("/static", StaticFiles(directory="Front/static"), name="static")
app.mount("/img", StaticFiles(directory="Front/static/img"), name="img")


@app.get("/")
async def index():
    return "Hello, World enemy!"


# --- Страница входа ---
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})



def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.verify(plain_password, hashed_password)
    except Exception:
        try:
            import bcrypt as raw_bcrypt
            return raw_bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception as e:
            print(f"Password verification error: {e}")
            return False


# --- Обработка входа ---
@app.post("/login")
async def login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...)
):
    user = await load_user(login)
    if user and verify_password(password, user["password_hash"]):
        response = RedirectResponse(url=f"{APP_ROOT_PATH}/admin", status_code=303)
        manager.set_cookie(response, manager.create_access_token(data={"sub": login}))
        return response
    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": "Неверный логин или пароль"},
        status_code=401
    )


async def require_admin(request: Request):
    token = request.cookies.get(manager.cookie_name)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": f"{APP_ROOT_PATH}/login"}
        )

    try:
        user = await manager.get_current_user(token)
        if not user:
            raise InvalidCredentialsException
        return user
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": f"{APP_ROOT_PATH}/login"}
        )


# --- Защита /admin ---
@app.get("/admin")
async def admin_index(
    request: Request,
    user=Depends(require_admin)
):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"last_updated": dir_last_updated("Front/static/js")}
    )


# --- Выход ---
@app.get("/logout")
async def logout():
    response = RedirectResponse(url=f"{APP_ROOT_PATH}/login")
    response.delete_cookie("auth_token")
    return response



def dir_last_updated(folder):
    return str(max(
        os.path.getmtime(os.path.join(root_path, f))
        for root_path, dirs, files in os.walk(folder)
        for f in files
    ))


# --- Startup / Shutdown ---
@app.on_event("startup")
async def startup():
    await db_off.open()
    global user_repository
    user_repository = UserRepository(db_off)


@app.on_event("shutdown")
async def shutdown():
    await db_off.close()


# --- Подключение роутеров ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(page_CalcSorting.router)
app.include_router(page_CalcKP.router)
app.include_router(page_Service.router)
app.include_router(page_Separator.router)
app.include_router(page_Noria.router)
app.include_router(page_API.router)
app.include_router(calc_sorting.router)
app.include_router(admin.router)
