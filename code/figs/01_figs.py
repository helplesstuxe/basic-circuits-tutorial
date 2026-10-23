"""01 反相放大：全部配图（图 01-p2-2 由 code/01_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/01_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "01"
R1, Rf = 10e3, 100e3


def inverting(d, r1="$R_1$ 10 kΩ", rf="$R_f$ 100 kΩ", vin="$V_i$ 输入", vminus=None, cur=False):
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    r = elm.Resistor().left().label(r1)
    if cur:
        r.label("$I \\rightarrow$", "bottom")      # 电流方向
    d += r
    d += elm.Dot(open=True).label(vin, "left")
    up = elm.Line().up().at(j.center).length(2.3 if vminus else 1.5)
    if vminus:
        up.label(vminus, "bottom", fontsize=11)      # 标在竖线右侧
    d += up
    rr = elm.Resistor().right().label(rf).tox(op.out.x + 0.5)
    if cur:
        rr.label("$I \\rightarrow$", "bottom")
    d += rr
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(0.5)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$ 输出", "right")
    return op


# ---------- 图 01-p1-1 反相放大电路 ----------
with drawing() as d:
    inverting(d)
save_schem(d, N, "01_p1_1_circuit.png")

# ---------- 图 01-p1-2 电压「跷跷板」：沿 R1、Rf 的电压分布 ----------
Vi = 0.5
Vo = -Rf / R1 * Vi
x = np.array([0, R1, R1 + Rf]) / 1e3                 # 沿电阻链累计的电阻（kΩ）：输入端 0，反相端 10，输出端 110
v = np.array([Vi, 0.0, Vo])
print(f"输入端 {Vi} V，反相端（虚地）0 V，输出端 {Vo} V；斜率每 kΩ {(Vo - Vi) / 110:.3f} V")
assert abs((Vi - 0) / R1 - (0 - Vo) / Rf) < 1e-12      # 两段电阻上的电流相等（虚断）
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(x, v, **fs.LS["third"], label="沿 $R_1$ → $R_f$ 的电压")
ax.axvspan(0, 10, color=fs.C["fill"], alpha=0.8, lw=0)
ax.axvspan(10, 110, color=fs.C["fill2"], alpha=0.8, lw=0)
ax.text(5, -4.2, "$R_1$\n10 kΩ", ha="center", fontsize=9)
ax.text(60, -4.2, "$R_f$　100 kΩ", ha="center", fontsize=9)
ax.plot([0], [Vi], "o", color=fs.C["vin"], ms=6, zorder=6)
ax.plot([110], [Vo], "o", color=fs.C["vout"], ms=6, zorder=6)
ax.plot([10], [0], "^", color="k", ms=9, zorder=6)
fs.mark(ax, 0, Vi, fmt="{:.1f}", unit=" V", dx=6, dy=4)
fs.mark(ax, 110, Vo, fmt="{:.1f}", unit=" V", dx=-34, dy=-12)
ax.annotate("虚地 0 V（支点）", (10, 0), (25, 1.2), fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))
fs.ref_h(ax, 0, "0 V")
fs.axlabels(ax, "从输入端算起经过的电阻", "kΩ", "电压", "V")
ax.set_xlim(-3, 113); ax.set_ylim(-6, 2); ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "01_p1_2_seesaw.png")

# ---------- 图 01-p1-3 输入与输出：倒过来、放大 ----------
t = np.linspace(0, 2e-3, 1001)
vi = fs.sine(t, 1e3, amp=0.5)
vo = -2 * vi                                          # 取 Rf/R1 = 2，便于和输入放在同一坐标里看
print(f"放大 2 倍反相：输入峰值 0.5 V → 输出峰值 {vo.max():.1f} V，输入最高时（0.25 ms）输出 {vo[125]:.1f} V")
assert abs(vo[125] + 1.0) < 1e-9
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi, **fs.LS["vin"], label="$V_i$ 输入")
ax.plot(t * 1e3, vo, **fs.LS["vout"], label="$V_o$ 输出（$R_f/R_1$ = 2）")
fs.ref_h(ax, 0, "0 V")
fs.mark(ax, 0.25, vi[125], fmt="{:.1f}", unit=" V", dx=6, dy=2)
fs.mark(ax, 0.25, vo[125], fmt="{:.1f}", unit=" V", dx=6, dy=-10)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "01_p1_3_invert_wave.png")

# ---------- 图 01-p2-1 虚短虚断分析图 ----------
with drawing() as d:
    inverting(d, vminus="虚地 $V_-$ ≈ 0 V", cur=True)
save_schem(d, N, "01_p2_1_analysis.png")

# ---------- 图 01-p2-3 反相加法器 ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot().label("虚地", "bottom", ofst=0.15))
    d += elm.Line().left().length(0.5)
    d += (k := elm.Dot())
    d += elm.Resistor().left().label("$R_1$ 10 kΩ")
    d += elm.Dot(open=True).label("$V_1$", "left")
    d += elm.Line().up().at(k.center).length(1.4)
    d += elm.Resistor().left().label("$R_2$ 10 kΩ")
    d += elm.Dot(open=True).label("$V_2$", "left")
    d += elm.Line().up().at(j.center).length(2.6)
    d += elm.Resistor().right().label("$R_f$ 10 kΩ").tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(0.5)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$", "right")
save_schem(d, N, "01_p2_3_summer.png")

# ---------- 图 01-p2-4 加法器波形：两个信号混在一起 ----------
t = np.linspace(0, 2e-3, 2001)
v1 = fs.sine(t, 1e3, amp=0.5)
v2 = fs.sine(t, 5e3, amp=0.2)
vo = -(v1 + v2)                                       # R1 = R2 = Rf，所以 V_o = −(V_1 + V_2)
print(f"加法器：V1 峰值 0.5 V（1 kHz），V2 峰值 0.2 V（5 kHz），输出最低 {vo.min():.2f} V、最高 {vo.max():.2f} V")
assert abs(vo.max() - 0.7) < 0.01
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, v1, **fs.LS["vin"], label="$V_1$（1 kHz）")
ax.plot(t * 1e3, v2, **fs.LS["third"], label="$V_2$（5 kHz）")
ax.plot(t * 1e3, vo, **fs.LS["vout"], label="$V_o = -(V_1 + V_2)$")
k = np.argmax(vo)
fs.mark(ax, t[k] * 1e3, vo[k], fmt="{:.2f}", unit=" V", dx=6, dy=2)
fs.ref_h(ax, 0, "0 V")
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8)
fs.save(fig, N, "01_p2_4_summer_wave.png")

# ---------- 图 01-p3-1 信号源内阻的影响：R1 不能太小 ----------
R1s = np.logspace(2, 6, 200)                          # R1 从 100 Ω 扫到 1 MΩ，始终保持 Rf = 10·R1
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.axhline(10, **fs.LS["good"], label="理想 $|A_v|$ = 10")
for Rs, key in ((1e3, "vout"), (100, "third")):
    g = 10 * R1s / (R1s + Rs)                         # 源内阻和 R1 串联：|A_v| = Rf / (Rs + R1)
    ax.semilogx(R1s, g, **fs.LS[key], label=f"信号源内阻 {Rs:g} Ω")
    for r in (1e3, 10e3):
        gv = 10 * r / (r + Rs)
        fs.mark(ax, r, gv, fmt="{:.2f}", dx=4, dy=-12 if key == "vout" else 4)
g1k = 10 * 10e3 / (10e3 + 1e3)
print(f"内阻 1 kΩ、R1 = 10 kΩ 时 |A_v| = {g1k:.2f}；R1 = 1 kΩ 时只有 {10*1e3/2e3:.2f}")
assert abs(g1k - 9.09) < 0.01
fs.axlabels(ax, "输入电阻 $R_1$（$R_f$ 始终取 10 $R_1$）", "Ω", "放大倍数 $|A_v|$", None)
ax.set_ylim(0, 11); ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "01_p3_1_source_loading.png")

# ---------- 图 01-p3-2 放大倍数随频率下降（增益带宽积 GBW） ----------
GBW = 1.2e6                                           # LM358B 典型增益带宽积 1.2 MHz
f = np.logspace(2, 7, 400)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
for G, key in ((1, "vout"), (10, "third"), (100, "fb")):
    fc = GBW / (1 + G)                                # 闭环带宽 ≈ GBW / (1 + |A_v|)
    mag = G / np.sqrt(1 + (f / fc) ** 2)              # 只用幅值公式：频率到 fc 时倍数降到 0.707 倍
    ax.loglog(f, mag, **fs.LS[key], label=f"$|A_v|$ = {G}：$f_c$ ≈ {fc/1e3:.0f} kHz")
    fs.mark(ax, fc, G / np.sqrt(2), fmt="{:.2g}", dx=5, dy=4)
    print(f"|A_v| = {G}: 带宽 f_c ≈ {fc/1e3:.1f} kHz，此处倍数 {G/np.sqrt(2):.2f}")
assert abs(GBW / 11 - 109.1e3) < 100
fs.axlabels(ax, "频率", "Hz", "放大倍数 $|A_v|$", None); ax.legend(loc="lower left", fontsize=8)
fs.save(fig, N, "01_p3_2_bandwidth.png")

# ---------- page3 正文与练习里的其余数字（只打印 + 断言，不画图） ----------
k = 1 / np.sqrt(2)
print(f"0.707 的来历：1/√2 = {k:.4f}；倍数降到 1/√2 时输出功率 ∝ 电压² 降到 {k**2:.2f} 倍（一半）")
assert abs(k - 0.7071) < 1e-4 and abs(k**2 - 0.5) < 1e-12
print(f"放大 1000 倍拆两级：每级 √1000 = {np.sqrt(1000):.1f} 倍，32 × 32 = {32*32}")
assert abs(np.sqrt(1000) - 31.6) < 0.1
SR, Vp = 0.5e6, 10.0                                  # 压摆率 0.5 V/μs = 0.5e6 V/s；输出峰值 10 V
f_sr = SR / (2 * np.pi * Vp)                          # 正弦最大斜率 2πf·Vp ≤ SR
print(f"压摆率限制：峰值 {Vp:g} V 的正弦，频率不超过 {f_sr:.0f} Hz（约 8 kHz）")
assert 7900 < f_sr < 8000
Rs = 500
g_ideal, g_1M, g_1M_rs = 20, 1e6 / 51e3, 1e6 / (51e3 + Rs)
print(f"练习 2(1)：1 MΩ/51 kΩ = {g_1M:.2f}（取整误差 {100*(1-g_1M/20):.1f}%），计入 500 Ω 内阻后 {g_1M_rs:.2f}（总误差 {100*(1-g_1M_rs/20):.1f}%）")
assert abs(g_1M_rs - 19.42) < 0.01 and 2.8 < 100 * (1 - g_1M_rs / 20) < 3.0
print(f"练习 2(2)：最大输入峰值 10.5/20 = {10.5/20:.3f} V；(3) 带宽 1.2 MHz/21 = {GBW/21/1e3:.1f} kHz")
assert abs(10.5 / 20 - 0.525) < 1e-12 and abs(GBW / 21 - 57.1e3) < 100
Vi_pk, Vo_sat = 2.0, -14.9                            # 练习 3：输入峰值 2 V，−10 倍，输出卡在 −14.9 V
Vm = (Vi_pk * 100e3 + Vo_sat * 10e3) / 110e3          # 反相端电压 = 两端电压按 R1、Rf 分压
print(f"练习 3：输入 +{Vi_pk:g} V、输出卡在 {Vo_sat} V 时，反相端电压 {Vm:.3f} V；R1 电流 {(Vi_pk-Vm)/10:.3f} mA，Rf 电流 {(Vm-Vo_sat)/100:.3f} mA")
assert abs(Vm - 0.464) < 0.001
