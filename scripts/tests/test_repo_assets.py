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




class TestCommittedAssetsContent(unittest.TestCase):
    """Những thứ phải có trong *file đã commit*, không phải trong hàm vẽ."""

    def test_every_asset_has_a_title(self):
        # Thẻ <title> là thứ trình đọc màn hình đọc lên thay cho hình.
        # Ngoại lệ: ảnh trang trí thuần (role="presentation") thì không có
        # gì để đọc — nhưng bù lại phải mang aria-hidden.
        for name in asset_files():
            text = read(name)
            if 'role="presentation"' in text:
                self.assertIn('aria-hidden="true"', text, name)
                continue
            self.assertRegex(text, r"<title[^>]*>[^<]+</title>", name)

    def test_every_asset_declares_a_description(self):
        for name in asset_files():
            text = read(name)
            if 'role="presentation"' in text:
                continue
            self.assertIn("<desc", text, name)

    def test_no_asset_is_empty_or_tiny(self):
        for name in asset_files():
            self.assertGreater(len(read(name)), 500, name)

    def test_no_asset_contains_python_placeholder(self):
        # Dấu hiệu file được ghi từ template mà quên thay biến.
        for name in asset_files():
            text = read(name)
            for token in ("{", "}", "%s", "@FONT@"):
                if token in ("{", "}"):
                    continue
                self.assertNotIn(token, text, name)

    def test_no_trailing_whitespace_in_drawn_text(self):
        for name in asset_files():
            for line in read(name).split("\n"):
                if "<text" in line:
                    self.assertNotIn(" >", line, name)

    def test_no_asset_uses_emoji(self):
        # Emoji phụ thuộc font của máy người xem; repo vẽ mọi thứ bằng path.
        for name in asset_files():
            text = read(name)
            self.assertFalse(
                any(0x1F300 <= ord(ch) <= 0x1FAFF for ch in text), name)


class TestLiveClockSlotsInFile(unittest.TestCase):
    """84 ô số phải thật sự nằm trong file đã commit."""

    def setUp(self):
        self.text = read("live-clock.svg")

    def test_has_24_hour_slots(self):
        self.assertEqual(len(re.findall(r'class="clockTime[^"]*" x="308"', self.text)), 24)

    def test_has_60_minute_slots(self):
        self.assertEqual(len(re.findall(r'class="clockTime[^"]*" x="324"', self.text)), 60)

    def test_exactly_one_slot_is_highlighted_per_column(self):
        hour = re.findall(r'class="clockTime nowSlot" x="308"', self.text)
        minute = re.findall(r'class="clockTime nowSlot" x="324"', self.text)
        self.assertEqual((len(hour), len(minute)), (1, 1))

    def test_hour_slots_cycle_in_a_day(self):
        self.assertIn("animation-duration: 86400s", self.text)

    def test_minute_slots_cycle_in_an_hour(self):
        self.assertIn("slotMin 3600s", self.text)

    def test_day_arc_ring_is_present(self):
        self.assertIn('r="95"', self.text)



class TestAssetsCrossRenderer(unittest.TestCase):
    """Những thứ một trình vẽ khắt khe (resvg) sẽ bỏ qua hoặc crash."""

    def test_no_font_shorthand(self):
        for name in asset_files():
            for line in read(name).split("\n"):
                self.assertNotIn("font:", line.replace("font-family", ""), name)

    def test_no_filter_on_gradient_ellipse(self):
        # resvg panic khi tính vùng lọc cho ellipse tô gradient lấn ra ngoài.
        for name in asset_files():
            for line in read(name).split("\n"):
                if "<ellipse" in line:
                    self.assertNotIn("filter=", line, name)

    def test_every_url_reference_exists(self):
        for name in asset_files():
            text = read(name)
            defined = set(re.findall(r'id="([^"]+)"', text))
            used = set(re.findall(r"url\(#([^)]+)\)", text))
            self.assertEqual(sorted(used - defined), [], name)

    def test_no_negative_zero_numbers(self):
        # '-0' xuất hiện khi một phép tính ra -0.0; vô hại nhưng là dấu hiệu
        # của toạ độ suy biến.
        for name in asset_files():
            self.assertNotIn('="-0"', read(name), name)



RE_HEX = re.compile(r"#[0-9A-Fa-f]{3,8}")


class TestAssetShape(unittest.TestCase):
    """Hình dạng chung của mọi ảnh đã commit."""

    def test_every_asset_has_a_title_and_aria_label(self):
        for name in asset_files():
            text = read(name)
            if 'role="presentation"' in text:
                # Đường kẻ trang trí: cố ý ẩn với trình đọc màn hình.
                self.assertIn('aria-hidden="true"', text, name)
                continue
            self.assertIn("<title>", text, name)
            self.assertIn("aria-label=", text, name)
            self.assertIn('role="img"', text, name)

    def test_no_script_or_foreign_object(self):
        for name in asset_files():
            text = read(name)
            for tag in ("<script", "<foreignObject", "javascript:", "onload="):
                self.assertNotIn(tag, text, name)

    def test_width_and_height_agree_with_viewbox(self):
        for name in asset_files():
            text = read(name)
            width = re.search(r'<svg[^>]*width="(\d+)"', text)
            height = re.search(r'<svg[^>]*height="(\d+)"', text)
            box = re.search(r'viewBox="0 0 (\d+) (\d+)"', text)
            self.assertIsNotNone(box, name)
            self.assertEqual(int(width.group(1)), int(box.group(1)), name)
            self.assertEqual(int(height.group(1)), int(box.group(2)), name)

    def test_every_colour_is_a_hex_or_a_url(self):
        for name in asset_files():
            for value in re.findall(r'(?:fill|stroke|stop-color)="([^"]+)"',
                                    read(name)):
                # "freeze"/"remove" là chế độ của <animate fill=…>, không
                # phải màu; "none"/"transparent"/"currentColor" là từ khoá.
                if value in ("none", "freeze", "remove", "transparent",
                             "currentColor", "inherit"):
                    continue
                if not value.startswith(("url(", "#")):
                    self.fail("%s: màu %r không phải hex" % (name, value))

    def test_assets_stay_under_the_budget(self):
        for name in asset_files():
            size = os.path.getsize(os.path.join(ASSETS, name))
            self.assertLess(size, 40 * 1024, "%s nặng %d byte" % (name, size))

    def test_every_asset_has_motion(self):
        for name in asset_files():
            text = read(name)
            self.assertTrue("@keyframes" in text or "<animate" in text,
                            "%s không có hoạt ảnh nào" % name)

if __name__ == "__main__":
    unittest.main()
