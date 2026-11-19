# -*- coding: utf-8 -*-
"""Test đường kẻ và chân trang."""

import unittest

from helpers import SCRIPTS, assert_valid_svg  # noqa: F401

from svgkit import divider, footer, i18n
from svgkit.palette import get_palette


class TestDivider(unittest.TestCase):
    def test_valid(self):
        assert_valid_svg(self, divider(get_palette()), "divider")

    def test_has_moving_spark(self):
        self.assertIn("<animate", divider(get_palette()))

    def test_role_presentation(self):
        self.assertIn('role="presentation"', divider(get_palette()))


class TestFooter(unittest.TestCase):
    def setUp(self):
        self.svg = footer(get_palette(), i18n.get())

    def test_valid(self):
        assert_valid_svg(self, self.svg, "footer")

    def test_text(self):
        self.assertIn("Thanks for visiting", self.svg)
        self.assertIn("Keep learning", self.svg)

    def test_waves_are_clipped(self):
        self.assertIn('clip-path="url(#cardBody)"', self.svg)
        self.assertIn('class="wave"', self.svg)

    def test_wave_paths_closed(self):
        self.assertIn(" Z", self.svg)




class TestSmilReducedMotion(unittest.TestCase):
    """SMIL không tắt được bằng CSS — phải ẩn phần tử mang SMIL."""

    def test_divider_declares_the_rule(self):
        svg = divider(get_palette())
        self.assertIn("prefers-reduced-motion", svg)
        self.assertIn(".smilOnly { display: none }", svg)

    def test_divider_marks_its_sparks(self):
        svg = divider(get_palette())
        self.assertGreaterEqual(svg.count('class="smilOnly"'), 5)

    def test_footer_marks_its_bubbles(self):
        svg = footer(get_palette(), i18n.get("vi"))
        self.assertIn(".smilOnly { display: none }", svg)
        self.assertEqual(svg.count("smilOnly"), 7)

    def test_static_line_survives_reduced_motion(self):
        # đường kẻ và viên kim cương tĩnh không mang class nên vẫn hiện
        svg = divider(get_palette())
        self.assertIn('height="1.6" fill="url(#ln)"', svg)

if __name__ == "__main__":
    unittest.main()


class TestMotion(unittest.TestCase):
    def test_two_sparks_travel_both_ways(self):
        svg = divider(get_palette())
        self.assertIn('values="-120;1020"', svg)
        self.assertIn('values="1020;-120"', svg)

    def test_footer_has_bubbles(self):
        svg = footer(get_palette(), i18n.get("vi"))
        self.assertEqual(svg.count('"bubble smilOnly"'), 6)
        self.assertIn('values="0;.55;0"', svg)

    def test_travelling_dot_crosses_the_line(self):
        svg = divider(get_palette())
        self.assertIn('attributeName="cx"', svg)
        self.assertIn('values="-12;1012"', svg)      # width mặc định 1000

    def test_side_dots_breathe_out_of_phase(self):
        svg = divider(get_palette())
        self.assertIn('values=".15;.75;.15"', svg)
        self.assertIn('values=".75;.15;.75"', svg)

    def test_footer_has_twinkling_stars(self):
        svg = footer(get_palette(), i18n.get("vi"))
        self.assertEqual(svg.count('class="twinkle"'), 5)
        self.assertIn('animation-delay:-3.4s', svg)
