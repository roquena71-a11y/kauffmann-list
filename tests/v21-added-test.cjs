/* v21: placas añadidas de Berlín (CC BY) y Colonia (dl-de/zero-2-0) no se mezclan
   con data/stones.json (ODbL) y no reutilizan un id ya publicado.
   El desplazamiento de dibujo (dla/dlo) se mide con hav() oficial (R=6.371.000 m,
   la misma fórmula que pipeline/tools/geo.py) y no puede superar 25 m salvo
   excepción documentada en excepciones-25m-v20.csv o excepciones-25m-v21*.csv. */
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const stones = JSON.parse(fs.readFileSync(path.join(root, 'data/stones.json'), 'utf8'));
const berlin = JSON.parse(fs.readFileSync(path.join(root, 'data/berlin-added-20261121.json'), 'utf8'));
const koeln = JSON.parse(fs.readFileSync(path.join(root, 'data/koeln-added-20261121.json'), 'utf8'));
const exist = new Set(stones.stones.map(s => s.id));

function hav(la1, lo1, la2, lo2) {
  const p = Math.PI / 180;
  const x = Math.sin((la2 - la1) * p / 2) ** 2
    + Math.cos(la1 * p) * Math.cos(la2 * p) * Math.sin((lo2 - lo1) * p / 2) ** 2;
  return 2 * 6371000 * Math.asin(Math.sqrt(Math.min(1, x)));
}

function loadExceptions() {
  const ids = new Set();
  for (const name of fs.readdirSync(root)) {
    if (!/^excepciones-25m-v2[01].*\.csv$/.test(name)) continue;
    const lines = fs.readFileSync(path.join(root, name), 'utf8').split(/\r?\n/);
    for (const line of lines.slice(1)) {
      if (!line.trim()) continue;
      const id = line.split(',')[0].trim();
      if (id) ids.add(id);
    }
  }
  return ids;
}
const exceptions = loadExceptions();

function check(part, src, lic, prefix) {
  if (!part.meta || !part.meta.license || !part.meta.license_url) throw new Error(src + ': falta meta.license');
  if (!Array.isArray(part.stones) || !part.stones.length) throw new Error(src + ': sin placas');
  if (part.meta.count !== part.stones.length) throw new Error(src + ': count ' + part.meta.count + ' != ' + part.stones.length);
  const seen = new Set();
  let maxMove = 0, maxId = null;
  for (const s of part.stones) {
    if (!s.id || exist.has(s.id) || seen.has(s.id)) throw new Error(src + ': id ausente o duplicado ' + s.id);
    seen.add(s.id);
    if (!String(s.id).startsWith(prefix)) throw new Error(src + ': id no usa el prefijo ' + prefix + ' ' + s.id);
    if (s.src !== src) throw new Error(src + ': src ' + s.src);
    if (s.lic !== lic) throw new Error(src + ': lic ' + s.lic);
    if (s.la == null || s.lo == null) throw new Error(src + ': sin coordenadas de origen ' + s.id);
    if (s.cc && s.cc !== 'DE') throw new Error(src + ': cc inesperado ' + s.cc);
    if (s.i) throw new Error(src + ': no debe inventarse inscripción ' + s.id);
    if (s.dla != null && s.dlo != null) {
      const d = hav(s.la, s.lo, s.dla, s.dlo);
      if (d > maxMove) { maxMove = d; maxId = s.id; }
      if (d > 25 && !exceptions.has(s.id)) {
        throw new Error(src + ': desplazamiento ' + d.toFixed(4) + ' m en ' + s.id + ' (límite 25 m; no está en excepciones documentadas)');
      }
    }
  }
  return { n: seen.size, maxMove, maxId };
}
const rb = check(berlin, 'berlin', 'cc-by', 'ber-');
const rk = check(koeln, 'koeln', 'dl-de-zero', 'koeln-');
if (berlin.meta.license_url.indexOf('opendefinition.org/licenses/cc-by') < 0) throw new Error('berlin license_url');
if (koeln.meta.license_url.indexOf('govdata.de/dl-de/zero-2-0') < 0) throw new Error('koeln license_url');
console.log('OK: v21 added berlin', rb.n, 'koeln', rk.n, 'sin colisión con stones.json; máx hav()',
  Math.max(rb.maxMove, rk.maxMove).toFixed(4), 'm',
  (rb.maxMove >= rk.maxMove ? rb.maxId : rk.maxId));
