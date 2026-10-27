"""35 程控增益与 AGC：全部配图。运行（仓库根目录）：/workspace/circuits-venv/bin/python code/figs/35_figs.py
数字来自 code/35_sim.py（Python 模拟）和 spice/35/*.cir（ngspice + TI LM358 模型）；本脚本会打印图上标的数。
本文件里的 Breadboard 类照抄自 21_figs.py，另加了 16 脚芯片 dip16()；40、41 节的面包板图也从这里导入它。"""
import os, sys, re, shutil, subprocess, tempfile, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import figstyle as fs
from figstyle import C

P = "35"


def load_sim():
    spec = importlib.util.spec_from_file_location("sim35", os.path.join(ROOT, "code", "35_sim.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_spice(node, cir, vectors):
    """把 spice/<node>/<cir> 复制到临时目录（.include 改成绝对路径），在 .endc 前加 wrdata，跑 ngspice，返回数组。
    返回的列：第 0 列为自变量，之后每个向量一列（wrdata 的成对列已去重）。"""
    src = os.path.join(ROOT, "spice", node, cir)
    txt = open(src, encoding="utf-8").read()
    txt = txt.replace("../models/", os.path.join(ROOT, "spice", "models") + "/")
    txt = re.sub(r"^\.endc", "wrdata out.dat " + " ".join(vectors) + "\n.endc", txt, count=1, flags=re.M)
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, "a.cir"), "w", encoding="utf-8").write(txt)
        shutil.copy(os.path.join(ROOT, "spice", node, ".spiceinit"), tmp)
        r = subprocess.run([shutil.which("ngspice") or "/usr/bin/ngspice", "-b", "a.cir"], cwd=tmp,
                           capture_output=True, text=True, timeout=600)
        assert os.path.exists(os.path.join(tmp, "out.dat")), r.stdout[-1500:] + r.stderr[-1500:]
        d = np.loadtxt(os.path.join(tmp, "out.dat"))
    return np.column_stack([d[:, 0]] + [d[:, 2 * i + 1] for i in range(len(vectors))])


# ======================================================================
# 面包板小工具（照抄 21_figs.py，另加 dip16）
# ======================================================================
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

    def wire(self, h1, h2, kind="sig", bend=0.0, via=(), hops=(), hop_r=0.3):
        """via：中间拐点（走在两列孔之间，避免压孔）；hops：竖直线段跨过电源轨线的 y 值，画成半圆「跨线弯」。"""
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
                if xa == xb:
                    sgn = 1 if yb > ya else -1
                    for yh in sorted([h for h in hops if min(ya, yb) + hop_r < h < max(ya, yb) - hop_r], key=lambda h: sgn * h):
                        th = np.linspace(-np.pi / 2, np.pi / 2, 15)
                        xs += list(xa - hop_r * np.cos(th)); ys += list(yh + sgn * hop_r * np.sin(th))
                xs.append(xb); ys.append(yb)
        self.ax.plot(xs, ys, color=BB_WIRE[kind], lw=2.4, solid_capstyle="round", zorder=3)
        for x, y in ((x1, y1), (x2, y2)):
            self.ax.plot(x, y, "o", ms=3.2, color=BB_WIRE[kind], zorder=4)

    def ext(self, xy, text, kind="sig", dx=-0.45, dy=0.0, ha="right"):
        self.ax.plot(*xy, "o", ms=7, mfc="white", mec=BB_WIRE[kind], mew=1.6, zorder=5)
        self.ax.text(xy[0] + dx, xy[1] + dy, text, ha=ha, va="center", fontsize=8, color=BB_WIRE[kind], zorder=5)
        return xy

    def _pins(self, name, hs):
        for k, h in hs.items():
            self._use(h, f"{name}.{k}")
            self.pins[f"{name}.{k}"] = h

    def two(self, name, h1, h2, style="R", label=None, lpos=None):
        """两脚元件：style = R / C / CE（h1 为 + 脚）/ D（h1 阳极）/ LED / Z / L / F。"""
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
        if style in ("D", "Z", "LED"):
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

    def dipn(self, name, col, n, label):
        """n 脚双列直插芯片跨在中间凹槽上，缺口朝左：1…n/2 脚在 f 行（col 起往右），n/2+1…n 脚在 e 行（从右往左）。"""
        m = n // 2
        hs = {}
        for k in range(m):
            hs[str(1 + k)] = f"f{col + k}"
            hs[str(n - k)] = f"e{col + k}"
        self._pins(name, hs)
        ax = self.ax
        ax.add_patch(mpatches.FancyBboxPatch((col - 0.45, 3.35), m - 0.1, 1.3, boxstyle="round,pad=0.05",
                                             fc="#333333", ec="k", zorder=6))
        ax.add_patch(mpatches.Wedge((col - 0.45, 4.0), 0.25, -90, 90, fc="#888888", zorder=7))
        ax.text(col + (m - 1) / 2, 4.0, label, color="white", fontsize=7.5, ha="center", va="center", zorder=7)
        for k in range(m):
            for pin, y in ((1 + k, 3.0), (n - k, 5.0)):
                ax.plot([col + k, col + k], [y, 4.0 + (0.65 if y > 4 else -0.65)], color="0.3", lw=1.4, zorder=5)
            ax.text(col + k, 3.55, str(1 + k), color="white", fontsize=6, ha="center", va="center", zorder=8)
            ax.text(col + k, 4.45, str(n - k), color="white", fontsize=6, ha="center", va="center", zorder=8)

    def dip8(self, name, col, label):
        self.dipn(name, col, 8, label)

    def dip16(self, name, col, label):
        self.dipn(name, col, 16, label)

    def multi(self, name, hs, label, w=None, h=1.0, fc="#555555", at=None):
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
        x, y = self.xy(h)
        self.ax.plot(x, y, "o", ms=9, mfc="none", mec=C["third"], mew=1.6, zorder=9)
        self.ax.text(x + dx, y + dy, text, fontsize=7.5, color=C["third"], ha=ha, va="bottom", zorder=9,
                     bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))

    def note(self, x, y, text, **kw):
        kw.setdefault("fontsize", 8)
        self.ax.text(x, y, text, **kw)

    def legend(self, kinds=("pos", "gnd", "neg", "sig"), y=0.035):
        from matplotlib.lines import Line2D
        names = dict(pos="正电源线（橙）", gnd="0 V 地线（黑）", neg="负电源线（蓝）", sig="信号线（绿）")
        hs = [Line2D([], [], color=BB_WIRE[k], lw=2.4, label=names[k]) for k in kinds]
        self.ax.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, y), ncol=len(hs), fontsize=8,
                       frameon=False)


# ======================================================================
# page1
# ======================================================================
def p1_1_fixed_vs_auto(S):
    """图 35-p1-1：输入从 3 mV 到 2 V，固定 G≈2、固定 G≈69 与自动换挡三种情况下，ADC 看到多少个字。"""
    vin = np.logspace(np.log10(3e-3), np.log10(1.5), 400)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for g, sty, name in ((S.G_REAL[0], LSkey("vin"), "固定 X0 档（G≈2）"), (S.G_REAL[5], LSkey("fb"), "固定 X5 档（G≈69）")):
        n = [S.adc(min(g * v, S.VCLIP)) for v in vin]
        ax.plot(vin * 1e3, n, **sty, label=name)
    ks, vo, _ = S.digital_agc(np.repeat(vin, 8))
    n = [S.adc(v) for v in vo[7::8]]
    ax.plot(vin * 1e3, n, **LSkey("vout"), label="自动换挡（30 %–90 %）")
    ax.set_xscale("log"); ax.set_yscale("log")
    fs.ref_h(ax, S.adc(S.FS), f"满量程 3.0 V = {S.adc(S.FS)} 字", x=0.45)
    fs.ref_h(ax, S.adc(S.UP * S.FS), f"30 % = {S.adc(S.UP*S.FS)} 字", x=0.98)
    fs.ref_h(ax, round(S.DOWN * S.adc(S.FS)), f"90 % = {round(S.DOWN * S.adc(S.FS))} 字", x=0.98)
    n12 = S.adc(S.G_REAL[0] * 0.03)
    fs.mark(ax, 30, n12, "{:.0f}", " 字", dx=0, dy=0)
    fs.axlabels(ax, "输入幅度", "mV", "ADC 读数", "字")
    ax.set_ylim(0.8, 1400)
    ax.legend(loc="lower right", fontsize=8)
    fs.save(fig, P, "35_p1_1_fixed_vs_auto.png")
    print(f"[图 35-p1-1] 30 mV 在 G≈2 下 {n12} 字；满量程 {S.adc(S.FS)} 字；30 % 门槛 {S.adc(S.UP*S.FS)} 字")


def LSkey(k):
    return dict(fs.LS[k])


def p1_2_blocks():
    """图 35-p1-2：数字 AGC 的方框图。"""
    fig, ax = fs.diagram(9, 2.8)
    s = fs.box(ax, 0.9, 1.6, "传感器\n小信号", w=1.3, h=0.8)
    a = fs.box(ax, 3.0, 1.6, "程控增益\n放大器 PGA", w=1.6, h=0.8, fc=C["hi"])
    d = fs.box(ax, 5.2, 1.6, "ADC", w=1.0, h=0.8)
    m = fs.box(ax, 7.4, 1.6, "单片机\n比较 + 换挡", w=1.7, h=0.8)
    fs.arrow(ax, s["r"], a["l"])
    fs.arrow(ax, a["r"], d["l"], "放大后")
    fs.arrow(ax, d["r"], m["l"], "读数")
    ax.annotate("", xy=(3.0, 1.2), xytext=(7.4, 1.2), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=C["edge"],
                connectionstyle="bar,fraction=-0.25"))
    ax.text(5.2, 0.35, "选档线（换哪个电阻）", ha="center", fontsize=9)
    ax.text(7.4, 2.35, "读数 > 90 % 满量程 → 降一档\n读数 < 30 % 满量程 → 升一档", ha="center", fontsize=8.5)
    fs.save(fig, P, "35_p1_2_blocks.png")


def p1_3_db():
    """图 35-p1-6：倍数与 dB 的对照尺，标出六个档位（名义值）。"""
    fig, ax = plt.subplots(figsize=fs.SIZE["diagram"])
    g = np.logspace(0, 3, 400)
    ax.plot(g, 20 * np.log10(g), **LSkey("vout"))
    for gn, lab in ((2, "×2"), (5.17, "×5.17"), (10.09, "×10.1"), (20.6, "×20.6"), (51, "×51"), (101, "×101")):
        ax.plot(gn, 20 * np.log10(gn), "o", color=C["vin"])
        ax.text(gn, 20 * np.log10(gn) + 4, f"{lab}\n{20*np.log10(gn):.1f} dB", ha="center", fontsize=8)
        print(f"[图 35-p1-6] {lab} = {20*np.log10(gn):.2f} dB")
    ax.set_xscale("log")
    fs.axlabels(ax, "放大倍数 G", None, "20·lg G", "dB")
    ax.set_ylim(-2, 72)
    fs.save(fig, P, "35_p1_6_db.png")


# ======================================================================
# page2：电路图
# ======================================================================
import schem
from schem import elm


def _opamp_core(d, x0=0.0, y0=0.0):
    """同相放大：+ 在上（theta(0).flip()），返回 op。"""
    op = elm.Opamp(leads=True).theta(0).flip().anchor("in2").at((x0, y0))
    d += op
    return op


def p2_1_series(S, name="35_p2_1_series.png"):
    """图：CD4051（带引脚名方框）的 COM 接反相端，X0…X5 各串一个 R_g 到地。R_on 与 R_g 串联，进增益。"""
    with schem.drawing(fontsize=11) as d:
        op = _opamp_core(d, 2.0, 4.0)
        pp, pm, po = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
        d += elm.Line().at(pp).to((0.0, pp[1]))
        d += elm.Dot(open=True).at((0.0, pp[1])).label("$V_{in}$", "left")
        xo = po[0] + 1.0
        for xy, t in (((pp[0] - 0.3, pp[1] + 0.3), "3"), ((pm[0] - 0.3, pm[1] + 0.3), "2"), ((po[0] + 0.35, po[1] + 0.3), "1")):
            d += elm.Label().at(xy).label(t, fontsize=9)
        d += elm.Label().at((op.center[0], op.center[1] + 1.9)).label("U1A（LM358，8 脚 +5 V、4 脚地）", fontsize=10)
        d += elm.Line().at(po).to((xo + 1.0, po[1]))
        d += elm.Dot(open=True).at((xo + 1.0, po[1])).label("$V_{out}$\n→ ADC", "right")
        d += elm.Dot().at((xo, po[1]))
        yt = pm[1] - 1.6
        xm = pm[0] - 0.6
        d += elm.Line().at(pm).to((xm, pm[1]))
        d += elm.Line().at((xm, pm[1])).to((xm, yt))
        d += elm.Dot().at((xm, yt))
        d += elm.Resistor().at((xm, yt)).to((xo, yt)).label("$R_f$ 100 kΩ", "top")
        d += elm.Line().at((xo, yt)).to((xo, po[1]))
        mod = schem.module("CD4051（8 选 1 模拟开关）", left=("3 COM", "11 A", "10 B", "9 C", "6 INH"),
                           right=("13 X0", "14 X1", "15 X2", "12 X3", "1 X4", "5 X5"), w=5.0)
        d += mod.theta(0).anchor("3 COM").at((xm, yt - 3.6))
        a = mod.absanchors
        d += elm.Line().at((xm, yt)).to(a["3 COM"])
        for nm, txt in (("11 A", "A"), ("10 B", "B"), ("9 C", "C")):
            q = a[nm]
            d += elm.Line().at(q).to((q[0] - 0.8, q[1]))
            d += elm.Dot(open=True).at((q[0] - 0.8, q[1])).label(f"选档 {txt}", "left", fontsize=9)
        q = a["6 INH"]
        d += elm.Line().at(q).to((q[0] - 0.8, q[1])); d += elm.Ground().at((q[0] - 0.8, q[1]))
        # 方框里画「当前接通 X5」的示意开关
        xl_in, xr_in = a["3 COM"][0] + 1.9, a["5 X5"][0] - 1.9
        d += elm.Line().at((xl_in, a["3 COM"][1])).to((xr_in, a["5 X5"][1])).color(C["vout"]).linewidth(2.4)
        d += elm.Label().at(((xl_in + xr_in) / 2 + 0.25, (a["3 COM"][1] + a["5 X5"][1]) / 2)).label("接通 X5\n约 470 Ω", fontsize=9, color=C["vout"], halign="left")
        rg = dict(X0="100 kΩ", X1="24 kΩ", X2="11 kΩ", X3="5.1 kΩ", X4="2 kΩ", X5="1 kΩ")
        xg = a["13 X0"][0] + 3.2
        for nm in ("13 X0", "14 X1", "15 X2", "12 X3", "1 X4", "5 X5"):
            q = a[nm]; on = nm.endswith("X5")
            r = elm.Resistor().at(q).to((xg, q[1])).scale(0.8)
            d += r.color(C["vout"]) if on else r
            d += elm.Label().at(((q[0] + xg) / 2, q[1] + 0.32)).label("$R_g$ " + rg[nm.split()[1]], fontsize=8.5)
        d += elm.Line().at((xg, a["13 X0"][1])).to((xg, a["5 X5"][1]))
        d += elm.Ground().at((xg, a["5 X5"][1]))
        d += elm.Label().at((xo + 1.6, yt - 0.6)).label("$G = 1 + \\dfrac{R_f}{R_g + R_{on}}$", halign="left", fontsize=12)
        d += elm.Label().at((a["3 COM"][0] + 2.5, a["6 INH"][1] - 2.0)).label("16 VDD → +5 V；7 VEE、8 VSS → 0 V（图中略）", fontsize=9, color="#555555")
        schem.save_schem(d, P, name)


def p2_2_ron_error(S):
    """图 35-p2-2：六档的增益误差，R_on = 125 Ω（15 V 供电典型值）与 470 Ω（5 V 供电典型值）。"""
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    k = np.arange(6)
    e125 = [100 * ((1 + S.RF / (r + 125)) / (1 + S.RF / r) - 1) for r in S.RG]
    e470 = [100 * (S.G_REAL[i] / S.G_NOM[i] - 1) for i in range(6)]
    ax.bar(k - 0.18, e125, 0.36, color=C["vin"], label="$R_{on}$ = 125 Ω（VDD = 15 V）")
    ax.bar(k + 0.18, e470, 0.36, color=C["bad"], label="$R_{on}$ = 470 Ω（VDD = 5 V）")
    for i in range(6):
        ax.text(i + 0.18, e470[i] - 1.0, f"{e470[i]:.1f}%", ha="center", va="top", fontsize=8)
        ax.text(i - 0.18, e125[i] - 1.0, f"{e125[i]:.1f}", ha="center", va="top", fontsize=7.5, color=C["vin"])
    ax.set_xticks(k, [f"X{i}\nG={S.G_NOM[i]:.3g}" for i in k])
    fs.axlabels(ax, "档位（名义增益）", None, "增益误差", "%")
    ax.set_ylim(-37, 2)
    ax.axhline(0, color="k", lw=0.8)
    ax.legend(loc="lower left", fontsize=8)
    fs.save(fig, P, "35_p2_2_ron_error.png")
    print("[图 35-p2-2] 125 Ω 误差 %:", [round(x, 2) for x in e125], " 470 Ω 误差 %:", [round(x, 2) for x in e470])


def p2_3_kelvin():
    """图 35-p2-3：抽头接法。电阻串从输出到地，开关只把某个抽头接到反相端（几乎没有电流流过开关）。"""
    with schem.drawing(fontsize=11) as d:
        op = _opamp_core(d, 2.0, 4.0)
        pp, pm, po = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
        d += elm.Line().at(pp).to((0.0, pp[1]))
        d += elm.Dot(open=True).at((0.0, pp[1])).label("$V_{in}$", "left")
        xl = po[0] + 1.2
        d += elm.Line().at(po).to((xl + 1.2, po[1]))
        d += elm.Dot(open=True).at((xl + 1.2, po[1])).label("$V_{out}$", "right")
        d += elm.Dot().at((xl, po[1]))
        vals = ["51k", "30k", "10k", "5.1k", "3k", "1k", "1k"]
        y = po[1]
        taps = []
        for i, v in enumerate(vals):
            d += elm.Resistor().at((xl, y)).to((xl, y - 1.5))
            d += elm.Label().at((xl + 0.45, y - 0.75)).label(v, halign="left", fontsize=9.5)
            y -= 1.5
            if i < 6:
                d += elm.Dot().at((xl, y))
                taps.append((xl, y))
        d += elm.Ground().at((xl, y))
        gains = ["2.02", "5.03", "10.0", "20.2", "50.6", "101"]
        xsw = xl - 0.7
        xb = xsw - 1.6
        for i, (tx, ty) in enumerate(taps):
            on = (i == 5)
            col = C["vout"] if on else "black"
            d += elm.Line().at((tx, ty)).to((xsw, ty)).color(col)
            if on:
                d += elm.Line().at((xsw, ty)).to((xb, ty)).color(col).linewidth(2.4)
                d += elm.Dot(open=True).at((xsw - 0.35, ty)); d += elm.Dot(open=True).at((xb + 0.35, ty))
            else:
                d += elm.Switch().at((xsw, ty)).to((xb, ty))
            d += elm.Label().at((xb - 0.15, ty - 0.35)).label(f"X{i}  G={gains[i]}", halign="right", fontsize=8.5,
                                                                 color=col)
        ybot, ytop = taps[-1][1], taps[0][1]
        d += elm.Line().at((xb, ybot)).to((xb, ytop))
        xin = pm[0] - 0.6
        d += elm.Line().at((xb, ytop)).to((xin, ytop))
        d += elm.Line().at((xin, ytop)).to((xin, pm[1]))
        d += elm.Line().at((xin, pm[1])).to(pm)
        d += elm.Label().at((xb - 0.15, ybot - 1.0)).label("X5 接通：$R_{on}$ 约 470 Ω\n（几乎不流电流，不进倍数）", halign="right", fontsize=9, color=C["vout"])
        d += elm.Label().at((xin - 0.15, (ytop + pm[1]) / 2 - 0.3)).label("CD4051\nCOM", halign="right", fontsize=9)
        # 链电流箭头
        xa = xl + 1.6
        d += elm.Arrow().at((xa, po[1] - 0.6)).to((xa, ybot - 0.9)).color(C["vin"]).linewidth(1.8)
        d += elm.Label().at((xa + 0.25, (po[1] + ybot) / 2)).label("链电流\n$V_{out}$ ÷ 101 kΩ\n（2 V 时约 20 µA）",
                                                                   halign="left", fontsize=9, color=C["vin"])
        schem.save_schem(d, P, "35_p2_3_kelvin.png")


def p2_4_peak():
    """图 35-p2-4：单二极管峰值检波 vs 精密峰值检波（SPICE 波形）。"""
    a = run_spice("35", "t_peak.cir", ["v(in)", "v(pa)", "v(hb)"])
    t = a[:, 0] * 1e3
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    m = (t > 40) & (t < 200)
    ax.plot(t[m], a[m, 1], color=C["vin"], lw=0.6, label="输入 1 kHz 正弦")
    ax.plot(t[m], a[m, 2], **LSkey("fb"), label="单二极管 + C + 放电电阻")
    ax.plot(t[m], a[m, 3], **LSkey("vout"), label="精密峰值检波（二极管在运放环内）")
    fs.ref_v(ax, 60, "60 ms 输入降到 0.5 V")
    w1 = (t > 58) & (t < 60); w2 = (t > 198) & (t < 200)
    i1 = np.where(w1)[0][np.argmax(a[w1, 3])]; i2 = np.where(w2)[0][np.argmax(a[w2, 3])]
    fs.mark(ax, t[i1], a[i1, 2], "{:.2f}", " V", dy=-0.18)
    fs.mark(ax, t[i1], a[i1, 3], "{:.2f}", " V", dy=0.12)
    fs.mark(ax, t[i2], a[i2, 2], "{:.2f}", " V", dx=-12, dy=-0.15)
    fs.mark(ax, t[i2], a[i2, 3], "{:.2f}", " V", dx=-12, dy=0.12)
    fs.axlabels(ax, "时间", "ms", "电压", "V")
    ax.set_ylim(-1.1, 1.45)
    ax.legend(loc="lower right", fontsize=7.5, ncol=1)
    fs.save(fig, P, "35_p2_4_peak.png")


def p2_5_digital_agc(S):
    """图 35-p2-5：数字 AGC 演示（Python 模拟）。上：输入；中：档位；下：ADC 看到的输出与两条门槛。"""
    t, v = S.demo_profile()
    ks, vo, est = S.digital_agc(v)
    fig, axs = plt.subplots(3, 1, figsize=(7, 5.0), sharex=True)
    axs[0].semilogy(t, v * 1e3, **LSkey("vin"))
    axs[0].set_ylabel("输入 / mV")
    axs[1].step(t, ks, where="post", color=C["third"], lw=1.4)
    axs[1].set_yticks(range(6), [f"X{i}" for i in range(6)], fontsize=8)
    axs[1].set_ylabel("档位")
    axs[2].plot(t, vo, **LSkey("vout"))
    for y, txt in ((S.DOWN * S.FS, "90 %：降档"), (S.UP * S.FS, "30 %：升档")):
        fs.ref_h(axs[2], y, txt)
    axs[2].set_ylim(0, 3.4)
    fs.axlabels(axs[2], "时间", "s", "放大后", "V")
    i7 = np.argmax(t >= 7)
    axs[2].annotate("7 s 输入突降：\n每 20 ms 升一档", xy=(7.05, vo[i7]), xytext=(7.6, 2.0), fontsize=8,
                    arrowprops=dict(arrowstyle="->", lw=0.8))
    fs.save(fig, P, "35_p2_5_digital_agc.png")
    print(f"[图 35-p2-5] 换档 {int(np.sum(np.diff(ks) != 0))} 次")


# ======================================================================
# page3
# ======================================================================
def p3_1_bandwidth():
    a = run_spice("35", "ac.cir", ["mag(v(oa))", "mag(v(ob))", "mag(v(oc))"])
    f = a[:, 0]
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for col, sty, name in ((1, "vout", "X5 理想开关 G=101"), (2, "fb", "X5 串 470 Ω G≈69"), (3, "vin", "X0 G≈2")):
        g = 20 * np.log10(a[:, col])
        ax.semilogx(f, g, **LSkey(sty), label=name)
        g0 = g[np.argmin(np.abs(f - 100))]
        i = np.argmax(g < g0 - 3.0103)                      # 在 i−1 与 i 两点之间按 lg f 线性插值
        f3 = 10 ** np.interp(g0 - 3.0103, [g[i], g[i - 1]], [np.log10(f[i]), np.log10(f[i - 1])])
        ax.plot(f3, g0 - 3.0103, "o", color="k", ms=4)
        ax.annotate(f"{f3/1e3:.3g} kHz", (f3, g0 - 3.0103), xytext=(-62, 6) if col == 1 else ((8, -16) if col == 2 else (6, 6)),
                    textcoords="offset points", fontsize=8.5)
        print(f"[图 35-p3-1] {name}: 低频 {g0:.2f} dB，−3 dB 点 {f3:.4g} Hz")
    fs.axlabels(ax, "频率", "Hz", "增益", "dB")
    ax.set_ylim(-5, 48)
    ax.legend(loc="lower left", fontsize=8)
    fs.save(fig, P, "35_p3_1_bandwidth.png")


def p3_2_hunting(S):
    vin = np.full(14, 0.6)
    k1, o1, _ = S.digital_agc(vin, up=0.45)
    k2, o2, _ = S.digital_agc(vin)
    fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"], sharey=True)
    for ax, o, k, ttl in ((axs[0], o1, k1, "升档门槛 45 %：来回跳"), (axs[1], o2, k2, "升档门槛 30 %：稳住")):
        n = np.arange(len(o))
        ax.step(n, o, where="post", color=C["vout"], lw=1.6)
        for i in n:
            ax.text(i + 0.5, o[i] + 0.12, f"X{k[i]}", ha="center", fontsize=7.5)
        fs.ref_h(ax, S.DOWN * S.FS, "90 %")
        ylo = 0.45 * S.FS if ax is axs[0] else S.UP * S.FS
        fs.ref_h(ax, ylo)
        ax.text(1.01, ylo, "45 %" if ax is axs[0] else "30 %", transform=ax.get_yaxis_transform(),
                ha="left", va="center", fontsize=9, color="0.3", clip_on=False)   # 下门槛的标签写在坐标框右外侧，避开 X0 标签
        ax.set_title(ttl, fontsize=10)
        ax.set_xticks(range(0, 14, 2))
        fs.axlabels(ax, "循环次数", None, "放大后" if ax is axs[0] else None, "V" if ax is axs[0] else None)
    axs[0].set_ylim(0, 3.6)
    fs.save(fig, P, "35_p3_2_hunting.png")


def p3_3_agc_speed(S):
    """图 35-p3-3：模拟 AGC 三种积分时间常数。上：每个周期的输出峰值；下：增益（dB）。"""
    fig, axs = plt.subplots(2, 1, figsize=(7, 4.8), sharex=True)
    for ti, sty in zip(S.TAUS, ("vin", "vout", "fb")):
        t, x, y, g, dd = S.analog_agc(ti)
        ts, rp, first = S.agc_metrics(t, y, g)
        per = int(round(1e-3 / (t[1] - t[0])))
        m = len(y) // per
        pk = np.abs(y[: m * per]).reshape(m, per).max(axis=1)
        tc = t[: m * per: per] * 1e3
        lab = f"τ_i = {ti*1e3:g} ms：{ts*1e3:.0f} ms 回到 ±1 dB，稳态增益起伏 {rp:.2f} dB"
        axs[0].plot(tc, pk, **LSkey(sty), label=lab)
        axs[1].plot(t * 1e3, g, **LSkey(sty))
        print(f"[图 35-p3-3] τ={ti*1e3:g} ms 首周期峰值 {first:.2f} V，±1 dB 用 {ts*1e3:.0f} ms，起伏 {rp:.2f} dB")
    axs[0].axhspan(10 ** (-1 / 20), 10 ** (1 / 20), color=C["hi"], alpha=0.35, lw=0)
    axs[0].set_yscale("log"); axs[0].set_ylim(0.01, 12)
    axs[0].set_ylabel("输出峰值 / V")
    axs[0].legend(loc="lower right", fontsize=7.5)
    for x0, txt in ((100, "输入 ×10"), (300, "输入 ÷10")):
        for ax in axs:
            ax.axvline(x0, color="0.5", ls=":", lw=0.9)
        axs[0].text(x0 + 3, 7, txt, fontsize=8)
    axs[0].text(4, 0.02, "0 ms 的冲高：仿真从 40 dB 起步，不看它", fontsize=7.5, color="0.35")
    fs.axlabels(axs[1], "时间", "ms", "增益", "dB")
    fs.save(fig, P, "35_p3_3_agc_speed.png")


# ======================================================================
# page4：面包板与实验原理图
# ======================================================================
def bb35():
    """35 page4：LM358 同相放大 + CD4051 选 R_g，Arduino 供 5 V 并选档、读 A0。"""
    bb = Breadboard(ncol=32, rails=dict(tp=("+5 V", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"), bn=("（不用）", "gnd")),
                    figsize=(11, 6.6))
    bb.ax.set_ylim(-6.4, 14.6)
    HOP_T = [BB_RAIL_Y["tn"] - 0.32]
    HOP_TT = [BB_RAIL_Y["tn"] - 0.32, BB_RAIL_Y["tp"] + 0.32]
    HOP_B = [BB_RAIL_Y["bp"] + 0.32, BB_RAIL_Y["bn"] - 0.32]
    bb.wire(bb.ext((-2.4, 11.4), "Arduino 5V", "pos"), "tp1", "pos")
    bb.wire(bb.ext((-2.4, 10.4), "Arduino GND", "gnd"), "tn1", "gnd")
    bb.wire("tn31", "bp31", "gnd")
    # LM358
    bb.dip8("U1", 4, "LM358")
    bb.wire("a4", "tp4", "pos", hops=HOP_T)                 # 8 脚 V+
    bb.two("C1", "b4", "tn3", "C", "100n", lpos=(-1.0, 0.0))
    bb.wire("c5", "c6", "sig")                              # 7–6 脚相连（空闲半边接成跟随器）
    bb.wire("a7", "tn7", "gnd")                             # 5 脚接地
    bb.wire("j7", "bp7", "gnd")                             # 4 脚 GND
    bb.two("RF", "g4", "g9", "R", "Rf 100k", lpos=(0, 0.62))
    bb.wire("h5", "h9", "sig", bend=0.8)                    # 2 脚（反相端）延到第 9 列（弧线向上拱，给输入线让出 h、i 行之间）
    bb.two("RO", "i4", "i1", "R", "1k", lpos=(0, -0.62))
    bb.wire("j1", bb.ext((1.0, -5.6), "→ Arduino A0", "sig", dx=0.45, ha="left"), "sig", hops=HOP_B)
    # 输入：5 V → 15k → 电位器 → 地；滑动端直接接 3 脚（或经 ÷11）
    bb.wire("a10", "tp10", "pos", hops=HOP_T)
    bb.two("RA", "b10", "b12", "R", "15k", lpos=(0, -0.62))
    bb.multi("RP", {"1": "c12", "W": "c13", "3": "c14"}, "10k 电位器", w=2.6, h=0.55, at=(13.0, 7.5))
    bb.wire("a14", "tn14", "gnd")
    bb.two("R10", "b13", "b17", "R", "10k", lpos=(0, -0.62))
    bb.two("R1", "a17", "tn17", "R", "1k", lpos=(0.35, 0))
    bb.wire("d13", "h6", "sig", via=[(13.5, 6.0), (13.5, 0.5), (6.0, 0.5)])   # 走 h、i 两行之间，不压 h9
    # 选做（「没有示波器怎么办」交流验证）：10 µF + 端 c17、− 端 c18；a18 跳线给信号源的信号夹
    bb.two("C3", "c17", "c18", "CE", None)
    bb.wire("a18", bb.ext((18.0, 13.7), "选做：信号源信号夹夹这根线 →\n（信号源的地夹接 0 V 轨）", "sig", dx=-0.45), "sig", hops=HOP_TT)
    # CD4051：col 20–27
    bb.dip16("U2", 20, "CD4051")
    bb.wire("a20", "tp20", "pos", hops=HOP_T)               # 16 脚 VDD
    bb.two("C2", "b20", "tn19", "C", "100n", lpos=(-1.0, 0.0))
    for col, name, r in ((21, "RG2", "11k"), (22, "RG1", "24k"), (23, "RG0", "100k")):
        bb.two(name, f"a{col}", f"tn{col}", "R", None)
    bb.two("RG3", "a24", "tn25", "R", None)
    for col, pin in ((25, "D2"), (26, "D3"), (27, "D4")):
        bb.wire(f"b{col}", bb.ext((col + 0.0, 13.6 + 0.0 * col), "", "sig"), "sig", via=[(col + 0.5, 8.0), (col + 0.5, 13.1), (col, 13.1)] if False else (), hops=HOP_TT)
    bb.ax.text(28.0, 13.6, "→ Arduino D2 D3 D4\n（A B C 选档）", fontsize=7.5, color=BB_WIRE["sig"], va="center")
    bb.two("RG4", "j20", "bp20", "R", None)
    bb.two("RG5", "j24", "bp23", "R", None)
    bb.wire("i22", "i9", "sig", via=[(22, -0.5), (9, -0.5)])  # 3 脚 COM → 反相端
    for col in (25, 26, 27):
        bb.wire(f"j{col}", f"bp{col}", "gnd")               # 6 INH、7 VEE、8 VSS
    bb.note(19.0, 12.7, "R_g（上排）：X0 23 列 100k、\nX1 22 列 24k、X2 21 列 11k、\nX3 24 列 5.1k（落到 25 列地轨）", va="center", fontsize=7.5)
    bb.note(14.2, 5.1, "选做 10µF\n+ c17  − c18", va="center", fontsize=7, ha="left")
    bb.note(13.0, -5.0, "R_g（下排）：X4 20 列 2k、X5 24 列 1k（落到 23 列地轨）", va="center", fontsize=7.5)
    bb.note(-7.3, 6.2, "要 ÷11 小信号：把绿线\n上端从 d13 改插 d17", fontsize=7.5, va="center")
    # 连接检查
    assert bb.connected("U1.8", "tp1") and bb.connected("U2.16", "tp1") and bb.connected("RA.1", "tp1")
    assert bb.connected("U1.4", "tn1") and bb.connected("U2.8", "tn1") and bb.connected("U2.7", "tn1") and bb.connected("U2.6", "tn1")
    assert bb.connected("U1.5", "tn1") and bb.connected("U1.6", "U1.7")
    assert bb.connected("RF.1", "U1.1") and bb.connected("RF.2", "U1.2") and bb.connected("U2.3", "U1.2")
    assert bb.connected("RO.1", "U1.1") and not bb.connected("U1.1", "U1.2")
    assert bb.connected("RP.1", "RA.2") and bb.connected("RP.3", "tn1") and bb.connected("RP.W", "U1.3")
    assert bb.connected("R10.1", "RP.W") and bb.connected("R10.2", "R1.1") and bb.connected("R1.2", "tn1")
    for name, pin in (("RG0", "13"), ("RG1", "14"), ("RG2", "15"), ("RG3", "12"), ("RG4", "1"), ("RG5", "5")):
        a = f"{name}.1" if name not in ("RG4", "RG5") else f"{name}.1"
        assert bb.connected(a, f"U2.{pin}") and bb.connected(f"{name}.2", "tn1"), name
    assert not bb.connected("U2.11", "U2.10") and not bb.connected("U2.3", "tn1") and not bb.connected("tp1", "tn1")
    assert not bb.connected("U1.3", "U1.2")
    assert bb.connected("C3.1", "R10.2", "R1.1") and not bb.connected("C3.2", "C3.1") and not bb.connected("C3.2", "tn1")
    assert bb.pins["C3.1"] != "d17" and "d17" not in bb.used   # d17 留给输入线（第 6～8 步改插）
    bb.probe("j4", "①输出", dx=-0.3, dy=-0.95, ha="right")
    bb.probe("j9", "②反相端", dx=0.3, dy=-0.95)
    bb.probe("h24", "③X5 脚", dx=0.3, dy=0.25)
    bb.probe("h6", "④同相端", dx=-0.3, dy=0.15, ha="right")
    bb.legend(("pos", "gnd", "sig"), y=0.02)
    print(f"35 p4 面包板：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def p4_2_schem_lab(name="35_p4_2_schem_lab.png"):
    import lab_schem as L
    with schem.drawing(fontsize=11) as d:
        # 输入网络
        x0, ytop = 0.0, 7.0
        d += elm.Vdd().at((x0, ytop)).label("+5 V")
        d += elm.Resistor().at((x0, ytop)).to((x0, ytop - 2.4))
        L.lab(d, (x0 + 0.45, ytop - 1.2), "RA 15k")
        L.colnote(d, (x0 - 0.6, ytop - 1.2), "b10→b12", "left", ofst=0.0)
        d += (pot := elm.Potentiometer().at((x0, ytop - 2.4)).to((x0, ytop - 5.0)))
        d += elm.Ground().at((x0, ytop - 5.0))
        L.lab(d, (x0 - 0.5, ytop - 3.7), "RP 10k\n第 12–14 列", ha="right", fs_=9.5)
        tp = pot.absanchors["tap"]
        xw = tp[0] + 1.4
        d += elm.Line().at(tp).to((xw, tp[1]))
        d += elm.Dot().at((xw, tp[1]))
        L.colnote(d, (xw, tp[1] + 0.25), "滑动端 d13", "top", ofst=0.0)
        # ÷11 支路
        d += elm.Resistor().at((xw, tp[1])).to((xw, tp[1] - 2.2))
        L.lab(d, (xw + 0.45, tp[1] - 1.1), "R10 10k", fs_=10)
        d += elm.Dot().at((xw, tp[1] - 2.2))
        d += elm.Resistor().at((xw, tp[1] - 2.2)).to((xw, tp[1] - 4.0))
        d += elm.Ground().at((xw, tp[1] - 4.0))
        L.lab(d, (xw + 0.45, tp[1] - 3.1), "R1 1k", fs_=10)
        L.colnote(d, (xw - 0.25, tp[1] - 2.2), "第 17 列（÷11）", "left", ofst=0.0)
        # 运放
        xop = 6.3
        op = elm.Opamp(leads=True).theta(0).flip().anchor("in2").at((xop, tp[1]))
        d += op
        pp, pm, po = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
        d += elm.Line().at((xw, tp[1])).to(pp).color(C["fb"]).linewidth(2.0)
        L.lab(d, ((xw + pp[0]) / 2 - 0.2, tp[1] + 0.35), "绿线 d13→h6", ha="center", fs_=8.5, color=C["fb"])
        L.probe(d, (pp[0] - 0.35, pp[1]), "④", dx=0.0, dy=-0.9)
        L.lab(d, (pp[0] - 0.1, pp[1] + 0.25), "3", fs_=8.5)
        L.lab(d, (pm[0] - 0.1, pm[1] - 0.25), "2", fs_=8.5)
        L.lab(d, (po[0] - 0.4, po[1] + 0.3), "1", fs_=8.5)
        L.lab(d, (xop + 1.0, tp[1] + 1.7), "LM358（U1）\n8 脚 +5 V，4 脚地", ha="center", fs_=9)
        xo = po[0] + 0.9
        d += elm.Line().at(po).to((xo, po[1]))
        d += elm.Dot().at((xo, po[1]))
        L.probe(d, (xo, po[1]), "①", dx=0.0, dy=0.9)
        d += elm.Resistor().at((xo, po[1])).to((xo + 2.4, po[1]))
        L.lab(d, (xo + 1.2, po[1] + 0.5), "RO 1k", ha="center", fs_=10)
        d += elm.Dot(open=True).at((xo + 2.4, po[1])).label("Arduino A0", "right")
        # 反馈
        xm = pm[0] - 0.5
        yf = pm[1] - 1.6
        d += elm.Line().at(pm).to((xm, pm[1]))
        d += elm.Line().at((xm, pm[1])).to((xm, yf))
        d += elm.Dot().at((xm, yf))
        d += elm.Resistor().at((xm, yf)).to((xo, yf))
        L.lab(d, ((xm + xo) / 2 + 0.6, yf + 0.5), "RF 100k（g4→g9）", ha="center", fs_=10)
        d += elm.Line().at((xo, yf)).to((xo, po[1]))
        L.probe(d, (xm, yf), "②", dx=-0.9, dy=0.0)
        L.colnote(d, (xm - 0.2, pm[1] - 0.6), "第 9 列", "left", ofst=0.0)
        # CD4051 方框
        mod = schem.module("CD4051（U2）", left=("3 COM", "6 INH", "7 VEE", "8 VSS"),
                           right=("13 X0", "14 X1", "15 X2", "12 X3", "1 X4", "5 X5"), w=4.0)
        d += mod.theta(0).anchor("3 COM").at((xm, yf - 3.0))
        pc = mod.absanchors["3 COM"]
        d += elm.Line().at((xm, yf)).to(pc)
        L.colnote(d, (xm - 0.15, (yf + pc[1]) / 2), "绿线 i22→i9", "left", ofst=0.0)
        for nm in ("6 INH", "7 VEE", "8 VSS"):
            q = mod.absanchors[nm]
            d += elm.Line().at(q).to((q[0] - 0.6, q[1]))
            d += elm.Ground().at((q[0] - 0.6, q[1]))
        rg = dict(X0="100k", X1="24k", X2="11k", X3="5.1k", X4="2k", X5="1k")
        for nm in ("13 X0", "14 X1", "15 X2", "12 X3", "1 X4", "5 X5"):
            q = mod.absanchors[nm]
            d += elm.Resistor().at(q).to((q[0] + 2.6, q[1])).scale(0.7)
            d += elm.Ground().at((q[0] + 2.6, q[1])).theta(0)
            L.lab(d, (q[0] + 1.3, q[1] + 0.35), "$R_g$ " + rg[nm.split()[1]], ha="center", fs_=8.5)
        q5 = mod.absanchors["5 X5"]
        L.probe(d, (q5[0] + 0.4, q5[1]), "③", dx=0.0, dy=-0.85)
        top = mod.absanchors["3 COM"]
        L.note(d, (pc[0] - 1.5, mod.absanchors["13 X0"][1] - 6.8),
               "16 脚 VDD → +5 V；11 A / 10 B / 9 C ← Arduino D2 / D3 / D4\n（没有 Arduino：三根线分别插到 +5 V 或地，手动选档）")
        # 第 6–9 步的另两种输入（灰色虚线：换插，不是同时接）
        GR = "#888888"
        xa = xw + 1.4
        yd = tp[1] - 2.2
        d += elm.Line().at((xw, yd)).to((xa, yd)).color(GR).linestyle(":").linewidth(1.6)
        d += elm.Line().at((xa, yd)).to((xa, pp[1])).color(GR).linestyle(":").linewidth(1.6)
        L.lab(d, (xa + 0.2, yd - 0.15), "第 6–8 步\n上端改插 d17", fs_=8.5, color=GR)
        L.lab(d, (xa, tp[1] + 1.05), "第 9 步：上端改插地轨（0 V）", ha="center", fs_=8.5, color=GR)
        # Arduino 供电
        L.note(d, (x0 - 2.0, ytop + 1.6), "电源：Arduino 5V → 上、下 +5 V 轨；Arduino GND → 0 V 轨（第 30 列把两条 0 V 轨连起来）")
        # 两只去耦电容
        xc0 = xo + 5.4
        for k, (nm, where) in enumerate((("C1 100 nF", "LM358 8 脚旁\nb4→0 V 轨"), ("C2 100 nF", "CD4051 16 脚旁\nb20→0 V 轨"))):
            xc = xc0 + 2.6 * k
            d += elm.Vdd().at((xc, ytop)).label("+5 V")
            d += elm.Capacitor().at((xc, ytop)).to((xc, ytop - 1.8))
            d += elm.Ground().at((xc, ytop - 1.8))
            L.lab(d, (xc + 0.35, ytop - 0.9), nm, fs_=9)
            L.lab(d, (xc, ytop - 2.9), where, ha="center", fs_=8.5, color="#555555")
        # 不用的 B 组接成跟随器
        L._follower_b(d, xc0 + 0.6, tp[1] - 3.6, "c5–c6（7 脚接 6 脚）", "a7（5 脚）接地")
        schem.save_schem(d, P, name)


# ======================================================================
# 教师 / 学生审阅后补的图（2026-10-27）
# ======================================================================
CD4051_PINS = {1: "X4", 2: "X6", 3: "COM", 4: "X7", 5: "X5", 6: "INH", 7: "VEE", 8: "VSS",
               9: "C", 10: "B", 11: "A", 12: "X3", 13: "X0", 14: "X1", 15: "X2", 16: "VDD"}


def p2_pins():
    """CD4051 引脚图（DIP-16 俯视，缺口朝上），按本节接法着色。"""
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.set_xlim(-6.2, 6.2); ax.set_ylim(-1.6, 9.4); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(mpatches.FancyBboxPatch((-1.3, 0), 2.6, 8.6, boxstyle="round,pad=0.05", fc="#333333", ec="k"))
    ax.add_patch(mpatches.Wedge((0, 8.65), 0.4, 180, 360, fc="#888888"))
    ax.text(0, 4.3, "CD4051", color="white", rotation=90, ha="center", va="center", fontsize=11)
    def col(nm):
        if nm in ("X0", "X1", "X2", "X3", "X4", "X5"): return C["vout"], "接 $R_g$"
        if nm in ("X6", "X7"): return "0.55", "本节不用"
        if nm == "COM": return C["fb"], "接运放反相端"
        if nm in ("A", "B", "C"): return C["vin"], "选档线"
        if nm == "VDD": return C["bad"], "+5 V"
        return "#000000", "接 0 V"
    for k in range(8):
        y = 8.0 - 1.05 * k
        for pin, side in ((1 + k, -1), (16 - k, 1)):
            nm = CD4051_PINS[pin]; c, why = col(nm)
            x0 = side * 1.3
            ax.add_patch(mpatches.Rectangle((x0 if side > 0 else x0 - 0.45, y - 0.18), 0.45, 0.36, fc="#bbbbbb", ec="0.3"))
            ax.text(side * 1.0, y, str(pin), color="white", ha="center", va="center", fontsize=8.5)
            ax.text(side * 2.0, y, nm, color=c, ha="left" if side > 0 else "right", va="center", fontsize=11, fontweight="bold")
            ax.text(side * 3.2, y, why, color=c, ha="left" if side > 0 else "right", va="center", fontsize=8.5)
    ax.text(0, -0.7, "俯视，缺口朝上，1 脚在左上；插到面包板上缺口朝左时，1 脚在左下（f 行）", ha="center", fontsize=8.5)
    ax.text(0, -1.3, "C、B、A 组成二进制数（C 最高位）：101 = 5 → COM 接通 X5", ha="center", fontsize=8.5)
    fs.save(fig, P, "35_p2_0_pins.png")


def p2_peak_schem():
    """两种峰值检波的原理图（与 spice/35/t_peak.cir 相同）。"""
    with schem.drawing(fontsize=11) as d:
        # 左：单二极管
        d += elm.Dot(open=True).at((0, 0)).label("$V_{in}$", "left")
        d += elm.Diode().at((0, 0)).to((3.0, 0)).label("1N4148", "top")
        d += elm.Dot().at((3.0, 0))
        d += elm.Line().at((3.0, 0)).to((5.6, 0))
        d += elm.Dot(open=True).at((5.6, 0)).label("$V_{pk}$", "right")
        d += elm.Capacitor().at((3.0, 0)).to((3.0, -2.4))
        d += elm.Label().at((2.6, -1.2)).label("1 µF", halign="right", fontsize=10)
        d += elm.Dot().at((4.6, 0))
        d += elm.Resistor().at((4.6, 0)).to((4.6, -2.4))
        d += elm.Label().at((5.0, -1.2)).label("100 kΩ", halign="left", fontsize=10)
        d += elm.Line().at((3.0, -2.4)).to((4.6, -2.4))
        d += elm.Ground().at((3.8, -2.4))
        d += elm.Label().at((2.8, 2.0)).label("① 单二极管检波：输出少 0.5～0.7 V", fontsize=11)
        # 右：精密峰值检波
        x0 = 10.0
        op = elm.Opamp(leads=True).theta(0).flip().anchor("in2").at((x0, 0))
        d += op
        pp, pm, po = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
        d += elm.Line().at(pp).to((x0 - 1.0, pp[1]))
        d += elm.Dot(open=True).at((x0 - 1.0, pp[1])).label("$V_{in}$", "left")
        xd = po[0] + 2.6
        d += elm.Diode().at(po).to((xd, po[1])).label("1N4148", "top")
        d += elm.Dot().at((xd, po[1]))
        d += elm.Line().at((xd, po[1])).to((xd + 3.4, po[1]))
        d += elm.Dot(open=True).at((xd + 3.4, po[1])).label("$V_{pk}$", "right")
        xc, xr = xd + 1.4, xd + 2.6
        d += elm.Dot().at((xc, po[1])); d += elm.Dot().at((xr, po[1]))
        d += elm.Capacitor().at((xc, po[1])).to((xc, po[1] - 3.6))
        d += elm.Label().at((xc - 0.4, po[1] - 1.8)).label("1 µF", halign="right", fontsize=10)
        d += elm.Resistor().at((xr, po[1])).to((xr, po[1] - 3.6))
        d += elm.Label().at((xr + 0.4, po[1] - 1.8)).label("100 kΩ", halign="left", fontsize=10)
        d += elm.Line().at((xc, po[1] - 3.6)).to((xr, po[1] - 3.6))
        d += elm.Ground().at(((xc + xr) / 2, po[1] - 3.6))
        yf = pm[1] - 1.2
        xf = xd + 0.5
        for a, b in (((xf, po[1]), (xf, yf)), ((xf, yf), (pm[0] - 0.4, yf)),
                     ((pm[0] - 0.4, yf), (pm[0] - 0.4, pm[1])), ((pm[0] - 0.4, pm[1]), pm)):
            d += elm.Line().at(a).to(b).color(C["vout"]).linewidth(2.0)
        d += elm.Dot().at((xf, po[1]))
        d += elm.Label().at(((pm[0] + xf) / 2, yf - 0.4)).label("反馈从二极管后面取", fontsize=10, color=C["vout"])
        d += elm.Label().at((x0 + 2.6, 2.0)).label("② 精密峰值检波：二极管在运放环内", fontsize=11)
        schem.save_schem(d, P, "35_p2_peak_schem.png")


def agc_loop():
    """模拟 AGC 环框图（page1 / page2 / page3 共用）。"""
    fig, ax = fs.diagram(9.6, 3.6)
    ax.set_xlim(0, 9.6); ax.set_ylim(0, 3.6)
    ax.annotate("", xy=(1.55, 2.7), xytext=(0.2, 2.7), arrowprops=dict(arrowstyle="-|>", lw=1.3, color=C["vin"]))
    ax.text(0.2, 2.95, "$V_{in}$", color=C["vin"], fontsize=10)
    v = fs.box(ax, 2.4, 2.7, "VGA\n增益随 $V_{GAIN}$ 变", w=1.7, h=0.9, fc=C["hi"])
    ax.annotate("", xy=(9.3, 2.7), xytext=(3.25, 2.7), arrowprops=dict(arrowstyle="-|>", lw=1.6, color=C["vout"]))
    ax.text(8.6, 2.95, "$V_{out}$", color=C["vout"], fontsize=10)
    ax.plot([7.6, 7.6], [2.7, 1.25], color=C["vout"], lw=1.3); ax.plot(7.6, 2.7, "o", color=C["vout"], ms=4)
    pk = fs.box(ax, 7.6, 0.85, "精密峰值检波\n放电 $\\tau_d$", w=1.8, h=0.8)
    ax.add_patch(mpatches.Circle((5.4, 0.85), 0.3, fc="white", ec="k", lw=1.2))
    ax.text(5.4, 0.85, "Σ", ha="center", va="center", fontsize=11)
    ax.annotate("", xy=(5.72, 0.85), xytext=(6.7, 0.85), arrowprops=dict(arrowstyle="-|>", lw=1.2))
    ax.text(5.85, 0.55, "−", fontsize=13, ha="center")
    ax.text(6.2, 1.02, "峰值", fontsize=8.5, ha="center")
    ax.annotate("", xy=(5.4, 1.17), xytext=(5.4, 1.9), arrowprops=dict(arrowstyle="-|>", lw=1.2))
    ax.text(5.55, 1.55, "+  目标 1 V", fontsize=9)
    it = fs.box(ax, 3.4, 0.85, "积分器 $\\tau_i$\n（14 节）", w=1.6, h=0.8)
    ax.annotate("", xy=(4.22, 0.85), xytext=(5.08, 0.85), arrowprops=dict(arrowstyle="-|>", lw=1.2))
    ax.text(4.65, 0.5, "误差 e", fontsize=8.5, ha="center")
    ax.plot([2.58, 2.4], [0.85, 0.85], color=C["third"], lw=1.6, ls="-.")
    ax.annotate("", xy=(2.4, 2.22), xytext=(2.4, 0.85), arrowprops=dict(arrowstyle="-|>", lw=1.6, color=C["third"], ls="-."))
    ax.text(1.0, 1.5, "$V_{GAIN}$\n回到 VGA", color=C["third"], fontsize=9.5, ha="center")
    ax.text(4.8, 3.35, "输出大 → 峰值大 → e 变负 → 积分器把 $V_{GAIN}$ 往下拧 → 增益降（负反馈）", ha="center", fontsize=9)
    fs.save(fig, P, "35_agc_loop.png")


def p4_3_ac_inject():
    """图 35-p4-3：「没有示波器怎么办」里的交流耦合注入：直流偏置（滑动端 → ÷11）+ 信号源经 10 µF 叠到 d17。"""
    import lab_schem as L
    vw, r10, r1, c, f = 0.22, 10e3, 1e3, 10e-6, 50.0
    vdc = vw * r1 / (r10 + r1)
    rth = r10 * r1 / (r10 + r1)
    xc = 1 / (2 * np.pi * f * c)
    with schem.drawing(fontsize=11) as d:
        x0, ytop = 0.0, 7.0
        d += elm.Vdd().at((x0, ytop)).label("+5 V")
        d += elm.Resistor().at((x0, ytop)).to((x0, ytop - 2.4))
        L.lab(d, (x0 + 0.45, ytop - 1.2), "RA 15k（b10→b12）", fs_=10)
        d += (pot := elm.Potentiometer().at((x0, ytop - 2.4)).to((x0, ytop - 5.0)))
        d += elm.Ground().at((x0, ytop - 5.0))
        L.lab(d, (x0 - 0.5, ytop - 3.7), "RP 10k", ha="right", fs_=10)
        tp = pot.absanchors["tap"]
        xw = tp[0] + 1.4
        d += elm.Line().at(tp).to((xw, tp[1]))
        d += elm.Dot().at((xw, tp[1]))
        L.lab(d, (xw + 0.2, tp[1] + 0.35), f"滑动端 d13：调到约 {vw:.2f} V", fs_=9.5)
        d += elm.Resistor().at((xw, tp[1])).to((xw, tp[1] - 2.2))
        L.lab(d, (xw + 0.45, tp[1] - 1.1), "R10 10k", fs_=10)
        yn = tp[1] - 2.2
        d += elm.Dot().at((xw, yn))
        d += elm.Resistor().at((xw, yn)).to((xw, yn - 2.0))
        d += elm.Ground().at((xw, yn - 2.0))
        L.lab(d, (xw + 0.45, yn - 1.0), "R1 1k", fs_=10)
        # 去运放 3 脚
        xo = xw + 5.6
        d += elm.Line().at((xw, yn)).to((xo, yn))
        d += elm.Dot(open=True).at((xo, yn)).label("输入线 → LM358 3 脚（④）\n档位放在 X5", "right")
        L.lab(d, (xw + 0.15, yn + 0.35), f"d17：直流约 {vdc*1e3:.0f} mV", fs_=9.5, color=C["fb"])
        # 交流注入支路
        xs = xw + 3.0
        d += elm.Dot().at((xs, yn))
        d += elm.Capacitor(polar=True).at((xs, yn)).down().length(2.4)
        L.lab(d, (xs + 0.55, yn - 1.2), "10 µF\n+ 端 c17（第 17 列）\n− 端 c18", fs_=10)
        d += elm.SourceSin().at((xs, yn - 2.4)).down().length(2.0)
        d += elm.Ground().at((xs, yn - 4.4))
        L.lab(d, (xs + 0.6, yn - 3.6), "信号源 50～200 Hz（信号夹夹 a18 跳线）\n从最小慢慢调到④交流约 7 mV（有效值）", fs_=9.5, color=C["vin"])
        L.note(d, (x0 - 1.0, yn - 5.6), f"d17 对交流的等效电阻 ≈ 10k∥1k = {rth:.0f} Ω；10 µF 在 50 Hz 的容抗约 {xc:.0f} Ω，"
                                        "所以信号源要比④的读数大一些，按④的读数调。")
        L.note(d, (x0 - 1.0, yn - 6.2), "信号源的地接面包板 0 V 轨；先断电接好（幅度旋到最小），通电后再从最小调幅度；拆之前先调回最小、断电。")
        schem.save_schem(d, P, "35_p4_3_ac_inject.png")
    print(f"[图 35-p4-3] d17 直流 {vdc*1e3:.1f} mV，等效电阻 {rth:.0f} Ω，10 µF@50 Hz 容抗 {xc:.0f} Ω")


def p1_5_agc_schem(fname="35_p1_5_agc_schem.png"):
    """图 35-p1-5（page2 同图另存为图 35-p2-9）：模拟 AGC 的简化原理图（与 code/35_sim.py analog_agc 的 τ_d = 20 ms、目标 1 V、τ_i = 5 ms 一致）。"""
    W = 2.0
    with schem.drawing(fontsize=11) as d:
        vga = schem.module("U3　VGA（例如 AD8331）", left=("IN", "GAIN"), right=("OUT",), w=3.4)
        d += vga.at((0, 0)).anchor("IN")
        a = vga.absanchors
        pin_in, pin_g, pin_o = a["IN"], a["GAIN"], a["OUT"]
        d += elm.Line().at(pin_in).to((pin_in[0] - 1.6, pin_in[1]))
        d += elm.Dot(open=True).at((pin_in[0] - 1.6, pin_in[1])).label("$V_{in}$", "left")
        xo = pin_o[0] + 1.6
        d += elm.Line().at(pin_o).to((xo + 2.4, pin_o[1]))
        d += elm.Dot().at((xo, pin_o[1]))
        d += elm.Dot(open=True).at((xo + 2.4, pin_o[1])).label("$V_{out}$", "right")
        # U1A 精密峰值检波（+ 在上）
        yA = pin_o[1] - 3.2
        op = elm.Opamp(leads=True).theta(0).flip().anchor("in2").at((xo, yA))
        d += op
        pp, pm, po = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
        d += elm.Line().at((xo, pin_o[1])).to(pp)
        d += elm.Label().at((pp[0] + 0.25, pp[1] + 0.3)).label("3", fontsize=9)
        d += elm.Label().at((pm[0] + 0.25, pm[1] - 0.3)).label("2", fontsize=9)
        d += elm.Label().at((po[0] - 0.3, po[1] + 0.3)).label("1", fontsize=9)
        d += elm.Label().at((op.center[0] - 0.4, op.center[1] + 1.5)).label("U1A（LM358）", fontsize=10)
        xd = po[0] + 2.4
        d += elm.Diode().at(po).to((xd, po[1])).label("D1 1N4148", "top")
        xk = xd + 5.8
        d += elm.Line().at((xd, po[1])).to((xk, po[1]))
        for x in (xd, xd + 1.6, xd + 3.4):
            d += elm.Dot().at((x, po[1]))
        xc, xr = xd + 1.6, xd + 3.4
        yb = po[1] - 3.0
        d += elm.Capacitor().at((xc, po[1])).to((xc, yb))
        d += elm.Label().at((xc + 0.35, (po[1] + yb) / 2)).label("$C_d$ 1 µF", halign="left", fontsize=10)
        d += elm.Resistor().at((xr, po[1])).to((xr, yb))
        d += elm.Label().at((xr + 0.35, (po[1] + yb) / 2)).label("$R_d$ 20 kΩ", halign="left", fontsize=10)
        d += elm.Line().at((xc, yb)).to((xr, yb))
        d += elm.Ground().at((xc, yb))
        d += elm.Label().at((xk - 0.2, po[1] + 0.45)).label("$V_{pk}$", fontsize=11)
        # 反馈：从二极管后面回到 2 脚
        yf = pm[1] - 1.0
        for u, v in (((xd, po[1]), (xd, yf)), ((xd, yf), (pm[0] - 0.4, yf)),
                     ((pm[0] - 0.4, yf), (pm[0] - 0.4, pm[1])), ((pm[0] - 0.4, pm[1]), pm)):
            d += elm.Line().at(u).to(v).color(C["vout"]).linewidth(W)
        # V_pk 往下、往左进积分器 U1B（运放朝左）
        yI = yb - 3.6
        d += elm.Line().at((xk, po[1])).to((xk, yI))
        xri = xk - 3.4
        d += elm.Resistor().at((xk, yI)).to((xri, yI)).label("$R_i$ 50 kΩ", "top")
        ob = elm.Opamp(leads=True).theta(180).flip().anchor("in1").at((xri - 0.9, yI))
        d += ob
        bm, bp, bo = ob.absanchors["in1"], ob.absanchors["in2"], ob.absanchors["out"]
        d += elm.Line().at((xri, yI)).to(bm)
        d += elm.Dot().at((xri - 0.45, yI))
        d += elm.Label().at((bm[0] - 0.25, bm[1] - 0.3)).label("6", fontsize=9)
        d += elm.Label().at((bp[0] - 0.25, bp[1] + 0.3)).label("5", fontsize=9)
        d += elm.Label().at((bo[0] + 0.3, bo[1] + 0.3)).label("7", fontsize=9)
        d += elm.Label().at((ob.center[0] + 0.3, ob.center[1] - 1.6)).label("U1B（同一片 LM358）", fontsize=10)
        # C_i 跨在 6 脚和 7 脚之间（上方）
        yc = yI + 1.8
        d += elm.Line().at((xri - 0.45, yI)).to((xri - 0.45, yc))
        d += elm.Capacitor().at((xri - 0.45, yc)).to((bo[0] - 0.6, yc)).label("$C_i$ 100 nF", "top")
        d += elm.Line().at((bo[0] - 0.6, yc)).to((bo[0] - 0.6, bo[1]))
        d += elm.Dot().at((bo[0] - 0.6, bo[1]))
        # 5 脚：目标 1 V（+5 V 经 40k/10k 分压）
        xt = bp[0] + 0.9
        d += elm.Line().at(bp).to((xt, bp[1]))
        d += elm.Dot().at((xt, bp[1]))
        d += elm.Resistor().at((xt, bp[1])).to((xt, bp[1] - 2.6))
        d += elm.Label().at((xt + 0.35, bp[1] - 1.3)).label("$R_b$ 10 kΩ", halign="left", fontsize=10)
        d += elm.Ground().at((xt, bp[1] - 2.6))
        d += elm.Line().at((xt, bp[1])).to((xt + 2.2, bp[1]))
        d += elm.Resistor().at((xt + 2.2, bp[1])).to((xt + 4.8, bp[1])).label("$R_a$ 40 kΩ", "bottom")
        d += elm.Label().at((xt + 5.4, bp[1])).label("+5 V", fontsize=10)
        d += elm.Label().at((xt + 1.1, bp[1] - 0.45)).label("$V_{TGT}$ = 1 V", fontsize=10, color=C["vout"])
        # 7 脚输出 V_GAIN 回到 VGA 的 GAIN 脚
        xg = pin_g[0] - 1.0
        for u, v in ((bo, (xg, bo[1])), ((xg, bo[1]), (xg, pin_g[1])), ((xg, pin_g[1]), pin_g)):
            d += elm.Line().at(u).to(v).color(C["vout"]).linewidth(W)
        d += elm.Label().at((xg - 0.3, (bo[1] + pin_g[1]) / 2)).label("$V_{GAIN}$", halign="right", fontsize=11, color=C["vout"])
        d += elm.Label().at((pin_o[0] - 1.7, pin_g[1] - 1.3)).label("GAIN 电压越高，增益越大", fontsize=9, color="#555555")
        d += elm.Label().at((xc - 0.6, yb - 0.5)).label("$τ_d$ = 1 µF × 20 kΩ = 20 ms", halign="right", fontsize=10)
        d += elm.Label().at(((xri + bo[0]) / 2 - 3.0, yI - 5.4)).label("$τ_i$ = 50 kΩ × 100 nF = 5 ms；LM358 8 脚接 +5 V、4 脚接地", fontsize=10)
        schem.save_schem(d, P, fname)


if __name__ == "__main__":
    if sys.argv[1:]:
        S = load_sim()
        for name in sys.argv[1:]:
            if name == "p1_3_series":
                p2_1_series(S, "35_p1_3_cd4051.png")
            elif name == "p3_5_schem":
                p4_2_schem_lab("35_p3_5_schem_lab.png")
            else:
                f = globals()[name]
                f(S) if name in ("p2_1_series", "p1_1_fixed_vs_auto", "p2_2_ron_error", "p2_5_digital_agc", "p3_2_hunting", "p3_3_agc_speed") else f()
        sys.exit(0)
    S = load_sim()
    p1_1_fixed_vs_auto(S)
    p1_2_blocks()
    p1_3_db()
    p2_1_series(S, "35_p1_3_cd4051.png")
    p1_5_agc_schem()
    p1_5_agc_schem("35_p2_9_agc_schem.png")
    p2_1_series(S)
    p2_2_ron_error(S)
    p2_3_kelvin()
    p2_4_peak()
    p2_5_digital_agc(S)
    p3_1_bandwidth()
    p3_2_hunting(S)
    p3_3_agc_speed(S)
    bb = bb35()
    fs.save(bb.fig, P, "35_p4_1_bb_pga.png")
    plt.close("all")
    p4_2_schem_lab()
    p4_2_schem_lab("35_p3_5_schem_lab.png")
    p2_pins()
    p2_peak_schem()
    agc_loop()
    p4_3_ac_inject()
    print("35_figs OK")
