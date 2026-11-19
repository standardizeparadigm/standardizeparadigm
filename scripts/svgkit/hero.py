#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hero.py — Ảnh bìa động ở đầu trang.

Không cần dữ liệu GitHub, chỉ cần palette + thời điểm chạy. Toàn bộ chuyển
động là CSS/SMIL nên ảnh vẫn "sống" sau khi được commit.
"""

import random

from .primitives import esc, num, open_svg


def _grid(width, height, pal):
    parts = ['  <g opacity=".5">']
    for x in range(0, width + 1, 40):
        parts.append('    <path d="M%d 0V%d" stroke="%s" stroke-opacity=".05" '
                     'stroke-width="1"/>' % (x, height, pal.accent3))
    for y in range(0, height + 1, 40):
        parts.append('    <path d="M0 %dV%d" stroke="%s" stroke-opacity=".05" '
                     'stroke-width="1"/>' % (y, width, pal.accent3))
    parts.append("  </g>")
    return parts


def _stars(width, height, pal, seed=20260820):
    rnd = random.Random(seed)
    parts = []
    for _ in range(30):
        sx = rnd.uniform(20, width - 20)
        sy = rnd.uniform(14, height - 30)
        if 250 < sx < 830 and 55 < sy < 215:
            continue  # giữ vùng chữ sạch
        radius = rnd.uniform(0.7, 1.8)
        color = rnd.choice([pal.accent3, pal.title, pal.accent])
        delay = rnd.uniform(0, 4)
        parts.append('  <circle cx="%.0f" cy="%.0f" r="%.1f" fill="%s" '
                     'class="twinkle" style="animation-delay:-%.1fs"/>'
                     % (sx, sy, radius, color, delay))
    return parts


def _particles(pal, width, height, seed=77123):
    """Bụi sáng bay lên chậm — chi tiết nhỏ nhưng làm nền "thở"."""
    rnd = random.Random(seed)
    parts = ['  <g>']
    for index in range(14):
        px = rnd.uniform(30, width - 30)
        py = rnd.uniform(40, height - 50)
        if 250 < px < 840 and 40 < py < 220:
            px = rnd.uniform(30, 240)          # tránh vùng chữ
        radius = rnd.uniform(1.0, 2.2)
        rise = rnd.uniform(18, 40)
        duration = rnd.uniform(7, 13)
        begin = -rnd.uniform(0, 9)
        color = rnd.choice([pal.accent3, pal.accent])
        parts.append(
            '    <circle cx="%.0f" cy="%.0f" r="%.1f" fill="%s" opacity="0" '
            'class="dust">'
            '<animate attributeName="cy" values="%.0f;%.0f" dur="%.1fs" '
            'begin="%.1fs" repeatCount="indefinite"/>'
            '<animate attributeName="opacity" values="0;.7;0" dur="%.1fs" '
            'begin="%.1fs" repeatCount="indefinite"/>'
            '</circle>'
            % (px, py, radius, color, py + 6, py - rise, duration, begin,
               duration, begin))
    parts.append("  </g>")
    return parts


def _orbit(pal, cx=148, cy=140):
    parts = ['  <g>']
    parts.append('    <circle cx="%d" cy="%d" r="86" fill="url(#halo)" opacity=".9"/>'
                 % (cx, cy))
    parts.append('    <circle cx="%d" cy="%d" r="72" fill="none" stroke="%s" '
                 'stroke-opacity=".35" stroke-width="1"/>' % (cx, cy, pal.stroke))
    parts.append('    <circle cx="%d" cy="%d" r="55" fill="none" '
                 'stroke="url(#accentGrad)" stroke-width="1.4" stroke-dasharray="3 7" '
                 'class="spinSlow" style="transform-origin:%dpx %dpx"/>'
                 % (cx, cy, cx, cy))
    parts.append('    <circle cx="%d" cy="%d" r="36" fill="none" '
                 'stroke="url(#accentGrad)" stroke-opacity=".55" stroke-width="2" '
                 'stroke-dasharray="90 40" class="spinRev" '
                 'style="transform-origin:%dpx %dpx"/>' % (cx, cy, cx, cy))
    # Hai vòng lan toả chậm quanh lõi, như nhịp thở của thành phố nhỏ.
    for delay, duration in ((0, 5.2), (-2.6, 5.2)):
        parts.append('    <circle cx="%d" cy="%d" r="26" fill="none" '
                     'stroke="%s" stroke-width="1.4" opacity="0">'
                     '<animate attributeName="r" values="26;86" dur="%.1fs" '
                     'begin="%.1fs" repeatCount="indefinite"/>'
                     '<animate attributeName="opacity" values=".55;0" dur="%.1fs" '
                     'begin="%.1fs" repeatCount="indefinite"/>'
                     '</circle>' % (cx, cy, pal.accent3, duration, delay, duration, delay))
    parts.append('    <circle cx="%d" cy="%d" r="25" fill="url(#coreGrad)" '
                 'filter="url(#glow)"/>' % (cx, cy))
    parts.append('    <text x="%d" y="%d" text-anchor="middle" class="fSans" '
                 'style="font:800 18px %s;fill:%s;letter-spacing:.5px">SP</text>'
                 % (cx, cy + 6, pal.font, pal.bg_top))
    for ang, radius, color, speed in ((0, 56, pal.accent3, 15),
                                      (128, 72, pal.accent, 22),
                                      (238, 88, pal.accent3, 29)):
        parts.append('    <g transform="rotate(%d %d %d)"><g class="spinSlow" '
                     'style="transform-origin:%dpx %dpx;animation-duration:%ds">'
                     '<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s" '
                     'filter="url(#glow)"/></g></g>'
                     % (ang, cx, cy, cx, cy, speed, cx + radius, cy, color))
    parts.append("  </g>")
    return parts


def _typing(pal, t):
    """Ba câu tự gõ, mỗi câu có khung clip riêng."""
    lines = [t("hero.type1"), t("hero.type2"), t("hero.type3")]
    parts = ['  <g>']
    # Dấu nhắc vẽ bằng path: không phụ thuộc font, không bao giờ thành ô vuông
    parts.append('    <path d="M252 207 L259 214.5 L252 222" fill="none" '
                 'stroke="%s" stroke-width="2.4" stroke-linecap="round" '
                 'stroke-linejoin="round"/>' % pal.dim)
    slot = 8.4
    total = slot * len(lines)
    for i, line in enumerate(lines):
        cid = "typeClip%d" % i
        width = 12 + len(line) * 7.6
        base = width if i == 0 else 0
        parts.append('    <clipPath id="%s"><rect x="272" y="196" width="%.0f" '
                     'height="28">' % (cid, base))
        parts.append('      <animate attributeName="width" '
                     'values="0;0;%.0f;%.0f;0;0" '
                     'keyTimes="0;%.3f;%.3f;%.3f;%.3f;1" dur="%.1fs" '
                     'begin="%.1fs" repeatCount="indefinite"/>'
                     % (width, width,
                        (slot * i) / total,
                        (slot * i + 1.5) / total,
                        (slot * i + 5.4) / total,
                        (slot * i + 5.9) / total,
                        total, slot * i))
        parts.append('    </rect></clipPath>')
        parts.append('    <text x="282" y="217" class="heroType" '
                     'clip-path="url(#%s)">%s</text>' % (cid, esc(line)))
    parts.append('    <rect x="272" y="202" width="2" height="18" rx="1" '
                 'fill="%s" class="blink"/>' % pal.accent)
    parts.append("  </g>")
    return parts


def _pill(x, width, text, pal, solid=True):
    if solid:
        return ('  <g class="fadeUp" style="animation-delay:.22s">'
                '<rect x="%d" y="150" width="%d" height="24" rx="12" '
                'fill="%s" stroke="%s" stroke-opacity=".8"/>'
                '<text x="%s" y="166" text-anchor="middle" class="heroPill">%s</text>'
                '</g>' % (x, width, pal.panel, pal.stroke, num(x + width / 2.0), text))
    return ('  <g class="fadeUp" style="animation-delay:.3s">'
            '<rect x="%d" y="150" width="%d" height="24" rx="12" fill="none" '
            'stroke="%s" stroke-opacity=".55" stroke-dasharray="4 4"/>'
            '<text x="%s" y="166" text-anchor="middle" class="heroPill">%s</text>'
            '</g>' % (x, width, pal.accent2, num(x + width / 2.0), text))


def _chips(pal):
    """Ba chip công nghệ trôi nhẹ bên phải, lấp khoảng trống cho cân."""
    items = [("PY", 0.0, 92, 886), ("JS", 1.3, 140, 898), ("TS", 2.6, 188, 880)]
    parts = []
    for label, delay, y, x in items:
        parts.append(
            '  <g class="floatY" style="animation-delay:-%ss">'
            '<rect x="%d" y="%d" width="52" height="26" rx="9" fill="%s" '
            'fill-opacity=".7" stroke="%s" stroke-opacity=".5"/>'
            '<text x="%d" y="%d" text-anchor="middle" class="fMono" '
            'style="font:700 11px %s;fill:%s;letter-spacing:.6px">%s</text>'
            '</g>' % (delay, x, y, pal.panel, pal.stroke, x + 26, y + 17,
                      pal.mono, pal.accent3, label))
    return parts


def hero(pal, dt, t, width=1000, height=280):
    """Trả về toàn bộ nội dung hero.svg."""
    stamp = dt.strftime("%d/%m · %H:%M")
    parts = open_svg(pal, width, height,
                     "Standardize Paradigm - " + t("hero.sub"),
                     desc=t("desc.hero"), halo=False, radius=22)

    parts.append('  <g clip-path="url(#cardBody)">')
    parts += _grid(width, height, pal)
    parts.append('    <ellipse cx="150" cy="40" rx="250" ry="150" fill="url(#halo)" '
                 'filter="url(#soft)" class="driftA"/>')
    parts.append('    <ellipse cx="860" cy="250" rx="290" ry="150" '
                 'fill="url(#halo2)" filter="url(#soft)" class="driftB"/>')
    parts.append('    <ellipse cx="600" cy="300" rx="320" ry="130" fill="url(#halo)" '
                 'filter="url(#soft)" opacity=".55" class="driftC"/>')
    parts.append('    <rect x="0" y="0" width="%d" height="1.5" '
                 'fill="url(#accentGrad)" opacity="0" class="scan"/>' % width)
    # Vệt thứ hai mảnh hơn, chậm hơn và lệch pha: hai làn sáng không bao
    # giờ trùng nhau nên nền luôn có chuyển động, không bị "nhịp đều" nhàm.
    parts.append('    <rect x="0" y="0" width="%d" height="1" fill="%s" '
                 'opacity="0" class="scan" style="animation-duration:12.5s;'
                 'animation-delay:-4.2s"/>' % (width, pal.accent3))
    parts.append('  </g>')

    parts += _stars(width, height, pal)
    parts += _particles(pal, width, height)
    parts += _orbit(pal)
    parts += _chips(pal)

    # tiêu đề + vệt sáng chạy qua chữ
    parts.append('  <g class="fadeUp" style="animation-delay:.05s">')
    parts.append('    <text x="252" y="96" class="heroTitle" fill="url(#titleGrad)">'
                 'Standardize Paradigm</text>')
    # Vệt sáng quét qua chữ. Dùng SMIL (không dùng CSS) để lúc t=0 - khi
    # một số trình xem đứng yên ở khung đầu - hình chữ vẫn sạch, không bị
    # một mảng trắng đè lên nửa tiêu đề.
    parts.append('    <clipPath id="sheenClip">')
    parts.append('      <rect x="-460" y="52" width="150" height="60">')
    parts.append('        <animate attributeName="x" dur="7.5s" begin="1.2s" '
                 'repeatCount="indefinite" calcMode="spline" '
                 'values="-460;1012;1012" keyTimes="0;0.55;1" '
                 'keySplines="0.4 0 0.6 1;0 0 1 1"/>')
    parts.append('      </rect>')
    parts.append('    </clipPath>')
    parts.append('    <text x="252" y="96" class="heroTitle" fill="#FFFFFF" '
                 'opacity=".28" clip-path="url(#sheenClip)">Standardize Paradigm</text>')
    parts.append('    <rect x="253" y="106" width="74" height="3" rx="1.5" '
                 'fill="url(#accentGrad)" class="pulse"/>')
    parts.append('    <text x="252" y="134" class="heroSub">%s</text>' % esc(t("hero.sub")))
    parts.append("  </g>")

    # 4 pill thông tin + pill trạng thái
    pills = [(t("hero.pill1"), 66), (t("hero.pill2"), 58), (t("hero.pill3"), 68)]
    px = 252
    for label, pill_w in pills:
        parts.append(_pill(px, pill_w, esc(label), pal))
        px += pill_w + 9
    parts.append(_pill(px, 150, esc(t("hero.pill4")), pal, solid=False))

    # trạng thái "đang code"
    sx = px + 162
    parts.append('  <g class="fadeUp" style="animation-delay:.36s">'
                 '<rect x="%d" y="150" width="118" height="24" rx="12" fill="%s" '
                 'fill-opacity=".55" stroke="%s" stroke-opacity=".7"/>'
                 '<circle cx="%d" cy="162" r="3.4" fill="%s" class="pulse"/>'
                 '<text x="%d" y="166" class="heroPill" style="fill:%s">%s</text>'
                 '</g>' % (sx, pal.panel, pal.accent, sx + 14, pal.accent3,
                           sx + 24, pal.text, esc(t("hero.status"))))

    parts += _typing(pal, t)

    parts.append('  <text x="%d" y="256" text-anchor="end" class="heroHint">%s</text>'
                 % (width - 34, esc(t("hero.hint"))))
    parts.append('  <text x="252" y="256" class="heroHint">~/standardizeparadigm · '
                 '%s</text>' % esc(stamp))
    parts.append('  <rect x="30" y="%d" width="%d" height="3" rx="1.5" '
                 'fill="url(#accentGrad)" opacity=".55" class="pulseSlow"/>'
                 % (height - 10, width - 60))
    parts.append("</svg>")
    return "\n".join(parts)
