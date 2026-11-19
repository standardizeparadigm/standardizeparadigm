# -*- coding: utf-8 -*-
"""Test thẻ đồng hồ."""

import re
import unittest
from datetime import datetime, timezone

from helpers import SCRIPTS, assert_valid_svg  # noqa: F401

from svgkit import clock_card, i18n
from svgkit.clock import _day_arc, _greeting_key, _sun_moon
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



class TestLiveSlotRules(unittest.TestCase):
    """CSS và chế độ giảm chuyển động của các ô số."""

    def setUp(self):
        self.svg = clock_card(get_palette(), DT, i18n.get("vi"))

    def test_minute_cycle_is_one_hour(self):
        self.assertIn("slotMin 3600s linear infinite", self.svg)

    def test_hour_cycle_is_one_day(self):
        self.assertIn("animation-name: slotHour; animation-duration: 86400s",
                      self.svg)

    def test_keyframes_show_for_one_minute(self):
        # 60/3600 = 1.666%
        self.assertIn("@keyframes slotMin  { 0%, 1.666% { opacity: 1 }", self.svg)

    def test_keyframes_show_for_one_hour(self):
        # 3600/86400 = 4.166%
        self.assertIn("@keyframes slotHour { 0%, 4.166% { opacity: 1 }", self.svg)

    def test_reduced_motion_disables_the_digits(self):
        self.assertIn(".liveHour text, .liveMin text,", self.svg)



class TestFooterFitsCard(unittest.TestCase):
    """Dòng chân thẻ phải nằm gọn trong khổ 640px.

    Chữ SVG không tự xuống dòng: chuỗi quá dài chạy thẳng ra ngoài mép và
    bị cắt giữa từ. 9px với letter-spacing .3 cho khoảng 5,3px mỗi ký tự,
    chân thẻ bắt đầu ở x=254 nên còn 364px — tức khoảng 55 ký tự.
    """

    LIMIT = 56

    def test_vietnamese_footer_fits(self):
        self.assertLessEqual(len(i18n.get("vi")("clock.foot")), self.LIMIT)

    def test_english_footer_fits(self):
        self.assertLessEqual(len(i18n.get("en")("clock.foot")), self.LIMIT)

    def test_footer_text_reaches_the_card(self):
        svg = clock_card(get_palette("sky"), DT, i18n.get("vi"))
        self.assertIn(i18n.get("vi")("clock.foot"), svg)



class TestDayArc(unittest.TestCase):
    """Vòng cung tiến độ ngày: một vòng 24 giờ."""

    def _arc(self, hour, minute=0, second=0):
        return "".join(_day_arc(get_palette("sky"), 122, 140, 74, hour, minute, second))

    def test_midnight_draws_no_arc(self):
        self.assertNotIn("<path", self._arc(0))

    def test_six_hours_is_a_quarter(self):
        # 6h = 90°: điểm cuối nằm ngang bên phải tâm (122 + 95, 140).
        self.assertIn("217.00 140.00", self._arc(6))

    def test_noon_lands_at_the_bottom(self):
        self.assertIn("122.00 235.00", self._arc(12))

    def test_eighteen_hours_lands_on_the_left(self):
        self.assertIn("27.00 140.00", self._arc(18))

    def test_after_noon_uses_large_arc_flag(self):
        self.assertIn(" 0 1 ", self._arc(12))

    def test_morning_uses_small_arc_flag(self):
        self.assertIn(" 0 0 ", self._arc(6))

    def test_ring_sits_outside_the_ticks(self):
        self.assertIn('r="95"', self._arc(6))

    def test_tip_dot_pulses(self):
        self.assertIn('attributeName="r"', self._arc(9))



class TestSunMoon(unittest.TestCase):
    """Mặt trời ban ngày, trăng khuyết ban đêm — cả hai đều là hình vẽ tay."""

    def test_daytime_draws_a_sun(self):
        svg = _sun_moon(get_palette("sky"), 9, 100, 100)
        self.assertIn("<circle", svg)
        self.assertEqual(svg.count("<path"), 8)      # 8 tia

    def test_night_draws_a_moon_with_a_mask(self):
        svg = _sun_moon(get_palette("sky"), 21, 100, 100)
        self.assertIn('<mask id="moonBite"', svg)
        self.assertIn('mask="url(#moonBite)"', svg)

    def test_moon_bite_is_black_on_white(self):
        svg = _sun_moon(get_palette("sky"), 21, 100, 100)
        self.assertIn('fill="#000000"', svg)
        self.assertIn('fill="#FFFFFF"', svg)

    def test_moon_has_no_degenerate_arc(self):
        # Bản cũ có 'a4.6 4.6 0 106.4 6.4 5.6 5.6 0 01-0 -0': bán kính 0.
        svg = _sun_moon(get_palette("sky"), 21, 100, 100)
        self.assertNotIn("-0 -0", svg)
        self.assertNotIn("a4.6", svg)

    def test_six_am_is_already_sun(self):
        self.assertIn("<path", _sun_moon(get_palette("sky"), 6, 0, 0))

    def test_six_pm_is_already_moon(self):
        self.assertIn("moonBite", _sun_moon(get_palette("sky"), 18, 0, 0))

    def test_icon_is_positioned_at_the_given_point(self):
        svg = _sun_moon(get_palette("sky"), 12, 300, 170)
        self.assertIn('cx="300"', svg)
        self.assertIn('cy="170"', svg)

    def test_icon_uses_the_palette_not_a_fixed_colour(self):
        for theme in ("sky", "sunset", "mono"):
            svg = _sun_moon(get_palette(theme), 21, 10, 10)
            self.assertIn(get_palette(theme).accent3, svg, theme)



class TestHands(unittest.TestCase):
    """Ba kim: giờ, phút, giây. Góc phải đúng, và phải quay liên tục."""

    def _hands(self, hour, minute, second):
        from svgkit.clock import _hands
        return "\n".join(_hands(get_palette("sky"), 100, 100, hour, minute, second))

    def test_three_hands(self):
        svg = self._hands(10, 10, 10)
        self.assertEqual(svg.count("secHand"), 1)
        self.assertEqual(svg.count("minHand"), 1)
        self.assertEqual(svg.count("hourHand"), 1)

    def test_hands_rotate_around_the_centre(self):
        svg = self._hands(10, 10, 30)
        self.assertIn("--cx", svg)
        self.assertIn("--cy", svg)

    def test_hand_lengths_differ(self):
        # Kim giờ cao 40px, kim phút 56px, kim giây dài 72px (40 -> 112).
        self.assertIn('height="40"', self._hands(3, 0, 0))
        self.assertIn('height="56"', self._hands(3, 0, 0))
        self.assertIn('d="M100 112V40"', self._hands(3, 0, 0))

    def test_second_hand_is_the_thinnest(self):
        svg = self._hands(3, 0, 0)
        self.assertIn('stroke-width="2"', svg)      # kim giây
        self.assertIn('width="4"', svg)             # kim phút
        self.assertIn('width="6"', svg)             # kim giờ

    def test_hands_start_from_a_negative_delay(self):
        # Âm để kim ở đúng vị trí ngay khung hình đầu, không quay một vòng
        # từ 12 giờ rồi mới tới giờ thật.
        svg = self._hands(3, 30, 0)
        self.assertIn("animation-delay:-12600.000s", svg)   # 3h30
        self.assertIn("animation-delay:-1800.000s", svg)    # 30 phút

    def test_midnight_and_noon_look_identical(self):
        # Kim 12 giờ không phân biệt sáng/tối — đúng như đồng hồ thật.
        self.assertEqual(self._hands(0, 0, 0), self._hands(12, 0, 0))

    def test_hands_use_palette_colours(self):
        pal = get_palette("sky")
        svg = self._hands(9, 30, 15)
        self.assertIn(pal.accent3, svg)


class TestDial(unittest.TestCase):
    """Mặt số: 60 vạch phút, 12 vạch giờ, vạch giờ dài hơn."""

    def setUp(self):
        from svgkit.clock import _dial
        self.svg = "\n".join(_dial(get_palette("sky"), 100, 100, 60))

    def test_sixty_ticks(self):
        self.assertEqual(len(re.findall(r"<path|<line", self.svg)), 60)

    def test_every_tick_is_on_the_dial(self):
        xs = [float(v) for v in re.findall(r'x2="(-?\d+(?:\.\d+)?)"', self.svg)]
        if xs:
            self.assertTrue(min(xs) > 15 and max(xs) < 185, (min(xs), max(xs)))

    def test_ticks_are_inside_the_card(self):
        self.assertNotIn("NaN", self.svg)

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
