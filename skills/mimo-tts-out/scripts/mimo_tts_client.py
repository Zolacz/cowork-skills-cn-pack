#!/usr/bin/env python3
"""
mimo_tts_client.py — 调用小米 MiMo-V2.5-TTS 合成音频

当前为占位实现：
  - 真实 endpoint 是 https://platform.xiaomimimo.com/v1/audio/speech
  - 等 Token Plan 到账后把 ENV: MIMO_API_KEY 设上即可工作
  - 在没有 API key 的情况下：进入 "dry-run" 模式，把 SSML 拆 chunk 并写 transcript.txt，
    后续可在拿到 token 后只跑合成阶段。

依赖：requests （pip install requests）

用法：
    python mimo_tts_client.py script.ssml -o out.mp3 --voice zh-CN-Yunxi
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import wave
from pathlib import Path
from typing import Iterator


DEFAULT_ENDPOINT = os.environ.get(
    "MIMO_TTS_ENDPOINT", "https://platform.xiaomimimo.com/v1/audio/speech")
DEFAULT_MODEL = os.environ.get("MIMO_TTS_MODEL", "mimo-v2.5-tts")
DEFAULT_VOICE = os.environ.get("MIMO_TTS_VOICE", "zh-CN-Yunxi")


def split_ssml(ssml: str, max_chars: int) -> Iterator[str]:
    """按 <p> 拆 chunk，每个 chunk 仍是合法 SSML 片段。"""
    body = re.sub(r"^\s*<speak[^>]*>\s*|\s*</speak>\s*$", "", ssml.strip())
    paragraphs = re.findall(r"<p>.*?</p>", body, flags=re.S)
    if not paragraphs:
        paragraphs = [body]

    buf = []
    buf_len = 0
    for p in paragraphs:
        plen = len(p)
        if buf and buf_len + plen > max_chars:
            yield "<speak>" + "".join(buf) + "</speak>"
            buf, buf_len = [], 0
        buf.append(p)
        buf_len += plen
    if buf:
        yield "<speak>" + "".join(buf) + "</speak>"


def synth_chunk(text: str, voice: str, rate: float, dest: Path) -> bool:
    """合成单个 chunk → 写到 dest。"""
    api_key = os.environ.get("MIMO_API_KEY")
    if not api_key:
        # dry-run：写 transcript，方便审计
        dest.with_suffix(".txt").write_text(text)
        return False

    try:
        import requests
    except ImportError:
        print("缺少 requests: pip install requests --break-system-packages", file=sys.stderr)
        sys.exit(2)

    payload = {
        "model": DEFAULT_MODEL,
        "voice": voice,
        "input": text,
        "speed": rate,
        "format": "mp3",
    }
    r = requests.post(
        DEFAULT_ENDPOINT,
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=60,
    )
    if r.status_code >= 300:
        print(f"  ! TTS 失败 {r.status_code}: {r.text[:200]}", file=sys.stderr)
        return False
    dest.write_bytes(r.content)
    return True


def concat_mp3(parts: list[Path], out: Path) -> None:
    """简易 mp3 拼接：直接 cat（mp3 帧自同步）。
    若需要更可靠的拼接，请用 ffmpeg。"""
    with out.open("wb") as fout:
        for p in parts:
            fout.write(p.read_bytes())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ssml")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    ap.add_argument("--rate", type=float, default=1.0)
    ap.add_argument("--max-chunk-chars", type=int, default=500)
    args = ap.parse_args()

    ssml = Path(args.ssml).read_text()
    chunks = list(split_ssml(ssml, args.max_chunk_chars))
    print(f"==> 拆成 {len(chunks)} 个 chunk")

    tmp_dir = Path(args.output).with_suffix(".chunks")
    tmp_dir.mkdir(exist_ok=True)
    parts = []
    ok_count = 0
    for i, c in enumerate(chunks, 1):
        dest = tmp_dir / f"chunk_{i:03d}.mp3"
        ok = synth_chunk(c, args.voice, args.rate, dest)
        if ok:
            parts.append(dest)
            ok_count += 1
        print(f"  chunk {i}/{len(chunks)}: {'ok' if ok else 'dry-run (写 transcript)'}")

    if ok_count == 0:
        print(f"==> 未配置 MIMO_API_KEY，已写 transcript 到 {tmp_dir}/")
        print("    拿到 Token Plan 后设置 export MIMO_API_KEY=... 重跑。")
        return 0

    concat_mp3(parts, Path(args.output))
    print(f"==> 已合成 {args.output}（{len(parts)} chunks）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
