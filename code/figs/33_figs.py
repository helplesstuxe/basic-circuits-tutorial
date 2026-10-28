"""33 带通与 50 Hz 陷波：全部配图。
运行（仓库根目录）：/workspace/circuits-venv/bin/python code/figs/33_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。数值函数在 code/33_sim.py，面包板小工具在 code/33_bbkit.py。
"""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import lab_schem as ls
import figstyle as fs
from batt_pm import pm as bat_pm        # 电池旁的 + / − 小字（长线 = +）
import numpy as np
import matplotlib.pyplot as plt


def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, "..", fn))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


sim = _load("sim33", "33_sim.py")
bbk = _load("bbkit", "33_bbkit.py")
N = "33"
C, LS = fs.C, fs.LS
R1, R2, R3, CB = sim.R1_BP, sim.R2_BP, sim.R3_BP, sim.C_BP
F0, Q, A0, BW = sim.mfb_params(R1, R2, R3, CB)
RT, CT = sim.R_TT, sim.C_TT
FT = sim.twint_f0(RT, CT)
print(f"[数值] MFB 实验值：f0 = {F0:.1f} Hz，Q值 = {Q:.2f}，中心增益 = {A0:.3f}，带宽 = {BW:.1f} Hz")
print(f"[数值] 双 T：f0 = {FT:.2f} Hz")
assert abs(F0 - 1004.4) < 0.5 and abs(Q - 5.05) < 0.01 and abs(FT - 48.23) < 0.01


def axl(ax, xl, yl):
    """轴标签已写成「量 / 单位」格式。"""
    ax.set_xlabel(xl)
    if yl:
        ax.set_ylabel(yl)


# =====================================================================
# 图 33-p1-1 混着 50 Hz 交流声、噪声和漂移的信号，经过 1 kHz 带通
# =====================================================================
def p1_1():
    dt = 5e-6
    t = np.arange(0, 0.08, dt)
    rng = np.random.default_rng(3)
    sig = 0.2 * np.sin(2 * np.pi * 1000 * t)
    hum = 1.0 * np.sin(2 * np.pi * 50 * t)
    drift = 0.6 * t / 0.08
    noise = 0.3 * rng.standard_normal(len(t))
    vi = sig + hum + drift + noise
    vo = sim.mfb_ode_wave(vi, dt, R1, R2, R3, CB)
    k0 = int(0.06 / dt)
    vo_t, t_t = vo[k0:], t[k0:]
    # 输出里信号部分的大小：用同一算法只算信号
    vs = sim.mfb_ode_wave(sig, dt, R1, R2, R3, CB)[k0:]
    err = np.std(vo_t - vs)
    print(f"[数值] 图 33-p1-1：输入 = 1 kHz 0.20 V + 50 Hz 1.0 V + 0.6 V 漂移 + 噪声（均方根 0.3 V）")
    print(f"[数值]   输入峰峰值约 {np.ptp(vi[k0:]):.2f} V；输出里 1 kHz 成分幅度 {np.ptp(vs)/2:.3f} V，其余杂波均方根 {err:.3f} V")
    assert np.ptp(vs) / 2 > 0.19 and err < 0.03
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7, 5.6), sharex=True)
    ms = (t_t - 0.06) * 1e3
    a1.plot(ms, vi[k0:], color=C["vin"], lw=0.8, label="输入：信号 + 交流声 + 噪声 + 漂移")
    a1.set_ylim(-2.2, 3.2)
    a1.legend(loc="upper right", fontsize=9)
    axl(a1, "", "电压 / V")
    a1.set_title("图 33-p1-1 上：带通的输入（看不出 1 kHz 信号）", fontsize=10.5)
    a2.plot(ms, vo_t, color=C["vout"], lw=1.4, label="带通输出")
    a2.plot(ms, vs, color=C["good"], ls="--", lw=1.0, label="只有 1 kHz 信号时的输出")
    a2.set_ylim(-0.32, 0.42)
    a2.legend(loc="upper right", fontsize=9, ncol=2)
    axl(a2, "时间 / ms", "电压 / V")
    a2.set_title(f"下：带通输出（1 kHz 成分 {np.ptp(vs)/2:.2f} V，杂波只剩约 {err:.3f} V）", fontsize=10.5)
    fs.save(fig, N, "33_p1_1_noisy.png")


# =====================================================================
# 图 33-p1-2 Q值 1 / 5 / 20 三条带通曲线
# =====================================================================
def p1_2():
    f = np.logspace(2, 4, 1500)
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    styles = [(1, C["third"], "-."), (5, C["vout"], "-"), (20, C["fb"], "--")]
    for q, col, l in styles:
        m = sim.bp_mag(f, 1000, q, 1.0)
        lo, hi = sim.f3db(f, m, 1.0)
        print(f"[数值] 图 33-p1-2：Q值 {q:>2d}：降到 0.707 的两点 {lo:.0f} Hz、{hi:.0f} Hz，带宽 {hi-lo:.0f} Hz（= 1000/{q}）")
        assert abs((hi - lo) - 1000 / q) < 0.02 * 1000 / q
        ax.plot(f, m, color=col, ls=l, lw=1.8, label=f"Q值 = {q}：带宽 {hi-lo:.0f} Hz")
    m5 = sim.bp_mag(f, 1000, 5, 1.0)
    lo, hi = sim.f3db(f, m5, 1.0)
    ax.axhline(1 / np.sqrt(2), color=C["ref"], ls=":", lw=1)
    ax.text(105, 0.73, "0.707（−3 dB）", color=C["ref"], fontsize=9)
    ax.annotate("", xy=(lo, 0.62), xytext=(hi, 0.62), arrowprops=dict(arrowstyle="<->", color=C["vout"]))
    ax.annotate(f"Q值 5 的带宽：{lo:.0f}～{hi:.0f} Hz", (hi, 0.62), xytext=(2200, 0.5), fontsize=9, color=C["vout"],
                arrowprops=dict(arrowstyle="-", color=C["vout"], lw=0.7))
    ax.set_xscale("log")
    ax.set_ylim(0, 1.12)
    ax.legend(loc="upper right", fontsize=9)
    axl(ax, "频率 / Hz（对数刻度）", "输出 ÷ 输入")
    ax.set_title("图 33-p1-2 中心都在 1 kHz：Q值越大，通带越窄", fontsize=11)
    fs.save(fig, N, "33_p1_2_q_curves.png")


# =====================================================================
# 图 33-p1-3 带通去不掉落在带内的 50 Hz：陷波专门挖掉它
# =====================================================================
def p1_3():
    f = np.logspace(np.log10(5), np.log10(5000), 2000)
    m = sim.twint_mag(f, FT)
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.axvspan(20, 2000, color=C["hi"], alpha=0.25, lw=0)
    ax.text(30, 1.07, "假设：有用信号可能出现在 20 Hz～2 kHz", fontsize=9)
    ax.plot(f, m, color=C["vout"], lw=1.8, label="双 T 陷波（33 kΩ、100 nF）")
    for fx in (50, 1000):
        mx = sim.twint_mag(fx, FT)
        print(f"[数值] 图 33-p1-3：双 T 在 {fx} Hz：{mx:.3f}")
        ax.plot([fx], [mx], "o", color=C["good"], ms=5)
        txt = f"{fx} Hz：{mx:.3f}" + ("\n（交流声只剩约 2%）" if fx == 50 else "")
        ax.annotate(txt, (fx, mx), xytext=(12, 25) if fx == 50 else (-40, -45), textcoords="offset points",
                    fontsize=9, arrowprops=dict(arrowstyle="-", color="0.4", lw=0.7))
    ax.set_xscale("log")
    ax.set_ylim(0, 1.15)
    ax.legend(loc="lower right", fontsize=9)
    axl(ax, "频率 / Hz（对数刻度）", "输出 ÷ 输入")
    ax.set_title(f"图 33-p1-3 陷波：只在 {FT:.0f} Hz 附近挖一个坑", fontsize=11)
    assert sim.twint_mag(50, FT) < 0.02 and sim.twint_mag(1000, FT) > 0.98
    fs.save(fig, N, "33_p1_3_notch_band.png")


# =====================================================================
# 图 33-p1-4 方波进带通，出来接近正弦
# =====================================================================
def p1_4():
    dt = 2e-6
    t = np.arange(0, 0.05, dt)
    vi = 0.3 * np.sign(np.sin(2 * np.pi * 1000 * t + 1e-9))
    vo = sim.mfb_ode_wave(vi, dt, R1, R2, R3, CB)
    k0 = int(0.045 / dt)
    amp = np.ptp(vo[k0:]) / 2
    print(f"[数值] 图 33-p1-4：±0.30 V、1 kHz 方波 → 带通输出幅度 {amp:.3f} V（方波里 1 kHz 成分 4/π×0.30 = {4/np.pi*0.3:.3f} V）")
    assert abs(amp - 4 / np.pi * 0.3 * A0) < 0.03
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    ms = (t[k0:] - 0.045) * 1e3
    ax.plot(ms, vi[k0:], color=C["vin"], lw=1.5, label="输入：1 kHz 方波 ±0.30 V")
    ax.plot(ms, vo[k0:], color=C["vout"], lw=1.8, label=f"输出：近似正弦，幅度 {amp:.2f} V")
    ax.set_ylim(-0.55, 0.62)
    ax.legend(loc="upper right", fontsize=9, ncol=2)
    axl(ax, "时间 / ms", "电压 / V")
    ax.set_title("图 33-p1-4 方波进 1 kHz 带通：棱角被削掉，只剩 1 kHz 的正弦", fontsize=11)
    fs.save(fig, N, "33_p1_4_square_sine.png")


# =====================================================================
# 原理图：中点参考 V_MID、MFB 带通、双 T
# =====================================================================
def _vmid(d, pt, dy=-0.7, txt="V_MID"):
    """中点参考 V_MID 画成「空心圆点 + 文字」，不画接地符号（它不是 0 V）。"""
    x, y = pt
    d += elm.Line().at(pt).to((x, y + dy))
    d += elm.Dot(open=True).at((x, y + dy))
    ls.lab(d, (x, y + dy - 0.42), txt, ha="center", fs_=10, color=C["third"])


def _vg(d, x0=0.0, holes=False):
    """电池 + Cd 去耦 + RA/RB 分压（分压点 D）+ CM + 运放 B 跟随器 → 中点参考 V_MID。返回运放。holes=True 时写面包板孔位。"""
    yt, yb, ym = 4.0, -1.5, 1.25
    xa, xc, xo = x0 + 3.4, x0 + 5.4, x0 + 7.6
    d += (bt := elm.Battery().endpoints((x0, yb), (x0, yt)).reverse()); bat_pm(d, bt, plus_toward=(x0, yt), side=-1)
    ls.lab(d, (x0 - 0.5, (yt + yb) / 2), "9 V\n电池", ha="right", fs_=10)
    d += elm.Line().at((x0, yt)).to((xo + 1.0, yt))
    d += elm.Line().at((x0, yb)).to((xo + 1.0, yb))
    ls.lab(d, (x0 + 0.1, yt + 0.35), "+9 V" + (" 轨" if holes else ""), fs_=10)
    xd = x0 + 1.2
    d += elm.Capacitor().endpoints((xd, yt), (xd, yb))
    d += elm.Dot().at((xd, yt)); d += elm.Dot().at((xd, yb))
    ls.lab(d, (xd + 0.3, ym), "Cd 100 nF", fs_=9.5)
    if holes:
        ls.colnote(d, (xd + 0.3, ym - 0.5), "T+27–T−27", "right", ofst=0.0)
    d += elm.Ground().at((x0, yb))
    ls.lab(d, (x0 + 0.25, yb - 0.45), "GND" + (" 轨" if holes else "（0 V）"), fs_=10)
    for pt in ((xa, yt), (xa, yb), (xa, ym), (xc, ym), (xc, yb)):
        d += elm.Dot().at(pt)
    d += elm.Resistor().endpoints((xa, yt), (xa, ym))
    d += elm.Resistor().endpoints((xa, ym), (xa, yb))
    ls.lab(d, (xa - 0.45, (yt + ym) / 2), "RA\n10 kΩ", ha="right", fs_=10)
    ls.lab(d, (xa - 0.45, (ym + yb) / 2), "RB\n10 kΩ", ha="right", fs_=10)
    ls.lab(d, (xa + 0.15, ym + 0.3), "D", fs_=10)
    d += elm.Line().at((xa, ym)).to((xc, ym))
    d += elm.Capacitor(polar=True).endpoints((xc, ym), (xc, yb))
    ls.lab(d, (xc + 0.45, ym - 1.1), "CM\n10 µF", fs_=10)
    if holes:
        ls.colnote(d, (xa + 0.4, (yt + ym) / 2 + 0.2), "c25–c21", "right", ofst=0.0)
        ls.colnote(d, (xa + 0.4, (ym + yb) / 2 - 0.3), "a21→GND", "right", ofst=0.0)
        ls.colnote(d, (xc + 0.45, ym - 1.85), "d21(+)–d23", "right", ofst=0.0)
    d += elm.Line().at((xc, ym)).to((xo, ym))
    opb = elm.Opamp(leads=True).right().anchor("in2").at((xo, ym))
    d += opb
    b = opb.absanchors
    xl, xr, ytop = b["in1"][0] - 0.4, b["out"][0] + 0.4, b["in1"][1] + 0.9
    for p_, q_ in (((b["in1"]), (xl, b["in1"][1])), ((xl, b["in1"][1]), (xl, ytop)), ((xl, ytop), (xr, ytop)),
                   ((xr, ytop), (xr, b["out"][1])), ((xr, b["out"][1]), b["out"])):
        d += elm.Line().at(p_).to(q_).color(ls.TEAL if holes else "black").linewidth(1.8 if holes else 1.5)
    d += elm.Line().at(b["vd"]).to((b["vd"][0], yt))
    d += elm.Dot().at((b["vd"][0], yt))
    d += elm.Line().at(b["vs"]).to((b["vs"][0], yb))
    d += elm.Dot().at((b["vs"][0], yb))
    ls._pin(d, b["in2"], "5", dx=-0.2, dy=-0.25)
    ls._pin(d, b["in1"], "6", dx=-0.2, dy=0.25)
    ls._pin(d, b["out"], "7", dx=0.15, dy=0.25)
    ls._pin(d, b["vd"], "8", dx=0.25, dy=0.3)
    ls._pin(d, b["vs"], "4", dx=0.25, dy=-0.3)
    xvg = xr + 1.4
    d += elm.Line().at((xr, b["out"][1])).to((xvg, b["out"][1])).color(C["third"] if holes else "black").linewidth(1.8 if holes else 1.5)
    d += elm.Dot().at((xr, b["out"][1]))
    d += elm.Dot(open=True).at((xvg, b["out"][1]))
    ls.lab(d, (xvg + 0.25, b["out"][1]), "V_MID\n≈ 4.5 V", fs_=10, color=C["third"])
    if holes:
        ls.colnote(d, ((xl + b["vd"][0]) / 2, ytop + 0.2), "c16–c17", "top", ofst=0.0)
        ls.colnote(d, (b["vd"][0] + 0.2, yt - 0.3), "a15", "right", ofst=0.0)
        ls.colnote(d, (b["vs"][0] + 0.45, yb + 0.35), "j18", "right", ofst=0.0)
        ls.colnote(d, ((xc + xo) / 2 - 0.2, ym - 0.3), "b18→b21", "bottom", ofst=0.0)
        ls.colnote(d, (xr + 0.1, b["out"][1] - 0.75), "d16→V_MID 轨", "right", ofst=0.0)
    else:
        ls.lab(d, (b["vs"][0] + 0.4, b["vs"][1] - 1.0), "运放 B（跟随器）", ha="left", fs_=9.5, color=ls.GRAY)
    return opb


def p2_1():
    d = drawing(fontsize=11)
    _vg(d)
    ls.note(d, (-1.5, -3.3), "右边空心圆点 V_MID = 中点参考（约 4.5 V）：本节所有标 V_MID 的点都接到这里。它不是 0 V，不能和 GND 接在一起。")
    save_schem(d, N, "33_p2_1_schem_vmid.png")
    print("[图 33-p2-1] RA = RB = 10 kΩ 在 D 点把 9 V 分成一半，CM 10 µF 稳住，运放 B 跟随输出 V_MID ≈ 4.5 V；Cd 100 nF 电源去耦")


def _mfb(d, x0=0.0, y0=0.0, vals=("R1 82 kΩ", "R2 160 kΩ", "R3\n1.6 kΩ", "C1 10 nF", "C2 10 nF")):
    """MFB 带通：信号源（下端接 V_MID）→ R1 → A；R3 A→V_MID；C1 A→N；C2 A→输出；R2 N→输出；同相端接 V_MID。"""
    A = (x0 + 3, y0); Nn = (x0 + 6, y0)
    d += elm.SourceSin().endpoints((x0, y0 - 2.4), (x0, y0))
    ls.lab(d, (x0 - 0.6, y0 - 1.2), "手机\n音频", ha="right", fs_=10)
    _vmid(d, (x0, y0 - 2.4))
    d += elm.Resistor().endpoints((x0, y0), A).label(vals[0], "top")
    d += elm.Dot().at(A)
    d += elm.Resistor().endpoints(A, (A[0], y0 - 2.4))
    ls.lab(d, (A[0] + 0.45, y0 - 1.0), vals[2], fs_=10)
    _vmid(d, (A[0], y0 - 2.4))
    d += elm.Capacitor().endpoints(A, Nn).label(vals[3], "bottom")
    d += elm.Dot().at(Nn)
    d += elm.Line().at(Nn).to((Nn[0] + 0.9, y0))
    op = elm.Opamp(leads=True).right().anchor("in1").at((Nn[0] + 0.9, y0))
    d += op
    a = op.absanchors
    d += elm.Line().at(a["in2"]).to((a["in2"][0] - 0.5, a["in2"][1]))
    _vmid(d, (a["in2"][0] - 0.5, a["in2"][1]), dy=-0.9)
    xo = a["out"][0] + 0.6
    d += elm.Line().at(a["out"]).to((xo + 1.2, a["out"][1]))
    d += elm.Dot().at((xo, a["out"][1]))
    yr2, yc2 = y0 + 1.8, y0 + 3.4
    d += elm.Line().at(Nn).to((Nn[0], yr2))
    d += elm.Resistor().endpoints((Nn[0], yr2), (xo, yr2)).label(vals[1], "top")
    d += elm.Line().at((xo, yr2)).to((xo, a["out"][1]))
    d += elm.Line().at(A).to((A[0], yc2))
    d += elm.Capacitor().endpoints((A[0], yc2), (xo, yc2)).label(vals[4], "top")
    d += elm.Line().at((xo, yc2)).to((xo, yr2))
    d += elm.Dot().at((xo, yr2))
    return op, dict(vin=(x0, y0), A=A, N=Nn, out=(xo + 1.2, a["out"][1]), xo=xo)


def p2_2():
    d = drawing(fontsize=11)
    op, p = _mfb(d)
    ls.lab(d, (p["A"][0] - 0.15, p["A"][1] + 0.4), "A", ha="right", fs_=11)
    ls.lab(d, (p["N"][0] - 0.15, p["N"][1] + 0.4), "P 点", ha="right", fs_=11)
    d += elm.Dot(open=True).at(p["out"])
    ls.lab(d, (p["out"][0] + 0.25, p["out"][1]), "Vo（输出）", fs_=10.5)
    ls.lab(d, (p["vin"][0] - 0.15, p["vin"][1] + 0.4), "Vi", ha="right", fs_=10.5)
    ls.note(d, (-1.5, -4.4), "运放电源脚（8 脚 +9 V、4 脚 GND）没画；所有标 V_MID 的空心圆点是同一点（图 33-p2-1 的输出）。")
    save_schem(d, N, "33_p2_2_schem_mfb.png")
    print("[图 33-p2-2] MFB 带通：R1 82 kΩ，R2 160 kΩ，R3 1.6 kΩ，C1 = C2 = 10 nF")


def p2_3():
    f = np.logspace(2, np.log10(5000), 1500)
    m = sim.bp_mag(f, F0, Q, A0)
    fe = [200, 500, 800, 900, 1000, 1100, 1200, 2000, 5000]
    me = [sim.mfb_ode(x, R1, R2, R3, CB) for x in fe]
    for x, y in zip(fe, me):
        print(f"[数值] 图 33-p2-4：{x:>5d} Hz 公式 {sim.bp_mag(x, F0, Q, A0):.4f}，逐步算 {y:.4f}")
        assert abs(y - sim.bp_mag(x, F0, Q, A0)) < 0.02 * sim.bp_mag(x, F0, Q, A0) + 1e-3
    lo, hi = sim.f3db(f, m, A0)
    print(f"[数值] 图 33-p2-4：峰值 {A0:.3f}，−3 dB 两点 {lo:.0f} Hz、{hi:.0f} Hz")
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(f, m, color=C["good"], ls="--", lw=1.4, label="公式（黑色虚线）")
    ax.plot(fe, me, "o", color=C["vout"], ms=6, label="逐步算（33_sim.py）")
    ax.axhline(A0 / np.sqrt(2), color=C["ref"], ls=":", lw=1)
    ax.text(110, A0 / np.sqrt(2) + 0.03, f"峰值 × 0.707 = {A0/np.sqrt(2):.3f}（−3 dB）", color="0.35", fontsize=9)
    assert abs(lo - 910) < 2 and abs(hi - 1109) < 2
    for fx, yy, tx, off in ((lo, A0 / np.sqrt(2), f"{lo:.0f} Hz", (-44, -15)), (F0, A0, f"{F0:.0f} Hz", (6, 3)),
                            (hi, A0 / np.sqrt(2), f"{hi:.0f} Hz", (6, -15))):
        ax.plot([fx], [yy], "s", color="k", ms=4.5, zorder=6)
        ax.annotate(tx, (fx, yy), xytext=off, textcoords="offset points", fontsize=8.5)
        print(f"[数值] 图 33-p2-4：标出 {tx}")
    ax.annotate("", xy=(lo, A0 / np.sqrt(2)), xytext=(hi, A0 / np.sqrt(2)),
                arrowprops=dict(arrowstyle="<->", color=C["vout"]))
    ax.annotate(f"带宽 {lo:.0f}～{hi:.0f} Hz", (hi, A0 / np.sqrt(2)), xytext=(1700, 0.62), fontsize=9,
                color=C["vout"], arrowprops=dict(arrowstyle="-", color=C["vout"], lw=0.7))
    ax.text(F0 * 0.92, A0 + 0.04, f"峰值 {A0:.3f}", fontsize=9, ha="right")
    ax.set_xscale("log"); ax.set_ylim(0, 1.15)
    ax.legend(loc="center left", fontsize=9)
    axl(ax, "频率 / Hz（对数刻度）", "输出 ÷ 输入")
    ax.set_title("图 33-p2-4 MFB 带通（82k / 160k / 1.6k / 10 nF）", fontsize=11)
    fs.save(fig, N, "33_p2_4_mfb_curve.png")


def _twint(d, x0=0.0, y0=0.0, vals=("Ra 33 kΩ", "Rb 33 kΩ", "2C\n（2 × 100 nF）", "Ca 100 nF", "Cb 100 nF", "R/2\n（2 × 33 kΩ 并联）")):
    yt, yb = y0 + 3.6, y0
    M, Nn = (x0 + 3, yt), (x0 + 3, yb)
    d += elm.Line().at((x0, yb)).to((x0, yt))
    d += elm.Resistor().endpoints((x0, yt), M).label(vals[0], "top")
    d += elm.Resistor().endpoints(M, (x0 + 6, yt)).label(vals[1], "top")
    d += elm.Capacitor().endpoints(M, (M[0], yt - 1.6))
    d += elm.Ground().at((M[0], yt - 1.6))
    ls.lab(d, (M[0] + 0.45, yt - 0.8), vals[2], fs_=10)
    d += elm.Capacitor().endpoints((x0, yb), Nn).label(vals[3], "bottom")
    d += elm.Capacitor().endpoints(Nn, (x0 + 6, yb)).label(vals[4], "bottom")
    d += elm.Resistor().endpoints(Nn, (Nn[0], yb - 2.2))
    d += elm.Ground().at((Nn[0], yb - 2.2))
    ls.lab(d, (Nn[0] + 0.45, yb - 1.1), vals[5], fs_=10)
    d += elm.Line().at((x0 + 6, yb)).to((x0 + 6, yt))
    yo = (yt + yb) / 2
    d += elm.Line().at((x0 + 6, yo)).to((x0 + 7.4, yo))
    d += elm.Line().at((x0, yo)).to((x0 - 1.8, yo))
    for pt in (M, Nn, (x0, yt), (x0, yb), (x0 + 6, yt), (x0 + 6, yb), (x0 + 6, yo), (x0, yo)):
        d += elm.Dot().at(pt)
    d += elm.SourceSin().endpoints((x0 - 1.8, yo - 2.8), (x0 - 1.8, yo))
    d += elm.Ground().at((x0 - 1.8, yo - 2.8))
    ls.lab(d, (x0 - 2.4, yo - 1.4), "手机\n音频", ha="right", fs_=10)
    return dict(M=M, N=Nn, vin=(x0, yo), out=(x0 + 7.4, yo), yt=yt, yb=yb, x0=x0)


def p2_4():
    d = drawing(fontsize=11)
    p = _twint(d)
    ls.lab(d, (p["M"][0] - 0.2, p["M"][1] - 0.4), "T 点", ha="right", fs_=11)
    ls.lab(d, (p["N"][0] - 0.2, p["N"][1] + 0.4), "P 点", ha="right", fs_=11)
    d += elm.Dot(open=True).at(p["out"])
    ls.lab(d, (p["out"][0] + 0.25, p["out"][1]), "Vo", fs_=10.5)
    ls.lab(d, (p["vin"][0] - 0.2, p["vin"][1] + 0.35), "Vi", ha="right", fs_=10.5)
    ls.note(d, (-4.0, -3.8), "上路：电阻–电阻，中点 T 经 2C 接地；下路：电容–电容，中点 P 经 R/2 接地。两路在输出端汇合。")
    save_schem(d, N, "33_p2_5_schem_twint.png")
    print(f"[图 33-p2-5] 双 T：R = 33 kΩ，C = 100 nF，f0 = 1/(2πRC) = {FT:.2f} Hz")


def p2_5():
    """把输出端接地，看两路分别送到输出端的电流。"""
    R, Cc = RT, CT
    def currents(f):
        w = 2 * np.pi * f
        # 输出接地时：上路 M 点电压、下路 N 点电压（只此处用复数，页面不出现）
        vM = (1 / R) / (2 / R + 1j * w * 2 * Cc)
        vN = (1j * w * Cc) / (2 * 1j * w * Cc + 2 / R)
        return vM / R, vN * 1j * w * Cc
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.8))
    for ax, f in zip(axs, (FT, 200)):
        iR, iC = currents(f)
        t = np.linspace(0, 2 / f, 600)
        ph = 2 * np.pi * f * t
        yR = 1e6 * np.abs(iR) * np.sin(ph + np.angle(iR))
        yC = 1e6 * np.abs(iC) * np.sin(ph + np.angle(iC))
        s = yR + yC
        print(f"[数值] 图 33-p2-7：{f:.1f} Hz，输入 1 V 幅度：经 Rb 电流 {1e6*abs(iR):.2f} µA，经 Cb 电流 {1e6*abs(iC):.2f} µA，合起来 {np.max(np.abs(s)):.2f} µA")
        ax.plot(t * 1e3, yR, color=C["cur"], lw=1.8, label="经 Rb 来的电流")
        ax.plot(t * 1e3, yC, color=C["third"], ls="-.", lw=1.8, label="经 Cb 来的电流")
        ax.plot(t * 1e3, s, color=C["good"], ls="--", lw=1.4, label="两股相加")
        ax.set_title(f"{f:.1f} Hz：相加 = {np.max(np.abs(s)):.2f} µA", fontsize=10)
        axl(ax, "时间 / ms", "电流 / µA")
        if f == FT:
            assert np.max(np.abs(s)) < 0.01
    axs[0].legend(loc="lower left", fontsize=8)
    axs[0].set_ylim(-16, 16)
    axs[1].set_ylim(-75, 75)
    fig.suptitle("图 33-p2-7 输出端接地时两路送来的电流（输入 1 V 幅度）", fontsize=11)
    fs.save(fig, N, "33_p2_7_twint_currents.png")


def p2_6():
    f = np.logspace(1, 3, 1500)
    m = sim.twint_mag(f, FT)
    fe = [10, 20, 30, 40, 48.23, 60, 80, 100, 200, 500, 1000]
    me = [sim.twint_ode(x, RT, CT) for x in fe]
    for x, y in zip(fe, me):
        print(f"[数值] 图 33-p2-8：{x:>7g} Hz 公式 {sim.twint_mag(x, FT):.4f}，逐步算 {y:.4f}")
        assert abs(y - sim.twint_mag(x, FT)) < 0.005
    lo, hi = sim.f3db(f, -m + 1.0, 1.0) if False else (None, None)
    # 降到 0.707 的两点
    i0 = int(np.argmin(m))
    lo = np.interp(-1 / np.sqrt(2), -m[:i0 + 1], f[:i0 + 1])
    hi = np.interp(1 / np.sqrt(2), m[i0:], f[i0:])
    print(f"[数值] 图 33-p2-8：输出低于 0.707 的范围 {lo:.1f}～{hi:.1f} Hz（坑很宽）")
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(f, m, color=C["good"], ls="--", lw=1.4, label="公式（黑色虚线）")
    ax.plot(fe, me, "o", color=C["vout"], ms=6, label="逐步算（33_sim.py）")
    ax.axhline(1 / np.sqrt(2), color=C["ref"], ls=":", lw=1)
    ax.text(11, 0.74, "0.707 倍（−3 dB）", color="0.35", fontsize=9)
    ax.annotate("", xy=(lo, 0.58), xytext=(hi, 0.58), arrowprops=dict(arrowstyle="<->", color=C["third"]))
    ax.text(FT, 0.61, f"低于 0.707：{lo:.0f}～{hi:.0f} Hz", ha="center", fontsize=9, color=C["third"])
    ax.text(FT * 1.08, 0.04, f"最深处 {FT:.1f} Hz", fontsize=9)
    ax.set_xscale("log"); ax.set_ylim(0, 1.08)
    ax.legend(loc="lower right", fontsize=9)
    axl(ax, "频率 / Hz（对数刻度）", "输出 ÷ 输入")
    ax.set_title("图 33-p2-8 双 T 陷波（33 kΩ / 100 nF，输出不接负载）", fontsize=11)
    fs.save(fig, N, "33_p2_8_twint_curve.png")


# =====================================================================
# page3：R3 改中心频率、运放太慢、双 T 元件不配对
# =====================================================================
def p3_1():
    f = np.linspace(400, 2000, 2000)
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    for r3, col, l in ((1e3, C["vin"], "-"), (1.6e3, C["vout"], "-"), (3e3, C["third"], "-.")):   # 电位器两端与实验值
        f0, q, a0, bw = sim.mfb_params(R1, R2, r3, CB)
        m = sim.bp_mag(f, f0, q, a0)
        print(f"[数值] 图 33-p3-1：R3 = {r3/1e3:g} kΩ → f0 = {f0:.0f} Hz，Q值 = {q:.2f}，带宽 = {bw:.1f} Hz，峰值 {a0:.3f}")
        ax.plot(f, m, color=col, ls=l, lw=1.8, label=f"R3 = {r3/1e3:g} kΩ：f0 {f0:.0f} Hz，带宽 {bw:.0f} Hz")
        assert abs(bw - 198.9) < 0.5
    ax.set_ylim(0, 1.32)
    ax.legend(loc="upper right", fontsize=9)
    axl(ax, "频率 / Hz", "输出 ÷ 输入")
    ax.set_title("图 33-p3-1 只换 R3：中心频率移动，带宽和峰值不变", fontsize=11)
    fs.save(fig, N, "33_p3_1_r3_sweep.png")


def p3_2():
    f = np.linspace(500, 1500, 1200)
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    rows = [(None, C["good"], "--", "理想运放"), (20e3, C["bad"], "-", "GBW 20 kHz"),
            (100e3, C["third"], "-.", "GBW 100 kHz"), (1e6, C["vout"], "-", "GBW 1 MHz")]
    print(f"[数值] 图 33-p3-3：2 × Q值² = {2*Q**2:.0f}")
    for g, col, l, name in rows:
        m = np.abs(sim.mfb_nodal(f, R1, R2, R3, CB, CB, gbw=g, a0=1e5))
        i0 = int(np.argmax(m))
        lo, hi = sim.f3db(f, m, m[i0])
        fc = np.sqrt(lo * hi)
        aol = "" if g is None else f"，1 kHz 处开环放大 {g/1e3:.0f} 倍"
        print(f"[数值] 图 33-p3-3：{name}：峰值 {m[i0]:.3f}，中心 {fc:.0f} Hz，带宽 {hi-lo:.0f} Hz{aol}")
        ax.plot(f, m, color=col, ls=l, lw=1.8, label=f"{name}：中心 {fc:.0f} Hz")
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper right", fontsize=9)
    axl(ax, "频率 / Hz", "输出 ÷ 输入")
    ax.set_title("图 33-p3-3 运放不够快：中心频率往下掉、峰变矮", fontsize=11)
    fs.save(fig, N, "33_p3_3_gbw.png")


def p3_3():
    f = np.linspace(35, 65, 3000)
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    rows = [((RT, RT, RT / 2, CT, CT, 2 * CT), C["good"], "--", "元件全部配对"),
            ((RT, RT, RT / 2 * 1.05, CT, CT, 2 * CT), C["bad"], "-", "R/2 大了 5%"),
            ((RT, RT, RT / 2, CT * 1.05, CT, 2 * CT), C["third"], "-.", "Ca 大了 5%")]
    for v, col, l, name in rows:
        m = np.abs(sim.twint_nodal(f, *v))
        i0 = int(np.argmin(m))
        m50 = abs(sim.twint_nodal(np.array([50.0]), *v))
        print(f"[数值] 图 33-p3-4：{name}：最低 {m[i0]:.4f}（{sim.db(m[i0]):.0f} dB）在 {f[i0]:.1f} Hz；50 Hz 处 {float(np.squeeze(m50)):.4f}")
        ax.plot(f, sim.db(m + 1e-9), color=col, ls=l, lw=1.8, label=f"{name}：最低 {sim.db(m[i0]):.0f} dB")
    ax.set_ylim(-80, 0)
    ax.legend(loc="lower right", fontsize=9)
    axl(ax, "频率 / Hz", "输出 ÷ 输入 / dB")
    ax.set_title("图 33-p3-4 双 T 元件差 5%：坑变浅、还挪了位置", fontsize=11)
    fs.save(fig, N, "33_p3_4_mismatch.png")


# =====================================================================
# page4：面包板与对应原理图
# =====================================================================
def p4_1():
    bb = bbk.Breadboard(30, "图 33-p4-1 A 区：MFB 带通 + 中点参考 V_MID（LM358，单 9 V）",
                        size=(10, 6.6), rails=("+9 V 轨", "GND 轨", "V_MID 轨", "GND 轨"))
    bb.chip(15, "LM358", names={1: "OUT", 2: "IN−", 3: "IN+", 4: "GND", 5: "IN+", 6: "IN−", 7: "OUT", 8: "V+"})
    # 运放 B：中点参考跟随器（上半）
    bb.wire("a15", "T+15", "pos")                 # 8 脚 → +9 V
    bb.wire("c16", "c17", "fb")                   # 7、6 脚短接
    bb.route("b18", "b21", "fb", dy=-0.5)         # 5 脚 → 第 21 列（分压点 D）
    bb.part("c21", "c25", "RA 10 kΩ", "R", lab_side=1)
    bb.wire("a25", "T+25", "pos")
    bb.part("a21", "T-21", "RB\n10 kΩ", "R", lab_side="r", fs_=7.5)
    bb.part("d21", "d23", "CM 10 µF", "E", lab_side=-1)
    bb.wire("a23", "T-23", "gnd")
    bb.part("T+27", "T-27", "Cd 100 nF", "C", lab_side="r", fs_=7.5)   # 电源去耦
    bb.wire("d16", "B-20", "vg", via=[(16, 2.1), (19.5, 2.1), (19.5, -6.2), (20, -6.2)])
    # 运放 A：MFB 带通（下半）
    bb.part("h3", "h7", "R1 82 kΩ", "R", lab_side=1)
    bb.part("j7", "B-7", "R3 1.6 kΩ", "R", lab_side="r")
    bb.part("i7", "i13", "C1 10 nF", "C", lab_side=-1)
    bb.part("g7", "g15", "C2 10 nF", "C", lab_side=1)
    bb.part("h13", "h15", "R2 160 kΩ", "R", lab_side=1, fs_=7.5)
    bb.wire("j16", "j13", "fb", via=[(16, -5.9), (13, -5.9)])
    bb.wire("j17", "B-17", "vg")                  # 3 脚 → V_MID 轨
    bb.wire("j18", "B+18", "gnd")                 # 4 脚 → GND
    bb.wire("T-29", "B+29", "gnd")
    # 外部：电池、手机
    bb.module(-3.2, 9.4, 3.6, 1.4, "9 V 电池")
    bb.wire((0.4, 10.4), "T+1", "pos", via=[(1, 10.4)])
    bb.wire((0.4, 9.7), "T-2", "gnd", via=[(2, 9.7)])
    bb.module(-3.3, -4.6, 3.0, 1.7, "手机音频\n转接板")
    bb.wire((-0.3, -3.4), "j3", "sig", via=[(3, -3.4)] if False else [(1.5, -3.4), (1.5, -5.4)])
    bb.wire((-1.0, -4.6), "B-2", "vg", via=[(-1.0, -6.2), (2, -6.2)])
    bb.probe("i3", "Ⓐ", dx=-0.9, dy=0.0)
    bb.probe("i15", "Ⓑ", dx=0.9, dy=0.0)
    bb.note(0.5, -8.9, "Ⓐ 第 3 列 = 输入点；Ⓑ 第 15 列 = 输出点；黑表笔插紫色 V_MID 轨。量 V_MID 本身：红表笔插紫轨、黑表笔插最下 GND 轨", ha="left")
    bb.note(0.5, -9.7, "芯片 1–4 脚在 f 排、8–5 脚在 e 排（第 15–18 列）；电解电容 CM 的 + 脚在 d21；Cd 跨在 +9 V 轨与 GND 轨之间（第 27 列）", ha="left")
    bb.legend(y=-0.02)
    bb.save(N, "33_p4_1_breadboard.png")
    print("[图 33-p4-1] 面包板 A 区：LM358 第 15–18 列；R1 h3–h7，R3 j7→V_MID 轨，C1 i7–i13，C2 g7–g15，R2 h13–h15，j16→j13，j17→V_MID 轨，j18→GND；"
          "a15→+9 V，c16–c17，b18→b21，RA c21–c25，a25→+9 V，RB a21→GND 轨，CM d21(+)–d23，a23→GND，Cd T+27–T−27，d16→V_MID 轨（第 20 列）")


def p4_2():
    """图 33-p4-2：与图 33-p4-1 一一对应的原理图（孔位用灰色小字）。"""
    d = drawing(fontsize=10.5)
    ls.title(d, (5.1, 6.6), "中点参考 V_MID（运放 B，第 15–27 列上半）")
    _vg(d, 0.0, holes=True)
    x0, y0 = 17.0, 1.5
    ls.title(d, (x0 + 5.0, 6.6), "MFB 带通（运放 A，第 3–18 列下半）")
    op, p = _mfb(d, x0, y0)
    a = op.absanchors
    ls._pin(d, a["in1"], "2", dx=-0.2, dy=0.25)
    ls._pin(d, a["in2"], "3", dx=-0.2, dy=-0.25)
    ls._pin(d, a["out"], "1", dx=0.15, dy=0.25)
    ls.colnote(d, (x0 + 0.15, y0 - 0.35), "j3", "right", ofst=0.0)
    ls.colnote(d, (x0 + 0.5, y0 - 2.75), "手机地→V_MID 轨", "right", ofst=0.0)
    ls.colnote(d, (p["A"][0] + 0.12, p["A"][1] + 0.35), "第 7 列", "right", ofst=0.0)
    ls.colnote(d, (p["A"][0] + 0.45, y0 - 1.75), "j7→V_MID 轨", "right", ofst=0.0)
    ls.colnote(d, (p["N"][0] - 0.12, p["N"][1] + 0.35), "第 13 列", "left", ofst=0.0)
    ls.colnote(d, (p["N"][0] + 0.45, y0 - 0.3), "j16→j13", "bottom", ofst=0.0)
    ls.colnote(d, (a["in2"][0] - 0.15, a["in2"][1] - 1.5), "j17→V_MID 轨", "bottom", ofst=0.0)
    ls.colnote(d, (p["xo"] + 0.1, a["out"][1] - 0.35), "第 15 列", "right", ofst=0.0)
    ls.probe(d, p["vin"], "Ⓐ", dx=-0.9, dy=0.7)
    ls.probe(d, p["out"], "Ⓑ", dx=0.8, dy=0.0)
    ls.note(d, (-1.5, -3.6), "读 Ⓐ、Ⓑ 时黑表笔插 V_MID 轨（紫色空心圆点），万用表交流电压挡。两只运放是同一片 LM358，8 脚 +9 V、4 脚 GND 两组共用。")
    save_schem(d, N, "33_p4_2_schem_lab.png")
    print("[图 33-p4-2] 原理图与图 33-p4-1 一一对应（孔位见灰字）")


def p4_3():
    bb = bbk.Breadboard(20, "图 33-p4-3 B 区：双 T 陷波（不用电池）", size=(8.4, 6.6), rails=("", "GND 轨", "GND 轨", ""))
    bb.part("c4", "c10", "Ra 33 kΩ", "R", lab_side=1)
    bb.part("c10", "c16", "Rb 33 kΩ", "R", lab_side=1)
    bb.part("a10", "T-10", "C3 100 nF", "C", lab_side="l")
    bb.part("a11", "T-11", "C4 100 nF", "C", lab_side="r")
    bb.wire("b10", "b11", "fb")
    bb.part("h4", "h10", "Ca 100 nF", "C", lab_side=1)
    bb.part("h10", "h16", "Cb 100 nF", "C", lab_side=1)
    bb.part("j10", "B-10", "R4 33 kΩ", "R", lab_side="l")
    bb.part("j11", "B-11", "R5 33 kΩ", "R", lab_side="r")
    bb.wire("i10", "i11", "fb")
    bb.wire("e4", "f4", "sig")
    bb.wire("e16", "f16", "out")
    bb.wire("T-19", "B-19", "gnd")
    bb.module(-3.2, 8.8, 3.0, 1.7, "手机音频\n转接板")
    bb.wire((-0.2, 9.9), "a4", "sig", via=[(4, 9.9)])
    bb.wire((-1.7, 8.8), "T-1", "gnd", via=[(-1.7, 8.25), (1, 8.25)])
    bb.probe("b4", "Ⓐ", dx=-0.9, dy=0.0)
    bb.probe("b16", "Ⓑ", dx=0.9, dy=0.0)
    bb.note(0.5, -8.9, "C3 ∥ C4 = 2C（200 nF，b10–b11 短接）；R4 ∥ R5 = R/2（16.5 kΩ，i10–i11 短接）", ha="left")
    bb.note(0.5, -9.7, "Ⓐ 第 4 列 = 输入点；Ⓑ 第 16 列 = 输出点；黑表笔插 GND 轨", ha="left")
    bb.legend(y=-0.02)
    bb.save(N, "33_p4_3_breadboard_twint.png")
    print("[图 33-p4-3] 双 T：Ra c4–c10，Rb c10–c16，C3 a10→GND，C4 a11→GND，b10–b11；Ca h4–h10，Cb h10–h16，R4 j10→GND，R5 j11→GND，i10–i11；e4–f4，e16–f16")


def p4_4():
    d = drawing(fontsize=10.5)
    p = _twint(d, vals=("Ra 33 kΩ", "Rb 33 kΩ", "C3 ∥ C4\n（2 × 100 nF）", "Ca 100 nF", "Cb 100 nF", "R4 ∥ R5\n（2 × 33 kΩ）"))
    M, Nn, yt, yb = p["M"], p["N"], p["yt"], p["yb"]
    ls.colnote(d, (M[0] - 0.2, yt - 0.7), "T 点：第 10 列上半", "left", ofst=0.0)
    ls.colnote(d, (M[0] + 0.45, yt - 1.6), "a10、a11→GND，b10–b11", "right", ofst=0.0)
    ls.colnote(d, (Nn[0] - 0.2, yb + 0.6), "P 点：第 10 列下半", "left", ofst=0.0)
    ls.colnote(d, (Nn[0] + 0.45, yb - 1.9), "j10、j11→GND，i10–i11", "right", ofst=0.0)
    ls.colnote(d, (-0.15, yt + 0.35), "第 4 列（e4–f4）", "left", ofst=0.0)
    ls.colnote(d, (6.15, yt + 0.35), "第 16 列（e16–f16）", "right", ofst=0.0)
    ls.colnote(d, (-1.6, p["vin"][1] + 0.3), "a4", "right", ofst=0.0)
    ls.probe(d, (0, yt), "Ⓐ", dx=-0.9, dy=0.0)
    ls.probe(d, p["out"], "Ⓑ", dx=0.8, dy=0.0)
    ls.note(d, (-4.0, -3.8), "接地符号 = GND 轨（上下两条在第 19 列连通，手机地接上方那条）；万用表交流电压挡，黑表笔插 GND 轨。")
    save_schem(d, N, "33_p4_4_schem_lab.png")
    print("[图 33-p4-4] 双 T 原理图与图 33-p4-3 一一对应")


def p4_5():
    vin = 0.30
    fm = [200, 500, 800, 900, 1000, 1100, 1200, 2000, 5000]
    ft = [20, 30, 40, 45, 48, 50, 55, 60, 100, 200, 1000]
    om = [vin * sim.bp_mag(x, F0, Q, A0) for x in fm]
    ot = [vin * sim.twint_mag(x, FT) for x in ft]
    for x, y in zip(fm, om):
        print(f"[数值] 图 33-p4-5：MFB 输入 0.30 V，{x:>5d} Hz → 应读 {y:.3f} V")
    for x, y in zip(ft, ot):
        print(f"[数值] 图 33-p4-5：双 T 输入 0.30 V，{x:>5d} Hz → 应读 {y*1e3:.1f} mV")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 4.0))
    a1.plot(fm, om, "o-", color=C["vout"], lw=1.4)
    for x, y in zip(fm, om):
        if x in (500, 1000, 2000):
            a1.annotate(f"{y:.3f} V", (x, y), textcoords="offset points", xytext=(4, 6), fontsize=8.5)
    a1.set_xscale("log"); a1.set_ylim(0, 0.36)
    from matplotlib.ticker import NullFormatter
    a1.set_xticks([200, 500, 1000, 2000, 5000]); a1.set_xticklabels(["200", "500", "1k", "2k", "5k"])
    a1.xaxis.set_minor_formatter(NullFormatter())
    axl(a1, "频率 / Hz", "万用表读数 / V")
    a1.set_title("A 区 MFB：读 Ⓑ", fontsize=10)
    a2.plot(ft, np.array(ot) * 1e3, "o-", color=C["vout"], lw=1.4)
    for x, y in zip(ft, ot):
        if x in (20, 50, 200):
            a2.annotate(f"{y*1e3:.0f} mV" if y > 0.01 else f"{y*1e3:.1f} mV", (x, y * 1e3),
                        textcoords="offset points", xytext=(10, 2) if x == 50 else (4, 6), fontsize=8.5)
    a2.set_xscale("log"); a2.set_ylim(0, 330)
    a2.set_xticks([20, 50, 100, 200, 500, 1000]); a2.set_xticklabels(["20", "50", "100", "200", "500", "1k"])
    a2.xaxis.set_minor_formatter(NullFormatter())
    axl(a2, "频率 / Hz", "万用表读数 / mV")
    a2.set_title("B 区双 T：读 Ⓑ", fontsize=10)
    fig.suptitle("图 33-p4-5 输入点 Ⓐ 固定 0.30 V 时，输出点 Ⓑ 应读到的值", fontsize=11)
    fs.save(fig, N, "33_p4_5_no_scope.png")


# =====================================================================
# 新增图（评审后补）：p1-5 两种电路并排、p2-3 戴维南等效、p2-6 输出短路、p3-2 R3 电位器、p3-5 双 T 微调
# =====================================================================
def p1_5():
    """图 33-p1-5：左 MFB 带通、右双 T 陷波的简化电路，蓝绿色虚线箭头标出 MFB 的两条反馈路。"""
    d = drawing(fontsize=10.5)
    ls.title(d, (4.8, 5.4), "左：MFB 带通（3 只电阻 + 2 只电容 + 1 只运放）")
    op, p = _mfb(d, 0.0, 0.0)
    A, xo = p["A"], p["xo"]
    for y, t in ((1.8 + 0.95, "R2 那条反馈路"), (3.4 + 0.95, "C2 那条反馈路")):
        d += elm.Line(arrow="->").at((xo, y)).to((A[0] + (3.0 if "R2" in t else 0.0), y)).color(C["fb"]).linestyle("--").linewidth(1.4)
        ls.lab(d, ((xo + A[0] + (3.0 if "R2" in t else 0.0)) / 2, y + 0.3), t, ha="center", fs_=9.5, color=C["fb"])
    x0 = 18.0
    ls.title(d, (x0 + 2.5, 5.4), "右：双 T 陷波（3R + 3C，不用运放）")
    q = _twint(d, x0, -0.6, vals=("R", "R", "2C", "C", "C", "R/2"))
    ls.lab(d, (q["M"][0] - 0.2, q["M"][1] - 0.4), "T 点", ha="right", fs_=10)
    ls.lab(d, (q["N"][0] - 0.2, q["N"][1] + 0.4), "P 点", ha="right", fs_=10)
    ls.note(d, (-1.5, -4.2), "MFB：输出经 C2、R2 两条路送回输入一侧（蓝绿色虚线箭头），只让 f0 附近通过。双 T：两路 T 形网络在输出端相加，在 f0 处正好抵消。")
    save_schem(d, N, "33_p1_5_two_circuits.png")
    print("[图 33-p1-5] MFB 带通与双 T 陷波简化电路并排；双 T 共 3 只电阻 + 3 只电容（R/2、2C 各算 1 只）")


def p2_thev():
    """图 33-p2-3：R1、R3 合起来等效成一个小电压源串一个小电阻。"""
    r13 = sim.par(R1, R3); k = R3 / (R1 + R3)
    print(f"[数值] 图 33-p2-3：R1 ∥ R3 = {r13:.0f} Ω，分压比 R3/(R1+R3) = {k:.4f}")
    assert abs(r13 - 1569) < 1 and abs(k - 0.0191) < 0.0001
    d = drawing(fontsize=10.5)
    d += elm.SourceSin().endpoints((0, -2.4), (0, 0))
    ls.lab(d, (-0.6, -1.2), "Vi", ha="right", fs_=10.5)
    _vmid(d, (0, -2.4))
    A = (3.2, 0)
    d += elm.Resistor().endpoints((0, 0), A).label("R1 82 kΩ", "top")
    d += elm.Dot().at(A)
    d += elm.Resistor().endpoints(A, (A[0], -2.4))
    ls.lab(d, (A[0] + 0.45, -1.2), "R3\n1.6 kΩ", fs_=10)
    _vmid(d, (A[0], -2.4))
    d += elm.Line().at(A).to((5.2, 0)); d += elm.Dot(open=True).at((5.2, 0))
    ls.lab(d, (5.45, 0), "A 点 →\nC1、C2、运放", fs_=9.5)
    ls.lab(d, (10.0, 0.9), "⇒ 等效成", ha="center", fs_=12)
    x = 13.0
    d += elm.SourceSin().endpoints((x, -2.4), (x, 0))
    ls.lab(d, (x - 0.6, -1.2), f"Vi × {k:.3f}", ha="right", fs_=10.5)
    _vmid(d, (x, -2.4))
    d += elm.Resistor().endpoints((x, 0), (x + 3.4, 0)).label(f"R1 ∥ R3 ≈ {r13/1e3:.2f} kΩ", "top")
    d += elm.Dot(open=True).at((x + 3.4, 0))
    ls.lab(d, (x + 3.65, 0), "A 点 →\n同一个滤波核心", fs_=9.5)
    ls.note(d, (-1.0, -4.0), f"从 A 点往左看：信号先被 R1、R3 分压成 {k:.3f} 倍，再串一个 {r13/1e3:.2f} kΩ 的小电阻。R3 越小，等效电阻越小，f0 越高。")
    save_schem(d, N, "33_p2_3_thevenin.png")


def p2_short():
    """图 33-p2-6：双 T 输出端用导线接地，两路送来的电流 I_R、I_C。"""
    d = drawing(fontsize=10.5)
    p = _twint(d)
    x0, yt, yb = p["x0"], p["yt"], p["yb"]
    ls.lab(d, (p["M"][0] - 0.2, p["M"][1] - 0.4), "T 点", ha="right", fs_=10.5)
    ls.lab(d, (p["N"][0] - 0.2, p["N"][1] + 0.4), "P 点", ha="right", fs_=10.5)
    out = p["out"]
    d += elm.Line().at(out).to((out[0], out[1] - 2.6)).linewidth(3.0)
    d += elm.Ground().at((out[0], out[1] - 2.6))
    ls.lab(d, (out[0] + 0.3, out[1] - 1.3), "输出端用导线\n接地（短路）", fs_=9.5)
    d += elm.Line(arrow="->").at((x0 + 3.7, yt + 1.0)).to((x0 + 5.6, yt + 1.0)).color(C["cur"]).linewidth(1.6)
    ls.lab(d, (x0 + 4.65, yt + 1.35), "I_R（经 Rb）", ha="center", fs_=10, color=C["cur"])
    d += elm.Line(arrow="->").at((x0 + 3.7, yb + 0.6)).to((x0 + 5.6, yb + 0.6)).color(C["cur"]).linewidth(1.6)
    ls.lab(d, (x0 + 4.65, yb + 0.95), "I_C（经 Cb）", ha="center", fs_=10, color=C["cur"])
    ls.note(d, (-4.0, -3.8), "两路电流都流进粗导线。f0 处 I_R 和 I_C 一样大、方向时刻相反，合起来是 0（见图 33-p2-7）。")
    save_schem(d, N, "33_p2_6_schem_short.png")
    print("[图 33-p2-6] 双 T 输出短路，天蓝色箭头 I_R、I_C")


def p3_pot():
    """图 33-p3-2：R3 = 1 kΩ 固定电阻 + 0～2 kΩ 电位器，拧一圈 f0 从约 1.27 kHz 到约 0.74 kHz。"""
    fa = sim.mfb_params(R1, R2, 1e3, CB)[0]; fb_ = sim.mfb_params(R1, R2, 3e3, CB)[0]
    print(f"[数值] 图 33-p3-2：电位器拧到 0 Ω（R3 = 1 kΩ）f0 = {fa:.0f} Hz；拧到 2 kΩ（R3 = 3 kΩ）f0 = {fb_:.1f} Hz")
    assert abs(fa - 1266) < 1 and abs(fb_ - 739.6) < 0.3
    d = drawing(fontsize=10.5)
    d += elm.Line().at((0, 0)).to((1.0, 0)); d += elm.Dot(open=True).at((0, 0))
    ls.lab(d, (-0.25, 0), "R1 来", ha="right", fs_=10)
    A = (2.5, 0)
    d += elm.Line().at((1.0, 0)).to(A); d += elm.Dot().at(A)
    ls.lab(d, (A[0] - 0.2, 0.35), "A 点", ha="right", fs_=10)
    d += elm.Line().at(A).to((5.0, 0)); d += elm.Dot(open=True).at((5.0, 0))
    ls.lab(d, (5.25, 0), "接 C1、C2", fs_=10)
    d += elm.Resistor().endpoints(A, (A[0], -2.2))
    ls.lab(d, (A[0] + 0.45, -1.1), "1 kΩ 固定", fs_=10)
    d += elm.Potentiometer().endpoints((A[0], -2.2), (A[0], -4.6))
    ls.lab(d, (A[0] + 0.8, -3.4), "0～2 kΩ 电位器\n（滑片接一端）", fs_=10)
    _vmid(d, (A[0], -4.6))
    ls.note(d, (-1.5, -6.3), f"R3 = 1～3 kΩ：f0 约 {fa:.0f}～{fb_:.0f} Hz，带宽始终约 199 Hz。")
    save_schem(d, N, "33_p3_2_schem_r3pot.png")


def p3_trim():
    """图 33-p3-5：双 T 微调：Ra、Rb 各并 1 MΩ，R/2 再并 470 kΩ，坑底从 48.2 Hz 挪到约 49.9 Hz。"""
    ra = sim.par(RT, 1e6); rc = sim.par(RT / 2, 470e3)
    fn, mn = sim.null_scan(ra, ra, rc, CT, CT, 2 * CT)
    h50 = abs(sim.twint_nodal(np.array([50.0]), ra, ra, rc, CT, CT, 2 * CT)[0])
    print(f"[数值] 图 33-p3-5：Ra = Rb = {ra/1e3:.2f} kΩ，R/2 = {rc/1e3:.2f} kΩ → 坑底 {fn:.2f} Hz，50 Hz 处 {h50:.5f}")
    assert abs(fn - 49.85) < 0.1
    d = drawing(fontsize=10.5)
    x0, yt, yb = 0.0, 4.2, 0.0
    Mx = x0 + 3
    d += elm.Line().at((x0, yb)).to((x0, yt))
    d += elm.Resistor().endpoints((x0, yt), (Mx, yt)).label("Ra 33 kΩ", "bottom")
    d += elm.Resistor().endpoints((Mx, yt), (x0 + 6, yt)).label("Rb 33 kΩ", "bottom")
    for xa_, xb_ in ((x0, Mx), (Mx, x0 + 6)):
        d += elm.Line().at((xa_, yt)).to((xa_, yt + 1.3))
        d += elm.Line().at((xb_, yt)).to((xb_, yt + 1.3))
        d += elm.Resistor().endpoints((xa_, yt + 1.3), (xb_, yt + 1.3)).label("并 1 MΩ", "top").color(C["third"])
    d += elm.Capacitor().endpoints((Mx, yt), (Mx, yt - 1.6))
    d += elm.Ground().at((Mx, yt - 1.6))
    d += elm.Dot().at((Mx, yt + 1.3))   # 两只 1 MΩ 的中点接 T 点（丁字连接画实心点）
    ls.lab(d, (Mx + 0.45, yt - 0.8), "2C 200 nF", fs_=10)
    ls.lab(d, (Mx - 0.2, yt - 0.4), "T 点", ha="right", fs_=10)
    d += elm.Capacitor().endpoints((x0, yb), (Mx, yb)).label("Ca 100 nF", "top")
    d += elm.Capacitor().endpoints((Mx, yb), (x0 + 6, yb)).label("Cb 100 nF", "top")
    ls.lab(d, (Mx - 0.2, yb - 0.4), "P 点", ha="right", fs_=10)
    yk = yb - 0.7
    d += elm.Line().at((Mx, yb)).to((Mx, yk)); d += elm.Dot().at((Mx, yk))
    d += elm.Resistor().endpoints((Mx, yk), (Mx, yk - 2.0))
    ls.lab(d, (Mx - 0.45, yk - 1.0), "R/2\n16.5 kΩ", ha="right", fs_=10)
    d += elm.Line().at((Mx, yk)).to((Mx + 1.5, yk))
    d += elm.Resistor().endpoints((Mx + 1.5, yk), (Mx + 1.5, yk - 2.0)).color(C["third"])
    ls.lab(d, (Mx + 1.95, yk - 1.0), "并 470 kΩ", fs_=10, color=C["third"])
    d += elm.Line().at((Mx + 1.5, yk - 2.0)).to((Mx, yk - 2.0)); d += elm.Dot().at((Mx, yk - 2.0))
    d += elm.Ground().at((Mx, yk - 2.0))
    d += elm.Line().at((x0 + 6, yb)).to((x0 + 6, yt))
    yo = (yt + yb) / 2
    d += elm.Line().at((x0 + 6, yo)).to((x0 + 7.4, yo)); d += elm.Dot(open=True).at((x0 + 7.4, yo))
    ls.lab(d, (x0 + 7.65, yo), "Vo", fs_=10.5)
    d += elm.Line().at((x0, yo)).to((x0 - 1.0, yo)); d += elm.Dot(open=True).at((x0 - 1.0, yo))
    ls.lab(d, (x0 - 1.25, yo), "Vi", ha="right", fs_=10.5)
    for pt in ((Mx, yt), (Mx, yb), (x0, yt), (x0, yb), (x0 + 6, yt), (x0 + 6, yb), (x0 + 6, yo), (x0, yo)):
        d += elm.Dot().at(pt)
    ls.note(d, (-2.0, -4.0), f"红紫色 3 只是加上去的大电阻：等效 Ra = Rb ≈ {ra/1e3:.2f} kΩ，R/2 ≈ {rc/1e3:.2f} kΩ，坑底挪到 {fn:.2f} Hz。")
    save_schem(d, N, "33_p3_5_schem_trim.png")


if __name__ == "__main__":
    for fn in (p1_1, p1_2, p1_3, p1_4, p1_5, p2_1, p2_2, p2_thev, p2_3, p2_4, p2_short, p2_5, p2_6,
               p3_1, p3_pot, p3_2, p3_3, p3_trim, p4_1, p4_2, p4_3, p4_4, p4_5):
        fn()
