"""05 精密整流：电路图和静态特性图（时域仿真图由 code/05_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/05_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "05"
VON, RD, RL, A = 0.7, 10.0, 10e3, 1e5     # 折线二极管 0.7 V / 10 Ω；负载 10 kΩ；运放开环增益 10 万（同 P3）
RAIL = 13.5                                # ±15 V 供电时输出最多摆到约 ±13.5 V
K = RL / (RL + RD)                         # 二极管导通电阻和负载的分压


def passive(vi):
    """普通二极管半波整流：输入超过 0.7 V 才有输出。"""
    return np.where(vi > VON, (vi - VON) * K, 0.0)


def precision(vi):
    """基本型精密整流（静态）：返回 (V_o, 运放输出脚电压)。
    二极管导通时 V_oa = A(V_i − V_o)、V_o = K(V_oa − 0.7)，联立得 V_o = K(A·V_i − 0.7)/(1 + K·A)。"""
    vi = np.asarray(vi, dtype=float)
    vo = K * (A * vi - VON) / (1 + K * A)
    on = vo > 0
    vo = np.where(on, vo, 0.0)
    voa = np.where(on, vo / K + VON, np.clip(A * vi, -RAIL, RAIL))
    return vo, voa


# ---------- 图 05-p1-1 普通二极管半波整流 ----------
with drawing() as d:
    d += (src := elm.SourceSin().up().label("$V_i$\n峰值 0.2 V", "left"))
    d += elm.Line().right().length(0.8)
    d += elm.Diode().right().label("硅二极管")
    d += elm.Line().right().length(0.8)
    d += (j := elm.Dot())
    d += elm.Resistor().down().toy(src.start).label("$R_L$ 10 kΩ", "bottom")
    d += elm.Line().left().tox(src.start)
    d += elm.Ground().at(src.start)
    d += elm.Line().right().at(j.center).length(1.0)
    d += elm.Dot(open=True).label("$V_o$ ≈ 0 V", "right")
save_schem(d, N, "05_p1_1_passive.png")

# ---------- 图 05-p1-2 基本型精密整流（超级二极管） ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in2).length(0.8)
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Diode().right().at(op.out).length(2.5).label("二极管", "top")
    d += (j := elm.Dot())
    d += elm.Line().right().length(1.0)
    d += elm.Dot(open=True).label("$V_o$", "right")
    d += elm.Resistor().down().at(j.center).length(2.2).label("$R_L$ 10 kΩ", "bottom")
    d += elm.Ground()
    d += elm.Line().up().at(j.center).length(1.6).color(C["fb"])
    d += elm.Line().left().tox(op.in1.x - 0.8).color(C["fb"]).label("反馈线：从二极管后面取", "top")
    d += elm.Line().down().toy(op.in1).color(C["fb"])
    d += elm.Line().right().tox(op.in1).color(C["fb"])
    d += elm.Dot().at(op.out).label("运放输出脚", "bottom", ofst=0.2)
save_schem(d, N, "05_p1_2_superdiode.png")

# ---------- 图 05-p1-3 小信号整流：普通二极管 vs 精密整流 ----------
t = np.linspace(0, 2e-3, 1000)
vi = 0.2 * np.sin(2 * np.pi * 1e3 * t)
vp = passive(vi)
vo, _ = precision(vi)
print(f"[数值] 峰值 0.2 V：普通二极管输出最大 {vp.max()*1e3:.1f} mV，精密整流输出最大 {vo.max()*1e3:.1f} mV")
assert vp.max() == 0 and abs(vo.max() - 0.2) < 1e-3
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi * 1e3, **fs.LS["vin"], label="输入 $V_i$（峰值 0.2 V）")
ax.plot(t * 1e3, vp * 1e3, **fs.LS["bad"], label="普通二极管整流：一直是 0")
ax.plot(t * 1e3, vo * 1e3, **fs.LS["vout"], label="精密整流 $V_o$：正半周原样通过")
fs.ref_h(ax, 0)
fs.mark(ax, 0.25, vo.max() * 1e3, fmt="{:.0f}", unit=" mV", dx=6, dy=2)
fs.axlabels(ax, "时间", "ms", "电压", "mV")
ax.set_ylim(-260, 330)
ax.legend(loc="upper right", fontsize=8, ncol=1)
fs.save(fig, N, "05_p1_3_compare.png")

# ---------- 图 05-p2-1 传输特性：V_o 和运放输出脚随 V_i 变化 ----------
v = np.linspace(-1, 1, 801)
vo, voa = precision(v)
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a1.plot(v, v.clip(0), **fs.LS["good"], label="理想整流")
a1.plot(v, passive(v), **fs.LS["bad"], label="普通二极管")
a1.plot(v, vo, **fs.LS["vout"], label="精密整流 $V_o$")
fs.ref_v(a1, 0.7, "0.7 V", y=0.35)
fs.axlabels(a1, "输入 $V_i$", "V", "输出 $V_o$", "V")
a1.legend(loc="upper left", fontsize=8)
vo01, voa01 = (float(x) for x in precision(0.1))
err_uV = (0.1 - vo01) * 1e6
print(f"[数值] V_i = 0.1 V：精密整流 V_o = {vo01*1e3:.4f} mV，误差 {err_uV:.1f} µV（= 运放输出脚电压 ÷ A = {voa01/A*1e6:.1f} µV，只算开环增益；真实 741 的失调约 1 mV，SPICE 误差约 1.0 mV）")
print(f"[数值] V_i = 0.1 V：运放输出脚 {voa01:.3f} V；普通二极管输出 {float(passive(0.1)):.1f} V")
assert abs(err_uV - voa01 / A * 1e6) < 0.1 and err_uV < 10, "只算开环增益时，误差 = 运放输出脚电压 ÷ 开环增益，只有几微伏"
a2.plot(v, voa, **fs.LS["third"], label="运放输出脚电压")
a2.plot(v, vo, **fs.LS["vout"], label="电路输出 $V_o$")
fs.ref_h(a2, -RAIL, f"负饱和 −{RAIL} V", x=0.98)
fs.mark(a2, 0.1, voa01, fmt="{:.2f}", unit=" V", dx=6, dy=-12)
fs.axlabels(a2, "输入 $V_i$", "V", "电压", "V")
a2.set_ylim(-15, 3)
a2.legend(loc="center right", fontsize=8)
fs.save(fig, N, "05_p2_1_transfer.png")

# ---------- 图 05-p2-3 改进型（反相型）精密半波整流 ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.6)
    d += (j := elm.Dot().label("$V_-$（虚地）", "bottom", ofst=0.15))
    d += elm.Resistor().left().label("$R_1$ 10 kΩ")
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Line().left().at(op.in2).length(0.6)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    # D2：从虚地指向运放输出脚（输入为正时导通，钳住运放输出）
    d += elm.Line().up().at(j.center).length(1.4)
    d += (k := elm.Dot())
    d += elm.Diode().right().tox(op.out.x).label("$D_2$", "top")
    d += elm.Line().down().toy(op.out)
    # D1：从运放输出脚指向输出端（输入为负时导通）
    d += elm.Diode().right().at(op.out).length(2.2).label("$D_1$", "bottom")
    d += (o := elm.Dot())
    d += elm.Line().right().length(0.8)
    d += elm.Dot(open=True).label("$V_o$", "right")
    # R_f：从输出端回到虚地
    d += elm.Line().up().at(k.center).length(1.4)
    d += elm.Resistor().right().tox(o.center.x).label("$R_f$ 10 kΩ")
    d += elm.Line().down().toy(o.center)
    d += elm.Resistor().down().at(o.center).length(2.0).label("$R_L$ 10 kΩ", "bottom")
    d += elm.Ground()
save_schem(d, N, "05_p2_3_improved.png")

print("05_figs OK")

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


def bb05(improved):
    """05 page4：±9 V（两节 9 V 电池串联）、LM741、1N4148。improved=False 画基本型，True 画改进型。
    两种接法共用一套骨架：分压点在第 9 列下半区，虚地（2 脚）用跳线引到第 8 列上半区，输出端在第 11 列上半区。"""
    bb = Breadboard(ncol=30, rails=dict(tp=("+9 V", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"), bn=("−9 V", "neg")))
    bb.wire(bb.ext((-2.0, 11.4), "电池① 正极 +9 V", "pos"), "tp1", "pos")
    bb.wire(bb.ext((-2.0, 10.0), "两节电池相接处 0 V", "gnd"), "tn2", "gnd")
    bb.wire(bb.ext((-2.0, -3.4), "电池② 负极 −9 V", "neg"), "bn1", "neg")
    bb.wire("tn29", "bp29", "gnd")                       # 上下两条 0 V 轨连起来
    bb.dip8("U1", 12, "LM741")
    bb.wire("a13", "tp13", "pos")                        # 7 脚 → +9 V
    bb.wire("j15", "bn15", "neg")                        # 4 脚 → −9 V
    # 输入分压：RA 8.2 kΩ 一端接电源轨，RB 100 Ω 到地，分压点在第 9 列下半区
    bb.two("RA", "g5", "g9", "R", "RA 8.2k")
    bb.wire("h5", "bn5" if improved else "tp5", "neg" if improved else "pos")
    bb.two("RB", "j9", "bp9", "R", "RB 100")
    # 2 脚（第 13 列下半区）用跳线引到第 8 列上半区
    bb.wire("g13", "e8", "sig")
    # D1：6 脚（第 14 列上半区）→ 输出端（第 11 列上半区）；RL 10 kΩ 从输出端接到上方 0 V 轨
    bb.two("D1", "c14", "c11", "D", "D1 1N4148", lpos=(1.8, -0.05))
    bb.two("RL", "a11", "tn11", "R", "RL 10k", lpos=(0.45, 0.1))
    if not improved:
        bb.wire("i9", "i14", "sig")                      # 分压点 → 3 脚（同相输入）
        bb.wire("b8", "b11", "sig")                      # 反馈：输出端 → 2 脚，接在二极管后面
    else:
        bb.wire("g14", "bp14", "gnd")                    # 3 脚接地
        bb.two("R1", "h9", "h13", "R", "R1 10k")         # 分压点 → R1 → 2 脚（虚地）
        bb.two("D2", "d8", "d14", "D", "D2 1N4148", lpos=(3.3, -0.05))      # D2：阳极接虚地，阴极接 6 脚
        bb.two("Rf", "b8", "b11", "R", "Rf 20k")         # Rf：输出端 → 虚地
    # 连接检查：电源、分压、二极管方向、反馈都接对，且没有把不该通的点连在一起
    assert bb.connected("U1.7", "tp30") and bb.connected("U1.4", "bn30")
    assert bb.connected("tn1", "bp1") and not bb.connected("tp1", "tn1") and not bb.connected("bn1", "bp1")
    assert bb.connected("RA.2", "RB.1") and bb.connected("RB.2", "bp1")
    assert bb.connected("RA.1", "bn1" if improved else "tp1")
    assert bb.connected("U1.6", "D1.1") and bb.connected("D1.2", "RL.1") and bb.connected("RL.2", "bp1")
    if not improved:
        assert bb.connected("U1.3", "RB.1") and bb.connected("U1.2", "D1.2")
    else:
        assert bb.connected("U1.3", "bp1") and bb.connected("R1.1", "RB.1") and bb.connected("R1.2", "U1.2")
        assert bb.connected("D2.1", "U1.2") and bb.connected("D2.2", "U1.6")
        assert bb.connected("Rf.1", "U1.2") and bb.connected("Rf.2", "D1.2")
        assert not bb.connected("U1.2", "U1.6") and not bb.connected("U1.2", "D1.2")
    bb.probe("f9", "Vi", dx=-0.35, dy=0.3, ha="right")
    bb.probe("e11", "Vo", dx=-0.3, dy=0.3, ha="right")
    bb.probe("b14", "6 脚", dx=0.35, dy=0.3)
    bb.legend()
    print(f"05 p4 面包板（{'改进型' if improved else '基本型'}）：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


bb = bb05(False)
fs.save(bb.fig, N, "05_p4_1_bb_basic.png")
bb = bb05(True)
fs.save(bb.fig, N, "05_p4_2_bb_improved.png")
print("05_figs p4 OK")

# ======================================================================
# 第 8 轮补图：page1–page3 正文讲到的电路连接（不动上面的图号）
# ======================================================================
HL = C["bad"]          # 强调色：接错的那根线、新加的元件


def _superdiode(d, x0=0.0, fb_before=False, diode_rev=False, title=None, rl="$R_L$ 10 kΩ", show_voa=False):
    """在 (x0, 0) 画基本型精密整流；fb_before=True 时反馈线从运放输出脚取（错误接法），
    diode_rev=True 时二极管调头。返回 (op, 输出点)。"""
    d += (op := elm.Opamp(leads=True).right().at((x0, 0)).anchor("center"))
    d += elm.Line().left().at(op.in2).length(0.8)
    d += elm.Dot(open=True).label("$V_+ = V_i$" if show_voa else "$V_i$", "left")
    d += (pa := elm.Dot().at(op.out))
    dio = elm.Diode().right().at(op.out).length(2.5)
    if diode_rev:
        dio = dio.reverse().color(HL).label("二极管调头", "top")
    else:
        dio = dio.label("$V_D$ ≈ 0.7 V" if show_voa else "二极管", "top")
    d += dio
    d += (j := elm.Dot())
    d += elm.Line().right().length(1.0)
    d += elm.Dot(open=True).label("$V_o$", "right")
    d += (rr := elm.Resistor().down().at(j.center).length(2.2).label(rl, "bottom"))
    d += elm.Ground()
    src = pa.center if fb_before else j.center
    col = HL if fb_before else C["fb"]
    d += elm.Line().up().at(src).length(1.6).color(col)
    d += elm.Line().left().tox(op.in1.x - 0.8).color(col).label("反馈线：$V_- = V_o$" if show_voa else "", "top", color=col)
    d += elm.Line().down().toy(op.in1).color(col)
    d += elm.Line().right().tox(op.in1).color(col)
    if show_voa:
        d += elm.Label().at((op.out.x + 1.1, op.out.y - 0.6)).label("$V_{oa}$（运放输出脚）", fontsize=11)
        d += elm.Arrow().down().at((j.center.x - 0.6, j.center.y - 1.0)).length(1.0).color(C["cur"])
        d += elm.Label().at((j.center.x - 0.75, j.center.y - 1.5)).label("$I$", fontsize=12, color=C["cur"], halign="right")
    if title:
        d += elm.Label().at((x0 + 1.6, -3.9)).label(title, fontsize=12)
    return op, j, rr


# ---------- 图 05-p1-4 两个常见接错：反馈取错位置、二极管接反 ----------
with drawing() as d:
    _superdiode(d, 0, fb_before=True, title="(a) 反馈线从运放输出脚取（二极管前面）")
    d += elm.Label().at((1.0, 2.55)).label("反馈接在这里：二极管在环外", fontsize=11, color=HL)
    _superdiode(d, 10.5, diode_rev=True, title="(b) 反馈位置对，但二极管调头")
    d += elm.Label().at((11.6, 2.55)).label("反馈线：从二极管后面取", fontsize=11, color=C["fb"])
save_schem(d, N, "05_p1_4_mistakes.png")

# ---------- 图 05-p2-5 基本型的记号：V+、V−、V_oa、V_D、电流方向 ----------
with drawing() as d:
    _superdiode(d, 0, show_voa=True)
save_schem(d, N, "05_p2_5_basic_labels.png")


def _improved(d, x0=0.0, r1="$R_1$ 10 kΩ", rf="$R_f$ 10 kΩ", rev=False, rs=None, vin="$V_i$", vout="$V_o$", rl="$R_L$ 10 kΩ"):
    """在 (x0, 0) 画改进型（反相型）精密半波整流（同图 05-p2-3）。rev=True：D1、D2 同时调头；
    rs 给出时在输入前串一个信号源内阻（强调色）。返回 (op, 输入端点, 输出点)。"""
    d += (op := elm.Opamp(leads=True).right().at((x0, 0)).anchor("center"))
    d += elm.Line().left().at(op.in1).length(0.6)
    d += (j := elm.Dot().label("$V_-$（虚地）", "bottom", ofst=0.15))
    d += elm.Resistor().left().label(r1)
    if rs:
        d += (pin := elm.Dot())
        d += elm.Resistor().left().label(rs, color=HL).color(HL)
    else:
        pin = None
    d += (vi := elm.Dot(open=True).label(vin, "left"))
    d += elm.Line().left().at(op.in2).length(0.6)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().up().at(j.center).length(1.4)
    d += (k := elm.Dot())
    e2 = elm.Diode().right().tox(op.out.x).label("$D_2$", "top")
    d += (e2.reverse() if rev else e2)
    d += elm.Line().down().toy(op.out)
    e1 = elm.Diode().right().at(op.out).length(2.2).label("$D_1$", "bottom")
    d += (e1.reverse() if rev else e1)
    d += (o := elm.Dot())
    if vout:
        d += elm.Line().right().length(0.8)
        d += elm.Dot(open=True).label(vout, "right")
    d += elm.Line().up().at(k.center).length(1.4)
    d += elm.Resistor().right().tox(o.center.x).label(rf)
    d += elm.Line().down().toy(o.center)
    if rl:
        d += elm.Resistor().down().at(o.center).length(2.0).label(rl, "bottom")
        d += elm.Ground()
    return op, vi, o


# ---------- 图 05-p2-6 例 3：两只二极管调头的半波 + 加权反相加法器 = 全波 ----------
with drawing() as d:
    op1, vi, o1 = _improved(d, 0, r1="R", rf="R", rev=True, vout="", rl=None)
    d += elm.Label().at((o1.center.x + 0.35, o1.center.y - 0.45)).label("$V_h$", fontsize=12)
    # 加法器：V_h 经 R/2、V_i 经 R 进入第二个运放的反相端，反馈电阻 R
    d += (op2 := elm.Opamp(leads=True).right().at((o1.center.x + 4.5, o1.center.y)).anchor("in1"))
    d += elm.Line().left().at(op2.in1).length(0.6)
    d += (s := elm.Dot())
    d += elm.Resistor().left().tox(o1.center).label("R/2", "bottom")
    # V_i 支路：从输入端往上，越过第一级，接到加法点
    d += elm.Line().up().at(vi.center).length(5.0).color(C["vin"])
    d += elm.Resistor().right().tox(s.center.x).label("R（$V_i$ 直接送过来）", "top").color(C["vin"])
    d += elm.Line().down().toy(s.center).color(C["vin"])
    d += elm.Line().up().at(s.center).length(1.6)
    d += elm.Line().right().length(0.2)
    d += elm.Resistor().right().tox(op2.out.x + 0.5).label("R", "top")
    d += elm.Line().down().toy(op2.out)
    d += elm.Line().left().tox(op2.out)
    d += elm.Line().left().at(op2.in2).length(0.4)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().right().at((op2.out.x + 0.5, op2.out.y)).length(0.8)
    d += elm.Dot(open=True).label("$V_o = |V_i|$", "right")
    d += elm.Label().at((0.8, -3.0)).label("第一级：D1、D2 同时调头的改进型", fontsize=11)
    d += elm.Label().at((op2.center.x, -3.0)).label("第二级：加权反相加法器", fontsize=11)
save_schem(d, N, "05_p2_6_fullwave_ex3.png")

# ---------- 图 05-p3-3 排查表和练习里的两种情形 ----------
with drawing() as d:
    _superdiode(d, 0, fb_before=True, title="(a) 排查表第 1 行、练习 4：反馈线接在二极管前面")
    d += elm.Label().at((1.0, 2.55)).label("错：反馈从运放输出脚取", fontsize=11, color=HL)
    _improved(d, 13.0, r1="$R_1$", rf="$R_f$", rs="$R_s$ 1 kΩ")
    d += elm.Label().at((11.2, -3.9)).label("(b) 排查表第 5 行、练习 3：信号源内阻 $R_s$ 和 $R_1$ 串联", fontsize=12)
    d += elm.Label().at((6.7, -0.9)).label("信号源", fontsize=10, color=HL)
save_schem(d, N, "05_p3_3_cases.png")

# ---------- 图 05-p3-4 练习 5：精密整流 + RC 低通求平均 = 交流电压表 ----------
with drawing() as d:
    op, vi, o = _improved(d, 0, r1="$R_1$", rf="$R_f$", vout="", rl=None)
    d += elm.Line().right().at(o.center).length(0.6)
    d += elm.Resistor().right().label("$R$（滤波）", "top").color(C["fb"])
    d += (a := elm.Dot())
    d += elm.Capacitor().down().length(2.0).label("$C$", "bottom").color(C["fb"])
    d += elm.Ground()
    d += elm.Line().right().at(a.center).length(1.2)
    d += elm.Dot(open=True).label("平均值 → 万用表", "right")
    d += elm.Label().at((o.center.x + 0.1, o.center.y - 0.5)).label("整流输出", fontsize=10)
save_schem(d, N, "05_p3_4_average.png")
print("05_figs 第 8 轮补图 OK")
