"""21 线性稳压：电路图（schemdraw）。运行：/workspace/circuits-venv/bin/python code/figs/21_figs.py
图上的数字与 code/21_sim.py 的打印一致（V_ref 4.82 V、V_o 8.51 V、运放输出 9.26 V），本脚本也会打印它们。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem
from schem import elm
from batt_pm import pm as bat_pm        # 电池旁的 + / − 小字（长线 = +）

P = "21"
VZ0 = 5.1 - 7.0 * 0.049                  # 1N4733A 击穿起点（见 17 page2）
VREF = VZ0 + 7.0 * (14.0 - VZ0) / 1007.0   # 14 V 输入、R_Z 1 kΩ 时的基准
RF, R1 = 3900.0, 5100.0
VO = VREF * (1 + RF / R1)
VB = VO + 0.755


def regulator(d, detail):
    """画出「基准 + 误差放大 + 调整管」三块。detail=True 时标元件值和电压。"""
    top = 6.0
    d += elm.Dot(open=True).at((0, top)).label("$V_i$\n14 V（带纹波）" if detail else "$V_i$\n整流滤波后", "left")
        # 基准：R_Z + 稳压管
    d += elm.Dot().at((1.5, top))
    d += elm.Resistor().endpoints((1.5, top), (1.5, 3.0)).label("$R_Z$\n1 kΩ" if detail else "$R_Z$", "bottom")
    d += elm.Dot().at((1.5, 3.0))
    d += elm.Zener().endpoints((1.5, 0), (1.5, 3.0)).label("1N4733A\n5.1 V" if detail else "稳压管", "bottom")
    # 误差放大器
    op = elm.Opamp(leads=True).right().anchor("in2").at((3.2, 3.0))
    d += op
    d += elm.Line().endpoints((1.5, 3.0), op.in2)
    d += elm.Label().at((1.3, 3.0)).label(f"$V_{{ref}}$\n{VREF:.2f} V" if detail else "$V_{ref}$", loc="left")
    # 调整管
    q = elm.BjtNpn().theta(0).anchor("base").at((op.out[0] + 1.2, op.out[1]))
    d += q
    d += elm.Line().endpoints(op.out, q.base)
    if detail:
        d += elm.Label().at((op.out[0] + 0.55, op.out[1] + 0.35)).label(f"{VB:.2f} V", loc="center")
    cx = q.collector[0]
    d += elm.Line().endpoints((0, top), (cx, top))
    d += elm.Line().endpoints(q.collector, (cx, top))
    d += elm.Label().at((cx + 1.3, q.center[1] + 0.2)).label("调整管\nTIP31" if detail else "射极跟随器", loc="center")
    qx = q.emitter[0]
    ex = qx + 2.7          # 让 R_f 在发射极右边 1.2 处
    d += elm.Line().endpoints(q.emitter, (q.emitter[0], 1.9))
    d += elm.Line().endpoints((qx, 1.9), (ex + 2.0, 1.9))
    # 分压反馈：R_f、R_1
    d += elm.Dot().at((ex - 1.5, 1.9))
    d += elm.Resistor().endpoints((ex - 1.5, 1.9), (ex - 1.5, -0.3)).label("$R_f$ 3.9 kΩ" if detail else "$R_f$", "bottom")
    d += elm.Dot().at((ex - 1.5, -0.3))
    d += elm.Resistor().endpoints((ex - 1.5, -0.3), (ex - 1.5, -2.5)).label("$R_1$ 5.1 kΩ" if detail else "$R_1$", "bottom")
    # 反馈线回到运放反相端
    d += elm.Line().endpoints(op.in1, (op.in1[0] - 0.4, op.in1[1]))
    d += elm.Line().endpoints((op.in1[0] - 0.4, op.in1[1]), (op.in1[0] - 0.4, -0.3))
    d += elm.Line().endpoints((op.in1[0] - 0.4, -0.3), (ex - 1.5, -0.3))
    d += elm.Label().at((op.in1[0] - 0.2, -0.65)).label("反馈：把输出的一部分送回反相端", loc="right")
    if detail:
        d += elm.Capacitor().endpoints((ex + 0.4, 1.9), (ex + 0.4, -2.5)).label("$C_o$\n10 µF", "bottom")
        d += elm.Dot().at((ex + 0.4, 1.9))
        d += elm.Dot().at((ex + 0.4, -2.5))
        d += elm.Resistor().endpoints((ex + 2.0, 1.9), (ex + 2.0, -2.5)).label("负载\n0.5 A", "bottom")
    else:
        d += elm.Resistor().endpoints((ex + 2.0, 1.9), (ex + 2.0, -2.5)).label("负载", "bottom")
    d += elm.Line().endpoints((ex + 2.0, 1.9), (ex + 3.2, 1.9))
    d += elm.Dot(open=True).at((ex + 3.2, 1.9)).label(f"$V_o$\n{VO:.2f} V" if detail else "$V_o$\n稳定", "right")
    d += elm.Line().endpoints((1.5, 0), (1.5, -2.5))
    d += elm.Line().endpoints((1.5, -2.5), (ex + 3.2, -2.5))
    d += elm.Dot(open=True).at((ex + 3.2, -2.5)).label("0 V", "right")
    d += elm.Dot().at((ex - 1.5, -2.5))
    d += elm.Dot().at((ex + 2.0, -2.5))


def p1_1():
    with schem.drawing(fontsize=11) as d:
        regulator(d, detail=False)
        d += elm.Label().at((1.5, 6.6)).label("① 基准", loc="center")
        d += elm.Label().at((4.6, 4.9)).label("② 误差放大", loc="center")
        d += elm.Label().at((6.2, 6.6)).label("③ 调整管", loc="center")
    schem.save_schem(d, P, "21_p1_1_blocks.png")


def p2_1():
    with schem.drawing(fontsize=11) as d:
        regulator(d, detail=True)
        d += elm.Label().at((4.6, 4.9)).label("LM358（由 $V_i$ 供电）", loc="center")
    print(f"[图 21-p2-1] V_ref {VREF:.2f} V、运放输出 {VB:.2f} V、V_o {VO:.2f} V、R_Z 1 kΩ、R_f 3.9 kΩ、R_1 5.1 kΩ、C_o 10 µF、0.5 A")
    assert abs(VO - 8.51) < 0.005
    schem.save_schem(d, P, "21_p2_1_detail.png")


def p2_3():
    """变体：7805 三端稳压器的典型接法（TI uA78xx 手册的测试电路电容值）。"""
    with schem.drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 3)).label("$V_i$\n7–25 V", "left")
        d += elm.Line().endpoints((0, 3), (3, 3))
        d += elm.Dot().at((1.5, 3))
        d += elm.Capacitor().endpoints((1.5, 3), (1.5, 0)).label("$C_i$\n0.33 µF", "bottom")
        for a, b in (((3, 2.2), (5.5, 2.2)), ((5.5, 2.2), (5.5, 3.8)), ((5.5, 3.8), (3, 3.8)), ((3, 3.8), (3, 2.2))):
            d += elm.Line().endpoints(a, b)
        d += elm.Label().at((4.25, 3.35)).label("7805", loc="center")
        d += elm.Label().at((3.15, 2.75)).label("IN", loc="right")
        d += elm.Label().at((5.35, 2.75)).label("OUT", loc="left")
        d += elm.Label().at((4.25, 2.45)).label("GND", loc="center")
        d += elm.Line().endpoints((5.5, 3), (8, 3))
        d += elm.Dot().at((6.5, 3))
        d += elm.Capacitor().endpoints((6.5, 3), (6.5, 0)).label("$C_o$\n0.1 µF", "bottom")
        d += elm.Dot(open=True).at((8, 3)).label("$V_o$\n5 V", "right")
        d += elm.Line().endpoints((4.25, 2.2), (4.25, 0))
        d += elm.Line().endpoints((0, 0), (8, 0))
        d += elm.Dot().at((1.5, 0)); d += elm.Dot().at((4.25, 0)); d += elm.Dot().at((6.5, 0))
        d += elm.Dot(open=True).at((0, 0)).label("0 V", "left")
        d += elm.Dot(open=True).at((8, 0)).label("0 V", "right")
        d += elm.Label().at((4.0, -0.8)).label("两只电容都要贴着芯片引脚焊", loc="center")
    print("[图 21-p2-3] 7805：V_i 7–25 V、C_i 0.33 µF、C_o 0.1 µF、V_o 5 V")
    schem.save_schem(d, P, "21_p2_3_7805.png")


if __name__ == "__main__":
    p1_1(); p2_1(); p2_3()
    print("21_figs OK")

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
# 导线颜色：正电源 = 橙色，0 V（地）= 黑色，负电源 = 蓝色，信号 = 绿色。
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
    def wire(self, h1, h2, kind="sig", bend=0.0, via=(), hops=(), hop_r=0.3):
        """via：中间拐点（走在两列孔之间，避免压孔）；hops：竖直线段跨过电源轨线的 y 值，画成半圆「跨线弯」，表示从上面跨过、不接轨。"""
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
            pts = [(x1, y1)] + list(via) + [(x2, y2)]
            xs, ys = [pts[0][0]], [pts[0][1]]
            for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
                if xa == xb:                                   # 竖直段：在跨轨处插半圆
                    sgn = 1 if yb > ya else -1
                    for yh in sorted([h for h in hops if min(ya, yb) + hop_r < h < max(ya, yb) - hop_r], key=lambda h: sgn * h):
                        th = np.linspace(-np.pi / 2, np.pi / 2, 15)
                        xs += list(xa - hop_r * np.cos(th)); ys += list(yh + sgn * hop_r * np.sin(th))
                xs.append(xb); ys.append(yb)
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
        """测量点：在孔上画紫色空心圈并写上名字。"""
        x, y = self.xy(h)
        self.ax.plot(x, y, "o", ms=9, mfc="none", mec=C["third"], mew=1.6, zorder=9)
        self.ax.text(x + dx, y + dy, text, fontsize=7.5, color=C["third"], ha=ha, va="bottom", zorder=9,
                     bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))

    def note(self, x, y, text, **kw):
        self.ax.text(x, y, text, fontsize=8, **kw)

    def legend(self, kinds=("pos", "gnd", "neg", "sig")):
        from matplotlib.lines import Line2D
        names = dict(pos="正电源线（橙）", gnd="0 V 地线（黑）", neg="负电源线（蓝）", sig="信号线（绿）")
        hs = [Line2D([], [], color=BB_WIRE[k], lw=2.4, label=names[k]) for k in kinds]
        self.ax.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, 0.035), ncol=len(hs), fontsize=8,
                       frameon=False)


def bb08():
    """21 page4：12 V 直流输入的分立线性稳压。LM358（5–8 脚那一半空闲）、TIP31、1N4733A、R_Z 1k、R_f 3.9k、R_1 5.1k。
    下方两条轨接电源（外侧 +12 V、内侧 0 V），右端用两根跳线连到上方两条轨；负载功率电阻放在面包板外，用两根线引出。"""
    bb = Breadboard(ncol=30, rails=dict(tp=("+12 V", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"), bn=("+12 V", "pos")),
                    figsize=(10, 5.6))
    bb.wire(bb.ext((-2.0, -3.4), "12 V 直流电源 +", "pos"), "bn1", "pos")
    bb.wire(bb.ext((-2.0, -2.2), "12 V 直流电源 −", "gnd"), "bp2", "gnd")
    bb.wire("bn28", "tp28", "pos", bend=0.0)
    bb.wire("bp29", "tn29", "gnd", bend=0.0)
    bb.dip8("U1", 13, "LM358")
    bb.wire("a13", "tp13", "pos")                 # 8 脚 V+ → +12 V
    bb.wire("j16", "bp16", "gnd")                 # 4 脚 GND
    bb.wire("c14", "c15", "sig")                  # 空闲的那一半：7 脚接 6 脚
    bb.wire("a16", "tn16", "gnd")                 # 5 脚接地
    # 调整管 TIP31：金属片朝后，脚朝下，从左到右 B、C、E
    bb.multi("Q1", {"B": "f8", "C": "f9", "E": "f10"}, "TIP31", w=3.0, at=(9.0, 4.1))
    bb.wire("j9", "bn9", "pos")                   # 集电极 → +12 V
    bb.wire("g8", "g13", "sig")                   # 运放 1 脚 → 基极
    bb.two("Rf", "i10", "i14", "R", "Rf 3.9k", lpos=(0, -0.62))
    bb.two("R1", "j14", "bp14", "R", "R1 5.1k", lpos=(0.35, 0))
    # 基准：+12 V → R_Z → 稳压管阴极（第 19 列）→ 3 脚
    bb.wire("j17", "bn17", "pos")
    bb.two("RZ", "i17", "i19", "R", "RZ 1k", lpos=(0, -0.62))
    bb.two("DZ", "g20", "g19", "Z", "1N4733A", lpos=(1.6, 0.55))
    bb.wire("j20", "bp20", "gnd")
    bb.wire("h15", "h19", "sig")
    # 负载：功率电阻放在板外
    # j10 引出线：先横移半格走到第 10、11 列孔之间，再竖直向下，在两条下方电源轨线处画「跨线弯」，表示从轨上方跨过、不接轨
    bb.wire("j10", bb.ext((10.5, -5.0), "接负载 RL 一端", "sig", dx=0.45, ha="left"), "sig",
            via=[(10.5, -1.0)], hops=[BB_RAIL_Y["bp"] + 0.32, BB_RAIL_Y["bn"] - 0.32])
    bb.wire(bb.ext((5.0, -5.0), "RL 另一端", "gnd", dx=-0.45, ha="right"), "bp5", "gnd")
    # 连接检查
    assert bb.connected("tp1", "bn1") and bb.connected("tn1", "bp1") and not bb.connected("tp1", "tn1")
    assert bb.connected("U1.8", "bn1") and bb.connected("U1.4", "bp1") and bb.connected("U1.5", "bp1")
    assert bb.connected("U1.6", "U1.7")
    assert bb.connected("Q1.C", "bn1") and bb.connected("Q1.B", "U1.1")
    assert bb.connected("Q1.E", "Rf.1") and bb.connected("Rf.2", "U1.2") and bb.connected("R1.1", "U1.2")
    assert bb.connected("R1.2", "bp1")
    assert bb.connected("RZ.1", "bn1") and bb.connected("RZ.2", "DZ.2") and bb.connected("DZ.2", "U1.3")
    assert bb.connected("DZ.1", "bp1")
    assert not bb.connected("Q1.E", "Q1.B") and not bb.connected("U1.2", "U1.3") and not bb.connected("U1.1", "U1.2")
    bb.probe("f19", "V_ref", dx=0.3, dy=0.35)
    bb.probe("g14", "反相端", dx=0.3, dy=0.35)
    bb.probe("h13", "运放输出", dx=-0.3, dy=-0.35, ha="right")
    bb.probe("h10", "V_o", dx=-0.3, dy=0.0, ha="right")
    bb.note(21.5, 1.4, "C_o 不接（见正文）")
    bb.legend(("pos", "gnd", "sig"))
    print(f"21 p4 面包板：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def p4_breadboards():
    bb = bb08()
    fs.save(bb.fig, P, "21_p4_1_bb_regulator.png")
    plt.close(bb.fig)
    print("21_figs p4 OK")


if __name__ == "__main__":
    p4_breadboards()


# ======================================================================
# 第 8 轮补图：page1–page3 正文讲到的电路连接（不动上面的图号）
# ======================================================================
from schem import *                    # drawing / save_schem / elm
HL = C["bad"]                          # 强调色：新加的、要注意的元件


def p1_4_zener_follower():
    """图 21-p1-4：17 节末尾的「稳压管 + 射极跟随器」，输出被钉在 V_Z − V_BE。"""
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 4)).label("$V_i$", "left")
        d += elm.Dot().at((1.5, 4))
        d += elm.Resistor().endpoints((1.5, 4), (1.5, 1.5)).label("$R_Z$", "bottom")
        d += elm.Dot().at((1.5, 1.5))
        d += elm.Zener().endpoints((1.5, -1.5), (1.5, 1.5)).label("稳压管", "bottom")
        d += elm.Label().at((1.3, 1.5)).label("$V_Z$", loc="left")
        q = elm.BjtNpn().theta(0).anchor("base").at((3.0, 1.5))
        d += q
        d += elm.Line().endpoints((1.5, 1.5), q.base)
        d += elm.Line().endpoints(q.collector, (q.collector[0], 4))
        d += elm.Line().endpoints((0, 4), (q.collector[0], 4))
        d += elm.Label().at((q.center[0] + 1.0, q.center[1] + 0.1)).label("射极跟随器", loc="center", color=HL)
        ex = q.emitter[0]
        d += elm.Line().endpoints(q.emitter, (ex, -0.2))
        d += elm.Dot().at((ex, -0.2))
        d += elm.Resistor().endpoints((ex, -0.2), (ex, -1.5)).label("负载", "bottom")
        d += elm.Line().endpoints((ex, -0.2), (ex + 1.3, -0.2))
        d += elm.Dot(open=True).at((ex + 1.3, -0.2)).label("$V_o = V_Z - V_{BE}$", "right", color=HL)
        d += elm.Line().endpoints((1.5, -1.5), (ex + 1.3, -1.5))
        d += elm.Dot(open=True).at((ex + 1.3, -1.5)).label("0 V", "right")
    print("[图 21-p1-4] V_o = V_Z − V_BE")
    save_schem(d, P, "21_p1_4_zener_follower.png")


def p2_4_ripple_path():
    """图 21-p2-4：输入纹波经 R_Z 与 r_Z 分压漏到基准，再被同相放大 1.765 倍。"""
    dvref = 2.0 * 7.0 / 1007.0
    with drawing(fontsize=11) as d:
        d += elm.SourceSin().endpoints((0, -1.5), (0, 3))
        d += elm.Label().at((-0.9, 0.75)).label("$\\Delta V_i$\n2 V 峰峰", loc="left")
        d += elm.Line().endpoints((0, 3), (0.5, 3))
        d += elm.Resistor().endpoints((0.5, 3), (3.5, 3)).label("$R_Z$ 1 kΩ", "top")
        d += elm.Dot().at((3.5, 3))
        d += elm.Resistor().endpoints((3.5, 3), (3.5, 1.0)).label("$r_Z$ 7 Ω", "bottom").color(HL)
        d += (bt := elm.Battery().endpoints((3.5, 1.0), (3.5, -1.5)).label("$V_{Z0}$\n4.757 V", "bottom"))   # 从上往下画、不 reverse：长线（+）在上，接 r_Z
        bat_pm(d, bt, plus_toward=(3.5, 1.0), side=1)
        d += elm.Line().endpoints((0, -1.5), (3.5, -1.5))
        d += elm.Label().at((5.4, 0.9)).label("稳压管模型\n（电池串小电阻）", loc="right", fontsize=9, color="#666666")
        d += elm.Line().endpoints((3.5, 3), (5.2, 3))
        d += elm.Dot(open=True).at((5.2, 3)).label(f"$\\Delta V_{{ref}}$ ≈ {dvref*1e3:.1f} mV", "top")
        d += elm.Arrow().endpoints((5.6, 3), (8.4, 3)).color(C["vout"]).label("同相放大 ×1.765", "bottom", color=C["vout"])
        d += elm.Label().at((8.6, 3)).label(f"输出纹波\n≈ {dvref*1.765e3:.1f} mV", loc="right", color=C["vout"])
    print(f"[图 21-p2-4] ΔV_ref {dvref*1e3:.1f} mV、输出纹波 {dvref*1.765e3:.1f} mV")
    assert abs(dvref * 1e3 - 13.9) < 0.05 and abs(dvref * 1.765e3 - 24.5) < 0.1
    save_schem(d, P, "21_p2_4_ripple_path.png")


def chip3(d, x, y, name, bottom="GND", w=2.5, h=1.6):
    """三端稳压芯片的方框：返回 (IN, OUT, 底脚) 三个引脚坐标。"""
    x1, y1 = x + w, y + h
    for a, b in (((x, y), (x1, y)), ((x1, y), (x1, y1)), ((x1, y1), (x, y1)), ((x, y1), (x, y))):
        d += elm.Line().endpoints(a, b)
    d += elm.Label().at((x + w / 2, y + h * 0.72)).label(name, loc="center")
    d += elm.Label().at((x + 0.15, y + h / 2 - 0.1)).label("IN", loc="right", fontsize=9)
    d += elm.Label().at((x1 - 0.15, y + h / 2 - 0.1)).label("OUT", loc="left", fontsize=9)
    d += elm.Label().at((x + w / 2, y + 0.25)).label(bottom, loc="center", fontsize=9)
    return (x, y + h / 2), (x1, y + h / 2), (x + w / 2, y)


def lm317_core(d, x0=0.0, r1_hl=False):
    """LM317：R1 接 OUT 与 ADJ，R2 接 ADJ 与地。返回 (输出节点 x, 地线 y)。"""
    pin_in, pin_out, adj = chip3(d, x0 + 1.5, 2.2, "LM317", bottom="ADJ")
    d += elm.Dot(open=True).at((x0, pin_in[1])).label("$V_i$", "left")
    d += elm.Line().endpoints((x0, pin_in[1]), pin_in)
    xr = pin_out[0] + 1.2
    d += elm.Line().endpoints(pin_out, (xr + 1.6, pin_out[1]))
    d += elm.Dot().at((xr, pin_out[1]))
    r1 = elm.Resistor().endpoints((xr, pin_out[1]), (xr, 0.6)).label("$R_1$", "bottom")
    d += r1.color(HL) if r1_hl else r1
    d += elm.Dot().at((xr, 0.6))
    d += elm.Line().endpoints(adj, (adj[0], 0.6))
    d += elm.Line().endpoints((adj[0], 0.6), (xr, 0.6))
    d += elm.Resistor().endpoints((xr, 0.6), (xr, -1.6)).label("$R_2$", "bottom")
    d += elm.Line().endpoints((x0, -1.6), (xr + 1.6, -1.6))
    d += elm.Dot(open=True).at((x0, -1.6)).label("0 V", "left")
    return xr, pin_out[1], -1.6


def p2_5_lm317():
    """图 21-p2-5：LM317 可调稳压的接法。"""
    with drawing(fontsize=11) as d:
        xr, yo, yg = lm317_core(d)
        d += elm.Dot(open=True).at((xr + 1.6, yo)).label("$V_o$", "right")
        d += elm.Label().at((xr + 1.6, (yo + 0.6) / 2)).label("$V_{REF}$\n1.25 V", loc="center", color=C["vin"], fontsize=10)
        d += elm.Arrow().endpoints((3.2, 1.6), (3.2, 0.9)).color(C["cur"])
        d += elm.Label().at((3.45, 1.25)).label("$I_{ADJ}$", loc="right", color=C["cur"], fontsize=10)
    print("[图 21-p2-5] LM317：V_REF 1.25 V、R1、R2、I_ADJ")
    save_schem(d, P, "21_p2_5_lm317.png")


def p3_3_lab():
    """图 21-p3-3：第五节动手实验的接法——原理篇电路 + 可调直流电源 + 180 Ω / 18 Ω 负载切换 + 示波器。"""
    top = 6.0
    with drawing(fontsize=11) as d:
        d += elm.SourceV().endpoints((-1.2, -2.5), (-1.2, top))
        d += elm.Label().at((-3.0, 1.75)).label("可调直流电源\n14 V\n限流 0.6 A", loc="left")
        d += elm.Line().endpoints((1.5, 0), (1.5, -2.5))
        d += elm.Line().endpoints((-1.2, top), (1.5, top))
        d += elm.Dot().at((1.5, top))
        d += elm.Resistor().endpoints((1.5, top), (1.5, 3.0)).label("$R_Z$\n1 kΩ", "bottom")
        d += elm.Dot().at((1.5, 3.0))
        d += elm.Zener().endpoints((1.5, 0), (1.5, 3.0)).label("1N4733A", "bottom")
        op = elm.Opamp(leads=True).right().anchor("in2").at((3.2, 3.0))
        d += op
        d += elm.Line().endpoints((1.5, 3.0), op.in2)
        d += elm.Label().at((1.3, 3.0)).label(f"$V_{{ref}}$\n{VREF:.2f} V", loc="left")
        d += elm.Label().at((4.6, 4.9)).label("LM358（由输入供电）", loc="center")
        q = elm.BjtNpn().theta(0).anchor("base").at((op.out[0] + 1.2, op.out[1]))
        d += q
        d += elm.Line().endpoints(op.out, q.base)
        d += elm.Label().at((op.out[0] + 0.55, op.out[1] + 0.35)).label("约 9.2 V", loc="center", fontsize=9)
        cx = q.collector[0]
        d += elm.Line().endpoints((1.5, top), (cx, top))
        d += elm.Line().endpoints(q.collector, (cx, top))
        d += elm.Label().at((cx + 1.2, q.center[1] + 0.2)).label("TIP31\n装散热片", loc="center", color=HL)
        qx = q.emitter[0]; ex = qx + 2.7
        d += elm.Line().endpoints(q.emitter, (qx, 1.9))
        d += elm.Line().endpoints((qx, 1.9), (ex + 4.4, 1.9))
        d += elm.Dot().at((ex - 1.5, 1.9))
        d += elm.Resistor().endpoints((ex - 1.5, 1.9), (ex - 1.5, -0.3)).label("$R_f$ 3.9 kΩ", "bottom")
        d += elm.Dot().at((ex - 1.5, -0.3))
        d += elm.Resistor().endpoints((ex - 1.5, -0.3), (ex - 1.5, -2.5)).label("$R_1$ 5.1 kΩ", "bottom")
        d += elm.Line().endpoints(op.in1, (op.in1[0] - 0.4, op.in1[1]))
        d += elm.Line().endpoints((op.in1[0] - 0.4, op.in1[1]), (op.in1[0] - 0.4, -0.3))
        d += elm.Line().endpoints((op.in1[0] - 0.4, -0.3), (ex - 1.5, -0.3))
        d += elm.Capacitor().endpoints((ex + 0.4, 1.9), (ex + 0.4, -2.5)).label("$C_o$\n10 µF", "bottom")
        d += elm.Dot().at((ex + 0.4, 1.9)); d += elm.Dot().at((ex + 0.4, -2.5))
        d += elm.Dot().at((ex + 2.8, 1.9))
        sw = elm.SwitchSpdt2().down().anchor("a").at((ex + 2.8, 1.9)).color(HL)
        d += sw
        d += elm.Label().at((ex + 3.3, 1.2)).label("S", loc="right", color=HL)
        d += elm.Line().endpoints(sw.b, (ex + 2.0, sw.b[1]))
        d += elm.Line().endpoints(sw.c, (ex + 3.6, sw.c[1]))
        d += elm.Resistor().endpoints((ex + 2.0, sw.b[1]), (ex + 2.0, -2.5)).label("180 Ω\n10 W", "bottom")
        d += elm.Resistor().endpoints((ex + 3.6, sw.c[1]), (ex + 3.6, -2.5)).label("18 Ω\n10 W", "bottom").color(HL)
        d += elm.Dot(open=True).at((ex + 4.4, 1.9)).label(f"$V_o$ {VO:.2f} V\n接示波器", "right")
        d += elm.Line().endpoints((-1.2, -2.5), (ex + 4.4, -2.5))
        d += elm.Dot(open=True).at((ex + 4.4, -2.5)).label("0 V（示波器地）", "right")
        for x in (1.5, ex - 1.5, ex + 2.0, ex + 3.6):
            d += elm.Dot().at((x, -2.5))
        d += elm.Label().at((ex + 2.8, -3.6)).label("开关 S 在 180 Ω（约 0.05 A）和 18 Ω（约 0.47 A）之间切换", loc="center", fontsize=9, color=HL)
    print(f"[图 21-p3-3] 14 V、限流 0.6 A、V_ref {VREF:.2f} V、V_o {VO:.2f} V、180 Ω / 18 Ω")
    save_schem(d, P, "21_p3_3_lab.png")


def p3_4_protect():
    """图 21-p3-4：故障表最后两行的改法。(a) 7812 输出与输入之间反接保护二极管；(b) LM317 加假负载。"""
    with drawing(fontsize=11) as d:
        pin_in, pin_out, gnd = chip3(d, 1.5, 0.8, "7812")
        d += elm.Dot(open=True).at((0, pin_in[1])).label("$V_i$", "left")
        d += elm.Line().endpoints((0, pin_in[1]), pin_in)
        xo = pin_out[0] + 1.5
        d += elm.Line().endpoints(pin_out, (xo + 1.2, pin_out[1]))
        d += elm.Dot().at((0.8, pin_in[1])); d += elm.Dot().at((xo, pin_out[1]))
        d += elm.Line().endpoints((0.8, pin_in[1]), (0.8, 3.2))
        d += elm.Line().endpoints((xo, pin_out[1]), (xo, 3.2))
        d += elm.Diode().endpoints((xo, 3.2), (0.8, 3.2)).color(HL).label("保护二极管（阴极接输入）", "top", color=HL)
        d += elm.Capacitor().endpoints((xo, pin_out[1]), (xo, -1.0)).label("输出电容\n存着 12 V", "bottom")
        d += elm.Dot(open=True).at((xo + 1.2, pin_out[1])).label("$V_o$ 12 V", "right")
        d += elm.Line().endpoints(gnd, (gnd[0], -1.0))
        d += elm.Line().endpoints((0, -1.0), (xo + 1.2, -1.0))
        d += elm.Dot(open=True).at((0, -1.0)).label("0 V", "left")
        d += elm.Label().at((3.2, -2.9)).label("(a) 7812：断电时电容的电从二极管放掉", loc="center")
        X = 10.5
        xr, yo, yg = lm317_core(d, X, r1_hl=False)
        xl = xr + 1.6
        d += elm.Dot().at((xl, yo))
        d += elm.Resistor().endpoints((xl, yo), (xl, yg)).label("假负载", "bottom").color(HL)
        d += elm.Line().endpoints((xl, yo), (xl + 1.0, yo))
        d += elm.Dot(open=True).at((xl + 1.0, yo)).label("$V_o$", "right")
        d += elm.Label().at((X + 3.6, -2.9)).label("(b) LM317：一直接着假负载（或减小 $R_1$）", loc="center")
    print("[图 21-p3-4] 7812 保护二极管、LM317 假负载")
    save_schem(d, P, "21_p3_4_protect.png")


def round8():
    p1_4_zener_follower(); p2_4_ripple_path(); p2_5_lm317(); p3_3_lab(); p3_4_protect()
    print("21_figs 第 8 轮补图 OK")


if __name__ == "__main__":
    round8()
