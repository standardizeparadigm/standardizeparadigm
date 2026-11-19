# -*- coding: utf-8 -*-
"""Test bộ kiểm tra sức khỏe repo (các hàm nhận diện lỗi)."""

import unittest

from helpers import SCRIPTS  # noqa: F401

import check_repo


class TestUrlChecks(unittest.TestCase):
    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []

    def test_good_url_passes(self):
        check_repo.check_url("https://example.com/a%20b", "test")
        self.assertEqual(check_repo.errors, [])

    def test_broken_percent_escape(self):
        check_repo.check_url("https://example.com/vi%C3ean", "test")
        self.assertTrue(check_repo.errors)

    def test_bad_escape_pair(self):
        check_repo.check_url("https://example.com/%E2%8", "test")
        self.assertTrue(check_repo.errors)

    def test_space_in_url(self):
        check_repo.check_url("https://example.com/a b", "test")
        self.assertTrue(check_repo.errors)

    def test_anchor_ignored(self):
        check_repo.check_url("#about", "test")
        self.assertEqual(check_repo.errors, [])


class TestOrphanEscapes(unittest.TestCase):
    def test_detects_lost_percent(self):
        self.assertTrue(check_repo.looks_like_orphan_escape("E280A2"))
        self.assertTrue(check_repo.looks_like_orphan_escape("E29CA8"))

    def test_ignores_colour_codes(self):
        for colour in ("0D1117", "38BDF8", "0EA5E9", "7DD3FC", "0369A1"):
            self.assertFalse(check_repo.looks_like_orphan_escape(colour),
                             "nhầm mã màu %s thành escape" % colour)

    def test_ignores_odd_length(self):
        self.assertFalse(check_repo.looks_like_orphan_escape("E280A"))


class TestMojibake(unittest.TestCase):
    def test_vietnamese_is_clean(self):
        samples = ["ĐÃ trôi", "Học sinh lớp 7", "Thứ Năm", "CẬP NHẬT",
                   "cầu vồng", "TỰ HỌC"]
        for text in samples:
            self.assertIsNone(check_repo.RE_MOJIBAKE.search(text), text)

    def test_classic_mojibake_detected(self):
        # "é" bị đọc sai thành hai ký tự
        self.assertIsNotNone(check_repo.RE_MOJIBAKE.search("caf\u00c3\u00a9"))
        self.assertIsNotNone(check_repo.RE_MOJIBAKE.search("d\u00e2\u20ac\u2122"))

    def test_cjk_detected(self):
        self.assertIsNotNone(check_repo.RE_CJK.search("thanh tiến \u5ea6"))
        self.assertIsNotNone(check_repo.RE_HANGUL.search("D\uc7a1 vụ"))

    def test_no_cjk_in_vietnamese(self):
        self.assertIsNone(check_repo.RE_CJK.search("Tiến độ hiện từng cột"))


if __name__ == "__main__":
    unittest.main()


class TestAssetRefs(unittest.TestCase):
    """Mọi ./... trong Markdown phải trỏ tới file có thật."""

    def setUp(self):
        import os
        import tempfile

        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self._root = check_repo.ROOT
        check_repo.ROOT = self.root
        check_repo.errors = []
        check_repo.warnings = []

    def tearDown(self):
        check_repo.ROOT = self._root
        self.tmp.cleanup()

    def _write(self, name, body):
        import os

        path = os.path.join(self.root, name)
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(
            path
        ) else None
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(body)
        return path

    def test_existing_asset_ok(self):
        self._write("assets/a.svg", "<svg xmlns='http://www.w3.org/2000/svg'/>")
        self._write("README.md", '<img src="./assets/a.svg" alt="" />')
        check_repo.check_asset_refs()
        self.assertEqual(check_repo.errors, [])

    def test_missing_asset_flagged(self):
        self._write("README.md", '<img src="./assets/missing.svg" alt="" />')
        check_repo.check_asset_refs()
        self.assertEqual(len(check_repo.errors), 1)
        self.assertIn("missing.svg", check_repo.errors[0])

    def test_markdown_link_relative(self):
        self._write("docs/guide.md", "[readme](../README.md)")
        self._write("README.md", "# hello\n")
        check_repo.check_asset_refs()
        self.assertEqual(check_repo.errors, [])

    def test_anchor_only_ignored(self):
        self._write("README.md", '[top](#top) <a href="#stats">s</a>\n')
        check_repo.check_asset_refs()
        self.assertEqual(check_repo.errors, [])
