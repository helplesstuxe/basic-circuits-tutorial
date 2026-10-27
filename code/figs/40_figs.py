"""40 热式流量与 RTD 恒温差：全部配图。运行（仓库根目录）：/workspace/circuits-venv/bin/python code/figs/40_figs.py
数字来自 code/40_sim.py（Python 热模型 + Arduino 读数模拟）和 spice/40/*.cir（ngspice）；本脚本会打印图上标的数。
面包板类 Breadboard、run_spice 从 code/figs/35_figs.py 导入（不修改那个文件）。"""
import os, sys, io, contextlib, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import figstyle as fs
from figstyle import C
import schem
from schem import elm
import lab_schem as L

P = "40"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


F35 = _load("figs35", "code/figs/35_figs.py")
Breadboard, BB_RAIL_Y, BB_WIRE, run_spice = F35.Breadboard, F35.BB_RAIL_Y, F35.BB_WIRE, F35.run_spice
S = _load("sim40", "code/40_sim.py")


def LSk(k):
    return dict(fs.LS[k])


def sim_all():
    """跑一遍 40_sim.report()（不打印），拿到全部仿真结果。"""
    with contextlib.redirect_stdout(io.StringIO()):
        out = S.report()
    return out


# ======================================================================
# page1
# ======================================================================
def p1_1_wind(O):
    """图 40-p1-1：固定 60 % 占空加热，无风 / 1 m/s 风两种情况下加热 NTC 比环境高多少（从冷态开始）。"""
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for v, key, ls in ((0, "wind_0", "vin"), (1, "wind_1", "vout")):
        r = O[key]
        t, dT = r["t"], r["Tn"] - r["Ta"]
        ax.plot(t, dT, **LSk(ls), label=f"{'无风' if v == 0 else '1 m/s 的风'}（占空固定 60 %）")
        _, tn = S.steady(0.6 * S.P_MAX, float(v))
        fs.mark(ax, 560, dT[np.searchsorted(t, 560)], "{:.2f}", " K", dy=0.25 if v == 0 else 0.3)
        i63 = np.argmax(dT >= 0.632 * tn)
        print(f"[图 40-p1-1] v={v}：稳态 {tn:.2f} K，到 63 % 用 {t[i63]:.0f} s")
    fs.axlabels(ax, "时间", "s", "加热 NTC − 环境", "K")
    ax.set_xlim(0, 600); ax.set_ylim(0, 5)
    ax.legend(loc="lower right", fontsize=8)
    fs.save(fig, P, "40_p1_1_wind.png")


def p1_2_king(O):
    """图 40-p1-2：探头的散热能力 δ = P/ΔT 随风速变化（模型连续曲线 + 0～3 m/s 七个点）。"""
    A, B, G_of = O["king"]
    vs = np.linspace(0, 3, 301)
    g = np.array([1 / S.dTn_per_W(v) for v in vs]) * 1e3
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(vs, g, **LSk("vout"), label="探头整体的散热能力 δ = P / ΔT")
    for v in (0.0, 1.0, 2.0, 3.0):
        fs.mark(ax, v, G_of[v] * 1e3, "{:.1f}", " mW/K", dx=0.05, dy=-6 if v else 3)
    ax.annotate("从 0 到 1 m/s 涨了 27.5 mW/K\n从 2 到 3 m/s 只涨 9.4 mW/K", xy=(2.5, G_of[2.5] * 1e3), xytext=(1.25, 25),
                fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.8))
    print(f"[图 40-p1-2] 0→1 增 {(G_of[1.0] - G_of[0.0]) * 1e3:.1f}，2→3 增 {(G_of[3.0] - G_of[2.0]) * 1e3:.1f} mW/K")
    fs.axlabels(ax, "风速 v", "m/s", "散热能力 δ", "mW/K")
    ax.set_ylim(0, 80); ax.set_xlim(-0.05, 3.1)
    ax.legend(loc="upper left", fontsize=8)
    fs.save(fig, P, "40_p1_2_king.png")


def p1_3_rt():
    """图 40-p1-3：10 kΩ NTC 与 PT100 的电阻—温度曲线（0～100 °C）。"""
    T = np.linspace(0, 100, 401)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    a1.plot(T, S.ntc_R(T) / 1e3, **LSk("vin"))
    a2.plot(T, S.pt100(T), **LSk("vout"))
    for T0 in (25, 45):
        fs.mark(a1, T0, float(S.ntc_R(T0)) / 1e3, "{:.2f}", " kΩ", dx=3, dy=2)
    for T0 in (0, 100):
        fs.mark(a2, T0, S.pt100(T0), "{:.1f}", " Ω", dx=(5 if T0 == 0 else -28), dy=1.5)
    k_ntc = (S.ntc_R(25.5) - S.ntc_R(24.5))
    k_pt = S.pt100(25.5) - S.pt100(24.5)
    a1.text(40, 22, f"25 °C 处：每升 1 K\n电阻变 {k_ntc:.0f} Ω\n（{k_ntc / 1e4 * 100:.1f} %）", fontsize=8.5)
    a2.text(40, 105, f"25 °C 处：每升 1 K\n电阻变 {k_pt:+.3f} Ω\n（{k_pt / S.pt100(25) * 100:+.2f} %）", fontsize=8.5)
    print(f"[图 40-p1-3] NTC 25 °C 斜率 {k_ntc:.1f} Ω/K = {k_ntc / 1e4 * 100:.2f} %/K；PT100 {k_pt:.4f} Ω/K = {k_pt / S.pt100(25) * 100:.3f} %/K")
    a1.set_title("10 kΩ NTC（温度升高，电阻下降）", fontsize=10)
    a2.set_title("PT100（温度升高，电阻缓慢上升）", fontsize=10)
    fs.axlabels(a1, "温度", "°C", "电阻", "kΩ")
    fs.axlabels(a2, "温度", "°C", "电阻", "Ω")
    a1.set_ylim(0, 36); a2.set_ylim(95, 145)
    fs.save(fig, P, "40_p1_3_rt.png")


def p1_4_blocks():
    """图 40-p1-4：本节实验的方框图。"""
    fig, ax = fs.diagram(9.5, 3.4)
    ax.add_patch(mpatches.FancyBboxPatch((0.3, 0.35), 3.6, 2.7, boxstyle="round,pad=0.05", fc="#eef6fb", ec=C["cur"], lw=1.0, ls="--"))
    ax.text(2.1, 2.85, "风道（风从左往右吹）", ha="center", fontsize=9, color=C["cur"])
    for y in (1.0, 1.7, 2.4):
        fs.arrow(ax, (0.45, y), (1.0, y), color=C["cur"])
    n2 = fs.box(ax, 1.55, 2.2, "环境 NTC\nN2（上风处）", w=1.0, h=0.6, fs=8.5)
    hb = fs.box(ax, 3.05, 1.2, "加热电阻 RH\n+ 贴着的 NTC N1", w=1.4, h=0.75, fc=C["fill2"], fs=8.5)
    ar = fs.box(ax, 6.2, 1.9, "Arduino\n读 A0、A1，算温差\n开关控温，算平均占空", w=2.3, h=1.0, fs=8.5)
    q = fs.box(ax, 6.2, 0.45, "IRLZ44N 开关 + 9 V", w=2.3, h=0.5, fs=8.5)
    out = fs.box(ax, 8.65, 1.9, "平均占空\n→ 风速", w=1.2, h=0.7, fc=C["hi"], fs=8.5)
    fs.arrow(ax, n2["r"], (ar["l"][0], 2.2), "A1", fs=8)
    fs.arrow(ax, hb["r"], (ar["l"][0], 1.65), "A0", fs=8)
    fs.arrow(ax, ar["b"], q["t"], None)
    ax.text(6.3, 1.05, "D9", fontsize=8)
    fs.arrow(ax, q["l"], (3.05, 0.82), "加热电流", fs=8)
    fs.arrow(ax, ar["r"], out["l"])
    fs.save(fig, P, "40_p1_4_blocks.png")


# ======================================================================
# page2
# ======================================================================
def p2_1_ntc_div():
    """图 40-p2-1：NTC 分压接 ADC（两路一样：A0 加热 NTC，A1 环境 NTC）。"""
    with schem.drawing(fontsize=11) as d:
        for k, (x, name, pin, note) in enumerate(((0.0, "N1", "A0", "加热 NTC\n（贴在 RH 上）"), (6.0, "N2", "A1", "环境 NTC\n（上风处）"))):
            d += elm.Vdd().at((x, 6)).label("+5 V")
            d += elm.Resistor().at((x, 6)).to((x, 3.5))
            L.lab(d, (x + 0.45, 4.75), f"R_S 10 kΩ", fs_=10)
            d += elm.Dot().at((x, 3.5))
            d += elm.Thermistor().at((x, 3.5)).to((x, 1.0))
            L.lab(d, (x + 0.55, 2.25), f"{name} NTC 10 kΩ\n{note}", fs_=9.5)
            d += elm.Ground().at((x, 1.0))
            d += elm.Line().at((x, 3.5)).to((x - 1.6, 3.5))
            d += elm.Dot(open=True).at((x - 1.6, 3.5)).label(f"Arduino {pin}", "left")
        L.lab(d, (-3.6, -0.3), "$V = 5\\,\\mathrm{V}\\times\\dfrac{R_{NTC}}{R_S + R_{NTC}}$，ADC 读数 $= 1024\\times\\dfrac{R_{NTC}}{R_S+R_{NTC}}$", fs_=11)
        L.lab(d, (-3.6, -1.2), "25 °C：R_NTC = 10.00 kΩ → 2.500 V（512 字）；45 °C：4.372 kΩ → 1.521 V（311.5 字）", fs_=9.5, color="#333333")
        schem.save_schem(d, P, "40_p2_1_ntc_div.png")


def p2_2_ntc_curve():
    """图 40-p2-2：分压输出与 ADC 读数随温度变化，15～50 °C。"""
    T = np.linspace(15, 50, 351)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(T, S.ntc_V(T), **LSk("vin"), label="A0 电压")
    for T0, dy in ((20, 0.12), (25, 0.12), (45, 0.12)):
        fs.mark(ax, T0, float(S.ntc_V(T0)), "{:.3f}", " V", dx=0.6, dy=dy)
    ax2 = ax.twinx()
    ax2.set_ylim(np.array([1.2, 3.2]) * 1024 / 5)
    ax.set_ylim(1.2, 3.2)
    ax2.set_ylabel("ADC 读数 / 字")
    s25 = (S.ntc_V(25.5) - S.ntc_V(24.5)) * 1e3
    s45 = (S.ntc_V(45.5) - S.ntc_V(44.5)) * 1e3
    ax.text(30, 2.75, f"25 °C 附近每升 1 K 降 {abs(s25):.1f} mV（{abs(s25) / 1e3 * 1024 / 5:.2f} 字）\n"
                     f"45 °C 附近每升 1 K 降 {abs(s45):.1f} mV（{abs(s45) / 1e3 * 1024 / 5:.2f} 字）", fontsize=8.5)
    print(f"[图 40-p2-2] 斜率 25 °C {s25:.2f} mV/K，45 °C {s45:.2f} mV/K")
    fs.axlabels(ax, "温度", "°C", "A0 电压", "V")
    fs.save(fig, P, "40_p2_2_ntc_curve.png")


def p2_3_heater():
    """图 40-p2-3：加热器低边开关。+9 V → RH 560 Ω → IRLZ44N → 地，D9 经 100 Ω 驱动栅极，100 kΩ 下拉。"""
    with schem.drawing(fontsize=11) as d:
        xg, yg = 3.0, 2.0
        d += elm.Dot(open=True).at((-1.0, yg)).label("Arduino D9\n（0 / 5 V）", "left")
        d += elm.Resistor().at((-1.0, yg)).to((xg, yg))
        L.lab(d, (1.0, yg + 0.55), "R_G 100 Ω", ha="center", fs_=10)
        d += elm.Dot().at((xg, yg))
        d += elm.Resistor().at((xg, yg)).to((xg, -1.0))
        L.lab(d, (xg - 0.45, 0.5), "R_PD\n100 kΩ", ha="right", fs_=10)
        d += elm.Ground().at((xg, -1.0))
        q = elm.NFet().theta(0).reverse().anchor("gate").at((xg + 1.2, yg))
        d += q
        d += elm.Line().at((xg, yg)).to(q.gate)
        xq = q.drain[0]
        L.lab(d, (xq + 0.5, yg), "Q1 IRLZ44N", fs_=10)
        d += elm.Line().at(q.source).to((xq, -1.0))
        d += elm.Ground().at((xq, -1.0))
        d += elm.Resistor().at((xq, 7.0)).to(q.drain)
        L.lab(d, (xq + 0.45, (7.0 + q.drain[1]) / 2), "R_H 560 Ω（2 W）\n= 加热器", fs_=10)
        d += elm.Vdd().at((xq, 7.0)).label("+9 V")
        d += elm.Arrow().at((xq + 2.9, 6.5)).to((xq + 2.9, 0.0)).color(C["cur"])
        L.lab(d, (xq + 3.1, 3.2), "导通时\n9 V ÷ 560 Ω = 16.07 mA\nP = 0.1446 W\n（只用了 2 W 额定的 7.2 %）", fs_=9.5, color=C["cur"])
        L.lab(d, (-2.6, -2.4), "Arduino 的 GND 必须和 9 V 电源的 − 极接在一起（共地），否则 D9 的 5 V 加不到栅—源之间。", fs_=9.5, color="#333333")
        schem.save_schem(d, P, "40_p2_3_heater.png")


def p2_4_cp_resp(O):
    """图 40-p2-4：恒功率（CP，占空固定 60 %）时风速台阶下的温差响应。"""
    r = O["cp"]
    t = r["t"]
    fig, (a0, a1) = plt.subplots(2, 1, figsize=(7, 4.0), sharex=True, gridspec_kw=dict(height_ratios=[1, 2.2]))
    a0.plot(t, r["v"], **LSk("cur"))
    a0.set_ylabel("风速 / m/s"); a0.set_ylim(-0.2, 2.5)
    a1.plot(t, r["dTm"], color="0.7", lw=0.8, label="Arduino 算出的温差（带 ADC 量化）")
    a1.plot(t, r["Tn"] - r["Ta"], **LSk("vin"), label="加热 NTC 真实温升")
    for (a, b, lab) in ((120, 300, "0→1"), (300, 480, "1→2"), (480, 660, "2→0")):
        td, y0, yf = S.t90(t, r["Tn"] - r["Ta"], a, b)
        a1.text(a + 5, 4.6, f"{lab} m/s\nt90 = {td:.1f} s", fontsize=8, va="top")
        fs.mark(a1, b - 10, yf, "{:.2f}", " K", dx=-45, dy=0.25)
        print(f"[图 40-p2-4] {lab}：t90 {td:.1f} s")
    for x in (120, 300, 480):
        a0.axvline(x, **LSk("ref")); a1.axvline(x, **LSk("ref"))
    fs.axlabels(a1, "时间", "s", "温差", "K")
    a1.set_ylim(0, 5); a1.set_xlim(0, 660)
    a1.legend(loc="lower left", fontsize=7.5)
    fs.save(fig, P, "40_p2_4_cp_resp.png")


def p2_5_pt100():
    """图 40-p2-5：工业版 PT100 电桥 + 仪表放大器（G = 100）。"""
    with schem.drawing(fontsize=11) as d:
        d += elm.Vdd().at((0, 6.5)).label("+2.5 V 基准")
        d += elm.Line().at((0, 6.5)).to((-2.0, 6.5)); d += elm.Line().at((0, 6.5)).to((2.0, 6.5))
        d += elm.Resistor().at((-2.0, 6.5)).to((-2.0, 3.5)); L.lab(d, (-2.45, 5.0), "R1 2.4 kΩ", ha="right", fs_=10)
        d += elm.Resistor().at((2.0, 6.5)).to((2.0, 3.5)); L.lab(d, (2.45, 5.0), "R2 2.4 kΩ", fs_=10)
        d += elm.Dot().at((-2.0, 3.5)); d += elm.Dot().at((2.0, 3.5))
        d += elm.Thermistor().at((-2.0, 3.5)).to((-2.0, 0.5)); L.lab(d, (-3.75, 2.0), "PT100\n（$R_T$）", ha="right", fs_=10)
        d += elm.Resistor().at((2.0, 3.5)).to((2.0, 0.5)); L.lab(d, (2.45, 2.0), "R3 100 Ω\n（= 0 °C 的 PT100）", fs_=10)
        d += elm.Line().at((-2.0, 0.5)).to((2.0, 0.5)); d += elm.Ground().at((0, 0.5))
        L.lab(d, (-1.85, 3.85), "A", fs_=10); L.lab(d, (2.15, 3.85), "B", fs_=10)
        op = elm.Opamp(leads=True).anchor("in1").at((5.2, 3.5))
        d += op
        d += elm.Line().at((2.0, 3.5)).to(op.in1)
        d += elm.Line().at((-2.0, 3.5)).to((-3.3, 3.5))
        d += elm.Line().at((-3.3, 3.5)).to((-3.3, -0.6))
        d += elm.Line().at((-3.3, -0.6)).to((op.in2[0] - 0.6, -0.6))
        d += elm.Line().at((op.in2[0] - 0.6, -0.6)).to((op.in2[0] - 0.6, op.in2[1])); d += elm.Line().at((op.in2[0] - 0.6, op.in2[1])).to(op.in2)
        L.lab(d, (op.out[0] - 1.6, op.out[1] + 1.4), "仪表放大器\nG = 100（30 节）", ha="center", fs_=9.5)
        d += elm.Line().at(op.out).to((op.out[0] + 1.0, op.out[1]))
        d += elm.Dot(open=True).at((op.out[0] + 1.0, op.out[1])).label("$V_o$", "right")
        L.lab(d, (-4.5, -1.6), "差压 $V_A - V_B$：25 °C 9.309 mV、50 °C 18.48 mV、100 °C 36.41 mV（放大 100 倍后 0.931 / 1.848 / 3.641 V）", fs_=9.5)
        L.lab(d, (-4.5, -2.3), "流过 PT100 的电流约 1 mA（0 °C 1.000 mA，100 °C 0.985 mA），自热只有几十 mK", fs_=9.5)
        schem.save_schem(d, P, "40_p2_5_pt100.png")
    for T in (25, 50, 100):
        vd, vo = S.bridge(T)
        print(f"[图 40-p2-5] {T} °C：{vd * 1e3:.3f} mV，{vo:.4f} V")


# ======================================================================
# page3
# ======================================================================
def p3_1_onoff(O):
    """图 40-p3-1：带回差的开关控温（主实验）。上：风速；中：温差与 1.8/2.2 K 两条门槛；下：加热开关与平均占空。"""
    r = O["onoff"]
    t = r["t"]
    fig, axs = plt.subplots(3, 1, figsize=(7, 5.4), sharex=True, gridspec_kw=dict(height_ratios=[0.8, 1.6, 1.6]))
    axs[0].plot(t, r["v"], **LSk("cur")); axs[0].set_ylabel("风速\n/ m/s"); axs[0].set_ylim(-0.2, 2.5)
    axs[1].plot(t, r["dTm"], **LSk("vin"), label="Arduino 算出的温差")
    axs[1].axhline(2.2, **LSk("ref")); axs[1].axhline(1.8, **LSk("ref"))
    axs[1].text(130, 2.66, "虚线：高于 2.2 K 关加热，低于 1.8 K 开加热", fontsize=8, color=C["ref"] if "ref" in C else "0.35")
    axs[1].set_ylabel("温差 / K"); axs[1].set_ylim(1.2, 2.8)
    axs[2].fill_between(t, 0, r["duty"] * 100, step="post", color=C["vout"], alpha=0.25, lw=0, label="加热开 / 关（100 % / 0 %）")
    axs[2].plot(t, r["avg"] * 100, color=C["third"], lw=1.8, label="最近 3 个开关周期的平均占空")
    for (lab, td, d0, df, per) in O["oo_steps"]:
        print(f"[图 40-p3-1] {lab}：{d0 * 100:.1f}→{df * 100:.1f} %，t90 {td:.1f} s，周期 {per:.1f} s")
    for x, (lab, td, d0, df, per) in zip((120, 300, 480), O["oo_steps"]):
        axs[2].text(x + 4, 104, f"→ {df * 100:.1f} %", fontsize=8, color=C["third"], va="bottom")
    axs[2].text(5, 104, f"{O['oo_steps'][0][2] * 100:.1f} %", fontsize=8, color=C["third"], va="bottom")
    for a in axs:
        for x in (120, 300, 480):
            a.axvline(x, **LSk("ref"))
    axs[2].set_ylim(0, 125)
    fs.axlabels(axs[2], "时间", "s", "占空", "%")
    axs[2].legend(loc="lower left", fontsize=7.5, ncol=2)
    axs[2].set_xlim(0, 660)
    fs.save(fig, P, "40_p3_1_onoff.png")


def p3_2_calib(O):
    """图 40-p3-2：标定。点 = 恒定风速下开关控温的平均占空；线 = 四点 / 五点三次多项式（占空 → 风速）。"""
    cal = O["oo_cal"]
    vs = np.array(sorted(cal)); ds = np.array([cal[v] for v in vs])
    dd = np.linspace(ds.min(), ds.max(), 300)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(dd * 100, np.polyval(O["poly_oo"], dd), **LSk("fb"), label="四点标定（0、1、2、2.5 m/s）")
    ax.plot(dd * 100, np.polyval(O["poly5"], dd), **LSk("vout"), label="五点标定（再加 0.5 m/s）")
    ax.plot(ds * 100, vs, "o", color="k", ms=5, label="仿真：恒定风速下的平均占空", zorder=5)
    for v in (0.5, 1.5):
        e4 = np.polyval(O["poly_oo"], cal[v]); e5 = np.polyval(O["poly5"], cal[v])
        print(f"[图 40-p3-2] 真值 {v}：四点 {e4:.3f}（{(e4 - v) / v * 100:+.1f} %），五点 {e5:.3f}（{(e5 - v) / v * 100:+.1f} %）")
    e4 = np.polyval(O["poly_oo"], cal[0.5])
    ax.annotate(f"真值 0.5 m/s\n四点标定读成 {e4:.2f} m/s（{(e4 - 0.5) / 0.5 * 100:+.0f} %）", xy=(cal[0.5] * 100, e4),
                xytext=(32, 1.4), fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.axvline(100, **LSk("ref")); ax.text(99, 0.1, "3 m/s：一直开着\n= 超出量程", ha="right", fontsize=8, color=C["bad"])
    fs.axlabels(ax, "平均占空", "%", "风速", "m/s")
    ax.set_xlim(25, 102); ax.set_ylim(-0.1, 3.1)
    ax.legend(loc="upper left", fontsize=7.5)
    fs.save(fig, P, "40_p3_2_calib.png")


def p3_3_amb(O):
    """图 40-p3-3：环境温度 300 s 时升 1 K，风速一直 1 m/s。有 / 无环境补偿的平均占空。"""
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for comp, ls, lab in ((True, "vout", "用环境 NTC 补偿（温差 = N1 − N2）"), (False, "bad", "不补偿（温差 = N1 − 开机时的环境温度）")):
        r = O[f"amb_oo_{comp}"]
        a, _ = S.cycle_duty(r["t"], r["duty"])
        st = LSk(ls)
        if ls == "bad":
            st = dict(color=C["bad"], lw=1.6)
        ax.plot(r["t"], a * 100, **st, label=lab)
        tail = np.nanmean(a[r["t"] > 540])
        fs.mark(ax, 590, tail * 100, "{:.1f}", " %", dx=-60, dy=4)
    fs.ref_v(ax, 300, "300 s：环境 25 → 26 °C")
    fs.axlabels(ax, "时间", "s", "平均占空", "%")
    ax.set_ylim(0, 90); ax.set_xlim(0, 600)
    ax.legend(loc="lower left", fontsize=8)
    fs.save(fig, P, "40_p3_3_amb.png")


def p3_4_pi(O):
    """图 40-p3-4：0→1 m/s 台阶，PI 三组参数与开关控温（平均占空）对比。"""
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for (Kp, Ti), ls in (((0.1, 10.0), "fb"), ((0.6, 10.0), "vout"), ((2.0, 10.0), "third")):
        r = O[f"pi_{Kp}_{Ti}"]
        ax.plot(r["t"], r["duty"] * 100, **LSk(ls), label=f"PI：K_p = {Kp}，T_i = {Ti:.0f} s（t90 = {O[f'pi_{Kp}_{Ti}_t90']:.1f} s）")
        print(f"[图 40-p3-4] Kp={Kp}：t90 {O[f'pi_{Kp}_{Ti}_t90']:.1f} s")
    r = S.simulate("ONOFF", t_end=300, vfun=lambda t: 0.0 if t < 120 else 1.0)
    a, _ = S.cycle_duty(r["t"], r["duty"])
    td, _, _ = S.t90(r["t"], np.nan_to_num(a), 120, 300)
    ax.plot(r["t"], a * 100, color="k", lw=1.4, label=f"开关控温的 3 周期平均（t90 = {td:.1f} s）")
    print(f"[图 40-p3-4] 开关控温 t90 {td:.1f} s")
    fs.ref_v(ax, 120, "120 s：风速 0 → 1 m/s")
    fs.axlabels(ax, "时间", "s", "占空", "%")
    ax.set_xlim(60, 300); ax.set_ylim(0, 105)
    ax.legend(loc="lower right", fontsize=7.5)
    fs.save(fig, P, "40_p3_4_pi.png")


def p3_5_cta_schem():
    """图 40-p3-5：工业模拟 CTA：运放直接驱动电桥顶端，热膜 R_s 是电桥的一臂。"""
    with schem.drawing(fontsize=11) as d:
        xt, yt = 0.0, 7.0
        d += elm.Line().at((-2.0, yt)).to((2.0, yt))
        d += elm.Dot().at((xt, yt))
        d += elm.Resistor().at((-2.0, yt)).to((-2.0, 4.0)); L.lab(d, (-2.45, 5.5), "R_A 20 Ω", ha="right", fs_=10)
        d += elm.Resistor().at((2.0, yt)).to((2.0, 4.0)); L.lab(d, (2.45, 5.5), "R_B 200 Ω", fs_=10)
        d += elm.Dot().at((-2.0, 4.0)); d += elm.Dot().at((2.0, 4.0))
        d += elm.Thermistor().at((-2.0, 4.0)).to((-2.0, 1.0)); L.lab(d, (-3.0, 2.5), "热膜 $R_s$\n20 Ω（20 °C）\n热到 +30 K\n= 22.31 Ω", ha="right", fs_=9.5)
        d += elm.Resistor().at((2.0, 4.0)).to((2.0, 1.0)); L.lab(d, (1.6, 2.5), "R_C 223.1 Ω\n= 10 × 22.31 Ω", ha="right", fs_=9.5)
        d += elm.Line().at((-2.0, 1.0)).to((2.0, 1.0)); d += elm.Ground().at((0, 1.0))
        op = elm.Opamp(leads=True).flip().anchor("in2").at((3.6, 4.0))
        d += op
        d += elm.Line().at((2.0, 4.0)).to(op.in2)
        d += elm.Line().at((-2.0, 4.0)).to((-4.8, 4.0))
        d += elm.Line().at((-4.8, 4.0)).to((-4.8, -0.2))
        d += elm.Line().at((-4.8, -0.2)).to((3.0, -0.2))
        d += elm.Line().at((3.0, -0.2)).to((3.0, op.in1[1])); d += elm.Line().at((3.0, op.in1[1])).to(op.in1)
        xo = op.out[0] + 0.5
        d += elm.Line().at(op.out).to((xo, op.out[1]))
        d += elm.Line().at((xo, op.out[1])).to((xo, 8.0))
        d += elm.Line().at((xo, 8.0)).to((xt, 8.0))
        d += elm.Line().at((xt, 8.0)).to((xt, yt))
        L.lab(d, (op.out[0] - 1.3, op.out[1] - 1.3), "运放（+ 在上）", ha="center", fs_=9)
        L.lab(d, (xt + 0.35, yt + 0.45), "电桥顶端电压 $V_{top}$ = 输出信号", fs_=10, color=C["third"])
        L.lab(d, (-5.6, -1.1), "风一吹 → $R_s$ 变冷、阻值变小 → 运放输入差变号 → 输出升高、加大加热 → $R_s$ 又回到 22.31 Ω。", fs_=9.5)
        L.lab(d, (-5.6, -1.8), "电桥平衡条件 $R_s/R_A = R_C/R_B$：热膜永远被拉回同一个温度，风越大 $V_{top}$ 越高。", fs_=9.5)
        schem.save_schem(d, P, "40_p3_5_cta_schem.png")


def p3_6_cta_spice():
    """图 40-p3-6：SPICE：同一只热膜，模拟 CTA 与恒流（CP）对风速台阶的反应。"""
    a = run_spice("40", "cta.cir", ["v(vel)", "v(top)", "v(th1)", "v(th2)"])
    t = a[:, 0] * 1e3
    m = (t > 400) & (t < 2000)
    fig, (a0, a1) = plt.subplots(2, 1, figsize=(7, 4.2), sharex=True)
    a0.plot(t[m], a[m, 2], **LSk("vout"), label="CTA：电桥顶端电压 $V_{top}$")
    a0b = a0.twinx()
    a0b.plot(t[m], a[m, 1], **LSk("cur")); a0b.set_ylabel("风速 / m/s", color=C["cur"]); a0b.set_ylim(-0.3, 4)
    a0.set_ylabel("$V_{top}$ / V"); a0.set_ylim(1.8, 3.6)
    a1.plot(t[m], a[m, 3], **LSk("vout"), label="CTA 热膜温升（几乎不变）")
    a1.plot(t[m], a[m, 4], **LSk("vin"), label="恒流 CP 热膜温升")
    a1.set_ylabel("温升 / K"); a1.set_ylim(0, 35)
    fs.axlabels(a1, "时间", "ms")
    a0.legend(loc="center right", fontsize=7.5); a1.legend(loc="lower right", fontsize=7.5)
    i = np.searchsorted(t, 990)
    fs.mark(a0, t[i], a[i, 2], "{:.3f}", " V", dx=-120, dy=0.12)
    fs.mark(a1, t[i], a[i, 4], "{:.2f}", " K", dx=-120, dy=2.5)
    fs.mark(a1, t[i], a[i, 3], "{:.2f}", " K", dx=-120, dy=3.5)
    fs.save(fig, P, "40_p3_6_cta_spice.png")


# ======================================================================
# page4：面包板（两段）+ 对照原理图
# ======================================================================
def _ntc_body(bb, name):
    """在 two() 画的元件上盖一个黑色小珠子，表示 NTC（环氧珠形）。"""
    (x1, y1), (x2, y2) = bb.xy(bb.pins[name + ".1"]), bb.xy(bb.pins[name + ".2"])
    bb.ax.add_patch(mpatches.Ellipse(((x1 + x2) / 2, (y1 + y2) / 2), 0.9, 0.6, fc="#222222", ec="k", zorder=7))


def bb40(stage):
    """stage 1：两路 NTC 分压（A0 加热 NTC，A1 环境 NTC）；stage 2：再加 IRLZ44N + 560 Ω 加热器（9 V）。"""
    bb = Breadboard(ncol=30, rails=dict(tp=("+5 V", "pos"), tn=("0 V", "gnd"), bp=("0 V", "gnd"),
                                        bn=("+9 V" if stage == 2 else "+9 V（第 2 段才接）", "pos")),
                    figsize=(11, 6.6))
    bb.ax.set_ylim(-6.6, 14.8)
    HOP_TT = [BB_RAIL_Y["tn"] - 0.32, BB_RAIL_Y["tp"] + 0.32]
    HOP_B = [BB_RAIL_Y["bp"] + 0.32, BB_RAIL_Y["bn"] - 0.32]
    bb.wire(bb.ext((-2.4, 11.4), "Arduino 5V", "pos"), "tp1", "pos")
    bb.wire(bb.ext((-2.4, 10.4), "Arduino GND", "gnd"), "tn1", "gnd")
    bb.wire("tn2", "bp2", "gnd")                                   # 上下 0 V 轨连通（共地）
    # 环境 NTC 分压 → A1（第 3～11 列）
    bb.wire("a3", "tp3", "pos")
    bb.two("RS2", "b3", "b7", "R", "R_S2 10k", lpos=(0, -0.62))
    bb.two("N2", "c7", "c11", "R", "N2 环境 NTC", lpos=(0, -0.7)); _ntc_body(bb, "N2")
    bb.wire("a11", "tn11", "gnd")
    bb.wire("a7", bb.ext((7.0, 13.7), "", "sig"), "sig", hops=HOP_TT)
    bb.ax.text(7.4, 13.7, "→ Arduino A1", fontsize=8, color=BB_WIRE["sig"], va="center")
    # 加热 NTC 分压 → A0（第 17～25 列）
    bb.wire("a17", "tp17", "pos")
    bb.two("RS1", "b17", "b21", "R", "R_S1 10k", lpos=(0, -0.62))
    bb.two("N1", "c21", "c25", "R", "N1 加热 NTC", lpos=(0, -0.7)); _ntc_body(bb, "N1")
    bb.wire("a25", "tn25", "gnd")
    bb.wire("a21", bb.ext((21.0, 13.7), "", "sig"), "sig", hops=HOP_TT)
    bb.ax.text(21.4, 13.7, "→ Arduino A0", fontsize=8, color=BB_WIRE["sig"], va="center")
    assert bb.connected("RS2.1", "tp1") and bb.connected("RS2.2", "N2.1") and bb.connected("N2.2", "tn1")
    assert bb.connected("RS1.1", "tp1") and bb.connected("RS1.2", "N1.1") and bb.connected("N1.2", "tn1")
    assert bb.connected("tn1", "bp1") and not bb.connected("tp1", "tn1") and not bb.connected("RS1.2", "RS2.2")
    bb.probe("e7", "① A1 分压", dx=0.3, dy=-0.95)
    bb.probe("e21", "② A0 分压", dx=0.3, dy=-0.95)
    if stage == 1:
        bb.note(9.0, -5.4, "N2 用两根约 15 cm 的导线引到风扇上风处，离加热器 ≥ 5 cm；先不插第 2 段的元件", fontsize=8, ha="center")
    else:
        bb.wire(bb.ext((-2.4, -2.6), "9 V 电源 −", "gnd"), "bp1", "gnd")
        bb.wire(bb.ext((-2.4, -3.6), "9 V 电源 +", "pos"), "bn1", "pos")
        bb.multi("Q1", {"G": "f27", "D": "f28", "S": "f29"}, "IRLZ44N", w=2.8, h=0.7, at=(28.0, 4.0))
        bb.wire(bb.ext((19.0, -5.8), "Arduino D9 →", "sig", dx=-0.45), "j19", "sig", hops=HOP_B)
        bb.two("RG", "g19", "g23", "R", "R_G 100", lpos=(0, 0.6))
        bb.wire("h23", "h27", "sig")
        bb.two("RPD", "j27", "bp26", "R", None)
        bb.ax.text(27.35, -1.2, "R_PD\n100k", fontsize=7.5, ha="left", va="center")
        bb.two("RH", "i21", "i25", "R", None)
        xl, yl = bb.xy("i20")   # 标签放在 R_H 左边空着的 i17–i20，不压橙色虚线框和 h23–h27 绿线
        bb.ax.text(xl + 0.2, yl, "R_H 560 Ω 2 W", fontsize=7.5, ha="right", va="center", zorder=9,
                   bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none"))
        bb.wire("j21", "bn22", "pos", hops=[BB_RAIL_Y["bp"] + 0.32])
        bb.wire("j25", "j28", "sig", bend=-0.0) if False else bb.wire("g25", "g28", "sig", bend=0.7)
        bb.wire("j29", "bp29", "gnd")
        # 只圈 N1 头部和 R_H 本体（不圈 R_G、引脚）：两者用绝缘的 Kapton 胶带包在一起
        (xn, yn), (xr, yr) = bb.xy("c23"), bb.xy("i23")
        for (xc, yc) in ((xn, yn), (xr, yr)):
            bb.ax.add_patch(mpatches.FancyBboxPatch((xc - 1.0, yc - 0.42), 2.0, 0.84, boxstyle="round,pad=0.08", fc="none",
                                                    ec=C["bad"], lw=1.2, ls="--", zorder=8))
        bb.ax.annotate("", xy=(xr + 1.05, yr + 0.2), xytext=(xn + 1.05, yn - 0.2),
                       arrowprops=dict(arrowstyle="<->", color=C["bad"], lw=1.0, ls="--"), zorder=8)
        bb.ax.text(xn - 4.6, (yn + yr) / 2 + 0.25, "N1 头部弯过来贴 R_H 本体，\n用 Kapton 绝缘胶带只包本体，不碰引脚", fontsize=7.2,
                   color=C["bad"], ha="right", va="center", zorder=9, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none"))
        assert bb.connected("RG.2", "Q1.G") and bb.connected("RPD.1", "Q1.G") and bb.connected("RPD.2", "tn1")
        assert bb.connected("RH.2", "Q1.D") and bb.connected("RH.1", "bn1") and bb.connected("Q1.S", "tn1")
        assert not bb.connected("bn1", "tn1") and not bb.connected("bn1", "tp1") and not bb.connected("Q1.D", "Q1.G")
        bb.probe("h28", "③ 漏极 D", dx=0.3, dy=-0.9)
        bb.probe("j23", "④ 栅极 G", dx=0.42, dy=-0.22)   # j23 空着，和 g23/h23 同一节点；i23 被 R_H 本体盖住
    bb.legend(("pos", "gnd", "sig"), y=0.02)
    print(f"40 p4 面包板第 {stage} 段：连接检查通过，占用 {len(bb.used)} 个孔")
    return bb


def p4_2_schem_lab():
    """图 40-p4-2：第 1 段（两路 NTC 分压）对照原理图。"""
    with schem.drawing(fontsize=11) as d:
        for x, rs, n, col_rs, col_n, pin, pr, ttl in ((0.0, "R_S2 10k", "N2 环境 NTC", "b3–b7", "c7–c11", "A1", "①", "环境（上风处）"),
                                                       (7.0, "R_S1 10k", "N1 加热 NTC", "b17–b21", "c21–c25", "A0", "②", "加热（贴着 R_H）")):
            d += elm.Vdd().at((x, 7)).label("+5 V 轨")
            d += elm.Resistor().at((x, 7)).to((x, 4))
            L.lab(d, (x + 0.45, 5.5), rs, fs_=10); L.colnote(d, (x - 0.45, 5.5), col_rs, "left", ofst=0.0)
            d += elm.Dot().at((x, 4))
            d += elm.Thermistor().at((x, 4)).to((x, 1))
            L.lab(d, (x + 0.5, 2.5), n, fs_=10); L.colnote(d, (x - 0.45, 2.5), col_n, "left", ofst=0.0)
            d += elm.Ground().at((x, 1))
            d += elm.Line().at((x, 4)).to((x + 2.4, 4)).color(C["fb"]).linewidth(2.0)
            d += elm.Dot(open=True).at((x + 2.4, 4)).label(f"Arduino {pin}", "right")
            L.probe(d, (x, 4), pr, dx=-0.9, dy=0.6)
            # 选装 100 nF：分压点到 0 V（灰色点线），A0/A1 读数跳字时才加
            xc = x + 1.3
            d += elm.Dot().at((xc, 4)).color("#737373")
            d += elm.Capacitor().at((xc, 4)).to((xc, 2.0)).color("#737373").linestyle(":")
            d += elm.Ground().at((xc, 2.0)).color("#737373")
            L.lab(d, (xc + 0.3, 3.0), "C 100 nF\n（选装）", fs_=8.5, color="#666666")
            L.colnote(d, (xc + 0.3, 2.2), f"{'e7' if pin == 'A1' else 'e21'}→0 V 轨", "right", ofst=0.0)
            L.title(d, (x + 1.0, 8.4), ttl)
        L.note(d, (-2.5, -0.4), "灰色小字 = 面包板孔位；黄色圆圈 = 测量点（黑表笔接 0 V 轨）；绿线 = 去 Arduino 的信号线（a7、a21 引出）。")
        L.note(d, (-2.5, -1.0), "上下两条 0 V 轨由第 2 列的黑线连通；+5 V、0 V 都来自 Arduino（USB 供电）。25 °C 时①②都应约 2.50 V。")
        L.note(d, (-2.5, -1.6), "灰色点线的 100 nF 是选装件：A0/A1 读数跳字时才加，加之前先断电（拔 9 V 电池扣和 USB）。")
        schem.save_schem(d, P, "40_p4_2_schem_lab.png")


def p4_4_schem_lab():
    """图 40-p4-4：第 2 段（加热器 + 开关管）对照原理图，N1 分压也画出来表示热耦合。"""
    with schem.drawing(fontsize=11) as d:
        xg, yg = 3.0, 2.0
        d += elm.Dot(open=True).at((-1.5, yg)).label("Arduino D9", "left")
        d += elm.Line().at((-1.5, yg)).to((-0.5, yg)).color(C["fb"]).linewidth(2.0)
        L.colnote(d, (-1.0, yg - 0.3), "j19", "bottom", ofst=0.0)
        d += elm.Resistor().at((-0.5, yg)).to((xg, yg))
        L.lab(d, (1.25, yg + 0.55), "R_G 100 Ω", ha="center", fs_=10); L.colnote(d, (1.25, yg - 0.45), "g19–g23", "bottom", ofst=0.0)
        d += elm.Dot().at((xg, yg))
        L.probe(d, (xg, yg), "④", dx=0.0, dy=1.0)
        L.colnote(d, (xg + 0.55, yg + 1.0), "量 j23", "right", ofst=0.0)
        d += elm.Resistor().at((xg, yg)).to((xg, -1.0))
        L.lab(d, (xg - 0.45, 0.5), "R_PD 100k", ha="right", fs_=10); L.colnote(d, (xg - 0.45, -0.1), "j27–0 V 轨", "left", ofst=0.0)
        d += elm.Ground().at((xg, -1.0))
        q = elm.NFet().theta(0).reverse().anchor("gate").at((xg + 1.4, yg))
        d += q
        d += elm.Line().at((xg, yg)).to(q.gate)
        L.colnote(d, (xg + 0.75, yg - 0.35), "绿线 h23→h27", "bottom", ofst=0.0)
        xq = q.drain[0]
        L.lab(d, (xq + 0.5, yg), "Q1 IRLZ44N\nG f27、D f28、S f29", fs_=9.5)
        d += elm.Line().at(q.source).to((xq, -1.0)); d += elm.Ground().at((xq, -1.0))
        L.colnote(d, (xq + 0.3, -0.6), "j29 → 0 V 轨", "right", ofst=0.0)
        yd = q.drain[1] + 0.8
        d += elm.Line().at(q.drain).to((xq, yd)); d += elm.Dot().at((xq, yd))
        L.probe(d, (xq, yd), "③", dx=-1.0, dy=0.0)
        d += elm.Resistor().at((xq, 7.5)).to((xq, yd))
        L.lab(d, (xq + 0.45, (7.5 + yd) / 2), "R_H 560 Ω 2 W", fs_=10)
        L.colnote(d, (xq + 0.45, (7.5 + yd) / 2 - 0.6), "i21–i25；g25→g28 接 D", "right", ofst=0.0)
        d += elm.Vdd().at((xq, 7.5)).label("+9 V 轨（j21）")
        # N1 分压（热耦合）
        xn = xq + 5.2
        d += elm.Vdd().at((xn, 7.5)).label("+5 V")
        d += elm.Resistor().at((xn, 7.5)).to((xn, 5.0)); L.lab(d, (xn + 0.45, 6.25), "R_S1 10k", fs_=10)
        d += elm.Dot().at((xn, 5.0))
        d += elm.Thermistor().at((xn, 5.0)).to((xn, 2.5)); L.lab(d, (xn + 0.5, 3.75), "N1", fs_=10)
        d += elm.Ground().at((xn, 2.5))
        d += elm.Line().at((xn, 5.0)).to((xn + 1.8, 5.0)).color(C["fb"]).linewidth(2.0)
        d += elm.Dot(open=True).at((xn + 1.8, 5.0)).label("A0", "right")
        L.probe(d, (xn, 5.0), "②", dx=-0.9, dy=0.5)
        d += elm.Line().at((xq + 0.9, 4.6)).to((xn - 0.6, 3.75)).color(C["bad"]).linestyle("--")
        L.lab(d, ((xq + xn) / 2 + 0.4, 3.0), "胶带包在一起\n（热量从 R_H 传到 N1）", ha="center", fs_=9, color=C["bad"])
        L.note(d, (-3.5, -2.3), "9 V 电源 − 接下方 0 V 轨第 1 列，+ 接最下方 +9 V 轨第 1 列；Arduino GND 经上 0 V 轨、第 2 列黑线与它相连（共地）。")
        L.note(d, (-3.5, -2.9), "③ 加热开时约 0.3 mV、关时约 9 V；④ 开时约 5 V、关时 0 V。N2（环境）一路同图 40-p4-2，没有画出。")
        schem.save_schem(d, P, "40_p4_4_schem_lab.png")


if __name__ == "__main__":
    O = sim_all()
    p1_1_wind(O); p1_2_king(O); p1_3_rt(); p1_4_blocks()
    p2_1_ntc_div(); p2_2_ntc_curve(); p2_3_heater(); p2_4_cp_resp(O); p2_5_pt100()
    p3_1_onoff(O); p3_2_calib(O); p3_3_amb(O); p3_4_pi(O); p3_5_cta_schem(); p3_6_cta_spice()
    for st, name in ((1, "40_p4_1_breadboard_ntc.png"), (2, "40_p4_3_breadboard_heater.png")):
        bb = bb40(st)
        fs.save(bb.fig, P, name)
        plt.close("all")
    p4_2_schem_lab(); p4_4_schem_lab()
    print("40_figs OK")
