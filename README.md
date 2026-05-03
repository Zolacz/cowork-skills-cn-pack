# cowork-skills-cn-pack

> 面向中文开发者的 Cowork × Claude Code 生产力 Skill 套装。
> 5 个开箱即用的本地化 skill，覆盖 PR 评审、论文起草、文档同步、数据治理、TTS 输出。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills: 5](https://img.shields.io/badge/Skills-5-blue.svg)]()
[![Cowork](https://img.shields.io/badge/Cowork-compatible-purple.svg)]()
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-orange.svg)]()

## 这是什么

把日常用 Claude Code / Cowork 模式跑下来沉淀的 5 个真实工作流，**抽象成可一键加载的 skill 集合**。每个 skill 都对应一个我每天都在跑的具体场景，不是 demo，是产线。

| Skill | 一句话定位 | 触发场景 |
|---|---|---|
| `cn-pr-review` | 中文 PR / Diff 自动评审 | 上游 review 漏检 / 中文项目改动审查 |
| `paper-drafter` | 论文 / PDF 阅读 + 起草助手 | 综述写作、文献追踪、研究笔记 |
| `doc-code-sync` | 代码改动 → 文档同步重写 | README / API 文档老化、漂移 |
| `data-grouper` | Excel / CSV 智能分类 + 质量报告 | 杂乱表格清洗、客户名单去重 |
| `mimo-tts-out` | 把 Claude 的输出转成可朗读语音脚本 | 长文阅读 / 通勤听报告 / 视频配音底稿 |

## 设计原则

1. **真实驱动**：每个 skill 都来自我每天 Claude Code / Cowork 重度使用中沉淀的真实痛点，不是「想象中可能有用」。
2. **中文友好**：默认中文上下文、中文输出格式、贴合中国开发者的工程习惯（commit message 中文、文档中文优先、单位人民币）。
3. **长链推理**：skill 内部明确支持 plan mode → 子任务并行 → 闭环验证三段式工作流。
4. **多模型可插拔**：`mimo-tts-out` 是模型路由的范式样板——主推小米 MiMo-V2.5 的 TTS 能力，未来可扩展到 reasoning / 多模态全栈双模型协同。

## 项目结构

```
cowork-skills-cn-pack/
├── .claude-plugin/
│   └── plugin.json              # plugin manifest
├── skills/
│   ├── cn-pr-review/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── paper-drafter/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── doc-code-sync/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── data-grouper/
│   │   ├── SKILL.md
│   │   └── scripts/
│   └── mimo-tts-out/
│       ├── SKILL.md
│       └── scripts/
├── docs/
│   ├── architecture.md          # 架构图与协作模式
│   ├── token-economics.md       # Token 消耗模型
│   └── mimo-integration.md      # MiMo 接入路线图
├── examples/                    # 使用样例（输入 → 输出）
├── install.sh                   # 一键安装到本地 Cowork / Claude Code
├── LICENSE
└── README.md
```

## 安装

```bash
# 克隆仓库到本地
git clone https://github.com/Zolacz/cowork-skills-cn-pack.git
cd cowork-skills-cn-pack

# 一键安装（自动检测 Cowork 还是 Claude Code 环境）
bash install.sh
```

或者直接把 `skills/` 下的任一文件夹拷贝到你 Cowork / Claude Code 的 skills 目录即可。

## 使用样例

```bash
# 在 Claude Code / Cowork 里直接说：
> 帮我评审 PR #123 的 diff
# → 自动激活 cn-pr-review

> 把 docs/ 下所有 README 跟 src/ 里的最新代码同步一下
# → 自动激活 doc-code-sync

> 把这份 8 万字的研究报告，做成 15 分钟可朗读的语音脚本
# → 自动激活 mimo-tts-out（调用 MiMo-V2.5-TTS）
```

详见 `examples/` 目录。

## 与 MiMo 的协同

`mimo-tts-out` 是这个 pack 里第一个对接小米 MiMo 生态的 skill，定位是「主模型 (Claude) 做长链推理与文本生成 → MiMo TTS 做最后一公里语音合成」的多 Agent 协同范式。

后续路线（详见 `docs/mimo-integration.md`）：

- **mimo-tts-out**：MiMo-V2.5-TTS 接入 ✅（占位 SDK 已就位，等 Token Plan 到账后切换到真实 endpoint）
- **mimo-cn-reason**（路线图）：把中文 reasoning 子任务路由到 MiMo-V2.5-Pro，对比延迟/质量
- **mimo-code-review**（路线图）：让 MiMo 做 PR 二轮意见，与 Claude 主审形成「双审制」

## 贡献

欢迎 issue & PR。中文 / English 都可以。

## License

MIT © 2026 Zola
