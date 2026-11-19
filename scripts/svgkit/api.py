#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api.py — Nói chuyện với GitHub: REST để lấy số liệu, GraphQL để lấy lịch
contribution.

Điểm quan trọng: mọi lỗi đều được nuốt rồi trả None, để tầng trên giữ
nguyên ảnh cũ chứ không ghi đè bằng dữ liệu rỗng.
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.github.com"
GRAPHQL = "https://api.github.com/graphql"
TZ_VN = timezone(timedelta(hours=7))


def now_vn():
    return datetime.now(TZ_VN)


def to_vn(dt):
    """Quy đổi một mốc thời gian bất kỳ về giờ Việt Nam (UTC+7).

    - `None` -> `None` (tầng trên giữ ảnh cũ)
    - datetime không có tzinfo: coi như **đã là** giờ Việt Nam (giữ nguyên)
    - datetime có tzinfo: quy đổi thật, nên truyền giờ UTC cũng ra đúng giờ VN

    Vì sao cần: GitHub Actions chạy ở UTC. Chỉ cần một chỗ quên quy đổi là
    đồng hồ hiện sai 7 tiếng, mà nhìn ảnh thì không ai đoán ra lỗi ở đâu.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(TZ_VN)


# --------------------------------------------------------------- REST
def request_json(url, token="", payload=None, tries=3, quiet=False):
    """GET (hoặc POST nếu có payload) và trả JSON, lỗi thì None."""
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-cards-lts",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token

    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            body = ""
            try:
                body = " ".join(error.read().decode("utf-8", "replace")[:250].split())
            except Exception:
                pass
            if error.code in (403, 429) and attempt < tries - 1:
                sys.stderr.write("  HTTP %s -> thử lại | %s\n" % (error.code, body))
                time.sleep(5 * (attempt + 1))
                continue
            if not quiet:
                sys.stderr.write("  !! HTTP %s trên %s\n     %s\n"
                                 % (error.code, url, body))
            return None
        except Exception as error:                      # mạng, timeout, JSON hỏng
            if quiet:
                return None
            if attempt < tries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            sys.stderr.write("  Lỗi mạng: %s\n" % error)
            return None
    return None


def api_status(path, token=""):
    """GET một lần, trả (mã_http, json|None).

    Khác api(): ở đây ta cần biết 404 (workflow chưa có trên nhánh mặc
    định) tách khỏi lỗi mạng, nên phải giữ lại mã trạng thái.
    """
    url = path if path.startswith("http") else API + path
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "profile-cards-lts"}
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, None
    except Exception:
        return 0, None


def api(path, token="", tries=3, quiet=False):
    url = path if path.startswith("http") else API + path
    return request_json(url, token=token, tries=tries, quiet=quiet)


# --------------------------------------------------------------- REST data
def collect_user(login, token="", display_name=""):
    """Thu thập số liệu cho thẻ: stars, forks, repos, followers, languages..."""
    print("  tạo thẻ cho user : %s" % login)
    print("  có GITHUB_TOKEN  : %s" % ("có" if token else "KHÔNG CÓ"))

    user = api("/users/" + urllib.parse.quote(login), token)
    if not user:
        sys.stderr.write("  !! không đọc được /users/%s\n" % login)
        return None
    print("  OK /users/%s -> public_repos=%s followers=%s"
          % (login, user.get("public_repos"), user.get("followers")))

    repos = []
    for page in range(1, 6):
        chunk = api("/users/%s/repos?per_page=100&type=owner&sort=pushed&page=%d"
                    % (urllib.parse.quote(login), page), token)
        if not chunk:
            break
        repos.extend(chunk)
        if len(chunk) < 100:
            break

    own = [repo for repo in repos if not repo.get("fork")]
    stars = sum(repo.get("stargazers_count", 0) for repo in own)
    forks = sum(repo.get("forks_count", 0) for repo in own)

    langs = {}
    for repo in own[:40]:
        data = api("/repos/%s/languages" % repo.get("full_name", ""), token)
        if not data:
            continue
        for name, size in data.items():
            langs[name] = langs.get(name, 0) + int(size)
    if not langs:
        for repo in own:
            name = repo.get("language")
            if name:
                langs[name] = langs.get(name, 0) + 1

    commits = None
    search = api("/search/commits?q=author:%s&per_page=1"
                 % urllib.parse.quote(login), token)
    if isinstance(search, dict) and "total_count" in search:
        commits = search["total_count"]

    print("  tổng kết: repos=%d own=%d stars=%d forks=%d langs=%d commits=%s"
          % (len(repos), len(own), stars, forks, len(langs), commits))

    return {
        "login": login,
        "name": display_name or user.get("name") or user.get("login") or login,
        "stars": stars,
        "forks": forks,
        "repos": user.get("public_repos", len(own)),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "commits": commits,
        "langs": langs or {"Python": 1},
    }


# --------------------------------------------------------------- GraphQL
CONTRIBUTION_QUERY = """
query ($login: String!) {
  user(login: $login) {
    contributionsCollection {
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


CONCLUSION_MAP = {
    "success": "passing",
    "failure": "failing",
    "timed_out": "failing",
    "startup_failure": "failing",
    "action_required": "failing",
    "cancelled": "unknown",
    "skipped": "unknown",
    "neutral": "unknown",
    "stale": "unknown",
}


def age_minutes(iso, now=None):
    """Số phút đã trôi qua kể từ mốc ISO-8601 của GitHub ("2026-11-19T09:04:11Z").

    Trả None khi không đọc được chuỗi — thà thiếu nhãn còn hơn in một con
    số sai (ví dụ "0 phút trước" cho một lần chạy từ hôm qua).
    """
    if not iso:
        return None
    try:
        moment = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        return None
    moment = moment.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    minutes = int((now - moment).total_seconds() // 60)
    return max(0, minutes)


def workflow_states(owner, repo, token="", files=None):
    """Trạng thái lần chạy gần nhất của từng workflow.

    Trả về [(tên_ngắn, trạng_thái, số_phút_từ_lần_chạy)] với trạng thái là
    một trong passing / failing / running / none / unknown. Phần tử thứ ba
    là None khi không xác định được — dải trạng thái khi đó bỏ trống nhãn. Không có token hoặc
    workflow chưa tồn tại trên nhánh mặc định -> "none" (chưa chạy),
    chứ không ném lỗi.
    """
    from .status import WORKFLOWS

    wanted = files or WORKFLOWS
    rows = []
    for filename, short in wanted:
        if not token:
            rows.append((short, "unknown", None))
            continue
        code, info = api_status(
            "/repos/%s/%s/actions/workflows/%s/runs?per_page=1&exclude_pull_requests=true"
            % (owner, repo, filename), token)
        if code == 404:
            # workflow chưa nằm trên nhánh mặc định -> đúng lý do shields báo đỏ
            rows.append((short, "missing", None))
            continue
        runs = ((info or {}).get("workflow_runs") or [])
        if code != 200:
            rows.append((short, "unknown", None))
            continue
        if not runs:
            rows.append((short, "none", None))
            continue
        run = runs[0]
        age = age_minutes(run.get("updated_at") or run.get("created_at"))
        if run.get("status") in ("in_progress", "queued", "requested", "waiting"):
            rows.append((short, "running", age))
        else:
            rows.append((short, CONCLUSION_MAP.get(run.get("conclusion"), "unknown"),
                         age))
    return rows


def _streaks(days):
    """Trả về (chuỗi hiện tại, chuỗi dài nhất) tính theo số ngày."""
    longest = current = 0
    run = 0
    for _, count in days:
        if count > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    # chuỗi hiện tại: đếm ngược từ hôm nay
    for _, count in reversed(days):
        if count > 0:
            current += 1
        else:
            break
    return current, longest


def contributions(login, token):
    """Lịch contribution 1 năm. Không có token hoặc lỗi -> None."""
    if not token:
        sys.stderr.write("  (bỏ qua activity) không có GITHUB_TOKEN\n")
        return None
    payload = {"query": CONTRIBUTION_QUERY, "variables": {"login": login}}
    result = request_json(GRAPHQL, token=token, payload=payload)
    if not isinstance(result, dict):
        return None
    if result.get("errors"):
        sys.stderr.write("  !! GraphQL: %s\n" % result["errors"][0].get("message"))
        return None
    try:
        calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        total = int(calendar.get("totalContributions", 0))
        days = []
        for week in calendar.get("weeks", []):
            for day in week.get("contributionDays", []):
                days.append((datetime.strptime(day["date"], "%Y-%m-%d").date(),
                             int(day.get("contributionCount", 0))))
    except (KeyError, TypeError, ValueError) as error:
        sys.stderr.write("  !! GraphQL trả dữ liệu lạ: %s\n" % error)
        return None

    days.sort(key=lambda item: item[0])
    current, longest = _streaks(days)
    print("  activity: %d contributions · chuỗi hiện tại %d · dài nhất %d"
          % (total, current, longest))
    return {
        "total": total,
        "days": days,
        "streak_current": current,
        "streak_longest": longest,
    }
