"""18 微分电路：全部配图（图 18-p2-3 由 code/18_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/18_figs.py
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

N = "18"
_spec = importlib.util.spec_from_file_location("sim13", os.path.join(HERE, "..", "18_sim.py"))
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


# ---------- 图 18-p1-1 斜率直觉：输出 = −(输入的斜率) × R_f·C ----------
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
fs.save(fig, N, "18_p1_1_slope.png")

# ---------- 图 18-p1-2 微分器电路 ----------
with drawing() as d:
    differentiator(d)
save_schem(d, N, "18_p1_2_differentiator.png")

# ---------- 图 18-p1-3 三角波进、方波出 ----------
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
fs.save(fig, N, "18_p1_3_triangle_square.png")

# ---------- 图 18-p2-1 推导用：电流 I 和虚地 ----------
with drawing() as d:
    differentiator(d, cur=True)
save_schem(d, N, "18_p2_1_analysis.png")

# ---------- 图 18-p2-2 实用微分器 ----------
with drawing() as d:
    differentiator(d, practical=True)
save_schem(d, N, "18_p2_2_practical.png")

# ---------- 图 18-p3-1 运放带宽有限时：理想微分器振铃 ----------
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
fs.save(fig, N, "18_p3_1_ringing.png")

# ---------- 图 18-p3-2 R1 扫描：抗干扰 vs 边沿变慢 ----------
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
fs.save(fig, N, "18_p3_2_r1_sweep.png")


# ---------- 图 18-p1-4 附图第二格：输入、反馈都是电容 ----------
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
save_schem(d, N, "18_p1_4_cap_cap.png")

# ---------- 图 18-p1-5 同一个方波，三种接法的输出 ----------
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
fs.save(fig, N, "18_p1_5_three_circuits.png")

# ---------- 图 18-p1-6 用 LM358B 搭理想微分器会自己振；加小电阻 R1 或小电容 C_f 就压住了（ngspice + TI 官方模型） ----------
TRI = "PULSE(-0.5 0.5 0 1m 1m 1n 2m)"          # ±0.5 V、500 Hz 三角波（与图 18-p1-3 相同）
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
fs.save(fig, N, "18_p1_6_ringing_fix.png")

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


# ======================= page4 动手实验篇：面包板接线图 =======================
# 面包板俯视图小工具（各节点脚本各带一份，互不依赖）。
# 坐标：列号 1…ncol 从左到右；上半区 a–e、下半区 f–j（同一列的 a–e 五个孔互相连通，f–j 也连通）；
# 上下各有两条电源轨：靠外的一条标「+」，靠里的一条标「−」，整条横向连通。
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

BB_Y = {r: 5.6 - i for i, r in enumerate("abcde")}
BB_Y.update({r: -1.4 - i for i, r in enumerate("fghij")})
BB_Y.update({"T+": 8.6, "T-": 7.7, "B-": -6.7, "B+": -7.6})
WIRE = dict(pos=(fs.C["bad"], "正电源"), gnd=("#000000", "地（0 V）"), neg=(fs.C["third"], "负电源"),
            sig=(fs.C["vin"], "输入信号"), out=(fs.C["vout"], "输出"), fb=(fs.C["fb"], "反馈 / 其他连线"))


class Breadboard:
    def __init__(self, ncol=30, title=None, size=(10, 6.4), rails=("+", "−", "−", "+")):
        self.ncol, self.used = ncol, set()
        self.fig, self.ax = plt.subplots(figsize=size)
        ax = self.ax
        ax.add_patch(FancyBboxPatch((0.2, -8.3), ncol + 0.6, 17.6, boxstyle="round,pad=0.1",
                                    fc="#f7f5ef", ec="0.55", lw=1.0))
        ax.add_patch(Rectangle((0.4, -0.55), ncol + 0.2, 0.7, fc="#e4e0d6", ec="none"))   # 中间凹槽
        for key, lab in zip(("T+", "T-", "B-", "B+"), rails):
            y = BB_Y[key]
            col = fs.C["bad"] if lab.startswith("+") else ("#000000" if lab in ("−", "GND", "0 V") else fs.C["third"])
            ax.plot([0.6, ncol + 0.4], [y + 0.42, y + 0.42], color=col, lw=1.0)
            ax.text(0.0, y, lab, ha="right", va="center", fontsize=10, color=col, fontweight="bold")
            for c in range(1, ncol + 1):
                if c % 6:
                    ax.add_patch(Circle((c, y), 0.12, fc="0.72", ec="none"))
        for r in "abcdefghij":
            y = BB_Y[r]
            ax.text(0.15, y, r, ha="right", va="center", fontsize=8, color="0.35")
            ax.text(ncol + 0.85, y, r, ha="left", va="center", fontsize=8, color="0.35")
            for c in range(1, ncol + 1):
                ax.add_patch(Circle((c, y), 0.12, fc="0.72", ec="none"))
        for c in range(1, ncol + 1):
            if c == 1 or c % 5 == 0:
                ax.text(c, 6.35, str(c), ha="center", va="bottom", fontsize=7.5, color="0.35")
                ax.text(c, -6.15, str(c), ha="center", va="top", fontsize=7.5, color="0.35")
        ax.set_xlim(-3.4, ncol + 4.8)
        ax.set_ylim(-11.2, 11.6)
        ax.set_aspect("equal")
        ax.axis("off")
        if title:
            ax.set_title(title, fontsize=11)

    def xy(self, h):
        """'e10' → 第 10 列 e 排；'T+3' / 'B-7' → 上（T）/ 下（B）电源轨第 3 / 7 列。"""
        if h[0] in "TB" and h[1] in "+-":
            return float(h[2:]), BB_Y[h[:2]]
        return float(h[1:]), BB_Y[h[0]]

    def _hole(self, p):
        x, y = self.xy(p) if isinstance(p, str) else p
        if isinstance(p, str):
            self.ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=4))
        return x, y

    def wire(self, a, b, kind="fb", via=None):
        """导线：a、b 为孔名或 (x, y)；via 为中间拐点列表。颜色按 kind 取（见 WIRE）。"""
        self.used.add(kind)
        pts = [self._hole(a)] + list(via or []) + [self._hole(b)]
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=WIRE[kind][0], lw=2.4, solid_capstyle="round", zorder=5)

    def part(self, a, b, label, kind="R", lab_side=1):
        """两脚元件：R 电阻、C 电容、E 电解电容（+ 脚在 a）、D 二极管（a 阳 b 阴）、L LED（a 阳）、
        S 按钮、P 小灯泡。画成方框简化符号，标签写在旁边。"""
        (x1, y1), (x2, y2) = self._hole(a), self._hole(b)
        ax = self.ax
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.plot([x1, x2], [y1, y2], color="0.35", lw=1.2, zorder=5)
        fc = dict(R="#d9c7a3", C="#f2d27a", E="#6d8fb5", D="#555555", L="#ffffff", S="#bbbbbb",
                  P="#fff7c2")[kind]
        horiz = abs(x2 - x1) >= abs(y2 - y1)
        w, h = (0.9, 0.5) if horiz else (0.5, 0.9)
        if kind in "LP":
            ax.add_patch(Circle((mx, my), 0.42, fc=fc, ec="0.2", lw=1.0, zorder=6))
        else:
            ax.add_patch(FancyBboxPatch((mx - w / 2, my - h / 2), w, h, boxstyle="round,pad=0.05",
                                        fc=fc, ec="0.2", lw=1.0, zorder=6))
        if kind in "EDL":
            ax.text(x1 + (0.25 if horiz else 0.25), y1 + (0.3 if horiz else 0), "+", fontsize=8,
                    ha="center", va="center", zorder=7, color=fs.C["bad"])
        if lab_side == "r":
            ax.text(max(x1, x2) + 0.3, my, label, ha="left", va="center", fontsize=8.5, zorder=7)
        elif horiz:
            ax.text(mx, my + 0.55 * lab_side, label, ha="center", va="bottom" if lab_side > 0 else "top",
                    fontsize=8.5, zorder=7)
        else:
            ax.text(mx + 0.45 * lab_side, my, label, ha="left" if lab_side > 0 else "right",
                    va="center", fontsize=8.5, zorder=7)

    def chip(self, col, label, npin=8, names=None):
        """DIP 芯片跨在中间凹槽上：第 1 脚在 f 排第 col 列（左下，缺口朝左），逆时针数，
        第 npin 脚在 e 排第 col 列。脚号和脚名写在芯片体上。"""
        half = npin // 2
        ax = self.ax
        y0, y1 = BB_Y["f"] + 0.22, BB_Y["e"] - 0.22
        ax.add_patch(Rectangle((col - 0.5, y0), half, y1 - y0, fc="#2b2b2b", ec="k", zorder=6))
        ax.add_patch(Circle((col - 0.5, (y0 + y1) / 2), 0.28, fc="#f7f5ef", ec="none", zorder=7))
        ax.text(col + (half - 1) / 2, (y0 + y1) / 2, label, color="w", ha="center",
                va="center", fontsize=9, zorder=8)
        for i in range(half):
            for p, row in ((i + 1, "f"), (npin - i, "e")):
                x, y = col + i, BB_Y[row]
                ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=7))
                txt = str(p) + ("\n" + names[p] if names and p in names else "")
                ax.text(x, y0 + 0.08 if row == "f" else y1 - 0.08, txt, ha="center",
                        va="bottom" if row == "f" else "top", fontsize=6, color="w", zorder=8,
                        linespacing=0.9)

    def module(self, x, y, w, h, label, fc="#e6f0f8"):
        """面包板外的模块（电池、信号源、继电器模块等），返回方框中心。"""
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec="0.3",
                                         lw=1.0, zorder=6))
        self.ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8.5, zorder=7)
        return x + w / 2, y + h / 2

    def note(self, x, y, text, **kw):
        self.ax.text(x, y, text, fontsize=8, zorder=8, **kw)

    def legend(self, loc="lower center"):
        from matplotlib.lines import Line2D
        cname = {fs.C["bad"]: "红", "#000000": "黑", fs.C["third"]: "紫", fs.C["vin"]: "蓝",
                 fs.C["vout"]: "橙", fs.C["fb"]: "绿", fs.C["cur"]: "天蓝"}
        def lab(c, t):                                # 图例写成「用途（色名）」；用途里已有括号时并进同一对括号
            return t[:-1] + f"，{cname[c]}）" if t.endswith("）") else f"{t}（{cname[c]}）"
        hs = [Line2D([], [], color=WIRE[k][0], lw=2.4, label=lab(*WIRE[k])) for k in WIRE if k in self.used]
        self.ax.legend(handles=hs, loc=loc, ncol=len(hs), fontsize=8.5, frameon=False,
                       bbox_to_anchor=(0.5, -0.01))

    def save(self, prefix, name):
        return fs.save(self.fig, prefix, name)

# ---------- 图 18-p4-1：实用微分器的面包板接线（±9 V，两节 9 V 电池） ----------
bb = Breadboard(30, "实用微分器面包板俯视图（LM358，±9 V）", rails=("+9 V", "GND", "GND", "−9 V"))
bb.chip(14, "LM358", names={1: "OUT", 2: "IN−", 3: "IN+", 4: "V−", 8: "V+"})
bb.wire("a14", "T+14", "pos")                      # 第 8 脚 → +9 V
bb.wire("j17", "B+17", "neg")                      # 第 4 脚 → −9 V
bb.wire("j16", "B-16", "gnd")                      # 第 3 脚 → 地
bb.wire("a17", "T-17", "gnd")                      # 第 5 脚（B 路同相端）→ 地
bb.wire("c15", "c16", "fb")                        # 第 6、7 脚短接：B 路接成跟随器，不让它乱振
bb.part("h4", "h8", "R1 1 kΩ", "R", lab_side=1)
bb.part("i8", "i12", "C 100 nF", "C", lab_side=-1)
bb.wire("j12", "j15", "fb")                        # C 的右脚 → 第 2 脚（反相端）
bb.wire("h15", "h20", "fb")                        # 反相端引到第 20 列，方便接反馈元件
bb.part("i20", "i24", "Rf 10 kΩ", "R", lab_side=1)
bb.part("j20", "j24", "Cf 10 nF", "C", lab_side="r")
bb.wire("g14", "g24", "out")                       # 第 1 脚（输出）→ 第 24 列
bb.wire("T-28", "B-28", "gnd")                     # 上下两条地轨连起来
src = bb.module(-3.2, -4.4, 3.0, 1.6, "信号源\n手机/电位器")
bb.wire((0.6, -3.6), "j4", "sig")
bb.wire((0.6, -4.2), "B-2", "gnd")
bat = bb.module(-3.2, 9.4, 4.0, 1.4, "9 V 电池 ×2 串联\n中点 = GND")
bb.wire((1.4, 9.9), "T+1", "pos")
bb.wire((0.8, 9.6), "T-3", "gnd")
bb.wire((-3.2, 10.1), "B+1", "neg", via=[(-3.3, 10.1), (-3.3, -8.6), (1.0, -8.6)])
bb.note(25.2, -2.6, "测输出：\n红表笔 h24\n黑表笔 GND", va="center")
bb.note(5.0, -9.6, "慢速实验：C 换 100 µF 电解（+ 脚插 i8 朝输入），Rf 换 100 kΩ，信号源换电位器", ha="left")
bb.note(5.0, -10.4, "对比振铃：拔掉 R1（改用导线连 h4–h8）、拔掉 Cf", ha="left")
bb.legend()
bb.save(N, "18_p4_1_breadboard.png")
print("[接线] LM358 第 1–4 脚在 f14–f17，第 8–5 脚在 e14–e17；R1 h4–h8，C i8–i12，导线 j12–j15、h15–h20、g14–g24，Rf i20–i24，Cf j20–j24")

# ---------- 图 18-p4-2：没有示波器时，手拧电位器做「秒级微分」，万用表读数随时间的样子 ----------
R1s, Cs, RFs, CFs = 1e3, 100e-6, 100e3, 10e-9        # 慢速版：R_f·C = 10 s
V_TOP = 9.0 * 10e3 / (82e3 + 10e3)                     # 82 kΩ 串 10 kΩ 电位器，电位器顶端电压
print(f"[数值] 慢速版 R_f·C {RFs*Cs:.0f} s，R1·C {R1s*Cs:.2f} s，R_f·C_f {RFs*CFs*1e3:.0f} ms；"
      f"电位器顶端 {V_TOP:.3f} V（9 V × 10/92）")


def slow_run(t, vin):
    """理想运放下的实用微分器：状态 = C 上电压 vc、C_f 上电压 vo（反相端为虚地）。
    i = (vin − vc)/R1 流过 C；同一电流流入 R_f ∥ C_f：C_f·dvo/dt = −i − vo/R_f。"""
    vc = vo = 0.0
    out = np.zeros_like(t); dt = t[1] - t[0]
    for k in range(1, len(t)):
        i = (vin[k] - vc) / R1s
        vc += i / Cs * dt
        vo += (-i - vo / RFs) / CFs * dt
        out[k] = vo
    return out


dt = 2e-5
t = np.arange(0, 40, dt)
ramp10 = np.clip((t - 2) / 10, 0, 1) * V_TOP                                   # 10 s 匀速拧到底
ramp5 = np.clip((t - 2) / 5, 0, 1) * V_TOP                                     # 5 s 拧到底
back = np.where(t < 22, ramp10, np.clip(1 - (t - 22) / 10, 0, 1) * V_TOP)      # 再用 10 s 拧回来
o10, o5, ob = slow_run(t, ramp10), slow_run(t, ramp5), slow_run(t, back)
p10 = float(o10[(t > 6) & (t < 10)].mean()); p5 = float(o5[(t > 4) & (t < 6.5)].mean())
pb = float(ob[(t > 26) & (t < 30)].mean()); rest = float(np.abs(o10[(t > 14) & (t < 20)]).max())
print(f"[数值] 10 s 拧到底：平台 {p10:+.3f} V（公式 −R_f·C·V/T = {-RFs*Cs*V_TOP/10:+.3f} V）；"
      f"5 s 拧到底：{p5:+.3f} V；10 s 拧回来：{pb:+.3f} V；停手 2 s 后 |V_o| ≤ {rest:.4f} V")
assert abs(p10 + RFs * Cs * V_TOP / 10) < 0.01 and abs(p5 - 2 * p10) < 0.02 and abs(pb + p10) < 0.01
assert rest < 0.005
fig, (a1, a2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
a1.plot(t, back, label="输入：10 s 拧到底，停 10 s，再 10 s 拧回", **fs.LS["vin"])
a1.plot(t, ramp5, label="输入：5 s 拧到底", **fs.LS["third"])
a1.set_ylabel(fs.qlabel("电位器电压", "V")); a1.legend(loc="upper right", fontsize=8)
a2.plot(t, ob, label="输出：对应 10 s 拧到底再拧回", **fs.LS["vout"])
a2.plot(t, o5, label="输出：对应 5 s 拧到底", **fs.LS["fb"])
fs.ref_h(a2, 0)
fs.mark(a2, 8, p10, "{:+.2f}", " V", dy=-0.35)
fs.mark(a2, 5, p5, "{:+.2f}", " V", dy=-0.35)
fs.mark(a2, 28, pb, "{:+.2f}", " V", dy=0.2)
a2.set_ylim(-2.6, 1.3); a2.legend(loc="lower right", fontsize=8)
fs.axlabels(a2, "时间", "s", "万用表读数（输出）", "V")
fig.tight_layout()
fs.save(fig, N, "18_p4_2_slow_ramp.png")

# ---------- page4 测量表：±9 V 供电时的交流读数（LM358B 模型） ----------
for lab, r1, cf in (("实用版（R1 + Cf）", sim.R1, sim.CF), ("拆掉 R1、Cf", None, None)):
    t, v = sim.lm358(TRI, r1=r1, cf=cf, vs=9)
    m = t > 2e-3
    dc, ac = float(v[m].mean()), float(np.sqrt(((v[m] - v[m].mean()) ** 2).mean()))
    print(f"[数值] ±9 V，±0.5 V、500 Hz 三角波，{lab}：输出直流 {dc*1e3:+.0f} mV，真有效值 {ac:.2f} V，"
          f"最高 {v[m].max():+.2f} V，最低 {v[m].min():+.2f} V")
    if r1:
        assert abs(ac - 0.82) < 0.02 and abs(dc) < 0.02
    else:
        assert v[m].max() > 4
print(f"[数值] 输入三角波 ±0.5 V 的真有效值 {0.5/np.sqrt(3):.3f} V（峰值 ÷ √3）")


# ======================= 第 8 轮补图：正文讲到具体连接、附近却没有电路图的地方 =======================
ACC = fs.C["bad"]
def diff_var(d, x0, y0, r1=False, cf=False, title=None, hl=True, vals=("100 nF", "10 kΩ", "1 kΩ", "10 nF")):
    d += (op := elm.Opamp(leads=True).right().at((x0, y0)).anchor("center"))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    d += elm.Capacitor().left().label(f"$C$ {vals[0]}")
    if r1:
        d += elm.Resistor().left().label(f"$R_1$ {vals[2]}").color(ACC if hl else "black")
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Line().up().at(j.center).length(1.5)
    if cf: d += (a := elm.Dot())
    d += elm.Resistor().right().label(f"$R_f$ {vals[1]}").tox(op.out.x + 0.5)
    if cf: d += (b := elm.Dot())
    d += elm.Line().down().toy(op.out); d += elm.Dot()
    if cf:
        d += elm.Line().up().at(a.center).length(1.4).color(ACC if hl else "black")
        d += elm.Capacitor().right().label(f"$C_f$ {vals[3]}").tox(b.center.x).color(ACC if hl else "black")
        d += elm.Line().down().toy(b.center).color(ACC if hl else "black")
    d += elm.Line().left().at(op.in2).length(0.5); d += elm.Line().down().length(0.5); d += elm.Ground()
    d += elm.Line().right().at(op.out).length(0.75)
    d += elm.Dot(open=True).label("$V_o$", "right")
    if title:
        d += elm.Label().at((x0 - 1.5, y0 + (4.3 if cf else 3.0))).label(title, fontsize=12)
    return op


# ---------- 图 18-p1-7 无源 RC 微分 vs 运放微分（page1「痛点」第三段） ----------
def passive_rc(d, x0, y0):
    d += elm.Dot(open=True).at((x0, y0)).label("$V_i$", "left")
    d += elm.Capacitor().right().label("$C$").label("$V_i - V_o$", "bottom", fontsize=10)
    d += (n := elm.Dot())
    d += elm.Line().right().length(1.5)
    d += elm.Dot(open=True).label("$V_o$", "right")
    d += (r := elm.Resistor().down().at(n.center))
    d += elm.Ground()
    d += elm.Label().at((r.center.x + 0.6, r.center.y)).label("$R$", halign="left")
    d += elm.Label().at((r.center.x + 0.6, r.center.y - 0.7)).label("输出 = R 上的电压", fontsize=10, halign="left")
    d += elm.Label().at((x0 + 0.5, y0 + 2.2)).label("（a）无源 RC：电容右端跟着输出变", fontsize=12, halign="left")
with drawing(fontsize=11) as d:
    passive_rc(d, 0, 0)
    op = diff_var(d, 12.5, -0.7, hl=False)
    d += elm.Label().at((9.5, 3.0)).label("（b）运放版：电容右端钉在虚地 0 V", fontsize=12, halign="left")
    d += elm.Label().at((op.in1.x - 0.45, op.in1.y - 0.45)).label("0 V", fontsize=10, color=ACC)
save_schem(d, N, "18_p1_7_passive_vs_opamp.png")


# ---------- 图 18-p1-8 四种接法：理想 / 只串 R1 / 只并 Cf / 都加（与图 18-p1-6 的四行波形一一对应） ----------
with drawing(fontsize=11) as d:
    diff_var(d, 0, 0, title="① 只有 C 和 $R_f$（理想微分器）")
    diff_var(d, 11, 0, r1=True, title="② 只串小电阻 $R_1$")
    diff_var(d, 0, -9, cf=True, title="③ 只并小电容 $C_f$")
    diff_var(d, 11, -9, r1=True, cf=True, title="④ 两个都加（实用微分器）")
save_schem(d, N, "18_p1_8_four_variants.png")
print("[电路图] 18-p1-8：新加的 R1 1 kΩ、Cf 10 nF 用强调色")

# ---------- 图 18-p3-3 本教程双电源实用微分器 vs TI SBOA276C 单电源示例（page3 参数表） ----------
def ti_single(d, x0, y0):
    d += (op := elm.Opamp(leads=True).right().at((x0, y0)).anchor("center"))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    d += elm.Capacitor().left().label("C1 15 nF")
    d += elm.Resistor().left().label("R1 1 kΩ")
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Line().up().at(j.center).length(1.5)
    d += elm.Resistor().right().label("R2（即 $R_f$）499 kΩ").tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out); d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(0.5).color(ACC)
    d += elm.Line().down().length(1.0).color(ACC)
    d += (k := elm.Dot().color(ACC).label("2.5 V", "right", color=ACC))
    d += elm.Resistor().left().label("R3 100 kΩ").color(ACC)
    d += elm.Line().up().length(0.4).color(ACC)
    d += elm.Vdd().label("+5 V").color(ACC)
    d += (r4 := elm.Resistor().down().at(k.center).color(ACC))
    d += elm.Label().at((r4.center.x + 0.5, r4.center.y)).label("R4 100 kΩ", halign="left", color=ACC)
    d += elm.Ground().color(ACC)
    d += elm.Line().right().at(op.out).length(0.75)
    d += elm.Dot(open=True).label("$V_o$（围绕 2.5 V 摆动）", "right")
with drawing(fontsize=11) as d:
    diff_var(d, 0, 0, r1=True, cf=True, hl=False)
    d += elm.Label().at((-5.5, 4.4)).label("（a）本教程：±15 V 双电源，同相端接地", fontsize=12, halign="left")
    ti_single(d, 14, 0)
    d += elm.Label().at((6.5, 4.4)).label("（b）TI SBOA276C 示例（TLV9061）：5 V 单电源，同相端接 2.5 V", fontsize=12, halign="left")
save_schem(d, N, "18_p3_3_supply_variants.png")
