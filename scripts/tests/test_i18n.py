# -*- coding: utf-8 -*-
"""Test bộ chữ hai ngôn ngữ."""

import os
import re
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
        self.assertIn("42%", t("stats.to_next", pct=42, next="A"))

    def test_missing_format_arg_does_not_crash(self):
        self.assertIn("{pct}", i18n.get()("stats.to_next"))

    def test_weekday_names(self):
        self.assertEqual(i18n.get("vi").weekday(3), "Thứ Năm")
        self.assertEqual(i18n.get("en").weekday(0), "Monday")
        self.assertEqual(i18n.get("vi").weekday(6), "Chủ Nhật")




class TestStringHygiene(unittest.TestCase):
    """Chuỗi trong i18n phải sạch — người dùng thấy chúng nguyên văn."""

    def _strings(self):
        for lang, table in i18n.STRINGS.items():
            for key, value in table.items():
                yield lang, key, value

    def test_no_trailing_spaces(self):
        for lang, key, value in self._strings():
            self.assertEqual(value, value.strip(), "%s/%s" % (lang, key))

    def test_no_double_spaces(self):
        for lang, key, value in self._strings():
            self.assertNotIn("  ", value, "%s/%s" % (lang, key))

    def test_all_vietnamese_diacritics_are_precomposed(self):
        # Dấu rời (NFD) hiện thành ô vuông trong vài font hệ thống.
        import unicodedata
        for lang, key, value in self._strings():
            self.assertEqual(value, unicodedata.normalize("NFC", value),
                             "%s/%s" % (lang, key))

    def test_keys_never_start_or_end_with_a_dot(self):
        for lang, key, value in self._strings():
            self.assertFalse(key.startswith(".") or key.endswith("."), key)

    def test_no_placeholder_without_a_name(self):
        for lang, key, value in self._strings():
            self.assertNotIn("{}", value, "%s/%s" % (lang, key))

    def test_english_strings_have_no_vietnamese_letters(self):
        vietnamese = "ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ"
        for key, value in i18n.STRINGS["en"].items():
            lowered = value.lower()
            for letter in vietnamese:
                self.assertNotIn(letter, lowered, "en/%s" % key)



class TestKeyHygiene(unittest.TestCase):
    """Tên khoá và cách dùng placeholder."""

    def test_keys_are_namespaced(self):
        for key in i18n.STRINGS["vi"]:
            self.assertIn(".", key, key)

    def test_placeholders_are_lowercase_names(self):
        for key, text in i18n.STRINGS["vi"].items():
            for name in re.findall(r"\{(\w+)\}", text):
                self.assertTrue(name.islower(), "%s: {%s}" % (key, name))

    def test_no_placeholder_is_repeated(self):
        for key, text in i18n.STRINGS["vi"].items():
            names = re.findall(r"\{(\w+)\}", text)
            self.assertEqual(len(names), len(set(names)), key)

    def test_no_percent_formatting_left(self):
        # %s / %d sẽ làm Translator.format ném KeyError khó hiểu.
        for key, text in i18n.STRINGS["vi"].items():
            self.assertNotRegex(text, r"%[sdrf]", key)

    def test_extra_arguments_are_ignored(self):
        # Gọi thừa tham số không được làm sập ảnh.
        self.assertIsInstance(i18n.get()("hero.title", unused=1), str)



class TestNoDeadStrings(unittest.TestCase):
    """Khoá dịch không ai dùng là bản dịch chết — vẫn phải dịch, vẫn sai."""

    def _corpus(self):
        root = SCRIPTS
        text = []
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d != "__pycache__" and d != "tests"]
            for name in sorted(files):
                if name.endswith((".py", ".md")) and name != "i18n.py":
                    with open(os.path.join(base, name), encoding="utf-8") as f:
                        text.append(f.read())
        return "\n".join(text)

    def test_every_key_is_referenced_somewhere(self):
        corpus = self._corpus()
        dead = sorted(key for key in i18n.STRINGS["vi"]
                      if ('"%s"' % key) not in corpus)
        self.assertEqual(dead, [])

if __name__ == "__main__":
    unittest.main()


class TestStatusStrings(unittest.TestCase):
    """Chuỗi của dải trạng thái phải có đủ ở cả hai ngôn ngữ."""

    KEYS = ("status.title", "status.desc", "status.foot", "status.passing",
            "status.failing", "status.running", "status.none", "status.missing",
            "status.unknown")

    def test_all_keys_in_both_languages(self):
        for lang in ("vi", "en"):
            t = i18n.get(lang)
            for key in self.KEYS:
                self.assertNotEqual(t(key), key, "%s thiếu ở %s" % (key, lang))

    def test_labels_are_uppercase(self):
        t = i18n.get("vi")
        for key in ("status.passing", "status.failing", "status.running"):
            self.assertEqual(t(key), t(key).upper())

    def test_desc_accepts_stamp(self):
        text = i18n.get("vi")("status.desc", stamp="19/11 · 15:44")
        self.assertIn("19/11", text)

class TestFallbacks(unittest.TestCase):
    def test_unknown_key_returns_key(self):
        from svgkit import i18n

        self.assertEqual(i18n.get("vi")("khong.co.khoa.nay"), "khong.co.khoa.nay")

    def test_unknown_lang_falls_back(self):
        from svgkit import i18n

        self.assertEqual(i18n.get("xx").lang, i18n.DEFAULT_LANG)

    def test_placeholder_substitution(self):
        from svgkit import i18n

        text = i18n.get("vi")("stats.to_next", pct=74, next="A")
        self.assertIn("74", text)
        self.assertNotIn("{pct}", text)


class TestKeysUsedByCode(unittest.TestCase):
    def test_every_referenced_key_exists(self):
        import os
        import re

        from svgkit import i18n

        pattern = re.compile(r"""(?<!desc=)\bt\(\s*["']([a-zA-Z0-9_.]+)["']""")
        roots = [os.path.join(SCRIPTS, "svgkit"),
                 os.path.join(SCRIPTS, "generate_cards.py")]
        used = set()
        for root in roots:
            paths = ([root] if os.path.isfile(root)
                     else [os.path.join(root, f) for f in os.listdir(root)
                           if f.endswith(".py")])
            for path in paths:
                with open(path, encoding="utf-8") as handle:
                    used.update(pattern.findall(handle.read()))
        known = set(i18n.STRINGS["vi"])
        missing = sorted(key for key in used if key not in known)
        self.assertEqual(missing, [], "khoá i18n dùng mà chưa khai báo: %s" % missing)
