#!/usr/bin/env python3
"""v19 ronda 2: cierra el bucle con la distribución REAL de la app (agrupación, cuadrícula, empujones de hasta 8 m entre casas cercanas).
Repite: sidewalk.py → tests/sidewalk-render-check.py (Chrome, cuadrado de 1,2 m + 0,5 m) → si alguna columna dibujada queda a menos de 0,5 m de un edificio,
sube la holgura extra de su grupo (pipeline/tools/sidewalk-extra.json) y vuelve a calcular. Necesita un servidor local: python3 -m http.server 8899 en la raíz del repo.
Uso: /usr/bin/python3 pipeline/tools/sidewalk_loop.py [http://127.0.0.1:8899/]"""
import json, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8899/'
XF = Path(__file__).with_name('sidewalk-extra.json')
extra = json.load(open(XF)) if XF.exists() else {}
for it in range(8):
    subprocess.run([sys.executable, str(R / 'pipeline/tools/sidewalk.py')], check=True, cwd=R, stdout=subprocess.DEVNULL)
    out = R / '/tmp/sw-render.json' if False else Path('/tmp/sw-render.json')
    r = subprocess.run([sys.executable, str(R / 'tests/sidewalk-render-check.py'), BASE, '--json', str(out)], cwd=R, capture_output=True, text=True)
    res = json.load(open(out)); T = {t['id']: t for t in json.load(open(R / 'data/sidewalk-v19.json'))['stones']}
    bad = [x for x in res if x['toca']]
    print('iteración', it, 'fallan', [(x['n'], x['centro_a_edificio_m']) for x in bad])
    if not bad: break
    for x in bad:
        g = T[x['id']]['grupo_id']; extra[g] = round(extra.get(g, 0) + 0.3, 2)
    XF.write_text(json.dumps(extra, indent=1))
else:
    sys.exit('no converge')
print('extras', extra)
