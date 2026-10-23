"""04 差分放大：全部配图（图 04-p2-2 由 code/04_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/04_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "04"


def diffamp(d, labs=("$R_1$ 10 kΩ", "$R_2$ 100 kΩ", "$R_3$ 10 kΩ", "$R_4$ 100 kΩ"),
            v1="$V_1$", v2="$V_2$", vo="$V_o$ 输出", note_minus=None, note_plus=None, at=None, r4side="bottom"):
    """四电阻差分放大。返回 (op, 左端 V1 点, 左端 V2 点)。"""
    op = elm.Opamp(leads=True).right()
    if at is not None:
        op.at(at).anchor("in1")
    d += op
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j1 := elm.Dot())
    d += elm.Resistor().left().label(labs[0], "top")
    p1 = d.here
    if v1:
        d += elm.Dot(open=True).label(v1, "left")
    up = elm.Line().up().at(j1.center).length(1.5)
    d += up
    d += elm.Resistor().right().label(labs[1]).tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(0.5)
    d += (j2 := elm.Dot())
    d += elm.Resistor().left().label(labs[2], "bottom")
    p2 = d.here
    if v2:
        d += elm.Dot(open=True).label(v2, "left")
    d += elm.Resistor().down().at(j2.center).label(labs[3], r4side)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    if vo:
        d += elm.Dot(open=True).label(vo, "right")
    if note_minus:
        d += elm.Label().at((j1.center[0] + 0.15, j1.center[1] + 0.9)).label(note_minus, halign="left", fontsize=11)
    if note_plus:
        d += elm.Label().at((j2.center[0] + 0.5, j2.center[1] - 1.5)).label(note_plus, halign="left", fontsize=11)
    return op, p1, p2


# ---------- 图 04-p1-2 差分放大电路 ----------
with drawing() as d:
    diffamp(d, v1="$V_1$ 输入 1", v2="$V_2$ 输入 2")
save_schem(d, N, "04_p1_2_circuit.png")
print("差分倍数 R2/R1 = 100 kΩ / 10 kΩ = 10，R4/R3 = 10（两组比例相同）")

# ---------- 图 04-p1-1 两根线上同样的干扰，相减后只剩差值 ----------
t = np.linspace(0, 0.2, 4001)
vd = fs.sine(t, 10, amp=0.5)                          # 为了看得见，这里差分信号取 0.5 V
vcm = fs.sine(t, 50, amp=2.0)
V1, V2 = vcm - vd / 2, vcm + vd / 2
vo = 1.0 * (V2 - V1)                                  # 取倍数 1，只看「相减」
print(f"两根线都带 2 V、50 Hz 干扰；差值峰值 {vd.max():.1f} V；相减后输出峰值 {vo.max():.1f} V")
assert np.allclose(vo, vd)
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"], sharey=True)
a1.plot(t * 1e3, V1, **fs.LS["vin"], label="$V_1$")
a1.plot(t * 1e3, V2, **fs.LS["third"], label="$V_2$")
fs.axlabels(a1, "时间", "ms", "电压", "V"); a1.set_title("两根输入线（都带 50 Hz 干扰）", fontsize=10)
a1.legend(loc="lower right", fontsize=8, ncol=2)
a2.plot(t * 1e3, vo, **fs.LS["vout"], label="$V_2$ − $V_1$")
fs.mark(a2, 25, 0.5, fmt="{:.1f}", unit=" V", dx=6, dy=2)
fs.axlabels(a2, "时间", "ms", None, None); a2.set_title("相减之后（干扰抵消）", fontsize=10)
a2.legend(loc="lower right", fontsize=8)
for a in (a1, a2):
    a.set_ylim(-3, 3)
fs.save(fig, N, "04_p1_1_subtract.png")

# ---------- 图 04-p2-1 推导用的差分放大 ----------
with drawing() as d:
    diffamp(d, v1="$V_1$", v2="$V_2$",
            note_minus="$V_- = V_+$（虚短）",
            note_plus="$V_+ = V_2 \\cdot R_4/(R_3+R_4)$", r4side="top")
save_schem(d, N, "04_p2_1_analysis.png")

# ---------- 图 04-p2-3 三运放仪表放大器 ----------
with drawing() as d:
    d.config(fontsize=11)
    d += (a1 := elm.Opamp(leads=True).flip().label("A1", "center", fontsize=10))
    d += elm.Line().left().at(a1.in2).length(0.8)
    d += elm.Dot(open=True).label("$V_1$", "left")
    d += elm.Line().left().at(a1.in1).length(0.5)
    d += (n1 := elm.Dot())
    d += elm.Line().down().length(1.8)
    d += elm.Resistor().down().label("$R_g$ 1 kΩ", "top")
    d += elm.Line().down().length(1.8)
    d += (n2 := elm.Dot())
    d += elm.Line().right().length(0.5)
    d += (a2 := elm.Opamp(leads=True).anchor("in1").label("A2", "center", fontsize=10))
    d += elm.Line().left().at(a2.in2).length(0.8)
    d += elm.Dot(open=True).label("$V_2$", "left")
    xo = a1.out[0] + 0.6
    # A1 反馈：n1 → 向下 → 电阻 R → 上到 A1 输出
    d += elm.Line().at(n1.center).to((n1.center[0], n1.center[1] - 1.5))
    d += elm.Resistor().right().label("$R$ 10 kΩ", "bottom").tox(xo)
    d += elm.Line().up().toy(a1.out)
    d += elm.Dot()
    d += elm.Line().left().tox(a1.out)
    d += elm.Line().at(n2.center).to((n2.center[0], n2.center[1] + 1.5))
    d += elm.Resistor().right().label("$R$ 10 kΩ", "top").tox(xo)
    d += elm.Line().down().toy(a2.out)
    d += elm.Dot()
    d += elm.Line().left().tox(a2.out)
    # 后级：四个 10 kΩ 的差分放大（倍数 1）
    ymid = (a1.out[1] + a2.out[1]) / 2
    op, p1, p2 = diffamp(d, labs=("10 kΩ", "10 kΩ", "10 kΩ", "10 kΩ"), v1=None, v2=None,
                         vo="$V_o$", at=(xo + 4.6, ymid + 0.6))
    d += elm.Line().at((xo, a1.out[1])).to((p1[0] - 0.5, a1.out[1]))
    d += elm.Line().down().toy(p1[1])
    d += elm.Line().right().tox(p1[0])
    d += elm.Line().at((xo, a2.out[1])).to((p2[0] - 0.5, a2.out[1]))
    d += elm.Line().up().toy(p2[1])
    d += elm.Line().right().tox(p2[0])
save_schem(d, N, "04_p2_3_ina.png")
R, Rg = 10e3, 1e3
G = 1 + 2 * R / Rg
print(f"仪表放大器：倍数 = 1 + 2R/Rg = 1 + 2 × 10 kΩ / 1 kΩ = {G:.0f}（后级 4 个 10 kΩ，倍数 1）")
assert G == 21


def gains(R1, R2, R3, R4):
    """返回 (差分倍数, 共模倍数)。"""
    a = R4 / (R3 + R4) * (1 + R2 / R1)                  # V2 到输出的倍数
    b = R2 / R1                                         # V1 到输出的倍数（取负号）
    return (a + b) / 2, a - b


# ---------- 图 04-p3-1 电阻误差与共模抑制比 ----------
eps = np.logspace(-4, np.log10(0.05), 300)              # 电阻误差 0.01% ～ 5%
one = np.array([20 * np.log10(abs(g[0] / g[1])) for g in (gains(10e3, 100e3, 10e3, 100e3 * (1 + e)) for e in eps)])
worst = np.array([20 * np.log10(abs(g[0] / g[1])) for g in
                  (gains(10e3 * (1 + e), 100e3 * (1 - e), 10e3 * (1 - e), 100e3 * (1 + e)) for e in eps)])
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.semilogx(eps * 100, one, **fs.LS["third"], label="只有 $R_4$ 偏差")
ax.semilogx(eps * 100, worst, **fs.LS["bad"], label="四只电阻都按最坏方向偏差")
for e in (0.001, 0.01):
    g1 = gains(10e3, 100e3, 10e3, 100e3 * (1 + e)); c1 = 20 * np.log10(abs(g1[0] / g1[1]))
    g4 = gains(10e3 * (1 + e), 100e3 * (1 - e), 10e3 * (1 - e), 100e3 * (1 + e)); c4 = 20 * np.log10(abs(g4[0] / g4[1]))
    print(f"电阻误差 {e*100:g}%：只偏一只 CMRR {c1:.0f} dB，四只最坏 {c4:.0f} dB")
    fs.mark(ax, e * 100, c1, fmt="{:.0f}", unit=" dB", dx=6, dy=4)
    fs.mark(ax, e * 100, c4, fmt="{:.0f}", unit=" dB", dx=-40, dy=-14)
g = gains(10e3 * 1.01, 100e3 * 0.99, 10e3 * 0.99, 100e3 * 1.01)
assert 40 < 20 * np.log10(abs(g[0] / g[1])) < 50                 # 1% 电阻最坏只有 40 多 dB
fs.axlabels(ax, "电阻误差", "%", "共模抑制比 CMRR", "dB")
ax.set_ylim(20, 110); ax.legend(loc="upper right", fontsize=8)
ax.set_xticks([0.01, 0.1, 1]); ax.set_xticklabels(["0.01", "0.1", "1"])
fs.save(fig, N, "04_p3_1_cmrr_tolerance.png")

# ---------- 图 04-p3-2 信号源内阻（只在 V1 一侧）破坏平衡 ----------
Rs = np.logspace(0, 4, 300)                              # 1 Ω ～ 10 kΩ
cm = np.array([20 * np.log10(abs(g[0] / g[1])) for g in (gains(10e3 + r, 100e3, 10e3, 100e3) for r in Rs)])
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.semilogx(Rs, cm, **fs.LS["bad"], label="$V_1$ 一侧串入内阻 $R_s$")
for r in (100, 1000):
    gg = gains(10e3 + r, 100e3, 10e3, 100e3); c = 20 * np.log10(abs(gg[0] / gg[1]))
    print(f"内阻 {r} Ω：CMRR 降到 {c:.0f} dB，差分倍数 {gg[0]:.2f}")
    fs.mark(ax, r, c, fmt="{:.0f}", unit=" dB", dx=6, dy=4)
fs.ref_h(ax, 61, "61 dB（1% 电阻只偏一只）", x=0.02, ha="left")
assert 20 * np.log10(abs(gains(11e3, 100e3, 10e3, 100e3)[0] / gains(11e3, 100e3, 10e3, 100e3)[1])) < 45
fs.axlabels(ax, "信号源内阻 $R_s$", "Ω", "共模抑制比 CMRR", "dB")
ax.set_ylim(20, 110); ax.legend(loc="upper right", fontsize=8)
ax.set_xticks([1, 10, 100, 1e3, 1e4]); ax.set_xticklabels(["1", "10", "100", "1 k", "10 k"])
fs.save(fig, N, "04_p3_2_source_resistance.png")
