"""Sin JavaScript (Chrome headless): el texto, la cabecera, el pie y los enlaces a los datos se ven y se pueden pulsar.
Uso: python3 tests/noscript-check.py http://localhost:8831/index.html   (necesita playwright y Chrome; no publica nada)"""
import sys
from playwright.sync_api import sync_playwright
url=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for vp in ({'width':390,'height':800},{'width':1366,'height':768}):
        c=b.new_context(java_script_enabled=False,viewport=vp)
        pg=c.new_page(); pg.goto(url); pg.wait_for_timeout(500)
        res=pg.evaluate("""()=>{const out={};
          const vis=(e)=>{const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&cs.display!=='none'};
          const ns=document.querySelector('.noscript');out.noscript=ns?vis(ns):null;
          out.intro=getComputedStyle(document.getElementById('intro')).display;
          out.links=[...document.querySelectorAll('.noscript a, .foot a, .top a')].map(a=>{const r=a.getBoundingClientRect();const cx=r.x+r.width/2,cy=r.y+r.height/2;const el=document.elementFromPoint(cx,cy);return [a.getAttribute('href')||a.textContent, vis(a), el===a||a.contains(el)]});
          out.top=vis(document.querySelector('.top'));out.foot=vis(document.querySelector('.foot'));
          out.scrollH=document.documentElement.scrollHeight;return out}""")
        print(vp['width'], res['noscript'], res['intro'], res['top'], res['foot'], res['scrollH'])
        assert res['noscript'] and res['intro'] == 'none' and res['top'] and res['foot'], res
        bad = [l for l in res['links'] if not l[1] or (not l[2] and l[0] != '#')]
        assert not bad, bad
        c.close()
    b.close()
print('noscript-check: OK')
