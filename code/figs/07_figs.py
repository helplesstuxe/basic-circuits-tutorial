"""07 射极跟随器：除 07_sim.py 那两张以外的所有配图。运行：python code/figs/07_figs.py
图上出现的每个数字都由本脚本打印（fs.mark 自动打印；其余用 print）。三极管模型与 code/07_sim.py 相同。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from schem import *
import figstyle as fs

P = "07"
VT, IS, BETA, VCC, I_LIM = 0.02585, 1e-13, 50.0, 12.0, 0.030


def follower(vb, rl, beta=BETA):
    """与 07_sim.py 相同：二分法解发射极电压。返回 (V_o, V_BE, I_E)。"""
    lo, hi = 0.0, vb
    for _ in range(60):
        vo = (lo + hi) / 2
        vbe = VT * np.log(vo / rl * beta / (beta + 1) / IS + 1)
        lo, hi = (vo, hi) if vb - vo > vbe else (lo, vo)
    return vo, vbe, vo / rl


def opamp_follower(d, x, y, vin="$V_i$"):
    """在 (x, y) 处画一个 03 节点那样的电压跟随器，返回运放对象。"""
    d += (op := elm.Opamp(leads=True).right().at((x, y)).anchor("in2"))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    d += elm.Line().up().length(1.2)
    d += elm.Line().right().tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(1.0)
    d += elm.Dot(open=True).label(vin, "left")
    return op


def compare_schem():
    """图 07-p1-1：左边运放直接带 50 Ω，右边运放 → NPN 射极跟随器 → 50 Ω。"""
    with drawing(fontsize=11) as d:
        op = opamp_follower(d, 0, 0, "5 V")
        d += elm.Line().right().at(op.out).length(1.0)
        d += elm.Resistor().down().label("$R_L$ 50 Ω\n要 100 mA", "top")
        d += elm.Ground()
        d += elm.Label().at((op.center[0], op.center[1] - 2.6)).label("① 运放直接带：最多约 30 mA")
        op2 = opamp_follower(d, 9, 0, "5 V")
        d += elm.Line().right().at(op2.out).length(0.8)
        d += (q := elm.BjtNpn().anchor("base").label("NPN\nTIP31", "right", ofst=(0.1, -0.2)))
        d += elm.Line().up().at(q.collector).length(0.4)
        d += elm.Vdd().label("+12 V")
        d += elm.Line().down().at(q.emitter).length(0.6)
        d += elm.Resistor().down().label("$R_L$ 50 Ω", "top")
        d += elm.Ground()
        d += elm.Label().at((op2.center[0] - 0.5, op2.center[1] - 3.6)).label("② 加射极跟随器：运放只出约 1.7 mA")
    print("[图 07-p1-1] 5 V、50 Ω、100 mA、30 mA、+12 V、1.7 mA（基极电流见 07_sim.py 的 1.68 mA）")
    save_schem(d, P, "07_p1_1_compare.png")


def current_bars():
    """图 07-p1-2：负载要的电流 vs 运放能给的电流 vs 跟随器要运放给的电流。"""
    vo, vbe, ie = follower(5.0, 50.0)
    ib = ie / (BETA + 1)
    names = ["50 Ω 负载\n要的电流", "LM358 拉电流\n（典型）", "LM358 拉电流\n（最小）", "加跟随器后\n运放要给的"]
    vals = [5.0 / 50 * 1e3, 30.0, 20.0, ib * 1e3]
    cols = [fs.C["vout"], fs.C["vin"], fs.C["bad"], fs.C["fb"]]
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    bars = ax.bar(names, vals, color=cols, width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f} mA", ha="center", fontsize=9)
        print(f"[图 07-p1-2] {v:.1f} mA")
    fs.axlabels(ax, None, None, "电流", "mA"); ax.set_ylim(0, 120)
    fs.save(fig, P, "07_p1_2_current.png")


def analogy():
    """图 07-p1-3：水塔—阀门类比。"""
    fig, ax = fs.diagram(8, 2.8)
    fs.box(ax, 1.0, 2.1, "水塔\n（电源 12 V）", w=1.6, h=0.8)
    fs.box(ax, 3.6, 2.1, "大阀门\n（三极管）", w=1.6, h=0.8)
    fs.box(ax, 6.6, 2.1, "用水的房子\n（负载）", w=1.8, h=0.8)
    fs.box(ax, 3.6, 0.5, "小手轻拧\n（运放 1.7 mA）", w=2.0, h=0.7)
    fs.arrow(ax, (1.8, 2.1), (2.8, 2.1), "大水流")
    fs.arrow(ax, (4.4, 2.1), (5.7, 2.1), "100 mA 级")
    fs.arrow(ax, (3.6, 0.85), (3.6, 1.7), dashed=True)
    ax.text(5.2, 0.6, "房子水位跟着手的指令走，\n但总比指令低一个台阶（约 0.7 V）", fontsize=9, va="center")
    print("[图 07-p1-3] 12 V、1.7 mA、100 mA、0.7 V")
    fs.save(fig, P, "07_p1_3_analogy.png")


def analysis_schem():
    """图 07-p2-1：标出 V_i、V_BE、V_o、I_B、I_C、I_E、R_L 的分析图。"""
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 0)).label("$V_i$ 输入", "left")
        d += elm.Line().right().length(1.2).label("$I_B$ →", "top")
        d += (q := elm.BjtNpn().anchor("base").label("Q1", "right", ofst=(0.1, -0.2)))
        d += elm.Line().up().at(q.collector).length(0.5).label("$I_C$ ↓", "right")
        d += elm.Vdd().label("$V_{CC}$ 12 V")
        d += elm.Line().down().at(q.emitter).length(1.0).label("$I_E$ ↓", "top")
        d += (je := elm.Dot())
        d += elm.Resistor().down().label("$R_L$", "top")
        d += elm.Ground()
        d += elm.Line().right().at(je.center).length(1.5)
        d += elm.Dot(open=True).label("$V_o$ 输出", "right")
        d += elm.Label().at((q.base[0] - 1.2, q.base[1] - 1.3)).label("$V_{BE}$ ≈ 0.7 V\n（基极比发射极高）")
    print("[图 07-p2-1] V_CC 12 V、V_BE ≈ 0.7 V")
    save_schem(d, P, "07_p2_1_analysis.png")


def loop_schem():
    """图 07-p2-4：运放反馈取自发射极，自动补上 V_BE。"""
    vo, vbe, ie = follower(5.0, 50.0)
    with drawing(fontsize=11) as d:
        d += (op := elm.Opamp(leads=True).right().flip())
        d += elm.Line().left().at(op.in2).length(1.0)
        d += elm.Dot(open=True).label("$V_i$ 5 V", "left")
        d += elm.Line().right().at(op.out).length(0.6).label(f"{5 + vbe:.2f} V", "top")
        d += (q := elm.BjtNpn().anchor("base"))
        d += elm.Line().up().at(q.collector).length(0.4)
        d += elm.Vdd().label("+12 V")
        d += elm.Line().down().at(q.emitter).length(1.6)
        d += (je := elm.Dot())
        d += elm.Resistor().down().label("$R_L$ 50 Ω", "top")
        d += elm.Ground()
        d += elm.Line().right().at(je.center).length(1.2)
        d += elm.Dot(open=True).label("$V_o$ 5.00 V", "right")
        d += elm.Line().left().at(op.in1).length(0.5)
        d += elm.Line().down().toy(je.center)
        d += elm.Line().right().tox(je.center).label("反馈取自发射极", "bottom")
    print(f"[图 07-p2-4] V_i 5 V、运放输出 {5 + vbe:.2f} V、+12 V、50 Ω、V_o 5.00 V")
    save_schem(d, P, "07_p2_4_loop.png")


def power_curve():
    """图 07-p3-1：R_L = 50 Ω 时管耗随输出电压的变化。"""
    vo = np.linspace(0, VCC, 241)
    p = (VCC - vo) * vo / 50.0 * BETA / (BETA + 1)
    k = np.argmax(p)
    v5, _, ie5 = follower(5.0, 50.0)
    p5 = (VCC - v5) * ie5 * BETA / (BETA + 1)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(vo, p, **fs.LS["vout"], label="管耗 $P_C$（负载 50 Ω）")
    fs.ref_h(ax, 0.625, "2N3904 额定 0.625 W（25 °C）", x=0.02, ha="left")
    fs.ref_h(ax, 2.0, "TIP31 不加散热片 2 W", x=0.02, ha="left")
    fs.mark(ax, vo[k], p[k], "{:.2f}", " W", dx=4, dy=4)
    fs.mark(ax, v5, p5, "{:.2f}", " W", dx=6, dy=-14)
    fs.axlabels(ax, "输出电压 $V_o$", "V", "管耗", "W"); ax.set_ylim(0, 2.3)
    ax.legend(loc="center right", fontsize=8)
    print(f"[图 07-p3-1] 最大管耗在 V_o = {vo[k]:.1f} V（V_CC 的一半），{p[k]:.2f} W；V_i 5 V 时 {p5:.2f} W")
    print(f"[温升] TIP31 不加散热片 θ_JA 62.5 °C/W：{p5:.2f} W → 结温比环境高 {p5 * 62.5:.0f} °C；最坏 {p[k]:.2f} W → {p[k] * 62.5:.0f} °C")
    assert abs(vo[k] - VCC / 2) < 0.1 and p5 > 0.625
    fs.save(fig, P, "07_p3_1_power.png")


def pushpull():
    """图 07-p3-2：推挽射极跟随器的交越失真（V_BE 按 0.7 V 常数近似）。"""
    t = np.linspace(0, 0.02, 801)
    vi = fs.sine(t, 100, amp=3.0)
    vo = np.where(vi > 0.7, vi - 0.7, np.where(vi < -0.7, vi + 0.7, 0.0))
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(t * 1e3, vi, **fs.LS["vin"], label="输入 $V_i$")
    ax.plot(t * 1e3, vo, **fs.LS["vout"], label="推挽输出 $V_o$")
    ax.axhspan(-0.7, 0.7, color=fs.C["ref"], alpha=0.15)
    ax.text(0.2, 0.15, "死区 ±0.7 V：两只管子都不导通", fontsize=9)
    k = np.argmax(vi)
    fs.mark(ax, t[k] * 1e3, vo[k], "{:.1f}", " V", dx=8, dy=-14)
    fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-3.6, 3.6)
    ax.legend(loc="upper right", fontsize=8)
    print("[图 07-p3-2] 输入 ±3 V、死区 ±0.7 V")
    fs.save(fig, P, "07_p3_2_pushpull.png")


def beta_table():
    """page3 参数表用：β 不同时基极电流和输出电压。"""
    for b in (25, 50, 100, 300):
        vo, vbe, ie = follower(5.0, 50.0, beta=b)
        print(f"[β 扫描] β = {b:>3}：V_o = {vo:.3f} V，I_B = {ie / (b + 1) * 1e3:.2f} mA")


def examples():
    """page2 例题、动手实验、page3 练习用的数（例题按 V_BE = 0.7 V 常数估算，和正文手算一致）。"""
    def hand(vi, rl, beta, vcc):
        vo = vi - 0.7; ie = vo / rl; ib = ie / (beta + 1); p = (vcc - vo) * ie * beta / (beta + 1)
        return vo, ie, ib, p
    for tag, args in (("例 1", (6.0, 100.0, 50, 12.0)), ("例 2", (3.3, 47.0, 50, 12.0)),
                      ("例 3 / 12 V", (5.7, 50.0, 100, 12.0)), ("例 3 / 7 V", (5.7, 50.0, 100, 7.0)),
                      ("练习 1", (9.0, 20.0, 50, 15.0)), ("练习 2", (2.7, 100.0, 100, 5.0))):
        vo, ie, ib, p = hand(*args)
        print(f"[{tag}] V_i {args[0]} V、R_L {args[1]:.0f} Ω、β {args[2]}、V_CC {args[3]:.0f} V：V_o = {vo:.1f} V，I_E = {ie*1e3:.1f} mA，I_B = {ib*1e3:.2f} mA，P_C = {p:.3f} W")
    print(f"[练习 1] 2.726 W × θ_JA 62.5 °C/W = {2.726 * 62.5:.0f} °C 温升（不加散热片）")
    print(f"[练习 2] 5 V 供电：LM358B 输出最高约 5 − 1.4 = {5 - 1.4:.1f} V，跟随器输出最高约 {5 - 1.4 - 0.7:.1f} V")
    # 动手实验：9 V 供电，1 kΩ 电位器滑片直接接 2N3904 基极（β 取 100），把滑片调到 5 V
    rth = 247.0                                   # 1 kΩ 电位器在 9 V 上调出 5 V 时，滑片的戴维南内阻 = 444 Ω ∥ 556 Ω ≈ 247 Ω
    for rl in (1000.0, 220.0):
        lo, hi = 0.0, 5.0                         # 解：5 V − I_B·R_th − V_BE(I) = V_o
        for _ in range(60):
            vo = (lo + hi) / 2; ie = vo / rl; ib = ie / 101
            vbe = VT * np.log(ie * 100 / 101 / IS + 1)
            lo, hi = (vo, hi) if 5.0 - ib * rth - vo > vbe else (lo, vo)
        vdir = 5.0 * rl / (rl + rth)
        print(f"[实验] R_L = {rl:.0f} Ω：跟随器 V_E ≈ {vo:.2f} V（V_B ≈ {5.0 - ib * rth:.2f} V），管耗 {(9.0 - vo) * ie * 100 / 101:.2f} W；滑片直接接负载只剩 {vdir:.2f} V")


def rout_rin_rb():
    """page2「从两头看」与 page3「基极电阻怎么选」用的数（模型同上，V_OH = 10.5 V 同 07_sim.py）。"""
    v1k, _, i1k = follower(5.0, 1000.0)
    v20, _, i20 = follower(5.0, 20.0)
    r_out = (v1k - v20) / (i20 - i1k)
    print(f"[R_out] 1 kΩ → 20 Ω：I_E {i1k*1e3:.1f} → {i20*1e3:.0f} mA（多 {(i20-i1k)*1e3:.0f} mA），输出降 {(v1k-v20)*1e3:.0f} mV，"
          f"R_out ≈ {r_out:.2f} Ω；V_T·ln({i20/i1k:.0f}) = {VT*np.log(i20/i1k):.3f} V")
    print(f"[R_in] (β + 1)·R_L = {BETA + 1:.0f} × 50 Ω = {(BETA + 1) * 50:.0f} Ω")
    assert 0.3 < r_out < 1.0
    RB, V_OH = 470.0, 10.5                        # TI AN-4 图 8 的基极电阻 R1 = 470 Ω
    for b in (50, 25):
        vo, vbe, ie = follower(5.0, 50.0, beta=b)
        ib = ie / (b + 1); drop = ib * RB
        print(f"[基极电阻] β = {b}：I_B {ib*1e3:.2f} mA × 470 Ω = {drop:.2f} V；反馈不含 R_B 时输出约 {vo:.2f} − {drop:.2f} = {vo - drop:.2f} V；"
              f"反馈取自发射极时运放输出 5 + {vbe:.2f} + {drop:.2f} = {5 + vbe + drop:.2f} V（上限 {V_OH} V）")
        assert 5 + vbe + drop < V_OH


if __name__ == "__main__":
    compare_schem(); current_bars(); analogy(); analysis_schem(); loop_schem(); power_curve(); pushpull(); beta_table(); rout_rin_rb(); examples()

from figstyle import C  # page4 面包板小工具要用的配色

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

    def multi(self, name, hs, label, w=None, h=1.0, fc="#555555", at=None, pinlab_below=False):
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
            if pinlab_below:       # 方块压得很扁时，脚名写在孔的右下方，不压方块
                ax.text(x + 0.18, y - 0.18, k, fontsize=6.5, ha="left", va="top", color="k", zorder=8)
            else:
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

    def legend(self, kinds=("pos", "gnd", "neg", "sig"), names=None):
        from matplotlib.lines import Line2D
        names = names or dict(pos="正电源线（橙）", gnd="0 V 地线（黑）", neg="负电源线（蓝）", sig="信号线（蓝绿）")
        hs = [Line2D([], [], color=BB_WIRE[k], lw=2.4, label=names[k]) for k in kinds]
        self.ax.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, 0.035), ncol=len(hs), fontsize=8,
                       frameon=False)


def bb07(mode):
    """07 page4：9 V 单电源，1 kΩ 电位器分压，2N3904 射极跟随器。
    mode = "follower"：电位器滑片 → 基极，发射极经 RL 接 0 V；mode = "direct"：拿掉三极管，220 Ω 直接挂在滑片上。"""
    bb = Breadboard(ncol=30, rails=dict(tp=("+9 V", "pos"), tn=("0 V", "gnd"), bp=("（不用）", "gnd"), bn=("（不用）", "gnd")))
    bb.wire(bb.ext((-2.0, 11.4), "9 V 电池 正极", "pos"), "tp1", "pos")
    bb.wire(bb.ext((-2.0, 10.0), "9 V 电池 负极（0 V）", "gnd"), "tn2", "gnd")
    # 电位器 RP：三只脚插 e3（端 1）、e4（滑片 W）、e5（端 3）
    bb.multi("RP", {"1": "e3", "W": "e4", "3": "e5"}, "RP 1k", w=2.6, h=0.5, at=(4.0, 5.5), pinlab_below=True)   # 扁方块只占 d、e 两行之间
    bb.wire("a3", "tp3", "pos")                 # 端 1 → +9 V
    bb.wire("a5", "tn5", "gnd")                 # 端 3 → 0 V
    if mode == "follower":
        # 2N3904 平面朝自己：E、B、C 从左到右插 e13、e14、e15
        bb.multi("Q1", {"E": "e13", "B": "e14", "C": "e15"}, "2N3904", w=2.6, h=0.5, at=(14.0, 5.5), pinlab_below=True)
        bb.wire("c4", "c14", "sig")             # 滑片 → 基极
        bb.wire("a15", "tp15", "pos")           # 集电极 → +9 V
        bb.two("RL", "a13", "tn13", "R", "RL", lpos=(0.35, 0.0))
        assert bb.connected("RP.W", "Q1.B") and bb.connected("Q1.C", "tp1") and bb.connected("Q1.E", "RL.1")
        assert bb.connected("RL.2", "tn1") and not bb.connected("Q1.E", "Q1.B")
        bb.probe("b14", "V_B", dx=0.3, dy=0.3)
        bb.probe("b13", "V_E", dx=-0.3, dy=0.3, ha="right")
        bb.probe("c15", "V_C", dx=0.3, dy=0.3)
    else:
        bb.two("RX", "a4", "tn4", "R", "220", lpos=(0.45, 0.1))   # 220 Ω 直接挂在滑片上
        assert bb.connected("RP.W", "RX.1") and bb.connected("RX.2", "tn1")
        bb.probe("c4", "滑片", dx=0.3, dy=0.3)
    assert bb.connected("RP.1", "tp1") and bb.connected("RP.3", "tn1") and not bb.connected("tp1", "tn1")
    bb.legend(("pos", "gnd", "sig"), names=dict(pos="正电源线（橙）", gnd="0 V 地线（黑）", sig="信号线（绿）"))
    print(f"07 p4 面包板（{mode}）：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def p4_breadboards():
    for k, (mode, name) in enumerate((("follower", "07_p4_1_bb_follower.png"), ("direct", "07_p4_2_bb_direct.png"))):
        bb = bb07(mode)
        fs.save(bb.fig, P, name)
        plt.close(bb.fig)
    print("07_figs p4 OK")


if __name__ == "__main__":
    p4_breadboards()


# ======================================================================
# 第 8 轮补图：page1–page3 正文讲到的电路连接（不动上面的图号）
# ======================================================================
HL = C["bad"]          # 强调色：新加的、接错的、要注意的元件


def divider_load_schem():
    """图 07-p1-4：直接用分压器去带 50 Ω 负载。"""
    with drawing(fontsize=11) as d:
        d += elm.Vdd().label("电源")
        d += elm.Resistor().down().label("$R_1$", "top")
        d += (j := elm.Dot().label("空载时 5 V", "left"))
        d += elm.Resistor().down().label("$R_2$", "top")
        d += elm.Ground()
        d += elm.Line().right().at(j.center).length(2.2).color(HL)
        d += elm.Resistor().down().label("负载\n50 Ω", "bottom").color(HL)
        d += elm.Ground().color(HL)
        d += elm.Label().at((j.center.x + 2.6, j.center.y + 0.9)).label("接上 50 Ω 后，它和 $R_2$ 并联，\n电压塌下去", fontsize=10, color=HL, halign="left")
    print("[图 07-p1-4] 5 V、50 Ω")
    save_schem(d, P, "07_p1_4_divider_load.png")


def pot_experiment(d, x0, mode, re="$R_E$\n1 kΩ / 220 Ω", note=None):
    """低压实验：9 V、1 kΩ 电位器滑片调到 5 V。mode="follower" 滑片 → 2N3904 基极；mode="direct" 220 Ω 直接挂滑片。"""
    d += elm.Vdd().at((x0, 0)).label("+9 V")
    d += (pot := elm.Potentiometer().down().at((x0, 0)))
    d += elm.Label().at((x0 - 0.5, -1.5)).label("电位器\n1 kΩ", fontsize=10, halign="right")
    d += elm.Ground()
    d += elm.Line().right().at(pot.tap).length(1.6)
    d += (w := elm.Dot())
    d += elm.Label().at((w.center.x - 0.3, w.center.y + 0.75)).label("滑片 5 V（空载）", fontsize=10)
    if mode == "follower":
        d += elm.Line().right().length(0.8)
        d += (q := elm.BjtNpn().anchor("base").label("2N3904", "right", ofst=(0.1, -0.2)))
        d += elm.Label().at((q.base[0] - 0.1, q.base[1] - 0.45)).label("$V_B$", fontsize=10, color=C["vin"])
        d += elm.Line().up().at(q.collector).length(0.4)
        d += elm.Vdd().label("+9 V")
        d += elm.Line().down().at(q.emitter).length(0.5)
        d += (je := elm.Dot().label("$V_E$", "right"))
        d += elm.Resistor().down().label(re, "bottom")
        d += elm.Ground()
    else:
        d += elm.Line().right().length(1.6).color(HL)
        d += elm.Resistor().down().label("220 Ω\n直接接滑片", "bottom").color(HL)
        d += elm.Ground().color(HL)
    if note:
        d += elm.Label().at((x0 + 1.8, -6.6)).label(note, fontsize=10, color=HL if mode == "direct" else "black")


def pot_schem(name, tag):
    with drawing(fontsize=11) as d:
        pot_experiment(d, 0, "follower", note="(a) 加三极管：1 kΩ 时 $V_E$ 约 4.36 V，220 Ω 时约 4.28 V")
        pot_experiment(d, 10.0, "direct", note="(b) 拿掉三极管：滑片电压掉到约 2.36 V")
    print(f"[{tag}] 9 V、1 kΩ 电位器、5 V、2N3904、1 kΩ/220 Ω、4.36 V、4.28 V、2.36 V")
    save_schem(d, P, name)


def thevenin_beta_schem():
    """图 07-p2-5：软电源推基极时，内阻被除以 β + 1、负载被乘以 β + 1。"""
    with drawing(fontsize=11) as d:
        d += elm.SourceV().up().at((0, -3.0))
        d += elm.Label().at((-0.9, -2.0)).label("$V_s$", fontsize=11)
        d += elm.Line().up().length(0.6)
        d += elm.Resistor().right().length(2.4).label("$R_s$（软电源内阻）", "top").color(HL)
        d += (jb := elm.Dot())
        d += elm.Line().right().length(0.6)
        d += (q := elm.BjtNpn().anchor("base"))
        d += elm.Line().up().at(q.collector).length(0.4)
        d += elm.Vdd().label("$V_{CC}$")
        d += elm.Line().down().at(q.emitter).length(0.5)
        d += (je := elm.Dot())
        d += elm.Resistor().down().label("$R_L$", "top").length(2.0)
        d += elm.Ground()
        d += elm.Line().at((0, -3.0)).down().length(0.2)
        d += elm.Ground()
        d += elm.Line().right().at(je.center).length(1.4)
        d += elm.Dot(open=True).label("$V_o$", "right")
        d += elm.Arrow().at((jb.center.x - 0.1, jb.center.y - 1.6)).to((jb.center.x - 0.1, jb.center.y - 0.2)).color(C["vin"])
        d += elm.Label().at((jb.center.x - 0.3, jb.center.y - 2.2)).label("往右看进基极：\n约 $(\\beta+1)R_L$", fontsize=10, color=C["vin"])
        d += elm.Arrow().at((je.center.x + 1.9, je.center.y - 1.3)).to((je.center.x + 0.9, je.center.y - 0.15)).color(C["vout"])
        d += elm.Label().at((je.center.x + 2.0, je.center.y - 1.8)).label("往回看：约 $R_s/(\\beta+1)$\n再加不到 1 Ω", fontsize=10, color=C["vout"], halign="left")
        d += elm.Label().at((2.6, -4.6)).label("(a) 实际电路", fontsize=11)
        # (b) 从负载往回看的等效电路
        X = 11.5
        d += elm.SourceV().up().at((X, -3.0))
        d += elm.Label().at((X - 0.9, -2.0)).label("$V_s - V_{BE}$", fontsize=11, halign="right")
        d += elm.Line().up().length(0.6)
        d += elm.Resistor().right().length(2.6).label("约 $R_s/(\\beta+1)$", "top").color(HL)
        d += (k := elm.Dot())
        d += elm.Resistor().down().toy(-3.0).label("$R_L$", "bottom")
        d += elm.Line().left().tox(X)
        d += elm.Line().right().at(k.center).length(1.2)
        d += elm.Dot(open=True).label("$V_o$", "right")
        d += elm.Label().at((X + 1.4, -4.6)).label("(b) 从负载往回看的等效", fontsize=11)
    print("[图 07-p2-5] R_s/(β+1)、(β+1)R_L、不到 1 Ω")
    save_schem(d, P, "07_p2_5_thevenin_beta.png")


def base_resistor_schem():
    """图 07-p3-3：基极串 470 Ω，反馈取运放输出（R_B 在环外）与反馈取自发射极对比。"""
    with drawing(fontsize=11) as d:
        for X, loop in ((0.0, False), (12.0, True)):
            if loop:
                d += (op := elm.Opamp(leads=True).right().flip().at((X, 0)).anchor("in2"))
                d += elm.Line().left().at(op.in2).length(1.0)
                d += elm.Dot(open=True).label("$V_i$ 5 V", "left")
            else:
                op = opamp_follower(d, X, 0, "$V_i$ 5 V")
            d += elm.Line().right().at(op.out).length(0.5)
            d += elm.Resistor().right().length(2.0).label("$R_B$ 470 Ω", "top").color(HL)
            d += (q := elm.BjtNpn().anchor("base").label("TIP31", "right", ofst=(0.1, -0.2)))
            d += elm.Line().up().at(q.collector).length(0.4)
            d += elm.Vdd().label("+12 V")
            d += elm.Line().down().at(q.emitter).length(1.6)
            d += (je := elm.Dot())
            d += elm.Resistor().down().label("$R_L$ 50 Ω", "top")
            d += elm.Ground()
            d += elm.Line().right().at(je.center).length(1.2)
            if loop:
                d += elm.Dot(open=True).label("$V_o$ 5.00 V", "right")
                d += elm.Line().left().at(op.in1).length(0.5).color(C["fb"])
                d += elm.Line().down().toy(je.center).color(C["fb"])
                d += elm.Line().right().tox(je.center).label("反馈取自发射极", "bottom", color=C["fb"]).color(C["fb"])
                d += elm.Label().at((op.out[0] + 0.3, op.out[1] - 0.45)).label("约 6.50 V", fontsize=10)
                d += elm.Label().at((X + 3.0, -5.6)).label("(b) 反馈取自发射极：运放自动补上 $R_B$ 的压降", fontsize=11, color=C["fb"])
            else:
                d += elm.Dot(open=True).label("$V_o$ 约 3.5 V", "right")
                d += elm.Label().at((X + 3.0, -5.6)).label("(a) 反馈只取运放自己的输出：$R_B$ 在环外", fontsize=11, color=HL)
    print("[图 07-p3-3] 470 Ω、5 V、+12 V、50 Ω、约 3.5 V、6.50 V、5.00 V（数值见 rout_rin_rb 的打印，β = 50）")
    save_schem(d, P, "07_p3_3_base_resistor.png")


def exercise_schem():
    """图 07-p3-4：练习 1、练习 2 的电路。"""
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 0)).label("$V_i$ 9 V", "left")
        d += elm.Line().right().length(1.2)
        d += (q := elm.BjtNpn().anchor("base").label("TIP31\n不加散热片", "right", ofst=(0.1, -0.2)))
        d += elm.Line().up().at(q.collector).length(0.4)
        d += elm.Vdd().label("$V_{CC}$ 15 V")
        d += elm.Line().down().at(q.emitter).length(0.6)
        d += (je := elm.Dot())
        d += elm.Resistor().down().label("$R_L$ 20 Ω", "top")
        d += elm.Ground()
        d += elm.Line().right().at(je.center).length(1.0)
        d += elm.Dot(open=True).label("$V_o$", "right")
        d += elm.Label().at((1.5, -5.4)).label("(a) 练习 1（β = 50）", fontsize=11)
        op = opamp_follower(d, 8.5, 0, "$V_i$ 2.7 V")
        d += elm.Label().at((op.center[0] - 0.1, op.center[1] + 0.05)).label("LM358\n接 5 V", fontsize=9)
        d += elm.Line().right().at(op.out).length(0.8)
        d += (q := elm.BjtNpn().anchor("base").label("NPN\nβ = 100", "right", ofst=(0.1, -0.2)))
        d += elm.Line().up().at(q.collector).length(0.4)
        d += elm.Vdd().label("+5 V")
        d += elm.Line().down().at(q.emitter).length(0.6)
        d += (je := elm.Dot())
        d += elm.Resistor().down().label("$R_L$ 100 Ω", "top")
        d += elm.Ground()
        d += elm.Line().right().at(je.center).length(1.0)
        d += elm.Dot(open=True).label("$V_o$", "right")
        d += elm.Label().at((10.5, -5.4)).label("(b) 练习 2：全部用 5 V 单电源", fontsize=11)
    print("[图 07-p3-4] 9 V、15 V、20 Ω、TIP31；2.7 V、5 V、100 Ω、β = 100")
    save_schem(d, P, "07_p3_4_exercises.png")


def pushpull_schem():
    """图 07-p3-5：练习 4 的推挽射极跟随器（不加偏置）。"""
    with drawing(fontsize=11) as d:
        d += (qn := elm.BjtNpn().right().anchor("emitter").at((0, 0.3)).label("NPN", "right", ofst=(0.1, 0.2)))
        d += elm.Line().up().at(qn.collector).length(0.4)
        d += elm.Vdd().label("正电源")
        d += (qp := elm.BjtPnp().right().anchor("emitter").at((0, -0.3)).label("PNP", "right", ofst=(0.1, -0.2)))
        d += elm.Line().down().at(qp.collector).length(0.4)
        d += elm.Vss().label("负电源")
        d += elm.Line().at(qn.emitter).to(qp.emitter)
        d += elm.Dot().at((0, 0))
        d += elm.Line().at((0, 0)).right().length(1.6)
        d += (jo := elm.Dot())
        d += elm.Resistor().down().label("$R_L$", "top")
        d += elm.Ground()
        d += elm.Line().right().at(jo.center).length(1.0)
        d += elm.Dot(open=True).label("$V_o$", "right")
        xb = qn.base[0] - 0.8
        d += elm.Line().at(qn.base).left().tox(xb)
        d += elm.Line().down().toy(qp.base[1])
        d += elm.Line().right().tox(qp.base[0])
        d += elm.Dot().at((xb, 0))
        d += elm.Line().at((xb, 0)).left().length(1.4)
        d += elm.Dot(open=True).label("$V_i$\n±3 V 正弦", "left")
        d += elm.Label().at((xb - 0.3, 1.9)).label("两只基极接在一起", fontsize=10, color=C["vin"])
        d += elm.Label().at((0.3, 0.45)).label("发射极接在一起", fontsize=10, color=C["vout"], halign="left")
    print("[图 07-p3-5] ±3 V")
    save_schem(d, P, "07_p3_5_pushpull_schem.png")


def round8():
    divider_load_schem()
    pot_schem("07_p1_5_pot_experiment.png", "图 07-p1-5")
    thevenin_beta_schem()
    pot_schem("07_p2_6_pot_experiment.png", "图 07-p2-6")
    base_resistor_schem()
    exercise_schem()
    pushpull_schem()
    print("07_figs 第 8 轮补图 OK")


if __name__ == "__main__":
    round8()
