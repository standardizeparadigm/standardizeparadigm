#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử dải trạng thái workflow (svgkit.status)."""

import datetime
import os
import sys
import unittest
import xml.dom.minidom as minidom

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from svgkit import i18n  # noqa: E402
from svgkit.palette import get_palette  # noqa: E402
from svgkit.status import (GAP, MARGIN, PILL_W, STATE_STYLE, STRIP_H,  # noqa: E402
                           WORKFLOWS, status_strip, width_for)

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
        for bad in ("Ã", "â€", "\\u"):
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


if __name__ == "__main__":
    unittest.main()
