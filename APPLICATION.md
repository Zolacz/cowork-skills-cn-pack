# 申请材料 · Xiaomi MiMo Orbit 百万亿 Token 创造者激励计划

> 私人备忘 — 提交申请时直接照抄。

---

## 第 04 题答案（建议字数 600 字左右，1200 字符上限内）

我是个人独立开发者，过去 6 个月把 Anthropic 的 Claude Code（CLI 编码 Agent）和 Cowork 模式（桌面端文件 + MCP Agent）作为日常主力开发工具，**过去 30 天 Anthropic 账单约 $___**（详见附件账单截图），日均稳定消耗百万级 Token。

**项目名称**：cowork-skills-cn-pack — 面向中文开发者的 Cowork × Claude Code 生产力 Skill 套装（GitHub 公开仓库 + MIT 许可）。

**核心痛点**：作为单兵作战的全栈开发者，我需要在代码工程、信息调研、文档生产、数据治理之间高频切换。市面通用 LLM 处理不了真正的长链推理任务——一旦任务超过 20 轮工具调用、跨 10+ 文件改动，就会出现上下文污染、幻觉漂移、状态丢失。这个项目把我每天用 Claude Code/Cowork 沉淀下来的 5 个真实工作流抽象成可一键加载的 skill 集合。

**核心逻辑流（长链推理 + 多 Agent 协同）**：项目采用三层 Agent 架构。

1. **主 Agent（Claude Plan Mode）**：负责任务拆解、Skill 路由、上下文聚合，绝不直接处理大对象；
2. **子 Agent 池（Task Tool）**：并行派发 Explore / Plan / general-purpose 等专精子 Agent，每个独立上下文，只回收摘要；
3. **5 个 Skill**：cn-pr-review（中文 PR 评审）、paper-drafter（论文起草）、doc-code-sync（代码文档同步）、data-grouper（数据治理）、mimo-tts-out（MiMo TTS 收口）。

**典型长链场景**：用户上传 5 篇论文要求"做成 10 分钟可听播客"。系统派 5 个子 Agent 并行入库（每个独立 ctx 不污染主上下文），主 Agent 基于 5 份 yaml 摘要起草综述，cite_normalize 自动补参考文献节，rewrite_for_speech 做朗读化重写，最后 mimo-tts-out 调 MiMo-V2.5-TTS 拆 chunk 并行合成 mp3。**单次任务 45 轮工具调用、跨 10+ 文件、消耗约 83 万 Claude Token + 2,000 MiMo Credits**。

**为什么需要 MiMo Token Plan**：mimo-tts-out 已经把 MiMo-V2.5-TTS 的客户端工程做完（dry-run 模式跑通），只差 API Key 接通真实 endpoint。下一阶段路线图明确：(1) v0.2 完成 TTS 真实链路 benchmark；(2) v0.3 新增 mimo-cn-reason，把中文 reasoning 子任务路由到 MiMo-V2.5-Pro，输出 Claude × MiMo × DeepSeek 在中文 agentic claw 任务上的对比报告；(3) v0.4 新增 mimo-code-review 形成"双审制 PR 评审"。所有阶段产物**完整开源到 GitHub，反哺 MiMo Orbit 生态**。

---

## 第 05 题 · 证明材料清单

按推荐优先级上传（限 5 个）：

| 文件 | 类型 | 说明 |
|---|---|---|
| 1. anthropic_bill_30d.png | png | 过去 30 天 Anthropic 账单截图（**必传**——最硬证据） |
| 2. github_repo_screenshot.png | png | cowork-skills-cn-pack 仓库首页（README + 文件树） |
| 3. claude_code_long_chain.png | png | Claude Code 一次长链任务的终端截图（plan + 工具调用序列） |
| 4. cowork_skill_loaded.png | png | Cowork 里 skills 已加载、被自动触发的截图 |
| 5. paper_to_podcast_demo.mp4 | mp4 | examples/02 场景的实录（PDF → mp3，可选）|

最少传 1+2+3 即可。**1 是 must-have**，没有就退一档。

---

## 关键备忘

- 申请邮箱必须与 platform.xiaomimimo.com 注册邮箱一致（本人是 zolaalo688@gmail.com）
- 未收到通过邮件 → 3 天后重新提交
- 拿到 Token Plan 后立刻：
  1. `export MIMO_API_KEY=...`
  2. 跑 examples/02 的端到端 demo
  3. 把首段成品 mp3 放到 GitHub release，写一条申请通过 + 集成实录的博客
- 反哺生态计划：每完成 v0.2 / v0.3 / v0.4 阶段都发一篇技术博客 + leaderboard 页

---

## GitHub 仓库结构（已就位）

```
cowork-skills-cn-pack/
├── .claude-plugin/plugin.json
├── README.md                    # 项目主页
├── LICENSE                      # MIT
├── install.sh                   # 一键安装到本地 Cowork / Claude Code
├── APPLICATION.md               # 本文（不进 git）
├── docs/
│   ├── architecture.md          # 三层 Agent 架构详解
│   ├── mimo-integration.md      # MiMo 路线图 v0.2 → v0.5
│   └── token-economics.md       # Token 消耗模型与档位推导
├── skills/
│   ├── cn-pr-review/
│   │   ├── SKILL.md
│   │   └── scripts/{diff_summary,risk_classifier,commit_lint}.py  # 已自检 ✓
│   ├── paper-drafter/
│   │   ├── SKILL.md
│   │   └── scripts/{extract_paper,cite_normalize}.py
│   ├── doc-code-sync/
│   │   ├── SKILL.md
│   │   └── scripts/scan_drift.py
│   ├── data-grouper/
│   │   ├── SKILL.md
│   │   └── scripts/{profile_table,normalize_cn}.py             # 已自检 ✓
│   └── mimo-tts-out/
│       ├── SKILL.md
│       └── scripts/{rewrite_for_speech,mimo_tts_client}.py     # 已自检 ✓
└── examples/
    ├── 01-cn-pr-review.md       # 实战示例 + Token 统计
    └── 02-paper-to-podcast.md   # 跨 Skill 串联 + 多 Agent 协同
```
