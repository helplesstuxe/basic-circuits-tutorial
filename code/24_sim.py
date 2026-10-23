"""24 隔离电源与数字隔离器：三个小仿真，生成 24-isolated-power/img/ 里的曲线图。
运行：/workspace/circuits-venv/bin/python code/24_sim.py
A 工频变压器匝数比与整流滤波后的输出电压（后半段同 06 page2：峰值减两只二极管压降）。
B 不稳压隔离 DC-DC 模块（以 NME0505SC 为例：5 V 进、5 V 200 mA 出）的输出电压随负载变化的示意模型，以及两种补救（假负载电阻、稳压管钳位）。
C 光耦（通用型，上拉 1.9 kΩ）与数字隔离器（ISO7721）传输延时对比示意。
数据来源见 notes/24-research.md。图上的每个数字都由本脚本打印；关键结论用 assert 检查。
本脚本只做计算；A 部分的 220 V 只是公式里的数字，动手实验一律用 12 V 以下低压电源。
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "24"

# ================= A 匝数比 → 输出电压 =================
V1, VD = 220.0, 0.7                     # 初级有效值；每只整流二极管压降（同 06 page2）
def vdc_max(n, v1=V1):
    """匝数比 n = N1/N2 时，桥式整流 + 电容滤波后的最高电压：√2·V1/n − 2·V_D。"""
    return math.sqrt(2) * v1 / n - 2 * VD

n_main = 220 / 12                         # 220 V → 12 V 的变压器
v_main = vdc_max(n_main)
v_lo, v_hi = vdc_max(n_main, V1 * 0.9), vdc_max(n_main, V1 * 1.1)
print(f"[A] 匝数比 N1/N2 = {n_main:.2f}：副边 {V1/n_main:.1f} V 有效值，峰值 {math.sqrt(2)*V1/n_main:.2f} V，整流后最高 {v_main:.2f} V")
print(f"[A] 电网 ±10%（{V1*0.9:.0f} V ~ {V1*1.1:.0f} V，示意）时：{v_lo:.2f} V ~ {v_hi:.2f} V")
assert abs(v_main - 15.57) < 0.01                       # 与 06 page2 的 15.57 V 一致
n_need = math.sqrt(2) * V1 / (9 + 2 * VD)               # 例：想要整流后约 9 V
print(f"[A] 想要整流后约 9 V：N1/N2 ≈ {n_need:.1f}")

ns = np.linspace(10, 30, 201)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.fill_between(ns, [vdc_max(n, V1*0.9) for n in ns], [vdc_max(n, V1*1.1) for n in ns], color="0.85", label="电网电压 ±10% 的范围（示意）")
ax.plot(ns, [vdc_max(n) for n in ns], **fs.LS["vout"], label="220 V 时整流滤波后的最高电压")
fs.mark(ax, n_main, v_main, "{:.2f}", " V", dx=6, dy=4)
fs.mark(ax, n_main, v_hi, "{:.2f}", " V", dx=-44, dy=4, color="0.3")
fs.mark(ax, n_main, v_lo, "{:.2f}", " V", dx=-44, dy=-12, color="0.3")
fs.ref_v(ax, n_main, f"N1/N2 = {n_main:.2f}（220 V → 12 V）", y=0.97)
print(f"[数值] 竖线 N1/N2 = {n_main:.2f}")
ax.set_ylim(0, 32)
ax.legend(loc="upper right", fontsize=8)
fs.axlabels(ax, "匝数比 N1/N2", None, "电压", "V")
fs.save(fig, N, "24_p2_2_turns.png")

# ================= B 不稳压隔离模块：输出随负载 =================
I_FULL, V_NOM = 0.200, 5.0              # NME0505SC：额定 200 mA、5 V
LOAD_REG = 0.12                         # 负载调整率典型 12%（10% → 100% 负载）
def v_module(i, vin=5.0):
    """示意模型：10%~100% 负载之间输出从 5.6 V 线性降到 5.0 V；低于约 5% 负载时升到约两倍（手册说法）；
    输入每变 1%，输出变 1.2%（手册线性调整率上限）。i 是总负载电流 / A。"""
    x = max(i, 0.0) / I_FULL
    v = V_NOM * (1 + LOAD_REG * (1 - x) / 0.9)
    v += 4.4 / (1 + math.exp((x - 0.065) / 0.006))      # 轻载上翘（示意）
    return v * (1 + 1.2 * (vin - 5.0) / 5.0)

def solve(i_user, extra=lambda v: 0.0, vin=5.0):
    """求工作点：模块输出 V 要同时满足 V = v_module(用户电流 + 补救电路电流)。二分法。"""
    lo, hi = 0.0, 15.0
    for _ in range(80):
        m = (lo + hi) / 2
        if v_module(i_user + extra(m), vin) > m:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2

I_ISO, I_SENSOR = 1.7e-3, 3.0e-3        # ISO7721 副边电流典型 1.7 mA（1 Mbps）；传感器 3 mA（示意）
I_USER = I_ISO + I_SENSOR
R_DUMMY = 270.0                          # 假负载：5.6 V / 20 mA ≈ 280 Ω，取 270 Ω
VZ, RZ = 5.1, 24.0                       # 稳压管钳位：(5.6 − 5.1) V / 20 mA = 25 Ω，取 24 Ω
dummy = lambda v: v / R_DUMMY
zener = lambda v: max(v - VZ, 0.0) / RZ

v_full, v_10 = v_module(I_FULL), v_module(0.1 * I_FULL)
v_bare, v_dum, v_zen = solve(I_USER), solve(I_USER, dummy), solve(I_USER, zener)
v_bare_hi = solve(I_USER, vin=5.5)
print(f"[B] 满载 200 mA：{v_full:.2f} V；10% 负载 20 mA：{v_10:.2f} V（负载调整率 {(v_10-v_full)/V_NOM*100:.0f}%）")
print(f"[B] 现场侧只用 {I_USER*1e3:.1f} mA（{I_USER/I_FULL*100:.2f}% 负载）：不处理 {v_bare:.2f} V；输入 5.5 V 时 {v_bare_hi:.2f} V")
print(f"[B] 加 {R_DUMMY:.0f} Ω 假负载：{v_dum:.2f} V，假负载电流 {v_dum/R_DUMMY*1e3:.1f} mA、功耗 {v_dum**2/R_DUMMY*1e3:.0f} mW，留给用户的电流约 {(I_FULL - v_dum/R_DUMMY)*1e3:.0f} mA")
print(f"[B] 加 {VZ} V 稳压管 + {RZ:.0f} Ω：{v_zen:.2f} V，稳压管支路 {zener(v_zen)*1e3:.1f} mA")
iz_off = next(i for i in np.linspace(0, I_FULL, 2001) if v_module(i) <= VZ)
print(f"[B] 负载超过 {iz_off*1e3:.0f} mA（{iz_off/I_FULL*100:.0f}%）后模块输出低于 {VZ} V，稳压管支路不再耗电")
ISO_ABS_MAX, ISO_REC_MAX = 6.0, 5.5
assert v_bare > ISO_ABS_MAX                   # 结论 1：轻载时输出超过 ISO7721 的绝对最大值 6 V
assert v_dum < 5.65 and v_zen < 5.65          # 结论 2：两种补救都把电压拉回手册 10% 负载时的水平
assert v_dum > ISO_REC_MAX                    # 结论 3：仍略高于 ISO7721 推荐上限 5.5 V（正文要提醒）
assert abs((v_10 - v_full) / V_NOM - 0.12) < 0.005

ii = np.linspace(0, I_FULL, 801)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(ii * 1e3, [v_module(i) for i in ii], **fs.LS["vout"], label="模块输出电压（示意模型）")
ax.axvspan(0, 0.1 * I_FULL * 1e3, color="0.9", zorder=0)
ax.text(1, 3.2, "低于 10%\n负载", fontsize=8, color="0.3")
fs.ref_h(ax, ISO_ABS_MAX, f"ISO7721 绝对最大 {ISO_ABS_MAX:.0f} V", x=0.99)
fs.mark(ax, I_USER * 1e3, v_bare, "{:.2f}", " V", dx=6, dy=-4, color=fs.C["bad"], marker="x")
fs.mark(ax, 0.1 * I_FULL * 1e3, v_10, "{:.2f}", " V", dx=4, dy=6)
fs.mark(ax, I_FULL * 1e3, v_full, "{:.2f}", " V", dx=-34, dy=-14)
ax.set_xlim(0, 205); ax.set_ylim(3, 11.5)
ax.legend(loc="upper right", fontsize=8)
fs.axlabels(ax, "负载电流", "mA", "输出电压", "V")
print(f"[数值] 用户负载 {I_USER*1e3:.1f} mA；10% 负载 {0.1*I_FULL*1e3:.0f} mA；满载 {I_FULL*1e3:.0f} mA")
fs.save(fig, N, "24_p2_4_load.png")

iu = np.linspace(0, I_FULL * 0.6, 601)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(iu * 1e3, [solve(i) for i in iu], **fs.LS["bad"], label="不处理")
ax.plot(iu * 1e3, [solve(i, dummy) for i in iu], **fs.LS["vout"], label=f"并 {R_DUMMY:.0f} Ω 假负载")
ax.plot(iu * 1e3, [solve(i, zener) for i in iu], **fs.LS["third"], label=f"{VZ} V 稳压管 + {RZ:.0f} Ω 钳位")
fs.ref_h(ax, ISO_ABS_MAX, f"{ISO_ABS_MAX:.0f} V", x=0.99)
fs.ref_h(ax, ISO_REC_MAX, f"{ISO_REC_MAX} V", x=0.93)
fs.mark(ax, I_USER * 1e3, v_dum, "{:.2f}", " V（两种补救相同）", dx=8, dy=6, color="k")
v_dum100, v_zen100 = solve(0.1, dummy), solve(0.1, zener)
fs.mark(ax, 100, v_dum100, "{:.2f}", " V", dx=-10, dy=-14, color=fs.C["vout"])
fs.mark(ax, 100, v_zen100, "{:.2f}", " V", dx=4, dy=6, color=fs.C["third"])
print(f"[B] 用户 100 mA 时：假负载方案 {v_dum100:.2f} V（假负载仍吃 {v_dum100/R_DUMMY*1e3:.1f} mA），稳压管方案 {v_zen100:.2f} V（稳压管支路 {zener(v_zen100)*1e3:.1f} mA）")
assert abs(v_dum - v_zen) < 0.02 and zener(v_zen100) < 0.5 * v_dum100 / R_DUMMY   # 重载时稳压管支路耗电不到假负载的一半
ax.set_ylim(4.5, 11.5)
ax.legend(loc="upper right", fontsize=8)
fs.axlabels(ax, "现场侧电路自己用的电流", "mA", "模块输出电压", "V")
fs.save(fig, N, "24_p3_2_fix.png")

# ================= C 传输延时对比 =================
T_PHL, T_PLH = 0.5e-6, 40e-6            # 通用光耦，上拉 1.9 kΩ（TI SLLA526D 表中典型值）
TAU = (T_PLH - T_PHL) / math.log((VCC_O := 5.0 - 0.2) / 2.5)   # 示意：从 0.2 V 回升，让输入变低后 40 µs 时刚好过 2.5 V
T_ISO = 11e-9                           # ISO7721 典型传输延时
F_SIG, VCC = 5e3, 5.0
t = np.linspace(0, 400e-6, 40001)
vin = np.where((t % (1 / F_SIG)) < 0.5 / F_SIG, VCC, 0.0)

def opto(t):
    """光耦 + 上拉输出（反相）：输入变高 → 0.5 µs 后迅速拉低；输入变低 → 按 τ 缓慢回升。"""
    v, out, last = VCC, [], 0.0
    dt = t[1] - t[0]
    for k, tk in enumerate(t):
        on = ((tk - T_PHL) % (1 / F_SIG)) < 0.5 / F_SIG if tk >= T_PHL else False
        v = 0.2 if on else v + (VCC - v) * dt / TAU
        out.append(v)
    return np.array(out)

vo_opto = opto(t)
vo_iso = np.where(((t - T_ISO) % (1 / F_SIG)) < 0.5 / F_SIG, VCC, 0.0) * (t >= T_ISO)
t_fall = t[np.argmax(vo_opto < VCC / 2)]
i_rise = np.argmax((t > 100e-6) & (vo_opto > VCC / 2))
t_rise = t[i_rise] - 100e-6
v_end_low = vo_opto[np.argmin(abs(t - 199.9e-6))]
rate_opto = 1 / (4 * max(T_PHL, T_PLH)); rate_iso = 1 / (4 * T_ISO)
bit_uart = 1 / 115200
print(f"[C] 光耦：输入变高后 {t_fall*1e6:.1f} µs 输出过半；输入变低后 {t_rise*1e6:.1f} µs 输出才回升过半")
print(f"[C] 下一个脉冲到来前（{(1/F_SIG - 0.5/F_SIG)*1e6:.0f} µs 后）光耦输出只回到 {v_end_low:.2f} V")
print(f"[C] 数字隔离器延时 {T_ISO*1e9:.0f} ns；按 SLLA526D 的估算式 1/(4·最大延时)：光耦 {rate_opto/1e3:.2f} kbps，ISO7721 {rate_iso/1e6:.1f} Mbps")
print(f"[C] 115200 波特率串口一位宽 {bit_uart*1e6:.2f} µs，比光耦慢的那一边 {T_PLH*1e6:.0f} µs 短")
assert abs(t_rise - T_PLH) < 0.5e-6 and t_fall < 1e-6
assert bit_uart < T_PLH and T_ISO < bit_uart / 100

fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
tu = t * 1e6
ax.plot(tu, vin + 12, **fs.LS["vin"], label="输入信号（单片机发出）")
ax.plot(tu, vo_iso + 6, **fs.LS["vout"], label="数字隔离器输出（延时 11 ns，与输入重合）")
ax.plot(tu, vo_opto, **fs.LS["third"], label="光耦输出（反相；上拉 1.9 kΩ）")
for y0 in (0, 6, 12):
    fs.ref_h(ax, y0 + VCC / 2, None)
ax.annotate(f"慢：约 {t_rise*1e6:.0f} µs 才过半", xy=(100 + t_rise * 1e6, VCC / 2), xytext=(150, 2.0),
            fontsize=9, arrowprops=dict(arrowstyle="->", color="0.3"))
ax.annotate(f"快：约 {t_fall*1e6:.1f} µs", xy=(t_fall * 1e6, 0.3), xytext=(25, 1.0), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="0.3"))
print(f"[数值] 图注：慢 约 {t_rise*1e6:.0f} µs；快 约 {t_fall*1e6:.1f} µs；信号 {F_SIG/1e3:.0f} kHz")
ax.set_yticks([0, 5, 6, 11, 12, 17]); ax.set_yticklabels(["0", "5", "0", "5", "0", "5"])
ax.set_ylim(-1, 21.5)
ax.legend(loc="upper right", fontsize=8, ncol=1)
fs.axlabels(ax, "时间", "µs", "电压（三条曲线上下错开）", "V")
fs.save(fig, N, "24_p1_2_delay.png")
