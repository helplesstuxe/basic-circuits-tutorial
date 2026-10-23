"""22 三极管驱动继电器：除 22_sim.py 那两张以外的所有配图。运行：python code/figs/22_figs.py
图上出现的每个数字都由本脚本打印（fs.mark 自动打印；其余用 print）。模型与 code/22_sim.py 相同。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from schem import *
import figstyle as fs

P = "22"
VCC, R_COIL, V_BE, V_SAT = 5.0, 70.0, 0.7, 0.2
I_MAX = (VCC - V_SAT) / R_COIL


def drive(v_pin, rb, beta):
    """返回 (I_C, V_CE)；与 22_sim.py 的 drive() 相同的分段模型。"""
    ib = np.maximum(v_pin - V_BE, 0.0) / rb
    ic = np.minimum(beta * ib, I_MAX)
    vce = np.where(beta * ib >= I_MAX, V_SAT, VCC - ic * R_COIL)
    return ic, vce


def driver_schem():
    """图 22-p1-3：单片机引脚 → R_B → NPN → 继电器线圈（反并续流二极管）；触点在隔离带另一侧切换 220V 灯。"""
    with drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 0)).label("单片机引脚\n（5 V / 0 V）", "left")
        d += elm.Resistor().right().label("$R_B$ 680 Ω")
        d += (q := elm.BjtNpn().anchor("base").label("Q1\n2N3904", "right", ofst=(0.1, -0.2)))
        d += elm.Line().down().at(q.emitter).length(0.6)
        d += elm.Ground()
        d += elm.Line().up().at(q.collector).length(0.5)
        d += (jc := elm.Dot())
        d += (kc := Coil(label="").up())
        d += elm.Label().at((kc.center[0] - 1.5, kc.center[1])).label("继电器线圈 K1\n5 V / 70 Ω")
        d += (jt := elm.Dot())
        d += elm.Line().up().length(0.6)
        d += elm.Vdd().label("+5 V")
        d += elm.Line().right().at(jc.center).length(1.6)
        d += elm.Diode().up().toy(jt.center).label("D1 续流\n1N4148", "right")
        d += elm.Line().left().tox(jt.center)
        barrier(d, 6.2, -1.8, 4.6, "低压侧 ｜ 220V 侧")
        d += elm.Dot(open=True).at((7.6, 3.6)).label("L 220V", "left")
        d += elm.Line().right().length(0.4)
        d += ContactNO().right().label("K1 常开触点", ofst=0.5)
        d += elm.Line().right().length(0.4)
        d += elm.Line().down().length(1.2)
        d += LampX().down().label("灯", "right")
        d += elm.Line().down().length(1.0)
        d += elm.Line().left().tox(7.6)
        d += elm.Dot(open=True).label("N", "left")
    print("[图 22-p1-3] R_B 680 Ω、2N3904、线圈 5 V / 70 Ω、续流二极管 1N4148、触点切换 220V 灯")
    save_schem(d, P, "22_p1_3_driver.png")


def current_bars():
    """图 22-p1-1：单片机引脚能给的电流 vs 继电器线圈要的电流。"""
    names = ["引脚建议\n（测试条件）", "引脚绝对\n最大值", "SRD-05VDC\n高灵敏型线圈", "SRD-05VDC\n标准型线圈"]
    vals = [20.0, 40.0, 71.4, 89.3]
    cols = [fs.C["vin"], fs.C["bad"], fs.C["vout"], fs.C["vout"]]
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.bar(names, vals, color=cols, width=0.55)
    for k, v in enumerate(vals):
        ax.text(k, v + 2, f"{v:g} mA", ha="center", fontsize=9)
        print(f"[图 22-p1-1] {names[k].replace(chr(10), '')}: {v:g} mA")
    fs.ref_h(ax, 40)
    fs.axlabels(ax, None, None, "电流", "mA")
    ax.set_ylim(0, 105)
    fs.save(fig, P, "22_p1_1_current.png")


def two_states():
    """图 22-p1-2：开到底（R_B = 680 Ω）与半开（R_B = 10 kΩ，β = 100）的对比。"""
    cases = [("开到底\n$R_B$ = 680 Ω", 680), ("半开\n$R_B$ = 10 kΩ", 10e3)]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    for k, (name, rb) in enumerate(cases):
        ic, vce = drive(5.0, rb, 100)
        pct = (VCC - vce) / VCC * 100
        p = vce * ic * 1e3
        c = fs.C["vin"] if k == 0 else fs.C["bad"]
        a1.bar(k, pct, color=c, width=0.5); a1.text(k, pct + 2, f"{pct:.0f}%", ha="center", fontsize=9)
        a2.bar(k, p, color=c, width=0.5); a2.text(k, p + 2, f"{p:.1f} mW", ha="center", fontsize=9)
        print(f"[图 22-p1-2] {name.replace(chr(10), ' ')}（β = 100）：线圈 {pct:.0f}% 额定，三极管 {p:.1f} mW")
    for a in (a1, a2):
        a.set_xticks([0, 1], [c[0] for c in cases])
    fs.ref_h(a1, 75, "吸合门限 75%", x=0.98)
    a1.set_ylim(0, 110); a2.set_ylim(0, 105)
    fs.axlabels(a1, None, None, "线圈电压占额定值", "%")
    fs.axlabels(a2, None, None, "三极管发热功率", "mW")
    fs.save(fig, P, "22_p1_2_states.png")


def ic_ib():
    """图 22-p2-1：I_C 随 I_B 变化——先按 β 斜线上升，碰到线圈允许的上限就"顶住"（饱和）。"""
    ib = np.linspace(0, 8e-3, 801)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for beta, key in [(300, "vin"), (100, "vout"), (30, "third")]:
        ax.plot(ib * 1e3, np.minimum(beta * ib, I_MAX) * 1e3, **fs.LS[key], label=f"β = {beta}")
    fs.ref_h(ax, I_MAX * 1e3, f"上限 $(V_{{CC}}-0.2\\,\\mathrm{{V}})/R$ = {I_MAX*1e3:.1f} mA", x=0.98)
    need = I_MAX / 30
    fs.ref_v(ax, need * 1e3, f"$I_C/\\beta_{{min}}$ = {need*1e3:.2f} mA", y=0.55)
    ib_use = (5.0 - V_BE) / 680
    fs.ref_v(ax, ib_use * 1e3, f"680 Ω：{ib_use*1e3:.2f} mA", y=0.35)
    print(f"[图 22-p2-1] 上限 {I_MAX*1e3:.1f} mA；β_min = 30 时需要 {need*1e3:.2f} mA；R_B = 680 Ω 给 {ib_use*1e3:.2f} mA（{ib_use/need:.1f} 倍）")
    fs.axlabels(ax, "基极电流 $I_B$", "mA", "集电极电流 $I_C$", "mA")
    ax.set_ylim(0, 85)
    ax.legend(loc="lower center")
    fs.save(fig, P, "22_p2_1_icib.png")


def rb_sweep():
    """图 22-p3-1：扫 R_B，看线圈拿到的电压占额定值多少（三种 β）。"""
    rb = np.logspace(2, 5, 600)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for beta, key in [(300, "vin"), (100, "vout"), (30, "third")]:
        ic, vce = drive(5.0, rb, beta)
        ax.plot(rb, (VCC - vce) / VCC * 100, **fs.LS[key], label=f"β = {beta}")
        # 线圈电压刚好跌到 75% 吸合门限时的 R_B
        r75 = beta * (5.0 - V_BE) / (0.75 * VCC / R_COIL)
        print(f"[图 22-p3-1] β = {beta}：R_B 超过 {r75/1e3:.2f} kΩ 时线圈低于 75%")
    fs.ref_h(ax, 75, "吸合门限 75%", x=0.30)
    fs.ref_v(ax, 680, "680 Ω", y=0.25)
    ax.set_xscale("log")
    fs.axlabels(ax, "基极电阻 $R_B$", "Ω", "线圈电压占额定值", "%")
    ax.set_ylim(0, 105)
    ax.legend(loc="lower left")
    fs.save(fig, P, "22_p3_1_rbsweep.png")


def uln_schem():
    """图 22-p3-2（练习答案）：ULN2003 驱动两路 12 V 继电器，COM 接线圈电源。"""
    with drawing(fontsize=11) as d:
        d += (u := module("ULN2003", ("IN1", "IN2", "GND"), ("OUT1", "OUT2", "COM")))
        d += elm.Line().left().at(u.IN1).length(1.0)
        d += elm.Dot(open=True).label("单片机 引脚 1", "left")
        d += elm.Line().left().at(u.IN2).length(1.0)
        d += elm.Dot(open=True).label("单片机 引脚 2", "left")
        d += elm.Line().left().at(u.GND).length(0.6)
        d += elm.Ground()
        top = u.OUT1.y + 2.6
        d += elm.Line().right().at(u.OUT1).length(1.2)
        d += (k1 := Coil(label="").up().toy(top))
        d += elm.Label().at((k1.center[0] - 1.1, k1.center[1])).label("K1 线圈\n12 V")
        d += elm.Line().right().at(u.OUT2).length(3.2)
        d += (k2 := Coil(label="").up().toy(top))
        d += elm.Label().at((k2.center[0] + 1.0, k2.center[1])).label("K2 线圈\n12 V")
        d += elm.Line().right().at(u.COM).length(5.8)
        d += elm.Line().up().toy(top)
        d += elm.Line().left().tox(u.OUT1.x + 1.2)
        d += elm.Line().up().at((u.OUT1.x + 2.8, top)).length(0.5)
        d += elm.Vdd().label("+12 V")
    print("[图 22-p3-2] ULN2003：IN1/IN2 直接接单片机引脚，OUT 接线圈下端，COM 接 +12 V")
    save_schem(d, P, "22_p3_2_uln2003.png")


if __name__ == "__main__":
    driver_schem(); current_bars(); two_states(); ic_ib(); rb_sweep(); uln_schem()
