// v19: Jersey 20, Finlandia 7 y Rumanía 2 añadidas (19-11-2026): datos completos, base de 65832 intacta, sin duplicados, cada exclusión con su motivo.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.join(__dirname, '..');
function assert(c, m) { if (!c) throw new Error('FAIL: ' + m); }
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/stones.json'), 'utf8'));
const M = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/v19-added-20261119.json'), 'utf8'));
const S = D.stones, base = M.meta.previous_records;
assert(base === 65832 && S.length === base + 29 && S.length === D.meta.count, 'base 65832 + 29 = ' + S.length);
const added = S.slice(base), old = S.slice(0, base);
assert(D.meta.v19_added.records === 29 && D.meta.v19_added.countries.JE === 20 && D.meta.v19_added.countries.FI === 7 && D.meta.v19_added.countries.RO === 2, 'meta.v19_added');
const strip = s => { const { dla, dlo, ...r } = s; return r; };      // v19: dla/dlo (posición de dibujo) pueden añadirse a IE/SE; lo demás no cambia
const h = crypto.createHash('sha256').update(JSON.stringify(old.map(strip))).digest('hex');
assert(h === M.meta.previous_sha256_json_list, 'base intacta (sha256, sin dla/dlo) ' + h);
const cnt = cc => added.filter(s => s.cc === cc).length;
assert(cnt('JE') === 20 && cnt('FI') === 7 && cnt('RO') === 2, 'JE 20, FI 7, RO 2');
assert(old.filter(s => (s.cc || 'DE') === 'DE').length === 65820 && old.filter(s => s.cc === 'IE').length === 6 && old.filter(s => s.cc === 'SE').length === 6, 'DE 65820, IE 6, SE 6 intactos');
const ids = new Set(old.map(s => s.id));
added.forEach((s, i) => {
  assert(!ids.has(s.id), 'id nuevo ' + s.id); ids.add(s.id);
  assert(s.id === M.added[i].id && s.n === M.added[i].n, 'manifiesto alineado ' + s.id);
  assert(s.n && typeof s.la === 'number' && typeof s.lo === 'number', 'nombre y coordenadas ' + s.id);
  assert(s.i || s.a, 'inscripción o dirección ' + s.id);
  assert(s.c, 'ciudad/parroquia ' + s.id);
  assert(/^n\d+$/.test(s.id) || (s.src === 'wd' && s.id === s.wd), 'id OSM o Qid de la piedra ' + s.id);
  assert(!s.img || !s.img.startsWith('File:'), 'img sin prefijo File: ' + s.id);
  if (s.cc === 'JE') { assert(s.la > 49.1 && s.la < 49.3 && s.lo > -2.3 && s.lo < -2.0 && s.src === 'osm' && /^HERE LIVED|^AT 13 ROYAL/.test(s.i) && s.laid && s.b, 'Jersey ' + s.id); assert(/^\d{4}$/.test(s.b) && s.i.includes('BORN') && s.i.includes(s.b), 'Jersey: año de nacimiento = placa ' + s.id); }
  if (s.cc === 'FI') { assert(s.c === 'Helsinki' && s.sub && s.src === 'osm+wd' && /^Q\d+$/.test(s.wd) && /^Tässä asui/.test(s.i), 'Finlandia ' + s.id); assert(!s.a, 'Finlandia: OSM/Wikidata no traen dirección; no se inventa'); }
  if (s.cc === 'RO') { assert(s.src === 'wd' && s.id === s.wd && /^Q\d+$/.test(s.wd), 'Rumanía solo Wikidata ' + s.id); }
});
assert(added.filter(s => s.cc === 'JE').every(s => !s.wd), 'Jersey: ninguna piedra con ítem de Wikidata (no se inventa)');
const by = Object.fromEntries(added.map(s => [s.n, s]));
assert(by['Miriam Zeiger Mozes'].p === 'Q37819936' && /supravietuit/.test(by['Miriam Zeiger Mozes'].i) && by['Miriam Zeiger Mozes'].c === 'Marca', 'Rumanía: Miriam');
assert(by['Bloch Lorand'].a === 'Piața Romanilor 8' && by['Bloch Lorand'].c === 'Timișoara' && !by['Bloch Lorand'].i, 'Rumanía: Bloch Lorand (dirección de Wikidata, sin inscripción)');
assert(by['Janka Kollmann'].wp === 'fi:Georg ja Janka Kollmann', 'Janka: fi.wikipedia de OSM');
assert(by["Lucy Renee Schwob 'Claude Cahun'"].p === 'Q219634', 'Cahun p');
// exclusiones
const ex = Object.fromEntries(M.excluded.map(e => [e.id, e]));
assert(M.excluded.length === 2 && ex.n919561807 && ex.Q44068923, 'excluidas: n919561807 (FI) y Q44068923 (RO)');
M.excluded.forEach(e => { assert(e.reason, 'motivo ' + e.id); assert(!added.some(s => s.id === e.id), 'excluida ausente ' + e.id); });
console.log('OK jefiro-added: Jersey 20, Finlandia 7, Rumanía 2; base 65832 intacta; 2 exclusiones con motivo');
