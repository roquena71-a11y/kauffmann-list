"""Versión ÚNICA de la app (tests/app-version.json → ?v=N en index.html y VERSION/SHELL de sw.js).
Uso:
  python3 tests/bump-version.py          sube la versión (N+1), reescribe index.html y sw.js y guarda las huellas
  python3 tests/bump-version.py --sync   no sube: reescribe con la versión actual y guarda las huellas (solo si aún no se publicó)
El test tests/version-test.cjs falla si cambia un archivo de la app (JS/CSS/fuentes/2d/proyecto…) sin subir la versión,
o si index.html, sw.js y app-version.json no dicen la misma versión."""
import hashlib, json, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
VF = os.path.join(ROOT, 'tests', 'app-version.json')
FRESH = re.compile(r'(\.html|/|\.json|\.jsonld|\.txt|\.xml|\.webmanifest)$')   # «red primero» en sw.js: no hace falta subir versión
def shell_list(sw):
    body = re.search(r'const SHELL = (\[[\s\S]*?\]);', sw).group(1)
    body = re.sub(r'//[^\n]*', '', body)
    return re.findall(r"'([^']+)'", body)
def hashes(sw):
    out = {}
    for f in shell_list(sw):
        f = f.split('?')[0]
        if FRESH.search(f): continue
        out[f] = hashlib.sha256(open(os.path.join(ROOT, f), 'rb').read()).hexdigest()[:16]
    return dict(sorted(out.items()))
def main():
    cur = json.load(open(VF))['version'] if os.path.exists(VF) else 17
    v = cur if '--sync' in sys.argv else cur + 1
    ip, sp = os.path.join(ROOT, 'index.html'), os.path.join(ROOT, 'sw.js')
    html = re.sub(r'((?:href|src)="[a-z0-9\-]+\.(?:js|css))(\?v=\d+)?"', lambda m: f'{m.group(1)}?v={v}"', open(ip).read())
    sw = open(sp).read()
    sw = re.sub(r"VERSION = 'kauffmann-v\d+-pages'", f"VERSION = 'kauffmann-v{v}-pages'", sw)
    sw = re.sub(r"(\.(?:js|css))\?v=\d+'", rf"\1?v={v}'", sw)
    sw = re.sub(r"con \?v=\d+", f"con ?v={v}", sw)
    open(ip, 'w').write(html); open(sp, 'w').write(sw)
    json.dump({'version': v, 'note': 'Fuente única de la versión. Cambiar solo con tests/bump-version.py', 'hashes': hashes(sw)}, open(VF, 'w'), indent=1)
    print('versión', v, '·', len(hashes(sw)), 'archivos con huella')
if __name__ == '__main__': main()
