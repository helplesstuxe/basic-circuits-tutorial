"""15 有源滤波：全部配图（图 15-p2-2 由 code/15_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/15_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

N = "15"
R, C = 16e3, 10e-9                                     # 一阶：fc ≈ 995 Hz
R1, R2, C1, C2 = 4.22e3, 18.4e3, 10e-9, 33e-9          # Sallen-Key 巴特沃斯 1 kHz（TI SLOA049 表 10-1）
first = ([1.0], [R * C, 1.0])                          # 一阶低通：1/(sRC + 1)
sk = ([1.0], [R1 * R2 * C1 * C2, C1 * (R1 + R2), 1.0])  # Sallen-Key：1/(s²R1R2C1C2 + sC1(R1+R2) + 1)


def follower_tail(d, node, out_len=1.0):
    """从 node 引线到运放同相端，运放接成跟随器，返回运放。"""
    d += elm.Line().right().at(node).length(1.0)
    d += (op := elm.Opamp(leads=True).right().anchor("in2"))
    d += elm.Line().left().at(op.in1).length(0.4)
    d += elm.Line().up().length(1.2)
    d += elm.Line().right().tox(op.out.x + 0.4)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().right().at(op.out).length(out_len)
    d += elm.Dot(open=True).label("$V_o$", "right")
    return op


# ---------- 图 15-p1-1 带高频噪声的信号经过低通 ----------
t = np.linspace(0, 40e-3, 40001)
clean = fs.sine(t, 50, amp=1.0)
noisy = clean + 0.3 * np.sin(2 * np.pi * 10e3 * t)
_, y, _ = signal.lsim(first, noisy, t)
ripple = np.max(np.abs(y[20000:] - signal.lsim(first, clean, t)[1][20000:]))
print(f"输入：50 Hz 1 V 信号 + 10 kHz 0.3 V 噪声；经 fc ≈ 995 Hz 一阶低通后噪声剩约 {ripple:.2f} V")
assert ripple < 0.04
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, noisy, **{**fs.LS["vin"], "lw": 0.8}, label="$V_i$ 输入（带 10 kHz 噪声）")
ax.plot(t * 1e3, y, **fs.LS["vout"], label="$V_o$ 低通输出")
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-1.8, 2.2)
ax.legend(loc="upper right", fontsize=8, ncol=2)
fs.save(fig, N, "15_p1_1_denoise.png")

# ---------- 图 15-p1-2 一阶有源低通 ----------
with drawing() as d:
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R$ 16 kΩ")
    d += (n := elm.Dot())
    d += elm.Capacitor().down().label("$C$ 10 nF", "bottom")
    d += elm.Ground()
    follower_tail(d, n.center)
save_schem(d, N, "15_p1_2_first_order.png")
print(f"一阶低通 fc = 1/(2π × 16 kΩ × 10 nF) = {1 / (2 * np.pi * R * C):.0f} Hz")

# ---------- 图 15-p2-1 Sallen-Key 二阶低通 ----------
with drawing() as d:
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R_1$ 4.22 kΩ")
    d += (a := elm.Dot())
    d += elm.Resistor().right().label("$R_2$ 18.4 kΩ")
    d += (b := elm.Dot())
    d += elm.Capacitor().down().label("$C_1$ 10 nF", "bottom")
    d += elm.Ground()
    op = follower_tail(d, b.center, out_len=2.4)
    d += elm.Line().up().at(a.center).length(3.6)
    d += elm.Capacitor().right().label("$C_2$ 33 nF").tox(op.out.x + 1.4)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
save_schem(d, N, "15_p2_1_sallen_key.png")
f0 = 1 / (2 * np.pi * np.sqrt(R1 * R2 * C1 * C2))
Q = np.sqrt(R1 * R2 * C1 * C2) / (C1 * (R1 + R2))
print(f"Sallen-Key：f0 = {f0:.0f} Hz，Q = {Q:.3f}")
assert abs(Q - 0.707) < 0.01 and abs(f0 - 1000) < 20

# ---------- 图 15-p2-3 一阶有源高通 ----------
with drawing() as d:
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Capacitor().right().label("$C$ 100 nF")
    d += (n := elm.Dot())
    d += elm.Resistor().down().label("$R$ 15.9 kΩ", "bottom")
    d += elm.Ground()
    follower_tail(d, n.center)
save_schem(d, N, "15_p2_3_highpass.png")
print(f"一阶高通 fc = 1/(2π × 15.9 kΩ × 100 nF) = {1 / (2 * np.pi * 15.9e3 * 100e-9):.0f} Hz")

# ---------- 图 15-p3-1 方波经过两种低通 ----------
t = np.linspace(0, 4e-3, 8001)
sq = fs.square(t, 500, amp=0.5, offset=0.5)            # 0～1 V、500 Hz 方波
_, y1, _ = signal.lsim(first, sq, t)
_, y2, _ = signal.lsim(sk, sq, t)
os2 = y2.max() - 1
print(f"500 Hz 方波（0～1 V）：一阶输出最高 {y1.max():.2f} V，二阶最高 {y2.max():.2f} V（过冲 {os2*100:.0f}%）")
assert 0.0 < os2 < 0.06
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, sq, **fs.LS["vin"], label="$V_i$ 方波 500 Hz")
ax.plot(t * 1e3, y1, **fs.LS["third"], label="一阶低通输出")
ax.plot(t * 1e3, y2, **fs.LS["vout"], label="二阶 Sallen-Key 输出")
k = np.argmax(y2)
fs.mark(ax, t[k] * 1e3, y2[k], fmt="{:.2f}", unit=" V", dx=6, dy=4)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-0.1, 1.45)
ax.legend(loc="upper right", fontsize=8, ncol=3)
fs.save(fig, N, "15_p3_1_square.png")

# ---------- 图 15-p3-2 漏了 2π：截止频率低了 6 倍多 ----------
f = np.logspace(1, 5, 600)
R_bad = 1 / (1e3 * C)                                   # 错误：R = 1/(fC) = 100 kΩ
fc_ok, fc_bad = 1 / (2 * np.pi * R * C), 1 / (2 * np.pi * R_bad * C)
h = lambda fx, fc: 20 * np.log10(1 / np.sqrt(1 + (fx / fc) ** 2))
print(f"漏了 2π：R 取成 {R_bad/1e3:.0f} kΩ，实际 fc = {fc_bad:.0f} Hz；1 kHz 处 {h(1e3, fc_bad):.0f} dB（应为 {h(1e3, fc_ok):.0f} dB）")
assert abs(fc_bad - 159) < 1
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.semilogx(f, h(f, fc_ok), **fs.LS["vout"], label="正确：R = 16 kΩ")
ax.semilogx(f, h(f, fc_bad), **fs.LS["bad"], label="漏了 2π：R = 100 kΩ")
fs.ref_v(ax, 1e3, "1 kHz（设计目标）")
fs.ref_v(ax, fc_bad, f"{fc_bad:.0f} Hz", y=0.12)
fs.mark(ax, 1e3, h(1e3, fc_bad), fmt="{:.0f}", unit=" dB", dx=-40, dy=-14)
fs.mark(ax, 1e3, h(1e3, fc_ok), fmt="{:.0f}", unit=" dB", dx=8, dy=-14)
fs.axlabels(ax, "频率", "Hz", "输出/输入 幅度", "dB")
ax.set_xticks([10, 100, 1e3, 1e4, 1e5]); ax.set_xticklabels(["10", "100", "1 k", "10 k", "100 k"])
ax.set_ylim(-60, 8); ax.legend(loc="lower left", fontsize=8)
fs.save(fig, N, "15_p3_2_missing_2pi.png")

# ---------- 参数与调试篇引用的经验数字（无图，只打印并断言） ----------
GBW_LM358 = 1.2e6                                       # LM358B 增益带宽积
need = lambda gain, fc: 100 * gain * fc                 # Microchip ADN003：Sallen-Key 要 GBW ≥ 100 × 倍数 × fc
n1, n2 = need(1, 1e3), need(10, 100e3)
print(f"GBW 经验要求：1 kHz 跟随型 {n1/1e3:.0f} kHz（LM358B {GBW_LM358/1e6:.1f} MHz 够用）；100 kHz × 10 倍 {n2/1e6:.0f} MHz（是 LM358B 的 {n2/GBW_LM358:.0f} 倍）")
assert n1 == 100e3 and n1 <= GBW_LM358 and n2 == 100e6 and round(n2 / GBW_LM358) == 83
drift = 30e-6 * 100                                     # C0G：±30 ppm/°C，温度变 100 °C
print(f"C0G 温度变 100 °C：容量最多变 {drift*100:.1f}%")
assert abs(drift - 0.003) < 1e-12
shift = 1 / np.sqrt(0.85 * 0.85) - 1                    # Sallen-Key：fc ∝ 1/√(C1·C2)，两只 X7R 都 −15%
print(f"两只电容都少 15%：截止频率高出 {shift*100:.1f}%")
assert abs(shift - 0.176) < 0.001

