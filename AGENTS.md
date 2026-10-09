# AGENTS.md — 本仓库给 AI 助手的规则

**每个任务开始前先读 `README_AGENT_RULES.md`（完整版）**；下面是同一条规则的简版，必须遵守：

**第 0 步（强制，先于任何其它动作）**：第一个响应就用**一次 `read_files`** 把 `README_AGENT_RULES.md` +
`.clinerules/00-agent-rules.md` 和本次任务要读的代码一起读进来（合并成一次调用，不额外占批次）；
只认文件当前文字，记忆/摘要不算数，不许等用户提醒；**没读 = 严重违规** → 立即补读并复核已发出的改动。

1. 验证只做 1 次必要的：改完只 `python -m py_compile <文件>`；不做全量 self-test / phantom 重建 /
   多组对比 / 反复渲染 / 重复重跑。用户明确要数字时才做一次针对性实测。
2. 命令最少化：一条命令回答一个问题，能合并用 `;`；看输出就重定向到文件再 `read_files`。
   检索一律 `search_codebase`（一次多个 pattern）/ `read_files`（一次多个区间）；**禁止用 shell 做
   纯检索**（`Select-String`、`Get-ChildItem -Recurse`），不许"没命中→再猜一条"连环 grep。
3. 一轮回答工具调用 ≤ 2 批（= 读/改 + 验证）；用户说"N 分钟内"→ 最小改动 + 一次编译，立刻回答。
   **独立改动必须同一响应批量发出**（多个 editor 并行），禁止一处改动一个响应；markdown 不用编译。
   动手前先用一次 `read_files` 把锚点原文（含缩进）读准；单次 editor 文本 ≤6000 字，超了先写前半、下一响应追加。
4. 回答顺序：结论 → 改了哪个文件哪几行 → 怎么用 →（可选）一次验证。不复述日志。中文回答；
   说"只答是/否"就只答是或否。
5. 已知事实不要重复调查：Stage 1 = `data_processing/RotationalReconstruct.py`；Stage 2 =
   `RotationalVolume.py` + `RotationalVolumePanel.py`（panel 加载 TIFF 时调 Stage 1）。
   IDE 运行改 `RotationalVolumePanel.py` 末尾的 `SCAN_FILES`。"Split the B-line at the fold"
   默认勾选 → `window.segments[0/1]["volume"]` = 按 Xc 切两段、各 360° 的 volume。
   偏心 pierce 时未勾选面板的"双半圆"是几何必然，不要再证明。
6. 参数命名只有 `P`/`Xc`/`d`（见 `README_AGENT_RULES.md` 第 5 节）；旧名（`half_turn`/`centre`/`offset`/
   `axis_px`/`guess_px`/`initial_center`/`--center` 等）只作兼容别名。
