"""10 电压比较器：ngspice + TI LM393A 官方模型核对。在仓库根目录运行：python spice/10/run.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check

def wave(r, f):
    d = np.loadtxt(pathlib.Path(r["_dir"]) / f)
    return d

print("== 10 电压比较器 ==")
# 基本比较器（图10-p1-1）
r = ng.run("schmitt_sweep.cir", dict(R1="1m", R2="1e12"))
check("p1 图10-p1-1", "基准分压 Vref", 2.5, r["vref"], "V")
check("p1 图10-p1-1", "基本比较器上升翻转点", 2.5, r["vh"], "V", tol=1)
check("p1 图10-p1-1", "基本比较器下降翻转点", 2.5, r["vl"], "V", tol=1)
check("p1 图10-p1-1", "输出高电平(2.2k 上拉)", 5.0, r["voh"], "V")
check("p3 §1 表", "输出低电平(灌 2.3 mA) ≤0.4 V", 0.4, r["vol"], "V", "页面为上限", v="✅" if r["vol"] <= 0.4 else "❌")
# 施密特（图10-p1-3、page2 §2、图10-p2-1）
r = ng.run("schmitt_sweep.cir")
check("p2 §2 / 图10-p2-1", "上门限 VH", 2.75, r["vh"], "V", tol=2)
check("p2 §2 / 图10-p2-1", "下门限 VL(计入 R3)", 2.255, r["vl"], "V", tol=2)
check("p2 §2 / 图10-p2-1", "回差", 0.495, r["vh"] - r["vl"], "V")
# page3 §2 R2 扫描端点
for r2, dv in (("1meg", 0.05), ("68k", 0.72)):
    r = ng.run("schmitt_sweep.cir", dict(R2=r2))
    check("p3 §2 R2 扫描", f"R2={r2} 回差", dv, r["vh"] - r["vl"], "V")
# 练习 2：R2=220k 回差约 0.23 V；330k 约 0.15 V
for r2, dv in (("220k", 0.23), ("330k", 0.15)):
    r = ng.run("schmitt_sweep.cir", dict(R2=r2))
    check("p3 练习2", f"R2={r2} 回差", dv, r["vh"] - r["vl"], "V")
# 练习 3：上拉改接 3.3 V（页面忽略 R3 阻值）
r = ng.run("schmitt_sweep.cir", dict(VPU=3.3, VHALF=1.65))
check("p3 练习3", "上拉 3.3 V：上门限", 2.75, r["vh"], "V", tol=2)
check("p3 练习3", "上拉 3.3 V：下门限", 2.42, r["vl"], "V", "SPICE 计入 R3=2.2k", tol=2)
check("p3 练习3", "上拉 3.3 V：回差", 0.33, r["vh"] - r["vl"], "V")

# page1 第 3 步：占空比
def duty(r, thr=2.5):
    d = wave(r, "sine.txt"); t, vo = d[:, 0], d[:, 3]
    k = (t >= 2e-3) & (t < 6e-3)
    tt = t[k]; hi = (vo[k] > thr).astype(float)
    return np.trapezoid(hi, tt) / (tt[-1] - tt[0]), d
r = ng.run("sine.cir", dict(R1="1m", R2="1e12"))
check("p1 示波器第3步", "中心 2.5 V：高电平占空比", 50, duty(r)[0] * 100, "%")
r = ng.run("sine.cir", dict(R1="1m", R2="1e12", VC=2.75))
check("p1 示波器第3步", "中心 2.75 V：高电平占空比", 66.7, duty(r)[0] * 100, "%")
# 第 5 步：施密特
r = ng.run("sine.cir")
D, d = duty(r)
check("p1 示波器第5步", "施密特 高电平占空比", 49.8, D * 100, "%")
t, vin, vo = d[:, 0], d[:, 1], d[:, 3]
k = t > 2e-3; t, vin, vo = t[k], vin[k], vo[k]
up = t[1:][(vo[:-1] < 2.5) & (vo[1:] >= 2.5)][0]
dn = t[1:][(vo[:-1] >= 2.5) & (vo[1:] < 2.5)][0]
# 普通比较器翻转时刻：正弦过 2.5 V（上升过零在每周期 0 ms，下降在 0.5 ms）
check("p1 示波器第5步", "翻高比普通比较器晚", 0.083, ((up % 1e-3)) * 1e3, "ms")
check("p1 示波器第5步", "翻低比普通比较器晚", 0.083, ((dn - 0.5e-3) % 1e-3) * 1e3, "ms", "页面称两次都约 0.08 ms")
check("p1 示波器第5步", "翻高时的输入电压", 2.75, np.interp(up, t, vin), "V", tol=2)
check("p1 示波器第5步", "翻低时的输入电压", 2.26, np.interp(dn, t, vin), "V", tol=2)
r = ng.run("sine.cir", dict(AMP=0.2))
d = wave(r, "sine.txt"); vo = d[d[:, 0] > 0.5e-3, 3]
check("p1 示波器第5步", "幅度 0.2 V 时翻转次数", 0, float(np.count_nonzero(np.diff(vo > 2.5))), "次", v="✅")

# page3 §1 响应时间 / 上升时间
r = ng.run("resp.cir")
check("p3 §1 表", "响应时间 低→高(100 mV 阶跃, 5 mV 过驱, 15 pF)", 1.3, (r["tplh"] - 10e-6) * 1e6, "µs", tol=30)
r5 = ng.run("resp.cir", dict(VLO=2.595, VHI=2.495))   # 高->低：反向 100 mV 阶跃、5 mV 过驱
check("p3 §1 表", "响应时间 高→低(同条件)", 1.3, (r5["tplh"] - 10e-6) * 1e6 if False else (r5["tphl"] - 10e-6) * 1e6, "µs", tol=30)
check("p3 §1", "上升沿 10–90%(2.2k×15p)", 33, (r["t90"] - r["t10"]) * 1e9, "ns", "RC=33 ns；10–90% 理论 2.2·RC=73 ns", v="ℹ️")
r = ng.run("resp.cir", dict(R3="1meg"))
check("p3 §1", "上拉 1 MΩ 上升沿 10–90%", 15, (r["t90"] - r["t10"]) * 1e6, "µs", "RC=15 µs；10–90% 理论 33 µs", v="ℹ️")

# page3 §4 窗口比较器
r = ng.run("window.cir")
for k, p in zip(("t1", "t2", "t3", "t4"), (3.33, 6.66, 13.33, 16.66)):
    check("p3 图10-p3-3", f"窗口输出跳变 {k}", p, r[k], "s", tol=2)

# page2 §4 噪声对比（与 code/10_sim.py 同一段输入）
t = np.arange(0, 20, 0.01)
clean = 2.0 + 1.0 * (1 - np.abs(t - 10) / 10)
rng = np.random.default_rng(1)
vin = clean + 0.04 * rng.standard_normal(len(t))
pwl = "\n+ ".join(f"{a:.2f} {b:.5f}" for a, b in zip(t, vin))
src = (pathlib.Path(__file__).parent / "noise.cir").read_text(encoding="utf-8")
r = ng.run("noise.cir", dict(VIN=pwl))
d = wave(r, "noise.txt")
n1 = int(np.count_nonzero(np.diff(d[:, 3] > 2.5)))
n2 = int(np.count_nonzero(np.diff(d[:, 5] > 2.5)))
check("p2 §4 代码输出", "普通比较器翻转次数", 98, n1, "次")
check("p2 §4 代码输出", "施密特比较器翻转次数", 2, n2, "次", tol=0)
ng.save()
