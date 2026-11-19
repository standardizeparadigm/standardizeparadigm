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


if __name__ == "__main__":
    unittest.main()
