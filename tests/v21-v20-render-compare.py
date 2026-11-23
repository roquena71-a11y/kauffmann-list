#!/usr/bin/env python3
"""Compara las posiciones DIBUJADAS (_dla/_dlo/_ang) de las 72.110 placas de v20
entre el cliente b142fa48 y este cliente v21. Las placas nuevas deben coincidir
con el dla/dlo (o la/lo) del archivo, sin relayout en el cliente.
v29: dos pasadas. Sin alineación (?alignoff=1) todo debe ser idéntico a b142fa48, como en v21.
Con alineación, la posición esperada es la de data/align-v24.json (tests/align_expected.py) para las
placas que están en él y la de antes para las demás; las reglas las comprueba tests/v24-align-check.py.

Uso: python3 tests/v21-v20-render-compare.py <url_v21> <url_v20>
Bloquea kl-contador y *.workers.dev.
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import align_expected as AE  # noqa: E402

M_LAT = 111320.0
TOL_M = 0.01          # 1 cm
TOL_ANG_DEG = 0.5
BLOCK_HOSTS = ('kl-contador', 'workers.dev')
V20_N = 72110


def dist_m(la1, lo1, la2, lo2):
    return math.hypot((la1 - la2) * M_LAT, (lo1 - lo2) * M_LAT * math.cos(math.radians((la1 + la2) / 2)))


def ang_diff_deg(a, b):
    """Smallest difference of unsigned row axes (period π) in degrees, then signed if needed.
    Auditor C asked rendered _ang to match; we compare the stored angle modulo π, and also the raw value.
    """
    da = abs((a or 0) - (b or 0))
    # raw
    raw = math.degrees(min(da, abs(da - 2 * math.pi), abs(da - 4 * math.pi) if da > 2 * math.pi else da))
    # axis (period π)
    d = abs((a or 0) - (b or 0)) % math.pi
    d = min(d, math.pi - d)
    return math.degrees(d), raw


async def dump(url, expect_min, label):
    t0 = time.time()
    blocked = []
    allowed = set()
    errs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path='/usr/bin/google-chrome',
            headless=True,
            args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader',
                  '--ignore-gpu-blocklist', '--disable-dev-shm-usage'],
        )
        ctx = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            service_workers='block',
            locale='es-ES',
        )
        page = await ctx.new_page()
        page.on('pageerror', lambda e: errs.append(str(e)))

        async def route_handler(route):
            u = route.request.url
            host = ''
            try:
                host = u.split('/')[2]
            except Exception:
                pass
            if any(b in u or b in host for b in BLOCK_HOSTS):
                blocked.append(u)
                await route.abort()
                return
            if u.startswith('http'):
                allowed.add(host)
            await route.continue_()

        await page.route('**/*', route_handler)
        await page.goto(url, wait_until='load', timeout=120000)
        await page.wait_for_function(
            f"typeof DATA!=='undefined' && DATA.length>={expect_min} && DATA.every(s=>s._dla!==undefined || s._aliasOf) && (!window.KLAlign || KLAlign.ready)",
            timeout=600000,
        )
        rows = await page.evaluate("""() => DATA.map(s => ({
          id: String(s.id),
          src: s.src || null,
          cc: s.cc || null,
          sla: s.sla ?? null, slo: s.slo ?? null,
          la: s.la, lo: s.lo,
          dla_file: s.dla ?? null, dlo_file: s.dlo ?? null,
          _dla: s._dla, _dlo: s._dlo, _ang: s._ang || 0,
          alias: s._aliasOf || null
        }))""")
        n = len(rows)
        print(
            f"  dumped {label}: n={n} blocked={len(blocked)} errs={len(errs)} "
            f"hosts={sorted(allowed)} t={round(time.time()-t0,1)}s",
            flush=True,
        )
        if errs:
            print('  page errors:', errs[:8], flush=True)
        if any('kl-contador' in h or 'workers.dev' in h for h in allowed):
            raise SystemExit(f'FAIL {label}: se contactó un host prohibido: {sorted(allowed)}')
        await browser.close()
    return {r['id']: r for r in rows}, blocked, errs


def is_added(r):
    src = r.get('src') or ''
    i = r.get('id') or ''
    return src in ('berlin', 'koeln') or i.startswith('ber-') or i.startswith('koeln-')


def compare(v20, v21, EXP, label):
    """v29: posición esperada = la del archivo de alineación (data/align-v24.json) si la placa está en él; si no, la de b142fa48 (v20)
    y, para las nuevas, su dla/dlo de archivo. Con EXP vacío (?alignoff=1) es exactamente la comprobación de v21."""
    moved, ang_only = [], []
    n_aligned = 0
    for i, a in v20.items():
        b = v21[i]
        if a.get('_dla') is None or b.get('_dla') is None:
            if a.get('alias') or b.get('alias'):
                if b.get('_dla') is None:
                    moved.append((i, 'sin _dla en v21', a, b))
                    continue
            else:
                moved.append((i, 'sin _dla', a, b))
                continue
        e = EXP.get(b.get('alias') or i)
        if e is not None:
            n_aligned += 1
            a = dict(a, _dla=e[0], _dlo=e[1], _ang=e[2])
        d = dist_m(a['_dla'], a['_dlo'], b['_dla'], b['_dlo'])
        axis_deg, raw_deg = ang_diff_deg(a['_ang'], b['_ang'])
        if d > TOL_M:
            moved.append((d, i, a, b, axis_deg))
        elif axis_deg > TOL_ANG_DEG or raw_deg > TOL_ANG_DEG:
            ang_only.append((raw_deg, axis_deg, i, a, b))

    added = [r for r in v21.values() if is_added(r)]
    pin_fail, cc_fail = [], []
    for r in added:
        if r.get('cc') != 'DE':
            cc_fail.append(r['id'])
        if r.get('alias'):
            continue
        if r.get('_dla') is None:
            pin_fail.append((r['id'], 'sin _dla'))
            continue
        e = EXP.get(r['id'])
        if e is not None:
            d = dist_m(r['_dla'], r['_dlo'], e[0], e[1])
            if d > TOL_M or ang_diff_deg(r['_ang'], e[2])[1] > TOL_ANG_DEG:
                pin_fail.append((r['id'] + '/alineación', d, r))
            continue
        d = dist_m(r['_dla'], r['_dlo'], r['la'], r['lo'])
        if d > TOL_M:
            pin_fail.append((r['id'], d, r))
        if r.get('dla_file') is not None:
            d2 = dist_m(r['_dla'], r['_dlo'], r['dla_file'], r['dlo_file'])
            if d2 > TOL_M:
                pin_fail.append((r['id'] + '/dla_file', d2, r))

    ok = True
    print(f'[{label}] v20 stones compared: {len(v20)} (en su posición alineada de data/align-v24.json: {n_aligned}; idénticas a b142fa48: {len(v20) - n_aligned})')
    print(f'[{label}] v21 total: {len(v21)} (nuevas={len(added)})')
    if moved:
        ok = False
        moved.sort(key=lambda x: -(x[0] if isinstance(x[0], float) else 0))
        print(f'FAIL [{label}]: {len(moved)} placas de v20 fuera de su posición esperada (tol {TOL_M} m). Máx {moved[0][0]:.4f} m id={moved[0][1]}')
        for row in moved[:12]:
            if isinstance(row[0], float):
                d, i, a, b, ad = row
                print(f'  {i} d={d:.4f}m angΔ={ad:.3f}°  esperada=({a["_dla"]},{a["_dlo"]},ang={a["_ang"]}) dibujada=({b["_dla"]},{b["_dlo"]},ang={b["_ang"]})')
            else:
                print(' ', row[1], row[0])
    else:
        print(f'OK [{label}]: las 72.110 placas de v20 se dibujan en su posición esperada (b142fa48 o, si está alineada, data/align-v24.json)')
    if ang_only:
        ok = False
        ang_only.sort(reverse=True)
        print(f'FAIL [{label}]: {len(ang_only)} placas de v20 cambian solo el ángulo (tol {TOL_ANG_DEG}°). p.ej. {ang_only[0][2]} raw={ang_only[0][0]:.3f}° axis={ang_only[0][1]:.3f}°')
    if pin_fail:
        ok = False
        print(f'FAIL [{label}]: {len(pin_fail)} placas nuevas fuera de su posición esperada (dla/dlo del archivo o alineación)')
        print(' ', pin_fail[:8])
    else:
        vis_new = sum(1 for r in added if not r.get('alias'))
        print(f'OK [{label}]: {vis_new} placas nuevas visibles en su posición esperada (dla/dlo del archivo o alineación)')
    if cc_fail:
        ok = False
        print(f'FAIL [{label}]: {len(cc_fail)} placas nuevas sin cc=DE, p.ej. {cc_fail[:8]}')
    else:
        print(f'OK [{label}]: {len(added)} placas nuevas llevan cc=DE')
    return ok, moved, ang_only, pin_fail, cc_fail, added


async def main():
    if len(sys.argv) < 3:
        print('uso: v21-v20-render-compare.py <url_v21> <url_v20>', file=sys.stderr)
        sys.exit(2)
    url_v21 = sys.argv[1].rstrip('/') + '/index.html?intro=0&lang=es'
    url_v20 = sys.argv[2].rstrip('/') + '/index.html?intro=0&lang=es'
    print('START v20', url_v20, flush=True)
    v20, b20, e20 = await dump(url_v20, V20_N, 'v20')
    print('START v21', url_v21, flush=True)
    v21, b21, e21 = await dump(url_v21, V20_N, 'v21')

    if len(v20) != V20_N:
        print(f'FAIL: v20 DATA tiene {len(v20)} placas, se esperaban {V20_N}')
        sys.exit(1)

    missing = [i for i in v20 if i not in v21]
    if missing:
        print(f'FAIL: {len(missing)} ids de v20 no están en v21, p.ej. {missing[:8]}')
        sys.exit(1)

    print('START v21 sin alineación (?alignoff=1 = disposición de v28)', flush=True)
    v21off, b21o, e21o = await dump(url_v21 + '&alignoff=1', V20_N, 'v21-alignoff')
    EXP = AE.load()
    ok1, *_ = compare(v20, v21off, {}, 'sin alineación')
    ok, moved, ang_only, pin_fail, cc_fail, added = compare(v20, v21, EXP, 'con alineación')
    ok = ok and ok1
    out = os.environ.get('V21_RENDER_CMP_OUT')
    if out:
        Path(out).write_text(json.dumps({
            'n_v20': len(v20), 'n_v21': len(v21), 'n_added': len(added),
            'moved': len(moved), 'ang_only': len(ang_only),
            'pin_fail': len(pin_fail), 'cc_fail': len(cc_fail),
            'moved_ids': [m[1] if isinstance(m[0], float) else m[0] for m in moved[:50]],
        }, indent=2))

    if not ok:
        sys.exit(1)
    print('OK: v21-v20-render-compare')


if __name__ == '__main__':
    asyncio.run(main())
