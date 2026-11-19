# -*- coding: utf-8 -*-
"""Test bộ chữ hai ngôn ngữ."""

import unittest

from helpers import SCRIPTS  # noqa: F401

from svgkit import i18n


class TestStrings(unittest.TestCase):
    def test_all_languages_have_same_keys(self):
        base = set(i18n.STRINGS["vi"].keys())
        for lang, table in i18n.STRINGS.items():
            self.assertEqual(set(table.keys()), base,
                             "%s thiếu/thừa khóa so với vi" % lang)

    def test_no_empty_strings(self):
        for lang, table in i18n.STRINGS.items():
            for key, value in table.items():
                self.assertTrue(value.strip(), "%s:%s rỗng" % (lang, key))

    def test_placeholders_match_across_languages(self):
        import re
        pattern = re.compile(r"\{(\w+)\}")
        for key, value in i18n.STRINGS["vi"].items():
            expected = set(pattern.findall(value))
            for lang, table in i18n.STRINGS.items():
                found = set(pattern.findall(table[key]))
                self.assertEqual(found, expected,
                                 "%s:%s lệch placeholder" % (lang, key))


class TestTranslator(unittest.TestCase):
    def test_vietnamese_default(self):
        t = i18n.get()
        self.assertEqual(t.lang, "vi")
        self.assertEqual(t("stats.rank"), "RANK")

    def test_english(self):
        t = i18n.get("en")
        self.assertEqual(t("act.days"), "days")

    def test_unknown_language_falls_back(self):
        t = i18n.get("klingon")
        self.assertEqual(t.lang, i18n.DEFAULT_LANG)

    def test_unknown_key_returns_key(self):
        self.assertEqual(i18n.get()("khong.co.khoa"), "khong.co.khoa")

    def test_formatting(self):
        t = i18n.get()
        self.assertIn("42%", t("stats.progress", pct=42))

    def test_missing_format_arg_does_not_crash(self):
        self.assertIn("{pct}", i18n.get()("stats.progress"))

    def test_weekday_names(self):
        self.assertEqual(i18n.get("vi").weekday(3), "Thứ Năm")
        self.assertEqual(i18n.get("en").weekday(0), "Monday")
        self.assertEqual(i18n.get("vi").weekday(6), "Chủ Nhật")


if __name__ == "__main__":
    unittest.main()
