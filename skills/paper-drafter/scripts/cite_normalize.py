#!/usr/bin/env python3
"""
cite_normalize.py — 把 [id1, id2] 占位引文替换成顺序数字编号 [1][2]，并生成参考文献节

用法：
    python cite_normalize.py draft.md ./.papers/ > final.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CITE_RE = re.compile(r"\[([a-z][a-z0-9_]*(?:\s*,\s*[a-z][a-z0-9_]*)*)\]")


def load_bibtex(papers_dir: Path) -> dict[str, str]:
    """读 .papers/*.yaml 提取 bibtex 字段。极简解析，仅适用于本工具产出的 yaml。"""
    out = {}
    for f in papers_dir.glob("*.yaml"):
        text = f.read_text()
        m = re.search(r"^id:\s*(\S+)", text, re.M)
        if not m:
            continue
        pid = m.group(1)
        bm = re.search(r"^bibtex:\s*\|\s*\n((?:  .*\n?)*)", text, re.M)
        bib = bm.group(1) if bm else f"@misc{{{pid}, note=auto}}"
        out[pid] = bib.replace("\n  ", "\n").rstrip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("papers_dir")
    args = ap.parse_args()

    text = Path(args.draft).read_text()
    bib = load_bibtex(Path(args.papers_dir))

    order: list[str] = []

    def repl(m: re.Match) -> str:
        ids = [s.strip() for s in m.group(1).split(",")]
        nums = []
        for i in ids:
            if i not in order:
                order.append(i)
            nums.append(str(order.index(i) + 1))
        return "[" + "][".join(nums) + "]"

    body = CITE_RE.sub(repl, text)
    print(body)
    print("\n## 参考文献\n")
    for n, pid in enumerate(order, 1):
        print(f"[{n}] {bib.get(pid, '@misc{' + pid + '}')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
