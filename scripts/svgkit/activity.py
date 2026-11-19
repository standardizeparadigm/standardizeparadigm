#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
activity.py — Thẻ hoạt động contribution (dữ liệu thật từ GitHub).

Vẽ 14 ngày gần nhất dưới dạng cột, kèm tổng cả năm và hai chuỗi
(streak) hiện tại / dài nhất. Nếu không lấy được dữ liệu, hàm trả None
để workflow giữ nguyên ảnh cũ thay vì ghi đè bằng thẻ rỗng.
"""

from .primitives import esc, human, icon, open_svg

WEEKDAY_SHORT = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
WEEKDAY_SHORT_EN = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def _stat_block(pal, x, icon_name, value, label, delay):
    return [
        '  <g class="fadeUp" style="animation-delay:%.2fs">' % delay,
        '    <rect x="%d" y="58" width="184" height="52" rx="12" fill="%s" '
        'stroke="%s" stroke-opacity=".8"/>' % (x, pal.panel, pal.stroke),
        icon(icon_name, x + 12, 71, pal.accent3, 0.85, 1.7),
        '    <text x="%d" y="86" class="bigValue">%s</text>'
        % (x + 44, esc(value)),
        '    <text x="%d" y="101" class="midLabel">%s</text>'
        % (x + 44, esc(label)),
        '  </g>',
    ]


def activity_card(pal, contrib, dt, t, width=640, height=258):
    """contrib = {total, days:[(date, count)...], streak_current, streak_longest}."""
    if not contrib or not contrib.get("days"):
        return None

    days = contrib["days"][-14:]
    stamp = dt.strftime("%d/%m · %H:%M")
    total = contrib.get("total", 0)
    current = contrib.get("streak_current", 0)
    longest = contrib.get("streak_longest", 0)
    weekdays = WEEKDAY_SHORT if t.lang == "vi" else WEEKDAY_SHORT_EN

    parts = open_svg(pal, width, height, "contribution activity card")
    parts.append('  <g class="fadeUp">')
    parts.append('    <rect x="22" y="22" width="4" height="18" rx="2" '
                 'fill="url(#accentGrad)"/>')
    parts.append('    <text x="36" y="37" class="cardTitle">%s</text>'
                 % esc(t("act.title")))
    parts.append('    <text x="618" y="36" text-anchor="end" class="cardSub">%s</text>'
                 % esc(t("act.sub", stamp=stamp)))
    parts.append('  </g>')

    parts += _stat_block(pal, 22, "spark", human(total), t("act.total"), 0.10)
    parts += _stat_block(pal, 222, "flame", "%s %s" % (human(current), t("act.days")),
                         t("act.streak"), 0.18)
    parts += _stat_block(pal, 422, "trophy", "%s %s" % (human(longest), t("act.days")),
                         t("act.best"), 0.26)

    # nhãn khu vực biểu đồ
    parts.append('  <g class="fadeUp" style="animation-delay:.32s">')
    parts.append('    <text x="22" y="128" class="footNote" '
                 'style="letter-spacing:1.2px">%s</text>' % esc(t("act.range")))
    today_count = days[-1][1] if days else 0
    parts.append('    <text x="618" y="128" text-anchor="end" class="footNote">'
                 '%s</text>' % esc(t("act.today", n=today_count)))
    parts.append('  </g>')

    # lưới ngang
    baseline = 208
    top = 144
    for gy in (top, 165, 186, baseline):
        parts.append('    <path d="M22 %dH618" stroke="%s" stroke-opacity=".10" '
                     'stroke-width="1"/>' % (gy, pal.label))

    peak = max([c for _, c in days] + [1])
    slot = (width - 44) / float(len(days))
    bar_w = min(26.0, slot * 0.62)

    for i, (day, count) in enumerate(days):
        cx = 22 + i * slot + slot / 2.0
        x = cx - bar_w / 2.0
        ratio = count / float(peak)
        bar_h = 4 + ratio * (baseline - top - 4)
        is_today = (i == len(days) - 1)
        fill = "url(#barGradV)" if count else pal.stroke
        opacity = "1" if count else ".7"
        delay = 0.12 + i * 0.035
        parts.append('  <g class="fadeUp" style="animation-delay:%.2fs">' % (delay * 0.8))
        parts.append('    <rect x="%.1f" y="%d" width="%.1f" height="%.1f" rx="%.1f" '
                     'fill="%s" opacity="%s"%s>'
                     % (x, baseline - bar_h, bar_w, bar_h,
                        min(6.0, bar_w / 2.0), fill, opacity,
                        ' filter="url(#glowSoft)"' if is_today else ""))
        if count:
            parts.append('      <animate attributeName="height" from="0" to="%.1f" '
                         'dur=".9s" begin="%.2fs" fill="freeze" calcMode="spline" '
                         'keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>'
                         % (bar_h, delay))
            parts.append('      <animate attributeName="y" from="%d" to="%.1f" '
                         'dur=".9s" begin="%.2fs" fill="freeze" calcMode="spline" '
                         'keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>'
                         % (baseline, baseline - bar_h, delay))
        parts.append('    </rect>')
        if is_today:
            parts.append('    <circle cx="%.1f" cy="%.1f" r="3.4" fill="%s" '
                         'class="pulse"/>' % (cx, baseline - bar_h - 10, pal.accent3))
        parts.append('  </g>')
        # nhãn thứ
        try:
            wd = int(day.strftime("%w"))          # 0 = Chủ nhật
            wd_index = (wd + 6) % 7              # 0 = thứ Hai
        except AttributeError:
            wd_index = i % 7
        color = pal.accent3 if is_today else pal.dim
        parts.append('  <text x="%.1f" y="224" text-anchor="middle" class="fMono" '
                     'style="font-size:8px;fill:%s;letter-spacing:.3px">%s</text>'
                     % (cx, color, weekdays[wd_index]))

    parts.append('  <g class="fadeUp" style="animation-delay:.7s">')
    parts.append('    <circle cx="26" cy="242" r="3" fill="%s" class="pulse"/>'
                 % pal.accent)
    parts.append('    <text x="36" y="245" class="footNote">%s</text>'
                 % esc(t("act.foot", stamp=stamp)))
    parts.append('  </g>')
    parts.append("</svg>")
    return "\n".join(parts)
