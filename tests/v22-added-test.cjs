/* v22 Batch 1: validates all 13 open municipal datasets added in Batch 1:
   - separated from data/stones.json (ODbL) and v21 Berlin/Köln
   - unique IDs across stones.json + v21 + v22
   - license, prefix, country code, coordinates, no invented inscriptions
   - hav(la, lo, dla, dlo) <= 25 m (or documented exception) */
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');

const stones = JSON.parse(fs.readFileSync(path.join(root, 'data/stones.json'), 'utf8'));
const berlin = JSON.parse(fs.readFileSync(path.join(root, 'data/berlin-added-20261121.json'), 'utf8'));
const koeln = JSON.parse(fs.readFileSync(path.join(root, 'data/koeln-added-20261121.json'), 'utf8'));
const exist = new Set([
  ...stones.stones.map(s => s.id),
  ...berlin.stones.map(s => s.id),
  ...koeln.stones.map(s => s.id),
]);

function hav(la1, lo1, la2, lo2) {
  const p = Math.PI / 180;
  const x = Math.sin((la2 - la1) * p / 2) ** 2
    + Math.cos(la1 * p) * Math.cos(la2 * p) * Math.sin((lo2 - lo1) * p / 2) ** 2;
  return 2 * 6371000 * Math.asin(Math.sqrt(Math.min(1, x)));
}

const SPECS = [
  { file: 'data/moenchengladbach-added-20261121.json', src: 'moenchengladbach', lic: 'dl-de-zero', prefix: 'mg-', cc: 'DE', count: 170, allowInsc: false },
  { file: 'data/denhaag-added-20261121.json',          src: 'denhaag',          lic: 'cc0-opendata', prefix: 'dh-', cc: 'NL', count: 308, allowInsc: false },
  { file: 'data/krefeld-added-20261121.json',          src: 'krefeld',          lic: 'dl-de-zero', prefix: 'kr-', cc: 'DE', count: 174, allowInsc: false },
  { file: 'data/monza-added-20261121.json',            src: 'monza',            lic: 'cc0-opendata', prefix: 'mz-', cc: 'IT', count: 162, allowInsc: false },
  { file: 'data/viersen-added-20261121.json',          src: 'viersen',          lic: 'dl-de-zero', prefix: 'vie-', cc: 'DE', count: 122, allowInsc: false },
  { file: 'data/memmingen-added-20261121.json',        src: 'memmingen',        lic: 'cc-by-4',    prefix: 'mm-', cc: 'DE', count: 9,   allowInsc: false },
  { file: 'data/moers-added-20261121.json',            src: 'moers',            lic: 'dl-de-zero', prefix: 'mo-', cc: 'DE', count: 51,  allowInsc: false },
  { file: 'data/grevenbroich-added-20261121.json',     src: 'grevenbroich',     lic: 'cc0-opendata', prefix: 'gv-', cc: 'DE', count: 36, allowInsc: true },
  { file: 'data/firenze-added-20261121.json',          src: 'firenze',          lic: 'cc-by-4',    prefix: 'fi-', cc: 'IT', count: 49,  allowInsc: true },
  { file: 'data/xanten-added-20261121.json',           src: 'xanten',           lic: 'dl-de-zero', prefix: 'xa-', cc: 'DE', count: 43, allowInsc: false },
  { file: 'data/dresden-added-20261121.json',          src: 'dresden',          lic: 'dl-de-by',   prefix: 'dr-', cc: 'DE', count: 5,   allowInsc: false },
  { file: 'data/erkrath-added-20261121.json',          src: 'erkrath',          lic: 'dl-de-zero', prefix: 'erk-', cc: 'DE', count: 4,  allowInsc: false },
  { file: 'data/dormagen-added-20261121.json',         src: 'dormagen',         lic: 'dl-de-zero', prefix: 'dor-', cc: 'DE', count: 2,  allowInsc: false },
];

const globalSeen = new Set();
let total = 0, maxMove = 0, maxId = null;
for (const sp of SPECS) {
  const part = JSON.parse(fs.readFileSync(path.join(root, sp.file), 'utf8'));
  if (!part.meta || !part.meta.license || !part.meta.license_url) throw new Error(sp.src + ': missing meta.license');
  if (!Array.isArray(part.stones) || part.stones.length !== sp.count) {
    throw new Error(`${sp.src}: expected ${sp.count}, got ${part.stones && part.stones.length}`);
  }
  if (part.meta.count !== part.stones.length) throw new Error(sp.src + ': meta.count mismatch');
  for (const s of part.stones) {
    if (!s.id || exist.has(s.id) || globalSeen.has(s.id)) throw new Error(sp.src + ': duplicate/existing id ' + s.id);
    globalSeen.add(s.id);
    if (!String(s.id).startsWith(sp.prefix)) throw new Error(sp.src + ': bad prefix ' + s.id);
    if (s.src !== sp.src) throw new Error(sp.src + ': bad src ' + s.src);
    if (s.lic !== sp.lic) throw new Error(sp.src + ': bad lic ' + s.lic);
    if (s.cc !== sp.cc) throw new Error(sp.src + ': bad cc ' + s.cc);
    if (s.la == null || s.lo == null) throw new Error(sp.src + ': missing la/lo ' + s.id);
    if (!sp.allowInsc && s.i) throw new Error(sp.src + ': unexpected inscription on ' + s.id);
    if (s.dla == null || s.dlo == null) throw new Error(sp.src + ': missing dla/dlo ' + s.id);
    const d = hav(s.la, s.lo, s.dla, s.dlo);
    if (d > maxMove) { maxMove = d; maxId = s.id; }
    if (d > 25) throw new Error(`${sp.src}: move ${d.toFixed(4)}m > 25m on ${s.id}`);
    total++;
  }
}
console.log(`OK: v22 Batch 1 (${SPECS.length} sources, ${total} stones, zero id collisions, max hav()=${maxMove.toFixed(4)}m on ${maxId})`);
