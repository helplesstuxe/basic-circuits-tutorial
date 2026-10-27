"""43 推挽功放：甲、乙、甲乙类：全部配图。
运行：/workspace/circuits-venv/bin/python code/figs/43_figs.py
波形 / 扫描数据来自 spice/43/*.csv（由 spice/43/run.py 从 ngspice 结果抽稀生成，先跑 run.py）。
图上的每个数字都由本脚本算出并打印；关键结论用 assert 检查。
电路统一用单 12 V 电源：TL072 一半做 6 V 中点参考 V_MID（只给输入偏置），另一半做增益 3 的同相放大，
BD139 / BD140 推挽，输出经 1000 µF 耦合电容接 8 Ω 负载到真地。
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from lab_schem import probe, colnote, lab, title, note, ring, Hop, _dbox, GRAY

N = "43"
SP = os.path.join(HERE, "..", "..", "spice", "43")


def csv(name):
    """读 spice/43 下的 CSV（第一行是列名），返回 {列名: 数组}。"""
    path = os.path.join(SP, name)
    head = open(path).readline().strip().split(",")
    arr = np.loadtxt(path, delimiter=",", skiprows=1, ndmin=2)
    return {h: arr[:, i] for i, h in enumerate(head)}


# ============================ 公共数值（page2 推导用的同一组数） ============================
VS = 12.0                 # 单电源
VCC = VS / 2              # 单电源 + 耦合电容：等效 V_CC = 6 V
RL = 8.0                  # 8 Ω / 5 W 功率电阻（测效率用）
RSPK = 8.0 + 10.0         # 试听：8 Ω 喇叭串 10 Ω
RE = 3.3                  # 发射极电阻
GAIN = 3.0                # 1 + 20k/10k
RTH_JA, RTH_JC = 100.0, 10.0      # BD139 数据手册 °C/W
IQ = 32.96e-3             # SPICE 静态电流（R_E 3.3 Ω，两只 1N4148，恒流源约 23.7 mA）
VP_MAX = 3.11             # SPICE：输入 1.2 V 峰值时的 V_p（上恒流源没有余量了，正负半周一起被卡住）
ICCS = 23.7e-3            # SPICE：恒流源电流（上 23.75 mA、下 23.6 mA）


def pb_ideal(vp, vcc=VCC, rl=RL):
    """理想乙类（单电源时 V_S = 2 V_CC，只有上管从电源取电）：P_L、P_S、P_D、η。"""
    pl = vp ** 2 / (2 * rl)
    ps = 2 * vcc * vp / (np.pi * rl)
    return pl, ps, ps - pl, np.divide(pl, ps, out=np.zeros_like(np.asarray(pl, float)), where=np.asarray(ps) > 0)


VP_PD = 2 * VCC / np.pi
PD_MAX = 2 * VCC ** 2 / (np.pi ** 2 * RL)
PL_MAX = VCC ** 2 / (2 * RL)
print(f"[数值] 甲类：电源 {VS*VS/(2*RL):.2f} W，最大输出 {VS*VS/(8*RL):.2f} W，η_max = 25%")
print(f"[数值] 乙类（等效 V_CC 6 V、8 Ω）：P_L,max = {PL_MAX:.3f} W；管耗最大点 V_p = {VP_PD:.3f} V，P_D,max = {PD_MAX:.3f} W（每管 {PD_MAX/2:.3f} W）= {PD_MAX/PL_MAX:.3f} P_L,max")
assert abs(VS * VS / (2 * RL) - 9) < 1e-9 and abs(VS * VS / (8 * RL) - 2.25) < 1e-9
assert abs(VP_PD - 3.820) < 1e-3 and abs(PD_MAX - 0.912) < 1e-3 and abs(PD_MAX / PL_MAX - 0.405) < 1e-3
_pl, _ps, _pd, _eta = pb_ideal(np.array([2.0]))
print(f"[数值] V_p = 2 V：P_L = {_pl[0]:.3f} W，P_S = {_ps[0]:.3f} W，η = {_eta[0]*100:.1f}%")
assert abs(_ps[0] - 0.955) < 1e-3 and abs(_eta[0] - 0.2618) < 1e-3
EFF = csv("eff.csv")


# ============================ 公用电路图：单 12 V 推挽 ============================
def amp(d, bias="AB", loop="in", lab_cols=False, show_vm_box=True, show_meter=True, rl_text="$R_L$ 8 Ω", show_zobel=True, src="sin"):
    """画单 12 V 推挽功放。bias：'B' 乙类（两基极直接接运放输出）/ 'AB' 甲乙类（两只 1N4148 + 上下两个约 24 mA 恒流源）；
    loop：'open' 反馈取自运放输出 m（推挽在环外）/ 'in' 反馈取自推挽输出 OUT（推挽在环内）/ None 不画运放。
    返回关键点坐标字典。"""
    P = {}
    yT, yG = 6.0, -6.4
    xm = 4.4                          # 偏置列（运放输出 m 所在竖线）
    xo = 1.6                          # 运放输出
    P.update(yT=yT, yG=yG, xm=xm)
    # ---------- 推挽两管 ----------
    yb1, yb2 = 2.3, -2.3
    q1 = elm.BjtNpn(circle=True).anchor("base").at((xm + 1.3, yb1))
    q2 = elm.BjtPnp(circle=True).anchor("base").at((xm + 1.3, yb2))
    d += q1
    d += q2
    xe = q1.emitter[0]
    P.update(q1=q1, q2=q2, xe=xe)
    # 基极阻尼电阻 RS1 / RS2（22 Ω，焊在管子基极脚上）
    d += elm.Resistor().endpoints((xm, yb1), q1.base).scale(0.45).label("22 Ω", loc="top", fontsize=8.5)
    d += elm.Resistor().endpoints((xm, yb2), q2.base).scale(0.45).label("22 Ω", loc="bottom", fontsize=8.5)
    lab(d, (q1.center[0] + 0.55, q1.center[1] + 0.1), "Q1\nBD139", fs_=10)
    lab(d, (q2.center[0] + 0.55, q2.center[1] - 0.1), "Q2\nBD140", fs_=10)
    # 集电极：Q1 经电流表到 +12 V；Q2 到地
    if show_meter:
        d += elm.Line().at(q1.collector).to((xe, q1.collector[1] + 0.3))
        d += (mA := elm.MeterA().endpoints((xe, q1.collector[1] + 0.3), (xe, yT)))
        lab(d, (xe + 0.75, (q1.collector[1] + 0.3 + yT) / 2), "电流表\n（10 A 插孔、A 档）", fs_=9, color=C["cur"])
        P["meter"] = (xe, (q1.collector[1] + 0.3 + yT) / 2)
    else:
        d += elm.Line().at(q1.collector).to((xe, yT))
    d += elm.Line().at(q2.collector).to((xe, yG))
    # 发射极电阻 → OUT
    yo = 0.0
    d += elm.Resistor().endpoints(q1.emitter, (xe, yo + 0.0)).scale(0.6)
    d += elm.Resistor().endpoints((xe, yo), q2.emitter).scale(0.6)
    lab(d, (xe - 0.35, (q1.emitter[1] + yo) / 2), "RE1\n3.3 Ω", ha="right", fs_=9)
    lab(d, (xe - 0.35, (q2.emitter[1] + yo) / 2), "RE2\n3.3 Ω", ha="right", fs_=9)
    d += elm.Dot().at((xe, yo))
    P["out"] = (xe, yo)
    # 耦合电容 + 负载到真地
    xc = xe + 3.8
    d += elm.Line().at((xe, yo)).to((xe + 1.2, yo))
    # Zobel 网络：10 Ω + 100 nF 从 OUT 到真地
    xz = xe + 1.2
    if show_zobel:
        d += elm.Dot().at((xz, yo))
        d += elm.Resistor().endpoints((xz, yo), (xz, -2.4)).scale(0.6).label("Rz\n10 Ω", loc="bottom", fontsize=8.5)
        d += elm.Capacitor().endpoints((xz, -2.4), (xz, -4.2)).label("Cz\n100 nF", loc="bottom", fontsize=8.5)
        d += elm.Line().at((xz, -4.2)).to((xz, yG))
    P["zobel"] = (xz, -2.4)
    d += elm.Capacitor(polar=True).endpoints((xe + 1.2, yo), (xc, yo)).label("$C_o$ 1000 µF / 25 V", loc="top", fontsize=10)
    d += elm.Dot().at((xc, yo))
    d += elm.Resistor().endpoints((xc, yo), (xc, yG)).label(rl_text, loc="bottom", fontsize=10)
    P["ld"] = (xc, yo)
    P["xc"] = xc
    # 电源与地线
    d += elm.Line().at((xm - 0.0 if bias == "AB" else xe, yT)).to((xe, yT))
    d += elm.Line().at((xm if bias == "AB" else xe, yG)).to((xc, yG))
    d += elm.Vdd().at((xe, yT)).label("+12 V", fontsize=10)
    d += elm.Ground().at((xc, yG))
    lab(d, (xc + 0.3, yG - 0.35), "真地（GND）", fs_=9)
    # 偏置
    if bias == "AB":
        d += elm.SourceI().endpoints((xm, yT), (xm, yb1)).label("恒流源\n约 24 mA", loc="bottom", fontsize=9.5)
        d += elm.Dot().at((xm, yb1))
        d += elm.Diode().endpoints((xm, yb1), (xm, 0)).label("D1", loc="bottom", fontsize=9)
        d += elm.Dot().at((xm, 0))
        d += elm.Diode().endpoints((xm, 0), (xm, yb2)).label("D2", loc="bottom", fontsize=9)
        d += elm.Dot().at((xm, yb2))
        d += elm.SourceI().endpoints((xm, yb2), (xm, yG)).label("恒流源\n约 24 mA", loc="bottom", fontsize=9.5)
        d += elm.Dot().at((xm, yT))
        d += elm.Dot().at((xm, yG))
        lab(d, (xm - 1.05, 1.15), "1N4148 ×2\n贴在散热片上", ha="right", fs_=9)
    else:
        d += elm.Line().at((xm, yb1)).to((xm, yb2))
        d += elm.Dot().at((xm, 0))
    P["m"] = (xm, 0)
    P["b1"], P["b2"] = (xm, yb1), (xm, yb2)
    if loop is None:
        return P
    # ---------- 运放 UB（增益 3 同相放大） ----------
    op = elm.Opamp(leads=True).right().flip().anchor("out").at((xo, 0))
    d += op
    d += elm.Line().at(op.out).to((xm, 0))
    lab(d, (op.center[0] - 0.2, op.center[1] + 1.25), "TL072 B", ha="center", fs_=9.5)
    P["op"] = op
    # + 输入：Cin、Rbias；− 输入：RG 到中点参考 V_MID、RF 到 m 或 OUT
    pin, nin = op.in2, op.in1          # flip 之后 in2(+) 在上、in1(−) 在下
    if pin[1] < nin[1]:
        pin, nin = nin, pin
    xf = nin[0] - 0.45                 # 反馈节点 fb（RF 从这里往下）
    xg = xf - 1.5                      # RG 竖线
    xinp = xg - 1.0                    # 同相输入节点 inp（Rbias 竖线）
    yv = -4.4                          # 中点参考母线 V_MID
    d += elm.Line().at(pin).to((xinp, pin[1]))
    d += elm.Dot().at((xinp, pin[1]))
    if src == "sin":
        d += elm.Capacitor(polar=True).endpoints((xinp - 2.4, pin[1]), (xinp, pin[1])).label("Cin 10 µF", loc="top", fontsize=10)
        d += elm.SourceSin().endpoints((xinp - 2.4, yv + 0.8), (xinp - 2.4, pin[1])).label("信号源", loc="top", fontsize=9.5)
        d += elm.Ground().at((xinp - 2.4, yv + 0.8))
    else:                              # 实验 C：电位器分压慢扫，滑动端经 100 Ω 接 inp（信号源和 Cin 那一端拔掉）
        xs = xinp - 3.0
        d += elm.Resistor().endpoints((xs + 0.6, pin[1]), (xinp, pin[1])).label("100 Ω", loc="top", fontsize=9.5)
        d += elm.Resistor().endpoints((xs, pin[1] + 1.0), (xs, pin[1] + 3.2)).label("4.7 kΩ", loc="top", fontsize=9.5)
        d += elm.Vdd().at((xs, pin[1] + 3.2)).label("+12 V", fontsize=9.5)
        d += elm.Resistor().endpoints((xs, pin[1] - 1.0), (xs, pin[1] + 1.0)).label("电位器\n2 kΩ", loc="top", fontsize=9.5)
        d += elm.Line().at((xs + 0.6, pin[1])).to((xs + 0.25, pin[1]))
        d += elm.Arrow().at((xs + 0.6, pin[1])).to((xs + 0.22, pin[1]))
        d += elm.Resistor().endpoints((xs, pin[1] - 3.2), (xs, pin[1] - 1.0)).label("4.7 kΩ", loc="top", fontsize=9.5)
        d += elm.Ground().at((xs, pin[1] - 3.2))
    P["inp"] = (xinp, pin[1])
    P["sig"] = (xinp - 2.4, pin[1])
    d += elm.Resistor().endpoints((xinp, pin[1]), (xinp, yv)).label("Rbias\n100 kΩ", loc="top", fontsize=9.5)
    d += elm.Line().at(nin).to((xg, nin[1]))
    d += elm.Dot().at((xf, nin[1]))
    d += elm.Resistor().endpoints((xg, nin[1]), (xg, yv)).label("RG\n10 kΩ", loc="bottom", fontsize=9.5)
    d += elm.Line().at((xinp - 0.5, yv)).to((xg, yv)).color(C["fb"])
    d += elm.Dot().at((xinp, yv))
    lab(d, (xinp - 0.6, yv), "$V_{MID}$ = 6 V", ha="right", fs_=10, color=C["fb"])
    P["vm"] = (xinp, yv)
    P["fb"] = (xf, nin[1])
    P["xg"] = xg
    if loop == "open":
        yrf = -1.75
        xj = (xo + xm) / 2
        d += elm.Line().at((xf, nin[1])).to((xf, yrf))
        d += elm.Resistor().endpoints((xf, yrf), (xj, yrf)).label("RF 20 kΩ", loc="bottom", fontsize=9.5).color(C["fb"])
        d += elm.Line().at((xj, yrf)).to((xj, 0)).color(C["fb"])
        d += elm.Dot().at((xj, 0))
        P["rf"] = ((xf + xj) / 2, yrf)
    else:
        yrf = -5.3
        xj = xe + 0.8
        d += elm.Line().at((xf, nin[1])).to((xf, yrf))
        d += elm.Resistor().endpoints((xf, yrf), (xf + 2.4, yrf)).label("RF 20 kΩ", loc="bottom", fontsize=9.5).color(C["fb"])
        for xa, xh in ((xf + 2.4, xm), (xm + 0.25, xe)):        # 穿过偏置列和 Q2 集电极线：跨线弯
            d += elm.Line().at((xa, yrf)).to((xh - 0.25, yrf)).color(C["fb"])
            d += Hop().at((xh, yrf)).theta(0).color(C["fb"])
        d += elm.Line().at((xe + 0.25, yrf)).to((xj, yrf)).color(C["fb"])
        d += elm.Line().at((xj, yrf)).to((xj, yo)).color(C["fb"])
        d += elm.Dot().at((xj, yo))
        P["rf"] = (xf + 1.2, yrf)
    P["xo"] = xo
    return P




# =============================== page1 ===============================
# ---------- 图 43-p1-1：甲类（电阻负载）——不放音也烧 9 W ----------
IQ_A = VS / (2 * RL)
print(f"[图 43-p1-1] 甲类：I_q = {IQ_A:.2f} A，电源 {VS*IQ_A:.1f} W，最大 P_L = {VCC**2/(2*RL):.2f} W")
with drawing(fontsize=11) as d:
    yT, yG = 5.0, -3.6
    q = elm.BjtNpn(circle=True).anchor("base").at((0, 0))
    d += q
    xc = q.collector[0]
    d += elm.Resistor().endpoints((xc, yT), q.collector).label("$R_L$ 8 Ω（喇叭位置）", loc="bottom", fontsize=10)
    d += elm.Vdd().at((xc, yT)).label("+12 V", fontsize=10)
    d += elm.Line().at(q.emitter).to((xc, yG))
    d += elm.Ground().at((xc, yG))
    d += elm.Dot().at((xc, q.collector[1] + 0.3))
    lab(d, (q.center[0] + 0.55, q.center[1] - 0.6), "Q", fs_=10)
    d += elm.Line().at((-3.2, 0)).to(q.base)
    lab(d, (-3.2, 0.75), "输入 + 偏置：\n让集电极静止时停在 6 V", fs_=10)
    ring(d, (xc, q.collector[1] + 0.3), "$V_C$ 静止 = 6 V", dx=1.4)
    lab(d, (xc + 1.6, 3.4), "没有声音时也一直流\n$I_q$ = 6 V ÷ 8 Ω = 0.75 A", fs_=10, color=C["cur"])
    lab(d, (xc + 1.6, -1.9), "电源一直给：12 V × 0.75 A = 9 W\n喇叭最多拿到：(6 V)² ÷ (2 × 8 Ω) = 2.25 W\n效率最高 2.25 ÷ 9 = 25%", fs_=10)
    d += elm.Arrow().at((xc - 0.55, yT - 0.6)).to((xc - 0.55, q.collector[1] + 0.6)).color(C["cur"]).linewidth(1.3)
save_schem(d, N, "43_p1_1_class_a.png")

# ---------- 图 43-p1-2：推挽的想法：一只管子推、一只管子拉 ----------
with drawing(fontsize=11) as d:
    P = amp(d, "B", None, show_meter=False, show_zobel=False)
    d += elm.Line().at((P["xm"] - 2.4, 0)).to(P["m"])
    lab(d, (P["xm"] - 2.5, 0), "驱动电压 m\n（静止 6 V）", ha="right", fs_=10)
    xe, xc = P["xe"], P["xc"]
    d += elm.Arc2(k=0.3).at((xe + 0.35, 2.9)).to((xc - 0.5, 0.9)).color(C["bad"]).linewidth(1.4)
    lab(d, (xc + 0.5, 3.0), "正半周：Q1 导通，\n+12 V 经 Q1 往喇叭「推」电流", fs_=9.5, color=C["bad"])
    d += elm.Arc2(k=-0.3).at((xc - 0.5, -0.9)).to((xe + 0.35, -2.9)).color(C["vin"]).linewidth(1.4)
    lab(d, (xc + 1.6, -1.2), "负半周：Q2 导通，\n电容放电，电流经 Q2「拉」回地", fs_=9.5, color=C["vin"])
    lab(d, (xe + 0.25, -0.5), "OUT 静止 6 V", fs_=9)
    note(d, (P["xm"] - 6.0, -7.6), "只用一个 12 V 电源：推挽中点 OUT 停在 6 V，$C_o$ 把这 6 V 直流挡住，只让交流进喇叭；喇叭另一端接真地。")
save_schem(d, N, "43_p1_2_push_pull_idea.png")

# ---------- 图 43-p1-3：乙类的交越失真（SPICE：乙类、推挽在环外、输入 0.67 V 峰值、1 kHz） ----------
w = csv("w_B_open.csv")
t = (w["t_s"] - w["t_s"][0]) * 1e3
dz = np.abs(w["v_ld"]) < 0.02
lo, hi = (w["v_m"][dz] - 6).min(), (w["v_m"][dz] - 6).max()
print(f"[图 43-p1-3] 乙类死区：输出 |v_L| < 20 mV 时 m − 6 V 在 [{lo:.3f}, {hi:.3f}] V；负载峰值 {w['v_ld'].max():.3f} V（理想 2 V）")
assert -0.66 < lo < -0.58 and 0.58 < hi < 0.66
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw=dict(width_ratios=[1.6, 1]))
a1.plot(t, w["v_m"] - 6, color=fs.C["vin"], label="运放输出 m − 6 V（推挽的输入）")
a1.plot(t, w["v_ld"], color=fs.C["vout"], lw=1.8, label="负载电压 $v_L$")
for k in np.where(np.diff(dz.astype(int)) == 1)[0]:
    e = k + np.argmax(~dz[k + 1:]) + 1
    a1.axvspan(t[k], t[e], color=fs.C["bad"], alpha=0.15, lw=0)
a1.text(0.02, 0.03, "浅橙色带：两只管子都不导通，\n输出贴在 0 V", transform=a1.transAxes, fontsize=9, color=fs.C["bad"])
fs.ref_h(a1, 0)
fs.axlabels(a1, "时间", "ms", "电压", "V")
a1.set_title("(a) 波形：过零时输出「卡住」一段")
a1.legend(loc="upper right", fontsize=8.5)
a1.set_ylim(-2.4, 2.9)
ix = np.argsort(w["v_m"])
a2.plot(w["v_m"][ix] - 6, w["v_ld"][ix], color=fs.C["vout"], lw=1.8, label="乙类（SPICE）")
xx = np.linspace(-2.2, 2.2, 3)
a2.plot(xx, xx, **fs.LS["good"], label="理想：输出 = 输入")
a2.axvspan(lo, hi, color=fs.C["bad"], alpha=0.15, lw=0)
a2.annotate("", xy=(lo, -1.2), xytext=(hi, -1.2), arrowprops=dict(arrowstyle="<->", color=fs.C["bad"]))
a2.text(0, -1.45, "死区 ±0.6 V", ha="center", va="top", color=fs.C["bad"], fontsize=10)
fs.axlabels(a2, "m − 6 V", "V", "$v_L$", "V")
a2.set_title("(b) 输入–输出关系")
a2.legend(loc="upper left", fontsize=8.5)
fs.save(fig, N, "43_p1_3_crossover.png")

# ---------- 图 43-p1-4：效率随输出幅度：甲类 vs 乙类（理想）vs 甲乙类实测（SPICE） ----------
vp = np.linspace(0, VCC, 200)
eta_a = vp ** 2 / (2 * RL) / (VS * IQ_A)
eta_b = np.pi * vp / (4 * VCC)
fig, ax = plt.subplots(figsize=(7.4, 4.2))
ax.plot(vp, eta_a * 100, color=fs.C["third"], label="甲类（理想，$I_q$ = 0.75 A）")
ax.plot(vp, eta_b * 100, color=fs.C["vin"], label="乙类（理想，公式 $\\pi V_p/(4 \\times 6\\ V)$）")
ax.plot(EFF["vp"], EFF["eta"] * 100, "o", color=fs.C["vout"], ms=5, label=f"甲乙类 + 环内（SPICE，含 $I_q$ {IQ*1e3:.0f} mA）")
ax.axvspan(VP_MAX, VCC, color="0.85", alpha=0.6, lw=0)
ax.text((VP_MAX + VCC) / 2, 8, "本电路\n摆不到", ha="center", fontsize=9, color="0.3")
fs.mark(ax, VCC, 25, "{:.0f}", "%", color=fs.C["third"], dx=-0.55, dy=4)
fs.mark(ax, VCC, 78.5, "{:.1f}", "%", color=fs.C["vin"], dx=-0.6, dy=-8)
i3 = int(np.argmin(np.abs(EFF["vin_pk"] - 1.0)))
fs.mark(ax, EFF["vp"][i3], EFF["eta"][i3] * 100, "{:.1f}", "%", color=fs.C["vout"], dx=0.35, dy=-7)
fs.axlabels(ax, "负载电压峰值 $V_p$", "V", "效率 η", "%")
ax.set_xlim(0, VCC + 0.1)
ax.set_ylim(0, 85)
ax.legend(loc="upper left", fontsize=8.5)
print(f"[图 43-p1-4] 甲类 V_p=6 V 时 {eta_a[-1]*100:.1f}%；乙类 {eta_b[-1]*100:.1f}%；SPICE 甲乙类 V_p={EFF['vp'][i3]:.2f} V 时 {EFF['eta'][i3]*100:.1f}%")
assert abs(eta_a[-1] - 0.25) < 1e-9 and abs(eta_b[-1] - np.pi / 4) < 1e-9
fs.save(fig, N, "43_p1_4_efficiency.png")


# =============================== page2 ===============================
# ---------- 图 43-p2-1：完整电路（甲乙类 + 推挽在环内） ----------
with drawing(fontsize=11) as d:
    P = amp(d, "AB", "in")
    note(d, (P["xinp"] - 3.4 if "xinp" in P else P["sig"][0] - 1.0, -8.0),
         "$V_{MID}$（中点参考）由 TL072 另一半产生：两只 10 kΩ 把 12 V 分成 6 V，再接成跟随器输出。\n"
         "它只给运放输入定 6 V 的静止点，喇叭电流不走它；喇叭经 $C_o$ 回到真地。")
    lab(d, (P["m"][0] - 0.2, P["m"][1] + 0.45), "m", ha="right", fs_=11, color=fs.C["vin"])
    lab(d, (P["out"][0] + 0.2, P["out"][1] + 0.35), "OUT", fs_=11, color=fs.C["vout"])
    colnote(d, P["zobel"], "Zobel：高频时给 OUT\n一个电阻性负载", "right", ofst=0.5)
print("[图 43-p2-1] 完整电路：增益 3，RF 20 kΩ 接 OUT，基极 22 Ω，Zobel 10 Ω + 100 nF")
save_schem(d, N, "43_p2_1_full_circuit.png")

# ---------- 图 43-p2-2：P_L、P_S、P_D 随 V_p（理想乙类公式 + SPICE 点） ----------
vp = np.linspace(0, VCC, 300)
pl, ps, pd, eta = pb_ideal(vp)
fig, ax = plt.subplots(figsize=(7.4, 4.3))
ax.plot(vp, ps, color=fs.C["bad"], label="电源给出 $P_S$（公式）")
ax.plot(vp, pl, color=fs.C["vout"], label="负载拿到 $P_L$（公式）")
ax.plot(vp, pd, color=fs.C["third"], lw=2.2, label="两管合计发热 $P_D=P_S-P_L$（公式）")
ax.plot(EFF["vp"], EFF["ps"] - EFF["pl"], "s", color=fs.C["third"], ms=4.5, mfc="none", label="两管发热（SPICE，含 $I_q$）")
fs.mark(ax, VP_PD, PD_MAX, "{:.3f}", "W", color=fs.C["third"], dx=0.2, dy=0.3)
ax.axvline(VP_PD, color=fs.C["third"], ls=":", lw=1)
ax.text(VP_PD + 0.08, 0.05, f"$V_p$ = {VP_PD:.2f} V", color=fs.C["third"], fontsize=9)
ax.axvspan(VP_MAX, VCC, color="0.85", alpha=0.6, lw=0)
ax.text((VP_MAX + VCC) / 2, 2.05, "本电路\n到不了", ha="center", fontsize=9, color="0.3")
fs.axlabels(ax, "负载电压峰值 $V_p$", "V", "功率", "W")
ax.set_xlim(0, VCC)
ax.set_ylim(0, 2.6)
ax.legend(loc="upper left", fontsize=8.5)
print(f"[图 43-p2-2] P_D 最大 {PD_MAX:.3f} W @ V_p {VP_PD:.2f} V；V_p=6 V：P_S {ps[-1]:.3f} W，P_L {pl[-1]:.3f} W")
assert abs(ps[-1] - 2 * 36 / (np.pi * 8)) < 1e-9
fs.save(fig, N, "43_p2_2_power_vs_vp.png")

# ---------- 图 43-p2-3：耦合电容的低频角（幅频曲线，对数横轴） ----------
fig, ax = plt.subplots(figsize=(7.2, 4.0))
for nm, col in (("1000u", fs.C["vout"]), ("470u", fs.C["vin"])):
    a = csv(f"ac_{nm}.csv")
    g = a["gain"] / a["gain"].max()
    ax.semilogx(a["f_hz"], 20 * np.log10(g), color=col, label=f"$C_o$ = {nm[:-1]} µF（SPICE）")
    fc = 1 / (2 * np.pi * RL * float(nm[:-1]) * 1e-6)
    ax.plot([fc], [-3.0103], "o", color=col, ms=4, zorder=5)
    ax.annotate(f"{fc:.1f} Hz", (fc, -3.0103), xytext=(-48 if nm == "1000u" else 6, -14 if nm == "1000u" else 6),
                textcoords="offset points", fontsize=9, color=col)
    print(f"[图 43-p2-3] C_o={nm}：f_c = 1/(2π·8 Ω·C) = {fc:.1f} Hz")
fs.ref_h(ax, -3)
fs.axlabels(ax, "频率（对数横轴）", "Hz", "相对增益", "dB")
ax.set_ylim(-20, 2)
ax.legend(loc="lower right", fontsize=9)
fs.save(fig, N, "43_p2_3_cout_lowcut.png")

# ---------- 图 43-p2-4：直流转移：乙类死区 vs 甲乙类（推挽在环外，测试负载 2 kΩ ∥ 2 kΩ） ----------
fig, ax = plt.subplots(figsize=(7.0, 4.2))
DCB, DCAB = csv("dc_B.csv"), csv("dc_AB.csv")
ax.plot(DCB["v_m"] - 6, DCB["v_out"] - 6, color=fs.C["bad"], lw=2, label="乙类（两基极直接接 m）")
ax.plot(DCAB["v_m"] - 6, DCAB["v_out"] - 6, color=fs.C["vout"], lw=2, label="甲乙类（两只 1N4148 垫偏置）")
xx = np.array([-1.5, 1.5])
ax.plot(xx, xx, **fs.LS["good"], label="理想：OUT = m")
s = np.abs(DCB["v_out"] - 6) < 0.01
blo, bhi = (DCB["v_m"][s] - 6).min(), (DCB["v_m"][s] - 6).max()
ax.axvspan(blo, bhi, color=fs.C["bad"], alpha=0.12, lw=0)
ax.text(0, -1.1, f"乙类死区\n{blo:+.2f} ～ {bhi:+.2f} V", ha="center", color=fs.C["bad"], fontsize=9.5)
print(f"[图 43-p2-4] 乙类：OUT 离开 6 V ±10 mV 前 m−6 在 [{blo:.3f}, {bhi:.3f}] V")
assert -0.5 < blo < -0.42 and 0.42 < bhi < 0.5
fs.axlabels(ax, "m − 6 V", "V", "OUT − 6 V", "V")
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.legend(loc="upper left", fontsize=8.5)
# 小插图：测试负载怎么接
ins = ax.inset_axes([0.66, 0.04, 0.33, 0.42])
ins.set_xlim(0, 4); ins.set_ylim(0, 5); ins.axis("off")
ins.add_patch(Rectangle((0, 0), 4, 5, fc="white", ec="0.6", lw=0.8))
ins.plot([1.2, 1.2], [0.5, 4.5], color="k", lw=1.2)
for yy in (3.0, 1.0):
    ins.add_patch(Rectangle((0.95, yy), 0.5, 1.0, fc="#d9c7a3", ec="0.2", lw=0.8, zorder=3))
    ins.text(1.6, yy + 0.5, "2 kΩ", fontsize=7.5, va="center")
ins.text(1.2, 4.6, "+12 V", ha="center", fontsize=7.5, color=fs.C["bad"])
ins.text(1.2, 0.05, "GND", ha="center", fontsize=7.5)
ins.plot([1.2], [2.5], "o", color="k", ms=3)
ins.plot([1.2, 2.2], [2.5, 2.5], color="k", lw=1.2)
ins.text(2.3, 2.5, "OUT", fontsize=7.5, va="center")
ins.text(0.15, 4.0, "测试负载", fontsize=7.5, rotation=90, va="center")
ins.text(2.0, 4.0, "对交流相当于 1 kΩ\n直流把 OUT 拉在 6 V", fontsize=7, va="center", color="0.25")
fs.save(fig, N, "43_p2_4_dc_transfer.png")

# ---------- 图 43-p2-5：乙类放进环内：运放输出 m 在过零时「跳」 ----------
w = csv("w_B_loop.csv")
t = (w["t_s"] - w["t_s"][0]) * 1e3
fig, ax = plt.subplots(figsize=(7.6, 4.0))
ax.plot(t, w["v_m"] - 6, color=fs.C["vin"], label="运放输出 m − 6 V")
ax.plot(t, w["v_ld"], color=fs.C["vout"], lw=2, label="负载电压 $v_L$")
ax.plot(t, 3 * w["v_sig"], **fs.LS["good"], label="理想：3 × 输入")
fs.ref_h(ax, 0)
k = int(np.argmax(w["v_m"]))
fs.mark(ax, t[k], w["v_m"][k] - 6, "{:.2f}", "V", color=fs.C["vin"], dx=0.15, dy=0.2)
print(f"[图 43-p2-5] 乙类环内：m 最高 {w['v_m'].max():.2f} V，负载峰值 {w['v_ld'].max():.3f} V")
assert 9.4 < w["v_m"].max() < 9.8 and 1.95 < w["v_ld"].max() < 2.05
fs.axlabels(ax, "时间", "ms", "电压", "V")
ax.set_ylim(-4, 4.6)
ax.legend(loc="upper right", fontsize=8.5, ncol=3)
fs.save(fig, N, "43_p2_5_loop_jump.png")


# ---------- 图 43-p2-6：恒流源偏置的内部（上 Q3 BD140、下 Q4 BD139） ----------
V_D56, V_EB3 = 1.295, 0.654            # SPICE 工作点（spice/43/ccs_op.cir，run.py「教师复核后补充」）：D5+D6 两端、Q3 发射结
I_EST = (V_D56 - V_EB3) / 27
print(f"[图 43-p2-6] 恒流源：({V_D56} − {V_EB3}) / 27 Ω = {I_EST*1e3:.1f} mA；SPICE {ICCS*1e3:.1f} mA；二极管电流 ≈ (12 − {V_D56}) / 4.7 kΩ = {(12-V_D56)/4.7:.2f} mA")
assert abs(I_EST - 23.7e-3) < 0.1e-3 and ICCS >= 22e-3
with drawing(fontsize=11) as d:
    xq = 0.0
    yT, yG = 7.0, -7.0
    q3 = elm.BjtPnp(circle=True).anchor("base").at((xq, 3.4))
    d += q3
    xe = q3.emitter[0]
    d += elm.Resistor().endpoints((xe, yT), q3.emitter).label("Rx3 27 Ω", loc="bottom", fontsize=10)
    d += elm.Vdd().at((xe, yT)).label("+12 V", fontsize=10)
    d += elm.Line().at((xq - 2.2, yT)).to((xe, yT))
    d += elm.Diode().endpoints((xq - 2.2, yT), (xq - 2.2, 5.2)).label("D5", loc="bottom", fontsize=9)
    d += elm.Diode().endpoints((xq - 2.2, 5.2), (xq - 2.2, 3.4)).label("D6", loc="bottom", fontsize=9)
    d += elm.Line().at((xq - 2.2, 3.4)).to(q3.base)
    d += elm.Dot().at((xq - 2.2, 3.4))
    d += elm.Resistor().endpoints((xq - 2.2, 3.4), (xq - 2.2, 1.2)).label("Rk3\n4.7 kΩ", loc="bottom", fontsize=9)
    d += elm.Ground().at((xq - 2.2, 1.2))
    lab(d, (q3.center[0] + 0.55, q3.center[1]), "Q3\nBD140", fs_=10)
    yb1, yb2 = 1.6, -1.6
    d += elm.Line().at(q3.collector).to((xe, yb1))
    d += elm.Dot().at((xe, yb1))
    d += elm.Diode().endpoints((xe, yb1), (xe, 0)).label("D1", loc="bottom", fontsize=9)
    d += elm.Dot().at((xe, 0))
    d += elm.Diode().endpoints((xe, 0), (xe, yb2)).label("D2", loc="bottom", fontsize=9)
    d += elm.Dot().at((xe, yb2))
    for y, t in ((yb1, "b1 → 22 Ω → Q1 基极"), (0, "m ← 运放输出"), (yb2, "b2 → 22 Ω → Q2 基极")):
        d += elm.Line().at((xe, y)).to((xe + 1.6, y))
        lab(d, (xe + 1.75, y), t, fs_=10)
    q4 = elm.BjtNpn(circle=True).anchor("base").at((xq, -3.4))
    d += q4
    d += elm.Line().at(q4.collector).to((xe, yb2))
    d += elm.Resistor().endpoints(q4.emitter, (xe, yG)).label("Rx4 27 Ω", loc="bottom", fontsize=10)
    d += elm.Ground().at((xe, yG))
    d += elm.Line().at((xq - 2.2, yG)).to((xe, yG))
    d += elm.Diode().endpoints((xq - 2.2, -3.4), (xq - 2.2, -5.2)).label("D7", loc="bottom", fontsize=9)
    d += elm.Diode().endpoints((xq - 2.2, -5.2), (xq - 2.2, yG)).label("D8", loc="bottom", fontsize=9)
    d += elm.Line().at((xq - 2.2, -3.4)).to(q4.base)
    d += elm.Dot().at((xq - 2.2, -3.4))
    d += elm.Resistor().endpoints((xq - 2.2, -1.2), (xq - 2.2, -3.4)).label("Rk4\n4.7 kΩ", loc="bottom", fontsize=9)
    d += elm.Vdd().at((xq - 2.2, -1.2))
    lab(d, (xq - 2.6, -0.9), "+12 V", ha="right", fs_=9)
    lab(d, (q4.center[0] + 0.55, q4.center[1]), "Q4\nBD139", fs_=10)
    lab(d, (xe + 1.9, 4.6), "上恒流源：D5 + D6 把 Q3 基极钉在 +12 V 下面约 1.30 V，\nQ3 的发射结再吃掉约 0.65 V，Rx3 两端约 1.295 − 0.654 ≈ 0.64 V，\n电流 ≈ 0.64 V ÷ 27 Ω ≈ 23.7 mA（SPICE），和 b1 点电压几乎无关", fs_=9.5, color=C["cur"])
    lab(d, (xe + 1.9, -4.6), "下恒流源：镜像。D7 + D8 把 Q4 基极钉在 GND 上面约 1.30 V，\n从 b2 点往下抽约 23.6 mA", fs_=9.5, color=C["cur"])
save_schem(d, N, "43_p2_6_ccs_detail.png")

# =============================== page3 ===============================
# ---------- 图 43-p3-1：偏置失配时 I_q 怎么涨（SPICE） ----------
q = csv("iq.csv")
fig, ax = plt.subplots(figsize=(7.0, 4.0))
x = np.arange(len(q["dv_mV"]))
ax.bar(x - 0.2, q["iq_RE3p3_mA"], 0.4, color=fs.C["vout"], label="$R_E$ = 3.3 Ω（本节）")
ax.bar(x + 0.2, q["iq_RE1_mA"], 0.4, color=fs.C["bad"], label="$R_E$ = 1 Ω")
for i in range(len(x)):
    ax.text(x[i] - 0.2, q["iq_RE3p3_mA"][i] + 1.5, f"{q['iq_RE3p3_mA'][i]:.0f}", ha="center", fontsize=9)
    ax.text(x[i] + 0.2, q["iq_RE1_mA"][i] + 1.5, f"{q['iq_RE1_mA'][i]:.0f}", ha="center", fontsize=9)
ax.axhline(50, color="0.3", ls="--", lw=1)
ax.text(1.6, 53, "50 mA：实验里超过就断电", fontsize=9, color="0.3")
ax.set_xticks(x, [f"{int(v)} mV" for v in q["dv_mV"]])
fs.axlabels(ax, "偏置失配：管子比二极管热，相当于偏置电压多出这么多", None, "静态电流 $I_q$", "mA")
ax.set_ylim(0, 145)
ax.legend(loc="upper left", fontsize=9)
print("[图 43-p3-1] I_q（mA）R_E 3.3 Ω：", list(q["iq_RE3p3_mA"]), "；R_E 1 Ω：", list(q["iq_RE1_mA"]))
assert q["iq_RE3p3_mA"][2] < q["iq_RE1_mA"][2] and q["iq_RE3p3_mA"][2] < 50 and q["iq_RE1_mA"][0] > 50
fs.save(fig, N, "43_p3_1_iq_mismatch.png")

# ---------- 图 43-p3-2：四种接法的 THD（SPICE，1 kHz，V_p ≈ 2 V 那一档输入） ----------
names = [("B_open", "乙类\n环外"), ("AB_open", "甲乙类\n环外"), ("B_loop", "乙类\n环内"), ("AB_loop", "甲乙类\n环内")]
thd = []
for nm, _ in names:
    h = csv(f"h_{nm}.csv")
    thd.append(np.sqrt(sum(h[f"h{k}"][0] ** 2 for k in range(2, 11))))
fig, ax = plt.subplots(figsize=(7.0, 4.0))
bars = ax.bar(range(4), thd, color=[fs.C["bad"], fs.C["third"], fs.C["vin"], fs.C["vout"]])
ax.set_yscale("log")
for i, v in enumerate(thd):
    ax.text(i, v * 1.25, f"{v:.3g}%", ha="center", fontsize=10)
ax.set_xticks(range(4), [n for _, n in names])
fs.axlabels(ax, None, None, "THD（对数纵轴）", "%")
ax.set_ylim(0.003, 80)
print("[图 43-p3-2] THD %：", [f"{v:.4g}" for v in thd])
assert 20 < thd[0] < 22 and 1.6 < thd[1] < 2.0 and 0.06 < thd[2] < 0.08 and 0.007 < thd[3] < 0.010
fs.save(fig, N, "43_p3_2_thd_bars.png")


# ---------- 图 43-p3-3：h_FE 按最坏 25 算：电阻偏置会「饿」，恒流源不会（SPICE） ----------
ST = csv("starve.csv")          # 行：typ_rb470、lowb_rb470、lowb_ccs；列：目标 2 V / 3 V 时的实际 V_p 与运放电流峰值
cases = ["典型 $h_{FE}$\n电阻 470 Ω", "$h_{FE}$ ≈ 25\n电阻 470 Ω", "$h_{FE}$ ≈ 25\n恒流源（本节）"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.0))
x = np.arange(3)
for col, key, lab_ in ((fs.C["vin"], "2", "目标 $V_p$ = 2 V"), (fs.C["vout"], "3", "目标 $V_p$ = 3 V")):
    off = -0.2 if key == "2" else 0.2
    a1.bar(x + off, ST[f"vp_{key}"], 0.4, color=col, label=lab_)
    a2.bar(x + off, ST[f"io_{key}"], 0.4, color=col, label=lab_)
    for i in range(3):
        a1.text(x[i] + off, ST[f"vp_{key}"][i] + 0.06, f"{ST[f'vp_{key}'][i]:.2f}", ha="center", fontsize=9)
        a2.text(x[i] + off, ST[f"io_{key}"][i] + 0.6, f"{ST[f'io_{key}'][i]:.1f}", ha="center", fontsize=9)
for yy in (2, 3):
    a1.axhline(yy, color="0.5", ls=":", lw=1)
a1.set_xticks(x, cases)
a1.set_ylim(0, 3.8)
fs.axlabels(a1, None, None, "实际负载峰值 $V_p$", "V")
a1.set_title("(a) 能推到多大")
a1.legend(loc="upper left", fontsize=8.5)
a2.axhline(26, color=fs.C["bad"], ls="--", lw=1)
a2.text(-0.45, 26.8, "TL072 短路电流典型 26 mA", fontsize=9, color=fs.C["bad"])
a2.set_xticks(x, cases)
a2.set_ylim(0, 32)
fs.axlabels(a2, None, None, "运放输出电流峰值", "mA")
a2.set_title("(b) 运放要出多大力")
fs.save(fig, N, "43_p3_3_bias_starve.png")
print("[图 43-p3-3] V_p@2/3 V：", [f"{v:.3f}" for v in ST["vp_2"]], [f"{v:.3f}" for v in ST["vp_3"]], "；运放 mA：", [f"{v:.1f}" for v in ST["io_2"]], [f"{v:.1f}" for v in ST["io_3"]])
assert ST["vp_2"][1] < 1.8 and ST["vp_3"][2] > 2.8 and ST["io_3"][2] < 15 and ST["io_2"][1] > 19

# ---------- 图 43-p3-4：乙类环内在 10 kHz：过零处残留尖刺 ----------
w = csv("w_B_loop10k.csv")
t = (w["t_s"] - w["t_s"][0]) * 1e6
fig, ax = plt.subplots(figsize=(7.4, 4.0))
ax.plot(t, w["v_ld"] - 3 * w["v_sig"], color=fs.C["bad"], lw=1.6, label="误差 = $v_L$ − 3 × 输入")
ax2 = ax.twinx()
ax2.plot(t, w["v_ld"], color=fs.C["vout"], lw=1, alpha=0.6, label="$v_L$（右轴）")
ax2.set_ylabel("$v_L$（V）")
fs.ref_h(ax, 0)
err = np.abs(w["v_ld"] - 3 * w["v_sig"]).max()
print(f"[图 43-p3-4] 10 kHz 乙类环内：误差最大 {err*1e3:.0f} mV")
fs.axlabels(ax, "时间", "µs", "误差", "V")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8.5)
fs.save(fig, N, "43_p3_4_10k_spike.png")


# =============================== page4 动手实验篇 ===============================
# 面包板画法（与 39 节同一套，复制到本脚本，不改公共模块）
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



# ---------- 实验数值（全部取自 spice/43 的 CSV 和本脚本的公式） ----------
E2 = EFF["vin_pk"] == 0.67
LAB_I, LAB_VP = float(EFF["ps"][E2][0] / VS), float(EFF["vp"][E2][0])
LAB_VRMS = float(np.sqrt(EFF["pl"][E2][0] * RL))
LAB_ETA = float(EFF["eta"][E2][0])
E3 = EFF["vin_pk"] == 1.0
PD_EACH = float((EFF["ps"][E3][0] - EFF["pl"][E3][0]) / 2)
print(f"[数值] 实验：输入 0.67 V 峰值 → V_p {LAB_VP:.2f} V，电流表 {LAB_I*1e3:.1f} mA，负载 {LAB_VRMS:.3f} V rms，η {LAB_ETA*100:.1f}%")
print(f"[数值] 静态：I_q {IQ*1e3:.1f} mA → R_E 上 {IQ*RE*1e3:.0f} mV；50 mA 对应 {0.05*RE*1e3:.0f} mV")
print(f"[数值] 输入 1.0 V 峰值：每管发热 {PD_EACH:.2f} W，不装散热片温升 ≈ {PD_EACH*RTH_JA:.0f} °C；静态每管 {6*IQ:.3f} W → {6*IQ*RTH_JA:.1f} °C")
SPK_VP = 3.0 * 8 / RSPK
print(f"[数值] 试听（8 Ω 喇叭串 10 Ω）：V_p 3.0 V 时喇叭峰值 {SPK_VP:.2f} V，喇叭 {SPK_VP**2/16:.3f} W，10 Ω 上 {(3.0*10/RSPK)**2/20:.3f} W")
assert abs(LAB_I - 0.08254) < 5e-4 and abs(LAB_ETA - 0.2548) < 2e-3 and abs(PD_EACH - 0.44) < 0.01

# ---------- 图 43-p4-1：面包板 ----------
def to126(bb, holes, label, below=False):
    """TO-126 小功率管直接插在面包板上：holes 为三个相邻孔（左→右：E、C、B，以手册引脚图为准）。"""
    (x0, y), (x2, _) = bb.xy(holes[0]), bb.xy(holes[2])
    yb = y - 0.95 if below else y + 0.25
    bb.ax.add_patch(FancyBboxPatch((x0 - 0.4, yb), x2 - x0 + 0.8, 0.7, boxstyle="round,pad=0.03",
                                   fc="#3a3a3a", ec="k", lw=0.8, zorder=6))
    bb.ax.text((x0 + x2) / 2, yb + 0.35, label, color="w", ha="center", va="center", fontsize=6.5, zorder=8)
    for h, t in zip(holes, "ECB"):
        x, yy = bb._hole(h)
        bb.ax.text(x, yy + (0.35 if below else -0.32), t, ha="center", va="center", fontsize=6.5,
                   color="0.1", zorder=8, bbox=dict(fc="#f7f5ef", ec="none", pad=0.1))


WIRE["pos"] = (fs.C["bad"], "+12 V")
WIRE["gnd"] = ("#000000", "GND（真地）")
WIRE["sig"] = (fs.C["vin"], "输入 / 运放输出 m")
WIRE["out"] = (fs.C["vout"], "推挽输出 OUT")
WIRE["fb"] = (fs.C["fb"], "中点参考 / 反馈 / 偏置")
WIRE["jmp"] = (fs.C["third"], "C2 才插的跳线")


def draw_bb(expC=False):
    """图 43-p4-1（expC=False）和图 43-p4-4（实验 C 改线）共用的面包板。"""
    bb = Breadboard(42, "推挽功放：TL072 + 两个恒流源 + BD139 / BD140（功率管连同 D1、D2 装在散热片上，放在板外）" if not expC else
                    "实验 C 改线：反馈改接 m、电位器慢扫输入、测试负载；C2 时再插两根紫色跳线",
                    size=(12.0, 9.6), rails=("+12 V", "GND", "GND", "+12 V"))
    bb.ax.set_xlim(-3.4, 47.0)
    bb.ax.set_ylim(-19.5, 13.8)
    bb.chip(3, "TL072", 8, names={1: "1OUT", 2: "1IN−", 3: "1IN+", 4: "GND", 5: "2IN+", 6: "2IN−", 7: "2OUT", 8: "V+"})
    # 运放 A：中点参考 V_MID
    bb.wire("a3", "T+3", "pos")                         # 8 脚 V+
    bb.wire("j6", "B-6", "gnd")                         # 4 脚 GND
    bb.wire("g3", "g4", "fb")                           # 1 脚接 2 脚：跟随器
    bb.part("j5", "B+5", "", "R")
    bb.note(5, -8.1, "R1\n10 kΩ", ha="center", va="top")
    bb.wire("h5", "h8", "fb", via=[(5, -2.9), (8, -2.9)])
    bb.part("j8", "B-8", "", "R")
    bb.note(8, -8.1, "R2\n10 kΩ", ha="center", va="top")
    bb.part("i8", "i10", "Cd 10 µF", "E", -1)
    bb.wire("j10", "B-10", "gnd")
    bb.wire("h3", "h1", "fb")
    bb.wire("g1", "d1", "fb")                           # V_MID 跨过凹槽到上半区第 1 列
    # 运放 B：增益 3
    bb.part("b1", "b5", "RG 10 kΩ", "R", 1)
    bb.part("c1", "c6", "", "R")
    bb.note(3.5, 3.15, "Rbias 100 kΩ", ha="center", va="center", bbox=dict(fc="#f7f5ef", ec="none", pad=0.3))
    bb.part("a6", "a9", "", "E")
    bb.note(7.5, 6.3, "Cin 10 µF", ha="center")
    bb.wire("a5", "a12", "fb", via=[(5, 6.6), (12, 6.6)])
    bb.part("a12", "a15", "RF 20 kΩ", "R", -1)
    if not expC:
        bb.wire("a15", "a26", "fb", via=[(15, 7.1), (26, 7.1)])
    else:
        bb.wire("a15", "b16", "fb", via=[(15, 7.1), (16.35, 7.1), (16.35, 4.6)])        # 反馈改接 m
    # m：2OUT（7 脚，上半区第 4 列）→ 上半区第 16 列，再跨凹槽接到下半区第 16 列
    bb.wire("d4", "d16", "sig", via=[(4, 2.1), (16, 2.1)])
    bb.wire("e16", "f16", "sig")
    # b1 = 上半区第 17 列；b2 = 下半区第 18 列（上下恒流源的输出经长线接过来）
    # 发射极电阻与 OUT（第 26 列，上下半区用短线连通）
    bb.part("c22", "c26", "RE1 3.3 Ω", "R", 1)
    bb.part("h22", "h26", "RE2 3.3 Ω", "R", -1)
    bb.wire("d26", "g26", "out")
    bb.part("i26", "i29", "Rz 10 Ω", "R", -1)
    bb.part("j29", "B-29", "", "C")
    bb.note(29, -8.1, "Cz\n100 nF", ha="center", va="top")
    bb.part("b26", "b30", "$C_o$ 1000 µF", "E", 1)
    # 上恒流源（上半区第 33～38 列）：Q3 BD140 插在 c33/c34/c35
    to126(bb, ("c33", "c34", "c35"), "Q3 BD140")
    bb.part("T+33", "a33", "", "R")
    bb.note(32.6, 8.15, "Rx3 27 Ω", ha="right", va="center")
    bb.part("a35", "T-35", "", "R")
    bb.note(35.4, 6.6, "Rk3 4.7 kΩ", ha="left", va="center")
    bb.part("d37", "d35", "D6", "D", -1)
    bb.part("T+38", "a38", "", "D")
    bb.note(38.4, 8.0, "D5", ha="left", va="center")
    bb.wire("b38", "b37", "fb")
    bb.wire("e34", "e17", "fb", via=[(34, -0.15), (17, -0.15)])
    # 下恒流源（下半区第 33～38 列）：Q4 BD139 插在 g33/g34/g35
    to126(bb, ("g33", "g34", "g35"), "Q4 BD139", below=True)
    bb.part("j33", "B-33", "", "R")
    bb.note(32.6, -6.05, "Rx4 27 Ω", ha="right", va="center")
    bb.part("j35", "B+35", "", "R")
    bb.note(35.4, -7.15, "Rk4 4.7 kΩ", ha="left", va="center")
    bb.part("i35", "i37", "D7", "D", -1)
    bb.part("j38", "B-38", "", "D")
    bb.note(38.4, -6.0, "D8", ha="left", va="center")
    bb.wire("h37", "h38", "fb")
    bb.wire("f34", "g18", "fb", via=[(34, -1.9), (18, -1.9)])
    # 电源轨：上下两条 +12 V、两条 GND 在右边连通
    bb.wire("T+41", "B+41", "pos", via=[(41.6, 8.6), (41.6, -7.6)])
    bb.wire("T-40", "B-40", "gnd", via=[(40.3, 7.2), (41.2, 7.2), (41.2, -6.2), (40.3, -6.2)])
    # 板外：两只功率管（各装散热片；D1、D2 用导热胶贴在散热片上；22 Ω 焊在基极脚上）、电流表、负载、信号源、电源
    bb.module(12.4, 11.0, 11.4, 2.5, "Q1 BD139 + D1（导热胶贴在同一散热片上）\nRS1 22 Ω 焊在基极脚；D1 阳极接 RS1 另一端 = b1", fc="#e8e8e8")
    bb.wire((17, 11.0), "a17", "fb")
    bb.note(17.2, 10.2, "b1")
    bb.wire((16, 11.0), "a16", "sig")
    bb.note(15.0, 10.2, "D1 阴")
    bb.wire((22, 11.0), "a22", "out")
    bb.note(22.2, 10.2, "E")
    bb.module(26.0, 11.3, 5.0, 1.7, "电流表\n10 A 插孔、直流 A 档", fc="#dff0fb")
    bb.wire((23.8, 12.2), (26.0, 12.2), "pos")
    bb.note(24.0, 12.5, "C")
    bb.wire((31.0, 12.2), "T+31", "pos", via=[(31.6, 12.2), (31.6, 9.6), (31, 9.6)])
    bb.module(12.4, -14.1, 11.4, 2.5, "Q2 BD140 + D2（导热胶贴在另一块散热片上）\nRS2 22 Ω 焊在基极脚；D2 阴极接 RS2 另一端 = b2", fc="#e8e8e8")
    bb.wire((18, -11.6), "j18", "fb")
    bb.note(18.2, -10.9, "b2")
    bb.wire((16, -11.6), "j16", "sig")
    bb.note(15.0, -10.9, "D2 阳")
    bb.wire((22, -11.6), "j22", "out")
    bb.note(22.2, -10.9, "E")
    bb.wire((23.8, -12.8), "B-24", "gnd", via=[(24.6, -12.8), (24.6, -9.4), (24, -9.4)])
    bb.note(23.9, -13.3, "C")
    bb.module(33.0, 11.2, 8.6, 2.4, "负载：8 Ω / 5 W 功率电阻\n（试听：喇叭串 10 Ω / 2 W）", fc="#fdeccf")
    bb.wire("b30", (34.0, 11.2), "out", via=[(30, 10.3), (34.0, 10.3)])
    bb.wire((41.6, 12.4), "T-39", "gnd", via=[(43.6, 12.4), (43.6, 8.15), (39, 8.15)])
    if not expC:
        bb.module(-3.0, 9.6, 8.0, 2.0, "信号源（手机 / 信号发生器）\n先把音量调到 0", fc="#e6f0f8")
        bb.wire((4.0, 9.6), "a9", "sig", via=[(9, 9.6)])
        bb.wire((0.0, 9.6), "T-2", "gnd", via=[(0.0, 8.2), (2, 8.2)])
    else:
        bb.module(-3.0, 9.6, 8.0, 2.0, "信号源：实验 C 拔掉\n（看示波器时才接回 a9）", fc="#eeeeee")
        bb.ax.plot([4.0, 9, 9], [10.6, 10.6, BB_Y["a"]], color=fs.C["vin"], lw=1.8, ls="--", zorder=5)
    bb.module(0.5, -16.2, 9.5, 1.8, "12 V 直流电源（限流 0.5 A）\n或 12 V 适配器 + 1 A 保险丝", fc="#e6f0f8")
    bb.wire((2.5, -14.4), "B+2", "pos")
    bb.wire((8.0, -14.4), "B-3", "gnd", via=[(8.0, -9.0), (3.0, -9.0)])
    if expC:
        # 电位器慢扫输入：+12 V → 4.7 kΩ → 电位器 2 kΩ → 4.7 kΩ → GND；滑动端经 100 Ω 接 inp（上半区第 6 列）
        bb.part("B+12", "j12", "", "R")
        bb.note(11.6, -8.9, "4.7 kΩ", ha="right", va="center")
        bb.ax.add_patch(FancyBboxPatch((11.6, BB_Y["h"] - 0.45), 2.8, 0.9, boxstyle="round,pad=0.05", fc="#bcd3ea", ec="0.2", zorder=6, alpha=0.6))
        for c in (12, 13, 14):                         # 三只脚插在 h12、h13、h14，脚点画在方框上面看得见
            bb._hole(f"h{c}")
            bb.ax.add_patch(Circle(bb.xy(f"h{c}"), 0.17, fc="0.15", ec="none", zorder=8))
        bb.ax.annotate("电位器 2 kΩ：中间脚 h13 = 滑动端", xy=bb.xy("h13"), xytext=(13.3, BB_Y["i"] - 0.15), ha="left", va="top", fontsize=6.5, zorder=9,
                       arrowprops=dict(arrowstyle="-", lw=0.7, color="0.2"), bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.9))
        bb.part("j14", "B-14", "", "R")
        bb.note(14.4, -8.9, "4.7 kΩ", ha="left", va="center")
        bb.part("g11", "g13", "100 Ω", "R", -1)
        bb.wire("f11", "d6", "sig", via=[(11, 3.05), (6, 3.05)])
        bb.note(6.3, 3.35, "滑动端 → inp", color=fs.C["vin"])
        # 测试负载 2 kΩ ∥ 2 kΩ：a26 → +12 V，j26 → GND
        bb.part("a26", "T+25", "", "R")
        bb.note(25.4, 8.15, "2 kΩ", ha="right", va="center")
        bb.part("j26", "B-25", "", "R")
        bb.note(25.4, -6.0, "2 kΩ", ha="right", va="center")
        # C2 才插的两根跳线（紫色），旁边红色 ×
        bb.wire("c16", "c17", "jmp")
        bb.wire("h16", "h18", "jmp")
        for (xx, yy) in ((16.5, BB_Y["c"] + 0.55), (17.0, BB_Y["h"] - 0.55)):
            bb.ax.text(xx, yy, "×", color=fs.C["bad"], fontsize=13, fontweight="bold", ha="center", va="center", zorder=11)
        bbp(bb, "b6", "⑦")
        # C3 才用：反馈线的 b16 一端改插 f26（a26 被测试负载占着；f26 经 g26 的橙线同属 OUT）
        bb.ax.add_patch(Circle(bb.xy("f26"), 0.34, fc="none", ec=fs.C["fb"], lw=1.8, ls="--", zorder=9))
    bbp(bb, "e1", "①")
    bbp(bb, "g16", "②")
    bbp(bb, "b22", "③", edge=fs.C["bad"])
    bbp(bb, "e26", "④")
    bbp(bb, "e33", "⑤")
    bbp(bb, "i33", "⑥", edge=fs.C["bad"])
    if expC:
        bb.note(26.5, -15.2, "实验 C 读数：⑦ inp（b6）和 ④ OUT（e26），黑表笔都接 GND 轨\n"
                "每隔约 50 mV 拧一下电位器，记下 inp 和 OUT；虚线 = 看示波器时才接的信号线\n"
                "紫色线带红 × = C2 才插的跳线：c16–c17 短接 D1，h16–h18 短接 D2\n"
                "绿色虚线圈 f26 = C3 时反馈线 b16 一端改插的孔（a26 被 2 kΩ 占着，f26 经 g26 橙线同属 OUT）\n"
                "改线、插拔跳线之前都先断电", va="center")
    else:
        bb.note(26.5, -15.2, "测量点（黄圈）：①中点参考 $V_{MID}$　②运放输出 m　④推挽输出 OUT——黑表笔都接 GND 轨\n"
                "③量 RE1 两端：红表笔插第 22 列，黑表笔插第 26 列；读数 mV ÷ 3.3 = 静态电流 mA\n"
                "⑤红表笔插上面 +12 V 轨，黑表笔插第 33 列：Rx3 上约 0.64 V，÷ 27 Ω = 上恒流源电流\n"
                "⑥红表笔插第 33 列（下半区），黑表笔插 GND 轨：Rx4 上约 0.64 V，÷ 27 Ω = 下恒流源电流", va="center")
    bb.legend()
    _lg = bb.ax.get_legend(); _lg.set_loc("lower center"); _lg.set_bbox_to_anchor((0.5, 0.0)); _lg.set_ncols(3)
    bb.save(N, "43_p4_4_expC_breadboard.png" if expC else "43_p4_1_breadboard.png")


draw_bb(False)


# ---------- 图 43-p4-2：对照原理图（测量点与面包板列号） ----------
with drawing(fontsize=11) as d:
    P = amp(d, "AB", "in")
    probe(d, P["vm"], "①", dx=-0.2, dy=-0.9)
    probe(d, P["m"], "②", dx=-0.6, dy=-0.9)
    probe(d, (P["xe"], 1.15), "③", dx=1.6, dy=0.3)
    probe(d, P["out"], "④", dx=0.7, dy=0.9)
    colnote(d, P["b1"], "b1 = 上半区第 17 列", "left", ofst=0.3)
    colnote(d, P["m"], "m = 第 16 列", "left", ofst=1.4)
    colnote(d, P["b2"], "b2 = 下半区第 18 列", "left", ofst=0.3)
    colnote(d, (P["xm"], 4.3), "上恒流源：第 33～38 列", "left", ofst=0.3)
    colnote(d, (P["xm"], -4.3), "下恒流源：第 33～38 列", "left", ofst=0.3)
    colnote(d, (P["xc"], -3.0), "负载在板外", "right", ofst=0.4)
    note(d, (P["sig"][0] - 1.0, -8.0),
         "③ = RE1 两端的电压（红表笔接 Q1 发射极那一端）：每 3.3 mV 就是 1 mA 静态电流。\n"
         "⑤⑥ = 两只 27 Ω 上的电压（恒流源内部见原理与实现篇），约 0.64 V 即约 24 mA。\n"
         "$V_{MID}$ 由 TL072 的另一半产生（面包板第 3～5 列下半区），只给运放偏置，不接喇叭。")
print("[图 43-p4-2] 对照原理图：①V_MID ②m ③RE1 两端 ④OUT")
save_schem(d, N, "43_p4_2_schem_lab.png")

# ---------- 图 43-p4-3：没有示波器——直流慢扫的预期读数（推挽在环外，测试负载 2 kΩ ∥ 2 kΩ） ----------
fig, ax = plt.subplots(figsize=(7.0, 4.2))
for D, col, lab_ in ((DCB, fs.C["bad"], "乙类（两基极直接接 m）"), (DCAB, fs.C["vout"], "甲乙类（垫两只 1N4148）")):
    x = D["vx"] - 6
    ax.plot(x, D["v_out"] - 6, color=col, lw=1.6, label=lab_ + "：OUT − 6 V")
    k = np.isclose((x * 1000) % 50, 0, atol=1e-6) | np.isclose((x * 1000) % 50, 50, atol=1e-6)
    ax.plot(x[k], D["v_out"][k] - 6, "o", color=col, ms=4)
ax.plot(DCB["vx"] - 6, DCB["v_m"] - 6, **fs.LS["ref"], label="m − 6 V（两种接法几乎一样）")
s = np.abs(DCB["v_out"] - 6) < 0.01
ilo, ihi = (DCB["vx"][s] - 6).min(), (DCB["vx"][s] - 6).max()
ax.axvspan(ilo, ihi, color=fs.C["bad"], alpha=0.12, lw=0)
ax.text(0, -0.9, f"乙类：inp 在这 {ihi - ilo:.2f} V 里\nOUT 一动不动", ha="center", color=fs.C["bad"], fontsize=9.5)
sa = np.abs(DCAB["v_out"] - 6) < 0.01
print(f"[图 43-p4-3] 输入宽度：乙类 {ihi - ilo:.3f} V，甲乙类 {(DCAB['vx'][sa] - 6).max() - (DCAB['vx'][sa] - 6).min():.3f} V；圆点 = 每 50 mV 读一次")
assert 0.29 < ihi - ilo < 0.33
fs.axlabels(ax, "inp − 6 V（用电位器调）", "V", "读数 − 6 V", "V")
ax.set_xlim(-0.5, 0.5)
ax.set_ylim(-1.5, 1.5)
ax.legend(loc="upper left", fontsize=8.5)
fs.save(fig, N, "43_p4_3_dc_readings.png")
lo_pot, hi_pot = 12 * 4.7 / 11.4, 12 * 6.7 / 11.4
print(f"[数值] 电位器分压范围 {lo_pot:.2f}～{hi_pot:.2f} V")
assert lo_pot < 5.0 and hi_pot > 7.0


# =============================== 教师复核后补充的图 ===============================
# ---------- 图 43-p4-4：实验 C 改线的面包板 ----------
draw_bb(True)

# ---------- 图 43-p4-5：实验 C 的原理图（推挽在环外、电位器慢扫、测试负载、C2 跳线） ----------
with drawing(fontsize=11) as d:
    P = amp(d, "AB", "open", show_meter=False, src="pot")
    xm, yb1, yb2 = P["xm"], P["b1"][1], P["b2"][1]
    for ya, yb_ in ((yb1, 0.0), (0.0, yb2)):      # C2 跳线：从 D1 / D2 左边绕过去
        d += elm.Line().at((xm, ya)).to((xm - 0.55, ya)).color(fs.C["third"]).linestyle("--")
        d += elm.Line().at((xm - 0.55, ya)).to((xm - 0.55, yb_)).color(fs.C["third"]).linestyle("--")
        d += elm.Line().at((xm - 0.55, yb_)).to((xm, yb_)).color(fs.C["third"]).linestyle("--")
        lab(d, (xm - 0.55, (ya + yb_) / 2), "×", ha="center", fs_=14, color=fs.C["bad"])
    lab(d, (xm - 0.7, -3.4), "紫色虚线 = C2 才插的跳线\n（短接 D1、D2 → 乙类）", ha="right", fs_=9, color=fs.C["third"])
    xz, xc = P["zobel"][0], P["xc"]
    xt = xc + 1.9
    d += elm.Line().at((xz, 0)).to((xz, 1.3))
    d += elm.Line().at((xz, 1.3)).to((xt, 1.3))
    d += elm.Dot().at((xt, 1.3))
    d += elm.Resistor().endpoints((xt, 1.3), (xt, 3.7)).label("2 kΩ", loc="bottom", fontsize=9.5)
    d += elm.Vdd().at((xt, 3.7)).label("+12 V", fontsize=9.5)
    d += elm.Resistor().endpoints((xt, -1.1), (xt, 1.3)).label("2 kΩ", loc="bottom", fontsize=9.5)
    d += elm.Ground().at((xt, -1.1))
    lab(d, (xt + 1.1, 2.5), "测试负载：\n对交流相当于 1 kΩ，\n直流把 OUT 拉在 6 V", ha="left", fs_=9, color=C["cur"])
    probe(d, P["inp"], "⑦", dx=-0.2, dy=0.9)
    probe(d, P["out"], "④", dx=0.7, dy=0.9)
    lab(d, (P["rf"][0], P["rf"][1] - 0.9), "RF 改接 m（面包板 b16）", ha="center", fs_=9, color=C["fb"])
    note(d, (P["sig"][0] - 1.5, -8.0),
         "实验 C 的接法：信号源拔掉，电位器分压后经 100 Ω 慢慢推 inp（⑦，面包板 b6）；\n"
         "RF 从 OUT 改接到运放输出 m，推挽级在反馈环外；每一步读 ⑦ 和 ④（OUT），黑表笔接 GND。\n"
         "C1 不插跳线（甲乙类）；C2 断电后插上两根紫色跳线（乙类）；C3 断电，把 RF 的 b16 一端插到 f26（同属 OUT，a26 被测试负载占着）。")
print("[图 43-p4-5] 实验 C 原理图：电位器 4.7 k + 2 k + 4.7 k，100 Ω 到 inp，测试负载 2 kΩ×2，跳线短接 D1、D2")
_lo, _hi = 12 * 4.7 / 11.4, 12 * 6.7 / 11.4
assert abs(_lo - 4.947) < 0.01 and abs(_hi - 7.053) < 0.01
save_schem(d, N, "43_p4_5_expC_schem.png")

# ---------- 图 43-p4-6：功率管模块怎么做（板外，各装一块散热片） ----------
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.8))
for ax, q, dn, cdest, tdest in ((axs[0], "Q1 BD139", "D1", "C（中间脚）→ 电流表 → +12 V", "D1 阴极 → a16（m）"),
                                (axs[1], "Q2 BD140", "D2", "C（中间脚）→ GND 轨", "D2 阳极 → j16（m）")):
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((1.0, 4.2), 5.0, 3.2, fc="#c9ced6", ec="0.3", lw=1.2))          # 散热片
    for k in range(6):
        ax.add_patch(Rectangle((1.2 + 0.8 * k, 7.4), 0.35, 0.5, fc="#c9ced6", ec="0.3", lw=0.8))
    ax.text(3.5, 7.0, f"{q} 的散热片（带电！= 集电极）", ha="center", fontsize=9)
    ax.add_patch(Rectangle((2.2, 4.4), 2.6, 0.25, fc="#f2d27a", ec="0.4", lw=0.8))           # 绝缘垫
    ax.text(4.95, 4.52, "绝缘垫\n（可选）", fontsize=7.5, va="center")
    ax.add_patch(FancyBboxPatch((2.4, 4.65), 2.2, 1.6, boxstyle="round,pad=0.03", fc="#3a3a3a", ec="k"))
    ax.text(3.5, 5.45, q, color="w", ha="center", va="center", fontsize=9)
    for i, (pn, xx) in enumerate(zip("ECB", (2.8, 3.5, 4.2))):
        ax.plot([xx, xx], [4.65, 2.6], color="0.25", lw=2)
        ax.text(xx, 2.35, pn, ha="center", va="top", fontsize=10, fontweight="bold")
    ax.add_patch(Rectangle((4.05, 3.0), 0.3, 0.9, fc="#d9c7a3", ec="0.2"))                   # 22 Ω 焊在 B 脚
    ax.text(4.45, 3.45, "22 Ω 焊在\nB 脚上", fontsize=8, va="center")
    ax.add_patch(FancyBboxPatch((1.4, 5.0), 0.7, 0.35, boxstyle="round,pad=0.02", fc="#f0c27a", ec="0.2"))
    ax.text(1.75, 4.9, dn + "\n（导热胶\n贴牢）", ha="center", va="top", fontsize=7.5)
    ax.text(0.2, 1.4, "E → RE（a22 / j22）\n" + cdest + "\n22 Ω 另一端 + " + dn + " 另一脚 = 基极线（b1 → a17 / b2 → j18）\n" + tdest,
            fontsize=8.3, va="top")
fig.suptitle("功放管模块：管脚从左到右 E、C、B（以手册引脚图为准）；两块散热片绝不能相碰", fontsize=10.5)
print("[图 43-p4-6] 模块：Q1 散热片 = +12 V，Q2 散热片 = GND")
fs.save(fig, N, "43_p4_6_module.png")

# ---------- 图 43-p4-7：实验 D 试听接法（8 Ω 喇叭串 10 Ω） ----------
with drawing(fontsize=11) as d:
    d += elm.Dot(open=True).at((0, 0)).label("OUT（第 26 列）", loc="left", fontsize=10)
    d += elm.Capacitor(polar=True).at((0, 0)).right().length(2.4).label("$C_o$ 1000 µF", loc="top", fontsize=10)
    d += elm.Dot().at((2.4, 0)).label("b30", loc="bottom", fontsize=9)
    d += elm.Resistor().at((2.4, 0)).right().length(2.6).label("10 Ω / 2 W", loc="top", fontsize=10)
    d += elm.Line().at((5.0, 0)).to((6.2, 0))
    d += (sp := elm.Speaker().at((6.2, 0)).right().anchor("in1").label("8 Ω 喇叭", loc="top", fontsize=10))
    d += elm.Line().at(sp.in2).to((sp.in2[0], -2.4))
    d += elm.Line().at((sp.in2[0], -2.4)).to((2.4, -2.4))
    d += elm.Ground().at((2.4, -2.4))
    lab(d, (3.1, -3.0), "GND 轨", fs_=9)
    note(d, (-1.5, -4.2), "原来的 8 Ω 功率电阻换成「10 Ω 串 8 Ω 喇叭」：负载位置共 18 Ω。\n"
         "万用表交流档量 b30 对 GND，先在正常接法下调到约 0.71 V（峰值约 1 V），之后音量旋钮不再动。\n"
         "喇叭上峰值约 0.44 V、约 12 mW，10 Ω 上约 15 mW，喇叭和电阻都很安全。")
print(f"[图 43-p4-7] 试听：负载位置峰值 1 V → 喇叭峰值 {8/RSPK:.3f} V，喇叭 {(8/RSPK)**2/16*1e3:.1f} mW，10 Ω {(10/RSPK)**2/20*1e3:.1f} mW")
assert abs((8 / RSPK) ** 2 / 16 * 1e3 - 12.3) < 0.1 and abs((10 / RSPK) ** 2 / 20 * 1e3 - 15.4) < 0.1
save_schem(d, N, "43_p4_7_listen.png")
