# ESTADO v23 — Mobile UX, Compass, Initial Framing & Load-Time Fix

- **Branch:** `v23` (from `b45fcb95`, v22; local only, not pushed)
- **Worktree:** `/workspace/kl-v23`
- **App / SW version:** `v24` (`tests/bump-version.py`, `kauffmann-v24-pages`)
- **Date:** 2026-11-22

## 1. Measured Load-Time Root Cause (Issue 3)

Profiled on `b45fcb95` (`v22`) in Playwright Chromium mobile emulation (`412×915`, `dpr=2`, gzip HTTP, `kl-contador` and `*.workers.dev` blocked):

1. **`clusterByDist(noAddr, 3.5)` in `app3d.js` (O(N²) bottleneck):** `6,935` stones without street addresses ran an unindexed double loop (~24M `distM` calls), blocking the main thread for **`1,831 ms` unthrottled** (~4–5 s on mobile CPU).
2. **`buildStones()` total (`3,023 ms` unthrottled on v22):**
   - `addrKey(s)` recomputed 7 regex replacements ~250k times; `neighbors()` created ~1.45M `'street|x:y'` string keys; `vis.sort` called `localeCompare(..., 'de')` uncached across 28,929 groups.
   - Ran the 16-iteration 75k-stone collision grid pass even when `META.layout_pinned === true` (all 72,110 base stones pinned).
   - Allocated `74,979` unused `STONES_FC` polygon features even when `KLCols` replaces `'stones'`.
   - Built `ensureSearchIndex()` (`75,122` `_t`/`_c` token arrays + `1,978` `#cities` `<option>` DOM nodes) synchronously before `kl:data`.
3. **`KLCols.add()` in `columns.js`:** Eagerly built `74,979 × 38`-vertex rounded-square polygons (~2.85M coordinates) and uploaded them to MapLibre's worker at startup (`zoom ~2.1`), even though `'stones'` has `minzoom: 14.6` (invisible at overview zoom). Combined with `buildStones()`, this caused ~`6.6–7.1 s` unthrottled / ~`11.7 s` throttled main-thread lockup before overlays rendered.
4. **Serial data waterfall & SW slow-network timeout:** All 15 `*-added-*.json` files (~160 KB gz) were fetched serially *after* `data/stones.json` (~5.59 MB gz / 26.0 MB raw) downloaded and parsed, and `sw.js` `SLOW_MS` waited `4,500 ms` before falling back to cache on slow repeat visits.

### Before vs. After Timings (`412×915`, cached gzip, counters blocked)

| Profile | v22 (`b45fcb95`) `vis` / `overlays` | v23 (`v24`) `vis` / `overlays` | First Paint / FCP |
|---|---:|---:|---:|
| Local gzip unthrottled | `7,384 ms` / `7,441 ms` | `3,130 ms` / `3,496 ms` | `80 ms` |
| Mobile 4G `20 Mbps`, `50 ms` RTT, `2× CPU` | `18,594 ms` / `18,803 ms` | `8,326–8,874 ms` / `9,061–9,683 ms` (`dcl 919–987 ms`) | `220–308 ms` |
| Mobile 4G `10 Mbps`, `60 ms` RTT, `3× CPU` | `29,333 ms` / `29,533 ms` | `13,726 ms` / `14,728 ms` | `248 ms` |

## 2. All 4 Fixes Implemented

1. **Bottom sheet collapse (`index.html`, `mapui.js`, `mapui.css`):**
   - Added `'collapsed'` (`46 px`) state on portrait mobile displaying the drag handle pill + localized label (`Buscar · Países` / `Suche · Länder` / `Search · Countries`), hiding search/countries/results until expanded.
   - `#sheetHandle` tap toggles `collapsed <-> peek` (or `half` when search/detail is active); pointer/touch drag resizes smoothly down to `46 px` and snaps across `collapsed / peek / half / full`; keyboard `ArrowUp`/`ArrowDown`/`Escape` work across all states; tapping empty map lowers `half`/`full` to `peek` without re-opening `collapsed`.
   - Accessible name when collapsed includes `T('sheetCollapsed')` (`Buscar · Países — Mostrar la lista`) to satisfy WCAG 2.5.3 (`label-content-name-mismatch`).
2. **Compact square gold compass (`columns.js`, `style3d.css`, `app3d.js`):**
   - Replaced the 3-button `⟲ N ⟳` cluster (`#rotBtns`) with a single `36×36 px` square gold compass (`#rotNorth`) featuring a rotating inline SVG needle + `N`.
   - Hidden when `|bearing| < 1°` (initial `bearing: 0°`); appears bottom-left when rotated with localized `aria-label` including angle (`Mirar al norte (35°)`), resets north on tap/keyboard, WCAG 2.2 AA (`>= 24×24 px` target, axe 0).
3. **Load-time optimization (`index.html`, `app3d.js`, `columns.js`, `sw.js`):**
   - Early `fetch('data/stones.json')` in `<head>` (without parsing JSON before `DOMContentLoaded` or saturating connection pool with 15 small files ahead of `maplibre-gl.js` and style); parallel `Promise.all` fetch of `stones.json` + 15 added JSONs in `load()`.
   - Spatial-grid `clusterByDist` for `n > 40`, cached `addrKey` (`s._ak`), `Intl.Collator('de')`, 2-level `near` lookup map, skipped 16-iter collision pass when all groups are pinned, skipped unused `STONES_FC` when `KLCols` is present, added `map.getStyle()` guard in `tryAddOverlays()`.
   - Deferred `ensureSearchIndex()` (`60 ms` post-overlays + lazy on focus/search/vigil) and deferred `KLCols.add()` 3D column polygon generation until `zoom >= 12.5` (or `?modelos=` / selection), mounting automatically on zoom/move/select.
   - Lowered `sw.js` `SLOW_MS` from `4500` to `1800` and protected `*-added-*.json` in `trim()`.
4. **Closer initial view (`mapui.js`, `app3d.js`):**
   - Replaced world-wide `dataBounds()` framing (`zoom ~2.13`, `bearing -8°`) with `HOME_BOUNDS = [[-6.4, 45.2], [17.5, 55.6]]` and `homePadding()` (`zoom 3.50` on `412×915`, `bearing 0°`), framing Western/Central Europe while keeping Dublin, Hamburg, and Berlin visible.

## 3. Verification (Zero Skips, Counters Blocked via `bwrap`)

- **Rendered invariance:**
  - Direct comparison vs `b45fcb95` (`v22`): `75,122 / 75,122` stones (`VISIBLE = 74,979`, `0` diffs in `_dla`, `_dlo`, `_ang`, `_aliasOf`).
  - `tests/v22-render-compare.py` vs `990ddc10`: `73,950` existing `moved=0 ang_only=0`, `1,172` Batch-1 pinned `pin_fail=0`.
  - `tests/v21-v20-render-compare.py` vs `b142fa48`: `72,110` v20 stones identical + `1,836` v21 visible pinned.
- **Full `REQUIRE_OAV=1 tests/run-all.sh` (no skips):**
  - `node --check`, all JS data/dedupe/sidewalk/counter/update-flow/version (`v24`) tests: **OK**.
  - `pipeline/tests` (`68 tests`): **OK**.
  - `REQUIRE_OAV=1 ai-door-check.py` (`openapi-spec-validator: válido`, `4,519` find files, `733,929` rows, `9,354` permalinks): **0 errors**.
  - `ai-sim.py` (seeds 1 & 2): **20/20** each.
  - `sidewalk-render-check.py`, `sidewalk-render-check20.py` (`9,329` stones), `map2d-check.py`, `v21-new-render-placement.py`, `v22-new-render-placement.py` (`0` violations): **OK**.
  - `country-row-check.py`, `disc-card-check.py`, `attribution-check.py` (axe 0 across 7 viewports), `country-buttons-check.py` (`FALLOS: ninguno`): **OK**.
  - New `tests/v23-ux-and-perf-check.py`: `OK v23 UX: 412x915/360x780/1366x800 initial view (z=3.50), sheet collapse (tap/drag/keys), compass (36x36, axe 0), deferred 3D` and `OK v23 load budget (412x915 gzip 4G 20Mbps 2xCPU): fcp=308ms dcl=919ms vis=8326ms overlays=9061ms`.
- **`publicar.yml` simulation (`--offline` with `pipeline/cache`, `REQUIRE_OAV=1`, `bwrap`):**
  - `pipeline build --strict --offline`: `10,418` API files (`181,668` people across 7 families), `127` site files; `pipeline validate`: `0` errors; `ai-door-check.py`: `0` errors; `ai-sim.py`: `20/20`; `version-test.cjs`: `v24` OK; `rsync` to `/tmp/kl-v23-site`: clean.

## 4. Mobile `412×915` Screenshots (`/workspace/v23-data/shots/`)

- **Before (`b45fcb95`, v22):** `before-initial-412x915.png`, `before-sheet-half-412x915.png`, `before-after-drag-412x915.png`, `before-rotated-412x915.png`
- **After (`v23` / `v24`):** `after-initial-412x915.png`, `after-collapsed-412x915.png`, `after-rotated-412x915.png`, `after-sheet-half-412x915.png`
