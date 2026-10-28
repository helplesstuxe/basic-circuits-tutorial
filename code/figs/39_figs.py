"""39 恒流源与线圈励磁驱动：全部配图。
运行：/workspace/circuits-venv/bin/python code/figs/39_figs.py
波形数据来自 spice/39/*.csv（由 spice/39/run.py 从 ngspice 结果重采样生成）。
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
from batt_pm import pm as bat_pm        # 电池旁的 + / − 小字（长线 = +）
import numpy as np
import matplotlib.pyplot as plt
from lab_schem import probe, colnote, lab, title, note, Hop, _dbox, _pin, _par_arrow, GRAY

N = "39"
SP = os.path.join(HERE, "..", "..", "spice", "39")


def csv(name):
    """读 spice/39 下的 CSV（第一行是列名），返回 {列名: 数组}。"""
    path = os.path.join(SP, name)
    head = open(path).readline().strip().split(",")
    arr = np.loadtxt(path, delimiter=",", skiprows=1)
    return {h: arr[:, i] for i, h in enumerate(head)}


# ============================ 公共数值（page2 推导用的同一组数） ============================
VCC = 12.0                                   # 电源 12 V
R1, R2 = 10e3, 910.0                         # 基准分压
RS = 10.0                                    # 采样电阻
V_REF = VCC * R2 / (R1 + R2)                 # 同相端电压
I_SET = V_REF / RS                           # 设定电流
VDS_MIN = 0.5                                # 给 MOSFET 留的最小 V_DS
RL_MAX = (VCC - V_REF - VDS_MIN) / I_SET     # 顺从电压允许的最大负载
RTH_JA = 62.0                                # IRLZ44N 不装散热片时结到环境热阻 °C/W
T_AMB = 25.0
R_ON_BRIDGE = 0.307 + 0.258                  # DRV8871 上管 + 下管导通电阻（典型）
L_COIL, R_COIL = 0.1, 75.0                   # 仿真线圈 100 mH / 75 Ω（20 °C）
ALPHA_CU = 0.00393                           # 退火铜电阻温度系数 /K（20 °C）
print(f"[数值] V_REF = {V_REF:.4f} V，I_SET = {I_SET*1e3:.2f} mA，R_L 上限 = {RL_MAX:.1f} Ω")
assert abs(V_REF - 1.0009) < 1e-4 and abs(RL_MAX - 104.9) < 0.05

# SPICE 扫描结果（spice/39/39_ccs.cir，run.py 已逐项对照）
SP_RL = np.array([0.01, 10, 22, 47, 68, 100, 105, 110, 115, 120, 130, 150])
SP_I = np.array([100.107, 100.107, 100.107, 100.107, 100.107, 100.107, 100.107, 99.969, 95.9864, 92.2951, 85.7034, 74.9917]) / 1e3
SP_VDS = {0.01: 10.9979, 10: 9.99786, 22: 8.79657, 47: 6.2939, 68: 4.19165, 100: 0.988221, 105: 0.487686}


def i_ideal(rl, vcc=VCC):
    """理想恒流沉：没掉出恒流区时电流 = I_SET；掉出后 MOSFET 全开，电流 = V/(R_L+R_S)（忽略 22 mΩ 导通电阻）。"""
    return np.minimum(I_SET, vcc / (rl + RS))


# =============================== page1 ===============================
# ---------- 图 39-p1-1：线圈变热后电流怎么变（电压驱动 vs 恒流驱动） ----------
T = np.linspace(20, 80, 121)
Rc = R_COIL * (1 + ALPHA_CU * (T - 20))
I_v = VCC / (Rc + R_ON_BRIDGE)
I_c = np.full_like(T, I_SET)
assert (Rc + RS).max() < RL_MAX                 # 80 °C 时线圈电阻仍在恒流区内
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(T, I_v * 1e3, **fs.LS["vin"], label="电压驱动（12 V 直接加在线圈上）")
ax.plot(T, I_c * 1e3, **fs.LS["vout"], label="恒流驱动（设定 100 mA）")
i20 = VCC / (R_COIL + R_ON_BRIDGE)
r60 = R_COIL * (1 + ALPHA_CU * 40)
i60 = VCC / (r60 + R_ON_BRIDGE)
fs.mark(ax, 20, i20 * 1e3, "{:.1f}", " mA", fs.C["vin"], dx=4, dy=-12)
fs.mark(ax, 60, i60 * 1e3, "{:.1f}", " mA", fs.C["vin"], dx=4, dy=4)
fs.mark(ax, 60, I_SET * 1e3, "{:.1f}", " mA", fs.C["vout"], dx=4, dy=5)
drop = (i60 / i20 - 1) * 100
print(f"[数值] 线圈 20 °C {R_COIL:.0f} Ω → 60 °C {r60:.2f} Ω；电压驱动电流变化 {drop:.1f}%")
assert abs(r60 - 86.79) < 0.01 and abs(drop + 13.4) < 0.1
ax.text(40, 128, f"线圈从 20 °C 热到 60 °C：\n电压驱动电流少了 {-drop:.1f}%，恒流驱动不变", fontsize=9, ha="center")
ax.set_ylim(80, 175)
fs.axlabels(ax, "线圈温度", "°C", "线圈电流", "mA")
ax.legend(loc="lower left", fontsize=8.5)
fs.save(fig, N, "39_p1_1_temp_drift.png")


# ---------- 恒流沉原理图（图 39-p1-2 简化版、图 39-p2-1 完整版、图 39-p4-2 实验版共用） ----------
def ccs(d, full=True, x0=0.0, node_labels=True, pins=True):
    """恒流沉电路：返回关键节点坐标。full=False 时省掉 RG/CF，基准写成 1 V 电源。"""
    yT = 6.5
    xm = x0 + 6.5                                  # MOSFET 所在竖线
    if full:
        d += elm.Line().at((x0 - 4.0, yT)).to((xm, yT))
    d += elm.Vdd().at((xm, yT)).label("+12 V")
    d += elm.Resistor().endpoints((xm, yT), (xm, 4.0)).label("$R_L$ 负载", loc="bottom")
    d += elm.Dot().at((xm, 4.0))
    q = elm.NFet().theta(0).reverse().anchor("drain").at((xm, 4.0))
    d += q
    A = q.absanchors
    lab(d, (xm + 0.25, 3.85), "D 漏极", fs_=9.5, color=GRAY)
    lab(d, (xm + 0.25, 2.55), "S 源极", fs_=9.5, color=GRAY)
    lab(d, (xm + 0.45, 3.2), "Q1 IRLZ44N", fs_=10)
    lab(d, (A["gate"][0] + 0.1, A["gate"][1] - 0.35), "G", fs_=9.5, color=GRAY)
    ys = 0.9
    d += elm.Line().at(A["source"]).to((xm, ys))
    d += elm.Dot().at((xm, ys))
    d += elm.Resistor().endpoints((xm, ys), (xm, -1.6)).label("$R_S$ 10 Ω\n采样电阻", loc="bottom")
    d += elm.Ground().at((xm, -1.6))
    op = elm.Opamp(leads=True).right().flip().anchor("out").at((x0 + 1.6, A["gate"][1]))
    d += op
    O = op.absanchors
    lab(d, (O["center"][0] - 0.15, O["center"][1]), "LM358", ha="center", fs_=9)
    xc = x0 + 2.4
    if full:
        d += elm.Line().at(O["out"]).to((xc, O["out"][1]))
        d += elm.Dot().at((xc, O["out"][1]))
        d += elm.Resistor().endpoints((xc, O["out"][1]), A["gate"]).label("$R_G$ 100 Ω", loc="top")
        d += elm.Capacitor().endpoints((xc, O["out"][1]), (xc, ys)).label("$C_F$\n10 nF", loc="bottom")
        d += elm.Dot().at((xc, ys))
        d += elm.Resistor().endpoints((xm, ys), (xc, ys)).label("$R_F$ 1 kΩ", loc="bottom")
    else:
        d += elm.Line().at(O["out"]).to(A["gate"])
        d += elm.Line().at((xm, ys)).to((xc, ys))
    xn = O["in1"][0] - 0.6
    d += elm.Line().at((xc, ys)).to((xn, ys))
    d += elm.Line().at((xn, ys)).to((xn, O["in1"][1]))
    d += elm.Line().at((xn, O["in1"][1])).to(O["in1"])
    xr = x0 - 4.0
    d += elm.Line().at(O["in2"]).to((xr, O["in2"][1]))
    d += elm.Dot().at((xr, O["in2"][1]))
    if full:
        d += elm.Dot().at((xr, yT))
        d += elm.Resistor().endpoints((xr, yT), (xr, O["in2"][1])).label("$R_1$ 10 kΩ", loc="top")
        d += elm.Resistor().endpoints((xr, O["in2"][1]), (xr, -1.6)).label("$R_2$ 910 Ω", loc="top")
        d += elm.Ground().at((xr, -1.6))
    else:
        d += elm.SourceV().endpoints((xr, -1.6), (xr, O["in2"][1])).label("基准\n1 V", loc="bottom")
        d += elm.Ground().at((xr, -1.6))
    # LM358 A 组引脚号：3 脚 +、2 脚 −、1 脚输出
    if pins:                                        # 实验篇图 39-p4-2 自己标脚号，传 pins=False
        lab(d, (O["in2"][0] + 0.15, O["in2"][1] + 0.25), "3", fs_=9, color=GRAY)
        lab(d, (O["in1"][0] + 0.15, O["in1"][1] - 0.25), "2", fs_=9, color=GRAY)
        lab(d, (O["out"][0] - 0.05, O["out"][1] + 0.3), "1", fs_=9, color=GRAY)
    vd, vs = O["vd"], O["vs"]
    top, bot = (vs, vd) if vs[1] > vd[1] else (vd, vs)      # 上面那根短线标 8 脚（+12 V），下面标 4 脚（地）
    d += elm.Line().at(top).to((top[0], top[1] + 0.4))
    lab(d, (top[0] + 0.15, top[1] + 0.3), "8 脚接 +12 V", fs_=9, color=GRAY)
    d += elm.Line().at(bot).to((bot[0], bot[1] - 0.4))
    lab(d, (bot[0] + 0.15, bot[1] - 0.3), "4 脚接地", fs_=9, color=GRAY)
    P = dict(xr=xr, vref=(xr, O["in2"][1]), s=(xm, ys), d=(xm, 4.0), out=O["out"], gate=A["gate"],
             xm=xm, yT=yT, inm=O["in1"], inp=O["in2"], xc=xc, ys=ys)
    if node_labels:
        lab(d, (xr - 0.2, O["in2"][1] + 0.35), "$V_{REF}$", ha="right", fs_=11, color=fs.C["fb"])
        lab(d, (xm + 0.3, ys + 0.3), "$V_S$", fs_=11, color=fs.C["vout"])
    return P


with drawing(fontsize=11) as d:
    P = ccs(d, full=False)
    _par_arrow(d, (P["xm"], P["yT"] - 0.3), (P["xm"], 4.3), (-0.45, 0))
    lab(d, (P["xm"] - 0.6, 5.3), "电流 I", ha="right", fs_=10, color=fs.C["cur"])
    note(d, (P["xr"] - 0.8, -3.0), "运放一直调栅极，让 $V_S$ 等于基准 1 V：I = 1 V ÷ 10 Ω = 0.1 A，和 $R_L$ 是多少无关")
print("[图 39-p1-2] 简化恒流沉：基准 1 V、R_S 10 Ω → 0.1 A")
save_schem(d, N, "39_p1_2_ccs_simple.png")

# ---------- 图 39-p1-3：电磁流量计励磁的分工（方框图） ----------
fig, ax = fs.diagram(9, 2.8, xlim=(0, 11.4), ylim=(0, 3.2))
fs.box(ax, 1.2, 2.2, "定时器\n（单片机）", w=1.8, h=0.9)
fs.box(ax, 4.2, 2.2, "H 桥\n管「方向」", w=1.8, h=0.9)
fs.box(ax, 7.2, 2.2, "励磁线圈\n（产生磁场）", w=1.9, h=0.9, fc=fs.C["fill2"])
fs.box(ax, 4.2, 0.6, "恒流沉\n管「大小」", w=1.8, h=0.9)
fs.box(ax, 10.0, 2.2, "水流切割磁场\n电极出信号\n→ 38 同步检波", w=2.2, h=1.1)
fs.arrow(ax, (2.1, 2.2), (3.3, 2.2), "6.25 Hz")
fs.arrow(ax, (5.1, 2.35), (6.25, 2.35), "+100 mA")
fs.arrow(ax, (6.25, 2.05), (5.1, 2.05), "−100 mA", dashed=True)
fs.arrow(ax, (4.2, 1.75), (4.2, 1.05), "")
fs.arrow(ax, (8.15, 2.2), (8.9, 2.2), "磁场")
ax.text(5.4, 0.6, "电流大小恒定 → 磁场强度恒定", fontsize=9, va="center")
print("[图 39-p1-3] 方框图：6.25 Hz 换向、±100 mA")
fs.save(fig, N, "39_p1_3_excitation_blocks.png")


# =============================== page2 ===============================
with drawing(fontsize=11) as d:
    P = ccs(d, full=True)
    lab(d, (P["gate"][0] - 0.3, P["gate"][1] + 0.4), "$V_G$", ha="right", fs_=11, color=fs.C["vin"])
print("[图 39-p2-1] 完整恒流沉：R1 10k / R2 910 / RS 10 / RG 100 / RF 1k / CF 10n")
save_schem(d, N, "39_p2_1_ccs_full.png")

# ---------- 图 39-p2-2：电流和 V_DS 随负载电阻变化 ----------
rl = np.linspace(0, 150, 601)
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a1.plot(rl, i_ideal(rl) * 1e3, **fs.LS["good"], label="理想计算")
a1.plot(SP_RL, SP_I * 1e3, "o", color=fs.C["vout"], ms=4, label="SPICE")
fs.ref_v(a1, RL_MAX, f"{RL_MAX:.0f} Ω", y=0.25)
fs.mark(a1, 47, SP_I[3] * 1e3, "{:.1f}", " mA", fs.C["vout"], dx=-20, dy=-14)
fs.mark(a1, 120, SP_I[9] * 1e3, "{:.1f}", " mA", fs.C["bad"], dx=-48, dy=-6)
fs.mark(a1, 150, SP_I[11] * 1e3, "{:.1f}", " mA", fs.C["bad"], dx=-44, dy=-4)
a1.set_ylim(60, 112)
fs.axlabels(a1, "负载电阻 $R_L$", "Ω", "电流", "mA")
a1.legend(loc="lower left", fontsize=8)
a1.set_title("电流：105 Ω 以内不变", fontsize=10)
vds_th = np.maximum(VCC - i_ideal(rl) * (rl + RS), 0)
a2.plot(rl, vds_th, **fs.LS["good"], label="12 − I·($R_L$ + 10 Ω)")
xs = np.array(list(SP_VDS))
a2.plot(xs, [SP_VDS[k] for k in xs], "o", color=fs.C["vin"], ms=4, label="SPICE")
for k, dy in ((47, 6), (100, 6)):
    fs.mark(a2, k, SP_VDS[k], "{:.2f}", " V", fs.C["vin"], dx=4, dy=dy)
fs.ref_h(a2, VDS_MIN, "0.5 V", x=0.98)
fs.axlabels(a2, "负载电阻 $R_L$", "Ω", "MOSFET 两端 $V_{DS}$", "V")
a2.legend(loc="upper right", fontsize=8)
a2.set_title("$V_{DS}$：负载越大，留给管子的越少", fontsize=10)
for k in SP_VDS:
    assert abs(SP_VDS[k] - (VCC - I_SET * (k + RS))) < 0.01
assert abs(SP_I[:7] - I_SET).max() < 5e-5 and SP_I[9] < 0.093
fs.save(fig, N, "39_p2_2_sweep_rl.png")

# ---------- 图 39-p2-3：MOSFET 管耗与不装散热片时的结温 ----------
rl2 = np.linspace(0, RL_MAX, 300)
p = (VCC - I_SET * (rl2 + RS)) * I_SET
tj = T_AMB + RTH_JA * p
fig, a1 = plt.subplots(figsize=fs.SIZE["single"])
a1.plot(rl2, tj, **fs.LS["bad"], label="不装散热片（62 °C/W，室温 25 °C）")
for r in (0, 47, 100):
    pv = (VCC - I_SET * (r + RS)) * I_SET
    fs.mark(a1, r, T_AMB + RTH_JA * pv, "{:.0f}", " °C", fs.C["bad"], dx=5, dy=4)
    print(f"[数值] R_L={r} Ω：P = {pv:.3f} W")
fs.ref_h(a1, 60, "60 °C：测温探头读到这里就断电", x=0.99)
fs.ref_h(a1, 175, "结温上限 175 °C", x=0.99)
a1.set_ylim(0, 190)
fs.axlabels(a1, "负载电阻 $R_L$", "Ω", "MOSFET 结温（估算）", "°C")
a1.legend(loc="lower left", fontsize=8.5)
P0 = (VCC - I_SET * RS) * I_SET
P47 = (VCC - I_SET * (47 + RS)) * I_SET
assert abs(P0 - 1.10) < 0.005 and abs(P47 - 0.63) < 0.005 and T_AMB + RTH_JA * P0 > 60
fs.save(fig, N, "39_p2_3_power_tj.png")

# ---------- 图 39-p2-4：H 桥 + 恒流沉 驱动线圈 ----------
def hbridge(ref, name, snubber=True):
    with drawing(fontsize=11) as d:
        xl, xr, yt, ym, yb = 0.0, 7.0, 6.0, 3.0, 0.0
        d += elm.Line().at((xl, yt)).to((xr, yt))
        d += elm.Vdd().at((3.5, yt)).label("+12 V")
        d += elm.Switch().endpoints((xl, yt), (xl, ym)).label("S1", loc="bottom")
        d += elm.Switch().endpoints((xr, yt), (xr, ym)).label("S2", loc="bottom")
        d += elm.Switch().endpoints((xl, ym), (xl, yb)).label("S3", loc="bottom")
        d += elm.Switch().endpoints((xr, ym), (xr, yb)).label("S4", loc="bottom")
        for x in (xl, xr):
            d += elm.Dot().at((x, ym))
        d += elm.Line().at((xl, ym)).to((1.2, ym))
        d += elm.Inductor2(loops=3).endpoints((1.2, ym), (3.6, ym)).label("线圈 L 100 mH", loc="top")
        d += elm.Resistor().endpoints((3.6, ym), (6.0, ym)).label("线圈电阻 75 Ω", loc="top")
        d += elm.Line().at((6.0, ym)).to((xr, ym))
        _dbox(d, 1.0, ym - 0.55, 6.15, ym + 1.25)
        lab(d, (3.6, ym + 1.55), "励磁线圈（一个元件，画成 L 加 R）", ha="center", fs_=9.5, color=GRAY)
        lab(d, (xl - 0.3, ym + 0.35), "OUT1", ha="right", fs_=9.5, color=GRAY)
        lab(d, (xr + 0.3, ym + 0.35), "OUT2", fs_=9.5, color=GRAY)
        if snubber:  # RC 吸收（直觉篇还没讲，p1-4 不画）
            d += elm.Line().at((1.2, ym)).to((1.2, ym - 1.3))
            d += elm.Resistor().endpoints((1.2, ym - 1.3), (3.8, ym - 1.3)).label("$R_{SN}$ 1 kΩ", loc="bottom")
            d += elm.Capacitor().endpoints((3.8, ym - 1.3), (6.5, ym - 1.3)).label("$C_{SN}$ 100 nF", loc="bottom")
            d += elm.Line().at((6.5, ym - 1.3)).to((6.5, ym))
            d += elm.Dot().at((1.2, ym)); d += elm.Dot().at((6.5, ym))
        d += elm.Line().at((xl, yb)).to((xr, yb))
        d += elm.Dot().at((3.5, yb))
        lab(d, (3.7, yb + 0.3), "桥底", fs_=9.5, color=GRAY)
        d += elm.SourceI().endpoints((3.5, yb), (3.5, -2.6)).label("恒流沉 100 mA\n（{ref} 的电路，\n$R_L$ 处换成整个 H 桥）".format(ref=ref), loc="bottom")
        d += elm.Ground().at((3.5, -2.6))
        _par_arrow(d, (0.0, yt - 0.3), (0.0, ym + 0.3), (-0.5, 0))
        lab(d, (8.6, 5.0), "阶段 A：S1、S4 闭合\n电流 OUT1 → OUT2（+）\n阶段 B：S2、S3 闭合\n电流 OUT2 → OUT1（−）", fs_=9.5)
        lab(d, (8.6, 1.4), ("S1～S4：四只分立 MOS 管\n（DRV8871 的下管源极在片内\n接地，桥底引不出，不能这样接）\n每只开关自带一只体二极管（图中未画）"
                            if snubber else "S1～S4：四只分立 MOS 管"), fs_=9.5, color=GRAY)  # 直觉篇还没讲 DRV8871、体二极管
    print(f"[{name}] H 桥 + 恒流沉，线圈 100 mH / 75 Ω" + ("，RC 吸收 1k + 100n" if snubber else "，不画 RC 吸收"))
    save_schem(d, N, name)


hbridge("图 39-p2-1", "39_p2_4_hbridge_ccs.png")
hbridge("图 39-p1-2", "39_p1_4_hbridge.png", snubber=False)  # 直觉篇同页原理图

# ---------- 图 39-p2-5：换向波形（电压驱动 vs 恒流驱动） ----------
cv, ci = csv("coil_v.csv"), csv("coil_i.csv")
t0 = 0.160
tv, iv = (cv["t_s"] - t0) * 1e3, cv["i_A"] * 1e3
tc, ic, vb = (ci["t_s"] - t0) * 1e3, ci["i_A"] * 1e3, ci["v_bot"]
w = (tv > -2) & (tv < 12)
wc = (tc > -2) & (tc < 12)
fig, (a1, a2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True, gridspec_kw=dict(height_ratios=[2, 1]))
a1.plot(tv[w], iv[w], **fs.LS["vin"], label="电压驱动（12 V 直接换向）")
a1.plot(tc[wc], ic[wc], **fs.LS["vout"], label="恒流驱动（H 桥 + 100 mA 恒流沉）")
fs.ref_h(a1, 0, None)
fs.ref_v(a1, 0, "换向", y=0.97)
ipk_i = int(np.argmax(np.where(wc, ic, -1e9)))
t_pk, i_pk = tc[ipk_i], ic[ipk_i]
after = wc & (tc > t_pk)
t_settle = tc[after][np.where(np.abs(ic[after] - 100.09) > 1.0)[0][-1]]
fs.mark(a1, 11.5, iv[w][-1], "{:.1f}", " mA", fs.C["vin"], dx=-50, dy=4)
fs.mark(a1, t_pk, i_pk, "{:.0f}", " mA", fs.C["vout"], dx=8, dy=-14)
fs.mark(a1, 11.5, ic[wc][-1], "{:.1f}", " mA", fs.C["vout"], dx=-50, dy=-13)
print(f"[数值] 恒流驱动：换向后 {t_pk:.2f} ms 冲到 {i_pk:.1f} mA，{t_settle:.2f} ms 后回到 100 mA ±1 mA 以内")
assert 118.5 < i_pk < 119.7 and 3.2 < t_settle < 3.5 and 2.7 < t_pk < 3.0
a1.set_ylim(-190, 190)
fs.axlabels(a1, "", None, "线圈电流", "mA")
a1.legend(loc="lower right", fontsize=8)
a2.plot(tc[wc], vb[wc], **fs.LS["third"], label="桥底电压（恒流沉漏极）")
fs.ref_v(a2, 0, None)
fs.mark(a2, 11.5, vb[wc][-1], "{:.2f}", " V", fs.C["third"], dx=-48, dy=4)
fs.axlabels(a2, "换向后的时间", "ms", "电压", "V")
a2.legend(loc="upper right", fontsize=8)
assert abs(vb[wc][-1] - 4.44) < 0.02
fs.save(fig, N, "39_p2_5_reversal.png")

# ---------- 图 39-p3-9：Howland 电流泵（page3 变体，只作了解） ----------
with drawing(fontsize=11) as d:
    op = elm.Opamp(leads=True).right().anchor("out").at((6.0, 0.0)); d += op
    O = op.absanchors
    # 反相端：R1 到地，R2 到输出
    d += elm.Line().at(O["in1"]).to((O["in1"][0] - 0.6, O["in1"][1]))
    xA = O["in1"][0] - 0.6
    d += elm.Dot().at((xA, O["in1"][1]))
    d += elm.Line().at((xA, O["in1"][1])).to((xA, 2.2))
    d += elm.Resistor().endpoints((xA, 2.2), (O["out"][0] + 0.6, 2.2)).label("$R_2$ 10 kΩ", loc="top")
    d += elm.Line().at((O["out"][0] + 0.6, 2.2)).to((O["out"][0] + 0.6, 0))
    d += elm.Line().at(O["out"]).to((O["out"][0] + 0.6, 0))
    d += elm.Dot().at((O["out"][0] + 0.6, 0))
    d += elm.Resistor().endpoints((xA, O["in1"][1]), (xA - 3.0, O["in1"][1])).label("$R_1$ 10 kΩ", loc="top")
    d += elm.Ground().at((xA - 3.0, O["in1"][1]))
    # 同相端：R3 来自 V_IN，R4 来自输出，负载 R_L 接地
    xB = O["in2"][0] - 0.6
    d += elm.Line().at(O["in2"]).to((xB, O["in2"][1]))
    d += elm.Dot().at((xB, O["in2"][1]))
    d += elm.Resistor().endpoints((xB - 3.0, O["in2"][1]), (xB, O["in2"][1])).label("$R_3$ 10 kΩ", loc="top")
    d += elm.Dot(open=True).at((xB - 3.0, O["in2"][1])).label("$V_{IN}$", "left")
    d += elm.Line().at((xB, O["in2"][1])).to((xB, -2.4))
    d += elm.Dot().at((xB, -2.4))
    d += elm.Resistor().endpoints((xB, -2.4), (O["out"][0] + 0.6, -2.4)).label("$R_4$ 10 kΩ", loc="bottom")
    d += elm.Line().at((O["out"][0] + 0.6, -2.4)).to((O["out"][0] + 0.6, 0))
    d += elm.Resistor().endpoints((xB, -2.4), (xB, -5.0)).label("$R_L$ 负载", loc="bottom")
    d += elm.Ground().at((xB, -5.0))
    lab(d, (xB + 2.6, -3.9), "$I_L$ = $V_{IN}$ / $R_3$\n（要求 $R_2/R_1 = R_4/R_3$）\n运放需要 ± 双电源", fs_=10)
print("[图 39-p3-9] Howland 电流泵：四只 10 kΩ")
save_schem(d, N, "39_p3_9_howland.png")


def z_howland(r1, r2, r3, r4):
    """Howland 输出阻抗：Z = 1 / (1/R3 − R2/(R1·R4))。"""
    return 1.0 / (1.0 / r3 - r2 / (r1 * r4))


z_p = z_howland(10e3, 10e3, 10e3, 10.1e3)
z_m = z_howland(10e3, 10e3, 10e3, 9.9e3)
print(f"[数值] Howland：R4 偏 +1% → Z = {z_p/1e6:.2f} MΩ；偏 −1% → Z = {z_m/1e6:.2f} MΩ")
assert abs(z_p - 1.01e6) < 1e3 and z_m < 0


# =============================== page3 ===============================
# ---------- 图 39-p3-2：采样电阻 R_S 怎么选 ----------
VOS_MAX = 3e-3                                    # LM358B 失调电压最大 3 mV（手册）
rs = np.linspace(1, 20, 200)
rlmax = (VCC - VDS_MIN - 0.1 * rs) / 0.1
err = VOS_MAX / (0.1 * rs) * 100
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a1.plot(rs, rlmax, **fs.LS["vin"])
for r, dy in ((1, -14), (10, 4), (20, 4)):
    fs.mark(a1, r, (VCC - VDS_MIN - 0.1 * r) / 0.1, "{:.0f}", " Ω", fs.C["vin"], dx=4, dy=dy)
fs.axlabels(a1, "采样电阻 $R_S$", "Ω", "能带的最大负载", "Ω")
a1.set_title("$R_S$ 越大，留给负载的电压越少", fontsize=10)
a2.plot(rs, err, **fs.LS["bad"])
for r, dy in ((1, -4), (10, 6)):
    fs.mark(a2, r, VOS_MAX / (0.1 * r) * 100, "{:.1f}", "%", fs.C["bad"], dx=6, dy=dy)
fs.axlabels(a2, "采样电阻 $R_S$", "Ω", "失调电压造成的最大误差", "%")
a2.set_title("$R_S$ 越小，3 mV 失调占比越大", fontsize=10)
assert abs(VOS_MAX / 0.1 / 1 * 100 - 3.0) < 1e-9 and abs(VOS_MAX / 1.0 * 100 - 0.3) < 1e-9
fs.save(fig, N, "39_p3_2_rs_choice.png")

# ---------- 图 39-p3-6：阶跃响应 有/无 补偿 ----------
st = csv("step.csv")
ts = (st["t_s"] - 3e-3) * 1e6
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
vr = np.where(ts < 0, 0.5, 1.0)
ax.plot(ts, vr, **fs.LS["fb"], label="基准 $V_{REF}$ 从 0.5 V 跳到 1.0 V")
ax.plot(ts, st["vs_nocomp"], **fs.LS["third"], label="不加 $R_G$、$C_F$")
ax.plot(ts, st["vs_comp"], **fs.LS["vout"], label="加 $R_G$ 100 Ω + $C_F$ 10 nF")
k1 = np.argmax(st["vs_comp"]); k0 = np.argmax(st["vs_nocomp"])
os1 = (st["vs_comp"][k1] - 1.0) / 0.5 * 100
os0 = (st["vs_nocomp"][k0] - 1.0) / 0.5 * 100
fs.mark(ax, ts[k1], st["vs_comp"][k1], "{:.3f}", " V", fs.C["vout"], dx=-62, dy=0)
fs.mark(ax, ts[k0], st["vs_nocomp"][k0], "{:.3f}", " V", fs.C["third"], dx=6, dy=0)
print(f"[数值] 过冲：有补偿 {os1:.1f}%，无补偿 {os0:.1f}%")
assert abs(os1 - 15.0) < 0.5 and abs(os0 - 28.7) < 0.5
ax.set_xlim(-5, 60); ax.set_ylim(0.4, 1.45)
fs.axlabels(ax, "基准跳变后的时间", "µs", "采样电阻电压 $V_S$", "V")
ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "39_p3_6_step_comp.png")

# ---------- 图 39-p3-8：线圈两端 不加 / 加 RC 吸收 ----------
ns = csv("coil_i_nosnub.csv")
tn = (ns["t_s"] - 0.230) * 1e3
m = (tc >= 70) & (tc <= 71.5)                     # 同一时间窗（230–231.5 ms）里加了 RC 的波形
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(tn * 1e3, ns["v_bot"], **fs.LS["bad"], label="不加 RC 吸收：仿真里一直在振荡")
ax.plot((tc[m] - 70) * 1e3, vb[m], **fs.LS["vout"], label="加 1 kΩ + 100 nF：平稳")
lo, hi = ns["v_bot"].min(), ns["v_bot"].max()
fs.ref_h(ax, lo, f"最低 {lo:.2f} V", x=0.99)
fs.ref_h(ax, hi, f"最高 {hi:.2f} V", x=0.99)
fs.mark(ax, 1300, vb[m][-1], "{:.2f}", " V", fs.C["vout"], dx=-10, dy=6)
_mid = (ns["v_bot"].max() + ns["v_bot"].min()) / 2       # 用上穿中线的时刻量振荡周期
_k = np.where((ns["v_bot"][:-1] < _mid) & (ns["v_bot"][1:] >= _mid))[0]
_tx = tn[_k] + (_mid - ns["v_bot"][_k]) / (ns["v_bot"][_k + 1] - ns["v_bot"][_k]) * (tn[_k + 1] - tn[_k])
T_OSC = float(np.mean(np.diff(_tx))) * 1e-3              # s
C_EQ = (T_OSC / (2 * np.pi)) ** 2 / 0.1
print(f"[数值] 无吸收振荡周期 {T_OSC*1e6:.1f} µs → 等效电容 {C_EQ*1e9:.2f} nF，sqrt(L/C) = {np.sqrt(0.1/C_EQ)/1e3:.2f} kΩ，100 nF / C = {100e-9/C_EQ:.1f}")
assert abs(T_OSC * 1e6 - 175) < 1 and abs(C_EQ * 1e9 - 7.8) < 0.05
_t0 = _tx[2] * 1e3
ax.annotate("", xy=(_t0 + T_OSC * 1e6, 13.6), xytext=(_t0, 13.6), arrowprops=dict(arrowstyle="<->", lw=1.0))
ax.text(_t0 + T_OSC * 0.5e6, 13.8, "一个周期约 175 µs", ha="center", va="bottom", fontsize=8.5)
print(f"[数值] 无吸收桥底电压 {lo:.3f}–{hi:.3f} V")
assert abs(lo - 1.01) < 0.02 and abs(hi - 12.54) < 0.02
ax.set_ylim(-0.5, 18)
fs.axlabels(ax, "时间（换向后 70 ms 起）", "µs", "桥底电压", "V")
ax.legend(loc="upper left", fontsize=8, ncol=2)
fs.save(fig, N, "39_p3_8_snubber.png")


# ---------- 图 39-p3-4：错误接法——采样电阻挪到高边（预测题，spice/39/39_wrong.cir） ----------
def wrong_fig(answer, cols=False):
  with drawing(fontsize=11) as d:
      xm, yT = 6.5, 8.0
      d += elm.Line().at((-4.0, yT)).to((xm, yT))
      d += elm.Vdd().at((xm, yT)).label("+12 V")
      d += elm.Resistor().endpoints((xm, yT), (xm, 6.0)).label("$R_S$ 10 Ω\n（挪到了上面）", loc="bottom", color=fs.C["bad"])
      d += elm.Dot().at((xm, 6.0))
      lab(d, (xm + 0.3, 6.25), "X 点", fs_=11, color=fs.C["bad"])
      d += elm.Resistor().endpoints((xm, 6.0), (xm, 4.0)).label("$R_L$ 47 Ω", loc="bottom")
      q = elm.NFet().theta(0).reverse().anchor("drain").at((xm, 4.0)); d += q
      A = q.absanchors
      lab(d, (xm + 0.45, 3.2), "Q1 IRLZ44N", fs_=10)
      d += elm.Line().at(A["source"]).to((xm, 1.2))
      d += elm.Ground().at((xm, 1.2))
      lab(d, (xm + 0.3, 1.6), "源极直接接地", fs_=9.5, color=GRAY)
      op = elm.Opamp(leads=True).right().flip().anchor("out").at((1.6, A["gate"][1])); d += op
      O = op.absanchors
      lab(d, (O["center"][0] - 0.15, O["center"][1]), "LM358", ha="center", fs_=9)
      d += elm.Resistor().endpoints(O["out"], A["gate"]).label("$R_G$ 100 Ω", loc="top")
      xn = O["in1"][0] - 0.6
      yf = 6.0
      d += elm.Resistor().endpoints((xm, yf), (2.4, yf)).label("$R_F$ 1 kΩ", loc="top", color=fs.C["bad"])
      d += elm.Line().at((2.4, yf)).to((xn, yf))
      d += elm.Line().at((xn, yf)).to((xn, O["in1"][1]))
      d += elm.Line().at((xn, O["in1"][1])).to(O["in1"])
      xr = -4.0
      d += elm.Line().at(O["in2"]).to((xr, O["in2"][1]))
      d += elm.Dot().at((xr, O["in2"][1]))
      d += elm.Dot().at((xr, yT))
      d += elm.Resistor().endpoints((xr, yT), (xr, O["in2"][1])).label("$R_1$ 10 kΩ", loc="top")
      d += elm.Resistor().endpoints((xr, O["in2"][1]), (xr, 0.0)).label("$R_2$ 910 Ω", loc="top")
      d += elm.Ground().at((xr, 0.0))
      lab(d, (xr - 0.2, O["in2"][1] + 0.35), "$V_{REF}$ 1 V", ha="right", fs_=11, color=fs.C["fb"])
      if answer:
          note(d, (xr - 0.8, -1.4), "反馈仍从 $R_S$ 下端（X 点）取回运放反相端。\nX 点 = 12 V − 10 Ω × I，永远在 11 V 以上，比 1 V 大得多：\n运放输出被拉到约 0 V，MOS 管关断，电流几乎为 0（SPICE：0.005 mA）")
      else:
          note(d, (xr - 0.8, -1.4), "反馈仍从 $R_S$ 下端（X 点）取回运放反相端。\n先别往下看，自己想：X 点大约是几伏？运放的两个输入端谁大？\n运放输出会往哪边跑？负载电流是 100 mA、比 100 mA 大，还是接近 0？")
      if cols:                                    # 图 39-p4-6：选做 A7 照这张图在面包板上改线
          colnote(d, (xm, 7.0), "RS：+12 V 轨 → j28\n（原来 j28 那根红线拔掉）", "right", ofst=2.4)
          colnote(d, (xm, 5.0), "$R_L$ 仍在 g24–g28", "right", ofst=2.4)
          colnote(d, (xm, 2.3), "第 22 列：黑线接 GND 轨\n（原来的 RS 拔走）", "right", ofst=2.4)
          probe(d, (xm, 6.0), "A7-1", dx=-1.3, dy=-1.0)
          probe(d, O["out"], "A7-2", dx=0.0, dy=1.1)
          lab(d, (2.4, 5.55), "反馈线的一头从 g22 挪到 h28", fs_=9.5, color=fs.C["fb"])
  return d
d = wrong_fig(False)
print("[图 39-p3-4] 错误接法预测题：R_S 挪到高边（不含结论）")
save_schem(d, N, "39_p3_4_wrong_highside.png")
d = wrong_fig(True)
print("[图 39-p3-5] 错误接法答案：R_S 在高边 → 电流几乎为 0")
save_schem(d, N, "39_p3_5_wrong_answer.png")

# ---------- 图 39-p3-3：可选升级——TL431 基准代替 R1、R2 分压 ----------
VK = 2.495                                         # TL431 基准典型值（TI 手册）
i_div = VK / 25e3
i_tl = (VCC - VK) / 4.7e3 - i_div
v_mid = VK * 10 / 25
print(f"[数值] TL431：分压电流 {i_div*1e3:.3f} mA，TL431 电流 {i_tl*1e3:.2f} mA，中点 {v_mid:.3f} V")
assert abs(i_tl * 1e3 - 1.92) < 0.01 and abs(v_mid - 0.998) < 1e-3
with drawing(fontsize=11) as d:
    xk, yT = 0.0, 7.0
    d += elm.Vdd().at((xk, yT)).label("+12 V")
    d += elm.Resistor().endpoints((xk, yT), (xk, 4.5)).label("4.7 kΩ", loc="bottom")
    d += elm.Dot().at((xk, 4.5))
    lab(d, (xk - 0.2, 5.15), "K 点 约 2.495 V", ha="right", fs_=10.5, color=fs.C["fb"])
    z = elm.Zener().endpoints((xk, 2.0), (xk, 4.5)).label("TL431\n（K 在上，A 在下）", loc="bottom"); d += z
    d += elm.Ground().at((xk, 2.0))
    # REF 脚：第三只独立的脚，从三角形侧面斜着伸出（不从阴极横杠的高度接），再用导线短接回 K 点
    d += elm.Line().at((xk - 0.13, 3.33)).to((xk - 0.55, 2.95))
    d += elm.Dot().at((xk - 0.55, 2.95))
    lab(d, (xk - 0.8, 2.62), "REF", fs_=9.5, color=fs.C["bad"])
    d += elm.Line().at((xk - 0.55, 2.95)).to((xk - 1.4, 2.95))
    d += elm.Line().at((xk - 1.4, 2.95)).to((xk - 1.4, 4.5))
    d += elm.Line().at((xk - 1.4, 4.5)).to((xk, 4.5))
    lab(d, (xk - 1.55, 3.7), "REF 脚（第三只脚）\n用导线和 K 短接", ha="right", fs_=10, color=fs.C["bad"])
    # K 点 → 15 kΩ → 中点 → 10 kΩ → 地
    xd = 3.6
    d += elm.Line().at((xk, 4.5)).to((xd, 4.5))
    d += elm.Resistor().endpoints((xd, 4.5), (xd, 2.0)).label("15 kΩ", loc="bottom")
    d += elm.Dot().at((xd, 2.0))
    d += elm.Resistor().endpoints((xd, 2.0), (xd, -0.5)).label("10 kΩ", loc="bottom")
    d += elm.Ground().at((xd, -0.5))
    d += elm.Line().at((xd, 2.0)).to((xd + 2.2, 2.0))
    d += elm.Dot(open=True).at((xd + 2.2, 2.0)).label("$V_{REF}$ 0.998 V\n接 LM358 3 脚\n（取代 $R_1$、$R_2$）", "right")
    note(d, (xk - 2.6, -1.6), "TL431 电流约 1.92 mA（手册要求 1 mA 以上）；分压只取走约 0.1 mA。\n引脚顺序因封装而异：动手前对照你手里那只的数据手册，别把 A、K 接反。")
print("[图 39-p3-3] TL431 基准接法")
save_schem(d, N, "39_p3_3_tl431_ref.png")

# ---------- 图 39-p3-1 / 39-p3-7：参数篇本页对照用的原理图（与 p2-1、p2-4 同一电路） ----------
with drawing(fontsize=11) as d:
    P = ccs(d, full=True)
    lab(d, (P["gate"][0] - 0.3, P["gate"][1] + 0.4), "$V_G$", ha="right", fs_=11, color=fs.C["vin"])
    note(d, (P["xr"] - 0.8, -3.3), "V_CC = 12 V；V_REF = 12 V × 910 ÷ (10 k + 910) ≈ 1.0009 V；I = V_REF ÷ R_S ≈ 100 mA；R_G、R_F、C_F 是补偿网络")
print("[图 39-p3-1] 参数篇对照：完整恒流沉（LM358 标 1/2/3/4/8 脚）")
save_schem(d, N, "39_p3_1_ccs_params.png")
hbridge("图 39-p3-1", "39_p3_7_hbridge_snubber.png")
# ======================= page4 动手实验篇：面包板接线图 =======================
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

# =============================== page4 动手实验篇 ===============================
YEL = fs.C["hi"]


def bbp(bb, hole, text, edge="k"):
    """面包板上的测量点：黄色圆圈写编号，红边 = 红表笔插这里，黑边 = 黑表笔插这里。"""
    x, y = bb.xy(hole) if isinstance(hole, str) else hole
    bb.ax.add_patch(Circle((x, y), 0.36, fc=YEL, ec=edge, lw=1.6, zorder=9))
    bb.ax.text(x, y, text, ha="center", va="center", fontsize=8.5, zorder=10)


# ---------- 实验 A：理论读数（与 page2、spice/39 一致） ----------
LAB_RL = [22, 47, 68, 100, 120]
LAB_I = {r: (I_SET if r + RS < RL_MAX + RS else None) for r in LAB_RL}
for r in LAB_RL:
    i = float(i_ideal(r)) if r <= RL_MAX else float(SP_I[list(SP_RL).index(r)])
    vds = VCC - i * (r + RS)
    LAB_I[r] = (i, i * RS, vds, vds * i)
    print(f"[数值] 实验A R_L={r} Ω：I = {i*1e3:.1f} mA，V_S = {i*RS:.3f} V，V_DS = {vds:.3f} V，管耗 {vds*i:.2f} W，R_L 功率 {i*i*r:.2f} W")
assert abs(LAB_I[47][2] - 6.296) < 0.01 and abs(LAB_I[120][1] - 0.923) < 0.001 and LAB_I[120][2] < 0.01
assert max(LAB_I[r][0] ** 2 * r for r in LAB_RL) < 2.0 * 0.6        # 2 W 电阻留足一半余量

# ---------- 图 39-p4-1：实验 A 面包板 ----------
WIRE["pos"] = (fs.C["bad"], "+12 V")
WIRE["gnd"] = ("#000000", "GND（0 V）")
WIRE["sig"] = (fs.C["fb"], "基准 $V_{REF}$")
WIRE["out"] = (fs.C["vin"], "栅极驱动")
WIRE["fb"] = (fs.C["vout"], "采样反馈 / 漏极")
bb = Breadboard(30, "实验 A：恒流沉（LM358 + IRLZ44N + 10 Ω 采样电阻，负载 $R_L$ 换着插）",
                size=(10, 8.4), rails=("+12 V", "GND", "GND", "+12 V"))
bb.ax.set_ylim(-14.5, 11.6)
bb.chip(8, "LM358", 8, names={1: "OUT", 2: "IN−", 3: "IN+", 4: "GND", 8: "V+"})
bb.wire("a8", "T+8", "pos")
bb.wire("c9", "c10", "fb")                       # 另一半运放接成跟随器（7 脚接 6 脚）
bb.wire("a11", "T-11", "gnd")                    # 5 脚接地
bb.wire("j11", "B-11", "gnd")                    # 4 脚接地
bb.part("g3", "g5", "R1 10 kΩ", "R", 1)
bb.wire("j3", "B+3", "pos")
bb.part("j5", "B-5", "", "R")
bb.ax.text(5.35, -6.05, "R2 910 Ω", ha="left", va="center", fontsize=8.5, zorder=7, bbox=dict(fc="#f7f5ef", ec="none", pad=0.5))
bb.wire("h5", "h10", "sig", via=[(5, -2.9), (10, -2.9)])
bb.part("g8", "g9", "", "C")
bb.ax.text(8.5, -1.9, "CF", ha="center", va="bottom", fontsize=7.5, zorder=7)
bb.part("i9", "i14", "", "R")
bb.ax.text(11.5, -3.92, "RF 1 kΩ", ha="center", va="center", fontsize=8.5, zorder=7, bbox=dict(fc="#f7f5ef", ec="none", pad=0.5))
bb.part("j8", "j13", "", "R")
bb.ax.text(13.3, -5.4, "RG 100 Ω", ha="left", va="center", fontsize=8.5, zorder=7,
           bbox=dict(fc="#f7f5ef", ec="none", pad=0.5))
bb.wire("h13", "h20", "out", via=[(13, -2.9), (20, -2.9)])
bb.wire("g14", "g22", "fb", via=[(14, -1.9), (22, -1.9)])
# IRLZ44N：三脚插 f20（G）f21（D）f22（S），散热片朝上
bb.ax.add_patch(Rectangle((19.45, -1.0), 3.1, 1.6, fc="#2b2b2b", ec="k", zorder=6))
bb.ax.add_patch(Rectangle((19.45, 0.6), 3.1, 1.5, fc="#b8bcc2", ec="0.3", zorder=6))
bb.ax.text(21, -0.2, "IRLZ44N", color="w", ha="center", va="center", fontsize=8, zorder=8)
bb.ax.text(21, 1.35, "散热片", ha="center", va="center", fontsize=8, zorder=8)
for c, nm in ((20, "G"), (21, "D"), (22, "S")):
    bb.ax.plot([c, c], [-1.0, BB_Y["f"]], color="0.3", lw=1.6, zorder=7)
    bb.ax.add_patch(Circle((c, BB_Y["f"]), 0.17, fc="0.15", ec="none", zorder=7))
    bb.ax.text(c + 0.18, -1.2, nm, fontsize=7, ha="left", va="center", zorder=8)
bb.wire("i21", "i24", "fb", via=[(21, -4.9), (24, -4.9)])
bb.part("g24", "g28", "$R_L$（2 W，换着插）", "R", 1)
bb.wire("j28", "B+28", "pos")
bb.part("j22", "B-22", "", "R")
bb.ax.text(22.35, -6.05, "RS 10 Ω", ha="left", va="center", fontsize=8.5, zorder=7, bbox=dict(fc="#f7f5ef", ec="none", pad=0.5))
bb.wire("T+30", "B+30", "pos", via=[(30.75, 8.6), (30.75, -7.6)])
bb.wire("T-29", "B-29", "gnd", via=[(29.5, 7.2), (30.4, 7.2), (30.4, -6.2), (29.5, -6.2)])
bb.module(1.0, -12.6, 7.0, 1.7, "12 V 直流电源适配器\n（≥ 0.5 A）", fc="#e6f0f8")
bb.wire((2.5, -10.9), "B+2", "pos")
bb.wire((6.5, -10.9), "B-7", "gnd", via=[(6.5, -9.0), (7.0, -9.0)])
bbp(bb, "i5", "①")
bbp(bb, "h22", "②")
bbp(bb, "j21", "③", edge=fs.C["bad"])
bbp(bb, "h8", "④")
bb.note(10.5, -10.6, "测量点（黄圈）：①基准 $V_{REF}$　②采样电压 $V_S$　④运放 1 脚\n"
        "这三个都是红表笔插黄圈、黑表笔插 GND 轨；③是 $V_{DS}$：红表笔插 j21（漏极列），\n黑表笔插 h22（源极列）",
        va="center")
bb.note(12.6, 4.2, "上半区只用第 8～11 列：8 脚接 +12 V；\n另一半运放 7、6 脚用 c9–c10 短线连起来、\n5 脚接地，免得它乱振。MOSFET 立着插，\n散热片朝上，别让金属片碰到任何导线。", va="center",
        bbox=dict(fc="#f7f5ef", ec="none", pad=1.5))
bb.legend()
_lg = bb.ax.get_legend(); _lg.set_loc("upper center"); _lg.set_bbox_to_anchor((0.5, 0.995)); _lg.set_ncols(3)
bb.save(N, "39_p4_1_breadboard_ccs.png")

# ---------- 图 39-p4-2：实验 A 对照原理图 ----------
with drawing(fontsize=11) as d:
    P = ccs(d, full=True, pins=False)
    lab(d, (P["gate"][0] - 0.3, P["gate"][1] + 0.4), "$V_G$", ha="right", fs_=11, color=fs.C["vin"])
    probe(d, P["vref"], "①", dx=-0.9, dy=-0.9)
    probe(d, P["s"], "②", dx=0.9, dy=-0.6)
    probe(d, P["d"], "③", dx=1.0, dy=0.6)
    probe(d, P["out"], "④", dx=0.0, dy=1.2)
    colnote(d, (P["xr"], (P["yT"] + P["inp"][1]) / 2), "R1 在 g3–g5", "left", ofst=1.9)
    colnote(d, (P["xr"], (P["inp"][1] - 1.6) / 2), "R2 在 j5–GND 轨", "left", ofst=1.9)
    colnote(d, ((P["xc"] + P["xm"]) / 2, P["ys"] - 1.0), "RF 在 i9–i14", "bottom", ofst=0.1)
    colnote(d, (P["xm"], -1.35), "RS 在 j22–GND 轨", "left", ofst=0.5)
    colnote(d, (P["xm"], 5.25), "$R_L$ 在 g24–g28", "left", ofst=0.5)
    colnote(d, ((P["xc"] + P["gate"][0]) / 2, P["out"][1] + 0.9), "RG 在 j8–j13", "top", ofst=0.1)
    _bx, _by = P["xm"] + 2.2, -3.0
    _dbox(d, _bx, _by, _bx + 6.4, _by + 2.1)
    lab(d, (_bx + 0.2, _by + 1.05), "LM358 另一半（B 运放）：\n6、7 脚短接（c9–c10），5 脚接地（a11），\n接成接地的跟随器，防止它乱振", fs_=9, color=GRAY)
    colnote(d, (P["xr"], P["yT"]), "R1 上端：j3 红线接 +12 V 轨", "left", ofst=0.5)
    note(d, (P["xr"] - 1.0, -3.4), "第 5 列 = $V_{REF}$；第 8 列 = 运放 1 脚；第 9 列 = 运放 2 脚；第 10 列 = 运放 3 脚；"
         "第 20/21/22 列 = G/D/S。\n③ 的红表笔插漏极（第 21 列），黑表笔插源极（第 22 列）；其余测量点黑表笔都接 GND。")
print("[图 39-p4-2] 实验 A 对照原理图：①V_REF ②V_S ③V_DS ④1 脚")
save_schem(d, N, "39_p4_2_schem_lab.png")

# ---------- 实验 B：DRV8871 换向，线圈用 12 V 继电器 ----------
R_RELAY, R_SEN = 400.0, 10.0                    # SRD-12VDC 线圈（手册 400 Ω）、采样 10 Ω
I_B = VCC / (R_RELAY + R_SEN + R_ON_BRIDGE)
V_SEN, V_COIL, V_OUT = I_B * R_SEN, I_B * R_RELAY, I_B * (R_RELAY + R_SEN)
lo_b = VCC / (R_RELAY * 1.1 + R_SEN + R_ON_BRIDGE) * R_SEN
hi_b = VCC / (R_RELAY * 0.9 + R_SEN + R_ON_BRIDGE) * R_SEN
TAU_RELAY_NOTE = "继电器线圈电感手册没给，不估时间常数"
print(f"[数值] 实验B：I = {I_B*1e3:.2f} mA，V_SEN = {V_SEN:.3f} V，线圈 {V_COIL:.2f} V，OUT1–OUT2 {V_OUT:.2f} V；"
      f"线圈 ±10% 时 V_SEN {lo_b:.3f}–{hi_b:.3f} V")
assert abs(V_SEN - 0.292) < 0.001 and abs(V_COIL - 11.69) < 0.01 and abs(V_OUT - 11.98) < 0.01
assert abs(lo_b - 0.266) < 0.001 and abs(hi_b - 0.324) < 0.001

# ---------- 图 39-p4-3：实验 B 面包板 ----------
WIRE["pos"] = (fs.C["bad"], "+5 V（Arduino）/ +12 V")
WIRE["gnd"] = ("#000000", "GND（公共地）")
WIRE["sig"] = (fs.C["vin"], "控制 IN1 / IN2")
WIRE["out"] = (fs.C["vout"], "OUT1 / OUT2")
WIRE["fb"] = (fs.C["fb"], "接继电器线圈")
bb = Breadboard(24, "实验 B：DRV8871 模块给继电器线圈换向（图中 IN1=1、IN2=0，正向）",
                size=(10, 9.0), rails=("（未用）", "（未用）", "GND", "+5 V"))
for t in bb.ax.texts:
    if t.get_text() == "（未用）":
        t.set_color("0.6"); t.set_fontweight("normal"); t.set_fontsize(8.5)
for ln in bb.ax.lines:
    ys = ln.get_ydata()
    if len(ys) == 2 and ys[0] == ys[1] and ys[0] in (BB_Y["T+"] + 0.42, BB_Y["T-"] + 0.42):
        ln.set_color("0.75")
bb.ax.set_ylim(-21.0, 11.6)
bb.ax.set_xlim(-3.4, 31.0)
COLS_B = dict(IN1=4, IN2=8)
bb.wire("i4", "B+5", "pos")
bb.wire("i8", "B-9", "gnd")
for name, c in COLS_B.items():
    bb.wire(f"f{c}", (c, -11.0), "sig", via=[(c - 0.5, -1.9), (c - 0.5, -9.0), (c, -9.6)])
    bb.ax.text(c + 0.3, -3.0, name, ha="left", va="center", fontsize=9, color=fs.C["vin"], fontweight="bold", zorder=9)
bb.part("h18", "h22", "$R_{SEN}$ 10 Ω", "R", -1)
bb.wire("g14", (25.6, -1.9), "fb", via=[(14, -1.9)])
bb.wire("g18", (25.6, -2.9), "fb", via=[(18, -2.9)])
bb.module(25.6, -3.8, 4.4, 2.8, "继电器\nSRD-12VDC\n（只用两个\n线圈脚）", fc="#fdf1d8")
mx0, my0 = 2.0, -15.8
bb.module(mx0, my0, 22.0, 4.8, "", fc="#e8eef5")
bb.ax.text(13.0, -13.6, "DRV8871 模块（Adafruit 3190）\n不接 ILIM 以外的任何东西；板上 30 kΩ 限流约 2 A", ha="center", va="center", fontsize=8.5, zorder=8)
PINB = {"IN1": (4, -11.0), "IN2": (8, -11.0), "GND": (11, -11.0)}
for k, (x, y) in PINB.items():
    bb.ax.add_patch(Circle((x, y), 0.22, fc="0.15", ec="none", zorder=8))
    bb.ax.text(x, y - 0.45, k, ha="center", va="top", fontsize=7.5, zorder=8)
bb.wire(PINB["GND"], "B-12", "gnd", via=[(11, -9.0), (12, -9.0)])
TB = {"OUT1": (14.0, -11.0), "OUT2": (22.0, -11.0), "VM": (16.0, -15.8), "GND ": (20.0, -15.8)}
for k, (x, y) in TB.items():
    bb.ax.add_patch(Rectangle((x - 0.35, y - 0.35), 0.7, 0.7, fc="#3a7d44", ec="k", zorder=8))
    bb.ax.text(x, y - 0.55 if y > -12 else y + 0.55, k.strip(), ha="center", va="top" if y > -12 else "bottom", fontsize=7.5, zorder=8)
bb.wire(TB["OUT1"], "j14", "out")
bb.wire(TB["OUT2"], "j22", "out")
bb.module(14.5, -20.4, 7.0, 1.6, "12 V 直流电源适配器", fc="#e6f0f8")
bb.wire((16.0, -18.8), TB["VM"], "pos")
bb.wire((20.0, -18.8), TB["GND "], "gnd")
# VM 旁的 100 µF 电解电容：吸收换向时线圈回灌的能量（工程调研建议）
bb.ax.plot([16.0, 17.2], [-17.6, -17.6], color=WIRE["pos"][0], lw=1.6, zorder=7)
bb.ax.plot([18.8, 20.0], [-17.6, -17.6], color="k", lw=1.6, zorder=7)
bb.ax.add_patch(Rectangle((17.2, -17.95), 1.6, 0.7, fc="#3b5b92", ec="k", zorder=8))
bb.ax.text(17.45, -17.6, "+", color="w", ha="center", va="center", fontsize=8, zorder=9)
bb.ax.text(18.0, -17.0, "C 100 µF / 25 V（+ 接 VM）", ha="center", va="bottom", fontsize=7.5, zorder=9,
           bbox=dict(fc="#f7f5ef", ec="none", pad=0.5))
bb.module(-2.6, -20.4, 7.6, 1.6, "Arduino UNO（只用 5V、GND）", fc="#efe6f3")
bb.wire((-1.6, -18.8), "B+1", "pos", via=[(-1.6, -9.0), (1.0, -9.0)])
bb.wire((0.6, -18.8), "B-3", "gnd", via=[(0.6, -10.0), (2.5, -10.0), (2.5, -7.1)])
bbp(bb, "f14", "①", edge=fs.C["bad"])
bbp(bb, "f18", "①")
bbp(bb, "i18", "②", edge=fs.C["bad"])
bbp(bb, "i22", "②")
bb.note(13.0, 3.6, "测量点（黄圈）：红边 = 红表笔，黑边 = 黑表笔\n①线圈电压（第 14 列 → 第 18 列）\n②采样电压（第 18 列 → 第 22 列），"
        "÷ 10 Ω 就是电流\n上半区不用", va="center", ha="center", bbox=dict(fc="#f7f5ef", ec="none", pad=1.5))
bb.legend()
_lg = bb.ax.get_legend(); _lg.set_loc("upper center"); _lg.set_bbox_to_anchor((0.5, 0.995)); _lg.set_ncols(3)
bb.save(N, "39_p4_3_breadboard_drv.png")

# ---------- 图 39-p4-4：实验 B 对照原理图 ----------
with drawing(fontsize=11) as d:
    m = module("DRV8871 模块", left=("IN1", "IN2", "GND"), right=("OUT1", "OUT2", "VM"), w=3.4).at((0, 0))
    d += m
    A = m.absanchors
    # 控制端
    d += elm.Line().at(A["IN1"]).to((A["IN1"][0] - 1.6, A["IN1"][1]))
    d += elm.Vdd().at((A["IN1"][0] - 1.6, A["IN1"][1])).label("+5 V（1）")
    colnote(d, (A["IN1"][0] - 0.8, A["IN1"][1]), "第 4 列", "bottom")
    d += elm.Line().at(A["IN2"]).to((A["IN2"][0] - 3.4, A["IN2"][1]))
    d += elm.Ground().at((A["IN2"][0] - 3.4, A["IN2"][1]))
    lab(d, (A["IN2"][0] - 3.6, A["IN2"][1] + 0.35), "GND（0）", ha="right", fs_=9.5)
    colnote(d, (A["IN2"][0] - 1.0, A["IN2"][1]), "第 8 列", "bottom")
    d += elm.Line().at(A["GND"]).to((A["GND"][0] - 0.8, A["GND"][1]))
    d += elm.Ground().at((A["GND"][0] - 0.8, A["GND"][1]))
    # 电源
    xv = A["VM"][0] + 2.6
    d += elm.Line().at(A["VM"]).to((xv, A["VM"][1]))
    d += (bt := elm.Battery().endpoints((xv, A["VM"][1] - 2.4), (xv, A["VM"][1])).reverse()); bat_pm(d, bt, plus_toward=(xv, A["VM"][1]), side=1)
    lab(d, (xv + 0.5, A["VM"][1] - 1.9), "12 V\n适配器", fs_=10)
    d += elm.Ground().at((xv, A["VM"][1] - 2.4))
    xcap = A["VM"][0] + 0.9                        # 100 µF 电解电容并在 VM 与地之间
    d += elm.Dot().at((xcap, A["VM"][1]))
    d += elm.Capacitor(polar=True).endpoints((xcap, A["VM"][1]), (xcap, A["VM"][1] - 2.4))
    lab(d, (xcap - 0.35, A["VM"][1] - 1.2), "100 µF", ha="right", fs_=9.5)
    d += elm.Line().at((xcap, A["VM"][1] - 2.4)).to((xv, A["VM"][1] - 2.4))
    # 线圈与采样电阻
    yo1, yo2 = A["OUT1"][1], A["OUT2"][1]
    x1 = A["OUT1"][0] + 1.0
    xJ = x1 + 7.0
    d += elm.Line().at(A["OUT1"]).to((x1, yo1))
    d += elm.Dot().at((x1, yo1))
    d += elm.Line().at((x1, yo1)).to((x1, yo1 + 2.0))
    d += elm.Inductor2(loops=3).endpoints((x1, yo1 + 2.0), (x1 + 3.0, yo1 + 2.0))
    d += elm.Resistor().endpoints((x1 + 3.0, yo1 + 2.0), (xJ, yo1 + 2.0)).label("约 400 Ω", loc="top")
    lab(d, (x1 + 3.0, yo1 + 3.75), "继电器线圈 SRD-12VDC（线圈的电感 + 铜线电阻）", ha="center", fs_=10)
    d += elm.Line().at((xJ, yo1 + 2.0)).to((xJ, yo1))
    d += elm.Dot().at((xJ, yo1))
    d += elm.Resistor().endpoints((xJ, yo1), (xJ, yo2 - 2.0)).label("$R_{SEN}$ 10 Ω", loc="bottom")
    x2 = x1 + 3.0
    d += elm.Line().at((xJ, yo2 - 2.0)).to((x2, yo2 - 2.0))
    d += elm.Line().at((x2, yo2 - 2.0)).to((x2, yo2))
    d += elm.Line().at((x2, yo2)).to(A["OUT2"])
    d += elm.Dot().at((x2, yo2))
    colnote(d, (x1, yo1), "第 14 列", "left", ofst=0.25)
    colnote(d, (xJ, yo1), "第 18 列", "right", ofst=0.25)
    colnote(d, (x2, yo2 - 2.0), "第 22 列", "bottom")
    _par_arrow(d, (x1 + 0.3, yo1 + 2.05), (xJ - 0.3, yo1 + 2.05), (0, 1.0))
    lab(d, ((x1 + xJ) / 2 + 1.2, yo1 + 1.35), "IN1=1、IN2=0 时电流方向", fs_=9, color=fs.C["cur"])
    probe(d, (x1, yo1 + 1.0), "①", dx=0.9, dy=0)
    probe(d, (xJ, yo1 - 1.0), "②", dx=0.9, dy=0)
    note(d, (-5.5, yo2 - 4.6), "① 线圈电压：红表笔第 14 列，黑表笔第 18 列；② 采样电压：红表笔第 18 列，黑表笔第 22 列。\n"
         "把 IN1、IN2 两根跳线对调（IN1=0、IN2=1），① ② 都变成负数：电流反向了。")
print("[图 39-p4-4] 实验 B 对照原理图：DRV8871 + 继电器线圈 400 Ω + R_SEN 10 Ω")
save_schem(d, N, "39_p4_4_schem_lab.png")


# ---------- 图 39-p4-5：程序换向时 Arduino 与 DRV8871 模块的接线 ----------
with drawing(fontsize=11) as d:
    m = module("DRV8871 模块", left=("IN1", "IN2", "GND"), right=("OUT1", "OUT2", "VM"), w=3.4).at((0, 0))
    d += m
    A = m.absanchors
    ar = module("Arduino Uno", left=(), right=("D2", "D3", "GND"), w=3.0).at((-9.0, 0))
    d += ar
    B = ar.absanchors
    for a, b, c, txt in (("D2", "IN1", fs.C["vin"], "第 4 列"), ("D3", "IN2", fs.C["vin"], "第 8 列"), ("GND", "GND", "black", "GND 轨")):
        d += elm.Line(color=c).at(B[a]).to(A[b])
        colnote(d, ((B[a][0] + A[b][0]) / 2, A[b][1]), txt, "top", ofst=0.05)
    xg = (B["GND"][0] + A["GND"][0]) / 2
    d += elm.Dot().at((xg, A["GND"][1]))
    d += elm.Ground().at((xg, A["GND"][1]))
    for nm in ("OUT1", "OUT2", "VM"):
        d += elm.Line().at(A[nm]).to((A[nm][0] + 1.0, A[nm][1]))
    lab(d, (A["OUT1"][0] + 1.2, A["OUT1"][1] - 0.5), "OUT1、OUT2、VM：\n和图 39-p4-4 完全一样\n（线圈 + $R_{SEN}$，12 V + 100 µF）", fs_=9.5, color=GRAY)
    note(d, (-9.5, A["GND"][1] - 2.2), "只改两根线：第 4 列原来接 +5 V 轨的线、第 8 列原来接 GND 轨的线都拔掉，\n"
         "改为第 4 列接 Arduino D2、第 8 列接 Arduino D3；Arduino 的 GND 一定要接到面包板 GND 轨。\n"
         "Arduino 用 USB 供电；12 V 适配器只接模块的 VM，不接 Arduino 的 5 V 脚。")
print("[图 39-p4-5] 程序换向：Arduino D2/D3 → DRV8871 IN1/IN2，共地")
save_schem(d, N, "39_p4_5_arduino_wiring.png")

# ---------- 图 39-p4-6：选做 A7——把采样电阻挪到高边（亲手验证预测题） ----------
d = wrong_fig(False, cols=True)
print("[图 39-p4-6] 选做 A7：高边接法改线图")
save_schem(d, N, "39_p4_6_schem_highside.png")

# ---------- 图 39-p4-7：示波器上应看到的换向波形（R_SEN 两端，CH1 − CH2） ----------
R_LOOP = R_RELAY + R_SEN + R_ON_BRIDGE
L_LIST = (0.2, 0.4, 0.8)                       # 继电器线圈电感手册没给；0.4 H 取自 zencircuitlab 零件页 [待核实]
t = np.linspace(-1, 8, 1801) * 1e-3
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
styles = (fs.LS["third"], fs.LS["vout"], fs.LS["vin"])
T0 = {}
for L, st in zip(L_LIST, styles):
    tau = L / R_LOOP
    v = np.where(t < 0, -V_SEN, V_SEN * (1 - 2 * np.exp(-np.clip(t, 0, None) / tau)))
    T0[L] = tau * np.log(2)
    ax.plot(t * 1e3, v, **st, label=f"L = {L*1e3:.0f} mH：τ = {tau*1e3:.2f} ms，过零 $t_0$ = {T0[L]*1e3:.2f} ms")
fs.ref_h(ax, 0, None)
fs.ref_v(ax, 0, "换向", y=0.97)
ax.plot([T0[0.4] * 1e3], [0], "o", color=fs.C["vout"], ms=4, zorder=5)
print(f"[数值] L=0.4 H 过零 t0 = {T0[0.4]*1e3:.2f} ms")
ax.annotate(f"$t_0$ ≈ {T0[0.4]*1e3:.2f} ms", (T0[0.4] * 1e3, 0), xytext=(T0[0.4] * 1e3 + 0.6, -0.12), fontsize=9, color=fs.C["vout"],
            arrowprops=dict(arrowstyle="->", color=fs.C["vout"]))
ax.set_ylim(-0.36, 0.36)
fs.axlabels(ax, "IN1/IN2 翻转后的时间", "ms", "$V_{SEN}$（CH1 − CH2）", "V")
ax.legend(loc="lower right", fontsize=7.5)
print(f"[数值] 实验B 换向：R_loop = {R_LOOP:.1f} Ω，" + "，".join(f"L={L} H → t0={T0[L]*1e3:.3f} ms" for L in L_LIST))
assert abs(T0[0.4] * 1e3 - 0.675) < 0.005
fs.save(fig, N, "39_p4_7_reversal_scope.png")
