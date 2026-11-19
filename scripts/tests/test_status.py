#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử dải trạng thái workflow (svgkit.status)."""

import datetime
import os
import sys
import unittest
import xml.dom.minidom as minidom

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from svgkit import status, i18n  # noqa: E402
from svgkit.palette import get_palette  # noqa: E402
from svgkit.status import (GAP, MARGIN, PILL_W, STATE_STYLE, STRIP_H,  # noqa: E402
                           WORKFLOWS, human_age, status_strip, width_for)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

DT = datetime.datetime(2026, 11, 19, 15, 44, tzinfo=datetime.timezone(
    datetime.timedelta(hours=7)))


def render(rows=None, lang="vi", theme="sky"):
    rows = rows if rows is not None else [("3D CONTRIB", "passing"),
                                          ("HEALTH", "failing")]
    return status_strip(get_palette(theme), rows, DT, i18n.get(lang))


class TestLayout(unittest.TestCase):
    def test_width_grows_with_count(self):
        self.assertEqual(width_for(1), MARGIN * 2 + PILL_W)
        self.assertEqual(width_for(7), MARGIN * 2 + 7 * PILL_W + 6 * GAP)
        self.assertLess(width_for(3), width_for(4))

    def test_width_matches_viewbox(self):
        svg = render([("A", "passing")] * 5)
        dom = minidom.parseString(svg)
        root = dom.documentElement
        self.assertEqual(root.getAttribute("height"), str(STRIP_H))
        self.assertEqual(root.getAttribute("width"), str(width_for(5)))

    def test_every_row_gets_a_pill(self):
        rows = [("MỘT", "passing"), ("HAI", "failing"), ("BA", "running")]
        svg = render(rows)
        self.assertEqual(svg.count('height="40" rx="11"'), len(rows))
        for name, _state in rows:
            self.assertIn(">%s<" % name, svg)

    def test_empty_rows_still_draws(self):
        svg = render([])
        minidom.parseString(svg)
        self.assertIn("KHÔNG RÕ", svg)          # nhãn dự phòng

    def test_pills_are_inside_the_canvas(self):
        rows = [("X", "passing")] * 7
        svg = render(rows)
        last_left = MARGIN + (len(rows) - 1) * (PILL_W + GAP)
        self.assertIn('<rect x="%d" y="9"' % last_left, svg)
        self.assertLess(last_left + PILL_W, width_for(len(rows)))
        self.assertGreater(MARGIN, 0)


class TestStates(unittest.TestCase):
    def test_every_state_has_style(self):
        for state in ("passing", "failing", "running", "none", "unknown",
                      "missing"):
            self.assertIn(state, STATE_STYLE)

    def test_colors_are_distinct_for_meaning(self):
        colors = [STATE_STYLE[s][0] for s in ("passing", "failing", "running")]
        self.assertEqual(len(set(colors)), 3)

    def test_state_label_comes_from_i18n(self):
        vi = render([("X", "passing")], "vi")
        en = render([("X", "passing")], "en")
        self.assertIn("ĐẠT", vi)
        self.assertIn("PASSING", en)
        self.assertNotIn("PASSING", vi)

    def test_unknown_state_falls_back(self):
        svg = render([("X", "không-tồn-tại")])
        self.assertIn(i18n.get("vi")("status.unknown"), svg)

    def test_missing_state_says_merge(self):
        self.assertIn(i18n.get("vi")("status.missing"),
                      render([("X", "missing")]))

    def test_running_gets_spinning_arc(self):
        svg = render([("X", "running")])
        self.assertIn('class="spinDot"', svg)
        self.assertIn("stroke-dasharray", svg)
        self.assertNotIn('class="spinDot"', render([("X", "passing")]))

    def test_ring_only_for_live_states(self):
        living = render([("X", "passing")])
        dead = render([("X", "none")])
        self.assertIn('r="9" fill="none"', living)
        self.assertNotIn('r="9" fill="none"', dead)

    def test_glow_only_for_live_states(self):
        self.assertIn('filter="url(#glow)"', render([("X", "running")]))
        self.assertNotIn('filter="url(#glow)"', render([("X", "unknown")]))


class TestContent(unittest.TestCase):
    def test_desc_carries_timestamp(self):
        svg = render()
        self.assertIn("19/11", svg)
        self.assertIn("15:44", svg)

    def test_palette_colors_are_used(self):
        svg = render(theme="emerald")
        pal = get_palette("emerald")
        self.assertIn(pal.panel, svg)
        self.assertIn(pal.stroke, svg)

    def test_no_foreign_script_leaks(self):
        svg = render()
        # viết bằng escape để chính file test không chứa chuỗi mojibake
        for bad in ("\u00c3", "\u00e2\u20ac", "\u0000"):
            self.assertNotIn(bad, svg)

    def test_workflow_list_is_unique_and_complete(self):
        names = [short for _f, short in WORKFLOWS]
        self.assertEqual(len(names), len(set(names)))
        files = [f for f, _s in WORKFLOWS]
        self.assertEqual(len(files), len(set(files)))
        for filename in files:
            self.assertTrue(filename.endswith(".yml"), filename)

    def test_all_state_labels_exist_in_both_languages(self):
        for state, (_color, key) in STATE_STYLE.items():
            for lang in ("vi", "en"):
                text = i18n.get(lang)(key)
                self.assertNotEqual(text, key, "%s thiếu ở %s" % (key, lang))

    def test_each_theme_renders_valid_svg(self):
        for theme in ("sky", "emerald", "violet", "sunset", "ocean", "mono"):
            for lang in ("vi", "en"):
                minidom.parseString(render(theme=theme, lang=lang))



    def test_every_workflow_file_is_on_the_strip(self):
        """Chốt chặn cho đúng lỗi của vòng 4: thêm workflow mà quên dải."""
        folder = os.path.join(ROOT, ".github", "workflows")
        on_disk = {name for name in os.listdir(folder) if name.endswith(".yml")}
        listed = {filename for filename, _short in WORKFLOWS}
        self.assertEqual(on_disk - listed, set(), "workflow thiếu trên dải")
        self.assertEqual(listed - on_disk, set(), "dải trỏ tới file không có")

    def test_strip_order_matches_workflow_list(self):
        rows = [(short, "passing") for _f, short in WORKFLOWS]
        svg = status_strip(get_palette(), rows, DT, i18n.get("vi"))
        positions = [svg.index(">%s<" % short) for short, _s in rows]
        self.assertEqual(positions, sorted(positions))




class TestStripTimezone(unittest.TestCase):
    def test_stamp_is_vietnam_time(self):
        utc = datetime.datetime(2026, 11, 19, 9, 0,
                                tzinfo=datetime.timezone.utc)
        svg = status_strip(get_palette(), [("X", "passing")], utc,
                           i18n.get("vi"))
        self.assertIn("19/11 · 16:00", svg)




class TestHumanAge(unittest.TestCase):
    """human_age() — ba mốc: phút, giờ, ngày."""

    def setUp(self):
        self.t = i18n.get("vi")

    def test_none_is_none(self):
        self.assertIsNone(human_age(None, self.t))

    def test_under_an_hour_uses_minutes(self):
        self.assertEqual(human_age(0, self.t), "0 phút trước")
        self.assertEqual(human_age(59, self.t), "59 phút trước")

    def test_under_a_day_uses_hours(self):
        self.assertEqual(human_age(60, self.t), "1 giờ trước")
        self.assertEqual(human_age(1439, self.t), "23 giờ trước")

    def test_a_day_or_more_uses_days(self):
        self.assertEqual(human_age(1440, self.t), "1 ngày trước")
        self.assertEqual(human_age(1440 * 3 + 59, self.t), "3 ngày trước")

    def test_english_labels(self):
        en = i18n.get("en")
        self.assertEqual(human_age(5, en), "5m ago")
        self.assertEqual(human_age(120, en), "2h ago")



class TestPillAgeLabel(unittest.TestCase):
    """Nhãn tuổi chỉ hiện khi biết tuổi, và không đè lên nhãn trạng thái."""

    def setUp(self):
        self.t = i18n.get("vi")
        self.two = status_strip(get_palette(), [("A", "passing"), ("B", "failing")],
                                DT, self.t)
        self.three = status_strip(
            get_palette(), [("A", "passing", 7), ("B", "failing", None)], DT, self.t)

    def test_no_label_without_age(self):
        self.assertNotIn("phút trước", self.two)

    def test_label_appears_with_age(self):
        self.assertIn("7 phút trước", self.three)

    def test_none_age_renders_nothing(self):
        # viên B không có số phút -> không có nhãn nào cho nó
        self.assertEqual(self.three.count("trước"), 1)

    def test_two_tuple_rows_still_parse(self):
        minidom.parseString(self.two.encode("utf-8"))
        minidom.parseString(self.three.encode("utf-8"))

    def test_footer_stamp_is_separate(self):
        self.assertIn("cập nhật", self.three)



class TestSummaryCounter(unittest.TestCase):
    """Con số tổng kết ở chân dải."""

    def _strip(self, rows, lang="vi"):
        return status_strip(get_palette(), rows, DT, i18n.get(lang))

    def test_counts_passing_and_running_as_ok(self):
        rows = [("A", "passing"), ("B", "running"), ("C", "failing"),
                ("D", "missing")]
        self.assertIn("2/4 workflow ổn", self._strip(rows))

    def test_all_green(self):
        rows = [("A", "passing"), ("B", "passing")]
        self.assertIn("2/2 workflow ổn", self._strip(rows))

    def test_english_wording(self):
        rows = [("A", "passing"), ("B", "failing")]
        self.assertIn("1/2 workflows OK", self._strip(rows, "en"))

    def test_unknown_states_are_not_ok(self):
        rows = [("A", "unknown"), ("B", "none")]
        self.assertIn("0/2 workflow ổn", self._strip(rows))



class TestPillGeometry(unittest.TestCase):
    """Hai nhãn trong một viên thuốc không được chạm nhau."""

    # Ước lượng rộng: phông mono 6.8px ~4.15px/ký tự + letter-spacing .2;
    # phông đậm 10px ~6.1px/ký tự + .4. Cố tình ước RỘNG hơn thực tế một
    # chút — thà thừa khe còn hơn chạm nhau trên máy không có phông đẹp.
    def _age_width(self, text):
        return len(text) * 4.35

    def _value_width(self, text):
        return len(text) * 6.5

    def test_worst_case_labels_do_not_overlap(self):
        t = i18n.get("vi")
        value_room = 30
        for state in ("passing", "failing", "running", "none", "unknown"):
            label = t(status.STATE_STYLE[state][1])
            for minutes in (0, 59, 60, 900, 60 * 24 * 12):
                age = status.human_age(minutes, t)
                left_end = value_room + self._value_width(label)
                right_start = status.PILL_W - 9 - self._age_width(age)
                self.assertLess(left_end, right_start,
                                "%s + %s" % (label, age))

    def test_pill_is_wide_enough_for_the_longest_name(self):
        # Tên ngắn nhất trong repo là 13 ký tự ("README GARDEN").
        name_end = 30 + 13 * 5.4
        self.assertLess(name_end, status.PILL_W - 9)

    def test_width_for_grows_linearly(self):
        self.assertEqual(status.width_for(1), status.MARGIN * 2 + status.PILL_W)
        self.assertEqual(status.width_for(3) - status.width_for(2),
                         status.PILL_W + status.GAP)

    def test_svg_width_matches_width_for(self):
        rows = [("A", "passing"), ("B", "failing"), ("C", "passing")]
        svg = status.status_strip(get_palette("sky"), rows, DT, i18n.get("vi"))
        self.assertIn('width="%d"' % status.width_for(3), svg)



class TestStateStyles(unittest.TestCase):
    """Sáu trạng thái, sáu màu, sáu nhãn — không trạng thái nào vô hình."""

    STATES = ("passing", "failing", "running", "none", "missing", "unknown")

    def test_every_state_has_a_colour_and_a_key(self):
        for state in self.STATES:
            self.assertIn(state, status.STATE_STYLE)
            colour, key = status.STATE_STYLE[state]
            self.assertRegex(colour, r"^#[0-9A-Fa-f]{6}$")
            self.assertTrue(key.startswith("status."))

    def test_labels_are_distinct(self):
        t = i18n.get()
        labels = [t(status.STATE_STYLE[state][1]) for state in self.STATES]
        self.assertEqual(len(set(labels)), len(labels))

    def test_unknown_state_falls_back_instead_of_crashing(self):
        rows = [("X", "exploded"), ("Y", "passing")]
        svg = status.status_strip(get_palette("sky"), rows, DT, i18n.get())
        self.assertIn(i18n.get()("status.unknown"), svg)

    def test_running_state_carries_the_spinning_arc(self):
        rows = [("X", "running")]
        svg = status.status_strip(get_palette("sky"), rows, DT, i18n.get())
        self.assertIn('class="spinDot"', svg)

    def test_passing_state_pulses_instead_of_spinning(self):
        rows = [("X", "passing")]
        svg = status.status_strip(get_palette("sky"), rows, DT, i18n.get())
        self.assertNotIn('class="spinDot"', svg)
        self.assertIn("pulseSlow", svg)


class TestSummaryLine(unittest.TestCase):
    def test_all_passing_counts_seven(self):
        rows = [("A%d" % i, "passing") for i in range(7)]
        svg = status.status_strip(get_palette("sky"), rows, DT, i18n.get())
        self.assertIn("7/7", svg)

    def test_failures_are_not_counted_as_ok(self):
        rows = [("A", "passing"), ("B", "failing"), ("C", "none")]
        svg = status.status_strip(get_palette("sky"), rows, DT, i18n.get())
        self.assertIn("1/3", svg)

    def test_missing_counts_as_not_ok(self):
        rows = [("A", "missing"), ("B", "passing")]
        svg = status.status_strip(get_palette("sky"), rows, DT, i18n.get())
        self.assertIn("1/2", svg)

    def test_footer_mentions_the_draw_time(self):
        # Mốc có múi giờ UTC -> dải phải in theo giờ Việt Nam (+7).
        svg = status.status_strip(get_palette("sky"), [("A", "passing")],
                                  datetime.datetime(
                                      2026, 11, 19, 15, 4,
                                      tzinfo=datetime.timezone.utc),
                                  i18n.get())
        self.assertIn("19/11", svg)
        self.assertIn("22:04", svg)   # 15:04 UTC -> 22:04 giờ Việt Nam

if __name__ == "__main__":
    unittest.main()
