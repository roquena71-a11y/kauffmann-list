#!/usr/bin/env python3
"""v20r4 (auditoría B ronda 3, R3-5): las cifras de biografías/enlaces (4.038 + 24.670 + 37.112 = 65.820) se midieron el 18-nov-2026 sobre las 65.820 placas que entonces se contaban como Alemania;
hoy Alemania tiene 65.830 (−19 reclasificadas, +29 de las 1.480). Se dice así, sin cambiar las cifras. Idempotente. Uso: texts20_r4.py"""
from pathlib import Path
R = Path(__file__).resolve().parents[2]
REP = {
 'proyecto/index.html': [('(Stand 18. November 2026)', '(Stand 18. November 2026, gemessen an den damals als Deutschland gezählten 65.820 Steinen)')],
 'proyecto/proyecto.js': [('(Stand 18. November 2026)', '(Stand 18. November 2026, gemessen an den damals als Deutschland gezählten 65.820 Steinen)'),
                          ('(as of 18 November 2026)', '(as of 18 November 2026, measured on the 65,820 stones then counted as Germany)'),
                          ('(a 18 de noviembre de 2026)', '(a 18 de noviembre de 2026, medidas sobre las 65.820 placas que entonces se contaban como Alemania)')],
 'proyecto/blatt-de.html': [('4.038 Biografietexte auf der Karte (nur Deutschland),', '4.038 Biografietexte auf der Karte (nur Deutschland; gemessen am 18. November 2026 an den damals 65.820 Steinen),')],
 'proyecto/blatt-en.html': [('4,038 biography texts on the map (Germany only),', '4,038 biography texts on the map (Germany only; measured on 18 November 2026 on the 65,820 stones then),')],
 'index.html': [('(Germany only, measured 2026-11-18)', '(Germany only, measured 2026-11-18 on the 65,820 stones then counted as Germany)')],
 'kauffmann-list.jsonld': [('(Germany only, measured 2026-11-18)', '(Germany only, measured 2026-11-18 on the 65,820 stones then counted as Germany)')],
}
for f, reps in REP.items():
    p = R / f; t = p.read_text(encoding='utf-8'); o = t
    for a, b in reps:
        if a in t and b not in t: t = t.replace(a, b)
    p.write_text(t, encoding='utf-8'); print(f, 'cambiado' if t != o else 'sin cambios')
