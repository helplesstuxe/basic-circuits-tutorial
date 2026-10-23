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
        d += (src := elm.Battery().up().label("$V_i$\n12 V", "left"))
        d += elm.Line().right(2.5)
        d += (r1 := elm.Resistor().down().label("$R_1$\n10 kΩ"))
        d += (j := elm.Dot())
        d += (r2 := elm.Resistor().down().label("$R_2$\n10 kΩ"))
        d += elm.Line().left().tox(src.start)
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
    vsw = np.where(t1 < t_off, 0.0, V + i1 * Roff)                # 开关两端电压
    x1 = (t1 - t_off) * 1e6
    axs[0, 0].plot(x1, i1 * 1e3, **fs.LS["cur"], label="线圈电流 $I$")
    axs[0, 1].plot(x1, vsw, **fs.LS["bad"], label="开关两端电压（无二极管）")
    peak = V + I0 * Roff
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


if __name__ == "__main__":
    p1_1_divider(); p1_2_rc(); p1_3_symbols(); p1_4_relay_loops()
    p2_1_loading(); p2_3_square(); p2_4_flyback(); p2_5_timer()
    p3_1_tau_scan(); p3_2_divider_tradeoff(); p3_3_rl_answer()
