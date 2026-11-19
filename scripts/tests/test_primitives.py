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


class TestNumbers(unittest.TestCase):
    def test_human_small(self):
        from svgkit.primitives import human

        self.assertEqual(human(0), "0")
        self.assertEqual(human(7), "7")
        self.assertEqual(human(999), "999")

    def test_human_thousands(self):
        from svgkit.primitives import human

        self.assertEqual(human(1000), "1k")
        self.assertEqual(human(3476), "3.5k")
        self.assertEqual(human(12345), "12.3k")

    def test_human_millions(self):
        from svgkit.primitives import human

        self.assertEqual(human(1200000), "1.2M")

    def test_num_trims_float(self):
        from svgkit.primitives import num

        self.assertEqual(num(12.0), "12")
        self.assertEqual(num(12.345), "12.3")


class TestEscape(unittest.TestCase):
    def test_special_characters(self):
        from svgkit.primitives import esc

        self.assertEqual(esc("a & b"), "a &amp; b")
        self.assertEqual(esc("<b>"), "&lt;b&gt;")
        self.assertEqual(esc('nói "xin chào"'), "nói &quot;xin chào&quot;")

    def test_vietnamese_untouched(self):
        from svgkit.primitives import esc

        self.assertEqual(esc("Lập trình viên tự học"), "Lập trình viên tự học")

    def test_escaped_text_stays_parseable(self):
        from helpers import parse
        from svgkit.primitives import esc

        svg = ('<svg xmlns="http://www.w3.org/2000/svg"><text>%s</text></svg>'
               % esc('5 < 7 & "8" > 6'))
        dom = parse(svg)
        node = dom.getElementsByTagName("text")[0]
        self.assertIn("<", node.firstChild.data)


class TestIcons(unittest.TestCase):
    def test_unknown_icon_is_empty(self):
        from svgkit.primitives import icon

        self.assertEqual(icon("khong-co-icon-nay", 0, 0, "#FFFFFF"), "")

    def test_known_icons_draw_path(self):
        from svgkit.primitives import ICONS, icon

        for name in ICONS:
            out = icon(name, 10, 20, "#38BDF8")
            self.assertIn("<path", out, name)
            self.assertIn("#38BDF8", out, name)
