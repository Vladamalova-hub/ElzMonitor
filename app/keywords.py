import re
import unicodedata


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", (value or "")).lower()
    text = text.replace("ё", "е")
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_keyword(value: str) -> str:
    return normalize_text(value)


RAW_KEYWORDS = [
    "елизово",
    "елизовский",
    "елизове",
    "елизова",
    "сокочи",
    "нагорный",
    "раздольный",
    "николаевка",
    "сосновка",
    "пионерский",
    "светлый поселок",
    "крутобереговый",
    "вулканный",
    "ганалы",
    "поселок дальний",
    "малки",
    "начики",
    "паратунка",
    "термальный",
    "коряки",
    "северные коряки",
    "поселок зеленый",
    "поселок новый",
    "поселок красный",
    "двуречье",
    "керкино",
    "пиначево",
    "лесной поселок",
    "березняки",
    "южные коряки",
]

KEYWORDS = sorted({normalize_keyword(item) for item in RAW_KEYWORDS if item.strip()})


def _matches_keyword(normalized_text: str, keyword: str) -> bool:
    if not keyword:
        return False
    if keyword in normalized_text:
        return True

    stem = keyword.rstrip("аоеиуыеййь")
    if stem and stem in normalized_text:
        return True

    if " " not in keyword:
        for suffix in ("ов", "ев", "ск", "ский", "ой", "ий", "ый", "ая", "ое", "ые"):
            if keyword.endswith(suffix) and len(keyword) > len(suffix):
                candidate = keyword[: -len(suffix)]
                if candidate and candidate in normalized_text:
                    return True
    return False


def find_keyword_hits(text: str):
    if not text:
        return []

    normalized = normalize_text(text)
    hits = []
    for keyword in KEYWORDS:
        if _matches_keyword(normalized, keyword):
            hits.append(keyword)
    return sorted(set(hits))
