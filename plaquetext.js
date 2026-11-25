/* Kauffmann List v31–v32 — la inscripción escrita en la placa de latón de cada columna (solo de cerca).
   Se carga sola (perezosa) la primera vez que el mapa llega a zoom >= 19,5; nunca en la carga inicial.
   Capa custom WebGL '3d': un cuadrado texturizado por placa sobre la cara de latón, con letras oscuras grabadas.
   El texto sale SOLO del campo i de nuestros datos (OSM ODbL / Wikidata CC0 / Firenze / Grevenbroich): nunca se inventa;
   sin inscripción la placa queda en blanco (latón con surcos). Usa map, VISIBLE/DATA, byId, selected y KLCols (columns.js). */
(function(root){
  'use strict';
  const INK = '#3a2a10', FACE = '#d6b25a';           // letras grabadas sobre la cara (contraste WCAG ≈ 6:1)
  // Capa desde z20. Qué se escribe depende del tamaño de la placa EN PANTALLA (no solo del zoom): las placas están a 16,4 m y la
  // cámara de MapLibre baja deprisa (escritorio 1280x800: 33 m a z20,5, 23 m a z21, 16 m a z21,5; teléfono: 43 / 30 / 21 m).
  // Medido: cara de 0,86 m = 51 px a z20,5 y 124 px a z21 en escritorio; 41 / 79 / 219 px a z20,5 / 21 / 21,5 en teléfono.
  // Z_NAME / Z_FULL quedan como referencia del plan (≈ escritorio 20,5 / teléfono 21,5).
  const Z_ON = 20, Z_NAME = 20.5, Z_FULL = 21.5;
  const PX_NAME = 40, PX_FULL = 100;                 // px de la cara (escritorio): nombre desde 40 px, inscripción entera desde 100 px
  const Z_ON_NARROW = 19.5, PX_NAME_NARROW = 26;     // v35 C2: teléfono (≤760 px): nombre desde ~z20,2 a 42° (cara ≈ 31 px)
  const CAM_CLEAR = 0.25;                            // v35 C3: solo se oculta el texto si la cámara está a ≤0,25 m de la cara o debajo
  function isNarrow(){ return typeof window !== 'undefined' && window.matchMedia && matchMedia('(max-width: 760px)').matches; }
  function zOn(){ return isNarrow() ? Z_ON_NARROW : Z_ON; }
  function pxName(){ return isNarrow() ? PX_NAME_NARROW : PX_NAME; }
  const MAX_STONES = 60, MAX_TEX = 72;               // placas en vista dibujadas / texturas en caché (LRU)
  const FACE_HALF_M = 0.43;                         // media cara (columns.js FACE_HALF)
  const LIFT = 0.005;                                // m sobre la cara (16,42 m); los surcos (16,44 m) se ocultan donde hay texto
  const HALF_IN = 0.40;                              // semilado del área de texto (cara: 0,43 m)

  // ---------- texto: funciones puras (también se prueban en node) ----------
  const fold = t => String(t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/ß/g, 'ss');
  function upper(t){ return String(t).toLocaleUpperCase('de-DE'); }
  // Las mismas líneas que la ficha: «|» y saltos de línea son cortes; nada más se cambia.
  const DD = (typeof module !== 'undefined' && module.exports && typeof require === 'function') ? require('./dedupe.js') : root.KLDedupe;
  const show = t => (DD && DD.inscDisplay ? DD.inscDisplay(t) : String(t)).trim();
  function hardLines(i){ return String(i || '').replace(/\s*\|\s*/g, '\n').split(/\n/).map(x => x.trim()).filter(Boolean); }
  // Texto de la placa: el campo i propio o, en registros fusionados, el primero que lo tenga (misma persona, nuestros datos).
  function inscOf(s){
    if (!s) return null;
    // v32: texto PARA MOSTRAR (sin <br />, '''…''', [[…|…]], &#…; — KLDedupe.inscDisplay, el mismo que la ficha)
    if (s.i && String(s.i).trim()){ const t = show(s.i); if (t) return t; }
    for (const r of (s._also || [])) if (r && r.i && String(r.i).trim()){ const t = show(r.i); if (t) return t; }
    return null;
  }
  // Modo nombre: el trozo de la inscripción (cortes «|», salto o coma) que contiene el nombre de la persona; si no está, nada.
  function nameLine(s){
    // El nombre tal como está escrito en i: del primer al último término del nombre (campo n) dentro del trozo de i
    // (separado por «|», salto o coma) que más términos contiene. Siempre un trozo LITERAL de i; si no se encuentra, null.
    const i = inscOf(s); if (!i) return null;
    const toks = new Set(fold(s.n || '').split(/[^a-z0-9]+/).filter(t => t.length >= 2));
    if (!toks.size) return null;
    const need = Math.min(2, toks.size);
    let best = null;
    for (const seg of String(i).split(/\s*[|\n,]\s*/)){
      const words = [...seg.matchAll(/[\p{L}\p{N}\p{M}'’-]+/gu)];
      const hit = w => fold(w[0]).split(/[^a-z0-9]+/).filter(t => toks.has(t));
      for (let a = 0; a < words.length; a++){
        if (!hit(words[a]).length) continue;
        let e = a; const got = new Set(hit(words[a]));
        for (let j = a + 1; j < words.length && j - e <= 2; j++){ const h = hit(words[j]); if (h.length){ e = j; h.forEach(t => got.add(t)); } }
        if (got.size >= need && (!best || got.size > best.n)) best = {n: got.size, text: seg.slice(words[a].index, words[e].index + words[e][0].length)};
        a = e;
      }
    }
    return best ? best.text : null;
  }

  function linesFor(s, mode){
    if (mode === 'name'){ const l = nameLine(s); return l ? [upper(l)] : null; }
    const i = inscOf(s); if (!i) return null;
    return hardLines(i).map(upper);
  }
  // Ajuste de palabras a un ancho (measure = función de ancho), igual que el texto de la ficha al pasar de línea.
  function wrap(lines, width, measure){
    const out = [];
    for (const line of lines){
      let cur = '';
      for (const w of line.split(/\s+/).filter(Boolean)){
        const t = cur ? cur + ' ' + w : w;
        if (!cur || measure(t) <= width) cur = t; else { out.push(cur); cur = w; }
      }
      if (cur) out.push(cur);
    }
    return out;
  }
  // Mayor tamaño de letra con el que todo cabe en el cuadrado (ninguna palabra se corta ni se sale).
  function fit(lines, box, measureAt, maxPx, minPx){
    for (let px = maxPx; px >= minPx; px -= 1){
      const m = t => measureAt(t, px);
      const w = wrap(lines, box, m);
      if (w.length * px * 1.2 <= box && w.every(l => m(l) <= box)) return {px, lines: w};
    }
    const m = t => measureAt(t, minPx);
    return {px: minPx, lines: wrap(lines, box, m), overflow: true};
  }
  // Modo según el tamaño de la cara en pantalla (px) y la altura de la cámara sobre la placa (m)
  function modeFor(z, facePx, camAboveFace, opts){
    const z0 = (opts && opts.zOn != null) ? opts.zOn : ((typeof window !== 'undefined') ? zOn() : Z_ON);
    const pn = (opts && opts.pxName != null) ? opts.pxName : ((typeof window !== 'undefined') ? pxName() : PX_NAME);
    const cc = (opts && opts.camClear != null) ? opts.camClear : CAM_CLEAR;
    if (z < z0) return [null, 'zoom'];
    if (!(camAboveFace > cc)) return [null, 'camara'];
    if (facePx >= PX_FULL) return ['full', ''];
    if (facePx >= pn) return ['name', ''];
    return [null, 'pequena'];
  }
  // Contraste WCAG 2.x
  function lum(hex){ const c = [1, 3, 5].map(k => parseInt(hex.slice(k, k + 2), 16) / 255).map(v => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; }
  function contrast(a, b){ const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  const API = {INK, FACE, Z_ON, Z_NAME, Z_FULL, PX_NAME, PX_FULL, Z_ON_NARROW, PX_NAME_NARROW, CAM_CLEAR, isNarrow, zOn, pxName, modeFor, fold, hardLines, inscOf, nameLine, linesFor, wrap, fit, contrast};
  if (typeof module !== 'undefined' && module.exports){ module.exports = API; return; }

  // ---------- navegador ----------
  const FONT = px => `700 ${px}px "Helvetica Neue", Arial, "Liberation Sans", sans-serif`;
  const mctx = document.createElement('canvas').getContext('2d');
  const measureAt = (t, px) => { mctx.font = FONT(px); return mctx.measureText(t).width; };
  // Cámara: distancia al centro (m) = cameraToCenterDistance / px por metro; altura = distancia · cos(inclinación)
  function camera(faceTop){
    const t = map.transform, c = map.getCenter(), lat = c.lat * Math.PI / 180;
    const ppm = t.worldSize / (2 * Math.PI * 6378137 * Math.cos(lat));
    const D = t.cameraToCenterDistance / ppm, cp = Math.cos(map.getPitch() * Math.PI / 180), alt = D * cp;
    // tamaño de una placa cuya cara cae en el centro de la pantalla (a lo largo del rayo central: D − altura / cos(inclinación))
    const near = D - faceTop / Math.max(cp, 0.2);
    const facePx = alt > faceTop ? ppm * 2 * FACE_HALF_M * D / Math.max(near, 0.5) : 0;
    return {alt, above: alt - faceTop, facePx};
  }
  const st = {ids: [], drawn: 0, mode: null, textures: 0, skipped: '', quads: []};

  function paint(s, mode){
    const lines = linesFor(s, mode); if (!lines) return null;
    const N = mode === 'full' ? 512 : 256, pad = Math.round(N * 0.035), box = N - 2 * pad;
    const f = fit(lines, box, measureAt, mode === 'full' ? 64 : 72, mode === 'full' ? 6 : 10);
    if (f.overflow) return null;   // no cabe ni a la letra mínima: la placa queda lisa (nunca se corta el texto a medias)
    const cv = document.createElement('canvas'); cv.width = cv.height = N;
    const g = cv.getContext('2d');
    g.clearRect(0, 0, N, N);
    g.font = FONT(f.px); g.textAlign = 'center'; g.textBaseline = 'middle';
    const lh = f.px * 1.2, y0 = N / 2 - (f.lines.length - 1) * lh / 2;
    f.lines.forEach((l, k) => {
      // grabado: un filo claro debajo y la letra oscura encima
      g.fillStyle = 'rgba(255,236,170,0.55)'; g.fillText(l, N / 2, y0 + k * lh + Math.max(1, f.px * 0.06));
      g.fillStyle = INK; g.fillText(l, N / 2, y0 + k * lh);
    });
    return {canvas: cv, lines: f.lines, px: f.px, overflow: !!f.overflow};
  }

  // ---------- caché de texturas (LRU) ----------
  const cache = new Map();   // key → {tex, info}
  function texFor(gl, s, mode){
    const key = s.id + '|' + mode;
    let e = cache.get(key);
    if (e){ cache.delete(key); cache.set(key, e); return e; }
    const info = paint(s, mode);
    e = {tex: null, info};
    if (info){
      const tex = gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, info.canvas);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      e.tex = tex; info.canvas = null;
    }
    cache.set(key, e);
    while (cache.size > MAX_TEX){ const [k, old] = cache.entries().next().value; if (old.tex) gl.deleteTexture(old.tex); cache.delete(k); }
    st.textures = cache.size;
    return e;
  }

  // ---------- placas en vista ----------
  let inView = [];
  function refresh(){
    const z = map.getZoom();
    if (z < zOn()){ inView = []; return; }
    const rows = (typeof VISIBLE !== 'undefined' && VISIBLE.length) ? VISIBLE : DATA;
    const b = map.getBounds(), c = map.getCenter();
    // a mucha inclinación, getBounds() cubre el suelo lejano y deja fuera las placas junto a la cámara
    const pad = 0.15 + 0.9 * Math.max(0, Math.tan(map.getPitch() * Math.PI / 180));
    const pl = (b.getEast() - b.getWest()) * pad, pa = (b.getNorth() - b.getSouth()) * pad;
    const w = b.getWest() - pl, e = b.getEast() + pl, so = b.getSouth() - pa, n = b.getNorth() + pa;
    const cos = Math.cos(c.lat * Math.PI / 180), out = [];
    for (const s of rows){
      if (s._aliasOf || s._dla === undefined) continue;
      if (s._dla < so || s._dla > n || s._dlo < w || s._dlo > e) continue;
      const dx = (s._dlo - c.lng) * cos, dy = s._dla - c.lat;
      out.push([dx * dx + dy * dy, s]);
    }
    out.sort((a, b2) => a[0] - b2[0]);
    inView = out.slice(0, MAX_STONES).map(x => x[1]);
  }

  // ---------- matriz con origen local (doble precisión) ----------
  function mul(a, b){ const o = new Float64Array(16); for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++){ let v = 0; for (let k = 0; k < 4; k++) v += a[k * 4 + j] * b[i * 4 + k]; o[i * 4 + j] = v; } return o; }

  const VS = `attribute vec3 a_pos; attribute vec2 a_uv; uniform mat4 u_m; varying vec2 v_uv;
    void main(){ v_uv = a_uv; gl_Position = u_m * vec4(a_pos, 1.0); }`;
  const FS = `precision mediump float; uniform sampler2D u_tex; uniform float u_shade; varying vec2 v_uv;
    void main(){ vec4 c = texture2D(u_tex, v_uv); gl_FragColor = vec4(c.rgb * u_shade, c.a); }`;

  const layer = {
    id: 'plaque-text', type: 'custom', renderingMode: '3d',
    onAdd(m, gl){
      const sh = (t, src) => { const x = gl.createShader(t); gl.shaderSource(x, src); gl.compileShader(x); if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(x)); return x; };
      const p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(p);
      if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
      this.p = p; this.aPos = gl.getAttribLocation(p, 'a_pos'); this.aUv = gl.getAttribLocation(p, 'a_uv');
      this.uM = gl.getUniformLocation(p, 'u_m'); this.uTex = gl.getUniformLocation(p, 'u_tex'); this.uShade = gl.getUniformLocation(p, 'u_shade');
      this.buf = gl.createBuffer(); this.gl = gl;
    },
    onRemove(m, gl){ try { for (const e of cache.values()) if (e.tex) gl.deleteTexture(e.tex); cache.clear(); if (this.buf) gl.deleteBuffer(this.buf); if (this.p) gl.deleteProgram(this.p); } catch (e) {} },
    render(gl, args){
      try { if (st.backend === 'html') return;
      const z = map.getZoom(), K = window.KLCols, ks = K && K.state ? K.state() : null;
      const cam = camera(ks ? ks.faceTop : 16.42), [mode, mwhy] = modeFor(z, cam.facePx, cam.above);
      const why = mwhy || (!ks || !ks.plaqueLayers ? 'sin-placas' : (ks.animating || ks.T < 1 ? 'animando' : ''));
      st.mode = why ? null : mode; st.skipped = why; st.facePx = Math.round(cam.facePx); st.camAlt = +cam.alt.toFixed(1);
      if (why){ st.drawn = 0; st.ids = []; st.quads = []; if (K && K.setTextIds) K.setTextIds([]); return; }
      const M = (args && args.defaultProjectionData && args.defaultProjectionData.mainMatrix) || (args && args.modelViewProjectionMatrix) || args;
      const c = map.getCenter(), ref = maplibregl.MercatorCoordinate.fromLngLat([c.lng, c.lat], 0), k = ref.meterInMercatorCoordinateUnits();
      // T(ref) · S(k, -k, k): vértices en metros (este, norte, arriba) alrededor del centro de la vista
      const L = new Float64Array([k, 0, 0, 0,  0, -k, 0, 0,  0, 0, k, 0,  ref.x, ref.y, 0, 1]);
      const MM = new Float32Array(mul(Array.from(M), L));
      const brg = map.getBearing() * Math.PI / 180, upE = Math.sin(brg), upN = Math.cos(brg);
      gl.useProgram(this.p);
      gl.uniformMatrix4fv(this.uM, false, MM);
      gl.uniform1i(this.uTex, 0); gl.activeTexture(gl.TEXTURE0);
      gl.uniform1f(this.uShade, document.body.classList.contains('dark') ? 0.85 : 1.0);
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
      gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL); gl.depthMask(false);
      gl.disable(gl.CULL_FACE);
      gl.bindBuffer(gl.ARRAY_BUFFER, this.buf);
      gl.enableVertexAttribArray(this.aPos); gl.enableVertexAttribArray(this.aUv);
      gl.vertexAttribPointer(this.aPos, 3, gl.FLOAT, false, 20, 0); gl.vertexAttribPointer(this.aUv, 2, gl.FLOAT, false, 20, 12);
      const drawn = [], quads = [], sel = typeof selected !== 'undefined' ? selected : null;
      for (const s of inView){
        // v35 C1: también se escribe la placa seleccionada (antes se saltaba y solo quedaba el fuste pálido)
        const top = K.topOf(s.id); if (!top) continue;
        const e = texFor(gl, s, mode); if (!e.tex) continue;
        const A = s._ang || 0, ca = Math.cos(A), sa = Math.sin(A);
        // de los 4 giros de 90° de la placa, el que deja el texto más derecho en pantalla
        let best = 0, bd = -2;
        for (let q = 0; q < 4; q++){ const a = A + q * Math.PI / 2, ue = -Math.sin(a), un = Math.cos(a), d = ue * upE + un * upN; if (d > bd){ bd = d; best = q; } }
        const a = A + best * Math.PI / 2, xa = [Math.cos(a), Math.sin(a)], ya = [-Math.sin(a), Math.cos(a)];
        const mc = maplibregl.MercatorCoordinate.fromLngLat([s._dlo, s._dla], 0);
        const ox = (mc.x - ref.x) / k, oy = -(mc.y - ref.y) / k, h = HALF_IN, zz = top + LIFT;   // metros exactos en Mercator alrededor del centro
        const P = (u, v) => [ox + (u * xa[0] + v * ya[0]) * h, oy + (u * xa[1] + v * ya[1]) * h, zz];
        const tl = P(-1, 1), tr = P(1, 1), br = P(1, -1), bl = P(-1, -1);
        const d = new Float32Array([...tl, 0, 0, ...tr, 1, 0, ...br, 1, 1,  ...tl, 0, 0, ...br, 1, 1, ...bl, 0, 1]);
        gl.bufferData(gl.ARRAY_BUFFER, d, gl.DYNAMIC_DRAW);
        gl.bindTexture(gl.TEXTURE_2D, e.tex);
        gl.drawArrays(gl.TRIANGLES, 0, 6);
        drawn.push(s.id); quads.push({id: s.id, a, half: h, z: zz, up: bd, lines: e.info.lines, px: e.info.px});
      }
      gl.depthMask(true);
      st.drawn = drawn.length; st.ids = drawn; st.quads = quads;
      if (K.setTextIds) K.setTextIds(drawn);
      } catch (e) { startFallback('render'); }
    }
  };


  // v35 C5: si la capa WebGL no arranca (shader, addLayer, GPU), las placas no se quedan solo con surcos.
  // Respaldo: etiquetas HTML sobre la cara (sin pedir nada a la red). Los surcos se dejan ver (el texto ya no está en la textura).
  st.backend = 'webgl';
  function projectTop(lng, lat, elev){
    try {
      const t = map.transform, ll = new maplibregl.LngLat(lng, lat);
      if (t.locationPoint && t.locationPoint.length >= 2) return t.locationPoint(ll, elev);
      const mc = maplibregl.MercatorCoordinate.fromLngLat([lng, lat], elev);
      if (typeof t.coordinatePoint === 'function') return t.coordinatePoint({x: mc.x, y: mc.y, z: mc.z});
    } catch (e) {}
    return map.project([lng, lat]);
  }
  function paintHtml(){
    refresh();
    const z = map.getZoom(), K = window.KLCols, ks = K && K.state ? K.state() : null;
    const cam = camera(ks ? ks.faceTop : 16.42), [mode, mwhy] = modeFor(z, cam.facePx, cam.above);
    const why = mwhy || (!ks || !ks.plaqueLayers ? 'sin-placas' : (ks.animating || ks.T < 1 ? 'animando' : ''));
    st.mode = why ? null : mode; st.skipped = why; st.facePx = Math.round(cam.facePx); st.camAlt = +cam.alt.toFixed(1);
    let box = document.getElementById('kl-plaque-fb');
    if (!box){ box = document.createElement('div'); box.id = 'kl-plaque-fb';
      box.style.cssText = 'position:absolute;inset:0;pointer-events:none;z-index:4;overflow:hidden;';
      (map.getCanvasContainer() || map.getContainer()).appendChild(box); }
    box.innerHTML = '';
    if (why){ st.drawn = 0; st.ids = []; st.quads = []; if (K && K.setTextIds) K.setTextIds([]); return; }
    const drawn = [], quads = [], fs = Math.max(9, Math.min(22, Math.round((cam.facePx || 40) / (mode === 'full' ? 9 : 5))));
    for (const s of inView){
      const lines = linesFor(s, mode); if (!lines) continue;
      const top = K && K.topOf ? K.topOf(s.id) : 16.42; if (!top) continue;
      const p = projectTop(s._dlo, s._dla, top + LIFT);
      const el = document.createElement('div');
      el.style.cssText = 'position:absolute;left:'+p.x+'px;top:'+p.y+'px;transform:translate(-50%,-50%);color:'+INK+';font:700 '+fs+'px/1.15 "Helvetica Neue",Arial,sans-serif;text-align:center;white-space:pre;text-shadow:0 0 3px '+FACE+',0 0 6px '+FACE+';';
      el.textContent = lines.join('\n');
      box.appendChild(el);
      drawn.push(s.id); quads.push({id: s.id, a: s._ang || 0, half: HALF_IN, z: top + LIFT, up: 1, lines: lines, px: fs});
    }
    st.drawn = drawn.length; st.ids = drawn; st.quads = quads;
  }
  function startFallback(why){
    if (st.backend === 'html') return;
    st.backend = 'html';
    if (why && !st.skipped) st.skipped = String(why);
    try { if (map.getLayer('plaque-text')) map.removeLayer('plaque-text'); } catch (e) {}
    if (window.KLCols && KLCols.setTextIds) KLCols.setTextIds([]);
    if (!st._fbOn){ st._fbOn = true; map.on('move', paintHtml); map.on('moveend', () => { refresh(); paintHtml(); }); document.addEventListener('kl:align', paintHtml); }
    paintHtml();
  }
  function install(){
    if (!window.map || !map.getStyle || !map.isStyleLoaded()) return setTimeout(install, 300);
    if (st.backend === 'html'){ paintHtml(); return; }
    if (map.getLayer('plaque-text')) return;
    try {
      const before = map.getLayer('sel-glow') ? 'sel-glow' : undefined;
      map.addLayer(layer, before);
      refresh();
      map.on('moveend', () => { refresh(); map.triggerRepaint(); });
      document.addEventListener('kl:align', () => { refresh(); map.triggerRepaint(); });
      map.on('styledata', () => {
        if (st.backend === 'html') return;
        try { if (!map.getLayer('plaque-text') && map.isStyleLoaded()) map.addLayer(layer, map.getLayer('sel-glow') ? 'sel-glow' : undefined); }
        catch (e) { startFallback('styledata'); }
      });
      map.triggerRepaint();
    } catch (e) { startFallback('install'); }
  }
  root.KLPlaqueText = Object.assign({}, API, {state: () => Object.assign({}, st, {inView: inView.map(s => s.id), backend: st.backend}), refresh, startFallback, layerId: 'plaque-text', _cache: cache, _paint: paint});
  install();
})(typeof window !== 'undefined' ? window : globalThis);
