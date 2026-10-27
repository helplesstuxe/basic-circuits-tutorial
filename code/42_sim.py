"""42 流量计信号链总览（A 部分 capstone）：本节所有数值的出处。
运行（仓库根目录）：/workspace/circuits-venv/bin/python code/42_sim.py
页面上的每个数字都由本脚本打印，关键结论用 assert 检查；本脚本不写任何文件。
图由 code/figs/42_figs.py 画，它会 import 本文件；SPICE 复核见 spice/42/run.py 和 review/spice/42.md。

page4 实验电路（风扇测速线模拟脉冲型流量计）：
  风扇电源：12 V → LM317（R_A 240 Ω，R_ADJ = 2 kΩ 电位器接成可变电阻）→ 风扇红线；直流调压调速，绝不用 PWM 斩电源
  测速线（黄线，开集电极，每转 2 个脉冲）→ R_PU 10 kΩ 上拉到 Arduino 5 V
  宽带通：测速线 → R_IN 100 kΩ → C_HP 1 µF → 节点 NB；NB 经 R_HP 100 kΩ 接中点参考 V_MID（5 V 经 10k/10k 分压）；
          NB 经 C_LP 1 nF 接 0 V
  施密特（LM393，12 V 供电，反相接法）：NB → IN−；IN+ = 5 V 经 10k/10k 分压，再经 R_H 100 kΩ 接到输出；
          输出经 4.7 kΩ 上拉到 Arduino 5 V → D2（attachInterrupt）
  Arduino：D2 测周期 → 换算“流量” → D9 analogWrite → 41 节发送器（12k/10k + 10 µF → LM358 → 2N3904，R_S 100 Ω）
          A0 经 10 kΩ 读 R_S 上端；AREF 接 LM4040-2.5（5 V 经 1 kΩ 供电）；250 Ω 只用万用表量
"""
import math, importlib.util, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S41 = _load("sim41_for42", "code/41_sim.py")      # 41 节的发送器模型（只读引用）

# ====================================================================== 1. 各类流量计的信号量级
# ---- 电磁：E = k·B·D_pipe·v，ADI 文章给的典型灵敏度 150–200 µV/(m/s)
EM_SENS = (150e-6, 175e-6, 200e-6)     # V/(m/s)
EM_G1 = 10                              # 第一级仪表放大倍数上限（电极极化直流太大，不能放太多）
EM_V = (0.5, 1.0, 15.0)                 # m/s


def em_signal(v, sens=175e-6, pp=True):
    """励磁正反交替：电极电压在 +E 与 −E 之间跳，峰峰值 2E。"""
    return (2 if pp else 1) * sens * v


EM_1MS_G10 = em_signal(1.0, pp=False) * EM_G1
EM_15_PP = [em_signal(15, s) for s in (150e-6, 200e-6)]
assert abs(EM_1MS_G10 - 1.75e-3) < 1e-9
assert abs(EM_15_PP[0] - 4.5e-3) < 1e-9 and abs(EM_15_PP[1] - 6.0e-3) < 1e-9
EM_ADC_PP = 2.0                         # 希望 15 m/s 时送进 ADC 的峰峰值约 2 V（例题设定）
EM_G2 = EM_ADC_PP / (em_signal(15) * EM_G1)       # 第二级（35 节 PGA）需要的倍数
EM_LOW_PP = em_signal(0.5) * EM_G1 * EM_G2         # 0.5 m/s 时到 ADC 的峰峰值

# ---- 超声时差：Δt ≈ 2·L·v·cosθ / c²（37 节），空气声速 c = 331.3 + 0.606·T_air
def c_air(t_air):
    return 331.3 + 0.606 * t_air


def tof_dt(L, v, c, cos_th=1.0):
    return 2 * L * v * cos_th / c ** 2


US_L, US_V, US_C = 0.2, 3.0, c_air(20)
US_DT = tof_dt(US_L, US_V, US_C)
US_T1 = US_L / US_C
assert abs(US_C - 343.42) < 0.01 and abs(US_DT * 1e6 - 10.17) < 0.01

# ---- 涡街：f = St·v/d
VX_ST, VX_D = 0.2, 0.010
VX_V = (0.3, 1.0, 3.0)
VX_F = [VX_ST * v / VX_D for v in VX_V]
assert [round(f) for f in VX_F] == [6, 20, 60]

# ---- 涡轮：Q_V = f·60/K（FLOMEC 例：500 Hz、K = 100 脉冲/加仑 → 300 gpm）
TB_EX = 500 * 60 / 100
assert TB_EX == 300

# ---- 差压：Q_V = C_d·A2·sqrt(2ΔP/(ρ(1−β⁴)))
DP_RHO, DP_D, DP_BETA, DP_CD = 1000.0, 0.050, 0.5, 0.6


def dp_flow(dp, rho=DP_RHO, D=DP_D, beta=DP_BETA, cd=DP_CD):
    a2 = math.pi * (beta * D) ** 2 / 4
    v2 = math.sqrt(2 * dp / (rho * (1 - beta ** 4)))
    return cd * a2 * v2, v2


DP_PTS = (100, 2500, 10000)
DP_Q = [dp_flow(p)[0] * 1e3 for p in DP_PTS]        # L/s
assert [round(q, 3) for q in DP_Q] == [0.136, 0.680, 1.360]


def dp_err(p, e=0.001):
    """差压读数（满量程归一化 p）有 e（满量程的 0.1 %）误差时，流量误差：%FS 和 % 读数。"""
    q, q2 = math.sqrt(p), math.sqrt(p + e)
    return (q2 - q) * 100, (q2 - q) / q * 100


DP_ERR = {p: dp_err(p) for p in (1.0, 0.25, 0.04, 0.01, 0.008)}
assert abs(DP_ERR[0.01][1] - 4.88) < 0.01 and abs(DP_ERR[1.0][0] - 0.05) < 0.001


def s3051(x):
    """Rosemount 3051S 开方输出的低流量处理：0–0.6 % 差压按斜率 1 线性；0.6–0.8 % 线性过渡（斜率约 42）；之后开方。"""
    x = np.asarray(x, float)
    y = np.sqrt(np.clip(x, 0, None))
    lo = x <= 0.006
    mid = (x > 0.006) & (x < 0.008)
    y = np.where(lo, x, y)
    slope = (math.sqrt(0.008) - 0.006) / 0.002
    y = np.where(mid, 0.006 + slope * (x - 0.006), y)
    return y


S3051_SLOPE = (math.sqrt(0.008) - 0.006) / 0.002
assert abs(S3051_SLOPE - 41.7) < 0.05
DBL = {p: (math.sqrt(p), p ** 0.25) for p in (0.01, 0.10, 0.25, 0.50, 1.0)}
assert abs(DBL[0.10][1] - 0.562) < 0.001 and abs(math.sqrt(0.10) - 0.316) < 0.001

# ====================================================================== 2. page4 实验：风扇当脉冲流量计
V5 = 5.00          # Arduino 5 V 引脚，实测为准，写进程序
V5_EX = 4.83       # 论坛实测例（页面只当“比如”）
PPR = 2            # Intel 4 线风扇规范：每转 2 个脉冲
K_SIM = 20.0       # 自定义“模拟流量”系数：每升 20 个脉冲（纯属示意，风扇不是流量计）
F_FS = 100.0       # 满量程频率（Hz）→ 20 mA
F_CUT = 5.0        # 低流量切除（Hz）：低于它一律输出 4.00 mA
T_OUT = 0.5        # 超过 0.5 s 没有脉冲 → 频率记 0


def rpm_of(f):
    return f * 60 / PPR


def flow_lpm(f, k=K_SIM):
    return f * 60 / k


def ma_of(f):
    if f < F_CUT:
        return 4.0
    return min(20.0, 4.0 + 16.0 * f / F_FS)


def code_of(ma, v5=V5):
    return S41.code_for(ma, v5=v5)


def chain(f, v5_prog=V5, v5_true=V5, vref=2.500):
    """频率 → 设定 mA → PWM 码 → 真实 V_SET → 回路电流 → 250 Ω 电压 → A0（AREF = LM4040）读回。"""
    ma = ma_of(f)
    code = code_of(ma, v5_prog)
    vset = S41.vset_of(code, v5=v5_true)
    r = S41.sender(vset, 0.0)
    n0 = int(np.clip(np.floor(r["ie"] * S41.R_S / vref * 1024), 0, 1023))
    ie_a0 = n0 * vref / 1024 / S41.R_S
    # 对照：41 节的默认接法（AREF = 5 V 引脚），程序按 v5_prog 换算
    n41 = int(np.clip(np.floor(r["ie"] * S41.R_S / v5_true * 1024), 0, 1023))
    ie_41 = n41 * v5_prog / 1024 / S41.R_S
    return dict(f=f, rpm=rpm_of(f), q=flow_lpm(f), ma=ma, code=code, vset=vset, ic=r["ic"], ie=r["ie"],
                v250=r["ic"] * S41.R_RX, n0=n0, ie_a0=ie_a0, n41=n41, ie_41=ie_41)


LAB_F = (0.0, 3.0, 30.0, 50.0, 80.0, 100.0, 120.0)
LAB = [chain(f) for f in LAB_F]
LAB_483 = [chain(f, v5_prog=V5, v5_true=V5_EX) for f in (50.0, 100.0)]
LAB_483_OK = [chain(f, v5_prog=V5_EX, v5_true=V5_EX) for f in (50.0, 100.0)]
_c = {round(d["f"]): d for d in LAB}
assert _c[0]["code"] == 45 and _c[50]["code"] == 135 and _c[100]["code"] == 224 and _c[120]["code"] == 224
assert _c[3]["ma"] == 4.0 and _c[30]["ma"] == 8.8

# A0 分辨率（AREF = 2.500 V）与 LM4040 电流
A0_LSB_MA = 2.5 / 1024 / 100 * 1e3
R_Z = 1000.0
R_AREF_IN = 32e3                                # Arduino 文档：AREF 内部约 32 kΩ


def lm4040_i(v5):
    return (v5 - 2.5) / R_Z - 2.5 / R_AREF_IN


I_Z = {v: lm4040_i(v) for v in (5.00, V5_EX)}
assert all(60e-6 < i < 15e-3 for i in I_Z.values())

# 计时分辨率：micros() 每 4 µs 跳一次
def micros_err(f, n_periods=1):
    return 4e-6 / (n_periods / f) * 100


# ---- LM317 风扇电源：V_o = 1.25·(1 + R_ADJ/R_A)（忽略 I_ADJ 项）
R_A = 240.0


def lm317_v(r_adj):
    return 1.25 * (1 + r_adj / R_A)


def lm317_r_for(v):
    return (v / 1.25 - 1) * R_A


LM317_PTS = {v: lm317_r_for(v) for v in (4.0, 7.0, 10.0)}
assert abs(lm317_v(0) - 1.25) < 1e-9 and abs(lm317_v(2000) - 11.67) < 0.01
FAN_I_EX = 0.15                               # 假设风扇标签电流 0.15 A（举例，以标签为准）


def lm317_p(vfan, i=FAN_I_EX, vin=12.0):
    return (vin - vfan) * i


# ---- 宽带通 + 施密特
R_PU, R_IN, C_HP, R_HP, C_LP = 10e3, 100e3, 1e-6, 100e3, 1e-9
R_MID = 10e3                       # V_MID 分压上下各 10 kΩ → 戴维南 5 kΩ
R_R1, R_R2, R_H, R_OUT = 10e3, 10e3, 100e3, 4.7e3
VOL = 0.065                        # LM393 吸 1 mA 时的输出低电平（沿用 36 节 SPICE 值）
VMID = V5 / 2


def bp_H(f):
    """从测速线（理想 0/5 V 源）到 NB 的复增益：R_IN + C_HP 串联，NB 对地 C_LP、对 V_MID 是 R_HP + 5 kΩ。"""
    w = 2 * np.pi * np.asarray(f, float)
    zs = R_IN + 1 / (1j * w * C_HP)
    zp = 1 / (1 / (R_HP + R_MID / 2) + 1j * w * C_LP)
    return zp / (zs + zp)


BP_PASS = abs(bp_H(50.0))
_ff = np.logspace(-2, 5, 20001)
_hh = abs(bp_H(_ff))
_band = _ff[_hh >= _hh.max() / math.sqrt(2)]
BP_FL, BP_FH = _band[0], _band[-1]
BP_F0 = math.sqrt(BP_FL * BP_FH)
BP_Q = BP_F0 / (BP_FH - BP_FL)
assert BP_Q < 1 and BP_FL < 1 and BP_FH > 2000


def schmitt_th(vpull=V5):
    """反相施密特：IN+ 由 10k/10k 分压（戴维南 5 kΩ、2.5 V）再经 R_H 接输出。
    输出高时输出节点被 R_OUT 上拉，同时经 R_H + 5 kΩ 接 2.5 V，求真实高电平。"""
    rth, vth = R_R1 * R_R2 / (R_R1 + R_R2), V5 * R_R2 / (R_R1 + R_R2)
    voh = (vpull / R_OUT + vth / (R_H + rth)) / (1 / R_OUT + 1 / (R_H + rth))
    vu = (vth / rth + voh / R_H) / (1 / rth + 1 / R_H)
    vl = (vth / rth + VOL / R_H) / (1 / rth + 1 / R_H)
    return vu, vl, voh


VU, VL, VOH = schmitt_th()
assert abs(VU - 2.614) < 1e-3 and abs(VL - 2.384) < 1e-3 and abs(VOH - 4.893) < 1e-3


def tach_wave(t, f, duty=0.5):
    return np.where((t * f) % 1.0 < duty, 0.0, 1.0)     # 1 = 开集电极关断（被上拉成高）


def frontend(f=60.0, duty=0.5, t_end=1.2, dt=2e-6, v5=V5, keep_from=None):
    """显式欧拉逐步仿真：测速线（开集电极 + 10 k 上拉）→ R_IN → C_HP → NB（R_HP 到 V_MID、C_LP 到地）→ LM393 反相施密特。
    返回 dict：各节点波形（keep_from 之后）、比较器切换时 NB 的电压、输出边沿数。"""
    n = int(t_end / dt)
    t = np.arange(n) * dt
    off = tach_wave(t, f, duty)
    vc = 0.0              # C_HP 两端电压（左正）：初值 0，起动后 HP 时间常数约 0.2 s
    vnb = VMID
    out_hi = True
    vtach = np.empty(n); vnbv = np.empty(n); vout = np.empty(n)
    sw_up, sw_dn = [], []
    vmid = v5 / 2
    for k in range(n):
        # 测速线节点：开集电极导通时 ≈ 0 V；关断时由 R_PU 上拉，同时经 R_IN 流向 C_HP
        if off[k] > 0.5:
            vt = (v5 / R_PU + (vc + vnb) / R_IN) / (1 / R_PU + 1 / R_IN)
        else:
            vt = 0.0
        i_in = (vt - vc - vnb) / R_IN
        vc += i_in / C_HP * dt
        i_lp = i_in - (vnb - vmid) / (R_HP + R_MID / 2)
        vnb += i_lp / C_LP * dt if C_LP > 0 else 0
        # 反相施密特：NB 高于上门限 → 输出拉低；低于下门限 → 输出变高
        if out_hi and vnb > VU:
            out_hi = False; sw_up.append(vnb)
        elif (not out_hi) and vnb < VL:
            out_hi = True; sw_dn.append(vnb)
        vtach[k] = vt; vnbv[k] = vnb; vout[k] = VOH if out_hi else VOL
    k0 = int((keep_from if keep_from is not None else t_end - 0.2) / dt)
    edges = int(np.sum(np.diff((vout[k0:] > 2.5).astype(int)) == 1))
    return dict(t=t[k0:], tach=vtach[k0:], nb=vnbv[k0:], out=vout[k0:], edges=edges,
                avg_tach=vtach[k0:].mean(), avg_nb=vnbv[k0:].mean(), avg_out=vout[k0:].mean(),
                nb_max=vnbv[k0:].max(), nb_min=vnbv[k0:].min())


# ====================================================================== 3. page3 举一反三
# 例 1（完整例题）：磁电式涡轮流量计（题设数据）
EX1_K = 900.0                  # 脉冲/L（题设）
EX1_Q = (2.0, 30.0)            # L/min
EX1_A_MIN = 0.020              # 2 L/min 时线圈输出峰值 20 mV（题设），幅度与 f 成正比
EX1_F = [q * EX1_K / 60 for q in EX1_Q]
EX1_A_MAX = EX1_A_MIN * EX1_F[1] / EX1_F[0]
EX1_HALF_HYS = (VU - VL) / 2
EX1_G_MIN = 4 * EX1_HALF_HYS / EX1_A_MIN           # 最小信号放大后峰值 ≥ 半回差的 4 倍
EX1_G = 34.0                                        # 同相放大 1 + 33k/1k = 34
EX1_SWING = 4.0                                     # 12 V 单电源、V_MID = 4.5 V 时 LM358 不削顶的大约摆幅（± 4 V，题设取值）
EX1_TOP = EX1_A_MAX * EX1_G
EX1_FL = EX1_F[0] / 5
EX1_FH = EX1_F[1] * 5
EX1_C_HP = 1e-6
EX1_R_HP = 1 / (2 * math.pi * EX1_FL * EX1_C_HP)
EX1_C_LP = 10e-9
EX1_R_LP = 1 / (2 * math.pi * EX1_FH * EX1_C_LP)
EX1_R_HP_E, EX1_R_LP_E = 27e3, 6.8e3                # 取标准值
EX1_FL_E = 1 / (2 * math.pi * EX1_R_HP_E * EX1_C_HP)
EX1_FH_E = 1 / (2 * math.pi * EX1_R_LP_E * EX1_C_LP)
EX1_MID_Q = 16.0
EX1_MID_F = EX1_MID_Q * EX1_K / 60
EX1_MID_MA = 4 + 16 * EX1_MID_F / EX1_F[1]
assert abs(EX1_F[0] - 30) < 1e-9 and abs(EX1_F[1] - 450) < 1e-9
assert EX1_G > EX1_G_MIN and EX1_TOP > EX1_SWING     # 大流量必然削顶——对频率型信号无害

# 例 2（留空）：差压变送器 0–2500 Pa 线性 4–20 mA，读到 8.0 mA
EX2_DP_FS = 2500.0
EX2_MA = 8.0
EX2_P = (EX2_MA - 4) / 16
EX2_DP = EX2_P * EX2_DP_FS
EX2_QFRAC = math.sqrt(EX2_P)
EX2_QV = dp_flow(EX2_DP)[0] * 1e3
EX2_QV_FS = dp_flow(EX2_DP_FS)[0] * 1e3
assert abs(EX2_DP - 625) < 1e-9 and abs(EX2_QFRAC - 0.5) < 1e-12
assert abs(EX2_QV - 0.340) < 0.001 and abs(EX2_QV_FS - 0.680) < 0.001

# 例 3（变体）：压电涡街（题设：钝体 20 mm，St = 0.2，流速 0.5–5 m/s）
EX3_D, EX3_V = 0.020, (0.5, 5.0)
EX3_F = [VX_ST * v / EX3_D for v in EX3_V]
assert abs(EX3_F[0] - 5) < 1e-9 and abs(EX3_F[1] - 50) < 1e-9

# 练习：电磁流量计第二级倍数（灵敏度 150 µV/(m/s)，0.5 m/s）
EXR_PP = em_signal(0.5, 150e-6) * EM_G1


def report():
    print("== 1. 各类流量计的信号量级 ==")
    print(f"电磁 175 µV/(m/s) × 1 m/s × G{EM_G1} = {EM_1MS_G10*1e3:.2f} mV；15 m/s 峰峰值 {EM_15_PP[0]*1e3:.1f}–{EM_15_PP[1]*1e3:.1f} mV")
    print(f"电磁：15 m/s 经 G1={EM_G1} 后 {em_signal(15)*EM_G1*1e3:.1f} mVpp，要到 {EM_ADC_PP} Vpp 需第二级 ×{EM_G2:.1f}；"
          f"同样倍数下 0.5 m/s 只有 {EM_LOW_PP*1e3:.0f} mVpp")
    print(f"超声（空气）c = {US_C:.1f} m/s，L = {US_L} m，v = {US_V} m/s：单程 {US_T1*1e6:.0f} µs，Δt = {US_DT*1e6:.2f} µs")
    print(f"涡街 St=0.2、d=10 mm：{VX_V} m/s → {[round(f) for f in VX_F]} Hz；涡轮 FLOMEC 例 {TB_EX:.0f} gpm")
    print(f"差压例（水，D=50 mm，β=0.5，C_d=0.6）：{DP_PTS} Pa → {[round(q, 3) for q in DP_Q]} L/s")
    for p, (a, b) in DP_ERR.items():
        print(f"  差压 {p*100:.1f} % 满量程，差压误差 0.1 %FS → 流量误差 {a:.2f} %FS = {b:.2f} % 读数")
    print(f"3051S 过渡段斜率 {S3051_SLOPE:.1f}；双重开方：" + "，".join(f"{p*100:.0f}% 差压 → 应 {a*100:.1f}% 显示 {b*100:.1f}%" for p, (a, b) in DBL.items()))
    print("== 2. page4 ==")
    print(f"每转 {PPR} 脉冲：f = 40/60/80/100 Hz → {[rpm_of(f) for f in (40, 60, 80, 100)]} rpm")
    for d in LAB:
        print(f"  f={d['f']:5.1f} Hz rpm={d['rpm']:5.0f} 模拟流量 {d['q']:6.1f} L/min → {d['ma']:5.2f} mA，码 {d['code']:3d}，V_SET {d['vset']:.3f} V，"
              f"回路 {d['ic']*1e3:.2f} mA，250 Ω 上 {d['v250']:.3f} V；A0（2.5 V 基准）码 {d['n0']} → {d['ie_a0']*1e3:.2f} mA")
    for d, e in zip(LAB_483, LAB_483_OK):
        print(f"  V5 实为 4.83 V、程序写 5.00：f={d['f']:.0f} Hz 设 {d['ma']:.1f} mA，实际回路 {d['ic']*1e3:.2f} mA（250 Ω 上 {d['v250']:.3f} V）；"
              f"LM4040 基准的 A0 读回 I_E {d['ie_a0']*1e3:.2f} mA，41 节比例接法读回 {d['ie_41']*1e3:.2f} mA；"
              f"改写 V5=4.83 后码 {e['code']}、回路 {e['ic']*1e3:.2f} mA")
    print(f"A0 每个码 = {A0_LSB_MA*1e3:.1f} µA；LM4040 电流 V5=5.00: {I_Z[5.0]*1e3:.2f} mA，4.83: {I_Z[V5_EX]*1e3:.2f} mA")
    print(f"micros() 4 µs：单周期误差 60 Hz {micros_err(60):.3f} %，233 Hz {micros_err(233):.3f} %；0.5 s 窗口 60 Hz {micros_err(60, 30):.4f} %")
    print(f"LM317：R_ADJ=0 → {lm317_v(0):.2f} V，2 kΩ → {lm317_v(2000):.2f} V（公式，未计压差）；4/7/10 V 需 R_ADJ "
          + "/".join(f"{r:.0f}" for r in LM317_PTS.values()) + " Ω")
    print(f"LM317 功耗（风扇 0.15 A 举例）：7 V {lm317_p(7):.2f} W，4 V {lm317_p(4):.2f} W，10 V {lm317_p(10):.2f} W")
    print(f"宽带通：通带增益 {BP_PASS:.3f}，−3 dB {BP_FL:.2f} Hz – {BP_FH:.0f} Hz，几何中心 {BP_F0:.1f} Hz，Q 值 {BP_Q:.3f}")
    for f in (5, 10, 30, 60, 100, 250, 1000):
        print(f"  |H({f} Hz)| = {abs(bp_H(f)):.3f}")
    print(f"施密特门限：上 {VU:.3f} V，下 {VL:.3f} V，回差 {VU-VL:.3f} V，输出高 {VOH:.3f} V")
    print("== 3. page3 ==")
    print(f"例1 f = {EX1_F[0]:.0f}–{EX1_F[1]:.0f} Hz，幅度 {EX1_A_MIN*1e3:.0f}–{EX1_A_MAX*1e3:.0f} mV 峰；G ≥ {EX1_G_MIN:.1f}，取 {EX1_G:.0f}（1 + 33k/1k）；"
          f"大流量放大后 {EX1_TOP:.1f} V 峰 > ±{EX1_SWING} V → 削顶无害；HP {EX1_FL:.0f} Hz → R = {EX1_R_HP/1e3:.1f} kΩ（1 µF）；"
          f"LP {EX1_FH:.0f} Hz → R = {EX1_R_LP/1e3:.2f} kΩ（10 nF）；取 27k/6.8k → {EX1_FL_E:.2f} Hz / {EX1_FH_E:.0f} Hz；"
          f"16 L/min → {EX1_MID_F:.0f} Hz → {EX1_MID_MA:.2f} mA")
    print(f"例2 8 mA → {EX2_P*100:.0f} % 差压 = {EX2_DP:.0f} Pa → 流量 {EX2_QFRAC*100:.0f} % = {EX2_QV:.3f} L/s（满量程 {EX2_QV_FS:.3f}）")
    print(f"例3 f = {EX3_F[0]:.0f}–{EX3_F[1]:.0f} Hz；练习：150 µV/(m/s)·0.5 m/s·G10 = {EXR_PP*1e3:.2f} mVpp")


if __name__ == "__main__":
    report()
    r = frontend(60.0)
    print(f"前端仿真 60 Hz：NB {r['nb_min']:.2f}–{r['nb_max']:.2f} V，平均 测速线 {r['avg_tach']:.2f} / NB {r['avg_nb']:.2f} / 输出 {r['avg_out']:.2f} V，0.2 s 内上升沿 {r['edges']}")
    assert r["edges"] == 12
    for f in (10.0, 100.0):
        q = frontend(f, t_end=2.0, keep_from=1.0)
        print(f"前端仿真 {f:.0f} Hz：1 s 内上升沿 {q['edges']}，NB {q['nb_min']:.2f}–{q['nb_max']:.2f} V")
        assert q["edges"] == int(f)
    print("42_sim OK")
