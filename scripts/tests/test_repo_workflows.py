#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử tích hợp: workflow thật trong repo có đúng quy ước không.

Khác với `test_check_repo.py` (kiểm thử *hàm* bằng fixture tạm), file này
chạy chính các luật đó trên repo thật. Nhờ vậy một thay đổi workflow sai
quy ước sẽ đỏ ngay khi chạy test trên máy, không phải đợi CI.
"""

import os
import re
import unittest

from helpers import SCRIPTS  # noqa: F401  (bảo đảm scripts/ nằm trong sys.path)

import check_repo

ROOT = os.path.dirname(SCRIPTS)
FOLDER = os.path.join(ROOT, ".github", "workflows")


def workflow_files():
    return sorted(name for name in os.listdir(FOLDER)
                  if name.endswith((".yml", ".yaml")))


def read(name):
    with open(os.path.join(FOLDER, name), encoding="utf-8") as handle:
        return handle.read()


class TestRepoWorkflows(unittest.TestCase):
    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []

    def test_hygiene_rules_pass_on_real_repo(self):
        check_repo.check_workflow_hygiene(ROOT)
        self.assertEqual(check_repo.errors, [])

    def test_docs_match_real_crons(self):
        check_repo.check_workflow_docs(ROOT)
        self.assertEqual(check_repo.errors, [])

    def test_every_workflow_has_a_name(self):
        for name in workflow_files():
            match = re.search(r"^name:\s*(.+)$", read(name), flags=re.M)
            self.assertIsNotNone(match, "%s thiếu name:" % name)
            self.assertTrue(match.group(1).strip(), "%s có name rỗng" % name)

    def test_every_workflow_declares_permissions(self):
        for name in workflow_files():
            self.assertIn("permissions:", read(name), name)

    def test_scheduled_workflows_have_concurrency(self):
        for name in workflow_files():
            text = read(name)
            if "cron:" in text:
                self.assertIn("concurrency:", text, name)

    def test_cron_values_are_five_fields(self):
        for filename, crons in check_repo.real_crons(ROOT).items():
            for cron in crons:
                self.assertEqual(len(cron.split()), 5, "%s: %s" % (filename, cron))


class TestStatusTriggerNames(unittest.TestCase):
    """`workflow_run` khớp theo TÊN workflow — đổi tên là trigger chết lặng."""

    def test_every_listed_name_exists(self):
        text = read("status.yml")
        # chỉ lấy danh sách trong khối workflow_run: từ "workflows:" tới "types:"
        block = text.split("workflow_run:", 1)[1].split("types:", 1)[0]
        listed = re.findall(r'- "(.+)"', block)
        self.assertTrue(listed, "status.yml không liệt kê workflow nào")
        real = set()
        for name in workflow_files():
            if name == "status.yml":
                continue
            match = re.search(r"^name:\s*(.+)$", read(name), flags=re.M)
            if match:
                real.add(match.group(1).strip())
        self.assertEqual([n for n in listed if n not in real], [])


if __name__ == "__main__":
    unittest.main()
