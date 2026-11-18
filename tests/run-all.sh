#!/bin/sh
# Ejecuta todas las pruebas locales (no publica nada).
set -e
cd "$(dirname "$0")/.."
for f in source-links.js dedupe.js counter.js app3d.js people.js columns.js imagery.js sw.js; do node --check "$f"; done
node tests/source-links-test.mjs
node tests/dedupe-test.cjs
node tests/wd-added-test.cjs
node tests/counter-sw-test.cjs
python3 -m unittest discover -s pipeline/tests -t . 2>&1 | tail -3
