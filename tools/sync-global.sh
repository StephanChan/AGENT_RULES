#!/usr/bin/env bash
# 把这套规则的"自动加载摘要"同步进 Cline 的全局规则目录，并把仓库路径固定成 ~/.agent-rules 符号链接。
#
# 用法：
#   bash tools/sync-global.sh <Cline全局规则目录> [--force]
#   CLINE_GLOBAL_RULES_DIR=<路径> bash tools/sync-global.sh [--force]
#
# 全局规则目录在哪：Cline 的 Rules 面板里能看到/创建它（官方文档没给固定路径，所以本脚本不猜）。
#
# 行为（幂等）：
#   1) 跑 python3 tools/check_rules.py，不通过就中止（机器可判定的项交给工具）；
#   2) 建/检查 ~/.agent-rules → 仓库根 的符号链接（无空格稳定路径，仓库搬家只改它）；
#   3) 把 .clinerules/00-agent-rules.md 复制到全局规则目录，并在首行加"自动生成"标记；
#      目标已存在但不是本工具生成的 → 除非 --force，否则不覆盖。
#
# 退出码：0 成功 / 1 用法错误 / 2 规则检查未通过 / 3 拒绝覆盖
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINK="$HOME/.agent-rules"
SRC="$REPO/.clinerules/00-agent-rules.md"
MARKER="<!-- 由 tools/sync-global.sh 自动同步；请勿在本文件编辑，改 $REPO/.clinerules/00-agent-rules.md -->"
MARKER_GREP="由 tools/sync-global.sh 自动同步"

FORCE=0
DEST_DIR=""
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    -h|--help) sed -n '2,19p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) DEST_DIR="$arg" ;;
  esac
done
[ -n "$DEST_DIR" ] || DEST_DIR="${CLINE_GLOBAL_RULES_DIR:-}"

if [ -z "$DEST_DIR" ]; then
  echo "用法：bash tools/sync-global.sh <Cline全局规则目录> [--force]" >&2
  echo "  全局规则目录 = Cline 的 Rules 面板里显示/创建的那个目录；也可用环境变量 CLINE_GLOBAL_RULES_DIR 传入。" >&2
  exit 1
fi
[ -f "$SRC" ] || { echo "找不到 $SRC" >&2; exit 1; }

echo "[1/3] 检查规则文件"
python3 "$REPO/tools/check_rules.py" || { echo "规则文件检查未通过，先修再同步。" >&2; exit 2; }

echo "[2/3] 固定路径：$LINK → $REPO"
if [ -L "$LINK" ]; then
  if [ "$(readlink "$LINK")" = "$REPO" ]; then
    echo "  已就绪"
  else
    echo "  警告：$LINK 已指向 $(readlink "$LINK")，不是本仓库；要改指向请自行删掉后重跑。" >&2
  fi
elif [ -e "$LINK" ]; then
  echo "  警告：$LINK 已存在且不是符号链接，跳过（没有动它）。" >&2
else
  ln -s "$REPO" "$LINK"
  echo "  已创建"
fi

echo "[3/3] 同步到全局规则目录：$DEST_DIR"
mkdir -p "$DEST_DIR"
DEST="$DEST_DIR/00-agent-rules.md"
if [ -f "$DEST" ] && [ "$FORCE" -ne 1 ]; then
  if ! head -n 1 "$DEST" | grep -q "$MARKER_GREP"; then
    echo "  拒绝覆盖：$DEST 不是本工具生成的（确认要覆盖就加 --force）。" >&2
    exit 3
  fi
fi
{ printf '%s\n' "$MARKER"; cat "$SRC"; } > "$DEST"
echo "  完成：${DEST}（$(wc -l < "$DEST" | tr -d ' ') 行）"

echo
echo "下一步：把 $REPO/CLINE_CUSTOM_INSTRUCTIONS.md 里的三行粘进 Cline 全局 Custom Instructions；"
echo "        其中 <RULES_DIR> 用 ${LINK}（或直接写 ${REPO}）。"
