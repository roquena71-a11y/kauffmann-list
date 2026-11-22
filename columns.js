/* Kauffmann List — columnas doradas con la forma de la placa (3 variantes), subida una a una y botones de giro.
   Se carga después de app3d.js. Usa DATA, map, COL_HALF, M_LAT de app3d.js.
   Modelo activo: ?modelo=1|2|3 o el selector (visible con ?modelos=1). Por defecto: 1. */
(function(){
  // Forma de la placa original: cuadrado con esquinas redondeadas, arriba plano, sin remate.
  // half = media anchura (m); rad = radio de las esquinas como fracción de half; top = altura (m).
  const MODELS = {
    1: { name:'Esquinas suaves',   parts:[{half:0.60, rad:0.18, base:0, top:16, color:'GOLD', op:0.96}] },
    2: { name:'Esquinas redondas', parts:[{half:0.60, rad:0.38, base:0, top:16, color:'GOLD', op:0.96}] },
    3: { name:'Esbelta',           parts:[{half:0.48, rad:0.30, base:0, top:18, color:'GOLD', op:0.96}] },
  };
  const q = new URLSearchParams(location.search);
  let current = +(q.get('modelo') || 1);   // modelo elegido: 1 · Esquinas suaves (los otros solo con ?modelo= o ?modelos=1)
  if (!MODELS[current]) current = 1;
  let layerIds = [], sourceIds = [], firstSym = null, pendingAdd = false;
  let T = 1, animating = false;

  function poly(lo, la, halfM, rad, ang){
    // cuadrado de media anchura halfM con esquinas redondeadas (radio rad*halfM), 8 segmentos por esquina
    const r = rad * halfM, c = halfM - r, mLa = 1 / M_LAT, mLo = 1 / (M_LAT * Math.cos(la * Math.PI / 180)), ring = [];
    const cA = Math.cos(ang||0), sA = Math.sin(ang||0);
    const corners = [[c, c, 0], [-c, c, 1], [-c, -c, 2], [c, -c, 3]];
    for (const [cx, cy, q] of corners)
      for (let k = 0; k <= 8; k++){
        const a = (q + k / 8) * Math.PI / 2;
        const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r;
        ring.push([lo + (x*cA - y*sA) * mLo, la + (x*sA + y*cA) * mLa]);
      }
    ring.push(ring[0]);
    return [ring];
  }
  const fcCache = {};
  function fcFor(half, sides){
    const k = half + ':' + sides; if (fcCache[k]) return fcCache[k];
    const rows = (typeof VISIBLE !== 'undefined' && VISIBLE.length) ? VISIBLE : DATA;
    return fcCache[k] = {type:'FeatureCollection', features: rows.map((s, i) => ({type:'Feature',
      properties:{id:s.id, r: ((i * 2654435761) >>> 0) % 1000 / 1000},          // retraso fijo por columna (0–1)
      geometry:{type:'Polygon', coordinates:poly(s._dlo, s._dla, half, sides, s._ang)}}))};
  }
  // altura animada: cada columna sube con su propio retraso
  const grow = (v, ring) => ['*', v, ['max', 0, ['min', 1, ['*', ['-', T, ['*', ['get','r'], 0.7]], ring ? 3.3 : 3.3]]]];

  function remove(){
    for (const id of layerIds) if (map.getLayer(id)) map.removeLayer(id);
    for (const id of sourceIds) if (map.getSource(id)) map.removeSource(id);
    layerIds = []; sourceIds = [];
  }
  function add(firstSymbol, force){
    if (firstSymbol !== undefined) firstSym = firstSymbol;
    if (!map || !VISIBLE || !VISIBLE.length) return;
    if (!force && map.getZoom() < 12.5 && !q.has('modelos') && !selected){
      remove();
      pendingAdd = true;
      return;
    }
    pendingAdd = false;
    remove();
    const M = MODELS[current], before = map.getLayer('sel-glow') ? 'sel-glow' : undefined;
    M.parts.forEach((p, i) => {
      const sid = 'col-' + p.half + '-' + p.rad;
      if (!map.getSource(sid)){ map.addSource(sid, {type:'geojson', data:fcFor(p.half, p.rad), maxzoom:16, buffer:16, tolerance:0}); sourceIds.push(sid); }
      const id = i === 0 ? 'stones' : 'stones-' + i;          // la capa 'stones' recibe los clics
      map.addLayer({id, type:'fill-extrusion', source:sid, minzoom:14.6, paint:{
        'fill-extrusion-color': p.color === 'GOLD' ? GOLD : p.color,
        'fill-extrusion-base': grow(p.base), 'fill-extrusion-height': grow(p.top, p.ring),
        'fill-extrusion-opacity': p.op, 'fill-extrusion-vertical-gradient': true}}, before);
      layerIds.push(id);
    });
    filterSel();
  }
  function setT(t){
    T = t;
    MODELS[current].parts.forEach((p, i) => { const id = i === 0 ? 'stones' : 'stones-' + i;
      if (map.getLayer(id)){ map.setPaintProperty(id, 'fill-extrusion-base', grow(p.base)); map.setPaintProperty(id, 'fill-extrusion-height', grow(p.top, p.ring)); } });
    map.triggerRepaint();                        // asegurar que se dibuje el último paso
  }
  function rise(){
    if (animating || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    animating = true; const t0 = performance.now(), dur = 1800;
    const step = now => { const k = Math.min(1, (now - t0) / dur); setT(k); if (k < 1) requestAnimationFrame(step); else animating = false; };
    setT(0); requestAnimationFrame(step);
  }
  function ensureCols(){
    if (!pendingAdd || !map) return;
    if (map.getZoom() >= 12.5 || selected || q.has('modelos')) add(undefined, true);
  }
  function filterSel(){
    if (pendingAdd && selected && map && map.getZoom() >= 12.5) add(undefined, true);
    const f = selected ? ['!=', ['get','id'], selected] : null;
    for (const id of layerIds) if (map.getLayer(id)) map.setFilter(id, f);
    if (selected && map.getZoom() >= 14.6){
      const s = byId.get(selected); if (s){ tipPinned = true; showTip(s); return; }
    }
    if (!tipHover) { tipPinned = false; hideTip(); }
  }
  function setModel(n){
    if (!MODELS[n]) return; current = n;
    add(undefined, true); rise(); paintPicker();
  }

  // subir cuando se entra a escala de calle
  let wasStreet = false;
  function watchZoom(){ const st = map.getZoom() >= 14.6; if (st && !wasStreet) rise(); wasStreet = st; }

  // ---------- selector de modelos (prueba) ----------
  function paintPicker(){ document.querySelectorAll('#modelPick button').forEach(b => b.setAttribute('aria-pressed', +b.dataset.m === current)); }
  function picker(){
    if (!q.has('modelos') || document.getElementById('modelPick')) return;
    const d = document.createElement('div'); d.id = 'modelPick';
    d.innerHTML = '<span>Modelo</span>' + Object.entries(MODELS).map(([k, m]) => `<button data-m="${k}">${k} · ${m.name}</button>`).join('');
    d.addEventListener('click', e => { const b = e.target.closest('button'); if (b) setModel(+b.dataset.m); });
    map.getContainer().appendChild(d); paintPicker();   // dentro del mapa
  }

  // ---------- brújula compacta (solo visible cuando el mapa está girado) ----------
  function normBearing(deg){
    let b = ((deg || 0) % 360 + 360) % 360;
    return b > 180 ? b - 360 : b;
  }
  function updateCompass(updateLabel){
    const d = document.getElementById('rotBtns'); if (!d || !map) return;
    const b = normBearing(map.getBearing());
    const rotated = Math.abs(b) >= 1;
    d.hidden = !rotated;
    if (!rotated) return;
    const needle = d.querySelector('.kl-compass-needle');
    if (needle) needle.style.transform = `rotate(${(-b).toFixed(1)}deg)`;
    if (updateLabel !== false) relabel(Math.round(Math.abs(b)));
  }
  function rotateButtons(){
    if (document.getElementById('rotBtns')) return;
    const d = document.createElement('div'); d.id = 'rotBtns'; d.hidden = true;
    d.innerHTML = '<button type="button" id="rotNorth" data-r="0" title="Mirar al norte" aria-label="Mirar al norte">' +
                  '<svg class="kl-compass-svg" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">' +
                  '<g class="kl-compass-needle">' +
                  '<polygon points="12,2.5 15.2,11.5 12,10 8.8,11.5" fill="currentColor"/>' +
                  '<polygon points="12,21.5 15.2,12.5 12,14 8.8,12.5" fill="currentColor" opacity="0.35"/>' +
                  '</g>' +
                  '<text x="12" y="14.5" text-anchor="middle" font-size="6.5" font-weight="700" fill="currentColor" opacity="0.9">N</text>' +
                  '</svg></button>';
    d.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      const dur = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 500;
      map.easeTo({bearing: 0, duration: dur, essential: true});
    });
    map.getContainer().appendChild(d);           // dentro del mapa, también en el móvil
    map.on('rotate', () => updateCompass(false));
    map.on('rotateend', () => updateCompass(true));
    map.on('moveend', () => updateCompass(true));
    relabel();
    updateCompass(true);
  }
  // texto de la brújula en el idioma elegido (ES/DE/EN, definidos en app3d.js)
  function relabel(deg){
    // (aquí «T» es la variable de animación de este archivo, así que se lee la tabla I18N de app3d.js directamente)
    const d = document.getElementById('rotBtns'); if (!d || typeof I18N === 'undefined' || typeof lang === 'undefined') return;
    const b = d.querySelector('button[data-r="0"]'); if (!b) return;
    const tr = I18N[lang] || I18N.es;
    const nDeg = typeof deg === 'number' ? deg : Math.round(Math.abs(window.map ? normBearing(map.getBearing()) : 0));
    const v = (nDeg >= 1 && typeof tr.rotNorthDeg === 'function') ? tr.rotNorthDeg(nDeg) : tr.rotNorth;
    if (typeof v === 'string') { b.title = v; b.setAttribute('aria-label', v); }
  }

  // ---------- nombre al pasar el cursor o al tocar (solo s.n del dato; nunca se inventa) ----------
  let tip = null, tipId = null, tipPinned = false, tipHover = false;
  function tipEl(){
    if (tip) return tip;
    tip = document.createElement('div');
    tip.id = 'stoneTip';
    tip.setAttribute('role','status');
    tip.hidden = true;
    map.getContainer().appendChild(tip);
    return tip;
  }
  function topPx(lo, la, h){
    const p = map.project([lo, la]);
    const mpp = 156543.03392 * Math.cos(la * Math.PI/180) / Math.pow(2, map.getZoom());
    p.y -= (h / mpp) * Math.sin(map.getPitch() * Math.PI/180);
    return p;
  }
  function showTip(s){
    if (!s){ hideTip(); return; }
    const el = tipEl();
    const name = ((s._n||s.n) && String(s._n||s.n).trim()) || '—';
    if (tipId !== s.id){ el.textContent = name; tipId = s.id; }
    const p = topPx(s._dlo, s._dla, COL_H);
    const W = map.getContainer().clientWidth, Hmap = map.getContainer().clientHeight;
    el.hidden = false;
    const tw = el.offsetWidth || 160, th = el.offsetHeight || 28;
    const x = Math.max(6, Math.min(W - tw - 6, p.x - tw/2));
    const y = Math.max(6, Math.min(Hmap - th - 6, p.y - th - 10));
    el.style.left = x + 'px'; el.style.top = y + 'px';
  }
  function hideTip(){
    if (!tip || tipPinned) return;
    tip.hidden = true; tipId = null;
  }
  function bindTip(){
    if (map._klTipBound) return; map._klTipBound = true;
    map.on('mousemove', 'stones', e => {
      const s = byId.get(e.features[0].properties.id); if (!s) return;
      tipHover = true; tipPinned = false; showTip(s);
    });
    map.on('mouseleave', 'stones', () => {
      tipHover = false;
      if (selected && map.getZoom() >= 14.6){ const s = byId.get(selected); if (s){ tipPinned = true; showTip(s); return; } }
      hideTip();
    });
    map.on('click', 'stones', e => {
      const s = byId.get(e.features[0].properties.id);
      if (s){ tipPinned = true; tipHover = false; showTip(s); }
    });
    map.on('move', () => { if (tip && !tip.hidden && tipId){ const s = byId.get(tipId); if (s) showTip(s); } });
    map.on('zoomend', () => { if (tip && !tip.hidden && map.getZoom() < 14.6){ tipPinned = false; tipHover = false; hideTip(); } });
  }

  window.KLCols = { add, filterSel, setModel, rise, MODELS, relabel };
  const boot = () => { if (!window.map || !map.on) return setTimeout(boot, 200);
    map.on('zoom', ensureCols); map.on('moveend', ensureCols);
    map.on('zoomend', watchZoom); rotateButtons(); picker(); bindTip(); };
  boot();
})();
