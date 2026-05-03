#!/usr/bin/env python3
"""
commit_lint.py — 检查 commit message 是否符合中文工程规范

规则（默认）：
  - 单行 ≤ 50 字
  - 动词开头（修复 / 新增 / 优化 / 重构 / 文档 / 测试 / 构建）
  - 推荐有 scope: <动词>(<scope>): <描述>
  - 不以句号结尾
  - 不以 "更新代码" "修改一些东西" 这类废话开头

用法：
    git log -1 --pretty=%B | python commit_lint.py
    python commit_lint.py -i msg.txt
"""
from __future__ import annotations

import argparse
import re
import sys
import json

VERBS = ["修复", "新增", "优化", "重构", "文档", "测试", "构建", "样式", "回退",
         "fix", "feat", "refactor", "perf", "docs", "test", "chore", "style", "revert"]
NOISE = ["更新代码", "修改一些东西", "随便改改", "wip", "tmp", "测试一下", "保存"]


def lint(msg: str) -> dict:
    issues = []
    msg = msg.strip()
    first_line = msg.splitlines()[0] if msg else ""

    if not first_line:
        issues.append({"level": "high", "rule": "empty", "msg": "commit message 不能为空"})
        return {"first_line": first_line, "issues": issues, "suggestion": ""}

    if len(first_line) > 50:
        issues.append({"level": "med", "rule": "too_long",
                       "msg": f"首行长度 {len(first_line)} > 50"})

    if first_line.endswith("。") or first_line.endswith("."):
        issues.append({"level": "low", "rule": "trailing_dot", "msg": "首行不应以句号结尾"})

    # 动词开头（含 conventional commits）
    cc_match = re.match(r"^([a-z]+)(?:\([^)]+\))?\s*[:：]\s*", first_line)
    starts_with_verb = cc_match and cc_match.group(1).lower() in VERBS
    starts_with_cn_verb = any(first_line.startswith(v) for v in VERBS if any("一" <= c <= "鿿" for c in v))
    if not (starts_with_verb or starts_with_cn_verb):
        issues.append({"level": "med", "rule": "no_verb",
                       "msg": "建议以动词开头：修复/新增/优化/重构/feat/fix/..."})

    for n in NOISE:
        if n in first_line.lower():
            issues.append({"level": "high", "rule": "noise",
                           "msg": f"包含废话词 “{n}”，请说明改了什么"})
            break

    # 改进建议
    suggestion = ""
    if any(i["rule"] in ("no_verb", "noise") for i in issues):
        suggestion = "建议改写为：<动词>(<scope>): <一句话说明改了什么 / 为什么>"

    return {"first_line": first_line, "issues": issues, "suggestion": suggestion}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input")
    args = ap.parse_args()
    msg = open(args.input).read() if args.input else sys.stdin.read()
    print(json.dumps(lint(msg), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
