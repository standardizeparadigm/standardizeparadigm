#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
svgkit — bộ vẽ SVG cho profile README.

Mỗi file một việc:
    palette.py     màu, theme, xếp hạng
    i18n.py        chữ tiếng Việt / tiếng Anh
    primitives.py  escape, icon, CSS, defs
    hero.py        ảnh bìa
    divider.py     đường kẻ + chân trang
    cards.py       thẻ thống kê, thẻ ngôn ngữ
    clock.py       đồng hồ Việt Nam
    activity.py    thẻ hoạt động contribution
    status.py      dải trạng thái các workflow
    api.py         GitHub REST + GraphQL

Dùng:
    from svgkit import get_palette, i18n, hero, divider
"""

__version__ = "2.1.0"

from . import api, i18n  # noqa: F401
from .activity import activity_card  # noqa: F401
from .cards import langs_card, stats_card, waiting_card  # noqa: F401
from .clock import clock_card  # noqa: F401
from .divider import divider, footer  # noqa: F401
from .hero import hero  # noqa: F401
from .palette import (DEFAULT_THEME, Palette, THEMES, get_palette, grade,  # noqa: F401
                      lang_color, theme_names)
from .status import status_strip  # noqa: F401

__all__ = [
    "api", "i18n", "activity_card", "langs_card", "stats_card", "waiting_card",
    "clock_card", "divider", "footer", "hero", "status_strip", "get_palette", "grade",
    "lang_color", "theme_names", "Palette", "THEMES", "DEFAULT_THEME",
]
