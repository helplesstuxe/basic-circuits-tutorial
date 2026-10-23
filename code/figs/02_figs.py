"""02 同相放大：全部配图（图 02-p2-2 由 code/02_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/02_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "02"


def noninverting(d, r1="$R_1$ 10 kΩ", rf="$R_f$ 20 kΩ", vminus=None, vplus=None):
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    d += elm.Resistor().left().label(r1)
    d += elm.Ground().right()                          # R1 另一端接地
    up = elm.Line().up().at(j.center).length(2.3 if vminus else 1.5)
    if vminus:
        up.label(vminus, "bottom", fontsize=11)
    d += up
    d += elm.Resistor().right().label(rf).tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    pl = elm.Line().left().at(op.in2).length(3.5)
    if vplus:
        pl.label(vplus, "bottom", fontsize=11)
    d += pl
    d += elm.Dot(open=True).label("$V_i$ 输入", "left")
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$ 输出", "right")
    return op


# ---------- 图 02-p1-1 同相放大电路 ----------
with drawing() as d:
    noninverting(d)
save_schem(d, N, "02_p1_1_circuit.png")

# ---------- 图 02-p1-2 电压「杠杆」：从地沿 R1、Rf 到输出 ----------
R1, Rf, Vi = 10e3, 20e3, 0.5
Vo = (1 + Rf / R1) * Vi
x = np.array([0, R1, R1 + Rf]) / 1e3                 # 从地算起经过的电阻（kΩ）：地 0，反相端 10，输出 30
v = np.array([0.0, Vi, Vo])
print(f"地 0 V，反相端 {Vi} V（= 输入，虚短），输出端 {Vo} V")
assert abs((Vi - 0) / R1 - (Vo - Vi) / Rf) < 1e-12     # 同一电流流过 R1 和 Rf（虚断）
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(x, v, **fs.LS["third"], label="沿 地 → $R_1$ → $R_f$ 的电压")
ax.axvspan(0, 10, color=fs.C["fill"], alpha=0.8, lw=0)
ax.axvspan(10, 30, color=fs.C["fill2"], alpha=0.8, lw=0)
ax.text(5, 1.6, "$R_1$\n10 kΩ", ha="center", fontsize=9)
ax.text(20, 1.6, "$R_f$　20 kΩ", ha="center", fontsize=9)
ax.plot([0], [0], "^", color="k", ms=9, zorder=6)
ax.plot([10], [Vi], "o", color=fs.C["vin"], ms=6, zorder=6)
ax.plot([30], [Vo], "o", color=fs.C["vout"], ms=6, zorder=6)
fs.mark(ax, 10, Vi, fmt="{:.1f}", unit=" V", dx=6, dy=-12)
fs.mark(ax, 30, Vo, fmt="{:.1f}", unit=" V", dx=-36, dy=4)
ax.annotate("地 0 V（支点）", (0, 0), (3, -0.35), fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))
fs.axlabels(ax, "从地算起经过的电阻", "kΩ", "电压", "V")
ax.set_xlim(-1.5, 32); ax.set_ylim(-0.5, 2.0); ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "02_p1_2_lever.png")

# ---------- 图 02-p1-3 输入与输出：同方向放大 ----------
t = np.linspace(0, 2e-3, 1001)
vi = fs.sine(t, 1e3, amp=0.5)
vo = 3 * vi
print(f"放大 3 倍同相：输入峰值 0.5 V → 输出峰值 {vo.max():.1f} V，0.25 ms 时输入 {vi[125]:.1f} V、输出 {vo[125]:.1f} V")
assert abs(vo[125] - 1.5) < 1e-9
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi, **fs.LS["vin"], label="$V_i$ 输入")
ax.plot(t * 1e3, vo, **fs.LS["vout"], label="$V_o$ 输出（3 倍）")
fs.ref_h(ax, 0, "0 V")
fs.mark(ax, 0.25, vi[125], fmt="{:.1f}", unit=" V", dx=6, dy=-12)
fs.mark(ax, 0.25, vo[125], fmt="{:.1f}", unit=" V", dx=6, dy=2)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "02_p1_3_inphase_wave.png")

# ---------- 图 02-p2-1 分析图 ----------
with drawing() as d:
    noninverting(d, vminus="$V_- \\approx V_i$（虚短）", vplus="$I \\approx 0$（虚断）")
save_schem(d, N, "02_p2_1_analysis.png")

# ---------- 图 02-p2-3 两种接法的倍数对比 ----------
k = np.linspace(0, 10, 101)                           # 电阻比 Rf/R1
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(k, 1 + k, **fs.LS["vout"], label="同相：$1 + R_f/R_1$")
ax.plot(k, k, **fs.LS["third"], label="反相：$R_f/R_1$（取绝对值）")
fs.ref_h(ax, 1, "1 倍")
for kk in (0, 2):
    fs.mark(ax, kk, 1 + kk, fmt="{:.0f}", dx=-4, dy=8)
print("电阻比 0 时同相倍数 1（跟随器），电阻比 2 时同相 3 倍、反相 2 倍")
assert (1 + k).min() == 1
fs.axlabels(ax, "电阻比 $R_f/R_1$", None, "放大倍数", None); ax.legend(loc="upper left", fontsize=8)
fs.save(fig, N, "02_p2_3_gain_compare.png")

# ---------- 图 02-p3-1 单电源 5 V：输入太大就削顶 ----------
VCC, V_HI = 5.0, 5.0 - 1.5                            # LM358B 正向摆幅约 V+ − 1.5 V
vin = np.linspace(0, 2.5, 251)
vout = np.clip(2 * vin, 0.0, V_HI)                    # 2 倍同相放大，输出不超过 3.5 V（低端约 0 V，此处忽略 0.1 V）
v_knee = V_HI / 2
print(f"单电源 5 V、2 倍：输出最高 {V_HI} V，输入超过 {v_knee:.2f} V 开始削顶")
assert abs(v_knee - 1.75) < 1e-9
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(vin, 2 * vin, **fs.LS["good"], label="理想 $V_o = 2V_i$")
ax.plot(vin, vout, **fs.LS["vout"], label="实际 $V_o$")
fs.ref_h(ax, V_HI, f"{V_HI} V（摆幅上限）", x=0.05, ha="left")
fs.ref_v(ax, v_knee, f"{v_knee:.2f} V", y=0.4)
fs.mark(ax, v_knee, V_HI, fmt="{:.1f}", unit=" V", dx=6, dy=-14)
fs.axlabels(ax, "输入 $V_i$", "V", "输出 $V_o$", "V"); ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "02_p3_1_single_supply_clip.png")

# ---------- 图 02-p3-2 带宽：同相 f_c ≈ GBW / A_v ----------
GBW = 1.2e6
f = np.logspace(2, 7, 400)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
for G, key in ((2, "vout"), (10, "third"), (100, "fb")):
    fc = GBW / G                                      # 同相放大：带宽 ≈ GBW / A_v
    mag = G / np.sqrt(1 + (f / fc) ** 2)
    ax.loglog(f, mag, **fs.LS[key], label=f"$A_v$ = {G}：$f_c$ ≈ {fc/1e3:.0f} kHz")
    fs.mark(ax, fc, G / np.sqrt(2), fmt="{:.2g}", dx=5, dy=4)
    print(f"A_v = {G}: 带宽 f_c ≈ {fc/1e3:.1f} kHz，此处倍数 {G/np.sqrt(2):.2f}")
assert abs(GBW / 10 - 120e3) < 1
fs.axlabels(ax, "频率", "Hz", "放大倍数", None); ax.legend(loc="lower left", fontsize=8)
fs.save(fig, N, "02_p3_2_bandwidth.png")

# ---------- 正文与练习里的其余数字（只打印 + 断言） ----------
IB = 10e-9                                            # LM358B 输入偏置电流典型值 10 nA（最大 35 nA，TI 手册）
for Rsrc in (100e6,):
    print(f"输入电流 {IB*1e9:g} nA 流过 {Rsrc/1e6:g} MΩ 内阻，误差电压 {IB*Rsrc:.1f} V（最大 35 nA 时 {35e-9*Rsrc:.1f} V）")
assert abs(IB * 100e6 - 1.0) < 1e-9
Rs, R1, Rf, Vs = 50e3, 10e3, 20e3, 1.0                 # 新练习 2：内阻 50 kΩ 的分压器输出 1 V
v_inv = -Rf / (Rs + R1) * Vs
v_non = (1 + Rf / R1) * Vs
print(f"练习 2：反相 {v_inv:.3f} V（只有理想 -2 V 的 {v_inv/-2*100:.0f}%），同相 {v_non:.1f} V")
assert abs(v_inv + 0.333) < 0.001 and v_non == 3.0
print(f"带宽两种写法：反馈分压比 R1/(R1+Rf)，同相 10 倍 → {1.2e6/10/1e3:.0f} kHz，反相 10 倍 → {1.2e6/11/1e3:.0f} kHz")
