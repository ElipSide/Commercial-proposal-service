# models.py
from pydantic import BaseModel
from typing import Dict, Any, Optional,List

class GroupInfo(BaseModel):
    Sieve: Dict[str, Any] = {}
    sep_machine: Dict[str, Any] = {}
    elevator: Dict[str, Any] = {}
    compressor: Dict[str, Any] = {}
    photo_sorter: Dict[str, Any] = {}
    extra_equipment: Dict[str, Any] = {}
    Service: Dict[str, Any] = {}
    attendance: Dict[str, Any] = {}
    Pneumatic_feed: Dict[str, Any] = {}
    laboratory_equipment: Dict[str, Any] = {}


class ListCP(BaseModel):
    user_id_tg: str
    key_cp: str
    short_title: str
    creation_date: str = ""
    currency: str = ""
    payment_method: str = ""
    delivery_term: str = ""
    warranty: str = ""
    manager_id_tg: str = ""

class DataCP(BaseModel):
    cp_key: str
    group_info: GroupInfo
    price: int = 0
    sale: int = 0
    additional_info: Dict[str, Any] = {}

class WriteKPRequest(BaseModel):
    createKP: DataCP
    List: ListCP

class CheckInfoRequest(BaseModel):
    id_tg: str
    analysis_link: str = ""
    analytics_photo: str = ""
    pdf_kp: bool = False
    agreement_kp: bool = False
    invoice_kp: str = ""
    organization: str = ""
    inn: str = ""
    address: str = ""
    phone_number: str = ""
    email: str = ""
    bic: str = ""
    checking_account: str = ""
    first_name: str = ""
    second_name: str = ""
    surname: str = ""
    position_user: str = ""
    acts_basis: str = ""
    number_proxy: str = ""
    contract_ready: bool = False
    agreement_signed: bool = False
    invoice_sent: bool = False
    lastmanager_invoice: str = ""
    height: int = 0
    city: str = ""
    organization_shortname: str = ""
    organization_fullname: str = ""
    ogrn: str = ""
    kpp: str = ""
    bank_info: str = ""
    corporate_account: str = ""


class CalculationData(BaseModel):
    Product: str
    Purpose: str
    Count_tray: int
    performance: Optional[float] = None


class CompressorRequest(BaseModel):
    Result_air: float
    air_flow_per_tray: float
    Count_tray: int
    Product: str

class CompressorResponse(BaseModel):
    El_copres: Dict
    count_kompres: int
    loop_air: float
    min_comp_air: float
    warning: Optional[str] = None

class CompressorPerformance(BaseModel):
    id_row: int
    name: str
    produced_by: str
    id: int
    min_perf: float
    max_perf: float


class CompressorInfo(BaseModel):
    id_row: int
    id_bitrix: Optional[int]
    id_erp: Optional[str]
    name: str
    name_print: Optional[str]
    produced_by: str
    photo: Optional[str]
    price: Optional[float]
    addit_params: bool
    addit_equipment: bool
    height: Optional[float]
    width: Optional[float]
    depth: Optional[float]
    id_provider: Optional[int]


