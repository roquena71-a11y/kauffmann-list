# ESTADO v25 — paso 3: texto de la inscripción en la placa
Rama v25-texto desde e9994bfa (v30, paso 1 en auditoría), worktree /workspace/kl-v25-texto. Sin push ni publicación.
RESTRICCIÓN mientras auditan el paso 1: nada de run-all, pruebas de presupuesto ni capturas pesadas; solo comprobaciones ligeras (node, una página a nice 19).

## Diseño
- plaquetext.js (nuevo, carga perezosa al llegar a zoom ≥19,5; nunca en la carga inicial): capa custom WebGL '3d' con un cuadrado texturizado por placa sobre la cara de latón (≈16,45 m), solo placas en vista a z≥20 (máx. 60, las más cercanas al centro).
- Texto SOLO del campo i (como la ficha: «|» y saltos = líneas; se ajusta al ancho), en MAYÚSCULAS, letras #3a2a10 sobre la cara #d6b25a. z20,5–21,5: solo la línea del nombre (segmento de i que contiene el nombre); z≥21,5: inscripción completa. Sin i (o sin línea de nombre en modo nombre): latón en blanco con surcos.
- Orientación: lados de la placa según _ang (align-v24); de los 4 giros de 90° se usa el más derecho para la cámara.
- Donde hay texto se ocultan los surcos de esa placa (filtro en 'stones-grooves').
- Precisión: matriz con origen local en doble precisión (vértices en metros), sin pérdidas de float32.

## Estado 24-11-2026 05:22 (hora de Berlín) — CÓDIGO LISTO PARA PRUEBAS COMPLETAS (no ejecutadas: esperar permiso)
Versión v31 (tests/bump-version.py; plaquetext.js?v=31 en el SHELL del service worker). Commits en v25-texto.
- Cambio respecto al plan: el modo NO depende solo del zoom. Medido (escritorio 1280x800): la cámara está a 33 m a z20,5,
  23 m a z21 y 16 m (¡a la altura de las placas!) a z21,5; teléfono 43 / 30 / 21 m. Cara de 0,86 m en pantalla: escritorio
  51 px (z20,5) / 124 px (z21); teléfono 41 / 79 / 219 px (z20,5 / 21 / 21,5). Por eso: desde z20, nombre si la cara mide
  ≥ 40 px, inscripción entera si ≥ 100 px, y nada si la cámara está a < 1 m sobre la placa (o debajo: escritorio > z21,4).
  Resultado ≈ plan: escritorio nombre z20,5 / entera ~z20,9; teléfono nombre z20,5 / entera ~z21,2.
- Línea del nombre: trozo LITERAL de i, del primer al último término del nombre (campo n) — p. ej. «MARGOT ADLER». Si no está, nada.
- Inscripciones que no caben ni a la letra mínima (14 de 67.013): placa lisa (nunca texto cortado).
- Cámara inclinada a zoom alto: las placas (16 m) quedan por encima de la vista; se dibujan igual (no molesta).
- Aviso de consola previo, NO de este paso (sale también con ?textooff=1): «Expected value to be of type number, but found null».
- ?textooff=1 desactiva el texto (placas como v30).

Pruebas:
- tests/v25-plaque-text-unit.cjs (node, en run-all): 75.122 placas; 67.013 con i = texto de la ficha en mayúsculas; 8.109 lisas;
  nombre literal en 63.018; ajuste sin perder palabras; contraste letras/cara 6,83:1 (WCAG AA ≥ 4,5).
- tests/v25-plaque-text-check.py (navegador, en run-all tras v25-corner): una sola ejecución de humo a nice 19 → OK
  (perezoso; z20,2 nada; z20,8 nombre 4; z21,2 entera 4; girado 100° 4; inclinado 30° 4; z21,6 nada; surcos ocultos solo bajo
  texto; 8.109 sin i siempre lisas; 20.760 píxeles cambian, 18.404 más oscuros; contador bloqueado, 0 peticiones).
- version-test, counter-sw-test, update-flow-test: OK.
- NO ejecutado (por la restricción de auditoría): run-all completo, presupuesto de carga, capturas grandes.
Capturas de humo: /workspace/v24-data/texto-smoke/on-z21.2-p0.png (inscripción legible), on-z20.8-p0.png (nombre).

## 24-11-2026 06:18–06:49 (hora de Berlín) — run-all COMPLETO: OK (RUN_ALL_EXIT:0, «FALLOS: ninguno»)
Paso 1 aprobado por los 3 auditores. Venv nuevo (/workspace/v24-data/venv-runall-v25t), REQUIRE_OAV=1, sin SKIP, contador
bloqueado (/etc/hosts de bloqueo + rutas), presupuesto sin cambiar. Script /workspace/v24-data/run-all-v25t.sh, registro
/workspace/v24-data/run-all-v25t-0618.log. Presupuesto de carga (412x915 4G 2xCPU): fcp 196 ms, overview 5406 ms,
overlays 9839 ms (v30: 9798), vis 10430 ms, street_zoom 129/513 ms — plaquetext.js no entra en la carga. Sin el fallo
intermitente de atribución a 844x390.
- Prueba inclinada reforzada (commit 928a7d44): vista centrada en las CARAS (centro desplazado 16,42·tan(p) en el rumbo),
  35° y rumbo 30° a z20,6: la captura con texto ≠ sin texto (3798 píxeles, 3649 más oscuros), cambios dentro del mapa, modo nombre.
  El tamaño de cara en pantalla ahora se mide a lo largo del rayo central (D − h/cos p), correcto también inclinado.
- Revisada a ojo la vista de nombre (z20,8): HERMANN ADLER / RUTH ADLER / MARGOT ADLER / AMALIE ADLER, legibles y derechas.

## 24-11-2026 08:12–08:16 (hora de Berlín) — v32: marcado HTML/wiki en inscripciones (nota del auditor A)
Los 3 auditores aprobaron v31 (fe93a97f). Arreglo SOLO DE PRESENTACIÓN (data/ sin cambios): KLDedupe.inscDisplay (dedupe.js)
usado por la ficha (app3d.js, placa de latón) y por la placa 3D (plaquetext.js inscOf):
<br>, <br/>, <br /> → salto; <b> sin ningún </b> (separador roto) → salto; otras etiquetas fuera (espacio si unían palabras);
'''x''' → x ('' sueltas = comillas reales, se quedan); [[destino|texto]] → texto, [[x]] → x; entidades &#8218; &nbsp; … → carácter.
Afectadas: 116 inscripciones en 116 placas — 40 con <br>/<b> (las de la nota del auditor A: 35 <br>, 2 <br>+''', 3 <b>),
64 con '''negrita''', 6 [[enlace]], 6 &#…;. Lista con antes/después (ficha y placa): /workspace/v24-data/review/inscripciones-markup.csv
(script: /workspace/v24-data/review/make-markup-csv.cjs). «<haft 11.11.1938» (n13378996105) no es etiqueta: se deja igual.
Pruebas: v25-plaque-text-unit.cjs (no queda marcado; mismas palabras que una referencia independiente; <br> = líneas; 10 casos
fijos) y v25-plaque-text-check.py (ficha y placa de 4 casos en el navegador). Versión v32 (kauffmann-v32-pages).

## 24-11-2026 08:17–08:48 (hora de Berlín) — run-all COMPLETO v32: OK (RUN_ALL_EXIT:0, «FALLOS: ninguno»)
Venv nuevo (/workspace/v24-data/venv-runall-v32), REQUIRE_OAV=1, sin SKIP, contador bloqueado, presupuesto sin cambiar; carga al
empezar 0,91. Registro /workspace/v24-data/run-all-v32-0817.log. Presupuesto (412x915 4G 2xCPU): fcp 176 ms, overview 5347 ms,
overlays 9643 ms, vis 10227 ms, street_zoom 85/501 ms. Atribución a 844x390 sin fallo intermitente.
