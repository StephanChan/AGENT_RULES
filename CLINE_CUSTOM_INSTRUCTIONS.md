# 粘进 Cline 全局 Custom Instructions 的三行（一次设置，之后**任何目录**的新项目都自动生效）

设置位置：Cline 设置（⚙）→ Custom Instructions（**全局**，不是本工作区）。

**先把 `<RULES_DIR>` 换成绝对路径**——不要写"工作区的 `README_AGENT_RULES.md`"：新项目在别的目录里，工作区里没有这些文件。
建议先建一个**无空格**的稳定路径（仓库以后搬家只改符号链接，全局文本不用动）：

```bash
ln -s "/Users/你的用户名/Documents/Codes/Agent Rules" ~/.agent-rules   # ← 换成你的实际路径
# 于是 <RULES_DIR> = /Users/你的用户名/.agent-rules
```

若某个工作区里已经有自己的 `.clinerules/`（例如本仓库自身），那套会自动加载，本三行只是冗余保险，不冲突。

1. 每个任务的第一步：用一次 `read_files` 读 `<RULES_DIR>/README_AGENT_RULES.md` 与 `<RULES_DIR>/.clinerules/00-agent-rules.md`，
   并把本次任务要读的代码文件/区间合并进这同一次调用（不额外占批次）。没读规则就开始改代码 = 严重违规，先补读再复核已发出的改动。
   若这两个文件读不到（路径变了 / 没权限），**立刻停下告诉我**，不要凭记忆继续。
2. 规则只以文件**当前文字**为准，不认"记忆 / 上下文摘要 / 上一轮的约定"；不许等用户提醒。
   优先级：用户当前轮的明确指令 > 规则文件 > 记忆/历史约定。
3. 其余细节（验证次数、命令数量、批量编辑、回答格式、命名、安全边界、失败与证据、规则维护、交付自检）一律以
   `<RULES_DIR>/README_AGENT_RULES.md` 为准——不要在这里复述，避免与文件版本漂移；
   **项目专属内容**（安装/构建/测试命令、已知坑）以**当前项目自己的 `AGENTS.md`** 为准。

## 两个可选增强（更省事）

- **让它自动加载**：把 `<RULES_DIR>/.clinerules/00-agent-rules.md` 同步进 Cline 的**全局规则目录**（路径在 Rules 面板里可见/创建），
  它会在所有项目自动生效，连"第 0 步读规则"都不依赖 agent 自觉：
  `bash <RULES_DIR>/tools/sync-global.sh <Cline全局规则目录>`（幂等；拒绝覆盖非本工具生成的文件，除非加 `--force`）。
- **跨工具兜底**：把同样的三行放进 `~/.agents/AGENTS.md`——Cline 会读它，Codex / Cursor 等也认这个标准。

给项目写 `AGENTS.md` 时用模板：`<RULES_DIR>/references/project-agents-template.md`。
读不到上面的文件时**不要凭记忆编规则**（README_AGENT_RULES.md 第 8 节）。

在新机器上从零安装（clone → 符号链接 → 全局规则目录 → 验收）：见 `INSTALL.md`。
