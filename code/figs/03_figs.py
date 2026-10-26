"""03 半导体入门：全部配图（电路图 + 特性曲线）。
运行：/workspace/circuits-venv/bin/python code/figs/03_figs.py
图上的每个数字都由 fs.mark 或 print 打印；关键结论用 assert 检查。
器件模型是教学用的简化模型，参数取自数据手册的典型值（出处见 notes/03-research.md）。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
import figstyle as fs
import schem
import schemdraw.elements as elm

P = "03"
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


# ---------------- 引脚标注（第 9 轮）：每个三极管 / MOS 管符号都写「字母 + 中文名」 ----------------
PIN_NAME = {"base": "B 基极", "collector": "C 集电极", "emitter": "E 发射极",
            "gate": "G 栅极", "drain": "D 漏极", "source": "S 源极"}
PIN_C = "#333333"


def pinlab(d, el, at=None, fs_=9, color=PIN_C, skip=()):
    """给三极管 / MOS 管的每只脚写上「B 基极」「C 集电极」「E 发射极」或「G 栅极」「D 漏极」「S 源极」。
    默认位置：上下两只脚写在引线右侧、靠近管身；控制脚（基极 / 栅极）写在引线上方。
    at = {脚名: (dx, dy, 对齐)} 可以逐只改位置（相对该脚的端点）。"""
    a = el.absanchors
    cx, cy = a["center"]
    at = at or {}
    for pin, name in PIN_NAME.items():
        if pin not in a or pin in skip:
            continue
        x, y = a[pin]
        if pin in at:
            dx, dy, ha = at[pin]
        elif pin == "base":                          # 基极：写在引线左下方，避开发射极箭头
            dx, dy, ha = (0.35, -0.45, "right") if x < cx else (-0.35, -0.45, "left")
        elif pin == "gate":                          # 栅极：写在引线上方，避开栅极那块板
            dx, dy, ha = (0.1, 0.32, "right") if x < cx else (-0.1, 0.32, "left")
        else:                                        # 上下两只脚：写在右侧，往管身方向挪一点
            dx, dy, ha = 0.2, (0.3 if y < cy else -0.3), "left"
        d += elm.Label().at((x + dx, y + dy)).label(name, fontsize=fs_, color=color, halign=ha, valign="center")


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
    schem.save_schem(d, P, "03_p1_1_diode_valve.png")


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
    schem.save_schem(d, P, "03_p1_2_zener.png")


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
        pinlab(d, q)
        d += elm.Label().at((2.6, -0.4)).label("三极管：小电流 $I_B$ 控制大电流 $I_C$")
        # 右：N 沟道 MOS 管
        x = 12
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
        pinlab(d, m)
        d += elm.Label().at((11.1, -0.4)).label("MOS 管：电压 $V_{GS}$ 控制电流")
    schem.save_schem(d, P, "03_p1_3_switches.png")


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
    fs.save(fig, P, "03_p2_1_diode_iv.png")
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
    fs.save(fig, P, "03_p2_2_zener_iv.png")
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
    fs.save(fig, P, "03_p2_3_bjt_regions.png")
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
    fs.save(fig, P, "03_p2_4_mos_transfer.png")
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
    fs.save(fig, P, "03_p3_1_rb_sweep.png")
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
    fs.save(fig, P, "03_p3_2_rdson.png")
    return res


if __name__ == "__main__":
    fs.check_cjk("二极管正接反接灯亮不亮稳压管输出约三极管小电流控制大电流沟道示意模型硅红色击穿区变化很大几乎未没有集电极发射负载线截止放大饱和栅源漏阈值基数据手册最小偏导通电阻热")
    p1_1(); p1_2(); p1_3()
    p2_1(); p2_2(); p2_3(); p2_4()
    p3_1(); p3_2()
    print("03_figs OK")


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
    """跳线：kind 取 pos/gnd/neg/sig/out（红/黑/紫/蓝/橙）。via=[(x, y), ...] 时按这些拐点折线走，避免压住元件。"""
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
    三极管开关的读数照搬 review/spice/03.md 的面包板核对表。"""
    # ① 1N4148 + 1 kΩ：先算 5 V 时的工作点，再算电位器调到几个电压时的点
    body = "\n".join(f"V{k} in{k} 0 {v}\nR{k} in{k} d{k} 1k\nXD{k} d{k} 0 1N4148" for k, v in enumerate(P4_VIN))
    r = bb_ng_op(body, [f"v(d{k})" for k in range(len(P4_VIN))], ["1N4148_nexperia.lib"])
    vd = np.array([r[f"v(d{k})"] for k in range(len(P4_VIN))])
    idd = (np.array(P4_VIN) - vd) / 1e3 * 1e3                # mA
    for v, a, b in zip(P4_VIN, vd, idd):
        print(f"[03 page4] 1N4148 + 1 kΩ，输入 {v:.1f} V：二极管 {a:.3f} V，电阻 {v - a:.2f} V，电流 {b:.2f} mA")
    assert 0.66 <= vd[-1] <= 0.71, "5 V 时应落在 review 表的 0.66–0.71 V 里"
    assert vd[1] < vd[-1] < vd[1] + 0.12, "电流从 0.3 mA 涨到 4.3 mA，压降只多了约 0.1 V"
    # ② 1N4733A：9 V 电池 + 560 Ω，空载 / 接 1 kΩ / 接 470 Ω
    z = bb_ng_op("V1 a 0 9\nR1 a z1 560\nXZ1 0 z1 DI_1N4733A\n"
                 "R2 a z2 560\nXZ2 0 z2 DI_1N4733A\nRL2 z2 0 1k\n"
                 "R3 a z3 560\nXZ3 0 z3 DI_1N4733A\nRL3 z3 0 470",
                 ["v(z1)", "v(z2)", "v(z3)"], ["1N47xxA_diodes_zener.lib"])
    vz0, vz1k, vz470 = z["v(z1)"], z["v(z2)"], z["v(z3)"]
    iz0 = (9 - vz0) / 560
    print(f"[03 page4] 9 V / 560 Ω / 1N4733A：空载 {vz0:.2f} V（V_Z ±5% → {vz0 * 0.95:.2f}～{vz0 * 1.05:.2f} V），"
          f"稳压管电流 {iz0 * 1e3:.1f} mA，电阻上 {9 - vz0:.2f} V")
    print(f"[03 page4] 接 1 kΩ 负载：{vz1k:.2f} V（{vz1k * 0.95:.2f}～{vz1k * 1.05:.2f} V），负载电流 {vz1k / 1e3 * 1e3:.1f} mA，"
          f"稳压管剩 {((9 - vz1k) / 560 - vz1k / 1e3) * 1e3:.1f} mA")
    lo = 9 * 470 * 0.95 / (470 * 0.95 + 560 * 1.05); hi = 9 * 470 * 1.05 / (470 * 1.05 + 560 * 0.95)
    print(f"[03 page4] 接 470 Ω 负载：{vz470:.2f} V，稳压管几乎不导电，等于普通分压 9×470/(560+470) = "
          f"{9 * 470 / 1030:.2f} V（电阻公差 → {lo:.2f}～{hi:.2f} V）")
    assert abs(vz0 - 4.99) < 0.02 and abs(iz0 * 1e3 - 7.2) < 0.1, "和 review 表 12 V/1 kΩ（约 7 mA，约 5.0 V）同一个工作点"
    assert vz0 - vz1k < 0.1, "接 1 kΩ 负载，输出只掉几十毫伏"
    assert abs(vz470 - 9 * 470 / 1030) < 0.02, "接 470 Ω 后稳压管退出，变成普通分压"
    assert (round(lo, 2), round(hi, 2)) == (3.88, 4.33)
    # ③ 三极管放大区：Vin 1.64 V、RB 47 kΩ、RC 1 kΩ，页面公式 V_C = 5 − β·I_B·R_C（饱和时约 0.2 V）
    ib = (1.64 - 0.7) / 47e3
    for beta in (100, 130, 230):
        vc = max(5 - beta * ib * 1e3, 0.2)
        print(f"[03 page4] β = {beta}：I_B = {ib * 1e6:.0f} μA，集电极 {vc:.2f} V")
    assert abs(ib * 1e6 - 20) < 0.1 and abs(5 - 100 * ib * 1e3 - 3.0) < 0.01 and 5 - 230 * ib * 1e3 < 0.5
    print(f"[03 page4] 饱和时 LED 电流约 (5 − 2 − 0.1)/220 = {(5 - 2 - 0.1) / 220 * 1e3:.0f} mA，"
          f"基极电流约 (5 − 0.75)/10k = {(5 - 0.75) / 10e3 * 1e3:.2f} mA")
    return vd, idd


# ---------------- 图 03-p4-1：面包板接线图 ----------------
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
    for x, text in ((6.5, "A 区：二极管"), (12.5, "B 区：三极管开关")):
        ax.text(x, 4.3, text, ha="center", va="center", fontsize=8, color="0.3")
    # C 区在下半块：标签放在下半块 g 行第 18～22 列的空位上（同字号同颜色，底色同板子，盖住空孔，不压槽、不压元件）
    ax.text(20.2, 2.0, "C 区：稳压管（9 V）", ha="center", va="center", fontsize=8, color="0.3", zorder=2,
            bbox=dict(boxstyle="square,pad=0.15", fc="#f4f1ea", ec="none"))
    bb_legend(ax, [("pos", "红线：接电源正极"), ("gnd", "黑线：接地"), ("sig", "蓝线：控制信号")])
    print("[图 03-p4-1] A：1k b3–b7，1N4148 阳极 c7、阴极 c10，测点① 第 7 列；"
          "B：控制线 a13→+5 V，RB b13–b17，2N3904 E d16 / B d17 / C d18，RC c18–c22，LED 阳极 b25、阴极 b22，"
          "测点② 第 17 列、③ 第 18 列；电位器 c27/c28/c29，测点④ 第 28 列；"
          "C：+9 V→j20，560 Ω i20–i24，1N4733A 阴极 h24、阳极 h27，RL f24–f29，测点⑤ 第 24 列")
    fs.save(fig, P, "03_p4_1_breadboard.png")


# ---------------- 图 03-p4-2：没有示波器也没有曲线仪时，逐点测二极管伏安特性 ----------------
def p4_2_iv(vd, idd):
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    v = np.linspace(0.40, 0.75, 300)
    ax.plot(v, diode_i(v) * 1e3, **fs.LS["good"], label="原理与实现篇的指数公式（示意参数）")
    ax.plot(vd, idd, "o", color=fs.C["third"], ms=5, label="逐点读数（1N4148 厂家模型算出）")
    for k, (tx, ty, ha) in ((1, (0.47, 1.0, "left")), (-1, (0.705, 3.6, "left"))):
        ax.plot(vd[k], idd[k], "o", color="k", ms=3.5, zorder=5)
        ax.annotate(f"{vd[k]:.2f} V，{idd[k]:.2f} mA", (vd[k], idd[k]), (tx, ty), ha=ha, va="center", fontsize=9,
                    arrowprops=dict(arrowstyle="-", color="0.3", lw=0.7))
        print(f"[数值] 图 03-p4-2 标注：{vd[k]:.2f} V，{idd[k]:.2f} mA")
    fs.ref_v(ax, 0.7, "0.7 V")
    ax.set_xlim(0.40, 0.80); ax.set_ylim(0, 5.5)
    fs.axlabels(ax, "二极管两端电压（万用表①）", "V", "电流 = 1 kΩ 两端电压 ÷ 1 kΩ", "mA")
    ax.legend(loc="upper left")
    assert idd[-1] > 4 and idd[1] < 0.5
    fs.save(fig, P, "03_p4_2_iv_points.png")


if __name__ == "__main__":
    _vd, _id = p4_numbers()
    p4_1_breadboard(); p4_2_iv(_vd, _id)


# ======================================================================================
# 第 8 轮补电路图（page1–page3）：正文/例题/练习里描述了具体接法、但附近没有电路图的地方
# ======================================================================================
EMPH = schem.C["third"]      # 新出现、需要强调的元件
BAD = schem.C["bad"]         # 错误接法的标注


def _vsrc(d, x, y0, y1, text):
    """竖放电池：负极在 y0（下）、正极在 y1（上），左侧标注。"""
    ym = (y0 + y1) / 2
    d += elm.Line().endpoints((x, y0), (x, ym - 0.9))
    d += elm.Battery().endpoints((x, ym - 0.9), (x, ym + 0.9))
    d += elm.Line().endpoints((x, ym + 0.9), (x, y1))
    d += elm.Label().at((x - 0.9, ym)).label(text)


def _diode_loop(d, x0, vtxt, rtxt, parts, itxt):
    """电池 → 电阻 → 若干只二极管（竖着向下）→ 回到电池负极。parts: [(元件类, 标注, 颜色)]。"""
    top, bot = 4.0, -2.0 - 1.6 * (len(parts) - 1)
    xr = x0 + 2.6
    _vsrc(d, x0, bot, top, vtxt)
    d += elm.Line().endpoints((x0, top), (xr - 0.2, top))
    d += elm.Resistor().endpoints((xr - 0.2, top), (xr + 2.4, top)).label(rtxt)
    xd = xr + 2.4
    y = top
    for k, (E, txt, col) in enumerate(parts):
        y_next = y - (3.0 if k == 0 else 1.6)
        d += E().endpoints((xd, y if k else y), (xd, y_next)).color(col)
        d += elm.Label().at((xd + 0.75, (y + y_next) / 2)).label(txt, halign="left", color=col)
        y = y_next
    d += elm.Line().endpoints((xd, y), (xd, bot))
    d += elm.Line().endpoints((xd, bot), (x0, bot))
    d += elm.Label().at((x0 + 1.3, top + 0.45)).label(itxt, color=schem.C["cur"])


def p2_6_diode_circuits():
    print("[图 03-p2-6] (a) 5 V 串 1 kΩ 串硅二极管，I≈4.3 mA；(b) 例 1：5 V 串 330 Ω 串红色 LED")
    i_a = (5 - 0.7) / 1000 * 1e3
    i_b = (5 - 2) / 330 * 1e3
    print(f"[数值] 估算电流 (a) {i_a:.1f} mA，(b) {i_b:.1f} mA")
    assert abs(i_a - 4.3) < 0.05 and abs(i_b - 9.1) < 0.05
    with schem.drawing(fontsize=11) as d:
        _diode_loop(d, 0.0, "$V_{CC}$\n5 V", "$R$  1 kΩ", [(elm.Diode, "硅二极管\n$V_D$ ≈ 0.7 V", "black")], "→ $I$ ≈ 4.3 mA")
        d += elm.Label().at((2.6, -3.2)).label("(a) 第 1 节：电源串电阻串二极管")
        _diode_loop(d, 9.0, "$V_{CC}$\n5 V", "$R$  330 Ω", [(elm.LED, "红色 LED\n$V_D$ ≈ 2 V", EMPH)], "→ $I$ ≈ 9.1 mA")
        d += elm.Label().at((11.6, -3.2)).label("(b) 例 1：LED 串限流电阻")
    schem.save_schem(d, P, "03_p2_6_diode_circuits.png")


def _npn_switch(d, x0, vin_txt, rb_txt, vcc_txt, rc_txt, rb_color="black", rc_color="black", rc_load=False):
    """低边 NPN 开关：输入 → R_B → 基极；V_CC → R_C（或负载）→ 集电极；发射极接地。返回三极管。"""
    xq = x0 + 4.0
    q = elm.BjtNpn().anchor("base").at((xq, 0.0))
    d += q
    xc = q.collector[0]
    d += elm.Line().endpoints(q.collector, (xc, 1.2))
    d += elm.Resistor().endpoints((xc, 4.0), (xc, 1.2)).color(rc_color)
    d += elm.Label().at((xc + 0.4, 2.6)).label(rc_txt, halign="left", color=rc_color)
    d += elm.Dot(open=True).at((xc, 4.0)).label(vcc_txt, "top")
    d += elm.Resistor().endpoints((x0 + 0.6, 0.0), (xq, 0.0)).color(rb_color).label(rb_txt, color=rb_color)
    d += elm.Dot(open=True).at((x0 + 0.6, 0.0)).label(vin_txt, "left")
    d += elm.Line().endpoints(q.emitter, (xc, -1.4))
    d += elm.Ground().at((xc, -1.4))
    pinlab(d, q, at={"collector": (0.25, -0.25, "left"), "emitter": (0.25, 0.25, "left")})
    return q


def p2_7_bjt_switch():
    print("[图 03-p2-7] NPN 开关：V_i 经 R_B 进基极，5 V 经 R_C=1 kΩ 进集电极，发射极接地")
    with schem.drawing(fontsize=11) as d:
        q = _npn_switch(d, 0.0, "$V_i$", "$R_B$  47 kΩ（第 3 节）\n10 kΩ（第 5 节）", "$V_{CC}$ = 5 V", "$R_C$\n1 kΩ")
        xc = q.collector[0]
        d += elm.Label().at((xc - 0.55, 1.75)).label("↓ $I_C$", color=schem.C["cur"], halign="right")
        d += elm.Label().at((1.7, -0.75)).label("→ $I_B$", color=schem.C["cur"])
        d += elm.Label().at((xc + 2.6, 0.0)).label("$V_{CE}$\n（C 对地）", color=EMPH)
        d += elm.Label().at((3.0, -2.6)).label("$V_{BE}$ ≈ 0.7 V，$V_{CE} = V_{CC} - I_C R_C$")
    schem.save_schem(d, P, "03_p2_7_bjt_switch.png")


def p2_8_pmos_highside():
    print("[图 03-p2-8] P 沟道高边开关：源极接 12 V，漏极经负载接地，栅极上拉到 12 V，开关 K 把栅极拉到地")
    with schem.drawing(fontsize=11) as d:
        xs = 6.0
        m = elm.PFet().reverse().anchor("source").at((xs, 4.0))
        d += m
        g = m.gate
        d += elm.Line().endpoints((1.5, 5.0), (xs, 5.0))
        d += elm.Line().endpoints((xs, 5.0), m.source)
        d += elm.Dot(open=True).at((1.5, 5.0)).label("+12 V", "left")
        d += elm.Dot().at((g[0] - 1.6, 5.0))
        d += elm.Resistor().endpoints((g[0] - 1.6, 5.0), (g[0] - 1.6, g[1])).color(EMPH)
        d += elm.Label().at((g[0] - 2.0, (5.0 + g[1]) / 2)).label("上拉电阻", color=EMPH, halign="right")
        d += elm.Line().endpoints((g[0] - 1.6, g[1]), g)
        d += elm.Dot().at((g[0] - 1.6, g[1]))
        d += elm.Switch().endpoints((g[0] - 1.6, g[1]), (g[0] - 1.6, g[1] - 2.4))
        d += elm.Label().at((g[0] - 2.0, g[1] - 1.2)).label("开关 K", halign="right")
        d += elm.Ground().at((g[0] - 1.6, g[1] - 2.4))
        d += elm.Resistor().endpoints(m.drain, (xs, m.drain[1] - 2.4)).label("负载", "bottom")
        d += elm.Ground().at((xs, m.drain[1] - 2.4))
        pinlab(d, m)
        d += elm.Label().at((4.0, -1.4)).label("K 断开：栅极被拉到 12 V，$V_{GS}$ = 0 V → 关断\nK 闭合：栅极 = 0 V，$V_{GS}$ = −12 V → 导通")
    schem.save_schem(d, P, "03_p2_8_pmos_highside.png")


def p3_3_rb_sweep_circuit():
    print("[图 03-p3-3] 扫描一的电路：3.3 V 驱动经 R_B（0.5–15 kΩ）进基极，5 V 经 100 Ω 负载进集电极")
    with schem.drawing(fontsize=11) as d:
        q = _npn_switch(d, 0.0, "单片机\n3.3 V", "$R_B$  0.5–15 kΩ 扫描", "5 V", "负载\n100 Ω", rb_color=EMPH)
        d += elm.Label().at((q.collector[0] + 2.3, 0.0)).label("测 $V_{CE}$", color=schem.C["cur"])
    schem.save_schem(d, P, "03_p3_3_rb_sweep_circuit.png")


def p3_4_two_diodes():
    print("[图 03-p3-4] 练习 1：12 V 串 1 kΩ 串两只同方向硅二极管")
    with schem.drawing(fontsize=11) as d:
        _diode_loop(d, 0.0, "12 V", "1 kΩ", [(elm.Diode, "$D_1$", "black"), (elm.Diode, "$D_2$", "black")], "→ $I$ = ?")
    schem.save_schem(d, P, "03_p3_4_two_diodes.png")


def p3_5_nmos_floating():
    print("[图 03-p3-5] 练习 4：3.3 V 引脚直接接 2N7000 栅极，5 V 经 100 Ω 进漏极，栅极到地什么都没接")
    with schem.drawing(fontsize=11) as d:
        xd = 5.0
        m = elm.NFet().reverse().anchor("drain").at((xd, 1.5))
        d += m
        g = m.gate
        d += elm.Resistor().endpoints((xd, 4.4), m.drain)
        d += elm.Label().at((xd + 0.4, 3.0)).label("负载\n100 Ω", halign="left")
        d += elm.Dot(open=True).at((xd, 4.4)).label("5 V", "top")
        d += elm.Line().endpoints((0.5, g[1]), g)
        d += elm.Dot(open=True).at((0.5, g[1])).label("单片机引脚\n0 / 3.3 V", "left")
        d += elm.Label().at((xd + 1.6, m.drain[1] - 0.75)).label("2N7000", halign="left", fontsize=10)
        pinlab(d, m)
        d += elm.Line().endpoints(m.source, (xd, m.source[1] - 0.6))
        d += elm.Ground().at((xd, m.source[1] - 0.6))
        d += elm.Label().at((2.0, g[1] - 1.3)).label("栅极和地之间\n什么都没接", color=BAD)
    schem.save_schem(d, P, "03_p3_5_nmos_floating.png")


def p3_6_pmos_direct():
    print("[图 03-p3-6] 练习 5：P 沟道管源极接 12 V，栅极直接接 5 V 单片机引脚，漏极经负载接地")
    with schem.drawing(fontsize=11) as d:
        xs = 5.0
        m = elm.PFet().reverse().anchor("source").at((xs, 3.5))
        d += m
        g = m.gate
        d += elm.Line().endpoints(m.source, (xs, 4.4))
        d += elm.Dot(open=True).at((xs, 4.4)).label("+12 V", "top")
        d += elm.Line().endpoints((0.5, g[1]), g)
        d += elm.Dot(open=True).at((0.5, g[1])).label("单片机引脚\n0 / 5 V", "left")
        d += elm.Resistor().endpoints(m.drain, (xs, m.drain[1] - 2.4))
        d += elm.Label().at((xs + 0.4, m.drain[1] - 1.2)).label("负载", halign="left")
        d += elm.Ground().at((xs, m.drain[1] - 2.4))
        pinlab(d, m)
    schem.save_schem(d, P, "03_p3_6_pmos_direct.png")


def p3_7_pmos_fixed():
    print("[图 03-p3-7] 练习 5 答案：栅极上拉到 12 V，NPN 把栅极拉到地，单片机经 R_B 控制 NPN")
    with schem.drawing(fontsize=11) as d:
        xs = 8.0
        m = elm.PFet().reverse().anchor("source").at((xs, 4.0))
        d += m
        g = m.gate
        d += elm.Line().endpoints((g[0] - 1.6, 5.0), (xs, 5.0))
        d += elm.Line().endpoints((xs, 5.0), m.source)
        d += elm.Dot(open=True).at((xs, 5.0)).label("+12 V", "top")
        xg = g[0] - 1.6
        d += elm.Resistor().endpoints((xg, 5.0), (xg, g[1])).color(EMPH)
        d += elm.Label().at((xg - 0.4, (5.0 + g[1]) / 2)).label("上拉电阻", color=EMPH, halign="right")
        d += elm.Line().endpoints((xg, g[1]), g)
        d += elm.Dot().at((xg, g[1]))
        q = elm.BjtNpn().anchor("collector").at((xg, g[1] - 1.0)).color(EMPH)
        d += q
        d += elm.Line().endpoints((xg, g[1]), q.collector).color(EMPH)
        d += elm.Ground().at(q.emitter)
        d += elm.Resistor().endpoints((q.base[0] - 3.0, q.base[1]), q.base).color(EMPH).label("$R_B$", color=EMPH)
        d += elm.Dot(open=True).at((q.base[0] - 3.0, q.base[1])).label("单片机引脚\n0 / 5 V", "left")
        d += elm.Resistor().endpoints(m.drain, (xs, m.drain[1] - 2.4))
        d += elm.Label().at((xs + 0.4, m.drain[1] - 1.2)).label("负载", halign="left")
        d += elm.Ground().at((xs, m.drain[1] - 2.4))
        pinlab(d, m)
        pinlab(d, q, color=EMPH, at={"collector": (0.2, -0.25, "left")})
        d += elm.Label().at((4.5, -1.6)).label("引脚高 → NPN 导通 → 栅极 ≈ 0 V → P 沟道管导通\n引脚低 → NPN 截止 → 栅极被拉回 12 V → 关断")
    schem.save_schem(d, P, "03_p3_7_pmos_fixed.png")


if __name__ == "__main__":
    p2_6_diode_circuits(); p2_7_bjt_switch(); p2_8_pmos_highside()
    p3_3_rb_sweep_circuit(); p3_4_two_diodes(); p3_5_nmos_floating(); p3_6_pmos_direct(); p3_7_pmos_fixed()


# ======================================================================================
# 第 9 轮：三极管怎样放大（page1/page2/page4）、四种管子的符号与引脚、常用功能对照（page1）
# ======================================================================================
AMP = dict(vcc=5.0, rc=1e3, rb=10e3, beta=100.0, vbe=0.7, vsat=0.2, vq=0.95, dv=0.1)   # 共射放大例子（理想模型）


def ce_amp(vin, vcc=5.0, rc=1e3, rb=10e3, beta=100.0, vbe=0.7, vsat=0.2):
    """共射放大（理想模型）：I_B = (V_i − 0.7)/R_B（不小于 0），I_C = β·I_B（不超过饱和电流），V_C = V_CC − I_C·R_C。"""
    vin = np.asarray(vin, dtype=float)
    ib = np.clip((vin - vbe) / rb, 0, None)
    ic = np.minimum(beta * ib, (vcc - vsat) / rc)
    return ib, ic, vcc - ic * rc


def amp_numbers():
    """page1/page2 例子里的每个数：打印并断言。"""
    a = AMP
    vin = np.array([a["vq"] - a["dv"], a["vq"], a["vq"] + a["dv"]])
    ib, ic, vc = ce_amp(vin, a["vcc"], a["rc"], a["rb"], a["beta"])
    for v, x, y, z in zip(vin, ib, ic, vc):
        print(f"[03 放大] V_i = {v:.2f} V：I_B = {x * 1e6:.0f} μA，I_C = {y * 1e3:.1f} mA，V_C = {z:.1f} V")
    gain = (vc[2] - vc[0]) / (vin[2] - vin[0])
    print(f"[03 放大] 输入变化 {vin[2] - vin[0]:.1f} V → 输出变化 {vc[2] - vc[0]:+.1f} V，电压放大倍数 {gain:+.0f}（负号 = 反相）")
    assert np.allclose(ib * 1e6, [15, 25, 35]) and np.allclose(ic * 1e3, [1.5, 2.5, 3.5]) and np.allclose(vc, [3.5, 2.5, 1.5])
    assert abs(gain + 10) < 1e-9 and abs(a["beta"] * a["rc"] / a["rb"] - 10) < 1e-9, "放大倍数 = β·R_C/R_B = 10"
    for vq in (0.75, 1.15):
        lo, hi = ce_amp(np.array([vq - a["dv"], vq + a["dv"]]))[2]
        print(f"[03 放大] 偏置 {vq:.2f} V：V_C 在 {hi:.2f}～{lo:.2f} V 之间")
    return gain


def p1_4_amp_idea():
    """四条曲线从上到下：V_i → I_B → I_C → V_C，横轴对齐，竖虚线标出「输入最高时输出最低」。"""
    a = AMP
    t = np.linspace(0, 2, 801)                                     # ms，信号 1 kHz，画两个周期
    vin = a["vq"] + a["dv"] * np.sin(2 * np.pi * t)
    ib, ic, vc = ce_amp(vin)
    fig, axs = plt.subplots(4, 1, figsize=(7, 6.4), sharex=True)
    rows = [(vin, 1, "vin", "输入 $V_i$ / V", a["vq"], "中心 0.95 V，变化 ±0.1 V"),
            (ib * 1e6, 1, "cur", "基极电流 $I_B$ / μA", 25, "中心 25 μA，变化 ±10 μA"),
            (ic * 1e3, 1, "cur", "集电极电流 $I_C$ / mA", 2.5, "中心 2.5 mA，变化 ±1 mA（β = 100 倍）"),
            (vc, 1, "vout", "集电极 $V_C$ / V", 2.5, "中心 2.5 V，变化 ±1 V，方向相反")]
    for ax, (y, _, key, lab, mid, txt) in zip(axs, rows):
        ax.plot(t, y, **fs.LS[key])
        fs.ref_h(ax, mid)
        ax.set_ylabel(lab, fontsize=8.5)
        span = (y.max() - y.min())
        ax.set_ylim(y.min() - 0.45 * span, y.max() + 0.75 * span)
        ax.text(1.02, y.max() + 0.4 * span, txt, ha="center", va="center", fontsize=8.5,
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
        k = np.argmax(vin)
        fs.mark(ax, t[k], y[k], fmt="{:.2f}" if key in ("vin",) else "{:.1f}", dx=5, dy=(4 if key == "vout" else -11))
    for ax in axs:
        ax.axvline(0.25, **fs.LS["ref"])
    axs[0].text(0.27, a["vq"] - 0.14, "输入最高的时刻", fontsize=8, color="0.3", va="center")
    axs[3].text(0.27, 0.95, "输出正好最低", fontsize=8, color="0.3", va="center")
    fs.axlabels(axs[3], "时间", "ms")
    assert abs(vin.max() - 1.05) < 1e-3 and abs(vc.min() - 1.5) < 1e-3 and abs(vc.max() - 3.5) < 1e-3
    assert np.argmax(vin) == np.argmin(vc), "反相：输入最高时输出最低"
    fs.save(fig, P, "03_p1_4_amp_idea.png")


# ---------------- 图 03-p1-5：四种管子的符号、引脚名和电流方向（手工画，箭头完全可控） ----------------
def _arr(ax, p, q, color="black", lw=1.4, hw=0.16, hl=0.22):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle=f"-|>,head_width={hw},head_length={hl}",
                                                     color=color, lw=lw, shrinkA=0, shrinkB=0))


def _cur(ax, p, q, text, side="right"):
    """天蓝色电流箭头 + 名字。"""
    _arr(ax, p, q, color=fs.C["cur"], lw=1.6, hw=0.22, hl=0.3)
    xm, ym = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    if side == "right":
        ax.text(xm + 0.15, ym, text, ha="left", va="center", fontsize=9.5, color=fs.C["cur"])
    elif side == "left":
        ax.text(xm - 0.15, ym, text, ha="right", va="center", fontsize=9.5, color=fs.C["cur"])
    else:
        ax.text(xm, ym - 0.22, text, ha="center", va="top", fontsize=9.5, color=fs.C["cur"])


def _pin(ax, x, y, text, ha="center", va="center"):
    ax.text(x, y, text, ha=ha, va=va, fontsize=9.5, color="#222222", fontweight="bold")


def _sym_bjt(ax, x, y, pnp=False):
    """BJT：基极竖杠在 x−0.3；NPN 集电极在上、发射极在下；PNP 发射极在上、集电极在下。返回各脚端点。"""
    k = dict(color="black", lw=1.6, solid_capstyle="round")
    ax.plot([x - 0.3, x - 0.3], [y - 0.55, y + 0.55], color="black", lw=3.2)       # 基极竖杠
    ax.plot([x - 1.4, x - 0.3], [y, y], **k)                                      # 基极引线
    ax.plot([x - 0.3, x + 0.45, x + 0.45], [y + 0.22, y + 0.65, y + 1.45], **k)    # 上面一只脚
    ax.plot([x - 0.3, x + 0.45, x + 0.45], [y - 0.22, y - 0.65, y - 1.45], **k)    # 下面一只脚
    ax.add_patch(plt.Circle((x + 0.05, y), 0.95, fill=False, lw=1.0, color="0.35"))
    if not pnp:      # NPN：发射极（下）箭头朝外，指向离开基极的方向
        _arr(ax, (x - 0.05, y - 0.365), (x + 0.38, y - 0.61))
        return dict(B=(x - 1.4, y), C=(x + 0.45, y + 1.45), E=(x + 0.45, y - 1.45))
    _arr(ax, (x + 0.38, y + 0.61), (x - 0.05, y + 0.365))                           # PNP：发射极（上）箭头朝里
    return dict(B=(x - 1.4, y), E=(x + 0.45, y + 1.45), C=(x + 0.45, y - 1.45))


def _sym_mos(ax, x, y, pch=False, full=False):
    """MOS：栅极板在 x−0.5、沟道在 x−0.25。N 沟道漏极在上；P 沟道源极在上（和本书电路图里的摆法一样）。
    full=False：本书电路图的简化画法（P 沟道在栅极画小圆圈）；full=True：手册常见的完整画法（三段沟道 + 衬底箭头）。"""
    k = dict(color="black", lw=1.6, solid_capstyle="round")
    xg = x - 0.55
    ax.plot([xg, xg], [y - 0.5, y + 0.5], **k)                                     # 栅极板
    xin = x - 1.4
    if pch and not full:
        ax.add_patch(plt.Circle((xg - 0.13, y), 0.12, fill=False, lw=1.4, color="black"))
        ax.plot([xin, xg - 0.25], [y, y], **k)
    else:
        ax.plot([xin, xg], [y, y], **k)
    xc = x - 0.3
    if full:
        for y0, y1 in ((0.3, 0.62), (-0.16, 0.16), (-0.62, -0.3)):
            ax.plot([xc, xc], [y + y0, y + y1], color="black", lw=2.6)
    else:
        ax.plot([xc, xc], [y - 0.62, y + 0.62], color="black", lw=2.6)
    ax.plot([xc, x + 0.45, x + 0.45], [y + 0.46, y + 0.46, y + 1.45], **k)
    ax.plot([xc, x + 0.45, x + 0.45], [y - 0.46, y - 0.46, y - 1.45], **k)
    top, bot = ("S", "D") if pch else ("D", "S")
    if full:   # 衬底线：从沟道中间连到源极
        ys = y + 0.46 if pch else y - 0.46
        ax.plot([xc, x + 0.45], [y, y], **k)
        ax.plot([x + 0.45, x + 0.45], [y, ys], **k)
        if pch:
            _arr(ax, (xc + 0.05, y), (x + 0.3, y))           # P 沟道：箭头朝外
        else:
            _arr(ax, (x + 0.4, y), (xc + 0.05, y))           # N 沟道：箭头朝里（指向沟道）
    return {"G": (xin, y), top: (x + 0.45, y + 1.45), bot: (x + 0.45, y - 1.45)}


def p1_5_symbols():
    names = {"B": "B 基极", "C": "C 集电极", "E": "E 发射极", "G": "G 栅极", "D": "D 漏极", "S": "S 源极"}
    fig, ax = plt.subplots(figsize=(10, 7.4))
    ax.set_xlim(-0.6, 16.2); ax.set_ylim(-9.3, 3.2); ax.set_aspect("equal"); ax.axis("off")
    xs = [2.0, 6.2, 10.4, 14.4]
    y = 0.0
    sym = [_sym_bjt(ax, xs[0], y), _sym_bjt(ax, xs[1], y, pnp=True),
           _sym_mos(ax, xs[2], y), _sym_mos(ax, xs[3], y, pch=True)]
    for p in sym:
        for k, (px, py) in p.items():
            if k in "BG":
                _pin(ax, px - 0.1, py + 0.32, names[k], ha="center", va="bottom")
            elif py > y:
                _pin(ax, px, py + 0.12, names[k], va="bottom")
            else:
                _pin(ax, px, py - 0.12, names[k], va="top")
    # 电流方向（天蓝色）：NPN 从 B、C 流进，从 E 流出；PNP 从 E 流进，从 B、C 流出
    x = xs[0] + 0.45
    _cur(ax, (xs[0] - 1.25, y - 0.35), (xs[0] - 0.55, y - 0.35), "$I_B$", side="below")
    _cur(ax, (x + 0.3, y + 1.35), (x + 0.3, y + 0.75), "$I_C$")
    _cur(ax, (x + 0.3, y - 0.75), (x + 0.3, y - 1.35), "$I_E$")
    x = xs[1] + 0.45
    _cur(ax, (x + 0.3, y + 1.35), (x + 0.3, y + 0.75), "$I_E$")
    _cur(ax, (xs[1] - 0.55, y - 0.35), (xs[1] - 1.25, y - 0.35), "$I_B$", side="below")
    _cur(ax, (x + 0.3, y - 0.75), (x + 0.3, y - 1.35), "$I_C$")
    for xx in xs[2:]:
        x = xx + 0.45
        _cur(ax, (x + 0.3, y + 1.35), (x + 0.3, y + 0.75), "$I_D$")
        _cur(ax, (x + 0.3, y - 0.75), (x + 0.3, y - 1.35), "$I_D$")
        ax.text(xx - 1.0, y - 0.35, "$I_G \\approx 0$", ha="center", va="top", fontsize=9.5, color=fs.C["cur"])
    caps = ["NPN 三极管\n箭头在发射极上、朝外\n电流从 E 流出\n导通：B 比 E 高约 0.7 V",
            "PNP 三极管\n箭头在发射极上、朝里\n电流从 E 流进\n导通：B 比 E 低约 0.7 V",
            "N 沟道 MOS 管\n本书画法：没有箭头\n电流 D → S\n导通：G 比 S 高过门限",
            "P 沟道 MOS 管\n本书画法：栅极画小圆圈\n电流 S → D\n导通：G 比 S 低过门限"]
    for xx, c in zip(xs, caps):
        ax.text(xx, y - 2.15, c, ha="center", va="top", fontsize=9, linespacing=1.45)
    ax.text(0.0, 2.75, "上排：本书电路图里的画法（天蓝色箭头 = 电流方向）", fontsize=10, color="0.25", ha="left")
    # 下排：手册里常见的 MOS 完整画法
    y2 = -6.6
    ax.plot([-0.4, 16.0], [-4.35, -4.35], color="0.75", lw=0.8, ls=":")
    ax.text(0.0, -4.75, "下排：数据手册里常见的 MOS 管完整画法（沟道画成三段，箭头画在中间那条衬底线上）", fontsize=10,
            color="0.25", ha="left")
    full = [_sym_mos(ax, xs[2], y2, full=True), _sym_mos(ax, xs[3], y2, pch=True, full=True)]
    for p in full:
        for k, (px, py) in p.items():
            if k == "G":
                _pin(ax, px - 0.1, py + 0.32, names[k], ha="center", va="bottom")
            elif py > y2:
                _pin(ax, px, py + 0.12, names[k], va="bottom")
            else:
                _pin(ax, px, py - 0.12, names[k], va="top")
    ax.text(xs[2] + 1.0, y2, "箭头朝里\n（N 沟道）", ha="left", va="center", fontsize=9)
    ax.text(xs[3] + 1.0, y2, "箭头朝外\n（P 沟道）", ha="left", va="center", fontsize=9)
    ax.text(0.0, y2 + 0.9, "三极管的箭头 = 发射极电流的方向\n"
                           "  NPN：朝外（电流流出）\n  PNP：朝里（电流流进）\n\n"
                           "MOS 管的衬底箭头 = 那个内部\n二极管从 P 指向 N 的方向\n"
                           "  N 沟道朝里，P 沟道朝外\n  正好和三极管反过来",
            ha="left", va="top", fontsize=9.2, linespacing=1.45,
            bbox=dict(boxstyle="round,pad=0.4", fc=fs.C["fill"], ec="0.7"))
    print("[图 03-p1-5] 上排 NPN / PNP / N 沟道 / P 沟道（本书画法）带引脚名和电流方向；下排 MOS 完整画法：N 沟道箭头朝里，P 沟道朝外")
    fs.save(fig, P, "03_p1_5_symbols.png")


# ---------------- 图 03-p1-6：TO-92 / SOT-23 引脚排列（平面朝自己、引脚朝下） ----------------
PINOUTS = [("2N3904 / 2N3906\nS8050 / S8550", "EBC", None),
           ("2N7000", "SGD", None),
           ("BC547 / BC557", "CBE", "和 2N3904 正好相反！"),
           ("2SC1815", "ECB", "中间是集电极！")]


def p1_6_pinouts():
    pn = {"E": "发射极", "B": "基极", "C": "集电极", "S": "源极", "G": "栅极", "D": "漏极"}
    fig, ax = plt.subplots(figsize=(10, 4.9))
    ax.set_xlim(-0.3, 20.3); ax.set_ylim(-5.3, 4.6); ax.set_aspect("equal"); ax.axis("off")
    for i, (name, order, warn) in enumerate(PINOUTS):
        x0 = 0.4 + i * 3.9
        # 正面（平面）：矩形，上沿圆一点
        ax.add_patch(plt.Rectangle((x0, 0.0), 2.6, 2.4, fc="#3a3a3a", ec="black", lw=1.0))
        ax.text(x0 + 1.3, 1.45, name, ha="center", va="center", fontsize=7.8, color="white", linespacing=1.3)
        ax.text(x0 + 1.3, 0.35, "平面朝你", ha="center", va="center", fontsize=7, color="#dddddd")
        # 顶视小图：D 字形，平面一侧朝下（朝你）
        th = np.linspace(0, np.pi, 40)
        ax.fill(np.r_[x0 + 1.3 + 0.75 * np.cos(th)], np.r_[3.05 + 0.75 * np.sin(th)], fc="#3a3a3a", ec="black", lw=0.8)
        ax.text(x0 + 1.3, 2.75, "从上往下看", ha="center", va="top", fontsize=6.5, color="0.35")
        ax.text(x0 + 2.25, 3.05, "↓你", ha="left", va="bottom", fontsize=7, color="0.35")
        for k, ch in enumerate(order):
            xp = x0 + 0.45 + k * 0.85
            ax.plot([xp, xp], [0.0, -1.5], color="#9e9e9e", lw=3.2, solid_capstyle="butt")
            col = fs.C["bad"] if warn and ((order == "CBE" and ch in "CE") or (order == "ECB" and ch in "CB")) else "#222222"
            ax.text(xp, -1.65, f"{ch}\n{pn[ch]}", ha="center", va="top", fontsize=8.5, color=col, linespacing=1.2)
        if warn:
            ax.text(x0 + 1.3, -3.05, warn, ha="center", va="top", fontsize=8.5, color=fs.C["bad"])
        print(f"[图 03-p1-6] {name.replace(chr(10), ' ')}：平面朝你、引脚朝下，从左到右 {'-'.join(order)}")
    # SOT-23 贴片：顶视
    x0 = 16.2
    ax.add_patch(plt.Rectangle((x0, 0.2), 2.6, 1.6, fc="#3a3a3a", ec="black", lw=1.0))
    ax.text(x0 + 1.3, 1.0, "SOT-23\n（从上往下看）", ha="center", va="center", fontsize=7, color="white")
    for (xp, y0, y1, num) in ((x0 + 0.55, 0.2, -0.45, "1"), (x0 + 2.05, 0.2, -0.45, "2"), (x0 + 1.3, 1.8, 2.45, "3")):
        ax.add_patch(plt.Rectangle((xp - 0.22, min(y0, y1)), 0.44, abs(y1 - y0), fc="#bdbdbd", ec="0.3", lw=0.6))
        ax.text(xp, (y1 - 0.12) if y1 < y0 else (y1 + 0.12), num, ha="center", va="top" if y1 < y0 else "bottom",
                fontsize=8.5, fontweight="bold")
    ax.text(x0 + 1.3, -1.0, "MOS 管（AO3400A、AO3401A、\nBSS138）：1 G、2 S、3 D\n"
                            "三极管（MMBT3904）：\n1 B、2 E、3 C", ha="center", va="top", fontsize=8, linespacing=1.35)
    ax.text(0.4, -4.4, "同样的封装，不同型号的引脚顺序可以不一样。上面只是常见型号；买到的管子以它自己的数据手册为准，"
                       "\n插板前先查手册（或用万用表的二极管挡、hFE 挡核对一遍）。",
            ha="left", va="center", fontsize=9, color="#333333",
            bbox=dict(boxstyle="round,pad=0.35", fc=fs.C["fill2"], ec="0.7"))
    fs.save(fig, P, "03_p1_6_pinouts.png")


# ---------------- 图 03-p1-7 / 03-p1-8：常用功能小电路（每个都标出后续章节） ----------------
def _bot_label(d, xy, text):
    d += elm.Label().at(xy).label(text, fontsize=10, halign="center", valign="top")


def p1_7_bjt_uses():
    cur = schem.C["cur"]
    with schem.drawing(fontsize=10) as d:
        # (a) 共射放大
        q = elm.BjtNpn().theta(0).anchor("base").at((2.6, 0.0)); d += q
        xc = q.collector[0]
        d += elm.Line().endpoints(q.collector, (xc, 1.2))
        d += elm.Resistor().endpoints((xc, 3.8), (xc, 1.2)).label("$R_C$ 1k", loc="bottom")
        d += elm.Dot(open=True).at((xc, 3.8)).label("+5 V", "top")
        d += elm.Dot().at((xc, 1.2))
        d += elm.Line().endpoints((xc, 1.2), (xc + 1.6, 1.2))
        d += elm.Dot(open=True).at((xc + 1.6, 1.2)).label("$V_C$\n（反相、放大）", "right", color=schem.C["vout"])
        d += elm.Resistor().endpoints((0.0, 0.0), q.base).label("$R_B$ 10k")
        d += elm.Dot(open=True).at((0.0, 0.0)).label("$V_i$\n0.95 V\n±0.1 V", "left", color=schem.C["vin"])
        d += elm.Ground().at(q.emitter)
        pinlab(d, q, fs_=8, at={"collector": (0.2, -0.3, "left"), "emitter": (0.2, 0.3, "left")})
        _bot_label(d, (2.4, -1.9), "(a) 共射放大：小变化 → 大变化\n（本节第 2、4 页）")
        # (b) NPN 低边：继电器线圈 + 续流二极管
        x0 = 9.2
        q = elm.BjtNpn().theta(0).anchor("base").at((x0 + 2.6, 0.0)); d += q
        xc = q.collector[0]
        d += elm.Line().endpoints(q.collector, (xc, 1.0))
        d += elm.Inductor2(loops=3).endpoints((xc, 3.4), (xc, 1.0))
        d += elm.Label().at((xc - 0.5, 2.2)).label("继电器\n线圈", halign="right")
        d += elm.Line().endpoints((xc, 3.4), (xc, 3.8))
        d += elm.Dot(open=True).at((xc, 3.8)).label("+12 V", "top")
        d += elm.Dot().at((xc, 3.4)); d += elm.Dot().at((xc, 1.0))
        d += elm.Line().endpoints((xc, 3.4), (xc + 1.2, 3.4))
        d += elm.Diode().endpoints((xc + 1.2, 1.0), (xc + 1.2, 3.4))
        d += elm.Line().endpoints((xc, 1.0), (xc + 1.2, 1.0))
        d += elm.Label().at((xc + 1.55, 2.2)).label("续流\n二极管", halign="left")
        d += elm.Resistor().endpoints((x0 + 0.2, 0.0), q.base).label("$R_B$ 1k")
        d += elm.Dot(open=True).at((x0 + 0.2, 0.0)).label("单片机\n3.3 V", "left")
        d += elm.Ground().at(q.emitter)
        pinlab(d, q, fs_=8, at={"collector": (0.2, -0.3, "left"), "emitter": (0.2, 0.3, "left")})
        _bot_label(d, (x0 + 2.0, -1.9), "(b) NPN 低边开关：驱动继电器\n（→ 07）")
        # (c) PNP 高边开关
        y0 = -9.0
        q = elm.BjtPnp().theta(0).anchor("base").at((2.6, y0 + 2.4)); d += q
        xe = q.emitter[0]
        d += elm.Line().endpoints(q.emitter, (xe, y0 + 4.4))
        d += elm.Dot(open=True).at((xe, y0 + 4.4)).label("+5 V", "top")
        d += elm.Dot().at((xe, y0 + 4.0))
        d += elm.Line().endpoints((xe, y0 + 4.0), (1.4, y0 + 4.0))
        d += elm.Resistor().endpoints((1.4, y0 + 4.0), (1.4, q.base[1])).label("10k", loc="bottom")
        d += elm.Dot().at((1.4, q.base[1]))
        d += elm.Line().endpoints((1.4, q.base[1]), q.base)
        d += elm.Resistor().endpoints((-1.2, q.base[1]), (1.4, q.base[1])).label("$R_B$ 1k")
        d += elm.Dot(open=True).at((-1.2, q.base[1])).label("控制\n拉低 = 开", "left")
        d += elm.Line().endpoints(q.collector, (xe, y0 + 1.6))
        d += elm.Resistor().endpoints((xe, y0 + 1.6), (xe, y0 - 0.2)).label("负载", loc="bottom")
        d += elm.Ground().at((xe, y0 - 0.2))
        pinlab(d, q, fs_=8, at={"emitter": (0.2, -0.45, "left"), "collector": (0.2, 0.3, "left")})
        _bot_label(d, (2.0, y0 - 1.3), "(c) PNP 高边开关：负载的一端一直接地\n（→ 07、06）")
        # (d) 射极跟随器
        x0 = 9.2
        q = elm.BjtNpn().theta(0).anchor("base").at((x0 + 2.6, y0 + 2.4)); d += q
        xc = q.collector[0]
        d += elm.Line().endpoints(q.collector, (xc, y0 + 4.4))
        d += elm.Dot(open=True).at((xc, y0 + 4.4)).label("+12 V", "top")
        d += elm.Line().endpoints((x0 + 0.6, q.base[1]), q.base)
        d += elm.Dot(open=True).at((x0 + 0.6, q.base[1])).label("$V_i$", "left", color=schem.C["vin"])
        d += elm.Dot().at((xc, y0 + 1.4))
        d += elm.Line().endpoints(q.emitter, (xc, y0 + 1.4))
        d += elm.Line().endpoints((xc, y0 + 1.4), (xc + 1.6, y0 + 1.4))
        d += elm.Dot(open=True).at((xc + 1.6, y0 + 1.4)).label("$V_o \\approx V_i - 0.7$ V", "right", color=schem.C["vout"])
        d += elm.Resistor().endpoints((xc, y0 + 1.4), (xc, y0 - 0.4)).label("$R_E$", loc="bottom")
        d += elm.Ground().at((xc, y0 - 0.4))
        pinlab(d, q, fs_=8, at={"collector": (0.2, -0.3, "left"), "emitter": (0.2, 0.15, "left")})
        _bot_label(d, (x0 + 2.4, y0 - 1.3), "(d) 射极跟随：电压不放大，电流放大\n（→ 19、21）")
    print("[图 03-p1-7] (a) 共射放大 (b) NPN 低边驱动继电器 + 续流二极管 (c) PNP 高边开关 (d) 射极跟随器")
    schem.save_schem(d, P, "03_p1_7_bjt_uses.png")


def p1_8_mos_uses():
    with schem.drawing(fontsize=10) as d:
        # (a) N 沟道低边 PWM 调速
        m = elm.NFet().theta(0).reverse().anchor("drain").at((3.4, 1.0)); d += m
        xd = m.drain[0]
        d += elm.Motor().endpoints((xd, 3.8), (xd, 1.0))
        d += elm.Label().at((xd - 0.7, 2.4)).label("电机", halign="right")
        d += elm.Dot().at((xd, 3.8)); d += elm.Dot().at((xd, 1.0))
        d += elm.Line().endpoints((xd, 3.8), (xd, 4.2))
        d += elm.Dot(open=True).at((xd, 4.2)).label("+12 V", "top")
        d += elm.Line().endpoints((xd, 3.8), (xd + 1.3, 3.8))
        d += elm.Diode().endpoints((xd + 1.3, 1.0), (xd + 1.3, 3.8))
        d += elm.Line().endpoints((xd, 1.0), (xd + 1.3, 1.0))
        d += elm.Label().at((xd + 1.65, 2.4)).label("续流\n二极管", halign="left")
        g = m.gate
        d += elm.Resistor().endpoints((g[0] - 2.6, g[1]), (g[0] - 0.2, g[1])).label("100 Ω")
        d += elm.Line().endpoints((g[0] - 0.2, g[1]), g)
        d += elm.Dot(open=True).at((g[0] - 2.6, g[1])).label("单片机\nPWM", "left")
        d += elm.Dot().at((g[0] - 0.2, g[1]))
        d += elm.Resistor().endpoints((g[0] - 0.2, g[1]), (g[0] - 0.2, m.source[1] - 0.4)).label("100k", loc="bottom")
        d += elm.Line().endpoints((g[0] - 0.2, m.source[1] - 0.4), (xd, m.source[1] - 0.4))
        d += elm.Line().endpoints(m.source, (xd, m.source[1] - 0.4))
        d += elm.Ground().at((xd, m.source[1] - 0.4))
        pinlab(d, m, fs_=8)
        _bot_label(d, (2.6, -2.6), "(a) N 沟道低边开关：电机、灯带调速\n（AO3400A、IRLZ44N → 06、26）")
        # (b) P 沟道高边：给一整块电路通断电
        x0 = 10.4
        m = elm.PFet().theta(0).reverse().anchor("source").at((x0 + 3.6, 3.4)); d += m
        xs = m.source[0]; g = m.gate
        d += elm.Line().endpoints(m.source, (xs, 4.2))
        d += elm.Dot(open=True).at((xs, 4.2)).label("+5 V", "top")
        d += elm.Dot().at((xs, 3.8))
        xg = g[0] - 1.0
        d += elm.Line().endpoints((xs, 3.8), (xg, 3.8))
        d += elm.Resistor().endpoints((xg, 3.8), (xg, g[1])).label("10k", loc="bottom")
        d += elm.Dot().at((xg, g[1]))
        d += elm.Line().endpoints((xg, g[1]), g)
        n = elm.NFet().theta(0).reverse().anchor("drain").at((xg, g[1] - 0.8)); d += n
        d += elm.Line().endpoints((xg, g[1]), n.drain)
        d += elm.Ground().at(n.source)
        d += elm.Line().endpoints((n.gate[0] - 1.0, n.gate[1]), n.gate)
        d += elm.Dot(open=True).at((n.gate[0] - 1.0, n.gate[1])).label("单片机 3.3 V\n高 = 开", "left")
        d += elm.Resistor().endpoints(m.drain, (xs, m.drain[1] - 2.4)).label("后级电路", loc="bottom")
        d += elm.Ground().at((xs, m.drain[1] - 2.4))
        pinlab(d, m, fs_=8)
        d += elm.Label().at((n.gate[0] + 0.1, n.source[1] - 0.1)).label("BSS138", fontsize=8, halign="right")
        pinlab(d, n, fs_=8)
        _bot_label(d, (x0 + 2.4, -2.6), "(b) P 沟道高边开关：给后级电路通断电\n（AO3401A → 06）")
        # (c) BSS138 双向电平转换：源极接 3.3 V 一侧，漏极接 5 V 一侧，栅极固定接 3.3 V
        y0 = -9.6
        m = elm.NFet().theta(0).reverse().anchor("source").at((4.2, y0 + 0.8)); d += m
        s_, dr, g = m.source, m.drain, m.gate
        d += elm.Line().endpoints(s_, (4.2, y0 + 0.2)); d += elm.Dot().at((4.2, y0 + 0.2))
        d += elm.Line().endpoints((4.2, y0 + 0.2), (0.6, y0 + 0.2))
        d += elm.Dot(open=True).at((0.6, y0 + 0.2)).label("3.3 V 一侧\n（单片机）", "left")
        d += elm.Dot().at((1.8, y0 + 0.2))
        d += elm.Resistor().endpoints((1.8, y0 + 0.2), (1.8, y0 + 2.8)).label("10k", loc="bottom")
        d += elm.Dot(open=True).at((1.8, y0 + 2.8)).label("3.3 V", "top")
        d += elm.Line().endpoints(g, (3.2, g[1]))
        d += elm.Line().endpoints((3.2, g[1]), (3.2, y0 + 4.4))
        d += elm.Dot(open=True).at((3.2, y0 + 4.4)).label("3.3 V", "top")
        d += elm.Line().endpoints(dr, (4.2, y0 + 3.2)); d += elm.Dot().at((4.2, y0 + 3.2))
        d += elm.Line().endpoints((4.2, y0 + 3.2), (7.6, y0 + 3.2))
        d += elm.Dot(open=True).at((7.6, y0 + 3.2)).label("5 V 一侧\n（模块）", "right")
        d += elm.Dot().at((6.2, y0 + 3.2))
        d += elm.Resistor().endpoints((6.2, y0 + 3.2), (6.2, y0 + 5.6)).label("10k", loc="bottom")
        d += elm.Dot(open=True).at((6.2, y0 + 5.6)).label("5 V", "top")
        d += elm.Label().at((4.9, (s_[1] + dr[1]) / 2)).label("BSS138", fontsize=8.5, halign="left")
        pinlab(d, m, fs_=8)
        _bot_label(d, (4.0, y0 - 0.6), "(c) 电平转换：3.3 V ↔ 5 V\n（→ 29）")
        d += elm.Label().at((10.8, y0 + 2.6)).label(
            "还有一个常见用法：四只 MOS 管搭成 H 桥，\n让电机能正转、反转（→ 26）。\n\n"
            "选哪种：\n· 负载另一端接电源 → N 沟道放在下面（低边）\n· 负载另一端必须接地 → P 沟道放在上面（高边）",
            fontsize=9.5, halign="left", valign="center")
    print("[图 03-p1-8] (a) N 沟道低边 PWM + 续流二极管 + 100 Ω/100k (b) P 沟道高边 + 10k 上拉 + BSS138 拉低（+5 V） (c) BSS138 电平转换")
    schem.save_schem(d, P, "03_p1_8_mos_uses.png")


# ---------------- page2：共射放大一步一步算 ----------------
def p2_9_ce_amp():
    print("[图 03-p2-9] 共射放大：直流 0.95 V 串 ±0.1 V 小信号 → R_B 10 kΩ → 基极；5 V → R_C 1 kΩ → 集电极（输出 V_C）；发射极接地")
    cur = schem.C["cur"]
    with schem.drawing(fontsize=11) as d:
        x0 = 1.4
        q = _npn_switch(d, x0, "", "$R_B$  10 kΩ", "$V_{CC}$ = 5 V", "$R_C$\n1 kΩ")
        xc = q.collector[0]
        d += elm.Line().endpoints((0.0, 0.0), (x0 + 0.6, 0.0))
        d += elm.SourceSin().endpoints((0.0, -1.7), (0.0, 0.0))
        d += elm.Label().at((-0.8, -0.85)).label("小信号\n±0.1 V", halign="right", color=schem.C["vin"])
        d += elm.SourceV().endpoints((0.0, -3.4), (0.0, -1.7))
        d += elm.Label().at((-0.8, -2.55)).label("直流偏置\n0.95 V", halign="right")
        d += elm.Ground().at((0.0, -3.4))
        d += elm.Label().at((0.4, 0.45)).label("$V_i$", color=schem.C["vin"], halign="left")
        d += elm.Dot().at((xc, 1.2))
        d += elm.Line().endpoints((xc, 1.2), (xc + 2.0, 1.2))
        d += elm.Dot(open=True).at((xc + 2.0, 1.2)).label("输出 $V_C$", "right", color=schem.C["vout"])
        d += elm.Label().at((xc - 0.55, 2.6)).label("↓ $I_C$", color=cur, halign="right")
        d += elm.Label().at((x0 + 2.2, -0.75)).label("→ $I_B$", color=cur)
        d += elm.Label().at((xc + 0.4, -2.3)).label("① $I_B = (V_i - 0.7)/R_B$\n② $I_C = \\beta I_B$\n③ $V_C = V_{CC} - I_C R_C$",
                                                    halign="left", fontsize=10.5)
    schem.save_schem(d, P, "03_p2_9_ce_amp.png")


def p2_10_qpoint():
    a = AMP
    vce = np.linspace(0, 5.5, 600)
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    for ib_ua, key in [(15, "vin"), (25, "vout"), (35, "third")]:
        ax.plot(vce, bjt_ic(vce, ib_ua * 1e-6, a["beta"]) * 1e3, **fs.LS[key], label=f"$I_B$ = {ib_ua} µA")
    ax.plot(vce, (a["vcc"] - vce) / a["rc"] * 1e3, **fs.LS["good"], label="负载线（5 V、1 kΩ）")
    ib, ic, vc = ce_amp(np.array([a["vq"] - a["dv"], a["vq"], a["vq"] + a["dv"]]))
    txt = ["输入 0.85 V", "Q 点：输入 0.95 V", "输入 1.05 V"]
    for v, i, t, dy in zip(vc, ic * 1e3, txt, (8, 8, 8)):
        fs.mark(ax, v, i, fmt="{:.1f}", unit=" mA", dx=6, dy=dy)
        ax.annotate(t, (v, i), xytext=(-8, -14), textcoords="offset points", fontsize=8.5, color="0.25", ha="right")
    ax.annotate("", xy=(vc[2], -0.05), xytext=(vc[0], -0.05),
                arrowprops=dict(arrowstyle="<->", color=fs.C["vout"], lw=1.4))
    ax.text((vc[0] + vc[2]) / 2, 0.1, "$V_C$ 在 1.5～3.5 V 之间摆动（2 V）", ha="center", va="bottom", fontsize=9, color="k")
    ax.annotate("", xy=(5.25, ic[2] * 1e3), xytext=(5.25, ic[0] * 1e3),
                arrowprops=dict(arrowstyle="<->", color=fs.C["cur"], lw=1.4))
    ax.text(5.2, ic[1] * 1e3, "$I_C$ 摆动\n2 mA", ha="right", va="center", fontsize=9,
            bbox=dict(fc="white", ec="none", alpha=0.9, pad=1), zorder=5)
    ax.set_xlim(0, 5.5); ax.set_ylim(-0.4, 5.4)
    fs.axlabels(ax, "集电极电压 $V_C$（$= V_{CE}$）", "V", "集电极电流 $I_C$", "mA")
    ax.legend(loc="upper right", fontsize=8)
    assert np.allclose(vc, [3.5, 2.5, 1.5])
    fs.save(fig, P, "03_p2_10_qpoint.png")


def p2_11_bias():
    a = AMP
    t = np.linspace(0, 2, 801)
    fig, axs = plt.subplots(1, 3, figsize=(10, 3.4), sharey=True)
    cases = [(0.95, "(a) 偏置合适：中心 0.95 V"), (0.75, "(b) 偏置太低：中心 0.75 V"), (1.15, "(c) 偏置太高：中心 1.15 V")]
    for ax, (vq, title) in zip(axs, cases):
        vin = vq + a["dv"] * np.sin(2 * np.pi * t)
        vc = ce_amp(vin)[2]
        ideal = a["vcc"] - a["beta"] * (vin - a["vbe"]) / a["rb"] * a["rc"]
        ax.plot(t, ideal, **fs.LS["good"], label="不被削的样子")
        ax.plot(t, vc, **fs.LS["vout"], label="实际 $V_C$")
        clip = np.abs(vc - ideal) > 1e-6
        if clip.any():
            ax.plot(t[clip], vc[clip], color=fs.C["bad"], lw=2.4, ls="none", marker="x", ms=3, markevery=12)
        fs.ref_h(ax, 5.0, "5 V（截止）" if ax is axs[0] else None, x=0.98)
        fs.ref_h(ax, 0.2, "0.2 V（饱和）" if ax is axs[0] else None, x=0.98)
        ax.set_title(title, fontsize=9.5)
        print(f"[03 放大] {title}：V_C 实际 {vc.min():.2f}～{vc.max():.2f} V")
        fs.axlabels(ax, "时间", "ms")
    axs[0].set_ylabel(fs.qlabel("集电极 $V_C$", "V"))
    axs[1].text(1.0, 2.0, "顶上被削平：\n输入低的那半周\n基极电流降到 0", ha="center", fontsize=8.5, color=fs.C["bad"])
    axs[2].text(1.0, 2.6, "底下被削平：\n输入高的那半周\n三极管进了饱和", ha="center", fontsize=8.5, color=fs.C["bad"])
    axs[0].set_ylim(-0.8, 6.6)
    axs[0].legend(loc="upper left", fontsize=7.5)
    v_lo = ce_amp(0.75 + a["dv"] * np.sin(2 * np.pi * t))[2]; v_hi = ce_amp(1.15 + a["dv"] * np.sin(2 * np.pi * t))[2]
    assert abs(v_lo.max() - 5.0) < 1e-9 and abs(v_hi.min() - 0.2) < 1e-9
    fs.save(fig, P, "03_p2_11_bias.png")


# ---------------- page4 实验二：只用万用表看「放大」 ----------------
AMP_STEPS = [-0.10, -0.05, 0.0, 0.05, 0.10]


def p4_amp_numbers():
    """实验二（RB 10k、RC 1k、5 V，电位器上端串 22 kΩ）：先在 0～1.56 V 里扫出 V_C 曲线、找到 V_C = 2.5 V 的 Q 点，
    再算 Q ± 0.05 V、± 0.10 V 五个点和两头（0.60 V、1.30 V）的读数。全部用 ngspice + onsemi 2N3904 模型。"""
    top = 5 * 10 / 32
    grid = np.round(np.arange(0.0, top + 1e-9, 0.01), 3)
    body = "\n".join(f"V{k} i{k} 0 {v}\nRB{k} i{k} b{k} 10k\nRC{k} vcc c{k} 1k\nQ{k} c{k} b{k} 0 Q2n3904"
                     for k, v in enumerate(grid))
    r = bb_ng_op("VCC vcc 0 5\n" + body, [f"v(c{k})" for k in range(len(grid))], ["2N3904_onsemi.lib"])
    vcg = np.array([r[f"v(c{k})"] for k in range(len(grid))])
    k = np.where(vcg < 2.5)[0][0]
    vq = grid[k - 1] + (2.5 - vcg[k - 1]) * (grid[k] - grid[k - 1]) / (vcg[k] - vcg[k - 1])
    vq = round(vq, 3)
    pts = [round(vq + s, 3) for s in AMP_STEPS] + [0.60, 1.30]
    body = "\n".join(f"V{k} i{k} 0 {v}\nRB{k} i{k} b{k} 10k\nRC{k} vcc c{k} 1k\nQ{k} c{k} b{k} 0 Q2n3904"
                     for k, v in enumerate(pts))
    r = bb_ng_op("VCC vcc 0 5\n" + body, [f"v(b{k})" for k in range(len(pts))] + [f"v(c{k})" for k in range(len(pts))],
                 ["2N3904_onsemi.lib"])
    rows = []
    for k, v in enumerate(pts):
        vb, vc = r[f"v(b{k})"], r[f"v(c{k})"]
        ib, ic = (v - vb) / 10e3, (5 - vc) / 1e3
        rows.append((v, vb, vc, ib, ic))
        print(f"[03 page4 实验二] V_i = {v:.3f} V：V_B = {vb:.3f} V，V_C = {vc:.2f} V，I_B = {ib * 1e6:.1f} μA，"
              f"I_C = {ic * 1e3:.2f} mA，I_C/I_B = {ic / ib if ib > 1e-9 else float('nan'):.0f}")
    a, b = rows[0], rows[4]
    gain = (b[2] - a[2]) / (b[0] - a[0])
    beta_d = (b[4] - a[4]) / (b[3] - a[3])
    print(f"[03 page4 实验二] Q 点 V_i = {vq:.3f} V；V_i 变 {b[0] - a[0]:.2f} V，V_C 变 {b[2] - a[2]:+.2f} V，"
          f"放大倍数 {gain:+.1f}；V_B 只变 {(b[1] - a[1]) * 1e3:.0f} mV；ΔI_C/ΔI_B = {beta_d:.0f}")
    print(f"[03 page4 实验二] 电位器上端 {top:.3f} V；最大基极电流 < {(top - 0.6) / 10e3 * 1e6:.0f} μA；"
          f"最大集电极电流 < {5 / 1e3 * 1e3:.0f} mA；Q 点管耗 {2.5 * 2.5:.2f} mW")
    assert 0.83 < vq < 0.87, "和 review/spice/03.md 的 0.851 V 一致"
    assert -14 < gain < -8 and b[1] - a[1] < 0.05 and rows[5][2] > 4.0 and rows[6][2] < 0.4
    assert 100 < beta_d < 180
    return vq, rows, grid, vcg


def p4_4_breadboard_amp():
    """实验二的面包板：只改 B 区和电位器，A 区、C 区不动。"""
    rails = {"T1": ("+5 V", BB_WIRE["pos"]), "T2": ("GND", BB_WIRE["gnd"]),
             "B1": ("+9 V（电池）", BB_WIRE["pos"]), "B2": ("GND", BB_WIRE["gnd"])}
    fig, ax = bb_board(30, rails, figsize=(10, 6.2))
    bb_wire(ax, "T2-2", "B2-2", "gnd", via=[(-1.0, 10.8), (-1.0, -3.6)])
    # A 区（不动）
    bb_wire(ax, "T1-3", "a3", "pos")
    bb_res(ax, "b3", "b7", "1k")
    bb_part2(ax, "c7", "c10", "1N4148", kind="diode", dy=0.55)
    bb_wire(ax, "a10", "T2-10", "gnd")
    # B 区：放大
    bb_wire(ax, "a13", "b28", "sig", via=[(13, 10.2), (28.0, 10.2), (28.0, 8.6)])
    bb_res(ax, "b13", "b17", "RB 10k")
    bb_block(ax, ["d16", "d17", "d18"], "", pins=["E", "B", "C"], fc="#cfd8dc")
    _bb_label(ax, 13.6, 6.2, "2N3904 平面朝你\nE 发射极\nB 基极\nC 集电极", fs_=6.8)
    bb_wire(ax, "a16", "T2-16", "gnd", via=[(15.6, 9.0), (15.6, 10.8)])
    bb_res(ax, "c18", "c22", "RC 1k（换）")
    bb_wire(ax, "T1-22", "a22", "pos")
    bb_res(ax, "d22", "d27", "22k（新加）", dy=-0.6)
    bb_probe(ax, "e17", "②", dx=-0.6, dy=-0.9)
    bb_probe(ax, "e18", "③", dx=0.6, dy=-0.9)
    # 电位器：上端改由 22k 供电，下端仍接地
    bb_block(ax, ["c27", "c28", "c29"], "", pins=["+", "滑", "−"], fc="#d7ccc8")
    _bb_label(ax, 29.6, 8.0, "电位器\n10k", fs_=7)
    bb_wire(ax, "a29", "T2-29", "gnd")
    bb_probe(ax, "e28", "④", dx=0.0, dy=-0.9)
    # C 区（不动）
    bb_wire(ax, "B1-20", "j20", "pos")
    bb_res(ax, "i20", "i24", "R 560")
    bb_part2(ax, "h27", "h24", "1N4733A", kind="diode", dy=0.55)
    bb_wire(ax, "j27", "B2-27", "gnd")
    ax.text(6.5, 4.3, "A 区不动", ha="center", va="center", fontsize=8, color="0.3")
    ax.text(22.5, 4.3, "B 区：三极管放大（实验二）", ha="center", va="center", fontsize=8, color="0.3")
    ax.text(20.2, 2.0, "C 区不动", ha="center", va="center", fontsize=8, color="0.3", zorder=2,
            bbox=dict(boxstyle="square,pad=0.15", fc="#f4f1ea", ec="none"))
    bb_legend(ax, [("pos", "红线：接电源正极"), ("gnd", "黑线：接地"), ("sig", "蓝线：输入信号")])
    print("[图 03-p4-4] 实验二：RB 10k b13–b17，RC 1k c18–c22，红线 +5 V→a22，22k d22–d27（给电位器上端供电），"
          "LED 拔掉、+5 V→a25 和 +5 V→a27 两根红线拔掉，蓝线 a13→b28；测点② 第 17 列、③ 第 18 列、④ 第 28 列")
    fs.save(fig, P, "03_p4_4_breadboard_amp.png")


def p4_6_amp_curve(vq, rows, grid, vcg):
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    ax.plot(grid, vcg, **fs.LS["vout"], label="集电极 ③（SPICE，典型 2N3904）")
    ib, ic, vc = ce_amp(grid)
    ax.plot(grid, vc, **fs.LS["good"], label="第 2 页的理想模型（β = 100，$V_{BE}$ = 0.7 V）")
    for v, vb, c, _, _ in rows[:5]:
        ax.plot(v, c, "o", color=fs.C["third"], ms=6, zorder=5)
    fs.mark(ax, rows[0][0], rows[0][2], fmt="{:.2f}", unit=" V", dx=-46, dy=-4, color=fs.C["third"])
    fs.mark(ax, rows[2][0], rows[2][2], fmt="{:.2f}", unit=" V（Q 点）", dx=8, dy=2, color=fs.C["third"])
    fs.mark(ax, rows[4][0], rows[4][2], fmt="{:.2f}", unit=" V", dx=8, dy=0, color=fs.C["third"])
    ax.axvspan(rows[0][0], rows[4][0], color=fs.C["fill"], zorder=0)
    ax.text(0.30, 2.6, "截止：基极电流 ≈ 0\n③ 接近 5 V", ha="center", fontsize=8.5)
    ax.text(1.38, 1.3, "饱和：③ 贴着\n0.1～0.2 V", ha="center", fontsize=8.5)
    ax.text(vq, 4.7, "浅蓝色带：本实验\n调的五个点", ha="center", fontsize=8.5)
    fs.ref_h(ax, 2.5)
    ax.set_xlim(0, 1.6); ax.set_ylim(-0.2, 5.4)
    fs.axlabels(ax, "输入 ④（滑动端）", "V", "集电极 ③", "V")
    ax.legend(loc="lower left", fontsize=8)
    fs.save(fig, P, "03_p4_6_amp_curve.png")


if __name__ == "__main__":
    fs.check_cjk("偏置合适太低高中心削平样子实际时间输入最刻输出正好变化方向相反基极集电极发射极栅漏源沟道箭头朝外里"
                 "流进出导通比门限书画法没有小圆圈手册常见完整三段衬底线内部二极管指正好反过来平面你从上往下看"
                 "贴片号同样封装型顺序不一可以只是买到它自己数据为准插板前先查万用表挡核对遍相续继器单片机拉低开负载"
                 "端一直接地射跟随电压不放大流章节调速灯带后级通断电平转换模块还有个常用法四只搭成桥让正转选哪种放在下面"
                 "实验二新加换滑区动信号典型理想模型截止饱和贴着浅蓝色带本调五点摆动")
    amp_numbers()
    p1_4_amp_idea(); p1_5_symbols(); p1_6_pinouts(); p1_7_bjt_uses(); p1_8_mos_uses()
    p2_9_ce_amp(); p2_10_qpoint(); p2_11_bias()
    vq, rows, grid, vcg = p4_amp_numbers()
    p4_4_breadboard_amp(); p4_6_amp_curve(vq, rows, grid, vcg)
