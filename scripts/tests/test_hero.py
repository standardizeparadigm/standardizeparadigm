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


class TestParticles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svg = hero(get_palette("sky"), DT, i18n.get("vi"))

    def test_particles_have_smil(self):
        self.assertIn('attributeName="cy"', self.svg)
        self.assertIn('values="0;.7;0"', self.svg)

    def test_particles_stay_out_of_text_block(self):
        import re

        dust = re.findall(r'<circle cx="(\d+)" cy="(\d+)" r="[\d.]+" fill="#[^"]+" '
                          r'opacity="0" class="dust"', self.svg)
        self.assertEqual(len(dust), 14)
        for cx, cy in dust:
            x, y = int(cx), int(cy)
            inside = 250 < x < 840 and 40 < y < 220
            self.assertFalse(inside, "hạt sáng rơi vào vùng chữ tại (%d, %d)" % (x, y))


class TestCorePulse(unittest.TestCase):
    def test_two_expanding_rings(self):
        svg = hero(get_palette(), DT, i18n.get("vi"))
        self.assertEqual(svg.count('values="26;86"'), 2)
        self.assertIn('values=".55;0"', svg)

    def test_rings_slower_than_second_hand(self):
        svg = hero(get_palette(), DT, i18n.get("vi"))
        self.assertIn('dur="5.2s"', svg)


class TestEveryTheme(unittest.TestCase):
    def test_all_themes_render(self):
        from svgkit.palette import theme_names

        for name in theme_names():
            svg = hero(get_palette(name), DT, i18n.get("vi"))
            self.assertIn("<svg", svg, name)
            self.assertNotIn("@", svg.split("</defs>")[-1].split("<text")[0],
                             "token chưa thay trong theme %s" % name)
