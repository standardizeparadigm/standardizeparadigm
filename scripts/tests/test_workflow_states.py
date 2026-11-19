#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử api.workflow_states() — cách đọc trạng thái từng workflow.

Không gọi mạng: thay api.api_status() bằng hàm giả để mô phỏng từng mã HTTP
và từng `conclusion` mà GitHub trả về.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWorkflowStates(unittest.TestCase):
    """api.workflow_states() — phân loại lần chạy gần nhất."""

    def _states(self, code, payload, token="t"):
        from svgkit import api
        original = api.api_status
        api.api_status = lambda *_a, **_k: (code, payload)
        try:
            rows = api.workflow_states("o", "r", token,
                                       files=[("a.yml", "A"), ("b.yml", "B")])
            # hàng có 3 phần tử: (tên, trạng thái, số phút từ lần chạy cuối)
            return {row[0]: row[1] for row in rows}
        finally:
            api.api_status = original

    def test_404_means_not_on_default_branch(self):
        self.assertEqual(self._states(404, None)["A"], "missing")

    def test_success_is_passing(self):
        run = {"workflow_runs": [{"status": "completed", "conclusion": "success"}]}
        self.assertEqual(self._states(200, run)["A"], "passing")

    def test_failure_is_failing(self):
        run = {"workflow_runs": [{"status": "completed", "conclusion": "failure"}]}
        self.assertEqual(self._states(200, run)["A"], "failing")

    def test_timeout_is_failing(self):
        run = {"workflow_runs": [{"status": "completed", "conclusion": "timed_out"}]}
        self.assertEqual(self._states(200, run)["A"], "failing")

    def test_in_progress_is_running(self):
        run = {"workflow_runs": [{"status": "in_progress", "conclusion": None}]}
        self.assertEqual(self._states(200, run)["A"], "running")

    def test_queued_is_running(self):
        run = {"workflow_runs": [{"status": "queued", "conclusion": None}]}
        self.assertEqual(self._states(200, run)["A"], "running")

    def test_cancelled_is_unknown(self):
        run = {"workflow_runs": [{"status": "completed", "conclusion": "cancelled"}]}
        self.assertEqual(self._states(200, run)["A"], "unknown")

    def test_no_runs_is_none(self):
        self.assertEqual(self._states(200, {"workflow_runs": []})["A"], "none")

    def test_server_error_is_unknown(self):
        self.assertEqual(self._states(500, None)["A"], "unknown")

    def test_without_token_everything_is_unknown(self):
        rows = self._states(200, None, token="")
        self.assertEqual(set(rows.values()), {"unknown"})



class TestAgeMinutes(unittest.TestCase):
    """age_minutes() — đổi mốc ISO của GitHub thành số phút."""

    NOW = __import__("datetime").datetime(
        2026, 11, 19, 10, 0, 0, tzinfo=__import__("datetime").timezone.utc)

    def _age(self, iso):
        from svgkit import api
        return api.age_minutes(iso, self.NOW)

    def test_zero_when_just_finished(self):
        self.assertEqual(self._age("2026-11-19T10:00:30Z"), 0)

    def test_minutes(self):
        self.assertEqual(self._age("2026-11-19T09:04:11Z"), 55)

    def test_garbage_is_none_not_zero(self):
        # None quan trọng hơn 0: 0 nghĩa là "vừa xong", còn None nghĩa là
        # "không biết" — và dải trạng thái sẽ bỏ trống nhãn thay vì nói dối.
        self.assertIsNone(self._age("hôm qua"))
        self.assertIsNone(self._age(""))
        self.assertIsNone(self._age(None))

    def test_future_timestamp_never_negative(self):
        self.assertEqual(self._age("2026-11-19T10:05:00Z"), 0)

    def test_aware_now_is_not_mangled(self):
        from svgkit import api
        naive_now = self.NOW.replace(tzinfo=None)
        self.assertEqual(api.age_minutes("2026-11-19T09:00:00Z", naive_now), 60)

if __name__ == "__main__":
    unittest.main()
