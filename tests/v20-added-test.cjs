// v20: países añadidos (OSM ODbL + Wikidata CC0): cuentas por país = manifiesto = stones.json, base v19 intacta, ids únicos, sin duplicados, cada exclusión con motivo.
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
function assert(c, m) { if (!c) throw new Error('FAIL: ' + m); }
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/stones.json'), 'utf8'));
const M = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/v20-added-20261120.json'), 'utf8'));
const S = D.stones, prev = M.meta.previous_records;
assert(S.length === D.meta.count && D.meta.layout_pinned === true, 'meta.count y layout_pinned');
assert(prev === 65861, 'base v19 = 65861');
const ids = new Set(S.map(s => s.id)); assert(ids.size === S.length, 'ids únicos');
const wds = S.map(s => s.wd).filter(Boolean); assert(new Set(wds).size === wds.length, 'Qid únicos');
const byAdded = {}; M.added.forEach(a => { byAdded[a.cc] = (byAdded[a.cc] || 0) + 1; });
for (const a of M.added) { const s = S.find(x => x.id === a.id); assert(s, 'registro en stones.json ' + a.id); assert(s.cc === a.cc, 'cc ' + a.id); assert(Math.abs(s.la - a.la) < 1e-9 && Math.abs(s.lo - a.lo) < 1e-9, 'coordenada de origen intacta ' + a.id); assert(s.n && s.n.length > 1, 'nombre ' + a.id); assert(/^(n|w|r)\d+$|^Q\d+$/.test(s.id), 'id de fuente abierta ' + a.id); }
for (const [cc, c] of Object.entries(M.meta.countries)) assert((byAdded[cc] || 0) === c.anadidas, 'cuenta ' + cc + ' ' + (byAdded[cc] || 0) + ' = ' + c.anadidas);
assert(M.added.length === M.meta.records, 'total = manifiesto');
assert(M.excluded.every(e => e.id && e.cc && e.reason && e.reason.length >= 3), 'cada exclusión con motivo');
assert(D.meta.v20_wd1480_added >= 25 && D.meta.v20_wd1480_added <= 32, 'de las 1.480 añadidas: ' + D.meta.v20_wd1480_added);
const wd32 = S.filter(s => s.gm === 'commons:coordinates'); assert(wd32.length === D.meta.v20_wd1480_added && wd32.every(s => s.wd && s.img), '32 con foto de Commons');
const ccs = new Set(S.map(s => s.cc || 'DE')); assert(ccs.size === 27, '27 países: ' + ccs.size);
console.log('OK v20-added: ' + M.added.length + ' placas en ' + Object.keys(byAdded).length + ' países, +' + wd32.length + ' de las 1.480, base v19 intacta, ids/Qid únicos, 27 países en total');
