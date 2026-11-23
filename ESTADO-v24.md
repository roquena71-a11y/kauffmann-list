# ESTADO v24 — Step 1: contrast and brass plaque (no alignment yet)

- **Branch:** `v24` (from `2a6ceec7`, app v26; local only, not pushed)
- **Worktree:** `/workspace/kl-v24`
- **App / SW version:** `v28` (`tests/bump-version.py`, `kauffmann-v28-pages`) after the F1 fix. The audited step-1 code was v27 at `ef592220`.
- **Date:** 2026-11-23 (Europe/Berlin)
- **Scope:** Carlos approved three changes step by step. This file covers **step 1 only** (restored contrast + brass plaque, plus the F1 groove-sync fix). Sidewalk alignment is step 2 and is **not** started.
- **Commits:** `ef592220` (v27 step 1), `b6dc0077` (ESTADO hash note), and the v28 F1 fix (hash filled after that commit). Local only, not pushed.

## 1. What changed (step 1, v27)

1. **Restored column contrast (`app3d.js`):**
   - Lighting restored to commit `9025a3c0`: `setLight({anchor:'map', position:[1.4, 210, 35], color:'#fff1d0', intensity:0.5})`. The v26 light from `d1df0526` (`polar 62°`, `intensity 0.62`) was more lateral and flattened the top face against beige day buildings (`#e7e0d2`).
   - GOLD interpolate keeps the historical z5/z12 stops (`#c6a15b`, `#e0bc62`) so overview zoom is unchanged, and uses street-level `#e0b020` instead of washed-out `#f0d48a` (same choice as the approved plaque-preview `b49fed79`).
   - The same light is used in day and night. Night review shots show a warm gold shaft and a readable cap against dark slate buildings.
   - Harmless `?base=day|night|…` query so tests and screenshots can force a style without touching `localStorage`.
2. **Brass plaque on every column (`columns.js`):**
   - Production port of the approved mockup: inset rim (`half 0.51 m`, `16.00–16.26 m`, `#7a5720`) and face (`half 0.43 m`, `16.16–16.42 m`, `#d6b25a`), plus four blank grooves (`#5a3f16`, `16.30–16.345 m`). No names or invented inscription text.
   - Shaft geometry, `_dla` / `_dlo` / `_ang`, and the existing spatial index are unchanged (render-compare `moved=0`, `pin_fail=0`).
   - Performance: plaques use a tight ~300–400 m viewport box (not the multi-kilometre shaft preload); `minzoom` 16.2 for the plate, 17.8 for grooves; grooves are **one MultiPolygon per stone**. `add()` still no-ops below zoom 12.5, so plaques are not on the overview `kl-clu` path.
3. **Day-mode collapsed sheet contrast (`mapui.css`, `style3d.css`):**
   - The collapsed label `.sheet-lbl` was `#f0d48a` on the day panel `#f7f4ee` (contrast ~1.3:1). It is `#5c4310` in day mode (8.44:1, WCAG AA). Night keeps the gold label on `#0e1726`. The winning rule is in `mapui.css` (loads after `style3d.css`): `html.js body:not(.dark) .sheet-handle .sheet-lbl`.
4. **Tests:** `tests/v24-plaque-contrast-check.py` (source GOLD/LIGHT, plaque layers and inset features with no text, day/night canvas contrast, overview GOLD stops, axe 0 in day street view, Berlin 16.5 shaft budget, 18.5 plaque budget, mobile heap, and — after F1 — pan-then-zoom groove sync). Hooked into `tests/run-all.sh` after `v23-ux-and-perf-check.py`.
5. **Version:** originally bumped to **v27**; after F1, **v28**.

Data is unchanged (75,122 map stones, API 181,668 people). Alignment of groups to the sidewalk is explicitly out of scope for this step.

## 2. Performance (412×915, dpr 2, counters blocked)

Official `tests/v24-plaque-contrast-check.py` after the F1 fix (2026-11-23 18:12 Europe/Berlin):

| Metric | Budget | Measured (v28, after F1) |
|---|---:|---:|
| First street zoom 16.5 (`jumpTo` sync / first `stones` paint) | ≤ 250 / 2500 ms | **49 / 406 ms** (n=3) |
| Close zoom 18.5 (shafts + plaques painted) | ≤ 3500 ms | **1 / 21 ms** (n=9) |
| Mobile JS heap after street + close view | ≤ 512 MB | **193.6 MB** (total 272.9 MB) |
| Plaque features in a tight Berlin view | 1 groove MultiPolygon per shaft | 14 / 14 / 14 / 14 (shaft, rim, face, grooves) |
| F1 pan 16.5 then zoom 18.2 | srcGr = srcRim; painted grooves = faces | pan **90/90**; z18.2 **nFace/nGr = 7/7** |

Day contrast sample: column gold `[187, 145, 60]` vs façade `[150, 145, 133]` (chroma 0.50 vs 0.07). Night: gold `[185, 143, 59]` vs building `[54, 59, 65]`. Axe 0 on day street view.

## 3. Screenshots (phone 412×915, dpr 2)

Required day shots (taken for v27; F1 does not change the Westend/Niedenau/Eschersheimer framing or contrast):

- `/workspace/v24-data/shots/v24-westend-412x915.png` — Westendstraße 82 (4)
- `/workspace/v24-data/shots/v24-niedenau-412x915.png` — Niedenau 43 (5)
- `/workspace/v24-data/shots/v24-eschersheimer-412x915.png` — Eschersheimer Landstraße 39 (5)

Night / overview review:

- `/workspace/v24-data/shots/v24-westend-night-412x915.png`
- `/workspace/v24-data/shots/v24-niedenau-night-412x915.png`
- `/workspace/v24-data/shots/v24-overview-day-412x915.png`
- `/workspace/v24-data/shots/v24-overview-night-412x915.png`

## 4. Full `REQUIRE_OAV=1 tests/run-all.sh` on v27 (`ef592220`)

- Fresh venv at the time: `/tmp/v24-ci-venv`
- Counters blocked with `bwrap` and `/workspace/v21-data/publish-hosts-block`
- No `SKIP_COUNTRY_BUTTONS`; `V22_NEAR_DIR=/workspace/v22-data/near`
- Log: `/workspace/v24-data/run-all.log` — **`RUN_ALL_EXIT:1`** at `check_load_budget` (`overlays 12769ms` > 11500). Everything through `OK v23 UX`, render-compare **73,950 `moved=0`**, 1,172 **`pin_fail=0`**, placement **0 violations** had passed. Plaque test and `country-buttons-check.py` (`FALLOS: ninguno`) were run separately and passed.
- The 11,500 ms overlay budget was **not** raised. Auditor B independently confirmed v27 is not slower than v26 on overlays; both missed 11,500 ms while audits ran in parallel (v26 median 13,858; v27 median 12,819; historical official v26 on 2026-11-22 was 9,811 ms).

## 5. Not in this step

- Sidewalk / group alignment (step 2)
- Publish or `git push` (needs Carlos’s explicit yes)
- Raising the shared v23 11,500 ms overlay budget

## 6. Round 1 audits and F1 fix (v28)

- Audits of `ef592220` (app v27): **A PASS**, **C PASS**, **B FAIL** (`/workspace/audits/v24/B/auditoria-B-ronda1.md`).
- **F1 (MEDIUM):** after a pan at zoom 16.5 then zoom to 18.2, rim/face `setData` ran but `col-placa-grooves` stayed stale. `ensureCols` only called `setData` on grooves when `z >= GROOVE_MINZOOM - 0.4` (17.4); a later zoom-in short-circuited because `plaquesOk` was already true. Auditor probe: pan east at 16.5 updated `srcRim` 106 → 90, `srcGr` stayed 106; at 18.2, 7 faces and **0 grooves**.
- **Fix** (`columns.js`): rim, face and grooves always share the same tight box (`setPlaqueSources` / `setGrooveSource`, including below `GROOVE_MINZOOM` — the layer itself stays unpainted until 17.8). `loadedGrooveBox` is tracked separately; `ensureCols` does not return early unless grooves are also fresh, so a zoom-in after a street-level pan still refreshes them. Same path after rotate (`moveend`).
- **Test:** `tests/v24-plaque-contrast-check.py` now walks exactly that sequence (Berlin 16.5 → pan to 13.455,52.517 at 16.5 → zoom 18.2 → rotate 40°). On the unfixed tree (same `columns.js` as `ef592220`) the isolated probe **failed**: `srcRim=90`, `srcGr=106`. After the fix it **passed**: pan **90/90**, z18.2 **nFace/nGr=7/7**. The official test also passed (numbers in §2).
- **Version:** bumped to **v28** so phones pick up `columns.js`.
- Load budget still **not** raised.
- Full `REQUIRE_OAV=1 tests/run-all.sh` after the fix: **`run-all: OK`**, `RUN_ALL_EXIT:0`.
  - Fresh venv `/tmp/v24-r2-ci-venv` (`tests/requirements-ci.txt` + Playwright 1.65.2 + Shapely 2.2.0). Counters blocked with `bwrap` and `/workspace/v21-data/publish-hosts-block`. No `SKIP_COUNTRY_BUTTONS`. `V22_NEAR_DIR=/workspace/v22-data/near`.
  - Box at start (18:13:04 Europe/Berlin): no other browser tests, our ports free, load average **0.89 / 1.86 / 3.35**, ~12 GiB available. End (18:42:44): load **6.54 / 6.14 / 5.48** (the suite’s own Chrome, especially country-buttons).
  - Log: `/workspace/v24-data/run-all-r2.log`.
  - Highlights: versión única **v28**; unittest **68 OK**; `ai-door` 0; `ai-sim` seeds 1 and 2 20/20; render-compare **73,950 `moved=0` `ang_only=0`**, 1,172 **`pin_fail=0`**; placement **0 violations**; `OK v23 UX` (z=3.50); **load budget passed**: `fcp=204ms dcl=1164ms overview=5914ms overlays=11446ms vis=11786ms street_zoom=102ms/764ms` (11,500 ms threshold **not** raised; 11,446 is inside it). Plaque test **OK** including F1 (`pan srcRim/srcGr=90/90`, `z18.2 nFace/nGr=7/7`; street 50/440 ms, close 1/21 ms, heap 191.4 MB). `country-buttons-check.py` **`FALLOS: ninguno`**.
  - Because the official overlay budget passed on this idle run, v26 was not re-measured here. Earlier misses (constructor and auditor B) happened while other work/audits were loading the box; this run shows the 11,500 ms bar is still reachable without changing the threshold.
