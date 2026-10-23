#!/usr/bin/env python3
"""10 稳压管稳压：ngspice + Diodes Inc. 1N4733A / 1N4742A、onsemi 2N3904 / TIP31C 官方模型复核页面数值。从仓库根运行：python spice/10/run.py"""
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

m = ngspice("dc_main.cir", need=["vo_rl_10", "vo_rl_11", "vo_rl_12", "vo_rl_14", "vin_on01", "vin_on1", "iin12", "vo12_20",
                                 "iz0", "vo0", "iz20", "vo20", "vo40", "ildrop1", "ildrop01", "iz14", "vo14", "rmax5", "rcut01",
                                 "rmin065", "pz40", "iz40", "izr120", "vor120", "izr47", "vor47", "lab180_iz_1000", "lab180_iz_255",
                                 "lab270_iz_255", "lab270_vo_255", "lab180_vo_255", "lab_vo_270_255_95", "lab_on1"])
RK = ["opp", "oav", "omn", "izmn"]
r12, l180, l270 = ngspice("t_rip12.cir", RK), ngspice("t_low180.cir", RK), ngspice("t_low270.cir", RK)
p4a, p4b = ngspice("t_p4_390.cir", RK), ngspice("t_p4_910.cir", RK)
f = ngspice("dc_fol.cir", need=["vo0", "vo1", "vo100", "iz0", "iz100", "vb100", "pc12"])
e2 = ngspice("dc_ex2.cir", need=["iz", "vo", "pz", "pr"])
e3 = ngspice("dc_ex3.cir", need=["iz0", "iz200", "vb200", "vo200", "pc200", "iz200_10"])

# ---- page1 直觉篇 ----
row("p1 图10-p1-2", "稳压管开始导通的输入（I_Z=0.1 mA）", 8.1, m["vin_on01"], "V", f"I_Z=1 mA 时 {m['vin_on1']:.2f} V")
row("p1 图10-p1-2", "输入 10 V 输出（RL 255 Ω）", 4.83, m["vo_rl_10"], "V", "在 1N4733A ±5% 容差内")
row("p1 图10-p1-2", "输入 14 V 输出（RL 255 Ω）", 4.97, m["vo_rl_14"], "V", "在 ±5% 容差内")
row("p1 图10-p1-2 / p2 开头", "10→14 V 输出变化", 146, (m["vo_rl_14"] - m["vo_rl_10"]) * 1e3, "mV", "页面 r_Z 用手册最大值 7 Ω")
row("p1 图10-p1-3", "12 V±0.5 V 纹波 → 输出峰峰", 36.5, r12["opp"] * 1e3, "mV")
row("p1 图10-p1-3", "输出平均", 4.90, r12["oav"], "V")
row("p1 §四", "12 V、20 mA 负载时输入电流", 39.5, m["iin12"] * 1e3, "mA")
row("p1 §四", "输入功率", 0.47, m["iin12"] * 12, "W")
row("p1 §四", "负载功率", 0.10, m["vo12_20"] * 0.02, "W")
row("p1 §四", "效率", 21, m["vo12_20"] * 0.02 / (m["iin12"] * 12) * 100, "%")
# ---- page2 原理与实现篇 ----
row("p2 叠加验证", "10 V→11 V 输出差（RL 255 Ω）", 36.5, (m["vo_rl_11"] - m["vo_rl_10"]) * 1e3, "mV", "与纹波同一原因")
row("p2 图10-p2-1", "空载 I_Z（10 V）", 28.0, m["iz0"] * 1e3, "mA")
row("p2 图10-p2-1", "负载 20 mA 时 I_Z", 8.8, m["iz20"] * 1e3, "mA", "V_o 高 0.17 V 所致，容差内")
row("p2 图10-p2-1", "负载 20 mA 时 V_o", 4.819, m["vo20"], "V")
row("p2 图10-p2-1", "失去稳压的负载电流（I_Z=0.1 mA）", 29.2, m["ildrop01"] * 1e3, "mA", f"I_Z=1 mA 时 {m['ildrop1']*1e3:.1f} mA")
row("p2 图10-p2-1", "负载 40 mA 时 V_o", 2.80, m["vo40"], "V")
row("p2 §负载调整", "负载 0→20 mA 输出下降", 0.13, m["vo0"] - m["vo20"], "V", "页面 r_Z 7 Ω")
row("p2 例1 / §下限核对", "14 V 空载 I_Z", 49.4, m["iz14"] * 1e3, "mA")
row("p2 例1", "14 V 空载 V_o", 5.10, m["vo14"], "V")
row("p2 例1", "稳压管功耗", 0.25, m["vo14"] * m["iz14"], "W")
row("p2 例1", "R 功耗", 0.44, (14 - m["vo14"]) ** 2 / 180, "W")
row("p2 图10-p2-3", "跟随器轻载输出（页面“空载”，SPICE 取 1 mA）", 4.253, f["vo1"], "V", f"真正 0 mA 时发射极浮到 {f['vo0']:.2f} V")
row("p2 图10-p2-3", "跟随器 100 mA 输出", 4.232, f["vo100"], "V")
row("p2 图10-p2-3", "跟随器 1→100 mA 输出下降", 22, (f["vo1"] - f["vo100"]) * 1e3, "mV", "V_BE 随电流增大约 0.25 V")
row("p2 图10-p2-3", "跟随器空载 I_Z", 28.0, f["iz0"] * 1e3, "mA")
row("p2 图10-p2-3", "跟随器 100 mA 时 I_Z", 24.9, f["iz100"] * 1e3, "mA")
row("p2 §射极跟随器", "100 mA 时基极电流（页面 β=30 假设）", 3.23, ((10 - f["vb100"]) / 180 - f["iz100"]) * 1e3, "mA", "模型 β≈38，按 β 最小值 30 是题设")
row("p2 §射极跟随器", "12 V、100 mA 三极管功耗", 0.78, f["pc12"], "W")
row("p2 例2", "1N4742A 390 Ω 24 V 空载 I_Z", 30.5, e2["iz"] * 1e3, "mA")
row("p2 例2", "V_o", 12.09, e2["vo"], "V")
row("p2 例2", "稳压管功耗", 0.37, e2["pz"], "W")
row("p2 例2", "R 功耗", 0.36, e2["pr"], "W")
row("p2 例3", "560 Ω 14 V 空载 I_Z", 16.3, e3["iz0"] * 1e3, "mA", "功率管用 TIP31C 代表（替代）")
row("p2 例3", "14 V、200 mA 基极电压", 4.85, e3["vb200"], "V")
row("p2 例3", "14 V、200 mA 输出", 4.15, e3["vo200"], "V")
row("p2 例3", "三极管功耗", 1.97, e3["pc200"], "W")
row("p2 例3", "10 V、200 mA 时 I_Z（设计要求 ≥5 mA）", 5, e3["iz200_10"] * 1e3, "mA", "TIP31C β 大于 60，余量更大")
# ---- page3 参数与调试篇 ----
row("p3 图10-p3-1", "R 上限（10 V、20 mA、I_Z=5 mA）", 208, m["rmax5"], "Ω")
row("p3 图10-p3-1", "R 下限（14 V 空载、P_Z=0.65 W）", 73, m["rmin065"], "Ω")
row("p3 图10-p3-1", "R=40 Ω 稳压管功耗", 1.21, m["pz40"], "W")
row("p3 图10-p3-1", "R=40 Ω 稳压管电流", 197, m["iz40"] * 1e3, "mA", "两者都超 I_ZM 178 mA")
row("p3 图10-p3-1", "完全断流的 R（I_Z=0.1 mA）", 263, m["rcut01"], "Ω")
row("p3 图10-p3-2", "R 180 Ω、10–11 V、20 mA 输出纹波", 37, l180["opp"] * 1e3, "mV")
row("p3 图10-p3-2", "R 270 Ω 输出最低", 4.60, l270["omn"], "V")
row("p3 图10-p3-2", "R 270 Ω 输出纹波", 178, l270["opp"] * 1e3, "mV")
row("p3 图10-p3-2", "270 Ω / 180 Ω 纹波倍数", 5, l270["opp"] / l180["opp"], "×")
row("p3 §4 第1步", "空载时稳压管开始击穿的输入（I_Z=1 mA）", 4.8, m["lab_on1"], "V")
row("p3 §4 第2步", "1 kΩ→255 Ω 时 I_Z 减少量 ≈ 负载电流增加量", None, (m["lab180_iz_1000"] - m["lab180_iz_255"]) * 1e3, "mA", "负载电流增加约 14.5 mA（页面定性：等量减小）")
row("p3 §4 第3步", "R 270 Ω、255 Ω 负载 I_Z", 0.7, m["lab270_iz_255"] * 1e3, "mA")
row("p3 §4 第3步", "R 270 Ω、255 Ω 负载 V_o（低于第2步）", None, m["lab270_vo_255"], "V", f"第2步 {m['lab180_vo_255']:.3f} V")
row("p3 §4 第3步", "再调到 9.5 V 输出", 4.6, m["lab_vo_270_255_95"], "V")
row("p3 练习1", "120 Ω 14 V 空载 I_Z", 72.8, m["izr120"] * 1e3, "mA")
row("p3 练习1", "V_o", 5.27, m["vor120"], "V")
row("p3 练习1", "稳压管功耗", 0.38, m["izr120"] * m["vor120"], "W")
row("p3 练习2", "47 Ω 14 V 空载 I_Z（页面：离 178 mA 只差一点）", 171, m["izr47"] * 1e3, "mA", "SPICE 已超 I_ZM 178 mA")
row("p3 练习2", "V_o", 5.96, m["vor47"], "V")
row("p3 练习2", "稳压管功耗", 1.02, m["izr47"] * m["vor47"], "W")
row("p3 练习4", "1N4742A 390 Ω 1.2 kΩ 输出纹波", 22, p4a["opp"] * 1e3, "mV", "平均输入取 30 V（假设）")
row("p3 练习4", "R=910 Ω 时纹波（要求 <10 mV）", 10, p4b["opp"] * 1e3, "mV", "页面值为上限；SPICE 390 Ω 已达标")
report("10 稳压管稳压")
