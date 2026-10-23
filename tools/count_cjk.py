#!/usr/bin/env python3
"""统计 Markdown 正文的汉字数（硬标准：每页 ≥ 500 汉字，不含代码和公式）。
排除：代码块 ```…```、块公式 $$…$$、行内公式 $…$、行内代码 `…`、图片 ![替代文字](路径) 的替代文字、HTML 注释 <!-- -->。
用法:
  python tools/count_cjk.py 01-inverting-amp/page1.md [更多文件...]
  python tools/count_cjk.py                # 不给参数 = 仓库里所有 P*/NN-*/page*.md
  python tools/count_cjk.py --min 500 …    # 改下限（默认 500）
退出码：0 = 全部达标；1 = 至少一页不足（LOW）。
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def body_cjk(text: str) -> int:
    text = re.sub(r"```.*?```", "", text, flags=re.S)        # 代码块
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)       # HTML 注释
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)      # 块公式
    text = re.sub(r"(?<!\\)\$[^$\n]+?\$", "", text)           # 行内公式
    text = re.sub(r"`[^`\n]*`", "", text)                     # 行内代码
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)          # 图片替代文字（图注要写在图下方的正文里）
    return len(re.findall(r"[\u4e00-\u9fff]", text))


if __name__ == "__main__":
    args = sys.argv[1:]
    lo = 500
    if "--min" in args:
        i = args.index("--min"); lo = int(args[i + 1]); del args[i:i + 2]
    files = args or sorted(glob.glob(os.path.join(ROOT, "[P0-9]*-*", "page*.md")))
    if not files:
        print("（还没有 page*.md）"); sys.exit(0)
    bad = 0
    for p in files:
        n = body_cjk(open(p, encoding="utf-8").read())
        flag = "OK " if n >= lo else "LOW"
        bad += n < lo
        print(f"{flag} {n:5d}  {os.path.relpath(p, ROOT) if os.path.isabs(p) else p}")
    print(f"{len(files) - bad}/{len(files)} 页达标（下限 {lo} 汉字）", file=sys.stderr)
    sys.exit(1 if bad else 0)
