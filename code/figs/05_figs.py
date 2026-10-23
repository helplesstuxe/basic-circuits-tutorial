"""05 精密整流：电路图和静态特性图（时域仿真图由 code/05_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/05_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "05"
VON, RD, RL, A = 0.7, 10.0, 10e3, 1e5     # 折线二极管 0.7 V / 10 Ω；负载 10 kΩ；运放开环增益 10 万（同 P3）
RAIL = 13.5                                # ±15 V 供电时输出最多摆到约 ±13.5 V
K = RL / (RL + RD)                         # 二极管导通电阻和负载的分压


def passive(vi):
    """普通二极管半波整流：输入超过 0.7 V 才有输出。"""
    return np.where(vi > VON, (vi - VON) * K, 0.0)


def precision(vi):
    """基本型精密整流（静态）：返回 (V_o, 运放输出脚电压)。
    二极管导通时 V_oa = A(V_i − V_o)、V_o = K(V_oa − 0.7)，联立得 V_o = K(A·V_i − 0.7)/(1 + K·A)。"""
    vi = np.asarray(vi, dtype=float)
    vo = K * (A * vi - VON) / (1 + K * A)
    on = vo > 0
    vo = np.where(on, vo, 0.0)
    voa = np.where(on, vo / K + VON, np.clip(A * vi, -RAIL, RAIL))
    return vo, voa


# ---------- 图 05-p1-1 普通二极管半波整流 ----------
with drawing() as d:
    d += (src := elm.SourceSin().up().label("$V_i$\n峰值 0.2 V", "left"))
    d += elm.Line().right().length(0.8)
    d += elm.Diode().right().label("硅二极管")
    d += elm.Line().right().length(0.8)
    d += (j := elm.Dot())
    d += elm.Resistor().down().toy(src.start).label("$R_L$ 10 kΩ", "bottom")
    d += elm.Line().left().tox(src.start)
    d += elm.Ground().at(src.start)
    d += elm.Line().right().at(j.center).length(1.0)
    d += elm.Dot(open=True).label("$V_o$ ≈ 0 V", "right")
save_schem(d, N, "05_p1_1_passive.png")

# ---------- 图 05-p1-2 基本型精密整流（超级二极管） ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in2).length(0.8)
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Diode().right().at(op.out).length(2.5).label("二极管", "top")
    d += (j := elm.Dot())
    d += elm.Line().right().length(1.0)
    d += elm.Dot(open=True).label("$V_o$", "right")
    d += elm.Resistor().down().at(j.center).length(2.2).label("$R_L$ 10 kΩ", "bottom")
    d += elm.Ground()
    d += elm.Line().up().at(j.center).length(1.6).color(C["fb"])
    d += elm.Line().left().tox(op.in1.x - 0.8).color(C["fb"]).label("反馈线：从二极管后面取", "top")
    d += elm.Line().down().toy(op.in1).color(C["fb"])
    d += elm.Line().right().tox(op.in1).color(C["fb"])
    d += elm.Dot().at(op.out).label("运放输出脚", "bottom", ofst=0.2)
save_schem(d, N, "05_p1_2_superdiode.png")

# ---------- 图 05-p1-3 小信号整流：普通二极管 vs 精密整流 ----------
t = np.linspace(0, 2e-3, 1000)
vi = 0.2 * np.sin(2 * np.pi * 1e3 * t)
vp = passive(vi)
vo, _ = precision(vi)
print(f"[数值] 峰值 0.2 V：普通二极管输出最大 {vp.max()*1e3:.1f} mV，精密整流输出最大 {vo.max()*1e3:.1f} mV")
assert vp.max() == 0 and abs(vo.max() - 0.2) < 1e-3
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi * 1e3, **fs.LS["vin"], label="输入 $V_i$（峰值 0.2 V）")
ax.plot(t * 1e3, vp * 1e3, **fs.LS["bad"], label="普通二极管整流：一直是 0")
ax.plot(t * 1e3, vo * 1e3, **fs.LS["vout"], label="精密整流 $V_o$：正半周原样通过")
fs.ref_h(ax, 0)
fs.mark(ax, 0.25, vo.max() * 1e3, fmt="{:.0f}", unit=" mV", dx=6, dy=2)
fs.axlabels(ax, "时间", "ms", "电压", "mV")
ax.set_ylim(-260, 330)
ax.legend(loc="upper right", fontsize=8, ncol=1)
fs.save(fig, N, "05_p1_3_compare.png")

# ---------- 图 05-p2-1 传输特性：V_o 和运放输出脚随 V_i 变化 ----------
v = np.linspace(-1, 1, 801)
vo, voa = precision(v)
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a1.plot(v, v.clip(0), **fs.LS["good"], label="理想整流")
a1.plot(v, passive(v), **fs.LS["bad"], label="普通二极管")
a1.plot(v, vo, **fs.LS["vout"], label="精密整流 $V_o$")
fs.ref_v(a1, 0.7, "0.7 V", y=0.35)
fs.axlabels(a1, "输入 $V_i$", "V", "输出 $V_o$", "V")
a1.legend(loc="upper left", fontsize=8)
vo01, voa01 = (float(x) for x in precision(0.1))
err_uV = (0.1 - vo01) * 1e6
print(f"[数值] V_i = 0.1 V：精密整流 V_o = {vo01*1e3:.4f} mV，误差 {err_uV:.1f} µV（= 运放输出脚电压 ÷ A = {voa01/A*1e6:.1f} µV）")
print(f"[数值] V_i = 0.1 V：运放输出脚 {voa01:.3f} V；普通二极管输出 {float(passive(0.1)):.1f} V")
assert abs(err_uV - voa01 / A * 1e6) < 0.1 and err_uV < 10, "误差 = 运放输出脚电压 ÷ 开环增益，只有几微伏"
a2.plot(v, voa, **fs.LS["third"], label="运放输出脚电压")
a2.plot(v, vo, **fs.LS["vout"], label="电路输出 $V_o$")
fs.ref_h(a2, -RAIL, f"负饱和 −{RAIL} V", x=0.98)
fs.mark(a2, 0.1, voa01, fmt="{:.2f}", unit=" V", dx=6, dy=-12)
fs.axlabels(a2, "输入 $V_i$", "V", "电压", "V")
a2.set_ylim(-15, 3)
a2.legend(loc="center right", fontsize=8)
fs.save(fig, N, "05_p2_1_transfer.png")

# ---------- 图 05-p2-3 改进型（反相型）精密半波整流 ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.6)
    d += (j := elm.Dot().label("$V_-$（虚地）", "bottom", ofst=0.15))
    d += elm.Resistor().left().label("$R_1$ 10 kΩ")
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Line().left().at(op.in2).length(0.6)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    # D2：从虚地指向运放输出脚（输入为正时导通，钳住运放输出）
    d += elm.Line().up().at(j.center).length(1.4)
    d += (k := elm.Dot())
    d += elm.Diode().right().tox(op.out.x).label("$D_2$", "top")
    d += elm.Line().down().toy(op.out)
    # D1：从运放输出脚指向输出端（输入为负时导通）
    d += elm.Diode().right().at(op.out).length(2.2).label("$D_1$", "bottom")
    d += (o := elm.Dot())
    d += elm.Line().right().length(0.8)
    d += elm.Dot(open=True).label("$V_o$", "right")
    # R_f：从输出端回到虚地
    d += elm.Line().up().at(k.center).length(1.4)
    d += elm.Resistor().right().tox(o.center.x).label("$R_f$ 10 kΩ")
    d += elm.Line().down().toy(o.center)
    d += elm.Resistor().down().at(o.center).length(2.0).label("$R_L$ 10 kΩ", "bottom")
    d += elm.Ground()
save_schem(d, N, "05_p2_3_improved.png")

print("05_figs OK")
