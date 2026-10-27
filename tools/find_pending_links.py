#!/usr/bin/env python3
"""找出 Markdown 里指向「还没发布的节点目录」的相对链接（发布前处理死链用，做法见 notes/pending-links.md）。

用法：python tools/find_pending_links.py [--ref origin/main] 文件或目录 ...
  「已发布」= 该节点目录在 --ref（默认 HEAD）的提交里存在，且没有被本次一起列在命令行上。
  目录 = 本批要发布的节点目录，它们之间的互链不算死链。
输出每处：文件:行号、原链接 Markdown；有死链时退出码 1。只读，不改文件。
"""
import argparse, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK = re.compile(r"\[([^\]]*)\]\(((?:\.\./)+(\d\d-[A-Za-z0-9-]+)/[^)\s]*)\)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("paths", nargs="+")
    a = ap.parse_args()
    tree = subprocess.run(["git", "-C", ROOT, "ls-tree", "--name-only", a.ref], capture_output=True, text=True, check=True).stdout.split()
    files, batch = [], set()
    for p in a.paths:
        if os.path.isdir(p):
            batch.add(os.path.basename(os.path.normpath(p)))
            files += [os.path.join(dp, f) for dp, _, fs in os.walk(p) for f in sorted(fs) if f.endswith(".md")]
        else:
            files.append(p)
    published = set(tree) | batch
    n = 0
    for f in sorted(files):
        for i, line in enumerate(open(f, encoding="utf-8"), 1):
            for m in LINK.finditer(line):
                if m.group(3) not in published:
                    n += 1
                    print(f"{f}:{i}: {m.group(0)}")
    print(f"pending={n}")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
