# -*- coding: utf-8 -*-
"""Test thẻ hoạt động contribution."""

import re
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


class TestStreaksFunction(unittest.TestCase):
    """`_streaks` tính hai con số mà thẻ in ra."""

    def test_empty_is_zero_pair(self):
        self.assertEqual(_streaks([]), (0, 0))

    def test_single_busy_day(self):
        self.assertEqual(_streaks(series([3])), (1, 1))

    def test_trailing_days_make_the_current_streak(self):
        self.assertEqual(_streaks(series([0, 2, 5, 1]))[0], 3)

    def test_zero_today_breaks_the_current_streak(self):
        self.assertEqual(_streaks(series([1, 1, 0]))[0], 0)

    def test_longest_survives_a_gap(self):
        self.assertEqual(_streaks(series([1, 1, 1, 0, 1]))[1], 3)

    def test_all_busy_is_both(self):
        self.assertEqual(_streaks(series([1, 1, 1, 1])), (4, 4))


class TestStreakRendering(unittest.TestCase):
    """Chuỗi ngày đến từ API; thẻ chỉ vẽ lại, không được bịa."""

    def _card(self, **extra):
        contrib = {"total": 42, "days": series([2, 0, 5])}
        contrib.update(extra)
        return activity_card(get_palette("sky"), contrib, DT, i18n.get("vi"))

    def test_missing_streak_renders_zero(self):
        self.assertIn('>0 ngày<', self._card())

    def test_provided_streak_reaches_the_card(self):
        svg = self._card(streak_current=8, streak_longest=14)
        self.assertIn(">8 ngày<", svg)
        self.assertIn(">14 ngày<", svg)

    def test_total_is_printed(self):
        self.assertIn(">42<", self._card())

    def test_empty_day_list_returns_none(self):
        # Hợp đồng: không có ngày nào thì trả None để tầng trên giữ ảnh cũ,
        # thay vì ghi đè bằng một biểu đồ trống.
        self.assertIsNone(activity_card(get_palette("sky"),
                                        {"total": 0, "days": []},
                                        DT, i18n.get("vi")))

    def test_none_total_is_shown_as_a_dash(self):
        # Không biết tổng thì hiện gạch, không hiện 0: 0 là một con số khẳng
        # định "năm nay chưa có contribution nào".
        svg = activity_card(get_palette("sky"),
                            {"total": None, "days": series([1])},
                            DT, i18n.get("vi"))
        self.assertIn('class="bigValue">-<', svg)



RE_BAR = re.compile(r'<rect x="([\d.]+)" y="(-?\d+)" width="([\d.]+)" '
                    r'height="([\d.]+)" rx="([\d.]+)" fill="([^"]+)"')


class TestBarGeometry(unittest.TestCase):
    """Cột biểu đồ: tỉ lệ đúng, cột 0 vẫn có chỗ đứng, không tràn lề."""

    def _card(self, counts):
        days = [(DT - timedelta(days=len(counts) - 1 - i), c)
                for i, c in enumerate(counts)]
        contrib = {"total": sum(counts), "days": days,
                   "streak_current": 1, "streak_longest": 2}
        return activity_card(get_palette("sky"), contrib, DT, i18n.get("vi"))

    def _bars(self, counts):
        svg = self._card(counts)
        bars = []
        for x, y, w, h, rx, fill in RE_BAR.findall(svg):
            # Bỏ qua nền thẻ và các ô thống kê: cột nằm trong vùng biểu đồ.
            if 22 <= float(x) <= 620 and 140 <= int(y) + float(h) <= 210:
                bars.append((float(x), int(y), float(h), fill))
        return sorted(bars)

    def test_one_bar_per_day(self):
        self.assertEqual(len(self._bars([0] * 13 + [5])), 14)

    def test_taller_count_draws_taller_bar(self):
        bars = self._bars([0] * 13 + [500])
        self.assertGreater(bars[-1][2], 60)

    def test_zero_day_keeps_a_stub(self):
        bars = self._bars([0] * 14)
        self.assertTrue(all(abs(h - 4) < 0.6 for _, _, h, _ in bars))

    def test_bars_stay_inside_the_card(self):
        for x, _, _, _ in self._bars([1] * 14):
            self.assertGreaterEqual(x, 22 - 0.1)
            self.assertLessEqual(x + 26, 618 + 0.1)

    def test_bars_are_evenly_spaced(self):
        # Toạ độ được in một chữ số thập phân nên khe có thể lệch 0.1px.
        xs = [x for x, _, _, _ in self._bars([1] * 14)]
        gaps = [b - a for a, b in zip(xs, xs[1:])]
        self.assertLess(max(gaps) - min(gaps), 0.25, gaps)

    def test_empty_history_still_draws(self):
        """14 ngày trắng vẫn phải ra ảnh, không phải workflow đỏ."""
        svg = self._card([0] * 14)
        self.assertIsNotNone(svg)
        self.assertTrue(svg.rstrip().endswith("</svg>"))

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
