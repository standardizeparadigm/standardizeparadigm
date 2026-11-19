# -*- coding: utf-8 -*-
"""Test thẻ đồng hồ."""

import unittest
from datetime import datetime, timezone

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


class TestVietnamTime(unittest.TestCase):
    """Đồng hồ phải luôn hiện giờ Việt Nam, kể cả khi nhận mốc UTC.

    Đây là lỗi từng làm ảnh hiện sai 7 tiếng: GitHub Actions chạy ở UTC, chỉ
    cần một chỗ quên quy đổi là sai cả ngày lẫn lời chào.
    """

    def _svg(self, dt, lang="vi"):
        return clock_card(get_palette(), dt, i18n.get(lang))

    def test_utc_becomes_vietnam_time(self):
        utc = datetime(2026, 11, 19, 9, 0, tzinfo=timezone.utc)
        svg = self._svg(utc)
        self.assertIn(">16:00<", svg)
        self.assertNotIn(">09:00<", svg)

    def test_naive_is_taken_as_vietnam_time(self):
        svg = self._svg(datetime(2026, 11, 19, 15, 4))
        self.assertIn(">15:04<", svg)

    def test_greeting_follows_converted_hour(self):
        # 09:00 UTC = 16:00 giờ VN -> "Chào buổi chiều", không phải buổi sáng
        svg = self._svg(datetime(2026, 11, 19, 9, 0, tzinfo=timezone.utc))
        self.assertIn("Chào buổi chiều", svg)

    def test_day_progress_uses_converted_time(self):
        # 09:00 UTC = 16:00 VN -> 2/3 ngày = 67%
        svg = self._svg(datetime(2026, 11, 19, 9, 0, tzinfo=timezone.utc))
        self.assertIn("67%", svg)

    def test_date_not_shifted_backwards(self):
        # 17:30 UTC ngày 19 = 00:30 ngày 20 giờ VN
        utc = datetime(2026, 11, 19, 17, 30, tzinfo=timezone.utc)
        svg = self._svg(utc)
        self.assertIn(">00:30<", svg)
        self.assertIn("20/11/2026", svg)


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

class TestTickChase(unittest.TestCase):
    """12 vạch giờ sáng lần lượt như đèn chạy."""

    def setUp(self):
        self.svg = clock_card(get_palette(), DT, i18n.get("vi"))

    def test_twelve_major_ticks_animate(self):
        self.assertEqual(self.svg.count('values=".45;1;.45"'), 12)

    def test_phases_are_spread_around_the_dial(self):
        for begin in ("0.00s", "1.50s", "3.00s", "5.50s"):
            self.assertIn('begin="%s"' % begin, self.svg)

    def test_minor_ticks_stay_still(self):
        self.assertEqual(self.svg.count('stroke-width="1" stroke-linecap="round" opacity=".55"'),
                         48)
