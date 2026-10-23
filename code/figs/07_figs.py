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
    fs.ref_h(ax, 0.35, "2N3904 不加散热片 0.35 W", x=0.02, ha="left")
    fs.ref_h(ax, 2.0, "TIP31 不加散热片 2 W", x=0.02, ha="left")
    fs.mark(ax, vo[k], p[k], "{:.2f}", " W", dx=4, dy=4)
    fs.mark(ax, v5, p5, "{:.2f}", " W", dx=6, dy=-14)
    fs.axlabels(ax, "输出电压 $V_o$", "V", "管耗", "W"); ax.set_ylim(0, 2.3)
    ax.legend(loc="center right", fontsize=8)
    print(f"[图 07-p3-1] 最大管耗在 V_o = {vo[k]:.1f} V（V_CC 的一半），{p[k]:.2f} W；V_i 5 V 时 {p5:.2f} W")
    print(f"[温升] TIP31 不加散热片 θ_JA 62.5 °C/W：{p5:.2f} W → 结温比环境高 {p5 * 62.5:.0f} °C；最坏 {p[k]:.2f} W → {p[k] * 62.5:.0f} °C")
    assert abs(vo[k] - VCC / 2) < 0.1 and p5 > 0.35
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
