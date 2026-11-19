# -*- coding: utf-8 -*-
"""Test bảng màu, theme và cách chấm hạng."""

import unittest

from helpers import SCRIPTS  # noqa: F401  (đảm bảo sys.path)

from svgkit.palette import (DEFAULT_THEME, THEMES, Palette, get_palette,
                            grade, lang_color, theme_names)


class TestThemes(unittest.TestCase):
    def test_default_theme_exists(self):
        self.assertIn(DEFAULT_THEME, THEMES)

    def test_every_theme_has_all_colors(self):
        for name, palette in THEMES.items():
            self.assertIsInstance(palette, Palette)
            for field in ("bg_top", "bg_bot", "panel", "stroke", "title",
                          "text", "label", "dim", "accent", "accent2",
                          "accent3", "deep"):
                value = getattr(palette, field)
                self.assertTrue(value.startswith("#"), "%s.%s không phải màu"
                                % (name, field))
                self.assertIn(len(value), (4, 7), "%s.%s sai độ dài" % (name, field))

    def test_theme_names_is_complete(self):
        self.assertEqual(sorted(theme_names()), sorted(THEMES.keys()))

    def test_unknown_theme_falls_back(self):
        self.assertEqual(get_palette("khong-co-theme-nay").name, DEFAULT_THEME)

    def test_tokens_cover_every_placeholder(self):
        tokens = get_palette().as_tokens()
        for key, value in tokens.items():
            self.assertTrue(key.startswith("@") and key.endswith("@"))
            self.assertTrue(value)


class TestGrade(unittest.TestCase):
    def test_grade_letters(self):
        self.assertEqual(grade({"stars": 0, "repos": 0, "followers": 0,
                                "commits": 0, "forks": 0})[0], "C")
        big = grade({"stars": 500, "repos": 60, "followers": 200,
                     "commits": 5000, "forks": 100})
        self.assertEqual(big[0], "S")

    def test_grade_percent_in_range(self):
        for stats in ({"stars": 0}, {"stars": 10, "repos": 3},
                      {"followers": 40, "commits": 500}):
            letter, percent = grade(stats)
            self.assertTrue(0 < percent <= 1)
            self.assertIn(letter, ("S", "A+", "A", "B+", "B", "C+", "C"))

    def test_grade_missing_keys_do_not_crash(self):
        self.assertTrue(grade({})[0])


class TestLangColor(unittest.TestCase):
    def test_known_language(self):
        self.assertEqual(lang_color("Python"), "#3572A5")

    def test_unknown_language_uses_ramp(self):
        color = lang_color("Ngôn ngữ lạ", 0)
        self.assertTrue(color.startswith("#"))

    def test_ramp_wraps_around(self):
        self.assertEqual(lang_color("Lạ", 0), lang_color("Lạ", 8))


if __name__ == "__main__":
    unittest.main()
