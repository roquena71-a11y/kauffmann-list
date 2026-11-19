// Piedras de Irlanda añadidas (19-11-2026): 6 completas en Dublín, base alemana intacta, sin duplicados.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.join(__dirname, '..');
function assert(c, m) { if (!c) throw new Error('FAIL: ' + m); }
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/stones.json'), 'utf8'));
const M = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/ie-added-20261119.json'), 'utf8'));
const V14 = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/wd-added-20261118.json'), 'utf8'));
const S = D.stones;
assert(S.length === D.meta.count, 'meta.count = número de registros');
assert(D.meta.ireland_added && D.meta.ireland_added.records === 6, 'meta.ireland_added.records = 6');
const base = V14.meta.base_records + V14.added.length;
const added = S.slice(base, base + 6);
const old = S.slice(0, base);
assert(old.length === 65820, 'la base alemana (v14) sigue en 65820: ' + old.length);
assert(added.length === 6 && added.length === M.added.length, '6 registros de Irlanda');
added.forEach((s, i) => {
  assert(s.cc === 'IE', 'cc=IE ' + s.id);
  assert(s.c === 'Dublin', 'municipio Dublin ' + s.id);
  assert(s.src === 'osm+wd', 'fuente osm+wd ' + s.id);
  assert(/^n\d+$/.test(s.id), 'id de nodo OSM ' + s.id);
  assert(s.wd && /^Q\d+$/.test(s.wd), 'wd de la piedra ' + s.id);
  assert(s.n && s.n.trim(), 'nombre ' + s.id);
  assert(s.a === 'Donore Avenue 8', 'dirección OSM ' + s.id);
  assert(typeof s.la === 'number' && typeof s.lo === 'number', 'coordenadas ' + s.id);
  assert(s.la > 53.3 && s.la < 53.4 && s.lo < -6.2 && s.lo > -6.4, 'coords en Dublín ' + s.id);
  assert(s.i && s.i.length > 10, 'inscripción ' + s.id);
  assert(s.img && !s.img.startsWith('File:'), 'foto Commons sin prefijo File: ' + s.id);
  assert(s.id === M.added[i].id && s.n === M.added[i].n, 'manifiesto alineado ' + s.id);
});
const ids = new Set(added.map(s => s.id));
assert(ids.size === 6, 'ids únicos');
assert(!ids.has('n12723562419'), 'el nodo incompleto de Cork no está en el mapa');
M.excluded.forEach(e => assert(!ids.has(e.id), 'excluido ausente: ' + e.id));
// No se duplica un ítem de Wikidata ni un nodo.
const wds = added.map(s => s.wd);
assert(new Set(wds).size === 6, 'Qids de piedra únicos');
const oldIds = new Set(old.map(s => s.id));
added.forEach(s => assert(!oldIds.has(s.id), 'id nuevo ' + s.id));
// Distintos nombres en la misma dirección: no son duplicados.
const names = new Set(added.map(s => s.n));
assert(names.size === 6, '6 personas distintas');
// Ettie tiene Qid de persona (subject:wikidata); las demás no inventan p.
const ettie = added.find(s => s.id === 'n13067653180');
assert(ettie.p === 'Q56036390', 'Ettie Gluck subject:wikidata');
added.filter(s => s.id !== 'n13067653180').forEach(s => assert(!s.p, 'sin p inventado ' + s.id));
console.log('OK ie-added: 6 placas en Dublin, IE, osm+wd, base de 65820 intacta, excluido n12723562419');
