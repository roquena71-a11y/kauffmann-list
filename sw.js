/* Kauffmann List — service worker: offline app shell + last downloaded stone data.
   Map tiles and orthophoto WMS requests are NOT cached (keep them online; no bulk prefetch). */
const VERSION = 'kauffmann-v6-pages';
const SHELL = ['./','index.html','style.css','style3d.css','app3d.js','imagery.js','manifest.webmanifest',
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
self.addEventListener('install', e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  if (url.pathname.endsWith('/data/stones.json')) {
    e.respondWith(caches.open(VERSION).then(async c => {
      const hit = await c.match(e.request);
      const net = fetch(e.request).then(r => { if (r.ok) c.put(e.request, r.clone()); return r; }).catch(() => hit);
      return hit || net;
    }));
    return;
  }
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).catch(() => caches.match('index.html'))));
});
