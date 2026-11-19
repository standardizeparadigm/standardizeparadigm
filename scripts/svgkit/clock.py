#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clock.py — Thẻ đồng hồ "sống" theo giờ Việt Nam.

Kim giờ/kim phút được đặt đúng vị trí tại thời điểm vẽ, rồi tiếp tục quay
bằng CSS (12h / 1h / 60s mỗi vòng). Kim giây lệch pha theo số giây thật
nên nhìn như đồng hồ thật giữa hai lần workflow cập nhật.
"""

import math

from .api import to_vn
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
    # Trăng khuyết: một hình tròn bị "cắn" bởi một hình tròn khác, cắt bằng
    # mask. Bản cũ dùng cung tròn có bán kính truyền vào là 0 nên mọi trình
    # vẽ đều ra một cục méo; cách này đúng ở mọi bộ dựng, kể cả trình xem
    # ảnh không hiểu CSS.
    side = 22.0
    return ('<mask id="moonBite" maskUnits="userSpaceOnUse" '
            'x="%.1f" y="%.1f" width="%.0f" height="%.0f">'
            '<rect x="%.1f" y="%.1f" width="%.0f" height="%.0f" fill="#FFFFFF"/>'
            '<circle cx="%.1f" cy="%.1f" r="5.0" fill="#000000"/></mask>'
            '<circle cx="%.1f" cy="%.1f" r="6.4" fill="%s" mask="url(#moonBite)"/>'
            % (x - side / 2, y - side / 2, side, side,
               x - side / 2, y - side / 2, side, side,
               x + 4.6, y - 2.4,
               x, y, pal.accent3))


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
    # Vệt sáng quét quanh vành: kim quay đã "sống", vành cũng phải thở.
    parts.append('    <circle cx="%d" cy="%d" r="%d" fill="none" '
                 'stroke="url(#accentGrad)" stroke-width="2" '
                 'stroke-dasharray="70 320" stroke-opacity=".55" class="spinSlow" '
                 'style="transform-origin:%dpx %dpx;animation-duration:18s"/>'
                 % (cx, cy, radius + 1, cx, cy))
    for i in range(60):
        angle = math.radians(i * 6 - 90)
        major = (i % 5 == 0)
        inner = radius - (13 if major else 6)
        x1, y1 = cx + inner * math.cos(angle), cy + inner * math.sin(angle)
        x2, y2 = cx + (radius - 3) * math.cos(angle), cy + (radius - 3) * math.sin(angle)
        path = ('M%.2f %.2fL%.2f %.2f' % (x1, y1, x2, y2))
        if major:
            # 12 vạch giờ sáng lần lượt như đèn chạy: một làn sóng đi vòng
            # quanh mặt đồng hồ 6 giây/lượt, lệch pha theo đúng vị trí vạch.
            parts.append('    <path d="%s" stroke="%s" stroke-width="2" '
                         'stroke-linecap="round" opacity=".85">'
                         % (path, pal.accent3))
            parts.append('      <animate attributeName="opacity" '
                         'values=".45;1;.45" dur="6s" begin="%.2fs" '
                         'repeatCount="indefinite"/>' % (i / 10.0))
            parts.append('    </path>')
        else:
            parts.append('    <path d="%s" stroke="%s" stroke-width="1" '
                         'stroke-linecap="round" opacity=".55"/>'
                         % (path, pal.stroke))
    parts.append('  </g>')
    return parts


def _day_arc(pal, cx, cy, radius, hour, minute, second):
    """Vòng cung ngoài cùng: hôm nay đã trôi qua bao nhiêu phần.

    Đây là thứ mặt đồng hồ thường không nói được. Nhìn kim thì biết mấy
    giờ; nhìn vòng cung thì biết ngày còn dài hay đã gần hết — một vòng
    đầy 360° ứng với tròn 24 giờ, nên 6 giờ sáng là đúng một phần tư.
    """
    sweep = 360.0 * (hour * 3600 + minute * 60 + second) / 86400.0
    ring = radius + 21
    parts = ['  <g class="fadeUp" style="animation-delay:.24s">']
    parts.append('    <circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
                 'stroke-opacity=".16" stroke-width="3"/>'
                 % (cx, cy, ring, pal.accent))
    # Ngay sau nửa đêm cung chỉ còn vài phần nghìn độ: vẽ ra chỉ thành một
    # chấm méo, nên bỏ hẳn cho sạch.
    if sweep > 0.4:
        end = math.radians(sweep - 90.0)
        large = 1 if sweep > 180.0 else 0
        x, y = cx + ring * math.cos(end), cy + ring * math.sin(end)
        parts.append('    <path d="M%d %dA%d %d 0 %d 1 %.2f %.2f" fill="none" '
                     'stroke="url(#accentGrad)" stroke-width="3" '
                     'stroke-linecap="round" stroke-opacity=".8"/>'
                     % (cx, cy - ring, ring, ring, large, x, y))
        parts.append('    <circle cx="%.2f" cy="%.2f" r="3.4" fill="%s">'
                     % (x, y, pal.accent3))
        parts.append('      <animate attributeName="r" values="2.6;4.4;2.6" '
                     'dur="3.2s" repeatCount="indefinite"/>')
        parts.append('    </circle>')
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
        '    <circle cx="%d" cy="%d" r="2.6" fill="%s" fill-opacity=".8"/>'
        % (cx, cy + 12, pal.accent),
        '  </g>',
        '  <circle cx="%d" cy="%d" r="6" fill="%s" stroke="%s" stroke-width="2.4"/>'
        % (cx, cy, pal.bg_bot, pal.accent),
        '  <circle cx="%d" cy="%d" r="2" fill="%s"/>' % (cx, cy, "#FFFFFF"),
    ]


# Số giờ/phút tự nhảy mỗi phút, không cần JavaScript và không cần workflow
# chạy lại: 24 ô giờ + 60 ô phút xếp chồng đúng một chỗ, mỗi ô chỉ hiện trong
# khoảng thời gian của nó. Ô của ảnh chụp hiện sẵn (opacity 1) nên trình xem
# tĩnh — và người bật "giảm chuyển động" — vẫn thấy đúng giờ của ảnh chụp.
LIVE_TIME_CSS = """
    .liveHour text, .liveMin text { opacity: 0;
      animation: slotMin 3600s linear infinite; }
    .liveHour text { animation-name: slotHour; animation-duration: 86400s; }
    .liveHour text.nowSlot, .liveMin text.nowSlot { opacity: 1; }
    @keyframes slotMin  { 0%, 1.666% { opacity: 1 } 1.667%, 100% { opacity: 0 } }
    @keyframes slotHour { 0%, 4.166% { opacity: 1 } 4.167%, 100% { opacity: 0 } }
""".strip()

HOUR_X, COLON_X, MIN_X = 308, 316, 324
TIME_Y = 124


def _live_time(pal, px, hour, minute, second):
    """Ba khối: ô giờ, dấu hai chấm, ô phút.

    Độ trễ của mỗi ô = thời điểm ô đó bắt đầu hiện, tính từ lúc trang tải.
    Ô hiện tại nhận độ trễ âm (đang trong khung của nó) nên hiện ngay.
    """
    parts = ['  <g class="fadeUp" style="animation-delay:.2s">']
    parts.append('    <g class="liveHour" text-anchor="end" '
                 'fill="url(#titleGrad)">')
    for value in range(24):
        step = (value - hour) % 24
        delay = step * 3600 - (minute * 60 + second)
        parts.append('      <text class="clockTime%s" x="%d" y="%d" '
                     'style="animation-delay:%.1fs">%02d</text>'
                     % (" nowSlot" if value == hour else "", HOUR_X, TIME_Y,
                        delay, value))
    parts.append('    </g>')
    parts.append('    <text class="clockTime" x="%d" y="%d" '
                 'text-anchor="middle" fill="url(#accentGrad)">:</text>'
                 % (COLON_X, TIME_Y))
    parts.append('    <g class="liveMin" text-anchor="start" '
                 'fill="url(#titleGrad)">')
    for value in range(60):
        step = (value - minute) % 60
        delay = step * 60 - second
        parts.append('      <text class="clockTime%s" x="%d" y="%d" '
                     'style="animation-delay:%.1fs">%02d</text>'
                     % (" nowSlot" if value == minute else "", MIN_X, TIME_Y,
                        delay, value))
    parts.append('    </g>')
    parts.append('  </g>')
    return parts


def clock_card(pal, dt, t, width=640, height=258):
    # Mọi mốc thời gian đều quy về giờ Việt Nam, kể cả khi nơi gọi truyền UTC.
    dt = to_vn(dt)
    hour, minute = dt.hour, dt.minute
    second = dt.second + dt.microsecond / 1000000.0
    cx, cy, radius = 122, 140, 74
    px, bar_w = 244, 372
    done = ((hour * 60 + minute) / 1440.0) * 100

    parts = open_svg(pal, width, height, t("clock.title"),
                     desc=t("desc.clock"))
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

    parts.append('  <style>%s</style>' % LIVE_TIME_CSS)

    parts += _dial(pal, cx, cy, radius)
    parts += _day_arc(pal, cx, cy, radius, hour, minute, second)
    parts += _hands(pal, cx, cy, hour, minute, second)

    # bảng số bên phải
    parts.append('  <g class="fadeUp" style="animation-delay:.2s">')
    parts.append('    <text x="%d" y="74" class="clockLabel">%s</text>'
                 % (px, esc(t("clock.label"))))
    # Mốc thời gian đã vẽ, để không ai nhầm ảnh tĩnh là "giờ hiện tại".
    parts.append('    <text x="%d" y="74" text-anchor="end" class="cardSub">%s</text>'
                 % (px + bar_w, esc(t("clock.updated", hhmm=dt.strftime("%H:%M")))))
    parts += _live_time(pal, px, hour, minute, second)
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
    # Còn bao lâu nữa hết ngày: phần trăm nói "đã đi được bao xa", con số này
    # nói "còn bao xa" — cùng một dữ liệu, hai cách đọc, và cách thứ hai là
    # cách người ta thật sự cần lúc 23h.
    left_min = 24 * 60 - (hour * 60 + dt.minute)
    parts.append('    <text x="%d" y="206" text-anchor="end" class="footNote" '
                 'style="letter-spacing:.6px;fill:%s">%s</text>'
                 % (px + bar_w - 46, pal.dim,
                    esc(t("clock.left", h=left_min // 60, m=left_min % 60))))
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
                 % (px + 10, esc(t("clock.foot"))))
    parts.append('  </g>')
    parts.append("</svg>")
    return "\n".join(parts)
