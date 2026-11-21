import unittest
from pipeline.denhaag_names import parse_denhaag_names


class DenHaagNameParsingTests(unittest.TestCase):
    def test_en_never_splits_inside_words_henriette_helena(self):
        # dh-294: 'Henriette' contains 'en' and must never be split
        self.assertEqual(
            parse_denhaag_names("Fam. Davidson, Maurits (1885) en Henriette Hester (1886)"),
            [("Maurits Davidson", "1885", None), ("Henriette Hester Davidson", "1886", None)],
        )
        # dh-296: 'Helena' contains 'en' and must never be split
        self.assertEqual(
            parse_denhaag_names("Fam. Konraad - Betje Helena ( 1909) en Sara (1933)"),
            [("Betje Helena Konraad", "1909", None), ("Sara Konraad", "1933", None)],
        )

    def test_dh_306_two_people_split(self):
        self.assertEqual(
            parse_denhaag_names("Davids Zeelander Grietje Zeelander-Cohen"),
            [("Davids Zeelander", None, None), ("Grietje Zeelander-Cohen", None, None)],
        )

    def test_strip_web_title_suffixes_and_living_age(self):
        # dh-122
        self.assertEqual(
            parse_denhaag_names("Gerrit Jan Bakker | Erelijst van Gevallenen 1940-1945"),
            [("Gerrit Jan Bakker", None, None)],
        )
        # dh-155
        self.assertEqual(
            parse_denhaag_names("Frederik Willem Franx - Nationaal Monument Kamp Vught (nmkampvught.nl)"),
            [("Frederik Willem Franx", None, None)],
        )
        # dh-193: birth info extracted to birth_date, never left in display name n
        res = parse_denhaag_names("Walter Eylenburg (born 14 December 1929) ? Dokin")
        self.assertEqual(res, [("Walter Eylenburg", "1929-12-14", None)])
        self.assertNotIn("born", res[0][0].lower())
        self.assertNotIn("1929", res[0][0])
        self.assertNotIn("dokin", res[0][0].lower())

    def test_additional_denhaag_cases(self):
        self.assertEqual(
            parse_denhaag_names("Levij Barend van Hoorn, Anna van Hoorn-Lezer en Aäron van Hoorn"),
            [
                ("Levij Barend van Hoorn", None, None),
                ("Anna van Hoorn-Lezer", None, None),
                ("Aäron van Hoorn", None, None),
            ],
        )
        self.assertEqual(
            parse_denhaag_names("Leonardus Josephus Maria 'Leo'Coppes"),
            [("Leonardus Josephus Maria 'Leo' Coppes", None, None)],
        )
        self.assertEqual(parse_denhaag_names("https://www.joodsmonument.nl/nl/page/147542/emanuel-van-leeuwen"), [])
        self.assertEqual(parse_denhaag_names("+Nederlanders bij Duits Verzet in Duitsland ? wordpress.com"), [])


if __name__ == "__main__":
    unittest.main()
