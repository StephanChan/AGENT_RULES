#!/usr/bin/env python3
"""规则文件硬约束检查：编码、换行符、长度预算、编号连续性。

约定见 README_AGENT_RULES.md 第 11、13 节：
  - 根目录 md：UTF-8 无 BOM + CRLF；`.clinerules/*.md`、`references/*.md`、`tools/*`：UTF-8 无 BOM + LF
  - 长度：README_AGENT_RULES.md <= 150 行，`.clinerules/*.md` <= 60 行，`references/*.md` / INSTALL.md <= 120 行，AGENTS.md <= 30 行
  - `## N.` 章节号与 `N. ` 条目号连续（防止增删规则时把交叉引用写坏）

用法：python3 tools/check_rules.py    # 合规 exit 0；违规打印明细并 exit 1
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRLF, LF, BOM = b"\r\n", b"\n", b"\xef\xbb\xbf"

# (相对路径, 期望换行符, 行数上限或 None)
PINNED = [
    ("README_AGENT_RULES.md", CRLF, 150),
    ("AGENTS.md", CRLF, 30),
    ("CLINE_CUSTOM_INSTRUCTIONS.md", CRLF, None),
    ("INSTALL.md", CRLF, 120),
    (".clinerules/00-agent-rules.md", LF, 60),
]
# 除 PINNED 外一并检查的文件：(glob, 期望换行符, 行数上限或 None)
EXTRA = [
    (".clinerules/*.md", LF, 60),
    ("references/*.md", LF, 120),
    ("tools/*", LF, None),
    (".pre-commit-config.yaml", LF, None),
]

HEADING_RE = re.compile(r"^## (\d+)\.", re.M)   # ## N. 章节号
ITEM_RE = re.compile(r"^(\d+)\. ", re.M)        # N. 条目号


def seq_problems(rel, nums, label, first_ok):
    """编号必须连续，且从 first_ok 之一开始（多个列表各自从 1 重新开始）。"""
    if len(nums) < 2:
        return []
    if nums[0] not in first_ok:
        return ["%s: %s编号应从 %d 开始，实际从 %d 开始" % (rel, label, min(first_ok), nums[0])]
    prev = nums[0]
    for cur in nums[1:]:
        if cur != prev + 1 and cur != 1:
            return ["%s: %s编号不连续（%d 后面是 %d）" % (rel, label, prev, cur)]
        prev = cur
    return []


def check(rel, eol, limit):
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        return ["%s: 文件不存在" % rel]
    raw = open(path, "rb").read()
    problems = []
    if raw[:3] == BOM:
        problems.append("%s: 多了 UTF-8 BOM（应为无 BOM）" % rel)
    crlf = raw.count(CRLF)
    if eol == CRLF and crlf != raw.count(LF):
        problems.append("%s: 换行符应为 CRLF（CRLF=%d, LF=%d）" % (rel, crlf, raw.count(LF)))
    if eol == LF and crlf:
        problems.append("%s: 换行符应为 LF（发现 %d 个 CRLF）" % (rel, crlf))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        problems.append("%s: 不是合法 UTF-8（%s）" % (rel, exc))
        return problems
    if limit is not None and len(text.splitlines()) > limit:
        problems.append("%s: %d 行，超预算 %d 行——先删再加"
                        % (rel, len(text.splitlines()), limit))
    problems += seq_problems(rel, [int(n) for n in HEADING_RE.findall(text)], "章节", (0, 1))
    problems += seq_problems(rel, [int(n) for n in ITEM_RE.findall(text)], "条目", (1,))
    return problems


def main():
    targets = list(PINNED)
    known = {rel for rel, _, _ in PINNED}
    for pattern, eol, limit in EXTRA:
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            rel = os.path.relpath(path, ROOT)
            if rel not in known:
                known.add(rel)
                targets.append((rel, eol, limit))
    problems = []
    for rel, eol, limit in targets:
        problems.extend(check(rel, eol, limit))
    for item in problems:
        print("  - " + item)
    if problems:
        print("规则文件检查未通过（%d 项）。" % len(problems))
        return 1
    print("规则文件检查通过：编码/BOM、换行符、长度预算、编号连续性。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
