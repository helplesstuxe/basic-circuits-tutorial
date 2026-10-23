"""12 积分电路：全部配图（图 12-p2-3 由 code/12_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/12_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "12"
_spec = importlib.util.spec_from_file_location("sim12", os.path.join(HERE, "..", "12_sim.py"))
sim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sim)
RC = sim.R * sim.C
print(f"[数值] R {sim.R/1e3:.0f} kΩ，C {sim.C*1e9:.0f} nF → RC {RC*1e3:.1f} ms")


def integrator(d, rf=None, cur=False):
    """反相积分器：01 节的反相放大把 R_f 换成电容 C；rf 不为 None 时在 C 旁再并一个电阻。"""
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot().label("虚地 0 V", "bottom", ofst=0.15) if cur else elm.Dot())
    r = elm.Resistor().left().label("$R$ 10 kΩ")
    if cur:
        r.label("$I \\rightarrow$", "bottom")
    d += r
    d += elm.Dot(open=True).label("$V_i$ 输入", "left")
    d += elm.Line().up().at(j.center).length(1.5)
    d += (a := elm.Dot()) if rf else elm.Line().length(0)
    c = elm.Capacitor().right().label("$C$ 100 nF").tox(op.out.x + 0.5)
    if cur:
        c.label("$I \\rightarrow$ 给电容充电", "bottom")
    d += c
    d += (b := elm.Dot()) if rf else elm.Line().length(0)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    if rf:
        d += elm.Line().up().at(a.center).length(1.5)
        d += elm.Resistor().right().label(rf).tox(b.center.x)
        d += elm.Line().down().toy(b.center)
    d += elm.Line().left().at(op.in2).length(0.5)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$ 输出", "right")


# ---------- 图 12-p1-1 面积直觉：输出 = −(输入曲线下的面积) ÷ RC ----------
t = np.arange(0, 6e-3, 1e-6)
vin = np.select([t < 2e-3, t < 3e-3, t < 5e-3], [1.0, 0.0, -0.5], 0.0)
vo = sim.integrate(t, vin)
fig, (a0, a1) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
tm = t * 1e3
a0.plot(tm, vin, **fs.LS["vin"], label="输入电压 $V_i$")
a0.fill_between(tm, 0, vin, where=vin > 0, color=fs.C["vin"], alpha=0.25)
a0.fill_between(tm, 0, vin, where=vin < 0, color=fs.C["bad"], alpha=0.25)
a0.text(1.0, 0.45, "面积 +2 V·ms", ha="center", fontsize=9)
a0.text(4.0, -0.3, "面积 −1 V·ms", ha="center", fontsize=9)
print("[数值] 面积 +2 V·ms（1 V × 2 ms），−1 V·ms（−0.5 V × 2 ms）")
fs.ref_h(a0, 0)
a0.set_ylim(-0.9, 1.4); a0.set_ylabel(fs.qlabel("输入", "V")); a0.legend(loc="upper right", fontsize=8)
a1.plot(tm, vo, **fs.LS["vout"], label="积分器输出 $V_o$（RC = 1 ms）")
for x in (2.0, 3.0, 5.0):
    k = int(round(x * 1e3))
    fs.mark(a1, x, vo[k], "{:.1f}", " V", dx=4, dy=-12)
assert abs(vo[2000] + 2.0) < 0.01 and abs(vo[3000] + 2.0) < 0.01 and abs(vo[5000] + 1.0) < 0.01
fs.ref_h(a1, 0)
a1.set_ylim(-2.6, 0.6); a1.set_ylabel(fs.qlabel("输出", "V")); a1.legend(loc="upper right", fontsize=8)
a1.set_xlabel(fs.qlabel("时间", "ms"))
fs.save(fig, N, "12_p1_1_area.png")

# ---------- 图 12-p1-2 积分器电路 ----------
with drawing() as d:
    integrator(d)
save_schem(d, N, "12_p1_2_integrator.png")

# ---------- 图 12-p1-3 方波进、三角波出 ----------
t = np.arange(0, 6e-3, 1e-6)
vin = sim.square(t)
vo = sim.integrate(t, vin)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vin, **fs.LS["vin"], label="输入：±1 V、500 Hz 方波")
ax.plot(t * 1e3, vo, **fs.LS["vout"], label="输出：三角波")
ax.annotate("输入 +1 V：\n每 ms 下降 1 V", (0.5, -0.5), xytext=(0.15, -1.75), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="0.3"))
ax.annotate("输入 −1 V：\n每 ms 上升 1 V", (1.5, -0.5), xytext=(2.2, -1.75), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="0.3"))
pp = vo.max() - vo.min()
print(f"[数值] 斜率 ±1 V/ms，三角波峰峰值 {pp:.2f} V（0 到 −1 V）")
assert abs(pp - 1.0) < 0.01
fs.ref_h(ax, 0)
ax.set_ylim(-2.2, 1.9)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.legend(loc="upper right", fontsize=8, ncol=2)
fs.save(fig, N, "12_p1_3_square_triangle.png")

# ---------- 图 12-p2-1 推导用：电流 I 和虚地 ----------
with drawing() as d:
    integrator(d, cur=True)
save_schem(d, N, "12_p2_1_analysis.png")

# ---------- 图 12-p2-2 实用积分器：C 旁并 R_f ----------
with drawing() as d:
    integrator(d, rf="$R_f$ 1 MΩ（给直流一条出路）")
save_schem(d, N, "12_p2_2_practical.png")

# ---------- 图 12-p3-1 R_f 怎么选：大了漂得远，小了三角波变形 ----------
rfs = [10e3, 100e3, 1e6, 10e6]
t = np.arange(0, 3.0, 5e-6)
centers = []
for rf in rfs:
    v = sim.integrate(t, sim.square(t, offset=sim.OFFSET), rf=rf)
    centers.append(v[t > 2.9].mean())
    print(f"[数值] R_f {rf/1e3:g} kΩ：20 mV 偏置下输出中心 {centers[-1]:.2f} V（理论 −R_f/R×20 mV = {-rf/sim.R*0.02:.2f} V）")
assert abs(centers[2] + 2.0) < 0.05 and centers[3] < -12      # 10 MΩ 已经接近饱和
fig, (a0, a1) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a0.semilogx(rfs, centers, **{**fs.LS["bad"], "marker": "o", "markevery": 1})
for rf, c in zip(rfs, centers):
    txt = f"{c:.2f} V（顶到饱和）" if rf > 5e6 else f"{c:.2f} V"
    a0.annotate(txt, (rf, c), xytext=(-70, 10) if rf > 5e6 else (6, 4), textcoords="offset points", fontsize=8)
fs.ref_h(a0, -sim.VSAT, "−13.5 V 饱和", x=0.02, ha="left")
a0.set_xlim(5e3, 3e7); a0.set_ylim(-15, 1.5)
fs.axlabels(a0, "$R_f$", "Ω", "输出中心电平", "V")
a0.set_title("(a) 20 mV 偏置把输出推离 0 V", fontsize=10)
ts = np.arange(0, 0.2, 2e-6)
styles = [fs.LS["bad"], fs.LS["third"], fs.LS["vout"]]
pps = []
for rf, st in zip(rfs[:3], styles):
    v = sim.integrate(ts, sim.square(ts), rf=rf)
    k = ts > 0.2 - 4e-3
    pps.append(v[k].max() - v[k].min())
    a1.plot((ts[k] - ts[k][0]) * 1e3, v[k], **st, label=f"$R_f$ = {rf/1e3:g} kΩ：峰峰 {pps[-1]:.2f} V")
    print(f"[数值] R_f {rf/1e3:g} kΩ：500 Hz 方波稳定后输出峰峰值 {pps[-1]:.2f} V（理想 1.00 V）")
assert 0.9 < pps[0] < 0.95 and abs(pps[1] - 1.0) < 0.02 and abs(pps[2] - 1.0) < 0.02
a1.set_ylim(-1.0, 1.0)
fs.axlabels(a1, "时间", "ms", "输出", "V"); a1.legend(loc="lower right", fontsize=7)
a1.set_title("(b) $R_f$ 太小：三角波被压扁、变圆", fontsize=10)
fig.tight_layout()
fs.save(fig, N, "12_p3_1_rf_sweep.png")

# ---------- 图 12-p3-2 时间常数 RC 怎么选 ----------
t = np.arange(0, 6e-3, 1e-6)
vin = sim.square(t)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
for c, st in zip([5e-9, 100e-9, 1e-6], [fs.LS["bad"], fs.LS["vout"], fs.LS["third"]]):
    v = sim.integrate(t, vin, c=c)
    pp = v.max() - v.min()
    rc = sim.R * c * 1e3
    print(f"[数值] C {c*1e9:g} nF（RC {rc:g} ms）：输出峰峰 {pp:.2f} V，最低 {v.min():.2f} V")
    ax.plot(t * 1e3, v, **st, label=(f"C = {c*1e9:g} nF" if c < 1e-6 else "C = 1 μF") + f"，RC = {rc:g} ms：峰峰 {pp:.2f} V")
    if c == 5e-9:
        assert v.min() <= -sim.VSAT + 1e-6
fs.ref_h(ax, -sim.VSAT, "−13.5 V 饱和（被削平）", x=0.99)
ax.set_ylim(-15, 17)
fs.axlabels(ax, "时间", "ms", "输出", "V"); ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "12_p3_2_rc_choice.png")
