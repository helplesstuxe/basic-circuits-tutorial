#!/usr/bin/env python3
"""检查 Markdown 里的配图是否合规（notes/AUTHOR_GUIDE.md「图的规则」的可自动检查部分）：
  1. 每个 ![…](路径) 指向的本地文件存在，且是 PNG（禁止 ASCII 图、Mermaid：```mermaid 块直接 FAIL）；
  2. 每张 PNG < 200 KB；
  3. 图号格式「图 NN-pX-k」与文件夹、页码一致（如 05-inverting-amp/page2.md 里只能出现「图 05-p2-k」），
     同一页里 k 从 1 起连续、不重复定义；
  4. 每个图号至少出现两次（图前引导句或图后讲解里提到 + 图注本身）。
用法：python tools/check_figs.py [文件 …]（不给参数 = 所有 P*/NN-*/page*.md）。退出码 0 = 通过。
"""
import glob, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)[^)]*\)|<img[^>]*src=\"([^\"]+)\"")
NUM = re.compile(r"图\s*([P0-9]{2})-p([1-9])-(\d+)")


def check(path):
    rel = os.path.relpath(os.path.abspath(path), ROOT)
    txt = open(path, encoding="utf-8").read()
    probs = []
    if re.search(r"^```\s*mermaid", txt, flags=re.M):
        probs.append("含 ```mermaid 块（禁止，改成 Python 画的 PNG）")
    for m in IMG.finditer(txt):
        src = m.group(1) or m.group(2)
        if src.startswith("http"):
            continue
        f = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(path)), src))
        if not os.path.exists(f):
            probs.append(f"图片不存在：{src}")
        elif not f.lower().endswith(".png"):
            probs.append(f"不是 PNG：{src}")
        elif os.path.getsize(f) >= 200 * 1024:
            probs.append(f"超过 200 KB：{src}（{os.path.getsize(f) // 1024} KB）")
    folder = os.path.basename(os.path.dirname(os.path.abspath(path)))
    pm = re.match(r"page(\d)\.md$", os.path.basename(path))
    nums = NUM.findall(txt)
    cnt = Counter(nums)
    if pm:
        node = folder.split("-")[0]
        for nn, px, k in cnt:
            if nn != node or px != pm.group(1):
                probs.append(f"图号 图 {nn}-p{px}-{k} 与本页（{node} page{pm.group(1)}）不符")
        ks = sorted({int(k) for nn, px, k in cnt if nn == node and px == pm.group(1)})
        if ks and ks != list(range(1, len(ks) + 1)):
            probs.append(f"图号不连续：{ks}")
        for key, c in cnt.items():
            if c < 2:
                probs.append(f"图 {key[0]}-p{key[1]}-{key[2]} 只出现 1 次（缺引导句或图后讲解）")
    n_img = len(IMG.findall(txt))
    print(f"{'OK  ' if not probs else 'FAIL'} 图 {n_img:2d}  {rel}")
    for p in probs:
        print("      " + p)
    return not probs


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "[P0-9]*-*", "page*.md")))
    if not files:
        print("（还没有 page*.md）"); sys.exit(0)
    ok = [check(f) for f in files]
    sys.exit(0 if all(ok) else 1)
