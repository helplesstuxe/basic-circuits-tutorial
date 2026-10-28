"""41 4–20 mA 电流环：全部配图。运行（仓库根目录）：/workspace/circuits-venv/bin/python code/figs/41_figs.py
数字来自 code/41_sim.py（公式 + 简化模型）和 spice/41/*.cir（ngspice，TI LM358 + onsemi 2N3904 模型）；本脚本会打印图上标的数。
面包板类 Breadboard、run_spice 从 code/figs/35_figs.py 导入（不修改那个文件）。"""
import os, sys, io, contextlib, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import figstyle as fs
from batt_pm import pm as bat_pm        # 电池旁的 + / − 小字（长线 = +）
from figstyle import C
import schem
from schem import elm
import lab_schem as L

P = "41"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


F35 = _load("figs35", "code/figs/35_figs.py")
Breadboard, BB_RAIL_Y, BB_WIRE, run_spice = F35.Breadboard, F35.BB_RAIL_Y, F35.BB_WIRE, F35.run_spice
S = _load("sim41", "code/41_sim.py")


def LSk(k):
    return dict(fs.LS[k])


# ======================================================================
# page1
# ======================================================================
def p1_1_error():
    """图 41-p1-1：同一段导线，电压传输（接收端输入电阻 10 kΩ / 1 kΩ）和 24 V 电流环（250 Ω 接收）的读数误差。"""
    rw = np.linspace(0, 800, 801)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(rw, S.err_voltage(rw, 10e3), **LSk("vin"), label="电压传输，接收端输入电阻 10 kΩ")
    ax.plot(rw, S.err_voltage(rw, 1e3), **LSk("vout"), label="电压传输，接收端输入电阻 1 kΩ")
    ec = S.err_current(rw, 24.0, S.XTR115_VMIN, r_rx=250)
    ax.plot(rw, ec, **LSk("fb"), label="4–20 mA 电流环（24 V 电源，250 Ω 接收，20 mA）")
    rk = 2 * S.r_wire(1000)
    ax.axvline(rk, **LSk("ref"))
    ax.text(rk + 8, 24, f"1 km 长的两芯线\n（0.2 mm² 铜）≈ {rk:.0f} Ω", fontsize=8)
    fs.mark(ax, rk, S.err_voltage(rk, 10e3), "{:.2f}", " %", dx=15, dy=-4)
    fs.mark(ax, rk, S.err_voltage(rk, 1e3), "{:.2f}", " %", dx=15, dy=-4)
    knee = (24.0 - S.XTR115_VMIN) / 0.020 - 250
    ax.plot([knee], [0.0], "o", color="k", ms=5)
    ax.text(knee - 15, 2.0, f"{knee:.0f} Ω", ha="right", fontsize=9)
    ax.annotate("电流环在这之前误差都是 0；\n超过它，电源电压不够了", xy=(knee, 0.5), xytext=(600, 18), fontsize=8,
                arrowprops=dict(arrowstyle="->", lw=0.8))
    print(f"[图 41-p1-1] 1 km 双线 {rk:.1f} Ω：10 kΩ 输入误差 {S.err_voltage(rk, 10e3):.2f} %，1 kΩ 输入 {S.err_voltage(rk, 1e3):.2f} %；电流环拐点 {knee:.0f} Ω")
    fs.axlabels(ax, "两根导线的总电阻", "Ω", "读数偏低", "%")
    ax.set_xlim(0, 800); ax.set_ylim(-1, 45)
    ax.legend(loc="upper left", fontsize=7.5)
    fs.save(fig, P, "41_p1_1_error.png")


def p1_4_ne43():
    """图 41-p1-4：NAMUR NE43 的电流分区（取自 Beckhoff、WAGO 手册），并标出本节 Arduino 能发出的几个电流。"""
    fig, ax = plt.subplots(figsize=(7, 2.4))
    zones = [(0, 3.6, "故障（低）\n≤ 3.6", C["bad"], 0.35), (3.6, 3.8, "", "0.75", 0.5), (3.8, 4.0, "", C["fb"], 0.2),
             (4.0, 20.0, "测量值 4–20 mA", C["fb"], 0.45), (20.0, 20.5, "", C["fb"], 0.2), (20.5, 21.0, "", "0.75", 0.5),
             (21.0, 24.0, "故障（高）\n≥ 21", C["bad"], 0.35)]
    for a, b, t, c, al in zones:
        ax.axvspan(a, b, ymin=0.25, ymax=0.75, color=c, alpha=al, lw=0)
        if t:
            ax.text((a + b) / 2, 0.55, t, ha="center", va="center", fontsize=8.5)
    ax.annotate("3.6–3.8\n过渡", xy=(3.7, 0.25), xytext=(6.3, 0.05), fontsize=7.5, ha="center", arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.annotate("20.5–21\n过渡", xy=(20.75, 0.25), xytext=(17.6, 0.05), fontsize=7.5, ha="center", arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.text(12.0, 0.33, "3.8–4 和 20–20.5 是超量程，仍算测量值（浅色）", ha="center", fontsize=7.5)
    pts = ((38, "analogWrite(38)"), (45, "45"), (224, "224"), (255, "255"))
    for code, txt in pts:
        i = S.vset_of(code) / S.R_S * S.BETA / (S.BETA + 1) * 1e3      # 全部用 β = 100 模型值
        ax.plot([i], [0.75], "v", color="k", ms=7)
        dx = {38: -1.3, 45: 1.3}.get(code, 0.0)
        ax.text(i + dx, 0.80, f"{txt}\n{i:.2f} mA", ha="center", va="bottom", fontsize=7.5)
        print(f"[图 41-p1-4] code {code}：回路电流 {i:.2f} mA → {S.ne43(i)}")
    ax.set_xlim(0, 24); ax.set_ylim(0, 1.25); ax.set_yticks([])
    fs.axlabels(ax, "回路电流", "mA")
    fs.save(fig, P, "41_p1_4_ne43.png")


def p1_2_loop():
    """图 41-p1-2：两线制电流环方框图：电源、变送器、导线、接收电阻串成一个圈，处处同一个电流。"""
    fig, ax = fs.diagram(9.0, 3.4)
    ps = fs.box(ax, 1.2, 1.7, "回路电源\n24 V（工厂）\n12 V（本节）", w=1.8, h=1.0, fs=8.5)
    tx = fs.box(ax, 7.6, 2.6, "变送器（两线制）\n传感器 + 恒流源\n例：XTR115", w=2.2, h=1.0, fc=C["fill2"], fs=8.5)
    rx = fs.box(ax, 7.6, 0.75, "接收电阻 250 Ω\n1–5 V 送 ADC", w=2.2, h=0.8, fs=8.5)
    fs.arrow(ax, (ps["r"][0], 2.0), (tx["l"][0], 2.6), "导线（几十米到上千米）", fs=8, color=C["cur"])
    fs.arrow(ax, (tx["b"][0] + 0.6, tx["b"][1]), (rx["t"][0] + 0.6, rx["t"][1]), None, color=C["cur"])
    fs.arrow(ax, (rx["l"][0], 0.75), (ps["r"][0], 1.4), "回线", fs=8, color=C["cur"])
    ax.text(4.5, 1.75, "整个圈里只有一个电流 I\n4 mA = 量程下限，20 mA = 上限\n导线电阻只吃掉电压，不改 I", ha="center",
            va="center", fontsize=8.5, color=C["cur"])
    fs.save(fig, P, "41_p1_2_loop.png")


def _tx_box(d, x0, y0, x1, y1, text, fs_=9.5):
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        d += elm.Line().endpoints(a, b).linewidth(1.4)
    L.lab(d, ((x0 + x1) / 2, (y0 + y1) / 2), text, ha="center", fs_=fs_)


def _bat(d, x, yb, yt, text):
    """竖放的电源：上端 +，下端 −（两端都画真实导线，不用接地符号）。"""
    d += (bt := elm.Battery().at((x, yb)).to((x, yt)).reverse())
    bat_pm(d, bt, plus_toward=(x, yt), side=-1)
    L.lab(d, (x - 0.45, (yb + yt) / 2), text, ha="right", fs_=10)


def p1_3_wires():
    """图 41-p1-3：两线制与四线制变送器的接法对比（原理图）。"""
    cur = dict(color=C["cur"])
    with schem.drawing(fontsize=10) as d:
        # 左：两线制
        L.title(d, (3.5, 5.3), "两线制：2 根线，既供电又传信号")
        _bat(d, 0, 0, 3, "24 V")
        for a, b in (((0, 3), (0, 4)), ((0, 4), (3, 4)), ((5, 4), (7, 4)), ((7, 0), (0, 0))):
            d += elm.Line().at(a).to(b).color(C["cur"]).linewidth(2.0)
        _tx_box(d, 3, 3.4, 5, 4.6, "变送器\n+　　−", fs_=9)
        d += elm.Resistor().at((7, 4)).to((7, 0)).color(C["vin"])
        L.lab(d, (7.4, 2.0), "250 Ω\n接收", fs_=10, color=C["vin"])
        L.lab(d, (3.5, 1.2), "同一个电流 I\n4–20 mA 表示读数", ha="center", fs_=9.5, color=C["cur"])
        # 右：四线制
        x = 11
        L.title(d, (x + 3.8, 5.3), "四线制：2 根供电 + 2 根信号")
        _bat(d, x, 0, 3, "24 V")
        for a, b in (((x, 3), (x, 4)), ((x, 4), (x + 3, 4)), ((x, 0), (x + 3, 0))):
            d += elm.Line().at(a).to(b)
        _tx_box(d, x + 3, -0.3, x + 5, 4.3, "变送器\n\n自己\n有电源", fs_=9)
        L.lab(d, (x + 3.1, 4.0), "V+", fs_=8.5); L.lab(d, (x + 3.1, 0.0), "0 V", fs_=8.5)
        L.lab(d, (x + 4.9, 3.0), "OUT+", ha="right", fs_=8.5); L.lab(d, (x + 4.9, 1.0), "OUT−", ha="right", fs_=8.5)
        for a, b in (((x + 5, 3), (x + 7, 3)), ((x + 7, 1), (x + 5, 1))):
            d += elm.Line().at(a).to(b).color(C["cur"]).linewidth(2.0)
        d += elm.Resistor().at((x + 7, 3)).to((x + 7, 1)).color(C["vin"])
        L.lab(d, (x + 7.4, 2.0), "250 Ω\n接收", fs_=10, color=C["vin"])
        L.lab(d, (x + 1.5, -1.0), "供电回路和信号回路分开", ha="center", fs_=9.5)
        schem.save_schem(d, P, "41_p1_3_wires.png")


# ======================================================================
# page2
# ======================================================================
def _sender(d, lab=False, a1=True):
    """电压→电流发送器原理图（p2_2 和 p4_2 共用）。a1=True 画 A1 的 22k/10k 分压；lab=True 时再加测量点。"""
    # PWM 输入 + 12k/10k + 10 µF
    xs, ys = 2.6, 2.0
    d += elm.Dot(open=True).at((-1.6, ys)).label("Arduino D9\nPWM 0/5 V", "left")
    d += elm.Resistor().at((-1.6, ys)).to((xs, ys))
    L.lab(d, (0.5, ys + 0.5), "R1 12 kΩ", ha="center", fs_=10)
    d += elm.Dot().at((xs, ys))
    d += elm.Resistor().at((xs, ys)).to((xs, ys - 2.6))
    d += elm.Ground().at((xs, ys - 2.6))
    L.lab(d, (xs - 0.4, ys - 1.3), "R2\n10 kΩ", ha="right", fs_=10)
    d += elm.Line().at((xs, ys)).to((xs + 1.3, ys))
    d += elm.Capacitor().at((xs + 1.3, ys)).to((xs + 1.3, ys - 2.6))
    d += elm.Ground().at((xs + 1.3, ys - 2.6))
    L.lab(d, (xs + 1.75, ys - 1.3), "C1\n10 µF", fs_=10)
    d += elm.Dot().at((xs + 1.3, ys))
    # 运放（+ 在下）
    op = elm.Opamp(leads=True).right().flip().anchor("in2").at((xs + 4.4, ys))
    d += op
    pp, pm, po = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
    d += elm.Line().at((xs + 1.3, ys)).to(pp)
    L.lab(d, (xs + 1.5, ys + 0.3), "$V_{SET}$", fs_=10, color=C["vin"])
    L.lab(d, (op.absanchors["center"][0] - 0.6, ys + 1.9), "LM358（A 半）\n8 脚 +12 V，4 脚地", ha="center", fs_=9)
    # R_B → 基极
    xb = po[0] + 2.6
    d += elm.Resistor().at(po).to((xb, po[1]))
    L.lab(d, ((po[0] + xb) / 2, po[1] + 0.5), "R_B 1 kΩ", ha="center", fs_=10)
    q = elm.BjtNpn(circle=True).anchor("base").at((xb, po[1]))
    d += q
    qc, qe = q.absanchors["collector"], q.absanchors["emitter"]
    L.lab(d, (qc[0] + 0.5, po[1]), "Q1 2N3904", fs_=10)
    # 回路：+12 V → R_x → 250 Ω → 集电极
    ytop = qc[1] + 5.0
    d += elm.Vdd().at((qc[0], ytop)).label("+12 V")
    d += elm.Resistor().at((qc[0], ytop)).to((qc[0], ytop - 2.2))
    L.lab(d, (qc[0] + 0.45, ytop - 1.1), "R_x（导线电阻）\n0 / 100 / 220 / 470 Ω", fs_=9.5)
    d += elm.Resistor().at((qc[0], ytop - 2.2)).to((qc[0], ytop - 4.4)).color(C["cur"])
    L.lab(d, (qc[0] + 0.45, ytop - 3.3), "250 Ω 接收电阻\n（只用万用表量）", fs_=9.5, color=C["cur"])
    d += elm.Line().at((qc[0], ytop - 4.4)).to(qc)
    # 发射极 → R_S → 地；→ 运放 −
    ye = qe[1] - 1.0
    d += elm.Line().at(qe).to((qe[0], ye))
    d += elm.Dot().at((qe[0], ye))
    d += elm.Resistor().at((qe[0], ye)).to((qe[0], ye - 2.4))
    d += elm.Ground().at((qe[0], ye - 2.4))
    L.lab(d, (qe[0] + 0.45, ye - 1.2), "R_S 100 Ω", fs_=10)
    xm = pm[0] - 0.5
    d += elm.Line().at(pm).to((xm, pm[1]))
    # 反馈线：− 端 → 下绕到发射极
    if not a1:
        d += elm.Line().at((xm, pm[1])).to((xm, ye)).color(C["fb"])
        d += elm.Line().at((xm, ye)).to((qe[0], ye)).color(C["fb"])
        L.lab(d, ((xm + qe[0]) / 2, ye - 0.45), "负反馈：$V_E$ 被拉到 $V_{SET}$", ha="center", fs_=9, color=C["fb"])
    else:   # 实验图：反馈线从 A1 分压下方绕过去，不与它交叉
        yb, xr = po[1] - 6.8, qe[0] - 0.9
        for p0, p1 in (((xm, pm[1]), (xm, yb)), ((xm, yb), (xr, yb)), ((xr, yb), (xr, ye)), ((xr, ye), (qe[0], ye))):
            d += elm.Line().at(p0).to(p1).color(C["fb"])
        L.lab(d, ((xm + xr) / 2, yb - 0.45), "负反馈：2 脚接发射极，$V_E$ 被拉到 $V_{SET}$", ha="center", fs_=9, color=C["fb"])
    # A0 经 10 kΩ
    xa = qe[0] + 2.8
    d += elm.Line().at((qe[0], ye)).to((qe[0] + 0.6, ye))
    d += elm.Resistor().at((qe[0] + 0.6, ye)).to((xa, ye))
    L.lab(d, ((qe[0] + 0.6 + xa) / 2, ye + 0.5), "10 kΩ", ha="center", fs_=10)
    d += elm.Dot(open=True).at((xa, ye)).label("Arduino A0", "right")
    if a1:
        # A1：运放输出经 22k/10k
        xo = po[0] + 0.8
        d += elm.Dot().at((xo, po[1]))
        d += elm.Line().at((xo, po[1])).to((xo, po[1] - 1.0))
        d += elm.Resistor().at((xo, po[1] - 1.0)).to((xo, po[1] - 3.4))
        L.lab(d, (xo + 0.4, po[1] - 2.2), "22 kΩ", fs_=9.5)
        d += elm.Dot().at((xo, po[1] - 3.4))
        d += elm.Resistor().at((xo, po[1] - 3.4)).to((xo, po[1] - 5.8))
        d += elm.Ground().at((xo, po[1] - 5.8))
        L.lab(d, (xo + 0.4, po[1] - 4.6), "10 kΩ", fs_=9.5)
        d += elm.Line().at((xo, po[1] - 3.4)).to((xo - 1.2, po[1] - 3.4))
        d += elm.Dot(open=True).at((xo - 1.2, po[1] - 3.4)).label("Arduino A1", "left")
    # 引脚号（灰色）：LM358 A 半 3 = +、2 = −、1 = 输出；2N3904 B / C / E
    G9 = dict(fs_=9, color="#666666")
    L.lab(d, (pp[0] + 0.25, pp[1] + 0.3), "3", **G9)
    L.lab(d, (pm[0] + 0.25, pm[1] - 0.4), "2", **G9)
    L.lab(d, (po[0] - 0.45, po[1] + 0.3), "1", **G9)
    L.lab(d, (xb - 0.3, po[1] + 0.3), "B", **G9)
    L.lab(d, (qc[0] - 0.45, qc[1] + 0.2), "C", **G9)
    L.lab(d, (qe[0] - 0.45, qe[1] - 0.25), "E", **G9)
    if lab:
        L.probe(d, po, "①", dx=-0.6, dy=0.9)
        L.probe(d, (qe[0], ye), "②", dx=-0.45, dy=0.75)
        L.probe(d, (qc[0], ytop - 4.4), "③", dx=-0.9, dy=0.0)
        L.probe(d, (xs + 1.3, ys), "④", dx=0.0, dy=0.8)
    return dict(xs=xs, ys=ys, po=po, qc=qc, qe=qe, ye=ye, ytop=ytop, xa=xa)


def p2_2_vi():
    """图 41-p2-2：本节的电压→电流发送器（V_SET 由 D9 的 PWM 滤波得到）。"""
    with schem.drawing(fontsize=11) as d:
        g = _sender(d, lab=False, a1=True)
        L.lab(d, (-1.6, g["ye"] - 6.6), "$I_E = V_{SET} / R_S$；回路电流 $I_C = I_E\\cdot\\beta/(\\beta+1)$，比 $I_E$ 少约 1 %。", fs_=10)
        L.lab(d, (-1.6, g["ye"] - 7.3), "A1 读到运放输出的 10/32；analogWrite(224) → $V_{SET}$ = 1.996 V → 19.96 mA；R1/R2 = 12k/10k 让满码 255 只到 22.73 mA。", fs_=9.5, color="#333333")
        schem.save_schem(d, P, "41_p2_2_vi.png")


def p2_1_budget():
    """图 41-p2-1：回路电压预算（20 mA 时各部分分到多少伏）。"""
    I = 0.020
    rows = [
        ("本节实验 12 V\n250 Ω 接收", 12.0, [("250 Ω", I * 250, C["cur"]), ("R_S", I * S.R_S, C["fb"]),
                                         ("晶体管 V_CE（其中 4.7 V\n可让给 R_x ≈ 235 Ω）", 12.0 - I * 250 - I * S.R_S, "0.85")]),
        ("XTR115 24 V\n250 Ω 接收", 24.0, [("250 Ω", I * 250, C["cur"]), ("XTR115 ≥ 7.5 V", S.XTR115_VMIN, C["vout"]),
                                          ("导线可用（÷ 20 mA = 575 Ω）", 24.0 - I * 250 - S.XTR115_VMIN, "0.85")]),
        ("XTR115 12 V\n250 Ω 接收", 12.0, [("250 Ω", I * 250, C["cur"]), ("XTR115 ≥ 7.5 V", S.XTR115_VMIN, C["vout"])]),
        ("XTR115 12 V\n100 Ω 接收", 12.0, [("100 Ω", I * 100, C["cur"]), ("XTR115 ≥ 7.5 V", S.XTR115_VMIN, C["vout"]),
                                          ("导线可用", 12.0 - I * 100 - S.XTR115_VMIN, "0.85")]),
    ]
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    for k, (name, vs, parts) in enumerate(rows):
        y = len(rows) - 1 - k
        x = 0.0
        for lab, v, c in parts:
            ax.barh(y, v, left=x, height=0.55, color=c, edgecolor="k", lw=0.6)
            ax.text(x + v / 2, y, f"{lab}\n{v:.1f} V", ha="center", va="center", fontsize=7)
            x += v
        ax.plot([vs, vs], [y - 0.38, y + 0.38], color="k", lw=2)
        tot = sum(p[1] for p in parts)
        if tot > vs + 1e-9:
            ax.text(tot + 0.2, y, f"需要 {tot:.1f} V，比 {vs:.0f} V 多，带不动", va="center", fontsize=8, color=C["bad"])
        print(f"[图 41-p2-1] {name.replace(chr(10), ' ')}：" + "，".join(f"{l} {v:.2f} V" for l, v, _ in parts) + f"；电源 {vs} V")
    ax.text(12.3, 0.0, "导线可用 2.5 V ÷ 20 mA = 125 Ω", fontsize=7.5, va="center")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=8)
    ax.set_ylim(-0.6, 3.6)
    fs.axlabels(ax, "回路里的电压（20 mA 时；黑竖线 = 电源电压）", "V")
    ax.set_xlim(0, 26)
    fs.save(fig, P, "41_p2_1_budget.png")


def _loopwire(d, pts, lw=2.6):
    for a, b in zip(pts[:-1], pts[1:]):
        d += elm.Line().at(a).to(b).color(C["cur"]).linewidth(lw)


def p2_3_fullloop():
    """图 41-p2-3：完整回路原理图：12 V 电源的负端用真实导线接回，导线电阻画成两只 R_线/2，天蓝色描出唯一电流路径。"""
    with schem.drawing(fontsize=10) as d:
        yt, yb = 8.0, -1.6
        _bat(d, 0, 2.0, 4.5, "12 V\n电源")
        _loopwire(d, [(0, 4.5), (0, yt), (0.8, yt)])
        d += elm.Resistor().at((0.8, yt)).to((3.3, yt)).color(C["vin"]).linewidth(2.0)
        L.lab(d, (2.05, yt - 0.75), "250 Ω 接收", ha="center", color=C["vin"])
        # 可选 100 nF（灰色点线）
        for a, b in (((0.8, yt), (0.8, yt + 1.3)), ((3.3, yt + 1.3), (3.3, yt))):
            d += elm.Line().at(a).to(b).color(L.GRAY).linestyle(":")
        d += elm.Capacitor().at((0.8, yt + 1.3)).to((3.3, yt + 1.3)).color(L.GRAY).linestyle(":")
        L.lab(d, (2.05, yt + 2.05), "可选 100 nF（灰色点线）", ha="center", fs_=8.5, color=L.GRAY)
        _loopwire(d, [(3.3, yt), (4.0, yt)])
        d += elm.Resistor().at((4.0, yt)).to((6.4, yt)).linewidth(2.0)
        L.lab(d, (5.2, yt + 0.6), "导线电阻 R线/2（去线）", ha="center")
        # 变送器
        xq = 12.4
        q = elm.BjtNpn(circle=True).anchor("base").at((xq, 4.6))
        d += q
        qc, qe = q.absanchors["collector"], q.absanchors["emitter"]
        _loopwire(d, [(6.4, yt), (qc[0], yt), qc])
        L.lab(d, (qc[0] + 0.45, 4.6), "Q1", fs_=10)
        ye = qe[1] - 0.9
        _loopwire(d, [qe, (qe[0], ye)])
        d += elm.Dot().at((qe[0], ye))
        d += elm.Resistor().at((qe[0], ye)).to((qe[0], ye - 2.3)).linewidth(2.0)
        L.lab(d, (qe[0] + 0.45, ye - 1.15), "$R_S$ 100 Ω", fs_=10)
        _loopwire(d, [(qe[0], ye - 2.3), (qe[0], yb), (6.4, yb)])
        d += elm.Resistor().at((6.4, yb)).to((4.0, yb)).linewidth(2.0)
        L.lab(d, (5.2, yb - 0.6), "导线电阻 R线/2（回线）", ha="center")
        _loopwire(d, [(4.0, yb), (0, yb), (0, 2.0)])
        op = elm.Opamp(leads=True).right().flip().anchor("out").at((xq - 2.2, 4.6))
        d += op
        po, pm, pp = op.absanchors["out"], op.absanchors["in1"], op.absanchors["in2"]
        d += elm.Resistor().at(po).to((xq, 4.6))
        L.lab(d, ((po[0] + xq) / 2, 5.15), "R_B", ha="center", fs_=9)
        xm = pm[0] - 0.4
        for a, b in (((pm), (xm, pm[1])), ((xm, pm[1]), (xm, ye)), ((xm, ye), (qe[0], ye))):
            d += elm.Line().at(a).to(b).color(C["fb"])
        d += elm.Line().at(pp).to((pp[0] - 0.6, pp[1]))
        d += elm.Dot(open=True).at((pp[0] - 0.6, pp[1])).label("$V_{SET}$", "left")
        L._dbox(d, 6.9, ye - 2.0, 14.6, 6.9)
        L.lab(d, (7.1, 6.5), "本节的变送器（运放 + Q1 + $R_S$）", fs_=9.5, color=L.GRAY)
        # I 标注
        for xy in ((0.35, 6.4), (3.65, yt + 0.4), (8.6, yt + 0.35)):
            L.lab(d, xy, "$I$", fs_=12, color=C["cur"])
        for xy in ((qe[0] + 0.35, ye + 0.45), (8.6, yb + 0.4), (0.35, 0.4)):
            L.lab(d, xy, "$I_E$", fs_=12, color=C["cur"])
        L.lab(d, ((po[0] + xq) / 2, 4.05), "$I_B$ →", ha="center", fs_=10, color=C["cur"])
        L.lab(d, (7.4, 0.3), "集电极以上处处 = $I$；$R_S$ 上 $I_E = I + I_B$（约多 1 %）", ha="center", fs_=11, color=C["cur"])
        L.lab(d, (7.4, -0.4), "（天蓝色粗线 = 回路电流的路径；$I_B$ 来自运放，不经过 250 Ω）", ha="center", fs_=9, color=C["cur"])
        L.lab(d, (-0.8, yb - 1.5), "实验里两段 R线/2 合成一只 $R_x$，插在 +12 V 和 250 Ω 之间；串联元件换顺序，电流不变。", fs_=9)
        schem.save_schem(d, P, "41_p2_3_fullloop.png")


def p2_4_divider():
    """图 41-p2-4：PWM 滤波两种接法：不分压（10 kΩ + 10 µF）和本节的 12k/10k 分压 + 10 µF。"""
    with schem.drawing(fontsize=10) as d:
        for x0, r1, ttl, vfull in ((0.0, "10 kΩ", "不分压", 5.0), (9.0, "12 kΩ（R1）", "本节：12k/10k 分压", S.V5 * S.K_DIV)):
            L.title(d, (x0 + 2.6, 2.6), ttl)
            d += elm.Dot(open=True).at((x0, 1.2)).label("D9", "left")
            d += elm.Resistor().at((x0, 1.2)).to((x0 + 2.6, 1.2))
            L.lab(d, (x0 + 1.3, 1.75), r1, ha="center", fs_=9.5)
            d += elm.Dot().at((x0 + 2.6, 1.2))
            xc = x0 + 2.6
            if x0 > 0:
                d += elm.Resistor().at((xc, 1.2)).to((xc, -1.2))
                d += elm.Ground().at((xc, -1.2))
                L.lab(d, (xc - 0.35, 0.0), "10 kΩ\n（R2）", ha="right", fs_=9.5)
                d += elm.Line().at((xc, 1.2)).to((xc + 1.2, 1.2))
                xc += 1.2
                d += elm.Dot().at((xc, 1.2))
            d += elm.Capacitor().at((xc, 1.2)).to((xc, -1.2))
            d += elm.Ground().at((xc, -1.2))
            L.lab(d, (xc + 0.35, 0.0), "10 µF", fs_=9.5)
            d += elm.Line().at((xc, 1.2)).to((xc + 1.0, 1.2))
            d += elm.Dot(open=True).at((xc + 1.0, 1.2)).label("$V_{SET}$", "right")
            L.lab(d, (x0 + 2.6, -2.5), f"满码 255：$V_{{SET}}$ = {vfull:.3f} V", ha="center", fs_=10)
            print(f"[图 41-p2-4] {ttl}：满码 V_SET = {vfull:.3f} V")
        schem.save_schem(d, P, "41_p2_4_divider.png")


# ======================================================================
# page3
# ======================================================================
def _sweep():
    """sweep.cir：R_x 从 1 Ω 慢慢扫到 701 Ω（0.005 s 起每秒 1400 Ω），三路设定 1.2 / 2.0 / 2.1 V。"""
    a = run_spice("41", "sweep.cir", ["rx", "ila", "ilb", "ilc", "iea", "ieb", "iec", "hda", "hdb", "hdc"])
    m = a[:, 0] > 0.006
    return a[m]


def p3_1_compliance(a):
    """图 41-p3-1：回路电流（流过 250 Ω）和 A0 看到的发射极电流随 R_x 的变化。"""
    rx = a[:, 1]
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    for (il, ie, lab, st) in ((2, 5, "12 mA", "vin"), (3, 6, "20 mA", "vout"), (4, 7, "21 mA", "third")):
        ax.plot(rx, a[:, il] * 1e3, **LSk(st), label=f"设定 {lab}：回路电流（250 Ω 上）")
        ax.plot(rx, a[:, ie] * 1e3, color=LSk(st)["color"], ls=":", lw=1.2, label=f"设定 {lab}：A0 读到的 $I_E$")
    for r, col in ((470, 3), (220, 4)):
        i = np.argmin(abs(rx - r))
        fs.mark(ax, rx[i], a[i, col] * 1e3, "{:.2f}", " mA", dx=12, dy=-1.6)
    i = np.argmin(abs(rx - 470))
    fs.mark(ax, rx[i], a[i, 6] * 1e3, "{:.2f}", " mA", dx=12, dy=0.6)
    fs.ref_v(ax, 235, "20 mA 线性上限 235 Ω")
    fs.axlabels(ax, "模拟导线电阻 R_x", "Ω", "电流", "mA")
    ax.set_xlim(0, 700); ax.set_ylim(8, 23)
    ax.legend(loc="lower left", fontsize=7, ncol=2)
    fs.save(fig, P, "41_p3_1_compliance.png")


def p3_2_headroom(a):
    """图 41-p3-2：“余量” H = 运放输出 − 发射极电压，随 R_x 变化；超过 1.3 V 判回路异常。"""
    rx = a[:, 1]
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for col, lab, st in ((8, "设定 12 mA", "vin"), (9, "设定 20 mA", "vout"), (10, "设定 21 mA", "third")):
        ax.plot(rx, a[:, col], **LSk(st), label=lab)
    fs.ref_h(ax, S.H_LIMIT, "报警门限 1.3 V", x=0.98)
    for r, col, dy in ((0.0, 9, 0.6), (220, 10, 0.9), (470, 9, -1.2)):
        i = np.argmin(abs(rx - max(r, 2)))
        fs.mark(ax, rx[i], a[i, col], "{:.2f}", " V", dx=12, dy=dy)
    fs.axlabels(ax, "模拟导线电阻 R_x", "Ω", "余量 H", "V")
    ax.set_xlim(0, 700); ax.set_ylim(0, 10)
    ax.legend(loc="upper left", fontsize=7.5)
    fs.save(fig, P, "41_p3_2_headroom.png")


def p3_6_power():
    """图 41-p3-6：2N3904 的功耗随电流变化（12 V，R_x = 0），以及 250 Ω 被短接时。"""
    I = np.linspace(0, 0.0227, 300)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(I * 1e3, S.p_transistor(I) * 1e3, **LSk("vout"), label="正常：12 V − 250 Ω − 100 Ω 剩下的给晶体管")
    ax.plot(I * 1e3, S.p_transistor(I, rx=-S.R_RX) * 1e3, **LSk("bad"), label="250 Ω 被短接（接错）")
    ax.plot(I * 1e3, I ** 2 * S.R_RX * 1e3, **LSk("cur"), label="250 Ω 电阻自己的功耗")
    Im = 12.0 / (2 * (S.R_RX + S.R_S))
    fs.mark(ax, Im * 1e3, S.p_transistor(Im) * 1e3, "{:.1f}", " mW", dx=-1.5, dy=18)
    fs.mark(ax, 20, S.p_transistor(0.020) * 1e3, "{:.1f}", " mW", dx=0.3, dy=-28)
    fs.mark(ax, 20, S.p_transistor(0.020, rx=-S.R_RX) * 1e3, "{:.0f}", " mW", dx=-4.5, dy=8)
    ax.text(0.5, 215, "2N3904 手册：25 °C 时最大 625 mW，RθJA 200 °C/W\n→ 0.2 W 时管子比环境热约 40 °C（别用手摸）", fontsize=7.5)
    fs.axlabels(ax, "电流", "mA", "功耗", "mW")
    ax.set_xlim(0, 23); ax.set_ylim(0, 260)
    ax.legend(loc="center left", fontsize=7)
    fs.save(fig, P, "41_p3_6_power.png")


def p3_5_wave():
    """图 41-p3-5：wave.cir：analogWrite 45 → 224 时的回路电流（12k/10k + 10 µF）与不分压方案对比，下图放大看纹波。"""
    a = run_spice("41", "wave.cir", ["i1", "i2"])
    t = a[:, 0]
    fig, (a0, a1) = plt.subplots(2, 1, figsize=(7, 4.4))
    m = t > 0.35
    a0.plot(t[m], a[m, 1] * 1e3, **LSk("vout"), label="本节：12k/10k 分压 + 10 µF")
    a0.plot(t[m], a[m, 2] * 1e3, **LSk("vin"), label="不分压：10k + 10 µF（占空 8 % → 40 %）")
    fs.ref_v(a0, 0.5, "0.5 s 改码")
    a0.set_ylim(0, 23); a0.set_xlim(0.35, 1.2)
    fs.axlabels(a0, "时间", "s", "回路电流", "mA")
    a0.legend(loc="lower right", fontsize=7.5)
    m2 = (t > 1.10) & (t < 1.12)
    a1.plot((t[m2] - 1.10) * 1e3, a[m2, 1] * 1e3, **LSk("vout"))
    a1.plot((t[m2] - 1.10) * 1e3, a[m2, 2] * 1e3, **LSk("vin"))
    pp1 = np.ptp(a[(t > 1.19), 1]) * 1e6
    pp2 = np.ptp(a[(t > 1.19), 2]) * 1e6
    a1.text(0.3, 19.965, f"峰峰值：本节 {pp1:.0f} µA，不分压 {pp2:.0f} µA（≈ 490 Hz，周期 2.04 ms）", fontsize=8)
    print(f"[图 41-p3-5] 稳态纹波：12k/10k {pp1:.1f} µApp，不分压 {pp2:.1f} µApp；平均 {a[t > 1.1, 1].mean() * 1e3:.3f} / {a[t > 1.1, 2].mean() * 1e3:.3f} mA")
    fs.axlabels(a1, "时间（从 1.10 s 起）", "ms", "回路电流", "mA")
    a1.set_ylim(19.6, 20.0)
    fs.save(fig, P, "41_p3_5_wave.png")


def _opamp_fb(d, xg, yg, ye_node, x_out_gap=2.2):
    """局部图用：运放输出经 R_B 到 (xg, yg)，反相端蓝绿色反馈线接到 ye_node，同相端接 V_SET。"""
    op = elm.Opamp(leads=True).right().flip().anchor("out").at((xg - x_out_gap, yg))
    d += op
    po, pm, pp = op.absanchors["out"], op.absanchors["in1"], op.absanchors["in2"]
    d += elm.Resistor().at(po).to((xg, yg))
    L.lab(d, ((po[0] + xg) / 2, yg + 0.55), "R_B 1 kΩ", ha="center", fs_=9)
    xm = pm[0] - 0.4
    for a, b in ((pm, (xm, pm[1])), ((xm, pm[1]), (xm, ye_node[1])), ((xm, ye_node[1]), ye_node)):
        d += elm.Line().at(a).to(b).color(C["fb"])
    d += elm.Line().at(pp).to((pp[0] - 0.6, pp[1]))
    d += elm.Dot(open=True).at((pp[0] - 0.6, pp[1])).label("$V_{SET}$", "left")
    return op


def p3_3_fet():
    """图 41-p3-3：把 2N3904 换成 2N7000 的局部原理图：G、D、S 分别接原来 B、C、E 的位置。"""
    with schem.drawing(fontsize=10) as d:
        xg = 6.0
        q = elm.NFet().reverse().anchor("gate").at((xg, 3.0))
        d += q
        qd, qs = q.absanchors["drain"], q.absanchors["source"]
        d += elm.Line().at(qd).to((qd[0], qd[1] + 1.2))
        d += elm.Dot(open=True).at((qd[0], qd[1] + 1.2)).label("接 250 Ω 下端（原集电极 C 的位置）", "right")
        ye = qs[1] - 0.8
        d += elm.Line().at(qs).to((qs[0], ye))
        d += elm.Dot().at((qs[0], ye))
        d += elm.Resistor().at((qs[0], ye)).to((qs[0], ye - 2.2))
        d += elm.Ground().at((qs[0], ye - 2.2))
        L.lab(d, (qs[0] + 0.4, ye - 1.1), "$R_S$ 100 Ω", fs_=10)
        _opamp_fb(d, xg, 3.0, (qs[0], ye))
        L.lab(d, (qd[0] + 0.7, 3.0), "2N7000\nG = 栅极 ↔ 原 B\nD = 漏极 ↔ 原 C\nS = 源极 ↔ 原 E", fs_=9.5)
        L.lab(d, (0.0, ye - 3.2), "栅极不取电流：流过 $R_S$ 的电流全部来自漏极，A0 读到的就是回路电流。", fs_=9.5)
        schem.save_schem(d, P, "41_p3_3_fet.png")


def p3_4_pulldown():
    """图 41-p3-4：坏例：A0 再加 100 kΩ 下拉，会和 10 kΩ 分压。"""
    k = 100e3 / (10e3 + 100e3)   # V_E 被运放钉住；R_S 和 10k+100k 这一串并联，不参与分压
    with schem.drawing(fontsize=10) as d:
        d += elm.Dot(open=True).at((0, 2.0)).label("发射极 $V_E$", "left")
        d += elm.Line().at((0, 2.0)).to((0.8, 2.0))
        d += elm.Dot().at((0.8, 2.0))
        d += elm.Resistor().at((0.8, 2.0)).to((0.8, -0.4))
        d += elm.Ground().at((0.8, -0.4))
        L.lab(d, (1.2, 0.8), "$R_S$\n100 Ω", fs_=9.5)
        d += elm.Line().at((0.8, 2.0)).to((2.8, 2.0))
        d += elm.Resistor().at((2.8, 2.0)).to((5.4, 2.0))
        L.lab(d, (4.1, 2.55), "10 kΩ", ha="center", fs_=9.5)
        d += elm.Dot().at((6.4, 2.0))
        d += elm.Line().at((5.4, 2.0)).to((7.4, 2.0))
        d += elm.Dot(open=True).at((7.4, 2.0)).label("Arduino A0", "right")
        d += elm.Resistor().at((6.4, 2.0)).to((6.4, -0.4)).color(C["bad"])
        d += elm.Ground().at((6.4, -0.4)).color(C["bad"])
        L.lab(d, (6.85, 0.8), "100 kΩ 下拉\n（多余，别加）", fs_=9.5, color=C["bad"])
        L.lab(d, (5.75, 1.15), "×", ha="center", fs_=20, color=C["bad"])
        L.lab(d, (-0.6, -1.9), f"A0 = 100 / (10 + 100) × $V_E$ = {k:.3f} × $V_E$：读数偏低 {100 * (1 - k):.1f} %（$R_S$ 并在旁边，不在这一串里）", fs_=10)
        print(f"[图 41-p3-4] 100 kΩ 下拉：A0 = {k:.4f} V_E")
        schem.save_schem(d, P, "41_p3_4_pulldown.png")


def p3_7_wronggnd():
    """图 41-p3-7：坏例：把 250 Ω 下端（集电极）多接一根地线。数字来自 41_sim 第 9 部分和 spice/41/wrong_gnd.cir。"""
    ig = S.VS / (S.R_RX + 470)
    with schem.drawing(fontsize=10) as d:
        xc = 6.0
        d += elm.Vdd().at((xc, 9.0)).label("+12 V")
        d += elm.Resistor().at((xc, 9.0)).to((xc, 6.8)).color(C["cur"])
        L.lab(d, (xc + 0.45, 7.9), "$R_x$ 470 Ω", fs_=10)
        d += elm.Resistor().at((xc, 6.8)).to((xc, 4.6)).color(C["cur"])
        L.lab(d, (xc + 0.45, 5.7), "250 Ω", fs_=10, color=C["vin"])
        d += elm.Dot().at((xc, 4.6))
        # 多出来的地线
        d += elm.Line().at((xc, 4.6)).to((xc + 3.0, 4.6)).color(C["bad"]).linewidth(2.2)
        d += elm.Line().at((xc + 3.0, 4.6)).to((xc + 3.0, 3.6)).color(C["bad"]).linewidth(2.2)
        d += elm.Ground().at((xc + 3.0, 3.6)).color(C["bad"])
        L.lab(d, (xc + 1.5, 4.6), "×", ha="center", fs_=22, color=C["bad"])
        L.lab(d, (xc + 3.4, 4.3), "多接的这根地线（错）", fs_=10, color=C["bad"])
        d += elm.Line().at((xc, 4.6)).to((xc, 3.9))
        q = elm.BjtNpn(circle=True).right().anchor("collector").at((xc, 3.9))
        d += q
        qb, qe = q.absanchors["base"], q.absanchors["emitter"]
        ye = qe[1] - 0.6
        d += elm.Line().at(qe).to((qe[0], ye))
        d += elm.Dot().at((qe[0], ye))
        d += elm.Resistor().at((qe[0], ye)).to((qe[0], ye - 2.0))
        d += elm.Ground().at((qe[0], ye - 2.0))
        L.lab(d, (qe[0] + 0.4, ye - 1.0), "$R_S$ 100 Ω", fs_=9.5)
        _opamp_fb(d, qb[0], qb[1], (qe[0], ye))
        L.lab(d, (-1.4, ye - 3.4), f"天蓝色 + 朱红色 = 电流抄的近路：12 V ÷ (470 + 250) Ω = {ig * 1e3:.1f} mA，250 Ω 上 {ig * 250:.2f} V，和设定无关。", fs_=10)
        L.lab(d, (-1.4, ye - 4.1), "SPICE：运放输出顶到约 10.5 V，发射极只剩 0.165 V，A0 显示约 1.6 mA，余量 10.3 V → 程序报警。", fs_=10)
        print(f"[图 41-p3-7] 错误接地：{ig * 1e3:.2f} mA，{ig * 250:.3f} V")
        schem.save_schem(d, P, "41_p3_7_wronggnd.png")


# ======================================================================
# page4：面包板 + 对照原理图
# ======================================================================
def bb41():
    bb = Breadboard(ncol=36, rails=dict(tp=("+12 V", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"), bn=("+12 V", "pos")),
                    figsize=(12, 6.8))
    bb.ax.set_ylim(-6.8, 15.2)
    HOP_T = [BB_RAIL_Y["tn"] - 0.32]
    HOP_B = [BB_RAIL_Y["bp"] + 0.32, BB_RAIL_Y["bn"] - 0.32]
    bb.wire(bb.ext((-2.4, 11.4), "12 V 电源 +", "pos"), "tp1", "pos")
    bb.wire(bb.ext((-2.4, 10.4), "12 V 电源 −", "gnd"), "tn1", "gnd")
    bb.wire("tn34", "bp34", "gnd")                                         # 上下 0 V 轨连通
    bb.wire("tp35", "bn35", "pos", hops=[BB_RAIL_Y["tn"], BB_RAIL_Y["bp"]])  # 上下 +12 V 轨连通
    # PWM 滤波：D9 → R1 12k → 第 5 列 → R2 10k、C1 10 µF 到地 → 绿线到 3 脚（第 14 列）
    bb.wire(bb.ext((1.0, -6.0), "Arduino D9 →", "sig", dx=-0.45), "j1", "sig", hops=HOP_B)
    bb.two("R1", "h1", "h5", "R", "R1 12k", lpos=(0, 0.55))
    bb.two("R2", "j5", "bp5", "R", None)
    bb.ax.text(4.7, -1.75, "R2 10k", fontsize=7, ha="right")
    bb.two("C1", "i5", "bp7", "C", None)
    bb.ax.text(6.4, 0.5, "C1 10µ（+ 接 i5）", fontsize=7, va="center")
    bb.wire("g5", "g14", "sig")
    # LM358：第 12–15 列
    bb.dip8("U1", 12, "LM358")
    bb.wire("a12", "tp11", "pos", hops=HOP_T)                 # 8 脚 +12 V
    bb.two("C2", "b12", "tn10", "C", "100n", lpos=(-1.2, 0.0))
    bb.wire("c13", "c14", "sig")                              # 7–6 相连（B 半接成跟随器）
    bb.wire("a15", "tn15", "gnd")                             # 5 脚接地
    bb.wire("j15", "bp15", "gnd")                             # 4 脚地
    # A1 分压：1 脚 → R3 22k → 第 9 列 → R4 10k → 地；h9 引出到 A1
    bb.two("R3", "i12", "i9", "R", "R3 22k", lpos=(0, -0.5))
    bb.two("R4", "j9", "bp8", "R", None)
    bb.ax.text(8.7, -1.25, "R4 10k", fontsize=7, ha="right")
    bb.wire("h9", bb.ext((9.0, -6.0), "→ A1", "sig", dx=0.45, ha="left"), "sig", hops=HOP_B)
    # R_B：1 脚 → 第 17 列 → 绿线到基极
    bb.two("RB", "h12", "h17", "R", "R_B 1k", lpos=(0, 0.55))
    bb.wire("g17", "g23", "sig")
    # 2N3904：E f22、B f23、C f24（平面朝自己）
    bb.multi("Q1", {"E": "f22", "B": "f23", "C": "f24"}, "2N3904", w=2.8, h=0.7, at=(23.0, 4.0))
    bb.wire("i13", "i22", "sig")                              # 2 脚 ← 发射极（负反馈）
    bb.two("RS", "j22", "bp22", "R", None)
    bb.ax.text(21.6, -1.75, "R_S 100", fontsize=7, ha="right")
    bb.two("RA0", "h22", "h27", "R", "10k", lpos=(0.6, 0.55))
    bb.wire("j27", bb.ext((27.0, -6.0), "→ A0", "sig", dx=0.45, ha="left"), "sig", hops=HOP_B)
    # 回路：集电极 → 250 Ω → R_x → +12 V
    bb.two("RL", "i24", "i29", "R", None)
    bb.ax.text(26.5, -0.75, "250 Ω", fontsize=7.5, ha="center", color=C["cur"])
    bb.two("RX", "h29", "h33", "R", "R_x", lpos=(0, 0.55))
    bb.wire("j33", "bn33", "pos", hops=[BB_RAIL_Y["bp"]])
    bb.wire(bb.ext((25.0, -6.0), "Arduino GND", "gnd", dx=-0.45), "bp25", "gnd", hops=[BB_RAIL_Y["bn"]])
    # 连接检查
    assert bb.connected("U1.8", "tp1") and bb.connected("RX.2", "tp1") and bb.connected("tp1", "bn1")
    assert bb.connected("U1.4", "tn1") and bb.connected("U1.5", "tn1") and bb.connected("U1.6", "U1.7") and bb.connected("tn1", "bp1")
    assert bb.connected("R1.2", "R2.1") and bb.connected("R1.2", "C1.1") and bb.connected("R1.2", "U1.3")
    assert bb.connected("R2.2", "tn1") and bb.connected("C1.2", "tn1")
    assert bb.connected("U1.2", "Q1.E") and bb.connected("RS.1", "Q1.E") and bb.connected("RA0.1", "Q1.E") and bb.connected("RS.2", "tn1")
    assert bb.connected("U1.1", "RB.1") and bb.connected("RB.2", "Q1.B") and bb.connected("U1.1", "R3.1")
    assert bb.connected("R3.2", "R4.1") and bb.connected("R4.2", "tn1")
    assert bb.connected("Q1.C", "RL.1") and bb.connected("RL.2", "RX.1")
    assert not bb.connected("tp1", "tn1") and not bb.connected("U1.1", "U1.2") and not bb.connected("U1.2", "U1.3")
    assert not bb.connected("Q1.C", "Q1.E") and not bb.connected("Q1.B", "Q1.E") and not bb.connected("R1.1", "R1.2")
    for safe in ("RA0.2", "R4.1"):                            # 去 Arduino 的点不能碰 12 V、集电极或运放输出
        assert not bb.connected(safe, "tp1") and not bb.connected(safe, "Q1.C") and not bb.connected(safe, "U1.1")
    # 250 Ω 的替代接法：100 Ω i24–i26 + 150 Ω g26–g29。150 Ω 放在 g 排，不跨过 j27 → A0 那根线
    for h in ("i26", "g26", "g29"):
        assert h not in bb.used, f"替代接法要用的 {h} 已被占用"
    assert not bb.connected("g26", "RA0.2") and not bb.connected("g26", "tp1") and not bb.connected("g26", "tn1")
    assert bb.connected("g29", "RL.2") and bb.connected("g29", "RX.1") and not bb.connected("g29", "RA0.2")
    bb.probe("j12", "①运放输出", dx=-0.2, dy=-1.0, ha="right")
    bb.probe("g22", "②发射极", dx=-0.3, dy=-0.95, ha="right")
    bb.probe("j24", "③集电极", dx=0.25, dy=-1.0)
    bb.probe("j14", "④V_SET", dx=0.25, dy=-1.0)
    bb.note(30.0, 13.3, "万用表 V 档跨在 250 Ω 两端（i24、i29 所在列）\n读到的伏数 ÷ 250 = 回路电流", fontsize=7.5, ha="center")
    bb.note(12.0, 13.6, "Arduino 的 5V 脚不接面包板；GND 接下面的 0 V 轨（R_S 下端那条）", fontsize=7.5, ha="center")
    bb.legend(("pos", "gnd", "sig"), y=0.02)
    print(f"41 p4 面包板：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def p4_2_schem_lab():
    """图 41-p4-2：与面包板一一对应的实验原理图（带测量点和 A1 分压）。"""
    with schem.drawing(fontsize=11) as d:
        g = _sender(d, lab=True)
        qc, ytop = g["qc"], g["ytop"]
        L.lab(d, (qc[0] + 0.45, ytop - 4.2), "（或 100 Ω i24–i26 + 150 Ω g26–g29 串联）", fs_=8.5, color="#333333")
        # 右上角小框：LM358 B 半 + 8 脚去耦
        bx, by = qc[0] + 7.6, ytop - 1.4
        L._follower_b(d, bx, by, "c13–c14 短线（7 脚接 6 脚）", "a15 → 0 V（5 脚）", gname="0 V", ttl="同一片 LM358 的 B 半（不用）")
        xc8 = bx + 7.2
        d += elm.Vdd().at((xc8, by - 1.6)).label("+12 V（8 脚，a12）")
        d += elm.Capacitor().at((xc8, by - 1.6)).to((xc8, by - 3.6))
        d += elm.Ground().at((xc8, by - 3.6)).label("0 V", "bottom")
        L.lab(d, (xc8 + 0.4, by - 2.6), "100 nF 去耦\nb12 → 上方 0 V 轨", fs_=8.5)
        L._dbox(d, bx - 2.0, by - 4.8, xc8 + 3.0, by + 3.3)
        y0 = g["po"][1] - 8.3
        for k, t in enumerate(("孔位：D9 → j1，R1 h1–h5，R2 j5→地，C1 i5→地，绿线 g5→g14（3 脚）；LM358 第 12–15 列；",
                               "　　　R_B h12–h17，绿线 g17→g23（基极）；2N3904 E/B/C = f22/f23/f24；绿线 i13→i22（2 脚接发射极）；",
                               "　　　R_S j22→地；10 kΩ h22–h27，j27 → A0；250 Ω i24–i29，R_x h29–h33，j33 → +12 V 轨；",
                               "　　　22 kΩ i12–i9，10 kΩ j9→地，h9 → A1。圆圈①～④ = 红表笔位置（① j12、② g22、③ j24、④ j14），黑表笔接 0 V 轨。")):
            L.note(d, (-1.6, y0 - 0.6 * k), t)
        schem.save_schem(d, P, "41_p4_2_schem_lab.png")



def p1_5_sender():
    """图 41-p1-5：直觉篇「本节要搭什么」对照用的原理图：PWM 经 RC → LM358 + 2N3904 + 100 Ω 恒流，12 V、R_x、250 Ω 串成一圈。"""
    with schem.drawing(fontsize=11) as d:
        g = _sender(d, lab=False, a1=False)
        y0 = g["ye"] - 3.6
        L.lab(d, (-1.6, y0), "(1) PWM → R1/R2/C1 滤成直流 $V_{SET}$；(2) 运放 + Q1 + R_S 让 R_S 上的电压 = $V_{SET}$，电流 = $V_{SET}$ / 100 Ω；", fs_=10)
        L.lab(d, (-1.6, y0 - 0.65), "(3) 回路：+12 V → R_x → 250 Ω → Q1 的 C → E → R_S → 地（12 V 负端）；(4) 万用表量 250 Ω，Arduino 只经 10 kΩ 看 R_S 上端（A0）。", fs_=10)
        schem.save_schem(d, P, "41_p1_5_sender.png")


if __name__ == "__main__":
    p1_1_error(); p1_2_loop(); p1_3_wires(); p1_4_ne43(); p1_5_sender()
    p2_1_budget(); p2_2_vi(); p2_3_fullloop(); p2_4_divider()
    A = _sweep()
    p3_1_compliance(A); p3_2_headroom(A); p3_3_fet(); p3_4_pulldown(); p3_5_wave(); p3_6_power(); p3_7_wronggnd()
    bb = bb41()
    fs.save(bb.fig, P, "41_p4_1_breadboard.png")
    plt.close("all")
    p4_2_schem_lab()
    print("41_figs OK")
