"""v20: utilidades comunes (sin dependencias) para añadir países desde OSM (ODbL) y Wikidata (CC0). Nada se inventa:
solo se copian etiquetas o se lee literalmente la inscripción; cada exclusión lleva un motivo."""
import re, unicodedata, math
from difflib import SequenceMatcher

def norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.replace('ß', 'ss').replace('ł', 'l').replace('Ł', 'L').replace('ø', 'o').replace('Ø', 'O').replace('đ', 'd').replace('Đ', 'D').replace('æ', 'ae').replace('œ', 'oe')
    return re.sub(r'[^a-z0-9 ]+', ' ', s.lower()).strip()

STOP = {'born', 'geb', 'geboren', 'nee', 'nata', 'nato', 'nascuda', 'nascut', 'van', 'de', 'der', 'den', 'von', 'la', 'le', 'di', 'da', 'du', 'dos', 'del', 'el', 'dr', 'prof', 'und', 'and', 'et', 'née', 'f', 'fod', 'fodt', 'født', 'urodzona', 'rozena', 'rozen', 'rod', 'szul', 'szuletett', 'ben', 'bat', 'ibn', 'bint', 'jr', 'sr', 'dit', 'dite', 'alias', 'the', 'of', 'family'}

def toks(s):
    return [t for t in norm(s).split() if len(t) >= 3 and t not in STOP]

def tok_in(t, text_norm, words):
    if t in words: return True
    if len(t) >= 5:
        stem = t[:-2]
        if any(w.startswith(stem) or t.startswith(w) and len(w) >= 4 for w in words): return True
    if len(t) >= 5:   # grafías vecinas (Sigmund/Siegmund): solo si casi idénticas
        return any(abs(len(w) - len(t)) <= 1 and SequenceMatcher(None, t, w).ratio() >= 0.88 for w in words)
    return False

def name_in_text(name, text):
    """Fracción de los tokens significativos del nombre que aparecen (con flexión leve) en el texto."""
    tk = toks(name)
    if not tk: return 0.0
    tn = norm(text); words = set(tn.split())
    return sum(tok_in(t, tn, words) for t in tk) / len(tk)

GENERIC_RE = re.compile(r'^(stolpersteine?|stolperschwelle|stolpersteen|stolpersteine|struikelstenen?|struikelsteen|pierres? (d.|de )?achoppement|pav[ée]s? (de la m[ée]moire|d.achoppement)?|pietr[ae] d.inciampo|piedras? (de )?(tropiezo)|stolperstein|zlat[ýy] k[aá]men|potknutí k[aá]men|kamie[nń] pami[eę]ci|botl|k[ao]ste|[ck]ameni? spotik|spotikalni kamen|botlekamen|bot[li]e?kamen|st[oö]testen|forgyller|minnestein|snublestein|drag|stumbling stones?|botlestein)\b[\s:,.\-–]*(?P<rest>.*)$', re.I)
PREFIX_FOR = re.compile(r'^(f[üu]r|voor|pour|per|dla|for|av|f[öo]r|til|til minne om|zum gedenken an|in memoriam|dedicated to|to|a|ter nagedachtenis aan|à la mémoire de|alla memoria di|na pamiątkę|na pamiatku|na památku|pro|za|pre|para|en memoria de|v spomin na|az? emlékére)\b[\s:,.\-–]*(?P<nm>.+)$', re.I)
COLLECTIVE_RE = re.compile(r'\b(familie|family|famille|familia|rodina|rodiny|rodzina|familj|familien|famiglia|gezin|mit familie|geschwister|brothers|sisters|siblings|geschwisterpaar|ehepaar|und kinder|\&|\bund\b|\bet\b|\bund\b| en | i | a )\b', re.I)

def clean_name(raw):
    """(nombre, motivo_si_no). Solo quita prefijos literales «Stolperstein für …»; nunca reconstruye un nombre."""
    n = (raw or '').strip()
    n = re.sub(r'\s+', ' ', n)
    if not n: return None, 'sin nombre'
    m = GENERIC_RE.match(n)
    if m:
        rest = m.group('rest').strip()
        if not rest: return None, 'nombre genérico («%s»)' % n
        m2 = PREFIX_FOR.match(rest)
        if m2: n = m2.group('nm').strip()
        else: return None, 'nombre genérico con texto que no es un nombre (%s)' % n[:60]
    if re.search(r'\d', n): return None, 'el nombre contiene cifras (%s)' % n[:60]
    return n, None

def split_insc(t):
    t = (t or '').strip()
    if not t: return ''
    if '|' in t: t = re.sub(r'\s*\|\s*', '\n', t)
    elif t.count('/') >= 3: t = re.sub(r'\s*/\s*', '\n', t)
    elif '\\' in t: t = re.sub(r'\s*\\\\+\s*', '\n', t)
    t = re.sub(r'\n+', '\n', t).strip()
    return t

def date_ok(s):
    return bool(re.fullmatch(r'\d{4}(-\d{2}(-\d{2})?)?', (s or '').strip()))

def years_in(text):
    return set(re.findall(r'\b(1[89]\d\d|20[0-2]\d)\b', text or ''))

def parse_wp(v):
    v = (v or '').strip()
    m = re.match(r'https?://([a-z\-]+)\.wikipedia\.org/wiki/(.+)$', v)
    if m:
        from urllib.parse import unquote
        return '%s:%s' % (m.group(1), unquote(m.group(2)).replace('_', ' '))
    m = re.match(r'^([a-z]{2,3}(?:-[a-z]+)?):(.+)$', v)
    return v if m else None

NUMBER_FIRST = {'FR', 'GB', 'GG', 'JE', 'IE', 'AD', 'LU', 'BE_FR'}

def compose_addr(street, hn, cc):
    street = (street or '').strip(); hn = (hn or '').strip()
    if not street: return None
    if not hn: return street
    return ('%s %s' % (hn, street)) if cc in NUMBER_FIRST else ('%s %s' % (street, hn))

def parse_memorial_addr(a):
    """memorial:addr «Calle 12, Ciudad» → (calle, número) cuando se puede leer sin adivinar; si no, (None, None)."""
    a = (a or '').strip()
    m = re.match(r'^(.*?[^\d,\s])[ ,]+(\d+[a-zA-Z]?(?:[-/]\d+[a-zA-Z]?)?)(?:,|$| )', a)
    if m: return m.group(1).strip(), m.group(2)
    m = re.match(r'^(\d+[a-zA-Z]?)(?:,| )\s*([^\d,][^,]*)', a)
    if m: return m.group(2).strip(), m.group(1)
    return None, None

def street_sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b: return 0.0
    if a == b: return 1.0
    ta, tb = set(a.split()), set(b.split())
    j = len(ta & tb) / max(1, len(ta | tb))
    return max(SequenceMatcher(None, a, b).ratio(), j)

def hn_norm(h):
    return re.sub(r'\s+', '', (h or '').lower()).strip('.')

def hn_match(h, tag):
    h = hn_norm(h); parts = [hn_norm(x) for x in re.split(r'[;,/]', tag or '')] + [hn_norm(tag)]
    if h in parts: return True
    base = lambda x: re.fullmatch(r'(\d+)([a-z])?', x)   # 13 ↔ 13C: el mismo edificio con entradas/viviendas con letra
    bh = base(h)
    return bool(bh) and any((bp := base(p)) and bp.group(1) == bh.group(1) and (not bp.group(2) or not bh.group(2)) for p in parts)

POS_FIXME = re.compile(r'(position|posici|posit|location|lokal|standort|exact|verify|überprüf|lage|coord|ubicaci|placement|resurvey|check|postie)', re.I)
GONE_RE = re.compile(r'(entfernt|gestohlen|removed|stolen|gone|no longer|non essere pi|plus pr[ée]sent|disparu|verwijderd|gestolen|nicht mehr|missing|ukraden|odstraněn|odstranen|usunięt|nie istnieje|dům již neexistuje|dum jiz neexistuje|demolished|zničen|ukradnut)', re.I)


YEARS_RE = re.compile(r'^(?P<nm>.+?)\s*[\(\[]\s*(?:f\.|\*|b\.|geb\.)?\s*(?P<b>1[89]\d\d)\s*[-–—]\s*(?:d\.|\u2020)?\s*(?P<d>19[3-4]\d)\s*[\)\]]$')
def strip_years(raw):
    """«Herman Bild (1882-1942)» → («Herman Bild», '1882', '1942'). Solo años literales del título (nacimiento 1800–1929, muerte 1930–1949, vida ≤ 100 años); si no, no toca nada."""
    m = YEARS_RE.match((raw or '').strip())
    if m and int(m.group('d')) > int(m.group('b')) and int(m.group('d')) - int(m.group('b')) <= 100: return m.group('nm').strip(), m.group('b'), m.group('d')
    return raw, None, None
