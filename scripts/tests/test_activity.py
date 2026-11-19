# -*- coding: utf-8 -*-
"""Test thẻ hoạt động contribution."""

import unittest
from datetime import date, datetime, timedelta, timezone

from helpers import SCRIPTS, assert_valid_svg  # noqa: F401

from svgkit import activity_card, i18n
from svgkit.api import _streaks
from svgkit.palette import get_palette

DT = datetime(2026, 11, 19, 15, 4, 5)


def series(counts, end=date(2026, 11, 19)):
    start = end - timedelta(days=len(counts) - 1)
    return [(start + timedelta(days=i), c) for i, c in enumerate(counts)]


CONTRIB = {
    "total": 1234,
    "days": series([0, 1, 2, 3, 0, 5, 4, 3, 2, 1, 0, 0, 6, 7]),
    "streak_current": 2,
    "streak_longest": 15,
}


class TestActivityCard(unittest.TestCase):
    def setUp(self):
        self.svg = activity_card(get_palette(), CONTRIB, DT, i18n.get())

    def test_valid(self):
        assert_valid_svg(self, self.svg, "activity")

    def test_headline_numbers(self):
        self.assertIn("1.2k", self.svg)   # tổng cả năm
        self.assertIn("CHUỖI DÀI NHẤT", self.svg)
        self.assertIn("15 ngày", self.svg)

    def test_last_14_days_only(self):
        dom = self.svg
        self.assertEqual(dom.count('class="fMono"'), 14)

    def test_english(self):
        svg = activity_card(get_palette(), CONTRIB, DT, i18n.get("en"))
        self.assertIn("CONTRIBUTION ACTIVITY", svg)
        self.assertIn("days", svg)

    def test_no_data_returns_none(self):
        self.assertIsNone(activity_card(get_palette(), None, DT, i18n.get()))
        self.assertIsNone(activity_card(get_palette(), {"days": []}, DT,
                                        i18n.get()))


class TestStreaks(unittest.TestCase):
    def test_simple(self):
        current, longest = _streaks(series([1, 1, 0, 1, 1, 1]))
        self.assertEqual(current, 3)
        self.assertEqual(longest, 3)

    def test_current_zero_when_today_empty(self):
        current, longest = _streaks(series([1, 1, 1, 0]))
        self.assertEqual(current, 0)
        self.assertEqual(longest, 3)

    def test_all_zero(self):
        self.assertEqual(_streaks(series([0, 0, 0])), (0, 0))

    def test_all_full(self):
        self.assertEqual(_streaks(series([2, 2, 2, 2])), (4, 4))


class TestAverageLineFlow(unittest.TestCase):
    def test_average_line_flows(self):
        svg = activity_card(get_palette("sky"), CONTRIB, DT, i18n.get("vi"))
        self.assertIn("dashFlow", svg)
        self.assertIn("stroke-dasharray", svg)

class TestActivityTimezone(unittest.TestCase):
    def test_stamp_is_vietnam_time(self):
        utc = datetime(2026, 11, 19, 9, 0, tzinfo=timezone.utc)
        svg = activity_card(get_palette(), CONTRIB, utc, i18n.get("vi"))
        self.assertIn("19/11 · 16:00", svg)


class TestTodayHalo(unittest.TestCase):
    """Cột hôm nay có vòng thở phía sau chấm sáng."""

    def setUp(self):
        self.svg = activity_card(get_palette(), CONTRIB, DT, i18n.get("vi"))

    def test_halo_ring_present(self):
        self.assertIn('r="11" fill="none"', self.svg)
        self.assertIn('class="pulseSlow"', self.svg)

    def test_dot_has_glow(self):
        self.assertIn('r="3.4" fill="', self.svg)
        self.assertIn('filter="url(#glow)"', self.svg)


if __name__ == "__main__":
    unittest.main()


class TestAverageLine(unittest.TestCase):
    def test_line_appears_for_mixed_data(self):
        svg = self.card([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 40])
        self.assertIn('stroke-dasharray="4 6"', svg)
        self.assertIn("TB ", svg)

    def test_no_line_when_all_equal(self):
        svg = self.card([5] * 14)
        self.assertNotIn('stroke-dasharray="4 6"', svg)

    def card(self, counts):
        import datetime as dtmod

        from svgkit import i18n
        from svgkit.activity import activity_card
        from svgkit.palette import get_palette

        base = dtmod.date(2026, 11, 19)
        days = [(base - dtmod.timedelta(days=13 - i), c) for i, c in enumerate(counts)]
        contrib = {"total": sum(counts), "days": days,
                   "streak_current": 0, "streak_longest": 3}
        return activity_card(get_palette(), contrib,
                             dtmod.datetime(2026, 11, 19, 15, 0), i18n.get("vi"))


class TestPeakLabel(unittest.TestCase):
    def test_peak_label_on_busiest_day(self):
        counts = [0, 3, 1, 2, 9, 1, 0, 0, 2, 1, 0, 0, 1, 0]
        from svgkit import i18n
        from svgkit.activity import activity_card
        from svgkit.palette import get_palette
        import datetime as dtmod

        base = dtmod.date(2026, 11, 19)
        days = [(base - dtmod.timedelta(days=13 - i), c) for i, c in enumerate(counts)]
        contrib = {"total": sum(counts), "days": days,
                   "streak_current": 0, "streak_longest": 2}
        svg = activity_card(get_palette(), contrib,
                            dtmod.datetime(2026, 11, 19, 9, 0), i18n.get("vi"))
        self.assertIn("cao nhất", svg)

    def test_no_peak_label_when_today_is_peak(self):
        import datetime as dtmod

        from svgkit import i18n
        from svgkit.activity import activity_card
        from svgkit.palette import get_palette

        base = dtmod.date(2026, 11, 19)
        counts = [1] * 13 + [9]
        days = [(base - dtmod.timedelta(days=13 - i), c) for i, c in enumerate(counts)]
        contrib = {"total": 22, "days": days, "streak_current": 1, "streak_longest": 1}
        svg = activity_card(get_palette(), contrib,
                            dtmod.datetime(2026, 11, 19, 9, 0), i18n.get("vi"))
        self.assertNotIn("cao nhất", svg)
