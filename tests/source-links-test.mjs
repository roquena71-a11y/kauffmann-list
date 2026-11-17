import { createRequire } from 'module';
import { pathToFileURL } from 'url';
import { createContext, runInContext } from 'vm';
import { readFileSync } from 'fs';

const src = readFileSync(new URL('../source-links.js', import.meta.url), 'utf8');
const ctx = createContext({ module: { exports: {} }, globalThis: {} });
ctx.globalThis = ctx;
runInContext(src, ctx);
const KL = ctx.KLSourceLinks || ctx.module.exports;

function assert(cond, msg){ if (!cond) throw new Error('FAIL: '+msg); }

// parse names from our dataset, including geb.
const p1 = KL.parsePersonName('Elfriede Löpert');
assert(p1.first==='Elfriede' && p1.last==='Löpert' && p1.query==='Elfriede Löpert', 'Löpert parse');
const p2 = KL.parsePersonName('Gertrud Böhm geb. Cohn');
assert(p2.first==='Gertrud' && p2.last==='Böhm' && p2.maiden==='Cohn' && p2.query==='Gertrud Böhm', 'Böhm geb. stripped from query');
const p3 = KL.parsePersonName('Abraham A. Bukofzer');
assert(p3.first==='Abraham A.' && p3.last==='Bukofzer' && p3.query==='Abraham A. Bukofzer', 'Bukofzer initials');
const p4 = KL.parsePersonName('Michael Frankenthal');
assert(p4.query==='Michael Frankenthal', 'Frankenthal');
assert(KL.parsePersonName('')===null && KL.parsePersonName('   ')===null, 'empty name');

const sL = {n:'Elfriede Löpert', a:'Isestraße 69, Hamburg', c:'Hamburg'};
const list = KL.sourceSearchList(sL, null, 'es');
const byKey = Object.fromEntries(list.map(x => [x.key, x]));
assert(byKey.arolsenSearchName, 'arolsen present');
assert(byKey.arolsenSearchName.href==='https://collections.arolsen-archives.org/en/search?s=Elfriede%20L%C3%B6pert', 'arolsen URL '+byKey.arolsenSearchName.href);
assert(byKey.yvSearchName.href==='https://collections.yadvashem.org/en/names/search-results-names?page=1&gn_first_name=Elfriede&gnt_first_name=yvSynonym&gn_last_name=L%C3%B6pert&gnt_last_name=yvSynonym', 'yv URL '+byKey.yvSearchName.href);
assert(byKey.ushmmSearchName.href==='https://www.ushmm.org/remember/resources-holocaust-survivors-victims/database-of-holocaust-survivor-and-victim-names/search-names?any_first_name=Elfriede&any_last_name=L%C3%B6pert', 'ushmm URL '+byKey.ushmmSearchName.href);
assert(byKey.gbSearchPage.href==='https://apps.bundesarchiv.de/gedenkbuch/en', 'gb search page (no fake deep link)');
assert(byKey.gbSearchPage.prefilled===false, 'gb not claimed prefilled');
assert(byKey.hhSearchName.href==='https://stolpersteine-hamburg.de/suchergebnisse?name=Elfriede%20L%C3%B6pert', 'hamburg de/es URL');
assert(!byKey.beSearchName, 'no berlin link for hamburg stone');

const listEn = KL.sourceSearchList(sL, null, 'en');
const hhEn = listEn.find(x=>x.key==='hhSearchName');
assert(hhEn.href==='https://stolpersteine-hamburg.de/en/results?name=Elfriede%20L%C3%B6pert', 'hamburg en URL');

const sF = {n:'Michael Frankenthal', b:'1866-09-01', a:'Isestraße 69, 20149 Hamburg', c:'Hamburg', gb:['868017'], us:['9234168']};
const listF = KL.sourceSearchList(sF, null, 'de');
const keysF = listF.map(x=>x.key);
assert(keysF.includes('gb') && !keysF.includes('gbSearchPage'), 'gedenkbuch record instead of search page when id exists');
assert(listF.find(x=>x.key==='gb').href==='https://www.bundesarchiv.de/gedenkbuch/de868017', 'gb record url');
assert(!keysF.includes('ushmmSearchName') && keysF.includes('ushmm'), 'ushmm record when id exists');
assert(keysF.includes('yvSearchName'), 'yv name search when no yv id');
const usRec = listF.find(x=>x.key==='ushmm');
assert(usRec.href.includes('PersonId=9234168'), 'ushmm person id');

const sB = {n:'Abraham A. Bukofzer', b:'1886-02-23', a:'Trautenaustraße 18, 10717 Berlin', c:'Berlin'};
const listB = KL.sourceSearchList(sB, null, 'en');
const be = listB.find(x=>x.key==='beSearchName');
assert(be && be.href==='https://www.stolpersteine-berlin.de/en/finding-stolpersteine?name=Abraham%20A.%20Bukofzer', 'berlin en URL '+ (be&&be.href));
const usB = listB.find(x=>x.key==='ushmmSearchName');
assert(!/birth_year/.test(usB.href), 'ushmm does not force an exact birth year (false zeros) '+usB.href);
assert(!listB.some(x=>x.key==='hhSearchName'), 'no hamburg link for berlin stone');

const sG = {n:'Gertrud Böhm geb. Cohn', a:'Isestraße 69, Hamburg', c:'Hamburg'};
const hhG = KL.sourceSearchList(sG, null, 'de').find(x=>x.key==='hhSearchName');
assert(hhG.href.includes('name=Gertrud%20B%C3%B6hm'), 'hamburg strips geb. from query');
assert(!/[?&]name=[^#]*geb/i.test(hhG.href) && !hhG.href.includes('Cohn'), 'hamburg query has no geb/Cohn: '+hhG.href);

const anon = KL.sourceSearchList({n:'unbekannt', c:'Hamburg'}, null, 'es', {anon:true});
assert(!anon.some(x=>x.prefilled && x.q), 'anon has no name-prefilled links');
assert(anon.some(x=>x.key==='gbSearchPage'), 'anon still gets honest gedenkbuch search page');
assert(!anon.some(x=>x.key==='hhSearchName'), 'anon no city name search');

for (const it of [...list, ...listF, ...listB, ...listEn]) {
  assert(!/[?&](utm_|fbclid|gclid|mc_cid|ref=)/.test(it.href), 'no tracking params: '+it.href);
  assert(it.href.startsWith('https://'), 'https only: '+it.href);
}

console.log('OK', list.length, 'links for Elfriede Löpert (es)');

// ---------- Auditorías A/B/C (17-11-2026) ----------
const P = n => KL.parsePersonName(n);
const pq = (n, first, last, maiden) => { const r = P(n); assert(r && r.first===first && r.last===last && (maiden===undefined || r.maiden===maiden), 'parse '+n+' → '+JSON.stringify(r)); };
pq('Franziska Levy (geb. Bucky)', 'Franziska', 'Levy', 'Bucky');
pq('Amalie Levy, geb. Meyer', 'Amalie', 'Levy', 'Meyer');
pq('Dr. Max Schlösser', 'Max', 'Schlösser');
pq('Prof. Dr. med. Simon Bloch', 'Simon', 'Bloch');
pq('Felix Max Frank, Dr.', 'Felix Max', 'Frank');
pq('Ilse Wachtel verh. Kahn', 'Ilse', 'Wachtel');
pq('Ilse Schaefer (verw. Sternberg)', 'Ilse', 'Schaefer');
pq('Albert Levy, Arbeitsort', 'Albert', 'Levy');
pq('Amalie Levy,', 'Amalie', 'Levy');
pq('Hilde Lewin, geb.1920', 'Hilde', 'Lewin');
pq('Elise van der Wyk', 'Elise', 'van der Wyk');
pq('Moses ‚Martin‘ Delmonte', 'Moses', 'Delmonte');
pq('Stolperstein dedicated to Hermann Wertheim', 'Hermann', 'Wertheim');
pq('Stolperstein: Simon Hertz', 'Simon', 'Hertz');
pq('Anna Chana Strauß', 'Anna Chana', 'Strauß');
for (const n of ['unbekannter Wert','Unbekannt','die unbekannten Kinder des Kinderkrankenhauses Rothenburgsort','Familie Frank','12 Bürger jüdischen Glaubens',
  '8 Stolpersteine: Charlotte Steinbock, Max X','Synagogue','Walter Isay, Friederike Isay und Fanny Isay','Romm Jg. 1904','N.N.','http://www.wikidata.org/.well-known/genid/abc'])
  assert(KL.isCollectiveName(n), 'collective/anonymous: '+n);
for (const n of ['Resi Heim','Albert Levy, Arbeitsort','Hilde Lewin, geb.1920','Stolperstein, Thekla Abel','Elfriede Löpert'])
  assert(!KL.isCollectiveName(n), 'not collective: '+n);
for (const n of ['unbekannter Wert','Familie Frank','12 Bürger jüdischen Glaubens']) {
  const L2 = KL.sourceSearchList({n, c:'Hamburg', a:'X 1, Hamburg'}, null, 'de');
  assert(!L2.some(x => x.q), 'no prefilled name search for '+n);
  assert(!L2.some(x => x.key==='hhSearchName'), 'no city name search for '+n);
}
// YV/USHMM con nombre bien separado (sin coma, paréntesis ni título)
const lv = KL.sourceSearchList({n:'Franziska Levy (geb. Bucky)', c:'Berlin'}, null, 'en');
const yvL = lv.find(x=>x.key==='yvSearchName').href;
assert(yvL.includes('gn_first_name=Franziska&') && yvL.includes('gn_last_name=Levy&'), 'yv parse with (geb.) '+yvL);
const usL = lv.find(x=>x.key==='ushmmSearchName').href;
assert(usL.endsWith('any_first_name=Franziska&any_last_name=Levy'), 'ushmm parse with (geb.) '+usL);
const dr = KL.sourceSearchList({n:'Dr. Max Schlösser'}, null, 'en').find(x=>x.key==='yvSearchName').href;
assert(dr.includes('gn_first_name=Max&'), 'title stripped for YV '+dr);
// Un solo nombre: no se adivina nombre/apellido en YV/USHMM
const one = KL.sourceSearchList({n:'Klara'}, null, 'en').map(x=>x.key);
assert(one.includes('yvSearch') && !one.includes('yvSearchName') && one.includes('ushmmSearch'), 'single token → generic YV/USHMM '+one);
// Gedenkbuch: id codificado; registro directo oculta la página de búsqueda
const gbEvil = KL.sourceSearchList({n:'A B', gb:['123/../../evil?x=1']}, null, 'de').find(x=>x.key==='gb').href;
assert(gbEvil === 'https://www.bundesarchiv.de/gedenkbuch/de123%2F..%2F..%2Fevil%3Fx%3D1', 'gb id encoded '+gbEvil);
const hasGb = KL.sourceSearchList({n:'Eva Cahn'}, null, 'es', {has:{gb:true, yv:true, ushmm:true}}).map(x=>x.key);
assert(!hasGb.includes('gbSearchPage') && !hasGb.includes('yvSearchName') && !hasGb.includes('ushmmSearchName'), 'person view with direct records hides those searches '+hasGb);
// rec.links: solo http(s)
const bad = KL.sourceSearchList({n:'A B'}, {links:{berlin:'javascript:alert(1)', hamburg:'data:text/html,x', bremen:' https://www.stolpersteine-bremen.de/detail.php?id=1 '}}, 'de');
assert(!bad.some(x=>/^(javascript|data):/i.test(x.href)), 'no javascript:/data: hrefs');
assert(bad.some(x=>x.key==='bremenBio' && x.href==='https://www.stolpersteine-bremen.de/detail.php?id=1'), 'https bio kept');
assert(KL.safeUrl('JaVaScRiPt:alert(1)')==='' && KL.safeUrl('http://ex.org/a')==='http://ex.org/a', 'safeUrl');
// OSM y Wikidata nunca salen en «Buscar en las fuentes»
const all = KL.sourceSearchList({n:'Lina Friedmann geb. Blecher', id:'n123', wd:'Q1', p:'Q2', c:'Hamburg', gb:['1']}, null, 'es');
assert(!all.some(x=>/openstreetmap|wikidata/.test(x.href)), 'no OSM/Wikidata in source search');
assert(new Set(all.map(x=>x.href)).size === all.length, 'no repeated hrefs');
console.log('OK audits A/B/C name parsing, anon/collective, gb encoding, safeUrl, no OSM/WD');
