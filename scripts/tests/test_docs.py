#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quy ước hình thức cho tài liệu Markdown.

Không kiểm tra nội dung đúng/sai (việc của người đọc) mà kiểm tra những
thứ máy kiểm được và người hay quên: đúng một H1, không nhảy cấp tiêu đề,
tiêu đề luôn có dòng trống phía trước, file kết thúc bằng đúng một newline.
Mỗi lỗi trong số này đều từng xuất hiện thật trong repo này.
"""

import os
import re
import unittest

from helpers import SCRIPTS  # noqa: F401  (bảo đảm scripts/ nằm trong sys.path)

ROOT = os.path.dirname(SCRIPTS)

DOC_FILES = ["README.md", "CHANGELOG.md", ".github/CONTRIBUTING.md",
             "scripts/svgkit/README.md"]
DOCS_DIR = os.path.join(ROOT, "docs")

RE_H1 = re.compile(r"^# \S")
RE_HEADING = re.compile(r"^(#{1,6}) \S")
RE_FENCE = re.compile(r"^\s*```")


def all_docs():
    paths = [os.path.join(ROOT, name) for name in DOC_FILES]
    if os.path.isdir(DOCS_DIR):
        paths += [os.path.join(DOCS_DIR, n) for n in sorted(os.listdir(DOCS_DIR))
                  if n.endswith(".md")]
    return [p for p in paths if os.path.exists(p)]


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def prose_lines(text):
    """(số_dòng, nội_dung) của những dòng *ngoài* khối code."""
    inside = False
    for number, line in enumerate(text.splitlines(), 1):
        if RE_FENCE.match(line):
            inside = not inside
            continue
        if not inside:
            yield number, line


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def has_h1(path):
    return any(RE_H1.match(line) for _, line in prose_lines(read(path)))


class TestSingleH1(unittest.TestCase):
    def test_never_more_than_one_h1(self):
        for path in all_docs():
            count = sum(1 for _, line in prose_lines(read(path))
                        if RE_H1.match(line))
            self.assertLessEqual(count, 1, "%s có %d H1" % (rel(path), count))

    def test_docs_folder_files_have_an_h1(self):
        # README trang cá nhân cố tình mở bằng ảnh bìa chứ không bằng chữ,
        # nên chỉ các bài trong docs/ (và CHANGELOG) bắt buộc có H1.
        for path in all_docs():
            if os.path.basename(os.path.dirname(path)) == "docs" or \
                    path.endswith(("CHANGELOG.md", "CONTRIBUTING.md")):
                self.assertTrue(has_h1(path), "%s thiếu H1" % rel(path))

    def test_h1_comes_before_every_other_heading(self):
        for path in all_docs():
            headings = [line for _, line in prose_lines(read(path))
                        if RE_HEADING.match(line)]
            self.assertTrue(headings, rel(path))
            if has_h1(path):
                self.assertTrue(headings[0].startswith("# "), rel(path))


class TestHeadingLevels(unittest.TestCase):
    def test_levels_never_skip(self):
        for path in all_docs():
            # Không có H1 thì bài được phép mở bằng ## (README trang cá nhân).
            previous = 1 if not has_h1(path) else 0
            for number, line in prose_lines(read(path)):
                match = RE_HEADING.match(line)
                if not match:
                    continue
                level = len(match.group(1))
                self.assertLessEqual(level, previous + 1,
                                     "%s:%d nhảy cấp %d → %d"
                                     % (rel(path), number, previous, level))
                previous = level

    def test_heading_has_blank_line_before_it(self):
        for path in all_docs():
            lines = read(path).splitlines()
            for number, line in prose_lines(read(path)):
                if not RE_HEADING.match(line) or number == 1:
                    continue
                self.assertEqual(lines[number - 2].strip(), "",
                                 "%s:%d thiếu dòng trống trước tiêu đề"
                                 % (rel(path), number))


class TestFileEdges(unittest.TestCase):
    def test_ends_with_exactly_one_newline(self):
        for path in all_docs():
            text = read(path)
            self.assertTrue(text.endswith("\n"), rel(path))
            self.assertFalse(text.endswith("\n\n"), "%s có dòng trống cuối"
                             % rel(path))

    def test_no_crlf(self):
        for path in all_docs():
            self.assertNotIn("\r", read(path), rel(path))

    def test_no_trailing_spaces(self):
        for path in all_docs():
            for number, line in prose_lines(read(path)):
                self.assertEqual(line, line.rstrip(),
                                 "%s:%d có khoảng trắng cuối dòng"
                                 % (rel(path), number))


class TestAnimationsDoc(unittest.TestCase):
    """Bài kiểm kê hoạt ảnh phải kết thúc bằng lối thoát."""

    def setUp(self):
        self.path = os.path.join(DOCS_DIR, "ANIMATIONS.md")
        self.text = read(self.path)

    def test_reduced_motion_section_is_last(self):
        headings = [line for _, line in prose_lines(self.text)
                    if line.startswith("## ")]
        self.assertTrue(headings)
        self.assertIn("Tắt hoạt ảnh", headings[-1])

    def test_table_lists_every_asset_with_animation(self):
        for name in ("hero", "divider", "footer", "stats", "top-langs",
                     "live-clock", "activity", "status"):
            self.assertIn("`%s.svg`" % name, self.text)




class TestTestingDoc(unittest.TestCase):
    """Bài TESTING.md phải khớp bộ test thật.

    Trước đây bảng trong bài có cột "số test" và nó lệch ngay sau lần thêm
    test đầu tiên. Giờ bài chỉ ghi tổng số — và chính test này đếm lại.
    """

    def setUp(self):
        self.path = os.path.join(DOCS_DIR, "TESTING.md")
        self.text = read(self.path)

    def _real_total(self):
        loader = unittest.defaultTestLoader
        suite = loader.discover(os.path.join(ROOT, "scripts", "tests"),
                                top_level_dir=os.path.join(ROOT, "scripts"))
        return suite.countTestCases()

    def test_stated_total_matches_reality(self):
        match = re.search(r"Hiện có \*\*(\d+) test\*\*", self.text)
        self.assertIsNotNone(match, "TESTING.md thiếu câu 'Hiện có **N test**'")
        self.assertEqual(int(match.group(1)), self._real_total())

    def test_stated_file_count_matches_reality(self):
        match = re.search(r"Hiện có \*\*\d+ test\*\* trên (\d+) file", self.text)
        self.assertIsNotNone(match)
        real = len([n for n in os.listdir(os.path.join(ROOT, "scripts", "tests"))
                    if n.startswith("test_") and n.endswith(".py")])
        self.assertEqual(int(match.group(1)), real)

    def test_every_test_file_is_listed(self):
        folder = os.path.join(ROOT, "scripts", "tests")
        for name in sorted(os.listdir(folder)):
            if name.startswith("test_") and name.endswith(".py"):
                self.assertIn("`%s`" % name, self.text,
                              "%s chưa có trong bảng bản đồ" % name)



class TestDocsStructure(unittest.TestCase):
    """Cấu trúc tài liệu: thứ người đọc thấy trước tiên."""

    def _docs(self):
        return sorted(n for n in os.listdir(DOCS_DIR) if n.endswith(".md"))

    def test_every_doc_starts_with_an_h1(self):
        for name in self._docs():
            lines = [line for line in read(os.path.join(DOCS_DIR, name)).split("\n")
                     if line.strip()]
            self.assertTrue(lines[0].startswith("# "), name)

    def test_no_doc_has_two_empty_sections(self):
        for name in self._docs():
            text = read(os.path.join(DOCS_DIR, name))
            self.assertNotIn("\n## \n", text, name)

    def test_no_doc_ends_with_orphan_table(self):
        # Bảng ở cuối file mà không có câu dẫn thì trông như file bị cắt.
        for name in self._docs():
            lines = [line for line in read(os.path.join(DOCS_DIR, name)).split("\n")
                     if line.strip()]
            self.assertFalse(lines[-1].startswith("|"), name)



RE_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class TestInternalLinks(unittest.TestCase):
    """Liên kết nội bộ trong tài liệu phải trỏ tới file có thật."""

    def _targets(self, path):
        for number, line in prose_lines(read(path)):
            for target in RE_LINK.findall(line):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                yield number, target.split("#")[0]

    def test_every_relative_link_resolves(self):
        for path in all_docs():
            for number, target in self._targets(path):
                if not target:
                    continue
                resolved = os.path.normpath(
                    os.path.join(os.path.dirname(path), target))
                self.assertTrue(os.path.exists(resolved),
                                "%s:%d trỏ tới %r không tồn tại"
                                % (rel(path), number, target))

    def test_anchors_point_at_existing_headings(self):
        for path in all_docs():
            anchors = {self._slug(h) for h in
                       re.findall(r"^#{1,6} (.+)$", read(path), re.M)}
            for number, line in prose_lines(read(path)):
                for target in RE_LINK.findall(line):
                    if "#" not in target or target.startswith("http"):
                        continue
                    file_part, _, anchor = target.partition("#")
                    base = path if not file_part else os.path.normpath(
                        os.path.join(os.path.dirname(path), file_part))
                    if not os.path.exists(base) or not anchor:
                        continue
                    base_anchors = {self._slug(h) for h in re.findall(
                        r"^#{1,6} (.+)$", read(base), re.M)}
                    self.assertIn(anchor, base_anchors,
                                  "%s:%d mục #%s không có trong %s"
                                  % (rel(path), number, anchor, rel(base)))

    @staticmethod
    def _slug(heading):
        text = heading.strip().lower()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"\s+", "-", text).strip("-")



# Trình soạn thảo và công cụ dán web hay để lại những ký tự này. Chữ Việt bị
# đọc sai bảng mã vẫn đoán ra được, nhưng grep thì không, và bản dịch thì hỏng.
BROKEN_MARKS = {
    "\ufffd": "ký tự thay thế U+FFFD",
    "\u00a0": "dấu cách không ngắt (NBSP)",
    "\u200b": "dấu cách rộng bằng 0 (ZWSP)",
    "\ufeff": "BOM giữa file",
}
# Chuỗi "Ã" một mình là chữ Việt hợp lệ (ĐÃ, Ã); chỉ bắt khi đi kèm một ký
# tự Latin-1 bổ sung — dấu hiệu của UTF-8 bị đọc thành Latin-1.
RE_MOJIBAKE = re.compile("[\u00c3\u00c2][\u0080-\u00bf\u2018-\u203a]")

EXEMPT = {"scripts/check_repo.py", "scripts/tests/test_check_repo.py"}


class TestNoBrokenCharacters(unittest.TestCase):
    """Không một file nào được mang ký tự hỏng."""

    def _files(self):
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = sorted(d for d in dirs
                             if d not in {".git", "node_modules", "__pycache__",
                                          "assets", ".venv"})
            for name in sorted(files):
                if not name.endswith((".md", ".py", ".yml", ".yaml", ".svg")):
                    continue
                path = os.path.join(base, name)
                if rel(path) in EXEMPT:
                    continue
                yield path

    def test_no_replacement_or_invisible_space(self):
        for path in self._files():
            text = read(path)
            for mark, label in BROKEN_MARKS.items():
                self.assertNotIn(mark, text, "%s có %s" % (rel(path), label))

    def test_no_latin1_mojibake(self):
        for path in self._files():
            for number, line in enumerate(read(path).splitlines(), 1):
                self.assertIsNone(RE_MOJIBAKE.search(line),
                                  "%s:%d nghi chữ hỏng: %r"
                                  % (rel(path), number, line.strip()[:60]))

    def test_vietnamese_words_are_precomposed(self):
        # Dấu mũ rời (NFD) hiển thị đúng nhưng tìm kiếm không ra.
        for path in self._files():
            text = read(path)
            self.assertNotIn("\u0300", text, rel(path))

if __name__ == "__main__":
    unittest.main()
