#!/usr/bin/env python3
"""v20r3 (auditoría B ronda 2, R2-5): textos públicos de proyecto/ (index.html, proyecto.js, blatt-de.html, blatt-en.html) con las cifras y fechas actuales (72.038 placas, 27 países,
fechas de instantánea por grupo de países). Las cifras de biografías/enlaces (4.038, 24.670, 37.112) solo se pueden medir en Alemania: se rotulan «(Deutschland / Germany / Alemania, 18-nov-2026)»
y NO se extienden a los demás países. Uso: texts20.py (lee data/stones.json). Reemplazos exactos: si una cadena ya no está, avisa."""
import json, re
from pathlib import Path
R = Path(__file__).resolve().parents[2]
S = json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']
N = len(S); DE = sum(1 for s in S if not s.get('cc') or s['cc'] == 'DE'); IMG = sum(1 for s in S if s.get('img')); INS = sum(1 for s in S if s.get('i'))
PCT = 100.0 * IMG / N
dot = lambda n: '{:,}'.format(n).replace(',', '.'); com = lambda n: '{:,}'.format(n)
pct_de = ('%.1f' % PCT).replace('.', ',') + ' %'; pct_en = '%.1f%%' % PCT
print('total', N, 'DE', DE, 'img', IMG, pct_en, 'insc', INS)
REP = [  # (cadena vieja, nueva)
 ('65.820 Steine.', '%s Steine in 27 Ländern (%s in Deutschland).' % (dot(N), dot(DE))), ('65,820 stones.', '%s stones in 27 countries (%s in Germany).' % (com(N), com(DE))),
 ('65.820', dot(N)), ('65,820', com(N)), ('50.636', dot(IMG)), ('50,636', com(IMG)), ('61.948', dot(INS)), ('61,948', com(INS)),
 ('(76,9 %)', '(%s)' % pct_de), ('76,9 %)', pct_de + ')'), ('76.9%', pct_en),
 # alcance: Alemania y 26 países más
 ('freie, nicht kommerzielle Karte der Stolpersteine in Deutschland. Eine Familie', 'freie, nicht kommerzielle Karte der Stolpersteine in Deutschland und 26 weiteren Ländern Europas. Eine Familie'),
 ('Karte der Stolpersteine in Deutschland, begründet', 'Karte der Stolpersteine in Deutschland und 26 weiteren Ländern Europas, begründet'),
 ('freie Karte der Stolpersteine in Deutschland. Für Institutionen', 'freie Karte der Stolpersteine in Deutschland und 26 weiteren Ländern Europas. Für Institutionen'),
 ('non-commercial map of the Stolpersteine in Germany. A family', 'non-commercial map of the Stolpersteine in Germany and 26 other European countries. A family'),
 ('map of the Stolpersteine in Germany, founded', 'map of the Stolpersteine in Germany and 26 other European countries, founded'),
 ('mapa libre y no comercial de las Stolpersteine en Alemania. Una familia', 'mapa libre y no comercial de las Stolpersteine en Alemania y otros 26 países de Europa. Una familia'),
 # fechas y fuentes
 ('Zahlen vom 18. November 2026. Quelle der Steine: OpenStreetMap, ODbL, Auszug 4. November 2026, und Wikidata, CC0, Stand 18. November 2026;',
  'Zahlen vom 20. November 2026. Quelle der Steine: OpenStreetMap, ODbL (Deutschland, Irland, Schweden, Jersey, Finnland und Rumänien: Auszug vom 4. November 2026; die übrigen Länder: Auszug vom 18. November 2026, am 20. November 2026 per Id aufgefrischt), und Wikidata, CC0 (Stand 18. November 2026 für jene sechs Länder, 20. November 2026 für die übrigen); die Zahlen zu Biografietexten und Links unten gelten nur für Deutschland (Stand 18. November 2026);'),
 ('Figures of 18 November 2026. The stones come from OpenStreetMap, ODbL, extract of 4 November 2026, and Wikidata, CC0, as of 18 November 2026;',
  'Figures of 20 November 2026. The stones come from OpenStreetMap, ODbL (Germany, Ireland, Sweden, Jersey, Finland and Romania: extract of 4 November 2026; the other countries: extract of 18 November 2026, refreshed by id on 20 November 2026), and Wikidata, CC0 (as of 18 November 2026 for those six countries, 20 November 2026 for the rest); the figures on biography texts and links below are for Germany only (as of 18 November 2026);'),
 ('Cifras del 18 de noviembre de 2026. Las placas vienen de OpenStreetMap, ODbL, extracto del 4 de noviembre de 2026, y de Wikidata, CC0, a 18 de noviembre de 2026;',
  'Cifras del 20 de noviembre de 2026. Las placas vienen de OpenStreetMap, ODbL (Alemania, Irlanda, Suecia, Jersey, Finlandia y Rumanía: extracto del 4 de noviembre de 2026; los demás países: extracto del 18 de noviembre de 2026, refrescado por id el 20 de noviembre), y de Wikidata, CC0 (a 18 de noviembre de 2026 para esos seis países, 20 de noviembre para los demás); las cifras de textos biográficos y enlaces de abajo son solo de Alemania (a 18 de noviembre de 2026);'),
 ('OpenStreetMap, ODbL, 4. November 2026; Wikidata, CC0, 18. November 2026 (', 'OpenStreetMap, ODbL (Deutschland, Irland, Schweden, Jersey, Finnland, Rumänien: 4. November 2026; übrige Länder: 18. November 2026, am 20. November per Id aufgefrischt); Wikidata, CC0 (18. bzw. 20. November 2026) ('),
 ('OpenStreetMap, ODbL, 4 November 2026; Wikidata, CC0, 18 November 2026 (', 'OpenStreetMap, ODbL (Germany, Ireland, Sweden, Jersey, Finland, Romania: 4 November 2026; other countries: 18 November 2026, refreshed by id on 20 November); Wikidata, CC0 (18 and 20 November 2026) ('),
 # biografías/enlaces: solo Alemania
 ('die 4.038 auf der Karte', 'die 4.038 auf der Karte (nur Deutschland)'), ('the 4,038 on the map', 'the 4,038 on the map (Germany only)'), ('las 4.038 que aparecen en el mapa', 'las 4.038 que aparecen en el mapa (solo Alemania)'),
 ('4.038 Biografietexte auf der Karte,', '4.038 Biografietexte auf der Karte (nur Deutschland),'), ('4,038 biography texts on the map,', '4,038 biography texts on the map (Germany only),'),
 ('Nur mit Link, ohne Text: 24.670.', 'Nur mit Link, ohne Text: 24.670 (Deutschland).'), ('Link only, no text: 24,670.', 'Link only, no text: 24,670 (Germany).'),
 ('mit Biografietext auf der Karte"', 'mit Biografietext auf der Karte (nur Deutschland)"'), ('mit Biografietext auf der Karte<', 'mit Biografietext auf der Karte (nur Deutschland)<'),
 ('nur mit Link, ohne Text"', 'nur mit Link, ohne Text (nur Deutschland)"'), ('nur mit Link, ohne Text<', 'nur mit Link, ohne Text (nur Deutschland)<'),
 ('ohne Text und ohne solchen Link"', 'ohne Text und ohne solchen Link (nur Deutschland)"'), ('ohne Text und ohne solchen Link<', 'ohne Text und ohne solchen Link (nur Deutschland)<'),
 ('with a biography text on the map"', 'with a biography text on the map (Germany only)"'), ('link only, no text"', 'link only, no text (Germany only)"'), ('no text and no such link"', 'no text and no such link (Germany only)"'),
 ('con texto biográfico en el mapa"', 'con texto biográfico en el mapa (solo Alemania)"'), ('solo con enlace, sin texto"', 'solo con enlace, sin texto (solo Alemania)"'), ('sin texto y sin ese enlace"', 'sin texto y sin ese enlace (solo Alemania)"'),
]
for f in ('proyecto/index.html', 'proyecto/proyecto.js', 'proyecto/blatt-de.html', 'proyecto/blatt-en.html'):
    t = (R / f).read_text(encoding='utf-8'); o = t
    for a, b in REP:
        if a in t and a != b: t = t.replace(a, b)
    (R / f).write_text(t, encoding='utf-8'); print(f, 'cambiado' if t != o else 'sin cambios')
