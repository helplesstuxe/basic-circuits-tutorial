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
    bb.note(19.0, -3.2, "黑表笔一律插 GND 轨\n（测 V_CE 时就是发射极）\n紫色圈 = 下红表笔的列", va="center")
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


# ======================= 第 8 轮补电路图（page1–page3：凡正文讲具体电路连接处，附近都要有电路图） =======================
from schem import C as _C
EMPH = _C["third"]      # 强调色（红紫）：新加的元件、要特别注意的电流路径
BAD = _C["bad"]         # 朱红：错误接法、超限


def _relay_drv(d, x0, vcc="+5 V", pin="单片机引脚", rb="$R_B$ 680 Ω", q="Q1\n2N3904",
               coil="继电器线圈\n70 Ω", diode="ok", dlab="D1", dcol=None, pulldown=None, ic=None):
    """低边 NPN 继电器驱动的通用画法；返回关键点坐标。
    diode: "ok" 正确（负极朝电源）/ "rev" 接反 / "zener" 串稳压管 / None 不加。
    pulldown: None 或 (标注, 颜色)，画基极到地的下拉电阻。ic: 电源线上标的电流文字。"""
    d += elm.Dot(open=True).at((x0, 0)).label(pin, "left")
    d += elm.Resistor().endpoints((x0, 0), (x0 + 2.4, 0)).label(rb)
    bx = x0 + 3.4
    d += elm.Line().endpoints((x0 + 2.4, 0), (bx, 0))
    d += (qq := elm.BjtNpn().anchor("base").at((bx, 0)).label(q, "right", ofst=(0.1, -0.2)))
    cx = qq.collector[0]
    d += elm.Line().endpoints(qq.emitter, (cx, -1.3))
    d += elm.Ground().at((cx, -1.3))
    if pulldown:
        px = x0 + 2.9
        d += elm.Dot().at((px, 0))
        d += elm.Resistor().endpoints((px, 0), (px, -1.9)).color(pulldown[1]).label(pulldown[0], "bottom", color=pulldown[1])
        d += elm.Ground().at((px, -1.9))
    d += elm.Line().endpoints(qq.collector, (cx, 1.2))
    d += elm.Dot().at((cx, 1.2))
    d += Coil(label="").endpoints((cx, 1.2), (cx, 3.7))
    d += elm.Label().at((cx - 0.5, 2.45)).label(coil, halign="right")
    d += elm.Dot().at((cx, 3.7))
    top = elm.Line().endpoints((cx, 3.7), (cx, 4.9))
    d += top
    if ic:
        d += elm.CurrentLabelInline(direction="in", ofst=0.25).at(top).label(ic, "right")
    d += elm.Vdd().at((cx, 4.9)).label(vcc)
    dx = cx + 1.6
    if diode in ("ok", "rev"):
        col = dcol or "black"
        d += elm.Line().endpoints((cx, 1.2), (dx, 1.2)).color(col)
        dd = elm.Diode().endpoints((dx, 1.2), (dx, 3.7)).color(col)
        if diode == "rev":
            dd.reverse()
        d += dd
        d += elm.Label().at((dx + 0.45, 2.45)).label(dlab, halign="left", color=col)
        d += elm.Line().endpoints((dx, 3.7), (cx, 3.7)).color(col)
    elif diode == "zener":
        col = dcol or "black"
        d += elm.Line().endpoints((cx, 1.2), (dx, 1.2)).color(col)
        d += elm.Diode().endpoints((dx, 1.2), (dx, 2.45)).color(col)
        d += elm.Zener().endpoints((dx, 2.45), (dx, 3.7)).reverse().color(col)
        d += elm.Label().at((dx + 0.35, 1.8)).label("D1", halign="left", color=col)
        d += elm.Label().at((dx + 0.35, 3.1)).label(dlab, halign="left", color=col)
        d += elm.Line().endpoints((dx, 3.7), (cx, 3.7)).color(col)
    return dict(cx=cx, dx=dx, bx=bx, q=qq)


def fig_p1_4():
    """图 22-p1-4（错误示范）：单片机引脚直接接继电器线圈。"""
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 3.0)).label("单片机引脚\n输出 5 V", "left")
        d += elm.Line().endpoints((0, 3.0), (2.0, 3.0))
        d += Coil(label="").endpoints((2.0, 3.0), (2.0, 0.5))
        d += elm.Label().at((1.6, 1.75)).label("继电器线圈\n5 V / 70 Ω", halign="right")
        d += elm.Ground().at((2.0, 0.5))
        w = elm.Line().endpoints((2.0, 3.0), (2.0, 3.0))
        d += elm.Label().at((2.5, 2.3)).label("线圈要 71.4 mA\n引脚绝对最大只有 40 mA", halign="left", color=BAD)
        d += elm.Label().at((2.5, 1.0)).label("断开瞬间线圈挤出的高压尖峰\n直接打回引脚", halign="left", color=BAD)
    print("[图 22-p1-4] 错误示范：引脚直接推 70 Ω 线圈，要 71.4 mA > 40 mA")
    save_schem(d, P, "22_p1_4_pin_direct.png")


def fig_p2_5():
    """图 22-p2-5：推导一用到的电路与数值（R_B 680 Ω → I_B 6.32 mA；I_C(max) 68.6 mA；V_CE 0.2 V）。"""
    ib = (5.0 - V_BE) / 680
    assert abs(ib * 1e3 - 6.32) < 0.01 and abs(I_MAX * 1e3 - 68.6) < 0.05
    with drawing(fontsize=11) as d:
        r = _relay_drv(d, 0, pin="单片机引脚\n$V_{pin}$ = 5 V", ic=f"$I_C$ = {I_MAX*1e3:.1f} mA",
                       coil="线圈 $R_{coil}$\n70 Ω")
        d += elm.Label().at((1.2, -0.6)).label(f"→ $I_B$ = {ib*1e3:.2f} mA", fontsize=10, color=EMPH)
        d += elm.Label().at((2.6, -0.9)).label("$V_{BE}$ = 0.7 V", fontsize=10, halign="right")
        d += elm.Label().at((r["cx"] + 0.3, -0.85)).label("$V_{CE}$ = 0.2 V（饱和）", fontsize=10, halign="left")
    print(f"[图 22-p2-5] I_B = {ib*1e3:.2f} mA，I_C(max) = {I_MAX*1e3:.1f} mA")
    save_schem(d, P, "22_p2_5_rb_calc.png")


def fig_p2_6():
    """图 22-p2-6：关断瞬间 (a) 无二极管，线圈电流只能给杂散电容充电；(b) 有 D1，电流经 D1 绕回线圈。"""
    with drawing(fontsize=11) as d:
        r = _relay_drv(d, 0, pin="引脚\n5 V→0 V", rb="$R_B$", q="Q1\n关断", coil="线圈\n0.1 H", diode=None)
        cx = r["cx"]
        d += elm.Line().endpoints((cx, 1.2), (cx + 1.6, 1.2)).color(BAD)
        d += elm.Capacitor().endpoints((cx + 1.6, 1.2), (cx + 1.6, -0.6)).color(BAD).linestyle("--")
        d += elm.Label().at((cx + 1.95, 0.3)).label("杂散电容\n$C$ ≈ 100 pF", halign="left", color=BAD, fontsize=10)
        d += elm.Ground().at((cx + 1.6, -0.6))
        d += elm.Label().at((cx + 0.3, 6.5)).label("(a) 不加续流二极管：集电极冲到约 2173 V", halign="center", fontsize=11)
        x1 = 10.0
        r2 = _relay_drv(d, x1, pin="引脚\n5 V→0 V", rb="$R_B$", q="Q1\n关断", coil="线圈\n0.1 H", diode="ok",
                        dlab="D1", dcol=EMPH)
        c2, d2 = r2["cx"], r2["dx"]
        d += elm.LoopCurrent([elm.Line().at((c2, 3.7)).to((d2, 3.7)), elm.Line().at((d2, 3.7)).to((d2, 1.2)),
                              elm.Line().at((d2, 1.2)).to((c2, 1.2)), elm.Line().at((c2, 1.2)).to((c2, 3.7))],
                             direction="ccw", pad=0.55).color(EMPH)
        d += elm.Label().at((d2 + 0.35, 0.6)).label("线圈电流经 D1\n绕回线圈上端\n集电极钳在 5.7 V", halign="left", color=EMPH, fontsize=10)
        d += elm.Label().at((c2 + 0.3, 6.5)).label("(b) 线圈两端反并 D1", halign="center", fontsize=11)
    print(f"[图 22-p2-6] 无二极管尖峰估算 {VCC + I_MAX*np.sqrt(0.1/100e-12):.0f} V；有 D1 钳在 {VCC+0.7:.1f} V")
    save_schem(d, P, "22_p2_6_off_compare.png")


def fig_p2_7():
    """图 22-p2-7：第六节低压实验电路——跳线代替单片机，触点只接 5 V + 1 kΩ + LED，万用表测 V_CE。"""
    with drawing(fontsize=11) as d:
        r = _relay_drv(d, 0, pin="跳线：接 5 V\n或接地", rb="$R_B$ 680 Ω\n（步骤 3 换 10 kΩ）",
                       coil="SRD-05VDC\n线圈", dlab="1N4148")
        cx, dx = r["cx"], r["dx"]
        mx = dx + 1.9
        d += elm.Line().endpoints((dx, 1.2), (mx, 1.2)).color(EMPH)
        d += elm.MeterV().endpoints((mx, 1.2), (mx, -1.3)).color(EMPH).label("万用表\n测 $V_{CE}$", "right", color=EMPH)
        d += elm.Line().endpoints((mx, -1.3), (cx, -1.3)).color(EMPH)
        x2 = mx + 3.2
        d += elm.Vdd().at((x2, 4.9)).label("+5 V")
        d += ContactNO().endpoints((x2, 4.9), (x2, 3.1))
        d += elm.Label().at((x2 + 0.6, 4.0)).label("K1 常开触点", halign="left")
        d += elm.Resistor().endpoints((x2, 3.1), (x2, 1.1))
        d += elm.Label().at((x2 + 0.6, 2.1)).label("1 kΩ", halign="left")
        d += elm.LED().endpoints((x2, 1.1), (x2, -0.9))
        d += elm.Label().at((x2 + 0.9, 0.1)).label("LED", halign="left")
        d += elm.Ground().at((x2, -0.9))
        d += elm.Label().at((x2 - 0.5, -2.0)).label("触点侧也只接 5 V 低压负载", halign="center", fontsize=10)
    print("[图 22-p2-7] 实验：680 Ω、2N3904、1N4148、触点接 5 V + 1 kΩ + LED")
    save_schem(d, P, "22_p2_7_lab.png")


def fig_p3_3():
    """图 22-p3-3：续流二极管 (a) 正确（负极接 +5 V）与 (b) 接反（导通即短路）。"""
    with drawing(fontsize=11) as d:
        _relay_drv(d, 0, pin="引脚", rb="$R_B$", q="Q1", coil="线圈", dlab="D1\n负极朝 +5 V")
        d += elm.Label().at((3.9, 6.5)).label("(a) 正确：平时 D1 反向截止", halign="center")
        x1 = 10.0
        r = _relay_drv(d, x1, pin="引脚", rb="$R_B$", q="Q1\n导通", coil="线圈", diode="rev", dlab="D1 接反",
                       dcol=BAD)
        cx, dx = r["cx"], r["dx"]
        d += elm.Arrow().endpoints((dx - 0.45, 3.4), (dx - 0.45, 1.5)).color(BAD)   # 短路电流：+5 V → D1 → 集电极
        d += elm.Label().at((dx + 0.35, 0.4)).label("+5 V 经 D1 直接灌进\n集电极 → Q1 → 地：\n几乎短路", halign="left", color=BAD, fontsize=10)
        d += elm.Label().at((x1 + 3.9, 6.5)).label("(b) 接反：Q1 一导通就短路", halign="center", color=BAD)
    save_schem(d, P, "22_p3_3_diode_dir.png")


def fig_p3_4():
    """图 22-p3-4：基极到地加 10 kΩ 下拉，单片机复位（引脚悬空）时 Q1 保持截止。"""
    with drawing(fontsize=11) as d:
        _relay_drv(d, 0, pin="单片机引脚\n（复位时悬空）", pulldown=("新加下拉\n10 kΩ", EMPH))
    print("[图 22-p3-4] 基极下拉 10 kΩ")
    save_schem(d, P, "22_p3_4_pulldown.png")


def fig_p3_5():
    """图 22-p3-5：练习 2——3.3 V 单片机驱动 12 V / 400 Ω 继电器，两边共地。"""
    ic = (12 - V_SAT) / 400
    ib = (3.3 - V_BE) / 1500
    assert abs(ic * 1e3 - 29.5) < 0.05 and abs(ib * 1e3 - 1.73) < 0.01
    with drawing(fontsize=11) as d:
        r = _relay_drv(d, 0, vcc="+12 V", pin="3.3 V 单片机引脚", rb="$R_B$ 1.5 kΩ",
                       coil="SRD-12VDC\n线圈 400 Ω", ic=f"$I_C$ ≈ {ic*1e3:.1f} mA")
        d += elm.Label().at((r["cx"], -2.6)).label("单片机的地和 12 V 电源的地接在一起（共地）", halign="center", fontsize=10)
    print(f"[图 22-p3-5] 练习 2：I_C = {ic*1e3:.1f} mA，I_B = {ib*1e3:.2f} mA")
    save_schem(d, P, "22_p3_5_ex2_12v.png")


def fig_p3_6():
    """图 22-p3-6：练习 4——12 V 继电器，续流二极管串稳压管 V_Z。"""
    with drawing(fontsize=11) as d:
        r = _relay_drv(d, 0, vcc="+12 V", pin="单片机引脚", rb="$R_B$", q="Q1\n2N3904\n$V_{CEO}$ = 40 V",
                       coil="12 V 继电器\n线圈", diode="zener", dlab="Z1 稳压 $V_Z$ = ?")
        d += elm.Label().at((r["dx"] + 0.35, 0.3)).label("关断时集电极\n钳在 12 + 0.7 + $V_Z$", halign="left", fontsize=10, color=EMPH)
    save_schem(d, P, "22_p3_6_ex4_zener12.png")


if __name__ == "__main__":
    fig_p1_4(); fig_p2_5(); fig_p2_6(); fig_p2_7(); fig_p3_3(); fig_p3_4(); fig_p3_5(); fig_p3_6()
