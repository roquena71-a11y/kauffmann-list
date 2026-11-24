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
