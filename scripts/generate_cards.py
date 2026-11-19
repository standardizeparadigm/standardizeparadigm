#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 generate_cards.py — cửa vào duy nhất để vẽ toàn bộ SVG của profile
=====================================================================
 Vì sao có file này?
   Các service như github-readme-stats.vercel.app dùng chung server công
   cộng cho hàng trăm nghìn người -> hết quota là ảnh báo lỗi 503.
   Ở đây ta tự gọi API bằng token riêng của repo, tự vẽ, rồi commit ảnh
   vào repo. Ảnh nằm trong repo nên KHÔNG BAO GIỜ bị rate-limit.

 Sinh ra:
   assets/hero.svg         ảnh bìa động        (không cần API)
   assets/divider.svg      đường kẻ động        (không cần API)
   assets/footer.svg       chân trang động      (không cần API)
   assets/live-clock.svg   đồng hồ Việt Nam     (không cần API)
   assets/stats.svg        thẻ thống kê         (cần API)
   assets/top-langs.svg    thẻ ngôn ngữ         (cần API)
   assets/activity.svg     lịch contribution    (cần GraphQL + token)

 Ví dụ:
   python3 scripts/generate_cards.py --all
   python3 scripts/generate_cards.py --cards --activity --strict
   python3 scripts/generate_cards.py --clock
   python3 scripts/generate_cards.py --hero --theme emerald --lang en
   python3 scripts/generate_cards.py --demo --all --out /tmp/thu
   python3 scripts/generate_cards.py --list-themes

 Nguyên tắc ổn định:
   - Chỉ dùng thư viện chuẩn (không pip install -> không vỡ môi trường)
   - Ghi file kiểu atomic: lỗi giữa chừng thì ảnh cũ vẫn nguyên
   - API lỗi: giữ ảnh cũ, không ghi đè bằng thẻ rỗng
   - Tự thử lại 3 lần khi mạng lỗi hoặc bị giới hạn
=====================================================================
"""

import argparse
import hashlib
import json
import os
import random
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from svgkit import (activity_card, api, clock_card, divider, footer, hero,  # noqa: E402
                    i18n, langs_card, stats_card, status_strip, waiting_card)
from svgkit.palette import THEMES, get_palette  # noqa: E402

OUT_DIR = os.environ.get("OUT_DIR", "assets")
USER = (os.environ.get("GH_USER")
        or os.environ.get("USERNAME")
        or os.environ.get("GITHUB_REPOSITORY_OWNER")
        or "")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
DISPLAY_NAME = os.environ.get("DISPLAY_NAME", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "standardizeparadigm/standardizeparadigm")

BAD_USER = (
    "\n!! KHÔNG BIẾT VẼ THẺ CHO AI\n"
    "   Thiếu biến GH_USER / USERNAME / GITHUB_REPOSITORY_OWNER.\n"
    "   Trong workflow cần:  env:  GH_USER: ...owner...\n")

BAD_DATA = (
    "\n!! KHÔNG LẤY ĐƯỢC DỮ LIỆU TỪ API GITHUB\n"
    "   Xem các dòng HTTP ở trên để biết lý do. Thường là:\n"
    "    - 404: sai tên user (kiểm tra GH_USER)\n"
    "    - 401: GITHUB_TOKEN không được truyền vào bước này\n"
    "    - 403 + rate limit: đợi vài phút rồi chạy lại\n"
    "   ẢNH CŨ ĐƯỢC GIỮ NGUYÊN (không ghi đè bằng ảnh rỗng).\n")


SMART = False          # --smart: bỏ qua ghi khi dữ liệu chưa đổi
DRY_RUN = False        # --dry-run: vẽ nhưng không ghi file nào
QUIET = False          # --quiet: chỉ in cảnh báo và lỗi
DATA_MARK = re.compile(r"<!-- data:([0-9a-f]{8,}) -->")


# ------------------------------------------------------------------ output
def say(message):
    """In tiến trình — trừ khi người dùng chọn --quiet."""
    if not QUIET:
        print(message)


def data_hash(payload):
    """Vân tay ngắn của dữ liệu (không gồm thời gian) để so sánh ảnh."""
    if payload is None:
        return None
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def stamp_data_mark(content, fingerprint):
    """Nhúng dấu dữ liệu vào ảnh để lượt sau biết có cần vẽ lại không."""
    if not fingerprint or "<!-- data:" in content:
        return content
    return content.replace("</svg>", "<!-- data:%s -->\n</svg>" % fingerprint)


def read_mark(path):
    try:
        with open(path, encoding="utf-8") as handle:
            found = DATA_MARK.search(handle.read())
    except OSError:
        return None
    return found.group(1) if found else None


def write(name, content, fingerprint=None):
    """Ghi file kiểu atomic: hoặc xong hẳn, hoặc không đụng gì tới file cũ.

    Ở chế độ --smart, nếu ảnh cũ đã mang đúng dấu dữ liệu này thì bỏ qua:
    dữ liệu GitHub chưa đổi thì không cần commit thêm một dòng thời gian.
    """
    content = stamp_data_mark(content, fingerprint)
    final_path = os.path.join(OUT_DIR, name)
    if SMART and fingerprint and read_mark(final_path) == fingerprint:
        say("= %s không đổi (bỏ qua)" % name)
        return False
    if DRY_RUN:
        say("[dry-run] sẽ ghi %s (%d bytes)"
            % (final_path, len(content.encode("utf-8"))))
        return False
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    final_path = os.path.join(OUT_DIR, name)
    fd, tmp_path = tempfile.mkstemp(dir=OUT_DIR, prefix=".tmp-", suffix=".svg")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, final_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    say("đã ghi %s (%d bytes)" % (final_path, len(content.encode("utf-8"))))
    return True


# ------------------------------------------------------------------ demo
def demo_data():
    return {
        "name": "Standardize Paradigm",
        "stars": 128, "forks": 24, "repos": 17,
        "followers": 96, "following": 42, "commits": 1482,
        "langs": {"Python": 512000, "TypeScript": 261000, "HTML": 143000,
                  "CSS": 96000, "C++": 41000, "JavaScript": 22000,
                  "Shell": 9000, "Markdown": 6000},
    }


def status_demo_rows():
    """Trạng thái mẫu cho --demo: đủ 5 loại để xem màu."""
    return [("3D CONTRIB", "passing"), ("STATS CARDS", "passing"),
            ("LIVE CLOCK", "running"), ("README GARDEN", "passing"),
            ("HEALTH", "failing"), ("WELCOME", "none"), ("STATUS", "passing")]


def demo_contrib(dt):
    """Dữ liệu contribution giả nhưng ổn định, đủ để xem thử bố cục."""
    from datetime import date, timedelta
    rnd = random.Random(7)
    days = []
    for offset in range(364, -1, -1):
        day = dt.date() - timedelta(days=offset)
        weight = 1.0 if day.weekday() < 5 else 0.45
        days.append((day, max(0, int(rnd.gauss(4, 5) * weight))))
    current, longest = api._streaks(days)
    return {"total": sum(c for _, c in days), "days": days,
            "streak_current": current, "streak_longest": longest}


# ------------------------------------------------------------------ CLI
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Vẽ toàn bộ SVG cho profile README.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("user", nargs="?", default="",
                        help="tên user GitHub (mặc định lấy từ GH_USER)")
    parser.add_argument("--all", action="store_true", help="vẽ tất cả (mặc định)")
    parser.add_argument("--cards", action="store_true", help="stats + top-langs")
    parser.add_argument("--hero", action="store_true", help="hero + divider + footer")
    parser.add_argument("--clock", action="store_true", help="đồng hồ")
    parser.add_argument("--activity", action="store_true", help="thẻ hoạt động")
    parser.add_argument("--status", action="store_true",
                        help="dải trạng thái các workflow")
    parser.add_argument("--placeholder", action="store_true", help="thẻ chờ dữ liệu")
    parser.add_argument("--demo", action="store_true", help="dùng dữ liệu mẫu")
    parser.add_argument("--strict", action="store_true",
                        help="lỗi dữ liệu thì trả mã 1 (mặc định chỉ cảnh báo)")
    parser.add_argument("--theme", default="sky",
                        help="bảng màu: %s" % ", ".join(THEMES))
    parser.add_argument("--lang", default=i18n.DEFAULT_LANG,
                        help="ngôn ngữ thẻ: vi | en")
    parser.add_argument("--out", default=None, help="thư mục ghi ảnh")
    parser.add_argument("--list-themes", action="store_true",
                        help="in danh sách theme rồi thoát")
    parser.add_argument("--list-langs", action="store_true",
                        help="in danh sách ngôn ngữ rồi thoát")
    parser.add_argument("--version", action="store_true",
                        help="in phiên bản rồi thoát")
    parser.add_argument("--check", action="store_true",
                        help="kiểm tra các SVG đã có trong thư mục ra")
    parser.add_argument("--smart", action="store_true",
                        help="chỉ ghi ảnh khi dữ liệu thật sự đổi (bớt commit rác)")
    parser.add_argument("--dry-run", action="store_true",
                        help="vẽ và kiểm tra nhưng không ghi file nào")
    parser.add_argument("--quiet", action="store_true",
                        help="không in tiến trình, chỉ in lỗi")
    return parser.parse_args(argv)


def check_assets(directory):
    """Parse mọi .svg trong thư mục; in bảng và trả mã thoát."""
    import xml.dom.minidom

    files = sorted(f for f in os.listdir(directory) if f.endswith(".svg")) \
        if os.path.isdir(directory) else []
    if not files:
        sys.stderr.write("Không tìm thấy SVG nào trong %s\n" % directory)
        return 1
    bad = 0
    for name in files:
        path = os.path.join(directory, name)
        try:
            xml.dom.minidom.parse(path)
        except Exception as error:                      # noqa: BLE001
            bad += 1
            print("  ✗ %-20s %s" % (name, error))
        else:
            print("  ✓ %-20s %6d bytes" % (name, os.path.getsize(path)))
    print("%d/%d SVG hợp lệ" % (len(files) - bad, len(files)))
    return 1 if bad else 0


def main(argv=None):
    global OUT_DIR, USER, SMART, DRY_RUN, QUIET
    args = parse_args(argv)
    SMART = bool(args.smart)
    DRY_RUN = bool(args.dry_run)
    QUIET = bool(args.quiet)

    if args.version:
        print("generate_cards.py %s (svgkit)" % sys.modules["svgkit"].__version__)
        return 0

    if args.list_langs:
        for code in i18n.LANGS:
            print("%-3s %s" % (code, i18n.get(code)("lang.name")))
        return 0

    if args.check:
        return check_assets(args.out or OUT_DIR)

    if args.list_themes:
        for name, palette in THEMES.items():
            say("%-9s accent=%s accent2=%s accent3=%s"
                  % (name, palette.accent, palette.accent2, palette.accent3))
        return 0

    if args.out:
        OUT_DIR = args.out
    if args.user:
        USER = args.user

    selected = (args.cards or args.hero or args.clock or args.activity
                or args.status)
    want_all = args.all or not selected

    palette = get_palette(args.theme)
    translator = i18n.get(args.lang)
    dt = api.now_vn()

    say("== generate_cards.py %s · theme=%s · lang=%s · %s (UTC+7) =="
          % (sys.modules["svgkit"].__version__, palette.name,
             translator.lang, dt.strftime("%d/%m/%Y %H:%M:%S")))

    if args.placeholder:
        write("stats.svg", waiting_card(
            palette, 640, translator("wait.title.stats"),
            translator("wait.line1"), translator("wait.line2"),
            desc=translator("desc.wait")))
        write("top-langs.svg", waiting_card(
            palette, 640, translator("wait.title.langs"),
            translator("wait.empty1"), translator("wait.empty2"),
            desc=translator("desc.wait")))
        return 0

    status = 0
    data = None

    if want_all or args.hero:
        # Ảnh bìa / chân trang là thiết kế, không phải số liệu: vẽ lại mỗi
        # giờ một lần (hoặc khi đổi theme / đổi tên) thay vì mỗi 10 phút.
        design = data_hash({"design": [USER, DISPLAY_NAME, palette.name,
                                       translator.lang, dt.strftime("%Y-%m-%dT%H")]})
        write("hero.svg", hero(palette, dt, translator), design)
        write("divider.svg", divider(palette), design)
        write("footer.svg", footer(palette, translator), design)

    if want_all or args.clock:
        write("live-clock.svg", clock_card(palette, dt, translator))

    if want_all or args.cards:
        if args.demo:
            data = demo_data()
        else:
            if not USER:
                sys.stderr.write(BAD_USER)
                return 1 if args.strict else 0
            data = api.collect_user(USER, TOKEN, DISPLAY_NAME)
            if not data:
                sys.stderr.write(BAD_DATA)
                return 1 if args.strict else 0
        fingerprint = data_hash({"cards": data})
        write("stats.svg", stats_card(palette, data, dt, translator), fingerprint)
        write("top-langs.svg", langs_card(palette, data, dt, translator), fingerprint)
        say("  XONG: 2 thẻ đã được ghi bằng dữ liệu thật")

    if want_all or args.activity:
        contrib = (demo_contrib(dt) if args.demo
                   else api.contributions(USER or DISPLAY_NAME, TOKEN))
        if contrib:
            content = activity_card(palette, contrib, dt, translator)
            if content:
                write("activity.svg", content,
                      data_hash({"activity": contrib}))
        else:
            say("  (bỏ qua) không có dữ liệu contribution — giữ nguyên ảnh cũ")
            status = status or (1 if args.strict else 0)

    if want_all or args.status:
        if args.demo:
            rows = status_demo_rows()
        else:
            owner, _, repo = REPO.partition("/")
            rows = api.workflow_states(owner, repo, TOKEN)
        write("status.svg", status_strip(palette, rows, dt, translator),
              data_hash({"status": rows}))

    return status


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:                       # pragma: no cover
        import traceback
        traceback.print_exc()
        sys.stderr.write("Lỗi không mong đợi: %s\n" % error)
        sys.exit(1 if "--strict" in sys.argv else 0)
