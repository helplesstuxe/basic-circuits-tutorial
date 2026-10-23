"""ngspice 小工具（每个节点目录各放一份，内容相同）。

用法：在仓库根目录运行 `python spice/NN/run.py`。
- run(cir, params) 把 spice/NN/xxx.cir 复制到临时目录（附带 .spiceinit: ngbehavior=psa，
  以便读入 PSpice 格式的厂家模型），把 `.param NAME=...` 行替换成 params 里的值，
  把 `.include ../models/...` 改成绝对路径，然后 `ngspice -b` 运行。
- netlist 的 .control 段里用  echo "RESULT name $&var"  输出结果；本工具解析这些行。
- .control 段里可写 @NAME@ 占位符，默认值用 "*@def NAME=value" 注释行给出。
- wrdata 写出的文件留在返回的临时目录里，可用 load_wrdata 读取。
"""
import json, pathlib, re, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
MODELS = (HERE.parent / "models").resolve()
NGSPICE = shutil.which("ngspice") or "/usr/bin/ngspice"
ROWS = []
TMPS = []
import atexit
atexit.register(lambda: [shutil.rmtree(d, ignore_errors=True) for d in TMPS])


def run(cir, params=None, keep=False):
    src = (HERE / cir).read_text(encoding="utf-8")
    params = params or {}
    def sub_param(m):      # 一行 .param 里可以有多个 NAME=value，逐个替换
        body = re.sub(r"(\w+)\s*=\s*(\{[^}]*\}|\S+)",
                      lambda k: f"{k.group(1)}={params[k.group(1)]}" if k.group(1) in params else k.group(0),
                      m.group(2))
        return m.group(1) + body
    src = re.sub(r"^(\.param\s+)(.*)$", sub_param, src, flags=re.M | re.I)
    # 文本占位符 @NAME@（用于 .control 段，.param 在那里不可用）；默认值写在 "*@def NAME=value" 行
    defs = dict(re.findall(r"^\*@def\s+(\w+)=(\S+)", src, flags=re.M))
    defs.update({k: v for k, v in params.items()})
    for k, v in defs.items():
        src = src.replace(f"@{k}@", str(v))
    src = re.sub(r"\.\./models/", str(MODELS) + "/", src)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="spice_"))
    TMPS.append(tmp)
    (tmp / ".spiceinit").write_text("set ngbehavior=psa\nset num_threads=1\n")
    (tmp / cir).write_text(src, encoding="utf-8")
    p = subprocess.run([NGSPICE, "-b", cir], cwd=tmp, capture_output=True, text=True, timeout=900)
    out = p.stdout + p.stderr
    res = {}
    for line in out.splitlines():
        m = re.match(r"^\s*RESULT\s+(\S+)\s+(\S+)", line)
        if m:
            try:
                res[m.group(1)] = float(m.group(2))
            except ValueError:
                res[m.group(1)] = float("nan")
    if p.returncode != 0 or not res:
        sys.stderr.write(out[-3000:])
        raise RuntimeError(f"ngspice failed on {cir} (rc={p.returncode})")
    res["_dir"] = str(tmp)
    if not keep:
        pass
    return res


def load_wrdata(path):
    import numpy as np
    d = np.loadtxt(path)
    return d


def check(where, desc, page, spice, unit="", note="", v=None, tol=10.0):
    """记录并打印一行：页面值 / SPICE 值 / 偏差%（page 为 None 时只列 SPICE 值）。
    v：结论（"✅" "⚠️" "❌" 或 "ℹ️" 仅供参考）；不给时偏差在 tol% 内记 ✅，否则记 "?"（待人工判定）。"""
    spice = float(spice)
    if page is None or page == 0:
        dev = None
    else:
        dev = (spice - page) / abs(page) * 100
    if v is None:
        if page is None:
            v = "ℹ️"
        elif dev is None:
            v = "✅" if abs(spice) < 0.1 else "?"
        else:
            v = "✅" if abs(dev) <= tol else "?"
    ROWS.append(dict(where=where, desc=desc, page=page, spice=spice, unit=unit, dev=dev, note=note, v=v))
    ps = "—" if page is None else f"{page:.4g}"
    ds = "—" if dev is None else f"{dev:+.1f}%"
    print(f"{where:<22s} {desc:<34s} 页面 {ps:>9s} {unit:<4s} SPICE {spice:>10.4g} {unit:<4s} 偏差 {ds:>8s} {v} {note}")


def save(name="results.json"):
    (HERE / name).write_text(json.dumps(ROWS, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n共 {len(ROWS)} 项；结果已写入 {HERE.name}/{name}")
