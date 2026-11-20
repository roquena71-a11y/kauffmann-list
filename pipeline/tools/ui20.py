#!/usr/bin/env python3
"""v20: textos de la interfaz generados desde los países que hay en data/stones.json (nombres es/de/en, palabras de búsqueda, listas en meta/JSON-LD/llms).
Parte siempre de los archivos de HEAD (v19), así que se puede repetir. Uso: ui20.py"""
import json, re, subprocess
from pathlib import Path
R = Path(__file__).resolve().parents[2]
NAMES = {  # cc: (es, de, en, palabras extra de búsqueda)
 'DE': ('Alemania', 'Deutschland', 'Germany', ''), 'IE': ('Irlanda', 'Irland', 'Ireland', ''), 'SE': ('Suecia', 'Schweden', 'Sweden', ''), 'JE': ('Jersey', 'Jersey', 'Jersey', ''),
 'FI': ('Finlandia', 'Finnland', 'Finland', 'suomi'), 'RO': ('Rumanía', 'Rumänien', 'Romania', 'rumania romania'), 'LV': ('Letonia', 'Lettland', 'Latvia', 'latvija'),
 'SK': ('Eslovaquia', 'Slowakei', 'Slovakia', 'slovensko'), 'AD': ('Andorra', 'Andorra', 'Andorra', ''), 'GG': ('Guernsey', 'Guernsey', 'Guernsey', ''),
 'LI': ('Liechtenstein', 'Liechtenstein', 'Liechtenstein', ''), 'GB': ('Reino Unido', 'Vereinigtes Königreich', 'United Kingdom', 'uk gran bretana great britain england escocia scotland'),
 'LU': ('Luxemburgo', 'Luxemburg', 'Luxembourg', 'letzebuerg'), 'PL': ('Polonia', 'Polen', 'Poland', 'polska'), 'SI': ('Eslovenia', 'Slowenien', 'Slovenia', 'slovenija'),
 'BE': ('Bélgica', 'Belgien', 'Belgium', 'belgique belgie'), 'CH': ('Suiza', 'Schweiz', 'Switzerland', 'suisse svizzera'), 'DK': ('Dinamarca', 'Dänemark', 'Denmark', 'danmark'),
 'GR': ('Grecia', 'Griechenland', 'Greece', 'hellas'), 'HR': ('Croacia', 'Kroatien', 'Croatia', 'hrvatska'), 'HU': ('Hungría', 'Ungarn', 'Hungary', 'magyarorszag'),
 'UA': ('Ucrania', 'Ukraine', 'Ukraine', ''), 'ES': ('España', 'Spanien', 'Spain', 'espana'), 'IT': ('Italia', 'Italien', 'Italy', ''),
 'AT': ('Austria', 'Österreich', 'Austria', 'osterreich oesterreich'), 'FR': ('Francia', 'Frankreich', 'France', ''), 'NL': ('Países Bajos', 'Niederlande', 'Netherlands', 'holanda holland nederland'),
 'CZ': ('Chequia', 'Tschechien', 'Czechia', 'republica checa czech republic cesko'), 'NO': ('Noruega', 'Norwegen', 'Norway', 'norge'), 'LT': ('Lituania', 'Litauen', 'Lithuania', 'lietuva'),
}
# app3d.js parte de 7f726e0 (grupos fijos de v20); lo demás, de la v19 (49e7725)
def head(p): return subprocess.run(['git', 'show', ('7f726e0:' if p == 'app3d.js' else '49e7725:') + p], cwd=R, capture_output=True, text=True, check=True).stdout
def main():
    S = json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']
    from collections import Counter
    cnt = Counter((s.get('cc') or 'DE') for s in S)
    order = ['DE'] + sorted([c for c in cnt if c != 'DE'], key=lambda c: -cnt[c])
    missing = [c for c in order if c not in NAMES]; assert not missing, missing
    def lst(i, conj):
        n = [NAMES[c][i] for c in order]
        return ', '.join(n[:-1]) + ' ' + conj + ' ' + n[-1]
    es, de, en = lst(0, 'y'), lst(1, 'und'), lst(2, 'and'); k = len(order) - 1
    short = {'es': 'Alemania y otros %d países de Europa' % k, 'de': 'Deutschland und %d weiteren Ländern Europas' % k, 'en': 'Germany and %d other European countries' % k}
    OLD = {'es': 'Alemania, Irlanda, Suecia, Jersey, Finlandia y Rumanía', 'de': 'Deutschland, Irland, Schweden, Jersey, Finnland und Rumänien', 'en': 'Germany, Ireland, Sweden, Jersey, Finland and Romania'}
    a = head('app3d.js')
    cn = {i: '{' + ','.join("%s:'%s'" % (c, NAMES[c][i]) for c in order) + '}' for i in range(3)}
    parts = a.split("countryName:")
    assert len(parts) == 4
    out = parts[0]
    for i in range(3):
        j = parts[i + 1].index('}') + 1
        out += 'countryName:' + cn[i] + parts[i + 1][j:]
    a = out
    words = {c: ' '.join(dict.fromkeys(' '.join(NAMES[c][:3]).lower().replace('ä', 'a').replace('ö', 'o').replace('í', 'i').replace('é', 'e').replace('ñ', 'n').replace('ü', 'u').split() + NAMES[c][3].split())) for c in order if c != 'DE'}
    a = re.sub(r"const COUNTRY_WORDS = \{[^\n]*\};", lambda m: 'const COUNTRY_WORDS = {' + ', '.join("%s:'%s'" % (c, w) for c, w in words.items()) + '};', a, count=1)
    # subtítulos y texto «Acerca de»
    for lang, key in (('es', 'Stolpersteine en '), ('de', 'Stolpersteine in '), ('en', 'Stolpersteine in ')):
        a = a.replace("subtitle:'%s%s ·" % (key, OLD[lang]), "subtitle:'%s%s ·" % (key, short[lang]), 1)
    a = a.replace('placas en ' + OLD['es'] + ' a partir', 'placas en ' + es + ' a partir', 1).replace('Steine in ' + OLD['de'] + ' aus', 'Steine in ' + de + ' aus', 1).replace('stones in ' + OLD['en'] + ' from', 'stones in ' + en + ' from', 1)
    a = a.replace(' (Irlanda, Suecia, Jersey, Finlandia, Rumanía), solo', ', solo', 1).replace(' (Irland, Schweden, Jersey, Finnland, Rumänien), wird', ', wird', 1).replace(' (Ireland, Sweden, Jersey, Finland, Romania), only', ', only', 1)
    a = a.replace('<name>Stolpersteine in ' + OLD['de'] + '</name>', '<name>Stolpersteine in Europa (' + de + ')</name>', 1)
    # Posición aproximada deducida de la foto de Commons
    a = a.replace("posApprox:'Posición aproximada (del edificio, por su dirección en OpenStreetMap)',", "posApprox:'Posición aproximada (del edificio, por su dirección en OpenStreetMap)', posApproxPhoto:'Posición aproximada (la de la foto de la placa en Wikimedia Commons, comprobada con la dirección en OpenStreetMap)',", 1)
    a = a.replace("posApprox:'Ungefähre Position (Gebäude laut Adresse in OpenStreetMap)',", "posApprox:'Ungefähre Position (Gebäude laut Adresse in OpenStreetMap)', posApproxPhoto:'Ungefähre Position (die des Fotos des Steins auf Wikimedia Commons, mit der Adresse in OpenStreetMap geprüft)',", 1)
    a = a.replace("posApprox:'Approximate position (the building, from its address in OpenStreetMap)',", "posApprox:'Approximate position (the building, from its address in OpenStreetMap)', posApproxPhoto:'Approximate position (that of the stone’s photo on Wikimedia Commons, checked against the address in OpenStreetMap)',", 1)
    a = a.replace("s.gm?T('posApprox'):''", "s.gm?T(/^commons/.test(s.gm)?'posApproxPhoto':'posApprox'):''", 1)
    # v20r2 (auditoría B, W8): fechas de instantánea reales por grupo de países
    V = "(m.v20_added||{})"
    a = a.replace("OpenStreetMap (instantánea ${m.osm_snapshot}) y Wikidata (${m.wikidata_snapshot})", "OpenStreetMap (instantánea ${m.osm_snapshot.slice(0,10)} para Alemania, Irlanda, Suecia, Jersey, Finlandia y Rumanía; ${%s.snapshot_osm.slice(0,10)}, refrescada el 2026-11-20, para el resto) y Wikidata (${(m.wikidata_added||{}).snapshot||m.wikidata_snapshot} para esos países; ${%s.snapshot_wikidata} para el resto)" % (V, V), 1)
    a = a.replace("OpenStreetMap (Stand ${m.osm_snapshot}) und Wikidata (${m.wikidata_snapshot})", "OpenStreetMap (Stand ${m.osm_snapshot.slice(0,10)} für Deutschland, Irland, Schweden, Jersey, Finnland und Rumänien; ${%s.snapshot_osm.slice(0,10)}, am 2026-11-20 aufgefrischt, für die übrigen) und Wikidata (${(m.wikidata_added||{}).snapshot||m.wikidata_snapshot} für diese Länder; ${%s.snapshot_wikidata} für die übrigen)" % (V, V), 1)
    a = a.replace("OpenStreetMap (snapshot ${m.osm_snapshot}) and Wikidata (${m.wikidata_snapshot})", "OpenStreetMap (snapshot ${m.osm_snapshot.slice(0,10)} for Germany, Ireland, Sweden, Jersey, Finland and Romania; ${%s.snapshot_osm.slice(0,10)}, refreshed on 2026-11-20, for the rest) and Wikidata (${(m.wikidata_added||{}).snapshot||m.wikidata_snapshot} for those countries; ${%s.snapshot_wikidata} for the rest)" % (V, V), 1)
    # v20r3 (auditoría C ronda 2): una dirección sin número de casa (solo la calle) agrupa a <=8 m, no a 15 m (si no, Brahmsallee/Grindelallee forman un grupo de 42/22 columnas repartidas en 76 m)
    _old = "for (const list of byAddr.values()) clusters.push(...clusterByDist(list, 15));"
    assert _old in a
    a = a.replace(_old, "for (const [k, list] of byAddr) clusters.push(...clusterByDist(list, /\\d/.test(k) ? 15 : 8));", 1)
    assert a.count('snapshot_osm.slice') == 3
    _chk = re.sub(r'instantánea \$\{m\.osm_snapshot[^`]*?para el resto\)|Stand \$\{m\.osm_snapshot[^`]*?für die übrigen\)|snapshot \$\{m\.osm_snapshot[^`]*?for the rest\)', '', a)   # el texto de «Acerca de» nombra a propósito los países de la v19
    for lang in OLD: assert OLD[lang] not in _chk or lang == '', lang
    (R / 'app3d.js').write_text(a, encoding='utf-8')
    # index.html / jsonld / agents
    h = head('index.html')
    h = h.replace('mapa libre de Stolpersteine en ' + OLD['es'], 'mapa libre de Stolpersteine en ' + short['es']).replace('Mapa libre de los Stolpersteine en ' + OLD['es'], 'Mapa libre de los Stolpersteine en ' + short['es'])
    h = h.replace('Stolpersteine en ' + OLD['es'], 'Stolpersteine en ' + short['es']).replace('Stolpersteine in ' + OLD['de'], 'Stolpersteine in ' + short['de']).replace('Stolpersteine in ' + OLD['en'], 'Stolpersteine in ' + short['en'])
    def ld(x):
        x = x.replace('Stolpersteine in Germany, Ireland, Sweden, Jersey, Finland and Romania', 'Stolpersteine in ' + short['en'])
        x = x.replace('of every Stolperstein (memorial plaque for victims of National Socialism) in Germany, Ireland, Sweden, Jersey, Finland and Romania', 'of the Stolpersteine (memorial plaques for victims of National Socialism) that open data (OpenStreetMap, Wikidata) allows us to verify in ' + en)
        x = x.replace('"Germany", "Ireland", "Sweden", "Jersey", "Finland", "Romania"', ', '.join('"%s"' % NAMES[c][2] for c in order))
        places = ', '.join('{"@type": "Place", "name": "%s"}' % NAMES[c][2] for c in order)
        return re.sub(r'"spatialCoverage": \[[^\]]*\]', lambda m: '"spatialCoverage": [' + places + ']', x, count=1)
    h = ld(h)
    h = h.replace('Stolperstein (memorial plaque for victims of National Socialism) in ' + OLD['en'], 'Stolperstein (memorial plaque for victims of National Socialism) in ' + en)
    h = h.replace('Germany, Ireland, Sweden, Jersey, Finland and Romania', short['en'].replace('Germany and', 'Germany and'))
    places = ', '.join('{"@type": "Place", "name": "%s"}' % NAMES[c][2] for c in order)
    h = re.sub(r'"spatialCoverage": \[[^\]]*\]', lambda m: '"spatialCoverage": [' + places + ']', h, count=1)
    def stats(x):   # v20r3 (B R2-5): cifras y fechas actuales de los datos (JSON-LD de index.html y kauffmann-list.jsonld)
        SS = json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']; n = len(SS); de = sum(1 for s in SS if not s.get('cc') or s['cc'] == 'DE')
        cnt = lambda k: sum(1 for s in SS if s.get(k))
        for lab, k in (('with name', 'n'), ('with inscription', 'i'), ('with address', 'a'), ('with birth date', 'b'), ('with death date', 'd'), ('with Wikimedia Commons photo', 'img'),
                       ('with Bundesarchiv Gedenkbuch ID', 'gb'), ('with USHMM ID', 'us'), ('with Yad Vashem ID', 'yv')):
            x, m = re.subn(r'("name": "%s", "value": )\d+' % lab, lambda mm: mm.group(1) + str(cnt(k)), x); assert m <= 1
        x = re.sub(r'("name": "Stolpersteine in dataset", "value": )\d+', lambda mm: mm.group(1) + str(n), x)
        for lab in ('Wikipedia biography shown (CC BY-SA, certain match)', 'official or archive link only, no biography text', 'no biography and no official or archive link'):
            x = x.replace('"name": "%s"' % lab, '"name": "%s (Germany only, measured 2026-11-18)"' % lab)
        x = x.replace('Status 2026-11-18, in preparation, not published: 65,820 stones mapped from open data', 'Status 2026-11-20, in preparation, not published: {:,} stones in 27 countries ({:,} in Germany) mapped from open data'.format(n, de))
        x = x.replace('Biography texts shown only from Wikipedia CC BY-SA on a certain match (4,038)', 'Biography texts shown only from Wikipedia CC BY-SA on a certain match (4,038, Germany only)')
        x = x.replace('the measured coverage on 18 November 2026', 'the measured coverage on 20 November 2026')
        x = x.replace('"dateModified": "2026-11-18"', '"dateModified": "2026-11-20"').replace('"dateModified": "2026-11-04"', '"dateModified": "2026-11-18"')
        return x
    h = stats(h)
    (R / 'index.html').write_text(h, encoding='utf-8')
    (R / 'kauffmann-list.jsonld').write_text(stats(ld(head('kauffmann-list.jsonld'))), encoding='utf-8')
    print('países', order, 'cortos', short)
if __name__ == '__main__': main()
