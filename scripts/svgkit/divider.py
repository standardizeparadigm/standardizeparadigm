#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
divider.py — Đường kẻ động và ảnh chân trang.

Thay cho các file GIF nặng từ user-images.githubusercontent.com: nhẹ hơn
nhiều, không phụ thuộc server ngoài, và chạy hoạt ảnh mượt.
"""

from .primitives import esc, open_svg, smil_reduce_style


def divider(pal, width=1000, height=26):
    """Đường kẻ mảnh, có vệt sáng chạy ngang và viên kim cương ở giữa."""
    mid = width / 2.0
    parts = [
        # Đường kẻ thuần trang trí: role="presentation" để trình đọc màn
        # hình bỏ qua, nhưng vẫn phải aria-hidden — một số trình đọc không
        # hiểu role của SVG và sẽ đọc "graphic" vô nghĩa.
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        'xmlns="http://www.w3.org/2000/svg" role="presentation" '
        'aria-hidden="true">',
        '  <defs>',
        '    <linearGradient id="ln" x1="0" y1="0" x2="1" y2="0">',
        f'      <stop offset="0%" stop-color="{pal.accent}" stop-opacity="0"/>',
        f'      <stop offset="20%" stop-color="{pal.accent}" stop-opacity=".55"/>',
        f'      <stop offset="50%" stop-color="{pal.accent3}" stop-opacity=".95"/>',
        f'      <stop offset="80%" stop-color="{pal.accent}" stop-opacity=".55"/>',
        f'      <stop offset="100%" stop-color="{pal.accent}" stop-opacity="0"/>',
        '    </linearGradient>',
        '    <linearGradient id="sparkLine" x1="0" y1="0" x2="1" y2="0">',
        '      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>',
        '      <stop offset="50%" stop-color="#FFFFFF" stop-opacity=".95"/>',
        '      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>',
        '    </linearGradient>',
        '    <filter id="dGlow"><feGaussianBlur stdDeviation="2.4"/></filter>',
        '  </defs>',
        smil_reduce_style(),
        f'  <rect x="0" y="12" width="{width}" height="1.6" fill="url(#ln)"/>',
        '  <rect class="smilOnly" x="-120" y="11.4" width="120" height="2.8" '
        'fill="url(#sparkLine)" filter="url(#dGlow)">',
        f'    <animate attributeName="x" values="-120;{width + 20}" dur="7s" '
        'repeatCount="indefinite"/>',
        '  </rect>',
        '  <rect class="smilOnly" x="-120" y="12.2" width="60" height="1.6" '
        'fill="url(#sparkLine)" opacity=".45" filter="url(#dGlow)">',
        f'    <animate attributeName="x" values="{width + 20};-120" dur="13s" '
        'repeatCount="indefinite"/>',
        '  </rect>',
        f'  <g class="smilOnly" transform="translate({mid:.1f} 13)">',
        '    <rect x="-4.5" y="-4.5" width="9" height="9" rx="2" '
        f'transform="rotate(45)" fill="{pal.accent3}" opacity=".9">',
        '      <animateTransform attributeName="transform" type="rotate" '
        'values="45;225;45" dur="12s" repeatCount="indefinite"/>',
        '    </rect>',
        f'    <circle r="13" fill="none" stroke="{pal.accent}" stroke-opacity=".25">',
        '      <animate attributeName="r" values="8;16;8" dur="4.5s" '
        'repeatCount="indefinite"/>',
        '      <animate attributeName="stroke-opacity" values=".3;0;.3" '
        'dur="4.5s" repeatCount="indefinite"/>',
        '    </circle>',
        '  </g>',
        # Hạt sáng nhỏ chạy dọc theo đường kẻ, ngược chiều với vệt sáng chính:
        # hai chuyển động cắt nhau nên mắt luôn thấy đường kẻ "đang sống".
        f'  <circle class="smilOnly" cy="13" r="2.6" fill="{pal.accent3}" '
        'filter="url(#dGlow)">',
        f'    <animate attributeName="cx" values="-12;{width + 12}" dur="9s" '
        'repeatCount="indefinite"/>',
        '    <animate attributeName="opacity" values="0;1;1;0" dur="9s" '
        'repeatCount="indefinite"/>',
        '  </circle>',
        f'  <circle class="smilOnly" cx="150" cy="13" r="2" fill="{pal.accent}" '
        'opacity=".55">',
        '    <animate attributeName="opacity" values=".15;.75;.15" dur="5.5s" '
        'repeatCount="indefinite"/>',
        '  </circle>',
        f'  <circle class="smilOnly" cx="850" cy="13" r="2" fill="{pal.accent}" '
        'opacity=".55">',
        '    <animate attributeName="opacity" values=".75;.15;.75" dur="5.5s" '
        'repeatCount="indefinite"/>',
        '  </circle>',
        '</svg>',
    ]
    return "\n".join(parts)


def _wave(y0, amplitude, period, width, phase=0):
    """Sóng tuần hoàn để cuộn ngang liền mạch."""
    half = period / 2.0
    d = ["M0 %.1f" % y0]
    x = 0.0
    up = True
    while x < width:
        control_x = x + half / 2.0
        end_x = x + half
        control_y = y0 - amplitude if up else y0 + amplitude
        d.append("Q%.1f %.1f %.1f %.1f" % (control_x, control_y, end_x, y0))
        x = end_x
        up = not up
    return " ".join(d)


def footer(pal, t, width=1000, height=200):
    """Ảnh chân trang: sóng chuyển động + lời cảm ơn."""
    period = 500
    fill = ('%s L%d %d L0 %d Z' % (_wave(152, 14, period, width + period * 2),
                                    width + period * 2, height, height))
    fill2 = ('%s L%d %d L0 %d Z' % (_wave(170, 10, period, width + period * 2),
                                     width + period * 2, height, height))
    parts = open_svg(pal, width, height, t("footer.title"),
                     desc=t("desc.footer"), halo=False, radius=22)
    parts.append(smil_reduce_style())
    parts.append('  <g clip-path="url(#cardBody)">')
    parts.append('    <ellipse cx="140" cy="-20" rx="260" ry="130" '
                 'fill="url(#halo)" filter="url(#soft)"/>')
    parts.append('    <ellipse cx="880" cy="40" rx="240" ry="130" '
                 'fill="url(#halo2)" filter="url(#soft)"/>')
    parts.append('    <g transform="translate(-%d 0)"><g class="wave">'
                 '<path d="%s" fill="url(#barGrad)" opacity=".16"/></g></g>'
                 % (period, fill))
    parts.append('    <g transform="translate(-%d 0)"><g class="wave2">'
                 '<path d="%s" fill="url(#accentGrad)" opacity=".22"/></g></g>'
                 % (period, fill2))
    parts.append('    <ellipse cx="500" cy="58" rx="230" ry="70" '
                 'fill="url(#halo)" opacity=".5" class="pulseSlow"/>')
    for index, (bx, delay, size) in enumerate(
            ((120, 0.0, 3.2), (250, -1.6, 2.2), (410, -3.1, 2.8),
             (610, -0.8, 2.0), (760, -2.4, 3.6), (880, -4.2, 2.4))):
        parts.append('    <circle cx="%d" cy="%d" r="%.1f" fill="%s" opacity="0" '
                     'class="bubble smilOnly">'
                     '<animate attributeName="cy" values="%d;%d" dur="11s" '
                     'begin="%.1fs" repeatCount="indefinite"/>'
                     '<animate attributeName="opacity" values="0;.55;0" dur="11s" '
                     'begin="%.1fs" repeatCount="indefinite"/>'
                     '</circle>'
                     % (bx, 186 - index * 3, size, pal.accent3,
                        190 - index * 3, 96 - index * 4, delay, delay))
    # Vài ngôi sao nhấp nháy ở nửa trên: chân trang không chỉ có sóng.
    for sx, sy, radius, delay in ((64, 34, 1.6, 0.0), (298, 22, 1.2, -1.1),
                                  (512, 34, 1.8, -2.3), (702, 20, 1.3, -3.4),
                                  (934, 42, 1.5, -0.7)):
        parts.append('    <circle cx="%d" cy="%d" r="%.1f" fill="%s" '
                     'class="twinkle" style="animation-delay:%.1fs"/>'
                     % (sx, sy, radius, pal.accent3, delay))
    parts.append('  </g>')
    parts += [
        '  <g class="fadeUp">',
        '    <text x="500" y="54" text-anchor="middle" class="footTitle" '
        'fill="url(#titleGrad)">%s</text>' % esc(t("footer.title")),
        '    <text x="500" y="78" text-anchor="middle" class="footSub">%s</text>'
        % esc(t("footer.sub")),
        '    <rect x="452" y="92" width="96" height="3" rx="1.5" '
        'fill="url(#accentGrad)" class="pulse"/>',
        '    <text x="500" y="118" text-anchor="middle" class="heroHint">%s</text>'
        % esc(t("footer.made")),
        '  </g>',
        '</svg>',
    ]
    return "\n".join(parts)
