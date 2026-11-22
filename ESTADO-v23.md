# ESTADO v23 — Mobile UX, Compass, Initial Framing & Performance (Rounds 1–2)

- **Branch:** `v23` (from `b45fcb95`, v22; local only, not pushed)
- **Worktree:** `/workspace/kl-v23`
- **App / SW version:** `v25` (`tests/bump-version.py`, `kauffmann-v25-pages`)
- **Date:** 2026-11-22

## 1. Round 1 + Round 2 Fixes Implemented

1. **Bottom sheet collapse (`index.html`, `mapui.js`, `mapui.css`):**
   - Added `'collapsed'` (`46 px`) state on portrait mobile showing the drag pill + localized label (`Buscar · Países` / `Suche · Länder` / `Search · Countries`).
   - Tap on `#sheetHandle` toggles `collapsed <-> peek` (or `half` when search/detail active); touch/pointer drag snaps across `collapsed / peek / half / full`; keyboard `ArrowUp`/`ArrowDown`/`Escape` work across all states; tapping empty map lowers `half`/`full` to `peek` without re-opening `collapsed`.
   - Accessible name when collapsed includes `T('sheetCollapsed')` (`WCAG 2.5.3`).
2. **Compact square gold compass (`columns.js`, `style3d.css`, `app3d.js`):**
   - Replaced the 3-button `⟲ N ⟳` cluster (`#rotBtns`) with a single `36×36 px` square gold compass (`#rotNorth`) featuring a rotating inline SVG needle + `N`.
   - Hidden when `|bearing| < 1°` (initial `bearing: 0°`); appears bottom-left when rotated with localized `aria-label` including angle (`Mirar al norte (35°)`), resets north on tap/keyboard (`>= 24×24 px`, axe 0).
3. **Closer initial view (`mapui.js`, `app3d.js`):**
   - Replaced world-wide `dataBounds()` framing (`zoom ~2.13`, `bearing -8°`) with `HOME_BOUNDS = [[-6.4, 45.2], [17.5, 55.6]]` and `homePadding()` (`zoom 3.50` on `412×915`, `bearing 0°`), framing Western/Central Europe while keeping Dublin, Hamburg, and Berlin visible.
4. **Load-time & Overview Paint Speedup (`index.html`, `app3d.js`, `mapui.js`, `sw.js`):**
   - Early `fetch('data/stones.json').then(r => r.json())` in `<head>` + parallel `Promise.all` fetch of `stones.json` + 15 added JSONs in `load()`.
   - Spatial-grid `clusterByDist`, cached `addrKey`, `Intl.Collator('de')`, skipped 16-iter collision pass when pinned, skipped unused `STONES_FC`, deferred `ensureSearchIndex()`, lowered `sw.js` `SLOW_MS` to `1800` and protected `*-added-*.json`.
   - **Round 2 immediate overview paint:** Mounts `pts` (`glow` heatmap + `stone-dots`) and `a0` immediately after JSON parse *before* `buildStones()`, yields one macrotask so the golden European overview paints ~3.0 s sooner (`5,012 ms` median vs `8,009 ms` in `47e9f70d`), then runs `buildStones()`, mounts `house-lights` + `kl-clu`, and defers `a1..a3` (`minzoom >= 7.5`) until `zoom >= 6.5` or `350 ms` idle.
5. **First-street-zoom Freeze Fix (Auditor C warning, `columns.js`):**
   - Replaced eager all-74,979-polygon construction on first zoom `>= 12.5` with a lightweight `0.05°` spatial index over `VISIBLE` + per-stone feature cache (`featCache`).
   - `fcFor(half, sides, box)` builds only columns inside the padded viewport bounds (plus `selected`), updating seamlessly via `src.setData(...)` on zoom/pan with identical polygon coordinates (`poly()` & deterministic `r` unchanged).
6. **2D Offline & Single-Version Guard (Auditor B F1, `2d/index.html`, `sw.js`, `tests/bump-version.py`, `tests/version-test.cjs`):**
   - Versioned `2d/style.css?v=25`, `2d/app.js?v=25`, `../counter.js?v=25` in `2d/index.html` and matched them in `sw.js` `SHELL` alongside `vendor/leaflet.markercluster/MarkerCluster.Default.css`.
   - Updated `tests/bump-version.py` and `tests/version-test.cjs` to enforce `?v=N` and `SHELL` membership for both `index.html` and `2d/index.html` (plus `vendor/`/`fonts/` 2D assets), and added a real-SW offline 2D check in `tests/v23-ux-and-perf-check.py`.

## 2. Measured Before vs. After (3-Run Medians, `412×915` dpr=2, gzip 4G `20 Mbps` / `50 ms` RTT / `2× CPU`, counters blocked)

### Initial Load
| Metric | v22 (`b45fcb95`) | Round 1 (`47e9f70d`, v24) | Round 2 (v25) |
|---|---:|---:|---:|
| `FCP` | — | `192 ms` | `192 ms` |
| `DCL` | — | `954 ms` | `908 ms` |
| First golden overview (`pts` + `a0`) | `~18,803 ms` | `8,009 ms` | **`5,012 ms`** |
| Overlays (`pts` + `kl-clu`) | `18,594–18,803 ms` | `8,009 ms` | `9,263 ms` |
| `VISIBLE > 74,000` (`vis`) | `16,483–18,594 ms` | `8,723 ms` | `9,543 ms` |

### First Street Zoom (`map.jumpTo` to Berlin `[13.388, 52.517]`, `zoom 16.5`, `pitch 45°`, `2× CPU`)
| Metric | Round 1 (`47e9f70d`, v24) | Round 2 (v25) | Speedup |
|---|---:|---:|---:|
| Main-thread sync stall (`jumpTo`) | `564 ms` | **`83 ms`** | **6.8× faster** |
| First animation frame (`raf1`) | `3,302 ms` | **`369 ms`** | **8.9× faster** |
| First rendered `stones` painted | `5,838 ms` | **`548 ms`** | **10.7× faster** |

## 3. Verification (Fresh Venv `/tmp/v23-ci-venv`, Zero Skips, Counters Blocked via `bwrap`)

- **Rendered invariance:**
  - Direct comparison vs `b45fcb95` (`v22`): `75,122 / 75,122` stones (`VISIBLE = 74,979`, `diffs = 0` in `_dla`, `_dlo`, `_ang`, `_aliasOf`).
  - `tests/v22-render-compare.py` vs `990ddc10`: `73,950` existing `moved=0 ang_only=0`, `1,172` Batch-1 pinned `pin_fail=0`.
  - `tests/v21-v20-render-compare.py` vs `b142fa48`: `72,110` v20 stones identical + `1,836` v21 visible pinned.
- **Full `REQUIRE_OAV=1 tests/run-all.sh` (NO skips):**
  - All Node JS/data/dedupe/sidewalk/counter/update-flow/version (`v25`) checks: **OK**.
  - `pipeline/tests` (`68 tests`), `REQUIRE_OAV=1 ai-door-check.py` (`0` errors, `4,519` find files, `733,929` rows), `ai-sim.py` (`20/20` seeds 1 & 2): **OK**.
  - `sidewalk-render-check.py`, `sidewalk-render-check20.py` (`9,329` stones), `map2d-check.py`, `v21-new-render-placement.py`, `v22-new-render-placement.py` (`0` violations): **OK**.
  - `country-row-check.py`, `disc-card-check.py`, `attribution-check.py` (axe 0 across 7 sizes), `country-buttons-check.py` (`FALLOS: ninguno` across 10 sizes × 27 countries): **OK**.
  - `tests/v23-ux-and-perf-check.py` (UX + 2D offline real-SW + 4G/2×CPU load + street-zoom budget): **OK**.
- **`publicar.yml` simulation (`--offline`, `REQUIRE_OAV=1`, `bwrap`):**
  - `pipeline build --strict --offline`, `pipeline validate`, `ai-door-check.py`, `ai-sim.py` (`20/20`), `version-test.cjs` (`v25`), `rsync` to `/tmp/kl-v23-site` (`16,085` files): **OK**.
