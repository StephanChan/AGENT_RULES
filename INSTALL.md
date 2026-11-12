# INSTALL.md — 在新机器上启用这套规则

一次配置，之后**任何目录**的新项目都自动生效。前置：`git` 与 `python3`（脚本与检查器只用标准库）。

## 0. 前提：改动要先提交

本仓库是规则的**唯一真源**：改规则只改这里，提交推送后其它机器 `git pull` 即可。
**没提交的改动，新机器 clone 不到。**

## 1. 克隆到固定路径

```bash
git clone <本仓库地址> ~/agent-rules      # 路径不要带空格、不要藏在深层目录
cd ~/agent-rules
python3 tools/check_rules.py             # 应输出"规则文件检查通过"
```

## 2. 建稳定路径 + 同步到 Cline 全局规则目录

```bash
bash tools/sync-global.sh "<Cline 全局规则目录>"
```

- `<Cline 全局规则目录>` 的路径在 Cline 的 **Rules 面板**里可见/创建（官方文档没给固定路径，脚本**不猜**）。
- 脚本做三件事：① 跑 `check_rules.py`（不过就中止）② 建 `~/.agent-rules → 仓库根` 符号链接 ③ 把
  `.clinerules/00-agent-rules.md` 复制进全局规则目录（首行带"自动生成"标记；目标不是本工具生成的则拒绝覆盖，除非 `--force`）。
- 结果：`<RULES_DIR> = <你的家目录>/.agent-rules`。
- Windows 上没有 `bash`：用等价脚本 `tools\sync-global.ps1`（同样三步、同样退出码），见文末「Windows 补充」。

## 3. 配置 Cline 全局 Custom Instructions

设置（⚙）→ **Custom Instructions（全局，不是本工作区）** → 粘贴 `CLINE_CUSTOM_INSTRUCTIONS.md` 里的三行，
把其中的 `<RULES_DIR>` 换成 `<你的家目录>/.agent-rules`。

## 4. 验收

1. `python3 tools/check_rules.py` → 通过；
2. 在**别的目录**开一个项目、提一个任务：agent 第一步就去读 `<RULES_DIR>/README_AGENT_RULES.md` = 生效；
3. 它不读 → 回看第 3 步是否保存在**全局**而不是工作区。

## 5. 日常维护

```bash
cd ~/agent-rules && git pull && bash tools/sync-global.sh "<Cline 全局规则目录>"
```

- 改规则：改 `README_AGENT_RULES.md`（唯一完整版）→ 同步镜像 `.clinerules/00-agent-rules.md`、`AGENTS.md` →
  跑 `python3 tools/check_rules.py` → 提交。
- 项目要留事实（命令、坑）：照 `references/project-agents-template.md` 在该项目里写 `AGENTS.md`。
- 可选跨工具兜底：把三行放进 `~/.agents/AGENTS.md`（Cline 会读，Codex / Cursor 等也认）。

## Windows 补充（没有 `bash` 时）

`tools\sync-global.ps1` 是 `tools/sync-global.sh` 的等价实现：同样跑 `check_rules.py`、建 `~/.agent-rules` 稳定路径、
复制 `.clinerules/00-agent-rules.md` 到全局规则目录（首行加"自动生成"标记、拒绝覆盖非本工具生成的文件，除非 `-Force`），
退出码同为 `0/1/2/3`。前置：Python 3 在 `PATH` 上；Anaconda 没进 `PATH` 时用 `-PythonPath` 显式指定。

```powershell
cd D:\Codes\AGENT_RULES                                  # 仓库放在无空格、不深的固定路径
& 'D:\Anaconda\python.exe' .\tools\check_rules.py        # 应输出"规则文件检查通过"
powershell -ExecutionPolicy Bypass -File .\tools\sync-global.ps1 `
  -RulesDir '<Cline 全局规则目录>' -PythonPath 'D:\Anaconda\python.exe'
```

- WIN 上的 `~/.agent-rules` 是**目录联接（Junction）**，不需要管理员权限；验收：
  `Get-Item $HOME\.agent-rules | Select-Object LinkType,Target`。
- `<Cline 全局规则目录>` 仍是 Rules 面板里那个目录（实测依据：`C:\Users\<你>\Documents\Cline\` 下已有 `Hooks`、`Workflows`，
  同级 `Rules` 即全局规则目录；以面板显示为准）。
- Custom Instructions 三行里的 `<RULES_DIR>` 写 `C:\Users\<你>\.agent-rules`。
- 日常维护：仓库更新后重跑上面第二条命令（幂等）。

## 三条边界（避免踩坑）

- 全局规则目录里那份是**复制**出去的，不是符号链接（Cline 是否跟随符号链接**未验证**）——所以改完规则要再跑一次同步脚本（`sync-global.sh`；Windows 为 `sync-global.ps1`）。
- 项目专属内容**不进**本仓库（见 `README_AGENT_RULES.md` 第 13 节）。
- 别把长规则直接粘进全局 Custom Instructions：那里每轮都进上下文，太长会被忽略。
