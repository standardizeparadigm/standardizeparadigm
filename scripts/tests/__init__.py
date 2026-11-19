# -*- coding: utf-8 -*-
"""Bộ test cho svgkit.

Chạy:
    python3 -m unittest discover -s scripts/tests -t scripts -v
"""

import os
import sys

# Cho phép `from helpers import ...` trong mọi file test, dù chạy bằng
# unittest discover hay chạy trực tiếp một file.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
