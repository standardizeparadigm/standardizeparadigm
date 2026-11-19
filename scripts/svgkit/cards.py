#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cards.py — Hai thẻ dữ liệu: thống kê và ngôn ngữ.

Cả hai cùng kích thước 640x258 để đứng cạnh nhau cho thẳng hàng.
"""

from .palette import grade, lang_color
from .primitives import esc, human, icon, open_svg


def _header(pal, title, right_text):
    return [
        '  <g class="fadeUp">',
        '    <rect x="22" y="22" width="4" height="18" rx="2" '
        'fill="url(#accentGrad)"/>',
        '    <text x="36" y="37" class="cardTitle">%s</text>' % esc(title),
        '    <text x="618" y="36" text-anchor="end" class="cardSub">%s</text>'
        % esc(right_text),
        '  </g>',
    ]


def _footer(pal, text):
    return [
        '  <g class="fadeUp" style="animation-delay:.62s">',
        '    <circle cx="26" cy="242" r="3" fill="%s" class="pulse"/>' % pal.accent,
        '    <text x="36" y="245" class="footNote">%s</text>' % esc(text),
        '  </g>',
    ]


def _rank_ring(pal, percent, letter, label, progress_text,
               cx=528, cy=144, radius=56):
    import math
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - percent)
    parts = ['  <g class="fadeUp" style="animation-delay:.5s">']
    parts.append('    <circle cx="%d" cy="%d" r="%d" fill="url(#halo)" opacity=".85"/>'
                 % (cx, cy, radius + 26))
    parts.append('    <circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
                 'stroke-width="1" stroke-dasharray="2 6" stroke-opacity=".8" '
                 'class="spinSlow" style="transform-origin:%dpx %dpx;'
                 'animation-duration:34s"/>'
                 % (cx, cy, radius + 12, pal.accent2, cx, cy))
    parts.append('    <circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
                 'stroke-width="9" stroke-opacity=".18"/>'
                 % (cx, cy, radius, pal.accent))
    parts.append('    <circle cx="%d" cy="%d" r="%d" fill="none" '
                 'stroke="url(#accentGrad)" stroke-width="9" stroke-linecap="round" '
                 'transform="rotate(-90 %d %d)" stroke-dasharray="%.1f" '
                 'stroke-dashoffset="%.1f">'
                 % (cx, cy, radius, cx, cy, circumference, offset))
    parts.append('      <animate attributeName="stroke-dashoffset" from="%.1f" '
                 'to="%.1f" dur="1.6s" begin=".15s" fill="freeze" '
                 'calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>'
                 % (circumference, offset))
    parts.append('    </circle>')
    # Điểm sáng nằm đúng đầu cung tiến độ — mắt bám vào đó là biết rank tới đâu.
    angle = math.radians(-90 + 360 * percent)
    tip_x = cx + radius * math.cos(angle)
    tip_y = cy + radius * math.sin(angle)
    parts.append('    <g>')
    parts.append('      <circle cx="%.1f" cy="%.1f" r="10" fill="none" '
                 'stroke="%s" stroke-opacity=".45" class="pulseSlow"/>'
                 % (tip_x, tip_y, pal.accent3))
    parts.append('      <circle cx="%.1f" cy="%.1f" r="4.6" fill="%s" '
                 'filter="url(#glow)" class="pulse"/>'
                 % (tip_x, tip_y, pal.accent3))
    parts.append('    </g>')
    parts.append('    <text x="%d" y="%d" text-anchor="middle" class="fSans" '
                 'style="font:800 32px %s;fill:%s">%s</text>'
                 % (cx, cy + 6, pal.font, pal.title, esc(letter)))
    parts.append('    <text x="%d" y="%d" text-anchor="middle" class="fSans" '
                 'style="font:700 8.5px %s;fill:%s;letter-spacing:2px">%s</text>'
                 % (cx, cy + 24, pal.font, pal.label, esc(label)))
    parts.append('    <text x="%d" y="%d" text-anchor="middle" class="cardSub">'
                 '%s</text>' % (cx, cy + 80, esc(progress_text)))
    parts.append('  </g>')
    return parts


def stats_card(pal, data, dt, t, width=640, height=258):
    """Thẻ thống kê: 6 ô số liệu + vòng hạng."""
    letter, percent = grade(data)
    stamp = dt.strftime("%d/%m · %H:%M")
    parts = open_svg(pal, width, height, t("stats.title"),
                     desc=t("desc.stats"))
    parts.append('  <clipPath id="cardClip"><rect x="0" y="0" width="%d" '
                 'height="%d" rx="18"/></clipPath>' % (width, height))
    parts.append('  <g clip-path="url(#cardClip)">'
                 '<rect x="-200" y="-60" width="170" height="380" '
                 'fill="url(#sheenGrad)" class="sheen" opacity=".55"/></g>')

    parts += _header(pal, t("stats.title"), t("stats.updated", stamp=stamp))

    rows = [
        ("star", t("stats.stars"), data.get("stars")),
        ("fork", t("stats.forks"), data.get("forks")),
        ("repo", t("stats.repos"), data.get("repos")),
        ("users", t("stats.followers"), data.get("followers")),
        ("follow", t("stats.following"), data.get("following")),
        ("commit", t("stats.commits"), data.get("commits")),
    ]
    cols = [22, 216]
    row_y = [62, 120, 178]
    for i, (icon_name, label, value) in enumerate(rows):
        x = cols[i % 2]
        y = row_y[i // 2]
        parts.append('  <g class="fadeUp" style="animation-delay:%.2fs">'
                     % (0.08 + 0.07 * i))
        parts.append('    <rect x="%d" y="%d" width="180" height="50" rx="12" '
                     'fill="%s" stroke="%s" stroke-opacity=".85"/>'
                     % (x, y, pal.panel, pal.stroke))
        parts.append('    <rect x="%d" y="%d" width="34" height="34" rx="10" '
                     'fill="%s" fill-opacity=".14" stroke="%s" stroke-opacity=".45"/>'
                     % (x + 8, y + 8, pal.accent, pal.accent))
        parts.append(icon(icon_name, x + 15.5, y + 15.5, pal.accent3, 0.8, 1.7))
        shown = human(value) if value is not None else "-"
        parts.append('    <text x="%d" y="%d" class="tileValue">%s</text>'
                     % (x + 52, y + 27, esc(shown)))
        parts.append('    <text x="%d" y="%d" class="tileLabel">%s</text>'
                     % (x + 52, y + 41, esc(label)))
        parts.append('  </g>')

    parts += _rank_ring(pal, percent, letter, t("stats.rank"),
                        t("stats.progress", pct=int(percent * 100)))
    parts += _footer(pal, t("stats.foot"))
    parts.append("</svg>")
    return "\n".join(parts)


def langs_card(pal, data, dt, t, width=640, height=258):
    """Thẻ ngôn ngữ: thanh xếp chồng + chú giải 2 cột."""
    every = sorted((data.get("langs") or {}).items(), key=lambda kv: -kv[1])
    items = every[:8]
    if not items:
        items = [("Python", 1)]
        every = items
    # Phần trăm tính trên TOÀN BỘ byte code, không phải chỉ 8 ngôn ngữ đầu:
    # nhờ vậy "89.3%" đúng kể cả khi còn ngôn ngữ nhỏ không hiện ra.
    total = sum(v for _, v in every) or 1
    rest = every[8:]
    rest_pct = 100.0 * sum(v for _, v in rest) / total
    stamp = dt.strftime("%d/%m · %H:%M")

    parts = open_svg(pal, width, height, t("langs.title"),
                     desc=t("desc.langs"))
    parts += _header(pal, t("langs.title"), t("langs.sub"))

    bx, by, bw, bh = 22, 54, width - 44, 16
    parts.append('  <clipPath id="barClip"><rect x="%d" y="%d" width="%d" '
                 'height="%d" rx="8"/></clipPath>' % (bx, by, bw, bh))
    parts.append('  <rect x="%d" y="%d" width="%d" height="%d" rx="8" '
                 'fill="%s" stroke="%s" stroke-opacity=".7"/>'
                 % (bx, by, bw, bh, pal.panel, pal.stroke))
    parts.append('  <g clip-path="url(#barClip)">')
    x = float(bx)
    for i, (name, value) in enumerate(items):
        segment = bw * (value / float(total))
        parts.append('    <rect x="%.1f" y="%d" width="%.1f" height="%d" fill="%s">'
                     % (x, by, segment + 0.6, bh, lang_color(name, i)))
        parts.append('      <animate attributeName="width" from="0" to="%.1f" '
                     'dur="1.1s" begin="%.2fs" fill="freeze" calcMode="spline" '
                     'keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>'
                     % (segment + 0.6, 0.1 + 0.06 * i))
        parts.append('    </rect>')
        x += segment
    parts.append('    <rect x="%d" y="%d" width="%d" height="%.1f" fill="url(#gloss)"/>'
                 % (bx, by, bw, bh / 2.0))
    parts.append('    <rect x="-160" y="%d" width="150" height="%d" '
                 'fill="url(#sheenGrad)" class="sheen" '
                 'style="animation-duration:5.5s"/>' % (by - 6, bh + 12))
    parts.append('  </g>')

    col_x = [22, 330]
    y0 = 104
    for i, (name, value) in enumerate(items):
        cx = col_x[i % 2]
        y = y0 + (i // 2) * 32
        pct = 100.0 * value / total
        label = name if len(name) <= 14 else name[:13] + "…"
        parts.append('  <g class="fadeUp" style="animation-delay:%.2fs">'
                     % (0.18 + 0.06 * i))
        parts.append('    <circle cx="%d" cy="%d" r="5" fill="%s"/>'
                     % (cx + 5, y - 4, lang_color(name, i)))
        parts.append('    <text x="%d" y="%d" class="legendName">%s</text>'
                     % (cx + 18, y, esc(label)))
        parts.append('    <text x="%d" y="%d" text-anchor="end" class="legendValue">'
                     '%.1f%%</text>' % (cx + 262, y, pct))
        parts.append('    <rect x="%d" y="%d" width="262" height="3" rx="1.5" '
                     'fill="%s" fill-opacity=".55"/>' % (cx, y + 6, pal.panel))
        parts.append('    <rect x="%d" y="%d" width="%.1f" height="3" rx="1.5" '
                     'fill="%s" opacity=".95" class="growIn" '
                     'style="animation-delay:%.2fs;transform-origin:%dpx %dpx">'
                     % (cx, y + 6, 262 * pct / 100.0, lang_color(name, i),
                        0.24 + 0.06 * i, cx, y + 7.5))
        parts.append('    </rect>')
        parts.append('  </g>')

    if rest:
        parts.append('  <text x="618" y="%d" text-anchor="end" class="footNote">%s</text>'
                     % (height - 10, esc(t("langs.more", n=len(rest),
                                           pct=("%.1f" % rest_pct)))))
    parts += _footer(pal, t("langs.foot", stamp=stamp))
    parts.append("</svg>")
    return "\n".join(parts)


def waiting_card(pal, width, title, line1, line2):
    """Thẻ tạm khi chưa có dữ liệu (không bao giờ đè lên ảnh thật)."""
    parts = open_svg(pal, width, 258, title)
    parts.append('  <text x="%d" y="112" text-anchor="middle" class="fSans" '
                 'style="font:700 14px %s;fill:%s">%s</text>'
                 % (width // 2, pal.font, pal.text, esc(line1)))
    parts.append('  <text x="%d" y="138" text-anchor="middle" class="footNote" '
                 'style="font-size:10px">%s</text>' % (width // 2, esc(line2)))
    for i in range(3):
        parts.append('  <circle cx="%d" cy="170" r="4.5" fill="%s" class="pulse" '
                     'style="animation-delay:%.2fs"/>'
                     % (width // 2 - 18 + i * 18,
                        [pal.accent, pal.accent2, pal.accent3][i], i * 0.3))
    parts.append("</svg>")
    return "\n".join(parts)
