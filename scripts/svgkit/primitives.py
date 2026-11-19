#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
primitives.py — Những viên gạch dùng chung: chuỗi an toàn, icon, CSS, defs.

Nguyên tắc: CSS và defs đều sinh từ Palette, nên đổi theme là đổi màu
toàn bộ mà không phải sờ vào từng thẻ.
"""

# --------------------------------------------------------------- chuỗi
def esc(text):
    """Làm sạch chuỗi trước khi nhét vào XML."""
    text = str(text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text.replace('"', "&quot;")


def human(number):
    """1284 -> 1.3k, 2400000 -> 2.4M. Không phải số thì trả '-'."""
    try:
        number = int(number)
    except (TypeError, ValueError):
        return "-"
    if number >= 1000000:
        return str(round(number / 1000000.0, 1)).replace(".0", "") + "M"
    if number >= 1000:
        return str(round(number / 1000.0, 1)).replace(".0", "") + "k"
    return str(number)


def num(value):
    """Số thực gọn gàng cho thuộc tính SVG."""
    return ("%.1f" % value).rstrip("0").rstrip(".")


# --------------------------------------------------------------- icon
# Toàn bộ icon là nét vẽ tay bằng path, không dùng emoji -> hiển thị
# giống nhau trên Windows, macOS, Linux.
ICONS = {
    "star": '<path d="M12 2.9l2.9 5.9 6.5.95-4.72 4.6 1.12 6.49L12 17.8l-5.8 3.04 '
            '1.12-6.49L2.6 9.75l6.5-.95z"/>',
    "fork": '<circle cx="6" cy="5" r="2.4"/><circle cx="6" cy="19" r="2.4"/>'
            '<circle cx="18" cy="7" r="2.4"/><path d="M6 7.4v9.2"/>'
            '<path d="M18 9.4c0 4.2-4 4.6-8 5.4"/>',
    "repo": '<rect x="4.4" y="4.4" width="15.2" height="15.2" rx="3"/>'
            '<path d="M8.4 9h7.2"/><path d="M8.4 12.6h5"/>',
    "users": '<circle cx="9.2" cy="8.4" r="3.1"/><circle cx="17.2" cy="9.8" r="2.3"/>'
             '<path d="M3.4 19.2c.5-3.3 2.8-5.2 5.8-5.2s5.3 1.9 5.8 5.2"/>'
             '<path d="M15.6 14.4c2.2.2 3.9 1.9 4.4 4.4"/>',
    "follow": '<path d="M2.6 12S6.1 6.4 12 6.4 21.4 12 21.4 12 17.9 17.6 12 17.6 '
              '2.6 12 2.6 12z"/><circle cx="12" cy="12" r="2.7"/>',
    "commit": '<circle cx="12" cy="12" r="3.5"/><path d="M2.4 12h6.1"/>'
              '<path d="M15.5 12h6.1"/>',
    "clock": '<circle cx="12" cy="12" r="8.6"/><path d="M12 7.3V12l3.7 2.2"/>',
    "code": '<path d="M9 7.4L3.7 12 9 16.6"/><path d="M15 7.4L20.3 12 15 16.6"/>',
    "spark": '<path d="M12 3.2v4.4"/><path d="M12 16.4v4.4"/><path d="M3.2 12h4.4"/>'
             '<path d="M16.4 12h4.4"/><circle cx="12" cy="12" r="2.2"/>',
    "flame": '<path d="M12 3.2c2.6 3.1 1.1 4.9 2.6 6.6 1-.6 1.4-1.7 1.3-3 '
             '2 2.1 3.1 4.2 3.1 6.5A7 7 0 015 13.3c0-2.6 1.5-4.7 3.4-6.4 '
             '.2 1.4.7 2.3 1.6 2.8 1-2-1.5-4.2 2-6.5z"/>',
    "trophy": '<path d="M8 4.5h8v4.2a4 4 0 01-8 0z"/><path d="M8 5.6H5.3v1.5A3.2 '
              '3.2 0 008.5 10.3"/><path d="M16 5.6h2.7v1.5a3.2 3.2 0 01-3.2 3.2"/>'
              '<path d="M12 12.7v3.6"/><path d="M8.4 19.6h7.2"/>'
              '<path d="M10 16.3h4l.6 3.3H9.4z"/>',
    "globe": '<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/>'
             '<path d="M12 3.4c2.4 2.3 3.7 5.2 3.7 8.6S14.4 18.3 12 20.6"/>'
             '<path d="M12 3.4C9.6 5.7 8.3 8.6 8.3 12s1.3 6.3 3.7 8.6"/>',
}


def icon(name, x, y, color, scale=0.78, width=1.9):
    """Chèn một icon tại (x, y) với kích thước 24x24 nhân `scale`.

    Tên lạ rơi về `spark` — thà hiện một ngôi sao nhỏ còn hơn để trống
    một ô trong thẻ.
    """
    body = ICONS.get(name, ICONS["spark"])
    return ('<g transform="translate(%s %s) scale(%s)" fill="none" stroke="%s" '
            'stroke-width="%s" stroke-linecap="round" stroke-linejoin="round">'
            '%s</g>' % (num(x), num(y), num(scale), color, num(width), body))


# --------------------------------------------------------------- CSS
CSS = """
  .fSans { font-family: @FONT@; }
  .fMono { font-family: @MONO@; }
  .cardTitle   { font: 800 14px @FONT@; fill: @TITLE@; letter-spacing: 2.2px; }
  .cardSub     { font: 600 9.5px @MONO@; fill: @DIM@; letter-spacing: .8px; }
  .tileValue   { font: 800 19px @FONT@; fill: @TITLE@; }
  .tileLabel   { font: 600 9.5px @FONT@; fill: @LABEL@; letter-spacing: .7px; }
  .legendName  { font: 700 11.5px @FONT@; fill: @TEXT@; }
  .legendValue { font: 800 11.5px @MONO@; fill: @ACCENT3@; }
  .footNote    { font: 500 9px @FONT@; fill: @DIM@; letter-spacing: .3px; }
  .bigValue    { font: 800 22px @FONT@; fill: @TITLE@; }
  .midLabel    { font: 700 8.5px @FONT@; fill: @LABEL@; letter-spacing: 1.3px; }
  .heroTitle   { font: 800 46px @FONT@; letter-spacing: -1.2px; }
  .heroSub     { font: 600 14.5px @FONT@; fill: @LABEL@; letter-spacing: .2px; }
  .heroPill    { font: 700 10.5px @FONT@; fill: @ACCENT3@; letter-spacing: .5px; }
  .heroType    { font: 600 13px @MONO@; fill: @ACCENT3@; }
  .heroHint    { font: 500 10px @MONO@; fill: @DIM@; letter-spacing: .6px; }
  .clockTime   { font: 800 54px @FONT@; letter-spacing: -1.5px; }
  .clockDate   { font: 600 13px @FONT@; fill: @TEXT@; }
  .clockLabel  { font: 700 9px @FONT@; fill: @DIM@; letter-spacing: 1.6px; }
  .clockBig    { font: 700 11px @FONT@; fill: @TEXT@; }
  .footTitle   { font: 800 24px @FONT@; fill: @TITLE@; letter-spacing: .4px; }
  .footSub     { font: 600 11px @MONO@; fill: @ACCENT3@; letter-spacing: 1px; }

  .pulse      { animation: pulse 2.6s ease-in-out infinite; }
  .pulseSlow  { animation: pulse 4.4s ease-in-out infinite; }
  .blink      { animation: blink 1.05s steps(1, end) infinite; }
  /* Vòng cung quay tại chỗ quanh một chấm nhỏ (dùng cho trạng thái đang chạy) */
  .spinDot    { animation: spin 1.6s linear infinite;
                transform-box: fill-box; transform-origin: center; }
  .spinSlow   { animation: spin 26s linear infinite;
                transform-box: view-box; transform-origin: center; }
  .spinRev    { animation: spinRev 34s linear infinite;
                transform-box: view-box; transform-origin: center; }
  .driftA     { animation: driftA 16s ease-in-out infinite;
                transform-box: view-box; transform-origin: center; }
  .driftB     { animation: driftB 21s ease-in-out infinite;
                transform-box: view-box; transform-origin: center; }
  .driftC     { animation: driftC 26s ease-in-out infinite;
                transform-box: view-box; transform-origin: center; }
  .floatY     { animation: floatY 5.2s ease-in-out infinite; }
  .twinkle    { animation: twinkle 4s ease-in-out infinite; }
  .fadeUp     { animation: fadeUp .72s cubic-bezier(.2,.8,.2,1) both; }
  .growIn     { animation: growIn .8s cubic-bezier(.2,.8,.2,1) both;
                transform-box: view-box; transform-origin: left center; }
  .sheen      { animation: sheen 6.5s ease-in-out infinite; }
  .scan       { animation: scan 7.5s linear infinite; }
  .secHand    { animation: spin 60s linear infinite;
                transform-box: view-box; transform-origin: var(--cx) var(--cy); }
  .minHand    { animation: spin 3600s linear infinite;
                transform-box: view-box; transform-origin: var(--cx) var(--cy); }
  .hourHand   { animation: spin 43200s linear infinite;
                transform-box: view-box; transform-origin: var(--cx) var(--cy); }
  .wave       { animation: wave 14s linear infinite; }
  .wave2      { animation: wave 19s linear infinite reverse; }

  @keyframes pulse     { 0%,100% { opacity: .35 } 50% { opacity: 1 } }
  @keyframes blink     { 0%,49% { opacity: 1 } 50%,100% { opacity: 0 } }
  @keyframes spin      { to { transform: rotate(360deg) } }
  @keyframes spinRev   { to { transform: rotate(-360deg) } }
  @keyframes driftA    { 0%,100% { transform: translate(0,0) } 50% { transform: translate(26px,-14px) } }
  @keyframes driftB    { 0%,100% { transform: translate(0,0) } 50% { transform: translate(-30px,12px) } }
  @keyframes driftC    { 0%,100% { transform: translate(0,0) scale(1) } 50% { transform: translate(14px,10px) scale(1.06) } }
  @keyframes floatY    { 0%,100% { transform: translateY(0) } 50% { transform: translateY(-7px) } }
  @keyframes twinkle   { 0%,100% { opacity: .12 } 50% { opacity: .85 } }
  @keyframes fadeUp    { from { opacity: .001; transform: translateY(9px) } to { opacity: 1; transform: translateY(0) } }
  @keyframes growIn    { from { transform: scaleX(.001) } to { transform: scaleX(1) } }
  @keyframes sheen     { 0% { transform: translateX(-460px) } 55%,100% { transform: translateX(760px) } }
  @keyframes scan      { 0% { transform: translateY(-40px); opacity: 0 } 12% { opacity: .55 }
                         88% { opacity: .55 } 100% { transform: translateY(300px); opacity: 0 } }
  @keyframes wave      { to { transform: translateX(-500px) } }

  /* Ai bật "giảm chuyển động" trong hệ điều hành thì thấy ảnh tĩnh,
     vẫn đẹp và vẫn đủ thông tin — không phải hy sinh nội dung. */
  @media (prefers-reduced-motion: reduce) {
    .pulse, .pulseSlow, .blink, .spinSlow, .spinRev, .driftA, .driftB,
    .driftC, .floatY, .twinkle, .fadeUp, .growIn, .sheen, .scan, .spinDot,
    .secHand, .minHand, .hourHand, .wave, .wave2 { animation: none !important; }
  }
"""


# --------------------------------------------------------------- defs
DEFS = """
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0%" stop-color="@BGTOP@"/>
      <stop offset="100%" stop-color="@BGBOT@"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="@ACCENT@" stop-opacity=".75"/>
      <stop offset="45%" stop-color="@DEEP@" stop-opacity=".35"/>
      <stop offset="100%" stop-color="@ACCENT3@" stop-opacity=".55"/>
    </linearGradient>
    <linearGradient id="titleGrad" x1="0" y1="0" x2="1" y2="0.4">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="42%" stop-color="@ACCENT3@"/>
      <stop offset="100%" stop-color="@ACCENT2@"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="@DEEP@"/>
      <stop offset="55%" stop-color="@ACCENT2@"/>
      <stop offset="100%" stop-color="@ACCENT3@"/>
    </linearGradient>
    <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="@DEEP@"/>
      <stop offset="60%" stop-color="@ACCENT2@"/>
      <stop offset="100%" stop-color="@ACCENT@"/>
    </linearGradient>
    <linearGradient id="barGradV" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0%" stop-color="@DEEP@" stop-opacity=".85"/>
      <stop offset="100%" stop-color="@ACCENT3@"/>
    </linearGradient>
    <linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity=".16"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="sheenGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity=".22"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="fadeMaskGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#000000"/>
    </linearGradient>
    <radialGradient id="halo" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="@ACCENT@" stop-opacity=".30"/>
      <stop offset="100%" stop-color="@ACCENT@" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="halo2" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="@ACCENT3@" stop-opacity=".22"/>
      <stop offset="100%" stop-color="@ACCENT3@" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="coreGrad" cx="35%" cy="30%" r="80%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="55%" stop-color="@ACCENT@"/>
      <stop offset="100%" stop-color="@DEEP@"/>
    </radialGradient>
    <filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="34"/>
    </filter>
    <filter id="glow" x="-70%" y="-70%" width="240%" height="240%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glowSoft" x="-70%" y="-70%" width="240%" height="240%">
      <feGaussianBlur stdDeviation="8" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
"""


def _fill(template, pal):
    tokens = pal.as_tokens()
    out = template
    for key, value in tokens.items():
        out = out.replace(key, value)
    return out


def css_block(pal):
    """Khối <style> theo palette."""
    return "  <style>\n%s\n  </style>" % _fill(CSS, pal)


def defs_block(pal):
    """Khối <defs> theo palette."""
    return _fill(DEFS, pal)


def open_svg(pal, width, height, label, desc=None, halo=True, radius=18):
    """Mở thẻ: SVG + CSS + defs + nền + viền gradient.

    Kèm clipPath "cardBody" để mọi lớp trang trí (quầng sáng, sóng, sao)
    không tràn ra ngoài bốn góc bo tròn.

    `label` vào cả `aria-label` lẫn `<title>`; `desc` (nếu có) thành
    `<desc>` — trình đọc màn hình đọc đúng nội dung thay vì "graphic".
    """
    parts = [
        '<svg width="%d" height="%d" viewBox="0 0 %d %d" '
        'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s" '
        'preserveAspectRatio="xMidYMid meet">'
        % (width, height, width, height, esc(label)),
        '  <title>%s</title>' % esc(label),
    ]
    if desc:
        parts.append('  <desc>%s</desc>' % esc(desc))
    parts += [
        css_block(pal),
        defs_block(pal),
        '  <clipPath id="cardBody"><rect x="0" y="0" width="%d" height="%d" '
        'rx="%d"/></clipPath>' % (width, height, radius),
        '  <g clip-path="url(#cardBody)">',
        '    <rect x="0" y="0" width="%d" height="%d" fill="url(#bg)"/>'
        % (width, height),
    ]
    if halo:
        parts.append('    <ellipse cx="%d" cy="0" rx="260" ry="140" '
                     'fill="url(#halo)" opacity=".55"/>' % int(width * 0.18))
        parts.append('    <ellipse cx="%d" cy="%d" rx="240" ry="120" '
                     'fill="url(#halo2)" opacity=".45"/>'
                     % (int(width * 0.92), height))
    parts.append('  </g>')
    parts.append('  <rect x="0.7" y="0.7" width="%.1f" height="%.1f" rx="%.1f" '
                 'fill="none" stroke="url(#edge)" stroke-width="1.3"/>'
                 % (width - 1.4, height - 1.4, radius - 0.7))
    return parts


def sheen(pal, width, height, delay=0.0, opacity=0.5):
    """Vệt sáng chéo chạy qua thẻ."""
    return ('  <g clip-path="url(#clip-%d)">'
            '<rect x="-200" y="-60" width="170" height="%d" fill="url(#sheenGrad)" '
            'class="sheen" opacity="%s" style="animation-delay:%ss"/></g>'
            % (int(width * 10 + height), height + 140, opacity, delay))
