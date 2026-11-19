# -*- coding: utf-8 -*-
"""Test cửa vào dòng lệnh: xuất file, chế độ demo, theme, ngôn ngữ."""

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.dom.minidom as minidom

from helpers import SCRIPTS

import generate_cards  # noqa: E402  (đã có sys.path trong helpers)


class TestCli(unittest.TestCase):
    def setUp(self):
        self.out = tempfile.mkdtemp(prefix="cards-test-")

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def run_cli(self, *args):
        return generate_cards.main(list(args) + ["--out", self.out])

    def test_demo_all_writes_every_asset(self):
        self.assertEqual(self.run_cli("--demo", "--all"), 0)
        expected = {"hero.svg", "divider.svg", "footer.svg", "live-clock.svg",
                    "stats.svg", "top-langs.svg", "activity.svg"}
        self.assertEqual(set(os.listdir(self.out)), expected)
        for name in expected:
            path = os.path.join(self.out, name)
            minidom.parse(path)               # không được lỗi XML

    def test_clock_only(self):
        self.assertEqual(self.run_cli("--demo", "--clock"), 0)
        self.assertEqual(os.listdir(self.out), ["live-clock.svg"])

    def test_hero_group(self):
        self.assertEqual(self.run_cli("--demo", "--hero"), 0)
        self.assertEqual(set(os.listdir(self.out)),
                         {"hero.svg", "divider.svg", "footer.svg"})

    def test_cards_group(self):
        self.assertEqual(self.run_cli("--demo", "--cards"), 0)
        self.assertEqual(set(os.listdir(self.out)),
                         {"stats.svg", "top-langs.svg"})

    def test_placeholder(self):
        self.assertEqual(self.run_cli("--placeholder"), 0)
        self.assertEqual(set(os.listdir(self.out)),
                         {"stats.svg", "top-langs.svg"})
        content = open(os.path.join(self.out, "stats.svg"), encoding="utf-8").read()
        self.assertIn("Profile Cards", content)

    def test_theme_and_lang(self):
        self.assertEqual(
            self.run_cli("--demo", "--cards", "--theme", "violet", "--lang", "en"), 0)
        content = open(os.path.join(self.out, "stats.svg"), encoding="utf-8").read()
        self.assertIn("#A78BFA", content)
        self.assertIn("UPDATED", content)

    def test_missing_user_is_not_a_crash(self):
        # không có GH_USER trong môi trường test -> trả 0 (không --strict)
        saved = generate_cards.USER
        generate_cards.USER = ""
        try:
            self.assertEqual(self.run_cli("--cards"), 0)
        finally:
            generate_cards.USER = saved

    def test_list_themes(self):
        self.assertEqual(generate_cards.main(["--list-themes"]), 0)

    def test_writes_are_atomic(self):
        # không được để lại file tạm .tmp-*
        self.run_cli("--demo", "--all")
        leftovers = [n for n in os.listdir(self.out) if n.startswith(".tmp-")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()


class TestInfoFlags(unittest.TestCase):
    def test_version_prints_number(self):
        import generate_cards

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = generate_cards.main(["--version"])
        self.assertEqual(code, 0)
        self.assertRegex(out.getvalue(), r"\d+\.\d+\.\d+")

    def test_list_langs(self):
        import generate_cards

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = generate_cards.main(["--list-langs"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("vi", text)
        self.assertIn("en", text)


class TestCheckFlag(unittest.TestCase):
    def test_check_reports_good_files(self):
        import generate_cards

        with tempfile.TemporaryDirectory() as tmp:
            generate_cards.OUT_DIR = tmp
            generate_cards.main(["--demo", "--cards", "--out", tmp])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = generate_cards.main(["--check", "--out", tmp])
            self.assertEqual(code, 0)
            self.assertIn("hợp lệ", out.getvalue())

    def test_check_reports_broken_file(self):
        import generate_cards

        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "broken.svg"), "w", encoding="utf-8") as handle:
                handle.write("<svg><rect</svg>")
            with contextlib.redirect_stdout(io.StringIO()):
                code = generate_cards.main(["--check", "--out", tmp])
            self.assertEqual(code, 1)

    def test_check_empty_dir(self):
        import generate_cards

        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(io.StringIO()):
                code = generate_cards.main(["--check", "--out", tmp])
            self.assertEqual(code, 1)


class TestInfoFlags(unittest.TestCase):
    def test_version_prints_number(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = generate_cards.main(["--version"])
        self.assertEqual(code, 0)
        self.assertRegex(out.getvalue(), r"\d+\.\d+\.\d+")

    def test_list_langs(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = generate_cards.main(["--list-langs"])
        self.assertEqual(code, 0)
        self.assertIn("vi", out.getvalue())
        self.assertIn("en", out.getvalue())


class TestCheckFlag(unittest.TestCase):
    def test_check_reports_good_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate_cards.main(["--demo", "--cards", "--out", tmp])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = generate_cards.main(["--check", "--out", tmp])
            self.assertEqual(code, 0)
            self.assertIn("hợp lệ", out.getvalue())

    def test_check_reports_broken_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "broken.svg"), "w", encoding="utf-8") as handle:
                handle.write("<svg><rect</svg>")
            with contextlib.redirect_stdout(io.StringIO()):
                code = generate_cards.main(["--check", "--out", tmp])
            self.assertEqual(code, 1)

    def test_check_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(io.StringIO()):
                code = generate_cards.main(["--check", "--out", tmp])
            self.assertEqual(code, 1)


class TestInfoFlags(unittest.TestCase):
    def test_version_prints_number(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = generate_cards.main(["--version"])
        self.assertEqual(code, 0)
        self.assertRegex(out.getvalue(), r"\d+\.\d+\.\d+")

    def test_list_langs(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = generate_cards.main(["--list-langs"])
        self.assertEqual(code, 0)
        self.assertIn("vi", out.getvalue())
        self.assertIn("en", out.getvalue())


class TestCheckFlag(unittest.TestCase):
    def test_check_reports_good_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate_cards.main(["--demo", "--cards", "--out", tmp])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = generate_cards.main(["--check", "--out", tmp])
            self.assertEqual(code, 0)
            self.assertIn("hợp lệ", out.getvalue())

    def test_check_reports_broken_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "broken.svg"), "w", encoding="utf-8") as handle:
                handle.write("<svg><rect</svg>")
            with contextlib.redirect_stdout(io.StringIO()):
                code = generate_cards.main(["--check", "--out", tmp])
            self.assertEqual(code, 1)

    def test_check_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(io.StringIO()):
                code = generate_cards.main(["--check", "--out", tmp])
            self.assertEqual(code, 1)


class TestAsScript(unittest.TestCase):
    """Chạy như script thật, không import — bắt lỗi thứ tự khai báo hàm."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "generate_cards.py")] + list(args),
            capture_output=True, text=True)

    def test_version(self):
        result = self._run("--version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("generate_cards.py", result.stdout)

    def test_check_on_demo_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._run("--demo", "--all", "--out", tmp)
            result = self._run("--check", "--out", tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("7/7", result.stdout)

    def test_demo_all_as_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run("--demo", "--all", "--out", tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len([f for f in os.listdir(tmp) if f.endswith(".svg")]), 7)


class TestSmartMode(unittest.TestCase):
    def setUp(self):
        self.out = tempfile.mkdtemp(prefix="cards-smart-")

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def _run(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            generate_cards.main(["--demo", "--cards", "--activity",
                                 "--smart", "--out", self.out])
        return out.getvalue()

    def test_second_run_writes_nothing(self):
        import time

        first = self._run()
        self.assertNotIn("không đổi", first)
        before = {name: os.path.getmtime(os.path.join(self.out, name))
                  for name in os.listdir(self.out)}
        time.sleep(0.01)
        second = self._run()
        self.assertIn("không đổi", second)
        after = {name: os.path.getmtime(os.path.join(self.out, name))
                 for name in os.listdir(self.out)}
        self.assertEqual(before, after)

    def test_without_smart_always_writes(self):
        self._run()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            generate_cards.main(["--demo", "--cards", "--out", self.out])
        self.assertNotIn("không đổi", out.getvalue())

    def test_data_marker_present(self):
        self._run()
        with open(os.path.join(self.out, "stats.svg"), encoding="utf-8") as handle:
            text = handle.read()
        self.assertRegex(text, r"<!-- data:[0-9a-f]{12} -->")
