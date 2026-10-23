"""21 MOS 管开关：本节点全部配图（电路图用 schemdraw，曲线用 matplotlib）。
运行：/workspace/circuits-venv/bin/python code/figs/21_figs.py   → 21-mosfet-switch/img/
仿真模型在 code/21_sim.py（栅极电荷示意模型，量级参考 IRLZ44N 数据手册）。
"""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import matplotlib.pyplot as plt
import figstyle as fs
from schem import drawing, save_schem, elm

_spec = importlib.util.spec_from_file_location("sim21", os.path.join(HERE, "..", "21_sim.py"))
sim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sim)


def gate_drive(d, q, r_label="$R_G$\n100 Ω", src_label="单片机引脚\n0 / 5 V"):
    """在 MOS 管 q 的栅极左边画：单片机方波源 → R_G → 栅极，栅源之间 R_GS 下拉。"""
    g = q.gate
    d += elm.Line().endpoints(g, (g[0] - 0.8, g[1]))
    d += elm.Dot().at((g[0] - 0.8, g[1]))
    d += elm.Resistor().endpoints((g[0] - 0.8, g[1]), (g[0] - 0.8, g[1] - 2.2)).label("$R_{GS}$\n10 kΩ", loc="bottom")
    d += elm.Ground().at((g[0] - 0.8, g[1] - 2.2))
    d += elm.Resistor().endpoints((g[0] - 0.8, g[1]), (g[0] - 3.8, g[1])).label(r_label, loc="top")
    d += elm.SourceSquare().endpoints((g[0] - 3.8, g[1]), (g[0] - 3.8, g[1] - 2.2)).label(src_label, loc="bottom")
    d += elm.Ground().at((g[0] - 3.8, g[1] - 2.2))


def fig_p1_1():
    """低边开关：负载在上，N 沟道 MOS 管在下（源极接地）。"""
    with drawing() as d:
        d += elm.Vdd().at((0, 6)).label("+12 V")
        d += elm.Lamp().endpoints((0, 6), (0, 3.6)).label("负载\n12 V / 3 A", loc="bottom")
        d += elm.Dot().at((0, 3.6))
        q = elm.NFet().theta(0).reverse().anchor("drain").at((0, 3.6)).label("Q1\nN 沟道", loc="right", ofst=(0.3, 0))
        d += q
        d += elm.Ground().at(q.source)
        pin_labels(d, q)
        # 体二极管：MOS 管内部天生自带，阳极在源极 S、阴极在漏极 D（schemdraw 的 NFet 不画它，这里补上）
        bx = q.drain[0] + 2.4
        d += elm.Line().endpoints(q.drain, (bx, q.drain[1]))
        d += elm.Diode().endpoints((bx, q.source[1]), (bx, q.drain[1])).label("体二极管\n（管内自带）", loc="bottom", ofst=0.15)
        d += elm.Line().endpoints((bx, q.source[1]), q.source)
        d += elm.Dot().at(q.source)
        gate_drive(d, q)
    save_schem(d, "21", "21_p1_1_low_side.png")


def pin_labels(d, q, gdx=0.25, right=False):
    """在 MOS 管三个引脚旁标出 G、D、S（right=True 时 D、S 标在引脚右边，避开左边的导线）。"""
    g, dr, so = q.gate, q.drain, q.source
    d += elm.Label().at((g[0] + gdx, g[1] + 0.3)).label("G", fontsize=10)
    if right:
        d += elm.Label().at((dr[0] + 0.3, dr[1] - 0.3)).label("D", fontsize=10)
        d += elm.Label().at((so[0] + 0.3, so[1] - 0.15)).label("S", fontsize=10)
    else:
        d += elm.Label().at((dr[0] - 0.3, dr[1] - 0.15)).label("D", fontsize=10)
        d += elm.Label().at((so[0] - 0.3, so[1] + 0.15)).label("S", fontsize=10)


def fig_p1_2():
    """高边开关：P 沟道 MOS 管在上（源极接 +12 V），负载在下；一只小 N 沟道管 Q2 负责把栅极拉低。"""
    with drawing() as d:
        q1 = elm.PFet().theta(0).reverse().anchor("source").at((0, 6)).label("Q1\nP 沟道", loc="right", ofst=(0.3, 0))
        d += q1
        d += elm.Vdd().at((0, 6)).label("+12 V")
        d += elm.Lamp().endpoints(q1.drain, (q1.drain[0], q1.drain[1] - 2.4)).label("负载", loc="bottom")
        d += elm.Ground().at((q1.drain[0], q1.drain[1] - 2.4))
        g = q1.gate
        gx = g[0] - 1.0
        d += elm.Line().endpoints(g, (gx, g[1]))
        d += elm.Dot().at((gx, g[1]))
        d += elm.Resistor().endpoints((gx, g[1]), (gx, 6)).label("上拉\n10 kΩ", loc="top")
        d += elm.Line().endpoints((gx, 6), (0, 6))
        d += elm.Dot().at((0, 6))
        q2 = elm.NFet().theta(0).reverse().anchor("drain").at((gx, g[1] - 0.9)).label("Q2", loc="right", ofst=(0.2, 0))
        d += elm.Line().endpoints((gx, g[1]), (gx, g[1] - 0.9))
        d += q2
        d += elm.Ground().at(q2.source)
        pin_labels(d, q1, gdx=-0.3, right=True); pin_labels(d, q2)
        gate_drive(d, q2, r_label="1 kΩ", src_label="单片机引脚\n0 / 3.3 V")
    save_schem(d, "21", "21_p1_2_high_side.png")


def fig_p2_2():
    """导通损耗、开关损耗随 PWM 频率的变化（R_G = 100 Ω，5 V 驱动，12 V / 3 A，占空比 50%）。"""
    s = sim.simulate(r_g=100.0)
    e_sw = s["e_on"] + s["e_off"]
    f = np.logspace(2, 5, 300)
    p_cond, p_sw = sim.losses(f, e_sw)
    p_cond = np.full_like(f, p_cond)
    total = p_cond + p_sw
    f_eq = p_cond[0] / e_sw
    print(f"[数值] 每周期开关能量 E_on + E_off = {e_sw*1e6:.1f} μJ；导通损耗 = {p_cond[0]:.3f} W；两者相等的频率 = {f_eq/1e3:.1f} kHz")
    assert abs(p_cond[0] - 3.0 ** 2 * 0.025 * 0.5) < 1e-9
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.loglog(f / 1e3, p_cond, **fs.LS["vin"], label="导通损耗 $I^2 R_{DS(on)} D$")
    ax.loglog(f / 1e3, p_sw, **fs.LS["vout"], label="开关损耗 $(E_{on}+E_{off}) f$")
    ax.loglog(f / 1e3, total, **fs.LS["third"], label="合计")
    fs.ref_v(ax, f_eq / 1e3, f"{f_eq/1e3:.1f} kHz")
    for fk in (1.0, 20.0, 100.0):
        pc, ps = sim.losses(fk * 1e3, e_sw)
        fs.mark(ax, fk, pc + ps, fmt="{:.3f}", unit=" W", dx=-10, dy=8)
    fs.axlabels(ax, "PWM 频率", "kHz", "MOS 管发热", "W")
    ax.legend(loc="upper left", fontsize=8)
    fs.save(fig, "21", "21_p2_2_loss_vs_freq.png")
    return e_sw


def fig_p2_3():
    """感性负载（电机）+ 续流二极管的低边开关。"""
    with drawing() as d:
        d += elm.Vdd().at((0, 6.4)).label("+12 V")
        d += elm.Line().endpoints((0, 6.4), (0, 6.0))
        d += elm.Dot().at((0, 6.0))
        d += elm.Motor().endpoints((0, 6.0), (0, 3.6)).label("直流电机 M", loc="top")
        d += elm.Line().endpoints((0, 6.0), (2.4, 6.0))
        d += elm.Diode().endpoints((2.4, 3.6), (2.4, 6.0)).label("续流二极管\nD1", loc="bottom")
        d += elm.Line().endpoints((2.4, 3.6), (0, 3.6))
        d += elm.Dot().at((0, 3.6))
        q = elm.NFet().theta(0).reverse().anchor("drain").at((0, 3.6)).label("Q1", loc="right", ofst=(0.3, 0))
        d += q
        d += elm.Ground().at(q.source)
        gate_drive(d, q)
    save_schem(d, "21", "21_p2_3_motor_flyback.png")


def fig_p3_3():
    """练习题用：续流二极管接反（阳极接 +12 V、阴极接漏极）的电机低边开关。"""
    with drawing() as d:
        d += elm.Vdd().at((0, 6.4)).label("+12 V")
        d += elm.Line().endpoints((0, 6.4), (0, 6.0))
        d += elm.Dot().at((0, 6.0))
        d += elm.Motor().endpoints((0, 6.0), (0, 3.6)).label("直流电机 M", loc="top")
        d += elm.Line().endpoints((0, 6.0), (2.4, 6.0))
        d += elm.Diode().endpoints((2.4, 6.0), (2.4, 3.6)).label("D1\n（方向接反）", loc="bottom")
        d += elm.Line().endpoints((2.4, 3.6), (0, 3.6))
        d += elm.Dot().at((0, 3.6))
        q = elm.NFet().theta(0).reverse().anchor("drain").at((0, 3.6)).label("Q1", loc="right", ofst=(0.3, 0))
        d += q
        d += elm.Ground().at(q.source)
        gate_drive(d, q)
    save_schem(d, "21", "21_p3_3_flyback_reversed.png")


def fig_p3_1():
    """栅极电阻扫描：10 Ω、100 Ω、1 kΩ 时的开通波形和 20 kHz 下的开关损耗。"""
    rgs = [10.0, 100.0, 1000.0]
    styles = [fs.LS["vin"], fs.LS["vout"], fs.LS["third"]]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    out = []
    for rg, st in zip(rgs, styles):
        s = sim.simulate(r_g=rg, t_on=20e-6, t_end=40e-6)
        us = s["t"] * 1e6
        lab = f"$R_G$ = {rg:g} Ω"
        a1.plot(us, s["v_ds"], **st, label=lab)
        e = s["e_on"] + s["e_off"]
        out.append((rg, s["t_sw_on"], s["t_sw_off"], e, 5.0 / rg))
        print(f"[数值] R_G = {rg:g} Ω：开通 {s['t_sw_on']*1e6:.2f} μs，关断 {s['t_sw_off']*1e6:.2f} μs，"
              f"每周期开关能量 {e*1e6:.2f} μJ，20 kHz 开关损耗 {e*20e3:.3f} W，栅极峰值电流 {5/rg*1e3:.0f} mA")
    fs.axlabels(a1, "时间（开通瞬间）", "μs", "$V_{DS}$", "V")
    a1.set_xlim(-0.2, 8); a1.legend(loc="center right", fontsize=8)
    for i, (rg, ton, toff, e, ipk) in enumerate(out):
        fs.mark(a1, ton * 1e6, 1.2, fmt=f"{ton*1e6:.2f} μs", unit="", dx=3, dy=6 + 12 * (i == 0))
    x = np.arange(len(rgs))
    pw = [e * 20e3 for (_, _, _, e, _) in out]
    a2.bar(x, pw, color=[fs.C["vin"], fs.C["vout"], fs.C["third"]], width=0.55)
    for i, p in enumerate(pw):
        fs.mark(a2, i, p, fmt="{:.3f}", unit=" W", dx=-14, dy=4)
    a2.set_xticks(x, [f"{rg:g} Ω" for rg in rgs])
    fs.axlabels(a2, "栅极电阻 $R_G$", None, "20 kHz 开关损耗", "W")
    a2.set_yscale("log"); a2.set_ylim(0.01, max(pw) * 3)
    assert out[2][1] > 5 * out[1][1], "R_G 加大 10 倍，开通时间也大约变成 10 倍"
    assert out[0][4] > 0.4, "R_G = 10 Ω 时栅极峰值电流达 500 mA，远超单片机引脚能力"
    fs.save(fig, "21", "21_p3_1_rg_sweep.png")


def fig_p3_2():
    """3 A 负载时的导通发热：按数据手册 R_DS(on) 最大值计算（不同驱动电压）。"""
    data = [  # (型号, 驱动电压, R_DS(on) 最大值 mΩ)；None = 手册在这个电压下不保证
        ("IRLZ44N", "10 V", 22), ("IRLZ44N", "5 V", 25), ("IRLZ44N", "4 V", 35),
        ("AO3400A", "4.5 V", 32), ("AO3400A", "2.5 V", 48),
        ("IRF540N", "10 V", 44), ("IRF540N", "3.3 V", None)]
    i_l = 3.0
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    labels, vals = [], []
    for k, (part, v, r) in enumerate(data):
        labels.append(f"{part}\n{v}")
        if r is None:
            ax.bar(k, 0.02, color=fs.C["bad"], width=0.6)
            ax.plot([k], [0.06], marker="x", color=fs.C["bad"], ms=9)
            ax.text(k, 0.12, "手册\n不保证", ha="center", fontsize=8, color=fs.C["bad"])
            print(f"[数值] {part} @ {v}：手册未给 R_DS(on)")
            continue
        p = i_l ** 2 * r / 1e3
        vals.append(p)
        ax.bar(k, p, color=fs.C["vin"] if part != "IRF540N" else fs.C["fb"], width=0.6)
        fs.mark(ax, k, p, fmt="{:.2f}", unit=" W", dx=-12, dy=4)
    ax.set_xticks(range(len(data)), labels, fontsize=8)
    fs.axlabels(ax, "型号与驱动电压", None, "3 A 时导通发热", "W")
    ax.set_ylim(0, 0.55)
    assert abs(i_l ** 2 * 0.025 - 0.225) < 1e-9
    fs.save(fig, "21", "21_p3_2_heat_datasheet.png")


if __name__ == "__main__":
    fig_p1_1(); fig_p1_2(); fig_p2_2(); fig_p2_3(); fig_p3_1(); fig_p3_2(); fig_p3_3()
