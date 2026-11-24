# ESTADO v25 — revisión (solo investigación, sin publicar)
Worktree /workspace/kl-v25-review, rama v25-review desde 3e46ab52 (v29 en vivo). Notas y datos en /workspace/v24-data/review/, capturas en /workspace/v24-data/shots-review/.
## 1 · Fotos
- 02:20 Cliente local (contador bloqueado, 0 peticiones): 74 979 placas visibles, 53 476 con foto (71,3 %), 21 503 sin foto.
  Por fuente (visibles / con foto): osm+wd 29 427/28 005 · osm 21 376/9 822 · wd 21 168/15 649 · municipales (Köln 1 550, Den Haag 306, Berlín 286, …) 3 008/0.
- La ficha muestra la foto de Commons (Special:FilePath?width=480, loading=lazy). Prueba UI: 6/6 cargan (naturalWidth 245–500), 0 errores de consola. Muestra HEAD/GET de 39 miniaturas: 39/39 OK. Sin CSP que lo bloquee. No hay foto en el mapa, solo en la ficha.
- 49 552 de los 53 476 nombres de archivo contienen «Stolperstein» (el resto suele ser retrato de la persona o de la casa).
- Fuentes nuevas comprobadas: Wikidata hoy (SPARQL 02:23): 969 placas sin foto ya tienen P18 + 375 solo categoría P373. OSM fuera de DE (extractos v20): ~346 con archivo de Commons en image/wikimedia_commons no usado (108 de stolpersteine-salzburg.at y otros: licencia desconocida, no). imgx (URL Commons) en 332 placas sin foto no se usa en la ficha. OSM DE: sin extracto local y Overpass no responde (02:26) → desconocido.
## 3 · Remates
- 02:45 shots_review.py (/workspace/v24-data/review/): v29 en vivo vs variante de diagnóstico exp-mz22 (fuentes con maxzoom 22, inyectado solo en el navegador). Primera pasada cortada por tiempo (700 s): solo parte de las capturas.
## 2 · Inscripción en la placa
- 02:55 66 883/74 979 visibles tienen inscripción (campo i): osm+wd 29 310, osm 18 016, wd 19 427 (OSM inscription = ODbL; Wikidata P1684 = CC0), Firenze 95 y Grevenbroich 35 (abiertos municipales); 8 096 sin texto (incl. 2 878 municipales). Longitud: mediana 89, p90 130, máx 532 caracteres.
- Ya se muestra en la ficha como «brassplate» HTML. En el mapa: placa = 0,86 m de cara (half 0,43). A z20 en lat 50 son ~9 px CSS; a z22 (máx. del mapa) ~36 px → el nombre solo es legible a z≥21,5 y la inscripción completa nunca a escala.
- MapLibre 5.24: las etiquetas (symbol) van al suelo, no a 16,4 m; fill-extrusion-pattern no se puede orientar por placa. Vía viable: capa custom WebGL (quads texturizados a 16,42 m con atlas de texto en canvas) solo para placas en vista a z≥19, cargada aparte (no afecta al presupuesto de carga inicial).
- 03:12 Capturas de escritorio v29 (cenital z20.5, z19.5; 35° z19.5; 50° z18.5) hechas. Diagnóstico en código (columns.js / app3d.js):
  a) Fuentes GeoJSON de columna/placa/surcos con maxzoom:16 → MapLibre recorta y cuantiza a la rejilla de la tesela z16 (8192 unidades por ~393 m en lat 50 ≈ 4,8 cm). Las esquinas redondeadas (radio 5–11 cm, 8 segmentos) y el canto del marco (0,08 m = 1,7 pasos) quedan escalonados y de grosor desigual por lado.
  b) Antialias desactivado en pantallas ≤760 px (antialias:!narrowScreen, también en canvasContextAttributes): en el teléfono, bordes en dientes de sierra.
  c) Surcos a 16,30–16,345 m DENTRO de la cara de latón (16,16–16,42 m): están tapados; solo asoman como puntitos (precisión de profundidad). Por eso la placa se ve «en blanco».
  Experimento exp-mz22 (maxzoom 22 inyectado en el navegador) en marcha para comparar.
- 03:30 CONFIRMADO con el experimento: westend-z20.5-cenital-RECORTE-arriba-v29-abajo-maxzoom22.png → con maxzoom 16 (v29) las esquinas salen en pico/muesca y el marco con grosor desigual; con maxzoom 22 las esquinas son redondas y el marco uniforme. Los surcos solo asoman como puntitos en ambos (tapados por la cara). Capturas de teléfono 390x844 en marcha.
- 03:45 Teléfono 390x844 (DPR 2, sin antialias): mismo defecto, mismo arreglo (westend-z20.5-cenital-390x844-RECORTE-izq-v29-der-maxzoom22.png). 0 peticiones al contador en todas las capturas.
## Fotos nuevas posibles (sin duplicar): P18 actual 969 + imgx 332 + OSM fuera de DE con archivo de Commons 356 → unión 1 650 placas (de 21 503 sin foto). OSM DE: desconocido (Overpass no respondió). Municipales (3 008): sus fuentes no traen foto.
- Aviso de licencia: la ficha enlaza la página de Commons pero no muestra autor ni licencia (CC BY-SA lo pide) → añadir crédito (extmetadata de la API de Commons) en el mismo arreglo.
## Veredicto y plan: ver informe final (resumen al agente principal).

# PASO 1 v25 — esquinas (rama v25-review, desde 3e46ab52)
- 03:13 columns.js: marco/cara concéntricos (radio cara 0,035 m, marco 0,115 m → canto 0,08 m uniforme), ids de fuente fijos (sid), maxzoom placas+surcos 22 y fustes 20, surcos encima de la cara (16,42–16,44 m). node --check OK. Pendiente: prueba, antialias en teléfono, v30, capturas, run-all.
- 03:15 tests/v25-corner-check.py (nuevo, en run-all tras v24-plaque): v30 OK (canto 0,079–0,081 m, error radial ≤0,5 mm; autocontrol z16: 0,045–0,10 m / 1–3 cm → falla como debe); contra v29 FALLA (maxzoom 16, surcos dentro de la cara, canto desigual). Captura rápida z20.5 cenital: esquinas redondas, marco uniforme, surcos visibles.
- 03:26 Medición de antialias en teléfono (aa_measure.py) — 1.ª pasada abortada: una variante dio overlays 11 531 ms (>11 500) con la máquina a carga 2,4 (otro agente ejecuta pipeline/tools/fetch_commons_credits.py); se repite registrando ambas variantes alternadas.
- 03:47 Antialias en teléfono MEDIDO (aa_measure.py, 3 rondas alternas, 412x915 4G CPU×2, SwiftShader; aa-measure.json): presupuesto de carga igual (overlays AA off 11 075/10 258/10 083 ms, AA on 11 102/10 160/10 482 ms, con carga ~2 por la propia medición); fotograma girando a z18.5 66,7 → 133–150 ms y a z20 83–100 → 167–183 ms (≈2×). DECISIÓN: se deja apagado en ≤760 px (el arreglo de geometría quita los picos; el AA duplicaría el coste por fotograma en teléfonos lentos). Sin cambio en app3d.js.
- 03:47 bump-version → v30 (kauffmann-v30-pages, ?v=30), version-test OK.
- 03:47 run-all completo lanzado (venv nuevo venv-runall-v25c, bwrap + hosts del contador, carga 0,46; otro agente tiene fetch_commons_credits.py en marcha con nice, ~1 % CPU) → /workspace/v24-data/run-all-v25c.log
- 03:59 run-all: todo OK hasta v25-corner-check incluido (47 líneas OK); presupuesto overlays 9 798 ms (v29: 9 564), fcp 196, dcl 977, overview 5 488, vis 10 432, street_zoom 128/551 ms. En marcha country-buttons.
- 04:29 **run-all COMPLETO: RUN_ALL_EXIT:0, «run-all: OK», country-buttons «FALLOS: ninguno», 0 omitidas** (03:46–04:21, REQUIRE_OAV=1, venv nuevo venv-runall-v25c, contador bloqueado). Overlays 9 798 ms ≤ 11 500 (sin tocar). Log /workspace/v24-data/run-all-v25c.log. Siguen las capturas antes/después.
- 04:30 Capturas antes(v29 /workspace/kl-v24s2)/después(v30) en marcha: shots-v25-corners.py (reanudable: salta las que ya existen), escritorio y luego teléfono; 2 sitios × (z18.5 50°, z19.5 35°, z20.5 cenital, z20.5 30°).
- 04:51 Capturas: escritorio 12/16 hechas (Westend completo antes/después; Zimmerstraße antes). Cadena reducida: el teléfono se hará solo a z19.5 35° y z20.5 cenital.
- 04:57 Capturas escritorio 16/16 (0 peticiones al contador). Lanzado teléfono 390x844 (z19.5 35°, z20.5 cenital).
- 04:58 Comparación escritorio: /workspace/v24-data/shots-v25-corners/COMPARA-escritorio-1280x800-z20.5-antes-v29-despues-v30.png (script /workspace/v24-data/compare_v25.py). Teléfono en marcha.
- 05:05 Teléfono 6/8 (Westend antes/después, Zimmerstraße antes).
- 05:12 Capturas COMPLETAS (escritorio 16, teléfono 8; 0 peticiones al contador). Comparaciones: /workspace/v24-data/shots-v25-corners/COMPARA-escritorio-1280x800-z20.5-antes-v29-despues-v30.png y COMPARA-telefono-390x844-antes-v29-despues-v30.png. En teléfono (sin antialias) los surcos finos se ven algo dentados/discontinuos a z19.5; esquinas y marco correctos.
- PASO 1 LISTO para auditoría. Sin push.
