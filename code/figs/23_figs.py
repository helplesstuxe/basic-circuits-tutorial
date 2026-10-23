"""23 光耦隔离：除 23_sim.py 那两张以外的所有配图，以及例题、练习用到的数字。运行：python code/figs/23_figs.py
图上出现的每个数字都由本脚本打印（fs.mark 自动打印；其余用 print）。光耦模型与 code/23_sim.py 相同。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from schem import *
import figstyle as fs

P = "23"
V_F, VCC, VCE_SAT, C_EFF, TAU_FALL = 1.2, 5.0, 0.2, 1e-9, 2e-6   # 与 23_sim.py 相同（C_EFF、TAU_FALL 是示意值）


def v_out(i_f, ctr, r_l, vcc=VCC):
    """与 23_sim.py 相同：输出 = max(V_CE(sat), VCC − CTR·I_F·R_L)。"""
    return np.maximum(VCE_SAT, vcc - ctr * i_f * r_l)


def problem():
    """图 23-p1-1：直接连线（地线相连）与光耦隔离（地分开）的对比。"""
    fig, ax = fs.diagram(8.4, 3.6)
    ax.text(0.05, 3.25, "① 直接连线", fontsize=10, color=fs.C["bad"])
    a = fs.box(ax, 1.3, 2.5, "强电侧\n电机、继电器、220 V 检测", w=2.2, h=0.8)
    b = fs.box(ax, 7.0, 2.5, "单片机\n（5 V）", w=1.6, h=0.8)
    fs.arrow(ax, (a["r"][0], 2.7), (b["l"][0], 2.7), "信号线")
    fs.arrow(ax, (a["r"][0], 2.3), (b["l"][0], 2.3), color=fs.C["bad"])
    ax.text(4.15, 2.05, "共用地线：干扰电流、故障高压顺着它窜过来", ha="center", va="top", fontsize=9, color=fs.C["bad"])
    ax.text(0.05, 1.35, "② 用光耦", fontsize=10, color=fs.C["good"])
    a2 = fs.box(ax, 1.3, 0.65, "强电侧", w=2.2, h=0.7)
    o1 = fs.box(ax, 3.35, 0.65, "LED", w=1.0, h=0.7)
    o2 = fs.box(ax, 4.95, 0.65, "光敏\n三极管", w=1.0, h=0.7)
    fs.arrow(ax, o1["r"], o2["l"], "光")
    b2 = fs.box(ax, 7.0, 0.65, "单片机", w=1.6, h=0.7)
    fs.arrow(ax, a2["r"], o1["l"], "电流")
    fs.arrow(ax, o2["r"], b2["l"], "电流")
    ax.add_patch(plt.Rectangle((2.7, 0.15), 2.9, 1.15, fill=False, ec=fs.C["edge"], lw=1.0, ls=":"))
    ax.text(4.15, 1.38, "光耦（一个封装）", ha="center", fontsize=9)
    ax.plot([4.15, 4.15], [0.15, 1.05], color=fs.C["ref"], ls="--", lw=1.2)
    ax.text(4.15, 0.05, "隔离带：没有任何导线穿过", ha="center", va="top", fontsize=9, color=fs.C["ref"])
    ax.text(1.3, 0.15, "地：GND1", ha="center", va="top", fontsize=9)
    ax.text(7.0, 0.15, "地：GND2", ha="center", va="top", fontsize=9)
    ax.set_ylim(-0.4, 3.6)
    print("[图 23-p1-1] 220 V、5 V（只有文字）")
    fs.save(fig, P, "23_p1_1_problem.png")


def circuit(name, analysis=False):
    """图 23-p1-2 / 23-p2-1：完整的光耦输入电路（PC817 + 2.2 kΩ + 4.7 kΩ），中间画隔离带。"""
    with drawing(fontsize=11) as d:
        d += (oc := elm.Optocoupler().at((0, 0)))
        d += elm.Resistor().left().at(oc.anode).label("$R_{in}$ 2.2 kΩ", "top")
        d += elm.Line().left().length(0.6)
        d += (top_in := elm.Dot())
        d += elm.Line().down().at(oc.cathode).toy(-2.6)
        d += elm.Line().left().tox(top_in.center[0])
        d += (bot := elm.Dot())
        d += elm.SourceV().up().at(bot.center).toy(0).label("12 V\n信号", "top")
        d += elm.Ground().at(bot.center)
        d += elm.Label().at((bot.center[0] + 0.9, -3.4)).label("GND1")
        d += elm.Line().right().at(oc.collector).length(1.0)
        d += (j := elm.Dot())
        d += elm.Resistor().up().label("$R_L$ 4.7 kΩ", "bottom")
        d += elm.Vdd().label("+5 V")
        d += elm.Line().right().at(j.center).length(1.4)
        d += elm.Dot(open=True).label("$V_{out}$ → 单片机引脚" if analysis else "输出 → 单片机引脚", "right")
        d += elm.Line().down().at(oc.emitter).toy(-2.6)
        d += (g2 := elm.Ground())
        d += elm.Label().at((oc.emitter[0] + 0.9, -3.4)).label("GND2")
        barrier(d, 0.75, -3.6, 1.6)
        d += elm.Label().at((-2.3, 2.0)).label("输入侧（强电那边）", color=fs.C["bad"])
        d += elm.Label().at((3.4, 3.6)).label("输出侧（单片机这边）", color=fs.C["vin"])
        if analysis:
            d += elm.Label().at((-1.5, -1.0)).label("$I_F$ ↓\n$V_F$ ≈ 1.2 V")
            d += elm.Label().at((3.4, -1.3)).label("$I_C$ ↓\n最多 CTR × $I_F$")
    print("[图 %s] 12 V、2.2 kΩ、4.7 kΩ、+5 V%s" % (name, "、V_F ≈ 1.2 V" if analysis else ""))
    save_schem(d, P, name)


def timing():
    """图 23-p1-3：输入 12 V 方波 → LED 电流 → 输出（反相）。"""
    t = np.linspace(0, 3e-3, 3001)
    on = (t % 1e-3) < 0.5e-3
    vin = np.where(on, 12.0, 0.0)
    i_f = np.where(on, (12.0 - V_F) / 2200, 0.0)
    vo = v_out(i_f, 0.5, 4700)
    fig, axs = plt.subplots(3, 1, figsize=(7, 4.2), sharex=True)
    axs[0].plot(t * 1e3, vin, **fs.LS["vin"]); fs.axlabels(axs[0], None, None, "输入", "V"); axs[0].set_ylim(-1, 14)
    axs[1].plot(t * 1e3, i_f * 1e3, **fs.LS["cur"]); fs.axlabels(axs[1], None, None, "$I_F$", "mA"); axs[1].set_ylim(-0.5, 6.5)
    axs[2].plot(t * 1e3, vo, **fs.LS["vout"]); fs.axlabels(axs[2], "时间", "ms", "输出", "V"); axs[2].set_ylim(-0.5, 6)
    fs.mark(axs[1], 0.25, i_f[250] * 1e3, "{:.2f}", " mA", dx=6, dy=-14)
    fs.mark(axs[2], 0.25, vo[250], "{:.1f}", " V", dx=6, dy=4)
    fs.mark(axs[2], 0.75, vo[750], "{:.1f}", " V", dx=6, dy=-14)
    axs[2].text(1.03, 1.6, "输入高的时候输出低：反相", fontsize=9)
    print("[图 23-p1-3] 12 V；CTR 按 50%")
    fs.save(fig, P, "23_p1_3_timing.png")


def tradeoff():
    """图 23-p3-1：上拉电阻 R_L 的取舍——越大越省电流，但上升沿越慢。"""
    rl = np.logspace(np.log10(470), np.log10(47e3), 200)
    t_r = 2.2 * rl * C_EFF * 1e6
    i_f = (VCC - VCE_SAT) / rl / 0.25 * 1e3          # 按老化后 CTR 25% 要饱和所需的 I_F
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.loglog(rl / 1e3, t_r, **fs.LS["vout"], label="上升时间（左轴）")
    ax2 = ax.twinx()
    ax2.loglog(rl / 1e3, i_f, **fs.LS["vin"], label="所需 $I_F$，CTR 按 25%（右轴）")
    for r in (1.0, 4.7, 47.0):
        dxr = -52 if r > 10 else 8
        fs.mark(ax, r, 2.2 * r * 1e3 * C_EFF * 1e6, "{:.1f}", " μs", dx=dxr, dy=-16)
        fs.mark(ax2, r, 4.8 / r / 0.25, "{:.2f}", " mA", dx=dxr, dy=8)
    fs.axlabels(ax, "上拉电阻 $R_L$", "kΩ", "上升时间", "μs")
    ax2.set_ylabel("所需 $I_F$ / mA")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper center", fontsize=8)
    ax.set_ylim(0.5, 1000); ax2.set_ylim(0.05, 100)
    from matplotlib.ticker import FuncFormatter
    fmt = FuncFormatter(lambda v, _: f"{v:g}")
    for a in (ax, ax2):
        a.yaxis.set_major_formatter(fmt)
    ax.xaxis.set_major_formatter(fmt)
    assert 2.2 * 47e3 * C_EFF > 1e-4 and 4.8 / 1.0 / 0.25 > 15
    fs.save(fig, P, "23_p3_1_tradeoff.png")


def zero_cross():
    """图 23-p3-2：AC 输入光耦检测市电过零（原理示意，不是可照抄的电路）。"""
    vp, r_in, r_l, ctr = 220 * np.sqrt(2), 100e3, 10e3, 0.5
    t = np.linspace(0, 0.04, 8001)
    v = vp * np.sin(2 * np.pi * 50 * t)
    i_f = np.maximum(np.abs(v) - V_F, 0) / r_in       # 两只反并联 LED：正负半周都有电流
    vo = v_out(i_f, ctr, r_l)
    v_th = (VCC - 3.0) / r_l / ctr * r_in + V_F         # 输出高于 3.0 V 时市电的绝对值
    width = 2 * np.arcsin(v_th / vp) / (2 * np.pi * 50)
    p_r = 220 ** 2 / r_in
    print(f"[过零] 峰值 {vp:.0f} V；|v| < {v_th:.0f} V 时输出高于 3.0 V；每个过零脉冲宽约 {width*1e3:.2f} ms；每秒 100 个")
    print(f"[过零] 输入电阻 100 kΩ 上的功耗约 {p_r:.2f} W（示意）")
    assert 0.5e-3 < width < 1.2e-3
    fig, axs = plt.subplots(2, 1, figsize=(7, 3.6), sharex=True)
    axs[0].plot(t * 1e3, v, **fs.LS["vin"], label="市电（示意）")
    axs[0].axhspan(-v_th, v_th, color=fs.C["ref"], alpha=0.25)
    fs.axlabels(axs[0], None, None, "市电", "V"); axs[0].set_ylim(-380, 480)
    axs[0].text(10.3, 60, f"±{v_th:.0f} V", fontsize=9)
    axs[1].plot(t * 1e3, vo, **fs.LS["vout"], label="光耦输出")
    fs.ref_h(axs[1], 3.0, "3.0 V", x=0.53, ha="left")
    fs.axlabels(axs[1], "时间", "ms", "输出", "V"); axs[1].set_ylim(-0.5, 6)
    for a in axs: a.legend(loc="upper left", bbox_to_anchor=(0.3, 1.0), fontsize=8)
    fs.save(fig, P, "23_p3_2_zerocross.png")


def examples():
    """page2 例题、page3 练习、动手实验用到的数字。"""
    def need_if(vcc, rl, ctr):                         # 要饱和所需的 I_F
        return (vcc - VCE_SAT) / rl / ctr
    # 例 1：24 V 信号、5 V 单片机、R_L 10 kΩ、PC817 最小 50% → 设计值 25%
    i1 = need_if(5, 10e3, 0.25); r1 = (24 - V_F) / 3e-3; i1r = (24 - V_F) / 6800
    print(f"[例 1] 要 I_C ≥ {(5-VCE_SAT)/10e3*1e3:.2f} mA → I_F ≥ {i1*1e3:.2f} mA；按 3 mA 算 R_in = {r1/1e3:.2f} kΩ，取 6.8 kΩ → I_F = {i1r*1e3:.2f} mA，电阻功耗 {i1r**2*6800*1e3:.0f} mW")
    # 例 2：12 V、R_L 4.7 kΩ、设计值 25%
    i2 = need_if(5, 4.7e3, 0.25); r2 = (12 - V_F) / i2
    print(f"[例 2] I_F ≥ {i2*1e3:.2f} mA → R_in ≤ {r2/1e3:.2f} kΩ，取 2.2 kΩ → I_F = {(12-V_F)/2200*1e3:.2f} mA")
    # 例 3：3.3 V 单片机、5 V 信号、R_L 4.7 kΩ、某型号最小 CTR 80% → 设计值 40%
    i3 = need_if(3.3, 4.7e3, 0.40); r3 = (5 - V_F) / i3
    print(f"[例 3] V_IL = {0.3*3.3:.2f} V；I_C ≥ {(3.3-VCE_SAT)/4.7e3*1e3:.2f} mA → I_F ≥ {i3*1e3:.2f} mA → R_in ≤ {r3/1e3:.2f} kΩ，取 1.5 kΩ → I_F = {(5-V_F)/1500*1e3:.2f} mA")
    # 练习 1：I_F 5 mA、CTR 设计值 25% → 最小 R_L
    print(f"[练习 1] I_C = {5*0.25:.2f} mA → R_L ≥ {(5-VCE_SAT)/1.25e-3/1e3:.2f} kΩ")
    # 练习 2：10 kΩ 上拉的上升时间与串口位宽
    for baud in (9600, 115200):
        print(f"[练习 2] {baud} 波特：每位 {1e6/baud:.1f} μs；10 kΩ 上升时间 {2.2*10e3*C_EFF*1e6:.0f} μs，占一位的 {2.2*10e3*C_EFF*baud*100:.0f}%")
    # 练习 3：LED 电流太大
    print(f"[练习 3] 12 V 配 470 Ω：I_F = {(12-V_F)/470*1e3:.1f} mA，电阻功耗 {((12-V_F)/470)**2*470*1e3:.0f} mW")
    # 动手实验：9 V 电池当"外部信号"，5 V 当输出侧
    i_lab = (9 - V_F) / 2200
    print(f"[实验] 9 V 配 2.2 kΩ：I_F = {i_lab*1e3:.2f} mA；CTR 50% 时 I_C 最多 {i_lab*0.5*1e3:.2f} mA，4.7 kΩ 只要 1.02 mA → 输出约 0.2 V")
    print(f"[实验] 9 V 配 22 kΩ：I_F = {(9-V_F)/22e3*1e3:.2f} mA；CTR 50% 时输出 {float(v_out((9-V_F)/22e3, 0.5, 4700)):.2f} V，CTR 200% 时 {float(v_out((9-V_F)/22e3, 2.0, 4700)):.2f} V")


if __name__ == "__main__":
    problem()
    circuit("23_p1_2_circuit.png")
    timing()
    circuit("23_p2_1_analysis.png", analysis=True)
    tradeoff()
    zero_cross()
    examples()
