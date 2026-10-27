#!/usr/bin/env python3
"""30 仪表放大器与电桥：ngspice + TI LM358B 官方模型复核页面数值。
运行：在仓库根目录执行 python spice/30/run.py（约 4 分钟）。
把 spice/30 单独复制到别处也能跑：只要在仓库根目录下运行，或者旁边有 ../models，脚本都能找到 spice/models。"""
# ---- 通用小工具：调用 ngspice -b，解析 .control 里 echo 出来的 "RES 名字 数值" ----
import subprocess, re, sys, pathlib, math, tempfile
HERE = pathlib.Path(__file__).resolve().parent
ROWS = []

def find_models():
    """按顺序找 spice/models：本目录旁边的 ../models；当前目录及其上级里的 spice/models；本脚本上级里的 spice/models。"""
    cands = [HERE.parent / "models"]
    for base in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents, *HERE.parents]:
        cands.append(base / "spice" / "models")
    for c in cands:
        if (c / "LMx58B_LM2904B.lib").is_file():
            return c.resolve()
    sys.exit("找不到 spice/models/LMx58B_LM2904B.lib：请在仓库根目录运行，或把 spice/models 一起复制过来。")

MODELS = find_models()

def ngspice(cir, need=()):
    """把网表复制到临时目录（.include 改成 spice/models 的绝对路径），batch 运行，返回 {名字: 数值}；缺值或出错就报错退出。
    不在仓库里写任何文件。"""
    text = (HERE / cir).read_text().replace(".include ../models/", f".include {MODELS}/")
    with tempfile.TemporaryDirectory() as td:
        (pathlib.Path(td) / cir).write_text(text)
        if (HERE / ".spiceinit").is_file():
            (pathlib.Path(td) / ".spiceinit").write_text((HERE / ".spiceinit").read_text())
        r = subprocess.run(["ngspice", "-b", cir], cwd=td, capture_output=True, text=True, timeout=900)
    out = r.stdout + r.stderr
    vals = {}
    for k, v in re.findall(r"^RES\s+(\S+)\s+(\S+)", out, re.M):
        try:
            vals[k] = float(v)
        except ValueError:
            vals[k] = float("nan")
    miss = [n for n in need if n not in vals or math.isnan(vals[n])]
    if r.returncode != 0 or miss or re.search(r"(?im)fatal error|error on line|aborted|timestep too small|op failed|failed!\s*$", out):
        print(out[-3000:])
        sys.exit(f"ngspice 运行 {cir} 失败（返回码 {r.returncode}，缺少 {miss}）")
    return vals

def row(loc, item, page, spice, unit="", note=""):
    """记录一行：页面位置 / 项目 / 页面值 / SPICE 值 / 偏差%。page 可为 None（页面只给定性描述）。"""
    dev = None if (page in (None, 0) or spice is None) else (spice - page) / abs(page) * 100
    ROWS.append((loc, item, page, spice, unit, dev, note))

def fmt(x):
    if x is None:
        return "—"
    a = abs(x)
    if a == 0:
        return "0"
    if a >= 1000 or a < 0.01:
        return f"{x:.4g}"
    return f"{x:.4g}"

def report(title):
    print(f"==== {title}：页面值 / SPICE 值 / 偏差% ====")
    w = max(len(r[0]) + len(r[1]) for r in ROWS) + 3
    for loc, item, page, spice, unit, dev, note in ROWS:
        d = "   —  " if dev is None else f"{dev:+7.2f}%"
        print(f"{(loc + ' ' + item):<{w}} 页面 {fmt(page):>9} {unit:<3} | SPICE {fmt(spice):>9} {unit:<3} | {d}  {note}")
    print(f"共 {len(ROWS)} 项。")
# ---- 工具结束 ----

# ---- 1. 差模：电桥 + 三运放仪表放大器（page2 例题、page4 第 9～12 步）----
d = ngspice("lab_dc.cir", need=[f"{p}_{k}" for p in ("vd", "vo", "vm", "a1", "a2") for k in range(4)] + ["vd_g1", "vo_g1"])
row("p4 第 3 步", "中点参考 V_MID", 4.5, d["vm_0"], "V")
row("p4 第 8 步", "RX 短接时 Vo−V_MID（零点）", None, d["vo_0"] * 1e3, "mV", "模型失调 ×21")
for k, rx, vd, vo, a1, a2, loc in [(1, 100, 22.388, 0.4701, 4.2761, 4.7463, "p2 §二 / p4 第 9 步"),
                                   (2, 220, 48.961, 1.0282, 4.0104, 5.0386, "p4 第 10 步"),
                                   (3, 470, 103.32, 2.1698, 3.4668, 5.6365, "p2 例2 / p4 第 11 步")]:
    row(loc, f"RX={rx} Ω 电桥差压", vd, d[f"vd_{k}"] * 1e3, "mV")
    row(loc, f"RX={rx} Ω A1 输出", a1, d[f"a1_{k}"], "V")
    row(loc, f"RX={rx} Ω A2 输出", a2, d[f"a2_{k}"], "V")
    row(loc, f"RX={rx} Ω Vo−V_MID", vo, d[f"vo_{k}"], "V")
    row(loc, f"RX={rx} Ω Vo−V_MID 减零点", vo, d[f"vo_{k}"] - d["vo_0"], "V")
row("p4 第 12 步", "拔掉 RG（倍数 1）Vo−V_MID", 0.1033, d["vo_g1"], "V", "RX=470 Ω")

# ---- 2. 共模：J2 短接两中点，RC 4.7k 拉低/抬高（page4 第 13～16 步）----
c = ngspice("lab_cm.cir", need=[f"{p}_c{k}" for p in ("lo", "hi", "vcl", "vch") for k in range(4)])
row("p4 第 13 步", "RC 接 0 V 时共模", 2.938, c["vcl_c0"], "V")
row("p4 第 14 步", "RC 接 V+ 时共模", 6.062, c["vch_c0"], "V")
dvcm = c["vch_c0"] - c["vcl_c0"]
row("p4 第 14 步", "差分级电阻全等：ΔVo", 0.1, (c["hi_c0"] - c["lo_c0"]) * 1e3, "mV", "页面写'约 0.1 mV'")
for k, name, page in [(1, "R10 串 100 Ω：ΔVo", 15.5), (2, "四只 5% 最坏：ΔVo", 297.6), (3, "R10 串 100 Ω 且拔 RG：ΔVo", 15.5)]:
    row("p4 第 15～16 步 / 图 30-p4-5", name, page, (c[f"hi_c{k}"] - c[f"lo_c{k}"]) * 1e3, "mV")
for k, name, g, page in [(1, "R10 串 100 Ω 整机 CMRR", 21, 72.5), (3, "同上拔 RG 整机 CMRR", 1, 46.1)]:
    acm = (c[f"hi_c{k}"] - c[f"lo_c{k}"]) / dvcm
    row("p2 §三 / p4 第 15～16 步", name, page, 20 * math.log10(g / abs(acm)), "dB")

# ---- 3. 差分级失配的共模倍数（理想运放，page2 §三、图 30-p2-3、图 30-p3-3）----
m = ngspice("mt061.cir", need=[f"{p}_{k}" for p in ("acm", "adm") for k in range(4)])
for k, name, page, page_ina in [(0, "一只 +0.1%", 66.0, 92.5), (1, "一只 +1%", 46.1, 72.5), (2, "四只 1% 最坏", 34.1, 60.5), (3, "四只 5% 最坏", 20.4, 46.9)]:
    row("p2 §三 图 30-p2-3", f"{name} 差分级 CMRR", page, 20 * math.log10(1 / abs(m[f"acm_{k}"])), "dB", "差模按设计值 1")
    row("p2 §三 图 30-p2-3", f"{name} 仪表放大器 CMRR", page_ina, 20 * math.log10(21 / abs(m[f"acm_{k}"])), "dB")
    row("补充", f"{name} 差分级实际差模倍数", None, m[f"adm_{k}"], "", "说明'按设计值 1'的影响")
row("p3 练习 2", "四只 1% 最坏 1 V 共模 → 输出", 19.8, abs(m["acm_2"]) * 1e3, "mV")

# ---- 4. 中点参考 V_MID：只分压 vs 分压 + 跟随器，挂 1 kΩ（page2 §五 / 图 30-p2-5、page4 第 3 步）----
v = ngspice("vground.cir", need=["vda", "vm"])
row("p2 §五 / p4 第 3 步", "只用分压挂 1 kΩ", 0.75, v["vda"], "V")
row("p2 §五 / p4 第 3 步", "分压 + 跟随器挂 1 kΩ：V_MID", 4.5, v["vm"], "V")

# ---- 5. 典型错误：单运放差分直接接电桥（page1 §三、图 30-p1-3）----
s = ngspice("single_diff.cir", need=["s100", "s0", "s1"])
row("p1 §三 图 30-p1-3", "单运放差分 RX=100 Ω 输出", 149.2, s["s100"] * 1e3, "mV", "设计以为 223.9 mV")
row("p1 §三 图 30-p1-3", "四只 1% 最坏，共模 +1.5625 V：ΔVo", 44.6, (s["s1"] - s["s0"]) * 1e3, "mV")

# ---- 6. page2 例1：RG = 2 kΩ，RX = 220 Ω ----
e = ngspice("ex1_rg2k.cir", need=["a1", "a2", "vo"])
row("p2 例1", "RG=2k A1 输出", 4.2552, e["a1"], "V")
row("p2 例1", "RG=2k A2 输出", 4.7938, e["a2"], "V")
row("p2 例1", "RG=2k Vo−V_MID", 0.5386, e["vo"], "V", "含模型失调 ×11")

report("30 仪表放大器与电桥")
