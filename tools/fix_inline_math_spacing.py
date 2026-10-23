#!/usr/bin/env python3
"""在 Markdown 行内公式 $...$ 两侧补 ASCII 空格，让 GitHub 能识别为公式。

GitHub 规则（经 markdown API 验证）：开 `$` 紧跟在 CJK 字符/全角标点/`-` 等后面时不渲染，
如 `次，$\\omega$` → 纯文本；`次， $\\omega$` → 公式。闭 `$` 后接 CJK 实测无影响，
但为稳妥也在闭 `$` 与紧随的 CJK 字符/全角标点之间补一个空格。

不改动：``` / ~~~ 代码块、$$ 块公式（单行或多行）、行内代码 `...`、`\\$` 转义、
HTML 标签 <...> 内的 $、公式内部文字。开 `$` 前若为 `* _ ( [ { ~` 等 ASCII 起始符
（如 **$n$**、($n$)）不加空格——这些 GitHub 能渲染，加空格反而会破坏加粗。
同一行 $ 个数为奇数时整行跳过并在 stderr 报告。

用法: python tools/fix_inline_math_spacing.py [--check] file.md ...
"""
import re, sys

NO_SPACE_BEFORE_OPEN = set(" \t*_([{~")
CJK = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef\u2018-\u201f\u2026\u2014]")


def dollar_positions(line):
    """返回行内可作为行内公式分隔符的单个 $ 的下标；遇到 $$ 返回 None。"""
    pos, i, n = [], 0, len(line)
    while i < n:
        c = line[i]
        if c == "\\":
            i += 2; continue
        if c == "`":
            j = i
            while j < n and line[j] == "`": j += 1
            tick = line[i:j]
            k = line.find(tick, j)
            # 找到等长闭合反引号才算代码段（简化处理：不检查更长串）
            if k != -1:
                i = k + len(tick); continue
            i = j; continue
        if c == "<":
            m = re.match(r"</?[A-Za-z][^<>]*>", line[i:])
            if m:
                i += m.end(); continue
        if c == "$":
            if i + 1 < n and line[i + 1] == "$":
                return None
            pos.append(i)
        i += 1
    return pos


def fix_line(line, where, warn):
    pos = dollar_positions(line)
    if not pos:
        return line, 0
    if pos is None:
        return line, 0
    if len(pos) % 2:
        warn(f"{where}: odd number of $ ({len(pos)}), skipped")
        return line, 0
    inserts = []  # 插入空格的位置（插在该下标之前）
    for a, b in zip(pos[::2], pos[1::2]):
        inner = line[a + 1:b]
        if not inner or inner[0].isspace() or inner[-1].isspace():
            warn(f"{where}: suspicious pair {line[a:b+1]!r}, skipped line")
            return line, 0
        if a > 0 and line[a - 1] not in NO_SPACE_BEFORE_OPEN:  # 全角空格 U+3000 也不算空格
            inserts.append(a)
        if b + 1 < len(line) and CJK.match(line[b + 1]):
            inserts.append(b + 1)
    for p in sorted(inserts, reverse=True):
        line = line[:p] + " " + line[p:]
    return line, len(inserts)


def fix_text(text, name="<text>", warn=lambda m: print(m, file=sys.stderr)):
    out, total = [], 0
    fence = None      # 当前代码块的围栏串
    in_display = False
    for ln, line in enumerate(text.split("\n"), 1):
        s = line.lstrip()
        if fence:
            if s.startswith(fence[0] * len(fence)) and s.strip(fence[0]) == "":
                fence = None
            out.append(line); continue
        m = re.match(r"(`{3,}|~{3,})", s)
        if m:
            fence = m.group(1); out.append(line); continue
        if in_display:
            if "$$" in line: in_display = False
            out.append(line); continue
        if s.startswith("$$") and line.count("$$") == 1:
            in_display = True; out.append(line); continue
        new, k = fix_line(line, f"{name}:{ln}", warn)
        total += k
        out.append(new)
    return "\n".join(out), total


if __name__ == "__main__":
    args = sys.argv[1:]
    check = "--check" in args
    files = [a for a in args if a != "--check"]
    grand = 0
    for f in files:
        old = open(f, encoding="utf-8").read()
        new, k = fix_text(old, f)
        assert new.replace(" ", "") == old.replace(" ", ""), f
        grand += k
        print(f"{k:4d}  {f}")
        if k and not check:
            open(f, "w", encoding="utf-8").write(new)
    print(f"{grand:4d}  total{' (check only)' if check else ''}")
