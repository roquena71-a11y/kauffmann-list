# Lista Kauffmann — Análisis de licencias, datos de personas fallecidas y uso por agentes de IA

> **BORRADOR — requiere revisión.** Análisis elaborado por un asistente de IA (APEX-LEGAL) para un responsable sin licencia profesional. No es asesoría jurídica. Fecha de verificación de fuentes: **2026-11-11**. Lo marcado [VERIFY] no pudo comprobarse en vivo.

## 0. Situación de partida (leída del repo)

- `data/stones.json`: 64.576 registros que **fusionan y deduplican** OSM y Wikidata (`src: "osm" | "wd"`), metadato `license: ODbL 1.0`. → Es una **Derivative Database** de OSM; correcto que sea ODbL en su conjunto (CC0 de Wikidata puede incorporarse a ODbL sin conflicto).
- `data/bio/*.json`: enlaces e inscripción estructurada por QID; `data/bio/text/`: extractos literales de Wikipedia (CC BY-SA 4.0) con título, `oldid`, página de autores y licencia.
- Fotos de Commons: solo enlazadas. Gedenkbuch/Arolsen/Yad Vashem/USHMM: solo enlaces.

## 1. Licencias

### 1.1 Fuentes verificadas

| Fuente | Licencia | Verificación |
|---|---|---|
| OSM | ODbL 1.0 — Derivative Database (§1), Produced Work (§1, §4.3 aviso), share-alike (§4.4), Collective Database (§4.5), oferta de la base en forma legible por máquina (§4.6) | https://opendatacommons.org/licenses/odbl/1-0/ (2026-11-11) |
| OSMF — Produced Work | Test: ¿la salida está pensada para extraer los datos? Si sí → base de datos; si no → Produced Work. Los dumps no son Produced Work. | https://osmfoundation.org/wiki/Licence/Community_Guidelines/Produced_Work_-_Guideline (2026-11-11) |
| OSMF — Collective Database | Sin share-alike si cada tipo de dato/propiedad es 100 % OSM o 100 % no-OSM; las referencias (claves de join) cuentan; fusionar+deduplicar datos ajenos con OSM puede arrastrarlos a ODbL | https://osmfoundation.org/wiki/Licence/Community_Guidelines/Collective_Database_Guideline_Guideline (2026-11-11) |
| OSMF — Atribución | "© OpenStreetMap" / enlace a openstreetmap.org/copyright, visible sin interacción | https://osmfoundation.org/wiki/Licence/Attribution_Guidelines (2026-11-11) |
| Wikidata | CC0 (espacio principal) | https://www.wikidata.org/wiki/Wikidata:Licensing (2026-11-11) |
| Wikipedia | CC BY-SA 4.0 | https://creativecommons.org/licenses/by-sa/4.0/ (ya citado en LICENCIAS.md; [VERIFY] compatibilidad unidireccional CC BY-SA ↔ ODbL: no existe declaración de compatibilidad conocida) |

### 1.2 Qué licencia lleva cada archivo (regla)

| Archivo / salida | Naturaleza ODbL | Licencia |
|---|---|---|
| `data/stones.json` y cualquier JSON por apellido/lugar derivado de él (`api/v1/...`) | **Derivative Database** (está hecho para extraer datos) | **ODbL 1.0** + atribución OSM + mención Wikidata CC0 |
| Registros solo-Wikidata publicados aparte (sin coordenadas/IDs de OSM) | No derivan de OSM | CC0 (puede declararse ODbL por simplicidad) |
| `data/bio/text/*` (extractos Wikipedia) | Contenido, no base OSM | **CC BY-SA 4.0**, con autoría y `oldid` por registro. **No incrustar** en archivos ODbL: ponerlo en archivos separados o, si se incrusta, cada campo debe llevar su licencia y el archivo declarar licencia mixta [VERIFY] |
| Mapa renderizado, PDF, capturas | **Produced Work** | Aviso ODbL (§4.3) + oferta de la base (§4.6) → enlazar a `stones.json` |
| Datos de fase 2 (Yad Vashem, Arolsen, USHMM, Bundesarchiv) | Ajenos a OSM | **La licencia que otorgue cada institución** (probablemente no abierta). Archivos separados por fuente |
| `openapi.json`, `llms.txt` | Documentación | CC BY 4.0 o CC0 (a elección) |

### 1.3 Riesgo clave de share-alike en la fase 2

Si los datos de una institución se **fusionan en el mismo registro** que un Stolperstein de OSM (match por nombre+lugar y deduplicación), el resultado podría ser una Derivative Database y el share-alike exigiría publicarlo bajo ODbL — algo que la institución casi seguro no autoriza. **Medida:** archivos separados por fuente, clave propia de la institución + QID de Wikidata; el cruce con OSM se hace **en el navegador** (visualización = Produced Work) o mediante tabla de enlaces mínima. [VERIFY — abogado de PI/licencias abiertas, o consulta a la OSMF Licensing Working Group].

## 2. Datos de personas fallecidas

| Norma | Contenido | Fuente (2026-11-11) |
|---|---|---|
| RGPD, considerando 27 | El Reglamento no se aplica a datos de fallecidos; los Estados miembros pueden regular | https://gdpr-info.eu/recitals/no-27/ |
| Derecho post-mortem de la personalidad (DE) | Base en Art. 1 (1) GG; *Mephisto* (BVerfGE 30, 173); protección se desvanece con el recuerdo (*Emil Nolde*, BGH 1989); componente patrimonial 10 años (BGH I ZR 277/03); legitimados: familiares cercanos; remedio: cesación (Unterlassung), no indemnización | https://de.wikipedia.org/wiki/Postmortales_Persönlichkeitsrecht (fuente secundaria — [VERIFY] con las sentencias) |
| § 189 StGB | Ultraje a la memoria de un difunto: hasta 2 años o multa | https://www.gesetze-im-internet.de/stgb/__189.html |
| § 22 KUG | Imágenes: consentimiento de familiares hasta 10 años tras la muerte | https://www.gesetze-im-internet.de/kunsturhg/__22.html |
| Arolsen, Rules for Data Processing (1-12-2025), párr. (10) | Para Arolsen, la información de fallecidos no es dato personal; si no consta el año de muerte, se presume fallecida 60 años después del documento | https://arolsen-archives.org/aroa/documents/data-processing-rules_de-en-fr_2025-12-01.pdf |

**Conclusión:** para víctimas asesinadas el RGPD no aplica; el riesgo jurídico real es bajo y se concentra en (i) **supervivientes posiblemente vivos**, (ii) **familiares vivos** mencionados en textos o identificables (el RGPD sí les aplica, incl. Art. 9 si se revela origen/religión), (iii) errores que afecten a la dignidad (p. ej., confundir víctima y perpetrador), (iv) uso indebido por terceros (listas de "judíos" para fines antisemitas). [VERIFY — si Alemania/Hamburgo tienen norma específica para fallecidos; no se encontró en el BDSG].

### Matriz de riesgos

| # | Riesgo | Prob. | Grav. | Medida |
|---|---|---|---|---|
| R1 | Publicar a un superviviente vivo (p. ej. niño de Kindertransport nacido ≥1916) con datos de origen/religión (Art. 9 RGPD) | Media | Alta | Regla 4–5 |
| R2 | Mencionar a descendientes vivos por nombre (textos Wikipedia, biografías) | Media | Media | Regla 6 |
| R3 | Share-alike ODbL contamina datos de socios → incumplimiento con socio | Media (fase 2) | Alta | Regla 2–3 |
| R4 | Falta de atribución/aviso §4.3/§4.6 o licencia errónea en JSON | Media | Media | Regla 1, 7 |
| R5 | Error de identidad/dato falso → reclamación de familiares (Unterlassung, § 189 StGB solo si hay ultraje) | Baja | Media | Regla 8–9 |
| R6 | Reutilización masiva por IA/scrapers con fines de odio o sin atribución | Media | Media | Regla 10–11 |
| R7 | Impresum/obligaciones de identificación (§ 5 DDG solo para servicios "geschäftsmäßige, in der Regel gegen Entgelt" — https://www.gesetze-im-internet.de/ddg/__5.html; § 18 MStV para contenidos periodístico-editoriales [VERIFY]) choca con el anonimato del dueño | Media | Baja-Media | Pregunta al abogado |
| R8 | Copiar datos de Yad Vashem/USHMM/Arolsen/Gedenkbuch sin permiso (fase 1) | Baja si solo enlaces | Alta | Regla 12 |

## 3. Términos para agentes de IA (llms.txt / terms)

- `llms.txt` **no tiene valor jurídico propio**; la reserva TDM válida en Alemania debe ser **legible por máquina** (§ 44b (3) UrhG — https://www.gesetze-im-internet.de/urhg/__44b.html). Como el objetivo es *permitir* el uso, no hace falta reserva para los datos ODbL/CC0; pero ODbL y CC BY-SA **siguen obligando** a quien redistribuya.
- Texto propuesto (borrador) para `llms.txt` y `/terms`:
  1. "Datos de `api/v1/stones*`: ODbL 1.0, © OpenStreetMap contributors + Wikidata (CC0). Si redistribuyes la base o un extracto sustancial, debe seguir bajo ODbL."
  2. "Extractos `bio/text`: CC BY-SA 4.0; cita artículo, `oldid` y autores."
  3. "Datos de [institución]: licencia propia [ver campo `license`]; no reutilizar fuera de lo que esa licencia permita" (fase 2).
  4. "Cita siempre: 'Lista Kauffmann' + enlace a la ficha + fuente original. No presentes inferencias como hechos; los datos pueden contener errores; remite a la fuente primaria."
  5. "Prohibido usar estos datos para acosar, elaborar listas de descendientes, perfiles étnico-religiosos de personas vivas, negacionismo o fines antisemitas." (cláusula contractual de buena fe; su exigibilidad frente a ODbL es dudosa [VERIFY]).
  6. "Correcciones/retirada: [canal]."

## 4. Reglas que el código debe aplicar

1. Cada JSON publicado lleva `meta.license`, `meta.attribution`, `meta.source_url` y `meta.generated`; los de `stones` → ODbL.
2. Datos de cada institución (fase 2) en **archivos y prefijos separados** (`api/v1/yv/…`), con su propia `license`; nunca fusionados/deduplicados con registros OSM en un mismo objeto.
3. Clave de cruce: QID de Wikidata o ID de la institución; el join con OSM, solo en cliente.
4. Exclusión/minimización de posibles vivos: si no hay fecha o indicio de muerte (`ERMORDET`, `TOT`, `deceased`, fecha de muerte) **y** nacimiento ≥ (año actual − 110) o desconocido → no publicar en la API; en el mapa, solo lo que figura en la placa física.
5. Inscripciones con `ÜBERLEBT`, `FLUCHT`, `BEFREIT`, `ENTKAM` y nacimiento ≥1916: sin extractos biográficos ni enlaces a fichas de registro de supervivientes.
6. No publicar nombres de terceros (hijos, nietos) fuera de la inscripción; filtrar en extractos Wikipedia o publicar solo el enlace.
7. Página de mapa y PDFs: aviso ODbL visible + enlace a la base descargable (§4.3/§4.6).
8. Botón "Corregir / retirar" por ficha; lista `suppressed.json` (solo IDs) aplicada en el build; plazo de respuesta objetivo ≤ 14 días [VERIFY].
9. Cada dato con su fuente y fecha de snapshot; nunca "generar" ni completar campos por inferencia.
10. Sin cookies/analítica (ya cumple); `robots.txt` y `llms.txt` coherentes.
11. No exponer búsquedas inversas por "origen/religión" de personas vivas; la API solo indexa por apellido/lugar de víctimas.
12. Fase 1: de Yad Vashem/Arolsen/USHMM/Gedenkbuch **solo enlaces** (sin copiar campos ni descargar CSV) hasta tener permiso escrito.

## 5. Preguntas para un abogado

1. ¿JSON por apellido/lugar = Derivative Database (ODbL) en todos los casos? ¿Basta la oferta §4.6 con enlazar `stones.json`?
2. ¿El esquema "archivos separados + join en cliente" evita el share-alike para datos de socios?
3. ¿Cómo combinar legalmente un campo CC BY-SA dentro de un archivo ODbL?
4. ¿Existe en Alemania (o Hamburgo) regulación de datos de fallecidos al amparo del considerando 27?
5. ¿Qué umbral de edad/indicio es razonable para presumir fallecimiento; vale el criterio de 110 años?
6. ¿Necesita el sitio Impressum (§ 5 DDG / § 18 MStV) siendo gratuito y no comercial? ¿Puede usarse una dirección de servicio?
7. ¿Es exigible una cláusula de "usos prohibidos" sobre datos ODbL?
8. ¿Riesgo de responsabilidad por usos de terceros (IA) de la API?

## 6. No verificado

- Términos de uso de Yad Vashem: la web devolvió HTTP 403 a la consulta automatizada (https://www.yadvashem.org/terms-and-conditions.html). [VERIFY — leer manualmente].
- Wording exacto de § 18 MStV. [VERIFY — abogado de medios].
- Sentencias de derecho post-mortem citadas vía Wikipedia (fuente secundaria).
