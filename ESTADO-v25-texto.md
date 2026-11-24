# ESTADO v25 — paso 3: texto de la inscripción en la placa
Rama v25-texto desde e9994bfa (v30, paso 1 en auditoría), worktree /workspace/kl-v25-texto. Sin push ni publicación.
RESTRICCIÓN mientras auditan el paso 1: nada de run-all, pruebas de presupuesto ni capturas pesadas; solo comprobaciones ligeras (node, una página a nice 19).

## Diseño
- plaquetext.js (nuevo, carga perezosa al llegar a zoom ≥19,5; nunca en la carga inicial): capa custom WebGL '3d' con un cuadrado texturizado por placa sobre la cara de latón (≈16,45 m), solo placas en vista a z≥20 (máx. 60, las más cercanas al centro).
- Texto SOLO del campo i (como la ficha: «|» y saltos = líneas; se ajusta al ancho), en MAYÚSCULAS, letras #3a2a10 sobre la cara #d6b25a. z20,5–21,5: solo la línea del nombre (segmento de i que contiene el nombre); z≥21,5: inscripción completa. Sin i (o sin línea de nombre en modo nombre): latón en blanco con surcos.
- Orientación: lados de la placa según _ang (align-v24); de los 4 giros de 90° se usa el más derecho para la cámara.
- Donde hay texto se ocultan los surcos de esa placa (filtro en 'stones-grooves').
- Precisión: matriz con origen local en doble precisión (vértices en metros), sin pérdidas de float32.
