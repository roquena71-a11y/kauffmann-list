// v31 (paso 3): funciones puras de plaquetext.js sobre TODAS las placas de data/stones.json + municipales:
// el texto sale solo del campo i (nada inventado), nada se pierde al ajustar líneas, la línea del nombre es un trozo literal de i,
// y el contraste de las letras sobre la cara de latón cumple WCAG (>= 4,5:1).
const fs = require('fs'), path = require('path');
const P = require('../plaquetext.js');
const ROOT = path.join(__dirname, '..');
function assert(c, m){ if (!c){ console.error('FAIL: ' + m); process.exit(1); } }
const stones = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'stones.json'), 'utf8')).stones;
for (const f of fs.readdirSync(path.join(ROOT, 'data')).filter(f => /-added-2026112\d\.json$/.test(f))){
  const j = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', f), 'utf8'));
  for (const s of (Array.isArray(j.stones) ? j.stones : [])) stones.push(s);
}
const up = t => String(t).toLocaleUpperCase('de-DE');
const words = ls => ls.join(' ').split(/\s+/).filter(Boolean);
const measureAt = (t, px) => t.length * px * 0.62;   // ancho aproximado de una sans en negrita
let withI = 0, full = 0, named = 0, noName = 0, overflow = 0;
for (const s of stones){
  const L = P.linesFor(s, 'full');
  if (!s.i){ assert(L === null, `${s.id}: sin i pero hay texto`); assert(P.linesFor(s, 'name') === null, `${s.id}: sin i pero hay nombre`); continue; }
  withI++;
  assert(L && L.length, `${s.id}: con i pero sin texto`);
  // 1) mismo texto que la ficha (cortes «|» y saltos), solo en mayúsculas
  const ref = String(s.i).replace(/\s*\|\s*/g, '\n').split(/\n/).map(x => x.trim()).filter(Boolean).map(up);
  assert(JSON.stringify(L) === JSON.stringify(ref), `${s.id}: líneas distintas de la ficha`);
  full++;
  // 2) ajuste: ninguna palabra se pierde, cambia ni se inventa
  for (const [box, maxPx, minPx] of [[476, 64, 6], [238, 72, 10]]){
    const f = P.fit(L, box, measureAt, maxPx, minPx);
    assert(JSON.stringify(words(f.lines)) === JSON.stringify(words(L)), `${s.id}: el ajuste cambió las palabras`);
    if (f.overflow) overflow++;
  }
  // 3) nombre: trozo literal de i que contiene el nombre
  const n = P.nameLine(s);
  if (n){ named++; assert(String(s.i).includes(n), `${s.id}: la línea del nombre no es literal de i: ${n}`); }
  else noName++;
}
const cr = P.contrast(P.INK, P.FACE);
assert(cr >= 4.5, `contraste ${cr.toFixed(2)} < 4,5`);
assert(P.contrast('#000000', '#ffffff') > 20.9 && Math.abs(P.contrast('#777777', '#ffffff') - 4.48) < 0.02, 'fórmula de contraste');
assert(P.Z_ON === 20 && P.Z_NAME === 20.5 && P.Z_FULL === 21.5, 'umbrales de zoom');
console.log(`OK plaque-text (unidad): ${stones.length} placas, ${withI} con inscripción (texto = ficha en mayúsculas, ${full}), ${stones.length - withI} en blanco; línea del nombre literal en ${named} (sin línea de nombre: ${noName}); ajuste sin perder palabras (no caben ni a la letra mínima y quedan lisas: ${overflow}); contraste letras/cara ${cr.toFixed(2)}:1`);
