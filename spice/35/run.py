#!/usr/bin/env python3
"""35 程控增益与 AGC：ngspice + TI LM358（LMx58_LM2904 模型）复核页面数值。CD4051 用「理想开关 + R_on」代替（仓库里还没有它的模型）。从仓库根运行：python spice/35/run.py"""
# ---- 通用小工具：调用 ngspice -b，解析 .control 里 echo 出来的 "RES 名字 数值" ----
import subprocess, re, sys, pathlib, math
HERE = pathlib.Path(__file__).resolve().parent
ROWS = []

def ngspice(cir, need=()):
    """在本目录下以 batch 模式运行 cir，返回 {名字: 数值}；缺值或出错就报错退出。"""
    r = subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=900)
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

RG = [100e3, 24e3, 11e3, 5.1e3, 2e3, 1e3]
VIN = [1.0, 0.4, 0.2, 0.1, 0.05, 0.03]
G = {}
for k in range(6):
    d = ngspice(f"dc_g{k}.cir", need=[f"v{q}{t}" for q in "omx" for t in "snhw"])
    for t, ron in (("n", 0), ("h", 125), ("s", 470), ("w", 1050)):
        G[(k, t)] = d[f"vo{t}"] / d[f"vm{t}"]          # 用反相端电压当分母：扣掉失调
        page = 1 + 100e3 / (RG[k] + ron)
        row(f"p2 档位表 X{k}", f"R_on={ron} Ω 时 G", page, G[(k, t)])
    if k in (0, 5):
        ron_meas = (d["vms"] - d["vxs"]) / (d["vxs"] / RG[k])
        row(f"p4 §六 X{k}", "由 ②③ 反算 R_on", 470, ron_meas, "Ω")
        row(f"p4 §六 X{k}", "① 输出", None, d["vos"], "V", f"输入 {VIN[k]} V，含模型失调")
        row(f"p4 §六 X{k}", "② 反相端 − 输入（失调）", None, (d["vms"] - VIN[k]) * 1e3, "mV", "页面：毫伏级，LM358 手册最大 ±7 mV")
row("p2 §二", "G=101 档串 125 Ω 误差", -11.0, (G[(5, "h")] / G[(5, "n")] - 1) * 100, "%")
row("p2 §二", "G=101 档串 470 Ω 误差", -31.7, (G[(5, "s")] / G[(5, "n")] - 1) * 100, "%")
row("p2 §二", "G=101 档串 1050 Ω（5 V 最大）误差", -50.7, (G[(5, "w")] / G[(5, "n")] - 1) * 100, "%")
d5 = ngspice("dc_g5.cir", need=["vos"])
row("p4 §六", "X5 档 V_out/V_in（不扣失调）", None, d5["vos"] / 0.03, "", "比 V_out/V(②) 大，差在失调")
k = ngspice("dc_kelvin.cir", need=["vok", "vmk", "vt1", "voz", "vokw", "vmkw", "vt1w"])
row("p2 §三 抽头接法", "最底抽头 G = 101.1k/1k", 101.1, k["vok"] / k["vt1"], "")
row("p2 §三 抽头接法", "最底抽头 V_out/V(反相端)（扣失调）", 101.1, k["vok"] / k["vmk"], "")
row("p2 §三 抽头接法", "开关取 1050 Ω 时 V_out/V(反相端)", 101.1, k["vokw"] / k["vmkw"], "", "最坏 R_on 也不进增益")
row("p2 §三 抽头接法", "1050 Ω 与 470 Ω 输出之差", None, (k["vokw"] / k["vok"] - 1) * 100, "%")
row("p2 §三 抽头接法", "偏置电流造成的链比偏差", None, (k["vok"] / k["vt1"] / 101.1 - 1) * 100, "%", "I_B≈20 nA 流进 1k 底电阻（链电流 20 µA）")
row("p2 §三 抽头接法", "开关两端压差（偏置电流 × 470 Ω）", None, (k["vt1"] - k["vmk"]) * 1e6, "µV", "页面：几乎为 0")
row("p3 故障表", "零输入时 G≈69 档的输出", None, k["voz"], "V", "= 失调 × 69")
c = ngspice("clip.cir", need=["vmax", "vknee"])
row("p2/p4 满量程", "LM358 5 V 供电输出上限", 3.8, c["vmax"], "V", "页面取满量程 3.0 V 留余量")
a = ngspice("ac.cir", need=["g0a", "g0b", "g0c", "bwa", "bwb", "bwc"])
row("p3 §一 带宽", "G=101（理想开关）−3 dB", 9.6e3, a["bwa"], "Hz")
row("p3 §一 带宽", "G≈69（串 470 Ω）−3 dB", 14.1e3, a["bwb"], "Hz")
row("p3 §一 带宽", "G≈2 −3 dB", 0.94e6, a["bwc"], "Hz")
row("p3 §一 带宽", "G=101 时 增益×带宽", 0.97e6, a["g0a"] * a["bwa"], "Hz", "LM358 手册 0.7 MHz、LM358B 1.2 MHz")
p = ngspice("t_peak.cir", need=["pa55", "pb55", "pbmin", "pamin", "pbend", "paend", "tdec"])
row("p2 §四 图35-p2-6", "单二极管 1 V 输入的保持值", 0.53, p["pa55"], "V")
row("p2 §四 图35-p2-6", "单二极管 0.5 V 输入的保持值", 0.12, p["paend"], "V")
row("p2 §四 图35-p2-6", "精密检波 1 V 输入的保持值", 1.00, p["pb55"], "V")
row("p2 §四 图35-p2-6", "精密检波 保持值最低点", 0.97, p["pbmin"], "V")
row("p2 §四 图35-p2-6", "精密检波 0.5 V 输入的保持值", 0.51, p["pbend"], "V")
row("p2 §四 图35-p2-6", "降到 0.52 V 用时（τ=0.1 s 估 65 ms）", 65e-3, p["tdec"], "s")
report("35 程控增益与 AGC")
