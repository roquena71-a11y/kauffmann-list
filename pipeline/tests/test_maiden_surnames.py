"""Unit tests for maiden/married surname extraction (Auditor A ronda 2, gv-11)."""
import unittest

from pipeline.maiden_surnames import extract_surnames

GV11_INSCRIPTION = (
    "Hier wohnte\nCilly Hirsch\nVerh. Claessens\nJg. 1907\n"
    "Flucht 1935 Belgien/Holland\nInterniert Westerbork\n"
    "Deportiert 1942 Auschwitz\nErmordet 31.8.1942"
)


class TestExtractSurnames(unittest.TestCase):
    def test_gv11_cilly_claessens_inscription_includes_maiden_hirsch(self):
        surnames = extract_surnames("Cilly Claessens", "Claessens", GV11_INSCRIPTION)
        self.assertIn("claessens", surnames)
        self.assertIn("hirsch", surnames)

    def test_slash_form_verh(self):
        surnames = extract_surnames(
            "Cilly Claessens", "Claessens",
            "Cilly Hirsch / Verh. Claessens / Jg. 1907",
        )
        self.assertIn("claessens", surnames)
        self.assertIn("hirsch", surnames)

    def test_geb_in_name_includes_both(self):
        surnames = extract_surnames("Cilly Claessens geb. Hirsch", "Claessens")
        self.assertIn("claessens", surnames)
        self.assertIn("hirsch", surnames)

    def test_gesch_in_name_includes_both(self):
        surnames = extract_surnames("Anna Müller Gesch. Schmidt", "Müller")
        self.assertIn("mueller", surnames)
        self.assertIn("schmidt", surnames)

    def test_verw_in_inscription_includes_both(self):
        surnames = extract_surnames(
            "Eva Lehmann", "Lehmann",
            "Hier wohnte\nEva Cohn\nverw. Lehmann\nJg. 1890",
        )
        self.assertIn("lehmann", surnames)
        self.assertIn("cohn", surnames)


if __name__ == "__main__":
    unittest.main()
