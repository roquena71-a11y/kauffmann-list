# ESTADO v20r2 (arreglos tras la auditoría B de 7fd66d2)
Worktree: /workspace/countries-proto-v20r2 (rama v20r2, base 7fd66d2). NO tocar /workspace/countries-proto-v20 (lo usan A y C).
Datos de trabajo: V20_DATA=/workspace/v20-data-r2 (copia; near/pbf enlazados). Informe B: /workspace/audits/countries/v20-indep/B/auditoria-B.md
- [x] worktree + datos r2 creados; merge_v20.py ya no escribe en el directorio original.

## 07:25 código F1–F5 + menores en build/merge/common/inscription (sin reconstruir aún)
- F1 mnf (nº, calle) · F2 not_one_person + sujeto no humano + nombre de una palabra en WD · F3 pick_img + fetch_commons_exists.py (cache commons_exists20.json: 3995 existen / 33 no) · F4 names_compatible ≤15 m (build y merge) · F5 d solo si el año está en la inscripción · fixme de posición estricto (≤15 m o foto independiente) · wp genérico fuera · palabras de muerte NL/FR/CZ/IT/ES/PL/HU/SK/HR (58 unit tests OK)
- Siguiente: reconstruir todos los países (build_v20.py CC) y merge.
