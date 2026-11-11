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
# Supervivencia: se reconoce también como PREFIJO de palabra (überlebte, befreiten, versteckte, Fluchtweg…).
SURVIVAL_PREFIX = re.compile(_W + r"(überlebt|ueberlebt|uberlebt|gerettet|befreit|entkam|entkommen|versteckt)")
FLIGHT_PREFIX = re.compile(_W + r"(flucht|flücht|fluecht|geflohen|geflüchtet|gefluechtet|emigriert|ausgewandert)")
FLED = FLIGHT_PREFIX
DEPORTED = re.compile(_W + r"(deportiert|abgeschoben|ausgewiesen|polenaktion)" + _E)
IMPRISONED = re.compile(_W + r"(verhaftet|inhaftiert|zuchthaus|gefängnis|gefaengnis|kz|schutzhaft|lager)" + _E)
NEGATED_SURVIVAL = re.compile(r"(nicht|nur (eine|einer|eines)|keine?r?)\s+(überlebt|ueberlebt|uberlebt)")
# Muerte "débil" (tot, Tod, Todesmarsch, gestorben…) acompañada de fecha explícita: "tot 1942", "gestorben 3.4.1944".
DATED_DEATH = re.compile(_W + r"(tot|gestorben|starb|umgekommen|verstorben|für tot erklärt|fuer tot erklaert)" + _E
                         + r"[^|;]{0,40}?\b(\d{1,2}\.\s?\d{1,2}\.\s?)?(1[89]\d\d)\b")

ATTEMPT = re.compile(r"versucht\w*[\s/,.]+(?:die\s+|eine\s+)?(?:flucht in den tod|freitod|suizid|selbstmord)|(?:suizid|selbstmord)versuch\w*")

DEATH_FATES = {"murdered", "died_in_persecution", "suicide"}


def _clean(text):
    t = (text or "").lower()
    # Un intento ("versuchte Flucht in den Tod", "Suizidversuch") no es suicidio consumado.
    t = ATTEMPT.sub(" ", t)
    # "Flucht in den Tod" es suicidio: no es marca de huida ni de supervivencia.
    return t, t.replace("flucht in den tod", " ")


def has_survival_word(text):
    _, t = _clean(text)
    return bool(SURVIVAL_PREFIX.search(t)) and not NEGATED_SURVIVAL.search(t)


def has_survivor_marker(text):
    """Marca de posible superviviente (docs/legal regla 5): ÜBERLEBT/FLUCHT/BEFREIT/ENTKAM y variantes."""
    _, t = _clean(text)
    return bool(SURVIVAL_PREFIX.search(t) and not NEGATED_SURVIVAL.search(t)) or bool(FLIGHT_PREFIX.search(t))


def fate_from_text(text):
    """Devuelve (fate, basis) a partir de palabras escritas en la inscripción. Orden conservador.

    - Asesinato explícito (ermordet, hingerichtet, erschossen…) prevalece siempre.
    - Si hay marca de supervivencia/huida, las palabras de muerte débiles (tot, Tod, Todesmarsch, gestorben…)
      solo cuentan si llevan fecha explícita; si no, survived (überlebt/befreit/gerettet/entkam/versteckt) o fled.
    """
    raw, t = _clean(text)
    if not raw.strip():
        return "unknown", None
    if SUICIDE.search(raw):
        return "suicide", "inscription_text"
    if MURDERED.search(t):
        return "murdered", "inscription_text"
    survival = has_survival_word(t)
    flight = bool(FLIGHT_PREFIX.search(t))
    if survival or flight:
        if DATED_DEATH.search(t):
            return "died_in_persecution", "inscription_text"
        if MISSING.search(t):
            return "missing", "inscription_text"
        return ("survived" if survival else "fled"), "inscription_text"
    if DIED.search(t):
        return "died_in_persecution", "inscription_text"
    if MISSING.search(t):
        return "missing", "inscription_text"
    if DEPORTED.search(t):
        return "deported", "inscription_text"
    if IMPRISONED.search(t):
        return "imprisoned", "inscription_text"
    return "unknown", None


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
