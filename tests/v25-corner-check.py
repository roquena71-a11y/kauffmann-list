#!/usr/bin/env python3
"""v25 (paso 1, esquinas): remate de la columna con esquinas redondas y marco de latón uniforme.
Comprueba en el navegador, con la geometría REAL que dibuja el cliente (fuentes GeoJSON de columns.js):
  1. maxzoom de las fuentes: placas (marco, cara) y surcos >= 22, fuste >= 20 (con maxzoom 16 MapLibre cuantizaba los
     vértices a la rejilla de la tesela z16 ≈ 4,8 cm en lat 50: picos en las esquinas y marco de grosor desigual).
  2. Simulando esa cuantización (8192 unidades por tesela en el maxzoom de cada fuente), para cada placa de Westendstraße 82
     y Zimmerstraße 48b–50: canto visible del marco (cara→borde del marco) = 0,08 m ± 1 cm en TODO el contorno (lados y esquinas)
     y cada arco de esquina de la cara a ±1 cm de su radio. Autocontrol: con maxzoom 16 las mismas medidas deben fallar.
  3. Surcos encima de la cara de latón (base >= altura de la cara), no tapados dentro de ella; y dentro de la cara en planta.
Uso: python3 tests/v25-corner-check.py BASE_URL"""
import asyncio, math, os, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8899/'
CHROME = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
SPOTS = {'Westendstraße 82': ['Q131924672', 'Q131924669', 'Q131924674', 'Q131924675'],
         'Zimmerstraße 48b–50': ['Q132154636', 'Q132855136', 'Q132154647', 'Q132154640']}
RIM_W, TOL_W, TOL_R = 0.08, 0.010, 0.010
R_EARTH = 6378137.0

def merc(lo, la):
    return (math.radians(lo) * R_EARTH, math.log(math.tan(math.pi / 4 + math.radians(la) / 2)) * R_EARTH)
def quant(ring, z):
    """Vértices llevados a la rejilla entera de la tesela (extent 8192) en el zoom z, como hace geojson-vt."""
    if z is None: return ring
    n = 2 ** z * 8192; out = []
    for lo, la in ring:
        x = (lo + 180) / 360 * n; s = math.sin(math.radians(la)); y = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
        x, y = round(x), round(y)
        lo2 = x / n * 360 - 180; la2 = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
        out.append((lo2, la2))
    return out
def local(ring, lo0, la0, ang):
    """Metros en el marco de la placa (girado -ang), origen en el centro de la placa; corrige la escala de Mercator."""
    k = math.cos(math.radians(la0)); x0, y0 = merc(lo0, la0); c, s = math.cos(-ang), math.sin(-ang); out = []
    for lo, la in ring:
        x, y = merc(lo, la); x = (x - x0) * k; y = (y - y0) * k
        out.append((x * c - y * s, x * s + y * c))
    return out
def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p; dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)
def ring_dist(p, ring): return min(seg_dist(p, ring[i], ring[i + 1]) for i in range(len(ring) - 1))
def densify(ring, step=0.01):
    out = []
    for i in range(len(ring) - 1):
        a, b = ring[i], ring[i + 1]; n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return out
def measure(face, rim, half_f, r_f):
    """Canto del marco (min/max de la distancia cara→marco en el contorno denso de la cara) y error radial de los arcos."""
    pts = densify(face); w = [ring_dist(p, rim) for p in pts]
    c = half_f - r_f; rad_err = 0.0
    for (x, y) in face[:-1]:
        if abs(x) > c + 1e-4 and abs(y) > c + 1e-4:   # vértice de arco (fuera del cuadrado interior)
            rad_err = max(rad_err, abs(math.hypot(abs(x) - c, abs(y) - c) - r_f))
    return min(w), max(w), rad_err

async def main():
    fails = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        pg = await (await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')).new_page()
        blocked = []; errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        async def rh(r): blocked.append(r.request.url); await r.abort()
        await pg.route('**/*.workers.dev/**', rh); await pg.route('**/*kl-contador*', rh)
        await pg.goto(BASE + 'index.html?intro=0&lang=es&base=day', wait_until='domcontentloaded', timeout=180000)
        await pg.wait_for_function("typeof VISIBLE!=='undefined' && VISIBLE.length>70000 && window.map && map.loaded && map.loaded() && (!window.KLAlign || KLAlign.ready)", timeout=300000)
        res = {}
        for name, ids in SPOTS.items():
            r = await pg.evaluate("""async (ids) => {
              const ss = ids.map(id => byId.get(id)).filter(Boolean);
              const la = ss.reduce((a,s)=>a+s._dla,0)/ss.length, lo = ss.reduce((a,s)=>a+s._dlo,0)/ss.length;
              map.jumpTo({center:[lo, la], zoom:20, pitch:0, bearing:0});
              if (window.KLCols && KLCols.finish) KLCols.finish();
              await new Promise(r => { map.once('idle', r); setTimeout(r, 8000); });
              const st = map.getStyle(), src = st.sources, lay = Object.fromEntries(st.layers.map(l => [l.id, l]));
              const dataOf = id => { const s = map.getSource(id); const d = s && s._data; return (d && d.geojson) || d || null; };
              const featOf = (id, sid) => { const d = dataOf(id); if (!d || !d.features) return null; const f = d.features.find(f => f.properties && f.properties.id === sid); return f ? f.geometry.coordinates : null; };
              const num = e => Array.isArray(e) ? (typeof e[1] === 'number' ? e[1] : null) : e;
              return {
                maxz: {shaft: (src[lay['stones'].source]||{}).maxzoom, rim: (src['col-0.51-0.1']||{}).maxzoom, face: (src['col-0.43-0.08']||{}).maxzoom, grooves: (src['col-placa-grooves']||{}).maxzoom},
                faceTop: num(lay['stones-2'] && lay['stones-2'].paint['fill-extrusion-height']),
                grooveBase: num(lay['stones-grooves'] && lay['stones-grooves'].paint['fill-extrusion-base']),
                stones: ss.map(s => ({id: s.id, la: s._dla, lo: s._dlo, ang: s._ang || 0, rim: featOf('col-0.51-0.1', s.id), face: featOf('col-0.43-0.08', s.id), gr: featOf('col-placa-grooves', s.id)}))
              }; }""", ids)
            res[name] = r
        await b.close()
    for name, r in res.items():
        mz = r['maxz']
        if not (mz['rim'] and mz['rim'] >= 22 and mz['face'] and mz['face'] >= 22 and mz['grooves'] and mz['grooves'] >= 22): fails.append(f'{name}: maxzoom placas/surcos < 22: {mz}')
        if not (mz['shaft'] and mz['shaft'] >= 20): fails.append(f'{name}: maxzoom del fuste < 20: {mz}')
        if r['faceTop'] is None or r['grooveBase'] is None or r['grooveBase'] < r['faceTop'] - 1e-9: fails.append(f"{name}: surcos dentro de la cara (base {r['grooveBase']} < cara {r['faceTop']})")
        for s in r['stones']:
            if not s['rim'] or not s['face'] or not s['gr']: fails.append(f"{name} {s['id']}: falta geometría de placa en la fuente"); continue
            rim0 = s['rim'][0]; face0 = s['face'][0]
            # radio y semilado reales de la cara a partir de la geometría sin cuantizar
            fl = local(face0, s['lo'], s['la'], s['ang']); half_f = max(max(abs(x), abs(y)) for x, y in fl)
            c_guess = [math.hypot(x, y) for x, y in fl]
            # r_f: el arco a 45° está a distancia (half-r)*√2 + r del centro → r = (half*√2 - dmax)/(√2-1)
            dmax = max(c_guess); r_f = (half_f * math.sqrt(2) - dmax) / (math.sqrt(2) - 1)
            line = []
            for z in dict.fromkeys((mz['rim'], 16)):
                f = local(quant(face0, z), s['lo'], s['la'], s['ang']); rm = local(quant(rim0, z), s['lo'], s['la'], s['ang'])
                wmin, wmax, rerr = measure(f, rm, half_f, r_f)
                ok = abs(wmin - RIM_W) <= TOL_W and abs(wmax - RIM_W) <= TOL_W and rerr <= TOL_R
                line.append((z, round(wmin, 4), round(wmax, 4), round(rerr, 4), ok))
                if z == mz['rim'] and not ok: fails.append(f"{name} {s['id']}: marco desigual o esquina no redonda con maxzoom {z}: canto {wmin:.3f}–{wmax:.3f} m, error radial {rerr:.3f} m")
                if z == 16 and ok: fails.append(f"{name} {s['id']}: el autocontrol con maxzoom 16 no detecta la cuantización ({wmin:.3f}–{wmax:.3f}, {rerr:.3f})")
            # surcos dentro de la cara en planta
            gx = [pt for poly in s['gr'] for ring in poly for pt in local(ring, s['lo'], s['la'], s['ang'])]
            if max(max(abs(x), abs(y)) for x, y in gx) > half_f - 0.05: fails.append(f"{name} {s['id']}: surco fuera de la cara")
            print(f"{name} {s['id']}: cara semilado {half_f:.3f} m radio {r_f:.3f} m | [maxzoom, canto min, canto max, error radial, ok]: {line}")
        print(f"{name}: maxzoom {mz} · cara hasta {r['faceTop']} m · surcos desde {r['grooveBase']} m")
    print('peticiones al contador:', len(blocked), '| errores de página:', errs[:3])
    if blocked: fails.append(f'peticiones al contador: {len(blocked)}')
    if errs: fails.append(f'errores de página: {errs[:3]}')
    if fails:
        print('FALLO v25-corner-check:'); [print('  -', f) for f in fails[:20]]; sys.exit(1)
    print('OK v25-corner-check: esquinas redondas y canto del marco 0,08 m ±1 cm en todo el contorno (maxzoom placas 22, fuste 20); surcos visibles sobre la cara')
asyncio.run(main())
