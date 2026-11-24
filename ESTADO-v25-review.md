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
