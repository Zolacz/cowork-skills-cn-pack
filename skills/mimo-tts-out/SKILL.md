---
name: mimo-tts-out
description: 把 Claude / Cowork 的文本输出转成可朗读的语音脚本，并通过小米 MiMo-V2.5-TTS 生成音频。当用户要求"读出来"、"转成语音"、"做成播客"、"通勤听"、"导成 mp3"、"把这份报告念给我听"时触发。先做"朗读化重写"（把书面长句改成可听的口语短句、把表格 / 代码块跳过或叙述化、加停顿提示），再调用 MiMo TTS 合成 wav / mp3。覆盖播客式产出、视频配音底稿、有声笔记三种模式。触发词包括"念给我听"、"转成语音"、"做成音频"、"播客脚本"、"TTS"、"text to speech"、"通勤听"、"导成 mp3"、"配音稿"。
license: MIT
---

# mimo-tts-out · 主模型 + MiMo TTS 双 Agent 协同 Skill

## 设计目标

把"长文阅读 → 通勤听 / 视频配音 / 有声笔记"这件事一键化。

**这是 cowork-skills-cn-pack 里第一个对接小米 MiMo-V2.5 生态的 skill**，演示主模型 (Claude) 做长链推理与文本规划、MiMo 做最后一公里语音合成的多 Agent 协同范式。

## 触发判断

| 用户说 | 触发模式 |
|---|---|
| "把这份报告念给我听" | 通勤听模式（默认） |
| "做成 5 分钟的播客脚本" | 播客模式（含开场/结尾） |
| "给这个视频做配音稿" | 配音稿模式（含 SSML 停顿提示） |
| "存成 mp3" | 直接合成 + 导出 |

## 双 Agent 协同流程

```
                ┌────────────────────────┐
                │  用户输入 / 上一段输出  │
                └────────────┬───────────┘
                             │
            ┌────────────────▼─────────────────┐
            │ Step 1 · Claude 主 Agent         │
            │   - 朗读化重写                    │
            │   - 拆段落 / 标停顿               │
            │   - 跳过 / 叙述化代码块、表格      │
            │   - 输出带 SSML 标记的稿件         │
            └────────────────┬─────────────────┘
                             │ tts_script.ssml
                             ▼
            ┌────────────────▼─────────────────┐
            │ Step 2 · MiMo-V2.5-TTS 子 Agent  │
            │   - 调 MiMo TTS endpoint         │
            │   - 拆 chunk 并行合成（≤500 字/块）│
            │   - 拼接 wav → 导出 mp3          │
            └────────────────┬─────────────────┘
                             │ output.mp3
                             ▼
                       <交付给用户>
```

## Step 1 · 朗读化重写规则（Claude 主 Agent 做）

把书面文字改成"听得懂"的语言：

| 原文（书面） | 改写后（可听） |
|---|---|
| 如表 1 所示，A 项指标提升 12%。 | 第一项指标提升了百分之十二。 |
| 详见 https://example.com/foo | （直接删去链接） |
| ```python\nprint(x)\n``` | （跳过代码块）我们用一行 Python 把 x 打印出来。 |
| 1.5em / 16px / DXA | 单位"em / 像素"等照常念，避免"DXA"这种生僻词 |
| 「他说："你好。"」 | 他说：你好。（去掉嵌套引号） |

**默认每 80 字加一个 `<break time="300ms"/>`**——避免 TTS 听感"赶"。

输出格式（SSML 子集）：

```xml
<speak>
  <p>欢迎收听今天的研究简报。<break time="500ms"/></p>
  <p>第一项议题：百万亿 Token 创造者激励计划。<break time="300ms"/></p>
  <p>这个计划由小米 MiMo 在 2026 年 4 月发起，<break time="200ms"/>面向全球 AI 开发者免费发放 100 万亿 Token。</p>
</speak>
```

## Step 2 · 调用 MiMo-V2.5-TTS

**当前状态**：占位实现，等 Token Plan 到账后切到真实 endpoint。

```python
# scripts/mimo_tts_client.py
DEFAULT_ENDPOINT = "https://platform.xiaomimimo.com/v1/audio/speech"
DEFAULT_MODEL = "mimo-v2.5-tts"
DEFAULT_VOICE = "zh-CN-Yunxi"   # 默认中文男声；可选 zh-CN-Xiaoxiao 等
```

**chunk 策略**（避免长 SSML 失败）：

- 每段 ≤ 500 字
- 段间合成后用 ffmpeg concat（保留 SSML 内置停顿）

```bash
# 合成
python scripts/mimo_tts_client.py tts_script.ssml -o output.mp3 \
    --voice zh-CN-Yunxi --rate 1.0 --max-chunk-chars 500
```

## 模式差异

| 模式 | 加什么 | 删什么 |
|---|---|---|
| 通勤听 | 段落首句小节标题口播 | 引文标记 / 表格 |
| 播客 | 30s 开场 + 关键词标签 + 30s 结尾 | 同上 |
| 配音稿 | 时间戳 / 镜头切分提示 | 同上，且需保留 SSML 精细停顿 |

## 与其他 skill 的协同

- `paper-drafter` 出的研究笔记 → mimo-tts-out 做有声版
- `cn-pr-review` 的评审报告 → mimo-tts-out 做"晨会 5 分钟版"
- `data-grouper` 的质量报告 → mimo-tts-out 做"汇报版"

## MiMo Token 用量预估（每分钟成品音频）

- 文本：约 250 中文字
- TTS 调用：1 次 / chunk（500 字 / chunk → ≈ 1 次 / 2 分钟成品）
- 折合 MiMo Credits：估约 200–400 Credits / 分钟成品（待真实接口确认）

## 反例

- ❌ 把 markdown 直接塞给 TTS（会念出 `*` `#` `-`）
- ❌ 不分 chunk 一次合成 30 分钟（多数 TTS 限 1024 字）
- ❌ 念出 URL（听众无法记下）
- ❌ 念出代码（用"叙述化"替代）
