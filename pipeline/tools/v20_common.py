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

GENERIC_RE = re.compile(r'^(stolpersteine?|stolperschwelle|stolpersteen|stolpersteine|struikelstenen?|struikelsteen|pierres? (d.|de )?achoppement|pav[ée]s? (de la m[ée]moire|d.achoppement)?|pietr[ae] d.inciampo|piedras? (de )?(tropiezo)|stolperstein|zlat[ýy] k[aá]men|potknutí k[aá]men|kamie[nń] pami[eę]ci|botl|k[ao]ste|[ck]ameni? spotik|spotikalni kamen|botlekamen|bot[li]e?kamen|st[oö]testen|forgyller|minnestein|snublestein|drag|stumbling stones?|botlestein|stein der erinnerung|stein zur erinnerung)\b[\s:,.\-–]*(?P<rest>.*)$', re.I)
PREFIX_FOR = re.compile(r'^(f[üu]r|voor|pour|per|dla|for|av|f[öo]r|til|til minne om|zum gedenken an|in memoriam|dedicated to|to|a|ter nagedachtenis aan|à la mémoire de|alla memoria di|na pamiątkę|na pamiatku|na památku|pro|za|pre|para|en memoria de|v spomin na|az? emlékére)\b[\s:,.\-–]*(?P<nm>.+)$', re.I)
COLLECTIVE_RE = re.compile(r'\b(familie|family|famille|familia|rodina|rodiny|rodzina|familj|familien|famiglia|gezin|mit familie|geschwister|brothers|sisters|siblings|geschwisterpaar|ehepaar|und kinder|\&|\bund\b|\bet\b|\bund\b| en | i | a )\b', re.I)

def clean_name(raw):
    """(nombre, motivo_si_no). Solo quita prefijos literales «Stolperstein für …»; nunca reconstruye un nombre."""
    n = (raw or '').strip()
    n = re.sub(r'\s+', ' ', n)
    n = re.sub(r'[\s|\[;,/:]+$', '', n); n = re.sub(r'^[\s|\]]+', '', n)   # v20r2: separadores sueltos («Hugo Lippers|», «Hergott[»)
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
        v = '%s:%s' % (m.group(1), unquote(m.group(2)).replace('_', ' '))
    elif not re.match(r'^([a-z]{2,3}(?:-[a-z]+)?):(.+)$', v): return None
    # v20r2: la página genérica sobre las piedras (no sobre la persona) no es un enlace de persona
    if re.fullmatch(r"(pietre d.inciampo|stolpersteine|stolperstein|struikelstenen|pierres? d.achoppement|stolpersteine in .*|liste der stolpersteine.*|lista (de )?(delle )?(pietre|piedras).*|kamienie pami[eę]ci|stolpersteine?)", v.split(':', 1)[1].strip(), re.I): return None
    return v

NUMBER_FIRST = {'FR', 'GB', 'GG', 'JE', 'IE', 'AD', 'LU', 'BE_FR'}

def compose_addr(street, hn, cc):
    street = (street or '').strip(); hn = (hn or '').strip()
    if not street: return None
    if not hn: return street
    return ('%s %s' % (hn, street)) if cc in NUMBER_FIRST else ('%s %s' % (street, hn))

def parse_memorial_addr(a):
    """memorial:addr «Calle 12, Ciudad» → (calle, número) cuando se puede leer sin adivinar; si no, (None, None)."""
    a = (a or '').strip()
    m = re.match(r'^(.*?[^\d,\s])[ ,]+(\d+(?:\s?[a-zA-Z](?![a-zA-Z]))?(?:[-/]\d+[a-zA-Z]?)?)(?:\s*,|$| )', a)   # v20r3 (B, W11): «25 A» (letra del portal separada por un espacio)
    if m: return m.group(1).strip(), re.sub(r'\s+', '', m.group(2))
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

# ---- v20r2 (auditoría B): nombres que no son una sola persona ----
NOT_PERSON_RE = re.compile(r'\b(hier|waren|wohnten|wohnte|stellvertretend|zwangsarbeit|festspiele|quartett|institut|blindeninstitut|kulturschaffenden|juedischen|menschen|vielen|opfern|oost polen|lager|suppenkuche|suppenkuchen|gemeinde|schulverein|verein|erinnerung|idokapszula|kapszula|capsule|stolpersteine|stolperstein|llambordes)\b|\b\w*(familie|verein|waisenhaus|bethaus|synagoge|kinderheim|altersheim|krankenhaus)\b|^a [a-z]')   # v20r3 (A/B ronda 2): Großfamilie, Turnverein, Waisenhaus, Bethaus…
COMMA_JUNK = re.compile(r'^(geb|geboren|nee|née|born|f|dit|alias|gen|genannt|jr|sr|dr|prof)\b', re.I)
def not_one_person(name):
    """Motivo (str) si el «nombre» no es UNA persona: varias personas («A & B», «A; B», «A, B», «...»), rótulo o institución; None si parece una persona."""
    n = (name or '').strip()
    if re.search(r'[;&]|\.\.\.|…', n): return 'el nombre junta a varias personas (%s)' % n[:70]
    segs = [s.strip() for s in n.split(',') if s.strip()]
    segs = [s for s in segs if not COMMA_JUNK.match(s)]
    if len(segs) >= 2 and all(len(toks(s)) >= 2 or len(s.split()) >= 2 for s in segs): return 'el nombre junta a varias personas separadas por comas (%s)' % n[:70]
    if re.match(r'^[A-Za-zÀ-ž]\.\s*[^\s.]+$', n): return 'el nombre es solo una inicial y un apellido (%s): no identifica a la persona' % n[:60]
    if NOT_PERSON_RE.search(norm(n)): return 'el «nombre» es un rótulo o una institución, no una persona (%s)' % n[:70]
    return None

def names_compatible(a, b):
    """Nombres de la misma persona: iguales (normalizados) o los tokens de uno (>= 2) son subconjunto de los del otro (segundo nombre, apellido de soltera)."""
    if norm(a) == norm(b): return True
    ta, tb = set(toks(a)), set(toks(b))
    sm, bg = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return len(sm) >= 2 and sm <= bg

_IGN = {'geb', 'geboren', 'born', 'nee', 'f', 'fod', 'fodt', 'urodzona', 'rozena', 'rozen', 'dit', 'dite', 'alias', 'the', 'of', 'family', 'dr', 'prof', 'jr', 'sr', 'med', 'ing', 'mag'}
def name_exact_in(name, text):
    """Estricto (auditoría A, F4): cada palabra del nombre (con partículas von/van/de…, ignorando grafía ß/diacríticos y mayúsculas) aparece TAL CUAL en la inscripción."""
    tk = [x for x in norm(name).split() if len(x) >= 2 and x not in _IGN]
    if not tk: return False
    words = set(norm(text).split())
    return all(x in words for x in tk)

COUNTRY_NAMES = {norm(x) for x in ('Belgium Belgique België Belgien Schweiz Suisse Svizzera Switzerland Svizra Česko Czechia Czech Republic Česká republika Ceska republika Nederland Netherlands The Netherlands Pays-Bas Niederlande France Frankreich Luxembourg Luxemburg Lëtzebuerg Deutschland Germany Allemagne Österreich Austria Autriche Italia Italy Italie España Spain Espagne Polska Poland Pologne Magyarország Hungary Hongrie Slovensko Slovakia Slovaquie Norge Norway Norvège Danmark Denmark Danemark Lietuva Lithuania Latvija Latvia Hrvatska Croatia Croatie Liechtenstein Andorra Guernsey Jersey United Kingdom UK Ireland Éire Sverige Sweden Suomi Finland România Romania').split() } | {norm(x) for x in ('Czech Republic', 'The Netherlands', 'United Kingdom', 'Česká republika')} | {norm(x) for x in 'CZ SK AT CH FR LU NL BE IT HU PL DK NO LV LT HR LI AD GG JE GB IE SE FI RO DE ES SI GR UA UK'.split()}   # v20r3 (A ronda 2): códigos ISO («…, Brno, CZ»)
STREET_RE = re.compile(r"^(rue|avenue|av\.?|boulevard|bd\.?|place|chemin|grand'?\s?rue|grande rue|route|impasse|all[ée]e|quai|square|cours|passage|sentier|faubourg|ruelle|rte|stra(ss|ß)e|weg|gasse|platz|laan|straat|plein|singel|gracht|via|viale|piazza|calle|plaza|ulice|ul\.|náměstí|namesti|utca|út|tér|ulica|iela|gatvė|lane|road|street)\b|(stra(ss|ß)e|straat|gasse|platz|weg|laan|ulice|utca|lane|road|street)$", re.I)
def bad_city(c):
    c = (c or '').strip()
    return (not c) or norm(c) in COUNTRY_NAMES or bool(STREET_RE.search(c)) or bool(re.search(r'\d', c))
def clean_city(c):
    c = re.sub(r'\s+(municipality|kommune|kommun)$', '', (c or '').strip(), flags=re.I)
    return c

def death_years(insc):
    """Años que la inscripción escribe junto a una palabra de muerte (ermordet/assassiné/zavražděn… + fecha, 45 caracteres después o, si no hay, antes en la misma línea)."""
    import sys as _s
    from pathlib import Path as _P
    _s.path.insert(0, str(_P(__file__).resolve().parents[2]))
    from pipeline.inscription import MURDERED, DIED, SUICIDE
    low = (insc or '').lower(); out = set()
    for rx in (MURDERED, DIED, SUICIDE):
        for m in rx.finditer(low):
            after = low[m.end(): m.end() + 45].split('\n')[0]
            ys = re.findall(r'\b(1[89]\d\d|20[0-2]\d)\b', after)
            if ys: out.add(ys[0]); continue
            line_start = low.rfind('\n', 0, m.start()) + 1
            ys = re.findall(r'\b(1[89]\d\d|20[0-2]\d)\b', low[max(line_start, m.start() - 45): m.start()])
            if ys: out.add(ys[-1])
    return out

def birth_year(s):
    if s.get('b'): return s['b'][:4]
    ys = sorted(years_in(s.get('i') or ''))
    return ys[0] if ys else None
def same_person_dup(s, t, maxm=15):
    """Misma persona: <= maxm m (lo comprueba quien llama), nombres compatibles y, si ambas traen año de nacimiento (campo b o el más antiguo de la inscripción), el mismo."""
    if not names_compatible(s['n'], t['n']): return False
    by1, by2 = birth_year(s), birth_year(t)
    return not (by1 and by2 and by1 != by2)


import re as _re2
def clean_pasted_tags(s):
    """v20r3 (A ronda 2, F9): etiquetas OSM pegadas dentro del texto de la inscripción («…memorial=stolperstein name=… network=…», «…1944historic=memorial»)."""
    return _re2.sub(r'\s*(?<![A-Za-z])(historic|memorial(?::\w+)?|network|name|stolperstein)=.*$', '', s or '', flags=_re2.S).strip()

def norm_date(v):
    """v20r3 (B ronda 2, R2-2): ISO aaaa[-mm[-dd]]; «23.04.1942» y «1884-1-29» se normalizan; «Jg. 1926» → 1926; «unknown», «unbek.», URLs… → ''."""
    v = (v or '').strip()
    if _re2.fullmatch(r'\d{4}(-\d\d(-\d\d)?)?', v): return v
    m = _re2.fullmatch(r'(\d{1,2})\.\s?(\d{1,2})\.\s?(\d{4})', v)
    if m: d, mo, y = int(m[1]), int(m[2]), m[3]
    else:
        m = _re2.fullmatch(r'(\d{4})-(\d{1,2})-(\d{1,2})', v)
        if m: y, mo, d = m[1], int(m[2]), int(m[3])
        else:
            m = _re2.fullmatch(r'Jg\.?\s*(\d{4})', v)
            return m[1] if m else ''
    if 1 <= mo <= 12 and 1 <= d <= 31: return '%s-%02d-%02d' % (y, mo, d)
    return ''


PERSECUTION_RE = re.compile(r'deport|internat|lager|camp\b|\bkz\b|auschwitz|theresienstadt|terez[ií]n|buchenwald|dachau|verfolg|flucht|vertrieb|persecut|rafle|r[eé]sist|widerstand|gestapo|nazi|shoah|holocaust|ermordet|assassin|zavra|vyhn', re.I)
def post1950_nonvictim(insc):
    """True si la inscripción solo habla de algo posterior a 1950 (ninguna fecha 1933-1945 ni palabra de persecución): no es una víctima del nazismo (v20r3)."""
    yi = [int(y) for y in years_in(insc)]
    return bool([y for y in yi if y > 1950]) and not any(1933 <= y <= 1945 for y in yi) and not PERSECUTION_RE.search(insc or '')
