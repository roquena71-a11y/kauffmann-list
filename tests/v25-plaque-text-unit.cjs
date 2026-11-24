// v31 (paso 3): funciones puras de plaquetext.js sobre TODAS las placas de data/stones.json + municipales:
// el texto sale solo del campo i (nada inventado), nada se pierde al ajustar líneas, la línea del nombre es un trozo literal de i,
// y el contraste de las letras sobre la cara de latón cumple WCAG (>= 4,5:1).
// v32: las inscripciones con marcado (<br />, '''…''', [[…|…]], &#…;) se muestran limpias (KLDedupe.inscDisplay, ficha y placa):
// no queda ninguna etiqueta ni sintaxis wiki, y no se pierde ni se añade ninguna palabra (comparado con una referencia independiente).
const fs = require('fs'), path = require('path');
const P = require('../plaquetext.js');
const D = require('../dedupe.js');
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
  const ref = D.inscDisplay(s.i).replace(/\s*\|\s*/g, '\n').split(/\n/).map(x => x.trim()).filter(Boolean).map(up);
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
  if (n){ named++; assert(D.inscDisplay(s.i).includes(n), `${s.id}: la línea del nombre no es literal de i: ${n}`); }
  else noName++;
}
// ---------- v32: marcado HTML/wiki ----------
const MARKUP = /<\/?[a-z][^<>]*>|'''|\[\[|\]\]|&(#x?[0-9a-f]+|[a-z]+);/i;
const LEFT = /<\/?[a-z][^<>]*>|'''|\[\[|\]\]|&(#x?[0-9a-f]+|nbsp|amp|quot|lt|gt|apos|shy|[lr]squo|sbquo|[lr]dquo|bdquo|[nm]dash);/i;
const ENTREF = {'&#8218;': '‚', '&#8216;': '‘', '&nbsp;': ' ', '&amp;': '&'};
// referencia independiente: quita el marcado sin reglas finas y compara solo las PALABRAS (letras y cifras)
function refWords(raw){
  let x = String(raw).replace(/\[\[[^\]|]*\|/g, ' ').replace(/<[^<>]*>/g, ' ').replace(/'''/g, ' ').replace(/\[\[|\]\]/g, ' ');
  for (const [k, v] of Object.entries(ENTREF)) x = x.split(k).join(' ' + v + ' ');
  return x.split(/[^\p{L}\p{N}]+/u).filter(Boolean).join(' ');
}
const dispWords = t => String(t).split(/[^\p{L}\p{N}]+/u).filter(Boolean).join(' ');
let mk = 0, mkStones = new Set(), brLines = 0;
for (const s of stones) for (const r of [s, ...(s._also || [])]){
  if (!r || !r.i || !MARKUP.test(r.i)) continue;
  const t = D.inscDisplay(r.i);
  if (t === r.i) continue;
  mk++; mkStones.add(s.id);
  assert(!LEFT.test(t), `${s.id}: queda marcado en «${t.slice(0, 80)}»`);
  assert(dispWords(t) === refWords(r.i), `${s.id}: palabras distintas tras limpiar:\n  ${dispWords(t)}\n  ${refWords(r.i)}`);
  if (/<br/i.test(r.i)) { assert(t.split('\n').length === r.i.split(/<br\s*\/?>/i).filter(x => x.trim()).length, `${s.id}: <br> no es salto de línea`); brLines++; }
  if (r === s){
    const L2 = P.linesFor(s, 'full');
    assert(L2 && !L2.some(l => LEFT.test(l)), `${s.id}: la placa pintaría marcado`);
  }
}
assert(mk >= 40, `solo ${mk} inscripciones con marcado (se esperaban >= 40)`);
// casos fijos
const EX = [["Hier wohnte<br />'''Walter Rosenbaum'''<br />Jg. 1908", 'Hier wohnte\nWalter Rosenbaum\nJg. 1908'],
  ['Schillerstraße 29<b>Else Hirschberg<b>1892-1942', 'Schillerstraße 29\nElse Hirschberg\n1892-1942'],
  ['Dr. [[Alfred Meyer (Zahnmediziner)|Alfred Meyer]] Jg. 1898', 'Dr. Alfred Meyer Jg. 1898'],
  ['HERTHA &#8218;BETHEL&#8216; FRANK', 'HERTHA ‚BETHEL‘ FRANK'], ['a<br>b<br/>c<BR />d', 'a\nb\nc\nd'],
  ['<b>Anna</b> Kahn&nbsp;Jg.', 'Anna Kahn Jg.'], ["1944'Wehrkraftzersetzung''Beleidigung'", "1944'Wehrkraftzersetzung''Beleidigung'"],
  ['Jg. 1885|<haft 11.11.1938', 'Jg. 1885|<haft 11.11.1938'], ['interniert [[Durchgangslager Westerbork|Westerbork]] deportiert', 'interniert Westerbork deportiert'],
  ['Im Widerstand [[Naturfreunde]]', 'Im Widerstand Naturfreunde']];
for (const [a, b] of EX) assert(D.inscDisplay(a) === b, `inscDisplay(${JSON.stringify(a)}) = ${JSON.stringify(D.inscDisplay(a))} ≠ ${JSON.stringify(b)}`);
const cr = P.contrast(P.INK, P.FACE);
assert(cr >= 4.5, `contraste ${cr.toFixed(2)} < 4,5`);
assert(P.contrast('#000000', '#ffffff') > 20.9 && Math.abs(P.contrast('#777777', '#ffffff') - 4.48) < 0.02, 'fórmula de contraste');
assert(P.Z_ON === 20 && P.Z_NAME === 20.5 && P.Z_FULL === 21.5, 'umbrales de zoom');
console.log(`OK plaque-text (unidad): ${stones.length} placas, ${withI} con inscripción (texto = ficha en mayúsculas, ${full}), ${stones.length - withI} en blanco; línea del nombre literal en ${named} (sin línea de nombre: ${noName}); ajuste sin perder palabras (no caben ni a la letra mínima y quedan lisas: ${overflow}); marcado HTML/wiki limpio en ${mk} inscripciones de ${mkStones.size} placas (${brLines} con <br>), sin perder palabras; contraste letras/cara ${cr.toFixed(2)}:1`);
