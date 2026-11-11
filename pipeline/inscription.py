"""Extracción literal de datos de inscripciones de Stolpersteine (alemán).

Regla: solo se extrae lo que el texto dice; no se completa ni se infiere nada que no esté escrito.
"""
import re

from .util import normalize_date, clean_str

_W = r"(?<![a-zäöüß])"   # inicio de palabra (alemán)
_E = r"(?![a-zäöüß])"    # fin de palabra

SUICIDE = re.compile(_W + r"(flucht in den tod|freitod|suizid|selbstmord|nahm sich das leben)" + _E)
MURDERED = re.compile(_W + r"(ermordet|hingerichtet|erschossen|erhängt|erhaengt|getötet|getoetet|totgeschlagen|vergast|umgebracht|euthanasie)" + _E)
DIED = re.compile(_W + r"(tot|gestorben|starb|umgekommen|verstorben|für tot erklärt|fuer tot erklaert|todesmarsch|tod)" + _E)
MISSING = re.compile(_W + r"(verschollen|schicksal unbekannt)" + _E)
SURVIVED = re.compile(_W + r"(überlebt|ueberlebt|uberlebt|befreit|entkam|entkommen)" + _E)
FLED = re.compile(_W + r"(flucht|geflohen|geflüchtet|gefluechtet|flüchtete|fluechtete|emigriert|ausgewandert|entkam|entkommen)" + _E)
DEPORTED = re.compile(_W + r"(deportiert|abgeschoben|ausgewiesen|polenaktion)" + _E)
IMPRISONED = re.compile(_W + r"(verhaftet|inhaftiert|zuchthaus|gefängnis|gefaengnis|kz|schutzhaft|lager)" + _E)
NEGATED_SURVIVAL = re.compile(r"(nicht|nur (eine|einer|einer?s?)|keine?r?)\s+(überlebt|ueberlebt|uberlebt)")

# Marcadores que la política de datos trata como "posible superviviente" (docs/legal: regla 5).
SURVIVOR_MARKERS = re.compile(_W + r"(überlebt|ueberlebt|uberlebt|flucht|flüchtete|fluechtete|geflohen|geflüchtet|befreit|entkam|entkommen)" + _E)

DEATH_FATES = {"murdered", "died_in_persecution", "suicide"}


def fate_from_text(text):
    """Devuelve (fate, basis) a partir de palabras clave de la inscripción. Orden conservador."""
    t = (text or "").lower()
    if not t.strip():
        return "unknown", None
    if SUICIDE.search(t):
        return "suicide", "inscription_text"
    if MURDERED.search(t):
        return "murdered", "inscription_text"
    t_no_flight_death = t.replace("flucht in den tod", "")
    if DIED.search(t_no_flight_death):
        return "died_in_persecution", "inscription_text"
    if MISSING.search(t):
        return "missing", "inscription_text"
    if SURVIVED.search(t) and not NEGATED_SURVIVAL.search(t):
        return "survived", "inscription_text"
    if FLED.search(t_no_flight_death):
        return "fled", "inscription_text"
    if DEPORTED.search(t):
        return "deported", "inscription_text"
    if IMPRISONED.search(t):
        return "imprisoned", "inscription_text"
    return "unknown", None


def has_survivor_marker(text):
    t = (text or "").lower().replace("flucht in den tod", "")
    return bool(SURVIVOR_MARKERS.search(t))


_BIRTHNAME = re.compile(r"\b(?:geb\.|geborene?|geb)\s*([A-ZÄÖÜa-zäöüß][\wÄÖÜäöüß'\-]+)", re.I)


def _nice_case(word):
    if word and word.isupper() and len(word) > 1:
        return word[0] + word[1:].lower()
    return word


def birth_name_from(text):
    m = _BIRTHNAME.search(text or "")
    if not m:
        return None
    w = m.group(1).strip("-'")
    if w.lower() in ("am", "im", "in", "jg", "den", "1", "geb"):
        return None
    return _nice_case(w)


def split_name(raw):
    """Separa el nombre mostrado y el apellido de nacimiento explícito ('geb. X').
    No inventa nombre/apellido: solo corta en 'geb.' / 'verh.' cuando está escrito."""
    raw = clean_str(raw)
    if not raw:
        return None, None
    if re.search(r"genid|https?://", raw):
        return None, None
    birth = birth_name_from(raw)
    display = re.split(r"\s*,?\s*\b(?:geb\.|geborene?\b|verh\.|verheiratete?\b)", raw, flags=re.I)[0].strip(" ,")
    return display or raw, birth


_DEP_EVENT = re.compile(r"(\d{1,2}\.\s?\d{1,2}\.\s?\d{4}|(?:\d{1,2}\.\s?)?(?:jan|feb|märz|maerz|apr|mai|juni?|juli?|aug|sept?|okt|nov|dez)[a-zä]*\.?\s+\d{4}|\d{4})\s+([^\d]+?)(?=\s+(?:\d|$)|$)", re.I)


def deportations_from(text, source_id):
    """Eventos de deportación literales: [{date, place, raw}]."""
    raw = clean_str(text)
    if not raw:
        return []
    body = re.sub(r"^\s*(deportiert|abgeschoben|ausgewiesen)\s*", "", raw, flags=re.I)
    events = []
    for m in _DEP_EVENT.finditer(body):
        place = clean_str(m.group(2).strip(" ,;/"))
        if place and re.match(r"^(und|nach|in|über|ueber|ins)\b", place, re.I):
            place = clean_str(re.sub(r"^(und|nach|in|über|ueber|ins)\s+", "", place, flags=re.I))
        events.append({"date": normalize_date(m.group(1).replace(" ", "")) or normalize_date(m.group(1)),
                       "place": place, "raw": raw if not events else None, "source_id": source_id})
    if not events:
        events.append({"date": None, "place": None, "raw": raw, "source_id": source_id})
    return events


_DEATH_PLACE = re.compile(r"\b(?i:ermordet|tot|gestorben|umgekommen|starb|hingerichtet|erschossen)\b[^.]*?\b(?i:in)\s+([A-ZÄÖÜ][\wÄÖÜäöüß\-/ ]+?)\s*(?:$|\d|,|\.|\|)")


def death_place_from(text):
    m = _DEATH_PLACE.search(text or "")
    if not m:
        return None
    place = clean_str(m.group(1))
    if place and place.isupper():
        place = " ".join(_nice_case(w) for w in place.split())
    return place


_JG = re.compile(r"\b(?:jg\.?|jahrgang|geb\.?|geboren)\s*(?:\d{1,2}\.\s?\d{1,2}\.\s?)?(\d{4})\b", re.I)


def birth_year_from_inscription(text):
    m = _JG.search(text or "")
    return m.group(1) if m else None
