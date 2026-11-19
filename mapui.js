/* Lista Kauffmann — interfaz del mapa (v17):
   · placas visibles a cualquier escala: cuadros dorados con el número de placas (agrupadas) que se abren al tocarlos;
   · lista de países (todas las placas, también fuera de Alemania) y vista inicial con todos los países;
   · en el teléfono: mapa a pantalla completa, búsqueda y resultados en una hoja inferior que se arrastra,
     capas en un solo botón y menú compacto. En el escritorio no cambia el diseño (solo países y cuadros).
   Se carga después de app3d.js y people.js. Usa map, VISIBLE, DATA, T, lang, fmtNum, esc, openStone, addOverlays. */
(function () {
  'use strict';
  const TXT = {
    es: {mapLabel:'Mapa 3D', basemapsLabel:'Mapa base', searchPhShort:'Nombre, apellido o calle…',
         ml:{'NavigationControl.ZoomIn':'Acercar','NavigationControl.ZoomOut':'Alejar','NavigationControl.ResetBearing':'Arrastrar para girar el mapa; pulsar para volver al norte',
             'GeolocateControl.FindMyLocation':'Mostrar mi ubicación','GeolocateControl.LocationNotAvailable':'Ubicación no disponible',
             'AttributionControl.ToggleAttribution':'Mostrar u ocultar créditos del mapa','Map.Title':'Mapa'},
         menu:'Menú', layers:'Capas del mapa', countries:'Países', countriesT:'Placas por país',
         sheetOpen:'Mostrar la lista', sheetClose:'Ocultar la lista', sheetFull:'Ampliar la lista',
         cluTip:n=>`${n} placas aquí. Toque para acercar.`},
    de: {mapLabel:'3D-Karte', basemapsLabel:'Grundkarte', searchPhShort:'Vorname, Nachname oder Straße…',
         ml:{'NavigationControl.ZoomIn':'Vergrößern','NavigationControl.ZoomOut':'Verkleinern','NavigationControl.ResetBearing':'Ziehen zum Drehen der Karte; klicken, um nach Norden auszurichten',
             'GeolocateControl.FindMyLocation':'Meinen Standort zeigen','GeolocateControl.LocationNotAvailable':'Standort nicht verfügbar',
             'AttributionControl.ToggleAttribution':'Kartennachweise ein- oder ausblenden','Map.Title':'Karte'},
         menu:'Menü', layers:'Kartenebenen', countries:'Länder', countriesT:'Steine nach Land',
         sheetOpen:'Liste zeigen', sheetClose:'Liste ausblenden', sheetFull:'Liste vergrößern',
         cluTip:n=>`${n} Steine hier. Tippen zum Hineinzoomen.`},
    en: {mapLabel:'3D map', basemapsLabel:'Base map', searchPhShort:'First name, surname or street…',
         ml:{'NavigationControl.ZoomIn':'Zoom in','NavigationControl.ZoomOut':'Zoom out','NavigationControl.ResetBearing':'Drag to rotate the map; click to reset north',
             'GeolocateControl.FindMyLocation':'Show my location','GeolocateControl.LocationNotAvailable':'Location not available',
             'AttributionControl.ToggleAttribution':'Show or hide map credits','Map.Title':'Map'},
         menu:'Menu', layers:'Map layers', countries:'Countries', countriesT:'Stones by country',
         sheetOpen:'Show the list', sheetClose:'Hide the list', sheetFull:'Expand the list',
         cluTip:n=>`${n} stones here. Tap to zoom in.`}
  };
  for (const k of Object.keys(TXT)) if (I18N[k]) Object.assign(I18N[k], TXT[k]);
  const $ = s => document.querySelector(s);
  // Diseño de teléfono: vertical hasta 900 px de ancho (también tableta en vertical) y cualquier pantalla de ≤500 px de alto (teléfono girado).
  const mq = matchMedia('(max-width: 900px), (max-height: 500px)');
  const lq = matchMedia('(max-height: 500px) and (orientation: landscape)');
  const isMobile = () => mq.matches;
  const isLand = () => mq.matches && lq.matches;   // en horizontal la lista va a la izquierda, a toda altura
  const side = $('#side'), handle = $('#sheetHandle'), top = $('.top'), foot = $('.foot'), menuBtn = $('#menuBtn'),
        menu = $('#topMenu'), layersBtn = $('#layersBtn'), layers = $('#basemapsPanel'), root = document.documentElement;
  const DEFAULT_BOUNDS = [[-6.4, 47.2], [15.1, 55.1]];   // Alemania + Irlanda (antes de cargar los datos)

  /* ---------- medidas de la pantalla del teléfono ---------- */
  let sheet = 'peek', peekH = 150;
  function topH(){ return isMobile() && top ? top.getBoundingClientRect().height : 0; }
  function vh(){ return window.innerHeight || document.documentElement.clientHeight; }
  function measurePeek(){
    if (!isMobile()) return;
    const search = side.querySelector('.search'), filters = side.querySelector('.filters');
    const fh = (filters && getComputedStyle(filters).display !== 'none') ? filters.getBoundingClientRect().height + 8 : 0;
    peekH = Math.round(handle.getBoundingClientRect().height + search.getBoundingClientRect().height - fh);
    peekH = Math.max(96, Math.min(peekH, Math.round(vh() * (isLand() ? 0.5 : 0.4))));   // v19: en horizontal la hoja cerrada puede llegar a la mitad para que se vea la fila de países entera
  }
  function heightFor(st){
    const max = vh() - topH() - 6;
    if (st === 'full' || (st === 'half' && isLand())) return max;
    if (st === 'half'){
      let hh = Math.min(max, Math.max(peekH + 120, Math.round(vh() * 0.5)));
      // v19 ronda 4: en pantallas bajas la hoja a media altura no debe tapar los controles de la derecha (zoom, brújula, 3D, ubicación) ni dejar la atribución encima de ellos (24 px + holgura)
      const tr = document.querySelector('.maplibregl-ctrl-top-right');
      if (tr && !isLand()){ const bottom = tr.getBoundingClientRect().bottom; if (bottom > 0) hh = Math.max(peekH + 60, Math.min(hh, Math.round(vh() - bottom - 40))); }
      return hh;
    }
    return peekH;
  }
  function paintVars(h){
    root.style.setProperty('--top-h', topH() + 'px');
    root.style.setProperty('--sheet-h', (isMobile() && !isLand() ? Math.min(h, Math.max(Math.round(vh() * 0.5), heightFor('half'))) : 0) + 'px');   // v19 ronda 4: con la hoja a media altura (ficha abierta) la atribución y los controles suben con la hoja real, también en pantallas bajas (360×640: la hoja mide 353 px > 50 %)
  }
  function setSheet(st, opts){
    if (!isMobile()){ side.removeAttribute('data-sheet'); side.style.height = ''; paintVars(0); return; }
    sheet = st; side.dataset.sheet = st;
    if (st === 'peek') measurePeek();
    const h = heightFor(st);
    side.style.height = h + 'px';
    paintVars(h);
    handle.setAttribute('aria-expanded', st === 'peek' ? 'false' : 'true');
    const lab = T(st === 'peek' ? 'sheetOpen' : st === 'half' ? 'sheetFull' : 'sheetClose');
    handle.setAttribute('aria-label', lab); handle.title = lab;
    if (!(opts && opts.quiet) && window.map) setTimeout(() => map.resize(), 0);
  }
  window.KLUI = {
    // Desplazamiento del vuelo a una placa: en el teléfono, la placa queda en la parte visible del mapa (sobre la hoja).
    offset(){ if (!isMobile()) return [0, 60];
      if (isLand()) return [Math.round(side.getBoundingClientRect().width / 2), Math.round(topH() / 2)]; const sh = Math.max(heightFor('half'), side.getBoundingClientRect().height); return [0, Math.round((topH() - sh) / 2 + 30)]; },
    home(){ return homeCamera(); },
    setSheet, get sheet(){ return sheet; }
  };

  /* ---------- hoja inferior (teléfono) ---------- */
  function cycle(){ if (isLand()) { setSheet(sheet === 'peek' ? 'full' : 'peek'); return; } setSheet(sheet === 'peek' ? 'half' : sheet === 'half' ? 'full' : 'peek'); }
  handle.addEventListener('click', e => { if (dragMoved) { e.preventDefault(); return; } cycle(); });
  handle.addEventListener('keydown', e => {
    if (e.key === 'ArrowUp'){ e.preventDefault(); setSheet(sheet === 'peek' ? 'half' : 'full'); }
    else if (e.key === 'ArrowDown'){ e.preventDefault(); setSheet(sheet === 'full' ? 'half' : 'peek'); }
    else if (e.key === 'Escape' && sheet !== 'peek'){ e.preventDefault(); setSheet('peek'); }
  });
  // Arrastrar la hoja (asa o cabecera de búsqueda, sin contar el campo de texto). También se puede con el botón (WCAG 2.5.7).
  let drag = null, dragMoved = false;
  function onDown(e){
    if (!isMobile() || e.button > 0) return;
    if (e.target.closest('input,select,textarea,a,.countries button')) return;
    drag = {y: e.clientY, h: side.getBoundingClientRect().height, t: performance.now(), id: e.pointerId}; dragMoved = false;
  }
  function onMove(e){
    if (!drag || e.pointerId !== drag.id) return;
    const dy = e.clientY - drag.y;
    if (!dragMoved && Math.abs(dy) < 6) return;
    if (!dragMoved){ dragMoved = true; side.classList.add('dragging'); try { e.target.setPointerCapture(e.pointerId); } catch (_) {} }
    const h = Math.max(peekH * 0.8, Math.min(heightFor('full'), drag.h - dy));
    side.style.height = h + 'px';
    e.preventDefault();
  }
  function onUp(e){
    if (!drag || e.pointerId !== drag.id) return;
    const d = drag; drag = null; side.classList.remove('dragging');
    if (!dragMoved) return;
    const h = side.getBoundingClientRect().height, v = (e.clientY - d.y) / Math.max(1, performance.now() - d.t);
    let st;
    if (v > 0.6) st = sheet === 'full' && h > heightFor('half') * 0.8 ? 'half' : 'peek';
    else if (v < -0.6) st = h > heightFor('half') + 40 ? 'full' : 'half';
    else st = ['peek', 'half', 'full'].map(s => [s, Math.abs(heightFor(s) - h)]).sort((a, b) => a[1] - b[1])[0][0];
    setSheet(st);
    setTimeout(() => { dragMoved = false; }, 0);
  }
  for (const el of [handle, side.querySelector('.search')]){
    el.addEventListener('pointerdown', onDown);
    el.addEventListener('pointermove', onMove);
    el.addEventListener('pointerup', onUp);
    el.addEventListener('pointercancel', onUp);
  }
  // Escribir, ver resultados o abrir una ficha: la hoja sube a la mitad.
  const q = $('#q');
  q.addEventListener('focus', () => { if (isMobile() && sheet === 'peek') setSheet('half'); });
  const grow = () => { if (isMobile() && sheet === 'peek') setSheet('half'); };
  new MutationObserver(() => { const open = !$('#detail').hidden; side.classList.toggle('has-detail', open); if (open) grow(); }).observe($('#detail'), {attributes: true, attributeFilter: ['hidden']});
  new MutationObserver(() => { if ($('#results').children.length && document.activeElement === q) grow(); }).observe($('#results'), {childList: true});

  /* ---------- menú (teléfono) ---------- */
  function setMenu(open, focusBack){
    top.classList.toggle('menu-open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open){ setLayers(false); const f = menu.querySelector('button,a'); if (f) f.focus(); }
    else if (focusBack) menuBtn.focus();
  }
  menuBtn.addEventListener('click', () => setMenu(!top.classList.contains('menu-open')));
  menu.addEventListener('keydown', e => { if (e.key === 'Escape'){ e.preventDefault(); setMenu(false, true); } });
  menu.addEventListener('click', e => { if (isMobile() && e.target.closest('#remember,#replayIntro,#aboutLink')) setMenu(false); });
  function placeFoot(){
    // En el teléfono, los enlaces del pie (datos, proyecto, mapa 2D…) van dentro del menú; en el escritorio, abajo.
    // Dentro del menú el pie no es un «contentinfo» (axe: landmark-contentinfo-is-top-level).
    if (isMobile()){ if (foot.parentNode !== menu) menu.append(foot); foot.setAttribute('role', 'group'); foot.setAttribute('aria-label', T('menu')); }
    else { if (foot.parentNode === menu) document.body.insertBefore(foot, $('#about')); foot.removeAttribute('role'); foot.removeAttribute('aria-label'); }
  }

  /* ---------- capas (teléfono: un solo botón) ---------- */
  function setLayers(open, focusBack){
    layers.classList.toggle('open', open);
    document.body.classList.toggle('layers-open', open);   // mientras está abierto, los botones de giro no quedan debajo
    layersBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open){ setMenu(false); const f = layers.querySelector('button[aria-pressed=true]') || layers.querySelector('button'); if (f) f.focus(); }
    else if (focusBack) layersBtn.focus();
  }
  layersBtn.addEventListener('click', () => setLayers(!layers.classList.contains('open')));
  layers.addEventListener('keydown', e => { if (e.key === 'Escape' && isMobile()){ e.preventDefault(); setLayers(false, true); } });
  layers.addEventListener('click', e => { if (isMobile() && e.target.closest('#sourcesBtn')) setLayers(false); });
  document.addEventListener('pointerdown', e => {
    if (!isMobile()) return;
    if (layers.classList.contains('open') && !e.target.closest('#basemapsPanel,#layersBtn')) setLayers(false);
    if (top.classList.contains('menu-open') && !e.target.closest('.top')) setMenu(false);
  }, true);

  /* ---------- países ---------- */
  let COUNTRIES = [];
  function buildCountries(){
    // Número por país = registros de data/stones.json (la misma cuenta que «N placas en el mapa»); el encuadre, con las columnas visibles.
    const m = new Map(), get = s => { const cc = (s.cc || 'DE').toUpperCase(); let c = m.get(cc); if (!c) m.set(cc, c = {cc, n: 0, w: 180, s: 90, e: -180, nn: -90}); return c; };
    for (const s of DATA) get(s).n++;
    for (const s of VISIBLE){
      const c = get(s);
      if (s.lo < c.w) c.w = s.lo; if (s.lo > c.e) c.e = s.lo; if (s.la < c.s) c.s = s.la; if (s.la > c.nn) c.nn = s.la;
    }
    COUNTRIES = [...m.values()].sort((a, b) => b.n - a.n);
    paintCountries();
  }
  function cname(cc){ const names = T('countryName') || {}; return names[cc] || cc; }
  function paintCountries(){
    const box = $('#countries'); if (!box) return;
    if (COUNTRIES.length < 1){ box.replaceChildren(); return; }
    box.innerHTML = `<span class="countries-t">${esc(T('countries'))}:</span>` + COUNTRIES.map(c =>
      `<button type="button" data-cc="${esc(c.cc)}"><span class="sq" aria-hidden="true"></span>${esc(cname(c.cc))} <span class="n">${fmtNum(c.n)}</span></button>`).join('');
    if (isMobile() && sheet === 'peek') setSheet('peek');   // v19: la fila de países ahora se parte en líneas: volver a medir la hoja cerrada
  }
  // v19: degradado de «hay más países» (solo en horizontal, ver mapui.css): se quita cuando la fila llega al final
  (function(){ const box = $('#countries'); if (!box) return;
    const upd = () => box.classList.toggle('at-end', box.scrollLeft + box.clientWidth >= box.scrollWidth - 4);
    box.addEventListener('scroll', upd, {passive:true}); window.addEventListener('resize', upd); new MutationObserver(upd).observe(box, {childList:true}); upd(); })();
  $('#countries').addEventListener('click', e => {
    const b = e.target.closest('button[data-cc]'); if (!b || !window.map) return;
    const c = COUNTRIES.find(x => x.cc === b.dataset.cc); if (!c) return;
    if (document.body.classList.contains('vigil-on') && typeof stopVigil === 'function') stopVigil();
    if (isMobile()) setSheet('peek');
    // Pocas placas juntas (una calle, Dublín): acercarse e inclinar. Pocas placas pero en ciudades lejanas (Suecia: Malmö y Estocolmo, ~500 km): ver todas, sin inclinar (v18).
    const tiny = c.n < 50 && Math.max(c.e - c.w, c.nn - c.s) < 0.02;   // v19: ≈2 km (una calle: Dublín); Jersey (isla de ~12 km) y Helsinki (~5 km) se ven enteras, sin inclinar
    const ext = Math.max(c.e - c.w, c.nn - c.s), pad = tiny ? 0.002 : (ext < 1 ? 0.01 : 0.15);
    const box = [[c.w - pad, c.s - pad], [c.e + pad, c.nn + pad]], spread = c.n < 50 && !tiny;
    let cam = null;
    try { cam = spread ? fitCamera(box) : map.cameraForBounds(box, {padding: padding()}); } catch (err) {}   // spread: cálculo propio (cameraForBounds falla con el mapa inclinado)
    if (!cam || !isFinite(cam.zoom)) return;
    const z = Math.min(tiny ? 16.6 : 12, cam.zoom);
    map.flyTo({center: cam.center, zoom: z, pitch: tiny ? 58 : (spread ? 0 : map.getPitch()), bearing: spread ? 0 : map.getBearing(), duration: reduceMotion ? 0 : 2400, essential: true});
  });
  document.querySelectorAll('.lang button').forEach(b => b.addEventListener('click', () => { applyI18n(); paintCountries(); setSheet(sheet, {quiet: true}); }));

  /* ---------- vista inicial: todos los países ---------- */
  function padding(){
    if (isLand()) return {top: topH() + 12, bottom: 70, left: Math.round(side.getBoundingClientRect().width) + 72, right: 84};   // v19 ronda 3: libre de la barra de capas (a la derecha de la lista), de los botones de giro, de la atribución y de los controles de la derecha
    if (isMobile()) return {top: topH() + 16, bottom: Math.round(heightFor('peek')) + 104, left: 40, right: 84};   // v19 ronda 4: left 40 (a 320 px el recuadro de Hyam Goldman tocaba el botón de capas, que llega a x=54). v19 ronda 3: encima de la hoja van los botones ⟲ N ⟳ (a 46 px de la hoja, 40 px de alto): el país no debe quedar detrás
    return {top: 20, bottom: 100, left: 20, right: 60};   // escritorio: la barra de capas (Noche · Día · Hoy…) ocupa ~70 px abajo; v18: Malmö quedaba tapada
  }
  function dataBounds(){
    if (!COUNTRIES.length) return DEFAULT_BOUNDS;
    let w = 180, s = 90, e = -180, n = -90;
    for (const c of COUNTRIES){ w = Math.min(w, c.w); s = Math.min(s, c.s); e = Math.max(e, c.e); n = Math.max(n, c.nn); }
    return [[w - 0.2, s - 0.2], [e + 0.2, n + 0.2]];
  }
  // Cámara que muestra todas las placas (cálculo propio en Mercator: cameraForBounds de MapLibre aleja de más con el mapa inclinado).
  function fitCamera(bounds){
    const el = map.getContainer(), p = padding();
    const W = Math.max(50, el.clientWidth - p.left - p.right), H = Math.max(50, el.clientHeight - p.top - p.bottom);
    const mx = lo => (lo + 180) / 360, my = la => { const r = la * Math.PI / 180; return (1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2; };
    const [[w, s], [e, n]] = bounds;
    const dx = Math.max(1e-6, mx(e) - mx(w)), dy = Math.max(1e-6, my(s) - my(n));
    const zoom = Math.log2(Math.min(W / (512 * dx), H / (512 * dy)));
    // centro del rectángulo útil (sin cabecera ni hoja): se desplaza el centro del mapa por la diferencia de márgenes
    const cx = (mx(w) + mx(e)) / 2, cy = (my(n) + my(s)) / 2, scale = 512 * Math.pow(2, zoom);
    const ox = (p.right - p.left) / 2 / scale, oy = (p.bottom - p.top) / 2 / scale;
    const X = cx + ox, Y = cy + oy;
    const lon = X * 360 - 180, lat = Math.atan(Math.sinh(Math.PI * (1 - 2 * Y))) * 180 / Math.PI;
    return {center: [lon, lat], zoom};
  }
  function homeCamera(){
    if (!window.map) return {};
    let cam = null;
    try { cam = fitCamera(dataBounds()); } catch (e) {}
    if (!cam || !isFinite(cam.zoom)) return {};
    return {center: cam.center, zoom: Math.max(1, Math.min(cam.zoom - 0.15, 6)), pitch: isMobile() ? 40 : 50, bearing: -8};
  }
  let userMoved = false;
  const deep = () => /#s=/.test(location.hash) || /[?&](q|vigil)=/.test(location.search);
  const introOpen = () => !root.classList.contains('intro-skip');
  if (window.map){
    map.on('movestart', e => { if (e && e.originalEvent) userMoved = true; });
    if (!deep() && !introOpen()) map.jumpTo(homeCamera());
  }
  document.addEventListener('kl:data', () => {
    buildCountries();
    if (isMobile()) setSheet(sheet, {quiet: true});
    if (!deep() && !introOpen() && !userMoved && window.map && !map.isMoving()) map.easeTo(Object.assign(homeCamera(), {duration: reduceMotion ? 0 : 600}));
  });

  /* ---------- placas a cualquier escala: cuadros dorados agrupados ---------- */
  const CLU_MAX = 14.6;   // desde aquí se ven las columnas una a una (columns.js)
  let CLU_FC = null;
  function badge(size, border, fill){
    const r = 2, px = size * r, c = document.createElement('canvas'); c.width = c.height = px;
    const g = c.getContext('2d');
    g.fillStyle = border; g.fillRect(0, 0, px, px);
    g.fillStyle = fill; const b = Math.round(2.5 * r); g.fillRect(b, b, px - 2 * b, px - 2 * b);
    return {img: g.getImageData(0, 0, px, px), r};
  }
  function addImages(){
    if (!map.hasImage('kl-badge')){ const b = badge(40, '#e0bc62', 'rgba(7,17,31,0.86)'); map.addImage('kl-badge', b.img, {pixelRatio: b.r}); }
    if (!map.hasImage('kl-one')){
      const r = 2, px = 18 * r, c = document.createElement('canvas'); c.width = c.height = px; const g = c.getContext('2d');
      g.fillStyle = '#1a140c'; g.fillRect(0, 0, px, px);
      const gr = g.createLinearGradient(0, 0, px, px); gr.addColorStop(0, '#f0d48a'); gr.addColorStop(.55, '#c6a15b'); gr.addColorStop(1, '#8d6a32');
      g.fillStyle = gr; g.fillRect(3 * r / 2, 3 * r / 2, px - 3 * r, px - 3 * r);
      map.addImage('kl-one', g.getImageData(0, 0, px, px), {pixelRatio: r});
    }
  }
  function addClusters(){
    if (!window.map || !VISIBLE || !VISIBLE.length || map.getSource('kl-clu')) return;
    if (!CLU_FC) CLU_FC = {type: 'FeatureCollection', features: VISIBLE.map(s => ({type: 'Feature', properties: {id: s.id}, geometry: {type: 'Point', coordinates: [s.lo, s.la]}}))};
    addImages();
    map.addSource('kl-clu', {type: 'geojson', data: CLU_FC, cluster: true, clusterRadius: 56, clusterMaxZoom: 13.5, maxzoom: 14});
    const big = ['coalesce', ['get', 'point_count'], 1];
    // A escala de país, los grupos grandes ya se ven como campo de luz y columnas doradas: su cuadro aparece desde el zoom 6.
    // Los grupos pequeños y las placas sueltas (p. ej. Dublín) se ven siempre.
    map.addLayer({id: 'kl-clu', type: 'symbol', source: 'kl-clu', maxzoom: CLU_MAX,
      filter: ['all', ['has', 'point_count'], ['any', ['<', ['get', 'point_count'], 50], ['>=', ['zoom'], 6]]],
      layout: {'icon-image': 'kl-badge', 'icon-allow-overlap': true, 'icon-ignore-placement': true, 'text-allow-overlap': true, 'text-ignore-placement': true,
        'icon-size': ['step', big, 0.7, 10, 0.76, 100, 0.86, 1000, 0.96],
        'text-field': ['get', 'point_count_abbreviated'], 'text-font': ['Noto Sans Regular'],
        'text-size': ['step', big, 12.5, 100, 12, 1000, 11.5], 'symbol-sort-key': ['-', 0, big]},
      paint: {'text-color': '#f0d48a', 'icon-opacity': ['interpolate', ['linear'], ['zoom'], 13.6, 1, CLU_MAX, 0.4], 'text-opacity': ['interpolate', ['linear'], ['zoom'], 13.6, 1, CLU_MAX, 0.4]}});
    map.addLayer({id: 'kl-one', type: 'symbol', source: 'kl-clu', maxzoom: CLU_MAX, filter: ['!', ['has', 'point_count']],
      layout: {'icon-image': 'kl-one', 'icon-allow-overlap': true, 'icon-ignore-placement': true, 'icon-size': ['interpolate', ['linear'], ['zoom'], 6, 0.9, 13, 1.1]}});
  }
  if (typeof addOverlays === 'function'){
    const _add = addOverlays;
    addOverlays = function(){ _add.apply(this, arguments); try { addClusters(); } catch (e) { console.warn('clusters', e); } };
  }
  (function wire(){
    if (!window.map){ setTimeout(wire, 200); return; }
    if (map.isStyleLoaded() && VISIBLE && VISIBLE.length) addClusters();
    map.on('click', 'kl-clu', e => { const f = e.features && e.features[0]; if (f) expand(f); });
    async function expand(f){
      const src = map.getSource('kl-clu');
      let z = 0; try { z = await src.getClusterExpansionZoom(f.properties.cluster_id); } catch (_) { z = map.getZoom() + 2; }
      map.easeTo({center: f.geometry.coordinates, zoom: Math.min(Math.max(z + 0.3, map.getZoom() + 1.2), 16.2), duration: reduceMotion ? 0 : 900, essential: true});
    }
    map.on('click', 'kl-one', e => { const f = e.features && e.features[0]; if (f) openStone(f.properties.id); });
    // Tolerancia de toque: una placa suelta o un grupo a menos de 14 px del dedo también se abre (zona ≥ 28 px; WCAG 2.5.8).
    map.on('click', e => {
      const L = ['kl-one', 'kl-clu'].filter(id => map.getLayer(id)); if (!L.length) return;
      if (map.queryRenderedFeatures(e.point, {layers: L}).length) return;      // ya lo atiende el clic exacto
      const r = 14, fs = map.queryRenderedFeatures([[e.point.x - r, e.point.y - r], [e.point.x + r, e.point.y + r]], {layers: L});
      if (!fs.length) return;
      const d = f => { const p = map.project(f.geometry.coordinates); return Math.hypot(p.x - e.point.x, p.y - e.point.y); };
      const f = fs.sort((a, b) => d(a) - d(b))[0];
      if (f.properties.cluster_id != null) expand(f); else openStone(f.properties.id);
    });
    for (const id of ['kl-clu', 'kl-one']){
      map.on('mouseenter', id, () => { map.getCanvas().style.cursor = 'pointer'; });
      map.on('mouseleave', id, () => { map.getCanvas().style.cursor = ''; });
    }
    // Tocar el mapa vacío en el teléfono baja la hoja y cierra los menús.
    const quiet = new Set(['glow', 'house-lights', 'stone-dots', 'sel-glow', 'bldg3d']);
    map.on('click', e => {
      if (!isMobile()) return;
      let hit = [];
      try { hit = map.queryRenderedFeatures(e.point).filter(f => f.layer && !quiet.has(f.layer.id) && f.layer.source !== 'openmaptiles' && f.layer.source !== 'eox'); } catch (_) {}
      if (!hit.length && sheet !== 'peek' && $('#detail').hidden) setSheet('peek');
    });
    map.on('dragstart', () => { if (isMobile() && sheet === 'full') setSheet('half'); });
  })();

  /* ---------- textos de los controles de MapLibre y del buscador en ES/DE/EN ---------- */
  function relabel(){
    const ml = T('ml') || {};
    if (window.map){
      try { map._locale = Object.assign({}, map._locale || {}, ml); } catch (e) {}   // textos que MapLibre vuelve a poner (p. ej. ubicación)
      const c = map.getContainer(), set = (sel, k) => c.querySelectorAll(sel).forEach(b => { if (ml[k]) { b.setAttribute('aria-label', ml[k]); b.title = ml[k]; } });
      set('.maplibregl-ctrl-zoom-in', 'NavigationControl.ZoomIn'); set('.maplibregl-ctrl-zoom-out', 'NavigationControl.ZoomOut');
      set('.maplibregl-ctrl-compass', 'NavigationControl.ResetBearing'); set('.maplibregl-ctrl-geolocate:not(.maplibregl-ctrl-geolocate-error)', 'GeolocateControl.FindMyLocation');
      set('.maplibregl-ctrl-attrib-button', 'AttributionControl.ToggleAttribution');
      const cv = map.getCanvas(); if (cv && ml['Map.Title']) cv.setAttribute('aria-label', ml['Map.Title']);
    }
    // En pantallas estrechas el texto largo del buscador se cortaba («…calle y ciuda»): versión corta.
    const qi = $('#q'); if (qi && isMobile() && (innerWidth < 480 || isLand())) qi.placeholder = T('searchPhShort');
  }
  document.querySelectorAll('.lang button').forEach(b => b.addEventListener('click', () => setTimeout(relabel, 0)));
  if (window.map) map.once('idle', relabel);

  /* ---------- foco: volver de la ficha y cerrar diálogos (WCAG 2.4.3) ---------- */
  let lastStone = null;
  $('#detail').addEventListener('click', e => {
    if (!e.target.closest('#back')) return;
    const id = lastStone;
    setTimeout(() => {
      const b = id && document.querySelector(`#results button[data-id="${CSS.escape(id)}"]`);
      (b && b.offsetParent ? b : $('#q')).focus();
    }, 0);
  }, true);
  new MutationObserver(() => { if (!$('#detail').hidden && typeof selected !== 'undefined' && selected) lastStone = selected; }).observe($('#detail'), {childList: true});
  let opener = null;
  document.addEventListener('click', e => { const b = e.target.closest('button,a'); if (b && !b.closest('dialog')) opener = b; }, true);
  document.querySelectorAll('dialog').forEach(d => d.addEventListener('close', () => {
    let t = opener;
    if (t && t.closest('#topMenu') && !top.classList.contains('menu-open')) t = isMobile() ? menuBtn : t;
    if (t && t.closest('#basemapsPanel') && !layers.classList.contains('open') && isMobile()) t = layersBtn;
    if (t && t.isConnected && t.getClientRects().length) setTimeout(() => t.focus(), 0);
  }));

  /* ---------- arranque y cambios de tamaño ---------- */
  function layout(){
    placeFoot(); applyI18n(); relabel();
    if (!isMobile()){ setMenu(false); setLayers(false); }
    setSheet(isMobile() ? (side.dataset.sheet || 'peek') : 'peek', {quiet: true});
    if (window.map) map.resize();
  }
  for (const m of [mq, lq]) (m.addEventListener ? m.addEventListener('change', layout) : m.addListener(layout));
  window.addEventListener('resize', () => { if (isMobile() && !drag) setSheet(sheet, {quiet: true}); });
  // Al cerrar la introducción aparecen la cabecera y la hoja: medir de nuevo (si no, --top-h quedaría en 0).
  new MutationObserver(() => { if (!introOpen()) setTimeout(() => setSheet(sheet, {quiet: true}), 60); }).observe(root, {attributes: true, attributeFilter: ['class']});
  applyI18n();
  layout();
  if (VISIBLE && VISIBLE.length) buildCountries();
})();
