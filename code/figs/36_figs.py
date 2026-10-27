"""36 施密特整形与频率/脉冲计数：全部配图。
运行（仓库根目录）：/workspace/circuits-venv/bin/python code/figs/36_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。数值函数在 code/36_sim.py，面包板小工具在 code/33_bbkit.py。
SPICE 对照值取自 spice/36/results.json（review/spice/36.md）。
"""
import os, sys, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import lab_schem as ls
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt


def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, "..", fn))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


sim = _load("sim36", "36_sim.py")
bbk = _load("bbkit", "33_bbkit.py")
N = "36"
C, LS = fs.C, fs.LS
SP = {r["desc"]: r["spice"] for r in json.load(open(os.path.join(HERE, "..", "..", "spice", "36", "results.json"), encoding="utf-8"))}
F_SIG, F_N = sim.F_SIG, sim.F_NOISE
VH, VL, VOH, VOL = sim.VH, sim.VL, sim.VOH, sim.VOL


def axl(ax, xl, yl):
    ax.set_xlabel(xl)
    if yl:
        ax.set_ylabel(yl)


def _edges(t, vo, thr=2.5):
    vo = np.asarray(vo)
    up = np.where((vo[1:] > thr) & (vo[:-1] <= thr))[0]
    return np.asarray(t)[1:][up]


# =====================================================================
# 图 36-p1-1 一个门限 vs 两个门限：同样带干扰的输入，输出各翻转几次
# =====================================================================
def p1_1():
    t0, t1 = 0.100, 0.130
    _, _, r0 = sim.simulate(r2=None, t_end=t1 + 0.001, keep=(t0, t1))
    _, _, r2 = sim.simulate(t_end=t1 + 0.001, keep=(t0, t1))
    fig, axs = plt.subplots(2, 1, figsize=(7.4, 5.6), sharex=True)
    out = []
    for ax, r, ttl in ((axs[0], r0, "普通比较器（不接 R2）：只有一个门限 2.5 V"),
                       (axs[1], r2, "施密特（R2 = 220 kΩ）：上门限、下门限两条线")):
        t = (np.array(r["t"]) - t0) * 1e3
        ax.plot(t, r["v2"], color=C["vin"], lw=1.0, label="比较器输入（带干扰的近似正弦）")
        vo = np.array(r["vo"])
        ax.plot(t, 1.6 + (vo - VOL) / (VA_ := sim.VA) * 0.5, color=C["vout"], lw=1.6, label="输出（缩小画，高 = 5 V）")
        n = len(_edges(r["t"], vo))
        out.append(n)
        if r is r0:
            ax.axhline(2.5, **LS["ref"]); ax.text(30.3, 2.5, "门限 2.5 V", fontsize=8.5, va="center")
        else:
            ax.axhline(VH, color=C["fb"], ls="--", lw=1.0); ax.axhline(VL, color=C["fb"], ls="--", lw=1.0)
            ax.text(30.3, VH, f"上门限 {VH:.2f} V", fontsize=8.5, va="center", color=C["fb"])
            ax.text(30.3, VL, f"下门限 {VL:.2f} V", fontsize=8.5, va="center", color=C["fb"])
        ax.set_title(f"{ttl}　→ 30 ms 里输出升了 {n} 次", fontsize=10)
        ax.set_ylim(1.5, 3.0)
        ax.set_ylabel("电压 / V")
    axs[0].legend(loc="upper left", fontsize=8.5, ncol=2)
    axs[1].set_xlabel("时间 / ms（30 ms 里有 3 个信号周期）")
    fig.suptitle("图 36-p1-1 同一个带干扰的输入：一个门限 vs 两个门限", fontsize=10.5)
    fs.save(fig, N, "36_p1_1_single_vs_schmitt.png")
    print(f"[数值] 图 36-p1-1：30 ms 内上升沿 普通比较器 {out[0]} 次，施密特 {out[1]} 次（信号周期 {1e3/F_SIG:.2f} ms）")
    assert out[1] == 3 and out[0] > 3


# =====================================================================
# 图 36-p1-2 流量计 → 整形 → 计数 → 流量
# =====================================================================
def p1_2():
    fig, ax = fs.diagram(9.0, 3.0)
    b1 = fs.box(ax, 1.0, 2.0, "涡轮/涡街\n流量计", w=1.5, h=0.9)
    b2 = fs.box(ax, 3.3, 2.0, "施密特整形\n（LM393 + 回差）", w=2.0, h=0.9, fc=C["fill2"])
    b3 = fs.box(ax, 5.7, 2.0, "Arduino\n数脉冲、量周期", w=1.9, h=0.9)
    b4 = fs.box(ax, 8.0, 2.0, "流量\nQ = f × 60 / K", w=1.7, h=0.9)
    fs.arrow(ax, b1["r"], b2["l"]); fs.arrow(ax, b2["r"], b3["l"]); fs.arrow(ax, b3["r"], b4["l"])
    t = np.linspace(0, 1, 200)
    x0, y0 = 1.65, 0.75
    ax.plot(x0 + t * 1.1, y0 + 0.25 * np.sin(2 * np.pi * 3 * t) + 0.06 * np.sin(2 * np.pi * 31 * t), color=C["vin"], lw=1.1)
    ax.text(x0 + 0.55, 0.25, "近似正弦 + 干扰", fontsize=8.5, ha="center")
    sq = np.where(np.sin(2 * np.pi * 3 * t) > 0, 0.25, -0.25)
    ax.plot(4.1 + t * 1.1, y0 + sq, color=C["vout"], lw=1.4)
    ax.text(4.65, 0.25, "干净的方波", fontsize=8.5, ha="center")
    q = sim.gpm(500, 100)
    ax.text(7.2, 0.6, f"例：K = 100 个/加仑，\nf = 500 Hz → {q:.0f} 加仑/分钟", fontsize=8.5, ha="left")
    ax.set_title("图 36-p1-2 数脉冲就是数流量：一个脉冲 = 固定的一小份水", fontsize=10.5)
    fs.save(fig, N, "36_p1_2_flow_chain.png")
    print(f"[数值] 图 36-p1-2：K = 100、500 Hz → {q:.0f} GPM")
    assert q == 300


# =====================================================================
# 原理图（第 2 页无孔位版、第 4 页带孔位版共用）
# =====================================================================
def _schem(d, holes=False):
    H = (lambda s: s) if holes else (lambda s: "")
    SIG, OUT = C["vin"], C["vout"]
    # 信号源 D7 → Rs1 → n1 → Rs2 → n2
    d += elm.Dot(open=True).at((0, 0))
    ls.lab(d, (-0.25, 0.0), "D7\ntone 100 Hz" + H("\n蓝线 → j3"), ha="right", fs_=9.5, color=SIG)
    d += elm.Resistor().endpoints((0, 0), (3, 0))
    ls.lab(d, (1.5, 0.65), "Rs1 1 kΩ" + H("（h3–h7）"), ha="center", fs_=9.5)
    d += elm.Dot().at((3, 0))
    d += elm.Capacitor(polar=True).endpoints((3, 0), (3, -2.4))
    d += elm.Ground().at((3, -2.4))
    ls.lab(d, (3.4, -1.2), "C1 4.7 µF\n电解，+ 在上" + H("\nj7→GND"), fs_=9.5)
    d += elm.Resistor().endpoints((3, 0), (6, 0))
    ls.lab(d, (4.5, -0.65), "Rs2 1 kΩ" + H("（g7–g11）"), ha="center", fs_=9.5)
    d += elm.Dot().at((6, 0))
    d += elm.Capacitor(polar=True).endpoints((6, 0), (6, -2.4))
    d += elm.Ground().at((6, -2.4))
    ls.lab(d, (6.4, -1.2), "C2 4.7 µF\n电解，+ 在上" + H("\nj11→GND"), fs_=9.5)
    # 干扰 D5 → Rn → n2
    yn = 2.6
    d += elm.Dot(open=True).at((0, yn))
    ls.lab(d, (-0.25, yn), "D5\nPWM 976.6 Hz\n（干扰）" + H("\n天蓝线 → j14"), ha="right", fs_=9.5, color=C["cur"])
    d += elm.Resistor().endpoints((0, yn), (3.4, yn))
    ls.lab(d, (1.7, yn + 0.65), "Rn 2.2 kΩ" + H("（i11–i14）"), ha="center", fs_=9.5)
    d += elm.Line().at((3.4, yn)).to((6, yn))
    d += elm.Line().at((6, yn)).to((6, 0))
    # n2 → R1 → IN+
    x21 = 9.6
    d += elm.Resistor().endpoints((6, 0), (x21, 0))
    ls.lab(d, ((6 + x21) / 2, -0.65), "R1 10 kΩ" + H("\n跳线 h11–h16，R1 g16–g21"), ha="center", fs_=9.5)
    d += elm.Dot().at((x21, 0))
    opa = elm.Opamp(leads=True).right().flip().anchor("in2").at((x21 + 1.2, 0.0))
    d += opa
    a = opa.absanchors
    d += elm.Line().at((x21, 0)).to(a["in2"])
    ls._pin(d, a["in2"], "3", dx=-0.2, dy=0.25)
    ls._pin(d, a["in1"], "2", dx=-0.2, dy=-0.25)
    ls._pin(d, a["out"], "1", dx=0.15, dy=0.25)
    ls.lab(d, (a["in2"][0] + 0.8, a["out"][1]), "LM393\nA 组", fs_=9)
    t, b = a["vs"], a["vd"]
    d += elm.Line().at(t).to((t[0], t[1] + 0.5))
    d += elm.Vdd().at((t[0], t[1] + 0.5)).label("+9 V")
    ls._pin(d, t, "8", dx=0.25, dy=0.22)
    d += elm.Line().at(b).to((b[0], b[1] - 0.5))
    d += elm.Ground().at((b[0], b[1] - 0.5))
    ls._pin(d, b, "4", dx=0.25, dy=-0.22)
    if holes:
        ls.colnote(d, (b[0] + 0.3, b[1] - 0.75), "j22→GND", "right", ofst=0.0)
        ls.colnote(d, (x21 + 0.1, 0.35), "第 21 列", "top", ofst=0.0)
    # 输出节点、R2 正反馈、R3 上拉到 Arduino 5 V
    xo, yo = a["out"][0] + 0.9, a["out"][1]
    d += elm.Line().at(a["out"]).to((xo, yo))
    d += elm.Dot().at((xo, yo))
    yr2 = 3.0
    d += elm.Line().at((x21, 0)).to((x21, yr2))
    d += elm.Resistor().endpoints((x21, yr2), (xo, yr2))
    ls.lab(d, ((x21 + xo) / 2, yr2 + 0.65), "R2 220 kΩ" + H("（h19–h21）"), ha="center", fs_=9.5)
    d += elm.Line().at((xo, yr2)).to((xo, yo))
    x3 = xo + 1.4
    d += elm.Line().at((xo, yo)).to((x3, yo)).color(OUT).linewidth(1.8)
    d += elm.Dot().at((x3, yo))
    d += elm.Resistor().endpoints((x3, yo), (x3, yo + 3.0))
    d += elm.Vdd().at((x3, yo + 3.0)).label("+5 V（Arduino）")
    ls.lab(d, (x3 + 0.45, yo + 1.5), "R3 4.7 kΩ" + H("\nj19→+5 V 轨"), fs_=9.5)
    xa = x3 + 2.2
    d += elm.Line().at((x3, yo)).to((xa, yo)).color(OUT).linewidth(1.8)
    d += elm.Dot(open=True).at((xa, yo))
    ls.lab(d, (xa + 0.25, yo), "→ Arduino D8\n（Timer1 捕获）" + H("\n橙线 i19 → D8"), fs_=9.5, color=OUT)
    ls.probe(d, (x3, yo), "②", dx=0.0, dy=-1.3)
    if holes:
        ls.colnote(d, (xo + 0.1, yo - 0.4), "第 19 列", "right", ofst=0.0)
    # 2.5 V 参考：Ra、Rb 分 Arduino 5 V，Cref 滤波
    xr, yref = x21 - 0.4, -3.8
    d += elm.Vdd().at((xr - 4.2, yref)).label("+5 V")
    d += elm.Resistor().endpoints((xr - 4.2, yref), (xr, yref))
    ls.lab(d, (xr - 2.6, yref - 0.6) if holes else (xr - 2.1, yref + 0.6), "Ra 10 kΩ" + H("（j20→+5 V 轨）"), ha="center", fs_=9.5)
    d += elm.Dot().at((xr, yref))
    d += elm.Resistor().endpoints((xr, yref), (xr, yref - 2.6))
    d += elm.Ground().at((xr, yref - 2.6))
    ls.lab(d, (xr - 0.45, yref - 1.3), "Rb 10 kΩ" + H("\ni20–i25\nj25→GND"), ha="right", fs_=9.5)
    xc = xr + 1.6
    d += elm.Line().at((xr, yref)).to((xc, yref))
    d += elm.Capacitor().endpoints((xc, yref), (xc, yref - 2.6))
    d += elm.Ground().at((xc, yref - 2.6))
    ls.lab(d, (xc + 0.4, yref - 1.3), "Cref 100 nF" + H("\nh20–h25"), fs_=9.5)
    yin1 = a["in1"][1]
    d += elm.Line().at((xr, yref)).to((xr, yin1)).color(C["fb"]).linewidth(1.6)
    d += elm.Line().at((xr, yin1)).to(a["in1"]).color(C["fb"]).linewidth(1.6)
    ls.probe(d, (xc, yref), "③", dx=1.0, dy=0.0)
    ls.lab(d, (xc + 1.6, yref + 0.5), "参考 2.5 V", fs_=9.5, color=C["fb"])
    ls.probe(d, (6, 0), "①", dx=0.9, dy=1.1)
    if holes:
        ls.colnote(d, (xr + 0.15, (yref + yin1) / 2), "第 20 列", "right", ofst=0.0)
    return dict(n2=(6, 0), out=(x3, yo), ref=(xc, yref))


def p1_3():
    """图 36-p1-3：直觉篇里的实验电路（与图 36-p2-1 同一张原理图）。"""
    d = drawing(fontsize=11)
    _schem(d)
    ls.note(d, (-3.5, -7.7), "LM393 用 9 V 电池供电；R3 上拉、Ra 都接 Arduino 的 5 V，所以送进 D8 的高电平不超过 5 V。两边的 GND 连在一起。")
    ls.note(d, (-3.5, -8.4), "① = 比较器输入 n2；② = 输出；③ = 参考 2.5 V。去掉 R2 就是「没有回差」的单门限比较器。")
    save_schem(d, N, "36_p1_3_schem.png")


def p3_1():
    """图 36-p3-1：参数篇对照用的原理图（R1、R2、R3、信号源两级 RC、测量点①②③）。"""
    d = drawing(fontsize=11)
    _schem(d)
    ls.note(d, (-3.5, -7.7), "信号源内阻 Rs = Rs1 + Rs2（两级 RC 的电阻，本图是 1 kΩ + 1 kΩ）；回差电流从输出经 R2、R1 流进 n2，再流过 Rs。")
    ls.note(d, (-3.5, -8.4), "① = n2；② = 输出（R3 上拉到 Arduino 5 V）；③ = 参考 2.5 V。LM393 8 脚接 +9 V、4 脚接 GND，B 组 5、6 脚接 GND。")
    save_schem(d, N, "36_p3_1_schem.png")


def p2_1():
    d = drawing(fontsize=11)
    _schem(d)
    ls.note(d, (-3.5, -7.7), "LM393 用 9 V 电池供电（只管比较器本身）；R3 上拉、Ra 都接 Arduino 的 5 V，所以送进 D8 的高电平不超过 5 V。两边的 GND 连在一起。")
    ls.note(d, (-3.5, -8.4), "① = 比较器输入 n2；② = 输出；③ = 参考 2.5 V。LM393 的 B 组不用：5、6 脚接 GND。")
    save_schem(d, N, "36_p2_1_schem.png")
    print("[图 36-p2-1] 原理图：D7→Rs1 1k→C1 4.7µ→Rs2 1k→C2 4.7µ（n2）←Rn 2.2k←D5；n2→R1 10k→IN+；R2 220k；R3 4.7k→5 V；IN−=2.5 V")


# =====================================================================
# 图 36-p2-2 回差曲线：输入慢慢升、慢慢降，输出在哪里跳
# =====================================================================
def p2_2():
    fig, ax = plt.subplots(figsize=(7, 4.2))
    x0, x1 = 2.2, 2.8
    ax.plot([x0, VH], [VOL, VOL], color=C["vout"], lw=2.0)
    ax.plot([VH, x1], [VOH, VOH], color=C["vout"], lw=2.0)
    ax.plot([VL, VH], [VOH, VOH], color=C["vout"], lw=2.0)
    ax.plot([VL, VH], [VOL, VOL], color=C["vout"], lw=2.0)
    ax.annotate("", (VH, VOH - 0.15), (VH, VOL + 0.15), arrowprops=dict(arrowstyle="-|>", color=C["vout"], lw=1.5))
    ax.annotate("", (VL, VOL + 0.15), (VL, VOH - 0.15), arrowprops=dict(arrowstyle="-|>", color=C["vout"], lw=1.5))
    ax.annotate("输入往上走", (2.45, VOL + 0.35), xytext=(2.25, VOL + 0.9), fontsize=9, arrowprops=dict(arrowstyle="->"))
    ax.annotate("输入往下走", (2.55, VOH - 0.35), xytext=(2.62, VOH - 1.0), fontsize=9, arrowprops=dict(arrowstyle="->"))
    ax.axvline(2.5, **LS["ref"])
    ax.text(2.505, 2.5, "不接 R2 时\n唯一的门限\n2.5 V", fontsize=8.5, color="0.4")
    spv, spl = SP["上门限 VH（R2 = 220k）"], SP["下门限 VL（R2 = 220k）"]
    ax.plot([spv, spl], [2.5, 2.5], "x", color=C["bad"], ms=9, mew=2, label=f"SPICE 门限 {spv:.3f} / {spl:.3f} V")
    fs.span(ax, VL, VH, 0.6 * VOH + 0.3, f"回差 {(VH-VL)*1000:.0f} mV")
    ax.set_xlim(x0, x1); ax.set_ylim(-0.3, 5.6)
    ax.legend(loc="upper left", fontsize=9)
    axl(ax, "比较器输入 n2 / V", "输出（D8 上看到的）/ V")
    ax.set_title(f"图 36-p2-2 上门限 {VH:.2f} V、下门限 {VL:.2f} V：中间这一段输出「记得」上一次的状态", fontsize=10.5)
    fs.save(fig, N, "36_p2_2_hysteresis.png")
    print(f"[数值] 图 36-p2-2：VH = {VH:.4f}，VL = {VL:.4f}，回差 {(VH-VL)*1e3:.1f} mV，VOH = {VOH:.3f}，VOL = {VOL}；SPICE {spv:.4f}/{spl:.4f}")
    assert abs(spv - VH) < 0.01 and abs(spl - VL) < 0.01


# =====================================================================
# 图 36-p2-3 D7 方波、D5 干扰经两级 RC 变成什么样
# =====================================================================
def p2_3():
    t0, t1 = 0.100, 0.120
    _, _, r = sim.simulate(r2=None, t_end=t1 + 0.001, keep=(t0, t1))
    _, _, rs = sim.simulate(r2=None, noise=False, t_end=t1 + 0.001, keep=(t0, t1))
    t = np.array(r["t"])
    tm = (t - t0) * 1e3
    d7 = np.where((t * F_SIG) % 1.0 < 0.5, sim.VA, 0.0)
    fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.0), sharex=True, gridspec_kw=dict(height_ratios=(1, 1.5)))
    axs[0].plot(tm, d7, color=C["third"], lw=1.4, label=f"D7：tone(7, 100)，实际 {F_SIG:.2f} Hz 方波")
    axs[0].set_ylim(-0.5, 6.2); axs[0].set_ylabel("D7 / V")
    axs[0].legend(loc="upper right", fontsize=8.5)
    axs[1].plot(tm, r["v2"], color=C["vin"], lw=1.0, label="n2（D7 + D5 干扰）")
    axs[1].plot(tm, rs["v2"], color=C["good"], ls="--", lw=1.2, label="n2（假如没有 D5 干扰）")
    pp_s, pp_n = sim.amplitudes()
    axs[1].axhline(2.5, **LS["ref"])
    axs[1].set_ylim(2.05, 2.95); axs[1].set_ylabel("n2 / V")
    axs[1].legend(loc="upper right", fontsize=8.5)
    axs[1].text(0.3, 2.1, f"信号峰峰值 {pp_s:.2f} V，干扰峰峰值 {pp_n*1000:.0f} mV（SPICE {SP['n2 上干扰峰峰值（Rn = 2.2k）']*1000:.0f} mV）", fontsize=8.5)
    axl(axs[1], "时间 / ms", None)
    fig.suptitle("图 36-p2-3 两级 RC 把方波磨成「近似正弦」，D5 的干扰是叠在上面的细小锯齿", fontsize=10.5)
    fs.save(fig, N, "36_p2_3_signal_noise.png")
    print(f"[数值] 图 36-p2-3：n2 信号峰峰值 {pp_s:.3f} V，干扰 {pp_n*1000:.1f} mV")
    assert 0.53 < pp_s < 0.55 and 0.12 < pp_n < 0.13


# =====================================================================
# 图 36-p2-4 门控计数 vs 倒数计数：误差随频率
# =====================================================================
def p2_4():
    f = np.logspace(0, 4.3, 300)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(f, sim.gate_err(f) * 100, color=C["vin"], lw=1.8, label="门控计数：数 1 s 里的脉冲（±1 个）")
    fmin8 = sim.timer1_fmin(8)
    ok = f >= fmin8
    ax.plot(f[ok], sim.recip_err(f[ok]) * 100, color=C["vout"], lw=1.8, label="倒数计数：量一个周期（Timer1 ÷8，2 MHz，±1 个计数）")
    ax.axvline(fmin8, color=C["vout"], ls=":", lw=1.0)
    ax.text(fmin8 * 0.93, 30, f"÷8 低于 {fmin8:.2f} Hz\n会溢出（要换 ÷64）", fontsize=8, ha="right", color=C["vout"])
    ax.axhline(sim.TIMEBASE * 100, color=C["bad"], ls="--", lw=1.2, label=f"Uno 陶瓷谐振器的初始误差上限 ±{sim.TIMEBASE*100:g} %")
    fx = np.sqrt(sim.F_CPU / 8)
    ax.plot([fx], [sim.gate_err(fx) * 100], "o", color="k", ms=6)
    ax.annotate(f"交点 {fx:.0f} Hz", (fx, sim.gate_err(fx) * 100), textcoords="offset points", xytext=(8, -14), fontsize=9)
    ax.plot([F_SIG], [sim.gate_err(F_SIG) * 100], "s", color=C["vin"], ms=6)
    ax.annotate("100 Hz：±1 %", (F_SIG, 1.0), textcoords="offset points", xytext=(8, 4), fontsize=9, color=C["vin"])
    ax.plot([F_SIG], [sim.recip_err(F_SIG) * 100], "s", color=C["vout"], ms=6)
    ax.annotate("100 Hz：±0.005 %", (F_SIG, sim.recip_err(F_SIG) * 100), textcoords="offset points", xytext=(8, -12), fontsize=9, color=C["vout"])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_ylim(1e-5, 200)
    ax.legend(loc="lower left", fontsize=8.5)
    axl(ax, "信号频率 / Hz（对数刻度）", "读数的最大相对误差 / %（对数刻度）")
    ax.set_title(f"图 36-p2-4 低频量周期、高频数脉冲；但准不准还要看时基（最多 ±{sim.TIMEBASE*100:g} %）", fontsize=10.5)
    fs.save(fig, N, "36_p2_4_gate_vs_recip.png")
    print(f"[数值] 图 36-p2-4：100 Hz 门控 ±{sim.gate_err(100)*100:.2f} %，倒数 ±{sim.recip_err(100)*100:.4f} %；交点 {fx:.1f} Hz")
    assert abs(fx - 1414.2) < 0.1 and abs(fmin8 - 30.52) < 0.01 and f[ok].min() >= fmin8


# =====================================================================
# 图 36-p2-5 Timer1 输入捕获：计数器一直在数，边沿一来就「拍照」
# =====================================================================
def p2_5():
    fclk = sim.F_CPU / 8
    t = np.linspace(0, 0.05, 20001)
    cnt = (t * fclk) % 65536
    edges = np.arange(1, 6) / F_SIG
    edges = edges[edges < 0.05]
    caps = [int(e * fclk) % 65536 for e in edges]
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    ax.plot(t * 1e3, cnt, color=C["vin"], lw=1.2, label="TCNT1：Timer1 的计数值（每 0.5 µs 加 1）")
    ax.axhline(65535, **LS["ref"]); ax.text(0.3, 66500, "65535 之后回到 0（溢出）", fontsize=8.5)
    for k, (e, c) in enumerate(zip(edges, caps)):
        ax.plot([e * 1e3], [c], "o", color=C["vout"], ms=7)
        ax.axvline(e * 1e3, color=C["vout"], lw=0.6, ls=":")
        ax.annotate(f"ICR1 = {c}", (e * 1e3, c), textcoords="offset points", xytext=(4, 6 if k % 2 == 0 else -14), fontsize=8.5)
    d01 = caps[1] - caps[0]
    kw = next(k for k in range(1, len(caps)) if caps[k] < caps[k - 1])
    d12 = caps[kw] - caps[kw - 1]
    d12w = d12 + 65536
    ax.text(1, -15000, f"相邻两次相减：{caps[1]} − {caps[0]} = {d01}；中间跨过溢出时 {caps[kw]} − {caps[kw-1]} + 65536 = {d12w}",
            fontsize=8.5)
    ax.set_ylim(-20000, 76000); ax.set_xlim(0, 50)
    ax.legend(loc="upper right", fontsize=8.5)
    axl(ax, "时间 / ms", "计数值")
    ax.set_title(f"图 36-p2-5 输入捕获：每个上升沿把计数值抄进 ICR1；{F_SIG:.2f} Hz 一个周期约 {sim.timer1_counts(F_SIG, 8):.0f} 个计数", fontsize=10)
    fs.save(fig, N, "36_p2_5_timer1_capture.png")
    print(f"[数值] 图 36-p2-5：捕获值 {caps}；差 {d01}、{d12w}")
    assert abs(d01 - 19968) <= 1 and abs(d12w - 19968) <= 1 and d12 < 0


# =====================================================================
# 图 36-p3-2 R2 扫一遍：回差太小多数、太大不数
# =====================================================================
def p3_2():
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    styles = {2.2e3: (C["vin"], "o"), 1e3: (C["vout"], "s"), 470: (C["third"], "^")}
    allres = {}
    for rn in sim.RN_SET:
        res = sim.sweep(rn=rn)
        allres[rn] = res
        pp = sim.amplitudes(rn)[1]
        col, mk = styles[rn]
        ax.plot([dv * 1e3 for _, dv, _ in res], [e for _, _, e in res], marker=mk, color=col, lw=1.3,
                label=f"Rn = {rn/1e3:g} kΩ（干扰峰峰值 {pp*1000:.0f} mV）")
        print(f"[数值] 图 36-p3-2：Rn = {rn:g}：" + "，".join(f"{r2/1e3:.0f}k→{e}" for r2, _, e in res))
    off = [(dv, sim.simulate(r2=r2, rn=1e12, noise=False)[0]) for r2, dv, _ in allres[2.2e3]]
    ax.plot([dv * 1e3 for dv, _ in off], [e for _, e in off], marker="x", color=C["good"], ls="--", lw=1.2,
            label="拔掉干扰（只有信号）")
    print("[数值] 图 36-p3-2：拔掉干扰：" + "，".join(f"{r2/1e3:.0f}k→{e}" for (r2, _, _), (_, e) in zip(allres[2.2e3], off)))
    ax.axhline(100, **LS["ref"]); ax.text(130, 40, "正确：100 个", fontsize=9, color="0.35")
    for r2, dv, e in allres[2.2e3]:
        if r2 in (47e3, 220e3, 1e6):
            ax.annotate(f"R2 = {r2/1e3:.0f}k", (dv * 1e3, e), textcoords="offset points", xytext=(4, 8), fontsize=8.5)
    ax.set_xscale("log")
    ax.set_ylim(-30, 1050)
    ax.legend(loc="upper right", fontsize=8.5)
    axl(ax, "回差 ΔV / mV（对数刻度；R2 越小回差越大）", "1 s 内数到的上升沿 / 个")
    ax.set_title("图 36-p3-2 回差要比干扰大、比信号小：否则不是多数，就是一个也数不到", fontsize=10.5)
    fs.save(fig, N, "36_p3_2_r2_window.png")
    r = {r2: e for r2, _, e in allres[2.2e3]}
    assert r[220e3] == 100 and r[47e3] == 0 and dict((round(dv, 4), e) for dv, e in off)
    assert [e for _, e in off][4] == 0 and [e for _, e in off][6] == 100


# =====================================================================
# 图 36-p3-3 信号源内阻太大：回差电流把输入拉偏，永远到不了门限
# =====================================================================
def p3_3():
    t0, t1 = 0.10, 0.13
    _, _, ra = sim.simulate(rn=1e12, noise=False, t_end=t1 + 0.001, keep=(t0, t1))
    _, _, rb = sim.simulate(rs=10e3, c=470e-9, rn=1e12, noise=False, t_end=t1 + 0.001, keep=(t0, t1))
    fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True)
    out = []
    for ax, r, ttl in ((axs[0], ra, "Rs = 1 kΩ、C = 4.7 µF（本节用的）"), (axs[1], rb, "Rs = 10 kΩ、C = 470 nF（时间常数一样）")):
        tm = (np.array(r["t"]) - t0) * 1e3
        ax.plot(tm, r["vp"], color=C["vin"], lw=1.2, label="同相端 IN+（3 脚）")
        ax.axhline(2.5, color=C["fb"], ls="--", lw=1.0, label="反相端 2.5 V")
        n = len(_edges(r["t"], r["vo"]))
        out.append(n)
        ax.set_title(f"{ttl}：30 ms 里输出升了 {n} 次", fontsize=10)
        ax.set_ylabel("电压 / V"); ax.set_ylim(2.05, 3.25)
        assert 2.05 < min(r["vp"]) and max(r["vp"]) < 3.25          # 曲线不被裁掉
    axs[1].legend(loc="lower right", fontsize=8.5)
    axl(axs[1], "时间 / ms（拔掉干扰，只有信号；R2 = 220 kΩ）", None)
    i_h = (sim.VREF - VOL) / (sim.R1 + sim.R2)
    fig.suptitle(f"图 36-p3-3 回差电流约 {i_h*1e6:.1f} µA：流过 20 kΩ 拉偏 {i_h*20e3*1000:.0f} mV，流过 2 kΩ 只拉偏 {i_h*2e3*1000:.0f} mV", fontsize=10.5)
    fs.save(fig, N, "36_p3_3_source_resistance.png")
    print(f"[数值] 图 36-p3-3：1k 网络 30 ms 内 {out[0]} 次；10k 网络 {out[1]} 次；回差电流 {i_h*1e6:.2f} µA")
    assert out[0] == 3 and out[1] == 0


# =====================================================================
# 第 4 页：面包板（LM393 在第 19–22 列）+ 带孔位的原理图
# =====================================================================
LM_NAMES = {1: "OUTA", 2: "IN−A", 3: "IN+A", 4: "GND", 5: "IN+B", 6: "IN−B", 7: "OUTB", 8: "VCC"}


def _bow(bb, a, b, label, dy=0.5):
    """拱形两脚元件：脚在孔 a、b，身子抬高 dy（落在两排孔之间），中间的孔露出来。"""
    from matplotlib.patches import FancyBboxPatch
    (x1, y1), (x2, y2) = bb._hole(a), bb._hole(b)
    ym = y1 + dy
    bb.ax.plot([x1, x1 + 0.25, x2 - 0.25, x2], [y1, ym, ym, y2], color="0.35", lw=1.2, zorder=5)
    mx = (x1 + x2) / 2
    bb.ax.add_patch(FancyBboxPatch((mx - 0.4, ym - 0.17), 0.8, 0.34, boxstyle="round,pad=0.04",
                                   fc="#d9c7a3", ec="0.2", lw=1.0, zorder=6))
    # 标签放在拱形身子左侧（右侧 h22–h24 是 Cref 的身子，放右边会被误认成 Cref 的标签）
    # 再画一条细引线指到身子上，避免看成上方 R1 的标签
    bb.ax.annotate(label, xy=(mx - 0.45, ym), xytext=(x1 - 0.35, ym - 0.12), ha="right", va="center",
                   fontsize=7, zorder=7, arrowprops=dict(arrowstyle="-", color="0.25", lw=0.7, shrinkA=1, shrinkB=0))


def p4_1():
    nc = 31
    bb = bbk.Breadboard(nc, "图 36-p4-1 面包板：LM393 在第 19–22 列；上方两条轨是 9 V 电池，下方两条轨是 Arduino",
                        size=(11, 9.2), rails=("+9 V", "GND", "GND", "+5 V"))
    ax = bb.ax
    # 信号网络
    bb.part("h3", "h7", "Rs1 1k", "R", lab_side=1, fs_=7.5)
    bb.part("j7", "B-7", "", "E"); bb.note(7.3, -6.1, "C1", fontsize=7)
    bb.part("g7", "g11", "Rs2 1k", "R", lab_side=1, fs_=7.5)
    bb.part("j11", "B-11", "", "E"); bb.note(11.3, -6.1, "C2", fontsize=7)
    bb.part("i11", "i14", "Rn 2.2k", "R", lab_side=-1, fs_=7.5)
    bb.wire("h11", "h16", "fb")
    bb.part("g16", "g21", "R1 10k", "R", lab_side=1, fs_=7)  # 标签在上方，下方留给 R2 的标签
    # LM393
    bb.chip(19, "LM393", names=LM_NAMES)
    bb.wire("a19", "T+19", "pos")
    bb.part("b19", "T-17", "", "C"); bb.note(16.8, 5.0, "Cd 100 nF", fontsize=7, ha="right", va="center")
    bb.wire("a21", "T-21", "gnd"); bb.wire("a22", "T-22", "gnd")
    bb.wire("j22", "B-22", "gnd")
    # R2 画成「拱起来」的跨线：两脚插 h19、h21，身子抬到 g、h 两排之间，露出中间的 h20（Cref 的左脚插在那里）
    _bow(bb, "h19", "h21", "R2 220k")
    bb.part("j19", "B+19", "", "R"); bb.note(18.6, -6.9, "R3 4.7k", fontsize=7, ha="right", va="center")
    # 参考
    bb.part("j20", "B+20", "", "R"); bb.note(20.4, -6.9, "Ra 10k", fontsize=7, ha="left", va="center")
    bb.part("i20", "i25", "Rb 10k", "R", lab_side=-1, fs_=7)
    # Cref 跨 h20–h25：引线在 h21（R2 右脚的孔）处向下绕开一点，表示从 R2 拱形下面穿过、不接 h21
    from matplotlib.patches import FancyBboxPatch as _FBP
    (_x0, _y0), (_x5, _) = bb._hole("h20"), bb._hole("h25")
    _x21 = bb._hole("h21")[0]
    bb.ax.plot([_x0, _x21 - 0.5, _x21 - 0.38, _x21 + 0.38, _x21 + 0.5, _x5],
               [_y0, _y0, _y0 - 0.26, _y0 - 0.26, _y0, _y0], color="0.35", lw=1.2, zorder=5)
    _mc = (_x0 + _x5) / 2
    bb.ax.add_patch(_FBP((_mc - 0.45, _y0 - 0.25), 0.9, 0.5, boxstyle="round,pad=0.05",
                         fc="#f2d27a", ec="0.2", lw=1.0, zorder=6))
    _xc, _yc = bb._hole("h25")
    bb.ax.text(_xc + 0.3, _yc, "Cref 100n", ha="left", va="center", fontsize=7, zorder=7)
    bb.wire("j25", "B-25", "gnd")
    # 电池与地线
    bb.module(-3.2, 9.4, 3.6, 1.4, "9 V 电池")
    bb.wire((0.4, 10.4), "T+1", "pos", via=[(1, 10.4)])
    bb.wire((0.4, 9.7), "T-2", "gnd", via=[(2, 9.7)])
    bb.wire(f"T-{nc}", f"B-{nc}", "gnd", via=[(nc + 0.5, 7.7), (nc + 0.5, -6.7)])
    # Arduino
    ym = -11.9
    bb.module(0.4, ym - 1.6, 21.0, 1.6, "Arduino Uno（USB 接电脑，供 5 V）", fs_=9)
    p5 = bb.pin(1.0, ym, "5V", va="top", dy=0.25)
    pg = bb.pin(2.5, ym, "GND", va="top", dy=0.25)
    p7 = bb.pin(3.5, ym, "D7", va="top", dy=0.25)
    pd5 = bb.pin(14.5, ym, "D5", va="top", dy=0.25)
    p8 = bb.pin(17.5, ym, "D8", va="top", dy=0.25)
    bb.wire("B+1", p5, "pos")
    bb.wire("B-2", pg, "gnd", via=[(2, -7.15), (2.5, -7.15)])
    bb.wire("j3", p7, "sig", via=[(3, -5.9), (3.5, -5.9)])
    bb.wire("j14", pd5, "clk", via=[(14, -5.9), (14.5, -5.9)])
    bb.wire("i19", p8, "out", via=[(19, -4.9), (17.5, -4.9)])
    bb.probe("f11", "①", dx=0.0, dy=0.9)
    bb.probe("h19", "②", dx=-1.3, dy=-0.5)
    bb.probe("h20", "③", dx=0.0, dy=-0.5)
    ax.set_ylim(-17.4, 11.6)
    ax.set_xlim(-3.6, nc + 2.6)
    bb.note(0.0, -14.4, "① 第 11 列 = 比较器输入 n2；② 第 19 列 = 输出（接 D8）；③ 第 20 列 = 参考 2.5 V；黑表笔插 GND 轨。表笔碰该列任意一个空孔或元件脚都行", ha="left")
    bb.note(0.0, -15.2, "LM393：1–4 脚在 f 排（第 19–22 列），8–5 脚在 e 排；8 脚 a19 → +9 V，Cd 100 nF b19 → GND，B 组 5、6 脚 a22、a21 → GND", ha="left")
    bb.note(0.0, -16.0, "R1 跨在 g16–g21、Cref 跨在 h20–h25、Rb 跨在 i20–i25：只有两端插的孔算连接。R2 拱起来跨在 h19–h21 上方，h20 归 Cref 的左脚", ha="left")
    bb.note(0.0, -16.8, "下方 +5 V 轨只接 Arduino 5V，绝不和上方 +9 V 轨连；两组 GND 轨在第 31 列连通（右侧黑线），Arduino GND 接下方 GND 轨", ha="left")
    bb.legend(y=-0.03)
    bb.save(N, "36_p4_1_breadboard.png")
    print("[图 36-p4-1] D7→j3；Rs1 h3–h7；C1 j7→GND；Rs2 g7–g11；C2 j11→GND；Rn i11–i14；D5→j14；h11–h16；R1 g16–g21；"
          "LM393 第 19–22 列；a19→+9 V；Cd b19→GND；a21、a22→GND；j22→GND；R2 h19–h21；R3 j19→+5 V；i19→D8；"
          "Ra j20→+5 V；Rb i20–i25；Cref h20–h25；j25→GND")


def p4_2():
    d = drawing(fontsize=10.5)
    _schem(d, holes=True)
    ls.note(d, (-3.5, -7.9), "对照图 36-p4-1：每个元件后面的灰色小字就是它在面包板上的孔位；+9 V 只接 LM393 的 8 脚，其余「+5 V」都是下方那条 Arduino 5 V 轨。")
    ls.note(d, (-3.5, -8.6), "LM393 的 8 脚：a19→+9 V，Cd 100 nF 从 b19→GND；B 组 5、6 脚 a22、a21→GND。第 4 步才插 Rn（D5 干扰），第 5 步才插 R2。")
    ls.note(d, (-3.5, -9.3), "测量点：① n2（第 11 列）　② 输出（第 19 列）　③ 参考 2.5 V（第 20 列）；黑表笔插 GND 轨。")
    save_schem(d, N, "36_p4_2_schem_lab.png")
    print("[图 36-p4-2] 带孔位的原理图，与图 36-p4-1 一一对应")


# =====================================================================
# 图 36-p3-4 变体：霍尔涡轮流量计（开集电极输出）直接接 Arduino
# =====================================================================
def p3_4():
    d = drawing(fontsize=10.5)
    # 传感器方框
    bx, by, bw, bh = 0.0, -1.5, 3.2, 4.0
    for (xa, ya), (xb, yb) in (((bx, by), (bx + bw, by)), ((bx + bw, by), (bx + bw, by + bh)),
                               ((bx + bw, by + bh), (bx, by + bh)), ((bx, by + bh), (bx, by))):
        d += elm.Line().at((xa, ya)).to((xb, yb)).color("#4d4d4d")
    ls.lab(d, (bx + bw / 2, by + bh / 2), "霍尔涡轮\n流量计\n（内部：霍尔元件\n+ 整形\n+ 开集电极输出）", ha="center", fs_=9.5)
    yr, ys, yk = by + bh - 0.6, by + bh / 2, by + 0.6
    xe = bx + bw
    # 红线：传感器电源
    d += elm.Line().at((xe, yr)).to((xe + 2.0, yr)).color("#d0101e").linewidth(1.8)
    d += elm.Line().at((xe + 2.0, yr)).to((xe + 2.0, yr + 1.0)).color("#d0101e").linewidth(1.8)
    d += elm.Vdd().at((xe + 2.0, yr + 1.0)).label("传感器电源\n（按它的手册：可能是 5 V，\n也可能是 5～24 V）")
    ls.lab(d, (xe + 0.15, yr + 0.3), "红线", fs_=9, color="#d0101e")
    # 黄线：信号 → 上拉到 Arduino 5 V → D8
    xs = xe + 5.0
    d += elm.Line().at((xe, ys)).to((xs, ys)).color(C["vout"]).linewidth(1.8)
    ls.lab(d, (xe + 0.15, ys + 0.3), "黄线（信号）", fs_=9, color=C["vout"])
    d += elm.Dot().at((xs, ys))
    d += elm.Resistor().endpoints((xs, ys), (xs, ys + 3.0))
    d += elm.Vdd().at((xs, ys + 3.0)).label("+5 V（Arduino）")
    ls.lab(d, (xs + 0.45, ys + 1.5), "上拉 4.7 kΩ\n只能接 Arduino 5 V", fs_=9.5)
    xa = xs + 2.4
    d += elm.Line().at((xs, ys)).to((xa, ys)).color(C["vout"]).linewidth(1.8)
    d += elm.Dot(open=True).at((xa, ys))
    ls.lab(d, (xa + 0.25, ys), "→ Arduino D8\n（Timer1 捕获）", fs_=9.5, color=C["vout"])
    # 黑线：GND，和 Arduino GND 相连
    d += elm.Line().at((xe, yk)).to((xa, yk)).color("#000000").linewidth(1.8)
    d += elm.Dot(open=True).at((xa, yk))
    ls.lab(d, (xa + 0.25, yk), "→ Arduino GND", fs_=9.5)
    ls.lab(d, (xe + 0.15, yk + 0.3), "黑线", fs_=9)
    d += elm.Line().at((xe + 1.2, yk)).to((xe + 1.2, yk - 0.8))
    d += elm.Dot().at((xe + 1.2, yk))
    d += elm.Ground().at((xe + 1.2, yk - 0.8))
    ls.note(d, (-0.5, -3.4), "不需要 LM393：传感器里已经整形好了。上拉电阻绝不能接到传感器的 12 V 或 24 V 电源上，否则 D8 的保护二极管会被迫导通、电流倒灌，损坏引脚。")
    ls.note(d, (-0.5, -4.0), "传感器的黑线和 Arduino 的 GND 一定要连在一起；导线很长时，可以在 Arduino 一侧再加一级本节的施密特整形。")
    save_schem(d, N, "36_p3_4_hall_variant.png")
    print("[图 36-p3-4] 霍尔流量计变体：红线→传感器电源；黑线→GND（与 Arduino GND 相连）；黄线→4.7k 上拉到 Arduino 5 V→D8")


if __name__ == "__main__":
    if sys.argv[1:]:
        for name in sys.argv[1:]:
            globals()[name]()
        sys.exit(0)
    for fn in (p1_1, p1_2, p1_3, p2_1, p2_2, p2_3, p2_4, p2_5, p3_1, p3_2, p3_3, p3_4, p4_1, p4_2):
        fn()
