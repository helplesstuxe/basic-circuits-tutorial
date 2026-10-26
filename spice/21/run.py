#!/usr/bin/env python3
"""21 线性稳压：分立稳压电路（LM358 + TIP31C + 1N4733A）与 7805 替代核对。"""
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

DC = ["vref", "vo", "vob", "iin", "iz"]
RIP = ["opp", "omn", "ipp", "imn", "rav", "oav", "izav"]
d14 = ngspice("t_dc14.cir", need=DC)
d14l = ngspice("t_dc14l.cir", need=DC)
d13 = ngspice("t_dc13.cir", need=DC)
d15 = ngspice("t_dc15.cir", need=DC)
l180 = ngspice("t_lab180.cir", need=DC)
l18 = ngspice("t_lab18.cir", need=DC)
e1 = ngspice("t_ex1.cir", need=DC)
e2 = ngspice("t_ex2.cir", need=DC)
p1 = ngspice("t_p1.cir", need=DC)
r14 = ngspice("t_rip14.cir", need=RIP)
r115 = ngspice("t_rip115.cir", need=RIP)
r12 = ngspice("t_rip12.cir", need=RIP)
r2k = ngspice("t_ripRZ2k.cir", need=RIP)
dr = ngspice("t_drop05.cir", need=["v12", "v11", "v10", "hd10", "vknee"])
drl = ngspice("t_drop005.cir", need=["vknee"])
sc = ngspice("t_stab_C10.cir", need=["opp", "fosc"])
se = ngspice("t_stab_esr1L.cir", need=["opp"])
s78 = ngspice("t_78xx_sub.cir", need=["vo12", "ii12", "vo9", "ii9"])

# ---- 主例：14 V、0.5 A ----
vo, vref = d14["vo"], d14["vref"]
il = vo / 17.66
ie = il + vo / 9000.0                       # 负载 + 分压电阻
pin = 14 * -d14["iin"]
pload = vo * il
pc = (14 - vo) * ie
row("p2 §2 第1步", "I_Z（14 V）", 9.18, -d14["iz"] * 1e3, "mA")
row("p2 §2 第1步", "V_ref（14 V）", 4.821, vref, "V", "Diodes 1N4733A 模型 9 mA 时约 5.00 V；手册 5.1 V±5% @49 mA")
row("p2 §2 第3步 / p1 §三", "V_o = V_ref(1+R_f/R_1)", 8.508, vo, "V", f"按 SPICE 基准算公式值 {vref * (1 + 3.9 / 5.1):.3f} V")
row("p2 §2 第4步", "运放输出（0.5 A）", 9.26, d14["vob"], "V")
row("p2 §2 第4步", "V_BE（0.5 A）", 0.755, d14["vob"] - vo, "V", "TIP31C 模型")
row("p1 图21-p1-3", "从输入拿走的功率", 7.14, pin, "W")
row("p1 图21-p1-3", "负载得到的功率", 4.25, pload, "W", "负载电流 0.5 A，SPICE 输出电压高 0.32 V")
row("p1 图21-p1-3", "调整管发热", 2.75, pc, "W")
row("p1 图21-p1-3", "基准、分压、运放", 0.14, pin - pload - pc, "W")
row("p1 §四", "效率", 60, pload / pin * 100, "%")
dvl = (d14l["vo"] - vo) * 1e6
row("p1 §三 / p2 §三 / p2 §六", "负载 0.01→0.5 A 输出变化", 1.8, dvl, "µV",
    f"运放输出变 {(d14['vob'] - d14l['vob']) * 1e3:.0f} mV（页面设 V_BE 变 0.1 V）；等效 AK ≈ {(d14['vob'] - d14l['vob']) / (dvl * 1e-6):.0f}（页面 56667）")
row("p2 §六", "输入 13→15 V 输出变化", 24.5, (d15["vo"] - d13["vo"]) * 1e3, "mV")
# ---- 纹波 ----
row("p1 图21-p1-2 / p2 §五", "输出纹波（14 V 平均、2 V 峰峰）", 24.5, r14["opp"] * 1e3, "mV",
    f"基准纹波按 1N4733A 模型（9 mA 时 r_Z≈5.7 Ω）；抑制 {2 / r14['opp']:.0f} 倍")
row("p2 §五", "纹波抑制（dB）", 38, 20 * math.log10(2 / r14["opp"]), "dB")
row("p3 练习3", "R_Z 2 kΩ：输出纹波", 12.3, r2k["opp"] * 1e3, "mV", "指数型稳压管 r_Z∝1/I_Z，电流减半 r_Z 加倍，纹波几乎不变")
row("p3 练习3", "R_Z 2 kΩ：I_Z", 4.6, -r2k["izav"] * 1e3, "mA")
row("p3 练习3", "R_Z 2 kΩ：基准", 4.79, r2k["rav"], "V")
row("p3 练习3", "R_Z 2 kΩ：输出", 8.45, r2k["oav"], "V")
# ---- 压差 ----
row("p2 §四 / p3 §一", "最低输入（0.5 A）", 10.76, dr["vknee"], "V", "拐点定义：输出比 12 V 时低 20 mV")
row("p2 §四", "最低输入（0.05 A）", 10.70, drl["vknee"], "V")
row("p2 §六", "输入 12 V 时 V_o", 8.48, dr["v12"], "V")
row("p2 §六", "输入 11 V 时 V_o", 8.47, dr["v11"], "V")
row("p2 §四 / §六", "输入 10 V 时 V_o", 7.74, dr["v10"], "V")
row("p2 §四", "跟随区压差（输入 10 V）", 2.26, dr["hd10"], "V")
row("p3 §三 图21-p3-2", "11.5 V 平均：输出最低", 8.24, r115["omn"], "V")
row("p3 §三 图21-p3-2", "11.5 V 平均：输出纹波", 245, r115["opp"] * 1e3, "mV", f"是 14 V 时的 {r115['opp'] / r14['opp']:.0f} 倍（页面 10 倍）")
row("p3 练习2", "12 V 平均、2 V 纹波：输出纹波（无缺口）", None, r12["opp"] * 1e3, "mV", f"谷底 11 V；与 14 V 时 {r14['opp'] * 1e3:.1f} mV 相近，无缺口")
# ---- 例题、练习 ----
row("p2 例1", "R_f 7.5 kΩ、16 V：V_o", 11.91, e1["vo"], "V")
row("p2 例1", "调整管功耗", 2.05, (16 - e1["vo"]) * 0.5, "W", "差别来自 V_o 高 0.48 V")
row("p2 例2", "R_f 2.0 kΩ、12 V：V_o", 6.71, e2["vo"], "V")
row("p2 例2", "调整管功耗", 1.59, (12 - e2["vo"]) * 0.3, "W")
row("p3 练习1", "16 V、0.5 A 调整管功耗", 3.75, (16 - p1["vo"]) * 0.5, "W")
# ---- 动手实验 ----
row("p3 §五 第2步", "180 Ω：V_ref", 4.82, l180["vref"], "V")
row("p3 §五 第2步", "180 Ω：V_o", 8.51, l180["vo"], "V")
row("p3 §五 第2步", "180 Ω：运放输出", 9.2, l180["vob"], "V")
row("p3 §五 第3步", "换 18 Ω：输出变化（几乎不变）", None, (l18["vo"] - l180["vo"]) * 1e3, "mV")
row("p3 §五 第3步", "换 18 Ω：运放输出升高", None, (l18["vob"] - l180["vob"]) * 1e3, "mV", "页面：几十毫伏")
row("p3 §五 第4步", "输出开始下降的输入（10.7–10.8 V）", 10.75, dr["vknee"], "V")
# ---- 稳定性 ----
row("p2 图21-p2-1 C_o 10 µF", "理想 10 µF 直接并输出：输出峰峰", None, sc["opp"], "V", f"持续振荡 {sc['fosc'] / 1e3:.1f} kHz（页面图示为稳定直线）")
row("p3 §四", "10 µF 串 1 Ω ESR、0.05 A：输出峰峰", None, se["opp"] * 1e3, "mV", "稳定")
# ---- 7805（替代：LM317 接成 5 V）----
row("p2 例3（替代 LM317）", "12 V→5 V、1 A：V_o", 5.0, s78["vo12"], "V", "替代模型，仅核对功耗")
row("p2 例3（替代 LM317）", "功耗", 7.0, (12 - s78["vo12"]) * s78["vo12"] / 5, "W")
row("p3 练习4（替代 LM317）", "9 V→5 V、0.5 A 功耗", 2.0, (9 - s78["vo9"]) * s78["vo9"] / 10, "W")
report("21 线性稳压")
