/* Lista Kauffmann — enlaces de búsqueda a fuentes oficiales.
   Solo construye URLs con datos que ya están en la ficha (nombre, año de
   nacimiento, ciudad). No descarga, no copia y no guarda datos de esos archivos.
   Patrones comprobados el 2026-11-16 en los sitios oficiales (véase comentarios). */
(function (root) {
  'use strict';

  // Títulos y tratamientos que no forman parte del nombre en los buscadores.
  const TITLE_RE = /^(?:dr|prof|med|jur|phil|rer|nat|dent|vet|dipl|ing|h\.?\s*c|sanit[aä]tsrat|justizrat|kommerzienrat|rabbiner|pfarrer|kantor|lehrer)\.?$/i;
  // Marcadores tras los que ya no viene el nombre de la persona: «geb. X», «verh. X», «verw. X», «gesch.», «, Arbeitsort»…
  const MAIDEN_RE = /^(?:geb|geborene?|geboren|n[ée]e)\.?$/i;
  const STOP_RE = /^(?:geb|geborene?|geboren|n[ée]e|verh|verheiratete?|verw|verwitwete?|gesch|geschiedene?|alias|gen|genannt)\.?$/i;
  const PARTICLES = /^(?:von|vom|van|de|den|der|du|da|dos|del|della|di|la|le|ten|ter|zu|zum|zur|op|het|'t)$/i;

  // Nombres que no son de una persona concreta: no se rellena ninguna búsqueda con ellos.
  const PREFIX_RE = /^(?:stolperstein|stoperstein)\s*(?:[:,\-–]\s*|\s(?:f[üu]r|dedicated\s+to|for)\s+|\s+)(?=\S)/i;
  function isCollectiveName(raw) {
    const n = String(raw || '').replace(/\s+/g, ' ').trim().replace(PREFIX_RE, '');
    if (!n || n.length < 3) return true;
    if (/\bunbekannt\w*|\banonym\w*|\bnamenlos\w*|^\s*n\.?\s*n\.?\s*$|\bunknown\b/i.test(n)) return true;
    if (/^(?:familie|family|ehepaar|eheleute|geschwister|kinder|br[üu]der|schwestern|die\s|ihr\s|sein\s|ein\s|eine\s)/i.test(n)) return true;
    const head = n.replace(/\([^)]*\)/g, ' ').split(',')[0];
    if (/\d/.test(head)) return true; // «12 Bürger…», «Romm Jg. 1904», «8 Stolpersteine: …»
    if (/[:;]/.test(n)) return true;
    if (/\b(?:und|and|&|sowie)\b/i.test(n.replace(/\(.*?\)/g, ''))) return true; // dos o más personas
    if (/\b(?:synagoge|synagogue|gemeinde|opfer|juden|j[üu]dische[nrs]?|stolpersteine?|gedenk\w*|denkmal|zwangsarbeiter\w*)\b|^https?:/i.test(n)) return true;
    // «Bürger» es palabra de grupo («Bürger von X», «12 Bürger») pero también apellido (Schulim Bürger): solo es grupo si NO va tras un nombre de pila.
    if (/\bb[üu]rger\b/i.test(n) && !/^\p{Lu}[\p{L}'.-]+\s+(?:\p{Lu}[\p{L}'.-]+\s+)*B[üu]rger$/u.test(n.replace(/\([^)]*\)/g, '').trim())) return true;
    return false;
  }

  function parsePersonName(raw) {
    let n = String(raw || '').replace(/\s+/g, ' ').trim();
    if (!n) return null;
    n = n.replace(PREFIX_RE, '');
    let maiden = '';
    // «(geb. X)» → apellido de soltera; cualquier otro paréntesis se quita.
    n = n.replace(/\(([^)]*)\)/g, function (_, inner) {
      const m = /^\s*(?:geb\.?|geborene?|geboren|n[ée]e)\s+(.+?)\s*$/i.exec(inner);
      if (m && !maiden) maiden = m[1];
      return ' ';
    });
    n = n.replace(/[‚‘’'"“”„«»][^‚‘’'"“”„«»]{1,30}[‚‘’'"“”„«»]/g, ' '); // apodos entre comillas
    n = n.replace(/\s+/g, ' ').trim();
    // Lo que va tras la primera coma no es parte del nombre («, geb. X», «, Arbeitsort», «, Dr.»).
    const comma = n.indexOf(',');
    let afterComma = '';
    if (comma >= 0) { afterComma = n.slice(comma + 1).trim(); n = n.slice(0, comma).trim(); }
    if (!maiden && afterComma) {
      const m = /^(?:geb\.?|geborene?|geboren|n[ée]e)\s+([^,;]+)/i.exec(afterComma);
      if (m) maiden = m[1].trim();
    }
    let toks = n.split(' ').filter(Boolean);
    const out = [];
    for (let i = 0; i < toks.length; i++) {
      const w = toks[i];
      if (STOP_RE.test(w)) {
        if (MAIDEN_RE.test(w) && !maiden) maiden = toks.slice(i + 1).join(' ');
        break;
      }
      if (TITLE_RE.test(w.replace(/\.$/, '')) || /^(?:dr|prof)\./i.test(w)) continue;
      out.push(w);
    }
    toks = out.map(function (w) { return w.replace(/^[^\p{L}]+|[^\p{L}.'-]+$/gu, ''); }).filter(Boolean);
    maiden = maiden.replace(/[,;.)\s]+$/, '').trim();
    if (!toks.length) return null;
    // Apellido: último elemento, con partículas («van der Wyk», «von Halle»).
    let k = toks.length - 1;
    while (k > 1 && PARTICLES.test(toks[k - 1])) k--;
    const last = toks.slice(k).join(' ');
    const first = toks.slice(0, k).join(' ');
    const query = first ? first + ' ' + last : last;
    return { full: toks.join(' '), first: first, last: last, maiden: maiden, query: query };
  }

  // Solo http(s): nada de javascript:, data:, etc.
  function safeUrl(u) {
    const t = String(u || '').trim();
    return /^https?:\/\/[^\s"'<>]+$/i.test(t) ? t : '';
  }

  function birthYear(s) {
    const m = String((s && (s.b || s.birth_date)) || '').match(/\b(\d{4})\b/);
    return m ? m[1] : '';
  }

  function cityKey(s) {
    const t = [s && s.c, s && s.a, s && s.birth_place, s && s.death_place]
      .filter(Boolean).join(' ');
    if (/\bhamburg\b/i.test(t)) return 'hamburg';
    if (/\bberlin\b/i.test(t)) return 'berlin';
    return '';
  }

  function archiveLang(uiLang) { return uiLang === 'de' ? 'de' : 'en'; }

  function idsOf(v) {
    if (v == null || v === '') return [];
    return Array.isArray(v) ? v.filter(Boolean).map(String) : [String(v)];
  }

  /**
   * @param {object} s  piedra o persona: n, b, c, a, gb, yv, us, wd, p, id
   * @param {object|null} rec  paquete local de biografía (rec.links) si ya está cargado
   * @param {string} uiLang  'es'|'de'|'en'
   * @param {object} [opts]  {anon:boolean, has:{gb,yv,ushmm}} (has = registro directo ya enlazado en la ficha)
   * @returns {{href:string, key:string, prefilled:boolean, q?:string}[]}
   */
  function sourceSearchList(s, rec, uiLang, opts) {
    const items = [];
    const L = archiveLang(uiLang);
    const links = (rec && rec.links) || {};
    const anon = !!(opts && opts.anon) || isCollectiveName(s && s.n);
    const parsed = anon ? null : parsePersonName(s && s.n);
    const q = parsed && parsed.query;
    const city = cityKey(s);

    ['berlin', 'hamburg', 'bremen'].forEach(function (c) {
      const u = safeUrl(links[c]);
      if (u) items.push({ href: u, key: c + 'Bio', prefilled: true });
    });

    const has = (opts && opts.has) || {}; // registros directos ya mostrados en otro bloque (vista de persona)
    const gb = idsOf(links.gedenkbuch || (s && s.gb));
    const yv = idsOf(links.yadvashem || (s && s.yv));
    const us = idsOf(links.ushmm || (s && s.us));
    const hasGb = gb.length > 0 || !!has.gb, hasYv = yv.length > 0 || !!has.yv, hasUs = us.length > 0 || !!has.ushmm;

    // Registro directo solo si el id ya está en nuestros datos (Wikidata / rec).
    // www.bundesarchiv.de/gedenkbuch/{lang}{id} redirige a apps.bundesarchiv.de (comprobado 2026-11-16).
    gb.forEach(function (g) {
      items.push({ href: 'https://www.bundesarchiv.de/gedenkbuch/' + L + encodeURIComponent(g), key: 'gb', prefilled: true });
    });
    yv.forEach(function (y) {
      items.push({ href: 'https://collections.yadvashem.org/' + L + '/names/' + encodeURIComponent(y), key: 'yv', prefilled: true });
    });
    us.forEach(function (u) {
      items.push({ href: 'https://www.ushmm.org/online/hsv/person_view.php?PersonId=' + encodeURIComponent(u), key: 'ushmm', prefilled: true });
    });

    // Arolsen: GET ?s=NAME rellena la búsqueda y devuelve resultados (comprobado EN/DE, 2026-11-16).
    if (q) {
      items.push({
        href: 'https://collections.arolsen-archives.org/' + L + '/search?s=' + encodeURIComponent(q),
        key: 'arolsenSearchName', prefilled: true, q: q
      });
    } else {
      items.push({ href: 'https://collections.arolsen-archives.org/' + L + '/search', key: 'arolsenSearch', prefilled: false });
    }

    // Yad Vashem: la propia búsqueda oficial produce
    // ?page=1&gn_first_name=&gnt_first_name=yvSynonym&gn_last_name=&gnt_last_name=yvSynonym
    // (comprobado 2026-11-16: Frankenthal 3, Bukofzer 1, Böhm 28; Löpert 0 en esa base).
    // Con un solo nombre no sabemos si es nombre o apellido: buscador sin rellenar.
    if (parsed && parsed.last && parsed.first) {
      let yq = 'page=1';
      if (parsed.first) yq += '&gn_first_name=' + encodeURIComponent(parsed.first) + '&gnt_first_name=yvSynonym';
      yq += '&gn_last_name=' + encodeURIComponent(parsed.last) + '&gnt_last_name=yvSynonym';
      if (!hasYv) items.push({
        href: 'https://collections.yadvashem.org/' + L + '/names/search-results-names?' + yq,
        key: 'yvSearchName', prefilled: true, q: q
      });
    } else if (!hasYv) {
      items.push({ href: 'https://collections.yadvashem.org/' + L + '/names/search-results-names', key: 'yvSearch', prefilled: false });
    }

    // USHMM búsqueda nueva: ?any_first_name=&any_last_name=.
    // Sin año a propósito (comprobado 2026-11-17): con birth_year exacto «Clara Beschütz» 1876 da 0
    // (es de 1877); birth_year_range=1 sí funciona (5 resultados), pero los registros sin año de
    // nacimiento quedan fuera: «Carla Levy» da 4 resultados sin año y 0 con 1912 ±1.
    // No usamos la interfaz antigua /online/hsv/ para buscar (anunciada para desaparecer en otoño 2026).
    if (parsed && parsed.last && parsed.first) {
      let uq = '';
      if (parsed.first) uq += 'any_first_name=' + encodeURIComponent(parsed.first) + '&';
      uq += 'any_last_name=' + encodeURIComponent(parsed.last);
      if (!hasUs) items.push({
        href: 'https://www.ushmm.org/remember/resources-holocaust-survivors-victims/database-of-holocaust-survivor-and-victim-names/search-names?' + uq,
        key: 'ushmmSearchName', prefilled: true, q: q
      });
    } else if (!hasUs) {
      items.push({
        href: 'https://www.ushmm.org/remember/resources-holocaust-survivors-victims/database-of-holocaust-survivor-and-victim-names/search-names',
        key: 'ushmmSearch', prefilled: false
      });
    }

    // Gedenkbuch: la búsqueda oficial es un formulario JSF en apps.bundesarchiv.de.
    // ?name= NO rellena el campo ni lanza la búsqueda (comprobado 2026-11-16).
    // Enlazamos la página de búsqueda, sin fingir un deep link.
    if (!hasGb) {
      items.push({ href: 'https://apps.bundesarchiv.de/gedenkbuch/' + L, key: 'gbSearchPage', prefilled: false });
    }

    // Iniciativas urbanas, solo si la ciudad de nuestros datos es Hamburgo o Berlín.
    // Hamburg name= (sin «geb. …»): Löpert 1, Frankenthal 1, Gertrud Böhm 1.
    // «Gertrud Böhm geb. Cohn» en name= no encontró nada; por eso se envía First Last.
    // Berlin ?name=: Bukofzer / Abraham Bukofzer / Abraham A. Bukofzer / Abel Bernhard Schaefer, comprobado.
    // No hay ruta /es/ en esos sitios (404); DE o EN según el idioma de la interfaz.
    if (q && city === 'hamburg') {
      const hh = (uiLang === 'en')
        ? 'https://stolpersteine-hamburg.de/en/results?name=' + encodeURIComponent(q)
        : 'https://stolpersteine-hamburg.de/suchergebnisse?name=' + encodeURIComponent(q);
      items.push({ href: hh, key: 'hhSearchName', prefilled: true, q: q });
    }
    if (q && city === 'berlin') {
      const be = (uiLang === 'en')
        ? 'https://www.stolpersteine-berlin.de/en/finding-stolpersteine?name=' + encodeURIComponent(q)
        : 'https://www.stolpersteine-berlin.de/de/stolpersteine-finden?name=' + encodeURIComponent(q);
      items.push({ href: be, key: 'beSearchName', prefilled: true, q: q });
    }

    return items;
  }

  const api = { parsePersonName: parsePersonName, isCollectiveName: isCollectiveName, safeUrl: safeUrl, birthYear: birthYear, cityKey: cityKey, archiveLang: archiveLang, sourceSearchList: sourceSearchList };
  root.KLSourceLinks = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
