# -*- coding: utf-8 -*-
"""Test "cổng thông minh" của profile-3d.yml bằng gh giả.

Cổng này quyết định có vẽ lại biểu đồ 3D hay không. Nếu nó sai, hoặc
workflow vẽ lại 288 lần/ngày, hoặc ảnh đứng im mãi mãi — cả hai đều tệ.
Nên nó phải được test như mọi đoạn code khác.
"""

import os
import subprocess
import tempfile
import unittest

import helpers  # noqa: F401  (bảo đảm scripts/ nằm trong sys.path)

try:
    import yaml
except ImportError:                                     # pragma: no cover
    yaml = None

WORKFLOW = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), ".github", "workflows", "profile-3d.yml")

STUB = """#!/usr/bin/env bash
case "$2" in
  *runs*)   printf '%s' "${FAKE_LAST:-}" ;;
  *events*) printf '%s' "${FAKE_NEW:-0}" ;;
esac
exit 0
"""


def _gate_script():
    if yaml is None:
        raise unittest.SkipTest("cần PyYAML để đọc workflow")
    with open(WORKFLOW, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    for step in data["jobs"]["build"]["steps"]:
        if step.get("id") == "gate":
            return step["run"]
    raise AssertionError("không tìm thấy step có id: gate")


@unittest.skipIf(yaml is None, "cần PyYAML")
class TestGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = _gate_script()

    def _run(self, last, new, cwd=None):
        with tempfile.TemporaryDirectory() as tmp:
            stub = os.path.join(tmp, "gh")
            with open(stub, "w", encoding="utf-8") as handle:
                handle.write(STUB)
            os.chmod(stub, 0o755)
            out = os.path.join(tmp, "out")
            script = os.path.join(tmp, "gate.sh")
            with open(script, "w", encoding="utf-8") as handle:
                handle.write(self.script)
            env = dict(os.environ,
                       PATH=tmp + os.pathsep + os.environ.get("PATH", ""),
                       GITHUB_OUTPUT=out,
                       GITHUB_REPOSITORY="standardizeparadigm/standardizeparadigm",
                       GITHUB_REPOSITORY_OWNER="standardizeparadigm",
                       FAKE_LAST=last, FAKE_NEW=new)
            subprocess.run(["bash", script], env=env, capture_output=True, check=True,
                           cwd=cwd or tmp)
            with open(out, encoding="utf-8") as handle:
                text = handle.read()
        return "run=1" in text

    def test_first_ever_run(self):
        self.assertTrue(self._run("", "0"))

    def test_new_push_triggers(self):
        self.assertTrue(self._run(recent(10), "3"))

    def test_nothing_new_skips(self):
        self.assertFalse(self._run(recent(10), "0"))

    def test_day_old_triggers(self):
        self.assertTrue(self._run(recent(60 * 30), "0"))

    def test_garbage_count_is_safe(self):
        self.assertFalse(self._run(recent(10), "not-a-number"))


    def test_git_age_triggers_daily_refresh(self):
        """Ảnh 30 giờ tuổi, không có push nào -> vẫn phải vẽ lại."""
        with tempfile.TemporaryDirectory() as repo:
            self._make_repo(repo, hours_ago=30)
            self.assertTrue(self._run("", "0", cwd=repo))

    def test_fresh_image_skips(self):
        """Ảnh vừa đổi xong, không push -> bỏ qua."""
        with tempfile.TemporaryDirectory() as repo:
            self._make_repo(repo, hours_ago=1)
            self.assertFalse(self._run("", "0", cwd=repo))

    @staticmethod
    def _make_repo(path, hours_ago):
        import datetime

        stamp = (datetime.datetime.now(datetime.timezone.utc)
                 - datetime.timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
        os.makedirs(os.path.join(path, "profile-3d-contrib"), exist_ok=True)
        with open(os.path.join(path, "profile-3d-contrib", "a.svg"), "w",
                  encoding="utf-8") as handle:
            handle.write("<svg/>")
        env = dict(os.environ, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp,
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
        subprocess.run(["git", "init", "-q", path], check=True)
        subprocess.run(["git", "-C", path, "add", "-A"], check=True)
        subprocess.run(["git", "-C", path, "commit", "-q", "-m", "c"],
                       check=True, env=env)


def recent(minutes):
    """Mốc thời gian ISO-8601 trong quá khứ, dùng cho gh giả."""
    import datetime

    moment = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        minutes=minutes)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")

