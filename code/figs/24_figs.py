"""24 隔离电源与数字隔离器：电路图和方框图（schemdraw + figstyle 方框图）。
运行：/workspace/circuits-venv/bin/python code/figs/24_figs.py
图上的数字与 code/24_sim.py 一致（220 V → 12 V 变压器整流后 15.57 V；NME0505SC 5 V 200 mA；ISO7721；假负载 270 Ω），本脚本也会打印它们。
图 24-p2-1 的初级接市电，只画图、不做实验。"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem
from schem import elm, barrier, module
import figstyle as fs
import matplotlib.pyplot as plt

P = "24"
V_DC = math.sqrt(2) * 12 - 1.4
print(f"[数值] 220 V → 12 V 变压器，整流滤波后最高约 {V_DC:.2f} V；NME0505SC 5 V、200 mA；ISO7721；假负载 270 Ω")
assert abs(V_DC - 15.57) < 0.01


def p1_1():
    """图 24-p1-1：只用光耦时电源线把两侧的地连起来；加隔离电源后两侧完全分开。"""
    fig, ax = fs.diagram(8.6, 4.4)
    ax.text(0.05, 4.15, "① 信号用了光耦，电源却从单片机这边直接拉过去", fontsize=10, color=fs.C["bad"])
    a = fs.box(ax, 1.2, 3.1, "单片机侧\n5 V、GND1", w=1.9, h=0.9)
    o = fs.box(ax, 4.3, 3.45, "光耦", w=1.2, h=0.5)
    b = fs.box(ax, 7.3, 3.1, "现场侧\n传感器", w=1.9, h=0.9)
    fs.arrow(ax, (a["r"][0], 3.45), o["l"]); fs.arrow(ax, o["r"], (b["l"][0], 3.45), "信号")
    fs.arrow(ax, (a["r"][0], 2.85), (b["l"][0], 2.85), color=fs.C["bad"])
    fs.arrow(ax, (a["r"][0], 2.7), (b["l"][0], 2.7), color=fs.C["bad"])
    ax.text(4.3, 2.6, "5 V 电源线和地线也连过去了：GND1 = GND2，隔离白做 ×", ha="center", va="top", fontsize=9, color=fs.C["bad"])
    ax.plot([4.3, 4.3], [3.2, 3.75], color=fs.C["ref"], ls="--", lw=1.2)
    ax.text(0.05, 1.85, "② 信号走数字隔离器（或光耦），电源走隔离 DC-DC 模块", fontsize=10, color=fs.C["good"])
    a2 = fs.box(ax, 1.2, 0.85, "单片机侧\n5 V、GND1", w=1.9, h=0.9)
    p = fs.box(ax, 4.3, 1.2, "隔离 DC-DC 模块", w=2.2, h=0.5)
    s = fs.box(ax, 4.3, 0.5, "数字隔离器", w=2.2, h=0.5)
    b2 = fs.box(ax, 7.3, 0.85, "现场侧\n5 V、GND2", w=1.9, h=0.9)
    fs.arrow(ax, (a2["r"][0], 1.2), p["l"], "电能"); fs.arrow(ax, p["r"], (b2["l"][0], 1.2))
    fs.arrow(ax, (a2["r"][0], 0.5), s["l"], "信号"); fs.arrow(ax, s["r"], (b2["l"][0], 0.5))
    ax.plot([4.3, 4.3], [0.15, 1.6], color=fs.C["ref"], ls="--", lw=1.2)
    ax.text(4.3, 0.1, "隔离带：没有任何导线穿过", ha="center", va="top", fontsize=9, color="0.3")
    ax.set_ylim(-0.4, 4.4)
    print("[图 24-p1-1] 5 V（只有文字）")
    fs.save(fig, P, "24_p1_1_problem.png")


def p2_1():
    """图 24-p2-1：工频变压器隔离电源：220 V → 保险丝 → 变压器 → 桥式整流滤波（见 06）→ 约 15.57 V。"""
    with schem.drawing(fontsize=11) as d:
        t = elm.Transformer(t1=4, t2=4).anchor("p1")
        d += t.at((0, 3.0))
        p1, p2, s1, s2 = (t.absanchors[k] for k in ("p1", "p2", "s1", "s2"))
        x_src = p1[0] - 4.5
        d += elm.SourceSin().endpoints((x_src, p2[1]), (x_src, p1[1])).label("220 V\n市电", "left")
        d += elm.FuseIEC().endpoints((x_src, p1[1]), (p1[0] - 0.3, p1[1])).label("保险丝", "top")
        d += elm.Line().endpoints((p1[0] - 0.3, p1[1]), p1)
        d += elm.Line().endpoints((x_src, p2[1]), p2)
        xm = (p1[0] + s1[0]) / 2
        barrier(d, xm, p2[1] - 1.2, p1[1] + 1.0, text="隔离带（绕组之间）")
        d += elm.Label().at(((x_src + p1[0]) / 2, p2[1] - 0.9)).label("初级：带市电，危险", loc="center", color="#D55E00")
        d += (u := module("桥式整流\n+ 电容滤波\n（见 06）", ("AC1", "AC2"), ("+", "GND2"), w=3.0).theta(0).anchor("AC1").at((s1[0] + 1.5, s1[1])))
        d += elm.Line().endpoints(s1, u.absanchors["AC1"])
        d += elm.Line().endpoints(s2, (s2[0] + 0.75, s2[1]))
        d += elm.Line().endpoints((s2[0] + 0.75, s2[1]), (s2[0] + 0.75, u.absanchors["AC2"][1]))
        d += elm.Line().endpoints((s2[0] + 0.75, u.absanchors["AC2"][1]), u.absanchors["AC2"])
        vp, gp = u.absanchors["+"], u.absanchors["GND2"]
        d += elm.Line().endpoints(vp, (vp[0] + 1.2, vp[1]))
        d += elm.Dot(open=True).at((vp[0] + 1.2, vp[1])).label(f"约 {V_DC:.2f} V\n（直流）", "right")
        d += elm.Line().endpoints(gp, (gp[0] + 1.2, gp[1]))
        d += elm.Dot(open=True).at((gp[0] + 1.2, gp[1])).label("GND2", "right")
        d += elm.Label().at((xm, p1[1] + 2.0)).label("变压器 220 V → 12 V（N1/N2 ≈ 18.33）", loc="center")
        d += elm.Label().at((s1[0] + 3.5, p2[1] - 0.9)).label("副边：与市电隔离", loc="center")
    print(f"[图 24-p2-1] 220 V、12 V、N1/N2 ≈ {220/12:.2f}、{V_DC:.2f} V")
    schem.save_schem(d, P, "24_p2_1_transformer.png")


def p2_3():
    """图 24-p2-3：完整的隔离方案：NME0505SC 供电 + ISO7721 传信号，两颗芯片都跨在隔离带上。"""
    with schem.drawing(fontsize=11) as d:
        d += (m := module("隔离 DC-DC 模块\nNME0505SC", ("VIN", "GND1"), ("VOUT", "GND2"), w=3.4).at((0, 0)))
        a = {k: m.absanchors[k] for k in ("VIN", "GND1", "VOUT", "GND2")}
        d += (iso := module("数字隔离器 ISO7721", ("VCC1", "INA", "GND1"), ("VCC2", "OUTA", "GND2"), w=3.4).anchor("VCC1").at((a["VIN"][0], a["GND1"][1] - 2.6)))
        b = {k: iso.absanchors[k] for k in ("VCC1", "INA", "GND1", "VCC2", "OUTA", "GND2")}
        xm = (a["VIN"][0] + a["VOUT"][0]) / 2
        # 左边：单片机侧
        xl = a["VIN"][0] - 3.0
        d += elm.Dot(open=True).at((xl - 1.0, a["VIN"][1])).label("+5 V\n（单片机）", "left")
        d += elm.Line().endpoints((xl - 1.0, a["VIN"][1]), a["VIN"])
        d += elm.Dot().at((xl, a["VIN"][1]))
        d += elm.Capacitor().endpoints((xl, a["VIN"][1]), (xl, a["GND1"][1])).label("输入\n电容", "left")
        d += elm.Dot(open=True).at((xl - 1.0, a["GND1"][1])).label("GND1", "left")
        d += elm.Line().endpoints((xl - 1.0, a["GND1"][1]), a["GND1"])
        d += elm.Dot().at((xl, a["GND1"][1]))
        xl2 = a["VIN"][0] - 1.2
        d += elm.Dot().at((xl2, a["VIN"][1]))
        d += elm.Line().endpoints((xl2, a["VIN"][1]), (xl2, b["VCC1"][1]))
        d += elm.Line().endpoints((xl2, b["VCC1"][1]), b["VCC1"])
        d += elm.Dot().at((xl2 - 0.6, a["GND1"][1]))
        d += elm.Line().endpoints((xl2 - 0.6, a["GND1"][1]), (xl2 - 0.6, b["GND1"][1]))
        d += elm.Line().endpoints((xl2 - 0.6, b["GND1"][1]), b["GND1"])
        d += elm.Dot(open=True).at((xl - 1.0, b["INA"][1])).label("TX\n（单片机发出）", "left")
        d += elm.Line().endpoints((xl - 1.0, b["INA"][1]), b["INA"])
        # 右边：现场侧
        xr = a["VOUT"][0] + 2.0
        d += elm.Line().endpoints(a["VOUT"], (xr + 3.6, a["VOUT"][1]))
        d += elm.Line().endpoints(a["GND2"], (xr + 3.6, a["GND2"][1]))
        d += elm.Dot().at((xr, a["VOUT"][1])); d += elm.Dot().at((xr, a["GND2"][1]))
        d += elm.Capacitor().endpoints((xr, a["VOUT"][1]), (xr, a["GND2"][1])).label("输出\n电容", "right")
        d += elm.Dot().at((xr + 2.0, a["VOUT"][1])); d += elm.Dot().at((xr + 2.0, a["GND2"][1]))
        d += elm.Resistor().endpoints((xr + 2.0, a["VOUT"][1]), (xr + 2.0, a["GND2"][1])).label("假负载\n270 Ω", "right")
        d += elm.Dot(open=True).at((xr + 3.6, a["VOUT"][1])).label("现场侧 5 V", "right")
        d += elm.Dot(open=True).at((xr + 3.6, a["GND2"][1])).label("GND2", "right")
        xr2 = b["VCC2"][0] + 0.6
        d += elm.Dot().at((xr2, a["VOUT"][1]))
        d += elm.Line().endpoints((xr2, a["VOUT"][1]), (xr2, b["VCC2"][1]))
        d += elm.Line().endpoints((xr2, b["VCC2"][1]), b["VCC2"])
        d += elm.Dot().at((xr2 + 0.5, a["GND2"][1]))
        d += elm.Line().endpoints((xr2 + 0.5, a["GND2"][1]), (xr2 + 0.5, b["GND2"][1]))
        d += elm.Line().endpoints((xr2 + 0.5, b["GND2"][1]), b["GND2"])
        d += elm.Line().endpoints(b["OUTA"], (xr + 3.6, b["OUTA"][1]))
        d += elm.Dot(open=True).at((xr + 3.6, b["OUTA"][1])).label("到现场侧\n传感器 / 设备", "right")
        barrier(d, xm, b["GND1"][1] - 1.0, a["VIN"][1] + 2.0)
    print("[图 24-p2-3] NME0505SC、ISO7721、270 Ω、5 V")
    schem.save_schem(d, P, "24_p2_3_system.png")


def p3_1():
    """图 24-p3-1：示波器地夹和 USB 线经大地把 GND1、GND2 连起来。"""
    fig, ax = fs.diagram(8.6, 3.4)
    a = fs.box(ax, 1.4, 2.4, "单片机侧\nGND1", w=1.9, h=0.8)
    m = fs.box(ax, 4.3, 2.4, "隔离模块 +\n数字隔离器", w=2.0, h=0.8)
    b = fs.box(ax, 7.2, 2.4, "现场侧\nGND2", w=1.9, h=0.8)
    pc = fs.box(ax, 1.4, 0.6, "电脑\n（USB 线）", w=1.9, h=0.8)
    sc = fs.box(ax, 7.2, 0.6, "示波器\n（三孔插头）", w=1.9, h=0.8)
    fs.arrow(ax, a["r"], m["l"]); fs.arrow(ax, m["r"], b["l"])
    ax.plot([4.3, 4.3], [1.9, 2.9], color=fs.C["ref"], ls="--", lw=1.2)
    fs.arrow(ax, a["b"], pc["t"], color=fs.C["bad"])
    ax.text(1.5, 1.5, "USB 地线", fontsize=9, color=fs.C["bad"])
    fs.arrow(ax, b["b"], sc["t"], color=fs.C["bad"])
    ax.text(7.3, 1.5, "探头地夹", fontsize=9, color=fs.C["bad"])
    ax.plot([pc["r"][0], sc["l"][0]], [0.6, 0.6], color=fs.C["bad"], marker="x", markevery=[1], lw=1.4)
    ax.text(4.3, 0.7, "可能经插座地线连通 ×", ha="center", va="bottom", fontsize=9, color=fs.C["bad"])
    ax.text(4.3, 0.45, "GND1 和 GND2 绕过隔离带连在了一起", ha="center", va="top", fontsize=9, color=fs.C["bad"])
    ax.set_ylim(-0.1, 3.3)
    print("[图 24-p3-1] 无数字")
    fs.save(fig, P, "24_p3_1_scope.png")


p1_1(); p2_1(); p2_3(); p3_1()
print("[完成] 24_figs.py")
