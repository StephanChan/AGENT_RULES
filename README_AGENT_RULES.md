# README_AGENT_RULES.md — 给 AI 编码助手（Cline）的作业规则

**每次任务开始前先读本文件。** 目标：最短时间给出结果，少验证、少跑命令、不重复已查清的事。

## 0. 第 0 步（强制，先于任何其它动作）
- **第一个响应**就用**一次 `read_files`** 同时读 `README_AGENT_RULES.md` + `.clinerules\00-agent-rules.md`，
  并把本次任务要看的代码文件/区间一并放进去：合并成一次调用，**不额外占批次**（"读规则会多花一批/多花时间"从来不成立）。
- 只认文件**当前文字**；**记忆和上下文摘要不算数**，不许拿"我记得规则"顶替"我读过规则"。
- 不许等用户提醒——用户不该需要提醒；**没读 = 严重违规**：立刻补读，并复核该响应里已发出的改动与规则是否冲突，冲突就回滚重做。
- 若在新任务里仍读不到本文件，把 `CLINE_CUSTOM_INSTRUCTIONS.md` 的三行粘进 Cline 全局 Custom Instructions（一次设置，之后每个任务自动生效）。

## 1. 验证：只做 1 次必要的
- 改完代码：只跑 `python -m py_compile <改动的文件>`（或让用户直接在 IDE 里 Run）。编译通过就回答。
- 默认**不做**：全量 `run_self_test()`、重建 phantom、多组参数对比、反复渲染图、把结论写成脚本再跑一遍。
- 只有用户明确要求"证明/验证/给我数字"时才做一次针对性实测（一次脚本、一次运行，够用就停）。

## 2. 命令行：越少越好
- 每条命令必须直接回答一个问题；禁止探索式连跑。一轮里能合并的用 `;` 合并。
- 本终端 shell integration 常抓不到输出 → 需要看输出时重定向到文件再用 `read_files` 读（这是唯一允许的"多一步"，且不要重复跑）。
- **禁止用 shell 做纯检索**：查代码一律 `search_codebase`，一次调用传**多个** pattern（数组）；读文件一律 `read_files`，一次读多个文件/区间（带 start_line/end_line）。不要 `Get-ChildItem -Recurse`，不要反复 `Select-String` / grep，更不许"第一条没命中→再猜第二条"的连环检索。
- 已知的路径直接读，不要先列目录。

## 3. 时间预算与批量
- 一次回答里工具调用 ≤ 2 批：**1 批"读/改" + 1 批"验证"**；超过就先给结论并问是否继续。
- **独立改动必须同一响应批量发出**：不同文件、或同一文件不重叠区域的多个 editor 调用放进同一个响应并行发；一处改动一个响应算违规（2026-10-07 的"4 张图放一行"任务就因此跑了 8 批、超上限 4 倍）。
- 用户说"N 分钟内"：只做最小改动 + 一次编译/运行，立刻回答，不要在回答前跑完整测试。
- **改前先取锚点**：多处改动前先用一次 `read_files` 把每处锚点的原文**连缩进**读准，避免"锚点不唯一""锚点吃掉缩进"两类返工。
- 同一文件里不重叠的多个 editor 与前一点同义：**同一响应并发发完**（只有"失败重试"允许串行）；单次 editor 文本 ≤6000 字，大脚本先写前半、下一响应追加后半。
- 只有代码改动才需要编译（markdown / 规则文件改完不用跑任何命令）。

## 4. 回答格式
- 顺序：结论 → 改了哪个文件哪几行 → 怎么用 →（可选）一次验证结果。
- 不复述命令日志、不列"我检查了什么"。
- 中文回答；用户说"只答是/否"就只答是或否。

## 5. 本项目已知事实（不要重复调查）
- Stage 1 = `data_processing/RotationalReconstruct.py`（读 C-scan、分段、page match）；Stage 2 = `RotationalVolume.py`（几何/重建）+ `RotationalVolumePanel.py`（界面）。Panel 加载 TIFF 时调用 Stage 1（`rv._load_stage1()` → `load_scan` / `detect_segments`），是一条链，不是两条路。
- 界面入口：`data_processing/RotationalVolumePanel.py`。IDE 运行改文件**末尾**的 `SCAN_FILES` / `TURN_PAGES` / `VOXEL_LATERAL_UM` / `SELF_TEST`（`ide_argv()` 把它们转成 `--file` 等参数）；命令行：`python RotationalVolumePanel.py --file <tif>`。
- "Split the B-line at the fold" 复选框**默认已勾选**：Reconstruct 时自动按 Xc = `axis.Xc` 把 B 线切两段，每段用整圈 360° splat，得到两个 volume → `window.segments[0]["volume"]` / `[1]["volume"]`；API 版 `rv.reconstruct_segments(..., Xc=int(round(axis.Xc)))`。
- 偏心 pierce 时默认（未勾选的）half-turn 面板出现"两块半径不同的半圆"是几何必然（不是 bug）：每个 half-turn 只用 180° 页角，每页是整条 B 线，右翼落在 θ、左翼落在 θ+180。合成体 / runs 正常。**不要再重新证明这一点。**
- 环境：Windows PowerShell；解释器 `python`。
- **姿态/几何参数只有三个名字：P / Xc / d**（2026-10-07 统一）：
  P = 半圈（180°）的 B-line 数（旧名 `half_turn`/`half_turn_blines`/`DEFAULT_HALF_TURN_BLINES`）；
  Xc = 旋转轴在 B-line 上的穿透列/像素（旧名 `centre`/`centre_s`/`centre_column`/`fold`/`fold_px`/`axis.centre[0]`；深度分量是 `Xt`，gauge，不显示）；
  d = 轴到 B-scan 平面的距离（旧名 `offset`/`offset_n_um`，µm 一律写 `d_um`，列写 `d_columns`）。
  全圈长度写 `turn_pages`（**显式 = 2P**，不要再和 P 混用）。几何 JSON 的键是 `P`/`Xc`/`d`/`d_um`，
  旧文件（`half_turn`/`centre`/`offset`）仍可载入（`RotationalVolumePanel.adopt_geometry` 里有兼容表），
  命令行 `--P/--Xc/--d` 与旧写法 `--half-turn/--centre/--offset` 并存（Stage 1 的 seed 是 `--Xc`，兼容旧写法 `--center`）。
  **改名状态（2026-10-07，Xc 族已收尾）**：几何 → 打印 → 面板 → 姿态/重建 → Stage 1 全部统一（`RotationalGeometry.py`、
  `ThreadDnS.py`、`RotationalVolume.py`、`RotationalVolumePanel.py`、`RotationalReconstruct.py`）。
  Stage 1 的对外名字现在是 `mirror_*(data, P, Xc)`、`find_mirror_axis(..., Xc_guess=)`、`mirror_axis_report` 的键
  `Xc`/`Xc_guess`/`Xc_coarse`、`ReconstructionWindow(initial_Xc=)`、`--Xc`（旧名 `center`/`initial_center`/`--center`/
  `axis_px`/`guess_px`/`coarse_axis_px` 在活代码里已无引用；`--center` 仍作为命令行别名保留）。该模块里裸 `centre`
  **不都是** Xc：周期搜索的 lag 窗口中心（`centre = pages / divisor`）和重建网格中心（`centre = (n_grid - 1) / 2.0`）
  另有含义，**不能**整文件替换，动它之前先读锚点。内部局部种子名 `guess`（`_axis_profile`/`_best_axis` 的入参）和派生
  曲线名 `axis_profile` 保留旧写法，它们不是 API；`#` 注释掉的 Stage-2 残块里还有 `center_spin`/`pending_center`/
  `applied_xc` 字样（死代码，要恢复先重写）。几何 JSON 的旧键兼容表在 `RotationalVolumePanel.adopt_geometry`；
  `lag_d_other`/`d_curve` 没有任何读取方，故不需要兼容映射。
