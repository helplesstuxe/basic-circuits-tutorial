"""11 过载保护：全部配图（图 11-p2-2 由 code/11_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/11_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import schemdraw.flow as flow
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "11"
_spec = importlib.util.spec_from_file_location("sim11", os.path.join(HERE, "..", "11_sim.py"))
sim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sim)
V_H, V_L = sim.thresholds()
I_TRIP, I_BACK = V_H / sim.RS, V_L / sim.RS
print(f"[数值] 跳闸 {V_H*1e3:.0f} mV = {I_TRIP:.2f} A，恢复 {V_L*1e3:.0f} mV = {I_BACK:.2f} A，τ = {sim.TAU*1e3:.0f} ms")

# ---------- 图 11-p1-1 堵转：有无保护 ----------
dt = 1e-4
t = np.arange(0, 1.5, dt)
i_load = np.where(t < 0.5, sim.I_NORM, sim.I_STALL)
i_prot, _, on = sim.closed_loop(t, i_load, V_H, V_L, latch=True)
t_cut = t[np.argmax(~on)] - 0.5
t_th = float(sim.trip_time(sim.I_STALL, I_TRIP))
print(f"[数值] 堵转 5 A：{t_cut*1e3:.0f} ms 后切断（公式 {t_th*1e3:.0f} ms）；发热是正常的 {sim.I_STALL**2/sim.I_NORM**2:.0f} 倍")
assert abs(t_cut - t_th) < 1e-3
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t, i_load, **fs.LS["bad"], label="没有保护：一直 5 A，导线发热是正常的 25 倍")
ax.plot(t, i_prot, **fs.LS["vout"], label=f"有过载保护：堵转 {t_cut*1e3:.0f} ms 后切断")
fs.ref_v(ax, 0.5, "电机卡住（堵转）")
fs.ref_h(ax, I_TRIP, f"保护门限 {I_TRIP:.2f} A", x=0.99)
ax.set_ylim(-0.3, 6.8)
fs.axlabels(ax, "时间", "s", "电机电流", "A"); ax.legend(loc="center right", fontsize=8, bbox_to_anchor=(1.0, 0.6))
fs.save(fig, N, "11_p1_1_stall.png")

# ---------- 图 11-p1-2 方框图 ----------
with drawing(fontsize=11) as d:
    d += (b1 := flow.Box(w=2.4, h=1.3).label("负载电流 I\n（电机）"))
    d += flow.Arrow().right(d.unit / 2.5).at(b1.E)
    d += (b2 := flow.Box(w=2.6, h=1.3).anchor("W").label("采样电阻 $R_S$\n电流 → 电压"))
    d += flow.Arrow().right(d.unit / 2.5).at(b2.E)
    d += (b3 := flow.Box(w=2.6, h=1.3).anchor("W").label("RC 延时\n躲开启动电流"))
    d += flow.Arrow().right(d.unit / 2.5).at(b3.E)
    d += (b4 := flow.Box(w=2.6, h=1.3).anchor("W").label("比较器（带回差）\n超门限？"))
    d += flow.Arrow().down(d.unit / 2).at(b4.S)
    d += (b5 := flow.Box(w=2.6, h=1.3).anchor("N").label("开关切断\nMOS 管 / 继电器"))
    d += flow.Arrow().left().at(b5.W).tox(b1.S[0]).label("断开后电流变为 0", loc="top", fontsize=9)
    d += flow.Arrow().up().toy(b1.S)
save_schem(d, N, "11_p1_2_blocks.png")

# ---------- 图 11-p2-1 完整电路 ----------
with drawing(fontsize=11) as d:
    d += (op := elm.Opamp(leads=True, flip=True).label("比较器\nLM393", loc="center", ofst=(-0.35, 0), fontsize=9))
    # 同相端：基准分压 + 回差电阻
    d += elm.Line().left().at(op.in2).length(0.5)
    d += (p := elm.Dot())
    d += elm.Line().up().at(p.center).length(1.5)
    d += elm.Resistor().right().tox(op.out[0] + 0.75).label("$R_H$ 100 kΩ（回差）")
    d += elm.Line().down().toy(op.out)
    d += (o := elm.Dot())
    d += elm.Line().left().at(p.center).length(1.75)
    d += (q := elm.Dot().label("基准", "left"))
    d += elm.Resistor().up().at(q.center).label("$R_A$ 33 kΩ")
    d += elm.Vdd().label("+5 V")
    d += elm.Resistor().down().at(q.center).label("$R_B$ 1 kΩ", loc="bottom")
    d += elm.Ground()
    # 输出：上拉 → MOS 管栅极
    d += elm.Line().right().at(op.out).tox(o.center[0])
    d += elm.Line().right().at(o.center).length(1.25)
    d += (g := elm.Dot())
    d += elm.Resistor().up().at(g.center).label("$R_{PU}$\n2.2 kΩ")
    d += elm.Vdd().label("+5 V")
    d += elm.Line().right().at(g.center).length(1.0)
    gate = d.here
    d += (qm := elm.NFet().theta(0).reverse().anchor("gate").at(gate).label("Q1\nIRLZ44N", loc="right", ofst=(0.3, 0)))
    dr, src = qm.drain, qm.source
    d += elm.Line().up().at(dr).length(0.6)
    d += (m0 := elm.Dot())
    d += elm.Motor().up().at(m0.center).label("电机 M\n12 V / 1 A", loc="top")
    d += (m1 := elm.Dot())
    d += elm.Vdd().at(m1.center).label("+12 V")
    d += elm.Line().right().at(m1.center).length(2.0)
    d += elm.Diode().down().toy(m0.center).label("D1\n续流", loc="bottom")
    d += elm.Line().left().tox(m0.center[0])
    # 源极：采样电阻
    d += elm.Line().down().at(src).length(1.4)
    d += (s := elm.Dot().label("采样点", "right"))
    d += elm.Resistor().down().at(s.center).label("$R_S$ 0.1 Ω\n1 W", loc="bottom")
    d += elm.Ground()
    # 反相端：RC 滤波
    d += elm.Line().left().at(op.in1).length(0.5)
    d += elm.Line().down().toy(s.center)
    d += (f := elm.Dot())
    d += elm.Resistor().right().at(f.center).tox(s.center[0]).label("$R_F$ 10 kΩ")
    d += elm.Capacitor().down().at(f.center).label("$C_F$ 10 μF", loc="bottom")
    d += elm.Ground()
save_schem(d, N, "11_p2_1_circuit.png")

# ---------- 图 11-p3-1 闭环：切断以后会怎样 ----------
dt = 1e-5
t = np.arange(0, 0.5, dt)
i_load = np.where(t < 0.1, sim.I_NORM, sim.I_STALL)       # 0.1 s 时堵转
cases = [("无回差（门限都是 193 mV）", V_H, V_H, False, fs.LS["bad"]),
         ("有回差（193 / 146 mV）：打嗝式反复重启", V_H, V_L, False, fs.LS["vout"]),
         ("有回差 + 锁存：切断后保持，等人复位", V_H, V_L, True, fs.LS["good"])]
fig, ax = plt.subplots(3, 1, figsize=fs.SIZE["tall"], sharex=True)
for a, (name, vh, vl, latch, st) in zip(ax, cases):
    i, y, on = sim.closed_loop(t, i_load, vh, vl, latch=latch)
    n = sim.flips(on)
    m = t > 0.2
    i_avg = i[m].mean()
    a.plot(t * 1e3, i, **{**st, "lw": 0.8, "marker": None}, label=f"{name}\n翻转 {n} 次" + ("（每个 10 μs 仿真步都在翻）" if vh == vl else "") + f"，0.2 s 后平均电流 {i_avg:.2f} A")
    a.set_ylim(-0.5, 9.5); a.set_yticks([0, 1, 5]); a.set_ylabel(fs.qlabel("电流", "A"))
    a.legend(loc="upper right", fontsize=8)
    print(f"[数值] {name}：翻转 {n} 次，平均电流 {i_avg:.2f} A")
    if not latch and vh != vl:
        edges = np.flatnonzero(np.diff(on.astype(int)))
        offs = [(edges[k + 1] - edges[k]) * dt for k in range(len(edges) - 1) if not on[edges[k] + 1]]
        ons = [(edges[k + 1] - edges[k]) * dt for k in range(len(edges) - 1) if on[edges[k] + 1]]
        t_off, t_on = np.mean(offs[1:]), np.mean(ons[1:])
        print(f"[数值] 打嗝：断 {t_off*1e3:.1f} ms（公式 τ·ln(V_H/V_L) = {sim.TAU*np.log(V_H/V_L)*1e3:.1f} ms），"
              f"通 {t_on*1e3:.1f} ms，占空比 {t_on/(t_on+t_off)*100:.0f}%")
        assert abs(t_off - sim.TAU * np.log(V_H / V_L)) < 1e-3
        hic = (n, i_avg)
    if vh == vl:
        assert n > 100 and abs(i_avg - I_TRIP) < 0.1     # 无回差：高速开关，平均电流被“钉”在门限
        plain = (n, i_avg)
    if latch:
        assert n == 1 and i_avg == 0
for a in ax:
    fs.ref_v(a, 100, "堵转")
ax[-1].set_xlabel(fs.qlabel("时间", "ms"))
fs.save(fig, N, "11_p3_1_cutoff.png")

# ---------- 图 11-p3-2 反时限 & 启动电流 ----------
taus = [10e-3, 47e-3, 100e-3]
styles = [fs.LS["bad"], fs.LS["vout"], fs.LS["good"]]
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
I = np.logspace(np.log10(2.0), np.log10(30), 200)
for tau, st in zip(taus, styles):
    tt = sim.trip_time(I, I_TRIP, tau=tau)
    a1.loglog(I, tt * 1e3, **{**st, "marker": None}, label=f"τ = {tau*1e3:.0f} ms")
    t5, t20 = sim.trip_time(np.array([5.0, 20.0]), I_TRIP, tau=tau)
    print(f"[数值] τ = {tau*1e3:.0f} ms：5 A 堵转 {t5*1e3:.1f} ms 切断，20 A 短路 {t20*1e3:.2f} ms 切断")
fs.ref_v(a1, 5, "堵转 5 A", y=0.08)
fs.ref_v(a1, 20, "短路 20 A", y=0.08)
a1.set_xlabel(fs.qlabel("过载电流", "A")); a1.set_ylabel(fs.qlabel("切断时间", "ms"))
a1.set_title("(a) 电流越大，切得越快", fontsize=10); a1.legend(fontsize=8, loc="upper right")
from matplotlib.ticker import NullFormatter, ScalarFormatter
a1.set_xticks([2, 5, 10, 20, 30]); a1.xaxis.set_major_formatter(ScalarFormatter()); a1.xaxis.set_minor_formatter(NullFormatter())
dt = 1e-5
t = np.arange(0, 0.25, dt)
x = sim.start_current(t, 0.02)                           # 20 ms 时电机从静止启动
a2.plot(t * 1e3, x * sim.RS * 1e3, **{**fs.LS["vin"], "lw": 0.8}, label="未滤波 $I \\cdot R_S$")
peaks = {}
for tau, st in zip(taus, styles):
    y = sim.lowpass(x * sim.RS, dt, tau, 0.0)
    peaks[tau] = y.max()
    tag = "误跳闸" if y.max() > V_H else "不跳"
    a2.plot(t * 1e3, y * 1e3, **{**st, "marker": None}, label=f"τ = {tau*1e3:.0f} ms：峰值 {y.max()*1e3:.0f} mV，{tag}")
    print(f"[数值] 启动 5 A→1 A（衰减 20 ms），τ = {tau*1e3:.0f} ms 滤波后峰值 {y.max()*1e3:.0f} mV（{tag}）")
fs.ref_h(a2, V_H * 1e3, f"跳闸门限 {V_H*1e3:.0f} mV", x=0.99)
a2.set_ylim(0, 560)
a2.set_xlabel(fs.qlabel("时间", "ms")); a2.set_ylabel(fs.qlabel("比较器反相端电压", "mV"))
a2.set_title("(b) 电机启动：τ 太小会误跳闸", fontsize=10); a2.legend(fontsize=7, loc="upper right")
assert peaks[10e-3] > V_H and peaks[47e-3] < V_H and peaks[100e-3] < V_H
fs.save(fig, N, "11_p3_2_inverse_time.png")

# ---------- page3 参数表的数字：采样电阻怎么选 ----------
print("[表] Rs/Ω | 门限 mV | 1 A 功耗 W | 跳闸电流时功耗 W | LM393 失调 5 mV 占门限 | 1 A 时电机少得 V")
for rs in [0.01, 0.05, 0.1, 0.5]:
    vth = I_TRIP * rs
    print(f"[表] {rs} | {vth*1e3:.1f} | {1*rs:.2f} | {I_TRIP**2*rs:.2f} | {5e-3/vth*100:.1f}% | {1*rs:.2f}")
print(f"[数值] LM393 偏置电流 250 nA × R_F 10 kΩ = {250e-9*sim.RF*1e3:.1f} mV")
