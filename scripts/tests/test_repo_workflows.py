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

    def test_no_orphan_docs(self):
        check_repo.check_orphan_docs(ROOT)
        self.assertEqual(check_repo.errors, [])

    def test_svg_budget_holds(self):
        check_repo.check_svg_budget(ROOT)
        self.assertEqual(check_repo.errors, [])

    def test_test_claims_are_current(self):
        check_repo.check_test_claims(ROOT)
        self.assertEqual(check_repo.errors, [])

    def test_every_module_has_a_docstring(self):
        check_repo.check_module_docstrings(ROOT)
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




class TestNewLawsOnRealRepo(unittest.TestCase):
    """Các luật mới chạy trên repo thật — sai là đỏ ngay trên máy."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []

    def test_no_stale_places(self):
        check_repo.check_stale_places()
        self.assertEqual(check_repo.errors, [])

    def test_no_todo_markers(self):
        check_repo.check_todo_markers()
        self.assertEqual(check_repo.errors, [])

    def test_every_workflow_is_dispatchable(self):
        check_repo.check_workflow_dispatch()
        self.assertEqual(check_repo.errors, [])

    def test_no_shields_workflow_badges(self):
        check_repo.check_shields_workflow_badges()
        self.assertEqual(check_repo.errors, [])

    def test_cron_is_not_faster_than_github_allows(self):
        check_repo.check_cron_resolution()
        self.assertEqual(check_repo.errors, [])

    def test_actions_are_pinned(self):
        check_repo.check_action_pins()
        self.assertEqual(check_repo.errors, [])

    def test_jobs_have_timeouts(self):
        check_repo.check_job_timeouts()
        self.assertEqual(check_repo.errors, [])

    def test_assets_are_clean(self):
        check_repo.check_svg_text_classes()
        check_repo.check_svg_duplicate_ids()
        check_repo.check_svg_artifacts()
        check_repo.check_svg_safety()
        self.assertEqual(check_repo.errors, [])

    def test_markdown_is_well_formed(self):
        check_repo.check_heading_levels()
        check_repo.check_markdown_tables()
        check_repo.check_doc_titles()
        self.assertEqual(check_repo.errors, [])



class TestScheduleGrid(unittest.TestCase):
    """Lịch chạy thật: mỗi job một phút, không chen nhau."""

    def setUp(self):
        check_repo.errors = []
        check_repo.warnings = []

    def _minutes(self):
        grid = {}
        for name in workflow_files():
            for cron in re.findall(r'cron:\s*"([^"]+)"', read(name)):
                field = cron.split()[0]
                minutes = check_repo._cron_minutes(field)
                if minutes:
                    grid.setdefault(name, set()).update(minutes)
        return grid

    def test_five_jobs_have_a_schedule(self):
        # live-clock, profile-3d, profile-cards, readme-tend, status, health
        self.assertGreaterEqual(len(self._minutes()), 6)

    def test_no_two_jobs_share_a_minute(self):
        grid = self._minutes()
        names = sorted(grid)
        for i, left in enumerate(names):
            for right in names[i + 1:]:
                self.assertEqual(grid[left] & grid[right], set(),
                                 "%s và %s cùng phút" % (left, right))

    def test_the_clock_owns_the_five_minute_grid(self):
        grid = self._minutes()
        clock = grid.get("live-clock.yml", set())
        self.assertEqual(clock, set(range(0, 60, 5)))

    def test_every_schedule_is_within_github_limits(self):
        for name in workflow_files():
            for cron in re.findall(r'cron:\s*"([^"]+)"', read(name)):
                step = check_repo._minute_step(cron.split()[0])
                if step is not None:
                    self.assertGreaterEqual(step, 5, "%s: %s" % (name, cron))


class TestWorkflowStyle(unittest.TestCase):
    def test_every_file_ends_with_one_newline(self):
        for name in workflow_files():
            text = read(name)
            self.assertTrue(text.endswith("\n"), name)
            self.assertFalse(text.endswith("\n\n"), name)

    def test_every_file_has_a_comment_header(self):
        for name in workflow_files():
            lines = [l for l in read(name).splitlines() if l.strip()]
            self.assertTrue(lines[0].startswith("#"), name)

    def test_no_hardcoded_token(self):
        for name in workflow_files():
            text = read(name)
            self.assertNotIn("ghp_", text, name)
            self.assertNotIn("github_pat_", text, name)

    def test_no_secrets_in_plain_text(self):
        for name in workflow_files():
            for line in read(name).splitlines():
                if "secrets." in line:
                    self.assertIn("${{", line, name)



class TestUpdateCadence(unittest.TestCase):
    """Nhịp cập nhật: đủ dày để ảnh không cũ, đủ thưa để không phí."""

    def _cron(self, name):
        return re.findall(r'cron:\s*"([^"]+)"', read(name))

    def test_clock_runs_every_five_minutes(self):
        self.assertEqual(self._cron("live-clock.yml"), ["*/5 * * * *"])

    def test_status_runs_every_five_minutes(self):
        self.assertEqual(self._cron("status.yml"), ["2-59/5 * * * *"])

    def test_3d_checks_every_ten_minutes(self):
        self.assertEqual(self._cron("profile-3d.yml"), ["8-59/10 * * * *"])

    def test_cards_run_hourly(self):
        self.assertEqual(self._cron("profile-cards.yml"), ["13 * * * *"])

    def test_readme_stamp_runs_every_two_hours(self):
        self.assertEqual(self._cron("readme-tend.yml"), ["23 */2 * * *"])

    def test_no_job_runs_faster_than_github_allows(self):
        for name in workflow_files():
            for cron in self._cron(name):
                step = check_repo._minute_step(cron.split()[0])
                if step is not None:
                    self.assertGreaterEqual(step, 5, "%s %s" % (name, cron))

    def test_every_scheduled_job_is_also_dispatchable(self):
        for name in workflow_files():
            text = read(name)
            if "cron:" in text:
                self.assertIn("workflow_dispatch", text, name)

if __name__ == "__main__":
    unittest.main()
