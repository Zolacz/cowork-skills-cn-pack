#!/usr/bin/env python3
"""
extract_paper.py — PDF → 结构化 YAML 骨架（让 Claude 在子任务里精读时填槽）

这个脚本只做"机械可做的事"：
  - 提取 PDF 文本
  - 找到 title / authors / abstract / keywords
  - 切出 sections（按 "1. Introduction" 这类 heading）
  - 输出一份预填了 title/authors/abstract/sections 的 YAML 骨架

LLM 不擅长的事（contribution / method / limitations 摘要）留空，由 Claude 在子任务里填。

依赖：pypdf （pip install pypdf）

用法：
    python extract_paper.py paper.pdf > .papers/zhang2024.yaml
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("缺少 pypdf：pip install pypdf --break-system-packages", file=sys.stderr)
    sys.exit(2)


SECTION_HEADERS = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\.?\s+)?"
    r"(introduction|background|related work|method|methodology|approach|experiments|"
    r"results|evaluation|discussion|conclusion|references|"
    r"摘要|引言|方法|实验|结果|讨论|结论|参考文献)\b",
    re.IGNORECASE,
)


def read_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def guess_title(text: str) -> str:
    for ln in text.splitlines():
        s = ln.strip()
        if 8 < len(s) < 200 and not s.lower().startswith(("abstract", "摘要")):
            return s
    return "<unknown title>"


def guess_authors(text: str) -> list[str]:
    head = "\n".join(text.splitlines()[:30])
    candidates = re.findall(r"([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+)", head)
    return list(dict.fromkeys(candidates))[:8]


def guess_abstract(text: str) -> str:
    m = re.search(r"(?i)(?:abstract|摘要)[\s:]*\n?(.{60,1500}?)(?:\n\s*\n|1\.?\s+(?:introduction|引言))",
                  text, re.S)
    if m:
        return m.group(1).strip()
    return ""


def split_sections(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    sections, cur_name, cur_buf = [], "preface", []
    for ln in lines:
        m = SECTION_HEADERS.match(ln)
        if m:
            sections.append((cur_name, "\n".join(cur_buf).strip()))
            cur_name, cur_buf = m.group(1).strip().lower(), []
        else:
            cur_buf.append(ln)
    sections.append((cur_name, "\n".join(cur_buf).strip()))
    return [(n, c) for n, c in sections if c]


def yaml_escape(s: str) -> str:
    s = s.replace("\\", "\\\\").replace("\"", "\\\"")
    return f"\"{s}\"" if s else "\"\""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--id", help="paper id (default: pdf stem)", default=None)
    args = ap.parse_args()

    text = read_pdf_text(args.pdf)
    pid = args.id or Path(args.pdf).stem

    title = guess_title(text)
    authors = guess_authors(text)
    abstract = guess_abstract(text)
    sections = split_sections(text)

    print(f"id: {pid}")
    print(f"title: {yaml_escape(title)}")
    print("authors:")
    for a in authors:
        print(f"  - {yaml_escape(a)}")
    print(f"abstract: |\n  {abstract.replace(chr(10), chr(10) + '  ')[:1200]}")
    print(f"sections_found: {[n for n, _ in sections]}")
    print("# === 以下字段由 Claude 在精读子任务中填写 ===")
    for k in ["contribution", "method", "results", "limitations",
              "relevance_to_my_topic", "my_questions"]:
        print(f"{k}: |\n  ")
    print("bibtex: |\n  @article{" + pid + ",\n    title = " + yaml_escape(title) + ",\n  }")
    return 0


if __name__ == "__main__":
    sys.exit(main())
