# Документация по AJAX-запросам Python-сервера

Ниже собрана документация по AJAX-запросам, найденным во фронтенде (`Separator.js`, `common_function.js`, `botSortingKP.js`, `DBSorting.js`) и сопоставленным с FastAPI-роутами на сервере.

## Важно
- Задокументированы именно те эндпоинты, которые реально используются из JS.
- Часть ответов зависит от БД, поэтому для некоторых методов описана структура верхнего уровня и основные поля.
- В JS есть вызов `/off_bot/API/Error_KP`, но такого обработчика в загруженных Python-файлах не найдено.
- `writeCheckInfo` без `@router.post(...)` в `page_API.py` выглядит как недописанный/ошибочный роут, а реально используется `/API/test`.

---

## 1. Общие правила запросов

### Формат
Почти все запросы на сервер отправляются как:
- `Content-Type: application/json`
- тело: JSON-объект

Исключение:
- `/API/RecognizeFiles/{id}` — `multipart/form-data`, потому что туда загружается файл.

### Базовые префиксы
- `/off_bot/API/...` — основные бизнес-методы
- `/off_bot/API_CALC/...` — расчёты фотосепараторов и компрессоров
- `/off_bot/offer/...` — вспомогательные методы страницы КП/счёта

---

## 2. Расчётные AJAX-запросы (`/API_CALC`)

### 2.1 `POST /off_bot/API_CALC/Result_air`

**Назначение**  
Считает суммарный расход воздуха и расход на один лоток для фотосепаратора.

**Вход**
```json
{
  "sor": 5.5,
  "qual": 99.5,
  "performance": 3.2,
  "Count_tray": 3,
  "El_choice": {
    "mass1000_per_gram": 35,
    "k_masses": 1,
    "blow_per_m_sec": 120,
    "pressure_per_bar": 6
  }
}
```

**Поля**
- `sor` — исходная засоренность, число
- `qual` — требуемое качество, число
- `performance` — производительность, число
- `Count_tray` — число лотков, число
- `El_choice` — объект параметров выбранной конфигурации сепаратора

**Ответ**
```json
{
  "Result_air": 1234.5,
  "Count_tray": 3,
  "air_flow_per_tray": 411.5
}
```

---

### 2.2 `POST /off_bot/API_CALC/GetInfoSepar/{lang}`

**Назначение**  
Подбирает фотосепараторы и дополнительное оборудование под продукт, назначение, число лотков и производительность.

**Path params**
- `lang` — язык, обычно `ru` или `en`

**Вход**
```json
{
  "Product": "Пшеница",
  "Purpose": "Семена",
  "Count_tray": 3,
  "performance": 9.0,
  "choice_sorter": null
}
```

или при ручном выборе моделей:
```json
{
  "Product": "Пшеница",
  "Purpose": "Семена",
  "Count_tray": 3,
  "performance": 9.0,
  "choice_sorter": {
    "101": 2,
    "103": 1
  }
}
```

**Поля**
- `Product` — продукт
- `Purpose` — назначение
- `Count_tray` — требуемое число лотков
- `performance` — производительность
- `choice_sorter`:
  - `null` — сервер сам подбирает модели
  - объект `{id_сепаратора: количество}` — использовать выбранные модели

**Ответ**
```json
{
  "0": {
    "El_choice": {
      "product": "Пшеница",
      "purpose": "Семена",
      "performance_tray_per_t_h": 3.0,
      "sep_config": "RGB",
      "calculated_performance": 9.0
    },
    "count_separ": 1,
    "loop_tray": 3,
    "Separators": [
      {
        "id_row": 101,
        "name": "Фотоcепаратор ...",
        "name_print": "...",
        "model_series": "3.0",
        "configuration": "RGB",
        "id_provider": 3,
        "price": 1000000,
        "photo": "file.png",
        "height": 2000,
        "width": 1200,
        "depth": 1500,
        "additional_parameters": true,
        "additional_equipment": true,
        "tray": 3
      }
    ],
    "dop_equipment": [
      {
        "type": "Бункер",
        "model": "Бункер 3",
        "count": 1
      }
    ],
    "group_info": {
      "extra_equipment": {
        "20": 1,
        "23": 1
      }
    }
  }
}
```

---

### 2.3 `POST /off_bot/API_CALC/calculate_compressor/{lang}`

**Назначение**  
Подбирает компрессоры и дополнительное оборудование к ним.

**Path params**
- `lang` — `ru` или `en`

**Вход**
```json
{
  "Count_tray": 3,
  "Result_air": 1234.5,
  "air_flow_per_tray": 411.5,
  "Product": "Пшеница"
}
```

**Ответ**
```json
{
  "compressors": [
    {
      "compressor": {
        "id_row": 20,
        "id_bitrix": 123,
        "id_erp": "ERP-1",
        "name": "AirComp 500",
        "name_print": "AirComp 500",
        "produced_by": "Brand",
        "photo": "comp.png",
        "price": 250000,
        "addit_params": true,
        "addit_equipment": true,
        "height": 1800,
        "width": 900,
        "depth": 700,
        "id_provider": 3
      },
      "performance": {
        "id_row": 20,
        "name": "AirComp 500",
        "produced_by": "Brand",
        "id": 1,
        "min_perf": 1000,
        "max_perf": 1500
      },
      "count": 1,
      "air_flow": 1234.5
    }
  ],
  "total_air_flow": 1234.5,
  "min_required_air": 2010,
  "warning": null,
  "equipment_data": [
    {
      "type": "Доп оборудование",
      "model": "Платформа",
      "count": 1
    }
  ],
  "equipment_ids": {
    "22": 1
  }
}
```

---

## 3. Основные AJAX-запросы по КП и справочникам (`/API`)

### 3.1 `GET /off_bot/API/getListData/{lang}`

**Назначение**  
Возвращает основные справочники для экрана КП.

**Ответ**
```json
{
  "prod": [],
  "index": [],
  "ids": [],
  "machine": [],
  "kompressor": [],
  "photoMachine": [],
  "Service": [],
  "extra_equipment": [],
  "group_names": [],
  "attendance": [],
  "Elevator": [],
  "Pneumatic_feed": [],
  "sieve_size": [],
  "laboratory_equipment": []
}
```

---

### 3.2 `GET /off_bot/API/getListData_Separ/{lang}`

**Назначение**  
Возвращает справочники только для калькулятора фотосепараторов.

**Ответ**
```json
{
  "Separ_perf": [],
  "Compressor_perf": [],
  "List_separ": [],
  "List_compressor": [],
  "List_equipment": [],
  "sieve_size": [],
  "List_gost": []
}
```

---

### 3.3 `GET /off_bot/API/getUserInfo/{id}`

**Назначение**  
Возвращает карточку пользователя и его `check_info`.

**Ответ**
```json
{
  "user": [
    {
      "id_tg": "123",
      "surname": "Иванов",
      "name": "Иван",
      "middle_name": "Иванович",
      "phone_number": "+7999...",
      "mail": "mail@test.ru",
      "language": "ru",
      "data_reg": "2025-01-01",
      "access_level": "manager",
      "photo": "/path",
      "company": "ООО ...",
      "login": "username",
      "description": "text",
      "id_erp": "ERP-1",
      "job_title": "Менеджер"
    }
  ],
  "check_info": null
}
```

---

### 3.4 `GET /off_bot/API/getKPInfo/{key_Cp}`

**Назначение**  
Возвращает сохранённое КП по ключу.

**Ответ**
```json
{
  "List": [
    {
      "user_id_tg": "123",
      "key_cp": "abc123",
      "short_title": "abc123",
      "creation_date": "2026-03-24",
      "currency": "",
      "payment_method": "",
      "delivery_term": "",
      "warranty": "",
      "manager_id_tg": "123"
    }
  ],
  "createKP": [
    {
      "cp_key": "abc123",
      "price": 1000000,
      "group_info": { "...": "..." },
      "pdf_send": false,
      "id_send_mess": null,
      "id_send_check": null,
      "sale": 0,
      "additional_info": { "...": "..." }
    }
  ],
  "changed_price_List": null,
  "changed_sale_List": null
}
```

---

### 3.5 `POST /off_bot/API/Write_new_cp/{pages}/{user_id_tg}/{key_cp}`

**Назначение**  
Создаёт заготовку нового КП или возвращает уже существующее.

**Ответ при создании нового**
```json
{
  "key": "AbC123xYz9",
  "data_CP": {
    "cp_key": "AbC123xYz9",
    "group_info": {
      "Sieve": {},
      "sep_machine": {},
      "elevator": {},
      "compressor": {},
      "photo_sorter": {},
      "extra_equipment": {},
      "Service": {},
      "attendance": {},
      "Pneumatic_feed": {},
      "laboratory_equipment": {}
    },
    "price": 0,
    "sale": 0,
    "additional_info": {}
  },
  "List_CP": {
    "user_id_tg": "123",
    "key_cp": "AbC123xYz9",
    "short_title": "AbC123xYz9",
    "creation_date": "2026-03-24T10:00:00",
    "currency": "",
    "payment_method": "",
    "delivery_term": "",
    "warranty": "",
    "manager_id_tg": ""
  }
}
```

---

### 3.6 `POST /off_bot/API/Write_createdKP/{pages}/{user_id}`

**Назначение**  
Сохраняет новое КП в БД.

**Вход**
```json
{
  "createKP": {
    "cp_key": "abc123",
    "group_info": {
      "Sieve": {},
      "sep_machine": {},
      "elevator": {},
      "compressor": {},
      "photo_sorter": {},
      "extra_equipment": {},
      "Service": {},
      "attendance": {},
      "Pneumatic_feed": {},
      "laboratory_equipment": {}
    },
    "price": 0,
    "sale": 0,
    "additional_info": {}
  },
  "List": {
    "user_id_tg": "123",
    "key_cp": "abc123",
    "short_title": "abc123",
    "creation_date": "2026-03-24",
    "currency": "",
    "payment_method": "",
    "delivery_term": "",
    "warranty": "",
    "manager_id_tg": ""
  }
}
```

**Ответ**
```json
{
  "user_id_tg": "123",
  "key_cp": "abc123",
  "short_title": "abc123",
  "creation_date": "2026-03-24",
  "currency": "",
  "payment_method": "",
  "delivery_term": "",
  "warranty": "",
  "manager_id_tg": "123"
}
```

---

### 3.7 `POST /off_bot/API/Update_createdKP/{key}`

**Назначение**  
Обновляет уже сохранённое КП.

**Вход**
```json
{
  "createKP": {
    "cp_key": "abc123",
    "group_info": { "...": "..." },
    "price": 100000,
    "sale": 5,
    "additional_info": { "...": "..." }
  },
  "List": {
    "user_id_tg": "123",
    "key_cp": "abc123",
    "short_title": "abc123"
  }
}
```

**Ответ**
```json
true
```

---

### 3.8 `POST /off_bot/API/create_check_info`

**Назначение**  
Создаёт пустой шаблон `check_info`.

**Ответ**
```json
{
  "id_tg": "",
  "analysis_link": "",
  "analytics_photo": "",
  "pdf_kp": false,
  "agreement_kp": false,
  "invoice_kp": "",
  "organization": "",
  "inn": "",
  "address": "",
  "phone_number": "",
  "email": "",
  "bic": "",
  "checking_account": "",
  "first_name": "",
  "second_name": "",
  "surname": "",
  "position_user": "",
  "acts_basis": "",
  "number_proxy": "",
  "contract_ready": false,
  "agreement_signed": false,
  "invoice_sent": false,
  "lastmanager_invoice": "2026-03-23",
  "height": 0,
  "city": "",
  "organization_shortname": "",
  "organization_fullname": "",
  "ogrn": "",
  "kpp": "",
  "bank_info": "",
  "corporate_account": ""
}
```

---

### 3.9 `GET /off_bot/API/getProviderData`

**Назначение**  
Возвращает список поставщиков.

**Ответ**
```json
{
  "provider": [
    {
      "id": 3,
      "organization_fullname": "ООО ...",
      "organization_shortname": "ООО ...",
      "country": "Россия",
      "city": "Барнаул",
      "inn": "...",
      "ogrn": "...",
      "kpp": "...",
      "address": "...",
      "index": "...",
      "phone_number": "...",
      "email": "...",
      "bic": "...",
      "bank_info": "...",
      "checking_account": "...",
      "corporate_account": "...",
      "first_name": "...",
      "second_name": "...",
      "surname": "...",
      "position_user": "...",
      "acts_basis": "...",
      "number_proxy": "...",
      "seal_photo": "...",
      "signature_photo": "...",
      "equipment": "...",
      "chat_id": "...",
      "preamble_buy": "...",
      "preamble_sell": "..."
    }
  ]
}
```

---

### 3.10 `GET /off_bot/API/getConditionsData/{lang}`

**Назначение**  
Возвращает гарантию, доставку, оплату и дополнительные параметры.

**Ответ**
```json
{
  "warranty": [],
  "delivery_terms": [],
  "payment_method": [],
  "dop_info": []
}
```

---

### 3.11 `GET /off_bot/API/getcounterparty`

**Назначение**  
Возвращает краткий список контрагентов.

**Ответ**
```json
{
  "counterparty": [
    {
      "id_row": 1,
      "name": "ООО Ромашка",
      "inn": "1234567890",
      "region": "Алтайский край"
    }
  ]
}
```

---

### 3.12 `GET /off_bot/API/Id_counterparty/{id}`

**Назначение**  
Возвращает полную карточку контрагента по id.

**Ответ**
```json
{
  "counterparty": [
    {
      "id_row": 1,
      "name": "ООО Ромашка",
      "orgn_ogrnip": "...",
      "inn": "...",
      "kpp": "...",
      "address": "...",
      "region": "...",
      "phone_number": "...",
      "email": "...",
      "bank": "...",
      "correspondent_account": "...",
      "bic": "...",
      "surname": "...",
      "first_name": "...",
      "patronymic": "...",
      "basis": "...",
      "number_proxy": "...",
      "checking_account": "..."
    }
  ]
}
```

---

### 3.13 `POST /off_bot/API/write_counterparty`

**Назначение**  
Создаёт нового контрагента.

**Вход**
```json
{
  "name": "ООО Ромашка",
  "orgn_ogrnip": "...",
  "inn": "...",
  "kpp": "...",
  "address": "...",
  "region": "...",
  "phone_number": "...",
  "email": "...",
  "bank": "...",
  "correspondent_account": "...",
  "bic": "...",
  "surname": "...",
  "first_name": "...",
  "patronymic": "...",
  "basis": "...",
  "number_proxy": "...",
  "checking_account": "..."
}
```

**Ответ**
```json
true
```

---

### 3.14 `POST /off_bot/API/test`

**Назначение**  
Сохраняет `check_info` в таблицу `user_list`.

**Вход**
```json
{
  "check_info": {
    "id_tg": "123",
    "analysis_link": "",
    "analytics_photo": "",
    "pdf_kp": false,
    "agreement_kp": false,
    "invoice_kp": "",
    "organization": "",
    "inn": "",
    "address": "",
    "phone_number": "",
    "email": "",
    "bic": "",
    "checking_account": "",
    "first_name": "",
    "second_name": "",
    "surname": "",
    "position_user": "",
    "acts_basis": "",
    "number_proxy": "",
    "contract_ready": false,
    "agreement_signed": false,
    "invoice_sent": false,
    "lastmanager_invoice": "2026-03-23",
    "height": 0,
    "city": "",
    "organization_shortname": "",
    "organization_fullname": "",
    "ogrn": "",
    "kpp": "",
    "bank_info": "",
    "corporate_account": ""
  }
}
```

**Ответ**
```json
true
```

---

### 3.15 `POST /off_bot/API/SaveChangePrice`

**Назначение**  
Сохраняет ручные изменения цены по строкам КП.

**Вход**
```json
{
  "cp_key": "abc123",
  "changed_price_List": {
    "photo_sorter": {
      "101": 1500000
    },
    "compressor": {
      "20": 200000
    }
  }
}
```

**Ответ**
```json
true
```

---

### 3.16 `POST /off_bot/API/SaveChangeSale`

**Назначение**  
Сохраняет ручные скидки по строкам КП.

**Вход**
```json
{
  "cp_key": "abc123",
  "changed_sale_List": {
    "photo_sorter": {
      "101": 10
    },
    "compressor": {
      "20": 5
    }
  }
}
```

**Ответ**
```json
true
```

---

### 3.17 `POST /off_bot/API/RecognizeFiles/{id}`

**Назначение**  
Загружает файл и распознаёт из него реквизиты/данные клиента.

**Формат запроса**
`multipart/form-data`

**Поля формы**
- `file` — файл (`UploadFile`)

**Ответ**
```json
{
  "result": [
    {
      "organization_shortname": "ООО Ромашка",
      "inn": "1234567890",
      "kpp": "123456789",
      "address": "г. Москва ...",
      "bic": "044525225",
      "checking_account": "40702810...",
      "bank_info": "АО Банк ...",
      "corporate_account": "30101810...",
      "first_name": "Иван",
      "second_name": "Иванович",
      "surname": "Иванов",
      "position_user": "Директор",
      "acts_basis": "Устав",
      "number_proxy": ""
    }
  ]
}
```

---

### 3.18 `POST /off_bot/API/Get_Bitrix/{tg_id}`

**Назначение**  
Создаёт/обновляет сделку в Bitrix по данным КП.

**Вход**
```json
{
  "key": "abc123",
  "buyer": {
    "organization_shortname": "ООО Ромашка"
  },
  "sum": 1000000
}
```

**Ответ**
```json
{
  "code": 200,
  "id_deal": 12345
}
```

Возможные коды:
- `200` — сделка создана
- `405`
- `406`
- `407`
- `408`
- `409` — сделка уже существует
- `500` — внутренняя ошибка

---

### 3.19 `POST /off_bot/API/Get_Bitrix_company/{id_deal}`

**Назначение**  
Получает данные компании из Bitrix по ID сделки.

**Ответ**
```json
{
  "result": {
    "inn": "...",
    "title": "...",
    "address": "..."
  }
}
```

---

### 3.20 `POST /off_bot/API/Update_check_info`

**Назначение**  
Обновляет данные пользователя и `check_info`.

**Вход**
```json
{
  "User_Info": {
    "id_tg": "123",
    "access_level": "manager",
    "company": "ООО СИСОРТ",
    "data_reg": "2025-01-01",
    "language": "ru",
    "login": "username",
    "mail": "mail@test.ru",
    "middle_name": "Иванович",
    "name": "Иван",
    "phone_number": "+7999...",
    "photo": "",
    "surname": "Иванов",
    "description": "text",
    "id_erp": "ERP-1",
    "job_title": "Менеджер"
  },
  "check_info": {
    "id_tg": "123",
    "inn": "1234567890",
    "address": "Москва",
    "phone_number": "+7999...",
    "email": "mail@test.ru",
    "bic": "044525225",
    "checking_account": "40702810...",
    "first_name": "Иван",
    "second_name": "Иванович",
    "surname": "Иванов",
    "position_user": "Директор",
    "acts_basis": "Устав",
    "number_proxy": "",
    "pdf_kp": false,
    "contract_ready": false,
    "agreement_signed": false,
    "invoice_sent": false,
    "lastmanager_invoice": "2026-03-23",
    "organization_shortname": "ООО Ромашка",
    "organization_fullname": "Общество ...",
    "ogrn": "...",
    "kpp": "...",
    "bank_info": "...",
    "corporate_account": "..."
  }
}
```

**Ответ**
```json
true
```

---

### 3.21 `POST /off_bot/API/SendMessage_ChatTo`

**Назначение**  
Отправляет сообщение в Telegram-чат менеджеру или клиенту.

**Вход**
```json
{
  "chat": "manager",
  "chatID": "-100...",
  "text": "Текст",
  "keyCP": "abc123",
  "tg_id": "123",
  "UserName": "username",
  "page": "KP"
}
```

**Ответ**
- если `chat == "manager"` — `message_id`
- иначе — результат `TgSend.sieveGetMessage(data)`

---

### 3.22 `POST /off_bot/API/Sieve_GetAgreement`

**Назначение**  
Формирует договор(ы) по КП.

**Вход**
```json
[
  {
    "client": false,
    "key": "abc123",
    "seller": {
      "organization_shortname": "ООО СИСОРТ"
    },
    "buyer": {
      "user_id": "123"
    },
    "id_provider": 3,
    "sum": 1000000,
    "date": "2026-03-24",
    "FIO_manager": "Иванов И.И.",
    "Id_manager": "123",
    "additional_info": {},
    "NameFile": "ООО СИСОРТ",
    "Chat_id": "123"
  }
]
```

**Ответ**
```json
"filename"
```

---

### 3.23 `POST /off_bot/API/Sieve_GetCheck`

**Назначение**  
Формирует счёт(а) по КП.

**Вход**
```json
[
  {
    "client": false,
    "key": "abc123",
    "seller": { "...": "..." },
    "buyer": { "...": "..." },
    "id_provider": 3,
    "sum": 1000000,
    "date": "2026-03-24",
    "Id_manager": "123",
    "Chat_id": "123",
    "additional_info": {}
  }
]
```

**Ответ**
На практике лучше считать успешным служебный JSON/строку результата генерации документа. Формат в коде не унифицирован.

---

## 4. AJAX-запросы из `/offer`

### 4.1 `POST /off_bot/offer/Sieve_CaseChange`

**Назначение**  
Преобразование регистра текста через `CaseChange.StartCase`.

**Вход**
```json
{
  "text": "текст для преобразования"
}
```

**Ответ**  
Обычно строка с преобразованным текстом.

---

### 4.2 `GET /off_bot/offer/UserInfo_Key/{key}`

**Назначение**  
Возвращает пользователя по ключу КП.

**Ответ**
```json
{
  "user": [
    {
      "id_tg": "123",
      "surname": "Иванов",
      "name": "Иван",
      "middle_name": "Иванович",
      "phone_number": "+7999...",
      "mail": "mail@test.ru",
      "language": "ru",
      "data_reg": "2025-01-01",
      "access_level": "manager",
      "photo": "",
      "company": "ООО ...",
      "login": "username",
      "description": "",
      "id_erp": "",
      "job_title": ""
    }
  ]
}
```

---

### 4.3 `POST /off_bot/offer/Save_NewCounter`

**Назначение**  
Создаёт нового контрагента в таблице `contractor`.

**Вход**  
Структура такая же, как у `/API/write_counterparty`.

**Ответ**
```json
true
```

---

### 4.4 `POST /off_bot/offer/CSort_GetCheck`

**Назначение**  
Формирует счёт и возвращает URL PDF-файла.

**Вход**
```json
{
  "buyer": {
    "bic": "044525225",
    "inn": "1234567890",
    "user_id": "123"
  },
  "id_provider": 3,
  "key": "abc123",
  "sum": 1000000,
  "NameFile": "ООО Ромашка",
  "Chat_id": "123"
}
```

**Ответ**
```json
"https://csort-news.ru/off_bot/static/document/check/PDF/file.pdf"
```

---

## 5. Полезные модели

### `GroupInfo`
```json
{
  "Sieve": {},
  "sep_machine": {},
  "elevator": {},
  "compressor": {},
  "photo_sorter": {},
  "extra_equipment": {},
  "Service": {},
  "attendance": {},
  "Pneumatic_feed": {},
  "laboratory_equipment": {}
}
```

Обычно каждый вложенный объект — это словарь вида:
```json
{
  "101": 2,
  "205": 1
}
```
где ключ — `id_row` или другой ID номенклатуры, а значение — количество.

---

## 6. Что стоит исправить в API

1. Везде явно задавать `contentType: 'application/json'` на фронте для JSON-запросов.
2. Унифицировать ответы:
   - либо всегда `{ "success": true, "data": ... }`
   - либо строго типизированные JSON-объекты.
3. Исправить `Update_createdKP/{key}` — сейчас path-параметр по смыслу не совпадает с тем, что передаёт фронт.
4. Исправить `Sieve_GetAgreement`, чтобы он возвращал не строку `"filename"`, а реальный результат.
5. Удалить или починить `writeCheckInfo`, потому что сейчас используется `/API/test`.
6. Задокументировать или добавить отсутствующий `/API/Error_KP`, потому что фронт его вызывает.
