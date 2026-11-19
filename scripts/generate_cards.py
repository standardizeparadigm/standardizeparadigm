#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 generate_cards.py  --  Sinh toan bo hinh SVG cho profile README
=====================================================================
 Vi sao co file nay?
   Cac service nhu github-readme-stats.vercel.app la server CONG CONG
   dung chung cho hang tram nghin nguoi -> het quota API la anh bao loi.
   File nay goi API GitHub bang token rieng cua repo, tu ve SVG, roi
   commit vao repo. Anh nam trong repo -> KHONG BAO GIO bi rate-limit.

 Sinh ra 5 file:
   assets/hero.svg        anh bia dong (khong can du lieu)
   assets/divider.svg     duong ke dong (khong can du lieu)
   assets/stats.svg       the thong ke (can API)
   assets/top-langs.svg   the ngon ngu (can API)
   assets/live-clock.svg  dong ho Viet Nam, cap nhat moi ~5 phut

 Cach dung:
   python3 scripts/generate_cards.py --all          # tat ca
   python3 scripts/generate_cards.py --cards        # chi stats + langs (can API)
   python3 scripts/generate_cards.py --clock        # chi dong ho (khong can API)
   python3 scripts/generate_cards.py --hero         # chi hero + divider
   python3 scripts/generate_cards.py --demo --all   # du lieu mau de thu
   python3 scripts/generate_cards.py --placeholder  # the "dang doi du lieu"

 Nguyen tac on dinh:
   - Chi dung thu vien chuan cua Python (khong pip install -> khong vo)
   - Ghi file kieu "atomic": loi giua chung thi anh cu van nguyen ven
   - API loi -> giu nguyen anh cu, khong ghi de bang the rong
   - Tu thu lai 3 lan khi mang loi / bi gioi han
=====================================================================
"""

import json
import os
import random
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# ------------------------------------------------------------------ config
API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER = (os.environ.get("GH_USER")
        or os.environ.get("USERNAME")
        or os.environ.get("GITHUB_REPOSITORY_OWNER")
        or "")
OUT_DIR = os.environ.get("OUT_DIR", "assets")
DISPLAY_NAME = os.environ.get("DISPLAY_NAME", "")
TZ_VN = timezone(timedelta(hours=7))

# --out DIR  -> ghi anh vao thu muc khac (tien cho viec xem thu)
_argv = sys.argv[1:]
if "--out" in _argv:
    _i = _argv.index("--out")
    if _i + 1 < len(_argv):
        OUT_DIR = _argv[_i + 1]
        del _argv[_i:_i + 2]
        sys.argv = [sys.argv[0]] + _argv

ARGS = set(a for a in sys.argv[1:] if a.startswith("--"))
DEMO = "--demo" in ARGS
PLACEHOLDER = "--placeholder" in ARGS
STRICT = "--strict" in ARGS

for a in sys.argv[1:]:
    if not a.startswith("--"):
        USER = a

BAD_USER = (
    "\n!! KHONG BIET TAO THE CHO AI\n"
    "   Khong co bien GH_USER / USERNAME / GITHUB_REPOSITORY_OWNER.\n"
    "   Trong workflow phai co:  env:  GH_USER: ...owner...\n")

BAD_DATA = (
    "\n!! KHONG LAY DUOC DU LIEU TU API GITHUB\n"
    "   Xem cac dong HTTP o tren de biet ly do. Thuong la:\n"
    "    - HTTP 404: sai ten user (kiem tra bien GH_USER).\n"
    "    - HTTP 401: GITHUB_TOKEN khong duoc truyen vao buoc nay.\n"
    "    - HTTP 403 + rate limit: doi vai phut roi chay lai.\n"
    "    - Loi mang: chay lai workflow.\n"
    "   THE CU DUOC GIU NGUYEN (khong ghi de bang the rong).\n")

# ------------------------------------------------------------------ palette
BG_TOP = "#07111D"
BG_BOT = "#0A1421"
PANEL = "#0B1B2B"
PANEL2 = "#0E2133"
STROKE = "#17334F"
TITLE = "#E8F4FF"
TEXT = "#C6D8EA"
LABEL = "#8CA4BD"
DIM = "#5C7590"
ACCENT = "#38BDF8"
ACCENT2 = "#0EA5E9"
ACCENT3 = "#7DD3FC"
DEEP = "#0369A1"
WHITE = "#FFFFFF"

FONT = "'Segoe UI',Inter,Ubuntu,Helvetica,Arial,sans-serif"
MONO = "'Fira Code',Consolas,'SF Mono',monospace"

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#F1E05A", "TypeScript": "#3178C6",
    "HTML": "#E34C26", "CSS": "#563D7C", "SCSS": "#C6538C",
    "Java": "#B07219", "C": "#555555", "C++": "#F34B7D", "C#": "#178600",
    "Go": "#00ADD8", "Rust": "#DEA584", "Ruby": "#701516", "PHP": "#4F5D95",
    "Kotlin": "#A97BFF", "Swift": "#F05138", "Dart": "#00B4AB",
    "Shell": "#89E051", "Lua": "#000080", "Vue": "#41B883",
    "Jupyter Notebook": "#DA5B0B", "Batchfile": "#C1F12E",
    "PowerShell": "#012456", "Makefile": "#427819", "Dockerfile": "#384D54",
    "Markdown": "#083FA1", "Assembly": "#6E4C13", "Processing": "#0096D8",
    "Scratch": "#4D97FF", "Astro": "#FF5A03", "Svelte": "#FF3E00",
}
RAMP = ["#38BDF8", "#0EA5E9", "#0284C7", "#7DD3FC", "#0369A1",
        "#60A5FA", "#2563EB", "#93C5FD"]


def lang_color(name, i):
    return LANG_COLORS.get(name, RAMP[i % len(RAMP)])


# ------------------------------------------------------------------ helpers
def esc(s):
    s = str(s)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s.replace('"', "&quot;")


def human(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "-"
    if n >= 1000000:
        return str(round(n / 1000000.0, 1)).replace(".0", "") + "M"
    if n >= 1000:
        return str(round(n / 1000.0, 1)).replace(".0", "") + "k"
    return str(n)


def now_vn():
    return datetime.now(TZ_VN)


def stamp(dt):
    """'19/11 · 14:05' - co ca phut -> dung voi yeu cau cap nhat theo phut."""
    return dt.strftime("%d/%m · %H:%M")


WEEKDAY_VI = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm",
              "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


def greeting(hour):
    if 5 <= hour < 11:
        return "Chào buổi sáng"
    if 11 <= hour < 13:
        return "Chào buổi trưa"
    if 13 <= hour < 18:
        return "Chào buổi chiều"
    if 18 <= hour < 23:
        return "Chào buổi tối"
    return "Đang thức khuya"


def api(path, tries=3):
    """GET mot endpoint API GitHub. Tra None neu that bai."""
    url = path if path.startswith("http") else API + path
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "profile-cards-lts")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "replace")[:250]
                body = " ".join(body.split())
            except Exception:
                pass
            if e.code in (403, 429) and attempt < tries - 1:
                sys.stderr.write("  HTTP %s -> thu lai | %s\n"
                                 % (e.code, body))
                time.sleep(5 * (attempt + 1))
                continue
            sys.stderr.write("  !! HTTP %s tren %s\n     %s\n"
                             % (e.code, url, body))
            return None
        except Exception as e:
            if attempt < tries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            sys.stderr.write("Loi mang: %s\n" % e)
            return None
    return None


# ------------------------------------------------------------------ icons
# Icon ve bang duong net (stroke) -> hien thi giong nhau tren moi he dieu
# hanh, khong phu thuoc font emoji.
ICONS = {
    "star": '<path d="M12 2.9l2.9 5.9 6.5.95-4.72 4.6 1.12 6.49L12 17.8l-5.8 3.04 1.12-6.49L2.6 9.75l6.5-.95z"/>',
    "fork": '<circle cx="6" cy="5" r="2.4"/><circle cx="6" cy="19" r="2.4"/><circle cx="18" cy="7" r="2.4"/>'
            '<path d="M6 7.4v9.2"/><path d="M18 9.4c0 4.2-4 4.6-8 5.4"/>',
    "repo": '<rect x="4.4" y="4.4" width="15.2" height="15.2" rx="3"/>'
            '<path d="M8.4 9h7.2"/><path d="M8.4 12.6h5"/>',
    "users": '<circle cx="9.2" cy="8.4" r="3.1"/><circle cx="17.2" cy="9.8" r="2.3"/>'
             '<path d="M3.4 19.2c.5-3.3 2.8-5.2 5.8-5.2s5.3 1.9 5.8 5.2"/>'
             '<path d="M15.6 14.4c2.2.2 3.9 1.9 4.4 4.4"/>',
    "follow": '<path d="M2.6 12S6.1 6.4 12 6.4 21.4 12 21.4 12 17.9 17.6 12 17.6 2.6 12 2.6 12z"/>'
              '<circle cx="12" cy="12" r="2.7"/>',
    "commit": '<circle cx="12" cy="12" r="3.5"/><path d="M2.4 12h6.1"/><path d="M15.5 12h6.1"/>',
    "clock": '<circle cx="12" cy="12" r="8.6"/><path d="M12 7.3V12l3.7 2.2"/>',
    "code": '<path d="M9 7.4L3.7 12 9 16.6"/><path d="M15 7.4L20.3 12 15 16.6"/>',
    "spark": '<path d="M12 3.2v4.4"/><path d="M12 16.4v4.4"/><path d="M3.2 12h4.4"/>'
             '<path d="M16.4 12h4.4"/><circle cx="12" cy="12" r="2.2"/>',
    "trophy": '<path d="M8 4.5h8v4.2a4 4 0 01-8 0z"/><path d="M8 5.6H5.3v1.5A3.2 3.2 0 008.5 10.3"/>'
              '<path d="M16 5.6h2.7v1.5a3.2 3.2 0 01-3.2 3.2"/><path d="M12 12.7v3.6"/>'
              '<path d="M8.4 19.6h7.2"/><path d="M10 16.3h4l.6 3.3H9.4z"/>',
}


def icon(name, x, y, color=ACCENT, scale=0.78, width=1.9):
    body = ICONS.get(name, ICONS["spark"])
    return (
        '<g transform="translate(%.2f %.2f) scale(%.3f)" fill="none" '
        'stroke="%s" stroke-width="%.2f" stroke-linecap="round" '
        'stroke-linejoin="round">%s</g>' % (x, y, scale, color, width, body)
    )


# ------------------------------------------------------------------ style
STYLE = """
  .fSans { font-family: %(font)s; }
  .fMono { font-family: %(mono)s; }
  .cardTitle   { font: 800 14px %(font)s; fill: #E8F4FF; letter-spacing: 2.2px; }
  .cardSub     { font: 600 9.5px %(mono)s; fill: #5C7590; letter-spacing: .8px; }
  .tileValue   { font: 800 19px %(font)s; fill: #F2FAFF; }
  .tileLabel   { font: 600 9.5px %(font)s; fill: #7E97B0; letter-spacing: .7px; }
  .legendName  { font: 700 11.5px %(font)s; fill: #D4E6F5; }
  .legendValue { font: 800 11.5px %(mono)s; fill: #7DD3FC; }
  .footNote    { font: 500 9px %(font)s; fill: #546B84; letter-spacing: .3px; }
  .heroTitle   { font: 800 46px %(font)s; letter-spacing: -1.2px; }
  .heroSub     { font: 600 14.5px %(font)s; fill: #9FC4E2; letter-spacing: .2px; }
  .heroPill    { font: 700 10.5px %(font)s; fill: #A8D6F4; letter-spacing: .5px; }
  .heroType    { font: 600 13px %(mono)s; fill: #7DD3FC; }
  .heroHint    { font: 500 10px %(mono)s; fill: #4E6884; letter-spacing: .6px; }
  .clockTime   { font: 800 54px %(font)s; letter-spacing: -1.5px; }
  .clockDate   { font: 600 13px %(font)s; fill: #A9C6E0; }
  .clockLabel  { font: 700 9px %(font)s; fill: #5C7590; letter-spacing: 1.6px; }
  .clockBig    { font: 700 11px %(font)s; fill: #B7D3EA; }

  .pulse      { animation: pulse 2.6s ease-in-out infinite; }
  .pulseSlow  { animation: pulse 4.4s ease-in-out infinite; }
  .blink      { animation: blink 1.05s steps(1, end) infinite; }
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
  .twinkle    { animation: twinkle 4s ease-in-out infinite; }
  .fadeUp     { animation: fadeUp .72s cubic-bezier(.2,.8,.2,1) both; }
  .growIn     { animation: growIn .8s cubic-bezier(.2,.8,.2,1) both;
                transform-box: view-box; transform-origin: left center; }
  .sheen      { animation: sheen 6.5s ease-in-out infinite; }
  .secHand    { animation: spin 60s linear infinite;
                transform-box: view-box; transform-origin: var(--cx) var(--cy); }
  .minHand    { animation: spin 3600s linear infinite;
                transform-box: view-box; transform-origin: var(--cx) var(--cy); }
  .hourHand   { animation: spin 43200s linear infinite;
                transform-box: view-box; transform-origin: var(--cx) var(--cy); }

  @keyframes pulse     { 0%%,100%% { opacity: .35 } 50%% { opacity: 1 } }
  @keyframes blink     { 0%%,49%% { opacity: 1 } 50%%,100%% { opacity: 0 } }
  @keyframes spin      { to { transform: rotate(360deg) } }
  @keyframes spinRev   { to { transform: rotate(-360deg) } }
  @keyframes driftA    { 0%%,100%% { transform: translate(0,0) } 50%% { transform: translate(26px,-14px) } }
  @keyframes driftB    { 0%%,100%% { transform: translate(0,0) } 50%% { transform: translate(-30px,12px) } }
  @keyframes driftC    { 0%%,100%% { transform: translate(0,0) scale(1) } 50%% { transform: translate(14px,10px) scale(1.06) } }
  @keyframes twinkle   { 0%%,100%% { opacity: .12 } 50%% { opacity: .85 } }
  @keyframes fadeUp    { from { opacity: .001; transform: translateY(9px) } to { opacity: 1; transform: translateY(0) } }
  @keyframes growIn    { from { transform: scaleX(.001) } to { transform: scaleX(1) } }
  @keyframes sheen     { 0%% { transform: translateX(-460px) } 55%%,100%% { transform: translateX(760px) } }
""" % {"font": FONT, "mono": MONO}

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
    <linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity=".16"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="sheenGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity=".22"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
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
      <stop offset="0%" stop-color="#EAF8FF"/>
      <stop offset="55%" stop-color="@ACCENT@"/>
      <stop offset="100%" stop-color="@DEEP@"/>
    </radialGradient>
    <linearGradient id="divGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="@ACCENT@" stop-opacity="0"/>
      <stop offset="18%" stop-color="@ACCENT@" stop-opacity=".55"/>
      <stop offset="50%" stop-color="@ACCENT3@" stop-opacity=".95"/>
      <stop offset="82%" stop-color="@ACCENT@" stop-opacity=".55"/>
      <stop offset="100%" stop-color="@ACCENT@" stop-opacity="0"/>
    </linearGradient>
    <filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="34"/>
    </filter>
    <filter id="soft2" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="12"/>
    </filter>
    <filter id="glow" x="-70%" y="-70%" width="240%" height="240%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
""".replace("@BGTOP@", BG_TOP).replace("@BGBOT@", BG_BOT).replace("@ACCENT3@", ACCENT3).replace("@ACCENT2@", ACCENT2).replace("@ACCENT@", ACCENT).replace("@DEEP@", DEEP)


def open_svg(w, h, label, halo=True):
    p = ['<svg width="%d" height="%d" viewBox="0 0 %d %d" '
         'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s" '
         'preserveAspectRatio="xMidYMid meet">' % (w, h, w, h, esc(label)),
         "  <style>", STYLE, "  </style>", DEFS,
         '  <rect x="0" y="0" width="%d" height="%d" rx="18" fill="url(#bg)"/>'
         % (w, h)]
    if halo:
        p.append('  <ellipse cx="%.0f" cy="0" rx="260" ry="140" '
                 'fill="url(#halo)" opacity=".55"/>' % (w * 0.18))
        p.append('  <ellipse cx="%.0f" cy="%d" rx="240" ry="120" '
                 'fill="url(#halo2)" opacity=".45"/>' % (w * 0.92, h))
    p.append('  <rect x="0.7" y="0.7" width="%.1f" height="%.1f" rx="17.3" '
             'fill="none" stroke="url(#edge)" stroke-width="1.3"/>'
             % (w - 1.4, h - 1.4))
    return p


# ------------------------------------------------------------------ hero
def hero(dt):
    w, h = 1000, 280
    rnd = random.Random(20260820)
    p = ['<svg width="%d" height="%d" viewBox="0 0 %d %d" '
         'xmlns="http://www.w3.org/2000/svg" role="img" '
         'aria-label="Standardize Paradigm - hoc sinh lop 7, lap trinh vien tu hoc">'
         % (w, h, w, h),
         "  <style>", STYLE, "  </style>", DEFS,
         '  <rect x="0" y="0" width="%d" height="%d" rx="22" fill="url(#bg)"/>' % (w, h)]

    # luoi mo + 3 quang sang nen
    p.append('  <g opacity=".5">')
    for x in range(0, w + 1, 40):
        p.append('    <path d="M%d 0V%d" stroke="#7DD3FC" stroke-opacity=".05" '
                 'stroke-width="1"/>' % (x, h))
    for y in range(0, h + 1, 40):
        p.append('    <path d="M0 %dV%d" stroke="#7DD3FC" stroke-opacity=".05" '
                 'stroke-width="1"/>' % (y, w))
    p.append('  </g>')
    p.append('  <ellipse cx="150" cy="40" rx="250" ry="150" fill="url(#halo)" '
             'filter="url(#soft)" class="driftA"/>')
    p.append('  <ellipse cx="860" cy="250" rx="290" ry="150" fill="url(#halo2)" '
             'filter="url(#soft)" class="driftB"/>')
    p.append('  <ellipse cx="600" cy="300" rx="320" ry="130" fill="url(#halo)" '
             'filter="url(#soft)" opacity=".55" class="driftC"/>')

    # sao lap lanh
    for i in range(26):
        sx = rnd.uniform(20, w - 20)
        sy = rnd.uniform(14, h - 30)
        if 250 < sx < 820 and 60 < sy < 210:
            continue  # khong de sao de len chu
        r = rnd.uniform(0.7, 1.7)
        col = rnd.choice([ACCENT3, WHITE, ACCENT])
        delay = rnd.uniform(0, 4)
        p.append('  <circle cx="%.0f" cy="%.0f" r="%.1f" fill="%s" '
                 'class="twinkle" style="animation-delay:-%.1fs"/>'
                 % (sx, sy, r, col, delay))

    # bieu tuong orbit ben trai
    cx, cy = 148, 140
    p.append('  <g>')
    p.append('    <circle cx="%d" cy="%d" r="86" fill="url(#halo)" opacity=".9"/>' % (cx, cy))
    p.append('    <circle cx="%d" cy="%d" r="72" fill="none" stroke="%s" '
             'stroke-opacity=".35" stroke-width="1"/>' % (cx, cy, STROKE))
    p.append('    <circle cx="%d" cy="%d" r="55" fill="none" stroke="url(#accentGrad)" '
             'stroke-width="1.4" stroke-dasharray="3 7" '
             'class="spinSlow" style="transform-origin:%dpx %dpx"/>' % (cx, cy, cx, cy))
    p.append('    <circle cx="%d" cy="%d" r="36" fill="none" stroke="url(#accentGrad)" '
             'stroke-opacity=".55" stroke-width="2" stroke-dasharray="90 40" '
             'class="spinRev" style="transform-origin:%dpx %dpx"/>' % (cx, cy, cx, cy))
    p.append('    <circle cx="%d" cy="%d" r="25" fill="url(#coreGrad)" filter="url(#glow)"/>'
             % (cx, cy))
    p.append('    <text x="%d" y="%d" text-anchor="middle" class="fSans" '
             'style="font:800 18px %s;fill:#04121E;letter-spacing:.5px">SP</text>'
             % (cx, cy + 6, FONT))
    for ang, r, col, spd in ((0, 56, ACCENT3, 15), (128, 72, ACCENT, 22),
                             (238, 88, ACCENT3, 29)):
        p.append('    <g transform="rotate(%d %d %d)"><g class="spinSlow" '
                 'style="transform-origin:%dpx %dpx;animation-duration:%ds">'
                 '<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s" '
                 'filter="url(#glow)"/></g></g>'
                 % (ang, cx, cy, cx, cy, spd, cx + r, cy, col))
    p.append('  </g>')

    # tieu de + hieu ung sang chay qua chu
    p.append('  <g class="fadeUp" style="animation-delay:.05s">')
    p.append('    <text x="252" y="96" class="heroTitle" fill="url(#titleGrad)">'
             'Standardize Paradigm</text>')
    p.append('    <clipPath id="sheenClip"><rect x="252" y="52" width="360" '
             'height="60" class="sheen" style="animation-duration:7.5s"/></clipPath>')
    p.append('    <text x="252" y="96" class="heroTitle" fill="#FFFFFF" '
             'opacity=".28" clip-path="url(#sheenClip)">Standardize Paradigm</text>')
    p.append('    <rect x="253" y="106" width="74" height="3" rx="1.5" '
             'fill="url(#accentGrad)" class="pulse"/>')
    p.append('    <text x="252" y="134" class="heroSub">Học sinh lớp 7 '
             '· Lập trình viên tự học · Long Xuyên, An Giang</text>')
    p.append('  </g>')

    # 3 pill thong tin
    pills = [("LỚP 7", 66), ("UTC+7", 58), ("TỰ HỌC", 68)]
    px = 252
    for text_, pw in pills:
        p.append('  <g class="fadeUp" style="animation-delay:.22s">'
                 '<rect x="%d" y="150" width="%d" height="24" rx="12" '
                 'fill="#0A2135" stroke="%s" stroke-opacity=".8"/>'
                 '<text x="%d" y="166" text-anchor="middle" class="heroPill">%s</text>'
                 '</g>' % (px, pw, STROKE, px + pw / 2.0, text_))
        px += pw + 9
    p.append('  <g class="fadeUp" style="animation-delay:.3s">'
             '<rect x="%d" y="150" width="150" height="24" rx="12" fill="none" '
             'stroke="%s" stroke-opacity=".55" stroke-dasharray="4 4"/>'
             '<text x="%d" y="166" text-anchor="middle" class="heroPill" '
             'style="fill:#7DD3FC">LONG XUYÊN</text></g>'
             % (px, ACCENT2, px + 75))

    # dong go chu (typewriter) chay vong 3 cau
    p.append('  <g>')
    p.append('    <text x="252" y="216" class="heroType" style="fill:%s">&#8250;</text>' % DIM)
    lines = [
        "print(\"Hello World\")",
        "học một thứ → mở ra mười thứ",
        "bug hôm nay = bài học ngày mai",
    ]
    slot = 8.4
    for i, line in enumerate(lines):
        cid = "typeClip%d" % i
        width = 12 + len(line) * 7.6
        base_w = width if i == 0 else 0
        p.append('    <clipPath id="%s"><rect x="272" y="196" width="%.0f" height="28">'
                 % (cid, base_w))
        p.append('      <animate attributeName="width" '
                 'values="0;0;%.0f;%.0f;0;0" '
                 'keyTimes="0;%.3f;%.3f;%.3f;%.3f;1" dur="%.1fs" '
                 'begin="%.1fs" repeatCount="indefinite"/>'
                 % (width, width,
                    (slot * i) / (slot * len(lines)),
                    (slot * i + 1.5) / (slot * len(lines)),
                    (slot * i + 5.4) / (slot * len(lines)),
                    (slot * i + 5.9) / (slot * len(lines)),
                    slot * len(lines), slot * i))
        p.append('    </rect></clipPath>')
        p.append('    <text x="282" y="217" class="heroType" clip-path="url(#%s)">'
                 '%s</text>' % (cid, esc(line)))
    p.append('    <rect x="272" y="202" width="2" height="18" rx="1" '
             'fill="%s" class="blink"/>' % ACCENT)
    p.append('  </g>')

    # chan trang
    p.append('  <text x="%d" y="256" text-anchor="end" class="heroHint">'
             'keep learning · keep building · stay curious</text>' % (w - 34))
    p.append('  <text x="252" y="256" class="heroHint">~/standardizeparadigm · '
             '%s</text>' % stamp(dt))
    p.append('  <rect x="30" y="%d" width="%d" height="3" rx="1.5" '
             'fill="url(#accentGrad)" opacity=".55" class="pulseSlow"/>'
             % (h - 10, w - 60))
    p.append('</svg>')
    return "\n".join(p)


# ------------------------------------------------------------------ divider
def divider():
    w, h = 1000, 26
    p = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
         'xmlns="http://www.w3.org/2000/svg" role="presentation">',
         '  <defs>',
         '    <linearGradient id="ln" x1="0" y1="0" x2="1" y2="0">',
         f'      <stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>',
         f'      <stop offset="20%" stop-color="{ACCENT}" stop-opacity=".55"/>',
         f'      <stop offset="50%" stop-color="{ACCENT3}" stop-opacity=".95"/>',
         f'      <stop offset="80%" stop-color="{ACCENT}" stop-opacity=".55"/>',
         f'      <stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/>',
         '    </linearGradient>',
         '    <linearGradient id="sparkLine" x1="0" y1="0" x2="1" y2="0">',
         f'      <stop offset="0" stop-color="{WHITE}" stop-opacity="0"/>',
         f'      <stop offset="50%" stop-color="{WHITE}" stop-opacity=".95"/>',
         f'      <stop offset="100%" stop-color="{WHITE}" stop-opacity="0"/>',
         '    </linearGradient>',
         '    <filter id="dGlow"><feGaussianBlur stdDeviation="2.4"/></filter>',
         '  </defs>',
         f'  <rect x="0" y="12" width="{w}" height="1.6" fill="url(#ln)"/>',
         '  <rect x="-120" y="11.4" width="120" height="2.8" fill="url(#sparkLine)" '
         'filter="url(#dGlow)">',
         f'    <animate attributeName="x" values="-120;{w + 20}" dur="7s" '
         'repeatCount="indefinite"/>',
         '  </rect>',
         '  <g transform="translate(500 13)">',
         f'    <rect x="-4.5" y="-4.5" width="9" height="9" rx="2" '
         f'transform="rotate(45)" fill="{ACCENT3}" opacity=".9">',
         '      <animateTransform attributeName="transform" type="rotate" '
         'values="45;225;45" dur="12s" repeatCount="indefinite"/>',
         '    </rect>',
         f'    <circle r="13" fill="none" stroke="{ACCENT}" stroke-opacity=".25">',
         '      <animate attributeName="r" values="8;16;8" dur="4.5s" '
         'repeatCount="indefinite"/>',
         '      <animate attributeName="stroke-opacity" values=".3;0;.3" '
         'dur="4.5s" repeatCount="indefinite"/>',
         '    </circle>',
         '  </g>',
         f'  <circle cx="150" cy="13" r="2" fill="{ACCENT}" opacity=".55"/>',
         f'  <circle cx="850" cy="13" r="2" fill="{ACCENT}" opacity=".55"/>',
         '</svg>']
    return "\n".join(p)


# ------------------------------------------------------------------ stats card
def card_stats(d, dt):
    w, h = 640, 258
    letter, pct = grade(d)
    p = open_svg(w, h, "github stats card")
    p.append('  <clipPath id="cardClip"><rect x="0" y="0" width="%d" height="%d" '
             'rx="18"/></clipPath>' % (w, h))
    p.append('  <g clip-path="url(#cardClip)">')
    p.append('    <rect x="-200" y="-60" width="170" height="380" '
             'fill="url(#sheenGrad)" class="sheen" opacity=".55"/>')
    p.append('  </g>')

    # header
    p.append('  <g class="fadeUp">')
    p.append('    <rect x="22" y="22" width="4" height="18" rx="2" '
             'fill="url(#accentGrad)"/>')
    p.append('    <text x="36" y="37" class="cardTitle">GITHUB STATS</text>')
    p.append('    <text x="%d" y="36" text-anchor="end" class="cardSub">'
             'CẬP NHẬT %s</text>' % (w - 22, esc(stamp(dt))))
    p.append('  </g>')

    rows = [
        ("star", "STARS", d["stars"]),
        ("fork", "FORKS", d["forks"]),
        ("repo", "REPOS", d["repos"]),
        ("users", "FOLLOWERS", d["followers"]),
        ("follow", "FOLLOWING", d["following"]),
        ("commit", "COMMITS", d["commits"]),
    ]
    cols = [22, 216]
    row_y = [62, 120, 178]
    for i, (ic, label, val) in enumerate(rows):
        x = cols[i % 2]
        y = row_y[i // 2]
        delay = 0.08 + 0.07 * i
        p.append('  <g class="fadeUp" style="animation-delay:%.2fs">' % delay)
        p.append('    <rect x="%d" y="%d" width="180" height="50" rx="12" '
                 'fill="%s" stroke="%s" stroke-opacity=".85"/>' % (x, y, PANEL, STROKE))
        p.append('    <rect x="%d" y="%d" width="34" height="34" rx="10" '
                 'fill="%s" fill-opacity=".14" stroke="%s" stroke-opacity=".45"/>'
                 % (x + 8, y + 8, ACCENT, ACCENT))
        p.append(icon(ic, x + 15.5, y + 15.5, ACCENT3, 0.8, 1.7))
        p.append('    <text x="%d" y="%d" class="tileValue">%s</text>'
                 % (x + 52, y + 27, esc(human(val) if val is not None else "-")))
        p.append('    <text x="%d" y="%d" class="tileLabel">%s</text>'
                 % (x + 52, y + 41, label))
        p.append('  </g>')

    # vong rank
    cx, cy, r = 528, 144, 56
    circ = 2 * 3.141592653589793 * r
    off = circ * (1 - pct)
    p.append('  <g class="fadeUp" style="animation-delay:.5s">')
    p.append('    <circle cx="%d" cy="%d" r="%d" fill="url(#halo)" opacity=".85"/>'
             % (cx, cy, r + 26))
    p.append('    <circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
             'stroke-width="1" stroke-dasharray="2 6" stroke-opacity=".8" '
             'class="spinSlow" style="transform-origin:%dpx %dpx;'
             'animation-duration:34s"/>' % (cx, cy, r + 12, ACCENT2, cx, cy))
    p.append('    <circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
             'stroke-width="9" stroke-opacity=".18"/>' % (cx, cy, r, ACCENT))
    p.append('    <circle cx="%d" cy="%d" r="%d" fill="none" stroke="url(#accentGrad)" '
             'stroke-width="9" stroke-linecap="round" transform="rotate(-90 %d %d)" '
             'stroke-dasharray="%.1f" stroke-dashoffset="%.1f">'
             % (cx, cy, r, cx, cy, circ, off))
    p.append('      <animate attributeName="stroke-dashoffset" from="%.1f" '
             'to="%.1f" dur="1.6s" begin=".15s" fill="freeze" '
             'calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>'
             % (circ, off))
    p.append('    </circle>')
    p.append('    <text x="%d" y="%d" text-anchor="middle" class="fSans" '
             'style="font:800 32px %s;fill:#F2FAFF">%s</text>'
             % (cx, cy + 6, FONT, esc(letter)))
    p.append('    <text x="%d" y="%d" text-anchor="middle" class="fSans" '
             'style="font:700 8.5px %s;fill:#7E97B0;letter-spacing:2px">RANK</text>'
             % (cx, cy + 24, FONT))
    p.append('    <text x="%d" y="%d" text-anchor="middle" class="cardSub">'
             '%d%% TIẾN ĐỘ</text>' % (cx, cy + 80, int(pct * 100)))
    p.append('  </g>')

    # footer
    p.append('  <g class="fadeUp" style="animation-delay:.62s">')
    p.append('    <circle cx="26" cy="%d" r="3" fill="%s" class="pulse"/>'
             % (h - 15, ACCENT))
    p.append('    <text x="36" y="%d" class="footNote">Dữ liệu thật từ GitHub API '
             '· ảnh nằm trong repo nên không bao giờ rate-limit</text>' % (h - 12))
    p.append('  </g>')
    p.append('</svg>')
    return "\n".join(p)


# ------------------------------------------------------------------ langs card
def card_langs(d, dt):
    w, h = 640, 258
    items = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:8]
    total = sum(v for _, v in items) or 1
    p = open_svg(w, h, "most used languages card")
    p.append('  <clipPath id="cardClip2"><rect x="0" y="0" width="%d" height="%d" '
             'rx="18"/></clipPath>' % (w, h))

    p.append('  <g class="fadeUp">')
    p.append('    <rect x="22" y="22" width="4" height="18" rx="2" '
             'fill="url(#accentGrad)"/>')
    p.append('    <text x="36" y="37" class="cardTitle">MOST USED LANGUAGES</text>')
    p.append('    <text x="%d" y="36" text-anchor="end" class="cardSub">'
             'THEO BYTE CODE THẬT</text>' % (w - 22))
    p.append('  </g>')

    # thanh xep chong
    bx, by, bw, bh = 22, 54, w - 44, 16
    p.append('  <clipPath id="barClip"><rect x="%d" y="%d" width="%d" height="%d" '
             'rx="8"/></clipPath>' % (bx, by, bw, bh))
    p.append('  <rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="#0A1A28" '
             'stroke="%s" stroke-opacity=".7"/>' % (bx, by, bw, bh, STROKE))
    p.append('  <g clip-path="url(#barClip)">')
    x = float(bx)
    for i, (name, val) in enumerate(items):
        seg = bw * (val / float(total))
        p.append('    <rect x="%.1f" y="%d" width="%.1f" height="%d" fill="%s">'
                 % (x, by, seg + 0.6, bh, lang_color(name, i)))
        p.append('      <animate attributeName="width" from="0" to="%.1f" '
                 'dur="1.1s" begin="%.2fs" fill="freeze" calcMode="spline" '
                 'keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>' % (seg + 0.6, 0.1 + 0.06 * i))
        p.append('    </rect>')
        x += seg
    p.append('    <rect x="%d" y="%d" width="%d" height="%.1f" fill="url(#gloss)"/>'
             % (bx, by, bw, bh / 2.0))
    p.append('    <rect x="-160" y="%d" width="150" height="%d" fill="url(#sheenGrad)" '
             'class="sheen" style="animation-duration:5.5s"/>' % (by - 6, bh + 12))
    p.append('  </g>')

    # chu giai 2 cot x 4 hang
    col_x = [22, 330]
    y0 = 104
    for i, (name, val) in enumerate(items):
        cx = col_x[i % 2]
        y = y0 + (i // 2) * 32
        pct = 100.0 * val / total
        label = name if len(name) <= 14 else name[:13] + "…"
        p.append('  <g class="fadeUp" style="animation-delay:%.2fs">' % (0.18 + 0.06 * i))
        p.append('    <circle cx="%d" cy="%d" r="5" fill="%s"/>'
                 % (cx + 5, y - 4, lang_color(name, i)))
        p.append('    <text x="%d" y="%d" class="legendName">%s</text>'
                 % (cx + 18, y, esc(label)))
        p.append('    <text x="%d" y="%d" text-anchor="end" class="legendValue">'
                 '%.1f%%</text>' % (cx + 262, y, pct))
        p.append('    <rect x="%d" y="%d" width="262" height="3" rx="1.5" '
                 'fill="#132A3D"/>' % (cx, y + 6))
        p.append('    <rect x="%d" y="%d" width="%.1f" height="3" rx="1.5" '
                 'fill="%s" opacity=".95" class="growIn" '
                 'style="animation-delay:%.2fs;transform-origin:%dpx %dpx">'
                 % (cx, y + 6, 262 * pct / 100.0, lang_color(name, i),
                    0.24 + 0.06 * i, cx, y + 7.5))
        p.append('    </rect>')
        p.append('  </g>')

    p.append('  <g class="fadeUp" style="animation-delay:.7s">')
    p.append('    <circle cx="26" cy="%d" r="3" fill="%s" class="pulse"/>'
             % (h - 15, ACCENT))
    p.append('    <text x="36" y="%d" class="footNote">Tính theo số byte code thật '
             'trong các repo công khai · cập nhật %s</text>'
             % (h - 12, esc(stamp(dt))))
    p.append('  </g>')
    p.append('</svg>')
    return "\n".join(p)


# ------------------------------------------------------------------ clock
def card_clock(dt):
    w, h = 640, 258
    hh = dt.hour
    mm = dt.minute
    ss = dt.second + dt.microsecond / 1000000.0
    cx, cy, R = 122, 140, 74

    p = open_svg(w, h, "dong ho Viet Nam cap nhat moi 5 phut")
    p.append('  <clipPath id="cardClip3"><rect x="0" y="0" width="%d" height="%d" '
             'rx="18"/></clipPath>' % (w, h))
    p.append('  <g clip-path="url(#cardClip3)">')
    p.append('    <rect x="-200" y="-60" width="170" height="380" '
             'fill="url(#sheenGrad)" class="sheen" opacity=".45" '
             'style="animation-duration:9s"/>')
    p.append('  </g>')

    p.append('  <g class="fadeUp">')
    p.append('    <rect x="22" y="22" width="4" height="18" rx="2" '
             'fill="url(#accentGrad)"/>')
    p.append('    <text x="36" y="37" class="cardTitle">LIVE CLOCK</text>')
    p.append('    <text x="%d" y="36" text-anchor="end" class="cardSub">'
             'UTC+7 · LÀM MỚI MỖI 5 PHÚT</text>' % (w - 22))
    p.append('  </g>')

    # mat dong ho
    p.append('  <g class="fadeUp" style="animation-delay:.12s">')
    p.append('    <circle cx="%d" cy="%d" r="%d" fill="url(#halo)"/>' % (cx, cy, R + 30))
    p.append('    <circle cx="%d" cy="%d" r="%d" fill="#0A1725" stroke="url(#edge)" '
             'stroke-width="3"/>' % (cx, cy, R))
    p.append('    <circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" '
             'stroke-opacity=".65" stroke-width="1" stroke-dasharray="2 5" '
             'class="spinSlow" style="transform-origin:%dpx %dpx;'
             'animation-duration:40s"/>' % (cx, cy, R + 9, ACCENT, cx, cy))
    # vach gio
    import math
    for i in range(60):
        ang = math.radians(i * 6 - 90)
        major = (i % 5 == 0)
        r1 = R - (13 if major else 6)
        r2 = R - 3
        x1, y1 = cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)
        x2, y2 = cx + r2 * math.cos(ang), cy + r2 * math.sin(ang)
        p.append('    <path d="M%.2f %.2fL%.2f %.2f" stroke="%s" '
                 'stroke-width="%s" stroke-linecap="round" opacity="%s"/>'
                 % (x1, y1, x2, y2,
                    ACCENT3 if major else "#2B4C6B",
                    "2" if major else "1",
                    ".85" if major else ".55"))
    # kim gio (quay cham 12h) + kim phut (1h) + kim giay (60s)
    h_ang = ((hh % 12) + mm / 60.0) * 30.0
    m_ang = (mm + ss / 60.0) * 6.0
    p.append('    <g transform="rotate(%.3f %d %d)">' % (h_ang, cx, cy))
    p.append('      <g class="hourHand" style="--cx:%dpx;--cy:%dpx;'
             'animation-delay:%.3fs">' % (cx, cy, -((hh % 12) * 3600 + mm * 60 + ss)))
    p.append('        <rect x="%d" y="%d" width="6" height="40" rx="3" '
             'fill="#DCEBF7"/>' % (cx - 3, cy - 33))
    p.append('      </g>')
    p.append('    </g>')
    p.append('    <g transform="rotate(%.3f %d %d)">' % (m_ang, cx, cy))
    p.append('      <g class="minHand" style="--cx:%dpx;--cy:%dpx;'
             'animation-delay:%.3fs">' % (cx, cy, -(mm * 60 + ss)))
    p.append('        <rect x="%d" y="%d" width="4" height="56" rx="2" '
             'fill="#9FD2EF"/>' % (cx - 2, cy - 47))
    p.append('      </g>')
    p.append('    </g>')
    p.append('    <g class="secHand" style="--cx:%dpx;--cy:%dpx;'
             'animation-delay:%.3fs">' % (cx, cy, -ss))
    p.append('      <path d="M%d %dV%d" stroke="%s" stroke-width="2" '
             'stroke-linecap="round" filter="url(#glow)"/>'
             % (cx, cy + 12, cy - 60, ACCENT))
    p.append('      <circle cx="%d" cy="%d" r="4.5" fill="%s"/>' % (cx, cy - 60, ACCENT3))
    p.append('    </g>')
    p.append('    <circle cx="%d" cy="%d" r="6" fill="#0A1725" stroke="%s" '
             'stroke-width="2.4"/>' % (cx, cy, ACCENT))
    p.append('    <circle cx="%d" cy="%d" r="2" fill="%s"/>' % (cx, cy, WHITE))
    p.append('  </g>')

    # bang so
    px = 244
    p.append('  <g class="fadeUp" style="animation-delay:.2s">')
    p.append('    <text x="%d" y="74" class="clockLabel">GIỜ VIỆT NAM · UTC+7</text>'
             % px)
    p.append('    <text x="%d" y="124" class="clockTime" fill="url(#titleGrad)">'
             '%s</text>' % (px, dt.strftime("%H:%M")))
    p.append('    <text x="%d" y="148" class="clockDate">%s · %s</text>'
             % (px, esc(WEEKDAY_VI[dt.weekday()]), dt.strftime("%d/%m/%Y")))
    p.append('  </g>')

    # pill loi chao
    greet = greeting(hh)
    gw = 26 + len(greet) * 6.6
    p.append('  <g class="fadeUp" style="animation-delay:.3s">')
    p.append('    <rect x="%d" y="160" width="%.0f" height="24" rx="12" '
             'fill="#0A2135" stroke="%s" stroke-opacity=".85"/>'
             % (px, gw, ACCENT2))
    p.append('    <circle cx="%d" cy="172" r="3.4" fill="%s" class="pulse"/>'
             % (px + 14, ACCENT3))
    p.append('    <text x="%d" y="176" class="clockBig">%s</text>'
             % (px + 25, esc(greet)))
    p.append('  </g>')

    # tien do ngay
    done = ((hh * 60 + mm) / 1440.0) * 100
    bar_w = 372
    p.append('  <g class="fadeUp" style="animation-delay:.4s">')
    p.append('    <text x="%d" y="206" class="footNote" '
             'style="letter-spacing:1.1px">NGÀY HÔM NAY ĐÃ TRÔI</text>' % px)
    p.append('    <text x="%d" y="206" text-anchor="end" class="legendValue">'
             '%.0f%%</text>' % (px + bar_w, done))
    p.append('    <rect x="%d" y="212" width="%d" height="8" rx="4" fill="#132A3D"/>'
             % (px, bar_w))
    p.append('    <rect x="%d" y="212" width="%.1f" height="8" rx="4" '
             'fill="url(#barGrad)">' % (px, bar_w * done / 100.0))
    p.append('      <animate attributeName="width" from="0" to="%.1f" dur="1.3s" '
             'begin=".3s" fill="freeze" calcMode="spline" keyTimes="0;1" '
             'keySplines="0.2 0.8 0.2 1"/>' % (bar_w * done / 100.0))
    p.append('      <animate attributeName="opacity" values=".75;1;.75" '
             'dur="3.4s" repeatCount="indefinite"/>')
    p.append('    </rect>')
    p.append('    <circle cx="%.1f" cy="216" r="5" fill="%s" filter="url(#glow)" '
             'class="pulse"/>' % (px + bar_w * done / 100.0, ACCENT3))
    p.append('  </g>')

    # chan
    p.append('  <g class="fadeUp" style="animation-delay:.5s">')
    p.append('    <circle cx="%d" cy="%d" r="3" fill="%s" class="pulse"/>'
             % (px, h - 16, ACCENT))
    p.append('    <text x="%d" y="%d" class="footNote">Cập nhật lúc %s · '
             'tự làm mới mỗi 5 phút bởi GitHub Actions</text>'
             % (px + 10, h - 13, esc(dt.strftime("%H:%M"))))
    p.append('  </g>')
    p.append('</svg>')
    return "\n".join(p)


# ------------------------------------------------------------------ waiting
def card_waiting(w, title, line1, line2):
    p = open_svg(w, 258, title)
    p.append('  <text x="%d" y="112" text-anchor="middle" class="fSans" '
             'style="font:700 14px %s;fill:#C6D8EA">%s</text>'
             % (w // 2, FONT, esc(line1)))
    p.append('  <text x="%d" y="138" text-anchor="middle" class="footNote" '
             'style="font-size:10px">%s</text>' % (w // 2, esc(line2)))
    for i in range(3):
        p.append('  <circle cx="%d" cy="170" r="4.5" fill="%s" class="pulse" '
                 'style="animation-delay:%.2fs"/>'
                 % (w // 2 - 18 + i * 18, [TITLE, ACCENT, ACCENT3][i], i * 0.3))
    p.append('</svg>')
    return "\n".join(p)


# ------------------------------------------------------------------ data
def collect():
    print("  tao the cho user : %s" % USER)
    print("  co GITHUB_TOKEN  : %s" % ("co" if TOKEN else "KHONG CO"))
    user = api("/users/" + urllib.parse.quote(USER))
    if not user:
        sys.stderr.write("  !! khong doc duoc /users/%s\n" % USER)
        return None
    print("  OK /users/%s -> public_repos=%s followers=%s"
          % (USER, user.get("public_repos"), user.get("followers")))

    repos = []
    for page in range(1, 6):
        chunk = api("/users/%s/repos?per_page=100&type=owner&sort=pushed&page=%d"
                    % (urllib.parse.quote(USER), page))
        if not chunk:
            break
        repos.extend(chunk)
        if len(chunk) < 100:
            break

    own = [r for r in repos if not r.get("fork")]
    stars = sum(r.get("stargazers_count", 0) for r in own)
    forks = sum(r.get("forks_count", 0) for r in own)

    langs = {}
    for r in own[:40]:
        data = api("/repos/%s/languages" % r.get("full_name", ""))
        if not data:
            continue
        for k, v in data.items():
            langs[k] = langs.get(k, 0) + int(v)
    if not langs:
        for r in own:
            k = r.get("language")
            if k:
                langs[k] = langs.get(k, 0) + 1

    commits = None
    s = api("/search/commits?q=author:%s&per_page=1" % urllib.parse.quote(USER))
    if isinstance(s, dict) and "total_count" in s:
        commits = s["total_count"]
    else:
        sys.stderr.write("  (chu y) khong lay duoc so commit -> the se hien '-'\n")
    print("  tong ket: repos=%d own=%d stars=%d forks=%d langs=%d commits=%s"
          % (len(repos), len(own), stars, forks, len(langs), commits))

    return {
        "name": DISPLAY_NAME or user.get("name") or user.get("login") or USER,
        "stars": stars,
        "forks": forks,
        "repos": user.get("public_repos", len(own)),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "commits": commits,
        "langs": langs or {"Python": 1},
    }


def demo_data():
    return {
        "name": "Standardize Paradigm",
        "stars": 128, "forks": 24, "repos": 17,
        "followers": 96, "following": 42, "commits": 1482,
        "langs": {"Python": 512000, "TypeScript": 261000, "HTML": 143000,
                  "CSS": 96000, "C++": 41000, "JavaScript": 22000,
                  "Shell": 9000, "Markdown": 6000},
    }


def grade(d):
    score = (d["stars"] * 3 + d["repos"] * 4 + d["followers"] * 5
             + (d["commits"] or 0) * 0.06 + d["forks"] * 2)
    table = [(900, "S", 0.98), (600, "A+", 0.92), (380, "A", 0.84),
             (220, "B+", 0.74), (120, "B", 0.62), (50, "C+", 0.48),
             (0, "C", 0.34)]
    for need, letter, pct in table:
        if score >= need:
            return letter, pct
    return "C", 0.34


# ------------------------------------------------------------------ output
def write(name, content):
    """Ghi file kieu atomic: hoac thanh cong hoan toan, hoac khong doi gi."""
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    final = os.path.join(OUT_DIR, name)
    fd, tmp = tempfile.mkstemp(dir=OUT_DIR, prefix=".tmp-", suffix=".svg")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(tmp, 0o644)
        os.replace(tmp, final)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    print("da ghi %s (%d bytes)" % (final, len(content.encode("utf-8"))))


def main():
    dt = now_vn()
    args = set(sys.argv[1:])
    want_all = "--all" in args or not (
        args & {"--cards", "--clock", "--hero", "--placeholder"})
    want_cards = want_all or "--cards" in args
    want_clock = want_all or "--clock" in args
    want_hero = want_all or "--hero" in args

    print("== generate_cards.py · %s (UTC+7) ==" % dt.strftime("%d/%m/%Y %H:%M:%S"))

    if "--placeholder" in args:
        write("stats.svg", card_waiting(
            640, "GitHub Stats",
            "Chạy workflow \"Profile Cards\" để tạo thẻ này",
            "Actions → Profile Cards (LTS) → Run workflow"))
        write("top-langs.svg", card_waiting(
            640, "Most Used Languages",
            "Chưa có dữ liệu",
            "Thẻ này sẽ tự điền sau khi workflow chạy lần đầu"))
        return 0

    if want_hero:
        write("hero.svg", hero(dt))
        write("divider.svg", divider())

    if want_clock:
        write("live-clock.svg", card_clock(dt))

    if want_cards:
        if DEMO:
            d = demo_data()
        else:
            if not USER:
                sys.stderr.write(BAD_USER)
                return 1 if STRICT else 0
            d = collect()
            if not d:
                sys.stderr.write(BAD_DATA)
                return 1 if STRICT else 0
        write("stats.svg", card_stats(d, dt))
        write("top-langs.svg", card_langs(d, dt))
        print("  XONG: 2 the da duoc ghi bang DU LIEU THAT")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        import traceback
        traceback.print_exc()
        sys.stderr.write("Loi khong mong doi: %s\n" % exc)
        sys.exit(1 if STRICT else 0)
