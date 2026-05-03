#!/usr/bin/env python3
"""
rewrite_for_speech.py — 把 markdown / 普通文本"朗读化"

只做机械可做的预处理：
  - 删除 URL
  - 删除 markdown 的 #, *, `, ![]() 等标记
  - 跳过 fenced code block（用 "（此处略过一段示例代码）" 替代）
  - 把表格用一句话概述（首行 + "等数据"）
  - 切短句、加默认 <break/>

LLM 该做的（语义重写、术语改写）由 Claude 主任务在调用本工具前完成；
本工具只负责"机械洁净"。

用法：
    python rewrite_for_speech.py paper.md > script.ssml
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


URL_RE = re.compile(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+")
CODE_BLOCK_RE = re.compile(r"```.*?```", re.S)
TABLE_RE = re.compile(r"^\|.*\|\s*$\n^\|[-:\s|]+\|\s*$\n(?:^\|.*\|\s*$\n)+", re.M)
MD_HEADER_RE = re.compile(r"^#{1,6}\s*", re.M)
MD_BOLD_ITALIC_RE = re.compile(r"\*+|_+|`+")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
MD_IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")


def summarize_table(_m: re.Match) -> str:
    return "（此处省略一张数据表）"


def clean_markdown(text: str) -> str:
    text = MD_IMG_RE.sub("", text)
    text = MD_LINK_RE.sub(r"\1", text)
    text = CODE_BLOCK_RE.sub("（此处略过一段示例代码）", text)
    text = TABLE_RE.sub(summarize_table, text)
    text = MD_HEADER_RE.sub("", text)
    text = MD_BOLD_ITALIC_RE.sub("", text)
    text = URL_RE.sub("", text)
    return text


SENT_END = re.compile(r"([。！？；…\n])")


def into_paragraphs(text: str) -> list[str]:
    parts = []
    buf = []
    cur_len = 0
    for tok in SENT_END.split(text):
        if not tok:
            continue
        buf.append(tok)
        cur_len += len(tok)
        if SENT_END.fullmatch(tok) and cur_len >= 30:
            parts.append("".join(buf).strip())
            buf, cur_len = [], 0
    if buf:
        parts.append("".join(buf).strip())
    return [p for p in parts if p]


def to_ssml(paragraphs: list[str]) -> str:
    out = ["<speak>"]
    for p in paragraphs:
        # 长段落每 80 字加一个 break
        chunks = []
        cur = ""
        for ch in p:
            cur += ch
            if len(cur) >= 80 and ch in "，、 ":
                chunks.append(cur + '<break time="200ms"/>')
                cur = ""
        if cur:
            chunks.append(cur)
        out.append(f"<p>{''.join(chunks)}<break time=\"400ms\"/></p>")
    out.append("</speak>")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    args = ap.parse_args()
    raw = Path(args.input).read_text()
    cleaned = clean_markdown(raw)
    paragraphs = into_paragraphs(cleaned)
    print(to_ssml(paragraphs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
