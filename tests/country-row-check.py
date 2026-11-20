"""v20: con ~30 países la fila es plegable (6 + «Más países (N)», aria-expanded; abierta, con scroll propio de altura limitada); en horizontal bajo siguen todos en una fila que se desliza.
v19 ronda 2 (auditoría C-A1/A-A1): la fila de países en el teléfono no esconde botones sin avisar.
Vertical (360×740, 412×915): los 6 botones se parten en líneas y están TODOS dentro de la pantalla, cada uno de >= 24 px (WCAG 2.5.8).
Horizontal bajo (844×390, 667×375): la fila se desliza, tiene degradado «hay más» (máscara) mientras no está al final, y al desplazarla hasta el final se ve el último (el último país) y se quita el degradado. Ningún botón queda cortado por abajo.
Solo localhost. Uso: python3 tests/country-row-check.py BASE_URL"""
import asyncio, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1]
async def main():
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        for w, h, land in ((360, 740, False), (412, 915, False), (844, 390, True), (667, 375, True)):
            ctx = await b.new_context(viewport={'width': w, 'height': h}, is_mobile=True, has_touch=True, service_workers='block', locale='es-ES')
            pg = await ctx.new_page()
            await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
            await pg.wait_for_function("document.querySelectorAll('#countries button').length>=6", timeout=120000)
            await pg.wait_for_timeout(2000)
            r = await pg.evaluate("""()=>{const c=document.querySelector('#countries'), bs=[...c.querySelectorAll('button')], vh=innerHeight, vw=innerWidth;
              const vis=()=>bs.filter(b=>{const r=b.getBoundingClientRect(), cr=c.getBoundingClientRect(); return r.bottom<=vh+.5 && r.left>=cr.left-.5 && r.right<=cr.right+.5 && r.right<=vw+.5}).length;
              const mask=getComputedStyle(c).maskImage||getComputedStyle(c).webkitMaskImage||'none';
              const before={vis:vis(), mask, atEnd:c.classList.contains('at-end'), scrolls:c.scrollWidth>c.clientWidth+2};
              c.scrollLeft=c.scrollWidth; return new Promise(res=>setTimeout(()=>res({before, after:{vis:vis(), lastVisible:(()=>{const r=bs[bs.length-1].getBoundingClientRect(), cr=c.getBoundingClientRect(); return r.right<=cr.right+.5&&r.left>=cr.left-.5&&r.bottom<=vh+.5})(), atEnd:c.classList.contains('at-end'), mask:getComputedStyle(c).maskImage||'none'}, minH:Math.min(...bs.map(b=>b.getBoundingClientRect().height)), minW:Math.min(...bs.map(b=>b.getBoundingClientRect().width))}),150));}""")
            print(w, h, r)
            if r['minH'] < 24 or r['minW'] < 24: bad.append((w, h, 'objetivo < 24 px'))
            if not land:
                if r['before']['vis'] != 7 or r['before']['scrolls']: bad.append((w, h, 'plegada: se esperan 6 países + «Más países» visibles sin desplazar', r['before']['vis']))
                mb = await pg.query_selector('#countries button.more')
                if not mb: bad.append((w, h, 'falta el botón «Más países»'))
                else:
                    if await mb.get_attribute('aria-expanded') != 'false': bad.append((w, h, 'aria-expanded debería ser false'))
                    await mb.click(); await pg.wait_for_timeout(300)
                    o = await pg.evaluate("""()=>{const c=document.querySelector('#countries'), cr=c.getBoundingClientRect(), bs=[...c.querySelectorAll('button')];
                      const more=c.querySelector('button.more'); const last=bs.filter(b=>b!==more).pop(); c.scrollTop=c.scrollHeight; const lr=last.getBoundingClientRect(), cr2=c.getBoundingClientRect();
                      return {exp:more.getAttribute('aria-expanded'), n:bs.length-1, h:Math.round(cr.height), maxH:getComputedStyle(c).maxHeight, bottom:Math.round(cr.bottom), vh:innerHeight, lastVisible: lr.bottom<=cr2.bottom+1 && lr.top>=cr2.top-1, bigEnough: bs.every(b=>b.getBoundingClientRect().height>=24)}}""")
                    print('  abierta', o)
                    if o['exp'] != 'true' or o['n'] < 20: bad.append((w, h, 'abierta: aria-expanded/true y todos los países', o))
                    if o['h'] > 190: bad.append((w, h, 'abierta: la lista crece demasiado (>190 px); debe tener scroll propio', o))
                    if not o['lastVisible']: bad.append((w, h, 'abierta: el último país no es alcanzable con el scroll', o))
                    if o['bottom'] > o['vh']: bad.append((w, h, 'abierta: la lista se sale de la pantalla', o))
            else:
                if not r['before']['scrolls']: bad.append((w, h, 'se esperaba fila deslizable'))
                elif r['before']['mask'] == 'none' or r['before']['atEnd']: bad.append((w, h, 'falta el degradado de «hay más»'))
                if r['before']['vis'] < 1 or r['before']['vis'] >= 20: bad.append((w, h, 'la fila debería enseñar algún botón y dejar otros por ver'))
                if not r['after']['lastVisible'] or not r['after']['atEnd'] or r['after']['mask'] != 'none': bad.append((w, h, 'al desplazar hasta el final debe verse el último botón (el último país) y quitarse el degradado'))
            await ctx.close()
        await b.close()
    if bad: print('FALLO', bad); sys.exit(1)
    print('OK: fila de países en el teléfono (6 + «Más países» plegable en vertical, con scroll propio al abrir; degradado «hay más» en horizontal bajo)')
asyncio.run(main())
