"""v37 (auditoría A2/M4): las licencias por fuente que dice llms.txt salen de pipeline/sources/*.json, nunca a mano."""
import re
import unittest

from pipeline import agents
from pipeline.config import load_families, load_sources


def licence_lines(txt):
    """{archivo data/*-added-*.json: familia} según la sección «## Licences» de un llms.txt."""
    sec = txt.split("## Licences", 1)[1].split("\n## ", 1)[0]
    out = {}
    for line in sec.splitlines():
        m = re.match(r"- `api/v1/([a-z0-9-]+)/`", line)
        if not m:
            continue
        for f in re.findall(r"`(data/[a-z0-9]+-added-\*\.json)`", line):
            out.setdefault(f, []).append(m.group(1))
    return out


class LicencesInLlms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load_sources()
        cls.families = load_families(sources=cls.sources)
        fam_indexes = {f: {"count_people": 1} for f in cls.families if not f.startswith("partners/")}
        fam_indexes["dl-de-by"] = {"count_people": 0}
        cls.txt = agents.llms_txt(fam_indexes, cls.families, "2026-11-26", cls.sources)

    def test_every_added_file_under_its_source_family(self):
        got = licence_lines(self.txt)
        expected = {}
        for sid, cfg in self.sources.items():
            m = agents.ADDED_RE.match((cfg.get("input") or {}).get("path") or "")
            if m:
                expected["data/%s-added-*.json" % m.group(1)] = cfg["license_family"]
        self.assertTrue(expected)
        for f, fam in expected.items():
            self.assertEqual(got.get(f), [fam], "%s: llms.txt %s, pipeline %s" % (f, got.get(f), fam))
        self.assertEqual(sorted(got), sorted(expected))

    def test_den_haag_is_cc_by_4(self):
        self.assertEqual(self.sources["denhaag_opendata"]["license_family"], "cc-by-4")
        self.assertEqual(licence_lines(self.txt)["data/denhaag-added-*.json"], ["cc-by-4"])
        self.assertIn("Gemeente Den Haag", self.txt)

    def test_zero_family_explained_not_advertised(self):
        self.assertNotIn("Search manifest – dl-de-by", self.txt)
        line = [l for l in self.txt.splitlines() if l.startswith("- dl-de-by (")][0]
        self.assertIn("0 person records", line)
        self.assertIn("possibly-living rule", line)
        self.assertIn("data/dresden-added-*.json", line)


if __name__ == "__main__":
    unittest.main()
