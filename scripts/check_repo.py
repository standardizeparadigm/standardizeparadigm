#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 check_repo.py  --  "Sức khỏe" của repo, kiểm tra trước khi lỗi xảy ra
=====================================================================
 Chạy trong workflow .github/workflows/health.yml, cũng chạy tay được:

   python3 scripts/check_repo.py            # báo lỗi + cảnh báo
   python3 scripts/check_repo.py --quiet    # chỉ in khi có vấn đề

 Nó kiểm tra:
   1. Mọi file SVG có phải XML hợp lệ không
   2. Chữ bị lỗi encoding (ký tự thay thế, chữ Hàn/Trung lạc vào,
      mojibake kiểu chữ Latin-1 lạc vào)
   3. URL trong tài liệu: %-escape có đúng không, có giải mã ra UTF-8
      hợp lệ không, có dấu cách lạc không
   4. Link nội bộ (#anchor) có trỏ tới mục có thật không
   5. Ảnh dùng đường dẫn tương đối có tồn tại thật không
   6. Workflow YAML: parse được, có name/on/jobs, job có runs-on,
      cron đủ 5 trường
   7. Script Python: biên dịch được
   8. Vệ sinh file: không BOM, không CRLF, không ký tự điều khiển,
      UTF-8 hợp lệ, không có khoảng trắng thừa cuối dòng

 Mã thoát: 0 = ổn (có thể có cảnh báo), 1 = có lỗi cần sửa.
=====================================================================
"""

import codecs
import io
import os
import re
import sys
import glob
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUIET = "--quiet" in sys.argv

errors = []
warnings = []
checked = {"svg": 0, "md": 0, "yml": 0, "py": 0, "file": 0}


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def read(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return f.read()


# --------------------------------------------------------------- 1. SVG
def check_svg():
    """Mọi file `.svg` phải parse được XML, có thẻ `<svg>` và có `<title>`.

    `<title>` là thứ trình đọc màn hình đọc thay cho "graphic"; ảnh trang trí
    thuần tuý được miễn nếu tự khai `role="presentation"` — đó là cách đúng
    để nói "đừng đọc ảnh này", chứ không phải bỏ trống.
    """
    import xml.dom.minidom as md
    for path in sorted(glob.glob(os.path.join(ROOT, "**", "*.svg"),
                                recursive=True)):
        if "/.git/" in path.replace(os.sep, "/"):
            continue
        checked["svg"] += 1
        try:
            md.parse(path)
        except Exception as e:
            err("SVG lỗi XML: %s — %s" % (rel(path), e))
            continue
        raw = read(path)
        if "<svg" not in raw:
            err("SVG thiếu thẻ <svg>: %s" % rel(path))
        elif "<title>" not in raw:
            # <title> là thứ trình đọc màn hình đọc thay cho "graphic".
            # Ảnh trang trí thuần tuý (đường kẻ) được miễn nếu tự khai báo
            # là trình diễn — đó là cách đúng để nói "đừng đọc ảnh này".
            decorative = ('aria-hidden="true"' in raw
                          or 'role="presentation"' in raw)
            if not decorative:
                err("SVG thiếu <title> (ảnh không có tên đọc lên): %s" % rel(path))


# ------------------------------------------------- 1b. Ảnh phải co giãn được
def check_svg_viewbox(root=None):
    """Mỗi ảnh phải khai báo `viewBox`.

    README đặt ảnh theo phần trăm (`width="48%"`). Không có `viewBox` thì
    `width` bị hiểu là pixel và ảnh giữ nguyên kích thước gốc: nửa màn hình
    trên laptop, tràn ra ngoài trên điện thoại. `viewBox` là thứ biến một
    ảnh vẽ cứng thành một ảnh co giãn.
    """
    root = root or ROOT
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(".svg"):
                continue
            path = os.path.join(base, name)
            head = read(path)[:600]
            if "viewBox=" not in head:
                err("%s thiếu 'viewBox' (không co giãn theo khung)" % rel(path))


# --------------------------------------------------------------- 2. chữ
RE_BAD_CHARS = [
    ("\ufffd", "ký tự thay thế U+FFFD (dữ liệu bị hỏng khi lưu file)"),
]
RE_CJK = re.compile(r"[\u4e00-\u9fff]")
RE_HANGUL = re.compile(r"[\uac00-\ud7af]")
# Các cụm "mojibake" điển hình. Viết bằng escape cho chắc, kẻo file này
# tự bắt lỗi của chính nó. Lưu ý: "Ã" một mình vẫn hợp lệ trong tiếng Việt
# (ĐÃ, Ã...), nên chỉ bắt khi nó đi kèm một ký tự Latin-1 bổ sung.
RE_MOJIBAKE = re.compile("(\u00c3[\u0080-\u00bf]|\u00e2\u20ac|\u00c4\u2018|"
                         "\u00e1\u00ba|\u00e1\u00bb|\u00c6\u00b0|"
                         "\u00c2[\u00bb\u00ab\u00b0])")


def check_text_encoding(path, text):
    """Bắt ký tự lạ trong một file đã đọc: Hán, Hàn, mojibake, ký tự thay thế.

    Tách khỏi `check_markdown` để dùng lại được cho mọi file văn bản, không
    chỉ Markdown.
    """
    for token, why in RE_BAD_CHARS:
        if token in text:
            line = text[:text.index(token)].count("\n") + 1
            err("%s:%d có %s" % (rel(path), line, why))
    m = RE_CJK.search(text)
    if m:
        line = text[:m.start()].count("\n") + 1
        err("%s:%d có chữ Hán lạc vào (%r)" % (rel(path), line, m.group(0)))
    m = RE_HANGUL.search(text)
    if m:
        line = text[:m.start()].count("\n") + 1
        err("%s:%d có chữ Hàn lạc vào (%r)" % (rel(path), line, m.group(0)))
    for m in RE_MOJIBAKE.finditer(text):
        line = text[:m.start()].count("\n") + 1
        err("%s:%d nghi lỗi encoding (%r)" % (rel(path), line, m.group(0)))
        break


# ------------------------------------------------- 2b. Vệ sinh file văn bản
TEXT_SUFFIXES = (".md", ".py", ".yml", ".yaml", ".svg", ".json", ".txt",
                 ".cfg", ".toml", ".html", ".css", ".js")
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".mypy_cache"}
ALLOWED_CONTROL = {"\t", "\n"}


def check_file_hygiene(root=None):
    """Bắt lỗi "vô hình": BOM, xuống dòng CRLF, ký tự điều khiển, UTF-8 hỏng.

    Những lỗi này không hiện ra trên trình duyệt nhưng làm diff loạn, làm
    script đọc file thất bại, và là mầm của mọi kiểu "hỏng kí tự".
    """
    root = root or ROOT
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(TEXT_SUFFIXES):
                continue
            path = os.path.join(base, name)
            checked["file"] += 1
            with open(path, "rb") as handle:
                raw = handle.read()
            if raw.startswith(codecs.BOM_UTF8):
                err("%s: có BOM UTF-8 ở đầu file" % rel(path))
                raw = raw[len(codecs.BOM_UTF8):]
            if b"\r\n" in raw:
                line = raw[:raw.index(b"\r\n")].count(b"\n") + 1
                err("%s:%d dùng CRLF (hãy đổi sang LF)" % (rel(path), line))
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError as error:
                err("%s: không phải UTF-8 hợp lệ (byte %d)"
                    % (rel(path), error.start))
                continue
            for index, line in enumerate(text.split("\n"), 1):
                for char in line:
                    if ord(char) < 32 and char not in ALLOWED_CONTROL:
                        err("%s:%d có ký tự điều khiển U+%04X"
                            % (rel(path), index, ord(char)))
                        break
                else:
                    if line != line.rstrip():
                        warn("%s:%d có khoảng trắng thừa cuối dòng"
                             % (rel(path), index))
                    continue
                break


# --------------------------------------------------------------- 3. URL
URL_RE = re.compile(r"(?:src|href)\s*=\s*\"([^\"]+)\"|"
                    r"\]\(([^)\s]+)\)|"
                    r"(https?://[^\s<>\"')\]]+)")
HEX_ORPHAN = re.compile(r"(?<![%A-Fa-f0-9])([A-F0-9]{6,})(?![A-Fa-f0-9])")


def looks_like_orphan_escape(token):
    """'E280A2' -> '•' (đúng là escape bị mất dấu %).

    Mã màu như '0D1117' hay '38BDF8' giải mã ra byte điều khiển hoặc UTF-8
    sai -> không bị coi là lỗi.
    """
    if len(token) % 2:
        return False
    try:
        text = bytes.fromhex(token).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return False
    if not text:
        return False
    return all(ch.isprintable() and ord(ch) > 0x9f for ch in text)


def verify_url(url, where):
    if url.startswith(("#", "mailto:", "tel:")):
        return
    if " " in url:
        err("%s: URL có dấu cách: %s" % (where, url))
        return
    # %-escape phải đúng
    i = 0
    while True:
        i = url.find("%", i)
        if i < 0:
            break
        frag = url[i + 1:i + 3]
        if len(frag) < 2 or not re.fullmatch(r"[0-9A-Fa-f]{2}", frag):
            err("%s: %%-escape sai chỗ: %s" % (where, url[max(0, i - 12):i + 6]))
            break
        i += 3
    # giải mã phải ra UTF-8 hợp lệ (bắt được kiểu vi%C3ean)
    try:
        urllib.parse.unquote_to_bytes(url).decode("utf-8")
    except UnicodeDecodeError:
        err("%s: URL giải mã ra UTF-8 không hợp lệ: %s" % (where, url))
        return
    # hex "trần" kiểu E280A2 (thiếu dấu %)
    for m in HEX_ORPHAN.finditer(url):
        if looks_like_orphan_escape(m.group(1)):
            err("%s: có %%-escape bị mất dấu %% (%s): %s"
                % (where, m.group(1), url))
            break


def check_markdown(path):
    """Kiểm một file Markdown: ký tự lạ, link, ảnh nhúng, tiêu đề, bảng.

    Gọi từ vòng `os.walk` trong `main()` vì `glob` không đi vào thư mục ẩn
    như `.github/` — nơi có mẫu issue và CONTRIBUTING.
    """
    text = read(path)
    checked["md"] += 1
    check_text_encoding(path, text)
    for m in URL_RE.finditer(text):
        url = m.group(1) or m.group(2) or m.group(3)
        if not url:
            continue
        line = text[:m.start()].count("\n") + 1
        where = "%s:%d" % (rel(path), line)
        verify_url(url, where)
        # ảnh/đường dẫn tương đối phải tồn tại
        if not url.startswith(("http", "#", "mailto:", "tel:", "data:")):
            target = url.split("#")[0].split("?")[0]
            if not target:
                continue
            full = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if not os.path.exists(full):
                err("%s: đường dẫn không tồn tại: %s" % (where, target))

    # anchor nội bộ
    anchors = set(re.findall(r"<a\s+name=\"([^\"]+)\"", text))
    for h in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.M):
        slug = h.strip().lower()
        slug = re.sub(r"[^\w\s\u00c0-\u1ef9-]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        anchors.add(slug)
    for m in re.finditer(r"\]\(#([^)\s]+)\)|href=\"#([^\"]+)\"", text):
        name = m.group(1) or m.group(2)
        if name and name not in anchors:
            line = text[:m.start()].count("\n") + 1
            err("%s:%d anchor #%s không tồn tại" % (rel(path), line, name))


# --------------------------------------------------------------- 4. YAML
def check_workflows():
    """Đọc từng workflow bằng PyYAML (nếu có) và kiểm cấu trúc cơ bản.

    Không có PyYAML thì chỉ kiểm ở mức văn bản — vẫn bắt được cron sai và
    action thiếu phiên bản, hai thứ hay hỏng nhất.
    """
    paths = sorted(glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml"))
                   + glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yaml")))
    try:
        import yaml
        have_yaml = True
    except Exception:
        have_yaml = False
        warn("Không có PyYAML — chỉ kiểm tra workflow ở mức văn bản")
    for path in paths:
        checked["yml"] += 1
        raw = read(path)
        check_text_encoding(path, raw)
        if not have_yaml:
            for key in ("name:", "on:", "jobs:", "runs-on:"):
                if key not in raw:
                    err("%s: thiếu '%s'" % (rel(path), key))
            for cron in re.findall(r"cron:\s*\"([^\"]+)\"", raw):
                if len(cron.split()) != 5:
                    err("%s: cron sai định dạng: %s" % (rel(path), cron))
            continue
        try:
            doc = yaml.safe_load(raw)
        except Exception as e:
            err("%s: YAML không parse được — %s" % (rel(path), e))
            continue
        if not isinstance(doc, dict):
            err("%s: nội dung YAML không phải mapping" % rel(path))
            continue
        if "name" not in doc:
            err("%s: thiếu 'name'" % rel(path))
        on = doc.get("on", doc.get(True))
        if not on:
            err("%s: thiếu 'on'" % rel(path))
        else:
            sched = on.get("schedule") if isinstance(on, dict) else None
            if sched:
                for item in sched:
                    cron = (item or {}).get("cron", "")
                    if len(str(cron).split()) != 5:
                        err("%s: cron sai định dạng: %s" % (rel(path), cron))
        jobs = doc.get("jobs") or {}
        if not jobs:
            err("%s: không có job nào" % rel(path))
        for jname, job in (jobs or {}).items():
            if not isinstance(job, dict):
                err("%s: job '%s' không hợp lệ" % (rel(path), jname))
                continue
            if "runs-on" not in job and "uses" not in job:
                err("%s: job '%s' thiếu 'runs-on'" % (rel(path), jname))
        # mọi action dùng chung đều phải có @version
        for m in re.finditer(r"uses:\s*([^\s#]+)", raw):
            ref = m.group(1)
            if "@" not in ref or ref.endswith("@"):
                err("%s: action thiếu phiên bản: %s" % (rel(path), ref))


# ------------------------------------- 3b. Quy ước an toàn cho workflow
def check_workflow_hygiene(root=None):
    """Ba thứ tối thiểu để một workflow tự commit không gây hoạ.

    1. `permissions:` — không khai là mặc định rộng, dễ fail ở bước push.
    2. `concurrency:` — hai lượt chồng nhau cùng push là cách nhanh nhất
       để sinh conflict.
    3. `timeout-minutes` cho **mỗi job** — thiếu thì một job treo sẽ chạy
       tới 6 tiếng (mặc định của GitHub).
    4. Workflow có `git push` phải có cổng chặn bot, nếu không nó sẽ
       kích hoạt chính nó qua sự kiện push.
    """
    root = root or ROOT
    folder = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith((".yml", ".yaml")):
            continue
        path = os.path.join(folder, name)
        text = read(path)
        where = rel(path)
        if "permissions:" not in text:
            err("%s: thiếu 'permissions:'" % where)
        if "cron:" in text and "concurrency:" not in text:
            err("%s: có lịch chạy nhưng thiếu 'concurrency:'" % where)
        runners = len(re.findall(r"^\s+runs-on:", text, flags=re.M))
        timeouts = len(re.findall(r"^\s+timeout-minutes:", text, flags=re.M))
        if runners and timeouts < runners:
            err("%s: %d job nhưng chỉ %d 'timeout-minutes'"
                % (where, runners, timeouts))
        if "git push" in text and "github-actions[bot]" not in text:
            err("%s: có 'git push' mà thiếu cổng chặn bot (vòng lặp vô hạn)" % where)


# ---------------------------------------- 4a. Tài liệu phải khớp lịch chạy
CRON_FIELD_OK = re.compile(r"^[0-9*/,\-]+$")


def looks_like_cron(text):
    fields = text.split()
    return (len(fields) == 5
            and all(CRON_FIELD_OK.match(f) for f in fields))


def real_crons(root=None):
    """{tên_file.yml: [cron, ...]} đọc từ .github/workflows/."""
    root = root or ROOT
    folder = os.path.join(root, ".github", "workflows")
    found = {}
    if not os.path.isdir(folder):
        return found
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith((".yml", ".yaml")):
            continue
        with io.open(os.path.join(folder, name), encoding="utf-8") as handle:
            found[name] = re.findall(r"cron:\s*[\"']([^\"']+)[\"']", handle.read())
    return found


def check_workflow_docs(root=None):
    """Bảng lịch chạy trong tài liệu phải khớp cron thật trong workflow.

    Vì sao cần: đổi `*/5` thành `*/30` trong YAML mà quên sửa bảng là tài
    liệu nói dối. Chuyện này đã xảy ra hai lần, nên giờ để máy bắt.
    """
    root = root or ROOT
    crons = real_crons(root)
    if not crons:
        return
    everything = {c for values in crons.values() for c in values}

    doc = os.path.join(root, "docs", "WORKFLOWS.md")
    if os.path.exists(doc):
        for number, line in enumerate(read(doc).split("\n"), 1):
            files = re.findall(r"`([\w.\-]+\.ya?ml)`", line)
            if not files:
                continue
            for name in files:
                if name not in crons:
                    err("docs/WORKFLOWS.md:%d nhắc workflow không tồn tại: %s"
                        % (number, name))
                    continue
                for quoted in re.findall(r"`([^`]+)`", line):
                    if not looks_like_cron(quoted):
                        continue
                    if quoted not in crons[name]:
                        err("docs/WORKFLOWS.md:%d ghi lịch %r cho %s, nhưng file "
                            "thật là %s" % (number, quoted, name,
                                            ", ".join(crons[name]) or "không có schedule"))
        # Chiều ngược lại: workflow mới thêm mà không có dòng nào trong bảng
        # thì người đọc không bao giờ biết nó tồn tại.
        doc_text = read(doc)
        for name in sorted(crons):
            if "`%s`" % name not in doc_text:
                err("docs/WORKFLOWS.md: không có dòng nào cho %s" % name)

    readme = os.path.join(root, "README.md")
    if os.path.exists(readme):
        for number, line in enumerate(read(readme).split("\n"), 1):
            for quoted in re.findall(r"<code>([^<]+)</code>", line):
                if looks_like_cron(quoted) and quoted not in everything:
                    err("README.md:%d có lịch %r mà không workflow nào dùng"
                        % (number, quoted))


# ------------------------------------------------------- 4b. Ảnh & link nội bộ
LOCAL_REF = re.compile(r'(?:src|href)\s*=\s*"(\.[^"]+)"|\]\((\.[^)\s]+)\)')


def check_asset_refs():
    """Mọi tham chiếu ./... trong Markdown phải trỏ tới file có thật.

    Bắt đúng loại lỗi hay gặp nhất: đổi tên ảnh trong assets/ mà quên
    sửa README -> trang hiện biểu tượng ảnh vỡ.
    """
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".venv")]
        for name in sorted(files):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(base, name)
            for match in LOCAL_REF.finditer(read(path)):
                ref = match.group(1) or match.group(2)
                ref = ref.split("#", 1)[0].split("?", 1)[0]
                if not ref or ref.startswith("./#"):
                    continue
                target = os.path.normpath(os.path.join(base, ref))
                if not os.path.exists(target):
                    err("%s: trỏ tới file không tồn tại: %s" % (rel(path), ref))


def check_dead_assets(root=None):
    """Mọi ảnh trong assets/ phải được nhắc tới ở đâu đó.

    Ảnh không ai nhúng là ảnh đã chết: nó vẫn được workflow vẽ lại mỗi
    ngày, vẫn nằm trong lịch sử git, nhưng không xuất hiện ở đâu cả.
    Hoặc là xoá nó, hoặc là nhúng nó — không có lựa chọn thứ ba.
    """
    root = root or ROOT
    folder = os.path.join(root, "assets")
    if not os.path.isdir(folder):
        return
    names = sorted(n for n in os.listdir(folder) if n.lower().endswith(".svg"))
    corpus = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".venv")]
        for name in files:
            if name.lower().endswith((".md", ".yml", ".yaml", ".py")):
                corpus.append(read(os.path.join(base, name)))
    blob = "\n".join(corpus)
    for name in names:
        if name not in blob:
            err("assets/%s không được nhúng ở đâu (ảnh chết)" % name)


# ------------------------------------------------------- 4a2. Ngân sách ảnh
SVG_BUDGET = 40 * 1024          # 40 KB: một ảnh README không nên nặng hơn


def check_svg_budget(root=None, limit=SVG_BUDGET):
    """Mỗi ảnh SVG phải nằm dưới ngân sách bề rộng.

    Chỉ áp cho `assets/` — ảnh do repo này tự vẽ. `profile-3d-contrib/` do
    action bên thứ ba sinh ra (mỗi file ~180 KB, hàng trăm `path`), không
    phải thứ ta kiểm soát.

    Ảnh được tải trên mọi lần mở trang và qua CDN của GitHub. 40 KB là mức
    thoải mái cho một thẻ 640×258 có CSS + SMIL; vượt qua đó thường là dấu
    hiệu ai đó nhúng dữ liệu lớn (base64, path dày đặc) vào file.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        if "/.git/" in path.replace(os.sep, "/"):
            continue
        size = os.path.getsize(path)
        if size > limit:
            err("%s nặng %.1f KB, vượt ngân sách %.0f KB"
                % (rel(path), size / 1024.0, limit / 1024.0))


# --------------------------------------------------------- 4b0. README ngắn
README_BUDGET = 360            # dòng: đủ để giới thiệu, không đủ để lan man


def check_readme_length(root=None, limit=README_BUDGET):
    """README không được dài quá ngân sách dòng đã đặt.

    Trang cá nhân là thứ người lạ mở 20 giây rồi đóng. README dài quá 360
    dòng là dấu hiệu nội dung đã tràn ra khỏi phần giới thiệu và nên
    chuyển vào `docs/`.
    """
    root = root or ROOT
    path = os.path.join(root, "README.md")
    if not os.path.exists(path):
        return
    # splitlines: `split("\n")` đếm thêm một dòng rỗng do newline cuối,
    # khiến README đúng 360 dòng bị báo là 361.
    lines = len(read(path).splitlines())
    if lines > limit:
        err("README.md dài %d dòng, vượt ngân sách %d — chuyển bớt vào docs/"
            % (lines, limit))


# ---------------------------------------------------- 4b1. Tài liệu mồ côi
MD_LINK = re.compile(r"\]\(([^)\s]+)")


def markdown_files(root=None):
    root = root or ROOT
    found = []
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if name.lower().endswith(".md"):
                found.append(os.path.join(base, name))
    return found


def check_orphan_docs(root=None):
    """Bài trong docs/ phải được nhắc tới từ một bài khác.

    Tài liệu không ai dẫn tới thì coi như không tồn tại: người mới sẽ không
    bao giờ đọc `docs/ARCHITECTURE.md` nếu README không có link. README và
    CHANGELOG được miễn — chúng là cửa vào và nhật ký, không phải bài con.
    """
    root = root or ROOT
    files = markdown_files(root)
    if not files:
        return
    corpus = "\n".join(read(path) for path in files)
    exempt = ("README.md", "CHANGELOG.md")
    docs_dir = os.path.join(root, "docs")
    for path in files:
        if os.path.dirname(path) != docs_dir:
            continue
        name = os.path.basename(path)
        if name in exempt:
            continue
        if name not in corpus.replace(os.sep, "/"):
            err("docs/%s không được bài nào dẫn tới (tài liệu mồ côi)" % name)


# ------------------------------------------------- 4b2. Số test trong tài liệu
RE_TEST_CLAIM = re.compile(r"hơn (\d+) unit test")
TEST_DEF = re.compile(r"^\s+def test_", flags=re.M)


def real_test_count(root=None):
    """Đếm test bằng cách đọc file — không import, không chạy gì."""
    root = root or ROOT
    total = 0
    for path in sorted(glob.glob(os.path.join(root, "scripts", "tests", "test_*.py"))):
        total += len(TEST_DEF.findall(read(path)))
    return total


def check_test_claims(root=None):
    """Câu "hơn N unit test" phải còn đúng.

    Tài liệu ghi "hơn 100" từ lúc bộ test còn 100 bài; giờ có hơn 320 mà
    câu đó vẫn nằm đó. Người đọc không kiểm được, còn máy thì kiểm được.
    Điều kiện: N <= số thật < N + 100 (đủ rộng để không phải sửa mỗi lần
    thêm một test, đủ chặt để không nói dối quá một phần ba).
    """
    root = root or ROOT
    total = real_test_count(root)
    if not total:
        return
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(base, name)
            for number, line in enumerate(read(path).split("\n"), 1):
                for claimed in RE_TEST_CLAIM.findall(line):
                    claimed = int(claimed)
                    if claimed > total:
                        err("%s:%d ghi 'hơn %d unit test' nhưng chỉ có %d"
                            % (rel(path), number, claimed, total))
                    elif total >= claimed + 100:
                        err("%s:%d ghi 'hơn %d unit test', con số thật đã là %d "
                            "— hãy nâng lên" % (rel(path), number, claimed, total))


# -------------------------------- 4bj. lớp CSS dùng trong ảnh phải có khai báo
RE_CLASS_ATTR = re.compile(r'\bclass="([^"]+)"')
RE_CLASS_RULE = re.compile(r"\.([A-Za-z][\w-]*)")


def check_class_references(root=None):
    """Mọi lớp dùng trong ảnh phải có luật CSS trong chính ảnh đó.

    `class="pulse-typo"` không làm SVG hỏng — nó chỉ đơn giản là không chuyển
    động. Không có gì báo, và mắt người khó phân biệt "ảnh tĩnh" với "ảnh
    thiếu hoạt ảnh" nếu nhìn trong một giây.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        text = read(path)
        # Chỉ soi trong khối <style>: dấu chấm trong phần thân là toạ độ.
        style = RE_STYLE.findall(text)
        defined = set(RE_CLASS_RULE.findall("\n".join(style)))
        for attribute in RE_CLASS_ATTR.findall(text):
            names = attribute.split()
            # `smilOnly` đánh dấu phần tử chỉ được SMIL điều khiển (CSS tắt
            # hẳn), nên lớp đi kèm không cần luật CSS.
            if "smilOnly" in names:
                continue
            for name in names:
                if name in ("fSans", "fMono"):
                    continue
                if name not in defined:
                    err("%s: lớp %r không có luật CSS — hoạt ảnh sẽ im lặng "
                        "không chạy" % (rel(path), name))


RE_STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)

# ------------------------ 4bm. Keyframe khai báo và keyframe được dùng
RE_KEYFRAMES_DEF = re.compile(r"@keyframes\s+([A-Za-z][\w-]*)")
# `animation: none` và các từ khoá chung không phải tên keyframe.
NON_KEYFRAME_WORDS = {"none", "inherit", "initial", "unset", "revert",
                      "ease", "ease-in", "ease-out", "ease-in-out", "linear",
                      "alternate", "reverse", "infinite", "both", "forwards",
                      "backwards", "running", "paused", "normal", "steps"}
RE_ANIMATION_USE = re.compile(r"animation(?:-name)?\s*:\s*([A-Za-z][\w-]*)")


def check_keyframes(root=None):
    """Keyframe phải có đôi: khai báo thì phải dùng, dùng thì phải khai báo.

    `animation: pulsee 2s` không báo lỗi; phần tử chỉ đứng im. Ngược lại, một
    `@keyframes` không ai dùng là vài trăm byte chết trong mỗi ảnh — nhân lên
    tám ảnh thì thành vài KB.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        text = read(path)
        style = "\n".join(RE_STYLE.findall(text))
        defined = set(RE_KEYFRAMES_DEF.findall(style))
        used = set(RE_ANIMATION_USE.findall(style)) - NON_KEYFRAME_WORDS
        for name in sorted(used - defined):
            err("%s: animation dùng %r nhưng không có @keyframes tương ứng"
                % (rel(path), name))
        for name in sorted(defined - used):
            err("%s: @keyframes %r không được dùng ở đâu" % (rel(path), name))


# ------------------------------ 4bl. url(#id) phải trỏ tới một định nghĩa
PAINT_TAGS = ("linearGradient", "radialGradient", "filter", "clipPath",
              "mask", "pattern", "symbol", "marker")
RE_URL_REF = re.compile(r"url\(#([^)]+)\)")


def check_url_targets(root=None):
    """Mỗi `url(#x)` phải trỏ tới gradient / filter / clipPath / mask / pattern.

    `filter="url(#gloww)"` không làm ảnh hỏng: trình duyệt bỏ qua thuộc tính
    và vẽ nét sắc lẹm thay vì nét phát sáng. Không có thông báo nào — chỉ có
    một chỗ trông hơi khác với ý định.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        text = read(path)
        kinds = {}
        for tag in PAINT_TAGS:
            for ident in re.findall(r'<%s\b[^>]*\bid="([^"]+)"' % tag, text):
                kinds[ident] = tag
        for ident in sorted(set(RE_URL_REF.findall(text))):
            if ident not in kinds:
                err("%s: url(#%s) không trỏ tới định nghĩa nào (chỉ nhận %s)"
                    % (rel(path), ident, ", ".join(PAINT_TAGS)))


# ---------------------------------- 4bk. Không có NaN / None trong thuộc tính
RE_BAD_NUMBER = re.compile(
    # NaN / None trong giá trị thuộc tính, hoặc số mũ kiểu 1.5e-07 ngay sau
    # một lệnh path / dấu cách / dấu phẩy (mã màu #1E90FF không bị bắt).
    r'(="[^"]*(?:NaN|None)[^"]*"|'
    r'(?:[\s,MLHVCSQTAZmlhvcsqtaz])-?\d+(?:\.\d+)?[eE][+-]?\d+)')


def check_bad_numbers(root=None):
    """Toạ độ trong ảnh không được là NaN, None hay số mũ.

    Một phép chia cho 0 hay một `None` lọt vào f-string sẽ tạo `d="MNaN 12"`:
    SVG hợp lệ về cú pháp XML, trình duyệt bỏ qua cả phần tử, và ảnh chỉ mất
    một nét — không có lỗi nào để lần theo.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        for number, line in enumerate(read(path).split("\n"), 1):
            # Bỏ chú thích (dấu dữ liệu hex cũng giống số mũ) và mã màu
            # (#0EA5E9 cũng vậy) trước khi soi, để không bắt oan.
            cleaned = re.sub(r"<!--.*?-->", "", line)
            cleaned = re.sub(r"#[0-9A-Fa-f]{3,8}", "#hex", cleaned)
            for match in RE_BAD_NUMBER.findall(cleaned):
                err("%s:%d có số không hợp lệ trong thuộc tính: %s"
                    % (rel(path), number, match.strip()))


# ---------------------------- 4bj2. Không còn nhãn "lớp 7" ở đâu
RE_GRADE_CLAIM = re.compile(r"(?:lớp|lop|grade|class)[\s-]*7\b", re.I)
GRADE_EXEMPT = {"scripts/check_repo.py", "scripts/tests/test_check_repo.py"}


def check_no_grade_claim(root=None):
    """Không file nào được nhắc "lớp 7" / "grade 7".

    Nhãn này từng nằm trên ảnh bìa, trong README, badge shields và cả câu
    giới thiệu — bốn chỗ, bốn kiểu viết. Đổi ý một lần là phải sửa cả bốn,
    nên nó cần một luật thay vì trí nhớ.
    """
    root = root or ROOT
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith((".md", ".py", ".yml", ".yaml", ".svg")):
                continue
            path = os.path.join(base, name)
            if rel(path) in GRADE_EXEMPT:
                continue
            for number, line in enumerate(read(path).split("\n"), 1):
                found = RE_GRADE_CLAIM.search(line)
                if found:
                    err("%s:%d còn nhắc tới lớp học (%r)"
                        % (rel(path), number, found.group(0)))


# ------------------------------------------- 4bi. id trùng trong một ảnh
RE_SVG_ID = re.compile(r'\bid="([^"]+)"')


def check_duplicate_ids(root=None):
    """Một file SVG không được có hai phần tử cùng `id`.

    Trình duyệt không báo gì: `url(#halo)` chỉ trỏ tới phần tử ĐẦU TIÊN, còn
    phần tử thứ hai lặng lẽ mất hiệu ứng. Lỗi chỉ hiện ra khi ai đó soi ảnh
    bằng trình vẽ khắt khe hơn, hoặc khi màu hiển thị khác dự kiến.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        seen = set()
        for ident in RE_SVG_ID.findall(read(path)):
            if ident in seen:
                err("%s: id %r xuất hiện hai lần" % (rel(path), ident))
            seen.add(ident)


# -------------------------------------------- 4bh. Không dùng 'font' viết tắt
RE_FONT_SHORTHAND = re.compile(r"\bfont:\s*\d")


def check_font_shorthand(root=None):
    """CSS trong ảnh không được dùng thuộc tính viết tắt `font:`.

    `font: 800 54px Arial` là cú pháp hợp lệ, nhưng một số trình vẽ SVG
    (resvg, vài bản librsvg, trình xem ảnh desktop) bỏ qua cả khai báo —
    chữ rơi về 16px mặc định. Cùng một file vì thế hiện hai kiểu khác
    nhau: trình duyệt đẹp, mọi nơi khác vỡ bố cục.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        for number, line in enumerate(read(path).split("\n"), 1):
            if RE_FONT_SHORTHAND.search(line):
                err("%s:%d dùng 'font:' viết tắt — hãy viết "
                    "font-weight/font-size/font-family" % (rel(path), number))


# ------------------------------------------------- 4bc. Ví dụ Python phải chạy
RE_FENCE = re.compile(r"^(\s*)```(\w*)\s*$(.*?)^\1```\s*$", re.M | re.S)


def check_python_fences(root=None):
    """Khối ```python trong tài liệu phải biên dịch được.

    Ví dụ trong tài liệu là thứ người mới copy nguyên si. Một dấu hai chấm
    thiếu hay thụt lề lệch ở đó không làm test nào đỏ, nhưng làm người copy
    mất mười phút đầu tiên — đúng mười phút mà ví dụ sinh ra để tiết kiệm.
    Khối có `>>>` là phiên làm việc, không phải module, nên được bỏ qua.
    """
    root = root or ROOT
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(base, name)
            text = read(path)
            for match in RE_FENCE.finditer(text):
                if match.group(2) not in ("python", "py"):
                    continue
                code = match.group(3)
                if code.startswith("\n"):
                    code = code[1:]
                if ">>>" in code:
                    continue
                line = text.count("\n", 0, match.start()) + 2
                try:
                    compile(code, str(path), "exec")
                except SyntaxError as exc:
                    err("%s:%d ví dụ Python không biên dịch được: %s"
                        % (rel(path), line + (exc.lineno or 1) - 1, exc.msg))


# ------------------------------------------------ 4bb. Mỗi file test có mục riêng
def check_test_file_docs(root=None):
    """Mỗi `scripts/tests/test_*.py` phải được kể tên trong docs/TESTING.md.

    Không phải chuyện hình thức: danh sách file test trong tài liệu là bản đồ
    duy nhất để người mới biết "test cái này nằm ở đâu". Một file test không
    có tên trong đó thì lần sau muốn thêm ca cho nó, người ta sẽ tạo thêm một
    file thứ hai — rồi hai chỗ cùng test một thứ.
    """
    root = root or ROOT
    folder = os.path.join(root, "scripts", "tests")
    doc = os.path.join(root, "docs", "TESTING.md")
    if not os.path.isdir(folder) or not os.path.exists(doc):
        return
    text = read(doc)
    for name in sorted(os.listdir(folder)):
        if not name.startswith("test_") or not name.endswith(".py"):
            continue
        if name not in text:
            err("docs/TESTING.md không nhắc tới %s (file test không có mục "
                "riêng trong bản đồ)" % name)


# ------------------------------------------------- 4be. Nhịp hoạt ảnh an toàn
RE_CSS_BLOCK = re.compile(r"\{([^{}]*)\}")
RE_ANIM_DECL = re.compile(r"animation(?:-duration)?\s*:\s*([^;}]*)")
RE_SECONDS = re.compile(r"(\d*\.?\d+)s\b")
ANIM_FLOOR = 1.0


def check_animation_pace(root=None, floor=ANIM_FLOOR):
    """Hoạt ảnh lặp vô hạn không được nhanh hơn một chu kỳ mỗi giây.

    WCAG 2.3.1 đặt ngưỡng an toàn ở ba lần nháy mỗi giây; một chu kỳ mỗi
    giây là biên rộng gấp ba, đủ để không ai phải nheo mắt. Chu kỳ dài (kim
    đồng hồ quay một vòng mỗi giờ) thì không sao — luật chỉ chặn phía nhanh.

    Đọc theo từng khối khai báo chứ không theo từng dòng: `animation-duration`
    và `animation-iteration-count: infinite` viết tách hai dòng vẫn là một
    hoạt ảnh lặp, và cách viết tách dòng là cách dễ lọt lưới nhất.
    """
    root = root or ROOT
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(".svg"):
                continue
            path = os.path.join(base, name)
            text = read(path)
            for match in RE_CSS_BLOCK.finditer(text):
                body = match.group(1)
                if "infinite" not in body:
                    continue
                line = text.count("\n", 0, match.start()) + 1
                for decl in RE_ANIM_DECL.findall(body):
                    for raw in RE_SECONDS.findall(decl):
                        if float(raw) < floor:
                            err("%s:%d hoạt ảnh lặp %ss quá nhanh "
                                "(tối thiểu %gs)" % (rel(path), line,
                                                     raw, floor))


# -------------------------------------------------- 4bd. Nhịp hoạt ảnh SMIL
RE_SMIL_DUR = re.compile(r'dur="(\d*\.?\d+)(m?s)"')
RE_SMIL_LOOP = re.compile(r'repeatCount="indefinite"')


def check_smil_pace(root=None, floor=ANIM_FLOOR):
    """Cùng ngưỡng với CSS, áp cho hoạt ảnh SMIL (`<animate>`).

    SMIL được dùng ở những chỗ cần chạy cả khi trình xem không hiểu CSS, nên
    nó có đường đi riêng và cũng cần luật riêng — sửa CSS không chạm tới nó.
    `dur` tính bằng mili giây được quy đổi trước khi so.
    """
    root = root or ROOT
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(".svg"):
                continue
            path = os.path.join(base, name)
            for number, line in enumerate(read(path).split("\n"), 1):
                if not RE_SMIL_LOOP.search(line):
                    continue
                for raw, unit in RE_SMIL_DUR.findall(line):
                    seconds = float(raw) / (1000.0 if unit == "ms" else 1.0)
                    if seconds < floor:
                        err("%s:%d SMIL lặp %s%s quá nhanh (tối thiểu %gs)"
                            % (rel(path), number, raw, unit, floor))


# ---------------------------------------------------- 4bf. Không dùng emoji
# Khoảng mã của emoji (pictograph) và ký hiệu một-màu. Dấu tick `✓` và dấu
# chéo `✗` cố tình nằm ngoài: chúng là ký tự đánh dấu trong output terminal,
# rộng một ô, không phải hình vẽ.
RE_EMOJI = re.compile("[\u2300-\u23ff\U0001F000-\U0001FAFF"
                      "\u2600-\u27bf\u2b00-\u2bff\ufe0f]")
EMOJI_ALLOWED = {"\u2713", "\u2717"}
EMOJI_SUFFIXES = (".md", ".py", ".yml", ".yaml", ".svg", ".json", ".txt")


def check_no_emoji(root=None):
    """Repo không dùng emoji — kể cả trong tiêu đề, bảng và thông báo.

    Emoji phụ thuộc font của máy đọc: máy không có font màu hiện ô vuông,
    máy có thì hiện hình to gấp đôi chữ, nên cùng một README cao thấp khác
    nhau. Trình đọc màn hình còn đọc tên chúng thành lời ("mầm cây", "bắt
    tay") giữa câu. Chữ thuần thì mọi nơi giống nhau.
    """
    root = root or ROOT
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(EMOJI_SUFFIXES):
                continue
            path = os.path.join(base, name)
            for number, line in enumerate(read(path).split("\n"), 1):
                found = [ch for ch in RE_EMOJI.findall(line)
                         if ch not in EMOJI_ALLOWED]
                if found:
                    err("%s:%d có emoji %s — dùng chữ thuần"
                        % (rel(path), number,
                           " ".join("U+%04X" % ord(ch) for ch in found)))


# ------------------------------------------------- 4bg. Tài liệu mở bằng tiêu đề
def check_doc_titles(root=None):
    """Mỗi tài liệu phải mở bằng một tiêu đề cấp 1.

    GitHub lấy dòng đầu làm mô tả khi chia sẻ link; không có tiêu đề thì nó
    lấy dòng đầu tiên bất kỳ — thường là một câu giữa đoạn. README được
    miễn vì nó mở bằng khối `<div>` căn giữa.
    """
    root = root or ROOT
    folder = os.path.join(root, "docs")
    if not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith(".md"):
            continue
        path = os.path.join(folder, name)
        for line in read(path).split("\n"):
            if not line.strip():
                continue
            if not line.startswith("# "):
                err("docs/%s phải mở bằng một tiêu đề '# '" % name)
            break


# --------------------------------------------------- 4bf. Ảnh không gọi ra ngoài
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
RE_URL_IN_SVG = re.compile(r"https?://[^\"'\s)]+")
UNSAFE_SVG = ("<script", "javascript:", "onload=", "onclick=", "onerror=")


def check_svg_safety(root=None):
    """Ảnh tự vẽ không được gọi tài nguyên ngoài, không mang mã chạy.

    Một ảnh README tải từ CDN của GitHub; mọi URL bên trong nó là một lần
    gọi mạng của người xem (và là một chỗ có thể chết). `<script>` và
    thuộc tính `on*` thì GitHub đã lọc — nhưng nếu file được xem ở nơi
    khác thì không. Cả hai đều không có lý do tồn tại trong ảnh này.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        text = read(path)
        for url in RE_URL_IN_SVG.findall(text):
            if url.rstrip("/") != SVG_NAMESPACE:
                err("%s gọi ra ngoài: %s" % (rel(path), url))
        for marker in UNSAFE_SVG:
            if marker.lower() in text.lower():
                err("%s chứa %r — ảnh tự vẽ không cần mã chạy"
                    % (rel(path), marker))


# --------------------------------------------------- 4be. Bảng Markdown thẳng cột
RE_TABLE_DIVIDER = re.compile(r"^\|?[\s:|-]+\|[\s:|-]*$")


def check_markdown_tables(root=None):
    """Mọi dòng trong một bảng phải cùng số cột.

    Một dòng thiếu dấu `|` làm cả bảng lệch: ô cuối trôi sang cột khác và
    trên GitHub trông như bảng bị "gãy". Markdown không coi đó là lỗi cú
    pháp, nên không có gì báo.
    """
    root = root or ROOT
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(base, name)
            lines = read(path).split("\n")
            index = 0
            while index + 1 < len(lines):
                head, divider = lines[index], lines[index + 1]
                if not head.startswith("|") or not RE_TABLE_DIVIDER.match(divider):
                    index += 1
                    continue
                columns = head.count("|")
                row = index + 2
                while row < len(lines) and lines[row].startswith("|"):
                    if lines[row].count("|") != columns:
                        err("%s:%d bảng có %d cột nhưng dòng này có %d"
                            % (rel(path), row + 1, columns, lines[row].count("|")))
                    row += 1
                index = row


# ------------------------------------------------- 4bd. Dấu vết của dữ liệu hỏng
PY_ARTIFACTS = ("None", "NaN", "Traceback", "KeyError")


def check_svg_artifacts(root=None):
    """Ảnh đã commit không được chứa dấu vết rác của Python.

    Khi một khoá thiếu, f-string in ra chữ `None` ngay giữa thẻ; khi chia
    cho 0, nó in `NaN` hoặc `inf`. Trình duyệt vẽ những thứ đó như chữ bình
    thường, nên ảnh vẫn "trông ổn" cho tới khi có người đọc kỹ.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        text = read(path)
        for token in PY_ARTIFACTS:
            if token in text:
                err("%s chứa dấu vết dữ liệu hỏng: %r" % (rel(path), token))
        for bad in ("nan", "inf%"):
            if bad in text:
                err("%s chứa số hỏng: %r" % (rel(path), bad))


# ------------------------------------------------ 4bc. Chữ trong SVG có class
RE_TEXT = re.compile(r"<text\b[^>]*>")
RE_ID = re.compile(r'\bid="([^"]+)"')


def check_svg_text_classes(root=None):
    """Mọi `<text>` phải mang `class`.

    Chữ không có class thừa hưởng font mặc định của trình duyệt — Times
    New Roman 16px đen — nên một nhãn quên class sẽ hiện giữa thẻ như dán
    từ tài liệu khác sang. Không có lỗi nào báo; chỉ mắt thấy.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        for tag in RE_TEXT.findall(read(path)):
            if "class=" not in tag:
                err("%s: thẻ %s thiếu class" % (rel(path), tag[:60]))


def check_svg_duplicate_ids(root=None):
    """Trong một file SVG, `id` phải là duy nhất.

    `url(#id)` chỉ trỏ tới phần tử đầu tiên trùng id. Một gradient khai
    báo hai lần nghĩa là nửa số hình dùng sai màu — và trông vẫn "có vẻ
    đúng" nên rất khó lần ra.
    """
    root = root or ROOT
    for path in sorted(glob.glob(os.path.join(root, "assets", "*.svg"))):
        seen = {}
        for found in RE_ID.findall(read(path)):
            seen[found] = seen.get(found, 0) + 1
        for found, count in sorted(seen.items()):
            if count > 1:
                err("%s: id '%s' xuất hiện %d lần" % (rel(path), found, count))



# -------------------------------------------- 4bb. Mọi job phải có hạn giờ
RE_JOB = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$", re.M)
RE_TIMEOUT = re.compile(r"^\s{4}timeout-minutes:\s*\d+\s*$", re.M)


def check_job_timeouts(root=None):
    """Mỗi job phải khai báo `timeout-minutes`.

    Mặc định của GitHub là **360 phút**. Một bước treo (chờ mạng, chờ khoá)
    sẽ giữ runner suốt 6 tiếng trước khi bị cắt — và không ai nhận được
    thông báo nào. 5 phút là đủ cho mọi job của repo này.
    """
    root = root or ROOT
    folder = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith((".yml", ".yaml")):
            continue
        path = os.path.join(root, ".github", "workflows", name)
        text = read(path)
        if text.startswith("jobs:"):
            block = text.split("jobs:", 1)[1]
        elif "\njobs:" in text:
            block = text.split("\njobs:", 1)[1]
        else:
            continue
        # Khoá job nằm ở đúng hai dấu cách; bước bên trong thì sâu hơn.
        jobs = RE_JOB.findall(block)
        if jobs and len(RE_TIMEOUT.findall(block)) < len(jobs):
            err("%s: %d job nhưng chỉ %d 'timeout-minutes' — mặc định là 360 phút"
                % (rel(path), len(jobs), len(RE_TIMEOUT.findall(block))))


# ------------------------------------------------- 4ba. Cấp tiêu đề Markdown
RE_HEADING = re.compile(r"^(#{1,6})\s+\S", re.M)


def check_heading_levels(root=None):
    """Tiêu đề không được nhảy cấp (## rồi ####).

    Mục lục của GitHub dựng theo cấp tiêu đề; nhảy cấp làm mục lục lệch
    một bậc và không có công cụ nào báo. Đây là lỗi chỉ mắt người thấy, và
    chỉ thấy khi cuộn đúng chỗ đó.
    """
    root = root or ROOT
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(base, name)
            previous = 0
            in_code = False
            for number, line in enumerate(read(path).split("\n"), 1):
                # Bỏ qua khối mã: dòng '#' trong ``` là comment Python, và
                # comment Ruby/Python cấp 1 chen giữa h2/h3 sẽ báo lỗi sai.
                if line.lstrip().startswith("```"):
                    in_code = not in_code
                    continue
                if in_code or not RE_HEADING.match(line):
                    continue
                level = len(line) - len(line.lstrip("#"))
                if previous and level > previous + 1:
                    err("%s:%d tiêu đề nhảy cấp (h%d ngay sau h%d)"
                        % (rel(path), number, level, previous))
                previous = level


# ---------------------------------------------- 4b9. Action phải ghim phiên bản
RE_USES = re.compile(r"^\s*(?:-\s*)?uses:\s*(\S+)\s*$", re.M)
RE_PINNED = re.compile(r"@v\d+(\.\d+)*$|@[0-9a-f]{40}$")


def check_action_pins(root=None):
    """Mọi `uses:` phải ghim phiên bản, không chạy theo nhánh.

    `@main` nghĩa là workflow của bạn hôm nay chạy code khác hôm qua, và
    không ai biết lúc nào nó đổi. Repo đã hứa "ghim phiên bản" trong
    docs/WORKFLOWS.md — luật này giữ lời hứa đó.
    """
    root = root or ROOT
    folder = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith((".yml", ".yaml")):
            continue
        path = os.path.join(folder, name)
        for action in RE_USES.findall(read(path)):
            action = action.strip("'\"")
            if action.startswith("./"):
                continue                      # action tự viết trong repo
            if not RE_PINNED.search(action):
                err("%s: '%s' không ghim phiên bản (dùng @vN hoặc SHA)"
                    % (rel(path), action))


# ------------------------------------------------ 4b8. Nhịp cron hợp lệ
RE_CRON = re.compile(r"^\s*-\s*cron:\s*[\"']([^\"']+)[\"']", re.M)
RE_CRON_STEP = re.compile(r"^\*/(\d+)$")


def _minute_step(field):
    """Bước nhảy của trường phút, hoặc None nếu là 'mỗi phút'."""
    step = RE_CRON_STEP.match(field)
    if step:
        return int(step.group(1))
    if field == "*":
        return 0
    return None


def check_cron_resolution(root=None):
    """Cron phải lịch sự với hạn mức của GitHub.

    GitHub không chạy cron dày hơn 5 phút một lần và cũng không báo lỗi:
    `* * * * *` chỉ đơn giản là chạy mỗi 5 phút trong khi người viết tưởng
    là mỗi phút. Ảnh "cập nhật mỗi phút" nhờ vậy là lời hẹn không bao giờ
    thành hiện thực — phút nhảy trong ảnh là do CSS, không phải do cron.
    """
    root = root or ROOT
    folder = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith((".yml", ".yaml")):
            continue
        path = os.path.join(folder, name)
        for expression in RE_CRON.findall(read(path)):
            fields = expression.split()
            if len(fields) != 5:
                err("%s: cron %r không đủ 5 trường" % (rel(path), expression))
                continue
            step = _minute_step(fields[0])
            if step is not None and step < 5:
                err("%s: cron %r dày hơn 5 phút — GitHub sẽ âm thầm gộp lại"
                    % (rel(path), expression))


# ------------------------ 4b6a. Danh sách workflow trên ảnh phải là thật
def status_workflows(root=None):
    """[(file.yml, tên_ngắn), ...] đọc từ svgkit/status.py."""
    path = os.path.join(root or ROOT, "scripts", "svgkit", "status.py")
    if not os.path.exists(path):
        return []
    block = read(path).split("WORKFLOWS = [", 1)[-1].split("]", 1)[0]
    return re.findall(r'\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', block)


def check_status_workflow_list(root=None):
    """Dải trạng thái chỉ được kể tên workflow có thật.

    `status.WORKFLOWS` là danh sách viết tay. Xoá hay đổi tên một workflow mà
    quên sửa danh sách thì dải sẽ hiện một viên "CHỜ MERGE" mãi mãi — API trả
    404, ảnh vẫn đẹp, chỉ sai.
    """
    root = root or ROOT
    folder = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(folder):
        return
    real = {name for name in os.listdir(folder)
            if name.endswith((".yml", ".yaml"))}
    for filename, short in status_workflows(root):
        if filename not in real:
            err("dải trạng thái liệt kê %r (%s) nhưng file đó không tồn tại"
                % (short, filename))


# ----------------------------------- 4b6b. Hai workflow không chạy cùng phút
def _cron_minutes(field):
    """Tập phút (0-59) mà trường cron phút sẽ nổ. None nếu không hiểu."""
    if not field:
        return None
    minutes = set()
    for part in field.split(","):
        if not part:
            return None
        step = 1
        span = part
        if "/" in part:
            span, _, step_text = part.partition("/")
            if not step_text.isdigit() or int(step_text) < 1:
                return None
            step = int(step_text)
        if span in ("*", ""):
            span = "0-59"
        if "-" in span:
            low, _, high = span.partition("-")
            if not (low.isdigit() and high.isdigit()):
                return None
            low, high = int(low), int(high)
        elif span.isdigit():
            low = high = int(span)
        else:
            return None
        if not 0 <= low <= high <= 59:
            return None
        minutes.update(range(low, high + 1, step))
    return minutes or None


def check_cron_minute_collisions(root=None):
    """Hai workflow lịch không nên nổ đúng cùng một phút.

    Không sai về cú pháp, nhưng cùng phút nghĩa là cùng tranh một lượt
    runner và cùng push lên một nhánh: job sau phải `git pull --rebase` rồi
    đẩy lại, và lần nào cũng có một bên chờ. Lệch phút là sửa miễn phí.
    """
    root = root or ROOT
    folder = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(folder):
        return
    grid = {}
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith((".yml", ".yaml")):
            continue
        for expression in RE_CRON.findall(read(os.path.join(folder, name))):
            fields = expression.split()
            if len(fields) != 5:
                continue
            minutes = _cron_minutes(fields[0])
            if minutes:
                grid.setdefault(name, set()).update(minutes)
    names = sorted(grid)
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            shared = sorted(grid[left] & grid[right])
            if shared:
                warn("%s và %s cùng chạy ở phút %s — lệch phút sẽ tránh "
                     "hai job giành một lượt runner"
                     % (left, right, ", ".join(str(m) for m in shared)))


# ------------------------------------------- 4b7. Badge workflow của shields
SHIELDS_WORKFLOW = ("img.shields.io/github/actions/workflow",
                    "img.shields.io/github/workflow/status")


def check_shields_workflow_badges(root=None):
    """Không dùng badge trạng thái workflow của shields.io.

    shields chỉ đọc được workflow **nằm trên nhánh mặc định**, nên workflow
    mới tạo sẽ hiện ô đỏ "repo or workflow not found" ngay trên trang chủ.
    Repo đã thay bằng `assets/status.svg` tự vẽ — luật này giữ cho nó
    không quay lại.
    """
    for base, dirs, files in os.walk(root or ROOT):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(base, name)
            text = read(path)
            for marker in SHIELDS_WORKFLOW:
                if marker in text:
                    err("%s dùng badge workflow của shields (%s) — hãy dùng "
                        "assets/status.svg" % (rel(path), marker))


# ------------------------------------------- 4b5b. pip cũng phải ghim phiên bản
RE_PIP_INSTALL = re.compile(r"pip\s+install[^\n|]*")
RE_PINNED_PKG = re.compile(r"[A-Za-z0-9_.-]+==\d")


def check_pip_pins(root=None):
    """Lệnh `pip install` trong workflow phải ghim phiên bản.

    Mọi action đã ghim ở một tag; để pip thì mỗi ngày cài một bản khác. Một
    bản PyYAML đổi cách đọc cũng đủ để bộ test workflow chuyển từ "chạy" sang
    "skip" mà không ai biết — bộ test vẫn xanh, chỉ là nó không còn kiểm gì.
    """
    root = root or ROOT
    folder = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith((".yml", ".yaml")):
            continue
        path = os.path.join(folder, name)
        for number, line in enumerate(read(path).split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("#") or "echo " in line:
                continue
            for command in RE_PIP_INSTALL.findall(line):
                if command.strip() == "pip install":
                    continue
                if not RE_PINNED_PKG.search(command):
                    err("%s:%d 'pip install' không ghim phiên bản — hãy "
                        "thêm ==x.y.z" % (rel(path), number))


# --------------------------------------------- 4b6. Workflow phải chạy tay được
def check_workflow_dispatch(root=None):
    """Mọi workflow phải có `workflow_dispatch`.

    Không có nó thì khi ảnh sai, người duy nhất sửa được là người biết
    chờ đúng khung giờ của cron. Một nút "Run workflow" là khác biệt giữa
    "sửa trong 30 giây" và "đợi 3 tiếng".
    """
    root = root or ROOT
    folder = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith((".yml", ".yaml")):
            continue
        path = os.path.join(folder, name)
        if "workflow_dispatch" not in read(path):
            err("%s: thiếu 'workflow_dispatch' (không chạy tay được)" % rel(path))


# ------------------------------------------------------- 4b5. Dấu việc còn treo
RE_TODO = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")


def check_todo_markers(root=None):
    """Không để TODO/FIXME trong code đã merge.

    Ghi chú việc còn treo trong code là cách chắc chắn nhất để nó không bao
    giờ được làm: không ai đọc lại, không công cụ nào nhắc. Việc còn treo
    thuộc về issue, không thuộc về comment.
    """
    root = root or ROOT
    # File này định nghĩa luật nên phải nhắc tới các dấu đó.
    exempt = ("scripts/check_repo.py", "scripts/tests/test_check_repo.py")
    for base, dirs, files in os.walk(os.path.join(root, "scripts")):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            path = os.path.join(base, name)
            if rel(path) in exempt:
                continue
            for number, line in enumerate(read(path).split("\n"), 1):
                if RE_TODO.search(line) and "noqa" not in line:
                    err("%s:%d còn dấu việc treo (%s)"
                        % (rel(path), number, RE_TODO.search(line).group(1)))


# ------------------------------------------------- 4b4. Địa danh đã đổi chỗ
STALE_PLACES = ("Long Xuyên", "Long Xuyen", "An Giang")


def check_stale_places(root=None):
    """Không được còn địa danh cũ trong bất kỳ file nào.

    Chỗ ở đã đổi sang phường Kon Tum, tỉnh Quảng Ngãi. Một chuỗi còn sót
    trong ảnh hero hay trong README là thông tin sai về chính chủ repo —
    loại lỗi người đọc không thể tự phát hiện là đã cũ.
    """
    root = root or ROOT
    # Chính file này và test của nó phải chứa chuỗi cũ để định nghĩa/kiểm
    # tra luật — không tính là vi phạm.
    exempt = ("scripts/check_repo.py", "scripts/tests/test_check_repo.py")
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(TEXT_SUFFIXES):
                continue
            path = os.path.join(base, name)
            if rel(path) in exempt:
                continue
            text = read(path)
            for stale in STALE_PLACES:
                if stale in text:
                    err("%s còn địa danh cũ %r" % (rel(path), stale))


# --------------------------------------------------- 4b3. Dấu merge còn sót
RE_CONFLICT = re.compile(r"^(<{7}|={7}|>{7})(\s|$)", flags=re.M)


def check_conflict_markers(root=None):
    """Không được còn dấu `<<<<<<<` / `=======` / `>>>>>>>` trong file.

    Sau một lần merge có xung đột, dấu này lọt vào file là chuyện thường.
    Markdown thì hiện ra như chữ, Python thì `SyntaxError`, SVG thì XML
    hỏng — nhưng nếu file đó không ai mở lại thì lỗi nằm im rất lâu.
    """
    root = root or ROOT
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(TEXT_SUFFIXES):
                continue
            path = os.path.join(base, name)
            for number, line in enumerate(read(path).split("\n"), 1):
                if RE_CONFLICT.match(line):
                    err("%s:%d còn dấu merge (%s)"
                        % (rel(path), number, line[:7]))
                    break


# --------------------------------------------------- 4c. Tự sửa lỗi vô hình
def fixable_text(text):
    """Chuẩn hoá một file văn bản về dạng sạch, KHÔNG đổi nội dung.

    Chỉ sửa những thứ mà người đọc không thấy nhưng máy thì khó chịu: BOM,
    CRLF, khoảng trắng cuối dòng, dòng trống cuối file, thiếu newline cuối.
    Không bao giờ đụng vào chữ, thứ tự dòng hay ký tự tiếng Việt.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def fix_text_files(root=None):
    """Chạy `fixable_text()` trên mọi file văn bản; trả về danh sách đã sửa."""
    root = root or ROOT
    changed = []
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.lower().endswith(TEXT_SUFFIXES):
                continue
            path = os.path.join(base, name)
            raw = open(path, encoding="utf-8", errors="replace").read()
            clean = fixable_text(raw)
            if clean != raw:
                with open(path, "w", encoding="utf-8", newline="\n") as handle:
                    handle.write(clean)
                changed.append(rel(path))
    return changed


# ------------------------------------------------------ 4d. Docstring đầu file
def check_module_docstrings(root=None):
    """Mọi file Python phải mở đầu bằng docstring.

    Không phải chuyện hình thức: docstring đầu file là thứ duy nhất nói
    *vì sao* module tồn tại. File không có nó thì sáu tháng sau không ai
    dám sửa — kể cả tác giả.
    """
    root = root or ROOT
    for base, dirs, files in os.walk(os.path.join(root, "scripts")):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            path = os.path.join(base, name)
            for line in read(path).split("\n"):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if stripped[0] not in ("\"", "'"):
                    err("%s: thiếu docstring đầu file" % rel(path))
                break


# --------------------------------------------------------------- 5. Python
def check_python():
    """Biên dịch MỌI file .py trong scripts/ (kể cả svgkit/ và tests/)."""
    for base, dirs, files in os.walk(os.path.join(ROOT, "scripts")):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            path = os.path.join(base, name)
            checked["py"] += 1
            src = read(path)
            check_text_encoding(path, src)
            try:
                compile(src, path, "exec")
            except SyntaxError as e:
                err("Python lỗi cú pháp: %s — %s" % (rel(path), e))
        # mỗi gói con phải có __init__.py thì mới import được trên CI
        if base != os.path.join(ROOT, "scripts") and files:
            if "__init__.py" not in files:
                warn("Thư mục %s thiếu __init__.py" % rel(base))


# --------------------------------------------------------------- main

def list_rules():
    """In tên và câu đầu tiên trong docstring của từng luật.

    Danh sách này sinh ra từ chính module, nên không bao giờ cũ: luật mới
    thêm vào là nó hiện ra, luật bị xoá là nó biến mất. `docs/TESTING.md`
    mới là chỗ giải thích *vì sao*; đây là chỗ trả lời "repo tự kiểm gì".
    """
    names = sorted(name for name in globals()
                   if name.startswith("check_") and callable(globals()[name]))
    for name in names:
        doc = (globals()[name].__doc__ or "").strip().split("\n")[0]
        print("  %-26s %s" % (name, doc))
    return names


def main(argv=None):
    # Dọn trạng thái cũ: khi hàm này được gọi từ trong test (hoặc gọi hai lần
    # trong một tiến trình), lỗi của lượt trước còn nằm trong danh sách và
    # làm lượt này báo đỏ vô cớ.
    del errors[:]
    del warnings[:]
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--help" in argv or "-h" in argv:
        print("Dùng: python3 scripts/check_repo.py [--fix]")
        print("  --fix   chuẩn hoá BOM/CRLF/khoảng trắng thay vì chỉ báo lỗi")
        print("  --rules in danh sách luật kèm một dòng giải thích")
        return 0
    if "--rules" in argv:
        names = list_rules()
        print("\n%d luật." % len(names))
        return 0
    if "--fix" in argv:
        fixed = fix_text_files()
        print("Đã sửa %d file." % len(fixed))
        for name in fixed:
            print("  ~ " + name)
    check_svg()
    check_file_hygiene()
    check_workflow_docs()
    check_workflow_hygiene()
    check_workflows()
    check_asset_refs()
    check_dead_assets()
    check_test_claims()
    check_orphan_docs()
    check_readme_length()
    check_conflict_markers()
    check_stale_places()
    check_todo_markers()
    check_workflow_dispatch()
    check_pip_pins()
    check_shields_workflow_badges()
    check_cron_resolution()
    check_cron_minute_collisions()
    check_status_workflow_list()
    check_action_pins()
    check_heading_levels()
    check_job_timeouts()
    check_svg_text_classes()
    check_svg_duplicate_ids()
    check_svg_artifacts()
    check_markdown_tables()
    check_svg_safety()
    check_font_shorthand()
    check_no_grade_claim()
    check_no_emoji()
    check_duplicate_ids()
    check_class_references()
    check_bad_numbers()
    check_url_targets()
    check_keyframes()
    check_animation_pace()
    check_smil_pace()
    check_doc_titles()
    check_python_fences()
    check_test_file_docs()
    check_svg_budget()
    check_svg_viewbox()
    check_python()
    check_module_docstrings()
    # Mọi file Markdown trong repo (README, docs, CONTRIBUTING, mẫu issue...).
    # Dùng os.walk vì glob không đi vào thư mục ẩn như .github/.
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".venv")]
        for name in sorted(files):
            if name.lower().endswith(".md"):
                check_markdown(os.path.join(base, name))
    for name in ("README.md", "docs/WORKFLOWS.md", ".github/CONTRIBUTING.md"):
        if not os.path.exists(os.path.join(ROOT, name)):
            err("Thiếu file tài liệu bắt buộc: %s" % name)

    print("=" * 62)
    print(" KIỂM TRA SỨC KHỎE REPO")
    print("=" * 62)
    print(" Đã kiểm tra: %d SVG · %d Markdown · %d workflow · %d script Python"
          % (checked["svg"], checked["md"], checked["yml"], checked["py"]))
    print("              + %d file văn bản (BOM, CRLF, UTF-8, ký tự lạ)"
          % checked["file"])
    if warnings:
        print("\n CẢNH BÁO (%d)" % len(warnings))
        for w in warnings:
            print("   • " + w)
    if errors:
        print("\n LỖI CẦN SỬA (%d)" % len(errors))
        for e in errors:
            print("   ✗ " + e)
        print("\n KẾT LUẬN: CÓ LỖI")
        return 1
    print("\n KẾT LUẬN: MỌI THỨ ỔN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
