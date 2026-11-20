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
def head(p): return subprocess.run(['git', 'show', '49e7725:' + p], cwd=R, capture_output=True, text=True, check=True).stdout
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
    for lang in OLD: assert OLD[lang] not in a or lang == '', lang
    (R / 'app3d.js').write_text(a, encoding='utf-8')
    # index.html / jsonld / agents
    h = head('index.html')
    h = h.replace('mapa libre de Stolpersteine en ' + OLD['es'], 'mapa libre de Stolpersteine en ' + short['es']).replace('Mapa libre de los Stolpersteine en ' + OLD['es'], 'Mapa libre de los Stolpersteine en ' + short['es'])
    h = h.replace('Stolpersteine en ' + OLD['es'], 'Stolpersteine en ' + short['es']).replace('Stolpersteine in ' + OLD['de'], 'Stolpersteine in ' + short['de']).replace('Stolpersteine in ' + OLD['en'], 'Stolpersteine in ' + short['en'])
    def ld(x):
        x = x.replace('Stolpersteine in Germany, Ireland, Sweden, Jersey, Finland and Romania', 'Stolpersteine in ' + short['en'])
        x = x.replace('of every Stolperstein (memorial plaque for victims of National Socialism) in Germany, Ireland, Sweden, Jersey, Finland and Romania', 'of the Stolpersteine (memorial plaques for victims of National Socialism) that open data (OpenStreetMap, Wikidata) allows us to verify in ' + en)
        x = x.replace('"Germany", "Ireland", "Sweden", "Jersey", "Finland", "Romania"', ', '.join('"%s"' % NAMES[c][2] for c in order))
        return x
    h = ld(h)
    h = h.replace('Stolperstein (memorial plaque for victims of National Socialism) in ' + OLD['en'], 'Stolperstein (memorial plaque for victims of National Socialism) in ' + en)
    h = h.replace('Germany, Ireland, Sweden, Jersey, Finland and Romania', short['en'].replace('Germany and', 'Germany and'))
    places = ', '.join('{"@type": "Place", "name": "%s"}' % NAMES[c][2] for c in order)
    h = re.sub(r'"spatialCoverage": \[[^\]]*\]', lambda m: '"spatialCoverage": [' + places + ']', h, count=1)
    (R / 'index.html').write_text(h, encoding='utf-8')
    (R / 'kauffmann-list.jsonld').write_text(ld(head('kauffmann-list.jsonld')), encoding='utf-8')
    print('países', order, 'cortos', short)
if __name__ == '__main__': main()
