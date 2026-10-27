"""37 过零检测与超声波时差：本节所有数值的出处。
运行（仓库根目录）：/workspace/circuits-venv/bin/python code/37_sim.py
页面上的每个数字都由本脚本打印，关键结论用 assert 检查。图由 code/figs/37_figs.py 画，它会 import 本文件。

实验电路（page4，图 37-p2-2）：
  发射：Arduino D3、D11 各串 150 Ω 接 MA40S4S 两脚，程序按 Timer1 的节拍让两脚反相翻转，8 个周期 40 kHz（±5 V，10 Vp-p）。
  接收：MA40S4R 一脚接 V_MID（12 V 经 10k/10k 分压 + TL072 A 跟随 = 6 V），另一脚接 TL072 B 的 5 脚，100k 偏置到 V_MID；
        TL072 B 同相放大 11 倍（Rf 100k，Rg 10k + Cg 100 nF 到 V_MID）。
  武装：LM393 A，IN− = 放大输出，IN+ = 门限 V_TH（12 V—100k—10k 电位器—V_MID，比 V_MID 高 0～0.55 V）。
  过零：LM393 B，IN+ = 放大输出经 10k，回差电阻 4.7 MΩ；IN− = V_MID 经 10k。两只 LM393 输出各 2.2k 上拉到 Arduino 5 V。
  逻辑：SN74HC74（Arduino 5 V 供电）。FF1：/PRE1 = 武装输出，D1、CLK1 接地，Q1 → D2；FF2：CLK2 = 过零输出，/PRE2 接 5 V；
        两个 /CLR 接 Arduino D4；Q2 → D8（Timer1 输入捕获 ICP1）；/Q2 是万用表测点。
回波模型（8 周期方波经发射、接收两个 Q = 15 的谐振）只是示意：Q 值数据手册没给，结论只依赖「整周期跳变」这一点。
"""
import math
import numpy as np
from scipy.signal import lfilter

# ---------------------------------------------------------------- 声速与传播时间
def c_air(theta):
    """空气声速，Wikipedia《Speed of sound》：331.32·√(1 + θ/273.15) m/s。"""
    return 331.32 * math.sqrt(1 + theta / 273.15)


TH0 = 20.0
C0 = c_air(TH0)
L0 = 0.20
T0 = L0 / C0
SLOPE = {th: 1e-3 / c_air(th) * 1e6 for th in (15, 20, 25, 30)}     # µs/mm
assert abs(C0 - 343.24) < 0.01 and abs(T0 * 1e6 - 582.69) < 0.01
assert abs(SLOPE[20] - 2.913) < 1e-3 and abs(SLOPE[15] - 2.939) < 1e-3 and abs(SLOPE[30] - 2.865) < 1e-3


def tof(L, c, v=0.0):
    """顺流 t1 = L/(c+v)，逆流 t2 = L/(c−v)。"""
    return L / (c + v), L / (c - v)


def v_from_t(L, t1, t2):
    """SLAAES9 式 4：v = (L/2)(1/t1 − 1/t2)，不需要知道 c。"""
    return L / 2 * (1 / t1 - 1 / t2)


V_FAN = 3.0
T1, T2 = tof(L0, C0, V_FAN)
DT = T2 - T1
DT_APPROX = 2 * L0 * V_FAN / C0 ** 2
ONEWAY = L0 * V_FAN / C0 ** 2                       # 风扇开/关，单向的变化
assert abs(DT * 1e6 - 10.19) < 0.01 and abs(DT_APPROX * 1e6 - 10.19) < 0.01 and abs(ONEWAY * 1e6 - 5.09) < 0.01
assert abs(v_from_t(L0, T1, T2) - V_FAN) < 1e-9
TEMPCO = (L0 / c_air(20.5) - L0 / c_air(19.5)) * 1e6  # µs/°C
assert abs(TEMPCO + 0.994) < 0.001
DT_TABLE = {v: (tof(L0, C0, v)[1] - tof(L0, C0, v)[0]) * 1e6 for v in (1, 2, 3, 5)}
assert abs(DT_TABLE[1] - 3.40) < 0.01 and abs(DT_TABLE[5] - 16.98) < 0.01
# 一阵 3 m/s 的风，c 变 1 °C：用 Δt·c²/(2L) 算 v，c 取错 1 °C 的误差
V_WRONG_C = DT * c_air(21) ** 2 / (2 * L0)

# 水：L = 0.1 m，c = 1481 m/s（20 °C 淡水）
CW, LW = 1481.0, 0.10
DT_W1 = 2 * LW * 1.0 / CW ** 2
DT_W001 = 2 * LW * 0.01 / CW ** 2
TW = LW / CW
assert abs(DT_W1 * 1e9 - 91.2) < 0.05 and abs(DT_W001 * 1e9 - 0.912) < 0.001
TDC7200 = 55e-12
T_ARD = 1 / 16e6
assert abs(T_ARD * 1e9 - 62.5) < 1e-9
RATIO_RES = T_ARD / TDC7200                           # 约 1136 倍

# ---------------------------------------------------------------- Arduino 计时
F_CPU = 16e6
F_TX = 40e3
T_CAR = 1 / F_TX
HALF_TICKS = int(F_CPU / F_TX / 2)                    # 每半个周期 200 个滴答
N_CYC = 8
T_BURST = N_CYC * T_CAR
T_BLANK = 350e-6
BLANK_TICKS = int(T_BLANK * F_CPU)
T_REP = 5e-3
REP_TICKS = int(T_REP * F_CPU)
OVF = 65536 / F_CPU
assert HALF_TICKS == 200 and BLANK_TICKS == 5600 and REP_TICKS == 80000 and REP_TICKS - 65536 == 14464
assert abs(T_BURST - 200e-6) < 1e-12 and abs(OVF * 1e3 - 4.096) < 1e-9
COUNTS_T0 = T0 * F_CPU
assert round(COUNTS_T0) == 9323
L_MIN_BLANK = T_BLANK * C0                            # 首达时间等于盲区结束时的间距
OCR2A = F_CPU / (2 * F_TX) - 1                        # 若改用 Timer2 CTC 翻转（变体）
assert OCR2A == 199

# ---------------------------------------------------------------- 发射驱动
C_TR = 2550e-12
V_PIN = 5.0
V_DIFF = 2 * V_PIN                                    # 两脚反相：±5 V，10 Vp-p
VPP_MAX = 20.0                                        # MA40S4S 最大 20 Vp-p
I_PIN_MAX = 40e-3


def drive(rs):
    """一次反相翻转电容两端变化 10 V；两只串联电阻共 2rs。返回 峰值电流、τ、40 kHz 基波保留。"""
    rt = 2 * rs
    ipk = V_DIFF / rt
    tau = rt * C_TR
    keep = 1 / math.sqrt(1 + (2 * math.pi * F_TX * tau) ** 2)
    return ipk, tau, keep


IPK150, TAU150, KEEP150 = drive(150)
IPK100, _, _ = drive(100)
I_AVG = 2 * C_TR * V_DIFF * F_TX
XC40 = 1 / (2 * math.pi * F_TX * C_TR)
assert abs(IPK150 * 1e3 - 33.3) < 0.05 and abs(TAU150 * 1e6 - 0.765) < 0.001 and abs(KEEP150 - 0.982) < 0.001
assert IPK100 >= I_PIN_MAX and IPK150 < I_PIN_MAX
assert abs(I_AVG * 1e3 - 2.04) < 0.01 and abs(XC40 - 1560) < 1
assert V_DIFF < VPP_MAX and 2 * 12 > VPP_MAX            # 12 V H 桥是 24 Vp-p，超标
I_AVG_BURST = I_AVG * T_BURST / T_REP                 # 每 5 ms 只发 200 µs

# ---------------------------------------------------------------- 接收链
VS = 12.0
V_MID = VS * 10 / 20
GAIN = 1 + 100e3 / 10e3
GBW_TL072 = 3e6
G40 = GAIN / math.sqrt(1 + (GAIN * F_TX / GBW_TL072) ** 2)
F_HP_IN = 1 / (2 * math.pi * 100e3 * C_TR)
F_HP_G = 1 / (2 * math.pi * 10e3 * 100e-9)


def hp(f, fc):
    return (f / fc) / math.sqrt(1 + (f / fc) ** 2)


def gain_stage(f):
    """同相放大，Rg 串 Cg：|1 + Rf/(Rg + 1/jωCg)|。"""
    z = 10e3 + 1 / (1j * 2 * math.pi * f * 100e-9)
    return abs(1 + 100e3 / z)


H50 = hp(50, F_HP_IN) * gain_stage(50)
H40K = hp(F_TX, F_HP_IN) * gain_stage(F_TX)
assert abs(V_MID - 6.0) < 1e-12 and GAIN == 11
assert abs(G40 - 10.88) < 0.01 and abs(F_HP_IN - 624) < 1 and abs(F_HP_G - 159) < 1
assert abs(H40K - 11.0) < 0.01 and abs(H50 - 0.274) < 0.001
SUPPRESS_50 = H40K / H50                               # 40 kHz 比 50 Hz 多放大的倍数
# TL072（经典）共模输入下限 = V− + 4 V（±15 V 表 VCM 最小 ±11 V）
CM_LOW = 4.0
MARGIN = {vs: vs / 2 - CM_LOW for vs in (9.0, 12.0)}
assert MARGIN[9.0] == 0.5 and MARGIN[12.0] == 2.0
# LM393 共模上限 VCC − 1.5 V（25 °C）/ VCC − 2 V（全温度）
LM_CM_MAX = (VS - 1.5, VS - 2.0)
# LM358 压摆率 0.3 V/µs 在 40 kHz 下不失真的最大峰值
LM358_PK = 0.3e6 / (2 * math.pi * F_TX)
assert abs(LM358_PK - 1.19) < 0.01

# 门限电位器：12 V —— 100k —— 10k 电位器 —— V_MID
I_POT = (VS - V_MID) / 110e3
VTH_SPAN = I_POT * 10e3
assert abs(VTH_SPAN - 0.545) < 0.001

# 过零比较器回差：IN+ 经 10k 接信号，4.7 MΩ 接输出（低 ≈ 0.1 V，高 ≈ 5 V）；IN− 经 10k 接 V_MID
R_IN, R_HY = 10e3, 4.7e6
V_OL, V_OH = 0.1, 5.0


def zc_thresholds(r_hy=R_HY, vref=V_MID, vol=V_OL, voh=V_OH):
    k = R_IN / (R_IN + r_hy)
    up = (vref - k * vol) / (1 - k)       # 输出为低时，信号要升过它
    dn = (vref - k * voh) / (1 - k)       # 输出为高时，信号要降过它
    return up - vref, dn - vref


ZC_UP, ZC_DN = zc_thresholds()
ZC_UP_1M, ZC_DN_1M = zc_thresholds(1e6)
assert abs(ZC_UP * 1e3 - 12.5) < 0.1 and abs(ZC_DN * 1e3 - 2.1) < 0.1
assert abs((ZC_UP - ZC_DN) * 1e3 - 10.4) < 0.1
assert abs(ZC_UP_1M * 1e3 - 59.0) < 0.1

# 74HC74（SCLS094F，4.5 V）：VIH ≥ 3.15 V，建立时间 20 ns，CLK→Q 典型 20 ns、最大 35 ns；输入沿 ≤ 500 ns
HC_VIH, HC_SETUP, HC_TPD, HC_TPD_MAX, HC_EDGE = 3.15, 20e-9, 20e-9, 35e-9, 500e-9
R_PU = 2.2e3
I_PU = 5.0 / R_PU
TAU_PU = R_PU * 20e-12                   # 上拉 2.2k、约 20 pF（估算）
assert 2.2 * TAU_PU < HC_EDGE and I_PU < 6e-3

# ---------------------------------------------------------------- 回波模型（示意，Q = 15 是假设）
FS = 8e6
Q_TR = 15.0
A_NOM = 0.50              # 放大后回波最大峰值（示意值，用来定门限的位置；真实值以实测为准）


def _bp(x, f0=F_TX, q=Q_TR):
    w0 = 2 * math.pi * f0 / FS
    al = math.sin(w0) / (2 * q)
    b = np.array([al, 0, -al]) / (1 + al)
    a = np.array([1 + al, -2 * math.cos(w0), 1 - al]) / (1 + al)
    return lfilter(b, a, x)


_N = int(2.5e-3 * FS)
T_AX = np.arange(_N) / FS
_burst = np.where(T_AX < T_BURST, np.sign(np.sin(2 * np.pi * F_TX * T_AX + 1e-9)), 0.0)
_shape = _bp(_bp(_burst))
_shape /= np.max(np.abs(_shape))


def echo(L=L0, gain=1.0, theta=TH0, v=0.0, a=A_NOM, spread=True):
    """放大器输出相对 V_MID 的回波（V）：延迟 L/(c+v)，幅度按 1/距离（以 0.2 m 为 1）× gain × a。"""
    d = int(round(L / (c_air(theta) + v) * FS))
    y = np.zeros(_N)
    y[d:] = _shape[:_N - d]
    k = (L0 / L) if spread else 1.0
    return y * a * gain * k


def peaks(sig, L=L0, theta=TH0, n=20):
    d = int(round(L / c_air(theta) * FS))
    per = int(FS / F_TX)
    return np.array([sig[d + k * per: d + (k + 1) * per].max() for k in range(n)])


PK = peaks(echo()) / A_NOM
THR_REL = 0.5 * (PK[3] + PK[4])
V_TH = THR_REL * A_NOM                       # 门限比 V_MID 高多少（示意）
LO_OK, HI_OK = THR_REL / PK[4], THR_REL / PK[3]
assert abs(THR_REL - 0.338) < 0.001 and abs(LO_OK - 0.834) < 0.002 and abs(HI_OK - 1.249) < 0.002
assert int(np.argmax(PK)) == 10 and PK[8] > 0.9         # 包络第 9～11 个周期升到顶


def thr_time(sig, thr, t_from=T_BLANK):
    i0 = int(t_from * FS)
    idx = np.nonzero(sig[i0:] > thr)[0]
    return None if len(idx) == 0 else (i0 + idx[0]) / FS


def armed_zc(sig, thr, up=ZC_UP, dn=ZC_DN, t_from=T_BLANK):
    """74HC74 两级逻辑：先等信号超过门限（武装），再等过零比较器的下一个上升沿（带回差）。"""
    ta = thr_time(sig, thr, t_from)
    if ta is None:
        return None
    i = int(ta * FS)
    high = sig[i] > up                    # 武装时刻在正峰附近，比较器为高
    for j in range(i + 1, len(sig)):
        if high and sig[j] < dn:
            high = False
        elif (not high) and sig[j] > up:
            # 线性插值到穿越 up 的时刻
            f = (up - sig[j - 1]) / (sig[j] - sig[j - 1])
            return (j - 1 + f) / FS
    return None


GAINS = (0.5, 0.7, 1.0, 1.4, 2.0)
T_THR = {g: thr_time(echo(gain=g, spread=False), V_TH) for g in GAINS}
T_ZC = {g: armed_zc(echo(gain=g, spread=False), V_TH) for g in GAINS}
_dz = [T_ZC[g] * 1e6 for g in GAINS]
assert abs(_dz[0] - _dz[1] - 25) < 0.2 and abs(_dz[1] - _dz[2] - 25) < 0.2 and abs(_dz[2] - _dz[3] - 25) < 0.2
assert abs(_dz[3] - _dz[4]) < 0.15
T_ZC_NOM = T_ZC[1.0]
OFFSET = T_ZC_NOM - T0                      # 首达之外多出来的固定时间
assert 120e-6 < OFFSET < 130e-6
# 在同一个武装周期里，幅度 ×0.9 / ×1.1 时过零时刻的微小移动（回差 12.5 mV 带来的相位偏移）
T_ZC_09 = armed_zc(echo(gain=0.9, spread=False), V_TH)
T_ZC_11 = armed_zc(echo(gain=1.1, spread=False), V_TH)
ZC_SHIFT = abs(T_ZC_09 - T_ZC_11)
T_THR_SHIFT = abs(thr_time(echo(gain=0.9, spread=False), V_TH) - thr_time(echo(gain=1.1, spread=False), V_TH))
assert ZC_SHIFT < 0.1e-6 and T_THR_SHIFT > 1.2e-6

# 门限扫描：V_TH 从 0.05 V 到 0.50 V，看 t 怎样一台阶一台阶地跳
VTH_SCAN = np.round(np.arange(0.04, 0.505, 0.01), 3)
T_SCAN = np.array([np.nan if (x := armed_zc(echo(), vt)) is None else x for vt in VTH_SCAN])
STEPS = np.diff(T_SCAN[~np.isnan(T_SCAN)]) * 1e6
assert np.all((np.abs(STEPS) < 0.2) | (np.abs(STEPS - 25) < 0.2))

# 改间距：幅度按 1/距离 变
L_SET = (0.17, 0.19, 0.21, 0.23)
T_L = np.array([armed_zc(echo(L=L), V_TH) for L in L_SET])
FIT = np.polyfit(np.array(L_SET) * 1e3, T_L * 1e6, 1)
assert abs(FIT[0] - SLOPE[20]) < 0.005 and abs(FIT[1] - OFFSET * 1e6) < 1.0   # 回波延迟按 8 MHz 取整，单点差 ≤ 0.13 µs
C_FROM_SLOPE = 1e3 / FIT[0]
L_WIDE = (0.10, 0.12, 0.15, 0.20, 0.25, 0.30)
T_WIDE = {L: armed_zc(echo(L=L), V_TH) for L in L_WIDE}
RES_WIDE = {L: (T_WIDE[L] - (L / C0 + OFFSET)) * 1e6 for L in L_WIDE}
assert abs(RES_WIDE[0.15] + 25) < 0.3 and abs(RES_WIDE[0.30] - 25) < 0.3 and abs(RES_WIDE[0.25] - 25) < 0.3 and abs(RES_WIDE[0.20]) < 0.01
assert abs(RES_WIDE[0.12] + 25) < 0.3 and abs(RES_WIDE[0.10] + 25) < 0.3   # 再近，幅度已到 ×2，最早只能在第 4 个周期武装

# 风扇：顺风、逆风、关
T_OFF = armed_zc(echo(), V_TH)
T_DOWN = armed_zc(echo(v=V_FAN), V_TH)
T_UP = armed_zc(echo(v=-V_FAN), V_TH)
DT_MEAS = T_UP - T_DOWN
V_EST = DT_MEAS * C_FROM_SLOPE ** 2 / (2 * L0)
assert abs(DT_MEAS * 1e6 - 10.19) < 0.15 and abs(V_EST - 3.0) < 0.05
V_EST_2T = v_from_t(L0, T_DOWN - OFFSET, T_UP - OFFSET)        # 先减掉固定偏移，再用 SLAAES9 两时间法
assert abs(V_EST_2T - 3.0) < 0.05

# ---------------------------------------------------------------- 万用表核对：/Q2 的平均电压
V5 = 5.00


def vq_avg(tq, v5=V5, trep=T_REP):
    """/Q2 从每轮开始（清零）到捕获时刻为高，其余为低：平均值 = V5·tq/T_rep。"""
    return v5 * tq / trep


VQ_NOM = vq_avg(T_ZC_NOM)
VQ_PER_MM = vq_avg(SLOPE[20] * 1e-6 * 1e-3 * 1e3) * 1e3 / 1e3     # mV/mm
MV_PER_US = vq_avg(1e-6) * 1e3
assert abs(MV_PER_US - 1.0) < 1e-12 and abs(VQ_PER_MM * 1e3 - 2.913) < 0.001
VQ_FAN = vq_avg(ONEWAY) * 1e3
VQ_MISS = V5                                                   # 一次也没捕获到：/Q2 一直为高

# ---------------------------------------------------------------- 练习题用的数（与正文的数故意不同）
EX_L15_V2 = (tof(0.15, C0, 2.5)[1] - tof(0.15, C0, 2.5)[0]) * 1e6          # µs
EX_W05 = 2 * 0.05 * 0.5 / CW ** 2 * 1e9                                     # ns
EX_SLIP_V = 25e-6 * C0 ** 2 / (2 * L0)                                       # 跳一个周期 → 冒出的风速
EX_T25 = 0.25 / C0 * 1e6
EX_ICR25 = (0.25 / C0 + OFFSET) * F_CPU
EX_HY22 = zc_thresholds(2.2e6)
EX_SPAN47 = (VS - V_MID) / (47e3 + 10e3) * 10e3
EX_REP10_TICKS = int(10e-3 * F_CPU)
EX_MV_US_10 = vq_avg(1e-6, trep=10e-3) * 1e3
EX_I120, EX_I180 = drive(120)[0] * 1e3, drive(180)[0] * 1e3
EX_T30 = L0 / c_air(30) * 1e6
EX_VQ30_SHIFT = vq_avg((L0 / c_air(30) - L0 / C0)) * 1e3
EX_G08 = armed_zc(echo(gain=0.8, spread=False), V_TH) * 1e6
EX_VTH_HALF = 0.5 * (PK[3] + PK[4]) * A_NOM * 0.5
EX_G05_RECENTER = armed_zc(echo(gain=0.5, spread=False), EX_VTH_HALF) * 1e6
EX_T15_SPACING = armed_zc(echo(L=0.15), V_TH) * 1e6
assert abs(EX_L15_V2 - 6.37) < 0.01 and abs(EX_SLIP_V - 7.36) < 0.01
assert EX_REP10_TICKS == 160000 and abs(EX_MV_US_10 - 0.5) < 1e-12 and EX_I120 > 40 and EX_I180 < 40
assert abs(EX_G08 - 732.8) < 0.2 and abs(EX_G05_RECENTER - T_ZC_NOM * 1e6) < 0.3

# ---------------------------------------------------------------- 打印
if __name__ == "__main__":
    print(f"[数值] c(20 °C) = {C0:.2f} m/s；L = 0.20 m → t = {T0*1e6:.2f} µs = {COUNTS_T0:.0f} 个 62.5 ns 计数")
    for th in (15, 20, 25, 30):
        print(f"[数值] {th} °C：c = {c_air(th):.2f} m/s，每 1 mm 声程 {SLOPE[th]:.3f} µs，0.2 m → {L0/c_air(th)*1e6:.2f} µs")
    for v, d in DT_TABLE.items():
        print(f"[数值] v = {v} m/s：Δt = {d:.2f} µs")
    print(f"[数值] v = 3 m/s：t1 = {T1*1e6:.2f} µs，t2 = {T2*1e6:.2f} µs，Δt = {DT*1e6:.2f} µs（近似 {DT_APPROX*1e6:.2f}），单向变化 {ONEWAY*1e6:.2f} µs")
    print(f"[数值] 温度系数 {TEMPCO:.3f} µs/°C；c 取错 1 °C 时算出 v = {V_WRONG_C:.3f} m/s")
    print(f"[数值] 水 L = 0.1 m：t = {TW*1e6:.2f} µs；1 m/s → {DT_W1*1e9:.1f} ns；1 cm/s → {DT_W001*1e9:.3f} ns；Arduino 62.5 ns / TDC7200 55 ps = {RATIO_RES:.0f} 倍")
    print(f"[数值] 半周期 {HALF_TICKS} 滴答；猝发 {T_BURST*1e6:.0f} µs；盲区 {T_BLANK*1e6:.0f} µs = {BLANK_TICKS} 滴答（声走 {L_MIN_BLANK*100:.1f} cm）；一轮 {REP_TICKS} 滴答，溢出 {OVF*1e3:.3f} ms")
    print(f"[数值] 发射 150 Ω：峰值 {IPK150*1e3:.1f} mA，τ {TAU150*1e6:.2f} µs，基波保留 {KEEP150:.3f}；100 Ω：{IPK100*1e3:.0f} mA；平均 {I_AVG*1e3:.2f} mA（猝发期间），每 5 ms 平均 {I_AVG_BURST*1e3:.3f} mA；容抗 {XC40:.0f} Ω")
    print(f"[数值] V_MID {V_MID:.1f} V；增益 {GAIN:.0f}，40 kHz 实际 {G40:.2f}（GBW 3 MHz）；高通 {F_HP_IN:.0f} Hz / {F_HP_G:.0f} Hz；50 Hz 总增益 {H50:.4f}，40 kHz {H40K:.3f}，相差 {SUPPRESS_50:.0f} 倍")
    print(f"[数值] TL072 共模余量：9 V {MARGIN[9.0]:.1f} V，12 V {MARGIN[12.0]:.1f} V；LM393 共模上限 {LM_CM_MAX[0]:.1f}/{LM_CM_MAX[1]:.1f} V；LM358 40 kHz 最大峰值 {LM358_PK:.2f} V")
    print(f"[数值] 门限电位器：V_TH − V_MID 可调 0～{VTH_SPAN:.3f} V（电流 {I_POT*1e6:.1f} µA）")
    print(f"[数值] 过零比较器 4.7 MΩ：上升门限 +{ZC_UP*1e3:.1f} mV，下降 +{ZC_DN*1e3:.1f} mV，回差 {(ZC_UP-ZC_DN)*1e3:.1f} mV；若用 1 MΩ：+{ZC_UP_1M*1e3:.1f} / +{ZC_DN_1M*1e3:.1f} mV")
    print(f"[数值] 上拉 2.2k：灌电流 {I_PU*1e3:.2f} mA，上升沿 τ ≈ {TAU_PU*1e9:.0f} ns")
    print("[数值] 各周期正峰（归一化）：" + " ".join(f"{p:.3f}" for p in PK[:14]))
    print(f"[数值] 门限 = 第 4、5 峰中点 {THR_REL:.3f}（× {A_NOM} V = {V_TH*1e3:.0f} mV）；不跳周期 ×{LO_OK:.2f} … ×{HI_OK:.2f}")
    for g in GAINS:
        print(f"[数值] 幅度 ×{g}：幅度门限 {T_THR[g]*1e6:.2f} µs | 武装 + 过零 {T_ZC[g]*1e6:.2f} µs")
    print(f"[数值] ×0.9 → ×1.1：过零时刻移动 {ZC_SHIFT*1e9:.0f} ns，幅度门限移动 {T_THR_SHIFT*1e6:.2f} µs；固定偏移 {OFFSET*1e6:.1f} µs")
    print("[数值] 门限扫描：" + "，".join(f"{vt:.2f}→{'—' if np.isnan(t) else f'{t*1e6:.1f}'}" for vt, t in zip(VTH_SCAN, T_SCAN)))
    print("[数值] 间距 " + "，".join(f"{L*100:.0f} cm→{t*1e6:.2f} µs" for L, t in zip(L_SET, T_L)) + f"；斜率 {FIT[0]:.4f} µs/mm，截距 {FIT[1]:.1f} µs，c = {C_FROM_SLOPE:.1f} m/s")
    print("[数值] 大范围改间距的残差：" + "，".join(f"{L*100:.0f} cm {r:+.1f} µs" for L, r in RES_WIDE.items()))
    print(f"[数值] 风扇 3 m/s：关 {T_OFF*1e6:.2f}，顺 {T_DOWN*1e6:.2f}，逆 {T_UP*1e6:.2f} µs；Δt {DT_MEAS*1e6:.2f} µs → v = {V_EST:.3f} m/s；两时间法 {V_EST_2T:.3f} m/s")
    print(f"[数值] /Q2 平均：{VQ_NOM:.4f} V；每 1 µs {MV_PER_US:.1f} mV，每 1 mm {VQ_PER_MM*1e3:.3f} mV，风扇单向 {VQ_FAN:.2f} mV；没捕获到读 {VQ_MISS:.2f} V")
    print(f"[练习] L = 0.15 m、v = 2.5 m/s：Δt = {EX_L15_V2:.2f} µs；水 L = 0.05 m、v = 0.5 m/s：{EX_W05:.1f} ns；跳一个周期相当于 v = {EX_SLIP_V:.2f} m/s")
    print(f"[练习] L = 0.25 m：首达 {EX_T25:.2f} µs，ICR1 约 {EX_ICR25:.0f}；R_HY 2.2 MΩ：+{EX_HY22[0]*1e3:.1f} / +{EX_HY22[1]*1e3:.1f} mV；100k 换 47k：V_TH 可调 0～{EX_SPAN47:.3f} V")
    print(f"[练习] 一轮 10 ms：{EX_REP10_TICKS} 滴答，每 1 µs {EX_MV_US_10:.1f} mV；120 Ω {EX_I120:.1f} mA，180 Ω {EX_I180:.1f} mA")
    print(f"[练习] 30 °C、0.2 m：{EX_T30:.2f} µs，/Q2 变 {EX_VQ30_SHIFT:.2f} mV；幅度 ×0.8：{EX_G08:.2f} µs；幅度 ×0.5 门限减半到 {EX_VTH_HALF*1e3:.1f} mV：{EX_G05_RECENTER:.2f} µs；15 cm：{EX_T15_SPACING:.2f} µs")

    # ------------------------------------------------------------ 首审修改（教师、学生 1）用到的数
    # page1「先算一遍」+ page2 例 0（渐隐）
    V_FADE = 6.8e-6 * C0 ** 2 / (2 * L0)
    V_FADE_2T = v_from_t(L0, 579.6e-6, 586.4e-6)
    assert abs(V_FADE - 2.00) < 0.01 and abs(V_FADE_2T - 2.0) < 0.05
    print(f"[首审] 例 0：Δt = 6.8 µs → v = {V_FADE:.2f} m/s；两时间法 t1 579.6 / t2 586.4 µs → v = {V_FADE_2T:.2f} m/s")
    # page1 练习 3：顺风那次晚 25 µs，近似式与两时间法
    EX3_V_2T = v_from_t(L0, T0 + 25e-6, T0)
    assert abs(EX3_V_2T + 7.06) < 0.01
    print(f"[首审] 练习 3：Δt = −25 µs → 近似式 −{EX_SLIP_V:.2f} m/s；两时间法 {EX3_V_2T:.2f} m/s")
    # page2：武装到捕获的时间，和 3/4 周期比
    T_ARM_NOM = T_THR[1.0]
    ARM_TO_CAP = (T_ZC_NOM - T_ARM_NOM) * 1e6
    assert abs(ARM_TO_CAP - 21.04) < 0.05 and abs(0.75 * T_CAR * 1e6 - 18.75) < 1e-9
    print(f"[首审] 武装 {T_ARM_NOM*1e6:.2f} µs → 捕获 {T_ZC_NOM*1e6:.2f} µs：相隔 {ARM_TO_CAP:.2f} µs（3/4 周期 {0.75*T_CAR*1e6:.2f} µs）")
    # page2：ICR1
    ICR_NOM = T_ZC_NOM * F_CPU
    print(f"[首审] 例 1：ICR1 ≈ {ICR_NOM:.0f}（只算首达 {COUNTS_T0:.0f}）")
    # page3 换数的练习：×1.3、13 cm
    EX_G13 = armed_zc(echo(gain=1.3, spread=False), V_TH) * 1e6
    EX_T13 = armed_zc(echo(L=0.13), V_TH) * 1e6
    EX_T13_LIN = (0.13 / C0 + OFFSET) * 1e6
    EX_G14 = armed_zc(echo(gain=1.4, spread=False), V_TH) * 1e6   # page3 练习 2：图 p3-2 平台上标的是 ×1.4
    assert abs(EX_G14 - 682.78) < 0.01 and 0.01 < EX_G13 - EX_G14 < 0.025
    print(f"[r2] 练习 2：×1.3 {EX_G13:.3f} µs，×1.4 {EX_G14:.3f} µs，相差 {EX_G13 - EX_G14:.3f} µs（一格 62.5 ns）")
    assert abs(ARM_TO_CAP - 0.75 * T_CAR * 1e6 - 2.3) < 0.05          # page2：武装约在峰前 2.3 µs
    assert abs(EX_G13 - 682.80) < 0.01 and abs(EX_T13 - EX_T13_LIN + 25) < 0.3
    print(f"[首审] 幅度 ×1.3：{EX_G13:.2f} µs（早一个周期）；13 cm：线性外推 {EX_T13_LIN:.2f} µs，模型 {EX_T13:.2f} µs")
    # page4：差分法（整根木条转 180°，每个方向开减关）
    D_DOWN = (T_DOWN - T_OFF) * 1e6
    D_UP = (T_UP - T_OFF) * 1e6
    DT_DIFF = D_UP - D_DOWN
    V_DIFF_EST = DT_DIFF * 1e-6 * C_FROM_SLOPE ** 2 / (2 * L0)
    assert abs(D_DOWN + 5.12) < 0.05 and abs(D_UP - 5.13) < 0.05 and abs(DT_DIFF - DT_MEAS * 1e6) < 1e-9
    # 模型的过零时刻落在 125 ns 台阶上，两边都正好 5.125；不取台阶的理论值不对称
    assert abs(D_DOWN + 5.125) < 1e-6 and abs(D_UP - 5.125) < 1e-6
    D_DOWN_TH = (L0 / (C0 + V_FAN) - L0 / C0) * 1e6
    D_UP_TH = (L0 / (C0 - V_FAN) - L0 / C0) * 1e6
    assert abs(D_DOWN_TH + 5.05) < 0.005 and abs(D_UP_TH - 5.14) < 0.005
    print(f"[r2] 差分理论值：顺风 {D_DOWN_TH:+.2f} µs，逆风 {D_UP_TH:+.2f} µs；模型 {D_DOWN:+.3f}/{D_UP:+.3f} µs；"
          f"页面读数相减 {round(T_DOWN*1e6, 2) - round(T_OFF*1e6, 2):+.2f}/{round(T_UP*1e6, 2) - round(T_OFF*1e6, 2):+.2f} µs")
    assert abs((round(T_DOWN*1e6, 2) - round(T_OFF*1e6, 2)) + 5.12) < 1e-6 and abs((round(T_UP*1e6, 2) - round(T_OFF*1e6, 2)) - 5.13) < 1e-6
    PER_MM_V = SLOPE[20] / DT_TABLE[1]          # 1 mm 放置误差相当于多少 m/s
    assert abs(PER_MM_V - 0.86) < 0.005
    print(f"[首审] 差分：顺风 开−关 {D_DOWN:+.3f} µs，逆风 开−关 {D_UP:+.3f} µs，Δt {DT_DIFF:.2f} µs → {V_DIFF_EST:.3f} m/s；"
          f"1 mm 放置误差 = {SLOPE[20]:.3f} µs ≈ {PER_MM_V:.2f} m/s 的风（1 m/s 只有 {DT_TABLE[1]:.2f} µs）")
    # page4：V5 变 0.4 % 对 ④ 的影响
    DV5 = VQ_NOM * 0.004 * 1e3
    print(f"[首审] V5 变 0.4 %（20 mV）：④ 变 {DV5:.1f} mV，风扇单向只有 {VQ_FAN:.2f} mV")
    assert abs(DV5 - 2.8) < 0.05
    # page4：木条表面反射多走的路
    for h in (0.01, 0.025):
        extra = (2 * math.hypot(L0 / 2, h) - L0) * 1e3
        print(f"[首审] 探头离木条 {h*100:.1f} cm：反射路径多 {extra:.2f} mm ≈ {extra*SLOPE[20]:.1f} µs")
    # page4：门限扫描到最大仍只见一两级时，100k 换 47k
    print(f"[首审] V_TH 最大 {VTH_SPAN:.3f} V；100k 换 47k 后 {EX_SPAN47:.3f} V")
    # page3 变式：斜向安装 cosθ
    DT_COS = 2 * 0.05 * 1.0 * math.cos(math.radians(45)) / CW ** 2 * 1e9
    assert abs(DT_COS - 32.2) < 0.1
    print(f"[首审] 变式：水 L = 5 cm、θ = 45°、1 m/s → Δt ≈ {DT_COS:.1f} ns（Arduino 一格 62.5 ns 的 {DT_COS/62.5:.2f} 倍；TDC7200 {DT_COS*1e-9/TDC7200:.0f} 格）")
    # page2 / page3：220 Ω 备选
    I220, TAU220, KEEP220 = drive(220)
    print(f"[首审] 220 Ω：峰值 {I220*1e3:.1f} mA，τ {TAU220*1e6:.2f} µs，基波保留 {KEEP220:.3f}（150 Ω 为 {KEEP150:.3f}，回波小 {(1-KEEP220/KEEP150)*100:.0f} %）")
    # 斜率：理论 vs 四点回归
    print(f"[首审] 斜率：理论 1/c = {SLOPE[20]:.3f} µs/mm；模型四点回归 {FIT[0]:.3f} µs/mm")
    # page3：按 Murata 手册粗估回波峰值（SPL 120 dB @ 10 Vrms、30 cm；灵敏度 −63 dB re 10 V/Pa）
    V_FUND = 4 / math.pi * 5.0 / math.sqrt(2)                 # 10 Vp-p 方波的基波有效值
    SPL30 = 120 + 20 * math.log10(V_FUND / 10)
    P20 = 20e-6 * 10 ** (SPL30 / 20) * 0.30 / 0.20            # 球面扩散 1/r
    V_RX = 10 * 10 ** (-63 / 20) * P20
    V_PK_AMP = V_RX * math.sqrt(2) * 11
    assert abs(V_FUND - 4.50) < 0.01 and abs(P20 - 13.5) < 0.1 and abs(V_PK_AMP - 1.49) < 0.02
    print(f"[首审] 手册估算：基波 {V_FUND:.2f} Vrms → 30 cm {SPL30:.1f} dB SPL → 20 cm {P20:.1f} Pa → 接收 {V_RX*1e3:.1f} mV rms → ×11 稳态峰值 {V_PK_AMP:.2f} V")
