"""32 电荷放大器：全部配图。
运行：/workspace/circuits-venv/bin/python code/figs/32_figs.py [p1_1 p4_3 ...]
图上的每个数字都来自 code/32_sim.py（用 importlib 载入并调用它的函数），运行时打印出来。
面包板图用 code/30_bbkit.py 画，同时做「连通检查」（assert 每个节点真的连在一起、不该连的没连上）；
p3_3 的「拿掉 R_I 会振荡」用 ngspice + TI LMC648x 宏模型现算（网表就是 spice/32/hold.cir）。SPICE 复核见 spice/32/run.py。
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
sim = _load("sim32", os.path.join(HERE, "..", "32_sim.py"), quiet=True)

N = "32"
W = bb.BB_WIRE
VM = sim.VMID


# 电源轨（T1/T2/B1/B2）每 5 孔一组，第 6、12、18、24、30… 列是组间空档，没有孔。
def _rail_ok(h):
    if h[:2] in bb.BB_RAILY:
        c = int(h.split("-")[1])
        assert c % 6 != 0, f"{h}：电源轨第 {c} 列是组间空档，没有孔"
    return h


_bb_xy_orig = bb.bb_xy


def _bb_xy_checked(h):
    return _bb_xy_orig(_rail_ok(h))


bb.bb_xy = _bb_xy_checked        # 30_bbkit 内部画线、画元件、画探针都经过 bb_xy，这里统一检查（不改 30_bbkit.py）


def _board(**kw):
    """bb.bb_board 会把电源轨每一列都画上孔；这里把 6 的倍数列的孔盖掉，和实物一致。"""
    fig, ax = bb.bb_board(**kw)
    cols = kw.get("cols", 30)
    for name, y in bb.BB_RAILY.items():
        if name in (kw.get("rails") or {}):
            for c in range(6, cols + 1, 6):
                ax.plot(c, y, "s", ms=3.4, color="#f4f1ea", zorder=1.5)
    return fig, ax


# ======================================================================================
# 连通检查（与 31、38 节同一写法）
# ======================================================================================
class Net:
    def __init__(self):
        self.p = {}

    @staticmethod
    def strip(h):
        _rail_ok(h)
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


def wire(net, ax, a, b, kind, via=()):
    bb.bb_wire(ax, a, b, kind, via=via)
    net.join(a, b)


def must(net, groups, apart):
    for g in groups:
        for h in g[1:]:
            assert net.same(g[0], h), f"{g[0]} 与 {h} 应该相通"
    for a, b in apart:
        assert not net.same(a, b), f"{a} 与 {b} 不应相通"


# ======================================================================================
# 原理图小工具：单电源电荷放大器（反相端在上、同相端在下）
# ======================================================================================
def camp(d, x0, y0, cf="C_F", rf="R_F", rf_dashed=False, rf_note="", vmid_lab="V_MID", pins=True, opname="U1A",
         ri="R_I", src=True, cs="C_S", reset=False):
    """(x0, y0) = 反相端节点 N。输入：N ←R_I← 输入点 ←C_S← S。返回 dict(n, out, op, plus, si)。"""
    d += (op := elm.Opamp(leads=True).theta(0).anchor("in1").at((x0 + 1.2, y0)))
    n = (x0, y0)
    d += elm.Line().at(n).to(op.absanchors["in1"])
    d += elm.Dot().at(n)
    o = op.absanchors["out"]
    xr = o[0] + 0.6
    d += elm.Line().at(o).to((xr, o[1])); d += elm.Dot().at((xr, o[1]))
    yc = y0 + 2.6
    d += elm.Line().at(n).to((x0, yc))
    d += elm.Capacitor().at((x0, yc)).to((xr, yc))
    ls.lab(d, ((x0 + xr) / 2, yc + 0.6), cf, ha="center", fs_=10)
    d += elm.Line().at((xr, yc)).to((xr, o[1]))
    if rf:
        yt = y0 + 4.6
        d += elm.Line().at((x0, yc)).to((x0, yt))
        r = elm.Resistor().at((x0, yt)).to((xr, yt))
        if rf_dashed:
            r = r.linestyle("--")
        d += r
        ls.lab(d, ((x0 + xr) / 2, yt + 0.55), rf + rf_note, ha="center", fs_=10)
        d += elm.Line().at((xr, yt)).to((xr, yc))
        d += elm.Dot().at((x0, yc)); d += elm.Dot().at((xr, yc))
    if reset:                      # 复位按钮 SB 并在 C_F 上：按下 = C_F 两端短接（放掉电荷），松手 = 断开
        yl = (y0 + 4.6) if rf else yc
        yb = yl + 2.0
        d += elm.Line().at((x0, yl)).to((x0, yb))
        d += elm.Button().at((x0, yb)).to((xr, yb))
        d += elm.Line().at((xr, yb)).to((xr, yl))
        d += elm.Dot().at((x0, yl)); d += elm.Dot().at((xr, yl))
        ls.lab(d, ((x0 + xr) / 2, yb + 0.75), reset if isinstance(reset, str) else "复位按钮 SB（并在 C_F 上）",
               ha="center", fs_=9, color=fs.C["fb"])
    p = op.absanchors["in2"]
    xp = x0 - 0.6
    d += elm.Line().at(p).to((xp, p[1]))
    d += elm.Line().at((xp, p[1])).to((xp, p[1] - 0.8))
    d += elm.Dot(open=True).at((xp, p[1] - 0.8))
    ls.lab(d, (xp, p[1] - 1.3), vmid_lab, ha="center", fs_=10, color=fs.C["fb"])
    si = None
    if ri:
        xs = x0 - 3.0
        d += elm.Resistor().at((xs, y0)).to(n)
        ls.lab(d, ((xs + x0) / 2, y0 + 0.55), ri, ha="center", fs_=10)
        d += elm.Dot().at((xs, y0))
        si = (xs, y0)
        if src:
            d += elm.Capacitor().at((xs - 2.6, y0)).to((xs, y0))
            ls.lab(d, (xs - 1.3, y0 + 0.65), cs, ha="center", fs_=10)
            d += elm.Dot(open=True).at((xs - 2.6, y0))
            ls.lab(d, (xs - 2.85, y0), "S", ha="right", fs_=10)
    if pins:
        ls._pin(d, op.absanchors["in1"], "2", dx=0.3, dy=0.25)
        ls._pin(d, op.absanchors["in2"], "3", dx=0.3, dy=-0.25)
        ls._pin(d, o, "1", dx=-0.3, dy=0.25)
    ls.lab(d, (op.absanchors["center"][0] - 0.25, op.absanchors["center"][1]), opname, ha="center", fs_=9, color=ls.GRAY)
    return dict(n=n, out=(xr, o[1]), op=op, plus=(xp, p[1] - 0.8), si=si)


def vmid_gen(d, x, ytop, ybot):
    """9 V —RM1— 分压点 —RM2— 0 V，分压点并 CM，再经 U1B 跟随器输出 V_MID。返回 V_MID 输出点。"""
    ymid = (ytop + ybot) / 2
    d += elm.Vdd().at((x, ytop)).label("+9 V", fontsize=9)
    d += elm.Resistor().at((x, ytop)).to((x, ymid)); ls.lab(d, (x - 0.4, (ytop + ymid) / 2), "RM1 10k", ha="right", fs_=9.5)
    d += elm.Dot().at((x, ymid))
    d += elm.Resistor().at((x, ymid)).to((x, ybot)); ls.lab(d, (x - 0.4, (ymid + ybot) / 2), "RM2 10k", ha="right", fs_=9.5)
    d += elm.Ground().at((x, ybot))
    d += elm.Line().at((x, ymid)).to((x + 1.4, ymid))
    d += elm.Capacitor(polar=True).at((x + 1.4, ymid)).to((x + 1.4, ybot)); d += elm.Ground().at((x + 1.4, ybot))
    ls.lab(d, (x + 1.8, (ymid + ybot) / 2 - 0.3), "CM 10µF\n（+ 朝上）", ha="left", fs_=9)
    d += elm.Dot().at((x + 1.4, ymid))
    d += elm.Line().at((x + 1.4, ymid)).to((x + 3.6, ymid))
    d += (ub := elm.Opamp(leads=True).theta(0).anchor("in2").at((x + 3.6, ymid)))
    i1, uo = ub.absanchors["in1"], ub.absanchors["out"]
    d += elm.Line().at(uo).to((uo[0] + 0.5, uo[1])); d += elm.Line().at((uo[0] + 0.5, uo[1])).to((uo[0] + 0.5, uo[1] + 1.6))
    d += elm.Line().at((uo[0] + 0.5, uo[1] + 1.6)).to((i1[0] - 0.5, uo[1] + 1.6))
    d += elm.Line().at((i1[0] - 0.5, uo[1] + 1.6)).to((i1[0] - 0.5, i1[1])); d += elm.Line().at((i1[0] - 0.5, i1[1])).to(i1)
    ls._pin(d, i1, "6", dx=0.3, dy=0.25); ls._pin(d, ub.absanchors["in2"], "5", dx=0.3, dy=-0.25); ls._pin(d, uo, "7", dx=-0.3, dy=0.25)
    ls.lab(d, (ub.absanchors["center"][0] - 0.25, ub.absanchors["center"][1]), "U1B", ha="center", fs_=9, color=ls.GRAY)
    d += elm.Line().at((uo[0] + 0.5, uo[1])).to((uo[0] + 1.6, uo[1])); d += elm.Dot(open=True).at((uo[0] + 1.6, uo[1]))
    d += elm.Dot().at((uo[0] + 0.5, uo[1]))
    ls.lab(d, (uo[0] + 1.8, uo[1]), "V_MID", ha="left", fs_=10, color=fs.C["fb"])
    return (uo[0] + 1.6, uo[1])


def pwr(d, op, xc, yc):
    vd, vs = op.absanchors["vd"], op.absanchors["vs"]
    d += elm.Line().at(vd).to((vd[0], vd[1] + 0.6)); d += elm.Vdd().at((vd[0], vd[1] + 0.6)).label("+9 V", fontsize=9)
    d += elm.Line().at(vs).to((vs[0], vs[1] - 0.5)); d += elm.Ground().at((vs[0], vs[1] - 0.5))
    ls._pin(d, vd, "8", dx=0.3, dy=0.25); ls._pin(d, vs, "4", dx=0.3, dy=-0.25)
    d += elm.Vdd().at((xc, yc)).label("V+（8 脚）", fontsize=9)
    d += elm.Capacitor().at((xc, yc)).to((xc, yc - 1.8)); d += elm.Ground().at((xc, yc - 1.8))
    ls.lab(d, (xc + 0.45, yc - 0.9), "C1 0.1µF\n（紧贴 8 脚）", fs_=9)


# ======================================================================================
# page1
# ======================================================================================
def p1_1():
    """电压模式（跟随器）vs 电荷模式（电荷放大器），同一个传感器 + 电缆。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (-2.0, 9.6), "（a）电压模式：传感器 + 电缆 → 跟随器")
        xq = -6.0
        d += elm.SourceI().at((xq, 0.0)).to((xq, 4.0)); ls.lab(d, (xq - 0.6, 2.0), "电荷 Q", ha="right", fs_=10)
        d += elm.Ground().at((xq, 0.0))
        d += elm.Line().at((xq, 4.0)).to((-1.0, 4.0))
        for x, t in ((-4.4, "C_p\n传感器"), (-2.4, "C_c\n电缆")):
            d += elm.Dot().at((x, 4.0)); d += elm.Capacitor().at((x, 4.0)).to((x, 0.0)); d += elm.Ground().at((x, 0.0))
            ls.lab(d, (x + 0.45, 2.0), t, ha="left", fs_=9.5)
        d += (f := elm.Opamp(leads=True).theta(0).anchor("in2").at((-1.0, 4.0)).flip())
        fo = f.absanchors["out"]
        d += elm.Line().at(fo).to((fo[0] + 0.5, fo[1])); d += elm.Line().at((fo[0] + 0.5, fo[1])).to((fo[0] + 0.5, fo[1] + 1.8))
        i1 = f.absanchors["in1"]
        d += elm.Line().at((fo[0] + 0.5, fo[1] + 1.8)).to((i1[0] - 0.4, fo[1] + 1.8))
        d += elm.Line().at((i1[0] - 0.4, fo[1] + 1.8)).to((i1[0] - 0.4, i1[1])); d += elm.Line().at((i1[0] - 0.4, i1[1])).to(i1)
        d += elm.Dot(open=True).at((fo[0] + 1.2, fo[1])); d += elm.Line().at((fo[0] + 0.5, fo[1])).to((fo[0] + 1.2, fo[1]))
        ls.lab(d, (fo[0] + 1.4, fo[1]), "V", fs_=10, color=fs.C["vout"])
        ls.lab(d, (-3.4, -1.5), "Q 分到 C_p 和 C_c 上：\nV = Q / (C_p + C_c)", ha="center", fs_=9.5, color=fs.C["bad"])
        ls.title(d, (11.0, 9.6), "（b）电荷模式：电荷放大器")
        t = camp(d, 12.0, 4.0, cf="C_F", rf=None, ri=None, src=False, vmid_lab="")
        ls.lab(d, (11.4 + 0.3, 2.2), "参考电压", ha="left", fs_=10, color=fs.C["fb"])
        xq = 8.0
        d += elm.SourceI().at((xq, 0.0)).to((xq, 4.0)); ls.lab(d, (xq - 0.6, 2.0), "电荷 Q", ha="right", fs_=10)
        d += elm.Ground().at((xq, 0.0))
        d += elm.Line().at((xq, 4.0)).to(t["n"])
        for x, tt in ((9.0, "C_p"), (10.2, "C_c")):
            d += elm.Dot().at((x, 4.0)); d += elm.Capacitor().at((x, 4.0)).to((x, 0.0)); d += elm.Ground().at((x, 0.0))
            ls.lab(d, (x - 0.35, 1.4), tt, ha="right", fs_=9.5)
        d += elm.Line().at(t["out"]).to((t["out"][0] + 0.8, t["out"][1])); d += elm.Dot(open=True).at((t["out"][0] + 0.8, t["out"][1]))
        ls.lab(d, (t["out"][0] + 1.0, t["out"][1]), "V_out", fs_=10, color=fs.C["vout"])
        ls.lab(d, (12.0, 4.5), "N", ha="right", fs_=10)
        ls.lab(d, (11.0, -1.5), "N 点被反馈钉住，C_p、C_c 两端电压不变：\nQ 全部搬到 C_F 上", ha="center", fs_=9.5, color=fs.C["fb"])
    print("[图 32-p1-1] (a) 电荷源 + C_p + C_c → 跟随器；(b) 电荷源 + C_p + C_c → 反相端 N，C_F 反馈，同相端接参考电压；1/2/3 脚已标")
    save_schem(d, N, "32_p1_1_voltage_vs_charge.png")


def p1_2():
    """同一份 100 pC：电压模式随电缆变长而缩水，电荷模式不变。"""
    q, cp, cf = 100e-12, 1e-9, 1e-9
    cc = np.logspace(-11, -8, 200)
    vv = q / (cp + cc) * 1e3
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.semilogx(cc * 1e9, vv, **fs.LS["bad"], label="电压模式 Q/(C_p+C_c)")
    ax.semilogx(cc * 1e9, np.full_like(cc, q / cf * 1e3), **fs.LS["vout"], label="电荷模式 Q/C_F（C_F 1 nF）")
    for c in (0.1e-9, 1e-9, 10e-9):
        v = q / (cp + c) * 1e3
        ax.plot(c * 1e9, v, "o", ms=5, color=fs.C["bad"])
        ax.text(c * 1e9 * 1.12, v + 4, f"{v:.1f} mV", fontsize=8.5)
        print(f"[图 32-p1-2] C_c = {c*1e9:g} nF：电压模式 {v:.2f} mV；电荷模式 {q/cf*1e3:.1f} mV")
    fs.axlabels(ax, "电缆电容 C_c", "nF", "输出幅度", "mV")
    ax.set_ylim(0, 120)
    ax.legend(fontsize=8.5, loc="lower left")
    ax.set_title("同一个传感器（C_p = 1 nF，Q = 100 pC），电缆越接越长", fontsize=10)
    fs.save(fig, N, "32_p1_2_cable.png")


def p1_3():
    """9 V 单电源：0 V、V_MID、+9 V，以及 N 点在哪里。"""
    fig, ax = plt.subplots(figsize=(7.4, 2.8))
    ax.set_xlim(-0.9, 10.2); ax.set_ylim(0, 3.1); ax.axis("off")
    ax.plot([0, 9], [1.0, 1.0], color="0.3", lw=1.2)
    for v, lab in ((0, "0 V\n电池负极"), (VM, f"V_MID\n{VM:.1f} V"), (9, "+9 V\n电池正极")):
        ax.plot([v, v], [0.9, 1.1], color="0.3", lw=1.2)
        ax.text(v, 0.8, lab, ha="center", va="top", fontsize=8.5)
    ax.annotate("", (VM + 4.4, 2.0), (VM, 2.0), arrowprops=dict(arrowstyle="->", color=fs.C["vout"], lw=1.5))
    ax.annotate("", (VM - 4.4, 2.0), (VM, 2.0), arrowprops=dict(arrowstyle="->", color=fs.C["vout"], lw=1.5))
    ax.text(VM, 2.2, "输出（B 点）以 V_MID 为中心上下摆", ha="center", fontsize=9, color=fs.C["vout"])
    ax.plot(VM, 1.45, "v", ms=9, color=fs.C["fb"])
    ax.text(VM + 0.25, 1.5, "N（2 脚）也在这里：被反馈钉在 V_MID，不是 0 V", fontsize=8.5, color=fs.C["fb"])
    ax.set_title("9 V 电池单电源：三个名字、三个地方", fontsize=10)
    print(f"[图 32-p1-3] 0 V / V_MID {VM:.1f} V / +9 V；N 点被钉在 V_MID")
    fs.save(fig, N, "32_p1_3_vmid.png")


# ======================================================================================
# page2
# ======================================================================================
def p2_1():
    """完整原理图（阶段二的形式）：压电片 → R_I → N，C_F ∥ R_F，V_MID 由 U1B 缓冲，引脚号。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (4.0, 10.6), "单电源电荷放大器（LMC6482，9 V 电池）")
        t = camp(d, 6.0, 4.0, cf="C_F", rf="R_F", ri="R_I", src=False)
        xs = t["si"][0]
        d += elm.Line().at(t["si"]).to((xs - 1.2, 4.0))
        d += elm.SourceI().at((xs - 1.2, 0.6)).to((xs - 1.2, 4.0))
        ls.lab(d, (xs - 1.8, 2.3), "压电片\n（电荷 Q ∥ C_p）", ha="right", fs_=9.5)
        d += elm.Line().at((xs - 1.2, 0.6)).to((xs - 1.2, -0.2)); d += elm.Dot(open=True).at((xs - 1.2, -0.2))
        ls.lab(d, (xs - 1.2, -0.7), "V_MID", ha="center", fs_=10, color=fs.C["fb"])
        pwr(d, t["op"], 15.5, 9.4)
        o = t["out"]
        d += elm.Line().at(o).to((o[0] + 1.0, o[1])); d += elm.Dot(open=True).at((o[0] + 1.0, o[1]))
        ls.lab(d, (o[0] + 1.2, o[1]), "V_out", fs_=10, color=fs.C["vout"])
        ls.lab(d, (5.7, 4.5), "N", ha="right", fs_=10)
        vmid_gen(d, 2.0, -2.6, -7.4)
    print("[图 32-p2-1] 电荷放大器：R_I 串在 N 前，C_F ∥ R_F，3 脚接 V_MID；V_MID = RM1/RM2 10k/10k 分压 + CM 10µF，经 U1B（5/6/7 脚）缓冲；8/4 脚 + C1")
    save_schem(d, N, "32_p2_1_schematic.png")


def p2_3():
    """压电片 → 电荷放大器的幅频：f_L 由 R_F·C_F 定，f_H 由 R_I·C_p 定。"""
    f = np.logspace(-2.5, 4.5, 800)
    fig, ax = plt.subplots(figsize=(7.4, 3.3))
    sty = [fs.LS["vout"], fs.LS["vin"], fs.LS["fb"]]
    for cp, st in zip(sim.CP_LIST, sty):
        m = sim.mag(f, 1.0, sim.CF2, sim.RF, sim.RI, cp)
        kw = dict(st); kw.pop("markevery", None); kw.pop("marker", None)
        fh = sim.f_h(sim.RI, cp)
        ax.semilogx(f, 20 * np.log10(m), **kw, label=f"C_p = {cp*1e9:.0f} nF：f_H = {fh:.0f} Hz")
        print(f"[图 32-p2-3] C_p = {cp*1e9:.0f} nF：f_H = {fh:.1f} Hz")
    fl = sim.f_l(sim.RF, sim.CF2)
    ax.axvline(fl, **fs.LS["ref"]); ax.text(fl * 1.15, -12, f"f_L = {fl:.3f} Hz", fontsize=8.5)
    ax.axhline(-3, **fs.LS["ref"]); ax.text(10 ** 4.45, -2.6, "−3 dB", ha="right", va="bottom", fontsize=8)
    fs.axlabels(ax, "频率", "Hz", "输出 / 中频", "dB")
    ax.set_ylim(-30, 3)
    ax.legend(fontsize=8.5, loc="lower center")
    ax.set_title("R_F 10 MΩ、C_F 100 nF、R_I 10 kΩ", fontsize=10)
    print(f"[图 32-p2-3] f_L = 1/(2π·10 MΩ·100 nF) = {fl:.4f} Hz")
    fs.save(fig, N, "32_p2_3_band.png")


def p2_2():
    """同一份电荷进来之后：拔掉 R_F（保持）、R_F·C_F = 100 ms、慢速演示 10 s。"""
    v0 = -sim.charge_mode(VM)
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.2, 3.1))
    t = np.linspace(0, 0.6, 600)
    a.plot(t, np.full_like(t, v0), **fs.LS["good"], label="拔掉 R_F（保持模式）")
    a.plot(t, sim.decay(v0, sim.RF * sim.CF1, t), **fs.LS["vout"], label="R_F 10 MΩ ∥ C_F 10 nF")
    fs.axlabels(a, "电荷进来之后的时间", "s", "B − A", "V")
    a.set_ylim(-0.03, 0.52); a.legend(fontsize=8)
    a.set_title("τ = R_F·C_F = %.0f ms" % (sim.RF * sim.CF1 * 1e3), fontsize=9.5)
    t2 = np.linspace(0, 32, 600)
    taus = sim.RF * sim.CF_SLOW
    b.plot(t2, sim.decay(v0, taus, t2), **fs.LS["vin"], label="C_F 1 µF ∥ 10 MΩ（慢速演示）")
    fs.axlabels(b, "时间", "s", "B − A", "V")
    b.set_ylim(-0.03, 0.52); b.legend(fontsize=8)
    b.set_title(f"τ = {taus:.0f} s：用秒表就能看", fontsize=9.5)
    print(f"[图 32-p2-2] 起点 {v0:.3f} V；τ = {sim.RF*sim.CF1*1e3:.0f} ms 与 {taus:.0f} s")
    fs.save(fig, N, "32_p2_2_decay.png")


# ======================================================================================
# page3
# ======================================================================================
def p3_1():
    """保持模式漂移 I_B/C_F：四种运放（对数轴），对照判据。"""
    names = ["LMC6482", "TL072", "LM358B", "LM358"]
    typ = [sim.drift(sim.IB_TYP[k], sim.CF1) * 1e3 for k in names]
    mx = [sim.drift(sim.IB_MAX[k], sim.CF1) * 1e3 for k in names]
    crit = 0.01 * 0.45 / 10 * 1e3
    fig, ax = plt.subplots(figsize=(7.4, 3.1))
    x = np.arange(4)
    ax.bar(x - 0.18, typ, 0.34, color=fs.C["vin"], label="典型 I_B / C_F")
    ax.bar(x + 0.18, mx, 0.34, color=fs.C["bad"], label="最大 I_B / C_F")
    ax.set_yscale("log"); ax.set_ylim(1e-3, 1e6)
    ax.axhline(crit, **fs.LS["good"]); ax.text(3.45, crit * 1.6, f"判据 {crit:.2f} mV/s", ha="right", fontsize=8.5)
    for i in range(4):
        ax.text(x[i] - 0.18, typ[i] * 1.5, f"{typ[i]:.2g}", ha="center", fontsize=8)
        ax.text(x[i] + 0.18, mx[i] * 1.5, f"{mx[i]:.3g}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(names)
    ax.set_ylabel("漂移 / (mV/s)")
    ax.legend(fontsize=8, loc="upper left")
    ax.set_title("C_F = 10 nF，拔掉 R_F", fontsize=10)
    print(f"[图 32-p3-1] 典型 {typ}，最大 {mx}（mV/s），判据 {crit:.2f} mV/s")
    fs.save(fig, N, "32_p3_1_drift.png")


def p3_2():
    """三种常见的错误接法（只画接法，不给结果）。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (-1.5, 9.8), "（a）万用表一支表笔碰 N（2 脚）")
        t = camp(d, 0.0, 4.0, cf="C_F", rf="R_F", ri="R_I", src=True)
        d += elm.Dot().at((0.0, 5.6))
        d += elm.MeterV().at((0.0, 5.6)).left().length(3.0).color(fs.C["bad"])
        d += elm.Line().at((-3.0, 5.6)).to((-4.6, 5.6)).color(fs.C["bad"])
        d += elm.Ground().at((-4.6, 5.6))
        ls.lab(d, (-4.6, 6.2), "0 V", ha="center", fs_=9.5)
        ls.lab(d, (-1.5, 6.5), "万用表（约 10 MΩ）", ha="center", fs_=9, color=fs.C["bad"])
        ls.title(d, (14.0, 9.8), "（b）省掉 R_I：C_S 直接接 N")
        t2 = camp(d, 15.0, 4.0, cf="C_F", rf=None, ri=None, src=False)
        d += elm.Capacitor().at((12.0, 4.0)).to(t2["n"]).color(fs.C["bad"])
        ls.lab(d, (13.5, 4.65), "C_S", ha="center", fs_=10, color=fs.C["bad"])
        d += elm.Dot(open=True).at((12.0, 4.0)); ls.lab(d, (11.75, 4.0), "S", ha="right", fs_=10)
        ls.title(d, (6.0, -3.6), "（c）把 LMC6482 换成手边的 LM358，拔掉 R_F")
        camp(d, 7.0, -9.0, cf="C_F", rf=None, ri="R_I", src=True, opname="LM358")
    print("[图 32-p3-2] 错误接法：(a) 万用表碰 N 到 0 V；(b) C_S 不经 R_I 直接接 N；(c) 换 LM358 并拔掉 R_F")
    save_schem(d, N, "32_p3_2_miswire.png")


def _hold_body(ri):
    with open(os.path.join(HERE, "..", "..", "spice", "32", "hold.cir"), encoding="utf-8") as f:
        t = f.read()
    t = t.replace(".include ../models/", f".include {bb.MODELS}/").replace("\n.end\n", "\n")
    return t.replace("ri=10k", f"ri={ri}")


def p3_3():
    """SPICE：复位中，有 / 没有 R_I 时 U1A 输出（TI LMC648x 宏模型）。"""
    res = {}
    for ri in ("1m", "10k"):
        t, y = bb.ng_wave(_hold_body(ri), "tran 20n 1m 0 20n uic", ["v(out)"])
        k = t >= 0.95e-3
        res[ri] = (t[k], y[k])
    pp0 = np.ptp(res["1m"][1]) * 1e3; pp1 = np.ptp(res["10k"][1]) * 1e3
    tt, yy = res["1m"]
    zc = tt[1:][(yy[:-1] < VM) & (yy[1:] >= VM)]
    fo = (len(zc) - 1) / (zc[-1] - zc[0]) if len(zc) > 2 else float("nan")
    assert pp0 > 100 and pp1 < 5, (pp0, pp1)
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    ax.plot((res["1m"][0] - 0.95e-3) * 1e6, res["1m"][1], **fs.LS["bad"], label=f"没有 R_I：峰峰值 {pp0:.0f} mV，约 {fo/1e3:.0f} kHz")
    ax.plot((res["10k"][0] - 0.95e-3) * 1e6, res["10k"][1], **fs.LS["good"], label=f"R_I = 10 kΩ：峰峰值 {pp1:.1f} mV")
    fs.axlabels(ax, "时间（从 0.95 ms 起）", "µs", "U1A 输出（B 点）", "V")
    ax.set_ylim(4.1, 4.95); ax.legend(fontsize=8.5, loc="upper right")
    ax.set_title("SPICE（TI LMC648x 宏模型）：按住复位按钮，S1 不动", fontsize=10)
    print(f"[SPICE 32-p3-3] 没有 R_I：峰峰值 {pp0:.1f} mV，约 {fo/1e3:.0f} kHz；有 R_I：峰峰值 {pp1:.2f} mV")
    fs.save(fig, N, "32_p3_3_no_ri.png")


# ======================================================================================
# page4：面包板（带连通检查）+ 实验原理图
# ======================================================================================
RAILS = {"T1": ("+9 V", W["pos"]), "T2": ("0 V", W["gnd"]),
         "B1": ("0 V", W["gnd"]), "B2": ("+9 V", W["pos"])}


def battery(ax):
    """面包板下方的 9 V 电池扣：红线 → B2（+9 V），黑线 → B1（0 V）。"""
    x0, y0 = 22.0, -7.6
    ax.add_patch(bb._BbRect((x0, y0), 6.5, 1.5, fc="#fff3c4", ec="0.3", lw=0.8, zorder=5))
    ax.text(x0 + 3.25, y0 + 0.55, "9 V 电池（电池扣）", ha="center", va="center", fontsize=7.5, zorder=6)
    for nm, x, h, k in (("+", x0 + 5.5, "B2-28", "pos"), ("−", x0 + 1.0, "B1-23", "gnd")):
        ax.text(x, y0 + 1.15, nm, ha="center", fontsize=9, zorder=6)
        x1, y1 = bb.bb_xy(h)
        ax.plot([x, x, x1], [y0 + 1.5, y1 - 0.0, y1], color=W[k], lw=2.0, zorder=3)
        ax.plot(x1, y1, "o", ms=3.5, color=W[k], zorder=4)


def _common(ax, net):
    """各步共用：电源跳线、芯片、去耦、V_MID 分压 + U1B 跟随器、第 3 列 V_MID 延长。"""
    wire(net, ax, "T1-1", "B2-1", "pos", via=[(-0.9, 11.6), (-0.9, -3.6)])
    wire(net, ax, "T2-2", "B1-2", "gnd", via=[(-0.4, 10.8), (-0.4, -2.8)])
    net.join("B2-28", "B2-1"); net.join("B1-23", "B1-2")      # 电池扣（板外）
    bb.bb_dip8(ax, 14, "LMC6482")
    wire(net, ax, "a14", "T1-14", "pos")       # 8 脚 V+
    wire(net, ax, "j17", "B1-17", "gnd")       # 4 脚 V−
    bb.bb_part2(ax, "b14", "T2-13", "C1 0.1µF", kind="box", dy=-0.6, fc="#ffe0b2")
    bb.bb_res(ax, "b20", "b24", "RM1 10k")
    wire(net, ax, "a24", "T1-23", "pos")       # 电源轨第 24 列是组间空档，没有孔
    bb.bb_res(ax, "c20", "c26", "RM2 10k", dy=-0.55)
    wire(net, ax, "a26", "T2-26", "gnd")
    bb.bb_part2(ax, "a20", "T2-19", "CM 10µF", kind="cap", dy=0.6)
    wire(net, ax, "d17", "d20", "fb")          # 5 脚接分压点
    wire(net, ax, "b15", "b16", "fb")          # 7 脚接 6 脚：U1B 跟随器，输出就是 V_MID
    wire(net, ax, "c16", "j3", "fb", via=[(16.0, 6.6), (3.0, 6.6)])   # V_MID 延长到第 3 列（下半区）
    battery(ax)


def _assert_common(net):
    must(net, [["d20", "b20", "c20", "a20", "d17", "e17"], ["b15", "b16", "e15", "e16", "c16", "j3", "h3", "f3"],
               ["b14", "a14", "e14", "T1-5", "B2-9"], ["j17", "f17", "B1-29", "T2-3", "B1-23"]],
         apart=[("d20", "b15"), ("f15", "f16"), ("f14", "T1-1"), ("f14", "T2-1"),
                ("f15", "T2-1"), ("f15", "T1-1"), ("e15", "e17"), ("j3", "T2-1"), ("j3", "T1-1")])


def _probes(ax, b_hole="j14"):
    bb.bb_probe(ax, "a15", "A", dx=0.0, dy=1.4)
    bb.bb_probe(ax, b_hole, "B", dx=1.5, dy=-3.6)
    bb.bb_probe(ax, "T1-28", "C", dx=0.0, dy=1.0)


# ---------------- 阶段一的公共部分：S1、CS、RI、复位按钮 SB ----------------
def _button(ax, net=None):
    """四脚轻触按钮 SB 跨隔离槽插在 e11/e13/f11/f13，只用对角两脚 e11（上半区第 11 列）和 f13（下半区第 13 列）。
    按钮不是导线：连通检查里不 join（按下时才通）。"""
    bb.bb_block(ax, ["e11", "e13", "f11", "f13"], "", pins=["用", "", "", "用"], fc="#e1bee7", pad=0.3)
    ax.text(12.0, 4.3, "SB", ha="center", va="center", fontsize=7.5, zorder=7)


def _dash_hint(ax, a, b, text, dy=0.55, at=None):
    (x0, y0), (x1, y1) = bb.bb_xy(a), bb.bb_xy(b)
    ax.plot([x0, x1], [y0, y1], ls="--", color="0.45", lw=1.4, zorder=3)
    for x, y in ((x0, y0), (x1, y1)):
        ax.plot(x, y, "o", ms=4, mfc="white", mec="0.45", zorder=4)
    tx, ty, ha = at if at else ((x0 + x1) / 2, (y0 + y1) / 2 + dy, "center")
    ax.text(tx, ty, text, ha=ha, va="center", fontsize=6.8, color="0.35", zorder=6,
            bbox=dict(fc="white", ec="none", pad=0.5, alpha=0.85))


def _stage1(ax, net, vmode=False):
    """阶段一（电荷模式）。vmode=True 时画第 8 步的电压模式改法。"""
    _common(ax, net)
    if not vmode:
        wire(net, ax, "d16", "g16", "fb", via=[(16.4, 6.0), (16.4, 2.6)])     # V_MID → 3 脚
        bb.bb_part2(ax, "i14", "i15", "CF 10n", kind="box", dy=-0.55, fc="#c8e6c9")
        wire(net, ax, "j15", "j10", "sig")                                    # N 延长到第 10 列
        wire(net, ax, "g13", "g14", "out")                                    # SB 下脚 → 输出（1 脚）
    else:
        wire(net, ax, "d16", "g13", "fb", via=[(16.4, 6.0), (16.4, 2.6), (13.0, 2.6)])   # V_MID → SB 下脚
        wire(net, ax, "i14", "i15", "out")                                    # 1 脚接 2 脚：跟随器
        wire(net, ax, "j16", "j10", "sig")                                    # 3 脚接第 10 列
    _button(ax)
    wire(net, ax, "d11", "h10", "sig", via=[(10.4, 6.0), (10.4, 1.0)])      # SB 上脚 → 第 10 列
    bb.bb_res(ax, "g7", "g10", "RI 10k", dy=0.5)
    bb.bb_part2(ax, "i4", "i7", "CS 1n", kind="box", dy=-0.6, fc="#c8e6c9")
    bb.bb_block(ax, ["h3", "h4", "h5"], "", pins=["①", "公共", "②"], fc="#b3e5fc", pad=0.3)
    ax.text(2.3, 1.0, "S1", ha="right", va="center", fontsize=7.5, zorder=7)
    wire(net, ax, "j5", "B1-5", "gnd")                                        # S1 ② → 0 V（第 6 步断电改到 B2）
    _probes(ax)


def _assert_stage1(net, vmode=False):
    _assert_common(net)
    vm = ["c16", "j3", "h3", "d16"]
    if not vmode:
        must(net, [["f15", "i15", "j15", "j10", "g10", "h10", "d11", "e11"], ["f14", "g14", "g13", "f13", "i14", "j14"],
                   vm + ["g16", "f16"], ["h4", "i4"], ["h5", "j5", "B1-5", "T2-1"], ["g7", "i7"]],
             apart=[("f15", "f14"), ("e11", "f13"), ("g7", "g10"), ("i4", "i7"), ("f16", "f15"), ("h3", "h4"),
                    ("h4", "h5"), ("h3", "h5"), ("g10", "T1-1"), ("g10", "B1-1"), ("g7", "B1-1"), ("j3", "f10")])
    else:
        must(net, [["f16", "j16", "j10", "g10", "h10", "d11", "e11"], ["f14", "f15", "i14", "i15", "j14"],
                   vm + ["g13", "f13"], ["h4", "i4"], ["h5", "j5", "B1-5"], ["g7", "i7"]],
             apart=[("f16", "f15"), ("e11", "f13"), ("g7", "g10"), ("g16", "d16"), ("f13", "f14")])


def p4_1():
    """阶段一：保持模式（电荷模式），S1 拨动开关注入，复位按钮 SB 并在 CF 上。"""
    net = Net()
    fig, ax = _board(cols=30, rails=RAILS, figsize=(10, 6.8))
    ax.set_ylim(-8.3, 12.7)
    _stage1(ax, net)
    _assert_stage1(net)
    _dash_hint(ax, "h14", "h15", "← RF（第 9 步断电后插）", at=(15.6, 1.0, "left"))
    _dash_hint(ax, "j7", "B1-7", "", dy=0)
    ax.text(7.3, -2.2, "CC", ha="left", fontsize=6.8, color="0.35")
    ax.text(0.3, -5.4, "S1 拨到①（h3）：S 端接 V_MID；拨到②（h5）：接 0 V。\nSB 只用对角两脚 e11、f13。\n虚线 = 后面断电时才插：CC（j7→B1，第 7 步）、RF（h14–h15，第 9 步）",
            ha="left", va="top", fontsize=7.5, color=fs.C["bad"])
    print("[图 32-p4-1] 阶段一面包板：U1 第 14～17 列；CF i14–i15；SB e11/f13（d11→h10，g13→g14）；j15→j10；RI g7–g10；"
          "CS i4–i7；S1 h3①/h4 公共/h5②，j5→B1；连通检查通过")
    fs.save(fig, N, "32_p4_1_bb_stage1.png")


def _lab_vmid(d, x, y):
    """实验原理图里：V_MID 发生器放左下角。"""
    return vmid_gen(d, x, y, y - 4.8)


def _s1(d, sp, up_lab="V_MID\n（h3，第 3 列）", dn_lab="0 V\n（j5 → B1）", note=None):
    """S 端往左引出，挂拨动开关 S1：①（左下）接 V_MID，②（右下）接 0 V。"""
    x = sp[0] - 2.2
    d += elm.Line().at(sp).to((x, sp[1])); d += elm.Line().at((x, sp[1])).to((x, sp[1] - 0.6))
    d += (sw := elm.SwitchSpdt2().at((x, sp[1] - 0.6)).down().anchor("a"))
    ls.lab(d, (x + 0.2, sp[1] + 0.45), "S1（公共脚 h4）", ha="center", fs_=9, color=fs.C["fb"])
    b_, c_ = sw.absanchors["b"], sw.absanchors["c"]
    lo, hi = (b_, c_) if b_[0] < c_[0] else (c_, b_)
    d += elm.Line().at(lo).to((lo[0] - 0.8, lo[1])); d += elm.Line().at((lo[0] - 0.8, lo[1])).to((lo[0] - 0.8, lo[1] - 1.0))
    d += elm.Dot(open=True).at((lo[0] - 0.8, lo[1] - 1.0))
    ls.lab(d, (lo[0] - 0.8, lo[1] - 1.5), "① " + up_lab, ha="center", fs_=9, color=fs.C["fb"])
    d += elm.Line().at(hi).to((hi[0] + 0.8, hi[1])); d += elm.Line().at((hi[0] + 0.8, hi[1])).to((hi[0] + 0.8, hi[1] - 1.0))
    d += elm.Ground().at((hi[0] + 0.8, hi[1] - 1.0))
    ls.lab(d, (hi[0] + 1.2, hi[1] - 0.4), "② " + dn_lab, ha="left", fs_=9)
    if note:
        ls.lab(d, (hi[0] + 0.8, hi[1] - 2.3), note, ha="center", fs_=8.5, color=fs.C["bad"])


def p4_2():
    with drawing(fontsize=11) as d:
        ls.title(d, (4.0, 13.6), "阶段一：保持模式（U1 = LMC6482，9 V 电池）")
        t = camp(d, 6.0, 4.0, cf="CF 10 nF（i14–i15）", rf="RF 10 MΩ", rf_dashed=True, rf_note="（第 9 步断电后插 h14–h15）",
                 ri="RI 10 kΩ", cs="CS 1 nF", reset="复位按钮 SB（e11 → 第 10 列 = N，f13 → 第 14 列 = 输出）")
        si = t["si"]
        d += elm.Line().at(si).to((si[0], 2.4))
        d += elm.Capacitor().at((si[0], 2.4)).to((si[0], 0.4)).linestyle("--"); d += elm.Ground().at((si[0], 0.4))
        ls.lab(d, (si[0] + 0.35, 1.6), "CC", ha="left", fs_=9, color=ls.GRAY)
        ls.lab(d, (si[0], -0.75), "CC 第 7 步断电后\n插 j7→B1", ha="center", fs_=8.5, color=ls.GRAY)
        ls.lab(d, ((si[0] + 6.0) / 2, 3.45), "g7–g10", ha="center", fs_=8.5, color=ls.GRAY)
        ls.lab(d, (si[0] - 1.3, 3.45), "i4–i7", ha="center", fs_=8.5, color=ls.GRAY)
        _s1(d, (si[0] - 2.6, 4.0), note="第 6 步：断电后\nj5 改接 B2（+9 V）")
        ls.lab(d, (5.8, 4.45), "N", ha="right", fs_=10)
        pwr(d, t["op"], 15.5, 12.4)
        o = t["out"]
        d += elm.Line().at(o).to((o[0] + 1.2, o[1])); d += elm.Dot(open=True).at((o[0] + 1.2, o[1]))
        ls.probe(d, (o[0] + 0.6, o[1]), "B", dx=0.0, dy=-1.2)
        ls.colnote(d, (o[0] + 1.4, o[1]), "第 14 列（1 脚）", "right")
        ls.lab(d, (t["plus"][0], 0.9), "（3 脚经 d16→g16）", ha="center", fs_=8.5, color=ls.GRAY)
        vo = _lab_vmid(d, 4.0, -4.0)
        ls.probe(d, vo, "A", dx=0.6, dy=-1.0)
        ls.colnote(d, (vo[0] + 0.3, vo[1] + 0.6), "第 15/16 列上半区（7、6 脚）\nc16 → j3 延长到第 3 列", "right", ofst=0.0)
    print("[图 32-p4-2] 阶段一原理图：S1（①V_MID/②0 V）—CS 1 nF—RI 10 kΩ—N，CF 10 nF ∥ 复位按钮 SB，RF 10 MΩ 虚线；CC 虚线到 0 V；V_MID 由 U1B 缓冲；测量点 A/B（C 在 +9 V 轨）")
    save_schem(d, N, "32_p4_2_lab_stage1.png")


def p4_3():
    """第 8 步：电压模式对照（断电改 4 处：拔 CF；j15→j10 改 j16→j10；i14–i15 插短线；d16 那根线下端 g16 改 g13，拔 g13→g14）。"""
    net = Net()
    fig, ax = _board(cols=30, rails=RAILS, figsize=(10, 6.8))
    ax.set_ylim(-8.3, 12.7)
    _stage1(ax, net, vmode=True)
    _assert_stage1(net, vmode=True)
    _dash_hint(ax, "j7", "B1-7", "", dy=0)
    ax.text(7.3, -2.2, "CC", ha="left", fontsize=6.8, color="0.35")
    ax.text(0.3, -5.4, "全程断电改：拔 CF、拔 g13→g14；j15→j10 改 j16→j10；\ni14–i15 插短线；d16 线的下端 g16 改 g13（SB 按下 = 第 10 列接 V_MID）\nCC 0/10/100 nF 断电时插在 j7→B1（虚线）",
            ha="left", va="top", fontsize=7.5, color=fs.C["bad"])
    print("[图 32-p4-3] 电压模式面包板：i14–i15 短接（跟随器），j16→j10，d16→g13（SB 另一脚接 V_MID），RI g7–g10，CS i4–i7，S1 h3/h4/h5；连通检查通过")
    fs.save(fig, N, "32_p4_3_bb_vmode.png")


def p4_4():
    with drawing(fontsize=11) as d:
        ls.title(d, (4.0, 10.6), "第 8 步：电压模式对照（U1A 接成跟随器）")
        d += (op := elm.Opamp(leads=True).theta(0).anchor("in2").at((6.0, 4.0)).flip())
        i2, i1, o = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
        d += elm.Line().at(o).to((o[0] + 0.6, o[1])); d += elm.Line().at((o[0] + 0.6, o[1])).to((o[0] + 0.6, o[1] + 1.8))
        d += elm.Line().at((o[0] + 0.6, o[1] + 1.8)).to((i1[0] - 0.4, o[1] + 1.8))
        d += elm.Line().at((i1[0] - 0.4, o[1] + 1.8)).to((i1[0] - 0.4, i1[1])); d += elm.Line().at((i1[0] - 0.4, i1[1])).to(i1)
        ls.lab(d, ((o[0] + i1[0]) / 2, o[1] + 2.25), "i14–i15 短线（1 脚接 2 脚）", ha="center", fs_=8.5, color=ls.GRAY)
        ls._pin(d, i2, "3", dx=0.3, dy=-0.25); ls._pin(d, i1, "2", dx=0.3, dy=0.25); ls._pin(d, o, "1", dx=-0.3, dy=0.25)
        ls.lab(d, (op.absanchors["center"][0] - 0.25, op.absanchors["center"][1]), "U1A", ha="center", fs_=9, color=ls.GRAY)
        d += elm.Line().at((4.6, 4.0)).to(i2)
        d += elm.Dot().at((4.6, 4.0)); ls.lab(d, (4.5, 4.45), "第 10 列（j16→j10）", ha="right", fs_=8.5, color=ls.GRAY)
        d += elm.Resistor().at((1.6, 4.0)).to((4.6, 4.0)); ls.lab(d, (3.1, 3.4), "RI 10 kΩ", ha="center", fs_=10)
        d += elm.Dot().at((1.6, 4.0))
        d += elm.Capacitor().at((-1.0, 4.0)).to((1.6, 4.0)); ls.lab(d, (0.3, 4.65), "CS 1 nF", ha="center", fs_=10)
        d += elm.Dot(open=True).at((-1.0, 4.0)); ls.lab(d, (-1.25, 4.3), "S", ha="right", fs_=10)
        d += elm.Line().at((1.6, 4.0)).to((1.6, 2.4))
        d += elm.Capacitor().at((1.6, 2.4)).to((1.6, 0.4)).linestyle("--"); d += elm.Ground().at((1.6, 0.4))
        ls.lab(d, (2.0, 1.4), "CC 0 / 10 / 100 nF\nj7 → B1", ha="left", fs_=9, color=ls.GRAY)
        ls.colnote(d, (1.6, 4.0), "第 7 列", "top", ofst=1.1)
        # 复位按钮：第 10 列 ↔ V_MID
        d += elm.Line().at((4.6, 4.0)).to((4.6, 6.6))
        d += elm.Button().at((4.6, 6.6)).up().length(1.6)
        d += elm.Dot(open=True).at((4.6, 8.2))
        ls.lab(d, (4.9, 8.4), "V_MID（d16 → g13）", ha="left", fs_=9, color=fs.C["fb"])
        ls.lab(d, (4.1, 7.4), "SB", ha="right", fs_=9.5, color=fs.C["fb"])
        _s1(d, (-1.0, 4.0))
        d += elm.Line().at((o[0] + 0.6, o[1])).to((o[0] + 1.4, o[1])); d += elm.Dot(open=True).at((o[0] + 1.4, o[1]))
        ls.probe(d, (o[0] + 1.0, o[1]), "B", dx=0.0, dy=-1.2)
        ls.colnote(d, (o[0] + 1.6, o[1]), "第 14 列（1 脚）", "right")
        ls.lab(d, (6.4, 0.8), "U1 的 8 脚 +9 V、4 脚 0 V、C1 去耦、U1B 的 V_MID\n都和图 32-p4-2 一样，没画", ha="left", fs_=8.5, color=ls.GRAY)
    print("[图 32-p4-4] 电压模式原理图：S1—CS 1 nF—RI 10 kΩ—3 脚，1 脚接 2 脚；SB 把第 10 列接 V_MID；CC 虚线到 0 V")
    save_schem(d, N, "32_p4_4_lab_vmode.png")


def p4_5():
    """阶段二：压电片 + C_F 100 nF（∥ R_F 10 MΩ，第 13 步才插）+ 反并联 1N4148 钳位。"""
    net = Net()
    fig, ax = _board(cols=30, rails=RAILS, figsize=(10, 6.8))
    ax.set_ylim(-8.3, 12.7)
    _common(ax, net)
    wire(net, ax, "d16", "g16", "fb", via=[(16.4, 6.0), (16.4, 2.6)])
    bb.bb_part2(ax, "i14", "i15", "CF 100n", kind="box", dy=-0.55, fc="#c8e6c9")
    wire(net, ax, "j15", "j10", "sig")
    wire(net, ax, "g13", "g14", "out")
    _button(ax)
    wire(net, ax, "d11", "h10", "sig", via=[(10.4, 6.0), (10.4, 1.0)])
    bb.bb_res(ax, "g7", "g10", "RI 10k", dy=0.5)
    bb.bb_part2(ax, "f10", "f3", "D1 1N4148", kind="diode", dy=0.55)
    bb.bb_part2(ax, "i3", "i10", "D2 1N4148", kind="diode", dy=-0.6)
    _dash_hint(ax, "h14", "h15", "← RF（第 13 步断电后插）", at=(15.6, 1.0, "left"))
    x0, y0 = 4.0, -7.6                                                    # 压电片（板外）
    ax.add_patch(plt.Circle((x0 + 1.2, y0 + 0.7), 0.9, fc="#e0e0e0", ec="0.3", zorder=5))
    ax.add_patch(plt.Circle((x0 + 1.2, y0 + 0.7), 0.55, fc="#f5d76e", ec="0.4", zorder=6))
    ax.text(x0 + 2.4, y0 + 0.3, "压电片：红线（中间陶瓷面）→ j7，黑线（铜片）→ g3", fontsize=7.2, zorder=6)
    for h, k, pts in (("j7", "pos", [(x0 + 1.6, y0 + 1.5), (x0 + 1.6, -1.8), (7.0, -1.8)]),
                      ("g3", "gnd", [(x0 + 0.8, y0 + 1.5), (x0 + 0.8, -1.5), (2.4, -1.5), (2.4, 2.0)])):
        x1, y1 = bb.bb_xy(h)
        pts = pts + [(x1, y1)]
        ax.plot([q[0] for q in pts], [q[1] for q in pts], color=W[k], lw=2.0, zorder=7)
        ax.plot(x1, y1, "o", ms=3.5, color=W[k], zorder=8)
    _probes(ax)
    _assert_common(net)
    must(net, [["f15", "j15", "j10", "g10", "h10", "f10", "i10", "i15", "d11", "e11"], ["f14", "i14", "j14", "g14", "g13", "f13"],
               ["g3", "f3", "i3", "j3", "c16", "d16", "g16"]],
         apart=[("g7", "g10"), ("f10", "f3"), ("j7", "g3"), ("f16", "f15"), ("j3", "f10"), ("e11", "f13")])
    ax.text(9.0, -5.4, "和阶段一相比（断电改）：拔 S1、CS、j5 线；\nCF 换 100n；加 D1、D2（色环 = 阴极）和压电片",
            ha="left", va="top", fontsize=7.5, color=fs.C["bad"])
    print("[图 32-p4-5] 阶段二面包板：CF 100n i14–i15，SB e11/f13，RI g7–g10；D1 阳极 f10 阴极 f3，D2 阳极 i3 阴极 i10；压电片 j7/g3；RF h14–h15 虚线；连通检查通过")
    fs.save(fig, N, "32_p4_5_bb_stage2.png")


def p4_6():
    with drawing(fontsize=11) as d:
        ls.title(d, (4.0, 13.6), "阶段二：压电片（CF 100 nF，RF 10 MΩ 第 13 步才插，反并联钳位）")
        t = camp(d, 6.0, 4.0, cf="CF 100 nF（i14–i15）", rf="RF 10 MΩ", rf_dashed=True, rf_note="（第 13 步断电后插 h14–h15）",
                 ri="RI 10 kΩ", src=False, reset="复位按钮 SB（e11 / f13）")
        xs = t["si"][0]
        xq, xc = xs - 1.4, xs - 2.8                       # 电荷源、C_p 两条竖线（压电片 = 电荷源 ∥ C_p）
        d += elm.Line().at(t["si"]).to((xq, 4.0)); d += elm.Line().at((xq, 4.0)).to((xc, 4.0))
        d += elm.SourceI().at((xq, 0.8)).to((xq, 4.0))
        d += elm.Capacitor().at((xc, 0.8)).to((xc, 4.0))
        d += elm.Dot().at((xq, 4.0)); d += elm.Dot().at((xq, 0.8))
        d += elm.Line().at((xc, 0.8)).to((xq, 0.8))
        ls.lab(d, (xc - 0.5, 2.4), "Cp\n10～30 nF", ha="right", fs_=9)
        ls.lab(d, ((xq + xc) / 2, 4.6), "压电片（红线 j7 / 黑线 g3）", ha="center", fs_=9)
        d += elm.Line().at((xq, 0.8)).to((xq, 0.0)); d += elm.Dot(open=True).at((xq, 0.0))
        ls.lab(d, (xq, -0.5), "V_MID（第 3 列）", ha="center", fs_=9.5, color=fs.C["fb"])
        # 钳位：D1、D2 反并联在 N 和 V_MID 之间。N 取自 R_I 右端（2 脚一侧）那根竖线，向左上引出，避开 3 脚引线
        nx, ny = t["n"]
        yt, yb, ytop = ny + 1.3, ny + 1.7, ny + 3.5
        x1, x2 = nx - 3.6, nx - 2.4
        d += elm.Dot().at((nx, yt)); d += elm.Line().at((nx, yt)).to(((x1 + x2) / 2, yt))
        d += elm.Line().at(((x1 + x2) / 2, yt)).to(((x1 + x2) / 2, yb))
        d += elm.Line().at((x1, yb)).to((x2, yb))
        d += elm.Diode().at((x1, yb)).to((x1, ytop))           # D1：阳极接 N，阴极接 V_MID
        d += elm.Diode().at((x2, ytop)).to((x2, yb))           # D2：阳极接 V_MID，阴极接 N
        d += elm.Line().at((x1, ytop)).to((x2, ytop))
        d += elm.Line().at(((x1 + x2) / 2, ytop)).to(((x1 + x2) / 2, ytop + 0.6))
        d += elm.Dot(open=True).at(((x1 + x2) / 2, ytop + 0.6))
        ls.lab(d, ((x1 + x2) / 2, ytop + 1.05), "V_MID（第 3 列）", ha="center", fs_=9.5, color=fs.C["fb"])
        ls.lab(d, (x1 - 0.6, (yb + ytop) / 2), "D1\n阳 f10（N）\n阴 f3", ha="right", fs_=8.5)
        ls.lab(d, (x2 + 0.6, (yb + ytop) / 2), "D2\n阳 i3\n阴 i10（N）", ha="left", fs_=8.5)
        ls.lab(d, ((x1 + x2) / 2, yt - 0.35), "N（第 10 列）", ha="center", fs_=8.5, color=ls.GRAY)
        pwr(d, t["op"], 15.5, 12.4)
        o = t["out"]
        d += elm.Line().at(o).to((o[0] + 1.2, o[1])); d += elm.Dot(open=True).at((o[0] + 1.2, o[1]))
        ls.probe(d, (o[0] + 0.6, o[1]), "B", dx=0.0, dy=-1.2)
        ls.colnote(d, (o[0] + 1.4, o[1]), "第 14 列（1 脚）", "right")
        vo = _lab_vmid(d, 4.0, -4.0)
        ls.probe(d, vo, "A", dx=0.6, dy=-1.0)
    print("[图 32-p4-6] 阶段二原理图：压电片（电荷源 ∥ Cp）—RI 10 kΩ—N，D1/D2 反并联接在 N 与 V_MID 之间；CF 100 nF ∥ RF 10 MΩ（虚线）∥ 复位按钮 SB")
    save_schem(d, N, "32_p4_6_lab_stage2.png")


def p4_7():
    """思考题的接法图（结论在 page4 的折叠答案里，图上不写）。"""
    with drawing(fontsize=11) as d:
        ls.title(d, (-1.0, 13.0), "思考题 1：万用表从 N 碰 0 V（RF 插着）")
        camp(d, 0.0, 4.0, cf="CF 10n", rf="RF 10M", ri="RI 10k", src=True, cs="CS 1n")
        d += elm.Dot().at((0.0, 5.6))
        d += elm.MeterV().at((0.0, 5.6)).left().length(3.0).color(fs.C["bad"])
        d += elm.Line().at((-3.0, 5.6)).to((-4.6, 5.6)).color(fs.C["bad"])
        d += elm.Ground().at((-4.6, 5.6))
        ls.lab(d, (-4.6, 6.2), "0 V", ha="center", fs_=9.5)
        ls.title(d, (14.0, 13.0), "思考题 2：S1 的①改接 0 V、②接 +9 V")
        t2 = camp(d, 15.0, 4.0, cf="CF 10n", rf=None, ri="RI 10k", src=True, cs="CS 1n")
        sp = (t2["si"][0] - 2.6, 4.0)
        d += elm.Line().at(sp).to((sp[0], 3.2))
        d += (sw := elm.SwitchSpdt2().at((sp[0], 3.2)).down().anchor("a"))
        b_, c_ = sw.absanchors["b"], sw.absanchors["c"]
        lo, hi = (b_, c_) if b_[0] < c_[0] else (c_, b_)
        d += elm.Line().at(lo).to((lo[0], lo[1] - 0.6)); d += elm.Ground().at((lo[0], lo[1] - 0.6))
        ls.lab(d, (lo[0] - 0.2, lo[1] - 0.3), "① 0 V", ha="right", fs_=9)
        d += elm.Line().at(hi).to((hi[0] + 0.6, hi[1])); d += elm.Vdd().at((hi[0] + 0.6, hi[1])).label("+9 V", fontsize=9)
        ls.lab(d, (hi[0] + 0.1, hi[1] - 0.45), "②", ha="left", fs_=9.5)
        ls.lab(d, (sp[0] - 0.7, 2.6), "S1", ha="right", fs_=9.5, color=fs.C["fb"])
        ls.title(d, (6.0, -4.0), "思考题 3：阶段二把 CF 换成 1 nF")
        t3 = camp(d, 7.0, -10.0, cf="CF 1n", rf="RF 10M", ri="RI 10k", src=False)
        xs = t3["si"][0]
        d += elm.Line().at(t3["si"]).to((xs - 1.2, -10.0))
        d += elm.SourceI().at((xs - 1.2, -13.2)).to((xs - 1.2, -10.0)); ls.lab(d, (xs - 1.8, -11.6), "压电片", ha="right", fs_=9.5)
        d += elm.Line().at((xs - 1.2, -13.2)).to((xs - 1.2, -14.0)); d += elm.Dot(open=True).at((xs - 1.2, -14.0))
        ls.lab(d, (xs - 1.2, -14.5), "V_MID", ha="center", fs_=9.5, color=fs.C["fb"])
    print("[图 32-p4-7] 思考题接法：(1) 万用表 N→0 V；(2) S1 ①0 V/②+9 V；(3) 阶段二 CF 1 nF")
    save_schem(d, N, "32_p4_7_think.png")


if __name__ == "__main__":
    names = sys.argv[1:] or [k for k in list(globals()) if k[:2] in ("p1", "p2", "p3", "p4") and k[2] == "_" and callable(globals()[k])]
    for k in names:
        globals()[k]()
