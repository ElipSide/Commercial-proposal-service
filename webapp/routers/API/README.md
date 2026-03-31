# 📘 API Документация (AJAX) — Калькулятор фотосепараторов

---
## 🔹 0. Основная ссылка 

### `https://csort-news.ru`

## 🔹 1. Получение справочников

### `GET /off_bot/API/getListData_Separ/{lang}`

Получение всех справочных данных для работы калькулятора.

**Параметры:**
- `lang`: `ru` | `en`

**Ответ:**
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

## 📌 Использование данных

### Список продуктов
```js
Product_List = уникальные значения Separ_perf.product
```

### Список назначений
```js
List_purpose = Separ_perf.filter(f => f.product == Product)
```

### Выбор параметров
```js
El_choice = Separ_perf.filter(f => 
    f.product == Product && f.purpose == Purpose
)[0]

Count_tray = performance/El_choice['performance_tray_per_t_h']

```

---

## 🔹 Основные параметры

- `performance` — производительность (т/ч)
- `sor` — исходная засоренность (%)
- `qual` — требуемое качество (%)

---

# 🔹 2. Расчёт расхода воздуха


### `POST /off_bot/API_CALC/Result_air`

Расчёт общего расхода воздуха.

**Вход:**
```json
{
  "sor": 5.5,
  "qual": 99.5,
  "performance": 9,
  "Count_tray": Count_tray,
  "El_choice": El_choice
}
```

**Ответ:**
```json
{
  "Result_air": 1234.5,
  "Count_tray": Count_tray,
  "air_flow_per_tray": 411.5
}
```

**Описание:**
- `Result_air` — общий расход воздуха  
- `air_flow_per_tray` — расход на 1 лоток  

---

# 🔹 3. Подбор фотосепараторов

### `POST /off_bot/API_CALC/GetInfoSepar/{lang}`

Подбор оборудования.

**Вход:**
```json
{
  "Product": "Пшеница",
  "Purpose": "Семена",
  "Count_tray": 3,
  "performance": 6,
  "choice_sorter": null
}
```

**Описание:**
- `choice_sorter = null` → авто подбор  
- `{id: count}` → ручной выбор  

---

## 📤 Ответ

```json
{
    "El_choice": {
        "id_row": 1,
        "product": "Пшеница",
        "segment": [
            "КФХ",
            "Семеновод"
        ],
        "purpose": [
            "Семена"
        ],
        "mass1000_per_gram": 40,
        "garbage": [
            "овсюг",
            "гречиха татарская",
            "проросшая пшеница"
        ],
        "garbage_percentage": 2,
        "quality_percentage": 99.99,
        "performance_tray_per_t_h": 2,
        "blow_per_m_sec": 2,
        "k_masses": 1.8,
        "pressure_per_bar": 3,
        "sep_config": "N+N(Extra light)",
        "calculated_performance": 6
    },
    "count_separ": 1,
    "loop_tray": 3,
    "Separators": [
        {
            "id_row": 96,
            "bitrix_id": "521529",
            "id_erp": "00-00000891#00000000166",
            "name": "Фотосепаратор СмартСорт 3.3",
            "name_print": "Фотосепаратор СмартСорт 3.3",
            "model_series": "3.3",
            "configuration": "N+N(Extra light)",
            "id_provider": 3,
            "price": 4266000,
            "photo": "SmartSort3_3.png",
            "height": 1900,
            "width": 1360,
            "depth": 1420,
            "additional_parameters": false,
            "additional_equipment": false,
            "tray": 3
        },
        {
            "id_row": 104,
            "bitrix_id": "480239",
            "id_erp": "00-00000682#00000000166",
            "name": "Фотосепаратор СмартСорт 3.3L",
            "name_print": "Фотосепаратор СмартСорт 3.3L",
            "model_series": "3.3L",
            "configuration": "N+N(Extra light)",
            "id_provider": 3,
            "price": 3879000,
            "photo": "SmartSort3_3L.png",
            "height": 1900,
            "width": 1360,
            "depth": 1420,
            "additional_parameters": false,
            "additional_equipment": false,
            "tray": 3
        }
    ],
    "dop_equipment": {
        "0": {
            "type": "Бункер",
            "model": "Бункер загрузочный разборный 3-х лотковый",
            "count": 1
        },
        "1": {
            "type": "Сходы",
            "model": "Комплект сходов для ф/с Смартсорт 3.YZ",
            "count": 1
        },
        "2": {
            "type": "Аспирация",
            "model": "Комплект аспирации для Смартсорт 3.YZ",
            "count": 1
        }
    },
    "group_info": { - то то с помощью чего потом получится получить кп 
        "extra_equipment": {
            "3": 1,
            "9": 1,
            "15": 1
        }
    }
}
```


## 📌 Поля ответа

### `Separators`
Список моделей

### `count_separ`
Количество машин

### `loop_tray`
Общее количество лотков

### `dop_equipment`
Дополнительное оборудование

### `group_info`
Используется для формирования КП

---

# 🔹 4. Подбор компрессора

### `POST /off_bot/API_CALC/calculate_compressor/{lang}`

**Вход:**
```json
{
  "Count_tray": 3,
  "Result_air": 1234.5,
  "air_flow_per_tray": 411.5,
  "Product": "Пшеница"
}
```

---

## 📤 Ответ

```json
{
    "compressors": [
        {
            "compressor": {
                "id_row": 4,
                "id_bitrix": 486371,
                "id_erp": "00-00001432#",
                "name": "Xeleron Z10A",
                "name_print": "Xeleron Dry T250 Z10A 8 бар",
                "produced_by": "Xeleron",
                "photo": "T250_Z10A_8.png",
                "price": 530000,
                "addit_params": true,
                "addit_equipment": false,
                "height": 1470,
                "width": 710,
                "depth": 1430,
                "id_provider": 3
            },
            "performance": {
                "id_row": 4,
                "name": "SLT-15V",
                "produced_by": "Sollant",
                "id": 4,
                "min_perf": 2050,
                "max_perf": 2390
            },
            "count": 1, - кол-во компрессоров
            "air_flow": 2010
        }
    ],
    "total_air_flow": 2010,
    "min_required_air": 2010,
    "warning": null,
    "equipment_data": [],
    "equipment_ids": {}
}
```

---

## 📌 Описание

- `compressors` — список компрессоров  
- `count` — количество  
- `air_flow` — расход  

- `total_air_flow` — общий поток  
- `min_required_air` — минимально допустимый  
- `warning` — предупреждение  

---

# 🔹 5. Сценарий работы

1. Получить справочники  
2. Выбрать продукт и назначение  
3. Рассчитать воздух  
4. Подобрать сепараторы  
5. Подобрать компрессор  
6. Использовать `group_info` для КП  

---

# 🔹 6. Важные замечания

- `El_choice` — ключевой объект  
- `group_info` — используется для формирования КП  
- расчёты завязаны на `Separ_perf`  
- компрессоры считаются после воздуха  

---

# 🔹 7. Рекомендации

- использовать `application/json`
- не менять структуру API
- проверять `warning`
