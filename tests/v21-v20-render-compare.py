#!/usr/bin/env python3
"""Compara las posiciones DIBUJADAS (_dla/_dlo/_ang) de las 72.110 placas de v20
entre el cliente b142fa48 y este cliente v21. Las placas nuevas deben coincidir
con el dla/dlo (o la/lo) del archivo, sin relayout en el cliente.

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
            f"typeof DATA!=='undefined' && DATA.length>={expect_min} && DATA.every(s=>s._dla!==undefined || s._aliasOf)",
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

    moved, ang_only = [], []
    for i, a in v20.items():
        b = v21[i]
        if a.get('_dla') is None or b.get('_dla') is None:
            # alias without copy would be a bug
            if a.get('alias') or b.get('alias'):
                # still require drawn coords
                if b.get('_dla') is None:
                    moved.append((i, 'sin _dla en v21', a, b))
                    continue
            else:
                moved.append((i, 'sin _dla', a, b))
                continue
        d = dist_m(a['_dla'], a['_dlo'], b['_dla'], b['_dlo'])
        axis_deg, raw_deg = ang_diff_deg(a['_ang'], b['_ang'])
        if d > TOL_M:
            moved.append((d, i, a, b, axis_deg))
        elif axis_deg > TOL_ANG_DEG or raw_deg > TOL_ANG_DEG:
            ang_only.append((raw_deg, axis_deg, i, a, b))

    added = [r for r in v21.values() if is_added(r)]
    pin_fail, cc_fail, gt25 = [], [], []
    # official hav for 25 m on rendered vs source (s.sla if present else file origin — after swap, s.la is drawing)
    # Policy: _dla/_dlo must equal s.la/s.lo (file drawing position) unless aliased to a v20 primary.
    for r in added:
        if r.get('cc') != 'DE':
            cc_fail.append(r['id'])
        if r.get('alias'):
            continue
        if r.get('_dla') is None:
            pin_fail.append((r['id'], 'sin _dla'))
            continue
        d = dist_m(r['_dla'], r['_dlo'], r['la'], r['lo'])
        if d > TOL_M:
            pin_fail.append((r['id'], d, r))
        # also vs file dla if present
        if r.get('dla_file') is not None:
            d2 = dist_m(r['_dla'], r['_dlo'], r['dla_file'], r['dlo_file'])
            if d2 > TOL_M:
                pin_fail.append((r['id'] + '/dla_file', d2, r))

    ok = True
    print(f'v20 stones compared: {len(v20)}')
    print(f'v21 total: {len(v21)} (nuevas={len(added)})')
    if moved:
        ok = False
        moved.sort(key=lambda x: -(x[0] if isinstance(x[0], float) else 0))
        print(f'FAIL: {len(moved)} placas de v20 se mueven al dibujarlas en v21 (tol {TOL_M} m). Máx {moved[0][0]:.4f} m id={moved[0][1]}')
        for row in moved[:12]:
            if isinstance(row[0], float):
                d, i, a, b, ad = row
                print(f'  {i} d={d:.4f}m angΔ={ad:.3f}°  v20=({a["_dla"]},{a["_dlo"]},ang={a["_ang"]}) v21=({b["_dla"]},{b["_dlo"]},ang={b["_ang"]})')
            else:
                print(' ', row[1], row[0])
    else:
        print('OK: las 72.110 placas de v20 se dibujan en la misma posición y ángulo que en b142fa48')

    if ang_only:
        ok = False
        ang_only.sort(reverse=True)
        print(f'FAIL: {len(ang_only)} placas de v20 cambian solo el ángulo (tol {TOL_ANG_DEG}°). p.ej. {ang_only[0][2]} raw={ang_only[0][0]:.3f}° axis={ang_only[0][1]:.3f}°')
    if pin_fail:
        ok = False
        print(f'FAIL: {len(pin_fail)} placas nuevas no están clavadas al dla/dlo del archivo')
        print(' ', pin_fail[:8])
    else:
        vis_new = sum(1 for r in added if not r.get('alias'))
        print(f'OK: {vis_new} placas nuevas visibles se dibujan exactamente en el dla/dlo del archivo')
    if cc_fail:
        ok = False
        print(f'FAIL: {len(cc_fail)} placas nuevas sin cc=DE, p.ej. {cc_fail[:8]}')
    else:
        print(f'OK: {len(added)} placas nuevas llevan cc=DE')

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
