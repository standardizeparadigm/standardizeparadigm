#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n.py — Chữ trên các thẻ, hai thứ tiếng.

Mặc định tiếng Việt (`--lang vi`), có thể đổi sang tiếng Anh (`--lang en`).
Thêm ngôn ngữ mới = thêm một dict cùng bộ khóa; test sẽ báo nếu thiếu khóa.
"""

LANGS = ("vi", "en")
DEFAULT_LANG = "vi"

STRINGS = {
    "vi": {
        # --- thẻ thống kê
        "stats.title": "GITHUB STATS",
        "stats.updated": "CẬP NHẬT {stamp}",
        "stats.stars": "STARS",
        "stats.forks": "FORKS",
        "stats.repos": "REPOS",
        "stats.followers": "FOLLOWERS",
        "stats.following": "FOLLOWING",
        "stats.commits": "COMMITS",
        "stats.rank": "RANK",
        "stats.progress": "{pct}% TIẾN ĐỘ",
        "stats.foot": "Dữ liệu thật từ GitHub API · ảnh nằm trong repo nên không bao giờ rate-limit",
        # --- thẻ ngôn ngữ
        "langs.title": "MOST USED LANGUAGES",
        "langs.sub": "THEO BYTE CODE THẬT",
        "langs.foot": "Tính theo số byte code thật trong các repo công khai · cập nhật {stamp}",
        # --- đồng hồ
        "clock.title": "LIVE CLOCK",
        "clock.sub": "UTC+7 · LÀM MỚI MỖI 5 PHÚT",
        "clock.label": "GIỜ VIỆT NAM · UTC+7",
        "clock.day": "NGÀY HÔM NAY ĐÃ TRÔI",
        "clock.foot": "Cập nhật lúc {hhmm} · tự làm mới mỗi 5 phút bởi GitHub Actions",
        "clock.greet.morning": "Chào buổi sáng",
        "clock.greet.noon": "Chào buổi trưa",
        "clock.greet.afternoon": "Chào buổi chiều",
        "clock.greet.evening": "Chào buổi tối",
        "clock.greet.night": "Đang thức khuya",
        # --- thẻ hoạt động
        "act.title": "CONTRIBUTION ACTIVITY",
        "act.sub": "365 NGÀY · {stamp}",
        "act.total": "CẢ NĂM",
        "act.streak": "CHUỖI HIỆN TẠI",
        "act.best": "CHUỖI DÀI NHẤT",
        "act.days": "ngày",
        "act.range": "14 NGÀY GẦN NHẤT",
        "act.today": "HÔM NAY +{n}",
        "act.foot": "Đếm từ lịch contribution thật của GitHub · cập nhật {stamp}",
        # --- chung
        "wait.title.stats": "GitHub Stats",
        "wait.title.langs": "Most Used Languages",
        "wait.line1": "Chạy workflow “Profile Cards” để tạo thẻ này",
        "wait.line2": "Actions → Profile Cards (LTS) → Run workflow",
        "wait.empty1": "Chưa có dữ liệu",
        "wait.empty2": "Thẻ này sẽ tự điền sau khi workflow chạy lần đầu",
        # --- hero
        "hero.sub": "Học sinh lớp 7 · Lập trình viên tự học · Long Xuyên, An Giang",
        "hero.pill1": "LỚP 7",
        "hero.pill2": "UTC+7",
        "hero.pill3": "TỰ HỌC",
        "hero.pill4": "LONG XUYÊN",
        "hero.status": "đang code",
        "hero.type1": "print(\"Hello World\")",
        "hero.type2": "học một thứ → mở ra mười thứ",
        "hero.type3": "bug hôm nay = bài học ngày mai",
        "hero.hint": "keep learning · keep building · stay curious",
        # --- footer
        "footer.title": "Thanks for visiting!",
        "footer.sub": "Keep learning • Keep building • Keep being curious",
        "footer.made": "Làm bằng Python và rất nhiều lần Ctrl+S",
        "desc.hero": "Ảnh bìa: tên, vai trò và nơi sống của tác giả",
    },
    "en": {
        "stats.title": "GITHUB STATS",
        "stats.updated": "UPDATED {stamp}",
        "stats.stars": "STARS",
        "stats.forks": "FORKS",
        "stats.repos": "REPOS",
        "stats.followers": "FOLLOWERS",
        "stats.following": "FOLLOWING",
        "stats.commits": "COMMITS",
        "stats.rank": "RANK",
        "stats.progress": "{pct}% PROGRESS",
        "stats.foot": "Real data from the GitHub API · images live in the repo, so no rate limits",
        "langs.title": "MOST USED LANGUAGES",
        "langs.sub": "BY REAL CODE BYTES",
        "langs.foot": "Measured by real code bytes across public repos · updated {stamp}",
        "clock.title": "LIVE CLOCK",
        "clock.sub": "UTC+7 · REFRESHED EVERY 5 MIN",
        "clock.label": "VIETNAM TIME · UTC+7",
        "clock.day": "OF TODAY ALREADY GONE",
        "clock.foot": "Updated at {hhmm} · auto-refreshed every 5 minutes by GitHub Actions",
        "clock.greet.morning": "Good morning",
        "clock.greet.noon": "Good noon",
        "clock.greet.afternoon": "Good afternoon",
        "clock.greet.evening": "Good evening",
        "clock.greet.night": "Still awake",
        "act.title": "CONTRIBUTION ACTIVITY",
        "act.sub": "365 DAYS · {stamp}",
        "act.total": "THIS YEAR",
        "act.streak": "CURRENT STREAK",
        "act.best": "LONGEST STREAK",
        "act.days": "days",
        "act.range": "LAST 14 DAYS",
        "act.today": "TODAY +{n}",
        "act.foot": "Counted from the real GitHub contribution calendar · updated {stamp}",
        "wait.title.stats": "GitHub Stats",
        "wait.title.langs": "Most Used Languages",
        "wait.line1": "Run the “Profile Cards” workflow to build this card",
        "wait.line2": "Actions → Profile Cards (LTS) → Run workflow",
        "wait.empty1": "No data yet",
        "wait.empty2": "This card fills itself the first time the workflow runs",
        "hero.sub": "Grade 7 student · self-taught developer · Long Xuyen, An Giang",
        "hero.pill1": "GRADE 7",
        "hero.pill2": "UTC+7",
        "hero.pill3": "SELF-TAUGHT",
        "hero.pill4": "LONG XUYEN",
        "hero.status": "coding now",
        "hero.type1": "print(\"Hello World\")",
        "hero.type2": "learn one thing → unlock ten more",
        "hero.type3": "today's bug = tomorrow's lesson",
        "hero.hint": "keep learning · keep building · stay curious",
        "footer.title": "Thanks for visiting!",
        "footer.sub": "Keep learning • Keep building • Keep being curious",
        "footer.made": "Made with Python and a lot of Ctrl+S",
        "desc.hero": "Cover image: the author's name, role and location",
    },
}


WEEKDAYS = {
    "vi": ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy",
           "Chủ Nhật"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
           "Sunday"],
}


class Translator:
    """Tra cứu chuỗi theo khóa, tự điền tham số, thiếu khóa thì trả khóa."""

    def __init__(self, lang=DEFAULT_LANG):
        self.lang = lang if lang in STRINGS else DEFAULT_LANG
        self.table = STRINGS[DEFAULT_LANG].copy()
        self.table.update(STRINGS[self.lang])

    def weekday(self, index):
        """0 = thứ Hai ... 6 = Chủ Nhật."""
        return WEEKDAYS[self.lang][int(index) % 7]

    def __call__(self, key, **kwargs):
        text = self.table.get(key, key)
        try:
            return text.format(**kwargs) if kwargs else text
        except (KeyError, IndexError, ValueError):
            return text


def get(lang=DEFAULT_LANG):
    return Translator(lang)
