#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
palette.py — Bảng màu, theme và xếp hạng.

Mọi màu của bộ SVG đều đi qua đây, nên muốn đổi "da" cho cả bộ chỉ cần
thêm một mục vào THEMES là xong (`--theme <tên>`).
"""

from dataclasses import dataclass

FONT = "'Segoe UI',Inter,Ubuntu,Helvetica,Arial,sans-serif"
MONO = "'Fira Code',Consolas,'SF Mono',monospace"


@dataclass(frozen=True)
class Palette:
    """Một bảng màu hoàn chỉnh cho toàn bộ thẻ."""

    name: str
    bg_top: str
    bg_bot: str
    panel: str
    stroke: str
    title: str
    text: str
    label: str
    dim: str
    accent: str
    accent2: str
    accent3: str
    deep: str
    font: str = FONT
    mono: str = MONO

    # --- các dẫn xuất tiện dụng -------------------------------------
    @property
    def panel_soft(self):
        return self.panel

    def as_tokens(self):
        return {
            "@BGTOP@": self.bg_top,
            "@BGBOT@": self.bg_bot,
            "@PANEL@": self.panel,
            "@STROKE@": self.stroke,
            "@TITLE@": self.title,
            "@TEXT@": self.text,
            "@LABEL@": self.label,
            "@DIM@": self.dim,
            "@ACCENT@": self.accent,
            "@ACCENT2@": self.accent2,
            "@ACCENT3@": self.accent3,
            "@DEEP@": self.deep,
            "@FONT@": self.font,
            "@MONO@": self.mono,
        }


THEMES = {
    "sky": Palette(
        name="sky",
        bg_top="#07111D", bg_bot="#0A1421", panel="#0B1B2B", stroke="#17334F",
        title="#E8F4FF", text="#C6D8EA", label="#8CA4BD", dim="#5C7590",
        accent="#38BDF8", accent2="#0EA5E9", accent3="#7DD3FC", deep="#0369A1",
    ),
    "emerald": Palette(
        name="emerald",
        bg_top="#05130F", bg_bot="#081A16", panel="#0A1F1A", stroke="#1B3F35",
        title="#E6FFF6", text="#C3E4D9", label="#87AFA2", dim="#54786D",
        accent="#34D399", accent2="#10B981", accent3="#6EE7B7", deep="#047857",
    ),
    "violet": Palette(
        name="violet",
        bg_top="#0B0718", bg_bot="#110B22", panel="#150D2A", stroke="#34215A",
        title="#F3EBFF", text="#D6C8EE", label="#A491C4", dim="#6E5C93",
        accent="#A78BFA", accent2="#8B5CF6", accent3="#C4B5FD", deep="#6D28D9",
    ),
    "sunset": Palette(
        name="sunset",
        bg_top="#140A0B", bg_bot="#1B0E10", panel="#221114", stroke="#52262C",
        title="#FFEFE9", text="#F0D3CB", label="#C39A93", dim="#8A625D",
        accent="#FB923C", accent2="#F97316", accent3="#FDBA74", deep="#C2410C",
    ),
    "ocean": Palette(
        name="ocean",
        bg_top="#04121A", bg_bot="#061A24", panel="#08202C", stroke="#12455A",
        title="#E4FAFF", text="#BEE6F2", label="#84AFBF", dim="#527A89",
        accent="#22D3EE", accent2="#06B6D4", accent3="#67E8F9", deep="#0E7490",
    ),
    "mono": Palette(
        name="mono",
        bg_top="#0A0A0A", bg_bot="#101010", panel="#151515", stroke="#2A2A2A",
        title="#F5F5F5", text="#D4D4D4", label="#9A9A9A", dim="#6B6B6B",
        accent="#E5E5E5", accent2="#A3A3A3", accent3="#FAFAFA", deep="#525252",
    ),
}

DEFAULT_THEME = "sky"


def get_palette(name=DEFAULT_THEME):
    """Trả về Palette theo tên; tên lạ thì rơi về theme mặc định."""
    return THEMES.get((name or "").strip().lower(), THEMES[DEFAULT_THEME])


def theme_names():
    return list(THEMES.keys())


# --------------------------------------------------------------- ngôn ngữ
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


def lang_color(name, index=0):
    """Màu chính thức của ngôn ngữ, không có trong bảng thì lấy từ dải màu."""
    return LANG_COLORS.get(name, RAMP[index % len(RAMP)])


# --------------------------------------------------------------- xếp hạng
# Ngưỡng điểm của từng hạng, cao xuống thấp. Điểm = sao×3 + repo×4 +
# follower×5 + fork×2 + commit×0.06 — mọi số đều đọc được từ API công khai.
GRADES = [(900, "S"), (600, "A+"), (380, "A"), (220, "B+"),
          (120, "B"), (50, "C+"), (0, "C")]


def score(stats):
    """Điểm thô, chưa xếp hạng."""
    return (stats.get("stars", 0) * 3
            + stats.get("repos", 0) * 4
            + stats.get("followers", 0) * 5
            + (stats.get("commits") or 0) * 0.06
            + stats.get("forks", 0) * 2)


def grade_progress(stats):
    """(hạng, phần trăm đã đi tới hạng kế, hạng kế hoặc None).

    Vòng cung trên thẻ phải nói một điều có thật. Bản cũ trả về một hằng số
    theo hạng (B+ luôn 74%), nên ai thêm 20 sao vẫn thấy đúng 74% và con số
    thành lời nói suông. Giờ nó là vị trí thật trong khoảng giữa hai hạng:
    279 điểm nằm giữa 220 (B+) và 380 (A) -> 37% tới A.
    """
    value = score(stats)
    for i, (need, letter) in enumerate(GRADES):
        if value >= need:
            if i == 0:
                return letter, 1.0, None
            top = GRADES[i - 1][0]
            span = float(top - need) or 1.0
            return letter, max(0.0, min(1.0, (value - need) / span)), GRADES[i - 1][1]
    return "C", 0.0, "C+"


def grade(stats):
    """Chấm hạng từ số liệu thật (không phải điểm thành tích)."""
    letter, percent, _ = grade_progress(stats)
    return letter, percent
