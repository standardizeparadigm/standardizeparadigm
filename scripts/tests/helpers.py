# -*- coding: utf-8 -*-
"""Tiện ích dùng chung cho các file test."""

import os
import sys
import xml.dom.minidom as minidom

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


def parse(svg_text):
    """Parse SVG, trả về DOM. Ném lỗi nếu XML hỏng."""
    return minidom.parseString(svg_text.encode("utf-8"))


def assert_valid_svg(testcase, svg_text, label="svg"):
    testcase.assertIn("<svg", svg_text, "%s thiếu thẻ <svg>" % label)
    testcase.assertIn("</svg>", svg_text, "%s thiếu thẻ đóng </svg>" % label)
    testcase.assertIn('xmlns="http://www.w3.org/2000/svg"', svg_text,
                      "%s thiếu xmlns" % label)
    dom = parse(svg_text)
    testcase.assertEqual(dom.documentElement.tagName, "svg")
    return dom


def render_demo_all():
    """Vẽ toàn bộ thẻ ở chế độ demo, trả dict {tên file: nội dung}."""
    import shutil
    import tempfile

    import generate_cards

    tmp = tempfile.mkdtemp(prefix="cards-demo-")
    try:
        old = generate_cards.OUT_DIR
        generate_cards.OUT_DIR = tmp
        generate_cards.main(["--demo", "--all", "--out", tmp])
        generate_cards.OUT_DIR = old
        result = {}
        for name in sorted(os.listdir(tmp)):
            if name.endswith(".svg"):
                with open(os.path.join(tmp, name), encoding="utf-8") as handle:
                    result[name] = handle.read()
        return result
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
