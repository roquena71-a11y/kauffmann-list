"""Utilidades comunes: normalización, fechas, slugs y escritura JSON determinista."""
import json
import os
import re
import unicodedata

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(PIPELINE_DIR)

# Partículas que no cuentan para el apellido de ordenación/particionado.
NAME_PARTICLES = {"von", "van", "de", "der", "den", "zu", "zur", "vom", "ten", "ter", "da", "di", "del", "la", "le"}
TITLES = {"dr", "dr.", "prof", "prof.", "rabbiner", "rabbi", "dipl.-ing.", "ing.", "sanitätsrat", "justizrat"}


_TRANSLIT = str.maketrans({"ł": "l", "ø": "o", "đ": "d", "ð": "d", "þ": "th", "æ": "ae", "œ": "oe", "ı": "i"})


def fold(s):
    """Minúsculas sin acentos, igual que norm() del frontend (app3d.js), sin la regla de 'str'.

    ß→ss, umlauts→vocal base, ae/oe/ue→a/o/u, todo lo que no sea [a-z0-9] → espacio.
    """
    s = str(s or "").lower().replace("ß", "ss").replace("ä", "a").replace("ö", "o").replace("ü", "u")
    s = s.translate(_TRANSLIT)
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.replace("ae", "a").replace("oe", "o").replace("ue", "u")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()


def surname_key(family_name):
    """Clave de apellido normalizada (solo a-z) usada para particionar por prefijo.

    Se quitan partículas iniciales (von, van, de...) para que 'von Ossietzky' vaya a 'o'.
    """
    tokens = fold(family_name).split()
    while len(tokens) > 1 and tokens[0] in NAME_PARTICLES:
        tokens = tokens[1:]
    key = re.sub(r"[^a-z]", "", "".join(tokens))
    return key


def slugify(text, fallback="unknown"):
    """Slug ASCII igual que citySlug() del frontend."""
    s = unicodedata.normalize("NFKD", str(text or ""))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = re.sub(r"[^\x00-\x7F]", "", s)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:80] or fallback


def person_shard(person_id, chars=2):
    """Fragmento de una ficha completa: los `chars` últimos caracteres del id, en minúsculas.

    Regla trivial de calcular para un agente o para JS:
    id.slice(-2).toLowerCase().replace(/[^a-z0-9]/g, '_')
    """
    tail = person_id[-chars:].lower()
    tail = re.sub(r"[^a-z0-9]", "_", tail)
    return tail.rjust(chars, "_")


_MONTHS = {
    "jan": 1, "januar": 1, "january": 1, "feb": 2, "februar": 2, "february": 2, "mar": 3, "märz": 3, "maerz": 3,
    "march": 3, "apr": 4, "april": 4, "mai": 5, "may": 5, "jun": 6, "juni": 6, "june": 6, "jul": 7, "juli": 7,
    "july": 7, "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "okt": 10, "oct": 10, "oktober": 10,
    "october": 10, "nov": 11, "november": 11, "dez": 12, "dec": 12, "dezember": 12, "december": 12,
}


def _ymd(y, m=None, d=None):
    y = int(y)
    if not (1000 <= y <= 2100):
        return None
    if not m:
        return "%04d" % y
    m = int(m)
    if not (1 <= m <= 12):
        return "%04d" % y
    if not d:
        return "%04d-%02d" % (y, m)
    d = int(d)
    if not (1 <= d <= 31):
        return "%04d-%02d" % (y, m)
    return "%04d-%02d-%02d" % (y, m, d)


def normalize_date(value):
    """Convierte fechas variadas a ISO parcial (YYYY, YYYY-MM, YYYY-MM-DD). None si no es fecha."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    m = re.match(r"^[+]?(\d{4})(?:-(\d{1,2})(?:-(\d{1,2}))?)?(?:T.*)?$", s)
    if m:
        y, mo, d = m.groups()
        mo = mo if mo and int(mo) else None
        d = d if d and int(d) else None
        return _ymd(y, mo, d if mo else None)
    m = re.match(r"^(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})$", s)
    if m:
        return _ymd(m.group(3), m.group(2), m.group(1))
    m = re.match(r"^(\d{4})\.(\d{1,2})[.-](\d{1,2})$", s)
    if m:
        return _ymd(m.group(1), m.group(2), m.group(3))
    m = re.match(r"^(?:jg\.?|jahrgang)\s*(\d{4})$", s, re.I)
    if m:
        return _ymd(m.group(1))
    m = re.match(r"^(?:(\d{1,2})\.?\s+)?([A-Za-zäÄ]+)\.?\s+(\d{4})$", s)
    if m and m.group(2).lower() in _MONTHS:
        return _ymd(m.group(3), _MONTHS[m.group(2).lower()], m.group(1))
    return None


def date_year(value):
    if value and re.match(r"^\d{4}", str(value)):
        return int(str(value)[:4])
    return None


def clean_str(value):
    if value is None:
        return None
    s = re.sub(r"\s+", " ", str(value)).strip()
    return s or None


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path, obj, line_keys=()):
    """Escribe JSON determinista. Las listas cuyos nombres estén en line_keys van un elemento por línea
    (diffs de git limpios). Devuelve el número de bytes escritos."""
    parts = []
    keys = sorted(obj.keys())
    for i, k in enumerate(keys):
        v = obj[k]
        if k in line_keys and isinstance(v, list):
            if v:
                body = ",\n".join(dumps(x) for x in v)
                parts.append("%s:[\n%s\n]" % (dumps(k), body))
            else:
                parts.append("%s:[]" % dumps(k))
        else:
            parts.append("%s:%s" % (dumps(k), dumps(v)))
    text = "{" + ",\n".join(parts) + "}\n"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = text.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = text.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
