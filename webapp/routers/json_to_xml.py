import os
import time
import datetime
import json

def json_to_xml(json_obj, line_padding=""):
    """Convert a JSON object to XML string."""
    result_list = []

    json_obj_type = type(json_obj)

    if json_obj_type is list:
        for sub_elem in json_obj:
            result_list.append(json_to_xml(sub_elem, line_padding))
        return "\n".join(result_list)

    if json_obj_type is dict:
        for tag_name in json_obj:
            sub_obj = json_obj[tag_name]
            result_list.append(f"{line_padding}<{tag_name}>")
            result_list.append(json_to_xml(sub_obj, "\t" + line_padding))
            result_list.append(f"{line_padding}</{tag_name}>")
        return "\n".join(result_list)
    return f"{line_padding}{json_obj}"

def main_json(json_data):
    unix_time = int(time.time())

    # Directory path
    
    directory_path = 'Front/static/document/agrement/XML'
    
    # Create directory if it doesn't exist
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            # print(f"Directory {directory_path} created successfully")
        except Exception as e:
            print(f"Error creating directory {directory_path}: {e}")
            return

    new_json_data = return_json(json_data)
    
    xml_data = f"<root>{json_to_xml(new_json_data)}</root>"

    # Save XML to file
    xml_file_path = f'{directory_path}/{json_data["NameFile"]} №{json_data["number"]}.xml'
    try:
        with open(xml_file_path, "w", encoding="utf-8") as xml_file:
            xml_file.write(xml_data)
            return xml_file_path
        # print(f"XML file created successfully at {xml_file_path}")
    except Exception as e:
        print(f"Error writing XML file {xml_file_path}: {e}")
    
def return_json(json_data):
    key = json_data['key']
    CategoryId = json_data['CategoryId']
    CreateIn1сErp = json_data['CreateIn1сErp']
    print(CreateIn1сErp)
    OrderNumber = json_data['number']
    Date_create = datetime.datetime.today().strftime("%d.%m.%Y")
    inn = json_data['buyer']['inn']
    kpp = json_data['buyer']['kpp']
    bik = json_data['buyer']['bic']
    bankAccount = json_data['buyer']['checking_account']
    Address = json_data['buyer']['address']
    email = json_data['buyer']['email']
    phone = json_data['buyer']['phone_number']
    first_name = json_data['buyer']['first_name']
    second_name = json_data['buyer']['second_name']
    surname = json_data['buyer']['surname'] 
    job_title = json_data['buyer']['position_user'] 
    Acts_basis = json_data['buyer']['acts_basis']
    number_proxy = json_data['buyer']['number_proxy']

    products_list = []
    for i in range(len(json_data['List'])):
        print(json_data['List'][i])
        name_product = json_data['List'][i]['name']
        count_product = json_data['List'][i]['count']
        price_product = json_data['List'][i]['price']
        summ_product = json_data['List'][i]['sum']
        try:
          id_erp = json_data['List'][i]['id_erp']

        except:
          id_erp = ''
        summ_product_nalog = summ_product *22 / 122 


        FIO_manager = json_data['FIO_manager']
        id_erp_manager = json_data['id_erp_manager']
        
        product = {
            "LineNumber": i + 1,
            "id": 135823 + i,
            "id_1c": id_erp,
            "productName": name_product,
            "characteristic": "",
            "quantity": count_product,
            "price": price_product,
            "discountRate": 0,
            "discountAmount": 0,
            "amount": summ_product,
            "vatAmount": summ_product_nalog,
            "amountIncludingVat": summ_product, 
        }
        products_list.append(product)

    new_json_data = {    
        "CustomerOrder": {
            "externalId": key,        
            "OrderNumber": OrderNumber,
            "OrderDate": Date_create,
            "OrderFile": "",
            "taxIncluded": "true",
            "taxRate": 22,
            "CategoryId": CategoryId,
            "CreateIn1сErp": CreateIn1сErp
        },
        "Manager": {
            "id": "93",
            "id_1c": id_erp_manager,
            "name": FIO_manager
        },
        "Client": {
            "id": "631",
            "inn": inn,
            "kpp": kpp,
            "bik": bik,
            "bankAccount": bankAccount,
            "Address": Address,
            "email": email,
            "phone": phone,
            "Signatory": {
                "id": 2631,
                "firstname": first_name,
                "secondname": second_name,
                "lastname": surname,
                "jobTitle": job_title,
                "basis": Acts_basis,
                "basis_info": number_proxy
            }
        },                     
        "Products": products_list,
        "comment":json_data['comment'],
        "Link": json_data['Link'],
        "id_deal": json_data['id_deal']

    }
    return new_json_data