"""34 开关电容滤波：页面里用到的全部数值都由本脚本算出（在仓库根目录运行：python code/34_sim.py）。
电路：CD4053 的 A 路当单刀双掷开关，C1（小电容）在「输入」和「输出」之间来回搬电荷，C2（大电容）存电荷。
时钟：24 节的 LM358 弛张振荡器，9 V 单电源。时钟的高低电平 VOH、VOL 取自 spice/34 的仿真（LM358 输出到不了 0 V 和 9 V）。
"""
import numpy as np

VCC = 9.0                 # 电池电压 / V
VOH, VOL = 7.79, 0.64     # LM358 时钟输出的高、低电平 / V（spice/34/osc.cir 仿真值）
RT1, RT2 = 68e3, 136e3    # 定时电阻：一只 68 kΩ，或两只 68 kΩ 串联
CT = 100e-9               # 定时电容 100 nF
F_CLK1, F_CLK2 = 104.4, 52.44   # SPICE 量得的时钟频率 / Hz（LM358B 模型）
C1, C2 = 10e-9, 1e-6      # 搬运电容 10 nF、存储电容 1 µF
VIN = 4.5                 # 输入：10 kΩ/10 kΩ 分压
RL = 1e6                  # 静态核对用的 1 MΩ 负载
RON_TYP, RON_MAX = 180.0, 400.0   # CD4053 导通电阻（VDD = 10 V 时典型 / 最大，手册表格）
RON_5V_TYP, RON_5V_MAX = 470.0, 1050.0   # VDD = 5 V 时典型 / 最大（手册；125 Ω 只是 15 V 时的典型值）
VIH_5 = 3.5               # VDD = 5 V 时控制端最低「高」电压（手册）
VIH_10 = 7.0              # CD4053 控制端「认作高」的最低电压（VDD = 10 V 时，手册）


def r_eq(f, c1=C1):
    """开关电容的等效电阻：每拍搬 c1·ΔV 的电荷，每秒 f 拍，平均电流 f·c1·ΔV，所以 R = 1/(f·c1)。"""
    return 1.0 / (f * c1)


def tau_rc(f, c1=C1, c2=C2):
    """把 R_eq 当电阻看：τ = R_eq·C2 = C2/(f·C1)。"""
    return r_eq(f, c1) * c2


def alpha(c1=C1, c2=C2):
    """每拍 C2 上的电压向输入靠近「剩余差距」的 alpha 倍：alpha = C1/(C1 + C2)。"""
    return c1 / (c1 + c2)


def step_discrete(f, n, vin=VIN, c1=C1, c2=C2, rl=None):
    """一拍一拍地算：A 拍 C1 充到 vin；B 拍 C1 与 C2 分电荷。rl 给出时，B 拍之间 C2 还经 rl 放电一个周期。
    返回每拍结束后 C2 上的电压（长度 n + 1，含起点 0）。"""
    a = alpha(c1, c2)
    v = np.zeros(n + 1)
    for k in range(n):
        x = v[k] + (vin - v[k]) * a            # 分电荷：总电荷不变
        if rl is not None:
            x *= np.exp(-1.0 / (f * rl * c2))  # 一个周期里经 rl 漏掉一点
        v[k + 1] = x
    return v


def cycles_to(frac, c1=C1, c2=C2):
    """离散模型里到达终值 frac（如 0.632、0.95）要几拍：(1 − alpha)^n = 1 − frac。"""
    return np.log(1 - frac) / np.log(1 - alpha(c1, c2))


def t_to(frac, f, c1=C1, c2=C2):
    return cycles_to(frac, c1, c2) / f


def v_rl(f, vin=VIN, rl=RL):
    """接 rl 后的稳态：R_eq 与 rl 分压。"""
    return vin * rl / (rl + r_eq(f))


def relax_T(R, C, voh=VOH, vol=VOL, vcc=VCC):
    """24 节弛张振荡器周期（三只相等门限电阻）：上门限 (vcc + voh)/3，下门限 (vcc + vol)/3；
    两段充放电各用 RC·ln(起点差距/终点差距)。返回 (T, 上门限, 下门限, 高电平时间)。"""
    vh, vl = (vcc + voh) / 3, (vcc + vol) / 3
    th = R * C * np.log((voh - vl) / (voh - vh))
    tl = R * C * np.log((vh - vol) / (vl - vol))
    return th + tl, vh, vl, th


def alias(f, fs):
    """被采样频率 fs「看成」的频率：离 f 最近的 fs 整数倍之差。"""
    return abs(f - round(f / fs) * fs)


def rc_lp(f, fc):
    """一阶 RC 低通幅度（20 节）：1/sqrt(1 + (f/fc)²)。"""
    return 1 / np.sqrt(1 + (f / fc) ** 2)


if __name__ == "__main__":
    print("== 等效电阻 ==")
    for f in (10e3, 1e3, F_CLK1, F_CLK2):
        print(f"f = {f:8.2f} Hz：R_eq = {r_eq(f)/1e3:8.1f} kΩ，τ(RC) = {tau_rc(f):.4f} s")
    print(f"1 nF、10 kHz：R_eq = {r_eq(10e3, 1e-9)/1e3:.0f} kΩ")
    print(f"alpha = C1/(C1+C2) = {alpha():.5f} = 1/{1/alpha():.0f}；第一拍抬高 {VIN*alpha()*1e3:.1f} mV")
    print(f"63% 要 {cycles_to(0.632):.1f} 拍；95% 要 {cycles_to(0.95):.1f} 拍（RC 估算分别为 100、{3*100:.0f}）")
    for f in (F_CLK1, F_CLK2):
        print(f"f = {f} Hz：63% 在 {t_to(0.632, f):.3f} s（读 {0.632*VIN:.2f} V），95% 在 {t_to(0.95, f):.3f} s（读 {0.95*VIN:.2f} V）；"
              f"接 1 MΩ 稳态 {v_rl(f):.3f} V，离散 {step_discrete(f, 3000, rl=RL)[-1]:.3f} V")
    print("== 时钟（24 节弛张振荡器，9 V） ==")
    for R in (RT1, RT2):
        T, vh, vl, th = relax_T(R, CT)
        print(f"R = {R/1e3:.0f} kΩ：上门限 {vh:.3f} V，下门限 {vl:.3f} V，T = {T*1e3:.3f} ms = {T/(R*CT):.3f}RC，"
              f"f = {1/T:.1f} Hz，高电平占 {th/T*100:.1f}%，直流挡平均 {VOL + th/T*(VOH-VOL):.2f} V")
    T, vh, vl, th = relax_T(RT1, CT)
    tl = T - th
    k_h, k_l = th / (RT1 * CT), tl / (RT1 * CT)
    print(f"三个电压的平均值：上门限 (9 + 0 + {VOH})/3 = {vh:.3f} V，下门限 (9 + 0 + {VOL})/3 = {vl:.3f} V")
    print(f"戴维南加权：4.5×10/15 + VOH×5/15 = {4.5*10/15 + VOH*5/15:.3f} V，4.5×10/15 + VOL×5/15 = {4.5*10/15 + VOL*5/15:.3f} V（同一回事）")
    print(f"高电平段 ln(({VOH}−{vl:.3f})/({VOH}−{vh:.3f})) = {k_h:.3f}，低电平段 ln(({vh:.3f}−{VOL})/({vl:.3f}−{VOL})) = {k_l:.3f}，合计 {k_h+k_l:.3f}，占空比 {k_h/(k_h+k_l)*100:.1f}%")
    assert abs(k_h - 0.736) < 0.001 and abs(k_l - 0.656) < 0.001 and abs(k_h + k_l - 1.391) < 0.001
    assert abs(vh - 4.5*10/15 - VOH*5/15) < 1e-9
    f_formula1, f_formula2 = 1 / relax_T(RT1, CT)[0], 1 / relax_T(RT2, CT)[0]
    print(f"公式 {f_formula1:.1f} / {f_formula2:.2f} Hz，ngspice {F_CLK1} / {F_CLK2} Hz：低 {(1-F_CLK1/f_formula1)*100:.1f}% / {(1-F_CLK2/f_formula2)*100:.1f}%；"
          f"公式一半 {F_CLK1/2:.1f} Hz，ngspice 频率比 {F_CLK1/F_CLK2:.3f}")
    assert 1.0 < (1 - F_CLK1 / f_formula1) * 100 < 1.4 and (1 - F_CLK2 / f_formula2) < (1 - F_CLK1 / f_formula1)
    print(f"低电平检查：VOL = {VOL} V < VIL ≈ 0.3×VDD = {0.3*VCC:.1f} V")
    print(f"理想满幅（24 节）：T = 2·ln2·RC = {2*np.log(2)*RT1*CT*1e3:.3f} ms → {1/(2*np.log(2)*RT1*CT):.1f} Hz")
    print(f"VOH − VIH(10 V) = {VOH - VIH_10:.2f} V；按 70% VDD 估算 9 V 时 VIH = {0.7*VCC:.2f} V，余量 {VOH-0.7*VCC:.2f} V")
    print(f"对比：若整板改用 5 V，LM358 高电平约 {VOH-(VCC-5):.2f} V（同样比电源低约 {VCC-VOH:.2f} V），VIH(5 V) = {VIH_5} V，余量只剩 {VOH-(VCC-5)-VIH_5:.2f} V")
    print("== 开关导通电阻 ==")
    for r in (RON_TYP, RON_MAX, RON_5V_TYP, RON_5V_MAX):
        tc = r * C1
        print(f"R_on = {r:.0f} Ω：R_on·C1 = {tc*1e6:.1f} µs；半个时钟周期 {0.5/F_CLK1*1e3:.2f} ms = {0.5/F_CLK1/tc:.0f} 个时间常数")
    rs = 5e3
    print(f"分压源内阻 5 kΩ：5 kΩ·C1 = {rs*C1*1e6:.0f} µs，半周期内 {0.5/F_CLK1/(rs*C1):.0f} 个时间常数")
    print("== 混叠 ==")
    for f, fs in ((95, 100), (105, 100), (5, 100), (200, 100), (98, 100)):
        print(f"{f} Hz 用 {fs} Hz 采样 → 看起来像 {alias(f, fs):.0f} Hz")
    for f, fs in ((60, 100), (40, 100), (150, 100), (50, 20)):
        print(f"{f} Hz 用 {fs} Hz 采样 → 看起来像 {alias(f, fs):.0f} Hz")
    assert alias(200, 100) == 0 and alias(60, 100) == 40 and alias(50, 20) == 10 and alias(40, 100) == 40
    print(f"104.4 Hz 时钟：99.4 Hz → {alias(99.4, F_CLK1):.1f} Hz；若按 104 Hz 算 → {alias(99.4, 104):.1f} Hz")
    print(f"车轮：每秒 24 帧拍 23 圈/秒的轮子 → 看到 {alias(23, 24):.0f} 圈/秒（方向倒转）")
    print("== 抗混叠 RC ==")
    fcl = F_CLK1 / 10
    print(f"抗混叠截止取 f_CLK/10 = {fcl:.1f} Hz：对 {F_CLK1-5:.1f} Hz（离时钟 5 Hz）衰减到 {rc_lp(F_CLK1-5, fcl):.3f}，"
          f"对 1 Hz 保留 {rc_lp(1, fcl):.4f}")
    fc1, fc2 = 1 / (2 * np.pi * tau_rc(F_CLK1)), 1 / (2 * np.pi * tau_rc(F_CLK2))
    print(f"开关电容低通的截止频率 fc = 1/(2πτ)：{fc1:.3f} Hz / {fc2:.3f} Hz")
    assert abs(fc1 - 0.166) < 0.001 and abs(fc2 - 0.083) < 0.001
    print(f"1 Hz 经开关电容低通（104.4 Hz 时钟）剩 {rc_lp(1, fc1):.3f}；混出的 5 Hz 再经它剩 {rc_lp(5, fc1):.3f}，"
          f"与前置 0.104 相乘 {rc_lp(F_CLK1-5, fcl)*rc_lp(5, fc1):.4f}")
    RF, CF = 1.5e3, 10e-6
    fcf = 1 / (2 * np.pi * RF * CF)
    print(f"前置实用值 Rf 1.5 kΩ、Cf 10 µF：截止 {fcf:.1f} Hz，99.4 Hz → {rc_lp(99.4, fcf):.3f}，Cf/C1 = {CF/C1:.0f}，"
          f"每拍被 C1 抽走 ≤ {C1/(C1+CF)*100:.1f}% 的差距")
    RS, CS = 10e3, 10e-6
    fcs = 1 / (2 * np.pi * RS * CS)
    print(f"后置（跟随器之后）Rs 10 kΩ、Cs 10 µF：截止 {fcs:.2f} Hz，{F_CLK1} Hz 的台阶 → {rc_lp(F_CLK1, fcs):.4f}")
    assert abs(fcf - 10.6) < 0.05 and abs(rc_lp(99.4, fcf) - 0.106) < 0.001 and abs(fcs - 1.59) < 0.01
    print("== 动手实验补充 ==")
    print(f"第 7 步前放电：52.44 Hz 时 τ = {tau_rc(F_CLK2):.3f} s，10 s 后剩 {VIN*np.exp(-10/tau_rc(F_CLK2))*1e3:.1f} mV，15 s 后剩 {VIN*np.exp(-15/tau_rc(F_CLK2))*1e3:.1f} mV")
    print(f"95% 处的台阶：剩余差距 {0.05*VIN*1e3:.0f} mV ÷ 101 = {0.05*VIN*alpha()*1e3:.1f} mV")
    print(f"时钟加倍 {2*F_CLK1:.1f} Hz：R_eq = {r_eq(2*F_CLK1)/1e3:.1f} kΩ，接 1 MΩ 读 {v_rl(2*F_CLK1):.2f} V")
    print(f"C1 = 1 nF：63% {t_to(0.632, F_CLK1, 1e-9):.2f} s，95% {t_to(0.95, F_CLK1, 1e-9):.1f} s")
    print(f"表笔直接接 C2（10 MΩ）：终值 {v_rl(F_CLK1, rl=10e6):.2f} V，τ 变成 {1/(1/r_eq(F_CLK1)+1/10e6)*C2:.2f} s")
    print(f"ngspice 95% 2.84 s / 5.60 s 比计算 {t_to(0.95, F_CLK1):.3f} / {t_to(0.95, F_CLK2):.3f} s 低 {(1-2.838/t_to(0.95, F_CLK1))*100:.1f}% / {(1-5.603/t_to(0.95, F_CLK2))*100:.1f}%")
    print("== 台阶 ==")
    for ratio in (10, 100, 1000):
        print(f"C2/C1 = {ratio}：第一拍台阶 {VIN/(ratio+1)*1e3:.1f} mV，63% 要 {cycles_to(0.632, 1, ratio):.1f} 拍")
    print("== 跟踪预告 ==")
    for fs_ in (20, 50, 200):
        print(f"信号 {fs_} Hz → 时钟 {100*fs_} Hz（100:1）")
    print("== 例题与练习（教师审读后换数；答案不在正文里出现）==")
    n2 = cycles_to(0.632, C1, 2.2e-6)
    print(f"例 1：63% 要 {cycles_to(0.632):.2f} 拍 → {t_to(0.632, F_CLK1):.3f} s")
    print(f"例 2：C2 = 2.2 µF，每拍乘 220/221，63% 要 {n2:.1f} 拍 → {n2/F_CLK1:.2f} s")
    assert abs(n2 - 220.4) < 0.2 and abs(n2 / F_CLK1 - 2.11) < 0.01
    req3, tau3 = r_eq(1e3, 4.7e-9), tau_rc(1e3, 4.7e-9, 1e-6)
    st3 = VIN * alpha(4.7e-9, 1e-6)
    print(f"例 3：C1 = 4.7 nF、1 kHz、C2 = 1 µF：R_eq = {req3/1e3:.1f} kΩ，τ = {tau3:.3f} s，第一级台阶 {st3*1e3:.1f} mV")
    assert abs(req3 - 212.8e3) < 100 and abs(tau3 - 0.213) < 0.001 and abs(st3 - 0.021) < 0.0005
    t_ex1 = tau_rc(500, 10e-9, 0.47e-6)
    print(f"练习 1：C1 10 nF、C2 0.47 µF、时钟 500 Hz：R_eq = {r_eq(500)/1e3:.0f} kΩ，τ = {t_ex1*1e3:.0f} ms")
    assert abs(t_ex1 - 0.094) < 1e-6
    va, vb = v_rl(F_CLK1, rl=2.2e6), v_rl(F_CLK2, rl=2.2e6)
    print(f"练习 2：接 2.2 MΩ：{F_CLK1} Hz 读 {va:.3f} V（R_eq {r_eq(F_CLK1)/1e3:.0f} kΩ），{F_CLK2} Hz 读 {vb:.2f} V（R_eq {r_eq(F_CLK2)/1e3:.0f} kΩ）")
    assert abs(va - 3.135) < 0.001 and abs(vb - 2.41) < 0.005
    fa3 = alias(200, 2 * F_CLK1)
    print(f"练习 3：时钟 {2*F_CLK1:.1f} Hz、200 Hz 干扰 → 冒充 {fa3:.1f} Hz；前置 RC 截止 {2*F_CLK1/10:.2f} Hz 时剩 {rc_lp(200, 2*F_CLK1/10):.3f}")
    assert abs(fa3 - 8.8) < 1e-6 and abs(rc_lp(200, 20.88) - 0.104) < 0.001
    r3a, r3b = (F_CLK1 - 5) / (F_CLK1 / 10), 200 / (2 * F_CLK1 / 10)
    print(f"练习 3 补充：干扰 / 截止 = {r3a:.2f}（正文 99.4 Hz）与 {r3b:.2f}（练习 200 Hz），所以剩下的比例几乎一样")
    assert abs(r3a - 9.52) < 0.01 and abs(r3b - 9.58) < 0.01
    k50 = [50 * f for f in (50, 200)]
    print(f"练习 4（MF10 50:1 模式）：信号 50 → 200 Hz，时钟 {k50[0]} → {k50[1]} Hz（100:1 模式的一半）")
    assert k50 == [2500, 10000]
    ti1, ti2 = tau_rc(F_CLK1, C1, 0.1e-6), tau_rc(2 * F_CLK1, C1, 0.1e-6)
    print(f"练习 5（迁移，14 积分器）：输入电阻换成开关 + 10 nF，积分电容 0.1 µF：R_eq C = {ti1*1e3:.1f} ms；时钟加倍 {ti2*1e3:.1f} ms")
    assert abs(ti1 - 0.0958) < 0.0001 and abs(ti2 - 0.0479) < 0.0001
    print(f"预测题（page1）：时钟加倍 → τ = {tau_rc(2*F_CLK1):.3f} s（原来 {tau_rc(F_CLK1):.3f} s），反应更快")
    print(f"page1 带通倍数（三位）：见 34_figs 图 34-p1-1；10/11 序列：第一拍差距 {VIN*10/11:.2f} V，输出 {VIN-VIN*10/11:.2f} V")
    print(f"图 34-p3-1（横轴改秒）：C2/C1 = 10/100/1000 时 τ = " + " / ".join(f"{tau_rc(F_CLK1, C1, C1*r):.4f}" for r in (10, 100, 1000)) + " s")
