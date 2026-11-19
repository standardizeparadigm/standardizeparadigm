#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
divider.py — Đường kẻ động và ảnh chân trang.

Thay cho các file GIF nặng từ user-images.githubusercontent.com: nhẹ hơn
nhiều, không phụ thuộc server ngoài, và chạy hoạt ảnh mượt.
"""

from .primitives import esc, open_svg


def divider(pal, width=1000, height=26):
    """Đường kẻ mảnh, có vệt sáng chạy ngang và viên kim cương ở giữa."""
    mid = width / 2.0
    parts = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        'xmlns="http://www.w3.org/2000/svg" role="presentation">',
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
        f'  <rect x="0" y="12" width="{width}" height="1.6" fill="url(#ln)"/>',
        '  <rect x="-120" y="11.4" width="120" height="2.8" '
        'fill="url(#sparkLine)" filter="url(#dGlow)">',
        f'    <animate attributeName="x" values="-120;{width + 20}" dur="7s" '
        'repeatCount="indefinite"/>',
        '  </rect>',
        '  <rect x="-120" y="12.2" width="60" height="1.6" '
        'fill="url(#sparkLine)" opacity=".45" filter="url(#dGlow)">',
        f'    <animate attributeName="x" values="{width + 20};-120" dur="13s" '
        'repeatCount="indefinite"/>',
        '  </rect>',
        f'  <g transform="translate({mid:.1f} 13)">',
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
        f'  <circle cx="150" cy="13" r="2" fill="{pal.accent}" opacity=".55"/>',
        f'  <circle cx="850" cy="13" r="2" fill="{pal.accent}" opacity=".55"/>',
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
