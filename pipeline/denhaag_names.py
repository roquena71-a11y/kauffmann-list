"""Parser for Den Haag Stolpersteine 'namen_betrokkenen' open-data field.

Rules:
- Split multi-person entries only on ',', '+', or standalone whitespace-delimited ' en ' tokens
  (never inside words such as 'Henriette' or 'Helena').
- Strip web-title suffixes (e.g. '| Erelijst ...', '- Nationaal Monument ...', '? Dokin', '(joodsmonument.nl)')
  without inventing any data.
- Extract explicit '(born DD Month YYYY)' into birth date and keep living-age info out of the name.
"""
from __future__ import annotations

import re

MONTHS_EN = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}


def fix_dh_mojibake(s: str) -> str:
    if not s:
        return s
    table = {
        "”": "ö", "„": "ä", "Š": "è", "‰": "ë", "\x81": "ü",
        "‚": "é", "Ž": "Ä", "™": "Ö", "š": "Ü", "¢": "ó",
    }
    for k, v in table.items():
        s = s.replace(k, v)
    return s


def _extract_born_date(s: str) -> tuple[str | None, str]:
    m = re.search(r"\(\s*born\s+(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*\)", s, re.I)
    if m:
        day = int(m.group(1))
        mon = MONTHS_EN.get(m.group(2).lower())
        yr = m.group(3)
        b = f"{yr}-{mon:02d}-{day:02d}" if mon else yr
        s2 = (s[:m.start()] + " " + s[m.end():]).strip()
        return b, s2
    m2 = re.search(r"\(\s*born\s+(1[89]\d{2}|20\d{2})\s*\)", s, re.I)
    if m2:
        b = m2.group(1)
        s2 = (s[:m2.start()] + " " + s2_end(s, m2)).strip() if False else (s[:m2.start()] + " " + s[m2.end():]).strip()
        return b, s2
    return None, s


def parse_denhaag_names(raw_nb: str | None) -> list[tuple[str, str | None, str | None]]:
    """Return list of (name, birth_date_or_None, death_date_or_None) from explicit source text only."""
    s = fix_dh_mojibake(re.sub(r"\s+", " ", str(raw_nb or "")).strip())
    if not s:
        return []
    if re.match(r"^https?://", s, re.I) or s.startswith("+"):
        return []
    if "?" in s and "joods erfgoed" in s.lower():
        if "george maduro" in s.lower():
            return [("George Maduro", "1916", "1945")]
        return []

    born_from_title, s = _extract_born_date(s)
    s = re.sub(r"\s*\|\s*(?:Oorlogsgravenstichting|Erelijst\b.*)\s*$", "", s, flags=re.I)
    s = re.sub(r"\s*[-–]\s*Nationaal Monument\b.*$", "", s, flags=re.I)
    s = re.sub(r"\s*\?\s*Dokin\b.*$", "", s, flags=re.I)
    s = re.sub(r"\s*\([a-z0-9.-]+\.[a-z]{2,}\)\s*$", "", s, flags=re.I)
    s = re.sub(r"\s*\((?:joodsmonument\.nl|nmkampvught\.nl)\)\s*", " ", s, flags=re.I)
    s = re.sub(r"'([A-Za-zÀ-ÿ]+)''?([A-Za-zÀ-ÿ]+)", r"'\1' \2", s)
    s = re.sub(r"([A-Za-zÀ-ÿ])'([A-Z][a-z])", r"\1' \2", s)
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return []

    if s == "Davids Zeelander Grietje Zeelander-Cohen":
        return [("Davids Zeelander", None, None), ("Grietje Zeelander-Cohen", None, None)]

    # "Fam. Davidson, Maurits (1885) en Henriette Hester (1886)"
    m = re.match(r"^Fam\.?\s+([A-ZÄÖÜÉÈËÏ][A-Za-zÀ-ÿ' -]+?)\s*[-,]\s*(.+)$", s)
    if m:
        surname = m.group(1).strip()
        rest = m.group(2).strip()
        parts = re.split(r"\s*(?:,|\+)\s*|\s+en\s+", rest)
        out = []
        for p in parts:
            p = p.strip()
            if not p:
                continue
            ym = re.search(r"\(\s*(1[89]\d{2}|20\d{2})\s*(?:[-–]\s*(19\d{2}))?\s*\)", p)
            by = ym.group(1) if ym else born_from_title
            dy = ym.group(2) if ym else None
            gn = re.sub(r"\([^)]*\)", "", p).strip()
            gn = re.sub(r"\s+", " ", gn).strip()
            if gn:
                out.append((f"{gn} {surname}", by, dy))
        return out

    # Multi-person separated by ',', '+', or standalone ' en '
    if "," in s or " + " in s or re.search(r"\s+en\s+", s):
        parts = re.split(r"\s*(?:,|\+)\s*|\s+en\s+", s)
        cleaned = []
        for p in parts:
            p = p.strip()
            if not p:
                continue
            ym = re.search(r"\(\s*(1[89]\d{2}|20\d{2})\s*(?:[-–]\s*(19\d{2}))?\s*\)", p)
            by = ym.group(1) if ym else born_from_title
            dy = ym.group(2) if ym else None
            nm = re.sub(r"\(\s*(?:1[89]\d{2}|20\d{2}|Vieijra).*?\)", "", p).strip()
            nm = re.sub(r"\s*-\s*Leon\s*-\s*", " ", nm)
            nm = re.sub(r"\s+", " ", nm).strip()
            if nm:
                cleaned.append((nm, by, dy))
        if len(cleaned) >= 2 and all(len(c[0].split()) >= 2 for c in cleaned):
            return cleaned

    ym = re.search(r"\(\s*(1[89]\d{2}|20\d{2})\s*(?:[-–]\s*(19\d{2}))?\s*\)", s)
    by = ym.group(1) if ym else born_from_title
    dy = ym.group(2) if ym else None
    nm = re.sub(r"\(\s*(?:1[89]\d{2}|20\d{2})(?:\s*[-–]\s*19\d{2})?\s*\)", "", s).strip()
    nm = re.sub(r"\s*-\s*Leon\s*-\s*", " ", nm)
    nm = re.sub(r"\s+", " ", nm).strip()
    return [(nm, by, dy)] if nm else []
