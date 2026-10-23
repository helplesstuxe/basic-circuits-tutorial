"""03 电压跟随器：全部配图（图 03-p2-2 由 code/03_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/03_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

N = "03"


def follower(d, vin="$V_i$ 输入", vout="$V_o$ 输出", lab_minus=None, lab_plus=None, out_len=1.25):
    """跟随器：输出直接接回反相端。返回 (op, 输入端点, 输出端点)。"""
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    up = elm.Line().up().at(j.center).length(1.6 if lab_minus else 1.2)
    if lab_minus:
        up.label(lab_minus, "bottom", fontsize=11)
    d += up
    d += elm.Line().right().tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    pl = elm.Line().left().at(op.in2).length(3.2 if lab_plus else 1.5)
    if lab_plus:
        pl.label(lab_plus, "bottom", fontsize=11)
    d += pl
    if vin:
        d += elm.Dot(open=True).label(vin, "left")
    pin = d.here
    d += elm.Line().right().at(op.out).length(out_len)
    if vout:
        d += elm.Dot(open=True).label(vout, "right")
    pout = d.here
    return op, pin, pout


def divider(d, top="10 kΩ", bot="10 kΩ", vs="10 V"):
    """从当前位置向左画分压器：返回分压点。"""
    d += elm.Line().left().length(0.8)
    d += (mid := elm.Dot())
    d += elm.Resistor().up().label(top, "bottom")
    d += elm.Vdd().label(vs)
    d += elm.Resistor().down().at(mid.center).label(bot, "bottom")
    d += elm.Ground()
    return mid


# ---------- 图 03-p1-2 跟随器电路 ----------
with drawing() as d:
    follower(d)
save_schem(d, N, "03_p1_2_circuit.png")

# ---------- 图 03-p1-1 分压器直接接负载 ----------
with drawing() as d:
    d += (s := elm.Dot(open=True).label("分压点", "top"))
    d += elm.Line().right().at(s.center).length(1.5)
    d += elm.Resistor().down().label("$R_L$ 1 kΩ\n负载", "bottom")
    d += elm.Ground()
    d.here = s.center
    d += elm.Line().left().length(0.01)
    divider(d)
save_schem(d, N, "03_p1_1_direct.png")

# ---------- 图 03-p1-3 分压器经跟随器接负载 ----------
with drawing() as d:
    op, pin, pout = follower(d, vin=None, vout=None, out_len=0.8)
    d.here = pin
    divider(d)
    d += elm.Resistor().down().at(pout).label("$R_L$ 1 kΩ\n负载", "bottom")
    d += elm.Ground()
save_schem(d, N, "03_p1_3_buffered.png")
print("分压 10 V × 10/(10+10) = 5 V；直接接 1 kΩ 负载只剩 "
      f"{10 * (1e3 * 10e3 / 11e3) / (10e3 + 1e3 * 10e3 / 11e3):.2f} V，经跟随器仍为 5.00 V")

# ---------- 图 03-p2-1 分析图 ----------
with drawing() as d:
    follower(d, lab_minus="$V_- = V_o$（导线直连）", lab_plus="$I \\approx 0$，$V_+ = V_i$")
save_schem(d, N, "03_p2_1_analysis.png")

# ---------- 图 03-p2-3 基准电压缓冲 ----------
with drawing() as d:
    op, pin, pout = follower(d, vin=None, vout=None, out_len=4.4)
    d.here = pin
    d += elm.Line().left().length(0.8)
    d += (mid := elm.Dot())
    d += elm.Resistor().up().label("10 kΩ", "bottom")
    d += elm.Vdd().label("5 V")
    d += elm.Resistor().down().at(mid.center).label("10 kΩ", "bottom")
    d += elm.Ground()
    d += elm.Line().left().at(mid.center).length(1.6)
    d += elm.Capacitor().down().label("100 nF", "top")
    d += elm.Ground()
    for dx, txt in ((1.6, "去 ADC 参考端"), (4.4, "去比较器门限")):
        x = op.out.x + dx
        if dx < 4:
            d += elm.Dot().at((x, op.out.y))
        d += elm.Line().down().at((x, op.out.y)).length(1.0)
        d += elm.Dot(open=True).label(txt, "bottom")
    d += elm.Line().right().at(op.out).length(0.01).label("$V_{ref}$ = 2.5 V", "top", ofst=(2.0, 0.1))
save_schem(d, N, "03_p2_3_vref_buffer.png")

# ---------- 图 03-p3-1 容性负载：振铃与隔离电阻 ----------
wt = 2 * np.pi * 1.2e6                                 # LM358B 增益带宽积 1.2 MHz
Ro, CL = 300.0, 0.1e-6                                 # LM358B 手册：开环输出电阻 RO = 300 Ω（f = 1 MHz、IO = 0）；负载电容 0.1 μF
CLOAD_RATED = 100e-12                                  # LM358B 手册：容性负载驱动能力 100 pF
print(f"负载电容 0.1 μF 是手册容性负载能力 100 pF 的 {CL / CLOAD_RATED:.0f} 倍")
assert round(CL / CLOAD_RATED) == 1000
t = np.linspace(0, 60e-6, 6001)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e6, np.where(t > 0, 1.0, 0.0) * 0.1, **fs.LS["vin"], label="$V_i$ 输入阶跃 0.1 V")
res, settle = {}, {}
for Riso, key, name in ((0.0, "bad", "直接接 0.1 μF"), (10.0, "third", "串 10 Ω"), (33.0, "vout", "串 33 Ω 隔离电阻")):
    T = (Ro + Riso) * CL
    # 负载电压 / 输入 = wt / (T s² + (1 + wt·Riso·CL) s + wt)（单极点运放 + 输出电阻 + 隔离电阻 + 电容）
    _, y = signal.step(([wt], [T, 1 + wt * Riso * CL, wt]), T=t)
    y = 0.1 * y
    k = np.argmax(y)
    os_pct = (y[k] / 0.1 - 1) * 100
    res[Riso] = os_pct
    out = np.abs(y - 0.1) > 0.002                      # 偏离 0.1 V 超过 2%
    settle[Riso] = t[np.nonzero(out)[0][-1]] if out[-1] == False else np.inf
    ax.plot(t * 1e6, y, **fs.LS[key], label=f"负载电压：{name}")
    if Riso != 10.0:
        fs.mark(ax, t[k] * 1e6, y[k], fmt="{:.3f}", unit=" V", dx=6, dy=4)
    print(f"{name}：最高 {y[k]:.3f} V，过冲 {os_pct:.1f}%，进入 ±2% 的时间 {settle[Riso] * 1e6:.1f} μs")
assert res[0.0] > 80 and 30 < res[10.0] < 50 and res[33.0] < 2
assert settle[0.0] == np.inf and settle[33.0] < 10e-6   # 直接接电容：60 μs 内都没稳住；33 Ω：10 μs 内稳住
print(f"1 mA 负载电流在 33 Ω 上的压降：{1e-3 * 33 * 1e3:.0f} mV")
fs.ref_h(ax, 0.1, "0.1 V")
fs.axlabels(ax, "时间", "μs", "电压", "V"); ax.legend(loc="upper right", fontsize=8, ncol=2)
ax.set_ylim(-0.01, 0.27)
fs.save(fig, N, "03_p3_1_cap_load.png")

# ---------- 图 03-p3-2 单电源 5 V 跟随器：两头都到不了 ----------
vin = np.linspace(0, 5, 501)
V_HI, V_LO = 5.0 - 1.5, 0.02                           # LM358B：输出最高约 V+ − 1.5 V；最低按 SPICE（TI 模型 0.024 V）取约 0.02 V（第 7 轮由 0.1 V 更正）
vout = np.clip(vin, V_LO, V_HI)
print(f"单电源 5 V 跟随器：输出范围 {V_LO} V ～ {V_HI} V")
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(vin, vin, **fs.LS["good"], label="理想 $V_o = V_i$")
ax.plot(vin, vout, **fs.LS["vout"], label="实际 $V_o$")
fs.ref_h(ax, V_HI, f"{V_HI} V", x=0.02, ha="left")
fs.ref_h(ax, V_LO, f"{V_LO} V", x=0.6, ha="left")
fs.mark(ax, V_HI, V_HI, fmt="{:.1f}", unit=" V", dx=6, dy=-14)
assert vout.max() == 3.5 and vout.min() == 0.02
fs.axlabels(ax, "输入 $V_i$", "V", "输出 $V_o$", "V"); ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "03_p3_2_single_supply.png")

# ---------- 正文与练习里的其余数字（只打印 + 断言） ----------
# 压摆率：不用求导，直接数值算正弦相邻两点的斜率，找最大值，和 2πfVp 对比
f, Vp = 1e3, 1.0
tt = np.linspace(0, 1 / f, 100001)
vv = Vp * np.sin(2 * np.pi * f * tt)
slope = np.max(np.abs(np.diff(vv) / np.diff(tt)))
print(f"1 kHz、峰值 1 V 正弦：数值最大斜率 {slope:.1f} V/s，2πfVp = {2*np.pi*f*Vp:.1f} V/s，平均斜率 4fVp = {4*f*Vp:.0f} V/s")
assert abs(slope / (2 * np.pi * f * Vp) - 1) < 1e-3
print(f"最大斜率 / 平均斜率 = {slope/(4*f*Vp):.3f}（π/2 = {np.pi/2:.3f}）")
# 分压器内阻：两只 10 kΩ 并联 5 kΩ，接 1 kΩ 负载
print(f"5 V × 1/(5+1) = {5*1/(5+1):.2f} V")
assert abs(5 / 6 - 0.83) < 0.01
# 诊断练习：隔离电阻 33 Ω、负载 0.5 mA 的压降
print(f"33 Ω × 0.5 mA = {33*0.5e-3*1e3:.1f} mV")
assert abs(33 * 0.5e-3 - 0.0165) < 1e-9
