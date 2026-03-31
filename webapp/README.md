# webapp

Веб-приложение для расчётов, формирования КП, счетов и договоров, а также работы с Telegram WebApp для оборудования Csort.

## Что делает проект

`webapp` — это backend на FastAPI и набор frontend-страниц/скриптов для:
- расчёта решётных машин;
- подбора фотосепараторов и связанного оборудования;
- формирования коммерческих предложений;
- генерации счетов, договоров и PDF;
- работы с данными пользователей, контрагентов и поставщиков;
- интеграций с Telegram Bot API, DaData, Bitrix и внешними сервисами распознавания.

## Стек

- Python
- FastAPI
- PostgreSQL
- Jinja2 templates
- JavaScript / Telegram WebApp
- Uvicorn

## Структура

Примерно проект устроен так:

```text
webapp/
├── main.py
├── .env
├── README.md
├── push_message.py
├── create_pdf_kp.py
├── company_information.py
├── routers/
│   ├── auth.py
│   ├── users.py
│   ├── page_API.py
│   ├── page_CalcKP.py
│   ├── page_CalcSorting.py
│   ├── page_Separator.py
│   ├── page_Service.py
│   ├── page_Noria.py
│   ├── dadata_search.py
│   ├── ReadCheck.py
│   └── ReadCheckHtml.py
├── db/
│   ├── db_ext.py
│   └── db_ext_func.py
└── Front/
    ├── templates/
    └── static/
```

## Запуск

### 1. Установить зависимости

```bash
pip install -r requirements.txt
```

Если `requirements.txt` пока не полный, обычно дополнительно нужны:

```bash
pip install fastapi uvicorn python-dotenv jinja2 requests pillow python-docx psycopg[binary] passlib bcrypt gspread oauth2client dadata
```

### 2. Создать `.env`

Файл `.env` рекомендуется хранить в корне проекта рядом с `main.py`.

Минимальный пример:

```env
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=5432

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DADATA_TOKEN=your_dadata_token

GOOGLE_CREDENTIALS_PATH=Front/static/json/crend.json
GOOGLE_SPREADSHEET_ID=your_google_sheet_id
GOOGLE_WORKSHEET_NAME=main

BITRIX_COMPANY_API_URL=https://example.com/api/v1/company-for-deal
BITRIX_BEARER_TOKEN=your_bitrix_token

IMAGE_TO_JSON_URL=http://127.0.0.1:8443/image_to_json
```

### 3. Запустить приложение

```bash
uvicorn main:app --reload
```

## Локальные адреса

Если приложение поднято локально:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- с учётом `root_path=/off_bot`: основные маршруты будут доступны через `/off_bot/...`

Примеры:
- `http://127.0.0.1:8000/off_bot/`
- `http://127.0.0.1:8000/off_bot/login`
- `http://127.0.0.1:8000/off_bot/docs`

## Основные модули

### `main.py`
Точка входа приложения:
- создаёт `FastAPI`;
- подключает шаблоны, статику и middleware;
- инициализирует БД;
- подключает роутеры;
- отвечает за login/logout и admin-доступ.

### `routers/page_API.py`
Основной API-слой для frontend и Telegram WebApp:
- получение справочников и номенклатуры;
- чтение/создание/обновление КП;
- работа с контрагентами;
- отправка сообщений в Telegram;
- работа с файлами;
- интеграции с DaData, Bitrix и внешними сервисами.

### `push_message.py`
Отправка сообщений, изображений и PDF через Telegram Bot API.

### `Front/static/js/`
Frontend-логика калькуляторов, карточек оборудования, КП и Telegram WebApp.

## Что важно вынести в `.env`

В `.env` нужно хранить всё, что не должно попадать в git:

- токены;
- API keys;
- bearer tokens;
- логины/пароли/строки подключения к БД;
- URL внешних сервисов, если они зависят от окружения;
- пути к credential-файлам.

Обычно **не обязательно** выносить:
- `root_path`;
- названия папок шаблонов и статики;
- favicon path;
- служебные константы интерфейса;
- локальные значения по умолчанию, которые не являются секретами.

## Git

В `.gitignore` обязательно должны быть:

```gitignore
.env
__pycache__/
*.pyc
Front/static/json/crend.json
*.log
```

Если есть отдельные credential-файлы или выгрузки:

```gitignore
Front/static/img_manager/files/
Front/static/document/deal_elevator/
Front/static/img_sieve/
```

## База данных

По текущему README в проекте используются как минимум следующие основные таблицы: `additional_parameters`, `calc_sieve`, `calc_sieve_index`, `calc_sieve_size`, `currency`, `delivery_terms`, `list_of_created_cp`, `payment_method`, `provider_list`, `separat_table`, `sessions`, `sieve_table`, `struct_created_cp`, `user_credentials`, `user_info`, `user_list`, `warranty` fileciteturn8file0

### Ключевые таблицы

#### `struct_created_cp`
Хранит структуру коммерческого предложения:
- `cp_key`
- `price`
- `group_info`

#### `list_of_created_cp`
Метаданные созданного КП:
- `user_id_tg`
- `key_cp`
- `creation_date`
- `payment_method`
- `delivery_term`
- `warranty`
- `manager_id_tg`

#### `user_info`
Основная информация о пользователе:
- Telegram ID
- ФИО
- телефон
- email
- язык
- роль
- компания

#### `user_list`
Реквизиты и данные для документов:
- ИНН
- адрес
- телефон
- email
- БИК
- расчётный счёт
- подписант
- основание подписания
- реквизиты компании

#### `provider_list`
Реквизиты поставщиков и компаний.

#### `sieve_table`, `calc_sieve`, `calc_sieve_index`, `separat_table`
Справочники оборудования и таблицы расчётов. Их описание уже было в старом README fileciteturn8file0

## Типовой сценарий работы

1. Пользователь открывает WebApp из Telegram.
2. Frontend получает справочники и данные пользователя через `/API/...`.
3. Пользователь подбирает оборудование или собирает КП.
4. Backend сохраняет структуру КП в БД.
5. При необходимости формируются PDF, счета, договоры.
6. Telegram-бот отправляет пользователю или менеджеру сообщение/файл.

## Полезные API-роуты

Несколько важных маршрутов:
- `GET /API/getListData/{lang}`
- `GET /API/getUserInfo/{id}`
- `GET /API/getKPInfo/{key_Cp}`
- `POST /API/Write_new_cp/{pages}/{user_id_tg}/{key_cp}`
- `POST /API/Write_createdKP/{pages}/{user_id}`
- `POST /API/Update_createdKP/{key}`
- `POST /API/RecognizeFiles/{id}`
- `GET /API/SearchInn_dadata/{inn}`
- `GET /API/SearchBic_dadata/{bic}`

## Что улучшить дальше

Рекомендуемые следующие шаги:

1. Собрать единый `config.py` / `settings.py` для всех env-переменных.
2. Убрать хардкод URL, токенов и путей из всех модулей.
3. Разбить слишком большие JS-файлы на меньшие модули.
4. Добавить `requirements.txt`, если он ещё не оформлен.
5. Добавить миграции БД через Alembic.
6. Написать отдельный README для frontend и отдельный README для API.

## Замечания по текущему README

В текущем варианте README:
- повторяется блок `# webapp / Quickstart / Backend / Таблицы` дважды;
- описание БД вставлено как сырой дамп схемы;
- нет инструкции по `.env`;
- нет описания интеграций и структуры проекта fileciteturn8file0

Поэтому этот README лучше использовать как обновлённую рабочую версию.
