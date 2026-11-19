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
