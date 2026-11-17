/* Lista Kauffmann — fusión de registros repetidos SOLO para mostrar (stones.json no cambia).
   Regla (17-11-2026, tras la auditoría C): se juntan dos registros solo si
   - el nombre completo normalizado es igual (o uno solo añade «geb. X» y el año coincide),
   - están en la misma dirección (grupo de dirección) y a pocos metros,
   - el año de nacimiento (campo b o «Jg.» de la inscripción) coincide en los dos;
     si a uno le falta el año, solo si es una pareja clara OpenStreetMap + Wikidata
     (uno es nodo OSM sin Wikidata, el otro es el elemento Wikidata, o el OSM apunta a ese Q),
   - y nada se contradice: fechas, años, «geb.», un campo «nombre» que no aparece en su propia
     inscripción (dato de origen erróneo), o dos inscripciones distintas sin el mismo elemento Wikidata.
   Ante la duda se muestran los dos. */
(function (root) {
  'use strict';

  function fold(t) {
    return String(t || '').toLowerCase()
      .replace(/ß/g, 'ss').replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue')
      .normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
  }
  function yearOf(v) { const m = String(v || '').match(/(1[7-9]|20)\d{2}/); return m ? m[0] : ''; }
  function nameKey(s) {
    let n = fold(s && s.n);
    n = n.replace(/\b(dr|prof|med|jur|phil|rer|nat)\.?(?=\s|$|[.,])/g, ' ')
      .replace(/[.,;:()'"‚‘’“”„«»]/g, ' ').replace(/\s+/g, ' ').trim();
    return n;
  }
  const GEB_RE = /\s+(?:geb|geboren|nee|verh|verheiratet|verw|gesch)\b.*/;
  function nameCore(s) { return nameKey(s).replace(GEB_RE, '').trim(); }
  function nameTail(s) { const m = nameKey(s).match(GEB_RE); return m ? m[0].trim() : ''; }

  const ANON_RE = /\b(sinto|sinti|sintiza|romni|rommni|roma|rom|unbekannt\w*|anonym\w*|namenlos\w*)\b|^\s*n\.?\s*n\.?\s*$/i;
  function isGenericName(s) {
    const n = String((s && s.n) || '').trim();
    if (!n || n.length < 3 || ANON_RE.test(n)) return true;
    if (/^(ein[e]?\s+)?(romm|rommni|sinto|sinteza|sintiza)(\s|$)/i.test(nameKey(s))) return true;
    if (/\d/.test(n) || /^(familie|ehepaar|geschwister|kinder)\b/i.test(n)) return true;
    return false;
  }

  // «Jg. 1904», «JG 1929», «Jahrgang 1871»
  const JG_RE = /\bj(?:g|ahrgang)\b\.?\s*(1[89]\d{2})/gi;
  function inscYears(s) {
    const out = [];
    const t = String((s && s.i) || '');
    let m; JG_RE.lastIndex = 0;
    while ((m = JG_RE.exec(t))) out.push(m[1]);
    return out;
  }
  // Años de nacimiento conocidos de un registro. ok:false si se contradicen entre sí.
  function birthYears(s) {
    const set = new Set();
    const b = yearOf(s && s.b); if (b) set.add(b);
    inscYears(s).forEach(function (y) { set.add(y); });
    return set;
  }
  function fullDate(v) {
    const t = String(v || '');
    if (/^\d{4}-\d{2}-\d{2}$/.test(t) && !/-00/.test(t)) return t;
    const m = t.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
    if (m) return m[3] + '-' + ('0' + m[2]).slice(-2) + '-' + ('0' + m[1]).slice(-2);
    return '';
  }

  // ¿El campo «nombre» aparece en su propia inscripción? Si no, el dato de origen es dudoso.
  function nameInInscription(s) {
    if (!s || !s.i) return true; // sin inscripción no podemos comprobarlo
    const words = new Set(fold(s.i).replace(/[^a-z0-9]+/g, ' ').split(' ').filter(Boolean));
    const toks = nameCore(s).replace(/[^a-z0-9 ]+/g, ' ').split(' ').filter(function (w) { return w.length >= 2; });
    if (!toks.length) return false;
    return toks.every(function (w) { return words.has(w); });
  }

  function isOsm(s) { return /^[nwr]\d+$/.test(String(s && s.id)); }
  function isWdItem(s) { return /^Q\d+$/.test(String(s && s.id)); }
  function osmWdPair(a, b) {
    const pair = function (o, w) {
      return isOsm(o) && isWdItem(w) && (!o.wd || o.wd === w.id);
    };
    return pair(a, b) || pair(b, a);
  }

  function info(s) {
    if (s._dd) return s._dd;
    const ys = birthYears(s);
    const d = {
      generic: isGenericName(s), key: nameKey(s), core: nameCore(s), tail: nameTail(s),
      nin: nameInInscription(s), years: ys, by: ys.size === 1 ? [...ys][0] : '',
      fb: fullDate(s.b), dy: yearOf(s.d), fd: fullDate(s.d),
      wd: s.wd || (isWdItem(s) ? s.id : ''),
      insc: fold(s.i).replace(/[^a-z0-9]+/g, '')
    };
    try { Object.defineProperty(s, '_dd', { value: d, enumerable: false, configurable: true, writable: true }); } catch (e) {}
    return d;
  }
  // Devuelve {same:boolean, why:string}
  function compare(a, b) {
    const A = info(a), B = info(b);
    if (A.generic || B.generic) return { same: false, why: 'generic' };
    if (!A.key || A.key.length < 3 || !B.key) return { same: false, why: 'noname' };
    let nameRule;
    if (A.key === B.key) nameRule = 'full';
    else if (A.core && A.core.length >= 5 && A.core === B.core && (!A.tail || !B.tail)) nameRule = 'core';
    else return { same: false, why: 'name' };
    if (!A.nin || !B.nin) return { same: false, why: 'badNameField' };
    // Mismo elemento de Wikidata = misma persona según la fuente. Si no, y las dos inscripciones
    // dicen cosas distintas (otro destino, otra fecha…), ante la duda se muestran las dos.
    const sameItem = !!((A.wd && B.wd && A.wd === B.wd) || (a.p && b.p && a.p === b.p));
    if (!sameItem && A.insc && B.insc && A.insc !== B.insc) return { same: false, why: A.wd && B.wd ? 'differentWikidataAndInscription' : 'inscriptionDiffers' };
    if (a.p && b.p && a.p !== b.p) return { same: false, why: 'differentPerson' };
    if (A.years.size > 1 || B.years.size > 1) return { same: false, why: 'internalYearConflict' };
    if (A.by && B.by && A.by !== B.by) return { same: false, why: 'birthYear' };
    if (A.fb && B.fb && A.fb !== B.fb) return { same: false, why: 'birthDate' };
    if (A.dy && B.dy && A.dy !== B.dy) return { same: false, why: 'deathYear' };
    if (A.fd && B.fd && A.fd !== B.fd) return { same: false, why: 'deathDate' };
    const bothYears = !!(A.by && B.by);
    if (nameRule === 'core' && !bothYears) return { same: false, why: 'coreNeedsYears' };
    if (!bothYears && !osmWdPair(a, b)) return { same: false, why: 'noYearNotPair' };
    return { same: true, why: nameRule + (bothYears ? '+year' : '+osmWdPair') };
  }
  function samePerson(a, b) { return compare(a, b).same; }

  const api = { fold: fold, yearOf: yearOf, nameKey: nameKey, nameCore: nameCore, isGenericName: isGenericName,
    inscYears: inscYears, birthYears: birthYears, nameInInscription: nameInInscription, osmWdPair: osmWdPair,
    compare: compare, samePerson: samePerson };
  root.KLDedupe = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
