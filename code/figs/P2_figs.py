"""P2 半导体入门：全部配图（电路图 + 特性曲线）。
运行：/workspace/circuits-venv/bin/python code/figs/P2_figs.py
图上的每个数字都由 fs.mark 或 print 打印；关键结论用 assert 检查。
器件模型是教学用的简化模型，参数取自数据手册的典型值（出处见 notes/P2-research.md）。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
import figstyle as fs
import schem
import schemdraw.elements as elm

P = "P2"
VT = 0.02585          # 热电压 kT/q，室温约 25.85 mV


# ---------------- 简化器件模型 ----------------
def diode_i(v, Is=1e-14, n=1.0):
    """肖克利二极管方程：I = Is·(e^(V/(n·VT)) − 1)。Is=1e-14 A、n=1 时硅管 1 mA 约 0.65 V。"""
    return Is * (np.exp(np.clip(v, -5, 3.5) / (n * VT)) - 1)


def diode_v(i, Is=1e-14, n=1.0):
    """反解：给定正向电流求压降。"""
    return n * VT * np.log(i / Is + 1)


LED_IS, LED_N = 1e-18, 2.0   # 红色 LED 的示意参数：10 mA 时压降约 1.9 V


IZT = 49e-3           # 1N4733A 的测试电流 I_ZT：手册的 V_Z = 5.1 V 就是在这个电流下测的


def zener_v(iz, vz=5.1, rz=7.0, izt=IZT):
    """击穿区模型 V = V_Z + r_Z·(I_Z − I_ZT)：I_Z = I_ZT 时正好等于手册的 V_Z。"""
    return vz + rz * (iz - izt)


def zener_i(v, vz=5.1, rz=7.0, izt=IZT):
    """稳压管（以阳极→阴极为正方向）：正向像普通二极管；反向电压超过 V_Z − r_Z·I_ZT 后，
    电流按 1/rz 急剧增大（击穿区是一条直线，I_Z = I_ZT 时两端电压正好是 V_Z）。"""
    fwd = diode_i(v)
    v0 = vz - rz * izt                                    # 直线外推到电流为 0 的电压，约 4.757 V
    rev = np.where(v < -v0, (v + v0) / rz, 0.0)          # 击穿后的近似直线，斜率 1/rz
    return fwd + rev


def bjt_ic(vce, ib, beta=100.0, vk=0.06):
    """三极管输出特性（示意）：放大区 I_C = β·I_B；V_CE 很小时进入饱和，I_C 被压下来。"""
    return beta * ib * (1 - np.exp(-vce / vk))


def mos_id(vgs, vth=2.1, k=0.2):
    """MOS 管转移特性（平方律，示意）：V_GS < V_th 时 I_D≈0；之后 I_D = k/2·(V_GS − V_th)²。"""
    ov = np.clip(vgs - vth, 0, None)
    return 0.5 * k * ov ** 2


def mos_rdson(vgs, vth=2.1, k=0.2):
    """完全导通时的导通电阻 R_DS(on) ≈ 1 / (k·(V_GS − V_th))（平方律模型的线性区）。"""
    return 1.0 / (k * (vgs - vth))


def bjt_switch(vin, rb, rc, vcc=5.0, beta=100.0, vbe=0.7, vcesat=0.2):
    """三极管开关的直流工作点（分段模型）：返回 (I_B, I_C, V_CE, 区域)。"""
    ib = max(0.0, (vin - vbe) / rb)
    ic_max = (vcc - vcesat) / rc
    if ib == 0:
        return 0.0, 0.0, vcc, "截止"
    if beta * ib < ic_max:
        ic = beta * ib
        return ib, ic, vcc - ic * rc, "放大"
    return ib, ic_max, vcesat, "饱和"


# ================= page1 =================
def p1_1():
    """二极管正接、反接：灯亮 / 灯不亮。"""
    with schem.drawing(fontsize=11) as d:
        for x0, rev, txt, lamp in [(0, False, "二极管正接", "灯亮"), (7, True, "二极管反接", "灯不亮")]:
            d += elm.SourceV().endpoints((x0, 0), (x0, 3)).label("6 V", loc="bottom")
            d += elm.Line().endpoints((x0, 3), (x0 + 1, 3))
            dd = elm.Diode().endpoints((x0 + 1, 3), (x0 + 4, 3)).label(txt, loc="top")
            d += dd.reverse() if rev else dd
            d += elm.Lamp().endpoints((x0 + 4, 3), (x0 + 4, 0)).label(lamp, loc="bottom")
            d += elm.Line().endpoints((x0 + 4, 0), (x0, 0))
    schem.save_schem(d, P, "P2_p1_1_diode_valve.png")


def p1_2():
    """稳压管：串电阻接 12 V，两端稳定在 5.1 V。"""
    with schem.drawing(fontsize=11) as d:
        d += elm.SourceV().endpoints((0, 0), (0, 3)).label("12 V", loc="bottom")
        d += elm.Resistor().endpoints((0, 3), (3, 3)).label("R  1 kΩ", loc="top")
        d += elm.Zener().endpoints((3, 0), (3, 3)).label("稳压管\n$V_Z$ = 5.1 V", loc="bottom")
        d += elm.Line().endpoints((3, 3), (5, 3))
        d += elm.Dot(open=True).at((5, 3)).label("输出约 5.1 V", loc="right")
        d += elm.Line().endpoints((3, 0), (0, 0))
        d += elm.Line().endpoints((3, 0), (5, 0))
        d += elm.Dot(open=True).at((5, 0)).label("0 V", loc="right")
    schem.save_schem(d, P, "P2_p1_2_zener.png")


def p1_3():
    """三极管与 MOS 管各当一个开关，点亮 LED。"""
    with schem.drawing(fontsize=11) as d:
        # 左：NPN 三极管
        d += elm.Line().endpoints((2, 6), (4, 6))
        d += elm.Dot(open=True).at((2, 6)).label("+5 V", loc="left")
        d += elm.Resistor().endpoints((4, 6), (4, 4.2)).label("$R_C$\n220 Ω", loc="bottom")
        d += elm.LED().endpoints((4, 4.2), (4, 2.6))
        q = elm.BjtNpn().theta(0).anchor("collector").at((4, 2.6))
        d += q
        d += elm.Resistor().endpoints((q.base[0] - 2.5, q.base[1]), q.base).label("$R_B$  10 kΩ", loc="top")
        d += elm.Dot(open=True).at((q.base[0] - 2.5, q.base[1])).label("控制 0/5 V", loc="left")
        d += elm.Ground().at(q.emitter)
        d += elm.Label().at((2.6, -0.4)).label("三极管：小电流 $I_B$ 控制大电流 $I_C$")
        # 右：N 沟道 MOS 管
        x = 9.5
        d += elm.Line().endpoints((x - 2, 6), (x, 6))
        d += elm.Dot(open=True).at((x - 2, 6)).label("+5 V", loc="left")
        d += elm.Resistor().endpoints((x, 6), (x, 4.2)).label("$R_D$\n220 Ω", loc="bottom")
        d += elm.LED().endpoints((x, 4.2), (x, 2.6))
        m = elm.NFet().theta(0).reverse().anchor("drain").at((x, 2.6))
        d += m
        g = m.gate
        d += elm.Line().endpoints((g[0] - 2.5, g[1]), g)
        d += elm.Dot(open=True).at((g[0] - 2.5, g[1])).label("控制 0/5 V", loc="left")
        d += elm.Dot().at((g[0] - 0.8, g[1]))
        d += elm.Resistor().endpoints((g[0] - 0.8, g[1]), (g[0] - 0.8, m.source[1] - 0.3)).label("$R_{GS}$\n100 kΩ", loc="bottom")
        d += elm.Line().endpoints((g[0] - 0.8, m.source[1] - 0.3), (m.source[0], m.source[1] - 0.3))
        d += elm.Line().endpoints(m.source, (m.source[0], m.source[1] - 0.3))
        d += elm.Ground().at((m.source[0], m.source[1] - 0.3))
        d += elm.Label().at((8.6, -0.4)).label("MOS 管：电压 $V_{GS}$ 控制电流")
    schem.save_schem(d, P, "P2_p1_3_switches.png")


# ================= page2 =================
def p2_1():
    """普通硅二极管与红色 LED 的正向伏安特性。"""
    v = np.linspace(0, 2.4, 1200)
    i_si = diode_i(v) * 1e3
    i_led = diode_i(v, LED_IS, LED_N) * 1e3
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(v, i_si, **fs.LS["vin"], label="硅二极管（如 1N4148）")
    ax.plot(v, i_led, **fs.LS["third"], label="红光 LED")
    v1 = float(diode_v(1e-3)); v10 = float(diode_v(10e-3))
    vl10 = float(diode_v(10e-3, LED_IS, LED_N))
    fs.ref_h(ax, 10)
    fs.mark(ax, v10, 10, fmt="{:.0f}", unit=" mA", dx=-58, dy=4)
    print(f"[数值] 硅管 1 mA 压降 {v1:.3f} V，10 mA 压降 {v10:.3f} V；LED 10 mA 压降 {vl10:.2f} V")
    fs.ref_v(ax, v10, f"{v10:.2f} V")
    fs.ref_v(ax, vl10, f"{vl10:.2f} V")
    ax.set_ylim(-1, 25); ax.set_xlim(0, 2.4)
    fs.axlabels(ax, "二极管两端电压 $V_D$", "V", "电流", "mA")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.85))
    assert 0.6 < v1 < 0.7 and 0.68 < v10 < 0.75, "硅管压降应在 0.7 V 左右"
    assert 1.8 < vl10 < 2.1, "红色 LED 压降应在 2 V 左右"
    assert diode_v(20e-3) - diode_v(1e-3) < 0.1, "电流涨 20 倍，压降只涨不到 0.1 V"
    fs.save(fig, P, "P2_p2_1_diode_iv.png")
    return v1, v10, vl10


def p2_2():
    """稳压管完整伏安特性：正向像二极管，反向在 −5.1 V 处击穿后电压几乎不变。"""
    v = np.linspace(-6.0, 1.0, 3000)
    i = zener_i(v) * 1e3
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(v, i, **fs.LS["third"], label="稳压管 5.1 V（如 1N4733A）")
    fs.ref_h(ax, 0)
    fs.ref_v(ax, -5.1, "$-V_Z$ = −5.1 V（测试电流 49 mA 处）")
    # 反向电流 5 mA 和 49 mA（测试电流 I_ZT）时的电压，模型 V = V_Z + r_Z·(I_Z − I_ZT)
    v5 = -zener_v(5e-3); v49 = -zener_v(49e-3)
    fs.mark(ax, v5, -5, fmt="{:.0f}", unit=" mA", dx=6, dy=-2)
    fs.mark(ax, v49, -49, fmt="{:.0f}", unit=" mA", dx=6, dy=-2)
    print(f"[数值] 反向 5 mA 时 V = {v5:.3f} V，反向 49 mA 时 V = {v49:.3f} V，相差 {v5 - v49:.3f} V")
    ax.text(-2.8, 6, "反向未击穿：几乎没有电流", ha="center", fontsize=9)
    ax.text(-4.9, -38, "击穿区：电流变化很大，\n电压几乎不变", ha="left", fontsize=9)
    ax.set_ylim(-60, 20)
    fs.axlabels(ax, "两端电压（阳极减阴极）", "V", "电流", "mA")
    ax.legend(loc="lower right")
    assert abs(v5 - v49) < 0.35, "5→49 mA 电压变化应小于 0.35 V"
    assert abs(v49 + 5.1) < 1e-9, "测试电流 49 mA 时必须正好等于手册 V_Z = 5.1 V"
    assert abs(float(zener_i(v49)) * 1e3 + 49) < 1e-6, "曲线与公式一致：−5.1 V 处电流 −49 mA"
    fs.save(fig, P, "P2_p2_2_zener_iv.png")
    return v5, v49


def p2_3():
    """NPN 输出特性 + 负载线：三个工作区。"""
    vcc, rc, beta = 5.0, 1000.0, 100.0
    vce = np.linspace(0, 5.5, 600)
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    for ib_ua, key in [(10, "vin"), (20, "vout"), (30, "third"), (40, "fb"), (60, "cur")]:
        ax.plot(vce, bjt_ic(vce, ib_ua * 1e-6, beta) * 1e3, **fs.LS[key], label=f"$I_B$ = {ib_ua} µA")
    ax.plot(vce, (vcc - vce) / rc * 1e3, **fs.LS["good"], label="负载线（$V_{CC}$ = 5 V，$R_C$ = 1 kΩ）")
    pts = []
    for vin in [0.0, 1.64, 5.0]:
        ib, ic, v, reg = bjt_switch(vin, 47e3, rc, vcc, beta)
        pts.append((reg, ib, ic, v))
        fs.mark(ax, v, ic * 1e3, fmt="{:.1f}", unit=f" mA（{reg}）", dx=6, dy=4)
        print(f"[数值] V_in={vin} V, R_B=47k: I_B={ib*1e6:.1f} µA, I_C={ic*1e3:.2f} mA, V_CE={v:.2f} V, {reg}")
    ax.set_xlim(0, 5.5); ax.set_ylim(-0.3, 6.5)
    fs.axlabels(ax, "集电极-发射极电压 $V_{CE}$", "V", "集电极电流 $I_C$", "mA")
    ax.legend(loc="upper right", fontsize=8)
    assert [p[0] for p in pts] == ["截止", "放大", "饱和"]
    assert abs(pts[1][2] - beta * pts[1][1]) < 1e-9, "放大区 I_C = β·I_B"
    assert pts[2][3] < 0.3 and pts[2][2] < beta * pts[2][1], "饱和区 V_CE 很小，且 I_C < β·I_B"
    fs.save(fig, P, "P2_p2_3_bjt_regions.png")
    return pts


def p2_4():
    """N 沟道 MOS 管转移特性：I_D 随 V_GS 变化，阈值 V_GS(th)≈2.1 V。"""
    vgs = np.linspace(0, 6, 600)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(vgs, mos_id(vgs) * 1e3, **fs.LS["cur"], label="漏极电流 $I_D$（示意模型）")
    fs.ref_v(ax, 2.1, "$V_{GS(th)}$ ≈ 2.1 V", y=0.6)
    vals = {}
    for vg in [1.5, 3.3, 5.0]:
        idv = float(mos_id(vg)) * 1e3
        vals[vg] = idv
        fs.mark(ax, vg, idv, fmt="{:.0f}", unit=" mA", dx=-50 if vg > 4 else 6, dy=6)
        print(f"[数值] V_GS={vg} V → I_D={idv:.1f} mA")
    fs.axlabels(ax, "栅源电压 $V_{GS}$", "V", "漏极电流 $I_D$", "mA")
    ax.legend(loc="upper left")
    assert vals[1.5] == 0.0 and vals[5.0] > 5 * vals[3.3], "阈值以下不导通；5 V 驱动比 3.3 V 强得多"
    fs.save(fig, P, "P2_p2_4_mos_transfer.png")
    return vals


# ================= page3 =================
def p3_1():
    """改 R_B：β=60 与 β=200 两只管子的 V_CE。"""
    vcc, rc, vin = 5.0, 100.0, 3.3      # 单片机 3.3 V 驱动，负载 100 Ω，饱和时 I_C = 48 mA
    rbs = np.linspace(500, 15000, 400)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    out = {}
    for beta, key, lab in [(60, "vout", "β = 60（数据手册 50 mA 时的最小值）"), (200, "third", "β = 200（偏大的管子）")]:
        v = np.array([bjt_switch(vin, rb, rc, vcc, beta)[2] for rb in rbs])
        ax.plot(rbs / 1e3, v, **fs.LS[key], label=lab)
        rb_edge = (vin - 0.7) / ((vcc - 0.2) / rc / beta)
        out[beta] = rb_edge
        fs.ref_v(ax, rb_edge / 1e3, f"{rb_edge/1e3:.1f} kΩ", y=0.55 if beta == 60 else 0.3)
        print(f"[数值] β={beta}: R_B ≤ {rb_edge:.0f} Ω 才饱和")
    fs.ref_h(ax, 0.2, "饱和 $V_{CE}$ ≈ 0.2 V", x=0.98)
    fs.mark(ax, 1.0, bjt_switch(vin, 1000, rc, vcc, 60)[2], fmt="{:.1f}", unit=" V", dx=4, dy=6)
    fs.axlabels(ax, "基极电阻 $R_B$", "kΩ", "$V_{CE}$", "V")
    ax.legend(loc="upper left", fontsize=8)
    assert out[60] < out[200]
    assert bjt_switch(vin, 4700, rc, vcc, 60)[3] == "放大", "β 小的管子配 4.7 kΩ 不饱和"
    assert bjt_switch(vin, 4700, rc, vcc, 200)[3] == "饱和", "β 大的管子配 4.7 kΩ 能饱和"
    v47 = bjt_switch(vin, 4700, rc, vcc, 60)[2]
    fs.mark(ax, 4.7, v47, fmt="{:.2f}", unit=" V", dx=6, dy=4)
    assert bjt_switch(vin, 1000, rc, vcc, 60)[3] == "饱和"
    fs.save(fig, P, "P2_p3_1_rb_sweep.png")
    return out


def p3_2():
    """MOS 管导通电阻随 V_GS 变化，以及 0.2 A 时的发热。"""
    vgs = np.linspace(2.6, 10, 400)
    r = mos_rdson(vgs)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(vgs, r, **fs.LS["vout"], label="$R_{DS(on)}$（示意模型）")
    res = {}
    for vg in [3.3, 5.0, 10.0]:
        rv = float(mos_rdson(vg)); res[vg] = rv
        fs.mark(ax, vg, rv, fmt="{:.2f}", unit=" Ω", dx=6, dy=4)
        print(f"[数值] V_GS={vg} V: R_DS(on)={rv:.2f} Ω，0.2 A 时发热 {0.2**2*rv*1e3:.0f} mW")
    fs.ref_v(ax, 2.1, "$V_{GS(th)}$", y=0.5)
    ax.set_ylim(0, 6); ax.set_xlim(1.8, 10.5)
    fs.axlabels(ax, "栅源电压 $V_{GS}$", "V", "导通电阻", "Ω")
    ax.legend(loc="upper right")
    assert res[3.3] > 3 * res[10.0], "只比阈值高一点时，导通电阻大好几倍"
    fs.save(fig, P, "P2_p3_2_rdson.png")
    return res


if __name__ == "__main__":
    fs.check_cjk("二极管正接反接灯亮不亮稳压管输出约三极管小电流控制大电流沟道示意模型硅红色击穿区变化很大几乎未没有集电极发射负载线截止放大饱和栅源漏阈值基数据手册最小偏导通电阻热")
    p1_1(); p1_2(); p1_3()
    p2_1(); p2_2(); p2_3(); p2_4()
    p3_1(); p3_2()
    print("P2_figs OK")


# ======================================================================================
# 动手实验篇（page4）用的面包板俯视图小工具。
# 各节点 figs 脚本里各带一份同样的代码（共享模块只由总纲修改）；以后可以挪进 code/figs/ 的共享模块。
# 坐标：列号 1～30 从左到右；a～e 行在上半块，f～j 行在下半块，中间是隔离槽；
# 上下各有两条电源轨，名字用 "T1"（最上）、"T2"、"B1"、"B2"（最下）加列号，例如 "T1-5"。
# 同一列的 a～e 五个孔是连通的，f～j 五个孔是连通的；同一条电源轨整条连通。
# ======================================================================================
import matplotlib.pyplot as _bb_plt
from matplotlib.patches import Rectangle as _BbRect, Polygon as _BbPoly, Wedge as _BbWedge

BB_ROWY = {r: y for r, y in zip("abcdefghij", [9, 8, 7, 6, 5, 3, 2, 1, 0, -1])}
BB_RAILY = {"T1": 11.6, "T2": 10.8, "B1": -2.8, "B2": -3.6}
BB_WIRE = dict(pos="#CC0000", gnd="#000000", neg=fs.C["third"], sig=fs.C["vin"], out=fs.C["vout"])


def bb_xy(h):
    """孔名 → 坐标：'a5' → (5, 9)；'T1-5' → (5, 11.6)。"""
    if h[:2] in BB_RAILY:
        return float(h.split("-")[1]), BB_RAILY[h[:2]]
    return float(h[1:]), float(BB_ROWY[h[0]])


def bb_board(cols=30, rails=None, figsize=(10, 5.6)):
    """画空白面包板。rails = {"T1": ("+9 V", 颜色), ...}，只画给出的电源轨。返回 (fig, ax)。"""
    rails = rails or {}
    fig, ax = _bb_plt.subplots(figsize=figsize)
    ax.set_xlim(-1.6, cols + 4.2); ax.set_ylim(-5.5, 12.7)
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(_BbRect((0.2, -4.2), cols + 0.6, 16.4, fc="#f4f1ea", ec="0.6", lw=0.8, zorder=0))
    ax.add_patch(_BbRect((0.2, 3.65), cols + 0.6, 0.7, fc="#e4e0d6", ec="none", zorder=0))   # 中间隔离槽
    for c in range(1, cols + 1):
        for r, y in BB_ROWY.items():
            ax.plot(c, y, "s", ms=2.6, color="0.55", zorder=1)
        if c == 1 or c % 5 == 0:
            ax.text(c, 9.65, str(c), ha="center", va="bottom", fontsize=7, color="0.3")
            ax.text(c, -1.75, str(c), ha="center", va="top", fontsize=7, color="0.3")
    for r, y in BB_ROWY.items():
        ax.text(0.45, y, r, ha="center", va="center", fontsize=7, color="0.3")
        ax.text(cols + 0.55, y, r, ha="center", va="center", fontsize=7, color="0.3")
    for name, y in BB_RAILY.items():
        if name not in rails:
            continue
        text, col = rails[name]
        ax.plot([0.7, cols + 0.3], [y + 0.32, y + 0.32], color=col, lw=0.9, zorder=1)
        for c in range(1, cols + 1):
            ax.plot(c, y, "s", ms=2.6, color="0.55", zorder=1)
        ax.text(cols + 1.0, y, text, ha="left", va="center", fontsize=8, color=col)
    return fig, ax


def bb_wire(ax, a, b, kind="sig", via=()):
    """跳线：kind 取 pos/gnd/neg/sig/out（红/黑/红紫/蓝/橙）。via=[(x, y), ...] 时按这些拐点折线走，避免压住元件。"""
    pts = [bb_xy(a)] + list(via) + [bb_xy(b)]
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=BB_WIRE[kind], lw=2.4, solid_capstyle="round", zorder=3)
    ax.plot([xs[0], xs[-1]], [ys[0], ys[-1]], "o", ms=4, color=BB_WIRE[kind], zorder=4)


def _bb_label(ax, x, y, text, fs_=7.5):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs_, zorder=6,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))


def bb_res(ax, a, b, text, dy=0.55):
    """电阻：两条引脚 + 中间米色小方块，标签写在方块旁边。"""
    (x0, y0), (x1, y1) = bb_xy(a), bb_xy(b)
    ax.plot([x0, x1], [y0, y1], color="0.25", lw=1.2, zorder=4)
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    horiz = abs(x1 - x0) >= abs(y1 - y0)
    w, h = (0.9, 0.36) if horiz else (0.36, 0.9)
    ax.add_patch(_BbRect((xm - w / 2, ym - h / 2), w, h, fc="#e8cf9c", ec="0.25", lw=0.8, zorder=5))
    if horiz:
        _bb_label(ax, xm, ym + dy, text)
    else:
        _bb_label(ax, xm + (0.85 if dy > 0 else -0.85), ym, text)
    for x, y in ((x0, y0), (x1, y1)):
        ax.plot(x, y, "o", ms=3, color="0.25", zorder=5)


def bb_part2(ax, a, b, text, kind="diode", dy=0.55, fc="white"):
    """两脚元件：kind = diode（a 脚是阳极，b 脚是阴极，画竖杠）、led（同上，填色）、cap（电解电容，a 脚是正极）、box。"""
    (x0, y0), (x1, y1) = bb_xy(a), bb_xy(b)
    ax.plot([x0, x1], [y0, y1], color="0.25", lw=1.2, zorder=4)
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    L = max(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5, 1e-9)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L          # 从 a 指向 b 的单位向量
    nx, ny = -uy, ux
    s = 0.32
    if kind in ("diode", "led"):
        tri = [(xm - ux * s + nx * s, ym - uy * s + ny * s), (xm - ux * s - nx * s, ym - uy * s - ny * s),
               (xm + ux * s, ym + uy * s)]
        ax.add_patch(_BbPoly(tri, closed=True, fc=(fc if kind == "led" else "0.25"), ec="0.2", lw=0.8, zorder=5))
        ax.plot([xm + ux * s + nx * s, xm + ux * s - nx * s], [ym + uy * s + ny * s, ym + uy * s - ny * s],
                color="0.1", lw=1.6, zorder=5)
    elif kind == "cap":
        ax.add_patch(_BbRect((xm - 0.32, ym - 0.32), 0.64, 0.64, fc="#3b5b92", ec="0.2", lw=0.8, zorder=5))
        _bb_label(ax, x0 + ux * 0.35 + nx * 0.35, y0 + uy * 0.35 + ny * 0.35, "+", fs_=8)
    else:
        ax.add_patch(_BbRect((xm - 0.4, ym - 0.3), 0.8, 0.6, fc=fc, ec="0.2", lw=0.8, zorder=5))
    if abs(x1 - x0) >= abs(y1 - y0):
        _bb_label(ax, xm, ym + dy, text)
    else:
        _bb_label(ax, xm + (0.85 if dy > 0 else -0.85), ym, text)
    for x, y in ((x0, y0), (x1, y1)):
        ax.plot(x, y, "o", ms=3, color="0.25", zorder=5)


def bb_block(ax, holes, text, pins=None, fc="white", pad=0.38, fs_=7.5, tdy=0.0):
    """多脚元件（三极管、继电器、电位器、按钮、电池盒等）：画一个盖住这些孔的方块，pins 给每只脚的小字。
    tdy ≠ 0 时把元件名挪到方块上方（tdy > 0）或下方（tdy < 0），免得压住引脚。"""
    pts = [bb_xy(h) for h in holes]
    xs, ys = zip(*pts)
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    ax.add_patch(_BbRect((x0, y0), x1 - x0, y1 - y0, fc=fc, ec="0.2", lw=0.9, alpha=0.92, zorder=5))
    if tdy:
        _bb_label(ax, (x0 + x1) / 2, (y1 + tdy) if tdy > 0 else (y0 + tdy), text, fs_=fs_)
    else:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center", fontsize=fs_, zorder=6)
    for i, (x, y) in enumerate(pts):
        ax.plot(x, y, "o", ms=3, color="0.2", zorder=6)
        if pins:
            ax.text(x, y - 0.42, pins[i], ha="center", va="top", fontsize=6, color="0.15", zorder=6)


def bb_dip8(ax, col, text="LM358"):
    """8 脚芯片跨在隔离槽上：1～4 脚在 f 行第 col～col+3 列，8～5 脚在 e 行第 col～col+3 列，缺口朝左。"""
    ax.add_patch(_BbRect((col - 0.45, 3.25), 3.9, 2.15, fc="0.18", ec="0.1", zorder=5))
    ax.add_patch(_BbWedge((col - 0.45, 4.3), 0.3, -90, 90, fc="#f4f1ea", ec="none", zorder=6))
    ax.text(col + 1.5, 4.3, text, ha="center", va="center", fontsize=8, color="white", zorder=6)
    for k in range(4):
        ax.text(col + k, 3.55, str(k + 1), ha="center", va="center", fontsize=6.5, color="white", zorder=6)
        ax.text(col + k, 5.05, str(8 - k), ha="center", va="center", fontsize=6.5, color="white", zorder=6)


def bb_probe(ax, h, text, dx=0.0, dy=0.9):
    """测量点：朱红色以外的黑框圆圈 + 编号，指向某个孔。"""
    x, y = bb_xy(h)
    ax.annotate(text, (x, y), (x + dx, y + dy), ha="center", va="center", fontsize=7.5, zorder=7,
                bbox=dict(boxstyle="circle,pad=0.15", fc=fs.C["hi"], ec="0.2", lw=0.7),
                arrowprops=dict(arrowstyle="-", color="0.2", lw=0.7))


def bb_legend(ax, items, x=1.0, y=-5.0):
    """底部图例：items = [(kind, 文字), ...]。"""
    for i, (kind, text) in enumerate(items):
        xx = x + i * 6.2
        ax.plot([xx, xx + 1.0], [y, y], color=BB_WIRE[kind], lw=2.4)
        ax.text(xx + 1.25, y, text, ha="left", va="center", fontsize=7.5)


def bb_ng_op(body, exprs, includes=()):
    """用 ngspice 跑一次直流工作点（.op），返回 {表达式: 数值}。body 是网表正文，exprs 如 ["v(out)", "i(v1)"]；
    includes 是 spice/models/ 下的模型文件名。网表写在临时目录，跑完即删，仓库里不留文件。"""
    import os as _os, re as _re, shutil as _sh, subprocess as _sp, tempfile as _tf
    models = _os.path.abspath(_os.path.join(_os.path.dirname(fs.__file__), "..", "..", "spice", "models"))
    inc = "\n".join(f".include {_os.path.join(models, m)}" for m in includes)
    prints = "\n".join(f"print {e}" for e in exprs)
    cir = f"* page4 工作点\n{inc}\n{body}\n.control\nop\n{prints}\n.endc\n.end\n"
    tmp = _tf.mkdtemp(prefix="p4op_")
    try:
        with open(_os.path.join(tmp, ".spiceinit"), "w") as f:
            f.write("set ngbehavior=psa\nset num_threads=1\n")      # 读入 PSpice 格式的厂家模型
        with open(_os.path.join(tmp, "op.cir"), "w", encoding="utf-8") as f:
            f.write(cir)
        r = _sp.run([_sh.which("ngspice") or "/usr/bin/ngspice", "-b", "op.cir"], cwd=tmp,
                    capture_output=True, text=True, timeout=300)
    finally:
        _sh.rmtree(tmp, ignore_errors=True)
    vals = {k.lower(): float(v) for k, v in _re.findall(r"^\s*(\S+)\s*=\s*([-+0-9.eE]+)\s*$", r.stdout, _re.M)}
    out = {e: vals.get(e.lower()) for e in exprs}
    assert r.returncode == 0 and None not in out.values(), f"ngspice 失败：{r.stdout[-800:]}{r.stderr[-800:]}"
    return out


# ---------------- 动手实验篇（page4）：数值（每个数都打印并断言） ----------------
P4_VIN = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0]      # 电位器滑动端调到的几个电压（逐点测二极管伏安特性）


def p4_numbers():
    """page4 的期望读数。二极管、稳压管用 ngspice + 厂家模型（1N4148 Nexperia、1N4733A Diodes Inc.）现算；
    三极管开关的读数照搬 review/spice/P2.md 的面包板核对表。"""
    # ① 1N4148 + 1 kΩ：先算 5 V 时的工作点，再算电位器调到几个电压时的点
    body = "\n".join(f"V{k} in{k} 0 {v}\nR{k} in{k} d{k} 1k\nXD{k} d{k} 0 1N4148" for k, v in enumerate(P4_VIN))
    r = bb_ng_op(body, [f"v(d{k})" for k in range(len(P4_VIN))], ["1N4148_nexperia.lib"])
    vd = np.array([r[f"v(d{k})"] for k in range(len(P4_VIN))])
    idd = (np.array(P4_VIN) - vd) / 1e3 * 1e3                # mA
    for v, a, b in zip(P4_VIN, vd, idd):
        print(f"[P2 page4] 1N4148 + 1 kΩ，输入 {v:.1f} V：二极管 {a:.3f} V，电阻 {v - a:.2f} V，电流 {b:.2f} mA")
    assert 0.66 <= vd[-1] <= 0.71, "5 V 时应落在 review 表的 0.66–0.71 V 里"
    assert vd[1] < vd[-1] < vd[1] + 0.12, "电流从 0.3 mA 涨到 4.3 mA，压降只多了约 0.1 V"
    # ② 1N4733A：9 V 电池 + 560 Ω，空载 / 接 1 kΩ / 接 470 Ω
    z = bb_ng_op("V1 a 0 9\nR1 a z1 560\nXZ1 0 z1 DI_1N4733A\n"
                 "R2 a z2 560\nXZ2 0 z2 DI_1N4733A\nRL2 z2 0 1k\n"
                 "R3 a z3 560\nXZ3 0 z3 DI_1N4733A\nRL3 z3 0 470",
                 ["v(z1)", "v(z2)", "v(z3)"], ["1N47xxA_diodes_zener.lib"])
    vz0, vz1k, vz470 = z["v(z1)"], z["v(z2)"], z["v(z3)"]
    iz0 = (9 - vz0) / 560
    print(f"[P2 page4] 9 V / 560 Ω / 1N4733A：空载 {vz0:.2f} V（V_Z ±5% → {vz0 * 0.95:.2f}～{vz0 * 1.05:.2f} V），"
          f"稳压管电流 {iz0 * 1e3:.1f} mA，电阻上 {9 - vz0:.2f} V")
    print(f"[P2 page4] 接 1 kΩ 负载：{vz1k:.2f} V（{vz1k * 0.95:.2f}～{vz1k * 1.05:.2f} V），负载电流 {vz1k / 1e3 * 1e3:.1f} mA，"
          f"稳压管剩 {((9 - vz1k) / 560 - vz1k / 1e3) * 1e3:.1f} mA")
    lo = 9 * 470 * 0.95 / (470 * 0.95 + 560 * 1.05); hi = 9 * 470 * 1.05 / (470 * 1.05 + 560 * 0.95)
    print(f"[P2 page4] 接 470 Ω 负载：{vz470:.2f} V，稳压管几乎不导电，等于普通分压 9×470/(560+470) = "
          f"{9 * 470 / 1030:.2f} V（电阻公差 → {lo:.2f}～{hi:.2f} V）")
    assert abs(vz0 - 4.99) < 0.02 and abs(iz0 * 1e3 - 7.2) < 0.1, "和 review 表 12 V/1 kΩ（约 7 mA，约 5.0 V）同一个工作点"
    assert vz0 - vz1k < 0.1, "接 1 kΩ 负载，输出只掉几十毫伏"
    assert abs(vz470 - 9 * 470 / 1030) < 0.02, "接 470 Ω 后稳压管退出，变成普通分压"
    assert (round(lo, 2), round(hi, 2)) == (3.88, 4.33)
    # ③ 三极管放大区：Vin 1.64 V、RB 47 kΩ、RC 1 kΩ，页面公式 V_C = 5 − β·I_B·R_C（饱和时约 0.2 V）
    ib = (1.64 - 0.7) / 47e3
    for beta in (100, 130, 230):
        vc = max(5 - beta * ib * 1e3, 0.2)
        print(f"[P2 page4] β = {beta}：I_B = {ib * 1e6:.0f} μA，集电极 {vc:.2f} V")
    assert abs(ib * 1e6 - 20) < 0.1 and abs(5 - 100 * ib * 1e3 - 3.0) < 0.01 and 5 - 230 * ib * 1e3 < 0.5
    print(f"[P2 page4] 饱和时 LED 电流约 (5 − 2 − 0.1)/220 = {(5 - 2 - 0.1) / 220 * 1e3:.0f} mA，"
          f"基极电流约 (5 − 0.75)/10k = {(5 - 0.75) / 10e3 * 1e3:.2f} mA")
    return vd, idd


# ---------------- 图 P2-p4-1：面包板接线图 ----------------
def p4_1_breadboard():
    rails = {"T1": ("+5 V", BB_WIRE["pos"]), "T2": ("GND", BB_WIRE["gnd"]),
             "B1": ("+9 V（电池）", BB_WIRE["pos"]), "B2": ("GND", BB_WIRE["gnd"])}
    fig, ax = bb_board(30, rails, figsize=(10, 6.2))
    bb_wire(ax, "T2-2", "B2-2", "gnd", via=[(-1.0, 10.8), (-1.0, -3.6)])     # 只连地，+5 V 和 +9 V 不能连
    # A 区：1N4148 正向压降（第 3～10 列）
    bb_wire(ax, "T1-3", "a3", "pos")
    bb_res(ax, "b3", "b7", "1k")
    bb_part2(ax, "c7", "c10", "1N4148", kind="diode", dy=0.55)
    bb_wire(ax, "a10", "T2-10", "gnd")
    bb_probe(ax, "d7", "①", dx=-0.9, dy=0.0)
    # B 区：2N3904 开关（第 13～25 列）
    bb_wire(ax, "a13", "T1-13", "sig")
    bb_res(ax, "b13", "b17", "RB 10k")
    bb_block(ax, ["d16", "d17", "d18"], "", pins=["E", "B", "C"], fc="#cfd8dc")
    _bb_label(ax, 14.1, 6.0, "2N3904\n平面朝你")
    bb_wire(ax, "a16", "T2-16", "gnd", via=[(15.6, 9.0), (15.6, 10.8)])
    bb_res(ax, "c18", "c22", "RC 220")
    bb_part2(ax, "b25", "b22", "LED", kind="led", fc="#ff6666", dy=0.55)
    bb_wire(ax, "T1-25", "a25", "pos")
    bb_probe(ax, "e17", "②", dx=-0.6, dy=-0.9)
    bb_probe(ax, "e18", "③", dx=0.6, dy=-0.9)
    # 电位器（第 27～29 列）
    bb_wire(ax, "T1-27", "a27", "pos")
    bb_block(ax, ["c27", "c28", "c29"], "", pins=["+", "滑", "−"], fc="#d7ccc8")
    _bb_label(ax, 28, 8.0, "电位器 10k")
    bb_wire(ax, "a29", "T2-29", "gnd")
    bb_probe(ax, "e28", "④", dx=0.0, dy=-0.9)
    # C 区：1N4733A 稳压（下半块第 20～29 列，9 V 电池供电）
    bb_wire(ax, "B1-20", "j20", "pos")
    bb_res(ax, "i20", "i24", "R 560")
    bb_part2(ax, "h27", "h24", "1N4733A", kind="diode", dy=0.55)
    bb_wire(ax, "j27", "B2-27", "gnd")
    bb_res(ax, "f24", "f29", "RL（后插）", dy=0.55)
    bb_wire(ax, "j29", "B2-29", "gnd")
    bb_probe(ax, "g24", "⑤", dx=-1.0, dy=0.0)
    for x, text in ((6.5, "A 区：二极管"), (12.5, "B 区：三极管开关"), (23.5, "C 区：稳压管（9 V）")):
        ax.text(x, 4.3, text, ha="center", va="center", fontsize=8, color="0.3")
    bb_legend(ax, [("pos", "红线：接电源正极"), ("gnd", "黑线：接地"), ("sig", "蓝线：控制信号")])
    print("[图 P2-p4-1] A：1k b3–b7，1N4148 阳极 c7、阴极 c10，测点① 第 7 列；"
          "B：控制线 a13→+5 V，RB b13–b17，2N3904 E d16 / B d17 / C d18，RC c18–c22，LED 阳极 b25、阴极 b22，"
          "测点② 第 17 列、③ 第 18 列；电位器 c27/c28/c29，测点④ 第 28 列；"
          "C：+9 V→j20，560 Ω i20–i24，1N4733A 阴极 h24、阳极 h27，RL f24–f29，测点⑤ 第 24 列")
    fs.save(fig, P, "P2_p4_1_breadboard.png")


# ---------------- 图 P2-p4-2：没有示波器也没有曲线仪时，逐点测二极管伏安特性 ----------------
def p4_2_iv(vd, idd):
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    v = np.linspace(0.40, 0.75, 300)
    ax.plot(v, diode_i(v) * 1e3, **fs.LS["good"], label="原理与实现篇的指数公式（示意参数）")
    ax.plot(vd, idd, "o", color=fs.C["third"], ms=5, label="逐点读数（1N4148 厂家模型算出）")
    for k, (tx, ty, ha) in ((1, (0.47, 1.0, "left")), (-1, (0.705, 3.6, "left"))):
        ax.plot(vd[k], idd[k], "o", color="k", ms=3.5, zorder=5)
        ax.annotate(f"{vd[k]:.2f} V，{idd[k]:.2f} mA", (vd[k], idd[k]), (tx, ty), ha=ha, va="center", fontsize=9,
                    arrowprops=dict(arrowstyle="-", color="0.3", lw=0.7))
        print(f"[数值] 图 P2-p4-2 标注：{vd[k]:.2f} V，{idd[k]:.2f} mA")
    fs.ref_v(ax, 0.7, "0.7 V")
    ax.set_xlim(0.40, 0.80); ax.set_ylim(0, 5.5)
    fs.axlabels(ax, "二极管两端电压（万用表①）", "V", "电流 = 1 kΩ 两端电压 ÷ 1 kΩ", "mA")
    ax.legend(loc="upper left")
    assert idd[-1] > 4 and idd[1] < 0.5
    fs.save(fig, P, "P2_p4_2_iv_points.png")


if __name__ == "__main__":
    _vd, _id = p4_numbers()
    p4_1_breadboard(); p4_2_iv(_vd, _id)
