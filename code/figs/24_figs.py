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
        d += elm.Label().at((s1[0] + 3.5, p2[1] - 0.9)).label("次级：与市电隔离", loc="center")
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


# ======================= page4 动手实验篇 =======================
import numpy as np
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

    def sip(self, col, row, label, names, w_extra=0.0, fc="#2b2b2b", tc="w", up=True):
        """单排引脚元件（TO-220 / TO-92 三极管、电位器、SIP 模块等）：引脚从第 col 列起插在 row 排，
        names 是各脚名字列表；元件体画在引脚上方（up=True）或下方。"""
        ax, n = self.ax, len(names)
        x0, y = col, BB_Y[row]
        h = 1.25
        yb = y + 0.25 if up else y - 0.25 - h
        ax.add_patch(FancyBboxPatch((x0 - 0.45, yb), n - 1 + 0.9 + w_extra, h, boxstyle="round,pad=0.04",
                                    fc=fc, ec="k", lw=1.0, zorder=6))
        ax.text(x0 + (n - 1 + w_extra) / 2, yb + h * 0.66, label, color=tc, ha="center", va="center",
                fontsize=8, zorder=8)
        for i, nm in enumerate(names):
            ax.plot([x0 + i, x0 + i], [y, yb + (0 if up else h)], color="0.25", lw=1.4, zorder=5)
            ax.add_patch(Circle((x0 + i, y), 0.17, fc="0.15", ec="none", zorder=7))
            ax.text(x0 + i, yb + h * 0.2, nm, color=tc, ha="center", va="center", fontsize=6.5, zorder=8)

    def probe(self, h, text, dx=0.0, dy=0.0):
        """测量点：紫色圆圈 + 标签。"""
        x, y = self.xy(h)
        self.ax.add_patch(Circle((x, y), 0.36, fc="none", ec=fs.C["third"], lw=1.6, zorder=9))
        self.ax.text(x + dx, y + dy, text, color=fs.C["third"], fontsize=8, ha="center", va="center",
                     zorder=9, fontweight="bold")

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


WIRE["gnd2"] = (fs.C["third"], "隔离侧 0V（3 脚）")
WIRE["out"] = (fs.C["fb"], "隔离侧 +Vo（4 脚）")

# B0505S-1WR3（Mornsun）数据手册 2026.09.07-A/7：5 V 输入 4.5～5.5 V，5 V 输出 200 mA 最大 / 20 mA 最小；
# 满载效率 78/82 %（最小/典型）；输入电流满载 244 mA 典型、257 mA 最大，空载 8 mA 典型；
# 负载调整率（10%→100% 负载）典型 10 %、最大 15 %；纹波 30/75 mVp-p；开关频率 270 kHz；
# 隔离 1500 VDC 1 分钟；绝缘电阻 ≥1000 MΩ（500 VDC）；隔离电容 20 pF 典型；不可热插拔。
# 手册 Fig.1（5 V 输入其他输出的输出调整曲线）读图：10% 负载时 Max +10 %、Typ +5 %、Min 0 %，
# 100% 负载时 Max +2.5 %、Typ −2.5 %、Min −7.5 %，三条近似平行的直线。低于 10% 负载手册不给。
BS_CURVE = dict(typ=(5.0, -2.5), max=(10.0, 2.5), min=(0.0, -7.5))     # (10% 负载, 100% 负载) 的偏差 / %
BS_IMAX, BS_ETA, BS_IIN_NL = 0.200, (0.78, 0.82), 8e-3
P4_LOADS = {"240 Ω": 240.0, "51 Ω": 51.0, "25 Ω": 25.0}


def bs_dev(frac, which="typ"):
    """手册 Fig.1 的直线：负载占额定的比例 frac（0.1～1.0）→ 输出偏差 / %。"""
    a, b = BS_CURVE[which]
    return a + (b - a) * (frac - 0.1) / 0.9


def bs_vout(r, which="typ"):
    """输出接电阻 r 时的工作点：V = 5·(1 + 偏差(V/r/0.2)/100)，用不动点迭代解。"""
    v = 5.0
    for _ in range(60):
        v = 5.0 * (1 + bs_dev(v / r / BS_IMAX, which) / 100)
    return v


def fig_p4_1():
    """图 24-p4-1：B0505S 隔离模块实验的面包板接线（上面两条轨是输入侧，下面两条轨是隔离侧）。"""
    bb = Breadboard(30, "B0505S 隔离模块实验面包板俯视图（上两条轨 = 输入侧，下两条轨 = 隔离侧）",
                    size=(12.0, 6.6), rails=("+5 V", "GND", "0V", "+Vo"))
    ax = bb.ax
    ax.set_xlim(-3.6, 38.5)
    bb.sip(8, "c", "B0505S", ["GND", "Vin", "0V", "+Vo"], w_extra=0.0)   # 1 脚 c8、2 脚 c9、3 脚 c10、4 脚 c11
    ax.text(7.5, 5.5, "1", fontsize=7, ha="center", color="0.25")
    # 输入侧
    bb.wire("a8", "T-8", "gnd")
    bb.wire("a9", "T+9", "pos")
    bb.part("T+4", "T-4", "C_in 4.7 μF", "E", lab_side="r")
    bb.module(-3.4, 9.6, 4.2, 1.5, "5 V 电源\n（USB 电源模块）")
    bb.wire((0.8, 10.35), "T+1", "pos", via=[(1.0, 10.35)])
    bb.wire((-1.3, 9.6), "T-2", "gnd", via=[(-1.3, 8.15), (2.0, 8.15)])
    # 隔离侧：3、4 脚跨过凹槽，再接到下面两条轨
    bb.wire("e10", "f10", "gnd2")
    bb.wire("j10", "B-10", "gnd2")
    bb.wire("e11", "f11", "out")
    bb.wire("j11", "B+11", "out", via=[(11.0, -7.15), (11.0, -7.15)])
    bb.part("B+14", "B-14", "C_out 10 μF", "E", lab_side="r")
    bb.part("B+20", "B-20", "R_L（空 / 240 Ω / 51 Ω / 25 Ω）", "R", lab_side="r")
    # 隔离带
    ax.plot([9.5, 9.5], [3.0, 5.4], ls="--", color="0.4", lw=1.4, zorder=9)
    bb.note(9.75, 2.15, "隔离带在模块里面", color="0.3")
    # 测量点
    bb.probe("T-13", "A", dx=0.9)
    bb.probe("T+13", "B", dx=0.9)
    bb.probe("B-26", "C", dx=0.9)
    bb.probe("B+26", "D", dx=0.9)
    bb.note(31.9, 7.2, "A = GND（1 脚）\nB = +5 V（2 脚）", va="center")
    bb.note(31.9, -7.2, "C = 0V（3 脚）\nD = +Vo（4 脚）", va="center")
    bb.note(31.9, 0.0, "上下两组轨之间\n没有任何导线：\n能量只经模块里的\n变压器过去", va="center")
    bb.note(1.0, -12.4, "紫色圈 = 下表笔的位置；断电时用电阻挡量 A、B 对 C、D，通电后用电压挡量 B–A、D–C", ha="left")
    bb.legend()
    bb.save("24", "24_p4_1_breadboard.png")
    print("[接线] B0505S 1 脚 GND c8、2 脚 Vin c9、3 脚 0V c10、4 脚 +Vo c11；a8→GND 轨，a9→+5 V 轨；"
          "C_in 4.7 μF 插在输入侧两轨之间；e10→f10、j10→0V 轨；e11→f11、j11→+Vo 轨；C_out 10 μF 与 R_L 插在隔离侧两轨之间")


def fig_p4_2():
    """图 24-p4-2：按手册 Fig.1 画出的输出电压范围，以及三只负载电阻的预期工作点。"""
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    fr = np.linspace(0.1, 1.0, 50)
    i_ma = fr * BS_IMAX * 1e3
    vt = 5 * (1 + bs_dev(fr, "typ") / 100)
    vmx = 5 * (1 + bs_dev(fr, "max") / 100)
    vmn = 5 * (1 + bs_dev(fr, "min") / 100)
    ax.fill_between(i_ma, vmn, vmx, color=fs.C["vout"], alpha=0.18, lw=0, label="手册 Max～Min 范围")
    ax.plot(i_ma, vt, color=fs.C["vout"], lw=2.0, label="手册典型（Typ）")
    ax.axvspan(0, 20, color="0.88", zorder=0)
    ax.text(10, 5.6, "低于 10%\n负载\n手册不保证", ha="center", va="center", fontsize=8.5, color="0.3")
    fs.ref_h(ax, 5.5, "ISO7721 推荐上限 5.5 V")
    cols = [fs.C["vin"], fs.C["fb"], fs.C["third"]]
    for (name, r), c in zip(P4_LOADS.items(), cols):
        v, lo, hi = bs_vout(r), bs_vout(r, "min"), bs_vout(r, "max")
        i = v / r * 1e3
        ax.plot([0, 230], [0, 230 * r / 1e3], color=c, lw=1.0, ls=":")
        ax.plot([i], [v], "o", color=c, ms=7, zorder=5)
        ax.annotate(f"{name}：{v:.2f} V，{i:.0f} mA", (i, v), xytext=(6, 10) if r > 30 else (-118, -20), textcoords="offset points",
                    color=c, fontsize=9)
        print(f"[数值] R_L {name}：典型 {v:.3f} V、{i:.1f} mA（{i / 2:.1f}% 负载），范围 {lo:.2f}～{hi:.2f} V，"
              f"电阻功耗 {v * v / r:.3f} W")
    ax.set_xlim(0, 230)
    ax.set_ylim(4.3, 5.8)
    fs.axlabels(ax, "输出电流", "mA", "输出电压（D 对 C）", "V")
    ax.set_title("B0505S 输出电压随负载变化（按手册 Fig.1 读图）", fontsize=10.5)
    ax.legend(fontsize=8.5, loc="lower center")
    fs.save(fig, "24", "24_p4_2_load.png")
    v25 = bs_vout(25.0)
    p_out = v25 ** 2 / 25.0
    for eta in BS_ETA:
        print(f"[数值] 25 Ω：输出 {p_out:.3f} W，效率 {eta:.0%} 时输入 {p_out / eta:.3f} W、输入电流 {p_out / eta / 5 * 1e3:.0f} mA")
    print(f"[数值] 负载调整：240 Ω → 25 Ω 典型下降 {bs_vout(240.0) - v25:.3f} V；手册最大 15% = 0.75 V")


fig_p4_1(); fig_p4_2()


# ======================= 第 8 轮补电路图（page1–page3：凡正文讲具体电路连接处，附近都要有电路图） =======================
from schem import *
from schem import C as _C
EMPH = _C["third"]      # 强调色（红紫）：新加的元件、测量点
BAD = _C["bad"]         # 朱红：带市电 / 错误


def _xf_bridge(d, title, v2, out, cap="滤波电容", ldo=None):
    """工频变压器 + 桥式整流 + 电容滤波（可选再接 LDO）。初级画成朱红色（带市电，只画不做）。返回输出端 x。"""
    d += (t := elm.Transformer(t1=4, t2=4).anchor("p2").at((0, 0)))
    p1, p2, s1, s2 = (t.absanchors[k] for k in ("p1", "p2", "s1", "s2"))
    xs = p1[0] - 3.6
    d += elm.SourceSin().endpoints((xs, p2[1]), (xs, p1[1])).color(BAD)
    d += elm.Label().at((xs - 0.7, 0.8)).label("220 V\n市电", halign="right", color=BAD)
    d += elm.FuseIEC().endpoints((xs, p1[1]), (p1[0] - 0.4, p1[1])).color(BAD).label("保险丝", "top", color=BAD)
    d += elm.Line().endpoints((p1[0] - 0.4, p1[1]), p1).color(BAD)
    d += elm.Line().endpoints((xs, p2[1]), p2).color(BAD)
    d += elm.Label().at((xs + 1.6, -0.9)).label("初级带市电：只画不做", color=BAD, fontsize=10)
    barrier(d, 0.5, -2.9, 3.6, "隔离带（绕组之间）")
    d += elm.Label().at((0.5, 4.6)).label(title, fontsize=11)
    d += elm.Label().at((s1[0] + 0.25, 2.25)).label(v2, halign="left", fontsize=10)
    xw = 4.4
    d += (r := elm.Rectifier().theta(-90).anchor("W").at((xw, 3.0)))
    A = r.absanchors
    d += elm.Line().endpoints(s1, (s1[0], A["W"][1]))
    d += elm.Line().endpoints((s1[0], A["W"][1]), A["W"])
    d += elm.Line().endpoints(s2, (s2[0], A["E"][1]))
    d += elm.Line().endpoints((s2[0], A["E"][1]), A["E"])
    gy = -2.4
    d += elm.Line().endpoints(A["S"], (A["S"][0], gy))
    d += elm.Label().at((A["S"][0] - 0.3, A["S"][1] + 0.3)).label("−", fontsize=12)
    d += elm.Label().at((A["N"][0] + 0.3, A["N"][1] + 0.35)).label("+", fontsize=12)
    xc = A["N"][0] + 1.2
    y = A["N"][1]
    d += elm.Line().endpoints(A["N"], (xc, y))
    d += elm.Dot().at((xc, y)); d += elm.Dot().at((xc, gy))
    d += elm.Capacitor(polar=True).endpoints((xc, y), (xc, gy))
    d += elm.Label().at((xc + 0.45, (y + gy) / 2)).label(cap, halign="left", fontsize=10)
    xo = xc + 2.4
    if ldo:
        d += (u := module(ldo, ("IN", "GND"), ("OUT",), w=2.4).right().anchor("IN").at((xc + 2.6, y)))
        d += elm.Line().endpoints((xc, y), u.absanchors["IN"])
        g = u.absanchors["GND"]
        d += elm.Line().endpoints(g, (xc + 1.6, g[1])); d += elm.Line().endpoints((xc + 1.6, g[1]), (xc + 1.6, gy))
        d += elm.Dot().at((xc + 1.6, gy))
        d += elm.Label().at((xc + 0.6, y + 0.45)).label(out, fontsize=10)
        o = u.absanchors["OUT"]
        xo = o[0] + 1.4
        d += elm.Line().endpoints(o, (xo, o[1]))
        d += elm.Dot(open=True).at((xo, o[1])).label("5 V", "right")
    else:
        d += elm.Line().endpoints((xc, y), (xo, y))
        d += elm.Dot(open=True).at((xo, y)).label(out, "right")
    d += elm.Line().endpoints((A["S"][0], gy), (xo, gy))
    d += elm.Dot(open=True).at((xo, gy)).label("GND2", "right")
    return xo


def _nme(d, name="NME0505SC", vin="+5 V", src=True):
    """隔离 DC-DC 模块：左 VIN/GND1，右 VOUT/GND2；左侧画 5 V 电源。返回四个引脚坐标。"""
    d += (m := module(f"隔离 DC-DC 模块\n{name}", ("VIN", "GND1"), ("VOUT", "GND2"), w=3.4).right().at((0, 0)))
    a = {k: m.absanchors[k] for k in ("VIN", "GND1", "VOUT", "GND2")}
    xl = a["VIN"][0] - 2.4
    d += elm.Line().endpoints((xl, a["VIN"][1]), a["VIN"])
    d += elm.Line().endpoints((xl, a["GND1"][1]), a["GND1"])
    if src:
        d += elm.SourceV().endpoints((xl, a["GND1"][1]), (xl, a["VIN"][1]))
        d += elm.Label().at((xl - 0.7, (a["VIN"][1] + a["GND1"][1]) / 2)).label(vin, halign="right")
    xm = (a["VIN"][0] + a["VOUT"][0]) / 2
    barrier(d, xm, a["GND2"][1] - 1.6, a["VIN"][1] + 2.3)
    return a


def fig_p1_3():
    """图 24-p1-3：交流侧方案：220 V → 保险丝 → 变压器 → 桥式整流 → 电容滤波，约 15.57 V。"""
    with drawing(fontsize=11) as d:
        _xf_bridge(d, "变压器 220 V → 12 V", "12 V", f"约 {V_DC:.2f} V 直流")
    print(f"[图 24-p1-3] 220 V → 12 V，整流滤波后约 {V_DC:.2f} V")
    save_schem(d, P, "24_p1_3_xfmr_bridge.png")


def fig_p1_4():
    """图 24-p1-4：断电后万用表电阻挡测 GND1 与 GND2，应为开路。"""
    with drawing(fontsize=11) as d:
        a = _nme(d, vin="+5 V\n（断开）")
        xr = a["VOUT"][0] + 2.0
        d += elm.Line().endpoints(a["VOUT"], (xr, a["VOUT"][1]))
        d += elm.Line().endpoints(a["GND2"], (xr, a["GND2"][1]))
        d += elm.Resistor().endpoints((xr, a["VOUT"][1]), (xr, a["GND2"][1]))
        d += elm.Label().at((xr + 0.45, a["VOUT"][1] - 0.5)).label("现场侧\n电路", halign="left")
        xl = a["VIN"][0] - 2.4
        y = a["GND2"][1] - 1.4
        d += elm.Dot().at((xl, a["GND1"][1])); d += elm.Dot().at((xr, a["GND2"][1]))
        d += elm.Line().endpoints((xl, a["GND1"][1]), (xl, y)).color(EMPH)
        d += elm.Line().endpoints((xl, y), (-0.2, y)).color(EMPH)
        d += elm.MeterOhm().endpoints((-0.2, y), (3.6, y)).color(EMPH)
        d += elm.Line().endpoints((3.6, y), (xr, y)).color(EMPH)
        d += elm.Line().endpoints((xr, y), (xr, a["GND2"][1])).color(EMPH)
        d += elm.Label().at((1.7, y - 1.0)).label("万用表电阻挡：GND1 ↔ GND2，应开路", color=EMPH, fontsize=10)
    save_schem(d, P, "24_p1_4_gnd_check.png")


def fig_p2_5():
    """图 24-p2-5：隔离 DC-DC 模块内部示意：开关切成约 110 kHz 方波 → 环形变压器 → 整流、电容滤波。"""
    with drawing(fontsize=11) as d:
        d += elm.SourceV().endpoints((-4.0, 0), (-4.0, 1.6))
        d += elm.Label().at((-4.7, 0.8)).label("5 V", halign="right")
        d += (sw := module("", ("+", "−"), ("A", "B"), w=3.0).right().anchor("+").at((-2.6, 1.6)))
        S = sw.absanchors
        d += elm.Label().at(((S["+"][0] + S["A"][0]) / 2, (S["+"][1] + S["−"][1]) / 2)).label("开关\n约 110 kHz", fontsize=10)
        d += elm.Line().endpoints((-4.0, 1.6), S["+"])
        d += elm.Line().endpoints((-4.0, 0), (-3.2, 0)); d += elm.Line().endpoints((-3.2, 0), (-3.2, S["−"][1])); d += elm.Line().endpoints((-3.2, S["−"][1]), S["−"])
        d += (t := elm.Transformer(t1=4, t2=4).anchor("p1").at((S["A"][0] + 1.4, S["A"][1])))
        T = t.absanchors
        d += elm.Line().endpoints(S["A"], T["p1"])
        d += elm.Line().endpoints(S["B"], (S["B"][0] + 0.7, S["B"][1])); d += elm.Line().endpoints((S["B"][0] + 0.7, S["B"][1]), (S["B"][0] + 0.7, T["p2"][1])); d += elm.Line().endpoints((S["B"][0] + 0.7, T["p2"][1]), T["p2"])
        d += elm.Label().at(((T["p1"][0] + T["s1"][0]) / 2, T["p1"][1] + 0.8)).label("环形变压器", fontsize=10)
        xd = T["s1"][0] + 2.2
        d += elm.Diode().endpoints(T["s1"], (xd, T["s1"][1])).label("整流", "top")
        d += elm.Dot().at((xd, T["s1"][1])); d += elm.Dot().at((xd, T["s2"][1]))
        d += elm.Capacitor().endpoints((xd, T["s1"][1]), (xd, T["s2"][1]))
        d += elm.Label().at((xd + 0.4, (T["s1"][1] + T["s2"][1]) / 2)).label("滤波", halign="left", fontsize=10)
        d += elm.Line().endpoints(T["s2"], (xd + 2.0, T["s2"][1]))
        d += elm.Line().endpoints((xd, T["s1"][1]), (xd + 2.0, T["s1"][1]))
        d += elm.Dot(open=True).at((xd + 2.0, T["s1"][1])).label("VOUT 5 V", "right")
        d += elm.Dot(open=True).at((xd + 2.0, T["s2"][1])).label("GND2", "right")
        xm = (T["p1"][0] + T["s1"][0]) / 2
        barrier(d, xm, T["p2"][1] - 1.6, T["p1"][1] + 1.4, "")
        x0, x1, y0, y1 = -3.4, xd + 1.2, T["p2"][1] - 1.2, T["p1"][1] + 1.6
        for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            d += elm.Line().endpoints(p, q).linestyle(":").color("#808080")
        d += elm.Label().at(((x0 + x1) / 2, y1 + 0.4)).label("NME0505SC 内部（示意，整流只画一只二极管）", fontsize=10)
    save_schem(d, P, "24_p2_5_module_inside.png")


def fig_p2_6():
    """图 24-p2-6：例 1：约 7.4 V 有效值的变压器（N1/N2 ≈ 29.9），整流滤波后约 9 V。"""
    n = math.sqrt(2) * 220 / (9 + 1.4)
    assert abs(n - 29.9) < 0.05
    print(f"[图 24-p2-6] N1/N2 = {n:.1f}，次级 {220/n:.1f} V 有效值")
    with drawing(fontsize=11) as d:
        _xf_bridge(d, f"变压器 N1/N2 ≈ {n:.1f}", f"约 {220/n:.1f} V", "约 9 V 直流")
    save_schem(d, P, "24_p2_6_ex1_9v.png")


def fig_p2_7():
    """图 24-p2-7：例 2：NME0512SC 输出 12 V，并 1.5 kΩ 假负载，再接现场侧 12 V 设备。"""
    with drawing(fontsize=11) as d:
        a = _nme(d, name="NME0512SC")
        xr = a["VOUT"][0] + 2.0
        for x, lab, c in ((xr, "假负载\n1.5 kΩ", EMPH), (xr + 2.9, "现场侧\n12 V 设备", "black")):
            d += elm.Dot().at((x, a["VOUT"][1])); d += elm.Dot().at((x, a["GND2"][1]))
            d += elm.Resistor().endpoints((x, a["VOUT"][1]), (x, a["GND2"][1])).color(c)
            d += elm.Label().at((x + 0.65, (a["VOUT"][1] + a["GND2"][1]) / 2)).label(lab, halign="left", color=c, fontsize=10)
        d += elm.Line().endpoints(a["VOUT"], (xr + 2.9, a["VOUT"][1]))
        d += elm.Line().endpoints(a["GND2"], (xr + 2.9, a["GND2"][1]))
        d += elm.Label().at((xr + 1.3, a["VOUT"][1] + 0.4)).label("12 V，最大 83 mA", fontsize=10)
    save_schem(d, P, "24_p2_7_ex2_dummy.png")


def fig_p2_8():
    """图 24-p2-8：第七部分实验接线：5 V → 模块；输出端负载（270 Ω / 25 Ω 2 W），万用表测 VOUT 对 GND2。"""
    with drawing(fontsize=11) as d:
        a = _nme(d, vin="5 V 直流\n电源")
        xr = a["VOUT"][0] + 2.0
        xv = xr + 3.6
        d += elm.Line().endpoints(a["VOUT"], (xv, a["VOUT"][1]))
        d += elm.Line().endpoints(a["GND2"], (xv, a["GND2"][1]))
        d += elm.Dot().at((xr, a["VOUT"][1])); d += elm.Dot().at((xr, a["GND2"][1]))
        d += elm.Resistor().endpoints((xr, a["VOUT"][1]), (xr, a["GND2"][1])).color(EMPH)
        d += elm.Label().at((xr + 0.65, (a["VOUT"][1] + a["GND2"][1]) / 2)).label("步骤 2：不接\n步骤 3：270 Ω\n步骤 4：25 Ω 2 W", halign="left", color=EMPH, fontsize=10)
        d += elm.MeterV().endpoints((xv, a["VOUT"][1]), (xv, a["GND2"][1])).color(EMPH)
        d += elm.Label().at((xv + 0.9, (a["VOUT"][1] + a["GND2"][1]) / 2)).label("测 VOUT\n对 GND2", halign="left", color=EMPH, fontsize=10)
        # 步骤 5：电压挡测 VOUT 对 GND1（跨隔离带，读数无确定意义），虚线
        xl = a["VIN"][0] - 2.4
        yl = a["GND2"][1] - 1.8
        xx = xv + 4.0
        d += elm.Dot().at((xl, a["GND1"][1])); d += elm.Dot().at((xv, a["VOUT"][1]))
        for p_, q_ in (((xl, a["GND1"][1]), (xl, yl)), ((xl, yl), (xx, yl)), ((xx, yl), (xx, yl + 0.4)), ((xx, a["VOUT"][1] + 0.6), (xx, a["VOUT"][1] + 1.0)), ((xx, a["VOUT"][1] + 1.0), (xv, a["VOUT"][1] + 1.0)), ((xv, a["VOUT"][1] + 1.0), (xv, a["VOUT"][1]))):
            d += elm.Line().endpoints(p_, q_).linestyle("--").color("#808080")
        d += elm.MeterV().endpoints((xx, yl + 0.4), (xx, a["VOUT"][1] + 0.6)).linestyle("--").color("#808080")
        d += elm.Label().at((1.7, yl - 0.9)).label("步骤 5：电压挡测 VOUT 对 GND1（读数无确定意义）", fontsize=10, color="#4d4d4d")
        d += elm.Label().at((1.7, yl - 1.7)).label("每次换电阻前先断电；实验期间输出端不接任何芯片", fontsize=10)
    save_schem(d, P, "24_p2_8_lab.png")


def fig_p3_3():
    """图 24-p3-3：两种补救：(a) 输出端并 270 Ω 假负载；(b) 5.1 V 稳压管串 36 Ω 跨在输出上。"""
    with drawing(fontsize=11) as d:
        for k, x0 in enumerate((0.0, 13.0)):
            d += (m := module("NME0505SC", ("VIN", "GND1"), ("VOUT", "GND2"), w=3.4).right().at((x0, 0)))
            a = {q: m.absanchors[q] for q in ("VIN", "GND1", "VOUT", "GND2")}
            for q in ("VIN", "GND1"):
                d += elm.Line().endpoints((a[q][0] - 1.0, a[q][1]), a[q])
                d += elm.Dot(open=True).at((a[q][0] - 1.0, a[q][1])).label("+5 V" if q == "VIN" else "GND1", "left")
            xm = (a["VIN"][0] + a["VOUT"][0]) / 2
            barrier(d, xm, a["GND2"][1] - 2.4, a["VIN"][1] + 1.9)
            xr = a["VOUT"][0] + 1.6
            xu = xr + 3.2
            yt, yb = a["VOUT"][1], a["GND2"][1] - 1.6
            d += elm.Line().endpoints(a["VOUT"], (xu, yt))
            d += elm.Line().endpoints(a["GND2"], (a["GND2"][0] + 0.6, a["GND2"][1]))
            d += elm.Line().endpoints((a["GND2"][0] + 0.6, a["GND2"][1]), (a["GND2"][0] + 0.6, yb))
            d += elm.Line().endpoints((a["GND2"][0] + 0.6, yb), (xu, yb))
            d += elm.Dot().at((xr, yt)); d += elm.Dot().at((xr, yb))
            if k == 0:
                d += elm.Resistor().endpoints((xr, yt), (xr, yb)).color(EMPH)
                d += elm.Label().at((xr + 0.6, (yt + yb) / 2)).label("假负载\n270 Ω", halign="left", color=EMPH, fontsize=10)
                d += elm.Label().at((x0 + 2.5, yt + 3.5)).label("(a) 假负载", fontsize=11)
            else:
                ym = (yt + yb) / 2
                d += elm.Resistor().endpoints((xr, yt), (xr, ym)).color(EMPH)
                d += elm.Zener().endpoints((xr, yb), (xr, ym)).color(EMPH)
                d += elm.Label().at((xr + 0.6, (yt + ym) / 2)).label("36 Ω", halign="left", color=EMPH, fontsize=10)
                d += elm.Label().at((xr + 0.6, (ym + yb) / 2)).label("5.1 V\n稳压管", halign="left", color=EMPH, fontsize=10)
                d += elm.Label().at((x0 + 2.5, yt + 3.5)).label("(b) 稳压管钳位（1N4733A 类）", fontsize=11)
            d += elm.Dot().at((xu, yt)); d += elm.Dot().at((xu, yb))
            d += elm.Resistor().endpoints((xu, yt), (xu, yb))
            d += elm.Label().at((xu + 0.6, (yt + yb) / 2)).label("现场侧电路\n4.7 mA", halign="left", fontsize=10)
    save_schem(d, P, "24_p3_3_fixes.png")


def fig_p3_4():
    """图 24-p3-4：练习 4：220 V → 9 V 变压器 → 桥式整流 → 大电容 → 5 V LDO。"""
    v = 9 * math.sqrt(2) - 1.4
    print(f"[图 24-p3-4] 9 V 变压器整流后约 {v:.2f} V")
    with drawing(fontsize=11) as d:
        _xf_bridge(d, "变压器 220 V → 9 V", "9 V", "LDO 输入", cap="大电容", ldo="5 V LDO")
    save_schem(d, P, "24_p3_4_ex4_ldo.png")


if __name__ == "__main__":
    fig_p1_3(); fig_p1_4(); fig_p2_5(); fig_p2_6(); fig_p2_7(); fig_p2_8(); fig_p3_3(); fig_p3_4()
