#!/usr/bin/env python3
"""19 射极跟随器：ngspice + onsemi 2N3904 / 2N3906 / TIP31C、TI LM358（LMx58）/ LM358B 官方模型复核页面数值。从仓库根运行：python spice/19/run.py"""
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

d = ngspice("dc_ef.cir", need=["r50_e1", "r1000_e1", "r100_e1", "r20_e1", "r50_ib1", "r20_ib1", "x1_e1", "x2_e1", "x3_e1", "p1_e2", "pmx2", "pmx1"])
note = lambda k: f"TIP31C: {d[k.replace('_e1', '_e2')]:.3f} V"
for r, pv in ((1000, 4.37), (100, 4.31), (50, 4.29), (20, 4.27)):
    row("p2 §3 负载扫描", f"5 V 输入, R_L {r} Ω 输出 (2N3904)", pv, d[f"r{r}_e1"], "V", note(f"r{r}_e1"))
row("p2 §3 负载扫描", "1 kΩ→20 Ω 输出变化 (2N3904)", 101, (d["r1000_e1"] - d["r20_e1"]) * 1e3, "mV",
    f"TIP31C: {(d['r1000_e2'] - d['r20_e2']) * 1e3:.0f} mV；R_out ≈ {(d['r1000_e1'] - d['r20_e1']) / (d['r20_ic1'] + d['r20_ib1'] - d['r1000_ic1'] - d['r1000_ib1']):.2f} Ω（页面 0.48 Ω）")
row("p1 图19-p1-2 / p2 推导二", "50 Ω 时基极电流 (2N3904)", 1.68, d["r50_ib1"] * 1e3, "mA", f"TIP31C: {d['r50_ib2'] * 1e3:.2f} mA")
row("p2 §3 负载扫描", "20 Ω 时基极电流 (2N3904)", 4.18, d["r20_ib1"] * 1e3, "mA", f"β 掉到 {d['r20_ic1'] / d['r20_ib1']:.0f}；TIP31C: {d['r20_ib2'] * 1e3:.2f} mA")
for r, pv in ((1000, 0.03), (100, 0.32), (50, 0.65), (20, 1.62)):
    row("p2 §3 负载扫描", f"R_L {r} Ω 管耗 (2N3904)", pv, (12 - d[f"r{r}_e1"]) * d[f"r{r}_ic1"], "W")
p50 = (12 - d["r50_e1"]) * d["r50_ic1"]
row("p2 §4", "50 Ω 时 2N3904 结温 (25 °C + P×200)", 155, 25 + p50 * 200, "°C", "仍超过 150 °C，结论不变")
row("p2 §4 R_in", "从运放看进去 V_i/I_B (2N3904)", 2550, 5 / d["r50_ib1"], "Ω")
row("p2 例1", "V_o", 5.3, d["x1_e1"], "V", note("x1_e1"))
row("p2 例1", "I_E", 53.0, (d["x1_ic1"] + d["x1_ib1"]) * 1e3, "mA")
row("p2 例1", "I_B（题设 β=50）", 1.04, d["x1_ib1"] * 1e3, "mA", "2N3904 模型 β 约 60")
row("p2 例1", "P_C", 0.348, (12 - d["x1_e1"]) * d["x1_ic1"], "W")
row("p2 例2", "V_o", 2.6, d["x2_e1"], "V", note("x2_e1"))
row("p2 例2", "I_E", 55.3, (d["x2_ic1"] + d["x2_ib1"]) * 1e3, "mA")
row("p2 例2", "I_B（题设 β=50）", 1.08, d["x2_ib1"] * 1e3, "mA")
row("p2 例2", "P_C", 0.510, (12 - d["x2_e1"]) * d["x2_ic1"], "W")
row("p2 例3", "V_i = 5.7 V 时 50 Ω 上电压", 5.0, d["x3_e1"], "V", note("x3_e1"))
row("p2 例3", "12 V 电源管耗", 0.693, (12 - d["x3_e1"]) * d["x3_ic1"], "W")
row("p2 例3", "7 V 电源管耗", 0.198, (7 - d["x3b_e1"]) * d["x3b_ic1"], "W")
row("p3 练习1 (TIP31C)", "V_o", 8.3, d["p1_e2"], "V")
row("p3 练习1 (TIP31C)", "I_B（题设 β=50）", 8.14, d["p1_ib2"] * 1e3, "mA", "TIP31C 模型 β 约 180，实际更小")
row("p3 练习1 (TIP31C)", "P_C", 2.73, (15 - d["p1_e2"]) * d["p1_ic2"], "W")
row("p3 图19-p3-1", "12 V/50 Ω 最大管耗 (TIP31C)", 0.71, d["pmx2"], "W", f"2N3904: {d['pmx1']:.3f} W")

s = ngspice("t_sine.cir", need=["mx1", "mn1", "mx2", "mn2", "bx1", "bn1", "bx2", "bn2"])
row("p2 图19-p2-2", "正弦输出最高 (2N3904)", 6.28, s["mx1"], "V", f"TIP31C: {s['mx2']:.3f} V")
row("p2 图19-p2-2", "正弦输出最低 (2N3904)", 2.31, s["mn1"], "V", f"TIP31C: {s['mn2']:.3f} V")
row("p2 图19-p2-2", "交流增益 (2N3904)", 0.994, (s["mx1"] - s["mn1"]) / 4, "", f"TIP31C: {(s['mx2'] - s['mn2']) / 4:.3f}")
row("p1 §4 / p2 图19-p2-2", "V_BE 最大（峰值处台阶）(2N3904)", 0.720, s["bx1"], "V", f"范围 {s['bn1']:.3f}~{s['bx1']:.3f}；TIP31C {s['bn2']:.3f}~{s['bx2']:.3f}")
row("p2 推导三", "3→7 V 时 V_BE 变化 (2N3904)", 26, (s["bx1"] - s["bn1"]) * 1e3, "mV", f"TIP31C: {(s['bx2'] - s['bn2']) * 1e3:.0f} mV")

a = ngspice("t_opA.cir", need=["vo"])
row("p1 §1 / p2 图19-p2-2", "LM358 直接带 50 Ω 的输出", 1.50, a["vo"], "V", f"约 {a['vo'] / 50 * 1e3:.0f} mA 限流")
b = ngspice("t_opB.cir", need=["ve", "vo"])
b3 = ngspice("t_opB3.cir", need=["ve", "vo"])
row("p2 图19-p2-4", "反馈取自发射极 V_o (TIP31C)", 5.00, b["ve"], "V", f"2N3904: {b3['ve']:.4f} V")
row("p2 图19-p2-4", "此时运放输出 (TIP31C)", 5.71, b["vo"], "V", f"2N3904: {b3['vo']:.3f} V")
rb = ngspice("t_opRB.cir", need=["ve", "vo"])
row("p3 §2", "环内串 470 Ω：V_o", 5.00, rb["ve"], "V")
row("p3 §2", "环内串 470 Ω：运放输出", 6.50, rb["vo"], "V", "页面按 β=50；TIP31C 基极电流小")
c = ngspice("t_opC.cir", need=["ve", "vo"])
row("p3 §2", "环外串 470 Ω（反馈取运放输出）V_o", 3.5, c["ve"], "V", "页面按 β=50 估压降 0.79 V")

l = ngspice("dc_lab.cir", need=["vb1k", "ve1k", "vw2", "vb220", "ve220", "ic220"])
row("p2 §7 第2步", "V_E（1 kΩ）", 4.36, l["ve1k"], "V")
row("p2 §7 第2步", "V_B − V_E（1 kΩ）", 0.7, l["vb1k"] - l["ve1k"], "V", "页面 0.6~0.7 V")
row("p2 §7 第3步", "V_E（220 Ω）", 4.28, l["ve220"], "V", f"V_B−V_E = {l['vb220'] - l['ve220']:.3f} V")
row("p1 §4", "220 Ω/1 kΩ 电流比", 4.5, (l["ve220"] / 220) / (l["ve1k"] / 1000), "")
row("p2 §7 第4步", "去掉三极管 220 Ω 挂滑片", 2.36, l["vw2"], "V")
row("p2 §7 第5步", "220 Ω 时管耗", 0.09, (9 - l["ve220"]) * l["ic220"], "W")

q = ngspice("t_ss5.cir", need=["ve27", "vo27", "vemax", "vomax"])
row("p3 练习2", "5 V 单电源 输入 2.7 V 输出", 2.0, q["ve27"], "V")
row("p3 练习2", "LM358B 输出最高", 3.6, q["vomax"], "V")
row("p3 练习2", "跟随器输出最高", 2.9, q["vemax"], "V")

p = ngspice("t_pp.cir", need=["mx", "mn", "vth"])
row("p3 练习4 图19-p3-2", "推挽输出峰值", 2.3, p["mx"], "V", f"负峰 {p['mn']:.3f} V")
row("p3 练习4 图19-p3-2", "死区边界（输出达 10 mV 时的输入）", 0.7, p["vth"], "V", "1 kΩ 负载，假设")

report("19 射极跟随器")
