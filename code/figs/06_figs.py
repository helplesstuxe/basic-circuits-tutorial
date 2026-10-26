"""06 MOS 管开关：本节点全部配图（电路图用 schemdraw，曲线用 matplotlib）。
运行：/workspace/circuits-venv/bin/python code/figs/06_figs.py   → 06-mosfet-switch/img/
仿真模型在 code/06_sim.py（栅极电荷示意模型，量级参考 IRLZ44N 数据手册）。
"""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import matplotlib.pyplot as plt
import figstyle as fs
from schem import drawing, save_schem, elm

_spec = importlib.util.spec_from_file_location("sim21", os.path.join(HERE, "..", "06_sim.py"))
sim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sim)


def gate_drive(d, q, r_label="$R_G$\n100 Ω", src_label="单片机引脚\n0 / 5 V"):
    """在 MOS 管 q 的栅极左边画：单片机方波源 → R_G → 栅极，栅源之间 R_GS 下拉。"""
    g = q.gate
    d += elm.Line().endpoints(g, (g[0] - 0.8, g[1]))
    d += elm.Dot().at((g[0] - 0.8, g[1]))
    d += elm.Resistor().endpoints((g[0] - 0.8, g[1]), (g[0] - 0.8, g[1] - 2.2)).label("$R_{GS}$\n10 kΩ", loc="bottom")
    d += elm.Ground().at((g[0] - 0.8, g[1] - 2.2))
    d += elm.Resistor().endpoints((g[0] - 0.8, g[1]), (g[0] - 3.8, g[1])).label(r_label, loc="top")
    d += elm.SourceSquare().endpoints((g[0] - 3.8, g[1]), (g[0] - 3.8, g[1] - 2.2)).label(src_label, loc="bottom")
    d += elm.Ground().at((g[0] - 3.8, g[1] - 2.2))


def fig_p1_1():
    """低边开关：负载在上，N 沟道 MOS 管在下（源极接地）。"""
    with drawing() as d:
        d += elm.Vdd().at((0, 6)).label("+12 V")
        d += elm.Lamp().endpoints((0, 6), (0, 3.6)).label("负载\n12 V / 3 A", loc="bottom")
        d += elm.Dot().at((0, 3.6))
        q = elm.NFet().theta(0).reverse().anchor("drain").at((0, 3.6)).label("Q1\nN 沟道", loc="right", ofst=(0.3, 0))
        d += q
        d += elm.Ground().at(q.source)
        pin_labels(d, q)
        # 体二极管：MOS 管内部天生自带，阳极在源极 S、阴极在漏极 D（schemdraw 的 NFet 不画它，这里补上）
        bx = q.drain[0] + 2.4
        d += elm.Line().endpoints(q.drain, (bx, q.drain[1]))
        d += elm.Diode().endpoints((bx, q.source[1]), (bx, q.drain[1])).label("体二极管\n（管内自带）", loc="bottom", ofst=0.15)
        d += elm.Line().endpoints((bx, q.source[1]), q.source)
        d += elm.Dot().at(q.source)
        gate_drive(d, q)
    save_schem(d, "06", "06_p1_1_low_side.png")


def pin_labels(d, q, gdx=0.25, right=False):
    """在 MOS 管三个引脚旁标出 G、D、S（right=True 时 D、S 标在引脚右边，避开左边的导线）。"""
    g, dr, so = q.gate, q.drain, q.source
    d += elm.Label().at((g[0] + gdx, g[1] + 0.3)).label("G", fontsize=10)
    if right:
        d += elm.Label().at((dr[0] + 0.3, dr[1] - 0.3)).label("D", fontsize=10)
        d += elm.Label().at((so[0] + 0.3, so[1] - 0.15)).label("S", fontsize=10)
    else:
        d += elm.Label().at((dr[0] - 0.3, dr[1] - 0.15)).label("D", fontsize=10)
        d += elm.Label().at((so[0] - 0.3, so[1] + 0.15)).label("S", fontsize=10)


def fig_p1_2():
    """高边开关：P 沟道 MOS 管在上（源极接 +12 V），负载在下；一只小 N 沟道管 Q2 负责把栅极拉低。"""
    with drawing() as d:
        q1 = elm.PFet().theta(0).reverse().anchor("source").at((0, 6)).label("Q1\nP 沟道", loc="right", ofst=(0.3, 0))
        d += q1
        d += elm.Vdd().at((0, 6)).label("+12 V")
        d += elm.Lamp().endpoints(q1.drain, (q1.drain[0], q1.drain[1] - 2.4)).label("负载", loc="bottom")
        d += elm.Ground().at((q1.drain[0], q1.drain[1] - 2.4))
        g = q1.gate
        gx = g[0] - 1.0
        d += elm.Line().endpoints(g, (gx, g[1]))
        d += elm.Dot().at((gx, g[1]))
        d += elm.Resistor().endpoints((gx, g[1]), (gx, 6)).label("上拉\n10 kΩ", loc="top")
        d += elm.Line().endpoints((gx, 6), (0, 6))
        d += elm.Dot().at((0, 6))
        q2 = elm.NFet().theta(0).reverse().anchor("drain").at((gx, g[1] - 0.9)).label("Q2", loc="right", ofst=(0.2, 0))
        d += elm.Line().endpoints((gx, g[1]), (gx, g[1] - 0.9))
        d += q2
        d += elm.Ground().at(q2.source)
        pin_labels(d, q1, gdx=-0.3, right=True); pin_labels(d, q2)
        gate_drive(d, q2, r_label="1 kΩ", src_label="单片机引脚\n0 / 3.3 V")
    save_schem(d, "06", "06_p1_2_high_side.png")


def fig_p2_2():
    """导通损耗、开关损耗随 PWM 频率的变化（R_G = 100 Ω，5 V 驱动，12 V / 3 A，占空比 50%）。"""
    s = sim.simulate(r_g=100.0)
    e_sw = s["e_on"] + s["e_off"]
    f = np.logspace(2, 5, 300)
    p_cond, p_sw = sim.losses(f, e_sw)
    p_cond = np.full_like(f, p_cond)
    total = p_cond + p_sw
    f_eq = p_cond[0] / e_sw
    print(f"[数值] 每周期开关能量 E_on + E_off = {e_sw*1e6:.1f} μJ；导通损耗 = {p_cond[0]:.3f} W；两者相等的频率 = {f_eq/1e3:.1f} kHz")
    assert abs(p_cond[0] - 3.0 ** 2 * 0.025 * 0.5) < 1e-9
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.loglog(f / 1e3, p_cond, **fs.LS["vin"], label="导通损耗 $I^2 R_{DS(on)} D$")
    ax.loglog(f / 1e3, p_sw, **fs.LS["vout"], label="开关损耗 $(E_{on}+E_{off}) f$")
    ax.loglog(f / 1e3, total, **fs.LS["third"], label="合计")
    fs.ref_v(ax, f_eq / 1e3, f"{f_eq/1e3:.1f} kHz")
    for fk in (1.0, 20.0, 100.0):
        pc, ps = sim.losses(fk * 1e3, e_sw)
        fs.mark(ax, fk, pc + ps, fmt="{:.3f}", unit=" W", dx=-10, dy=8)
    fs.axlabels(ax, "PWM 频率", "kHz", "MOS 管发热", "W")
    ax.legend(loc="upper left", fontsize=8)
    fs.save(fig, "06", "06_p2_2_loss_vs_freq.png")
    return e_sw


def fig_p2_3():
    """感性负载（电机）+ 续流二极管的低边开关。"""
    with drawing() as d:
        d += elm.Vdd().at((0, 6.4)).label("+12 V")
        d += elm.Line().endpoints((0, 6.4), (0, 6.0))
        d += elm.Dot().at((0, 6.0))
        d += elm.Motor().endpoints((0, 6.0), (0, 3.6)).label("直流电机 M", loc="top")
        d += elm.Line().endpoints((0, 6.0), (2.4, 6.0))
        d += elm.Diode().endpoints((2.4, 3.6), (2.4, 6.0)).label("续流二极管\nD1", loc="bottom")
        d += elm.Line().endpoints((2.4, 3.6), (0, 3.6))
        d += elm.Dot().at((0, 3.6))
        q = elm.NFet().theta(0).reverse().anchor("drain").at((0, 3.6)).label("Q1", loc="right", ofst=(0.3, 0))
        d += q
        d += elm.Ground().at(q.source)
        gate_drive(d, q)
    save_schem(d, "06", "06_p2_3_motor_flyback.png")


def fig_p3_3():
    """练习题用：续流二极管接反（阳极接 +12 V、阴极接漏极）的电机低边开关。"""
    with drawing() as d:
        d += elm.Vdd().at((0, 6.4)).label("+12 V")
        d += elm.Line().endpoints((0, 6.4), (0, 6.0))
        d += elm.Dot().at((0, 6.0))
        d += elm.Motor().endpoints((0, 6.0), (0, 3.6)).label("直流电机 M", loc="top")
        d += elm.Line().endpoints((0, 6.0), (2.4, 6.0))
        d += elm.Diode().endpoints((2.4, 6.0), (2.4, 3.6)).label("D1\n（方向接反）", loc="bottom")
        d += elm.Line().endpoints((2.4, 3.6), (0, 3.6))
        d += elm.Dot().at((0, 3.6))
        q = elm.NFet().theta(0).reverse().anchor("drain").at((0, 3.6)).label("Q1", loc="right", ofst=(0.3, 0))
        d += q
        d += elm.Ground().at(q.source)
        gate_drive(d, q)
    save_schem(d, "06", "06_p3_3_flyback_reversed.png")


def fig_p3_1():
    """栅极电阻扫描：10 Ω、100 Ω、1 kΩ 时的开通波形和 20 kHz 下的开关损耗。"""
    rgs = [10.0, 100.0, 1000.0]
    styles = [fs.LS["vin"], fs.LS["vout"], fs.LS["third"]]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    out = []
    for rg, st in zip(rgs, styles):
        s = sim.simulate(r_g=rg, t_on=20e-6, t_end=40e-6)
        us = s["t"] * 1e6
        lab = f"$R_G$ = {rg:g} Ω"
        a1.plot(us, s["v_ds"], **st, label=lab)
        e = s["e_on"] + s["e_off"]
        out.append((rg, s["t_sw_on"], s["t_sw_off"], e, 5.0 / rg))
        print(f"[数值] R_G = {rg:g} Ω：开通 {s['t_sw_on']*1e6:.2f} μs，关断 {s['t_sw_off']*1e6:.2f} μs，"
              f"每周期开关能量 {e*1e6:.2f} μJ，20 kHz 开关损耗 {e*20e3:.3f} W，栅极峰值电流 {5/rg*1e3:.0f} mA")
    fs.axlabels(a1, "时间（开通瞬间）", "μs", "$V_{DS}$", "V")
    a1.set_xlim(-0.2, 8); a1.legend(loc="center right", fontsize=8)
    for i, (rg, ton, toff, e, ipk) in enumerate(out):
        fs.mark(a1, ton * 1e6, 1.2, fmt=f"{ton*1e6:.2f} μs", unit="", dx=3, dy=6 + 12 * (i == 0))
    x = np.arange(len(rgs))
    pw = [e * 20e3 for (_, _, _, e, _) in out]
    a2.bar(x, pw, color=[fs.C["vin"], fs.C["vout"], fs.C["third"]], width=0.55)
    for i, p in enumerate(pw):
        fs.mark(a2, i, p, fmt="{:.3f}", unit=" W", dx=-14, dy=4)
    a2.set_xticks(x, [f"{rg:g} Ω" for rg in rgs])
    fs.axlabels(a2, "栅极电阻 $R_G$", None, "20 kHz 开关损耗", "W")
    a2.set_yscale("log"); a2.set_ylim(0.01, max(pw) * 3)
    assert out[2][1] > 5 * out[1][1], "R_G 加大 10 倍，开通时间也大约变成 10 倍"
    assert out[0][4] > 0.4, "R_G = 10 Ω 时栅极峰值电流达 500 mA，远超单片机引脚能力"
    fs.save(fig, "06", "06_p3_1_rg_sweep.png")


def fig_p3_2():
    """3 A 负载时的导通发热：按数据手册 R_DS(on) 最大值计算（不同驱动电压）。"""
    data = [  # (型号, 驱动电压, R_DS(on) 最大值 mΩ)；None = 手册在这个电压下不保证
        ("IRLZ44N", "10 V", 22), ("IRLZ44N", "5 V", 25), ("IRLZ44N", "4 V", 35),
        ("AO3400A", "4.5 V", 32), ("AO3400A", "2.5 V", 48),
        ("IRF540N", "10 V", 44), ("IRF540N", "3.3 V", None)]
    i_l = 3.0
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    labels, vals = [], []
    for k, (part, v, r) in enumerate(data):
        labels.append(f"{part}\n{v}")
        if r is None:
            ax.bar(k, 0.02, color=fs.C["bad"], width=0.6)
            ax.plot([k], [0.06], marker="x", color=fs.C["bad"], ms=9)
            ax.text(k, 0.12, "手册\n不保证", ha="center", fontsize=8, color=fs.C["bad"])
            print(f"[数值] {part} @ {v}：手册未给 R_DS(on)")
            continue
        p = i_l ** 2 * r / 1e3
        vals.append(p)
        ax.bar(k, p, color=fs.C["vin"] if part != "IRF540N" else fs.C["fb"], width=0.6)
        fs.mark(ax, k, p, fmt="{:.2f}", unit=" W", dx=-12, dy=4)
    ax.set_xticks(range(len(data)), labels, fontsize=8)
    fs.axlabels(ax, "型号与驱动电压", None, "3 A 时导通发热", "W")
    ax.set_ylim(0, 0.55)
    assert abs(i_l ** 2 * 0.025 - 0.225) < 1e-9
    fs.save(fig, "06", "06_p3_2_heat_datasheet.png")


if __name__ == "__main__":
    fig_p1_1(); fig_p1_2(); fig_p2_2(); fig_p2_3(); fig_p3_1(); fig_p3_2(); fig_p3_3()


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


WIRE["fb"] = (fs.C["fb"], "其他连线")

# 实验电路（全部 5 V）：+5 V → 220 Ω → 红色 LED → 漏极 D；源极 S 接地；电位器滑臂 → 100 Ω → 栅极 G；10 kΩ 栅源下拉。
# 下面这些期望读数来自 ngspice 仿真（Infineon IRLZ44N 官方模型 + LTspice 库 TLSV5100RED 红色 LED 模型），
# 数值抄在这里供作图和核对，不在本脚本里重新跑 SPICE。
P4_SPICE = dict(vgs_on=4.9505, vds_on=0.000281, va_on=2.0585, i_on=13.37e-3,   # 滑臂拧到 5 V
                vds_off=3.615, i_off=1.65e-6,                                    # 滑臂拧到 0 V
                vth_01mA=2.090, vth_5mA=2.100)                                   # LED 电流 0.1 mA / 5 mA 时的 V_GS


def fig_p4_1():
    """图 06-p4-1：低边 MOS 管开关的面包板接线（5 V，LED 负载，电位器当「单片机引脚」）。"""
    bb = Breadboard(30, "低边 MOS 管开关面包板俯视图（IRLZ44N，全部 5 V）", rails=("+5 V", "GND", "GND", "+5 V"))
    bb.sip(15, "a", "IRLZ44N", ["G", "D", "S"])                 # 正面（印字面）朝你，左起 G、D、S
    bb.part("b11", "b15", "R_G 100 Ω", "R", lab_side=1)
    bb.part("e15", "f15", "R_GS 10 kΩ", "R", lab_side=-1)       # 跨过中间凹槽：上端是栅极列，下端接地
    bb.wire("j15", "B-15", "gnd")
    bb.wire("e17", "B-17", "gnd", via=[(17.0, -0.2), (18.0, -0.2), (18.0, -6.7)])   # 源极 → 地
    bb.part("d21", "d16", "红色 LED", "L", lab_side=1)          # 阳极 d21，阴极（短脚）d16 = 漏极列
    bb.part("a21", "T+21", "220 Ω", "R", lab_side="r")
    bb.sip(5, "f", "电位器 10 kΩ", ["1", "滑臂", "3"], up=False, fc="#d0d6de", tc="k")
    bb.wire("j5", "B+5", "pos", via=[(4.4, -5.4), (4.4, -7.6)])
    bb.wire("j7", "B-7", "gnd")
    bb.wire("i6", "c11", "sig", via=[(9.2, -4.4), (9.2, 3.6)])
    bb.wire("T+29", "B+29", "pos", via=[(29.0, 9.3), (31.4, 9.3), (31.4, -8.3), (29.0, -8.3)])
    bb.wire("T-28", "B-28", "gnd", via=[(28.0, 7.2), (30.6, 7.2), (30.6, -7.1), (28.0, -7.1)])
    bb.module(-3.2, 9.4, 3.6, 1.4, "5 V 电源\n（USB 稳压模块）")
    bb.wire((0.4, 10.1), "T+1", "pos")
    bb.wire((-1.4, 9.4), "T-2", "gnd", via=[(-1.4, 7.7)])
    bb.probe("e11", "驱动", dy=-0.75)
    bb.probe("c15", "G", dx=-0.8, dy=0.0)
    bb.probe("e16", "D", dx=0.75, dy=0.0)
    bb.probe("b21", "A", dx=0.75)
    bb.note(20.5, -3.0, "黑表笔一律插 GND 轨\n（测 V_DS 时就是源极）\n紫色圈 = 下红表笔的列", va="center")
    bb.note(1.0, -9.6, "步骤 10 慢放电实验：R_GS 换 1 MΩ，再在 d15 与 GND 之间并 10 µF；拔掉 c11 那头的蓝线后计时", ha="left")
    bb.legend()
    bb.save("06", "06_p4_1_breadboard.png")
    print("[接线] IRLZ44N G/D/S 在 a15/a16/a17；R_G b11–b15；R_GS e15–f15，j15→GND；源极 e17→GND；"
          "LED 阳极 d21、阴极 d16；220 Ω a21→+5 V；电位器 f5/f6/f7，滑臂 i6→c11")


def fig_p4_2():
    """图 06-p4-2：没有示波器——栅极经 1 MΩ 慢慢放电，LED 在 V_GS 跌破门限时熄灭（秒级）。"""
    R, C, V0 = 1e6, 10e-6, 5.0
    tau = R * C
    t = np.linspace(0, 25, 1001)
    v = V0 * np.exp(-t / tau)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(t, v, label="栅源电压 V_GS（1 MΩ × 10 µF 放电）", **fs.LS["vin"])
    marks = [(P4_SPICE["vth_01mA"], "SPICE 模型门限 2.09 V", 0.02, "left", -2.2),
             (2.0, "手册上限 2.0 V", 0.98, "right", 0.3), (1.0, "手册下限 1.0 V", 0.98, "right", 0.3)]
    for vt, lab, xr, ha, dx in marks:
        tt = tau * np.log(V0 / vt)
        fs.ref_h(ax, vt, lab, x=xr, ha=ha)
        ax.plot([tt], [vt], "o", color=fs.C["vout"], ms=5, zorder=5)
        ax.text(tt + dx, vt + (0.15 if dx < 0 else -0.32), f"{tt:.1f} s", fontsize=9, color=fs.C["vout"])
        print(f"[数值] 门限 {vt:.2f} V：拔线后约 {tt:.1f} s LED 熄灭（τ = {tau:.0f} s，t = τ·ln(5/V_th)）")
    t_model = tau * np.log(V0 / P4_SPICE["vth_01mA"])
    t_lo, t_hi = tau * np.log(V0 / 2.0), tau * np.log(V0 / 1.0)
    assert abs(t_model - 8.7) < 0.1 and abs(t_lo - 9.2) < 0.1 and abs(t_hi - 16.1) < 0.1
    tau_m = 1 / (1 / R + 1 / 10e6) * C                     # 万用表 10 MΩ 并在栅极上
    tm = tau_m * np.log(V0 / P4_SPICE["vth_01mA"])
    print(f"[数值] 若万用表（10 MΩ）一直并在栅极上：τ 变为 {tau_m:.2f} s，模型门限下约 {tm:.1f} s 熄灭")
    ax.axvspan(t_lo, t_hi, color=fs.C["hi"], alpha=0.25, lw=0)
    ax.text((t_lo + t_hi) / 2, 4.3, "按手册门限范围，\nLED 在这段时间里熄灭", ha="center", fontsize=8.5)
    ax.set_xlim(0, 25); ax.set_ylim(0, 5.4)
    ax.legend(loc="upper right", fontsize=8.5)
    fs.axlabels(ax, "拔掉驱动线后的时间", "s", "栅源电压", "V")
    fs.save(fig, "06", "06_p4_2_slow_discharge.png")


if __name__ == "__main__":
    fig_p4_1(); fig_p4_2()
# ======================= 第 8 轮补电路图（page1–page3：凡正文讲具体电路连接处，附近都要有电路图） =======================
from schem import C as _C
EMPH = _C["third"]      # 强调色（红紫）：新加的东西、要特别注意的元件或电流路径
BAD = _C["bad"]         # 朱红：错误、超限


def fig_p1_3():
    """图 06-p1-3：N 沟道管放在高边（负载接地）——源极跟着负载升高，5 V 单片机开不到底。"""
    with drawing() as d:
        d += elm.Vdd().at((0, 6.4)).label("+12 V")
        q = elm.NFet().theta(0).reverse().anchor("drain").at((0, 6.4)).label("Q1\nN 沟道", loc="right", ofst=(0.3, 0))
        d += q
        pin_labels(d, q)
        d += elm.Dot().at(q.source)
        d += elm.Lamp().endpoints(q.source, (0, q.source[1] - 2.4)).label("负载\n（一端固定接地）", loc="bottom")
        d += elm.Ground().at((0, q.source[1] - 2.4))
        g = q.gate
        d += elm.Resistor().endpoints(g, (g[0] - 3.0, g[1])).label("$R_G$\n100 Ω", loc="top")
        d += elm.SourceSquare().endpoints((g[0] - 3.0, g[1]), (g[0] - 3.0, g[1] - 2.4)).label("单片机引脚\n0 / 5 V", loc="bottom")
        d += elm.Ground().at((g[0] - 3.0, g[1] - 2.4))
        d += elm.Line().endpoints((q.source[0] + 0.15, q.source[1]), (q.source[0] + 2.0, q.source[1])).linestyle(":").color(BAD)
        d += elm.Label().at((q.source[0] + 2.1, q.source[1] + 0.2)).label(
            "源极 S 跟着负载往上升：\n要开到底，栅极须比 S 高几伏，\n即比 12 V 还高几伏",
            fontsize=10, color=BAD, halign="left")
    save_schem(d, "06", "06_p1_3_nmos_high_side.png")


def fig_p2_4():
    """图 06-p2-4：栅极充电的等效电路——R_G 给 C_GS 充电，C_GD 跨在栅极和漏极之间（米勒电容）。"""
    with drawing(fontsize=11) as d:
        d += elm.Vdd().at((0, 8.4)).label("$V_{DD}$ +12 V")
        d += elm.Resistor().endpoints((0, 8.4), (0, 5.8)).label("负载\n12 V / 3 A", loc="bottom")
        d += elm.Line().endpoints((0, 5.8), (0, 4.6))
        q = elm.NFet().theta(0).reverse().anchor("drain").at((0, 4.6)).label("Q1\nIRLZ44N", loc="right", ofst=(0.3, 0))
        d += q
        d += elm.Ground().at(q.source)
        pin_labels(d, q)
        g = q.gate
        gx = g[0] - 1.2
        d += elm.Line().endpoints(g, (gx, g[1]))
        d += elm.Dot().at((gx, g[1]))
        # 管内寄生电容（虚线、强调色）：C_GS 从栅极到源极（地），C_GD 从栅极到漏极
        d += elm.Capacitor().endpoints((gx, g[1]), (gx, g[1] - 2.2)).color(EMPH).linestyle("--").label("$C_{GS}$", loc="bottom", color=EMPH)
        d += elm.Ground().at((gx, g[1] - 2.2))
        d += elm.Line().endpoints((gx, g[1]), (gx, 5.2)).color(EMPH).linestyle("--")
        d += elm.Capacitor().endpoints((gx, 5.2), (-0.0, 5.2)).color(EMPH).linestyle("--").label("$C_{GD}$（米勒电容）", loc="top", color=EMPH)
        d += elm.Dot().at((0, 5.2))
        d += elm.Resistor().endpoints((gx - 3.0, g[1]), (gx - 5.5, g[1])).label("$R_G$ 100 Ω", loc="top")
        d += (w := elm.Line().endpoints((gx - 3.0, g[1]), (gx, g[1])))
        d += elm.CurrentLabelInline(direction="in", ofst=0.3).at(w).label("$I_G$", loc="top")
        d += elm.SourceSquare().endpoints((gx - 5.5, g[1]), (gx - 5.5, g[1] - 2.2)).label("$V_{drv}$\n0 / 5 V", loc="bottom")
        d += elm.Ground().at((gx - 5.5, g[1] - 2.2))
        d += elm.Label().at((gx - 2.0, g[1] - 3.3)).label("虚线电容 = 管子内部的寄生电容（不是外接元件）", fontsize=9.5, color=EMPH)
    save_schem(d, "06", "06_p2_4_gate_equiv.png")


def _motor_off(d, x0, diode, title):
    """关断瞬间的电机低边开关：Q1 画成断开的开关；diode=True 时线圈电流经 D1 续流。"""
    top, mid = 6.0, 3.4
    d += elm.Vdd().at((x0, top + 0.4)).label("+12 V")
    d += elm.Line().endpoints((x0, top + 0.4), (x0, top))
    d += elm.Dot().at((x0, top))
    mot = elm.Motor().endpoints((x0, top), (x0, mid))
    d += mot
    d += elm.Label().at((x0 - 0.9, (top + mid) / 2)).label("电机 M\n（线圈）", fontsize=10.5, halign="right")
    d += elm.Dot().at((x0, mid))
    d += elm.Switch().endpoints((x0, mid), (x0, mid - 2.2))
    d += elm.Label().at((x0 - 0.9, mid - 1.1)).label("Q1 刚关断\n（相当于断开）", fontsize=10.5, halign="right")
    d += elm.Ground().at((x0, mid - 2.2))
    if diode:
        d += elm.Line().endpoints((x0, top), (x0 + 2.4, top))
        dd = elm.Diode().endpoints((x0 + 2.4, mid), (x0 + 2.4, top)).color(EMPH).label("D1", loc="bottom", color=EMPH)
        d += dd
        d += elm.Line().endpoints((x0 + 2.4, mid), (x0, mid))
        d += elm.LoopCurrent([elm.Line().at((x0, top)).to((x0 + 2.4, top)), dd,
                              elm.Line().at((x0 + 2.4, mid)).to((x0, mid)), mot], direction="cw", pad=0.35).color(EMPH)
        d += elm.Label().at((x0 + 0.9, mid - 1.3)).label("线圈电流绕小圈经 D1\n回到上端，漏极 ≈ 12.7 V", fontsize=10, color=EMPH, halign="left")
    else:
        d += elm.Label().at((x0 + 0.5, mid - 1.1)).label("漏极：线圈电流无路可走，\n电压冲到几千伏（理论值）\n→ 击穿 Q1", fontsize=10, color=BAD, halign="left")
        d += elm.Line().endpoints((x0 + 0.1, mid), (x0 + 0.45, mid - 0.6)).linestyle(":").color(BAD)
    d += elm.Label().at((x0, mid - 3.6)).label(title, fontsize=11)


def fig_p2_5():
    """图 06-p2-5：关断瞬间对比——不加续流二极管 / 加续流二极管 D1。"""
    with drawing() as d:
        _motor_off(d, 0.0, False, "(a) 不加续流二极管")
        _motor_off(d, 9.0, True, "(b) 线圈两端反并 D1")
    save_schem(d, "06", "06_p2_5_flyback_compare.png")


def _gate_divider(d, x0, rgs, vgs, title, emph=False):
    col = EMPH if emph else "black"
    d += elm.Battery().up().at((x0, 0)).length(2.4)
    d += elm.Label().at((x0 - 1.1, 1.2)).label("驱动\n5 V")
    d += elm.Line().endpoints((x0, 2.4), (x0, 3.0))
    d += elm.Resistor().endpoints((x0, 3.0), (x0 + 3.0, 3.0)).label("$R_G$ 100 Ω", loc="top")
    d += elm.Dot().at((x0 + 3.0, 3.0))
    d += elm.Resistor().endpoints((x0 + 3.0, 3.0), (x0 + 3.0, 0)).color(col).label(f"$R_{{GS}}$\n{rgs}", loc="bottom", color=col)
    d += elm.Line().endpoints((x0 + 3.0, 0), (x0, 0))
    d += elm.Ground().at((x0 + 1.5, 0))
    d += elm.Line().endpoints((x0 + 3.0, 3.0), (x0 + 4.2, 3.0))
    d += elm.Dot(open=True).at((x0 + 4.2, 3.0)).label(f"G：$V_{{GS}}$ ≈ {vgs}", "right", fontsize=10)
    d += elm.Label().at((x0 + 2.2, -1.4)).label(title, fontsize=10.5)


def fig_p3_4():
    """图 06-p3-4：稳态时栅极不取电流，R_G 和 R_GS 构成分压器。"""
    v1 = 5 * 10e3 / 10.1e3; v2 = 5 * 1e3 / 1.1e3
    print(f"[数值] R_GS = 10 kΩ：V_GS = {v1:.2f} V；R_GS = 1 kΩ：V_GS = {v2:.2f} V")
    assert abs(v1 - 4.95) < 0.01 and abs(v2 - 4.55) < 0.01
    with drawing(fontsize=11) as d:
        _gate_divider(d, 0.0, "10 kΩ", "4.95 V", "(a) 本教程取值：只损失 1%")
        _gate_divider(d, 9.0, "1 kΩ", "4.55 V", "(b) 下拉换成 1 kΩ：损失约 9%", emph=True)
    save_schem(d, "06", "06_p3_4_gate_divider.png")


def _high_side_24(d, x0, fix):
    """24 V 高边开关（练习 5）。fix=True 时在 Q2 漏极和 Q1 栅极之间串 10 kΩ（强调色）。"""
    q1 = elm.PFet().theta(0).reverse().anchor("source").at((x0, 6)).label("Q1\nP 沟道", loc="right", ofst=(0.3, 0))
    d += q1
    d += elm.Label().at((x0 + 0.35, q1.drain[1] + 0.05)).label("栅源极限 ±20 V", fontsize=10, halign="left")
    d += elm.Vdd().at((x0, 6)).label("+24 V")
    d += elm.Lamp().endpoints(q1.drain, (q1.drain[0], q1.drain[1] - 2.4)).label("负载", loc="bottom")
    d += elm.Ground().at((q1.drain[0], q1.drain[1] - 2.4))
    g = q1.gate
    gx = g[0] - 1.0
    d += elm.Line().endpoints(g, (gx, g[1]))
    d += elm.Dot().at((gx, g[1]))
    d += elm.Resistor().endpoints((gx, g[1]), (gx, 6)).label("上拉\n10 kΩ", loc="top")
    d += elm.Line().endpoints((gx, 6), (x0, 6))
    d += elm.Dot().at((x0, 6))
    yq = g[1] - 0.9
    if fix:
        d += elm.Resistor().endpoints((gx, g[1]), (gx, g[1] - 2.4)).color(EMPH).label("新加\n10 kΩ", loc="top", color=EMPH)
        yq = g[1] - 2.4
    else:
        d += elm.Line().endpoints((gx, g[1]), (gx, yq))
    q2 = elm.NFet().theta(0).reverse().anchor("drain").at((gx, yq)).label("Q2", loc="right", ofst=(0.2, 0))
    d += q2
    d += elm.Ground().at(q2.source)
    gate_drive(d, q2, r_label="1 kΩ", src_label="单片机引脚\n0 / 3.3 V")
    txt = "Q2 导通时：Q1 栅极 ≈ 12 V\n$V_{GS}$ ≈ −12 V，不超限" if fix else "Q2 导通时：Q1 栅极 ≈ 0 V\n$V_{GS}$ ≈ −24 V，超过 ±20 V"
    d += elm.Label().at((x0 - 2.5, g[1] - 5.6 if fix else g[1] - 4.4)).label(txt, fontsize=10, color=EMPH if fix else BAD)


def fig_p3_5():
    """图 06-p3-5：练习 5——高边开关改到 24 V（其余与直觉篇高边开关相同）。"""
    with drawing() as d:
        _high_side_24(d, 0.0, False)
    save_schem(d, "06", "06_p3_5_high_side_24v.png")


def fig_p3_6():
    """图 06-p3-6：练习 5 改法一——Q2 漏极与 Q1 栅极之间串 10 kΩ，与上拉分压。"""
    with drawing() as d:
        _high_side_24(d, 0.0, True)
    save_schem(d, "06", "06_p3_6_high_side_fix.png")


if __name__ == "__main__":
    fig_p1_3(); fig_p2_4(); fig_p2_5(); fig_p3_4(); fig_p3_5(); fig_p3_6()
