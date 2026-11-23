#!/usr/bin/env python3
"""v24: brass plaque present (no text), restored contrast vs buildings (day + night),
street-zoom / close-zoom budget and mobile heap, and grooves staying in sync
after pan-then-zoom (F1 of auditoría B ronda 1). Usage:
  python3 tests/v24-plaque-contrast-check.py [BASE_URL]
"""
from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
AXE = open('/workspace/tools-ai/node_modules/axe-core/axe.min.js').read()
TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
CHROME = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')

# Westendstraße 82 (4), used for contrast sampling.
WESTEND = ['Q131924672', 'Q131924669', 'Q131924674', 'Q131924675']

# Same budgets as tests/v23-ux-and-perf-check.py for the 16.5 jump; close zoom is extra.
STREET_SYNC_MS = 250
STREET_PAINT_MS = 2500
CLOSE_PAINT_MS = 3500
# Chrome 412×915 after street+close view; leaves headroom above typical ~200–350 MB.
HEAP_MB = 512


def check_source():
    app = (ROOT / 'app3d.js').read_text()
    cols = (ROOT / 'columns.js').read_text()
    gold = re.search(r"const GOLD = \['interpolate',\[\'linear\'\],\['zoom'\],\s*5,'(#......)',\s*12,'(#......)',\s*17,'(#......)'\]", app)
    assert gold, 'GOLD interpolate not found in app3d.js'
    assert gold.group(1) == '#c6a15b' and gold.group(2) == '#e0bc62', f'overview GOLD stops changed: {gold.groups()}'
    assert gold.group(3) == '#e0b020', f'street GOLD stop should be #e0b020, got {gold.group(3)}'
    light = re.search(r"const LIGHT = \{anchor:'map', position:\[([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)\], color:'(#......)', intensity:([0-9.]+)\}", app)
    assert light, 'LIGHT constant not found'
    assert float(light.group(3)) == 35 and float(light.group(5)) == 0.5, f'LIGHT is not 9025a3c0: {light.groups()}'
    assert "map.setLight(LIGHT)" in app
    assert 'BRASS_RIM' in cols and 'BRASS_FACE' in cols and 'col-placa-grooves' in cols
    assert 'PLACA_MINZOOM' in cols and 'GROOVE_MINZOOM' in cols
    # No invented inscription text in plaque geometry.
    assert not re.search(r'HIER WOHNTE|inscription|placaText|engravedText', cols)
    print(f"OK source: GOLD z5={gold.group(1)} z12={gold.group(2)} z17={gold.group(3)}; LIGHT polar={light.group(3)} intensity={light.group(5)}")
    return gold.groups()


def luma(rgb):
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a, b):
    L1, L2 = luma(a), luma(b)
    hi, lo = max(L1, L2), min(L1, L2)
    return (hi + 0.05) / (lo + 0.05)


def chroma(rgb):
    r, g, b = rgb
    mx, mn = max(r, g, b), min(r, g, b)
    return (mx - mn) / 255.0


def png_rgba(buf: bytes):
    """Minimal 8-bit RGB/RGBA PNG decoder (stdlib only)."""
    import struct, zlib
    assert buf[:8] == b'\x89PNG\r\n\x1a\n', 'not a PNG'
    i, w, h, ct, idat = 8, None, None, None, b''
    while i < len(buf):
        ln = struct.unpack('>I', buf[i:i+4])[0]
        typ = buf[i+4:i+8]
        data = buf[i+8:i+8+ln]
        i += 12 + ln
        if typ == b'IHDR':
            w, h, bit, ct = struct.unpack('>IIBB', data[:10])
        elif typ == b'IDAT':
            idat += data
        elif typ == b'IEND':
            break
    raw = zlib.decompress(idat)
    bpp = {2: 3, 6: 4}[ct]
    stride = w * bpp
    rows = []
    pos = 0
    for y in range(h):
        filt = raw[pos]
        pos += 1
        row = bytearray(raw[pos:pos+stride])
        pos += stride
        if filt == 1:
            for x in range(bpp, stride):
                row[x] = (row[x] + row[x-bpp]) & 255
        elif filt == 2:
            prev = rows[-1] if rows else bytes(stride)
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 255
        elif filt == 3:
            prev = rows[-1] if rows else bytes(stride)
            for x in range(stride):
                a = row[x-bpp] if x >= bpp else 0
                row[x] = (row[x] + ((a + prev[x]) // 2)) & 255
        elif filt == 4:
            prev = rows[-1] if rows else bytes(stride)
            def paeth(a, b, c):
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                return a if pa <= pb and pa <= pc else (b if pb <= pc else c)
            for x in range(stride):
                a = row[x-bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x-bpp] if x >= bpp else 0
                row[x] = (row[x] + paeth(a, b, c)) & 255
        elif filt != 0:
            raise ValueError(f'unsupported PNG filter {filt}')
        rows.append(bytes(row))
    return w, h, bpp, rows


def avg_at(rows, w, h, bpp, cx, cy, rad):
    r = g = b = n = 0
    x0, x1 = max(0, int(cx-rad)), min(w-1, int(cx+rad))
    y0, y1 = max(0, int(cy-rad)), min(h-1, int(cy+rad))
    for y in range(y0, y1+1):
        row = rows[y]
        for x in range(x0, x1+1):
            i = x * bpp
            rr, gg, bb = row[i], row[i+1], row[i+2]
            if rr+gg+bb < 40:
                continue
            r += rr; g += gg; b += bb; n += 1
    return [round(r/n), round(g/n), round(b/n), n] if n >= 8 else None


async def block_counters(pg, seen):
    async def abort(route):
        seen.append(route.request.url)
        await route.abort()
    await pg.route('**/*kl-contador*', abort)
    await pg.route('**/*.workers.dev/**', abort)


async def wait_data(pg):
    await pg.wait_for_function(
        "typeof VISIBLE !== 'undefined' && VISIBLE.length > 74000 && window.map && map.loaded && map.loaded() && (!window.KLAlign || KLAlign.ready)",
        timeout=180000,
    )


async def jump_group(pg, ids, zoom, pitch=58):
    return await pg.evaluate(
        """([ids, zoom, pitch]) => {
            const pts = ids.map(id => byId.get(id)).filter(Boolean);
            if (!pts.length) return {ok:false};
            const la = pts.reduce((t,s)=>t+(s._dla||s.la),0)/pts.length;
            const lo = pts.reduce((t,s)=>t+(s._dlo||s.lo),0)/pts.length;
            const ang = (pts[0]._ang || 0) * 180 / Math.PI;
            const bearing = ang + 20;
            map.jumpTo({center:[lo, la], zoom, pitch, bearing});
            if (window.KLCols && KLCols.finish) KLCols.finish();
            if (window.KLUI && KLUI.setSheet) KLUI.setSheet('collapsed');
            return {ok:true, n:pts.length, la, lo, ang, bearing, zoom:map.getZoom(),
                    dla: pts.map(s => +s._dla.toFixed(7)), dlo: pts.map(s => +s._dlo.toFixed(7)),
                    angR: pts.map(s => +s._ang.toFixed(6))};
        }""",
        [ids, zoom, pitch],
    )


async def settle(pg, ms=1500):
    try:
        await pg.evaluate("""() => new Promise(r => {
            if (map.loaded()) map.once('idle', r);
            else map.once('load', () => map.once('idle', r));
            setTimeout(r, 8000);
        })""")
    except Exception:
        pass
    await pg.wait_for_timeout(ms)


async def plaque_info(pg):
    return await pg.evaluate("""() => {
        const layers = (map.getStyle().layers || []).map(l => l.id);
        const placa = ['stones-1','stones-2','stones-grooves'].filter(id => layers.includes(id));
        const minz = {};
        for (const id of placa) minz[id] = map.getLayer(id) && map.getLayer(id).minzoom;
        const feat = id => map.getSource(id) ? map.querySourceFeatures(id).length : -1;
        const srcCounts = {
          shaft: feat('col-0.6-0.18'),
          rim: feat('col-0.51-0.1'),
          face: feat('col-0.43-0.08'),
          grooves: feat('col-placa-grooves'),
        };
        const qf = map.getSource('col-0.43-0.08') ? map.querySourceFeatures('col-0.43-0.08') : [];
        const sample = qf[0] || null;
        const keys = sample ? Object.keys(sample.properties || {}) : [];
        const textish = keys.filter(k => /name|text|insc|hier|wohente/i.test(k));
        const light = map.getLight ? map.getLight() : null;
        const gold = map.getLayer('stones') ? map.getPaintProperty('stones', 'fill-extrusion-color') : null;
        return {placa, minz, srcCounts, keys, textish, light, gold,
                zoom: map.getZoom(), show: !!(window.KLCols),
                rim: window.KLCols && KLCols.BRASS_RIM, face: window.KLCols && KLCols.BRASS_FACE};
    }""")


async def sample_regions(pg, ids):
    """Sample a Playwright screenshot (the presented canvas) at column tops vs a nearby façade."""
    geom = await pg.evaluate("""(ids) => {
        const pts = ids.map(id => byId.get(id)).filter(Boolean);
        if (!pts.length) return null;
        const TOP = 16.42;
        const z = map.getZoom(), pitch = map.getPitch() * Math.PI/180;
        const dpr = window.devicePixelRatio || 1;
        function topPx(s){
            const p = map.project([s._dlo, s._dla]);
            const mpp = 156543.03392 * Math.cos(s._dla * Math.PI/180) / Math.pow(2, z);
            return {x: p.x, y: p.y - (TOP / mpp) * Math.sin(pitch)};
        }
        const tops = pts.map(topPx);
        const mid = tops.reduce((t,p)=>({x:t.x+p.x/tops.length, y:t.y+p.y/tops.length}), {x:0,y:0});
        return {tops, mid, dpr, vw: innerWidth, vh: innerHeight};
    }""", ids)
    if not geom:
        return None
    png = await pg.screenshot(type='png')
    w, h, bpp, rows = png_rgba(png)
    # Screenshot is the full viewport at device pixels (412x915 @ dpr 2 → 824x1830).
    sx = w / geom['vw']
    sy = h / geom['vh']
    # Exclude chrome (header, menu, zoom/layer buttons, compass, sheet). The 3D lift
    # formula is only approximate, so we scan the visible map for brass-coloured pixels.
    x0, x1 = int(70*sx), int((geom['vw']-70)*sx)
    y0, y1 = int(80*sy), int((geom['vh']-160)*sy)
    cr = cg = cb = cn = 0
    br = bg = bb_ = bn = 0
    step = 2
    for y in range(y0, y1, step):
        row = rows[y]
        for x in range(x0, x1, step):
            i = x * bpp
            rr, gg, bb = row[i], row[i+1], row[i+2]
            chroma_v = max(rr,gg,bb) - min(rr,gg,bb)
            if rr >= 80 and bb <= rr * 0.55 and (rr - bb) >= 45 and chroma_v >= 40 and (rr+gg+bb)/3 <= 220:
                cr += rr; cg += gg; cb += bb; cn += 1
            elif 80 <= rr+gg+bb <= 730 and not (chroma_v >= 25 and (rr-bb) >= 28):
                br += rr; bg += gg; bb_ += bb; bn += 1
    col = [round(cr/cn), round(cg/cn), round(cb/cn), cn] if cn >= 20 else None
    bldg = [round(br/bn), round(bg/bn), round(bb_/bn), bn] if bn >= 40 else None
    return {
        'col': col, 'bldg': bldg,
        'tops': [{'x': round(p['x']), 'y': round(p['y'])} for p in geom['tops']],
        'size': [w, h], 'gold_n': cn, 'bldg_n': bn,
    }


async def run_axe(pg):
    await pg.add_script_tag(content=AXE)
    return await pg.evaluate(
        '(t) => axe.run(document, {runOnly: {type: "tag", values: t}})'
        '.then(r => r.violations.map(v => [v.id, v.nodes.length, v.nodes[0].target]))',
        TAGS,
    )


async def measure_zoom(pg, center, zoom, pitch, layer_ids):
    return await pg.evaluate("""([center, zoom, pitch, layers]) => new Promise(resolve => {
        const t0 = performance.now();
        let syncMs = 0;
        const check = () => {
            const have = layers.filter(id => map.getLayer(id));
            const fs = have.length ? map.queryRenderedFeatures({layers: have}) : [];
            if (fs.length > 0 || (performance.now() - t0) > 12000) {
                resolve({sync_ms: syncMs, painted_ms: Math.round(performance.now() - t0), count: fs.length, layers: have});
            } else requestAnimationFrame(check);
        };
        requestAnimationFrame(() => {
            const r0 = performance.now();
            void map.jumpTo({center, zoom, pitch, bearing: 0});
            if (window.KLCols && KLCols.finish) KLCols.finish();
            syncMs = Math.round(performance.now() - r0);
            requestAnimationFrame(check);
        });
    })""", [center, zoom, pitch, layer_ids])



async def jump_wait(pg, js, pred, ms=800):
    await pg.evaluate(js)
    await pg.wait_for_function("window.map && !map.isMoving()", timeout=20000)
    await pg.wait_for_function(pred, timeout=20000)
    await pg.wait_for_timeout(ms)


async def groove_sync_info(pg):
    """Source feature counts (serialize) plus painted face/groove counts."""
    return await pg.evaluate("""() => {
        const srcLen = (id) => {
            const s = map.getSource(id);
            if (!s || typeof s.serialize !== 'function') return -1;
            const d = s.serialize().data;
            return d && Array.isArray(d.features) ? d.features.length : -1;
        };
        const painted = (id) => map.getLayer(id) ? map.queryRenderedFeatures({layers:[id]}).length : -1;
        return {
            z: +map.getZoom().toFixed(2),
            center: [+map.getCenter().lng.toFixed(4), +map.getCenter().lat.toFixed(4)],
            srcRim: srcLen('col-0.51-0.1'),
            srcFace: srcLen('col-0.43-0.08'),
            srcGr: srcLen('col-placa-grooves'),
            nFace: painted('stones-2'),
            nGr: painted('stones-grooves'),
            nShaft: painted('stones'),
        };
    }""")


async def check_grooves_after_street_pan(pg):
    """F1 (auditoría B ronda 1, ef592220): pan at 16.5 then zoom to 18.2.

    On the buggy tree, a pan at 16.5 refreshes rim/face but leaves col-placa-grooves
    on the previous box; zooming in then short-circuits because plaquesOk is already
    true, so the new view paints faces and zero grooves. This path must fail there
    and pass once grooves stay in lockstep with rims/faces.
    """
    stones = "window.map && map.getLayer('stones') && map.queryRenderedFeatures({layers:['stones']}).length>0"
    await jump_wait(
        pg,
        "void map.jumpTo({center:[13.388,52.517], zoom:16.5, pitch:45, bearing:0}); if (window.KLCols && KLCols.finish) KLCols.finish()",
        stones,
    )
    start = await groove_sync_info(pg)
    assert start['nShaft'] > 0 and start['srcRim'] > 0, f"start 16.5 Berlin has no plaques: {start}"

    await jump_wait(
        pg,
        "void map.jumpTo({center:[13.455,52.517], zoom:16.5, pitch:45, bearing:0})",
        stones,
    )
    pan = await groove_sync_info(pg)
    assert pan['srcRim'] > 0 and pan['srcFace'] == pan['srcRim'], f"pan 16.5 rim/face mismatch: {pan}"
    assert pan['srcRim'] != start['srcRim'], f"pan 16.5 did not change the plaque box (test invalid): before={start} after={pan}"
    # Sources must stay in sync even below GROOVE_MINZOOM (so a later zoom-in is ready).
    assert pan['srcGr'] == pan['srcRim'], f"pan 16.5 left grooves stale: after={pan} before={start}"

    await jump_wait(
        pg,
        "void map.jumpTo({center:[13.455,52.517], zoom:18.2, pitch:55, bearing:0}); if (window.KLCols && KLCols.finish) KLCols.finish()",
        stones,
        1200,
    )
    close = await groove_sync_info(pg)
    assert close['srcGr'] > 0 and close['srcGr'] == close['srcRim'] == close['srcFace'], f"18.2 after pan: groove source stale: {close}"
    assert close['nFace'] > 0 and close['nGr'] > 0, f"18.2 after pan: faces painted but grooves did not: {close}"
    assert close['nGr'] == close['nFace'], f"18.2 after pan: painted groove/face counts differ: {close}"

    await jump_wait(
        pg,
        "void map.jumpTo({center:[13.455,52.517], zoom:18.2, pitch:55, bearing:40}); if (window.KLCols && KLCols.finish) KLCols.finish()",
        stones,
        800,
    )
    rot = await groove_sync_info(pg)
    assert rot['srcGr'] == rot['srcRim'] and rot['nGr'] > 0 and rot['nFace'] > 0, f"18.2 after rotate: grooves lost: {rot}"
    return {'start': start, 'pan': pan, 'zoom': close, 'rotate': rot}


async def main():
    check_source()
    base = (sys.argv[1].rstrip('/') + '/') if len(sys.argv) > 1 else None
    if not base:
        raise SystemExit('usage: v24-plaque-contrast-check.py BASE_URL')

    chrome = CHROME if Path(CHROME).exists() else None
    async with async_playwright() as p:
        b = await p.chromium.launch(
            executable_path=chrome, headless=True,
            args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist',
                  '--disable-dev-shm-usage', '--enable-precise-memory-info'],
        )
        ctx = await b.new_context(
            viewport={'width': 412, 'height': 915},
            is_mobile=True, has_touch=True, device_scale_factor=2,
            service_workers='block', locale='es-ES',
        )
        # ----- Day contrast + plaque presence -----
        pg = await ctx.new_page()
        errs, blocked = [], []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await block_counters(pg, blocked)
        await pg.goto(base + 'index.html?intro=0&lang=es&base=day', wait_until='domcontentloaded', timeout=180000)
        await wait_data(pg)
        info0 = await jump_group(pg, WESTEND, 19.5, 58)
        assert info0.get('ok') and info0['n'] == 4, info0
        await settle(pg, 1800)
        info = await plaque_info(pg)
        assert 'stones-1' in info['placa'] and 'stones-2' in info['placa'] and 'stones-grooves' in info['placa'], info
        assert info['minz'].get('stones-1') == 16.2 and info['minz'].get('stones-grooves') == 17.8, info['minz']
        assert info['srcCounts']['rim'] > 0 and info['srcCounts']['face'] > 0, info['srcCounts']
        assert info['srcCounts']['grooves'] > 0, info['srcCounts']
        # Grooves are one MultiPolygon per stone, not four features each.
        assert info['srcCounts']['grooves'] <= info['srcCounts']['face'] * 1.2, info['srcCounts']
        assert not info['textish'], f"plaque features carry text properties: {info}"
        assert info['light'] and abs(info['light']['position'][2] - 35) < 0.1 and abs(info['light']['intensity'] - 0.5) < 0.01, info['light']
        gold = info['gold']
        assert isinstance(gold, list) and gold[-1] == '#e0b020', gold

        day = await sample_regions(pg, WESTEND)
        assert day and day['col'] and day['bldg'], f"could not sample day pixels: {day}"
        cr_day = contrast_ratio(day['col'][:3], day['bldg'][:3])
        ch_col, ch_bldg = chroma(day['col'][:3]), chroma(day['bldg'][:3])
        # Top/plaque must be clearly more saturated gold than the beige façade, not a similar khaki.
        assert ch_col >= ch_bldg + 0.12, f"day chroma too close (col={day['col']} chroma={ch_col:.3f}, bldg={day['bldg']} chroma={ch_bldg:.3f})"
        assert day['col'][0] > day['col'][2] + 20 and day['col'][1] > day['col'][2] + 10, f"day top is not gold-like: {day['col']}"
        # Beige building should stay pale; gold shaft/top should not collapse into it.
        assert cr_day >= 1.15 or (ch_col - ch_bldg) >= 0.18, f"day contrast weak: ratio={cr_day:.2f} col={day['col']} bldg={day['bldg']}"

        ax = await run_axe(pg)
        assert not ax, f"axe violations on day street view: {ax}"
        await pg.close()

        # ----- Night contrast -----
        pg = await ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await block_counters(pg, blocked)
        await pg.goto(base + 'index.html?intro=0&lang=es&base=night', wait_until='domcontentloaded', timeout=180000)
        await wait_data(pg)
        infoN = await jump_group(pg, WESTEND, 19.5, 58)
        assert infoN.get('ok'), infoN
        await settle(pg, 1800)
        night = await sample_regions(pg, WESTEND)
        assert night and night['col'], f"could not sample night column: {night}"
        # Against dark slate buildings the gold must stay visibly warm and brighter.
        assert night['col'][0] > 90 and night['col'][1] > 60 and night['col'][0] > night['col'][2] + 15, f"night top not gold: {night['col']}"
        if night['bldg']:
            assert luma(night['col'][:3]) > luma(night['bldg'][:3]) * 1.15, f"night column not brighter than building: col={night['col']} bldg={night['bldg']}"
        lightN = await pg.evaluate("map.getLight()")
        assert abs(lightN['position'][2] - 35) < 0.1, lightN

        # ----- Overview zooms: a0 still uses the distant GOLD stops (unchanged) -----
        await pg.evaluate("void map.jumpTo({center:[10, 50.5], zoom:5.2, pitch:40, bearing:0})")
        await settle(pg, 800)
        ov = await pg.evaluate("""() => {
            const a0 = map.getLayer('a0') ? map.getPaintProperty('a0', 'fill-extrusion-color') : null;
            const light = map.getLight();
            const z = map.getZoom();
            return {a0, light, z, hasA0: !!map.getLayer('a0'), hasStones: !!map.getLayer('stones')};
        }""")
        assert ov['a0'] and ov['a0'][4] == '#c6a15b' and ov['a0'][6] == '#e0bc62', ov
        assert ov['hasA0'] and ov['z'] < 7, ov
        await pg.close()

        # ----- Perf: Berlin 16.5 (shafts) + 18.5 (plaques) + heap -----
        pg = await ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await block_counters(pg, blocked)
        await pg.goto(base + 'index.html?intro=0&lang=es&base=day', wait_until='domcontentloaded', timeout=180000)
        await wait_data(pg)
        await pg.wait_for_timeout(300)
        sz = await measure_zoom(pg, [13.388, 52.517], 16.5, 45, ['stones'])
        await settle(pg, 400)
        # Close zoom: fly to a stone actually on screen at 16.5 so plaques are in view.
        target = await pg.evaluate("""() => {
            const fs = map.getLayer('stones') ? map.queryRenderedFeatures({layers:['stones']}) : [];
            if (!fs.length) return [13.388, 52.517];
            const s = byId.get(fs[0].properties.id);
            return s ? [s._dlo, s._dla] : [13.388, 52.517];
        }""")
        close = await measure_zoom(pg, target, 18.5, 55, ['stones', 'stones-1', 'stones-2'])
        await settle(pg, 800)
        heap = await pg.evaluate("""() => {
            const m = performance.memory;
            return m ? {used_mb: +(m.usedJSHeapSize/1048576).toFixed(1),
                        total_mb: +(m.totalJSHeapSize/1048576).toFixed(1),
                        limit_mb: +(m.jsHeapSizeLimit/1048576).toFixed(1)} : null;
        }""")
        vis = await plaque_info(pg)

        # F1: pan at 16.5 then zoom to 18.2 (and a rotate) — grooves must follow rims/faces.
        # Run while the browser is still open (asserts and the OK line come after close).
        sync = await check_grooves_after_street_pan(pg)

        await pg.close()
        await ctx.close()
        await b.close()

        assert not errs, f"page errors: {errs}"
        assert not blocked, f"counter request escaped: {blocked}"
        assert sz['count'] > 0 and sz['sync_ms'] <= STREET_SYNC_MS and sz['painted_ms'] <= STREET_PAINT_MS, f"street 16.5 budget: {sz}"
        assert close['count'] > 0 and close['painted_ms'] <= CLOSE_PAINT_MS, f"close 18.5 plaque budget: {close}"
        if heap:
            assert heap['used_mb'] <= HEAP_MB, f"mobile heap {heap['used_mb']} MB exceeded {HEAP_MB} MB: {heap}"

        print(
            f"OK v24 plaque+contrast (412x915): day col={day['col']} bldg={day['bldg']} "
            f"ratio={cr_day:.2f} chroma={ch_col:.2f}/{ch_bldg:.2f}; "
            f"night col={night['col']} bldg={night.get('bldg')}; "
            f"street16.5={sz['sync_ms']}/{sz['painted_ms']}ms n={sz['count']}; "
            f"close18.5={close['sync_ms']}/{close['painted_ms']}ms n={close['count']}; "
            f"heap={heap}; plaque_feats={vis['srcCounts']}; "
            f"groove_sync pan srcRim/srcGr={sync['pan']['srcRim']}/{sync['pan']['srcGr']} "
            f"z18.2 nFace/nGr={sync['zoom']['nFace']}/{sync['zoom']['nGr']}"
        )


if __name__ == '__main__':
    asyncio.run(main())
