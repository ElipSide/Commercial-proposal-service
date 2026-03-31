# uvicorn main:app --reload
from fastapi import FastAPI, Request, Depends, HTTPException, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from fastapi.staticfiles import StaticFiles
import os
import hashlib
from fastapi_login.exceptions import InvalidCredentialsException
from routers import auth, users, page_CalcSorting, page_CalcKP, page_Service, page_Separator, page_Noria, admin
from routers.API import page_API, calc_sorting
from db.db_ext import Database
from db.db_ext_func import UserRepository
from passlib.hash import bcrypt

app = FastAPI(root_path="/off_bot", redirect_slashes=False)
favicon_path = 'favicon.ico'

# --- Настройка менеджера аутентификации ---
SECRET_KEY = "your-secret-key-here-change-it"  # Замени на реальный секрет!
manager = LoginManager(SECRET_KEY, token_url="/off_bot/login", use_cookie=True)
manager.cookie_name = "auth_token"

conninfo = "dbname=webapp_fastapi user=sammy password=PkMeuygrpcrZWK!ccIO85^n^LOnpc( host=v2210764.hosted-by-vdsina.ru port=5432"
db_off = Database(conninfo)
user_repository = None
global tech_work
tech_work = False

templates = Jinja2Templates(directory="Front/templates")
MYDIR = 'Front/static/js'

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

# --- CORS ---
origins = [
    "https://localhost.tiangolo.com",
    "https://localhost",
    "https://localhost:8080",
    "http://109.202.10.224",
    "https://109.202.10.224"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Упрощаем для разработки
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
        return False
    
# --- Обработка входа ---
@app.post("/login")
async def login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...)
):
    user = await load_user(login)  # возвращает dict с 'login' и 'password_hash'
    if user and verify_password(password, user['password_hash']):
        response = RedirectResponse(url="/off_bot/admin", status_code=303)
        manager.set_cookie(response, manager.create_access_token(data={"sub": login}))
        return response
    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": "Неверный логин или пароль"},
        status_code=401
    )
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Используем напрямую bcrypt вместо passlib
        import bcrypt
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


async def require_admin(request: Request):
    token = request.cookies.get(manager.cookie_name)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/off_bot/login"}
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
            headers={"Location": "/off_bot/login"}
        )

# --- Защита /admin ---
@app.get("/admin")
async def admin_index(
    request: Request,
    user = Depends(require_admin)
):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={'last_updated': dir_last_updated(MYDIR)}
    )
# --- Выход ---
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/off_bot/login")
    response.delete_cookie("auth_token")
    return response

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

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