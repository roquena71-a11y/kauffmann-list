# ESTADO v37-auditoria

- Rama `v37-auditoria` desde `origin/main` = `a1df42b7` (v36 en vivo). Worktree ligero: `/workspace/kl-v37-auditoria` (objetos compartidos con `/workspace/countries-proto-v20/.git`).
- Encargo (Carlos, 26-11-2026 16:43 CET): auditoría externa `/workspace/audits-kl/AUDITORIA-kauffmann-list.md` (escrita contra v30), ítems A2, M4, A3, M1, M5; subir a v37. Sin push, sin publicar, sin tocar el contador, sin cambiar datos de placas ni la/lo, sin regenerar api/ salvo lo imprescindible.

## 1 · Licencia de Den Haag (A2) — comprobado 26-11-2026 16:44–16:50 CET

Fuentes oficiales:
- https://data.overheid.nl/dataset/stolpersteine (ficha nacional): «Licentie» del conjunto = **CC-0 (1.0)**; pero las **5 distribuciones** (CSV, JSON, RDF/XML, Turtle, XLSX) dicen **CC-BY (4.0)**.
- CKAN de la misma ficha: https://data.overheid.nl/data/api/3/action/package_show?id=stolpersteine → `license_id` http://creativecommons.org/publicdomain/zero/1.0/deed.nl; cada `resources[].license_id` = http://creativecommons.org/licenses/by/4.0/deed.nl (las descargas apuntan a `https://den-haag-opendata.opendatasoft.com/api/explore/v2.1/catalog/datasets/stolpersteine/exports/{csv,json,rdfxml,turtle,xlsx}`).
- Portal municipal (OpenDataSoft) https://den-haag-opendata.opendatasoft.com/api/explore/v2.1/catalog/datasets/stolpersteine → `metas.default.license` = null; `metas.donl.dct_license` = «CC0 1.0» (metadato que se envía a data.overheid.nl).

Conclusión: la fuente oficial es **contradictoria** (conjunto CC0 1.0, descargas CC BY 4.0). Nuestros datos vienen de una descarga, y la familia `cc-by-4` (atribución a Gemeente Den Haag) cumple las dos lecturas; pasar a CC0 no sería seguro. Se mantiene **CC BY 4.0** (como ya decían `pipeline/sources/denhaag_opendata.json`, `families.json`, `LICENCIAS.md`, la API y el pie de `2d/`). El error real era solo `llms.txt` (línea Licences), que metía `data/denhaag-added-*.json` bajo CC0. Pendiente para Carlos: si quiere, preguntar a datashop@denhaag.nl cuál vale.

## Registro
