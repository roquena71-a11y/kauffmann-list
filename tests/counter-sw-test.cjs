// Contador propio (activado), service worker v16 y textos de las auditorías.
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
function assert(c, m) { if (!c) throw new Error('FAIL: ' + m); }
const C = require('../counter.js');

// --- Contador propio ---
assert(C.config.enabled === true && C.config.endpoint === 'https://kl-contador.roquena71.workers.dev/hit', 'counter ON with our own endpoint');
assert(C.isOn() === true, 'isOn true');
const EP = 'https://kl-contador.carlos-k.workers.dev/hit';
const on = { enabled: true, endpoint: EP };
const loc = (h, p, proto) => ({ hostname: h, host: h, pathname: p, protocol: proto || 'https:' });
const L = loc('roquena71-a11y.github.io', '/kauffmann-list/');
assert(C.countUrl(on, L, {}, '') === EP, 'counts a direct visit');
assert(C.countUrl(on, L, {}, 'https://www.google.com/') === EP, 'counts a visit coming from elsewhere');
assert(C.countUrl(on, loc('roquena71-a11y.github.io', '/kauffmann-list/2d/'), {}, 'https://roquena71-a11y.github.io/kauffmann-list/') === '', 'moving between sections is not a new visit');
assert(C.section('/kauffmann-list/2d/') === '/2d/' && C.section('/kauffmann-list/proyecto/blatt-de.html') === '/proyecto/' && C.section('/kauffmann-list/') === '/', 'sections');
const withQ = { hostname: 'roquena71-a11y.github.io', host: 'roquena71-a11y.github.io', pathname: '/kauffmann-list/', protocol: 'https:', search: '?q=Löpert', hash: '#s=n676133185' };
const r = C.request(withQ);
assert(r.body === '/' && C.countUrl(on, withQ, {}, '') === EP, 'only the section is sent, never ?q= or #s=');
assert(r.credentials === 'omit' && r.mode === 'no-cors' && r.method === 'POST' && r.referrerPolicy === 'origin', 'no credentials, origin only');
assert(C.countUrl(on, L, { doNotTrack: '1' }, '') === '', 'DNT respected');
assert(C.countUrl(on, L, { globalPrivacyControl: true }, '') === '', 'GPC respected');
assert(C.countUrl(on, L, { webdriver: true }, '') === '', 'automated browsers not counted');
assert(C.countUrl(on, loc('localhost', '/', 'http:'), {}, '') === '', 'never on localhost');
for (const bad of ['https://evil.example/hit', 'https://kl-contador.x.workers.dev/hit?x', 'http://kl-contador.x.workers.dev/hit', 'https://otro.x.workers.dev/hit', 'https://lista.goatcounter.com/count'])
  assert(C.countUrl({ enabled: true, endpoint: bad }, L, {}, '') === '', 'rejects endpoint ' + bad);
assert(C.countUrl({ enabled: 'yes', endpoint: EP }, L, {}, '') === '', 'flag must be literally true');
const src = fs.readFileSync(path.join(ROOT, 'counter.js'), 'utf8').replace(/\/\*[\s\S]*?\*\//, '');
assert(!/document\.cookie|localStorage|sessionStorage|indexedDB|goatcounter|new Image/.test(src), 'no cookies/storage/third-party');

// --- Service worker ---
const sw = fs.readFileSync(path.join(ROOT, 'sw.js'), 'utf8');
const appVer = JSON.parse(fs.readFileSync(path.join(ROOT, 'tests/app-version.json'), 'utf8')).version;
assert(new RegExp("VERSION = 'kauffmann-v" + appVer + "-pages'").test(sw), 'sw v' + appVer);
const shell = eval(sw.match(/const SHELL = (\[[\s\S]*?\]);/)[1]);
const bare = shell.map(f => f.replace(/\?v=\d+$/, ''));
for (const f of ['source-links.js', 'dedupe.js', 'counter.js', 'app3d.js', 'people.js', 'mapui.js', 'mapui.css', 'index.html']) assert(bare.includes(f), 'SHELL has ' + f);
for (const f of bare) { const p = path.join(ROOT, f === './' ? 'index.html' : f.endsWith('/') ? f + 'index.html' : f); assert(fs.existsSync(p), 'SHELL file exists: ' + f); }
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const order = ['source-links.js', 'dedupe.js', 'app3d.js', 'people.js', 'mapui.js', 'counter.js'].map(f => { const m = new RegExp('src="' + f.replace('.', '\\.') + '(\\?v=\\d+)?"').exec(html); return m ? m.index : -1; });
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
console.log('OK counter propio (on, DNT/GPC, sin cookies, solo sección), sw v' + appVer + ' + SHELL, labels, focus contrast ' + cr('#9cc3ff', '#0e1726').toFixed(2) + ':1');
