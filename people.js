/* Lista Kauffmann — personas de Wikidata (api/v1/cc0, CC0) en la búsqueda y en las fichas.
   Se carga después de app3d.js y usa sus funciones globales ($, esc, T, norm, map, closeDetail…).
   Las fichas de Wikidata (CC0) y las placas (ODbL) se unen solo aquí, en el navegador, por Qid:
   así cada base mantiene su licencia (ver docs/legal/analisis-licencias.md). */
(function(){
  'use strict';
  const API = 'api/v1/cc0/';
  const REPO_ISSUES = 'https://github.com/roquena71-a11y/kauffmann-list/issues/new';

  Object.assign(I18N.es, {
    wdPeople:'Personas registradas en Wikidata (sin placa en este mapa)', wdMore:'Busque por apellido para ver más personas de Wikidata.',
    wdData:'Datos de Wikidata', wdNote:'Datos de Wikidata (CC0). No hay placa de esta persona en el mapa.', wdStone:'Datos de Wikidata (CC0). Esta persona tiene placa en el mapa:',
    fate:'Destino', murdered:'Asesinado/a', suicide:'Suicidio durante la persecución', records:'Fichas en archivos y memoriales',
    hcz:'holocaust.cz — Base de víctimas (Chequia)', jm:'Joods Monument (Países Bajos)', wikipedia:'Wikipedia',
    fix:'Corregir o pedir retirada', fixNote:'Abre un formulario en GitHub (necesita cuenta). Indique qué dato es erróneo y la fuente.',
    nearPlace:'Ver lugar en el mapa', shareP:'Copiar enlace a esta ficha'
  });
  Object.assign(I18N.de, {
    wdPeople:'In Wikidata erfasste Personen (ohne Stein auf dieser Karte)', wdMore:'Suchen Sie nach dem Nachnamen, um weitere Personen aus Wikidata zu sehen.',
    wdData:'Daten aus Wikidata', wdNote:'Daten aus Wikidata (CC0). Für diese Person gibt es keinen Stein auf der Karte.', wdStone:'Daten aus Wikidata (CC0). Für diese Person gibt es einen Stein auf der Karte:',
    fate:'Schicksal', murdered:'Ermordet', suicide:'Suizid während der Verfolgung', records:'Einträge in Archiven und Gedenkstätten',
    hcz:'holocaust.cz — Opferdatenbank (Tschechien)', jm:'Joods Monument (Niederlande)', wikipedia:'Wikipedia',
    fix:'Korrektur oder Entfernung beantragen', fixNote:'Öffnet ein Formular auf GitHub (Konto nötig). Bitte Fehler und Quelle angeben.',
    nearPlace:'Ort auf der Karte zeigen', shareP:'Link zu diesem Eintrag kopieren'
  });
  Object.assign(I18N.en, {
    wdPeople:'People recorded in Wikidata (no stone on this map)', wdMore:'Search by surname to see more people from Wikidata.',
    wdData:'Data from Wikidata', wdNote:'Data from Wikidata (CC0). There is no stone for this person on the map.', wdStone:'Data from Wikidata (CC0). This person has a stone on the map:',
    fate:'Fate', murdered:'Murdered', suicide:'Suicide during persecution', records:'Records in archives and memorials',
    hcz:'holocaust.cz — Victims database (Czechia)', jm:'Joods Monument (Netherlands)', wikipedia:'Wikipedia',
    fix:'Report a correction or request removal', fixNote:'Opens a form on GitHub (account needed). Please state the error and the source.',
    nearPlace:'Show place on the map', shareP:'Copy link to this record'
  });


  Object.assign(I18N.es, { deathBtn:'Dónde murieron', deathTitle:(n)=>`${n} personas registradas en Wikidata murieron aquí`,
    deathNote:'Lugar de muerte según Wikidata (CC0). La lista está incompleta: solo incluye a quienes ya están en Wikidata.', more:'Ver más' });
  Object.assign(I18N.de, { deathBtn:'Wo sie starben', deathTitle:(n)=>`${n} in Wikidata erfasste Personen starben hier`,
    deathNote:'Sterbeort laut Wikidata (CC0). Die Liste ist unvollständig: sie enthält nur Personen, die bereits in Wikidata erfasst sind.', more:'Mehr anzeigen' });
  Object.assign(I18N.en, { deathBtn:'Where they died', deathTitle:(n)=>`${n} people recorded in Wikidata died here`,
    deathNote:'Place of death according to Wikidata (CC0). The list is incomplete: it only includes people already in Wikidata.', more:'Show more' });

  /* ---------- carga perezosa con caché en memoria ---------- */
  const cache = new Map();
  function getJSON(u){
    if (!cache.has(u)) cache.set(u, fetch(u).then(r => r.ok ? r.json() : null).catch(() => null));
    return cache.get(u);
  }
  const catalog = () => getJSON(API + 'index.json');

  /* Misma normalización que pipeline/util.py fold() y surname_key(). */
  const TR = {'ł':'l','ø':'o','đ':'d','ð':'d','þ':'th','æ':'ae','œ':'oe','ı':'i'};
  const PARTICLES = new Set(['von','van','de','der','den','zu','zur','vom','ten','ter','da','di','del','la','le']);
  function fold(s){
    return String(s||'').toLowerCase().replace(/ß/g,'ss').replace(/ä/g,'a').replace(/ö/g,'o').replace(/ü/g,'u')
      .replace(/[łøđðþæœı]/g, c => TR[c]).normalize('NFD').replace(/[̀-ͯ]/g,'')
      .replace(/ae/g,'a').replace(/oe/g,'o').replace(/ue/g,'u').replace(/[^a-z0-9]+/g,' ').trim();
  }
  function prefixFor(key, prefixes){
    let best = null;
    for (const p of prefixes) if (p !== '_' && key.startsWith(p) && (!best || p.length > best.length)) best = p;
    return best;
  }

  /* ---------- búsqueda ---------- */
  let ticket = 0;
  async function findPeople(query, place, exclude){
    const my = ++ticket;
    const qt = fold(query).split(' ').filter(w => w.length >= 2 && !PARTICLES.has(w)).slice(0, 4);
    if (!qt.some(w => w.length >= 3)) return null;
    const cat = await catalog(); if (!cat || my !== ticket) return null;
    const shards = [...new Set(qt.filter(w => w.length >= 3).map(w => prefixFor(w.replace(/[^a-z]/g,''), cat.search_prefixes)).filter(Boolean))];
    const packs = await Promise.all(shards.map(p => getJSON(API + 'search/index-' + p + '.json')));
    if (my !== ticket) return null;
    const pl = fold(place), out = [], seen = new Set();
    for (const pk of packs){
      if (!pk) continue;
      const C = Object.fromEntries(pk.columns.map((c, i) => [c, i]));
      for (const r of pk.rows){
        const id = r[C.id]; if (seen.has(id) || exclude.has(id)) continue;
        const toks = fold(r[C.name]).split(' ');
        if (!qt.every(w => toks.some(t => t.startsWith(w)))) continue;
        if (pl && !fold(r[C.locality]).includes(pl)) continue;
        seen.add(id);
        out.push({id, name:r[C.name], year:r[C.birth_year], loc:r[C.locality], lat:r[C.lat], lon:r[C.lon]});
      }
    }
    out.sort((a, b) => (a.name||'').localeCompare(b.name||'', 'de'));
    return out;
  }

  const LIMIT = 200;
  window.KLPeople = {
    /* Añade a la lista de resultados las personas de Wikidata que no tienen placa en el mapa. */
    async append(query, place, stoneHits){
      const list = $('#results');
      list.querySelectorAll('.wd-sep,.wd-hit').forEach(el => el.remove());
      const exclude = new Set(stoneHits.filter(s => s.p).map(s => 'wd-' + s.p));
      const res = await findPeople(query, place, exclude);
      if (!res || !res.length) return;
      const shown = res.slice(0, LIMIT);
      const html = `<li class="wd-sep"><div class="section-t">${esc(T('wdPeople'))} · ${fmtNum(res.length)}${res.length > LIMIT ? '+' : ''}</div></li>` +
        shown.map(p => `<li class="wd-hit"><button data-pid="${esc(p.id)}"><div class="nm">${esc(p.name||'—')}</div>
          <div class="meta">${esc([p.loc, p.year ? '* ' + p.year : ''].filter(Boolean).join(' · '))}</div></button></li>`).join('');
      list.insertAdjacentHTML('beforeend', html);
      if (!stoneHits.length) $('#status').textContent = T('results')(fmtNum(shown.length), res.length > LIMIT);
    },
    open: openPerson,
    fixLink
  };

  /* ---------- ficha de persona ---------- */
  async function loadPerson(pid){
    const shard = pid.slice(-2).toLowerCase().replace(/[^a-z0-9]/g, '_');
    const look = await getJSON(API + 'person/' + shard + '.json'); if (!look) return null;
    const row = look.rows.find(r => r[0] === pid); if (!row) return null;
    const pack = await getJSON(API + 'people/by-surname/' + row[1] + '.json'); if (!pack) return null;
    return pack.people.find(p => p.id === pid) || null;
  }
  const LINK_LABEL = {gedenkbuch:'gb', yad_vashem:'yv', ushmm:'ushmm', arolsen:'arolsen', holocaust_cz:'hcz', joods_monument:'jm', wikipedia:'wikipedia'};
  function personBlocks(p, skip){
    const fate = p.fate === 'murdered' ? T('murdered') : p.fate === 'suicide' ? T('suicide') : '';
    const facts = [[T('born'), [p.birth_date, p.birth_place].filter(Boolean).join(' · ')],
                   [T('died'), [p.death_date, p.death_place].filter(Boolean).join(' · ')],
                   [T('fate'), fate]]
      .filter(x => x[1]).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('');
    const recs = (p.links||[]).filter(l => LINK_LABEL[l.type] && !(skip && skip.has(l.url)))
      .map(l => `<li><a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(T(LINK_LABEL[l.type]))}</a></li>`).join('');
    return {facts, recs};
  }
  function fixLink(kind, id, name){
    const title = `${kind === 'stone' ? 'Placa' : 'Persona'} ${id}: corrección / retirada`;
    const body = `Ficha: ${location.origin}${location.pathname}#${kind === 'stone' ? 's' : 'p'}=${encodeURIComponent(id)}\nNombre: ${name||''}\n\nQué dato es erróneo o por qué pide la retirada:\n\nFuente que lo demuestra:\n`;
    return `<p class="note"><a href="${REPO_ISSUES}?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}" target="_blank" rel="noopener">${esc(T('fix'))}</a> — ${esc(T('fixNote'))}</p>`;
  }

  async function openPerson(pid, pt){
    const p = await loadPerson(pid); if (!p) return false;
    if (document.body.classList.contains('vigil-on')) stopVigil();
    selected = null; refreshSel();
    history.replaceState(null, '', '#p=' + encodeURIComponent(pid));
    const place = (p.places||[]).find(x => x.role === 'death' && x.lat != null) || (p.places||[]).find(x => x.lat != null);
    const ll = pt && pt.lat != null ? pt : place;
    if (ll && map) map.flyTo({center:[ll.lon, ll.lat], zoom:9, pitch:30, duration: reduceMotion ? 0 : 2400, essential:true});
    const {facts, recs} = personBlocks(p);
    const qid = p.identifiers && p.identifiers.wikidata;
    const d = $('#detail');
    // Placas enlazadas a esta persona por su Qid (s.p); si hay, el aviso lo dice y enlaza a ellas.
    const qn = qid ? String(qid).replace(/^wd-/, '') : (pid.startsWith('wd-') ? pid.slice(3) : null);
    const linked = qn ? [...byId.values()].filter(s => s.p === qn) : [];
    const note = linked.length
      ? `${esc(T('wdStone'))} ${linked.map(s => `<a href="#" data-stone="${esc(s.id)}">${esc([s.a, s.a && s.a.includes(cityOf(s)) ? "" : cityOf(s)].filter(Boolean).join(", ") || s.n)}</a>`).join(', ')}`
      : esc(T('wdNote'));
    d.innerHTML = `<button class="back" id="back">${T('back')}</button>
      <h2>${esc(p.name||'—')}</h2>
      <p class="note">${note}</p>
      <dl class="facts">${facts}</dl>
      <div class="actions"><button id="share">${T('shareP')}</button></div>
      ${recs ? `<div class="section-t">${T('records')}</div><ul class="links">${recs}</ul>` : ''}
      <div class="section-t">${T('sources')}</div>
      <ul class="links">${qid ? `<li><a href="https://www.wikidata.org/wiki/${esc(qid)}" target="_blank" rel="noopener">Wikidata ${esc(qid)}</a> (CC0)</li>` : ''}</ul>
      ${fixLink('person', pid, p.name)}`;
    $('#results').hidden = true; d.hidden = false; d.scrollTop = 0;
    $('#back').onclick = () => closeDetail(true);
    $('#share').onclick = e => { navigator.clipboard?.writeText(location.href); e.target.textContent = T('copied'); };
    d.querySelectorAll('a[data-stone]').forEach(a => a.onclick = ev => { ev.preventDefault(); openStone(a.dataset.stone, false); });
    return true;
  }

  /* ---------- enganches en app3d.js ---------- */
  $('#results').addEventListener('click', e => { const b = e.target.closest('button[data-pid]'); if (b) openPerson(b.dataset.pid); });

  // Ficha de placa: añade los datos de Wikidata de la persona (si existe ficha CC0) y el enlace de corrección.
  const _openStone = openStone;
  openStone = function(id, fromMap){
    _openStone(id, fromMap);
    const s = byId.get(id); if (!s) return;
    const d = $('#detail');
    d.insertAdjacentHTML('beforeend', fixLink('stone', id, s.n));
    if (!s.p) return;
    loadPerson('wd-' + s.p).then(p => {
      if (!p || selected !== id) return;
      // No repetir enlaces que la ficha de la placa ya muestra (sección de archivos).
      const shown = new Set([...d.querySelectorAll('a[href]')].map(a => a.href));
      const {facts, recs} = personBlocks(p, shown);
      if (!facts && !recs) return;
      const slot = $('#storySlot');
      const html = `<div class="section-t">${esc(T('wdData'))}</div>${facts ? `<dl class="facts">${facts}</dl>` : ''}
        ${recs ? `<ul class="links">${recs}</ul>` : ''}`;
      if (slot) slot.insertAdjacentHTML('beforebegin', html); else d.insertAdjacentHTML('beforeend', html);
    });
  };

  // Enlaces directos a una persona: #p=wd-Q…
  const _route = route;
  route = function(){
    const m = /#p=([^&]+)/.exec(location.hash);
    if (m){ openPerson(decodeURIComponent(m[1])).then(ok => { if (!ok) _route(); }); return; }
    _route();
  };


  /* ---------- capa «Dónde murieron»: lugares de muerte de las personas de Wikidata ---------- */
  let deathOn = false, deathFC = null;
  async function deathData(){
    if (deathFC) return deathFC;
    const idx = await getJSON(API + 'places/index.json'); if (!idx) return null;
    const C = Object.fromEntries(idx.columns.map((c, i) => [c, i]));
    deathFC = {type:'FeatureCollection', features: idx.rows.filter(r => r[C.lat] != null).map(r => ({type:'Feature',
      properties:{cc:r[C.country], slug:r[C.slug], label:r[C.label], n:r[C.count], pages:r[C.pages]},
      geometry:{type:'Point', coordinates:[r[C.lon], r[C.lat]]}}))};
    return deathFC;
  }
  function addDeathLayer(){
    if (!deathOn || !deathFC || !map || map.getSource('death')) return;
    map.addSource('death', {type:'geojson', data:deathFC});
    map.addLayer({id:'death-glow', type:'circle', source:'death',
      paint:{'circle-radius':['interpolate',['linear'],['zoom'],3,['*',1.6,['^',['get','n'],0.3333]],8,['*',3.2,['^',['get','n'],0.3333]],12,['*',6,['^',['get','n'],0.3333]]],
             'circle-color':'#dfe6f0','circle-opacity':0.18,'circle-blur':0.8,'circle-pitch-alignment':'map'}});
    map.addLayer({id:'death', type:'circle', source:'death',
      paint:{'circle-radius':['interpolate',['linear'],['zoom'],3,['max',2.5,['*',0.8,['^',['get','n'],0.3333]]],8,['max',4,['*',1.6,['^',['get','n'],0.3333]]],12,['max',6,['*',3,['^',['get','n'],0.3333]]]],
             'circle-color':'#cfd8e6','circle-opacity':0.75,'circle-stroke-color':'#f6f3ec','circle-stroke-width':1,'circle-pitch-alignment':'map'}});
  }
  function removeDeathLayer(){
    if (!map) return;
    ['death', 'death-glow'].forEach(l => { if (map.getLayer(l)) map.removeLayer(l); });
    if (map.getSource('death')) map.removeSource('death');
  }
  async function toggleDeath(){
    deathOn = !deathOn; paintDeathBtn();
    if (!deathOn){ removeDeathLayer(); return; }
    await deathData(); addDeathLayer();
    if (map) map.flyTo({center:[15.5, 50.8], zoom:4.9, pitch:20, duration: reduceMotion ? 0 : 2200, essential:true});
  }
  function paintDeathBtn(){ const b = $('#deathBtn'); if (b){ b.textContent = T('deathBtn'); b.setAttribute('aria-pressed', deathOn); } }

  async function openPlace(props, page){
    const name = props.slug + (page > 1 ? '~' + page : '');
    const pk = await getJSON(API + 'places/' + props.cc.toLowerCase() + '/' + name + '.json'); if (!pk) return;
    const C = Object.fromEntries(pk.columns.map((c, i) => [c, i]));
    const items = pk.rows.map(r => `<li><button data-pid="${esc(r[C.id])}"><div class="nm">${esc(r[C.name]||'—')}</div>
      <div class="meta">${r[C.birth_year] ? '* ' + esc(r[C.birth_year]) : ''}</div></button></li>`).join('');
    const d = $('#detail');
    if (page > 1){
      d.querySelector('#placeMore')?.remove();
      d.querySelector('#placeList').insertAdjacentHTML('beforeend', items);
    } else {
      if (document.body.classList.contains('vigil-on')) stopVigil();
      selected = null; refreshSel();
      d.innerHTML = `<button class="back" id="back">${T('back')}</button>
        <h2>${esc(props.label)}</h2>
        <p class="place">${esc(T('deathTitle')(fmtNum(props.n)))}</p>
        <p class="note">${esc(T('deathNote'))}</p>
        <ul class="results" id="placeList">${items}</ul>`;
      $('#results').hidden = true; d.hidden = false; d.scrollTop = 0;
      $('#back').onclick = () => closeDetail(true);
    }
    if (page < props.pages){
      d.insertAdjacentHTML('beforeend', `<p id="placeMore"><button class="linkish">${esc(T('more'))}</button></p>`);
      d.querySelector('#placeMore button').onclick = () => openPlace(props, page + 1);
    }
  }

  // Botón en la barra de mapas base, junto a «Fuentes».
  const bar = document.querySelector('.basemaps');
  if (bar){
    bar.insertAdjacentHTML('beforeend', '<button type="button" id="deathBtn" class="death-btn" aria-pressed="false"></button>');
    paintDeathBtn();
    $('#deathBtn').onclick = toggleDeath;
  }
  $('#detail').addEventListener('click', e => { const b = e.target.closest('button[data-pid]'); if (b) openPerson(b.dataset.pid); });
  // Cambiar de idioma repinta el botón.
  document.querySelectorAll('.lang button').forEach(b => b.addEventListener('click', paintDeathBtn));
  // Al cambiar el mapa base se rehacen las capas: volver a poner la de lugares de muerte.
  const _addOverlays = addOverlays;
  addOverlays = function(){ _addOverlays(); addDeathLayer(); };
  // Clic y cursor en los círculos (el mapa ya existe cuando se carga este archivo, o se crea enseguida).
  (function wire(){
    if (!map){ setTimeout(wire, 200); return; }
    map.on('click', 'death', e => {
      // Varios lugares en el mismo punto (p. ej. «Terezín», «Ghetto Theresienstadt», «KZ Theresienstadt»): elegir.
      const seen = new Set(), fs = (e.features || []).map(f => f.properties).filter(p => !seen.has(p.slug + p.cc) && seen.add(p.slug + p.cc))
        .sort((a, b) => b.n - a.n);
      if (fs.length === 1) { openPlace(fs[0], 1); return; }
      if (!fs.length) return;
      if (document.body.classList.contains('vigil-on')) stopVigil();
      const d = $('#detail');
      d.innerHTML = `<button class="back" id="back">${T('back')}</button><h2>${esc(T('deathBtn'))}</h2>
        <p class="note">${esc(T('deathNote'))}</p>
        <ul class="results">${fs.map((p, i) => `<li><button data-place="${i}"><div class="nm">${esc(p.label)}</div>
          <div class="meta">${fmtNum(p.n)}</div></button></li>`).join('')}</ul>`;
      $('#results').hidden = true; d.hidden = false; d.scrollTop = 0;
      $('#back').onclick = () => closeDetail(true);
      d.querySelectorAll('button[data-place]').forEach(b => b.onclick = () => openPlace(fs[+b.dataset.place], 1));
    });
    map.on('mouseenter', 'death', () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', 'death', () => map.getCanvas().style.cursor = '');
  })();

  // Búsqueda: tras pintar las placas, añade las personas de Wikidata.
  const _search = search;
  search = function(){
    _search();
    const q = $('#q').value;
    if (!q.trim()) { $('#results').querySelectorAll('.wd-sep,.wd-hit').forEach(el => el.remove()); return; }
    const hits = [...$('#results').querySelectorAll('button[data-id]')].map(b => byId.get(b.dataset.id)).filter(Boolean);
    KLPeople.append(q, $('#city').value, hits);
  };
})();
