"""Geometría mínima (sin dependencias) para comprobar placas contra huellas de edificios de OSM (ODbL).
Coordenadas locales en metros (este, norte) alrededor de un origen; suficiente a escala de calle."""
import math
M_LAT = 111320.0

def to_xy(lat, lon, o):
    return ((lon - o[1]) * M_LAT * math.cos(math.radians(o[0])), (lat - o[0]) * M_LAT)

def to_ll(x, y, o):
    return (o[0] + y / M_LAT, o[1] + x / (M_LAT * math.cos(math.radians(o[0]))))

def hav(a, b, c, d):
    p = math.pi / 180
    x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(x))

def _ring_from_geom(g):
    return [(p['lat'], p['lon']) for p in g]

def _stitch(ways):
    """Une trazos (listas de (lat,lon)) en anillos cerrados."""
    ways = [list(w) for w in ways if len(w) >= 2]
    rings = []
    while ways:
        cur = ways.pop(0)
        guard = 0
        while cur[0] != cur[-1] and guard < 500:
            guard += 1
            for i, w in enumerate(ways):
                if w[0] == cur[-1]: cur += w[1:]; ways.pop(i); break
                if w[-1] == cur[-1]: cur += w[::-1][1:]; ways.pop(i); break
                if w[-1] == cur[0]: cur = w[:-1] + cur; ways.pop(i); break
                if w[0] == cur[0]: cur = w[::-1][:-1] + cur; ways.pop(i); break
            else:
                break
        if cur[0] == cur[-1] and len(cur) >= 4: rings.append(cur)
    return rings

def building_polygons(elements):
    """{id: {'outer': [anillo,...], 'inner': [anillo,...], 'tags': {}}} con anillos en (lat, lon)."""
    out = {}
    for k, e in elements.items():
        t = e.get('tags') or {}
        if e['type'] == 'way':
            g = _ring_from_geom(e.get('geometry') or [])
            if len(g) >= 4 and g[0] == g[-1]: out[k] = {'outer': [g], 'inner': [], 'tags': t}
        elif e['type'] == 'relation':
            ou, inn = [], []
            for m in e.get('members', []):
                if m.get('type') == 'way' and m.get('geometry'):
                    (inn if m.get('role') == 'inner' else ou).append(_ring_from_geom(m['geometry']))
            outer, inner = _stitch(ou), _stitch(inn)
            if outer: out[k] = {'outer': outer, 'inner': inner, 'tags': t}
    return out

def pip(x, y, ring):
    ins = False; n = len(ring)
    for i in range(n - 1):
        x1, y1 = ring[i]; x2, y2 = ring[i + 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: ins = not ins
    return ins

def inside_poly(x, y, rings_o, rings_i):
    return any(pip(x, y, r) for r in rings_o) and not any(pip(x, y, r) for r in rings_i)

def seg_closest(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    cx, cy = ax + t * dx, ay + t * dy
    return cx, cy, math.hypot(px - cx, py - cy)

def dist_to_rings(x, y, rings):
    best = (1e9, None)
    for r in rings:
        for i in range(len(r) - 1):
            cx, cy, d = seg_closest(x, y, r[i][0], r[i][1], r[i + 1][0], r[i + 1][1])
            if d < best[0]: best = (d, (cx, cy))
    return best

def square_corners(x, y, half, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(x + c * dx - s * dy, y + s * dx + c * dy) for dx, dy in ((-half, -half), (half, -half), (half, half), (-half, half), (-half, -half))]

def seg_intersect(p1, p2, p3, p4):
    d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if abs(d) < 1e-12: return False
    t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
    u = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    return 0 <= t <= 1 and 0 <= u <= 1

def square_hits_poly(sq, rings_o, rings_i):
    """True si el cuadrado (anillo cerrado en xy) toca el interior del edificio."""
    if any(inside_poly(px, py, rings_o, rings_i) for px, py in sq[:4]): return True
    for r in rings_o:
        if any(pip(rx, ry, sq) for rx, ry in r[:-1]): return True
        for i in range(len(r) - 1):
            for j in range(4):
                if seg_intersect(r[i], r[i + 1], sq[j], sq[j + 1]): return True
    return False
