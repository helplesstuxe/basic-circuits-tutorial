#!/usr/bin/env python3
"""40 热式流量与 RTD 恒温差：ngspice 复核页面数值。电桥、CTA/CP 电热仿真用行为源；加热开关用 Infineon IRLZ44N 模型。从仓库根运行：python spice/40/run.py"""
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
import math
A, B = 3.9083e-3, -5.775e-7
pt = lambda t: 100 * (1 + A * t + B * t * t)

# ① PT100 电桥 + G=100
d = ngspice("bridge.cir", need=[f"vo{t}" for t in (0, 25, 50, 75, 100)])
for t in (25, 50, 100):
    r = pt(t)
    vd = 2.5 * (r / (2400 + r) - 100 / 2500)
    row(f"p2 §四 {t} °C", "电桥差压", vd * 1e3, d[f"vd{t}"] * 1e3, "mV")
    row(f"p2 §四 {t} °C", "INA 输出 (G=100)", vd * 100, d[f"vo{t}"], "V")
row("p2 §四", "PT100 电流 (0 °C)", 1.000, d["irt0"] * 1e3, "mA")
row("p2 §四", "PT100 电流 (100 °C)", 2.5 / (2400 + pt(100)) * 1e3, d["irt100"] * 1e3, "mA")
k = (d["vo100"] - d["vo0"]) / 100
dev50 = abs(k * 50 - d["vo50"]) / k
row("p2 §四", "端点直线 50 °C 偏差", 0.757, dev50, "K")

# ② CTA / CP
d = ngspice("cta.cir", need=["vb0", "vb2", "vb1", "tcta", "tcp", "th1a", "th1b", "th2b"])
R20, AL, C, G0, I = 20, 0.00385, 2e-4, 2e-3, 51.86e-3
g = lambda v: G0 * (1 + v ** 0.45)
row("p3 §五", "CTA 平衡温升 (v=0)", 30.0, d["th1a"], "K", "有限增益 → 略偏高")
row("p3 §五", "CTA 平衡温升 (v=2)", 30.0, d["th1b"], "K")
# CTA：θ 固定时 P = V²·Rs/(RA+Rs)²，所以 V² ∝ G·θ
Rs = R20 * (1 + AL * 30)
vb = lambda v: math.sqrt(g(v) * 30 / Rs) * (20 + Rs)
for v, key in ((0, "vb0"), (1, "vb1"), (2, "vb2")):
    row(f"p3 §五 v={v} m/s", "电桥顶端电压", vb(v), d[key], "V")
row("p3 §五", "King：V²(2)/V²(0)", (1 + 2 ** 0.45), (d["vb2"] / d["vb0"]) ** 2, "", "θ 变化 0.6 % 带来的差")
# CP：恒流，稳态 θ 满足 G·θ = I²R20(1+αθ)
th = lambda v: I * I * R20 / (g(v) - I * I * R20 * AL)
row("p3 §五 CP", "温升 v=0", th(0), d["th2a"], "K")
row("p3 §五 CP", "温升 v=2", th(2), d["th2b"], "K")
tau = C / (g(2) - I * I * R20 * AL)
row("p3 §五", "CP 63 % 时间 (0→2 m/s)", tau * 1e3, d["tcp"] * 1e3, "ms")
row("p3 §五", "CTA 63 % 时间 (0→2 m/s)", 0.7265, d["tcta"] * 1e3, "ms")
row("p3 §五", "CP/CTA 时间比", 60.8, d["tcp"] / d["tcta"], "")

# ③ 实验加热回路
d = ngspice("lab_mos.cir", need=["id", "vds", "ph", "pm", "vn25", "vn45", "phavg", "pmavg"])
row("p4 测量表 第7步", "加热电流", 9 / 560 * 1e3, d["id"] * 1e3, "mA")
row("p4 测量表 第7步", "加热功率 (100 %)", 9 * 9 / 560 * 1e3, d["ph"] * 1e3, "mW")
row("p2 §二", "MOSFET 导通损耗", 0.0054, d["pm"] * 1e3, "mW")
row("p4 测量表 ③", "MOSFET V_DS", 0.3364, d["vds"] * 1e3, "mV")
row("p4 测量表 ①", "NTC 分压 25 °C", 2.5, d["vn25"], "V")
row("p4 测量表 ②", "NTC 分压 45 °C", 5 * 4372 / 14372, d["vn45"], "V")
row("p2 §二", "PWM 50 % 平均功率", 9 * 9 / 560 * 0.5 * 1e3, d["phavg"] * 1e3, "mW")
row("p2 §二", "PWM 50 % MOSFET 损耗", 0.04355, d["pmavg"] * 1e3, "mW")
report("40 热式流量 SPICE 复核")
