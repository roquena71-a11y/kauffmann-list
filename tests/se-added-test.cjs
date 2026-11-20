// Piedras de Suecia añadidas (19-11-2026): 6 completas (Malmö 3, Estocolmo 3), base anterior intacta, sin duplicados.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.join(__dirname, '..');
function assert(c, m) { if (!c) throw new Error('FAIL: ' + m); }
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/stones.json'), 'utf8'));
const M = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/se-added-20261119.json'), 'utf8'));
const S = D.stones;
assert(S.length === D.meta.count, 'meta.count = número de registros');
assert(D.meta.sweden_added && D.meta.sweden_added.records === 6, 'meta.sweden_added.records = 6');
const base = M.meta.previous_records;
assert(base === 65826, 'base anterior 65826 (Alemania 65820 + Irlanda 6)');
const added = S.slice(base, base + 6), old = S.slice(0, base);
const strip = s => { const { dla, dlo, ...r } = s; if (['LU', 'AT', 'PL', 'CH'].includes(r.cc)) delete r.cc; return r; };   // v20: dla/dlo (posición de dibujo) y cc de los 15 registros alemanes reasignados a LU/AT/PL/CH (fuera de Alemania) no cuentan como cambio de la base

assert(S.length >= base + 6 + 29, 'al menos 65861 (v19 añadió 29 más): ' + S.length);
assert(added.length === 6 && added.length === M.added.length, '6 registros de Suecia');
// La base (Alemania + Irlanda) no cambió ni un byte.
const h = crypto.createHash('sha256').update(JSON.stringify(old.map(strip))).digest('hex');
assert(h === M.meta.previous_sha256_json_list, 'base intacta (sha256) ' + h);
assert(old.map(strip).filter(s => (s.cc || 'DE') === 'DE').length === 65820 && old.filter(s => s.cc === 'IE').length === 6, 'DE 65820 + IE 6');
const EXP = {
  n12212839191: ['Siegfried Gutmann', 'Skeppsbron', 'Malmö', '1885', '1943-03-20', 'osm'],
  n12212839192: ['Walter Gerson', 'Skeppsbron', 'Malmö', '1882', '1939-09-12', 'osm'],
  n12212839193: ['Schulim Bürger', 'Skeppsbron', 'Malmö', '1887', undefined, 'osm'],
  n12228264289: ['Hans Eduard Szybilski', 'Apelbergsgatan 36', 'Stockholm', '1907', undefined, 'osm+wd'],
  n12247227671: ['Erich Holewa', 'Kungsholmstorg 6', 'Stockholm', '1896', undefined, 'osm+wd'],
  n12247228901: ['Curt Moses', 'Gumshornsgatan 6', 'Stockholm', '1886', undefined, 'osm+wd'],
};
added.forEach((s, i) => {
  const e = EXP[s.id]; assert(e, 'id esperado ' + s.id);
  assert(s.cc === 'SE', 'cc=SE ' + s.id);
  assert(s.n === e[0] && s.a === e[1] && s.c === e[2] && s.b === e[3] && s.d === e[4] && s.src === e[5], 'campos ' + s.id);
  assert(/^n\d+$/.test(s.id), 'id de nodo OSM ' + s.id);
  assert(s.i && /F[ÖO]DD \d{4}/.test(s.i) && s.i.toUpperCase().includes(s.n.toUpperCase().replace('Ü', 'Ü')), 'inscripción con el nombre ' + s.id);
  assert(typeof s.la === 'number' && typeof s.lo === 'number', 'coordenadas ' + s.id);
  if (s.c === 'Malmö') assert(s.la > 55.5 && s.la < 55.7 && s.lo > 12.9 && s.lo < 13.1, 'coords en Malmö ' + s.id);
  else assert(s.la > 59.2 && s.la < 59.4 && s.lo > 17.9 && s.lo < 18.2, 'coords en Estocolmo ' + s.id);
  assert(s.id === M.added[i].id && s.n === M.added[i].n, 'manifiesto alineado ' + s.id);
  // Malmö: el «wikidata» de OSM es el artículo-lista de la Wikipedia, no una piedra: no se guarda como wd.
  if (s.c === 'Malmö') { assert(!s.wd && !s.p && !s.img, 'Malmö sin wd/p/img inventados ' + s.id); }
  else { assert(/^Q\d+$/.test(s.wd) && /^Q\d+$/.test(s.p) && s.img && !s.img.startsWith('File:'), 'Estocolmo wd, p, img ' + s.id); }
  assert(!s.wd || s.wd !== 'Q65088606', 'Q65088606 (lista) no es una piedra');
});
assert(new Set(added.map(s => s.id)).size === 6, 'ids únicos');
assert(new Set(added.map(s => s.n)).size === 6, '6 personas distintas');
assert(new Set(added.filter(s => s.wd).map(s => s.wd)).size === 3, '3 Qids de piedra únicos');
const oldIds = new Set(old.map(s => s.id));
added.forEach(s => assert(!oldIds.has(s.id), 'id nuevo ' + s.id));
assert(!added.some(s => s.id === 'n13892986434'), 'el nodo sin nombre (Nykvarn) no está en el mapa');
M.excluded.forEach(e => assert(!added.some(s => s.id === e.id), 'excluido ausente: ' + e.id));
assert(M.excluded.length === 1 && M.excluded[0].id === 'n13892986434', 'excluido: n13892986434');
assert(added.find(s => s.id === 'n12247227671').wp === 'sv:Erich Holewa', 'Holewa: enlace a sv.wikipedia (sitelink de Wikidata Q80913948)');
assert(added.find(s => s.id === 'n12228264289').laid === '2019-06-14', 'Szybilski colocada 2019-06-14 (OSM start_date)');
assert(added.filter(s => s.laid).length === 1, 'laid solo donde no hay conflicto de fuentes');
console.log('OK se-added: 6 placas (Malmö 3, Estocolmo 3), SE, base de 65826 intacta, excluido n13892986434');
