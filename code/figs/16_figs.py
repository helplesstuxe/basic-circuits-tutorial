"""16 振荡器：全部配图（图 16-p2-3 由 code/16_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/16_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "16"

def relax(d):
    d += (op := elm.Opamp(leads=True, flip=True).right())
    P = (op.out.x + 0.8, 0)
    d += elm.Line().endpoints(op.out, P); d += elm.Dot().at(P)
    d += elm.Line().right().at(P).length(0.8); d += elm.Dot(open=True).label("$V_o$", "right")
    # + 端：三个电阻
    B = (-1.6, op.in2.y); J = (-0.5, op.in2.y)
    d += elm.Line().endpoints(op.in2, B); d += elm.Dot().at(B); d += elm.Dot().at(J)
    d += elm.Resistor().up().at(B).length(2.0).label("$R_a$ 10 kΩ", "top")
    d += elm.Vdd().label("+5 V")
    d += elm.Line().endpoints(B, (-3.6, op.in2.y))
    d += elm.Resistor().down().length(2.0).label("$R_b$ 10 kΩ", "top"); d += elm.Ground()
    d += elm.Line().up().at(P).toy(2.0)
    d += elm.Resistor().left().tox(J[0]).label("$R_c$ 10 kΩ")
    d += elm.Line().down().toy(op.in2.y)
    # − 端：R 和 C
    A = (-1.3, op.in1.y); K = (-0.4, op.in1.y)
    d += elm.Line().endpoints(op.in1, A); d += elm.Dot().at(K)
    d += elm.Capacitor().down().at(A).length(1.8).label("$C$ 100 nF", "top"); d += elm.Ground()
    d += elm.Dot().at(A).label("$V_C$", "left")
    d += elm.Line().down().at(P).toy(-2.0)
    d += elm.Resistor().left().tox(K[0]).label("$R$ 10 kΩ", "bottom")
    d += elm.Line().up().toy(op.in1.y)
    return op

def wien(d, rf="$R_f$ 22 kΩ"):
    d += (op := elm.Opamp(leads=True, flip=True).right())
    P = (op.out.x + 0.8, 0)
    d += elm.Line().endpoints(op.out, P); d += elm.Dot().at(P)
    d += elm.Line().right().at(P).length(0.8); d += elm.Dot(open=True).label("$V_o$", "right")
    y2 = op.in2.y
    B = (-1.6, y2); J = (-0.6, y2); Cx = -4.0
    d += elm.Line().endpoints(op.in2, (Cx, y2)); d += elm.Dot().at(B); d += elm.Dot().at(J)
    d += elm.Resistor().down().at(B).length(1.6).label("$R$ 10 kΩ", "top"); d += elm.Ground()
    d += elm.Capacitor().down().at((Cx, y2)).length(1.6).label("$C$ 10 nF", "top"); d += elm.Ground()
    d += elm.Line().up().at(J).toy(2.0)
    d += elm.Capacitor().right().length(1.8).label("$C$ 10 nF")
    d += elm.Resistor().right().tox(P[0]).label("$R$ 10 kΩ")
    d += elm.Line().down().toy(0)
    y1 = op.in1.y; K = (-0.4, -2.4)
    d += elm.Line().endpoints(op.in1, (-0.4, y1)); d += elm.Line().endpoints((-0.4, y1), K); d += elm.Dot().at(K)
    d += elm.Resistor().right().at(K).tox(P[0]).label(rf, "bottom")
    d += elm.Line().up().toy(0)
    d += elm.Resistor().left().at(K).length(2.0).label("$R_g$ 10 kΩ", "bottom"); d += elm.Ground()
    return op


def relax_sim(vh, vl, R=10e3, C=100e-9, vcc=5.0, T=6e-3):
    """弛张振荡器：输出只有 vh、vl 两种；同相端门限 = (vcc + 0 + Vo)/3（三个等值电阻）。"""
    dt = R * C / 2000
    t = np.arange(0, T, dt)
    vc, high = 0.0, True
    VC, VO, edges = np.empty_like(t), np.empty_like(t), []
    for k in range(len(t)):
        vo = vh if high else vl
        th = (vcc + vo) / 3                           # 当前门限
        if high and vc >= th:                         # 电容涨到上门限 → 输出翻低
            high = False; edges.append(t[k])
        elif not high and vc <= th:                   # 电容降到下门限 → 输出翻高
            high = True; edges.append(t[k])
        vo = vh if high else vl
        vc += (vo - vc) / (R * C) * dt                # 电容经 R 向输出电压充放电
        VC[k], VO[k] = vc, vo
    e = np.array(edges[1:])                           # 去掉第一次（从 0 V 起步）
    t_high = np.mean(e[1::2] - e[0::2][:len(e[1::2])])   # 低→高 到 高→低：这里 e[0] 是翻高时刻
    period = np.mean(np.diff(e[0::2]))
    return t, VC, VO, period, t_high


# ---------- 图 16-p1-1 弛张方波振荡器 ----------
with drawing() as d:
    relax(d)
save_schem(d, N, "16_p1_1_relaxation.png")

# ---------- 图 16-p1-2 电容电压与输出方波 ----------
t, VC, VO, T, th = relax_sim(5.0, 0.0)
vH, vL = 10 / 3, 5 / 3
print(f"理想输出 0/5 V：门限 {vL:.2f} V 与 {vH:.2f} V；周期 {T*1e3:.2f} ms（{1/T:.0f} Hz），高电平占 {th/T*100:.0f}%")
assert abs(T - 2 * np.log(2) * 10e3 * 100e-9) < 0.02e-3   # T = 2 ln2 · RC ≈ 1.39RC
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, VO, **fs.LS["vout"], label="$V_o$ 输出方波")
ax.plot(t * 1e3, VC, **fs.LS["third"], label="$V_C$ 电容电压")
fs.ref_h(ax, vH, f"上门限 {vH:.2f} V", x=0.99)
fs.ref_h(ax, vL, f"下门限 {vL:.2f} V", x=0.99)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-0.3, 6.3); ax.set_xlim(-0.2, 7.4)
ax.legend(loc="upper left", fontsize=8, ncol=2)
fs.save(fig, N, "16_p1_2_relax_wave.png")

# ---------- 图 16-p2-1 文氏桥振荡器 ----------
with drawing() as d:
    wien(d)
save_schem(d, N, "16_p2_1_wien.png")

# ---------- 图 16-p2-2 文氏桥网络的选频 ----------
R, C = 10e3, 10e-9
f0 = 1 / (2 * np.pi * R * C)
f = np.logspace(2, np.log10(2e4), 600)
beta = 1 / np.sqrt(9 + (f / f0 - f0 / f) ** 2)
print(f"文氏桥 f0 = {f0:.0f} Hz，网络在 f0 处 V+/Vo = {1/3:.3f}；在 f0/10 和 10f0 处约 {1/np.sqrt(9 + 9.9**2):.3f}")
assert abs(beta.max() - 1 / 3) < 1e-4
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.semilogx(f, beta, **fs.LS["fb"], label="文氏桥网络 $V_+/V_o$")
fs.mark(ax, f0, 1 / 3, fmt="{:.3f}", dx=8, dy=4)
fs.ref_v(ax, f0, f"{f0:.0f} Hz", y=0.12)
fs.axlabels(ax, "频率", "Hz", "同相端/输出 幅度", None)
ax.set_xticks([100, 1e3, 1e4]); ax.set_xticklabels(["100", "1 k", "10 k"])
ax.set_ylim(0, 0.4); ax.legend(loc="upper left", fontsize=8)
fs.save(fig, N, "16_p2_2_wien_select.png")


# ---------- 文氏桥数值仿真（与 code/16_sim.py 相同的模型）----------
Rg, VMAX, dt = 10e3, 4.0, 0.2e-6
tw = np.arange(0, 20e-3, dt)
def run(amp):
    vc, vx = 0.0, 0.01
    out = np.empty_like(tw)
    for k in range(len(tw)):
        vo = amp(vx); i = (vo - vx - vc) / R
        vc += i / C * dt; vx += (i - vx / R) / C * dt; out[k] = vo
    return out
clip = run(lambda v: np.clip(3.2 * v, -VMAX, VMAX))
diode = run(lambda v: np.clip(v + v / Rg * 12e3 + 0.6 * np.tanh(v / Rg * 10e3 / 0.6), -VMAX, VMAX))

# ---------- 图 16-p2-4 正弦变方波：接一个比较器 ----------
w = tw > 17e-3
ts, vs = tw[w], diode[w]
sq = np.where(vs > 0, 4.0, -4.0)                      # 比较器：同相端接正弦，反相端接 0 V，输出 ±4 V
print(f"整形：正弦峰值 {vs.max():.2f} V → 比较器（门限 0 V）输出 ±4.0 V 方波")
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot((ts - ts[0]) * 1e3, vs, **fs.LS["vin"], label="$V_i$ 文氏桥正弦（送进比较器）")
ax.plot((ts - ts[0]) * 1e3, sq, **fs.LS["vout"], label="$V_o$ 比较器输出方波")
fs.ref_h(ax, 0, "门限 0 V", x=0.99)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-5, 6.2)
ax.legend(loc="upper left", fontsize=8, ncol=2)
fs.save(fig, N, "16_p2_4_shaping.png")


# ---------- 图 16-p3-1 削顶与稳幅的波形对比 ----------
def distortion(y, tt):
    """在 1400～1800 Hz 里逐个试频率，用最小二乘拟合基波正弦，返回（拟合曲线，偏离正弦的比例，频率）。"""
    best = None
    for fz in np.arange(1400, 1801, 1.0):
        M = np.column_stack([np.sin(2 * np.pi * fz * tt), np.cos(2 * np.pi * fz * tt), np.ones_like(tt)])
        coef, *_ = np.linalg.lstsq(M, y, rcond=None)
        fit = M @ coef
        r = np.sqrt(np.mean((y - fit) ** 2) / np.mean((fit - coef[2]) ** 2))
        if best is None or r < best[1]:
            best = (fit, r, fz)
    return best
w = tw > 15e-3
tt = tw[w]
fit_c, d_c, f_c = distortion(clip[w], tt)
fit_d, d_d, f_d = distortion(diode[w], tt)
print(f"偏离正弦的比例：削顶 {d_c*100:.1f}%（{f_c:.0f} Hz），二极管稳幅 {d_d*100:.1f}%（{f_d:.0f} Hz）")
assert d_c > 2.5 * d_d
k = tt < 15e-3 + 1.5e-3
fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"], sharey=True)
x = (tt[k] - tt[0]) * 1e3
axs[0].plot(x, fit_c[k], **fs.LS["good"], label="理想正弦")
axs[0].plot(x, clip[w][k], **fs.LS["bad"], label="增益 3.2 无稳幅")
axs[0].set_title(f"削顶：偏离正弦 {d_c*100:.1f}%", fontsize=9)
axs[1].plot(x, fit_d[k], **fs.LS["good"], label="理想正弦")
axs[1].plot(x, diode[w][k], **fs.LS["vout"], label="二极管稳幅")
axs[1].set_title(f"稳幅：偏离正弦 {d_d*100:.1f}%", fontsize=9)
for ax in axs:
    fs.axlabels(ax, "时间", "ms"); ax.legend(loc="lower left", fontsize=7)
axs[0].set_ylabel("$V_o$ / V"); axs[0].set_ylim(-6.5, 5.5)
fs.save(fig, N, "16_p3_1_distortion.png")

# ---------- 图 16-p3-2 运放输出不到电源轨：占空比变歪 ----------
fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"], sharey=True)
for ax, (vh, vl, name) in zip(axs, [(5.0, 0.0, "理想：输出 0～5 V"), (3.5, 0.1, "LM358：输出 0.1～3.5 V")]):
    t, VC, VO, T, th = relax_sim(vh, vl)
    up, dn = (5 + vh) / 3, (5 + vl) / 3
    print(f"{name}：门限 {dn:.2f}/{up:.2f} V，周期 {T*1e3:.2f} ms，高电平占 {th/T*100:.0f}%")
    ax.plot(t * 1e3, VO, **(fs.LS["vout"] if vh == 5 else fs.LS["bad"]), label="$V_o$")
    ax.plot(t * 1e3, VC, **fs.LS["third"], label="$V_C$")
    fs.ref_h(ax, up); fs.ref_h(ax, dn)
    ax.set_title(f"{name}，高电平占 {th/T*100:.0f}%", fontsize=9)
    fs.axlabels(ax, "时间", "ms"); ax.legend(loc="upper right", fontsize=7, ncol=2)
    if vh == 3.5:
        assert th / T > 0.6
axs[0].set_ylabel("电压 / V"); axs[0].set_ylim(-0.3, 6.5)
fs.save(fig, N, "16_p3_2_lm358_duty.png")
