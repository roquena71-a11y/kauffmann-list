/* v21: placas añadidas de Berlín (CC BY) y Colonia (dl-de/zero-2-0) no se mezclan
   con data/stones.json (ODbL) y no reutilizan un id ya publicado. */
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const stones = JSON.parse(fs.readFileSync(path.join(root, 'data/stones.json'), 'utf8'));
const berlin = JSON.parse(fs.readFileSync(path.join(root, 'data/berlin-added-20261121.json'), 'utf8'));
const koeln = JSON.parse(fs.readFileSync(path.join(root, 'data/koeln-added-20261121.json'), 'utf8'));
const exist = new Set(stones.stones.map(s => s.id));
function check(part, src, lic, prefix) {
  if (!part.meta || !part.meta.license || !part.meta.license_url) throw new Error(src + ': falta meta.license');
  if (!Array.isArray(part.stones) || !part.stones.length) throw new Error(src + ': sin placas');
  if (part.meta.count !== part.stones.length) throw new Error(src + ': count ' + part.meta.count + ' != ' + part.stones.length);
  const seen = new Set();
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
      // la/lo de origen intactos; el desplazamiento es solo de dibujo
      const mLat = 111320;
      const mid = (s.la + s.dla) / 2 * Math.PI / 180;
      const d = Math.hypot((s.la - s.dla) * mLat, (s.lo - s.dlo) * mLat * Math.cos(mid));
      if (d > 60) throw new Error(src + ': desplazamiento ' + d.toFixed(1) + ' m en ' + s.id);
    }
  }
  return seen.size;
}
const nb = check(berlin, 'berlin', 'cc-by', 'ber-');
const nk = check(koeln, 'koeln', 'dl-de-zero', 'koeln-');
if (berlin.meta.license_url.indexOf('opendefinition.org/licenses/cc-by') < 0) throw new Error('berlin license_url');
if (koeln.meta.license_url.indexOf('govdata.de/dl-de/zero-2-0') < 0) throw new Error('koeln license_url');
console.log('OK: v21 added berlin', nb, 'koeln', nk, 'sin colisión con stones.json');
