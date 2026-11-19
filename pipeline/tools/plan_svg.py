#!/usr/bin/env python3
"""Plano (SVG→PNG) de una placa: huellas de edificios (gris), vías (líneas), origen (rojo) y posición de dibujo (verde) + columna 1,2 m. Datos © OpenStreetMap (ODbL)."""
import json, sys, math, os, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import *
R = Path(__file__).resolve().parents[2]; D = Path(os.environ.get('V19_DATA', '/workspace/v19-data'))
def svg_for(s, near, B, half=28, px=900):
    o = (s['la'], s['lo']); sc = px / (2 * half)
    X = lambda x: px / 2 + x * sc; Y = lambda y: px / 2 - y * sc
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="100%%" height="100%%" fill="#f4f1ea"/>' % (px, px, px, px)]
    for hid, h in near['highways'].items():
        t = h.get('tags') or {}; g = [to_xy(p['lat'], p['lon'], o) for p in h.get('geometry', [])]
        if len(g) < 2 or all(abs(x) > half * 2 and abs(y) > half * 2 for x, y in g): continue
        hw = t.get('highway'); w = 5 if hw in ('footway', 'path', 'cycleway', 'steps', 'pedestrian') else 9
        col = '#d9a05b' if w == 5 else '#bdbdbd'
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%d" stroke-linecap="round" opacity=".85"/>' % (' '.join('%.1f,%.1f' % (X(x), Y(y)) for x, y in g), col, w))
        if t.get('name'):
            mx = [p for p in g if abs(p[0]) < half and abs(p[1]) < half]
            if mx: out.append('<text x="%.0f" y="%.0f" font-size="13" fill="#555">%s</text>' % (X(mx[0][0]) + 4, Y(mx[0][1]) - 4, t['name'].replace('&', '&amp;')))
    for bid, b in B.items():
        for r in b['outer']:
            g = [to_xy(a, c, o) for a, c in r]
            if all(abs(x) > half * 2 and abs(y) > half * 2 for x, y in g): continue
            hit = any(inside_poly(0, 0, [g], []) for _ in [0])
            out.append('<polygon points="%s" fill="%s" stroke="#666" stroke-width="1.5"/>' % (' '.join('%.1f,%.1f' % (X(x), Y(y)) for x, y in g), '#e8a7a7' if hit else '#9a9a9a'))
    r0 = 0.6 * sc
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#c00" stroke-dasharray="4 3"/><circle cx="%.1f" cy="%.1f" r="4" fill="#c00"/>' % (X(0) - r0, Y(0) - r0, 2 * r0, 2 * r0, X(0), Y(0)))
    if 'dla' in s:
        x, y = to_xy(s['dla'], s['dlo'], o)
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#d4a017" fill-opacity=".8" stroke="#8a6500" stroke-width="2"/><circle cx="%.1f" cy="%.1f" r="4" fill="#060"/><line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#060" stroke-width="2"/>' % (X(x) - r0, Y(y) - r0, 2 * r0, 2 * r0, X(x), Y(y), X(0), Y(0), X(x), Y(y)))
    out.append('<text x="10" y="22" font-size="16" fill="#222">%s · %s · rojo = origen (OSM/Wikidata), verde/dorado = posición de dibujo · cuadrado 1,2 m · © OpenStreetMap (ODbL)</text><line x1="10" y1="%d" x2="%d" y2="%d" stroke="#222" stroke-width="3"/><text x="%d" y="%d" font-size="13">10 m</text></svg>' % (s['n'].replace('&','&amp;'), s['id'], px - 20, 10 + 10 * sc, px - 20, 18 + 10 * sc, px - 20))
    return ''.join(out)
async def shoot(items, outdir):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True)
        pg = await b.new_page(viewport={'width': 900, 'height': 900})
        for name, svg in items:
            await pg.set_content('<body style="margin:0">%s</body>' % svg); await pg.screenshot(path=str(outdir / ('acera-%s.png' % name)))
        await b.close()
if __name__ == '__main__':
    near = json.load(open(D / 'near.json')); B = building_polygons(near['buildings'])
    data = json.load(open(R / 'data/stones.json'))['stones']; ids = sys.argv[1:]
    by = {s['id']: s for s in data}
    items = [(i, svg_for(by[i], near, B)) for i in ids]
    (R / 'shots').mkdir(exist_ok=True); asyncio.run(shoot(items, R / 'shots'))
