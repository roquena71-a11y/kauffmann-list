const I18N = {
  es: {
    title:'Lista Kauffmann', subtitle:'Stolpersteine en Alemania · Un nombre, una vida.',
    searchLabel:'Buscar por nombre', searchPh:'Nombre, apellido o calle…', cityLabel:'Lugar', cityPh:'Filtrar por lugar (opcional)',
    loading:'Cargando las placas…', ready:n=>`${n} placas en el mapa. Escriba un nombre para buscar.`,
    results:(n,more)=>`${n}${more?'+':''} resultado${n===1?'':'s'}`, none:'Sin resultados. Pruebe otra grafía, solo el apellido, o quite el filtro de lugar.',
    similar:'(grafías parecidas)', back:'← Volver a los resultados', inscription:'Inscripción de la placa', address:'Dirección', place:'Lugar', district:'Barrio',
    born:'Nacimiento', died:'Muerte', laid:'Placa colocada', type:'Tipo', threshold:'Stolperschwelle (umbral conmemorativo)',
    photo:'Foto de la placa: Wikimedia Commons — ver autor y licencia', bio:'Biografía y fuentes', research:'Buscar en archivos y memoriales',
    researchNote:'Los enlaces directos solo aparecen cuando la ficha ya está vinculada en Wikidata. Los demás abren el buscador del archivo; copie el nombre para buscar.',
    gb:'Libro Conmemorativo del Archivo Federal Alemán (Gedenkbuch)', yv:'Yad Vashem — Base central de nombres de víctimas de la Shoá', ushmm:'USHMM — Base de sobrevivientes y víctimas', arolsen:'Arolsen Archives',
    gbSearch:'Buscar en el Gedenkbuch', yvSearch:'Buscar en Yad Vashem', ushmmSearch:'Buscar en USHMM', arolsenSearch:'Buscar en Arolsen Archives',
    share:'Copiar enlace a esta placa', copied:'Enlace copiado', copyName:'Copiar nombre', nameCopied:'Nombre copiado',
    directions:'Cómo llegar (Google Maps)', osmDir:'Cómo llegar (OpenStreetMap)', sources:'Fuentes de esta ficha', derived:'(lugar deducido de placas cercanas)',
    about:'Acerca de los datos', close:'Cerrar', noinsc:'No hay transcripción de la inscripción en las fuentes.',
    attribution:'Datos: © <a href="https://www.openstreetmap.org/copyright">colaboradores de OpenStreetMap</a> (ODbL) y <a href="https://www.wikidata.org">Wikidata</a> (CC0). Mapa base © OpenStreetMap.',
    aboutHtml:m=>`<h2>Acerca de este mapa</h2><p>Los <em>Stolpersteine</em> («piedras de tropiezo») son placas de latón del artista Gunter Demnig, colocadas frente al último domicilio elegido libremente por personas perseguidas, deportadas o asesinadas por el nazismo.</p>
      <p>Este mapa reúne <strong>${m.count}</strong> placas en Alemania a partir de datos abiertos: OpenStreetMap (instantánea ${m.osm_snapshot}) y Wikidata (${m.wikidata_snapshot}). <strong>No están todas</strong>: según la Stiftung Spuren – Gunter Demnig hay más de 116.000 Stolpersteine en Europa, la mayoría en Alemania, y muchas aún no están registradas en datos abiertos. Si no encuentra a su familiar, consulte también <a href="https://www.stolpersteine.eu">stolpersteine.eu</a> y las iniciativas locales (p. ej. <a href="https://www.stolpersteine-berlin.de">Berlín</a>, <a href="https://www.stolpersteine-hamburg.de">Hamburgo</a>).</p>
      <p>Ningún dato ha sido inventado: cada campo procede de las fuentes citadas. Pueden existir errores o duplicados; las correcciones se hacen en OpenStreetMap o Wikidata.</p>
      <p>Licencia de la base de datos: <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a>. Fotos: Wikimedia Commons, cada una con su propia licencia.</p>`
  },
  de: {
    title:'Kauffmann-Liste', subtitle:'Stolpersteine in Deutschland · Ein Name, ein Leben.',
    searchLabel:'Nach Namen suchen', searchPh:'Vorname, Nachname oder Straße…', cityLabel:'Ort', cityPh:'Nach Ort filtern (optional)',
    loading:'Stolpersteine werden geladen…', ready:n=>`${n} Stolpersteine auf der Karte. Geben Sie einen Namen ein.`,
    results:(n,more)=>`${n}${more?'+':''} Treffer`, none:'Keine Treffer. Versuchen Sie eine andere Schreibweise, nur den Nachnamen oder entfernen Sie den Ortsfilter.',
    similar:'(ähnliche Schreibweisen)', back:'← Zurück zu den Treffern', inscription:'Inschrift', address:'Adresse', place:'Ort', district:'Stadtteil',
    born:'Geboren', died:'Gestorben', laid:'Verlegt', type:'Art', threshold:'Stolperschwelle',
    photo:'Foto des Steins: Wikimedia Commons — Urheber und Lizenz ansehen', bio:'Biografie und Quellen', research:'In Archiven und Gedenkstätten suchen',
    researchNote:'Direkte Links erscheinen nur, wenn der Eintrag bereits in Wikidata verknüpft ist. Die übrigen öffnen die Suche des Archivs; kopieren Sie den Namen.',
    gb:'Gedenkbuch des Bundesarchivs', yv:'Yad Vashem — Zentrale Datenbank der Namen der Holocaustopfer', ushmm:'USHMM — Holocaust Survivors and Victims Database', arolsen:'Arolsen Archives',
    gbSearch:'Im Gedenkbuch suchen', yvSearch:'Bei Yad Vashem suchen', ushmmSearch:'Beim USHMM suchen', arolsenSearch:'In den Arolsen Archives suchen',
    share:'Link zu diesem Stein kopieren', copied:'Link kopiert', copyName:'Namen kopieren', nameCopied:'Name kopiert',
    directions:'Route (Google Maps)', osmDir:'Route (OpenStreetMap)', sources:'Quellen dieses Eintrags', derived:'(Ort aus benachbarten Steinen abgeleitet)',
    about:'Über die Daten', close:'Schließen', noinsc:'Für diesen Stein ist in den Quellen keine Inschrift erfasst.',
    attribution:'Daten: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap-Mitwirkende</a> (ODbL) und <a href="https://www.wikidata.org">Wikidata</a> (CC0). Kartengrundlage © OpenStreetMap.',
    aboutHtml:m=>`<h2>Über diese Karte</h2><p>Stolpersteine sind Gedenktafeln aus Messing des Künstlers Gunter Demnig, verlegt vor dem letzten frei gewählten Wohnort von Menschen, die im Nationalsozialismus verfolgt, deportiert oder ermordet wurden.</p>
      <p>Diese Karte zeigt <strong>${m.count}</strong> Steine in Deutschland aus offenen Daten: OpenStreetMap (Stand ${m.osm_snapshot}) und Wikidata (${m.wikidata_snapshot}). <strong>Sie ist unvollständig</strong>: Laut Stiftung Spuren – Gunter Demnig liegen über 116.000 Stolpersteine in Europa, die meisten in Deutschland. Finden Sie einen Namen nicht, sehen Sie bitte auch bei <a href="https://www.stolpersteine.eu">stolpersteine.eu</a> und den lokalen Initiativen nach (z. B. <a href="https://www.stolpersteine-berlin.de">Berlin</a>, <a href="https://www.stolpersteine-hamburg.de">Hamburg</a>).</p>
      <p>Es wurden keine Angaben erfunden; jedes Feld stammt aus den genannten Quellen. Fehler oder Doppelungen sind möglich; Korrekturen erfolgen in OpenStreetMap bzw. Wikidata.</p>
      <p>Datenbanklizenz: <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a>. Fotos: Wikimedia Commons mit jeweils eigener Lizenz.</p>`
  },
  en: {
    title:'Kauffmann List', subtitle:'Stolpersteine in Germany · One name, one life.',
    searchLabel:'Search by name', searchPh:'First name, surname or street…', cityLabel:'Place', cityPh:'Filter by place (optional)',
    loading:'Loading stones…', ready:n=>`${n} stones on the map. Type a name to search.`,
    results:(n,more)=>`${n}${more?'+':''} result${n===1?'':'s'}`, none:'No results. Try another spelling, the surname only, or clear the place filter.',
    similar:'(similar spellings)', back:'← Back to results', inscription:'Inscription', address:'Address', place:'Place', district:'District',
    born:'Born', died:'Died', laid:'Stone laid', type:'Type', threshold:'Stolperschwelle (memorial threshold)',
    photo:'Photo of the stone: Wikimedia Commons — see author and licence', bio:'Biography and sources', research:'Search archives and memorials',
    researchNote:'Direct links appear only where the record is already linked in Wikidata. The others open the archive’s search; copy the name to search.',
    gb:'German Federal Archives Memorial Book (Gedenkbuch)', yv:'Yad Vashem — Central Database of Shoah Victims’ Names', ushmm:'USHMM — Holocaust Survivors and Victims Database', arolsen:'Arolsen Archives',
    gbSearch:'Search the Gedenkbuch', yvSearch:'Search Yad Vashem', ushmmSearch:'Search USHMM', arolsenSearch:'Search Arolsen Archives',
    share:'Copy link to this stone', copied:'Link copied', copyName:'Copy name', nameCopied:'Name copied',
    directions:'Directions (Google Maps)', osmDir:'Directions (OpenStreetMap)', sources:'Sources for this record', derived:'(place inferred from nearby stones)',
    about:'About the data', close:'Close', noinsc:'No transcription of the inscription in the sources.',
    attribution:'Data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> (ODbL) and <a href="https://www.wikidata.org">Wikidata</a> (CC0). Base map © OpenStreetMap.',
    aboutHtml:m=>`<h2>About this map</h2><p>Stolpersteine (“stumbling stones”) are brass plaques by the artist Gunter Demnig, set in front of the last freely chosen home of people persecuted, deported or murdered under National Socialism.</p>
      <p>This map shows <strong>${m.count}</strong> stones in Germany from open data: OpenStreetMap (snapshot ${m.osm_snapshot}) and Wikidata (${m.wikidata_snapshot}). <strong>It is incomplete</strong>: according to Stiftung Spuren – Gunter Demnig there are over 116,000 Stolpersteine in Europe, most of them in Germany. If you cannot find a name, please also check <a href="https://www.stolpersteine.eu">stolpersteine.eu</a> and local initiatives (e.g. <a href="https://www.stolpersteine-berlin.de">Berlin</a>, <a href="https://www.stolpersteine-hamburg.de">Hamburg</a>).</p>
      <p>No data has been invented; every field comes from the cited sources. Errors or duplicates are possible; corrections belong in OpenStreetMap or Wikidata.</p>
      <p>Database licence: <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a>. Photos: Wikimedia Commons, each under its own licence.</p>`
  }
};
/* ---- additions for the 3D view ---- */
const EXTRA = {
  es:{ remember:'Recordar a todos', baseNight:'Noche', baseDay:'Día', baseHoy:'Hoy', baseSat:'2016', sourcesBtn:'Fuentes', pause:'Pausar', resume:'Continuar', exit:'Salir',
       replay:'Introducción', project:'Sobre el proyecto', dlGeo:'Descargar GeoJSON', dlKml:'Descargar KML',
       classic:'Mapa clásico 2D', searchPh:'Nombre, apellido o dirección (calle y ciudad)…',
       vigilCount:n=>`${n} nombres`, vigilText:'Cada columna dorada recuerda a una persona, frente a la casa donde vivió. En silencio, recordamos sus nombres.',
       vigilPlace:(p,n)=>`${p} · ${n} placas`,
       nogl:'Este dispositivo no puede mostrar el mapa 3D. <a href="2d/">Abrir el mapa clásico 2D</a>.',
       aggHint:'Acerque el mapa para ver cada placa',
       story:'Su historia', archives:'Archivos', perInscription:'según la inscripción',
       noStory:'Todavía no tenemos su historia.', helpUs:'¿La conoce? Ayúdenos',
       anonNote:'Esta placa está anonimizada. No añadimos nada que no esté escrito en la piedra.',
       wpCite:'Texto de Wikipedia, sin cambios.', wpAuthors:'Autores de Wikipedia', wpRev:'revisión',
       berlinBio:'Biografía oficial, Stolpersteine Berlin', hamburgBio:'Biografía oficial, Stolpersteine Hamburg', bremenBio:'Biografía oficial, Stolpersteine Bremen',
       describedAt:'Enlace citado en Wikidata', contribNote:'El formulario para aportar o corregir una historia todavía no está abierto. Esta página no se ha publicado.',
       attribution3d:'Datos: © <a href="https://www.openstreetmap.org/copyright">colaboradores de OpenStreetMap</a> (ODbL) y <a href="https://www.wikidata.org">Wikidata</a> (CC0). Mapa base: <a href="https://openfreemap.org">OpenFreeMap</a> © OpenMapTiles.' },
  de:{ remember:'Aller gedenken', baseNight:'Nacht', baseDay:'Tag', baseHoy:'Heute', baseSat:'2016', sourcesBtn:'Quellen', pause:'Anhalten', resume:'Fortsetzen', exit:'Beenden',
       replay:'Einführung', project:'Über das Projekt', dlGeo:'GeoJSON herunterladen', dlKml:'KML herunterladen',
       classic:'Klassische 2D-Karte', searchPh:'Vorname, Nachname oder Adresse (Straße und Ort)…',
       vigilCount:n=>`${n} Namen`, vigilText:'Jede goldene Säule erinnert an einen Menschen, vor dem Haus, in dem er lebte. In Stille gedenken wir ihrer Namen.',
       vigilPlace:(p,n)=>`${p} · ${n} Steine`,
       nogl:'Dieses Gerät kann die 3D-Karte nicht anzeigen. <a href="2d/">Klassische 2D-Karte öffnen</a>.',
       aggHint:'Hineinzoomen, um jeden Stein zu sehen',
       story:'Die Geschichte', archives:'Archive', perInscription:'laut Inschrift',
       noStory:'Wir haben die Geschichte noch nicht.', helpUs:'Kennen Sie sie? Helfen Sie uns',
       anonNote:'Dieser Stein ist anonymisiert. Wir fügen nichts hinzu, was nicht auf dem Stein steht.',
       wpCite:'Wikipedia-Text, unverändert.', wpAuthors:'Wikipedia-Autorinnen und Autoren', wpRev:'Version',
       berlinBio:'Offizielle Biografie, Stolpersteine Berlin', hamburgBio:'Offizielle Biografie, Stolpersteine Hamburg', bremenBio:'Offizielle Biografie, Stolpersteine Bremen',
       describedAt:'Bei Wikidata genannter Link', contribNote:'Das Formular für Ergänzungen und Korrekturen ist noch nicht geöffnet. Diese Seite ist nicht veröffentlicht.',
       attribution3d:'Daten: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap-Mitwirkende</a> (ODbL) und <a href="https://www.wikidata.org">Wikidata</a> (CC0). Karte: <a href="https://openfreemap.org">OpenFreeMap</a> © OpenMapTiles.' },
  en:{ remember:'Remember them all', baseNight:'Night', baseDay:'Day', baseHoy:'Today', baseSat:'2016', sourcesBtn:'Sources', pause:'Pause', resume:'Resume', exit:'Exit',
       replay:'Introduction', project:'About the project', dlGeo:'Download GeoJSON', dlKml:'Download KML',
       classic:'Classic 2D map', searchPh:'First name, surname or address (street and city)…',
       vigilCount:n=>`${n} names`, vigilText:'Each golden column remembers one person, in front of the home where they lived. In silence, we remember their names.',
       vigilPlace:(p,n)=>`${p} · ${n} stones`,
       nogl:'This device cannot display the 3D map. <a href="2d/">Open the classic 2D map</a>.',
       aggHint:'Zoom in to see each stone',
       story:'Their story', archives:'Archives', perInscription:'as on the inscription',
       noStory:'We do not yet have their story.', helpUs:'Do you know it? Help us',
       anonNote:'This plaque is anonymised. We add nothing that is not written on the stone.',
       wpCite:'Wikipedia text, unchanged.', wpAuthors:'Wikipedia authors', wpRev:'revision',
       berlinBio:'Official biography, Stolpersteine Berlin', hamburgBio:'Official biography, Stolpersteine Hamburg', bremenBio:'Official biography, Stolpersteine Bremen',
       describedAt:'Link recorded in Wikidata', contribNote:'The form for contributions and corrections is not open yet. This site has not been published.',
       attribution3d:'Data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> (ODbL) and <a href="https://www.wikidata.org">Wikidata</a> (CC0). Base map: <a href="https://openfreemap.org">OpenFreeMap</a> © OpenMapTiles.' }
};
for (const l in EXTRA) Object.assign(I18N[l], EXTRA[l]);
Object.assign(I18N.es, {pitchTo3d:'Ver en ángulo (3D)', pitchTo2d:'Ver desde arriba (2D)', pitchFlatOnly:'La foto de 1945 se ve solo desde arriba', rotLeft:'Girar a la izquierda', rotNorth:'Mirar al norte', rotRight:'Girar a la derecha'});
Object.assign(I18N.de, {pitchTo3d:'Schräg ansehen (3D)', pitchTo2d:'Von oben ansehen (2D)', pitchFlatOnly:'Das Luftbild von 1945 gibt es nur von oben', rotLeft:'Nach links drehen', rotNorth:'Nach Norden ausrichten', rotRight:'Nach rechts drehen'});
Object.assign(I18N.en, {pitchTo3d:'View at an angle (3D)', pitchTo2d:'View from above (2D)', pitchFlatOnly:'The 1945 photo can only be viewed from above', rotLeft:'Rotate left', rotNorth:'Face north', rotRight:'Rotate right'});

let lang = (new URLSearchParams(location.search).get('lang') || localStorage.getItem('lang') || (navigator.language||'es').slice(0,2));
if (!I18N[lang]) lang = 'es';
const T = k => I18N[lang][k];
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmtNum = n => n.toLocaleString(lang === 'en' ? 'en' : lang === 'de' ? 'de' : 'es');
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

function applyI18n(){
  document.documentElement.lang = lang;
  document.querySelectorAll('[data-i18n]').forEach(el => { const v=T(el.dataset.i18n); if (typeof v==='string') el.textContent=v; });
  document.querySelectorAll('[data-i18n-ph]').forEach(el => el.placeholder = T(el.dataset.i18nPh));
  document.querySelectorAll('[data-i18n-html]').forEach(el => el.innerHTML = T(el.dataset.i18nHtml));
  document.querySelectorAll('.lang button').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === lang));
  document.title = T('title');
  if (typeof updatePitchBtn === 'function') updatePitchBtn();
  if (window.KLCols && KLCols.relabel) KLCols.relabel();
}

/* ---------- search (same rules as the 2D map) ---------- */
function norm(s){
  return String(s||'').toLowerCase().replace(/ß/g,'ss').replace(/ä/g,'a').replace(/ö/g,'o').replace(/ü/g,'u')
    .normalize('NFD').replace(/[\u0300-\u036f]/g,'')
    .replace(/ae/g,'a').replace(/oe/g,'o').replace(/ue/g,'u')
    .replace(/str\b/g,'strasse')                       // "Ritterstr" = "Ritterstraße"
    .replace(/[^a-z0-9]+/g,' ').trim();
}
function lev(a,b,max){
  if (Math.abs(a.length-b.length)>max) return max+1;
  let prev=Array.from({length:b.length+1},(_,i)=>i);
  for (let i=1;i<=a.length;i++){
    const cur=[i]; let best=i;
    for (let j=1;j<=b.length;j++){ cur[j]=Math.min(prev[j]+1,cur[j-1]+1,prev[j-1]+(a[i-1]===b[j-1]?0:1)); if (cur[j]<best) best=cur[j]; }
    if (best>max) return max+1; prev=cur;
  }
  return prev[b.length];
}

/* ---------- state ---------- */
var map; let DATA=[], META={}, byId=new Map(), VISIBLE=[], selected=null, base='night', AGG=[], STONES_FC=null, POINTS_FC=null, LIGHTS_FC=null, CITY_STATS=[];
const cityOf = s => s.c || s.cd || '';

/* ---------- geometry ---------- */
const M_LAT = 111320;
function square(lo, la, halfM, ang){
  const mLa = 1/M_LAT, mLo = 1/(M_LAT*Math.cos(la*Math.PI/180));
  const cA = Math.cos(ang||0), sA = Math.sin(ang||0);
  const pts = [[-halfM,-halfM],[halfM,-halfM],[halfM,halfM],[-halfM,halfM],[-halfM,-halfM]];
  return [pts.map(([x,y]) => [lo + (x*cA - y*sA)*mLo, la + (x*sA + y*cA)*mLa])];
}
// Individual columns: stones of the same house are laid out as a neat grid around the true point
// (same size everywhere: 1.20 m wide, 16 m tall). The detail panel and directions still use the recorded coordinates.
const COL_HALF = 0.60, COL_STEP = 1.85, COL_H = 16, COL_GAP_MIN = 1.55;
function addrKey(s){
  const fold = t => (t||'').toLowerCase().replace(/ß/g,'ss').replace(/ä/g,'ae').replace(/ö/g,'oe').replace(/ü/g,'ue');
  let a = fold(s.a)
    .replace(/\b\d{5}\b/g,'')
    .replace(/\b(deutschland|germany)\b/g,'')
    .replace(/[.,;/]/g,' ')
    .replace(/\bstr(?:asse)?\./g,'strasse ')
    .replace(/([a-z])str\b/g,'$1strasse')
    .replace(/\bstr\b/g,'strasse')
    .replace(/\s+/g,' ').trim();
  // Keep street + house number; drop trailing place names so "… 14, Berlin-Tempelhof" matches "… 14".
  const m = a.match(/^(.*?)(\d+\s*[a-z]?)(?:\s+|$)/);
  if (m) a = (m[1]+m[2]).replace(/\s+/g,' ').trim();
  return a;
}
function streetKey(s){ return addrKey(s).replace(/\d+\s*[a-z]?$/i,'').trim(); }
function distM(la1,lo1,la2,lo2){
  const mid = (la1+la2)/2 * Math.PI/180;
  return Math.hypot((la1-la2)*M_LAT, (lo1-lo2)*M_LAT*Math.cos(mid));
}
function clusterByDist(list, maxD){
  const n = list.length;
  if (!n) return [];
  if (n === 1) return [list.slice()];
  const parent = list.map((_,i)=>i);
  const find = i => parent[i]===i ? i : (parent[i]=find(parent[i]));
  for (let i=0;i<n;i++) for (let j=i+1;j<n;j++)
    if (distM(list[i].la,list[i].lo,list[j].la,list[j].lo) <= maxD){
      const a=find(i), b=find(j); if (a!==b) parent[a]=b;
    }
  const m = new Map();
  list.forEach((s,i)=> (m.get(find(i)) || m.set(find(i),[]).get(find(i))).push(s));
  return [...m.values()];
}
function yearOf(v){ const m = String(v||'').match(/(1[7-9]|20)\d{2}/); return m ? m[0] : ''; }
function nameKey(s){
  let n = (s.n||'').toLowerCase().replace(/ß/g,'ss').replace(/ä/g,'ae').replace(/ö/g,'oe').replace(/ü/g,'ue');
  n = n.replace(/\b(dr|prof|med)\.?\b/g,'').replace(/[.,]/g,' ').replace(/\s+/g,' ').trim();
  return n;
}
function nameCore(s){ return nameKey(s).replace(/\s+(?:geb|geboren|nee|née)\b.*/,'').trim(); }
function isGenericName(s){
  if (typeof isAnonStone === 'function' && isAnonStone(s)) return true;
  return /^(ein[e]?\s+)?(romm|rommni|sinto|sinteza|sintiza)(\s|$)/i.test(nameKey(s));
}
function yearsCompatible(a,b){
  const ba=a._by!=null?a._by:yearOf(a.b), bb=b._by!=null?b._by:yearOf(b.b); if (ba && bb && ba!==bb) return false;
  const da=a._dy!=null?a._dy:yearOf(a.d), db=b._dy!=null?b._dy:yearOf(b.d); if (da && db && da!==db) return false;
  return true;
}
function samePerson(a,b){
  if ((a._generic!=null?a._generic:isGenericName(a)) || (b._generic!=null?b._generic:isGenericName(b))) return false;
  const ka=a._nk!=null?a._nk:nameKey(a), kb=b._nk!=null?b._nk:nameKey(b);
  if (!ka || ka.length<3 || !kb) return false;
  if (ka===kb) return yearsCompatible(a,b);
  const ca=a._core!=null?a._core:nameCore(a), cb=b._core!=null?b._core:nameCore(b);
  if (ca && ca.length>=5 && ca===cb) return yearsCompatible(a,b);
  return false;
}
function richness(s){
  let n=0;
  if (s.i) n+=3; if (s.img) n+=2; if (s.b) n+=2; if (s.d) n+=1;
  if (s.wd) n+=2; if (s.src && String(s.src).includes('osm')) n+=1;
  if (s.w && s.w.length) n+=1; if (s.wp) n+=1; if (s.p) n+=1;
  return n;
}
function fillFrom(pri, o){
  if (!pri.b && o.b) pri.b = o.b;
  if (!pri.d && o.d) pri.d = o.d;
  if (!pri.i && o.i) pri.i = o.i;
  if (!pri.img && o.img) pri.img = o.img;
  if (!pri.wd && o.wd) pri.wd = o.wd;
  if (!pri.p && o.p) pri.p = o.p;
  if (!pri.a && o.a) pri.a = o.a;
  if (!pri.c && o.c) pri.c = o.c;
  if (!pri.laid && o.laid) pri.laid = o.laid;
  if (!pri.wp && o.wp) pri.wp = o.wp;
  if ((!pri.w || !pri.w.length) && o.w && o.w.length) pri.w = o.w;
  if ((o.n||'').length > (pri._n||pri.n||'').length) pri._n = o.n;
}
function principalAngle(pts){
  if (pts.length<2) return null;
  const la0=pts.reduce((t,p)=>t+p.la,0)/pts.length, lo0=pts.reduce((t,p)=>t+p.lo,0)/pts.length;
  const cos=Math.cos(la0*Math.PI/180);
  const xy=pts.map(p=>({x:(p.lo-lo0)*M_LAT*cos, y:(p.la-la0)*M_LAT}));
  let xx=0, yy=0, xyC=0;
  for (const p of xy){ xx+=p.x*p.x; yy+=p.y*p.y; xyC+=p.x*p.y; }
  const n=xy.length, tr=xx+yy, disc=Math.sqrt(Math.max(0,(xx-yy)*(xx-yy)/4 + xyC*xyC));
  const ev1=tr/2+disc, ev2=tr/2-disc;
  const lenMaj=Math.sqrt(Math.max(0,ev1)/n)*2, lenMin=Math.sqrt(Math.max(0,ev2)/n)*2;
  if (lenMaj<4 || lenMaj<2.2*Math.max(lenMin,0.8)) return null;
  let ang=0.5*Math.atan2(2*xyC, xx-yy);
  if (ang<0) ang+=Math.PI;
  return ang;
}

function buildStones(){
  for (const s of DATA){
    s._nk = nameKey(s);
    s._core = nameCore(s);
    s._generic = isGenericName(s);
    s._by = yearOf(s.b);
    s._dy = yearOf(s.d);
  }
  const byAddr = new Map(), noAddr = [];
  for (const s of DATA){
    const k = addrKey(s);
    if (!k) noAddr.push(s);
    else (byAddr.get(k) || byAddr.set(k,[]).get(k)).push(s);
  }
  let clusters = [];
  for (const list of byAddr.values()) clusters.push(...clusterByDist(list, 15));
  clusters.push(...clusterByDist(noAddr, 3.5));
  // Same recorded point, different wording of the address (or a shared wrong coordinate):
  // join them so the columns form one grid instead of sitting on top of each other.
  {
    const parent=clusters.map((_,i)=>i);
    const find=i=>parent[i]===i?i:(parent[i]=find(parent[i]));
    const cents=clusters.map(g=>({la:g.reduce((t,s)=>t+s.la,0)/g.length, lo:g.reduce((t,s)=>t+s.lo,0)/g.length}));
    const cell=0.00002, grid=new Map(); // ~2 m cells
    const key=(la,lo)=>Math.floor(la/cell)+':'+Math.floor(lo/cell);
    cents.forEach((c,i)=>{ const k=key(c.la,c.lo); (grid.get(k)||grid.set(k,[]).get(k)).push(i); });
    cents.forEach((c,i)=>{
      const a0=Math.floor(c.la/cell), b0=Math.floor(c.lo/cell);
      for (let di=-1;di<=1;di++) for (let dj=-1;dj<=1;dj++)
        for (const j of (grid.get((a0+di)+':'+(b0+dj))||[])){
          if (j<=i) continue;
          if (distM(c.la,c.lo,cents[j].la,cents[j].lo)<0.8){ const a=find(i), b=find(j); if (a!==b) parent[a]=b; }
        }
    });
    const m=new Map();
    clusters.forEach((g,i)=> (m.get(find(i))||m.set(find(i),[]).get(find(i))).push(...g));
    clusters=[...m.values()];
  }

  // Display-only merge: same person (same name at the same house, dates not in conflict).
  // stones.json is not changed; aliases stay in DATA/byId so a link to either id still opens the ficha.
  // Merge on the address group with a 25 m cap (OSM and Wikidata of the same house are often 15–20 m apart).
  let mergeGroups=0, mergeExtra=0;
  function mergePeople(list, maxD){
    if (list.length<2) return;
    const parent=list.map((_,i)=>i);
    const find=i=>parent[i]===i?i:(parent[i]=find(parent[i]));
    const tryPair=(i,j)=>{
      if (samePerson(list[i], list[j]) && distM(list[i].la,list[i].lo,list[j].la,list[j].lo)<=maxD){
        const a=find(i), b=find(j); if (a!==b) parent[a]=b;
      }
    };
    if (list.length<=40){
      for (let i=0;i<list.length;i++) for (let j=i+1;j<list.length;j++) tryPair(i,j);
    } else {
      const cell=0.00015, grid=new Map();
      const key=(la,lo)=>Math.floor(la/cell)+':'+Math.floor(lo/cell);
      list.forEach((s,i)=>{ const k=key(s.la,s.lo); (grid.get(k)||grid.set(k,[]).get(k)).push(i); });
      list.forEach((s,i)=>{
        const a=Math.floor(s.la/cell), b=Math.floor(s.lo/cell);
        for (let di=-1;di<=1;di++) for (let dj=-1;dj<=1;dj++)
          for (const j of (grid.get((a+di)+':'+(b+dj))||[])) if (j>i) tryPair(i,j);
      });
    }
    const buckets=new Map();
    list.forEach((s,i)=> (buckets.get(find(i))||buckets.set(find(i),[]).get(find(i))).push(s));
    for (const recs of buckets.values()){
      if (recs.length<2) continue;
      recs.sort((a,b)=> richness(b)-richness(a) || String(a.id).localeCompare(String(b.id)));
      const pri=recs[0];
      pri._also=recs.slice(1);
      pri._ids=recs.map(s=>s.id);
      pri._n=pri.n;
      for (const o of pri._also){ o._aliasOf=pri.id; fillFrom(pri, o); }
      mergeGroups++; mergeExtra+=recs.length-1;
    }
  }
  for (const list of byAddr.values()) mergePeople(list, 25);
  mergePeople(noAddr, 8);

  const groups = clusters.map(g => {
    const vis=g.filter(s=>!s._aliasOf);
    vis.sort((a,b)=> ((a._n||a.n)||'').localeCompare((b._n||b.n)||'','de') || String(a.id).localeCompare(String(b.id)));
    const la0 = g.reduce((t,s)=>t+s.la,0)/g.length;
    const lo0 = g.reduce((t,s)=>t+s.lo,0)/g.length;
    return {g:vis, all:g, la0, lo0, origLa:la0, origLo:lo0, step:COL_STEP, ang:0, sk:streetKey(g[0])};
  });

  // Street direction from our own coordinates (not live OSM tiles: those are only in the current view
  // after the style loads, so they cannot lay out the whole country at start).
  // 1) Principal axis of other houses on the same street within 180 m (needs 3 points, or 2 if >12 m apart).
  // 2) If that fails, the elongated cloud of this house's own recorded points.
  // 3) Smooth with the circular mean of neighbouring angles on the same street (80 m), then north–south if still none.
  function neighbors(pg, i, radius, cell, near){
    const pts=[], idxs=[];
    if (!pg.sk) return {pts, idxs};
    const a0=Math.floor(pg.la0/cell), b0=Math.floor(pg.lo0/cell);
    for (let di=-2;di<=2;di++) for (let dj=-2;dj<=2;dj++)
      for (const j of (near.get(pg.sk+'|'+((a0+di)+':'+(b0+dj)))||[])){
        const o=groups[j];
        if (distM(pg.la0,pg.lo0,o.la0,o.lo0)<=radius){ pts.push({la:o.la0, lo:o.lo0}); idxs.push(j); }
      }
    return {pts, idxs};
  }
  function meanAngle(angs){
    if (!angs.length) return null;
    let x=0,y=0;
    for (const a of angs){ x+=Math.cos(2*a); y+=Math.sin(2*a); }
    let m=0.5*Math.atan2(y,x); if (m<0) m+=Math.PI; return m;
  }
  const cellA=0.001, near=new Map();
  const akey=(sk,la,lo)=>sk+'|'+Math.floor(la/cellA)+':'+Math.floor(lo/cellA);
  groups.forEach((pg,i)=>{ if (!pg.sk) return; const k=akey(pg.sk,pg.la0,pg.lo0); (near.get(k)||near.set(k,[]).get(k)).push(i); });
  groups.forEach((pg,i)=>{
    let ang=null;
    if (pg.sk){
      const {pts}=neighbors(pg,i,180,cellA,near);
      if (pts.length>=3) ang=principalAngle(pts);
      else if (pts.length===2 && distM(pts[0].la,pts[0].lo,pts[1].la,pts[1].lo)>12) ang=principalAngle(pts);
    }
    if (ang==null) ang=principalAngle(pg.all.map(s=>({la:s.la, lo:s.lo})));
    pg._rawAng = ang;
  });
  groups.forEach((pg,i)=>{
    let ang=pg._rawAng;
    if (pg.sk){
      const {idxs}=neighbors(pg,i,80,cellA,near);
      const angs=idxs.map(j=>groups[j]._rawAng).filter(a=>a!=null);
      if (angs.length>=2) ang=meanAngle(angs);
    }
    pg.ang = ang||0;
    for (const s of pg.all) s._ang=pg.ang;
  });

  function layout(pg){
    const n=pg.g.length, cols=Math.ceil(Math.sqrt(n));
    const rows=Math.ceil(n/cols)||1;
    const cos=Math.cos(pg.la0*Math.PI/180), cA=Math.cos(pg.ang||0), sA=Math.sin(pg.ang||0);
    pg.g.forEach((s,i)=>{
      const cx=(i%cols)-(cols-1)/2, cy=Math.floor(i/cols)-(rows-1)/2;
      const east=cx*pg.step*cA - cy*pg.step*sA;
      const north=cx*pg.step*sA + cy*pg.step*cA;
      s._dla = pg.la0 + north/M_LAT;
      s._dlo = pg.lo0 + east/(M_LAT*cos);
    });
  }
  for (const pg of groups) layout(pg);

  // If two houses sit very close, shrink the grid a little and nudge the smaller field so columns never overlap.
  // Do not move a field more than 8 m from its recorded point.
  const maxShift = 8;
  for (let iter=0; iter<16; iter++){
    const cell=0.0002, grid=new Map();
    const key=(la,lo)=>Math.floor(la/cell)+':'+Math.floor(lo/cell);
    groups.forEach((pg,gi)=> pg.g.forEach(s=>{
      const k=key(s._dla,s._dlo); (grid.get(k)||grid.set(k,[]).get(k)).push({s,gi});
    }));
    const shift = groups.map(()=>({dy:0,dx:0,hits:0}));
    const shrink = groups.map(()=>false);
    let moved=false;
    groups.forEach((pg,gi)=> pg.g.forEach(s=>{
      const a=Math.floor(s._dla/cell), b=Math.floor(s._dlo/cell);
      for (let di=-1;di<=1;di++) for (let dj=-1;dj<=1;dj++)
        for (const o of (grid.get((a+di)+':'+(b+dj))||[])){
          if (o.gi<=gi) continue;
          const d=distM(s._dla,s._dlo,o.s._dla,o.s._dlo);
          if (d>=COL_GAP_MIN) continue;
          const A=groups[gi], B=groups[o.gi];
          let dy=(A.la0-B.la0)*M_LAT, dx=(A.lo0-B.lo0)*M_LAT*Math.cos(A.la0*Math.PI/180);
          let L=Math.hypot(dx,dy);
          if (L<0.2){ dx=1; dy=0; L=1; }
          const push=(COL_GAP_MIN-d+0.12)/2;
          const uy=dy/L, ux=dx/L;
          if (A.g.length<=B.g.length){ shift[gi].dy+=uy*push; shift[gi].dx+=ux*push; shift[gi].hits++; }
          else { shift[o.gi].dy-=uy*push; shift[o.gi].dx-=ux*push; shift[o.gi].hits++; }
          if (L<5 && (A.g.length>1 || B.g.length>1)){ shrink[gi]=true; shrink[o.gi]=true; }
          moved=true;
        }
    }));
    if (!moved) break;
    groups.forEach((pg,i)=>{
      if (shrink[i] && pg.step>1.50) pg.step=Math.max(1.50, pg.step-0.08);
      if (shift[i].hits){
        const mLa=1/M_LAT, mLo=1/(M_LAT*Math.cos(pg.la0*Math.PI/180));
        let nla=pg.la0+shift[i].dy*mLa, nlo=pg.lo0+shift[i].dx*mLo;
        const sh=distM(nla,nlo,pg.origLa,pg.origLo);
        if (sh>maxShift){ const k=maxShift/sh; nla=pg.origLa+(nla-pg.origLa)*k; nlo=pg.origLo+(nlo-pg.origLo)*k; }
        pg.la0=nla; pg.lo0=nlo;
      }
      if (shrink[i] || shift[i].hits) layout(pg);
    });
  }

  for (const s of DATA){
    if (s._aliasOf){ const p=byId.get(s._aliasOf); if (p){ s._dla=p._dla; s._dlo=p._dlo; s._ang=p._ang; } }
  }
  VISIBLE = DATA.filter(s=>!s._aliasOf);
  const feats = VISIBLE.map(s => ({type:'Feature', properties:{id:s.id}, geometry:{type:'Polygon', coordinates:square(s._dlo,s._dla,COL_HALF,s._ang)}}));
  STONES_FC = {type:'FeatureCollection', features:feats};
  POINTS_FC = {type:'FeatureCollection', features: VISIBLE.map(s=>({type:'Feature', properties:{}, geometry:{type:'Point', coordinates:[s.lo,s.la]}}))};
  LIGHTS_FC = {type:'FeatureCollection', features: groups.map(pg=>({type:'Feature', properties:{n:pg.g.length}, geometry:{type:'Point', coordinates:[pg.lo0, pg.la0]}}))};
  const ise69 = VISIBLE.filter(s => /Isestr/i.test(s.a||'') && /\b69\b/.test(s.a||'')).length;
  var KLMerge = {groups:mergeGroups, extra:mergeExtra, visible:VISIBLE.length, source:DATA.length, isestr69:ise69};
  if (typeof window!=='undefined') window.KLMerge = KLMerge;
}

// Aggregated columns per grid cell, one level per zoom band. Height ~ sqrt(count) so Berlin does not hide small towns.
const LEVELS = [
  {id:'a0', dLa:0.25,  dLo:0.40,   min:0,    max:7.5,  k:1500, half:1500},
  {id:'a1', dLa:0.06,  dLo:0.095,  min:7.5,  max:9.5,  k:750,  half:420},
  {id:'a2', dLa:0.015, dLo:0.024,  min:9.5,  max:11.8, k:320,  half:110},
  {id:'a3', dLa:0.004, dLo:0.0064, min:11.8, max:14.6, k:70,   half:28},
];
function buildAgg(){
  const rows = (VISIBLE && VISIBLE.length) ? VISIBLE : DATA;
  AGG = LEVELS.map(L=>{
    const cells = new Map();
    for (const s of rows){
      const k = Math.floor(s.la/L.dLa)+':'+Math.floor(s.lo/L.dLo);
      let c = cells.get(k); if (!c) cells.set(k, c={n:0,la:0,lo:0});
      c.n++; c.la+=s.la; c.lo+=s.lo;
    }
    const feats = [...cells.values()].map(c=>{
      const la=c.la/c.n, lo=c.lo/c.n;
      return {type:'Feature', properties:{n:c.n, h:Math.round(L.k*Math.sqrt(c.n)), la, lo},
              geometry:{type:'Polygon', coordinates:square(lo,la,L.half*Math.min(1.3,0.6+0.1*Math.log(c.n+1)))}};
    });
    return {L, fc:{type:'FeatureCollection', features:feats}};
  });
}

/* ---------- base maps ---------- */
const OFM = 'https://tiles.openfreemap.org/styles/';
function satStyle(){
  return {version:8, glyphs:'https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf',
    sources:{eox:{type:'raster', tileSize:256, maxzoom:15,
      tiles:['https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/GoogleMapsCompatible/{z}/{y}/{x}.jpg'],
      attribution:'<a href="https://s2maps.eu">Sentinel-2 cloudless</a> by EOX IT Services GmbH (contains modified Copernicus Sentinel data 2016), CC BY 4.0'}},
    layers:[{id:'bg',type:'background',paint:{'background-color':'#111'}},{id:'sat',type:'raster',source:'eox',paint:{'raster-saturation':-0.35,'raster-brightness-max':0.8}}]};
}
function styleFor(b){ return b==='sat' ? satStyle() : OFM + (b==='day' ? 'positron' : 'dark'); }

const GOLD = ['interpolate',['linear'],['zoom'], 5,'#c6a15b', 12,'#e0bc62', 17,'#f0d48a'];
function setBuildingsVisible(on){
  if (map && map.getLayer('bldg3d')) map.setLayoutProperty('bldg3d', 'visibility', on ? 'visible' : 'none');
}
function addOverlays(){
  const firstSymbol = (map.getStyle().layers.find(l=>l.type==='symbol')||{}).id;
  const narrow = matchMedia('(max-width: 760px)').matches;
  if (map.getSource('openmaptiles')){
    map.addLayer({id:'bldg3d', type:'fill-extrusion', source:'openmaptiles', 'source-layer':'building', minzoom: narrow ? 14.2 : 13.6,
      paint:{'fill-extrusion-color': base==='day' ? '#e7e0d2' : '#46536c',
             'fill-extrusion-height':['coalesce',['get','render_height'],8], 'fill-extrusion-base':['coalesce',['get','render_min_height'],0],
             'fill-extrusion-opacity': base==='day' ? 0.72 : 0.9}}, firstSymbol);
  }
  // soft golden light on the ground under the columns (a "field of light" at country/city scale)
  map.addSource('pts',{type:'geojson', data:POINTS_FC, maxzoom:14});
  map.addLayer({id:'stone-dots', type:'circle', source:'pts', minzoom:14, maxzoom:17.4,
    paint:{'circle-radius':['interpolate',['linear'],['zoom'],14,3,16,9,17.2,14],
           'circle-color':'#f0d48a','circle-opacity':0.55,'circle-blur':0.75,'circle-pitch-alignment':'map'}}, firstSymbol);
  map.addLayer({id:'glow', type:'heatmap', source:'pts', maxzoom:15,
    paint:{'heatmap-radius':['interpolate',['linear'],['zoom'],4,6,8,14,12,28,15,40],
           'heatmap-intensity':['interpolate',['linear'],['zoom'],4,0.25,9,0.6,14,1],
           'heatmap-weight':0.5,
           'heatmap-color':['interpolate',['linear'],['heatmap-density'],0,'rgba(0,0,0,0)',0.15,'rgba(150,110,40,0.25)',0.5,'rgba(210,165,70,0.45)',1,'rgba(255,225,150,0.7)'],
           'heatmap-opacity': base==='day' ? 0.5 : 0.85}}, firstSymbol);
  // Night: one soft light per house (not per stone). Cheap circle layer; hidden by day.
  if (LIGHTS_FC){
    map.addSource('house-lights',{type:'geojson', data:LIGHTS_FC, maxzoom:14});
    map.addLayer({id:'house-lights', type:'circle', source:'house-lights', minzoom:4, maxzoom:14.2,
      layout:{visibility: base==='day' ? 'none' : 'visible'},
      paint:{'circle-radius':['interpolate',['linear'],['zoom'],4,1.15,8,2.1,12,3.4,14,5],
             'circle-color':'#ffe2a0',
             'circle-opacity':['interpolate',['linear'],['zoom'],4,0.4,9,0.75,13.5,0.2],
             'circle-blur':0.65, 'circle-pitch-alignment':'map'}}, firstSymbol);
  }
  for (const {L,fc} of AGG){
    map.addSource(L.id,{type:'geojson', data:fc});
    map.addLayer({id:L.id, type:'fill-extrusion', source:L.id, minzoom:L.min, maxzoom:L.max,
      paint:{'fill-extrusion-color':GOLD, 'fill-extrusion-height':['get','h'], 'fill-extrusion-opacity':0.92, 'fill-extrusion-vertical-gradient':true}});
  }
  map.addSource('sel',{type:'geojson', data:selFC()});
  refreshSel && setTimeout(refreshSel,0);
  map.addLayer({id:'sel-glow', type:'circle', source:'sel', filter:['==',['geometry-type'],'Point'],
    paint:{'circle-radius':['interpolate',['linear'],['zoom'],12,18,18,60], 'circle-color':'#ffd56b', 'circle-opacity':0.45, 'circle-blur':1, 'circle-pitch-alignment':'map'}});
  map.addLayer({id:'sel', type:'fill-extrusion', source:'sel', filter:['==',['geometry-type'],'Polygon'],
    paint:{'fill-extrusion-color':'#fff3c4', 'fill-extrusion-height':['get','h'], 'fill-extrusion-opacity':1}});
  // columnas individuales (modelos en columns.js); si no carga, la columna simple de antes
  if (window.KLCols) KLCols.add(firstSymbol);
  else {
    map.addSource('stones',{type:'geojson', data:STONES_FC, maxzoom:16, buffer:16, tolerance:0});
    map.addLayer({id:'stones', type:'fill-extrusion', source:'stones', minzoom:14.6,
      paint:{'fill-extrusion-color':GOLD, 'fill-extrusion-height':COL_H, 'fill-extrusion-opacity':0.95, 'fill-extrusion-vertical-gradient':true}}, 'sel-glow');
  }
  map.setLight({anchor:"map", position:[1.5, 215, 62], color:"#fff1d0", intensity:0.62});
  try { map.setSky(base==='day'
      ? {'sky-color':'#d5e2f0','horizon-color':'#f4f1ea','fog-color':'#efe6d4','sky-horizon-blend':0.6,'horizon-fog-blend':0.55,'fog-ground-blend':0.55,'atmosphere-blend':0.4}
      : {'sky-color':'#07111f','horizon-color':'#1a3358','fog-color':'#101820','sky-horizon-blend':0.55,'horizon-fog-blend':0.55,'fog-ground-blend':0.65,'atmosphere-blend':0.55}); } catch(e){}
  if (window.KLImagery) KLImagery.onStyle();
}
function selFC(){
  const s = selected && byId.get(selected); if (!s) return {type:'FeatureCollection', features:[]};
  const zoomed = map && map.getZoom() >= 14.6;
  const feats = [{type:'Feature', properties:{}, geometry:{type:'Point', coordinates:[s._dlo,s._dla]}}];
  // the remembered person's column: same place, brighter and taller so it stands above the roofs
  feats.push({type:'Feature', properties:{h: zoomed ? 34 : 400}, geometry:{type:'Polygon', coordinates:square(s._dlo,s._dla, zoomed ? COL_HALF*1.15 : 12, s._ang)}});
  return {type:'FeatureCollection', features:feats};
}
function refreshSel(){ const src = map.getSource('sel'); if (src) src.setData(selFC()); if (window.KLCols) KLCols.filterSel(); else if (map.getLayer('stones')) map.setFilter('stones', selected ? ['!=',['get','id'],selected] : null); }

function paintBaseButtons(){
  document.body.classList.toggle('dark', base!=='day');
  document.querySelectorAll('.basemaps button[data-base]').forEach(x=>x.setAttribute('aria-pressed', x.dataset.base===base));
}
function ensureVectorStyle(done){
  if (map.getSource('openmaptiles')) { done(); return; }
  map.setStyle(styleFor('night'), {diff:false});
  map.once('style.load', () => { addOverlays(); done(); });
}
function setBase(b){
  if (b==='hoy') {
    base = 'hoy'; localStorage.setItem('base', base); paintBaseButtons();
    ensureVectorStyle(() => { if (window.KLImagery) KLImagery.setHoy(true); });
    return;
  }
  base = b; localStorage.setItem('base', b); paintBaseButtons();
  if (window.KLImagery) KLImagery.setHoy(false);
  map.setStyle(styleFor(b), {diff:false});
  map.once('style.load', addOverlays);
}

/* ---------- map ---------- */
function shouldIntro(){
  const q = new URLSearchParams(location.search);
  if (q.get('intro') === '0' || location.hash.startsWith('#s=') || q.get('vigil') || q.get('q')) return false;
  if (q.get('intro') === '1') return true;
  try { return localStorage.getItem('kauffmann.introSeen') !== '1'; } catch (e) { return false; }
}
const narrowScreen = matchMedia('(max-width: 760px)').matches;
/* ---------- 3D angle button ----------
   Fix: the compass (NavigationControl, visualizePitch) only resets to north AND flat (pitch 0),
   and there was no control to tilt back. This button always reflects the real pitch (also after
   touch / ctrl-drag gestures) and toggles between flat and the last used angle. */
const PITCH_FLAT = 8;                       // below this the map counts as "seen from above"
let lastAngle = null;                       // last angle the user had (restored by the button)
const defaultAngle = () => narrowScreen ? 42 : 52;
function flatOnly(){                        // 1945 photo / compare mode keeps the map flat on purpose
  try { const st = window.KLImagery && KLImagery.status(); return !!(st && st.aerial && st.region === 'BHV' && (st.epoch === '1945' || st.epoch === 'swipe')); }
  catch(e){ return false; }
}
function tiltBack(north){
  if (!map) return;
  const target = Math.min(Math.max(lastAngle || defaultAngle(), 30), 65);
  const v = north ? {pitch:target, bearing:0} : {pitch:target};
  if (reduceMotion) map.jumpTo(v); else map.easeTo({...v, duration:700, essential:true});
}
function updatePitchBtn(){
  const btn = document.querySelector('.kl-pitch-btn'); if (!btn || !map) return;
  const tilted = map.getPitch() >= PITCH_FLAT;
  const locked = !tilted && flatOnly();
  btn.textContent = tilted ? '2D' : '3D';
  btn.setAttribute('aria-pressed', String(tilted));
  btn.disabled = locked;
  const label = locked ? T('pitchFlatOnly') : (tilted ? T('pitchTo2d') : T('pitchTo3d'));
  btn.setAttribute('aria-label', label); btn.title = label;
}
class PitchControl {
  onAdd(m){
    this._c = document.createElement('div');
    this._c.className = 'maplibregl-ctrl maplibregl-ctrl-group';
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'kl-pitch-btn';
    btn.addEventListener('click', () => {
      if (m.getPitch() >= PITCH_FLAT) {
        lastAngle = m.getPitch();
        if (reduceMotion) m.jumpTo({pitch:0}); else m.easeTo({pitch:0, duration:700, essential:true});
      } else if (!flatOnly()) tiltBack();
    });
    this._c.append(btn);
    const remember = () => { const p = m.getPitch(); if (p >= PITCH_FLAT + 10) lastAngle = p; };
    m.on('pitch', updatePitchBtn); m.on('pitchend', () => { remember(); updatePitchBtn(); });
    m.on('moveend', updatePitchBtn);
    setTimeout(updatePitchBtn, 0);
    return this._c;
  }
  onRemove(){ this._c.remove(); }
}
/* Compass: when the map is flat, a press turns it north AND tilts it back (instead of doing nothing). */
function fixCompassTilt(){
  const cb = map.getContainer().querySelector('.maplibregl-ctrl-compass'); if (!cb) return;
  cb.addEventListener('click', e => {
    if (map.getPitch() < PITCH_FLAT && !flatOnly()) {
      e.stopImmediatePropagation(); e.preventDefault(); tiltBack(true);
    }
  }, true);
}

function initMap(){
  const intro = shouldIntro();
  base = intro ? 'night' : (localStorage.getItem('base') || 'night');
  if (base !== 'night' && base !== 'day' && base !== 'sat' && base !== 'hoy') base = 'night';
  paintBaseButtons();
  const styleKey = (base === 'hoy' || base === 'sat') ? (base === 'sat' ? 'sat' : 'night') : base;
  const mapOpts = {
    container:'map', style:styleFor(styleKey),
    center: intro ? [10, 28] : [10.45, 51.0],
    zoom: intro ? 1.05 : (narrowScreen ? 4.9 : 5.3),
    pitch: intro ? 0 : (narrowScreen ? 42 : 52),
    bearing: intro ? -18 : -12,
    maxPitch:70, attributionControl:{compact:true}, hash:false,
    fadeDuration: narrowScreen ? 0 : 250,
    antialias: !narrowScreen,
    pixelRatio: Math.min(window.devicePixelRatio || 1, narrowScreen ? 2 : 3),   // resolución completa de la pantalla
    projection: intro ? 'globe' : 'mercator',
    canvasContextAttributes:{antialias: !narrowScreen}
  };
  if (new URLSearchParams(location.search).has('captura')) mapOpts.maxCanvasSize = [8192, 8192];   // solo para imágenes 8K
  try { map = new maplibregl.Map(mapOpts); }
  catch (err) { console.warn('map', err); delete mapOpts.projection; map = new maplibregl.Map(mapOpts); }
  map.addControl(new maplibregl.NavigationControl({visualizePitch:true}), 'top-right');
  map.addControl(new PitchControl(), 'top-right');
  fixCompassTilt();
  map.addControl(new maplibregl.GeolocateControl({trackUserLocation:false}), 'top-right');
  map.on('error', e => console.warn('map error', e && e.error && e.error.message));
  map.once('style.load', ()=>{
    if (DATA.length) addOverlays(); else map._pendingOverlays = true;
    if (!intro && base === 'hoy' && window.KLImagery) KLImagery.setHoy(true);
  });
  map.on('click','stones', e => { const f=e.features && e.features[0]; if (f) openStone(f.properties.id, true); });
  for (const L of LEVELS){
    map.on('click', L.id, e => { const p=e.features[0].properties; map.flyTo({center:[p.lo,p.la], zoom:Math.min(L.max+0.6,17.2), pitch:Math.max(map.getPitch(),55), duration:2200, essential:true}); });
    map.on('mouseenter', L.id, ()=>map.getCanvas().style.cursor='pointer');
    map.on('mouseleave', L.id, ()=>map.getCanvas().style.cursor='');
  }
  map.on('mouseenter','stones',()=>map.getCanvas().style.cursor='pointer');
  map.on('mouseleave','stones',()=>map.getCanvas().style.cursor='');
  map.on('zoomend', refreshSel);
}

async function load(){
  $('#status').textContent = T('loading');
  const j = await (await fetch('data/stones.json')).json();
  META = j.meta; DATA = j.stones;
  for (const s of DATA){
    s._t = norm([s.n, s.a, s.sub, cityOf(s)].join(' ')).split(' ');
    s._c = norm(cityOf(s)); byId.set(s.id, s);
  }
  buildStones(); buildAgg();
  const cities = new Map();
  for (const s of VISIBLE){
    const c = cityOf(s); if (c){ const o = cities.get(c) || cities.set(c,{n:0,ids:[]}).get(c); o.n++; o.ids.push(s.id); }
  }
  CITY_STATS = [...cities.entries()].sort((a,b)=>b[1].n-a[1].n);
  $('#cities').innerHTML = [...cities.entries()].sort((a,b)=>a[0].localeCompare(b[0],'de')).map(([c,o])=>`<option value="${esc(c)}">${esc(c)} (${o.n})</option>`).join('');
  if (map.isStyleLoaded() || map._pendingOverlays) { if (!map.getSource('stones')) addOverlays(); }
  else map.once('style.load', ()=>{ if (!map.getSource('stones')) addOverlays(); });
  if (window.KLImagery) KLImagery.onData();
  $('#status').textContent = T('ready')(fmtNum(DATA.length));
  route();
}

function search(){
  const q = norm($('#q').value), cq = norm($('#city').value), list = $('#results');
  closeDetail(false);
  if (!q && !cq){ list.innerHTML=''; $('#status').textContent=T('ready')(fmtNum(DATA.length)); return; }
  const qt = q ? q.split(' ') : [], out=[], LIMIT=300;
  for (const s of DATA){
    if (s._aliasOf) continue;
    if (cq && !s._c.startsWith(cq) && !s._c.includes(' '+cq)) continue;
    let score=0, ok=true, minTok=3;
    for (const w of qt){
      let best=0;
      for (const t of s._t){
        if (t===w){best=3;break}
        if (t.startsWith(w)) best=Math.max(best,2);
        else if (w.length>=4 && best<1){ const mx=w.length>=8?2:1; if (lev(w,t,mx)<=mx) best=1; }
      }
      if (!best){ok=false;break} score+=best; if (best<minTok) minTok=best;
    }
    if (ok) out.push([score,s,minTok]);
  }
  const strong = out.filter(x=>x[2]>=2), fuzzyOnly = !strong.length && out.length>0;
  const res = strong.length ? strong : out;
  res.sort((a,b)=>b[0]-a[0] || (a[1].n||'').localeCompare(b[1].n||'','de'));
  const more = res.length>LIMIT, shown = res.slice(0,LIMIT);
  $('#status').textContent = res.length ? T('results')(fmtNum(shown.length),more)+(fuzzyOnly?' '+T('similar'):'') : T('none');
  list.innerHTML = shown.map(([,s])=>`<li><button data-id="${esc(s.id)}"><div class="nm">${esc(s.n||'—')}</div>
    <div class="meta">${esc([s.a||cityOf(s), s.b?('* '+s.b):''].filter(Boolean).join(' · '))}</div></button></li>`).join('');
}

function commonsThumb(f,w){ return 'https://commons.wikimedia.org/wiki/Special:FilePath/'+encodeURIComponent(f.replace(/ /g,'_'))+'?width='+w; }
function commonsPage(f){ return 'https://commons.wikimedia.org/wiki/File:'+encodeURIComponent(f.replace(/ /g,'_')); }
function wpUrl(v){ const m=/^([a-z\-]+):(.+)$/.exec(v); return m?`https://${m[1]}.wikipedia.org/wiki/${encodeURIComponent(m[2].replace(/ /g,'_'))}`:''; }
function osmUrl(s){ return /^[nw]\d+$/.test(s.id)?`https://www.openstreetmap.org/${s.id[0]==='n'?'node':'way'}/${s.id.slice(1)}`:''; }

const ANON_NAME = /\b(sinto|sinti|sintiza|romni|rommni|roma|rom|unbekannt|anonym|namenlos)\b|^\s*n\.?\s*n\.?\s*$/i;
function isAnonStone(s){ const n=(s.n||'').trim(); return !n || n.length<3 || ANON_NAME.test(n); }
function citySlug(city){
  let s = (city||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[^\x00-\x7F]/g,'');
  s = s.replace(/[^a-zA-Z0-9]+/g,'-').replace(/^-+|-+$/g,'').toLowerCase();
  return s.slice(0,80) || 'sin-lugar';
}
let bioManifest = null, bioPacks = {};
function loadManifest(){
  if (!bioManifest) bioManifest = fetch('data/bio/manifest.json').then(r => r.ok ? r.json() : {files:[]}).catch(() => ({files:[]}));
  return bioManifest;
}
function loadCityPack(slug){
  if (!bioPacks[slug]) bioPacks[slug] = fetch('data/bio/'+slug+'.json').then(r => r.ok ? r.json() : {}).catch(() => ({}));
  return bioPacks[slug];
}
async function recordFor(s){
  const man = await loadManifest();
  const slug = citySlug(cityOf(s) || 'sin-lugar');
  if (!(man.files||[]).includes(slug)) return null;
  const pack = await loadCityPack(slug);
  return pack[s.id] || null;
}
function archiveItems(s, rec){
  const L2 = lang==='de' ? 'de' : 'en';
  const links = (rec && rec.links) || {};
  const items = [];
  const add = (href, label) => items.push(`<li><a href="${esc(href)}" target="_blank" rel="noopener">${esc(label)}</a></li>`);
  if (links.berlin) add(links.berlin, T('berlinBio'));
  if (links.hamburg) add(links.hamburg, T('hamburgBio'));
  if (links.bremen) add(links.bremen, T('bremenBio'));
  (links.describedAt||[]).forEach(u => { let h=u; try{h=new URL(u).hostname.replace(/^www\./,'')}catch(e){} add(u, T('describedAt')+' · '+h); });
  const gb = links.gedenkbuch || s.gb || [];
  const yv = links.yadvashem || s.yv || [];
  const us = links.ushmm || s.us || [];
  gb.forEach(g => add('https://www.bundesarchiv.de/gedenkbuch/'+L2+g, T('gb')));
  yv.forEach(y => add('https://collections.yadvashem.org/'+L2+'/names/'+y, T('yv')));
  us.forEach(u => add('https://www.ushmm.org/online/hsv/person_view.php?PersonId='+u, T('ushmm')));
  if (!gb.length) add('https://www.bundesarchiv.de/gedenkbuch/'+L2, T('gbSearch'));
  if (!yv.length) add('https://collections.yadvashem.org/'+L2+'/names/search-results-names', T('yvSearch'));
  if (!us.length) add('https://www.ushmm.org/remember/resources-holocaust-survivors-victims/database-of-holocaust-survivor-and-victim-names/search-names', T('ushmmSearch'));
  add('https://collections.arolsen-archives.org/'+L2+'/search', T('arolsenSearch'));
  return items;
}
function paintStory(s, rec){
  const slot = $('#storySlot'); if (!slot || selected !== s.id) return;
  const dates = $('#inscDates');
  const insc = rec && rec.insc;
  if (dates){
    const bits = [];
    if (insc && insc.birth) bits.push(T('born')+': '+insc.birth);
    if (insc && insc.deportation) bits.push(insc.deportation);
    if (insc && insc.death) bits.push(insc.death);
    if (bits.length){ dates.hidden = false; dates.innerHTML = esc(bits.join(' · '))+' <span class="src-tag">'+esc(T('perInscription'))+'</span>'; }
    else dates.hidden = true;
  }
  const anon = isAnonStone(s);
  const parts = [];
  const links = (rec && rec.links) || {};
  const official = links.berlin || links.hamburg || links.bremen;
  if (rec && rec.wp && rec.wp.text){
    const w = rec.wp;
    parts.push(`<div class="section-t">${T('story')}</div>`);
    parts.push(`<div class="story">${esc(w.text)}</div>`);
    parts.push(`<p class="cite">${esc(T('wpCite'))} <a href="${esc(w.permalink)}" target="_blank" rel="noopener">${esc(w.title)}</a>, ${esc(T('wpRev'))} ${esc(w.revid)}. <a href="${esc(w.authors)}" target="_blank" rel="noopener">${esc(T('wpAuthors'))}</a>. <a href="${esc(w.licenseUrl)}" target="_blank" rel="noopener">${esc(w.license)}</a>.</p>`);
  } else if (anon) {
    parts.push(`<p class="help">${esc(T('anonNote'))}</p>`);
  } else if (!official) {
    parts.push(`<p class="help">${esc(T('noStory'))} <a href="#contribuir" id="contrib">${esc(T('helpUs'))}</a></p>`);
  }
  const items = archiveItems(s, rec);
  if (items.length) parts.push(`<div class="section-t">${T('archives')}</div><ul class="links">${items.join('')}</ul><p class="note">${T('researchNote')}</p>`);
  slot.innerHTML = parts.join('');
  const c = $('#contrib');
  if (c) c.onclick = e => { e.preventDefault(); $('#contribNote').textContent = T('contribNote'); $('#contribDlg').showModal(); };
}
function loadStory(s){
  const slot = $('#storySlot');
  if (slot) slot.innerHTML = '<p class="story-wait">…</p>';
  recordFor(s).then(async rec => {
    if (rec && rec.wp && !rec.wp.text){
      try {
        const t = await fetch('data/bio/text/'+encodeURIComponent(s.id)+'.json');
        if (t.ok) rec.wp.text = (await t.json()).text;
      } catch (e) {}
    }
    paintStory(s, rec);
  }).catch(() => paintStory(s, null));
}
function openStone(id, fromMap){
  let s = byId.get(id); if (!s) return;
  if (s._aliasOf) s = byId.get(s._aliasOf) || s;
  if (document.body.classList.contains('vigil-on')) stopVigil();
  selected = s.id; refreshSel();
  const targetZoom = 17.6;
  if (!fromMap || map.getZoom() < 16.5)
    map.flyTo({center:[s._dlo,s._dla], zoom:targetZoom, pitch:58, offset:[0, 60], bearing: map.getBearing() || -20, duration: reduceMotion ? 0 : 3200, essential:true, curve:1.5});
  map.once('moveend', refreshSel);
  history.replaceState(null,'','#s='+encodeURIComponent(id));
  const insc = s.i ? esc(s.i).split(/\s*\|\s*/).join('<br>') : '';
  const facts=[[T('address'),s.a],[T('place'),cityOf(s)+(s.cd&&!s.c?' '+T('derived'):'')],[T('district'),s.sub],[T('born'),s.b],[T('died'),s.d],[T('laid'),s.laid],[T('type'),s.kind==='stolperschwelle'?T('threshold'):'']]
    .filter(x=>x[1]).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('');
  const bio=[]; (s.w||[]).forEach(u=>{ let h=u; try{h=new URL(u).hostname.replace(/^www\./,'')}catch(e){} bio.push(`<li><a href="${esc(u)}" target="_blank" rel="noopener">${esc(h)}</a></li>`); });
  if (s.wp) bio.push(`<li><a href="${esc(wpUrl(s.wp))}" target="_blank" rel="noopener">Wikipedia: ${esc(s.wp.replace(/^[a-z]+:/,''))}</a></li>`);
  if (s.desc) bio.unshift(`<li>${esc(s.desc)}</li>`);
  const recs = [s, ...(s._also||[])];
  const src=[]; const seenSrc=new Set();
  for (const r of recs){ const u=osmUrl(r); if (u && !seenSrc.has(u)){ seenSrc.add(u); src.push(`<li><a href="${u}" target="_blank" rel="noopener">OpenStreetMap</a></li>`); } }
  for (const r of recs){ if (r.wd && !seenSrc.has('wd:'+r.wd)){ seenSrc.add('wd:'+r.wd); src.push(`<li><a href="https://www.wikidata.org/wiki/${esc(r.wd)}" target="_blank" rel="noopener">Wikidata ${esc(r.wd)}</a></li>`); } }
  for (const r of recs){ if (r.p && !seenSrc.has('p:'+r.p)){ seenSrc.add('p:'+r.p); src.push(`<li><a href="https://www.wikidata.org/wiki/${esc(r.p)}" target="_blank" rel="noopener">Wikidata (persona/Person) ${esc(r.p)}</a></li>`); } }
  const photo = s.img ? `<figure class="photo"><a href="${commonsPage(s.img)}" target="_blank" rel="noopener"><img loading="lazy" src="${commonsThumb(s.img,480)}" alt="${esc(s.n||'')}"></a><figcaption><a href="${commonsPage(s.img)}" target="_blank" rel="noopener">${T('photo')}</a></figcaption></figure>` : '';
  const d = $('#detail');
  d.innerHTML = `<button class="back" id="back">${T('back')}</button>
    <h2>${esc(s._n||s.n||'—')}</h2><p class="place">${esc([s.a, s.a&&s.a.includes(cityOf(s))?'':cityOf(s)].filter(Boolean).join(', '))}</p>
    <p class="dates" id="inscDates" hidden></p>
    <div class="section-t">${T('inscription')}</div>
    ${insc?`<div class="brassplate">${insc}</div>`:`<p class="note">${T('noinsc')}</p>`}
    ${photo}
    <dl class="facts">${facts}</dl>
    <div class="actions">
      <button id="share">${T('share')}</button>
      <a href="https://www.google.com/maps/dir/?api=1&destination=${s.la},${s.lo}" target="_blank" rel="noopener">${T('directions')}</a>
      <a href="https://www.openstreetmap.org/directions?to=${s.la}%2C${s.lo}#map=19/${s.la}/${s.lo}" target="_blank" rel="noopener">${T('osmDir')}</a>
    </div>
    <div id="storySlot"><p class="story-wait">…</p></div>
    ${bio.length?`<div class="section-t">${T('bio')}</div><ul class="links">${bio.join('')}</ul>`:''}
    <div class="section-t">${T('sources')}</div><ul class="links">${src.join('')}</ul>
    <p class="note">${T('attribution')}</p>`;
  $('#results').hidden = true; d.hidden = false; d.scrollTop = 0;
  $('#back').onclick = ()=>closeDetail(true);
  $('#share').onclick = e=>{ navigator.clipboard?.writeText(location.href); e.target.textContent=T('copied'); };
  loadStory(s);
}
function closeDetail(restore){
  $('#detail').hidden = true; $('#results').hidden = false;
  selected = null; if (map) refreshSel();
  if (restore) history.replaceState(null,'',location.pathname+location.search);
}
function route(){
  const m = /#s=([^&]+)/.exec(location.hash);
  if (m && byId.has(decodeURIComponent(m[1]))) { openStone(decodeURIComponent(m[1])); return; }
  const p = new URLSearchParams(location.search);
  if (p.get('q')){ $('#q').value = p.get('q'); search(); }
  if (p.get('vigil')) startVigil();
}

/* ---------- "Recordar a todos": calm remembrance tour ---------- */
let vigil = {on:false, paused:false, stop:0, timers:[], names:[], ni:0};
function vclear(){ vigil.timers.forEach(clearTimeout); vigil.timers=[]; clearInterval(vigil.nameTimer); map.stop(); }
function startVigil(){
  if (!DATA.length) return;
  closeDetail(true);
  vigil.on = true; vigil.paused = false; vigil.stop = -1;
  document.body.classList.add('vigil-on'); $('#vigil').hidden = false;
  $('#vigilCount').textContent = T('vigilCount')(fmtNum(DATA.length));
  $('#vigilText').textContent = T('vigilText');
  $('#vigilPause').textContent = T('pause');
  setTimeout(()=>map.resize(), 50);
  overview();
}
function overview(){
  vclear(); $('#vigilPlace').textContent=''; showNames(DATA.map(s=>s.id));
  map.flyTo({center:[10.45,51.0], zoom:window.innerWidth<760?4.9:5.5, pitch:55, bearing:-20, duration: reduceMotion?0:6000, essential:true});
  if (reduceMotion) return;
  vigil.timers.push(setTimeout(()=>{ rotate(40, 24000); vigil.timers.push(setTimeout(nextStop, 25000)); }, 6200));
}
function rotate(deg, ms){ map.easeTo({bearing: map.getBearing()+deg, duration: ms, easing: t=>t, essential:true}); }
function nextStop(){
  if (!vigil.on || vigil.paused) return;
  vigil.stop++;
  const tour = CITY_STATS.slice(0, 10);
  if (vigil.stop >= tour.length){ vigil.stop=-1; overview(); return; }
  const [city, o] = tour[vigil.stop];
  // centre on the densest small cell of that city (real stone positions only)
  const cells = new Map();
  for (const id of o.ids){ const s=byId.get(id); const k=Math.floor(s.la/0.003)+':'+Math.floor(s.lo/0.0048); const c=cells.get(k)||cells.set(k,{n:0,la:0,lo:0}).get(k); c.n++; c.la+=s._dla; c.lo+=s._dlo; }
  const best = [...cells.values()].sort((a,b)=>b.n-a.n)[0];
  vclear();
  $('#vigilPlace').textContent = T('vigilPlace')(city, fmtNum(o.n));
  showNames(o.ids);
  map.flyTo({center:[best.lo/best.n, best.la/best.n], zoom:16.4, pitch:64, bearing: map.getBearing()+30, duration:9000, curve:1.6, essential:true});
  vigil.timers.push(setTimeout(()=>{ rotate(35, 22000); vigil.timers.push(setTimeout(nextStop, 23000)); }, 9200));
}
function showNames(ids){
  const el = $('#vigilNames'); const pool = ids.slice();
  for (let i=pool.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [pool[i],pool[j]]=[pool[j],pool[i]]; }
  let i = 0;
  const step = ()=>{ if (vigil.paused) return; const s = byId.get(pool[i++ % pool.length]); el.style.opacity=0;
    setTimeout(()=>{ el.textContent = (s.n||'') + (s.b ? ' · ' + String(s.b).slice(0,4) : ''); el.style.opacity=1; }, 1200); };
  step(); vigil.nameTimer = setInterval(step, 4200);
}
function stopVigil(){
  vigil.on=false; vclear(); document.body.classList.remove('vigil-on'); $('#vigil').hidden = true; setTimeout(()=>map.resize(), 50);
}
$('#remember').onclick = ()=> vigil.on ? stopVigil() : startVigil();
$('#vigilExit').onclick = stopVigil;
$('#vigilPause').onclick = e=>{
  vigil.paused = !vigil.paused; e.target.textContent = vigil.paused ? T('resume') : T('pause');
  if (vigil.paused) { vigil.timers.forEach(clearTimeout); vigil.timers=[]; map.stop(); }
  else { vigil.stop--; nextStop(); }
};

/* ---------- wiring ---------- */
let tmr; const debounced=()=>{clearTimeout(tmr); tmr=setTimeout(search,180);};
$('#q').addEventListener('input',debounced); $('#city').addEventListener('input',debounced);
$('#results').addEventListener('click',e=>{const b=e.target.closest('button[data-id]'); if(b) openStone(b.dataset.id);});
document.querySelectorAll('.lang button').forEach(b=>b.onclick=()=>{lang=b.dataset.lang; localStorage.setItem('lang',lang); applyI18n(); if (window.KLImagery) KLImagery.refresh(); if(selected) openStone(selected,true); else search();});
document.querySelectorAll('.basemaps button[data-base]').forEach(b=>b.onclick=()=>setBase(b.dataset.base));
$('#aboutLink').onclick=e=>{e.preventDefault(); $('#aboutBody').innerHTML=T('aboutHtml')({...META,count:fmtNum(META.count||DATA.length)}); $('#about').showModal();};
window.addEventListener('hashchange', route);
function stoneProps(s){
  return {id:s.id, name:s.n||'', inscription:s.i||'', address:s.a||'', city:s.c||'', city_derived:s.cd||'',
    district:s.sub||'', birth:s.b||'', death:s.d||'', laid:s.laid||'', wikidata:s.wd||'', person:s.p||''};
}
function downloadText(name, mime, text){
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], {type:mime}));
  a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 2500);
}
$('#dlGeo').onclick = () => {
  if (!DATA.length) return;
  const fc = {type:'FeatureCollection', name:'stolpersteine_germany', license: META.license,
    features: DATA.map(s => ({type:'Feature', geometry:{type:'Point', coordinates:[s.lo, s.la]}, properties:stoneProps(s)}))};
  downloadText('stolpersteine_germany.geojson', 'application/geo+json', JSON.stringify(fc));
};
$('#dlKml').onclick = () => {
  if (!DATA.length) return;
  const xe = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const parts = ['<?xml version="1.0" encoding="UTF-8"?>','<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Stolpersteine in Deutschland</name>'];
  for (const s of DATA) {
    const p = stoneProps(s);
    const desc = [p.address, p.city, p.birth && ('* '+p.birth), p.death && ('† '+p.death), p.inscription].filter(Boolean).join(' · ');
    parts.push('<Placemark><name>'+xe(p.name)+'</name><description>'+xe(desc)+'</description><Point><coordinates>'+s.lo+','+s.la+',0</coordinates></Point></Placemark>');
  }
  parts.push('</Document></kml>');
  downloadText('stolpersteine_germany.kml', 'application/vnd.google-earth.kml+xml', parts.join('\n'));
};

const INTRO = {
  es:[
    {k:'Lista Kauffmann', t:'Cada placa, cada nombre, cada historia.', b:'Nunca olvidar.', c:'Continuar'},
    {k:'Lista Kauffmann', t:'Una columna, una persona.', b:'Cada columna dorada está frente a la casa donde alguien vivió. No es un edificio de entonces: es el memorial, hoy.', c:'Continuar'},
    {k:'Lista Kauffmann', t:'1945 y hoy, solo con fotografías reales.', b:'Donde hay una ortofoto oficial abierta, el mapa la muestra al acercarse. La fotografía de 1945, solo en Bremerhaven, donde está verificada. En las demás ciudades lo decimos con claridad.', c:'Entrar en el mapa'}
  ],
  de:[
    {k:'Kauffmann-Liste', t:'Jede Platte, jeder Name, jede Geschichte.', b:'Nie vergessen.', c:'Weiter'},
    {k:'Kauffmann-Liste', t:'Eine Säule, ein Mensch.', b:'Jede goldene Säule steht vor dem Haus, in dem jemand lebte. Sie ist kein Gebäude von damals: sie ist das Mahnmal, heute.', c:'Weiter'},
    {k:'Kauffmann-Liste', t:'1945 und heute, nur mit echten Fotografien.', b:'Wo ein amtliches offenes Orthophoto vorliegt, zeigt die Karte es beim Hineinzoomen. Das Luftbild von 1945 nur in Bremerhaven, wo es geprüft ist. Für die anderen Städte sagen wir das klar.', c:'Karte öffnen'}
  ],
  en:[
    {k:'Kauffmann List', t:'Every plaque, every name, every story.', b:'Never forget.', c:'Continue'},
    {k:'Kauffmann List', t:'One column, one person.', b:'Each golden column stands in front of the home where someone lived. It is not a building from that time: it is the memorial, today.', c:'Continue'},
    {k:'Kauffmann List', t:'1945 and today, only real photographs.', b:'Where an official open orthophoto exists, the map shows it as you zoom in. The 1945 aerial photograph only in Bremerhaven, where it is verified. For every other city we say so plainly.', c:'Enter the map'}
  ]
};
let introOn = false, introStep = 0, introSpin = 0;
function introSteps(){ return INTRO[lang] || INTRO.es; }
function paintIntro(){
  const s = introSteps()[introStep];
  $('#introTitle').textContent = s.t;
  $('#introBody').textContent = s.b;
  $('#introNext').textContent = s.c;
  document.querySelector('.intro-kicker').textContent = s.k;
  $('#introSkip').textContent = lang==='de' ? 'Überspringen' : lang==='en' ? 'Skip' : 'Omitir';
  const dots = $('#introDots');
  dots.replaceChildren();
  introSteps().forEach((_, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('aria-label', String(i+1));
    if (i===introStep) b.setAttribute('aria-current','true');
    b.onclick = () => { introStep = i; paintIntro(); };
    dots.append(b);
  });
}
function spinIntro(){
  if (!introOn || reduceMotion) return;
  clearTimeout(introSpin);
  map.easeTo({bearing: map.getBearing()+10, duration:9000, easing:t=>t, essential:true});
  introSpin = setTimeout(spinIntro, 9000);
}
function armGlobe(){
  try { map.setProjection({type:'globe'}); } catch (e) { console.warn('globe', e); }
  try { map.getCanvas().style.background = 'transparent'; map.getContainer().style.background = '#070b14'; } catch (e) {}
  try { map.setSky({'sky-color':'#070b14','horizon-color':'#163056','fog-color':'#070b14','atmosphere-blend':0.85,'sky-horizon-blend':0.35,'horizon-fog-blend':0.4,'fog-ground-blend':0.2}); } catch (e) {}
  map.jumpTo({center:[10, 22], zoom: narrowScreen ? 0.85 : 1.05, pitch:0, bearing:-20});
}
function openIntro(){
  introOn = true; introStep = 0;
  document.documentElement.classList.remove('intro-skip');
  paintIntro();
  setTimeout(() => map.resize(), 40);
  const go = () => { armGlobe(); spinIntro(); };
  if (map.isStyleLoaded()) go(); else map.once('style.load', go);
}
function closeIntro(fly){
  introOn = false; clearTimeout(introSpin); map.stop();
  try { localStorage.setItem('kauffmann.introSeen','1'); } catch (e) {}
  document.documentElement.classList.add('intro-skip');
  setTimeout(() => map.resize(), 40);
  if (!fly) {
    try { map.setProjection({type:'mercator'}); } catch (e) {}
    map.jumpTo({center:[10.45,51.0], zoom:narrowScreen?4.9:5.3, pitch:narrowScreen?42:52, bearing:-12});
    return;
  }
  const dur = reduceMotion ? 0 : 5200;
  map.flyTo({center:[10.45, 51.05], zoom:narrowScreen?4.9:5.35, pitch:narrowScreen?46:52, bearing:-14, duration:dur, essential:true, curve:1.4});
  const toMerc = () => { try { map.setProjection({type:'mercator'}); } catch (e) {} };
  if (dur === 0) toMerc(); else map.once('moveend', toMerc);
}
$('#introSkip').onclick = () => closeIntro(false);
$('#introNext').onclick = () => {
  if (introStep < introSteps().length - 1) { introStep++; paintIntro(); return; }
  closeIntro(true);
};
$('#replayIntro').onclick = () => openIntro();

applyI18n();
try {
  initMap();
  KLImagery.init({
    getMap: () => map,
    getData: () => DATA,
    getLang: () => lang,
    reduce: () => reduceMotion,
    buildings: setBuildingsVisible,
    markHoy: () => { base = 'hoy'; localStorage.setItem('base','hoy'); paintBaseButtons(); },
    needNightStyle: () => ensureVectorStyle(() => KLImagery.onStyle())
  });
  load();
  if (shouldIntro()) openIntro();
}
catch(e){ console.error(e); document.documentElement.classList.add('intro-skip'); $('#nogl').hidden=false; $('#nogl').innerHTML=T('nogl'); }
