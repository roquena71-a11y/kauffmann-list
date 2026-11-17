/* Lista Kauffmann — contador de visitas PROPIO (ACTIVADO).
   Solo suma visitas. Sin cookies, sin localStorage, sin script de terceros, sin huella.
   El servidor es código nuestro (carpeta counter-proto/worker) en la cuenta de Cloudflare de Carlos:
   guarda solo día, sección y un número. No guarda IP, navegador ni procedencia.
   Para activarlo: enabled:true y la dirección del contador, p. ej.
   'https://kl-contador.SUBDOMINIO.workers.dev/hit'.
   Qué se envía: solo la sección visitada ('/', '/2d/' o '/proyecto/'). Nunca el nombre buscado
   (?q=), la ficha abierta (#s= / #p=) ni el título. No se cuenta el paso de una sección a otra
   dentro de la página (se cuenta la entrada). Si el navegador pide «no rastrear» (DNT o GPC), no se cuenta. */
(function (root) {
  'use strict';
  var KL_COUNTER = { enabled: true, endpoint: 'https://kl-contador.roquena71.workers.dev/hit' };

  var ENDPOINT_RE = /^https:\/\/kl-contador\.[a-z0-9][a-z0-9-]{0,62}\.workers\.dev\/hit$/;
  function section(pathname) {
    var p = String(pathname || '/');
    if (/\/2d(\/|\/index\.html)?$/.test(p)) return '/2d/';
    if (/\/proyecto(\/|\/[^/]*\.html)?$/.test(p)) return '/proyecto/';
    return '/';
  }
  // ¿Viene de otra sección de la propia página? Entonces ya se contó al entrar.
  function internal(referrer, loc) {
    try { return !!referrer && new URL(referrer).host === loc.host; } catch (e) { return false; }
  }
  // Devuelve la dirección del contador o '' si no se debe contar. Pura, para probarla en node.
  function countUrl(cfg, loc, nav, referrer) {
    if (!cfg || cfg.enabled !== true) return '';
    if (!ENDPOINT_RE.test(String(cfg.endpoint || ''))) return '';
    if (!loc || loc.protocol !== 'https:') return '';               // nunca en local ni en file:
    if (/^(localhost|127\.|0\.0\.0\.0|\[::1\])/.test(loc.hostname || '')) return '';
    nav = nav || {};
    if (nav.doNotTrack === '1' || nav.globalPrivacyControl === true) return '';
    if (nav.webdriver === true) return '';                            // navegadores automáticos
    if (internal(referrer, loc)) return '';
    return cfg.endpoint;
  }
  function isOn() { return !!countUrl(KL_COUNTER, { protocol: 'https:', hostname: 'x', host: 'x', pathname: '/' }, {}, ''); }
  // Opciones del envío: sin credenciales (ni cookies), sin cuerpo más allá de la sección.
  // referrerPolicy 'origin': el navegador manda solo 'https://roquena71-a11y.github.io/' (con
  // 'no-referrer' mandaría Origin: null y el contador no podría comprobar que viene de la página).
  function request(loc) {
    return { method: 'POST', body: section(loc.pathname), mode: 'no-cors', credentials: 'omit',
             referrerPolicy: 'origin', cache: 'no-store', keepalive: true };
  }

  var api = { config: KL_COUNTER, countUrl: countUrl, section: section, isOn: isOn, request: request };
  root.KLCounter = api;
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; return; }
  if (typeof document === 'undefined' || typeof location === 'undefined' || typeof fetch !== 'function') return;
  function send() {
    var url = countUrl(KL_COUNTER, location, navigator, document.referrer);
    if (!url) return;
    try { fetch(url, request(location)).catch(function () {}); } catch (e) {}
  }
  if (document.prerendering) document.addEventListener('prerenderingchange', send, { once: true });
  else send();
})(typeof window !== 'undefined' ? window : globalThis);
