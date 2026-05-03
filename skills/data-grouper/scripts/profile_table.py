#!/usr/bin/env python3
"""
profile_table.py — 探查 csv / xlsx 表，输出列结构 + 可疑字段标记

依赖：pandas, openpyxl
    pip install pandas openpyxl --break-system-packages

用法：
    python profile_table.py customers.xlsx
    python profile_table.py orders.csv --sheet 0
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--sheet", default=0, help="xlsx 的 sheet 名或序号")
    ap.add_argument("--head", type=int, default=200)
    args = ap.parse_args()

    try:
        import pandas as pd
    except ImportError:
        print("缺少 pandas: pip install pandas openpyxl --break-system-packages", file=sys.stderr)
        return 2

    p = Path(args.path)
    if p.suffix.lower() in {".xlsx", ".xls", ".xlsm"}:
        df = pd.read_excel(p, sheet_name=args.sheet, nrows=args.head)
    else:
        df = pd.read_csv(p, nrows=args.head)

    print(f"# {p.name}")
    print(f"sampled rows: {len(df)} (head)")
    print(f"columns: {len(df.columns)}\n")

    for col in df.columns:
        s = df[col]
        null_pct = s.isna().mean() * 100
        sample = s.dropna().astype(str).unique().tolist()[:3]
        flags = []

        # 大小写不一致
        if s.dtype == object:
            lower_unique = {str(v).strip().lower() for v in s.dropna()}
            actual_unique = {str(v).strip() for v in s.dropna()}
            if 0 < len(lower_unique) < len(actual_unique):
                flags.append("⚠ 大小写不一致")

        # 多写法（同一概念多种 representation）
        if s.dtype == object and 0 < s.nunique() <= 50:
            for v in s.dropna().astype(str):
                if v.endswith("市") and v[:-1] in s.values:
                    flags.append("⚠ 多种写法")
                    break

        # null 率高
        if null_pct > 30:
            flags.append(f"⚠ null={null_pct:.0f}%")

        flag_str = " ".join(flags) if flags else ""
        print(f"  - {col:20s} {str(s.dtype):10s} null={null_pct:5.1f}%  sample={sample}  {flag_str}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
