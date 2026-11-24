# ESTADO v25 — revisión (solo investigación, sin publicar)
Worktree /workspace/kl-v25-review, rama v25-review desde 3e46ab52 (v29 en vivo). Notas y datos en /workspace/v24-data/review/, capturas en /workspace/v24-data/shots-review/.
## 1 · Fotos
- 02:20 Cliente local (contador bloqueado, 0 peticiones): 74 979 placas visibles, 53 476 con foto (71,3 %), 21 503 sin foto.
  Por fuente (visibles / con foto): osm+wd 29 427/28 005 · osm 21 376/9 822 · wd 21 168/15 649 · municipales (Köln 1 550, Den Haag 306, Berlín 286, …) 3 008/0.
- La ficha muestra la foto de Commons (Special:FilePath?width=480, loading=lazy). Prueba UI: 6/6 cargan (naturalWidth 245–500), 0 errores de consola. Muestra HEAD/GET de 39 miniaturas: 39/39 OK. Sin CSP que lo bloquee. No hay foto en el mapa, solo en la ficha.
- 49 552 de los 53 476 nombres de archivo contienen «Stolperstein» (el resto suele ser retrato de la persona o de la casa).
- Fuentes nuevas comprobadas: Wikidata hoy (SPARQL 02:23): 969 placas sin foto ya tienen P18 + 375 solo categoría P373. OSM fuera de DE (extractos v20): ~346 con archivo de Commons en image/wikimedia_commons no usado (108 de stolpersteine-salzburg.at y otros: licencia desconocida, no). imgx (URL Commons) en 332 placas sin foto no se usa en la ficha. OSM DE: sin extracto local y Overpass no responde (02:26) → desconocido.
