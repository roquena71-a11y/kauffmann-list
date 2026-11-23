#!/usr/bin/env python3
"""v29 (paso 2 de la v24): geometría OSM para alinear los grupos de columnas con su acera (align24.py) y para comprobarlo (tests/v24-align-check.py).
Fuentes (OSM, ODbL; extractos ya usados por v20–v22, no se descarga nada):
  base DE  : V20_NEAR/DE.pkl + V20_NEAR/D1480.json + V20_EXTRA/DE.json
  base otro: V20_NEAR/CC.pkl o CC.json + V20_EXTRA/CC.json
  añadidas : V21_NEAR/DE-berlin-koeln.pkl (berlin, koeln) · V22_NEAR/DE-batch1.pkl, NL-denhaag.pkl, IT-batch1.pkl (lotes v22)
Cada placa se comprueba con la fuente que se usó para colocarla en v20–v22 (extractos completos a <=100 m de cada placa)."""
import json, math, os, pickle, sys
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import building_polygons, M_LAT
import roadway20 as RWY

V20_NEAR = Path(os.environ.get('V24_V20_NEAR', '/workspace/v20-data/near'))
V20_EXTRA = Path(os.environ.get('V24_V20_EXTRA', '/workspace/v20-data-r4/near-extra'))
V21_NEAR = Path(os.environ.get('V24_V21_NEAR', '/workspace/v21-data/near'))
V22_NEAR = Path(os.environ.get('V24_V22_NEAR', '/workspace/v22-data/near'))
NOT_STREET = {'proposed', 'construction', 'platform', 'bus_stop', 'corridor', 'elevator', 'razed', 'abandoned', 'services', 'rest_area'}
V22_DE = {'moenchengladbach', 'krefeld', 'viersen', 'memmingen', 'moers', 'grevenbroich', 'xanten', 'dresden', 'erkrath', 'dormagen'}

def source_key(cc, src):
    """Clave de la fuente de geometría de una placa (cc de la placa; src = fuente municipal si es añadida)."""
    if src in ('berlin', 'koeln'): return 'DE-berlin-koeln'
    if src in V22_DE: return 'DE-batch1'
    if src == 'denhaag': return 'NL-denhaag'
    if src in ('monza', 'firenze'): return 'IT-batch1'
    return cc or 'DE'

def source_files(key):
    if key == 'DE-berlin-koeln': return [V21_NEAR / 'DE-berlin-koeln.pkl']
    if key in ('DE-batch1', 'NL-denhaag', 'IT-batch1'): return [V22_NEAR / (key + '.pkl')]
    fs = []
    pk, js = V20_NEAR / (key + '.pkl'), V20_NEAR / (key + '.json')
    fs.append(pk if pk.exists() else js)
    if key == 'DE': fs.append(V20_NEAR / 'D1480.json')
    ex = V20_EXTRA / (key + '.json')
    if ex.exists(): fs.append(ex)
    return fs

class Geo:
    """Edificios (polígonos) y vías (líneas) en lon/lat con STRtree; consultas locales en metros (x este, y norte) como geo.to_xy."""
    def __init__(self, key):
        self.key = key; bpolys = []; bids = set(); hl = []; ht = []; hids = set(); self.files = []
        for f in source_files(key):
            if not f.exists(): raise SystemExit('FALLO: falta la geometría OSM %s' % f)
            self.files.append(str(f))
            if f.suffix == '.pkl':
                d = pickle.load(open(f, 'rb'))
                B = ((bid, o, i) for bid, (o, i, t) in d['buildings'].items())
                H = ((hid, p, t) for hid, (p, t) in d['highways'].items())
            else:
                d = json.load(open(f, encoding='utf-8'))
                B = ((bid, b['outer'], b['inner']) for bid, b in building_polygons(d['buildings']).items())
                H = ((hid, [(q['lat'], q['lon']) for q in h.get('geometry', [])], h.get('tags') or {}) for hid, h in d['highways'].items())
            for bid, outer, inner in B:
                if bid in bids: continue
                bids.add(bid)
                try:
                    ps = [Polygon([(c, a) for a, c in r]) for r in outer if len(r) >= 4]
                    ps = [p if p.is_valid else p.buffer(0) for p in ps]
                    g = unary_union(ps) if len(ps) > 1 else ps[0]
                    if inner: g = g.difference(unary_union([Polygon([(c, a) for a, c in r]).buffer(0) for r in inner if len(r) >= 4]))
                    if not g.is_empty: bpolys.append(g)
                except Exception: continue
            for hid, pts, t in H:
                if hid in hids or len(pts) < 2: continue
                if t.get('highway') in NOT_STREET or t.get('tunnel') or t.get('indoor'): continue
                hids.add(hid); hl.append(LineString([(c, a) for a, c in pts])); ht.append(t)
            del d
        self.B = np.array(bpolys, dtype=object); self.H = np.array(hl, dtype=object); self.HT = ht
        self.btree = shapely.STRtree(self.B); self.htree = shapely.STRtree(self.H)
        self.nb, self.nh = len(bpolys), len(hl)

    def local(self, la0, lo0, rad):
        """(edificios locales, árbol, [(línea, tags)]) a <= rad m de (la0, lo0) en metros."""
        kx = M_LAT * math.cos(math.radians(la0)); ky = M_LAT
        dla, dlo = rad / ky, rad / kx
        q = shapely.box(lo0 - dlo, la0 - dla, lo0 + dlo, la0 + dla)
        f = lambda c: (c - np.array([lo0, la0])) * np.array([kx, ky])
        bi = self.btree.query(q); hi = self.htree.query(q)
        B = shapely.transform(self.B[bi], f) if len(bi) else np.array([], dtype=object)
        H = shapely.transform(self.H[hi], f) if len(hi) else np.array([], dtype=object)
        return B, shapely.STRtree(B) if len(B) else None, [(H[k], self.HT[j]) for k, j in enumerate(hi)]

def to_local(la, lo, la0, lo0):
    return ((np.asarray(lo) - lo0) * M_LAT * math.cos(math.radians(la0)), (np.asarray(la) - la0) * M_LAT)

def squares(xs, ys, ang, half=0.60):
    c, s = math.cos(ang), math.sin(ang)
    corners = [(-half, -half), (half, -half), (half, half), (-half, half), (-half, -half)]
    out = []
    for x, y in zip(xs, ys):
        out.append(shapely.polygons([(x + c * dx - s * dy, y + s * dx + c * dy) for dx, dy in corners]))
    return np.array(out, dtype=object)

def grid_offsets(n, cols, ang, step=1.85):
    """Igual que layoutAligned() de app3d.js: casilla i → (cx, cy) con cols columnas a lo largo de ang."""
    rows = math.ceil(n / cols) or 1
    cA, sA = math.cos(ang), math.sin(ang); out = []
    for i in range(n):
        cx = (i % cols) - (cols - 1) / 2; cy = (i // cols) - (rows - 1) / 2
        out.append((cx * step * cA - cy * step * sA, cx * step * sA + cy * step * cA))
    return out

def place_ll(la0, lo0, n, cols, ang, step=1.85):
    """Posiciones (lat, lon) exactamente como el cliente: la0 + north/M_LAT, lo0 + east/(M_LAT·cos la0)."""
    cos = math.cos(la0 * math.pi / 180)
    return [(la0 + no / M_LAT, lo0 + ea / (M_LAT * cos)) for ea, no in grid_offsets(n, cols, ang, step)]
