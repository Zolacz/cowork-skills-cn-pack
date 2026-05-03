# 示例 2：paper-drafter + mimo-tts-out 串联（论文 → 播客）

## 场景

用户上传 5 篇 RLHF 综述论文，要求"做成 10 分钟可朗读的研究简报"。
这是本 pack 里**真正考验长链推理 + 多 Agent 协同 + 多 Skill 串联**的场景。

## 完整执行轨迹

```
[T+0]    用户：「读完这 5 篇 PDF，做成 10 分钟通勤听的播客脚本+音频」

[T+5s]   Claude 主 Agent（Plan Mode）：
         · 计划：paper-drafter 入库 → 综述写作 → mimo-tts-out 朗读化 → 合成
         · 派 5 个并行子 Agent 处理 5 篇 PDF

[T+30s]  ┌──── 子 Agent 1: 论文 A ────┐
         │  pypdf 读 → extract_paper.py → │
         │  yaml: zhang2024.yaml         │
         └──────────────────────────────┘
         （子 Agent 2-5 并行同步执行，主 Agent 只回收文件名）

[T+90s]  主 Agent 拿到 5 个 yaml 文件，开始写综述：
         · 读 yaml 字段（不读 PDF 全文 — 反污染）
         · 按 templates/literature_review.md 起草
         · 引文用 [zhang2024, li2024] 占位

[T+180s] cite_normalize.py 把占位替换为 [1][2]，并补 GB/T 7714 参考文献节
         产物：draft.md

[T+200s] Claude 决策：mimo-tts-out 触发
         · rewrite_for_speech.py 做朗读化 → script.ssml
         · 长度 ≈ 2,500 字，预估成品 9.5 分钟

[T+220s] mimo_tts_client.py：
         · 拆成 5 个 ≤500 字的 chunk
         · 调 MiMo-V2.5-TTS API（zh-CN-Yunxi 男声，1.0x 语速）
         · 每个 chunk 约 4–6 秒延迟，并行 5 个 → 8 秒拿到 5 段 mp3
         · 拼接 → output.mp3

[T+240s] 交付：
         · draft.md       （文字版综述）
         · script.ssml    （朗读脚本）
         · output.mp3     （9.5 分钟播客）
```

## 工具调用统计

| 阶段 | 工具调用次数 |
|---|---:|
| paper-drafter 入库（5 篇并行）| 25 |
| paper-drafter 综述起草 | 12 |
| cite_normalize | 2 |
| rewrite_for_speech | 1 |
| mimo_tts_client（5 chunks）| 5 |
| **合计** | **45** |

## Token 消耗

- 5 个子 Agent 各 ~ 150k（独立 ctx）→ 750k
- 主 Agent 综述起草 ~ 80k
- TTS 文字 ~ 5k Claude tokens
- MiMo TTS Credits ~ 2,000 Credits（10 分钟成品）
- **Claude 合计：~ 835k tokens**
- **MiMo 合计：~ 2,000 Credits**

## 这段经历演示了什么

1. **多 Agent 并行**：5 个子 Agent 同时处理 5 篇 PDF，主上下文不污染
2. **Skill 串联**：paper-drafter → mimo-tts-out 自动接力
3. **长链推理**：从 PDF 字节流到 mp3 文件，跨越文档解析、语义理解、引文管理、语音合成 4 层抽象
4. **跨模型协作**：Claude 做长文本规划，MiMo 做 TTS 收口
5. **真实 Token 消耗**：单次任务 ~ 835k Claude tokens——这正是为什么需要 MiMo Token Plan
