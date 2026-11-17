// Informe de la fusión: qué se junta, por qué regla, y qué pares dudosos se dejan separados.
const fs=require('fs'), path=require('path');
const {run}=require('./merge-harness.cjs');
const KL=require('../dedupe.js');
const r=run(); const byId=r.byId; const D=r.D;
const yr=s=>[...KL.birthYears(s)].join('/')||'-';
const row=s=>({id:s.id,n:s.n,jg:yr(s),src:s.src,wd:s.wd||'',p:s.p||'',a:s.a||'',i:s.i||''});
const merges=[]; const rules={};
for(const s of D){ if(!s._also) continue; const recs=[s,...s._also]; const why=KL.compare(recs[0],recs[1]).why; rules[why]=(rules[why]||0)+1; merges.push({rule:why,recs:recs.map(row)}); }
// Pares dudosos: mismo nombre (completo o base) en la misma dirección, a <=25 m, que NO se juntan.
const addr=new Map(); for(const s of D){ const k=(s.a||'').toLowerCase().replace(/\s+/g,' ').trim(); if(!k) continue; (addr.get(k)||addr.set(k,[]).get(k)).push(s); }
const doubt=[]; const why={};
const dist=(a,b)=>Math.hypot((a.la-b.la)*111320,(a.lo-b.lo)*111320*Math.cos(a.la*Math.PI/180));
for(const list of addr.values()){ if(list.length<2) continue;
  for(let i=0;i<list.length;i++) for(let j=i+1;j<list.length;j++){ const a=list[i], b=list[j];
    if((a._aliasOf||a.id)===(b._aliasOf||b.id)) continue;
    if(KL.isGenericName(a)||KL.isGenericName(b)) continue;
    if(KL.nameCore(a)!==KL.nameCore(b) || KL.nameCore(a).length<5) continue;
    if(dist(a,b)>25) continue;
    const c=KL.compare(a,b); if(c.same) continue; // (unión rechazada por cadena; no debería pasar)
    why[c.why]=(why[c.why]||0)+1; doubt.push({why:c.why,a:row(a),b:row(b)});
  }}
const out={date:new Date().toISOString(),visible:r.KLMerge.visible,source:r.KLMerge.source,groups:r.KLMerge.groups,extra:r.KLMerge.extra,chainRejected:r.KLMerge.doubtful,rules,doubtByReason:why,merges,doubt};
fs.writeFileSync(path.join(__dirname,'..','shots','merge-report.json'),JSON.stringify(out,null,1));
console.log(JSON.stringify({groups:out.groups,extra:out.extra,visible:out.visible,rules,doubtPairs:doubt.length,doubtByReason:why}));
