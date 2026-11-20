#!/usr/bin/env python3
"""v20r4 (auditoría C ronda 3, §2): regla de CALZADA. El centro de una columna dibujada no puede quedar sobre la calzada de una vía rodada de OSM.
Vía rodada = highway motorway/trunk/primary/secondary/tertiary/unclassified/residential (sin túnel ni puente; no service, living_street, pedestrian, footway…: ahí no hay acera que deducir).
Semiancho de calzada: width/2 de OSM si existe (1,5–8 m); si no, por clase (residential/unclassified 2,5; tertiary 2,75; secondary 3,0; primary/trunk 3,5; motorway 7,0).
Regla (comprobación): el CENTRO de la columna dibujada debe estar a >= semiancho del eje (el solver deja 0,3 m más). Exención «acera pegada a la fachada»: si hay un edificio a < 6 m del centro la regla no se aplica
(la calle ya es estrecha entre fachadas; mismo criterio que la auditoría C). Sin edificio a <= 25 m del grupo no hay acera que deducir: no se mueve, se documenta. sidewalk=no en OSM: se documenta, no se mueve.
Este módulo lo usan el solver (sidewalk20.py), el CSV de excepciones (calzada-v20.csv) y el test (tests/sidewalk-render-check20.py)."""
import math
VEH = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential'}
HW = {'residential': 2.5, 'unclassified': 2.5, 'tertiary': 2.75, 'secondary': 3.0, 'primary': 3.5, 'trunk': 3.5, 'motorway': 7.0}
COL_HALF = 0.6; BLD_EXEMPT_NEAR = 6.0
def is_vehicular(tags):
    t = tags or {}
    return t.get('highway') in VEH and not t.get('tunnel') and not t.get('bridge') and not t.get('indoor')
def semiwidth(tags):
    t = tags or {}
    w = t.get('width') or t.get('est_width')
    if w:
        try:
            v = float(str(w).replace(',', '.').split()[0])
            if 3.0 <= v <= 16.0: return v / 2
        except ValueError: pass
    return HW[t['highway']]
NO_SIDEWALK = {'no', 'none'}
SOLVER_MARGIN = 0.3     # el solver deja el centro a >= semiancho + 0,3 m; la comprobación exige >= semiancho
BLD_NEAR_MAX = 25.0     # sin ningún edificio a <= 25 m del grupo no hay línea de fachada ni acera que deducir: no se mueve, se documenta
def constrained(tags):
    """Vía rodada que obliga a mantener el centro fuera de la calzada (sidewalk=no/none: sin acera en OSM, se documenta pero no se mueve)."""
    t = tags or {}
    return is_vehicular(t) and not any(t.get(k) in NO_SIDEWALK for k in ('sidewalk', 'sidewalk:both')) and not (t.get('sidewalk:left') in NO_SIDEWALK and t.get('sidewalk:right') in NO_SIDEWALK)
def no_sidewalk(tags): return is_vehicular(tags) and not constrained(tags)
