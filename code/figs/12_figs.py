"""12 积分电路：全部配图（图 12-p2-3 由 code/12_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/12_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "12"
_spec = importlib.util.spec_from_file_location("sim12", os.path.join(HERE, "..", "12_sim.py"))
sim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sim)
RC = sim.R * sim.C
print(f"[数值] R {sim.R/1e3:.0f} kΩ，C {sim.C*1e9:.0f} nF → RC {RC*1e3:.1f} ms")


def integrator(d, rf=None, cur=False):
    """反相积分器：01 节的反相放大把 R_f 换成电容 C；rf 不为 None 时在 C 旁再并一个电阻。"""
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot().label("虚地 0 V", "bottom", ofst=0.15) if cur else elm.Dot())
    r = elm.Resistor().left().label("$R$ 10 kΩ")
    if cur:
        r.label("$I \\rightarrow$", "bottom")
    d += r
    d += elm.Dot(open=True).label("$V_i$ 输入", "left")
    d += elm.Line().up().at(j.center).length(1.5)
    d += (a := elm.Dot()) if rf else elm.Line().length(0)
    c = elm.Capacitor().right().label("$C$ 100 nF").tox(op.out.x + 0.5)
    if cur:
        c.label("$I \\rightarrow$ 给电容充电", "bottom")
    d += c
    d += (b := elm.Dot()) if rf else elm.Line().length(0)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    if rf:
        d += elm.Line().up().at(a.center).length(1.5)
        d += elm.Resistor().right().label(rf).tox(b.center.x)
        d += elm.Line().down().toy(b.center)
    d += elm.Line().left().at(op.in2).length(0.5)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$ 输出", "right")


# ---------- 图 12-p1-1 面积直觉：输出 = −(输入曲线下的面积) ÷ RC ----------
t = np.arange(0, 6e-3, 1e-6)
vin = np.select([t < 2e-3, t < 3e-3, t < 5e-3], [1.0, 0.0, -0.5], 0.0)
vo = sim.integrate(t, vin)
fig, (a0, a1) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
tm = t * 1e3
a0.plot(tm, vin, **fs.LS["vin"], label="输入电压 $V_i$")
a0.fill_between(tm, 0, vin, where=vin > 0, color=fs.C["vin"], alpha=0.25)
a0.fill_between(tm, 0, vin, where=vin < 0, color=fs.C["third"], alpha=0.25)  # 负面积不是错误，用红紫色
a0.text(1.0, 0.45, "面积 +2 V·ms", ha="center", fontsize=9)
a0.text(4.0, -0.3, "面积 −1 V·ms", ha="center", fontsize=9)
print("[数值] 面积 +2 V·ms（1 V × 2 ms），−1 V·ms（−0.5 V × 2 ms）")
fs.ref_h(a0, 0)
a0.set_ylim(-0.9, 1.4); a0.set_ylabel(fs.qlabel("输入", "V")); a0.legend(loc="upper right", fontsize=8)
a1.plot(tm, vo, **fs.LS["vout"], label="积分器输出 $V_o$（RC = 1 ms）")
for x in (2.0, 3.0, 5.0):
    k = int(round(x * 1e3))
    fs.mark(a1, x, vo[k], "{:.1f}", " V", dx=4, dy=-12)
assert abs(vo[2000] + 2.0) < 0.01 and abs(vo[3000] + 2.0) < 0.01 and abs(vo[5000] + 1.0) < 0.01
fs.ref_h(a1, 0)
a1.set_ylim(-2.6, 0.6); a1.set_ylabel(fs.qlabel("输出", "V")); a1.legend(loc="upper right", fontsize=8)
a1.set_xlabel(fs.qlabel("时间", "ms"))
fs.save(fig, N, "12_p1_1_area.png")

# ---------- 图 12-p1-2 积分器电路 ----------
with drawing() as d:
    integrator(d)
save_schem(d, N, "12_p1_2_integrator.png")

# ---------- 图 12-p1-3 方波进、三角波出 ----------
t = np.arange(0, 6e-3, 1e-6)
vin = sim.square(t)
vo = sim.integrate(t, vin)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vin, **fs.LS["vin"], label="输入：±1 V、500 Hz 方波")
ax.plot(t * 1e3, vo, **fs.LS["vout"], label="输出：三角波")
ax.annotate("输入 +1 V：\n每 ms 下降 1 V", (0.5, -0.5), xytext=(0.15, -1.75), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="0.3"))
ax.annotate("输入 −1 V：\n每 ms 上升 1 V", (1.5, -0.5), xytext=(2.2, -1.75), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="0.3"))
pp = vo.max() - vo.min()
print(f"[数值] 斜率 ±1 V/ms，三角波峰峰值 {pp:.2f} V（0 到 −1 V）")
assert abs(pp - 1.0) < 0.01
fs.ref_h(ax, 0)
ax.set_ylim(-2.2, 1.9)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.legend(loc="upper right", fontsize=8, ncol=2)
fs.save(fig, N, "12_p1_3_square_triangle.png")

# ---------- 图 12-p2-1 推导用：电流 I 和虚地 ----------
with drawing() as d:
    integrator(d, cur=True)
save_schem(d, N, "12_p2_1_analysis.png")

# ---------- 图 12-p2-2 实用积分器：C 旁并 R_f ----------
with drawing() as d:
    integrator(d, rf="$R_f$ 1 MΩ（给直流一条出路）")
save_schem(d, N, "12_p2_2_practical.png")

# ---------- 图 12-p3-1 R_f 怎么选：大了漂得远，小了三角波变形 ----------
rfs = [10e3, 100e3, 1e6, 10e6]
t = np.arange(0, 3.0, 5e-6)
centers = []
for rf in rfs:
    v = sim.integrate(t, sim.square(t, offset=sim.OFFSET), rf=rf)
    centers.append(v[t > 2.9].mean())
    print(f"[数值] R_f {rf/1e3:g} kΩ：20 mV 偏置下输出中心 {centers[-1]:.2f} V（理论 −R_f/R×20 mV = {-rf/sim.R*0.02:.2f} V）")
assert abs(centers[2] + 2.0) < 0.05 and centers[3] < -12      # 10 MΩ 已经接近饱和
fig, (a0, a1) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a0.semilogx(rfs, centers, **{**fs.LS["bad"], "marker": "o", "markevery": 1})
for rf, c in zip(rfs, centers):
    txt = f"{c:.2f} V（顶到饱和）" if rf > 5e6 else f"{c:.2f} V"
    a0.annotate(txt, (rf, c), xytext=(-70, 10) if rf > 5e6 else (6, 4), textcoords="offset points", fontsize=8)
fs.ref_h(a0, -sim.VSAT, "−13.5 V 饱和", x=0.02, ha="left")
a0.set_xlim(5e3, 3e7); a0.set_ylim(-15, 1.5)
fs.axlabels(a0, "$R_f$", "Ω", "输出中心电平", "V")
a0.set_title("(a) 20 mV 偏置把输出推离 0 V", fontsize=10)
ts = np.arange(0, 0.2, 2e-6)
styles = [fs.LS["bad"], fs.LS["third"], fs.LS["vout"]]
pps = []
for rf, st in zip(rfs[:3], styles):
    v = sim.integrate(ts, sim.square(ts), rf=rf)
    k = ts > 0.2 - 4e-3
    pps.append(v[k].max() - v[k].min())
    a1.plot((ts[k] - ts[k][0]) * 1e3, v[k], **st, label=f"$R_f$ = {rf/1e3:g} kΩ：峰峰 {pps[-1]:.2f} V")
    print(f"[数值] R_f {rf/1e3:g} kΩ：500 Hz 方波稳定后输出峰峰值 {pps[-1]:.2f} V（理想 1.00 V）")
assert 0.9 < pps[0] < 0.95 and abs(pps[1] - 1.0) < 0.02 and abs(pps[2] - 1.0) < 0.02
a1.set_ylim(-1.0, 1.0)
fs.axlabels(a1, "时间", "ms", "输出", "V"); a1.legend(loc="lower right", fontsize=7)
a1.set_title("(b) $R_f$ 太小：三角波被压扁、变圆", fontsize=10)
fig.tight_layout()
fs.save(fig, N, "12_p3_1_rf_sweep.png")

# ---------- 图 12-p3-2 时间常数 RC 怎么选 ----------
t = np.arange(0, 6e-3, 1e-6)
vin = sim.square(t)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
for c, st in zip([5e-9, 100e-9, 1e-6], [fs.LS["bad"], fs.LS["vout"], fs.LS["third"]]):
    v = sim.integrate(t, vin, c=c)
    pp = v.max() - v.min()
    rc = sim.R * c * 1e3
    print(f"[数值] C {c*1e9:g} nF（RC {rc:g} ms）：输出峰峰 {pp:.2f} V，最低 {v.min():.2f} V")
    ax.plot(t * 1e3, v, **st, label=(f"C = {c*1e9:g} nF" if c < 1e-6 else "C = 1 μF") + f"，RC = {rc:g} ms：峰峰 {pp:.2f} V")
    if c == 5e-9:
        assert v.min() <= -sim.VSAT + 1e-6
fs.ref_h(ax, -sim.VSAT, "−13.5 V 饱和（被削平）", x=0.99)
ax.set_ylim(-15, 17)
fs.axlabels(ax, "时间", "ms", "输出", "V"); ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "12_p3_2_rc_choice.png")

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


def bb12():
    """12 page4：慢动作积分器。两节 9 V 电池给 LM358 供 ±9 V；R = 1 MΩ、C = 1 µF（RC = 1 s），
    输入取自两组 82k/1k 分压（约 ±0.108 V），万用表加秒表就能看到斜坡。"""
    bb = Breadboard(ncol=24, rails=dict(tp=("+9 V", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"),
                                        bn=("−9 V", "neg")), figsize=(10, 5.8))
    bb.wire(bb.ext((-2.0, 11.4), "电池 A 的 +", "pos"), "tp1", "pos")
    bb.wire(bb.ext((-2.0, 10.0), "A 的 − 和 B 的 +（相连）", "gnd"), "tn2", "gnd")
    bb.wire(bb.ext((-2.0, -3.4), "电池 B 的 −", "neg"), "bn1", "neg")
    bb.wire("tn3", "bp3", "gnd")                                 # 上下两条 0 V 轨连起来
    # 正输入分压：+9 V —82k— 第 9 列 —1k— 0 V
    bb.wire("a5", "tp5", "pos")
    bb.two("R1", "b5", "b9", "R", "82k", lpos=(0, 0.55))
    bb.two("R2", "c9", "c11", "R", "1k", lpos=(0, -0.5))
    bb.wire("a11", "tn11", "gnd")
    # 负输入分压：−9 V —82k— 第 9 列 —1k— 0 V
    bb.wire("j5", "bn5", "neg")
    bb.two("R3", "i5", "i9", "R", "82k", lpos=(0, -0.5))
    bb.two("R4", "h9", "h11", "R", "1k", lpos=(0, 0.5))
    bb.wire("j11", "bp11", "gnd")
    # LM358：1 脚在 f16
    bb.dip8("U1", 16, "LM358")
    bb.wire("a16", "tp16", "pos")                                # 8 脚 V+
    bb.wire("j19", "bn19", "neg")                                # 4 脚 V−
    bb.wire("d17", "d18", "sig")                                 # B 组接成跟随器：7 脚连 6 脚
    bb.wire("a19", "tn19", "gnd")                                # B 组 5 脚接地
    # 积分器（A 组）：输入第 13 列 —R 1M— 2 脚（第 17 列）；C 跨在 1 脚和 2 脚之间
    bb.two("RIN", "i13", "i17", "R", "R 1M", lpos=(0, -0.5))
    bb.two("C1", "g16", "g17", "C", "1µF", lpos=(0, 0.55))
    bb.two("RP", "j18", "bp17", "R", "1M", lpos=(0.45, 0.1))
    bb.wire("j16", "j17", "sig")                                 # 清零线：短接电容
    bb.wire("f13", "e9", "sig")                                  # 输入线：现在接正输入
    bb.note(12.0, -4.6, "输入线 f13 的另一端：插 e9 = +0.108 V，改插 f9 = −0.108 V，改插 0 V 轨 = 0 V", ha="center")
    bb.note(12.0, -5.15, "j16–j17 是清零线（拔掉 = 开始积分）；第 10 步拔掉它、改插 10 MΩ 到 j16–j17", ha="center")
    assert bb.connected("U1.8", "tp1") and bb.connected("U1.4", "bn1") and bb.connected("U1.5", "tn1")
    assert bb.connected("U1.6", "U1.7")
    assert bb.connected("R1.2", "R2.1", "RIN.1") and bb.connected("R1.1", "tp1") and bb.connected("R2.2", "tn1")
    assert bb.connected("R3.2", "R4.1") and bb.connected("R3.1", "bn1") and bb.connected("R4.2", "bp1")
    assert bb.connected("RIN.2", "U1.2", "C1.2") and bb.connected("C1.1", "U1.1")
    assert bb.connected("U1.3", "RP.1") and bb.connected("RP.2", "bp1", "tn1")
    assert not bb.connected("tp1", "bn1") and not bb.connected("tp1", "tn1") and not bb.connected("bn1", "bp1")
    assert not bb.connected("R3.2", "RIN.1")
    bb.probe("d9", "+0.108 V", dx=-0.3, dy=0.3, ha="right")
    bb.probe("g9", "−0.108 V", dx=-0.3, dy=-0.3, ha="right")
    bb.probe("g13", "V_i", dx=-0.3, dy=0.05, ha="right")
    bb.probe("h16", "V_o", dx=-0.3, dy=0.05, ha="right")
    bb.probe("h18", "V_+", dx=0.3, dy=0.05)
    bb.legend(("pos", "gnd", "neg", "sig"))
    print(f"12 p4 面包板：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def p4_breadboards():
    bb = bb12()
    fs.save(bb.fig, N, "12_p4_1_bb_integrator.png")
    plt.close(bb.fig)
    print("12_figs p4 OK")


if __name__ == "__main__":
    p4_breadboards()


# ===== 第 8 轮补图（page1–3）=====
from schem import *
HL = C["bad"]


def _l(d, xy, text, color=None):
    e = elm.Label().at(xy).label(text, loc="center")
    if color: e = e.color(color)
    d += e


def integ2(d, vin="$V_i$ 输入", rl="$R$ 10 kΩ", cl="$C$ 100 nF", par=None, cin=False, trim=False):
    """反相积分器变体：par=("sw"/"rf", 标签) 在 C 旁并开关或电阻；cin 输入串隔直电容；trim 同相端接可调基准。"""
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    d += elm.Resistor().left().label(rl)
    if cin:
        d += elm.Capacitor().left().label("$C_{in}$ 隔直").color(HL)
    d += (ind := elm.Dot(open=True).label(vin, "left"))
    op.ind = ind
    d += elm.Line().up().at(j.center).length(1.5)
    d += (a := elm.Dot())
    d += elm.Capacitor().right().label(cl).tox(op.out.x + 0.5)
    d += (b := elm.Dot())
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    if par:
        kind, lab = par
        d += elm.Line().up().at(a.center).length(1.5)
        if kind == "sw":
            d += elm.Switch().right().tox(b.center.x).label(lab).color(HL)
        else:
            d += elm.Resistor().right().tox(b.center.x).label(lab).color(HL)
        d += elm.Line().down().toy(b.center)
    d += elm.Line().left().at(op.in2).length(0.5)
    if trim:
        d += elm.Line().down().length(0.3)
        d += (sv := elm.SourceV().down().length(1.6).reverse().color(HL))
        _l(d, (sv.center.x - 1.6, sv.center.y), "可调基准\n（抵消失调）", HL)
    else:
        d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$ 输出", "right")
    return op


def p1_4_passive():
    with drawing(fontsize=11) as d:
        # (a) 无源 RC：输入 → R → 输出点，C 接地
        d += elm.Dot(open=True).at((0, 3)).label("$V_i$ 输入", "left")
        d += elm.Resistor().right().label("$R$")
        d += (n := elm.Dot())
        d += elm.Capacitor().down().length(2.2)
        _l(d, (n.center.x + 0.7, n.center.y - 1.1), "$C$")
        d += elm.Ground()
        d += elm.Line().right().at(n.center).length(1.5)
        d += elm.Dot(open=True).label("电容电压当输出", "right")
        _l(d, (2.5, -0.9), "(a) 无源 RC：电容越满，电流越小")
        # (b) 运放积分器
        d.here = (13.0, 2.2)
        integ2(d)
        _l(d, (12.5, -0.9), "(b) 运放积分器：反相端是虚地，电流恒为输入 ÷ R")
    save_schem(d, "12", "12_p1_4_passive_vs_opamp.png")


def p1_5_bench():
    with drawing(fontsize=11) as d:
        op = integ2(d, vin="")
        x0, y0 = op.ind.center.x, op.ind.center.y
        d += elm.SourceSin().down().at((x0 - 1.5, y0)).length(2.2)
        _l(d, (x0 - 3.2, y0 - 1.1), "信号发生器")
        d += elm.Line().right().at((x0 - 1.5, y0)).tox(x0)
        d += elm.Ground().at((x0 - 1.5, y0 - 2.2))
        d += elm.Line().down().at((x0 - 0.75, y0)).length(0.0)
        d += elm.Dot().at((x0 - 0.75, y0))
        d += elm.Line().up().at((x0 - 0.75, y0)).length(1.2).color(C["vin"])
        _l(d, (x0 - 0.75, y0 + 1.6), "示波器 CH1", C["vin"])
        xo = op.out.x + 1.25
        d += elm.Line().down().at((xo, op.out.y)).length(1.2).color(C["vout"])
        _l(d, (xo, op.out.y - 1.6), "示波器 CH2", C["vout"])
        _l(d, (op.center.x, op.center.y - 2.6), "运放 ±15 V 供电（图中省略）")
    save_schem(d, "12", "12_p1_5_bench.png")


def p2_4_ramp():
    with drawing(fontsize=11) as d:
        integ2(d, vin="−0.5 V 恒定输入", rl="$R$ 10 kΩ", cl="$C$ 100 nF（RC = 1 ms）", par=("sw", "清零开关"))
    save_schem(d, "12", "12_p2_4_ramp.png")


def p3_3_fixes():
    with drawing(fontsize=11) as d:
        integ2(d, par=("rf", "$R_f$"), cin=True)
        _l(d, (1.0, -3.8), "(a) 输入端串隔直电容")
        d.here = (16.0, 0)
        integ2(d, par=("rf", "$R_f$"), trim=True)
        _l(d, (16.5, -3.8), "(b) 同相端接可调基准")
    save_schem(d, "12", "12_p3_3_fixes.png")


def p3_4_coulomb():
    with drawing(fontsize=11) as d:
        integ2(d, vin="电流传感器\n0.1 V/A", rl="$R$ 200 kΩ", cl="$C$ 1 μF（RC = 0.2 s）", par=("sw", "测量前清零"))
    save_schem(d, "12", "12_p3_4_coulomb.png")


def round8():
    p1_4_passive(); p1_5_bench(); p2_4_ramp(); p3_3_fixes(); p3_4_coulomb()
    print("12_figs 第 8 轮补图 OK")


if __name__ == "__main__":
    round8()
