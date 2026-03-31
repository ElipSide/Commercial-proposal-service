from fastapi import APIRouter, Depends, Request, HTTPException
# from database.users import UserFunction
from routers.auth import LoginRequest
import sys
from datetime import datetime


# Dependency used for JWT validation
router = APIRouter(prefix="/api/bots")
# ClassUsFunc = UserFunction()

class RegisterRequest(LoginRequest):
    first_name: str
    username: str


# исправить
@router.post("/register")
async def register_user(request: Request):
    body = await request.json()
    print('register')
    print(body)
    from main import user_repository

    user = await user_repository.select_row(
        'user_info',
        '*',
        {'phone_number': str(body['phone_number'])}
    )

    print('user', user)
    if not user:
        data = {
        'id_tg': str(body['telegram_id']),  # id_tg
        'phone_number': str(body['phone_number']),  # phone_number
        "language": 'ru',  # language
        'access_level': "",
        "company": '',
        "data_reg": datetime.now().date(),  # data_reg (make sure this is in 'YYYY-MM-DD' format)
        'login': str(body['username']), # login
        'id_max':'',
        'login_max':''    
    }

        await user_repository.insert_row('user_info',data)
    else:
        data = {
            'phone_number': str(body['phone_number']),  # phone_number
            'id_tg':str(body['telegram_id']),
            'login':str(body['username'])
        }
        await user_repository.update_row('user_info', 'phone_number', data)


    password = "qwe"
    access_token = "qwe"
    refresh_token = "qwe"
    answer = True

    if not answer:
        raise HTTPException(status_code=409, detail="User already exists")
    return {"password": password, "access_token": access_token, "refresh_token": refresh_token, "status_code": 200}



@router.post("/getID_manag/{key}")
async def register_user(key: str):
    from main import user_repository
    id_manag = await user_repository.update_row('list_of_created_cp', 'user_id_tg', {'key_cp':key})
    return id_manag

# исправить
@router.get("/users/{telegram_id}")
async def get_user_by_telegram_id_handler(telegram_id: str):
    from main import user_repository
    user = await user_repository.select_row('user_info', '*', {'id_tg': telegram_id})
    print(user)
    if not user:
        return False
    access_user = await user_repository.select_row('user_info', 'access_level', {'id_tg': telegram_id})
    return access_user[0][0]


@router.get("/users_id")
async def get_user_by_telegram_id():
    from main import user_repository
    users = await user_repository.get_all_user_info()  # ClassUsFunc.get_users()
    return users

@router.get("/company_id")
async def get_company_id():
    from main import user_repository
    company = await user_repository.get_all_provider_list_info()
    return company

@router.get("/company_stat/{Company}")
async def get_company(Company: str):
    from main import user_repository
    week = await user_repository.find_rows_by_days_and_supplier(7, Company)
    month = await user_repository.find_rows_by_days_and_supplier(31, Company)
    return {'week': week, 'month': month}

@router.post("/users/write")
async def get_user_by_telegram_id_handler1(request: Request):
    List = await request.json()
    return List

@router.get("/reg_manger/{id_tg}")
async def register_user(id_tg: str):
    from main import user_repository

    ac_lvl = await user_repository.select_row('user_info', "id_tg, access_level", {'id_tg': id_tg})

    if len(ac_lvl[0][0]) == 0:
        await user_repository.insert_row('user_info', {"id_tg": id_tg, "surname": "-",
                                                       "name": "-", "middle_name": "-"})
    else:
        await user_repository.update_row('user_info', "id_tg",
                                         {"id_tg": id_tg, 'access_level': 'manager'})
@router.post("/create_link")
async def get_company(request: Request):
    from main import user_repository
    body = await request.json()
    body['id_tg'] = str(body['id_tg'])
    incl = await user_repository.select_row('transition_statistics', '*',
        {"id_tg": body['id_tg'], 'namelink':  body['namelink']})
    print(incl)
    if incl != []: return 403
    result = await user_repository.insert_row('transition_statistics', body)
    return {result}



@router.get("/get_AllLink/{id_tg}")
async def get_company(id_tg: str):
    from main import user_repository
    result = await user_repository.get_alllink_stat(id_tg)
    return result

@router.get("/shift_lock/{shift_lock}")
async def shift_lock(shift_lock: str):
    from main import user_repository
    print(shift_lock)
    shift_url = f'https://t.me/Csort_official_bot?start={shift_lock}'
    print(shift_url)
    incl = await user_repository.select_row('transition_statistics', '*',{"link": shift_url})
    print(incl)
    new_count = incl[0][4] + 1
    await user_repository.update_row('transition_statistics', "link",
                                         {"link": shift_url, 'count_users': new_count})
    return incl

