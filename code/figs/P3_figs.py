"""P3 运放入门：全部配图（电路图用 schemdraw，曲线用 matplotlib）。
运行：/workspace/circuits-venv/bin/python code/figs/P3_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。（图 P3-p2-2 由 code/P3_sim.py 生成）
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403  drawing、save_schem、elm，以及 figstyle 的全部工具
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "P3"

# ---------- 运放的「实际」参数（典型值，取自 TI LM358B 数据手册 SLOS068AB 的数量级）----------
A_OL = 1e5          # 开环增益：10 万倍（LM358B 典型 140 V/mV，这里取整数好算）
VCC, VEE = 15.0, -15.0
DROP = 1.5          # 输出离电源轨还差约 1.5 V（LM358B 正轨典型 1.35~1.5 V）
VOH, VOL = VCC - DROP, VEE + DROP


def opamp_out(vd, vcc=VCC, vee=VEE, drop=DROP, a=A_OL):
    """开环运放：V_o = A·(V+ − V-)，但被限制在 [V_EE + drop, V_CC − drop] 之间。"""
    return np.clip(a * vd, vee + drop, vcc - drop)


# ---------- 图 P3-p1-1 运放符号与五个引脚 ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.8)
    d += elm.Dot(open=True).label("反相输入端 $V_-$", "left")
    d += elm.Line().left().at(op.in2).length(0.8)
    d += elm.Dot(open=True).label("同相输入端 $V_+$", "left")
    d += elm.Line().right().at(op.out).length(0.8)
    d += elm.Dot(open=True).label("输出 $V_o$", "right")
    d += elm.Line().up().at(op.vd).length(0.8)
    d += elm.Vdd().label("$V_{CC}$ 正电源（如 +15 V）", "right")
    d += elm.Line().down().at(op.vs).length(0.8)
    d += elm.Vss().label("$V_{EE}$ 负电源（如 −15 V）", "right")
save_schem(d, N, "P3_p1_1_symbol.png")

# ---------- 图 P3-p1-2 开环传输特性：差一点点就顶到头 ----------
vd = np.linspace(-400e-6, 400e-6, 801)          # 两输入端电压差 V+ − V-：±400 μV
vo = opamp_out(vd)
lin = VOH / A_OL                                 # 线性区半宽：13.5 V / 10 万 = 135 μV
print(f"开环增益 A = {A_OL:.0f}，输出上限 {VOH} V、下限 {VOL} V，线性区 ±{lin*1e6:.0f} μV")
assert abs(lin - 135e-6) < 1e-9
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(vd * 1e6, vo, **fs.LS["vout"], label="$V_o$ 输出（A = 10 万）")
fs.ref_h(ax, VOH, f"上限 {VOH} V", x=0.02, ha="left"); fs.ref_h(ax, VOL, f"下限 {VOL} V", x=0.98)
fs.ref_v(ax, lin * 1e6, f"+{lin*1e6:.0f} μV", y=0.5); fs.ref_v(ax, -lin * 1e6, f"−{lin*1e6:.0f} μV", y=0.5)
fs.mark(ax, 50, opamp_out(50e-6), fmt="{:.1f}", unit=" V", dx=6, dy=-4)    # 差 50 μV 时输出 5 V
fs.axlabels(ax, "两输入端电压差 $V_+ - V_-$", "μV", "输出电压", "V")
ax.set_ylim(-16, 16); ax.legend(loc="center left")
assert abs(opamp_out(50e-6) - 5.0) < 1e-9
fs.save(fig, N, "P3_p1_2_openloop.png")

# ---------- 图 P3-p1-3 负反馈环路方框图 ----------
fig, ax = fs.diagram(9, 3.0)
b_in = fs.box(ax, 0.8, 2.0, "输入 $V_i$", w=1.3)
cmp_ = fs.box(ax, 3.0, 2.0, "比较\n$V_+ - V_-$", w=1.5, h=0.8)
amp = fs.box(ax, 5.3, 2.0, "放大 ×A\n（A ≈ 10 万）", w=1.7, h=0.8, fc=fs.C["fill2"])
b_out = fs.box(ax, 7.9, 2.0, "输出 $V_o$", w=1.3)
fb = fs.box(ax, 5.3, 0.6, "反馈网络（电阻分压）\n送回一部分 $V_o$", w=2.8, h=0.75)
fs.arrow(ax, b_in["r"], cmp_["l"], "接 $V_+$")
fs.arrow(ax, cmp_["r"], amp["l"])
fs.arrow(ax, amp["r"], b_out["l"])
fs.arrow(ax, (7.9, 1.7), (7.9, 0.6), color=fs.C["fb"])
fs.arrow(ax, (7.9, 0.6), fb["r"], color=fs.C["fb"])
fs.arrow(ax, fb["l"], (3.0, 0.6), color=fs.C["fb"])
fs.arrow(ax, (3.0, 0.6), cmp_["b"], color=fs.C["fb"])
ax.text(2.55, 1.05, "接 $V_-$\n（负反馈）", fontsize=9, color=fs.C["fb"], ha="right")
fs.save(fig, N, "P3_p1_3_feedback_loop.png")

# ---------- 图 P3-p2-1 用来推导的电路：反相放大（A 有限） ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True).label("A", "center", fontsize=12))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot().label("$V_-$", "bottom", ofst=0.15))
    d += elm.Resistor().left().label("$R_1$ 10 kΩ").label("$I_1 \\rightarrow$", "bottom")
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Line().up().at(j.center).length(1.5)
    d += elm.Resistor().right().label("$R_f$ 100 kΩ").label("$I_f \\rightarrow$", "bottom").tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(0.5)
    d += elm.Line().down().length(0.5)
    d += elm.Ground().label("$V_+$ = 0 V", "right")
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$", "right")
save_schem(d, N, "P3_p2_1_inverting_finiteA.png")

# ---------- 图 P3-p2-3 有负反馈 vs 没有负反馈 ----------
t = np.linspace(0, 2e-3, 2001)
vi = fs.sine(t, 1e3, amp=0.5)
v_closed = -(100e3 / 10e3) * vi                       # 负反馈：-10 倍，干干净净
v_open = opamp_out(vi - 0.0)                           # 不加反馈：输入接 V+，V- 接地
print(f"闭环输出峰值 {v_closed.max():.2f} V；开环输出在 {v_open.min()} V 与 {v_open.max()} V 之间来回跳")
assert abs(v_closed.max() - 5.0) < 1e-3 and v_open.max() == VOH and v_open.min() == VOL
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi, **fs.LS["vin"], label="$V_i$ 输入（峰值 0.5 V）")
ax.plot(t * 1e3, v_closed, **fs.LS["vout"], label="$V_o$ 有负反馈（−10 倍）")
ax.plot(t * 1e3, v_open, **{**fs.LS["bad"], "markevery": 0.05}, label="$V_o$ 没有反馈（开环）")
fs.ref_h(ax, 0, "0 V")
fs.mark(ax, 0.75, v_closed[750], fmt="{:.1f}", unit=" V", dx=6, dy=-2)
fs.mark(ax, 0.25, v_open[250], fmt="{:.1f}", unit=" V", dx=6, dy=-12)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-16, 16)
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1))
fs.save(fig, N, "P3_p2_3_open_vs_closed.png")

# ---------- 图 P3-p3-1 电源电压决定输出能摆多远 ----------
vi = fs.sine(t, 1e3, amp=0.8)
ideal = -10 * vi                                       # 理想：峰值 8 V
cases = [("±15 V 双电源", 15, -15, "vout"), ("±5 V 双电源", 5, -5, "third"), ("5 V 单电源", 5, 0, "bad")]
UP, DN = 1.5, 0.1                                      # LM358B：输出最高离正电源约 1.5 V，最低离负电源约 0.1 V
# 三种电源拆成上下三个子图，避免单电源曲线把 ±5 V 的削顶段盖住
fig, axs = plt.subplots(3, 1, figsize=(7, 6.2), sharex=True)
for ax, (lab, vcc, vee, key) in zip(axs, cases):
    lo, hi = vee + DN, vcc - UP
    v = np.clip(ideal, lo, hi)
    style = {**fs.LS[key], "markevery": 0.05} if key == "bad" else fs.LS[key]
    ax.plot(t * 1e3, ideal, **fs.LS["good"], zorder=5, label="理想 $V_o$ = −10 $V_i$")
    ax.plot(t * 1e3, v, **style, label=f"{lab}：{lo:g} ~ {hi:g} V")
    print(f"{lab}: 输出范围 {lo:g} V ~ {hi:g} V，实际峰值 {v.max():.2f} V / 谷值 {v.min():.2f} V")
    fs.ref_h(ax, 0, "0 V")
    fs.axlabels(ax, "时间" if ax is axs[-1] else None, "ms" if ax is axs[-1] else None, "电压", "V")
    ax.set_ylim(-9.5, 9.5); ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8)
assert np.clip(ideal, -14.9, 13.5).max() == ideal.max() and np.clip(ideal, -14.9, 13.5).min() == ideal.min()  # ±15 V 时 ±8 V 不削顶
fs.save(fig, N, "P3_p3_1_supply_clip.png")

# ---------- 图 P3-p3-2 开环增益不够时的增益误差 ----------
A = np.logspace(3, 7, 200)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
for G, key in ((1, "vout"), (10, "third"), (100, "fb")):
    err = 100 * (1 - 1 / (1 + (1 + G) / A))            # 反相放大：实际倍数比理想倍数小了百分之几
    ax.loglog(A, err, **fs.LS[key], label=f"目标倍数 {G}")
    e = 100 * (1 - 1 / (1 + (1 + G) / 1.4e5))
    fs.mark(ax, 1.4e5, e, fmt="{:.2g}", unit=" %", dx=6, dy=2)   # 统一保留两位有效数字：0.0014 / 0.0079 / 0.072
    print(f"目标倍数 {G}：A = 14 万时误差 {e:.2g} %")
fs.ref_v(ax, 1.4e5, "LM358B 典型 A = 14 万", y=0.98)
e100 = 100 * (1 - 1 / (1 + 101 / 1.4e5))
assert 0.07 < e100 < 0.075                              # 目标 100 倍时误差约 0.072 %
assert f"{100 * (1 - 1 / (1 + 2 / 1.4e5)):.2g}" == "0.0014"   # 目标 1 倍：2/140000 ≈ 0.0014 %
assert f"{100 * (1 - 1 / (1 + 11 / 1.4e5)):.2g}" == "0.0079"  # 目标 10 倍：11/140000 ≈ 0.0079 %
fs.axlabels(ax, "开环增益 A", None, "增益误差", "%"); ax.legend(loc="lower left")
fs.save(fig, N, "P3_p3_2_gain_error.png")
