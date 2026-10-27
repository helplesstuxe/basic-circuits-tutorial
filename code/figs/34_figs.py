"""34 开关电容滤波与跟踪滤波：全部配图。
运行（仓库根目录）：/workspace/circuits-venv/bin/python code/figs/34_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。数值函数在 code/34_sim.py，面包板小工具在 code/33_bbkit.py。
"""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import lab_schem as ls
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon


def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, "..", fn))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


sim = _load("sim34", "34_sim.py")
bbk = _load("bbkit", "33_bbkit.py")
N = "34"
C, LS = fs.C, fs.LS
F1, F2 = sim.F_CLK1, sim.F_CLK2
T63_1, T95_1 = sim.t_to(0.632, F1), sim.t_to(0.95, F1)
T63_2, T95_2 = sim.t_to(0.632, F2), sim.t_to(0.95, F2)
print(f"[数值] 时钟 {F1} Hz：63% 在 {T63_1:.3f} s，95% 在 {T95_1:.3f} s；时钟 {F2} Hz：63% 在 {T63_2:.3f} s，95% 在 {T95_2:.3f} s")
assert abs(T63_1 - 0.962) < 0.002 and abs(T63_2 - 1.916) < 0.002


def axl(ax, xl, yl):
    ax.set_xlabel(xl)
    if yl:
        ax.set_ylabel(yl)


def bp_mag(f, f0, q):
    """二阶带通幅频（33 节）：1/sqrt(1 + Q值²(f/f0 − f0/f)²)。"""
    f = np.asarray(f, float)
    return 1 / np.sqrt(1 + q ** 2 * (f / f0 - f0 / f) ** 2)


# =====================================================================
# 图 34-p1-1 痛点：固定在 50 Hz 的带通，信号频率随流量从 20 Hz 变到 200 Hz
# =====================================================================
def p1_1():
    f = np.logspace(np.log10(5), np.log10(1000), 800)
    m = bp_mag(f, 50, 5)
    fig, ax = plt.subplots(figsize=(7, 4.0))
    ax.plot(f, m, color=C["good"], ls="--", lw=1.4, label="固定带通（中心 50 Hz，Q值 = 5）")
    for fx, col in ((20, C["bad"]), (50, C["vout"]), (200, C["bad"])):
        g = bp_mag(fx, 50, 5)
        ax.plot([fx], [g], "o", color=col, ms=8)
        ax.annotate(f"{fx} Hz：剩 {g:.3f}", (fx, g), textcoords="offset points", xytext=(6, 10 if fx == 50 else 14),
                    fontsize=9.5, color=col)
        print(f"[数值] 图 34-p1-1：信号 {fx} Hz 过 50 Hz 带通后剩 {g:.3f}")
    ax.set_xscale("log"); ax.set_ylim(0, 1.15)
    ax.set_xticks([5, 10, 20, 50, 100, 200, 500, 1000]); ax.set_xticklabels(["5", "10", "20", "50", "100", "200", "500", "1k"])
    ax.legend(loc="upper right", fontsize=9)
    axl(ax, "频率 / Hz（对数刻度）", "输出 ÷ 输入")
    ax.set_title("图 34-p1-1 流量变了，信号频率跟着变，固定窗口就「接不住」", fontsize=10.5)
    assert bp_mag(200, 50, 5) < 0.1
    fs.save(fig, N, "34_p1_1_fixed_window.png")


# =====================================================================
# 图 34-p1-2 「小勺舀水」类比
# =====================================================================
def p1_2():
    fig, ax = fs.diagram(8, 3.6)
    # 左水桶（输入，水位固定）
    ax.add_patch(Rectangle((0.4, 0.4), 1.6, 2.4, fc="none", ec=C["edge"], lw=1.5))
    ax.add_patch(Rectangle((0.42, 0.42), 1.56, 1.9, fc=C["vin"], alpha=0.35, ec="none"))
    ax.text(1.2, 3.05, "大水池（输入电压）\n水位不变", ha="center", fontsize=9.5)
    # 右水桶（输出，C2）
    ax.add_patch(Rectangle((5.8, 0.4), 1.8, 2.4, fc="none", ec=C["edge"], lw=1.5))
    ax.add_patch(Rectangle((5.82, 0.42), 1.76, 0.7, fc=C["vout"], alpha=0.45, ec="none"))
    ax.text(6.7, 3.05, "大桶（C2，输出电压）\n一勺一勺慢慢涨", ha="center", fontsize=9.5)
    # 小勺
    for x, al in ((2.6, 1.0), (5.0, 0.45)):
        ax.add_patch(Rectangle((x, 1.6), 0.5, 0.35, fc=C["third"], alpha=al, ec=C["edge"]))
    ax.text(3.95, 2.25, "小勺（C1）", ha="center", fontsize=10, color=C["third"])
    fs.arrow(ax, (3.2, 1.85), (4.9, 1.85), color=C["third"])
    fs.arrow(ax, (4.9, 1.45), (3.2, 1.45), color=C["third"], dashed=True)
    ax.text(3.95, 1.0, "时钟每「嘀嗒」一次，\n小勺来回一趟", ha="center", fontsize=9)
    ax.text(3.95, 0.15, "勺越大、跑得越勤 → 水流越快 → 相当于「电阻」越小", ha="center", fontsize=9.5, color=C["edge"])
    ax.set_title("图 34-p1-2 开关电容就是「小勺舀水」", fontsize=10.5)
    fs.save(fig, N, "34_p1_2_ladle.png")
    print("[图 34-p1-2] 类比：小勺 = C1，大桶 = C2，来回一趟 = 一个时钟周期")


# =====================================================================
# 原理图小工具：单刀双掷开关（CD4053 的一路）
# =====================================================================
def _spdt(d, xa, xb, y, xm, ym, to="a", pins=None, color="black"):
    """两掷端 (xa, y)、(xb, y)，公共端 (xm, ym)。to='a' 时刀接 a 端。pins=(左脚号, 右脚号, 公共脚号)。"""
    for p in ((xa, y), (xb, y), (xm, ym)):
        d += elm.Dot(open=True).at(p)
    tgt = (xa, y) if to == "a" else (xb, y)
    oth = (xb, y) if to == "a" else (xa, y)
    d += elm.Line().at((xm, ym)).to((tgt[0] + (0.12 if to == "a" else -0.12), tgt[1] - 0.12)).color(color).linewidth(1.8)
    d += elm.Line().at((xm, ym)).to((oth[0] + (0.12 if to != "a" else -0.12), oth[1] - 0.12)).color("#999999").linewidth(1.0).linestyle("--")
    if pins:
        ls.lab(d, (xa, y + 0.35), pins[0], ha="center", fs_=9, color=ls.GRAY)
        ls.lab(d, (xb, y + 0.35), pins[1], ha="center", fs_=9, color=ls.GRAY)
        ls.lab(d, (xm + 0.25, ym - 0.1), pins[2], ha="left", fs_=9, color=ls.GRAY)


def _sc_core(d, x0=0.0, y0=0.0, holes=False, rl=False, vin_label="Vin", show_ctrl=True):
    """开关电容低通：Vin → AX(12)；公共端(14) 接 C1 到地；AY(13) → 输出节点（C2 到地）。返回关键点。"""
    xa, xb, xm, ym = x0 + 2.4, x0 + 5.4, x0 + 3.9, y0 - 1.3
    d += elm.Line().at((x0, y0)).to((xa, y0)).color(C["vin"] if holes else "black").linewidth(1.6)
    d += elm.Dot().at((x0, y0))
    ls.lab(d, (x0 - 0.15, y0 + 0.4), vin_label, ha="right", fs_=10.5)
    _spdt(d, xa, xb, y0, xm, ym, "a", pins=("AX 12 脚", "AY 13 脚", "公共端 14 脚"))
    d += elm.Capacitor().endpoints((xm, ym), (xm, ym - 2.2))
    d += elm.Ground().at((xm, ym - 2.2))
    ls.lab(d, (xm - 0.45, ym - 1.1), "C1\n10 nF", ha="right", fs_=10)
    xo = x0 + 7.4
    d += elm.Line().at((xb, y0)).to((xo, y0))
    d += elm.Dot().at((xo, y0))
    d += elm.Capacitor().endpoints((xo, y0), (xo, y0 - 3.5))
    d += elm.Ground().at((xo, y0 - 3.5))
    ls.lab(d, (xo + 0.45, y0 - 1.75), "C2\n1 µF（薄膜）", fs_=10)
    if rl:
        xr = xo + 2.2
        d += elm.Line().at((xo, y0)).to((xr, y0)).linestyle("--")
        d += elm.Resistor().endpoints((xr, y0), (xr, y0 - 3.5)).linestyle("--")
        d += elm.Ground().at((xr, y0 - 3.5))
        ls.lab(d, (xr + 0.45, y0 - 1.75), "RL 1 MΩ\n（第 7 步才插）", fs_=9.5)
    if show_ctrl:
        d += elm.Line().at((xm, y0 + 1.6)).to((xm, y0 + 0.2)).color(C["cur"]).linewidth(1.4).linestyle(":")
        ls.lab(d, (xm, y0 + 1.95), "A 11 脚 ← 时钟：低 → 接 AX，高 → 接 AY", ha="center", fs_=9.5, color=C["cur"])
    return dict(xa=xa, xb=xb, xm=xm, ym=ym, xo=xo, y0=y0)


def p1_3():
    d = drawing(fontsize=11)
    p = _sc_core(d, 0, 0, vin_label="输入", show_ctrl=False)
    ls.lab(d, (p["xo"] + 0.2, 0.45), "输出", fs_=10.5)
    # 右边：等效 RC
    x1 = p["xo"] + 4.5
    ls.lab(d, (x1 - 1.4, -1.0), "≈", ha="center", fs_=22)
    d += elm.Dot().at((x1, 0))
    d += elm.Resistor().endpoints((x1, 0), (x1 + 3.0, 0))
    ls.lab(d, (x1 + 1.5, 0.7), "R_eq = 1/(f_CLK × C1)", ha="center", fs_=10)
    d += elm.Dot().at((x1 + 3.0, 0))
    d += elm.Capacitor().endpoints((x1 + 3.0, 0), (x1 + 3.0, -3.5))
    d += elm.Ground().at((x1 + 3.0, -3.5))
    ls.lab(d, (x1 + 3.45, -1.75), "C2", fs_=10)
    ls.lab(d, (x1 - 0.15, 0.4), "输入", ha="right", fs_=10)
    ls.lab(d, (x1 + 3.2, 0.4), "输出", fs_=10)
    ls.note(d, (-0.5, -4.6), "左：开关来回拨（时钟控制），C1 一趟趟把电荷从输入搬到 C2；右：效果等于一只电阻 + C2 的 RC 低通（20 节）。")
    save_schem(d, N, "34_p1_3_schem_idea.png")
    print("[图 34-p1-3] 开关 + C1 ≈ 电阻 R_eq；与 C2 组成 RC 低通")



# =====================================================================
# 图 34-p1-4 整板框图：第一段时钟 → CD4053 控制脚；第二段 Vin → 开关 + C1 → C2 → 跟随器 → 万用表
# =====================================================================
def p1_4():
    fig, ax = fs.diagram(9.6, 3.9)
    y1, y0 = 2.65, 0.75
    b_in = fs.box(ax, 0.95, y1, "输入 Vin 4.5 V\n（两只 10 kΩ 分压）", w=1.7, h=0.85, fs=8.5)
    b_sw = fs.box(ax, 3.25, y1, "CD4053 A 组\n电子单刀双掷开关\n+ C1 10 nF（小勺）", w=2.0, h=1.0, fc=C["fill2"], fs=8.5)
    b_c2 = fs.box(ax, 5.45, y1, "C2 1 µF\n（大桶）", w=1.3, h=0.85, fc=C["fill2"], fs=8.5)
    b_f = fs.box(ax, 7.15, y1, "LM358 B 组\n电压跟随器", w=1.5, h=0.85, fs=8.5)
    b_m = fs.box(ax, 8.85, y1, "万用表\n直流 20 V 挡", w=1.3, h=0.85, fs=8.5)
    b_clk = fs.box(ax, 3.25, y0, f"LM358 A 组 方波时钟\n（24 节的振荡器，约 {F1} Hz）", w=2.9, h=0.8, fs=8.5)
    for a_, b_ in ((b_in, b_sw), (b_sw, b_c2), (b_c2, b_f), (b_f, b_m)):
        fs.arrow(ax, a_["r"], b_["l"])
    fs.arrow(ax, b_clk["t"], b_sw["b"], color=C["cur"], lw=1.6)
    ax.text(3.4, (y0 + y1) / 2 - 0.12, "控制脚 A（11 脚）\n低 → 接输入，高 → 接 C2", fontsize=8, color=C["cur"], ha="left", va="center")
    ax.add_patch(Rectangle((0.0, 1.95), 9.6, 1.45, fc="none", ec="0.6", lw=0.9, ls="--"))
    ax.add_patch(Rectangle((1.6, 0.2), 3.3, 1.15, fc="none", ec="0.6", lw=0.9, ls="--"))
    ax.text(0.05, 3.48, "第二段：开关电容低通（信号走这一排，从左到右）", fontsize=8.5, color="0.35", ha="left")
    ax.text(5.05, 0.5, "第一段：时钟\n整板只用一节 9 V 电池", fontsize=8.5, color="0.35", ha="left", va="center")
    ax.set_title("图 34-p1-4 本节实验的整板框图：两段，一片 LM358 的两组各管一段", fontsize=10.5)
    fs.save(fig, N, "34_p1_4_block.png")
    print(f"[图 34-p1-4] 框图：LM358 A 时钟 {F1} Hz → CD4053 11 脚；Vin 4.5 V → 开关 + C1 10 nF → C2 1 µF → LM358 B 跟随器 → 万用表")


# =====================================================================
# 图 34-p2-1 CD4053 引脚图（最小必要知识框）
# =====================================================================
def p2_1():
    names = {1: "BY", 2: "BX", 3: "CY", 4: "C 公共", 5: "CX", 6: "INH", 7: "VEE", 8: "VSS",
             9: "C 控制", 10: "B 控制", 11: "A 控制", 12: "AX", 13: "AY", 14: "A 公共", 15: "B 公共", 16: "VDD"}
    use = {6: "接 GND", 7: "接 GND", 8: "接 GND", 9: "接 GND", 10: "接 GND", 11: "← 时钟",
           12: "← 输入", 13: "→ C2", 14: "→ C1", 16: "接 +9 V"}
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    ax.set_xlim(-4.2, 8.2); ax.set_ylim(-0.6, 9.4); ax.axis("off"); ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), 4, 8.4, fc="#2b2b2b", ec="k"))
    ax.add_patch(Circle((2, 8.4), 0.35, fc="white", ec="none"))
    ax.text(2, 4.2, "CD4053", color="w", ha="center", va="center", fontsize=12, rotation=90)
    for i in range(8):
        y = 7.7 - i
        pl, pr = i + 1, 16 - i
        for p, x, ha in ((pl, -0.35, "right"), (pr, 4.35, "left")):
            ax.add_patch(Rectangle((x - 0.25 if ha == "right" else x - 0.1, y - 0.15), 0.35, 0.3, fc="#bbbbbb", ec="0.3"))
            col = C["bad"] if p in (7, 16) else ("black" if p not in use else C["edge"])
            ax.text(0.25 if ha == "right" else 3.75, y, str(p), color="w", ha="left" if ha == "right" else "right",
                    va="center", fontsize=9)
            ax.text(x - 0.35 if ha == "right" else x + 0.35, y, names[p], ha=ha, va="center", fontsize=9.5,
                    color=col, fontweight="bold" if p in (7, 16) else None)
            if p in use:
                ax.text(-2.2 if ha == "right" else 6.2, y, use[p], ha=ha, va="center", fontsize=9,
                        color=C["cur"] if p == 11 else ("#333333"))
    ax.text(2, 9.0, "缺口朝上；左边从上往下 1–8 脚，右边从下往上 9–16 脚", ha="center", fontsize=9)
    ax.text(2, -0.4, "红字：VEE（7 脚）、VDD（16 脚）。每条信号都必须在 VEE 和 VDD 之间（本节 0～9 V）", ha="center",
            fontsize=9, color=C["bad"])
    ax.set_title("图 34-p2-1 CD4053 引脚图（右栏是本节实验的接法）", fontsize=10.5)
    fs.save(fig, N, "34_p2_1_cd4053_pins.png")
    print("[图 34-p2-1] CD4053：16 VDD、8 VSS、7 VEE、6 INH、11/10/9 控制 A/B/C、14 A 公共、12 AX、13 AY")


def p2_2():
    d = drawing(fontsize=11)
    p = _sc_core(d, 0, 0, vin_label="Vin（4.5 V）")
    xo = p["xo"]
    d += elm.Line().at((xo, 0)).to((xo + 1.2, 0))
    op = elm.Opamp(leads=True).right().anchor("in2").at((xo + 1.2, 0))
    d += op
    a = op.absanchors
    ytop = a["in1"][1] + 0.9
    for p_, q_ in ((a["in1"], (a["in1"][0] - 0.4, a["in1"][1])), ((a["in1"][0] - 0.4, a["in1"][1]), (a["in1"][0] - 0.4, ytop)),
                   ((a["in1"][0] - 0.4, ytop), (a["out"][0] + 0.4, ytop)), ((a["out"][0] + 0.4, ytop), (a["out"][0] + 0.4, a["out"][1])),
                   ((a["out"][0] + 0.4, a["out"][1]), a["out"])):
        d += elm.Line().at(p_).to(q_)
    ls._pin(d, a["in2"], "5", dx=-0.2, dy=0.25)
    ls._pin(d, a["in1"], "6", dx=-0.2, dy=-0.25)
    ls._pin(d, a["out"], "7", dx=0.15, dy=0.25)
    xv = a["out"][0] + 1.6
    d += elm.Line().at(a["out"]).to((xv, a["out"][1]))
    d += elm.Dot(open=True).at((xv, a["out"][1]))
    ls.lab(d, (xv + 0.2, a["out"][1]), "Vout（接万用表）", fs_=10)
    ls.lab(d, (a["in2"][0] + 0.6, -1.5), "LM358 B 组\n跟随器", fs_=9.5, color=ls.GRAY)
    ls.lab(d, (xo + 0.2, -0.45), "输出节点", fs_=9.5)
    ls.note(d, (-0.5, -5.0), "CD4053：16 脚 +9 V；7、8、6 脚接 GND；不用的 B、C 两路控制脚 10、9 接 GND。跟随器让万用表不从 C2 上取电流。")
    save_schem(d, N, "34_p2_2_schem_sc.png")
    print("[图 34-p2-2] SC 低通：Vin→AX(12)，公共端(14)→C1 10 nF→GND，AY(13)→C2 1 µF→GND→LM358 B 跟随器")


# =====================================================================
# 图 34-p2-3 两相时序图（为了看清台阶，这张图用 C2 = 10 × C1）
# =====================================================================
def p2_3():
    f = 100.0
    ratio = 10
    T = 1 / f
    ncyc = 6
    n = 2000
    t = np.linspace(0, ncyc * T, ncyc * n, endpoint=False)
    ph = (t % T) >= T / 2           # 后半周 = 高 = 接 AY
    vin = 4.5
    vc1 = np.zeros_like(t); vo = np.zeros_like(t)
    v2 = 0.0
    steps = []
    for k in range(ncyc):
        i0, i1, i2 = k * n, k * n + n // 2, (k + 1) * n
        vc1[i0:i1] = vin
        vo[i0:i1] = v2
        v2 = v2 + (vin - v2) / (1 + ratio)
        steps.append(v2)
        vc1[i1:i2] = v2
        vo[i1:i2] = v2
    print("[数值] 图 34-p2-3（C2 = 10·C1）：每拍后输出 " + "、".join(f"{x:.2f}" for x in steps) + " V")
    fig, axs = plt.subplots(3, 1, figsize=(7, 5.6), sharex=True)
    ms = t * 1e3
    axs[0].plot(ms, np.where(ph, 7.8, 0.6), color=C["cur"], lw=1.6)
    axs[0].set_yticks([0.6, 7.8]); axs[0].set_yticklabels(["低\n接 AX", "高\n接 AY"])
    axs[0].set_title("图 34-p2-3 上：时钟（A 11 脚）", fontsize=10)
    for k in range(ncyc):
        axs[0].text((k + 0.25) * T * 1e3, 4.2, "充", ha="center", fontsize=9, color=C["vin"])
        axs[0].text((k + 0.75) * T * 1e3, 4.2, "倒", ha="center", fontsize=9, color=C["vout"])
    axs[1].plot(ms, vc1, color=C["third"], lw=1.6, ls="-.")
    axs[1].set_ylabel("C1 电压 / V"); axs[1].set_ylim(0, 5)
    axs[1].set_title("中：C1 先充到 4.5 V（充），再和 C2 分电荷（倒）", fontsize=10)
    axs[2].plot(ms, vo, color=C["vout"], lw=1.8)
    for k, x in enumerate(steps):
        axs[2].text((k + 0.98) * T * 1e3, x + 0.12, f"{x:.2f}", fontsize=8.5, ha="right")
    axs[2].set_ylabel("输出 / V"); axs[2].set_ylim(0, 3.2)
    axs[2].set_title("下：输出一台阶一台阶往上走（为看清楚，这里 C2 只取 C1 的 10 倍）", fontsize=10)
    axs[2].set_xlabel("时间 / ms")
    fs.save(fig, N, "34_p2_3_timing.png")


# =====================================================================
# 图 34-p2-4 阶跃响应：104 Hz / 52 Hz 时钟，与 RC 公式对比
# =====================================================================
def p2_4():
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for f, col, name in ((F1, C["vout"], "时钟 104 Hz"), (F2, C["third"], "时钟 52 Hz")):
        nc = int(8 * f)
        v = sim.step_discrete(f, nc)
        tt = np.arange(nc + 1) / f
        ax.step(tt, v, where="post", color=col, lw=1.6, label=f"{name}（一拍一拍算）")
        tau = sim.tau_rc(f)
        ax.plot(tt, sim.VIN * (1 - np.exp(-tt / tau)), color=C["good"], ls="--", lw=1.0)
        t63, t95 = sim.t_to(0.632, f), sim.t_to(0.95, f)
        ax.plot([t63], [0.632 * sim.VIN], "o", color=col)
        ax.plot([t95], [0.95 * sim.VIN], "s", color=col)
        ax.annotate(f"63%：{t63:.2f} s", (t63, 0.632 * sim.VIN), textcoords="data",
                    xytext=(0.12, 3.35) if f == F1 else (t63 + 0.1, 0.632 * sim.VIN - 0.32), fontsize=9, color=col)
        ax.annotate(f"95%：{t95:.2f} s", (t95, 0.95 * sim.VIN), textcoords="offset points", xytext=(6, -16), fontsize=9, color=col)
    ax.plot([], [], color=C["good"], ls="--", lw=1.0, label="RC 公式（R = R_eq）")
    ax.axhline(0.632 * sim.VIN, **LS["ref"]); ax.axhline(0.95 * sim.VIN, **LS["ref"])
    ax.text(7.9, 0.632 * sim.VIN - 0.2, f"{0.632*sim.VIN:.2f} V", ha="right", fontsize=8.5, color="0.4")
    ax.text(7.9, 0.95 * sim.VIN - 0.2, f"{0.95*sim.VIN:.2f} V", ha="right", fontsize=8.5, color="0.4")
    ax.set_xlim(0, 8); ax.set_ylim(0, 4.9)
    ax.legend(loc="lower right", fontsize=9)
    axl(ax, "时间 / s", "输出 / V")
    ax.set_title("图 34-p2-4 输入从 0 跳到 4.5 V：时钟减半，时间加倍", fontsize=10.5)
    fs.save(fig, N, "34_p2_4_step.png")
    print(f"[图 34-p2-4] 104 Hz：τ(RC) = {sim.tau_rc(F1):.3f} s；52 Hz：τ(RC) = {sim.tau_rc(F2):.3f} s")


# =====================================================================
# 时钟原理图（24 节弛张振荡器，9 V）
# =====================================================================
def _clock(d, x0=0.0, y0=0.0, holes=False, rt="Rt 68 kΩ"):
    """LM358 A 组弛张振荡器。返回输出节点坐标。"""
    opa = elm.Opamp(leads=True).right().flip().anchor("in2").at((x0, y0))
    d += opa
    a = opa.absanchors
    ls._pin(d, a["in2"], "3", dx=-0.2, dy=0.25)
    ls._pin(d, a["in1"], "2", dx=-0.2, dy=-0.25)
    ls._pin(d, a["out"], "1", dx=0.15, dy=0.25)
    ls.lab(d, (a["in2"][0] + 0.7, a["out"][1] + 0.0), "LM358\nA 组", fs_=9)
    yo = a["out"][1]
    xo = a["out"][0] + 1.6
    d += elm.Line().at(a["out"]).to((xo, yo)).color(C["out"] if False else (C["vout"] if holes else "black")).linewidth(1.8 if holes else 1.5)
    d += elm.Dot().at((xo, yo))
    # 正反馈 Rc：输出 → 同相端
    x16, xa_ = x0 - 1.6, x0 - 3.2
    yrc = y0 + 2.6
    d += elm.Line().at(a["in2"]).to((xa_, y0))
    d += elm.Dot().at((x16, y0)); d += elm.Dot().at((xa_, y0))
    d += elm.Line().at((xo, yo)).to((xo, yrc))
    d += elm.Resistor().endpoints((xo, yrc), (x16, yrc))
    ls.lab(d, ((xo + x16) / 2, yrc + 0.6), "Rc 10 kΩ" + ("（i11–i16）" if holes else ""), ha="center", fs_=9.5)
    d += elm.Line().at((x16, yrc)).to((x16, y0))
    d += elm.Resistor().endpoints((xa_, y0), (xa_, y0 + 2.2))
    d += elm.Vdd().at((xa_, y0 + 2.2)).label("+9 V")
    ls.lab(d, (xa_ - 0.45, y0 + 1.1), "Ra 10 kΩ" + ("\nh16–h20\nj20→+9 V" if holes else ""), ha="right", fs_=9)
    d += elm.Resistor().endpoints((xa_, y0), (xa_, y0 - 2.4))
    d += elm.Ground().at((xa_, y0 - 2.4))
    ls.lab(d, (xa_ - 0.45, y0 - 1.2), "Rb 10 kΩ" + ("\ng16→g22\nh22–h26\nj26→GND" if holes else ""), ha="right", fs_=9)
    # 定时 Rt、Ct：输出 → 反相端
    x15, yk = x0 - 0.9, y0 - 3.6
    d += elm.Line().at(a["in1"]).to((x15, a["in1"][1]))
    d += elm.Line().at((x15, a["in1"][1])).to((x15, yk))
    d += elm.Dot().at((x15, yk))
    d += elm.Line().at((xo, yo)).to((xo, yk))
    d += elm.Resistor().endpoints((xo, yk), (x15, yk))
    ls.lab(d, ((xo + x15) / 2, yk + 0.6), rt + ("（h11–h15）" if holes else ""), ha="center", fs_=9.5)
    d += elm.Capacitor().endpoints((x15, yk), (x15, yk - 2.2))
    d += elm.Ground().at((x15, yk - 2.2))
    ls.lab(d, (x15 - 0.45, yk - 1.1), "Ct 100 nF" + ("\nj15→GND" if holes else ""), ha="right", fs_=9)
    if holes:
        ls.colnote(d, (xo - 0.8, yo + 0.75), "g14→g11", "top", ofst=0.0)
        ls.colnote(d, (x15 + 0.15, a["in1"][1] - 0.6), "第 15 列", "right", ofst=0.0)
        ls.colnote(d, (x16 + 0.15, y0 + 0.9), "第 16 列", "right", ofst=0.0)
    return dict(out=(xo, yo), cap=(x15, yk), inp=(x16, y0), op=opa)


def p2_5():
    d = drawing(fontsize=11)
    p = _clock(d)
    ls.lab(d, (p["out"][0] + 0.3, p["out"][1] + 0.0), "时钟输出 → CD4053 的 A（11 脚）", fs_=10, color=C["cur"])
    T, vh, vl, th = sim.relax_T(sim.RT1, sim.CT)
    ls.note(d, (-6.5, -7.4), f"门限 {vh:.2f} V / {vl:.2f} V；周期约 {T/(sim.RT1*sim.CT):.2f} × Rt × Ct；Rt 换成两只 68 kΩ 串联（136 kΩ），频率减半。")
    ls.note(d, (-6.5, -8.1), "LM358：8 脚 +9 V，4 脚 GND（与跟随器 B 组共用一片）。")
    save_schem(d, N, "34_p2_5_schem_clock.png")
    print(f"[图 34-p2-5] 时钟：Rt 68 kΩ、Ct 100 nF，门限 {vh:.3f}/{vl:.3f} V，脚本 f = {1/T:.1f} Hz（SPICE {F1} Hz）")


# =====================================================================
# 图 34-p2-6 混叠：95 Hz 正弦用 100 Hz 采样，看起来像 5 Hz
# =====================================================================
def p2_6():
    fsig, fsmp = 95.0, 100.0
    t = np.linspace(0, 0.2, 8000)
    ts = np.arange(0, 0.2 + 1e-9, 1 / fsmp)
    fa = sim.alias(fsig, fsmp)
    print(f"[数值] 图 34-p2-6：{fsig:.0f} Hz 用 {fsmp:.0f} Hz 采样 → 看起来像 {fa:.0f} Hz")
    assert fa == 5
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot(t * 1e3, np.sin(2 * np.pi * fsig * t), color=C["vin"], lw=0.9, label=f"真实信号 {fsig:.0f} Hz")
    ax.plot(ts * 1e3, np.sin(2 * np.pi * fsig * ts), "o", color=C["bad"], ms=6, label=f"每秒 {fsmp:.0f} 次「看一眼」")
    ax.plot(t * 1e3, np.sin(2 * np.pi * fsig * 0) * 0 + np.cos(2 * np.pi * fa * t - np.pi / 2) * -1, color=C["vout"], lw=1.8,
            ls="--", label=f"只看这些点，以为是 {fa:.0f} Hz")
    ax.set_ylim(-1.5, 1.8)
    ax.legend(loc="upper right", fontsize=9, ncol=3)
    axl(ax, "时间 / ms", "电压（相对）")
    ax.set_title("图 34-p2-6 采样太慢：快信号「冒充」慢信号（混叠）", fontsize=10.5)
    fs.save(fig, N, "34_p2_6_alias.png")


# =====================================================================
# 图 34-p3-1 台阶大小 vs C2/C1
# =====================================================================
def p3_1():
    """三种 C2/C1：横轴是拍数（104.4 Hz 时钟下每拍 9.58 ms），左图全量程，右图把纵轴放大到 0–0.25 V。"""
    nb = 25
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.6, 3.9))
    cols = {10: C["third"], 100: C["vout"], 1000: C["vin"]}
    for ratio in (10, 100, 1000):
        v = sim.step_discrete(F1, nb, c1=1.0, c2=float(ratio))
        k = np.arange(nb + 1)
        tau = sim.tau_rc(F1, sim.C1, sim.C1 * ratio)
        lab = f"C2/C1 = {ratio}：第一步 {v[1]*1e3:.1f} mV，τ = {tau:.3g} s"
        for ax in (ax1, ax2):
            ax.step(k, v, where="post", color=cols[ratio], lw=1.5, label=lab if ax is ax1 else None)
        print(f"[数值] 图 34-p3-1：C2/C1 = {ratio}，第一步 {v[1]*1e3:.1f} mV，63% 在 {sim.cycles_to(0.632, 1, ratio):.1f} 拍，"
              f"104.4 Hz 时钟、C1 = 10 nF 时 τ = {tau:.4f} s")
        assert abs(v[1] - sim.VIN / (ratio + 1)) < 1e-9
    ax1.set_ylim(0, 4.8); ax2.set_ylim(0, 0.25)
    ax1.legend(loc="center right", bbox_to_anchor=(1.0, 0.42), fontsize=8)
    for ax in (ax1, ax2):
        ax.set_xlim(0, nb)
        axl(ax, f"拍数（每拍 1/{F1} s ≈ {1e3/F1:.2f} ms）", "输出 / V" if ax is ax1 else None)
    ax1.set_title("全量程：比值 10 很快到顶", fontsize=9.5)
    ax2.set_title("纵轴放大到 0–0.25 V：100、1000 的台阶", fontsize=9.5)
    fig.suptitle("图 34-p3-1 输入 4.5 V，三种 C2/C1 的前 25 拍：比值越大，台阶越细、上升越慢", fontsize=10.5)
    fs.save(fig, N, "34_p3_1_staircase.png")


# =====================================================================
# 图 34-p3-2 τ vs f_CLK（公式 + 离散 + SPICE 两点）
# =====================================================================
def p3_2():
    f = np.logspace(1, 3, 200)
    fig, ax = plt.subplots(figsize=(7, 4.0))
    ax.plot(f, sim.tau_rc(f), color=C["good"], ls="--", lw=1.3, label="τ = C2/(f_CLK·C1)")
    fd = np.array([10, 20, 52.44, 104.4, 200, 500, 1000])
    ax.plot(fd, sim.t_to(0.632, fd), "o", color=C["vout"], ms=6, label="一拍一拍算的 63% 时间")
    sp = [(104.4, 0.9619), (52.44, 1.9046)]   # spice/34 results.json
    ax.plot([x for x, _ in sp], [y for _, y in sp], "x", color=C["bad"], ms=10, mew=2, label="SPICE（实验电路整体）")
    for x, y in sp:
        ax.annotate(f"{x:.0f} Hz：{y:.2f} s", (x, y), textcoords="offset points", xytext=(8, 6), fontsize=9)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.legend(loc="upper right", fontsize=9)
    axl(ax, "时钟频率 / Hz（对数刻度）", "时间常数 / s（对数刻度）")
    ax.set_title("图 34-p3-2 时钟每快 10 倍，τ 就缩小到 1/10", fontsize=10.5)
    fs.save(fig, N, "34_p3_2_tau_vs_fclk.png")
    for x in (10, 100, 1000):
        print(f"[数值] 图 34-p3-2：f_CLK = {x} Hz → τ = {sim.tau_rc(x):.3f} s")



# =====================================================================
# 图 34-p3-3 真实开关：分压内阻 5 kΩ、导通电阻 R_on 串在 C1 的路上；负载 RL（或万用表 10 MΩ）并在 C2 上
# =====================================================================
def p3_3():
    rsrc = 10e3 * 10e3 / 20e3
    t_on = (sim.RON_TYP * sim.C1, sim.RON_MAX * sim.C1)
    t_src = rsrc * sim.C1
    half = 0.5 / F1
    print(f"[数值] 图 34-p3-3：R_on×C1 = {t_on[0]*1e6:.1f}～{t_on[1]*1e6:.1f} µs；5 kΩ×C1 = {t_src*1e6:.0f} µs；"
          f"半周期 {half*1e3:.2f} ms，是 5 kΩ×C1 的 {half/t_src:.0f} 倍")
    assert abs(t_src - 50e-6) < 1e-9 and abs(half * 1e3 - 4.79) < 0.005 and round(half / t_src) == 96
    d = drawing(fontsize=11)
    d += elm.Dot().at((0, 0))
    ls.lab(d, (-0.15, 0.4), "Vin 4.5 V", ha="right", fs_=10.5)
    d += elm.Resistor().endpoints((0, 0), (2.6, 0))
    ls.lab(d, (1.3, 0.65), "分压内阻 5 kΩ\n（R1∥R2）", ha="center", fs_=9.5)
    xa, xb, xm, ym = 3.4, 6.4, 4.9, -1.3
    d += elm.Line().at((2.6, 0)).to((xa, 0))
    _spdt(d, xa, xb, 0, xm, ym, "a", pins=("AX 12 脚", "AY 13 脚", "公共端 14 脚"))
    d += elm.Resistor().endpoints((xm, ym), (xm, ym - 2.2)).color(C["bad"])
    ls.lab(d, (xm + 0.45, ym - 1.1), "R_on 180～400 Ω\n（开关内部，约 10 V 供电时）", fs_=9.5, color=C["bad"])
    d += elm.Capacitor().endpoints((xm, ym - 2.2), (xm, ym - 4.2))
    d += elm.Ground().at((xm, ym - 4.2))
    ls.lab(d, (xm - 0.45, ym - 3.2), "C1\n10 nF", ha="right", fs_=10)
    xo = 8.6
    d += elm.Line().at((xb, 0)).to((xo, 0))
    d += elm.Dot().at((xo, 0))
    d += elm.Capacitor().endpoints((xo, 0), (xo, -3.5))
    d += elm.Ground().at((xo, -3.5))
    ls.lab(d, (xo - 0.45, -1.75), "C2\n1 µF", ha="right", fs_=10)
    xr = xo + 2.4
    d += elm.Line().at((xo, 0)).to((xr, 0)).linestyle("--")
    d += elm.Resistor().endpoints((xr, 0), (xr, -3.5)).linestyle("--")
    d += elm.Ground().at((xr, -3.5))
    ls.lab(d, (xr + 0.45, -1.75), "RL 1 MΩ\n或万用表 10 MΩ\n（虚线：负载）", fs_=9.5)
    d += elm.Line().at((xr, 0)).to((xr + 1.2, 0))
    ls.lab(d, (xr + 1.3, 0), "→ 跟随器", fs_=9.5)
    ls.note(d, (-0.5, -6.3), f"C1 每次充电要经过 5 kΩ 和 R_on：5 kΩ×C1 = {t_src*1e6:.0f} µs，R_on×C1 = {t_on[0]*1e6:.1f}～{t_on[1]*1e6:.1f} µs，"
                              f"都远小于半个时钟周期 {half*1e3:.2f} ms。")
    ls.note(d, (-0.5, -7.0), "RL 并在 C2 上，和 R_eq（约 958 kΩ）分压；万用表直接接 C2 也一样，所以要读跟随器的输出。")
    save_schem(d, N, "34_p3_3_schem_ron_load.png")
    print("[图 34-p3-3] Vin → 5 kΩ → AX；公共端 → R_on → C1 → GND；AY → C2；RL/10 MΩ 并在 C2 上")


# =====================================================================
# 图 34-p3-4 抗混叠 RC → SC → 平滑 RC
# =====================================================================
def p3_4():
    RF, CF, RS, CS = 1.5e3, 10e-6, 10e3, 10e-6
    fcf, fcs = 1 / (2 * np.pi * RF * CF), 1 / (2 * np.pi * RS * CS)
    d = drawing(fontsize=11)
    d += elm.Dot(open=True).at((0, 0))
    ls.lab(d, (-0.2, 0.4), "信号输入", ha="right", fs_=10)
    d += elm.Resistor().endpoints((0, 0), (3, 0)).label("Rf 1.5 kΩ", "top")
    d += elm.Dot().at((3, 0))
    d += elm.Capacitor().endpoints((3, 0), (3, -2.4))
    ls.lab(d, (3.45, -1.2), "Cf 10 µF", fs_=10)
    d += elm.Ground().at((3, -2.4))
    ls.lab(d, (1.6, -3.4), f"① 前置抗混叠 RC\n截止 {fcf:.1f} Hz ≈ f_CLK/10\nCf 是 C1 的 {CF/sim.C1:.0f} 倍", ha="center", fs_=9.5, color=C["vin"])
    d += elm.Line().at((3, 0)).to((4, 0))
    p = _sc_core(d, 4.0, 0.0, vin_label="", show_ctrl=False)
    ls.lab(d, (p["xm"] + 1.6, -4.4), "② 开关电容低通（C1、C2）", ha="center", fs_=9.5, color=C["vout"])
    xo = p["xo"]
    xf = xo + 1.2
    d += elm.Line().at((xo, 0)).to((xf, 0))
    a = _follower(d, xf, 0.0)
    xo2 = a["out"][0] + 0.6
    d += elm.Line().at(a["out"]).to((xo2, a["out"][1]))
    yo = a["out"][1]
    d += elm.Resistor().endpoints((xo2, yo), (xo2 + 3, yo)).label("Rs 10 kΩ", "top")
    d += elm.Dot().at((xo2 + 3, yo))
    d += elm.Capacitor().endpoints((xo2 + 3, yo), (xo2 + 3, yo - 2.4))
    ls.lab(d, (xo2 + 3.45, yo - 1.2), "Cs 10 µF", fs_=10)
    d += elm.Ground().at((xo2 + 3, yo - 2.4))
    d += elm.Line().at((xo2 + 3, yo)).to((xo2 + 4, yo))
    d += elm.Dot(open=True).at((xo2 + 4, yo))
    ls.lab(d, (xo2 + 4.2, yo), "输出", fs_=10)
    ls.lab(d, (xo2 + 1.8, yo - 3.4), f"③ 后置平滑 RC（接在跟随器之后）\n截止 {fcs:.2f} Hz，磨平台阶", ha="center", fs_=9.5, color=C["third"])
    g = sim.rc_lp(sim.F_CLK1 - 5, fcf)
    assert abs(g - 0.106) < 0.001 and CF / sim.C1 >= 1000
    ls.note(d, (-0.5, -5.4), f"例：f_CLK = {sim.F_CLK1} Hz 时，离时钟 5 Hz 的干扰（{sim.F_CLK1-5:.1f} Hz）经 ① 剩 {g:.3f}；C2 不直接带负载，Rs、Cs 由跟随器来推。")
    save_schem(d, N, "34_p3_4_schem_antialias.png")
    print(f"[图 34-p3-4] 抗混叠：Rf 1.5 kΩ + Cf 10 µF 截止 {fcf:.2f} Hz，{sim.F_CLK1-5:.1f} Hz → {g:.3f}；平滑 {fcs:.2f} Hz")


# =====================================================================
# 图 34-p3-5 跟踪滤波预告（框图）
# =====================================================================
def p3_5():
    fig, ax = fs.diagram(8.4, 3.2)
    b1 = fs.box(ax, 1.0, 2.1, "传感器\n（涡街）", w=1.5, h=0.9)
    b2 = fs.box(ax, 3.7, 2.1, "开关电容带通\n（如 MF10，100:1）", w=2.2, h=0.9, fc=C["fill2"])
    b3 = fs.box(ax, 6.5, 2.1, "整形、计数\n→ 流量", w=1.8, h=0.9)
    b4 = fs.box(ax, 3.7, 0.5, "在输入端测频率 f（36 节）\n幅度够大才更新：时钟 = 100 × f", w=3.6, h=0.75)
    fs.arrow(ax, b1["r"], b2["l"]); fs.arrow(ax, b2["r"], b3["l"])
    fs.arrow(ax, (b1["b"][0], b1["b"][1]), (b4["l"][0], b4["l"][1]), color=C["cur"])
    fs.arrow(ax, (b4["t"][0], b4["t"][1]), (b2["b"][0], b2["b"][1]), color=C["cur"])
    ax.text(5.7, 0.55, "测频接在滤波器前面：\n时钟还没对准时，\n滤波器输出几乎没有信号", fontsize=8.5, color=C["cur"], ha="left")
    ax.text(1.0, 3.0, "信号 20 Hz → 时钟 2 kHz；200 Hz → 20 kHz", fontsize=8.5, ha="left")
    ax.set_title("图 34-p3-5 预告：让窗口跟着信号走（跟踪滤波）", fontsize=10.5)
    fs.save(fig, N, "34_p3_5_tracking.png")
    print("[图 34-p3-5] 跟踪滤波框图：输入端测 f → 时钟 100f → SC 带通中心 = f")


# =====================================================================
# 第 4 页：两个阶段的面包板图 + 一一对应的原理图
# LM358 在第 14–17 列（照抄 24 节的布局）；CD4053 在第 28–35 列（16 脚：1 脚 f28 … 8 脚 f35，9 脚 e35 … 16 脚 e28）
# =====================================================================
LM_NAMES = {1: "OUT", 2: "IN−", 3: "IN+", 4: "GND", 5: "IN+", 6: "IN−", 7: "OUT", 8: "V+"}
CD_NAMES = {1: "BY", 2: "BX", 3: "CY", 4: "Ccom", 5: "CX", 6: "INH", 7: "VEE", 8: "VSS",
            9: "C", 10: "B", 11: "A", 12: "AX", 13: "AY", 14: "Acom", 15: "Bcom", 16: "VDD"}


def _bb_clock(bb):
    bb.chip(14, "LM358", names=LM_NAMES)
    bb.wire("a14", "T+14", "pos")                 # 8 脚 → +9 V
    bb.wire("j17", "B-17", "gnd")                 # 4 脚 → GND
    bb.wire("g14", "g11", "out")                  # 1 脚（时钟输出）→ 第 11 列
    bb.part("h11", "h15", "Rt 68 kΩ", "R", lab_side=1, fs_=7.5)
    bb.part("j15", "B-15", "", "C", lab_side="l", fs_=7.5)
    bb.note(14.6, -5.8, "Ct 100 nF（j15）→", fontsize=7, ha="right", va="center")
    bb.part("b14", "T-12", "", "C")               # Cd 100 nF：LM358 8 脚就近旁路到 GND
    bb.note(12.2, 5.0, "Cd 100 nF", fontsize=7, ha="right", va="center")
    bb.part("i11", "i16", "Rc 10 kΩ", "R", lab_side="r", fs_=7.5)
    bb.part("h16", "h20", "Ra 10 kΩ", "R", lab_side=1, fs_=7.5)
    bb.wire("j20", "B+20", "pos")
    bb.wire("g16", "g22", "fb")
    bb.part("h22", "h26", "Rb 10 kΩ", "R", lab_side=1, fs_=7.5)
    bb.wire("j26", "B-26", "gnd")
    bb.wire("c15", "c16", "fb")                   # 7、6 脚短接：B 组接成跟随器


def _bb_battery(bb, ncol):
    bb.module(-3.2, 9.4, 3.6, 1.4, "9 V 电池")
    bb.wire((0.4, 10.4), "T+1", "pos", via=[(1, 10.4)])
    bb.wire((0.4, 9.7), "T-2", "gnd", via=[(2, 9.7)])
    bb.wire(f"T+{ncol}", f"B+{ncol}", "pos", via=[(ncol + 0.5, 8.6), (ncol + 0.5, -7.6)])
    bb.wire(f"T-{ncol-1}", f"B-{ncol-1}", "gnd", via=[(ncol - 0.5, 7.7), (ncol - 0.5, -6.7)])


def p4_1():
    nc = 29
    bb = bbk.Breadboard(nc, "图 34-p4-1 第一阶段：时钟（24 节的弛张振荡器，9 V）", size=(9.6, 6.6),
                        rails=("+9 V", "GND", "GND", "+9 V"))
    _bb_clock(bb)
    bb.wire("a17", "T-17", "gnd")                 # 第一阶段：5 脚先接地，B 组闲着
    _bb_battery(bb, nc)
    bb.probe("f11", "①", dx=-0.9, dy=0.0)
    bb.probe("b15", "②", dx=0.0, dy=0.9)
    bb.note(0.5, -8.9, "① 第 11 列 = 时钟输出（直流挡读平均值）；② 第 15 列 = B 组输出（此时应接近 0 V）；黑表笔插 GND 轨", ha="left")
    bb.note(0.5, -9.7, "LM358 1–4 脚在 f 排、8–5 脚在 e 排（第 14–17 列）；Cd 100 nF：b14 → 上方 GND 轨（8 脚旁路）。第 6 步把 Rt 换成两只串联，见图 34-p4-6", ha="left")
    bb.legend(y=-0.02)
    bb.save(N, "34_p4_1_breadboard_clock.png")
    print("[图 34-p4-1] 第一阶段：LM358 第 14–17 列；a14→+9 V，j17→GND，g14→g11，Rt h11–h15，Ct j15→GND，Rc i11–i16，"
          "Ra h16–h20，j20→+9 V，g16–g22，Rb h22–h26，j26→GND；c15–c16，a17→GND")


def _follower(d, xin, yin, holes=False, in_note=None):
    op = elm.Opamp(leads=True).right().anchor("in2").at((xin, yin))
    d += op
    a = op.absanchors
    ytop = a["in1"][1] + 0.9
    pts = [a["in1"], (a["in1"][0] - 0.4, a["in1"][1]), (a["in1"][0] - 0.4, ytop), (a["out"][0] + 0.4, ytop),
           (a["out"][0] + 0.4, a["out"][1]), a["out"]]
    for p_, q_ in zip(pts[:-1], pts[1:]):
        d += elm.Line().at(p_).to(q_)
    ls._pin(d, a["in2"], "5", dx=-0.2, dy=0.25)
    ls._pin(d, a["in1"], "6", dx=-0.2, dy=-0.25)
    ls._pin(d, a["out"], "7", dx=0.15, dy=0.25)
    ls.lab(d, (a["in2"][0] + 0.9, a["in2"][1] - 1.5), "LM358 B 组", fs_=9, color=ls.GRAY)
    if holes:
        ls.colnote(d, (a["out"][0] + 0.5, ytop + 0.15), "c15–c16", "top", ofst=0.0)
    return a


def p4_2():
    d = drawing(fontsize=10.5)
    ls.title(d, (-1.0, 3.6), "时钟（LM358 A 组，第 11–26 列）")
    p = _clock(d, holes=True)
    ls.probe(d, p["out"], "①", dx=0.8, dy=0.6)
    xf, yf = p["out"][0] + 4.0, -4.0
    ls.title(d, (xf + 1.5, -1.6), "B 组先闲着")
    d += elm.Line().at((xf - 0.8, yf)).to((xf, yf))
    d += elm.Ground().at((xf - 0.8, yf))
    ls.colnote(d, (xf - 0.9, yf + 0.3), "a17→GND", "left", ofst=0.0)
    a = _follower(d, xf, yf, holes=True)
    ls.probe(d, a["out"], "②", dx=0.8, dy=0.0)
    ls.note(d, (-6.5, -8.2), "LM358：8 脚 a14→+9 V，Cd 100 nF b14→GND（旁路），4 脚 j17→GND（两组共用）。①读平均值，②应接近 0 V。孔位见灰色小字。")
    save_schem(d, N, "34_p4_2_schem_lab_clock.png")
    print("[图 34-p4-2] 第一阶段原理图，与图 34-p4-1 一一对应")


def p4_3():
    nc = 44
    bb = bbk.Breadboard(nc, "图 34-p4-3 第二阶段：加上 CD4053、C1、C2 和跟随器", size=(13, 7.2),
                        rails=("+9 V", "GND", "GND", "+9 V"))
    _bb_clock(bb)
    bb.chip(28, "CD4053", npin=16, names=CD_NAMES)
    bb.wire("a28", "T+28", "pos")                 # 16 脚 VDD → +9 V
    bb.part("b28", "T-26", "", "C")               # Cb 100 nF：VDD 就近旁路到 GND
    bb.wire("j33", "B-33", "gnd")                 # 6 脚 INH
    bb.wire("j34", "B-34", "gnd")                 # 7 脚 VEE
    bb.wire("j35", "B-35", "gnd")                 # 8 脚 VSS
    bb.wire("a34", "T-34", "gnd")                 # 10 脚 B 控制
    bb.wire("a35", "T-35", "gnd")                 # 9 脚 C 控制
    bb.part("a30", "T-30", "", "C")               # C1：14 脚 A 公共 → GND
    bb.part("a31", "T-31", "", "C")               # C2：13 脚 AY → GND
    bb.route("c31", "c21", "out", dy=-0.5)
    bb.wire("b21", "b17", "out")                  # → 5 脚（跟随器输入）
    bb.part("a21", "T-21", "RL 1 MΩ（虚线：第 7 步才插）", "R", lab_side="r", fs_=7, dashed=True)
    # 时钟线从第 11 列往下、绕到面包板下边缘外面再上去，不压 Ct 的本体和标签（教师第 2 轮新建议-04）
    bb.wire("j11", "a33", "clk", via=[(11, -5.75), (10.5, -5.75), (10.5, -8.05), (36.6, -8.05), (36.6, 6.05), (33, 6.05)])
    bb.part("c38", "c41", "R1 10 kΩ", "R", lab_side=-1, fs_=7.5)
    bb.wire("a41", "T+41", "pos")
    bb.part("a38", "T-38", "", "R")
    bb.note(38.0, 9.75, "R2 10 kΩ：a38 → GND", fontsize=7.5, ha="center")
    bb.wire("a39", "T-39", "gnd")
    bb.wire("d32", "d39", "sig")                  # 第 8 步的起始位置：J 插 d39（0 V）
    _bb_battery(bb, nc)
    bb.probe("f11", "①", dx=-0.9, dy=0.0)
    bb.probe("d15", "②", dx=-0.9, dy=0.0)
    bb.probe("e38", "③", dx=0.9, dy=0.0)
    bb.note(0.5, -8.9, "① 第 11 列 = 时钟；② 第 15 列 = 跟随器输出 Vout（掐秒表时一直看它）；③ 第 38 列 = Vin；黑表笔插 GND 轨", ha="left")
    bb.note(0.5, -9.7, "a17→GND 那根线已拔掉；CD4053 1–8 脚在 f 排、16–9 脚在 e 排（第 28–35 列）；天蓝线：时钟 j11 → a33（11 脚 A）", ha="left")
    bb.note(0.5, -10.5, "蓝线 = 跳线 J：一头固定在 d32（12 脚 AX）；图中画的是起始位置 d39（0 V，a39 接 GND），第 5 步改插 d38（Vin = 4.5 V）", ha="left")
    bb.note(0.5, -11.3, "上方四只电容：Cd 100 nF（b14 → GND，LM358 旁路）、Cb 100 nF（b28 → GND，CD4053 旁路）、C1 10 nF（a30 → GND）、C2 1 µF 薄膜（a31 → GND）", ha="left")
    bb.legend(y=-0.10)
    bb.save(N, "34_p4_3_breadboard_sc.png")
    print("[图 34-p4-3] 第二阶段：CD4053 第 28–35 列；a28→+9 V，Cb b28→GND，j33/j34/j35→GND，a34/a35→GND，C1 a30→GND，C2 a31→GND，"
          "c31→c21→b17，RL a21→GND（第 7 步，虚线），j11→a33，R1 c38–c41，a41→+9 V，R2 a38→GND，a39→GND，跳线 d32→d39（起始）/d38；Cd b14→GND")


def p4_4():
    d = drawing(fontsize=10.5)
    # 输入分压（第 38 列）
    xn = -3.0
    d += elm.Dot().at((xn, 0))
    d += elm.Resistor().endpoints((xn, 0), (xn, 2.6))
    d += elm.Vdd().at((xn, 2.6)).label("+9 V")
    ls.lab(d, (xn - 0.45, 1.3), "R1 10 kΩ\nc38–c41\na41→+9 V", ha="right", fs_=9)
    d += elm.Resistor().endpoints((xn, 0), (xn, -2.6))
    d += elm.Ground().at((xn, -2.6))
    ls.lab(d, (xn - 0.45, -1.6), "R2 10 kΩ\na38→GND", ha="right", fs_=9)
    ls.colnote(d, (xn + 0.1, 0.35), "第 38 列", "top", ofst=0.0)
    ls.probe(d, (xn, 0), "③", dx=-0.9, dy=0.0)
    # 跳线 J：d32 一头固定，另一头插 d38 或 d39
    xd = -1.8
    d += elm.Line().at((xn, 0)).to((xd, 0))
    d += elm.Dot(open=True).at((xd, 0)); d += elm.Dot(open=True).at((xd, -1.2))
    ls.lab(d, (xd, 0.35), "d38", ha="center", fs_=9, color=ls.GRAY)
    ls.lab(d, (xd + 0.2, -1.6), "d39（a39→GND）", ha="left", fs_=9, color=ls.GRAY)
    d += elm.Line().at((xd, -1.2)).to((xd, -2.0)); d += elm.Ground().at((xd, -2.0))
    xj = -0.6
    d += elm.Dot().at((xj, 0))
    d += elm.Line().at((xj, 0)).to((xd + 0.1, 0)).color(C["vin"]).linewidth(2.2)
    d += elm.Line().at((xj, 0)).to((xd + 0.1, -1.1)).color("#999999").linestyle("--")
    ls.lab(d, (xj + 0.15, -0.55), "跳线 J（d32 端）", fs_=9, color=C["vin"])
    # 开关电容（第 28–35 列）
    p = _sc_core(d, xj, 0.0, vin_label="", show_ctrl=False)
    xm, ym, xo = p["xm"], p["ym"], p["xo"]
    ls.colnote(d, (xm + 0.2, ym - 1.9), "a30→GND", "right", ofst=0.0)
    ls.colnote(d, (xo + 0.45, -2.75), "a31→GND", "right", ofst=0.0)
    # 时钟方框 + 控制线
    bx0, bx1, by0, by1 = -4.6, -1.6, -5.8, -4.2
    for p_, q_ in (((bx0, by1), (bx1, by1)), ((bx1, by1), (bx1, by0)), ((bx1, by0), (bx0, by0)), ((bx0, by0), (bx0, by1))):
        d += elm.Line().at(p_).to(q_).color(ls.GRAY)
    ls.lab(d, ((bx0 + bx1) / 2, (by0 + by1) / 2), "时钟\n（图 34-p4-2）", ha="center", fs_=9.5)
    yc = (by0 + by1) / 2
    xc = xm - 1.0
    d += elm.Line().at((bx1, yc)).to((xc, yc)).color(C["cur"]).linewidth(1.6)
    d += elm.Line().at((xc, yc)).to((xc, -0.6)).color(C["cur"]).linewidth(1.6)
    d += elm.Line().at((xc, -0.6)).to((xm - 0.55, -0.6)).color(C["cur"]).linewidth(1.4).linestyle(":")
    ls.lab(d, ((bx1 + xc) / 2, yc + 0.35), "j11→a33（A 11 脚）", ha="center", fs_=9, color=C["cur"])
    # RL（第 21 列，虚线 = 第 7 步才插）
    xr = xo + 2.6
    d += elm.Line().at((xo, 0)).to((xr, 0))
    d += elm.Dot().at((xr, 0))
    d += elm.Resistor().endpoints((xr, 0), (xr, -3.5)).linestyle("--")
    d += elm.Ground().at((xr, -3.5))
    ls.lab(d, (xr, -4.6), "RL 1 MΩ：a21→GND\n（第 7 步才插）", ha="center", fs_=9)
    ls.colnote(d, (xr, 0.35), "第 21 列", "top", ofst=0.0)
    ls.colnote(d, ((xo + xr) / 2, -0.35), "c31→c21", "bottom", ofst=0.0)
    xf = xr + 2.0
    d += elm.Line().at((xr, 0)).to((xf, 0))
    ls.colnote(d, ((xr + xf) / 2, -0.35), "b21→b17", "bottom", ofst=0.0)
    a = _follower(d, xf, 0.0, holes=True)
    ls.probe(d, a["out"], "②", dx=0.8, dy=0.0)
    ls.note(d, (-4.6, -6.6), "CD4053：16 脚 a28→+9 V，b28 经 Cb 100 nF→GND；6、7、8 脚 j33/j34/j35→GND；9、10 脚 a35/a34→GND。LM358 两组共用 8 脚 +9 V（Cd 100 nF b14→GND）、4 脚 GND。")
    ls.note(d, (-4.6, -7.3), "开关画的是时钟为低时：14 脚接 12 脚（AX，跳线 J 那边）；时钟为高时 14 脚接 13 脚（AY，C2 那边）。")
    save_schem(d, N, "34_p4_4_schem_lab_sc.png")
    print("[图 34-p4-4] 第二阶段原理图，与图 34-p4-3 一一对应")



# =====================================================================
# 第 6 步：Rt 换成两只 68 kΩ 串联（h11–h13、g13–g15）——局部原理图 + 面包板
# =====================================================================
def p4_5():
    d = drawing(fontsize=10.5)
    d += elm.Dot().at((0, 0))
    ls.lab(d, (-0.15, 0.45), "第 11 列\n（1 脚输出，Rc 也在这里）", ha="right", fs_=9.5)
    d += elm.Resistor().endpoints((0, 0), (3.0, 0))
    ls.lab(d, (1.5, 0.6), "Rt① 68 kΩ（h11–h13）", ha="center", fs_=9.5)
    d += elm.Dot().at((3.0, 0))
    ls.colnote(d, (3.0, -0.4), "第 13 列（只有两只 Rt 相连）", "bottom", ofst=0.0)
    d += elm.Resistor().endpoints((3.0, 0), (6.0, 0))
    ls.lab(d, (4.5, 0.6), "Rt② 68 kΩ（g13–g15）", ha="center", fs_=9.5)
    d += elm.Dot().at((6.0, 0))
    ls.lab(d, (6.2, 0.45), "第 15 列（2 脚 IN−）", fs_=9.5)
    d += elm.Capacitor().endpoints((6.0, 0), (6.0, -2.4))
    d += elm.Ground().at((6.0, -2.4))
    ls.lab(d, (6.45, -1.2), "Ct 100 nF（j15→GND）", fs_=9.5)
    rt = 2 * sim.RT1
    T, _, _, _ = sim.relax_T(rt, sim.CT)
    print(f"[数值] 图 34-p4-5：Rt = {rt/1e3:.0f} kΩ，脚本 f = {1/T:.1f} Hz，ngspice {F2} Hz")
    assert rt == sim.RT2
    ls.note(d, (-3.2, -3.6), f"两只串联 = {rt/1e3:.0f} kΩ：周期加倍，时钟约 {F2} Hz（ngspice）。原理图其余部分和图 34-p4-2 相同。")
    save_schem(d, N, "34_p4_5_schem_rt_series.png")
    print("[图 34-p4-5] 第 6 步局部：第 11 列 → Rt① h11–h13 → 第 13 列 → Rt② g13–g15 → 第 15 列（Ct、2 脚）")


def p4_6():
    nc = 29
    bb = bbk.Breadboard(nc, "图 34-p4-6 第 6 步：Rt 换成两只 68 kΩ 串联（其余不动）", size=(9.6, 6.6),
                        rails=("+9 V", "GND", "GND", "+9 V"))
    bb.chip(14, "LM358", names=LM_NAMES)
    bb.wire("a14", "T+14", "pos")
    bb.wire("j17", "B-17", "gnd")
    xg, yg = bb.xy("g14")
    bb.wire("g14", "g11", "out", via=[(14, yg - 0.45), (11, yg - 0.45)])   # 跳线从 g 排下方绕过去，露出 g14 的端点
    bb.part("h11", "h13", "Rt① 68 kΩ", "R", lab_side=-1, fs_=7.5)
    # Rt②：本体抬到 f、g 两排之间，两条引脚斜着插进 g13、g15，g14 的孔和橙线端点都露在外面（教师第 2 轮新建议-04）
    (x13, y13), (x15, _) = bb.xy("g13"), bb.xy("g15")
    yb = y13 + 0.55
    bb.ax.plot([x13, x13 + 0.45, x15 - 0.45, x15], [y13, yb, yb, y13], color="0.35", lw=1.2, zorder=5)
    from matplotlib.patches import FancyBboxPatch as _FB
    bb.ax.add_patch(_FB((14 - 0.42, yb - 0.17), 0.84, 0.34, boxstyle="round,pad=0.04", fc="#d9c7a3", ec="0.2", lw=1.0, zorder=6))
    for x in (x13, x15):
        bb.ax.plot([x], [y13], "o", color="0.2", ms=3, zorder=7)
    gx, gy = 14, yb
    bb.ax.annotate("Rt② 68 kΩ\n（g13–g15，新加）", xy=(gx, gy + 0.05), xytext=(8.6, gy + 1.6), fontsize=7,
                   ha="center", va="center", arrowprops=dict(arrowstyle="->", color="0.3", lw=0.8))
    bb.part("j15", "B-15", "", "C", lab_side="l", fs_=7.5)
    bb.note(14.6, -5.8, "Ct 100 nF（j15）→", fontsize=7, ha="right", va="center")
    bb.part("b14", "T-12", "", "C")
    bb.note(12.2, 5.0, "Cd 100 nF", fontsize=7, ha="right", va="center")
    bb.part("i11", "i16", "Rc 10 kΩ", "R", lab_side="r", fs_=7.5)
    bb.part("h16", "h20", "Ra 10 kΩ", "R", lab_side=1, fs_=7.5)
    bb.wire("j20", "B+20", "pos")
    bb.wire("g16", "g22", "fb")
    bb.part("h22", "h26", "Rb 10 kΩ", "R", lab_side=1, fs_=7.5)
    bb.wire("j26", "B-26", "gnd")
    bb.wire("c15", "c16", "fb")
    _bb_battery(bb, nc)
    bb.note(0.5, -8.9, "Rt① 68 kΩ：h11–h13（原来那只从 h15 改插到 h13）；Rt② 68 kΩ：g13–g15（新加）", ha="left")
    bb.note(0.5, -9.7, "Rt② 从 g14 那根橙线上方跨过，只占 g13、g15 两个孔；第二阶段的 CD4053 等元件都不用动（图中省略）", ha="left")
    bb.legend(y=-0.02)
    bb.save(N, "34_p4_6_breadboard_rt_series.png")
    print("[图 34-p4-6] 第 6 步：Rt① h11–h13，Rt② g13–g15，g14→g11 跳线保留")


def p4_7():
    """图 34-p4-7：跳线从 GND 换到 4.5 V 后，万用表应读到的 Vout（以 SPICE 的时钟频率算）。"""
    fig, ax = plt.subplots(figsize=(7, 4.0))
    marks = (0.5, 1, 2, 3, 5, 8)
    for f, col, name in ((F1, C["vout"], "时钟 104 Hz（Rt = 68 kΩ）"), (F2, C["third"], "时钟 52 Hz（Rt = 136 kΩ）")):
        tt = np.linspace(0, 10, 600)
        v = sim.VIN * (1 - (1 - sim.alpha()) ** (tt * f))
        ax.plot(tt, v, color=col, lw=1.8, label=name)
        for m in marks:
            vm = sim.VIN * (1 - (1 - sim.alpha()) ** (m * f))
            ax.plot([m], [vm], "o", color=col, ms=4)
            print(f"[数值] 图 34-p4-7：{name}，{m} s 时应读 {vm:.2f} V")
    for frac in (0.632, 0.95):
        ax.axhline(frac * sim.VIN, **LS["ref"])
        ax.text(9.9, frac * sim.VIN - 0.24, f"{frac*100:.0f}%：{frac*sim.VIN:.2f} V", ha="right", fontsize=8.5, color="0.35")
    for f, col in ((F1, C["vout"]), (F2, C["third"])):
        for frac, dy in ((0.632, -16), (0.95, -16)):
            tx = sim.t_to(frac, f)
            ax.annotate(f"{tx:.2f} s", (tx, frac * sim.VIN), textcoords="offset points", xytext=(4, dy), fontsize=8.5, color=col)
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.9)
    ax.legend(loc="lower right", fontsize=9)
    axl(ax, "按下秒表后的时间 / s", "万用表读数 Vout / V")
    ax.set_title("图 34-p4-7 秒表实验：应该在什么时刻读到 2.84 V 和 4.27 V", fontsize=10.5)
    fs.save(fig, N, "34_p4_7_expected.png")


if __name__ == "__main__":
    for fn in (p1_1, p1_2, p1_3, p1_4, p2_1, p2_2, p2_3, p2_4, p2_5, p2_6, p3_1, p3_2, p3_3, p3_4, p3_5,
               p4_1, p4_2, p4_3, p4_4, p4_5, p4_6, p4_7):
        fn()
