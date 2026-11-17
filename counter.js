/* Lista Kauffmann — contador de visitas (DESACTIVADO).
   Solo suma visitas. Sin cookies, sin localStorage, sin script de terceros, sin huella.
   Para activarlo hace falta una cuenta gratuita en https://www.goatcounter.com (la crea Carlos)
   y poner aquí enabled:true y su dirección, p. ej. 'https://CODIGO.goatcounter.com/count'.
   Qué se envía: solo la sección visitada ('/', '/2d/' o '/proyecto/'). Nunca el nombre buscado
   (?q=), la ficha abierta (#s= / #p=), el título ni la página de procedencia (no-referrer).
   GoatCounter recibe, como cualquier servidor, la IP y el navegador; según su política
   (https://www.goatcounter.com/help/privacy) no los guarda y solo guarda totales.
   Si el navegador pide «no rastrear» (DNT o GPC), no se cuenta. */
(function (root) {
  'use strict';
  var KL_COUNTER = { enabled: false, endpoint: '' };

  var ENDPOINT_RE = /^https:\/\/[a-z0-9][a-z0-9-]{1,40}\.goatcounter\.com\/count$/;
  function section(pathname) {
    var p = String(pathname || '/');
    if (/\/2d(\/|\/index\.html)?$/.test(p)) return '/2d/';
    if (/\/proyecto(\/|\/[^/]*\.html)?$/.test(p)) return '/proyecto/';
    return '/';
  }
  // Devuelve la URL del píxel o '' si no se debe contar. Pura, para poder probarla en node.
  function countUrl(cfg, loc, nav, rnd) {
    if (!cfg || cfg.enabled !== true) return '';
    if (!ENDPOINT_RE.test(String(cfg.endpoint || ''))) return '';
    if (!loc || loc.protocol !== 'https:') return '';               // nunca en local ni en file:
    if (/^(localhost|127\.|0\.0\.0\.0|\[::1\])/.test(loc.hostname || '')) return '';
    nav = nav || {};
    if (nav.doNotTrack === '1' || nav.globalPrivacyControl === true) return '';
    if (nav.webdriver === true) return '';                            // navegadores automáticos
    return cfg.endpoint + '?p=' + encodeURIComponent(section(loc.pathname)) + '&r=&t=&rnd=' + encodeURIComponent(String(rnd || ''));
  }
  function isOn() { return !!countUrl(KL_COUNTER, { protocol: 'https:', hostname: 'x', pathname: '/' }, {}, 1); }

  var api = { config: KL_COUNTER, countUrl: countUrl, section: section, isOn: isOn };
  root.KLCounter = api;
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; return; }
  if (typeof document === 'undefined' || typeof location === 'undefined') return;
  var url = countUrl(KL_COUNTER, location, navigator, Math.random().toString(36).slice(2, 8));
  if (!url) return;
  var img = new Image(1, 1);
  img.referrerPolicy = 'no-referrer';
  img.alt = '';
  img.src = url;
})(typeof window !== 'undefined' ? window : globalThis);
