const norm = s => String(s||'').toLowerCase().replace(/ß/g,'ss').replace(/ä/g,'a').replace(/ö/g,'o').replace(/ü/g,'u')
  .normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,' ').trim();
const $ = s => document.querySelector(s);
let DATA = [], byId = new Map();
const map = L.map('map', {zoomControl:true}).setView([51.1, 10.4], 6);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap'
}).addTo(map);
const cluster = L.markerClusterGroup({chunkedLoading:true, maxClusterRadius:48, spiderfyOnMaxZoom:true});
const icon = L.divIcon({className:'', iconSize:[12,12], iconAnchor:[6,6],
  html:'<span style="display:block;width:12px;height:12px;background:linear-gradient(135deg,#f0d48a,#c6a15b);border:1px solid #6b5424"></span>'});

function popup(s){
  const name = s.n || '—';
  const place = [s.a, s.c || s.cd, s.cc && s.cc!=='DE' ? s.cc : ''].filter(Boolean).join(', ');
  return '<strong>'+esc(name)+'</strong><br>'+esc(place)+
    (s.gm ? '<br><small>Posición aproximada (del edificio, por su dirección en OpenStreetMap)</small>' : '')+
    (s.disc ? '<br><small>Las fuentes no coinciden en la dirección (OpenStreetMap: «'+esc(s.a)+'»; otras fuentes: «'+esc(s.disc.alt)+'»). Ver la ficha en el mapa 3D.</small>' : '')+
    '<br><a href="../#s='+encodeURIComponent(s.id)+'">Abrir en el mapa 3D</a>';
}
function esc(s){ return String(s??'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

// Posición de DIBUJO (v19): dla/dlo si existen (columna sacada de un edificio hacia la acera); la de origen (la/lo) no se toca y es la que usan los enlaces de ruta y los datos.
const dpos = s => [s.dla ?? s.la, s.dlo ?? s.lo];
function show(s){
  const m = L.marker(dpos(s), {icon}).bindPopup(popup(s));
  map.flyTo(dpos(s), 17);
  m.addTo(map).openPopup();
}
function search(){
  const q = norm($('#q').value);
  const list = $('#results');
  if (!q) { list.innerHTML=''; $('#status').textContent = DATA.length.toLocaleString('es')+' placas.'; return; }
  const words = q.split(' ');
  const out = [];
  for (const s of DATA) {
    const t = s._t;
    if (words.every(w => t.some(tok => tok.startsWith(w) || tok===w))) out.push(s);
    if (out.length >= 200) break;
  }
  $('#status').textContent = out.length + ' resultados';
  list.innerHTML = out.map(s => '<li><button data-id="'+esc(s.id)+'"><b>'+esc(s.n||'—')+'</b><br><small>'+esc(s.a||s.c||'')+'</small></button></li>').join('');
}
$('#q').addEventListener('input', () => { clearTimeout(search._t); search._t = setTimeout(search, 160); });
$('#results').addEventListener('click', e => { const b = e.target.closest('button'); if (b) show(byId.get(b.dataset.id)); });

fetch('../data/stones.json').then(r => r.json()).then(j => {
  DATA = j.stones;
  for (const s of DATA) {
    s._t = norm([s.n, s.a, s.c, s.cd].join(' ')).split(' ');
    byId.set(s.id, s);
    cluster.addLayer(L.marker(dpos(s), {icon}).bindPopup(popup(s)));
  }
  map.addLayer(cluster);
  $('#status').textContent = DATA.length.toLocaleString('es') + ' placas. Escriba un nombre.';
  const m = /[#?]s=([^&]+)/.exec(location.hash + location.search);
  if (m && byId.has(decodeURIComponent(m[1]))) show(byId.get(decodeURIComponent(m[1])));
}).catch(() => { $('#status').textContent = 'No se pudieron cargar las placas.'; });
