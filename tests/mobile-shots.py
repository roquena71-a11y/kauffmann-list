"""Capturas de pantalla en teléfono y escritorio (no publica nada).
Uso: python3 tests/mobile-shots.py BASE_URL OUT_DIR"""
import asyncio, sys, os
from playwright.async_api import async_playwright
BASE, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
VPS = [('p360', 360, 780, True), ('p412', 412, 915, True), ('desk', 1366, 800, False)]
async def wait_data(pg):
    await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000", timeout=90000)
    await pg.wait_for_timeout(2500)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True,
            args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        for name, w, h, mob in VPS:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob, device_scale_factor=1, service_workers='block', locale='es-ES')
            pg = await ctx.new_page()
            errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
            await wait_data(pg); await pg.wait_for_timeout(3000)
            await pg.screenshot(path=f'{OUT}/{name}-1-inicio.png')
            # Dublín a escala regional (como Carlos: mover el mapa sin buscar)
            await pg.evaluate("void map.jumpTo({center:[-6.9,53.3], zoom:6.3, pitch:0, bearing:0})")
            await pg.wait_for_timeout(4000)
            await pg.screenshot(path=f'{OUT}/{name}-2-dublin-z6.png')
            await pg.evaluate("void map.jumpTo({center:[-6.28,53.333], zoom:11, pitch:30, bearing:0})")
            await pg.wait_for_timeout(4000)
            await pg.screenshot(path=f'{OUT}/{name}-3-dublin-z11.png')
            # búsqueda
            await pg.evaluate("void map.jumpTo({center:[10.45,51], zoom:5})")
            q = pg.locator('#q')
            if not await q.is_visible():
                for sel in ('#searchFab', '.searchbar'):
                    if await pg.locator(sel).count() and await pg.locator(sel).first.is_visible(): await pg.locator(sel).first.click(); break
            await q.fill('Gluck'); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=f'{OUT}/{name}-4-busqueda.png')
            await pg.locator('#results button[data-id]').first.click()
            await pg.wait_for_timeout(5000)
            await pg.screenshot(path=f'{OUT}/{name}-5-ficha.png')
            if await pg.locator('#layersBtn').is_visible():
                await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load'); await wait_data(pg)
                await pg.locator('#layersBtn').click(); await pg.wait_for_timeout(800)
                await pg.screenshot(path=f'{OUT}/{name}-6-capas.png')
                await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
                await pg.locator('#menuBtn').click(); await pg.wait_for_timeout(600)
                await pg.screenshot(path=f'{OUT}/{name}-7-menu.png')
                await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
                # tocar el cuadro de Irlanda en la lista de países
                await pg.locator('#countries button[data-cc=IE]').click(); await pg.wait_for_timeout(4500)
                await pg.screenshot(path=f'{OUT}/{name}-8-irlanda.png')
            ov = await pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
            print(name, 'errores:', errs, 'sin desbordamiento horizontal:', ov)
            await ctx.close()
        await b.close()
asyncio.run(main())
