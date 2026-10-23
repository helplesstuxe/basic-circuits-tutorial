"""10 稳压管稳压：电路图（schemdraw）。运行：/workspace/circuits-venv/bin/python code/figs/10_figs.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem
from schem import elm

P = "10"


def p1_1():
    """并联稳压：限流电阻 R + 稳压管 + 负载，标出 I_R = I_Z + I_L。"""
    with schem.drawing(fontsize=11) as d:
        d += elm.SourceV().endpoints((0, 0), (0, 3)).label("$V_i$\n10–14 V\n（06 的输出）", loc="bottom")
        r = elm.Resistor().endpoints((0, 3), (3.5, 3)).label("R  180 Ω", loc="top")
        d += r
        d += elm.CurrentLabelInline(direction="in").at(r).label("$I_R$", loc="bottom")
        d += elm.Dot().at((3.5, 3))
        z = elm.Zener().endpoints((3.5, 0), (3.5, 3)).label("1N4733A\n$V_Z$ = 5.1 V", loc="bottom")
        d += z
        d += elm.Line().endpoints((3.5, 3), (6.5, 3))
        d += elm.Dot().at((6.5, 3))
        d += elm.Resistor().endpoints((6.5, 3), (6.5, 0)).label("$R_L$\n负载", loc="bottom")
        d += elm.Line().endpoints((6.5, 3), (8.5, 3))
        d += elm.Dot(open=True).at((8.5, 3)).label("$V_o$ ≈ 5 V", loc="right")
        d += elm.Line().endpoints((0, 0), (8.5, 0))
        d += elm.Dot().at((3.5, 0))
        d += elm.Dot().at((6.5, 0))
        d += elm.Dot(open=True).at((8.5, 0)).label("0 V", loc="right")
        d += elm.Label().at((2.6, 1.5)).label("↓$I_Z$", loc="center")
        d += elm.Label().at((5.7, 1.5)).label("↓$I_L$", loc="center")
        d += elm.Label().at((4.2, -0.9)).label("$I_R$ = $I_Z$ + $I_L$：负载少拿多少，稳压管就多吃多少")
    schem.save_schem(d, P, "10_p1_1_shunt.png")


def p2_2():
    """变体：稳压管给三极管基极定电压，发射极输出 V_Z − 0.7 V。"""
    with schem.drawing(fontsize=11) as d:
        d += elm.SourceV().endpoints((0, 0), (0, 4.5)).label("$V_i$\n10–14 V", loc="bottom")
        d += elm.Resistor().endpoints((2.5, 4.5), (2.5, 2)).label("R\n180 Ω", loc="bottom")
        d += elm.Dot().at((2.5, 2))
        d += elm.Zener().endpoints((2.5, 0), (2.5, 2)).label("$V_Z$\n5.1 V", loc="bottom")
        q = elm.BjtNpn().theta(0).anchor("base").at((5.5, 2))
        d += q
        d += elm.Line().endpoints((2.5, 2), q.base)
        d += elm.Label().at((4.0, 2.4)).label("$I_B$ = $I_L$/(β+1)", loc="center")
        cx = q.collector[0]
        d += elm.Line().endpoints((0, 4.5), (cx, 4.5))
        d += elm.Dot().at((2.5, 4.5))
        d += elm.Line().endpoints(q.collector, (cx, 4.5))
        ex = q.emitter[0]
        d += elm.Line().endpoints(q.emitter, (ex, 1.0))
        d += elm.Line().endpoints((ex, 1.0), (8, 1.0))
        d += elm.Dot().at((8, 1.0))
        d += elm.Resistor().endpoints((8, 1.0), (8, 0)).label("$R_L$", loc="bottom")
        d += elm.Line().endpoints((8, 1.0), (9.5, 1.0))
        d += elm.Dot(open=True).at((9.5, 1.0)).label("$V_o$ ≈ $V_Z$ − 0.7 V", loc="right")
        d += elm.Line().endpoints((0, 0), (9.5, 0))
        d += elm.Dot().at((2.5, 0))
        d += elm.Dot().at((8, 0))
        d += elm.Dot(open=True).at((9.5, 0)).label("0 V", loc="right")
        d += elm.Label().at((cx + 1.9, 3.4)).label("NPN 三极管\n（大电流走 C→E）", loc="center")
    schem.save_schem(d, P, "10_p2_2_follower_schem.png")


if __name__ == "__main__":
    p1_1()
    p2_2()
    print("10_figs OK")

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


def bb10():
    """10 page4：R 180 Ω + 1N4733A 并联稳压，输入 9 V 电池或 ≤12 V 可调直流电源；负载 RL 可换 1k / 510 / 255 Ω。"""
    bb = Breadboard(ncol=18, rails=dict(tp=("+V_in（9～12 V）", "pos"), tn=("0 V", "gnd"), bp=("（不用）", "gnd"), bn=("（不用）", "gnd")),
                    figsize=(8.6, 5.4))
    bb.wire(bb.ext((-2.0, 11.4), "9 V 电池 / 直流电源 +", "pos"), "tp1", "pos")
    bb.wire(bb.ext((-2.0, 10.0), "电源 −", "gnd"), "tn2", "gnd")
    bb.wire("a3", "tp3", "pos")                          # 第 3 列 = 输入
    bb.two("R", "c3", "c7", "R", "R 180 Ω 1 W", lpos=(0, 0.62))
    bb.two("DZ", "b10", "b7", "Z", "1N4733A 色环在左", lpos=(-0.3, 0.62))   # 阳极 b10，阴极 b7
    bb.wire("a10", "tn10", "gnd")                        # 稳压管阳极 → 0 V（测 I_Z 时换成电流表）
    bb.two("RL", "d7", "d13", "R", "RL 1k / 510 / 255 Ω", lpos=(0, -0.75))
    bb.wire("a13", "tn13", "gnd")                        # 负载 → 0 V（测 I_L 时换成电流表）
    assert bb.connected("R.2", "DZ.2") and bb.connected("DZ.2", "RL.1")
    assert bb.connected("DZ.1", "tn1") and bb.connected("RL.2", "tn1") and bb.connected("R.1", "tp1")
    assert not bb.connected("tp1", "tn1") and not bb.connected("R.1", "R.2")
    bb.probe("b3", "V_in", dx=-0.35, dy=0.3, ha="right")
    bb.probe("e7", "V_o", dx=0.35, dy=-0.3)
    bb.note(9.0, -4.75, "测 I_Z：断电，拔掉 a10 的黑线，电流表红笔插 c10、黑笔接 0 V 轨", va="center", ha="center")
    bb.note(9.0, -5.35, "测 I_L：同样拔掉 a13 的黑线，电流表红笔插 c13、黑笔接 0 V 轨", va="center", ha="center")
    bb.legend(("pos", "gnd"))
    print(f"10 p4 面包板：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def p4_breadboards():
    bb = bb10()
    fs.save(bb.fig, P, "10_p4_1_bb_zener.png")
    plt.close(bb.fig)
    print("10_figs p4 OK")


if __name__ == "__main__":
    p4_breadboards()
