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

# ---------- page3 练习 2 / 练习 4 的数字（不画图，只打印并核对） ----------
t2 = np.arange(0, 0.5, dt)
x50 = sim.I_NORM + (sim.I_STALL - sim.I_NORM) * np.exp(-t2 / 0.05)   # 启动冲击改为 50 ms 衰减
ex2 = {}
for tau in (47e-3, 100e-3):
    y = sim.lowpass(x50 * sim.RS, dt, tau, 0.0)
    ex2[tau] = (y.max(), t2[y.argmax()])
    print(f"[数值] 练习 2：冲击衰减 50 ms，τ = {tau*1e3:.0f} ms 时峰值 {y.max()*1e3:.0f} mV（启动后 {t2[y.argmax()]*1e3:.0f} ms）")
assert ex2[47e-3][0] > V_H and ex2[100e-3][0] < V_H
assert abs(ex2[47e-3][0] - 0.220) < 0.005 and abs(ex2[100e-3][0] - 0.156) < 0.005
x20 = sim.I_NORM + (sim.I_STALL - sim.I_NORM) * np.exp(-t2 / 0.02)
i2t_extra = np.sum(x20**2 - sim.I_NORM**2) * dt
print(f"[数值] 练习 4：启动冲击比稳定 1 A 多出的 I²t = {i2t_extra:.3f} A²s（公式 16 × 20 ms = 0.32 A²s）")
assert abs(i2t_extra - 0.32) < 0.005

# ---------- page3 参数表的数字：采样电阻怎么选 ----------
print("[表] Rs/Ω | 门限 mV | 1 A 功耗 W | 跳闸电流时功耗 W | LM393 失调 5 mV 占门限 | 1 A 时电机少得 V")
for rs in [0.01, 0.05, 0.1, 0.5]:
    vth = I_TRIP * rs
    print(f"[表] {rs} | {vth*1e3:.1f} | {1*rs:.2f} | {I_TRIP**2*rs:.2f} | {5e-3/vth*100:.1f}% | {1*rs:.2f}")
print(f"[数值] LM393 偏置电流 250 nA × R_F 10 kΩ = {250e-9*sim.RF*1e3:.1f} mV")

import numpy as np                    # page4 面包板小工具要用
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs
from figstyle import C

# ======================================================================
# page4 动手实验篇：面包板俯视图（本节点自带一份小工具，只在本文件内使用）
# 面包板：列号 1..ncol；上半区 a–e 行、下半区 f–j 行，同一列的 a–e 五个孔连通，f–j 五个孔连通；
# 上下各两条电源轨（tp/tn 在上，bp/bn 在下），每条轨整条连通（有的面包板轨道在中间断开，正文会提醒）。
# 导线颜色：正电源 = 橙色，0 V（地）= 黑色，负电源 = 蓝色，信号 = 蓝绿色。
# 每条导线、每个元件引脚都登记到「网络」里（并查集），最后用 assert 检查想要的连接都接上了、不该通的没通。
# ======================================================================
import matplotlib.patches as mpatches

BB_Y = dict(a=9, b=8, c=7, d=6, e=5, f=3, g=2, h=1, i=0, j=-1)
BB_RAIL_Y = dict(tp=11.4, tn=10.6, bp=-2.6, bn=-3.4)
BB_WIRE = dict(pos=C["vout"], gnd="#000000", neg=C["vin"], sig=C["fb"])


class Breadboard:
    def __init__(self, ncol=30, rails=None, figsize=(10, 5.2)):
        self.ncol = ncol
        self.rails = rails or dict(tp=("+", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"), bn=("−", "neg"))
        self.parent = {}
        self.used = {}
        self.pins = {}
        self.fig, self.ax = plt.subplots(figsize=figsize)
        ax = self.ax
        ax.set_xlim(-7.5, ncol + 3.6)
        ax.set_ylim(-6.0, 12.4)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(mpatches.FancyBboxPatch((-0.6, -4.1), ncol + 1.2, 16.2, boxstyle="round,pad=0.1",
                                             fc="#f4f4f4", ec="0.6", lw=0.8))
        ax.add_patch(mpatches.Rectangle((-0.4, 3.6), ncol + 0.8, 0.8, fc="#e2e2e2", ec="none"))
        for r, y in BB_Y.items():
            ax.text(-0.9, y, r, ha="center", va="center", fontsize=7, color="0.35")
            ax.text(ncol + 0.9, y, r, ha="center", va="center", fontsize=7, color="0.35")
            for c in range(1, ncol + 1):
                ax.add_patch(mpatches.Rectangle((c - 0.13, y - 0.13), 0.26, 0.26, fc="0.72", ec="none"))
        for c in range(1, ncol + 1):
            if c == 1 or c % 5 == 0:
                ax.text(c, 9.75, str(c), ha="center", va="center", fontsize=7, color="0.35")
                ax.text(c, -1.75, str(c), ha="center", va="center", fontsize=7, color="0.35")
        for name, y in BB_RAIL_Y.items():
            lab, kind = self.rails[name]
            ax.plot([0.5, ncol + 0.5], [y + 0.32 * (1 if name in ("tp", "bp") else -1)] * 2,
                    color=BB_WIRE[kind], lw=1.0)
            ax.text(ncol + 1.0, y, lab, ha="left", va="center", fontsize=8, color=BB_WIRE[kind])
            for c in range(1, ncol + 1):
                if c % 6 != 0:
                    ax.add_patch(mpatches.Rectangle((c - 0.13, y - 0.13), 0.26, 0.26, fc="0.72", ec="none"))

    # ---- 孔位与网络 ----
    def xy(self, h):
        if isinstance(h, tuple):
            return h
        for rail in ("tp", "tn", "bp", "bn"):
            if h.startswith(rail):
                c = int(h[len(rail):])
                assert 1 <= c <= self.ncol and c % 6 != 0, f"电源轨孔 {h} 不存在"
                return (c, BB_RAIL_Y[rail])
        r, c = h[0], int(h[1:])
        assert r in BB_Y and 1 <= c <= self.ncol, f"孔 {h} 不存在"
        return (c, BB_Y[r])

    def strip(self, h):
        if isinstance(h, tuple):
            return ("ext", h)
        for rail in ("tp", "tn", "bp", "bn"):
            if h.startswith(rail):
                return rail
        return ("T" if h[0] in "abcde" else "B") + h[1:]

    def _find(self, s):
        self.parent.setdefault(s, s)
        while self.parent[s] != s:
            s = self.parent[s]
        return s

    def _union(self, a, b):
        self.parent[self._find(a)] = self._find(b)

    def _use(self, h, who):
        if isinstance(h, tuple):
            return
        self.xy(h)
        assert h not in self.used, f"孔 {h} 已被 {self.used[h]} 占用，{who} 不能再插"
        self.used[h] = who

    def net(self, h):
        return self._find(self.strip(self.pins.get(h, h)))

    def connected(self, *hs):
        return len({self.net(h) for h in hs}) == 1

    # ---- 画导线、元件、外部接线端 ----
    def wire(self, h1, h2, kind="sig", bend=0.0):
        self._use(h1, f"导线{h1}-{h2}")
        self._use(h2, f"导线{h1}-{h2}")
        self._union(self.strip(h1), self.strip(h2))
        (x1, y1), (x2, y2) = self.xy(h1), self.xy(h2)
        if bend:
            xm, ym = (x1 + x2) / 2, (y1 + y2) / 2 + bend
            t = np.linspace(0, 1, 30)
            xs = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * xm + t ** 2 * x2
            ys = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * ym + t ** 2 * y2
        else:
            xs, ys = [x1, x2], [y1, y2]
        self.ax.plot(xs, ys, color=BB_WIRE[kind], lw=2.4, solid_capstyle="round", zorder=3)
        for x, y in ((x1, y1), (x2, y2)):
            self.ax.plot(x, y, "o", ms=3.2, color=BB_WIRE[kind], zorder=4)

    def ext(self, xy, text, kind="sig", dx=-0.45, dy=0.0, ha="right"):
        """板外接线端（电池、电源、信号源的夹子）：画一个空心圆和文字，返回坐标元组，可直接当孔用。"""
        self.ax.plot(*xy, "o", ms=7, mfc="white", mec=BB_WIRE[kind], mew=1.6, zorder=5)
        self.ax.text(xy[0] + dx, xy[1] + dy, text, ha=ha, va="center", fontsize=8, color=BB_WIRE[kind], zorder=5)
        return xy

    def _pins(self, name, hs):
        for k, h in hs.items():
            self._use(h, f"{name}.{k}")
            self.pins[f"{name}.{k}"] = h

    def two(self, name, h1, h2, style="R", label=None, lpos=None):
        """两脚元件：style = R 电阻 / C 瓷片电容 / CE 电解电容（h1 为 + 脚）/ D 二极管（h1 阳极、h2 阴极）/ LED / Z 稳压管 / L 电感 / F 保险丝。"""
        self._pins(name, {"1": h1, "2": h2})
        (x1, y1), (x2, y2) = self.xy(h1), self.xy(h2)
        ax = self.ax
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        L = np.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        w = min(0.45 * L, 1.3)
        ax.plot([x1, xm - ux * w / 2], [y1, ym - uy * w / 2], color="0.45", lw=1.2, zorder=5)
        ax.plot([xm + ux * w / 2, x2], [ym + uy * w / 2, y2], color="0.45", lw=1.2, zorder=5)
        ang = np.degrees(np.arctan2(uy, ux))
        fc = dict(R="#d9c7a3", C="#f2d06b", CE="#5b7fa8", D="#444444", LED="#ffb3b3", Z="#9a6a3a",
                  L="#7f7f7f", F="#dddddd")[style]
        h = 0.55 if style != "CE" else 0.8
        rect = mpatches.FancyBboxPatch((xm - w / 2, ym - h / 2), w, h, boxstyle="round,pad=0.02",
                                       fc=fc, ec="0.25", lw=0.8, zorder=6)
        import matplotlib.transforms as mtr
        rect.set_transform(mtr.Affine2D().rotate_deg_around(xm, ym, ang) + ax.transData)
        ax.add_patch(rect)
        if style in ("D", "Z", "LED"):     # 阴极色环画在 h2 一端
            bx, by = xm + ux * w * 0.32, ym + uy * w * 0.32
            ax.plot([bx - uy * h / 2, bx + uy * h / 2], [by + ux * h / 2, by - ux * h / 2],
                    color="white" if style != "LED" else "0.2", lw=2.2, zorder=7)
        if style == "CE":
            ax.text(x1 - ux * 0.05 + 0.35 * uy, y1 + 0.35, "+", fontsize=9, ha="center", va="bottom",
                    color="k", zorder=7, fontweight="bold")
        if label:
            ox, oy = lpos or ((0, 0.62) if abs(uy) < 0.5 else (0.45, 0))
            ax.text(xm + ox, ym + oy, label, fontsize=7.5, ha="center" if abs(uy) < 0.5 and not lpos else "left",
                    va="center", zorder=8,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))

    def dip8(self, name, col, label, pinlabels=None):
        """8 脚双列直插芯片跨在中间凹槽上，缺口朝左：1–4 脚在 f 行（col..col+3），5–8 脚在 e 行（col+3..col）。"""
        hs = {}
        for k in range(4):
            hs[str(1 + k)] = f"f{col + k}"
            hs[str(8 - k)] = f"e{col + k}"
        self._pins(name, hs)
        ax = self.ax
        ax.add_patch(mpatches.FancyBboxPatch((col - 0.45, 3.35), 3.9, 1.3, boxstyle="round,pad=0.05",
                                             fc="#333333", ec="k", zorder=6))
        ax.add_patch(mpatches.Wedge((col - 0.45, 4.0), 0.25, -90, 90, fc="#888888", zorder=7))
        ax.text(col + 1.5, 4.0, label, color="white", fontsize=7.5, ha="center", va="center", zorder=7)
        for k in range(4):
            for pin, y in ((1 + k, 3.0), (8 - k, 5.0)):
                ax.plot([col + k, col + k], [y, 4.0 + (0.65 if y > 4 else -0.65)], color="0.3", lw=1.4, zorder=5)
            ax.text(col + k, 3.55, str(1 + k), color="white", fontsize=6, ha="center", va="center", zorder=8)
            ax.text(col + k, 4.45, str(8 - k), color="white", fontsize=6, ha="center", va="center", zorder=8)

    def multi(self, name, hs, label, w=None, h=1.0, fc="#555555", at=None):
        """多脚元件（三极管、电位器、模块……）：hs = {脚名: 孔}；画一个方块并从方块拉线到各脚，脚名标在孔旁。"""
        self._pins(name, hs)
        pts = [self.xy(v) for v in hs.values()]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        cx, cy = at or (np.mean(xs), max(ys) + 1.1)
        w = w or max(xs) - min(xs) + 1.0
        ax = self.ax
        ax.add_patch(mpatches.FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.05",
                                             fc=fc, ec="k", lw=0.8, zorder=6))
        ax.text(cx, cy, label, color="white", fontsize=7.5, ha="center", va="center", zorder=7)
        for k, (x, y) in zip(hs.keys(), pts):
            ax.plot([x, x], [y, cy - h / 2 if y < cy else cy + h / 2], color="0.3", lw=1.4, zorder=5)
            ax.text(x + 0.18, y + 0.32 * (1 if y < cy else -1), k, fontsize=6.5, ha="left",
                    va="bottom" if y < cy else "top", color="k", zorder=8)

    def probe(self, h, text, dx=0.35, dy=0.35, ha="left"):
        """测量点：在孔上画红紫色空心圈并写上名字。"""
        x, y = self.xy(h)
        self.ax.plot(x, y, "o", ms=9, mfc="none", mec=C["third"], mew=1.6, zorder=9)
        self.ax.text(x + dx, y + dy, text, fontsize=7.5, color=C["third"], ha=ha, va="bottom", zorder=9,
                     bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))

    def note(self, x, y, text, **kw):
        self.ax.text(x, y, text, fontsize=8, **kw)

    def legend(self, kinds=("pos", "gnd", "neg", "sig")):
        from matplotlib.lines import Line2D
        names = dict(pos="正电源线（橙）", gnd="0 V 地线（黑）", neg="负电源线（蓝）", sig="信号线（蓝绿）")
        hs = [Line2D([], [], color=BB_WIRE[k], lw=2.4, label=names[k]) for k in kinds]
        self.ax.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, 0.035), ncol=len(hs), fontsize=8,
                       frameon=False)


def bb11():
    """11 page4：低压、小电流版过载保护。12 V 只接小电阻负载（正常约 12 mA），7805 给 LM393 供 5 V；
    R_S 换成 10 Ω（跳闸电流约 19 mA），C_F 换成 470 µF（τ 4.7 s，肉眼和秒表看得清）；用 LM393 的 B 组。"""
    bb = Breadboard(ncol=30, rails=dict(tp=("+5 V（7805 输出）", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"),
                                        bn=("+12 V", "pos")), figsize=(11, 5.8))
    bb.wire(bb.ext((-2.0, -3.4), "12 V 直流电源 +", "pos"), "bn1", "pos")
    bb.wire(bb.ext((-2.0, -2.0), "12 V 直流电源 −", "gnd"), "bp2", "gnd")
    bb.wire("tn1", "bp1", "gnd")                                 # 上下两条 0 V 轨连起来
    # 7805（TO-220 正面朝你，从左到右 IN、GND、OUT）插 f2、f3、f4
    bb.multi("U2", {"IN": "f2", "GND": "f3", "OUT": "f4"}, "7805", w=2.8, h=0.8, fc="#4d4d4d", at=(3.0, 4.0))
    bb.wire("j2", "bn2", "pos")
    bb.wire("j3", "bp3", "gnd")
    bb.two("Cin", "h2", "h3", "C", None)
    bb.two("Cout", "i3", "i4", "C", None)
    bb.note(0.6, 1.25, "0.33µF", color="0.3", ha="right")
    bb.note(4.4, 0.0, "0.1µF", color="0.3")
    bb.wire("g4", "tp8", "pos")                                  # 5 V 跨过凹槽送到上方 +5 V 轨
    # LM393 插第 20～23 列；用 B 组（5 脚 IN+、6 脚 IN−、7 脚 OUT 都在上半区）
    bb.dip8("U1", 20, "LM393")
    bb.wire("a20", "tp20", "pos")                                # 8 脚 VCC
    bb.wire("j21", "bp21", "gnd")                                # A 组 2 脚接地（不用）
    bb.wire("j22", "bp22", "gnd")                                # A 组 3 脚接地（不用）
    bb.wire("j23", "bp23", "gnd")                                # 4 脚 GND
    bb.two("RPU", "b21", "b17", "R", "2.2k", lpos=(0, 0.55))
    bb.wire("a17", "tp17", "pos")
    bb.two("RH", "a21", "a23", "R", "100k", lpos=(0, 0.5))
    bb.two("RA", "b23", "b27", "R", "33k", lpos=(0.3, 0.55))
    bb.wire("a27", "tp27", "pos")
    bb.two("RB", "d23", "d25", "R", "1k", lpos=(0.2, -0.5))
    bb.wire("a25", "tn25", "gnd")
    # 功率部分：IRLZ44N 背面（金属片）朝你，从左到右 S、D、G，插 f13、f14、f15
    bb.multi("Q1", {"S": "f13", "D": "f14", "G": "f15"}, "IRLZ44N", w=2.8, h=0.8, fc="#4d4d4d", at=(14.0, 4.0))
    bb.wire("c21", "g15", "sig")                                 # 7 脚 OUT → 栅极
    bb.wire("c22", "g16", "sig")                                 # 6 脚 IN− ← 滤波后的电压（第 16 列）
    bb.two("RS", "j13", "bp13", "R", "R_S 10Ω", lpos=(-0.4, 0))
    bb.two("RF", "i13", "i16", "R", "R_F 10k", lpos=(0, -0.5))
    bb.two("CF", "j16", "bp16", "CE", "470µF", lpos=(0.4, 0))
    bb.wire("h14", "h8", "sig")                                  # 漏极引到第 8 列
    bb.two("RN", "j8", "bn8", "R", "1.5k", lpos=(-0.4, 0))
    bb.two("LED", "g10", "g8", "LED", "LED", lpos=(0, 0.55))     # 阳极 g10，阴极 g8（接漏极）
    bb.two("RLED", "j10", "bn10", "R", "2.2k", lpos=(0.45, 0))
    bb.two("RO", "i8", "bn5", "R", "RO", lpos=(-0.45, 0.2))
    bb.note(8.0, -4.6, "过载：RO（1k 或 470Ω）一端插 i8、", ha="center")
    bb.note(8.0, -5.15, "另一端插 bn5；拔掉 = 恢复正常负载", ha="center")
    assert bb.connected("U2.OUT", "tp1") and bb.connected("U1.8", "tp1") and bb.connected("U1.4", "tn1")
    assert bb.connected("U1.7", "Q1.G", "RPU.1", "RH.1") and bb.connected("U1.5", "RH.2", "RA.1", "RB.1")
    assert bb.connected("RPU.2", "RA.2", "tp1") and bb.connected("RB.2", "tn1")
    assert bb.connected("U1.6", "CF.1", "RF.2") and bb.connected("Q1.S", "RS.1", "RF.1")
    assert bb.connected("Q1.D", "RN.1", "LED.2", "RO.1") and bb.connected("LED.1", "RLED.1")
    assert bb.connected("RN.2", "RLED.2", "RO.2", "bn1", "U2.IN")
    assert bb.connected("RS.2", "CF.2", "U2.GND", "U1.2", "U1.3", "bp1")
    assert not bb.connected("tp1", "bn1") and not bb.connected("bn1", "bp1") and not bb.connected("tp1", "tn1")
    bb.probe("g13", "V_S", dx=-0.3, dy=0.25, ha="right")
    bb.probe("h16", "V_−", dx=0.3, dy=0.1)
    bb.probe("c23", "V_+", dx=0.3, dy=0.05)
    bb.probe("d21", "V_G", dx=-0.3, dy=0.05, ha="right")
    bb.probe("g14", "V_D", dx=0.05, dy=0.3)
    bb.probe("h4", "5 V", dx=0.3, dy=0.05)
    bb.legend(("pos", "gnd", "sig"))
    print(f"11 p4 面包板：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def p4_breadboards():
    bb = bb11()
    fs.save(bb.fig, N, "11_p4_1_bb_protect.png")
    plt.close(bb.fig)
    print("11_figs p4 OK")


if __name__ == "__main__":
    p4_breadboards()


# ===== 第 8 轮补图（page1–3）=====
from schem import *
HL = C["bad"]


def _l(d, xy, text, color=None):
    e = elm.Label().at(xy).label(text, loc="center")
    if color: e = e.color(color)
    d += e


def p1_3_sense():
    """直觉版：电机 → 开关 → 采样电阻 → 地，采样电压送比较器。"""
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 6))
        _l(d, (0, 6.5), "+12 V")
        d += elm.Motor().endpoints((0, 6), (0, 4))
        _l(d, (-1.2, 5), "电机 M")
        d += elm.Switch().endpoints((0, 4), (0, 2.3))
        _l(d, (-1.5, 3.15), "开关\n（MOS 管）")
        d += elm.Dot().at((0, 2.3))
        d += elm.Resistor().endpoints((0, 2.3), (0, 0)).color(HL)
        _l(d, (-1.4, 1.15), "采样电阻 $R_S$\n0.1 Ω", HL)
        d += elm.Ground().at((0, 0))
        d += elm.Line().endpoints((0, 2.3), (2.5, 2.3))
        d += elm.Arrow().at((2.5, 2.3)).to((4.0, 2.3))
        _l(d, (5.6, 2.3), "$V = I \\cdot R_S$\n（1 A → 0.1 V）\n去比较器判断")
        d += elm.Arrow().at((1.0, 5.6)).to((1.0, 3.0)).color(C["cur"])
        _l(d, (1.4, 4.3), "$I$", C["cur"])
    save_schem(d, "11", "11_p1_3_sense.png")


def p2_3_thresholds():
    """推导一：基准分压的戴维南等效 + 回差电阻，输出高 / 输出低两种情况。"""
    top = 3.0
    with drawing(fontsize=11) as d:
        for ox, high in ((0, True), (12.0, False)):
            d += elm.SourceV().endpoints((ox, 0), (ox, top))
            _l(d, (ox - 1.0, top / 2), "$V_T$\n0.147 V")
            d += elm.Resistor().endpoints((ox, top), (ox + 2.6, top))
            _l(d, (ox + 1.3, top + 0.55), "$R_T$ 0.971 kΩ")
            d += elm.Dot().at((ox + 2.6, top))
            _l(d, (ox + 2.6, top - 0.5), "同相端 +")
            d += elm.Resistor().endpoints((ox + 2.6, top), (ox + 5.4, top)).color(C["fb"])
            _l(d, (ox + 4.0, top + 0.55), "$R_H$ 100 kΩ", C["fb"])
            if high:
                d += elm.Resistor().endpoints((ox + 5.4, top), (ox + 8.0, top))
                _l(d, (ox + 6.7, top + 0.55), "$R_{PU}$ 2.2 kΩ")
                d += elm.SourceV().endpoints((ox + 8.0, 0), (ox + 8.0, top))
                _l(d, (ox + 9.0, top / 2), "$V_{CC}$\n5 V")
                d += elm.Line().endpoints((ox, 0), (ox + 8.0, 0))
                _l(d, (ox + 4.0, -0.9), "(a) 输出为高（MOS 管导通）：$V_H$ ≈ 0.193 V")
            else:
                d += elm.Line().endpoints((ox + 5.4, top), (ox + 5.4, 0)).color(HL)
                _l(d, (ox + 6.6, top / 2), "输出 ≈ 0 V\n（拉到地）", HL)
                d += elm.Line().endpoints((ox, 0), (ox + 5.4, 0))
                _l(d, (ox + 2.8, -0.9), "(b) 跳闸后输出为低：$V_L$ ≈ 0.146 V")
    save_schem(d, "11", "11_p2_3_thresholds.png")


def _kelvin(d, ox, good):
    top = 5.0
    d += elm.Line().endpoints((ox, top + 0.6), (ox, top))
    _l(d, (ox + 1.8, top + 0.95), "来自 MOS 管源极（电机电流 I）")
    d += elm.Dot().at((ox, top))
    d += elm.Resistor().endpoints((ox, top), (ox, 2.5))
    _l(d, (ox - 1.0, 3.75), "$R_S$\n0.1 Ω")
    d += elm.Dot().at((ox, 2.5))
    d += elm.Resistor().endpoints((ox, 2.5), (ox, 0)).color(HL if not good else "black")
    _l(d, (ox - 1.3, 1.25), "大电流地线\n（有压降）", HL if not good else None)
    d += elm.Dot().at((ox, 0))
    d += elm.Ground().at((ox, 0))
    bx = ox + 4.0
    for a, b in (((bx, 1.5), (bx + 2.2, 1.5)), ((bx + 2.2, 1.5), (bx + 2.2, 4.5)),
                 ((bx + 2.2, 4.5), (bx, 4.5)), ((bx, 4.5), (bx, 1.5))):
        d += elm.Line().endpoints(a, b)
    _l(d, (bx + 1.1, 3.0), "比较器\n入口")
    d += elm.Line().endpoints((ox, top), (ox + 2.0, top))
    d += elm.Line().endpoints((ox + 2.0, top), (ox + 2.0, 3.8))
    d += elm.Line().endpoints((ox + 2.0, 3.8), (bx, 3.8))
    _l(d, (bx - 0.35, 4.1), "+")
    col = C["fb"] if good else HL
    y_from = 2.5 if good else 0
    d += elm.Line().endpoints((ox, y_from), (ox + 2.0, y_from)).color(col)
    if not good:
        d += elm.Line().endpoints((ox + 2.0, y_from), (ox + 2.0, 2.5)).color(col)
    d += elm.Line().endpoints((ox + 2.0, 2.5), (bx, 2.5)).color(col)
    _l(d, (bx - 0.35, 2.8), "−")
    _l(d, (ox + 2.5, -1.0), "(b) 对：两根线直接从 $R_S$ 两端单独引出" if good
       else "(a) 错：采样地接在大电流地线远端，压降叠进采样电压")


def p3_3_kelvin():
    with drawing(fontsize=11) as d:
        _kelvin(d, 0, False)
        _kelvin(d, 11.0, True)
    save_schem(d, "11", "11_p3_3_kelvin.png")


def p3_4_fuse():
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 6))
        _l(d, (0, 6.5), "+12 V")
        d += elm.Fuse().endpoints((0, 6), (0, 4)).color(HL)
        _l(d, (-2.0, 5), "保险丝（慢断型）\n额定 ≥ 1.33 A\n熔化 $I^2t$ ≥ 1.6 A²s", HL)
        d += elm.Motor().endpoints((0, 4), (0, 2))
        _l(d, (-1.4, 3), "电机 M\n正常 1 A")
        d += elm.Switch().endpoints((0, 2), (0, 0))
        _l(d, (-1.0, 1), "开关")
        d += elm.Ground().at((0, 0))
    save_schem(d, "11", "11_p3_4_fuse.png")


def round8():
    p1_3_sense(); p2_3_thresholds(); p3_3_kelvin(); p3_4_fuse()
    print("11_figs 第 8 轮补图 OK")


if __name__ == "__main__":
    round8()
