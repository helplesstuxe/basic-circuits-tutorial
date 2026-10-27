"""38 同步检波（电磁流量计）：全部配图。
运行：/workspace/circuits-venv/bin/python code/figs/38_figs.py [p1_1 p4_3 ...]
图上的每个数字都来自 code/38_sim.py（这里用 importlib 载入并调用它的函数），运行时打印出来。
面包板图用 code/30_bbkit.py 画，同时登记到本文件自带的「连通检查」里，用 assert 确认每个节点真的连在一起、
不该连的没有连上；SPICE 复核见 spice/38/run.py。
"""
import os, sys, io, contextlib, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
import lab_schem as ls         # 只借用 probe / colnote / lab / title / note / _pin 这些小工具（不修改它）
import numpy as np
import matplotlib.pyplot as plt


def _load(name, path, quiet=False):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    if quiet:
        with contextlib.redirect_stdout(io.StringIO()):
            sp.loader.exec_module(m)
    else:
        sp.loader.exec_module(m)
    return m


bb = _load("bbkit30", os.path.join(HERE, "..", "30_bbkit.py"))
f30 = _load("figs30", os.path.join(HERE, "30_figs.py"))          # 只借用 draw_ina、decap（不修改 30 节文件）
sim = _load("sim38", os.path.join(HERE, "..", "38_sim.py"), quiet=True)

N = "38"
W = bb.BB_WIRE
G = sim.G
E = sim.EMID


# ======================================================================================
# 连通检查：面包板上同一列同一半区（a–e 或 f–j）的 5 个孔是一条金属片；电源轨整条相通；导线把两条金属片并起来。
# ======================================================================================
class Net:
    def __init__(self):
        self.p = {}

    @staticmethod
    def strip(h):
        if "-" in h:                     # 电源轨，如 "T1-5"
            return h.split("-")[0]
        r, c = h[0], int(h[1:])
        return ("top" if r in "abcde" else "bot", c)

    def f(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def join(self, a, b):
        self.p[self.f(self.strip(a))] = self.f(self.strip(b))

    def same(self, a, b):
        return self.f(self.strip(a)) == self.f(self.strip(b))


def wire(net, ax, a, b, kind, via=()):
    bb.bb_wire(ax, a, b, kind, via=via)
    net.join(a, b)


def must(net, groups, apart):
    """groups：每组里的孔必须相通；apart：每对必须不通。"""
    for g in groups:
        for h in g[1:]:
            assert net.same(g[0], h), f"{g[0]} 与 {h} 应该相通"
    for a, b in apart:
        assert not net.same(a, b), f"{a} 与 {b} 不应相通"


def dip16(ax, col, text):
    """16 脚芯片跨槽：1～8 脚在 f 行第 col～col+7 列，16～9 脚在 e 行第 col～col+7 列，缺口朝左。"""
    ax.add_patch(bb._BbRect((col - 0.45, 3.25), 7.9, 2.15, fc="0.18", ec="0.1", zorder=5))
    ax.add_patch(bb._BbWedge((col - 0.45, 4.3), 0.3, -90, 90, fc="#f4f1ea", ec="none", zorder=6))
    ax.text(col + 3.5, 4.3, text, ha="center", va="center", fontsize=8, color="white", zorder=6)
    for k in range(8):
        ax.text(col + k, 3.55, str(k + 1), ha="center", va="center", fontsize=6.5, color="white", zorder=6)
        ax.text(col + k, 5.05, str(16 - k), ha="center", va="center", fontsize=6.5, color="white", zorder=6)


def board_battery(ax, x=3.2):
    ax.add_patch(bb._BbRect((x, 12.9), 4.0, 0.75, fc="#ffe082", ec="0.3", lw=0.8, zorder=5))
    ax.text(x + 2.0, 13.27, "9 V 电池", ha="center", va="center", fontsize=7.5, zorder=6)
    ax.plot([x + 0.8, x + 0.8], [12.9, 11.6], color=W["pos"], lw=2.0, zorder=3); ax.plot(x + 0.8, 11.6, "o", ms=4, color=W["pos"], zorder=4)
    ax.plot([x + 3.2, x + 3.2], [12.9, 10.8], color=W["gnd"], lw=2.0, zorder=3); ax.plot(x + 3.2, 10.8, "o", ms=4, color=W["gnd"], zorder=4)
    ax.text(x + 0.4, 13.27, "+", ha="right", va="center", fontsize=9, color=W["pos"])
    ax.text(x + 3.6, 13.27, "−", ha="left", va="center", fontsize=9)


def arduino_box(ax, x0, y0, w, pins, title="Arduino Uno（USB 供电）"):
    """板外的 Arduino：pins = [(名字, x)]，每个引脚在盒子下沿有一个小方块。返回 {名字: (x, y)}。"""
    ax.add_patch(bb._BbRect((x0, y0), w, 1.0, fc="#b3e5fc", ec="0.3", lw=0.8, zorder=5))
    ax.text(x0 + 0.3, y0 + 0.72, title, ha="left", va="center", fontsize=7.5, zorder=6)
    out = {}
    for name, x in pins:
        ax.add_patch(bb._BbRect((x - 0.22, y0 - 0.05), 0.44, 0.3, fc="0.2", ec="none", zorder=6))
        ax.text(x, y0 + 0.36, name, ha="center", va="center", fontsize=6.5, zorder=6)
        out[name] = (x, y0 - 0.05)
    return out


def ext(ax, xy, hole, kind, via=()):
    """板外引脚 → 面包板孔（画线，不进连通检查：它连的是 Arduino）。"""
    x1, y1 = bb.bb_xy(hole)
    pts = [xy] + list(via) + [(x1, y1)]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=W[kind], lw=2.0, zorder=3, solid_capstyle="round")
    ax.plot(x1, y1, "o", ms=3.5, color=W[kind], zorder=4)


# ======================================================================================
# page1
# ======================================================================================
def p1_1():
    fig, ax = fs.diagram(w=8.4, h=3.8, xlim=(0, 10), ylim=(0, 4.6))
    from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
    ax.add_patch(Rectangle((1.0, 1.0), 6.0, 2.2, fc="#e8f1fa", ec=fs.C["edge"], lw=1.2))
    for y in (1.6, 2.1, 2.6):
        ax.add_patch(FancyArrowPatch((1.4, y), (3.0, y), arrowstyle="-|>", mutation_scale=10, color=fs.C["vin"]))
    ax.text(2.2, 2.85, "液体流速 v", ha="center", fontsize=9, color=fs.C["vin"])
    for x in (4.2, 4.8, 5.4):
        ax.add_patch(Circle((x, 2.1), 0.13, fc="white", ec=fs.C["third"], lw=1.2))
        ax.plot([x - 0.08, x + 0.08], [2.02, 2.18], color=fs.C["third"], lw=1); ax.plot([x - 0.08, x + 0.08], [2.18, 2.02], color=fs.C["third"], lw=1)
    ax.text(4.8, 1.25, "磁场 B（垂直纸面向里，线圈产生）", ha="center", fontsize=8.5, color=fs.C["third"])
    ax.add_patch(Rectangle((4.65, 3.2), 0.3, 0.35, fc="0.3")); ax.add_patch(Rectangle((4.65, 0.65), 0.3, 0.35, fc="0.3"))
    ax.annotate("", xy=(6.4, 3.2), xytext=(6.4, 1.0), arrowprops=dict(arrowstyle="<->", color="k", lw=1))
    ax.text(6.3, 2.1, "管径\nD_pipe", fontsize=8.5, va="center", ha="right")
    ax.plot([4.8, 8.6], [3.55, 3.55], color=fs.C["vout"], lw=1.4); ax.plot([4.8, 8.6], [0.65, 0.65], color=fs.C["vout"], lw=1.4)
    ax.plot([8.6, 8.6], [3.55, 2.6], color=fs.C["vout"], lw=1.4); ax.plot([8.6, 8.6], [0.65, 1.6], color=fs.C["vout"], lw=1.4)
    fs.box(ax, 8.6, 2.1, "电极电压\nE = k·B·D_pipe·v", w=2.4, h=1.0, fs=9, fc=fs.C["fill2"])
    ax.text(4.5, 3.4, "上电极", ha="right", fontsize=8.5); ax.text(4.5, 0.75, "下电极", ha="right", fontsize=8.5)
    ax.text(0.1, 4.3, "磁场里流动的导电液体 = 一根切割磁感线的「液体导线」", fontsize=10, weight="bold")
    print("[图 38-p1-1] 电磁流量计示意：E = k·B·D_pipe·v")
    fs.save(fig, N, "38_p1_1_flowmeter.png")


def _p_point(t, with50=True):
    """P 点对 V_MID 的电压（mV）：±E 方波 + 直流 + D5 的 50 Hz 干扰（用 38_sim 的数）。"""
    sig = np.where((t * sim.FEXC) % 1 < 0.5, 1.0, -1.0)
    dc = (sim.node_p(sim.VIO, 0, 0.5) + sim.node_p(0, 0, 0.5)) / 2
    v = E * sig + dc
    if with50:
        v = v + sim.e5 * np.sign(np.sin(2 * np.pi * 50.0 * t + 0.4))
    return v * 1e3, sig, dc * 1e3


def p1_2():
    t = np.arange(0, 0.64, 1e-4)
    v, sig, dc = _p_point(t)
    prod = v * sig                                    # 乘以同步的 ±1
    run = np.cumsum(prod) / np.arange(1, t.size + 1)
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.2, 3.0))
    a.plot(t * 1e3, v, color=fs.C["vin"], lw=0.7, label="电极上实际看到的（P 点）")
    a.plot(t * 1e3, (E * sig) * 1e3 + dc, **fs.LS["vout"], label="其中的有用信号 ±E")
    fs.ref_h(a, 0)
    fs.axlabels(a, "时间", "ms", "对 V_MID", "mV")
    a.set_title("信号 ±2.45 mV 埋在 10 倍的 50 Hz 干扰里", fontsize=10)
    a.legend(fontsize=8, loc="upper center", ncol=2)
    a.set_ylim(-32, 45)
    b.plot(t * 1e3, run, **fs.LS["third"], label="乘 ±1 以后的累计平均")
    b.axhline(E * 1e3, **fs.LS["good"], label="真值 E")
    fs.mark(b, t[-1] * 1e3, run[-1], "{:.3f}", " mV", dx=-70, dy=8)
    fs.axlabels(b, "时间", "ms", "累计平均", "mV")
    b.set_ylim(-1, 6)
    b.set_title("跟着励磁「乘 ±1 再平均」：干扰和直流抵消", fontsize=10)
    b.legend(fontsize=8, loc="upper right")
    print(f"[图 38-p1-3] E = {E*1e3:.4f} mV，直流 {dc:+.4f} mV，50 Hz ±{sim.e5*1e3:.3f} mV；4 个周期后平均 {run[-1]:.4f} mV")
    fs.save(fig, N, "38_p1_3_buried.png")


# ======================================================================================
# page2
# ======================================================================================
def p2_1():
    t = np.arange(0, 0.32, 1e-4)
    ph = (t * sim.FEXC) % 1
    ref = np.where(ph < 0.5, 1.0, -1.0)
    s = 2.0 + 0.5 * ref                              # 直流 2（单位任意）+ 幅度 0.5 的方波
    y = s * ref
    fig, ax = plt.subplots(3, 1, figsize=(7.2, 4.4), sharex=True)
    ax[0].plot(t * 1e3, s, **fs.LS["vin"]); ax[0].set_ylabel("输入 x")
    ax[0].axhline(s.mean(), **fs.LS["ref"]); ax[0].text(318, s.mean() + 0.08, f"平均 {s.mean():.2f}（只有直流）", ha="right", fontsize=8.5)
    ax[1].plot(t * 1e3, ref, **fs.LS["fb"]); ax[1].set_ylabel("参考 r")
    ax[1].set_ylim(-1.5, 1.5); ax[1].set_yticks([-1, 0, 1])
    ax[2].plot(t * 1e3, y, **fs.LS["vout"]); ax[2].set_ylabel("y = x·r")
    ax[2].axhline(y.mean(), **fs.LS["good"])
    ax[2].text(318, y.mean() + 0.15, f"平均 {y.mean():.2f} = 方波幅度", ha="right", fontsize=8.5)
    ax[2].set_xlabel("时间 / ms")
    for a in ax:
        a.axhline(0, color="0.6", lw=0.6)
    print(f"[图 38-p2-1] x = 2 ± 0.5，x 平均 {s.mean():.3f}；y = x·r 平均 {y.mean():.3f}（直流 2 被消掉）")
    fs.save(fig, N, "38_p2_1_times_pm1.png")


def p2_2():
    phis = np.linspace(0, 180, 181)
    tri = np.array([sim.demod_avg(p, n=20000) for p in phis])
    sine = 2 / np.pi * np.cos(np.radians(phis))
    pd = np.array([0, 45, 90, 135, 180])
    dig = np.array([sim.arduino_run(phi_deg=p, noise_lsb=0.5).mean() for p in pd]) / (E * 1e3)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.plot(phis, tri, **fs.LS["vout"], label="方波信号 × 方波参考：三角形 1 − 2φ/π")
    ax.plot(phis, sine, **fs.LS["third"], label="正弦信号 × 方波参考：(2/π)·cos φ")
    ax.plot(pd, dig, "o", color=fs.C["fb"], ms=6, label="数字法（只采每半周期后一半，38_sim）")
    for p, v in zip(pd, dig):
        print(f"[数值] 数字法 φ={p}°：{v:+.3f}")
    fs.mark(ax, 45, sim.demod_avg(45, n=20000), "{:.2f}", dx=6, dy=4)
    fs.mark(ax, 0, 2 / np.pi, "{:.3f}", dx=6, dy=-12)
    fs.ref_h(ax, 0)
    ax.set_xticks([0, 45, 90, 135, 180])
    fs.axlabels(ax, "参考比信号超前的相位 φ", "°", "平均值 ÷ 信号幅度")
    ax.legend(fontsize=8, loc="lower left")
    print("[图 38-p2-2] 相位定律：三角形 45° → 0.50，90° → 0；正弦 0° → 2/π = 0.637")
    fs.save(fig, N, "38_p2_2_phase_law.png")


def p2_3():
    cases = [("50/3\n16.7 Hz", 50 / 3), ("50/7\n7.14 Hz", 50 / 7), ("50/6\n8.33 Hz", 50 / 6), ("50/8\n6.25 Hz", 6.25), ("50/10\n5 Hz", 5.0)]
    vals = []
    for _, fe in cases:
        vals.append(max(abs(sim.interf_left(fe, theta=th, n=400_000)) for th in np.linspace(0, np.pi, 7)) * 100)
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    col = [fs.C["bad"] if v > 1 else fs.C["fb"] for v in vals]
    ax.bar(range(len(cases)), vals, color=col, width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.6, f"{v:.1f}%", ha="center", fontsize=9)
        print(f"[数值] 励磁 {cases[i][1]:.3f} Hz：剩 {v:.3f}%")
    ax.set_xticks(range(len(cases)), [c[0] for c in cases], fontsize=9)
    ax.set_ylim(0, 25)
    ax.set_ylabel("50 Hz 干扰剩下 / 幅度的 %")
    ax.set_title("50 Hz 是励磁的奇数倍（朱红）会漏进来；偶数倍（蓝绿）完全抵消", fontsize=10)
    print("[图 38-p2-3] 50 Hz 干扰残留：" + "，".join(f"{c[1]:.3f} Hz {v:.2f}%" for c, v in zip(cases, vals)))
    fs.save(fig, N, "38_p2_3_harmonics.png")


def draw_pm1(d, x0=0.0, y0=0.0, holes=False):
    """±1 级：U3B（R11、R12）+ CD4053 的 A 组开关 + LM393 电平转换 + RU 上拉。(x0, y0) = U3B 同相端左边。返回关键点。"""
    H = (lambda s: f"（{s}）") if holes else (lambda s: "")
    P = lambda x, y: (x0 + x, y0 + y)
    p = {}
    d += (op := elm.Opamp(leads=True).theta(0).anchor("in2").at(P(6.0, 0.0)))
    im, ip, o = op.absanchors["in1"], op.absanchors["in2"], op.absanchors["out"]
    p["op"] = op
    ls.lab(d, (op.absanchors["center"][0] - 0.25, op.absanchors["center"][1]), "U3B", ha="center", fs_=10)
    ls._pin(d, ip, "5", dx=0.3, dy=-0.22); ls._pin(d, im, "6", dx=0.3, dy=0.22); ls._pin(d, o, "7", dx=-0.3, dy=0.25)
    # 输入 fo → R11 → 6 脚；R12 从 7 脚绕回 6 脚
    d += elm.Line().at(P(-1.2, 1.25)).to(P(0.8, 1.25)).color(fs.C["vin"])
    d += elm.Dot().at(P(0.4, 1.25))
    p["fo"] = P(-1.2, 1.25)
    d += elm.Resistor().at(P(0.8, 1.25)).to(P(4.6, 1.25))
    ls.lab(d, P(2.7, 1.8), "R11 10k" + H("c9–c12"), ha="center", fs_=9.5)
    d += elm.Line().at(P(4.6, 1.25)).to(im); d += elm.Dot().at(P(5.2, 1.25))
    d += elm.Line().at(P(5.2, 1.25)).to(P(5.2, 3.0))
    d += elm.Resistor().at(P(5.2, 3.0)).to(P(10.0, 3.0))
    ls.lab(d, P(7.6, 3.55), "R12 10k" + H("b11–b12"), ha="center", fs_=9.5)
    d += elm.Line().at(P(10.0, 3.0)).to(P(10.0, o[1] - y0))
    d += elm.Line().at(o).to(P(10.8, o[1] - y0)); d += elm.Dot().at(P(10.0, o[1] - y0))
    p["out"] = P(10.8, o[1] - y0)
    # CD4053 A 组（画成单刀双掷开关）
    d += elm.Line().at(P(0.4, 1.25)).to(P(0.4, 0.45))
    d += elm.Line().at(P(0.4, 0.45)).to(P(2.6, 0.45))
    d += elm.Dot(open=True).at(P(2.6, 0.45)); ls._pin(d, P(2.6, 0.45), "13 AY", dx=0.0, dy=0.3)
    d += elm.Dot(open=True).at(P(2.6, -0.45)); ls._pin(d, P(2.6, -0.45), "12 AX", dx=0.0, dy=-0.32)
    d += elm.Line().at(P(2.6, -0.45)).to(P(1.0, -0.45)).color(fs.C["third"])
    d += elm.Dot(open=True).at(P(1.0, -0.45))
    ls.lab(d, P(0.8, -0.45), "V_MID", ha="right", fs_=10, color=fs.C["third"])
    p["vmid"] = P(1.0, -0.45)
    d += elm.Dot(open=True).at(P(4.0, 0.0)); ls._pin(d, P(4.0, 0.0), "14", dx=0.0, dy=0.3)
    d += elm.Line().at(P(4.0, 0.0)).to(P(2.72, 0.4)).linewidth(1.6)
    d += elm.Line().at(P(4.0, 0.0)).to(P(2.72, -0.4)).linestyle("--").color("#999999")
    d += elm.Line().at(P(4.0, 0.0)).to(ip)
    for a_, b_ in (((2.1, -1.0), (4.5, -1.0)), ((4.5, -1.0), (4.5, 1.0)), ((4.5, 1.0), (2.1, 1.0)), ((2.1, 1.0), (2.1, -1.0))):
        d += elm.Line().at(P(*a_)).to(P(*b_)).linestyle(":").color(ls.GRAY).linewidth(0.8)
    ls.lab(d, P(4.7, -0.75), "U4 CD4053（A 组）", fs_=9, color=ls.GRAY)
    # 选择端 A（11 脚）← LM393 输出 + RU 上拉到 9 V
    d += elm.Line().at(P(3.4, 0.2)).to(P(3.4, -2.2)).linestyle(":")
    ls._pin(d, P(3.4, -1.55), "11 A", dx=0.45, dy=0.0)
    d += elm.Dot().at(P(3.4, -2.2))
    p["sel"] = P(3.4, -2.2)
    d += elm.Line().at(P(3.4, -2.2)).to(P(12.0, -2.2))
    d += elm.Resistor().at(P(12.0, -2.2)).to(P(12.0, -0.5))
    d += elm.Vdd().at(P(12.0, -0.5)).label("9 V")
    ls.lab(d, P(12.35, -1.35), "RU 10k" + H("c32–c33"), fs_=9.5)
    d += elm.Line().at(P(3.4, -2.2)).to(P(3.4, -3.0))
    d += (cmp_ := elm.Opamp(leads=True).theta(0).anchor("out").at(P(3.4, -3.0)))
    p["cmp"] = cmp_
    ls.lab(d, (cmp_.absanchors["center"][0] - 0.2, cmp_.absanchors["center"][1]), "U5B\nLM393", ha="center", fs_=9)
    ls._pin(d, cmp_.absanchors["out"], "7", dx=0.25, dy=-0.25)
    ls._pin(d, cmp_.absanchors["in1"], "6", dx=0.3, dy=0.22)
    ls._pin(d, cmp_.absanchors["in2"], "5", dx=0.3, dy=-0.22)
    return p


def p2_4():
    with drawing(fontsize=11) as d:
        p = draw_pm1(d)
        c = p["cmp"]
        inp, inm = c.absanchors["in2"], c.absanchors["in1"]
        d += elm.Line().at(inp).to((inp[0] - 0.8, inp[1])).color(fs.C["fb"])
        ls.lab(d, (inp[0] - 0.95, inp[1]), "参考 D10（0/5 V）", ha="right", fs_=10, color=fs.C["fb"])
        d += elm.Line().at(inm).to((inm[0] - 0.8, inm[1]))
        ls.lab(d, (inm[0] - 0.95, inm[1]), "门限 2.5 V", ha="right", fs_=10)
        ls.lab(d, (p["out"][0] + 0.15, p["out"][1] + 0.5), "dm = +fo 或 −fo", fs_=10, color=fs.C["vout"])
        ls.lab(d, (p["fo"][0] - 0.15, p["fo"][1]), "fo（输入，\n对 V_MID）", ha="right", fs_=10, color=fs.C["vin"])
        ls.note(d, (-3.5, -5.0), "D10 高（5 V）→ LM393 输出管断开 → RU 把 A 拉到 9 V（CD4053 在 10 V 供电时要 ≥ 7 V 才认作 1）→ 接 AY：同相端 = fo，倍数 +1。")
        ls.note(d, (-3.5, -5.6), "D10 低（0 V）→ 输出管导通 → A ≈ 0 V → 接 AX（虚线）：同相端 = V_MID，U3B 变成 −R12/R11 = −1 倍反相放大。")
    print("[图 38-p2-4] ±1 级：sel=1 → 同相端 fo（+1）；sel=0 → 同相端 V_MID（−R12/R11 = −1）")
    save_schem(d, N, "38_p2_4_pm1_stage.png")


# ======================================================================================
# page3
# ======================================================================================
def p3_1():
    t, y1 = sim.chain(T=20, flip_at=8.0)
    cf0 = sim.CF; sim.CF = 100e-6
    t2, y2 = sim.chain(T=20, flip_at=8.0)
    sim.CF = cf0
    fig, ax = plt.subplots(figsize=(7.4, 3.1))
    ax.plot(t, y1 * 1e3, **fs.LS["vout"], label="CF 10 µF（τ = 1 s）")
    ax.plot(t2, y2 * 1e3, **fs.LS["third"], label="CF 100 µF（τ = 10 s）")
    fs.ref_v(ax, 8.0, "第 8 s 发 f（翻转 180°）")
    fs.ref_h(ax, 0)
    fs.mark(ax, 7.9, y1[t < 7.9][-1] * 1e3, "{:.2f}", " mV", dx=-62, dy=-16)
    fs.mark(ax, 19.9, y1[-1] * 1e3, "{:.2f}", " mV", dx=-62, dy=6)
    fs.mark(ax, 19.9, y2[-1] * 1e3, "{:.1f}", " mV", dx=-52, dy=8)
    fs.axlabels(ax, "时间", "s", "万用表读数 J−K", "mV")
    ax.legend(fontsize=8, loc="lower left")
    ax.set_ylim(-60, 72)
    print(f"[图 38-p3-1] 翻转前 {y1[t<7.9][-1]*1e3:.2f} mV；20 s 时 τ=1 s {y1[-1]*1e3:.2f} mV，τ=10 s {y2[-1]*1e3:.2f} mV")
    fs.save(fig, N, "38_p3_1_settling.png")


def p3_2():
    vdc = -G * sim.dcmax                             # 电位器拧到 0 V 端：INA 输出 −976 mV（page3 符号约定：高于 V_MID 为正）
    _, y = sim.chain(T=12, eps=0.02, vdc=vdc, ac=False)
    _, y0 = sim.chain(T=12, eps=0.02, vdc=0.0, ac=False)
    leak = (sim.tail_stats(_, y)[0] - sim.tail_stats(_, y0)[0]) * 1e3
    _, ya = sim.chain(T=12, eps=0.02, vdc=vdc, ac=True)
    _, ya0 = sim.chain(T=12, eps=0.02, vdc=0.0, ac=True)
    leak_ac = (sim.tail_stats(_, ya)[0] - sim.tail_stats(_, ya0)[0]) * 1e3
    duty = abs(2 * 0.01 * vdc * 1e3)
    _, yt = sim.chain(T=20, tone=sim.F50)
    rip = sim.tail_stats(_, yt, last=6.0)[1] * 1e3
    m0 = sim.tail_stats(*sim.chain(T=12))[0] * 1e3
    m45 = sim.tail_stats(*sim.chain(T=12, phi_deg=45))[0] * 1e3   # 模拟值只在 page4 第 6 步答案框里用
    loss_tri = m0 * 45 / 90                                       # 三角形定律：错 45° 读数剩 1 − 45/90 = 一半
    items = [("直流 " + f"{vdc*1e3:.0f}".replace("-", "−") + f" mV（电位器拧到 0 V 端）+ 失配 2%，\n不加交流耦合（模拟 {leak:+.2f}；公式 +9.76）", abs(leak), fs.C["bad"]),
             ("同上，加了 CH/RH 交流耦合", abs(leak_ac), fs.C["fb"]),
             ("占空比偏 1%（不加交流耦合，2δ·V_DC）", duty, fs.C["bad"]),
             ("U3B 失调 7 mV × 2（翻转相减可消）", 14.0, fs.C["vout"]),
             ("50 Hz：CF 上瞬时纹波峰峰（表上只跳 1～3 mV，平均不变）", rip, fs.C["vout"]),
             ("参考错 45°：读数少掉的部分（三角形定律）", loss_tri, fs.C["bad"])]
    fig, ax = plt.subplots(figsize=(7.6, 3.2))
    y_ = np.arange(len(items))
    ax.barh(y_, [max(i[1], 0.05) for i in items], color=[i[2] for i in items], height=0.55)
    for k, it in enumerate(items):
        ax.text(max(it[1], 0.05) * 1.15, k, f"{it[1]:.2f} mV", va="center", fontsize=9)
        print(f"[数值] {it[0]}：{it[1]:.3f} mV")
    ax.set_xscale("log"); ax.set_xlim(0.03, 300)
    ax.set_yticks(y_, [i[0] for i in items], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel(f"对读数的影响 / mV（有用读数 {m0:.2f} mV）")
    print(f"[图 38-p3-2] 误差来源：泄漏 {leak:.2f}/{leak_ac:.3f} mV，占空比 {duty:.2f}，失调 14，纹波 {rip:.2f}，45° 损失（三角形定律）{loss_tri:.2f}（模拟 {m0-m45:.2f}，不上图）")
    fs.save(fig, N, "38_p3_2_error_budget.png")



# ======================================================================================
# page4：面包板与对照原理图
# ======================================================================================
def _ina_board(ax, net):
    """30 节的仪表放大器（U1 第 22 列、U2 第 36 列、V_MID），孔位与图 30-p4-3 相同，只是电桥换成了模拟电极。"""
    wire(net, ax, "a22", "T1-22", "pos"); wire(net, ax, "j25", "B1-25", "gnd")
    bb.bb_dip8(ax, 22, "U1 LM358")
    bb.bb_part2(ax, "b22", "T2-21", "", kind="box", dy=0.0, fc="#f2c94c")
    bb._bb_label(ax, 20.0, 8.5, "C1 0.1µ", fs_=6.5)
    bb.bb_res(ax, "b23", "b24", "R5 10k")
    wire(net, ax, "a24", "a28", "fb")
    bb.bb_res(ax, "e28", "f28", "RG 1k", dy=0.55)
    wire(net, ax, "h23", "h28", "fb")
    bb.bb_res(ax, "i22", "i23", "R6 10k", dy=-0.55)
    wire(net, ax, "c23", "c32", "fb")
    bb.bb_res(ax, "e32", "f32", "R7 10k", dy=-0.55)
    wire(net, ax, "g32", "g37", "fb", via=[(32, 2.45), (37, 2.45)])
    wire(net, ax, "j22", "j33", "fb", via=[(22, -1.5), (33, -1.5)])
    bb.bb_res(ax, "i33", "i38", "R9 10k", dy=-0.5)
    bb.bb_res(ax, "h36", "h37", "R8 10k", dy=-0.5)
    bb.bb_res(ax, "h38", "h46", "R10 10k", dy=0.5)
    bb.bb_dip8(ax, 36, "U2 LM358")
    wire(net, ax, "a36", "T1-36", "pos"); wire(net, ax, "j39", "B1-39", "gnd")
    bb.bb_part2(ax, "b36", "T2-35", "", kind="box", dy=0.0, fc="#f2c94c")
    bb._bb_label(ax, 34.0, 8.5, "C2 0.1µ", fs_=6.5)
    wire(net, ax, "b37", "b38", "fb")
    bb.bb_res(ax, "b39", "b42", "RM1 10k")
    wire(net, ax, "a42", "T1-42", "pos")
    bb.bb_res(ax, "c39", "c44", "RM2 10k", dy=-0.5)
    wire(net, ax, "a44", "T2-44", "gnd")
    wire(net, ax, "d37", "g46", "neg", via=[(37, 6.5), (46, 6.5)])


def p4_1():
    """板 A：模拟电极（测试夹具）+ 30 节的仪表放大器。"""
    net = Net()
    rails = {"T1": ("9 V", W["pos"]), "T2": ("0 V", W["gnd"]), "B1": ("0 V", W["gnd"]), "B2": ("9 V", W["pos"])}
    fig, ax = bb.bb_board(46, rails, figsize=(13.6, 6.0))
    wire(net, ax, "T2-1", "B1-1", "gnd", via=[(-0.4, 10.8), (-0.4, -2.8)])
    wire(net, ax, "T1-1", "B2-1", "pos", via=[(-0.9, 11.6), (-0.9, -3.6)])
    board_battery(ax, 27.2)
    pins = arduino_box(ax, 0.6, 13.3, 9.0, [("D9", 2), ("D5", 3), ("GND", 6)])
    ext(ax, pins["D9"], "a2", "sig"); ext(ax, pins["D5"], "a3", "out")
    ext(ax, pins["GND"], "T2-6", "gnd"); net.join("T2-6", "T2-6")
    # 模拟电极：P 点 = 第 9 列上半；本地 V_MID = 第 9 列下半
    bb.bb_res(ax, "b2", "b9", "RS1 1M")
    bb.bb_part2(ax, "d5", "d3", "CN 10µ", kind="cap", dy=-0.6)
    bb.bb_res(ax, "c5", "c9", "RN 100k", dy=-0.5)
    wire(net, ax, "a9", "a11", "sig", via=[(9, 9.5), (11, 9.5)])
    bb.bb_res(ax, "e9", "f9", "RS2 1k", dy=0.0)
    bb.bb_block(ax, ["j16", "j17", "j18"], "", pins=None, fc="#90caf9", pad=0.32)
    bb._bb_label(ax, 17.0, -1.95, "RP 10k 电位器", fs_=7)
    wire(net, ax, "i16", "B2-16", "pos", via=[(15.55, 0), (15.55, -3.6)])
    wire(net, ax, "i18", "B1-18", "gnd", via=[(18.45, 0), (18.45, -2.8)])
    wire(net, ax, "f17", "e17", "fb")
    bb.bb_res(ax, "b11", "b17", "RD 100k")
    # P → U1 的 3 脚（仪放 + 输入，第 24 列下半）；夹具旁的 V_MID → U1 的 5 脚那一列（仪放 − 输入，第 25 列上半）
    wire(net, ax, "d11", "g24", "sig", via=[(11, 6.5), (20.5, 6.5), (20.5, 1.5), (24, 1.5)])
    wire(net, ax, "g9", "b25", "neg", via=[(9, 2.5), (19.5, 2.5), (19.5, 7.5), (25, 7.5)])
    _ina_board(ax, net)
    wire(net, ax, "i46", "d25", "neg", via=[(46, 0.5), (26.5, 0.5), (26.5, 6.5), (25, 6.5)])
    # 去板 B 的线
    for x, y0, kind, text in ((36, -1, "out", "Vo → 板 B a2"), (46, -1, "neg", "V_MID → 板 B 下外轨")):
        ax.plot([x, x], [y0, -5.2], color=W[kind], lw=2.0, zorder=3); ax.plot(x, y0, "o", ms=4, color=W[kind], zorder=4)
        bb._bb_label(ax, x, -5.55, text, fs_=7)
    for name, y, kind in (("T1", 11.6, "pos"), ("B1", -2.8, "gnd")):
        ax.plot([46, 49.6], [y, y], color=W[kind], lw=2.0, zorder=3)
    bb._bb_label(ax, 49.2, 12.2, "9 V → 板 B", fs_=7); bb._bb_label(ax, 49.2, -2.2, "0 V → 板 B", fs_=7)
    must(net, [["d9", "a11", "g24", "f24", "b11"], ["f9", "j9", "b25", "d25", "e25", "i46", "j46", "d37", "e37"],
               ["f17", "b17"], ["i16", "T1-5"], ["i18", "T2-3", "B1-30"], ["j36", "f36"]],
           apart=[("d9", "j9"), ("d9", "T1-1"), ("j9", "T2-1"), ("e17", "d9"), ("j36", "j46"), ("e25", "f24"), ("d9", "e25"), ("j9", "f24")])
    bb.bb_probe(ax, "d9", "A", dx=0.9, dy=-0.45)
    bb.bb_probe(ax, "j9", "B", dx=-1.0, dy=-0.9)
    bb.bb_probe(ax, "h17", "D", dx=1.0, dy=0.6)
    bb.bb_probe(ax, "g36", "C", dx=-0.8, dy=-0.9)
    ax.set_xlim(-1.6, 51.5); ax.set_ylim(-7.4, 14.6)
    ax.text(1.0, -6.3, "Arduino 用 USB 供电，模拟部分用 9 V 电池；两边的 0 V 由黑线 GND→T2-6 连在一起", fontsize=8, va="center")
    ax.text(1.0, -6.95, "蓝线 d11→g24：P → U1 的 3 脚（仪放 +）；紫线 g9→b25、i46→d25：V_MID → 5 脚那一列（仪放 −）；交叉处不相连；长线只从孔旁经过", fontsize=8, va="center")
    bb.bb_legend(ax, [("pos", "红：9 V"), ("gnd", "黑：0 V"), ("neg", "紫：V_MID")], x=1.0, y=-4.6)
    bb.bb_legend(ax, [("sig", "蓝：信号 P / D9"), ("out", "橙：D5 干扰、Vo 出线"), ("fb", "绿：放大器内部、跨槽短线")], x=20.0, y=-4.6)
    print("[图 38-p4-1] 板 A：D9→a2，RS1 b2–b9，D5→a3，CN d3(−)–d5(+)，RN c5–c9，P = 第 9 列上（a9→a11 延长），RS2 e9–f9，"
          "RP j16/j17/j18（i16→9 V，i18→0 V），f17–e17，RD b11–b17，d11→g24（P → U1 3 脚），g9→b25、i46→d25（V_MID → U1 5 脚那一列）；"
          "测点 A d9、B j9、C g36、D h17；连通检查通过")
    fs.save(fig, N, "38_p4_1_board_a.png")



def _vmid_buffer(d, x0, y0, out_note="V_MID ≈ 4.5 V\n紫线 d37→g46"):
    """RM1、RM2 分压 + U2B 跟随器（与 30 节同一位置）。(x0, y0) = U2B 同相端。"""
    d += elm.Vdd().at((x0 - 2.2, y0 + 3.0)).label("9 V")
    d += elm.Resistor().at((x0 - 2.2, y0 + 3.0)).to((x0 - 2.2, y0))
    ls.lab(d, (x0 - 2.6, y0 + 1.5), "RM1 10k\n（b39–b42）", ha="right", fs_=9.5)
    d += elm.Dot().at((x0 - 2.2, y0))
    d += elm.Resistor().at((x0 - 2.2, y0)).to((x0 - 2.2, y0 - 3.0))
    ls.lab(d, (x0 - 2.6, y0 - 1.5), "RM2 10k\n（c39–c44）", ha="right", fs_=9.5)
    d += elm.Ground().at((x0 - 2.2, y0 - 3.0))
    d += (fo := elm.Opamp(leads=True).theta(0).anchor("in2").at((x0, y0)))
    d += elm.Line().at((x0 - 2.2, y0)).to(fo.absanchors["in2"])
    o = fo.absanchors["out"]; m_ = fo.absanchors["in1"]
    d += elm.Line().at(m_).to((m_[0] - 0.5, m_[1]))
    d += elm.Line().at((m_[0] - 0.5, m_[1])).to((m_[0] - 0.5, m_[1] + 1.0))
    d += elm.Line().at((m_[0] - 0.5, m_[1] + 1.0)).to((o[0] + 0.6, m_[1] + 1.0))
    d += elm.Line().at((o[0] + 0.6, m_[1] + 1.0)).to((o[0] + 0.6, o[1]))
    d += elm.Line().at(o).to((o[0] + 1.6, o[1])).color(fs.C["third"])
    d += elm.Dot().at((o[0] + 0.6, o[1]))
    d += elm.Dot(open=True).at((o[0] + 1.6, o[1]))
    ls.lab(d, (o[0] + 1.8, o[1]), out_note, fs_=10, color=fs.C["third"])
    ls._pin(d, fo.absanchors["in2"], "5", dx=0.3, dy=-0.22)
    ls._pin(d, m_, "6", dx=0.3, dy=0.22)
    ls._pin(d, o, "7", dx=-0.3, dy=0.25)
    ls.lab(d, (fo.absanchors["center"][0] - 0.2, fo.absanchors["center"][1]), "U2B", ha="center", fs_=9)
    ls.lab(d, (o[0] + 0.8, m_[1] + 1.35), "b37–b38 短接", fs_=8.5, color=ls.TEAL)
    return fo


def p4_2():
    """板 A 对照原理图：模拟电极 + 仪表放大器（与图 38-p4-1 的孔位一一对应）。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (1.0, 15.2), "板 A：模拟电极 + 仪表放大器（U1、U2 都是 LM358；9 V 电池；Arduino 用 USB 供电）")
        nm = dict(R5="R5 10k（b23–b24）", R6="R6 10k（i22–i23）", RG="RG 1k\n（e28–f28）",
                  R7="R7 10k（e32–f32）", R8="R8 10k（h36–h37）", R9="R9 10k（i33–i38）", R10="R10 10k\n（h38–h46）")
        p = f30.draw_ina(d, -1.0, 0.0, names=nm)
        xP = -6.0
        # P 点：RS1 从 D9 来；RS2 到 V_MID；RN–CN 从 D5 来；RD 从电位器滑动端来
        # P → A2 的 3 脚（仪放 + 输入）：先向右，再向下走到下面那只运放
        xPd = xP + 1.6
        d += elm.Line().at((xP, 7.0)).to((xPd, 7.0)).color(fs.C["vin"])
        d += elm.Line().at((xPd, 7.0)).to((xPd, p["a2p"][1])).color(fs.C["vin"])
        d += elm.Line().at((xPd, p["a2p"][1])).to(p["a2p"]).color(fs.C["vin"])
        ls.lab(d, (xPd + 0.15, 0.4), "蓝线 d11→g24", ha="left", fs_=8, color=fs.C["vin"])
        # V_MID → A1 的 5 脚（仪放 − 输入）：同名空心圆
        d += elm.Line().at(p["a1p"]).to((p["a1p"][0] - 1.2, p["a1p"][1])).color(fs.C["third"])
        d += elm.Dot(open=True).at((p["a1p"][0] - 1.2, p["a1p"][1]))
        ls.lab(d, (p["a1p"][0] - 1.35, p["a1p"][1] + 0.55), "V_MID（d25←紫线 i46）", ha="right", fs_=9, color=fs.C["third"])
        d += elm.Dot().at((xP, 7.0))
        ls.probe(d, (xP, 7.0), "A", dx=0.0, dy=-1.0)
        ls.colnote(d, (xP + 0.25, 5.75), "P：第 9 列上半", "right", ofst=0.0)
        d += elm.Resistor().at((-12.0, 7.0)).to((xP, 7.0))
        ls.lab(d, (-9.0, 6.45), "RS1 1M（b2–b9）", ha="center", fs_=10)
        d += elm.Dot(open=True).at((-12.0, 7.0))
        ls.lab(d, (-12.2, 7.0), "Arduino D9\n（a2）", ha="right", fs_=10, color=fs.C["vin"])
        d += elm.Line().at((xP, 9.0)).to((xP, 7.0))
        d += elm.Resistor().at((-10.0, 9.0)).to((xP, 9.0))
        ls.lab(d, (-8.0, 9.55), "RN 100k（c5–c9）", ha="center", fs_=10)
        d += elm.Capacitor(polar=True).at((-13.0, 9.0)).to((-10.0, 9.0)).reverse()
        ls.lab(d, (-11.5, 9.75), "CN 10µ（+ 在 d5）", ha="center", fs_=9.5)
        d += elm.Dot(open=True).at((-13.0, 9.0))
        ls.lab(d, (-13.2, 9.0), "Arduino D5\n（a3）", ha="right", fs_=10, color=fs.C["vout"])
        d += elm.Dot().at((xP, 9.0))
        d += elm.Line().at((xP, 11.5)).to((xP, 9.0))
        d += elm.Resistor().at((-12.5, 11.5)).to((xP, 11.5))
        ls.lab(d, (-9.25, 12.05), "RD 100k（b11–b17）", ha="center", fs_=10)
        d += (rp := elm.Potentiometer().at((-16.0, 13.0)).to((-16.0, 10.0)))
        tap = rp.absanchors["tap"]
        d += elm.Line().at(tap).to((-12.5, tap[1]))
        ls.probe(d, (-13.6, tap[1]), "D", dx=0.0, dy=0.9)
        ls.lab(d, (-16.9, 11.5), "RP 10k\n（j16/j17/j18）", ha="right", fs_=9.5)
        d += elm.Vdd().at((-16.0, 13.0)).label("9 V（i16）")
        d += elm.Ground().at((-16.0, 10.0))
        ls.colnote(d, (-15.4, 10.2), "0 V（i18）", "right", ofst=0.0)
        ls.colnote(d, (-13.0, 11.05), "滑动端 j17，跨槽 f17–e17", "right", ofst=0.0)
        # RS2 → V_MID；V_MID → U1 3 脚
        d += elm.Resistor().at((xP, 7.0)).to((xP, 3.0))
        ls.lab(d, (xP - 0.4, 5.0), "RS2 1k\n（e9–f9）", ha="right", fs_=10)
        d += elm.Line().at((xP, 3.0)).to((xP, 0.0)).color(fs.C["third"])
        d += elm.Dot().at((xP, 0.0))
        d += elm.Line().at((xP, 0.0)).to((xP - 2.0, 0.0)).color(fs.C["third"])
        d += elm.Dot(open=True).at((xP - 2.0, 0.0))
        ls.lab(d, (xP - 2.2, 0.0), "V_MID", ha="right", fs_=10, color=fs.C["third"])
        ls.probe(d, (xP, 0.0), "B", dx=0.0, dy=-1.0)
        ls.colnote(d, (xP + 0.25, -1.3), "第 9 列下半（j9）", "right", ofst=0.0)
        ls.lab(d, (xP - 2.2, -0.75), "紫线 g9→b25 接到\nU1 5 脚那一列", ha="right", fs_=8.5, color=fs.C["third"])
        # INA 的引脚、电源
        for key, pin in (("a1p", "5"), ("a1m", "6"), ("a2p", "3"), ("a2m", "2"), ("a3p", "3"), ("a3m", "2")):
            ls._pin(d, p[key], pin, dx=0.3, dy=0.22 if key == "a1p" or key == "a1m" else -0.22)
        ls._pin(d, p["a1o"], "7", dx=-0.3, dy=0.25)
        ls._pin(d, p["a2o"], "1", dx=-0.3, dy=-0.25)
        ls._pin(d, p["a3o"], "1", dx=-0.3, dy=0.25)
        ls.lab(d, (p["a1"].absanchors["center"][0] + 1.5, p["a1p"][1] + 0.9), "U1B", ha="center", fs_=9, color=ls.GRAY)
        ls.lab(d, (p["a2"].absanchors["center"][0] + 1.5, p["a2p"][1] - 0.9), "U1A", ha="center", fs_=9, color=ls.GRAY)
        ls.lab(d, (p["a3"].absanchors["center"][0] + 1.5, p["a3p"][1] - 1.0), "U2A", ha="center", fs_=9, color=ls.GRAY)
        for op, top, bot in ((p["a1"], "8", None), (p["a2"], None, "4"), (p["a3"], "8", "4")):
            vd, vs = op.absanchors["vd"], op.absanchors["vs"]
            if op is p["a1"]:
                vd, vs = vs, vd
            if top:
                d += elm.Line().at(vd).to((vd[0], vd[1] + 0.5))
                d += elm.Vdd().at((vd[0], vd[1] + 0.5)).label("9 V")
                ls._pin(d, vd, top, dx=0.25, dy=0.25)
            if bot:
                d += elm.Line().at(vs).to((vs[0], vs[1] - 0.5))
                d += elm.Ground().at((vs[0], vs[1] - 0.5))
                ls._pin(d, vs, bot, dx=0.25, dy=-0.25)
        d += elm.Line().at((p["xo3"], p["a3o"][1])).to((p["xo3"] + 1.2, p["a3o"][1])).color(fs.C["vout"])
        d += elm.Dot(open=True).at((p["xo3"] + 1.2, p["a3o"][1]))
        ls.probe(d, (p["xo3"], p["a3o"][1]), "C", dx=0.0, dy=1.0)
        ls.lab(d, (p["xo3"] + 1.55, p["a3o"][1] - 0.05), "Vo（g36）\n橙线 j36 → 板 B a2", fs_=9.5, color=fs.C["vout"])
        yv = p["yref"] - 1.2
        d += elm.Line().at((p["xq"], p["yref"])).to((p["xq"], yv)).color(fs.C["third"])
        d += elm.Dot(open=True).at((p["xq"], yv))
        ls.lab(d, (p["xq"] + 0.3, yv - 0.1), "V_MID（第 46 列：h46、g46、i46→d25、j46→板 B）", fs_=9.5, color=fs.C["third"])
        _vmid_buffer(d, p["xq"] + 1.0, p["yref"] - 6.0)
        f30.decap(d, -16.0, -3.0, "C1", "U1：b22→上 0 V 轨")
        f30.decap(d, -11.0, -3.0, "C2", "U2：b36→上 0 V 轨")
        ls.note(d, (-17.0, -6.6), "读图：一条线 = 一个节点；空心圆 = 同名的点（所有 V_MID 是同一点，所有 9 V、0 V 各是同一条轨）；黄色圆圈 A～D = 测量点（字母）；")
        ls.note(d, (-17.0, -7.2), "灰色或括号里的字 = 面包板孔位；运放旁的小黑字 = 引脚号。Arduino 的 GND 接上 0 V 轨（T2-6），和 9 V 电池负极连在一起。")
    print("[图 38-p4-2] 板 A 原理图：RS1/RS2/RN–CN/RD–RP → P（测点 A）→ U1 3 脚（仪放 +）；V_MID → U1 5 脚（仪放 −）；G = 21；C1、C2 去耦")
    save_schem(d, N, "38_p4_2_schem_a.png")


def p4_3():
    """板 B：交流耦合 + 跟随（U3A）+ ±1 级（U3B、U4 CD4053、U5 LM393）+ RC 低通 + A0 分压。"""
    net = Net()
    rails = {"T1": ("9 V", W["pos"]), "T2": ("0 V", W["gnd"]), "B1": ("0 V", W["gnd"]), "B2": ("V_MID", W["neg"])}
    fig, ax = bb.bb_board(42, rails, figsize=(13.0, 6.2))
    wire(net, ax, "T2-1", "B1-1", "gnd", via=[(-0.4, 10.8), (-0.4, -2.8)])
    # 从板 A 来的四根线
    for y, kind, text in ((11.6, "pos", "9 V（板 A T1 轨）"), (-2.8, "gnd", "0 V（板 A B1 轨）"), (-3.6, "neg", "V_MID（板 A j46）")):
        ax.plot([-4.6, 0.7], [y, y], color=W[kind], lw=2.0, zorder=3)
        bb._bb_label(ax, -4.6, y + 0.45, text, fs_=6.5)
    ax.plot([-4.6, 2, 2], [12.4, 12.4, 9], color=W["out"], lw=2.0, zorder=3); ax.plot(2, 9, "o", ms=3.5, color=W["out"], zorder=4)
    bb._bb_label(ax, -3.0, 12.85, "Vo（板 A j36）", fs_=6.5)
    pins = arduino_box(ax, 3.4, 13.3, 39.0, [("A0", 5), ("D10", 35), ("5V", 38), ("GND", 41)])
    ext(ax, pins["A0"], "a5", "sig"); ext(ax, pins["D10"], "a35", "sig")
    ext(ax, pins["5V"], "a38", "pos"); ext(ax, pins["GND"], "T2-41", "gnd")
    # 输入：A0 分压、交流耦合
    bb.bb_res(ax, "b2", "b5", "RA1 10k")
    bb.bb_res(ax, "c5", "c8", "RA2 10k", dy=-0.5)
    wire(net, ax, "a8", "T2-8", "gnd")
    bb.bb_part2(ax, "e2", "f2", "", kind="box", dy=0.0, fc="#9fd3c7")
    bb._bb_label(ax, 3.4, 4.0, "CH 10µ\n无极性", fs_=6.5)
    bb.bb_res(ax, "i2", "i6", "RH 100k", dy=-0.5)
    wire(net, ax, "j6", "B2-6", "neg")
    # U3：A 半边跟随，B 半边 ±1
    bb.bb_dip8(ax, 10, "U3 LM358")
    wire(net, ax, "a10", "T1-10", "pos"); wire(net, ax, "j13", "B1-13", "gnd")
    bb.bb_part2(ax, "b10", "T2-9", "", kind="box", dy=0.0, fc="#f2c94c")
    bb._bb_label(ax, 8.0, 8.5, "C3 0.1µ", fs_=6.5)
    wire(net, ax, "g2", "g12", "sig", via=[(2, 2.5), (12, 2.5)])
    wire(net, ax, "g10", "g11", "fb")
    wire(net, ax, "h10", "h9", "fb")
    wire(net, ax, "f9", "e9", "fb")
    bb.bb_res(ax, "c9", "c12", "R11 10k", dy=-0.5)
    bb.bb_res(ax, "b11", "b12", "R12 10k", dy=0.5)
    wire(net, ax, "a11", "a15", "out", via=[(11, 9.5), (15, 9.5)])
    bb.bb_res(ax, "c15", "c19", "RF 100k", dy=0.5)
    bb.bb_part2(ax, "e19", "f19", "", kind="box", dy=0.0, fc="#9fd3c7")
    bb._bb_label(ax, 17.6, 4.0, "CF 10µ\n无极性", fs_=6.5)
    wire(net, ax, "j19", "B2-19", "neg")
    # U4 CD4053
    dip16(ax, 20, "U4 CD4053")
    wire(net, ax, "a20", "T1-20", "pos")
    bb.bb_part2(ax, "b20", "T2-19", "", kind="box", dy=0.0, fc="#f2c94c")
    bb._bb_label(ax, 19.2, 8.5, "C4", fs_=6.5)
    wire(net, ax, "a26", "T2-26", "gnd"); wire(net, ax, "a27", "T2-27", "gnd")
    for c in (25, 26, 27):
        wire(net, ax, f"j{c}", f"B1-{c}", "gnd")
    wire(net, ax, "d9", "d23", "sig", via=[(9, 5.6), (23, 5.6)])
    wire(net, ax, "d22", "d13", "fb", via=[(22, 6.5), (13, 6.5)])
    wire(net, ax, "j29", "B2-29", "neg"); wire(net, ax, "f29", "e29", "neg")
    wire(net, ax, "d29", "d24", "neg", via=[(29, 6.5), (24, 6.5)])
    # U5 LM393：只用 B 比较器（5、6、7 脚）
    bb.bb_dip8(ax, 32, "U5 LM393")
    wire(net, ax, "a32", "T1-32", "pos")
    bb.bb_part2(ax, "b32", "T2-31", "", kind="box", dy=0.0, fc="#f2c94c")
    bb._bb_label(ax, 30.6, 8.5, "C5", fs_=6.5)
    for c in (33, 34, 35):
        wire(net, ax, f"j{c}", f"B1-{c}", "gnd")
    bb.bb_res(ax, "c32", "c33", "RU 10k", dy=-0.5)
    wire(net, ax, "d33", "d25", "out", via=[(33, 5.6), (25, 5.6)])
    bb.bb_res(ax, "b38", "b36", "RT1 10k", dy=-0.5)
    bb.bb_res(ax, "a36", "T2-36", "RT2 10k", dy=0.5)
    wire(net, ax, "d36", "d34", "fb", via=[(36, 6.5), (34, 6.5)])
    must(net, [["a2", "b2", "e2"], ["f2", "g2", "f12", "h2", "i2"], ["f10", "g10", "f11", "h10", "h9", "f9", "e9", "c9", "d9", "d23", "e23"],
               ["j6", "B2-1", "j19", "j29", "e29", "d24", "e24"], ["e11", "b11", "a15", "b15", "c15"], ["c19", "e19", "d19"],
               ["e22", "d13", "e13"], ["e25", "d33", "e33", "c33", "b25"], ["b36", "a36", "d34", "e34"],
               ["a32", "e32", "a20", "e20", "a10", "e10", "T1-1"], ["j25", "j26", "j27", "a26", "a27", "j33", "j34", "j35", "j13", "T2-1"]],
         apart=[("f2", "e2"), ("f9", "f12"), ("e11", "e12"), ("e19", "f19"), ("j6", "T2-1"), ("e25", "T1-1"), ("e35", "e34"),
                ("e23", "e24"), ("e22", "e23"), ("e33", "e32")])
    bb.bb_probe(ax, "c2", "C", dx=-0.9, dy=0.5)
    bb.bb_probe(ax, "h2", "E", dx=-0.9, dy=0.0)
    bb.bb_probe(ax, "j10", "F", dx=0.0, dy=-1.0)
    bb.bb_probe(ax, "b15", "G", dx=-0.9, dy=0.0)
    bb.bb_probe(ax, "b25", "H", dx=0.8, dy=0.6)
    bb.bb_probe(ax, "d19", "J", dx=0.9, dy=0.0)
    bb.bb_probe(ax, "h19", "K", dx=0.9, dy=0.0)
    bb.bb_probe(ax, "d5", "L", dx=0.0, dy=-0.9)
    bb.bb_probe(ax, "c36", "M", dx=-0.75, dy=0.0)
    ax.set_xlim(-6.0, 46.5); ax.set_ylim(-7.4, 14.6)
    bb.bb_legend(ax, [("pos", "红：9 V / 5 V"), ("gnd", "黑：0 V"), ("neg", "紫：V_MID")], x=1.0, y=-4.6)
    bb.bb_legend(ax, [("sig", "蓝：信号"), ("out", "橙：±1 输出、选择线"), ("fb", "绿：芯片之间短线")], x=20.0, y=-4.6)
    ax.text(1.0, -6.3, "d9→d23、d33→d25 贴着 e 行上方走，d22→d13、d29→d24、d36→d34 从 d 行上方绕：这五根线彼此不交叉。U3 是 LM358，U5 是 LM393，别插反。", fontsize=8, va="center")
    ax.text(1.0, -6.95, "黄色小方块 C3、C4、C5 = 0.1 µF 去耦电容；青色方块 CH、CF = 10 µF 无极性电容（跨在中间槽上）。U4 第 1～5 脚（f20～f24）和 15 脚（a21）不用，空着。", fontsize=8, va="center")
    print("[图 38-p4-3] 板 B：Vo→a2，RA1 b2–b5，RA2 c5–c8，A0→a5，CH e2–f2，RH i2–i6，U3 第 10 列，g2→g12，g10–g11，h10→h9，f9–e9，"
          "R11 c9–c12，R12 b11–b12，a11→a15，RF c15–c19，CF e19–f19，U4 第 20 列，d9→d23，d22→d13，d29→d24，U5 第 32 列，"
          "RU c32–c33，d33→d25，D10→a35，5V→a38，RT1 b36–b38，RT2 a36→0 V，d36→d34；连通检查通过")
    fs.save(fig, N, "38_p4_3_board_b.png")


def p4_4():
    """板 B 对照原理图：隔直 + U3A 跟随 → ±1（U3B + U4 + U5B）→ RF/CF 平均；A0 分压；比较器阈值。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (-2.0, 7.6), "板 B：隔直 → 跟随 → ×±1 → RC 平均（U3 = LM358，U4 = CD4053，U5 = LM393；都接 9 V 和 0 V）")
        p = draw_pm1(d, 0.0, 0.0, holes=True)
        # U3A 跟随器：H → 3 脚；2 脚接 1 脚；1 脚 → fo
        d += (fa := elm.Opamp(leads=True).theta(0).anchor("out").at((-2.0, 1.25)))
        d += elm.Line().at((-2.0, 1.25)).to(p["fo"])
        ip, im, o = fa.absanchors["in2"], fa.absanchors["in1"], fa.absanchors["out"]
        ls.lab(d, (fa.absanchors["center"][0] - 0.25, fa.absanchors["center"][1]), "U3A", ha="center", fs_=10)
        ls._pin(d, ip, "3", dx=0.3, dy=-0.22); ls._pin(d, im, "2", dx=0.3, dy=0.22); ls._pin(d, o, "1", dx=-0.3, dy=0.25)
        d += elm.Line().at(im).to((im[0] - 0.5, im[1]))
        d += elm.Line().at((im[0] - 0.5, im[1])).to((im[0] - 0.5, im[1] + 1.0))
        d += elm.Line().at((im[0] - 0.5, im[1] + 1.0)).to((o[0] + 0.4, im[1] + 1.0))
        d += elm.Line().at((o[0] + 0.4, im[1] + 1.0)).to((o[0] + 0.4, o[1]))
        d += elm.Dot().at((o[0] + 0.4, o[1]))
        ls.lab(d, (o[0] - 1.0, im[1] + 1.35), "g10–g11 短接", fs_=8.5, color=ls.TEAL, ha="center")
        ls.probe(d, (p["fo"][0] + 0.2, p["fo"][1]), "F", dx=0.0, dy=-0.85)
        xH = ip[0] - 1.2
        d += elm.Line().at(ip).to((xH, ip[1]))
        d += elm.Dot().at((xH, ip[1]))
        ls.probe(d, (xH, ip[1]), "E", dx=0.0, dy=0.95)
        xV = xH - 4.5
        d += elm.Line().at((xV, ip[1])).to((xV + 0.75, ip[1]))
        d += elm.Capacitor().at((xV + 0.75, ip[1])).to((xH - 0.75, ip[1]))
        d += elm.Line().at((xH - 0.75, ip[1])).to((xH, ip[1]))
        ls.lab(d, (xH - 2.25, ip[1] + 0.75), "CH 10µ 无极性（e2–f2）", ha="center", fs_=9.5)
        d += elm.Resistor().at((xH, ip[1])).to((xH, ip[1] - 3.0))
        ls.lab(d, (xH - 0.35, ip[1] - 1.5), "RH 100k\n（i2–i6）", ha="right", fs_=9.5)
        d += elm.Line().at((xH, ip[1] - 3.0)).to((xH, ip[1] - 3.6)).color(fs.C["third"])
        d += elm.Dot(open=True).at((xH, ip[1] - 3.6))
        ls.lab(d, (xH - 0.25, ip[1] - 3.95), "V_MID（j6→下外轨）", ha="right", fs_=9.5, color=fs.C["third"])
        # Vo 输入 + A0 分压
        d += elm.Dot().at((xV, ip[1]))
        d += elm.Line().at((xV, ip[1])).to((xV - 1.3, ip[1])).color(fs.C["vout"])
        d += elm.Dot(open=True).at((xV - 1.3, ip[1]))
        ls.lab(d, (xV - 1.5, ip[1]), "Vo\n（板 A j36→a2）", ha="right", fs_=10, color=fs.C["vout"])
        ls.probe(d, (xV, ip[1]), "C", dx=0.0, dy=-0.95)
        d += elm.Line().at((xV, ip[1])).to((xV, 5.0))
        d += elm.Resistor().at((xV, 5.0)).to((xV + 2.4, 5.0))
        ls.lab(d, (xV + 1.2, 5.55), "RA1 10k（b2–b5）", ha="center", fs_=9.5)
        d += elm.Dot().at((xV + 2.4, 5.0))
        ls.probe(d, (xV + 2.4, 5.0), "L", dx=0.0, dy=0.95)
        d += elm.Resistor().at((xV + 2.4, 5.0)).to((xV + 2.4, 3.2))
        ls.lab(d, (xV + 2.75, 4.1), "RA2 10k（c5–c8）", fs_=9.5)
        d += elm.Ground().at((xV + 2.4, 3.2))
        d += elm.Line().at((xV + 2.4, 5.0)).to((xV + 4.6, 5.0)).color(fs.C["vin"])
        d += elm.Dot(open=True).at((xV + 4.6, 5.0))
        ls.lab(d, (xV + 4.8, 5.0), "Arduino A0（a5）", fs_=10, color=fs.C["vin"])
        # 输出平均：G → RF → J；CF → K = V_MID
        out = p["out"]
        yr = 2.0
        d += elm.Line().at(out).to((out[0], yr))
        ls.probe(d, (out[0], 1.3), "G", dx=-0.85, dy=0.0)
        d += elm.Resistor().at((out[0], yr)).to((out[0] + 3.5, yr))
        ls.lab(d, (out[0] + 1.75, yr + 0.55), "RF 100k（c15–c19）", ha="center", fs_=9.5)
        xj = out[0] + 3.5
        d += elm.Dot().at((xj, yr))
        d += elm.Line().at((xj, yr)).to((xj + 1.4, yr))
        d += elm.Dot(open=True).at((xj + 1.4, yr))
        ls.probe(d, (xj + 1.4, yr), "J", dx=0.0, dy=0.95)
        ls.lab(d, (xj + 1.65, yr), "d19", fs_=9.5)
        d += elm.Capacitor().at((xj, yr)).to((xj, yr - 2.6))
        ls.lab(d, (xj + 0.4, yr - 1.3), "CF 10µ 无极性\n（e19–f19）", fs_=9.5)
        d += elm.Dot().at((xj, yr - 2.6))
        ls.probe(d, (xj, yr - 2.6), "K", dx=1.0, dy=0.0)
        d += elm.Line().at((xj, yr - 2.6)).to((xj, yr - 3.4)).color(fs.C["third"])
        d += elm.Dot(open=True).at((xj, yr - 3.4))
        ls.lab(d, (xj + 0.25, yr - 3.75), "V_MID（j19→下外轨）", fs_=9.5, color=fs.C["third"])
        ls.lab(d, (xj - 0.6, yr + 1.5), "万用表直流 mV 档：红笔 J、黑笔 K", fs_=9.5, color=ls.GRAY)
        # 选择端测点 H、比较器输入
        ls.probe(d, (8.6, p["sel"][1]), "H", dx=0.0, dy=-0.85)
        cm = p["cmp"]
        c1, c2 = cm.absanchors["in1"], cm.absanchors["in2"]
        xM = c1[0] - 1.2
        d += elm.Line().at(c1).to((xM, c1[1]))
        d += elm.Dot().at((xM, c1[1]))
        ls.probe(d, (xM, c1[1]), "M", dx=0.0, dy=0.85)
        d += elm.Resistor().at((xM - 3.2, c1[1])).to((xM, c1[1]))
        ls.lab(d, (xM - 1.6, c1[1] - 0.6), "RT1 10k（b38–b36）", ha="center", fs_=9.5)
        d += elm.Dot(open=True).at((xM - 3.2, c1[1]))
        ls.lab(d, (xM - 3.4, c1[1]), "Arduino 5V\n（a38）", ha="right", fs_=10, color=fs.C["vdd"] if "vdd" in fs.C else "#c0392b")
        d += elm.Resistor().at((xM, c1[1])).to((xM, c1[1] - 2.2))
        ls.lab(d, (xM - 0.35, c1[1] - 1.6), "RT2 10k\n（a36→0 V）", ha="right", fs_=9.5)
        d += elm.Ground().at((xM, c1[1] - 2.2))
        xD = c2[0] - 0.45
        d += elm.Line().at(c2).to((xD, c2[1])).color(fs.C["vin"])
        d += elm.Line().at((xD, c2[1])).to((xD, c2[1] - 2.9)).color(fs.C["vin"])
        d += elm.Line().at((xD, c2[1] - 2.9)).to((xD - 5.5, c2[1] - 2.9)).color(fs.C["vin"])
        d += elm.Dot(open=True).at((xD - 5.5, c2[1] - 2.9))
        ls.lab(d, (xD - 5.7, c2[1] - 2.9), "Arduino D10\n（a35）", ha="right", fs_=10, color=fs.C["vin"])
        # 电源、不用的引脚、跳线清单
        x0n, y0n = 15.0, -2.6
        ls.lab(d, (x0n, y0n), "图上没画成线、但必须接的：", fs_=10)
        rows = ["U3 LM358：8 脚 → 9 V（a10），4 脚 → 0 V（j13）",
                "U4 CD4053：16 脚 VDD → 9 V（a20）",
                "　6 脚 INH、7 脚 VEE、8 脚 VSS → 0 V（j25、j26、j27）",
                "　9 脚 C、10 脚 B → 0 V（a27、a26）；1～5、15 脚空着",
                "U5 LM393：8 脚 → 9 V（a32），4 脚 → 0 V（j35）",
                "　U5A 不用：2、3 脚 → 0 V（j33、j34），1 脚空着",
                "跳线：蓝 d9→d23（F → 13 AY）；绿 d22→d13（14 → U3 5 脚）",
                "　紫 d29→d24、j29→V_MID（12 AX）；橙 a11→a15（G → RF）",
                "　橙 d33→d25（U5 7 脚 → 11 A）；绿 d36→d34（M → U5 6 脚）",
                "　紫 g2→g12（E → U3 3 脚）；h10→h9、f9–e9（F 到第 9 列上半）"]
        for i, r in enumerate(rows):
            ls.lab(d, (x0n, y0n - 0.6 * (i + 1)), r, fs_=9.5)
        f30.decap(d, 1.5, -5.6, "C3", "U3：b10→上 0 V 轨")
        f30.decap(d, 5.8, -5.6, "C4", "U4：b20→上 0 V 轨")
        f30.decap(d, 10.1, -5.6, "C5", "U5：b32→上 0 V 轨")
        ls.note(d, (-14.0, -9.4), "测点字母 C～M 与板 B 面包板图的黄色圆圈一一对应；芯片旁的小黑字是引脚号；括号里是孔位。所有 V_MID 空心圆都是板 A 送来的同一条线。")
    print("[图 38-p4-4] 板 B 原理图：C→CH→E→U3A→F→U3B/U4 ×±1→G→RF→J，CF→K(V_MID)；A0 分压 L；比较器 D10→5 脚，M→6 脚；去耦 C3–C5")
    save_schem(d, N, "38_p4_4_schem_b.png")

def p1_3():
    """示意：恒定磁场 vs 换向磁场；线圈 L/R 让磁场变圆，只用每个半周期的后一半。任意单位。"""
    T = 0.16; t = np.arange(0, 6 * T, 1e-4)
    S = 1.0
    drift = 4.0 * (1 - np.exp(-t / 0.5)) + 0.4 * np.sin(2 * np.pi * t / 0.7)     # 电极极化的慢漂移（示意）
    sq = np.where((t % T) < T / 2, 1.0, -1.0)
    tau = 0.012                                                                   # 线圈 L/R（示意）
    b = np.empty_like(t); b[0] = -1.0
    for i in range(1, t.size):
        b[i] = b[i - 1] + (sq[i] - b[i - 1]) * (1e-4 / tau)
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(8.4, 6.4), sharex=True)
    a1.plot(t * 1e3, S + drift, **fs.LS["vin"], label="电极电压 = 信号 + 极化漂移")
    a1.plot(t * 1e3, np.full_like(t, S), **fs.LS["good"], label="其中真正的流速信号")
    a1.set_title("(a) 磁场方向不变：信号和极化漂移都是「直流」，分不开", fontsize=10)
    a1.legend(fontsize=8, loc="lower right")
    a2.plot(t * 1e3, S * sq + drift, **fs.LS["vin"], label="电极电压 = ±信号 + 极化漂移")
    a2.plot(t * 1e3, drift, **fs.LS["third"], label="极化漂移（同一条）")
    pairs = []
    for k in range(6):
        m = (t >= k * T) & (t < (k + 0.5) * T); n_ = (t >= (k + 0.5) * T) & (t < (k + 1) * T)
        pairs.append(((S * sq + drift)[m].mean() - (S * sq + drift)[n_].mean()) / 2)
    a2.plot((np.arange(6) + 0.5) * T * 1e3, pairs, "o", color=fs.C["vout"], label="每个周期「正半 − 负半」÷2")
    a2.set_title("(b) 磁场来回换向：信号跟着翻号，漂移不翻号；两半相减就把漂移扣掉", fontsize=10)
    a2.legend(fontsize=8, loc="lower right", ncol=1)
    a3.plot(t * 1e3, b, **fs.LS["cur"], label="线圈电流 / 磁场（被 L/R 拖圆）")
    a3.plot(t * 1e3, sq, **fs.LS["ref"])
    for k in range(12):
        a3.axvspan((k * 0.5 + 0.25) * T * 1e3, (k + 1) * 0.5 * T * 1e3, color="0.6", alpha=0.3, lw=0)
    a3.set_title("(c) 换向那一下磁场要先「爬上来」：只用每个半周期的后一半（灰色阴影）", fontsize=10)
    a3.legend(fontsize=8, loc="lower right")
    a3.annotate("", xy=(T * 1e3, -1.45), xytext=(T / 2 * 1e3, -1.45), arrowprops=dict(arrowstyle="<->", lw=0.9))
    a3.text(T * 0.75 * 1e3, -1.75, "半周期 80 ms", ha="center", fontsize=8.5)
    a3.annotate("", xy=(T * 1e3, 1.4), xytext=(T * 0.75 * 1e3, 1.4), arrowprops=dict(arrowstyle="<->", lw=0.9))
    a3.text(T * 0.875 * 1e3, 1.55, "后一半 40 ms", ha="center", fontsize=8.5)
    a3.set_ylim(-2.0, 1.95)
    for a in (a1, a2, a3):
        a.set_yticks([]); fs.ref_h(a, 0)
    a1.set_ylabel("示意"); a2.set_ylabel("示意"); a3.set_ylabel("示意")
    a3.set_xlabel("时间 / ms")
    print(f"[图 38-p1-2] 示意：极化漂移 0→4（任意单位），信号 1；翻转相减各周期 {min(pairs):.3f}～{max(pairs):.3f}；半周期 80 ms，后一半 40 ms")
    fs.save(fig, N, "38_p1_2_reversal.png")


def p3_3():
    """两种错接：(a) Arduino D10 直接接 CD4053 的 11 脚；(b) INH（6 脚）悬空。"""
    vih9 = 0.7 * 9.0
    with drawing(fontsize=11) as d:
        ls.title(d, (0.0, 4.6), "(a) 省掉 LM393，D10 直接接 11 脚")
        d += elm.Dot(open=True).at((0.0, 2.0))
        ls.lab(d, (-0.2, 2.0), "Arduino D10\n（0 / 5 V）", ha="right", fs_=10, color=fs.C["vin"])
        d += elm.Line().at((0.0, 2.0)).to((4.0, 2.0)).color(fs.C["bad"])
        ls.lab(d, (2.0, 2.35), "× 直接一根线", ha="center", fs_=10, color=fs.C["bad"])
        for a_, b_ in (((4.0, 0.0), (7.5, 0.0)), ((7.5, 0.0), (7.5, 4.0)), ((7.5, 4.0), (4.0, 4.0)), ((4.0, 4.0), (4.0, 0.0))):
            d += elm.Line().at(a_).to(b_).color(ls.GRAY)
        ls.lab(d, (5.75, 2.6), "U4 CD4053", ha="center", fs_=10)
        ls.lab(d, (5.75, 1.6), "VDD = 9 V", ha="center", fs_=9.5)
        ls._pin(d, (4.0, 2.0), "11 A", dx=0.55, dy=0.0)
        d += elm.Line().at((5.75, 4.0)).to((5.75, 4.4)); d += elm.Vdd().at((5.75, 4.4)).label("9 V（16 脚）")
        ls.note(d, (-2.5, -0.8), "D10 高电平只有 5 V；CD4053 接 9 V 时要多高才算「高」？去 page3 的表里找。")
        x = 13.0
        ls.title(d, (x, 4.6), "(b) INH（6 脚）没接")
        for a_, b_ in (((x, 0.0), (x + 3.5, 0.0)), ((x + 3.5, 0.0), (x + 3.5, 4.0)), ((x + 3.5, 4.0), (x, 4.0)), ((x, 4.0), (x, 0.0))):
            d += elm.Line().at(a_).to(b_).color(ls.GRAY)
        ls.lab(d, (x + 1.75, 2.6), "U4 CD4053", ha="center", fs_=10)
        ls._pin(d, (x + 3.5, 1.0), "6 INH", dx=-0.75, dy=0.0)
        d += elm.Line().at((x + 3.5, 1.0)).to((x + 5.0, 1.0)).color(fs.C["bad"])
        d += elm.Dot(open=True).at((x + 5.0, 1.0))
        ls.lab(d, (x + 5.2, 1.0), "× 悬空", fs_=10, color=fs.C["bad"])
        ls._pin(d, (x + 3.5, 3.0), "7 VEE、8 VSS", dx=-1.1, dy=0.0)
        d += elm.Line().at((x + 3.5, 3.0)).to((x + 5.0, 3.0))
        d += elm.Ground().at((x + 5.0, 3.0))
        ls.note(d, (x - 1.0, -0.8), "正确：6、7、8 脚都接 0 V（j25、j26、j27）。")
    print(f"[图 38-p3-3] 错接：D10 5 V 直连（9 V 供电时 V_IH 按 0.7·VDD 估 {vih9:.1f} V）；INH 悬空")
    save_schem(d, N, "38_p3_3_miswire.png")


def p4_5():
    """参考曲线：模拟法 J−K 与数字法（串口）读数随参考相位的变化。"""
    ph = np.array([0, 45, 90, 135, 180])
    ana = np.array([sim.tail_stats(*sim.chain(phi_deg=float(p_), T=12))[0] * 1e3 for p_ in ph])
    dig_b = np.array([sim.arduino_run(phi_deg=float(p_), noise_lsb=0.5).mean() for p_ in ph])
    dig_n = np.array([sim.arduino_run(phi_deg=float(p_), noise_lsb=0.5, blank=False).mean() for p_ in ph])
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.0, 3.2))
    phc = np.linspace(0, 180, 181)
    a.plot(phc, G * E * 1e3 * (1 - phc / 90) * sim.RMETER / (sim.RMETER + sim.RF), **fs.LS["good"], label="理论 G·E·(1 − φ/90°)×表头因子")
    a.plot(ph, ana, "o", color=fs.C["vout"], label="模拟仿真 J−K")
    fs.axlabels(a, "参考相位 φ", "°", "J−K", "mV")
    a.set_title("模拟法（万用表读 J−K）", fontsize=10)
    a.legend(fontsize=8, loc="upper right"); fs.ref_h(a, 0)
    b.plot(ph, dig_b, "o-", color=fs.C["vout"], label="只采每半周期后一半")
    b.plot(ph, dig_n, "x--", color=fs.C["bad"], label="整段都采")
    b.axhline(E * 1e3, **fs.LS["ref"])
    fs.axlabels(b, "参考相位 φ", "°", "串口读数（折算到 P 点）", "mV")
    b.set_title("数字法（Arduino 串口）", fontsize=10)
    b.legend(fontsize=8, loc="lower left"); fs.ref_h(b, 0)
    for k in range(len(ph)):
        print(f"[数值] φ = {ph[k]:3d}°：J−K {ana[k]:+.2f} mV；数字 后半 {dig_b[k]:+.3f}，整段 {dig_n[k]:+.3f} mV")
    print("[图 38-p4-5] 参考曲线：模拟 J−K 与数字读数 vs 相位")
    fs.save(fig, N, "38_p4_5_expected.png")


def p4_6():
    """思考题用的两种改法（只画连接，不给结论）。"""
    tau = sim.RF * sim.CF
    t_set = tau * np.log(4.5 / 0.5e-3)
    tau_b = 10e-6 * (100e3 * 10e3 / (110e3))
    with drawing(fontsize=11) as d:
        ls.title(d, (0.0, 3.8), "(a) 把 CF 的下端从 V_MID 改接 0 V")
        d += elm.Dot(open=True).at((0.0, 2.0)); ls.probe(d, (0.0, 2.0), "G", dx=0.0, dy=0.9)
        d += elm.Resistor().at((0.0, 2.0)).to((3.5, 2.0)); ls.lab(d, (1.75, 2.55), "RF 100k", ha="center", fs_=10)
        d += elm.Dot().at((3.5, 2.0)); d += elm.Line().at((3.5, 2.0)).to((5.0, 2.0))
        d += elm.Dot(open=True).at((5.0, 2.0)); ls.probe(d, (5.0, 2.0), "J", dx=0.0, dy=0.9)
        d += elm.Capacitor().at((3.5, 2.0)).to((3.5, -0.6)); ls.lab(d, (3.9, 0.7), "CF 10µ", fs_=10)
        d += elm.Ground().at((3.5, -0.6))
        ls.lab(d, (3.9, -0.6), "0 V（改到下 0 V 轨）", fs_=9.5, color=fs.C["bad"])
        d += elm.Dot(open=True).at((6.6, 0.4)); ls.probe(d, (6.6, 0.4), "K", dx=0.0, dy=0.9)
        ls.lab(d, (6.85, 0.4), "V_MID", fs_=10, color=fs.C["third"])
        ls.note(d, (-0.5, -1.9), "万用表仍然红笔 J、黑笔 K。")
        x = 12.0
        ls.title(d, (x, 3.8), "(b) 拆掉 U3A 跟随器，E 直接接 R11 和 13 脚")
        d += elm.Dot(open=True).at((x, 2.0)); ls.lab(d, (x - 0.2, 2.0), "Vo", ha="right", fs_=10, color=fs.C["vout"])
        d += elm.Capacitor().at((x, 2.0)).to((x + 2.5, 2.0)); ls.lab(d, (x + 1.25, 2.7), "CH 10µ", ha="center", fs_=10)
        d += elm.Dot().at((x + 2.5, 2.0)); ls.probe(d, (x + 2.5, 2.0), "E", dx=0.0, dy=0.9)
        d += elm.Resistor().at((x + 2.5, 2.0)).to((x + 2.5, -0.5)); ls.lab(d, (x + 2.85, 0.75), "RH 100k", fs_=10)
        d += elm.Dot(open=True).at((x + 2.5, -0.5)); ls.lab(d, (x + 2.75, -0.5), "V_MID", fs_=10, color=fs.C["third"])
        d += elm.Line().at((x + 2.5, 2.0)).to((x + 5.0, 2.0)).color(fs.C["bad"])
        d += elm.Resistor().at((x + 5.0, 2.0)).to((x + 8.0, 2.0)); ls.lab(d, (x + 6.5, 2.55), "R11 10k → U3B 6 脚", ha="center", fs_=10)
        d += elm.Line().at((x + 5.0, 2.0)).to((x + 5.0, 0.6)).color(fs.C["bad"])
        d += elm.Dot(open=True).at((x + 5.0, 0.6)); ls.lab(d, (x + 5.25, 0.6), "U4 13 脚 AY", fs_=10)
        ls.note(d, (x - 0.5, -1.9), "U3A 的 1、2、3 脚空出来（2、3 脚接 0 V），其他不变。")
    print(f"[图 38-p4-6] 思考题改法；（答案用）τ = {tau:.2f} s，稳到 0.5 mV 需 τ·ln(4.5 V/0.5 mV) = {t_set:.1f} s；"
          f"拆跟随器后 ×−1 时 CH 看到 RH∥R11，τ = {tau_b*1e3:.1f} ms")
    save_schem(d, N, "38_p4_6_think.png")


if __name__ == "__main__":
    want = sys.argv[1:]
    for f in [k for k in list(globals()) if k.startswith("p") and k[1:2].isdigit()]:
        if not want or f in want:
            globals()[f]()
