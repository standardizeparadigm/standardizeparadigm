# -*- coding: utf-8 -*-
"""Test cửa vào dòng lệnh: xuất file, chế độ demo, theme, ngôn ngữ."""

import os
import shutil
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
