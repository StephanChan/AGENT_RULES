# AGENTS.md — 本仓库给 AI 助手的规则

**每个任务开始前先读 `README_AGENT_RULES.md`（唯一完整版）**；`.clinerules/00-agent-rules.md` 由 Cline 自动加载。
下面是**不可省略的硬约束摘要**，其余细节（验证/命令/批量/回答格式/命名/安全/自检）一律以
`README_AGENT_RULES.md` 为准，不要在本文件复述以免版本漂移。

**第 0 步（强制，先于任何其它动作）**：第一个响应就用**一次 `read_files`** 把 `README_AGENT_RULES.md` +
`.clinerules/00-agent-rules.md` 和本次任务要读的代码一起读进来（合并成一次调用，不额外占批次）；
只认文件当前文字，记忆/摘要不算数，不许等用户提醒；**没读 = 严重违规** → 立即补读并复核已发出的改动。

1. **验证只做 1 次**：改完只跑与改动文件类型匹配的一次语法/编译检查（`.py`→`python -m py_compile`；
   `.js`→`node --check`；`.json`→`ConvertFrom-Json`；非代码文件不跑命令）；不做全量 self-test /
   phantom 重建 / 多组对比 / 反复渲染 / 重复重跑。用户明确要数字时才做一次针对性实测。
2. **检索与编辑**：检索一律 `search_codebase`（一次多个 pattern）/ `read_files`（一次多个区间）；
   **禁止用 shell 做纯检索**（`Select-String`、`Get-ChildItem -Recurse`），不许"没命中→再猜一条"连环 grep。
   **独立改动必须在同一响应批量发出**（多个 editor 并行，含同一文件不重叠的区域）；单次 editor 文本 ≤6000 字。
3. **回答格式**：结论 → 改了哪个文件哪几行 → 怎么用 →（可选）一次验证。不复述命令日志、不贴大段已有代码；
   中文回答，说"只答是/否"就只答是或否。
4. **安全与诚实**：不删/不覆盖未确认的文件，不跑 `git push` / `reset --hard`，装依赖或联网前先问；
   不确定的 API/路径先查再写，没跑过的检查不说"已验证通过"；需求有真实分叉时用一次 `ask_question`。

规则完整版见 `README_AGENT_RULES.md`；已被查清的项目事实登记在 `.clinerules/00-agent-rules.md` 的"已知事实"节
（含适用范围），**不要重复调查**。
