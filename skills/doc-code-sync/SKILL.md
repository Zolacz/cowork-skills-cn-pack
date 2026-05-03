---
name: doc-code-sync
description: 代码 / 文档同步重写。当用户的代码改动了但 README / API 文档 / 注释 / docstring / CHANGELOG 没跟上时触发，自动检测漂移、修订文档、保持示例代码可运行。覆盖 README 漂移、API 接口变更、CLI 参数变化、配置项增删、依赖升级 5 类漂移。触发词包括"文档跟代码同步"、"更新文档"、"README 过时"、"docs out of date"、"sync docs"、"刷新 README"、"更新 API 文档"、"changelog 写一下"、"代码改了但文档没改"。
license: MIT
---

# doc-code-sync · 代码与文档同步 Skill

## 设计目标

绝大多数项目都有这个病：**代码迭代很快，文档永远落后**。
这个 skill 把"对齐"做成可重复执行的流程。

## 触发判断

| 用户说 | 触发模式 |
|---|---|
| "更新一下 README" | 全文档刷新 |
| "我改了 API，文档也帮我改" | API 漂移修复 |
| "把 CHANGELOG 加一行" | CHANGELOG 模式 |
| "看看哪些文档需要更新" | 漂移扫描模式 |

## 5 类典型漂移（覆盖 90% 场景）

| 类型 | 检测线索 | 修复方式 |
|---|---|---|
| **README 漂移** | README 里写的特性、参数、安装方式与代码对不上 | 比对 → 改写对应段落 |
| **API 漂移** | OpenAPI / docstring / 类型注解与实际签名不一致 | 重新生成接口文档块 |
| **CLI 漂移** | `--help` 输出与文档示例不同 | 重抓 `--help` → 替换 doc 里的示例块 |
| **配置漂移** | `config.yaml` 字段与文档表格对不上 | 重写"配置项"小节 |
| **依赖漂移** | `package.json` / `requirements.txt` 改了但安装步骤没改 | 更新安装段 |

## 工作流

### Step 1 · 漂移扫描

调用 `scripts/scan_drift.py`：

- 读所有 `*.md` 文档
- 提取代码块、参数表、安装段
- 对每段尝试在代码里找对应来源
- 输出 drift report：

```
文件                    行    类型        证据
README.md              42    cli         文档里写 --port，代码已重命名为 --listen
README.md              78    install     文档说 npm i，但 package.json 不存在；项目用 pnpm
docs/api.md            120   api         文档说返回 {ok}，代码返回 {success, data}
```

### Step 2 · 分级修复

对扫到的每条 drift：

- **🔴 严重**（用户照文档做就跑不起来）→ 立即修
- **🟡 中等**（参数名变化、字段重命名）→ 修，但保留旧引用作为 deprecation 提示
- **🟢 轻微**（措辞、语言风格）→ 仅在用户要求"全面刷新"时改

### Step 3 · 修订 + 验证

- 对每个段落用 Edit 工具做精确替换（不全文重写——保留原作者风格）
- 修完后再跑一次 scan_drift.py，确认 drift 数下降
- 如果改了 README 的安装段，**额外**在 sandbox 里跑一遍新指令验证

### Step 4 · CHANGELOG 自动更新

如果项目有 `CHANGELOG.md`，按 [Keep a Changelog](https://keepachangelog.com/) 风格追加：

```markdown
## [Unreleased]
### Changed
- 重命名 CLI 参数 `--port` → `--listen` (#123)
### Removed
- 移除已废弃的 `legacy_mode` 配置项 (#125)
```

## 中文文档特有约束

- 表格表头：用中文（"参数 / 类型 / 默认值 / 说明"）
- 代码注释：保持原语言（不要把 English 注释改成中文）
- API 字段说明：中文，但字段名保持英文 + 反引号
- 安装命令：中国镜像源做"备注"——`pip install foo  # 国内可加 -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 脚本

| 脚本 | 作用 |
|---|---|
| `scripts/scan_drift.py` | 扫所有文档，输出 drift report JSON |
| `scripts/refresh_cli_docs.py` | 跑一遍 CLI 的 `--help` 并替换文档里的示例块 |

## 反例

- ❌ 全文重写文档（破坏原作者风格 + 引入新错误）
- ❌ 把英文文档自动翻译成中文（除非用户明确要求）
- ❌ 在没有跑过的情况下声称"已修复并验证"
