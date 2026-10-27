"""44 D 类功放：全部配图。
运行：/workspace/circuits-venv/bin/python code/figs/44_figs.py
波形 / 扫描数据来自 spice/44/*.csv（由 spice/44/run.py --update 从 ngspice 结果抽稀生成）。
图上的每个数字都由本脚本算出并打印；关键结论用 assert 检查。
电路：单 12 V；TL072 出中点参考 V_MID 6 V 和三角波；LM393 两路互补比较（AD 调制）；DRV8871 模块 H 桥；
每腿 220 µH 功率电感 + 跨接 0.68 µF；负载 10 Ω 串 8 Ω 喇叭（BTL，两端都不接地）。
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
from lab_schem import probe, colnote, lab, title, note, ring, Hop, _dbox, GRAY

N = "44"
SP = os.path.join(HERE, "..", "..", "spice", "44")


def csv(name):
    """读 spice/44 下的 CSV（第一行是列名），返回 {列名: 数组}。"""
    path = os.path.join(SP, name)
    head = open(path).readline().strip().split(",")
    arr = np.genfromtxt(path, delimiter=",", skip_header=1, dtype=None, encoding="utf-8")
    if arr.dtype.names:
        return {h: arr[n] for h, n in zip(head, arr.dtype.names)}
    arr = np.atleast_2d(arr)
    return {h: arr[:, i] for i, h in enumerate(head)}


# ============================ 公共数值 ============================
VS = 12.0                      # 电源（DRV8871 的 VM）
VMID = 6.0
L_LEG, CF = 220e-6, 0.68e-6    # 每腿电感、跨接电容
DCR = 0.453                    # RLB0913-221K 直流电阻（典型）
ISAT = 0.64                    # RLB0913-221K 饱和电流
R10, RSPK = 10.0, 8.0
RLOAD = R10 + RSPK
RDS = 0.307 + 0.258            # DRV8871 高边 + 低边
NUM = {k: float(v) for k, v in zip(*csv("nums.csv").values())}
FSW, VTRI = NUM["fsw"], NUM["vtri"]
F_FORM = 22e3 / (4 * 10e3 * 4.7e3 * 2.2e-9)
GAIN = VS / VTRI
F0 = 1 / (2 * np.pi * np.sqrt(2 * L_LEG * CF))
Q18 = RLOAD * np.sqrt(CF / (2 * L_LEG))
IRIP = VS / (8 * L_LEG * FSW)
KIN = 10 / 14.7                # 输入 4.7 kΩ / 10 kΩ 分压
EFF = csv("eff.csv")
NUM_H0 = float(csv("ac.csv")["h_18ohm"][0])
CMP = csv("compare.csv")
print(f"[数值] 三角波：公式 f = R2/(4·R1·R·C) = {F_FORM/1e3:.2f} kHz，SPICE f_sw = {FSW/1e3:.2f} kHz，V_tri,p = {VTRI:.3f} V，增益 V_S/V_tri,p = {GAIN:.3f}")
print(f"[数值] LC：f0 = {F0/1e3:.3f} kHz，Q 值(18 Ω) = {Q18:.4f}，纹波公式 {IRIP:.4f} A，输入分压 {KIN:.4f}")
print(f"[数值] 中频总增益（源 → 负载峰值）≈ {KIN*GAIN:.3f}（再乘 LC 直流增益）")
assert abs(FSW - 38.56e3) < 100 and abs(VTRI - 2.732) < 0.005 and abs(F0 - 9201) < 5 and abs(Q18 - 0.7076) < 1e-3
assert abs(F_FORM - 53.19e3) < 50 and abs(IRIP - 0.1768) < 5e-4


def _shrink(name):
    """原理图线条多、PNG 偏大：在本节自己的 img 里把它转成 256 色调色板 PNG（看上去一样，体积小一半以上）。"""
    from PIL import Image
    path = os.path.join(HERE, "..", "..", "44-class-d-amp", "img", name)
    Image.open(path).convert("RGB").quantize(256).save(path, optimize=True)
    print(f"[压缩] {name} → {os.path.getsize(path) // 1024} KB")


def save(fig, name):
    return fs.save(fig, N, name)


# =============================== page1 ===============================
# ---------- 图 44-p1-1：三角波 + 信号 → PWM → 平均 ----------
def p1_1():
    """示意：为了看清，载波只取信号的 12 倍；三角波峰值 2.73 V、电源 12 V 用真实值。"""
    fsig, k = 1.0, 12
    t = np.linspace(0, 1, 24001)
    tri = fs.triangle(t, k * fsig, VTRI)
    sig = 1.8 * np.sin(2 * np.pi * fsig * t)
    pwm = np.where(sig > tri, VS, -VS)               # BTL 两端互补：+12 V 或 −12 V
    n = len(t) // k                                   # 每个载波周期的点数，滑动平均 = 「电感 + 电容」滤掉载波的效果
    avg = np.convolve(pwm, np.ones(n) / n, mode="same")
    ideal = sig / VTRI * VS
    fig, axs = plt.subplots(3, 1, figsize=(7, 5.6), sharex=True)
    axs[0].plot(t, tri, **fs.LS["fb"], label="三角波（载波）")
    axs[0].plot(t, sig, **fs.LS["vin"], label="音频信号")
    axs[0].set_ylabel("电压 / V"); axs[0].legend(loc="upper right", fontsize=8.5, ncol=2)
    axs[0].set_title("① 比较：信号高于三角波 → 输出 +12 V，低于 → 输出 −12 V", fontsize=10)
    axs[1].plot(t, pwm, color=fs.C["vout"], lw=1.0)
    axs[1].set_ylabel("电压 / V"); axs[1].set_ylim(-15, 15)
    axs[1].set_title("② H 桥输出（喇叭两端之间）：只有 +12 V、−12 V 两种值，脉冲宽窄跟着信号变", fontsize=10)
    axs[2].plot(t, ideal, **fs.LS["good"], label="理想：信号 × 12 V ÷ 2.73 V")
    axs[2].plot(t[n:-n], avg[n:-n], color=fs.C["third"], lw=1.6, label="每个载波周期取平均")
    axs[2].set_ylabel("电压 / V"); axs[2].legend(loc="upper right", fontsize=8.5)
    axs[2].set_title("③ 滤掉载波（取平均）：又变回放大了的音频", fontsize=10)
    axs[2].set_xlabel("时间（信号周期）")
    gpk = float(np.max(np.abs(avg[n:-n])))
    print(f"[图 44-p1-1] 信号峰值 1.8 V，理想输出峰值 {1.8/VTRI*VS:.2f} V，平均后峰值 {gpk:.2f} V")
    assert abs(gpk - 1.8 / VTRI * VS) < 0.6
    save(fig, "44_p1_1_pwm_idea.png")


# ---------- 图 44-p1-2：效率 ----------
def p1_2():
    pa = EFF["p_audio_W"]
    vp = EFF["vpk_V"]
    eta_b = np.pi * vp / (4 * VS) * 100              # 理想乙类 BTL（同 12 V、同 18 Ω）
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot(pa, EFF["eta_pct"], "o-", color=fs.C["vout"], lw=1.8, label="D 类（本节电路，SPICE）")
    ax.plot(pa, eta_b, **fs.LS["good"], marker="s", label="理想乙类推挽（同电源、同负载，公式）")
    i1 = int(np.argmin(np.abs(EFF["amp_V"] - 1.0)))
    fs.mark(ax, pa[i1], EFF["eta_pct"][i1], "{:.0f}", "%", dx=6, dy=-13)
    fs.mark(ax, pa[i1], eta_b[i1], "{:.1f}", "%", dx=6, dy=-13)
    fs.mark(ax, pa[-1], EFF["eta_pct"][-1], "{:.0f}", "%", dx=-12, dy=-15)
    fs.mark(ax, pa[0], EFF["eta_pct"][0], "{:.0f}", "%", dx=6, dy=-4)
    fs.axlabels(ax, "输出功率（喇叭 + 10 Ω）", "W", "效率", "%")
    ax.set_ylim(0, 100); ax.legend(loc="center left", bbox_to_anchor=(0.36, 0.5), fontsize=8.5)
    print(f"[图 44-p1-2] P = {pa[i1]:.3f} W：D 类 {EFF['eta_pct'][i1]:.1f}%，理想乙类 {eta_b[i1]:.1f}%；最大 {pa[-1]:.3f} W：D 类 {EFF['eta_pct'][-1]:.1f}%，乙类 {eta_b[-1]:.1f}%")
    assert EFF["eta_pct"][i1] > 3 * eta_b[i1]
    save(fig, "44_p1_2_efficiency.png")


# ---------- 图 44-p1-3：方框图 ----------
def p1_3():
    fig, ax = fs.diagram(10, 3.6)
    a = fs.box(ax, 1.0, 2.7, "音频信号\n（手机）", w=1.6, h=0.9)
    b = fs.box(ax, 1.0, 0.9, "三角波发生器\nTL072，38.6 kHz", w=1.8, h=0.9)
    c = fs.box(ax, 3.6, 1.8, "比较器 ×2\nLM393", w=1.7, h=1.0, fc=fs.C["fill2"])
    dd = fs.box(ax, 5.9, 1.8, "H 桥\nDRV8871 模块", w=1.7, h=1.0)
    e = fs.box(ax, 8.15, 1.8, "LC 滤波\n2 × 220 µH\n+ 0.68 µF", w=1.5, h=1.2, fc=fs.C["fill2"])
    sp = fs.box(ax, 9.5, 1.8, "10 Ω\n+ 喇叭", w=0.9, h=1.0)
    fs.arrow(ax, a["r"], (c["l"][0], 2.05))
    fs.arrow(ax, b["r"], (c["l"][0], 1.55))
    fs.arrow(ax, (c["r"][0], 2.0), (dd["l"][0], 2.0), "IN1", fs=8.5)
    fs.arrow(ax, (c["r"][0], 1.6), (dd["l"][0], 1.6))
    ax.text((c["r"][0] + dd["l"][0]) / 2, 1.45, "IN2", ha="center", va="top", fontsize=8.5)
    fs.arrow(ax, (dd["r"][0], 2.0), (e["l"][0], 2.0), "OUT1", fs=8.5)
    fs.arrow(ax, (dd["r"][0], 1.6), (e["l"][0], 1.6))
    ax.text((dd["r"][0] + e["l"][0]) / 2, 1.45, "OUT2", ha="center", va="top", fontsize=8.5)
    fs.arrow(ax, e["r"], sp["l"])
    ax.text(3.6, 0.55, "0 / 5 V 开关信号", ha="center", fontsize=8.5, color=fs.C["edge"])
    ax.text(5.9, 0.55, "0 / 12 V 方波，管子只开或关", ha="center", fontsize=8.5, color=fs.C["edge"])
    ax.text(8.15, 0.85, "滤掉 38.6 kHz，\n留下音频", ha="center", fontsize=8.5, color=fs.C["edge"])
    ax.text(5.0, 3.35, "D 类功放的四个方块：载波、比较（调制）、开关、滤波", ha="center", fontsize=10)
    save(fig, "44_p1_3_blocks.png")


# ---------- 图 44-p1-4：载波——三角波发生器（U1A 积分器 + U1B 施密特触发器，带引脚号） ----------
def _pinno(d, xy, n, dx=0.0, dy=0.25):
    """运放 / 比较器引脚号（小号深灰字）。"""
    d += elm.Label().at((xy[0] + dx, xy[1] + dy)).label(n, fontsize=8.5, color="#333333", halign="center", valign="center")


def _supply(d, op, top="+12 V", npos="8", nneg="4"):
    """在运放上下画电源脚：8 脚接 top，4 脚接 GND。"""
    a = op.absanchors
    t, b = a["vs"], a["vd"]
    if t[1] < b[1]:
        t, b = b, t
    d += elm.Line().at(t).to((t[0], t[1] + 0.45))
    d += elm.Vdd().at((t[0], t[1] + 0.45)).label(top, fontsize=8.5)
    _pinno(d, t, npos, dx=0.25, dy=0.2)
    d += elm.Line().at(b).to((b[0], b[1] - 0.45))
    d += elm.Ground().at((b[0], b[1] - 0.45))
    _pinno(d, b, nneg, dx=0.25, dy=-0.2)


def p1_4():
    print(f"[图 44-p1-4] 载波：Rint 4.7 kΩ、Cint 2.2 nF；Rs1 10 kΩ、Rs2 22 kΩ；Ct 100 nF、Rt 100 kΩ → t；"
          f"SPICE f = {FSW/1e3:.2f} kHz、三角波峰值 {VTRI:.2f} V")
    with drawing(fontsize=10) as d:
        TRI, SQ = fs.C["vout"], fs.C["vin"]
        # U1A 积分器：− = 2 脚（ni），+ = 3 脚（V_MID），输出 1 脚 = tri
        u1a = elm.Opamp(leads=True).theta(0).anchor("in1").at((2.0, 4.0))
        d += u1a
        A = u1a.absanchors
        _pinno(d, A["in1"], "2", dx=-0.2); _pinno(d, A["in2"], "3", dx=-0.2, dy=-0.25); _pinno(d, A["out"], "1", dx=0.15)
        lab(d, (A["in2"][0] + 0.75, A["out"][1]), "U1A\nTL072", fs_=8.5)
        _supply(d, u1a)
        d += elm.Resistor().endpoints((-1.6, 4.0), (1.2, 4.0)).label("Rint 4.7 kΩ", loc="top", fontsize=9)
        d += elm.Line().at((1.2, 4.0)).to(A["in1"])
        d += elm.Dot().at((1.2, 4.0))
        d += elm.Line().at((1.2, 4.0)).to((1.2, 6.6))
        d += elm.Capacitor().endpoints((1.2, 6.6), (6.4, 6.6)).label("Cint 2.2 nF", loc="top", fontsize=9)
        xt = 6.4
        d += elm.Line().at((xt, 6.6)).to((xt, A["out"][1]))
        d += elm.Line().at(A["out"]).to((xt, A["out"][1])).color(TRI).linewidth(1.8)
        d += elm.Dot().at((xt, A["out"][1]))
        lab(d, (1.35, 5.3), "ni", fs_=9)
        d += elm.Line().at(A["in2"]).to((A["in2"][0] - 0.5, A["in2"][1]))
        _vmid(d, (A["in2"][0] - 0.5, A["in2"][1]), "left")
        # U1B 施密特：+ = 5 脚（sp），− = 6 脚（V_MID），输出 7 脚 = sq
        u1b = elm.Opamp(leads=True).theta(0).flip().anchor("in2").at((11.0, 1.0))
        d += u1b
        B = u1b.absanchors
        _pinno(d, B["in2"], "5", dx=-0.2); _pinno(d, B["in1"], "6", dx=-0.2, dy=-0.25); _pinno(d, B["out"], "7", dx=0.15)
        lab(d, (B["in2"][0] + 0.75, B["out"][1]), "U1B\nTL072", fs_=8.5)
        _supply(d, u1b)
        d += elm.Line().at(B["in1"]).to((B["in1"][0] - 0.6, B["in1"][1]))
        _vmid(d, (B["in1"][0] - 0.6, B["in1"][1]), "down")
        # tri → Rs1 → sp；sq → Rs2 → sp
        ytri = A["out"][1]
        d += elm.Line().at((xt, ytri)).to((xt, 1.0)).color(TRI).linewidth(1.8)
        d += elm.Resistor().endpoints((xt, 1.0), (9.6, 1.0)).label("Rs1 10 kΩ", loc="top", fontsize=9)
        d += elm.Dot().at((9.6, 1.0))
        d += elm.Line().at((9.6, 1.0)).to(B["in2"])
        lab(d, (9.55, 1.45), "sp", ha="right", fs_=9)
        xs = B["out"][0] + 1.0
        d += elm.Line().at(B["out"]).to((xs, B["out"][1])).color(SQ).linewidth(1.8)
        d += elm.Dot().at((xs, B["out"][1]))
        d += elm.Line().at((9.6, 1.0)).to((9.6, -3.2))
        d += elm.Resistor().endpoints((9.6, -3.2), (xs, -3.2)).label("Rs2 22 kΩ", loc="bottom", fontsize=9)
        d += elm.Line().at((xs, -3.2)).to((xs, B["out"][1])).color(SQ).linewidth(1.8)
        # sq 回到 Rint 左端（积分器输入）
        d += elm.Line().at((xs, -3.2)).to((xs, -4.4)).color(SQ).linewidth(1.8)
        d += elm.Line().at((xs, -4.4)).to((-1.6, -4.4)).color(SQ).linewidth(1.8)
        d += elm.Line().at((-1.6, -4.4)).to((-1.6, 4.0)).color(SQ).linewidth(1.8)
        lab(d, (xs + 0.25, B["out"][1] - 0.45), "方波 sq\n1.5～10.5 V", fs_=9, color=SQ)
        lab(d, (3.0, -4.0), "方波 sq 回到积分器输入", ha="center", fs_=8.5, color=SQ)
        lab(d, (xt + 0.2, ytri + 0.5), "三角波 tri", fs_=9, color=TRI)
        # tri → Ct → t；Rt 接 V_MID
        d += elm.Line().at((xt, ytri)).to((xt + 1.6, ytri)).color(TRI).linewidth(1.8)
        d += elm.Line().at((xt + 1.6, ytri)).to((xt + 1.6, 5.3)).color(TRI).linewidth(1.8)
        d += elm.Capacitor().endpoints((xt + 1.6, 5.3), (11.2, 5.3)).label("Ct 100 nF", loc="top", fontsize=9)
        d += elm.Line().at((11.2, 5.3)).to((17.6, 5.3)).color(TRI).linewidth(1.8)
        d += elm.Dot().at((16.4, 5.3))
        d += elm.Resistor().endpoints((16.4, 5.3), (16.4, 3.0)).label("Rt\n100 kΩ", loc="bottom", fontsize=9)
        _vmid(d, (16.4, 3.0), "down")
        d += elm.Dot(open=True).at((17.6, 5.3))
        lab(d, (16.0, 5.75), "t", ha="center", fs_=10, color=TRI)
        lab(d, (17.8, 5.3), "t → 比较器\n（图 44-p1-6）", fs_=9, color=TRI)
        note(d, (-1.8, -5.8), "U1 = 一颗 TL072（双运放）：A 组 1、2、3 脚做积分器，B 组 5、6、7 脚做施密特触发器；8 脚 +12 V，4 脚 GND。\n"
                              "$V_{MID}$ ≈ 6 V 是 12 V 的一半，由另一颗 TL072（U2B）把两只 10 kΩ 分压缓冲出来（图 44-p1-5）。"
                              f"SPICE：约 {FSW/1e3:.1f} kHz，t 点三角波 $V_{{MID}}$ ± {VTRI:.2f} V。")
    save_schem(d, N, "44_p1_4_carrier_schem.png")
    _shrink("44_p1_4_carrier_schem.png")


# ---------- 图 44-p1-5：中点参考 V_MID（R1、R2 分压 + U2B 跟随器） ----------
def p1_vmid():
    with drawing(fontsize=10) as d:
        d += elm.Vdd().at((-1.0, -1.6)).label("+12 V", fontsize=9)
        d += elm.Resistor().endpoints((-1.0, -1.6), (-1.0, -4.0)).label("R1 10 kΩ", loc="top", fontsize=9)
        d += elm.Resistor().endpoints((-1.0, -4.0), (-1.0, -6.4)).label("R2 10 kΩ", loc="top", fontsize=9)
        d += elm.Ground().at((-1.0, -6.4))
        d += elm.Dot().at((-1.0, -4.0))
        d += elm.Line().at((-1.0, -4.0)).to((0.4, -4.0))
        d += elm.Dot().at((0.4, -4.0))
        d += elm.Capacitor().endpoints((0.4, -4.0), (0.4, -6.4)).label("Cd\n10 µF", loc="bottom", fontsize=9)
        d += elm.Ground().at((0.4, -6.4))
        lab(d, (-0.85, -3.6), "6 V", ha="left", fs_=8.5, color=GRAY)
        u2 = elm.Opamp(leads=True).right().at((1.5, -4.0)).anchor("in2").label("U2B\nTL072", loc="center", ofst=(0.3, 0), fontsize=9)
        d += u2
        _pins(d, u2, "6", "5", "7")
        d += elm.Line().at((0.4, -4.0)).to(u2.in2)
        d += elm.Line().at(u2.in1).to((1.2, u2.in1[1]))
        d += elm.Line().at((1.2, u2.in1[1])).to((1.2, -1.6))
        d += elm.Line().at((1.2, -1.6)).to((5.4, -1.6))
        d += elm.Line().at((5.4, -1.6)).to((5.4, u2.out[1]))
        d += elm.Line().at(u2.out).to((6.3, u2.out[1])).color(fs.C["fb"])
        d += elm.Dot().at((5.4, u2.out[1]))
        lab(d, (6.4, u2.out[1]), "$V_{MID}$ ≈ 6 V\n（送到上下两张图\n里的 $V_{MID}$）", ha="left", fs_=9, color=fs.C["fb"])
        d += elm.Line().at((9.6, -1.0)).to((9.6, -1.0)).color("white")  # 留出右侧文字空间
        note(d, (-1.6, -7.8), "6 脚接 7 脚 = 跟随器：7 脚电压等于 5 脚，但能往外送电流，分压点不会被后级拉偏。\n"
                              "U2 是另一颗 TL072：8 脚 +12 V，4 脚 GND；灰色小数字是引脚号。")
    print("[图 44-p1-5] 中点参考：R1/R2 10k 分压 → U2B 5 脚，6-7 短接，输出 V_MID ≈ 6 V；Cd 10 µF 滤纹波")
    save_schem(d, N, "44_p1_5_vmid_schem.png")
    _shrink("44_p1_5_vmid_schem.png")


# ---------- 图 44-p1-6：比较（U3A / U3B，LM393）+ 开关（DRV8871）+ 滤波（L1、L2、Cf）+ 负载 ----------
def p1_5():
    _drive_schem("44_p1_6_drive_schem.png")


def _drive_schem(name, extra=False):
    """extra=True：排错用，加 U3 退耦 100 nF、VM 旁 100 µF + 100 nF、IN2 故障标注。"""
    print("[图 44-p1-6] 比较 U3A(+3=s, −2=t, 1→IN1)、U3B(+5=t, −6=s, 7→IN2)，1 kΩ 上拉 +5 V；DRV8871 VM 12 V；"
          "L1/L2 220 µH、Cf 0.68 µF；10 Ω + 8 Ω，两端都不接地")
    with drawing(fontsize=10) as d:
        IN, PW = fs.C["vin"], fs.C["vout"]
        # 输入：信号源 → Rin1 → Cin → s；Rin2 → V_MID
        d += elm.SourceSin().endpoints((0, -1.4), (0, 1.0)).label("音频\n（手机）", loc="bottom", fontsize=9)
        d += elm.Ground().at((0, -1.4))
        d += elm.Resistor().endpoints((0, 1.0), (2.6, 1.0)).label("Rin1 4.7 kΩ", loc="top", fontsize=9)
        d += elm.Capacitor().endpoints((2.6, 1.0), (4.6, 1.0)).label("Cin 1 µF", loc="top", fontsize=9)
        d += elm.Line().at((4.6, 1.0)).to((6.6, 1.0)).color(IN).linewidth(1.8)
        d += elm.Dot().at((5.2, 1.0))
        lab(d, (5.3, 1.35), "s", fs_=10, color=IN)
        d += elm.Resistor().endpoints((5.2, 1.0), (5.2, -1.4)).label("Rin2\n10 kΩ", loc="bottom", fontsize=9)
        _vmid(d, (5.2, -1.4), "down")
        # t 来自图 44-p1-4
        yt = 5.2
        d += elm.Dot(open=True).at((0, yt))
        lab(d, (0, yt + 0.55), "t（三角波，来自图 44-p1-4）", ha="left", fs_=9, color=fs.C["vout"])
        d += elm.Line().at((0, yt)).to((7.6, yt)).color(fs.C["vout"]).linewidth(1.8)
        # U3A：+3 = s，−2 = t，1 → IN1
        ua = elm.Opamp(leads=True).theta(0).anchor("in1").at((9.0, yt))
        d += ua; A = ua.absanchors
        d += elm.Line().at((7.6, yt)).to(A["in1"]).color(fs.C["vout"]).linewidth(1.8)
        _pinno(d, A["in1"], "2", dx=-0.2); _pinno(d, A["in2"], "3", dx=-0.2, dy=-0.25); _pinno(d, A["out"], "1", dx=0.15)
        lab(d, (A["in2"][0] + 0.75, A["out"][1]), "U3A\nLM393", fs_=8.5)
        _supply(d, ua)
        if extra:                                     # 两颗芯片的退耦：画在左下空白处
            for xx, chip in ((0.6, "U1 TL072"), (3.4, "U3 LM393")):
                d += elm.Vdd().at((xx, -3.6)).label("+12 V（8 脚）", fontsize=8)
                d += elm.Capacitor().endpoints((xx, -3.6), (xx, -5.0)).label("100 nF", loc="bottom", fontsize=8.5)
                d += elm.Ground().at((xx, -5.0))
                lab(d, (xx, -6.0), f"{chip}\n4 脚 = GND", ha="center", fs_=8)
            lab(d, (2.0, -2.5), "电源脚就近退耦（贴着芯片插）", ha="center", fs_=8.5)
        # U3B：+5 = t，−6 = s，7 → IN2
        yb = -3.0
        ub = elm.Opamp(leads=True).theta(0).anchor("in1").at((9.0, yb))
        d += ub; B = ub.absanchors
        _pinno(d, B["in1"], "6", dx=-0.2); _pinno(d, B["in2"], "5", dx=-0.2, dy=-0.25); _pinno(d, B["out"], "7", dx=0.15)
        lab(d, (B["in2"][0] + 0.75, B["out"][1]), "U3B\nLM393", fs_=8.5)
        lab(d, (B["in2"][0] + 0.5, B["in2"][1] - 1.35), "（与 U3A 同一颗芯片，\n共用 8 脚、4 脚）", fs_=8, color=GRAY)
        # s → U3A 3 脚、U3B 6 脚
        d += elm.Line().at((6.6, 1.0)).to((6.6, A["in2"][1])).color(IN).linewidth(1.8)
        d += elm.Dot().at((6.6, 1.0))
        d += elm.Line().at((6.6, 1.0)).to((6.6, B["in1"][1])).color(IN).linewidth(1.8)
        for P in (A["in2"], B["in1"]):                 # s 的横线跨过 t 的竖线（不相连）
            d += elm.Line().at((6.6, P[1])).to((7.35, P[1])).color(IN).linewidth(1.8)
            d += Hop().at((7.6, P[1])).theta(0).color(IN).linewidth(1.8)
            d += elm.Line().at((7.85, P[1])).to(P).color(IN).linewidth(1.8)
        # t → U3B 5 脚
        d += elm.Dot().at((7.6, yt))
        d += elm.Line().at((7.6, yt)).to((7.6, 2.6)).color(fs.C["vout"]).linewidth(1.8)
        d += elm.Line().at((7.6, 2.6)).to((7.6, B["in2"][1])).color(fs.C["vout"]).linewidth(1.8)
        d += elm.Line().at((7.6, B["in2"][1])).to(B["in2"]).color(fs.C["vout"]).linewidth(1.8)
        # 上拉 + IN1/IN2
        xm0 = 16.0
        for P, nm in ((A, "IN1"), (B, "IN2")):
            y = P["out"][1]
            d += elm.Line().at(P["out"]).to((xm0, y))
            d += elm.Dot().at((13.6, y))
            d += elm.Resistor().endpoints((13.6, y), (13.6, y + 2.0)).label("1 kΩ", loc="bottom", fontsize=9)
            d += elm.Vdd().at((13.6, y + 2.0)).label("+5 V（Arduino）", fontsize=8.5)
        # DRV8871 模块
        x0, x1, ybot, ytop = xm0, xm0 + 3.2, -5.4, 6.6
        for a, b in (((x0, ybot), (x1, ybot)), ((x1, ybot), (x1, ytop)), ((x1, ytop), (x0, ytop)), ((x0, ytop), (x0, ybot))):
            d += elm.Line().endpoints(a, b).linewidth(1.6)
        lab(d, ((x0 + x1) / 2, 0.8), "DRV8871\n模块\n（H 桥：\n4 只\nMOS 管）", ha="center", fs_=10)
        lab(d, (x0 + 0.15, A["out"][1]), "IN1", fs_=8.5)
        lab(d, (x0 + 0.15, B["out"][1]), "IN2", fs_=8.5)
        yo1, yo2 = 3.4, -2.2
        lab(d, (x1 - 0.15, yo1), "OUT1", ha="right", fs_=8.5)
        lab(d, (x1 - 0.15, yo2), "OUT2", ha="right", fs_=8.5)
        xc = (x0 + x1) / 2
        lab(d, (xc, ytop - 0.35), "VM", ha="center", fs_=8.5)
        lab(d, (xc, ybot + 0.35), "GND", ha="center", fs_=8.5)
        d += elm.Line().at((xc, ytop)).to((xc, ytop + 0.8))
        d += elm.Vdd().at((xc, ytop + 0.8)).label("+12 V", fontsize=9)
        if extra:
            yv = ytop + 0.4
            d += elm.Dot().at((xc, yv))
            d += elm.Line().at((xc, yv)).to((x1 + 2.6, yv))
            d += elm.Dot().at((x1 + 1.0, yv))
            for xx, cc, pol in ((x1 + 1.0, "100 µF", True), (x1 + 2.6, "100 nF", False)):
                d += elm.Capacitor(polar=pol).endpoints((xx, yv), (xx, yv - 1.4)).label(cc, loc="bottom", fontsize=8.5)
                d += elm.Ground().at((xx, yv - 1.4))
            lab(d, (x1 + 1.8, yv + 0.45), "VM 退耦（模块旁）", ha="center", fs_=8.5)
        d += elm.Line().at((xc, ybot)).to((xc, ybot - 0.6))
        d += elm.Ground().at((xc, ybot - 0.6))
        # LC + 负载
        d += elm.Inductor2().endpoints((x1, yo1), (x1 + 3.0, yo1)).label("L1 220 µH", loc="top", fontsize=9)
        d += elm.Inductor2().endpoints((x1, yo2), (x1 + 3.0, yo2)).label("L2 220 µH", loc="bottom", fontsize=9)
        for y in (yo1, yo2):
            d += elm.Line().at((x1 + 3.0, y)).to((x1 + 6.2, y))
            d += elm.Dot().at((x1 + 3.8, y))
        d += elm.Capacitor().endpoints((x1 + 3.8, yo1), (x1 + 3.8, yo2)).label("Cf\n0.68 µF", loc="bottom", fontsize=9)
        ym = (yo1 + yo2) / 2
        d += elm.Resistor().endpoints((x1 + 6.2, yo1), (x1 + 6.2, ym)).label("10 Ω\n5 W", loc="bottom", fontsize=9)
        d += elm.Resistor().endpoints((x1 + 6.2, ym), (x1 + 6.2, yo2)).label("8 Ω\n喇叭", loc="bottom", fontsize=9)
        lab(d, (x1 + 3.3, yo2 - 1.2), "BTL：喇叭两端都不接地", ha="center", fs_=9, color=fs.C["bad"])
        if extra:
            lab(d, (x0 - 0.2, B["out"][1] - 0.9), "IN2 只能接 U3B 的 7 脚：\n接 GND 或 5 V 都会让喇叭吃直流", ha="right", fs_=8.5, color=fs.C["bad"])
        note(d, (-2.6, -7.8 if extra else -7.2), "U3 = 一颗 LM393（双比较器）：A 组 3 脚 +、2 脚 −、1 脚出；B 组 5 脚 +、6 脚 −、7 脚出；8 脚 +12 V，4 脚 GND。\n"
                              "两路的 s、t 接法正好相反，所以 IN1、IN2 互补；LM393 是开集电极输出，靠 1 kΩ 上拉到 Arduino 的 5 V 才有高电平。")
    save_schem(d, N, name)
    _shrink(name)


# =============================== page2 ===============================


# ---------- 图 44-p2-5：DRV8871 内部的 H 桥（4 只 N 沟道 MOS 管，标 G/D/S 与体二极管） ----------
def p2_5():
    print("[图 44-p2-5] DRV8871 内部 H 桥：上管 Q1/Q3 接 VM 12 V，下管 Q2/Q4 接 GND；OUT1 = Q1 S/Q2 D，OUT2 = Q3 S/Q4 D；"
          "直通 12 V ÷ 0.565 Ω ≈ 21 A")
    with drawing(fontsize=10) as d:
        xl, xr, yt, ym, yb = 0.0, 7.0, 8.0, 4.0, 0.0
        d += elm.Line().endpoints((xl, yt), (xr, yt))
        d += elm.Vdd().at((3.5, yt)).label("VM = +12 V", fontsize=9.5)
        d += elm.Line().endpoints((xl, yb), (xr, yb))
        d += elm.Ground().at((3.5, yb))
        for name, x, ytop, side, role in [("Q1", xl, yt, "L", "上管"), ("Q2", xl, ym, "L", "下管"),
                                          ("Q3", xr, yt, "R", "上管"), ("Q4", xr, ym, "R", "下管")]:
            q = elm.NFet().theta(0).anchor("drain").at((x, ytop - 0.4))
            q = q.reverse() if side == "L" else q
            d += elm.Line().endpoints((x, ytop), (x, ytop - 0.4))
            d += q
            d += elm.Line().endpoints(q.source, (x, ytop - 4.0))
            sgn = -1 if side == "L" else 1
            gx = q.gate[0] + 1.9 * sgn
            d += elm.Line().endpoints(q.gate, (gx, q.gate[1]))
            # 引脚字母
            lab(d, (q.gate[0] + 0.2 * sgn, q.gate[1] + 0.3), "G", ha="center", fs_=8.5, color="#333333")
            lab(d, (x - 0.25 * sgn, ytop - 0.55), "D", ha="center", fs_=8.5, color="#333333")
            lab(d, (x - 0.25 * sgn, q.source[1] + 0.15), "S", ha="center", fs_=8.5, color="#333333")
            lab(d, (q.gate[0] + 0.8 * sgn, q.gate[1] - 0.45), f"{name} {role}", ha="center", fs_=9)
            # 体二极管（S → D 方向导通）
            dx = -1.1 * sgn
            yd0, yd1 = ytop - 0.4, q.source[1]
            d += elm.Line().endpoints((x, yd0), (x + dx, yd0)).color(GRAY)
            d += elm.Diode().endpoints((x + dx, yd1), (x + dx, yd0)).color(GRAY)
            d += elm.Line().endpoints((x + dx, yd1), (x, yd1)).color(GRAY)
            # 栅极驱动块
        # 两侧驱动框
        for xs, nm, ha in ((xl - 2.3, "IN1", "right"), (xr + 2.3, "IN2", "left")):
            x0, x1 = (xs - 2.4, xs) if ha == "right" else (xs, xs + 2.4)
            for a, b in (((x0, 0.9), (x1, 0.9)), ((x1, 0.9), (x1, 7.6)), ((x1, 7.6), (x0, 7.6)), ((x0, 7.6), (x0, 0.9))):
                d += elm.Line().endpoints(a, b).color(GRAY).linestyle("--")
            lab(d, ((x0 + x1) / 2, 4.6), "栅极驱动\n+ 死区\n（芯片内部\n自动加\n220 ns）", ha="center", fs_=8.5, color=GRAY)
            xo = x0 - 0.8 if ha == "right" else x1 + 0.8
            xe = x0 if ha == "right" else x1
            d += elm.Line().endpoints((xo, 2.4), (xe, 2.4))
            d += elm.Dot(open=True).at((xo, 2.4))
            lab(d, (xo, 2.85), nm, ha="center", fs_=9.5)
        # 输出与负载
        d += elm.Dot().at((xl, ym)); d += elm.Dot().at((xr, ym))
        lab(d, (xl + 0.25, ym + 0.35), "OUT1", fs_=9.5)
        lab(d, (xr - 0.25, ym + 0.35), "OUT2", ha="right", fs_=9.5)
        d += elm.Line().endpoints((xl, ym), (2.0, ym))
        d += elm.Resistor().endpoints((2.0, ym), (5.0, ym)).label("L1、L2、Cf\n+ 负载", loc="bottom", fontsize=9)
        d += elm.Line().endpoints((5.0, ym), (xr, ym))
        # 直通路径（Q1、Q2 同时导通）
        bad = fs.C["bad"]
        d += elm.Line().endpoints((xl + 1.6, yt - 0.25), (xl + 1.6, yb + 0.3)).color(bad).linestyle("--").linewidth(1.6)
        d += elm.Arrow().endpoints((xl + 1.6, 1.2), (xl + 1.6, yb + 0.3)).color(bad).linewidth(1.6)
        lab(d, (xl + 1.85, 1.5), "直通：Q1、Q2 同时开，\n12 V 直接短到 GND，\n约 21 A", fs_=8.5, color=bad)
        note(d, (-5.5, -1.6), "左侧桥臂 Q1、Q2 的中点是 OUT1，右侧 Q3、Q4 的中点是 OUT2。四只都是 N 沟道 MOS 管：D 漏极、S 源极、G 栅极；\n"
                              "灰色的是管子自带的体二极管（S→D 方向导通），死区里两管都关时，电感电流就从它走。")
    save_schem(d, N, "44_p2_5_hbridge_fets.png")
    _shrink("44_p2_5_hbridge_fets.png")
# ---------- 图 44-p2-3：三角波和方波 ----------
def p2_3():
    w = csv("w_idle.csv")
    t = (w["t"] - w["t"][0]) * 1e6
    m = t < 80
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot(t[m], w["sq"][m], **fs.LS["vin"], label="方波（施密特触发器输出）")
    ax.plot(t[m], w["tri"][m], **fs.LS["vout"], label="三角波（积分器输出）")
    fs.ref_h(ax, VMID, "中点参考 6 V", x=0.99)
    tri, sq = w["tri"], w["sq"]
    fs.mark(ax, t[m][np.argmax(sq[m])], sq.max(), "{:.2f}", " V", dy=0.4)
    fs.mark(ax, t[m][np.argmin(sq[m])], sq.min(), "{:.2f}", " V", dy=-1.0)
    up, lo = float(np.max(w["tt"])), float(np.min(w["tt"]))
    print(f"[图 44-p2-3] 方波 {sq.min():.3f}～{sq.max():.3f} V；三角波（耦合后）{lo:.3f}～{up:.3f} V，峰值 {(up-lo)/2:.3f} V，中心 {(up+lo)/2:.3f} V，周期 {1e6/FSW:.2f} µs")
    i0 = np.where(m)[0]
    pk = i0[np.argmax(tri[m])]
    fs.mark(ax, t[pk], tri[pk], "{:.2f}", " V", dx=-38, dy=2)
    fs.span(ax, 10, 10 + 1e6 / FSW, 11.6, f"一个周期 {1e6/FSW:.1f} µs（{FSW/1e3:.1f} kHz）")
    fs.axlabels(ax, "时间", "µs", "电压", "V")
    ax.set_ylim(0, 13.2); ax.legend(loc="lower right", fontsize=8.5, ncol=2)
    assert abs((up - lo) / 2 - VTRI) < 0.05
    save(fig, "44_p2_3_triangle.png")


# ---------- 图 44-p2-4：比较器把信号变成脉宽 ----------
def p2_4():
    w = csv("w_pwm.csv")
    t = (w["t"] - w["t"][0]) * 1e6
    fig, axs = plt.subplots(3, 1, figsize=(7, 5.0), sharex=True)
    axs[0].plot(t, w["tri"], **fs.LS["fb"], label="三角波 t")
    axs[0].plot(t, w["s"], **fs.LS["vin"], label="信号 s")
    fs.ref_h(axs[0], VMID, "6 V", x=0.99)
    axs[0].set_ylabel("电压 / V"); axs[0].legend(loc="lower right", fontsize=8, ncol=2)
    axs[1].plot(t, w["in1"], color=fs.C["third"], lw=1.4)
    axs[1].set_ylabel("IN1 / V"); axs[1].set_ylim(-0.8, 6)
    axs[2].plot(t, w["o1"], color=fs.C["vout"], lw=1.4)
    axs[2].set_ylabel("OUT1 / V"); axs[2].set_ylim(-1.5, 14)
    axs[2].set_xlabel("时间 / µs")
    duty = float(np.mean(w["in1"] > 2.5))
    s_avg = float(np.mean(w["s"]))
    d_form = 0.5 + (s_avg - VMID) / (2 * VTRI)
    axs[1].set_title(f"信号高于三角波时 IN1 = 5 V：这一段高电平占 {duty*100:.0f}%", fontsize=9.5)
    axs[2].set_title(f"OUT1 跟着 IN1 在 0 V 和 12 V 之间切换，平均 {np.mean(w['o1']):.2f} V", fontsize=9.5)
    print(f"[图 44-p2-4] 窗口内 s 平均 {s_avg:.3f} V → 公式 D = {d_form*100:.1f}%；SPICE IN1 高电平占 {duty*100:.1f}%；OUT1 平均 {np.mean(w['o1']):.2f} V（公式 D×12 = {d_form*12:.2f} V）")
    assert abs(duty - d_form) < 0.06
    save(fig, "44_p2_4_pwm_window.png")
    return d_form, duty, s_avg


# ---------- 图 44-p2-7：LC 滤波器幅频曲线 ----------
def p2_7():
    a = csv("ac.csv")
    f, h = a["f_Hz"], a["h_18ohm"]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.semilogx(f, 20 * np.log10(h), color=fs.C["vout"], lw=1.8, label="LC 滤波器（带 18 Ω 负载，SPICE）")
    ax.semilogx(f, 20 * np.log10(np.abs(1 / (1 - (f / F0) ** 2 + 1j * f / (F0 * Q18)))), **fs.LS["good"], label="公式（不计电感直流电阻）")
    h0 = float(h[0]); hz = float(np.interp(20e3, f, h)); hs = float(np.interp(FSW, f, h))
    fs.ref_v(ax, F0, f"谐振频率 {F0/1e3:.1f} kHz", y=0.3)
    fs.ref_v(ax, FSW, f"开关频率 {FSW/1e3:.1f} kHz", y=0.93)
    fs.mark(ax, 20e3, 20 * np.log10(hz), "{:.1f}", " dB（20 kHz）", dx=-95, dy=-4)
    fs.mark(ax, FSW, 20 * np.log10(hs), "{:.1f}", " dB", dx=6, dy=4)
    ax.set_xlim(100, 2e5); ax.set_ylim(-45, 8)
    fs.axlabels(ax, "频率（对数横轴）", "Hz", "增益", "dB")
    ax.legend(loc="lower left", fontsize=8.5)
    print(f"[图 44-p2-7] 直流增益 {h0:.4f}（{20*np.log10(h0):.2f} dB），20 kHz {hz:.4f}（{20*np.log10(hz):.1f} dB），f_sw {hs:.5f}（{20*np.log10(hs):.1f} dB），−3 dB 点 {NUM['f3']/1e3:.2f} kHz")
    print(f"[数值] 直流增益公式 18/(18+2×0.453) = {RLOAD/(RLOAD+2*DCR):.4f}")
    assert abs(hs - NUM["hfs"]) < 1e-3 and abs(h0 - 0.9244) < 1e-3
    save(fig, "44_p2_7_lc_bode.png")


# ---------- 图 44-p2-8：放音时的输出 ----------
def p2_8():
    w = csv("w_sig.csv")
    t = (w["t"] - w["t"][0]) * 1e3
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7, 4.4), sharex=True)
    a1.plot(t, w["sig"], **fs.LS["vin"], label="信号源（峰值 1 V）")
    a1.plot(t, w["vd"], color=fs.C["vout"], lw=1.2, label="负载两端 v_d（10 Ω + 喇叭）")
    a1.set_ylabel("电压 / V"); a1.legend(loc="upper right", fontsize=8.5, ncol=2); a1.set_ylim(-4.2, 5.2)
    a2.plot(t, w["iL"], color=fs.C["cur"], lw=1.2)
    a2.set_ylabel("电感电流 / A"); a2.set_xlabel("时间 / ms")
    vpk = float(EFF["vpk_V"][EFF["amp_V"] == 1.0][0])
    ilpk = float(np.max(np.abs(w["iL"])))
    fs.ref_h(a1, vpk, f"基波峰值 {vpk:.2f} V", x=0.3)
    a2.set_title(f"电流 = 音频成分 + 38.6 kHz 的小三角纹波，最大 {ilpk:.3f} A", fontsize=9.5)
    print(f"[图 44-p2-8] 源 1 V 峰值 → 负载基波峰值 {vpk:.3f} V（增益 {vpk:.3f}，估算 {KIN*GAIN*NUM_H0:.3f}）；本窗口电感电流最大 {ilpk:.4f} A")
    save(fig, "44_p2_8_audio_wave.png")


# ---------- 图 44-p2-9：静音时 OUT1、OUT2 和电感电流 ----------
def p2_9():
    w = csv("w_idle.csv")
    t = (w["t"] - w["t"][0]) * 1e6
    m = t < 60
    fig, axs = plt.subplots(3, 1, figsize=(7, 5.0), sharex=True)
    axs[0].plot(t[m], w["o1"][m], color=fs.C["vout"], lw=1.4, label="OUT1")
    axs[0].plot(t[m], w["o2"][m], color=fs.C["vin"], lw=1.2, ls="--", label="OUT2")
    axs[0].set_ylabel("对 GND / V"); axs[0].legend(loc="center right", fontsize=8.5); axs[0].set_ylim(-1.5, 14)
    axs[0].set_title("没有信号：两端互补，各开一半时间", fontsize=9.5)
    axs[1].plot(t[m], w["o1"][m] - w["o2"][m], color=fs.C["third"], lw=1.2)
    axs[1].set_ylabel("OUT1 − OUT2 / V"); axs[1].set_ylim(-15, 15)
    axs[2].plot(t[m], w["iL"][m], color=fs.C["cur"], lw=1.4)
    ip = float(np.max(np.abs(w["iL"])))
    fs.ref_h(axs[2], IRIP, f"公式 {IRIP:.3f} A", x=0.99)
    fs.ref_h(axs[2], -IRIP, None)
    axs[2].set_ylabel("电感电流 / A"); axs[2].set_xlabel("时间 / µs")
    axs[2].set_title(f"电感电流在 ±{ip:.3f} A 之间来回（SPICE），平均约为 0", fontsize=9.5)
    print(f"[图 44-p2-9] 纹波电流峰值 SPICE {ip:.4f} A，公式 {IRIP:.4f} A；OUT1 平均 {np.mean(w['o1']):.3f} V")
    save(fig, "44_p2_9_idle_bridge.png")


# ---------- 图 44-p2-2：三角波发生器闭环（积分器 + 施密特） ----------
def p2_2():
    with drawing(fontsize=10) as d:
        u1a = elm.Opamp(leads=True).right().at((2, 4)).anchor("in1").label("U1A\n积分器", loc="center", ofst=(0.3, 0), fontsize=9)
        d += u1a
        d += elm.Resistor().endpoints((-1.6, 4), (1.4, 4)).label("Rint 4.7 kΩ", loc="top", fontsize=9)
        d += elm.Line().at((1.4, 4)).to((2, 4))
        d += elm.Dot().at((1.4, 4))
        d += elm.Line().at((1.4, 4)).to((1.4, 5.6))
        d += elm.Capacitor().endpoints((1.4, 5.6), (5.9, 5.6)).label("Cint 2.2 nF", loc="top", fontsize=9)
        d += elm.Line().at((5.9, 5.6)).to((5.9, 3.375))
        d += elm.Line().at(u1a.out).to((5.9, 3.375))
        d += elm.Dot().at((5.9, 3.375))
        d += elm.Line().at(u1a.in2).to((1.4, 2.75))
        _vmid(d, (1.4, 2.75), "left")
        u1b = elm.Opamp(leads=True).right().at((9.5, 3.0)).anchor("in1").label("U1B\n施密特", loc="center", ofst=(0.3, 0), fontsize=9)
        d += u1b
        d += elm.Line().at(u1b.in1).to((9.0, 3.0))
        d += elm.Line().at((9.0, 3.0)).to((9.0, 3.6)).color(fs.C["fb"])
        lab(d, (9.0, 3.9), "$V_{MID}$", ha="center", fs_=9.5, color=fs.C["fb"])
        d += elm.Line().at((5.9, 3.375)).to((5.9, 1.75))
        d += elm.Resistor().endpoints((5.9, 1.75), (8.6, 1.75)).label("Rs1 10 kΩ", loc="top", fontsize=9)
        d += elm.Line().at((8.6, 1.75)).to(u1b.in2)
        d += elm.Dot().at((8.9, 1.75))
        d += elm.Line().at((8.9, 1.75)).to((8.9, 0.6))
        d += elm.Resistor().endpoints((8.9, 0.6), (12.4, 0.6)).label("Rs2 22 kΩ", loc="bottom", fontsize=9)
        d += elm.Line().at((12.4, 0.6)).to((13.6, 0.6))
        d += elm.Line().at(u1b.out).to((13.6, 2.375))
        d += elm.Dot().at((13.6, 2.375))
        d += elm.Line().at((13.6, 2.375)).to((13.6, -0.4))
        d += elm.Dot().at((13.6, 0.6))
        d += elm.Line().at((13.6, -0.4)).to((-1.6, -0.4))
        d += elm.Line().at((-1.6, -0.4)).to((-1.6, 4))
        lab(d, (13.8, 2.9), "方波 sq", ha="left", fs_=9.5)
        lab(d, (7.6, 4.6), "三角波 tri", ha="left", fs_=9.5, color=fs.C["cur"])
        d += elm.Dot().at((5.9, 4.6))
        d += elm.Line().at((5.9, 4.6)).to((7.4, 4.6)).color(fs.C["cur"])
        # 三步说明（沿闭环方向）
        lab(d, (-1.4, -1.3), "① 积分到门槛：sq 经 Rint 给 Cint 充电，tri 匀速变化", ha="left", fs_=9.5, color="#333333")
        lab(d, (-1.4, -2.1), "② 施密特翻转：tri 经 Rs1 把 U1B 的 + 端推过 $V_{MID}$，sq 跳到另一边", ha="left", fs_=9.5, color="#333333")
        lab(d, (-1.4, -2.9), "③ 反向积分：sq 反号，tri 往回走，到另一个门槛再翻转……", ha="left", fs_=9.5, color="#333333")
        d += elm.Arrow().at((3.5, -0.4)).to((0.8, -0.4)).color(fs.C["vout"])
    print(f"[图 44-p2-2] 三角波闭环：Rint 4.7 kΩ，Cint 2.2 nF，Rs1 10 kΩ，Rs2 22 kΩ；公式 {F_FORM/1e3:.2f} kHz，SPICE {FSW/1e3:.2f} kHz")
    save_schem(d, N, "44_p2_2_tri_loop.png")
    _shrink("44_p2_2_tri_loop.png")


# ---------- 图 44-p2-6：死区时序（示意） ----------
TDEAD = 220e-9      # DRV8871 数据手册 7.3.4，典型值


def p2_6():
    td = TDEAD * 1e6
    t = np.linspace(0, 3, 3001)
    t_fall, t_rise = 0.5, 2.0
    in1 = np.where((t < t_fall) | (t >= t_rise), 1, 0)
    hs = np.where((t < t_fall) | (t >= t_rise + td), 1, 0)          # 上管：先关、晚开
    ls_ = np.where((t >= t_fall + td) & (t < t_rise), 1, 0)          # 下管：晚开、先关
    assert not np.any(hs & ls_)                                      # 任何时刻都不同时导通
    fig, axs = plt.subplots(5, 1, figsize=(7, 5.6), sharex=True)
    rows = [(in1, "IN1", fs.C["third"]), (1 - in1, "IN2", fs.C["third"]),
            (hs, "上管\n（OUT1→12 V）", fs.C["bad"]), (ls_, "下管\n（OUT1→GND）", "#000000")]
    for ax, (y, nm, c) in zip(axs, rows):
        ax.step(t, y, where="post", color=c, lw=1.6)
        ax.set_ylim(-0.3, 1.4); ax.set_yticks([0, 1]); ax.set_ylabel(nm, rotation=0, ha="right", va="center", fontsize=9)
    o1 = np.where(hs == 1, 12.0, np.where(ls_ == 1, 0.0, np.nan))
    axs[4].plot(t, o1, color=fs.C["vout"], lw=1.6)
    for a0 in (t_fall, t_rise):
        axs[4].plot([a0, a0 + td], [6, 6], color=fs.C["vout"], lw=1.4, ls="--")
    axs[4].set_ylim(-2, 15); axs[4].set_yticks([0, 12]); axs[4].set_ylabel("OUT1 / V", rotation=0, ha="right", va="center", fontsize=9)
    for ax in axs:
        for a0 in (t_fall, t_rise):
            ax.axvspan(a0, a0 + td, color="0.8", zorder=0)
    axs[2].annotate(f"$t_{{DEAD}}$ = {TDEAD*1e9:.0f} ns：两管都关", xy=(t_fall + td, 0.5), xytext=(0.95, 0.75), fontsize=9,
                    arrowprops=dict(arrowstyle="->", lw=0.8))
    axs[4].text(t_fall + td + 0.05, 7.5, "死区里电压由电感电流方向决定（虚线）", fontsize=8.5)
    axs[4].set_xlabel("时间 / µs（示意：略去芯片约 0.7 µs 的传播延迟）")
    axs[0].set_title("DRV8871 一侧桥臂：上管先关，等 $t_{DEAD}$ 再开下管（反之亦然）", fontsize=10)
    print(f"[图 44-p2-6] 死区 {TDEAD*1e9:.0f} ns；直通电流理论值 12 V ÷ {RDS:.3f} Ω ≈ {VS/RDS:.1f} A（芯片过流门槛 3.7～6.4 A）")
    save(fig, "44_p2_6_deadtime.png")


# ---------- 数值核对（page2 / page3 / page4 新增的数） ----------
def nums_fix():
    spk = ", ".join(f"{p * RSPK / RLOAD:.4f}" for p in EFF["p_audio_W"])
    print(f"[数值] 26 节驱动—刹车 PWM 照搬：静音 6 V 直流，理想 6/18 = {6/RLOAD:.3f} A，8 Ω 上 {(6/RLOAD)**2*RSPK:.3f} W；含损耗 6 × {NUM_H0:.4f} = {6*NUM_H0:.3f} V")
    i_load = np.sqrt(0.158 ** 2 + (0.6148 / RLOAD) ** 2)
    print(f"[数值] 负载有效值电流 √(0.158² + (0.6148/18)²) = {i_load:.4f} A → 10 Ω {i_load**2*R10:.3f} W，喇叭 {i_load**2*RSPK:.3f} W；载波进负载 {0.6148/RLOAD*1e3:.1f} mA；纹波有效值 {0.1837/np.sqrt(3):.4f} A")
    print(f"[数值] 喇叭分到的功率（×8/18）：{spk}")
    for amp in (40, 45, 120):
        v = amp / 127.5 * VS * NUM_H0
        irip = VS / (8 * L_LEG * 31372.5)
        print(f"[数值] 选做 D AMP = {amp}：负载峰值 {v:.3f} V，音频电流峰值 {v/RLOAD:.4f} A，31.37 kHz 纹波 {irip:.4f} A，电感峰值约 {v/RLOAD+irip:.3f} A")
    print(f"[数值] 信号源 1.5 V 峰值 → 有效值 {1.5/np.sqrt(2):.3f} V（万用表交流档读 ≤ 1.0 V）")


# =============================== page3 ===============================

# ---------- 图 44-p3-2：排错用对照原理图（比较器、H 桥、LC，带引脚号与退耦） ----------
def p3_2():
    print("[图 44-p3-2] 排错对照：同图 44-p1-6，另加 U3 退耦 100 nF、VM 100 µF + 100 nF、IN2 故障标注")
    _drive_schem("44_p3_2_debug_schem.png", extra=True)

def p3_1():
    h = csv("harm.csv")
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.bar(h["k"], h["rel_pct"], color=fs.C["vout"], width=0.6)
    for k, r in zip(h["k"], h["rel_pct"]):
        ax.text(k, r + 0.002, f"{r:.3f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(h["k"])
    fs.axlabels(ax, "谐波次数（400 Hz 的几倍）", None, "相对基波", "%")
    ax.set_ylim(0, 0.12)
    thd = float(np.sqrt(np.sum(h["rel_pct"] ** 2)))
    ax.set_title(f"SPICE：每个谐波都不到 0.1%，合起来 THD = {thd:.2f}%（真实电路会更大）", fontsize=9.5)
    print(f"[图 44-p3-1] THD（2～10 次合成）= {thd:.4f}%，run.py 值 {NUM['thd']:.4f}%")
    assert abs(thd - NUM["thd"]) < 0.01
    save(fig, "44_p3_1_harmonics.png")


def p3_3():
    names = {"none": "不加 LC", "eng100u": "100 µH + 0.33 µF\n（f0 ≈ 19.6 kHz）", "ours220u": "本节 220 µH + 0.68 µF\n（f0 ≈ 9.2 kHz）",
             "arduino": "本节 LC，换 Arduino\n31.4 kHz 载波"}
    cs = list(CMP["case"])
    pr = CMP["p_ripple_mW"]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    cols = [fs.C["bad"], fs.C["third"], fs.C["vout"], fs.C["fb"]]
    ax.bar(range(len(cs)), pr, color=cols, width=0.6)
    ax.set_yscale("log")
    for i, (p, ii) in enumerate(zip(pr, CMP["i_supply_mA"])):
        ax.text(i, p * 1.25, f"{p:.0f} mW\n电源 {ii:.1f} mA", ha="center", va="bottom", fontsize=8.5)
    ax.set_xticks(range(len(cs))); ax.set_xticklabels([names[c] for c in cs], fontsize=8.5)
    ax.set_ylim(5, 1e5)
    fs.axlabels(ax, "", None, "静音时负载上的载波功率", "mW")
    feng = 1 / (2 * np.pi * np.sqrt(2 * 100e-6 * 0.33e-6))
    print(f"[图 44-p3-3] 100 µH + 0.33 µF：f0 = {feng/1e3:.2f} kHz；载波功率 不加 {pr[0]:.0f} / 工程 {pr[1]:.1f} / 本节 {pr[2]:.1f} / Arduino {pr[3]:.1f} mW")
    assert pr[2] < pr[3] < pr[1] < pr[0]
    save(fig, "44_p3_3_lc_choice.png")


def p3_4():
    a = csv("ac.csv")
    f = a["f_Hz"]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.semilogx(f, 20 * np.log10(a["h_18ohm"]), color=fs.C["vout"], lw=1.8, label="接 10 Ω + 喇叭（18 Ω）")
    ax.semilogx(f, 20 * np.log10(a["h_noload"]), **fs.LS["third"], label="不接负载（空载）")   # 红紫色点划线，和橙色实线分得开
    fs.mark(ax, NUM["fnl"], 20 * np.log10(NUM["hnl"]), "{:.1f}", " dB", dx=6, dy=-4)
    ax.set_xlim(100, 2e5); ax.set_ylim(-45, 30)
    fs.axlabels(ax, "频率（对数横轴）", "Hz", "增益", "dB")
    ax.legend(loc="lower left", fontsize=8.5)
    ax.set_title(f"空载时在 {NUM['fnl']/1e3:.2f} kHz 处放大 {NUM['hnl']:.1f} 倍：没有电阻消耗能量", fontsize=9.5)
    print(f"[图 44-p3-4] 空载峰 {NUM['hnl']:.2f} 倍（{20*np.log10(NUM['hnl']):.1f} dB）@ {NUM['fnl']/1e3:.2f} kHz")
    save(fig, "44_p3_4_noload.png")


def p3_5():
    amp, il = EFF["amp_V"], EFF["il_pk_A"]
    p10 = EFF["p_load_total_W"] * R10 / RLOAD
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot(amp, il, "o-", color=fs.C["cur"], lw=1.8, label="电感电流峰值（SPICE）")
    fs.ref_h(ax, ISAT, f"RLB0913-221K 饱和电流 {ISAT} A", x=0.6)
    ax.axvspan(0, 1.5, color=fs.C["hi"], alpha=0.25, lw=0)
    ax.text(0.75, 0.08, "本节实验范围\n（信号源 ≤ 1.5 V 峰值）", ha="center", fontsize=8.5)
    i15 = int(np.argmin(np.abs(amp - 1.5)))
    fs.mark(ax, amp[i15], il[i15], "{:.2f}", " A", dx=-12, dy=8)
    fs.mark(ax, amp[-1], il[-1], "{:.2f}", " A", dx=-20, dy=8)
    ax.set_xlim(0, 2.7); ax.set_ylim(0, 0.75)
    fs.axlabels(ax, "信号源峰值", "V", "电流", "A")
    ax.legend(loc="lower right", fontsize=8.5)
    for a_, p in zip(amp, p10):
        print(f"[图 44-p3-5] 源 {a_:.2f} V：I_L,pk {il[list(amp).index(a_)]:.4f} A，10 Ω 上 {p:.3f} W，喇叭 {p*RSPK/R10:.3f} W")
    assert il[-1] < ISAT
    save(fig, "44_p3_5_inductor_peak.png")


# =============================== page4 动手实验篇 ===============================
# 面包板工具（与 43_figs.py 同一套画法，复制过来，不 import 别的节点脚本）
BB_Y = {r: 5.6 - i for i, r in enumerate("abcde")}
BB_Y.update({r: -1.4 - i for i, r in enumerate("fghij")})
BB_Y.update({"T+": 8.6, "T-": 7.7, "B-": -6.7, "B+": -7.6})
WIRE = dict(pos=(fs.C["bad"], "正电源"), gnd=("#000000", "地（0 V）"), neg=(fs.C["third"], "负电源"),
            sig=(fs.C["vin"], "输入信号"), out=(fs.C["vout"], "输出"), fb=(fs.C["fb"], "反馈 / 其他连线"))



# ---------- 图 44-p3-6：走线示意（星形接地） ----------
def p3_6():
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.set_xlim(0, 17); ax.set_ylim(-0.6, 9.4); ax.set_aspect("equal"); ax.axis("off")
    def box(x, y, w, h, t, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec="0.3", lw=1.0))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=9)
    box(0.3, 6.6, 3.4, 2.0, "12 V 电源\n（限流 0.2 A）", "#e6f0f8")
    box(0.3, 0.4, 5.6, 3.0, "面包板前级\nTL072 ×2、LM393\n（节点 t、s 在这里）", "#f7f5ef")
    box(7.4, 3.2, 3.0, 3.0, "DRV8871\n模块", "#e8e8e8")
    ax.add_patch(Rectangle((11.2, 5.2), 1.2, 0.5, fc="#5b5b5b")); ax.text(11.8, 5.95, "L1", ha="center", fontsize=8.5)
    ax.add_patch(Rectangle((11.2, 3.7), 1.2, 0.5, fc="#5b5b5b")); ax.text(11.8, 3.35, "L2", ha="center", fontsize=8.5)
    ax.plot([10.4, 11.2], [5.45, 5.45], color=fs.C["vout"], lw=2.6); ax.plot([10.4, 11.2], [3.95, 3.95], color=fs.C["vout"], lw=2.6)
    ax.plot([12.4, 13.4], [5.45, 5.45], "k", lw=1.6); ax.plot([12.4, 13.4], [3.95, 3.95], "k", lw=1.6)
    ax.plot([13.0, 13.0], [5.45, 4.85], "k", lw=1.2); ax.plot([13.0, 13.0], [4.55, 3.95], "k", lw=1.2)
    ax.plot([12.75, 13.25], [4.85, 4.85], "k", lw=2); ax.plot([12.75, 13.25], [4.55, 4.55], "k", lw=2)
    ax.text(12.7, 4.7, "Cf", fontsize=8.5, va="center", ha="right")
    # 绞合负载线
    xx = np.linspace(13.4, 15.2, 200)
    ax.plot(xx, 4.7 + 0.75 * np.cos(np.pi * (xx - 13.4) / 0.3), "k", lw=1.2)
    ax.plot(xx, 4.7 - 0.75 * np.cos(np.pi * (xx - 13.4) / 0.3), "k", lw=1.2)
    box(15.2, 3.7, 1.6, 2.0, "负载\n18 Ω", "#fdeccf")
    ax.text(14.3, 6.0, "负载线绞合", ha="center", fontsize=8.5)
    ax.annotate("", xy=(10.4, 2.7), xytext=(13.0, 2.7), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(11.7, 2.5, "OUT→L→Cf 越短越好", ha="center", va="top", fontsize=8.5, color=fs.C["vout"])
    # 星形接地点
    sx, sy = 2.8, 6.6
    ax.add_patch(Circle((sx, sy), 0.2, fc="k", zorder=5))
    ax.text(sx + 0.3, sy - 0.45, "星形接地点\n（电源负极端子）", fontsize=8.5, va="top")
    ax.plot([sx, sx, 9.8, 9.8], [sy, 7.7, 7.7, 6.2], "k", lw=3.2)
    ax.text(6.3, 7.85, "DRV8871 GND：单独一根粗线", ha="center", va="bottom", fontsize=8.5)
    ax.plot([sx, 1.6, 1.6], [sy, sy, 3.4], "k", lw=1.4)
    ax.text(1.45, 5.0, "前级 GND", ha="right", va="center", fontsize=8.5)
    # VM + 退耦
    ax.plot([1.0, 1.0, 7.4], [8.6, 9.0, 9.0], color=fs.C["bad"], lw=1.6)
    ax.plot([7.4, 7.9, 7.9], [9.0, 9.0, 6.2], color=fs.C["bad"], lw=1.6)
    ax.text(10.6, 8.4, "VM（红线）端子旁紧贴\n100 µF + 100 nF；粗黑线是 GND", fontsize=8.5, va="center")
    # 开关信号 IN1/IN2 与 t、s 保持距离
    ax.plot([5.9, 7.4], [2.6, 3.8], color=fs.C["vout"], lw=2.0); ax.plot([5.9, 7.4], [2.2, 3.5], color=fs.C["vout"], lw=2.0)
    ax.text(6.5, 1.6, "IN1、IN2（开关线）\n别贴着 t、s 走", fontsize=8.5, color=fs.C["vout"])
    ax.set_title("走线：开关回路短、两路 GND 只在电源负极相遇、负载线绞合", fontsize=10)
    print("[图 44-p3-6] 走线示意：星形接地点 = 电源负极；DRV8871 GND 单独回；VM 旁 100 µF + 100 nF")
    save(fig, "44_p3_6_layout.png")


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
            col = fs.C["third"] if lab == "+5 V" else fs.C["bad"] if lab.startswith("+") else ("#000000" if lab in ("−", "GND", "0 V") else fs.C["third"])
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

    def module(self, x, y, w, h, label, fc="#e6f0f8"):
        """面包板外的模块（电池、信号源、继电器模块等），返回方框中心。"""
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec="0.3",
                                         lw=1.0, zorder=6))
        self.ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8.5, zorder=7)
        return x + w / 2, y + h / 2

    def note(self, x, y, text, **kw):
        kw.setdefault("fontsize", 8)
        kw.setdefault("zorder", 8)
        self.ax.text(x, y, text, **kw)

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

YEL = fs.C["hi"]


def bbp(bb, hole, text, edge="k"):
    """面包板上的测量点：黄色圆圈写编号，红边 = 红表笔插这里，黑边 = 黑表笔插这里。"""
    x, y = bb.xy(hole) if isinstance(hole, str) else hole
    bb.ax.add_patch(Circle((x, y), 0.36, fc=YEL, ec=edge, lw=1.6, zorder=9))
    bb.ax.text(x, y, text, ha="center", va="center", fontsize=8.5, zorder=10)



WIRE.clear()
WIRE.update(pos=(fs.C["bad"], "+12 V"), gnd=("#000000", "GND"), v5=(fs.C["third"], "+5 V"),
            mid=(fs.C["fb"], "中点参考 V_MID"), tri=(fs.C["cur"], "三角波 / 方波"),
            sig=(fs.C["vin"], "音频 s"), pwm=(fs.C["vout"], "开关信号 / 功率输出"))


# ---------- 图 44-p4-1：面包板 ----------
def p4_1():
    bb = Breadboard(36, "D 类功放面包板：U1 三角波（TL072）、U2 中点参考（TL072）、U3 双比较器（LM393）；DRV8871 模块、LC、负载在板外",
                    size=(13.0, 7.6), rails=("+12 V", "GND", "GND", "+5 V"))
    ax = bb.ax
    ax.set_xlim(-4.6, 58.6)
    ax.set_ylim(-16.6, 13.4)

    def P(a, b, kind, t):                   # 元件体上写短代号，数值见下方元件表
        bb.part(a, b, "", kind)
        (x1, y1), (x2, y2) = bb.xy(a), bb.xy(b)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, t, ha="center", va="center", fontsize=5.6, zorder=8,
                color="w" if kind == "E" else "k")

    tl = {1: "1OUT", 2: "1IN−", 3: "1IN+", 4: "GND", 5: "2IN+", 6: "2IN−", 7: "2OUT", 8: "V+"}
    bb.chip(2, "U1 TL072", 8, names=tl)
    bb.chip(13, "U2 TL072", 8, names=tl)
    bb.chip(26, "U3 LM393", 8, names=tl)
    for c in (2, 13, 26):
        bb.wire(f"a{c}", f"T+{c}", "pos")
    for c in (5, 16, 29):
        bb.wire(f"j{c}", f"B-{c}", "gnd")
    for c in (3, 14, 27):                                          # 每片芯片 V+ 旁 100 nF 退耦：跨 +12 V 轨与 GND 轨
        P(f"T+{c}", f"T-{c}", "C", "100n")
    # ---- U1：1 组积分器（下半），2 组施密特触发器（上半） ----
    P("h2", "h3", "C", "Ci")                                       # Cint：1OUT(tri) — 1IN−
    bb.wire("b3", "b7", "tri", via=[(3, 5.1), (7, 5.1)])          # 2OUT(方波) → 第 7 列上半
    P("d7", "g7", "R", "Ri")                                       # Rint 跨凹槽
    bb.wire("i7", "i3", "tri", via=[(7, -3.9), (3, -3.9)])        # → 1IN−（第 3 列下半）
    P("a3", "a5", "R", "Rs2")
    bb.wire("c5", "c8", "tri", via=[(5, 3.1), (8, 3.1)])          # 2IN+(sp) → 第 8 列上半
    P("d8", "g8", "R", "Rs1")
    bb.wire("i2", "i8", "tri", via=[(2, -4.9), (8, -4.9)])        # 三角波 → 第 8 列下半
    # ---- U2：2 组 = V_MID 缓冲（上半），1 组闲置接跟随器（下半） ----
    P("T+16", "a16", "R", "R1")
    P("b16", "b17", "R", "R2")
    P("c16", "c17", "E", "Cd")
    bb.wire("a17", "T-17", "gnd")
    bb.wire("c14", "c15", "mid")                                  # 2OUT 接 2IN−
    bb.wire("d14", "d10", "mid", via=[(14, 2.1), (10, 2.1)])
    bb.wire("b10", "b4", "mid", via=[(10, 4.1), (4, 4.1)])        # → U1 6 脚
    bb.wire("e10", "f10", "mid")
    bb.wire("h10", "h4", "mid", via=[(10, -2.9), (4, -2.9)])      # → U1 3 脚
    bb.wire("g13", "g14", "mid")
    bb.wire("g10", "g15", "mid", via=[(10, -1.9), (15, -1.9)])
    bb.wire("b14", "b20", "mid", via=[(14, 4.1), (20, 4.1)])
    # ---- 三角波交流耦合、输入、两路比较 ----
    bb.wire("h8", "h18", "tri", via=[(8, -3.9), (18, -3.9)])
    P("j18", "j19", "C", "Ct")
    P("d20", "d19", "R", "Rt")
    bb.wire("e19", "f19", "tri")
    P("c20", "c21", "R", "Rn2")
    bb.wire("e21", "f21", "sig")
    P("b21", "b22", "C", "Cin")
    P("c22", "c23", "R", "Rn1")
    bb.wire("d21", "d28", "sig", via=[(21, 2.1), (28, 2.1)])
    bb.wire("c19", "c29", "tri", via=[(19, 3.1), (29, 3.1)])
    bb.wire("g21", "g28", "sig", via=[(21, -1.9), (28, -1.9)])
    bb.wire("h19", "h27", "tri", via=[(19, -2.9), (27, -2.9)])
    # ---- 比较器输出 + 上拉 ----
    bb.wire("i26", "i32", "pwm", via=[(26, -4.9), (32, -4.9)])
    bb.wire("a27", "g34", "pwm", via=[(27, 6.6), (34.5, 6.6), (34.5, -1.9), (34, -1.9)])
    P("j32", "B+32", "R", "Rp")
    P("j34", "B+34", "R", "Rp")
    bb.wire("T-35", "B-35", "gnd", via=[(35.6, 7.7), (35.6, -6.7)])
    # ---- 板外：DRV8871、电源、电流表 ----
    bb.module(37.5, -6.2, 6.4, 6.6, "DRV8871\n模块\n\nVM 12 V", fc="#e8e8e8")
    bb.wire("h32", (37.5, -2.9), "pwm", via=[(32, -2.9)])
    bb.note(37.7, -2.9, "IN1", fontsize=6.5, va="center", zorder=9)
    bb.wire("h34", (37.5, -3.9), "pwm", via=[(34, -3.9)])
    bb.note(37.7, -3.9, "IN2", fontsize=6.5, va="center", zorder=9)
    bb.note(40.7, -5.6, "GND", fontsize=6.5, va="center", ha="center", zorder=9)
    # VM 退耦：100 µF 电解（+ 接 VM）+ 100 nF，紧贴模块 VM / GND 端子
    bb.wire((42.4, 2.0), (38.8, 2.0), "pos")
    bb.part((40.4, 2.0), (40.4, 0.4), "", "E")
    ax.text(41.05, 1.25, "+", color=fs.C["bad"], fontsize=11, fontweight="bold", ha="center", va="center", zorder=9)   # 电解正极朝 VM
    bb.part((38.8, 2.0), (38.8, 0.4), "", "C")
    bb.note(37.6, 2.5, "VM 旁：100 µF（+ 接 VM）、100 nF，另一脚接模块 GND", fontsize=6.5, va="bottom")
    # DRV8871 GND：单独一根粗线绕右侧回电源负极（星形接地），不接面包板 GND 轨
    ax.plot([40.7, 40.7, 58.2, 58.2, 39.4, 39.4], [-6.2, -7.2, -7.2, 12.4, 12.4, 11.8],
            color="#000000", lw=4.2, solid_capstyle="round", zorder=5)
    bb.note(48.8, 12.6, "星形接地：两根 GND 线都回电源负极", fontsize=7.5, ha="center", va="bottom")
    bb.module(36.8, 9.6, 7.4, 2.2, "12 V 直流电源（限流 0.2 A）", fc="#e6f0f8")
    bb.wire((37.6, 9.6), "T+31", "pos", via=[(37.6, 9.2), (31, 9.2)])
    bb.wire((38.6, 9.6), "T-33", "gnd", via=[(38.6, 8.15), (33, 8.15)])
    bb.module(40.4, 3.6, 4.8, 1.8, "电流表（直流 200 mA 档）", fc="#dff0fb")
    bb.wire((43.6, 9.6), (43.6, 5.4), "pos")
    bb.wire((42.4, 3.6), (42.4, 0.4), "pos")
    bb.note(42.7, 1.8, "VM", fontsize=7.5)
    # ---- 板外：LC + 负载 ----
    yO1, yO2 = -1.5, -4.8
    for y, nm, o in ((yO1, "L1", "OUT1"), (yO2, "L2", "OUT2")):
        bb.wire((43.9, y), (45.6, y), "pwm")
        bb.note(44.0, y + 0.3, o, fontsize=6.5)
        ax.add_patch(FancyBboxPatch((45.6, y - 0.45), 2.6, 0.9, boxstyle="round,pad=0.05", fc="#5b5b5b", ec="k", zorder=6))
        ax.text(46.9, y, nm, color="w", ha="center", va="center", fontsize=7.5, zorder=7)
        bb.wire((48.2, y), (51.4, y), "pwm")
    ax.add_patch(FancyBboxPatch((49.2, -3.65), 1.2, 1.0, boxstyle="round,pad=0.05", fc="#f2d27a", ec="0.2", zorder=6))
    ax.plot([49.8, 49.8], [yO1, -2.65], color="0.35", lw=1.2, zorder=5)
    ax.plot([49.8, 49.8], [-3.65, yO2], color="0.35", lw=1.2, zorder=5)
    ax.text(49.8, -3.15, "Cf", ha="center", va="center", fontsize=7, zorder=7)
    bb.module(51.4, -5.6, 6.2, 4.9, "10 Ω / 5 W 电阻\n串 8 Ω 喇叭\n（先用假负载）\n两端都不接地！", fc="#fdeccf")
    # ---- 信号源、Arduino 5 V ----
    bb.module(16.4, 10.0, 9.6, 2.2, "信号源（手机 / 信号发生器），先把音量调到 0", fc="#e6f0f8")
    bb.wire((23.0, 10.0), "a23", "sig")
    bb.wire((18.2, 10.0), "T-22", "gnd", via=[(18.2, 9.5), (22, 9.5)])
    bb.module(-4.2, -12.2, 8.2, 2.2, "Arduino（USB 供电）\n只当 5 V 电源", fc="#e6f0f8")
    bb.wire((1.0, -10.0), "B+1", "v5")
    bb.wire((3.0, -10.0), "B-3", "gnd")
    # ---- 测量点 ----
    bbp(bb, "a20", "①")
    bbp(bb, "j2", "②")
    bbp(bb, "g32", "③")
    bbp(bb, "i34", "④")
    parts = ("元件表：R1、R2 10 kΩ　Cd 10 µF 电解（+ 接 c16）　Ri（Rint）4.7 kΩ　Ci（Cint）2.2 nF　Rs1 10 kΩ　Rs2 22 kΩ　"
             "Ct 100 nF　Rt 100 kΩ　Cin 1 µF　Rn1（Rin1）4.7 kΩ　Rn2（Rin2）10 kΩ　Rp 上拉 1 kΩ ×2\n"
             "板外：L1、L2 功率电感 RLB0913-221K（220 µH，饱和电流 0.64 A），不用色环电感；Cf 0.68 µF 薄膜电容；"
             "10 Ω / 5 W 功率电阻 + 8 Ω 喇叭（实验 A、B、C 先用 8 Ω / 5 W 假负载代替）\n"
             "测量点（黑表笔接 GND）：① V_MID　② 三角波　③ IN1　④ IN2。上下两条 GND 轨在第 35 列连通；+12 V 只在上排，+5 V 只在下排。\n"
             "退耦：第 3、14、27 列各一只 100 nF 跨 +12 V 轨与 GND 轨；DRV8871 的 GND 用粗线单独回电源负极（星形接地），不接面包板 GND 轨。")
    ax.text(4.8, -9.2, parts, ha="left", va="top", fontsize=7.6, linespacing=1.6)
    bb.legend()
    print("[图 44-p4-1] U1 第 2 列、U2 第 13 列、U3 第 26 列；V_MID 第 4/10/14/20 列；t 第 19 列；s 第 21 列；IN1 第 32 列；IN2 第 34 列")
    bb.save(N, "44_p4_1_breadboard.png")


# =============================== page4 原理图 ===============================
def _vmid(d, xy, side="down"):
    """在 xy 处画一小段线和「V_MID」标签（中点参考，蓝绿色）。"""
    x, y = xy
    if side == "down":
        d += elm.Line().at((x, y)).to((x, y - 0.5)).color(fs.C["fb"])
        lab(d, (x, y - 0.8), "$V_{MID}$", ha="center", fs_=9.5, color=fs.C["fb"])
    elif side == "left":
        d += elm.Line().at((x, y)).to((x - 0.6, y)).color(fs.C["fb"])
        lab(d, (x - 0.7, y), "$V_{MID}$", ha="right", fs_=9.5, color=fs.C["fb"])
    else:
        d += elm.Line().at((x, y)).to((x, y + 0.5)).color(fs.C["fb"])
        lab(d, (x, y + 0.8), "$V_{MID}$", ha="center", fs_=9.5, color=fs.C["fb"])


# ---------- 图 44-p4-2：对照原理图（测量点与面包板列号） ----------
def _pins(d, oa, nm, npl, nout, sup=True):
    """运放/比较器引脚号：小号数字写在引线上方（不画圆圈，免得和测量点①–④混）。"""
    for xy, t in ((oa.in1, nm), (oa.in2, npl)):
        lab(d, (xy[0] + 0.3, xy[1] + 0.25), t, ha="center", fs_=7.5, color=GRAY)
    lab(d, (oa.out[0] - 0.3, oa.out[1] + 0.25), nout, ha="center", fs_=7.5, color=GRAY)
    if sup:
        lab(d, (oa.vd[0] + 0.15, oa.vd[1] + 0.05), "8→+12 V", ha="left", fs_=7, color=GRAY)
        lab(d, (oa.vs[0] + 0.15, oa.vs[1] - 0.05), "4→GND", ha="left", fs_=7, color=GRAY)


def _full_schem(zones=False):
    """整机原理图。zones=False：page4 对照图（带测量点）；zones=True：page2 五块分区图。"""
    with drawing(fontsize=10) as d:
        # ---- U1A 积分器：方波 sq → Rint → ni；Cint 跨 ni 与 tri ----
        u1a = elm.Opamp(leads=True).right().at((2, 4)).anchor("in1").label("U1A\nTL072", loc="center", ofst=(0.3, 0), fontsize=9)
        d += u1a
        _pins(d, u1a, "2", "3", "1")
        d += elm.Resistor().endpoints((-1.6, 4), (1.4, 4)).label("Rint 4.7 kΩ", loc="top", fontsize=9)
        d += elm.Line().at((1.4, 4)).to((2, 4))
        d += elm.Dot().at((1.4, 4))
        d += elm.Line().at((1.4, 4)).to((1.4, 5.6))
        d += elm.Capacitor().endpoints((1.4, 5.6), (5.9, 5.6)).label("Cint 2.2 nF", loc="top", fontsize=9)
        d += elm.Line().at((5.9, 5.6)).to((5.9, 3.375))
        d += elm.Line().at(u1a.out).to((5.9, 3.375))
        d += elm.Dot().at((5.9, 3.375))
        d += elm.Line().at(u1a.in2).to((1.4, 2.75))
        _vmid(d, (1.4, 2.75), "left")
        # ---- U1B 施密特：+ = sp（Rs1 来自 tri，Rs2 来自 sq），− = V_MID ----
        u1b = elm.Opamp(leads=True).right().at((9.5, 3.0)).anchor("in1").label("U1B", loc="center", ofst=(0.3, 0), fontsize=9)
        d += u1b
        _pins(d, u1b, "6", "5", "7", sup=False)
        d += elm.Line().at(u1b.in1).to((9.0, 3.0))
        d += elm.Line().at((9.0, 3.0)).to((9.0, 3.6)).color(fs.C["fb"])
        lab(d, (9.0, 3.9), "$V_{MID}$", ha="center", fs_=9.5, color=fs.C["fb"])
        d += elm.Line().at((5.9, 3.375)).to((5.9, 1.75))
        d += elm.Resistor().endpoints((5.9, 1.75), (8.6, 1.75)).label("Rs1 10 kΩ", loc="top", fontsize=9)
        d += elm.Line().at((8.6, 1.75)).to(u1b.in2)
        d += elm.Dot().at((8.9, 1.75))
        d += elm.Line().at((8.9, 1.75)).to((8.9, 0.6))
        d += elm.Resistor().endpoints((8.9, 0.6), (12.4, 0.6)).label("Rs2 22 kΩ", loc="bottom", fontsize=9)
        d += elm.Line().at((12.4, 0.6)).to((13.6, 0.6))
        d += elm.Line().at(u1b.out).to((13.6, 2.375))
        d += elm.Dot().at((13.6, 2.375))
        d += elm.Line().at((13.6, 2.375)).to((13.6, -0.4))
        d += elm.Dot().at((13.6, 0.6))
        d += elm.Line().at((13.6, -0.4)).to((-1.6, -0.4))
        d += elm.Line().at((-1.6, -0.4)).to((-1.6, 4))
        lab(d, (13.8, 1.5), "方波 sq", ha="left", fs_=9)
        # ---- 三角波交流耦合到 V_MID：Ct + Rt，节点 t ----
        d += elm.Dot().at((5.9, 4.6))
        d += elm.Line().at((5.9, 4.6)).to((14.5, 4.6))
        lab(d, (6.1, 4.95), "三角波 tri", ha="left", fs_=9)
        d += elm.Capacitor().endpoints((14.5, 4.6), (17.0, 4.6)).label("Ct 100 nF", loc="top", fontsize=9)
        d += elm.Line().at((17.0, 4.6)).to((21, 4.6))
        d += elm.Dot().at((17.5, 4.6))
        d += elm.Resistor().endpoints((17.5, 4.6), (17.5, 2.1)).label("Rt\n100 kΩ", loc="bottom", fontsize=9)
        _vmid(d, (17.5, 2.1), "down")
        lab(d, (17.6, 5.0), "t", ha="left", fs_=10)
        # ---- 输入：信号源 → Rin1 → Cin → s；Rin2 到 V_MID ----
        d += elm.SourceSin().endpoints((9.0, -5.6), (9.0, -3.2)).label("信号源\n400 Hz", loc="bottom", fontsize=9)
        d += elm.Line().at((9.0, -3.2)).to((9.0, -2.5))
        d += elm.Ground().at((9.0, -5.6))
        d += elm.Resistor().endpoints((9.0, -2.5), (11.8, -2.5)).label("Rin1 4.7 kΩ", loc="top", fontsize=9)
        d += elm.Capacitor().endpoints((11.8, -2.5), (14.3, -2.5)).label("Cin 1 µF", loc="top", fontsize=9)
        d += elm.Line().at((14.3, -2.5)).to((21, -2.5))
        d += elm.Dot().at((15.0, -2.5))
        lab(d, (15.1, -2.15), "s", ha="left", fs_=10)
        d += elm.Resistor().endpoints((15.0, -2.5), (15.0, -5.0)).label("Rin2\n10 kΩ", loc="bottom", fontsize=9)
        _vmid(d, (15.0, -5.0), "down")
        # ---- LM393：A（− = t，+ = s）→ IN1；B（− = s，+ = t）→ IN2 ----
        u3a = elm.Opamp(leads=True).right().at((21, 4.6)).anchor("in1").label("U3A\nLM393", loc="center", ofst=(0.3, 0), fontsize=9)
        d += u3a
        _pins(d, u3a, "2", "3", "1")
        u3b = elm.Opamp(leads=True).right().at((21, -2.5)).anchor("in1").label("U3B", loc="center", ofst=(0.3, 0), fontsize=9)
        d += u3b
        _pins(d, u3b, "6", "5", "7", sup=False)
        d += elm.Dot().at((19.5, -2.5))
        d += elm.Line().at((19.5, -2.5)).to((19.5, 3.35))
        d += elm.Line().at((19.5, 3.35)).to(u3a.in2)
        d += elm.Dot().at((18.5, 4.6))
        d += elm.Line().at((18.5, 4.6)).to((18.5, -3.75))
        d += elm.Line().at((18.5, -3.75)).to(u3b.in2)
        lab(d, (21.2, -5.0), "LM393 的 8 脚 VCC 接 +12 V，4 脚 GND 接 GND", ha="left", fs_=8.5, color="#555555")
        # ---- 上拉 1 kΩ 到 Arduino 5 V，送 DRV8871 的 IN1 / IN2 ----
        for y, nm in ((u3a.out[1], "IN1"), (u3b.out[1], "IN2")):
            xo = u3a.out[0]
            d += elm.Line().at((xo, y)).to((28, y))
            d += elm.Dot().at((25.6, y))
            d += elm.Resistor().endpoints((25.6, y), (25.6, y + 2.1)).label("1 kΩ", loc="bottom", fontsize=9)
            d += elm.Vdd().at((25.6, y + 2.1)).label("+5 V（Arduino）", fontsize=8.5)
        # ---- DRV8871 模块 ----
        x0, x1, yb, yt = 28.0, 32.0, -4.6, 5.2
        for a, b in (((x0, yb), (x1, yb)), ((x1, yb), (x1, yt)), ((x1, yt), (x0, yt)), ((x0, yt), (x0, yb))):
            d += elm.Line().endpoints(a, b).linewidth(1.6)
        lab(d, (30.0, 0.6), "DRV8871\n模块\n（H 桥）", ha="center", fs_=10)
        lab(d, (28.15, u3a.out[1]), "IN1", ha="left", fs_=8.5)
        lab(d, (28.15, u3b.out[1]), "IN2", ha="left", fs_=8.5)
        lab(d, (31.85, 3.0), "OUT1", ha="right", fs_=8.5)
        lab(d, (31.85, -2.0), "OUT2", ha="right", fs_=8.5)
        lab(d, (30.0, yt - 0.35), "VM", ha="center", fs_=8.5)
        lab(d, (30.0, yb + 0.35), "GND", ha="center", fs_=8.5)
        d += elm.Line().at((30.0, yt)).to((30.0, 6.4))
        d += elm.Dot().at((30.0, 6.4))
        d += elm.MeterA().endpoints((30.0, 6.4), (30.0, 8.4)).label("电流表\n直流 200 mA 档", loc="top", fontsize=8.5)
        d += elm.Vdd().at((30.0, 8.4)).label("+12 V", fontsize=9)
        d += elm.Line().at((30.0, 6.4)).to((35.6, 6.4))
        for xc, nm, pol in ((33.0, "100 µF\n25 V", True), (35.6, "100 nF", False)):
            d += elm.Dot().at((xc, 6.4)) if xc < 35.6 else elm.Line().at((xc, 6.4)).to((xc, 6.4))
            d += elm.Capacitor(polar=pol).endpoints((xc, 6.4), (xc, 4.6)).label(nm, loc="bottom", fontsize=8.5)
            d += elm.Ground().at((xc, 4.6))
        lab(d, (30.3, 6.75), "VM", ha="left", fs_=8.5)
        d += elm.Line().at((30.0, yb)).to((30.0, -5.4))
        d += elm.Ground().at((30.0, -5.4))
        # ---- LC 滤波 + 负载（BTL：两端都不接地） ----
        d += elm.Inductor2().endpoints((32.0, 3.0), (35.2, 3.0)).label("L1 220 µH", loc="top", fontsize=9)
        d += elm.Inductor2().endpoints((32.0, -2.0), (35.2, -2.0)).label("L2 220 µH", loc="bottom", fontsize=9)
        d += elm.Line().at((35.2, 3.0)).to((38.8, 3.0))
        d += elm.Line().at((35.2, -2.0)).to((38.8, -2.0))
        d += elm.Dot().at((36.2, 3.0)); d += elm.Dot().at((36.2, -2.0))
        d += elm.Capacitor().endpoints((36.2, 3.0), (36.2, -2.0)).label("Cf\n0.68 µF", loc="bottom", fontsize=9)
        d += elm.Resistor().endpoints((38.8, 3.0), (38.8, 0.5)).label("10 Ω / 5 W", loc="bottom", fontsize=9)
        d += elm.Resistor().endpoints((38.8, 0.5), (38.8, -2.0)).label("8 Ω 喇叭\n（或 8 Ω 电阻）", loc="bottom", fontsize=9)
        lab(d, (34.0, -3.6), "BTL：OUT1、OUT2 都不接地\n示波器量 CH1 − CH2", ha="center", fs_=9, color=fs.C["bad"])
        # ---- 中点参考 V_MID：R1、R2、Cd + U2B 跟随器 ----
        d += elm.Vdd().at((-1.0, -1.6)).label("+12 V", fontsize=9)
        d += elm.Resistor().endpoints((-1.0, -1.6), (-1.0, -4.0)).label("R1 10 kΩ", loc="top", fontsize=9)
        d += elm.Resistor().endpoints((-1.0, -4.0), (-1.0, -6.4)).label("R2 10 kΩ", loc="top", fontsize=9)
        d += elm.Ground().at((-1.0, -6.4))
        d += elm.Dot().at((-1.0, -4.0))
        d += elm.Line().at((-1.0, -4.0)).to((0.4, -4.0))
        d += elm.Dot().at((0.4, -4.0))
        d += elm.Capacitor().endpoints((0.4, -4.0), (0.4, -6.4)).label("Cd\n10 µF", loc="bottom", fontsize=9)
        d += elm.Ground().at((0.4, -6.4))
        u2 = elm.Opamp(leads=True).right().at((1.5, -4.0)).anchor("in2").label("U2B", loc="center", ofst=(0.3, 0), fontsize=9)
        d += u2
        _pins(d, u2, "6", "5", "7")
        d += elm.Line().at((0.4, -4.0)).to(u2.in2)
        d += elm.Line().at(u2.in1).to((1.2, u2.in1[1]))
        d += elm.Line().at((1.2, u2.in1[1])).to((1.2, -1.6))
        d += elm.Line().at((1.2, -1.6)).to((5.4, -1.6))
        d += elm.Line().at((5.4, -1.6)).to((5.4, u2.out[1]))
        d += elm.Line().at(u2.out).to((6.3, u2.out[1])).color(fs.C["fb"])
        d += elm.Dot().at((5.4, u2.out[1]))
        lab(d, (6.4, u2.out[1]), "$V_{MID}$ ≈ 6 V" if zones else "$V_{MID}$ ≈ 6 V\n（送到各个 $V_{MID}$ 标签）", ha="left", fs_=9, color=fs.C["fb"])
        if zones:
            for (xa, ya, xb, yb_, tx) in ZONES:
                for a, b in (((xa, ya), (xb, ya)), ((xb, ya), (xb, yb_)), ((xb, yb_), (xa, yb_)), ((xa, yb_), (xa, ya))):
                    d += elm.Line().endpoints(a, b).linestyle("--").color("#888888").linewidth(1.2)
                d += elm.Label().at((xa + 0.2, yb_ - 0.35)).label(tx, fontsize=10, color="#555555", halign="left", valign="center")
            print("[图 44-p2-1] 整机原理图五块分区：" + "；".join(z[4].replace("\n", "") for z in ZONES))
            save_schem(d, N, "44_p2_1_schem_blocks.png")
            _shrink("44_p2_1_schem_blocks.png")
            return
        # ---- 测量点 ----
        probe(d, (5.4, u2.out[1]), "①", dx=0.0, dy=-1.0)
        probe(d, (5.9, 4.6), "②", dx=-0.9, dy=0.8)
        probe(d, (26.6, u3a.out[1]), "③", dx=0.3, dy=-0.9)
        probe(d, (26.6, u3b.out[1]), "④", dx=0.3, dy=-0.9)
        note(d, (-1.5, -8.6),
             "测量点（黄圈，与面包板图同号）：① 中点参考 $V_{MID}$　② 三角波 tri　③ IN1　④ IN2，黑表笔都接 GND。\n"
             "U2A 没用到：3 脚接 $V_{MID}$，2 脚接 1 脚；TL072 和 LM393 都是 8 脚接 +12 V、4 脚接 GND。灰色小数字是引脚号。\n"
             "负载两端都不接地：OUT1、OUT2 不能碰 GND，也不能用示波器地夹去夹。")
    print("[图 44-p4-2] 对照原理图：①V_MID ②tri ③IN1 ④IN2；BTL 负载 10 Ω + 8 Ω；L1/L2 220 µH，Cf 0.68 µF；VM 并 100 µF + 100 nF")
    save_schem(d, N, "44_p4_2_schem_lab.png")
    _shrink("44_p4_2_schem_lab.png")


# 分区框：(x 左, y 下, x 右, y 上, 标签)
ZONES = [(-2.3, -7.6, 7.9, -1.0, "1 中点参考"),
         (-2.3, -0.75, 18.1, 6.6, "2 三角波发生器"),
         (8.1, -7.6, 17.0, -1.3, "3 输入"),
         (18.3, -5.8, 27.6, 7.6, "4 比较器 + 上拉"),
         (27.8, -6.6, 41.6, 9.6, "5 H 桥 + LC + 负载")]


def p4_2():
    _full_schem(False)


# ---------- 图 44-p2-1：整机原理图（五块分区） ----------
def p2_1():
    _full_schem(True)


# ---------- 图 44-p3-7：反例——想用 1 MΩ 从 IN1 拉回 s 做迟滞（局部原理图，不要这样接） ----------
HY_IN1, HY_S, HY_VD = 2.47321, 5.96353, -0.144921   # spice/44/hyst.cir 的 30～40 ms 平均（ngspice）


def p3_7():
    i_hy = (HY_S - HY_IN1) / 1e6                       # 流过 1 MΩ 的平均电流
    print(f"[图 44-p3-7] 迟滞反例：IN1 平均 {HY_IN1:.3f} V，s 平均 {HY_S:.3f} V（比 6 V 低 {(VMID-HY_S)*1e3:.1f} mV），"
          f"1 MΩ 上平均电流 {i_hy*1e6:.2f} µA，负载直流 {HY_VD:.3f} V")
    assert abs(i_hy * 1e6 - 3.49) < 0.01 and abs(HY_VD + 0.145) < 0.001
    with drawing(fontsize=10) as d:
        d += elm.Line().at((0, 4.6)).to((5, 4.6))
        lab(d, (0, 4.95), "来自三角波（t）", ha="left", fs_=9)
        lab(d, (4.6, 4.95), "t", ha="left", fs_=10)
        d += elm.SourceSin().endpoints((0, -1.0), (0, 1.4)).label("信号源", loc="bottom", fontsize=9)
        d += elm.Ground().at((0, -1.0))
        d += elm.Resistor().endpoints((0, 1.4), (2.4, 1.4)).label("Rin1 4.7 kΩ", loc="top", fontsize=9)
        d += elm.Capacitor().endpoints((2.4, 1.4), (4.4, 1.4)).label("Cin 1 µF", loc="top", fontsize=9)
        d += elm.Line().at((4.4, 1.4)).to((5.0, 1.4))
        d += elm.Dot().at((5.0, 1.4))
        lab(d, (5.1, 1.0), "s", ha="left", fs_=10)
        d += elm.Resistor().endpoints((5.0, 1.4), (5.0, -1.4)).label("Rin2\n10 kΩ", loc="bottom", fontsize=9)
        _vmid(d, (5.0, -1.4), "down")
        d += elm.Line().at((5.0, 1.4)).to((5.0, 3.35))
        u = elm.Opamp(leads=True).right().at((5.0, 4.6)).anchor("in1").label("U3A\nLM393", loc="center", ofst=(0.3, 0), fontsize=9)
        d += u
        d += elm.Line().at((5.0, 3.35)).to(u.in2)
        xo, yo = u.out
        d += elm.Line().at((xo, yo)).to((xo + 3.0, yo))
        d += elm.Dot().at((xo + 1.0, yo))
        d += elm.Resistor().endpoints((xo + 1.0, yo), (xo + 1.0, yo + 2.1)).label("1 kΩ", loc="bottom", fontsize=9)
        d += elm.Vdd().at((xo + 1.0, yo + 2.1)).label("+5 V", fontsize=9)
        lab(d, (xo + 3.1, yo), "IN1 → DRV8871", ha="left", fs_=9)
        # 反例：1 MΩ 从 IN1 拉回 s（朱红虚线）
        xr = xo + 2.2
        d += elm.Dot().at((xr, yo)).color(fs.C["bad"])
        d += elm.Line().at((xr, yo)).to((xr, -2.6)).color(fs.C["bad"]).linestyle("--")
        d += elm.Resistor().endpoints((xr, -2.6), (6.5, -2.6)).color(fs.C["bad"]).label("Rhy 1 MΩ", loc="bottom", fontsize=9)
        d += elm.Line().at((6.5, -2.6)).to((6.5, 0.6)).color(fs.C["bad"]).linestyle("--")
        d += elm.Line().at((6.5, 0.6)).to((5.0, 0.6)).color(fs.C["bad"]).linestyle("--")
        d += elm.Dot().at((5.0, 0.6)).color(fs.C["bad"])
        lab(d, (xr + 0.3, -0.6), "× 不要这样接", ha="left", fs_=10, color=fs.C["bad"])
        for k, txt in enumerate((f"IN1 平均约 {HY_IN1:.2f} V，s 平均约 {HY_S:.2f} V",
                                 f"→ 1 MΩ 一直往下拉 s，约 {i_hy*1e6:.1f} µA",
                                 f"→ s 比 6 V 低 {(VMID-HY_S)*1e3:.0f} mV，占空比偏离 50 %",
                                 f"→ 静音时负载直流约 −{abs(HY_VD):.3f} V（SPICE）")):
            lab(d, (xr + 0.3, -1.3 - 0.6 * k), txt, ha="left", fs_=8.5, color=fs.C["bad"])
    save_schem(d, N, "44_p3_7_hyst.png")
    _shrink("44_p3_7_hyst.png")


# ---------- 图 44-p4-3：示波器怎么夹——对的接法（CH1 − CH2）和错的接法（地夹夹输出） ----------
def p4_3():
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.9))
    for k, ax in enumerate(axs):
        ok = k == 0
        ax.set_xlim(0, 10); ax.set_ylim(-1.4, 8.6); ax.set_aspect("equal"); ax.axis("off")
        # DRV8871 模块 + LC + 负载（简化）
        ax.add_patch(FancyBboxPatch((0.3, 2.0), 2.2, 4.0, boxstyle="round,pad=0.05", fc=fs.C["fill"], ec=fs.C["edge"]))
        ax.text(1.4, 4.0, "DRV8871\n模块", ha="center", va="center", fontsize=9.5)
        ax.text(2.45, 5.3, "OUT1", ha="right", fontsize=8); ax.text(2.45, 2.5, "OUT2", ha="right", fontsize=8)
        ax.text(1.4, 2.25, "GND", ha="center", fontsize=8)
        ax.plot([2.5, 3.3], [5.4, 5.4], "k", lw=1.4); ax.plot([2.5, 3.3], [2.6, 2.6], "k", lw=1.4)
        for y, nm in ((5.4, "L1"), (2.6, "L2")):
            ax.add_patch(Rectangle((3.3, y - 0.22), 1.1, 0.44, fc="#c8a46e", ec="0.2"))
            ax.text(3.85, y + 0.35, nm, ha="center", fontsize=8)
            ax.plot([4.4, 6.6], [y, y], "k", lw=1.4)
        ax.plot([5.0, 5.0], [5.4, 4.2], "k", lw=1.2); ax.plot([5.0, 5.0], [3.8, 2.6], "k", lw=1.2)
        ax.plot([4.7, 5.3], [4.2, 4.2], "k", lw=2); ax.plot([4.7, 5.3], [3.8, 3.8], "k", lw=2)
        ax.text(5.4, 4.0, "Cf", fontsize=8, va="center")
        ax.add_patch(Rectangle((6.35, 3.2), 0.5, 1.6, fc="#f6e3b4", ec="0.2"))
        ax.text(6.6, 4.0, "负载\n18 Ω", ha="center", va="center", fontsize=7.5)
        ax.plot([6.6, 6.6], [5.4, 4.8], "k", lw=1.2); ax.plot([6.6, 6.6], [3.2, 2.6], "k", lw=1.2)
        ax.plot([1.4, 1.4], [2.0, 0.9], "k", lw=1.6)
        ax.plot([0.6, 2.2], [0.9, 0.9], "k", lw=2.2); ax.text(2.3, 0.9, "电源 GND", fontsize=8.5, va="center")
        # 示波器
        ax.add_patch(FancyBboxPatch((7.6, 5.2), 2.2, 2.4, boxstyle="round,pad=0.05", fc="#eeeeee", ec="0.3"))
        ax.text(8.7, 6.4, "示波器\nMATH：\nCH1 − CH2" if ok else "示波器\n只开 CH1", ha="center", va="center", fontsize=8.5)
        # 探头尖
        ax.plot([6.6, 7.6], [5.4, 6.9], color=fs.C["vout"], lw=1.8)
        ax.text(7.0, 6.5, "CH1 尖", color=fs.C["vout"], fontsize=8, ha="right")
        if ok:
            ax.plot([6.6, 7.3, 7.3, 7.6], [2.6, 2.6, 5.7, 5.7], color=fs.C["vin"], lw=1.8)
            ax.text(7.4, 2.9, "CH2 尖", color=fs.C["vin"], fontsize=8)
            for xg in (1.0, 1.7):            # 两只地夹都夹电源 GND
                ax.plot([xg, xg], [0.9, 0.35], color="k", lw=1.2, ls="--")
            ax.text(0.2, 0.15, "CH1、CH2 的地夹都只夹电源 GND", fontsize=8.5, color="k")
            ax.text(5.0, 8.15, "✓ 对：两只探头尖各接负载一端，地夹只夹 GND", ha="center", fontsize=10, color=fs.C["fb"], fontweight="bold")
        else:
            ax.plot([6.6, 7.3, 7.3], [2.6, 2.6, 1.6], color="k", lw=1.6, ls="--")
            ax.plot([7.3, 7.3], [1.6, 0.9], color=fs.C["bad"], lw=2.4)
            ax.plot([3.9, 7.3], [0.9, 0.9], color=fs.C["bad"], lw=2.4, ls=":")
            ax.text(7.45, 2.0, "CH1 地夹\n夹在 OUT2 上", color=fs.C["bad"], fontsize=8)
            ax.text(5.0, -0.25, "地夹经示波器电源线接大地，电源 GND 往往也接大地\n→ OUT2 被直接短到 GND", ha="center", va="top", fontsize=8, color=fs.C["bad"])
            ax.text(6.6, 1.65, "×", color=fs.C["bad"], fontsize=20, fontweight="bold", ha="center", va="center")
            ax.text(5.0, 8.15, "× 错：地夹夹在输出上", ha="center", fontsize=10, color=fs.C["bad"], fontweight="bold")
    print("[图 44-p4-3] 示波器：对 = CH1、CH2 尖接负载两端 + 地夹都夹 GND + MATH CH1−CH2；错 = 地夹夹 OUT2（把 OUT2 短到 GND）")
    save(fig, "44_p4_3_scope_hookup.png")


# ---------- 图 44-p4-4：示波器上应该看到什么（SPICE） ----------
def p4_4():
    wi, ws = csv("w_idle.csv"), csv("w_sig.csv")
    ti = (wi["t"] - wi["t"][0]) * 1e6
    m = ti < 80
    ts = (ws["t"] - ws["t"][0]) * 1e3
    fig, axs = plt.subplots(2, 1, figsize=(7.0, 5.6))
    axs[0].plot(ti[m], wi["o1"][m], color=fs.C["vout"], lw=1.4, label="CH1：OUT1（电感前）对 GND")
    axs[0].plot(ti[m], wi["o2"][m], color=fs.C["vin"], lw=1.2, ls="--", label="CH2：OUT2（电感前）对 GND")
    axs[0].set_ylim(-1.5, 16); axs[0].legend(loc="upper right", fontsize=8, ncols=2)
    fs.axlabels(axs[0], "时间", "µs", "电压", "V")
    p = 1e6 / FSW
    axs[0].set_title(f"A：没有信号，探头在电感前——两路互补方波，周期约 {p:.1f} µs（{FSW/1e3:.1f} kHz）", fontsize=9.5)
    vd = ws["vd"]
    ac = vd - np.mean(vd)
    axs[1].plot(ts, ac, color=fs.C["third"], lw=1.3, label="MATH：CH1 − CH2（负载两端）")
    vp = (np.max(ac) - np.min(ac)) / 2
    tt = ws["t"] - ws["t"][0]
    A = np.column_stack([np.sin(2 * np.pi * 400 * tt), np.cos(2 * np.pi * 400 * tt), np.ones_like(tt)])
    cs = np.linalg.lstsq(A, vd, rcond=None)[0]
    v1 = float(np.hypot(cs[0], cs[1]))              # 400 Hz 基波峰值（最小二乘拟合）
    axs[1].plot(ts, A @ cs - np.mean(vd), color="k", lw=1.0, ls="--", label=f"400 Hz 基波（拟合），峰值 {v1:.2f} V")
    axs[1].set_ylim(-4.5, 4.5); axs[1].legend(loc="upper right", fontsize=8)
    fs.axlabels(axs[1], "时间", "ms", "电压", "V")
    axs[1].set_title(f"B：信号源 1 V、400 Hz，探头在负载两端——正弦（基波峰值 {v1:.2f} V）叠着一层载波残余，最高 {vp:.2f} V", fontsize=9.5)
    print(f"[图 44-p4-4] 空载波周期 {p:.2f} µs；负载两端 CH1−CH2 峰值（含残余）{vp:.3f} V，基波拟合峰值 {v1:.3f} V，平均 {np.mean(vd)*1e3:.1f} mV")
    assert abs(v1 - 2.687) < 0.03
    save(fig, "44_p4_4_scope_expect.png")


# ---------- 图 44-p4-5：选做 D 接线（Arduino 代替比较器） ----------
def p4_5():
    with drawing(fontsize=10) as d:
        def rect(x0, y0, x1, y1, lw=1.6, ls="-"):
            for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
                d.add(elm.Line().endpoints(a, b).linewidth(lw).linestyle(ls))
        rect(0, 0, 4, 5)
        lab(d, (2, 4.2), "Arduino UNO\n（USB 供电）", ha="center", fs_=10)
        for y, nm in ((3.0, "D11（OC2A）"), (2.0, "D3（OC2B，反相）"), (0.6, "GND")):
            lab(d, (3.85, y), nm, ha="right", fs_=8.5)
        rect(11, -1.0, 15, 5)
        lab(d, (13, 2.2), "DRV8871\n模块", ha="center", fs_=10)
        lab(d, (11.15, 3.0), "IN1", ha="left", fs_=8.5); lab(d, (11.15, 2.0), "IN2", ha="left", fs_=8.5)
        lab(d, (11.15, -0.4), "GND", ha="left", fs_=8.5)
        d += elm.Line().at((4, 3.0)).to((11, 3.0)).color(fs.C["vout"])
        d += elm.Line().at((4, 2.0)).to((11, 2.0)).color(fs.C["vout"])
        # 星形接地：Arduino GND 和 DRV8871 GND 各走一根线，只在电源负极这一点相遇
        d += elm.Line().at((4, 0.6)).to((6, 0.6))
        d += elm.Line().at((6, 0.6)).to((6, -2.4))
        d += elm.Line().at((6, -2.4)).to((8.5, -2.4))
        d += elm.Line().at((11, -0.4)).to((10, -0.4))
        d += elm.Line().at((10, -0.4)).to((10, -2.4))
        d += elm.Line().at((10, -2.4)).to((8.5, -2.4))
        d += elm.Dot().at((8.5, -2.4))
        d += elm.Line().at((8.5, -2.4)).to((8.5, -3.0))
        d += elm.Ground().at((8.5, -3.0))
        lab(d, (8.7, -3.5), "12 V 电源负极（星形接地点）", ha="left", fs_=8.5)
        lab(d, (5.7, -1.4), "Arduino GND\n回线", ha="right", fs_=8, color="#555555")
        lab(d, (10.3, -1.4), "DRV8871 GND\n回线", ha="left", fs_=8, color="#555555")
        lab(d, (8.5, -4.5), "两个地最终都在电源负极相遇", ha="center", fs_=9, color=fs.C["fb"])
        # 比较器输出：原来的两根线在此断开
        rect(5.0, 6.2, 8.6, 8.6, lw=1.2, ls="--")
        lab(d, (6.8, 7.8), "LM393 输出 ③④\n+ 1 kΩ 上拉", ha="center", fs_=9, color="#555555")
        for xx, yy in ((9.2, 3.0), (10.0, 2.0)):
            d += elm.Line().at((8.6 if xx == 9.2 else 8.6, 7.0 if xx == 9.2 else 6.6)).to((xx, 7.0 if xx == 9.2 else 6.6)).color("#999999").linestyle("--")
            d += elm.Line().at((xx, 7.0 if xx == 9.2 else 6.6)).to((xx, yy + 0.9)).color("#999999").linestyle("--")
            lab(d, (xx, yy + 0.6), "×", ha="center", fs_=16, color=fs.C["bad"])
        lab(d, (9.0, 5.2), "原来的线拔掉", ha="left", fs_=8.5, color=fs.C["bad"])
        # 功率部分（与对照原理图相同，简画）
        d += elm.Line().at((13, 5)).to((13, 5.6))
        d += elm.MeterA().endpoints((13, 5.6), (13, 7.4)).label("电流表", loc="top", fontsize=8.5)
        d += elm.Vdd().at((13, 7.4)).label("+12 V", fontsize=9)
        d += elm.Inductor2().endpoints((15, 3.0), (18, 3.0)).label("L1 220 µH", loc="top", fontsize=9)
        d += elm.Inductor2().endpoints((15, 1.0), (18, 1.0)).label("L2 220 µH", loc="bottom", fontsize=9)
        lab(d, (14.85, 3.0), "OUT1", ha="right", fs_=8.5); lab(d, (14.85, 1.0), "OUT2", ha="right", fs_=8.5)
        d += elm.Line().at((18, 3.0)).to((20.5, 3.0)); d += elm.Line().at((18, 1.0)).to((20.5, 1.0))
        d += elm.Dot().at((18.8, 3.0)); d += elm.Dot().at((18.8, 1.0))
        d += elm.Capacitor().endpoints((18.8, 3.0), (18.8, 1.0)).label("Cf", loc="bottom", fontsize=9)
        d += elm.Resistor().endpoints((20.5, 3.0), (20.5, 1.0)).label("10 Ω + 8 Ω", loc="bottom", fontsize=9)
        lab(d, (17.5, -0.4), "功率部分与对照原理图相同；两端都不接地", ha="center", fs_=8.5, color=fs.C["bad"])
    print("[图 44-p4-5] 选做 D：D11 → IN1，D3 → IN2；Arduino GND 与模块 GND 各一根回线，只在电源负极相遇；比较器输出断开（×）")
    save_schem(d, N, "44_p4_5_arduino_pwm.png")
    _shrink("44_p4_5_arduino_pwm.png")


if __name__ == "__main__":
    import sys as _s
    only = _s.argv[1:]
    for fn in (p1_1, p1_2, p1_3, p1_4, p1_vmid, p1_5, p2_1, p2_2, p2_3, p2_4, p2_5, p2_6, p2_7, p2_8, p2_9, p3_1, p3_2, p3_3, p3_4, p3_5, p3_6, p3_7,
               p4_1, p4_2, p4_3, p4_4, p4_5, nums_fix):
        if only and fn.__name__ not in only:
            continue
        fn()
