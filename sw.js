/* Kauffmann List — service worker: offline app shell + last downloaded stone data.
   Map tiles and orthophoto WMS requests are NOT cached (keep them online; no bulk prefetch).
   v17: las actualizaciones llegan a los teléfonos.
   · Páginas HTML y datos (data/*.json, api/*) → primero la red (revalidando la caché HTTP); la copia guardada solo sin conexión.
     Antes (≤ v16) la página y data/stones.json salían primero de la caché: la primera visita tras publicar mostraba la versión
     anterior (p. ej. «64.576 placas», la cifra de v13).
   · Archivos de la app → con ?v=N en index.html y en SHELL; nueva versión = URL nueva, nunca mezcla de versiones.
   · Al activarse una versión nueva sobre una anterior, las pestañas abiertas se recargan una vez (también las de una versión
     antigua, que no saben escuchar 'controllerchange'). */
const VERSION = 'kauffmann-v18-pages';
const SHELL = ['./','index.html',
  // index.html pide estos archivos con ?v=18: así una página nueva nunca se mezcla con archivos viejos de la caché.
  'style.css?v=18','style3d.css?v=18','mapui.css?v=18','app3d.js?v=18','people.js?v=18','columns.js?v=18','imagery.js?v=18','source-links.js?v=18','dedupe.js?v=18','counter.js?v=18','mapui.js?v=18',
  'manifest.webmanifest',
  'kauffmann-list.jsonld','robots.txt','sitemap.xml','data/bio/manifest.json',
  'proyecto/','proyecto/index.html','proyecto/proyecto.css','proyecto/proyecto.js',
  'proyecto/blatt-de.html','proyecto/blatt-en.html',
  'proyecto/kauffmann-liste-kurz-de.pdf','proyecto/kauffmann-liste-kurz-en.pdf',
  'fonts/fonts.css',
  'fonts/j8_w6_fAw7jrcalD7oKYNX0QfAnPW77l4ajn.woff2',
  'fonts/j8_w6_fAw7jrcalD7oKYNX0QfAnPW7Dl4Q.woff2',
  'fonts/j8_w6_fAw7jrcalD7oKYNX0QfAnPW7Ll4ajn.woff2',
  'fonts/NGS6v5_NC0k9P9GKTbFzsQ.woff2',
  'fonts/NGS6v5_NC0k9P9GYTbFzsQ.woff2',
  'fonts/NGS6v5_NC0k9P9H0TbFzsQ.woff2',
  'fonts/NGS6v5_NC0k9P9H2TbE.woff2',
  'fonts/NGS6v5_NC0k9P9H4TbFzsQ.woff2',
  'geo/de-states.json',
  'vendor/maplibre/maplibre-gl.js','vendor/maplibre/maplibre-gl.css',
  '2d/','2d/index.html','2d/app.js','2d/style.css',
  'vendor/leaflet/leaflet.js','vendor/leaflet/leaflet.css','vendor/leaflet.markercluster/leaflet.markercluster.js','vendor/leaflet.markercluster/MarkerCluster.css',
  'icons/icon-192.png','icons/icon-512.png','icons/apple-touch-icon.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => {
  const done = (async () => {
    const keys = await caches.keys();
    const old = keys.filter(k => k !== VERSION && k.startsWith('kauffmann-'));
    await Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)));
    await self.clients.claim();
    return old.length > 0;
  })();
  e.waitUntil(done);
  // Recargar las pestañas abiertas DESPUÉS de activarse (no dentro de waitUntil: la recarga necesita este service worker
  // ya activo para responder, y esperarla aquí lo bloquearía). Solo si había una versión anterior.
  done.then(async hadOld => {
    if (!hadOld) return;
    const wins = await self.clients.matchAll({ type: 'window' });
    await Promise.all(wins.map(w => w.navigate(w.url).catch(() => null)));
  }).catch(() => {});
});
const isFresh = (url, req) => req.mode === 'navigate' || /\.html$|\/$/.test(url.pathname) ||
  url.pathname.includes('/data/') || url.pathname.includes('/api/') || /\.(json|jsonld|txt|xml|webmanifest)$/.test(url.pathname);
// Clave de caché: las páginas se guardan sin «?q=…»/«#…» (una sola copia por página, no una por búsqueda).
const keyFor = (req, url) => req.mode === 'navigate' ? new Request(url.origin + url.pathname) : req;
const SLOW_MS = 4500;   // red lenta: pasado este tiempo, si hay copia guardada se muestra la copia (y la red la renueva por detrás)
// Tope de copias en tiempo de ejecución: como mucho MAX_RT respuestas de /data/ y otras tantas de /api/; se borran las más antiguas.
const MAX_RT = 40;
async function trim(c, url) {
  const part = url.pathname.includes('/api/') ? '/api/' : url.pathname.includes('/data/') ? '/data/' : null;
  if (!part) return;
  const keep = new Set(SHELL.map(u => new URL(u, self.location.href).href));
  const core = p => /\/data\/(stones\.json|bio\/manifest\.json)$/.test(p);   // las placas y el índice de biografías no se borran nunca
  const ks = (await c.keys()).filter(k => { const p = new URL(k.url).pathname; return p.includes(part) && !keep.has(k.url) && !core(p); });
  for (const k of ks.slice(0, Math.max(0, ks.length - MAX_RT))) await c.delete(k);
}
async function networkFirst(e, req, url) {
  const c = await caches.open(VERSION), key = keyFor(req, url);
  const cached = c.match(key).then(h => h || (req.mode === 'navigate' ? c.match('index.html') : undefined));
  const net = fetch(req, { cache: 'no-cache' }).then(async r => {   // pregunta siempre al servidor (ETag → 304 si no cambió)
    if (r.ok && r.type === 'basic') {
      const old = await c.match(key);
      const tag = h => h && (h.headers.get('etag') || h.headers.get('last-modified'));
      if (!old || tag(old) !== tag(r) || !tag(r)) { await c.put(key, r.clone()).catch(() => {}); trim(c, url).catch(() => {}); }
    }
    return r;
  });
  e.waitUntil(net.catch(() => null));                               // la copia se renueva aunque se haya mostrado la guardada
  const timer = new Promise(res => setTimeout(() => res('slow'), SLOW_MS));
  let r;
  try { r = await Promise.race([net, timer]); } catch (err) { r = 'error'; }
  if (r !== 'slow' && r !== 'error' && (r.ok || r.type === 'opaqueredirect')) return r;   // redirección (p. ej. /proyecto → /proyecto/): el navegador la sigue               // lo normal: la versión fresca de la red
  const hit = await cached;
  if (hit) return hit;                                               // red lenta, sin conexión o error 4xx/5xx → la copia
  if (r === 'slow') { try { return await net; } catch (err) { return Response.error(); } }
  if (r === 'error') return Response.error();
  return r;                                                          // error del servidor y sin copia: tal cual
}
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  if (isFresh(url, e.request)) { e.respondWith(networkFirst(e, e.request, url)); return; }
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request)));
});
