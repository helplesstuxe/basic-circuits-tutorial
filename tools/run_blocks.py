#!/usr/bin/env python3
"""抽取 Markdown 中的 ```python 代码块，逐块在临时目录里真的运行一遍（MPLBACKEND=Agg）。
  PASS  退出码 0；FAIL  退出码非 0（打印 stderr 末尾）；
  SKIP  含 '____'（学生填空）、首行是 '# 不运行'（示意片段）或 '# 未经运行验证' 的块。
代码块在临时目录运行，图片写到临时目录，不会污染仓库；需要 code/figs/ 里的共享模块时，代码块可以
`import figstyle`/`import schem`——本工具把 code/ 和 code/figs/ 加进 PYTHONPATH。
用法:
  python tools/run_blocks.py 05-inverting-amp/page2.md ...      # 指定文件
  python tools/run_blocks.py                                     # 不给参数 = 所有 P*/NN-*/page*.md
  python tools/run_blocks.py --scripts [code/01_*.py ...]        # 在仓库根目录运行仿真/画图脚本（默认 code/*.py 和 code/figs/*_figs.py）
请用教程的虚拟环境运行：/workspace/circuits-venv/bin/python tools/run_blocks.py …
退出码：0 = 没有 FAIL；1 = 至少一个 FAIL。
"""
import glob, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = {**os.environ, "MPLBACKEND": "Agg",
       "PYTHONPATH": os.pathsep.join([os.path.join(ROOT, "code"), os.path.join(ROOT, "code", "figs"),
                                       os.environ.get("PYTHONPATH", "")])}


def blocks(path, lang="python"):
    txt = open(path, encoding="utf-8").read()
    return re.findall(r"^[ \t]*```" + lang + r"[ \t]*\n(.*?)^[ \t]*```", txt, flags=re.S | re.M)


def run(cmd, cwd, label):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300, env=ENV)
    ok = r.returncode == 0
    print(f"{'PASS' if ok else 'FAIL'} {label}  out: {r.stdout.strip()[-200:]!r}")
    if not ok:
        print(r.stderr[-1500:])
    return ok


def main():
    args = sys.argv[1:]
    fail = npass = nskip = 0
    if args and args[0] == "--scripts":
        files = args[1:] or sorted(glob.glob(os.path.join(ROOT, "code", "[0-9P]*.py")) +
                                   glob.glob(os.path.join(ROOT, "code", "figs", "*_figs.py")))
        for f in files:
            ok = run([sys.executable, os.path.abspath(f)], ROOT, os.path.relpath(os.path.abspath(f), ROOT))
            fail += not ok; npass += ok
    else:
        files = args or sorted(glob.glob(os.path.join(ROOT, "[P0-9]*-*", "page*.md")))
        for p in files:
            rel = os.path.relpath(os.path.abspath(p), ROOT)
            for i, code in enumerate(blocks(p), 1):
                head = code.lstrip().split("\n", 1)[0]
                if "____" in code or head.startswith("# 不运行") or head.startswith("# 未经运行验证"):
                    print(f"SKIP {rel} block{i} (填空/示意/未经运行验证)"); nskip += 1; continue
                with tempfile.TemporaryDirectory() as d:
                    f = os.path.join(d, "blk.py"); open(f, "w", encoding="utf-8").write(code)
                    ok = run([sys.executable, f], d, f"{rel} block{i}")
                    fail += not ok; npass += ok
    print(f"PASS {npass}  SKIP {nskip}  FAIL {fail}", file=sys.stderr)
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
