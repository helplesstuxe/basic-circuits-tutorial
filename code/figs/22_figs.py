"""22 三极管驱动继电器：除 22_sim.py 那两张以外的所有配图。运行：python code/figs/22_figs.py
图上出现的每个数字都由本脚本打印（fs.mark 自动打印；其余用 print）。模型与 code/22_sim.py 相同。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from schem import *
import figstyle as fs

P = "22"
VCC, R_COIL, V_BE, V_SAT = 5.0, 70.0, 0.7, 0.2
I_MAX = (VCC - V_SAT) / R_COIL


def drive(v_pin, rb, beta):
    """返回 (I_C, V_CE)；与 22_sim.py 的 drive() 相同的分段模型。"""
    ib = np.maximum(v_pin - V_BE, 0.0) / rb
    ic = np.minimum(beta * ib, I_MAX)
    vce = np.where(beta * ib >= I_MAX, V_SAT, VCC - ic * R_COIL)
    return ic, vce


def driver_schem():
    """图 22-p1-3：单片机引脚 → R_B → NPN → 继电器线圈（反并续流二极管）；触点在隔离带另一侧切换 220V 灯。"""
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 0)).label("单片机引脚\n（5 V / 0 V）", "left")
        d += elm.Resistor().right().label("$R_B$ 680 Ω")
        d += (q := elm.BjtNpn().anchor("base").label("Q1\n2N3904", "right", ofst=(0.1, -0.2)))
        d += elm.Line().down().at(q.emitter).length(0.6)
        d += elm.Ground()
        d += elm.Line().up().at(q.collector).length(0.5)
        d += (jc := elm.Dot())
        d += (kc := Coil(label="").up())
        d += elm.Label().at((kc.center[0] - 1.5, kc.center[1])).label("继电器线圈 K1\n5 V / 70 Ω")
        d += (jt := elm.Dot())
        d += elm.Line().up().length(0.6)
        d += elm.Vdd().label("+5 V")
        d += elm.Line().right().at(jc.center).length(1.6)
        d += elm.Diode().up().toy(jt.center).label("D1 续流\n1N4148", "right")
        d += elm.Line().left().tox(jt.center)
        barrier(d, 6.2, -1.8, 4.6, "低压侧 ｜ 220V 侧")
        d += elm.Dot(open=True).at((7.6, 3.6)).label("L 220V", "left")
        d += elm.Line().right().length(0.4)
        d += ContactNO().right().label("K1 常开触点", ofst=0.5)
        d += elm.Line().right().length(0.4)
        d += elm.Line().down().length(1.2)
        d += LampX().down().label("灯", "right")
        d += elm.Line().down().length(1.0)
        d += elm.Line().left().tox(7.6)
        d += elm.Dot(open=True).label("N", "left")
    print("[图 22-p1-3] R_B 680 Ω、2N3904、线圈 5 V / 70 Ω、续流二极管 1N4148、触点切换 220V 灯")
    save_schem(d, P, "22_p1_3_driver.png")


def current_bars():
    """图 22-p1-1：单片机引脚能给的电流 vs 继电器线圈要的电流。"""
    names = ["引脚建议\n（测试条件）", "引脚绝对\n最大值", "SRD-05VDC\n高灵敏型线圈", "SRD-05VDC\n标准型线圈"]
    vals = [20.0, 40.0, 71.4, 89.3]
    cols = [fs.C["vin"], fs.C["bad"], fs.C["vout"], fs.C["vout"]]
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.bar(names, vals, color=cols, width=0.55)
    for k, v in enumerate(vals):
        ax.text(k, v + 2, f"{v:g} mA", ha="center", fontsize=9)
        print(f"[图 22-p1-1] {names[k].replace(chr(10), '')}: {v:g} mA")
    fs.ref_h(ax, 40)
    fs.axlabels(ax, None, None, "电流", "mA")
    ax.set_ylim(0, 105)
    fs.save(fig, P, "22_p1_1_current.png")


def two_states():
    """图 22-p1-2：开到底（R_B = 680 Ω）与半开（R_B = 10 kΩ，β = 100）的对比。"""
    cases = [("开到底\n$R_B$ = 680 Ω", 680), ("半开\n$R_B$ = 10 kΩ", 10e3)]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    for k, (name, rb) in enumerate(cases):
        ic, vce = drive(5.0, rb, 100)
        pct = (VCC - vce) / VCC * 100
        p = vce * ic * 1e3
        c = fs.C["vin"] if k == 0 else fs.C["bad"]
        a1.bar(k, pct, color=c, width=0.5); a1.text(k, pct + 2, f"{pct:.0f}%", ha="center", fontsize=9)
        a2.bar(k, p, color=c, width=0.5); a2.text(k, p + 2, f"{p:.1f} mW", ha="center", fontsize=9)
        print(f"[图 22-p1-2] {name.replace(chr(10), ' ')}（β = 100）：线圈 {pct:.0f}% 额定，三极管 {p:.1f} mW")
    for a in (a1, a2):
        a.set_xticks([0, 1], [c[0] for c in cases])
    fs.ref_h(a1, 75, "吸合门限 75%", x=0.98)
    a1.set_ylim(0, 110); a2.set_ylim(0, 105)
    fs.axlabels(a1, None, None, "线圈电压占额定值", "%")
    fs.axlabels(a2, None, None, "三极管发热功率", "mW")
    fs.save(fig, P, "22_p1_2_states.png")


def ic_ib():
    """图 22-p2-1：I_C 随 I_B 变化——先按 β 斜线上升，碰到线圈允许的上限就"顶住"（饱和）。"""
    ib = np.linspace(0, 8e-3, 801)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for beta, key in [(300, "vin"), (100, "vout"), (30, "third")]:
        ax.plot(ib * 1e3, np.minimum(beta * ib, I_MAX) * 1e3, **fs.LS[key], label=f"β = {beta}")
    fs.ref_h(ax, I_MAX * 1e3, f"上限 $(V_{{CC}}-0.2\\,\\mathrm{{V}})/R$ = {I_MAX*1e3:.1f} mA", x=0.98)
    need = I_MAX / 30
    fs.ref_v(ax, need * 1e3, f"$I_C/\\beta_{{min}}$ = {need*1e3:.2f} mA", y=0.55)
    ib_use = (5.0 - V_BE) / 680
    fs.ref_v(ax, ib_use * 1e3, f"680 Ω：{ib_use*1e3:.2f} mA", y=0.35)
    print(f"[图 22-p2-1] 上限 {I_MAX*1e3:.1f} mA；β_min = 30 时需要 {need*1e3:.2f} mA；R_B = 680 Ω 给 {ib_use*1e3:.2f} mA（{ib_use/need:.1f} 倍）")
    fs.axlabels(ax, "基极电流 $I_B$", "mA", "集电极电流 $I_C$", "mA")
    ax.set_ylim(0, 85)
    ax.legend(loc="lower center")
    fs.save(fig, P, "22_p2_1_icib.png")


def rb_sweep():
    """图 22-p3-1：扫 R_B，看线圈拿到的电压占额定值多少（三种 β）。"""
    rb = np.logspace(2, 5, 600)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for beta, key in [(300, "vin"), (100, "vout"), (30, "third")]:
        ic, vce = drive(5.0, rb, beta)
        ax.plot(rb, (VCC - vce) / VCC * 100, **fs.LS[key], label=f"β = {beta}")
        # 线圈电压刚好跌到 75% 吸合门限时的 R_B
        r75 = beta * (5.0 - V_BE) / (0.75 * VCC / R_COIL)
        print(f"[图 22-p3-1] β = {beta}：R_B 超过 {r75/1e3:.2f} kΩ 时线圈低于 75%")
    fs.ref_h(ax, 75, "吸合门限 75%", x=0.30)
    fs.ref_v(ax, 680, "680 Ω", y=0.25)
    ax.set_xscale("log")
    fs.axlabels(ax, "基极电阻 $R_B$", "Ω", "线圈电压占额定值", "%")
    ax.set_ylim(0, 105)
    ax.legend(loc="lower left")
    fs.save(fig, P, "22_p3_1_rbsweep.png")


def uln_schem():
    """图 22-p3-2（练习答案）：ULN2003 驱动两路 12 V 继电器，COM 接线圈电源。"""
    with drawing(fontsize=11) as d:
        d += (u := module("ULN2003", ("IN1", "IN2", "GND"), ("OUT1", "OUT2", "COM")))
        d += elm.Line().left().at(u.IN1).length(1.0)
        d += elm.Dot(open=True).label("单片机 引脚 1", "left")
        d += elm.Line().left().at(u.IN2).length(1.0)
        d += elm.Dot(open=True).label("单片机 引脚 2", "left")
        d += elm.Line().left().at(u.GND).length(0.6)
        d += elm.Ground()
        top = u.OUT1.y + 2.6
        d += elm.Line().right().at(u.OUT1).length(1.2)
        d += (k1 := Coil(label="").up().toy(top))
        d += elm.Label().at((k1.center[0] - 1.1, k1.center[1])).label("K1 线圈\n12 V")
        d += elm.Line().right().at(u.OUT2).length(3.2)
        d += (k2 := Coil(label="").up().toy(top))
        d += elm.Label().at((k2.center[0] + 1.0, k2.center[1])).label("K2 线圈\n12 V")
        d += elm.Line().right().at(u.COM).length(5.8)
        d += elm.Line().up().toy(top)
        d += elm.Line().left().tox(u.OUT1.x + 1.2)
        d += elm.Line().up().at((u.OUT1.x + 2.8, top)).length(0.5)
        d += elm.Vdd().label("+12 V")
    print("[图 22-p3-2] ULN2003：IN1/IN2 直接接单片机引脚，OUT 接线圈下端，COM 接 +12 V")
    save_schem(d, P, "22_p3_2_uln2003.png")


def zener_schem():
    """图 22-p2-4：续流二极管串稳压管。两只管子"负极对负极"串联后反并在线圈两端。"""
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 0)).label("单片机引脚", "left")
        d += elm.Resistor().right().label("$R_B$")
        d += (q := elm.BjtNpn().anchor("base").label("Q1", "right", ofst=(0.1, -0.2)))
        d += elm.Line().down().at(q.emitter).length(0.6)
        d += elm.Ground()
        d += elm.Line().up().at(q.collector).length(0.5)
        d += (jc := elm.Dot())
        d += (kc := Coil(label="").up().length(3.0))
        d += elm.Label().at((kc.center[0] - 1.3, kc.center[1])).label("继电器\n线圈")
        d += (jt := elm.Dot())
        d += elm.Line().up().length(0.6)
        d += elm.Vdd().label("+5 V")
        d += elm.Line().right().at(jc.center).length(1.8)
        d += (dd := elm.Diode().up().length(1.5))
        d += (zz := elm.Zener().up().length(1.5).reverse())
        d += elm.Label().at((dd.center[0] + 1.5, dd.center[1])).label("D1 普通二极管\n（负极朝上）")
        d += elm.Label().at((zz.center[0] + 1.5, zz.center[1])).label("Z1 稳压管 24 V\n（负极朝下）")
        d += elm.Line().left().tox(jt.center)
    print("[图 22-p2-4] 集电极 → D1（正极→负极）→ Z1（负极→正极）→ +5 V；钳位 5 + 0.7 + 24 = 29.7 V")
    save_schem(d, P, "22_p2_4_zener.png")


if __name__ == "__main__":
    driver_schem(); current_bars(); two_states(); ic_ib(); rb_sweep(); uln_schem(); zener_schem()


# ======================= page4 动手实验篇 =======================
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
        """测量点：红紫色圆圈 + 标签。"""
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
        hs = [Line2D([], [], color=WIRE[k][0], lw=2.4, label=WIRE[k][1]) for k in WIRE if k in self.used]
        self.ax.legend(handles=hs, loc=loc, ncol=len(hs), fontsize=8.5, frameon=False,
                       bbox_to_anchor=(0.5, -0.01))

    def save(self, prefix, name):
        return fs.save(self.fig, prefix, name)



WIRE["fb"] = (fs.C["fb"], "接继电器线圈")
WIRE["load"] = (fs.C["vout"], "触点侧 12 V 回路")

# 实验电路：线圈侧 = page2 §六 那套 5 V 电路（2N3904、680 Ω、SRD-05VDC 高灵敏型 70 Ω、1N4148 负极接 +5 V），
# 「单片机引脚」用 10 kΩ 电位器滑臂代替。触点侧只接一只 12 V 小灯泡和 12 V 直流电源，和线圈侧没有任何导线相连。
# 期望读数抄自 review/spice/22.md「面包板万用表读数」（onsemi 2N3904 官方模型），不在这里重新跑 SPICE。
P4_SPICE = dict(vce_on=0.2733, vcoil_on=4.73, vrb_on=4.13, vbe_on=0.87, vce_10k=2.7)


def fig_p4_1():
    """图 22-p4-1：三极管驱动继电器的面包板接线（线圈侧 5 V；触点侧只接 12 V 小灯泡）。"""
    bb = Breadboard(30, "三极管驱动继电器面包板俯视图（线圈侧 5 V，触点侧 12 V 小灯泡）",
                    size=(12.5, 6.6), rails=("+5 V", "GND", "GND", "+5 V"))
    ax = bb.ax
    ax.set_xlim(-3.4, 48.5)
    bb.sip(15, "a", "2N3904", ["E", "B", "C"], fc="#3a3a3a")          # 平面（印字面）朝你，左起 E、B、C
    bb.wire("e15", "B-15", "gnd")
    bb.part("b11", "b16", "R_B 680 Ω", "R", lab_side=1)
    bb.part("d17", "d22", "D1 1N4148", "D", lab_side=1)               # 阳极 d17（集电极列），阴极 d22
    bb.wire("a22", "T+22", "pos")
    bb.sip(5, "f", "电位器 10 kΩ", ["1", "滑臂", "3"], up=False, fc="#d0d6de", tc="k")
    bb.wire("j5", "B+5", "pos", via=[(4.4, -5.4), (4.4, -7.6)])
    bb.wire("j7", "B-7", "gnd")
    bb.wire("i6", "c11", "sig", via=[(9.2, -4.4), (9.2, 3.6)])
    bb.wire("T+29", "B+29", "pos", via=[(29.0, 9.3), (31.4, 9.3), (31.4, -8.3), (29.0, -8.3)])
    bb.wire("T-28", "B-28", "gnd", via=[(28.0, 7.2), (30.6, 7.2), (30.6, -7.1), (28.0, -7.1)])
    bb.module(-3.2, 9.4, 3.6, 1.4, "5 V 电源\n（USB 稳压模块）")
    bb.wire((0.4, 10.1), "T+1", "pos")
    bb.wire((-1.4, 9.4), "T-2", "gnd", via=[(-1.4, 7.7)])
    # 继电器放在面包板外（SRD 的引脚间距插不进面包板），五只脚各焊一根杜邦线
    rx, ry, rw, rh = 33.0, -1.6, 5.4, 6.4
    bb.module(rx, ry, rw, rh, "", fc="#cfe0f5")
    ax.text(rx + rw / 2, ry + rh - 0.6, "继电器 SRD-05VDC", ha="center", fontsize=8.5, zorder=8)
    pins = {"线圈 1": (rx + 0.2, ry + 4.4), "线圈 2": (rx + 0.2, ry + 1.6),
            "COM": (rx + rw - 0.2, ry + 4.4), "NO": (rx + rw - 0.2, ry + 3.0), "NC": (rx + rw - 0.2, ry + 1.6)}
    for nm, (x, y) in pins.items():
        ax.add_patch(Circle((x, y), 0.22, fc="#c8a24a", ec="0.2", zorder=8))
        ax.text(x + (0.45 if x < rx + 1 else -0.45), y, nm, ha="left" if x < rx + 1 else "right",
                va="center", fontsize=8, zorder=8)
    ax.plot([rx + rw / 2] * 2, [ry + 0.3, ry + rh - 1.1], ls="--", color="0.4", lw=1.6, zorder=9)
    bb.wire("c22", pins["线圈 1"], "fb", via=[(22.0, 3.6), (32.0, 3.6), (32.0, ry + 4.4)])
    bb.wire("e17", pins["线圈 2"], "fb", via=[(17.0, 1.0), (32.4, 1.0), (32.4, ry + 1.6)])
    # 触点侧：12 V 电源 + 小灯泡，只用鳄鱼夹线，不经过面包板
    bb.module(43.2, 6.6, 4.6, 1.6, "12 V 直流电源\n（适配器）", fc="#fde9d9")
    ax.text(44.6, 6.2, "+", color=fs.C["bad"], ha="center", va="top", fontsize=10, fontweight="bold", zorder=8)
    ax.text(47.2, 6.2, "−", color="k", ha="center", va="top", fontsize=10, fontweight="bold", zorder=8)
    lx, ly = 44.6, 2.4
    ax.add_patch(Circle((lx, ly), 0.65, fc="#fff7c2", ec="0.2", lw=1.0, zorder=7))
    for sx in (-1, 1):
        ax.plot([lx - 0.42, lx + 0.42], [ly - 0.42 * sx, ly + 0.42 * sx], color="0.2", lw=1.0, zorder=8)
    ax.text(lx + 0.9, ly, "12 V 小灯泡", ha="left", va="center", fontsize=8.5, zorder=8)
    bb.wire(pins["NO"], (lx - 0.65, ly), "load", via=[(40.5, ry + 3.0), (40.5, ly)])
    bb.wire((lx, ly + 0.65), (lx, 6.6), "load")
    bb.wire((46.8, 6.6), pins["COM"], "load", via=[(46.8, 5.4), (39.4, 5.4), (39.4, ry + 4.4)])
    ax.text(42.0, -1.4, "NC 悬空不接", ha="center", fontsize=8, color="0.3")
    ax.text(rx + rw / 2, ry - 0.6, "灰虚线：继电器内部隔开两侧", ha="center", va="top", fontsize=8, color="0.3")
    bb.probe("e11", "驱动", dy=-0.75)
    bb.probe("c16", "B", dx=0.0, dy=0.75)
    bb.probe("b17", "C", dx=0.75, dy=0.4)
    bb.probe("e22", "+5", dx=0.85)
    bb.note(19.0, -3.2, "黑表笔一律插 GND 轨\n（测 V_CE 时就是发射极）\n红紫色圈 = 下红表笔的列", va="center")
    bb.note(1.0, -9.6, "步骤 5 换基极电阻：R_B 从 680 Ω 换成 10 kΩ，位置不变（b11–b16）", ha="left")
    bb.legend()
    bb.save("22", "22_p4_1_breadboard.png")
    print("[接线] 2N3904 E/B/C 在 a15/a16/a17；E 列 e15→GND；R_B b11–b16；D1 阳极 d17、阴极 d22，a22→+5 V；"
          "线圈 1 ← c22，线圈 2 ← e17；电位器 f5/f6/f7，滑臂 i6→c11；触点侧 12 V → 灯泡 → NO，COM → 12 V 负极")
    print(f"[数值] 线圈电流 ≈ {P4_SPICE['vcoil_on']:.2f} V / 70 Ω = {P4_SPICE['vcoil_on'] / 70 * 1e3:.1f} mA；"
          f"基极电流 ≈ {P4_SPICE['vrb_on']:.2f} V / 680 Ω = {P4_SPICE['vrb_on'] / 680 * 1e3:.2f} mA；"
          f"强制 β ≈ {P4_SPICE['vcoil_on'] / 70 / (P4_SPICE['vrb_on'] / 680):.1f}")
    print(f"[数值] 吸合保证线 75% × 5 V = {0.75 * 5:.2f} V；释放保证线 10% × 5 V = {0.10 * 5:.2f} V；"
          f"线圈电阻 70 Ω ±10% = {70 * 0.9:.0f}–{70 * 1.1:.0f} Ω")


if __name__ == "__main__":
    fig_p4_1()
