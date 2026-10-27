"""41 4–20 mA 电流环：页面里所有数字的 Python 计算。运行（仓库根目录）：
    /workspace/circuits-venv/bin/python code/41_sim.py
内容：
  1. 接收电阻上的电压、回路允许的最大电阻（XTR115 手册：V+ ≥ 7.5 V）、铜线电阻
  2. 电压传输 vs 电流传输：导线电阻造成的读数误差
  3. NAMUR NE43 分区（Beckhoff 说明页，2003 版）
  4. 实验发送器（LM358 + 2N3904 + R_S 100 Ω，12 V，接收 250 Ω）：线性区/饱和区的简化模型、β 误差、失调误差、功耗
  5. 设定电压：D9 PWM（约 490 Hz）经 12k/10k 分压 + 10 µF 滤波：analogWrite 码值、步长、纹波、建立时间
  6. Arduino 端：A0 读 R_S、A1 读运放输出（22k/10k 分压）、“余量”判断，以及接收端（万用表）的 NE43 判断
简化模型里的 V_BE、V_OH、V_CE(sat) 取自 spice/41/vi_dc.cir 的 ngspice 结果（见各常数注释），β 取 100（同一模型 20 mA 时约 98）。"""
import numpy as np

# ---------------------------------------------------------------- 常数
VS = 12.0        # 回路电源（实验用 12 V 直流适配器）
R_RX = 250.0     # 接收电阻（只用万用表量）
R_S = 100.0      # 发射极采样电阻（低边，A0 经 10 kΩ 读它）
R_B = 1e3        # 基极电阻
R1, R2, C_F = 12e3, 10e3, 10e-6   # PWM 分压 + 滤波（12k/10k：5 V 脚只有 4.83 V 时满码仍 ≥ 21 mA）
F_PWM = 490.2    # Arduino Uno D9 的 analogWrite 频率（官方 analogWrite 参考页：D9 约 490 Hz）
V5 = 5.0         # Arduino 5 V（实际以万用表量到的为准）
V_BE = 0.759     # SPICE：20 mA 时 V_B − V_E ≈ 0.759 V，4 mA 时 0.678 V → 用 vbe_of(I) 按对数插值
V_OH = 10.53     # SPICE：LM358 在 12 V 单电源、输出灌 ~9 mA 进基极时的最高输出
V_CESAT = 0.05   # 深饱和（强制 β 只有 2 左右）时的 V_CE，SPICE 0.03～0.04 V
BETA = 100.0
DIV_A1 = 10 / 32  # A1 读运放输出用 22k/10k 分压
H_LIMIT = 1.3    # “余量”= 运放输出 − 发射极电压，超过它就判回路异常（V）
XTR115_VMIN = 7.5  # XTR115 手册：V+ 最低 7.5 V


def vbe_of(I):
    """2N3904（onsemi 模型）V_BE 随电流的对数关系，两点取自 SPICE：4 mA 0.678 V、20 mA 0.759 V。"""
    return V_BE + 0.0503 * np.log(max(I, 1e-6) / 0.020)


def v_rx(I, R):
    return I * R


def r_loop_max(vsup, vmin=XTR115_VMIN, imax=0.020):
    return (vsup - vmin) / imax


def r_wire(length_m, area_mm2=0.2, rho=1.72e-8):
    """一根铜导线的电阻；回路有去、回两根，所以电缆长 L 时要乘 2。"""
    return rho * length_m / (area_mm2 * 1e-6)


# ---------------------------------------------------------------- 2. 电压 vs 电流传输
def err_voltage(rw, rin):
    """电压信号经两根导线（合计 rw）送到输入电阻 rin 的接收端：读数偏低的百分比。"""
    return rw / (rw + rin) * 100


def err_current(rw, vsup, vmin, r_rx=R_RX, iset=0.020):
    """电流环：在顺从电压内误差为 0；超出后电流被限在 (vsup − vmin)/(r_rx + rw)。"""
    i = np.minimum(iset, (vsup - vmin) / (r_rx + rw))
    return (iset - i) / iset * 100


# ---------------------------------------------------------------- 3. NE43
def ne43(I_mA):
    if I_mA <= 3.6:
        return "故障（低）"
    if I_mA <= 3.8:
        return "过渡带（NE43 表中未定义）"
    if I_mA < 20.5:
        return "测量值" if 4.0 <= I_mA <= 20.0 else "测量值（4–20 之外的超量程区）"
    if I_mA < 21.0:
        return "过渡带（NE43 表中未定义）"
    return "故障（高）"


# ---------------------------------------------------------------- 4. 发送器模型
def sender(vset, rx, beta=BETA, vbe=None, voh=V_OH):
    """返回 dict：回路电流 ic（流过 250 Ω）、发射极电流 ie（A0 读到的）、基极电流 ib、运放输出 vo、余量 h、状态。
    线性区：V_E = vset，I_C = I_E·β/(β+1)。
    饱和区：V_C ≈ V_E + V_CE(sat)，I_C = (VS − V_E − V_CE(sat))/(R_RX + rx)；运放用基极电流补足 I_E，只要运放输出够得着。
    断线：rx = inf，I_C = 0，全部 I_E 来自基极。"""
    ie = vset / R_S
    vbe = vbe_of(ie) if vbe is None else vbe
    ic = ie * beta / (beta + 1)
    vc = VS - ic * (R_RX + rx) if np.isfinite(rx) else -np.inf
    if vc - vset >= 0.3:                                   # 线性
        ib = ie - ic
        vo = vset + vbe + ib * R_B
        return dict(ic=ic, ie=ie, ib=ib, vo=vo, h=vo - vset, state="线性")
    icx = (VS - vset - V_CESAT) / (R_RX + rx) if np.isfinite(rx) else 0.0
    ib = ie - icx
    vo = vset + vbe + ib * R_B
    if vo <= voh:                                           # 运放还能把 V_E 撑在 vset
        return dict(ic=icx, ie=ie, ib=ib, vo=vo, h=vo - vset, state="饱和（A0 仍正常）" if np.isfinite(rx) else "断线（A0 仍显示设定值）")
    # 运放到顶：V_E = (I_C + I_B)·R_S，I_B = (voh − vbe − V_E)/R_B，I_C = (VS − V_E − V_CESAT)/(R_RX + rx)
    g = 0.0 if not np.isfinite(rx) else 1 / (R_RX + rx)
    # V_E·(1/R_S + 1/R_B + g) = (voh − vbe)/R_B + g·(VS − V_CESAT)
    ve = ((voh - vbe) / R_B + g * (VS - V_CESAT)) / (1 / R_S + 1 / R_B + g)
    icx = g * (VS - ve - V_CESAT)
    ib = (voh - vbe - ve) / R_B
    return dict(ic=icx, ie=ve / R_S, ib=ib, vo=voh, h=voh - ve, state="运放到顶")


def p_transistor(I, rx=0.0):
    """线性区晶体管功耗 ≈ I·V_CE，V_CE = VS − I·(R_RX + rx + R_S)。"""
    return I * (VS - I * (R_RX + rx + R_S))


# ---------------------------------------------------------------- 5. PWM 设定
K_DIV = R2 / (R1 + R2)
R_TH = R1 * R2 / (R1 + R2)
TAU = R_TH * C_F


def code_for(I_mA, v5=V5, k=K_DIV):
    return int(round(I_mA * 1e-3 * R_S / (v5 * k) * 255))


def vset_of(code, v5=V5, k=K_DIV):
    return v5 * k * code / 255


def ripple(vh, D, f, R, C):
    """理想方波（0/vh，占空 D）经 RC 后的稳态纹波峰峰值和平均值（解析解）。"""
    T = 1 / f
    tau = R * C
    a, b = np.exp(-D * T / tau), np.exp(-(1 - D) * T / tau)
    vmin = vh * (1 - a) * b / (1 - a * b)
    vmax = vh - (vh - vmin) * a
    return vmax - vmin, (vmax + vmin) / 2


# ---------------------------------------------------------------- 6. Arduino 读数
def adc(v, vref=V5):
    return int(np.clip(np.floor(v / vref * 1024), 0, 1023))


def arduino_view(r):
    """把 sender() 的结果变成 Arduino 看到的：A0 码、I_E 估算、A1 码、余量判断。"""
    n0, n1 = adc(r["ie"] * R_S), adc(r["vo"] * DIV_A1)
    ie = n0 * V5 / 1024 / R_S
    vo = n1 * V5 / 1024 / DIV_A1
    h = vo - n0 * V5 / 1024
    return dict(n0=n0, n1=n1, ie_mA=ie * 1e3, h=h, alarm=h > H_LIMIT)


def report():
    out = {}
    print("== 1. 接收电压、回路电阻上限、导线 ==")
    for I in (0.004, 0.012, 0.020):
        print(f"  {I * 1e3:.0f} mA：250 Ω 上 {v_rx(I, 250):.2f} V，100 Ω 上 {v_rx(I, 100):.2f} V")
    for v in (24, 12):
        print(f"  XTR115 在 {v} V：回路总电阻上限 (V − 7.5 V)/20 mA = {r_loop_max(v):.0f} Ω")
    rw = r_wire(1)
    print(f"  0.2 mm² 铜线：{rw * 1e3:.1f} mΩ/m；电缆 1 km（去回 2 km）= {2 * 1000 * rw:.0f} Ω")
    print(f"  24 V + XTR115 + 250 Ω：留给导线 {r_loop_max(24) - 250:.0f} Ω → 0.2 mm² 电缆最长 {(r_loop_max(24) - 250) / (2 * rw) / 1000:.2f} km")
    print(f"  12 V + XTR115：留给 250 Ω 接收电阻和导线的只有 {r_loop_max(12):.0f} Ω（< 250 Ω，驱动不了）；换 100 Ω 接收还剩 {r_loop_max(12) - 100:.0f} Ω")
    print("== 2. 电压传输误差 ==")
    for rw_ in (10, 50, round(2 * 1000 * rw), 500):
        print(f"  导线 {rw_} Ω：接 10 kΩ 输入 {err_voltage(rw_, 10e3):.2f} %，接 1 kΩ 输入 {err_voltage(rw_, 1e3):.2f} %；"
              f"电流环(24 V, XTR115) {float(err_current(rw_, 24, 7.5)):.2f} %")
    print("== 3. NE43 ==")
    for I in (0, 3.0, 3.6, 3.7, 3.9, 4.0, 12, 20, 20.3, 20.7, 21.0, 21.75):
        print(f"  {I:5.2f} mA → {ne43(I)}")
    print("== 4. 发送器 ==")
    print(f"  线性条件：VS − I·(250 + R_x) − V_E ≥ 0.3 V → 20 mA 时 R_x ≤ {(VS - 2.0 - 0.3) / 0.020 - R_RX:.0f} Ω；21 mA 时 ≤ {(VS - 2.1 - 0.3) / 0.021 - R_RX:.0f} Ω；满码 {vset_of(255) / R_S * 1e3:.2f} mA 时 ≤ {(VS - vset_of(255) - 0.3) / (vset_of(255) / R_S) - R_RX:.0f} Ω")
    for b in (60, 100, 300):
        print(f"  β={b}：回路电流比 A0 读数少 1/(β+1) = {100 / (b + 1):.2f} %")
    print(f"  LM358 失调 7 mV → {7e-3 / R_S * 1e6:.0f} µA = 量程 16 mA 的 {7e-3 / R_S / 0.016 * 100:.2f} %")
    for rx in (0.0, 100.0, 220.0, 470.0, np.inf):
        for vs in (0.4, 1.2, 2.0, 2.1):
            r = sender(vs, rx)
            a = arduino_view(r)
            print(f"  R_x={rx:>4} Ω V_SET={vs:.1f} V：回路 {r['ic'] * 1e3:6.2f} mA，A0 侧 I_E {r['ie'] * 1e3:6.2f} mA，"
                  f"I_B {r['ib'] * 1e3:5.2f} mA，运放输出 {r['vo']:5.2f} V，余量 {r['h']:4.2f} V [{r['state']}]"
                  f" → Arduino A0={a['n0']} ({a['ie_mA']:.2f} mA) A1={a['n1']} 余量 {a['h']:.2f} V {'报警' if a['alarm'] else '正常'}")
    Is = np.linspace(0, 0.022, 2201)
    P = p_transistor(Is)
    print(f"  晶体管功耗最大 {P.max() * 1e3:.1f} mW（在 {Is[np.argmax(P)] * 1e3:.1f} mA）；4 mA {p_transistor(0.004) * 1e3:.1f} mW，"
          f"20 mA {p_transistor(0.020) * 1e3:.1f} mW；250 Ω 被短接、20 mA {0.020 * (VS - 0.020 * R_S) * 1e3:.0f} mW")
    print(f"  250 Ω 功耗：20 mA {0.02 ** 2 * 250 * 1e3:.0f} mW，满码 {vset_of(255) / R_S * 1e3:.2f} mA 时 {(vset_of(255) / R_S) ** 2 * 250 * 1e3:.0f} mW；"
          f"100 Ω 在 20 mA {0.02 ** 2 * 100 * 1e3:.0f} mW")
    print("== 5. PWM 设定 ==")
    print(f"  分压比 {K_DIV:.4f}，满码 {vset_of(255):.3f} V = {vset_of(255) / R_S * 1e3:.2f} mA，步长 {vset_of(1) * 1e3:.2f} mV = {vset_of(1) / R_S * 1e6:.1f} µA")
    print(f"  戴维南电阻 {R_TH / 1e3:.2f} kΩ，τ = {TAU * 1e3:.1f} ms，到 99 % 需 {TAU * np.log(100):.2f} s")
    codes = {}
    for I in (3.4, 3.6, 4.0, 12.0, 20.0, 21.0, 22.7):
        c = code_for(I)
        codes[I] = c
        pp, _ = ripple(V5 * K_DIV, c / 255, F_PWM, R_TH, C_F)
        print(f"  {I:4.1f} mA → analogWrite({c})，实际 {vset_of(c) / R_S * 1e3:.3f} mA（回路再少 1/(β+1)：{vset_of(c) / R_S * 1e3 * BETA / (BETA + 1):.2f} mA，NE43：{ne43(vset_of(c) / R_S * 1e3 * BETA / (BETA + 1))}），纹波 {pp * 1e3:.1f} mVpp = {pp / R_S * 1e6:.0f} µApp")
    out["codes"] = codes
    print("  对比：不分压 10k + 10 µF")
    for vs in (0.4, 1.2, 2.0):
        pp, _ = ripple(5, vs / 5, F_PWM, 10e3, C_F)
        print(f"    V_SET {vs} V：纹波 {pp * 1e3:.1f} mVpp；步长 {5 / 255 / R_S * 1e3:.3f} mA；到 99 % 需 {10e3 * C_F * np.log(100):.2f} s")
    print(f"  不分压时 analogWrite(255) → V_SET 5 V，要求 50 mA；按模型实际：{sender(5.0, 0.0)['ic'] * 1e3:.1f} mA 流过 250 Ω，"
          f"250 Ω 功耗 {sender(5.0, 0.0)['ic'] ** 2 * 250 * 1e3:.0f} mW")
    print("== 6. Arduino ==")
    print(f"  A0：1 LSB = {V5 / 1024 * 1e3:.3f} mV = {V5 / 1024 / R_S * 1e6:.1f} µA")
    print(f"  A1：1 LSB 对应运放输出 {V5 / 1024 / DIV_A1 * 1e3:.1f} mV；运放最高 {V_OH} V → A1 {V_OH * DIV_A1:.2f} V；就算输出顶到 12 V 也只有 {12 * DIV_A1:.2f} V")
    print(f"  高边错误接法：250 Ω 下端对地 = {[round(VS - I * 250, 1) for I in (0.004, 0.012, 0.020)]} V，超过 ATmega 引脚上限 VCC + 0.5 V = {V5 + 0.5} V")
    print(f"  集电极–发射极短路时发射极最高 {VS / (R_RX + R_S) * R_S:.2f} V（A0 安全）")
    print(f"  A0 串 10 kΩ：就算 A0 那根线误碰 12 V，流进钳位二极管的电流 ≤ (12 − 5 − 0.5)/10k = {(VS - V5 - 0.5) / 10e3 * 1e3:.2f} mA（论坛建议 ≤ 1 mA）")
    r_pd = 100e3
    k_pd = r_pd / (r_pd + 10e3)   # V_E 被运放钉住；R_S 并在 V_E 与地之间，不在这一串里
    print(f"  A0 不会悬空：它经 10 kΩ + R_S 100 Ω 接地。若再在 A0 加 100 kΩ 下拉，会和 10 kΩ 分压：A0 只看到 {k_pd:.3f} 倍，读数偏低 {100 * (1 - k_pd):.1f} %（20 mA 显示 {20 * k_pd:.2f} mA）")
    print(f"  A1 分压的戴维南电阻 22k∥10k = {22e3 * 10e3 / 32e3 / 1e3:.2f} kΩ；A0 源阻抗 10 kΩ + 100 Ω = 10.1 kΩ（手册建议约 10 kΩ 以下）")
    print("== 7. 接收电阻能不能读到故障高电流（D2-2） ==")
    for R in (250, 220, 200, 100):
        print(f"  {R} Ω × 22.8 mA = {R * 0.0228:.2f} V；× {vset_of(255) / R_S * 1e3:.2f} mA（本节满码）= {R * vset_of(255) / R_S:.2f} V")
    for vref in (5.0, 4.83):
        print(f"  参考电压 {vref} V 时，接收电阻最大 {vref / 0.0228:.0f} Ω（读到 22.8 mA）")
    print("== 8. Arduino 5 V 不是 5.00 V（实测例 4.83 V）时 ==")
    out["v5"] = {}
    for v5 in (5.0, 4.83):
        for code in (45, 224, 255):
            I = vset_of(code, v5=v5) / R_S
            n = adc(I * R_S, vref=v5)
            shown = n * V5 / 1024 / R_S          # 程序里仍按 5.00 V 换算
            shown_ok = n * v5 / 1024 / R_S       # 程序里代入实测值
            out["v5"][(v5, code)] = (I, shown, shown_ok)
            print(f"  5V 脚 = {v5} V，analogWrite({code})：实际 I_E {I * 1e3:.2f} mA；A0 读数 {n}，按 5.00 V 换算显示 {shown * 1e3:.2f} mA，按实测值换算 {shown_ok * 1e3:.2f} mA")
    print(f"  结论：PWM 和 ADC 都以 5 V 脚为基准，误差互相抵消 → A0 自检看不出；必须用万用表测 5 V 脚，代入 V5 常数后再算 analogWrite 的值")
    print(f"  代入 4.83 V 后 20 mA 要 analogWrite({code_for(20.0, v5=4.83)})，4 mA 要 analogWrite({code_for(4.0, v5=4.83)})")
    print("== 9. 教师审读补充：例题、练习题、错误接地 ==")
    for I in (12.0, 16.0):
        c = code_for(I)
        ie = vset_of(c) / R_S
        il = ie * BETA / (BETA + 1)
        print(f"  例：{I:.0f} mA → V_SET {I * 1e-3 * R_S:.2f} V，码 {I * 1e-3 * R_S / (V5 * K_DIV) * 255:.1f} → {c}，实际 V_SET {vset_of(c):.3f} V、I_E {ie * 1e3:.2f} mA，回路 {il * 1e3:.2f} mA，250 Ω 上 {il * 250:.2f} V")
    c8 = code_for(8.0, v5=4.83)
    print(f"  例 3：5 V 脚 4.83 V，8 mA → 码 {0.8 / (4.83 * K_DIV) * 255:.1f} → {c8}，实际 {vset_of(c8, v5=4.83) / R_S * 1e3:.2f} mA；3.00 V ÷ 250 Ω = {3.0 / 250 * 1e3:.1f} mA → {(3.0 / 250 * 1e3 - 4) / 16 * 100:.0f} %")
    print(f"  练习 1：12 mA 时 R_x ≤ (12 − 1.2 − 0.3)/0.012 − 250 = {(VS - 1.2 - 0.3) / 0.012 - R_RX:.0f} Ω")
    rs2 = 50.0
    c50 = int(round(1.0 / (V5 * K_DIV) * 255))
    ie_full = vset_of(255) / rs2
    ic_sat = (VS - vset_of(255) - V_CESAT) / R_RX
    ib_sat = ie_full - ic_sat
    vo_sat = vset_of(255) + vbe_of(ie_full) + ib_sat * R_B
    print(f"  练习 2：R_S 50 Ω，20 mA 要码 {c50}；顺从极限 {(VS - 1.0 - 0.3) / 0.020 - R_RX:.0f} Ω；每码 {vset_of(1) / rs2 * 1e6:.0f} µA；"
          f"满码要 {ie_full * 1e3:.1f} mA，管子饱和后回路 {ic_sat * 1e3:.1f} mA（运放输出需 {vo_sat:.2f} V < {V_OH} V，撑得住），"
          f"250 Ω 功耗 {ic_sat ** 2 * R_RX:.3f} W，R_S 功耗 {ie_full ** 2 * rs2:.3f} W")
    lsb = V5 / 1024
    print(f"  练习 3：R_S 10 Ω、20 mA → 0.2 V ÷ {lsb * 1e3:.3f} mV = {0.2 / lsb:.2f} 格（ADC 取整读 {adc(0.2)}）；100 Ω 时 {2.0 / lsb:.1f} 格（读 {adc(2.0)}）；"
          f"顺从极限 {(VS - 0.2 - 0.3) / 0.020 - R_RX:.0f} Ω")
    rw5 = r_wire(1, area_mm2=0.5)
    print(f"  练习 4：0.5 mm² 铜线 {rw5 * 1e3:.1f} mΩ/m，两芯 {2 * rw5 * 1e3:.1f} mΩ/m；24 V 留给导线 {r_loop_max(24) - 250:.0f} Ω → {(r_loop_max(24) - 250) / (2 * rw5) / 1000:.2f} km")
    print(f"  page1：(24 − 5 − 7.5)/0.02 = {r_loop_max(24) - 250:.0f} Ω；÷ {2 * 1000 * r_wire(1):.0f} Ω/km = {(r_loop_max(24) - 250) / (2 * 1000 * r_wire(1)):.2f} km")
    ig = VS / (R_RX + 470)
    print(f"  错误接地（集电极接 0 V，R_x = 470 Ω）：I = 12/(470+250) = {ig * 1e3:.2f} mA，250 Ω 上 {ig * 250:.2f} V（与设定无关），"
          f"250 Ω {ig ** 2 * 250 * 1e3:.0f} mW，R_x {ig ** 2 * 470 * 1e3:.0f} mW；R_x = 0 时会是 {VS / R_RX * 1e3:.0f} mA、{VS ** 2 / R_RX:.2f} W（所以只在 470 Ω 时做）")
    print(f"  纹波估算：码 135，{vset_of(255):.3f} × {135 / 255:.3f} × {1 - 135 / 255:.3f} × {1e3 / F_PWM:.2f} ms / {TAU * 1e3:.1f} ms = "
          f"{vset_of(255) * (135 / 255) * (1 - 135 / 255) / F_PWM / TAU * 1e3:.1f} mV → {vset_of(255) * (135 / 255) * (1 - 135 / 255) / F_PWM / TAU / R_S * 1e6:.0f} µA；f_c = {1 / (2 * np.pi * TAU):.2f} Hz")
    print(f"  12 V 实际偏低时 20 mA 顺从极限：11.5 V → {(11.5 - 2.0 - 0.3) / 0.02 - R_RX:.0f} Ω，11.7 V → {(11.7 - 2.0 - 0.3) / 0.02 - R_RX:.0f} Ω")
    print(f"  470 Ω/20 mA A1：V_O = 2.002 + 6.97 = {2.002 + 6.97:.2f} V → A1 {adc((2.002 + 6.97) * DIV_A1)} 格")
    return out


if __name__ == "__main__":
    report()
