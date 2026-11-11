"""Carga y valida la configuración de fuentes (sources/*.json) y familias de licencia (families.json)."""
import glob
import os
import re

from .util import PIPELINE_DIR, load_json

SOURCES_DIR = os.path.join(PIPELINE_DIR, "sources")
FAMILIES_PATH = os.path.join(PIPELINE_DIR, "families.json")
SUPPRESSED_PATH = os.path.join(PIPELINE_DIR, "suppressed.json")

REQUIRED = ["id", "name", "phase", "enabled", "publish_allowed", "adapter", "license", "license_url",
            "attribution", "id_prefix", "license_family", "priority"]


class ConfigError(Exception):
    pass


def validate_source(cfg, adapters):
    errs = []
    for k in REQUIRED:
        if k not in cfg:
            errs.append("falta '%s'" % k)
    if errs:
        return errs
    if not re.match(r"^[a-z0-9_]+$", cfg["id"]):
        errs.append("id inválido")
    if not re.match(r"^[a-z][a-z0-9]*$", cfg["id_prefix"]):
        errs.append("id_prefix inválido (solo [a-z0-9], empieza por letra)")
    if cfg["phase"] not in (1, 2):
        errs.append("phase debe ser 1 o 2")
    if cfg["adapter"] not in adapters:
        errs.append("adaptador desconocido: %s" % cfg["adapter"])
    fam = cfg["license_family"]
    if not re.match(r"^[a-z0-9_]+(/[a-z0-9_]+)?$", fam):
        errs.append("license_family inválida")
    if cfg["phase"] == 2 and fam != "partners/" + cfg["id"]:
        errs.append("una fuente de fase 2 debe tener su propia familia 'partners/%s' (nunca se mezcla con OSM)" % cfg["id"])
    if fam.startswith("partners/") and fam != "partners/" + cfg["id"]:
        errs.append("la familia partners/<x> pertenece solo a la fuente x")
    if cfg["adapter"] == "generic_tabular":
        m = cfg.get("mapping") or {}
        if "record_id" not in m:
            errs.append("mapping.record_id es obligatorio")
        if "input" not in cfg or not (cfg["input"].get("path") or cfg["input"].get("url")):
            errs.append("input.path o input.url es obligatorio")
    if not isinstance(cfg["publish_allowed"], bool) or not isinstance(cfg["enabled"], bool):
        errs.append("enabled y publish_allowed deben ser booleanos")
    return errs


def load_sources(sources_dir=None, adapters=None):
    from .adapters import ADAPTERS
    adapters = adapters or ADAPTERS
    out = {}
    for path in sorted(glob.glob(os.path.join(sources_dir or SOURCES_DIR, "*.json"))):
        cfg = load_json(path)
        errs = validate_source(cfg, adapters)
        if errs:
            raise ConfigError("%s: %s" % (os.path.basename(path), "; ".join(errs)))
        if cfg["id"] + ".json" != os.path.basename(path):
            raise ConfigError("%s: el nombre del archivo debe ser <id>.json" % path)
        out[cfg["id"]] = cfg
    return out


def load_families(path=None, sources=None):
    fams = load_json(path or FAMILIES_PATH)["families"]
    for sid, cfg in (sources or {}).items():
        fam = cfg["license_family"]
        if fam.startswith("partners/") and fam not in fams:
            fams[fam] = {"license": cfg["license"], "license_url": cfg["license_url"],
                         "attribution": [cfg["attribution"]], "description": "Datos de %s (archivo separado)." % cfg["name"],
                         "source_url": cfg.get("homepage")}
    for sid, cfg in (sources or {}).items():
        if cfg["license_family"] not in fams:
            raise ConfigError("%s: familia '%s' no definida en families.json" % (sid, cfg["license_family"]))
    return fams


def load_suppressed(path=None):
    p = path or SUPPRESSED_PATH
    if not os.path.exists(p):
        return set()
    data = load_json(p)
    ids = data.get("ids", []) if isinstance(data, dict) else data
    return set(str(x).strip() for x in ids if str(x).strip())
