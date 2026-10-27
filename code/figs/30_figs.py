"""30 仪表放大器与电桥：全部配图。
运行：/workspace/circuits-venv/bin/python code/figs/30_figs.py
图上的每个数字都由本脚本算出并打印；关键结论用 assert 检查。SPICE 复核见 spice/30/run.py。
"""
import os, sys, math, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
import lab_schem as ls         # 只借用 probe / colnote / lab / title / note / _pin 这些画图小工具（不修改它）
import numpy as np
import matplotlib.pyplot as plt

_sp = importlib.util.spec_from_file_location("bbkit30", os.path.join(HERE, "..", "30_bbkit.py"))
bb = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(bb)

N = "30"
VEX, R = 9.0, 10e3
G1 = 1 + 2 * 10e3 / 1e3


def bridge(vex, r, dr):
    """四臂 r，右下臂 r + dr：精确差压 Vb − Va 与近似 vex·dr/(4r)。"""
    return vex * (r + dr) / (2 * r + dr) - vex / 2, vex * dr / (4 * r)


def acm_exact(r1, r2, r3, r4):
    """差分级精确共模倍数（R1 入→反相端、R2 反馈、R3 入→同相端、R4 同相端→参考）。"""
    return r4 / (r3 + r4) * (1 + r2 / r1) - r2 / r1


# ======================================================================================
# 三运放仪表放大器的通用画法：A1 在上（翻转，+ 在上），A2 在下，RG 竖着接在两个反相端之间
# ======================================================================================
def draw_ina(d, x0, yB, names=None, gap=7.0, x3=None, show_ref=True):
    """返回关键点坐标 dict。names 给元件标签（R5、R6、RG、R7…R10、A1…A3）。"""
    nm = dict(A1="A1", A2="A2", A3="A3", R5="R5 10k", R6="R6 10k", RG="RG 1k",
              R7="R7 10k", R8="R8 10k", R9="R9 10k", R10="R10 10k")
    nm.update(names or {})
    yT = yB + gap
    d += (a1 := elm.Opamp(leads=True).theta(0).flip().anchor("in2").at((x0, yT)))
    d += (a2 := elm.Opamp(leads=True).theta(0).anchor("in2").at((x0, yB)))
    p = {}
    p["a1p"], p["a1m"], p["a1o"] = a1.absanchors["in2"], a1.absanchors["in1"], a1.absanchors["out"]
    p["a2p"], p["a2m"], p["a2o"] = a2.absanchors["in2"], a2.absanchors["in1"], a2.absanchors["out"]
    p["a1"], p["a2"] = a1, a2
    ls.lab(d, (a1.absanchors["center"][0] - 0.2, a1.absanchors["center"][1]), nm["A1"], ha="center", fs_=10)
    ls.lab(d, (a2.absanchors["center"][0] - 0.2, a2.absanchors["center"][1]), nm["A2"], ha="center", fs_=10)
    xn = x0 - 0.9
    yf1 = p["a1m"][1] - 1.0
    yf2 = p["a2m"][1] + 1.0
    xo = p["a1o"][0] + 0.7
    # A1 反相端 → 节点竖线 → R5（到 A1 输出）与 RG
    d += elm.Line().at(p["a1m"]).to((xn, p["a1m"][1]))
    d += elm.Line().at((xn, p["a1m"][1])).to((xn, yf1))
    d += elm.Dot().at((xn, yf1))
    d += elm.Resistor().at((xn, yf1)).to((xo, yf1))
    ls.lab(d, ((xn + xo) / 2, yf1 - 0.55), nm["R5"], ha="center", fs_=10)
    d += elm.Line().at((xo, yf1)).to((xo, p["a1o"][1]))
    d += elm.Line().at(p["a1o"]).to((xo, p["a1o"][1]))
    d += elm.Dot().at((xo, p["a1o"][1]))
    d += elm.Resistor().at((xn, yf1)).to((xn, yf2))
    ls.lab(d, (xn - 0.35, (yf1 + yf2) / 2), nm["RG"], ha="right", fs_=10)
    d += elm.Dot().at((xn, yf2))
    d += elm.Line().at((xn, yf2)).to((xn, p["a2m"][1]))
    d += elm.Line().at((xn, p["a2m"][1])).to(p["a2m"])
    d += elm.Resistor().at((xn, yf2)).to((xo, yf2))
    ls.lab(d, ((xn + xo) / 2, yf2 + 0.55), nm["R6"], ha="center", fs_=10)
    d += elm.Line().at((xo, yf2)).to((xo, p["a2o"][1]))
    d += elm.Line().at(p["a2o"]).to((xo, p["a2o"][1]))
    d += elm.Dot().at((xo, p["a2o"][1]))
    p["xn"], p["yf1"], p["yf2"], p["xo"] = xn, yf1, yf2, xo
    # 差分级（16 节的四电阻减法器）
    x3 = x3 if x3 is not None else xo + 4.2
    ym = (p["a1o"][1] + p["a2o"][1]) / 2
    d += (a3 := elm.Opamp(leads=True).theta(0).anchor("in2").at((x3, ym - 0.625)))
    p["a3p"], p["a3m"], p["a3o"], p["a3"] = a3.absanchors["in2"], a3.absanchors["in1"], a3.absanchors["out"], a3
    ls.lab(d, (a3.absanchors["center"][0] - 0.2, a3.absanchors["center"][1]), nm["A3"], ha="center", fs_=10)
    xr = x3 - 0.9
    d += elm.Line().at((xo, p["a1o"][1])).to((xo + 0.5, p["a1o"][1]))
    d += elm.Resistor().at((xo + 0.5, p["a1o"][1])).to((xr, p["a1o"][1]))
    ls.lab(d, ((xo + xr) / 2 + 0.25, p["a1o"][1] + 0.55), nm["R7"], ha="center", fs_=10)
    d += elm.Line().at((xr, p["a1o"][1])).to((xr, p["a3m"][1]))
    d += elm.Line().at((xr, p["a3m"][1])).to(p["a3m"])
    d += elm.Dot().at((xr, p["a1o"][1]))
    xo3 = p["a3o"][0] + 0.7
    d += elm.Resistor().at((xr, p["a1o"][1])).to((xo3, p["a1o"][1]))
    ls.lab(d, ((xr + xo3) / 2, p["a1o"][1] + 0.55), nm["R8"], ha="center", fs_=10)
    d += elm.Line().at((xo3, p["a1o"][1])).to((xo3, p["a3o"][1]))
    d += elm.Line().at(p["a3o"]).to((xo3, p["a3o"][1]))
    d += elm.Dot().at((xo3, p["a3o"][1]))
    d += elm.Line().at((xo, p["a2o"][1])).to((xo + 0.5, p["a2o"][1]))
    d += elm.Resistor().at((xo + 0.5, p["a2o"][1])).to((xr, p["a2o"][1]))
    ls.lab(d, ((xo + xr) / 2 + 0.25, p["a2o"][1] - 0.55), nm["R9"], ha="center", fs_=10)
    xq = xr + 0.45
    d += elm.Line().at((xr, p["a2o"][1])).to((xq, p["a2o"][1]))
    d += elm.Line().at((xq, p["a2o"][1])).to((xq, p["a3p"][1]))
    d += elm.Line().at((xq, p["a3p"][1])).to(p["a3p"])
    d += elm.Dot().at((xq, p["a2o"][1]))
    yref = p["a2o"][1] - 2.9
    d += elm.Resistor().at((xq, p["a2o"][1])).to((xq, yref))
    ls.lab(d, (xq + 0.35, (p["a2o"][1] + yref) / 2), nm["R10"], ha="left", fs_=10)
    p["xq"], p["yref"], p["xo3"], p["xr"] = xq, yref, xo3, xr
    return p


# ======================================================================================
# page1
# ======================================================================================
def draw_bridge(d, x0, y0, h=6.0, w=4.0, rnames=("R1 10k", "R2 10k", "R3 10k", "R4 10k"), meter=True,
                vex="9 V", bat=True):
    """惠斯通电桥：左臂 R1(上)/R2(下) 中点 Va，右臂 R3(上)/R4(下) 中点 Vb。返回 (va, vb, top, bot)。"""
    xl, xr = x0 + 2.0, x0 + 2.0 + w
    yt, yb = y0 + h, y0
    ym = (yt + yb) / 2
    if bat:
        d += elm.Battery().endpoints((x0, yb), (x0, yt)).reverse()
        ls.lab(d, (x0 - 0.45, ym), vex, ha="right", fs_=11)
        d += elm.Line().at((x0, yt)).to((xr, yt))
        d += elm.Line().at((x0, yb)).to((xr, yb))
        d += elm.Ground().at((x0, yb))
    d += elm.Dot().at((xl, yt)); d += elm.Dot().at((xl, yb))
    d += elm.Resistor().at((xl, yt)).to((xl, ym))
    d += elm.Resistor().at((xl, ym)).to((xl, yb))
    d += elm.Resistor().at((xr, yt)).to((xr, ym))
    d += elm.Resistor().at((xr, ym)).to((xr, yb))
    ls.lab(d, (xl - 0.4, (yt + ym) / 2), rnames[0], ha="right", fs_=10)
    ls.lab(d, (xl - 0.4, (ym + yb) / 2), rnames[1], ha="right", fs_=10)
    ls.lab(d, (xr + 0.4, (yt + ym) / 2), rnames[2], ha="left", fs_=10)
    ls.lab(d, (xr + 0.4, (ym + yb) / 2), rnames[3], ha="left", fs_=10)
    d += elm.Dot().at((xl, ym)); d += elm.Dot().at((xr, ym))
    ls.lab(d, (xl + 0.25, ym + 0.35), "Va", fs_=11, color=fs.C["vin"])
    ls.lab(d, (xr - 0.25, ym + 0.35), "Vb", ha="right", fs_=11, color=fs.C["vin"])
    if meter:
        d += elm.Line().at((xl, ym)).to((xl + 0.9, ym))
        d += elm.MeterV().endpoints((xl + 0.9, ym), (xr - 0.9, ym))
        d += elm.Line().at((xr - 0.9, ym)).to((xr, ym))
    return (xl, ym), (xr, ym), (xl, yt), (xl, yb)


def p1_1():
    with drawing(fontsize=11) as d:
        draw_bridge(d, 0, 0, rnames=("R1 10k", "R2 10k", "R3 10k", "R4 10k + ΔR\n（传感器）"))
        ls.note(d, (-1.5, -1.3), "两边都是 9 V 的一半左右；万用表跨在 Va、Vb 之间，只读两者的差 Vb − Va。")
    ex, _ = bridge(VEX, R, 100)
    print(f"[图 30-p1-1] 电桥：Va = 4.5 V，ΔR = 100 Ω 时 Vb = {4.5 + ex:.4f} V，差 {ex*1e3:.2f} mV")
    save_schem(d, N, "30_p1_1_bridge.png")


def p1_2():
    rx = np.linspace(0, 500, 201)
    ex = np.array([bridge(VEX, R, r)[0] for r in rx])
    fig, (a, b) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    a.plot(rx, np.full_like(rx, 4.5), **fs.LS["vin"], label="Va（左中点）")
    a.plot(rx, 4.5 + ex, **fs.LS["vout"], label="Vb（右中点）")
    a.set_ylim(0, 9.5)
    fs.ref_h(a, 9.0, "激励 9 V")
    fs.axlabels(a, "传感器变化 ΔR", "Ω", "对地电压", "V")
    a.legend(loc="lower right", fontsize=8.5)
    a.set_title("对地看：两条线几乎重合（共模 ≈ 4.5 V）", fontsize=10)
    b.plot(rx, ex * 1e3, **fs.LS["third"])
    fs.mark(b, 100, bridge(VEX, R, 100)[0] * 1e3, "{:.1f}", " mV", dx=8, dy=-14)
    fs.mark(b, 470, bridge(VEX, R, 470)[0] * 1e3, "{:.1f}", " mV", dx=-60, dy=0)
    fs.axlabels(b, "传感器变化 ΔR", "Ω", "差 Vb − Va", "mV")
    b.set_title("看差：才是有用信号（差模）", fontsize=10)
    v100 = bridge(VEX, R, 100)[0]
    print(f"[图 30-p1-2] 共模 4.5 V；差模 ΔR=100 Ω：{v100*1e3:.2f} mV，470 Ω：{bridge(VEX,R,470)[0]*1e3:.2f} mV；比值 {4.5/v100:.0f} 倍")
    fs.save(fig, N, "30_p1_2_cm_dm.png")


def p1_4():
    with drawing(fontsize=11) as d:
        va, vb, _, _ = draw_bridge(d, -9.5, -1.0, h=6.0, w=3.2, meter=False)
        p = draw_ina(d, 0, 0)
        # Va → A1 +（上）  Vb → A2 +（下）：注意 16 节习惯是 Vo ∝ V2 − V1，这里 A2 接 Vb
        d += elm.Line().at(va).to((va[0] + 0.9, va[1])).color(fs.C["vin"])
        d += elm.Line().at((va[0] + 0.9, va[1])).to((va[0] + 0.9, p["a1p"][1])).color(fs.C["vin"])
        d += elm.Line().at((va[0] + 0.9, p["a1p"][1])).to(p["a1p"]).color(fs.C["vin"])
        d += elm.Line().at(vb).to((vb[0] + 1.6, vb[1])).color(fs.C["vin"])
        d += elm.Line().at((vb[0] + 1.6, vb[1])).to((vb[0] + 1.6, p["a2p"][1])).color(fs.C["vin"])
        d += elm.Line().at((vb[0] + 1.6, p["a2p"][1])).to(p["a2p"]).color(fs.C["vin"])
        d += elm.Line().at((p["xq"], p["yref"])).to((p["xq"], p["yref"] - 0.3))
        d += elm.Dot(open=True).at((p["xq"], p["yref"] - 0.3))
        ls.lab(d, (p["xq"] + 0.3, p["yref"] - 0.65), "REF（接 V_MID，不是 0 V）", fs_=10, color=fs.C["third"])
        d += elm.Line().at((p["xo3"], p["a3o"][1])).to((p["xo3"] + 0.8, p["a3o"][1]))
        ls.lab(d, (p["xo3"] + 0.95, p["a3o"][1]), "Vo", fs_=12, color=fs.C["vout"])
        ls.title(d, (p["a1"].absanchors["center"][0], p["a1p"][1] + 1.3), "① 第一级：A1、A2 同相放大")
        ls.title(d, (p["a3"].absanchors["center"][0], p["a1o"][1] + 1.5), "② 第二级：16 节的减法器")
        ls.lab(d, (va[0] + 1.1, 5.55), "与上横线交叉不相连", fs_=8, color=ls.GRAY)
        ls.note(d, (-10.5, p["yref"] - 1.6), "电桥的两个中点分别直接进 A1、A2 的同相端：运放的同相端几乎不取电流，电桥的比例不被破坏；倍数只由一只 RG 决定。")
    print("[图 30-p1-4] Va→A1+，Vb→A2+；G = 1 + 2·10k/1k =", G1)
    save_schem(d, N, "30_p1_4_ina_idea.png")


def p1_5():
    fig, ax = fs.diagram(w=9.6, h=3.6, xlim=(0, 12), ylim=(0, 4.6))
    ax.text(0.1, 4.35, "电磁流量计（导电液体）", fontsize=10.5, weight="bold")
    fs.box(ax, 1.3, 3.4, "两个电极\n150～200 μV/(m/s)", w=2.4, h=0.9, fs=9)
    fs.box(ax, 4.6, 3.4, "仪表放大器\n抑制电极共模", w=2.2, h=0.9, fs=9, fc="#e8f1fa")
    fs.box(ax, 7.6, 3.4, "滤波 / 同步检波\n（38 节）", w=2.4, h=0.9, fs=9)
    fs.box(ax, 10.6, 3.4, "流速 → 流量", w=2.0, h=0.9, fs=9)
    for a_, b_ in ((2.5, 3.5), (5.7, 6.4), (8.8, 9.6)):
        fs.arrow(ax, (a_, 3.4), (b_, 3.4))
    ax.text(0.1, 1.95, "差压流量计（孔板 / 文丘里）", fontsize=10.5, weight="bold")
    fs.box(ax, 1.3, 1.0, "节流件前后\n压力差 ΔP", w=2.4, h=0.9, fs=9)
    fs.box(ax, 4.6, 1.0, "压阻电桥\n毫伏级输出", w=2.2, h=0.9, fs=9)
    fs.box(ax, 7.6, 1.0, "仪表放大器\n+ 模数转换", w=2.4, h=0.9, fs=9, fc="#e8f1fa")
    fs.box(ax, 10.6, 1.0, "开方：$Q_V$ ∝ √ΔP", w=2.0, h=0.9, fs=9)
    for a_, b_ in ((2.5, 3.5), (5.7, 6.4), (8.8, 9.6)):
        fs.arrow(ax, (a_, 1.0), (b_, 1.0))
    print("[图 30-p1-5] 两种流量计里仪表放大器的位置")
    fs.save(fig, N, "30_p1_5_flowmeters.png")



# ======================================================================================
# page2
# ======================================================================================
def p2_2():
    with drawing(fontsize=11) as d:
        p = draw_ina(d, 0, 0)
        for key, txt in (("a1p", "V1"), ("a2p", "V2")):
            x, y = p[key]
            d += elm.Line().at((x - 2.2, y)).to((x, y)).color(fs.C["vin"])
            d += elm.Dot(open=True).at((x - 2.2, y))
            ls.lab(d, (x - 2.45, y), txt, ha="right", fs_=12, color=fs.C["vin"])
        T = fs.C["fb"]
        ls.lab(d, (p["xn"] - 0.25, p["a1m"][1] + 0.35), "= V1（虚短）", ha="right", fs_=9.5, color=T)
        ls.lab(d, (p["xn"] - 0.25, p["a2m"][1] - 0.35), "= V2（虚短）", ha="right", fs_=9.5, color=T)
        ym = (p["yf1"] + p["yf2"]) / 2
        d += elm.Arrow().at((p["xn"] + 0.45, ym - 0.7)).to((p["xn"] + 0.45, ym + 0.7)).color(fs.C["cur"])
        ls.lab(d, (p["xn"] + 0.7, ym), "I = (V2 − V1) / RG\n（向上流，也流过 R5、R6）", fs_=9.5, color=fs.C["cur"])
        ls.lab(d, (p["xo"] + 0.25, p["a1o"][1] + 0.45), "V1 − I·R5", fs_=9.5, color=T)
        ls.lab(d, (p["xo"] + 0.25, p["a2o"][1] - 0.45), "V2 + I·R6", fs_=9.5, color=T)
        d += elm.Line().at((p["xq"], p["yref"])).to((p["xq"], p["yref"] - 0.3))
        d += elm.Dot(open=True).at((p["xq"], p["yref"] - 0.3))
        ls.lab(d, (p["xq"] + 0.3, p["yref"] - 0.65), "REF（接 V_MID，不是 0 V）", fs_=10, color=fs.C["third"])
        d += elm.Line().at((p["xo3"], p["a3o"][1])).to((p["xo3"] + 0.8, p["a3o"][1]))
        ls.lab(d, (p["xo3"] + 0.95, p["a3o"][1]), "Vo − REF\n= (1 + 2R/RG)(V2 − V1)", fs_=10, color=fs.C["vout"])
    print("[图 30-p2-2] 推导用节点：A1 出 V1 − IR，A2 出 V2 + IR，I = (V2 − V1)/RG")
    save_schem(d, N, "30_p2_2_ina_derive.png")


def p2_1():
    k = np.linspace(0, 0.10, 201)                          # ΔR/R
    ex = np.array([bridge(VEX, R, kk * R)[0] for kk in k])
    ap = VEX * k / 4
    fig, (a, b) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    a.plot(k * 100, ex * 1e3, **fs.LS["vout"], label="精确：Vex·ΔR / (2(2R + ΔR))")
    a.plot(k * 100, ap * 1e3, **fs.LS["good"], label="近似：Vex·ΔR / (4R)")
    fs.axlabels(a, "ΔR / R", "%", "电桥差压", "mV")
    a.legend(fontsize=8.5, loc="upper left")
    a.set_title("9 V 激励、10 kΩ 桥臂", fontsize=10)
    err = np.where(k > 0, (ap / np.where(ex == 0, 1, ex) - 1) * 100, 0)
    b.plot(k * 100, err, **fs.LS["third"])
    for kk in (0.01, 0.022, 0.047):
        e_ = (VEX * kk / 4 / bridge(VEX, R, kk * R)[0] - 1) * 100
        fs.mark(b, kk * 100, e_, "{:.2f}", " %", dx=6, dy=-12)
    fs.axlabels(b, "ΔR / R", "%", "近似偏大", "%")
    b.set_title("误差 ≈ ΔR/(2R)：1% 变化只差 0.5%", fontsize=10)
    assert abs((VEX * 0.01 / 4 / bridge(VEX, R, 100)[0] - 1) - 0.005) < 1e-6
    print("[图 30-p2-1] ΔR/R = 1%%：精确 %.3f mV，近似 %.3f mV" % (bridge(VEX, R, 100)[0] * 1e3, VEX * 0.01 / 4 * 1e3))
    fs.save(fig, N, "30_p2_1_bridge_exact.png")


def p2_3():
    cases = [("一只 +0.1%", (10e3, 10e3, 10e3, 10.01e3)), ("一只 +1%", (10e3, 10e3, 10e3, 10.1e3)),
             ("四只 1%\n最坏", (10.1e3, 9.9e3, 9.9e3, 10.1e3)), ("四只 5%\n最坏", (10.5e3, 9.5e3, 9.5e3, 10.5e3))]
    diff = [20 * math.log10(1 / acm_exact(*rr)) for _, rr in cases]
    ina = [c + 20 * math.log10(G1) for c in diff]
    x = np.arange(len(cases))
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    b1 = ax.bar(x - 0.2, diff, 0.38, color=fs.C["vin"], label="只有 16 节的差分级（倍数 1）")
    b2 = ax.bar(x + 0.2, ina, 0.38, color=fs.C["vout"], label="仪表放大器（第一级 21 倍）")
    for bars in (b1, b2):
        for r_ in bars:
            ax.text(r_.get_x() + r_.get_width() / 2, r_.get_height() + 1.5, f"{r_.get_height():.1f}", ha="center", fontsize=8.5)
    ax.set_xticks(x, [c[0] for c in cases], fontsize=9)
    ax.set_ylim(0, 108)
    ax.set_ylabel("共模抑制比 CMRR / dB")
    ax.legend(fontsize=8.5, loc="upper right")
    for (n_, _), a_, b_ in zip(cases, diff, ina):
        print(f"[图 30-p2-3] {n_.replace(chr(10), '')}：差分级 {a_:.1f} dB，仪表放大器 {b_:.1f} dB")
    fs.save(fig, N, "30_p2_3_cmr_compare.png")



# ======================================================================================
# page3
# ======================================================================================
def p3_1():
    g = np.logspace(0, 3, 200)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for tol, key, txt in ((0.001, "vin", "四只 0.1% 最坏"), (0.01, "vout", "四只 1% 最坏"), (0.05, "third", "四只 5% 最坏")):
        acm = acm_exact(10e3 * (1 + tol), 10e3 * (1 - tol), 10e3 * (1 - tol), 10e3 * (1 + tol))
        c = 20 * np.log10(g / acm)
        ax.semilogx(g, c, **fs.LS[key], label=f"{txt}（差分级 {20*math.log10(1/acm):.1f} dB）")
    fs.ref_v(ax, 21, "本节 G1 = 21")
    fs.axlabels(ax, "第一级倍数 G1", None, "整机 CMRR（只算电阻）", "dB")
    ax.set_ylim(10, 110)
    ax.legend(fontsize=8.5, loc="lower right")
    for tol in (0.001, 0.01, 0.05):
        acm = acm_exact(10e3 * (1 + tol), 10e3 * (1 - tol), 10e3 * (1 - tol), 10e3 * (1 + tol))
        print(f"[图 30-p3-3] {tol*100:g}% 最坏：G1=1 {20*math.log10(1/acm):.1f} dB，G1=21 {20*math.log10(21/acm):.1f} dB，G1=100 {20*math.log10(100/acm):.1f} dB")
    fs.save(fig, N, "30_p3_3_cmr_vs_gain.png")


def p3_2():
    vdc = np.linspace(0.05, 2.0, 300)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    g9 = 2 * (7.5 - 4.5) / vdc                       # 9 V 单电源 LM358：输出上限约 7.5 V，V_MID = 4.5 V
    g5 = 2 * (4.9 - 2.5) / vdc                       # 5 V 轨到轨（如 INA333 一类）：输出约 0.1～4.9 V，REF = 2.5 V
    ax.semilogy(vdc, g9, **fs.LS["vin"], label="9 V 单电源 + LM358（输出 ≤ 7.5 V，V_MID = 4.5 V）")
    ax.semilogy(vdc, g5, **fs.LS["third"], label="5 V 轨到轨（输出 ≤ 4.9 V，REF = 2.5 V）")
    for v in (0.2, 1.0, 2.0):
        fs.mark(ax, v, 6 / v, "{:.0f}", " 倍", dx=6, dy=4)
    fs.ref_h(ax, 10, "ADI：电磁流量计第一级一般 ≤ 10 倍", x=0.98)
    fs.axlabels(ax, "电极之间的直流差（极化电压）", "V", "第一级最多放大", "倍")
    ax.legend(fontsize=8.5, loc="upper right")
    print("[图 30-p3-2] 9 V/LM358：直流差 0.2 V → %.0f 倍，1 V → %.0f 倍，2 V → %.0f 倍" % (6 / 0.2, 6 / 1, 6 / 2))
    fs.save(fig, N, "30_p3_2_headroom.png")


def p3_3():
    q = np.linspace(0, 1, 401)
    fig, (a, b) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    a.plot(q * 100, q ** 2 * 100, **fs.LS["vout"])
    fs.mark(a, 10, 1.0, "{:.0f}", " %", dx=6, dy=6)
    fs.mark(a, 50, 25.0, "{:.0f}", " %", dx=-30, dy=8)
    fs.axlabels(a, "体积流量 $Q_V$（满量程）", "%", "差压 ΔP（满量程）", "%")
    a.set_title("ΔP ∝ $Q_V^2$：10% 流量只有 1% 差压", fontsize=10)
    qq = np.linspace(0.05, 1, 300)
    rel = 0.5 * 0.001 / qq ** 2 * 100
    b.semilogy(qq * 100, rel, **fs.LS["bad"])
    fs.mark(b, 10, 5.0, "{:.1f}", " %", dx=8, dy=0)
    fs.mark(b, 100, 0.05, "{:.2f}", " %", dx=-55, dy=8)
    b.axvspan(0, 6, color=fs.C["ref"], alpha=0.25)
    b.text(6.8, 20, "低流量切除区", fontsize=9)
    fs.axlabels(b, "体积流量 $Q_V$（满量程）", "%", "流量相对误差", "%")
    b.set_title("差压误差 0.1% 满量程 → 流量误差", fontsize=10)
    print("[图 30-p3-4] 10%% 流量差压 1%%；差压误差 0.1%% FS：10%% 流量 → %.1f%%，100%% → %.2f%%" % (0.5 * 0.001 / 0.01 * 100, 0.05))
    fs.save(fig, N, "30_p3_4_dp_sqrt.png")


def p3_4(fname="30_p3_5_ina_chip.png", tag="图 30-p3-5", r4="R4 10k"):
    with drawing(fontsize=11) as d:
        d += (ic := module("INA333（单片仪表放大器）", left=("+IN", "RG", "RG ", "−IN"), right=("V+", "VOUT", "REF", "V−"), w=3.6).right().at((0, 0)))
        A = ic.absanchors
        # 引脚号：TI INA333 数据手册 Pin Functions（RG 1/8，−IN 2，+IN 3，V− 4，REF 5，VOUT 6，V+ 7）
        for nm, pn in (("+IN", "3"), ("RG", "1"), ("RG ", "8"), ("−IN", "2")):
            ls._pin(d, A[nm], pn, dx=0.25, dy=0.22)
        for nm, pn in (("V+", "7"), ("VOUT", "6"), ("REF", "5"), ("V−", "4")):
            ls._pin(d, A[nm], pn, dx=-0.25, dy=0.22)
        va, vb, top, bot = draw_bridge(d, -10.5, A["−IN"][1] - 0.5, h=5.0, w=3.0, meter=False, vex="5 V",
                                       rnames=("R1 10k", "R2 10k", "R3 10k", r4))
        xv = vb[0] + 1.5
        d += elm.Line().at(vb).to((xv, vb[1])).color(fs.C["vin"])
        d += elm.Line().at((xv, vb[1])).to((xv, A["+IN"][1])).color(fs.C["vin"])
        d += elm.Line().at((xv, A["+IN"][1])).to(A["+IN"]).color(fs.C["vin"])
        yl = bot[1] - 0.9
        xa, xw = va[0] + 0.8, xv + 0.8
        d += elm.Line().at(va).to((xa, va[1])).color(fs.C["vin"])
        d += elm.Line().at((xa, va[1])).to((xa, yl)).color(fs.C["vin"])
        d += elm.Line().at((xa, yl)).to((xw, yl)).color(fs.C["vin"])
        d += elm.Line().at((xw, yl)).to((xw, A["−IN"][1])).color(fs.C["vin"])
        d += elm.Line().at((xw, A["−IN"][1])).to(A["−IN"]).color(fs.C["vin"])
        ls.lab(d, (xa + 0.15, bot[1] - 0.35), "交叉不相连", fs_=8, color=ls.GRAY)
        xr = A["RG"][0] - 0.8
        d += elm.Line().at(A["RG"]).to((xr, A["RG"][1]))
        d += elm.Line().at(A["RG "]).to((xr, A["RG "][1]))
        d += elm.Resistor(scale=0.45).at((xr, A["RG"][1])).to((xr, A["RG "][1]))
        ls.lab(d, (xr - 0.25, (A["RG"][1] + A["RG "][1]) / 2), "RG 5k", ha="right", fs_=9.5)
        xo = A["VOUT"][0]
        d += elm.Line().at(A["V+"]).to((xo + 0.8, A["V+"][1]))
        d += elm.Vdd().at((xo + 0.8, A["V+"][1])).label("5 V")
        d += elm.Line().at(A["V−"]).to((xo + 0.8, A["V−"][1]))
        d += elm.Ground().at((xo + 0.8, A["V−"][1]))
        d += elm.Line().at(A["VOUT"]).to((xo + 1.8, A["VOUT"][1]))
        ls.lab(d, (xo + 1.95, A["VOUT"][1]), "Vo = REF + 21 × (Vb − Va)", fs_=10, color=fs.C["vout"])
        xr2, yr2 = xo + 1.7, A["REF"][1] - 1.9
        d += elm.Line().at(A["REF"]).to((xr2, A["REF"][1]))
        d += elm.Line().at((xr2, A["REF"][1])).to((xr2, yr2))
        ipf = follower_left(d, (xr2, yr2), "跟随器")
        xdv = ipf[0] + 1.6
        d += elm.Line().at(ipf).to((xdv, ipf[1]))
        d += elm.Dot().at((xdv, ipf[1]))
        d += elm.Resistor(scale=0.7).at((xdv, ipf[1])).to((xdv, ipf[1] + 2.2))
        d += elm.Vdd().at((xdv, ipf[1] + 2.2)).label("5 V")
        d += elm.Resistor(scale=0.7).at((xdv, ipf[1])).to((xdv, ipf[1] - 2.2))
        d += elm.Ground().at((xdv, ipf[1] - 2.2))
        ls.lab(d, (xdv + 0.35, ipf[1] + 1.1), "10k", fs_=9)
        ls.lab(d, (xdv + 0.35, ipf[1] - 1.1), "10k", fs_=9)
        ls.lab(d, (xdv + 0.35, ipf[1]), "2.5 V", fs_=9)
        ls.lab(d, (xr2 + 2.0, yr2 - 2.2), "REF = 2.5 V 低阻基准（分压 + 跟随器）", ha="center", fs_=9.5, color=ls.GRAY)
        ls.note(d, (-11.5, A["−IN"][1] - 4.6), "外部只剩一只 RG：G = 1 + 100 kΩ / RG，RG = 5 kΩ 时 21 倍；内部那几只 R 由厂家在芯片里做好并匹配，比手挑的分立电阻好得多。引脚号按 TI INA333 数据手册（8 脚封装）：RG 1、8，−IN 2，+IN 3，V− 4，REF 5，VOUT 6，V+ 7。")
    print("[%s] INA333：G = 1 + 100k/RG，RG = 5k → %.0f" % (tag, 1 + 100e3 / 5e3))
    save_schem(d, N, fname)


def p2_6():
    """page2 例 3 同页原理图：与图 30-p3-5 同一电路（INA333，5 V 电桥，RG 5 kΩ，REF 2.5 V）。"""
    p3_4("30_p2_6_ina333_ex3.png", "图 30-p2-6", r4="R4 10k\n（变化 1% 的臂）")



# ======================================================================================
# page4：面包板（两片 LM358，46 列）
#   轨：T1 = V+ 9 V（红），T2 = 0 V（黑），B1 = 0 V（黑），B2 = V+（红）；左端 T1↔B2、T2↔B1 连通
#   U1 在第 22～25 列：A1 = B 半边（5 脚 + = Va，6 脚 −，7 脚 出），A2 = A 半边（3 脚 + = Vb，2 脚 −，1 脚 出）
#   U2 在第 36～39 列：A3 = A 半边（1 出、2 −、3 +），B 半边接成跟随器输出 V_MID
# ======================================================================================
def p4_3():
    W = bb.BB_WIRE
    rails = {"T1": ("V+（9 V）", W["pos"]), "T2": ("0 V", W["gnd"]), "B1": ("0 V", W["gnd"]), "B2": ("V+（9 V）", W["pos"])}
    fig, ax = bb.bb_board(46, rails, figsize=(13.6, 5.4))
    bb.bb_wire(ax, "T2-1", "B1-1", "gnd", via=[(-0.4, 10.8), (-0.4, -2.8)])
    bb.bb_wire(ax, "T1-1", "B2-1", "pos", via=[(-0.9, 11.6), (-0.9, -3.6)])
    # 左桥臂（上半区）
    bb.bb_wire(ax, "a2", "T1-2", "pos")
    bb.bb_res(ax, "b2", "b5", "R1 10k")
    bb.bb_res(ax, "c5", "c8", "R2 10k", dy=-0.55)
    bb.bb_wire(ax, "a8", "T2-8", "gnd")
    # 右桥臂（下半区）
    bb.bb_wire(ax, "j10", "B2-10", "pos")
    bb.bb_res(ax, "i10", "i13", "R3 10k", dy=-0.55)
    bb.bb_res(ax, "h13", "h16", "R4 9.1k")
    bb.bb_block(ax, ["j16", "j17", "j18"], "", pins=None, fc="#90caf9", pad=0.32)
    bb._bb_label(ax, 14.5, -1.0, "RP1 2k", fs_=7)
    bb.bb_res(ax, "i17", "i20", "RX", dy=-0.5)
    ax.add_patch(bb._BbRect((16.55, -0.5), 3.9, 1.0, fc="none", ec="0.35", lw=0.9, ls=(0, (3, 2)), zorder=6))
    bb._bb_label(ax, 14.95, 0.0, "第 9 步才插 →", fs_=6.5)   # 放在 i14–i16 空孔上，不挡 RP1 的 j16–j18
    rx_note = ax.texts[-1]
    bb.bb_wire(ax, "h17", "h20", "out")
    bb._bb_label(ax, 18.5, 1.55, "J1")
    bb.bb_wire(ax, "j20", "B1-20", "gnd")
    # Va → U1 5 脚（d25）；Vb → U1 3 脚（g24）
    bb.bb_wire(ax, "d5", "d25", "sig", via=[(5, 6.5), (25, 6.5)])
    bb.bb_wire(ax, "g13", "g24", "sig", via=[(13, 2.5), (24, 2.5)])
    # 共模测试才插：J2（虚线）、RC
    ax.plot([5, 5, 13, 13], [5, 4.0, 4.0, 3], color=W["sig"], lw=1.6, ls=(0, (3, 2)), zorder=3)
    bb._bb_label(ax, 9.0, 4.0, "J2（共模测试才插）", fs_=7)
    bb.bb_res(ax, "j13", "B1-13", "RC", dy=0.55)
    ax.add_patch(bb._BbRect((12.4, -3.15), 1.2, 2.6, fc="none", ec="0.35", lw=0.9, ls=(0, (3, 2)), zorder=6))
    # U1
    bb.bb_dip8(ax, 22, "U1 LM358")
    bb.bb_wire(ax, "a22", "T1-22", "pos")
    bb.bb_wire(ax, "j25", "B1-25", "gnd")
    bb.bb_part2(ax, "b22", "T2-21", "", kind="box", dy=0.0, fc="#f2c94c")
    bb._bb_label(ax, 20.0, 8.5, "C1 0.1µ", fs_=6.5)
    bb.bb_res(ax, "b23", "b24", "R5 10k")
    bb.bb_wire(ax, "a24", "a28", "fb")
    bb.bb_res(ax, "e28", "f28", "RG 1k", dy=0.55)
    bb.bb_wire(ax, "h23", "h28", "fb")
    bb.bb_res(ax, "i22", "i23", "R6 10k", dy=-0.55)
    # A1 出 → R7 → A3 −；A2 出 → R9 → A3 +
    bb.bb_wire(ax, "c23", "c32", "fb")
    bb.bb_res(ax, "e32", "f32", "R7 10k", dy=-0.55)
    bb.bb_wire(ax, "g32", "g37", "fb")
    bb.bb_wire(ax, "j22", "j33", "fb", via=[(22, -1.5), (33, -1.5)])
    bb.bb_res(ax, "i33", "i38", "R9 10k", dy=-0.5)
    bb.bb_res(ax, "h36", "h37", "R8 10k", dy=-0.5)
    bb.bb_res(ax, "h38", "h46", "R10 10k", dy=0.5)
    # U2 与中点参考 V_MID
    bb.bb_dip8(ax, 36, "U2 LM358")
    bb.bb_wire(ax, "a36", "T1-36", "pos")
    bb.bb_wire(ax, "j39", "B1-39", "gnd")
    bb.bb_part2(ax, "b36", "T2-35", "", kind="box", dy=0.0, fc="#f2c94c")
    bb._bb_label(ax, 34.0, 8.5, "C2 0.1µ", fs_=6.5)
    bb.bb_wire(ax, "b37", "b38", "fb")
    bb.bb_res(ax, "b39", "b42", "RM1 10k")
    bb.bb_wire(ax, "a42", "T1-42", "pos")
    bb.bb_res(ax, "c39", "c44", "RM2 10k", dy=-0.5)
    bb.bb_wire(ax, "a44", "T2-44", "gnd")
    bb.bb_wire(ax, "d37", "g46", "neg", via=[(37, 6.5), (46, 6.5)])
    bb._bb_label(ax, 43.5, 4.3, "紫线 = V_MID")
    # 9 V 电池画在板外
    ax.add_patch(bb._BbRect((3.2, 12.9), 4.0, 0.75, fc="#ffe082", ec="0.3", lw=0.8, zorder=5))
    ax.text(5.2, 13.27, "9 V 电池", ha="center", va="center", fontsize=7.5, zorder=6)
    ax.plot([4.0, 4.0], [12.9, 11.6], color=W["pos"], lw=2.0, zorder=3); ax.plot(4, 11.6, "o", ms=4, color=W["pos"], zorder=4)
    ax.plot([6.4, 6.4], [12.9, 10.8], color=W["gnd"], lw=2.0, zorder=3); ax.plot(6.4, 10.8, "o", ms=4, color=W["gnd"], zorder=4)
    ax.text(3.6, 13.27, "+", ha="right", va="center", fontsize=9, color=W["pos"])
    ax.text(6.8, 13.27, "−", ha="left", va="center", fontsize=9)
    ax.text(9.0, 13.5, "j22→j33 与 j25→0 V 两根线只是交叉，不相连；虚线框里的 RX 第 9 步才插（之前 J1 短接）；虚线 J2、虚线框 RC（4.7 kΩ）只在第 13～16 步插",
            ha="left", va="center", fontsize=8)
    ax.text(9.0, 13.0, "第 15、16 步：R10 改插 h38–h45，再把 100 Ω 插在 i45–i46（R10 与 V_MID 之间串 100 Ω）",
            ha="left", va="center", fontsize=8)
    bb.bb_probe(ax, "a5", "A", dx=-1.0, dy=0.6)
    bb.bb_probe(ax, "f13", "B", dx=-1.0, dy=0.6)
    bb.bb_probe(ax, "j36", "C", dx=0.0, dy=-1.1)
    bb.bb_probe(ax, "g46", "D", dx=1.0, dy=0.6)
    bb.bb_probe(ax, "d23", "E", dx=-0.9, dy=0.0)
    bb.bb_probe(ax, "h22", "F", dx=-0.9, dy=0.0)
    ax.set_ylim(-5.9, 14.0)
    bb.bb_legend(ax, [("pos", "红：V+"), ("gnd", "黑：0 V"), ("neg", "紫：V_MID 中点参考")], x=1.0, y=-4.75)
    bb.bb_legend(ax, [("sig", "蓝：电桥信号"), ("fb", "绿：放大器内部"), ("out", "橙：J1 短接")], x=21.0, y=-4.75)
    print("[图 30-p4-3] 左臂 R1 b2–b5、R2 c5–c8（Va 第 5 列）；右臂 R3 i10–i13、R4 h13–h16、RP1 j16/j17/j18、RX i17–i20、J1 h17–h20（Vb 第 13 列）；"
          "U1 第 22 列：Va→d25（5 脚），Vb→g24（3 脚），R5 b23–b24，R6 i22–i23，RG e28–f28；"
          "U2 第 36 列：R7 e32–f32，R8 h36–h37，R9 i33–i38，R10 h38–h46，V_MID = d37→g46")
    # 孔位断言：「第 9 步才插」标签压着的 i14–i16 必须是空孔；标签不能盖住 RP1（j16–j18）和 RX 虚线框
    ends = {(round(x, 2), round(y, 2)) for ln in ax.lines if ln.get_marker() == "o"
            for x, y in zip(ln.get_xdata(), ln.get_ydata())}
    for h in ("i14", "i15", "i16"):
        assert bb.bb_xy(h) not in ends, f"{h} 已被占用，标签不能压在上面"
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    tb = rx_note.get_bbox_patch().get_window_extent(rend)
    for pt in ax.patches:
        ext = pt.get_window_extent(rend)
        if ext.width < fig.bbox.width * 0.5 and tb.overlaps(ext) and pt.get_facecolor()[:3] != (1.0, 1.0, 1.0):
            raise AssertionError(f"「第 9 步才插」标签与图形 {pt} 重叠")
    print("[图 30-p4-3] 孔位断言通过：i14–i16 空，「第 9 步才插」标签不压 RP1、RX 框")
    fs.save(fig, N, "30_p4_3_breadboard.png")



def p4_5():
    rxs = [0, 100, 220, 470]
    v21 = [G1 * bridge(VEX, R, r)[0] for r in rxs]
    v1 = [bridge(VEX, R, r)[0] for r in rxs]
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.2, 3.2), gridspec_kw=dict(width_ratios=[1, 1.15]))
    a.plot(rxs, v21, "o", **fs.LS["vout"], label="RG 1 kΩ（21 倍）")
    rr = np.linspace(0, 470, 50)
    lin = G1 * VEX * rr / (4 * R)      # 小信号近似：差压 ≈ 9 V × RX ÷ 40 kΩ，再乘 21
    a.plot(rr, lin, color="0.35", ls="--", lw=1.2, label="小信号直线 21 × 9 V × RX ÷ 40 kΩ")
    lin470 = G1 * VEX * 470 / (4 * R)
    assert abs(lin470 - 2.221) < 0.001, lin470
    fs.mark(a, 470, lin470, "{:.3f}", " V", color="0.35", dx=-40, dy=8)
    a.plot([470], [v1[-1]], "s", color=fs.C["third"], ms=6, label="第 12 步：RX 470 Ω 时拔掉 RG（1 倍）")
    fs.mark(a, 470, v1[-1], "{:.3f}", " V", color=fs.C["third"], dx=-48, dy=8)
    for r, v in zip(rxs[1:], v21[1:]):
        fs.mark(a, r, v, "{:.3f}", " V", dx=-48 if r < 470 else -14, dy=6 if r < 470 else -14)
    fs.axlabels(a, "RX", "Ω", "Vo − V_MID（测点 C 对测点 D）", "V")
    a.legend(fontsize=8.5, loc="upper left")
    a.set_ylim(-0.1, 3.1)
    a.set_title("第 9～12 步：差模", fontsize=10)
    lo, hi = 4.5 * 4.7 / 7.2, 9 - 4.5 * 4.7 / 7.2
    dv = hi - lo
    cases = [("R10 串 100 Ω", acm_exact(10e3, 10e3, 10e3, 10.1e3)),
             ("四只 1% 最坏", acm_exact(10.1e3, 9.9e3, 9.9e3, 10.1e3)),
             ("四只 5% 最坏", acm_exact(10.5e3, 9.5e3, 9.5e3, 10.5e3))]
    y = np.arange(len(cases))
    vals = [c[1] * dv * 1e3 for c in cases]
    b.barh(y, vals, color=[fs.C["vin"], fs.C["vout"], fs.C["bad"]], height=0.55)
    for yy, v in zip(y, vals):
        b.text(v * 1.15, yy, f"{v:.1f} mV", va="center", fontsize=9)
    b.set_xscale("log"); b.set_xlim(5, 3000)
    b.set_yticks(y, [c[0] for c in cases], fontsize=9)
    b.invert_yaxis()
    b.set_xlabel("共模从 %.2f V 跳到 %.2f V 时 Vo 的变化 / mV" % (lo, hi))
    b.set_title("第 13～16 步：共模（四只完全匹配 ≈ 0）", fontsize=10)
    print("[图 30-p4-5] Vo−V_MID：" + "，".join(f"RX {r}: {v:.3f} V" for r, v in zip(rxs, v21)) +
          f"；拔 RG RX470: {v1[-1]:.4f} V；共模 {lo:.3f}→{hi:.3f} V，ΔVo：" + "，".join(f"{c[0]} {v:.1f} mV" for c, v in zip(cases, vals)))
    fs.save(fig, N, "30_p4_5_expected.png")


def decap(d, x, ytop, name, where):
    """去耦电容：V+ —— 0.1 µF —— 0 V，紧挨芯片的 8 脚和 0 V 轨。"""
    d += elm.Vdd().at((x, ytop)).label("V+（8 脚）")
    d += elm.Capacitor().at((x, ytop)).to((x, ytop - 1.6))
    d += elm.Ground().at((x, ytop - 1.6))
    ls.lab(d, (x + 0.45, ytop - 0.8), f"{name} 0.1µF\n（{where}）", fs_=9, ha="left")


def p4_4():
    T = ls.TEAL
    with drawing(fontsize=11) as d:
        ls.title(d, (2.5, 11.0), "仪表放大器实验（U1、U2 都是 LM358；9 V 单电源）")
        # 电源与电桥（两条臂横着画，避免交叉）
        xb, xp = -16.0, -13.5
        d += elm.Battery().endpoints((xb, -2.0), (xb, 7.0)).reverse()
        ls.lab(d, (xb - 0.45, 2.5), "9 V\n电池", ha="right", fs_=10)
        d += elm.Line().at((xb, 7.0)).to((xp, 7.0))
        d += elm.Ground().at((xb, -2.0)).label("0 V", "bottom")
        ls.colnote(d, (xb + 0.1, 7.25), "V+ 轨", "top", ofst=0.0)
        d += elm.Line().at((xp, 7.0)).to((xp, 0.0))
        d += elm.Dot().at((xp, 7.0))
        xm = -9.6
        d += elm.Resistor().at((xp, 7.0)).to((xm, 7.0))
        ls.lab(d, ((xp + xm) / 2, 7.55), "R1 10k（b2–b5）", ha="center", fs_=10)
        d += elm.Resistor().at((xp, 0.0)).to((xm, 0.0))
        ls.lab(d, ((xp + xm) / 2, 0.55), "R3 10k（i10–i13）", ha="center", fs_=10)
        d += elm.Dot().at((xm, 7.0)); d += elm.Dot().at((xm, 0.0))
        d += elm.Resistor().at((xm, 7.0)).to((xm, 3.9))
        ls.lab(d, (xm - 0.4, 5.45), "R2 10k\n（c5–c8）", ha="right", fs_=10)
        d += elm.Ground().at((xm, 3.9)).label("0 V", "bottom")
        d += elm.Resistor().at((xm, 0.0)).to((xm, -2.4))
        ls.lab(d, (xm - 0.4, -1.2), "R4 9.1k（h13–h16）", ha="right", fs_=10)
        d += elm.ResistorVar().at((xm, -2.4)).to((xm, -4.8))
        ls.lab(d, (xm - 0.9, -3.6), "RP1 2k 多圈\n（j16 端–j17 滑）", ha="right", fs_=10)
        d += elm.Dot().at((xm, -4.8))
        d += elm.Resistor().at((xm, -4.8)).to((xm, -7.2))
        ls.lab(d, (xm - 0.4, -6.0), "RX（i17–i20）", ha="right", fs_=10)
        d += elm.Dot().at((xm, -7.2))
        d += elm.Line().at((xm, -4.8)).to((xm + 1.0, -4.8)).color(fs.C["vout"])
        d += elm.Line().at((xm + 1.0, -4.8)).to((xm + 1.0, -7.2)).color(fs.C["vout"])
        d += elm.Line().at((xm + 1.0, -7.2)).to((xm, -7.2)).color(fs.C["vout"])
        ls.lab(d, (xm + 1.4, -6.0), "J1（h17–h20）\n调零时插上", fs_=9, color=fs.C["vout"])
        d += elm.Ground().at((xm, -7.2)).label("0 V（j20）", "bottom")
        # INA
        nm = dict(A1="A1", A2="A2", A3="A3", R5="R5 10k（b23–b24）", R6="R6 10k（i22–i23）", RG="RG 1k\n（e28–f28）",
                  R7="R7 10k（e32–f32）", R8="R8 10k（h36–h37）", R9="R9 10k（i33–i38）", R10="R10 10k\n（h38–h46）")
        p = draw_ina(d, -1.0, 0.0, names=nm, x3=None)
        d += elm.Line().at((xm, 7.0)).to(p["a1p"]).color(fs.C["vin"])
        d += elm.Line().at((xm, 0.0)).to(p["a2p"]).color(fs.C["vin"])
        ls.lab(d, (xm + 3.0, 7.35), "蓝线 d5→d25", ha="center", fs_=8.5, color=fs.C["vin"])
        ls.lab(d, (xm + 3.0, 0.35), "蓝线 g13→g24", ha="center", fs_=8.5, color=fs.C["vin"])
        ls.probe(d, (xm, 7.0), "A", dx=0.0, dy=1.1)
        ls.colnote(d, (xm + 0.7, 8.1), "Va 第 5 列", "right", ofst=0.0)
        ls.probe(d, (xm, 0.0), "B", dx=0.0, dy=1.1)
        ls.colnote(d, (xm + 0.7, 1.1), "Vb 第 13 列", "right", ofst=0.0)
        # J2、RC：共模测试才插（虚线）
        xj = xm + 1.9
        d += elm.Line().at((xj, 7.0)).to((xj, 0.0)).linestyle("--").color(fs.C["vin"])
        d += elm.Dot().at((xj, 7.0)); d += elm.Dot().at((xj, 0.0))
        ls.lab(d, (xj + 0.2, 4.6), "J2\n（共模测试）", fs_=8.5, color=fs.C["vin"])
        d += elm.Resistor().at((xj + 1.5, 0.0)).to((xj + 1.5, -2.6)).linestyle("--")
        d += elm.Dot().at((xj + 1.5, 0.0))
        ls.lab(d, (xj + 1.9, -1.3), "RC 4.7k\n（j13→0 V，\n或改接 V+）", fs_=8.5)
        d += elm.Ground().at((xj + 1.5, -2.6))
        decap(d, -15.5, -8.0, "C1", "U1：b22→上 0 V 轨")
        decap(d, -11.0, -8.0, "C2", "U2：b36→上 0 V 轨")
        # 引脚号与芯片
        for key, pin in (("a1p", "5"), ("a1m", "6"), ("a2p", "3"), ("a2m", "2"), ("a3p", "3"), ("a3m", "2")):
            ls._pin(d, p[key], pin, dx=0.3, dy=0.22 if key.endswith("p") and key != "a2p" and key != "a3p" else -0.22)
        ls._pin(d, p["a1o"], "7", dx=-0.3, dy=0.25)
        ls._pin(d, p["a2o"], "1", dx=-0.3, dy=-0.25)
        ls._pin(d, p["a3o"], "1", dx=-0.3, dy=0.25)
        ls.lab(d, (p["a1"].absanchors["center"][0] + 1.5, p["a1p"][1] + 0.9), "U1 B 半边", ha="center", fs_=9, color=ls.GRAY)
        ls.lab(d, (p["a2"].absanchors["center"][0] + 1.5, p["a2p"][1] - 0.9), "U1 A 半边", ha="center", fs_=9, color=ls.GRAY)
        ls.lab(d, (p["a3"].absanchors["center"][0] + 1.5, p["a3p"][1] - 1.0), "U2 A 半边", ha="center", fs_=9, color=ls.GRAY)
        for op, top, bot in ((p["a1"], "8", None), (p["a2"], None, "4"), (p["a3"], "8", "4")):
            vd, vs = op.absanchors["vd"], op.absanchors["vs"]
            # A1 是翻转画的：它的 vd 在下方
            if op is p["a1"]:
                vd, vs = vs, vd
            if top:
                d += elm.Line().at(vd).to((vd[0], vd[1] + 0.5))
                d += elm.Vdd().at((vd[0], vd[1] + 0.5)).label("V+")
                ls._pin(d, vd, top, dx=0.25, dy=0.25)
            if bot:
                d += elm.Line().at(vs).to((vs[0], vs[1] - 0.5))
                d += elm.Ground().at((vs[0], vs[1] - 0.5))
                ls._pin(d, vs, bot, dx=0.25, dy=-0.25)
        ls.colnote(d, (p["xo"] + 0.2, p["a1o"][1] - 0.45), "第 23 列上", "right", ofst=0.0)
        ls.colnote(d, (p["xo"] + 0.2, p["a2o"][1] + 0.45), "第 22 列下", "right", ofst=0.0)
        ls.probe(d, (p["xo"], p["a1o"][1]), "E", dx=0.0, dy=1.0)
        ls.probe(d, (p["xo"], p["a2o"][1]), "F", dx=0.0, dy=-1.0)
        d += elm.Line().at((p["xo3"], p["a3o"][1])).to((p["xo3"] + 0.8, p["a3o"][1]))
        ls.probe(d, (p["xo3"] + 0.8, p["a3o"][1]), "C", dx=0.8)
        ls.colnote(d, (p["xo3"] - 0.2, p["a3o"][1] - 0.9), "Vo 第 36 列下", "right", ofst=0.0)
        yv = p["yref"] - 1.6
        d += elm.Line().at((p["xq"], p["yref"])).to((p["xq"], yv))
        ls.lab(d, (p["xq"] - 0.2, p["yref"] - 0.8), "平时直连\n（h46）", ha="right", fs_=8.5, color=ls.GRAY)
        d += elm.Dot().at((p["xq"], p["yref"]))
        xb = p["xq"] + 1.3
        d += elm.Line().at((p["xq"], p["yref"])).to((xb, p["yref"])).linestyle("--")
        d += elm.Resistor(scale=0.6).at((xb, p["yref"])).to((xb, yv)).linestyle("--")
        d += elm.Line().at((xb, yv)).to((p["xq"], yv)).linestyle("--")
        ls.lab(d, (xb + 0.6, p["yref"] - 0.8), "第 15、16 步：拿掉直连，改串 100 Ω\n（R10 挪到 h38–h45，100 Ω 插 i45–i46）", fs_=8.5)
        d += elm.Dot().at((p["xq"], yv))
        ls.lab(d, (p["xq"] + 0.3, yv - 0.35), "V_MID（第 46 列）", fs_=10, color=fs.C["third"])
        # 中点参考 V_MID：RM1、RM2 分压 + U2 B 半边跟随器
        x0, y0 = p["xq"] - 1.2, p["yref"] - 6.2
        d += elm.Vdd().at((x0 - 2.2, y0 + 3.0)).label("V+")
        d += elm.Resistor().at((x0 - 2.2, y0 + 3.0)).to((x0 - 2.2, y0 + 0.0))
        ls.lab(d, (x0 - 2.6, y0 + 1.5), "RM1 10k\n（b39–b42）", ha="right", fs_=9.5)
        d += elm.Dot().at((x0 - 2.2, y0))
        ls.probe(d, (x0 - 2.2, y0), "G", dx=-1.0, dy=0.0)
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
        ls.lab(d, (o[0] + 1.8, o[1]), "V_MID ≈ 4.5 V\n紫线 d37→g46", fs_=10, color=fs.C["third"])
        ls.probe(d, (o[0] + 1.6, o[1]), "D", dx=0.0, dy=-1.0)
        ls._pin(d, fo.absanchors["in2"], "5", dx=0.3, dy=-0.22)
        ls._pin(d, m_, "6", dx=0.3, dy=0.22)
        ls._pin(d, o, "7", dx=-0.3, dy=0.25)
        ls.lab(d, (fo.absanchors["center"][0] - 0.2, fo.absanchors["center"][1]), "U2B", ha="center", fs_=9)
        ls.lab(d, (o[0] + 0.8, m_[1] + 1.35), "b37–b38 短接", fs_=8.5, color=T)
        for k, line in enumerate((
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；黄色圆圈 A～G = 测量点（字母，别和引脚号混）；灰色小字 = 面包板孔位；小黑字 = LM358 引脚号；所有 V+、0 V 符号各是同一条轨。",
            "测 Vo 时黑表笔接测点 D（V_MID），不接 0 V；虚线 J2、RC 只在第 13～16 步共模测试时插，平时不插。",
            "第 15、16 步：R10 改插 h38–h45，100 Ω 插在 i45–i46，即 R10 下端与 V_MID 之间串 100 Ω（R10 偏 1%，上面虚线画的那只）。",
        )):
            ls.note(d, (-17.0, y0 - 5.0 - 0.6 * k), line)
    print("[图 30-p4-4] 与面包板同名：R1–R10、RG、RP1、RX、J1、J2、RC、RM1、RM2；A1=U1B(5,6,7)，A2=U1A(3,2,1)，A3=U2A，跟随器 U2B")
    save_schem(d, N, "30_p4_4_schem_lab.png")


# ======================================================================================
# 新增（教师审阅）：单运放差分直接接电桥（误区）、比例测量、中点参考原理图、阶段一面包板与对照原理图
# ======================================================================================
def _single_diff(vex, dr, ra, rb, rc, rd, shift=0.0, vref=4.5, r=10e3):
    """电桥两中点看成戴维南源再接四电阻差分（理想运放），返回 Vo − V_MID。与 code/30_sim.py 第 6 节相同。"""
    vta, rta = vex / 2 + shift, r / 2
    vtb, rtb = vex * (r + dr) / (2 * r + dr) + shift, r * (r + dr) / (2 * r + dr)
    vp = (vtb * rd + vref * (rtb + rc)) / (rtb + rc + rd)
    return vp + (vp - vta) * rb / (rta + ra) - vref


def p1_3():
    with drawing(fontsize=11) as d:
        va, vb, _, _ = draw_bridge(d, -9.5, -1.0, h=6.0, w=3.2, meter=False)
        x0 = 0.0
        d += (op := elm.Opamp(leads=True).theta(0).anchor("in2").at((x0, 0.0)))
        inm, inp, out = op.absanchors["in1"], op.absanchors["in2"], op.absanchors["out"]
        xr = x0 - 0.9
        # Va → Ra → 反相端
        xa = vb[0] + 2.3
        d += elm.Line().at(va).to((va[0] + 0.9, va[1])).color(fs.C["vin"])
        d += elm.Line().at((va[0] + 0.9, va[1])).to((va[0] + 0.9, 6.3)).color(fs.C["vin"])
        d += elm.Line().at((va[0] + 0.9, 6.3)).to((xa, 6.3)).color(fs.C["vin"])
        d += elm.Line().at((xa, 6.3)).to((xa, 3.4)).color(fs.C["vin"])
        d += elm.Resistor().at((xa, 3.4)).to((xr, 3.4))
        ls.lab(d, ((xa + xr) / 2, 3.95), "Ra 10k", ha="center", fs_=10)
        d += elm.Dot().at((xr, 3.4))
        d += elm.Line().at((xr, 3.4)).to((xr, inm[1]))
        d += elm.Line().at((xr, inm[1])).to(inm)
        xo = out[0] + 0.7
        d += elm.Resistor().at((xr, 3.4)).to((xo, 3.4))
        ls.lab(d, ((xr + xo) / 2, 3.95), "Rb 100k", ha="center", fs_=10)
        d += elm.Line().at((xo, 3.4)).to((xo, out[1]))
        d += elm.Line().at(out).to((xo + 0.8, out[1]))
        d += elm.Dot().at((xo, out[1]))
        ls.lab(d, (xo + 0.95, out[1]), "Vo", fs_=12, color=fs.C["vout"])
        # Vb → Rc → 同相端，Rd 到 V_MID
        d += elm.Line().at(vb).to((vb[0] + 1.6, vb[1])).color(fs.C["vin"])
        d += elm.Line().at((vb[0] + 1.6, vb[1])).to((vb[0] + 1.6, inp[1])).color(fs.C["vin"])
        xq = xr - 0.5
        d += elm.Resistor().at((vb[0] + 1.6, inp[1])).to((xq, inp[1]))
        ls.lab(d, ((vb[0] + 1.6 + xq) / 2, inp[1] - 0.6), "Rc 10k", ha="center", fs_=10)
        d += elm.Line().at((xq, inp[1])).to(inp)
        d += elm.Dot().at((xq, inp[1]))
        d += elm.Resistor().at((xq, inp[1])).to((xq, inp[1] - 3.0))
        ls.lab(d, (xq + 0.35, inp[1] - 1.5), "Rd 100k", ha="left", fs_=10)
        d += elm.Dot(open=True).at((xq, inp[1] - 3.0))
        ls.lab(d, (xq + 0.3, inp[1] - 3.3), "接 V_MID（4.5 V 中点参考，不是 0 V）", fs_=10, color=fs.C["third"])
        ls.lab(d, (va[0] + 1.1, 5.55), "与上横线交叉不相连", fs_=8, color=ls.GRAY)
        ls.title(d, (x0 + 1.5, 7.2), "16 节的单运放差分（设计 10 倍）直接接电桥")
        d100 = bridge(VEX, R, 100)[0]
        v = _single_diff(VEX, 100, 10e3, 100e3, 10e3, 100e3)
        w = (10.1e3, 99e3, 9.9e3, 101e3)
        dv = _single_diff(VEX, 0, *w, shift=1.5625) - _single_diff(VEX, 0, *w)
        ls.note(d, (-10.5, -4.2), "Ra、Rb、Rc、Rd 就是 16 节四电阻差分放大里的 R1、R2、R3、R4（换个下标，免得和电桥的 R1～R4 混）。")
        ls.note(d, (-10.5, -4.85), "先预测：ΔR = 100 Ω 时 Vo 比 V_MID 高多少？两个中点一起升高时 Vo 动不动？答案在正文里。")
    print(f"[图 30-p1-3] 单运放差分接电桥：ΔR=100 Ω → {v*1e3:.1f} mV（倍数 {v/d100:.2f}）；1% 最坏、共模 +1.56 V → 漂 {dv*1e3:.1f} mV（{dv/v*100:.0f}%）")
    save_schem(d, N, "30_p1_3_single_diff.png")


def follower_left(d, out_xy, label="跟随器"):
    """朝左的电压跟随器：输出在左边 out_xy，返回同相端坐标。反相端直接绕回输出。"""
    d += (fw := elm.Opamp(leads=True).left().anchor("out").at(out_xy))
    A = fw.absanchors
    o, im, ip = A["out"], A["in1"], A["in2"]
    yfb = im[1] + (0.9 if im[1] > ip[1] else -0.9)
    d += elm.Line().at(im).to((im[0], yfb))
    d += elm.Line().at((im[0], yfb)).to((o[0], yfb))
    d += elm.Line().at((o[0], yfb)).to(o)
    d += elm.Dot().at(o)
    ls.lab(d, (A["center"][0] + 0.2, A["center"][1]), label, ha="center", fs_=8.5)
    return ip


def p2_4():
    with drawing(fontsize=11) as d:
        va, vb, top, bot = draw_bridge(d, 0, 0, h=6.0, w=3.2, meter=False, vex="Vex 9 V",
                                       rnames=("R1 10k", "R2 10k", "R3 10k", "R4 + ΔR"))
        ina = elm.Ic(pins=[elm.IcPin(name="−IN", side="left", slot="2/2"), elm.IcPin(name="+IN", side="left", slot="1/2"),
                           elm.IcPin(name="OUT", side="right"), elm.IcPin(name="REF", side="bottom")],
                     size=(3.4, 2.6), label="仪表放大器\nG = 21", lofst=0).right()
        d += ina.at((9.5, 1.6)).anchor("−IN")
        a = ina.absanchors
        d += elm.Line().at(va).to((va[0] + 0.6, va[1])).color(fs.C["vin"])
        d += elm.Line().at((va[0] + 0.6, va[1])).to((va[0] + 0.6, 6.6)).color(fs.C["vin"])
        d += elm.Line().at((va[0] + 0.6, 6.6)).to((8.6, 6.6)).color(fs.C["vin"])
        d += elm.Line().at((8.6, 6.6)).to((8.6, a["−IN"][1])).color(fs.C["vin"])
        d += elm.Line().at((8.6, a["−IN"][1])).to(a["−IN"]).color(fs.C["vin"])
        ls.lab(d, (va[0] + 0.75, 6.25), "交叉不相连", fs_=8, color=ls.GRAY)
        d += elm.Line().at(vb).to((8.0, vb[1])).color(fs.C["vin"])
        d += elm.Line().at((8.0, vb[1])).to((8.0, a["+IN"][1])).color(fs.C["vin"])
        d += elm.Line().at((8.0, a["+IN"][1])).to(a["+IN"]).color(fs.C["vin"])
        d += elm.Line().at(a["REF"]).to((a["REF"][0], a["REF"][1] - 0.6))
        ls.lab(d, (a["REF"][0] + 0.2, a["REF"][1] - 0.9), "接 V_MID（4.5 V）", fs_=9.5, color=fs.C["third"])
        adc = elm.Ic(pins=[elm.IcPin(name="IN", side="left"), elm.IcPin(name="VREF", side="right")],
                     size=(4.6, 2.4), label="模数转换器\n读数 = IN ÷ VREF", lofst=0).right()
        d += adc.at((15.5, a["OUT"][1])).anchor("IN")
        b = adc.absanchors
        d += elm.Line().at(a["OUT"]).to(b["IN"]).color(fs.C["vout"])
        ytop = top[1]
        xd = b["VREF"][0] + 5.6
        d += elm.Line().at(b["VREF"]).to((b["VREF"][0] + 0.6, b["VREF"][1])).color(fs.C["cur"])
        ipf = follower_left(d, (b["VREF"][0] + 0.6, b["VREF"][1]), "跟随器")
        yn = ipf[1]
        d += elm.Line().at((top[0] + 3.2, ytop)).to((xd, ytop)).color(fs.C["cur"])
        d += elm.Dot().at((top[0] + 3.2, ytop))
        d += elm.Resistor().at((xd, ytop)).to((xd, yn))
        ls.lab(d, (xd + 0.4, (ytop + yn) / 2), "Rr1 10k", ha="left", fs_=9.5)
        d += elm.Dot().at((xd, yn))
        d += elm.Resistor().at((xd, yn)).to((xd, yn - 3.0))
        ls.lab(d, (xd + 0.4, yn - 1.5), "Rr2 10k", ha="left", fs_=9.5)
        d += elm.Ground().at((xd, yn - 3.0))
        d += elm.Line().at((xd, yn)).to(ipf).color(fs.C["cur"])
        ls.lab(d, (xd - 4.0, ytop + 0.35), "同一个 Vex", fs_=9.5, color=fs.C["cur"])
        r9 = 21 * 9 * 100 / (2 * 20100) / 4.5
        r8 = 21 * 8 * 100 / (2 * 20100) / 4.0
        ls.note(d, (-1.5, -2.6), f"Vex = 9 V 时 OUT 比 V_MID 高 {21*9*100/(2*20100):.4f} V、VREF = 4.50 V；Vex = 8 V 时 {21*8*100/(2*20100):.4f} V、4.00 V。两次之比都是 {r9:.5f}：激励变了，读数不变。")
        ls.note(d, (-1.5, -3.25), "VREF 输入要求低阻驱动，所以分压后接一个跟随器（12 节）再送进去；模数转换器读的是 OUT 对 V_MID 的差，这里只画出比例关系。")
    assert abs(r9 - r8) < 1e-12
    print(f"[图 30-p2-4] 比例测量：9 V/8 V 激励时 OUT−V_MID 与 VREF 之比都是 {r9:.5f}")
    save_schem(d, N, "30_p2_4_ratiometric.png")


def p2_5():
    with drawing(fontsize=11) as d:
        xb = 0.0
        d += elm.Battery().endpoints((xb, 0.0), (xb, 6.0)).reverse()
        ls.lab(d, (xb - 0.45, 3.0), "9 V\n电池", ha="right", fs_=10)
        d += elm.Line().at((xb, 6.0)).to((3.0, 6.0)).color(fs.C["cur"])
        d += elm.Line().at((xb, 0.0)).to((3.0, 0.0))
        d += elm.Ground().at((xb, 0.0)).label("0 V（GND）", "bottom")
        ls.lab(d, (0.2, 6.4), "V+ = 9 V", fs_=10, color=fs.C["cur"])
        d += elm.Resistor().at((3.0, 6.0)).to((3.0, 3.0))
        ls.lab(d, (2.6, 4.5), "RM1 10k", ha="right", fs_=10)
        d += elm.Dot().at((3.0, 3.0))
        d += elm.Resistor().at((3.0, 3.0)).to((3.0, 0.0))
        ls.lab(d, (2.6, 1.5), "RM2 10k", ha="right", fs_=10)
        d += elm.Dot().at((3.0, 0.0))
        d += (op := elm.Opamp(leads=True).theta(0).anchor("in2").at((5.5, 3.0)))
        ip, im, o = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
        d += elm.Line().at((3.0, 3.0)).to(ip)
        ls.lab(d, (3.2, 2.55), "4.5 V（但带 5 kΩ 内阻）", fs_=9, color=ls.GRAY)
        ls.lab(d, (op.absanchors["center"][0] - 0.2, op.absanchors["center"][1]), "U2B", ha="center", fs_=9)
        d += elm.Line().at(im).to((im[0] - 0.4, im[1]))
        d += elm.Line().at((im[0] - 0.4, im[1])).to((im[0] - 0.4, im[1] + 1.1))
        d += elm.Line().at((im[0] - 0.4, im[1] + 1.1)).to((o[0] + 0.5, im[1] + 1.1))
        d += elm.Line().at((o[0] + 0.5, im[1] + 1.1)).to((o[0] + 0.5, o[1]))
        d += elm.Dot().at((o[0] + 0.5, o[1]))
        d += elm.Line().at(o).to((o[0] + 2.6, o[1])).color(fs.C["third"])
        ls.lab(d, (o[0] + 2.8, o[1]), "V_MID ≈ 4.5 V\n（中点参考，低内阻）", fs_=10, color=fs.C["third"])
        d += elm.Line().at((o[0] + 1.6, o[1])).to((o[0] + 1.6, o[1] - 1.5)).color(fs.C["third"])
        d += elm.Dot().at((o[0] + 1.6, o[1]))
        d += elm.Resistor().at((o[0] + 1.6, o[1] - 1.5)).to((o[0] + 1.6, o[1] - 4.0))
        ls.lab(d, (o[0] + 1.95, o[1] - 2.75), "负载（例如 1 kΩ）", fs_=9, ha="left")
        d += elm.Ground().at((o[0] + 1.6, o[1] - 4.0))
        ls.lab(d, (op.absanchors["center"][0] - 0.2, op.absanchors["center"][1] - 1.8), "运放电源脚（V+、0 V）省略未画", ha="center", fs_=8.5, color=ls.GRAY)
        par = 1e3 * 10e3 / 11e3
        ls.note(d, (-1.5, -1.9), f"只用分压、V_MID 上挂 1 kΩ：中点被拉到 {9*par/(10e3+par):.2f} V；加跟随器后仍是 4.5 V（跟随器供出 4.5 mA）。")
        ls.note(d, (-1.5, -2.55), "V_MID 是中点参考，不是 GND：量信号时黑表笔接 V_MID；V_MID 与 0 V 之间永远有 4.5 V，千万别把 V_MID 和 0 V 短接。")
    print(f"[图 30-p2-5] 中点参考：分压 + 跟随；只分压挂 1 kΩ → {9*par/(10e3+par):.2f} V")
    save_schem(d, N, "30_p2_5_vground.png")


def p4_1():
    W = bb.BB_WIRE
    rails = {"T1": ("V+（9 V）", W["pos"]), "T2": ("0 V", W["gnd"]), "B1": ("0 V", W["gnd"]), "B2": ("V+（9 V）", W["pos"])}
    fig, ax = bb.bb_board(46, rails, figsize=(13.6, 5.4))
    bb.bb_wire(ax, "T2-1", "B1-1", "gnd", via=[(-0.4, 10.8), (-0.4, -2.8)])
    bb.bb_wire(ax, "T1-1", "B2-1", "pos", via=[(-0.9, 11.6), (-0.9, -3.6)])
    bb.bb_dip8(ax, 36, "U2 LM358")
    bb.bb_wire(ax, "a36", "T1-36", "pos")
    bb.bb_wire(ax, "j39", "B1-39", "gnd")
    bb.bb_part2(ax, "b36", "T2-35", "", kind="box", dy=0.0, fc="#f2c94c")
    bb._bb_label(ax, 34.0, 8.5, "C2 0.1µ", fs_=6.5)
    bb.bb_wire(ax, "b37", "b38", "fb")
    bb.bb_res(ax, "b39", "b42", "RM1 10k")
    bb.bb_wire(ax, "a42", "T1-42", "pos")
    bb.bb_res(ax, "c39", "c44", "RM2 10k", dy=-0.5)
    bb.bb_wire(ax, "a44", "T2-44", "gnd")
    bb.bb_wire(ax, "d37", "g46", "neg", via=[(37, 6.5), (46, 6.5)])
    bb._bb_label(ax, 43.5, 4.3, "紫线 = V_MID")
    # 第 3 步临时插的负载 RL（虚线框）
    bb.bb_res(ax, "i46", "B1-46", "", dy=0.55)
    bb._bb_label(ax, 44.2, -0.9, "RL 1k", fs_=7)
    ax.add_patch(bb._BbRect((45.4, -3.2), 1.2, 4.5, fc="none", ec="0.35", lw=0.9, ls=(0, (3, 2)), zorder=6))
    ax.add_patch(bb._BbRect((3.2, 12.9), 4.0, 0.75, fc="#ffe082", ec="0.3", lw=0.8, zorder=5))
    ax.text(5.2, 13.27, "9 V 电池", ha="center", va="center", fontsize=7.5, zorder=6)
    ax.plot([4.0, 4.0], [12.9, 11.6], color=W["pos"], lw=2.0, zorder=3); ax.plot(4, 11.6, "o", ms=4, color=W["pos"], zorder=4)
    ax.plot([6.4, 6.4], [12.9, 10.8], color=W["gnd"], lw=2.0, zorder=3); ax.plot(6.4, 10.8, "o", ms=4, color=W["gnd"], zorder=4)
    ax.text(3.6, 13.27, "+", ha="right", va="center", fontsize=9, color=W["pos"])
    ax.text(6.8, 13.27, "−", ha="left", va="center", fontsize=9)
    ax.text(9.0, 13.27, "阶段一只搭中点参考：U2 和 RM1、RM2 的位置与阶段二完全相同，后面不用拆；虚线框里的 RL 只在第 3 步临时插",
            ha="left", va="center", fontsize=8)
    bb.bb_probe(ax, "g46", "D", dx=1.0, dy=0.6)
    bb.bb_probe(ax, "d39", "G", dx=-0.9, dy=0.6)
    ax.set_ylim(-5.9, 14.0)
    bb.bb_legend(ax, [("pos", "红：V+"), ("gnd", "黑：0 V"), ("neg", "紫：V_MID 中点参考"), ("fb", "绿：跟随器反馈")], x=1.0, y=-4.75)
    print("[图 30-p4-1] 阶段一：U2 第 36 列，RM1 b39–b42，RM2 c39–c44，b37–b38 短接，V_MID = d37→g46；RL i46→下 0 V 轨（第 3 步临时）")
    fs.save(fig, N, "30_p4_1_bb_vground.png")


def p4_2():
    T = ls.TEAL
    with drawing(fontsize=11) as d:
        ls.title(d, (4.0, 7.6), "阶段一：中点参考 V_MID（U2 的 B 半边接成跟随器）")
        xb = 0.0
        d += elm.Battery().endpoints((xb, 0.0), (xb, 6.0)).reverse()
        ls.lab(d, (xb - 0.45, 3.0), "9 V\n电池", ha="right", fs_=10)
        d += elm.Line().at((xb, 6.0)).to((3.0, 6.0))
        d += elm.Line().at((xb, 0.0)).to((3.0, 0.0))
        d += elm.Ground().at((xb, 0.0)).label("0 V", "bottom")
        ls.colnote(d, (xb + 0.1, 6.25), "V+ 轨（a42 接上轨）", "top", ofst=0.0)
        d += elm.Resistor().at((3.0, 6.0)).to((3.0, 3.0))
        ls.lab(d, (2.6, 4.5), "RM1 10k\n（b39–b42）", ha="right", fs_=9.5)
        d += elm.Dot().at((3.0, 3.0))
        d += elm.Resistor().at((3.0, 3.0)).to((3.0, 0.0))
        ls.lab(d, (2.6, 1.5), "RM2 10k\n（c39–c44）", ha="right", fs_=9.5)
        ls.colnote(d, (3.1, -0.25), "a44 接 0 V 轨", "bottom", ofst=0.0)
        d += (op := elm.Opamp(leads=True).theta(0).anchor("in2").at((5.5, 3.0)))
        ip, im, o = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
        d += elm.Line().at((3.0, 3.0)).to(ip)
        ls.probe(d, (3.0, 3.0), "G", dx=-0.9, dy=-0.6)
        ls.colnote(d, (3.3, 3.25), "第 39 列上", "top", ofst=0.0)
        ls.lab(d, (op.absanchors["center"][0] - 0.2, op.absanchors["center"][1]), "U2B", ha="center", fs_=9)
        d += elm.Line().at(im).to((im[0] - 0.4, im[1]))
        d += elm.Line().at((im[0] - 0.4, im[1])).to((im[0] - 0.4, im[1] + 1.1))
        d += elm.Line().at((im[0] - 0.4, im[1] + 1.1)).to((o[0] + 0.5, im[1] + 1.1))
        d += elm.Line().at((o[0] + 0.5, im[1] + 1.1)).to((o[0] + 0.5, o[1]))
        ls.lab(d, (im[0] - 0.5, im[1] + 1.45), "b37–b38 短接", fs_=8.5, color=T, ha="right")
        ls.lab(d, (op.absanchors["vd"][0] + 0.15, im[1] + 1.4), "交叉不相连", fs_=8, color=ls.GRAY)
        d += elm.Dot().at((o[0] + 0.5, o[1]))
        ls._pin(d, ip, "5", dx=0.3, dy=-0.22)
        ls._pin(d, im, "6", dx=0.3, dy=0.22)
        ls._pin(d, o, "7", dx=-0.3, dy=0.25)
        vd_, vs_ = op.absanchors["vd"], op.absanchors["vs"]
        d += elm.Line().at(vd_).to((vd_[0], vd_[1] + 1.7)); d += elm.Vdd().at((vd_[0], vd_[1] + 1.7)).label("V+")
        ls._pin(d, vd_, "8", dx=0.25, dy=0.25)
        d += elm.Line().at(vs_).to((vs_[0], vs_[1] - 0.5)); d += elm.Ground().at((vs_[0], vs_[1] - 0.5))
        ls._pin(d, vs_, "4", dx=0.25, dy=-0.25)
        xm = o[0] + 2.8
        d += elm.Line().at(o).to((xm, o[1])).color(fs.C["third"])
        ls.colnote(d, (o[0] + 0.7, o[1] + 0.25), "紫线 d37→g46", "top", ofst=0.0)
        d += elm.Dot().at((xm, o[1]))
        ls.probe(d, (xm, o[1]), "D", dx=0.9, dy=0.6)
        ls.lab(d, (xm + 0.3, o[1] - 0.45), "V_MID（第 46 列）", fs_=10, color=fs.C["third"])
        d += elm.Resistor().at((xm, o[1])).to((xm, o[1] - 3.0)).linestyle("--")
        ls.lab(d, (xm + 0.35, o[1] - 1.6), "RL 1k（第 3 步临时，\ni46→下 0 V 轨）", fs_=9, ha="left")
        d += elm.Ground().at((xm, o[1] - 3.0))
        decap(d, -3.2, 2.6, "C2", "U2：b36→\n上 0 V 轨")
        ls.note(d, (-1.5, -2.2), "读图：一条线 = 一个节点；黄色圆圈 = 测量点（用字母编号）；灰色小字 = 面包板孔位；小黑字 = LM358 引脚号；测点 D、G 都对 0 V 量。")
        ls.note(d, (-1.5, -2.85), "U2 的 A 半边（1、2、3 脚）阶段二才用，现在空着没关系。")
    print("[图 30-p4-2] 阶段一对照原理图：RM1、RM2、U2B（5、6、7 脚）、RL、测点 D、G")
    save_schem(d, N, "30_p4_2_schem_vground.png")


def p3_0():
    """RG 错接：A1 的反相端经 RG 到 0 V，A2 变成跟随器（page3 第一节，图 30-p3-1）。"""
    va, vb = 4.5, 4.5 + bridge(VEX, R, 100)[0]
    g1 = 1 + 10e3 / 1e3
    want = g1 * va
    vsat = VEX - 1.5
    with drawing(fontsize=11) as d:
        d += (a1 := elm.Opamp(leads=True).theta(0).anchor("in2").at((0, 4.0)))
        d += (a2 := elm.Opamp(leads=True).theta(0).anchor("in2").at((0, -1.5)))
        for op, nm, v, rn in ((a1, "A1", va, "R5 10k"), (a2, "A2", vb, "R6 10k")):
            A = op.absanchors
            ls.lab(d, (A["center"][0] - 0.2, A["center"][1]), nm, ha="center", fs_=10)
            if nm == "A1":   # 输入线从下面绕过来，避开 RG
                xi, yi = A["in2"][0] - 0.25, A["in2"][1] - 2.3
                d += elm.Line().at(A["in2"]).to((xi, A["in2"][1])).color(fs.C["vin"])
                d += elm.Line().at((xi, A["in2"][1])).to((xi, yi)).color(fs.C["vin"])
                d += elm.Line().at((xi, yi)).to((xi - 1.6, yi)).color(fs.C["vin"])
                ls.lab(d, (xi - 1.75, yi), f"Va {v:.2f} V", ha="right", fs_=10, color=fs.C["vin"])
            else:
                d += elm.Line().at(A["in2"]).to((A["in2"][0] - 1.2, A["in2"][1])).color(fs.C["vin"])
                ls.lab(d, (A["in2"][0] - 1.35, A["in2"][1]), f"Vb {v:.2f} V", ha="right", fs_=10, color=fs.C["vin"])
            xn, xo = A["in1"][0] - (1.0 if nm == "A1" else 0.5), A["out"][0] + 0.6
            yf = A["in1"][1] + 1.2
            d += elm.Line().at(A["in1"]).to((xn, A["in1"][1]))
            d += elm.Line().at((xn, A["in1"][1])).to((xn, yf))
            d += elm.Resistor(scale=0.8).at((xn, yf)).to((xo, yf))
            ls.lab(d, ((xn + xo) / 2, yf + 0.5), rn, ha="center", fs_=9.5)
            d += elm.Line().at((xo, yf)).to((xo, A["out"][1]))
            d += elm.Line().at(A["out"]).to((xo + 0.8, A["out"][1])); d += elm.Dot().at((xo, A["out"][1]))
            if nm == "A1":
                d += elm.Dot().at((xn, A["in1"][1]))
                d += elm.Resistor(scale=0.6).at((xn, A["in1"][1])).to((xn, A["in1"][1] - 1.8)).color(fs.C["bad"])
                ls.lab(d, (xn - 0.35, A["in1"][1] - 0.9), "RG 1k\n（错接到 0 V）", ha="right", fs_=9.5, color=fs.C["bad"])
                d += elm.Ground().at((xn, A["in1"][1] - 1.8))
                ls.lab(d, (xo + 0.95, A["out"][1]), f"想要 1 + R5/RG = {g1:.0f} 倍 × {va:.1f} V = {want:.1f} V\n实际顶在约 {vsat:.1f} V 不动", fs_=9.5, color=fs.C["bad"])
            else:
                ls.lab(d, (xo + 0.95, A["out"][1]), f"反相端只经 R6 接自己的输出：\n变成跟随器，输出 = Vb = {vb:.3f} V", fs_=9.5)
        ls.note(d, (-3.0, -4.2), "对比图 30-p2-2：RG 不再跨在两个反相端之间，两路倍数不一样，共模（4.5 V）也被 A1 放大，输出被顶到头。")
    print(f"[图 30-p3-1] RG 错接到 0 V：A1 想要 {g1:.0f}×{va} = {want:.1f} V，被限在约 {vsat:.1f} V；A2 跟随器 {vb:.4f} V")
    save_schem(d, N, "30_p3_1_rg_miswire.png")


def p4_6():
    """思考题 3：R10 下端接到分压中点（第 39 列）而不是 V_MID。"""
    rth = 10e3 * 10e3 / 20e3
    r10e = 10e3 + rth
    acm = acm_exact(10e3, 10e3, 10e3, r10e)
    with drawing(fontsize=11) as d:
        d += (a3 := elm.Opamp(leads=True).theta(0).anchor("in2").at((0, 0)))
        A = a3.absanchors
        ls.lab(d, (A["center"][0] - 0.2, A["center"][1]), "A3", ha="center", fs_=10)
        xr = A["in2"][0] - 0.9
        d += elm.Resistor(scale=0.8).at((xr - 3.0, A["in1"][1])).to((xr, A["in1"][1]))
        ls.lab(d, (xr - 1.5, A["in1"][1] + 0.5), "R7 10k", ha="center", fs_=9.5)
        d += elm.Line().at((xr, A["in1"][1])).to(A["in1"]); d += elm.Dot().at((xr, A["in1"][1]))
        ls.lab(d, (xr - 3.15, A["in1"][1]), "A1 输出", ha="right", fs_=9.5)
        xo = A["out"][0] + 0.6
        d += elm.Line().at((xr, A["in1"][1])).to((xr, A["in1"][1] + 1.3))
        d += elm.Resistor(scale=0.8).at((xr, A["in1"][1] + 1.3)).to((xo, A["in1"][1] + 1.3))
        ls.lab(d, ((xr + xo) / 2, A["in1"][1] + 1.8), "R8 10k", ha="center", fs_=9.5)
        d += elm.Line().at((xo, A["in1"][1] + 1.3)).to((xo, A["out"][1]))
        d += elm.Line().at(A["out"]).to((xo + 0.8, A["out"][1])); d += elm.Dot().at((xo, A["out"][1]))
        ls.lab(d, (xo + 0.95, A["out"][1]), "Vo", fs_=11, color=fs.C["vout"])
        d += elm.Resistor(scale=0.8).at((xr - 3.0, A["in2"][1])).to((xr, A["in2"][1]))
        ls.lab(d, (xr - 1.5, A["in2"][1] - 0.5), "R9 10k", ha="center", fs_=9.5)
        ls.lab(d, (xr - 3.15, A["in2"][1]), "A2 输出", ha="right", fs_=9.5)
        d += elm.Line().at((xr, A["in2"][1])).to(A["in2"]); d += elm.Dot().at((xr, A["in2"][1]))
        yg = A["in2"][1] - 3.0
        d += elm.Resistor(scale=0.8).at((xr, A["in2"][1])).to((xr, yg))
        ls.lab(d, (xr + 0.3, A["in2"][1] - 1.5), "R10 10k", fs_=9.5)
        d += elm.Dot().at((xr, yg))
        ls.probe(d, (xr, yg), "G", dx=0.9, dy=0.0)
        xm = xr - 2.6
        d += elm.Line().at((xr, yg)).to((xm, yg)).color(fs.C["bad"])
        ls.lab(d, ((xr + xm) / 2, yg + 0.35), "错：接第 39 列", ha="center", fs_=9, color=fs.C["bad"])
        d += elm.Resistor(scale=0.6).at((xm, yg)).to((xm, yg + 1.7))
        d += elm.Vdd().at((xm, yg + 1.7)).label("V+")
        d += elm.Resistor(scale=0.8).at((xm, yg)).to((xm, yg - 2.4))
        d += elm.Ground().at((xm, yg - 2.4))
        d += elm.Dot().at((xm, yg))
        ls.lab(d, (xm - 0.3, yg + 0.85), "RM1 10k", ha="right", fs_=9.5)
        ls.lab(d, (xm - 0.3, yg - 1.2), "RM2 10k", ha="right", fs_=9.5)
        # 等效电路
        xe = xo + 4.0
        ls.title(d, (xe + 1.5, 3.2), "从 R10 往下看，等效成：")
        d += elm.Resistor(scale=0.8).at((xe, 2.0)).to((xe, 0.0))
        ls.lab(d, (xe + 0.3, 1.0), "R10 10k", fs_=9.5)
        d += elm.Resistor(scale=0.8).at((xe, 0.0)).to((xe, -2.0)).color(fs.C["bad"])
        ls.lab(d, (xe + 0.3, -1.0), f"RM1∥RM2 = {rth/1e3:.0f} kΩ", fs_=9.5, color=fs.C["bad"])
        d += elm.Dot(open=True).at((xe, -2.0))
        ls.lab(d, (xe + 0.3, -2.3), "4.5 V", fs_=9.5)
        ls.lab(d, (xe - 0.3, 2.2), f"合起来 {r10e/1e3:.0f} kΩ，比 R8 大 50%", ha="right", fs_=9.5, color=fs.C["bad"])
        ls.note(d, (-6.5, yg - 3.4), f"R10 实际变成 {r10e/1e3:.0f} kΩ：共模倍数 = {acm:.2f}，差分级 CMRR 只剩约 {20*math.log10(1/acm):.0f} dB；R10 的电流还会拉动第 39 列。")
    print(f"[图 30-p4-6] R10 接分压中点：等效 {r10e/1e3:.0f} kΩ，Acm = {acm:.3f}，差分级 CMRR {20*math.log10(1/acm):.1f} dB")
    save_schem(d, N, "30_p4_6_ref_divider.png")


if __name__ == "__main__":
    import sys as _s
    want = _s.argv[1:]
    for f in [k for k in list(globals()) if k.startswith("p") and k[1:2].isdigit()]:
        if not want or f in want:
            globals()[f]()
