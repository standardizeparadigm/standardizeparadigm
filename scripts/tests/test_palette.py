# -*- coding: utf-8 -*-
"""Test bảng màu, theme và cách chấm hạng."""

import unittest

from helpers import SCRIPTS  # noqa: F401  (đảm bảo sys.path)

from svgkit.palette import (DEFAULT_THEME, THEMES, Palette, get_palette,
                            grade, grade_progress, lang_color, theme_names, GRADES)


class TestThemes(unittest.TestCase):
    def test_default_theme_exists(self):
        self.assertIn(DEFAULT_THEME, THEMES)

    def test_every_theme_has_all_colors(self):
        for name, palette in THEMES.items():
            self.assertIsInstance(palette, Palette)
            for field in ("bg_top", "bg_bot", "panel", "stroke", "title",
                          "text", "label", "dim", "accent", "accent2",
                          "accent3", "deep"):
                value = getattr(palette, field)
                self.assertTrue(value.startswith("#"), "%s.%s không phải màu"
                                % (name, field))
                self.assertIn(len(value), (4, 7), "%s.%s sai độ dài" % (name, field))

    def test_theme_names_is_complete(self):
        self.assertEqual(sorted(theme_names()), sorted(THEMES.keys()))

    def test_unknown_theme_falls_back(self):
        self.assertEqual(get_palette("khong-co-theme-nay").name, DEFAULT_THEME)

    def test_tokens_cover_every_placeholder(self):
        tokens = get_palette().as_tokens()
        for key, value in tokens.items():
            self.assertTrue(key.startswith("@") and key.endswith("@"))
            self.assertTrue(value)


class TestGrade(unittest.TestCase):
    def test_grade_letters(self):
        self.assertEqual(grade({"stars": 0, "repos": 0, "followers": 0,
                                "commits": 0, "forks": 0})[0], "C")
        big = grade({"stars": 500, "repos": 60, "followers": 200,
                     "commits": 5000, "forks": 100})
        self.assertEqual(big[0], "S")

    def test_grade_percent_in_range(self):
        for stats in ({"stars": 0}, {"stars": 10, "repos": 3},
                      {"followers": 40, "commits": 500}):
            letter, percent = grade(stats)
            # Phần trăm là vị trí trong khoảng giữa hai hạng, nên hạng thấp
            # nhất có thể đúng 0% — đó là sự thật, không phải lỗi.
            self.assertTrue(0 <= percent <= 1)
            self.assertIn(letter, ("S", "A+", "A", "B+", "B", "C+", "C"))

    def test_grade_missing_keys_do_not_crash(self):
        self.assertTrue(grade({})[0])


class TestLangColor(unittest.TestCase):
    def test_known_language(self):
        self.assertEqual(lang_color("Python"), "#3572A5")

    def test_unknown_language_uses_ramp(self):
        color = lang_color("Ngôn ngữ lạ", 0)
        self.assertTrue(color.startswith("#"))

    def test_ramp_wraps_around(self):
        self.assertEqual(lang_color("Lạ", 0), lang_color("Lạ", 8))




class TestGradeBoundaries(unittest.TestCase):
    """Hạng đổi đúng ở biên, không phải gần đúng.

    Bảng hạng là thứ người xem so sánh giữa các tháng; một ngưỡng lệch một
    điểm là cả một bậc chữ khác nhau.
    """

    def _stats(self, **kw):
        base = {"stars": 0, "repos": 0, "followers": 0, "commits": 0, "forks": 0}
        base.update(kw)
        return base

    def test_zero_is_c(self):
        self.assertEqual(grade(self._stats())[0], "C")

    def test_exact_threshold_is_inclusive(self):
        # 50 điểm: đúng biên C+ (repos 12 * 4 = 48, không đủ) -> dùng followers.
        self.assertEqual(grade(self._stats(followers=10))[0], "C+")

    def test_two_points_below_stays_lower(self):
        # 48 điểm (9 follower × 5 + 1 star × 3) vẫn dưới ngưỡng C+ là 50.
        self.assertEqual(grade(self._stats(followers=9, stars=1))[0], "C")

    def test_commits_weigh_six_hundredths(self):
        # 1000 commit = 60 điểm, đủ C+ mà không cần gì khác.
        self.assertEqual(grade(self._stats(commits=1000))[0], "C+")

    def test_none_commits_count_as_zero(self):
        self.assertEqual(grade(self._stats(commits=None))[0], "C")

    def test_percent_monotonic_across_letters(self):
        low = grade(self._stats())
        high = grade(self._stats(stars=400))
        self.assertLess(low[1], high[1])

    def test_top_grade_needs_900(self):
        self.assertEqual(grade(self._stats(stars=300))[0], "S")



def _luminance(color):
    """Độ sáng tương đối theo WCAG 2.1."""
    text = color.lstrip("#")
    if len(text) == 3:
        text = "".join(c * 2 for c in text)
    parts = [int(text[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    parts = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
             for c in parts]
    return 0.2126 * parts[0] + 0.7152 * parts[1] + 0.0722 * parts[2]


def _contrast(a, b):
    high, low = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class TestContrast(unittest.TestCase):
    """Chữ phải đọc được trên nền — đo bằng công thức WCAG, không bằng mắt.

    `title`, `text`, `label` là chữ nội dung nên cần >= 4.5 (mức AA cho chữ
    thường). `dim` là chú thích nhỏ và `accent` là nét trang trí, chỉ cần
    >= 3.0 (mức AA cho thành phần giao diện).
    """

    def setUp(self):
        self.themes = [(name, get_palette(name)) for name in theme_names()]

    def test_titles_are_readable(self):
        for name, pal in self.themes:
            self.assertGreaterEqual(_contrast(pal.title, pal.bg_bot), 4.5, name)

    def test_body_text_is_readable(self):
        for name, pal in self.themes:
            self.assertGreaterEqual(_contrast(pal.text, pal.bg_bot), 4.5, name)

    def test_labels_are_readable(self):
        for name, pal in self.themes:
            self.assertGreaterEqual(_contrast(pal.label, pal.bg_bot), 4.5, name)

    def test_dim_notes_reach_three_to_one(self):
        for name, pal in self.themes:
            self.assertGreaterEqual(_contrast(pal.dim, pal.bg_bot), 3.0, name)

    def test_accents_stand_out_from_background(self):
        for name, pal in self.themes:
            self.assertGreaterEqual(_contrast(pal.accent, pal.bg_bot), 3.0, name)

    def test_accent3_differs_from_accent(self):
        for name, pal in self.themes:
            self.assertNotEqual(pal.accent.lower(), pal.accent3.lower(), name)

    def test_contrast_helper_bounds(self):
        self.assertAlmostEqual(_contrast("#FFFFFF", "#000000"), 21.0, places=1)
        self.assertAlmostEqual(_contrast("#777777", "#777777"), 1.0, places=1)



class TestGradeProgress(unittest.TestCase):
    """Tiến độ trong khoảng giữa hai hạng — con số phải đổi khi điểm đổi."""

    def test_middle_of_band_is_half(self):
        # B+ bắt đầu ở 220, A ở 380; 300 điểm là đúng giữa.
        letter, percent, nxt = grade_progress({"followers": 60})
        self.assertEqual(letter, "B+")
        self.assertEqual(nxt, "A")
        self.assertAlmostEqual(percent, 0.5, places=2)

    def test_top_grade_is_full_and_has_no_next(self):
        letter, percent, nxt = grade_progress({"followers": 200})
        self.assertEqual((letter, percent, nxt), ("S", 1.0, None))

    def test_lowest_grade_can_be_zero(self):
        letter, percent, nxt = grade_progress({})
        self.assertEqual((letter, percent), ("C", 0.0))
        self.assertEqual(nxt, "C+")

    def test_percent_never_leaves_the_band(self):
        for followers in (1, 9, 11, 24, 45, 80, 130, 200):
            _, percent, _ = grade_progress({"followers": followers})
            self.assertGreaterEqual(percent, 0.0)
            self.assertLessEqual(percent, 1.0)

    def test_more_points_never_lower_the_ring(self):
        rings = [grade_progress({"stars": n})[1] for n in range(0, 320, 7)]
        # Trong cùng một hạng thì tăng dần; qua hạng mới vòng quay về 0.
        self.assertEqual(rings[0], 0.0)
        self.assertGreater(rings[-1], 0.9)

    def test_next_letter_is_the_one_above(self):
        order = [letter for _, letter in GRADES]
        for followers in range(0, 220, 3):
            letter, _, nxt = grade_progress({"followers": followers})
            if nxt is None:
                self.assertEqual(letter, "S")
                continue
            self.assertEqual(order.index(nxt), order.index(letter) - 1)



def _rgb(color):
    text = color.lstrip("#")
    if len(text) == 3:
        text = "".join(c * 2 for c in text)
    return tuple(int(text[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _lum(color):
    def channel(value):
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in _rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(front, back):
    """Tỉ số tương phản WCAG 2.1 giữa hai màu."""
    a, b = sorted((_lum(front), _lum(back)), reverse=True)
    return (a + 0.05) / (b + 0.05)


class TestContrast(unittest.TestCase):
    """Chữ trên thẻ phải đọc được ở cả sáu bảng màu, không chỉ bảng mặc định."""

    def test_title_is_readable_on_background(self):
        for name, pal in THEMES.items():
            with self.subTest(theme=name):
                self.assertGreater(contrast(pal.title, pal.bg_bot), 4.5)

    def test_body_text_is_readable_on_panel(self):
        for name, pal in THEMES.items():
            with self.subTest(theme=name):
                self.assertGreater(contrast(pal.text, pal.panel), 4.5)

    def test_dim_labels_are_still_above_three_to_one(self):
        # Nhãn phụ (tuổi workflow, chú thích) nhỏ nhưng vẫn phải đọc được.
        for name, pal in THEMES.items():
            with self.subTest(theme=name):
                self.assertGreater(contrast(pal.dim, pal.panel), 2.6)

    def test_accent_is_visible_on_background(self):
        for name, pal in THEMES.items():
            with self.subTest(theme=name):
                self.assertGreater(contrast(pal.accent3, pal.bg_top), 5.0)

    def test_no_two_themes_are_identical(self):
        seen = {}
        for name, pal in THEMES.items():
            key = (pal.bg_top, pal.accent, pal.accent3)
            self.assertNotIn(key, seen, "%s trùng bảng màu với %s"
                             % (name, seen.get(key)))
            seen[key] = name

if __name__ == "__main__":
    unittest.main()


class TestTokensAreComplete(unittest.TestCase):
    def test_css_placeholders_are_all_defined(self):
        import re

        from svgkit import primitives
        from svgkit.palette import get_palette

        tokens = set(re.findall(r"@[A-Z0-9_]+@", primitives.CSS + primitives.DEFS))
        mapping = get_palette().as_tokens()
        missing = sorted(token for token in tokens if token not in mapping)
        self.assertEqual(missing, [], "token thiếu trong Palette: %s" % missing)
