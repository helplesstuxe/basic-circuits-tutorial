#!/usr/bin/env python3
"""03 半导体入门：用 ngspice + 厂家模型核对页面数值。从仓库根运行：python spice/03/run.py"""
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
    if r.returncode != 0 or miss or re.search(r"(?i)fatal error|failed|error on line", out):
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

def sweep(cir):
    r = subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=300)
    rows = [list(map(float, l.split()[1:])) for l in r.stdout.splitlines() if l.startswith("SWEEP")]
    if r.returncode != 0 or not rows:
        print(r.stdout[-2000:], r.stderr[-2000:]); sys.exit(f"{cir} 失败")
    return rows

def cross(rows, col, level):
    """线性插值求第 col 列首次超过 level 时的 RB。"""
    for a, b in zip(rows, rows[1:]):
        if a[col] <= level < b[col]:
            return a[0] + (level - a[col]) * (b[0] - a[0]) / (b[col] - a[col])
    return None

d = ngspice("diodes.cir", need=["vlamp", "vz", "iz", "vz49", "vz5", "vf10", "id5", "ip"])
row("p1 图03-p1-1", "6V+1N4007+灯(20Ω假设) 灯电压", 5.3, d["vlamp"], "V")
row("p1 图03-p1-2", "12V/1k/1N4733A 输出", 5.1, d["vz"], "V")
row("p1 图03-p1-2", "电阻上电压", 6.9, 12 - d["vz"], "V")
row("p2 §1 0.7V规则例", "5V/1k/1N4148 电流", 4.31, d["id5"] * 1e3, "mA")
row("p2 §1 仿真打印", "2V 时 VD", 0.662, d["vd2"], "V")
row("p2 §1 仿真打印", "2V 时 I", 1.34, d["id2"] * 1e3, "mA")
row("p2 §1 仿真打印", "5V 时 VD", 0.692, d["vd5"], "V")
row("p2 §1 仿真打印", "12V 时 VD", 0.717, d["vd12"], "V")
row("p2 §1 仿真打印", "12V 时 I", 11.28, d["id12"] * 1e3, "mA")
row("p2 §1 1N4148", "1 mA 时 VF(典型0.6-0.7)", 0.65, d["vf1"], "V", "取区间中点")
row("p2 §1 1N4148", "10 mA 时 VF(典型≈0.7,≤1)", 0.70, d["vf10"], "V")
row("p2 §2 1N4733A", "49 mA 时 VZ", 5.1, d["vz49"], "V")
row("p2 §2 1N4733A", "5 mA 时 V", 4.792, d["vz5"], "V", "页面按 rZ=7Ω(最大值)")
row("p2 图03-p2-2", "击穿起点(取1mA)", 4.8, d["vz1"], "V")
row("p3 练习1", "12V/1k/两只1N4148", 10.6, d["ip"] * 1e3, "mA")
row("p3 练习1", "12V/1k/两只1N4007", 10.6, d["iq"] * 1e3, "mA")
row("p3 练习2", "稳压管电流(粗算)", 6.9, d["iz"] * 1e3, "mA")
row("p3 练习2", "稳压管功耗", 35, d["iz"] * d["vz"] * 1e3, "mW")
row("p3 练习2", "精算电流", 7.19, d["iz"] * 1e3, "mA")
row("p3 练习2", "精算电压", 4.81, d["vz"], "V")

b = ngspice("bjt.cir", need=["ib1_164", "vce1_164", "ic1_164", "vce1_5", "vin_sat3", "ib3"])
row("p1 图03-p1-3 左", "基极电流(几百µA)", 430, b["ib3"] * 1e6, "µA", "页面'几百微安'，按(5-0.7)/10k")
row("p1 图03-p1-3 左", "LED 电流(推算)", 12.7, b["ic3"] * 1e3, "mA", "(5-2-0.2)/220；LED 用2V源代替")
row("p2 §3 图03-p2-3", "Vin1.64V IB", 20, b["ib1_164"] * 1e6, "µA")
row("p2 §3 图03-p2-3", "Vin1.64V IC(β=100)", 2.0, b["ic1_164"] * 1e3, "mA")
row("p2 §3 图03-p2-3", "Vin1.64V VCE(β=100)", 3.0, b["vce1_164"], "V")
row("p2 §3 图03-p2-3", "Vin5V IB", 91.5, b["ib1_5"] * 1e6, "µA")
row("p2 §3 图03-p2-3", "Vin5V VCE(饱和)", 0.2, b["vce1_5"], "V")
row("p2 §3 图03-p2-3", "Vin5V IC", 4.8, b["ic1_5"] * 1e3, "mA")
row("p2 §5 图03-p2-5", "开始导通 Vin(IC=1mA)", 0.7, b["vin_1ma"], "V")
row("p2 §5 图03-p2-5", "进入饱和 Vin(VCE=0.3V)", 1.18, b["vin_sat3"], "V")
row("p2 §5 图03-p2-5", "进入饱和 Vin(VCE=0.2V)", 1.18, b["vin_sat"], "V")
row("p2 §5 图03-p2-5", "饱和 IC", 4.8, b["ic2_5"] * 1e3, "mA")

s = sweep("rbsweep.cir")   # 列：RB, VCE, IC, IB, VCE(12V/120Ω), IC(12V/120Ω)
at = {int(x[0]): x for x in s}
row("p2 例2", "饱和 IC", 48, at[1500][2] * 1e3, "mA")
row("p2 例2 / p3", "RB=1.5k VCE(≤0.3 即饱和)", 0.2, at[1500][1], "V", "2N3904 VCE(sat)max 0.3V@50mA")
row("p2 例2", "RB=1.5k IB", 1.6, at[1500][3] * 1e3, "mA")
row("p3 图03-p3-1", "RB=1k VCE", 0.2, at[1000][1], "V")
row("p3 图03-p3-1", "离开饱和 RB(VCE=0.3V)", 3.2, cross(s, 1, 0.3) / 1e3, "kΩ", "页面 β=60；真实管见报告")
row("p3 图03-p3-1", "离开饱和 RB(VCE=0.4V)", 3.2, cross(s, 1, 0.4) / 1e3, "kΩ")
row("p3 图03-p3-1", "RB=4.7k VCE(β=60)", 1.68, at[4700][1], "V", "真实典型 2N3904")
row("p3 图03-p3-1", "RB=4.7k IC", 33, at[4700][2] * 1e3, "mA")
row("p3 图03-p3-1", "RB=4.7k 管耗", 55, at[4700][1] * at[4700][2] * 1e3, "mW")
row("p3 图03-p3-1", "RB=10.8k VCE(β=200 边界)", 0.2, at[10800][1], "V", "页面假想 β=200 管")
row("p3 练习3", "RB=1k IC", 98, at[1000][5] * 1e3, "mA")
row("p3 练习3", "RB=1k VCE", 0.2, at[1000][4], "V")
row("p3 练习3", "RB=2.2k VCE(压线)", 0.2, at[2200][4], "V", "页面:β偏小就不饱和")
print("  [RB 扫描 3.3V→5V/100Ω]  " + "  ".join(f"{int(x[0])}Ω:{x[1]:.2f}V" for x in s))
print("  [RB 扫描 5V→12V/120Ω]   " + "  ".join(f"{int(x[0])}Ω:{x[4]:.2f}V" for x in s))

m = ngspice("mos.cir", need=["vth", "r45", "r10", "id3"])
row("p2 §4 / p3 参数表", "2N7000 VGS(th)(典型2.1,0.8-3.0)", 2.1, m["vth"], "V")
row("p3 参数表", "RDS(on)@4.5V,75mA (max5.3)", 5.3, m["r45"], "Ω", "LEVEL1 模型")
row("p3 参数表", "RDS(on)@10V,500mA (max5)", 5.0, m["r10"], "Ω")
row("p2 例3/p3 练习4", "3.3V 直驱 100Ω 负载电流", 48, m["id3"] * 1e3, "mA", "页面:半开半关、不稳妥")
row("p2 例3/p3 练习4", "3.3V 直驱 VDS", None, m["vds3"], "V")
row("p3 图03-p3-2(示意)", "Rds@3.3V,0.2A", 4.17, m["ra"], "Ω", "示意模型,不判")
row("p3 图03-p3-2(示意)", "Rds@5V,0.2A", 1.72, m["rb"], "Ω", "示意模型,不判")
row("p3 图03-p3-2(示意)", "Rds@10V,0.2A", 0.63, m["rc"], "Ω", "示意模型,不判")

report("03 半导体入门")
