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


def check_url(url, where):
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
    text = read(path)
    checked["md"] += 1
    check_text_encoding(path, text)
    for m in URL_RE.finditer(text):
        url = m.group(1) or m.group(2) or m.group(3)
        if not url:
            continue
        line = text[:m.start()].count("\n") + 1
        where = "%s:%d" % (rel(path), line)
        check_url(url, where)
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
def main():
    check_svg()
    check_file_hygiene()
    check_workflow_docs()
    check_workflow_hygiene()
    check_workflows()
    check_asset_refs()
    check_python()
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
    print("\n KẾT LUẬN: MỌI THỨ ỔN ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
