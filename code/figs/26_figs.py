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
    # 上升沿：MOS 管在低压侧约 3.3 V − VTH（模型 1 V）≈ 2.3 V 时关断，之后两边各自充电
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
    assert abs(VL[ii] - 2.32) < 0.05          # SPICE（Diodes BSS138 模型）分开点 2.32 V
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

import numpy as np                    # page4 面包板小工具要用
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs
from figstyle import C

# ======================================================================
# page4 动手实验篇：面包板俯视图（本节点自带一份小工具，只在本文件内使用）
# 面包板：列号 1..ncol；上半区 a–e 行、下半区 f–j 行，同一列的 a–e 五个孔连通，f–j 五个孔连通；
# 上下各两条电源轨（tp/tn 在上，bp/bn 在下），每条轨整条连通（有的面包板轨道在中间断开，正文会提醒）。
# 导线颜色：正电源 = 橙色，0 V（地）= 黑色，负电源 = 蓝色，信号 = 蓝绿色。
# 每条导线、每个元件引脚都登记到「网络」里（并查集），最后用 assert 检查想要的连接都接上了、不该通的没通。
# ======================================================================
import matplotlib.patches as mpatches

BB_Y = dict(a=9, b=8, c=7, d=6, e=5, f=3, g=2, h=1, i=0, j=-1)
BB_RAIL_Y = dict(tp=11.4, tn=10.6, bp=-2.6, bn=-3.4)
BB_WIRE = dict(pos=C["vout"], gnd="#000000", neg=C["vin"], sig=C["fb"])


class Breadboard:
    def __init__(self, ncol=30, rails=None, figsize=(10, 5.2)):
        self.ncol = ncol
        self.rails = rails or dict(tp=("+", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"), bn=("−", "neg"))
        self.parent = {}
        self.used = {}
        self.pins = {}
        self.fig, self.ax = plt.subplots(figsize=figsize)
        ax = self.ax
        ax.set_xlim(-7.5, ncol + 3.6)
        ax.set_ylim(-6.0, 12.4)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(mpatches.FancyBboxPatch((-0.6, -4.1), ncol + 1.2, 16.2, boxstyle="round,pad=0.1",
                                             fc="#f4f4f4", ec="0.6", lw=0.8))
        ax.add_patch(mpatches.Rectangle((-0.4, 3.6), ncol + 0.8, 0.8, fc="#e2e2e2", ec="none"))
        for r, y in BB_Y.items():
            ax.text(-0.9, y, r, ha="center", va="center", fontsize=7, color="0.35")
            ax.text(ncol + 0.9, y, r, ha="center", va="center", fontsize=7, color="0.35")
            for c in range(1, ncol + 1):
                ax.add_patch(mpatches.Rectangle((c - 0.13, y - 0.13), 0.26, 0.26, fc="0.72", ec="none"))
        for c in range(1, ncol + 1):
            if c == 1 or c % 5 == 0:
                ax.text(c, 9.75, str(c), ha="center", va="center", fontsize=7, color="0.35")
                ax.text(c, -1.75, str(c), ha="center", va="center", fontsize=7, color="0.35")
        for name, y in BB_RAIL_Y.items():
            lab, kind = self.rails[name]
            ax.plot([0.5, ncol + 0.5], [y + 0.32 * (1 if name in ("tp", "bp") else -1)] * 2,
                    color=BB_WIRE[kind], lw=1.0)
            ax.text(ncol + 1.0, y, lab, ha="left", va="center", fontsize=8, color=BB_WIRE[kind])
            for c in range(1, ncol + 1):
                if c % 6 != 0:
                    ax.add_patch(mpatches.Rectangle((c - 0.13, y - 0.13), 0.26, 0.26, fc="0.72", ec="none"))

    # ---- 孔位与网络 ----
    def xy(self, h):
        if isinstance(h, tuple):
            return h
        for rail in ("tp", "tn", "bp", "bn"):
            if h.startswith(rail):
                c = int(h[len(rail):])
                assert 1 <= c <= self.ncol and c % 6 != 0, f"电源轨孔 {h} 不存在"
                return (c, BB_RAIL_Y[rail])
        r, c = h[0], int(h[1:])
        assert r in BB_Y and 1 <= c <= self.ncol, f"孔 {h} 不存在"
        return (c, BB_Y[r])

    def strip(self, h):
        if isinstance(h, tuple):
            return ("ext", h)
        for rail in ("tp", "tn", "bp", "bn"):
            if h.startswith(rail):
                return rail
        return ("T" if h[0] in "abcde" else "B") + h[1:]

    def _find(self, s):
        self.parent.setdefault(s, s)
        while self.parent[s] != s:
            s = self.parent[s]
        return s

    def _union(self, a, b):
        self.parent[self._find(a)] = self._find(b)

    def _use(self, h, who):
        if isinstance(h, tuple):
            return
        self.xy(h)
        assert h not in self.used, f"孔 {h} 已被 {self.used[h]} 占用，{who} 不能再插"
        self.used[h] = who

    def net(self, h):
        return self._find(self.strip(self.pins.get(h, h)))

    def connected(self, *hs):
        return len({self.net(h) for h in hs}) == 1

    # ---- 画导线、元件、外部接线端 ----
    def wire(self, h1, h2, kind="sig", bend=0.0):
        self._use(h1, f"导线{h1}-{h2}")
        self._use(h2, f"导线{h1}-{h2}")
        self._union(self.strip(h1), self.strip(h2))
        (x1, y1), (x2, y2) = self.xy(h1), self.xy(h2)
        if bend:
            xm, ym = (x1 + x2) / 2, (y1 + y2) / 2 + bend
            t = np.linspace(0, 1, 30)
            xs = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * xm + t ** 2 * x2
            ys = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * ym + t ** 2 * y2
        else:
            xs, ys = [x1, x2], [y1, y2]
        self.ax.plot(xs, ys, color=BB_WIRE[kind], lw=2.4, solid_capstyle="round", zorder=3)
        for x, y in ((x1, y1), (x2, y2)):
            self.ax.plot(x, y, "o", ms=3.2, color=BB_WIRE[kind], zorder=4)

    def ext(self, xy, text, kind="sig", dx=-0.45, dy=0.0, ha="right"):
        """板外接线端（电池、电源、信号源的夹子）：画一个空心圆和文字，返回坐标元组，可直接当孔用。"""
        self.ax.plot(*xy, "o", ms=7, mfc="white", mec=BB_WIRE[kind], mew=1.6, zorder=5)
        self.ax.text(xy[0] + dx, xy[1] + dy, text, ha=ha, va="center", fontsize=8, color=BB_WIRE[kind], zorder=5)
        return xy

    def _pins(self, name, hs):
        for k, h in hs.items():
            self._use(h, f"{name}.{k}")
            self.pins[f"{name}.{k}"] = h

    def two(self, name, h1, h2, style="R", label=None, lpos=None):
        """两脚元件：style = R 电阻 / C 瓷片电容 / CE 电解电容（h1 为 + 脚）/ D 二极管（h1 阳极、h2 阴极）/ LED / Z 稳压管 / L 电感 / F 保险丝。"""
        self._pins(name, {"1": h1, "2": h2})
        (x1, y1), (x2, y2) = self.xy(h1), self.xy(h2)
        ax = self.ax
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        L = np.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        w = min(0.45 * L, 1.3)
        ax.plot([x1, xm - ux * w / 2], [y1, ym - uy * w / 2], color="0.45", lw=1.2, zorder=5)
        ax.plot([xm + ux * w / 2, x2], [ym + uy * w / 2, y2], color="0.45", lw=1.2, zorder=5)
        ang = np.degrees(np.arctan2(uy, ux))
        fc = dict(R="#d9c7a3", C="#f2d06b", CE="#5b7fa8", D="#444444", LED="#ffb3b3", Z="#9a6a3a",
                  L="#7f7f7f", F="#dddddd")[style]
        h = 0.55 if style != "CE" else 0.8
        rect = mpatches.FancyBboxPatch((xm - w / 2, ym - h / 2), w, h, boxstyle="round,pad=0.02",
                                       fc=fc, ec="0.25", lw=0.8, zorder=6)
        import matplotlib.transforms as mtr
        rect.set_transform(mtr.Affine2D().rotate_deg_around(xm, ym, ang) + ax.transData)
        ax.add_patch(rect)
        if style in ("D", "Z", "LED"):     # 阴极色环画在 h2 一端
            bx, by = xm + ux * w * 0.32, ym + uy * w * 0.32
            ax.plot([bx - uy * h / 2, bx + uy * h / 2], [by + ux * h / 2, by - ux * h / 2],
                    color="white" if style != "LED" else "0.2", lw=2.2, zorder=7)
        if style == "CE":
            ax.text(x1 - ux * 0.05 + 0.35 * uy, y1 + 0.35, "+", fontsize=9, ha="center", va="bottom",
                    color="k", zorder=7, fontweight="bold")
        if label:
            ox, oy = lpos or ((0, 0.62) if abs(uy) < 0.5 else (0.45, 0))
            ax.text(xm + ox, ym + oy, label, fontsize=7.5, ha="center" if abs(uy) < 0.5 and not lpos else "left",
                    va="center", zorder=8,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))

    def dip8(self, name, col, label, pinlabels=None):
        """8 脚双列直插芯片跨在中间凹槽上，缺口朝左：1–4 脚在 f 行（col..col+3），5–8 脚在 e 行（col+3..col）。"""
        hs = {}
        for k in range(4):
            hs[str(1 + k)] = f"f{col + k}"
            hs[str(8 - k)] = f"e{col + k}"
        self._pins(name, hs)
        ax = self.ax
        ax.add_patch(mpatches.FancyBboxPatch((col - 0.45, 3.35), 3.9, 1.3, boxstyle="round,pad=0.05",
                                             fc="#333333", ec="k", zorder=6))
        ax.add_patch(mpatches.Wedge((col - 0.45, 4.0), 0.25, -90, 90, fc="#888888", zorder=7))
        ax.text(col + 1.5, 4.0, label, color="white", fontsize=7.5, ha="center", va="center", zorder=7)
        for k in range(4):
            for pin, y in ((1 + k, 3.0), (8 - k, 5.0)):
                ax.plot([col + k, col + k], [y, 4.0 + (0.65 if y > 4 else -0.65)], color="0.3", lw=1.4, zorder=5)
            ax.text(col + k, 3.55, str(1 + k), color="white", fontsize=6, ha="center", va="center", zorder=8)
            ax.text(col + k, 4.45, str(8 - k), color="white", fontsize=6, ha="center", va="center", zorder=8)

    def multi(self, name, hs, label, w=None, h=1.0, fc="#555555", at=None):
        """多脚元件（三极管、电位器、模块……）：hs = {脚名: 孔}；画一个方块并从方块拉线到各脚，脚名标在孔旁。"""
        self._pins(name, hs)
        pts = [self.xy(v) for v in hs.values()]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        cx, cy = at or (np.mean(xs), max(ys) + 1.1)
        w = w or max(xs) - min(xs) + 1.0
        ax = self.ax
        ax.add_patch(mpatches.FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.05",
                                             fc=fc, ec="k", lw=0.8, zorder=6))
        ax.text(cx, cy, label, color="white", fontsize=7.5, ha="center", va="center", zorder=7)
        for k, (x, y) in zip(hs.keys(), pts):
            ax.plot([x, x], [y, cy - h / 2 if y < cy else cy + h / 2], color="0.3", lw=1.4, zorder=5)
            ax.text(x + 0.18, y + 0.32 * (1 if y < cy else -1), k, fontsize=6.5, ha="left",
                    va="bottom" if y < cy else "top", color="k", zorder=8)

    def probe(self, h, text, dx=0.35, dy=0.35, ha="left"):
        """测量点：在孔上画红紫色空心圈并写上名字。"""
        x, y = self.xy(h)
        self.ax.plot(x, y, "o", ms=9, mfc="none", mec=C["third"], mew=1.6, zorder=9)
        self.ax.text(x + dx, y + dy, text, fontsize=7.5, color=C["third"], ha=ha, va="bottom", zorder=9,
                     bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))

    def note(self, x, y, text, **kw):
        self.ax.text(x, y, text, fontsize=8, **kw)

    def legend(self, kinds=("pos", "gnd", "neg", "sig")):
        from matplotlib.lines import Line2D
        names = dict(pos="正电源线（橙）", gnd="0 V 地线（黑）", neg="负电源线（蓝）", sig="信号线（蓝绿）")
        hs = [Line2D([], [], color=BB_WIRE[k], lw=2.4, label=names[k]) for k in kinds]
        self.ax.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, 0.035), ncol=len(hs), fontsize=8,
                       frameon=False)


BB_WIRE["p33"] = C["vin"]          # 26 page4：+3.3 V 电源线用蓝色（本节点没有负电源）


class Breadboard26(Breadboard):
    """在通用面包板小工具上加两样东西：14 脚芯片、能区分 +5 V / +3.3 V 的图例。"""

    def dip14(self, name, col, label):
        """14 脚双列直插芯片跨在凹槽上，缺口朝左：1–7 脚在 f 行（col..col+6），8–14 脚在 e 行（col+6..col）。"""
        hs = {}
        for k in range(7):
            hs[str(1 + k)] = f"f{col + k}"
            hs[str(14 - k)] = f"e{col + k}"
        self._pins(name, hs)
        ax = self.ax
        ax.add_patch(mpatches.FancyBboxPatch((col - 0.45, 3.35), 6.9, 1.3, boxstyle="round,pad=0.05",
                                             fc="#333333", ec="k", zorder=6))
        ax.add_patch(mpatches.Wedge((col - 0.45, 4.0), 0.25, -90, 90, fc="#888888", zorder=7))
        ax.text(col + 3.0, 4.0, label, color="white", fontsize=7.5, ha="center", va="center", zorder=7)
        for k in range(7):
            for y in (3.0, 5.0):
                ax.plot([col + k, col + k], [y, 4.0 + (0.65 if y > 4 else -0.65)], color="0.3", lw=1.4, zorder=5)
            ax.text(col + k, 3.55, str(1 + k), color="white", fontsize=6, ha="center", va="center", zorder=8)
            ax.text(col + k, 4.45, str(14 - k), color="white", fontsize=6, ha="center", va="center", zorder=8)

    def button(self, name, h1, h2, label):
        """两脚轻触按键：两脚插在同一行的两个孔，按下才接通（画成带圆钮的小方块，不登记为导通）。"""
        self._pins(name, {"1": h1, "2": h2})
        (x1, y1), (x2, y2) = self.xy(h1), self.xy(h2)
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2 + 0.55
        ax = self.ax
        for x, y in ((x1, y1), (x2, y2)):
            ax.plot([x, x], [y, ym - 0.35], color="0.3", lw=1.4, zorder=5)
        ax.add_patch(mpatches.FancyBboxPatch((x1 - 0.2, ym - 0.4), x2 - x1 + 0.4, 0.8, boxstyle="round,pad=0.03",
                                             fc="#444444", ec="k", zorder=6))
        ax.add_patch(mpatches.Circle((xm, ym), 0.28, fc="#bbbbbb", ec="k", zorder=7))
        ax.text(xm, ym + 0.65, label, fontsize=7.5, ha="center", va="bottom", zorder=8,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))

    def legend26(self, kinds):
        from matplotlib.lines import Line2D
        names = dict(pos="+5 V 线（橙）", p33="+3.3 V 线（蓝）", gnd="0 V 地线（黑）", sig="信号线（蓝绿）")
        hs = [Line2D([], [], color=BB_WIRE[k], lw=2.4, label=names[k]) for k in kinds]
        self.ax.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, 0.035), ncol=len(hs), fontsize=8,
                       frameon=False)


def bb26_debounce():
    """26 page4 第一部分：上拉 + RC + 74HC14 消抖，C1 用 100 µF 让「消抖」慢到秒级，两只 LED 对比。
    门 1（1→2 脚）接 RC 之后的 B 点，门 2（3→4 脚）直接接按键上的 A 点。"""
    bb = Breadboard26(ncol=30, rails=dict(tp=("+5 V", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"),
                                          bn=("+3.3 V（本部分不用）", "p33")), figsize=(10.5, 6.0))
    bb.wire(bb.ext((-2.0, 11.4), "电源模块 5 V", "pos"), "tp1", "pos")
    bb.wire(bb.ext((-2.0, 10.0), "电源模块 GND", "gnd"), "tn2", "gnd")
    bb.wire("tn3", "bp3", "gnd")                                 # 上下两条 0 V 轨连起来
    # 上拉与按键：A 点 = 第 9 列（上下两半用 e9–f9 连起来）
    bb.two("R1", "tp8", "a9", "R", "R1 10k", lpos=(-1.2, 0.0))
    bb.wire("a7", "tn7", "gnd")
    bb.button("K1", "c7", "c9", "K1")
    bb.wire("e9", "f9", "sig")
    # RC：A —R2— B，B —C1— 0 V，B 直接是 74HC14 的 1 脚
    bb.two("R2", "g9", "g13", "R", "R2 10k", lpos=(0, 0.5))
    bb.two("C1", "j13", "bp13", "CE", "C1 100µ", lpos=(0.9, 0.0))
    bb.dip14("U1", 13, "74HC14")
    bb.wire("a13", "tp13", "pos")                                # 14 脚 VCC
    bb.two("C0", "b13", "tn11", "C", "100n", lpos=(-0.9, 0.0))
    bb.wire("j19", "bp19", "gnd")                                # 7 脚 GND
    for top, rail in (("a14", "tn14"), ("a16", "tn16"), ("a18", "tn17")):   # 13、11、9 脚（没用的输入）接地
        bb.wire(top, rail, "gnd")
    bb.wire("j17", "bp17", "gnd")                                # 5 脚（没用的输入）接地
    bb.wire("i9", "i15", "sig", bend=-0.45)                     # A 点 → 3 脚（门 2 输入，不经 RC）
    # 两路输出各接 1k + 红色 LED 到地
    bb.wire("h14", "h21", "sig", bend=0.45)                      # 2 脚 → 第 21 列
    bb.two("R3", "g21", "g25", "R", "R3 1k", lpos=(0, 0.5))
    bb.two("LED1", "j25", "bp25", "LED", "LED1", lpos=(0.75, 0.0))
    bb.wire("i16", "i27", "sig", bend=-0.45)                     # 4 脚 → 第 27 列
    bb.two("R4", "h27", "h29", "R", "R4 1k", lpos=(0, 0.5))
    bb.two("LED2", "j29", "bp29", "LED", "LED2", lpos=(0.85, 0.0))
    assert bb.connected("U1.14", "tp1") and bb.connected("U1.7", "tn2") and bb.connected("C0.2", "tn2")
    assert bb.connected("R1.2", "K1.2", "R2.1", "U1.3")          # A 点
    assert bb.connected("K1.1", "tn2")
    assert bb.connected("R2.2", "C1.1", "U1.1") and bb.connected("C1.2", "tn2")   # B 点
    assert bb.connected("U1.2", "R3.1") and bb.connected("R3.2", "LED1.1") and bb.connected("LED1.2", "tn2")
    assert bb.connected("U1.4", "R4.1") and bb.connected("R4.2", "LED2.1") and bb.connected("LED2.2", "tn2")
    for p in ("5", "9", "11", "13"):
        assert bb.connected(f"U1.{p}", "tn2"), p
    assert not bb.connected("tp1", "tn2") and not bb.connected("U1.1", "U1.3") and not bb.connected("U1.2", "U1.4")
    bb.probe("d9", "A", dx=0.3, dy=0.05)
    bb.probe("h13", "B", dx=0.3, dy=0.05)
    bb.probe("j14", "Y1", dx=-0.3, dy=-0.05, ha="right")
    bb.probe("j16", "Y2", dx=0.3, dy=-0.05)
    bb.note(15.0, -4.65, "按住 K1：LED2 立刻亮，LED1 约 1 s 后才亮；松开：LED2 约 0.2 s 后灭，LED1 约 1.6 s 后灭", ha="center")
    bb.note(15.0, -5.2, "C1 是电解电容，长脚（+）插 j13 接 B 点，短脚（−）插 0 V 轨；换 470 µF 后两个延时约 4.9 s / 7.7 s", ha="center")
    bb.legend26(("pos", "gnd", "sig"))
    print(f"26 p4 面包板一：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def bb26_shifter():
    """26 page4 第二、三部分：BSS138 双向电平转换。上排电源轨 3.3 V，下排 5 V；
    BSS138 焊在 SOT-23 转接板上，1 G、2 S、3 D 三个排针插 e13、e14、e15。"""
    bb = Breadboard26(ncol=30, rails=dict(tp=("+3.3 V", "p33"), tn=("0 V", "gnd"), bp=("0 V", "gnd"),
                                          bn=("+5 V", "pos")), figsize=(10.5, 6.0))
    bb.wire(bb.ext((-2.0, 11.4), "电源模块 3.3 V", "p33"), "tp1", "p33")
    bb.wire(bb.ext((-2.0, 10.0), "电源模块 GND", "gnd"), "tn2", "gnd")
    bb.wire(bb.ext((-2.0, -3.4), "电源模块 5 V", "pos"), "bn1", "pos")
    bb.wire("tn28", "bp28", "gnd")
    # 3.3 V 侧：第 2 列接 3.3 V，RPL 上拉到 L 点（第 6 列）
    bb.wire("a2", "tp2", "p33")
    bb.two("RPL", "b2", "b6", "R", "RPL 10k", lpos=(0, 0.5))
    bb.wire("d6", "d14", "sig", bend=0.45)                       # L 线 → S
    bb.wire("a6", bb.ext((4.6, 10.0), "L 拉低线", "sig", dx=-0.3), "sig")
    # 管子：转接板在凹槽上方
    bb.multi("Q1", {"G": "e13", "S": "e14", "D": "e15"}, "BSS138", w=2.9, h=0.7, at=(14.0, 4.0))
    bb.wire("a13", "tp13", "p33")                                # G 接 3.3 V
    bb.wire("c15", "g19", "sig")                                 # D → H 点（第 19 列下半）
    # 5 V 侧：第 23 列接 5 V，RPH 上拉到 H 点
    bb.two("RPH", "h19", "h23", "R", "RPH 10k", lpos=(0, 0.5))
    bb.wire("j23", "bn23", "pos")
    bb.wire("j19", bb.ext((21.0, -4.55), "H 拉低线", "sig", dx=-0.3), "sig")
    assert bb.connected("Q1.G", "tp1") and bb.connected("Q1.S", "RPL.2") and bb.connected("RPL.1", "tp1")
    assert bb.connected("Q1.D", "RPH.1") and bb.connected("RPH.2", "bn1")
    assert not bb.connected("Q1.S", "Q1.D") and not bb.connected("tp1", "bn1") and not bb.connected("tp1", "tn2")
    bb.probe("e6", "L（3.3 V 侧）", dx=0.3, dy=-0.75)
    bb.probe("i19", "H（5 V 侧）", dx=0.3, dy=-0.05)
    bb.probe("b13", "G", dx=0.3, dy=0.05)
    bb.note(21.5, 7.6, "第三部分（接反）：把 d14 那头改插 d15，\nc15 那头改插 c14，S、D 两侧对调", ha="center")
    bb.note(15.0, -5.2, "拉低线平时悬空；要拉低时插到最近的 0 V 轨；串一只 100 Ω 再插 = 模拟芯片开漏输出的导通电阻", ha="center")
    bb.legend26(("p33", "pos", "gnd", "sig"))
    print(f"26 p4 面包板二：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def p4_breadboards():
    bb = bb26_debounce()
    fs.save(bb.fig, N, "26_p4_1_bb_debounce.png")
    plt.close(bb.fig)
    bb = bb26_shifter()
    fs.save(bb.fig, N, "26_p4_2_bb_level_shift.png")
    plt.close(bb.fig)
    print("26_figs p4 OK")


if __name__ == "__main__":
    p4_breadboards()


# ======================= 第 8 轮补电路图（page1–page3：凡正文讲具体电路连接处，附近都要有电路图） =======================
from schem import C as _C
EMPH = _C["third"]      # 强调色（红紫）：新加的上拉 / 下拉电阻等
BAD = _C["bad"]


def _pin(d, x, y, text="单片机\n输入引脚"):
    d += elm.Line().endpoints((x, y), (x + 1.2, y))
    d += elm.Dot(open=True).at((x + 1.2, y)).label(text, "right")


def fig_p1_4():
    """图 26-p1-4：悬空、上拉、下拉三种接法（按键与电阻的位置）。"""
    with drawing(fontsize=11) as d:
        # (a) 悬空
        x = 0.0
        d += elm.Dot().at((x, 3.0))
        d += elm.Button().endpoints((x, 3.0), (x, 0.6))
        d += elm.Label().at((x - 0.9, 1.8)).label("按键", halign="right", fontsize=10)
        d += elm.Ground().at((x, 0.6))
        d += elm.Line().endpoints((x, 3.0), (x, 4.2)).linestyle(":").color(BAD)
        d += elm.Label().at((x, 4.6)).label("什么都没接", color=BAD, fontsize=10)
        _pin(d, x, 3.0)
        d += elm.Label().at((x + 1.2, -0.9)).label("(a) 悬空：松开时电平不确定")
        # (b) 上拉
        x = 6.0
        d += elm.Vdd().at((x, 5.6)).label("5 V")
        d += elm.Resistor().endpoints((x, 5.6), (x, 3.0)).color(EMPH)
        d += elm.Label().at((x - 0.45, 4.3)).label("上拉电阻\n10 kΩ", halign="right", color=EMPH, fontsize=10)
        d += elm.Dot().at((x, 3.0))
        d += elm.Button().endpoints((x, 3.0), (x, 0.6))
        d += elm.Label().at((x - 0.9, 1.8)).label("按键", halign="right", fontsize=10)
        d += elm.Ground().at((x, 0.6))
        _pin(d, x, 3.0)
        d += elm.Label().at((x + 1.2, -0.9)).label("(b) 上拉：松开为 1，按下为 0")
        # (c) 下拉
        x = 12.0
        d += elm.Vdd().at((x, 5.6)).label("5 V")
        d += elm.Button().endpoints((x, 5.6), (x, 3.0))
        d += elm.Label().at((x - 0.9, 4.3)).label("按键", halign="right", fontsize=10)
        d += elm.Dot().at((x, 3.0))
        d += elm.Resistor().endpoints((x, 3.0), (x, 0.6)).color(EMPH)
        d += elm.Label().at((x - 0.45, 1.8)).label("下拉电阻\n10 kΩ", halign="right", color=EMPH, fontsize=10)
        d += elm.Ground().at((x, 0.6))
        _pin(d, x, 3.0)
        d += elm.Label().at((x + 1.2, -0.9)).label("(c) 下拉：松开为 0，按下为 1")
    save_schem(d, N, "26_p1_4_pull_up_down.png")


def fig_p2_4():
    """图 26-p2-4：推导一的电路：V_CC 经上拉电阻 R 到引脚，按键从引脚接地；松手时只有漏电流，按下时电流 V_CC/R。"""
    with drawing(fontsize=11) as d:
        d += elm.Vdd().at((0, 6.0)).label("$V_{CC}$ = 5 V")
        d += elm.Resistor().endpoints((0, 6.0), (0, 3.0)).color(EMPH)
        d += elm.Label().at((-0.45, 4.5)).label("$R$\n10 kΩ", halign="right", color=EMPH)
        d += elm.Dot().at((0, 3.0))
        d += elm.Button().endpoints((0, 3.0), (0, 0.4))
        d += elm.Label().at((-0.9, 1.7)).label("按键", halign="right", fontsize=10)
        d += elm.Ground().at((0, 0.4))
        d += elm.Line().endpoints((0, 3.0), (3.0, 3.0))
        d += elm.Label().at((1.5, 3.45)).label("$I_{leak}$ ≤ 1 μA →", fontsize=10)
        d += elm.Label().at((1.5, 2.55)).label("$V_{pin}$", fontsize=10)
        d += elm.Dot(open=True).at((3.0, 3.0)).label("单片机\n输入引脚", "right")
        d += elm.Label().at((0.9, 1.5)).label("按下时：$I = V_{CC}/R$ = 0.5 mA ↓", halign="left", color=EMPH, fontsize=10)
    save_schem(d, N, "26_p2_4_pullup_calc.png")


def _od(d, x0, vtxt, rtxt, ctxt, drv, rx, rcol="black"):
    """开漏总线一根线：电源经上拉 R_p 到线，线对地有电容 C_b，开漏输出管（这里画成开关）把线拉低，右边是接收方。"""
    y = 3.0
    d += elm.Vdd().at((x0 + 2.0, 6.0)).label(vtxt)
    d += elm.Resistor().endpoints((x0 + 2.0, 6.0), (x0 + 2.0, y)).color(rcol)
    d += elm.Label().at((x0 + 1.55, 4.5)).label(rtxt, halign="right", color=rcol, fontsize=10)
    d += elm.Line().endpoints((x0, y), (x0 + 6.5, y))
    for xx in (x0, x0 + 2.0, x0 + 4.0):
        d += elm.Dot().at((xx, y))
    d += elm.Switch().endpoints((x0, y), (x0, 0.6))
    d += elm.Ground().at((x0, 0.6))
    d += elm.Label().at((x0 - 1.0, 1.8)).label(drv, halign="right", fontsize=10)
    d += elm.Capacitor().endpoints((x0 + 4.0, y), (x0 + 4.0, 0.6)).linestyle("--")
    d += elm.Ground().at((x0 + 4.0, 0.6))
    d += elm.Label().at((x0 + 4.45, 1.8)).label(ctxt, halign="left", fontsize=10)
    d += elm.Dot(open=True).at((x0 + 6.5, y)).label(rx, "right")


def fig_p2_5():
    """图 26-p2-5：推导二的电路：开漏输出 + 上拉 R_p + 线电容 C_b。"""
    with drawing(fontsize=11) as d:
        _od(d, 0, "$V_{CC}$", "上拉电阻\n$R_p$", "线电容 $C_b$\n（导线 + 引脚，\n虚线表示不是\n真的元件）",
            "开漏输出管\n（只会拉低或松手，\n拉低时吸收 $I_{OL}$）", "接收方输入", rcol=EMPH)
    save_schem(d, N, "26_p2_5_open_drain.png")


def _ls_model(d, x0, swap, title):
    """仿真二的模型：BSS138 电平转换，两边各 10 kΩ 上拉、50 pF 线电容、开漏输出（导通电阻 100 Ω）。swap=True：源漏接反。"""
    y = 3.0
    q = elm.NFet().theta(-90).reverse().anchor("source").at((x0 + 4.0, y))
    d += q
    left, right = q.source, q.drain
    yd = y - 1.3
    dcol = BAD if swap else "#8c8c8c"
    d += elm.Line().endpoints(left, (left[0], yd)).color(dcol if swap else "black")
    d += elm.Line().endpoints(right, (right[0], yd)).color(dcol if swap else "black")
    if swap:   # 源极在 5 V 侧：体二极管正极在右（5 V 侧）、负极在左（3.3 V 侧）
        d += elm.Diode().endpoints((right[0], yd), (left[0], yd)).color(BAD)
        d += elm.Label().at(((left[0] + right[0]) / 2, yd - 0.95)).label("体二极管把 5 V 侧送进 3.3 V 侧", color=BAD, fontsize=9)
    else:
        d += elm.Diode().endpoints((left[0], yd), (right[0], yd)).color(dcol)
        d += elm.Label().at(((left[0] + right[0]) / 2, yd - 0.95)).label("体二极管", color=dcol, fontsize=10)
    d += elm.Dot().at(left); d += elm.Dot().at(right)
    sl, sr = ("D", "S") if swap else ("S", "D")
    d += elm.Label().at((left[0] - 0.15, y + 0.35)).label(sl, halign="right", color=BAD if swap else "black")
    d += elm.Label().at((right[0] + 0.15, y + 0.35)).label(sr, halign="left", color=BAD if swap else "black")
    d += elm.Label().at((q.gate[0] - 0.3, q.gate[1] + 0.5)).label("Q1 BSS138", halign="right", fontsize=10)
    # 栅极接 3.3 V
    yt = y + 2.8
    d += elm.Line().endpoints(q.gate, (q.gate[0], yt))
    d += elm.Line().endpoints((x0 + 2.0, yt), (q.gate[0], yt))
    d += elm.Dot().at((x0 + 2.0, yt))
    d += elm.Vdd().at((x0 + 2.0, yt)).label("3.3 V")
    d += elm.Resistor().endpoints((x0 + 2.0, yt), (x0 + 2.0, y))
    d += elm.Label().at((x0 + 1.6, y + 1.4)).label("10 kΩ", halign="right", fontsize=10)
    d += elm.Vdd().at((x0 + 7.0, yt)).label("5 V")
    d += elm.Resistor().endpoints((x0 + 7.0, yt), (x0 + 7.0, y))
    d += elm.Label().at((x0 + 7.4, y + 1.4)).label("10 kΩ", halign="left", fontsize=10)
    d += elm.Line().endpoints((x0 - 1.6, y), left)
    d += elm.Line().endpoints(right, (x0 + 10.6, y))
    for xx in (x0 - 1.6, x0 + 0.0, x0 + 2.0, x0 + 7.0, x0 + 9.0, x0 + 10.6):
        d += elm.Dot().at((xx, y))
    d += elm.Label().at((x0 + 1.0, y + 0.35)).label("$V_L$", fontsize=10)
    d += elm.Label().at((x0 + 8.0, y + 0.35)).label("$V_H$", fontsize=10)
    for xx, side in ((x0 - 1.6, "l"), (x0 + 10.6, "r")):   # 开漏输出：100 Ω + 开关
        d += elm.Resistor().endpoints((xx, y), (xx, y - 1.6))
        d += elm.Switch().endpoints((xx, y - 1.6), (xx, y - 3.2))
        d += elm.Ground().at((xx, y - 3.2))
        lab = "开漏输出\n100 Ω + 开关" + ("\n（3.3 V 侧器件）" if side == "l" else "\n（5 V 侧器件）")
        d += elm.Label().at((xx + (-0.9 if side == "l" else 0.9), y - 1.6)).label(lab, halign="right" if side == "l" else "left", fontsize=9)
    for xx in (x0 + 0.0, x0 + 9.0):
        d += elm.Capacitor().endpoints((xx, y), (xx, y - 2.2)).linestyle("--")
        d += elm.Ground().at((xx, y - 2.2))
        d += elm.Label().at((xx + 0.4, y - 1.1)).label("50 pF", halign="left", fontsize=9)
    d += elm.Label().at((x0 + 4.5, y - 4.4)).label(title, color=BAD if swap else "black")


def fig_p2_6():
    """图 26-p2-6：仿真二的模型电路：(a) 正确接法；(b) 源极、漏极接反。"""
    with drawing(fontsize=11) as d:
        _ls_model(d, 0, False, "(a) 正确接法：源极接 3.3 V 侧，漏极接 5 V 侧")
        _ls_model(d, 19.0, True, "(b) 接反：源极到了 5 V 侧")
    save_schem(d, N, "26_p2_6_shifter_model.png")


def fig_p2_7():
    """图 26-p2-7：例 3：两只比较器的开漏输出共用 4.7 kΩ 上拉（线与）；其中一只换成推挽输出时的短路路径。"""
    with drawing(fontsize=11) as d:
        for x0, push in ((0.0, False), (11.0, True)):
            y = 3.0
            d += elm.Vdd().at((x0 + 2.0, 6.0)).label("5 V")
            d += elm.Resistor().endpoints((x0 + 2.0, 6.0), (x0 + 2.0, y))
            d += elm.Label().at((x0 + 1.55, 4.5)).label("4.7 kΩ", halign="right", fontsize=10)
            d += elm.Line().endpoints((x0, y), (x0 + (5.2 if push else 6.0), y)).color(BAD if push else "black")
            for xx in (x0, x0 + 2.0, x0 + 4.0):
                d += elm.Dot().at((xx, y))
            # 比较器 1：开漏，拉低
            c1 = BAD if push else "black"
            d += elm.Switch(action="close").endpoints((x0, y), (x0, 0.6)).color(c1)
            d += elm.Ground().at((x0, 0.6))
            d += elm.Label().at((x0 - 1.0, 1.8)).label("比较器 1\n开漏输出\n（正在拉低）", halign="right", color=c1, fontsize=10)
            if not push:
                d += elm.Switch().endpoints((x0 + 4.0, y), (x0 + 4.0, 0.6))
                d += elm.Ground().at((x0 + 4.0, 0.6))
                d += elm.Label().at((x0 + 4.9, 1.8)).label("比较器 2\n开漏输出", halign="left", fontsize=10)
                d += elm.Dot(open=True).at((x0 + 6.0, y)).label("线与输出", "right")
                d += elm.Label().at((x0 + 2.5, -0.9)).label("(a) 两只开漏输出：任一只拉低，线就为低")
            else:
                xp = x0 + 4.0
                d += elm.Line().endpoints((xp, y), (xp + 1.2, y)).color(BAD)
                d += elm.Vdd().at((xp + 1.2, 6.0)).label("5 V")
                d += elm.Switch(action="close").endpoints((xp + 1.2, 6.0), (xp + 1.2, y)).color(BAD)
                d += elm.Switch().endpoints((xp + 1.2, y), (xp + 1.2, 0.6)).color(OFF if "OFF" in globals() else "#8c8c8c")
                d += elm.Ground().at((xp + 1.2, 0.6))
                d += elm.Dot().at((xp + 1.2, y))
                d += elm.Label().at((xp + 2.1, 4.5)).label("比较器 2 换成推挽输出\n上管导通，输出 5 V", halign="left", color=BAD, fontsize=10)
                d += elm.Label().at((x0 + 2.5, -0.9)).label("(b) 推挽输出高、另一只拉低：5 V 直接短到地", color=BAD)
    save_schem(d, N, "26_p2_7_wired_and.png")


def fig_p3_3():
    """图 26-p3-3：扫描一的电路：3.3 V I²C 时钟线 SCL，上拉 R_p 取 1.5 / 4.7 / 10 kΩ，总线电容 200 pF。"""
    with drawing(fontsize=11) as d:
        _od(d, 0, "3.3 V", "上拉 $R_p$\n1.5 / 4.7 / 10 kΩ", "总线电容 $C_b$\n200 pF",
            "主机开漏输出\n（400 kHz 时钟）", "SCL（接各从机）", rcol=EMPH)
    save_schem(d, N, "26_p3_3_scl_rp.png")


def fig_p3_4():
    """图 26-p3-4：扫描二的电路：R1 = R2 = R、C = 1 μF；电容电压同时送施密特输入和单门限输入。"""
    with drawing(fontsize=11) as d:
        d += elm.Vdd().at((0, 6)).label("+5 V")
        d += elm.Resistor().endpoints((0, 6), (0, 3.5)).color(EMPH)
        d += elm.Label().at((-0.45, 4.75)).label("R1 = R\n100 Ω～47 kΩ", halign="right", color=EMPH, fontsize=10)
        d += elm.Dot().at((0, 3.5)).label("A", loc="left", ofst=0.15)
        d += elm.Button().endpoints((0, 3.5), (0, 1.0))
        d += elm.Label().at((-0.9, 2.25)).label("按键", halign="right", fontsize=10)
        d += elm.Ground().at((0, 1.0))
        d += elm.Resistor().endpoints((0, 3.5), (3.5, 3.5)).color(EMPH).label("R2 = R", loc="top", color=EMPH)
        d += elm.Dot().at((3.5, 3.5)).label("B", loc="top", ofst=0.15)
        d += elm.Capacitor().endpoints((3.5, 3.5), (3.5, 1.0)).label("C\n1 μF", loc="bottom")
        d += elm.Ground().at((3.5, 1.0))
        d += elm.Line().endpoints((3.5, 3.5), (5.0, 3.5))
        d += elm.Line().endpoints((4.5, 3.5), (4.5, 5.5)).color(BAD)
        d += elm.Dot().at((4.5, 3.5))
        d += elm.Line().endpoints((4.5, 5.5), (5.0, 5.5)).color(BAD)
        g = logic.SchmittNot().anchor("in1").at((5.0, 3.5))
        d += g
        d += elm.Label().at((g.out[0] + 0.6, 3.5)).label("74HC14 施密特输入\n（回差 1.73 V / 2.77 V）", halign="left", fontsize=10)
        g2 = logic.Not().anchor("in1").at((5.0, 5.5)).color(BAD)
        d += g2
        d += elm.Label().at((g2.out[0] + 0.6, 5.5)).label("对照：单门限 2.5 V 的普通输入\n（线上叠加 20 mV 噪声）", halign="left", color=BAD, fontsize=10)
    save_schem(d, N, "26_p3_4_tau_sweep_circuit.png")


def fig_p3_5():
    """图 26-p3-5：练习 1：门磁开关一直闭合，10 kΩ 上拉接 3 V 电池。"""
    with drawing(fontsize=11) as d:
        d += elm.Vdd().at((0, 6.0)).label("3 V 电池")
        d += elm.Resistor().endpoints((0, 6.0), (0, 3.0)).color(EMPH)
        d += elm.Label().at((-0.45, 4.5)).label("上拉电阻\n10 kΩ（或 1 MΩ）", halign="right", color=EMPH, fontsize=10)
        d += elm.Dot().at((0, 3.0))
        d += elm.Switch(action="close").endpoints((0, 3.0), (0, 0.6))
        d += elm.Label().at((-1.0, 1.8)).label("门磁开关\n（门关着时闭合）", halign="right", fontsize=10)
        d += elm.Ground().at((0, 0.6))
        _pin(d, 0, 3.0)
        d += elm.Label().at((0.4, 4.5)).label("电流 ↓", halign="left", color=EMPH, fontsize=10)
    save_schem(d, N, "26_p3_5_door_switch.png")


def fig_p3_6():
    """图 26-p3-6：练习 4：5 V 推挽输出经 10 kΩ / 20 kΩ 分压送 3.3 V 芯片输入（输入电容 10 pF）。"""
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 3.0)).label("5 V 芯片\n推挽输出", "left")
        d += elm.Resistor().endpoints((0, 3.0), (3.0, 3.0)).color(EMPH).label("10 kΩ", "top", color=EMPH)
        d += elm.Dot().at((3.0, 3.0))
        d += elm.Resistor().endpoints((3.0, 3.0), (3.0, 0.4)).color(EMPH)
        d += elm.Label().at((3.45, 1.7)).label("20 kΩ", halign="left", color=EMPH, fontsize=10)
        d += elm.Ground().at((3.0, 0.4))
        d += elm.Line().endpoints((3.0, 3.0), (6.5, 3.0))
        d += elm.Dot().at((5.2, 3.0))
        d += elm.Capacitor().endpoints((5.2, 3.0), (5.2, 0.4)).linestyle("--")
        d += elm.Label().at((5.65, 1.7)).label("输入电容\n10 pF", halign="left", fontsize=10)
        d += elm.Ground().at((5.2, 0.4))
        d += elm.Dot(open=True).at((6.5, 3.0)).label("3.3 V 芯片\n输入", "right")
    save_schem(d, N, "26_p3_6_divider.png")


if __name__ == "__main__":
    fig_p1_4(); fig_p2_4(); fig_p2_5(); fig_p2_6(); fig_p2_7(); fig_p3_3(); fig_p3_4(); fig_p3_5(); fig_p3_6()
