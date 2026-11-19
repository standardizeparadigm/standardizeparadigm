# -*- coding: utf-8 -*-
"""Test bộ kiểm tra sức khỏe repo (các hàm nhận diện lỗi)."""

import os
import shutil
import tempfile
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




class TestSvgAccessibility(unittest.TestCase):
    """SVG phải có <title>, trừ khi tự khai là ảnh trang trí."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        check_repo.checked = {"svg": 0, "md": 0, "workflow": 0, "py": 0,
                              "text": 0}
        self.tmp = tempfile.mkdtemp(prefix="svg-a11y-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _put(self, markup, name="a.svg"):
        with open(os.path.join(self.tmp, name), "w", encoding="utf-8") as fh:
            fh.write(markup)

    def _run(self):
        old = check_repo.ROOT
        check_repo.ROOT = self.tmp
        try:
            check_repo.check_svg()
        finally:
            check_repo.ROOT = old

    def test_titled_svg_passes(self):
        self._put('<svg xmlns="http://www.w3.org/2000/svg">'
                  '<title>Thẻ</title><rect/></svg>')
        self._run()
        self.assertEqual(check_repo.errors, [])

    def test_untitled_svg_is_flagged(self):
        self._put('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>')
        self._run()
        self.assertTrue(any("<title>" in e for e in check_repo.errors))

    def test_aria_hidden_svg_is_exempt(self):
        self._put('<svg xmlns="http://www.w3.org/2000/svg" '
                  'aria-hidden="true"><rect/></svg>')
        self._run()
        self.assertEqual(check_repo.errors, [])

    def test_presentation_role_svg_is_exempt(self):
        self._put('<svg xmlns="http://www.w3.org/2000/svg" '
                  'role="presentation"><rect/></svg>')
        self._run()
        self.assertEqual(check_repo.errors, [])



class TestDeadAssets(unittest.TestCase):
    """Ảnh trong assets/ không ai nhúng là ảnh chết."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="dead-assets-")
        os.makedirs(os.path.join(self.tmp, "assets"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _asset(self, name):
        with open(os.path.join(self.tmp, "assets", name), "w",
                  encoding="utf-8") as fh:
            fh.write("<svg/>")

    def _doc(self, text):
        with open(os.path.join(self.tmp, "README.md"), "w",
                  encoding="utf-8") as fh:
            fh.write(text)

    def test_referenced_asset_passes(self):
        self._asset("hero.svg")
        self._doc("![hero](./assets/hero.svg)")
        check_repo.check_dead_assets(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_unreferenced_asset_is_flagged(self):
        self._asset("orphan.svg")
        self._doc("không nhắc gì")
        check_repo.check_dead_assets(self.tmp)
        self.assertTrue(any("orphan.svg" in e for e in check_repo.errors))

    def test_reference_from_workflow_counts(self):
        os.makedirs(os.path.join(self.tmp, ".github"))
        self._asset("status.svg")
        with open(os.path.join(self.tmp, ".github", "x.yml"), "w",
                  encoding="utf-8") as fh:
            fh.write("run: python scripts/x.py --out assets/status.svg\n")
        check_repo.check_dead_assets(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_no_assets_folder_is_not_an_error(self):
        empty = tempfile.mkdtemp(prefix="no-assets-")
        try:
            check_repo.check_dead_assets(empty)
            self.assertEqual(check_repo.errors, [])
        finally:
            shutil.rmtree(empty, ignore_errors=True)



class TestWorkflowDocCoverage(unittest.TestCase):
    """Chiều ngược: mọi workflow phải có dòng trong bảng."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="cron-cover-")
        os.makedirs(os.path.join(self.tmp, ".github", "workflows"))
        os.makedirs(os.path.join(self.tmp, "docs"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _workflow(self, name, cron):
        with open(os.path.join(self.tmp, ".github", "workflows", name), "w",
                  encoding="utf-8") as handle:
            handle.write("name: x\non:\n  schedule:\n    - cron: \"%s\"\n" % cron)

    def _doc(self, text):
        with open(os.path.join(self.tmp, "docs", "WORKFLOWS.md"), "w",
                  encoding="utf-8") as handle:
            handle.write(text)

    def test_missing_row_is_flagged(self):
        self._workflow("a.yml", "*/5 * * * *")
        self._workflow("b.yml", "*/30 * * * *")
        self._doc("| `a.yml` | `*/5 * * * *` | x |\n")
        check_repo.check_workflow_docs(self.tmp)
        self.assertTrue(any("b.yml" in e for e in check_repo.errors))

    def test_every_workflow_listed_passes(self):
        self._workflow("a.yml", "*/5 * * * *")
        self._workflow("b.yml", "*/30 * * * *")
        self._doc("| `a.yml` | `*/5 * * * *` | x |\n"
                  "| `b.yml` | `*/30 * * * *` | y |\n")
        check_repo.check_workflow_docs(self.tmp)
        self.assertEqual(check_repo.errors, [])

if __name__ == "__main__":
    unittest.main()


class TestAssetRefs(unittest.TestCase):
    """Mọi ./... trong Markdown phải trỏ tới file có thật."""

    def setUp(self):
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


class TestFileHygiene(unittest.TestCase):
    """BOM / CRLF / ký tự điều khiển / UTF-8 hỏng / khoảng trắng thừa."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="hygiene-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, data):
        path = os.path.join(self.tmp, name)
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def test_clean_file_passes(self):
        self._write("ok.md", "# Tiêu đề\n\nNội dung tiếng Việt.\n".encode("utf-8"))
        check_repo.check_file_hygiene(self.tmp)
        self.assertEqual(check_repo.errors, [])
        self.assertEqual(check_repo.warnings, [])

    def test_bom_is_an_error(self):
        self._write("bom.md", check_repo.codecs.BOM_UTF8 + b"# x\n")
        check_repo.check_file_hygiene(self.tmp)
        self.assertTrue(any("BOM" in e for e in check_repo.errors))

    def test_crlf_is_an_error(self):
        self._write("crlf.py", b"print(1)\r\nprint(2)\r\n")
        check_repo.check_file_hygiene(self.tmp)
        self.assertTrue(any("CRLF" in e for e in check_repo.errors))

    def test_control_character_is_an_error(self):
        self._write("ctrl.md", "a\u0007b\n".encode("utf-8"))
        check_repo.check_file_hygiene(self.tmp)
        self.assertTrue(any("U+0007" in e for e in check_repo.errors))

    def test_invalid_utf8_is_an_error(self):
        self._write("bin.md", b"abc \xff\xfe def\n")
        check_repo.check_file_hygiene(self.tmp)
        self.assertTrue(any("UTF-8" in e for e in check_repo.errors))

    def test_trailing_space_is_only_a_warning(self):
        self._write("space.md", "# x   \n".encode("utf-8"))
        check_repo.check_file_hygiene(self.tmp)
        self.assertEqual(check_repo.errors, [])
        self.assertTrue(any("khoảng trắng thừa" in w for w in check_repo.warnings))

    def test_other_suffixes_are_ignored(self):
        self._write("image.png", b"\x89PNG\r\n\x1a\n\xff")
        check_repo.check_file_hygiene(self.tmp)
        self.assertEqual(check_repo.errors, [])


class TestWorkflowDocDrift(unittest.TestCase):
    """Bảng lịch chạy trong tài liệu phải khớp cron thật."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="cron-doc-")
        os.makedirs(os.path.join(self.tmp, ".github", "workflows"))
        os.makedirs(os.path.join(self.tmp, "docs"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _workflow(self, name, cron):
        path = os.path.join(self.tmp, ".github", "workflows", name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("name: x\non:\n  schedule:\n    - cron: \"%s\"\n" % cron)

    def _doc(self, text):
        with open(os.path.join(self.tmp, "docs", "WORKFLOWS.md"), "w",
                  encoding="utf-8") as handle:
            handle.write(text)

    def _readme(self, text):
        with open(os.path.join(self.tmp, "README.md"), "w",
                  encoding="utf-8") as handle:
            handle.write(text)

    def test_matching_cron_passes(self):
        self._workflow("a.yml", "*/5 * * * *")
        self._doc("| `a.yml` | `*/5 * * * *` | mỗi 5 phút |\n")
        check_repo.check_workflow_docs(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_stale_cron_is_flagged(self):
        self._workflow("a.yml", "*/30 * * * *")
        self._doc("| `a.yml` | `*/5 * * * *` | mỗi 5 phút |\n")
        check_repo.check_workflow_docs(self.tmp)
        self.assertTrue(any("*/5 * * * *" in e for e in check_repo.errors))

    def test_unknown_workflow_in_docs_is_flagged(self):
        self._workflow("a.yml", "*/5 * * * *")
        self._doc("| `khong-co.yml` | `*/5 * * * *` | x |\n")
        check_repo.check_workflow_docs(self.tmp)
        self.assertTrue(any("không tồn tại" in e for e in check_repo.errors))

    def test_readme_cron_must_exist_somewhere(self):
        self._workflow("a.yml", "*/5 * * * *")
        self._readme("<code>*/10 * * * *</code>\n")
        check_repo.check_workflow_docs(self.tmp)
        self.assertTrue(any("README.md" in e for e in check_repo.errors))

    def test_readme_cron_that_exists_passes(self):
        self._workflow("a.yml", "*/5 * * * *")
        self._readme("<code>*/5 * * * *</code>\n")
        check_repo.check_workflow_docs(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_cron_detection(self):
        self.assertTrue(check_repo.looks_like_cron("*/5 * * * *"))
        self.assertTrue(check_repo.looks_like_cron("0 23 * * *"))
        self.assertFalse(check_repo.looks_like_cron("mỗi 5 phút"))
        self.assertFalse(check_repo.looks_like_cron("*/5 * *"))


class TestWorkflowHygiene(unittest.TestCase):
    """Bốn quy ước an toàn của workflow."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="wf-hygiene-")
        os.makedirs(os.path.join(self.tmp, ".github", "workflows"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, text):
        with open(os.path.join(self.tmp, ".github", "workflows", "a.yml"),
                  "w", encoding="utf-8") as handle:
            handle.write(text)

    GOOD = (
        "name: x\n"
        "on:\n  schedule:\n    - cron: \"*/5 * * * *\"\n"
        "concurrency:\n  group: g\n"
        "permissions:\n  contents: write\n"
        "jobs:\n  j:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n"
        "    if: github.actor != 'github-actions[bot]'\n"
        "    steps:\n      - run: git push origin HEAD\n"
    )

    def test_good_workflow_passes(self):
        self._write(self.GOOD)
        check_repo.check_workflow_hygiene(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_missing_permissions(self):
        self._write(self.GOOD.replace("permissions:\n  contents: write\n", ""))
        check_repo.check_workflow_hygiene(self.tmp)
        self.assertTrue(any("permissions" in e for e in check_repo.errors))

    def test_schedule_needs_concurrency(self):
        self._write(self.GOOD.replace("concurrency:\n  group: g\n", ""))
        check_repo.check_workflow_hygiene(self.tmp)
        self.assertTrue(any("concurrency" in e for e in check_repo.errors))

    def test_job_needs_timeout(self):
        self._write(self.GOOD.replace("    timeout-minutes: 5\n", ""))
        check_repo.check_workflow_hygiene(self.tmp)
        self.assertTrue(any("timeout-minutes" in e for e in check_repo.errors))

    def test_push_needs_bot_guard(self):
        self._write(self.GOOD.replace(
            "    if: github.actor != 'github-actions[bot]'\n", ""))
        check_repo.check_workflow_hygiene(self.tmp)
        self.assertTrue(any("vòng lặp" in e for e in check_repo.errors))

    def test_workflow_without_push_needs_no_guard(self):
        self._write(self.GOOD.replace("      - run: git push origin HEAD\n",
                                      "      - run: echo hi\n"))
        check_repo.check_workflow_hygiene(self.tmp)
        self.assertEqual(check_repo.errors, [])
