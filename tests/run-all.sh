#!/bin/sh
# Ejecuta todas las pruebas locales (no publica nada).
set -e
cd "$(dirname "$0")/.."
for f in source-links.js dedupe.js counter.js app3d.js people.js columns.js imagery.js mapui.js sw.js; do node --check "$f"; done
node tests/source-links-test.mjs
node tests/dedupe-test.cjs
node tests/wd-added-test.cjs
node tests/ie-added-test.cjs
node tests/se-added-test.cjs
node tests/jefiro-added-test.cjs
node tests/sidewalk-test.cjs
node tests/counter-sw-test.cjs
node tests/update-flow-test.cjs
node tests/version-test.cjs
# Pipeline y puerta para IA (find/, OpenAPI, llms.txt, robots, JSON-LD). Si fallan, el script falla.
python3 -m unittest discover -s pipeline/tests -t . > /tmp/kl-unittest.log 2>&1 || { tail -40 /tmp/kl-unittest.log; exit 1; }
tail -3 /tmp/kl-unittest.log
# Con el sitio ya generado (python3 -m pipeline build …): comprobaciones sobre los archivos reales y simulación de una IA.
if [ -f api/v1/openapi.json ] && [ -f llms-full.txt ]; then
  python3 tests/ai-door-check.py
  python3 tests/ai-sim.py . --n 10 --seed 1 | tail -1
  python3 tests/ai-sim.py . --n 10 --seed 2 | tail -1
else
  echo "(omitido: ai-door-check y ai-sim necesitan el sitio generado: python3 -m pipeline build --strict --sources stolpersteine_de,wikidata_holocaust_victims)"
fi
# v19: columnas DIBUJADAS fuera de los edificios de OSM (necesita playwright + Chrome; si no hay, se omite con aviso)
if [ -x /usr/bin/google-chrome ] && /usr/bin/python3 -c "import playwright" 2>/dev/null; then
  python3 -m http.server 8899 --bind 127.0.0.1 >/dev/null 2>&1 & SRV=$!
  sleep 1
  /usr/bin/python3 tests/sidewalk-render-check.py http://127.0.0.1:8899/ > /tmp/kl-sidewalk.log 2>&1 || { tail -15 /tmp/kl-sidewalk.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-sidewalk.log
  /usr/bin/python3 tests/map2d-check.py http://127.0.0.1:8899/ > /tmp/kl-map2d.log 2>&1 || { tail -15 /tmp/kl-map2d.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-map2d.log
  /usr/bin/python3 tests/country-row-check.py http://127.0.0.1:8899/ > /tmp/kl-row.log 2>&1 || { tail -15 /tmp/kl-row.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-row.log
  /usr/bin/python3 tests/disc-card-check.py http://127.0.0.1:8899/ > /tmp/kl-disc.log 2>&1 || { tail -15 /tmp/kl-disc.log; kill $SRV; exit 1; }
  tail -1 /tmp/kl-disc.log
  kill $SRV
else
  echo "(omitido: tests/sidewalk-render-check.py necesita playwright y Chrome)"
fi
# Navegador (opcional, necesita playwright y Chrome): sin JavaScript y WCAG con axe → tests/noscript-check.py y work-ia/axe*.py
echo "run-all: OK"
