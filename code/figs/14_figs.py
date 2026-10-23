"""14 电压比较器：全部配图（图 14-p2-2 由 code/14_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/14_figs.py
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

N = "14"
_spec = importlib.util.spec_from_file_location("sim14", os.path.join(HERE, "..", "14_sim.py"))
sim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sim)
V_H, V_L = sim.thresholds()
print(f"[数值] V_ref {sim.VREF} V，R1 {sim.R1/1e3:.0f} kΩ，R2 {sim.R2/1e3:.0f} kΩ，R3 {sim.R3/1e3:.1f} kΩ"
      f" → V_H {V_H:.2f} V，V_L {V_L:.2f} V，回差 {V_H - V_L:.2f} V")


def vref_divider(d, op):
    """反相端：两只 10 kΩ 把 +5 V 分成 2.5 V。"""
    d += elm.Line().left().at(op.in1).length(0.75)
    d += elm.Line().up().length(1.5)
    d += elm.Line().left().length(1.0)
    d += (jr := elm.Dot().label("$V_{ref}$ 2.5 V", "left"))
    d += elm.Resistor().up().label("10 kΩ")
    d += elm.Vdd().label("+5 V")
    d += elm.Resistor().down().at(jr.center).label("10 kΩ")
    d += elm.Ground()


def output_pullup(d, op, start=1.5, r3="$R_3$ 2.2 kΩ\n上拉"):
    d += elm.Line().right().at(op.out).length(start)
    d += (o := elm.Dot())
    d += elm.Resistor().up().label(r3)
    d += elm.Vdd().label("+5 V")
    d += elm.Line().right().at(o.center).length(1.0)
    d += elm.Dot(open=True).label("$V_o$ → 单片机 / LED", "right")


# ---------- 图 14-p1-1 基本比较器 ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True).label("比较器\nLM393", loc="center", ofst=(-0.35, 0), fontsize=9))
    vref_divider(d, op)
    d += elm.Line().left().at(op.in2).length(0.75)
    d += elm.Line().down().length(1.5)
    d += elm.Line().left().length(2.5)
    d += elm.Dot(open=True).label("$V_{in}$ 传感器", "left")
    output_pullup(d, op)
save_schem(d, N, "14_p1_1_basic.png")

# ---------- 图 14-p1-2 单一门限 + 噪声 = 输出抖动 ----------
t, clean, vin = sim.make_input()
o1 = sim.comp_plain(vin)
win = (t > 3.5) & (t < 7.0)
n_win = sim.edges(o1[win])
print(f"[数值] 3.5–7.0 s 内普通比较器翻转 {n_win} 次（整段 {sim.edges(o1)} 次）")
assert n_win > 20
fig, (a0, a1) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True, gridspec_kw=dict(height_ratios=[1.5, 1]))
a0.plot(t[win], vin[win], **fs.LS["vin"], label="传感器电压（含噪声）")
a0.plot(t[win], clean[win], **fs.LS["good"], label="真实温度对应的电压")
fs.ref_h(a0, sim.VREF, "门限 $V_{ref}$ 2.5 V（25 °C）", x=0.01, ha="left")
a0.set_ylabel(fs.qlabel("电压", "V")); a0.legend(loc="lower right", fontsize=8)
a1.plot(t[win], o1[win], **fs.LS["bad"], label=f"比较器输出：3.5 s 内翻转 {n_win} 次")
a1.set_ylim(-0.6, 6.2); a1.set_ylabel(fs.qlabel("输出", "V")); a1.legend(loc="upper left", fontsize=8)
a1.set_xlabel(fs.qlabel("时间", "s"))
fs.save(fig, N, "14_p1_2_chatter.png")

# ---------- 图 14-p1-3 施密特比较器（同相，带回差） ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True).label("比较器\nLM393", loc="center", ofst=(-0.35, 0), fontsize=9))
    vref_divider(d, op)
    d += elm.Line().left().at(op.in2).length(0.75)
    d += elm.Line().down().length(1.5)
    d += (j := elm.Dot())
    d += elm.Resistor().left().label("$R_1$ 10 kΩ")
    d += elm.Dot(open=True).label("$V_{in}$ 传感器", "left")
    d += elm.Resistor().right().at(j.center).label("$R_2$ 100 kΩ（正反馈）", "bottom").tox(op.out.x + 0.75)
    d += elm.Line().up().toy(op.out)
    d += elm.Dot()
    output_pullup(d, op)
save_schem(d, N, "14_p1_3_schmitt.png")

# ---------- 图 14-p2-1 回差曲线（传输特性） ----------
x = np.linspace(2.0, 3.0, 501)
rise = np.where(x > V_H, 5.0, 0.0)
fall = np.where(x < V_L, 0.0, 5.0)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(x, sim.comp_plain(x), **fs.LS["ref"], label="普通比较器（只有一个门限 2.5 V）")
ax.plot(x, rise + 0.06, **fs.LS["vin"], label="输入上升时走的路")
ax.plot(x, fall - 0.06, **fs.LS["vout"], label="输入下降时走的路")
ax.annotate("", (2.62, 0.06), (2.38, 0.06), arrowprops=dict(arrowstyle="->", color=fs.C["vin"], lw=1.5))
ax.annotate("", (2.38, 4.94), (2.62, 4.94), arrowprops=dict(arrowstyle="->", color=fs.C["vout"], lw=1.5))
fs.ref_v(ax, V_H, f"$V_H$ {V_H:.2f} V", y=0.6)
fs.ref_v(ax, V_L, f"$V_L$ {V_L:.2f} V", y=0.6)
ax.annotate("", (V_H, 1.6), (V_L, 1.6), arrowprops=dict(arrowstyle="<->", lw=1))
ax.text((V_H + V_L) / 2, 1.75, f"回差 {V_H - V_L:.2f} V", ha="center", fontsize=9)
fs.axlabels(ax, "输入 $V_{in}$", "V", "输出 $V_o$", "V")
ax.set_ylim(-0.5, 6.4); ax.legend(loc="upper left", fontsize=8)
fs.save(fig, N, "14_p2_1_loop.png")

# ---------- 图 14-p3-1 回差宽度 vs 翻转次数 ----------
R2s = np.array([1000e3, 470e3, 330e3, 220e3, 150e3, 100e3, 68e3])
sigmas = [0.02, 0.04, 0.08]
styles = ["vin", "vout", "third"]
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
result = {}
for sg, st in zip(sigmas, styles):
    _, _, v = sim.make_input(sigma=sg)
    hy, ne = [], []
    for r2 in R2s:
        vh, vl = sim.thresholds(r2=r2)
        hy.append(vh - vl); ne.append(sim.edges(sim.comp_schmitt(v, vh, vl)))
    result[sg] = (np.array(hy), np.array(ne))
    print(f"[扫描] σ = {sg*1e3:.0f} mV：回差 " + "、".join(f"{h:.2f}" for h in hy) + " V → 翻转 " + "、".join(map(str, ne)) + " 次")
    ax.plot(hy, ne, marker="o", **{k: v_ for k, v_ in fs.LS[st].items() if k not in ("marker", "markevery")},
            label=f"噪声 σ = {sg*1e3:.0f} mV")
hy40, ne40 = result[0.04]
assert ne40[-1] == 2 and ne40[0] > 2
assert result[0.02][1][-1] == 2
k = np.flatnonzero(ne40 == 2)[0]
ax.plot([hy40[k]], [2], "o", color="k", ms=5, zorder=6)
ax.annotate(f"σ = 40 mV：回差 {hy40[k]:.2f} V 起\n只翻 2 次（一升一降 = 干净）", (hy40[k], 2), (0.5, 8), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=0.8))
print(f"[标注] σ = 40 mV 时回差 ≥ {hy40[k]:.2f} V 就只翻转 2 次")
fs.ref_h(ax, 2)
ax.set_yscale("log")
ax.set_yticks([2, 5, 10, 20, 50, 100, 200]); ax.set_yticklabels(["2", "5", "10", "20", "50", "100", "200"])  # 2 次那条参考线要有刻度
ax.minorticks_off()
fs.axlabels(ax, "回差 $V_H - V_L$", "V", "20 s 内输出翻转次数", None)
ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "14_p3_1_sweep.png")

# ---------- 图 14-p3-2 窗口比较器 ----------
with drawing() as d:
    d += (A := elm.Opamp(leads=True).label("A", loc="center", ofst=(-0.4, 0)))
    d += (B := elm.Opamp(leads=True).anchor("in1").at((A.in1.x, A.in1.y - 3.5)).label("B", loc="center", ofst=(-0.4, 0)))
    d += elm.Line().left().at(A.in1).length(1.0)
    d += elm.Dot(open=True).label("$V_L$ 2.25 V", "left")
    d += elm.Line().left().at(B.in2).length(1.0)
    d += elm.Dot(open=True).label("$V_H$ 2.75 V", "left")
    d += elm.Line().left().at(A.in2).length(0.5)
    d += (ja := elm.Dot())
    d += elm.Line().down().toy(B.in1)
    d += elm.Line().right().tox(B.in1)
    d += elm.Line().left().at(ja.center).length(2.0)
    d += elm.Dot(open=True).label("$V_{in}$", "left")
    d += elm.Line().right().at(A.out).length(1.0)
    d += (jo := elm.Dot())
    d += elm.Line().down().toy(B.out)
    d += elm.Line().left().tox(B.out)
    d += elm.Resistor().up().at(jo.center).label("2.2 kΩ")
    d += elm.Vdd().label("+5 V")
    d += elm.Line().right().at(jo.center).length(1.25)
    d += elm.Dot(open=True).label("$V_o$（两路输出并在一起）", "right")
save_schem(d, N, "14_p3_2_window.png")

# ---------- 图 14-p3-3 窗口比较器波形 ----------
tw = np.linspace(0, 20, 2001)
vw = 2.5 + 0.5 * np.sin(2 * np.pi * tw / 20 - np.pi / 2) * 1.0
outA = vw > 2.25
outB = vw < 2.75
vo = np.where(outA & outB, 5.0, 0.0)
ins = tw[np.flatnonzero(np.diff(vo) != 0)]
print("[数值] 窗口输出翻转时刻：" + "、".join(f"{x:.2f}" for x in ins) + " s")
assert len(ins) == 4
fig, (a0, a1) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True, gridspec_kw=dict(height_ratios=[1.4, 1]))
a0.plot(tw, vw, **fs.LS["vin"], label="$V_{in}$")
fs.ref_h(a0, 2.75, "$V_H$ 2.75 V", x=0.99)
fs.ref_h(a0, 2.25, "$V_L$ 2.25 V", x=0.99)
a0.set_ylabel(fs.qlabel("电压", "V")); a0.legend(loc="upper left", fontsize=8)
a1.plot(tw, vo, **fs.LS["vout"], label="$V_o$：只在 $V_L$ < $V_{in}$ < $V_H$ 时为高")
for x_ in ins:
    fs.ref_v(a1, x_, f"{x_:.2f}")
a1.set_ylim(-0.6, 6.4); a1.set_ylabel(fs.qlabel("输出", "V")); a1.legend(loc="center", fontsize=8)
a1.set_xlabel(fs.qlabel("时间", "s"))
fs.save(fig, N, "14_p3_3_window_wave.png")
