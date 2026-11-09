/* Hoy / 1945 imagery. Only endpoints checked on 7 Nov 2026: GetMap image + CORS.
   Rhineland-Palatinate returns a JPEG but no Access-Control-Allow-Origin, so it is listed and not drawn.
   Schleswig-Holstein and Saxony-Anhalt echo the Origin header only for https pages. */
(function () {
  const BHV_B = [8.45532, 53.4278, 8.68394, 53.6533];
  const HB_B = [8.45982, 53.0062, 9.0139, 53.232];
  const CC = 'https://creativecommons.org/licenses/by/4.0/';
  const DLBY = 'https://www.govdata.de/dl-de/by-2-0';
  const DL0 = 'https://www.govdata.de/dl-de/zero-2-0';

  function W(endpoint, layer, extra) {
    const j = endpoint.indexOf('?') >= 0 ? '&' : '?';
    return endpoint + j + 'SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=' + layer +
      '&STYLES=&SRS=EPSG:3857&BBOX={bbox-epsg-3857}&WIDTH=256&HEIGHT=256&FORMAT=image/jpeg&TRANSPARENT=FALSE' + (extra || '');
  }
  function capsUrl(endpoint) {
    const j = endpoint.indexOf('?') >= 0 ? '&' : '?';
    return endpoint + j + 'SERVICE=WMS&REQUEST=GetCapabilities';
  }

  const SENTINEL = {
    tiles: ['https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/GoogleMapsCompatible/{z}/{y}/{x}.jpg'],
    credit: {
      es: 'Vista general: Sentinel-2 cloudless 2016, ~10 m, EOX IT Services GmbH (datos Copernicus modificados) · CC BY 4.0. No es la ortofoto actual.',
      de: 'Übersicht: Sentinel-2 cloudless 2016, ~10 m, EOX IT Services GmbH (veränderte Copernicus-Daten) · CC BY 4.0. Kein aktuelles Orthophoto.',
      en: 'Overview: Sentinel-2 cloudless 2016, ~10 m, EOX IT Services GmbH (modified Copernicus data) · CC BY 4.0. Not a current orthophoto.'
    },
    href: CC
  };

  /* res/year are what the provider states. "variable" means the mosaic has no single flight date. */
  const SOURCES = {
    BHV: {
      id: 'BHV', land: 'HB',
      name: {es:'Bremerhaven', de:'Bremerhaven', en:'Bremerhaven'},
      res: '10 cm', year: '2025', license: 'CC BY 4.0', href: CC,
      endpoint: 'https://geodienste.bremen.de/wms_dop_lb', layer: 'dop10_2025_BHV',
      bounds: BHV_B, minzoom: 13, maxzoom: 19,
      center: [8.581, 53.539], zoom: 15.4,
      credit: '© GeoBasis-DE / Landesamt GeoInformation Bremen (2026), DOP10 Bremerhaven 2025 · CC BY 4.0',
      hist: {
        layer: 'luftbild_1945_BHV', year: '1945', license: 'CC BY 4.0', href: CC,
        credit: '© GeoBasis-DE / Landesamt GeoInformation Bremen (2026), Luftbild Bremerhaven 1945 · CC BY 4.0. Mes no documentado.'
      }
    },
    HB: {
      id: 'HB', land: 'HB',
      name: {es:'Bremen', de:'Bremen', en:'Bremen'},
      res: '10 cm', year: '2025', license: 'CC BY 4.0', href: CC,
      endpoint: 'https://geodienste.bremen.de/wms_dop_lb', layer: 'dop10_2025_HB',
      bounds: HB_B, minzoom: 13, maxzoom: 19,
      center: [8.807, 53.079], zoom: 14.6,
      credit: '© GeoBasis-DE / Landesamt GeoInformation Bremen (2026), DOP10 Bremen 2025 · CC BY 4.0'
    },
    BE: {
      id: 'BE',
      name: {es:'Berlín', de:'Berlin', en:'Berlin'},
      res: '20 cm', year: {es:'primavera 2025', de:'Frühjahr 2025', en:'spring 2025'},
      license: 'dl-de-zero-2.0', href: DL0,
      endpoint: 'https://gdi.berlin.de/services/wms/dop_2025_fruehjahr', layer: 'dop_2025',
      minzoom: 13, maxzoom: 18, center: [13.405, 52.52], zoom: 15,
      credit: '© Geoportal Berlin / DOP20 RGB Frühjahr 2025 · dl-de-zero-2.0'
    },
    BB: {
      id: 'BB',
      name: {es:'Brandeburgo', de:'Brandenburg', en:'Brandenburg'},
      res: '20 cm', year: '2022–2024', license: 'dl-de/by-2-0', href: DLBY,
      endpoint: 'https://isk.geobasis-bb.de/mapproxy/dop20_2022_2024/service/wms', layer: 'dop20_bebb_2022_2024_farbe',
      minzoom: 13, maxzoom: 18, center: [13.06, 52.39], zoom: 13.5,
      credit: '© GeoBasis-DE/LGB, DOP20 2022–2024 · dl-de/by-2-0'
    },
    HH: {
      id: 'HH',
      name: {es:'Hamburgo', de:'Hamburg', en:'Hamburg'},
      res: '20 cm', year: '2026', license: 'dl-de/by-2-0', href: DLBY,
      endpoint: 'https://geodienste.hamburg.de/wms_dop_zeitreihe_unbelaubt', layer: 'dop_zeitreihe_unbelaubt',
      extra: '&TIME=2026', minzoom: 16, maxzoom: 18,
      center: [9.993, 53.551], zoom: 16.2,
      credit: '© Freie und Hansestadt Hamburg, LGV, DOP unbelaubt TIME=2026 · dl-de/by-2-0. No se pide 2023 (Maxar).',
      note: {
        es: 'El servicio oficial no dibuja por debajo de esa escala (MaxScaleDenominator 5000). El año 2023 de la misma serie es Maxar y no se usa. 2026 es el año por defecto del servicio LGV; el GetMap del 7 nov 2026 devolvió fotografía real.',
        de: 'Der Dienst zeichnet unterhalb dieses Maßstabs nicht (MaxScaleDenominator 5000). Jahrgang 2023 derselben Serie ist Maxar und wird nicht abgefragt. 2026 ist der Standard des LGV-Dienstes.',
        en: 'The official service does not draw below this scale (MaxScaleDenominator 5000). The 2023 year of the same series is Maxar and is not requested. 2026 is the LGV service default.'
      }
    },
    NW: {
      id: 'NW',
      name: {es:'Renania del Norte-Westfalia', de:'Nordrhein-Westfalen', en:'North Rhine-Westphalia'},
      res: '10 cm', year: {es:'ciclo actual, fecha de vuelo variable', de:'aktueller Zyklus, Flugdatum örtlich verschieden', en:'current cycle, flight date varies'},
      license: 'dl-de-zero-2.0', href: DL0,
      endpoint: 'https://www.wms.nrw.de/geobasis/wms_nw_dop', layer: 'nw_dop_rgb',
      minzoom: 13, maxzoom: 19, center: [6.960, 50.938], zoom: 15,
      credit: '© GeoBasis-DE / Geobasis NRW, DOP 10 cm · dl-de-zero-2.0'
    },
    BY: {
      id: 'BY',
      name: {es:'Baviera', de:'Bayern', en:'Bavaria'},
      res: '20 cm', year: {es:'ciclo de 2 años, fecha local variable', de:'2-Jahres-Zyklus, lokales Datum verschieden', en:'2-year cycle, local date varies'},
      license: 'CC BY 4.0', href: CC,
      endpoint: 'https://geoservices.bayern.de/od/wms/dop/v1/dop20', layer: 'by_dop20c',
      minzoom: 13, maxzoom: 18, center: [11.576, 48.137], zoom: 14.5,
      credit: '© Bayerische Vermessungsverwaltung, DOP20 · CC BY 4.0'
    },
    BW: {
      id: 'BW',
      name: {es:'Baden-Württemberg', de:'Baden-Württemberg', en:'Baden-Württemberg'},
      res: '20 cm', year: {es:'actualización anual de una parte del land', de:'jährlich ein Teil der Landesfläche', en:'part of the state updated each year'},
      license: 'dl-de/by-2-0', href: DLBY,
      endpoint: 'https://owsproxy.lgl-bw.de/owsproxy/ows/WMS_LGL-BW_ATKIS_DOP_20_C', layer: 'IMAGES_DOP_20_RGB',
      minzoom: 13, maxzoom: 18, center: [9.182, 48.775], zoom: 14.5,
      credit: '© LGL Baden-Württemberg, DOP20 · dl-de/by-2-0 · www.lgl-bw.de'
    },
    HE: {
      id: 'HE',
      name: {es:'Hesse', de:'Hessen', en:'Hesse'},
      res: '20 cm', year: {es:'DOP20 vigente, sin un solo año de vuelo', de:'aktuelles DOP20, kein einzelnes Flugjahr', en:'current DOP20, no single flight year'},
      license: {es:'uso sin restricción, § 18 HVGG', de:'nutzungsfrei nach § 18 HVGG', en:'unrestricted use under HVGG § 18'},
      href: 'https://www.gds-srv.hessen.de/cgi-bin/lika-services/ogc-free-images.ows?SERVICE=WMS&REQUEST=GetCapabilities',
      endpoint: 'https://www.gds-srv.hessen.de/cgi-bin/lika-services/ogc-free-images.ows', layer: 'he_dop20_rgb',
      minzoom: 13, maxzoom: 18, center: [8.682, 50.110], zoom: 14.8,
      credit: '© Hessische Verwaltung für Bodenmanagement und Geoinformation, DOP20 · § 18 HVGG'
    },
    SN: {
      id: 'SN',
      name: {es:'Sajonia', de:'Sachsen', en:'Saxony'},
      res: '20 cm', year: {es:'fecha de vuelo variable', de:'Flugdatum variabel', en:'flight date varies'},
      license: 'dl-de/by-2-0', href: DLBY,
      endpoint: 'https://geodienste.sachsen.de/wms_geosn_dop-rgb/guest', layer: 'sn_dop_020',
      minzoom: 13, maxzoom: 18, center: [13.737, 51.050], zoom: 14.6,
      credit: '© GeoSN, DOP20 · dl-de/by-2-0'
    },
    TH: {
      id: 'TH',
      name: {es:'Turingia', de:'Thüringen', en:'Thuringia'},
      res: '20 cm', year: {es:'fecha de vuelo variable', de:'Flugdatum variabel', en:'flight date varies'},
      license: 'CC BY 4.0', href: CC,
      endpoint: 'https://www.geoproxy.geoportal-th.de/geoproxy/services/DOP20', layer: 'th_dop',
      minzoom: 13, maxzoom: 18, center: [11.029, 50.978], zoom: 14.4,
      credit: '© GDI-Th, DOP20 · CC BY 4.0'
    },
    NI: {
      id: 'NI',
      name: {es:'Baja Sajonia', de:'Niedersachsen', en:'Lower Saxony'},
      res: {es:'no declarada en el capabilities', de:'im Capabilities nicht genannt', en:'not stated in the capabilities'},
      year: {es:'fecha de vuelo variable', de:'Flugdatum variabel', en:'flight date varies'},
      license: 'CC BY 4.0', href: CC,
      endpoint: 'https://opendata.geoservices.lgln.niedersachsen.de/dop_wms', layer: 'ni_dop',
      minzoom: 13, maxzoom: 18, center: [9.732, 52.375], zoom: 14.4,
      credit: '© LGLN, DOP · CC BY 4.0',
      note: {
        es: 'El WMS abierto «WMS NI DOP» no publica los centímetros. No se afirma DOP10 ni DOP20.',
        de: 'Der offene Dienst „WMS NI DOP“ nennt keine Bodenauflösung. Weder DOP10 noch DOP20 wird behauptet.',
        en: 'The open “WMS NI DOP” service does not state a ground resolution. Neither DOP10 nor DOP20 is claimed.'
      }
    },
    ST: {
      id: 'ST', httpsOnly: true,
      name: {es:'Sajonia-Anhalt', de:'Sachsen-Anhalt', en:'Saxony-Anhalt'},
      res: '20 cm', year: {es:'fecha de vuelo variable', de:'Flugdatum variabel', en:'flight date varies'},
      license: 'dl-de/by-2-0', href: DLBY,
      endpoint: 'https://www.geodatenportal.sachsen-anhalt.de/wss/service/ST_LVermGeo_DOP_WMS_OpenData/guest',
      layer: 'lsa_lvermgeo_dop20_2',
      minzoom: 13, maxzoom: 18, center: [11.627, 52.131], zoom: 14.4,
      credit: '© GeoBasis-DE / LVermGeo Sachsen-Anhalt, DOP20 · dl-de/by-2-0',
      note: {
        es: 'CORS: el servicio refleja el origen solo en páginas https. En http://127.0.0.1 se usa la vista general de 2016. La ficha GovData del WMS DOP20 está bajo dl-de/by-2-0; el capabilities OpenData no repite el texto.',
        de: 'CORS: der Dienst spiegelt den Origin nur bei https. Unter http://127.0.0.1 erscheint die Übersicht von 2016.',
        en: 'CORS: the service echoes Origin only on https pages. On http://127.0.0.1 the 2016 overview is shown.'
      }
    },
    SH: {
      id: 'SH', httpsOnly: true,
      name: {es:'Schleswig-Holstein', de:'Schleswig-Holstein', en:'Schleswig-Holstein'},
      res: '20 cm', year: {es:'fecha de vuelo variable', de:'Flugdatum variabel', en:'flight date varies'},
      license: 'CC BY 4.0', href: CC,
      endpoint: 'https://dienste.gdi-sh.de/WMS_SH_DOP20col_OpenGBD', layer: 'sh_dop20_rgb',
      minzoom: 13, maxzoom: 18, center: [10.122, 54.323], zoom: 14.2,
      credit: '© GeoBasis-DE/LVermGeo SH, DOP20 · CC BY 4.0',
      note: {
        es: 'CORS: el servicio refleja el origen solo en páginas https. En http local se muestra Sentinel-2 2016.',
        de: 'CORS: Origin wird nur bei https gespiegelt. Lokal über http erscheint Sentinel-2 2016.',
        en: 'CORS: Origin is echoed only on https. Over local http, Sentinel-2 2016 is shown.'
      }
    },
    MV: {
      id: 'MV',
      name: {es:'Mecklemburgo-Pomerania Occidental', de:'Mecklenburg-Vorpommern', en:'Mecklenburg-Vorpommern'},
      res: '20 cm', year: {es:'ciclo de unos 3 años', de:'Zyklus von etwa 3 Jahren', en:'cycle of about 3 years'},
      license: {es:'atribución exigida; sin otras condiciones en el capabilities', de:'Quellenvermerk Pflicht; sonst keine Bedingungen im Capabilities', en:'attribution required; no other conditions in the capabilities'},
      endpoint: 'https://www.geodaten-mv.de/dienste/adv_dop', layer: 'mv_dop',
      minzoom: 13, maxzoom: 18, center: [11.414, 53.635], zoom: 14,
      credit: '© GeoBasis-DE/M-V, DOP 20 cm',
      note: {
        es: 'El WMS declara una resolución máxima de 0,20 m. Hay DOP10 como producto de descarga; este servicio de visualización es de 20 cm. El capabilities no nombra dl-de ni CC: exige el crédito y dice que no hay otras condiciones.',
        de: 'Der WMS nennt maximal 0,20 m. DOP10 gibt es als Download; dieser Darstellungsdienst ist 20 cm. Keine dl-de- oder CC-Angabe im Capabilities, nur der Quellenvermerk.',
        en: 'The WMS states a maximum of 0.20 m. DOP10 exists as a download; this view service is 20 cm. The capabilities name neither dl-de nor CC: they require the credit and state no other conditions.'
      }
    },
    SL: {
      id: 'SL',
      name: {es:'Sarre', de:'Saarland', en:'Saarland'},
      res: '20 cm', year: '2025', license: 'dl-de/by-2-0', href: DLBY,
      endpoint: 'https://geoportal.saarland.de/freewms/dop2025', layer: 'sl_dop20_rgb',
      minzoom: 13, maxzoom: 18, center: [6.996, 49.235], zoom: 14.6,
      credit: '© GeoBasis-DE/LVGL-SL, DOP20 2025 · dl-de/by-2-0',
      note: {
        es: 'El capabilities de 2025 dice Fees «None» y AccessConstraints «noLimitations». Las fichas MetaVer de la misma serie DOP (2020 y 2022) publican dl-de/by-2-0. Se muestra la capa RGB, no la infrarroja.',
        de: 'Capabilities 2025: Fees „None“, AccessConstraints „noLimitations“. MetaVer-Einträge derselben DOP-Serie (2020, 2022) nennen dl-de/by-2-0. Angezeigt wird RGB, nicht Infrarot.',
        en: 'The 2025 capabilities say Fees “None” and AccessConstraints “noLimitations”. MetaVer records for the same DOP series (2020, 2022) use dl-de/by-2-0. The RGB layer is shown, not infrared.'
      }
    },
    RP: {
      id: 'RP', usable: false,
      name: {es:'Renania-Palatinado', de:'Rheinland-Pfalz', en:'Rhineland-Palatinate'},
      res: '20 cm', year: {es:'fecha de vuelo variable', de:'Flugdatum variabel', en:'flight date varies'},
      license: 'dl-de/by-2-0', href: DLBY,
      endpoint: 'https://www.geoportal.rlp.de/owsproxy/00000000000000000000000000000000/a58791b84b5c4245c83f1155bbd51720',
      layer: 'rp_dop20',
      center: [8.247, 49.992], zoom: 14,
      credit: '© GeoBasis-DE / LVermGeoRP, DOP20 · dl-de/by-2-0',
      note: {
        es: 'El GetMap devuelve un JPEG (licencia dl-de/by-2-0 en el capabilities), pero ni http ni https reciben Access-Control-Allow-Origin. No se dibuja. Aquí se ve la vista general de 2016.',
        de: 'GetMap liefert ein JPEG (dl-de/by-2-0 im Capabilities), aber weder http noch https erhalten Access-Control-Allow-Origin. Nicht gezeichnet; Übersicht 2016.',
        en: 'GetMap returns a JPEG (dl-de/by-2-0 in the capabilities), but neither http nor https receives Access-Control-Allow-Origin. It is not drawn; the 2016 overview is shown.'
      }
    }
  };

  const ORDER = ['BHV','HB','BE','BB','HH','NW','BY','BW','HE','SN','TH','NI','ST','SH','MV','SL','RP'];

  const COPY = {
    es: {
      y1945:'1945', compare:'Comparar', hoy:'Hoy',
      swipe:'Arrastrar el límite entre 1945 y hoy',
      sourcesTitle:'Ortofotos oficiales',
      sourcesLead:'«Hoy» elige, según el lugar, la ortofoto oficial abierta de más resolución cuyo WMS respondió con imagen y CORS el 7 de noviembre de 2026. Al alejar el mapa, la vista general es Sentinel-2 de 2016 (10 m), no una ortofoto actual.',
      histLead:'Fotografía aérea de 1945 verificada: solo Bremerhaven (mes no documentado; no decir «mayo»). No hay mosaico abierto de 1945 para Berlín (1953 no es 1945), Hamburgo, NRW (desde 1951), Baviera, Dresde (1953), Fráncfort (visor sin WMS ni licencia confirmados) ni el resto. Sajonia-Anhalt ofrece descargas de 1945, no un WMS raster comprobado.',
      columns:'Las columnas doradas son el memorial de hoy, no edificios de 1945. Las posiciones son las actuales.',
      edges:'Los bordes negros son huecos del mosaico original.',
      zoomOut:'Vista general de 2016. Acerque para la ortofoto oficial.',
      noCors:'Sin ortofoto usable en este navegador.',
      https:'Se necesita https para esta ortofoto.',
      open:'Ver', see1945:'Ver 1945',
      endpoint:'Servicio', close:'Cerrar',
      unavailable:'Sin capa de 1945'
    },
    de: {
      y1945:'1945', compare:'Vergleichen', hoy:'Heute',
      swipe:'Grenze zwischen 1945 und heute ziehen',
      sourcesTitle:'Amtliche Orthophotos',
      sourcesLead:'„Heute“ wählt je nach Ort das offen lizenzierte Orthophoto höchster Auflösung, dessen WMS am 7. November 2026 ein Bild und CORS lieferte. Weit herausgezoomt ist die Übersicht Sentinel-2 von 2016 (10 m), kein aktuelles Orthophoto.',
      histLead:'Geprüftes Luftbild von 1945: nur Bremerhaven (Monat nicht belegt; nicht „Mai“ sagen). Kein offenes 1945-Mosaik für Berlin (1953 ist nicht 1945), Hamburg, NRW (ab 1951), Bayern, Dresden (1953), Frankfurt (Viewer ohne belegtes WMS und Lizenz) und die übrigen Städte. Sachsen-Anhalt hat 1945-Downloads, keinen geprüften Raster-WMS.',
      columns:'Die goldenen Säulen sind das heutige Mahnmal, keine Gebäude von 1945. Die Positionen sind die heutigen.',
      edges:'Schwarze Ränder sind Lücken des ursprünglichen Mosaiks.',
      zoomOut:'Übersicht von 2016. Hineinzoomen für das amtliche Orthophoto.',
      noCors:'In diesem Browser kein nutzbares Orthophoto.',
      https:'Für dieses Orthophoto ist https nötig.',
      open:'Zeigen', see1945:'1945 zeigen',
      endpoint:'Dienst', close:'Schließen',
      unavailable:'Keine 1945-Schicht'
    },
    en: {
      y1945:'1945', compare:'Compare', hoy:'Today',
      swipe:'Drag the edge between 1945 and today',
      sourcesTitle:'Official orthophotos',
      sourcesLead:'“Today” selects, by place, the highest-resolution open official orthophoto whose WMS returned an image and CORS on 7 November 2026. Zoomed out, the overview is Sentinel-2 from 2016 (10 m), not a current orthophoto.',
      histLead:'Verified 1945 aerial photograph: Bremerhaven only (month not documented; do not say “May”). No open 1945 mosaic for Berlin (1953 is not 1945), Hamburg, NRW (from 1951), Bavaria, Dresden (1953), Frankfurt (viewer without a confirmed WMS or licence), or the other cities. Saxony-Anhalt has 1945 downloads, not a verified raster WMS.',
      columns:'The golden columns are today’s memorial, not 1945 buildings. The positions are today’s.',
      edges:'Black edges are gaps in the original mosaic.',
      zoomOut:'2016 overview. Zoom in for the official orthophoto.',
      noCors:'No orthophoto this browser can draw.',
      https:'This orthophoto needs https.',
      open:'Show', see1945:'Show 1945',
      endpoint:'Service', close:'Close',
      unavailable:'No 1945 layer'
    }
  };

  let hooks = {}, POLYS = [], aerial = false, epoch = 'hoy', region = null;
  let mapHist = null, swipeP = 0.5, dimmed = false, hiddenIds = [];
  let moveTimer = 0, histBound = false, colsFC = null, dopKey = '';

  const $ = s => document.querySelector(s);
  const L = () => hooks.getLang ? hooks.getLang() : 'es';
  const T = k => (COPY[L()] || COPY.es)[k];
  const txt = v => !v ? '' : (typeof v === 'string' ? v : (v[L()] || v.es || ''));
  const secure = () => location.protocol === 'https:';
  const usable = src => !!(src && src.usable !== false && src.layer && (!src.httpsOnly || secure()));

  function inRect(b, lon, lat) { return b[0] <= lon && lon <= b[2] && b[1] <= lat && lat <= b[3]; }
  function ringHas(ring, lon, lat) {
    let inside = false, j = ring.length - 1;
    for (let i = 0; i < ring.length; i++) {
      const xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1];
      if ((yi > lat) !== (yj > lat) && lon < (xj - xi) * (lat - yi) / (yj - yi) + xi) inside = !inside;
      j = i;
    }
    return inside;
  }
  function contains(geom, lon, lat) {
    const polys = geom.type === 'MultiPolygon' ? geom.coordinates : [geom.coordinates];
    for (const poly of polys) {
      if (!poly || !poly.length || !ringHas(poly[0], lon, lat)) continue;
      if (poly.slice(1).some(h => ringHas(h, lon, lat))) continue;
      return true;
    }
    return false;
  }
  function regionAt(lon, lat) {
    const hb = POLYS.find(p => p.id === 'HB');
    if (hb && contains(hb.geom, lon, lat)) {
      if (inRect(BHV_B, lon, lat)) return 'BHV';
      if (inRect(HB_B, lon, lat)) return 'HB';
    }
    for (const p of POLYS) {
      if (p.id === 'HB') continue;
      if (contains(p.geom, lon, lat)) return p.id;
    }
    return null;
  }
  function bboxOf(geom) {
    let w = 180, s = 90, e = -180, n = -90;
    const polys = geom.type === 'MultiPolygon' ? geom.coordinates : [geom.coordinates];
    for (const poly of polys) for (const ring of poly) for (const p of ring) {
      if (p[0] < w) w = p[0]; if (p[0] > e) e = p[0];
      if (p[1] < s) s = p[1]; if (p[1] > n) n = p[1];
    }
    return [w - 0.04, s - 0.04, e + 0.04, n + 0.04];
  }
  function boundsFor(src) {
    if (src.bounds) return src.bounds;
    const p = POLYS.find(x => x.id === src.id);
    if (p) return bboxOf(p.geom);
    const c = src.center;
    return [c[0] - 1.2, c[1] - 0.8, c[0] + 1.2, c[1] + 0.8];
  }

  function square(lo, la, halfM) {
    const m = 111320, dLa = halfM / m, dLo = halfM / (m * Math.cos(la * Math.PI / 180));
    return [[[lo - dLo, la - dLa], [lo + dLo, la - dLa], [lo + dLo, la + dLa], [lo - dLo, la + dLa], [lo - dLo, la - dLa]]];
  }
  function columnFC() {
    if (colsFC) return colsFC;
    const data = hooks.getData ? hooks.getData() : [];
    const feats = [];
    for (const s of data) {
      if (!inRect(BHV_B, s.lo, s.la)) continue;
      const lo = s._dlo || s.lo, la = s._dla || s.la;
      feats.push({type:'Feature', properties:{h:16}, geometry:{type:'Polygon', coordinates:square(lo, la, 0.75)}});
    }
    colsFC = {type:'FeatureCollection', features:feats};
    return colsFC;
  }

  function map() { return hooks.getMap ? hooks.getMap() : null; }
  function beforeId() {
    const m = map(); if (!m || !m.getStyle()) return undefined;
    for (const id of ['bldg3d', 'glow', 'stone-dots', 'stones']) if (m.getLayer(id)) return id;
    const sym = m.getStyle().layers.find(l => l.type === 'symbol');
    return sym && sym.id;
  }
  function drop(id) {
    const m = map(); if (!m || !m.getStyle()) return;
    if (m.getLayer(id)) m.removeLayer(id);
    if (m.getSource(id)) m.removeSource(id);
  }

  function dimVector(on) {
    const m = map(); if (!m || !m.getStyle()) return;
    if (on === dimmed) return;
    dimmed = on;
    if (!on) {
      for (const id of hiddenIds) if (m.getLayer(id)) { try { m.setLayoutProperty(id, 'visibility', 'visible'); } catch (e) {} }
      hiddenIds = [];
      const bg = m.getStyle().layers.find(l => l.type === 'background');
      return;
    }
    hiddenIds = [];
    const skip = {sentinel:1, dop:1, histmain:1, bldg3d:1, glow:1, 'stone-dots':1, stones:1, sel:1, 'sel-glow':1};
    for (const l of m.getStyle().layers) {
      if (skip[l.id] || l.type === 'symbol' || l.type === 'background') continue;
      try { m.setLayoutProperty(l.id, 'visibility', 'none'); hiddenIds.push(l.id); } catch (e) {}
    }
    const bg = m.getStyle().layers.find(l => l.type === 'background');
    if (bg) { try { m.setPaintProperty(bg.id, 'background-color', '#14110e'); } catch (e) {} }
  }
  function photoLabels() {
    const m = map(); if (!m || !m.getStyle()) return;
    for (const l of m.getStyle().layers) {
      if (l.type !== 'symbol') continue;
      try {
        m.setPaintProperty(l.id, 'text-halo-color', 'rgba(255,250,242,0.94)');
        m.setPaintProperty(l.id, 'text-halo-width', 1.5);
        m.setPaintProperty(l.id, 'text-color', '#1a1714');
      } catch (e) {}
    }
  }
  function buildings(on) { if (hooks.buildings) hooks.buildings(on); }

  function addRaster(id, tiles, bounds, minzoom, maxzoom, extraPaint) {
    const m = map();
    drop(id);
    m.addSource(id, {type:'raster', tiles:tiles, tileSize:256, bounds:bounds, minzoom:0, maxzoom:maxzoom || 18, attribution:''});
    const paint = Object.assign({'raster-fade-duration':0, 'raster-resampling':'linear'}, extraPaint || {});
    const layer = {id:id, type:'raster', source:id, paint:paint};
    if (minzoom) layer.minzoom = minzoom;
    const before = beforeId();
    if (before) m.addLayer(layer, before); else m.addLayer(layer);
  }
  function ensureSentinel(on) {
    const m = map(); if (!m || !m.getStyle()) return;
    if (!on) { drop('sentinel'); return; }
    if (m.getSource('sentinel')) return;
    addRaster('sentinel', SENTINEL.tiles, [-180, -85, 180, 85], 0, 14, {'raster-saturation':-0.15, 'raster-brightness-max':0.92});
  }

  function mountDop(src) {
    const m = map(); if (!m) return;
    if (dopKey === src.id && m.getSource('dop')) return;
    addRaster('dop', [W(src.endpoint, src.layer, src.extra)], boundsFor(src), src.minzoom || 13, src.maxzoom || 18);
    dopKey = src.id;
  }
  function mountHistMain() {
    const src = SOURCES.BHV;
    const m = map(); if (!m) return;
    if (m.getSource('histmain')) return;
    addRaster('histmain', [W(src.endpoint, src.hist.layer)], BHV_B, 12, 18);
  }

  function syncHist() {
    const m = map();
    if (!mapHist || !m) return;
    mapHist.jumpTo({center:m.getCenter(), zoom:m.getZoom(), bearing:m.getBearing(), pitch:m.getPitch()});
  }
  function paintCols() {
    if (!mapHist || !mapHist.getSource) return;
    if (!mapHist.isStyleLoaded()) return;
    const fc = columnFC();
    if (!mapHist.getSource('cols')) {
      mapHist.addSource('cols', {type:'geojson', data:fc});
      mapHist.addLayer({id:'cols', type:'fill-extrusion', source:'cols',
        paint:{'fill-extrusion-color':'#e0bc62', 'fill-extrusion-height':['get','h'], 'fill-extrusion-opacity':0.95}});
    } else mapHist.getSource('cols').setData(fc);
  }
  function ensureHistMap() {
    const el = $('#mapHist');
    el.hidden = false;
    if (mapHist) { syncHist(); paintCols(); return; }
    const src = SOURCES.BHV;
    mapHist = new maplibregl.Map({
      container:'mapHist',
      style:{version:8, sources:{}, layers:[{id:'bg', type:'background', paint:{'background-color':'#1a1a1a'}}]},
      interactive:false, attributionControl:false, fadeDuration:0,
      pixelRatio:Math.min(window.devicePixelRatio || 1, 1.35),
      canvasContextAttributes:{antialias:false}
    });
    mapHist.on('load', () => {
      mapHist.addSource('h', {type:'raster', tileSize:256, bounds:BHV_B, maxzoom:18,
        tiles:[W(src.endpoint, src.hist.layer)]});
      mapHist.addLayer({id:'h', type:'raster', source:'h', paint:{'raster-fade-duration':0}});
      paintCols();
      syncHist();
    });
    if (!histBound) {
      histBound = true;
      map().on('move', syncHist);
      window.addEventListener('resize', () => { if (mapHist) mapHist.resize(); });
    }
  }
  function destroyHist() {
    if (mapHist) { mapHist.remove(); mapHist = null; }
    const el = $('#mapHist'); if (el) el.hidden = true;
  }
  function applySwipe() {
    const el = $('#mapHist'), line = $('#swipeLine'), handle = $('#swipeHandle');
    if (!el) return;
    el.style.clipPath = 'inset(0 ' + ((1 - swipeP) * 100).toFixed(3) + '% 0 0)';
    if (line) line.style.left = (swipeP * 100) + '%';
    if (handle) handle.style.left = (swipeP * 100) + '%';
    const left = $('#swipeTagL'), right = $('#swipeTagR');
    if (left) left.style.left = '12px';
    if (right) right.style.right = '12px';
  }

  function easeFlat() {
    const m = map(); if (!m) return;
    if (m.getPitch() < 2) return;
    if (hooks.reduce && hooks.reduce()) m.jumpTo({pitch:0});
    else m.easeTo({pitch:0, duration:700});
  }

  function applyView() {
    const m = map();
    if (!m) return;
    if (!m.isStyleLoaded()) { m.once('idle', applyView); return; }
    renderHud();
    if (!aerial) {
      dopKey = '';
      drop('sentinel'); drop('dop'); drop('histmain');
      destroyHist();
      const sw = $('#swipe'); if (sw) sw.hidden = true;
      dimVector(false);
      buildings(true);
      const credit = $('#imgCredit'); if (credit) credit.hidden = true;
      return;
    }
    dimVector(true);
    photoLabels();
    const c = m.getCenter();
    region = regionAt(c.lng, c.lat);
    if ((epoch === '1945' || epoch === 'swipe') && region !== 'BHV') epoch = 'hoy';
    const src = SOURCES[region];
    const z = m.getZoom();
    const dopOk = usable(src) && z >= (src.minzoom || 13) - 0.01;
    const show1945 = epoch === '1945' && region === 'BHV';
    const showSwipe = epoch === 'swipe' && region === 'BHV';

    ensureSentinel(true);
    if (show1945) {
      drop('dop');
      mountHistMain();
      destroyHist();
      const sw = $('#swipe'); if (sw) sw.hidden = true;
      buildings(false);
    } else if (showSwipe) {
      drop('histmain');
      if (dopOk) mountDop(src); else drop('dop');
      ensureHistMap();
      const sw = $('#swipe'); if (sw) sw.hidden = false;
      applySwipe();
      buildings(false);
      easeFlat();
    } else {
      drop('histmain');
      destroyHist();
      const sw = $('#swipe'); if (sw) sw.hidden = true;
      if (dopOk) mountDop(src); else drop('dop');
      buildings(true);
    }
    if (show1945) easeFlat();
    paintCredit(src, z, dopOk, show1945, showSwipe);
    renderHud();
  }

  function paintCredit(src, z, dopOk, show1945, showSwipe) {
    const el = $('#imgCredit'); if (!el) return;
    el.hidden = false;
    el.replaceChildren();
    const add = (text, href) => {
      if (el.childNodes.length) el.append(document.createTextNode(' · '));
      if (href) {
        const a = document.createElement('a');
        a.href = href; a.target = '_blank'; a.rel = 'noopener';
        a.textContent = text;
        el.append(a);
      } else el.append(document.createTextNode(text));
    };
    if (show1945 || showSwipe) add(SOURCES.BHV.hist.credit, SOURCES.BHV.hist.href);
    if (!show1945 && dopOk && src) add(src.credit, src.href);
    if (!show1945 && !dopOk) add(txt(SENTINEL.credit), SENTINEL.href);
  }

  function renderHud() {
    const hud = $('#aerialHud');
    const bar = $('#epochToggle');
    const hint = $('#hoyHint');
    if (!hud || !bar || !hint) return;
    const m = map();
    if (m && POLYS.length) region = regionAt(m.getCenter().lng, m.getCenter().lat);
    const inB = region === 'BHV';
    hud.hidden = !(aerial || inB);
    hint.textContent = hintText();
    bar.replaceChildren();
    if (!inB) return;
    const modes = [['1945', T('y1945')], ['swipe', T('compare')], ['hoy', T('hoy')]];
    for (const [mode, label] of modes) {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = label;
      b.setAttribute('aria-pressed', aerial && epoch === mode ? 'true' : 'false');
      b.onclick = () => setEpoch(mode);
      bar.append(b);
    }
  }
  function hintText() {
    const src = SOURCES[region];
    const m = map();
    const z = m ? m.getZoom() : 0;
    if (!aerial && region === 'BHV') {
      return L() === 'de' ? 'Bremerhaven: Luftbild 1945 und DOP10 2025.' :
        L() === 'en' ? 'Bremerhaven: 1945 aerial photograph and DOP10 2025.' :
        'Bremerhaven: fotografía de 1945 y DOP10 de 2025.';
    }
    if (!aerial) return '';
    if (epoch === '1945' || epoch === 'swipe') return T('columns') + ' ' + T('edges');
    if (!src) return T('zoomOut');
    if (src.usable === false) return txt(src.note) || T('noCors');
    if (src.httpsOnly && !secure()) return txt(src.note) || T('https');
    if (z < (src.minzoom || 13)) {
      const extra = src.note ? ' ' + txt(src.note) : '';
      return T('zoomOut') + extra;
    }
    const year = txt(src.year), res = txt(src.res), lic = txt(src.license);
    return txt(src.name) + ' · ' + res + ' · ' + year + ' · ' + lic;
  }

  function whenReady(fn) {
    const m = map(); if (!m) return;
    if (m.isStyleLoaded()) fn();
    else m.once('idle', fn);
  }
  function setEpoch(mode) {
    const m = map(); if (!m) return;
    epoch = mode;
    aerial = true;
    if (hooks.markHoy) hooks.markHoy();
    const go = () => {
      if ((mode === '1945' || mode === 'swipe') && regionAt(m.getCenter().lng, m.getCenter().lat) !== 'BHV') {
        m.jumpTo({center:SOURCES.BHV.center, zoom:SOURCES.BHV.zoom, pitch:0, bearing:m.getBearing()});
      }
      if (!m.getSource('openmaptiles') && hooks.needNightStyle) { hooks.needNightStyle(); return; }
      applyView();
    };
    whenReady(go);
  }
  function setHoy(on) {
    if (!on) { aerial = false; epoch = 'hoy'; whenReady(applyView); return; }
    aerial = true;
    if (epoch !== '1945' && epoch !== 'swipe') epoch = 'hoy';
    whenReady(applyView);
  }

  function fillSources() {
    const body = $('#sourcesBody'); if (!body) return;
    body.replaceChildren();
    const h = document.createElement('h2'); h.textContent = T('sourcesTitle'); body.append(h);
    const p = document.createElement('p'); p.textContent = T('sourcesLead'); body.append(p);
    const p2 = document.createElement('p'); p2.textContent = T('histLead'); body.append(p2);
    const list = document.createElement('ol'); list.className = 'src-list';
    for (const id of ORDER) {
      const src = SOURCES[id];
      const li = document.createElement('li');
      const title = document.createElement('strong');
      title.textContent = txt(src.name);
      li.append(title);
      const meta = document.createElement('div');
      meta.className = 'src-meta';
      const bits = [txt(src.res), txt(src.year), txt(src.license)].filter(Boolean);
      if (src.hist) bits.unshift('1945 + ' + T('hoy'));
      if (src.usable === false) bits.push(T('noCors'));
      else if (src.httpsOnly && !secure()) bits.push(T('https'));
      meta.textContent = bits.join(' · ');
      li.append(meta);
      if (src.note) {
        const n = document.createElement('p'); n.className = 'src-note'; n.textContent = txt(src.note); li.append(n);
      }
      const a = document.createElement('a');
      a.href = capsUrl(src.endpoint); a.target = '_blank'; a.rel = 'noopener';
      a.textContent = T('endpoint');
      li.append(a);
      if (src.usable !== false) {
        const b = document.createElement('button'); b.type = 'button'; b.textContent = T('open');
        b.onclick = () => { $('#sourcesDlg').close(); fly(src); };
        li.append(b);
      }
      if (src.hist) {
        const b = document.createElement('button'); b.type = 'button'; b.textContent = T('see1945');
        b.onclick = () => { $('#sourcesDlg').close(); setEpoch('1945'); };
        li.append(b);
      }
      list.append(li);
    }
    body.append(list);
    const close = $('#sourcesClose'); if (close) close.textContent = T('close');
    const handle = $('#swipeHandle'); if (handle) handle.setAttribute('aria-label', T('swipe'));
    const tagL = $('#swipeTagL'); if (tagL) tagL.textContent = '1945';
    const tagR = $('#swipeTagR'); if (tagR) tagR.textContent = T('hoy');
  }
  function fly(src) {
    const m = map(); if (!m || !src.center) return;
    if (!aerial && hooks.markHoy) { aerial = true; epoch = 'hoy'; hooks.markHoy(); }
    else { aerial = true; if (epoch !== '1945' && epoch !== 'swipe') epoch = 'hoy'; }
    m.flyTo({center:src.center, zoom:src.zoom || 14.5, pitch:epoch === 'hoy' ? Math.max(m.getPitch(), 48) : 0,
      bearing:m.getBearing(), duration:(hooks.reduce && hooks.reduce()) ? 0 : 1800, essential:true});
    if (!m.getSource('openmaptiles') && hooks.needNightStyle) hooks.needNightStyle();
    else applyView();
  }

  function schedule() { clearTimeout(moveTimer); moveTimer = setTimeout(applyView, 80); }

  function wireSwipe() {
    const handle = $('#swipeHandle'); if (!handle) return;
    let drag = false;
    const pos = clientX => {
      const wrap = document.querySelector('.mapwrap').getBoundingClientRect();
      swipeP = Math.min(0.92, Math.max(0.08, (clientX - wrap.left) / wrap.width));
      applySwipe();
    };
    handle.addEventListener('pointerdown', e => { drag = true; handle.setPointerCapture(e.pointerId); e.preventDefault(); e.stopPropagation(); });
    handle.addEventListener('pointermove', e => { if (drag) pos(e.clientX); });
    handle.addEventListener('pointerup', () => { drag = false; });
    handle.addEventListener('keydown', e => {
      if (e.key === 'ArrowLeft') { swipeP = Math.max(0.08, swipeP - 0.04); applySwipe(); }
      if (e.key === 'ArrowRight') { swipeP = Math.min(0.92, swipeP + 0.04); applySwipe(); }
    });
    const btn = $('#sourcesBtn');
    if (btn) btn.onclick = () => { fillSources(); $('#sourcesDlg').showModal(); };
  }

  window.KLImagery = {
    init(opts) {
      hooks = opts || {};
      wireSwipe();
      const m = map();
      if (m) m.on('moveend', schedule);
      fetch('geo/de-states.json').then(r => r.json()).then(gj => {
        POLYS = gj.features.map(f => ({id:f.properties.id, geom:f.geometry}));
        applyView();
      }).catch(e => console.warn('states', e));
      fillSources();
    },
    onStyle() { dimmed = false; hiddenIds = []; dopKey = ''; applyView(); },
    onData() { colsFC = null; paintCols(); },
    setHoy, setEpoch,
    setSwipe(p) { swipeP = p; applySwipe(); },
    refresh() { fillSources(); renderHud(); applyView(); },
    isAerial() { return aerial; },
    status() { return {region, epoch, aerial, swipe:swipeP}; }
  };
})();
