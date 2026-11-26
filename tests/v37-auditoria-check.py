"""v37 (auditoría externa, ítems A2/M4/A3/M1/M5): comprobaciones estáticas del sitio + capturas opcionales de 404.html.
Uso: python3 tests/v37-auditoria-check.py [--shots DIR]   (no publica; no abre el contador; solo archivos locales)"""
import json, os, re, sys
from html.parser import HTMLParser
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ROOT)
from pipeline import agents, sitefacts  # noqa: E402
from pipeline.config import load_sources  # noqa: E402
from pipeline.tests.test_licences_llms import licence_lines  # noqa: E402
errors, notes = [], []
err = errors.append
rd = lambda rel: open(os.path.join(ROOT, rel), encoding="utf-8").read()

# A2: cada data/*-added-*.json, en llms.txt bajo la familia de su fuente
src = load_sources()
got = licence_lines(rd("llms.txt"))
for sid, cfg in sorted(src.items()):
    m = agents.ADDED_RE.match((cfg.get("input") or {}).get("path") or "")
    if m:
        f = "data/%s-added-*.json" % m.group(1)
        if got.get(f) != [cfg["license_family"]]:
            err("llms.txt: %s bajo %s, la fuente %s dice %s" % (f, got.get(f), sid, cfg["license_family"]))
cat = json.loads(rd("api/v1/index.json"))
for fid, fam in cat["families"].items():
    for sid in fam["sources"]:
        if src.get(sid, {}).get("license_family", fid) != fid:
            err("api/v1/index.json: %s en %s" % (sid, fid))
notes.append("A2: %d archivos municipales en su familia; Den Haag → %s" % (len(got), got.get("data/denhaag-added-*.json")))
# M4: familia sin fichas, explicada y no anunciada
for fid, fam in cat["families"].items():
    if not fam["count_people"]:
        if "Search manifest – %s " % fid in rd("llms.txt"):
            err("llms.txt anuncia la búsqueda vacía %s" % fid)
        if "0 person records" not in fam.get("note_zero_people", ""):
            err("api/v1/index.json: %s sin note_zero_people" % fid)
        notes.append("M4: %s → %s" % (fid, fam["note_zero_people"][:90] + "…"))
if 'dl-de-by/find/index.json">búsqueda' in rd("index.html"):
    err("index.html noscript anuncia la búsqueda dl-de-by")
# A3: fechas y totales = datos
ch = sitefacts.apply(ROOT, check=True)
if ch:
    err("sitefacts: difieren %s (python3 -m pipeline.sitefacts)" % ch)
F = sitefacts.facts(ROOT)
notes.append("A3: mapa %s placas (%s ODbL + %s de %d listas), %d países, datos %s, build %s" % (
    "{:,}".format(F["map_total"]), "{:,}".format(F["odbl"]), "{:,}".format(F["added_total"]), F["lists"], F["countries"], F["data_date"], F["generated"]))


# M1: 404.html
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.tags = []
    def handle_starttag(s, t, a):
        s.tags.append((t, dict(a)))
h = rd("404.html"); p = P(); p.feed(h)
tags = p.tags
if not any(t == "meta" and a.get("name") == "robots" and "noindex" in a.get("content", "") for t, a in tags):
    err("404: sin noindex")
if any(t == "script" for t, a in tags) or "counter" in h:
    err("404: tiene script/contador")
for t, a in tags:
    for k in ("href", "src", "action"):
        v = a.get(k) or ""
        if re.match(r"(https?:)?//", v):
            err("404: recurso o enlace externo %s" % v)
        if v and not v.startswith(("/kauffmann-list/", "#", "data:")):
            err("404: ruta no absoluta %s (GitHub Pages la sirve en cualquier carpeta)" % v)
if not any(t == "a" and a.get("href") == "/kauffmann-list/" for t, a in tags):
    err("404: sin enlace a la portada")
langs = {a.get("lang") for t, a in tags if a.get("lang")}
if not {"es", "de", "en"} <= langs:
    err("404: faltan idiomas %s" % langs)
if not any(t == "h1" for t, a in tags) or not any(t == "main" for t, a in tags):
    err("404: sin h1/main")
if not any(t == "label" and a.get("for") == "q" for t, a in tags):
    err("404: campo de búsqueda sin label")


def lum(hx):
    c = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


pairs = {"texto": ("#1a1814", "#f4f1ea"), "enlace": ("#1f4f86", "#f4f1ea"), "secundario": ("#57524a", "#f4f1ea"),
         "otros idiomas": ("#57524a", "#fbf8f2"), "botón buscar": ("#6b4c16", "#ffffff"), "botón portada": ("#f6f3ec", "#07111f"),
         "cabecera": ("#f6f3ec", "#07111f"), "foco": ("#1f4f86", "#f4f1ea"), "borde campo (≥3:1)": ("#8a8274", "#ffffff")}
worst = min(pairs, key=lambda k: ratio(*pairs[k]))
for k, (a, b) in pairs.items():
    need = 3 if "≥3" in k or k == "foco" else 4.5
    if ratio(a, b) < need:
        err("404: contraste %s %.2f < %s" % (k, ratio(a, b), need))
notes.append("M1: 404.html sin scripts ni terceros, noindex, es/de/en; contraste mínimo %.2f:1 (%s)" % (ratio(*pairs[worst]), worst))
# M5: og:image
IMG = "https://roquena71-a11y.github.io/kauffmann-list/media/og-kauffmann.jpg"
for rel in ("index.html", "2d/index.html", "proyecto/index.html"):
    t = rd(rel)
    for need in ('property="og:image" content="%s"' % IMG, 'name="twitter:card" content="summary_large_image"', 'name="twitter:image" content="%s"' % IMG,
                 'property="og:image:alt"', 'property="og:title"', 'property="og:description"', 'property="og:image:width" content="1200"'):
        if need not in t:
            err("%s: falta %s" % (rel, need))
from PIL import Image  # noqa: E402
im = Image.open(os.path.join(ROOT, "media/og-kauffmann.jpg"))
sz = os.path.getsize(os.path.join(ROOT, "media/og-kauffmann.jpg"))
if im.size != (1200, 630) or sz > 200_000:
    err("og-kauffmann.jpg: %s, %d bytes" % (im.size, sz))
notes.append("M5: og:image 1200×630 %d KB en index, 2d y proyecto; twitter:card summary_large_image" % (sz // 1024))

shots = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
if shots:
    # 404.html servida bajo /kauffmann-list/ (como en GitHub Pages) para que las rutas absolutas funcionen; sin red externa
    import http.server, threading, socketserver, functools
    os.makedirs(shots, exist_ok=True)
    tmp = "/tmp/kl-v37-404-root"
    os.makedirs(tmp, exist_ok=True)
    if not os.path.islink(tmp + "/kauffmann-list"):
        os.symlink(ROOT, tmp + "/kauffmann-list")
    H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=tmp)
    H.log_message = lambda *a: None
    srv = socketserver.TCPServer(("127.0.0.1", 0), H); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=os.environ.get("CHROME_BIN", "/usr/bin/google-chrome"), args=["--disable-gpu"])
        for name, vp in (("404-desktop", {"width": 1280, "height": 800}), ("404-phone", {"width": 412, "height": 915})):
            pg = b.new_page(viewport=vp)
            ext = []
            pg.on("request", lambda r: ext.append(r.url) if not r.url.startswith(("http://127.0.0.1", "data:")) else None)
            pg.goto("http://127.0.0.1:%d/kauffmann-list/404.html" % port, wait_until="networkidle")
            if ext:
                err("404 (%s): peticiones externas %s" % (name, ext[:3]))
            if pg.evaluate("document.fonts.check('500 20px \"Frank Ruhl Libre\"')") is not True:
                err("404 (%s): no cargó la fuente del sitio" % name)
            sw = pg.evaluate("document.documentElement.scrollWidth > innerWidth")
            if sw:
                err("404 (%s): desborda en horizontal" % name)
            pg.keyboard.press("Tab")
            first = pg.evaluate("document.activeElement.textContent.trim()")
            out = os.path.join(shots, name + ".png")
            pg.screenshot(path=out, full_page=True)
            notes.append("captura %s (primer Tab: %s)" % (out, first))
            pg.close()
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        pg.goto("http://127.0.0.1:%d/kauffmann-list/media/og-kauffmann.jpg" % port)
        b.close()
    srv.shutdown()
for n in notes:
    print("· " + n)
for e in errors:
    print("ERROR: " + e)
print("v37-auditoria-check: %d errores" % len(errors))
sys.exit(1 if errors else 0)
