#!/usr/bin/env python3
"""
渲染图 5：paper-to-podcast 多 Agent 协同时序图

输出：docs/demo_paper_to_podcast_sequence.png

横轴：时间 0s → 240s
纵轴（lanes）：用户 / 主 Agent / 5 个子 Agent / mimo-tts-out / MiMo TTS API
事件：5 个子 Agent 并行入库 → 综述起草 → 朗读化重写 → MiMo TTS 5-chunk 并行合成
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

FONT_ZH = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W, H = 2200, 1500
BG = (255, 255, 255)
PANEL = (250, 250, 252)
GRID = (228, 228, 232)
INK = (32, 32, 36)
DIM = (110, 110, 120)
USER = (88, 91, 191)
MAIN = (35, 134, 184)
SUB = (152, 92, 188)
SKILL = (216, 134, 47)
MIMO = (212, 65, 65)

LEFT_PAD = 280
RIGHT_PAD = 80
TOP_PAD = 150
BOT_PAD = 110
PLOT_W = W - LEFT_PAD - RIGHT_PAD
PLOT_H = H - TOP_PAD - BOT_PAD

T_MIN, T_MAX = 0, 240
def t2x(t: float) -> int:
    return int(LEFT_PAD + (t - T_MIN) / (T_MAX - T_MIN) * PLOT_W)


LANES = [
    ("用户",                 USER),
    ("主 Agent (Plan Mode)",  MAIN),
    ("子 Agent A · 论文 1",   SUB),
    ("子 Agent B · 论文 2",   SUB),
    ("子 Agent C · 论文 3",   SUB),
    ("子 Agent D · 论文 4",   SUB),
    ("子 Agent E · 论文 5",   SUB),
    ("Skill: paper-drafter", SKILL),
    ("Skill: mimo-tts-out",  SKILL),
    ("MiMo-V2.5-TTS API",    MIMO),
]
LANE_GAP = PLOT_H / (len(LANES) - 1)


def lane_y(i: int) -> int:
    return int(TOP_PAD + i * LANE_GAP)


def is_cjk(c: str) -> bool:
    cp = ord(c)
    return (
        0x4E00 <= cp <= 0x9FFF or       # CJK Unified
        0x3000 <= cp <= 0x303F or       # CJK 标点
        0xFF00 <= cp <= 0xFFEF or       # 全角 ASCII
        0x3400 <= cp <= 0x4DBF or       # CJK Ext A
        0x2E80 <= cp <= 0x2EFF or       # CJK 部首
        0xFE30 <= cp <= 0xFE4F          # CJK 兼容
    )


def draw_text_mixed(draw: ImageDraw.ImageDraw, x, y, text, fill,
                    ascii_font, cjk_font):
    """逐字符切换字体：ASCII 用 ascii_font，CJK 用 cjk_font。"""
    cx = float(x)
    cur = ""
    cur_font = None
    for ch in text:
        f = cjk_font if is_cjk(ch) else ascii_font
        if cur_font is None:
            cur_font = f
        if f is cur_font:
            cur += ch
        else:
            draw.text((cx, y), cur, fill=fill, font=cur_font)
            cx += draw.textlength(cur, font=cur_font)
            cur = ch
            cur_font = f
    if cur:
        draw.text((cx, y), cur, fill=fill, font=cur_font)


def text_w_mixed(draw, text, ascii_font, cjk_font) -> float:
    """估算混合渲染的总宽度。"""
    total = 0.0
    cur = ""
    cur_font = None
    for ch in text:
        f = cjk_font if is_cjk(ch) else ascii_font
        if cur_font is None:
            cur_font = f
        if f is cur_font:
            cur += ch
        else:
            total += draw.textlength(cur, font=cur_font)
            cur = ch
            cur_font = f
    if cur:
        total += draw.textlength(cur, font=cur_font)
    return total


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # 字体集
    f_title_a = ImageFont.truetype(FONT_SANS_B, 32)
    f_title_z = ImageFont.truetype(FONT_ZH, 32)
    f_sub_a = ImageFont.truetype(FONT_SANS, 19)
    f_sub_z = ImageFont.truetype(FONT_ZH, 19)
    f_lane_a = ImageFont.truetype(FONT_SANS, 20)
    f_lane_z = ImageFont.truetype(FONT_ZH, 20)
    f_event_a = ImageFont.truetype(FONT_SANS, 17)
    f_event_z = ImageFont.truetype(FONT_ZH, 17)
    f_axis = ImageFont.truetype(FONT_MONO_B, 17)
    f_meta_a = ImageFont.truetype(FONT_SANS, 18)
    f_meta_z = ImageFont.truetype(FONT_ZH, 18)
    f_mono_label = ImageFont.truetype(FONT_MONO, 15)
    f_footer = ImageFont.truetype(FONT_MONO, 15)

    # === title ===
    draw_text_mixed(draw, 60, 32,
                    "paper-to-podcast · 多 Agent 协同时序",
                    INK, f_title_a, f_title_z)
    draw_text_mixed(draw, 60, 80,
                    "5 篇论文 → 10 分钟可朗读播客；演示长链推理 + 多子 Agent 并行 + 跨模型路由",
                    DIM, f_sub_a, f_sub_z)

    # === axis ===
    axis_y = TOP_PAD - 24
    draw.line([(LEFT_PAD, axis_y), (LEFT_PAD + PLOT_W, axis_y)], fill=GRID, width=2)
    for t in range(0, 241, 30):
        x = t2x(t)
        draw.line([(x, axis_y), (x, axis_y - 8)], fill=DIM, width=1)
        draw.text((x - 14, axis_y - 32), f"{t}s", fill=DIM, font=f_axis)
    draw_text_mixed(draw, LEFT_PAD + PLOT_W // 2 - 60, 110,
                    "──── 时间轴 ────", DIM, f_sub_a, f_sub_z)

    # === lanes ===
    for i, (name, color) in enumerate(LANES):
        y = lane_y(i)
        draw.line([(LEFT_PAD, y), (LEFT_PAD + PLOT_W, y)],
                  fill=GRID, width=1)
        draw.rectangle([20, y - 18, LEFT_PAD - 20, y + 18],
                       fill=PANEL, outline=GRID)
        draw.ellipse([34, y - 8, 50, y + 8], fill=color)
        draw_text_mixed(draw, 60, y - 12, name, INK, f_lane_a, f_lane_z)

    # === bars ===
    # 主 Agent
    draw.rounded_rectangle(
        [t2x(0), lane_y(1) - 10, t2x(240), lane_y(1) + 10],
        radius=6, fill=(*MAIN, 50), outline=MAIN, width=1)

    # 5 个子 Agent
    for i in range(5):
        y = lane_y(2 + i)
        draw.rounded_rectangle(
            [t2x(30), y - 10, t2x(90), y + 10],
            radius=6, fill=(*SUB, 80), outline=SUB, width=2)
        draw.text((t2x(46), y - 8), "PDF -> YAML",
                  fill=(255, 255, 255), font=f_mono_label)

    # paper-drafter
    draw.rounded_rectangle(
        [t2x(30), lane_y(7) - 10, t2x(180), lane_y(7) + 10],
        radius=6, fill=(*SKILL, 60), outline=SKILL, width=2)
    draw_text_mixed(draw, t2x(60), lane_y(7) - 8,
                    "综述起草 + cite_normalize",
                    INK, f_mono_label, f_event_z)

    # mimo-tts-out
    draw.rounded_rectangle(
        [t2x(200), lane_y(8) - 10, t2x(240), lane_y(8) + 10],
        radius=6, fill=(*SKILL, 60), outline=SKILL, width=2)
    draw_text_mixed(draw, t2x(204), lane_y(8) - 8,
                    "TTS 调度",
                    INK, f_mono_label, f_event_z)

    # MiMo TTS chunks
    for i in range(5):
        x0 = t2x(220 + i)
        x1 = t2x(232 + i)
        y_off = (i - 2) * 4
        y = lane_y(9) + y_off
        draw.rounded_rectangle(
            [x0, y - 6, x1, y + 6],
            radius=4, fill=(*MIMO, 90), outline=MIMO, width=1)
    draw_text_mixed(draw, t2x(206), lane_y(9) + 18,
                    "5 个 chunk 并行合成",
                    DIM, f_mono_label, f_event_z)

    # === arrows ===
    def arrow(t1, lane_a, t2, lane_b, label="", color=DIM):
        x1, y1 = t2x(t1), lane_y(lane_a)
        x2, y2 = t2x(t2), lane_y(lane_b)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return
        length = max(1, (dx * dx + dy * dy) ** 0.5)
        ux, uy = dx / length, dy / length
        ah = 12
        lx = x2 - ux * ah - uy * 6
        ly = y2 - uy * ah + ux * 6
        rx = x2 - ux * ah + uy * 6
        ry = y2 - uy * ah - ux * 6
        draw.polygon([(x2, y2), (lx, ly), (rx, ry)], fill=color)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            draw_text_mixed(draw, mx + 6, my - 8, label,
                            color, f_mono_label, f_event_z)

    arrow(0, 0, 5, 1, "请求", USER)
    for i in range(5):
        arrow(20, 1, 30, 2 + i, "派发", MAIN)
    for i in range(5):
        arrow(90, 2 + i, 100, 1, "yaml", SUB)
    arrow(100, 1, 100, 7, "起草", MAIN)
    arrow(180, 7, 185, 1, "draft.md", SKILL)
    arrow(195, 1, 200, 8, "rewrite", MAIN)
    for i in range(5):
        arrow(215, 8, 220 + i, 9, "", SKILL)
    arrow(235, 9, 238, 8, "mp3", MIMO)
    arrow(240, 8, 240, 0, "output.mp3", MIMO)

    # === event annotations ===
    annotations = [
        (0,   0,  ["用户上传 5 篇 PDF", "+ 任务要求"]),
        (10,  1,  ["Plan Mode：", "拆解 + 路由"]),
        (60,  4,  ["5 个并行子 Agent", "各自独立 ctx"]),
        (105, 7,  ["基于 yaml 摘要", "起草综述"]),
        (180, 7,  ["cite_normalize", "GB/T 7714 引用"]),
        (210, 8,  ["rewrite_for_speech", "朗读化 + SSML"]),
        (227, 9,  ["MiMo TTS", "5 chunk 并行"]),
        (240, 0,  ["交付 output.mp3", "(9.5 min)"]),
    ]
    for t, lane, labels in annotations:
        x = t2x(t)
        y = lane_y(lane)
        draw.ellipse([x - 7, y - 7, x + 7, y + 7],
                     fill=(255, 255, 255), outline=INK, width=2)
        place_above = lane > 5
        ty_base = y - 60 if place_above else y + 24
        for j, ln in enumerate(labels):
            tw = text_w_mixed(draw, ln, f_event_a, f_event_z)
            draw_text_mixed(draw, x - tw / 2, ty_base + j * 22,
                            ln, INK, f_event_a, f_event_z)

    # === bottom stats ===
    stats_y = H - BOT_PAD + 6
    draw.line([(60, stats_y - 10), (W - 60, stats_y - 10)],
              fill=GRID, width=2)
    draw_text_mixed(draw, 60, stats_y,
                    "工具调用 45 轮     跨文件 10+      Claude tokens ~ 83 万      MiMo Credits ~ 2,000",
                    INK, f_meta_a, f_meta_z)
    draw.text((60, stats_y + 32),
              "cowork-skills-cn-pack v0.1  ·  examples/02-paper-to-podcast.md  ·  github.com/zola/cowork-skills-cn-pack",
              fill=DIM, font=f_footer)

    # === legend ===
    leg_x = LEFT_PAD + 100
    leg_y = 92
    legends = [
        ("用户输入 / 交付", USER),
        ("主 Agent",        MAIN),
        ("子 Agent (并行)", SUB),
        ("Skill (本 pack)", SKILL),
        ("MiMo API",        MIMO),
    ]
    cx = leg_x
    for label, color in legends:
        draw.ellipse([cx, leg_y + 6, cx + 14, leg_y + 20], fill=color)
        cx += 20
        draw_text_mixed(draw, cx, leg_y + 4, label,
                        INK, f_event_a, f_event_z)
        cx += int(text_w_mixed(draw, label, f_event_a, f_event_z)) + 30

    out = "/sessions/eager-eloquent-brown/mnt/小米/cowork-skills-cn-pack/docs/demo_paper_to_podcast_sequence.png"
    img.save(out, "PNG")
    print("✓ wrote", out, "size:", W, "x", H)


if __name__ == "__main__":
    main()
