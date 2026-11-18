import asyncio, json, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1]
PAGES = sys.argv[2:] or ['2d/', 'proyecto/', 'proyecto/blatt-de.html', 'proyecto/blatt-en.html']
AXE = open('/workspace/tools-ai/node_modules/axe-core/axe.min.js').read()
TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice']
async def main():
    async with async_playwright() as p:
        total = 0
        for name, vp, mobile in (('desktop', {'width': 1366, 'height': 800}, False), ('mobile', {'width': 390, 'height': 844}, True)):
            b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True)
            ctx = await b.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile, service_workers='block', locale='es-ES')
            for pgname in PAGES:
                pg = await ctx.new_page()
                await pg.goto(BASE + pgname, wait_until='load'); await pg.wait_for_timeout(2500)
                await pg.add_script_tag(content=AXE)
                r = await pg.evaluate("(tags)=>axe.run(document,{runOnly:{type:'tag',values:tags}})", TAGS)
                print(name, pgname, 'violaciones:', len(r['violations']))
                for v in r['violations']:
                    total += 1
                    print('   ', v['impact'], v['id'], [n['target'] for n in v['nodes']][:3], '|', v['help'])
                await pg.close()
            await b.close()
        print('TOTAL', total)
asyncio.run(main())
