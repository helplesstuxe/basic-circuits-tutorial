"""14 电压比较器：全部配图（图 14-p2-2 由 code/14_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/14_figs.py
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

N = "14"
_spec = importlib.util.spec_from_file_location("sim14", os.path.join(HERE, "..", "14_sim.py"))
sim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sim)
V_H, V_L = sim.thresholds()
print(f"[数值] V_ref {sim.VREF} V，R1 {sim.R1/1e3:.0f} kΩ，R2 {sim.R2/1e3:.0f} kΩ，R3 {sim.R3/1e3:.1f} kΩ"
      f" → V_H {V_H:.2f} V，V_L {V_L:.2f} V，回差 {V_H - V_L:.2f} V")


def vref_divider(d, op):
    """反相端：两只 10 kΩ 把 +5 V 分成 2.5 V。"""
    d += elm.Line().left().at(op.in1).length(0.75)
    d += elm.Line().up().length(1.5)
    d += elm.Line().left().length(1.0)
    d += (jr := elm.Dot().label("$V_{ref}$ 2.5 V", "left"))
    d += elm.Resistor().up().label("10 kΩ")
    d += elm.Vdd().label("+5 V")
    d += elm.Resistor().down().at(jr.center).label("10 kΩ")
    d += elm.Ground()


def output_pullup(d, op, start=1.5, r3="$R_3$ 2.2 kΩ\n上拉"):
    d += elm.Line().right().at(op.out).length(start)
    d += (o := elm.Dot())
    d += elm.Resistor().up().label(r3)
    d += elm.Vdd().label("+5 V")
    d += elm.Line().right().at(o.center).length(1.0)
    d += elm.Dot(open=True).label("$V_o$ → 单片机 / LED", "right")


# ---------- 图 14-p1-1 基本比较器 ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True).label("比较器\nLM393", loc="center", ofst=(-0.35, 0), fontsize=9))
    vref_divider(d, op)
    d += elm.Line().left().at(op.in2).length(0.75)
    d += elm.Line().down().length(1.5)
    d += elm.Line().left().length(2.5)
    d += elm.Dot(open=True).label("$V_{in}$ 传感器", "left")
    output_pullup(d, op)
save_schem(d, N, "14_p1_1_basic.png")

# ---------- 图 14-p1-2 单一门限 + 噪声 = 输出抖动 ----------
t, clean, vin = sim.make_input()
o1 = sim.comp_plain(vin)
win = (t > 3.5) & (t < 7.0)
n_win = sim.edges(o1[win])
print(f"[数值] 3.5–7.0 s 内普通比较器翻转 {n_win} 次（整段 {sim.edges(o1)} 次）")
assert n_win > 20
fig, (a0, a1) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True, gridspec_kw=dict(height_ratios=[1.5, 1]))
a0.plot(t[win], vin[win], **fs.LS["vin"], label="传感器电压（含噪声）")
a0.plot(t[win], clean[win], **fs.LS["good"], label="真实温度对应的电压")
fs.ref_h(a0, sim.VREF, "门限 $V_{ref}$ 2.5 V（25 °C）", x=0.01, ha="left")
a0.set_ylabel(fs.qlabel("电压", "V")); a0.legend(loc="lower right", fontsize=8)
a1.plot(t[win], o1[win], **fs.LS["bad"], label=f"比较器输出：3.5 s 内翻转 {n_win} 次")
a1.set_ylim(-0.6, 6.2); a1.set_ylabel(fs.qlabel("输出", "V")); a1.legend(loc="upper left", fontsize=8)
a1.set_xlabel(fs.qlabel("时间", "s"))
fs.save(fig, N, "14_p1_2_chatter.png")

# ---------- 图 14-p1-3 施密特比较器（同相，带回差） ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True).label("比较器\nLM393", loc="center", ofst=(-0.35, 0), fontsize=9))
    vref_divider(d, op)
    d += elm.Line().left().at(op.in2).length(0.75)
    d += elm.Line().down().length(1.5)
    d += (j := elm.Dot())
    d += elm.Resistor().left().label("$R_1$ 10 kΩ")
    d += elm.Dot(open=True).label("$V_{in}$ 传感器", "left")
    d += elm.Resistor().right().at(j.center).label("$R_2$ 100 kΩ（正反馈）", "bottom").tox(op.out.x + 0.75)
    d += elm.Line().up().toy(op.out)
    d += elm.Dot()
    output_pullup(d, op)
save_schem(d, N, "14_p1_3_schmitt.png")

# ---------- 图 14-p2-1 回差曲线（传输特性） ----------
x = np.linspace(2.0, 3.0, 501)
rise = np.where(x > V_H, 5.0, 0.0)
fall = np.where(x < V_L, 0.0, 5.0)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(x, sim.comp_plain(x), **fs.LS["ref"], label="普通比较器（只有一个门限 2.5 V）")
ax.plot(x, rise + 0.06, **fs.LS["vin"], label="输入上升时走的路")
ax.plot(x, fall - 0.06, **fs.LS["vout"], label="输入下降时走的路")
ax.annotate("", (2.62, 0.06), (2.38, 0.06), arrowprops=dict(arrowstyle="->", color=fs.C["vin"], lw=1.5))
ax.annotate("", (2.38, 4.94), (2.62, 4.94), arrowprops=dict(arrowstyle="->", color=fs.C["vout"], lw=1.5))
fs.ref_v(ax, V_H, f"$V_H$ {V_H:.2f} V", y=0.6)
fs.ref_v(ax, V_L, f"$V_L$ {V_L:.2f} V", y=0.6)
ax.annotate("", (V_H, 1.6), (V_L, 1.6), arrowprops=dict(arrowstyle="<->", lw=1))
ax.text((V_H + V_L) / 2, 1.75, f"回差 {V_H - V_L:.2f} V", ha="center", fontsize=9)
fs.axlabels(ax, "输入 $V_{in}$", "V", "输出 $V_o$", "V")
ax.set_ylim(-0.5, 6.4); ax.legend(loc="upper left", fontsize=8)
fs.save(fig, N, "14_p2_1_loop.png")

# ---------- 图 14-p3-1 回差宽度 vs 翻转次数 ----------
R2s = np.array([1000e3, 470e3, 330e3, 220e3, 150e3, 100e3, 68e3])
sigmas = [0.02, 0.04, 0.08]
styles = ["vin", "vout", "third"]
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
result = {}
for sg, st in zip(sigmas, styles):
    _, _, v = sim.make_input(sigma=sg)
    hy, ne = [], []
    for r2 in R2s:
        vh, vl = sim.thresholds(r2=r2)
        hy.append(vh - vl); ne.append(sim.edges(sim.comp_schmitt(v, vh, vl)))
    result[sg] = (np.array(hy), np.array(ne))
    print(f"[扫描] σ = {sg*1e3:.0f} mV：回差 " + "、".join(f"{h:.2f}" for h in hy) + " V → 翻转 " + "、".join(map(str, ne)) + " 次")
    ax.plot(hy, ne, marker="o", **{k: v_ for k, v_ in fs.LS[st].items() if k not in ("marker", "markevery")},
            label=f"噪声 σ = {sg*1e3:.0f} mV")
hy40, ne40 = result[0.04]
assert ne40[-1] == 2 and ne40[0] > 2
assert result[0.02][1][-1] == 2
k = np.flatnonzero(ne40 == 2)[0]
ax.plot([hy40[k]], [2], "o", color="k", ms=5, zorder=6)
ax.annotate(f"σ = 40 mV：回差 {hy40[k]:.2f} V 起\n只翻 2 次（一升一降 = 干净）", (hy40[k], 2), (0.5, 8), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=0.8))
print(f"[标注] σ = 40 mV 时回差 ≥ {hy40[k]:.2f} V 就只翻转 2 次")
fs.ref_h(ax, 2)
ax.set_yscale("log")
ax.set_yticks([2, 5, 10, 20, 50, 100, 200]); ax.set_yticklabels(["2", "5", "10", "20", "50", "100", "200"])  # 2 次那条参考线要有刻度
ax.minorticks_off()
fs.axlabels(ax, "回差 $V_H - V_L$", "V", "20 s 内输出翻转次数", None)
ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "14_p3_1_sweep.png")

# ---------- 图 14-p3-2 窗口比较器 ----------
with drawing() as d:
    d += (A := elm.Opamp(leads=True).label("A", loc="center", ofst=(-0.4, 0)))
    d += (B := elm.Opamp(leads=True).anchor("in1").at((A.in1.x, A.in1.y - 3.5)).label("B", loc="center", ofst=(-0.4, 0)))
    d += elm.Line().left().at(A.in1).length(1.0)
    d += elm.Dot(open=True).label("$V_L$ 2.25 V", "left")
    d += elm.Line().left().at(B.in2).length(1.0)
    d += elm.Dot(open=True).label("$V_H$ 2.75 V", "left")
    d += elm.Line().left().at(A.in2).length(0.5)
    d += (ja := elm.Dot())
    d += elm.Line().down().toy(B.in1)
    d += elm.Line().right().tox(B.in1)
    d += elm.Line().left().at(ja.center).length(2.0)
    d += elm.Dot(open=True).label("$V_{in}$", "left")
    d += elm.Line().right().at(A.out).length(1.0)
    d += (jo := elm.Dot())
    d += elm.Line().down().toy(B.out)
    d += elm.Line().left().tox(B.out)
    d += elm.Resistor().up().at(jo.center).label("2.2 kΩ")
    d += elm.Vdd().label("+5 V")
    d += elm.Line().right().at(jo.center).length(1.25)
    d += elm.Dot(open=True).label("$V_o$（两路输出并在一起）", "right")
save_schem(d, N, "14_p3_2_window.png")

# ---------- 图 14-p3-3 窗口比较器波形 ----------
tw = np.linspace(0, 20, 2001)
vw = 2.5 + 0.5 * np.sin(2 * np.pi * tw / 20 - np.pi / 2) * 1.0
outA = vw > 2.25
outB = vw < 2.75
vo = np.where(outA & outB, 5.0, 0.0)
ins = tw[np.flatnonzero(np.diff(vo) != 0)]
print("[数值] 窗口输出翻转时刻：" + "、".join(f"{x:.2f}" for x in ins) + " s")
assert len(ins) == 4
fig, (a0, a1) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True, gridspec_kw=dict(height_ratios=[1.4, 1]))
a0.plot(tw, vw, **fs.LS["vin"], label="$V_{in}$")
fs.ref_h(a0, 2.75, "$V_H$ 2.75 V", x=0.99)
fs.ref_h(a0, 2.25, "$V_L$ 2.25 V", x=0.99)
a0.set_ylabel(fs.qlabel("电压", "V")); a0.legend(loc="upper left", fontsize=8)
a1.plot(tw, vo, **fs.LS["vout"], label="$V_o$：只在 $V_L$ < $V_{in}$ < $V_H$ 时为高")
for x_ in ins:
    fs.ref_v(a1, x_, f"{x_:.2f}")
a1.set_ylim(-0.6, 6.4); a1.set_ylabel(fs.qlabel("输出", "V")); a1.legend(loc="center", fontsize=8)
a1.set_xlabel(fs.qlabel("时间", "s"))
fs.save(fig, N, "14_p3_3_window_wave.png")


# ======================= page4 动手实验篇：面包板接线图 =======================
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
        hs = [Line2D([], [], color=WIRE[k][0], lw=2.4, label=WIRE[k][1]) for k in WIRE if k in self.used]
        self.ax.legend(handles=hs, loc=loc, ncol=len(hs), fontsize=8.5, frameon=False,
                       bbox_to_anchor=(0.5, -0.01))

    def save(self, prefix, name):
        return fs.save(self.fig, prefix, name)

# ---------- 图 14-p4-1：施密特比较器 + LED 指示的面包板接线（5 V，LM393） ----------
import importlib.util as _ilu
_sp = _ilu.spec_from_file_location("sim14", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "14_sim.py"))
sim14 = _ilu.module_from_spec(_sp); _sp.loader.exec_module(sim14)
bb = Breadboard(30, "施密特比较器面包板俯视图（LM393，5 V）", rails=("+5 V", "GND", "GND", "+5 V"))
bb.chip(12, "LM393", names={1: "OUTA", 2: "IN−A", 3: "IN+A", 4: "GND", 8: "VCC", 7: "OUTB", 6: "IN−B", 5: "IN+B"})
bb.wire("a12", "T+12", "pos")                       # 第 8 脚 VCC
bb.wire("g15", "B-15", "gnd")                       # 第 4 脚 GND
bb.part("g12", "g14", "R2 100 kΩ", "R", lab_side=1)  # 正反馈：输出 → 同相端
bb.part("h8", "h12", "R3 2.2 kΩ", "R", lab_side=-1)  # 上拉电阻
bb.wire("j8", "B+8", "pos")
bb.wire("h13", "h22", "fb")                         # 基准 → 第 2 脚
bb.part("i14", "i18", "R1 10 kΩ", "R", lab_side=-1)  # 输入电阻
bb.part("i22", "i26", "Ra 10 kΩ", "R", lab_side=1)
bb.wire("j26", "B+26", "pos")
bb.part("g22", "g28", "Rb 10 kΩ", "R", lab_side=1)
bb.wire("j28", "B-28", "gnd")
bb.wire("f22", "d14", "fb")                         # 基准 → 第 6 脚（B 路反相端）
bb.wire("j12", "b15", "out", via=[(16.45, -5.4), (16.45, 4.6)])   # A 路输出 → 第 5 脚（B 路同相端）
bb.wire("T+4", "a4", "pos")
bb.part("b4", "b8", "R4 1 kΩ", "R", lab_side=1)
bb.part("c8", "c13", "LED", "L", lab_side=-1)       # 阳极 c8，阴极 c13（第 7 脚 OUTB）
bb.wire("T+30", "B+30", "pos")                      # 上下两条 +5 V 轨连起来
bb.module(-3.2, 9.4, 3.4, 1.4, "5 V 直流电源")
bb.wire((0.2, 9.9), "T+1", "pos")
bb.wire((-0.4, 9.4), "T-3", "gnd")
bb.wire("T-29", "B-29", "gnd")                      # 上下两条地轨连起来
bb.module(31.3, -10.0, 3.2, 1.8, "电位器 10 kΩ\n两端接 +5 V、GND")
bb.wire((31.3, -9.1), "j18", "sig", via=[(18.0, -9.1)])
bb.note(31.6, 0.2, "测输入：\n红表笔 j18\n黑表笔 GND", va="bottom")
bb.note(0.5, -9.6, "基本比较器（对照）：拔掉 R2 即可；R1 上没有电流，同相端电压就等于输入", ha="left")
bb.note(0.5, -10.4, "LED 亮 = A 路输出为低（输入低于门限）；LED 灭 = A 路输出为高", ha="left")
bb.legend()
bb.save(N, "14_p4_1_breadboard.png")

VOL = 0.08                                            # review/spice/14.md：输出低约 0.08 V
vh0, vl0 = sim14.thresholds()
vh = (sim14.VREF * (sim14.R1 + sim14.R2) - VOL * sim14.R1) / sim14.R2       # 输出低按 0.08 V 而不是 0 V
vp20 = (2.0 * sim14.R2 + VOL * sim14.R1) / (sim14.R1 + sim14.R2)
ipu = (sim14.VCC - VOL) / sim14.R3
iled = (sim14.VCC - 1.9 - VOL) / 1e3
print(f"[数值] 门限（输出低按 0 V）：V_H {vh0:.3f} V，V_L {vl0:.3f} V；输出低按 {VOL} V 时 V_H {vh:.3f} V")
print(f"[数值] 输出低、V_in = 2.0 V 时同相端 {vp20:.3f} V；上拉电流 {ipu*1e3:.2f} mA；"
      f"LED 电流约 {iled*1e3:.1f} mA（按压降 1.9 V、B 路输出低 {VOL} V 估算）；回差 {vh - vl0:.3f} V")
assert 2.73 <= vh <= 2.75 and 2.25 <= vl0 <= 2.26 and abs(vp20 - 1.82) < 0.01 and abs(ipu - 2.2e-3) < 0.05e-3


# ======================= 第 8 轮补图：正文讲到具体连接、附近却没有电路图的地方 =======================
ACC = fs.C["bad"]


def schmitt_core(d, x0, y0, vin_label="$V_{in}$", r2="$R_2$ 100 kΩ"):
    """施密特比较器主体：反相端接 2.5 V 基准，Vin 经 R1 到同相端，R2 从同相端接到输出点；返回 (op, 输出点 x)。"""
    d += (op := elm.Opamp(leads=True).right().at((x0, y0)).anchor("center")
          .label("LM393", loc="center", ofst=(-0.35, 0), fontsize=9))
    vref_divider(d, op)
    d += elm.Line().right().at(op.out).length(0.75)
    d += elm.Line().left().at(op.in2).length(0.75)
    d += elm.Line().down().length(1.5)
    d += (j := elm.Dot().label("$V_+$", "top", ofst=(0.25, 0.05)))
    d += (r1 := elm.Resistor().left().label("$R_1$ 10 kΩ"))
    d += elm.Dot(open=True).label(vin_label, "left")
    d += (r2e := elm.Resistor().right().at(j.center).label(r2, "bottom").tox(op.out.x + 0.75))
    d += elm.Line().up().toy(op.out)
    d += elm.Dot()
    return op, r1, r2e


# ---------- 图 14-p1-4 示波器实验：电位器代替传感器，两路探头的位置（page1「在示波器上会看到什么」） ----------
with drawing(fontsize=11) as d:
    d += (op := elm.Opamp(leads=True).right().label("比较器\nLM393", loc="center", ofst=(-0.35, 0), fontsize=9))
    vref_divider(d, op)
    d += elm.Line().left().at(op.in2).length(0.75)
    d += elm.Line().down().length(1.5)
    d += (jv := elm.Dot())
    d += elm.Line().left().length(1.25)
    d += elm.Line().left().length(1.25).color(ACC)
    d += (pot := elm.Potentiometer().up().anchor("tap").color(ACC))
    d += elm.Label().at((pot.center.x - 1.0, pot.center.y)).label("电位器", color=ACC, halign="right")
    d += elm.Vdd().at(pot.end).label("+5 V").color(ACC)
    d += elm.Ground().at(pot.start).color(ACC)
    d += elm.Line().down().at(jv.center).length(1.0)
    d += elm.Dot(open=True).label("CH1：$V_{in}$", "bottom")
    output_pullup(d, op)
    d += elm.Line().down().at((op.out.x + 2.5, op.out.y)).length(1.0)
    d += elm.Dot(open=True).label("CH2：$V_o$", "bottom")
save_schem(d, N, "14_p1_4_scope_setup.png")
print("[电路图] 14-p1-4：电位器（强调色）代替传感器，CH1 接同相端，CH2 接输出")

# ---------- 图 14-p2-3 推门限用的两个状态：输出低 / 输出高（page2 第 2 节） ----------
with drawing(fontsize=11) as d:
    for k, (x0, low) in enumerate([(0, True), (14, False)]):
        op, r1, r2e = schmitt_core(d, x0, 0)
        o = (op.out.x + 0.75, op.out.y)
        d += elm.Line().right().at(o).length(1.25)
        d += (q := elm.Dot())
        d += elm.Resistor().up().label("$R_3$ 2.2 kΩ")
        d += elm.Vdd().label("$V_{CC}$ 5 V")
        d += elm.Line().down().at(q.center).length(0.75)
        d += (sw := elm.Switch(action="close" if low else "open").down().color(ACC))
        d += elm.Label().at((sw.center.x + 0.6, sw.center.y)).label("输出管\n导通" if low else "输出管\n截止", color=ACC, halign="left", fontsize=10)
        d += elm.Ground()
        d += elm.Label().at((q.center.x + 0.35, q.center.y + 0.35)).label("$V_o \\approx 0$" if low else "$V_o \\approx V_{CC}$", halign="left", fontsize=10)
        # 电流方向：输出低时电流从 Vin 经 R1、R2 流向输出；输出高时从 VCC 经 R3、R2 流回同相端
        y = r1.center.y - 1.0
        if low:
            d += elm.Arrow().right().at((r1.start.x - 1.2, y)).length(5.0).color(ACC).label("$I$：$V_{in}$ → $R_1$ → $R_2$ → 输出（到地）", "bottom", fontsize=10, color=ACC)
        else:
            d += elm.Arrow().left().at((r1.start.x + 3.8, y)).length(5.0).color(ACC).label("$I$：$V_{CC}$ → $R_3$ → $R_2$ → $V_+$（→ $R_1$）", "bottom", fontsize=10, color=ACC)
        title = "（a）输出为低：求上门限 $V_H$" if low else "（b）输出为高：求下门限 $V_L$"
        d += elm.Label().at((x0 - 4.5, 6.4)).label(title, fontsize=12, halign="left")
save_schem(d, N, "14_p2_3_two_states.png")
print("[电路图] 14-p2-3：两种输出状态下 R2 下端接到哪里（导通到地 / 经 R3 到 VCC）")

# ---------- 图 14-p3-4 练习 3：上拉电阻改接 3.3 V，比较器仍用 5 V ----------
with drawing(fontsize=11) as d:
    op, r1, r2e = schmitt_core(d, 0, 0)
    d += elm.Line().right().at((op.out.x + 0.75, op.out.y)).length(1.25)
    d += (q := elm.Dot())
    d += elm.Resistor().up().label("$R_3$ 上拉").color(ACC)
    d += elm.Vdd().label("+3.3 V（单片机电源）").color(ACC)
    d += elm.Line().right().at(q.center).length(1.0)
    d += elm.Dot(open=True).label("$V_o$ → 3.3 V 单片机", "right")
    d += elm.Label().at((op.center.x, op.center.y - 1.6)).label("比较器电源 $V_{CC}$ = 5 V", fontsize=10)
save_schem(d, N, "14_p3_4_pullup_3v3.png")

# ---------- 图 14-p3-5 练习 4 答案：电池先经 100 kΩ/100 kΩ 分压，再进窗口比较器 ----------
with drawing(fontsize=11) as d:
    d += elm.Dot(open=True).at((0, 0)).label("电池 +\n3.0～4.2 V", "left").color(ACC)
    d += elm.Line().right().length(0.75).color(ACC)
    d += (ra := elm.Resistor().down().color(ACC))
    d += (jm := elm.Dot().color(ACC))
    d += (rb := elm.Resistor().down().color(ACC))
    for r_ in (ra, rb):
        d += elm.Label().at((r_.center.x - 0.5, r_.center.y)).label("100 kΩ", color=ACC, halign="right")
    d += elm.Ground().color(ACC)
    d += elm.Line().right().at(jm.center).length(1.5)
    d += elm.Label().at((jm.center.x + 0.75, jm.center.y - 0.45)).label("1.5～2.1 V", fontsize=10, color=ACC)
    d += (ja := elm.Dot())
    xa = ja.center.x
    d += (A := elm.Opamp(leads=True).right().anchor("in2").at((xa + 0.75, jm.center.y + 2.0)).label("A", loc="center", ofst=(-0.4, 0)))
    d += (B := elm.Opamp(leads=True).right().anchor("in1").at((xa + 0.75, jm.center.y - 1.5)).label("B", loc="center", ofst=(-0.4, 0)))
    d += elm.Line().up().at(ja.center).toy(A.in2); d += elm.Line().right().tox(A.in2)
    d += elm.Line().down().at(ja.center).toy(B.in1); d += elm.Line().right().tox(B.in1)
    d += elm.Line().left().at(A.in1).length(0.4); d += elm.Line().up().length(0.6)
    d += elm.Dot(open=True).label("$V_L$ 1.5 V", "left")
    d += elm.Line().left().at(B.in2).length(0.4); d += elm.Line().down().length(0.6)
    d += elm.Dot(open=True).label("$V_H$ 2.1 V", "left")
    d += elm.Line().right().at(A.out).length(1.0)
    d += (jo := elm.Dot())
    d += elm.Line().down().toy(B.out); d += elm.Line().left().tox(B.out)
    d += elm.Resistor().up().at(jo.center).label("2.2 kΩ")
    d += elm.Vdd().label("+5 V")
    d += elm.Line().right().at(jo.center).length(1.25)
    d += elm.Dot(open=True).label("$V_o$（高 = 电池正常）", "right")
save_schem(d, N, "14_p3_5_battery_window.png")
print("[电路图] 14-p3-5：新加的 100 kΩ/100 kΩ 分压用强调色")
