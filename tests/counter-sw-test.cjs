// Contador (desactivado), service worker v12 y textos de las auditorías.
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
function assert(c, m) { if (!c) throw new Error('FAIL: ' + m); }
const C = require('../counter.js');

// --- Contador ---
assert(C.config.enabled === false && C.config.endpoint === '', 'counter is OFF in the code that would be published');
assert(C.isOn() === false, 'isOn false by default');
const on = { enabled: true, endpoint: 'https://lista-kauffmann.goatcounter.com/count' };
const loc = (h, p, proto) => ({ hostname: h, pathname: p, protocol: proto || 'https:' });
let u = C.countUrl(on, loc('roquena71-a11y.github.io', '/kauffmann-list/'), {}, 'r1');
assert(u === 'https://lista-kauffmann.goatcounter.com/count?p=%2F&r=&t=&rnd=r1', 'pixel url ' + u);
assert(C.countUrl(on, loc('roquena71-a11y.github.io', '/kauffmann-list/2d/'), {}, 1).includes('p=%2F2d%2F'), '2d section');
assert(C.countUrl(on, loc('roquena71-a11y.github.io', '/kauffmann-list/proyecto/blatt-de.html'), {}, 1).includes('p=%2Fproyecto%2F'), 'proyecto section');
// nunca el nombre buscado ni la ficha
const withQ = { hostname: 'roquena71-a11y.github.io', pathname: '/kauffmann-list/', protocol: 'https:', search: '?q=Löpert', hash: '#s=n676133185' };
u = C.countUrl(on, withQ, {}, 1);
assert(!/L%C3%B6pert|Löpert|n676133185|q=/.test(u), 'no search/hash leaked ' + u);
assert(C.countUrl(on, loc('roquena71-a11y.github.io', '/'), { doNotTrack: '1' }, 1) === '', 'DNT respected');
assert(C.countUrl(on, loc('roquena71-a11y.github.io', '/'), { globalPrivacyControl: true }, 1) === '', 'GPC respected');
assert(C.countUrl(on, loc('roquena71-a11y.github.io', '/'), { webdriver: true }, 1) === '', 'automated browsers not counted');
assert(C.countUrl(on, loc('localhost', '/', 'http:'), {}, 1) === '', 'never on localhost');
assert(C.countUrl({ enabled: true, endpoint: 'https://evil.example/count' }, loc('x.org', '/'), {}, 1) === '', 'only *.goatcounter.com/count');
assert(C.countUrl({ enabled: 'yes', endpoint: on.endpoint }, loc('x.org', '/'), {}, 1) === '', 'flag must be literally true');
const csrc = fs.readFileSync(path.join(ROOT, 'counter.js'), 'utf8');
assert(!/document\.cookie|localStorage|sessionStorage|indexedDB|gc\.zgo\.at/.test(csrc.replace(/\/\*[\s\S]*?\*\//, '')), 'no cookies/storage/third-party script in counter.js');
assert(/referrerPolicy = 'no-referrer'/.test(csrc), 'pixel sends no referrer');

// --- Service worker ---
const sw = fs.readFileSync(path.join(ROOT, 'sw.js'), 'utf8');
assert(/VERSION = 'kauffmann-v12-pages'/.test(sw), 'sw v12');
const shell = eval(sw.match(/const SHELL = (\[[\s\S]*?\]);/)[1]);
for (const f of ['source-links.js', 'dedupe.js', 'counter.js', 'app3d.js', 'people.js', 'index.html']) assert(shell.includes(f), 'SHELL has ' + f);
for (const f of shell) { const p = path.join(ROOT, f === './' ? 'index.html' : f.endsWith('/') ? f + 'index.html' : f); assert(fs.existsSync(p), 'SHELL file exists: ' + f); }
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const order = ['source-links.js', 'dedupe.js', 'app3d.js', 'people.js', 'counter.js'].map(f => html.indexOf('src="' + f + '"'));
assert(order.every(i => i > 0) && order.every((v, i) => !i || v > order[i - 1]), 'script order ' + order);

// --- Textos ---
const app = fs.readFileSync(path.join(ROOT, 'app3d.js'), 'utf8');
assert(!/Biograf[ií]a oficial|Offizielle Biografie|Official biography/.test(app.split('// Source links (audits A/B/C')[1]), 'no «oficial» in the new labels');
assert(/Biografía de la iniciativa Stolpersteine Hamburg/.test(app) && /Biografie bei Stolpersteine Hamburg/.test(app), 'accurate bio label');
assert(/scopeNote:'Yad Vashem y el Gedenkbuch registran a las víctimas judías/.test(app), 'neutral scope note ES');
assert(!/add\(u, 'OpenStreetMap'\)|'Wikidata \(persona\/Person\) '/.test(app), 'no OSM/Wikidata inside source search');
const css = fs.readFileSync(path.join(ROOT, 'style3d.css'), 'utf8');
assert(/body\.dark\{--focus:#9cc3ff\}/.test(css), 'dark focus colour');
function lum(h) { const c = [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255).map(x => x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; }
const cr = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
for (const bg of ['#0e1726', '#07111f', '#101c30', '#17263c', '#152033']) assert(cr('#9cc3ff', bg) >= 3, 'focus contrast ≥3:1 on ' + bg + ' = ' + cr('#9cc3ff', bg).toFixed(2));
assert(cr('#9cc3ff', '#07111f') >= 3, 'focus vs its navy halo');
console.log('OK counter (off, DNT/GPC, no leak), sw v12 + SHELL, labels, focus contrast ' + cr('#9cc3ff', '#0e1726').toFixed(2) + ':1');
