#!/usr/bin/env python3
"""
risk_classifier.py — 给每个 hunk 打风险标签

输入：diff_summary.py 的 JSON 输出（stdin 或 -i FILE）
输出：原 JSON + 每个 hunk 加上 `risks` 字段，每个 risk 是
    {level: 'high'|'med'|'low', kind, evidence}

用法：
    git diff main..HEAD | python diff_summary.py | python risk_classifier.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# (level, kind, regex, scope)  — scope: 'add' 只看 + 行 / 'any' 看任意行
PATTERNS = [
    # 高危
    ("high", "sql_injection",   re.compile(r"(?:SELECT|INSERT|UPDATE|DELETE).*?\+.*?(?:request|params|input)", re.I), "add"),
    ("high", "swallowed_error", re.compile(r"except\s*:\s*pass\b"), "add"),
    ("high", "swallowed_error", re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}"), "add"),
    ("high", "hardcoded_secret",re.compile(r"(?:api[_-]?key|secret|token|password)\s*=\s*['\"][A-Za-z0-9_\-]{12,}['\"]", re.I), "add"),
    ("high", "eval_used",       re.compile(r"\beval\s*\("), "add"),
    # 中危
    ("med",  "money_as_float",  re.compile(r"\b(price|amount|fee|balance|total|cost)\s*[:=]\s*[\d.]+\s*$", re.I), "add"),
    ("med",  "tz_hardcoded",    re.compile(r"\+08:00|Asia/Shanghai|GMT\+8"), "add"),
    ("med",  "string_zh",       re.compile(r"\"[一-鿿]+\""), "add"),
    ("med",  "todo_left",       re.compile(r"\b(?:TODO|FIXME|XXX|HACK)\b"), "add"),
    ("med",  "any_used_ts",     re.compile(r":\s*any\b|\bas\s+any\b"), "add"),
    ("med",  "race_shared_map", re.compile(r"\b(?:goroutine|go\s+func|asyncio\.create_task|spawn)\b"), "add"),
    # 低危
    ("low",  "console_log",     re.compile(r"\bconsole\.log\("), "add"),
    ("low",  "print_left",      re.compile(r"^print\("), "add"),
    ("low",  "long_function",   re.compile(r"^def\s+\w+\(.{120,}"), "add"),
]


def classify(data: dict) -> dict:
    for f in data.get("files", []):
        for h in f.get("hunks", []):
            risks = []
            for ln in h.get("lines", []):
                t = ln.get("type")
                txt = ln.get("text", "")
                for level, kind, rx, scope in PATTERNS:
                    if scope == "add" and t != "+":
                        continue
                    if rx.search(txt):
                        risks.append({
                            "level": level,
                            "kind": kind,
                            "line": ln.get("new_lineno"),
                            "evidence": txt.strip()[:140],
                        })
            h["risks"] = risks
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description="Tag diff hunks with risk labels.")
    ap.add_argument("-i", "--input", help="diff_summary JSON (default: stdin)")
    args = ap.parse_args()

    raw = open(args.input).read() if args.input else sys.stdin.read()
    data = json.loads(raw)
    out = classify(data)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
