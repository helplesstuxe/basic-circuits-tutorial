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
