"""06 桥式整流：电路图和运放全波整流的静态特性（桥式整流的时域仿真图由 code/06_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/06_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "06"
VON, A = 0.7, 1e5          # 二极管 0.7 V（同 P2）；运放开环增益 10 万（同 P3、05）
R = 10e3                   # 运放全波整流里的电阻 R


def diamond(d, x0=0.0, y0=0.0, s=2.2):
    """画二极管桥：上顶点 a、下顶点 b 接交流，右顶点是输出 +，左顶点是输出 −。返回四个顶点坐标。"""
    a, p, b, n = (x0, y0 + s), (x0 + s, y0), (x0, y0 - s), (x0 - s, y0)
    d += elm.Diode().at(a).to(p).label("$D_1$", "top")
    d += elm.Diode().at(b).to(p).label("$D_2$", "bottom")
    d += elm.Diode().at(n).to(a).label("$D_3$", "top")
    d += elm.Diode().at(n).to(b).label("$D_4$", "bottom")
    for q in (a, p, b, n):
        d += elm.Dot().at(q)
    return a, p, b, n


# ---------- 图 06-p1-1 二极管桥 ----------
with drawing() as d:
    a, p, b, n = diamond(d)
    d += elm.Label().at((a[0] + 0.35, a[1] + 0.3)).label("a", fontsize=11)
    d += elm.Label().at((b[0] + 0.35, b[1] - 0.3)).label("b", fontsize=11)
    d += elm.Line().at(a).left().length(4.2)
    d += (src := elm.SourceSin().down().toy(b[1]).label("交流输入\n（低压）", "left"))
    d += elm.Line().right().tox(b[0])
    d += elm.Line().at(p).right().length(2.0)
    d += (j := elm.Dot())
    d += elm.Resistor().down().length(3.4).label("$R_L$", "bottom")
    d += elm.Line().left().tox(n[0])
    # 这根竖线要穿过交流源到 b 的水平线（y = b[1]），两线不相连：画一个跨线小弧
    d += elm.Line().up().toy(b[1] - 0.3)
    d += elm.Arc2(k=0.9).to((n[0], b[1] + 0.3))
    d += elm.Line().up().toy(n[1])
    d += elm.Line().at(j.center).right().length(1.0)
    d += elm.Dot(open=True).label("$V_o$ +", "right")
    d += elm.Label().at((n[0] - 0.5, n[1])).label("−", fontsize=13)
    d += elm.Label().at((p[0] + 0.4, p[1] + 0.35)).label("+", fontsize=13)
save_schem(d, N, "06_p1_1_bridge.png")

# ---------- 图 06-p2-1 完整的整流滤波电源（变压器初级接市电） ----------
with drawing() as d:
    d += (tr := elm.Transformer(t1=4, t2=4).label("变压器\n220 V → 12 V", "top", ofst=0.6))
    d += elm.Fuse().left().at(tr.p1).length(3.0).label("保险丝", "top")
    d += elm.Dot(open=True).label("L", "left")
    d += elm.Line().at(tr.p2).left().length(3.0)
    d += elm.Dot(open=True).label("N", "left")
    d += elm.Label().at((tr.p1[0] - 2.2, (tr.p1[1] + tr.p2[1]) / 2)).label("市电\n220 V 50 Hz", fontsize=11, color=C["bad"])
    a, p, b, n = diamond(d, x0=tr.s1[0] + 3.6, y0=(tr.s1[1] + tr.s2[1]) / 2, s=1.8)
    d += elm.Line().at(tr.s1).right().length(0.8)
    d += elm.Line().up().toy(a[1] + 0.6)
    d += elm.Line().right().tox(a[0])
    d += elm.Line().down().toy(a[1])
    d += elm.Line().at(tr.s2).right().length(0.8)
    d += elm.Line().down().toy(b[1] - 0.6)
    d += elm.Line().right().tox(b[0])
    d += elm.Line().up().toy(b[1])
    d += elm.Line().at(p).right().length(1.5)
    d += (j1 := elm.Dot())
    d += elm.Line().right().length(2.2)
    d += (j2 := elm.Dot())
    d += elm.Line().right().length(1.0)
    d += elm.Dot(open=True).label("$V_o$ +", "right")
    d += elm.Capacitor(polar=True).down().at(j1.center).length(3.2).label("C\n2200 µF\n25 V", "bottom")
    d += elm.Line().left().tox(n[0])
    d += elm.Line().up().toy(n[1])
    d += elm.Resistor().down().at(j2.center).length(3.2).label("$R_L$\n75 Ω", "bottom")
    d += elm.Line().left().tox(j1.center.x)
    d += elm.Label().at((n[0] - 0.45, n[1])).label("−", fontsize=13)
save_schem(d, N, "06_p2_1_supply.png")

# ---------- 图 06-p2-3 运放全波整流（精密半波整流 + 加权加法器） ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True).label("A1", "center", fontsize=10))
    d += elm.Line().left().at(op.in1).length(0.6)
    d += (j := elm.Dot())
    d += elm.Resistor().left().label("R")
    d += (vin := elm.Dot(open=True).label("$V_i$", "left"))
    d += elm.Line().left().at(op.in2).length(0.6)
    d += elm.Line().down().length(0.4)
    d += elm.Ground()
    d += elm.Line().up().at(j.center).length(1.4)
    d += (k := elm.Dot())
    d += elm.Diode().right().tox(op.out.x).reverse().label("$D_2$", "top")
    d += elm.Line().down().toy(op.out)
    d += elm.Diode().right().at(op.out).length(2.2).reverse().label("$D_1$", "bottom")
    d += (o := elm.Dot().label("$V_h$", "bottom", ofst=0.15))
    d += elm.Line().up().at(k.center).length(1.4)
    d += elm.Resistor().right().tox(o.center.x).label("R")
    d += elm.Line().down().toy(o.center)
    # 第二级：加权加法器
    d += elm.Resistor().right().at(o.center).label("R/2", "top")
    d += (s := elm.Dot())
    d += elm.Line().right().length(1.4)
    d += (op2 := elm.Opamp(leads=True, anchor="in1").label("A2", "center", fontsize=10))
    d += elm.Line().left().at(op2.in2).length(0.3)
    d += elm.Line().down().length(0.3)
    d += elm.Ground()
    d += elm.Line().up().at(s.center).length(2.8)
    d += elm.Resistor().right().tox(op2.out.x + 0.3).label("R")
    d += elm.Line().down().toy(op2.out)
    d += elm.Line().left().tox(op2.out.x)
    d += elm.Line().right().at(op2.out).length(1.2)
    d += elm.Dot(open=True).label("$V_o$", "right")
    # 原始输入 V_i 直接送一路到加法器
    d += elm.Line().down().at(vin.center).length(3.2)
    d += elm.Line().right().tox(s.center.x - 2.0)
    d += elm.Resistor().right().tox(s.center.x).label("R", "bottom")
    d += elm.Line().up().toy(s.center)
save_schem(d, N, "06_p2_3_opamp_fullwave.png")


# ---------- 图 06-p2-4 运放全波整流 vs 二极管桥：小信号 ----------
def halfwave(vi):
    """第一级（二极管调头的反相精密半波整流，静态模型）：返回 (V_h, A1 输出脚电压)。
    V_i > 0：D1 导通，反相放大，V_h = −V_i / (1 + 2/A)；V_i < 0：D2 导通，A1 输出脚被钳在 +0.7 V，V_h = 0。"""
    vi = np.asarray(vi, dtype=float)
    vh = np.where(vi > 0, -vi / (1 + 2 / A), 0.0)
    pin = np.where(vi > 0, vh - VON, VON)
    return vh, pin


def fullwave(vi):
    """第二级加权加法器（有限增益 A）：V_o = −(V_i + 2·V_h) / (1 + 噪声增益/A)，噪声增益 = 1 + R/(R ∥ R/2) = 4。"""
    vh, _ = halfwave(vi)
    return -(vi + 2 * vh) / (1 + 4 / A)


def bridge_static(vi):
    """普通二极管桥（静态，不计内阻）：|V_i| 超过两个二极管压降才有输出。"""
    return np.clip(np.abs(vi) - 2 * VON, 0, None)


t = np.linspace(0, 2e-3, 1000)
vi = 0.5 * np.sin(2 * np.pi * 1e3 * t)
vh, _ = halfwave(vi)
vo = fullwave(vi)
vb = bridge_static(vi)
err = np.abs(vo - np.abs(vi)).max()
avg = vo.mean()
print(f"[数值] 峰值 0.5 V：运放全波整流输出最大 {vo.max()*1e3:.1f} mV，与 |V_i| 的最大误差 {err*1e6:.0f} µV；平均值 {avg*1e3:.1f} mV（理论 2/π × 0.5 V = {2/np.pi*0.5*1e3:.1f} mV）")
print(f"[数值] 普通二极管桥输出最大 {vb.max():.1f} V")
assert vb.max() == 0 and err < 50e-6 and abs(avg - 2 / np.pi * 0.5) < 2e-3
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a1.plot(t * 1e3, vi, **fs.LS["vin"], label="输入 $V_i$")
a1.plot(t * 1e3, vh, **fs.LS["third"], label="第一级 $V_h$")
a1.plot(t * 1e3, vo, **fs.LS["vout"], label="输出 $V_o$")
a1.plot(t * 1e3, vb, **fs.LS["bad"], label="二极管桥：0")
fs.ref_h(a1, 0)
fs.axlabels(a1, "时间", "ms", "电压", "V")
a1.set_ylim(-0.7, 1.0)
a1.legend(loc="upper right", fontsize=7.5, ncol=2)
v = np.linspace(-2.5, 2.5, 1001)
a2.plot(v, np.abs(v), **fs.LS["good"], label="理想 $|V_i|$")
a2.plot(v, fullwave(v), **fs.LS["vout"], label="运放全波整流")
a2.plot(v, bridge_static(v), **fs.LS["bad"], label="二极管桥")
fs.ref_v(a2, 1.4, "1.4 V", y=0.85)
fs.ref_v(a2, -1.4, "−1.4 V", y=0.85)
print("[数值] 二极管桥死区 ±1.4 V")
fs.axlabels(a2, "输入 $V_i$", "V", "输出", "V")
a2.legend(loc="upper center", fontsize=8)
a2.set_ylim(-0.2, 3.2)
fs.save(fig, N, "06_p2_4_opamp_fullwave_sim.png")

# 第一级输出脚电压（正文用）
for x in (0.3, -0.3):
    h, pin = (float(q) for q in halfwave(x))
    print(f"[数值] V_i = {x:+.1f} V：V_h = {h:+.3f} V，A1 输出脚 {pin:+.2f} V，V_o = {float(fullwave(x)):+.4f} V")

print("06_figs OK")
