#!/usr/bin/env python3
"""
diff_summary.py — 把 unified diff 拆成结构化摘要

输入：unified diff（stdin 或 -i FILE）
输出：JSON，包含每个文件的：
    - path
    - additions / deletions
    - hunks: [{header, lines: [{type:'+/-/=', text}]}]

用法：
    git diff main..HEAD | python diff_summary.py
    python diff_summary.py -i my.diff
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import List


HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)$")


@dataclass
class Line:
    type: str  # '+', '-', '='
    text: str
    new_lineno: int | None = None


@dataclass
class Hunk:
    header: str
    new_start: int
    lines: List[Line] = field(default_factory=list)


@dataclass
class FileChange:
    path: str
    old_path: str | None = None
    additions: int = 0
    deletions: int = 0
    hunks: List[Hunk] = field(default_factory=list)
    binary: bool = False


def parse_diff(text: str) -> List[FileChange]:
    files: List[FileChange] = []
    cur: FileChange | None = None
    cur_hunk: Hunk | None = None
    new_lineno = 0

    for raw in text.splitlines():
        # 文件起始
        if raw.startswith("diff --git"):
            cur = FileChange(path="?")
            files.append(cur)
            cur_hunk = None
            continue

        if cur is None:
            continue

        # 路径
        if raw.startswith("--- "):
            cur.old_path = raw[4:].strip()
            if cur.old_path.startswith("a/"):
                cur.old_path = cur.old_path[2:]
            continue
        if raw.startswith("+++ "):
            p = raw[4:].strip()
            if p.startswith("b/"):
                p = p[2:]
            cur.path = p
            continue

        if raw.startswith("Binary files"):
            cur.binary = True
            continue

        # hunk header
        m = HUNK_RE.match(raw)
        if m:
            new_start = int(m.group(2))
            cur_hunk = Hunk(header=raw, new_start=new_start)
            cur.hunks.append(cur_hunk)
            new_lineno = new_start
            continue

        if cur_hunk is None:
            continue

        # diff body
        if raw.startswith("+") and not raw.startswith("+++"):
            cur_hunk.lines.append(Line("+", raw[1:], new_lineno))
            cur.additions += 1
            new_lineno += 1
        elif raw.startswith("-") and not raw.startswith("---"):
            cur_hunk.lines.append(Line("-", raw[1:], None))
            cur.deletions += 1
        else:
            cur_hunk.lines.append(Line("=", raw[1:] if raw else "", new_lineno))
            new_lineno += 1

    return files


def to_dict(files: List[FileChange]) -> list:
    out = []
    for f in files:
        d = asdict(f)
        out.append(d)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Parse unified diff into structured JSON.")
    ap.add_argument("-i", "--input", help="diff file (default: stdin)")
    ap.add_argument("--max-hunks", type=int, default=0,
                    help="只保留每个文件前 N 个 hunk；0=全部")
    args = ap.parse_args()

    text = open(args.input).read() if args.input else sys.stdin.read()
    files = parse_diff(text)
    if args.max_hunks > 0:
        for f in files:
            f.hunks = f.hunks[: args.max_hunks]

    print(json.dumps({
        "summary": {
            "files_changed": len(files),
            "total_additions": sum(f.additions for f in files),
            "total_deletions": sum(f.deletions for f in files),
        },
        "files": to_dict(files),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
