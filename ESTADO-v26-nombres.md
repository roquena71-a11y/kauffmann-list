# ESTADO v26 — visibilidad de nombres en la placa (C1–C3, C5 barato)
Rama v26-nombres desde c4fe9ec5 (v34 en vivo, origin/main), worktree /workspace/kl-v26-nombres.
Sin push ni publicación. No se tocan datos (la/lo, stones). Se mantiene la ficha v34 (fotos, fechas).
Antialias del teléfono OFF. Presupuesto de overlays 11500 ms, sin subir. Contador bloqueado.

Diagnóstico: /workspace/audits/v24/C/diagnostico-C-v33-live-nombres.md
Mockups: /workspace/audits/v24/C/diag-v33-live/mockups/

Orden aprobado por Carlos (2026-11-25 04:24): C1, C2, C3, C5 (solo lo barato).

## Plan
- C1: la placa seleccionada se queda (texto incluido). Fuera el fuste pálido #fff3c4 de 34/400 m.
  Resalte: marco de oro alrededor de la columna (sigue cuadrada y oro) + resplandor; a zoom bajo, halo que pulsa.
- C2: en pantalla estrecha, PX_NAME ≈ 26 y Z_ON ≈ 19,5 (nombres a zoom de calle en 412×915, inclinación 42°).
- C3: CAM_CLEAR ≈ 0,25 m (solo se oculta el texto si la cámara está casi a la altura de la cara o debajo).
- C5 barato: si la capa WebGL no arranca, no dejar la placa en surcos sin letras; respaldo local, sin enviar nada a la red.

## 25-11-2026 04:26 (hora de Berlín) — C1 hecho
La columna seleccionada ya no se sustituye por el fuste pálido #fff3c4 de 34 m (o 400 m a z<14,6). Se queda la columna de oro
con placa y texto. Resalte: marco hueco de oro (#f0c44a, 16,50 m, fuera del rim) + el resplandor existente. A zoom <14,6,
halo circular que pulsa (respeta «reducir movimiento»). KLPlaqueText deja de saltarse el seleccionado; columns.js ya no
lo filtra de fuste, placa ni surcos.

## 25-11-2026 04:28 (hora de Berlín) — C2 hecho
Pantalla estrecha (≤760 px): Z_ON 19,5 y PX_NAME 26. En teléfono 412×915 a 42°, z20,2 (cara ≈ 31 px) entra en modo nombre
(antes «pequeña»). Escritorio sin cambio (z20 / 40 px). plaquetext.js se pide desde z19,0 en teléfono (z19,5 en escritorio).
