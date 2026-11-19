// v17: las actualizaciones llegan a los teléfonos (service worker) y la interfaz del mapa en el teléfono.
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.join(__dirname, '..');
function assert(c, m) { if (!c) throw new Error('FAIL: ' + m); }
const sw = fs.readFileSync(path.join(ROOT, 'sw.js'), 'utf8');
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const ver = /VERSION = 'kauffmann-v(\d+)-pages'/.exec(sw)[1];
// 1) Todos los CSS/JS propios de index.html llevan ?v=<versión del service worker> y están en SHELL con esa misma URL.
const shell = eval(sw.match(/const SHELL = (\[[\s\S]*?\]);/)[1]);
const own = [...html.matchAll(/(?:href|src)="([a-z0-9\-]+\.(?:js|css))(\?v=(\d+))?"/g)];
assert(own.length >= 10, 'own assets found ' + own.length);
for (const m of own) {
  assert(m[3] === ver, m[1] + ' lleva ?v=' + ver + ' (tiene ' + (m[2] || 'nada') + ')');
  assert(shell.includes(m[1] + '?v=' + ver), 'SHELL tiene ' + m[1] + '?v=' + ver);
  assert(fs.existsSync(path.join(ROOT, m[1])), 'existe ' + m[1]);
}
// 2) Estrategia: HTML y datos primero de la red; la caché solo sin conexión.
function makeSW() {
  const caches = new Map(), handlers = {}, log = [];
  const mkCache = () => { const m = new Map(); return {
    match: async (r, o) => { const k = typeof r === 'string' ? r : r.url; if (m.has(k)) return m.get(k); if (o && o.ignoreSearch) { for (const [kk, v] of m) if (kk.split('?')[0] === k.split('?')[0]) return v; } return undefined; },
    put: async (r, res) => { m.set(typeof r === 'string' ? r : r.url, res); }, addAll: async () => {},
    keys: async () => [...m.keys()].map(url => ({ url })), delete: async r => m.delete(typeof r === 'string' ? r : r.url), _m: m }; };
  const bg = [];
  const ctx = {
    self: { addEventListener: (t, f) => { handlers[t] = f; }, skipWaiting: () => {}, clients: { claim: async () => {}, matchAll: async () => [] } },
    caches: { open: async k => { if (!caches.has(k)) caches.set(k, mkCache()); return caches.get(k); }, keys: async () => [...caches.keys()], delete: async k => caches.delete(k),
      match: async r => { for (const c of caches.values()) { const h = await c.match(r); if (h) return h; } } },
    location: { origin: 'https://x.test', href: 'https://x.test/kauffmann-list/sw.js' }, URL, Request: function (u, o) { this.url = u; Object.assign(this, o); }, Response: { error: () => ({ error: true }) },
    fetch: async (r, o) => { log.push([r.url || r, o && o.cache]); if (ctx.offline) throw new Error('offline');
      if (ctx.redirect) return { ok: false, status: 0, type: 'opaqueredirect', url: r.url, body: 'redirect', headers: { get: () => null }, clone() { return this; } };
      if (ctx.delay) await new Promise(res => setTimeout(res, ctx.delay));
      const st = ctx.status || 200;
      const et = 'etag-' + ctx.etag;
      return { ok: st < 400, status: st, type: 'basic', url: r.url, body: (st < 400 ? 'net' : 'err' + st) + ':' + (r.url || r) + (ctx.tag || ''), headers: { get: () => et }, clone() { return this; } }; },
    etag: 1, offline: false, setTimeout, delay: 0, status: 0, tag: '' };
  ctx.self.location = ctx.location;
  vm.createContext(ctx); vm.runInContext(sw.replace(/^const /gm, 'var '), ctx);
  return { ctx, handlers, log, caches, bg };
}
async function fetchVia(S, url, mode) {
  let p; S.handlers.fetch({ request: { url, method: 'GET', mode: mode || 'cors' }, respondWith: x => { p = x; }, waitUntil: x => S.bg.push(x) });
  return p === undefined ? 'passthrough' : await p;
}
(async () => {
  const S = makeSW();
  const B = 'https://x.test/kauffmann-list/';
  // en línea: página y datos siempre de la red, revalidando la caché HTTP (cache: no-cache)
  let r = await fetchVia(S, B, 'navigate');
  assert(r.body === 'net:' + B, 'HTML de la red');
  assert(S.log.at(-1)[1] === 'no-cache', 'HTML revalida la caché HTTP');
  r = await fetchVia(S, B + 'data/stones.json');
  assert(r.body === 'net:' + B + 'data/stones.json' && S.log.at(-1)[1] === 'no-cache', 'stones.json de la red');
  // sin conexión: la última copia guardada
  S.ctx.offline = true;
  r = await fetchVia(S, B + 'data/stones.json');
  assert(r && r.body === 'net:' + B + 'data/stones.json', 'sin conexión: stones.json de la caché');
  r = await fetchVia(S, B + '?q=Gluck', 'navigate');
  assert(r && r.body === 'net:' + B, 'sin conexión: la página guardada');
  S.ctx.offline = false;
  // error del servidor (500) con copia guardada → la copia
  S.ctx.status = 500;
  r = await fetchVia(S, B + 'data/stones.json');
  assert(r.body === 'net:' + B + 'data/stones.json', 'error 500: la copia guardada');
  S.ctx.status = 0;
  // red lenta (> 4,5 s) con copia → la copia enseguida; la red renueva la copia por detrás
  S.ctx.delay = 6000; S.ctx.etag = 2; S.ctx.tag = '-nuevo';
  const t0 = Date.now(); r = await fetchVia(S, B + 'data/stones.json');
  assert(r.body === 'net:' + B + 'data/stones.json' && Date.now() - t0 < 5500, 'red lenta: la copia en ' + (Date.now() - t0) + ' ms');
  await Promise.all(S.bg);
  const c17 = S.caches.get('kauffmann-v' + ver + '-pages')._m;
  assert(c17.get(B + 'data/stones.json').body.endsWith('-nuevo'), 'la red lenta actualiza la copia por detrás');
  S.ctx.delay = 0; S.ctx.tag = '';
  // páginas con ?q=: una sola copia por página (no una por búsqueda)
  for (const q of ['A', 'B', 'C']) await fetchVia(S, B + 'index.html?q=' + q, 'navigate');
  const pageKeys = [...c17.keys()].filter(k => k.includes('index.html') || k.endsWith('/kauffmann-list/'));
  assert(pageKeys.every(k => !k.includes('?')), 'sin ?q en la caché: ' + pageKeys.join(' '));
  // /proyecto sin barra: el servidor redirige a /proyecto/ (respuesta «opaqueredirect»): se entrega tal cual, no la portada guardada
  S.ctx.redirect = true;
  r = await fetchVia(S, B + 'proyecto', 'navigate');
  assert(r.type === 'opaqueredirect', 'redirección /proyecto → /proyecto/ (no la portada): ' + r.body);
  r = await fetchVia(S, B + '2d', 'navigate');
  assert(r.type === 'opaqueredirect', 'redirección /2d → /2d/');
  assert(!c17.has(B + 'proyecto') && !c17.has(B + '2d'), 'la redirección no se guarda');
  S.ctx.redirect = false;
  // tope de copias de /api/ y /data/ (40 cada una; stones.json del SHELL nunca se borra)
  for (let i = 0; i < 70; i++) await fetchVia(S, B + 'api/find/p' + i + '.json');
  for (let i = 0; i < 55; i++) await fetchVia(S, B + 'data/search/s' + i + '.json');
  await new Promise(res => setTimeout(res, 50));
  const apiN = [...c17.keys()].filter(k => k.includes('/api/')).length, dataN = [...c17.keys()].filter(k => k.includes('/data/search/')).length;
  assert(apiN <= 40 && dataN <= 40 && c17.has(B + 'api/find/p69.json') && c17.has(B + 'data/stones.json'), 'tope de caché /api/ ' + apiN + ', /data/ ' + dataN);
  // otro origen (teselas, contador): no se toca
  assert(await fetchVia(S, 'https://tiles.openfreemap.org/x.pbf') === 'passthrough', 'teselas sin service worker');
  // 3) activar una versión nueva sobre una anterior recarga las pestañas abiertas (también páginas viejas sin listener)
  const S2 = makeSW(); const navs = [];
  await S2.ctx.caches.open('kauffmann-v' + (ver - 1) + '-pages');
  S2.ctx.self.clients.matchAll = async () => [{ url: B + '#s=n1', navigate: async u => navs.push(u) }];
  let w; S2.handlers.activate({ waitUntil: p => { w = p; } }); await w; await new Promise(r => setTimeout(r, 20));
  assert(navs.length === 1 && navs[0] === B + '#s=n1', 'recarga la pestaña abierta con su misma dirección');
  assert(!(await S2.ctx.caches.keys()).includes('kauffmann-v' + (ver - 1) + '-pages'), 'borra la caché vieja');
  const S3 = makeSW(); const navs3 = [];
  S3.ctx.self.clients.matchAll = async () => [{ url: B, navigate: async u => navs3.push(u) }];
  S3.handlers.activate({ waitUntil: p => { w = p; } }); await w; await new Promise(r => setTimeout(r, 20));
  assert(navs3.length === 0, 'primera instalación: no recarga');
  // la recarga no puede ir dentro de waitUntil (bloquea la activación: la navegación espera al propio service worker)
  const act = sw.slice(sw.indexOf("addEventListener('activate'"), sw.indexOf('const isFresh'));
  assert(/e\.waitUntil\(done\);[\s\S]*done\.then\([\s\S]*navigate/.test(act) && !/waitUntil\([^;]*navigate/.test(act), 'recarga fuera de waitUntil');
  // 4) La página escucha controllerchange y pide actualizar al volver a la pestaña
  assert(/updateViaCache: "none"/.test(html) && /controllerchange/.test(html) && /visibilitychange[\s\S]*reg\.update\(\)/.test(html), 'flujo de actualización en index.html');
  // 5) Ninguna cifra vieja escrita a mano en la web
  for (const f of ['index.html', 'app3d.js', 'mapui.js', 'people.js', 'llms.txt', 'llms-full.txt', '2d/index.html', '2d/app.js'])
    if (fs.existsSync(path.join(ROOT, f))) assert(!/64[.,\u00a0 ]?576/.test(fs.readFileSync(path.join(ROOT, f), 'utf8')), 'sin 64.576 en ' + f);
  // 6) Interfaz del teléfono: textos en ES/DE/EN y botones accesibles
  const ui = fs.readFileSync(path.join(ROOT, 'mapui.js'), 'utf8');
  for (const k of ['menu', 'layers', 'countries', 'sheetOpen', 'sheetClose', 'sheetFull', 'mapLabel', 'basemapsLabel', 'searchPhShort', 'NavigationControl.ZoomIn'.replace(/.*/, 'ml')]) for (const l of ['es', 'de', 'en'])
    { const blk = ui.split(new RegExp('\\n\\s+' + l + ': \\{'))[1].split(/\n\s+(?:es|de|en): \{|\n\s+\};/)[0];
      assert(new RegExp('\\b' + k + ':').test(blk), 'texto ' + k + ' en ' + l); }
  for (const id of ['menuBtn', 'layersBtn', 'sheetHandle']) assert(new RegExp('id="' + id + '"[^>]*aria-expanded="false"[^>]*aria-controls=|id="' + id + '"[^>]*aria-controls="[^"]+"[^>]*aria-expanded="false"').test(html), id + ' con aria-expanded/aria-controls');
  console.log('OK actualizaciones (v' + ver + ': ?v en ' + own.length + ' archivos, red primero para HTML y datos, recarga al activar), sin 64.576, textos del teléfono');
})().catch(e => { console.error(e.message || e); process.exit(1); });
