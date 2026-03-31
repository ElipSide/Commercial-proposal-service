from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Form
from pathlib import Path
import re
import os
import requests
import random
import string
from datetime import datetime, timedelta
from .models import DataCP, ListCP, GroupInfo, WriteKPRequest, CheckInfoRequest
import json
from ..push_message import TgSendMess
from psycopg import IntegrityError
import shutil
from ..company_information import DocumentParser
from PIL import Image
from docx import Document
import routers.dadata_search as dadata_search
import routers.ReadCheck as ReadCheck
import routers.ReadCheckHtml as ReadCheckHtml
import base64
from ..create_pdf_kp import createKpPdf
router = APIRouter(prefix="/API")
TgSend = TgSendMess()
create_kp = createKpPdf()

MYDIR = 'Front/static/js'
UPLOAD_DIR = Path("Front/static/img_manager/files")
CONVERTED_DIR = Path("Front/static/img_manager/files")

def remove_space(item):
    return ' '.join(item.split())


@router.get("/getListData/{lang}")
async def getList_Offer(lang: str):

    from main import user_repository
    result = {key: [] for key in ['prod', 'index', 'ids', 'machine', 'kompressor', 'photoMachine','Service', 'extra_equipment', 
        'group_names', 'attendance', 'Elevator', 'Pneumatic_feed', 'laboratory_equipment']}
    
    result['prod'] = [{"Prod": remove_space(item[0]), "type_letter": item[1], "type_clear": remove_space(item[2]),
                        "type_sieve": remove_space(item[3]), "min": item[4], "max": item[5], "Count": item[6],
                        "form": remove_space(item[7]), "id_provider": item[8]} for item in
                        await user_repository.get_all_calc_sieve_info(lang)]

    result['index'] = [{"prod": remove_space(item[0]), "Count": item[1], "id_provider": item[2]} for item in
                       await user_repository.get_all_calc_sieve_index_info(lang)]

    result['ids'] = [{"id": item[0], "id_bitrix": item[1], "Type": item[2], "Count": item[3], "price": item[4],
                    "id_provider": item[5], "id_erp": item[6], 'sieve_size': item[7], 'remainder': item[8]} for item in 
                    await user_repository.get_all_sieve_table_info(lang)]

    result['machine'] = [
        {"id_provider": item[0], "id_bitrix": item[1], "name": remove_space(item[2]), "name_print": item[3],
         "photo": item[4], "addit_params": item[5], "addit_equipment": item[6],
         "id_row": item[7], 'price': item[8], 'height': item[9], 'width': item[10], 'depth': item[11],
         'id_erp': item[12], 'sieve_position': item[13], 'sieve_size': item[14], 'description': item[15]} for item in 
         await user_repository.get_all_separat_table_info(lang)]

    result['photoMachine'] = [
        {"id_row": item[0], "bitrix_id": item[1], "id_erp": remove_space(item[2]), "name": item[3],
         "name_print": item[4], "model_series": item[5], "configuration": item[6],
         "id_provider": item[7], 'price': item[8], 'photo': item[9], 'height': item[10], 'width': item[11],
         'depth': item[12], 'description': item[16]} for item in
        await user_repository.get_all_photo_separators_info(lang)]

    result['kompressor'] = [{"id_row": item[0], "id_bitrix": item[1], "id_erp": item[2], "name": remove_space(item[3]),
        "name_print": item[4], "produced_by": item[5], "photo": item[6], "price": item[7],
        "addit_params": item[8], 'addit_equipment': item[9], 'height': item[10], 'width': item[11],
        'depth': item[12], "id_provider": item[13], "id_row2": item[14], 'description': item[15]} for item in
        await user_repository.get_all_compressors_info(lang)]
    
    result['Service'] = [{"id_row": item[0], "id_bitrix": item[1], "id_erp": item[2],"name": item[3], "nomenclature": item[4], "photo": item[5], "stock_balance": item[6],
            "price": item[7], "additional_parameters": item[8], "id_provider": item[9], "groups": item[10], "compatibility": item[11]} for item in await user_repository.get_all_service_info(lang)]
            
    result['attendance'] = [{"id_row": item[0], "id_bitrix": item[1], "id_erp": item[2],"name": item[3], "name_print": item[4], 
        "price": item[5]} for item in 
        await user_repository.get_all_attendance_info(lang)]

    result['extra_equipment'] = [
        {"id_bitrix": item[0], "id_erp": item[1], "name": item[2], "price": item[3], "photo": item[4],
         "id_row": item[5], "id_provider": item[6], 'tray': item[9]} for item in
        await user_repository.get_all_extra_equipment_info(lang)]
    
    result['Pneumatic_feed'] = [
        {"id_bitrix": item[0], "id_erp": item[1], "name": item[2], "price": item[3], "photo": item[4],
         "id_row": item[5], "id_provider": item[6],'height': item[7], 'width': item[10], 'depth': item[8], "name_print": item[11] } for item in
        await user_repository.get_all_pneumatic_feed(lang)]
    
    result['group_names'] = [{"id": item[0], "name": item[1]} for item in 
        await user_repository.get_all_group_names_info(lang)]

    result['Elevator'] = [{"id_row": item[0], "bitrix_id": item[1], "id_erp": item[2], "name": item[3],
         "name_print": item[4], "model": item[5],  "id_provider": item[6], 'price': item[7], 'photo': item[8],'height': item[11]} for item in await user_repository.get_all_elevator_info(lang)]
   
    result['sieve_size'] = [{"id_row": item[0], "size": item[1]} for item in 
        await user_repository.get_all_sieve_size_info()]

    result['laboratory_equipment'] = [{"id_row": item[7], "name": item[0], "name_print": item[1], "equipment_price": item[2], 
        "cost_price": item[3], "price": item[4], "markup": item[5], "equipment": item[6], "id_provider": item[8], "bitrix_id": item[9], 
        "id_erp": item[10],'photo':item[11]} for item in 
        await user_repository.get_all_laboratory_equipment_info(lang)]



    return result


@router.get("/getUserInfo/{id}")
async def getUserInfo_offer(id: str):

    from main import user_repository
    result = {key: [] for key in ['user', 'check_info']}
    result['user'] = [
        {"id_tg": item[0], "surname": item[1], "name": (item[2]), "middle_name": item[3], "phone_number": item[4],
         "mail": item[5], "language": item[6], "data_reg": item[7],
         "access_level": item[8], "photo": item[9], "company": item[10], "login": item[11], "description": item[12],
         "id_erp": item[13], "job_title": item[14]} for item in await user_repository.select_row('user_info', "*", {'id_tg' : id})]
    checkInfo = await user_repository.select_row('user_list', "*", {'id_tg' : id})
    if checkInfo == []:
        result['check_info'] = None
    else:
        result['check_info'] = [
            {"id_tg": item[0], "analysis_link": item[1], "analytics_photo": item[2], "pdf_kp": item[3],
             "agreement_kp": item[4], "invoice_kp": item[5], "organization": item[6],
             "inn": item[7], "address": item[8], "phone_number": item[9], "email": item[10], "bic": item[11],
             "checking_account": item[12], "first_name": item[13], "second_name": item[14],
             "surname": item[15], "position_user": item[16], "acts_basis": item[17], "number_proxy": item[18],
             "contract_ready": item[19], "agreement_signed": item[20], 'invoice_sent': item[21],
             "lastmanager_invoice": item[22], "height": item[23], "city": item[24], "organization_shortname": item[25],
             "organization_fullname": item[26], "ogrn": item[27],
             "kpp": item[28], "bank_info": item[29], "corporate_account": item[30]} for item in checkInfo]
        

    return result

@router.get("/getKPInfo/{key_Cp}")
async def getKPInfo_Offer(key_Cp: str):
    from main import user_repository
    result = {key: [] for key in ['List', 'createKP', 'changed_price_List', 'changed_sale_List']}
    result['createKP'] = [
        {"cp_key": item[0], "price": item[1], "group_info": (item[2]), "pdf_send": (item[3]), "id_send_mess": item[4],
         "id_send_check": item[5], 'sale':item[6], 'additional_info':item[7] } for item in await user_repository.select_row('struct_created_cp', '*', {'cp_key':key_Cp})]

    result['List'] = [{"user_id_tg": item[1], "key_cp": item[2], "short_title": (item[3]), "creation_date": item[4],
                       "currency": item[5], "payment_method": item[6], "delivery_term": item[7],
                       "warranty": item[8], 'manager_id_tg': item[9]} for item in await user_repository.select_row('list_of_created_cp', '*', {'key_cp':key_Cp})]
    
    async def fetch_and_format_list(table_name, key_Cp):
        data_list = await user_repository.select_row(table_name, "*", {'cp_key': key_Cp})
        return None if not data_list else [{"List": item[1]} for item in data_list]
    
    result['changed_price_List'] = await fetch_and_format_list('change_price_cp', key_Cp)
    result['changed_sale_List'] = await fetch_and_format_list('change_sale_cp', key_Cp)
    return result



@router.get("/getListData_Separ/{lang}")
async def getListData_Calc(lang: str):
    from main import user_repository
    result = {key: [] for key in ['Separ_perf', 'Compressor_perf', 'List_separ', 'List_compressor', 'List_equipment', 'List_gost']}

    result['Separ_perf'] = [
        {"id_row": item[0], "product": item[1], "segment": item[2], "purpose": item[3],
            "mass1000_per_gram": item[4], "garbage": item[5], "garbage_percentage": item[6], "quality_percentage": item[7],
            "performance_tray_per_t_h": item[8], 'blow_per_m_sec': item[9], 'k_masses': item[10], 'pressure_per_bar': item[11],
        'sep_config': item[12]} for item in await user_repository.get_perfom_config_photoseparators_info(lang)]

    result['Compressor_perf'] = [
        {"id_row": item[0], "name": item[1], "produced_by": item[2], "id": item[3],
         "min_perf": item[4], "max_perf": item[5]} for item in await user_repository.get_compressor_perfomance_info()]

    result['List_separ'] = [
        {"id_row": item[0], "bitrix_id": item[1], "id_erp": remove_space(item[2]), "name": item[3],
         "name_print": item[4], "model_series": item[5], "configuration": item[6],
         "id_provider": item[7], 'price': item[8], 'photo': item[9], 'height': item[10], 'width': item[11],
         'depth': item[12], 'additional_parameters': item[13], 'additional_equipment': item[14], 'tray':item[15]} for item in
        await user_repository.get_all_photo_separators_info(lang)]
    result['List_compressor'] = [{"id_row": item[0], "id_bitrix": item[1], "id_erp": item[2], "name": remove_space(item[3]),
                             "name_print": item[4], "produced_by": item[5], "photo": item[6], "price": item[7],
                             "addit_params": item[8], 'addit_equipment': item[9], 'height': item[10], 'width': item[11],
                             'depth': item[12], "id_provider": item[13], } for item in
                            await user_repository.get_all_compressors_info(lang)]
    result['List_equipment'] = [
        {"id_bitrix": item[0], "id_erp": item[1], "name": item[2], "price": item[3], "photo": item[4],
         "id_row": item[5], "id_provider": (item[6]), "count_tray": item[9]} for item in
        await user_repository.get_all_extra_equipment_info(lang)]
    
    result['sieve_size'] = [{"id_row": item[0], "size": item[1]} for item in await user_repository.get_all_sieve_size_info()]

    result['List_gost'] = [ {"id_row": item[0], "product": item[1], "purpose": item[2], "gost": item[3], "name": item[4],
         "link": item[5]} for item in await user_repository.get_Gost_info()]
    
    return result
# Роут для создания нового КП (аналог writeNewCP)
@router.post("/Write_new_cp/{pages}/{user_id_tg}/{key_cp}")
async def write_new_cp(pages: str , user_id_tg: str, key_cp: str,
):
    
    if key_cp != 'null':
        if pages in ("Sorting", "Separator"):
            List = await Read_createdKP_Calc(user_id_tg ,key_cp)
            data_cp = List['createKP']
            list_cp = List['List']
            return {"key": key_cp, 'data_CP': data_cp, 'List_CP': list_cp}
    else:
        # Генерация случайного ключа
        key = ''.join(
            random.choices(
                string.ascii_letters + string.digits,
                k=10
            )
        )

        # Формирование данных КП
        data_cp = DataCP(
            cp_key=key,
            group_info=GroupInfo(),
            additional_info={}
        )
        
        list_cp = ListCP(
            user_id_tg=user_id_tg,
            key_cp=key,
            short_title=key,
            creation_date=datetime.now().isoformat(),
            currency="",
            payment_method="",
            delivery_term="",
            warranty="",
            manager_id_tg=""
        )
      
        return {"key": key, 'data_CP': data_cp, 'List_CP': list_cp}


@router.post("/Write_createdKP/{pages}/{user_id}")
async def write_cp_list(request: Request,pages: str,user_id: str,data: WriteKPRequest):

    try:
        from main import user_repository

        current_date = datetime.now().strftime("%Y-%m-%d")
        data.List.creation_date = current_date
        data = await request.json()
        List = data['List']
        data['createKP']['group_info'] = json.dumps(data['createKP']['group_info'])
        data['createKP']['additional_info'] = json.dumps(data['createKP']['additional_info'])


        await user_repository.insert_row('struct_created_cp', data['createKP'])

        access_user = await user_repository.select_row('user_info', 'access_level', {'id_tg' : user_id})
        access_user = access_user[0][0]
        if access_user != 'client':
            List['manager_id_tg'] = user_id
        await user_repository.insert_row('list_of_created_cp', List)
        return List

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")









@router.post("/create_check_info")
async def create_check_info():
    try:
        # Создаем дату (вчерашний день)
        lastmanager_invoice = (datetime.now() - timedelta(days=1)).date().isoformat()
        
        check_info = CheckInfoRequest(
            id_tg="",  # Пустое значение, так как ID будет приходить из запроса
            lastmanager_invoice=lastmanager_invoice
        )
        
        return check_info.dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/getProviderData")
async def getProvider_Offer():

    from main import user_repository
    result = {key: [] for key in ['provider']}

    result['provider'] = [
        {"id": item[0], "organization_fullname": item[1], "organization_shortname": item[2], "country": item[3],
         "city": item[4], "inn": item[5], "ogrn": item[6],
         "kpp": item[7], "address": item[8], "index": item[9], "phone_number": item[10], "email": item[11],
         "bic": item[12], "bank_info": item[13],
         "checking_account": item[14], "corporate_account": item[15], "first_name": item[16], "second_name": item[17],
         "surname": item[18], "position_user": item[19], "acts_basis": item[20],
         "number_proxy": item[21], "seal_photo": item[22], "signature_photo": item[23], "equipment": item[24],
         "chat_id": item[25], "preamble_buy": item[26], "preamble_sell": item[27]} for item in
        await user_repository.get_all_provider_list_info()]

    return result



@router.get("/getConditionsData/{lang}")
async def getConditions_Offer(lang:str):
    from main import user_repository
    result = {key: [] for key in ['warranty', 'delivery_terms', 'payment_method', 'dop_info']}
   
    result['warranty'] = [
        {"id_provider": item[1], "warranty_period": item[2], "discount_value": item[3], "text": item[4]} for item
        in
        await user_repository.get_all_warranty_info(lang)]
    
    result['delivery_terms'] = [
        {"id_provider": (item[1]), "delivery_timeframe": item[2], "discount_value": item[3], "text": item[4]} for
        item in await user_repository.get_all_delivery_terms_info(lang)]

    result['payment_method'] = [
        {"id_provider": (item[1]), "payment_distribution": item[2], "discount_value": item[3], "text": item[4]} for
        item in await user_repository.get_all_payment_method_info(lang)]
    
    result['dop_info'] = [
        {"id": (item[1]), "parametr_name": item[3], "value": item[4],
         "unit_of_measurement": item[5], "type_machine": item[6]} for item in
        await user_repository.get_all_additional_parameters_info(lang)]

    return result



@router.get("/getcounterparty")
async def getcounterparty_Offer():
    from main import user_repository
    result = {key: [] for key in ['counterparty']}

    result['counterparty'] = [
        {"id_row": item[0], "name": item[1], "inn": item[3], "region": item[6]} for item in await user_repository.get_all_contractor_info()]

    return result

@router.get("/Id_counterparty/{id}")
async def getcounterparty_Offer(id: str):
    from main import user_repository
    result = {key: [] for key in ['counterparty']}
    
    result['counterparty'] = [
        {"id_row": item[0], "name": item[1], "orgn_ogrnip": item[2], "inn": item[3], "kpp": item[4], "address": item[5],
         "region": item[6], "phone_number": item[7], "email": item[8], "bank": item[9],
         "correspondent_account": item[10],
         "bic": item[11], "surname": item[12], "first_name": item[13], "patronymic": item[14], "basis": item[15],
         "number_proxy": item[16], "checking_account": item[17]} for item in await user_repository.select_row('contractor', '*', {'id_row':id})]

    return result



@router.post("/write_counterparty")
async def postcounterparty_Offer(request: Request):
    data = await request.json()
    from main import user_repository
    await  user_repository.insert_row('contractor', data)

    
    return True

@router.post("/SendMessage_ChatTo")
async def SendMessage_ChatTo(request: Request):
    data = await request.json()
    result = ''
    if data['chat'] == 'manager':
        result = TgSend.ManagerGetMessage(data)['result']['message_id']
    else:
        result = TgSend.sieveGetMessage(data)
    return result

@router.post("/test")
async def writeCheckInfo(request: Request):


    from main import user_repository
    data = await request.json()
    await  user_repository.insert_row('user_list', data['check_info'])
    return True



router.post("/writeCheckInfo")
async def writeCheckInfo(request: Request):


    from main import user_repository
    data = await request.json()
    await  user_repository.insert_row('user_list', data['check_info'])
    return True



@router.post("/SaveChangePrice")
async def SaveChangePrice(request: Request):

    from main import user_repository
    data = await request.json()
    try:
        await user_repository.save_changed_price_List(data)
    except IntegrityError as e:
        await user_repository.update_changed_price_List(data)
    return True


@router.post("/SaveChangeSale")
async def SaveChangeSale(request: Request):

    from main import user_repository
    data = await request.json()
    try:
        await user_repository.save_changed_sale_List(data)
    except IntegrityError as e:
        await user_repository.update_changed_sale_List(data)
    return True




@router.post("/Update_createdKP/{key}")
async def Update_createdKP_Calc(request: Request, key: str):
    from main import user_repository
    data = await request.json()
    data['createKP']['group_info'] = json.dumps(data['createKP']['group_info'])
    data['createKP']['additional_info'] = json.dumps(data['createKP']['additional_info'])


    await user_repository.update_row('struct_created_cp', 'cp_key', data['createKP'])
    await user_repository.update_row('list_of_created_cp', 'key_cp', data['List'])
    return True





@router.post("/RecognizeFiles/{id}")
async def RecognizeFiles(id: str, file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    converted_file_path = None
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        target_format = determine_target_format(file_path)
        if target_format:
            converted_filename = await convert_file(file_path, target_format)
            converted_file_path = UPLOAD_DIR / converted_filename
        else:
            converted_file_path = file_path
        SearcInfo = DocumentParser(
            converted_file_path,
            converted_file_path.suffix.lower().replace('.', ''),
            id
        )
        result = await SearcInfo.main()
        return {
            "result": result,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Ошибка при загрузке файла: {e}"})
    finally:
        if file_path.exists():
            file_path.unlink()
        if converted_file_path and converted_file_path != file_path and converted_file_path.exists():
            converted_file_path.unlink()




@router.post("/Get_Bitrix/{tg_id}")
async def Get_Bitrix(request: Request, tg_id: int):
    dataList =  await request.json()
    keyCP = dataList['key']
    result = await ReadCheckHtml.GetJson_bitrix(dataList)
    if result['code']== 200 or result['code']== 409: 
        data = {'text': f' Сделка с {dataList["buyer"]["organization_shortname"]} на сумму {dataList["sum"]}\nhttps://csort24.bitrix24.ru/crm/deal/details/{result["id_deal"]}/',
            'chatID':tg_id,
            'keyCP': keyCP
        }
        TgSend.Send_Text_markup(data)
    print(result)
    return result

@router.post("/Get_Bitrix_company/{id_deal}")
async def Get_Bitrix(id_deal: int):
    

    url = "https://csort-bitrix24.webtm.ru/api/v1/company-for-deal"

    headers = {
        "Authorization": "Bearer 503FQAqSnvSMXf45w4gWokVP87lqsv",  # если нужен
        "Accept": "application/json",
    }

    params = {
        "deal_id": id_deal
    }
    timeout = 60

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=timeout,
    )
    return response.json()

@router.post("/Update_check_info")
async def Update_check_info(request: Request):

    from main import user_repository
    data = await request.json()
    await user_repository.update_row('user_info', 'id_tg',data['User_Info'])
    await user_repository.update_row('user_list', 'id_tg', data['check_info'])

    return True



# Дописать выбор кп\сервис через переменные

@router.post("/Sieve_GetAgreement")
async def Sieve_GetAgreement(request: Request):

    from main import user_repository
    dataList = await request.json()

    if dataList[0]['client']== False:
        
        incl = await user_repository.select_row('statistics_of_generated_documents', '*',
            {"key": dataList[0]['key'], 'document': 'Договор'})
        
        data = {
            'key': dataList[0]['key'],
            'service': 'КП',
            'document': 'Договор',
            'supplier': re.sub(r"[\"]", "", dataList[0]['seller']['organization_shortname']),
            'buyer': dataList[0]['client'],
            'supplier_id': dataList[0]['Id_manager'],
            'sum': dataList[0]['sum'],
            'creation_date': dataList[0]['date'],
            'fio_manager': dataList[0]['FIO_manager']
        }
        if incl != []:
            await user_repository.update_row_mult_cond('statistics_of_generated_documents', ['document', 'key'], data)
        else:
            await user_repository.insert_row('statistics_of_generated_documents', data)

    for data in dataList:
        params = ('invoice', data['buyer']['user_id'], str(data['id_provider']), data['key'])
        key = data['key']
        number = await user_repository.execute_func(params)
        data['number'] = number

        data_getKPInfo_Offer = await getKPInfo_Offer(key)
        
        for i in range(len(data_getKPInfo_Offer['createKP'])):
            data['additional_info'] = data_getKPInfo_Offer['createKP'][i]['additional_info']
        
        filename = await ReadCheck.main(data, key)
    return 'filename'



# Дописать выбор кп\сервис через переменные
@router.post("/Sieve_GetCheck")
async def Sieve_GetCheck(request: Request):
    from main import user_repository
    dataList = await request.json()
    if dataList[0]['client']== False:
        incl = await user_repository.select_row('statistics_of_generated_documents', '*',
            {"key": dataList[0]['key'], 'document': 'Счет'})

        data = {
            'key': dataList[0]['key'],
            'service': 'КП',
            'document': 'Счет',
            'supplier': re.sub(r"[\"]", "", dataList[0]['seller']['organization_shortname']),
            'buyer': dataList[0]['client'],
            'supplier_id': dataList[0]['Id_manager'],
            'sum': dataList[0]['sum'],
            'creation_date': dataList[0]['date'],
            'fio_manager': dataList[0]['FIO_manager']
        }
        if incl != []:
            await user_repository.update_row_mult_cond('statistics_of_generated_documents', ['document', 'key'], data)
        else:
            await user_repository.insert_row('statistics_of_generated_documents', data)

    for data in dataList:
        params = ('contracts', data['buyer']['user_id'], str(data['id_provider']), data['key'])

        number = await user_repository.execute_func(params)
        data['number'] = number

        filename = await ReadCheckHtml.main(data)
    return filename



@router.post("/Sieve_SavePDF/{id_user}/{key}")
async def Sieve_SavePDF_Offer(id_user: str, key: str, request: Request):
    # if id_user != '5232657726':
    #     return False
    from main import user_repository
    dataList =  await request.json()

    incl = await user_repository.select_row('statistics_of_generated_documents', '*',
        {"key": key, 'document': 'КП'})
    if dataList['client']=='client':
        document = 'КП_клиент'
    else:
        document = 'КП'
    data = {
        'key': key,
        'service': 'КП',
        'document': document,
        'supplier': "ООО 'СИСОРТ'",
        'buyer': dataList['client'],
        'supplier_id': id_user,
        'sum': dataList['sum'],
        'creation_date': dataList['date'],
        'fio_manager': dataList['FIO']
    }
    if incl != []:
        await user_repository.update_row_mult_cond('statistics_of_generated_documents', ['document', 'key'], data)
    else:
        await user_repository.insert_row('statistics_of_generated_documents', data)


    await create_kp.main_save_kp_pdf(id_user,key,request)
    return 



@router.get("/GetCalkElevator/{id_deal}")
async def GetCalkElevator_Offer(id_deal: str, request: Request):
    document_name = id_deal.split('.')[0]
    
    if document_name in 'tg_tst':
        url = f"https://csort-transport.ru/static/new_data/web_data/TG_FOLDER/{document_name}/{id_deal}.json"
    else:
        url = f"https://csort-transport.ru/static/new_data/web_data/{document_name}/{id_deal}.json"
        
    response = requests.get(url, verify=False)
    response.raise_for_status()
    data = response.json()    

    save_dir = os.path.join("Front", "static", "document", "deal_elevator")
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"{id_deal}.json")

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # deal_elevator  -сюда загружать json 

    from main import user_repository
    nameEl = re.sub(r'([a-zA-Z]+)(\d+)', r'\1 \2', data['modelName'])


    value1 = float(data['modelPrice'])  # Заменяем запятую на пустоту (если есть)
    value2 = float(data['NDS']) # Заменяем запятую на точку
    priceEl = round(value1 * value2, 2)
    # priceEl = round(int(data['modelPrice']) * int(data['modelPrice']), 2)
    # round(int((str(data['modelPrice']).replace('.',','))*(str(data['NDS']).replace('.',','))), 2)
    
    
    height = (
        float(data['modelSize'].get('height', 0)) +
        float(data['modelSize'].get('top_length', 0)) +
        float(data['modelSize'].get('bottom_length', 0))+
        float(data['modelSize'].get('TransportLength', 0))

        
    )
    data_insert = {
        'price': priceEl,
        'height': height,
        'model':nameEl
    }
    await user_repository.update_row_mult_cond('elevator', ['model', 'height'], data_insert)

    return data

@router.get("/Sieve_GetData/{key}")
async def Sieve_GetData(key: str):
    from main import user_repository
    import os

    data = await user_repository.get_data_an_sieve_by_key(key)
    
    # Проверяем файлы в папке
    image_path = f'Front/static/img_sieve/{key}/'
    file_count = 0
    
    if os.path.exists(image_path):
        file_count = len([f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))])
    
    if data and file_count > 1:
        return {"result": data}
    else:
        return {"result": False}




@router.post("/Sieve_Analytics/{id}/{key}")
async def Sieve_SavePhoto(id: str, key: str, file: UploadFile, product: str = Form(...)):
    respData = {}
    
    directory = f"Front/static/img_sieve/{key}"
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(directory, exist_ok=True)
    filepath = f"{directory}/{id}.png"
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    with open(filepath, "rb") as f:
        im = f.read()
    datafile = base64.b64encode(im).decode('utf-8')
    respData[id] = [{
        'name': id, 
        'key': key,
        'photo': datafile, 
        'product': product
    }]
    
    result = requests.post('http://109.202.9.107:8443/image_to_json', json=respData)
    return 'result'


@router.get("/SearchInn_dadata/{inn}")
def SearchInn_dadata(inn: str):
    result = dadata_search.dadata_inn(inn)
    return result


@router.get("/SearchBic_dadata/{bic}")
def SearchBic_dadata(bic: str):
    result = dadata_search.dadata_bic(bic)
    return result


@router.post("/Manager_SavePhoto/{id}")
async def create_upload_file(id: str, file: UploadFile):
    filepath = f"Front/static/img_manager/{id}.png"
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)
    return f'/static/img_manager/{id}.png'


@router.post("/Error_KP")
async def Error_KP(request: Request):
    data = await request.json()
    TgSend.Send_Error(data)
    return ''

async def convert_file(file_path: Path, target_format: str):
    converted_path = CONVERTED_DIR / f"{file_path.stem}.{target_format}"
    try:
        # Обработка изображений
        if target_format == "jpg":
            if file_path.suffix.lower() in [".png", ".jpeg", ".jpg", ".bmp", ".tiff", ".gif", ".webp", ".heic", ".jfif"]:
                image = Image.open(file_path)
                rgb_image = image.convert("RGB")  # Убедимся, что формат RGB
                rgb_image.save(converted_path, format="JPEG")
        # Обработка документов Word
        elif target_format == "docx":
            if file_path.suffix.lower() in [".doc", ".rtf", ".odt"]:
                doc = Document(file_path)
                doc.save(converted_path)
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
        
        return f"{file_path.stem}.{target_format}"

    except Exception as e:
        print(f"Error converting file: {e}")
        return None
    
# Функция для определения формата назначения
def determine_target_format(file_path: Path):
    if file_path.suffix.lower() in [".png", ".jpeg", ".bmp", ".tiff", ".gif"]:
        return "jpg"
    elif file_path.suffix.lower() == ".doc":
        return "docx"
    elif file_path.suffix.lower() in [".txt", ".pdf", "jpg" , "docx"] : return False 
    return False

async def Read_createdKP_Calc(id:str,key:str,):
    from main import user_repository
    result = {key: [] for key in ['List', 'createKP']}

    result['createKP'] = [
        {"cp_key": item[0], "price": item[1], "group_info": (item[2]), "pdf_send": (item[3]), "id_send_mess": item[4],
         "id_send_check": item[5], 'sale':item[6], 'additional_info':item[7]  } for item in await user_repository.select_row('struct_created_cp', '*', {'cp_key':key})]

    result['List'] = [{"user_id_tg": item[1], "key_cp": item[2], "short_title": (item[3]), "creation_date": item[4],
                       "currency": item[5], "payment_method": item[6], "delivery_term": item[7],
                       "warranty": item[8], 'manager_id_tg': item[9]} for item in await user_repository.select_row('list_of_created_cp', '*', {'key_cp':key})]
    return result