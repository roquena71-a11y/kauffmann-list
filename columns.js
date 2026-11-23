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
  // Brass plate on the top face (slightly inset, stepped bevel). No names or invented text —
  // only geometric grooves. Plaques use a tighter viewport box and a higher minzoom than the
  // shaft so 75k columns stay cheap at mid-street zoom; grooves only appear up close.
  const BRASS_RIM = '#7a5720';
  const BRASS_FACE = '#d6b25a';
  const BRASS_GROOVE = '#5a3f16';
  const PLACA_MINZOOM = 16.2;
  const GROOVE_MINZOOM = 17.8;
  const PLACA_PARTS = [
    {half:0.51, rad:0.10, base:16.00, top:16.26, color:BRASS_RIM, op:1},
    {half:0.43, rad:0.08, base:16.16, top:16.42, color:BRASS_FACE, op:1},
  ];
  const partsOf = (n) => MODELS[n].parts.concat(PLACA_PARTS);
  let loadedPlaqueBox = null;
  let layerIds = [], sourceIds = [], firstSym = null, pendingAdd = false, loadedBox = null;
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
  function rect(lo, la, halfX, halfY, cx, cy, ang){
    const mLa = 1 / M_LAT, mLo = 1 / (M_LAT * Math.cos(la * Math.PI / 180));
    const cA = Math.cos(ang||0), sA = Math.sin(ang||0);
    const pts = [[-halfX,-halfY],[halfX,-halfY],[halfX,halfY],[-halfX,halfY],[-halfX,-halfY]];
    return pts.map(([x,y]) => {
      const X = cx + x, Y = cy + y;
      return [lo + (X*cA - Y*sA) * mLo, la + (X*sA + Y*cA) * mLa];
    });
  }
  // Plaques are only readable up close: pad ~300–400 m around the real viewport, not the
  // multi-kilometre preload box used for shafts.
  function plaqueBox(){
    if (!map) return null;
    try {
      const b = map.getBounds();
      const padLa = 0.003, padLo = 0.004;
      return { w: b.getWest() - padLo, s: b.getSouth() - padLa, e: b.getEast() + padLo, n: b.getNorth() + padLa, full: true };
    } catch (_) {
      const c = map.getCenter();
      return { w: c.lng - 0.006, s: c.lat - 0.005, e: c.lng + 0.006, n: c.lat + 0.005, full: true };
    }
  }
  // Índice espacial ligero sobre VISIBLE para construir solo los polígonos cercanos a la vista (evita congelar el primer zoom a calle).
  const CELL = 0.05, KEY_STRIDE = 100000;
  let indexedRows = null, grid = new Map(), indexById = new Map(), featCache = {};
  const cellKey = (ia, io) => (ia + 50000) * KEY_STRIDE + (io + 50000);
  function ensureIndex(rows){
    if (indexedRows === rows) return;
    indexedRows = rows;
    grid = new Map();
    indexById = new Map();
    featCache = {};
    for (let i = 0; i < rows.length; i++){
      const s = rows[i];
      indexById.set(s.id, i);
      const k = cellKey(Math.floor(s._dla / CELL), Math.floor(s._dlo / CELL));
      let b = grid.get(k); if (!b){ b = []; grid.set(k, b); }
      b.push(i);
    }
  }
  function targetBox(){
    if (!map) return null;
    const z = map.getZoom();
    if (z < 12.5) return null;
    const PAD_LA = 0.025, PAD_LO = 0.035;
    let w, s, e, n;
    try {
      const b = map.getBounds();
      w = b.getWest() - PAD_LO; s = b.getSouth() - PAD_LA;
      e = b.getEast() + PAD_LO; n = b.getNorth() + PAD_LA;
    } catch (_) {
      const c = map.getCenter();
      w = c.lng - 0.05; s = c.lat - 0.04; e = c.lng + 0.05; n = c.lat + 0.04;
    }
    const full = z >= 14.0;
    if (!full){
      const c = map.getCenter();
      w = Math.max(w, c.lng - 0.20); e = Math.min(e, c.lng + 0.20);
      s = Math.max(s, c.lat - 0.14); n = Math.min(n, c.lat + 0.14);
    }
    return { w, s, e, n, full };
  }
  function boxContains(outer, b){
    return !!outer && b.getWest() >= outer.w && b.getEast() <= outer.e && b.getSouth() >= outer.s && b.getNorth() <= outer.n;
  }
  function fcFor(half, sides, box){
    const rows = (typeof VISIBLE !== 'undefined' && VISIBLE.length) ? VISIBLE : DATA;
    ensureIndex(rows);
    const k = half + ':' + sides;
    const fc = featCache[k] || (featCache[k] = new Array(rows.length));
    const getFeat = i => {
      let f = fc[i];
      if (!f){
        const s = rows[i];
        f = fc[i] = {type:'Feature',
          properties:{id:s.id, r: ((i * 2654435761) >>> 0) % 1000 / 1000},      // retraso fijo por columna (0–1)
          geometry:{type:'Polygon', coordinates:poly(s._dlo, s._dla, half, sides, s._ang)}};
      }
      return f;
    };
    const feats = [];
    let hasSel = false;
    const selId = (typeof selected !== 'undefined' && selected) ? selected : null;
    if (box){
      const ia0 = Math.floor(box.s / CELL), ia1 = Math.floor(box.n / CELL);
      const io0 = Math.floor(box.w / CELL), io1 = Math.floor(box.e / CELL);
      for (let ia = ia0; ia <= ia1; ia++){
        for (let io = io0; io <= io1; io++){
          const bucket = grid.get(cellKey(ia, io));
          if (!bucket) continue;
          for (let j = 0; j < bucket.length; j++){
            const idx = bucket[j], s = rows[idx];
            if (s._dla >= box.s && s._dla <= box.n && s._dlo >= box.w && s._dlo <= box.e){
              feats.push(getFeat(idx));
              if (selId && s.id === selId) hasSel = true;
            }
          }
        }
      }
    }
    if (selId && !hasSel){
      const si = indexById.get(selId);
      if (si !== undefined) feats.push(getFeat(si));
    }
    return {type:'FeatureCollection', features: feats};
  }
  // Blank engraved-line look: four short grooves as ONE MultiPolygon per stone (not 4 features).
  const GROOVE_LINES = [
    {cx:0, cy: 0.22, hx:0.22, hy:0.016},
    {cx:0, cy: 0.08, hx:0.30, hy:0.016},
    {cx:0, cy:-0.05, hx:0.30, hy:0.016},
    {cx:0, cy:-0.18, hx:0.30, hy:0.016},
  ];
  function fcGrooves(box){
    const rows = (typeof VISIBLE !== 'undefined' && VISIBLE.length) ? VISIBLE : DATA;
    ensureIndex(rows);
    const feats = [];
    const selId = (typeof selected !== 'undefined' && selected) ? selected : null;
    const consider = [];
    if (box){
      const ia0 = Math.floor(box.s / CELL), ia1 = Math.floor(box.n / CELL);
      const io0 = Math.floor(box.w / CELL), io1 = Math.floor(box.e / CELL);
      for (let ia = ia0; ia <= ia1; ia++){
        for (let io = io0; io <= io1; io++){
          const bucket = grid.get(cellKey(ia, io));
          if (!bucket) continue;
          for (let j = 0; j < bucket.length; j++){
            const idx = bucket[j], s = rows[idx];
            if (s._dla >= box.s && s._dla <= box.n && s._dlo >= box.w && s._dlo <= box.e) consider.push(idx);
          }
        }
      }
    }
    if (selId){
      const si = indexById.get(selId);
      if (si !== undefined && !consider.includes(si)) consider.push(si);
    }
    for (const idx of consider){
      const s = rows[idx];
      const r = ((idx * 2654435761) >>> 0) % 1000 / 1000;
      const polys = GROOVE_LINES.map(L => [rect(s._dlo, s._dla, L.hx, L.hy, L.cx, L.cy, s._ang)]);
      feats.push({type:'Feature', properties:{id:s.id, r},
        geometry:{type:'MultiPolygon', coordinates:polys}});
    }
    return {type:'FeatureCollection', features: feats};
  }
  // altura animada: cada columna sube con su propio retraso
  const grow = (v, ring) => ['*', v, ['max', 0, ['min', 1, ['*', ['-', T, ['*', ['get','r'], 0.7]], ring ? 3.3 : 3.3]]]];

  function remove(){
    for (const id of layerIds) if (map.getLayer(id)) map.removeLayer(id);
    for (const id of sourceIds) if (map.getSource(id)) map.removeSource(id);
    layerIds = []; sourceIds = []; loadedBox = null; loadedPlaqueBox = null;
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
    const tb = targetBox();
    loadedBox = tb;
    const pb = plaqueBox();
    loadedPlaqueBox = pb;
    const parts = partsOf(current), before = map.getLayer('sel-glow') ? 'sel-glow' : undefined;
    parts.forEach((p, i) => {
      const sid = 'col-' + p.half + '-' + p.rad;
      const isPlaca = i > 0;
      const box = isPlaca ? pb : tb;
      if (!map.getSource(sid)){ map.addSource(sid, {type:'geojson', data:fcFor(p.half, p.rad, box), maxzoom:16, buffer:16, tolerance:0}); sourceIds.push(sid); }
      const id = i === 0 ? 'stones' : 'stones-' + i;          // la capa 'stones' recibe los clics
      map.addLayer({id, type:'fill-extrusion', source:sid, minzoom: isPlaca ? PLACA_MINZOOM : 14.6, paint:{
        'fill-extrusion-color': p.color === 'GOLD' ? GOLD : p.color,
        'fill-extrusion-base': grow(p.base), 'fill-extrusion-height': grow(p.top, p.ring),
        'fill-extrusion-opacity': p.op, 'fill-extrusion-vertical-gradient': true}}, before);
      layerIds.push(id);
    });
    const gsid = 'col-placa-grooves';
    if (!map.getSource(gsid)){ map.addSource(gsid, {type:'geojson', data:fcGrooves(pb), maxzoom:16, buffer:16, tolerance:0}); sourceIds.push(gsid); }
    map.addLayer({id:'stones-grooves', type:'fill-extrusion', source:gsid, minzoom:GROOVE_MINZOOM, paint:{
      'fill-extrusion-color': BRASS_GROOVE,
      'fill-extrusion-base': grow(16.30), 'fill-extrusion-height': grow(16.345),
      'fill-extrusion-opacity': 1, 'fill-extrusion-vertical-gradient': false}}, before);
    layerIds.push('stones-grooves');
    filterSel();
  }
  function setT(t){
    T = t;
    partsOf(current).forEach((p, i) => { const id = i === 0 ? 'stones' : 'stones-' + i;
      if (map.getLayer(id)){ map.setPaintProperty(id, 'fill-extrusion-base', grow(p.base)); map.setPaintProperty(id, 'fill-extrusion-height', grow(p.top, p.ring)); } });
    if (map.getLayer('stones-grooves')){
      map.setPaintProperty('stones-grooves', 'fill-extrusion-base', grow(16.30));
      map.setPaintProperty('stones-grooves', 'fill-extrusion-height', grow(16.345));
    }
    map.triggerRepaint();                        // asegurar que se dibuje el último paso
  }
  function rise(){
    if (animating || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    animating = true; const t0 = performance.now(), dur = 1800;
    const step = now => { const k = Math.min(1, (now - t0) / dur); setT(k); if (k < 1) requestAnimationFrame(step); else animating = false; };
    setT(0); requestAnimationFrame(step);
  }
  function ensureCols(){
    if (!map || typeof VISIBLE === 'undefined' || !VISIBLE.length) return;
    const z = map.getZoom();
    if (pendingAdd){
      if (z >= 12.5 || selected || q.has('modelos')) add(undefined, true);
      return;
    }
    if (!sourceIds.length || z < 12.5) return;
    let b;
    try { b = map.getBounds(); } catch (_) { return; }
    const shaftsOk = loadedBox && (loadedBox.full || z < 14.0) && boxContains(loadedBox, b);
    const plaquesOk = z < PLACA_MINZOOM - 0.4 || (loadedPlaqueBox && boxContains(loadedPlaqueBox, b));
    if (shaftsOk && plaquesOk) return;
    if (shaftsOk){
      // Shafts still cover the view: only refresh the tighter plaque/groove sources.
      const pb = plaqueBox();
      loadedPlaqueBox = pb;
      PLACA_PARTS.forEach(p => {
        const src = map.getSource('col-' + p.half + '-' + p.rad);
        if (src) src.setData(fcFor(p.half, p.rad, pb));
      });
      const gro = map.getSource('col-placa-grooves');
      if (gro && z >= GROOVE_MINZOOM - 0.4) gro.setData(fcGrooves(pb));
      return;
    }
    const tb = targetBox();
    loadedBox = tb;
    const needPlaque = z >= PLACA_MINZOOM - 0.4;
    const pb = needPlaque ? plaqueBox() : null;
    loadedPlaqueBox = pb;
    partsOf(current).forEach((p, i) => {
      const src = map.getSource('col-' + p.half + '-' + p.rad);
      if (!src) return;
      const isPlaca = i > 0;
      if (isPlaca && !needPlaque) return;
      src.setData(fcFor(p.half, p.rad, isPlaca ? pb : tb));
    });
    const gro = map.getSource('col-placa-grooves');
    if (gro && z >= GROOVE_MINZOOM - 0.4) gro.setData(fcGrooves(pb || plaqueBox()));
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

  window.KLCols = { add, filterSel, setModel, rise, finish(){ animating=false; setT(1); }, MODELS, relabel, PLACA_MINZOOM, GROOVE_MINZOOM, BRASS_RIM, BRASS_FACE, BRASS_GROOVE };
  const boot = () => { if (!window.map || !map.on) return setTimeout(boot, 200);
    map.on('zoom', ensureCols); map.on('moveend', ensureCols);
    map.on('zoomend', watchZoom); rotateButtons(); picker(); bindTip(); };
  boot();
})();
