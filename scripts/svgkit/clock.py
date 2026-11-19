#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clock.py — Thẻ đồng hồ "sống" theo giờ Việt Nam.

Kim giờ/kim phút được đặt đúng vị trí tại thời điểm vẽ, rồi tiếp tục quay
bằng CSS (12h / 1h / 60s mỗi vòng). Kim giây lệch pha theo số giây thật
nên nhìn như đồng hồ thật giữa hai lần workflow cập nhật.
"""

import math

from .primitives import esc, open_svg


def _greeting_key(hour):
    if 5 <= hour < 11:
        return "clock.greet.morning"
    if 11 <= hour < 13:
        return "clock.greet.noon"
    if 13 <= hour < 18:
        return "clock.greet.afternoon"
    if 18 <= hour < 23:
        return "clock.greet.evening"
    return "clock.greet.night"


def _sun_moon(pal, hour, x, y):
    """Mặt trời ban ngày, trăng khuyết ban đêm — vẽ bằng path, không emoji."""
    if 6 <= hour < 18:
        parts = ['<g stroke="%s" stroke-width="1.8" stroke-linecap="round" '
                 'fill="none">' % pal.accent3]
        parts.append('<circle cx="%s" cy="%s" r="4.2"/>' % (x, y))
        for i in range(8):
            angle = math.radians(i * 45)
            parts.append('<path d="M%.2f %.2fL%.2f %.2f"/>'
                         % (x + 7 * math.cos(angle), y + 7 * math.sin(angle),
                            x + 10 * math.cos(angle), y + 10 * math.sin(angle)))
        parts.append('</g>')
        return "".join(parts)
    return ('<path d="M%s %sa4.6 4.6 0 106.4 6.4 5.6 5.6 0 01-%s -%s" '
            'fill="%s"/>'
            % (x, y - 5, 0, 0, pal.accent3))


def _dial(pal, cx, cy, radius):
    parts = ['  <g class="fadeUp" style="animation-delay:.12s">']
    parts.append('    <circle cx="%d" cy="%d" r="%d" fill="url(#halo)"/>'
                 % (cx, cy, radius + 30))
    parts.append('    <circle cx="%d" cy="%d" r="%d" fill="%s" stroke="url(#edge)" '
                 'stroke-width="3"/>' % (cx, cy, radius, pal.bg_bot))
    parts.append('    <circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
                 'stroke-opacity=".65" stroke-width="1" stroke-dasharray="2 5" '
                 'class="spinSlow" style="transform-origin:%dpx %dpx;'
                 'animation-duration:40s"/>'
                 % (cx, cy, radius + 9, pal.accent, cx, cy))
    for i in range(60):
        angle = math.radians(i * 6 - 90)
        major = (i % 5 == 0)
        inner = radius - (13 if major else 6)
        x1, y1 = cx + inner * math.cos(angle), cy + inner * math.sin(angle)
        x2, y2 = cx + (radius - 3) * math.cos(angle), cy + (radius - 3) * math.sin(angle)
        parts.append('    <path d="M%.2f %.2fL%.2f %.2f" stroke="%s" '
                     'stroke-width="%s" stroke-linecap="round" opacity="%s"/>'
                     % (x1, y1, x2, y2,
                        pal.accent3 if major else pal.stroke,
                        "2" if major else "1",
                        ".85" if major else ".55"))
    parts.append('  </g>')
    return parts


def _hands(pal, cx, cy, hour, minute, second):
    hour_angle = ((hour % 12) + minute / 60.0) * 30.0
    minute_angle = (minute + second / 60.0) * 6.0
    return [
        '  <g transform="rotate(%.3f %d %d)">' % (hour_angle, cx, cy),
        '    <g class="hourHand" style="--cx:%dpx;--cy:%dpx;animation-delay:%.3fs">'
        % (cx, cy, -((hour % 12) * 3600 + minute * 60 + second)),
        '      <rect x="%d" y="%d" width="6" height="40" rx="3" fill="%s"/>'
        % (cx - 3, cy - 33, pal.title),
        '    </g>',
        '  </g>',
        '  <g transform="rotate(%.3f %d %d)">' % (minute_angle, cx, cy),
        '    <g class="minHand" style="--cx:%dpx;--cy:%dpx;animation-delay:%.3fs">'
        % (cx, cy, -(minute * 60 + second)),
        '      <rect x="%d" y="%d" width="4" height="56" rx="2" fill="%s" '
        'fill-opacity=".78"/>' % (cx - 2, cy - 47, pal.accent3),
        '    </g>',
        '  </g>',
        '  <g class="secHand" style="--cx:%dpx;--cy:%dpx;animation-delay:%.3fs">'
        % (cx, cy, -second),
        '    <path d="M%d %dV%d" stroke="%s" stroke-width="2" stroke-linecap="round" '
        'filter="url(#glow)"/>' % (cx, cy + 12, cy - 60, pal.accent),
        '    <circle cx="%d" cy="%d" r="4.5" fill="%s"/>' % (cx, cy - 60, pal.accent3),
        '  </g>',
        '  <circle cx="%d" cy="%d" r="6" fill="%s" stroke="%s" stroke-width="2.4"/>'
        % (cx, cy, pal.bg_bot, pal.accent),
        '  <circle cx="%d" cy="%d" r="2" fill="%s"/>' % (cx, cy, "#FFFFFF"),
    ]


def clock_card(pal, dt, t, width=640, height=258):
    hour, minute = dt.hour, dt.minute
    second = dt.second + dt.microsecond / 1000000.0
    cx, cy, radius = 122, 140, 74
    px, bar_w = 244, 372
    done = ((hour * 60 + minute) / 1440.0) * 100

    parts = open_svg(pal, width, height, "dong ho Viet Nam cap nhat moi 5 phut")
    parts.append('  <clipPath id="cardClip3"><rect x="0" y="0" width="%d" '
                 'height="%d" rx="18"/></clipPath>' % (width, height))
    parts.append('  <g clip-path="url(#cardClip3)"><rect x="-200" y="-60" '
                 'width="170" height="380" fill="url(#sheenGrad)" class="sheen" '
                 'opacity=".45" style="animation-duration:9s"/></g>')

    parts.append('  <g class="fadeUp">')
    parts.append('    <rect x="22" y="22" width="4" height="18" rx="2" '
                 'fill="url(#accentGrad)"/>')
    parts.append('    <text x="36" y="37" class="cardTitle">%s</text>'
                 % esc(t("clock.title")))
    parts.append('    <text x="618" y="36" text-anchor="end" class="cardSub">%s</text>'
                 % esc(t("clock.sub")))
    parts.append('  </g>')

    parts += _dial(pal, cx, cy, radius)
    parts += _hands(pal, cx, cy, hour, minute, second)

    # bảng số bên phải
    parts.append('  <g class="fadeUp" style="animation-delay:.2s">')
    parts.append('    <text x="%d" y="74" class="clockLabel">%s</text>'
                 % (px, esc(t("clock.label"))))
    parts.append('    <text x="%d" y="124" class="clockTime" fill="url(#titleGrad)">'
                 '%s</text>' % (px, dt.strftime("%H:%M")))
    parts.append('    <text x="%d" y="148" class="clockDate">%s · %s</text>'
                 % (px, esc(t.weekday(dt.weekday())), dt.strftime("%d/%m/%Y")))
    parts.append('  </g>')

    greeting = t(_greeting_key(hour))
    pill_w = 34 + len(greeting) * 6.6
    parts.append('  <g class="fadeUp" style="animation-delay:.3s">')
    parts.append('    <rect x="%d" y="160" width="%.0f" height="24" rx="12" '
                 'fill="%s" fill-opacity=".85" stroke="%s" stroke-opacity=".85"/>'
                 % (px, pill_w, pal.panel, pal.accent2))
    parts.append('    <circle cx="%d" cy="172" r="3.4" fill="%s" class="pulse"/>'
                 % (px + 14, pal.accent3))
    parts.append('    <text x="%d" y="176" class="clockBig">%s</text>'
                 % (px + 26, esc(greeting)))
    parts.append(_sun_moon(pal, hour, px + pill_w + 26, 172))
    parts.append('  </g>')

    # tiến độ trong ngày
    parts.append('  <g class="fadeUp" style="animation-delay:.4s">')
    parts.append('    <text x="%d" y="206" class="footNote" '
                 'style="letter-spacing:1.1px">%s</text>'
                 % (px, esc(t("clock.day"))))
    parts.append('    <text x="%d" y="206" text-anchor="end" class="legendValue">'
                 '%.0f%%</text>' % (px + bar_w, done))
    parts.append('    <rect x="%d" y="212" width="%d" height="8" rx="4" '
                 'fill="%s" fill-opacity=".6"/>' % (px, bar_w, pal.panel))
    parts.append('    <rect x="%d" y="212" width="%.1f" height="8" rx="4" '
                 'fill="url(#barGrad)">' % (px, bar_w * done / 100.0))
    parts.append('      <animate attributeName="width" from="0" to="%.1f" '
                 'dur="1.3s" begin=".3s" fill="freeze" calcMode="spline" '
                 'keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>'
                 % (bar_w * done / 100.0))
    parts.append('      <animate attributeName="opacity" values=".75;1;.75" '
                 'dur="3.4s" repeatCount="indefinite"/>')
    parts.append('    </rect>')
    parts.append('    <circle cx="%.1f" cy="216" r="5" fill="%s" '
                 'filter="url(#glow)" class="pulse"/>'
                 % (px + bar_w * done / 100.0, pal.accent3))
    parts.append('  </g>')

    parts.append('  <g class="fadeUp" style="animation-delay:.5s">')
    parts.append('    <circle cx="%d" cy="242" r="3" fill="%s" class="pulse"/>'
                 % (px, pal.accent))
    parts.append('    <text x="%d" y="245" class="footNote">%s</text>'
                 % (px + 10, esc(t("clock.foot", hhmm=dt.strftime("%H:%M")))))
    parts.append('  </g>')
    parts.append("</svg>")
    return "\n".join(parts)
