// Ejecuta la fusión real de app3d.js (buildStones) sobre data/stones.json, sin navegador.
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
function run() {
  const KLDedupe = require(path.join(ROOT, 'dedupe.js'));
  const src = fs.readFileSync(path.join(ROOT, 'app3d.js'), 'utf8');
  const a = src.indexOf('const M_LAT');
  const endMarker = "if (typeof window!=='undefined') window.KLMerge = KLMerge;\n}";
  const b = src.indexOf(endMarker) + endMarker.length;
  const anon = src.split('\n').find(l => /^const ANON_NAME\s*=/.test(l));
  const isAnon = src.split('\n').find(l => /^function isAnonStone/.test(l));
  const body = anon + '\n' + isAnon + '\nlet DATA=[], byId=new Map(), VISIBLE=[], STONES_FC, POINTS_FC, LIGHTS_FC;\n' +
    src.slice(a, b).replace("var KLMerge =", "KLMergeOut =") +
    '\nreturn {go:(d)=>{DATA=d; byId=new Map(d.map(s=>[s.id,s])); buildStones(); return {KLMerge:KLMergeOut, VISIBLE, byId};}};';
  let KLMergeOut;
  const mod = new Function('KLDedupe', 'window', 'KLMergeOut', body)(KLDedupe, undefined, undefined);
  const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/stones.json'))).stones;
  const out = mod.go(D);
  return { D, ...out };
}
module.exports = { run };
if (require.main === module) {
  const t0 = Date.now();
  const r = run();
  console.log('ms', Date.now() - t0, JSON.stringify({ groups: r.KLMerge.groups, extra: r.KLMerge.extra, visible: r.KLMerge.visible, source: r.KLMerge.source, isestr69: r.KLMerge.isestr69, doubtfulBuckets: r.KLMerge.doubtful.length }));
}
