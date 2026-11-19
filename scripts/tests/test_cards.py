# -*- coding: utf-8 -*-
"""Test hai thẻ dữ liệu và thẻ chờ."""

import unittest
from datetime import datetime

from helpers import SCRIPTS, assert_valid_svg  # noqa: F401

from svgkit import i18n, langs_card, stats_card, waiting_card
from svgkit.palette import get_palette

DT = datetime(2026, 11, 19, 15, 4, 5)
DATA = {
    "stars": 2, "forks": 0, "repos": 2, "followers": 3, "following": 5,
    "commits": 3476,
    "langs": {"Python": 500, "TypeScript": 300, "HTML": 100, "CSS": 50},
}


class TestStatsCard(unittest.TestCase):
    def setUp(self):
        self.svg = stats_card(get_palette(), DATA, DT, i18n.get())

    def test_valid(self):
        assert_valid_svg(self, self.svg, "stats")

    def test_shows_numbers(self):
        self.assertIn("3.5k", self.svg)      # commits được rút gọn
        self.assertIn(">2<", self.svg)       # stars
        self.assertIn("FOLLOWING", self.svg)

    def test_rank_ring_present(self):
        self.assertIn("stroke-dashoffset", self.svg)
        self.assertIn("RANK", self.svg)

    def test_missing_commits_shows_dash(self):
        svg = stats_card(get_palette(), dict(DATA, commits=None), DT, i18n.get())
        self.assertIn(">-<", svg)

    def test_english(self):
        svg = stats_card(get_palette(), DATA, DT, i18n.get("en"))
        self.assertIn("UPDATED", svg)


class TestLangsCard(unittest.TestCase):
    def setUp(self):
        self.svg = langs_card(get_palette(), DATA, DT, i18n.get())

    def test_valid(self):
        assert_valid_svg(self, self.svg, "langs")

    def test_percentages(self):
        self.assertIn("52.6%", self.svg)     # 500 / 950

    def test_sorted_by_size(self):
        self.assertLess(self.svg.index("Python"), self.svg.index("HTML"))

    def test_empty_data_falls_back(self):
        svg = langs_card(get_palette(), {"langs": {}}, DT, i18n.get())
        assert_valid_svg(self, svg, "langs-empty")
        self.assertIn("Python", svg)

    def test_long_name_truncated(self):
        data = {"langs": {"Jupyter Notebook Notebook": 10, "Go": 5}}
        svg = langs_card(get_palette(), data, DT, i18n.get())
        self.assertIn("…", svg)


class TestWaitingCard(unittest.TestCase):
    def test_valid(self):
        svg = waiting_card(get_palette(), 640, "GitHub Stats", "x", "y")
        assert_valid_svg(self, svg, "waiting")


if __name__ == "__main__":
    unittest.main()


class TestAccessibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from helpers import render_demo_all

        cls.cards = render_demo_all()

    def test_title_matches_aria_label(self):
        import re

        for name, svg in self.cards.items():
            if name == "divider.svg":
                continue          # trang trí thuần, role="presentation"
            aria = re.search(r'aria-label="([^"]*)"', svg)
            self.assertIsNotNone(aria, name)
            self.assertIn("<title>%s</title>" % aria.group(1), svg,
                          "thiếu <title> khớp aria-label trong %s" % name)

    def test_desc_present(self):
        for name, svg in self.cards.items():
            if name == "divider.svg":
                continue
            self.assertIn("<desc>", svg, "thiếu <desc> trong %s" % name)


class TestTopLanguageHighlight(unittest.TestCase):
    def test_first_language_has_ring(self):
        pal = get_palette()
        svg = langs_card(pal, {"langs": {"Python": 900, "Go": 100}}, DT, i18n.get("vi"))
        self.assertIn('r="9" fill="none"', svg)

    def test_other_languages_have_no_ring(self):
        pal = get_palette()
        svg = langs_card(pal, {"langs": {"Python": 900, "Go": 100}}, DT, i18n.get("vi"))
        self.assertEqual(svg.count('class="pulseSlow"'), 1)


class TestWaitingCard(unittest.TestCase):
    def test_guides_to_workflow(self):
        svg = waiting_card(get_palette(), 640, "GITHUB STATS",
                           i18n.get("vi")("wait.line1"),
                           i18n.get("vi")("wait.empty1"))
        self.assertIn("<svg", svg)
        self.assertIn("Profile Cards", svg)
        self.assertIn("<desc>", svg)

    def test_smaller_width_supported(self):
        svg = waiting_card(get_palette(), 420, "TITLE", "line", "line2")
        self.assertIn('width="420"', svg)
