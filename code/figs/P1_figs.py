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


# ---------------- 动手实验篇：数值（每个数都打印并断言） ----------------
def p4_numbers():
    tol = 0.05                                   # 5% 电阻
    vs = 5.0                                     # USB / 面包板电源模块的 5 V
    lo_r, hi_r = 10e3 * (1 - tol), 10e3 * (1 + tol)
    par = lambda a, b: a * b / (a + b)
    # ① 10 kΩ/10 kΩ 分压，不接负载 / 接 10 kΩ / 接 100 kΩ：最坏组合 = R1 最大配 R2 最小，反之亦然
    def rng(rl=None):
        vals = []
        for r1 in (lo_r, hi_r):
            for r2 in (lo_r, hi_r):
                for k in ((1 - tol, 1 + tol) if rl else (1,)):
                    low = par(r2, rl * k) if rl else r2
                    vals.append(vs * low / (r1 + low))
        return min(vals), max(vals)
    d0, d10, d100 = rng(), rng(10e3), rng(100e3)
    nom = lambda rl=None: vs * (par(10e3, rl) if rl else 10e3) / (10e3 + (par(10e3, rl) if rl else 10e3))
    print(f"[P1 page4] 5 V 分压：空载 {nom():.2f} V（{d0[0]:.2f}～{d0[1]:.2f}），接 10 kΩ {nom(10e3):.2f} V（{d10[0]:.2f}～{d10[1]:.2f}），"
          f"接 100 kΩ {nom(100e3):.2f} V（{d100[0]:.2f}～{d100[1]:.2f}）")
    assert abs(nom() - 2.5) < 1e-9 and abs(nom(10e3) - 5 / 3) < 1e-9 and abs(nom(100e3) - 2.381) < 0.001
    assert (round(d0[0], 2), round(d0[1], 2)) == (2.38, 2.62)
    assert (round(d10[0], 2), round(d10[1], 2)) == (1.56, 1.78)
    assert (round(d100[0], 2), round(d100[1], 2)) == (2.26, 2.51)
    # ② RC：5 V、10 kΩ、100 μF，每秒读一次；电容 ±20%、电阻 ±5% → τ 0.76～1.26 s
    t = np.arange(0, 11)
    tmin, tmax = 10e3 * 0.95 * 100e-6 * 0.8, 10e3 * 1.05 * 100e-6 * 1.2
    v_nom = vs * (1 - np.exp(-t / 1.0))
    v_lo, v_hi = vs * (1 - np.exp(-t / tmax)), vs * (1 - np.exp(-t / tmin))
    print(f"[P1 page4] τ 范围 {tmin:.2f}～{tmax:.2f} s；1 s：{v_nom[1]:.2f} V（{v_lo[1]:.2f}～{v_hi[1]:.2f}），"
          f"2 s：{v_nom[2]:.2f} V（{v_lo[2]:.2f}～{v_hi[2]:.2f}），5 s：{v_nom[5]:.2f} V，10 s：{v_nom[10]:.3f} V")
    assert abs(tmin - 0.76) < 1e-9 and abs(tmax - 1.26) < 1e-9
    assert abs(v_nom[1] - 3.16) < 0.005 and abs(v_lo[1] - 2.74) < 0.005 and abs(v_hi[1] - 3.66) < 0.005
    assert abs(v_nom[5] - 4.97) < 0.005 and v_lo[10] > 4.99
    # 放大 10 倍：100 kΩ + 100 μF，τ = 10 s，万用表 10 MΩ 输入电阻只让终值低约 1%
    print(f"[P1 page4] 100 kΩ×100 μF：τ = {100e3 * 100e-6:.0f} s，10 s 时 {vs * (1 - np.exp(-1)):.2f} V；"
          f"10 MΩ 表笔并上后终值 {vs * 10e6 / (10e6 + 100e3):.2f} V")
    assert abs(vs * 10e6 / (10e6 + 100e3) - 4.95) < 0.001
    # ③ 继电器 Omron G5V-1-DC5：线圈 167 Ω ±10%，额定 30 mA，电感 0.15 H（释放）/ 0.29 H（吸合）
    rc, l_on = 167, 0.29
    print(f"[P1 page4] 线圈电阻 {rc * 0.9:.0f}～{rc * 1.1:.0f} Ω，5 V 时电流 {vs / rc * 1e3:.0f} mA，τ = L/R = {l_on / rc * 1e3:.2f} ms")
    assert round(rc * 0.9) == 150 and round(rc * 1.1) == 184 and round(vs / rc * 1e3) == 30
    # 松手后续流：线圈 + 二极管（压降 vd）回路，i = (I0 + vd/R)·e^(−t/τ) − vd/R，降到 0 的时间
    i0, tau = vs / rc, l_on / rc
    for name, vd in (("1N4007（0.7 V）", 0.7), ("LED + 1N4148（2.7 V）", 2.0 + 0.7)):
        t0 = tau * np.log((i0 + vd / rc) / (vd / rc))
        print(f"[P1 page4] 续流支路 {name}：电流从 {i0 * 1e3:.0f} mA 降到 0 用 {t0 * 1e3:.1f} ms；"
              f"开关（按钮）两端最高 {vs + vd:.1f} V")
    assert abs(tau * np.log((i0 + 2.7 / rc) / (2.7 / rc)) * 1e3 - 1.8) < 0.05
    assert abs(tau * np.log((i0 + 0.7 / rc) / (0.7 / rc)) * 1e3 - 3.6) < 0.05
    # 触点一侧：5 V → COM → NO → 红色 LED（约 2 V）→ 1 kΩ → 地
    print(f"[P1 page4] 触点侧 LED 电流约 {(vs - 2) / 1e3 * 1e3:.1f} mA，1 kΩ 上约 {vs - 2:.1f} V")
    return t, v_nom, v_lo, v_hi


# ---------------- 图 P1-p4-1：面包板接线图 ----------------
def p4_1_breadboard():
    rails = {"T1": ("+5 V", BB_WIRE["pos"]), "T2": ("GND", BB_WIRE["gnd"]),
             "B1": ("+5 V", BB_WIRE["pos"]), "B2": ("GND", BB_WIRE["gnd"])}
    fig, ax = bb_board(30, rails, figsize=(10, 6.2))
    # 上下电源轨在左端连起来
    bb_wire(ax, "T1-1", "B1-1", "pos", via=[(-0.4, 11.6), (-0.4, -2.8)])
    bb_wire(ax, "T2-2", "B2-2", "gnd", via=[(-1.0, 10.8), (-1.0, -3.6)])
    # A 区：分压器（第 3～11 列）
    bb_wire(ax, "T1-3", "a3", "pos")
    bb_res(ax, "b3", "b7", "R1 10k")
    bb_res(ax, "c7", "c11", "R2 10k")
    bb_wire(ax, "a11", "T2-11", "gnd")
    bb_res(ax, "e7", "e11", "RL", dy=-0.55)
    bb_probe(ax, "d7", "①", dx=-0.9, dy=0.0)
    # B 区：RC 充放电（第 13～19 列）
    bb_wire(ax, "T1-13", "a13", "pos")
    bb_block(ax, ["c13", "c14", "c15"], "", pins=["充", "公共", "放"], fc="#cfd8dc")
    _bb_label(ax, 14, 7.75, "SW 拨动开关")
    bb_wire(ax, "a15", "T2-15", "gnd")
    bb_res(ax, "e14", "e18", "R 10k", dy=0.55)
    bb_part2(ax, "b18", "b19", "C 100μF", kind="cap", dy=0.5)
    bb_wire(ax, "a19", "T2-19", "gnd")
    bb_probe(ax, "d18", "②", dx=0.9, dy=0.0)
    # C 区：继电器（下半块，第 18～30 列）
    bb_wire(ax, "B1-18", "j18", "pos")
    bb_block(ax, ["i18", "i21"], "SB 按钮", fc="#cfd8dc")
    bb_block(ax, ["g21", "g24", "g26", "g28"], "继电器 KA（G5V-1-DC5）",
             pins=["线圈+", "线圈−", "COM", "NO"], fc="#dbe8f5", fs_=7, tdy=-1.0)
    bb_part2(ax, "f24", "f21", "1N4007", kind="diode", dy=0.55)
    bb_wire(ax, "j24", "B2-24", "gnd")
    bb_wire(ax, "B1-26", "j26", "pos")
    bb_part2(ax, "i28", "i30", "LED", kind="led", fc="#ff6666", dy=0.55)
    bb_res(ax, "j30", "B2-30", "1k", dy=0.55)
    bb_probe(ax, "j21", "③", dx=0.0, dy=-0.9)
    for x, text in ((7, "A 区：分压"), (16, "B 区：RC 充放电"), (27.5, "C 区：继电器")):
        ax.text(x, 4.3, text, ha="center", va="center", fontsize=8, color="0.3")
    bb_legend(ax, [("pos", "红线：接 +5 V"), ("gnd", "黑线：接地")])
    print("[图 P1-p4-1] A：R1 b3–b7，R2 c7–c11，RL e7–e11，测点① 第 7 列；"
          "B：SW c13/c14/c15，R e14–e18，C b18(+)–b19，测点② 第 18 列；"
          "C：SB i18–i21，KA 线圈 g21/g24、COM g26、NO g28，1N4007 阴极 f21、阳极 f24，LED i28→i30，1 kΩ j30→地，测点③ 第 21 列")
    fs.save(fig, P, "P1_p4_1_breadboard.png")


# ---------------- 图 P1-p4-2：没有示波器时，每秒读一次万用表 ----------------
def p4_2_stopwatch(t, v_nom, v_lo, v_hi):
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    tt = np.linspace(0, 10, 400)
    ax.fill_between(tt, 5 * (1 - np.exp(-tt / 1.26)), 5 * (1 - np.exp(-tt / 0.76)), color=fs.C["fill"],
                    label="元件公差范围（τ 0.76～1.26 s）")
    ax.plot(tt, 5 * (1 - np.exp(-tt)), **fs.LS["good"], label="标称值（τ = 1 s）")
    ax.plot(t, v_nom, "o", color=fs.C["third"], ms=5, label="每秒读一次的读数")
    fs.ref_h(ax, 5.0, "5 V")
    fs.mark(ax, 1, v_nom[1], unit=" V", dx=0.25, dy=-0.35)
    fs.mark(ax, 2, v_nom[2], unit=" V", dx=0.25, dy=-0.35)
    fs.mark(ax, 5, v_nom[5], unit=" V", dx=0.0, dy=-0.45)
    ax.set_xlim(-0.2, 10.4); ax.set_ylim(0, 5.6)
    fs.axlabels(ax, "开关拨到「充」以后的时间", "s", "电容电压", "V")
    ax.legend(loc="lower right")
    fs.save(fig, P, "P1_p4_2_stopwatch.png")


if __name__ == "__main__":
    _t, _vn, _vl, _vh = p4_numbers()
    p4_1_breadboard(); p4_2_stopwatch(_t, _vn, _vl, _vh)


# ======================================================================================
# 第 8 轮补电路图（凡正文讲具体电路连接处，附近都要有电路图）
# ======================================================================================
EMPH = C["third"]          # 强调色（红紫）：新加上去的负载 R_L、等效出来的 R2∥R_L


# ---------------- 图 P1-p2-8：空载分压器 / 接 R_L / 等效成 R1 串 R2∥R_L ----------------
def p2_8_divider_load():
    Vi, R1, R2, RL = 12.0, 10e3, 10e3, 10e3
    par = R2 * RL / (R2 + RL)
    v0 = Vi * R2 / (R1 + R2)
    v1 = Vi * par / (R1 + par)
    i0, i1 = Vi / (R1 + R2), Vi / (R1 + par)
    print(f"[图 P1-p2-8] 空载：I = {i0*1e3:.2f} mA，V_o = {v0:.2f} V；接 R_L = 10 kΩ：R2∥R_L = {par/1e3:.2f} kΩ，"
          f"I = {i1*1e3:.2f} mA，V_o = {v1:.2f} V")
    assert abs(v0 - 6) < 1e-9 and abs(par - 5e3) < 1e-6 and abs(v1 - 4) < 1e-9
    with drawing(fontsize=11) as d:
        def divider(x0, title, rl=False, merged=False, vo="4.00 V"):
            """左边电池，中间 R1 / R2（或合并后的 R2∥R_L）竖排，右边 V_o 输出端；rl=True 时在 V_o 与地之间并上 R_L。"""
            nonlocal d
            xr, top, mid, bot = x0 + 2.4, 3.0, 0.0, -3.0          # 电阻那一竖列的 x；顶线、中点、底线（GND）的 y
            d += elm.Line().endpoints((x0, bot), (x0, -1.0))
            d += elm.Battery().endpoints((x0, -1.0), (x0, 1.0))
            d += elm.Line().endpoints((x0, 1.0), (x0, top))
            d += elm.Label().at((x0 - 0.95, 0.0)).label("$V_i$\n12 V")
            d += elm.Line().endpoints((x0, top), (xr, top))
            d += elm.Line().endpoints((xr, top), (xr, 2.5))
            d += (r1 := elm.Resistor().endpoints((xr, 2.5), (xr, 0.5)).label("$R_1$\n10 kΩ"))
            d += elm.Line().endpoints((xr, 0.5), (xr, mid))
            d += elm.Dot().at((xr, mid))
            d += elm.Line().endpoints((xr, mid), (xr, -0.5))
            r2 = elm.Resistor().endpoints((xr, -0.5), (xr, -2.5))
            d += (r2.color(EMPH).label("$R_2 \\parallel R_L$\n5 kΩ", color=EMPH) if merged else r2.label("$R_2$\n10 kΩ"))
            d += elm.Line().endpoints((xr, -2.5), (xr, bot))
            d += elm.Line().endpoints((xr, bot), (x0, bot))
            d += elm.CurrentLabelInline(direction="in").at(r1).label("$I$", loc="bottom")
            if rl:
                xl = xr + 1.9
                d += elm.Line().endpoints((xr, mid), (xl, mid))
                d += elm.Dot().at((xl, mid))
                d += elm.Line().endpoints((xl, mid), (xl + 0.9, mid))
                d += elm.Dot(open=True).at((xl + 0.9, mid)).label(f"$V_o$ = {vo}", "right", fontsize=10)
                d += elm.Line().endpoints((xl, mid), (xl, -0.5)).color(EMPH)
                d += elm.Resistor().endpoints((xl, -0.5), (xl, -2.5)).color(EMPH).label("$R_L$\n10 kΩ", "bottom", color=EMPH)
                d += elm.Line().endpoints((xl, -2.5), (xl, bot)).color(EMPH)
                d += elm.Line().endpoints((xl, bot), (xr, bot)).color(EMPH)
                d += elm.Dot().at((xr, bot))
            else:
                d += elm.Line().endpoints((xr, mid), (xr + 1.9, mid))
                d += elm.Dot(open=True).at((xr + 1.9, mid)).label(f"$V_o$ = {vo}", "right", fontsize=10)
            d += elm.Label().at((x0 + 1.2, bot - 0.35)).label("GND（0 V）", fontsize=9)
            d += elm.Label().at((x0 + 2.4, bot - 1.1)).label(title, fontsize=10)
        divider(0.0, "(a) 空载：$V_o$ 端什么都不接", vo="6.00 V")
        divider(8.0, "(b) 接上负载 $R_L$：$R_L$ 跨在 $V_o$ 和 GND 之间", rl=True)
        divider(17.0, "(c) 等效：$R_1$ 串 $R_2 \\parallel R_L$，再用分压公式", merged=True)
    save_schem(d, P, "P1_p2_8_divider_load.png")



def _coil_circuit(d, x0, diode, title, sw_text, cur_text=None):
    """12 V 电池 → 开关 S → 继电器线圈（竖着画）→ 回到 0 V；diode=True 时在线圈两端反向并联续流二极管（阴极朝 12 V）。"""
    top, bot = 2.5, -2.5
    xs, xc = x0 + 3.2, x0 + 5.0
    d += elm.Line().endpoints((x0, bot), (x0, -1.0))
    d += elm.Battery().endpoints((x0, -1.0), (x0, 1.0))
    d += elm.Line().endpoints((x0, 1.0), (x0, top))
    d += elm.Label().at((x0 - 0.9, 0.0)).label("12 V")
    d += elm.Line().endpoints((x0, top), (x0 + 0.8, top))
    d += elm.Switch().endpoints((x0 + 0.8, top), (x0 + 2.8, top)).label("S（刚断开）", fontsize=10)
    d += elm.Label().at((x0 + 1.8, top - 0.75)).label(sw_text, fontsize=9, color=C["bad"] if not diode else "black")
    d += elm.Line().endpoints((x0 + 2.8, top), (xc, top))
    d += elm.Line().endpoints((xc, top), (xc, 1.0))
    d += elm.Inductor2(loops=4).endpoints((xc, 1.0), (xc, -1.0))
    d += elm.Label().at((xc - 1.0, 0.0)).label("KA 线圈\n0.1 H\n100 Ω", fontsize=10)
    d += elm.Line().endpoints((xc, -1.0), (xc, bot))
    d += elm.Line().endpoints((xc, bot), (x0, bot))
    d += elm.Label().at((x0 + 2.4, bot - 0.35)).label("0 V", fontsize=9)
    if diode:
        xd = xc + 2.6
        d += elm.Dot().at((xc, top)); d += elm.Dot().at((xc, bot))
        d += elm.Line().endpoints((xc, top), (xd, top)).color(EMPH)
        d += elm.Line().endpoints((xd, top), (xd, 1.0)).color(EMPH)
        d += elm.Diode().endpoints((xd, -1.0), (xd, 1.0)).color(EMPH)
        d += elm.Label().at((xd + 1.3, 0.6)).label("续流二极管\n阴极朝 12 V", color=EMPH, fontsize=10)
        d += elm.Line().endpoints((xd, -1.0), (xd, bot)).color(EMPH)
        d += elm.Line().endpoints((xd, bot), (xc, bot)).color(EMPH)
        if cur_text:
            d += elm.LoopArrow(direction="ccw", width=0.9, height=1.6).at((xc + 1.3, 0)).color(C["cur"])
            d += elm.Label().at((xd + 1.3, -0.9)).label(cur_text, fontsize=9, color=C["cur"])
    d += elm.Label().at((x0 + 3.0, bot - 1.1)).label(title, fontsize=10)


# ---------------- 图 P1-p2-9：线圈断电的两种电路：无 / 有续流二极管 ----------------
def p2_9_flyback_circuit():
    print("[图 P1-p2-9] 12 V，线圈 0.1 H、100 Ω（120 mA）；无二极管时开关两端 1200 V，有二极管时 12.7 V")
    with drawing(fontsize=11) as d:
        _coil_circuit(d, 0.0, False, "(a) 不加二极管：电流只能硬挤过断开的开关", "开关两端约 1200 V")
        _coil_circuit(d, 9.5, True, "(b) 线圈两端反向并联续流二极管", "开关两端 12.7 V", "断电后电流\n在这个小圈里绕")
    save_schem(d, P, "P1_p2_9_flyback_circuit.png")


# ---------------- 图 P1-p1-5：续流二极管反向并联在线圈两端（直觉篇用的单张图） ----------------
def p1_5_freewheel():
    print("[图 P1-p1-5] 12 V → 开关 S → KA 线圈 → 0 V，续流二极管阴极接 12 V 一侧")
    with drawing(fontsize=11) as d:
        _coil_circuit(d, 0.0, True, "开关断开后，线圈的电流经二极管绕回线圈", "", "断电后电流\n在这个小圈里绕")
    save_schem(d, P, "P1_p1_5_freewheel.png")


# ---------------- 图 P1-p2-10：RC 充放电电路（输入 V_i 在 5 V 和 0 V 之间切换） ----------------
def p2_10_rc_circuit():
    print("[图 P1-p2-10] R = 10 kΩ，C = 100 μF，τ = 1 s；I = (V_i − V_C)/R")
    with drawing(fontsize=11) as d:
        top, bot = 2.0, -2.0
        d += elm.Line().endpoints((0, bot), (0, -1.0))
        d += elm.SourceSquare().endpoints((0, -1.0), (0, 1.0))
        d += elm.Line().endpoints((0, 1.0), (0, top))
        d += elm.Label().at((-1.6, 0.0)).label("$V_i$\n5 V 或 0 V", fontsize=10)
        d += (r := elm.Resistor().endpoints((0, top), (3.0, top)).label("R  10 kΩ"))
        d += elm.CurrentLabelInline(direction="in").at(r).label("$I$", loc="bottom")
        d += elm.Dot().at((3.0, top))
        d += elm.Capacitor().endpoints((3.0, top), (3.0, bot)).label("C\n100 μF")
        d += elm.Line().endpoints((3.0, bot), (0, bot))
        d += elm.Line().endpoints((3.0, top), (4.8, top))
        d += elm.Dot(open=True).at((4.8, top)).label("$V_C$", "right")
        d += elm.Line().endpoints((3.0, bot), (4.8, bot))
        d += elm.Dot(open=True).at((4.8, bot)).label("0 V", "right")
        d += elm.Dot().at((3.0, bot))
        d += elm.Label().at((1.5, top + 0.9)).label("电阻两端电压 = $V_i - V_C$", fontsize=10)
    save_schem(d, P, "P1_p2_10_rc_circuit.png")


# ---------------- 图 P1-p3-4：练习 6 那个画错的电路（线圈和自己的常开触点串在一个回路里） ----------------
def p3_4_wrong_loop():
    print("[图 P1-p3-4] 5 V → SB → KA 线圈 → KA 常开触点 → 灯 EL → 回到电源")
    with drawing(fontsize=11) as d:
        top, bot = 2.0, -2.0
        d += elm.Line().endpoints((0, bot), (0, -1.0))
        d += elm.Battery().endpoints((0, -1.0), (0, 1.0))
        d += elm.Line().endpoints((0, 1.0), (0, top))
        d += elm.Label().at((-0.9, 0)).label("5 V")
        d += PushNO().endpoints((0, top), (2.5, top)).label("SB", ofst=0.6)
        d += Coil().endpoints((2.5, top), (5.0, top)).label("KA 线圈", ofst=0.3)
        d += elm.Line().endpoints((5.0, top), (6.5, top))
        d += ContactNO().endpoints((6.5, top), (6.5, bot + 1.5)).label("KA 常开触点", "right", ofst=0.3)
        d += elm.Line().endpoints((6.5, bot + 1.5), (6.5, bot))
        d += LampX().endpoints((6.5, bot), (3.0, bot)).label("灯 EL", "bottom")
        d += elm.Line().endpoints((3.0, bot), (0, bot))
        d += elm.Label().at((3.2, -0.3)).label("全部串在一个回路里\n——这样接灯不会亮", fontsize=10, color=C["bad"])
    save_schem(d, P, "P1_p3_4_wrong_loop.png")



# ---------------- 图 P1-p3-5：带负载的分压器（参数篇的取舍图和练习 3 共用） ----------------
def p3_5_divider_load():
    print("[图 P1-p3-5] 12 V，R1 = R2，负载 R_L 跨在 V_o 与地之间")
    with drawing(fontsize=11) as d:
        x0, xr, xl, top, bot = 0.0, 2.4, 4.3, 3.0, -3.0
        d += elm.Line().endpoints((x0, bot), (x0, -1.0))
        d += elm.Battery().endpoints((x0, -1.0), (x0, 1.0))
        d += elm.Line().endpoints((x0, 1.0), (x0, top))
        d += elm.Label().at((x0 - 0.95, 0.0)).label("$V_i$\n12 V")
        d += elm.Line().endpoints((x0, top), (xr, top))
        d += elm.Resistor().endpoints((xr, top), (xr, 0.0)).label("$R_1$")
        d += elm.Dot().at((xr, 0.0))
        d += elm.Resistor().endpoints((xr, 0.0), (xr, bot)).label("$R_2$")
        d += elm.Line().endpoints((xr, bot), (x0, bot))
        d += elm.Line().endpoints((xr, 0.0), (xl, 0.0))
        d += elm.Dot().at((xl, 0.0))
        d += elm.Line().endpoints((xl, 0.0), (xl + 0.9, 0.0))
        d += elm.Dot(open=True).at((xl + 0.9, 0.0)).label("$V_o$", "right")
        d += elm.Resistor().endpoints((xl, 0.0), (xl, bot)).color(EMPH).label("$R_L$", "bottom", color=EMPH)
        d += elm.Line().endpoints((xl, bot), (xr, bot)).color(EMPH)
        d += elm.Dot().at((xr, bot))
        d += elm.Label().at((xr, bot - 0.4)).label("GND（0 V）", fontsize=9)
    save_schem(d, P, "P1_p3_5_divider_load.png")

if __name__ == "__main__":
    p1_5_freewheel(); p2_8_divider_load(); p2_9_flyback_circuit(); p2_10_rc_circuit(); p3_4_wrong_loop(); p3_5_divider_load()
