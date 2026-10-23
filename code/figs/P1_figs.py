"""P1 元件速成：除 P1_sim.py 那张以外的所有配图。运行：python code/figs/P1_figs.py
图上出现的每个数字都由本脚本打印（fs.mark 自动打印；其余用 print）。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

PLAIN = FuncFormatter(lambda v, _: f"{v:g}")   # 对数坐标的刻度写成 1、10、100，而不是 10^0、10^1
from schem import *          # elm、drawing、save_schem、Coil、ContactNO …，以及 figstyle 的全部内容
import figstyle as fs

P = "P1"

# ---------------- 图 P1-p1-1：分压电路 ----------------
def p1_1_divider():
    with drawing() as d:
        d += (src := elm.Battery().up())
        d += elm.Label().at((src.center.x - 0.9, src.center.y)).label("$V_i$\n12 V")
        d += elm.Line().right(2.5)
        d += (r1 := elm.Resistor().down().label("$R_1$\n10 kΩ"))
        d += (j := elm.Dot())
        d += (r2 := elm.Resistor().down().label("$R_2$\n10 kΩ"))
        d += elm.Line().left().tox(src.start)
        d += elm.Line().up().toy(src.start)          # 把电池下端接到底线上，回路闭合
        d += elm.Line().right().at(j.center).length(2.0)
        d += elm.Dot(open=True).label("$V_o$ = 6 V", "right")
        d += elm.Line().right().at(r2.end).length(2.0)
        d += elm.Dot(open=True).label("0 V", "right")
    print("[图 P1-p1-1] V_i = 12 V, R1 = R2 = 10 kΩ, V_o = 12×10/(10+10) =", 12 * 10 / 20, "V")
    save_schem(d, P, "P1_p1_1_divider.png")


# ---------------- 图 P1-p1-2：RC 充电电路 ----------------
def p1_2_rc():
    with drawing() as d:
        d += (src := elm.Battery().up().label("$V_i$\n5 V", "left"))
        d += elm.Switch().right().label("S")
        d += elm.Resistor().right().label("R  10 kΩ")
        d += (j := elm.Dot())
        d += (c := elm.Capacitor().down().label("C\n100 μF"))
        d += elm.Line().left().tox(src.start)
        d += elm.Line().right().at(j.center).length(1.5)
        d += elm.Dot(open=True).label("$V_C$ 输出", "right")
    print("[图 P1-p1-2] V_i = 5 V, R = 10 kΩ, C = 100 μF")
    save_schem(d, P, "P1_p1_2_rc.png")


# ---------------- 图 P1-p1-3：触点与按钮符号一览 ----------------
def p1_3_symbols():
    with drawing(fontsize=11) as d:
        items = [(Coil, "线圈\nKA / KM"), (ContactNO, "常开触点"), (ContactNC, "常闭触点"),
                 (PushNO, "常开按钮\n（启动）"), (PushNC, "常闭按钮\n（停止）"),
                 (TimerNO, "通电延时\n闭合常开"), (TimerNC, "通电延时\n断开常闭")]
        x = 0
        for cls, lab in items:
            d += elm.Line().at((x, 0)).down().length(0.4)
            d += cls().down().label(lab, "bottom", fontsize=10, ofst=0.35)
            d += elm.Line().down().length(0.4)
            x += 3.0
    print("[图 P1-p1-3] 7 个符号")
    save_schem(d, P, "P1_p1_3_symbols.png")


# ---------------- 图 P1-p1-4：继电器的两个回路 ----------------
def p1_4_relay_loops():
    with drawing(fontsize=11) as d:
        # 左：控制回路（低压 5 V）
        d += (b1 := elm.Battery().up().at((0, 0)).label("控制电源\n5 V", "left"))
        d += elm.Line().right(1.0)
        d += PushNO().right().label("SB 按钮", ofst=0.6)
        d += elm.Line().right(0.5)
        d += (coil := Coil().down().label("KA 线圈", "right"))
        d += elm.Line().left().tox(b1.start)
        # 右：负载回路（独立的 12 V）：常开触点竖着画在左边，正对线圈
        x0 = coil.start.x + 4.5
        d += (k := ContactNO().down().at((x0, coil.start.y)).label("KA 常开触点", "right", ofst=0.3))
        d += elm.Line().right(1.0)
        d += LampX().right().label("灯 EL", "bottom")
        d += elm.Line().right(1.0)
        d += (b2 := elm.Battery().up().label("负载电源\n12 V", "right"))
        d += elm.Line().up().toy(coil.start.y)
        d += elm.Line().left().tox(x0)
        # 磁力联系：灰色虚线（不是导线）
        cy = (coil.start.y + coil.end.y) / 2
        d += elm.Line().at((coil.center.x + 0.35, cy)).to((x0 + 0.35, cy)).linestyle("--").color("#808080")
        d += elm.Label().at(((coil.center.x + x0) / 2 + 0.1, cy + 0.9)).label("磁力吸合\n（虚线≠导线）", fontsize=10, color="#4d4d4d")
    print("[图 P1-p1-4] 控制电源 5 V，负载电源 12 V")
    save_schem(d, P, "P1_p1_4_relay_loops.png")


# ---------------- 图 P1-p2-1：分压器接负载后输出下降 ----------------
def p2_1_loading():
    Vi, R1, R2 = 12.0, 10e3, 10e3
    RL = np.logspace(3, 7, 400)
    par = R2 * RL / (R2 + RL)
    vo = Vi * par / (R1 + par)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.semilogx(RL / 1e3, np.full_like(RL, Vi * R2 / (R1 + R2)), **fs.LS["good"], label="空载公式 6 V（理想值）")
    ax.semilogx(RL / 1e3, vo, **fs.LS["vout"], label="$V_o$ 接负载 $R_L$ 后（实际）")
    for rl, dy in [(10e3, 6), (100e3, -14), (1e6, -14)]:
        p = R2 * rl / (R2 + rl); v = Vi * p / (R1 + p)
        fs.mark(ax, rl / 1e3, v, unit=" V", dx=4, dy=dy)
        assert (rl > 50e3) or v < 4.1
    v100 = Vi * (R2 * 100e3 / (R2 + 100e3)) / (R1 + R2 * 100e3 / (R2 + 100e3))
    print(f"[结论] R_L = 10×R2 时误差 {(6 - v100) / 6 * 100:.1f}%")
    assert 4 < (6 - v100) / 6 * 100 < 6
    fs.axlabels(ax, "负载电阻 $R_L$", "kΩ", "输出电压", "V")
    ax.set_ylim(0, 6.8); ax.legend(loc="lower right"); ax.xaxis.set_major_formatter(PLAIN)
    fs.save(fig, P, "P1_p2_1_loading.png")


# ---------------- 图 P1-p2-3：方波激励下的 RC 输出 ----------------
def p2_3_square():
    tau = 1e-3
    fig, axs = plt.subplots(3, 1, figsize=(7, 5.6))
    for ax, half in zip(axs, [10, 3, 1]):            # 方波半周期 = 10τ、3τ、1τ
        f = 1 / (2 * half * tau)
        dt = tau / 200
        t = np.arange(0, 6 * half * tau, dt)
        vin = fs.square(t, f, amp=2.5, offset=2.5)
        vc = np.zeros_like(t)
        for k in range(1, len(t)):
            vc[k] = vc[k - 1] + (vin[k - 1] - vc[k - 1]) / tau * dt
        x = t / tau
        ax.plot(x, vin, **fs.LS["vin"], label="$V_i$ 方波")
        ax.plot(x, vc, **fs.LS["vout"], label="$V_C$ 输出")
        last = t > 4 * half * tau                     # 取最后一个周期（已进入稳态）
        vmax, vmin = vc[last].max(), vc[last].min()
        i_max = np.where(last)[0][np.argmax(vc[last])]
        i_min = np.where(last)[0][np.argmin(vc[last])]
        fs.mark(ax, x[i_max], vmax, unit=" V", dx=3, dy=3)
        fs.mark(ax, x[i_min], vmin, unit=" V", dx=-36, dy=4)
        ax.set_title(f"半周期 = {half}τ", loc="left", fontsize=10)
        print(f"[图 P1-p2-3] 半周期 {half}τ：最高 {vmax:.2f} V，最低 {vmin:.2f} V")
        ax.set_ylim(-0.6, 6.2)
        fs.axlabels(ax, "时间", "τ", "电压", "V")
        if half == 1:
            th = 5 * np.exp(-1) / (1 + np.exp(-1))
            assert abs(vmin - th) < 0.05 and abs(vmax - (5 - th)) < 0.05
            print(f"[公式] 半周期 1τ 稳态最低 {th:.2f} V")
        if half == 10:
            assert vmax > 4.99
    axs[0].legend(loc="center", ncol=2, fontsize=8, bbox_to_anchor=(0.55, 0.5))
    fs.save(fig, P, "P1_p2_3_square.png")


# ---------------- 图 P1-p2-4：电感断电尖峰（有 / 无续流二极管） ----------------
def p2_4_flyback():
    V, R, L, Roff, VD = 12.0, 100.0, 0.1, 10e3, 0.7
    I0 = V / R
    t_off = 1e-3
    print(f"[参数] 线圈 L = {L} H，线圈电阻 {R:.0f} Ω，电流 {I0*1e3:.0f} mA，开关断开后等效 {Roff/1e3:.0f} kΩ")
    fig, axs = plt.subplots(2, 2, figsize=fs.SIZE["grid"])
    # 无二极管：电流只能经过断开的开关（等效 10 kΩ）走，τ' = L/(R+Roff)
    t1 = np.linspace(t_off - 20e-6, t_off + 60e-6, 3000)
    taup = L / (R + Roff)
    i1 = np.where(t1 < t_off, I0, I0 * np.exp(-(t1 - t_off) / taup))
    vsw = np.where(t1 < t_off, 0.0, i1 * Roff)                    # 开关两端电压 = 电流 × 断开电阻（电源 12 V 与线圈电压已在回路里抵消）
    x1 = (t1 - t_off) * 1e6
    axs[0, 0].plot(x1, i1 * 1e3, **fs.LS["cur"], label="线圈电流 $I$")
    axs[0, 1].plot(x1, vsw, **fs.LS["bad"], label="开关两端电压（无二极管）")
    peak = I0 * Roff                                               # 120 mA × 10 kΩ = 1200 V（与 SPICE 一致）
    fs.mark(axs[0, 1], 0, peak, fmt="{:.0f}", unit=" V", dx=5, dy=-8, color=fs.C["bad"])
    fs.mark(axs[0, 0], taup * 1e6, I0 * np.exp(-1) * 1e3, fmt="{:.1f}", unit=" mA", dx=5, dy=3)
    print(f"[图 P1-p2-4] 无二极管：τ' = {taup*1e6:.1f} μs，尖峰 {peak:.0f} V")
    assert peak > 1000
    # 有二极管：电流经二极管续流，线圈两端被钳在 −0.7 V，τ = L/R
    t2 = np.linspace(t_off - 0.5e-3, t_off + 5e-3, 3000)
    tau = L / R
    i2 = np.where(t2 < t_off, I0, np.maximum((I0 + VD / R) * np.exp(-(t2 - t_off) / tau) - VD / R, 0))
    vsw2 = np.where(t2 < t_off, 0.0, np.where(i2 > 0, V + VD, V))
    x2 = (t2 - t_off) * 1e3
    axs[1, 0].plot(x2, i2 * 1e3, **fs.LS["cur"], label="线圈电流 $I$")
    axs[1, 1].plot(x2, vsw2, **fs.LS["vout"], label="开关两端电压（有二极管）")
    fs.mark(axs[1, 1], 0.5, V + VD, fmt="{:.1f}", unit=" V", dx=5, dy=4)
    t_zero = x2[np.argmax((t2 > t_off) & (i2 <= 0))]
    fs.mark(axs[1, 0], tau * 1e3, float(np.interp(t_off + tau, t2, i2)) * 1e3, fmt="{:.1f}", unit=" mA", dx=5, dy=3)
    print(f"[图 P1-p2-4] 有二极管：τ = {tau*1e3:.1f} ms，电流在断开后 {t_zero:.2f} ms 降到 0，开关电压 {V+VD:.1f} V")
    assert V + VD < 13
    for ax in axs[0]:
        fs.ref_v(ax, 0, "开关断开", y=0.6)
        fs.axlabels(ax, "时间（相对断开时刻）", "μs")
    for ax in axs[1]:
        fs.ref_v(ax, 0, "开关断开", y=0.6)
        fs.axlabels(ax, "时间（相对断开时刻）", "ms")
    axs[0, 0].set_ylabel(fs.qlabel("电流", "mA")); axs[1, 0].set_ylabel(fs.qlabel("电流", "mA"))
    axs[0, 1].set_ylabel(fs.qlabel("电压", "V")); axs[1, 1].set_ylabel(fs.qlabel("电压", "V"))
    axs[0, 1].set_ylim(-50, 1400); axs[1, 1].set_ylim(-1, 16)
    axs[0, 0].set_title("（a）无续流二极管：电流 10 μs 级就被掐断", loc="left", fontsize=10)
    axs[0, 1].set_title("（b）无续流二极管：开关两端上千伏", loc="left", fontsize=10)
    axs[1, 0].set_title("（c）有续流二极管：电流慢慢衰减", loc="left", fontsize=10)
    axs[1, 1].set_title("（d）有续流二极管：只比电源高 0.7 V", loc="left", fontsize=10)
    print("[标题数字] 10 μs 级、0.7 V")
    for ax in axs.flat:
        ax.legend(loc="upper right", fontsize=8)
    fs.save(fig, P, "P1_p2_4_flyback.png")


# ---------------- 图 P1-p2-5：时间继电器时序 ----------------
def p2_5_timer():
    T = 3.0
    t = np.linspace(0, 14, 1400)
    coil = ((t >= 2) & (t < 8)).astype(float)
    on_delay = ((t >= 2 + T) & (t < 8)).astype(float)
    off_delay = ((t >= 2) & (t < 8 + T)).astype(float)
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    ax.plot(t, coil * 0.8 + 4, **fs.LS["vin"], label="KT 线圈通电")
    ax.plot(t, on_delay * 0.8 + 2, **fs.LS["vout"], label="通电延时型：常开触点")
    ax.plot(t, off_delay * 0.8 + 0, **fs.LS["third"], label="断电延时型：常开触点")
    fs.span(ax, 2, 2 + T, 3.0, "延时 3 s")
    fs.span(ax, 8, 8 + T, 1.0, "延时 3 s")
    for x, lab in [(2, "线圈通电 t = 2 s"), (8, "线圈断电 t = 8 s")]:
        fs.ref_v(ax, x, lab)
    print("[图 P1-p2-5] 延时 3 s，线圈 2 s 通电、8 s 断电；通电延时型 5 s 闭合 8 s 断开；断电延时型 2 s 闭合 11 s 断开")
    assert on_delay[np.searchsorted(t, 4.9)] == 0 and on_delay[np.searchsorted(t, 5.1)] == 1
    assert off_delay[np.searchsorted(t, 10.9)] == 1 and off_delay[np.searchsorted(t, 11.1)] == 0
    ax.set_yticks([0.4, 2.4, 4.4]); ax.set_yticklabels(["断电延时\n常开触点", "通电延时\n常开触点", "线圈"])
    ax.set_ylim(-0.4, 5.6); fs.axlabels(ax, "时间", "s")
    ax.legend(loc="upper right", fontsize=8)
    fs.save(fig, P, "P1_p2_5_timer.png")


# ---------------- 图 P1-p2-6：通电延时与断电延时的四种触点符号 ----------------
class TimerOffNO(Element2Term):
    """断电延时「断开」常开触点：与 TimerNO 相同，只是半圆弧翻过来，开口朝向动触片。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (0.85, 0.42), GAP, (1, 0)]))
        self.segments.append(Segment([(0.45, 0.22), (0.45, 0.78)]))
        self.segments.append(SegmentArc((0.45, 0.62), width=0.5, height=0.32, theta1=0, theta2=180))


class TimerOffNC(Element2Term):
    """断电延时「闭合」常闭触点：与 TimerNC 相同，只是半圆弧翻过来。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (1.12, 0.42), GAP, (1, 0)]))
        self.segments.append(Segment([(1, 0), (1, 0.5)]))
        self.segments.append(Segment([(0.5, 0.19), (0.5, 0.78)]))
        self.segments.append(SegmentArc((0.5, 0.62), width=0.5, height=0.32, theta1=0, theta2=180))


def p2_6_timer_symbols():
    with drawing(fontsize=11) as d:
        items = [(TimerNO, "通电延时型\n常开触点\n（延时闭合）"), (TimerNC, "通电延时型\n常闭触点\n（延时断开）"),
                 (TimerOffNO, "断电延时型\n常开触点\n（延时断开）"), (TimerOffNC, "断电延时型\n常闭触点\n（延时闭合）")]
        x = 0
        for cls, lab in items:
            d += elm.Line().at((x, 0)).down().length(0.4)
            d += cls().down().label(lab, "bottom", fontsize=10, ofst=0.35)
            d += elm.Line().down().length(0.4)
            x += 3.6
    print("[图 P1-p2-6] 4 个延时触点符号：通电延时型半圆弧开口朝右（背离动触片），断电延时型开口朝左（朝向动触片）")
    save_schem(d, P, "P1_p2_6_timer_symbols.png")


# ---------------- 图 P1-p2-7：戴维南等效——分压器 = 6 V 理想电压源串 5 kΩ 内阻 ----------------
def p2_7_thevenin():
    Vi, R1, R2 = 12.0, 10e3, 10e3
    Voc = Vi * R2 / (R1 + R2)                 # 空载（开路）电压
    Isc = Vi / R1                             # 输出端短路时的电流（R2 被短路，只剩 R1）
    Rth = Voc / Isc                           # 内阻 = 空载电压 ÷ 短路电流
    print(f"[P1-p2-7] 空载电压 V_th = {Voc:.2f} V，短路电流 = {Isc*1e3:.2f} mA，内阻 R_th = {Rth/1e3:.2f} kΩ")
    assert abs(Voc - 6) < 1e-9 and abs(Isc - 1.2e-3) < 1e-12 and abs(Rth - 5e3) < 1e-6
    assert abs(Rth - R1 * R2 / (R1 + R2)) < 1e-6          # 和「R1、R2 并联」的结果一样
    for RL in (10e3, 100e3):
        par = R2 * RL / (R2 + RL)
        direct = Vi * par / (R1 + par)                     # 原理篇第一节的老算法：先并联、再分压
        thev = Voc * RL / (Rth + RL)                       # 新算法：6 V 串 5 kΩ，再和 R_L 分压
        print(f"[P1-p2-7] R_L = {RL/1e3:g} kΩ：先并联再分压 {direct:.2f} V，等效电路 {thev:.2f} V，掉了 {(Voc-thev)/Voc*100:.1f}%")
        assert abs(direct - thev) < 1e-9
    # 规律：负载是内阻的 10 倍时，输出掉 1/11
    print(f"[P1-p2-7] R_L = 10 × R_th 时输出为空载的 {10/11*100:.1f}%，掉 {1/11*100:.1f}%")
    assert abs(1 / 11 * 100 - 9.1) < 0.05
    # 内阻算例（完整示例）：电源盒空载 5.00 V，接 100 Ω 后 4.00 V
    E, RLa, Va = 5.0, 100.0, 4.0
    Ia = Va / RLa; r = (E - Va) / Ia
    Vb = E * 50 / (r + 50)
    print(f"[P1 内阻算例] 电流 {Ia*1e3:.0f} mA，内阻 r = {r:.0f} Ω；换 50 Ω 负载输出 {Vb:.2f} V；短路电流 {E/r*1e3:.0f} mA")
    assert abs(Ia - 0.04) < 1e-12 and abs(r - 25) < 1e-9 and abs(Vb - 3.33) < 0.005
    # 内阻留空题：9 V 电池空载 9.0 V，接 30 Ω 后 8.1 V
    E5, R5, V5 = 9.0, 30.0, 8.1
    I5 = V5 / R5; r5 = (E5 - V5) / I5
    print(f"[P1 内阻留空题] 电流 {I5*1e3:.0f} mA，内阻 {r5:.2f} Ω；接 10 Ω 时输出 {E5*10/(r5+10):.2f} V")
    assert abs(I5 - 0.27) < 1e-9 and abs(r5 - 3.33) < 0.005
    with drawing(fontsize=11) as d:
        # 左：原来的分压器 + 负载
        d += (src := elm.Battery().up().at((0, 0)))
        d += elm.Label().at((src.center.x - 0.9, src.center.y)).label("12 V")
        d += elm.Line().right(2.0)
        d += elm.Resistor().down().label("$R_1$\n10 kΩ")
        d += (j := elm.Dot())
        d += elm.Resistor().down().label("$R_2$\n10 kΩ")
        d += elm.Line().left().tox(src.start)
        d += elm.Line().up().toy(src.start)
        d += elm.Line().right().at(j.center).length(1.8)
        d += (a := elm.Dot(open=True).label("A", "right"))
        d += elm.Resistor().down().label("$R_L$", "bottom")
        d += elm.Line().left().length(1.8)
        d += elm.Label().at((1.5, -2.9)).label("原电路：分压器 + 负载", fontsize=10)
        # 中间的「等效」箭头
        d += elm.Label().at((6.0, 1.5)).label("从 A 点往里看\n两者一模一样  ⇔", fontsize=10)
        # 右：等效电路
        x0 = 9.0
        d += (s2 := elm.Battery().up().at((x0, 0)))
        d += elm.Label().at((x0 - 0.9, s2.center.y)).label("$V_{th}$\n6 V")
        d += elm.Resistor().right().label("$R_{th}$  5 kΩ")
        d += (b := elm.Dot(open=True).label("A", "right"))
        d += elm.Resistor().down().label("$R_L$", "bottom")
        d += elm.Line().left().tox(s2.start)
        d += elm.Label().at((x0 + 1.5, -0.8)).label("等效电路：理想电压源串内阻", fontsize=10)
    save_schem(d, P, "P1_p2_7_thevenin.png")


# ---------------- 参数与调试篇新增练习的答案数字 ----------------
def p3_new_exercises():
    T, on, off = 3.0, 2.0, 6.0
    nd_close = on + T if on + T < off else None          # 通电延时常开：等满 3 s 才闭合，线圈先断电就不闭合
    print(f"[P1 练习 4] 线圈 {on:g} s 通电、{off:g} s 断电，设定 {T:g} s：通电延时常开 {nd_close:g} s 闭合、{off:g} s 断开；"
          f"断电延时常开 {on:g} s 闭合、{off + T:g} s 断开")
    assert nd_close == 5.0 and off + T == 9.0
    # 若线圈只通电 2 s（2 s→4 s），不到 3 s，通电延时触点根本不动作
    assert not (2.0 + T < 4.0)
    print("[P1 练习 4] 若线圈 2 s→4 s 只通电 2 s：通电延时常开不闭合；断电延时常开 2 s 闭合、7 s 断开")


# ---------------- 图 P1-p3-1：改变 R（τ）对充电曲线的影响 ----------------
def p3_1_tau_scan():
    C = 100e-6
    t = np.linspace(0, 12, 1200)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    styles = [(4.7e3, "fb"), (10e3, "vout"), (22e3, "third")]
    for R, key in styles:
        tau = R * C
        v = fs.rc_step(t, tau, 0, 5)
        ax.plot(t, v, **fs.LS[key], label=f"R = {R/1e3:g} kΩ，τ = {tau:.2f} s")
        fs.mark(ax, 5 * tau, 5 * (1 - np.exp(-5)), unit=" V", dx=-14, dy=-14, color=fs.C[key])
        print(f"[图 P1-p3-1] R = {R/1e3:g} kΩ, τ = {tau:.2f} s, 5τ = {5*tau:.2f} s")
    fs.ref_h(ax, 5, "$V_i$ = 5 V", x=0.02, ha="left")
    fs.axlabels(ax, "时间", "s", "电容电压 $V_C$", "V")
    ax.set_ylim(0, 5.8); ax.legend(loc="lower right")
    fs.save(fig, P, "P1_p3_1_tau_scan.png")


# ---------------- 图 P1-p3-2：分压电阻取多大——耗电与负载误差 ----------------
def p3_2_divider_tradeoff():
    Vi, RL = 12.0, 100e3
    Rtot = np.logspace(2, 6.3, 300)          # R1 + R2，从 100 Ω 到 2 MΩ（R1 = R2）
    R2 = Rtot / 2
    I = Vi / Rtot * 1e3                      # 空载电流 mA
    par = R2 * RL / (R2 + RL)
    vo = Vi * par / (Rtot / 2 + par)
    err = (6 - vo) / 6 * 100
    fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    axs[0].loglog(Rtot / 1e3, I, **fs.LS["cur"], label="分压器自身耗电流")
    axs[1].semilogx(Rtot / 1e3, err, **fs.LS["bad"], label="接 100 kΩ 负载后的误差")
    for rt in [2e3, 20e3, 200e3]:
        fs.mark(axs[0], rt / 1e3, Vi / rt * 1e3, fmt="{:.2g}", unit=" mA", dx=4, dy=2)
        r2 = rt / 2; p = r2 * RL / (r2 + RL); e = (6 - Vi * p / (r2 + p)) / 6 * 100
        fs.mark(axs[1], rt / 1e3, e, fmt="{:.1f}", unit="%", dx=-10, dy=6)
    axs[1].fill_between(Rtot / 1e3, 0, 50, where=err > 10, color=fs.C["bad"], alpha=0.08)
    fs.axlabels(axs[0], "$R_1+R_2$", "kΩ", "电流", "mA")
    fs.axlabels(axs[1], "$R_1+R_2$", "kΩ", "误差", "%")
    axs[1].set_ylim(0, 50)
    axs[0].xaxis.set_major_formatter(PLAIN); axs[1].xaxis.set_major_formatter(PLAIN); axs[0].yaxis.set_major_formatter(PLAIN)
    for ax in axs:
        ax.legend(loc="upper right", fontsize=8)
    print("[图 P1-p3-2] V_i = 12 V，R_L = 100 kΩ，阴影 = 误差 > 10%")
    fs.save(fig, P, "P1_p3_2_divider_tradeoff.png")


# ---------------- 图 P1-p3-3（答案图）：RL 电路通电电流 ----------------
def p3_3_rl_answer():
    V, R, L = 12.0, 100.0, 0.1
    tau = L / R
    t = np.linspace(0, 6e-3, 600)
    i = V / R * (1 - np.exp(-t / tau))
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(t * 1e3, i * 1e3, **fs.LS["cur"], label="线圈电流 $I$")
    fs.ref_h(ax, V / R * 1e3, "最终 120 mA", x=0.02, ha="left")
    fs.ref_v(ax, tau * 1e3, "t = τ = 1 ms"); fs.ref_v(ax, 5 * tau * 1e3, "t = 5τ = 5 ms")
    fs.mark(ax, tau * 1e3, V / R * (1 - np.exp(-1)) * 1e3, fmt="{:.1f}", unit=" mA", dx=5, dy=-12)
    fs.mark(ax, 5 * tau * 1e3, V / R * (1 - np.exp(-5)) * 1e3, fmt="{:.1f}", unit=" mA", dx=-40, dy=-14)
    print("[图 P1-p3-3] 最终 120 mA，τ = 1 ms，5τ = 5 ms")
    assert abs(V / R * (1 - np.exp(-1)) * 1e3 - 75.9) < 0.1
    fs.axlabels(ax, "时间", "ms", "电流", "mA")
    ax.set_ylim(0, 140); ax.legend(loc="lower right")
    fs.save(fig, P, "P1_p3_3_rl_answer.png")


# ---------------- 参数与调试篇引用的手册数字（无图，只打印并断言） ----------------
def p3_datasheet_numbers():
    # Omron G5V-1 线圈参数表（参考值）：额定电压 → (线圈电阻 Ω, 衔铁释放时 L, 衔铁吸合时 L)
    g5v1 = {3: (60, 0.05, 0.11), 12: (960, 0.85, 1.63), 24: (3840, 3.48, 6.61)}
    for v, (r, l_off, l_on) in g5v1.items():
        print(f"[P1 page3] G5V-1 {v} V 款：R = {r} Ω，L = {l_off}～{l_on} H，吸合后电感约 {l_on / l_off:.1f} 倍")
        assert 1.8 < l_on / l_off < 2.3                 # 衔铁吸上后电感约变成一倍多
    r12, lo, hi = g5v1[12]
    print(f"[P1 page3] 12 V 款 τ = L/R = {lo / r12 * 1e3:.2f}～{hi / r12 * 1e3:.2f} ms；示意线圈 0.1 H/100 Ω 的 τ = {0.1 / 100 * 1e3:.0f} ms")
    assert abs(lo / r12 * 1e3 - 0.89) < 0.01 and abs(hi / r12 * 1e3 - 1.70) < 0.01
    # Nichicon UVR：容量误差 ±20% → τ = 10 kΩ × 100 μF = 1 s 的实际范围
    tau = 10e3 * 100e-6
    print(f"[P1 page3] ±20% 电容：τ 标称 {tau:.1f} s，实际 {tau * 0.8:.1f}～{tau * 1.2:.1f} s")
    assert abs(tau - 1.0) < 1e-9
    # CDE 应用指南：寿命乘数 Mv = 4.3 − 3.3·VA/VR
    mv = lambda ratio: 4.3 - 3.3 * ratio
    print(f"[P1 page3] Mv(90%) = {mv(0.9):.2f}，Mv(2/3) = {mv(2 / 3):.2f}，比值 {mv(2 / 3) / mv(0.9):.1f}")
    assert abs(mv(0.9) - 1.33) < 0.005 and abs(mv(2 / 3) - 2.1) < 0.005 and abs(mv(2 / 3) / mv(0.9) - 1.6) < 0.05
    need = 12 * 1.5
    pick = min(v for v in (6.3, 10, 16, 25, 35, 50) if v >= need)   # UVR 系列的标称电压挡
    print(f"[P1 page3] 12 V 电源 × 1.5 = {need:.0f} V，标称挡选 {pick:g} V")
    assert need == 18 and pick == 25


if __name__ == "__main__":
    p1_1_divider(); p1_2_rc(); p1_3_symbols(); p1_4_relay_loops()
    p2_1_loading(); p2_3_square(); p2_4_flyback(); p2_5_timer(); p2_6_timer_symbols(); p2_7_thevenin()
    p3_1_tau_scan(); p3_2_divider_tradeoff(); p3_3_rl_answer()
    p3_datasheet_numbers(); p3_new_exercises()
