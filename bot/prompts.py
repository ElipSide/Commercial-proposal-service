"""
Промпты и вызовы DeepSeek для двух задач:
1) извлечение оборудования из текста,
2) маршрутизация действий пользователя внутри черновика КП.

Вход:
- текст пользователя и короткий контекст сессии.

Выход:
- строго JSON-структуры для дальнейшей обработки ботом.
"""

import json
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from env_settings import get_settings


SETTINGS = get_settings()


TYPE_MACHINE_TO_GROUP: Dict[str, str] = {
    "sep_machine": "machine",
    "photo_sorter": "photoMachine",
    "compressor": "kompressor",
    "extra_equipment": "extra_equipment",
    "service": "Service",
    "elevator": "Elevator",
    "Pneumatic_feed": "Pneumatic_feed",
    # Псевдо-тип: это НЕ оборудование, а распознанные параметры для расчёта
    "calc_params": "calc_params",
}

EQUIPMENT_CATEGORIES_RU: Dict[str, str] = {
    "sep_machine": "Решетные машины",
    "photo_sorter": "Фотосепараторы",
    "elevator": "Транспортное оборудование",
    "Pneumatic_feed": "Пневмоподача",
    "compressor": "Компрессоры",
    "extra_equipment": "Дополнительное оборудование",
    "service": "Сервис",
    "services": "Услуги",
    "calc_params": "Параметры расчёта",
}


def _strip_code_fences(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[-1]
        if s.endswith("```"):
            s = s[:-3]
    return s.strip()


def _safe_json_load(s: str) -> Optional[dict]:
    try:
        s2 = _strip_code_fences(s)
        obj = json.loads(s2)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def build_equipment_prompt(transcript: str) -> Dict[str, str]:
    """Вход: transcript пользователя. Выход: system/user prompt для извлечения оборудования."""
    system = (
        "Ты — ассистент-менеджер компании Csort. "
        "По сообщению пользователя извлекай либо позиции для коммерческого предложения (оборудование/услуги), "
        "либо параметры для расчёта (продукт/назначение/производительность). "
        "Отвечай СТРОГО JSON, без markdown и без пояснений."
    )

    product_list: List[str] = [
        "Пшеница",
        "Лен",
        "Гречиха",
        "Рапс",
        "Ячмень",
        "Овес",
        "Горох",
        "Чечевица",
        "Соя",
        "Подсолнечник (кондитерский)",
        "Подсолнечник (масличный)",
        "Просо",
        "Кофе",
    ]

    # Назначения (purpose) зависят от продукта — список из твоей таблицы.
    # ВАЖНО: purpose в ответе должен быть строкой (одно выбранное значение), НЕ списком.
    purposes_by_product: Dict[str, List[str]] = {
        "Пшеница": ["Семена", "Товарная", "Фураж", "Мука", "Крупа", "Макароны", "Хлеб"],
        "Лен": ["Семена", "Масло", "Фасовка"],
        "Гречиха": ["Семена", "Крупа", "Товарная"],
        "Рапс": ["Семена", "Масло"],
        "Ячмень": ["Семена", "Крупа", "Солод", "Товарный", "Фураж"],
        "Овес": ["Семена", "Крупа", "Товарный", "Фураж"],
        "Горох": ["Семена", "Крупа", "Товарный", "Фураж"],
        "Чечевица": ["Семена", "Крупа", "Товарная"],
        "Соя": ["Семена", "Мука", "Масло", "Товарная"],
        "Подсолнечник (кондитерский)": ["Семена", "Жарщик", "Халва", "Товарный", "Ядро"],
        "Подсолнечник (масличный)": ["Масло", "Товарный", "Семена"],
        "Просо": ["Семена", "Крупа", "Товарное"],
        "Кофе": ["Зеленый", "Жареный"],
    }

    user = f"""
Определи, что просит пользователь:

A) Позиции КП (оборудование/услуги) — тогда возвращай items с реальными type_key оборудования.
B) Параметры расчёта (продукт / производительность / назначение) — тогда возвращай ОДИН item с type_key="calc_params".

КРИТИЧЕСКОЕ ПРАВИЛО:
Если пользователь указывает ТОЛЬКО:
- продукт (из списка)
- и/или производительность (т/ч)
- и/или назначение (purpose)
и НЕ указывает:
- модель фотосепаратора (например 1.1 / 2.2 / 3.3L / 1.1H и т.п.)
- конфигурацию (C+C, C+CN, CN+CN, N+N, ...)

ТО:
❌ НЕ НУЖНО подбирать оборудование
❌ НЕ НУЖНО возвращать type_key="photo_sorter"
✅ Нужно вернуть ТОЛЬКО параметры расчёта: type_key="calc_params"

Категории оборудования (используй ТОЛЬКО если есть явная модель/конфигурация/кол-во оборудования):
- Фотосепараторы -> type_key: photo_sorter -> type_key_db: {TYPE_MACHINE_TO_GROUP['photo_sorter']}
- Компрессоры -> type_key: compressor -> type_key_db: {TYPE_MACHINE_TO_GROUP['compressor']}
- Решетные машины -> type_key: sep_machine -> type_key_db: {TYPE_MACHINE_TO_GROUP['sep_machine']}
- Транспортное оборудование -> type_key: elevator -> type_key_db: {TYPE_MACHINE_TO_GROUP['elevator']}
- Пневмоподача -> type_key: Pneumatic_feed -> type_key_db: {TYPE_MACHINE_TO_GROUP['Pneumatic_feed']}
- Доп. оборудование -> type_key: extra_equipment -> type_key_db: {TYPE_MACHINE_TO_GROUP['extra_equipment']}
- Сервис/услуги -> type_key: service -> type_key_db: {TYPE_MACHINE_TO_GROUP['service']}

ВАЖНО:
- Всегда возвращай type_key="service" (не "services"), даже если пользователь пишет “услуги”.
- Верни только JSON (никаких ``` и текста вокруг).

Поля (для ЛЮБОГО item):

1) manufacturer (строка или null)
Нормализуй производителя:
- "соллант" / "sollant" -> "Sollant"
- "кселерон" / "xeleron" -> "Xeleron"
- "кросс эйр" / "cross air" / "cross" -> "Cross Air"
- "exelute" / "экселют" / "екселют" -> "EXELUTE"

2) model (строка или null)
Правила:
- Фотосепараторы: приводи к виду "2.2", "2.2L", "1.1H" (точка вместо запятой, суффиксы L/H сохраняй).
  Примеры: "2,2l" -> "2.2L", "1.1h" -> "1.1H", "3,3" -> "3.3".
- Компрессоры: модель как в названии серии, например "SLT-18.5V", "Z40A", "CA5,5-8GA-300DRY".
  Если пользователь пишет "Sollant 15" или "соллант 15", нормализуй к "SLT-15V".
  Если "Sollant 18.5" -> "SLT-18.5V".
  Если пользователь написал уже "SLT-15V" — оставь как есть.

3) configuration (строка или null) — только для фотосепараторов
Нормализуй варианты:
- "c+c" / "C + C" / "с+с" -> "C+C"
- "cn+cn" / "CN+CN" / "сн+сн" -> "CN+CN"
- "c+cn" / "C+CN" / "с+сн" -> "C+CN"
- если пользователь дополнительно говорит "extra light" или "легкий/лёгкий" -> добавь "(Extra light)", например "C+CN(Extra light)"
Если конфигурация не указана — null.

4) qty (целое число или null)
- "5 шт", "3 штуки", "2 штук" -> qty=5/3/2
- если количества нет — null

Параметры расчёта (используются, когда type_key="calc_params"):

5) product (строка или null)
- Только из списка: {product_list}
- Если продукта нет или он не из списка — null

6) capacity_tph (число или null)
- "10 т/ч" или "10 тонн в час" -> 10.0
- "8-12 т/ч" -> среднее 10.0
- если нет — null

7) purpose (строка или null)
- Назначение выбирай ТОЛЬКО из списка, который зависит от product:
{json.dumps(purposes_by_product, ensure_ascii=False)}
- Если purpose не указано пользователем:
  - попытайся поставить "Семена" (если оно есть в списке для данного продукта),
  - иначе поставь первое значение из списка для данного продукта (например для "Кофе" это "Зеленый").
- Если product=null — purpose=null.

8) confidence (число 0..1)
- приблизительная уверенность, 0.0 если совсем не уверен.

Примеры:

Пример 1 (параметры расчёта, БЕЗ оборудования):
Вход: "подбери оборудование пшеница 5 т/ч семена"
Выход: type_key="calc_params", product="Пшеница", capacity_tph=5.0, purpose="Семена", model=null, configuration=null, qty=null

Пример 2 (есть модель — значит это оборудование):
Вход: "добавь фотосепаратор 3.3L для пшеницы"
Выход: type_key="photo_sorter", model="3.3L", product="Пшеница" (если есть), capacity_tph=null (если нет), purpose=null (если не сказано)

Верни строго JSON в формате:

{{
  "items":[
    {{
      "type_key":"calc_params|photo_sorter|compressor|sep_machine|elevator|Pneumatic_feed|extra_equipment|service",
      "type_key_db":"calc_params|{TYPE_MACHINE_TO_GROUP['photo_sorter']}|{TYPE_MACHINE_TO_GROUP['compressor']}|{TYPE_MACHINE_TO_GROUP['sep_machine']}|{TYPE_MACHINE_TO_GROUP['elevator']}|{TYPE_MACHINE_TO_GROUP['Pneumatic_feed']}|{TYPE_MACHINE_TO_GROUP['extra_equipment']}|{TYPE_MACHINE_TO_GROUP['service']}",
      "name_ru":null,
      "manufacturer":null,
      "model":null,
      "configuration":null,
      "qty":null,
      "product":null,
      "capacity_tph":null,
      "purpose":null,
      "confidence":0.0
    }}
  ]
}}

Текст пользователя:
{transcript}
"""
    return {"system": system, "user": user}


async def deepseek_extract_equipment(transcript: str) -> Optional[str]:
    """Вход: текст пользователя. Выход: raw JSON-ответ DeepSeek или None."""
    api_key = SETTINGS.deepseek_api_key
    if not api_key:
        return None

    prompts = build_equipment_prompt(transcript)
    client = AsyncOpenAI(api_key=api_key, base_url=SETTINGS.deepseek_base_url)

    try:
        resp = await client.chat.completions.create(
            model=SETTINGS.deepseek_chat_model,
            messages=[
                {"role": "system", "content": prompts["system"]},
                {"role": "user", "content": prompts["user"]},
            ],
            stream=False,
            timeout=60,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        return None


def build_action_prompt(user_text: str, context: Dict[str, Any]) -> Dict[str, str]:
    """Вход: сообщение пользователя и контекст КП. Выход: prompt для классификации intent."""
    system = (
        "Ты — ассистент-менеджер, который ведёт диалог и управляет черновиком КП. "
        "Твоя задача: определить намерение пользователя (intent) и параметры для действия. "
        "Отвечай СТРОГО JSON, без markdown."
    )

    # context очень короткий: чтобы LLM понимал, что есть в КП
    ctx_items = context.get("kp_items_brief", [])
    ctx_last = context.get("last_item_brief", "")

    user = f"""
Определи intent и параметры. Возможные intent:
- "add" (пользователь хочет добавить оборудование)
- "set_qty" (поменять количество: "сделай 7", "надо 3 шт", "поставь 5")
- "remove" (удалить строку: "убери 2", "удали 1")
- "show_kp" (покажи КП)
- "get_kp" (получить/сформировать КП)
- "cancel_kp" (отменить/очистить КП)
- "unknown" (неясно)

Правила:
- "сделай 7" без уточнений -> set_qty на последнюю позицию (scope="last")
- "фотосепараторов надо 3 шт" -> set_qty (scope="type", type_key="photo_sorter")
- "компрессоров 2 шт" -> set_qty (scope="type", type_key="compressor")
- "убери 2" -> remove, remove_index=2
- "покажи кп" -> show_kp
- "получить кп" -> get_kp
- "отменить кп" -> cancel_kp

Вывод JSON:
{{
  "intent":"add|set_qty|remove|show_kp|get_kp|cancel_kp|unknown",
  "qty": null,
  "remove_index": null,
  "target": {{
    "scope": "last|type|index|unknown",
    "type_key": null,
    "index": null
  }}
}}

Контекст:
- Последняя позиция: "{ctx_last}"
- КП сейчас ({len(ctx_items)} поз): {ctx_items}

Сообщение пользователя:
{user_text}
"""
    return {"system": system, "user": user}


async def deepseek_extract_action(user_text: str, context: Dict[str, Any]) -> Optional[dict]:
    """Вход: сообщение пользователя и короткий контекст КП. Выход: dict intent или None."""
    api_key = SETTINGS.deepseek_api_key
    if not api_key:
        return None

    prompts = build_action_prompt(user_text, context)
    client = AsyncOpenAI(api_key=api_key, base_url=SETTINGS.deepseek_base_url)

    try:
        resp = await client.chat.completions.create(
            model=SETTINGS.deepseek_chat_model,
            messages=[
                {"role": "system", "content": prompts["system"]},
                {"role": "user", "content": prompts["user"]},
            ],
            stream=False,
            timeout=30,
        )
        raw = (resp.choices[0].message.content or "").strip()
        return _safe_json_load(raw)
    except Exception:
        return None
