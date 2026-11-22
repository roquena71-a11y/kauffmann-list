# ESTADO v23 — Mobile UX, Compass, Initial Framing & Load-Time Fix

Branch: `v23` (from `b45fcb95`, v22)
Worktree: `/workspace/kl-v23`
Version: `v24` (updated via `tests/bump-version.py`)

## Measured Load-Time Root Cause (Issue 3)

Profiled on `b45fcb95` (v22) in Chromium mobile emulation (`412×915`, `dpr=2`, gzip HTTP, `kl-contador` and `*.workers.dev` blocked):

1. **`clusterByDist(noAddr, 3.5)` in `app3d.js` (O(N²) bottleneck):** `6,935` stones without street addresses ran an unindexed double loop (~24M `distM` calls), blocking the main thread for **`1,831 ms` unthrottled** (~4–5 s on mobile CPU).
2. **`buildStones()` total (~`3,023 ms` unthrottled on v22):**
   - Repeated `addrKey(s)` (7 regex replacements × ~250k calls), repeated `localeCompare(..., 'de')`, and string key allocations in `neighbors()` (`1.45M` concats).
   - Always ran the 16-iteration 75k-stone collision grid pass even though `META.layout_pinned === true` (all 72,110 base stones already pre-separated).
   - Built `74,979` unused `STONES_FC` polygon features even when `KLCols` replaces `'stones'`.
   - Built `ensureSearchIndex()` (`75,122` `_t`/`_c` token arrays + `1,978` `#cities` `<option>` DOM nodes) synchronously before `kl:data`.
3. **`KLCols.add()` in `columns.js`:** Eagerly built `74,979 × 38`-vertex rounded-square polygons (~2.85M coordinates) and uploaded them to MapLibre's worker at initial overview zoom (`minzoom: 14.6`, completely invisible at startup). Combined with `buildStones()`, this caused ~`6.6–7.1 s` unthrottled / ~`11.7 s` throttled main-thread lockup.
4. **Serial data waterfall & SW timeout:** The 15 `*-added-*.json` files (~160 KB gz) were fetched serially *after* `data/stones.json` (~5.59 MB gz / 26.0 MB raw) downloaded and parsed, and `sw.js` `SLOW_MS` waited `4,500 ms` before falling back to cache on slow repeat visits.

### Before vs. After Timings (`412×915`, gzip, counters blocked)

| Profile | v22 (`b45fcb95`) `vis` / `overlays` | v23 (`v24`) `vis` / `overlays` | First Paint / FCP |
|---|---:|---:|---:|
| Local gzip unthrottled | `7,384 ms` / `7,441 ms` (live-equivalent `8,179 ms` / `10,931 ms`) | `3,130 ms` / `3,496 ms` | `80 ms` |
| Mobile 4G `20 Mbps`, `50 ms` RTT, `2× CPU` | `18,594 ms` / `18,803 ms` | `8,654 ms` / `9,509 ms` | `228 ms` |
| Mobile 4G `10 Mbps`, `60 ms` RTT, `3× CPU` | `29,333 ms` / `29,533 ms` | `13,726 ms` / `14,728 ms` | `248 ms` |

## 4 Fixes Implemented

1. **Collapsible bottom sheet (`index.html`, `mapui.js`, `mapui.css`):**
   - Added `'collapsed'` (`46 px`) state in portrait mobile showing the drag handle pill + localized label (`Buscar · Países` / `Suche · Länder` / `Search · Countries`), hiding search/countries/results until expanded.
   - Tapping `#sheetHandle` toggles `collapsed <-> peek` (or `half` if search/detail is open); pointer/touch drag smoothly resizes down to `46 px` and snaps across `collapsed / peek / half / full`; keyboard `ArrowUp`/`ArrowDown`/`Escape` support all states; tapping empty map lowers `half`/`full` to `peek` without re-opening `collapsed`.
   - Fixed WCAG 2.5.3 `label-content-name-mismatch` by including `T('sheetCollapsed')` in `#sheetHandle`'s `aria-label` when collapsed.

2. **Compact square gold compass (`columns.js`, `style3d.css`, `app3d.js`):**
   - Replaced the 3-button `⟲ N ⟳` cluster (`#rotBtns`) with a single compact `36×36 px` square gold compass (`#rotNorth`) with rotating inline SVG needle + `N`.
   - Hidden automatically when `|bearing| < 1°` (and initial `bearing` is `0°`), appears at bottom-left when rotated, announces bearing in ES/DE/EN (`aria-label`), resets to North on tap/keyboard, meets WCAG 2.2 AA (`>= 24×24 px` target size, keyboard access, contrast).

3. **Startup speed (`index.html`, `app3d.js`, `columns.js`, `sw.js`):**
   - Early `fetch('data/stones.json')` in `<head>` (without blocking `DOMContentLoaded` on JSON parsing); parallel `Promise.all` fetch of `stones.json` + 15 added JSONs in `load()`.
   - Spatial-grid `clusterByDist` for `n > 40`, cached `addrKey` (`s._ak`), `Intl.Collator('de')`, 2-level `near` lookup map, skipped 16-iter collision pass when all groups are pinned, skipped unused `STONES_FC` when `KLCols` is present.
   - Deferred `ensureSearchIndex()` (`s._t`, `s._c`, `#cities` DOM) by `60 ms` post-overlays (plus lazy on focus/search).
   - Deferred `KLCols.add()` 3D column polygon generation until zoom `>= 12.5` (or `?modelos=` / selection), mounting seamlessly on zoom/move/select.
   - Lowered `sw.js` `SLOW_MS` from `4500` to `1800` and protected `*-added-*.json` in `trim()`.

4. **Closer initial framing (`mapui.js`, `app3d.js`):**
   - Replaced world-wide `dataBounds()` framing (`zoom ~2.13`, `bearing -8°`) with `HOME_BOUNDS = [[-6.4, 45.2], [17.5, 55.6]]` and `homePadding()` (`zoom ~3.50` on `412×915`, `bearing 0°`), centering Western/Central Europe while keeping Dublin, Hamburg, and Berlin in frame.

## Invariance & Screenshots (Verified So Far)

- **Rendered invariance vs `b45fcb95` (`v22`):** `75,122 / 75,122` stones matched (`VISIBLE = 74,979`, `0` diffs in `_dla`, `_dlo`, `_ang`, `_aliasOf`).
- **Mobile `412×915` screenshots (`/workspace/v23-data/shots/`):**
  - Before (`b45fcb95`): `before-initial-412x915.png`, `before-sheet-half-412x915.png`, `before-after-drag-412x915.png`
  - After (`v23`): `after-initial-412x915.png`, `after-collapsed-412x915.png`, `after-rotated-412x915.png`, `after-sheet-half-412x915.png`
- **Existing Playwright checks passed:** `attribution-check.py` (axe 0 across 7 viewports), `country-row-check.py`, `disc-card-check.py`, `map2d-check.py`, `sidewalk-render-check.py`, `sidewalk-render-check20.py`, `version-test.cjs`, `counter-sw-test.cjs`, `update-flow-test.cjs`.

## Pending Final Verification

- Re-run `tests/v23-ux-and-perf-check.py` after WCAG 2.5.3 `aria-label` fix.
- Wire `tests/v23-ux-and-perf-check.py` into `tests/run-all.sh` and bump version if needed.
- Run full `REQUIRE_OAV=1 tests/run-all.sh` with no skips (including `country-buttons-check.py`, `v22-render-compare.py`, `v21-v20-render-compare.py`, `v21-new-render-placement.py`, `v22-new-render-placement.py`).
- Run clean `publicar.yml` simulation.
