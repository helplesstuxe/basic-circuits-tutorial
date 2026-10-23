"""06 桥式整流：电路图和运放全波整流的静态特性（桥式整流的时域仿真图由 code/06_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/06_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "06"
VON, A = 0.7, 1e5          # 二极管 0.7 V（同 P2）；运放开环增益 10 万（同 P3、05）
R = 10e3                   # 运放全波整流里的电阻 R


def diamond(d, x0=0.0, y0=0.0, s=2.2):
    """画二极管桥：上顶点 a、下顶点 b 接交流，右顶点是输出 +，左顶点是输出 −。返回四个顶点坐标。"""
    a, p, b, n = (x0, y0 + s), (x0 + s, y0), (x0, y0 - s), (x0 - s, y0)
    d += elm.Diode().at(a).to(p).label("$D_1$", "top")
    d += elm.Diode().at(b).to(p).label("$D_2$", "bottom")
    d += elm.Diode().at(n).to(a).label("$D_3$", "top")
    d += elm.Diode().at(n).to(b).label("$D_4$", "bottom")
    for q in (a, p, b, n):
        d += elm.Dot().at(q)
    return a, p, b, n


# ---------- 图 06-p1-1 二极管桥 ----------
with drawing() as d:
    a, p, b, n = diamond(d)
    d += elm.Label().at((a[0] + 0.35, a[1] + 0.3)).label("a", fontsize=11)
    d += elm.Label().at((b[0] + 0.35, b[1] - 0.3)).label("b", fontsize=11)
    d += elm.Line().at(a).left().length(4.2)
    d += (src := elm.SourceSin().down().toy(b[1]).label("交流输入\n（低压）", "left"))
    d += elm.Line().right().tox(b[0])
    d += elm.Line().at(p).right().length(2.0)
    d += (j := elm.Dot())
    d += elm.Resistor().down().length(3.4).label("$R_L$", "bottom")
    d += elm.Line().left().tox(n[0])
    # 这根竖线要穿过交流源到 b 的水平线（y = b[1]），两线不相连：画一个跨线小弧
    d += elm.Line().up().toy(b[1] - 0.3)
    d += elm.Arc2(k=0.9).to((n[0], b[1] + 0.3))
    d += elm.Line().up().toy(n[1])
    d += elm.Line().at(j.center).right().length(1.0)
    d += elm.Dot(open=True).label("$V_o$ +", "right")
    d += elm.Label().at((n[0] - 0.5, n[1])).label("−", fontsize=13)
    d += elm.Label().at((p[0] + 0.4, p[1] + 0.35)).label("+", fontsize=13)
save_schem(d, N, "06_p1_1_bridge.png")

# ---------- 图 06-p2-1 完整的整流滤波电源（变压器初级接市电） ----------
with drawing() as d:
    d += (tr := elm.Transformer(t1=4, t2=4).label("变压器\n220 V → 12 V", "top", ofst=0.6))
    d += elm.Fuse().left().at(tr.p1).length(3.0).label("保险丝", "top")
    d += elm.Dot(open=True).label("L", "left")
    d += elm.Line().at(tr.p2).left().length(3.0)
    d += elm.Dot(open=True).label("N", "left")
    d += elm.Label().at((tr.p1[0] - 2.2, (tr.p1[1] + tr.p2[1]) / 2)).label("市电\n220 V 50 Hz", fontsize=11, color=C["bad"])
    a, p, b, n = diamond(d, x0=tr.s1[0] + 3.6, y0=(tr.s1[1] + tr.s2[1]) / 2, s=1.8)
    d += elm.Line().at(tr.s1).right().length(0.8)
    d += elm.Line().up().toy(a[1] + 0.6)
    d += elm.Line().right().tox(a[0])
    d += elm.Line().down().toy(a[1])
    d += elm.Line().at(tr.s2).right().length(0.8)
    d += elm.Line().down().toy(b[1] - 0.6)
    d += elm.Line().right().tox(b[0])
    d += elm.Line().up().toy(b[1])
    d += elm.Line().at(p).right().length(1.5)
    d += (j1 := elm.Dot())
    d += elm.Line().right().length(2.2)
    d += (j2 := elm.Dot())
    d += elm.Line().right().length(1.0)
    d += elm.Dot(open=True).label("$V_o$ +", "right")
    d += elm.Capacitor(polar=True).down().at(j1.center).length(3.2).label("C\n2200 µF\n25 V", "bottom")
    d += elm.Line().left().tox(n[0])
    d += elm.Line().up().toy(n[1])
    d += elm.Resistor().down().at(j2.center).length(3.2).label("$R_L$\n75 Ω", "bottom")
    d += elm.Line().left().tox(j1.center.x)
    d += elm.Label().at((n[0] - 0.45, n[1])).label("−", fontsize=13)
save_schem(d, N, "06_p2_1_supply.png")

# ---------- 图 06-p2-3 运放全波整流（精密半波整流 + 加权加法器） ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True).label("A1", "center", fontsize=10))
    d += elm.Line().left().at(op.in1).length(0.6)
    d += (j := elm.Dot())
    d += elm.Resistor().left().label("R")
    d += (vin := elm.Dot(open=True).label("$V_i$", "left"))
    d += elm.Line().left().at(op.in2).length(0.6)
    d += elm.Line().down().length(0.4)
    d += elm.Ground()
    d += elm.Line().up().at(j.center).length(1.4)
    d += (k := elm.Dot())
    d += elm.Diode().right().tox(op.out.x).reverse().label("$D_2$", "top")
    d += elm.Line().down().toy(op.out)
    d += elm.Diode().right().at(op.out).length(2.2).reverse().label("$D_1$", "bottom")
    d += (o := elm.Dot().label("$V_h$", "bottom", ofst=0.15))
    d += elm.Line().up().at(k.center).length(1.4)
    d += elm.Resistor().right().tox(o.center.x).label("R")
    d += elm.Line().down().toy(o.center)
    # 第二级：加权加法器
    d += elm.Resistor().right().at(o.center).label("R/2", "top")
    d += (s := elm.Dot())
    d += elm.Line().right().length(1.4)
    d += (op2 := elm.Opamp(leads=True, anchor="in1").label("A2", "center", fontsize=10))
    d += elm.Line().left().at(op2.in2).length(0.3)
    d += elm.Line().down().length(0.3)
    d += elm.Ground()
    d += elm.Line().up().at(s.center).length(2.8)
    d += elm.Resistor().right().tox(op2.out.x + 0.3).label("R")
    d += elm.Line().down().toy(op2.out)
    d += elm.Line().left().tox(op2.out.x)
    d += elm.Line().right().at(op2.out).length(1.2)
    d += elm.Dot(open=True).label("$V_o$", "right")
    # 原始输入 V_i 直接送一路到加法器
    d += elm.Line().down().at(vin.center).length(3.2)
    d += elm.Line().right().tox(s.center.x - 2.0)
    d += elm.Resistor().right().tox(s.center.x).label("R", "bottom")
    d += elm.Line().up().toy(s.center)
save_schem(d, N, "06_p2_3_opamp_fullwave.png")


# ---------- 图 06-p2-4 运放全波整流 vs 二极管桥：小信号 ----------
def halfwave(vi):
    """第一级（二极管调头的反相精密半波整流，静态模型）：返回 (V_h, A1 输出脚电压)。
    V_i > 0：D1 导通，反相放大，V_h = −V_i / (1 + 2/A)；V_i < 0：D2 导通，A1 输出脚被钳在 +0.7 V，V_h = 0。"""
    vi = np.asarray(vi, dtype=float)
    vh = np.where(vi > 0, -vi / (1 + 2 / A), 0.0)
    pin = np.where(vi > 0, vh - VON, VON)
    return vh, pin


def fullwave(vi):
    """第二级加权加法器（有限增益 A）：V_o = −(V_i + 2·V_h) / (1 + 噪声增益/A)，噪声增益 = 1 + R/(R ∥ R/2) = 4。"""
    vh, _ = halfwave(vi)
    return -(vi + 2 * vh) / (1 + 4 / A)


def bridge_static(vi):
    """普通二极管桥（静态，不计内阻）：|V_i| 超过两个二极管压降才有输出。"""
    return np.clip(np.abs(vi) - 2 * VON, 0, None)


t = np.linspace(0, 2e-3, 1000)
vi = 0.5 * np.sin(2 * np.pi * 1e3 * t)
vh, _ = halfwave(vi)
vo = fullwave(vi)
vb = bridge_static(vi)
err = np.abs(vo - np.abs(vi)).max()
avg = vo.mean()
print(f"[数值] 峰值 0.5 V：运放全波整流输出最大 {vo.max()*1e3:.1f} mV，与 |V_i| 的最大误差 {err*1e6:.0f} µV；平均值 {avg*1e3:.1f} mV（理论 2/π × 0.5 V = {2/np.pi*0.5*1e3:.1f} mV）")
print(f"[数值] 普通二极管桥输出最大 {vb.max():.1f} V")
assert vb.max() == 0 and err < 50e-6 and abs(avg - 2 / np.pi * 0.5) < 2e-3
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a1.plot(t * 1e3, vi, **fs.LS["vin"], label="输入 $V_i$")
a1.plot(t * 1e3, vh, **fs.LS["third"], label="第一级 $V_h$")
a1.plot(t * 1e3, vo, **fs.LS["vout"], label="输出 $V_o$")
a1.plot(t * 1e3, vb, **fs.LS["bad"], label="二极管桥：0")
fs.ref_h(a1, 0)
fs.axlabels(a1, "时间", "ms", "电压", "V")
a1.set_ylim(-0.7, 1.0)
a1.legend(loc="upper right", fontsize=7.5, ncol=2)
v = np.linspace(-2.5, 2.5, 1001)
a2.plot(v, np.abs(v), **fs.LS["good"], label="理想 $|V_i|$")
a2.plot(v, fullwave(v), **fs.LS["vout"], label="运放全波整流")
a2.plot(v, bridge_static(v), **fs.LS["bad"], label="二极管桥")
fs.ref_v(a2, 1.4, "1.4 V", y=0.85)
fs.ref_v(a2, -1.4, "−1.4 V", y=0.85)
print("[数值] 二极管桥死区 ±1.4 V")
fs.axlabels(a2, "输入 $V_i$", "V", "输出", "V")
a2.legend(loc="upper center", fontsize=8)
a2.set_ylim(-0.2, 3.2)
fs.save(fig, N, "06_p2_4_opamp_fullwave_sim.png")

# 第一级输出脚电压（正文用）
for x in (0.3, -0.3):
    h, pin = (float(q) for q in halfwave(x))
    print(f"[数值] V_i = {x:+.1f} V：V_h = {h:+.3f} V，A1 输出脚 {pin:+.2f} V，V_o = {float(fullwave(x)):+.4f} V")

print("06_figs OK")

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


def bb06():
    """06 page4：低压交流（9 V 交流适配器或信号发生器）→ 四只二极管搭的桥 → 电容 + 负载。
    桥的两个交流输入端都放在第 12 列（上半区 = ~1，下半区 = ~2），这一列电源轨没有孔，导线可以从板外直接竖着进来。
    上半区：D3（c8→c12）、D1（d12→d16）；下半区：D4（g8→g12）、D2（h12→h16）；第 8 列是桥的 − 端，第 16 列是桥的 + 端。"""
    bb = Breadboard(ncol=30, rails=dict(tp=("直流 +", "pos"), tn=("直流 −", "gnd"), bp=("（不用）", "gnd"), bn=("（不用）", "gnd")))
    ac1 = bb.ext((12, 12.15), "交流输入 ~1（适配器一根线 / 发生器红夹）", "sig", dx=0.45, ha="left")
    ac2 = bb.ext((12, -5.0), "交流输入 ~2（适配器另一根线 / 发生器黑夹）", "sig", dx=0.45, ha="left")
    bb.wire(ac1, "a12", "sig")
    bb.wire(ac2, "j12", "sig")
    bb.two("D3", "c8", "c12", "D", "D3", lpos=(0, 0.62))
    bb.two("D1", "d12", "d16", "D", "D1", lpos=(0, -0.62))
    bb.two("D4", "g8", "g12", "D", "D4", lpos=(0, 0.62))
    bb.two("D2", "h12", "h16", "D", "D2", lpos=(0, -0.62))
    bb.wire("e8", "f8", "gnd")          # 上下两个 − 端连起来
    bb.wire("e16", "f16", "pos")        # 上下两个 + 端连起来
    bb.wire("a16", "tp16", "pos")       # 桥 + 端 → 上方「直流 +」轨
    bb.wire("a8", "tn8", "gnd")         # 桥 − 端 → 上方「直流 −」轨
    bb.wire("a22", "tp22", "pos")
    bb.wire("a26", "tn26", "gnd")
    bb.two("C1", "b22", "b26", "CE", "C1（+ 在左）", lpos=(0, 0.75))
    bb.two("RL", "d22", "d26", "R", "RL", lpos=(0, -0.62))
    # 连接检查
    assert bb.connected("D1.1", "D3.2", ac1) and bb.connected("D2.1", "D4.2", ac2)
    assert bb.connected("D1.2", "D2.2", "tp1", "C1.1", "RL.1")
    assert bb.connected("D3.1", "D4.1", "tn1", "C1.2", "RL.2")
    assert not bb.connected(ac1, ac2) and not bb.connected("tp1", "tn1")
    assert not bb.connected(ac1, "tp1") and not bb.connected(ac2, "tn1")
    bb.probe("b12", "~1", dx=0.3, dy=0.3)
    bb.probe("i12", "~2", dx=0.3, dy=0.3)
    bb.probe("e22", "V+", dx=0.3, dy=-0.85)
    bb.probe("e26", "V−", dx=0.3, dy=-0.85)
    bb.note(18.0, 1.9, "第 8 列 = 桥的 − 端", color="0.3", va="center")
    bb.note(18.0, 0.9, "第 16 列 = 桥的 + 端", color="0.3", va="center")
    bb.legend(("pos", "gnd", "sig"))
    print(f"06 p4 面包板：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


bb = bb06()
fs.save(bb.fig, N, "06_p4_1_bb_bridge.png")
print("06_figs p4 OK")
