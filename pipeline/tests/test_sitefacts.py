"""v37 (auditoría A3): fechas y totales del sitio salen de los datos (pipeline/sitefacts.py)."""
import json
import os
import re
import unittest

from pipeline import sitefacts

ROOT = sitefacts.ROOT


class SiteFacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.F = sitefacts.facts(ROOT)

    def test_map_total_is_what_the_map_loads(self):
        app = open(os.path.join(ROOT, "app3d.js"), encoding="utf-8").read()
        block = app.split("const addedFiles = [", 1)[1].split("];", 1)[0]
        files = re.findall(r"'(data/[a-z0-9]+-added-\d+\.json)'", block)
        n = 0
        for f in files:
            with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
                n += len(json.load(fh)["stones"])
        with open(os.path.join(ROOT, "data/stones.json"), encoding="utf-8") as fh:
            n += len(json.load(fh)["stones"])
        self.assertEqual(len(files), self.F["lists"])
        self.assertEqual(n, self.F["map_total"])

    def test_tracked_site_files_match_data(self):
        self.assertEqual(sitefacts.apply(ROOT, check=True), [], "ejecuta: python3 -m pipeline.sitefacts")

    def test_values_in_files(self):
        F = self.F
        for rel in ("index.html", "kauffmann-list.jsonld"):
            t = open(os.path.join(ROOT, rel), encoding="utf-8").read()
            self.assertIn('"value": %d' % F["map_total"], t)
            self.assertIn('"dateModified": "%s",' % F["data_date"], t)
            self.assertIn("map total {:,}".format(F["map_total"]), t)
        h = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
        desc = re.search(r'<meta name="description" content="([^"]+)"', h).group(1)
        self.assertIn("otros %d países" % (F["countries"] - 1), desc)
        sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
        self.assertRegex(sm, r"kauffmann-list/</loc>\s*<lastmod>%s</lastmod>" % F["data_date"])


if __name__ == "__main__":
    unittest.main()
