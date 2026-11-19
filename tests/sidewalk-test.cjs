// v19: placas de IE/SE/JE/FI/RO fuera de los edificios de OSM (instantánea tests/sidewalk/footprints-v19.json, © OpenStreetMap, ODbL).
// Prueba de DATOS: la posición de dibujo (dla/dlo si existe; si no, la de origen) queda fuera de todo edificio y a >= 0,95 m del borde (la columna dibujada mide 1,2 m);
// el desplazamiento respecto al origen es <= 25 m; las coordenadas de origen no se tocan. La comprobación de la posición realmente dibujada (con la cuadrícula
// de la app) está en tests/sidewalk-render-check.py.
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
function assert(c, m) { if (!c) throw new Error('FAIL: ' + m); }
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/stones.json'), 'utf8')).stones;
const FP = JSON.parse(fs.readFileSync(path.join(ROOT, 'tests/sidewalk/footprints-v19.json'), 'utf8'));
const T = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/sidewalk-v19.json'), 'utf8'));
const M_LAT = 111320, CCS = ['IE', 'SE', 'JE', 'FI', 'RO'], CLEAR = 0.95, MAXMOVE = 25;
const xy = (la, lo, o) => [(lo - o[1]) * M_LAT * Math.cos(o[0] * Math.PI / 180), (la - o[0]) * M_LAT];
const pip = (x, y, r) => { let ins = false; for (let i = 0; i < r.length - 1; i++) { const [x1, y1] = r[i], [x2, y2] = r[i + 1]; if ((y1 > y) !== (y2 > y) && x < (x2 - x1) * (y - y1) / (y2 - y1) + x1) ins = !ins; } return ins; };
const segd = (px, py, a, b) => { const dx = b[0] - a[0], dy = b[1] - a[1], L = dx * dx + dy * dy; const t = L ? Math.max(0, Math.min(1, ((px - a[0]) * dx + (py - a[1]) * dy) / L)) : 0; return Math.hypot(px - a[0] - t * dx, py - a[1] - t * dy); };
function check(s, la, lo) {
  const o = [la, lo]; let min = 1e9, inside = null;
  for (const bid of FP.near[s.id] || []) {
    const b = FP.buildings[bid]; const ro = b.o.map(r => r.map(p => xy(p[0], p[1], o))), ri = b.i.map(r => r.map(p => xy(p[0], p[1], o)));
    if (ro.some(r => pip(0, 0, r)) && !ri.some(r => pip(0, 0, r))) inside = bid;
    for (const r of ro.concat(ri)) for (let i = 0; i < r.length - 1; i++) min = Math.min(min, segd(0, 0, r[i], r[i + 1]));
  }
  return { inside, min };
}
const hav = (a, b, c, d) => { const p = Math.PI / 180, x = Math.sin((c - a) * p / 2) ** 2 + Math.cos(a * p) * Math.cos(c * p) * Math.sin((d - b) * p / 2) ** 2; return 2 * 6371000 * Math.asin(Math.sqrt(x)); };
const st = D.filter(s => CCS.includes(s.cc)); assert(st.length === 41, '41 placas IE6+SE6+JE20+FI7+RO2: ' + st.length);
assert(Object.keys(FP.near).length === 41 && T.stones.length === 41, 'instantánea y tabla con las 41');
let adj = 0, outsideAlready = 0;
for (const s of st) {
  const la = s.dla ?? s.la, lo = s.dlo ?? s.lo, r = check(s, la, lo);
  assert(!r.inside, `${s.id} ${s.n}: la posición de dibujo cae DENTRO del edificio ${r.inside}`);
  assert(r.min >= CLEAR, `${s.id} ${s.n}: a ${r.min.toFixed(2)} m de un edificio (< ${CLEAR} m, la columna se solaparía)`);
  const mv = hav(s.la, s.lo, la, lo); assert(mv <= MAXMOVE, `${s.id}: desplazada ${mv.toFixed(1)} m (> ${MAXMOVE})`);
  assert((s.dla == null) === (s.dlo == null), 'dla y dlo van juntos ' + s.id);
  if (s.dla != null) adj++; else outsideAlready++;
  const row = T.stones.find(x => x.id === s.id); assert(row, 'fila en data/sidewalk-v19.json ' + s.id);
  assert((row.estado === 'ajustada') === (s.dla != null), 'tabla coincide con los datos ' + s.id);
  assert(row.estado !== 'revisar', 'ninguna placa pendiente de revisión ' + s.id);
  if (row.estado === 'ajustada') assert(Math.abs(row.desplazamiento_m - mv) < 0.1 + 0.05 * mv, 'desplazamiento de la tabla ' + s.id);
  // coordenada de origen intacta: la de la tabla es la de stones.json
  assert(Math.abs(row.la - s.la) < 1e-9 && Math.abs(row.lo - s.lo) < 1e-9, 'origen intacto ' + s.id);
}
// el origen de cada placa añadida en v18/v19 coincide con la fuente (manifiestos)
for (const f of ['v19-added-20261119.json', 'se-added-20261119.json']) { const M = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', f), 'utf8')); for (const a of M.added) { const s = D.find(x => x.id === a.id); assert(s && Math.abs(s.la - a.la) < 1e-9 && Math.abs(s.lo - a.lo) < 1e-9, 'coordenada de origen = manifiesto ' + a.id); } }
console.log(`OK sidewalk: 41 placas fuera de edificios (${adj} con posición de dibujo ajustada, ${outsideAlready} ya en la acera), desplazamientos <= ${MAXMOVE} m, origen intacto`);
