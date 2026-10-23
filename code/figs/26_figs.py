"""26 上拉/下拉电阻与电平转换：全部配图（图 26-p2-2 由 code/26_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/26_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
import schemdraw.logic as logic
import numpy as np
import matplotlib.pyplot as plt

N = "26"
_spec = importlib.util.spec_from_file_location("sim26", os.path.join(HERE, "..", "26_sim.py"))
sim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sim)


def fig_p1_1():
    """悬空输入 vs 接了上拉电阻（示意）：人手靠近时，50 Hz 工频电场经约 0.5 pF 杂散电容耦合到引脚。"""
    t = np.arange(0, 0.1, 1e-5)
    rng = np.random.default_rng(7)
    c_c, c_in = 0.5e-12, 10e-12                       # 杂散耦合电容、引脚输入电容（示意）
    v_field = 20.0                                    # 人体相对地的 50 Hz 感应电压幅度（示意）
    drift = np.cumsum(rng.normal(0, 0.004, len(t)))   # 悬空节点上电荷慢慢漂移（示意）
    amp = v_field * c_c / (c_c + c_in)                # 电容分压：悬空时耦合进来的幅度
    v_float = np.clip(2.3 + drift + amp * np.sin(2 * np.pi * 50 * t), -0.5, 5.5)
    # 接 10 kΩ 上拉：引脚对地阻抗只有 10 kΩ，耦合电流 2πf·Cc·V 在它上面只产生微伏级电压
    amp_pu = v_field * 2 * np.pi * 50 * c_c * 10e3
    v_pu = 5.0 - amp_pu * np.sin(2 * np.pi * 50 * t)
    press = (t > 0.06) & (t < 0.08)
    v_float[press] = 0.0
    v_pu[press] = 0.0
    print(f"p1_1 悬空时耦合幅度 {amp:.2f} V；上拉 10 kΩ 时耦合幅度 {amp_pu*1e6:.0f} µV")
    read_f = np.where(v_float > sim.VIH, 1.0, np.where(v_float < sim.VIL, 0.0, 0.5))
    n_unsure = np.mean((v_float > sim.VIL) & (v_float < sim.VIH) & ~press)
    print(f"p1_1 悬空时有 {n_unsure*100:.0f}% 的时间落在 1.5～3.0 V 的「说不准」区")
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"][0:1] + (3.4,))
    ax.axhspan(sim.VIL, sim.VIH, color=fs.C["fill"], zorder=0)
    ax.text(25, (sim.VIL + sim.VIH) / 2, "VIL 1.5 V～VIH 3.0 V：读成 0 还是 1 说不准", fontsize=9, va="center",
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
    ax.plot(t * 1e3, v_float, **{**fs.LS["bad"], "markevery": 0.05}, label="悬空的引脚：电压随手的远近乱飘")
    ax.plot(t * 1e3, v_pu, **fs.LS["vout"], label="接 10 kΩ 上拉：稳稳停在 5 V")
    fs.ref_v(ax, 60, "按键按下", y=0.8)
    fs.ref_v(ax, 80, "松开", y=0.8)
    fs.ref_h(ax, sim.VIH)
    fs.ref_h(ax, sim.VIL)
    ax.set_ylim(-0.6, 7.6)
    ax.legend(loc="upper left", fontsize=9, ncol=2)
    fs.axlabels(ax, "时间", "ms", "引脚电压", "V")
    fs.save(fig, N, "26_p1_1_floating.png")
    assert amp > 0.5 and amp_pu < 1e-3 and n_unsure > 0.2


def fig_p1_2():
    """按一下按键，引脚电压的前 3 ms（示意抖动），程序数到几次「按下」。"""
    dt = 1e-6
    t = np.arange(4e-3, 8e-3, dt)
    closed = sim.bounce_state(t, 5e-3, 1.0, 2e-3, 1e-3, seed=3)
    v = np.where(closed, 0.0, 5.0)
    falls = int(np.count_nonzero(np.diff((v < 2.5).astype(int)) == 1))
    print(f"p1_2 一次按下，程序看到 {falls} 个下降沿")
    fig, ax = plt.subplots(figsize=(7, 2.8))
    ax.plot(t * 1e3, v, **{**fs.LS["bad"], "markevery": 0.04}, label=f"引脚电压：一次按下出现 {falls} 个下降沿")
    ax.plot([4, 5, 5, 8], [5, 5, 0, 0], **fs.LS["good"], label="理想按键：只跳一次")
    fs.ref_v(ax, 5.0, "手指按下")
    fs.span(ax, 5.0, 7.0, 5.6, "抖动约 2 ms", color="k")
    ax.set_ylim(-0.6, 6.6)
    ax.legend(loc="center right", fontsize=9)
    fs.axlabels(ax, "时间", "ms", "引脚电压", "V")
    fs.save(fig, N, "26_p1_2_bounce.png")
    assert falls >= 4
    return falls


def level_shifter_schem(d, x0=0.0, labels=True):
    """AN10441 的单 MOS 管双向电平转换：栅极接 3.3 V，源极接 3.3 V 侧，漏极接 5 V 侧。"""
    y = 2.0
    q = elm.NFet().theta(-90).reverse().anchor("source").at((x0 + 4.0, y))
    d += q
    d += elm.Label().at((q.gate[0] - 0.3, q.gate[1] + 0.3)).label("Q1 BSS138", halign="right")
    # 体二极管：正极在源极、负极在漏极（MOS 管内部自带，这里单独画出来）
    yd = y - 1.3
    d += elm.Line().endpoints(q.source, (q.source[0], yd))
    d += elm.Line().endpoints(q.drain, (q.drain[0], yd))
    d += elm.Diode().endpoints((q.source[0], yd), (q.drain[0], yd)).color("#8c8c8c")
    d += elm.Label().at(((q.source[0] + q.drain[0]) / 2, yd - 0.45)).label("体二极管（管内自带）", color="#8c8c8c")
    d += elm.Dot().at(q.source)
    d += elm.Dot().at(q.drain)
    # 低压侧
    d += elm.Line().endpoints((x0, y), q.source)
    d += elm.Dot().at((x0 + 2.0, y))
    d += elm.Resistor().endpoints((x0 + 2.0, y), (x0 + 2.0, y + 2.6)).label("RpL\n10 kΩ", loc="top")
    d += elm.Vdd().at((x0 + 2.0, y + 2.6)).label("3.3 V")
    d += elm.Dot(open=True).at((x0, y)).label("3.3 V 侧\n（单片机 SDA）", loc="left")
    # 栅极接 3.3 V
    d += elm.Line().endpoints(q.gate, (q.gate[0], y + 2.6))
    d += elm.Line().endpoints((x0 + 2.0, y + 2.6), (q.gate[0], y + 2.6))
    d += elm.Dot().at((x0 + 2.0, y + 2.6))
    # 高压侧
    d += elm.Line().endpoints(q.drain, (x0 + 9.5, y))
    d += elm.Dot().at((x0 + 7.0, y))
    d += elm.Resistor().endpoints((x0 + 7.0, y), (x0 + 7.0, y + 2.6)).label("RpH\n10 kΩ", loc="top")
    d += elm.Vdd().at((x0 + 7.0, y + 2.6)).label("5 V")
    d += elm.Dot(open=True).at((x0 + 9.5, y)).label("5 V 侧\n（传感器 SDA）", loc="right")
    d += elm.Label().at((q.source[0] - 0.15, y + 0.35)).label("S", halign="right")
    d += elm.Label().at((q.drain[0] + 0.15, y + 0.35)).label("D", halign="left")
    d += elm.Label().at((q.gate[0] - 0.15, q.gate[1] + 0.9)).label("G", halign="right")
    return q


def fig_p1_3():
    with drawing(fontsize=11) as d:
        level_shifter_schem(d)
        d += elm.Label().at((4.7, -0.6)).label("栅极 G 接低压电源 3.3 V；源极 S 接 3.3 V 侧，漏极 D 接 5 V 侧")
        save_schem(d, N, "26_p1_3_shifter.png")


def fig_p2_1():
    """RC + 施密特去抖电路：VCC—R1—A—R2—C，按键接 A 与地，C 上的电压进 74HC14。"""
    with drawing(fontsize=11) as d:
        d += elm.Vdd().at((0, 6)).label("+5 V")
        d += elm.Resistor().endpoints((0, 6), (0, 3.5)).label("R1\n10 kΩ", loc="top")
        d += elm.Dot().at((0, 3.5)).label("A", loc="left", ofst=0.15)
        d += elm.Button().endpoints((0, 3.5), (0, 1.0)).label("按键", loc="bottom")
        d += elm.Ground().at((0, 1.0))
        d += elm.Resistor().endpoints((0, 3.5), (3.5, 3.5)).label("R2 10 kΩ", loc="top")
        d += elm.Dot().at((3.5, 3.5)).label("B", loc="top", ofst=0.15)
        d += elm.Capacitor().endpoints((3.5, 3.5), (3.5, 1.0)).label("C\n1 μF", loc="bottom")
        d += elm.Ground().at((3.5, 1.0))
        d += elm.Line().endpoints((3.5, 3.5), (5.0, 3.5))
        g = logic.SchmittNot().anchor("in1").at((5.0, 3.5)).label("74HC14\n施密特反相器", loc="bottom", ofst=0.3)
        d += g
        d += elm.Line().endpoints(g.out, (g.out[0] + 1.2, g.out[1]))
        d += elm.Dot(open=True).at((g.out[0] + 1.2, g.out[1])).label("送单片机\n（按下 = 1）", loc="right")
        save_schem(d, N, "26_p2_1_rc_debounce.png")


def fig_p2_3():
    """电平转换仿真：(a) 正确接法，两边分别拉低；(b) 放大 3.3 V 侧松手后的上升沿；(c) 源漏接反。"""
    dt = 2e-9
    t = np.arange(0, 40e-6, dt)
    pl = (t > 5e-6) & (t < 15e-6)
    ph = (t > 22e-6) & (t < 32e-6)
    VL, VH = sim.level_shifter(t, pl, ph)
    VLs, VHs = sim.level_shifter(t, pl, ph, swapped=True)
    k = lambda tt: int(round(tt / dt))
    print(f"p2_3 正确接法：空闲 {VL[k(3e-6)]:.2f} / {VH[k(3e-6)]:.2f} V；3.3 V 侧拉低时 {VL[k(10e-6)]:.3f} / {VH[k(10e-6)]:.3f} V；"
          f"5 V 侧拉低时 {VL[k(27e-6)]:.3f} / {VH[k(27e-6)]:.3f} V")
    # 上升沿：MOS 管在低压侧约 3.3−1.3 = 2.0 V 时关断，之后两边各自充电
    i0 = k(15e-6)
    ii = i0 + np.argmax(VH[i0:] - VL[i0:] > 0.05)
    print(f"p2_3 松手后两边分开时的电压 {VL[ii]:.2f} V，时刻 +{(t[ii]-15e-6)*1e9:.0f} ns")
    t10 = lambda v, lev: (t[i0 + np.argmax(v[i0:] > lev)] - 15e-6) * 1e9
    print(f"p2_3 低压侧升到 0.7×3.3 V 用 {t10(VL, 0.7*3.3):.0f} ns，高压侧升到 0.7×5 V 用 {t10(VH, 0.7*5):.0f} ns")
    print(f"p2_3 接反：空闲 {VLs[k(3e-6)]:.2f} / {VHs[k(3e-6)]:.2f} V；3.3 V 侧拉低时 {VLs[k(10e-6)]:.3f} / {VHs[k(10e-6)]:.3f} V")
    fig, axs = plt.subplots(3, 1, figsize=(7, 6.4))
    us = t * 1e6
    for ax, a, b, ttl in [(axs[0], VL, VH, "(a) 正确接法：哪一边拉低，另一边都跟着变低；松手后各回各的高电平"),
                          (axs[2], VLs, VHs, "(c) 源极、漏极接反：空闲时 3.3 V 侧被体二极管抬到 3.85 V")]:
        ax.plot(us, b, **fs.LS["vout"], label="5 V 侧电压")
        ax.plot(us, a, **fs.LS["vin"], label="3.3 V 侧电压")
        ax.axvspan(5, 15, color=fs.C["fill"], zorder=0)
        ax.axvspan(22, 32, color=fs.C["fill2"], zorder=0)
        ax.text(10, 4.0, "3.3 V 侧\n器件拉低", ha="center", fontsize=8.5)
        ax.text(27, 4.0, "5 V 侧\n器件拉低", ha="center", fontsize=8.5)
        fs.ref_h(ax, 3.3, "3.3 V", x=0.5)
        ax.set_ylim(-0.4, 5.9)
        ax.set_title(ttl, fontsize=9.5)
        ax.legend(loc="center right", fontsize=8.5)
        fs.axlabels(ax, "时间", "μs", "电压", "V")
    # (b) 放大
    m = (t > 14.8e-6) & (t < 18e-6)
    axs[1].plot((t[m] - 15e-6) * 1e9, VH[m], **fs.LS["vout"], label="5 V 侧：后半段只靠 RpH 充电")
    axs[1].plot((t[m] - 15e-6) * 1e9, VL[m], **fs.LS["vin"], label="3.3 V 侧")
    fs.ref_h(axs[1], VL[ii], f"约 {VL[ii]:.1f} V 处 Q1 关断，两条线分开", x=0.99)
    axs[1].set_title("(b) 放大 15 μs 处：3.3 V 侧松手后的上升沿", fontsize=9.5)
    axs[1].set_ylim(-0.3, 5.6)
    axs[1].legend(loc="lower right", fontsize=8.5)
    fs.axlabels(axs[1], "松手后的时间", "ns", "电压", "V")
    fs.save(fig, N, "26_p2_3_shifter_sim.png")
    assert VL[k(27e-6)] < 0.2 and VH[k(10e-6)] < 0.2 and abs(VL[k(3e-6)] - 3.3) < 0.01
    assert VLs[k(3e-6)] > 3.7
    return VL[ii]


def fig_p3_1():
    """上拉电阻扫描：Cb = 200 pF、3.3 V、400 kHz（快速模式）。"""
    vcc, cb = 3.3, 200e-12
    lo, hi_fast, hi_std = sim.rp_min(vcc), sim.rp_max(300e-9, cb), sim.rp_max(1000e-9, cb)
    print(f"p3_1 Rp 最小 {lo:.0f} Ω；快速模式最大 {hi_fast:.0f} Ω；标准模式最大 {hi_std:.0f} Ω")
    fig, axs = plt.subplots(1, 2, figsize=(9.4, 3.4))
    t = np.arange(0, 5e-6, 2e-9)
    period = 2.5e-6
    released = (t % period) >= period / 2           # 前半周期主机拉低，后半周期松手
    styles = [(1.5e3, fs.LS["vout"]), (4.7e3, fs.LS["vin"]), (10e3, {**fs.LS["bad"], "markevery": 0.06})]
    for rp, st in styles:
        v = np.zeros_like(t)
        x = 0.0
        tau = rp * cb
        for i in range(1, len(t)):
            x = vcc + (x - vcc) * np.exp(-2e-9 / tau) if released[i] else 0.0
            v[i] = x
        v_end = v[np.argmax(t > period - 4e-9)]
        print(f"p3_1 Rp = {rp/1e3:.1f} kΩ：tr = {sim.rise_time(rp, cb)*1e9:.0f} ns，半个周期结束时 {v_end:.2f} V")
        axs[0].plot(t * 1e6, v, **st, label=f"{rp/1e3:g} kΩ")
    fs.ref_h(axs[0], 0.7 * vcc, "0.7·VCC = 2.31 V", x=0.53, ha="left", fs=8)
    fs.axlabels(axs[0], "时间", "μs", "SCL 电压", "V")
    axs[0].set_title("(a) 400 kHz 时钟，总线电容 200 pF", fontsize=9.5)
    axs[0].set_ylim(-0.2, 3.9)
    axs[0].legend(loc="upper left", fontsize=8.5, ncol=3)
    rp = np.linspace(500, 12e3, 300)
    axs[1].plot(rp / 1e3, sim.rise_time(rp, cb) * 1e9, **fs.LS["vout"], label="上升时间 tr = 0.8473·Rp·Cb")
    fs.ref_h(axs[1], 300, "快速模式上限 300 ns", x=0.99)
    fs.ref_h(axs[1], 1000, "标准模式上限 1000 ns", x=0.99)
    fs.ref_v(axs[1], lo / 1e3, f"Rp 最小 {lo/1e3:.2f} kΩ", y=0.6)
    axs[1].axvspan(lo / 1e3, hi_fast / 1e3, color=fs.C["fill"], zorder=0)
    axs[1].text(hi_fast / 1e3 + 0.3, 60, "← 阴影：快速模式可选范围", ha="left", fontsize=8.5)
    fs.axlabels(axs[1], "上拉电阻 Rp", "kΩ", "上升时间", "ns")
    axs[1].set_title("(b) Rp 越大，上升越慢", fontsize=9.5)
    axs[1].set_ylim(0, 2100)
    axs[1].legend(loc="upper left", fontsize=8.5)
    fs.save(fig, N, "26_p3_1_rp_sweep.png")
    assert 960 < lo < 970 and 1760 < hi_fast < 1780


def band_noise(n, dt, seed, rms=0.02, tau_n=50e-6):
    """示意噪声：白噪声经一阶低通（时间常数 50 μs）后缩放到 20 mV 有效值，代表地线、电源上的干扰。"""
    w = np.random.default_rng(seed).normal(0, 1, n)
    a = dt / tau_n
    y = np.empty(n); x = 0.0
    for i in range(n):
        x += a * (w[i] - x)
        y[i] = x
    return y / np.std(y) * rms


def fig_p3_2():
    """去抖时间常数扫描：R1 = R2 = R，C = 1 μF；20 次按键、每次抖动 0.5～6.2 ms（示意）；
    比较「施密特输入」和「无回差单门限 + 20 mV 低通噪声（示意）」两种读法。"""
    dt = 5e-6
    rs = np.array([100, 220, 470, 1e3, 2.2e3, 4.7e3, 10e3, 22e3, 47e3])
    rng = np.random.default_rng(11)
    events = [(rng.uniform(0.5e-3, 6.2e-3), rng.uniform(0.5e-3, 6.2e-3)) for _ in range(20)]
    extra_s, extra_p, delay = [], [], []
    for r in rs:
        es = ep = 0
        dmax = 0.0
        for j, (bp, br) in enumerate(events):
            t = np.arange(0, 0.4, dt)
            closed = sim.bounce_state(t, 0.01, 0.2, bp, br, seed=100 + j)
            vc = sim.rc_debounce(closed, dt, r, r, 1e-6)
            ls = sim.schmitt(vc)
            noise = band_noise(len(t), dt, 200 + j)
            lp = sim.plain_input(vc + noise)
            es += sim.count_edges(ls) - 2
            ep += sim.count_edges(lp) - 2
            i_f = np.argmax(~ls)
            i_r = i_f + np.argmax(ls[i_f:])
            dmax = max(dmax, t[i_f] - 0.01, t[i_r] - 0.2)
        extra_s.append(es / 20); extra_p.append(ep / 20); delay.append(dmax * 1e3)
        print(f"p3_2 R = {r/1e3:g} kΩ（按下 τ = {r*1e-6*1e3:g} ms）：施密特多出 {es/20:.2f} 次，单门限多出 {ep/20:.1f} 次，最长延迟 {dmax*1e3:.1f} ms")
    tau = rs * 1e-6 * 1e3
    fig, axs = plt.subplots(1, 2, figsize=(9.4, 3.3))
    axs[0].semilogx(tau, extra_p, **{**fs.LS["bad"], "markevery": 1}, label="无回差输入（单门限）")
    axs[0].semilogx(tau, extra_s, **fs.LS["vin"], marker="o", ms=4, label="施密特输入")
    fs.axlabels(axs[0], "按下时的时间常数 R2·C", "ms", "每次按键多出的翻转", "次")
    axs[0].set_title("(a) 多出来的翻转（理想是 0）", fontsize=9.5)
    axs[0].legend(loc="upper right", fontsize=8.5)
    axs[1].semilogx(tau, delay, **fs.LS["vout"], marker="o", ms=4, label="施密特输入的最长反应延迟")
    fs.ref_h(axs[1], 50, "50 ms：人感觉不到", x=0.6)
    fs.ref_h(axs[1], 100, "100 ms：明显迟钝", x=0.6)
    fs.axlabels(axs[1], "按下时的时间常数 R2·C", "ms", "延迟", "ms")
    axs[1].set_title("(b) 时间常数越大，反应越慢", fontsize=9.5)
    axs[1].set_ylim(0, 118)
    axs[1].legend(loc="upper left", fontsize=8.5)
    for ax in axs:
        ax.set_xticks([0.1, 0.3, 1, 3, 10, 30])
        ax.set_xticklabels(["0.1", "0.3", "1", "3", "10", "30"])
    fs.save(fig, N, "26_p3_2_tau_sweep.png")
    return rs, extra_s, extra_p, delay


if __name__ == "__main__":
    fig_p1_1(); fig_p1_2(); fig_p1_3()
    fig_p2_1(); fig_p2_3()
    fig_p3_1(); fig_p3_2()
