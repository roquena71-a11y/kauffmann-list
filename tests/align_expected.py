"""v29: posición de dibujo ESPERADA tras la alineación con la calle (data/align-v24.json).
Fórmula escrita aparte (no se importa la del pipeline): casilla i de una entrada [lat·1e7, lon·1e7, rumbo·10, columnas, ids…]
→ cx = (i % cols) − (cols−1)/2, cy = ⌊i/cols⌋ − (filas−1)/2; este = cx·paso·cos a − cy·paso·sin a; norte = cx·paso·sin a + cy·paso·cos a."""
import json, math
from pathlib import Path
R = Path(__file__).resolve().parents[1]
M_LAT = 111320.0
WAIT_JS = "(!window.KLAlign || KLAlign.ready)"   # los clientes anteriores no tienen KLAlign

def load(path=None):
    d = json.load(open(path or (R / 'data' / 'align-v24.json')))
    step = float(d['step']); out = {}
    for e in d['g']:
        la0, lo0, ang, cols, ids = e[0] / 1e7, e[1] / 1e7, e[2] * math.pi / 1800, e[3], e[4:]
        rows = math.ceil(len(ids) / cols) or 1; cos = math.cos(la0 * math.pi / 180)
        for i, sid in enumerate(ids):
            cx = (i % cols) - (cols - 1) / 2; cy = (i // cols) - (rows - 1) / 2
            east = cx * step * math.cos(ang) - cy * step * math.sin(ang)
            north = cx * step * math.sin(ang) + cy * step * math.cos(ang)
            out[str(sid)] = (la0 + north / M_LAT, lo0 + east / (M_LAT * cos), ang)
    return out
