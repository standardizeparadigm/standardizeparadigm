# -*- coding: utf-8 -*-
"""Test thẻ đồng hồ."""

import unittest
from datetime import datetime

from helpers import SCRIPTS, assert_valid_svg  # noqa: F401

from svgkit import clock_card, i18n
from svgkit.clock import _greeting_key
from svgkit.palette import get_palette

DT = datetime(2026, 11, 19, 15, 4, 5)


class TestClock(unittest.TestCase):
    def setUp(self):
        self.svg = clock_card(get_palette(), DT, i18n.get())

    def test_valid(self):
        assert_valid_svg(self, self.svg, "clock")

    def test_time_and_date(self):
        self.assertIn("15:04", self.svg)
        self.assertIn("19/11/2026", self.svg)
        self.assertIn("Thứ Năm", self.svg)

    def test_day_progress(self):
        # 15:04 = 904/1440 = 62.8%
        self.assertIn("63%", self.svg)

    def test_hands_are_synced(self):
        # kim giây lệch pha âm theo số giây thật
        self.assertIn("animation-delay:-5", self.svg)
        self.assertIn("--cx:122px", self.svg)

    def test_english(self):
        svg = clock_card(get_palette(), DT, i18n.get("en"))
        self.assertIn("Thursday", svg)
        self.assertIn("VIETNAM TIME", svg)


class TestGreeting(unittest.TestCase):
    def test_ranges(self):
        self.assertEqual(_greeting_key(7), "clock.greet.morning")
        self.assertEqual(_greeting_key(12), "clock.greet.noon")
        self.assertEqual(_greeting_key(15), "clock.greet.afternoon")
        self.assertEqual(_greeting_key(20), "clock.greet.evening")
        self.assertEqual(_greeting_key(2), "clock.greet.night")

    def test_every_hour_maps(self):
        for hour in range(24):
            self.assertTrue(_greeting_key(hour).startswith("clock.greet."))


if __name__ == "__main__":
    unittest.main()


class TestDialDetails(unittest.TestCase):
    def setUp(self):
        self.svg = clock_card(get_palette(), datetime(2026, 11, 19, 15, 34, 20),
                              i18n.get("vi"))

    def test_rim_sweep_present(self):
        self.assertIn('stroke-dasharray="70 320"', self.svg)
        self.assertIn("animation-duration:18s", self.svg)

    def test_second_hand_has_counterweight(self):
        self.assertIn('r="2.6"', self.svg)

    def test_sixty_tick_marks(self):
        self.assertEqual(self.svg.count('stroke-linecap="round" opacity='), 60)
