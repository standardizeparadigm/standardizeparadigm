#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`api.to_vn()` — quy đổi múi giờ, chỗ dễ sai nhất của cả bộ vẽ.

Một chỗ sai ở đây làm *mọi* thẻ in sai giờ, và triệu chứng (\"ảnh lệch 7
tiếng\") lại không chỉ thẳng vào hàm này. Nên nó được test riêng, kỹ hơn
mức một hàm ba dòng thường được test.
"""

import datetime
import unittest

from helpers import SCRIPTS  # noqa: F401  (bảo đảm scripts/ nằm trong sys.path)

from svgkit.api import TZ_VN, now_vn, to_vn

UTC = datetime.timezone.utc


class TestToVn(unittest.TestCase):
    def test_none_stays_none(self):
        self.assertIsNone(to_vn(None))

    def test_naive_is_kept_untouched(self):
        # Giờ không kèm múi được coi là đã là giờ Việt Nam — đây là hợp đồng
        # quan trọng: đầu vào naive của test cũ không được dịch đi 7 tiếng.
        naive = datetime.datetime(2026, 11, 19, 15, 4)
        self.assertEqual(to_vn(naive), naive)

    def test_utc_morning_shifts_to_afternoon(self):
        out = to_vn(datetime.datetime(2026, 11, 19, 9, 0, tzinfo=UTC))
        self.assertEqual(out.hour, 16)
        self.assertEqual(out.minute, 0)

    def test_late_utc_rolls_to_next_day(self):
        out = to_vn(datetime.datetime(2026, 11, 19, 17, 30, tzinfo=UTC))
        self.assertEqual((out.day, out.hour, out.minute), (20, 0, 30))

    def test_other_offset_is_converted(self):
        tokyo = datetime.timezone(datetime.timedelta(hours=9))
        out = to_vn(datetime.datetime(2026, 11, 19, 12, 0, tzinfo=tokyo))
        self.assertEqual(out.hour, 10)

    def test_result_is_in_vietnam_zone(self):
        out = to_vn(datetime.datetime(2026, 11, 19, 9, 0, tzinfo=UTC))
        self.assertEqual(out.utcoffset(), datetime.timedelta(hours=7))
        self.assertEqual(out.tzinfo, TZ_VN)

    def test_negative_offset_does_not_lose_minutes(self):
        west = datetime.timezone(datetime.timedelta(hours=-5))
        out = to_vn(datetime.datetime(2026, 11, 19, 23, 59, tzinfo=west))
        self.assertEqual((out.day, out.hour, out.minute), (20, 11, 59))


class TestNowVn(unittest.TestCase):
    def test_now_vn_is_aware_and_in_zone(self):
        moment = now_vn()
        self.assertIsNotNone(moment.tzinfo)
        self.assertEqual(moment.utcoffset(), datetime.timedelta(hours=7))

    def test_now_vn_recent(self):
        delta = now_vn() - datetime.datetime.now(UTC)
        self.assertLess(abs(delta.total_seconds()), 5)




class TestToVnEdges(unittest.TestCase):
    """Các mốc biên của một múi giờ cố định +7, không có giờ mùa hè."""

    def test_midnight_utc_is_seven(self):
        out = to_vn(datetime.datetime(2026, 11, 19, 0, 0, tzinfo=UTC))
        self.assertEqual((out.day, out.hour), (19, 7))

    def test_last_second_of_the_day_rolls_over(self):
        out = to_vn(datetime.datetime(2026, 11, 19, 23, 59, 59, tzinfo=UTC))
        self.assertEqual((out.day, out.hour, out.minute, out.second), (20, 6, 59, 59))

    def test_month_boundary(self):
        out = to_vn(datetime.datetime(2026, 11, 30, 20, 0, tzinfo=UTC))
        self.assertEqual((out.month, out.day), (12, 1))

    def test_year_boundary(self):
        out = to_vn(datetime.datetime(2026, 12, 31, 18, 0, tzinfo=UTC))
        self.assertEqual((out.year, out.month, out.day), (2027, 1, 1))

    def test_microseconds_survive(self):
        out = to_vn(datetime.datetime(2026, 11, 19, 9, 0, 0, 250000, tzinfo=UTC))
        self.assertEqual(out.microsecond, 250000)

    def test_large_positive_offset(self):
        far = datetime.timezone(datetime.timedelta(hours=14))
        out = to_vn(datetime.datetime(2026, 11, 19, 20, 0, tzinfo=far))
        self.assertEqual(out.hour, 13)

    def test_offset_with_minutes(self):
        # +05:30 -> 15:04 giờ VN là 13:34 giờ Ấn Độ, ngược lại vẫn phải đúng.
        india = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        out = to_vn(datetime.datetime(2026, 11, 19, 13, 34, tzinfo=india))
        self.assertEqual((out.hour, out.minute), (15, 4))

if __name__ == "__main__":
    unittest.main()
