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



class TestFixableText(unittest.TestCase):
    """`--fix` chỉ sửa thứ vô hình, không đổi nội dung."""

    def test_crlf_becomes_lf(self):
        self.assertEqual(check_repo.fixable_text("a\r\nb\r\n"), "a\nb\n")

    def test_bom_is_removed(self):
        self.assertEqual(check_repo.fixable_text("\ufeffa"), "a\n")

    def test_trailing_spaces_are_stripped(self):
        self.assertEqual(check_repo.fixable_text("a   \nb\t\n"), "a\nb\n")

    def test_missing_final_newline_is_added(self):
        self.assertEqual(check_repo.fixable_text("a"), "a\n")

    def test_extra_blank_lines_at_end_collapse(self):
        self.assertEqual(check_repo.fixable_text("a\n\n\n"), "a\n")

    def test_vietnamese_text_is_untouched(self):
        text = "Dải trạng thái — ĐẠT · 9 giờ trước\n"
        self.assertEqual(check_repo.fixable_text(text), text)

    def test_indentation_is_preserved(self):
        self.assertEqual(check_repo.fixable_text("  a\n    b\n"), "  a\n    b\n")



class TestFixTextFiles(unittest.TestCase):
    """fix_text_files() chạy trên thư mục thật, bỏ qua file nhị phân."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="fix-files-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _put(self, name, text, mode="w"):
        path = os.path.join(self.tmp, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode, encoding=None if "b" in mode else "utf-8",
                  newline="" if "b" not in mode else None) as handle:
            handle.write(text)
        return path

    def test_dirty_file_is_rewritten(self):
        path = self._put("a.md", "dòng  \r\ncuối")
        changed = check_repo.fix_text_files(self.tmp)
        self.assertEqual(len(changed), 1)
        with open(path, encoding="utf-8", newline="") as handle:
            self.assertEqual(handle.read(), "dòng\ncuối\n")

    def test_clean_repo_reports_nothing(self):
        self._put("a.md", "sạch\n")
        self.assertEqual(check_repo.fix_text_files(self.tmp), [])

    def test_second_run_is_a_no_op(self):
        self._put("a.md", "x  \r\n")
        check_repo.fix_text_files(self.tmp)
        self.assertEqual(check_repo.fix_text_files(self.tmp), [])

    def test_binary_and_skipped_dirs_are_ignored(self):
        self._put("image.png", b"\x89PNG\r\n", mode="wb")
        self._put(".git/config", "a\r\n")
        self.assertEqual(check_repo.fix_text_files(self.tmp), [])



class TestTestClaims(unittest.TestCase):
    """Câu 'hơn N unit test' trong tài liệu."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="claims-")
        os.makedirs(os.path.join(self.tmp, "scripts", "tests"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _tests(self, count):
        body = "".join("    def test_%d(self):\n        pass\n" % i
                       for i in range(count))
        with open(os.path.join(self.tmp, "scripts", "tests", "test_x.py"), "w",
                  encoding="utf-8") as handle:
            handle.write("import unittest\n\n\nclass T(unittest.TestCase):\n" + body)

    def _doc(self, text):
        with open(os.path.join(self.tmp, "README.md"), "w",
                  encoding="utf-8") as handle:
            handle.write(text)

    def test_accurate_claim_passes(self):
        self._tests(150)
        self._doc("hơn 100 unit test")
        check_repo.check_test_claims(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_claim_above_reality_is_flagged(self):
        self._tests(40)
        self._doc("hơn 100 unit test")
        check_repo.check_test_claims(self.tmp)
        self.assertTrue(any("chỉ có 40" in e for e in check_repo.errors))

    def test_stale_claim_is_flagged(self):
        self._tests(400)
        self._doc("hơn 100 unit test")
        check_repo.check_test_claims(self.tmp)
        self.assertTrue(any("hãy nâng lên" in e for e in check_repo.errors))

    def test_real_test_count_ignores_non_test_functions(self):
        self._tests(3)
        check_repo.check_test_claims(self.tmp)
        self.assertEqual(check_repo.real_test_count(self.tmp), 3)



class TestOrphanDocs(unittest.TestCase):
    """Tài liệu trong docs/ phải được dẫn tới từ đâu đó."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="orphan-")
        os.makedirs(os.path.join(self.tmp, "docs"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _put(self, name, text, folder=""):
        path = os.path.join(self.tmp, folder, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def test_linked_doc_passes(self):
        self._put("README.md", "xem [kiến trúc](docs/ARCHITECTURE.md)")
        self._put("ARCHITECTURE.md", "# Kiến trúc\n", "docs")
        check_repo.check_orphan_docs(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_unlinked_doc_is_flagged(self):
        self._put("README.md", "không nhắc gì")
        self._put("THEMES.md", "# Bảng màu\n", "docs")
        check_repo.check_orphan_docs(self.tmp)
        self.assertTrue(any("THEMES.md" in e for e in check_repo.errors))

    def test_readme_and_changelog_are_exempt(self):
        self._put("README.md", "a")
        self._put("CHANGELOG.md", "b")
        check_repo.check_orphan_docs(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_doc_can_be_linked_from_another_doc(self):
        self._put("README.md", "[faq](docs/FAQ.md)")
        self._put("FAQ.md", "xem [themes](THEMES.md)", "docs")
        self._put("THEMES.md", "# Bảng màu\n", "docs")
        check_repo.check_orphan_docs(self.tmp)
        self.assertEqual(check_repo.errors, [])



class TestSvgBudget(unittest.TestCase):
    """Mỗi ảnh trong assets/ phải nhẹ hơn ngân sách."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="budget-")
        os.makedirs(os.path.join(self.tmp, "assets"))
        os.makedirs(os.path.join(self.tmp, "profile-3d-contrib"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _svg(self, name, size, folder="assets"):
        path = os.path.join(self.tmp, folder, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("<svg>" + "x" * size + "</svg>")

    def test_small_asset_passes(self):
        self._svg("a.svg", 100)
        check_repo.check_svg_budget(self.tmp, limit=1000)
        self.assertEqual(check_repo.errors, [])

    def test_oversized_asset_is_flagged(self):
        self._svg("a.svg", 2000)
        check_repo.check_svg_budget(self.tmp, limit=1000)
        self.assertTrue(any("vượt ngân sách" in e for e in check_repo.errors))

    def test_third_party_folder_is_out_of_scope(self):
        self._svg("big.svg", 5000, folder="profile-3d-contrib")
        check_repo.check_svg_budget(self.tmp, limit=1000)
        self.assertEqual(check_repo.errors, [])

    def test_default_budget_is_forty_kilobytes(self):
        self.assertEqual(check_repo.SVG_BUDGET, 40 * 1024)



class TestModuleDocstrings(unittest.TestCase):
    """Luật docstring đầu file."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="docstring-")
        os.makedirs(os.path.join(self.tmp, "scripts", "svgkit"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _py(self, name, text):
        with open(os.path.join(self.tmp, "scripts", name), "w",
                  encoding="utf-8") as handle:
            handle.write(text)

    def test_docstring_passes(self):
        self._py("a.py", '"""Vì sao file này tồn tại."""\nimport os\n')
        check_repo.check_module_docstrings(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_shebang_then_docstring_passes(self):
        self._py("a.py", '#!/usr/bin/env python3\n"""doc"""\n')
        check_repo.check_module_docstrings(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_missing_docstring_is_flagged(self):
        self._py("a.py", "import os\n")
        check_repo.check_module_docstrings(self.tmp)
        self.assertTrue(any("docstring" in e for e in check_repo.errors))

    def test_nested_package_files_are_checked(self):
        path = os.path.join(self.tmp, "scripts", "svgkit", "b.py")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("x = 1\n")
        check_repo.check_module_docstrings(self.tmp)
        self.assertTrue(any("svgkit/b.py" in e for e in check_repo.errors))



class TestReadmeLength(unittest.TestCase):
    """README phải ngắn."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="readme-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _readme(self, lines):
        with open(os.path.join(self.tmp, "README.md"), "w",
                  encoding="utf-8") as handle:
            handle.write("\n".join("dòng %d" % i for i in range(lines)) + "\n")

    def test_short_readme_passes(self):
        self._readme(100)
        check_repo.check_readme_length(self.tmp, limit=360)
        self.assertEqual(check_repo.errors, [])

    def test_long_readme_is_flagged(self):
        self._readme(500)
        check_repo.check_readme_length(self.tmp, limit=360)
        self.assertTrue(any("vượt ngân sách" in e for e in check_repo.errors))

    def test_missing_readme_is_not_an_error(self):
        check_repo.check_readme_length(self.tmp, limit=360)
        self.assertEqual(check_repo.errors, [])

    def test_default_budget(self):
        self.assertEqual(check_repo.README_BUDGET, 360)



class TestConflictMarkers(unittest.TestCase):
    """Dấu merge còn sót."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="conflict-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _put(self, text, name="a.md"):
        with open(os.path.join(self.tmp, name), "w", encoding="utf-8") as handle:
            handle.write(text)

    def test_clean_file_passes(self):
        self._put("không có gì\n")
        check_repo.check_conflict_markers(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_marker_is_flagged(self):
        self._put("a\n<<<<<<< HEAD\nb\n=======\nc\n>>>>>>> main\n")
        check_repo.check_conflict_markers(self.tmp)
        self.assertEqual(len(check_repo.errors), 1)

    def test_one_error_per_file(self):
        self._put("<<<<<<< x\n=======\n>>>>>>>\n")
        check_repo.check_conflict_markers(self.tmp)
        self.assertEqual(len(check_repo.errors), 1)

    def test_longer_run_of_equals_is_not_a_marker(self):
        # đường kẻ Markdown 16 dấu = không phải dấu merge (8 ký tự thứ 8
        # không phải khoảng trắng), nên không được báo lỗi
        self._put("================\n")
        check_repo.check_conflict_markers(self.tmp)
        self.assertEqual(check_repo.errors, [])



class TestStalePlaces(unittest.TestCase):
    """Địa danh cũ không được quay lại."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="places-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _put(self, text, name="README.md"):
        with open(os.path.join(self.tmp, name), "w", encoding="utf-8") as handle:
            handle.write(text)

    def test_new_place_passes(self):
        self._put("Mình ở phường Kon Tum, tỉnh Quảng Ngãi.")
        check_repo.check_stale_places(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_old_place_is_flagged(self):
        self._put("Mình ở Long Xuyên, An Giang.")
        check_repo.check_stale_places(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_ascii_variant_is_flagged(self):
        self._put("based in Long Xuyen")
        check_repo.check_stale_places(self.tmp)
        self.assertTrue(any("Long Xuyen" in e for e in check_repo.errors))

    def test_filename_mentioning_place_is_flagged(self):
        self._put('<title>Long Xuyên</title>', name="hero.svg")
        check_repo.check_stale_places(self.tmp)
        self.assertTrue(check_repo.errors)



class TestTodoMarkers(unittest.TestCase):
    """TODO/FIXME trong code đã merge."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="todo-")
        os.makedirs(os.path.join(self.tmp, "scripts"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _py(self, text, name="a.py"):
        with open(os.path.join(self.tmp, "scripts", name), "w",
                  encoding="utf-8") as handle:
            handle.write(text)

    def test_clean_file_passes(self):
        self._py('"""doc"""\n\ndef f():\n    return 1\n')
        check_repo.check_todo_markers(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_todo_is_flagged(self):
        self._py('"""doc"""\n# TODO: sửa sau\n')
        check_repo.check_todo_markers(self.tmp)
        self.assertTrue(any("TODO" in e for e in check_repo.errors))

    def test_fixme_is_flagged(self):
        self._py('"""doc"""\nx = 1  # FIXME\n')
        check_repo.check_todo_markers(self.tmp)
        self.assertTrue(any("FIXME" in e for e in check_repo.errors))

    def test_noqa_line_is_exempt(self):
        self._py('"""doc"""\nimport x  # noqa: F401  TODO trong noqa\n')
        check_repo.check_todo_markers(self.tmp)
        self.assertEqual(check_repo.errors, [])



class TestWorkflowDispatch(unittest.TestCase):
    """Workflow phải chạy tay được."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="dispatch-")
        os.makedirs(os.path.join(self.tmp, ".github", "workflows"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _wf(self, name, text):
        with open(os.path.join(self.tmp, ".github", "workflows", name), "w",
                  encoding="utf-8") as handle:
            handle.write(text)

    def test_workflow_with_dispatch_passes(self):
        self._wf("a.yml", "on:\n  workflow_dispatch:\n")
        check_repo.check_workflow_dispatch(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_workflow_without_dispatch_is_flagged(self):
        self._wf("a.yml", "on:\n  push:\n")
        check_repo.check_workflow_dispatch(self.tmp)
        self.assertTrue(any("workflow_dispatch" in e for e in check_repo.errors))

    def test_missing_folder_is_not_an_error(self):
        empty = tempfile.mkdtemp(prefix="no-wf-")
        try:
            check_repo.check_workflow_dispatch(empty)
            self.assertEqual(check_repo.errors, [])
        finally:
            shutil.rmtree(empty, ignore_errors=True)



class TestShieldsWorkflowBadges(unittest.TestCase):
    """Badge workflow của shields.io từng hiện ô đỏ — không quay lại."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="shields-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _md(self, text):
        with open(os.path.join(self.tmp, "README.md"), "w",
                  encoding="utf-8") as handle:
            handle.write(text)

    def test_static_badges_pass(self):
        self._md('<img src="https://img.shields.io/badge/Grade-7-38BDF8" />')
        check_repo.check_shields_workflow_badges(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_actions_workflow_badge_is_flagged(self):
        self._md("![](https://img.shields.io/github/actions/workflow/status/a/b/x.yml)")
        check_repo.check_shields_workflow_badges(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_legacy_status_badge_is_flagged(self):
        self._md("![](https://img.shields.io/github/workflow/status/a/b/x.yml)")
        check_repo.check_shields_workflow_badges(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_own_status_svg_is_fine(self):
        self._md("![status](assets/status.svg)")
        check_repo.check_shields_workflow_badges(self.tmp)
        self.assertEqual(check_repo.errors, [])



class TestCronResolution(unittest.TestCase):
    """Cron dày hơn 5 phút: GitHub âm thầm gộp lại."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="cron-")
        os.makedirs(os.path.join(self.tmp, ".github", "workflows"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _wf(self, schedule):
        with open(os.path.join(self.tmp, ".github", "workflows", "a.yml"),
                  "w", encoding="utf-8") as handle:
            handle.write('on:\n  schedule:\n    - cron: "%s"\n'
                         '  workflow_dispatch:\n' % schedule)

    def test_five_minutes_passes(self):
        self._wf("*/5 * * * *")
        check_repo.check_cron_resolution(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_ten_minute_step_passes(self):
        self._wf("2-59/10 * * * *")
        check_repo.check_cron_resolution(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_hourly_at_minute_passes(self):
        self._wf("15 */3 * * *")
        check_repo.check_cron_resolution(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_every_minute_is_flagged(self):
        self._wf("* * * * *")
        check_repo.check_cron_resolution(self.tmp)
        self.assertTrue(any("5 phút" in e for e in check_repo.errors))

    def test_step_one_is_flagged(self):
        self._wf("*/1 * * * *")
        check_repo.check_cron_resolution(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_step_four_is_flagged(self):
        self._wf("*/4 * * * *")
        check_repo.check_cron_resolution(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_broken_expression_is_flagged(self):
        self._wf("*/5 * *")
        check_repo.check_cron_resolution(self.tmp)
        self.assertTrue(any("5 trường" in e for e in check_repo.errors))

    def test_minute_step_helper(self):
        self.assertEqual(check_repo._minute_step("*/12"), 12)
        self.assertEqual(check_repo._minute_step("*"), 0)
        self.assertIsNone(check_repo._minute_step("7"))
        self.assertIsNone(check_repo._minute_step("2-59/10"))



class TestActionPins(unittest.TestCase):
    """`uses:` phải ghim phiên bản."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="pins-")
        os.makedirs(os.path.join(self.tmp, ".github", "workflows"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _wf(self, uses):
        with open(os.path.join(self.tmp, ".github", "workflows", "a.yml"),
                  "w", encoding="utf-8") as handle:
            handle.write("jobs:\n  j:\n    steps:\n      - uses: %s\n" % uses)

    def test_major_tag_passes(self):
        self._wf("actions/checkout@v7")
        check_repo.check_action_pins(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_semver_tag_passes(self):
        self._wf("yoshi389111/github-profile-3d-contrib@v0.9.3")
        check_repo.check_action_pins(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_sha_pin_passes(self):
        self._wf("actions/checkout@" + "a" * 40)
        check_repo.check_action_pins(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_branch_is_flagged(self):
        self._wf("actions/checkout@main")
        check_repo.check_action_pins(self.tmp)
        self.assertTrue(any("ghim" in e for e in check_repo.errors))

    def test_no_version_is_flagged(self):
        self._wf("actions/checkout")
        check_repo.check_action_pins(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_local_action_is_exempt(self):
        self._wf("./.github/actions/local")
        check_repo.check_action_pins(self.tmp)
        self.assertEqual(check_repo.errors, [])



class TestHeadingLevels(unittest.TestCase):
    """Tiêu đề nhảy cấp làm mục lục lệch bậc."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="headings-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _md(self, text, name="doc.md"):
        with open(os.path.join(self.tmp, name), "w", encoding="utf-8") as handle:
            handle.write(text)

    def test_sequential_headings_pass(self):
        self._md("# T\n\n## A\n\n### A1\n\n## B\n")
        check_repo.check_heading_levels(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_skip_is_flagged(self):
        self._md("# T\n\n## A\n\n#### A1\n")
        check_repo.check_heading_levels(self.tmp)
        self.assertTrue(any("nhảy cấp" in e for e in check_repo.errors))

    def test_going_back_up_is_fine(self):
        self._md("## A\n\n### B\n\n# C\n")
        check_repo.check_heading_levels(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_hash_inside_code_fence_is_ignored(self):
        self._md("## A\n\n```\n# comment\n```\n\n### A1\n")
        check_repo.check_heading_levels(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_heading_without_space_is_not_a_heading(self):
        self._md("## A\n\n####not-a-heading\n")
        check_repo.check_heading_levels(self.tmp)
        self.assertEqual(check_repo.errors, [])



class TestJobTimeouts(unittest.TestCase):
    """Job thiếu timeout-minutes mặc định giữ runner 6 tiếng."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="timeouts-")
        os.makedirs(os.path.join(self.tmp, ".github", "workflows"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _wf(self, body):
        with open(os.path.join(self.tmp, ".github", "workflows", "a.yml"),
                  "w", encoding="utf-8") as handle:
            handle.write(body)

    def test_job_with_timeout_passes(self):
        self._wf("name: x\non:\n  workflow_dispatch:\n\njobs:\n  build:\n"
                 "    runs-on: ubuntu-latest\n    timeout-minutes: 5\n"
                 "    steps:\n      - run: echo hi\n")
        check_repo.check_job_timeouts(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_job_without_timeout_is_flagged(self):
        self._wf("name: x\non:\n  workflow_dispatch:\n\njobs:\n  build:\n"
                 "    runs-on: ubuntu-latest\n    steps:\n      - run: echo hi\n")
        check_repo.check_job_timeouts(self.tmp)
        self.assertTrue(any("timeout-minutes" in e for e in check_repo.errors))

    def test_two_jobs_one_timeout_is_flagged(self):
        self._wf("jobs:\n  a:\n    timeout-minutes: 5\n  b:\n    runs-on: x\n")
        check_repo.check_job_timeouts(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_file_without_jobs_is_ignored(self):
        self._wf("name: x\non:\n  workflow_dispatch:\n")
        check_repo.check_job_timeouts(self.tmp)
        self.assertEqual(check_repo.errors, [])



class TestSvgTextAndIds(unittest.TestCase):
    """Lỗi trong SVG mà không công cụ nào báo."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="svgtext-")
        os.makedirs(os.path.join(self.tmp, "assets"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _svg(self, body, name="a.svg"):
        with open(os.path.join(self.tmp, "assets", name), "w",
                  encoding="utf-8") as handle:
            handle.write(body)

    def test_text_with_class_passes(self):
        self._svg('<text class="big">1</text>')
        check_repo.check_svg_text_classes(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_text_without_class_is_flagged(self):
        self._svg("<text>Times New Roman</text>")
        check_repo.check_svg_text_classes(self.tmp)
        self.assertTrue(any("class" in e for e in check_repo.errors))

    def test_unique_ids_pass(self):
        self._svg('<linearGradient id="a"/><linearGradient id="b"/>')
        check_repo.check_svg_duplicate_ids(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_duplicate_id_is_flagged(self):
        self._svg('<linearGradient id="a"/><linearGradient id="a"/>')
        check_repo.check_svg_duplicate_ids(self.tmp)
        self.assertTrue(any("2 lần" in e for e in check_repo.errors))

    def test_missing_assets_folder_is_fine(self):
        empty = tempfile.mkdtemp(prefix="no-assets-")
        try:
            check_repo.check_svg_text_classes(empty)
            check_repo.check_svg_duplicate_ids(empty)
            self.assertEqual(check_repo.errors, [])
        finally:
            shutil.rmtree(empty, ignore_errors=True)



class TestSvgArtifacts(unittest.TestCase):
    """Rác Python lọt vào ảnh."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="artifacts-")
        os.makedirs(os.path.join(self.tmp, "assets"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _svg(self, body):
        with open(os.path.join(self.tmp, "assets", "a.svg"), "w",
                  encoding="utf-8") as handle:
            handle.write(body)

    def test_clean_svg_passes(self):
        self._svg('<text class="a">42</text>')
        check_repo.check_svg_artifacts(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_none_is_flagged(self):
        self._svg('<text class="a">None</text>')
        check_repo.check_svg_artifacts(self.tmp)
        self.assertTrue(any("None" in e for e in check_repo.errors))

    def test_nan_is_flagged(self):
        self._svg('<text class="a">nan%</text>')
        check_repo.check_svg_artifacts(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_traceback_is_flagged(self):
        self._svg("<desc>Traceback (most recent call last)</desc>")
        check_repo.check_svg_artifacts(self.tmp)
        self.assertTrue(any("Traceback" in e for e in check_repo.errors))



class TestMarkdownTables(unittest.TestCase):
    """Bảng lệch cột: GitHub vẫn hiện, chỉ là hiện sai."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="tables-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _md(self, text):
        with open(os.path.join(self.tmp, "d.md"), "w", encoding="utf-8") as handle:
            handle.write(text)

    def test_aligned_table_passes(self):
        self._md("| a | b |\n| :-- | :-- |\n| 1 | 2 |\n")
        check_repo.check_markdown_tables(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_missing_cell_is_flagged(self):
        self._md("| a | b |\n| :-- | :-- |\n| 1 |\n")
        check_repo.check_markdown_tables(self.tmp)
        self.assertTrue(any("cột" in e for e in check_repo.errors))

    def test_text_after_table_is_not_a_row(self):
        self._md("| a | b |\n| :-- | :-- |\n| 1 | 2 |\n\nĐoạn văn.\n")
        check_repo.check_markdown_tables(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_table_without_divider_is_ignored(self):
        self._md("| chỉ là chữ | có gạch |\n")
        check_repo.check_markdown_tables(self.tmp)
        self.assertEqual(check_repo.errors, [])



class TestSvgSafety(unittest.TestCase):
    """Ảnh tự vẽ: không gọi ra ngoài, không mang mã chạy."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="safety-")
        os.makedirs(os.path.join(self.tmp, "assets"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _svg(self, body):
        with open(os.path.join(self.tmp, "assets", "a.svg"), "w",
                  encoding="utf-8") as handle:
            handle.write(body)

    def test_namespace_is_allowed(self):
        self._svg('<svg xmlns="http://www.w3.org/2000/svg"><title>t</title></svg>')
        check_repo.check_svg_safety(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_external_image_is_flagged(self):
        self._svg('<image href="https://example.com/a.png"/>')
        check_repo.check_svg_safety(self.tmp)
        self.assertTrue(any("gọi ra ngoài" in e for e in check_repo.errors))

    def test_script_is_flagged(self):
        self._svg("<script>alert(1)</script>")
        check_repo.check_svg_safety(self.tmp)
        self.assertTrue(any("mã chạy" in e for e in check_repo.errors))

    def test_onload_is_flagged(self):
        self._svg('<svg onload="x()"></svg>')
        check_repo.check_svg_safety(self.tmp)
        self.assertTrue(check_repo.errors)



class TestDocTitles(unittest.TestCase):
    """Tài liệu không có tiêu đề: link chia sẻ hiện một câu giữa đoạn."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="titles-")
        os.makedirs(os.path.join(self.tmp, "docs"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _md(self, text, name="a.md"):
        with open(os.path.join(self.tmp, "docs", name), "w",
                  encoding="utf-8") as handle:
            handle.write(text)

    def test_h1_passes(self):
        self._md("# Tiêu đề\n\nnội dung\n")
        check_repo.check_doc_titles(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_leading_blank_lines_are_skipped(self):
        self._md("\n\n# Tiêu đề\n")
        check_repo.check_doc_titles(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_h2_first_is_flagged(self):
        self._md("## Mục\n")
        check_repo.check_doc_titles(self.tmp)
        self.assertTrue(any("tiêu đề" in e for e in check_repo.errors))

    def test_prose_first_is_flagged(self):
        self._md("Một câu mở đầu.\n\n# Tiêu đề\n")
        check_repo.check_doc_titles(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_missing_folder_is_fine(self):
        empty = tempfile.mkdtemp(prefix="no-docs-")
        try:
            check_repo.check_doc_titles(empty)
            self.assertEqual(check_repo.errors, [])
        finally:
            shutil.rmtree(empty, ignore_errors=True)



class TestExitCode(unittest.TestCase):
    """Mã thoát là thứ CI đọc — nó phải nói đúng."""

    def _main(self, argv):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_repo.main(argv)
        return code, out.getvalue()

    def test_clean_tree_exits_zero(self):
        code, text = self._main([])
        self.assertEqual(code, 0)
        self.assertIn("KẾT LUẬN: MỌI THỨ ỔN", text)

    def test_help_exits_zero(self):
        code, text = self._main(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("Dùng:", text)

    def test_main_clears_state_from_a_previous_run(self):
        # Lỗi của lượt trước không được làm lượt này báo đỏ.
        check_repo.errors.append("lỗi giả từ lượt trước")
        code, text = self._main([])
        self.assertEqual(code, 0)
        self.assertNotIn("lỗi giả", text)

    def test_summary_counts_are_reported(self):
        code, text = self._main([])
        self.assertIn("SVG", text)
        self.assertIn("workflow", text)
        self.assertIn("script Python", text)


class TestFontShorthand(unittest.TestCase):
    """`font:` viết tắt: trình duyệt hiểu, nhiều trình vẽ khác thì không."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="font-")
        os.makedirs(os.path.join(self.tmp, "assets"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _svg(self, body):
        with open(os.path.join(self.tmp, "assets", "a.svg"), "w",
                  encoding="utf-8") as handle:
            handle.write(body)

    def test_longhand_passes(self):
        self._svg("<style>.a { font-weight: 800; font-size: 54px; "
                  "font-family: Arial; }</style>")
        check_repo.check_font_shorthand(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_shorthand_in_style_block_is_flagged(self):
        self._svg("<style>.a { font: 800 54px Arial; }</style>")
        check_repo.check_font_shorthand(self.tmp)
        self.assertTrue(any("viết tắt" in e for e in check_repo.errors))

    def test_shorthand_in_inline_style_is_flagged(self):
        self._svg('<text style="font:600 7.5px monospace">x</text>')
        check_repo.check_font_shorthand(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_word_font_family_is_not_confused(self):
        self._svg('<text style="font-family:Arial;font-weight:700">x</text>')
        check_repo.check_font_shorthand(self.tmp)
        self.assertEqual(check_repo.errors, [])



class TestCronMinutes(unittest.TestCase):
    """Dịch trường phút của cron thành tập phút — và cảnh báo khi trùng."""

    def test_star_is_every_minute(self):
        self.assertEqual(check_repo._cron_minutes("*"), set(range(60)))

    def test_step_from_zero(self):
        self.assertEqual(check_repo._cron_minutes("*/5"),
                         {0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55})

    def test_offset_range(self):
        self.assertEqual(check_repo._cron_minutes("7-59/30"), {7, 37})

    def test_list_and_single(self):
        self.assertEqual(check_repo._cron_minutes("2,12,22"), {2, 12, 22})
        self.assertEqual(check_repo._cron_minutes("13"), {13})

    def test_nonsense_returns_none(self):
        for bad in ("", "abc", "60", "9-3", "*/0", "1/x"):
            self.assertIsNone(check_repo._cron_minutes(bad), bad)


class TestCronCollisions(unittest.TestCase):
    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="cron-")
        self.wf = os.path.join(self.tmp, ".github", "workflows")
        os.makedirs(self.wf)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _add(self, name, cron):
        with open(os.path.join(self.wf, name), "w", encoding="utf-8") as handle:
            handle.write('name: %s\non:\n  schedule:\n    - cron: "%s"\n'
                         % (name, cron))

    def test_shared_minute_is_reported(self):
        self._add("a.yml", "0 */3 * * *")
        self._add("b.yml", "0 */6 * * *")
        check_repo.check_cron_minute_collisions(self.tmp)
        self.assertTrue(any("cùng chạy" in w for w in check_repo.warnings))

    def test_disjoint_minutes_are_quiet(self):
        self._add("a.yml", "13 */3 * * *")
        self._add("b.yml", "*/5 * * * *")
        check_repo.check_cron_minute_collisions(self.tmp)
        self.assertEqual(check_repo.warnings, [])

    def test_real_repo_has_no_collision(self):
        check_repo.check_cron_minute_collisions()
        self.assertEqual([w for w in check_repo.warnings if "cùng chạy" in w], [])



class TestDuplicateIds(unittest.TestCase):
    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="ids-")
        os.makedirs(os.path.join(self.tmp, "assets"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _svg(self, body):
        with open(os.path.join(self.tmp, "assets", "a.svg"), "w",
                  encoding="utf-8") as handle:
            handle.write(body)

    def test_unique_ids_pass(self):
        self._svg('<defs><linearGradient id="a"/><linearGradient id="b"/></defs>')
        check_repo.check_duplicate_ids(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_double_id_is_reported_once(self):
        self._svg('<circle id="halo"/><ellipse id="halo"/>')
        check_repo.check_duplicate_ids(self.tmp)
        self.assertEqual(len(check_repo.errors), 1)
        self.assertIn("'halo'", check_repo.errors[0])


class TestClassReferences(unittest.TestCase):
    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="cls-")
        os.makedirs(os.path.join(self.tmp, "assets"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _svg(self, body):
        with open(os.path.join(self.tmp, "assets", "a.svg"), "w",
                  encoding="utf-8") as handle:
            handle.write(body)

    def test_defined_class_passes(self):
        self._svg('<style>.pulse { animation: p 1s }</style>'
                  '<circle class="pulse"/>')
        check_repo.check_class_references(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_descendant_selector_counts(self):
        self._svg('<style>.liveHour text { opacity: 0 }</style>'
                  '<g class="liveHour"><text>x</text></g>')
        check_repo.check_class_references(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_unknown_class_is_reported(self):
        self._svg('<style>.pulse { animation: p 1s }</style>'
                  '<circle class="pulse pulse-typo"/>')
        check_repo.check_class_references(self.tmp)
        self.assertTrue(any("pulse-typo" in e for e in check_repo.errors))

    def test_smil_only_class_is_exempt(self):
        self._svg('<style>.smilOnly { display: none }</style>'
                  '<circle class="dust smilOnly"/>')
        check_repo.check_class_references(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_real_assets_pass(self):
        check_repo.check_class_references()
        self.assertEqual(check_repo.errors, [])



class TestBadNumbers(unittest.TestCase):
    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []
        self.tmp = tempfile.mkdtemp(prefix="num-")
        os.makedirs(os.path.join(self.tmp, "assets"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _svg(self, body):
        with open(os.path.join(self.tmp, "assets", "a.svg"), "w",
                  encoding="utf-8") as handle:
            handle.write(body)

    def test_clean_numbers_pass(self):
        self._svg('<path d="M12.5 0.5A4 4 0 0 1 20 8"/>')
        check_repo.check_bad_numbers(self.tmp)
        self.assertEqual(check_repo.errors, [])

    def test_nan_is_reported(self):
        self._svg('<path d="MNaN 12"/>')
        check_repo.check_bad_numbers(self.tmp)
        self.assertTrue(any("NaN" in e for e in check_repo.errors))

    def test_none_is_reported(self):
        self._svg('<rect x="None" y="4" width="2" height="2"/>')
        check_repo.check_bad_numbers(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_scientific_notation_is_reported(self):
        # Trong toạ độ path, nơi số mũ hay xuất hiện nhất.
        self._svg('<path d="M1.5e-07 4L8 8"/>')
        check_repo.check_bad_numbers(self.tmp)
        self.assertTrue(check_repo.errors)

    def test_word_in_free_text_is_not_flagged(self):
        # Chữ "None" trong <desc> là văn xuôi, không phải toạ độ.
        self._svg('<text x="4" y="4">None of the above</text>')
        check_repo.check_bad_numbers(self.tmp)
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
