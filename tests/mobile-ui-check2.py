"""Ronda 2 (auditoría B): horizontal 844×390 y 667×375, tableta 768×1024, puntos de la intro, vigilia con hoja a la mitad,
tolerancia de toque en placas sueltas, textos del mapa en ES/DE/EN, foco tras «Volver» y diálogos, pie del menú.
Uso: python3 tests/mobile-ui-check2.py http://127.0.0.1:8842/   → shots/mobile-ui-check2.json y capturas en shots/after/"""
import asyncio, json, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1]
AXE = open('/workspace/tools-ai/node_modules/axe-core/axe.min.js').read()
TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
async def axe(pg, bp=False):
    await pg.add_script_tag(content=AXE)
    tags = TAGS + (['best-practice'] if bp else [])
    r = await pg.evaluate("(t)=>axe.run(document,{runOnly:{type:'tag',values:t}})", tags)
    return [[v['id'], v['impact'], [n['target'] for n in v['nodes']][:3]] for v in r['violations']]
OVER = """() => { const vis=e=>{const r=e.getBoundingClientRect(),cs=getComputedStyle(e);return r.width>0&&r.height>0&&cs.display!=='none'&&cs.visibility!=='hidden'&&r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth};
  const els=[...document.querySelectorAll('#layersBtn,#menuBtn,#rotBtns button,.maplibregl-ctrl-group button,.maplibregl-ctrl-attrib,#sheetHandle,#q,#vigilPause,#vigilExit,.basemaps.open button')].filter(vis);
  const bad=[]; for(let i=0;i<els.length;i++)for(let j=i+1;j<els.length;j++){ if(els[i].contains(els[j])||els[j].contains(els[i]))continue; const a=els[i].getBoundingClientRect(),b=els[j].getBoundingClientRect();
    const w=Math.min(a.right,b.right)-Math.max(a.left,b.left), h=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top); if(w>1&&h>1) bad.push([els[i].id||els[i].className.slice(0,25), els[j].id||els[j].className.slice(0,25), Math.round(w), Math.round(h)]); }
  return bad; }"""
MAPAREA = """() => { const m=document.querySelector('#map').getBoundingClientRect(), s=document.querySelector('#side').getBoundingClientRect(), t=document.querySelector('.top').getBoundingClientRect();
  // superficie del mapa que no tapa ni la lista ni la cabecera
  let free = m.width*m.height; const cut=(r)=>{const w=Math.max(0,Math.min(m.right,r.right)-Math.max(m.left,r.left)), h=Math.max(0,Math.min(m.bottom,r.bottom)-Math.max(m.top,r.top)); return w*h;};
  free -= cut(s) + cut(t); return Math.round(100*free/(innerWidth*innerHeight)); }"""
async def ctxpage(p, vp, mob, url='index.html?intro=0&lang=es', js=True):
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport=vp, is_mobile=mob, has_touch=mob, service_workers='block', locale='es-ES', java_script_enabled=js)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(BASE + url, wait_until='load')
    if js and 'intro=1' not in url:
        await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000 && document.querySelector('#countries button')", timeout=120000)
        await pg.wait_for_timeout(2500)
    return b, ctx, pg, errs
async def main():
    R = {}
    async with async_playwright() as p:
        # F1/F2/F3: horizontal y tableta
        for name, vp in (('l844', {'width': 844, 'height': 390}), ('l667', {'width': 667, 'height': 375}), ('t768', {'width': 768, 'height': 1024})):
            b, ctx, pg, errs = await ctxpage(p, vp, True)
            o = R[name] = {}
            o['mobile_layout'] = await pg.evaluate("getComputedStyle(document.querySelector('#layersBtn')).display!=='none'")
            o['map_free_pct_peek'] = await pg.evaluate(MAPAREA); o['overlaps_home'] = await pg.evaluate(OVER); o['axe_home'] = await axe(pg)
            await pg.screenshot(path=f'shots/after/{name}-1-inicio.png')
            await pg.click('#q'); await pg.fill('#q', 'Saks'); await pg.wait_for_timeout(1200)
            o['results_sheet'] = await pg.evaluate("[document.querySelector('#side').dataset.sheet, Math.round(document.querySelector('#side').getBoundingClientRect().height), Math.round(document.querySelector('#side').getBoundingClientRect().width)]")
            await pg.click('#results button[data-id]'); await pg.wait_for_timeout(4500)
            o['detail'] = await pg.evaluate("(()=>{const d=document.querySelector('#detail').getBoundingClientRect(); const s=DATA.find(x=>x.id===selected), p=map.project([s._dlo,s._dla]), side=document.querySelector('#side').getBoundingClientRect(), top=document.querySelector('.top').getBoundingClientRect();"
                                         "const free = innerWidth>innerHeight && innerHeight<=500 ? (p.x>side.right && p.x<innerWidth && p.y>top.bottom && p.y<innerHeight) : (p.y>top.bottom && p.y<side.top); return {detail_h:Math.round(d.height), stone_visible_on_free_map:free};})()")
            o['overlaps_detail'] = await pg.evaluate(OVER); o['axe_detail'] = await axe(pg)
            await pg.screenshot(path=f'shots/after/{name}-2-ficha.png')
            await pg.evaluate("document.querySelector('#back').click()"); await pg.wait_for_timeout(300)
            o['focus_after_back'] = await pg.evaluate("[document.activeElement.tagName, document.activeElement.dataset.id||document.activeElement.id]")
            await pg.evaluate("KLUI.setSheet('peek')"); await pg.wait_for_timeout(300)
            await pg.click('#layersBtn'); await pg.wait_for_timeout(400)
            o['layers_fit'] = await pg.evaluate("(()=>{const p=document.querySelector('#basemapsPanel'), r=p.getBoundingClientRect(); return {bottom:Math.round(r.bottom), vh:innerHeight, scrollable:p.scrollHeight>p.clientHeight, fits:r.bottom<=innerHeight};})()")
            await pg.evaluate("(()=>{const p=document.querySelector('#basemapsPanel'); p.scrollTop=p.scrollHeight;})()")
            o['last_layer_reachable'] = await pg.evaluate("(()=>{const b=[...document.querySelectorAll('#basemapsPanel button')].pop().getBoundingClientRect(); return b.bottom<=innerHeight && b.top>=0;})()")
            o['axe_layers'] = await axe(pg); o['overlaps_layers'] = await pg.evaluate(OVER)
            await pg.screenshot(path=f'shots/after/{name}-3-capas.png')
            o['errors'] = errs; await b.close()
        # F4: puntos de la intro
        b, ctx, pg, errs = await ctxpage(p, {'width': 390, 'height': 844}, True, 'index.html?intro=1&lang=es')
        await pg.wait_for_timeout(2500)
        R['intro_dots'] = await pg.evaluate("[...document.querySelectorAll('#introDots button')].map(b=>{const r=b.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height)];})")
        R['intro_axe'] = await axe(pg); await b.close()
        # F5: vigilia con la hoja a la mitad
        for vp in ({'width': 390, 'height': 844}, {'width': 412, 'height': 915}):
            b, ctx, pg, errs = await ctxpage(p, vp, True)
            await pg.evaluate("KLUI.setSheet('half')"); await pg.wait_for_timeout(400)
            await pg.click('#menuBtn'); await pg.click('#remember'); await pg.wait_for_timeout(2000)
            R[f'vigil_{vp["width"]}'] = {'overlaps': await pg.evaluate(OVER), 'axe': await axe(pg)}
            await pg.screenshot(path=f'shots/after/p{vp["width"]}-11-recordar-mitad.png'); await b.close()
        # F6: tolerancia de toque en una placa suelta (Dublín: las 6 no están agrupadas a zoom 14)
        b, ctx, pg, errs = await ctxpage(p, {'width': 390, 'height': 844}, True)
        T = {}
        one = None; CEN = None
        for cen in ([10.0, 53.55], [9.95, 53.58], [10.08, 53.6], [13.4, 52.52], [11.58, 48.14], [8.68, 50.11], [7.0, 50.94]):
            await pg.evaluate(f"void map.jumpTo({{center:{cen}, zoom:14.2, pitch:0, bearing:0}})"); await pg.wait_for_timeout(3000)
            one = await pg.evaluate("(()=>{const f=map.queryRenderedFeatures({layers:['kl-one']}).find(f=>{const p=map.project(f.geometry.coordinates); const others=map.queryRenderedFeatures([[p.x-30,p.y-30],[p.x+30,p.y+30]],{layers:['kl-one','kl-clu']}); return p.y>150&&p.y<600&&p.x>40&&p.x<330&&others.length===1;}); if(!f) return null; const p=map.project(f.geometry.coordinates); const r=map.getCanvas().getBoundingClientRect(); return [r.left+p.x, r.top+p.y, f.properties.id];})()")
            if one: CEN = cen; break
        T['target'] = one
        if one:
            for dx, dy in ((0, 0), (8, 0), (0, -10), (12, 0), (-9, 9)):
                await pg.evaluate("closeDetail(true); selected=null; KLUI.setSheet('peek')"); await pg.evaluate(f"void map.jumpTo({{center:{CEN}, zoom:14.2, pitch:0, bearing:0}})"); await pg.wait_for_timeout(1500)
                await pg.touchscreen.tap(one[0] + dx, one[1] + dy); await pg.wait_for_timeout(700)
                T[f'{dx},{dy}'] = await pg.evaluate("selected")
        R['tap_tolerance'] = T; await b.close()
        # F8 + F9 + F10: textos en DE/EN, foco al cerrar diálogos, pie del menú
        for lang in ('de', 'en', 'es'):
            b, ctx, pg, errs = await ctxpage(p, {'width': 390, 'height': 844}, True, f'index.html?intro=0&lang={lang}')
            await pg.evaluate(f"document.querySelector('.lang button[data-lang={lang}]').click()"); await pg.wait_for_timeout(500)
            R[f'labels_{lang}'] = await pg.evaluate("[document.querySelector('#map').getAttribute('aria-label'), document.querySelector('#basemapsPanel').getAttribute('aria-label'), document.querySelector('.maplibregl-ctrl-zoom-in').getAttribute('aria-label'), document.querySelector('.maplibregl-ctrl-compass').getAttribute('aria-label'), (document.querySelector('.maplibregl-ctrl-geolocate')||{getAttribute:()=>null}).getAttribute('aria-label'), document.querySelector('.maplibregl-canvas').getAttribute('aria-label'), document.querySelector('#q').placeholder, (()=>{const i=document.querySelector('#q'); return i.scrollWidth<=i.clientWidth;})()]")
            if lang == 'es':
                await pg.click('#menuBtn'); await pg.wait_for_timeout(300)
                R['menu_axe_bp'] = await axe(pg, bp=True)
                await pg.click('#aboutLink'); await pg.wait_for_timeout(500); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
                R['focus_after_about'] = await pg.evaluate("document.activeElement.id")
                await pg.click('#layersBtn'); await pg.click('#sourcesBtn'); await pg.wait_for_timeout(600); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
                R['focus_after_sources'] = await pg.evaluate("document.activeElement.id")
                await pg.screenshot(path='shots/after/p390-12-retrato.png')
            await b.close()
        # F7: sin JavaScript
        b, ctx, pg, errs = await ctxpage(p, {'width': 360, 'height': 780}, True, 'index.html', js=False)
        R['noscript'] = await pg.evaluate("[getComputedStyle(document.querySelector('#aboutLink')).display==='none'||document.querySelector('#aboutLink').getClientRects().length===0, document.querySelector('#replayIntro').getClientRects().length===0, getComputedStyle(document.body).backgroundColor]")
        await pg.screenshot(path='shots/after/p360-13-sin-js.png', full_page=True); await b.close()
    json.dump(R, open('shots/mobile-ui-check2.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(R, ensure_ascii=False))
asyncio.run(main())
