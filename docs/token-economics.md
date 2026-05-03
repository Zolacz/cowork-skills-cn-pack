# Token 经济学：本 pack 的真实消耗预估

> 给 MiMo 评审员、也给我自己一份"为什么需要这么多 Token"的可量化依据。

## 单次调用消耗

按本人使用 Claude Code / Cowork 的真实平均值估算（Anthropic 账单 + Cowork 监控对照）。

| skill | 输入 tokens | 输出 tokens | 工具调用次数 | 单次合计 |
|---|---:|---:|---:|---:|
| cn-pr-review（中等 PR：8 文件 / 300 行 diff） | 35,000 | 6,000 | 25 | ~ 50k |
| paper-drafter（5 篇论文综述） | 600,000 | 30,000 | 80 | ~ 850k |
| doc-code-sync（中型项目全扫） | 80,000 | 8,000 | 40 | ~ 130k |
| data-grouper（5,000 行 csv 智能打标） | 250,000 | 15,000 | 50 | ~ 320k |
| mimo-tts-out（10 分钟播客文本→MP3） | 30,000 | 4,000 | 8 + N×TTS | ~ 40k Claude + N×TTS |

## 一周典型工作量（个人重度开发者）

```
周一  |  cn-pr-review × 3      ≈ 150k
      |  doc-code-sync × 1     ≈ 130k
周二  |  paper-drafter × 1     ≈ 850k     ← 本周综述写作
周三  |  cn-pr-review × 4      ≈ 200k
      |  data-grouper × 1      ≈ 320k     ← 客户名单清洗
周四  |  paper-drafter × 1     ≈ 850k     ← 续读
      |  mimo-tts-out × 2      ≈ 80k + 2×TTS
周五  |  cn-pr-review × 5      ≈ 250k
      |  doc-code-sync × 1     ≈ 130k
周六  |  paper-drafter × 1     ≈ 850k     ← 出综述初稿
      |  mimo-tts-out × 1      ≈ 40k + 1×TTS
周日  |  data-grouper × 1      ≈ 320k
─────────────────────────────────────────
       小计：≈ 4.2M Claude tokens / 周
              + 3 次 TTS × 2,000 字 ≈ 600 Credits
```

按一个月 4 周计算：

```
月度 Claude tokens ≈ 16.8M
月度 MiMo TTS Credits ≈ 2,400
```

## 折算 MiMo Token Plan 档位

注意：MiMo 平台规则是 1 Token = 2 Credits（Pro 模型）。

如果**全部**任务都迁移到 MiMo（最激进假设）：

```
16.8M tokens × 2 Credits/token = 33.6M Credits / 月
```

- Lite (60M Credits) → 撑约 1.8 个月
- Standard (200M Credits) → 撑约 6 个月
- Pro (700M Credits) → 撑约 21 个月
- Max (1.6B Credits) → 撑约 4 年

如果**部分**任务迁移（更现实——把中文 reasoning + TTS + 二审路由到 MiMo，其余仍用主模型）：

```
约 30% 任务迁移 ≈ 10M Credits / 月
+ 集成阶段 v0.3 / v0.4 的 benchmark 跑量 ≈ 50–100M Credits（一次性）
+ TTS 持续调用 ≈ 5,000 Credits / 月
─────────────────────────────────────────
首年总消耗 ≈ 250M – 350M Credits
```

## 申请档位的合理依据

按上述计算：

- **Standard (2 亿) 不够**：会在 v0.3 benchmark 阶段消耗殆尽
- **Pro (7 亿) 刚好**：可以撑过完整路线图 v0.2–v0.4
- **Max (16 亿) 充裕**：留出 v0.5 多模态实验空间 + 反哺生态的二次跑量空间

**申请档位**：Max（理由：完整覆盖路线图 + 反哺空间）；可接受 Pro 起步，按里程碑增发。
