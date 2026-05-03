#!/usr/bin/env python3
"""
渲染图 4：cn-pr-review skill 实战运行的终端截图

输出：docs/demo_cn_pr_review_terminal.png

使用 PIL 直接画，避免 matplotlib 的字体回退问题。
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

# 字体（系统已确认存在）
FONT_ZH = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_MONO_R = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# 颜色（macOS Dark Terminal）
BG = (30, 30, 30)
TITLE_BAR = (60, 60, 60)
FG = (232, 232, 232)
GREEN = (126, 201, 142)
BLUE = (126, 175, 217)
YELLOW = (240, 198, 116)
RED = (204, 102, 102)
GREY = (144, 144, 144)
PURPLE = (178, 148, 187)

# 行：(color, text)
LINES = [
    (GREY,   "$ # 在 Cowork 里粘贴一段 diff，请求评审"),
    (FG,     "> 帮我评审这个 diff，重点看安全性："),
    (GREY,   "    @@ -10,6 +10,9 @@ def get_user(uid):"),
    (RED,    "    -    sql = \"SELECT * FROM users WHERE id = \" + str(uid)"),
    (GREEN,  "    +    sql = \"SELECT * FROM users WHERE id = ?\""),
    (RED,    "    -        return conn.execute(sql).fetchone()"),
    (GREEN,  "    +        return conn.execute(sql, (uid,)).fetchone()"),
    (GREEN,  "    +    api_key = \"sk-1234567890ABCDEF\""),
    (GREEN,  "    +    print(\"debug:\", api_key)"),
    (FG,     ""),
    (PURPLE, "[OK] Skill triggered: cn-pr-review"),
    (BLUE,   "  -> diff_summary.py     [hunks=1, +4/-2]"),
    (BLUE,   "  -> risk_classifier.py  [scanning 4 added lines...]"),
    (RED,    "    !! found risk: HIGH · hardcoded_secret @ src/api.py"),
    (BLUE,   "  -> commit_lint.py      [skipped — no commit msg provided]"),
    (FG,     ""),
    (YELLOW, "── 评审报告 ─────────────────────────────────────"),
    (FG,     "[1] 核心改动摘要"),
    (FG,     "    修复 get_user 的 SQL 拼接漏洞，改用参数化查询。"),
    (FG,     "    但同时引入硬编码 API Key 与 debug print。"),
    (FG,     ""),
    (FG,     "[2] 潜在风险"),
    (RED,    "    [HIGH] src/api.py:14 — 硬编码 API Key"),
    (FG,     "           \"sk-1234567890ABCDEF\"，严禁合并；需立即吊销。"),
    (RED,    "    [HIGH] src/api.py:15 — debug print 把 secret 落日志。"),
    (YELLOW, "    [MED]  src/api.py:13 — except: pass 静默吞异常。"),
    (FG,     ""),
    (FG,     "[3] 测试缺口"),
    (FG,     "    · 修复 SQL 注入但缺 test_get_user_with_evil_uid"),
    (FG,     "    · 缺 secret-leak 的 lint/CI 拦截规则"),
    (FG,     ""),
    (FG,     "[4] Commit Message 建议"),
    (GREEN,  "    fix(api): 修复 get_user SQL 注入并撤销硬编码 key"),
    (FG,     ""),
    (GREY,   "── stats ────────────────────────────────────────"),
    (GREY,   "  tool calls : 5      tokens in : 4.2k"),
    (GREY,   "  duration   : 38s    tokens out: 1.8k"),
    (GREY,   "  total      : ~38k tokens"),
    (FG,     ""),
    (GREY,   "  cowork-skills-cn-pack v0.1 · cn-pr-review skill"),
]


def has_cjk(s: str) -> bool:
    for c in s:
        if "　" <= c <= "鿿" or "✀" <= c <= "➿":
            return True
        # emoji 也走 CJK 路径
        cp = ord(c)
        if 0x1F300 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF:
            return True
    return False


def draw_text_mixed(draw, x, y, text, color, font_mono, font_zh):
    """逐字符切换字体：ASCII 用 mono，其它用 zh 字体。"""
    cx = x
    cur = ""
    cur_font = None
    for ch in text:
        is_cjk = has_cjk(ch)
        f = font_zh if is_cjk else font_mono
        if cur_font is None:
            cur_font = f
        if f is cur_font:
            cur += ch
        else:
            draw.text((cx, y), cur, fill=color, font=cur_font)
            cx += int(draw.textlength(cur, font=cur_font))
            cur = ch
            cur_font = f
    if cur:
        draw.text((cx, y), cur, fill=color, font=cur_font)


def main():
    W, H = 1500, 1700
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # 标题栏
    title_h = 44
    draw.rectangle([0, 0, W, title_h], fill=TITLE_BAR)
    # 三色按钮
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = 22 + i * 24
        cy = title_h // 2
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=c)

    # 标题
    title_font = ImageFont.truetype(FONT_MONO_R, 18)
    title_text = "claude — cn-pr-review demo  ·  80×40"
    tw = draw.textlength(title_text, font=title_font)
    draw.text(((W - tw) / 2, title_h // 2 - 11), title_text,
              fill=(200, 200, 200), font=title_font)

    # 正文
    mono = ImageFont.truetype(FONT_MONO_R, 22)
    mono_b = ImageFont.truetype(FONT_MONO, 22)
    zh = ImageFont.truetype(FONT_ZH, 22)

    line_h = 36
    pad_top = title_h + 24
    for i, (color, text) in enumerate(LINES):
        y = pad_top + i * line_h
        if not text:
            continue
        # 表头/段落使用粗体
        font_for_line = mono_b if text.startswith(("[OK]", "──", "[1]", "[2]", "[3]", "[4]")) else mono
        draw_text_mixed(draw, 28, y, text, color, font_for_line, zh)

    out_path = "/sessions/eager-eloquent-brown/mnt/小米/cowork-skills-cn-pack/docs/demo_cn_pr_review_terminal.png"
    img.save(out_path, "PNG")
    print("✓ wrote", out_path, "size:", W, "x", H)


if __name__ == "__main__":
    main()
