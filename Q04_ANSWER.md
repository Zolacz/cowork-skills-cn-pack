我是个人独立开发者，把 Anthropic Claude Code（CLI 编码 Agent）与 Cowork 模式（桌面端 + MCP Agent）作为日常主力工具，日均稳定消耗百万级 Token。基于这套真实使用，我把沉淀的 5 个工作流抽象成开源项目 cowork-skills-cn-pack（GitHub MIT 许可，5 个 SKILL.md + 10 个 Python 脚本，全部通过自检并实测产出真实结果）。

【核心痛点】作为单兵全栈开发者，每天在代码工程、信息调研、文档生产、数据治理间高频切换。通用 LLM 撑不起真正的长链推理：任务一旦超过 20 轮工具调用、跨 10+ 文件改动，就会上下文污染、幻觉漂移、状态丢失。本项目把「该用哪个 skill / 派哪个子 Agent / 结果怎么合并」做成可重复的工程方案。

【三层 Agent 架构（核心逻辑流）】
1. 主 Agent（Claude Plan Mode）：任务拆解、Skill 路由、上下文聚合，绝不直接处理大对象；
2. 子 Agent 池（Task Tool）：并行派发 Explore / Plan / general 等专精子 Agent，每个独立 ctx，只回收摘要；
3. 五个 Skill：cn-pr-review（中文 PR 评审）、paper-drafter（论文起草）、doc-code-sync（代码文档同步）、data-grouper（数据治理）、mimo-tts-out（MiMo TTS 收口）。

【典型长链场景】用户上传 5 篇论文做 10 分钟可听播客：系统派 5 个子 Agent 并行入库（独立 ctx 不污染主上下文），主 Agent 基于 YAML 摘要起草综述、自动补 GB/T 7714 参考文献，rewrite_for_speech 做朗读化，mimo-tts-out 拆 chunk 调 MiMo-V2.5-TTS 并行合成 mp3。单次 45 轮工具调用、跨 10+ 文件、约 83 万 Claude Token + 2,000 MiMo Credits。

【为什么需要 MiMo Token Plan】mimo-tts-out 客户端已完成（dry-run 跑通，缺 API Key 接通真实 endpoint）。明确路线：v0.2 完成 TTS 真实链路 benchmark；v0.3 新增 mimo-cn-reason 把中文 reasoning 路由到 MiMo-V2.5-Pro，输出 Claude × MiMo × DeepSeek 在中文 agentic claw 任务的对比报告；v0.4 新增 mimo-code-review 形成「双审制 PR 评审」。所有产物完整开源、反哺 Orbit 生态。
