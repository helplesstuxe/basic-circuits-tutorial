"""23 光耦隔离：除 23_sim.py 那两张以外的所有配图，以及例题、练习用到的数字。运行：python code/figs/23_figs.py
图上出现的每个数字都由本脚本打印（fs.mark 自动打印；其余用 print）。光耦模型与 code/23_sim.py 相同。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from schem import *
import figstyle as fs

P = "23"
V_F, VCC, VCE_SAT = 1.2, 5.0, 0.2                 # 与 23_sim.py 相同
TAU_B, C_EQ = 8e-6, 3.3e-9                         # 与 23_sim.py B 部分相同：按 PC817 SPICE 结果标定的基区电荷时间常数、输出端等效电容
CTR_B, I_F_B = 0.5, (12 - V_F) / 2.2e3             # 速度计算的条件：CTR 50%、12 V 配 2.2 kΩ（与 SPICE 核对时相同）
SPICE_TR = {2.2e3: 25.8, 4.7e3: 46.9, 10e3: 83.5}  # PC817 SPICE 模型的 10%→90% 上升时间 / μs（review/spice/23.md；2.2 kΩ 为第 7 轮用 spice/23/rise.cir 补跑）


def v_out(i_f, ctr, r_l, vcc=VCC):
    """与 23_sim.py 相同：输出 = max(V_CE(sat), VCC − CTR·I_F·R_L)。"""
    return np.maximum(VCE_SAT, vcc - ctr * i_f * r_l)


def edge_rise(r_l, t_on=150e-6, t_off=2e-3, dt=0.1e-6):
    """标定模型（与 23_sim.py B 部分相同）：LED 先亮 t_on 让电路稳定，再熄灭；r_l 可以是数组，一次算多个上拉电阻。
    返回 (亮时的低电平, 熄灭后升到 3.0 V 的时间, 10%→90% 上升时间)，单位 V、s、s。"""
    r_l = np.atleast_1d(np.asarray(r_l, dtype=float))
    v, i_c, a = np.full_like(r_l, VCC), np.zeros_like(r_l), np.exp(-dt / TAU_B)
    n_on, n_off = int(round(t_on / dt)), int(round(t_off / dt))
    for k in range(n_on):                                   # LED 亮：电流慢慢升到 CTR·I_F，输出被拉低
        i_c = CTR_B * I_F_B + (i_c - CTR_B * I_F_B) * a
        v = np.clip(v + ((VCC - v) / r_l - i_c) / C_EQ * dt, VCE_SAT, VCC)
    v_low = v.copy()
    lv10, lv90 = v_low + 0.1 * (VCC - v_low), v_low + 0.9 * (VCC - v_low)
    t3, t10, t90 = (np.full_like(r_l, np.nan) for _ in range(3))
    for k in range(1, n_off + 1):                           # LED 灭：电流慢慢减到 0，上拉经 R_L 给 C_EQ 充电
        i_c = i_c * a
        v = np.clip(v + ((VCC - v) / r_l - i_c) / C_EQ * dt, VCE_SAT, VCC)
        for arr, lv in ((t3, 3.0), (t10, lv10), (t90, lv90)):
            hit = np.isnan(arr) & (v >= lv)
            arr[hit] = k * dt
    return v_low, t3, t90 - t10


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
    """图 23-p3-1：上拉电阻 R_L 的取舍——越大越省电流，但上升沿越慢（上升时间用 SPICE 标定的模型）。"""
    rl = np.logspace(np.log10(1e3), np.log10(47e3), 60)
    _, _, tr = edge_rise(rl)
    t_r = tr * 1e6
    i_f = (VCC - VCE_SAT) / rl / 0.25 * 1e3          # 按老化后 CTR 25% 要饱和所需的 I_F
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.loglog(rl / 1e3, t_r, **fs.LS["vout"], label="上升时间：标定模型（左轴）")
    ax.loglog([r / 1e3 for r in SPICE_TR], list(SPICE_TR.values()), ls="none", marker="s", ms=5, mfc="none",
              color=fs.C["vout"], label="上升时间：PC817 SPICE（左轴）")
    ax2 = ax.twinx()
    ax2.loglog(rl / 1e3, i_f, **fs.LS["vin"], label="所需 $I_F$，CTR 按 25%（右轴）")
    v_low, _, tr_m = edge_rise([2.2e3, 4.7e3, 10e3, 47e3])
    for r, trm, (dxr, dyr) in zip((2.2, 4.7, 10.0, 47.0), tr_m, ((-40, 6), (-40, 6), (8, -14), (-52, 6))):
        fs.mark(ax, r, trm * 1e6, "{:.1f}", " μs", dx=dxr, dy=dyr)
    for r, (dxr, dyr) in zip((1.0, 4.7, 47.0), ((8, 4), (8, 4), (-52, -14))):
        fs.mark(ax2, r, 4.8 / r / 0.25, "{:.2f}", " mA", dx=dxr, dy=dyr)
    for r, ts in SPICE_TR.items():
        print(f"[图 23-p3-1] R_L = {r/1e3:g} kΩ：模型上升时间 {float(edge_rise(r)[2][0])*1e6:.1f} μs，SPICE {ts} μs")
    fs.axlabels(ax, "上拉电阻 $R_L$", "kΩ", "上升时间", "μs")
    ax2.set_ylabel("所需 $I_F$ / mA")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper center", fontsize=7.5)
    ax.set_ylim(5, 20000); ax2.set_ylim(0.05, 300)
    from matplotlib.ticker import FuncFormatter
    fmt = FuncFormatter(lambda v, _: f"{v:g}")
    for a in (ax, ax2):
        a.yaxis.set_major_formatter(fmt)
    ax.xaxis.set_major_formatter(fmt)
    for r, ts in SPICE_TR.items():                    # 标定模型与 SPICE 的上升时间相差在 15% 以内
        assert abs(float(edge_rise(r)[2][0]) * 1e6 / ts - 1) < 0.15
    assert tr_m[-1] > 1e-4 and 4.8 / 1.0 / 0.25 > 15
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
    # ---- 示意值的推理（H11AA1、Yageo CFR 手册数字），不是可照抄的设计 ----
    i_pk = vp / r_in                                    # LED 峰值电流
    print(f"[过零] LED 峰值电流 {i_pk*1e3:.2f} mA，远小于 H11AA1 的 ±40 mA；LED 功耗按有效值估算约 {i_pk/np.sqrt(2)*V_F*1e3:.1f} mW（上限 120 mW）")
    assert abs(i_pk - 3.11e-3) < 0.01e-3 and i_pk < 40e-3 and i_pk / np.sqrt(2) * V_F < 0.120
    print(f"[过零] 市电峰值 {vp:.0f} V < H11AA1 VIORM 850 V（峰值），隔离耐压 VISO 5000 V（有效值，1 分钟）")
    assert vp < 850
    rcwv = lambda p_w, r, vmax: min(np.sqrt(p_w * r), vmax)   # Yageo CFR：额定连续工作电压 = √(P·R) 与最高工作电压取小
    for name, p_w, vmax in (("CFR-25 1/4 W", 0.25, 250), ("CFR-50 1/2 W", 0.5, 350), ("CFR-100 1 W", 1.0, 500)):
        print(f"[过零] 单只 100 kΩ 用 {name}：允许 {rcwv(p_w, r_in, vmax):.0f} V，实际 220 V，功耗 {p_r:.2f} W / 额定 {p_w} W")
    assert rcwv(0.25, r_in, 250) < 220 < rcwv(0.5, r_in, 350) < 230 and rcwv(1.0, r_in, 500) > 300
    half_v, half_p = 220 / 2, 110 ** 2 / 50e3           # 拆成两只 50 kΩ 串联
    print(f"[过零] 两只 50 kΩ 串联：每只 {half_v:.0f} V、{half_p:.3f} W；用 1/2 W 时每只允许 {rcwv(0.5, 50e3, 350):.0f} V")
    assert abs(p_r - 0.484) < 0.001 and abs(half_p - 0.242) < 0.001 and rcwv(0.5, 50e3, 350) > half_v
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
    tr10 = float(edge_rise(10e3)[2][0])                # 标定模型；SPICE 是 83.5 μs
    for baud in (9600, 115200):
        print(f"[练习 2] {baud} 波特：每位 {1e6/baud:.1f} μs；10 kΩ 上升时间 模型 {tr10*1e6:.0f} μs、SPICE {SPICE_TR[10e3]:.1f} μs，"
              f"分别占一位的 {tr10*baud*100:.0f}%、{SPICE_TR[10e3]*1e-6*baud*100:.0f}%")
    assert 0.7 < SPICE_TR[10e3] * 1e-6 * 9600 < 0.9    # 9600 波特下上升时间占一位的八成左右
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


# ======================= page4 动手实验篇 =======================
# 面包板俯视图小工具（各节点脚本各带一份，互不依赖）。
# 坐标：列号 1…ncol 从左到右；上半区 a–e、下半区 f–j（同一列的 a–e 五个孔互相连通，f–j 也连通）；
# 上下各有两条电源轨：靠外的一条标「+」，靠里的一条标「−」，整条横向连通。
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

BB_Y = {r: 5.6 - i for i, r in enumerate("abcde")}
BB_Y.update({r: -1.4 - i for i, r in enumerate("fghij")})
BB_Y.update({"T+": 8.6, "T-": 7.7, "B-": -6.7, "B+": -7.6})
WIRE = dict(pos=(fs.C["bad"], "正电源"), gnd=("#000000", "地（0 V）"), neg=(fs.C["third"], "负电源"),
            sig=(fs.C["vin"], "输入信号"), out=(fs.C["vout"], "输出"), fb=(fs.C["fb"], "反馈 / 其他连线"))


class Breadboard:
    def __init__(self, ncol=30, title=None, size=(10, 6.4), rails=("+", "−", "−", "+")):
        self.ncol, self.used = ncol, set()
        self.fig, self.ax = plt.subplots(figsize=size)
        ax = self.ax
        ax.add_patch(FancyBboxPatch((0.2, -8.3), ncol + 0.6, 17.6, boxstyle="round,pad=0.1",
                                    fc="#f7f5ef", ec="0.55", lw=1.0))
        ax.add_patch(Rectangle((0.4, -0.55), ncol + 0.2, 0.7, fc="#e4e0d6", ec="none"))   # 中间凹槽
        for key, lab in zip(("T+", "T-", "B-", "B+"), rails):
            y = BB_Y[key]
            col = fs.C["bad"] if lab.startswith("+") else ("#000000" if lab in ("−", "GND", "0 V") else fs.C["third"])
            ax.plot([0.6, ncol + 0.4], [y + 0.42, y + 0.42], color=col, lw=1.0)
            ax.text(0.0, y, lab, ha="right", va="center", fontsize=10, color=col, fontweight="bold")
            for c in range(1, ncol + 1):
                if c % 6:
                    ax.add_patch(Circle((c, y), 0.12, fc="0.72", ec="none"))
        for r in "abcdefghij":
            y = BB_Y[r]
            ax.text(0.15, y, r, ha="right", va="center", fontsize=8, color="0.35")
            ax.text(ncol + 0.85, y, r, ha="left", va="center", fontsize=8, color="0.35")
            for c in range(1, ncol + 1):
                ax.add_patch(Circle((c, y), 0.12, fc="0.72", ec="none"))
        for c in range(1, ncol + 1):
            if c == 1 or c % 5 == 0:
                ax.text(c, 6.35, str(c), ha="center", va="bottom", fontsize=7.5, color="0.35")
                ax.text(c, -6.15, str(c), ha="center", va="top", fontsize=7.5, color="0.35")
        ax.set_xlim(-3.4, ncol + 4.8)
        ax.set_ylim(-11.2, 11.6)
        ax.set_aspect("equal")
        ax.axis("off")
        if title:
            ax.set_title(title, fontsize=11)

    def xy(self, h):
        """'e10' → 第 10 列 e 排；'T+3' / 'B-7' → 上（T）/ 下（B）电源轨第 3 / 7 列。"""
        if h[0] in "TB" and h[1] in "+-":
            return float(h[2:]), BB_Y[h[:2]]
        return float(h[1:]), BB_Y[h[0]]

    def _hole(self, p):
        x, y = self.xy(p) if isinstance(p, str) else p
        if isinstance(p, str):
            self.ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=4))
        return x, y

    def wire(self, a, b, kind="fb", via=None):
        """导线：a、b 为孔名或 (x, y)；via 为中间拐点列表。颜色按 kind 取（见 WIRE）。"""
        self.used.add(kind)
        pts = [self._hole(a)] + list(via or []) + [self._hole(b)]
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=WIRE[kind][0], lw=2.4, solid_capstyle="round", zorder=5)

    def part(self, a, b, label, kind="R", lab_side=1):
        """两脚元件：R 电阻、C 电容、E 电解电容（+ 脚在 a）、D 二极管（a 阳 b 阴）、L LED（a 阳）、
        S 按钮、P 小灯泡。画成方框简化符号，标签写在旁边。"""
        (x1, y1), (x2, y2) = self._hole(a), self._hole(b)
        ax = self.ax
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.plot([x1, x2], [y1, y2], color="0.35", lw=1.2, zorder=5)
        fc = dict(R="#d9c7a3", C="#f2d27a", E="#6d8fb5", D="#555555", L="#ffffff", S="#bbbbbb",
                  P="#fff7c2")[kind]
        horiz = abs(x2 - x1) >= abs(y2 - y1)
        w, h = (0.9, 0.5) if horiz else (0.5, 0.9)
        if kind in "LP":
            ax.add_patch(Circle((mx, my), 0.42, fc=fc, ec="0.2", lw=1.0, zorder=6))
        else:
            ax.add_patch(FancyBboxPatch((mx - w / 2, my - h / 2), w, h, boxstyle="round,pad=0.05",
                                        fc=fc, ec="0.2", lw=1.0, zorder=6))
        if kind in "EDL":
            ax.text(x1 + (0.25 if horiz else 0.25), y1 + (0.3 if horiz else 0), "+", fontsize=8,
                    ha="center", va="center", zorder=7, color=fs.C["bad"])
        if lab_side == "r":
            ax.text(max(x1, x2) + 0.3, my, label, ha="left", va="center", fontsize=8.5, zorder=7)
        elif horiz:
            ax.text(mx, my + 0.55 * lab_side, label, ha="center", va="bottom" if lab_side > 0 else "top",
                    fontsize=8.5, zorder=7)
        else:
            ax.text(mx + 0.45 * lab_side, my, label, ha="left" if lab_side > 0 else "right",
                    va="center", fontsize=8.5, zorder=7)

    def chip(self, col, label, npin=8, names=None):
        """DIP 芯片跨在中间凹槽上：第 1 脚在 f 排第 col 列（左下，缺口朝左），逆时针数，
        第 npin 脚在 e 排第 col 列。脚号和脚名写在芯片体上。"""
        half = npin // 2
        ax = self.ax
        y0, y1 = BB_Y["f"] + 0.22, BB_Y["e"] - 0.22
        ax.add_patch(Rectangle((col - 0.5, y0), half, y1 - y0, fc="#2b2b2b", ec="k", zorder=6))
        ax.add_patch(Circle((col - 0.5, (y0 + y1) / 2), 0.28, fc="#f7f5ef", ec="none", zorder=7))
        ax.text(col + (half - 1) / 2, (y0 + y1) / 2, label, color="w", ha="center",
                va="center", fontsize=9, zorder=8)
        for i in range(half):
            for p, row in ((i + 1, "f"), (npin - i, "e")):
                x, y = col + i, BB_Y[row]
                ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=7))
                txt = str(p) + ("\n" + names[p] if names and p in names else "")
                ax.text(x, y0 + 0.08 if row == "f" else y1 - 0.08, txt, ha="center",
                        va="bottom" if row == "f" else "top", fontsize=6, color="w", zorder=8,
                        linespacing=0.9)

    def sip(self, col, row, label, names, w_extra=0.0, fc="#2b2b2b", tc="w", up=True):
        """单排引脚元件（TO-220 / TO-92 三极管、电位器、SIP 模块等）：引脚从第 col 列起插在 row 排，
        names 是各脚名字列表；元件体画在引脚上方（up=True）或下方。"""
        ax, n = self.ax, len(names)
        x0, y = col, BB_Y[row]
        h = 1.25
        yb = y + 0.25 if up else y - 0.25 - h
        ax.add_patch(FancyBboxPatch((x0 - 0.45, yb), n - 1 + 0.9 + w_extra, h, boxstyle="round,pad=0.04",
                                    fc=fc, ec="k", lw=1.0, zorder=6))
        ax.text(x0 + (n - 1 + w_extra) / 2, yb + h * 0.66, label, color=tc, ha="center", va="center",
                fontsize=8, zorder=8)
        for i, nm in enumerate(names):
            ax.plot([x0 + i, x0 + i], [y, yb + (0 if up else h)], color="0.25", lw=1.4, zorder=5)
            ax.add_patch(Circle((x0 + i, y), 0.17, fc="0.15", ec="none", zorder=7))
            ax.text(x0 + i, yb + h * 0.2, nm, color=tc, ha="center", va="center", fontsize=6.5, zorder=8)

    def probe(self, h, text, dx=0.0, dy=0.0):
        """测量点：紫色圆圈 + 标签。"""
        x, y = self.xy(h)
        self.ax.add_patch(Circle((x, y), 0.36, fc="none", ec=fs.C["third"], lw=1.6, zorder=9))
        self.ax.text(x + dx, y + dy, text, color=fs.C["third"], fontsize=8, ha="center", va="center",
                     zorder=9, fontweight="bold")

    def module(self, x, y, w, h, label, fc="#e6f0f8"):
        """面包板外的模块（电池、信号源、继电器模块等），返回方框中心。"""
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec="0.3",
                                         lw=1.0, zorder=6))
        self.ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8.5, zorder=7)
        return x + w / 2, y + h / 2

    def note(self, x, y, text, **kw):
        self.ax.text(x, y, text, fontsize=8, zorder=8, **kw)

    def legend(self, loc="lower center"):
        from matplotlib.lines import Line2D
        cname = {fs.C["bad"]: "红", "#000000": "黑", fs.C["third"]: "紫", fs.C["vin"]: "蓝",
                 fs.C["vout"]: "橙", fs.C["fb"]: "绿", fs.C["cur"]: "天蓝"}
        def lab(c, t):                                # 图例写成「用途（色名）」；用途里已有括号时并进同一对括号
            return t[:-1] + f"，{cname[c]}）" if t.endswith("）") else f"{t}（{cname[c]}）"
        hs = [Line2D([], [], color=WIRE[k][0], lw=2.4, label=lab(*WIRE[k])) for k in WIRE if k in self.used]
        self.ax.legend(handles=hs, loc=loc, ncol=len(hs), fontsize=8.5, frameon=False,
                       bbox_to_anchor=(0.5, -0.01))

    def save(self, prefix, name):
        return fs.save(self.fig, prefix, name)

WIRE["gnd2"] = (fs.C["third"], "输入侧地（电池负极，不接 GND）")
WIRE["out"] = (fs.C["vout"], "输出（4 脚）")

# 动手实验的数值：ngspice + spice/models/PC817_ltspice.lib（Igain 按 CTR 50% / 200% 标定，见 spice/23/results.json）
# + LTspice 红色 LED 模型 TLSV5100RED；临时网表照 spice/23/rise.cir 改出（输入侧串红色指示 LED），不改 spice/ 下的文件。
P4_DC = dict(i_f=6.01e-3, v_rin=6.01, v_ind=1.92, v_ir=1.07)          # 9 V、R_in 1 kΩ、按住按钮
P4_LOW = {2.2e3: (0.195, 0.133), 4.7e3: (0.150, 0.109), 10e3: (0.123, 0.088), 47e3: (0.079, 0.050)}  # 按住时输出低电平 (CTR 50%, 200%) / V
P4_T3 = {2.2e3: 14.6, 4.7e3: 27.0, 10e3: 48.6, 47e3: 154.4}             # 示波器版：0/5 V 500 Hz 方波、R_in 330 Ω，LED 灭后升到 3.0 V / μs（CTR 50%）
P4_TR = {2.2e3: 25.9, 4.7e3: 46.7, 10e3: 82.8, 47e3: 257.5}             # 同上，10%→90% / μs
P4_SLOW = {2.2e3: 0.906, 4.7e3: 1.956, 10e3: 4.189, 47e3: 19.89}        # 慢速版（并 470 μF）：松开按钮后升到 3.0 V / s（CTR 50%）
C_SLOW = 470e-6


def fig_p4_1():
    """图 23-p4-1：PC817 上升时间实验的面包板接线（输入侧 9 V 电池在下半区，输出侧 5 V 在上半区，两边不共地）。"""
    bb = Breadboard(30, "PC817 上拉电阻与上升时间实验面包板俯视图（两侧电源不共地）",
                    size=(12.5, 6.6), rails=("+5 V", "GND", "电池−", "+9 V"))
    ax = bb.ax
    ax.set_xlim(-3.4, 40.5)
    bb.chip(20, "PC817", npin=4, names={1: "A", 2: "K", 3: "E", 4: "C"})   # 1 脚 f20、2 脚 f21、3 脚 e21、4 脚 e20
    # 输入侧（下半区，9 V 电池）
    bb.wire("j5", "B+5", "pos")
    bb.part("h5", "h9", "按钮", "S", lab_side=-1)
    bb.part("i9", "i14", "R_in 1 kΩ", "R", lab_side=-1)
    bb.part("g14", "g19", "红色指示 LED", "L", lab_side=1)
    bb.wire("h19", "h20", "sig")
    bb.wire("j21", "B-21", "gnd2")
    bb.module(-3.2, -10.9, 4.0, 1.5, "9 V 电池\n（输入侧电源）", fc="#fde9d9")
    bb.wire((0.6, -10.15), "B+1", "pos")
    bb.wire((-0.6, -9.4), "B-3", "gnd2", via=[(-0.6, -8.15), (3.0, -8.15)])
    # 输出侧（上半区，5 V）
    bb.wire("a21", "T-21", "gnd")
    bb.part("d20", "d26", "R_L（2.2 k / 4.7 k / 10 k / 47 k）", "R", lab_side=-1)
    bb.wire("a26", "T+26", "pos")
    bb.part("b20", "b23", "C 470 μF（第 8 步才插）", "E", lab_side="r")
    bb.wire("a23", "T-23", "gnd")
    bb.wire("c20", (33.5, 3.6), "out")
    bb.module(33.5, 2.9, 5.2, 1.4, "接万用表红表笔\n或示波器探头", fc="#fff3e0")
    bb.module(-3.2, 9.4, 3.6, 1.4, "5 V 电源\n（USB 稳压模块）")
    bb.wire((0.4, 10.1), "T+1", "pos")
    bb.wire((-1.4, 9.4), "T-2", "gnd", via=[(-1.4, 7.7)])
    bb.probe("a20", "OUT", dx=-1.4)
    bb.probe("j9", "P", dy=-0.75)
    bb.probe("j14", "Q", dy=-0.75)
    bb.probe("j20", "A", dx=-0.8)
    ax.plot([0.6, 30.4], [-0.2, -0.2], ls="--", color="0.4", lw=1.4, zorder=3)
    bb.note(31.6, -2.4, "上下两半之间\n没有任何导线：\n光是唯一的通路\n（隔离）", va="center")
    bb.note(1.0, -12.4, "紫色圈 = 下红表笔的列；OUT 对 GND 轨量，P、Q、A 对「电池−」轨量", ha="left")
    bb.legend()
    bb.save("23", "23_p4_1_breadboard.png")
    print("[接线] PC817 1 脚 f20、2 脚 f21、3 脚 e21、4 脚 e20；+9 V→j5，按钮 h5–h9，R_in i9–i14，红 LED g14(+)–g19，h19→h20，j21→电池−；"
          "R_L d20–d26，a26→+5 V，a21→GND，C 470 μF b20(+)–b23，a23→GND")
    print(f"[数值] 按住按钮：R_in 两端 {P4_DC['v_rin']:.2f} V → I_F = {P4_DC['v_rin'] / 1e3 * 1e3:.2f} mA；"
          f"红色 LED {P4_DC['v_ind']:.2f} V，PC817 LED {P4_DC['v_ir']:.2f} V")
    for rl, (lo50, lo200) in P4_LOW.items():
        need = (5 - 0.2) / rl
        print(f"[数值] R_L {rl / 1e3:g} kΩ：饱和需 I_C ≥ {need * 1e3:.2f} mA（CTR 50% 可给 {0.5 * P4_DC['i_f'] * 1e3:.2f} mA）；"
              f"按住时输出 {lo50:.3f} V（CTR 50%）/ {lo200:.3f} V（CTR 200%）")


def fig_p4_2():
    """图 23-p4-2：并上 470 μF 以后的慢速上升（左），以及和不并电容时（示波器才看得到的）上升时间的比较（右）。"""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.3), gridspec_kw=dict(width_ratios=[1.35, 1]))
    t = np.linspace(0, 30, 3001)
    cols = [fs.C["vin"], fs.C["vout"], fs.C["fb"], fs.C["third"]]
    offs = [(6, 8), (4, -14), (4, -14), (4, -14)]
    for (rl, (lo, _)), c, off in zip(P4_LOW.items(), cols, offs):
        tau = rl * C_SLOW
        v = 5 - (5 - lo) * np.exp(-t / tau)
        t3 = tau * np.log((5 - lo) / (5 - 3.0))
        a1.plot(t, v, color=c, lw=1.8, label=f"R_L = {rl / 1e3:g} kΩ")
        a1.plot([t3], [3.0], "o", color=c, ms=5)
        a1.annotate(f"{t3:.2f} s", (t3, 3.0), xytext=off, textcoords="offset points", color=c, fontsize=8.5)
        print(f"[图 23-p4-2 左] R_L {rl / 1e3:g} kΩ：τ = R_L·C = {tau:.2f} s，升到 3.0 V 用 {t3:.2f} s（ngspice {P4_SLOW[rl]:.2f} s）")
    fs.ref_h(a1, 3.0, "单片机高电平门限 3.0 V")
    a1.set_xlim(0, 30)
    a1.set_ylim(0, 5.4)
    fs.axlabels(a1, "松开按钮后的时间", "s", "输出（4 脚）电压", "V")
    a1.set_title("并 470 μF：用秒表就能计时", fontsize=10.5)
    a1.legend(fontsize=8.5, loc="lower right")
    rls = np.array(list(P4_T3))
    x = np.arange(len(rls))
    slow = np.array([P4_SLOW[r] for r in rls]) / P4_SLOW[rls[0]]
    fast = np.array([P4_T3[r] for r in rls]) / P4_T3[rls[0]]
    a2.bar(x - 0.18, slow, 0.36, color=fs.C["vout"], label="并 470 μF（秒级，秒表测）")
    a2.bar(x + 0.18, fast, 0.36, color=fs.C["vin"], label="不并电容（微秒级，示波器测）")
    a2.plot(x, rls / rls[0], "_", color=fs.C["ref"], ms=26, mew=2, label="和 R_L 成正比的位置")
    for i in range(len(rls)):
        a2.text(x[i] - 0.18, slow[i] + 0.3, f"{slow[i]:.1f}", ha="center", fontsize=8, color=fs.C["vout"])
        a2.text(x[i] + 0.18, fast[i] + 0.3, f"{fast[i]:.1f}", ha="center", fontsize=8, color=fs.C["vin"])
    a2.set_xticks(x, [f"{r / 1e3:g} kΩ" for r in rls])
    fs.axlabels(a2, "上拉电阻 R_L", None, "升到 3.0 V 的时间（以 2.2 kΩ 为 1）")
    a2.set_title("慢速版和真实速度的「倍数」不一样", fontsize=10.5)
    a2.legend(fontsize=8, loc="upper left")
    print("[图 23-p4-2 右] 倍数（以 2.2 kΩ 为 1）：慢速版 " + "、".join(f"{s:.2f}" for s in slow)
          + "；不并电容 " + "、".join(f"{f:.2f}" for f in fast) + "；R_L 之比 " + "、".join(f"{r / rls[0]:.2f}" for r in rls))
    for r in rls:
        print(f"[数值] 示波器版 R_L {r / 1e3:g} kΩ：升到 3.0 V {P4_T3[r]:.1f} μs，10%→90% {P4_TR[r]:.1f} μs")
    fig.tight_layout()
    fs.save(fig, "23", "23_p4_2_slow.png")


if __name__ == "__main__":
    fig_p4_1()
    fig_p4_2()


# ======================= 第 8 轮补电路图（page1–page3：凡正文讲具体电路连接处，附近都要有电路图） =======================
from schem import C as _C
EMPH = _C["third"]      # 强调色（红紫）：新加的元件、测量点
BAD = _C["bad"]         # 朱红：错误接法


def _opto(d, x0=0.0, vin="12 V\n信号", rin="$R_{in}$ 2.2 kΩ", rl="$R_L$ 4.7 kΩ", vcc="+5 V", part="PC817",
          out="输出 → 单片机引脚", src="dc", bleed=None, rbe=None, ceq=None, gy=-2.6, sides=True, g2="GND2"):
    """光耦输入电路通用画法（光耦放在 (x0, 0)）。src: "dc" 电压源 / "btn" 电池 + 按钮。
    bleed: LED 两端并的泄放电阻标注；rbe: 基极–发射极电阻标注（4N25 类）；ceq: 输出端等效电容标注。返回关键点。"""
    d += (oc := elm.Optocoupler(base=bool(rbe)).right().at((x0, 0)))
    d += elm.Label().at((x0 + 0.75, 0.75)).label(part, fontsize=10)
    ax, cy = oc.anode
    tap = ax - 0.7
    d += elm.Line().endpoints(oc.anode, (tap, 0))
    d += elm.Resistor().endpoints((tap, 0), (tap - 2.6, 0)).label(rin, "top")
    xs = tap - 3.2
    d += elm.Line().endpoints((tap - 2.6, 0), (xs, 0))
    d += elm.Line().endpoints(oc.cathode, (ax, gy))
    d += elm.Line().endpoints((ax, gy), (xs, gy))
    if src == "dc":
        d += elm.SourceV().endpoints((xs, gy), (xs, 0))
        d += elm.Label().at((xs - 0.7, gy / 2)).label(vin, halign="right")
    else:
        d += elm.Battery().endpoints((xs, gy), (xs, gy + 1.3))
        d += elm.Button().endpoints((xs, gy + 1.3), (xs, 0))
        d += elm.Label().at((xs - 0.7, gy + 0.6)).label(vin, halign="right")
        d += elm.Label().at((xs - 0.7, gy + 1.95)).label("按钮", halign="right")
    d += elm.Ground().at((xs, gy))
    d += elm.Label().at((xs + 0.9, gy - 0.8)).label("GND1")
    if bleed:
        d += elm.Dot().at((tap, 0)); d += elm.Dot().at((tap, gy))
        d += elm.Resistor().endpoints((tap, 0), (tap, gy)).color(EMPH)
        d += elm.Label().at((tap - 0.4, gy / 2)).label(bleed, halign="right", color=EMPH)
    cx = oc.collector[0]
    jx = cx + 1.0
    d += elm.Line().endpoints(oc.collector, (jx, oc.collector[1]))
    d += elm.Dot().at((jx, oc.collector[1]))
    d += elm.Resistor().endpoints((jx, oc.collector[1]), (jx, 2.5)).label(rl, "bottom")
    if "内部" in rl:
        d.elements[-1].linestyle("--")
    d += elm.Vdd().at((jx, 2.5)).label(vcc)
    ox = jx + 1.6
    d += elm.Line().endpoints((jx, oc.collector[1]), (ox, oc.collector[1]))
    d += elm.Dot(open=True).at((ox, oc.collector[1])).label(out, "right")
    eg = gy - (0.8 if rbe else 0)
    d += elm.Line().endpoints(oc.emitter, (cx, eg))
    d += elm.Ground().at((cx, eg))
    d += elm.Label().at((cx + 0.9, eg - 0.8)).label(g2)
    if rbe:
        bx, by = oc.absanchors["base"]
        d += elm.Resistor().endpoints((bx, by), (bx, eg)).color(EMPH)
        d += elm.Label().at((bx - 0.3, (by + eg) / 2)).label(rbe, halign="right", color=EMPH)
        d += elm.Line().endpoints((bx, eg), (cx, eg)).color(EMPH)
    if ceq:
        kx = jx + 0.8
        d += elm.Dot().at((kx, oc.collector[1]))
        d += elm.Capacitor().endpoints((kx, oc.collector[1]), (kx, gy)).color(EMPH).linestyle("--")
        d += elm.Label().at((kx + 0.4, gy / 2 - 0.2)).label(ceq, halign="left", color=EMPH, fontsize=10)
        d += elm.Line().endpoints((kx, gy), (cx, gy)).color(EMPH).linestyle("--")
    barrier(d, x0 + 0.75, (-1.9 if rbe else gy - 1.0), 1.9)
    if sides:
        d += elm.Label().at((xs + 1.2, 2.2)).label("输入侧", color=_C["bad"])
        d += elm.Label().at((ox + 0.6, 2.2)).label("输出侧", color=_C["vin"])
    return dict(oc=oc, xs=xs, jx=jx, ox=ox, cx=cx, gy=gy, eg=eg, tap=tap)


def fig_p1_4():
    """图 23-p1-4：断开两侧电源，万用表电阻挡/通断挡测 GND1 与 GND2 之间，应为开路。"""
    with drawing(fontsize=11) as d:
        r = _opto(d, vin="12 V 信号\n（已断开）", vcc="+5 V\n（已断开）")
        y = r["gy"] - 2.0
        d += elm.Line().endpoints((r["xs"], r["gy"]), (r["xs"], y)).color(EMPH)
        d += elm.Line().endpoints((r["xs"], y), (-0.6, y)).color(EMPH)
        d += elm.MeterOhm().endpoints((-0.6, y), (2.2, y)).color(EMPH).label("万用表 电阻挡 / 通断挡", "bottom", color=EMPH)
        d += elm.Line().endpoints((2.2, y), (r["cx"], y)).color(EMPH)
        d += elm.Line().endpoints((r["cx"], y), (r["cx"], r["gy"])).color(EMPH)
        d += elm.Label().at((0.8, y - 1.3)).label("应显示开路（OL 或 1）", color=EMPH, fontsize=10)
    save_schem(d, P, "23_p1_4_gnd_check.png")


def fig_p2_4():
    """图 23-p2-4：第五步的等效电路——LED 熄灭后，R_L 给输出端的等效电容充电。"""
    tau = 4.7e3 * C_EQ
    print(f"[图 23-p2-4] 等效电容 {C_EQ*1e9:.1f} nF；4.7 kΩ 时 R_L·C = {tau*1e6:.1f} μs")
    with drawing(fontsize=11) as d:
        _opto(d, vin="12 V\n→ 0 V", rl="$R_L$", ceq="等效电容 $C$\n（存储时间 + 米勒效应，\n标定值约 3.3 nF）",
              out="$V_{out}$", sides=False)
        d += elm.Label().at((3.0, -4.6)).label("LED 熄灭后：+5 V 经 $R_L$ 给 $C$ 充电，$\\tau = R_L C$", fontsize=10)
    save_schem(d, P, "23_p2_4_rise_equiv.png")


def fig_p2_5():
    """图 23-p2-5：例 1（24 V PLC、6.8 kΩ、10 kΩ 上拉、5 V）与例 3（5 V 输入、1.5 kΩ、4.7 kΩ 上拉、3.3 V）。"""
    i1 = (24 - V_F) / 6.8e3
    i3 = (5 - V_F) / 1.5e3
    assert abs(i1 * 1e3 - 3.35) < 0.01 and abs(i3 * 1e3 - 2.53) < 0.01
    print(f"[图 23-p2-5] 例 1：I_F = {i1*1e3:.2f} mA；例 3：I_F = {i3*1e3:.2f} mA")
    with drawing(fontsize=11) as d:
        _opto(d, 0, vin="PLC\n24 V", rin="$R_{in}$ 6.8 kΩ", rl="$R_L$ 10 kΩ", vcc="+5 V", out="5 V 单片机", sides=False)
        d += elm.Label().at((0.8, 4.3)).label(f"(a) 例 1：$I_F$ ≈ {i1*1e3:.2f} mA", fontsize=11)
        x1 = 12.5
        _opto(d, x1, vin="5 V\n信号", rin="$R_{in}$ 1.5 kΩ", rl="$R_L$ 4.7 kΩ", vcc="+3.3 V", out="3.3 V 单片机", sides=False)
        d += elm.Label().at((x1 + 0.8, 4.3)).label(f"(b) 例 3：$I_F$ ≈ {i3*1e3:.2f} mA", fontsize=11)
    save_schem(d, P, "23_p2_5_examples.png")


def fig_p2_6():
    """图 23-p2-6：第六节低压实验——9 V 电池 + 按钮 + 2.2 kΩ 点亮 LED；输出侧 4.7 kΩ 上拉，万用表测 4 脚。"""
    i_f = (9 - V_F) / 2.2e3
    print(f"[图 23-p2-6] 9 V、2.2 kΩ：I_F = {i_f*1e3:.2f} mA")
    with drawing(fontsize=11) as d:
        r = _opto(d, vin="9 V\n电池", rin="$R_{in}$ 2.2 kΩ\n（步骤 4 换 22 kΩ）", src="btn", out="", sides=False)
        oc = r["oc"]
        d += elm.Label().at((oc.anode[0] + 0.15, 0.35)).label("1", fontsize=9, halign="left")
        d += elm.Label().at((oc.cathode[0] + 0.15, -1.85)).label("2", fontsize=9, halign="left")
        d += elm.Label().at((oc.collector[0] + 0.15, 0.3)).label("4", fontsize=9, halign="left")
        d += elm.Label().at((oc.emitter[0] + 0.15, -1.85)).label("3", fontsize=9, halign="left")
        ox, gy, cx = r["ox"], r["gy"], r["cx"]
        y = oc.collector[1]
        d += elm.MeterV().endpoints((ox, y), (ox, gy)).color(EMPH)
        d += elm.Label().at((ox + 0.6, (y + gy) / 2)).label("万用表\n红表笔 → 4 脚\n黑表笔 → 地", halign="left", color=EMPH)
        d += elm.Line().endpoints((ox, gy), (cx, gy)).color(EMPH)
        d += elm.Label().at((0.8, -4.4)).label("电池负极（GND1）和 5 V 电源的地（GND2）不相连", fontsize=10)
    save_schem(d, P, "23_p2_6_lab.png")


def fig_p2_7():
    """图 23-p2-7：用 Arduino 读光耦——去掉 4.7 kΩ，改用 2 号脚的内部上拉，3 脚接 Arduino GND。"""
    with drawing(fontsize=11) as d:
        r = _opto(d, vin="9 V\n电池", rin="$R_{in}$ 2.2 kΩ", src="btn", rl="Arduino 内部上拉\n（INPUT_PULLUP）",
                  vcc="Arduino 5 V", out="Arduino 2 号脚", g2="Arduino GND", sides=False)
        d += elm.Label().at((0.8, -4.4)).label("输入侧的地（电池负极）不要接 Arduino", fontsize=10)
    save_schem(d, P, "23_p2_7_arduino.png")


def fig_p3_3():
    """图 23-p3-3：(a) LED 两端并泄放电阻（防前级漏电流）；(b) 4N25 基极–发射极接电阻（加快关断）。"""
    with drawing(fontsize=11) as d:
        _opto(d, 0, rin="$R_{in}$", rl="$R_L$", bleed="泄放电阻\n4.7～10 kΩ", vin="前级\n输出", sides=False)
        d += elm.Label().at((0.0, 4.3)).label("(a) LED 两端并泄放电阻", fontsize=11)
        x1 = 13.0
        _opto(d, x1, part="4N25", rin="$R_{in}$", rl="$R_L$", rbe="$R_{BE}$", vin="信号", sides=False)
        d += elm.Label().at((x1 + 0.6, 4.3)).label("(b) 4N25：基极–发射极接电阻", fontsize=11)
    save_schem(d, P, "23_p3_3_bleed_rbe.png")


def fig_p3_4():
    """图 23-p3-4：高速光耦 6N137 的接法——输出侧单独接 5 V 电源，输出脚外接上拉。"""
    with drawing(fontsize=11) as d:
        d += (u := module("6N137", ("阳极 2", "阴极 3"), ("VCC 8", "输出 6", "GND 5"), w=3.4).at((0, 0)))
        A = u.absanchors
        a, k = A["阳极 2"], A["阴极 3"]
        xs = a[0] - 4.2
        d += elm.Resistor().endpoints((a[0] - 0.6, a[1]), (a[0] - 3.2, a[1])).label("$R_{in}$", "top")
        d += elm.Line().endpoints(a, (a[0] - 0.6, a[1]))
        d += elm.Line().endpoints((a[0] - 3.2, a[1]), (xs, a[1]))
        gy = k[1] - 1.6
        d += elm.SourceV().endpoints((xs, gy), (xs, a[1]))
        d += elm.Label().at((xs - 0.7, (gy + a[1]) / 2)).label("信号", halign="right")
        d += elm.Line().endpoints(k, (k[0] - 0.6, k[1]))
        d += elm.Line().endpoints((k[0] - 0.6, k[1]), (k[0] - 0.6, gy))
        d += elm.Line().endpoints((k[0] - 0.6, gy), (xs, gy))
        d += elm.Ground().at((xs, gy))
        d += elm.Label().at((xs + 0.9, gy - 0.8)).label("GND1")
        v, o, g = A["VCC 8"], A["输出 6"], A["GND 5"]
        px = v[0] + 1.0
        top = v[1] + 1.4
        d += elm.Line().endpoints(v, (px, v[1])).color(EMPH)
        d += elm.Line().endpoints((px, v[1]), (px, top)).color(EMPH)
        d += elm.Dot().at((px, top))
        d += elm.Vdd().at((px, top)).label("+5 V（输出侧电源，4.5～5.5 V）", color=EMPH)
        rx = px + 1.4
        d += elm.Line().endpoints((px, top), (rx, top))
        d += elm.Resistor().endpoints((rx, top), (rx, o[1]))
        d += elm.Label().at((rx + 0.4, (top + o[1]) / 2)).label("上拉", halign="left")
        d += elm.Line().endpoints(o, (rx, o[1]))
        d += elm.Dot().at((rx, o[1]))
        d += elm.Line().endpoints((rx, o[1]), (rx + 1.2, o[1]))
        d += elm.Dot(open=True).at((rx + 1.2, o[1])).label("→ 单片机", "right")
        d += elm.Line().endpoints(g, (px, g[1]))
        d += elm.Line().endpoints((px, g[1]), (px, gy))
        d += elm.Ground().at((px, gy))
        d += elm.Label().at((px + 0.9, gy - 0.8)).label("GND2")
    save_schem(d, P, "23_p3_4_6n137.png")


def fig_p3_5():
    """图 23-p3-5（示意，不要动手做）：交流输入光耦经 100 kΩ 接市电，输出 10 kΩ 上拉，做过零检测。"""
    with drawing(fontsize=11) as d:
        x = 0.0
        d += elm.SourceSin().endpoints((-4.0, -2.4), (-4.0, 0)).label("220 V\n市电", "left").color(BAD)
        d += elm.Resistor().endpoints((-4.0, 0), (-1.4, 0)).label("100 kΩ（示意值）", "top").color(BAD)
        d += elm.Line().endpoints((-1.4, 0), (-0.6, 0)).color(BAD)
        d += elm.Line().endpoints((-0.6, 0), (-0.6, -2.4)).color(BAD)
        d += elm.Line().endpoints((-0.6, 0), (0.6, 0)).color(BAD)
        d += elm.LED().endpoints((0.6, 0), (0.6, -2.4)).color(BAD)
        d += elm.LED().endpoints((-0.6, -2.4), (-0.6, 0)).flip().color(BAD)
        d += elm.Line().endpoints((0.6, -2.4), (-4.0, -2.4)).color(BAD)
        d += (q := elm.NpnPhoto().anchor("base").at((2.6, -1.2)))
        d += elm.Line().endpoints((-1.1, 0.6), (3.8, 0.6)).linestyle(":")
        d += elm.Line().endpoints((3.8, 0.6), (3.8, -3.0)).linestyle(":")
        d += elm.Line().endpoints((3.8, -3.0), (-1.1, -3.0)).linestyle(":")
        d += elm.Line().endpoints((-1.1, -3.0), (-1.1, 0.6)).linestyle(":")
        d += elm.Label().at((1.35, 1.0)).label("交流输入光耦（两只 LED 反向并联）", fontsize=10)
        barrier(d, 1.6, -3.4, 0.4, "")
        cx = q.collector[0]
        d += elm.Line().endpoints(q.collector, (cx, 0.0))
        d += elm.Line().endpoints((cx, 0.0), (cx + 2.6, 0.0))
        d += elm.Dot().at((cx + 2.6, 0.0))
        d += elm.Resistor().endpoints((cx + 2.6, 0.0), (cx + 2.6, 2.4))
        d += elm.Label().at((cx + 3.0, 1.2)).label("10 kΩ", halign="left")
        d += elm.Vdd().at((cx + 2.6, 2.4)).label("+5 V")
        d += elm.Line().endpoints((cx + 2.6, 0.0), (cx + 4.0, 0.0))
        d += elm.Dot(open=True).at((cx + 4.0, 0.0)).label("过零脉冲 → 单片机", "right")
        d += elm.Line().endpoints(q.emitter, (cx, -3.8))
        d += elm.Ground().at((cx, -3.8))
        d += elm.Label().at((-2.2, -3.6)).label("整个输入侧带 220 V：原理示意，不要动手做", color=BAD, fontsize=10)
    save_schem(d, P, "23_p3_5_zerocross_schem.png")


def fig_p3_7():
    """图 23-p3-7：练习 4——用导线把 GND1 和 GND2 连起来（错误）。"""
    with drawing(fontsize=11) as d:
        r = _opto(d)
        y = r["gy"] - 1.8
        d += elm.Line().endpoints((r["xs"], r["gy"]), (r["xs"], y)).color(BAD)
        d += elm.Line().endpoints((r["xs"], y), (r["cx"], y)).color(BAD)
        d += elm.Line().endpoints((r["cx"], y), (r["cx"], r["gy"])).color(BAD)
        d += elm.Label().at((0.8, y - 0.5)).label("错误：一根导线把 GND1 和 GND2 连在一起，隔离失效", color=BAD, fontsize=10)
    save_schem(d, P, "23_p3_7_gnd_link.png")


def fig_p3_6():
    """图 23-p3-6：练习 1、3、5 共用的电路（PC817 / 4N25，12 V 输入、5 V 输出侧）。"""
    with drawing(fontsize=11) as d:
        _opto(d, 0, rin="$R_{in}$（练习 3：470 Ω）", rl="$R_L$ = ?", out="单片机", sides=False)
        d += elm.Label().at((0.0, 4.3)).label("(a) 练习 1、3：PC817，$I_F$ 5 mA，CTR 按 25%", fontsize=11)
        x1 = 13.5
        _opto(d, x1, part="4N25", rin="$R_{in}$ = ?", rl="$R_L$ 4.7 kΩ", out="单片机", sides=False)
        d += elm.Label().at((x1 + 0.4, 4.3)).label("(b) 练习 5：4N25，CTR 按 10%", fontsize=11)
    save_schem(d, P, "23_p3_6_ex_circuits.png")


if __name__ == "__main__":
    fig_p1_4(); fig_p2_4(); fig_p2_5(); fig_p2_6(); fig_p2_7(); fig_p3_3(); fig_p3_4(); fig_p3_5(); fig_p3_7(); fig_p3_6()
