"""
Распознавание голосовых сообщений и fallback-обогащение JSON по номенклатуре.

Вход:
- аудио/voice из Telegram, текст распознавания и JSON-представление позиций.

Выход:
- transcript, enriched JSON и подобранные атрибуты оборудования.
"""

import asyncio
import json
import re
import subprocess
import time
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import websockets

from env_settings import get_settings


SETTINGS = get_settings()
VOICE_UPLOAD_URL = SETTINGS.voice_upload_url
VOICE_WS_STATUS_URL_TPL = SETTINGS.voice_ws_status_url_tpl


# =========================
# Voice transcription
# =========================

_CFG_CYR_MAP = str.maketrans({
    "с": "c", "С": "C",
    "н": "n", "Н": "N",
})

def _norm_cfg(s: Any) -> str:
    x = str(s or "").strip()
    x = x.translate(_CFG_CYR_MAP)
    x = x.replace(" ", "")
    x = x.lower()
    return x


def _ensure_dirs() -> Dict[str, Path]:
    base = Path("process")
    audio_dir = base / "audio_files"
    audio_dir.mkdir(parents=True, exist_ok=True)
    return {"audio_dir": audio_dir}


def _normalize_to_wav_16k_mono(input_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_wav = out_dir / (input_path.stem + "_norm.wav")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(out_wav),
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError as e:
        raise RuntimeError("ffmpeg не найден. Установи: sudo apt-get install -y ffmpeg") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError("ffmpeg не смог конвертировать файл в WAV.") from e

    return out_wav


async def transcribe_voice_message(
    bot,
    message,
    status_message=None,
    *,
    upload_url: Optional[str] = None,
    ws_status_url_tpl: Optional[str] = None,
) -> Optional[str]:
    """
    Вход:
    - bot/message/status_message и опциональные URL сервиса распознавания.

    Выход:
    - строка transcript или None, если распознать аудио не удалось.
    """
    upload_url = upload_url or VOICE_UPLOAD_URL
    ws_status_url_tpl = ws_status_url_tpl or VOICE_WS_STATUS_URL_TPL

    dirs = _ensure_dirs()
    audio_dir = dirs["audio_dir"]

    async def _set_status(text: str, parse_mode: Optional[str] = None):
        try:
            if status_message:
                await status_message.edit_text(text, parse_mode=parse_mode)
        except Exception:
            pass

    file_obj = message.voice or message.audio
    if not file_obj:
        await _set_status("ℹ️ Пришли голосовое или аудиофайл.")
        return None

    await _set_status("Получаю файл для обработки…")

    file_id = file_obj.file_id
    tg_file = await bot.get_file(file_id)

    if message.voice:
        original_name = f"voice_{message.from_user.id}.ogg"
    else:
        original_name = getattr(file_obj, "file_name", None) or f"audio_{message.from_user.id}.bin"
        if "." not in original_name:
            original_name += ".bin"

    raw_path = audio_dir / f"raw_{int(time.time())}_{original_name}"

    try:
        try:
            await bot.download_file(tg_file.file_path, destination=raw_path)
        except TypeError:
            await bot.download_file(tg_file.file_path, raw_path)
    except Exception:
        await _set_status("⚠️ Не удалось скачать файл из Telegram.")
        return None

    if not raw_path.exists() or raw_path.stat().st_size == 0:
        await _set_status("⚠️ Файл скачался пустым, попробуй ещё раз.")
        return None

    await _set_status("Готовлю аудио…")

    try:
        wav_path = _normalize_to_wav_16k_mono(raw_path, audio_dir)
    except Exception:
        await _set_status("⚠️ Не удалось подготовить WAV.")
        try:
            raw_path.unlink(missing_ok=True)
        except Exception:
            pass
        return None
    finally:
        try:
            raw_path.unlink(missing_ok=True)
        except Exception:
            pass

    if not wav_path.exists() or wav_path.stat().st_size == 0:
        await _set_status("⚠️ WAV файл пустой.")
        return None

    await _set_status("Распознаю речь…")

    try:
        with wav_path.open("rb") as f:
            resp = requests.post(upload_url, files={"file": f}, timeout=360)
        resp.raise_for_status()
        task_id = resp.json().get("task_id")
    except Exception:
        await _set_status("⚠️ Сервер распознавания недоступен.")
        try:
            wav_path.unlink(missing_ok=True)
        except Exception:
            pass
        return None

    if not task_id:
        await _set_status("⚠️ Сервер перегружен. Попробуй позже.")
        try:
            wav_path.unlink(missing_ok=True)
        except Exception:
            pass
        return None

    ws_url = ws_status_url_tpl.format(task_id=task_id)

    def _extract_result_text(payload: Dict[str, Any]) -> str:
        txt = payload.get("result_text")
        if isinstance(txt, str) and txt.strip():
            return txt
        for key in ("text", "transcript", "result"):
            v = payload.get(key)
            if isinstance(v, str) and v.strip():
                return v
            if isinstance(v, dict):
                for sub in ("text", "result_text", "transcript"):
                    sv = v.get(sub)
                    if isinstance(sv, str) and sv.strip():
                        return sv
        msg = payload.get("message")
        if isinstance(msg, str) and msg.strip():
            return msg
        return ""

    result_text: Optional[str] = None
    last_progress = -1
    last_message = ""

    max_retries = 10
    retry_count = 0

    try:
        while retry_count < max_retries and not result_text:
            try:
                async with websockets.connect(ws_url) as websocket:
                    while True:
                        ws_msg = await websocket.recv()
                        data = json.loads(ws_msg)

                        status = data.get("status", "")
                        progress = int(data.get("progress", 0) or 0)
                        msg_txt = data.get("message", "") or ""

                        if status_message and (progress != last_progress or msg_txt != last_message):
                            await _set_status(
                                f"Обработка… {progress}%\n{msg_txt}",
                                parse_mode=None,
                            )
                            last_progress = progress
                            last_message = msg_txt

                        if status == "completed":
                            extracted = _extract_result_text(data)
                            result_text = extracted.strip() if extracted else None
                            break

                        if status == "failed":
                            await _set_status("⚠️ Не удалось обработать аудио.")
                            return None

            except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.WebSocketException):
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(1)
                    continue
                await _set_status("⚠️ Ошибка соединения с сервером распознавания.")
                return None

    except Exception:
        await _set_status("⚠️ Ошибка распознавания.")
        return None
    finally:
        try:
            wav_path.unlink(missing_ok=True)
        except Exception:
            pass

    return (result_text or "").strip() or None


# =========================
# Fallback extraction (product/capacity)
# =========================

_CAPACITY_RE = re.compile(
    r"(?P<val>\d+(?:[.,]\d+)?)\s*(?:т/ч|тн/ч|тонн(?:ы)?\s*в\s*час|тонн(?:ы)?)\b",
    re.IGNORECASE,
)

PRODUCTS_CANONICAL: Dict[str, str] = {
    "пшеница": "Пшеница",
    "лен": "Лен",
    "лён": "Лен",
    "гречка": "Гречиха",
    "гречиха": "Гречиха",
    "рапс": "Рапс",
    "ячмень": "Ячмень",
    "овес": "Овес",
    "овёс": "Овес",
    "горох": "Горох",
    "чечевица": "Чечевица",
    "соя": "Соя",
    "просо": "Просо",
    "кофе": "Кофе",
    "подсолнечник": "Подсолнечник (масличный)",
    "семечка": "Подсолнечник (масличный)",
}


PURPOSES_BY_PRODUCT: Dict[str, List[str]] = {
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

# Для fallback-распознавания назначений — простые стемы/синонимы.
_PURPOSE_STEMS = {
    "Семена": ["семен", "семя"],
    "Товарная": ["товар", "товарн"],
    "Товарный": ["товар", "товарн"],
    "Товарное": ["товар", "товарн"],
    "Фураж": ["фураж", "корм"],
    "Мука": ["мук"],
    "Крупа": ["круп"],
    "Макароны": ["макарон", "паста"],
    "Хлеб": ["хлеб", "пекар"],
    "Масло": ["масл"],
    "Фасовка": ["фасов", "упаков"],
    "Солод": ["солод", "пив"],
    "Жарщик": ["жарщик", "обжар", "жарен"],
    "Халва": ["халв"],
    "Ядро": ["ядро", "ядрышк"],
    "Зеленый": ["зелен", "зелё"],
    "Жареный": ["жарен", "обжар"],
}

def _fallback_extract_purpose(transcript: str, product: Optional[str]) -> Optional[str]:
    if not transcript:
        return None
    if not product:
        return None

    allowed = PURPOSES_BY_PRODUCT.get(product) or []
    if not allowed:
        return None

    t = _normalize_text(transcript)

    # Пытаемся найти явное упоминание назначения из allowed (по стемам).
    for p in allowed:
        stems = _PURPOSE_STEMS.get(p, [])
        for st in stems:
            if st and st in t:
                return p

    # Если не уточнили — дефолт "Семена" (если допустимо), иначе первый допустимый.
    if "Семена" in allowed:
        return "Семена"
    return allowed[0] if allowed else None

_PRODUCT_PATTERNS = [
    r"пшениц[аы]", r"л[её]н", r"гречк[аи]", r"гречих[аи]", r"рапс",
    r"ячмен[ья]", r"ов[её]с", r"горох", r"чечевиц[аы]", r"со[яи]",
    r"просо", r"кофе", r"подсолнечник", r"семечк[аи]",
]


def _normalize_product(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    return PRODUCTS_CANONICAL.get(raw.lower().strip())


def _fallback_extract_product_and_capacity(transcript: str) -> Dict[str, Any]:
    t = (transcript or "").lower()

    product: Optional[str] = None
    for pattern in _PRODUCT_PATTERNS:
        mm = re.search(pattern, t)
        if not mm:
            continue
        raw = mm.group(0).lower()

        if "подсолнечник" in raw or "семечк" in raw:
            if "кондитер" in t:
                product = "Подсолнечник (кондитерский)"
            else:
                product = "Подсолнечник (масличный)"
        else:
            product = _normalize_product(raw)

        if product:
            break

    capacity = None
    m = _CAPACITY_RE.search(transcript or "")
    if m:
        raw_val = m.group("val").replace(",", ".")
        try:
            capacity = float(raw_val)
        except Exception:
            capacity = None

    purpose = _fallback_extract_purpose(transcript, product)

    return {"product": product, "capacity_tph": capacity, "purpose": purpose}


def enrich_ds_json_with_fallback(ds_json_str: str, transcript: str) -> str:
    try:
        data = json.loads(ds_json_str)
    except Exception:
        return ds_json_str

    fb = _fallback_extract_product_and_capacity(transcript)
    items = data.get("items")

    if isinstance(items, list):
        for it in items:
            if not isinstance(it, dict):
                continue
            if it.get("product") in (None, "", "null") and fb.get("product"):
                it["product"] = fb["product"]
            if it.get("capacity_tph") in (None, "", "null") and fb.get("capacity_tph") is not None:
                it["capacity_tph"] = fb["capacity_tph"]
            if it.get("purpose") in (None, "", "null") and fb.get("purpose"):
                it["purpose"] = fb["purpose"]

        cfg = extract_photo_sorter_configuration(transcript)

        comp_model = extract_compressor_model(transcript)

        for it in items:
            if not isinstance(it, dict):
                continue

            # photo_sorter configuration
            if it.get("type_key") == "photo_sorter" and not it.get("configuration") and cfg:
                it["configuration"] = cfg

            # compressor model (если LLM не вытащил)
            if it.get("type_key") == "compressor" and not it.get("model") and comp_model:
                it["model"] = comp_model

    return json.dumps(data, ensure_ascii=False)


# =========================
# Matching utils
# =========================

def _normalize_text(s: str) -> str:
    s = (s or "").lower().strip()
    s = s.replace("ё", "е")
    s = re.sub(r"\s+", " ", s)
    return s


def _similarity(a: str, b: str) -> float:
    a_n = _normalize_text(a)
    b_n = _normalize_text(b)
    if not a_n or not b_n:
        return 0.0
    return SequenceMatcher(None, a_n, b_n).ratio()


def _norm(s: Any) -> str:
    return str(s or "").strip()


def _unique(seq: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in seq:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def _try_float(x: str) -> Optional[float]:
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return None


# =========================
# Photo models: base first, then suffix
# =========================

_BASE_MODEL_RE = re.compile(r"^\d+(?:\.\d+)?$")


def _norm_model(s: Any) -> str:
    x = str(s or "").strip().lower()
    x = x.replace(",", ".")
    return x


def get_available_models(records: List[Dict[str, Any]]) -> List[str]:
    base_models = set()
    extended_models = set()

    for r in records or []:
        raw = r.get("model_series")
        if not raw:
            continue
        model_lc = _norm_model(raw)
        if not model_lc:
            continue

        if _BASE_MODEL_RE.match(model_lc):
            base_models.add(model_lc)
        else:
            extended_models.add(model_lc)

    def _model_sort_key(m: str):
        num = re.findall(r"\d+(?:\.\d+)?", m)
        num = float(num[0]) if num else 0.0
        suffix = re.sub(r"[\d.]", "", m)
        return (num, suffix)

    return sorted(base_models, key=_model_sort_key) + sorted(extended_models, key=_model_sort_key)


def find_by_model_series(group_records: List[Dict[str, Any]], model: str) -> List[Dict[str, Any]]:
    m = _norm_model(model)
    if not m:
        return []
    return [rec for rec in (group_records or []) if _norm_model(rec.get("model_series")) == m]


def get_available_configurations(records: List[Dict[str, Any]]) -> List[str]:
    cfgs: List[str] = []
    for r in records or []:
        cfg = _norm(r.get("configuration"))
        if cfg:
            cfgs.append(cfg)
    return sorted(_unique(cfgs))


def pick_by_configuration(
    model_records: List[Dict[str, Any]],
    configuration: Optional[str],
    default_cfg: str = "C+C",
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    if not model_records:
        return None, []

    cfgs_raw = get_available_configurations(model_records)
    cfg_in_norm = _norm_cfg(configuration)
    default_norm = _norm_cfg(default_cfg)

    if not cfg_in_norm:
        # если не указали — пробуем дефолт
        for r in model_records:
            if _norm_cfg(r.get("configuration")) == default_norm:
                return r, cfgs_raw
        return model_records[0], cfgs_raw

    # точное совпадение (в нормализованном виде)
    for r in model_records:
        if _norm_cfg(r.get("configuration")) == cfg_in_norm:
            return r, cfgs_raw

    # если не нашли — дефолт
    for r in model_records:
        if _norm_cfg(r.get("configuration")) == default_norm:
            return r, cfgs_raw

    return model_records[0], cfgs_raw

def extract_photo_sorter_configuration(text: str) -> Optional[str]:
    raw = (text or "").strip()
    if not raw:
        return None

    t = raw.translate(_CFG_CYR_MAP).lower().replace(" ", "")

    # CN+CN / C+C / C+CN
    if "cn+cn" in t:
        return "CN+CN"
    if "c+c" in t:
        return "C+C"
    if "c+cn" in t:
        # если явно написали extra light / light / легкий
        t2 = _normalize_text(raw)
        if "extra" in t or "light" in t or "легк" in t2:
            return "C+CN(Extra light)"
        # если не уточнили — оставляем короткий вариант
        # (если в базе нет такого — пойдёт в подсказки)
        return "C+CN"

    return None

_QTY_RE = re.compile(r"\b(\d+)\s*(?:шт|штук|штуки)\b", re.IGNORECASE)

def extract_compressor_model(text: str) -> Optional[str]:
    raw = (text or "").strip()
    if not raw:
        return None

    qty = None
    mqty = _QTY_RE.search(raw)
    if mqty:
        try:
            qty = int(mqty.group(1))
        except Exception:
            qty = None

    # 1) сначала ищем токены с буквами+цифрами (SLT-18.5V, Z40A, CA5.5-8GA-300DRY)
    tokens = re.findall(r"\b[0-9A-Za-zА-Яа-я][0-9A-Za-zА-Яа-я\-\.,/]*\b", raw)
    cand = []
    for tok in tokens:
        if not re.search(r"\d", tok):
            continue
        if tok.isdigit() and qty is not None and int(tok) == qty:
            continue
        cand.append(tok)

    # отдаём “самый похожий на модель” (обычно последний)
    if cand:
        chosen = cand[-1].replace(",", ".")
        return chosen

    # 2) если остались только числа — берём последнее число, не равное qty
    nums = re.findall(r"\b\d+(?:[.,]\d+)?\b", raw)
    nums = [n.replace(",", ".") for n in nums]
    if qty is not None:
        nums = [n for n in nums if n != str(qty)]
    return nums[-1] if nums else None

# =========================
# Compressors: choose by manufacturer + model token
# =========================

_MFR_ALIASES = {
    "соллант": "sollant",
    "sollant": "sollant",
    "кселерон": "xeleron",
    "xeleron": "xeleron",
    "кросс": "cross air",
    "кросс эйр": "cross air",
    "cross air": "cross air",
    "cross": "cross air",
    "экселют": "exelute",
    "exelute": "exelute",
}

def _norm_comp(s: Any) -> str:
    x = str(s or "").strip().lower()
    x = x.replace("ё", "е").replace(",", ".")
    x = re.sub(r"\s+", " ", x)
    return x

def _norm_mfr(s: Any) -> str:
    x = _norm_comp(s)
    for k, v in _MFR_ALIASES.items():
        if k in x:
            return v
    return x

def _compressor_label(rec: Dict[str, Any]) -> str:
    return _norm(rec.get("name") or rec.get("name_print") or "")

def _compressor_model_token(rec: Dict[str, Any]) -> str:
    name = _norm_comp(rec.get("name") or rec.get("name_print") or "")
    if not name:
        return ""
    return name.split()[-1]  # SLT-18.5V / Z40A / CA5.5-8GA-300DRY

def get_available_compressors(records: List[Dict[str, Any]], manufacturer: Optional[str] = None) -> List[str]:
    mfr = _norm_mfr(manufacturer) if manufacturer else ""
    same: List[str] = []
    other: List[str] = []

    for r in records or []:
        label = _compressor_label(r)
        if not label:
            continue
        produced_by = _norm_mfr(r.get("produced_by") or "")
        if mfr and (mfr in produced_by or _similarity(mfr, produced_by) >= 0.6):
            same.append(label)
        else:
            other.append(label)

    # если производитель указан — отдаём только его модели (без мусора)
    if mfr:
        return _unique(same)

    return _unique(same) + _unique(other)

def find_compressor_by_model(
    records: List[Dict[str, Any]],
    manufacturer: Optional[str],
    model: str,
) -> Optional[Dict[str, Any]]:
    mfr = _norm_mfr(manufacturer) if manufacturer else ""
    mdl = _norm_comp(model)

    if not mdl:
        return None

    # сузим по производителю если он есть
    cand = []
    for r in records or []:
        produced_by = _norm_mfr(r.get("produced_by") or "")
        if mfr and not (mfr in produced_by or _similarity(mfr, produced_by) >= 0.6):
            continue
        cand.append(r)

    if not cand:
        cand = records or []

    best = None
    best_score = 0.0

    for r in cand:
        token = _compressor_model_token(r)
        name = _norm_comp(r.get("name") or "")
        namep = _norm_comp(r.get("name_print") or "")

        if token and token == mdl:
            score = 1.0
        elif mdl and (mdl in name or mdl in namep):
            score = 0.85
        else:
            score = max(_similarity(mdl, token), _similarity(mdl, name), _similarity(mdl, namep))

        if score > best_score:
            best_score = score
            best = r

    return best if best_score >= 0.55 else None


# =========================
# Main enrichment
# =========================

def enrich_ds_json_with_nomenclature(ds_json_str: str, nomenclature_data: Dict[str, Any]) -> str:
    try:
        data = json.loads(ds_json_str)
    except Exception:
        return ds_json_str

    items = data.get("items")
    if not isinstance(items, list):
        return json.dumps(data, ensure_ascii=False)

    for it in items:
        if not isinstance(it, dict):
            continue

        if it.get("nomenclature_id_erp") or it.get("nomenclature_name"):
            continue

        type_key = it.get("type_key")
        group_key = it.get("type_key_db")
        if not type_key or not group_key:
            continue

        group_records = nomenclature_data.get(group_key)
        if not isinstance(group_records, list) or not group_records:
            continue

        # -------------------------
        # PHOTO SORTERS
        # -------------------------
        if type_key == "photo_sorter":
            user_model = _norm(it.get("model"))
            user_cfg = it.get("configuration")

            if user_model:
                model_records = find_by_model_series(group_records, user_model)
                if not model_records:
                    it["nomenclature_error"] = "model_not_found"
                    it["nomenclature_model"] = user_model
                    it["nomenclature_suggestions_models"] = get_available_models(group_records)[:20]
                    continue

                chosen, cfgs = pick_by_configuration(model_records, user_cfg, default_cfg="C+C")
                if not chosen:
                    continue

                if not _norm(user_cfg):
                    it["configuration"] = "C+C"

                if _norm(user_cfg) and _norm(user_cfg) not in cfgs:
                    it["nomenclature_warning"] = "configuration_not_found_used_default"
                    it["nomenclature_suggestions_configurations"] = cfgs

                it["nomenclature_name"] = chosen.get("name") or chosen.get("name_print")
                it["nomenclature_model_series"] = chosen.get("model_series")
                it["nomenclature_configuration"] = chosen.get("configuration")
                it["nomenclature_id_row"] = chosen.get("id_row")
                it["nomenclature_id_erp"] = chosen.get("id_erp")
                it["nomenclature_id_bitrix"] = chosen.get("id_bitrix")
                continue

            it["nomenclature_error"] = "model_not_specified"
            it["nomenclature_suggestions_models"] = get_available_models(group_records)[:20]
            continue

        # -------------------------
        # COMPRESSORS
        # -------------------------
        if type_key == "compressor":
            user_model = _norm(it.get("model"))
            user_mfr = _norm(it.get("manufacturer"))

            if not user_model:
                it["nomenclature_error"] = "model_not_specified"
                it["nomenclature_suggestions_models"] = get_available_compressors(group_records, user_mfr)[:20]
                continue

            rec = find_compressor_by_model(group_records, user_mfr, user_model)
            if not rec:
                it["nomenclature_error"] = "model_not_found"
                it["nomenclature_model"] = user_model
                it["nomenclature_suggestions_models"] = get_available_compressors(group_records, user_mfr)[:20]
                continue

            id_bitrix = rec.get("id_bitrix")
            if id_bitrix is None:
                id_bitrix = rec.get("bitrix_id")

            it["nomenclature_name"] = rec.get("name_print") or rec.get("name")
            it["nomenclature_id_erp"] = rec.get("id_erp")
            it["nomenclature_id_bitrix"] = id_bitrix
            it["nomenclature_id_row"] = rec.get("id_row")
            it["nomenclature_group"] = group_key
            continue

        # -------------------------
        # OTHER GROUPS: simple fuzzy by name
        # -------------------------
        q = _normalize_text(_norm(it.get("model")) + " " + _norm(it.get("manufacturer")))
        if not q.strip():
            continue

        best_rec = None
        best_score = 0.0

        for rec in group_records:
            name = rec.get("name") or rec.get("name_print")
            if not isinstance(name, str) or not name.strip():
                continue
            score = _similarity(q, name)
            if score > best_score:
                best_score = score
                best_rec = rec

        if best_rec and best_score >= 0.55:
            it["nomenclature_name"] = best_rec.get("name_print") or best_rec.get("name")
            it["nomenclature_id_erp"] = best_rec.get("id_erp")
            it["nomenclature_id_bitrix"] = best_rec.get("id_bitrix")
            it["nomenclature_id_row"] = best_rec.get("id_row")
            it["nomenclature_group"] = group_key
            it["nomenclature_score"] = round(best_score, 3)

    return json.dumps(data, ensure_ascii=False)
