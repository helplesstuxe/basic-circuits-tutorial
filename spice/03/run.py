#!/usr/bin/env python3
"""03 电压跟随器：ngspice + TI LM358B 官方模型复核页面数值。从仓库根运行：python spice/03/run.py"""
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

d = ngspice("dc_div.cir", need=["d0", "o0", "d1", "o1", "il1_v", "d2", "o2", "d10k", "d100k", "e1d0", "e1d", "e1o", "e1i_v", "e2d", "e2o", "x2d", "x2o"])
row("p1 开头", "10V 两只10k 分压点空载", 5.0, d["d0"], "V")
row("p1 图03-p1-1", "1k 直接接分压点", 0.83, d["d2"], "V")
row("p1 图03-p1-3 / 第2步", "1k 接跟随器输出：分压点", 5.0, d["d1"], "V")
row("p1 图03-p1-3 / 第2步", "1k 接跟随器输出：负载电压", 5.0, d["o1"], "V")
row("p1 图03-p1-3 / 第2步", "1k 负载电流", 5.0, d["il1_v"] / 1e3 * 1e3, "mA")
row("p1 第3步", "1k 改接分压点：跟随器输出", 0.83, d["o2"], "V")
row("p2 仿真/图03-p2-2", "直接接 10k", 3.33, d["d10k"], "V")
row("p2 仿真/图03-p2-2", "直接接 100k", 4.76, d["d100k"], "V")
row("p2 例1 第1步", "10k/20k 空载", 3.33, d["e1d0"], "V")
row("p2 例1 第2步", "直接接 2k 模块", 0.77, d["e1d"], "V")
row("p2 例1 第3步", "经跟随器 模块电压", 3.33, d["e1o"], "V")
row("p2 例1 第3步", "模块电流", 1.7, d["e1i_v"] / 2e3 * 1e3, "mA")
row("p2 例2", "内阻50k 后级200k 直接接（比例）", 0.8, d["e2d"], "")
row("p3 练习2", "内阻20k 后级20k 直接接（比例）", 0.5, d["x2d"], "")
row("p3 练习2", "经跟随器（比例）", 1.0, d["x2o"], "")

v = ngspice("dc_vin.cir", need=["o5", "o0", "om12", "o25", "o18"])
row("p1 代数", "输入 5 V → 输出", 5.0, v["o5"], "V")
row("p1 代数", "输入 −1.2 V → 输出", -1.2, v["om12"], "V")
row("p2 代数", "输入 2.5 V → 输出", 2.5, v["o25"], "V")
row("p2 A=10万", "5 V 输入时输出与 5 V 之差（绝对值）", 0.05, abs(v["o5"] - 5) * 1e3, "mV", "主要是失调 0.29 mV；万用表量不出来的结论成立")
row("p3 练习1", "1.8 V 输入 3.6k 负载：输出", 1.8, v["o18"], "V")
row("p3 练习1", "负载电流", 0.5, v["o18"] / 3.6e3 * 1e3, "mA")
row("p3 练习3", "33 Ω × 0.5 mA 压降", 16.5, 33 * 0.5e-3 * 1e3, "mV", "欧姆定律，非仿真")
row("p3 §一", "33 Ω × 1 mA 压降", 33, 33 * 1e-3 * 1e3, "mV", "欧姆定律，非仿真")

c = ngspice("t_cap.cir", need=["pk0", "pp0a", "pp0b", "pk10", "pk33", "ts33"])
row("p3 图03-p3-1", "直接接 0.1µF 最高", 0.190, c["pk0"], "V")
row("p3 图03-p3-1", "直接接 55~65µs 峰峰值（仍在振）", None, (c["pp0a"] - c["pp0b"]) * 1e3, "mV", "页面：60 µs 还在振荡")
row("p3 图03-p3-1", "串 10 Ω 最高", 0.140, c["pk10"], "V")
row("p3 图03-p3-1", "串 33 Ω 最高", 0.101, c["pk33"], "V")
row("p3 图03-p3-1", "串 33 Ω 过冲", 1.0, (c["pk33"] / 0.1 - 1) * 100, "%")
row("p3 图03-p3-1", "串 33 Ω 进入 ±2% 时间（阶跃后）", 8.0, (c["ts33"] - 5e-6) * 1e6, "µs")

s = ngspice("t_ss5.cir", need=["omax", "omin", "vfail"])
row("p3 图03-p3-2", "5V 单电源 输出上限", 3.5, s["omax"], "V")
row("p3 图03-p3-2 / 小结", "5V 单电源 输出下限", 0.1, s["omin"], "V")
row("p3 图03-p3-2", "开始跟不上的输入", 3.5, s["vfail"], "V")
e = ngspice("t_ex1ss.cir", need=["o333", "omax2k"])
row("p2 例1 第4步", "5V 单电源 带 2k 输出", 3.33, e["o333"], "V")
row("p2 例1 第4步", "5V 单电源 带 2k 输出上限", 3.5, e["omax2k"], "V")
row("p2 例1 第4步", "余量", 0.17, e["omax2k"] - e["o333"], "V")
x = ngspice("t_ex5.cir", need=["o6", "omax12"])
row("p3 练习5", "12V 单电源 偏置输出", 6.0, x["o6"], "V")
row("p3 练习5", "12V 单电源 输出上限", 10.5, x["omax12"], "V")

r = ngspice("t_sr.cir", need=["a1", "s1", "a3", "s3", "a2", "a8", "ax", "ex", "ak", "ek"])
st = ngspice("t_step.cir", need=["srr", "srf"])
row("p3 §三", "压摆率（大阶跃 上升）", 0.5, st["srr"], "V/µs")
row("p3 §三", "压摆率（大阶跃 下降）", 0.5, st["srf"], "V/µs")
row("p3 §三 代数", "1V 峰 80 kHz 输出峰值", 1.0, r["a1"], "V", "不失真边缘，最大斜率 %.3f V/µs" % r["s1"])
row("p3 §三 代数", "3V 峰 27 kHz 输出峰值", 3.0, r["a3"], "V", "不失真边缘，最大斜率 %.3f V/µs" % r["s3"])
row("p3 练习4", "2V 峰 40 kHz 输出峰值", 2.0, r["a2"], "V")
row("p3 练习4", "100 kHz 峰值 0.8 V 输出峰值", 0.8, r["a8"], "V")
row("补充", "3V 峰 80 kHz（超 fmax）输出峰值", None, r["ax"], "V", "变成三角波，最大偏差 %.2f V" % r["ex"])
row("p1 第4步", "1 kHz 1V 峰 输出峰值", 1.0, r["ak"], "V", "与输入最大偏差 %.2f mV" % (r["ek"] * 1e3))

a = ngspice("ac.cir", need=["g10", "gpk", "bw"])
row("p2 代数", "低频倍数", 0.99999, a["g10"], "")
row("p3 §三 末段", "跟随器带宽", 1.2, a["bw"] / 1e6, "MHz", "模型有 %.1f dB 尖峰" % (20 * math.log10(a["gpk"])))

f1 = ngspice("t_ref.cir", need=["o0", "omin", "omax", "d0", "dmin"])
f2 = ngspice("t_ref2.cir", need=["a0", "amin", "amax"])
row("p2 例3", "基准 2.5 V（缓冲后）", 2.5, f1["o0"], "V")
row("p2 例3", "1mA/1µs 快脉冲：缓冲输出最大跳动", None, (f1["o0"] - f1["omin"]) * 1e3, "mV", "页面：几乎不跳（假设脉冲）")
row("p2 例3", "对照：同一脉冲直接抽 100nF 分压点", None, (f1["d0"] - f1["dmin"]) * 1e3, "mV")
row("p2 例3", "0.1mA/100ns 沿：缓冲输出最大跳动", None, max(f2["a0"] - f2["amin"], f2["amax"] - f2["a0"]) * 1e3, "mV")

report("03 电压跟随器")
