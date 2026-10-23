"""13 微分电路：全部配图（图 13-p2-3 由 code/13_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/13_figs.py
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

N = "13"
_spec = importlib.util.spec_from_file_location("sim13", os.path.join(HERE, "..", "13_sim.py"))
sim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sim)
TAU = sim.RF * sim.C
print(f"[数值] C {sim.C*1e9:.0f} nF，R_f {sim.RF/1e3:.0f} kΩ → R_f·C {TAU*1e3:.1f} ms")


def differentiator(d, practical=False, cur=False):
    """反相微分器：把积分器的 R 和 C 对调——输入串电容 C，反馈接电阻 R_f。
    practical=True 时输入再串 R1，反馈 R_f 旁并 C_f。"""
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot().label("虚地 0 V", "bottom", ofst=0.15) if cur else elm.Dot())
    c = elm.Capacitor().left().label("$C$ 100 nF")
    if cur:
        c.label("$I \\rightarrow$", "bottom")
    d += c
    if practical:
        d += elm.Resistor().left().label("$R_1$ 1 kΩ\n（限高频）")
    d += elm.Dot(open=True).label("$V_i$ 输入", "left")
    d += elm.Line().up().at(j.center).length(1.5)
    if practical:
        d += (a := elm.Dot())
    r = elm.Resistor().right().label("$R_f$ 10 kΩ").tox(op.out.x + 0.5)
    if cur:
        r.label("$I \\rightarrow$", "bottom")
    d += r
    if practical:
        d += (b := elm.Dot())
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    if practical:
        d += elm.Line().up().at(a.center).length(1.5)
        d += elm.Capacitor().right().label("$C_f$ 10 nF（压高频）").tox(b.center.x)
        d += elm.Line().down().toy(b.center)
    d += elm.Line().left().at(op.in2).length(0.5)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$ 输出", "right")


# ---------- 图 13-p1-1 斜率直觉：输出 = −(输入的斜率) × R_f·C ----------
t = np.arange(0, 6e-3, 1e-6)
vin = np.interp(t, [0, 1e-3, 2e-3, 4e-3, 6e-3], [0.0, 2.0, 2.0, 1.0, 1.0])
vo = sim.ideal(t, vin)
fig, (a0, a1) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
tm = t * 1e3
a0.plot(tm, vin, **fs.LS["vin"], label="输入电压 $V_i$")
a0.text(0.55, 0.35, "陡：每 ms +2 V", fontsize=9)
a0.text(1.2, 2.1, "平：斜率 0", fontsize=9)
a0.text(2.9, 1.65, "缓：每 ms −0.5 V", fontsize=9)
print("[数值] 斜率 +2 V/ms、0、−0.5 V/ms")
a0.set_ylim(-0.3, 2.6); a0.set_ylabel(fs.qlabel("输入", "V")); a0.legend(loc="lower right", fontsize=8)
a1.plot(tm, vo, **fs.LS["vout"], label="微分器输出 $V_o$（$R_f C$ = 1 ms）")
for x in (0.5, 1.5, 3.0):
    fs.mark(a1, x, round(float(vo[int(round(x * 1e3))]), 6) + 0.0, "{:.1f}", " V", dx=4, dy=6)
assert abs(vo[500] + 2) < 1e-6 and abs(vo[1500]) < 1e-6 and abs(vo[3000] - 0.5) < 1e-6
fs.ref_h(a1, 0)
a1.set_ylim(-2.6, 1.2); a1.set_ylabel(fs.qlabel("输出", "V")); a1.legend(loc="lower right", fontsize=8)
a1.set_xlabel(fs.qlabel("时间", "ms"))
fs.save(fig, N, "13_p1_1_slope.png")

# ---------- 图 13-p1-2 微分器电路 ----------
with drawing() as d:
    differentiator(d)
save_schem(d, N, "13_p1_2_differentiator.png")

# ---------- 图 13-p1-3 三角波进、方波出 ----------
t = np.arange(0, 6e-3, 1e-6)
vin = sim.triangle(t)
vo = sim.ideal(t, vin)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vin, **fs.LS["vin"], label="输入：±0.5 V、500 Hz 三角波（斜率 ±1 V/ms）")
ax.plot(t * 1e3, vo, **fs.LS["vout"], label="输出：±1 V 方波")
hi, lo = vo[(t > 1.2e-3) & (t < 1.8e-3)].mean(), vo[(t > 0.2e-3) & (t < 0.8e-3)].mean()
print(f"[数值] 上升段输出 {lo:.2f} V，下降段输出 {hi:.2f} V")
assert abs(hi - 1) < 1e-6 and abs(lo + 1) < 1e-6
fs.ref_h(ax, 0)
ax.set_ylim(-1.5, 2.0)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.legend(loc="upper right", fontsize=8, ncol=2)
fs.save(fig, N, "13_p1_3_triangle_square.png")

# ---------- 图 13-p2-1 推导用：电流 I 和虚地 ----------
with drawing() as d:
    differentiator(d, cur=True)
save_schem(d, N, "13_p2_1_analysis.png")

# ---------- 图 13-p2-2 实用微分器 ----------
with drawing() as d:
    differentiator(d, practical=True)
save_schem(d, N, "13_p2_2_practical.png")

# ---------- 图 13-p3-1 运放带宽有限时：理想微分器振铃 ----------
t = np.arange(0, 2.4e-3, 2e-8)
vin = sim.triangle(t)
y_i = sim.simulate(t, vin, gbw=sim.GBW)
y_p = sim.simulate(t, vin, r1=sim.R1, cf=sim.CF, gbw=sim.GBW)
k = (t > 1e-3) & (t < 2e-3)
peak_i, peak_p = y_i[k].max(), y_p[k].max()
z = np.flatnonzero(np.diff(np.sign(y_i[k] - 1.0)) != 0)
f_ring = (len(z) - 1) / 2 / (t[k][z[-1]] - t[k][z[0]])
f_th = np.sqrt(2 * np.pi * sim.GBW / TAU) / (2 * np.pi)
print(f"[数值] GBW {sim.GBW/1e6:.1f} MHz：理想微分器拐点后最高 {peak_i:.2f} V（应为 1 V），振铃约 {f_ring/1e3:.1f} kHz"
      f"（估算 √(2π·GBW/R_fC)/2π = {f_th/1e3:.1f} kHz）；实用版最高 {peak_p:.2f} V")
assert peak_i > 2.5 and peak_p < 1.01 and abs(f_ring - f_th) / f_th < 0.05
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
w = (t > 0.8e-3) & (t < 2.2e-3)
ax.plot(t[w] * 1e3, y_i[w], **{**fs.LS["bad"], "lw": 0.9, "marker": None}, label=f"理想微分器 + 真实运放：冲到 {peak_i:.2f} V，振铃 {f_ring/1e3:.1f} kHz")
ax.plot(t[w] * 1e3, y_p[w], **fs.LS["vout"], label=f"实用微分器 + 同一运放：最高 {peak_p:.2f} V，无振铃")
fs.ref_h(ax, 1.0, "应有的 +1 V", x=0.01, ha="left")
ax.set_ylim(-1.5, 4.3)
fs.axlabels(ax, "时间", "ms", "输出", "V"); ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "13_p3_1_ringing.png")

# ---------- 图 13-p3-2 R1 扫描：抗干扰 vs 边沿变慢 ----------
t = np.arange(0, 4e-3, 1e-7)
clean = sim.triangle(t)
noisy = clean + sim.noise(t)
r1s = [100.0, 300.0, 1e3, 3e3]
n_ideal = sim.noise_pp(t, sim.ideal(t, noisy), sim.ideal(t, clean), 1e-3)
nps, t90s, waves = [], [], []
for r1 in r1s:
    y0 = sim.simulate(t, clean, r1=r1)
    nps.append(sim.noise_pp(t, sim.simulate(t, noisy, r1=r1), y0, 1e-3))
    kk = (t > 1e-3) & (t < 2e-3)
    t90s.append(float(t[kk][np.argmax(y0[kk] > 0.8)] - 1e-3))   # 从 −1 V 爬到 +0.8 V（90% 摆幅）用时
    waves.append(y0)
    print(f"[数值] R1 {r1:g} Ω：干扰峰峰 {nps[-1]*1e3:.0f} mV，边沿 90% 用时 {t90s[-1]*1e3:.2f} ms（R1·C = {r1*sim.C*1e3:.2f} ms）")
print(f"[数值] 理想微分器干扰峰峰 {n_ideal:.2f} V")
assert all(np.diff(nps) < 0) and all(np.diff(t90s) > 0)
fig, (a0, a1) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a0.semilogx(r1s, np.array(nps) * 1e3, **{**fs.LS["vout"], "marker": "o"})
for r1, n in zip(r1s, nps):
    a0.annotate(f"{n*1e3:.0f} mV", (r1, n * 1e3), xytext=(5, 4), textcoords="offset points", fontsize=8)
fs.ref_h(a0, n_ideal * 1e3, f"理想微分器 {n_ideal*1e3:.0f} mV", x=0.98)
a0.set_xlim(60, 6e3); a0.set_ylim(0, 2900)
fs.axlabels(a0, "$R_1$", "Ω", "20 kHz 干扰在输出的峰峰值", "mV")
a0.set_title("(a) $R_1$ 越大，干扰越小", fontsize=10)
w = (t > 0.8e-3) & (t < 2e-3)
for r1, y, st, t9 in zip(r1s[1:], waves[1:], [fs.LS["third"], fs.LS["vout"], fs.LS["bad"]], t90s[1:]):
    a1.plot(t[w] * 1e3, y[w], **st, label=f"$R_1$ = {r1:g} Ω：90% 用时 {t9*1e3:.2f} ms")
a1.set_ylim(-1.3, 1.6)
fs.axlabels(a1, "时间", "ms", "输出", "V"); a1.legend(loc="lower right", fontsize=7)
a1.set_title("(b) $R_1$ 越大，方波边沿越慢", fontsize=10)
fig.tight_layout()
fs.save(fig, N, "13_p3_2_r1_sweep.png")


# ---------- 图 13-p1-4 附图第二格：输入、反馈都是电容 ----------
def cap_cap(d):
    """附图第二格的画法：输入串电容 C，反馈支路也只有一只电容 C_f（没有电阻）。"""
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    d += elm.Capacitor().left().label("$C$ 100 nF")
    d += elm.Dot(open=True).label("$V_i$ 输入", "left")
    d += elm.Line().up().at(j.center).length(1.5)
    d += elm.Capacitor().right().label("$C_f$ 50 nF（反馈也是电容）").tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(0.5)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$ 输出", "right")


with drawing() as d:
    cap_cap(d)
save_schem(d, N, "13_p1_4_cap_cap.png")

# ---------- 图 13-p1-5 同一个方波，三种接法的输出 ----------
CF2 = 50e-9                                   # 附图第二格的反馈电容
R_INT = 10e3                                  # 对照用积分器的输入电阻：R·C = 1 ms
t = np.arange(0, 4e-3, 1e-6)
dt = t[1] - t[0]
ph = (t * 500) % 1                            # 500 Hz
edge = 0.1                                    # 每个边沿占周期的 1/10 = 0.2 ms
vin = np.interp(ph, [0, edge, 0.5, 0.5 + edge, 1.0], [-0.5, 0.5, 0.5, -0.5, -0.5])
vo_int = -np.cumsum(vin) * dt / (R_INT * sim.C)          # 积分器：−面积 ÷ RC
vo_dif = sim.ideal(t, vin)                               # 微分器：−斜率 × R_f·C
vo_cc = -(sim.C / CF2) * (vin - vin[0])                  # 电容–电容：−(C/C_f)·（输入的变化量）
k_flat = (t > 0.5e-3) & (t < 0.9e-3)
pk_dif = float(np.abs(vo_dif).max())
cc_flat = float(vo_cc[k_flat].mean())
int_pp = float(np.ptp(vo_int[t > 1e-3]))
print(f"[数值] 方波 ±0.5 V、500 Hz，边沿 0.2 ms：积分器（RC 1 ms）三角波峰峰 {int_pp:.2f} V；"
      f"微分器（R_f·C 1 ms）边沿脉冲 {pk_dif:.1f} V、平顶 0 V；电容–电容（C/C_f = {sim.C/CF2:.0f}）平顶 {cc_flat:.1f} V")
assert abs(pk_dif - 5.0) < 0.05 and abs(cc_flat + 2.0) < 1e-6 and abs(vo_dif[k_flat]).max() < 1e-6
for IB in (10e-9, 20e-9):                     # LM358 输入偏置电流典型约 10～20 nA（TI 模型约 10 nA）
    drift = IB / CF2
    print(f"[数值] 电容–电容接法：偏置电流 {IB*1e9:.0f} nA 只能流进 C_f，输出漂移 {drift:.2f} V/s，"
          f"约 {13.5 / drift:.0f} s 漂过 13.5 V")
fig, axs = plt.subplots(4, 1, figsize=(7, 6.2), sharex=True)
tm = t * 1e3
axs[0].plot(tm, vin, **fs.LS["vin"], label="输入：±0.5 V 方波（边沿 0.2 ms）")
axs[1].plot(tm, vo_int, **fs.LS["vout"], label=f"积分器（输入 R、反馈 C）：三角波，峰峰 {int_pp:.2f} V")
axs[2].plot(tm, vo_dif, **fs.LS["third"], label=f"微分器（输入 C、反馈 R）：只在边沿出 ±{pk_dif:.0f} V 脉冲")
axs[3].plot(tm, vo_cc, **fs.LS["fb"], label=f"附图第二格（输入 C、反馈 C）：反相 {sim.C/CF2:.0f} 倍的方波")
for a, lim in zip(axs, [(-0.9, 1.1), (-0.8, 0.5), (-6.5, 7.5), (-2.8, 1.6)]):
    fs.ref_h(a, 0)
    a.set_ylim(*lim); a.set_ylabel(fs.qlabel("电压", "V"), fontsize=8)
    a.legend(loc="upper right", fontsize=7.5)
axs[3].set_xlabel(fs.qlabel("时间", "ms"))
fs.save(fig, N, "13_p1_5_three_circuits.png")

# ---------- 图 13-p1-6 用 LM358B 搭理想微分器会自己振；加小电阻 R1 或小电容 C_f 就压住了（ngspice + TI 官方模型） ----------
TRI = "PULSE(-0.5 0.5 0 1m 1m 1n 2m)"          # ±0.5 V、500 Hz 三角波（与图 13-p1-3 相同）
cases = [("只有 C 和 $R_f$（理想微分器）", None, None, {**fs.LS["bad"], "lw": 0.7, "marker": None}),
         ("只串小电阻 $R_1$ = 1 kΩ", sim.R1, None, fs.LS["third"]),
         ("只并小电容 $C_f$ = 10 nF", None, sim.CF, fs.LS["fb"]),
         ("$R_1$、$C_f$ 都加（实用微分器）", sim.R1, sim.CF, fs.LS["vout"])]
res = []
for name, r1, cf, st in cases:
    t, v = sim.lm358(TRI, r1=r1, cf=cf)
    k1 = (t > 1e-3) & (t < 2e-3)                 # 1 ms 拐角之后的半个周期（输出应为 +1 V）
    k2 = (t > 1.7e-3) & (t < 2.0e-3)             # 平顶后段
    pk, pp = float(v[k1].max()), float(np.ptp(v[k2]))
    pps = f"{pp:.2f} V" if pp >= 0.1 else f"{pp*1e3:.0f} mV"
    res.append((t, v, pk, pp, pps))
    print(f"[数值] LM358B，{name.replace('$', '')}：拐角后最高 {pk:.2f} V，平顶后段（1.7～2.0 ms）峰峰 {pps}")
t0, v0, pk0, pp0, _ = res[0]
x = v0[(t0 > 1e-3) & (t0 < 2e-3)]; x = x - x.mean(); tt = t0[(t0 > 1e-3) & (t0 < 2e-3)]
zc = tt[1:][np.diff(np.sign(x)) != 0]
f_ring_lm = 1 / (2 * np.mean(np.diff(zc)))
print(f"[数值] LM358B 理想微分器振铃频率约 {f_ring_lm/1e3:.1f} kHz；每个拐角都重新激发，整段平顶上一直在振")
assert pk0 > 4.0 and pp0 > 4.0 and 12e3 < f_ring_lm < 14.5e3
assert all(r[2] < 1.7 and r[3] < 0.05 for r in res[1:])
fig, axs = plt.subplots(4, 1, figsize=(7, 6.4), sharex=True)
for a, (name, r1, cf, st), (t, v, pk, pp, pps) in zip(axs, cases, res):
    w = (t > 0.8e-3) & (t < 4.2e-3)
    a.plot(t[w] * 1e3, v[w], **st, label=(f"{name}：拐角后冲到 {pk:.2f} V，平顶上一直振（峰峰 {pps}）" if a is axs[0]
           else f"{name}：最高 {pk:.2f} V，没有振铃"))
    fs.ref_h(a, 1.0); fs.ref_h(a, -1.0)
    a.set_ylim(-3.5, 8.0 if a is axs[0] else 2.6); a.set_ylabel(fs.qlabel("输出", "V"), fontsize=8)
    a.legend(loc="upper right", fontsize=7.5)
fs.ref_h(axs[3], 1.0, "+1 V", x=0.01, ha="left"); fs.ref_h(axs[3], -1.0, "−1 V", x=0.01, ha="left")
axs[3].set_xlabel(fs.qlabel("时间", "ms"))
print("[参考线] ±1 V（理想微分器应有的方波电平）")
fig.tight_layout()
fs.save(fig, N, "13_p1_6_ringing_fix.png")

# ---------- page1「在示波器上会看到什么」各步的读数（实用微分器 R1 1 kΩ + C_f 10 nF，LM358B） ----------
t, v = sim.lm358(TRI, r1=sim.R1, cf=sim.CF)
s1_hi = float(v[(t > 5.6e-3) & (t < 6.0e-3)].mean()); s1_lo = float(v[(t > 4.6e-3) & (t < 5.0e-3)].mean())
t, v = sim.lm358("PULSE(-0.5 0.5 0 0.5m 0.5m 1n 1m)", r1=sim.R1, cf=sim.CF)
s2_lo = float(v[(t > 5.42e-3) & (t < 5.49e-3)].mean()); s2_hi = float(v[(t > 5.92e-3) & (t < 5.99e-3)].mean())  # 每半个周期的末尾
SIN = "SIN(0 0.5 159.155)"                      # 159 Hz、幅度 0.5 V 正弦
t, v = sim.lm358(SIN, r1=sim.R1, cf=sim.CF, tstop=40e-3, tstep=2e-6)
s3_p = float(v[t > 20e-3].max())
t, v = sim.lm358(SIN, tstop=40e-3, tstep=2e-6)
s3_i_hi, s3_i_lo = float(v[t > 20e-3].max()), float(v[t > 20e-3].min())
t, v = sim.lm358("PULSE(-0.5 0.5 0.5m 1u 1u 1m 2m)", r1=sim.R1, cf=sim.CF)   # ±0.5 V、500 Hz 方波，边沿 1 µs
s4_hi, s4_lo = float(v[t > 2e-3].max()), float(v[t > 2e-3].min())
s4_flat = float(np.abs(v[(t > 3.2e-3) & (t < 3.5e-3)]).max())
print(f"[数值] 示波器第 1 步（500 Hz 三角波，实用版）：方波 {s1_hi:+.2f} V / {s1_lo:+.2f} V")
print(f"[数值] 示波器第 2 步（1 kHz 三角波，实用版）：每半个周期末尾 {s2_hi:+.2f} V / {s2_lo:+.2f} V")
print(f"[数值] 示波器第 3 步（159 Hz、0.5 V 正弦）：实用版输出幅度 {s3_p:.3f} V；"
      f"拆掉 R1、C_f 后峰值 {s3_i_hi:+.2f} V / {s3_i_lo:+.2f} V（叠着振铃）")
print(f"[数值] 示波器第 4 步（±0.5 V 方波，实用版）：边沿脉冲 {s4_hi:+.2f} V / {s4_lo:+.2f} V，"
      f"边沿后 0.7～1.0 ms 平顶处 |V_o| ≤ {s4_flat:.3f} V")
assert abs(s1_hi - 1) < 0.03 and abs(s1_lo + 1) < 0.03 and abs(s3_p - 0.5) < 0.02
assert s3_i_hi > 0.55 and s4_hi < 5
