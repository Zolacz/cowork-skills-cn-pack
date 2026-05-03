#!/usr/bin/env python3
"""
scan_drift.py — 扫描项目，找出文档 vs 代码不一致的地方

最简版本：
  - 找所有 *.md
  - 抽出 fenced code block 里的 cli 示例（```bash 之类）
  - 抽出 cli 调用：foo --opt val
  - 在代码里 grep 这些 --opt 是否出现
  - 输出 JSON drift report

用法：
    python scan_drift.py /path/to/project > drift.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CODE_BLOCK_RE = re.compile(r"```(?:bash|sh|shell|console)\s*\n(.*?)```", re.S)
CLI_OPT_RE = re.compile(r"--([a-zA-Z][\w-]+)")


def find_md_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.md") if "node_modules" not in p.parts and ".git" not in p.parts]


def scan_doc_cli_options(p: Path) -> dict[str, list[int]]:
    """文档里出现的 --opt → 行号"""
    out: dict[str, list[int]] = {}
    for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
        for m in CLI_OPT_RE.finditer(line):
            out.setdefault(m.group(1), []).append(i)
    return out


def grep_codebase(root: Path, opt: str) -> int:
    """在 src 里 grep --opt 是否还存在"""
    needles = [f"--{opt}", f'"{opt}"', f"'{opt}'"]
    count = 0
    for path in root.rglob("*"):
        if path.is_dir() or path.suffix in {".md", ".png", ".jpg", ".pdf"}:
            continue
        if "node_modules" in path.parts or ".git" in path.parts:
            continue
        try:
            txt = path.read_text(errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        for n in needles:
            if n in txt:
                count += 1
                break
    return count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    drift = []
    for md in find_md_files(root):
        opts = scan_doc_cli_options(md)
        for opt, lines in opts.items():
            hits = grep_codebase(root, opt)
            if hits == 0:
                drift.append({
                    "type": "cli",
                    "file": str(md.relative_to(root)),
                    "lines": lines,
                    "evidence": f"文档提到 --{opt}，但代码中找不到对应实现",
                    "level": "high",
                })

    print(json.dumps({
        "scanned_docs": len(find_md_files(root)),
        "drift_count": len(drift),
        "drift": drift,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
