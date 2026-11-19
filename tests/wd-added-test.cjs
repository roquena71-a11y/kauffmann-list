// Piedras de Wikidata añadidas (18-11-2026): cuenta, Qid, coordenadas, municipio, sin duplicados, base intacta.
// v14: regla permanente — mismo nombre normalizado a <=100 m de un registro anterior = duplicado; pares débiles revisados a mano; municipio, no barrio.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.join(__dirname, '..');
function assert(c, m) { if (!c) throw new Error('FAIL: ' + m); }
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/stones.json'), 'utf8'));
const M = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/wd-added-20261118.json'), 'utf8'));
const S = D.stones, base = M.meta.base_records;
assert(S.length === D.meta.count, 'meta.count = número de registros');
const added = S.slice(base, base + M.added.length), old = S.slice(0, base);
assert(added.length === M.added.length && added.length === D.meta.wikidata_added.records, 'cuenta: ' + added.length + ' = manifiesto = meta');
assert(added.length > 0, 'hay registros añadidos');
// La base no cambió ni un byte.
const sha = crypto.createHash('sha256').update(JSON.stringify(old)).digest('hex');
assert(sha === M.meta.base_sha256, 'los ' + base + ' registros anteriores no cambian');
// Qid, enlace a la fuente, forma del registro.
const ids = new Set(), ps = new Set(), seen = new Map();
const oldIds = new Set(old.flatMap(s => [s.id, s.wd].filter(Boolean))), oldP = new Set(old.map(s => s.p).filter(Boolean));
const fold = t => String(t || '').toLowerCase().replace(/ß/g, 'ss').replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
const nkey = n => fold(n).replace(/\b(dr|prof|med|jur|phil|rer|nat)\b/g, ' ').split(/\b(geb|geboren|nee|verh|verw|gesch)\b/)[0].replace(/\bjg\b.*$/, '').replace(/\s+/g, ' ').trim();
const hav = (a, b, c, d) => { const R = 6371008.8, p = Math.PI / 180, x = Math.sin((c - a) * p / 2) ** 2 + Math.cos(a * p) * Math.cos(c * p) * Math.sin((d - b) * p / 2) ** 2; return 2 * R * Math.asin(Math.sqrt(x)); };
const oldByName = new Map();
old.forEach(s => { const k = nkey(s.n); if (k && typeof s.la === 'number') { if (!oldByName.has(k)) oldByName.set(k, []); oldByName.get(k).push(s); } });
// Regla permanente: devuelve el registro anterior con el mismo nombre normalizado a <=100 m (o null).
function nearSameName(r) { const k = nkey(r.n); if (!k) return null; for (const o of oldByName.get(k) || []) if (hav(r.la, r.lo, o.la, o.lo) <= 100) return o; return null; }
// ---- Ronda 2: reglas R1-R5 contra la base y entre las añadidas (espejo de work/dup_rules.py) ----
const EQ = [['heinz','heinrich','henri'],['else','elsa','elisabeth','elise','elsbeth'],['hans','johannes','johann'],['fritz','friedrich','fred'],['willi','willy','wilhelm','wilhelmine'],['lotte','charlotte','lotti'],['jenny','jenni','johanna','jeanette'],['hanna','hannah','anna','anne','annchen'],['mira','maria','miriam'],['sofie','sophie','sophia'],['klara','clara'],['karl','carl'],['kurt','curt','konrad'],['luise','louise','lisa','louisa'],['benni','benny','benno','benjamin'],['jakob','jacob'],['moritz','maurice'],['ernst','ernest'],['martha','marta'],['emil','emile'],['siegfried','sigfried'],['bertha','berta'],['herta','hertha']];
const eqc = t => { const g = EQ.find(x => x.includes(t)); return g ? g.slice().sort()[0] : t; };
const toks = n => nkey(n).split(' ').filter(t => t.length > 1);
const iwords = s => fold(s).replace(/\b(hier|wohnte|wirkte|lernte|arbeitete|lebte|jg|jahrgang|geb|deportiert|ermordet|stolperstein|flucht|in|und|dr)\b/g, ' ').split(' ').filter(w => w.length > 1);
const jacc = (a, b) => { const x = new Set(iwords(a)), y = new Set(iwords(b)); const u = new Set([...x, ...y]); if (u.size < 4) return 0; let n = 0; x.forEach(w => { if (y.has(w)) n++; }); return n / u.size; };
const imgkey = f => String(f || '').replace(/_/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
const streetKey = a => { const m = /^\s*([^,\d]*[^,\d\s])\s+(\d+\s*[a-zA-Z]?)\b/.exec(a || ''); return m ? [fold(m[1]), fold(m[2]).replace(/ /g, '')] : null; };
const esc = t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
function rules(c, o, d) {
  const out = [], kc = nkey(c.n), ko = nkey(o.n);
  if (d <= 100 && kc && kc === ko) out.push('R1 mismo nombre normalizado');
  if (d <= 30 && !o.n && !o.i && o.img && !Array.isArray(o.img)) { const sk = streetKey(c.a); if (sk && new RegExp('\\b' + esc(sk[0]) + '\\b\\D{0,12}\\b' + esc(sk[1]) + '\\b').test(fold(o.img))) out.push('R2 nodo OSM sin nombre con foto «' + o.img + '»'); }
  if (d <= 100) {
    const tk = toks(c.n);
    if (tk.length >= 2 && kc !== ko) { const hay = new Set(fold((o.n || '') + ' ' + (o.i || '')).split(' ')); if (tk.every(t => hay.has(t))) out.push('R3 nombre completo en «' + (o.n || '') + '» / su inscripción'); }
    if (c.i && o.i && jacc(c.i, o.i) >= 0.95) out.push('R4 misma inscripción');
    const ci = new Set((c.img || []).map(imgkey)), oi = (Array.isArray(o.img) ? o.img : o.img ? [o.img] : []).map(imgkey), to = toks(o.n);
    oi.filter(f => ci.has(f)).forEach(f => { const ff = new Set(fold(f).split(' ')); if ((tk.length >= 2 && tk.every(t => ff.has(t))) || (to.length >= 2 && to.every(t => ff.has(t)))) out.push('R4 mismo archivo de foto de la persona'); });
    if (tk.length >= 2 && to.length >= 2 && kc !== ko && tk[tk.length - 1] === to[to.length - 1] && eqc(tk[0]) === eqc(to[0])) out.push('R5 mismo apellido y nombre de pila equivalente');
  }
  return out;
}
const grid = new Map(), gk = (la, lo) => Math.floor(la * 100) + ',' + Math.floor(lo * 100);
S.forEach(s => { if (typeof s.la === 'number') { const k = gk(s.la, s.lo); if (!grid.has(k)) grid.set(k, []); grid.get(k).push(s); } });
function nearby(r, rad) { const out = [], a = Math.floor(r.la * 100), b = Math.floor(r.lo * 100); for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) for (const o of grid.get((a + i) + ',' + (b + j)) || []) { const d = hav(r.la, r.lo, o.la, o.lo); if (d <= rad) out.push([o, d]); } return out; }
const PR = new Set((M.pares_revisados_distintos || []).map(p => [p[0], p[1]].sort().join('|')));
const WR0 = M.weak_reviewed || {};
let pairsReviewed = 0;
function ruleHits(r, img) {
  const c = Object.assign({}, r, { img }), bad = [];
  nearby(r, 100).forEach(([o, d]) => {
    if (o.id === r.id) return;
    const isAdded = o.id.startsWith('Q') && o.src === 'wd' && S.indexOf(o) >= base;
    const oo = isAdded ? Object.assign({}, o, { img: (M.added.find(m => m.q === o.id) || {}).img || [] }) : o;
    const rs = rules(c, oo, d);
    if (!rs.length) return;
    if (PR.has([r.id, o.id].sort().join('|'))) { pairsReviewed++; return; }
    if (WR0[r.id] && WR0[r.id].a === 'mantener' && !isAdded) return;
    bad.push(o.id + ' (' + Math.round(d) + ' m): ' + rs.join(', '));
  });
  return bad;
}
const oldNA = new Set(old.filter(s => s.n && s.a).map(s => fold(s.n.replace(/\s+geb\..*$/i, '')) + '|' + fold(s.a)));
// Una placa añadida debe recordar a una persona: P547 de Wikidata apunta a un humano (m.persona === 'P547', y entonces trae `p`), o el nombre/inscripción no tiene patrón de edificio, empresa o memorial.
const NONPERSON_NAME = /\b(kopfstein|synagoge|fabrik|denkmal|mahnmal|gedenk\w*|museum|schule|kirche|stiftung|weberei|rathaus|bahnhof|krankenhaus|friedhof|kaufhaus)\b/i;
const NONPERSON_INSC = /^\s*hier (stand|befand)|\b(gegründet von|erbaut \d{4}|abgerissen \d{4})\b/i;
function pareceNoPersona(n, i) { return NONPERSON_NAME.test(n || '') || (NONPERSON_INSC.test(i || '') && !/\bjg\b/i.test(i || '')); }
const BBOX = { la: [47.2, 55.1], lo: [5.8, 15.1] };
let geo = 0, p625 = 0, inMuni = 0;
added.forEach((s, i) => {
  const m = M.added[i];
  assert(m.q === s.id, 'orden manifiesto = orden registros ' + s.id);
  assert(/^Q\d+$/.test(s.id) && s.wd === s.id && s.src === 'wd', 'Qid propio y src=wd: ' + s.id);
  assert(!ids.has(s.id) && !oldIds.has(s.id), 'Qid no repetido: ' + s.id); ids.add(s.id);
  assert(typeof s.la === 'number' && typeof s.lo === 'number', 'tiene coordenadas ' + s.id);
  assert(s.la > BBOX.la[0] && s.la < BBOX.la[1] && s.lo > BBOX.lo[0] && s.lo < BBOX.lo[1], 'dentro de Alemania ' + s.id);
  assert(s.i || s.n, 'tiene inscripción o nombre ' + s.id);
  if (s.p) {
    assert(/^Q\d+$/.test(s.p), 'p válido ' + s.id);
    assert(!ps.has(s.p), 'persona no repetida entre las añadidas ' + s.p); ps.add(s.p);
    if (oldP.has(s.p)) {   // misma persona con otra piedra en otro lugar: solo si está verificada en el manifiesto
      const other = M.same_person_other_stone && M.same_person_other_stone[s.id];
      assert(other, 'persona ya en el mapa y no verificada como otra piedra: ' + s.id + ' ' + s.p);
      old.filter(o => o.p === s.p).forEach(o => assert(typeof o.la !== 'number' || hav(s.la, s.lo, o.la, o.lo) > 1000, 'otra piedra de la misma persona a >1 km: ' + s.id));
    }
  }
  const nn = nearSameName(s); assert(!nn, 'DUPLICADO: mismo nombre a <=100 m de ' + (nn && nn.id) + ': ' + s.id);
  assert(m.persona === 'P547' || m.persona === 'nombre', 'comprobación de persona en el manifiesto: ' + s.id);
  if (m.persona === 'P547') assert(s.p, 'P547 humano => trae persona (p): ' + s.id); else assert(!pareceNoPersona(s.n, s.i), 'NO ES UNA PLACA DE PERSONA (edificio/empresa/memorial): ' + s.id + ' ' + s.n);
  const rh = ruleHits(s, m.img || []); assert(!rh.length, 'DUPLICADO por regla R1-R5 sin revisar: ' + s.id + ' ' + s.n + ' ↔ ' + rh.join('; '));
  assert(m.muni && s.c === m.muni, 'municipio = ciudad de la cadena P131 (no barrio): ' + s.id + ' «' + s.c + '» vs «' + m.muni + '»');
  assert(!/^(Sulzbürg|Steinhude|Westerland)$/.test(s.c || ''), 'municipio, no pueblo/barrio: ' + s.id + ' ' + s.c);
  assert(!/^(Altstadt|Biebrich|Nordost|Obergiesing|Rheingauviertel)$/.test(s.c || ''), 'municipio, no barrio: ' + s.id + ' ' + s.c);
  assert(!s.sub || s.sub !== s.c, 'sub distinto del municipio ' + s.id);
  if (s.n && s.a) { const k = fold(s.n.replace(/\s+geb\..*$/i, '')) + '|' + fold(s.a); assert(!oldNA.has(k), 'mismo nombre+dirección que un registro anterior: ' + s.id); assert(!seen.has(k), 'mismo nombre+dirección repetido: ' + s.id + ' ' + seen.get(k)); seen.set(k, s.id); }
  if (s.gm) {
    geo++;
    assert(s.gm === 'geocoded:nominatim:house' && m.method === s.gm, 'método de geocodificación ' + s.id);
    assert(s.gc === 'high' || s.gc === 'medium', 'confianza ' + s.id);
    assert(/^(node|way|relation)\/\d+$/.test(s.go) && s.go === m.osm, 'objeto OSM ' + s.id);
    assert(s.a && /\d/.test(s.a), 'dirección con número ' + s.id);
  } else { p625++; assert(m.method === 'wikidata:P625', 'sin gm = coordenadas de Wikidata ' + s.id); }
  const bb = m.admin && M.bbox_municipios[m.admin];
  if (bb) { const t = 0.002; assert(s.la >= bb[0] - t && s.la <= bb[1] + t && s.lo >= bb[2] - t && s.lo <= bb[3] + t, 'dentro del municipio (bbox) ' + s.id + ' ' + m.admin); inMuni++; }
});
assert(geo + p625 === added.length, 'geo + P625 = total');
// La regla detecta de verdad: un registro anterior copiado a 10 m debe marcarse; a 300 m no.
{ const o = old.find(x => x.n && typeof x.la === 'number'); const t = { n: o.n, la: o.la + 0.00009, lo: o.lo }; assert(nearSameName(t), 'la regla de proximidad detecta un duplicado a 10 m'); assert(!nearSameName({ n: o.n, la: o.la + 0.003, lo: o.lo }) || hav(o.la + 0.003, o.lo, o.la, o.lo) <= 100, 'a 300 m no es duplicado por esta regla'); }
// Autopruebas de las reglas nuevas (mutaciones): cada una debe detectarse.
{
  const o = old.find(x => x.n && x.i && typeof x.la === 'number' && toks(x.n).length >= 2);
  const base0 = { id: 'QX', la: o.la + 0.00005, lo: o.lo };
  assert(rules(Object.assign({}, base0, { n: o.n, i: '' }), o, 5).length, 'R1 autoprueba');
  const o2 = { id: 'o2', n: '', i: '', img: 'Stolpersteinlage, 1, Am Erlenberg 30, Bessungen, Darmstadt.jpg' };
  assert(rules({ n: 'Eugenie Sölling', a: 'Am Erlenberg 30, Darmstadt' }, o2, 7).some(x => x.startsWith('R2')), 'R2 autoprueba: nodo sin nombre con foto de la dirección');
  assert(!rules({ n: 'Eugenie Sölling', a: 'Am Erlenberg 30, Darmstadt' }, o2, 60).length, 'R2 solo a <=30 m');
  assert(rules({ n: 'Ludwig Marx', a: '' }, { id: 'c', n: '', i: 'Edith Marx, Paula Marx, Ludwig Marx' }, 14).some(x => x.startsWith('R3')), 'R3 autoprueba: nodo colectivo');
  assert(rules({ n: 'Maria Anna Marx', i: 'HIER WOHNTE MIRA MARX JG. 1894 DEPORTIERT 1942 KRASNICZYN ERMORDET' }, { id: 'c', n: 'Mira Marx', i: 'HIER WOHNTE \nMIRA MARX \nJG. 1894 \nDEPORTIERT 1942 \nKRASNICZYN \nERMORDET' }, 2).some(x => x.startsWith('R4')), 'R4 autoprueba: misma inscripción');
  assert(rules({ n: 'Rudolf Levy', img: ['Stolperstein für Rudolf Levy (Frankfurt).jpg'] }, { id: 'c', n: 'Rudolf Levi', img: 'Stolperstein für Rudolf Levy (Frankfurt).jpg' }, 3).some(x => x.startsWith('R4')), 'R4 autoprueba: misma foto');
  assert(rules({ n: 'Heinz Bollinger' }, { id: 'c', n: 'Heinrich Philipp Bollinger' }, 14).some(x => x.startsWith('R5')), 'R5 autoprueba: Heinz/Heinrich');
  assert(!rules({ n: 'Karl Weil' }, { id: 'c', n: 'Hans Weil' }, 3).length, 'apellido igual y nombre distinto no es duplicado');
}
// Autopruebas de la comprobación de persona.
assert(pareceNoPersona('Kopfstein Alte Weberei', 'Alte Weberei / Mai 1944 bis April 1945 / Außenlager des KZ Dachau') && pareceNoPersona('Synagoge in Müllheim', 'HIER STAND DIE SYNAGOGE ERBAUT 1852') && pareceNoPersona('Seifenfabrik J. Chr. Höffler', 'SEIFENFABRIK J. CHR. HÖFFLER GEGRÜNDET VON MARIUS LANG 1873') && !pareceNoPersona('Albert  Platz', 'ALBERT PLATZ, JG. 1879, DEPORTIERT 1940') && !pareceNoPersona('Luise Nauhaus', ''), 'autoprueba: patrón de no-persona');
['Q137783248', 'Q138302073', 'Q134778243'].forEach(q => assert(!new Set(added.map(x => x.id)).has(q), 'no es placa de persona: pendiente, no en el mapa ' + q));
// Revisión manual de pares débiles y retenidos: excluidos/pendientes no están; los «mantener» sí.
const addedIds = new Set(added.map(s => s.id)), WR = M.weak_reviewed || {};
Object.keys(WR).forEach(q => { if (WR[q].a === 'mantener') assert(addedIds.has(q), 'revisado y mantenido: ' + q); else assert(!addedIds.has(q), 'revisado y ' + WR[q].a + ' no puede estar en el mapa: ' + q); });
assert(!addedIds.has('Q134878064') && !addedIds.has('Q132150902'), 'retenidos para revisión manual no están en el mapa');
assert(Object.keys(WR).length >= 50, 'tabla de revisión manual presente');
assert(!addedIds.has('Q134727262') && !addedIds.has('Q134931383') && !addedIds.has('Q134877682') && !addedIds.has('Q44200657') && addedIds.has('Q134877930'), 'ronda 2: duplicados retirados, Kurt Lion (Q134877930) se conserva');
['Q135899648','Q135899650','Q135899663','Q135234573','Q141639086','Q131924989','Q131924985','Q131924986','Q141572606'].forEach(q => assert(!addedIds.has(q), 'ronda 2: en pendientes, no en el mapa: ' + q));
assert(addedIds.has('Q134875359'), 'ronda 2: Q134875359 (Moltkestraße 20) recuperada');
const sp = M.same_person_other_stone || {}; Object.keys(sp).forEach(q => assert(addedIds.has(q), 'misma persona, otra piedra: añadida ' + q));
assert(!/^\s*$/.test(D.meta.wikidata_added.method), 'meta.wd_added.method');
console.log('OK wd-added: ' + pairsReviewed + ' coincidencias de reglas R1-R5 resueltas por revisión manual; ' + added.length + ' registros nuevos (' + p625 + ' con coordenadas de Wikidata, ' + geo + ' geocodificados a nivel de casa); todos con Qid, todos placas de persona (P547 humano o nombre sin patrón de edificio/empresa), en Alemania, ' + inMuni + ' comprobados contra el bbox de su municipio, sin duplicados (nombre+dirección y nombre a <=100 m), base de ' + base + ' intacta');
