# -*- coding: utf-8 -*-
"""Test thẻ đồng hồ."""

import re
import unittest
from datetime import datetime, timezone

from helpers import SCRIPTS, assert_valid_svg  # noqa: F401

from svgkit import clock_card, i18n
from svgkit.clock import _greeting_key
from svgkit.palette import get_palette

DT = datetime(2026, 11, 19, 15, 4, 5)

RE_NOW_HOUR = re.compile(r'class="clockTime nowSlot" x="308"[^>]*>(\d+)<')
RE_NOW_MIN = re.compile(r'class="clockTime nowSlot" x="324"[^>]*>(\d+)<')
RE_HOUR_SLOT = re.compile(r'class="clockTime[^"]*" x="308"[^>]*>(\d+)<')
RE_MIN_SLOT = re.compile(r'class="clockTime[^"]*" x="324"[^>]*>(\d+)<')


def now_slots(svg):
    """(giờ, phút) đang hiện sẵn — tức giờ của ảnh chụp.

    Sau khi tách thành 24 ô giờ + 60 ô phút, không còn một chuỗi "16:00"
    duy nhất để so; phải đọc đúng hai ô được đánh dấu nowSlot.
    """
    return (RE_NOW_HOUR.search(svg).group(1), RE_NOW_MIN.search(svg).group(1))


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
        self.assertEqual(now_slots(svg), ("16", "00"))
        self.assertNotIn(">09<", svg.split('x="308"')[1][:40])

    def test_naive_is_taken_as_vietnam_time(self):
        svg = self._svg(datetime(2026, 11, 19, 15, 4))
        self.assertEqual(now_slots(svg), ("15", "04"))

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
        self.assertEqual(now_slots(svg), ("00", "30"))
        self.assertIn("20/11/2026", svg)


class TestSnapshotStamp(unittest.TestCase):
    """Thẻ phải tự nói ảnh này vẽ lúc mấy giờ, để không ai nhầm là "giờ hiện tại"."""

    def test_stamp_shows_draw_time(self):
        svg = clock_card(get_palette(), DT, i18n.get("vi"))
        self.assertIn("cập nhật 15:04", svg)

    def test_stamp_is_right_aligned_in_digital_block(self):
        svg = clock_card(get_palette(), DT, i18n.get("vi"))
        self.assertIn('x="616" y="74" text-anchor="end"', svg)

    def test_stamp_is_the_only_place_holding_the_full_time(self):
        # giờ lớn giờ là 24 ô + 60 ô riêng, nên chuỗi "15:04" chỉ còn ở tem
        svg = clock_card(get_palette(), DT, i18n.get("vi"))
        self.assertEqual(svg.count("15:04"), 1)

    def test_english_stamp(self):
        svg = clock_card(get_palette(), DT, i18n.get("en"))
        self.assertIn("updated 15:04", svg)


class TestLabelNotRepeated(unittest.TestCase):
    """UTC+7 chỉ nói một lần (ở dòng phụ trên đầu thẻ), không lặp trong nhãn."""

    def test_label_is_short(self):
        svg = clock_card(get_palette(), DT, i18n.get("vi"))
        self.assertIn(">GIỜ VIỆT NAM</text>", svg)
        self.assertNotIn("GIỜ VIỆT NAM · UTC+7", svg)




class TestHoursLeft(unittest.TestCase):
    """Nhãn "còn bao lâu nữa hết ngày" cạnh thanh tiến độ."""

    def _card(self, hour, minute, lang="vi"):
        # giờ không kèm múi = giờ Việt Nam, nên khỏi phải quy đổi trong test
        return clock_card(get_palette(), datetime(2026, 11, 19, hour, minute),
                          i18n.get(lang))

    def test_counts_down_to_midnight(self):
        self.assertIn("còn 0g37", self._card(23, 23))

    def test_morning_has_a_full_day_ahead(self):
        self.assertIn("còn 16g00", self._card(8, 0))

    def test_minutes_are_zero_padded(self):
        self.assertIn("còn 1g05", self._card(22, 55))

    def test_english_label(self):
        self.assertIn("16h 00m left", self._card(8, 0, "en"))




class TestLiveTimeSlots(unittest.TestCase):
    """Ô số nhảy theo phút — phần làm đồng hồ "sống" mà không cần workflow."""

    def setUp(self):
        self.svg = clock_card(get_palette(), DT, i18n.get("vi"))

    def test_twenty_four_hour_slots(self):
        self.assertEqual(len(RE_HOUR_SLOT.findall(self.svg)), 24)

    def test_sixty_minute_slots(self):
        self.assertEqual(len(RE_MIN_SLOT.findall(self.svg)), 60)

    def test_exactly_one_slot_is_visible_by_default(self):
        self.assertEqual(self.svg.count("clockTime nowSlot"), 2)

    def test_only_the_snapshot_slot_is_marked(self):
        self.assertEqual(now_slots(self.svg), ("15", "04"))

    def test_colon_is_its_own_node(self):
        self.assertIn('x="316" y="124" text-anchor="middle"', self.svg)

    def test_minute_values_run_from_00_to_59(self):
        values = RE_MIN_SLOT.findall(self.svg)
        self.assertEqual(values, ["%02d" % v for v in range(60)])

    def test_hour_values_run_from_00_to_23(self):
        values = RE_HOUR_SLOT.findall(self.svg)
        self.assertEqual(values, ["%02d" % v for v in range(24)])



class TestLiveSlotTiming(unittest.TestCase):
    """Độ trễ phải đúng: ô hiện tại bắt đầu ngay, ô kế tiếp đúng 60 giây sau.

    Sai công thức thì đồng hồ chạy nhưng lệch — kiểu lỗi tệ nhất vì nó
    *trông* đúng."""

    def setUp(self):
        self.svg = clock_card(get_palette(), DT, i18n.get("vi"))   # 15:04:05

    def _delay(self, x, value):
        found = re.search(r'class="clockTime[^"]*" x="%d"[^>]*'
                          r'animation-delay:(-?[\d.]+)s">%s<'
                          % (x, value), self.svg)
        self.assertIsNotNone(found, "không thấy ô %s" % value)
        return float(found.group(1))

    def test_current_minute_starts_immediately(self):
        # 5 giây đã trôi qua trong phút hiện tại -> độ trễ âm đúng 5 giây
        self.assertEqual(self._delay(324, "04"), -5.0)

    def test_next_minute_waits_until_the_minute_turns(self):
        self.assertEqual(self._delay(324, "05"), 55.0)

    def test_minute_slots_cover_the_full_hour(self):
        self.assertEqual(self._delay(324, "03"), 59 * 60 - 5)

    def test_current_hour_starts_immediately(self):
        self.assertEqual(self._delay(308, "15"), -(4 * 60 + 5))

    def test_next_hour_waits_out_the_rest_of_this_one(self):
        self.assertEqual(self._delay(308, "16"), 3600 - (4 * 60 + 5))

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
