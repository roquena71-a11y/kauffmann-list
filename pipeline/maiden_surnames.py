"""Extract maiden and married surnames from names and inscriptions.

For patterns such as «X Verh. Y», «geb.», «Gesch.» and «verw.» (and similar
particles), BOTH the surname before the particle and the surname after it are
collected, so a municipal record named with the married surname can be matched
to an existing plaque that uses the maiden surname (and vice versa).
"""
from __future__ import annotations

import re
import unicodedata

# Longer forms first so "verheiratet" wins over "verh.", "geborene" over "geboren"/"geb.".
_PARTICLE = (
    r"(?:verheiratet|verh\.?|geborene|geboren|geb\.?|"
    r"geschieden|gesch\.?|verwitwet|verw\.?|n[ée]e)"
)
_SURNAME = r"([A-ZÄÖÜÉÈËÏÀ-ÿ][A-Za-zÀ-ÿ'’\-]+)"
_AFTER = re.compile(rf"\b{_PARTICLE}\s+{_SURNAME}", re.I)
# Surname immediately before the particle, allowing a newline or «/ , ; :».
_BEFORE = re.compile(rf"{_SURNAME}\s*[/|,;:]?\s*\b{_PARTICLE}\b", re.I)


def fold_surname(s: str) -> str:
    if not s:
        return ""
    s = str(s)
    for a, b in (
        ("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"),
        ("Ä", "ae"), ("Ö", "oe"), ("Ü", "ue"),
        ("ø", "o"), ("Ø", "o"), ("ł", "l"), ("Ł", "l"),
        ("æ", "ae"), ("Æ", "ae"), ("œ", "oe"), ("Œ", "oe"),
    ):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = re.sub(r"['’‘`´ʼ]", "", s)
    s = re.sub(r"[^a-zA-Z0-9\s-]", " ", s).lower()
    return re.sub(r"\s+", " ", s).strip()


def extract_surnames(raw_n: str, parsed_last: str, insc: str | None = None, fold=None) -> set[str]:
    """Return folded maiden and married surnames from a name and/or inscription."""
    fold = fold or fold_surname
    out: set[str] = set()
    if parsed_last:
        fl = fold(parsed_last)
        if fl:
            out.add(fl)
    for txt in (raw_n or "", insc or ""):
        for m in _AFTER.finditer(txt):
            w = fold(m.group(1))
            if w:
                out.add(w)
        for m in _BEFORE.finditer(txt):
            w = fold(m.group(1))
            if w:
                out.add(w)
    for s in list(out):
        if "-" in s:
            for part in s.split("-"):
                if len(part) >= 3:
                    out.add(part)
    return out
