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
                    "stats.svg", "top-langs.svg", "activity.svg", "status.svg"}
        self.assertEqual(set(os.listdir(self.out)), expected)
        for name in expected:
            path = os.path.join(self.out, name)
            minidom.parse(path)               # không được lỗi XML

    def test_status_only(self):
        self.assertEqual(self.run_cli("--demo", "--status"), 0)
        self.assertEqual(os.listdir(self.out), ["status.svg"])

    def test_status_demo_has_all_five_states(self):
        self.run_cli("--demo", "--status")
        with open(os.path.join(self.out, "status.svg"), encoding="utf-8") as handle:
            svg = handle.read()
        self.assertIn("ĐẠT", svg)          # passing
        self.assertIn("LỖI", svg)          # failing
        self.assertIn("ĐANG CHẠY", svg)    # running
        self.assertIn("CHƯA CHẠY", svg)    # none
        minidom.parseString(svg)

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




class TestUnknownFlags(unittest.TestCase):
    """Gõ sai theme/ngôn ngữ phải được nhắc, không im lặng."""

    def _run(self, argv):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(out):
                generate_cards.main(argv + ["--demo", "--clock", "--dry-run",
                                            "--out", tmp])
        return out.getvalue()

    def test_unknown_theme_warns_and_falls_back(self):
        text = self._run(["--theme", "skky"])
        self.assertIn("theme 'skky' không có", text)
        self.assertIn("dùng 'sky'", text)

    def test_unknown_language_warns_and_falls_back(self):
        text = self._run(["--lang", "e"])
        self.assertIn("ngôn ngữ 'e' không có", text)
        self.assertIn("'en'", text)

    def test_known_values_are_silent(self):
        for argv in (["--theme", "sky"], ["--lang", "en"]):
            self.assertNotIn("không có", self._run(argv))



class TestAtFlag(unittest.TestCase):
    """`--at`: vẽ như thể đang là một thời điểm khác."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="at-")
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_parses_three_shapes(self):
        for text in ("2026-11-19T23:50", "2026-11-19 23:50",
                     "2026-11-19T23:50:07"):
            moment = generate_cards.parse_moment(text)
            self.assertIsNotNone(moment, text)
            self.assertEqual((moment.hour, moment.minute), (23, 50))

    def test_hour_only(self):
        self.assertEqual(generate_cards.parse_moment("2026-11-19T07").hour, 7)

    def test_bad_input_is_none(self):
        for text in ("", "hôm qua", "2026-13-40", "19/11/2026"):
            self.assertIsNone(generate_cards.parse_moment(text), text)

    def test_clock_uses_the_given_moment(self):
        code = generate_cards.main(["--clock", "--at", "2026-11-19T23:50",
                                    "--out", self.tmp, "--quiet"])
        self.assertEqual(code, 0)
        with open(os.path.join(self.tmp, "live-clock.svg"), encoding="utf-8") as f:
            svg = f.read()
        self.assertIn("23:50", svg)
        minidom.parseString(svg)

    def test_bad_moment_exits_two(self):
        self.assertEqual(generate_cards.main(["--clock", "--at", "hôm qua",
                                              "--quiet"]), 2)

    def test_moment_does_not_leak_into_the_next_run(self):
        generate_cards.main(["--clock", "--at", "2026-11-19T07:05",
                             "--out", self.tmp, "--quiet"])
        generate_cards.main(["--clock", "--at", "2026-11-19T21:05",
                             "--out", self.tmp, "--quiet"])
        with open(os.path.join(self.tmp, "live-clock.svg"), encoding="utf-8") as f:
            svg = f.read()
        self.assertIn("21:05", svg)
        self.assertNotIn("07:05", svg)



class TestCheckFlagDetails(unittest.TestCase):
    """`--check` không chỉ bắt XML hỏng mà còn bắt ảnh phình."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="check-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.out = self.tmp

    def _write(self, name, body):
        with open(os.path.join(self.out, name), "w", encoding="utf-8") as handle:
            handle.write(body)

    def test_valid_files_return_zero(self):
        self._write("a.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.assertEqual(generate_cards.main(["--check", "--out", self.out]), 0)

    def test_total_size_is_printed(self):
        self._write("a.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            generate_cards.main(["--check", "--out", self.out])
        self.assertIn("tổng", buffer.getvalue())

    def test_oversized_file_fails(self):
        # 41 KB toàn khoảng trắng trong một comment: đường dẫn nhanh nhất để
        # vượt ngưỡng mà không cần vẽ gì.
        body = "<svg xmlns=\"http://www.w3.org/2000/svg\"><!--%s--></svg>" % (
            "x" * (41 * 1024))
        self._write("big.svg", body)
        self.assertEqual(generate_cards.main(["--check", "--out", self.out]), 1)

    def test_broken_xml_fails(self):
        self._write("bad.svg", "<svg><unclosed>")
        self.assertEqual(generate_cards.main(["--check", "--out", self.out]), 1)

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
            self.assertIn("8/8", result.stdout)

    def test_demo_all_as_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run("--demo", "--all", "--out", tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len([f for f in os.listdir(tmp) if f.endswith(".svg")]), 8)


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


class TestDataFingerprint(unittest.TestCase):
    def test_none_means_no_fingerprint(self):
        self.assertIsNone(generate_cards.data_hash(None))

    def test_stable_across_key_order(self):
        one = generate_cards.data_hash({"a": 1, "b": [1, 2]})
        two = generate_cards.data_hash({"b": [1, 2], "a": 1})
        self.assertEqual(one, two)
        self.assertEqual(len(one), 12)

    def test_changes_with_data(self):
        base = generate_cards.data_hash({"stars": 2})
        self.assertNotEqual(base, generate_cards.data_hash({"stars": 3}))

    def test_marker_roundtrip(self):
        import tempfile as tf

        with tf.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "x.svg")
            svg = generate_cards.stamp_data_mark("<svg></svg>", "abcdef123456")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(svg)
            self.assertEqual(generate_cards.read_mark(path), "abcdef123456")

    def test_missing_file_has_no_mark(self):
        self.assertIsNone(generate_cards.read_mark("/tmp/khong-ton-tai-12345.svg"))

    def test_stamp_is_idempotent(self):
        once = generate_cards.stamp_data_mark("<svg></svg>", "abcdef123456")
        twice = generate_cards.stamp_data_mark(once, "abcdef123456")
        self.assertEqual(once, twice)


class TestDryRunAndQuiet(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = generate_cards.main(["--demo", "--all", "--dry-run", "--out", tmp])
            self.assertEqual(code, 0)
            self.assertEqual([f for f in os.listdir(tmp) if f.endswith(".svg")], [])
            self.assertIn("[dry-run]", out.getvalue())

    def test_dry_run_still_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                generate_cards.main(["--demo", "--all", "--dry-run", "--out", tmp])
            self.assertFalse(os.path.exists(os.path.join(tmp, "stats.svg")))

    def test_quiet_prints_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                generate_cards.main(["--demo", "--cards", "--quiet", "--out", tmp])
            self.assertEqual(out.getvalue(), "")
            self.assertTrue(os.path.exists(os.path.join(tmp, "stats.svg")))
