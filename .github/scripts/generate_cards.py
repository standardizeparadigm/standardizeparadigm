#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 generate_cards.py  --  Bo sinh the thong ke GitHub (ban LTS)
=====================================================================
 Tai sao co file nay?
   Cac service nhu github-readme-stats.vercel.app la server CONG CONG
   dung chung cho hang tram nghin nguoi -> het quota API GitHub la anh
   bao loi (503 / Maximum retries exceeded). Day la loi phia service.

   File nay tu goi API GitHub bang token rieng cua repo ban, tu ve SVG,
   roi commit vao repo. Anh nam trong repo -> KHONG BAO GIO bi rate-limit.

 Dac diem LTS:
   - Chi dung thu vien chuan cua Python (khong pip install -> khong vo)
   - Dung GITHUB_TOKEN co san cua Actions (quota rieng cua repo ban)
   - Neu API loi: giu nguyen anh cu, KHONG ghi de anh rong, exit 0
   - Tu thu lai 3 lan khi mang loi

 Chay:
   python3 scripts/generate_cards.py                 (that, trong Actions)
   python3 scripts/generate_cards.py --demo          (du lieu mau, test)
   python3 scripts/generate_cards.py --placeholder   (the cho "dang doi")
=====================================================================
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# ------------------------------------------------------------------ config
API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER = os.environ.get("USERNAME", "")
OUT_DIR = os.environ.get("OUT_DIR", "assets")
DISPLAY_NAME = os.environ.get("DISPLAY_NAME", "")

DEMO = "--demo" in sys.argv
PLACEHOLDER = "--placeholder" in sys.argv
for a in sys.argv[1:]:
    if not a.startswith("--"):
        USER = a

# ------------------------------------------------------------------ theme
BG = "#0D1117"
TITLE = "#38BDF8"
TEXT = "#C9D1D9"
DIM = "#8B949E"
ACCENT = "#0EA5E9"
LIGHT = "#7DD3FC"
WHITE = "#FFFFFF"

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
    except Exception:
        return "-"
    if n >= 1000000:
        return str(round(n / 1000000.0, 1)) + "M"
    if n >= 1000:
        return str(round(n / 1000.0, 1)) + "k"
    return str(n)


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
            if e.code in (403, 429) and attempt < tries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            sys.stderr.write("HTTP %s tren %s\n" % (e.code, url))
            return None
        except Exception as e:
            if attempt < tries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            sys.stderr.write("Loi mang: %s\n" % e)
            return None
    return None


# ------------------------------------------------------------------ collect
def collect():
    user = api("/users/" + urllib.parse.quote(USER))
    if not user:
        return None

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

    return {
        "name": DISPLAY_NAME or user.get("name") or user.get("login") or USER,
        "stars": stars,
        "forks": forks,
        "repos": user.get("public_repos", len(own)),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "commits": commits,
        "langs": langs,
    }


def demo_data():
    return {
        "name": "Standardize Paradigm",
        "stars": 128, "forks": 24, "repos": 17,
        "followers": 96, "following": 42, "commits": 1482,
        "langs": {"Python": 512000, "JavaScript": 261000, "HTML": 143000,
                  "CSS": 96000, "C++": 41000, "Java": 22000,
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


# ------------------------------------------------------------------ svg base
STYLE = "\n".join([
    "    .t   { font: 700 18px 'Segoe UI', Ubuntu, Helvetica, sans-serif; fill: " + TITLE + " }",
    "    .k   { font: 600 13px 'Segoe UI', Ubuntu, Helvetica, sans-serif; fill: " + TEXT + " }",
    "    .v   { font: 700 13px 'Segoe UI', Ubuntu, Helvetica, sans-serif; fill: " + LIGHT + " }",
    "    .s   { font: 400 10px 'Segoe UI', Ubuntu, Helvetica, sans-serif; fill: " + DIM + " }",
    "    .g   { font: 700 26px 'Segoe UI', Ubuntu, Helvetica, sans-serif; fill: " + WHITE + " }",
    "    .row { opacity: 0; animation: slide .55s ease-out forwards }",
    "    @keyframes slide { from { opacity: 0; transform: translateX(-10px) } to { opacity: 1; transform: translateX(0) } }",
    "    .bar { transform: scaleX(0); transform-origin: left center; animation: grow 1.15s cubic-bezier(.2,.8,.2,1) forwards }",
    "    @keyframes grow { to { transform: scaleX(1) } }",
    "    .glow { animation: pulse 3.2s ease-in-out infinite }",
    "    @keyframes pulse { 0%, 100% { opacity: .55 } 50% { opacity: 1 } }",
])


def head(w, h, title, label):
    return "\n".join([
        '<svg width="%d" height="%d" viewBox="0 0 %d %d" fill="none" '
        'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">'
        % (w, h, w, h, esc(label)),
        "  <style>",
        STYLE,
        "  </style>",
        '  <defs>',
        '    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">',
        '      <stop offset="0%%" stop-color="%s" />' % TITLE,
        '      <stop offset="100%%" stop-color="%s" stop-opacity="0.15" />' % ACCENT,
        '    </linearGradient>',
        '  </defs>',
        '  <rect x="0.5" y="0.5" width="%d" height="%d" rx="10" fill="%s" '
        'stroke="url(#edge)" stroke-width="1" />' % (w - 1, h - 1, BG),
        '  <text x="25" y="33" class="t">%s</text>' % esc(title),
        '  <rect x="25" y="41" width="46" height="3" rx="1.5" fill="%s" class="glow" />' % TITLE,
    ])


# ------------------------------------------------------------------ card 1
def card_stats(d):
    w, h = 500, 205
    letter, pct = grade(d)
    rows = [
        ("\u2b50", "Total Stars Earned", human(d["stars"])),
        ("\U0001f374", "Total Forks", human(d["forks"])),
        ("\U0001f4e6", "Public Repositories", human(d["repos"])),
        ("\U0001f465", "Followers", human(d["followers"])),
        ("\U0001f52d", "Following", human(d["following"])),
        ("\u26a1", "Total Commits",
         human(d["commits"]) if d["commits"] is not None else "-"),
    ]
    p = [head(w, h, esc(d["name"]) + " - GitHub Stats", "github stats card")]
    y = 68
    for i, (icon, key, val) in enumerate(rows):
        delay = "%.2fs" % (0.12 * i)
        p.append('  <g class="row" style="animation-delay: %s">' % delay)
        p.append('    <text x="27" y="%d" class="k">%s</text>' % (y, icon))
        p.append('    <text x="52" y="%d" class="k">%s</text>' % (y, esc(key)))
        p.append('    <text x="330" y="%d" class="v" text-anchor="end">%s</text>'
                 % (y, esc(val)))
        p.append("  </g>")
        y += 22

    cx, cy, r = 417, 112, 44
    circ = 2 * 3.14159265 * r
    off = circ * (1 - pct)
    p.append('  <circle cx="%d" cy="%d" r="%d" stroke="%s" stroke-width="7" '
             'fill="none" opacity="0.25" />' % (cx, cy, r, ACCENT))
    p.append('  <circle cx="%d" cy="%d" r="%d" stroke="%s" stroke-width="7" '
             'fill="none" stroke-linecap="round" '
             'transform="rotate(-90 %d %d)" '
             'stroke-dasharray="%.1f" stroke-dashoffset="%.1f">'
             % (cx, cy, r, TITLE, cx, cy, circ, circ))
    p.append('    <animate attributeName="stroke-dashoffset" from="%.1f" '
             'to="%.1f" dur="1.4s" fill="freeze" '
             'calcMode="spline" keySplines="0.2 0.8 0.2 1" />' % (circ, off))
    p.append("  </circle>")
    p.append('  <text x="%d" y="%d" class="g" text-anchor="middle">%s</text>'
             % (cx, cy + 8, letter))
    p.append('  <text x="%d" y="%d" class="s" text-anchor="middle">RANK</text>'
             % (cx, cy + 26))
    p.append('  <text x="25" y="%d" class="s">Tu dong cap nhat moi ngay '
             '\u2022 anh nam trong repo nen khong bao gio rate-limit</text>'
             % (h - 14))
    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------------ card 2
def card_langs(d):
    w, h = 400, 205
    items = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:8]
    total = sum(v for _, v in items) or 1
    p = [head(w, h, "Most Used Languages", "most used languages card")]

    bx, by, bw, bh = 25, 60, w - 50, 11
    p.append('  <clipPath id="clip"><rect x="%d" y="%d" width="%d" height="%d" '
             'rx="5.5" /></clipPath>' % (bx, by, bw, bh))
    p.append('  <g clip-path="url(#clip)">')
    p.append('    <rect x="%d" y="%d" width="%d" height="%d" fill="#161B22" />'
             % (bx, by, bw, bh))
    x = float(bx)
    for i, (name, val) in enumerate(items):
        seg = bw * (val / float(total))
        p.append('    <rect x="%.1f" y="%d" width="%.1f" height="%d" fill="%s" '
                 'class="bar" style="animation-delay: %.2fs" />'
                 % (x, by, max(seg, 1.0), bh, lang_color(name, i), 0.08 * i))
        x += seg
    p.append("  </g>")

    col_x = [25, 215]
    y0 = 104
    for i, (name, val) in enumerate(items):
        cx_ = col_x[i % 2]
        y = y0 + (i // 2) * 24
        pct = 100.0 * val / total
        label = name if len(name) <= 13 else name[:12] + "\u2026"
        p.append('  <g class="row" style="animation-delay: %.2fs">' % (0.1 * i))
        p.append('    <circle cx="%d" cy="%d" r="5" fill="%s" />'
                 % (cx_ + 5, y - 4, lang_color(name, i)))
        p.append('    <text x="%d" y="%d" class="k">%s</text>'
                 % (cx_ + 17, y, esc(label)))
        p.append('    <text x="%d" y="%d" class="v" text-anchor="end">%.1f%%</text>'
                 % (cx_ + 160, y, pct))
        p.append("  </g>")

    p.append('  <text x="25" y="%d" class="s">Tinh theo so byte code that '
             'trong cac repo cua ban</text>' % (h - 14))
    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------------ waiting
def card_waiting(w, title, line1, line2):
    p = [head(w, 205, title, "waiting card")]
    p.append('  <text x="%d" y="100" class="k" text-anchor="middle">%s</text>'
             % (w // 2, esc(line1)))
    p.append('  <text x="%d" y="126" class="s" text-anchor="middle">%s</text>'
             % (w // 2, esc(line2)))
    p.append('  <circle cx="%d" cy="152" r="5" fill="%s" class="glow" />'
             % (w // 2 - 16, TITLE))
    p.append('  <circle cx="%d" cy="152" r="5" fill="%s" class="glow" '
             'style="animation-delay:.4s" />' % (w // 2, ACCENT))
    p.append('  <circle cx="%d" cy="152" r="5" fill="%s" class="glow" '
             'style="animation-delay:.8s" />' % (w // 2 + 16, LIGHT))
    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------------ main
def write(name, content):
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("da ghi %s (%d bytes)" % (path, len(content.encode("utf-8"))))


def main():
    if PLACEHOLDER:
        write("stats.svg", card_waiting(
            500, "GitHub Stats",
            "Chay workflow \"Profile Cards\" de tao the nay",
            "Actions -> Profile Cards (LTS) -> Run workflow"))
        write("top-langs.svg", card_waiting(
            400, "Most Used Languages",
            "Chua co du lieu",
            "The nay se tu dien sau khi workflow chay lan dau"))
        return 0

    if DEMO:
        d = demo_data()
    else:
        if not USER:
            sys.stderr.write("Thieu USERNAME -> giu nguyen anh cu.\n")
            return 0
        d = collect()
        if not d:
            sys.stderr.write("Khong lay duoc du lieu -> GIU NGUYEN anh cu, "
                             "README van hien binh thuong.\n")
            return 0

    write("stats.svg", card_stats(d))
    write("top-langs.svg", card_langs(d))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        sys.stderr.write("Loi khong mong doi: %s -> giu nguyen anh cu.\n" % exc)
        sys.exit(0)
