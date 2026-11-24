"""Extracción literal de datos de inscripciones de Stolpersteine (alemán; además palabras sueltas en sueco, inglés, finés y rumano, v18-v19).

Regla: solo se extrae lo que el texto dice; no se completa ni se infiere nada que no esté escrito.
"""
import re

from .util import normalize_date, clean_str

_W = r"(?<![a-zäöüß])"   # inicio de palabra (alemán)
_E = r"(?![a-zäöüß])"    # fin de palabra

SUICIDE = re.compile(_W + r"(flucht in den tod|freitod|suizid|selbstmord|nahm sich das leben|suicide)" + _E)
MURDERED = re.compile(_W + r"(ermordet|hingerichtet|erschossen|erhängt|erhaengt|getötet|getoetet|totgeschlagen|vergast|umgebracht|euthanasie|mördad|murdered|murhattiin|vermoord|geëxecuteerd|gefusilleerd|assassin[ée]e?s?|assassinat|fusill[ée]e?s?|zavražděn[aoiy]?|umučen[aoiy]?|popraven[aoiy]?|assassinat[oa]|uccis[oa]|fucilat[oa]|asesinad[oa]|fusilad[oa]|zamordowan[aoyi]?|rozstrzelan[aoyi]?|meggyilkolt|zavraždený|zavraždená|ubijen[aoi]?)" + _E)
DIED = re.compile(_W + r"(tot|gestorben|starb|umgekommen|verstorben|für tot erklärt|fuer tot erklaert|todesmarsch|tod|died|overleden|omgekomen|décédée?|decedut[oa]|mort|morte|morto|morta|muerto|muerta|fallecid[oa]|murió|zemřel[a]?|zahynul[a]?|zmarł[a]?|zginął|zginęła|zomrel[a]?|meghalt)" + _E)
MISSING = re.compile(_W + r"(verschollen|schicksal unbekannt|öde okänt)" + _E)
# Supervivencia: se reconoce también como PREFIJO de palabra (überlebte, befreiten, versteckte, Fluchtweg…).
SURVIVAL_PREFIX = re.compile(_W + r"(überlebt|ueberlebt|uberlebt|gerettet|befreit|entkam|entkommen|versteckt|survived|liberated|liberared|released|vapautui|supravie|eliberat|surv[eé]cu|lib[eé]r[eé]|rescap|[eé]chapp|[eé]vad|overleefd|overleefde|bevrijd|ondergedoken|sopravviss|liberat|scampat|sobreviv|liberad|rescatad|przeżył|przezyl|ocalał|ocalal|uwolnion|přežil|prezil|osvobozen|prežil|oslobod|túlél|megmenek|szabadul|preživ|oslobođ|pobegnil|overlevde|overlevede|befridd|befriet|izdzīvoj|atbrīvo|sobrevisqu|επιζ|вижив|врятува|iwwerlieft)")
FLIGHT_PREFIX = re.compile(_W + r"(flucht|flücht|fluecht|geflohen|geflüchtet|gefluechtet|emigriert|ausgewandert|flydde|fled|pakeni|fuite|fui[st]|escaped|ontsnapt|gevlucht|vlucht|fuga|fuggit|huy[óo]|escap|uciek|uciec|uprchl|emigrova|ušiel|utiekol|emigrir|menekül|pobjeg|pobeg|flyktet|flygtede|aizbēg|pabēg|втік|εγκατέλ|emigrat|emigrer|emigré|exil)")
FLED = FLIGHT_PREFIX
DEPORTED = re.compile(_W + r"(deportiert|abgeschoben|ausgewiesen|polenaktion|deporterad|deported)" + _E)
IMPRISONED = re.compile(_W + r"(verhaftet|inhaftiert|zuchthaus|gefängnis|gefaengnis|kz|schutzhaft|lager|imprisoned|interned)" + _E)
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


# --- Fechas literales de la inscripción (v25): solo lo que el texto escribe; no se infiere. ---

from .util import date_year

# Palabras de nacimiento, además de jg./geb./geboren (sueco, inglés, finés, rumano, francés, checo, polaco, neerlandés).
_BIRTH_LEAD = (
    r"(?:jg\.?|jahrgang|geb(?:oren)?\.?|geboren\s+am|"
    r"born|född|født|fodt|née|nee|"
    r"născut[ăa]?|nascut[ao]?|nascuda|nascut|"
    r"urodzon[ay]|rozen[ay]|rozen|"
    r"s\.(?=\s*\d)|"  # finés «s. 1941», solo si sigue un número
    r"\*)"
)
_BIRTH_NUM = re.compile(
    r"(?i)(?:^|[\s|,;/])" + _BIRTH_LEAD + r"\s*(?:am\s+)?(?:(\d{1,2})\.\s*(\d{1,2})\.\s*)?(\d{4})\b"
)
_BIRTH_MONTH = re.compile(
    r"(?i)(?:^|[\s|,;/])" + _BIRTH_LEAD + r"\s*(?:am\s+)?(?:(\d{1,2})\.?\s+)?([A-Za-zÄÖÜäöüß]+)\.?\s+(\d{4})\b"
)

_DEP_LEAD = re.compile(
    r"(?i)\b(deportiert|abgeschoben|ausgewiesen|deporterad|deported|deportata|deportata|"
    r"deportata|deportat[oa]|déporté[es]?|deportata|verschleppt|luovutettiin)\b"
)

# Fechas numéricas o con mes, en una ventana corta alrededor de una palabra clave.
_NUM_DATE = re.compile(r"\b(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})\b")
_YEAR_ONLY = re.compile(r"\b((?:1[7-9]|20)\d{2})\b")
_MONTH_DATE = re.compile(
    r"\b(?:(\d{1,2})\.?\s+)?([A-Za-zÄÖÜäöüß]+)\.?\s+(\d{4})\b", re.I
)


def _month_date(text):
    from .util import _MONTHS, _ymd
    out = []
    for m in _MONTH_DATE.finditer(text or ""):
        mon = (m.group(2) or "").lower().rstrip(".")
        if mon not in _MONTHS:
            continue
        out.append((_ymd(m.group(3), _MONTHS[mon], m.group(1)), m.group(0).strip(), m.start(), m.end()))
    return out


def _numeric_dates(text):
    from .util import _ymd
    out = []
    for m in _NUM_DATE.finditer(text or ""):
        out.append((_ymd(m.group(3), m.group(2), m.group(1)), m.group(0).strip(), m.start(), m.end()))
    return out


def _years_span(text, start, end):
    """Fechas y años en text[start:end], más precisas primero."""
    chunk = text[start:end]
    found = _numeric_dates(chunk) + _month_date(chunk)
    # Ajustar offsets al texto completo
    adj = [(v, raw, start + a, start + b) for v, raw, a, b in found]
    if adj:
        return adj
    out = []
    for m in _YEAR_ONLY.finditer(chunk):
        y = m.group(1)
        out.append((y, y, start + m.start(), start + m.end()))
    return out


def _unique_values(pairs):
    """Lista de valores normalizados en orden de aparición, sin repetir el mismo año compatible."""
    seen, vals = set(), []
    for v, raw, *_ in pairs:
        if not v:
            continue
        key = date_year(v)
        if key in seen:
            # Si llega una fecha más precisa del mismo año, se sustituye.
            for i, prev in enumerate(vals):
                if date_year(prev[0]) == key and len(v) > len(prev[0]):
                    vals[i] = (v, raw)
                    break
            continue
        seen.add(key)
        vals.append((v, raw))
    return vals


def _birth_matches(text):
    from .util import _MONTHS, _ymd
    t = text or ""
    hits = []
    for m in _BIRTH_NUM.finditer(t):
        d, mo, y = m.group(1), m.group(2), m.group(3)
        val = _ymd(y, mo, d) if mo else y
        hits.append((val, m.group(0).strip(), m.start(), m.end()))
    for m in _BIRTH_MONTH.finditer(t):
        mon = (m.group(2) or "").lower().rstrip(".")
        if mon not in _MONTHS:
            continue
        val = _ymd(m.group(3), _MONTHS[mon], m.group(1))
        hits.append((val, m.group(0).strip(), m.start(), m.end()))
    return hits


def _death_windows(text):
    """Ventanas de fecha ligadas a una palabra de muerte (o †).

    Primero se mira *después* de la palabra, en la misma línea (hasta 45 caracteres).
    Solo si ahí no hay fecha se acepta una fecha que preceda de inmediato
    («12.9.1939 MÖRDAD»), no un año más atrás en la frase (evita tomar el
    nacimiento en «BORN 1870 … SUICIDE 9.4.1944»).
    """
    raw = text or ""
    low = raw.lower()
    after, before = [], []

    def add_mark(start, end):
        line_end = raw.find("\n", end)
        if line_end < 0:
            line_end = len(raw)
        line_start = raw.rfind("\n", 0, start) + 1
        after.append((end, min(line_end, end + 45), start))
        # Fecha inmediatamente anterior (solo espacios).
        chunk = raw[line_start:start]
        m = re.search(r"((?:\d{1,2}\.\s*\d{1,2}\.\s*\d{4})|(?:\d{1,2}\.?\s+[A-Za-zÄÖÜäöüß]+\.?\s+\d{4})|(?:(?:1[7-9]|20)\d{2}))\s*$", chunk)
        if m:
            before.append((line_start + m.start(), start, start))

    for m in re.finditer(r"†", raw):
        add_mark(m.start(), m.end())
    for rx in (SUICIDE, MURDERED, DIED):
        for m in rx.finditer(low):
            add_mark(m.start(), m.end())
    return after, before


def _deportation_windows(text):
    raw = text or ""
    low = raw.lower()
    spans = []
    for m in _DEP_LEAD.finditer(low):
        line_end = low.find("\n", m.end())
        if line_end < 0:
            line_end = len(low)
        spans.append((m.start(), min(line_end, m.end() + 60), m.start()))
    return spans


def inscription_event_dates(text):
    """Fechas de nacimiento, muerte y deportación leídas de la inscripción.

    Devuelve un dict con claves birth, death, deportation. Cada una es:
      {value, raw, all: [(value, raw), ...]}
    value es una fecha ISO parcial, o None si no hay ninguna o si hay años distintos
    (en ese caso all tiene todas y no se elige en silencio).
    """
    t = text or ""
    out = {}

    def pack(role, hits):
        uniq = _unique_values(hits)
        years = {date_year(v) for v, _ in uniq}
        years.discard(None)
        if not uniq:
            return
        if len(years) > 1:
            out[role] = {"value": None, "raw": None, "all": uniq, "ambiguous": True}
        else:
            # La más precisa del único año.
            best = max(uniq, key=lambda x: len(x[0]))
            out[role] = {"value": best[0], "raw": best[1], "all": uniq, "ambiguous": False}

    birth_hits = _birth_matches(t)
    pack("birth", birth_hits)
    birth_spans = [(a, b) for _v, _r, a, b in birth_hits]

    def not_birth(hits):
        out = []
        for v, raw, a, b in hits:
            if any(a < bb and b > aa for aa, bb in birth_spans):
                continue
            out.append((v, raw, a, b))
        return out

    after, before = _death_windows(t)
    death_hits = []
    for a, b, _ in after:
        death_hits.extend(_years_span(t, a, b))
    death_hits = not_birth(death_hits)
    if not death_hits:
        for a, b, _ in before:
            death_hits.extend(_years_span(t, a, b))
        death_hits = not_birth(death_hits)
    pack("death", death_hits)

    dep_hits = []
    for a, b, _ in _deportation_windows(t):
        dep_hits.extend(_years_span(t, a, b))
    pack("deportation", dep_hits)
    return out


def dates_conflict(structured, insc_value):
    """True si ambos tienen año y el año no coincide.

    structured / insc_value son fechas ISO parciales o None.
    Un año (1870) frente a una fecha del mismo año (1870-01-09) no es conflicto.
    """
    ys, yi = date_year(structured), date_year(insc_value)
    return bool(ys and yi and ys != yi)


def dates_day_conflict(structured, insc_value):
    """True si ambos tienen fecha completa (día) del mismo año, pero el día o el mes no coinciden."""
    if not structured or not insc_value:
        return False
    if date_year(structured) != date_year(insc_value):
        return False
    if len(str(structured)) < 10 or len(str(insc_value)) < 10:
        return False
    return str(structured)[:10] != str(insc_value)[:10]
