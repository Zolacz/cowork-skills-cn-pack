# 示例 1：cn-pr-review 实战

## 输入

用户在 Cowork 里说：

> 帮我评审下面这个 diff，重点看安全性。

```diff
diff --git a/src/api.py b/src/api.py
@@ -10,6 +10,9 @@ def get_user(uid):
     conn = db.connect()
-    sql = "SELECT * FROM users WHERE id = " + str(uid)
+    sql = "SELECT * FROM users WHERE id = ?"
     try:
-        return conn.execute(sql).fetchone()
+        return conn.execute(sql, (uid,)).fetchone()
     except:
         pass
+    api_key = "sk-1234567890ABCDEF"
+    print("debug:", api_key)
```

## Skill 执行轨迹

```
1. cn-pr-review 触发
2. diff_summary.py 解析 → 1 file, +4/-2
3. risk_classifier.py 扫描 → 发现 1 处 high 风险
   · hardcoded_secret @ src/api.py: api_key = "sk-1234567890ABCDEF"
4. Claude 主 Agent 整合 → 输出四段式中文评审
```

## 输出

```markdown
## 1️⃣ 核心改动摘要
- 修复了 `get_user` 中的 SQL 拼接漏洞，改用参数化查询。
- 但本次提交同时引入了一处硬编码 API Key 与一个 debug print。

## 2️⃣ 潜在风险
- 🔴 高 · `src/api.py:14`：硬编码 API Key `"sk-1234567890ABCDEF"`，**严禁合并**。
  Key 必须放进环境变量或密钥管理服务，且这个 commit 一旦合并到公开仓库即视为泄露，
  需要立即撤销并重新签发。
- 🔴 高 · `src/api.py:15`：debug 用的 `print(api_key)` 把 secret 写进了日志。
- 🟡 中 · `src/api.py:13`：`except: pass` 静默吞所有异常。SQL 修复后这里仍未改，
  建议至少改成 `except Exception as e: logger.exception(e)`。

## 3️⃣ 测试缺口
- 修复了 SQL 注入但未看到对应的 test case（建议加一个 `test_get_user_with_evil_uid`）
- 没有针对硬编码 secret 的 lint/CI 拦截规则

## 4️⃣ Commit Message 修订建议
原文：（未提供）
建议：`fix(api): 修复 get_user SQL 注入并撤销硬编码 key`

---

### 可粘贴 Inline Comment 草稿

> **Line 14**: 这一行硬编码了 API Key，**严禁合入主干**。
> 请：1) 立即撤销并重新签发该 key；2) 改为 `os.getenv("XXX_API_KEY")`；
> 3) 在 `.gitleaks.toml` / pre-commit 加一条 secret 检测规则避免再犯。
```

## 真实 Token 消耗

- 输入：4.2k tokens（diff + skill metadata）
- 工具调用：5 次（diff_summary → risk_classifier → 3 次 Read 上下文文件）
- 输出：1.8k tokens（评审报告）
- **合计：~ 38k tokens**
