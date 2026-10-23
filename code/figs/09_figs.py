"""09 开关电源：电路图（schemdraw）。运行：/workspace/circuits-venv/bin/python code/figs/09_figs.py
图上的数字与 code/09_sim.py 一致（12 V → 5 V、1 A、200 kHz、47 µH、47 µF、占空比约 44%），本脚本也会打印它们。
全部是低压直流电路；变体二（反激电源次级）的初级接市电，图上只画成方框并写明危险。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem
from schem import elm

P = "09"
VIN, VO, IO, FSW, L_uH, C_uF = 12.0, 5.0, 1.0, 200e3, 47, 47
D = (VO + IO * 0.05 + 0.4) / (VIN - IO * 0.05 + 0.4)
print(f"[数值] V_in {VIN:.0f} V，V_o {VO:.0f} V，I_o {IO:.0f} A，f {FSW/1e3:.0f} kHz，L {L_uH} µH，C {C_uF} µF，D ≈ {D*100:.0f}%")
assert 0.43 < D < 0.45


def output_stage(d, x, top, detail, lab_c="$C_o$", lab_r="负载"):
    """从 (x, top) 开始画电感右边的输出电容、负载和输出端子；返回地线右端 x。"""
    d += elm.Dot().at((x, top))
    d += elm.Capacitor().endpoints((x, top), (x, 0)).label(f"{lab_c}\n{C_uF} µF" if detail else lab_c, "bottom")
    d += elm.Dot().at((x, 0))
    d += elm.Line().endpoints((x, top), (x + 3.0, top))
    d += elm.Resistor().endpoints((x + 3.0, top), (x + 3.0, 0)).label(f"{lab_r}\n5 Ω（1 A）" if detail else lab_r, "bottom")
    d += elm.Dot().at((x + 3.0, top))
    d += elm.Line().endpoints((x + 3.0, top), (x + 4.2, top))
    d += elm.Dot(open=True).at((x + 4.2, top)).label(f"$V_o$\n{VO:.0f} V" if detail else "$V_o$\n平稳的直流", "right")
    d += elm.Line().endpoints((x + 3.0, 0), (x + 4.2, 0))
    d += elm.Dot(open=True).at((x + 4.2, 0)).label("0 V", "right")
    return x + 4.2


def p1_1():
    """直觉版：开关 + 续流二极管 + 电感 + 电容。"""
    top = 4.0
    with schem.drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, top)).label("$V_{in}$\n12 V", "left")
        sw = elm.Switch().endpoints((0, top), (3.0, top)).label("开关：每秒通断 20 万次", "top")
        d += sw
        d += elm.Dot().at((3.0, top))
        d += elm.Schottky().endpoints((3.0, 0), (3.0, top)).label("续流二极管\n开关断开时\n给电流让路", "bottom")
        d += elm.Inductor2().endpoints((3.0, top), (6.0, top)).label("电感：保持电流", "top")
        output_stage(d, 6.0, top, False, lab_c="电容：攒住电压")
        d += elm.Line().endpoints((0, 0), (6.0, 0))
        d += elm.Dot(open=True).at((0, 0)).label("0 V", "left")
        d += elm.Dot().at((3.0, 0))
    schem.save_schem(d, P, "09_p1_1_concept.png")


def high_side(d, x0, top, label):
    """上管 N 沟道 MOSFET：漏极在左（接输入）、源极在右（接开关节点）。返回 (MOSFET, 源极 x)。"""
    q = elm.NFet().theta(90).reverse().anchor("drain").at((x0, top))
    d += q
    d += elm.Label().at((x0 + 0.75, top + 0.75)).label(label, loc="center")
    return q, x0 + 1.5


def p2_1():
    """异步降压：上管 MOSFET + 肖特基续流 + L + C，带元件值与反馈。"""
    top = 4.0
    with schem.drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((-1.2, top)).label(f"$V_{{in}}$\n{VIN:.0f} V", "left")
        d += elm.Line().endpoints((-1.2, top), (0.6, top))
        d += elm.Dot().at((0, top))
        d += elm.Capacitor().endpoints((0, top), (0, 0)).label("$C_{in}$\n10 µF", "top")
        q, sx = high_side(d, 0.6, top, "上管 MOSFET")
        nx = sx + 1.0
        d += elm.Line().endpoints((sx, top), (nx, top))
        d += elm.Dot().at((nx, top))
        d += elm.Label().at((nx + 0.3, top - 0.45)).label("开关节点", loc="center")
        d += elm.Schottky().endpoints((nx, 0), (nx, top)).label("肖特基\n二极管\n0.4 V", "bottom")
        d += elm.Inductor2().endpoints((nx, top), (nx + 3.0, top)).label(f"$L$　{L_uH} µH", "top")
        right = output_stage(d, nx + 3.0, top, True)
        d += elm.Line().endpoints((-1.2, 0), (nx + 3.0, 0))
        d += elm.Dot(open=True).at((-1.2, 0)).label("0 V", "left")
        d += elm.Dot().at((0, 0)); d += elm.Dot().at((nx, 0))
        # 控制器与反馈
        gx, gy = q.absanchors["gate"]
        bx, by = gx + 1.6, -1.6
        d += elm.Line().endpoints((gx, gy), (gx, by + 0.4))
        W = 2.9
        d += elm.Line().endpoints((bx - W, by + 0.4), (bx + W, by + 0.4))
        d += elm.Line().endpoints((bx + W, by + 0.4), (bx + W, by - 0.4))
        d += elm.Line().endpoints((bx + W, by - 0.4), (bx - W, by - 0.4))
        d += elm.Line().endpoints((bx - W, by - 0.4), (bx - W, by + 0.4))
        d += elm.Label().at((bx, by)).label(f"PWM 控制器（{FSW/1e3:.0f} kHz，D ≈ {D*100:.0f}%）", loc="center")
        d += elm.Line().endpoints((right, top), (right, by)).linestyle("--")
        d += elm.Line().endpoints((right, by), (bx + W, by)).linestyle("--")
        d += elm.Label().at(((right + bx + W) / 2, by - 0.35)).label("反馈：测输出，调占空比", loc="center")
    schem.save_schem(d, P, "09_p2_1_async.png")


def p2_4():
    """同步降压：下管 MOSFET 代替二极管。"""
    top = 4.0
    with schem.drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((-1.2, top)).label(f"$V_{{in}}$\n{VIN:.0f} V", "left")
        d += elm.Line().endpoints((-1.2, top), (0.6, top))
        d += elm.Dot().at((0, top))
        d += elm.Capacitor().endpoints((0, top), (0, 0)).label("$C_{in}$", "bottom")
        q, sx = high_side(d, 0.6, top, "上管")
        nx = sx + 1.2
        d += elm.Line().endpoints((sx, top), (nx, top))
        d += elm.Dot().at((nx, top))
        q2 = elm.NFet().theta(0).anchor("drain").at((nx, top - 1.0))
        d += elm.Line().endpoints((nx, top), (nx, top - 1.0))
        d += q2
        d += elm.Line().endpoints(q2.absanchors["source"], (nx, 0))
        g2 = q2.absanchors["gate"]
        d += elm.Label().at((g2[0] + 0.3, g2[1] + 1.0)).label("下管", loc="center")
        g1 = q.absanchors["gate"]
        d += elm.Line().endpoints(g1, (g1[0], g1[1] - 0.4))
        d += elm.Label().at((g1[0], g1[1] - 0.7)).label("驱动 A", loc="center")
        d += elm.Line().endpoints(g2, (g2[0] + 0.4, g2[1]))
        d += elm.Label().at((g2[0] + 0.9, g2[1] - 0.4)).label("驱动 B", loc="center")
        d += elm.Inductor2().endpoints((nx, top), (nx + 3.6, top)).label("$L$", "top")
        output_stage(d, nx + 3.6, top, False)
        d += elm.Line().endpoints((-1.2, 0), (nx + 3.6, 0))
        d += elm.Dot(open=True).at((-1.2, 0)).label("0 V", "left")
        d += elm.Dot().at((0, 0)); d += elm.Dot().at((nx, 0))
        d += elm.Label().at((nx + 1.5, -0.9)).label("两管轮流导通，中间留「死区」，绝不能同时导通", loc="center")
    schem.save_schem(d, P, "09_p2_4_sync.png")


def p2_5():
    """反激电源次级输出级（简化画法的补全）。"""
    with schem.drawing(fontsize=11) as d:
        t = elm.Transformer(t1=4, t2=4).anchor("p1")
        d += t.at((0, 4.0))
        # 初级侧（只画成方框说明）
        d += elm.Line().endpoints(t.p1, (t.p1[0] - 0.8, t.p1[1]))
        d += elm.Line().endpoints(t.p2, (t.p2[0] - 0.8, t.p2[1]))
        bx = t.p1[0] - 2.6
        y0, y1 = t.p2[1] - 0.3, t.p1[1] + 0.3
        for a, b in (((bx - 1.8, y0), (bx + 1.8, y0)), ((bx + 1.8, y0), (bx + 1.8, y1)),
                     ((bx + 1.8, y1), (bx - 1.8, y1)), ((bx - 1.8, y1), (bx - 1.8, y0))):
            d += elm.Line().endpoints(a, b)
        d += elm.Line().endpoints((bx + 1.8, t.p1[1]), (t.p1[0] - 0.8, t.p1[1]))
        d += elm.Line().endpoints((bx + 1.8, t.p2[1]), (t.p2[0] - 0.8, t.p2[1]))
        d += elm.Label().at((bx, (y0 + y1) / 2)).label("初级（接市电！）\n整流后约 311 V 直流\n+ MOSFET 开关", loc="center")
        # 次级：串联二极管 → 电容 ∥ 稳压管
        top, bot = t.s1[1], t.s2[1]
        x = t.s1[0]
        d += elm.Diode().endpoints((x, top), (x + 2.5, top)).label("整流二极管", "top")
        d += elm.Dot().at((x + 2.5, top))
        d += elm.Capacitor().endpoints((x + 2.5, top), (x + 2.5, bot)).label("$C_o$", "bottom")
        d += elm.Line().endpoints((x + 2.5, top), (x + 4.3, top))
        d += elm.Dot().at((x + 4.3, top))
        d += elm.Zener().endpoints((x + 4.3, bot), (x + 4.3, top)).label("稳压管\n（简化画法，\n实际多为反馈）", "bottom")
        d += elm.Line().endpoints((x + 4.3, top), (x + 5.3, top))
        d += elm.Dot(open=True).at((x + 5.3, top)).label("$V_o$", "right")
        d += elm.Line().endpoints((x, bot), (x + 5.3, bot))
        d += elm.Dot(open=True).at((x + 5.3, bot)).label("0 V", "right")
        d += elm.Dot().at((x + 2.5, bot)); d += elm.Dot().at((x + 4.3, bot))
        d += elm.Label().at(((t.p1[0] + t.s1[0]) / 2, top + 1.0)).label("变压器：隔离", loc="center")
        d += elm.Label().at((x + 1.5, bot - 0.8)).label("次级：脉冲 → 二极管整流 → 电容滤波（同 06）", loc="center")
    schem.save_schem(d, P, "09_p2_5_flyback.png")


p1_1(); p2_1(); p2_4(); p2_5()
print("[完成] 09_figs.py")

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


def bb09():
    """09 page4：现成降压模块（例如 LM2596 可调模块，焊上排针）跨在中间凹槽上；12 V 直流输入，负载功率电阻在板外。"""
    bb = Breadboard(ncol=30, rails=dict(tp=("+12 V 输入", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"), bn=("（不用）", "gnd")),
                    figsize=(10, 5.6))
    bb.wire(bb.ext((-2.0, 11.4), "12 V 直流电源 +", "pos"), "tp1", "pos")
    bb.wire(bb.ext((-2.0, 10.0), "12 V 直流电源 −", "gnd"), "tn2", "gnd")
    bb.wire("tn28", "bp28", "gnd")                      # 上下两条 0 V 轨连起来
    # 模块：输入端 IN+ / IN− 在左（第 4 列），输出端 OUT+ / OUT− 在右（第 20 列）
    bb.multi("M1", {"IN+": "e4", "IN−": "f4", "OUT+": "e20", "OUT−": "f20"}, "降压模块（例如 LM2596）  电位器调输出",
             w=17.0, h=1.3, fc="#6f8fb0", at=(12.0, 4.0))
    bb.wire("a4", "tp4", "pos")                         # IN+ → +12 V（测输入电流时把这根线换成电流表）
    bb.wire("j4", "bp4", "gnd")                         # IN− → 0 V
    bb.wire("j20", "bp20", "gnd")                       # OUT− → 0 V
    # a20 引出线：先横移半格走到第 20、21 列孔之间，再竖直向上，在两条上方电源轨线处画「跨线弯」，表示从轨上方跨过、不接轨
    bb.ax.set_ylim(-6.0, 13.5)                          # 留出板外接线端（y = 12.9）的位置，否则端点圆圈被裁掉
    bb.wire("a20", bb.ext((20.5, 12.9), "接负载 RL 一端", "sig", dx=0.45, ha="left"), "sig",
            via=[(20.5, 9.0)], hops=[BB_RAIL_Y["tn"] - 0.32, BB_RAIL_Y["tp"] + 0.32])
    bb.wire(bb.ext((16.0, -5.0), "RL 另一端", "gnd", dx=-0.45, ha="right"), "bp16", "gnd")
    assert bb.connected("M1.IN+", "tp1") and bb.connected("M1.IN−", "tn1") and bb.connected("M1.OUT−", "tn1")
    assert not bb.connected("M1.IN+", "M1.OUT+") and not bb.connected("tp1", "tn1")
    bb.probe("c4", "V_in", dx=0.35, dy=0.3)
    bb.probe("c20", "V_o", dx=0.35, dy=0.3)
    bb.note(19.0, -4.75, "测输入电流：断电，拔掉 a4 的橙线，", va="center")
    bb.note(19.0, -5.35, "电流表红笔接 +12 V 轨、黑笔接 b4", va="center")
    bb.legend(("pos", "gnd", "sig"))
    print(f"09 p4 面包板：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def p4_breadboards():
    bb = bb09()
    fs.save(bb.fig, P, "09_p4_1_bb_buck.png")
    plt.close(bb.fig)
    print("09_figs p4 OK")


p4_breadboards()


# ===== 第 8 轮补图（page1–3）=====
from schem import *
HL = C["bad"]


def _box(d, x0, y0, x1, y1, **kw):
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        e = elm.Line().endpoints(a, b)
        if "color" in kw: e = e.color(kw["color"])
        if "ls" in kw: e = e.linestyle(kw["ls"])
        d += e


def _half(d, ox, closed):
    """直觉版降压，ox 为横向偏移；closed=True 画开关闭合时的电流路径。"""
    top = 4.0
    cu = C["cur"]
    d += elm.Dot(open=True).at((ox, top)).label("$V_{in}$\n12 V", "left")
    if closed:
        d += elm.Line().endpoints((ox, top), (ox + 3.0, top)).color(cu)
        d += elm.Label().at((ox + 1.5, top + 0.45)).label("开关闭合", loc="center")
        d += elm.Schottky().endpoints((ox + 3.0, 0), (ox + 3.0, top)).label("二极管\n反偏，不通", "bottom")
    else:
        d += elm.Switch().endpoints((ox, top), (ox + 3.0, top)).label("开关断开", "top")
        d += elm.Schottky().endpoints((ox + 3.0, 0), (ox + 3.0, top)).color(cu).label("二极管导通\n节点 ≈ −0.4 V", "bottom")
    d += elm.Dot().at((ox + 3.0, top))
    d += elm.Inductor2().endpoints((ox + 3.0, top), (ox + 6.0, top)).color(cu).label(
        "左 12 V、右 5 V\n电流慢慢增大" if closed else "电感推着电流\n慢慢减小", "top")
    d += elm.Dot().at((ox + 6.0, top))
    d += elm.Capacitor().endpoints((ox + 6.0, top), (ox + 6.0, 0)).label("C", "bottom")
    d += elm.Line().endpoints((ox + 6.0, top), (ox + 8.0, top)).color(cu)
    d += elm.Resistor().endpoints((ox + 8.0, top), (ox + 8.0, 0)).color(cu).label("负载\n5 V", "bottom")
    d += elm.Line().endpoints((ox + 8.0, 0), (ox + 6.0, 0)).color(cu)
    d += elm.Dot().at((ox + 6.0, 0))
    g = elm.Line().endpoints((ox + 6.0, 0), (ox + 3.0, 0)).color(cu)
    d += g
    d += elm.Dot().at((ox + 3.0, 0))
    e = elm.Line().endpoints((ox + 3.0, 0), (ox, 0))
    if closed: e = e.color(cu)
    d += e
    d += elm.Dot(open=True).at((ox, 0)).label("0 V", "left")
    # 方向箭头
    if closed:
        d += elm.Arrow().at((ox + 0.6, top - 0.35)).to((ox + 2.4, top - 0.35)).color(cu)
    else:
        d += elm.Arrow().at((ox + 2.55, 0.8)).to((ox + 2.55, 3.2)).color(cu)
    d += elm.Arrow().at((ox + 6.4, top - 0.35)).to((ox + 7.6, top - 0.35)).color(cu)
    d += elm.Label().at((ox + 4.0, -1.0)).label("(a) 开关闭合：电源 → 电感 → 负载" if closed
                                               else "(b) 开关断开：地 → 二极管 → 电感 → 负载", loc="center")


def p1_4_paths():
    with drawing(fontsize=11) as d:
        _half(d, 0, True)
        _half(d, 11.0, False)
    save_schem(d, "09", "09_p1_4_paths.png")


def p2_6_phases():
    """伏秒平衡推导用的两个等效电路。"""
    top = 3.5
    with drawing(fontsize=11) as d:
        for ox, on in ((0, True), (11.5, False)):
            if on:
                d += elm.SourceV().endpoints((ox, 0), (ox, top))
                d += elm.Label().at((ox - 0.9, top / 2)).label("$V_{in}$", loc="center")
                d += elm.Line().endpoints((ox, top), (ox + 1.5, top)).label("上管导通", "top")
            else:
                d += elm.Line().endpoints((ox, 0), (ox, top))
                d += elm.Label().at((ox - 1.3, top / 2)).label("二极管导通\n（压降当 0）\n左端接地", loc="center")
                d += elm.Line().endpoints((ox, top), (ox + 1.5, top))
            d += elm.Dot().at((ox + 1.5, top)).label("$V_{in}$" if on else "0 V", "bottom")
            d += elm.Inductor2().endpoints((ox + 1.5, top), (ox + 4.5, top)).color(HL).label(
                "$L$：两端 $V_{in}-V_o$" if on else "$L$：两端 $-V_o$", "top")
            d += elm.Dot().at((ox + 4.5, top)).label("$V_o$", "bottom")
            d += elm.Capacitor().endpoints((ox + 4.5, top), (ox + 4.5, 0)).label("$C_o$", "bottom")
            d += elm.Line().endpoints((ox + 4.5, top), (ox + 6.3, top))
            d += elm.Resistor().endpoints((ox + 6.3, top), (ox + 6.3, 0)).label("负载", "bottom")
            d += elm.Line().endpoints((ox, 0), (ox + 6.3, 0))
            d += elm.Dot().at((ox + 4.5, 0))
            d += elm.Label().at((ox + 3.2, -1.4)).label(
                "(a) 导通 $DT$：电流上升" if on else "(b) 断开 $(1-D)T$：电流下降", loc="center")
    save_schem(d, "09", "09_p2_6_phases.png")


def p3_3_loops():
    """PCB 回路：回路 1、回路 2 与热点回路。"""
    top = 4.0
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((-1.2, top)).label("$V_{in}$", "left")
        d += elm.Line().endpoints((-1.2, top), (0.6, top))
        d += elm.Dot().at((0, top))
        d += elm.Capacitor().endpoints((0, top), (0, 0))
        d += elm.Label().at((-0.6, 2.0)).label("$C_{in}$", loc="center")
        q, sx = high_side(d, 0.6, top, "上管")
        nx = sx + 1.0
        d += elm.Line().endpoints((sx, top), (nx, top))
        d += elm.Dot().at((nx, top))
        d += elm.Label().at((nx + 0.2, top + 0.45)).label("开关节点", loc="center")
        d += elm.Schottky().endpoints((nx, 0), (nx, top))
        d += elm.Label().at((nx, -0.55)).label("续流二极管", loc="center")
        d += elm.Inductor2().endpoints((nx, top), (nx + 3.0, top)).label("$L$", "top")
        x2 = nx + 3.0
        d += elm.Dot().at((x2, top))
        d += elm.Capacitor().endpoints((x2, top), (x2, 0)).label("$C_o$", "bottom")
        d += elm.Line().endpoints((x2, top), (x2 + 2.0, top))
        d += elm.Resistor().endpoints((x2 + 2.0, top), (x2 + 2.0, 0)).label("负载", "bottom")
        d += elm.Line().endpoints((-1.2, 0), (x2 + 2.0, 0))
        d += elm.Dot(open=True).at((-1.2, 0)).label("0 V", "left")
        for x in (0, nx, x2): d += elm.Dot().at((x, 0))
        _box(d, 0.3, 0.3, x2 - 0.3, top - 0.3, color=C["fb"], ls="--")
        _box(d, nx + 0.3, 0.55, x2 - 0.55, top - 0.55, color=C["cur"], ls=":")
        _box(d, 0.5, 0.55, nx - 0.3, top - 0.55, color=HL, ls="-")
        d += elm.Label().at(((0.5 + nx - 0.3) / 2, 1.9)).label("热点回路", loc="center").color(HL)
        d += elm.Label().at(((nx + x2) / 2, 1.9)).label("回路 2\n（上管断开）", loc="center").color(C["cur"])
        d += elm.Label().at((x2 / 2, -1.2)).label("绿色虚线：回路 1（上管导通）", loc="center").color(C["fb"])
    save_schem(d, "09", "09_p3_3_loops.png")


def p3_4_lab():
    """效率与纹波实验的接法。"""
    with drawing(fontsize=11) as d:
        top = 4.0
        _box(d, -3.2, -0.3, -0.6, top + 0.3)
        d += elm.Label().at((-1.9, 2.0)).label("实验室\n直流电源\n12 V\n限流 1.5 A", loc="center")
        d += elm.Line().endpoints((-0.6, top), (0, top))
        d += elm.MeterA().endpoints((0, top), (2.0, top)).color(HL).label("$I_{in}$", "top")
        d += elm.Line().endpoints((2.0, top), (3.0, top))
        d += elm.Line().endpoints((-0.6, 0), (3.0, 0))
        _box(d, 3.0, -0.3, 6.0, top + 0.3)
        d += elm.Label().at((4.5, 2.0)).label("降压模块", loc="center")
        d += elm.Label().at((3.45, top - 0.35)).label("IN+", loc="center")
        d += elm.Label().at((3.45, 0.35)).label("IN−", loc="center")
        d += elm.Label().at((5.45, top - 0.35)).label("OUT+", loc="center")
        d += elm.Label().at((5.45, 0.35)).label("OUT−", loc="center")
        d += elm.Line().endpoints((6.0, top), (10.0, top))
        d += elm.Line().endpoints((6.0, 0), (10.0, 0))
        d += elm.Dot().at((7.0, top)); d += elm.Dot().at((7.0, 0))
        d += elm.Capacitor().endpoints((7.0, top), (7.0, 0))
        d += elm.Label().at((7.6, 1.2)).label("输出\n电容", loc="center")
        d += elm.Dot().at((8.5, top)); d += elm.Dot().at((8.5, 0))
        d += elm.MeterV().endpoints((8.5, top), (8.5, 0))
        d += elm.Label().at((9.2, 1.2)).label("测 $V_o$", loc="center")
        d += elm.Resistor().endpoints((10.0, top), (10.0, 0))
        d += elm.Label().at((10.9, 2.0)).label("负载\n5 Ω\n10 W", loc="center")
        # 示波器探头：接地弹簧顶在输出电容两端
        d += elm.Line().endpoints((7.0, top), (7.0, top + 1.0)).color(HL)
        d += elm.Line().endpoints((7.0, 0), (7.0, -0.7)).color(HL)
        d += elm.Label().at((7.0, -1.1)).label("探头地（接地弹簧）", loc="center").color(HL)
        d += elm.Label().at((7.0, top + 1.45)).label("示波器探头尖：顶在输出电容正端", loc="center").color(HL)
    save_schem(d, "09", "09_p3_4_lab.png")


def round8():
    p1_4_paths(); p2_6_phases(); p3_3_loops(); p3_4_lab()
    print("09_figs 第 8 轮补图 OK")


if __name__ == "__main__":
    round8()
