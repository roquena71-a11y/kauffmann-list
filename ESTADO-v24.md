# ESTADO v24 — Step 1: contrast and brass plaque (no alignment yet)

- **Branch:** `v24` (from `2a6ceec7`, app v26; local only, not pushed)
- **Worktree:** `/workspace/kl-v24`
- **App / SW version:** `v27` (`tests/bump-version.py`, `kauffmann-v27-pages`)
- **Date:** 2026-11-23 (Europe/Berlin)
- **Scope:** Carlos approved three changes step by step. This file covers **step 1 only** (restored contrast + brass plaque). Sidewalk alignment is step 2 and is **not** started.
- **Commit:** `ef59222088d487691a3340cb5358c378f597cb28` (local only, not pushed; this line recorded in a follow-up commit)

## 1. What changed

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
   - The collapsed label `.sheet-lbl` was `#f0d48a` on the day panel `#f7f4ee` (contrast ~1.3:1). It is `#5c4310` in day mode (8.44:1, WCAG AA). Night keeps the gold label on `#0e1726`. This was not visible to the v23 axe test, which runs in the default night style. The winning rule is in `mapui.css` (loads after `style3d.css`): `html.js body:not(.dark) .sheet-handle .sheet-lbl`.
4. **Tests:** `tests/v24-plaque-contrast-check.py` (source GOLD/LIGHT, plaque layers and inset features with no text, day/night canvas contrast, overview GOLD stops, axe 0 in day street view, Berlin 16.5 shaft budget, 18.5 plaque budget, mobile heap). Hooked into `tests/run-all.sh` after `v23-ux-and-perf-check.py`.
5. **Version:** app / SW bumped to **v27**. `tests/version-test.cjs` OK (`versión única v27`, 11 `?v` in 3D, 3 in 2D, 36 hashes). `counter.js` is unchanged and still `enabled: true` (the preview’s disabled counter was not copied).

Data is unchanged (75,122 map stones, API 181,668 people). Alignment of groups to the sidewalk is explicitly out of scope for this step.

## 2. Performance (412×915, dpr 2, counters blocked)

From `tests/v24-plaque-contrast-check.py` (standalone re-run 2026-11-23 16:59 Europe/Berlin; earlier run was 61/397 ms, heap 220.6 MB — both inside budget):

| Metric | Budget | Measured (this step) |
|---|---:|---:|
| First street zoom 16.5 (`jumpTo` sync / first `stones` paint) | ≤ 250 / 2500 ms | **69 / 481 ms** (n=3) |
| Close zoom 18.5 (shafts + plaques painted) | ≤ 3500 ms | **5 / 33 ms** (n=9) |
| Mobile JS heap after street + close view | ≤ 512 MB | **206.2 MB** (total 274.8 MB) |
| Plaque features in a tight Berlin view | 1 groove MultiPolygon per shaft | 14 / 14 / 14 / 14 (shaft, rim, face, grooves) |

Day contrast sample: column gold `[187, 145, 60]` vs façade `[150, 145, 133]` (chroma 0.50 vs 0.07). Night: gold `[185, 143, 59]` vs building `[54, 59, 65]`. Axe 0 on day street view after the sheet-label CSS fix.

## 3. Screenshots (phone 412×915, dpr 2)

Required day shots:

- `/workspace/v24-data/shots/v24-westend-412x915.png` — Westendstraße 82 (4)
- `/workspace/v24-data/shots/v24-niedenau-412x915.png` — Niedenau 43 (5)
- `/workspace/v24-data/shots/v24-eschersheimer-412x915.png` — Eschersheimer Landstraße 39 (5)

Night / overview review (same worktree, not a second design):

- `/workspace/v24-data/shots/v24-westend-night-412x915.png`
- `/workspace/v24-data/shots/v24-niedenau-night-412x915.png`
- `/workspace/v24-data/shots/v24-overview-day-412x915.png`
- `/workspace/v24-data/shots/v24-overview-night-412x915.png`

## 4. Full `REQUIRE_OAV=1 tests/run-all.sh`

- Fresh venv: `/tmp/v24-ci-venv` (`tests/requirements-ci.txt` + Playwright + Shapely)
- Counters blocked with `bwrap` and `/workspace/v21-data/publish-hosts-block`
- No `SKIP_COUNTRY_BUTTONS`
- Correct env: `V20_CLIENT=/workspace/countries-proto-v20r4`, `V21_CLIENT=/workspace/kl-v21`, `V22_DATA=/workspace/v22-data`, **`V22_NEAR_DIR=/workspace/v22-data/near`** (must `env -u` any stale `V22_NEAR_DIR`; if set, it wins over `V22_DATA`). `V20_DATA=/workspace/v21-data/place`, `V20_RENDERED_JSON=/workspace/v21-data/out/v20-rendered-vis.json`
- Logs: `/workspace/v24-data/run-all.log` (third attempt, correct near dir); first two attempts failed looking for `/workspace/v21-data/near/DE-batch1.pkl`

### 4.1 Third full run (2026-11-23 16:44–16:53 Europe/Berlin), `RUN_ALL_EXIT:1`

Everything up to and including attribution passed:

- unittest / ai-door / ai-sim 20/20 seeds 1 and 2
- 2D map height + 41 pins outside buildings
- v21-v20-render-compare: 72,110 identical + 1,836 new pinned, 75,122 total
- v22-render-compare: **73,950 `moved=0` `ang_only=0`**, 1,172 Batch-1 **`pin_fail=0`**
- v22-new-render-placement: **0 violations**
- country-row, Hassall disc card axe 0, attribution axe 0 in 7 sizes
- `OK v23 UX: 412x915/360x780/1366x800 initial view (z=3.50), sheet collapse, compass, deferred 3D`

Then `tests/v23-ux-and-perf-check.py` `check_load_budget` failed:

`overlays 12769ms exceeded 11500ms 4G-2xCPU budget (v22 baseline ~18800ms)`

The suite stops at the first failure, so the hooked `v24-plaque-contrast-check.py` and `country-buttons-check.py` did not run inside that invocation.

### 4.2 Not a v24 regression (control on unchanged v26)

The 11,500 ms overlay budget is time-to-`kl-clu` at overview zoom, before columns/plaques mount (`add()` no-ops below z 12.5). Official-path rechecks (UX first, then load budget, same bwrap/hosts block):

| Tree | Official overlays |
|---|---:|
| v24 (this worktree) | 12769 (in run-all), 12208, 11716 |
| v26 `/workspace/kl-v23` at `2a6ceec7` (unchanged) | 13031, 11654 |

Historical official v26 on this project (auditor B ronda 3, 2026-11-22): `overview=5587 overlays=9811 vis=10084 street_zoom=90/542`.

Breakdown (t0 includes Playwright/Chrome launch; isolated, no prior UX): Chrome launch is fine (~500–800 ms); the extra ~2 s vs yesterday is in `pts` → `kl-clu` (buildStones / cluster FC under 2× CPU) on **both** trees (~6.1–6.9 s vs historical ~4.1–4.2 s). v24 is not slower than v26. The 11,500 ms budget was **not** raised in this step.

### 4.3 Tests run outside that full pass (same venv, counters blocked)

- `tests/v24-plaque-contrast-check.py` — **OK** (16:59 Europe/Berlin). Numbers in §2.
- `tests/country-buttons-check.py` — **OK**, `FALLOS: ninguno` (started 17:00:49, finished 17:20 Europe/Berlin; 10 sizes). Log: `/workspace/v24-data/plaque-and-country.log`.
- `tests/version-test.cjs` — **OK** versión única v27.

## 5. Not in this step

- Sidewalk / group alignment (step 2)
- Publish or `git push` (needs Carlos’s explicit yes)
- Raising the shared v23 11,500 ms overlay budget (machine is ~2 s slower today for v26 as well; recalibrate only as a follow-up if Carlos wants)
