#!/usr/bin/env python3
"""13 桥式整流（只仿低压次级）：ngspice + Diodes 1N4007（替代 1N4001）/ Nexperia 1N4148 / TI TL072 官方模型复核页面数值。从仓库根运行：python spice/13/run.py"""
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

b = ngspice("t_bridge.cir", need=["pk0", "mx", "mn", "av", "ipk", "inr", "tr", "tf", "r470", "r1000", "r4700", "r10000"])
row("p1 图13-p1-2", "无电容输出峰值", 15.4, b["pk0"], "V")
row("p1 图13-p1-3", "2200 µF 最高", 14.67, b["mx"], "V")
row("p1 图13-p1-3", "2200 µF 最低", 14.00, b["mn"], "V")
row("p1/p2 §5", "纹波（峰峰）", 0.67, b["mx"] - b["mn"], "V")
row("p2 §5", "平均输出", 14.34, b["av"], "V")
row("p2 §5", "负载电流", 191, b["av"] / 75 * 1e3, "mA")
row("p1/p2 图13-p2-2", "每半周导通时间（门限 5 mA）", 2.42, (b["tf"] - b["tr"]) * 1e3, "ms")
row("p1/p2 图13-p2-2", "二极管电流尖峰", 1.19, b["ipk"], "A")
row("p2 §3", "上电第一周期浪涌", 6.7, b["inr"], "A")
row("p2 §3", "公式纹波 I/(2fC)（偏保守）", 0.87, (b["av"] / 75) / (2 * 50 * 2200e-6), "V", "SPICE 实际纹波更小，方向一致")
for c, pv in (("470", 2.89), ("1000", 1.45), ("4700", 0.31), ("10000", 0.15)):
    row("p3 图13-p3-1", f"{c} µF 纹波", pv, b["r" + c], "V")

e = ngspice("t_examples.cir", need=["e1mx", "e1pp", "e1av", "e2mx", "e2pp", "e2mxh"])
row("p2 例1", "0.2 A 最高（页面估算上限）", 15.57, e["e1mx"], "V", "页面已说明真实更低")
row("p2 例1", "0.2 A 纹波（公式 0.909）", 0.909, e["e1pp"], "V", "公式偏保守")
row("p2 例1", "0.2 A 平均（页面估算）", 15.1, e["e1av"], "V")
row("p2 例2", "9 V/0.5 A 电容最高（内阻 1 Ω）", 11.33, e["e2mx"], "V")
row("p2 例2", "同上（内阻 0.5 Ω）", 11.33, e["e2mxh"], "V")
row("p2 例2", "6800 µF 纹波（要求 ≤ 1 V）", 1.0, e["e2pp"], "V", "满足要求")

h = ngspice("t_half.cir", need=["hmx", "hpp", "hrv"])
row("p2 例3", "半波最高", 16.27, h["hmx"], "V")
row("p2 例3", "半波纹波（公式 1.82）", 1.82, h["hpp"], "V", "公式偏保守")
row("p2 例3", "二极管反向电压", 33, -h["hrv"], "V")

s = ngspice("t_scope.cir", need=["okav", "okpp", "okav2", "okpp2", "bdav", "bdpp", "bdcl", "bdav2", "bdpp2", "bdcl2"])
row("p3 图13-p3-2", "正确接法平均（1N4148 / 1N4001）", 2.93, s["okav"], "V", f"1N4001: {s['okav2']:.3f} V")
row("p3 图13-p3-2", "正确接法纹波", 0.20, s["okpp"], "V", f"1N4001: {s['okpp2']:.3f} V")
row("p3 图13-p3-2", "地夹接错 端口被钳在", -0.70, s["bdcl"], "V", f"1N4001: {s['bdcl2']:.3f} V")
row("p3 图13-p3-2", "地夹接错 短路电流 (5+钳位)/50", 86, (5 + s["bdcl"]) / 50 * 1e3, "mA")
row("p3 图13-p3-2", "地夹接错 平均", 3.17, s["bdav"], "V", f"1N4001: {s['bdav2']:.3f} V")
row("p3 图13-p3-2", "地夹接错 纹波", 0.50, s["bdpp"], "V", f"1N4001: {s['bdpp2']:.3f} V")

f = ngspice("t_fw.cir", need=["pk", "av", "emax", "emin", "bpk", "av3", "av3b"])
row("p2 图13-p2-4", "运放全波 0.5 V 输出峰值", 500.0, f["pk"] * 1e3, "mV")
row("p2 图13-p2-4", "运放全波 平均", 318.0, f["av"] * 1e3, "mV")
row("p2 图13-p2-4", "与 |Vi| 最大误差（含过零毛刺）", 0.040, max(abs(f["emax"]), abs(f["emin"])) * 1e3, "mV", "峰值处 10～120 µV；最大值来自 50 Hz 过零毛刺")
row("p2 图13-p2-4", "同信号 二极管桥输出峰值", 0, f["bpk"] * 1e3, "mV", "页面'始终 0'")
row("p3 练习4", "峰值 0.3 V 平均", 0.191, f["av3"], "V")
row("p3 练习4", "R/2 错装成 R 平均", 0.095, f["av3b"], "V")

d = ngspice("t_bleed.cir", need=["v10"])
row("p3 练习3", "4.7k 泄放 10 s 后剩余比例", 37, d["v10"] / 15.6 * 100, "%")

report("13 桥式整流（低压次级）")
