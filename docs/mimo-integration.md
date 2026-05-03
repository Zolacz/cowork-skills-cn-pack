# MiMo 集成路线图

> 描述 cowork-skills-cn-pack 接入小米 MiMo-V2.5 系列模型的分阶段计划。

## 现状（v0.1）

- **mimo-tts-out**：唯一已对接 MiMo 的 skill。
  - 客户端实现：`skills/mimo-tts-out/scripts/mimo_tts_client.py`
  - Endpoint：`https://platform.xiaomimimo.com/v1/audio/speech`
  - 当前模式：**dry-run**（写 transcript，不发请求；等 Token Plan 到账切到真实合成）

## v0.2 · TTS 真实链路（拿到 Token Plan 后 7 天内完成）

- 设置 `MIMO_API_KEY` 环境变量
- 跑一遍样例稿 → 拿到第一段 mp3
- 把延迟、成本、音质数据写进 `examples/mimo-tts-bench.md`
- 打通 paper-drafter → mimo-tts-out 的端到端样例

**预期 Token 用量**：每分钟成品音频约 200–400 MiMo Credits
**测试覆盖**：合成 30 分钟样例 ≈ 6,000–12,000 Credits

## v0.3 · `mimo-cn-reason`（中文 reasoning 路由）

新增 skill：把"中文 reasoning 子任务"路由到 MiMo-V2.5-Pro，主 Agent 仍是 Claude。

适用场景：

- 中文古诗 / 文言文理解
- 中文歧义消解
- 中文文档摘要 + 关键句抽取
- 中文 instruction-following

**协议**：

```
Claude 主 Agent
  → 检测到任务是"中文重逻辑型"
  → 派 mimo-cn-reason 子 Agent
       → 调 MiMo-V2.5-Pro chat completion
       → 回收摘要
  → Claude 整合并输出
```

**Benchmark 计划**：

```
| 任务类型               | Claude Sonnet 4.6 | MiMo-V2.5-Pro | DeepSeek-V4 |
|----------------------|------------------|---------------|-------------|
| 中文长文摘要（10k 字）   |                  |               |             |
| 中文 SQL 翻译          |                  |               |             |
| 古诗文理解             |                  |               |             |
| 中文歧义消解            |                  |               |             |
```

数据集来源：CMRC、CLUE、自建 200 题。

## v0.4 · `mimo-code-review`（双审制 PR 评审）

为 cn-pr-review 增加"二审"能力：

- 一审：Claude 主审，输出标准评审报告
- 二审：MiMo-V2.5-Pro 看一审报告 + 原 diff，挑战或补充
- 主 Agent 合并两份评审，标注「双审一致 / 不一致」

**价值假设**：双模型双审能显著降低高危项漏检率（待 benchmark 验证）。

## v0.5 · 多模态 skill 扩展

利用 MiMo 的多模态能力（图像 + 文本），新增：

- `mimo-screenshot-debug`：贴上屏幕截图自动定位 bug
- `mimo-chart-explainer`：扫一眼图就解读趋势

## Token 预算

按 Token Plan 各档位评估：

| 档位 | Credits | 可支撑路线图 |
|---|---:|---|
| Lite (6,000 万) | 60M | v0.2 完成 |
| Standard (2 亿) | 200M | v0.2 + v0.3 部分 benchmark |
| Pro (7 亿) | 700M | v0.2 + v0.3 完整 + v0.4 试点 |
| **Max (16 亿)** | **1.6B** | **v0.2 + v0.3 + v0.4 + v0.5 完整路线** |

申请 Max 档的明确依据：完整覆盖 4 个集成阶段 + 持续 benchmark + 公开报告。

## 反哺生态

每完成一个集成阶段，会以下列形式反哺 MiMo Orbit 生态：

1. GitHub 仓库公开（MIT），所有 issue、PR、commits 可追溯
2. 每个阶段写一篇技术博客（中文 + 英文），发布到知乎 / X
3. Benchmark 结果发布到独立 leaderboard 页
4. 把 mimo-tts-out / mimo-cn-reason / mimo-code-review 提交到 Cowork / Claude Code 的官方 skill 市场，扩大 MiMo 在 Claude 用户里的分发面
