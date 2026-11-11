"""Validador mínimo de JSON Schema (subconjunto de 2020-12) sin dependencias.

Soporta: type (incl. listas), enum, const, required, properties, additionalProperties (bool o esquema),
items, minItems, minLength, pattern, minimum, maximum, $ref local (#/$defs/...), anyOf, oneOf.
"""
import re

_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


class Validator:
    def __init__(self, schema):
        self.root = schema
        self._re = {}

    def _resolve(self, ref):
        if not ref.startswith("#/"):
            raise ValueError("solo se admiten $ref locales: %s" % ref)
        node = self.root
        for part in ref[2:].split("/"):
            node = node[part]
        return node

    def _pattern(self, p):
        if p not in self._re:
            self._re[p] = re.compile(p)
        return self._re[p]

    def errors(self, value, schema=None, path="$"):
        schema = self.root if schema is None else schema
        out = []
        if "$ref" in schema:
            out.extend(self.errors(value, self._resolve(schema["$ref"]), path))
        t = schema.get("type")
        if t is not None:
            types = t if isinstance(t, list) else [t]
            if not any(_TYPES[x](value) for x in types):
                return out + ["%s: tipo %s no es %s" % (path, type(value).__name__, "/".join(types))]
        if "enum" in schema and value not in schema["enum"]:
            out.append("%s: %r no está en enum" % (path, value))
        if "const" in schema and value != schema["const"]:
            out.append("%s: debe ser %r" % (path, schema["const"]))
        if isinstance(value, str):
            if "minLength" in schema and len(value) < schema["minLength"]:
                out.append("%s: longitud < %d" % (path, schema["minLength"]))
            if "pattern" in schema and not self._pattern(schema["pattern"]).search(value):
                out.append("%s: %r no cumple %s" % (path, value, schema["pattern"]))
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in schema and value < schema["minimum"]:
                out.append("%s: < %s" % (path, schema["minimum"]))
            if "maximum" in schema and value > schema["maximum"]:
                out.append("%s: > %s" % (path, schema["maximum"]))
        if isinstance(value, dict):
            for k in schema.get("required", []):
                if k not in value:
                    out.append("%s: falta '%s'" % (path, k))
            props = schema.get("properties", {})
            addl = schema.get("additionalProperties", True)
            for k, v in value.items():
                if k in props:
                    out.extend(self.errors(v, props[k], "%s.%s" % (path, k)))
                elif addl is False:
                    out.append("%s: propiedad no permitida '%s'" % (path, k))
                elif isinstance(addl, dict):
                    out.extend(self.errors(v, addl, "%s.%s" % (path, k)))
        if isinstance(value, list):
            if "minItems" in schema and len(value) < schema["minItems"]:
                out.append("%s: menos de %d elementos" % (path, schema["minItems"]))
            if "items" in schema:
                for i, v in enumerate(value):
                    out.extend(self.errors(v, schema["items"], "%s[%d]" % (path, i)))
        if "anyOf" in schema:
            if not any(not self.errors(value, s, path) for s in schema["anyOf"]):
                out.append("%s: no cumple ningún anyOf" % path)
        if "oneOf" in schema:
            if sum(1 for s in schema["oneOf"] if not self.errors(value, s, path)) != 1:
                out.append("%s: no cumple exactamente un oneOf" % path)
        return out

    def is_valid(self, value):
        return not self.errors(value)
