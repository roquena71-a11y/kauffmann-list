#!/bin/sh
# Ejecuta todas las pruebas locales (no publica nada).
set -e
cd "$(dirname "$0")/.."
PYTHON=${PYTHON:-python3}
CHROME=${CHROME_BIN:-/usr/bin/google-chrome}
for f in source-links.js dedupe.js counter.js app3d.js people.js columns.js imagery.js mapui.js sw.js; do node --check "$f"; done
node tests/source-links-test.mjs
node tests/dedupe-test.cjs
node tests/wd-added-test.cjs
node tests/ie-added-test.cjs
node tests/se-added-test.cjs
node tests/jefiro-added-test.cjs
node tests/v20-added-test.cjs
node tests/v21-added-test.cjs
node tests/v22-added-test.cjs
"$PYTHON" tests/v20r2-data-check.py
"$PYTHON" tests/v20r4-checks.py
node tests/sidewalk-test.cjs
node tests/counter-sw-test.cjs
node tests/update-flow-test.cjs
node tests/version-test.cjs
# Pipeline y puerta para IA (find/, OpenAPI, llms.txt, robots, JSON-LD). Si fallan, el script falla.
"$PYTHON" -m unittest discover -s pipeline/tests -t . > /tmp/kl-unittest.log 2>&1 || { tail -40 /tmp/kl-unittest.log; exit 1; }
tail -3 /tmp/kl-unittest.log
# Con el sitio ya generado (python3 -m pipeline build …): comprobaciones sobre los archivos reales y simulación de una IA.
if [ -f api/v1/openapi.json ] && [ -f llms-full.txt ]; then
  "$PYTHON" tests/ai-door-check.py
  "$PYTHON" tests/ai-sim.py . --n 10 --seed 1 | tail -1
  "$PYTHON" tests/ai-sim.py . --n 10 --seed 2 | tail -1
else
  echo "(omitido: ai-door-check y ai-sim necesitan el sitio generado: python3 -m pipeline build --strict --sources stolpersteine_de,wikidata_holocaust_victims,berlin_opendata,koeln_opendata)"
fi
# v19+: columnas DIBUJADAS fuera de los edificios de OSM (necesita playwright + Chrome; si no hay, se omite con aviso)
if [ -x "$CHROME" ] && "$PYTHON" -c "import playwright" 2>/dev/null; then
  PORT=${KL_HTTP_PORT:-8899}
  "$PYTHON" -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 & SRV=$!
  sleep 1
  "$PYTHON" tests/sidewalk-render-check.py http://127.0.0.1:${PORT}/ > /tmp/kl-sidewalk.log 2>&1 || { tail -15 /tmp/kl-sidewalk.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-sidewalk.log
  "$PYTHON" tests/sidewalk-render-check20.py http://127.0.0.1:${PORT}/ > /tmp/kl-sidewalk20.log 2>&1 || { tail -15 /tmp/kl-sidewalk20.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-sidewalk20.log
  "$PYTHON" tests/map2d-check.py http://127.0.0.1:${PORT}/ > /tmp/kl-map2d.log 2>&1 || { tail -15 /tmp/kl-map2d.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-map2d.log
  "$PYTHON" tests/map2d-mobile-check.py http://127.0.0.1:${PORT}/ > /tmp/kl-map2d-mobile.log 2>&1 || { tail -15 /tmp/kl-map2d-mobile.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-map2d-mobile.log
  # v21: las 72.110 placas de v20 deben dibujarse igual que en b142fa48; las nuevas, en su dla/dlo de archivo.
  V20_ROOT=${V20_CLIENT:-/workspace/countries-proto-v20r4}
  if [ -d "$V20_ROOT" ]; then
    V20PORT=${KL_HTTP_PORT_V20:-8970}
    "$PYTHON" -m http.server "$V20PORT" --bind 127.0.0.1 --directory "$V20_ROOT" >/dev/null 2>&1 & SRV20=$!
    sleep 1
    "$PYTHON" tests/v21-v20-render-compare.py http://127.0.0.1:${PORT}/ http://127.0.0.1:${V20PORT}/ > /tmp/kl-v20cmp.log 2>&1 || { tail -30 /tmp/kl-v20cmp.log; kill $SRV20; kill $SRV; exit 1; }
    tail -8 /tmp/kl-v20cmp.log
    SHAPELY_PP=""
    if ! "$PYTHON" -c "import shapely" 2>/dev/null && [ -d /workspace/venv-se/lib/python3.13/site-packages ]; then
      SHAPELY_PP="/workspace/venv-se/lib/python3.13/site-packages${PYTHONPATH:+:$PYTHONPATH}"
    fi
    PYTHONPATH="${SHAPELY_PP:-${PYTHONPATH:-}}" \
      V20_DATA="${V20_DATA:-/workspace/v21-data/place}" \
      V20_RENDERED_JSON="${V20_RENDERED_JSON:-/workspace/v21-data/out/v20-rendered-vis.json}" \
      "$PYTHON" tests/v21-new-render-placement.py http://127.0.0.1:${PORT}/ --v20-url http://127.0.0.1:${V20PORT}/ > /tmp/kl-v21place.log 2>&1 || { tail -40 /tmp/kl-v21place.log; kill $SRV20; kill $SRV; exit 1; }
    tail -12 /tmp/kl-v21place.log
    kill $SRV20
  else
    echo "(omitido: v21-v20-render-compare y v21-new-render-placement necesitan V20_CLIENT=$V20_ROOT)"
  fi
  # v22: las 73.950 placas de v21 deben dibujarse igual que en 990ddc10; las nuevas, en su dla/dlo de archivo.
  if [ -n "${V21_CLIENT:-}" ] && [ -d "$V21_CLIENT" ]; then
    V21PORT=${KL_HTTP_PORT_V21:-8971}
    "$PYTHON" -m http.server "$V21PORT" --bind 127.0.0.1 --directory "$V21_CLIENT" >/dev/null 2>&1 & SRV21=$!
    sleep 1
    "$PYTHON" tests/v22-render-compare.py http://127.0.0.1:${PORT}/ http://127.0.0.1:${V21PORT}/ > /tmp/kl-v22cmp.log 2>&1 || { tail -30 /tmp/kl-v22cmp.log; kill $SRV21; kill $SRV; exit 1; }
    tail -6 /tmp/kl-v22cmp.log
    kill $SRV21
  else
    echo "(omitido: tests/v22-render-compare.py necesita V21_CLIENT apuntando a un checkout limpio de 990ddc10)"
  fi
  # v22: holgura de columna, calzada, relación multipolygon y 1,55 m entre grupos en la posición DIBUJADA de Lote 1
  if { [ -n "${V22_NEAR_DIR:-}" ] && [ -d "$V22_NEAR_DIR" ]; } || { [ -n "${V22_DATA:-}" ] && [ -d "$V22_DATA/near" ]; }; then
    if "$PYTHON" -c "import shapely" 2>/dev/null; then
      "$PYTHON" tests/v22-new-render-placement.py http://127.0.0.1:${PORT}/ > /tmp/kl-v22place.log 2>&1 || { tail -40 /tmp/kl-v22place.log; kill $SRV; exit 1; }
      tail -6 /tmp/kl-v22place.log
    else
      echo "(omitido: tests/v22-new-render-placement.py necesita shapely)"
    fi
  else
    echo "(omitido: tests/v22-new-render-placement.py necesita V22_DATA o V22_NEAR_DIR con los pickles OSM)"
  fi
  "$PYTHON" tests/country-row-check.py http://127.0.0.1:${PORT}/ > /tmp/kl-row.log 2>&1 || { tail -15 /tmp/kl-row.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-row.log
  "$PYTHON" tests/disc-card-check.py http://127.0.0.1:${PORT}/ > /tmp/kl-disc.log 2>&1 || { tail -15 /tmp/kl-disc.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-disc.log
  "$PYTHON" tests/attribution-check.py http://127.0.0.1:${PORT}/ > /tmp/kl-attr.log 2>&1 || { tail -15 /tmp/kl-attr.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-attr.log
  "$PYTHON" tests/v23-ux-and-perf-check.py http://127.0.0.1:${PORT}/ > /tmp/kl-v23ux.log 2>&1 || { tail -20 /tmp/kl-v23ux.log; kill $SRV; exit 1; }
  tail -3 /tmp/kl-v23ux.log
  # encuadre de países (9 tamaños + 320x568; ~7 min). SKIP_COUNTRY_BUTTONS=1 lo omite en iteraciones rápidas.
  if [ -z "$SKIP_COUNTRY_BUTTONS" ]; then
    "$PYTHON" tests/country-buttons-check.py http://127.0.0.1:${PORT}/ > /tmp/kl-cb.log 2>&1 || { tail -25 /tmp/kl-cb.log; kill $SRV; exit 1; }
    tail -1 /tmp/kl-cb.log
  fi
  kill $SRV
else
  echo "(omitido: tests/sidewalk-render-check.py necesita playwright y Chrome)"
fi
# Navegador (opcional, necesita playwright y Chrome): sin JavaScript y WCAG con axe → tests/noscript-check.py y work-ia/axe*.py
echo "run-all: OK"
