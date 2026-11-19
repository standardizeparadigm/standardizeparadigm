#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử trên những ảnh **đã commit** trong `assets/`.

Test của từng renderer chứng minh *hàm vẽ* đúng. File này chứng minh *file
đang nằm trong repo* đúng — hai chuyện khác nhau: một ảnh có thể được sinh
ra từ phiên bản cũ của renderer và không ai vẽ lại.
"""

import os
import re
import unittest
import xml.dom.minidom as minidom

from helpers import SCRIPTS  # noqa: F401  (bảo đảm scripts/ nằm trong sys.path)

ROOT = os.path.dirname(SCRIPTS)
ASSETS = os.path.join(ROOT, "assets")


def asset_files():
    return sorted(n for n in os.listdir(ASSETS) if n.endswith(".svg"))


def read(name):
    with open(os.path.join(ASSETS, name), encoding="utf-8") as handle:
        return handle.read()


class TestCommittedAssets(unittest.TestCase):
    def test_assets_exist(self):
        self.assertGreaterEqual(len(asset_files()), 8)

    def test_every_asset_is_valid_xml(self):
        for name in asset_files():
            minidom.parseString(read(name).encode("utf-8"))

    def test_every_asset_has_viewbox_and_namespace(self):
        for name in asset_files():
            text = read(name)
            self.assertIn('xmlns="http://www.w3.org/2000/svg"', text, name)
            self.assertIn("viewBox=", text, name)

    def test_viewbox_matches_width_and_height(self):
        for name in asset_files():
            text = read(name)
            width = re.search(r'\bwidth="(\d+)"', text).group(1)
            height = re.search(r'\bheight="(\d+)"', text).group(1)
            self.assertIn('viewBox="0 0 %s %s"' % (width, height), text, name)

    def test_motion_can_be_turned_off(self):
        for name in asset_files():
            self.assertIn("prefers-reduced-motion", read(name), name)

    def test_single_data_marker(self):
        for name in asset_files():
            text = read(name)
            self.assertLessEqual(text.count("<!-- data:"), 1, name)


class TestLiveClockAsset(unittest.TestCase):
    """Ảnh đồng hồ đã commit phải tự nói nó chụp lúc nào."""

    def setUp(self):
        self.text = read("live-clock.svg")

    def test_has_snapshot_stamp(self):
        self.assertRegex(self.text, r"cập nhật \d\d:\d\d")

    def test_has_countdown_label(self):
        self.assertRegex(self.text, r"còn \d+g\d\d")

    def test_has_day_progress(self):
        self.assertIn("%", self.text)
        self.assertIn("clockTime", self.text)


if __name__ == "__main__":
    unittest.main()
