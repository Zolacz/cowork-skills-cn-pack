---
name: cn-pr-review
description: 中文 PR / Diff 自动评审。当用户要求评审 Pull Request、code review、看 diff、检查代码改动、做合并前审查、追究改动是否带来回归风险时触发。覆盖 git diff、GitHub PR、本地未提交改动三类输入。输出包含「核心改动摘要 / 潜在风险 / 测试缺口 / 中文 commit message 修订建议」四段式中文评审报告，并在严重问题处给出可粘贴的 inline comment。触发词包括"评审 PR"、"看一下这个 diff"、"code review"、"PR 审查"、"合并前过一遍"、"merge 前看下"、"check this PR"。
license: MIT
---

# cn-pr-review · 中文 PR 评审 Skill

## 设计目标

把"打开 GitHub → 切到 Files → 一行行看 → 写 review comment"这件事，变成「告诉 Claude 一个 PR 编号或 diff，1 分钟内拿到结构化的中文评审报告」的自动化流程。

针对中文工程团队的真实痛点：

- 上游 review 经常只看是否能 merge，**漏掉风险**与 **隐性回归**
- 中文项目的 commit message / 注释不规范，**code review 沦为格式 review**
- 重要 PR 需要 senior 复审，但 senior 时间稀缺

这个 skill 把 senior 的检查清单结构化下来，让 Claude 当一审。

## 触发判断

| 用户说 | 是否触发 |
|---|:---:|
| "评审 PR #123" | ✅ |
| "帮我看看这个 diff" | ✅ |
| "merge 前过一遍" | ✅ |
| "code review 一下" | ✅ |
| "这次改动有什么风险" | ✅ |
| "解释这个文件" | ❌（用 Read 即可） |
| "把这个 PR 合了" | ❌（不做实际 merge） |

## 工作流（长链推理，三段式）

### Step 1 · 收集 diff

按优先级试这几个来源，找到第一个能用的就停：

1. 用户消息里直接贴的 unified diff（最容易）
2. `gh pr diff <number>` —— 当前 git 仓库 + 本地有 GitHub CLI
3. `git diff <base>..<head>` —— 用户提供分支名
4. `git diff` / `git diff --staged` —— 用户说"我刚改的"

收集到的 diff 走 `scripts/diff_summary.py` 做行号标注与分块。

### Step 2 · 分桶分析

把 diff 按文件类型 / 改动性质拆成 4 桶并行审：

```
┌─────────────┬────────────────────────────────────────┐
│ 业务逻辑    │ src/**/*.{js,ts,py,go,rs,java}        │
│ 测试        │ test/** spec/** *_test.* *.test.*      │
│ 配置 / 基础 │ *.yml *.yaml *.toml Dockerfile         │
│ 文档        │ *.md *.mdx                            │
└─────────────┴────────────────────────────────────────┘
```

每桶用一个独立的子任务（Task tool 派发），并行评审。**只回收摘要，不回收完整内容**——避免主上下文污染。

### Step 3 · 输出四段式中文报告

```markdown
## 1️⃣ 核心改动摘要
（3-5 行，纯陈述事实，不做评价）

## 2️⃣ 潜在风险
- 🔴 高：…
- 🟡 中：…
- 🟢 低：…
（按风险等级排序，每条标注文件:行号）

## 3️⃣ 测试缺口
- 改动了 X 但没看到对应 test
- 现有 test 没覆盖 Y 路径

## 4️⃣ Commit Message 修订建议
原文：…
建议：…
（中文规范：动词开头、加 scope、限 50 字内）
```

如果出现🔴风险，**额外**生成 inline comment 草稿（可直接粘贴到 GitHub Files 视图）。

## 关键检查清单（默认逐项过一遍）

中文项目里最容易踩的坑，按命中频率排序：

1. **NPE / 空指针** —— 中文 if/else 经常省略空检查
2. **并发 race** —— 共享变量、map 读写、goroutine/asyncio 漏锁
3. **SQL 注入** —— 字符串拼 SQL、中文项目里的旧代码常见
4. **错误吞掉** —— `except: pass` / `if err != nil { return nil }` / `try { ... } catch {}`
5. **国际化** —— 写死中文字符串、时区写死 +08:00
6. **金额 / 单位** —— float 处理钱、单位混用（元/分/厘）
7. **测试缺口** —— 改动业务逻辑但 test 覆盖不到、或 test 只跑 happy path
8. **依赖膨胀** —— 加了一个新依赖只用了一个工具函数

## 反例：什么不该做

- **不要**改写代码再展示，evaluator 是 reviewer 不是 author
- **不要**给"这里可以更优雅"的 nit 评论，除非它真的影响可读性
- **不要**输出英文 review，除非用户明确要求
- **不要**对未改动的代码做评论（除非它直接被本次改动调用，且新出现风险）

## 脚本

| 脚本 | 作用 |
|---|---|
| `scripts/diff_summary.py` | 把原始 diff 转成「文件 → 改动行数 → 关键 hunk」的结构化摘要 |
| `scripts/risk_classifier.py` | 基于关键词 + AST 模式给每个 hunk 打风险标签 |
| `scripts/commit_lint.py` | 检查 commit message 是否符合中文规范（动词开头、限长、scope） |

## 与其他 skill 的协同

- 评审完后用户说"把建议写进 PR 评论"→ 调用 `gh pr comment` 提示用户确认
- 出现🔴风险且涉及大量代码 → 触发 `paper-drafter` 生成「修复建议技术备忘」
- PR 改了 API 但没改 README → 触发 `doc-code-sync`
