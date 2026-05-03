# 架构与协作模式

> 这份文档解释 cowork-skills-cn-pack 的整体设计哲学：怎么让 5 个 skill 在同一个会话里协同、又互不污染。

## 三层 Agent 架构

```
┌────────────────────────────────────────────────────────────────┐
│                  ░░░ 用户输入 / 上下文 ░░░                      │
└──────────────────────────────┬─────────────────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │          Claude 主 Agent（Plan Mode）        │
        │   · 任务拆解  · 工作流编排  · 上下文聚合       │
        └──────┬───────────────────────────────┬──────┘
               │                               │
       ┌───────▼───────┐               ┌───────▼───────┐
       │  子 Agent 池   │               │   Skill 库     │
       │  (Task Tool)  │               │  (本 pack)    │
       └───────┬───────┘               └───────┬───────┘
               │                               │
   ┌───────────┼─────────┐         ┌───────────┼───────────┬──────────┐
   ▼           ▼         ▼         ▼           ▼           ▼          ▼
 Explore   Plan-agent general   cn-pr-     paper-     doc-code-   data-     mimo-tts
                                review     drafter    sync        grouper   -out
                                                                              │
                                                                      ┌───────▼───────┐
                                                                      │ MiMo-V2.5-TTS │
                                                                      │   (子 Agent)   │
                                                                      └───────────────┘
```

### 第 1 层：主 Agent

负责长链推理、任务拆解、上下文聚合。它**不直接执行 skill 内部逻辑**——它只做「该用哪个 skill / 该派哪个子 Agent / 各方结果怎么合并」的决策。

### 第 2 层：子 Agent 池

通过 Task tool 派发并行子任务。**关键设计**：每个子 Agent 跑在独立上下文里，只回收一段摘要；主上下文不会被原始 PDF / 大型 diff / 全表数据污染。

### 第 3 层：Skills

5 个 skill 各自封装一类领域知识。Skill 之间是**横向协同**关系：

| 触发 skill | 常见后续 skill |
|---|---|
| `cn-pr-review` | `doc-code-sync`（如果 PR 改了 API） |
| `paper-drafter` | `mimo-tts-out`（把综述做成有声版） |
| `doc-code-sync` | `cn-pr-review`（修订作为新 PR） |
| `data-grouper` | `paper-drafter`（用清洗后数据写报告） |
| `mimo-tts-out` | — （管线终点） |

## 长链推理实例：研究简报 → 有声播客

一个真实场景，演示三层架构怎么协同：

```
1. 用户：把 5 篇 RLHF 论文做成 10 分钟可听的研究简报。

2. 主 Agent 决策：需要 paper-drafter + mimo-tts-out 两个 skill。

3. paper-drafter 触发，主 Agent 派 5 个子 Agent 并行：
   - Sub-Agent 1: 读论文 A, 输出 zhang2024.yaml
   - Sub-Agent 2: 读论文 B, 输出 li2024.yaml
   - Sub-Agent 3: 读论文 C, 输出 wang2024.yaml
   - Sub-Agent 4: 读论文 D, 输出 chen2025.yaml
   - Sub-Agent 5: 读论文 E, 输出 sun2025.yaml
   主 Agent 只回收文件名，不读 PDF 全文。

4. 主 Agent 基于 5 份 yaml 写综述草稿（Step 3 of paper-drafter）。

5. 综述草稿 → mimo-tts-out 触发：
   - Step 1: rewrite_for_speech.py 做朗读化
   - Step 2: mimo_tts_client.py 调 MiMo-V2.5-TTS 合成

6. 用户拿到：
   - draft.md（文字版）
   - draft.ssml（朗读脚本）
   - draft.mp3（10 分钟播客）
```

整个流程涉及：

- **5 个并行子 Agent 的派发与回收**
- **2 个 skill 串联**
- **1 个跨模型调用（Claude → MiMo-TTS）**
- **30+ 轮工具调用**
- **预估 80–150 万 Token 消耗**

这是典型的「单兵开发者无法手工完成、但 AI Agent 可以闭环交付」的工作流。

## 反污染设计

主 Agent 上下文有限。本 pack 的所有 skill 都遵循下列原则避免上下文污染：

1. **大对象不进主 ctx**：PDF 全文、长 diff、全表 csv 都在子 Agent 里处理，主 Agent 只见摘要
2. **结果存盘 而非传值**：paper-drafter 把每篇论文存成 yaml 在 `.papers/`，cite_normalize.py 后续读盘检索
3. **失败前置**：每个 skill 的 SKILL.md 前置写明触发条件 + 反例，主 Agent 决策时即可避免错误激活

## 成本结构

| skill | 平均一次调用 Token 消耗 | 调用频率（个人开发者）|
|---|---:|---|
| cn-pr-review | 30–80k | 2–5 次/天 |
| paper-drafter | 200–1000k（多篇） | 1–3 次/周 |
| doc-code-sync | 50–150k | 1–2 次/周 |
| data-grouper | 100–500k（按行数） | 1–2 次/周 |
| mimo-tts-out | 20–60k（Claude 改写）+ MiMo TTS Credits | 1 次/天 |

按重度个人开发者使用频率估算，**月度 Token 消耗约 8000 万 – 1.5 亿**——这正是申请 MiMo Token Plan Max 档（16 亿 Credits）的合理依据。
