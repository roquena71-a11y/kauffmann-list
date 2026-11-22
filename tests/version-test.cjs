// Versión única: tests/app-version.json = ?v= de index.html y 2d/index.html = VERSION y SHELL de sw.js; y ningún archivo de la app cambia sin subir la versión.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.join(__dirname, '..');
function assert(c, m) { if (!c) { console.error('FAIL: ' + m); process.exit(1); } }
const V = JSON.parse(fs.readFileSync(path.join(__dirname, 'app-version.json'), 'utf8'));
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const html2d = fs.readFileSync(path.join(ROOT, '2d', 'index.html'), 'utf8');
const sw = fs.readFileSync(path.join(ROOT, 'sw.js'), 'utf8');
const swv = +/VERSION = 'kauffmann-v(\d+)-pages'/.exec(sw)[1];
assert(swv === V.version, `sw.js VERSION v${swv} ≠ app-version.json ${V.version}`);
const own = [...html.matchAll(/(?:href|src)="([a-z0-9\-]+\.(?:js|css))(?:\?v=(\d+))?"/g)];
for (const m of own) assert(+m[2] === V.version, `${m[1]} en index.html lleva ?v=${m[2] || '(nada)'} y la versión es ${V.version}`);
const shell = sw.match(/const SHELL = (\[[\s\S]*?\]);/)[1].replace(/\/\/[^\n]*/g, '').match(/'([^']+)'/g).map(x => x.slice(1, -1));
for (const m of own) assert(shell.includes(`${m[1]}?v=${V.version}`), `SHELL de sw.js sin ${m[1]}?v=${V.version}`);
const own2d = [...html2d.matchAll(/(?:href|src)="((?:\.\.\/)?[a-z0-9\-]+\.(?:js|css))(?:\?v=(\d+))?"/g)];
assert(own2d.length >= 3, '2d/index.html debe referenciar al menos style.css, app.js y ../counter.js');
for (const m of own2d) {
  assert(+m[2] === V.version, `${m[1]} en 2d/index.html lleva ?v=${m[2] || '(nada)'} y la versión es ${V.version}`);
  const rel = path.posix.normalize(path.posix.join('2d', m[1]));
  assert(shell.includes(`${rel}?v=${V.version}`), `SHELL de sw.js sin ${rel}?v=${V.version}`);
}
// Todos los CSS/JS de vendor/ y fonts/ que carga 2d/index.html también deben estar en SHELL para que 2D funcione sin conexión.
for (const m of html2d.matchAll(/(?:href|src)="((?:\.\.\/)?(?:vendor|fonts)\/[^"?#]+)(?:\?v=\d+)?"/g)) {
  const rel = path.posix.normalize(path.posix.join('2d', m[1]));
  assert(shell.includes(rel), `SHELL de sw.js sin recurso 2D ${rel}`);
}
const FRESH = /(\.html|\/|\.json|\.jsonld|\.txt|\.xml|\.webmanifest)$/;
const now = {};
for (const f0 of shell) { const f = f0.split('?')[0]; if (FRESH.test(f)) continue; now[f] = crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, f))).digest('hex').slice(0, 16); }
const changed = Object.keys(now).filter(f => V.hashes[f] !== now[f]).concat(Object.keys(V.hashes).filter(f => !(f in now)));
assert(!changed.length, `cambiaron ${changed.join(', ')} sin subir la versión (los teléfonos seguirían con la copia vieja). Ejecute: python3 tests/bump-version.py`);
console.log(`OK versión única v${V.version}: index.html (${own.length} archivos ?v), 2d/index.html (${own2d.length} archivos ?v), sw.js y ${Object.keys(now).length} huellas al día`);
