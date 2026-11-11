"""Registro de adaptadores: el campo "adapter" de sources/<x>.json elige uno de estos."""
from . import generic_tabular, overpass, stones, wikidata_sparql

ADAPTERS = {
    "stones": stones.fetch,
    "wikidata_sparql": wikidata_sparql.fetch,
    "overpass": overpass.fetch,
    "generic_tabular": generic_tabular.fetch,
}
