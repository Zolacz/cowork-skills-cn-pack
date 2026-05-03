#!/usr/bin/env python3
"""
normalize_cn.py — 中文常见字段标准化

支持：
  - city: 北京 / 北京市 / Beijing → 北京
  - phone: +86 13800000000 / 86-138-0000-0000 / 138 0000 0000 → 13800000000
  - id_card: 脱敏成 110105********1234

用法：
    python normalize_cn.py customers.csv --city-col city --phone-col phone -o cleaned.csv
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CITY_SUFFIX = re.compile(r"(市|地区|自治州|盟)$")
EN_CITY = {
    "beijing": "北京", "shanghai": "上海", "guangzhou": "广州",
    "shenzhen": "深圳", "hangzhou": "杭州", "chengdu": "成都",
    "nanjing": "南京", "tianjin": "天津", "wuhan": "武汉",
    "chongqing": "重庆", "xian": "西安", "suzhou": "苏州",
}


def norm_city(v: str) -> str:
    if not isinstance(v, str):
        return v
    s = v.strip()
    if s.lower() in EN_CITY:
        return EN_CITY[s.lower()]
    s = CITY_SUFFIX.sub("", s)
    return s


PHONE_RE = re.compile(r"\D+")


def norm_phone(v: str) -> str:
    if not isinstance(v, str):
        return v
    digits = PHONE_RE.sub("", v)
    if digits.startswith("86") and len(digits) == 13:
        digits = digits[2:]
    if digits.startswith("0086") and len(digits) == 15:
        digits = digits[4:]
    return digits if len(digits) == 11 and digits[0] == "1" else v


def mask_id_card(v: str) -> str:
    if not isinstance(v, str) or len(v) not in (15, 18):
        return v
    return v[:6] + "*" * (len(v) - 10) + v[-4:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--city-col")
    ap.add_argument("--phone-col")
    ap.add_argument("--id-col")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    try:
        import pandas as pd
    except ImportError:
        print("缺少 pandas", file=sys.stderr)
        return 2

    p = Path(args.path)
    df = (pd.read_excel(p) if p.suffix.lower().startswith((".xls",))
          else pd.read_csv(p))

    if args.city_col:
        df[args.city_col + "_norm"] = df[args.city_col].map(norm_city)
    if args.phone_col:
        df[args.phone_col + "_norm"] = df[args.phone_col].map(norm_phone)
    if args.id_col:
        df[args.id_col + "_masked"] = df[args.id_col].map(mask_id_card)

    out = Path(args.output)
    if out.suffix.lower().startswith(".xls"):
        df.to_excel(out, index=False)
    else:
        df.to_csv(out, index=False)
    print(f"已写出 {out}（行数 {len(df)}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
