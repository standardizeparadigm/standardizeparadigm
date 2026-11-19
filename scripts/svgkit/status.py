#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
status.py — Dải trạng thái các workflow, vẽ ngay trong repo.

Vì sao không dùng badge của shields.io?

    shields cần biết *file workflow nằm trên nhánh mặc định*. Workflow mới
    tạo trên một nhánh thì badge trả "repo or workflow not found"; workflow
    chưa từng chạy thì trả "no status". Nhìn vào trang là thấy hai ô đỏ.

    Dải này đọc thẳng GitHub Actions API bằng token của repo, vẽ ra một file
    SVG rồi commit — đúng triết lý của cả trang: ảnh nằm trong repo, không
    phụ thuộc dịch vụ ngoài, không bao giờ "not found".
"""

from .api import to_vn
from .primitives import esc, open_svg

# Trạng thái → (màu, khoá i18n). Màu cố định theo nghĩa, không theo theme:
# xanh = ổn, đỏ = lỗi, hổ phách = đang chạy.
STATE_STYLE = {
    "passing": ("#34D399", "status.passing"),
    "failing": ("#F87171", "status.failing"),
    "running": ("#FBBF24", "status.running"),
    "none": ("#7A8CA3", "status.none"),
    "missing": ("#60A5FA", "status.missing"),
    "unknown": ("#7A8CA3", "status.unknown"),
}

# Workflow nào hiện trên dải. Thêm workflow mới = thêm một dòng ở đây.
WORKFLOWS = [
    ("profile-3d.yml", "3D CONTRIB"),
    ("profile-cards.yml", "STATS CARDS"),
    ("live-clock.yml", "LIVE CLOCK"),
    ("readme-tend.yml", "README GARDEN"),
    ("health.yml", "HEALTH"),
    ("welcome.yml", "WELCOME"),
    ("status.yml", "STATUS"),
]

PILL_W = 150
GAP = 8
MARGIN = 18
STRIP_H = 74


def width_for(count):
    """Chiều rộng cần cho `count` viên thuốc (để cả dải cân đối)."""
    return MARGIN * 2 + count * PILL_W + max(0, count - 1) * GAP


def _pill(pal, x, name, state, t, delay):
    color, key = STATE_STYLE.get(state, STATE_STYLE["unknown"])
    label = t(key)
    parts = ['  <g class="fadeUp" style="animation-delay:%.2fs">' % delay]
    parts.append('    <rect x="%d" y="9" width="%d" height="40" rx="11" '
                 'fill="%s" fill-opacity=".85" stroke="%s" stroke-opacity=".55"/>'
                 % (x, PILL_W, pal.panel, pal.stroke))
    parts.append('    <rect x="%d" y="9" width="%d" height="20" rx="10" '
                 'fill="url(#gloss)" opacity=".5"/>' % (x, PILL_W))
    if state == "running":
        # vòng cung khuyết quay tròn: dấu hiệu "đang chạy" rõ hơn nhấp nháy
        parts.append('    <circle cx="%d" cy="29" r="9" fill="none" stroke="%s" '
                     'stroke-width="1.7" stroke-opacity=".8" '
                     'stroke-dasharray="13 44" stroke-linecap="round" '
                     'class="spinDot"/>' % (x + 17, color))
    elif state == "passing":
        parts.append('    <circle cx="%d" cy="29" r="9" fill="none" stroke="%s" '
                     'stroke-opacity=".35" class="pulseSlow"/>' % (x + 17, color))
    parts.append('    <circle cx="%d" cy="29" r="4.4" fill="%s"%s/>'
                 % (x + 17, color,
                    ' filter="url(#glow)"' if state in ("passing", "running") else ""))
    parts.append('    <text x="%d" y="25" class="fMono" style="font:600 7.5px %s;'
                 'fill:%s;letter-spacing:.9px">%s</text>'
                 % (x + 30, pal.mono, pal.dim, esc(name)))
    parts.append('    <text x="%d" y="39" class="fSans" style="font:800 10px %s;'
                 'fill:%s;letter-spacing:.4px">%s</text>'
                 % (x + 30, pal.font, color, esc(label)))
    parts.append("  </g>")
    return parts


def status_strip(pal, rows, dt, t, width=None):
    """Vẽ dải trạng thái. `rows` = [(tên_ngắn, trạng_thái), ...]."""
    dt = to_vn(dt)
    if not rows:
        rows = [("—", "unknown")]
    width = width or width_for(len(rows))
    stamp = dt.strftime("%d/%m · %H:%M")

    parts = open_svg(pal, width, STRIP_H, t("status.title"),
                     desc=t("status.desc", stamp=stamp), halo=False, radius=14)
    parts.append('  <g clip-path="url(#cardBody)">')
    parts.append('    <rect x="-160" y="0" width="150" height="%d" '
                 'fill="url(#sheenGrad)" class="sheen" '
                 'style="animation-duration:9s"/>' % (STRIP_H - 18))
    parts.append("  </g>")

    x = MARGIN
    for index, (name, state) in enumerate(rows):
        parts += _pill(pal, x, name, state, t, 0.06 * index)
        x += PILL_W + GAP

    parts.append('  <g class="fadeUp" style="animation-delay:.5s">')
    parts.append('    <circle cx="%d" cy="%d" r="3" fill="%s" class="pulse"/>'
                 % (MARGIN + 4, STRIP_H - 12, pal.accent))
    parts.append('    <text x="%d" y="%d" class="footNote">%s</text>'
                 % (MARGIN + 14, STRIP_H - 9, esc(t("status.foot", stamp=stamp))))
    parts.append('  </g>')
    parts.append("</svg>")
    return "\n".join(parts)
