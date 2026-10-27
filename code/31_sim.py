"""31 跨阻放大器（光电二极管 → 电压）：页面上所有数字的来源。
运行：/workspace/circuits-venv/bin/python code/31_sim.py
只用 numpy / scipy；不写任何文件。SPICE 复核见 spice/31/run.py。

模型说明：
- 运放用「单极点」模型：开环增益 A(s) = ω_t / s，ω_t = 2π·GBW。
- 光电二极管 = 理想电流源 I 并一只电容 C_D（结电容 + 运放输入电容 + 杂散电容的总和）。
- 反馈 = R_F 并 C_F。由此得到电流→电压的传递函数（推导见 page2）：
      H(s) = R_F·ω_t / [ R_F(C_F + C_D)·s² + (1 + ω_t·R_F·C_F)·s + ω_t ]
"""
import numpy as np
from scipy import signal

# ---------------- 器件参数（来源见 page1～page4 的参考资料） ----------------
VCC = 5.0                 # 实验用 Arduino 的 5V 脚
RB1, RB2 = 10e3, 2.2e3    # 偏置分压：5 V —RB1— V_B —RB2— 0 V
GBW = 1.0e6               # LMC6482 手册 3 V 表格的增益带宽积（5 V 时保守取这个）
C_IN = 3e-12              # LMC6482 共模输入电容
CJ0 = 70e-12              # BPW34 结电容，反偏 0 V
CJ3, CJ3MAX = 25e-12, 40e-12  # BPW34 结电容，反偏 3 V（典型 / 最大）
VOH = 4.9                 # LMC6482 5 V、2 kΩ 负载时输出上限（典型）
VOL = 0.1                 # 输出下限（典型）
IB = dict(LMC6482=4e-12, LM358B=35e-9, LM358=250e-9)      # 输入偏置电流（最大值）
IB_TYP = dict(LMC6482=0.02e-12, LM358B=10e-9, LM358=20e-9)
RCAL = 10e6               # 校准用 10 MΩ
ADC_LSB = VCC / 1024      # analogRead 一个字
T_ADC = 100e-6            # analogRead 一次约 100 µs


def vb(vcc=VCC):
    return vcc * RB2 / (RB1 + RB2)


def cf_opt(rf, cd, gbw=GBW):
    """SBOA055A 式 (5)：让阶跃响应刚好不过冲（约 45°～65° 相位裕度）的 C_F。"""
    return (1 + np.sqrt(1 + 8 * np.pi * rf * cd * gbw)) / (4 * np.pi * rf * gbw)


def f_p(rf, cd, gbw=GBW):
    """SBOA055A 式 (6)：f_P = √(GBW / (2π R_F C_D))。"""
    return np.sqrt(gbw / (2 * np.pi * rf * cd))


def tf(rf, cd, cf, gbw=GBW):
    wt = 2 * np.pi * gbw
    return signal.lti([rf * wt], [rf * (cf + cd), 1 + wt * rf * cf, wt])


def zeta(rf, cd, cf, gbw=GBW):
    wt = 2 * np.pi * gbw
    a, b, c = rf * (cf + cd), 1 + wt * rf * cf, wt
    return b / (2 * np.sqrt(a * c)), np.sqrt(c / a) / (2 * np.pi)


def step(rf, cd, cf, gbw=GBW, tmax=None, n=40001):
    """单位电流阶跃（1 A）→ 输出（单位：V/A = Ω）。返回 t、y/R_F（终值 = 1）、过冲%、10–90% 上升时间。"""
    z, fn = zeta(rf, cd, cf, gbw)
    if tmax is None:
        tmax = max(12 / (2 * np.pi * fn * max(z, 0.02)), 5 * rf * (cf + 1e-15)) if z < 1 else 8 * rf * (cf + cd)
        tmax = min(tmax, 0.02)
    t = np.linspace(0, tmax, n)
    t, y = signal.step(tf(rf, cd, cf, gbw), T=t)
    y = y / rf
    ov = max(0.0, (y.max() - 1) * 100)
    t10 = t[np.argmax(y >= 0.1)]
    t90 = t[np.argmax(y >= 0.9)]
    return t, y, ov, t90 - t10


def bw3db(rf, cd, cf, gbw=GBW):
    f = np.logspace(1, 8, 20001)
    w, h = signal.freqresp(tf(rf, cd, cf, gbw), 2 * np.pi * f)
    m = np.abs(h) / rf
    k = np.argmax(m < 1 / np.sqrt(2))
    return f[k], 20 * np.log10(m.max())


def report():
    out = {}
    v = vb()
    out["VB"] = v
    print(f"偏置 V_B = 5 × 2.2/(10+2.2) = {v:.4f} V")
    # ---- 直流：校准 ----
    i_g = v / RCAL
    i_5 = (VCC - v) / RCAL
    print(f"校准①：10 MΩ 接 0 V，I = V_B/10M = {i_g*1e9:.2f} nA；R_F = 1 MΩ 时 Vout − V_B = {i_g*1e6*1e3:.2f} mV，Vout = {v + i_g*1e6:.4f} V")
    print(f"校准②：10 MΩ 接 5 V，I = (5 − V_B)/10M = {i_5*1e9:.2f} nA（从 +5 V 经 R_CAL 流进反相端）；Vout − V_B = {-i_5*1e6*1e3:.2f} mV，Vout = {v - i_5*1e6:.4f} V")
    out.update(I_g=i_g, I_5=i_5, dV_g=i_g * 1e6, dV_5=-i_5 * 1e6)
    # ---- 偏置电流误差 ----
    for k in ("LMC6482", "LM358B", "LM358"):
        print(f"偏置电流误差 I_B×1MΩ：{k} 典型 {IB_TYP[k]*1e6*1e3:.4g} mV，最大 {IB[k]*1e6*1e3:.4g} mV")
    print(f"换 LM358 做校准①：典型 Vout − V_B ≈ {(i_g - IB_TYP['LM358'])*1e6*1e3:.1f} mV，最坏 ≈ {(i_g - IB['LM358'])*1e6*1e3:.1f} mV")
    # ---- 量程 ----
    for rf in (47e3, 1e6):
        print(f"R_F = {rf/1e3:g} kΩ：输出从 V_B 升到 {VOH} V，最多容纳 I = {(VOH - v)/rf*1e6:.2f} µA；1 µA → {rf*1e-6*1e3:.0f} mV")
    print(f"BPW34 1 klx 短路电流 70 µA × 47 kΩ = {70e-6*47e3:.2f} V；× 1 MΩ = {70e-6*1e6:.0f} V（远超 5 V 电源，会饱和）")
    print(f"暗电流 2 nA × 1 MΩ = {2e-9*1e6*1e3:.0f} mV（手册 10 V 反偏时的典型值，这里反偏只有约 0.9 V，只会更小）")
    # ---- page4 第 7 步：反偏 + 串 1 MΩ，万用表 10 MΩ 并在上面 ----
    rp = 1 / (1 / 1e6 + 1 / 10e6)
    print(f"第 7 步：RS 1 MΩ ∥ 万用表 10 MΩ = {rp/1e6:.3f} MΩ；暗电流典型 2 nA → {2e-9*rp*1e3:.2f} mV，最大 30 nA → {30e-9*rp*1e3:.1f} mV")
    print(f"第 7 步：室内光约 21 µA（47k 时约 1 V）× {rp/1e6:.3f} MΩ = {21e-6*rp:.1f} V，远超 5 V → 读数顶到接近 5 V")
    # ---- 只用电阻（不用运放）----
    for r, c in ((1e6, CJ0), (47e3, CJ0)):
        print(f"光电二极管直接接 {r/1e3:g} kΩ 电阻：τ = R·C_D = {r*c*1e6:.2f} µs，带宽 1/(2πτ) = {1/(2*np.pi*r*c)/1e3:.2f} kHz")
    # ---- C_F 与 f_P ----
    for rf, cd in ((1e6, CJ0 + C_IN), (1e6, CJ3 + C_IN), (47e3, CJ0 + C_IN), (100e3, CJ3 + C_IN)):
        c = cf_opt(rf, cd)
        print(f"R_F={rf/1e3:g}k, C_D={cd*1e12:.0f}pF, GBW=1MHz：C_F ≥ {c*1e12:.2f} pF，f_P = {f_p(rf, cd)/1e3:.1f} kHz，"
              f"加 C_F 后带宽 1/(2πR_F C_F) = {1/(2*np.pi*rf*c)/1e3:.1f} kHz")
    # 留余量：GBW 按典型值的 60%（ADI 建议），例 1、例 2 的选值依据
    for rf in (1e6, 47e3):
        print(f"R_F={rf/1e3:g}k, C_D=73pF, GBW 按 60%：C_F ≥ {cf_opt(rf, CJ0 + C_IN, 0.6 * GBW)*1e12:.2f} pF")
    for rf, c in ((1e6, 3.9e-12), (47e3, 22e-12)):
        from scipy.optimize import brentq
        g = brentq(lambda x: cf_opt(rf, CJ0 + C_IN, x) - c, 1e5, 1e6)
        print(f"R_F={rf/1e3:g}k：{c*1e12:g} pF 刚好够时 GBW = {g/GBW*100:.0f}% 典型值")
    # 例题 2 的中间量
    rf, cd = 47e3, CJ0 + C_IN
    x = 8 * np.pi * rf * cd * GBW
    print(f"例2 中间量：8π·R_F·C_D·GBW = {x:.2f}，√(1+它) = {np.sqrt(1+x):.3f}，4π·R_F·GBW = {4*np.pi*rf*GBW:.4g}")
    rf, cd = 1e6, CJ0 + C_IN
    x = 8 * np.pi * rf * cd * GBW
    print(f"例1 中间量：8π·R_F·C_D·GBW = {x:.1f}，√(1+它) = {np.sqrt(1+x):.3f}，4π·R_F·GBW = {4*np.pi*rf*GBW:.4g}")
    # ---- 阶跃响应 ----
    cd = CJ0 + C_IN
    for rf, cfs in ((1e6, (0, 1e-12, 2.2e-12, 3.3e-12, 4.7e-12, 10e-12)), (47e3, (0, 10e-12, 22e-12, 27e-12))):
        for cf in cfs:
            z, fn = zeta(rf, cd, cf)
            t, y, ov, tr = step(rf, cd, cf)
            fb, pk = bw3db(rf, cd, cf)
            print(f"阶跃 R_F={rf/1e3:g}k C_D=73p C_F={cf*1e12:g}p：ζ={z:.3f}，振荡频率≈{fn/1e3:.1f} kHz，过冲 {ov:.1f}%，"
                  f"上升 {tr*1e6:.2f} µs，−3 dB 带宽 {fb/1e3:.1f} kHz，峰值 {pk:+.1f} dB")
    # ---- 慢速演示：C_F = 1 µF ----
    tau = 1e6 * 1e-6
    v0, v1 = v + i_g * 1e6, v - i_5 * 1e6
    for tt in (1, 2, 3, 5):
        print(f"慢速演示 τ = {tau:.1f} s：10 MΩ 从 0 V 改到 5 V 后 {tt} s，Vout = {v1 + (v0 - v1)*np.exp(-tt/tau):.4f} V")
    out.update(v0=v0, v1=v1, tau=tau)
    # ---- Arduino ----
    print(f"analogRead 一个字 = 5/1024 = {ADC_LSB*1e3:.3f} mV；90 mV ≈ {i_g*1e6/ADC_LSB:.1f} 个字；500 mV ≈ {(v0-v1)/ADC_LSB:.0f} 个字")
    z, fn = zeta(1e6, cd, 0)
    print(f"Arduino 每次读数约 {T_ADC*1e6:.0f} µs（≈{1/T_ADC/1e3:.0f} kS/s）；C_F=0 时振荡周期 {1/fn*1e6:.1f} µs，一次读数要跨过 {T_ADC*fn:.1f} 个周期")
    # ---- SBOA268 例子 ----
    cf268 = 1 / (2 * np.pi * 100e3 * 10e3)   # 原文叫 C1，这里叫 C_F，免得和去耦电容 C1 重名
    print(f"SBOA268：C_F ≤ 1/(2π·100k·10k) = {cf268*1e12:.1f} pF → 取 150 pF，带宽 {1/(2*np.pi*100e3*150e-12)/1e3:.2f} kHz；"
          f"GBW > (6p+150p)/(2π·100k·150p²) = {(156e-12)/(2*np.pi*100e3*(150e-12)**2)/1e3:.2f} kHz")
    print(f"同一电路用 SBOA055A 式(5)，C_D = 6 pF、GBW = 1.2 MHz：C_F ≥ {cf_opt(100e3, 6e-12, 1.2e6)*1e12:.2f} pF")
    rf3 = (4.9 - (5 * 2.2 / 12.2)) / 20e-6
    cmax3 = 1 / (2 * np.pi * 180e3 * 5e3)
    need3 = (73e-12 + 150e-12) / (2 * np.pi * 180e3 * (150e-12) ** 2)
    print(f"例3 变体（page2）：R_F ≤ (4.9 − {(5 * 2.2 / 12.2):.4f})/20 µA = {rf3/1e3:.1f} kΩ → 取 180 kΩ（20 µA 时 {(5 * 2.2 / 12.2) + 20e-6*180e3:.2f} V）；"
          f"C_F ≤ {cmax3*1e12:.1f} pF → 取 150 pF，带宽 {1/(2*np.pi*180e3*150e-12)/1e3:.2f} kHz；GBW > {need3/1e3:.2f} kHz；"
          f"式(5) 下限 {cf_opt(180e3, 73e-12, 1e6)*1e12:.2f} pF")
    return out


if __name__ == "__main__":
    report()
