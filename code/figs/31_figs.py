"""31 跨阻放大器（TIA）：全部配图。
运行：/workspace/circuits-venv/bin/python code/figs/31_figs.py [p1_1 p4_3 ...]
图上的每个数字都来自 code/31_sim.py（用 importlib 载入并调用它的函数），运行时打印出来。
面包板图用 code/30_bbkit.py 画，同时做「连通检查」（assert 每个节点真的连在一起、不该连的没连上）；
p3_3 的「二极管接反」用 ngspice + TI LMC648x 宏模型现算。SPICE 复核见 spice/31/run.py。
"""
import os, sys, io, contextlib, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
import lab_schem as ls         # 只借用 probe / colnote / lab / title / _pin 这些小工具（不修改它）
import numpy as np
import matplotlib.pyplot as plt


def _load(name, path, quiet=False):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    if quiet:
        with contextlib.redirect_stdout(io.StringIO()):
            sp.loader.exec_module(m)
    else:
        sp.loader.exec_module(m)
    return m


bb = _load("bbkit30", os.path.join(HERE, "..", "30_bbkit.py"))
sim = _load("sim31", os.path.join(HERE, "..", "31_sim.py"), quiet=True)

N = "31"
W = bb.BB_WIRE
CD = sim.CJ0 + sim.C_IN          # 73 pF：BPW34 零偏结电容 + 运放输入电容
VB = sim.vb()


# ======================================================================================
# 连通检查（与 38 节同一写法）
# ======================================================================================
class Net:
    def __init__(self):
        self.p = {}

    @staticmethod
    def strip(h):
        if "-" in h:
            return h.split("-")[0]
        r, c = h[0], int(h[1:])
        return ("top" if r in "abcde" else "bot", c)

    def f(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def join(self, a, b):          # 只用于导线：电阻、电容、二极管两端不算相通
        self.p[self.f(self.strip(a))] = self.f(self.strip(b))

    def same(self, a, b):
        return self.f(self.strip(a)) == self.f(self.strip(b))


def rail_ok(*holes):
    """电源轨每 5 孔一组，第 6、12、18、24、30、36… 列是组间空档，没有孔。"""
    for h in holes:
        if isinstance(h, str) and h[:2] in ("T1", "T2", "B1", "B2") and "-" in h:
            c = int(h.split("-")[1])
            assert c % 6 != 0, f"电源轨孔 {h} 不存在（第 {c} 列是组间空档）"


def part2(ax, a, b, *args, **kw):
    rail_ok(a, b)
    bb.bb_part2(ax, a, b, *args, **kw)


def wire(net, ax, a, b, kind, via=()):
    rail_ok(a, b)
    bb.bb_wire(ax, a, b, kind, via=via)
    net.join(a, b)


def must(net, groups, apart):
    for g in groups:
        for h in g[1:]:
            assert net.same(g[0], h), f"{g[0]} 与 {h} 应该相通"
    for a, b in apart:
        assert not net.same(a, b), f"{a} 与 {b} 不应相通"


# ======================================================================================
# 原理图小工具：单电源 TIA（反相端在上、同相端在下）
# ======================================================================================
def tia(d, x0, y0, rf="R_F", cf="C_F", pd=True, pd_rev=False, vb_lab="V_B", pins=True, opname="U1A",
        cf_dashed=False, vb_div=False, rf_note=None, cf_note=None):
    """(x0, y0) = 反相端节点（N）。返回 dict(n, out, op, pd_bot, plus)。"""
    d += (op := elm.Opamp(leads=True).theta(0).anchor("in1").at((x0 + 1.2, y0)))
    n = (x0, y0)
    d += elm.Line().at(n).to(op.absanchors["in1"])
    d += elm.Dot().at(n)
    o = op.absanchors["out"]
    yt = y0 + 2.6
    d += elm.Line().at(n).to((x0, yt))
    d += elm.Resistor().at((x0, yt)).to((o[0] + 0.6, yt))
    ls.lab(d, ((x0 + o[0] + 0.6) / 2, yt + 0.55), rf if rf_note is None else f"{rf}{rf_note}", ha="center", fs_=10)
    d += elm.Line().at((o[0] + 0.6, yt)).to((o[0] + 0.6, o[1]))
    d += elm.Line().at(o).to((o[0] + 0.6, o[1]))
    d += elm.Dot().at((o[0] + 0.6, o[1]))
    if cf:
        yc = y0 + 4.6
        d += elm.Line().at((x0, yt)).to((x0, yc))
        cap = elm.Capacitor().at((x0, yc)).to((o[0] + 0.6, yc))
        if cf_dashed:
            cap = cap.linestyle("--")
        d += cap
        ls.lab(d, ((x0 + o[0] + 0.6) / 2, yc + 0.6), cf if cf_note is None else f"{cf}{cf_note}", ha="center", fs_=10)
        d += elm.Line().at((o[0] + 0.6, yc)).to((o[0] + 0.6, yt))
        d += elm.Dot().at((x0, yt)); d += elm.Dot().at((o[0] + 0.6, yt))
    p = op.absanchors["in2"]
    xp = x0 - 0.6
    d += elm.Line().at(p).to((xp, p[1]))
    if vb_div:
        d += elm.Dot().at((xp, p[1]))
    else:
        d += elm.Line().at((xp, p[1])).to((xp, p[1] - 0.8))
        d += elm.Dot(open=True).at((xp, p[1] - 0.8))
        ls.lab(d, (xp - 0.25, p[1] - 0.8), vb_lab, ha="right", fs_=10, color=fs.C["fb"])
    pd_bot = None
    if pd:
        xd = x0 - 2.6
        d += elm.Line().at(n).to((xd, y0))
        ph = elm.Photodiode().at((xd, y0 - 3.4)).to((xd, y0)) if not pd_rev else elm.Photodiode().at((xd, y0)).to((xd, y0 - 3.4))
        d += ph
        d += elm.Ground().at((xd, y0 - 3.4))
        pd_bot = (xd, y0 - 3.4)
    if pins:
        ls._pin(d, op.absanchors["in1"], "2", dx=0.3, dy=0.25)
        ls._pin(d, op.absanchors["in2"], "3", dx=0.3, dy=-0.25)
        ls._pin(d, o, "1", dx=-0.3, dy=0.25)
    ls.lab(d, (op.absanchors["center"][0] - 0.25, op.absanchors["center"][1]), opname, ha="center", fs_=9, color=ls.GRAY)
    return dict(n=n, out=(o[0] + 0.6, o[1]), op=op, pd_bot=pd_bot, plus=(xp, p[1]))


def pwr(d, op, top="8", bot="4", vtxt="5 V", note_top=None, note_bot=None):
    vd, vs = op.absanchors["vd"], op.absanchors["vs"]
    d += elm.Line().at(vd).to((vd[0], vd[1] + 0.5))
    d += elm.Vdd().at((vd[0], vd[1] + 0.5)).label(vtxt, fontsize=9)
    d += elm.Line().at(vs).to((vs[0], vs[1] - 0.5))
    d += elm.Ground().at((vs[0], vs[1] - 0.5))
    ls._pin(d, vd, top, dx=0.3, dy=0.25)
    ls._pin(d, vs, bot, dx=0.3, dy=-0.25)
    if note_top:
        ls.colnote(d, (vd[0] + 0.5, vd[1] + 0.6), note_top, "right", ofst=0.0)
    if note_bot:
        ls.colnote(d, (vs[0] + 0.5, vs[1] - 0.6), note_bot, "right", ofst=0.0)


def divider(d, x, ytop, ymid, ybot, n1="RB1 10k", n2="RB2 2.2k", cb="CB 0.1µF", vtxt="5 V"):
    """5 V —RB1— V_B —RB2— 0 V，V_B 再对地并 CB。返回 V_B 点坐标。"""
    d += elm.Vdd().at((x, ytop)).label(vtxt, fontsize=9)
    d += elm.Resistor().at((x, ytop)).to((x, ymid))
    ls.lab(d, (x - 0.4, (ytop + ymid) / 2), n1, ha="right", fs_=9.5)
    d += elm.Dot().at((x, ymid))
    d += elm.Resistor().at((x, ymid)).to((x, ybot))
    ls.lab(d, (x - 0.4, (ymid + ybot) / 2), n2, ha="right", fs_=9.5)
    d += elm.Ground().at((x, ybot))
    if cb:
        d += elm.Line().at((x, ymid)).to((x + 1.4, ymid))
        d += elm.Capacitor().at((x + 1.4, ymid)).to((x + 1.4, ybot))
        d += elm.Ground().at((x + 1.4, ybot))
        ls.lab(d, (x + 1.8, (ymid + ybot) / 2), cb, ha="left", fs_=9.5)
        d += elm.Dot().at((x, ymid))
    return (x, ymid)


# ======================================================================================
# page1
# ======================================================================================
def _pd_arrow(d, x, ytop, ybot, text=None, dx=0.55, ha="left"):
    """天蓝色箭头：光电流方向（器件内部从阴极流向阳极）。"""
    d += elm.Arrow().at((x + dx, ytop)).to((x + dx, ybot)).color(fs.C["cur"]).linewidth(1.4)
    if text:
        ls.lab(d, (x + dx + (0.2 if ha == "left" else -0.2), (ytop + ybot) / 2), text, ha=ha, fs_=9, color=fs.C["cur"])


def p1_1():
    """最小必要知识：光电二极管的两种接法（零偏 / 反偏），天蓝色箭头是光电流。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (-7.6, 7.4), "（a）零偏：两极经电流表直接相连")
        xd = -6.0
        d += elm.Photodiode().at((xd, 0.0)).to((xd, 4.0))
        d += elm.Line().at((xd, 4.0)).to((-2.0, 4.0))
        d += elm.MeterA().endpoints((-2.0, 4.0), (-2.0, 0.0))
        d += elm.Line().at((-2.0, 0.0)).to((xd, 0.0))
        ls.lab(d, (xd - 0.5, 3.6), "阴极 K\n（竖线一侧）", ha="right", fs_=9)
        ls.lab(d, (xd - 0.5, 0.4), "阳极 A", ha="right", fs_=9)
        _pd_arrow(d, xd, 3.2, 0.8, "光电流\n（管内 K→A）")
        ls.lab(d, (-4.0, -1.0), "两端 0 V：C_D 约 70 pF", ha="center", fs_=9.5)
        ls.title(d, (3.0, 7.4), "（b）反偏：阴极接 +5 V，阳极经电流表到 0 V")
        xd = 4.0
        d += elm.Vdd().at((xd, 5.0)).label("+5 V", fontsize=9)
        d += elm.Line().at((xd, 5.0)).to((xd, 4.0))
        d += elm.Photodiode().at((xd, 0.0)).to((xd, 4.0))
        d += elm.MeterA().endpoints((xd, 0.0), (xd, -3.0))
        d += elm.Ground().at((xd, -3.0))
        ls.lab(d, (xd - 0.5, 3.6), "阴极 K", ha="right", fs_=9)
        ls.lab(d, (xd - 0.5, 0.4), "阳极 A", ha="right", fs_=9)
        _pd_arrow(d, xd, 3.2, -2.6, "光电流\n同一方向")
        ls.lab(d, (xd + 2.4, 1.6), "反偏 3 V 时\nC_D 约 25 pF", ha="left", fs_=9.5)
    print(f"[图 31-p1-1] 零偏 C_D {sim.CJ0*1e12:.0f} pF / 反偏 3 V C_D {sim.CJ3*1e12:.0f} pF；天蓝箭头 = 光电流（管内阴极→阳极）")
    save_schem(d, N, "31_p1_1_pd_basics.png")


def p1_2():
    """反偏 + 串电阻 vs 跨阻放大器（两张小原理图并排）。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (-7.0, 10.0), "（a）反偏 + 串 1 MΩ 电阻")
        xd = -5.0
        d += elm.Vdd().at((xd, 5.6)).label("+5 V", fontsize=9)
        d += elm.Line().at((xd, 5.6)).to((xd, 4.6))
        d += elm.Photodiode().at((xd, 1.2)).to((xd, 4.6))
        d += elm.Dot().at((xd, 1.2))
        d += elm.Resistor().at((xd, 1.2)).to((xd, -2.4))
        d += elm.Ground().at((xd, -2.4))
        ls.lab(d, (xd - 0.45, -0.6), "R 1 MΩ", ha="right", fs_=10)
        ls.lab(d, (xd + 0.6, 3.6), "BPW34（含 C_D）", ha="left", fs_=10)
        d += elm.Line().at((xd, 1.2)).to((xd + 1.8, 1.2))
        d += elm.Dot(open=True).at((xd + 1.8, 1.2))
        ls.lab(d, (xd + 2.0, 1.2), "V = I·R\n（取在阳极）", fs_=10, color=fs.C["vout"])
        _pd_arrow(d, xd, 4.2, -2.0, None, dx=-1.6)
        ls.lab(d, (xd - 1.8, 5.0), "光电流", ha="center", fs_=9, color=fs.C["cur"])
        ls.lab(d, (-3.4, -4.6), "V 升高，反偏 5 V − V 就变小：\nC_D 跟着变、还要经 R 充放电", ha="center", fs_=9.5, color=fs.C["bad"])
        ls.title(d, (7.5, 10.0), "（b）跨阻放大器 TIA")
        t = tia(d, 6.0, 4.0, rf="R_F 1 MΩ", cf="C_F", vb_lab="V_B")
        d += elm.Dot(open=True).at((t["out"][0] + 0.8, t["out"][1]))
        d += elm.Line().at(t["out"]).to((t["out"][0] + 0.8, t["out"][1]))
        ls.lab(d, (t["out"][0] + 1.0, t["out"][1]), "V_out", fs_=10, color=fs.C["vout"])
        ls.lab(d, (4.6, 4.45), "N", fs_=10)
        ls.lab(d, (5.0, -1.6), "N 点被反馈钉住：\nC_D 两端电压几乎不变", ha="center", fs_=9.5, color=fs.C["fb"])
    print("[图 31-p1-2] (a) +5 V→阴极，阳极→1 MΩ→0 V，从阳极取 V = I·R；(b) TIA：R_F 1 MΩ ∥ C_F，同相端接偏置 V_B，1/2/3 脚已标")
    save_schem(d, N, "31_p1_2_resistor_vs_tia.png")


def p1_3():
    """同一个光电流阶跃：电阻接法（C_D 70 pF / 25 pF）vs TIA（单极点运放模型）。"""
    rf = 1e6
    t = np.linspace(0, 400e-6, 4001)
    tau, tau3 = rf * sim.CJ0, rf * sim.CJ3
    y_r = 1 - np.exp(-t / tau)
    y_r3 = 1 - np.exp(-t / tau3)
    ts, ys, ov, tr = sim.step(rf, CD, 4.7e-12, tmax=400e-6, n=40001)
    tr_r, tr_r3 = tau * np.log(9), tau3 * np.log(9)
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.plot(t * 1e6, y_r, **fs.LS["third"], label="（a）串 1 MΩ，C_D 按 70 pF（0 V）")
    ax.plot(t * 1e6, y_r3, color=fs.C["third"], ls="--", lw=1.4, label="（a）串 1 MΩ，C_D 按 25 pF（反偏 3 V）")
    ax.plot(ts * 1e6, ys, **fs.LS["vout"], label="（b）TIA：R_F 1 MΩ ∥ 4.7 pF")
    ax.axhline(1, **fs.LS["good"])
    ax.axhline(0.9, **fs.LS["ref"]); ax.text(395, 0.86, "90%", ha="right", fontsize=8.5, color="0.4")
    fs.axlabels(ax, "光照突然变亮之后的时间", "µs", "输出 / 最终值", None)
    ax.set_ylim(-0.05, 1.15)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_title("同样 1 MΩ、同样的光电流阶跃", fontsize=10)
    print(f"[图 31-p1-3] 电阻：τ = {tau*1e6:.1f} µs（70 pF）/ {tau3*1e6:.1f} µs（25 pF），10–90% 上升 {tr_r*1e6:.1f} / {tr_r3*1e6:.1f} µs；"
          f"TIA（4.7 pF）：过冲 {ov:.1f}%，上升 {tr*1e6:.2f} µs")
    assert abs(tau - 70e-6) < 1e-9 and tr < tr_r3 / 5
    fs.save(fig, N, "31_p1_3_speed.png")


def p1_4():
    """单电源下的输出范围：0 V、V_OL、V_B、V_OH、5 V。"""
    fig, ax = plt.subplots(figsize=(7.4, 2.7))
    ax.set_xlim(-0.7, 5.7); ax.set_ylim(0, 3)
    ax.axis("off")
    ax.plot([0, 5], [1.0, 1.0], color="0.3", lw=1.2)
    for v, lab, dx, ha in ((0, "0 V", -0.05, "right"), (sim.VOL, "V_OL\n0.1 V", 0.05, "left"), (VB, f"V_B\n{VB:.2f} V", 0, "center"),
                           (sim.VOH, "V_OH\n4.9 V", -0.05, "right"), (5.0, "5 V", 0.05, "left")):
        ax.plot([v, v], [0.9, 1.1], color="0.3", lw=1.2)
        ax.text(v + dx, 0.8, lab, ha=ha, va="top", fontsize=8.5)
    ax.add_patch(plt.Rectangle((0, 1.12), sim.VOL, 0.35, fc=fs.C["bad"], alpha=0.35, ec="none"))
    ax.add_patch(plt.Rectangle((sim.VOH, 1.12), 5 - sim.VOH, 0.35, fc=fs.C["bad"], alpha=0.35, ec="none"))
    ax.text(0.02, 1.62, "输出到不了", fontsize=8.5, color=fs.C["bad"])
    ax.text(4.98, 1.62, "到不了", fontsize=8.5, color=fs.C["bad"], ha="right")
    ax.annotate("", (sim.VOH, 2.0), (VB, 2.0), arrowprops=dict(arrowstyle="->", color=fs.C["vout"], lw=1.6))
    ax.text((VB + sim.VOH) / 2, 2.15, "光电流 I 越大，输出从 V_B 往上走 I·R_F", ha="center", fontsize=9, color=fs.C["vout"])
    ax.annotate("", (sim.VOL, 2.0), (VB, 2.0), arrowprops=dict(arrowstyle="->", color=fs.C["fb"], lw=1.4))
    ax.text(0.05, 2.45, "电流反着流\n往下走", fontsize=8.5, color=fs.C["fb"])
    ax.set_title("LMC6482 用 5 V 单电源：为什么同相端要垫一个 V_B", fontsize=10)
    print(f"[图 31-p1-4] 0 V、V_OL {sim.VOL} V、V_B {VB:.4f} V、V_OH {sim.VOH} V、5 V")
    fs.save(fig, N, "31_p1_4_range.png")


# ======================================================================================
# page2
# ======================================================================================
def p2_1():
    """单电源 TIA 原理图：电流方向、V_B、引脚号。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (3.0, 9.6), "单电源跨阻放大器（LMC6482 的 A 半边，5 V 供电）")
        t = tia(d, 6.0, 4.0, rf="R_F", cf="C_F", vb_div=True)
        px, py = t["plus"]
        vbp = divider(d, -0.4, 2.2, -0.8, -3.6)
        d += elm.Line().at((px, py)).to((px, -0.8))
        d += elm.Line().at((px, -0.8)).to(vbp)
        ls.lab(d, (px + 0.2, -0.45), "V_B", ha="left", fs_=10, color=fs.C["fb"])
        pwr(d, t["op"])
        d += elm.Line().at(t["out"]).to((t["out"][0] + 1.0, t["out"][1]))
        d += elm.Dot(open=True).at((t["out"][0] + 1.0, t["out"][1]))
        ls.lab(d, (t["out"][0] + 1.2, t["out"][1]), "V_out", fs_=10, color=fs.C["vout"])
        ls.lab(d, (5.7, 4.5), "N", ha="right", fs_=10)
        ls.lab(d, (2.7, 3.5), "BPW34：阴极接 N\n阳极接 0 V", ha="right", fs_=9, color=ls.GRAY)
        xr = (6.0 + t["out"][0]) / 2
        d += elm.Line().at((xr + 0.6, 7.75)).to((xr - 0.6, 7.75)).color(fs.C["cur"]).linewidth(1.6)
        d += elm.Arrowhead().at((xr - 0.6, 7.75)).theta(180).color(fs.C["cur"])
        ls.lab(d, (xr + 0.8, 7.75), "I（全部走 R_F）", ha="left", fs_=9.5, color=fs.C["cur"])
        d += elm.Line().at((4.0, 3.6)).to((4.0, 2.2)).color(fs.C["cur"]).linewidth(1.6)
        d += elm.Arrowhead().at((4.0, 2.2)).theta(-90).color(fs.C["cur"])
        ls.lab(d, (4.2, 2.6), "I", fs_=9.5, color=fs.C["cur"])
    print("[图 31-p2-1] 单电源 TIA：RB1 10k / RB2 2.2k / CB 0.1µF 做 V_B；I 从输出经 R_F 流到 N，再进二极管阴极；引脚 1/2/3/4/8")
    save_schem(d, N, "31_p2_1_tia_schematic.png")


def p2_2():
    """噪声增益 vs 运放能给的增益（GBW/f）：没有 C_F 时两线相交时还在上升。"""
    rf = 1e6
    f = np.logspace(2, 7, 600)
    s = 2j * np.pi * f
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.loglog(f, sim.GBW / f, **fs.LS["vin"], label="运放能给的增益 GBW/f")
    for cf, st, lab in ((0.0, fs.LS["bad"], "电路要的增益，C_F = 0"), (4.7e-12, fs.LS["vout"], "电路要的增益，C_F = 4.7 pF")):
        zf = rf / (1 + s * rf * cf)
        ng = np.abs(1 + zf * s * CD)
        kw = dict(st); kw.pop("markevery", None); kw.pop("marker", None)
        kw["ls"] = "--" if cf == 0 else "-"
        ax.loglog(f, ng, **kw, label=lab + ("（虚线）" if cf == 0 else "（实线）"))
    fp = sim.f_p(rf, CD)
    ax.axvline(fp, **fs.LS["ref"])
    ax.text(fp * 1.1, 0.7, f"f_P ≈ {fp/1e3:.1f} kHz", fontsize=9)
    c = 4.7e-12
    ax.axhline((CD + c) / c, **fs.LS["ref"])
    ax.text(150, (CD + c) / c * 1.25, f"(C_D + C_F)/C_F = {(CD + c)/c:.1f}", fontsize=8.5)
    ax.set_ylim(0.5, 1e4); ax.set_xlim(1e2, 1e7)
    fs.axlabels(ax, "频率", "Hz", "增益（倍）", None)
    ax.legend(fontsize=8.5, loc="upper right")
    ax.set_title("R_F = 1 MΩ，C_D = 73 pF，GBW = 1 MHz", fontsize=10)
    print(f"[图 31-p2-2] f_P = √(GBW/(2πR_F C_D)) = {fp/1e3:.1f} kHz；C_F = 4.7 pF 时高频平台 (C_D+C_F)/C_F = {(CD+c)/c:.2f}")
    fs.save(fig, N, "31_p2_2_noise_gain.png")


def p2_3():
    """阶跃响应：C_F = 0 / 2.2 / 4.7 / 10 pF（单极点模型）。"""
    rf = 1e6
    fig, ax = plt.subplots(figsize=(7.4, 3.3))
    sty = {0.0: fs.LS["bad"], 2.2e-12: fs.LS["third"], 4.7e-12: fs.LS["vout"], 10e-12: fs.LS["fb"]}
    for cf, st in sty.items():
        t, y, ov, tr = sim.step(rf, CD, cf, tmax=120e-6, n=12001)
        kw = dict(st); kw.pop("markevery", None); kw.pop("marker", None)
        ax.plot(t * 1e6, y, **kw, label=f"C_F = {cf*1e12:g} pF：过冲 {ov:.1f}%")
        print(f"[图 31-p2-3] C_F = {cf*1e12:g} pF：过冲 {ov:.1f}%，10–90% 上升 {tr*1e6:.2f} µs")
    ax.axhline(1, **fs.LS["good"])
    fs.axlabels(ax, "时间", "µs", "输出 / 最终值", None)
    ax.set_ylim(-0.1, 2.45)
    ax.legend(fontsize=8.5, loc="upper right", ncol=2)
    ax.set_title("R_F = 1 MΩ，C_D = 73 pF，GBW 1 MHz 单极点运放", fontsize=10)
    fs.save(fig, N, "31_p2_3_step.png")


def p2_4():
    """跨阻的频率响应（|V_out/I| ÷ R_F）。"""
    rf = 1e6
    f = np.logspace(2, 6.3, 800)
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    sty = {0.0: fs.LS["bad"], 4.7e-12: fs.LS["vout"], 10e-12: fs.LS["fb"]}
    from scipy import signal
    for cf, st in sty.items():
        w, h = signal.freqresp(sim.tf(rf, CD, cf), 2 * np.pi * f)
        db = 20 * np.log10(np.abs(h) / rf)
        kw = dict(st); kw.pop("markevery", None); kw.pop("marker", None)
        fb, pk = sim.bw3db(rf, CD, cf)
        ax.semilogx(f, db, **kw, label=f"C_F = {cf*1e12:g} pF：峰值 {pk:+.1f} dB，−3 dB 在 {fb/1e3:.1f} kHz")
        print(f"[图 31-p2-4] C_F = {cf*1e12:g} pF：峰值 {pk:+.1f} dB，−3 dB 带宽 {fb/1e3:.1f} kHz")
    ax.axhline(-3, **fs.LS["ref"])
    fs.axlabels(ax, "频率", "Hz", "|V_out / I| 相对 R_F", "dB")
    ax.set_ylim(-30, 30)
    ax.legend(fontsize=8.5, loc="lower left")
    fs.save(fig, N, "31_p2_4_bode.png")


# ======================================================================================
# page3
# ======================================================================================
def p3_1():
    """扫 C_F：过冲和带宽（1 MΩ，零偏 73 pF 与约 0.9 V 反偏的估计范围之外只画两条：73 pF、28 pF）。"""
    rf = 1e6
    cfs = np.array([0.5, 1, 1.5, 2.2, 3.3, 4.7, 6.8, 10, 15, 22]) * 1e-12
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.2, 3.2))
    for cd, st, lab in ((CD, fs.LS["vout"], "C_D = 73 pF（零偏）"), (sim.CJ3 + sim.C_IN, fs.LS["vin"], "C_D = 28 pF（反偏 3 V）")):
        ovs, bws = [], []
        for cf in cfs:
            _, _, ov, _ = sim.step(rf, cd, cf)
            fb, _ = sim.bw3db(rf, cd, cf)
            ovs.append(ov); bws.append(fb / 1e3)
        a.semilogx(cfs * 1e12, ovs, marker="o", ms=3, **st, label=lab)
        b.semilogx(cfs * 1e12, bws, marker="o", ms=3, **st, label=lab)
        c = sim.cf_opt(rf, cd)
        a.axvline(c * 1e12, color=st["color"], ls=":", lw=0.9)
        print(f"[图 31-p3-1] {lab}：式(5) C_F = {c*1e12:.2f} pF；扫描过冲 " + ", ".join(f"{x*1e12:g}p→{o:.1f}%" for x, o in zip(cfs, ovs)))
        print("            带宽 " + ", ".join(f"{x*1e12:g}p→{v:.1f}kHz" for x, v in zip(cfs, bws)))
    fs.axlabels(a, "C_F", "pF", "阶跃过冲", "%")
    fs.axlabels(b, "C_F", "pF", "−3 dB 带宽", "kHz")
    a.legend(fontsize=8); b.legend(fontsize=8)
    a.set_title("点线：SBOA055A 式 (5) 给的 C_F", fontsize=9.5)
    b.set_title("C_F 越大越稳，但带宽越窄", fontsize=9.5)
    fs.save(fig, N, "31_p3_1_cf_sweep.png")


def p3_2():
    """偏置电流误差 I_B × 1 MΩ 与校准①的 90 mV 信号对比（对数轴）。"""
    names = ["LMC6482", "LM358B", "LM358"]
    typ = [sim.IB_TYP[k] * 1e6 * 1e3 for k in names]
    mx = [sim.IB[k] * 1e6 * 1e3 for k in names]
    sig = VB / sim.RCAL * 1e6 * 1e3
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    x = np.arange(3)
    ax.bar(x - 0.18, typ, 0.34, color=fs.C["vin"], label="典型 I_B × 1 MΩ")
    ax.bar(x + 0.18, mx, 0.34, color=fs.C["bad"], label="最大 I_B × 1 MΩ")
    ax.set_yscale("log"); ax.set_ylim(1e-5, 1e3)
    ax.axhline(sig, **fs.LS["good"]); ax.text(2.45, sig * 1.3, f"校准①信号 {sig:.2f} mV", ha="right", fontsize=8.5)
    for i in range(3):
        ax.text(x[i] - 0.18, typ[i] * 1.4, f"{typ[i]:.2g}", ha="center", fontsize=8)
        ax.text(x[i] + 0.18, mx[i] * 1.4, f"{mx[i]:.3g}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(names)
    ax.set_ylabel("误差电压 / mV")
    ax.legend(fontsize=8, loc="upper left")
    print(f"[图 31-p3-2] 典型 {typ}，最大 {mx}（mV），校准①信号 {sig:.2f} mV")
    fs.save(fig, N, "31_p3_2_ib_error.png")



def p3_3():
    """三种常见的错误接法（只画接法，不给结果）。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (-1.5, 9.8), "（a）示波器探头直接夹 2 脚")
        t = tia(d, 0.0, 4.0, rf="R_F", cf="C_F", pd=False, opname="U1A", pins=True)
        d += elm.Line().at(t["n"]).to((-1.6, 4.0))
        d += elm.Capacitor().at((-1.6, 4.0)).to((-1.6, 1.2)).linestyle("--").color(fs.C["bad"])
        d += elm.Ground().at((-1.6, 1.2))
        ls.lab(d, (-2.0, 2.6), "探头\n输入电容", ha="right", fs_=9, color=fs.C["bad"])
        ls.title(d, (13.0, 9.8), "（b）把 LMC6482 换成 LM358")
        t2 = tia(d, 14.0, 4.0, rf="R_F 1 MΩ", cf="C_F", pd=False, opname="LM358", pins=True)
        d += elm.Line().at((15.9, 4.45)).to((14.7, 4.45)).color(fs.C["bad"])
        d += elm.Arrowhead().at((14.7, 4.45)).theta(180).color(fs.C["bad"])
        ls.lab(d, (14.4, 5.0), "I_B 从 2 脚流出", ha="left", fs_=9, color=fs.C["bad"])
        ls.title(d, (5.5, -3.0), "（c）想用万用表测 10 MΩ 两端的电压")
        y = -6.0
        d += elm.Dot(open=True).at((1.0, y)); ls.lab(d, (0.7, y), "N（2 脚）", ha="right", fs_=10)
        d += elm.Resistor().at((1.0, y)).to((7.0, y))
        ls.lab(d, (4.0, y + 0.55), "R_CAL 10 MΩ", ha="center", fs_=10)
        d += elm.Dot(open=True).at((7.0, y)); ls.lab(d, (7.3, y), "0 V", fs_=10)
        d += elm.Line().at((1.6, y)).to((1.6, y - 2.0)); d += elm.Dot().at((1.6, y))
        d += elm.MeterV().endpoints((1.6, y - 2.0), (6.4, y - 2.0)).color(fs.C["bad"])
        d += elm.Line().at((6.4, y - 2.0)).to((6.4, y)); d += elm.Dot().at((6.4, y))
        ls.lab(d, (4.0, y - 3.2), "万用表（输入电阻约 10 MΩ）", ha="center", fs_=9, color=fs.C["bad"])
    print("[图 31-p3-3] 错误接法：(a) 探头电容并到 N 点；(b) 换 LM358，I_B 从 2 脚流出；(c) 万用表并在 R_CAL 两端")
    save_schem(d, N, "31_p3_3_miswire.png")


def p3_4():
    """Arduino 每 ~100 µs 读一个数 vs 微秒级振荡。"""
    rf = 1e6
    t, y, ov, _ = sim.step(rf, CD, 0.0, tmax=1.2e-3, n=120001)
    fn = sim.f_p(rf, CD)
    ts = np.arange(37e-6, 1.2e-3, sim.T_ADC)
    ys = np.interp(ts, t, y)
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    ax.plot(t * 1e6, y, color=fs.C["bad"], lw=0.8, label="C_F = 0 时的真实输出（单极点模型）")
    ax.plot(ts * 1e6, ys, "o", ms=5, color=fs.C["vin"], label=f"Arduino 每 {sim.T_ADC*1e6:.0f} µs 读到的一个数")
    ax.axhline(1, **fs.LS["good"])
    fs.axlabels(ax, "时间", "µs", "输出 / 最终值", None)
    ax.set_ylim(-0.2, 2.6)
    ax.legend(fontsize=8.5, loc="upper right")
    ax.set_title(f"一次读数之间振荡走了 {sim.T_ADC*fn:.1f} 个周期", fontsize=10)
    print(f"[图 31-p3-4] 振荡约 {fn/1e3:.1f} kHz（周期 {1/fn*1e6:.1f} µs），Arduino 间隔 {sim.T_ADC*1e6:.0f} µs，跨 {sim.T_ADC*fn:.1f} 个周期")
    fs.save(fig, N, "31_p3_4_arduino_slow.png")


# ======================================================================================
# page4：面包板（带连通检查）+ 实验原理图
# ======================================================================================
RAILS = {"T1": ("+5 V（Arduino 5V）", W["pos"]), "T2": ("0 V", W["gnd"]),
         "B1": ("0 V", W["gnd"]), "B2": ("+5 V", W["pos"])}


def arduino_top(ax, x0, y0, w, pins, title="Arduino Uno（USB 线接电脑供电）"):
    """面包板下方的 Arduino：引脚在盒子上沿。返回 {名字: (x, y)}。"""
    ax.add_patch(bb._BbRect((x0, y0), w, 1.6, fc="#b3e5fc", ec="0.3", lw=0.8, zorder=5))
    ax.text(x0 + 0.3, y0 + 0.4, title, ha="left", va="center", fontsize=7.5, zorder=6)
    out = {}
    for name, x in pins:
        ax.add_patch(bb._BbRect((x - 0.25, y0 + 1.3), 0.5, 0.3, fc="0.2", ec="none", zorder=6))
        ax.text(x, y0 + 1.05, name, ha="center", va="center", fontsize=6.5, zorder=6)
        out[name] = (x, y0 + 1.6)
    return out


def ext(ax, xy, hole, kind, via=()):
    """板外（Arduino）引脚 → 面包板孔：只画线，连通检查里单独登记。"""
    rail_ok(hole)
    x1, y1 = bb.bb_xy(hole)
    pts = [xy] + list(via) + [(x1, y1)]
    ax.plot([q[0] for q in pts], [q[1] for q in pts], color=W[kind], lw=2.0, zorder=3, solid_capstyle="round")
    ax.plot(x1, y1, "o", ms=3.5, color=W[kind], zorder=4)


def _common(ax, net):
    """两个阶段共用：电源跳线、芯片、去耦、偏置分压、不用的 B 半边。"""
    wire(net, ax, "T1-1", "B2-1", "pos", via=[(-0.9, 11.6), (-0.9, -3.6)])
    wire(net, ax, "T2-2", "B1-2", "gnd", via=[(-0.4, 10.8), (-0.4, -2.8)])
    bb.bb_dip8(ax, 14, "LMC6482")
    for k in range(4):                          # 芯片引脚本身：1~4 在 f 行，8~5 在 e 行
        net.strip(f"f{14+k}"); net.strip(f"e{14+k}")
    wire(net, ax, "a14", "T1-14", "pos")       # 8 脚 V+
    wire(net, ax, "j17", "B1-17", "gnd")       # 4 脚 V−
    part2(ax, "b14", "T2-13", "C1 0.1µF", kind="box", dy=-0.6, fc="#ffe0b2")
    part2(ax, "a20", "T2-19", "CB 0.1µF", kind="box", dy=0.6, fc="#ffe0b2")
    bb.bb_res(ax, "b20", "b24", "RB1 10k")
    wire(net, ax, "a24", "T1-23", "pos")
    bb.bb_res(ax, "c20", "c26", "RB2 2.2k", dy=-0.55)
    wire(net, ax, "a26", "T2-26", "gnd")
    wire(net, ax, "d20", "g16", "fb", via=[(18.6, 6.0), (18.6, 2.45), (16.0, 2.45)])
    wire(net, ax, "b15", "b16", "fb")          # 7 脚接 6 脚：B 半边接成跟随器
    wire(net, ax, "d17", "e20", "fb")          # 5 脚接 V_B


def _assert_common(net):
    must(net, [["d20", "e20", "d17", "g16", "f16", "i16"], ["b14", "a14", "T1-5"], ["j17", "B1-29", "T2-3"],
               ["b15", "b16"]],
         apart=[("g16", "T1-1"), ("g16", "T2-1"), ("f14", "f15"), ("f15", "f16"), ("f14", "T1-1"), ("f14", "T2-1"),
                ("f15", "T2-1"), ("f15", "T1-1"), ("e15", "e17")])


def _stage1(ax, net):
    """阶段一的全部元件（图 31-p4-1 和图 31-p4-3 共用）。"""
    _common(ax, net)
    bb.bb_res(ax, "h10", "h14", "RF 1M", dy=0.5)
    part2(ax, "i14", "i15", "CF 4.7p", kind="box", dy=-0.55, fc="#c8e6c9")
    wire(net, ax, "j15", "j10", "sig")
    bb.bb_res(ax, "g10", "g4", "RCAL 10M")
    bb.bb_block(ax, ["h3", "h4", "h5"], "", pins=["①", "公共", "②"], fc="#e1bee7", pad=0.3)
    bb._bb_label(ax, 1.5, 1.0, "S1", fs_=7.5)   # 白底标签放在 h1、h2 之间，不压开关脚
    wire(net, ax, "j3", "B1-3", "gnd")
    wire(net, ax, "j5", "B2-5", "pos", via=[(5.0, -2.2), (5.4, -2.2), (5.4, -3.6)])
    pins = arduino_top(ax, 4.0, -8.0, 18.0, [("GND", 7.0), ("5V", 11.0)], title="Arduino Uno（只当 5 V 电源，USB 供电）")
    ext(ax, pins["5V"], "B2-11", "pos"); ext(ax, pins["GND"], "B1-7", "gnd", via=[(7.0, -3.2)])
    bb.bb_probe(ax, "i16", "A", dx=2.0, dy=1.0)
    bb.bb_probe(ax, "g15", "B", dx=1.0, dy=-4.0)
    bb.bb_probe(ax, "g14", "C", dx=-2.0, dy=-4.0)
    bb.bb_probe(ax, "T1-28", "D", dx=0.0, dy=1.0)


def _assert_stage1(net):
    _assert_common(net)
    must(net, [["f15", "h10", "i15", "j15", "j10", "g10"], ["f14", "g14", "h14", "i14"], ["g4", "h4"],
               ["h3", "j3", "B1-1", "T2-1"], ["h5", "j5", "B2-1", "T1-1"]],
         apart=[("f15", "f14"), ("g10", "T1-1"), ("f15", "f16"), ("g15", "B1-1"), ("g4", "g10"),
                ("h4", "h3"), ("h4", "h5"), ("h3", "h5")])


def p4_1():
    """阶段一：直流校准（R_F 1 MΩ ∥ C_F 4.7 pF，R_CAL 10 MΩ 经拨动开关 S1 接 0 V 或 +5 V）。"""
    net = Net()
    fig, ax = bb.bb_board(cols=30, rails=RAILS, figsize=(10, 6.8))
    ax.set_ylim(-8.3, 12.7)
    _stage1(ax, net)
    _assert_stage1(net)
    ax.text(15.5, -5.0, "S1 拨向 ①（第 3 列）：RCAL 下端接 0 V；拨向 ②（第 5 列）：接 +5 V", ha="center", fontsize=8, color=fs.C["fb"])
    print("[图 31-p4-1] 阶段一面包板：U1 第 14～17 列；RF 1M h10–h14，CF 4.7p i14–i15，RCAL 10M g10–g4；"
          "S1 h3/h4/h5，j3→0 V，j5→+5 V；连通检查通过")
    fs.save(fig, N, "31_p4_1_bb_stage1.png")


def _lab_core(d, rf, cf, title):
    ls.title(d, (2.0, 10.6), title)
    t = tia(d, 6.0, 4.0, rf=rf, cf=cf, pd=False, vb_div=True, opname="U1A")
    px, py = t["plus"]
    vbp = divider(d, -2.4, 2.2, -0.8, -3.6)
    d += elm.Line().at((px, py)).to((px, -0.8)); d += elm.Line().at((px, -0.8)).to(vbp)
    ls.colnote(d, (0.3, -0.8), "第 20 列（V_B 结点）", "top", ofst=0.2)
    op = t["op"]
    vd, vs = op.absanchors["vd"], op.absanchors["vs"]
    d += elm.Line().at(vd).to((vd[0], vd[1] + 0.6))
    d += elm.Vdd().at((vd[0], vd[1] + 0.6)).label("5 V", fontsize=9)
    xc = 13.0                                   # 去耦电容单独画：V+（8 脚）—C1—0 V
    d += elm.Vdd().at((xc, 9.0)).label("V+（8 脚）", fontsize=9)
    d += elm.Capacitor().at((xc, 9.0)).to((xc, 7.2)); d += elm.Ground().at((xc, 7.2))
    ls.lab(d, (xc + 0.45, 8.1), "C1 0.1µF\n（紧贴 8 脚，b14→0 V 轨）", fs_=9)
    d += elm.Line().at(vs).to((vs[0], vs[1] - 0.5)); d += elm.Ground().at((vs[0], vs[1] - 0.5))
    ls._pin(d, vd, "8", dx=0.3, dy=0.25); ls._pin(d, vs, "4", dx=0.3, dy=-0.25)
    o = t["out"]
    d += elm.Line().at(o).to((o[0] + 1.2, o[1])); d += elm.Dot(open=True).at((o[0] + 1.2, o[1]))
    ls.probe(d, (o[0] + 0.6, o[1]), "C", dx=0.0, dy=-1.2)
    ls.colnote(d, (o[0] + 1.4, o[1]), "第 14 列（1 脚）", "right")
    ls.probe(d, t["n"], "B", dx=-0.8, dy=-0.9)
    ls.probe(d, (px, -0.8), "A", dx=0.9, dy=-0.6)
    ls.colnote(d, (px, 1.0), "第 16 列（3 脚）", "right")
    # 不用的 B 半边：跟随器
    d += (ub := elm.Opamp(leads=True).theta(0).anchor("in2").at((13.0, -3.0)))
    d += elm.Line().at(ub.absanchors["in2"]).to((12.0, -3.0))
    ls.lab(d, (11.8, -3.0), "V_B", ha="right", fs_=10, color=fs.C["fb"])
    uo = ub.absanchors["out"]
    d += elm.Line().at(uo).to((uo[0] + 0.5, uo[1])); d += elm.Line().at((uo[0] + 0.5, uo[1])).to((uo[0] + 0.5, uo[1] + 2.1))
    d += elm.Line().at((uo[0] + 0.5, uo[1] + 2.1)).to((ub.absanchors["in1"][0] - 0.6, uo[1] + 2.1))
    d += elm.Line().at((ub.absanchors["in1"][0] - 0.6, uo[1] + 2.1)).to((ub.absanchors["in1"][0] - 0.6, ub.absanchors["in1"][1]))
    d += elm.Line().at((ub.absanchors["in1"][0] - 0.6, ub.absanchors["in1"][1])).to(ub.absanchors["in1"])
    ls._pin(d, ub.absanchors["in1"], "6", dx=0.3, dy=0.25); ls._pin(d, ub.absanchors["in2"], "5", dx=0.3, dy=-0.25)
    ls._pin(d, uo, "7", dx=-0.3, dy=0.25)
    ls.lab(d, (ub.absanchors["center"][0] - 0.25, ub.absanchors["center"][1]), "U1B", ha="center", fs_=9, color=ls.GRAY)
    ls.lab(d, (13.5, -5.4), "不用的半边接成跟随器（不悬空）", ha="left", fs_=9, color=ls.GRAY)
    return t


def p4_2():
    with drawing(fontsize=11) as d:
        t = _lab_core(d, "RF 1 MΩ", "CF 4.7 pF", "阶段一：直流校准（U1 = LMC6482，Arduino 只当 5 V 电源）")
        n = t["n"]
        d += elm.Line().at(n).to((3.6, 4.0))
        d += elm.Resistor().at((3.6, 4.0)).to((3.6, 1.6))
        ls.lab(d, (3.2, 2.8), "RCAL\n10 MΩ", ha="right", fs_=10)
        d += (sw := elm.SwitchSpdt2().at((3.6, 1.6)).down().flip().anchor("a"))   # 画在①（正文第 1 步要求先拨到①）
        ls.lab(d, (3.0, 1.3), "S1", ha="right", fs_=10, color=fs.C["fb"])
        b_, c_ = sw.absanchors["b"], sw.absanchors["c"]
        lo, hi = (b_, c_) if b_[0] < c_[0] else (c_, b_)
        d += elm.Line().at(lo).to((lo[0], lo[1] - 0.5)); d += elm.Ground().at((lo[0], lo[1] - 0.5))
        ls.lab(d, (lo[0] - 0.25, lo[1] - 0.3), "①", ha="right", fs_=10)
        d += elm.Line().at(hi).to((hi[0] + 0.7, hi[1]))
        d += elm.Vdd().at((hi[0] + 0.7, hi[1])).label("+5 V", fontsize=9)
        ls.lab(d, (hi[0] + 0.1, hi[1] - 0.45), "②", ha="left", fs_=10)
        ls.colnote(d, (4.4, 4.0), "第 15 列（2 脚）→ j15 跳到第 10 列", "top", ofst=1.3)
    print("[图 31-p4-2] 阶段一原理图：RF 1 MΩ ∥ CF 4.7 pF，RCAL 10 MΩ 从 N 经 S1 接 0 V（①）或 +5 V（②），V_B 分压 10k/2.2k，C1 去耦，U1B 跟随器；测量点 A/B/C")
    save_schem(d, N, "31_p4_2_lab_stage1.png")


def p4_3():
    """第 7 步：在阶段一的板子空位上加「反偏 + 串电阻」小演示（第 20～24 列下半边）。"""
    net = Net()
    fig, ax = bb.bb_board(cols=30, rails=RAILS, figsize=(10, 6.8))
    ax.set_ylim(-8.3, 12.7)
    _stage1(ax, net)
    bb.bb_res(ax, "h20", "h22", "RS 1M", dy=0.5)
    part2(ax, "i22", "i24", "BPW34", kind="diode", dy=-0.6)
    wire(net, ax, "j20", "B1-20", "gnd")
    wire(net, ax, "j24", "B2-25", "pos", via=[(24.0, -2.2), (25.0, -2.2), (25.0, -3.6)])
    bb.bb_probe(ax, "g22", "E", dx=1.6, dy=-0.2)
    _assert_stage1(net)
    must(net, [["h22", "i22", "g22"], ["i24", "j24", "B2-1"], ["h20", "j20", "B1-1"]],
         apart=[("g22", "B1-1"), ("g22", "B2-1"), ("g22", "f16"), ("g22", "g15")])
    ax.add_patch(bb._BbRect((19.4, -1.5), 5.2, 3.0, fc="none", ec=fs.C["hi"], lw=1.6, ls="--", zorder=2))
    ax.text(22.0, -5.0, "第 20～24 列下半边是新加的 4 样东西；其余是阶段一原样不动", ha="center", fontsize=8, color=fs.C["fb"])
    print("[图 31-p4-3] 第 7 步面包板：RS 1M h20–h22，BPW34 阳极 i22、阴极 i24，j20→0 V，j24→+5 V；E = 第 22 列；连通检查通过")
    fs.save(fig, N, "31_p4_3_bb_series.png")


def p4_4():
    """第 7 步原理图：+5 V → BPW34 阴极，阳极（E）→ RS 1 MΩ → 0 V，万用表并在 RS 上。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (-1.0, 7.2), "第 7 步：反偏 + 串电阻（不用运放）")
        xd = 0.0
        d += elm.Vdd().at((xd, 6.0)).label("+5 V（第 24 列 → B2）", fontsize=9)
        d += elm.Line().at((xd, 6.0)).to((xd, 5.0))
        d += elm.Photodiode().at((xd, 1.6)).to((xd, 5.0))
        ls.lab(d, (xd - 0.5, 4.6), "阴极 K（i24）", ha="right", fs_=9)
        ls.lab(d, (xd - 0.5, 2.0), "阳极 A（i22）", ha="right", fs_=9)
        _pd_arrow(d, xd, 4.6, 2.0, "光电流", dx=0.6)
        d += elm.Dot().at((xd, 1.6))
        d += elm.Resistor().at((xd, 1.6)).to((xd, -2.0))
        ls.lab(d, (xd - 0.45, -0.2), "RS 1 MΩ\n（h20–h22）", ha="right", fs_=9.5)
        d += elm.Ground().at((xd, -2.0))
        d += elm.Line().at((xd, 1.6)).to((3.0, 1.6))
        d += elm.MeterV().endpoints((3.0, 1.6), (3.0, -2.0))
        d += elm.Line().at((3.0, -2.0)).to((xd, -2.0))
        ls.lab(d, (3.6, -0.2), "万用表\n（输入约 10 MΩ，\n和 RS 并联）", ha="left", fs_=9)
        ls.probe(d, (1.5, 1.6), "E", dx=0.0, dy=0.9)
    print("[图 31-p4-4] 第 7 步原理图：+5 V→BPW34 阴极，阳极 E→RS 1 MΩ→0 V；万用表 E 对 0 V")
    save_schem(d, N, "31_p4_4_series.png")


def p4_5():
    """阶段二：BPW34 + LED；LM358 一半做慢速/快速方波振荡器（24 节同一电路），另一半做跟随器去推 LED；按钮做快边沿。"""
    net = Net()
    fig, ax = bb.bb_board(cols=48, rails=RAILS, figsize=(17, 8.2))
    ax.set_ylim(-8.3, 12.7)
    _common(ax, net)
    bb.bb_res(ax, "h10", "h14", "RF 47k", dy=0.5)
    part2(ax, "i14", "i15", "CF 27p", kind="box", dy=-0.55, fc="#c8e6c9")
    wire(net, ax, "j15", "j10", "sig")
    part2(ax, "i8", "i10", "BPW34", kind="diode", dy=-0.6)
    wire(net, ax, "j8", "B1-8", "gnd")
    bb.bb_res(ax, "h2", "h5", "RLED 1k", dy=0.55)
    part2(ax, "g5", "g7", "LED", kind="led", dy=0.55, fc="#ff8a80")
    wire(net, ax, "j7", "B1-7", "gnd")
    # U2 = LM358：B 半边（上）做振荡器，A 半边（下）做跟随器
    bb.bb_dip8(ax, 34, "LM358")
    wire(net, ax, "a34", "T1-34", "pos")
    wire(net, ax, "j37", "B1-37", "gnd")
    part2(ax, "b34", "T2-32", "C2 0.1µF", kind="box", dy=-0.6, fc="#ffe0b2")
    wire(net, ax, "d35", "d31", "out")                       # 7 脚（振荡器输出）→ 第 31 列
    bb.bb_res(ax, "c31", "c36", "R 10k", dy=0.5)             # 定时电阻：输出 → 6 脚
    part2(ax, "a36", "T2-35", "C 100n", kind="box", dy=0.6, fc="#ffe0b2")
    bb.bb_res(ax, "b31", "b37", "Rc 10k", dy=0.5)
    bb.bb_res(ax, "c37", "c41", "Ra 10k", dy=-0.55)
    wire(net, ax, "a41", "T1-41", "pos")
    wire(net, ax, "d37", "d43", "fb")
    bb.bb_res(ax, "c43", "c47", "Rb 10k", dy=0.5)
    wire(net, ax, "a47", "T2-47", "gnd")
    wire(net, ax, "e31", "f31", "out")                       # 振荡器输出过隔离槽
    wire(net, ax, "i31", "i36", "out")                       # → 3 脚（跟随器同相端）
    wire(net, ax, "g34", "g35", "fb")                        # 1 脚接 2 脚：跟随器
    wire(net, ax, "j34", "j2", "sig", via=[(34.0, -2.3), (2.0, -2.3)])   # 跟随器输出 → RLED
    # 按钮：四脚轻触开关跨隔离槽，只用对角两脚 e30、f28
    bb.bb_block(ax, ["e28", "e30", "f28", "f30"], "按钮 S2", fc="#e1bee7", pad=0.3)
    wire(net, ax, "a30", "T1-29", "pos")
    x0, y0 = bb.bb_xy("j28")
    ax.plot([x0, x0], [y0, y0 - 0.6], ls="--", color=W["sig"], lw=1.6, zorder=3)
    ax.plot(x0, y0, "o", ms=4, mfc="white", mec=W["sig"], zorder=4)
    ax.text(28.0, -5.0, "按钮模式（第 8 步、第 10 步③）：\n断电时把蓝线右端从 j34 改插 j28", ha="center", fontsize=7.5, color=fs.C["bad"])
    pins = arduino_top(ax, 4.0, -8.0, 18.0, [("GND", 6.0), ("5V", 11.0)], title="Arduino Uno（只当 5 V 电源，USB 供电）")
    ext(ax, pins["5V"], "B2-11", "pos"); ext(ax, pins["GND"], "B1-5", "gnd", via=[(5.0, -3.2)])
    ax.add_patch(bb._BbRect((1.4, -1.6), 10.0, 4.3, fc="none", ec="0.35", lw=1.2, ls="--", zorder=2))
    ax.text(1.6, 2.4, "遮光盒罩住虚线框", ha="left", va="center", fontsize=7, color="0.3")
    bb.bb_probe(ax, "i16", "A", dx=2.0, dy=1.0)
    bb.bb_probe(ax, "g15", "B", dx=1.2, dy=-3.3)
    bb.bb_probe(ax, "g14", "C", dx=-1.6, dy=-3.3)
    bb.bb_probe(ax, "T1-28", "D", dx=0.0, dy=1.0)
    bb.bb_probe(ax, "a31", "F", dx=-1.0, dy=1.0)
    bb.bb_probe(ax, "h34", "G", dx=2.2, dy=-2.3)
    _assert_common(net)
    must(net, [["f15", "h10", "i15", "j15", "j10", "i10"], ["f14", "g14", "h14", "i14"], ["i8", "j8", "j7", "g7", "B1-1"],
               ["g5", "h5"],
               ["e35", "d35", "d31", "c31", "b31", "e31", "f31", "i31", "i36", "f36", "a31"],     # 振荡器输出 o
               ["e36", "c36", "a36"],                                                             # 反相端 n
               ["e37", "d37", "c37", "b37", "d43", "c43"],                                       # 同相端 p
               ["f34", "g34", "g35", "f35", "j34", "j2", "h2", "h34"],                            # 跟随器输出
               ["e34", "a34", "T1-1", "a41", "a30", "e30"], ["f37", "j37", "B1-1", "T2-1", "a47"],
               ["f28", "j28"]],
         apart=[("e35", "f34"), ("e36", "e37"), ("e35", "e36"), ("f34", "f36"), ("T1-1", "T2-1"),
                ("j2", "T1-1"), ("j2", "e35"), ("i10", "i8"), ("g5", "g7"), ("h2", "h5"),
                ("f28", "e30"), ("f28", "j2"), ("c41", "c37"), ("c43", "c47"), ("b31", "b37"), ("c31", "c36"),
                ("g4", "f15")])
    print("[图 31-p4-5] 阶段二面包板：RF 47k、CF 27p；BPW34 阳极 i8、阴极 i10；RLED h2–h5，LED 阳极 g5、阴极 g7，j7→0 V；"
          "U2 LM358 第 34～37 列：7 脚振荡器（R c31–c36，C a36→0 V，Rc b31–b37，Ra c37–c41→+5 V，Rb c43–c47→0 V），"
          "1 脚跟随器 → j34→j2；按钮 e30/f28；F=a31，G=h34；连通检查通过")
    fs.save(fig, N, "31_p4_5_bb_stage2.png")


def p4_6():
    with drawing(fontsize=11) as d:
        t = _lab_core(d, "RF 47 kΩ", "CF 27 pF", "阶段二（一）：测光的跨阻放大器")
        n = t["n"]
        d += elm.Line().at(n).to((3.6, 4.0))
        d += elm.Photodiode().at((3.6, 0.6)).to((3.6, 4.0))
        d += elm.Ground().at((3.6, 0.6))
        ls.lab(d, (2.9, 2.0), "BPW34\n阴极 i10\n阳极 i8", ha="right", fs_=9)
        _pd_arrow(d, 3.6, 3.6, 1.0, "光电流", dx=0.55)
    print("[图 31-p4-6] 阶段二 TIA 原理图：RF 47 kΩ ∥ CF 27 pF，BPW34 阴极接 N、阳极接 0 V，天蓝箭头 = 光电流")
    save_schem(d, N, "31_p4_6_lab_tia.png")


def p4_7():
    """阶段二（二）：U2B 方波振荡器（24 节同款）→ U2A 跟随器 → RLED → LED；按钮另给一个快边沿。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (0.0, 8.6), "阶段二（二）：让 LED 一亮一灭（U2 = LM358）")
        d += (op := elm.Opamp(leads=True, flip=True).theta(0).anchor("in1").at((1.2, 0.0)))
        n_, p_, o = op.absanchors["in1"], op.absanchors["in2"], op.absanchors["out"]
        xo = o[0] + 0.6
        d += elm.Line().at(o).to((xo, o[1])); d += elm.Dot().at((xo, o[1]))
        # 反相端 n：R 回到输出，C 到 0 V
        xn = n_[0] - 0.6
        d += elm.Line().at(n_).to((xn, n_[1])); d += elm.Dot().at((xn, n_[1]))
        d += elm.Line().at((xn, n_[1])).to((xn, n_[1] - 2.7))
        d += elm.Resistor().at((xn, n_[1] - 2.7)).to((xo, n_[1] - 2.7))
        ls.lab(d, ((xn + xo) / 2, n_[1] - 3.35), "R 10 kΩ（c31–c36）", ha="center", fs_=9)
        d += elm.Line().at((xo, n_[1] - 2.7)).to((xo, o[1]))
        d += elm.Line().at((xn, n_[1])).to((xn - 1.0, n_[1]))
        d += elm.Capacitor().at((xn - 1.0, n_[1])).to((xn - 1.0, n_[1] - 2.6))
        d += elm.Ground().at((xn - 1.0, n_[1] - 2.6))
        ls.lab(d, (xn - 1.45, n_[1] - 1.3), "C 100 nF\n（a36 → 0 V）", ha="right", fs_=9)
        # 同相端 p：Ra 到 +5 V，Rb 到 0 V，Rc 回到输出
        xp = p_[0] - 0.6
        d += elm.Line().at(p_).to((xp, p_[1])); d += elm.Dot().at((xp, p_[1]))
        d += elm.Line().at((xp, p_[1])).to((xp, p_[1] + 2.7))
        d += elm.Resistor().at((xp, p_[1] + 2.7)).to((xo, p_[1] + 2.7))
        ls.lab(d, ((xp + xo) / 2, p_[1] + 3.3), "Rc 10 kΩ（b31–b37）", ha="center", fs_=9)
        d += elm.Line().at((xo, p_[1] + 2.7)).to((xo, o[1]))
        xa = xp - 4.0
        d += elm.Line().at((xp, p_[1])).to((xa, p_[1])); d += elm.Dot().at((xa, p_[1]))
        d += elm.Resistor().at((xa, p_[1])).to((xa, p_[1] + 3.0))
        d += elm.Vdd().at((xa, p_[1] + 3.0)).label("+5 V", fontsize=9)
        ls.lab(d, (xa - 0.45, p_[1] + 1.3), "Ra 10 kΩ", ha="right", fs_=9)
        d += elm.Resistor().at((xa, p_[1])).to((xa, n_[1] - 3.4))
        d += elm.Ground().at((xa, n_[1] - 3.4))
        ls.lab(d, (xa - 0.45, n_[1] - 1.4), "Rb 10 kΩ", ha="right", fs_=9)
        ls._pin(d, n_, "6", dx=0.3, dy=-0.25); ls._pin(d, p_, "5", dx=0.3, dy=0.25); ls._pin(d, o, "7", dx=-0.3, dy=0.25)
        ls.lab(d, (op.absanchors["center"][0] - 0.25, op.absanchors["center"][1]), "U2B", ha="center", fs_=9, color=ls.GRAY)
        ls.probe(d, (xo, o[1]), "F", dx=0.6, dy=0.9)
        # 跟随器 U2A
        d += (fo := elm.Opamp(leads=True).theta(0).anchor("in2").at((xo + 2.4, o[1])))
        d += elm.Line().at((xo, o[1])).to(fo.absanchors["in2"])
        fi, fout = fo.absanchors["in1"], fo.absanchors["out"]
        xf = fout[0] + 0.6
        d += elm.Line().at(fout).to((xf, fout[1])); d += elm.Dot().at((xf, fout[1]))
        d += elm.Line().at((xf, fout[1])).to((xf, fi[1] + 1.4))
        d += elm.Line().at((xf, fi[1] + 1.4)).to((fi[0] - 0.5, fi[1] + 1.4))
        d += elm.Line().at((fi[0] - 0.5, fi[1] + 1.4)).to((fi[0] - 0.5, fi[1]))
        d += elm.Line().at((fi[0] - 0.5, fi[1])).to(fi)
        ls._pin(d, fi, "2", dx=0.3, dy=0.25); ls._pin(d, fo.absanchors["in2"], "3", dx=0.3, dy=-0.25)
        ls._pin(d, fout, "1", dx=-0.3, dy=0.25)
        ls.lab(d, (fo.absanchors["center"][0] - 0.25, fo.absanchors["center"][1]), "U2A", ha="center", fs_=9, color=ls.GRAY)
        ls.probe(d, (xf, fout[1]), "G", dx=0.7, dy=-0.9)
        # 驱动线 → RLED → LED → 0 V（LED 的回流单独一根黑线 j7）
        xl = xf + 2.4
        d += elm.Line().at((xf, fout[1])).to((xl - 0.8, fout[1]))
        ls.lab(d, (xl - 1.2, fout[1] + 0.35), "j34 → j2 蓝线", ha="center", fs_=8.5, color=fs.C["vin"])
        d += elm.Line().at((xl - 0.8, fout[1])).to((xl, fout[1]))
        d += elm.Dot().at((xl, fout[1]))
        d += elm.Resistor().at((xl, fout[1])).to((xl, fout[1] - 2.6))
        ls.lab(d, (xl + 0.45, fout[1] - 1.3), "RLED 1 kΩ\n（h2–h5）", fs_=9)
        d += elm.LED().at((xl, fout[1] - 2.6)).to((xl, fout[1] - 5.0))
        d += elm.Ground().at((xl, fout[1] - 5.0))
        ls.lab(d, (xl + 1.0, fout[1] - 3.8), "LED（g5 阳极，g7 阴极）\n照向 BPW34；j7 单独接 0 V", fs_=9)
        # 按钮：另一种驱动（第 8 步、第 10 步③④）
        xb = xl + 3.2
        d += elm.Vdd().at((xb, fout[1] + 3.2)).label("+5 V", fontsize=9)
        d += elm.Button().at((xb, fout[1] + 3.2)).down().length(1.8)
        d += elm.Line().at((xb, fout[1] + 1.4)).to((xb, fout[1] + 0.9)).linestyle("--")
        d += elm.Line().at((xb, fout[1] + 0.9)).to((xl, fout[1] + 0.9)).linestyle("--")
        d += elm.Line().at((xl, fout[1] + 0.9)).to((xl, fout[1])).linestyle("--")
        ls.lab(d, (xb + 0.5, fout[1] + 2.3), "按钮 S2\n（e30 接 +5 V，f28 → j28）", fs_=9)
        ls.lab(d, (xl + 0.6, fout[1] + 0.45), "虚线 = 按钮模式（第 8 步、第 10 步③）：断电时把蓝线右端从 j34 改到 j28", fs_=8.5, color=fs.C["bad"])
        va_, vb_ = op.absanchors["vd"], op.absanchors["vs"]
        top_, bot_ = (va_, vb_) if va_[1] > vb_[1] else (vb_, va_)
        d += elm.Line().at(top_).to((top_[0], top_[1] + 0.5)); d += elm.Vdd().at((top_[0], top_[1] + 0.5)).label("5 V", fontsize=9)
        d += elm.Line().at(bot_).to((bot_[0], bot_[1] - 0.5)); d += elm.Ground().at((bot_[0], bot_[1] - 0.5))
        ls._pin(d, top_, "8", dx=0.3, dy=0.25); ls._pin(d, bot_, "4", dx=0.3, dy=-0.25)
        ls.lab(d, (xa - 0.6, n_[1] - 5.0), "U2 的 8 脚接 +5 V、4 脚接 0 V；C2 0.1 µF 去耦（b34 → 0 V 轨）", ha="left", fs_=9, color=ls.GRAY)
    print("[图 31-p4-7] 阶段二原理图（二）：U2B 弛张振荡器（R 10k、C 100n、Ra/Rb/Rc 10k），U2A 跟随器 → RLED 1k → LED → 0 V；按钮 S2 另接 +5 V（虚线）")
    save_schem(d, N, "31_p4_7_lab_led.png")


def _ng_rev():
    """思考题用：二极管接反 / 万用表从 B 点接到 0 V（TI LMC648x 宏模型）。
    这个宏模型的 .op 在「接反」时会停在一个不符合物理的解（输出 0.1 V 而 N 点比 V_B 低——实测过），
    所以两题都用「5 V 在 1 ms 内上电、再等 8 ms」的瞬态分析，读 9 ms 时的值，和实物上电过程一致。"""
    head = """VCC vcc 0 PWL(0 0 1m 5)
RB1 vcc vb 10k
RB2 vb 0 2.2k
CB vb 0 100n
XU1 vb inm vcc 0 out LMC648x
"""
    ctl = ('tran 1u 10m\nmeas tran o FIND v(out) AT=9m\nmeas tran n FIND v(inm) AT=9m\nmeas tran b FIND v(vb) AT=9m\n'
           'echo "RES out $&o"\necho "RES inm $&n"\necho "RES vb $&b"')
    r = bb.ng_meas(head + "RF out inm 47k\nCF out inm 27p\nD1 inm 0 DGEN\n.model DGEN D\n", ctl, includes=["LMC648x_TI.lib"])
    m = bb.ng_meas(head + "RF out inm 1Meg\nCF out inm 4.7p\nRDMM inm 0 10Meg\n", ctl, includes=["LMC648x_TI.lib"])
    return r, m


def p4_8():
    """思考题的接法图（结论在 page4 的折叠答案里）。"""
    r, m = _ng_rev()
    assert r["out"] > 4.5, r                       # 接反：输出贴近正电源
    assert abs((m["out"] - m["vb"]) - m["vb"] / 10e6 * 1e6) < 0.01, m   # 万用表 10 MΩ 当成了 R_CAL
    print(f"[SPICE 31-p4-8] 二极管接反（无光）：V_out = {r['out']:.3f} V，N 点 {r['inm']:.3f} V")
    print(f"[SPICE 31-p4-8] 万用表 10 MΩ 从 B 接 0 V：V_out − V_B = {(m['out']-m['vb'])*1e3:.1f} mV")
    with drawing(fontsize=11) as d:
        ls.title(d, (-1.0, 9.8), "思考题 1：BPW34 插反了")
        tia(d, 0.0, 4.0, rf="RF 47k", cf="CF 27p", pd=True, pd_rev=True, opname="U1A")
        ls.title(d, (13.5, 9.8), "思考题 2：万用表接在 B 点和 0 V 之间")
        t2 = tia(d, 14.0, 4.0, rf="RF 1M", cf="CF 4.7p", pd=False, opname="U1A")
        d += elm.Line().at(t2["n"]).to((11.4, 4.0))
        d += elm.MeterV().endpoints((11.4, 4.0), (11.4, 0.6)).color(fs.C["bad"])
        d += elm.Ground().at((11.4, 0.6))
        ls.lab(d, (10.7, 2.3), "万用表\n（约 10 MΩ）", ha="right", fs_=9, color=fs.C["bad"])
        ls.title(d, (6.0, -2.6), "思考题 3：阶段二把 RF 换成 1 MΩ，在开灯的房间里测")
        tia(d, 7.0, -9.0, rf="RF 1M", cf="CF 4.7p", pd=True, opname="U1A")
    save_schem(d, N, "31_p4_8_think.png")


if __name__ == "__main__":
    names = sys.argv[1:] or [k for k in list(globals()) if k[:2] in ("p1", "p2", "p3", "p4") and k[2] == "_" and callable(globals()[k])]
    for k in names:
        globals()[k]()
