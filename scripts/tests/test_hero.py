# -*- coding: utf-8 -*-
"""Test ảnh bìa."""

import unittest
from datetime import datetime

from helpers import SCRIPTS, assert_valid_svg  # noqa: F401

from svgkit import hero, i18n
from svgkit.palette import get_palette

DT = datetime(2026, 11, 19, 15, 4, 5)


class TestHero(unittest.TestCase):
    def setUp(self):
        self.svg = hero(get_palette(), DT, i18n.get())

    def test_valid_svg(self):
        assert_valid_svg(self, self.svg, "hero")

    def test_has_title_and_subtitle(self):
        self.assertIn("Standardize Paradigm", self.svg)
        self.assertIn("Học sinh lớp 7", self.svg)

    def test_has_typing_animation(self):
        self.assertIn("typeClip0", self.svg)
        self.assertIn("repeatCount=\"indefinite\"", self.svg)

    def test_has_stamp(self):
        self.assertIn("19/11 · 15:04", self.svg)

    def test_english_variant(self):
        svg = hero(get_palette(), DT, i18n.get("en"))
        self.assertIn("Grade 7 student", svg)
        self.assertNotIn("Học sinh", svg)

    def test_theme_changes_colors(self):
        svg = hero(get_palette("sunset"), DT, i18n.get())
        self.assertIn("#FB923C", svg)

    def test_no_unreplaced_tokens(self):
        for token in ("@ACCENT@", "@FONT@", "@BGTOP@"):
            self.assertNotIn(token, self.svg)

    def test_no_emoji_dependency(self):
        # icon phải là path/circle, không phải emoji trong <text>
        self.assertNotIn("✨", self.svg)


if __name__ == "__main__":
    unittest.main()
