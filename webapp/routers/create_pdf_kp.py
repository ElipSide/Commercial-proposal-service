import os
import asyncio
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates
import routers.CreatePDF as CreatePDF

# внешние зависимости
import routers.API.page_API as page_API
import routers.page_CalcKP as page_CalcKP
from routers.push_message import TgSendMess

# модули
from .modules.pdf_utils import convert_html_to_pdf_kp
from .modules.google_utils import google_read
from .modules.dop_info_utils import (
    DopInfo_photo, DopInfo_machine, DopInfo_compressor, DopInfo_Elevator, DopInfo_laboratory
)
from .modules.pricing_utils import (
    getPhotoMachine, getMachine, getKompressor, getSieve,
    getExtra_equipment, getService, getAttendance, getElevator, getLaboratory
)
from .modules.offer_utils import getPayment_method, getDelivery_terms, getWarranty

TgSend = TgSendMess()
templates = Jinja2Templates(directory="Front/templates/")
url = "http://localhost:8000/off_bot"

def _float(x) -> float:
    try:
        return float(str(x).replace(",","."))
    except Exception as e:
        return 0.0
    
def _add_prefix(d: dict, prefix: str) -> dict:
    return {f"{prefix}_{k}": v for k, v in d.items()}

class createKpPdf:
    ATTENDANCE_EXCLUDE = ("6", "7")

    def __init__(self):
        self.today = datetime.now().date()
        self.today_str = self.today.strftime("%d.%m.%Y")
        self.date_3_days_str = (self.today + timedelta(days=3)).strftime("%d.%m.%Y")
        self.kp_info: dict = {}
    
    async def getting_user_data(self, key: str, id_user: str) -> dict:
        """получение данных пользователя"""
        info_users = await page_CalcKP.UserInfo_Key_offer(key)
        user = info_users["user"][0]
        lang = user["language"]
        
        if user["access_level"] == "manager":
            return {
                'lang': lang,
                'name_user': user["name"],
                'middle_name_user': user["middle_name"],
                'phone_number_user': user["phone_number"],
                'mail_user': user["mail"],
                'company_user': user["company"],
                'job_title': user["job_title"],
                'chat_id_tg': id_user
            }

        return {
            'lang': lang,
            'name_user': "Екатерина",
            'middle_name_user': "Костырченко",
            'phone_number_user': "79520015452",
            'mail_user': "ekaterina.prodd@gmail.com",
            'company_user': 'ООО "СИСОРТ"',
            'job_title': "",
            'chat_id_tg': "2013519822"
        }

    def get_sale_info(self, arr_kp_info):
        """"Получение скидок"""
        sale_discount = arr_kp_info["createKP"][0]["sale"]
        discount_price_List = (
            arr_kp_info["changed_price_List"][0]["List"] 
            if arr_kp_info["changed_price_List"] is not None 
            else {}
        )
        changed = arr_kp_info.get("changed_sale_List")
        sale = (
            changed[0]["List"]
            if changed and changed[0].get("List") is not None
            else None
        )

        return sale_discount, discount_price_List, sale
    
    def parse_equipment(self):
        """извлечение данных КП"""
        ki = self.kp_info
        return {
            "photo_sorter":   ki["photo_sorter"],
            "sep_machine":    ki["sep_machine"],
            "compressor":     ki["compressor"],
            "sieve":          ki["Sieve"],
            "extra_equipment":ki["extra_equipment"],
            "service":        ki["Service"],
            "attendance":     ki["attendance"],
            "elevator":       ki["elevator"],
            "laboratory":     ki["laboratory_equipment"],
        }
    
    def build_parts(self, equipment):
        """получение сроков доставки и гарантии"""
        mapping = [
            ("laboratory", "1"),
            ("photo_sorter", "2"),
            ("compressor", "4"),
            ("extra_equipment", "5"),
            ("elevator", "7"),
        ]

        deliveryParts, warrantyParts = [], []
        for key, code in mapping:
            if equipment[key]:
                deliveryParts.append(code)
                warrantyParts.append(code)
        return deliveryParts ,warrantyParts

    def build_equipment_rows(self, equipment: dict, sale_blocks: dict) -> dict:
        """Формирование id/count/sale""" 
        def rows(eq_key, sale_key):
            if not equipment[eq_key]:
                return [],[],[]
            ids = list(equipment[eq_key].keys())
            count = list(equipment[eq_key].values())
            sales = [sale_blocks.get(sale_key, {}).get(mid, 0) for mid in ids]
            return ids,count,sales
        
        att_ids = [k for k in equipment["attendance"] if k not in self.ATTENDANCE_EXCLUDE]
        att_count = [v for k, v in equipment["attendance"].items() if k not in self.ATTENDANCE_EXCLUDE]
        att_sales = [sale_blocks.get("attendance", {}).get(mid, 0) for mid in att_ids]

        return {
            "photo_sorter":    rows("photo_sorter", "photo_sorter"),
            "sep_machine":     rows("sep_machine", "sep_machine"),
            "compressor":      rows("compressor", "compressor"),
            "sieve":           rows("sieve", "Sieve"),
            "extra_equipment": rows("extra_equipment", "extra_equipment"),
            "service":         rows("service", "Service"),
            "elevator":        rows("elevator", "elevator"),
            "laboratory":      rows("laboratory", "laboratory_equipment"),
            "attendance":      (att_ids, att_count, att_sales),
        }

    def _combine_specs(self, parts: dict) -> dict:
        """Объединение спецификаций и подсчёт итогов"""
        combined_spec = {}
        total_keys = [
            "total_specification_sum",
            "total_specification_discount_price",
            "total_specification_sum_nds",
            "total_specification_price_nds",
            "total_specification_discount_sum_nds",
            "total_med_discount",
        ]
        totals = {k: 0.0 for k in total_keys}
        for label, part in parts.items():
            if part is None:
                continue
            combined_spec.update(_add_prefix(part["specification_dict"], label))
            for k in total_keys:
                totals[k] += _float(part.get(k, 0))
                
        return {"specification_dict": combined_spec, **totals}
    
    def _get_locale_strings(self, lang: str) -> dict:
        if lang == "ru":
            return {
                "text_bottom": f"Предложение действительно до {self.date_3_days_str}",
                "file_name_desc": f"КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ от {self.today_str}",
                "file_name": f"ПРЕДЛОЖЕНИЕ от {self.today_str} №{{key}}.pdf",
            }
        return {
            "text_bottom": f"The offer is valid until {self.date_3_days_str}",
            "file_name_desc": f"COMMERCIAL OFFER FROM {self.today_str}",
            "file_name": f"OFFER FROM {self.today_str}.pdf",
        }
        
    def _resolve_product_efficiency(self, additional_info: dict, dop_info_photo: list) -> tuple:
        """Определение культуры и производительности"""
        product = (additional_info.get("prod") or "").lower() or None
        efficiency = (additional_info.get("efficiency") or "").lower() or None

        if not product and dop_info_photo:
            product = "Пшеница"
            efficiency = dop_info_photo[0]["Производительность"]["value"]

        return product, efficiency
    
    def _get_product_datv(self, product: str | None) -> str | None:
        """Дательный падеж культуры"""  
        if not product:
            return None
        if "лен" in product:
            return "ЛЬНУ"
        if "подсолнечник" in product:
            return "ПОДСОЛНЕЧНИКУ"
        return None
    
    def _get_lizing_url(self, photo_machine: dict) -> str | None:
        try:
            spec = photo_machine["specification_dict"]
            if spec:
                first_idx = sorted(spec.keys())[0]
                model_name = spec[first_idx].get("specification_name")
                if model_name:
                    return google_read(model_name)
        except Exception:
            pass
        return None

    async def main_save_kp_pdf(self, id_user: str, key: str, request):
        """Основная функция"""

        # --- данные пользователя ---
        data_user = await self.getting_user_data(key, id_user)
        lang = data_user["lang"]

        arr_kp_info, table_data, ConditionsData = await asyncio.gather(
            page_API.getKPInfo_Offer(key),
            page_API.getList_Offer(lang),
            page_API.getConditions_Offer(lang),
        )
        
        print(arr_kp_info)

        self.kp_info = arr_kp_info["createKP"][0]["group_info"]
        additional_info = arr_kp_info["createKP"][0]["additional_info"]
        nds_now = int(additional_info["nds"]) if additional_info["nds"] else 22

        # --- скидки ---
        sale_discount, discount_price_List, sale = self.get_sale_info(arr_kp_info)
        sale_blocks = sale or {}

        equipment = self.parse_equipment()
        deliveryParts, warrantyParts = self.build_parts(equipment)
        rows = self.build_equipment_rows(equipment, sale_blocks)

        # --- доп. инфо параллельно ---
        dop_info_photo, dop_info_machine, dop_info_compressor, dop_info_elevator, dop_info_laboratory = (
            await asyncio.gather(
                DopInfo_photo(rows["photo_sorter"][0], lang, ConditionsData),
                DopInfo_machine(rows["sep_machine"][0], lang, ConditionsData),
                DopInfo_compressor(rows["compressor"][0], lang, ConditionsData),
                DopInfo_Elevator(list(additional_info.get("id_json", {}).values()), rows["elevator"][1], lang),
                DopInfo_laboratory(rows["laboratory"][0], lang, ConditionsData),
            )
        )
        # --- спецификации параллельно ---
        (
            PhotoMachine, Machine, Compressor, Laboratory, Sieve,
            Extra_equipment, Service, Attendance, Elevator
        ) = await asyncio.gather(
            getPhotoMachine(table_data, *rows["photo_sorter"], url, dop_info_photo, nds_now, sale_discount, discount_price_List),
            getMachine(table_data, *rows["sep_machine"], url, dop_info_machine, nds_now, sale_discount, discount_price_List),
            getKompressor(table_data, *rows["compressor"], url, dop_info_compressor, nds_now, sale_discount, discount_price_List),
            getLaboratory(table_data, *rows["laboratory"], url, dop_info_laboratory, nds_now, sale_discount, discount_price_List),
            getSieve(table_data, *rows["sieve"], nds_now, sale_discount, discount_price_List, url),
            getExtra_equipment(table_data, *rows["extra_equipment"], nds_now, sale_discount, discount_price_List, url),
            getService(table_data, *rows["service"], nds_now, sale_discount, discount_price_List, url),
            getAttendance(table_data, *rows["attendance"], nds_now, sale_discount, discount_price_List, url),
            getElevator(table_data, *rows["elevator"], nds_now, additional_info, sale_discount, discount_price_List, url),
        )

        spec_parts = {
            "PhotoMachine": PhotoMachine, "Machine": Machine,
            "Compressor": Compressor, "Sieve": Sieve,
            "Extra_equipment": Extra_equipment, "Service": Service,
            "Laboratory": Laboratory, "Attendance": Attendance,
            "Elevator": Elevator,
        }
        combined_dict = self._combine_specs(spec_parts)

        product, efficiency = self._resolve_product_efficiency(additional_info, dop_info_photo)
        product_datv = self._get_product_datv(product)
        url_lizing = self._get_lizing_url(PhotoMachine)

        report = await CreatePDF.createPDF(product, background=False) if product else None

        locale = self._get_locale_strings(lang)
        file_name = locale["file_name"].format(key=key)

        payment, delivery, warranty = await asyncio.gather(
            getPayment_method(arr_kp_info["List"][0]["payment_method"], ConditionsData),
            getDelivery_terms(deliveryParts, ConditionsData),
            getWarranty(warrantyParts, ConditionsData),
        )

        # --- контекст ---
        context_main = {
            "request": request,
            "url": url,
            "key": key,
            **{k: data_user[k] for k in ("chat_id_tg", "name_user", "middle_name_user", "phone_number_user", "mail_user", "company_user", "job_title")},
            "specification": combined_dict["specification_dict"],
            "total_specification_sum": combined_dict["total_specification_sum"],
            "total_specification_sum_nds": combined_dict["total_specification_sum_nds"],
            "total_specification_discount_price": combined_dict["total_specification_discount_price"],
            "total_specification_price_nds": combined_dict["total_specification_price_nds"],
            "total_specification_discount_sum_nds": combined_dict["total_specification_discount_sum_nds"],
            "total_med_discount": combined_dict["total_med_discount"],
            "sale_discount": sale_discount,
            "dop_info_photo": dop_info_photo,
            "dop_info_machine": dop_info_machine,
            "dop_info_compressor": dop_info_compressor,
            "dop_info_elevator": dop_info_elevator,
            "dop_info_laboratory": dop_info_laboratory,
            "payment": payment,
            "delivery": delivery,
            "warranty": warranty,
            "nds_now": nds_now,
            "product": product,
            "efficiency": efficiency,
            "product_datv": product_datv,
            "today_str": self.today_str,
            "id_row_photo_sorter": equipment["photo_sorter"],
            "url_lizing": url_lizing,
            "report": report,
        }
        

        # --- PDF ---
        rendered_main = templates.get_template(f"{lang}/create_pdf_kp.html").render(context_main)

        pdfdirs = os.path.join("Front", "static", "document", "reports")
        os.makedirs(pdfdirs, exist_ok=True)
        pdf_filename = os.path.join(pdfdirs, file_name)

        await convert_html_to_pdf_kp(rendered_main, pdf_filename, locale["text_bottom"])

        TgSend.agrement_PDFSend({
            "service": "КП",
            "chatID": id_user,
            "UserName": data_user["name_user"],
            "page": "Offer",
            "path_file": pdf_filename,
            "keyCP": key,
            "text": locale["file_name_desc"],
        })

