const I18N = {
  es: {
    title:'Lista Kauffmann', subtitle:'Stolpersteine en Alemania y otros 26 países de Europa · Un nombre, una vida.',
    searchLabel:'Buscar por nombre', searchPh:'Nombre, apellido o calle…', cityLabel:'Lugar', cityPh:'Filtrar por lugar (opcional)',
    loading:'Cargando las placas…', ready:n=>`${n} placas en el mapa. Escriba un nombre para buscar.`,
    results:(n,more)=>`${n}${more?'+':''} resultado${n===1?'':'s'}`, none:'Sin resultados. Pruebe otra grafía, solo el apellido, o quite el filtro de lugar.',
    similar:'(grafías parecidas)', back:'← Volver a los resultados', inscription:'Inscripción de la placa', address:'Dirección', country:'País', countryName:{DE:'Alemania',NL:'Países Bajos',FR:'Francia',AT:'Austria',NO:'Noruega',CZ:'Chequia',IT:'Italia',ES:'España',BE:'Bélgica',LU:'Luxemburgo',HU:'Hungría',LT:'Lituania',CH:'Suiza',PL:'Polonia',SK:'Eslovaquia',JE:'Jersey',HR:'Croacia',DK:'Dinamarca',GG:'Guernsey',FI:'Finlandia',AD:'Andorra',IE:'Irlanda',SE:'Suecia',LV:'Letonia',RO:'Rumanía',GB:'Reino Unido',LI:'Liechtenstein'}, place:'Lugar', district:'Barrio',
    born:'Nacimiento', died:'Muerte', laid:'Placa colocada', type:'Tipo', threshold:'Stolperschwelle (umbral conmemorativo)',
    photo:'Foto de la placa: Wikimedia Commons — ver autor y licencia', bio:'Biografía y fuentes', research:'Buscar en las fuentes',
    researchNote:'Enlaces externos; la Lista Kauffmann no copia sus datos.',
    gb:'Libro Conmemorativo del Archivo Federal Alemán (Gedenkbuch)', yv:'Yad Vashem — Base central de nombres de víctimas de la Shoá', ushmm:'USHMM — Base de sobrevivientes y víctimas', arolsen:'Arolsen Archives',
    gbSearch:'Buscar en el Gedenkbuch', yvSearch:'Buscar en Yad Vashem', ushmmSearch:'Buscar en USHMM', arolsenSearch:'Buscar en Arolsen Archives',
    gbSearchPage:'Gedenkbuch (Bundesarchiv): abrir la página de búsqueda (el nombre no se rellena solo)',
    arolsenSearchName:n=>`Buscar «${n}» en Arolsen Archives`,
    yvSearchName:n=>`Buscar «${n}» en Yad Vashem (Base central de nombres de víctimas de la Shoá)`,
    ushmmSearchName:n=>`Buscar «${n}» en USHMM (base de sobrevivientes y víctimas)`,
    hhSearchName:n=>`Buscar «${n}» en Stolpersteine Hamburg`,
    beSearchName:n=>`Buscar «${n}» en Stolpersteine Berlin`,
    share:'Copiar enlace a esta placa', copied:'Enlace copiado', copyName:'Copiar nombre', nameCopied:'Nombre copiado',
    directions:'Cómo llegar (Google Maps)', osmDir:'Cómo llegar (OpenStreetMap)', sources:'Fuentes de esta ficha', derived:'(lugar deducido de placas cercanas)', posApprox:'Posición aproximada (del edificio, por su dirección en OpenStreetMap)', posApproxPhoto:'Posición aproximada (la de la foto de la placa en Wikimedia Commons, comprobada con la dirección en OpenStreetMap)', posLabel:'Posición',
    discTitle:'Las fuentes no coinciden', discBody:(a,alt)=>`Esta ficha muestra la dirección y la posición de OpenStreetMap («${a}»; el punto está en esa calle). Otras fuentes dan «${alt}» (a unos 250–330 m). No se sabe con certeza dónde está la piedra. El punto de la fuente no se ha tocado; solo el dibujo se desplaza unos 0,85 m hacia la acera, para que no quede sobre la fachada.`, discAlt:alt=>`Dan «${alt}»:`, discMain:a=>`Dan «${a}»:`,
    about:'Acerca de los datos', close:'Cerrar', noinsc:'No hay transcripción de la inscripción en las fuentes.',
    attribution:'Datos: © <a href="https://www.openstreetmap.org/copyright">colaboradores de OpenStreetMap</a> (ODbL), <a href="https://www.wikidata.org">Wikidata</a> (CC0), Koordinierungsstelle Stolpersteine Berlin (CC BY) y conjuntos municipales abiertos (dl-de/zero-2-0, dl-de/by-2-0, CC BY 4.0, CC0). Mapa base © OpenStreetMap.',
    aboutHtml:m=>`<h2>Acerca de este mapa</h2><p>Los <em>Stolpersteine</em> («piedras de tropiezo») son placas de latón del artista Gunter Demnig, colocadas frente al último domicilio elegido libremente por personas perseguidas, deportadas o asesinadas por el nazismo.</p>
      <p>Este mapa reúne <strong>${m.count}</strong> placas en Alemania, Países Bajos, Francia, Austria, Noruega, Chequia, Italia, España, Bélgica, Luxemburgo, Hungría, Lituania, Suiza, Polonia, Eslovaquia, Jersey, Croacia, Dinamarca, Guernsey, Finlandia, Andorra, Irlanda, Suecia, Letonia, Rumanía, Reino Unido y Liechtenstein. De ellas, <strong>${m.odbl_count}</strong> proceden de OpenStreetMap (instantánea ${m.osm_snapshot.slice(0,10)} para Alemania, Irlanda, Suecia, Jersey, Finlandia y Rumanía; ${(m.v20_added||{}).snapshot_osm.slice(0,10)}, refrescada el 2026-11-20, para el resto) y Wikidata (${(m.wikidata_added||{}).snapshot||m.wikidata_snapshot} para esos países; ${(m.v20_added||{}).snapshot_wikidata} para el resto); <strong>${m.berlin_count}</strong> de la lista abierta de Stolpersteine de Berlín (Creative Commons Attribution, cc-by); <strong>${m.koeln_count}</strong> de la de Colonia (Datenlizenz Deutschland – Zero – Version 2.0); y <strong>${m.v22_count}</strong> de trece conjuntos municipales abiertos añadidos en v22: Den Haag, Krefeld, Mönchengladbach, Monza e Brianza, Viersen, Firenze, Moers (GDI-DE), Xanten, Grevenbroich, Memmingen, Erkrath, Dresden y Dormagen (Aachen y Schwalmtal también comprobadas, sin placas nuevas). <strong>No están todas</strong>: según la Stiftung Spuren – Gunter Demnig hay más de 116.000 Stolpersteine en Europa, la mayoría en Alemania, y muchas aún no están registradas en datos abiertos. Si no encuentra a su familiar, consulte también <a href="https://www.stolpersteine.eu">stolpersteine.eu</a> y las iniciativas locales (p. ej. <a href="https://www.stolpersteine-berlin.de">Berlín</a>, <a href="https://www.stolpersteine-hamburg.de">Hamburgo</a>).</p>
      <p>Ningún dato ha sido inventado: cada campo procede de las fuentes citadas. Pueden existir errores o duplicados; las correcciones de las placas de OpenStreetMap o Wikidata se hacen en esas fuentes, y las de las listas municipales abiertas (Berlín, Colonia, Den Haag, Krefeld, Mönchengladbach, Monza e Brianza, Viersen, Firenze, Moers, Xanten, Grevenbroich, Memmingen, Erkrath, Dresden y Dormagen) en los portales de origen o avisándonos.</p>
      <p>Posición en el mapa: las columnas se dibujan, en general, sobre la acera. Si el punto registrado cae dentro de un edificio de OpenStreetMap o a menos de medio metro de su fachada, solo se desplaza el dibujo hacia la calle: normalmente menos de 25 m; en 292 placas (grupos grandes o calles sin hueco tras la regla de calzada de v20r4) el dibujo queda más lejos, hasta unos 47 m (lista en «excepciones-25m-v20.csv»), y en 109 no se ha podido dejar medio metro libre (lista en «residuales-acera-v20.csv»). Las que quedarían sobre la calzada de una vía rodada sin hueco de acera se listan en «calzada-v20.csv». Las coordenadas de los datos y de los enlaces «Cómo llegar» siguen siendo las originales.</p>
      <p>Licencias: las placas de OpenStreetMap y Wikidata (<a href="data/stones.json">data/stones.json</a>, <a href="api/v1/odbl/index.json">api/v1/odbl</a>) están bajo <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a>. Las añadidas de la lista abierta de Berlín (<a href="data/berlin-added-20261121.json">data/berlin-added-20261121.json</a>, <a href="api/v1/cc-by/index.json">api/v1/cc-by</a>) son <a href="https://opendefinition.org/licenses/cc-by/">Creative Commons Attribution (cc-by)</a>, atribución: Koordinierungsstelle Stolpersteine Berlin; no se copian las biografías de stolpersteine-berlin.de. Las de Colonia, Mönchengladbach, Krefeld, Viersen, Moers (GDI-DE), Xanten, Erkrath y Dormagen (<a href="api/v1/dl-de-zero/index.json">api/v1/dl-de-zero</a>) están bajo la <a href="https://www.govdata.de/dl-de/zero-2-0">Datenlizenz Deutschland – Zero – Version 2.0</a>; Dresden (<a href="api/v1/dl-de-by/index.json">api/v1/dl-de-by</a>) bajo <a href="https://www.govdata.de/dl-de/by-2-0">dl-de/by-2-0</a> (Datenquelle: Landeshauptstadt Dresden, dl-de/by-2-0, opendata.dresden.de); Den Haag, Memmingen (Geodaten Stadt Memmingen) y Firenze (<a href="api/v1/cc-by-4/index.json">api/v1/cc-by-4</a>) bajo <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>; Monza e Brianza (Provincia di Monza e della Brianza) y Grevenbroich (<a href="api/v1/cc0-opendata/index.json">api/v1/cc0-opendata</a>) bajo <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>. Fotos: Wikimedia Commons, cada una con su propia licencia. Detalle en <a href="LICENCIAS.md">LICENCIAS.md</a>.</p>`
  },
  de: {
    title:'Kauffmann-Liste', subtitle:'Stolpersteine in Deutschland und 26 weiteren Ländern Europas · Ein Name, ein Leben.',
    searchLabel:'Nach Namen suchen', searchPh:'Vorname, Nachname oder Straße…', cityLabel:'Ort', cityPh:'Nach Ort filtern (optional)',
    loading:'Stolpersteine werden geladen…', ready:n=>`${n} Stolpersteine auf der Karte. Geben Sie einen Namen ein.`,
    results:(n,more)=>`${n}${more?'+':''} Treffer`, none:'Keine Treffer. Versuchen Sie eine andere Schreibweise, nur den Nachnamen oder entfernen Sie den Ortsfilter.',
    similar:'(ähnliche Schreibweisen)', back:'← Zurück zu den Treffern', inscription:'Inschrift', address:'Adresse', country:'Land', countryName:{DE:'Deutschland',NL:'Niederlande',FR:'Frankreich',AT:'Österreich',NO:'Norwegen',CZ:'Tschechien',IT:'Italien',ES:'Spanien',BE:'Belgien',LU:'Luxemburg',HU:'Ungarn',LT:'Litauen',CH:'Schweiz',PL:'Polen',SK:'Slowakei',JE:'Jersey',HR:'Kroatien',DK:'Dänemark',GG:'Guernsey',FI:'Finnland',AD:'Andorra',IE:'Irland',SE:'Schweden',LV:'Lettland',RO:'Rumänien',GB:'Vereinigtes Königreich',LI:'Liechtenstein'}, place:'Ort', district:'Stadtteil',
    born:'Geboren', died:'Gestorben', laid:'Verlegt', type:'Art', threshold:'Stolperschwelle',
    photo:'Foto des Steins: Wikimedia Commons — Urheber und Lizenz ansehen', bio:'Biografie und Quellen', research:'In den Quellen suchen',
    researchNote:'Externe Links; die Kauffmann-Liste kopiert deren Daten nicht.',
    gb:'Gedenkbuch des Bundesarchivs', yv:'Yad Vashem — Zentrale Datenbank der Namen der Holocaustopfer', ushmm:'USHMM — Holocaust Survivors and Victims Database', arolsen:'Arolsen Archives',
    gbSearch:'Im Gedenkbuch suchen', yvSearch:'Bei Yad Vashem suchen', ushmmSearch:'Beim USHMM suchen', arolsenSearch:'In den Arolsen Archives suchen',
    gbSearchPage:'Gedenkbuch (Bundesarchiv): Suchseite öffnen (der Name wird nicht vorausgefüllt)',
    arolsenSearchName:n=>`„${n}“ in den Arolsen Archives suchen`,
    yvSearchName:n=>`„${n}“ bei Yad Vashem suchen (Zentrale Datenbank der Namen der Holocaustopfer)`,
    ushmmSearchName:n=>`„${n}“ beim USHMM suchen (Holocaust Survivors and Victims Database)`,
    hhSearchName:n=>`„${n}“ bei Stolpersteine Hamburg suchen`,
    beSearchName:n=>`„${n}“ bei Stolpersteine Berlin suchen`,
    share:'Link zu diesem Stein kopieren', copied:'Link kopiert', copyName:'Namen kopieren', nameCopied:'Name kopiert',
    directions:'Route (Google Maps)', osmDir:'Route (OpenStreetMap)', sources:'Quellen dieses Eintrags', derived:'(Ort aus benachbarten Steinen abgeleitet)', posApprox:'Ungefähre Position (Gebäude laut Adresse in OpenStreetMap)', posApproxPhoto:'Ungefähre Position (die des Fotos des Steins auf Wikimedia Commons, mit der Adresse in OpenStreetMap geprüft)', posLabel:'Position',
    discTitle:'Die Quellen widersprechen sich', discBody:(a,alt)=>`Dieser Eintrag zeigt Adresse und Position aus OpenStreetMap („${a}“; der Punkt liegt an dieser Straße). Andere Quellen nennen „${alt}“ (etwa 250–330 m entfernt). Wo der Stein wirklich liegt, ist nicht sicher. Der Quellpunkt ist unverändert; nur die Darstellung ist etwa 0,85 m auf den Gehweg versetzt, damit sie nicht auf der Fassade liegt.`, discAlt:alt=>`Nennen „${alt}“:`, discMain:a=>`Nennen „${a}“:`,
    about:'Über die Daten', close:'Schließen', noinsc:'Für diesen Stein ist in den Quellen keine Inschrift erfasst.',
    attribution:'Daten: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap-Mitwirkende</a> (ODbL), <a href="https://www.wikidata.org">Wikidata</a> (CC0), Koordinierungsstelle Stolpersteine Berlin (CC BY) und offene kommunale Datensätze (dl-de/zero-2-0, dl-de/by-2-0, CC BY 4.0, CC0). Kartengrundlage © OpenStreetMap.',
    aboutHtml:m=>`<h2>Über diese Karte</h2><p>Stolpersteine sind Gedenktafeln aus Messing des Künstlers Gunter Demnig, verlegt vor dem letzten frei gewählten Wohnort von Menschen, die im Nationalsozialismus verfolgt, deportiert oder ermordet wurden.</p>
      <p>Diese Karte zeigt <strong>${m.count}</strong> Steine in Deutschland, Niederlande, Frankreich, Österreich, Norwegen, Tschechien, Italien, Spanien, Belgien, Luxemburg, Ungarn, Litauen, Schweiz, Polen, Slowakei, Jersey, Kroatien, Dänemark, Guernsey, Finnland, Andorra, Irland, Schweden, Lettland, Rumänien, Vereinigtes Königreich und Liechtenstein. Davon stammen <strong>${m.odbl_count}</strong> aus OpenStreetMap (Stand ${m.osm_snapshot.slice(0,10)} für Deutschland, Irland, Schweden, Jersey, Finnland und Rumänien; ${(m.v20_added||{}).snapshot_osm.slice(0,10)}, am 2026-11-20 aufgefrischt, für die übrigen) und Wikidata (${(m.wikidata_added||{}).snapshot||m.wikidata_snapshot} für diese Länder; ${(m.v20_added||{}).snapshot_wikidata} für die übrigen); <strong>${m.berlin_count}</strong> aus der offenen Berliner Stolperstein-Liste (Creative Commons Attribution, cc-by); <strong>${m.koeln_count}</strong> aus der Kölner Liste (Datenlizenz Deutschland – Zero – Version 2.0); sowie <strong>${m.v22_count}</strong> aus dreizehn in v22 ergänzten offenen kommunalen Datensätzen: Den Haag, Krefeld, Mönchengladbach, Monza e Brianza, Viersen, Florenz, Moers (GDI-DE), Xanten, Grevenbroich, Memmingen, Erkrath, Dresden und Dormagen (Aachen und Schwalmtal ebenfalls geprüft, ohne neue Steine). <strong>Sie ist unvollständig</strong>: Laut Stiftung Spuren – Gunter Demnig liegen über 116.000 Stolpersteine in Europa, die meisten in Deutschland. Finden Sie einen Namen nicht, sehen Sie bitte auch bei <a href="https://www.stolpersteine.eu">stolpersteine.eu</a> und den lokalen Initiativen nach (z. B. <a href="https://www.stolpersteine-berlin.de">Berlin</a>, <a href="https://www.stolpersteine-hamburg.de">Hamburg</a>).</p>
      <p>Es wurden keine Angaben erfunden; jedes Feld stammt aus den genannten Quellen. Fehler oder Doppelungen sind möglich; Korrekturen an Einträgen aus OpenStreetMap oder Wikidata gehören dorthin, Korrekturen an den kommunalen offenen Listen (Berlin, Köln, Den Haag, Krefeld, Mönchengladbach, Monza e Brianza, Viersen, Florenz, Moers, Xanten, Grevenbroich, Memmingen, Erkrath, Dresden und Dormagen) in die jeweiligen Quellportale oder an uns.</p>
      <p>Position auf der Karte: Die Säulen stehen in der Regel auf dem Gehweg. Liegt ein erfasster Punkt in einem OpenStreetMap-Gebäude oder weniger als einen halben Meter von dessen Fassade entfernt, wird nur die Darstellung zur Straße hin verschoben: normalerweise weniger als 25 m; bei 292 Steinen (große Gruppen oder Straßen ohne freie Stelle nach der Fahrbahnregel von v20r4) liegt die Darstellung weiter entfernt, bis etwa 47 m (Liste in „excepciones-25m-v20.csv“), und bei 109 ließ sich kein halber Meter Abstand freihalten (Liste in „residuales-acera-v20.csv“). Steine auf der Fahrbahn ohne Gehwegplatz stehen in „calzada-v20.csv“. Die Koordinaten in den Daten und in den Routenlinks bleiben die ursprünglichen.</p>
      <p>Lizenzen: Die Stolpersteine aus OpenStreetMap und Wikidata (<a href="data/stones.json">data/stones.json</a>, <a href="api/v1/odbl/index.json">api/v1/odbl</a>) stehen unter der <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a>. Die zusätzlich übernommenen Einträge der Berliner Open-Data-Liste (<a href="data/berlin-added-20261121.json">data/berlin-added-20261121.json</a>, <a href="api/v1/cc-by/index.json">api/v1/cc-by</a>) stehen unter <a href="https://opendefinition.org/licenses/cc-by/">Creative Commons Attribution (cc-by)</a>, Namensnennung: Koordinierungsstelle Stolpersteine Berlin; die biografischen Texte von stolpersteine-berlin.de werden nicht übernommen. Die Einträge für Köln, Mönchengladbach, Krefeld, Viersen, Moers (GDI-DE), Xanten, Erkrath und Dormagen (<a href="api/v1/dl-de-zero/index.json">api/v1/dl-de-zero</a>) stehen unter <a href="https://www.govdata.de/dl-de/zero-2-0">dl-de/zero-2-0</a>; Dresden (<a href="api/v1/dl-de-by/index.json">api/v1/dl-de-by</a>) unter <a href="https://www.govdata.de/dl-de/by-2-0">dl-de/by-2-0</a> (Datenquelle: Landeshauptstadt Dresden, dl-de/by-2-0, opendata.dresden.de); Den Haag, Memmingen (Geodaten Stadt Memmingen) und Florenz (<a href="api/v1/cc-by-4/index.json">api/v1/cc-by-4</a>) unter <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>; Monza e Brianza (Provincia di Monza e della Brianza) sowie Grevenbroich (<a href="api/v1/cc0-opendata/index.json">api/v1/cc0-opendata</a>) unter <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>. Fotos: Wikimedia Commons mit jeweils eigener Lizenz. Einzelheiten in <a href="LICENCIAS.md">LICENCIAS.md</a>.</p>`
  },
  en: {
    title:'Kauffmann List', subtitle:'Stolpersteine in Germany and 26 other European countries · One name, one life.',
    searchLabel:'Search by name', searchPh:'First name, surname or street…', cityLabel:'Place', cityPh:'Filter by place (optional)',
    loading:'Loading stones…', ready:n=>`${n} stones on the map. Type a name to search.`,
    results:(n,more)=>`${n}${more?'+':''} result${n===1?'':'s'}`, none:'No results. Try another spelling, the surname only, or clear the place filter.',
    similar:'(similar spellings)', back:'← Back to results', inscription:'Inscription', address:'Address', country:'Country', countryName:{DE:'Germany',NL:'Netherlands',FR:'France',AT:'Austria',NO:'Norway',CZ:'Czechia',IT:'Italy',ES:'Spain',BE:'Belgium',LU:'Luxembourg',HU:'Hungary',LT:'Lithuania',CH:'Switzerland',PL:'Poland',SK:'Slovakia',JE:'Jersey',HR:'Croatia',DK:'Denmark',GG:'Guernsey',FI:'Finland',AD:'Andorra',IE:'Ireland',SE:'Sweden',LV:'Latvia',RO:'Romania',GB:'United Kingdom',LI:'Liechtenstein'}, place:'Place', district:'District',
    born:'Born', died:'Died', laid:'Stone laid', type:'Type', threshold:'Stolperschwelle (memorial threshold)',
    photo:'Photo of the stone: Wikimedia Commons — see author and licence', bio:'Biography and sources', research:'Search the sources',
    researchNote:'External links; the Kauffmann List does not copy their data.',
    gb:'German Federal Archives Memorial Book (Gedenkbuch)', yv:'Yad Vashem — Central Database of Shoah Victims’ Names', ushmm:'USHMM — Holocaust Survivors and Victims Database', arolsen:'Arolsen Archives',
    gbSearch:'Search the Gedenkbuch', yvSearch:'Search Yad Vashem', ushmmSearch:'Search USHMM', arolsenSearch:'Search Arolsen Archives',
    gbSearchPage:'Gedenkbuch (Bundesarchiv): open the search page (the name is not pre-filled)',
    arolsenSearchName:n=>`Search “${n}” in the Arolsen Archives`,
    yvSearchName:n=>`Search “${n}” in Yad Vashem (Central Database of Shoah Victims’ Names)`,
    ushmmSearchName:n=>`Search “${n}” in the USHMM Holocaust Survivors and Victims Database`,
    hhSearchName:n=>`Search “${n}” on Stolpersteine Hamburg`,
    beSearchName:n=>`Search “${n}” on Stolpersteine Berlin`,
    share:'Copy link to this stone', copied:'Link copied', copyName:'Copy name', nameCopied:'Name copied',
    directions:'Directions (Google Maps)', osmDir:'Directions (OpenStreetMap)', sources:'Sources for this record', derived:'(place inferred from nearby stones)', posApprox:'Approximate position (the building, from its address in OpenStreetMap)', posApproxPhoto:'Approximate position (that of the stone’s photo on Wikimedia Commons, checked against the address in OpenStreetMap)', posLabel:'Position',
    discTitle:'Sources disagree', discBody:(a,alt)=>`This record shows the address and position from OpenStreetMap (“${a}”; the point lies on that street). Other sources give “${alt}” (about 250–330 m away). It is not certain where the stone is. The source point is untouched; only the drawing is shifted about 0.85 m onto the pavement so it does not sit on the façade.`, discAlt:alt=>`Give “${alt}”:`, discMain:a=>`Give “${a}”:`,
    about:'About the data', close:'Close', noinsc:'No transcription of the inscription in the sources.',
    attribution:'Data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> (ODbL), <a href="https://www.wikidata.org">Wikidata</a> (CC0), Koordinierungsstelle Stolpersteine Berlin (CC BY) and municipal open datasets (dl-de/zero-2-0, dl-de/by-2-0, CC BY 4.0, CC0). Base map © OpenStreetMap.',
    aboutHtml:m=>`<h2>About this map</h2><p>Stolpersteine (“stumbling stones”) are brass plaques by the artist Gunter Demnig, set in front of the last freely chosen home of people persecuted, deported or murdered under National Socialism.</p>
      <p>This map shows <strong>${m.count}</strong> stones in Germany, Netherlands, France, Austria, Norway, Czechia, Italy, Spain, Belgium, Luxembourg, Hungary, Lithuania, Switzerland, Poland, Slovakia, Jersey, Croatia, Denmark, Guernsey, Finland, Andorra, Ireland, Sweden, Latvia, Romania, United Kingdom and Liechtenstein. Of these, <strong>${m.odbl_count}</strong> come from OpenStreetMap (snapshot ${m.osm_snapshot.slice(0,10)} for Germany, Ireland, Sweden, Jersey, Finland and Romania; ${(m.v20_added||{}).snapshot_osm.slice(0,10)}, refreshed on 2026-11-20, for the rest) and Wikidata (${(m.wikidata_added||{}).snapshot||m.wikidata_snapshot} for those countries; ${(m.v20_added||{}).snapshot_wikidata} for the rest); <strong>${m.berlin_count}</strong> from Berlin’s open Stolpersteine list (Creative Commons Attribution, cc-by); <strong>${m.koeln_count}</strong> from the Cologne list (Data licence Germany – Zero – Version 2.0); and <strong>${m.v22_count}</strong> from thirteen municipal open datasets added in v22: Den Haag, Krefeld, Mönchengladbach, Monza e Brianza, Viersen, Florence, Moers (GDI-DE), Xanten, Grevenbroich, Memmingen, Erkrath, Dresden and Dormagen (Aachen and Schwalmtal also checked, 0 new stones). <strong>It is incomplete</strong>: according to Stiftung Spuren – Gunter Demnig there are over 116,000 Stolpersteine in Europe, most of them in Germany. If you cannot find a name, please also check <a href="https://www.stolpersteine.eu">stolpersteine.eu</a> and local initiatives (e.g. <a href="https://www.stolpersteine-berlin.de">Berlin</a>, <a href="https://www.stolpersteine-hamburg.de">Hamburg</a>).</p>
      <p>No data has been invented; every field comes from the cited sources. Errors or duplicates are possible; corrections to OpenStreetMap or Wikidata plaques belong there, and corrections to the municipal open-data lists (Berlin, Cologne, Den Haag, Krefeld, Mönchengladbach, Monza e Brianza, Viersen, Florence, Moers, Xanten, Grevenbroich, Memmingen, Erkrath, Dresden and Dormagen) belong in their source portals or with us.</p>
      <p>Position on the map: the columns are, in general, drawn on the pavement. If a recorded point falls inside an OpenStreetMap building or less than half a metre from its façade, only the drawing is moved towards the street: normally less than 25 m; for 292 stones (large groups or streets with no free spot after the v20r4 roadway rule) the drawing ends up further away, up to about 47 m (list in “excepciones-25m-v20.csv”), and for 109 half a metre of clearance could not be kept (list in “residuales-acera-v20.csv”). Stones that would sit on a carriageway with no sidewalk spot are listed in “calzada-v20.csv”. The coordinates in the data and in the directions links stay the original ones.</p>
      <p>Licences: plaques from OpenStreetMap and Wikidata (<a href="data/stones.json">data/stones.json</a>, <a href="api/v1/odbl/index.json">api/v1/odbl</a>) are under <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a>. Those added from Berlin’s open list (<a href="data/berlin-added-20261121.json">data/berlin-added-20261121.json</a>, <a href="api/v1/cc-by/index.json">api/v1/cc-by</a>) are under <a href="https://opendefinition.org/licenses/cc-by/">Creative Commons Attribution (cc-by)</a>, attribution: Koordinierungsstelle Stolpersteine Berlin; biographies from stolpersteine-berlin.de are not copied. Entries for Cologne, Mönchengladbach, Krefeld, Viersen, Moers (GDI-DE), Xanten, Erkrath and Dormagen (<a href="api/v1/dl-de-zero/index.json">api/v1/dl-de-zero</a>) are under <a href="https://www.govdata.de/dl-de/zero-2-0">dl-de/zero-2-0</a>; Dresden (<a href="api/v1/dl-de-by/index.json">api/v1/dl-de-by</a>) under <a href="https://www.govdata.de/dl-de/by-2-0">dl-de/by-2-0</a> (Datenquelle: Landeshauptstadt Dresden, dl-de/by-2-0, opendata.dresden.de); Den Haag, Memmingen (Geodaten Stadt Memmingen) and Florence (<a href="api/v1/cc-by-4/index.json">api/v1/cc-by-4</a>) under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>; Monza e Brianza (Provincia di Monza e della Brianza) and Grevenbroich (<a href="api/v1/cc0-opendata/index.json">api/v1/cc0-opendata</a>) under <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>. Photos: Wikimedia Commons, each under its own licence. Details in <a href="LICENCIAS.md">LICENCIAS.md</a>.</p>`
  }
};
/* ---- additions for the 3D view ---- */
const EXTRA = {
  es:{ remember:'Recordar a todos', baseNight:'Noche', baseDay:'Día', baseHoy:'Hoy', baseSat:'2016', sourcesBtn:'Fuentes', pause:'Pausar', resume:'Continuar', exit:'Salir',
       replay:'Introducción', project:'Sobre el proyecto', dlGeo:'Descargar GeoJSON', dlKml:'Descargar KML',
       classic:'Mapa clásico 2D', dataapi:'Datos abiertos y API', searchPh:'Nombre, apellido o dirección (calle y ciudad)…',
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
       attribution3d:'Datos: © <a href="https://www.openstreetmap.org/copyright">colaboradores de OpenStreetMap</a> (ODbL), <a href="https://www.wikidata.org">Wikidata</a> (CC0), Koordinierungsstelle Stolpersteine Berlin (CC BY) y conjuntos municipales abiertos (dl-de/zero-2-0, dl-de/by-2-0, CC BY 4.0, CC0). Mapa base: <a href="https://openfreemap.org">OpenFreeMap</a> © OpenMapTiles.' },
  de:{ remember:'Aller gedenken', baseNight:'Nacht', baseDay:'Tag', baseHoy:'Heute', baseSat:'2016', sourcesBtn:'Quellen', pause:'Anhalten', resume:'Fortsetzen', exit:'Beenden',
       replay:'Einführung', project:'Über das Projekt', dlGeo:'GeoJSON herunterladen', dlKml:'KML herunterladen',
       classic:'Klassische 2D-Karte', dataapi:'Offene Daten und API', searchPh:'Vorname, Nachname oder Adresse (Straße und Ort)…',
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
       attribution3d:'Daten: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap-Mitwirkende</a> (ODbL), <a href="https://www.wikidata.org">Wikidata</a> (CC0), Koordinierungsstelle Stolpersteine Berlin (CC BY) und offene kommunale Datensätze (dl-de/zero-2-0, dl-de/by-2-0, CC BY 4.0, CC0). Karte: <a href="https://openfreemap.org">OpenFreeMap</a> © OpenMapTiles.' },
  en:{ remember:'Remember them all', baseNight:'Night', baseDay:'Day', baseHoy:'Today', baseSat:'2016', sourcesBtn:'Sources', pause:'Pause', resume:'Resume', exit:'Exit',
       replay:'Introduction', project:'About the project', dlGeo:'Download GeoJSON', dlKml:'Download KML',
       classic:'Classic 2D map', dataapi:'Open data and API', searchPh:'First name, surname or address (street and city)…',
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
       attribution3d:'Data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> (ODbL), <a href="https://www.wikidata.org">Wikidata</a> (CC0), Koordinierungsstelle Stolpersteine Berlin (CC BY) and municipal open datasets (dl-de/zero-2-0, dl-de/by-2-0, CC BY 4.0, CC0). Base map: <a href="https://openfreemap.org">OpenFreeMap</a> © OpenMapTiles.' }
};
for (const l in EXTRA) Object.assign(I18N[l], EXTRA[l]);
Object.assign(I18N.es, {pitchTo3d:'3D: ver en ángulo', pitchTo2d:'2D: ver desde arriba', pitchFlatOnly:'La foto de 1945 se ve solo desde arriba', rotLeft:'Girar a la izquierda', rotNorth:'Mirar al norte', rotNorthDeg:d=>`Mirar al norte (${d}°)`, rotRight:'Girar a la derecha', sheetCollapsed:'Buscar · Países'});
Object.assign(I18N.de, {pitchTo3d:'3D: schräg ansehen', pitchTo2d:'2D: von oben ansehen', pitchFlatOnly:'Das Luftbild von 1945 gibt es nur von oben', rotLeft:'Nach links drehen', rotNorth:'Nach Norden ausrichten', rotNorthDeg:d=>`Nach Norden ausrichten (${d}°)`, rotRight:'Nach rechts drehen', sheetCollapsed:'Suche · Länder'});
Object.assign(I18N.en, {pitchTo3d:'3D: view at an angle', pitchTo2d:'2D: view from above', pitchFlatOnly:'The 1945 photo can only be viewed from above', rotLeft:'Rotate left', rotNorth:'Face north', rotNorthDeg:d=>`Face north (${d}°)`, rotRight:'Rotate right', sheetCollapsed:'Search · Countries'});
// Privacy note in «Acerca de»: honest in both states of the visit counter (counter.js; own counter in contador/, on since v13).
Object.assign(I18N.es, {privacyHtml:on=>on
  ? '<p><strong>Privacidad.</strong> Sin cookies, sin publicidad y sin perfiles. Contamos las visitas con un contador propio (código abierto, en una cuenta personal de Cloudflare): solo se envía la sección visitada, nunca el nombre buscado ni la ficha abierta. Como cualquier servidor, Cloudflare recibe la dirección IP y el navegador para entregar la petición; nuestro contador no los lee ni los guarda, no tiene registros activados y solo guarda el número de visitas por día. Si su navegador pide «no rastrear», su visita no se cuenta.</p>'
  : '<p><strong>Privacidad.</strong> Sin cookies, sin publicidad, sin rastreadores y sin contador de visitas.</p>'});
Object.assign(I18N.de, {privacyHtml:on=>on
  ? '<p><strong>Datenschutz.</strong> Keine Cookies, keine Werbung, keine Profile. Besuche zählen wir mit einem eigenen Zähler (offener Code, in einem persönlichen Cloudflare-Konto): Übermittelt wird nur der besuchte Bereich, nie der gesuchte Name oder die geöffnete Karte. Wie jeder Server erhält Cloudflare IP-Adresse und Browser, um die Anfrage zuzustellen; unser Zähler liest und speichert sie nicht, hat keine Protokolle eingeschaltet und speichert nur die Zahl der Besuche pro Tag. Wenn Ihr Browser „Do Not Track“ sendet, wird Ihr Besuch nicht gezählt.</p>'
  : '<p><strong>Datenschutz.</strong> Keine Cookies, keine Werbung, keine Tracker und kein Besucherzähler.</p>'});
Object.assign(I18N.en, {privacyHtml:on=>on
  ? '<p><strong>Privacy.</strong> No cookies, no ads, no profiles. We count visits with our own counter (open code, in a personal Cloudflare account): only the section visited is sent, never the name searched or the record opened. Like any server, Cloudflare receives the IP address and browser in order to deliver the request; our counter does not read or store them, has logging switched off and stores only the number of visits per day. If your browser sends “Do Not Track”, your visit is not counted.</p>'
  : '<p><strong>Privacy.</strong> No cookies, no ads, no trackers and no visit counter.</p>'});
// Source links (audits A/B/C, 17-11-2026): accurate wording, neutral scope note, no claim about OSM/Wikidata.
Object.assign(I18N.es, {
  researchNote:'Enlaces a archivos e iniciativas externos. La Lista Kauffmann no copia sus datos: solo enlaza. Al abrir un enlace de búsqueda, el nombre se envía a ese sitio.',
  scopeNote:'Yad Vashem y el Gedenkbuch registran a las víctimas judías de la persecución nazi; las personas perseguidas por otros motivos pueden no figurar allí.',
  berlinBio:'Biografía de la iniciativa Stolpersteine in Berlin', hamburgBio:'Biografía de la iniciativa Stolpersteine Hamburg', bremenBio:'Biografía de la iniciativa Stolpersteine Bremen'});
Object.assign(I18N.de, {
  researchNote:'Links zu externen Archiven und Initiativen. Die Kauffmann-Liste kopiert deren Daten nicht, sie verlinkt nur. Beim Öffnen eines Such-Links wird der Name an diese Website übermittelt.',
  scopeNote:'Yad Vashem und das Gedenkbuch verzeichnen die jüdischen Opfer der NS-Verfolgung; aus anderen Gründen verfolgte Menschen sind dort möglicherweise nicht erfasst.',
  yv:'Yad Vashem — Central Database of Shoah Victims’ Names',
  yvSearchName:n=>`„${n}“ bei Yad Vashem suchen (Central Database of Shoah Victims’ Names)`,
  berlinBio:'Biografie bei Stolpersteine in Berlin', hamburgBio:'Biografie bei Stolpersteine Hamburg', bremenBio:'Biografie bei Stolpersteine Bremen'});
Object.assign(I18N.en, {
  researchNote:'Links to external archives and initiatives. The Kauffmann List does not copy their data; it only links to them. When you open a search link, the name is sent to that site.',
  scopeNote:'Yad Vashem and the Gedenkbuch record the Jewish victims of Nazi persecution; people persecuted for other reasons may not be listed there.',
  berlinBio:'Biography by the Stolpersteine in Berlin initiative', hamburgBio:'Biography by the Stolpersteine Hamburg initiative', bremenBio:'Biography by the Stolpersteine Bremen initiative'});

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
  document.querySelectorAll('[data-i18n-aria]').forEach(el => { const v=T(el.dataset.i18nAria); if (typeof v==='string' && v) { el.setAttribute('aria-label', v); if (el.tagName === 'BUTTON') el.title = v; } });
  document.querySelectorAll('.lang button').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === lang));
  document.title = T('title');
  if (typeof updatePitchBtn === 'function') updatePitchBtn();
  if (window.KLCols && KLCols.relabel) KLCols.relabel();
}

/* ---------- search (same rules as the 2D map) ---------- */
const COUNTRY_WORDS = {NL:'paises bajos niederlande netherlands holanda holland nederland', FR:'francia frankreich france', AT:'austria osterreich oesterreich', NO:'noruega norwegen norway norge', CZ:'chequia tschechien czechia republica checa czech republic cesko', IT:'italia italien italy', ES:'espana spanien spain', BE:'belgica belgien belgium belgique belgie', LU:'luxemburgo luxemburg luxembourg letzebuerg', HU:'hungria ungarn hungary magyarorszag', LT:'lituania litauen lithuania lietuva', CH:'suiza schweiz switzerland suisse svizzera', PL:'polonia polen poland polska', SK:'eslovaquia slowakei slovakia slovensko', JE:'jersey', HR:'croacia kroatien croatia hrvatska', DK:'dinamarca danemark denmark danmark', GG:'guernsey', FI:'finlandia finnland finland suomi', AD:'andorra', IE:'irlanda irland ireland', SE:'suecia schweden sweden', LV:'letonia lettland latvia latvija', RO:'rumania rumanien romania', GB:'reino unido vereinigtes konigreich united kingdom uk gran bretana great britain england escocia scotland', LI:'liechtenstein'};
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
const countryLabel = s => { const cc=(s.cc||'DE').toUpperCase(); const names=T('countryName')||{}; return names[cc] || cc; };

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
const DE_COLLATOR = typeof Intl !== 'undefined' ? new Intl.Collator('de') : null;
const _foldAddr = t => (t||'').toLowerCase().replace(/ß/g,'ss').replace(/ä/g,'ae').replace(/ö/g,'oe').replace(/ü/g,'ue');
function addrKey(s){
  if (s._ak !== undefined) return s._ak;
  let a = _foldAddr(s.a)
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
  return (s._ak = a);
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
  if (n <= 40){
    for (let i=0;i<n;i++) for (let j=i+1;j<n;j++)
      if (distM(list[i].la,list[i].lo,list[j].la,list[j].lo) <= maxD){
        const a=find(i), b=find(j); if (a!==b) parent[a]=b;
      }
  } else {
    const cell = Math.max(maxD / M_LAT * 3.5, 0.0001);
    const grid = new Map();
    for (let i=0;i<n;i++){
      const k = Math.floor(list[i].la / cell) + ':' + Math.floor(list[i].lo / cell);
      let arr = grid.get(k); if (!arr){ arr = []; grid.set(k, arr); }
      arr.push(i);
    }
    for (let i=0;i<n;i++){
      const a0 = Math.floor(list[i].la / cell), b0 = Math.floor(list[i].lo / cell);
      for (let di=-1;di<=1;di++) for (let dj=-1;dj<=1;dj++){
        const arr = grid.get((a0+di) + ':' + (b0+dj));
        if (!arr) continue;
        for (const j of arr) if (j > i && distM(list[i].la,list[i].lo,list[j].la,list[j].lo) <= maxD){
          const a=find(i), b=find(j); if (a!==b) parent[a]=b;
        }
      }
    }
  }
  const m = new Map();
  list.forEach((s,i)=> (m.get(find(i)) || m.set(find(i),[]).get(find(i))).push(s));
  return [...m.values()];
}
// Name/date comparison for the display-only merge lives in dedupe.js (KLDedupe), tested in tests/dedupe-test.mjs.
const samePerson = (a,b) => KLDedupe.samePerson(a,b);
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
  if (!pri.a && o.a){ pri.a = o.a; delete pri._ak; }
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

const ADDED_SRCS = new Set([
  'berlin', 'koeln', 'moenchengladbach', 'denhaag', 'krefeld', 'monza', 'viersen',
  'memmingen', 'moers', 'grevenbroich', 'firenze', 'xanten', 'dresden', 'erkrath', 'dormagen'
]);
const ADDED_ID_RE = /^(ber-|koeln-|mg-|dh-|kr-|mz-|vie-|mm-|mo-|gv-|fi-|xa-|dr-|erk-|dor-)/;
const ADDED_SOURCE_META = {
  berlin: { label: 'Liste der Stolpersteine Berlin (Open Data, CC BY)', url: 'https://daten.berlin.de/datensaetze/liste-der-stolpersteine-berlin', lbLabel: 'berlinBio' },
  koeln: { label: 'Stolpersteine Köln (Open.NRW, dl-de/zero-2-0)', url: 'https://open.nrw/dataset/stolpersteine-koln-k', lbName: 'NS-Dokumentationszentrum der Stadt Köln' },
  moenchengladbach: { label: 'Stolpersteine Mönchengladbach (Open.NRW, dl-de/zero-2-0)', url: 'https://ckan.open.nrw.de/dataset/59e9bcd1-8096-42da-83ff-10d84f867093' },
  denhaag: { label: 'Stolpersteine Den Haag (CC BY 4.0)', url: 'https://data.overheid.nl/dataset/stolpersteine' },
  krefeld: { label: 'Stolpersteine Krefeld (Offene Geodaten, dl-de/zero-2-0)', url: 'https://www.krefeld.de/de/vermessung/digitale-geodaten/', lbName: 'Stadt Krefeld' },
  monza: { label: "Pietre d'inciampo Monza e Brianza (Provincia di Monza e della Brianza, CC0 1.0)", url: 'https://www.dati.lombardia.it/d/42ik-bq75', lbName: 'Provincia di Monza e della Brianza' },
  viersen: { label: 'Stolpersteine Viersen (GDI-DE, dl-de/zero-2-0)', url: 'https://registry.gdi-de.org/id/de.nw/e90f5c3f-ab6b-4c12-a392-b06d617bed83' },
  memmingen: { label: 'Geodaten Stadt Memmingen', url: 'https://open.bydata.de/api/hub/repo/datasets/stolpersteine_01' },
  moers: { label: 'Stolpersteine Moers (GDI-DE, dl-de/zero-2-0)', url: 'https://registry.gdi-de.org/id/de.nw/eaf69e88-5199-46d4-ae77-574fa5c9a0d4' },
  grevenbroich: { label: 'Stolpersteine Grevenbroich (Rhein-Kreis Neuss, CC0 1.0)', url: 'https://opendata.rhein-kreis-neuss.de/explore/dataset/grevenbroich-stolpersteine-gv-18012023/' },
  firenze: { label: "Pietre d'Inciampo Firenze (Comune di Firenze, CC BY 4.0)", url: 'https://dati.toscana.it/dataset/pietre-d-inciampo' },
  xanten: { label: 'Stolpersteine Xanten (GovData, dl-de/zero-2-0)', url: 'https://www.govdata.de/suche/daten/stolpersteine-xanten138aa' },
  dresden: { label: 'Datenquelle: Landeshauptstadt Dresden, dl-de/by-2-0, opendata.dresden.de', url: 'https://opendata.dresden.de/', lbName: 'Stolpersteine Dresden' },
  erkrath: { label: 'Stolpersteine Erkrath (GDI-DE, dl-de/zero-2-0)', url: 'https://registry.gdi-de.org/id/de.nw/6e74ad36-9ad0-488a-a5e1-95352a55b974' },
  dormagen: { label: 'Stolpersteine Dormagen (Rhein-Kreis Neuss, dl-de/zero-2-0)', url: 'https://opendata.rhein-kreis-neuss.de/explore/dataset/dormagen-stolpersteine/' }
};
function isAddedStone(s){
  return !!(s._added || ADDED_SRCS.has(s.src) || ADDED_ID_RE.test(String(s.id||'')));
}

function buildStones(){
  // v21: el layout de las 72.110 placas de v20 se calcula SOLO con ese conjunto, igual que en
  // b142fa48. Las placas municipales no entran en agrupación, ángulo, cuadrícula ni desplazamiento,
  // y se dibujan exactamente en el dla/dlo (o la/lo) del archivo.
  const baseAll = DATA.filter(s => !isAddedStone(s));
  const addedAll = DATA.filter(isAddedStone);
  for (const s of addedAll){
    delete s._aliasOf; delete s._also; delete s._ids; delete s._n;
  }

  const byAddr = new Map(), noAddr = [];
  for (const s of baseAll){
    const k = addrKey(s);
    if (!k) noAddr.push(s);
    else (byAddr.get(k) || byAddr.set(k,[]).get(k)).push(s);
  }
  let clusters = [];
  for (const [k, list] of byAddr) clusters.push(...clusterByDist(list, /\d/.test(k) ? 15 : 8));
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
  let mergeGroups=0, mergeExtra=0; const mergeDoubt=[];
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
      // Chained matches (A~B, B~C) must also hold for every pair; otherwise, when in doubt, show them all.
      let ok=true;
      for (let i=0;i<recs.length && ok;i++) for (let j=i+1;j<recs.length;j++) if (!samePerson(recs[i],recs[j])){ ok=false; break; }
      if (!ok){ mergeDoubt.push(recs.map(s=>s.id)); continue; }
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
    if (vis.length > 1) vis.sort((a,b)=> (DE_COLLATOR ? DE_COLLATOR.compare((a._n||a.n)||'', (b._n||b.n)||'') : ((a._n||a.n)||'').localeCompare((b._n||b.n)||'','de')) || String(a.id).localeCompare(String(b.id)));
    const la0 = g.reduce((t,s)=>t+s.la,0)/g.length;
    const lo0 = g.reduce((t,s)=>t+s.lo,0)/g.length;
    // v20: grupo «fijo» = todas sus placas traen posición de dibujo calculada en el servidor (dla/dlo, ya fuera de los edificios): la separación de grupos no lo mueve ni lo encoge.
    return {g:vis, all:g, la0, lo0, origLa:la0, origLo:lo0, step:COL_STEP, ang:0, sk:streetKey(g[0]), pinned:!!(typeof META!=='undefined' && META && META.layout_pinned) || g.every(s=>s.sla!=null)};
  });

  // Street direction from our own coordinates (not live OSM tiles: those are only in the current view
  // after the style loads, so they cannot lay out the whole country at start).
  // 1) Principal axis of other houses on the same street within 180 m (needs 3 points, or 2 if >12 m apart).
  // 2) If that fails, the elongated cloud of this house's own recorded points.
  // 3) Smooth with the circular mean of neighbouring angles on the same street (80 m), then north–south if still none.
  function neighbors(pg, i, radius, cell, near){
    const pts=[], idxs=[];
    if (!pg.sk) return {pts, idxs};
    const sm = near.get(pg.sk);
    if (!sm) return {pts, idxs};
    const a0=Math.floor(pg.la0/cell), b0=Math.floor(pg.lo0/cell);
    for (let di=-2;di<=2;di++){
      const row=(a0+di+500000)*1000000;
      for (let dj=-2;dj<=2;dj++){
        const bucket=sm.get(row+(b0+dj+500000));
        if (!bucket) continue;
        for (let k=0;k<bucket.length;k++){
          const j=bucket[k], o=groups[j];
          if (distM(pg.la0,pg.lo0,o.la0,o.lo0)<=radius){ pts.push({la:o.la0, lo:o.lo0}); idxs.push(j); }
        }
      }
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
  groups.forEach((pg,i)=>{
    if (!pg.sk) return;
    let sm=near.get(pg.sk); if (!sm){ sm=new Map(); near.set(pg.sk, sm); }
    const k=(Math.floor(pg.la0/cellA)+500000)*1000000 + (Math.floor(pg.lo0/cellA)+500000);
    let b=sm.get(k); if (!b){ b=[]; sm.set(k,b); }
    b.push(i);
  });
  groups.forEach((pg,i)=>{
    let ang=null;
    if (pg.sk){
      const {pts}=neighbors(pg,i,180,cellA,near);
      if (pts.length>=3) ang=principalAngle(pts);
      else if (pts.length===2 && distM(pts[0].la,pts[0].lo,pts[1].la,pts[1].lo)>12) ang=principalAngle(pts);
    }
    if (ang==null) ang=principalAngle(pg.all);
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
  if (groups.some(pg => !pg.pinned)) for (let iter=0; iter<16; iter++){
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
          if (A.pinned && B.pinned) continue;   // v20: dos grupos fijos no se mueven (el servidor ya los separó)
          const moveA = B.pinned ? true : (A.pinned ? false : A.g.length<=B.g.length);
          if (moveA){ shift[gi].dy+=uy*push; shift[gi].dx+=ux*push; shift[gi].hits++; }
          else { shift[o.gi].dy-=uy*push; shift[o.gi].dx-=ux*push; shift[o.gi].hits++; }
          if (L<5 && (A.g.length>1 || B.g.length>1)){ if (!A.pinned) shrink[gi]=true; if (!B.pinned) shrink[o.gi]=true; }
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

  for (const s of baseAll){
    if (s._aliasOf){ const p=byId.get(s._aliasOf); if (p){ s._dla=p._dla; s._dlo=p._dlo; s._ang=p._ang; } }
  }

  // Placas municipales: alias de una ya publicada (sin alterar el primário) o clavadas al dla/dlo del archivo.
  const baseVis = baseAll.filter(s=>!s._aliasOf);
  const baseByAddr = new Map();
  for (const p of baseVis){
    const k=addrKey(p);
    if (k) (baseByAddr.get(k)||baseByAddr.set(k,[]).get(k)).push(p);
  }
  const baseNoAddr = baseVis.filter(p=>!addrKey(p));
  for (const s of addedAll){
    let pri=null, priD=1e9;
    const ak=addrKey(s);
    const cands = ak ? (baseByAddr.get(ak)||[]) : baseNoAddr;
    for (const p of cands){
      if (!samePerson(s,p)) continue;
      const d=distM(s.la,s.lo,p.la,p.lo);
      if (d>25) continue;
      if (d<priD){ pri=p; priD=d; }
    }
    if (pri){
      s._aliasOf=pri.id;
      s._dla=pri._dla; s._dlo=pri._dlo; s._ang=pri._ang||0;
      fillFrom(pri, s);
      pri._also=(pri._also||[]).concat([s]);
      pri._ids=(pri._ids||[pri.id]).concat([s.id]);
    } else {
      s._dla=s.la; s._dlo=s.lo; s._ang=0;
    }
  }

  VISIBLE = DATA.filter(s=>!s._aliasOf);
  STONES_FC = (typeof window !== 'undefined' && window.KLCols) ? null : {type:'FeatureCollection', features:VISIBLE.map(s => ({type:'Feature', properties:{id:s.id}, geometry:{type:'Polygon', coordinates:square(s._dlo,s._dla,COL_HALF,s._ang)}}))};
  POINTS_FC = {type:'FeatureCollection', features: VISIBLE.map(s=>({type:'Feature', properties:{}, geometry:{type:'Point', coordinates:[s.lo,s.la]}}))};
  LIGHTS_FC = {type:'FeatureCollection', features: groups.map(pg=>({type:'Feature', properties:{n:pg.g.length}, geometry:{type:'Point', coordinates:[pg.lo0, pg.la0]}}))};
  const ise69 = VISIBLE.filter(s => /Isestr/i.test(s.a||'') && /\b69\b/.test(s.a||'')).length;
  groups.forEach((pg,i)=>{ for (const s of pg.g) s._gi=i; });   // v29: grupo de dibujo de cada placa visible de la base (comprobación de data/align-v24.json)
  if (typeof window!=='undefined') window.KLGroups = groups;   // v29: solo lectura (pruebas y herramienta de alineación con la acera)
  var KLMerge = {groups:mergeGroups, extra:mergeExtra, doubtful:mergeDoubt, visible:VISIBLE.length, source:DATA.length, isestr69:ise69};
  if (typeof window!=='undefined') window.KLMerge = KLMerge;
}

// Aggregated columns per grid cell, one level per zoom band. Height ~ sqrt(count) so Berlin does not hide small towns.
const LEVELS = [
  {id:'a0', dLa:0.25,  dLo:0.40,   min:0,    max:7.5,  k:1500, half:1500},
  {id:'a1', dLa:0.06,  dLo:0.095,  min:7.5,  max:9.5,  k:750,  half:420},
  {id:'a2', dLa:0.015, dLo:0.024,  min:9.5,  max:11.8, k:320,  half:110},
  {id:'a3', dLa:0.004, dLo:0.0064, min:11.8, max:14.6, k:70,   half:28},
];
function buildAgg(levels){
  const rows = (VISIBLE && VISIBLE.length) ? VISIBLE : DATA;
  AGG = (levels || LEVELS).map(L=>{
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

/* v27 contrast: GOLD z5/z12 stops unchanged since 9025a3c0. Street-level #f0d48a
   sat too close to day buildings #e7e0d2; z17 is #e0b020 so the shaft reads against
   the façade. Light is restored to 9025a3c0 (polar 35°, intensity 0.5) instead of
   d1df0526's more lateral light (polar 62°, intensity 0.62), which flattened the top. */
const GOLD = ['interpolate',['linear'],['zoom'], 5,'#c6a15b', 12,'#e0bc62', 17,'#e0b020'];
const LIGHT = {anchor:'map', position:[1.4, 210, 35], color:'#fff1d0', intensity:0.5};
function setBuildingsVisible(on){
  if (map && map.getLayer('bldg3d')) map.setLayoutProperty('bldg3d', 'visibility', on ? 'visible' : 'none');
}
function tryAddOverlays(){
  if (!map || !map.getStyle() || !map.getStyle().layers || !POINTS_FC || (!STONES_FC && !(typeof window!=='undefined' && window.KLCols)) || !AGG || !AGG.length){ if (map) map._pendingOverlays=true; return; }
  if (map.getSource('pts')) return;
  try { addOverlays(); map._pendingOverlays=false; }
  catch (e) { console.warn('addOverlays', e); map._pendingOverlays=true; }
}
function addOverlays(){
  // v21: no montar capas hasta que load() haya construido POINTS_FC/STONES_FC/AGG.
  // Con tres archivos de datos, style.load puede dispararse después de asignar DATA
  // y antes de buildStones(); si no, se añade 'pts' con undefined (aviso de GeoJSON) y las capas quedan a medias.
  if (!POINTS_FC || (!STONES_FC && !(typeof window!=='undefined' && window.KLCols)) || typeof AGG==='undefined' || !AGG){ if (map) map._pendingOverlays=true; return; }
  if (map.getSource('pts')) return;
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
    if (L.min >= 7.5 && map.getZoom() < 6.5) continue;
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
    if (!STONES_FC) STONES_FC = {type:'FeatureCollection', features:VISIBLE.map(s => ({type:'Feature', properties:{id:s.id}, geometry:{type:'Polygon', coordinates:square(s._dlo,s._dla,COL_HALF,s._ang)}}))};
    map.addSource('stones',{type:'geojson', data:STONES_FC, maxzoom:16, buffer:16, tolerance:0});
    map.addLayer({id:'stones', type:'fill-extrusion', source:'stones', minzoom:14.6,
      paint:{'fill-extrusion-color':GOLD, 'fill-extrusion-height':COL_H, 'fill-extrusion-opacity':0.95, 'fill-extrusion-vertical-gradient':true}}, 'sel-glow');
  }
  map.setLight(LIGHT);
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
function ensureAllAgg(){ if (AGG && AGG.length === 1 && DATA && DATA.length){ const a0 = AGG[0]; buildAgg(LEVELS.slice(1)); AGG = [a0, ...AGG]; } }
function setBase(b){ ensureAllAgg();
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
  const qBase = new URLSearchParams(location.search).get('base');
  base = intro ? 'night' : (qBase || localStorage.getItem('base') || 'night');
  if (base !== 'night' && base !== 'day' && base !== 'sat' && base !== 'hoy') base = 'night';
  paintBaseButtons();
  const styleKey = (base === 'hoy' || base === 'sat') ? (base === 'sat' ? 'sat' : 'night') : base;
  const mapOpts = {
    container:'map', style:styleFor(styleKey),
    center: intro ? [10, 28] : [6.5, 50.2],
    zoom: intro ? 1.05 : (narrowScreen ? 3.7 : 4.8),
    pitch: intro ? 0 : (narrowScreen ? 40 : 50),
    bearing: intro ? -18 : 0,
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
    tryAddOverlays();
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

let searchIndexed = false, citiesBuilt = false;
function ensureSearchIndex(){
  if (!searchIndexed && DATA && DATA.length){
    searchIndexed = true;
    for (const s of DATA){
      s._t = norm([s.n, s.a, s.sub, cityOf(s), s.cc && s.cc !== 'DE' ? (COUNTRY_WORDS[s.cc] || '') : ''].join(' ')).split(' ');
      s._c = norm(cityOf(s));
    }
  }
  if (!citiesBuilt && VISIBLE && VISIBLE.length){
    citiesBuilt = true;
    const cities = new Map();
    for (const s of VISIBLE){
      const c = cityOf(s); if (c){ const o = cities.get(c) || cities.set(c,{n:0,ids:[]}).get(c); o.n++; o.ids.push(s.id); }
    }
    CITY_STATS = [...cities.entries()].sort((a,b)=>b[1].n-a[1].n);
    $('#cities').innerHTML = [...cities.entries()].sort((a,b)=>a[0].localeCompare(b[0],'de')).map(([c,o])=>`<option value="${esc(c)}">${esc(c)} (${o.n})</option>`).join('');
  }
}

async function load(){
  $('#status').textContent = T('loading');
  // v21+v22: listas municipales abiertas en archivos y licencias aparte (no se mezclan en stones.json / ODbL).
  const addedFiles = [
    ['berlin', 'data/berlin-added-20261121.json'],
    ['koeln', 'data/koeln-added-20261121.json'],
    ['moenchengladbach', 'data/moenchengladbach-added-20261121.json'],
    ['denhaag', 'data/denhaag-added-20261121.json'],
    ['krefeld', 'data/krefeld-added-20261121.json'],
    ['monza', 'data/monza-added-20261121.json'],
    ['viersen', 'data/viersen-added-20261121.json'],
    ['memmingen', 'data/memmingen-added-20261121.json'],
    ['moers', 'data/moers-added-20261121.json'],
    ['grevenbroich', 'data/grevenbroich-added-20261121.json'],
    ['firenze', 'data/firenze-added-20261121.json'],
    ['xanten', 'data/xanten-added-20261121.json'],
    ['dresden', 'data/dresden-added-20261121.json'],
    ['erkrath', 'data/erkrath-added-20261121.json'],
    ['dormagen', 'data/dormagen-added-20261121.json']
  ];
  const pre = (typeof window !== 'undefined' && window.__klPre) || {};
  const fetchJson = u => fetch(u).then(r => { if (!r.ok) throw new Error(u+' '+r.status); return r.json(); });
  const getJson = u => pre[u] ? Promise.resolve(pre[u]).catch(() => fetchJson(u)) : fetchJson(u);
  const [j, ...added] = await Promise.all([getJson('data/stones.json'), ...addedFiles.map(([, u]) => getJson(u))]);
  META = j.meta; DATA = j.stones;
  const odblLen = j.stones.length;
  const addedCounts = {}, addedMeta = {};
  added.forEach((part, idx) => {
    const key = addedFiles[idx][0];
    const list = (part && Array.isArray(part.stones)) ? part.stones : [];
    for (let i = 0; i < list.length; i++){ list[i]._added = true; DATA.push(list[i]); }
    addedCounts[key] = list.length;
    addedMeta[key] = (part && part.meta) || null;
  });
  META.odbl_count = odblLen;
  META.berlin_count = addedCounts.berlin || 0;
  META.koeln_count = addedCounts.koeln || 0;
  META.v22_new_count = DATA.length - odblLen - META.berlin_count - META.koeln_count;
  META.count = DATA.length;
  META.v21_added = {
    berlin: addedMeta.berlin,
    koeln: addedMeta.koeln,
    records: META.berlin_count + META.koeln_count
  };
  META.v22_added = {
    counts: addedCounts,
    records: DATA.length - odblLen
  };
  // v19: posición de DIBUJO. Si el archivo trae dla/dlo (placa dentro de un edificio de OSM o a menos de 1 m de la fachada), la columna se dibuja ahí
  // (en la acera, hacia la calle); la coordenada de origen queda en sla/slo y es la que usan «Cómo llegar» y las descargas.
  for (const s of DATA){
    if (s.dla != null && s.dlo != null){ s.sla = s.la; s.slo = s.lo; s.la = s.dla; s.lo = s.dlo; }
    byId.set(s.id, s);
  }
  // Pintar la vista general (luz dorada y columnas a0) en cuanto llega el JSON, antes de buildStones().
  POINTS_FC = {type:'FeatureCollection', features: DATA.map(s => ({type:'Feature', properties:{}, geometry:{type:'Point', coordinates:[s.lo, s.la]}}))};
  buildAgg([LEVELS[0]]);
  let agg0 = AGG[0];
  tryAddOverlays();
  await new Promise(r => setTimeout(r, 0));
  buildStones();
  // Sustituir el a0/pts provisional (todo DATA) por VISIBLE, sin los alias.
  buildAgg([LEVELS[0]]);
  agg0 = AGG[0];
  AGG = [agg0];
  if (map && map.getSource('pts')) {
    if (POINTS_FC) map.getSource('pts').setData(POINTS_FC);
    if (map.getSource('a0')) map.getSource('a0').setData(agg0.fc);
    // Añadir a1..a3, luces de casas, clusters y columnas de calle.
    for (const {L, fc} of AGG) {
      if (L.min >= 7.5 && map.getZoom() < 6.5) continue;
      if (map.getSource(L.id)) { map.getSource(L.id).setData(fc); continue; }
      map.addSource(L.id, {type:'geojson', data:fc});
      map.addLayer({id:L.id, type:'fill-extrusion', source:L.id, minzoom:L.min, maxzoom:L.max,
        paint:{'fill-extrusion-color':GOLD, 'fill-extrusion-height':['get','h'], 'fill-extrusion-opacity':0.92, 'fill-extrusion-vertical-gradient':true}});
    }
    if (LIGHTS_FC && !map.getSource('house-lights')) {
      const firstSymbol = (map.getStyle().layers.find(l => l.type === 'symbol') || {}).id;
      map.addSource('house-lights', {type:'geojson', data:LIGHTS_FC, maxzoom:14});
      map.addLayer({id:'house-lights', type:'circle', source:'house-lights', minzoom:4, maxzoom:14.2,
        layout:{visibility: base==='day' ? 'none' : 'visible'},
        paint:{'circle-radius':['interpolate',['linear'],['zoom'],4,1.15,8,2.1,12,3.4,14,5],
               'circle-color':'#ffe2a0',
               'circle-opacity':['interpolate',['linear'],['zoom'],4,0.4,9,0.75,13.5,0.2],
               'circle-blur':0.65, 'circle-pitch-alignment':'map'}}, firstSymbol);
    }
    if (window.KLCols) KLCols.add();
    else if (!map.getSource('stones')) {
      map.addSource('stones',{type:'geojson', data:STONES_FC, maxzoom:16, buffer:16, tolerance:0});
      map.addLayer({id:'stones', type:'fill-extrusion', source:'stones', minzoom:14.6,
        paint:{'fill-extrusion-color':GOLD, 'fill-extrusion-height':COL_H, 'fill-extrusion-opacity':0.95, 'fill-extrusion-vertical-gradient':true}}, 'sel-glow');
    }
  } else {
    tryAddOverlays();
    if (!map.getSource('pts')) map.once('style.load', tryAddOverlays);
    if (!map.getSource('pts')) requestAnimationFrame(tryAddOverlays);
  }
  if (window.KLImagery) KLImagery.onData();
  $('#status').textContent = T('ready')(fmtNum(DATA.length));
  route();
  document.dispatchEvent(new CustomEvent('kl:data'));   // mapui.js: países, vista inicial con todos los países y clusters
  const mountRestAgg = () => {
    ensureAllAgg();
    if (!map || !map.getStyle() || !AGG || AGG.length < 2) return;
    for (const {L, fc} of AGG) {
      if (!map.getSource(L.id)) {
        map.addSource(L.id, {type:'geojson', data:fc});
        map.addLayer({id:L.id, type:'fill-extrusion', source:L.id, minzoom:L.min, maxzoom:L.max,
          paint:{'fill-extrusion-color':GOLD, 'fill-extrusion-height':['get','h'], 'fill-extrusion-opacity':0.92, 'fill-extrusion-vertical-gradient':true}});
      }
    }
  };
  startAlign();
  // v31: la inscripción escrita en la placa (plaquetext.js) se pide solo al acercarse (zoom >= 19,5), nunca en la carga inicial.
  const wantText = () => { if (map.getZoom() >= 19.5 && !window.KLPlaqueText && !document.getElementById('kl-plaquetext')) loadPlaqueText(); };
  map.on('zoomend', wantText); map.on('moveend', wantText);
  map.on('zoom', () => { if (map.getZoom() >= 6.5) mountRestAgg(); });
  setTimeout(mountRestAgg, 350);
  setTimeout(ensureSearchIndex, 60);
}

// v29: cada grupo de columnas mira a su calle de OSM y se dispone en 1–2 filas paralelas al bordillo (pipeline/tools/align24.py).
// Solo DIBUJO: data/align-v24.json fija _dla/_dlo/_ang; la/lo registrados, el mapa 2D, «Cómo llegar» y las descargas no cambian.
// Se pide DESPUÉS de montar los cuadros (kl-clu) para no retrasar la carga; los grupos que no están en el archivo se quedan como estaban.
const KLAlign = {ready:false, applied:0, entries:0, skipped:0, file:'data/align-v24.json', off:/[?&]alignoff=1\b/.test(location.search)};
if (typeof window!=='undefined') window.KLAlign = KLAlign;
function applyAlign(j){
  const step = +j.step || COL_STEP, list = Array.isArray(j.g) ? j.g : [];
  let n = 0, skipped = 0;
  for (const e of list){
    const k = e.length - 4;
    let ok = k > 0;
    const gi = (byId.get(e[4])||{})._gi;
    for (let i = 4; ok && i < e.length; i++){ const s = byId.get(e[i]); if (!s || s._aliasOf || s._gi !== gi) ok = false; }
    // Un grupo de la base solo se recoloca si la entrada trae TODAS sus placas visibles (si los datos cambian sin rehacer el archivo, se queda como estaba).
    if (ok && gi !== undefined && window.KLGroups && KLGroups[gi].g.length !== k) ok = false;
    if (!ok){ skipped++; continue; }
    const la0 = e[0]/1e7, lo0 = e[1]/1e7, ang = e[2]*Math.PI/1800, cols = e[3];
    const rows = Math.ceil(k/cols)||1, cos = Math.cos(la0*Math.PI/180), cA = Math.cos(ang), sA = Math.sin(ang);
    for (let i = 0; i < k; i++){
      const s = byId.get(e[4+i]);
      const cx = (i%cols)-(cols-1)/2, cy = Math.floor(i/cols)-(rows-1)/2;
      const east = cx*step*cA - cy*step*sA;
      const north = cx*step*sA + cy*step*cA;
      s._dla = la0 + north/M_LAT;
      s._dlo = lo0 + east/(M_LAT*cos);
      s._ang = ang;
      n++;
    }
  }
  for (const s of DATA) if (s._aliasOf){ const p = byId.get(s._aliasOf); if (p){ s._dla = p._dla; s._dlo = p._dlo; s._ang = p._ang||0; } }
  KLAlign.applied = n; KLAlign.entries = list.length; KLAlign.skipped = skipped;
  if (typeof window !== 'undefined' && window.KLCols){ if (KLCols.relayout) KLCols.relayout(); }
  else if (STONES_FC){
    STONES_FC = {type:'FeatureCollection', features:VISIBLE.map(s => ({type:'Feature', properties:{id:s.id}, geometry:{type:'Polygon', coordinates:square(s._dlo,s._dla,COL_HALF,s._ang)}}))};
    if (map && map.getSource('stones')) map.getSource('stones').setData(STONES_FC);
  }
  if (selected && map) refreshSel();
}
function loadPlaqueText(){
  if (new URLSearchParams(location.search).has('textooff')) return;   // ?textooff=1: placas en blanco como v30
  const v = ((document.querySelector('script[src*="columns.js"]') || {}).src || '').match(/[?&]v=(\d+)/);
  const el = document.createElement('script'); el.id = 'kl-plaquetext'; el.async = true;
  el.src = 'plaquetext.js' + (v ? '?v=' + v[1] : '');
  document.head.appendChild(el);
}
function startAlign(){
  if (KLAlign.off){ KLAlign.ready = true; return; }
  const t0 = Date.now();
  const go = () => fetch(KLAlign.file).then(r => { if (!r.ok) throw new Error(KLAlign.file+' '+r.status); return r.json(); })
    .then(j => { applyAlign(j); }).catch(e => { KLAlign.error = String(e); console.warn('align', e); })
    .finally(() => { KLAlign.ready = true; document.dispatchEvent(new CustomEvent('kl:align')); });
  const wait = () => { if ((map && map.getSource && map.getSource('kl-clu')) || Date.now() - t0 > 15000) go(); else setTimeout(wait, 250); };
  wait();
}

function search(){
  ensureSearchIndex();
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
function wpUrl(v){ if (/^https?:\/\//i.test(String(v||''))) return String(v); const m=/^([a-z\-]+):(.+)$/.exec(v); return m?`https://${m[1]}.wikipedia.org/wiki/${encodeURIComponent(m[2].replace(/ /g,'_'))}`:''; }
function osmUrl(s){ return /^[nw]\d+$/.test(s.id)?`https://www.openstreetmap.org/${s.id[0]==='n'?'node':'way'}/${s.id.slice(1)}`:''; }

const ANON_NAME = /\b(sinto|sinti|sintiza|romni|rommni|roma|rom|unbekannt\w*|anonym\w*|namenlos\w*)\b|^\s*n\.?\s*n\.?\s*$/i;
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
function extLink(href, label){
  return `<li><a href="${esc(href)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a></li>`;
}
function sourceSearchLabel(it){
  const fn = I18N[lang] && I18N[lang][it.key];
  if (typeof fn === 'function') return fn(it.q || '');
  return T(it.key);
}
function sourceSearchItems(s, rec, opts){
  const items = [];
  const add = (href, label) => { if (href && label) items.push(extLink(href, label)); };
  const list = (typeof KLSourceLinks !== 'undefined' && KLSourceLinks.sourceSearchList)
    ? KLSourceLinks.sourceSearchList(s, rec, lang, Object.assign({anon: isAnonStone(s)}, opts||{}))
    : [];
  const seen = new Set();
  list.forEach(it => { if (!seen.has(it.href)){ seen.add(it.href); add(it.href, sourceSearchLabel(it)); } });
  const links = (rec && rec.links) || {};
  const safe = (typeof KLSourceLinks !== 'undefined' && KLSourceLinks.safeUrl) ? KLSourceLinks.safeUrl : (u => /^https?:\/\//i.test(String(u||'')) ? String(u) : '');
  (links.describedAt||[]).forEach(u0 => { const u=safe(u0); if (!u || seen.has(u)) return; seen.add(u); let h=u; try{h=new URL(u).hostname.replace(/^www\./,'')}catch(e){} add(u, T('describedAt')+' · '+h); });
  // OpenStreetMap and Wikidata are NOT repeated here: they are in «Fuentes de esta ficha» (their data is used, under ODbL/CC0).
  sourceSearchItems.lastKeys = list.map(it => it.key);
  return items;
}
function renderSourceSearch(s, rec, opts){
  const box = document.getElementById('sourceSearch');
  if (!box) return;
  const items = sourceSearchItems(s, rec, opts);
  const keys = sourceSearchItems.lastKeys || [];
  const scope = keys.some(k => /^(yv|gb)/.test(k)) ? ` ${T('scopeNote')}` : '';
  box.innerHTML = (items.length ? `<ul class="links">${items.join('')}</ul>` : '') + `<p class="note">${T('researchNote')}${scope}</p>`;
}
function archiveItems(s, rec){ return sourceSearchItems(s, rec); }
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
    parts.push(`<p class="cite">${esc(T('wpCite'))} <a href="${esc(w.permalink)}" target="_blank" rel="noopener noreferrer">${esc(w.title)}</a>, ${esc(T('wpRev'))} ${esc(w.revid)}. <a href="${esc(w.authors)}" target="_blank" rel="noopener noreferrer">${esc(T('wpAuthors'))}</a>. <a href="${esc(w.licenseUrl)}" target="_blank" rel="noopener noreferrer">${esc(w.license)}</a>.</p>`);
  } else if (anon) {
    parts.push(`<p class="help">${esc(T('anonNote'))}</p>`);
  } else if (!official) {
    parts.push(`<p class="help">${esc(T('noStory'))} <a href="#contribuir" id="contrib">${esc(T('helpUs'))}</a></p>`);
  }
  slot.innerHTML = parts.join('');
  renderSourceSearch(s, rec);
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
function hostLinks(urls){ return urls.filter(u=>/^https:\/\//i.test(u)).map(u=>{ let h=u; try{h=new URL(u).hostname.replace(/^www\./,'')}catch(e){} return `<a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(h)}</a>`; }).join(', '); }
// v19: las fuentes discrepan sobre la dirección (campo disc de data/stones.json): aviso visible en la ficha, con enlaces
function discHtml(s){
  const d = s.disc; if (!d || !d.alt) return '';
  const osm = osmUrl(s) ? [osmUrl(s)] : [];
  return `<div class="disc" role="note"><strong>${esc(T('discTitle'))}.</strong> ${esc(T('discBody')(s.a||'', d.alt))}`+
    `<br>${esc(T('discAlt')(d.alt))} ${hostLinks(d.alt_src||[])}`+
    `<br>${esc(T('discMain')(s.a||''))} ${hostLinks([...osm, ...(d.main_src||[])])}</div>`;
}
function openStone(id, fromMap){
  let s = byId.get(id); if (!s) return;
  if (s._aliasOf) s = byId.get(s._aliasOf) || s;
  if (document.body.classList.contains('vigil-on')) stopVigil();
  selected = s.id; refreshSel();
  const targetZoom = 17.6;
  if (!fromMap || map.getZoom() < 16.5)
    map.flyTo({center:[s._dlo,s._dla], zoom:targetZoom, pitch:58, offset:(window.KLUI && KLUI.offset) ? KLUI.offset() : [0, 60], bearing: map.getBearing() || -20, duration: reduceMotion ? 0 : 3200, essential:true, curve:1.5});
  map.once('moveend', refreshSel);
  history.replaceState(null,'','#s='+encodeURIComponent(id));
  // Merged records (same person, e.g. a second stone or a second Wikidata item): show every distinct inscription.
  const inscSeen = new Set(), inscList = [];
  for (const r of [s, ...(s._also||[])]){ if (!r.i) continue; const k = KLDedupe.fold(r.i).replace(/[^a-z0-9]+/g,''); if (!inscSeen.has(k)){ inscSeen.add(k); inscList.push(r.i); } }
  const insc = inscList.map(t => esc(t).replace(/\s*\|\s*/g,'\n').split(/\n/).filter(Boolean).join('<br>')).join('</div><div class="brassplate">');
  const facts=[[T('address'),s.a],[T('place'),cityOf(s)+(s.cd&&!s.c?' '+T('derived'):'')],[T('country'),countryLabel(s)],[T('district'),s.sub],[T('born'),s.b],[T('died'),s.d],[T('laid'),s.laid],[T('posLabel'),s.gm?T(/^commons/.test(s.gm)?'posApproxPhoto':'posApprox'):''],[T('type'),s.kind==='stolperschwelle'?T('threshold'):'']]
    .filter(x=>x[1]).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('');
  const bio=[]; (s.w||[]).filter(u=>/^https?:\/\//i.test(String(u||''))).forEach(u=>{ let h=u; try{h=new URL(u).hostname.replace(/^www\./,'')}catch(e){} bio.push(`<li><a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(h)}</a></li>`); });
  if (s.wp) bio.push(`<li><a href="${esc(wpUrl(s.wp))}" target="_blank" rel="noopener noreferrer">Wikipedia: ${esc(s.wp.replace(/^[a-z]+:/,''))}</a></li>`);
  if (s.desc) bio.unshift(`<li>${esc(s.desc)}</li>`);
  const recs = [s, ...(s._also||[])];
  const src=[]; const seenSrc=new Set();
  for (const r of recs){ const u=osmUrl(r); if (u && !seenSrc.has(u)){ seenSrc.add(u); src.push(`<li><a href="${u}" target="_blank" rel="noopener noreferrer">OpenStreetMap</a></li>`); } }
  for (const r of recs){ if (r.wd && !seenSrc.has('wd:'+r.wd)){ seenSrc.add('wd:'+r.wd); src.push(`<li><a href="https://www.wikidata.org/wiki/${esc(r.wd)}" target="_blank" rel="noopener noreferrer">Wikidata ${esc(r.wd)}</a></li>`); } }
  for (const r of recs){ if (r.p && !seenSrc.has('p:'+r.p)){ seenSrc.add('p:'+r.p); src.push(`<li><a href="https://www.wikidata.org/wiki/${esc(r.p)}" target="_blank" rel="noopener noreferrer">Wikidata (persona/Person) ${esc(r.p)}</a></li>`); } }
  for (const r of recs){
    const am = ADDED_SOURCE_META[r.src];
    if (am){
      if (!seenSrc.has('od:'+r.src)){
        seenSrc.add('od:'+r.src);
        src.push(`<li><a href="${esc(am.url)}" target="_blank" rel="noopener noreferrer">${esc(am.label)}</a></li>`);
      }
      if (r.lb && /^https?:\/\//i.test(String(r.lb)) && !seenSrc.has('lb:'+r.lb)){
        seenSrc.add('lb:'+r.lb);
        const lbTxt = am.lbLabel ? T(am.lbLabel) : (am.lbName || am.label);
        src.push(`<li><a href="${esc(r.lb)}" target="_blank" rel="noopener noreferrer">${esc(lbTxt)}</a></li>`);
      }
    }
  }
  const photo = s.img ? `<figure class="photo"><a href="${commonsPage(s.img)}" target="_blank" rel="noopener noreferrer"><img loading="lazy" src="${commonsThumb(s.img,480)}" alt="${esc(s.n||'')}"></a><figcaption><a href="${commonsPage(s.img)}" target="_blank" rel="noopener noreferrer">${T('photo')}</a></figcaption></figure>` : '';
  const d = $('#detail');
  d.innerHTML = `<button class="back" id="back">${T('back')}</button>
    <h2>${esc(s._n||s.n||'—')}</h2><p class="place">${esc([s.a, s.a&&s.a.includes(cityOf(s))?'':cityOf(s), countryLabel(s)].filter(Boolean).join(', '))}</p>
    ${discHtml(s)}
    <p class="dates" id="inscDates" hidden></p>
    <div class="section-t">${T('inscription')}</div>
    ${insc?`<div class="brassplate">${insc}</div>`:`<p class="note">${T('noinsc')}</p>`}
    ${photo}
    <dl class="facts">${facts}</dl>
    <div class="actions">
      <button id="share">${T('share')}</button>
      <a href="https://www.google.com/maps/dir/?api=1&destination=${s.sla ?? s.la},${s.slo ?? s.lo}" target="_blank" rel="noopener noreferrer">${T('directions')}</a>
      <a href="https://www.openstreetmap.org/directions?to=${s.sla ?? s.la}%2C${s.slo ?? s.lo}#map=19/${s.sla ?? s.la}/${s.slo ?? s.lo}" target="_blank" rel="noopener noreferrer">${T('osmDir')}</a>
    </div>
    <div id="storySlot"><p class="story-wait">…</p></div>
    ${bio.length?`<div class="section-t">${T('bio')}</div><ul class="links">${bio.join('')}</ul>`:''}
    <div class="section-t">${T('research')}</div>
    <div id="sourceSearch"></div>
    <div class="section-t">${T('sources')}</div><ul class="links">${src.join('')}</ul>
    <p class="note">${T('attribution')}</p>`;
  $('#results').hidden = true; d.hidden = false; d.scrollTop = 0;
  $('#back').onclick = ()=>closeDetail(true);
  $('#share').onclick = e=>{ navigator.clipboard?.writeText(location.href); e.target.textContent=T('copied'); };
  renderSourceSearch(s, null);
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
  ensureSearchIndex();
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
$('#q').addEventListener('focus',ensureSearchIndex,{once:true}); $('#city').addEventListener('focus',ensureSearchIndex,{once:true});
$('#q').addEventListener('input',debounced); $('#city').addEventListener('input',debounced);
$('#results').addEventListener('click',e=>{const b=e.target.closest('button[data-id]'); if(b) openStone(b.dataset.id);});
document.querySelectorAll('.lang button').forEach(b=>b.onclick=()=>{lang=b.dataset.lang; localStorage.setItem('lang',lang); applyI18n(); if (window.KLImagery) KLImagery.refresh(); if(selected) openStone(selected,true); else search();});
document.querySelectorAll('.basemaps button[data-base]').forEach(b=>b.onclick=()=>setBase(b.dataset.base));
$('#aboutLink').onclick=e=>{e.preventDefault(); $('#aboutBody').innerHTML=T('aboutHtml')({...META,count:fmtNum(META.count||DATA.length),odbl_count:fmtNum(META.odbl_count||0),berlin_count:fmtNum(META.berlin_count||0),koeln_count:fmtNum(META.koeln_count||0),v22_count:fmtNum(META.v22_new_count||0)})+T('privacyHtml')(typeof KLCounter!=='undefined' && KLCounter.isOn()); $('#about').showModal();};
window.addEventListener('hashchange', route);
function stoneProps(s){
  return {id:s.id, name:s.n||'', inscription:s.i||'', address:s.a||'', city:s.c||'', city_derived:s.cd||'', country:s.cc||'DE',
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
    features: DATA.map(s => ({type:'Feature', geometry:{type:'Point', coordinates:[s.slo ?? s.lo, s.sla ?? s.la]}, properties:stoneProps(s)}))};
  downloadText('stolpersteine_germany.geojson', 'application/geo+json', JSON.stringify(fc));
};
$('#dlKml').onclick = () => {
  if (!DATA.length) return;
  const xe = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const parts = ['<?xml version="1.0" encoding="UTF-8"?>','<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Stolpersteine in Europa (Deutschland, Niederlande, Frankreich, Österreich, Norwegen, Tschechien, Italien, Spanien, Belgien, Luxemburg, Ungarn, Litauen, Schweiz, Polen, Slowakei, Jersey, Kroatien, Dänemark, Guernsey, Finnland, Andorra, Irland, Schweden, Lettland, Rumänien, Vereinigtes Königreich und Liechtenstein)</name>'];
  for (const s of DATA) {
    const p = stoneProps(s);
    const desc = [p.address, p.city, p.birth && ('* '+p.birth), p.death && ('† '+p.death), p.inscription].filter(Boolean).join(' · ');
    parts.push('<Placemark><name>'+xe(p.name)+'</name><description>'+xe(desc)+'</description><Point><coordinates>'+(s.slo ?? s.lo)+','+(s.sla ?? s.la)+',0</coordinates></Point></Placemark>');
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
    map.jumpTo(Object.assign({center:[6.5,50.2], zoom:narrowScreen?3.7:4.8, pitch:narrowScreen?40:50, bearing:0}, (window.KLUI && KLUI.home) ? KLUI.home() : {}));
    return;
  }
  const dur = reduceMotion ? 0 : 5200;
  map.flyTo(Object.assign({center:[6.5, 50.2], zoom:narrowScreen?3.7:4.8, pitch:narrowScreen?40:50, bearing:0}, (window.KLUI && KLUI.home) ? KLUI.home() : {}, {duration:dur, essential:true, curve:1.4}));
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
