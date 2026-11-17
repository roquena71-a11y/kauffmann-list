// Fusión de repetidos (solo para mostrar). Unidad + datos reales (data/stones.json).
const path = require('path');
const KL = require('../dedupe.js');
const { run } = require('./merge-harness.cjs');
function assert(c, m) { if (!c) { throw new Error('FAIL: ' + m); } }
const S = (o) => Object.assign({ la: 50, lo: 8, a: 'X 1' }, o);

// --- Reglas ---
assert(!KL.samePerson(S({id:'n1',n:'Alexander Freiwald',i:'Hier wohnte Alexander Freiwald Jg. 1871',src:'osm+wd',wd:'Q1'}), S({id:'n2',n:'Alexander Freiwald',i:'Hier wohnte Alexander Freiwald Jg. 1904',src:'osm+wd',wd:'Q2'})), 'different Jg. → two people');
assert(!KL.samePerson(S({id:'Q1',n:'Berthold Weinberg',i:'Hier wohnte Berthold Weinberg Jg. 1909'}), S({id:'Q2',n:'Berthold  Weinberg',i:'Hier wohnte Berthold Weinberg Jg. 1941'})), 'baby 1941 is not his father');
assert(!KL.samePerson(S({id:'n1',n:'Frieda Schönfeld geb. Herzberg',i:'Hier wohnte Frieda Schönfeld geb. Herzberg Jg. 1892'}), S({id:'n2',n:'Frieda Schönfeld geb. Hammerschlag',i:'Hier wohnte Frieda Schönfeld geb. Hammerschlag Jg. 1892'})), 'different geb. → two people');
assert(!KL.samePerson(S({id:'n1',n:'Jenny Wallach verh. Levi',i:'Jenny Wallach verh. Levi Jg. 1887'}), S({id:'n2',n:'Jenny Wallach verh. Süsskind',i:'Jenny Wallach verh. Süsskind Jg. 1887'})), 'different verh. → two people');
assert(KL.compare(S({id:'Q1',n:'Moses Delmonte',b:'1868-09-16',i:'Hier wohnte Moses Delmonte Jg. 1868'}), S({id:'Q2',n:'Moses Delmonte',b:'1868-09-16',i:'Hier wohnte Sara Delmonte geb. Delmonte Jg. 1860'})).same===false, 'bad name field (Sara) never merged');
assert(KL.compare(S({id:'n1',n:'Auguste Simson',i:'Hier wohnte Auguste Simson'}), S({id:'n2',n:'Auguste Simson',i:'Hier wohnte Wilhelm Simson'})).why==='badNameField', 'Wilhelm Simson not hidden');
assert(!KL.samePerson(S({id:'n1',n:'Nanni Kurzmann',b:'19.10.1879',i:'Nanni Kurzmann JG. 1879 Izbica'}), S({id:'n2',n:'Nanni Kurzmann',b:'25.10.1879',i:'Nanni Kurzmann JG. 1879 Krasniczyn'})), 'different birth dates → two');
assert(!KL.samePerson(S({id:'n1',n:'Josef Sanders',src:'osm'}), S({id:'n2',n:'Josef Sanders',src:'osm'})), 'no year, two OSM nodes → keep both');
assert(KL.samePerson(S({id:'n1',n:'Hans Muster',src:'osm',i:'Hier wohnte Hans Muster'}), S({id:'Q9',n:'Hans Muster',src:'wd',i:'Hier wohnte Hans Muster'})), 'no year, clear OSM+Wikidata pair, same name and text → merge');
assert(!KL.samePerson(S({id:'n1',n:'Hans Muster',src:'osm+wd',wd:'Q8'}), S({id:'Q9',n:'Hans Muster',src:'wd'})), 'no year, OSM points to another Q → keep both');
assert(KL.samePerson(S({id:'n1',n:'Ella Deutsch geb. Jessel',i:'Hier wohnte Ella Deutsch geb. Jessel Jg. 1877',src:'osm'}), S({id:'Q1',n:'Ella Deutsch',i:'Hier wohnte Ella Deutsch geb. Jessel Jg. 1877',src:'wd'})), 'one adds geb., same Jg. and text → merge');
assert(!KL.samePerson(S({id:'n1',n:'Klara Heine',i:'Hier wohnte Klara Heine Jg. 1898 Aktion T4',wd:'Q1'}), S({id:'Q2',n:'Klara Heine',i:'Hier wohnte Klara Heine Jg. 1898 ausgewiesen nach Polen',wd:'Q2'})), 'two inscriptions, two items → show both');
assert(KL.samePerson(S({id:'Q1',n:'Michael Frankenthal',p:'Q7',b:'1866-09-01',i:'Michael Frankenthal Jg. 1866 A'}), S({id:'Q2',n:'Michael Frankenthal',p:'Q7',b:'1866-09-01',i:'Michael Frankenthal Jg. 1866 A B'})), 'same Wikidata person (p) → same person');
assert(!KL.samePerson(S({id:'n1',n:'Martha Schürmann verh. Strauss',b:'1861',i:'Martha Schürmann verh. Strauss Jg. 1902'}), S({id:'Q1',n:'Martha Schürmann',i:'Martha Schürmann Jg. 1902'})), 'record whose own years conflict is never merged');
assert(!KL.samePerson(S({id:'n1',n:'Familie Frank'}), S({id:'n2',n:'Familie Frank'})), 'collective names never merged');

// --- Datos reales ---
const r = run();
const byId = r.byId;
const hidden24 = [
  ['n13290469138','Alexander Freiwald','1871'],['n1794209827','Alexander Freiwald','1904'],
  ['n1794209854','Karl Janson','1911'],['n1794209855','Karl Janson','1890'],
  ['Q134778440','Bertha Stern','1871'],['Q134778529','Bertha Stern','1904'],
  ['Q131310320','Berthold Weinberg','1909'],['Q131310330','Berthold Weinberg','1941'],
  ['n12844532250','Oskar Abeles','1922'],['n12844532252','Oskar Abeles','1900'],
  ['Q133257855','Johanna Marx','1881'],['Q133257953','Johanna Marx','1899'],
  ['n1794209842','Elise Freiwald','1875'],['n1794209843','Elise Freiwald','1899'],
  ['n9950943136','Cäcilie Fischbein','1916'],['n9950943138','Cäcilie Fischbein','1891'],
  ['n12728852672','Erich Marcus','1927'],['n12728852675','Erich Marcus','1896'],
  ['Q131314812','Johanne van Coevorden','1875'],['Q131314824','Johanne van Coevorden','1907'],
  ['n2435554646','Elisabeth Winterstein','1903'],['n2435554651','Elisabeth Winterstein','1937'],
  ['n13596330485','Jenny Wallach','1887'],['n13596330488','Jenny Wallach','1890'],
  ['n13597711112','Johanna Müller','1865'],['n13597711117','Johanna Müller','1890'],
  ['n4870354522','Frieda Schönfeld','1892'],['n4870354521','Frieda Schönfeld','1892'],
  ['Q139006758','Hilde Lewin',''],['Q139006760','Hilde Lewin','1920'],
  ['Q111685633','Sara Delmonte','1860'],['Q101070070','Moses','1868'],
  ['Q131287941','Grete Birnbaum','1922'],['Q131287946','Alfred Birnbaum','1924'],
  ['Q131287930','Max Birnbaum','1893'],['Q131287937','Margarete Birnbaum','1895'],
  ['n3234770177','Käthe Löwenherz','1897'],['n3234770178','Erwin Löwenherz','1891'],
  ['n830095194','Simon Morgenthau','1850'],['n830095188','Fritz Morgenthau','1885'],['n830095182','Sophie Morgenthau','1864'],
  ['n4526578119','Eva Fischbac','1929'],['n4526578118','Julius Fischbach','1892'],
  ['n6766501978','Luise Höflich','1856'],['n9668943130','Matthias Höflich','1859'],
  ['n3310495440','Wilhelm Simson',''],['n3310495439','Auguste Simson',''],
];
for (const [id, nm, jg] of hidden24) {
  const s = byId.get(id);
  assert(s, 'exists ' + id);
  assert(!s._aliasOf, 'visible with own column/ficha: ' + id + ' ' + nm + ' (alias of ' + s._aliasOf + ')');
  assert((s.i || '').includes(nm.split(' ')[0]) || (s.n||'').includes(nm.split(' ')[0]), 'inscription/name mentions ' + nm + ' for ' + id);
  if (jg) assert(KL.inscYears(s).includes(jg) || KL.yearOf(s.b) === jg, 'year ' + jg + ' for ' + id);
}
// Toda fusión que queda cumple las reglas en todos sus pares
let groups = 0;
for (const s of r.D) if (s._also) { groups++; const recs = [s, ...s._also]; for (let i=0;i<recs.length;i++) for (let j=i+1;j<recs.length;j++) assert(KL.samePerson(recs[i], recs[j]), 'merged pair obeys rules ' + recs[i].id + ' ' + recs[j].id); }
assert(groups === r.KLMerge.groups, 'group count');
assert(r.KLMerge.visible + r.KLMerge.extra === r.KLMerge.source, 'nobody lost: visible + merged = source');
console.log('OK dedupe: ' + r.KLMerge.groups + ' groups, ' + r.KLMerge.extra + ' merged records, ' + r.KLMerge.visible + ' visible of ' + r.KLMerge.source + '; all ' + hidden24.length + ' records from audit C visible; Isestraße 69: ' + r.KLMerge.isestr69);
