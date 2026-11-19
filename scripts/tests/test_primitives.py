# -*- coding: utf-8 -*-
"""Test các viên gạch: escape, rút gọn số, icon, CSS, defs, khung thẻ."""

import unittest

from helpers import SCRIPTS, assert_valid_svg  # noqa: F401

from svgkit import primitives
from svgkit.palette import get_palette


class TestEscaping(unittest.TestCase):
    def test_ampersand(self):
        self.assertEqual(primitives.esc("A & B"), "A &amp; B")

    def test_angle_brackets(self):
        self.assertEqual(primitives.esc("<b>"), "&lt;b&gt;")

    def test_quotes(self):
        self.assertEqual(primitives.esc('say "hi"'), "say &quot;hi&quot;")

    def test_vietnamese_untouched(self):
        text = "Học sinh lớp 7 · Long Xuyên"
        self.assertEqual(primitives.esc(text), text)

    def test_non_string_input(self):
        self.assertEqual(primitives.esc(42), "42")


class TestHuman(unittest.TestCase):
    def test_small_numbers(self):
        self.assertEqual(primitives.human(0), "0")
        self.assertEqual(primitives.human(999), "999")

    def test_thousands(self):
        self.assertEqual(primitives.human(1000), "1k")
        self.assertEqual(primitives.human(1284), "1.3k")

    def test_millions(self):
        self.assertEqual(primitives.human(2400000), "2.4M")

    def test_bad_input(self):
        self.assertEqual(primitives.human(None), "-")
        self.assertEqual(primitives.human("abc"), "-")

    def test_num_strips_trailing_zeros(self):
        self.assertEqual(primitives.num(12.0), "12")
        self.assertEqual(primitives.num(12.50), "12.5")


class TestIcons(unittest.TestCase):
    def test_all_icons_render(self):
        for name in primitives.ICONS:
            markup = primitives.icon(name, 10, 10, "#ffffff")
            self.assertIn("<g transform=", markup)
            self.assertNotIn("None", markup)

    def test_unknown_icon_falls_back(self):
        markup = primitives.icon("khong-co", 0, 0, "#ffffff")
        self.assertIn("circle", markup)


class TestStyle(unittest.TestCase):
    def test_css_has_no_placeholders_left(self):
        css = primitives.css_block(get_palette("emerald"))
        self.assertNotIn("@ACCENT@", css)
        self.assertNotIn("@FONT@", css)
        self.assertIn("emerald", "emerald")  # sanity

    def test_css_colors_follow_theme(self):
        sky = primitives.css_block(get_palette("sky"))
        violet = primitives.css_block(get_palette("violet"))
        self.assertNotEqual(sky, violet)
        self.assertIn("#F3EBFF", violet)   # màu tiêu đề của theme violet

    def test_defs_complete(self):
        defs = primitives.defs_block(get_palette())
        for gradient in ("bg", "edge", "titleGrad", "accentGrad", "barGrad",
                         "halo", "glow"):
            self.assertIn('id="%s"' % gradient, defs)
        self.assertNotIn("@", defs)


class TestOpenSvg(unittest.TestCase):
    def test_open_svg_parses(self):
        parts = primitives.open_svg(get_palette(), 640, 258, "test card")
        parts.append("</svg>")
        assert_valid_svg(self, "\n".join(parts))

    def test_contains_clip_and_border(self):
        markup = "\n".join(primitives.open_svg(get_palette(), 640, 258, "x"))
        self.assertIn('id="cardBody"', markup)
        self.assertIn('stroke="url(#edge)"', markup)


if __name__ == "__main__":
    unittest.main()


class TestReducedMotion(unittest.TestCase):
    def test_css_disables_animation_when_requested(self):
        from svgkit import primitives

        self.assertIn("prefers-reduced-motion", primitives.CSS)
        self.assertIn("animation: none !important", primitives.CSS)

    def test_every_animated_class_is_covered(self):
        import re

        from svgkit import primitives

        block = primitives.CSS.split("prefers-reduced-motion")[1]
        declared = set(re.findall(r"^\s*\.(\w+)\s*\{ animation:", primitives.CSS, re.M))
        for name in declared:
            self.assertIn("." + name, block, "thiếu %s trong khối giảm chuyển động" % name)
