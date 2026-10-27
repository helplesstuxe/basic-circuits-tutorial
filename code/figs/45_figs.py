"""45 集成功放芯片与散热保护：全部配图。
运行：/workspace/circuits-venv/bin/python code/figs/45_figs.py
LM386 的波形 / 扫描数据来自 spice/45/*.csv（由 spice/45/run.py --update 从 ngspice 结果生成）；
PAM8403、TPA3116D2、LM7805 的数字按数据手册参数用公式算出。
图上的每个数字都由本脚本算出并打印；关键结论用 assert 检查。
实验电路：9 V 单电源，LM386N（DIP-8），脚6 100 µF + 0.1 µF，脚7 10 µF，输出 220 µF → 10 Ω → 8 Ω 喇叭，
吸收网络 10 Ω + 47 nF；输入 10 kΩ / 1 kΩ 分压 + 10 kΩ 电位器。
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
from lab_schem import probe, colnote, lab, title, note, ring, Hop, _dbox, GRAY


N = "45"
SP = os.path.join(HERE, "..", "..", "spice", "45")


def csv(name):
    """读 spice/45 下的 CSV（第一行是列名），返回 {列名: 数组}。"""
    path = os.path.join(SP, name)
    head = open(path).readline().strip().split(",")
    arr = np.genfromtxt(path, delimiter=",", skip_header=1, dtype=None, encoding="utf-8")
    if arr.dtype.names:
        return {h: arr[n] for h, n in zip(head, arr.dtype.names)}
    arr = np.atleast_2d(arr)
    return {h: arr[:, i] for i, h in enumerate(head)}


# ============================ 公共数值 ============================
NUM = {k: float(v) for k, v in zip(*csv("nums.csv").values())}
VS = 9.0                         # 实验电源
IQ = 4.3e-3                      # LM386 在 9 V 的静态电流（数据手册 Figure 9-4 读数，SPICE 同值）
VLOSS = 1.15                     # LM386 输出离每条电源轨的距离（由 N-3 的 700 mW @ 9 V / 8 Ω 反推，见下）
R10, RSPK = 10.0, 8.0
RL = R10 + RSPK
TH_PDIP, TH_SOIC = 53.4, 115.7   # LM386 RθJA（°C/W）
PD_PDIP, PD_SOIC = 1.25, 0.73    # LM386 封装功耗上限（绝对最大额定值）
RDS_PAM = 0.18 + 0.14            # PAM8403 上管 + 下管导通电阻
IQ_PAM = 16e-3                   # PAM8403 在 5 V 的静态电流（两声道）
G_PAM = 10 ** (24 / 20)          # PAM8403 最大增益 24 dB
TH_PAM = 110.0
IQ_7805, TH_7805 = 8e-3, 54.0    # LM7805 静态电流（SNOSBT0L LM7805 表：25 °C 时最大 8 mA，取最大值）、TO-220 θJA（绝对最大额定值注 (3)，自由空气）
RDS_TPA, ICC_TPA = 0.12, 20e-3   # TPA3116D2 导通电阻、12 V 静态电流

# ---- LM386：由 N-3 的 700 mW（9 V、8 Ω、10 % THD）反推输出离电源轨的距离 ----
VP_N3 = np.sqrt(2 * 0.7 * 8)
LOSS_N3 = VS / 2 - VP_N3
print(f"[数值] LM386N-3 700 mW @ 9 V/8 Ω → 峰值 {VP_N3:.3f} V → 离电源轨 {LOSS_N3:.3f} V（模型取 {VLOSS} V）")
assert abs(LOSS_N3 - VLOSS) < 0.01


def p_se(vs, r, loss=0.0):
    """单端（SE）输出、正弦满幅时负载功率：峰值 vs/2 − loss。"""
    vp = np.clip(vs / 2 - loss, 0, None)
    return vp ** 2 / (2 * r)


def p_btl(vs, r, rds=0.0):
    """BTL 输出满幅时负载功率：峰值 vs·r/(r+rds)。"""
    vp = vs * r / (r + rds)
    return vp ** 2 / (2 * r)


def pd_se_max(vs, r, iq=IQ):
    """单端 B 类（AB 类）功放芯片最大发热：VS²/(2π²RL) + VS·IQ。"""
    return vs ** 2 / (2 * np.pi ** 2 * r) + vs * iq


VP_LAB = VS / 2 - VLOSS
P18 = VP_LAB ** 2 / (2 * RL)
P18_SPK, P18_R = P18 * RSPK / RL, P18 * R10 / RL
P8_IDEAL, P8_LOSS = p_se(VS, 8), p_se(VS, 8, VLOSS)
print(f"[数值] LM386 9 V：8 Ω 理想 {P8_IDEAL:.3f} W、扣 1.15 V 后 {P8_LOSS:.3f} W；18 Ω 满幅峰值 {VP_LAB:.2f} V → {P18:.4f} W"
      f"（喇叭 {P18_SPK:.4f} W，10 Ω {P18_R:.4f} W）")
assert abs(P8_IDEAL - 1.2656) < 1e-3 and abs(P8_LOSS - 0.700) < 0.002 and abs(P18 - 0.3117) < 1e-3

# 输入分压：10 kΩ 上，下面 1 kΩ ∥ 10 kΩ 电位器 ∥ 50 kΩ（LM386 输入电阻）
R_LO = 1 / (1 / 1e3 + 1 / 10e3 + 1 / 50e3)
KDIV = R_LO / (10e3 + R_LO)
VPHONE = 1.48                    # 手机满音量 1.05 V 有效值 × √2 = 1.485 V，取 1.48 V（与 SPICE 信号源一致）
print(f"[数值] 手机满音量峰值 {VPHONE:.3f} V；分压比 {KDIV:.5f} → 脚3 {VPHONE*KDIV:.4f} V（SPICE {NUM['脚3 峰值（分压 + 电位器开满）']:.4f} V）")
assert abs(VPHONE * KDIV - NUM["脚3 峰值（分压 + 电位器开满）"]) < 0.002
VIN_CLIP20, VIN_CLIP200 = VP_LAB / 20, VP_LAB / 200
print(f"[数值] 刚削顶的输入峰值：增益 20 → {VIN_CLIP20*1e3:.1f} mV，增益 200 → {VIN_CLIP200*1e3:.2f} mV；手机直连 {VPHONE:.2f} V 是 ±0.4 V 上限的 {VPHONE/0.4:.1f} 倍")

# 内部增益网络
G20 = 2 * 15e3 / (150 + 1.35e3)
G200 = 2 * 15e3 / 150
def g_net(f, c=10e-6):
    zc = 1 / (2j * np.pi * f * c)
    zp = 1.35e3 * zc / (1.35e3 + zc)
    return abs(2 * 15e3 / (150 + zp))
print(f"[数值] 增益公式：2×15k/(150+1.35k) = {G20:.2f}；2×15k/150 = {G200:.1f}；"
      f"10 µF 跨 1–8：100 Hz {g_net(100):.1f}，20 Hz {g_net(20):.1f}（SPICE {NUM['增益 200 档 100 Hz']:.1f}、{NUM['增益 200 档 20 Hz']:.1f}）")
assert abs(G20 - 20) < 1e-9 and abs(G200 - 200) < 1e-9
assert abs(g_net(100) - NUM["增益 200 档 100 Hz"]) / NUM["增益 200 档 100 Hz"] < 0.02
assert abs(g_net(20) - NUM["增益 200 档 20 Hz"]) / NUM["增益 200 档 20 Hz"] < 0.02

FC8 = 1 / (2 * np.pi * 220e-6 * 8)
FC18 = 1 / (2 * np.pi * 220e-6 * RL)
FZOB = 1 / (2 * np.pi * 10 * 47e-9)
print(f"[数值] 220 µF 下限：8 Ω {FC8:.1f} Hz，18 Ω {FC18:.1f} Hz（SPICE {NUM['220 µF + 18 Ω 下限 −3 dB']:.1f} Hz）；吸收网络 10 Ω/47 nF 拐点 {FZOB/1e3:.1f} kHz")
FC250_18, FC250_8 = 1 / (2 * np.pi * 18 * 250e-6), 1 / (2 * np.pi * 8 * 250e-6)
FZ_05 = 1 / (2 * np.pi * 10 * 0.05e-6)
print(f"[数值] 手册图 9-1/9-3 的 250 µF：18 Ω 下限 {FC250_18:.1f} Hz、8 Ω {FC250_8:.1f} Hz；0.05 µF + 10 Ω 拐点 {FZ_05/1e3:.1f} kHz")
assert abs(FC18 - NUM["220 µF + 18 Ω 下限 −3 dB"]) < 0.5

# 发热与温升
PD_ROWS = [("9 V、18 Ω（本实验）", 9, 18), ("9 V、8 Ω", 9, 8), ("12 V、8 Ω", 12, 8)]
PD = {k: pd_se_max(v, r) for k, v, r in PD_ROWS}
for k, v, r in PD_ROWS:
    print(f"[数值] LM386 最大发热 {k}：{PD[k]:.3f} W → 温升 PDIP {PD[k]*TH_PDIP:.1f} °C，SOIC {PD[k]*TH_SOIC:.1f} °C")
assert abs(PD["9 V、18 Ω（本实验）"] - NUM["芯片发热最大值（扫描）"]) < 0.002
PD_LAB = NUM["芯片发热（电源 − 喇叭 − 10 Ω）"]
print(f"[数值] 手机满音量、增益 20：芯片 {PD_LAB:.3f} W → PDIP 温升 {PD_LAB*TH_PDIP:.1f} °C")

# PAM8403（5 V，BTL）
PAM = {r: p_btl(5, r, RDS_PAM) for r in (4, 8, 18)}
P_PAM18_SPK = PAM[18] * RSPK / RL
print(f"[数值] PAM8403 5 V 满幅：4 Ω {PAM[4]:.3f} W，8 Ω {PAM[8]:.3f} W，18 Ω {PAM[18]:.3f} W（喇叭 {P_PAM18_SPK:.3f} W）；"
      f"SE 同 5 V/8 Ω 理想 {p_se(5, 8):.3f} W")
VIN_PAM_CLIP = 5 * RL / (RL + RDS_PAM) / G_PAM
print(f"[数值] PAM8403 增益 24 dB = {G_PAM:.2f} 倍，18 Ω 满幅所需输入峰值 {VIN_PAM_CLIP:.3f} V")


def pam_pin(p, r=RL, vdd=5.0):
    """PAM8403 单声道输出功率 p 时从 5 V 取的功率（导通损耗 + 静态，不含开关损耗：偏乐观）。"""
    irms2 = p / r
    return p + irms2 * RDS_PAM + vdd * IQ_PAM


def via_7805(p5, vin=9.0):
    """经 LM7805 从 9 V 取电：输入电流 = 输出电流 + 7805 静态电流。"""
    return vin * (p5 / 5.0 + IQ_7805)


ETA_PAM8 = 1.8 / pam_pin(1.8, 8)
print(f"[数值] PAM8403 8 Ω 1.8 W 的模型效率 {ETA_PAM8*100:.1f} %（数据手册 87 %，模型没算开关损耗，偏高）")
P01 = 0.1
SW = csv("sweep.csv")
ETA386_01 = np.interp(P01, SW["pl"], SW["pl"] / SW["pin"])
ETA_PAM01 = P01 / pam_pin(P01)
ETA_7805_01 = P01 / via_7805(pam_pin(P01))
print(f"[数值] 18 Ω 上 0.1 W：LM386 效率 {ETA386_01*100:.1f} %，PAM8403 {ETA_PAM01*100:.1f} %，PAM8403+7805（从 9 V）{ETA_7805_01*100:.1f} %")
PIN_PAMFULL = pam_pin(PAM[18])
I5_FULL = PIN_PAMFULL / 5
PD_7805 = (9 - 5) * I5_FULL + 9 * IQ_7805
PIN9_FULL = via_7805(PIN_PAMFULL)
PIN386_FULL = VS * (VP_LAB / (np.pi * RL) + IQ)
print(f"[数值] PAM8403 满幅（18 Ω {PAM[18]:.3f} W）：5 V 电流 {I5_FULL*1e3:.1f} mA；7805 发热 {PD_7805:.3f} W → 温升 {PD_7805*TH_7805:.1f} °C；"
      f"从 9 V 总效率 {PAM[18]/PIN9_FULL*100:.1f} %，只看芯片 {PAM[18]/PIN_PAMFULL*100:.1f} %")
print(f"[数值] LM386 满幅（18 Ω {P18:.3f} W）：电源 {PIN386_FULL:.3f} W，效率 {P18/PIN386_FULL*100:.1f} %")
PD_PAM_FULL = PIN_PAMFULL - PAM[18]
PD_PAM8 = 2 * (1.8 / 0.87 - 1.8)
print(f"[数值] PAM8403 单声道 18 Ω 满幅发热 {PD_PAM_FULL:.3f} W → 温升 {PD_PAM_FULL*TH_PAM:.1f} °C；"
      f"两声道 8 Ω 各 1.8 W（按 87 %）发热 {PD_PAM8:.3f} W → 温升 {PD_PAM8*TH_PAM:.1f} °C")
assert abs(ETA_PAM01 - 0.55) < 0.01

# ---- 选做 D：PAM8403 的输入要不要分压 ----
RI_PAM = 18e3                                    # PAM8403 最大增益 24 dB 时的输入电阻 RI（手册 p.7）
R_LO_D = 1 / (1 / 1e3 + 1 / 10e3 + 1 / RI_PAM)   # 1 kΩ ∥ 10 kΩ 电位器（开满）∥ RI
VIN_D = VPHONE * R_LO_D / (10e3 + R_LO_D)
VDIFF_D = VIN_D * G_PAM
VSPK_D = VDIFF_D * RSPK / (RL + RDS_PAM)
PSPK_D = VSPK_D ** 2 / (2 * RSPK)
VIN_D_CLIP = 5.0 / G_PAM                         # 差分峰值到 5 V（满电源）时的输入峰值
I_SQ = 5.0 / (RL + RDS_PAM)                      # 不分压、满音量：输出削成 ±5 V 方波
PSPK_SQ, PR10_SQ = I_SQ ** 2 * RSPK, I_SQ ** 2 * R10
I5_SQ = I_SQ + IQ_PAM
I9_SQ = I5_SQ + IQ_7805
PD_7805_SQ = (9 - 5) * I5_SQ + 9 * IQ_7805
print(f"[数值] 选做 D 加分压：输入峰值 {VIN_D*1e3:.1f} mV × {G_PAM:.2f} = 差分 {VDIFF_D:.3f} V，喇叭峰值 {VSPK_D:.3f} V，{PSPK_D*1e3:.1f} mW；"
      f"输入到 {VIN_D_CLIP*1e3:.0f} mV 峰值才顶到 5 V")
print(f"[数值] 选做 D 不分压满音量（方波 ±5 V，{RL+RDS_PAM:.2f} Ω）：电流 {I_SQ:.3f} A，喇叭 {PSPK_SQ:.3f} W，10 Ω {PR10_SQ:.3f} W；"
      f"5 V 侧 {I5_SQ*1e3:.0f} mA，9 V 侧 {I9_SQ*1e3:.0f} mA；7805 发热 {PD_7805_SQ:.3f} W → 无散热片温升 {PD_7805_SQ*TH_7805:.0f} °C")
print(f"[数值] 7805 静态 {IQ_7805*1e3:.0f} mA（手册最大）：选做 D 静音时 9 V 侧电流 ≤ {(IQ_PAM+IQ_7805)*1e3:.0f} mA；"
      f"满幅正弦 7805 发热 {PD_7805:.3f} W → 无散热片温升 {PD_7805*TH_7805:.1f} °C（θJA {TH_7805:.0f} °C/W），用 §6.4 的 23.9 °C/W 则 {PD_7805*23.9:.1f} °C")
assert PSPK_D < 0.06 and PSPK_SQ > 0.5

# TPA3116D2
TPA12 = p_btl(12, 8, 2 * RDS_TPA)
TPA21 = p_btl(21, 4, 2 * RDS_TPA)
print(f"[数值] TPA3116D2：12 V/8 Ω 满幅 {TPA12:.2f} W；21 V/4 Ω {TPA21:.1f} W（数据手册 50 W @ 10 % THD）；12 V 空载 {12*ICC_TPA:.2f} W")
# 练习 5（选型迁移）：12 V 电源、4 Ω 喇叭、要 3 W
SEL_LM_P = p_se(12, 4, VLOSS)
SEL_LM_PD = pd_se_max(12, 4)
SEL_TPA_P = p_btl(12, 4, 2 * RDS_TPA)
SEL_I3 = np.sqrt(3 / 4)
SEL_TPA_COND = SEL_I3 ** 2 * 2 * RDS_TPA
print(f"[数值] 选型 12 V/4 Ω/3 W：LM386 单端最大 {SEL_LM_P:.2f} W，最大发热 {SEL_LM_PD:.3f} W → DIP 温升 {SEL_LM_PD*TH_PDIP:.0f} °C；"
      f"TPA3116D2 满幅 {SEL_TPA_P:.1f} W，3 W 时电流有效值 {SEL_I3:.3f} A，导通损耗 {SEL_TPA_COND:.2f} W + 空载 {12*ICC_TPA:.2f} W")


def _shrink(name):
    """原理图线条多、PNG 偏大：在本节自己的 img 里把它转成 256 色调色板 PNG。"""
    from PIL import Image
    path = os.path.join(HERE, "..", "..", "45-audio-amp-ics", "img", name)
    Image.open(path).convert("RGB").quantize(256).save(path, optimize=True)
    print(f"[压缩] {name} → {os.path.getsize(path) // 1024} KB")


def save(fig, name):
    return fs.save(fig, N, name)


# =============================== page1 ===============================
# ---------- 图 45-p1-1：三颗芯片的电源电压范围 ----------
def p1_1():
    rows = [("LM386N-1 / N-3", 4, 12, 15, fs.C["vin"]),
            ("LM386N-4", 5, 18, 22, fs.C["vin"]),
            ("PAM8403", 2.5, 5.5, 6.0, fs.C["vout"]),
            ("TPA3116D2", 4.5, 26, 30, fs.C["third"])]
    fig, ax = plt.subplots(figsize=(7.4, 3.3))
    for i, (nm, lo, hi, amax, c) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, hi - lo, left=lo, height=0.5, color=c, alpha=0.85)
        ax.plot([amax, amax], [y - 0.32, y + 0.32], color=fs.C["bad"], lw=2.2)
        ax.text(amax + 0.4, y, f"绝对最大 {amax:g} V", va="center", fontsize=8.5, color=fs.C["bad"])
        ax.text(lo - 0.3, y, f"{lo:g}–{hi:g} V", va="center", ha="right", fontsize=8.5)
        print(f"[图 45-p1-1] {nm}：推荐 {lo}–{hi} V，绝对最大 {amax} V")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.axvline(9, **fs.LS["ref"]); ax.axvline(12, **fs.LS["good"])
    ax.text(9, 3.55, "实验 9 V", ha="center", fontsize=8.5, color="0.35")
    ax.text(12, 3.55, "本书上限 12 V", ha="left", fontsize=8.5)
    ax.text(5, -0.75, "↑ 5 V（7805 稳压后给 PAM8403）", ha="left", fontsize=8.5, color=fs.C["vout"])
    ax.axvline(5, color=fs.C["vout"], ls=":", lw=0.9)
    ax.set_xlim(-1, 36); ax.set_ylim(-1.0, 3.9)
    fs.axlabels(ax, "电源电压", "V", None, None)
    ax.set_ylabel("")
    save(fig, "45_p1_1_supply.png")


# ---------- 图 45-p1-2：单端（SE）与 BTL：同一个电源、同一只 8 Ω 喇叭 ----------
def p1_2():
    v = np.linspace(2, 14, 200)
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(v, p_se(v, 8), **fs.LS["vin"], label="单端 SE（理想：峰值 = 电源/2）")
    ax.plot(v, p_btl(v, 8), **fs.LS["vout"], label="BTL（理想：峰值 = 电源）")
    ax.plot(v, p_se(v, 8, VLOSS), **fs.LS["third"], label="LM386（离电源轨各 1.15 V）")
    vb = np.linspace(2.5, 5.5, 50)
    ax.plot(vb, p_btl(vb, 8, RDS_PAM), **fs.LS["fb"], label="PAM8403（扣掉 0.32 Ω 导通电阻）")
    pts = [(6, 0.325, "LM386N-1\n0.325 W"), (9, 0.7, "LM386N-3\n0.7 W"), (5, 1.8, "PAM8403\n1.8 W")]
    for x, y, t in pts:
        ax.plot(x, y, "o", color="k", ms=5)
        ax.annotate(t, (x, y), xytext={6: (6, -22), 9: (-62, 8), 5: (-8, 8)}[x], ha="left" if x != 5 else "right",
                    textcoords="offset points", fontsize=8)
    ax.plot([], [], "o", color="k", ms=5, label="黑点：数据手册（10 % 失真）")
    ax.set_yscale("log"); ax.set_ylim(0.03, 20)
    fs.axlabels(ax, "电源电压", "V", "8 Ω 上的最大正弦功率", "W")
    ax.legend(fontsize=7.6, loc="lower right")
    k = p_btl(9, 8) / p_se(9, 8)
    print(f"[图 45-p1-2] 同电源 BTL/SE = {k:.1f} 倍；5 V/8 Ω：SE {p_se(5, 8):.3f} W，BTL {p_btl(5, 8):.3f} W，PAM8403 计算 {PAM[8]:.3f} W；"
          "黑点 = 数据手册 10 % THD 值")
    assert abs(k - 4) < 1e-9
    save(fig, "45_p1_2_se_btl.png")


# ---------- 图 45-p1-3：效率随输出功率（18 Ω 负载：10 Ω + 8 Ω） ----------
def p1_3():
    sw = SW
    m = sw["a"] <= 0.16 + 1e-9
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(sw["pl"][m], 100 * sw["pl"][m] / sw["pin"][m], **fs.LS["vin"], label="LM386，9 V（SPICE）")
    p = np.linspace(0.002, PAM[18], 200)
    ax.plot(p, 100 * p / pam_pin(p), **fs.LS["vout"], label="PAM8403 芯片本身，5 V（计算）")
    ax.plot(p, 100 * p / via_7805(pam_pin(p)), **fs.LS["third"], label="PAM8403 + 7805，从 9 V（计算）")
    ax.axvline(P01, **fs.LS["ref"])
    for y, c, dx, dy in ((ETA386_01, fs.C["vin"], -0.012, 5), (ETA_PAM01, fs.C["vout"], -0.012, 0),
                         (ETA_7805_01, fs.C["third"], 0.012, -6)):
        ax.plot(P01, 100 * y, "o", color=c, ms=5)
        ax.text(P01 + dx, 100 * y + dy, f"{100*y:.0f} %", fontsize=8.5, va="center", ha="right" if dx < 0 else "left", color=c)
    ax.plot(sw["pl"][m][-1], 100 * sw["pl"][m][-1] / sw["pin"][m][-1], "x", color=fs.C["bad"], ms=8, mew=2)
    ax.text(sw["pl"][m][-1], 100 * sw["pl"][m][-1] / sw["pin"][m][-1] - 9, "LM386 开始削顶", fontsize=8, ha="center", color=fs.C["bad"])
    ax.set_xlim(0, 0.7); ax.set_ylim(0, 100)
    fs.axlabels(ax, "10 Ω + 8 Ω 上的输出功率", "W", "效率", "%")
    ax.legend(fontsize=7.8, loc="lower right")
    assert round(100 * ETA_7805_01) == 25, "page1 正文写「约 25%」，与图上标注同步"
    print(f"[图 45-p1-3] 0.1 W：LM386 {ETA386_01*100:.1f} %，PAM8403 {ETA_PAM01*100:.1f} %，+7805 {ETA_7805_01*100:.1f} %；"
          f"LM386 削顶前 {sw['pl'][m][-1]:.3f} W 效率 {100*sw['pl'][m][-1]/sw['pin'][m][-1]:.1f} %")
    save(fig, "45_p1_3_efficiency.png")


# =============================== page2 ===============================
def _res(ax, p, q, text, side=1, fs_=8.5):
    """方框图里的小电阻：p→q 的线段中间画一个小矩形，旁边写阻值。"""
    (x1, y1), (x2, y2) = p, q
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    horiz = abs(x2 - x1) >= abs(y2 - y1)
    ax.plot([x1, x2], [y1, y2], color="k", lw=1.2, zorder=2)
    w, h = (0.7, 0.26) if horiz else (0.26, 0.7)
    ax.add_patch(Rectangle((mx - w / 2, my - h / 2), w, h, fc="w", ec="k", lw=1.2, zorder=3))
    if horiz:
        ax.text(mx, my + 0.22 * side, text, ha="center", va="bottom" if side > 0 else "top", fontsize=fs_)
    else:
        ax.text(mx + 0.22 * side, my, text, ha="left" if side > 0 else "right", va="center", fontsize=fs_)


def _pin(ax, xy, n, name, side="left"):
    x, y = xy
    ax.add_patch(Rectangle((x - 0.13, y - 0.13), 0.26, 0.26, fc="#2b2b2b", ec="k", zorder=4))
    dx = {"left": -0.22, "right": 0.22, "bottom": 0, "top": 0}[side]
    dy = {"bottom": -0.25, "top": 0.25}.get(side, 0)
    ha = {"left": "right", "right": "left"}.get(side, "center")
    va = {"bottom": "top", "top": "bottom"}.get(side, "center")
    ax.text(x + dx, y + dy, f"{n} 脚 {name}", ha=ha, va=va, fontsize=8.5, zorder=5)


# ---------- 图 45-p2-1：LM386 内部的增益网络（简化） ----------
def p2_1():
    fig, ax = fs.diagram(8.0, 4.4)
    ax.add_patch(FancyBboxPatch((1.2, 0.4), 6.6, 3.6, boxstyle="round,pad=0.05", fc="#f4f4f4", ec="0.5", ls="--"))
    ax.text(1.35, 3.8, "LM386 芯片内部（简化）", fontsize=9, color="0.35")
    b_in = fs.box(ax, 2.7, 2.6, "输入级\n（差分放大）", w=1.7, h=1.0)
    b_out = fs.box(ax, 6.2, 2.6, "放大 + 输出级", w=1.9, h=1.0, fc=fs.C["fill2"])
    fs.arrow(ax, b_in["r"], b_out["l"])
    _pin(ax, (1.2, 2.9), 3, "+IN"); _pin(ax, (1.2, 2.3), 2, "−IN")
    ax.plot([1.2, 1.85], [2.9, 2.9], "k", lw=1.2); ax.plot([1.2, 1.85], [2.3, 2.3], "k", lw=1.2)
    _pin(ax, (7.8, 2.6), 5, "VOUT", "right")
    ax.plot([7.15, 7.8], [2.6, 2.6], "k", lw=1.2)
    # 反馈 15 kΩ：5 脚 → 1 脚节点
    ax.plot([7.5, 7.5], [2.6, 1.6], "k", lw=1.2)
    _res(ax, (7.5, 1.6), (4.6, 1.6), "15 kΩ（反馈）", side=1)
    ax.plot([4.6, 4.6], [1.6, 0.4], "k", lw=1.2)
    _pin(ax, (4.6, 0.4), 1, "GAIN", "bottom")
    _res(ax, (4.6, 0.95), (3.0, 0.95), "1.35 kΩ", side=1)
    ax.plot([3.0, 3.0], [0.95, 0.4], "k", lw=1.2)
    _pin(ax, (3.0, 0.4), 8, "GAIN", "bottom")
    _res(ax, (3.0, 0.95), (3.0, 2.1), "150 Ω", side=-1)
    ax.plot([4.6, 4.6], [0.95, 0.95], "k")
    ax.text(5.0, 0.62, "1、8 脚之间接 10 µF：\n把 1.35 kΩ 短路", fontsize=8, color=fs.C["bad"], va="center")
    g20 = 2 * 15e3 / (150 + 1.35e3); g200 = 2 * 15e3 / 150
    ax.text(1.2, 4.75, f"不接电容：增益 = 2 × 15 kΩ ÷ (150 Ω + 1.35 kΩ) = {g20:.0f}\n"
                       f"1–8 接 10 µF：增益 = 2 × 15 kΩ ÷ 150 Ω = {g200:.0f}", fontsize=9, ha="left", va="top")
    ax.set_xlim(-0.6, 9.8); ax.set_ylim(-0.5, 4.9)
    print(f"[图 45-p2-1] 增益 {g20:.1f} / {g200:.1f}（内部 15 kΩ、150 Ω、1.35 kΩ 取自 SNAS545D 第 1 页的简化原理图 Schematic；15 kΩ、1.35 kΩ 另见 §8.3/§9.2.1.2.1 正文；150 Ω 也可由增益 200 反推）")
    save(fig, "45_p2_1_gain_network.png")


# ---------- 图 45-p2-2：增益的幅频曲线（对数横轴）+ 输出电容的低频下限 ----------
def p2_2():
    ac = csv("ac.csv")
    f = ac["f_Hz"]
    fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    ax = axs[0]
    ax.loglog(f, ac["g20"], **fs.LS["vin"], label="1–8 脚空着（增益 20 档）")
    ax.loglog(f, ac["g200"], **fs.LS["vout"], label="1–8 接 10 µF（增益 200 档）")
    for x, y in ((1e3, NUM["增益 20 档 1 kHz"]), (1e3, NUM["增益 200 档 1 kHz"]), (100, NUM["增益 200 档 100 Hz"]),
                 (20, NUM["增益 200 档 20 Hz"])):
        ax.plot(x, y, "o", color="k", ms=4)
        ax.annotate(f"{y:.0f}", (x, y), xytext=(4, -12), textcoords="offset points", fontsize=8)
    for fc_, g in ((NUM["增益 20 档上限 −3 dB"], 20), (NUM["增益 200 档上限 −3 dB"], 200)):
        ax.plot(fc_, g / np.sqrt(2), "x", color=fs.C["bad"], ms=7, mew=2)
        ax.annotate(f"{fc_/1e3:.0f} kHz" if fc_ > 1e5 else f"{fc_/1e3:.1f} kHz", (fc_, g / np.sqrt(2)),
                    xytext=(-50, -14), textcoords="offset points", fontsize=8, color=fs.C["bad"])
    ax.set_xlim(10, 2e6); ax.set_ylim(5, 400)
    fs.axlabels(ax, "频率", "Hz", "增益（5 脚 ÷ 3 脚）", "倍")
    ax.legend(fontsize=7.5, loc="lower left")
    ax.set_title("芯片本身（SPICE）", fontsize=10)
    ax = axs[1]
    h8 = 1 / np.sqrt(1 + (FC8 / f) ** 2)
    ax.semilogx(f, ac["hp"], **fs.LS["vout"], label="18 Ω（10 Ω + 8 Ω，SPICE）")
    ax.semilogx(f, h8, **fs.LS["third"], label="只接 8 Ω（公式）")
    ax.axhline(1 / np.sqrt(2), **fs.LS["ref"])
    for fc_, c in ((FC18, fs.C["vout"]), (FC8, fs.C["third"])):
        ax.plot(fc_, 1 / np.sqrt(2), "o", color=c, ms=5)
        ax.annotate(f"{fc_:.0f} Hz", (fc_, 1 / np.sqrt(2)), xytext=(6, -14), textcoords="offset points", fontsize=8, color=c)
    ax.set_xlim(5, 20e3); ax.set_ylim(0, 1.1)
    fs.axlabels(ax, "频率", "Hz", "喇叭一侧 ÷ 5 脚", None)
    ax.legend(fontsize=7.5, loc="lower right")
    ax.set_title("220 µF 输出电容（高通）", fontsize=10)
    print(f"[图 45-p2-2] 增益 20：1 kHz {NUM['增益 20 档 1 kHz']:.2f}，上限 {NUM['增益 20 档上限 −3 dB']/1e3:.0f} kHz；"
          f"增益 200：1 kHz {NUM['增益 200 档 1 kHz']:.1f}，100 Hz {NUM['增益 200 档 100 Hz']:.1f}，20 Hz {NUM['增益 200 档 20 Hz']:.1f}，上限 {NUM['增益 200 档上限 −3 dB']/1e3:.1f} kHz；"
          f"220 µF 下限 18 Ω {FC18:.1f} Hz、8 Ω {FC8:.1f} Hz")
    save(fig, "45_p2_2_gain_freq.png")


# ---------- 图 45-p2-3：芯片发热随输出功率（9 V、18 Ω） ----------
def p2_3():
    sw = SW
    m = sw["a"] <= 0.16 + 1e-9
    vp = np.linspace(0, VP_LAB, 200)
    pl = vp ** 2 / (2 * RL)
    pc = VS * vp / (np.pi * RL) + VS * IQ - pl
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(pl, pc, **fs.LS["good"], label="公式（B 类 + 静态电流）")
    ax.plot(sw["pl"][m], sw["pc"][m], "o", color=fs.C["vout"], ms=4, label="SPICE 扫描")
    ax.plot(sw["pl"][~m], sw["pc"][~m], "x", color=fs.C["bad"], ms=5, label="SPICE：已削顶")
    pk = NUM["芯片发热最大值（扫描）"]
    i = int(np.argmax(sw["pc"]))
    ax.annotate(f"最大 {pk:.3f} W", (sw["pl"][i], pk), xytext=(-20, 12), textcoords="offset points", fontsize=8.5)
    ax.axhline(VS * IQ, **fs.LS["ref"])
    ax.text(0.01, VS * IQ - 0.006, f"没有声音时：9 V × 4.3 mA = {VS*IQ*1e3:.0f} mW", fontsize=8, ha="left", va="top", color="0.35")
    ax.set_xlim(0, 0.36); ax.set_ylim(0, 0.32)
    fs.axlabels(ax, "10 Ω + 8 Ω 上的功率", "W", "芯片发热", "W")
    ax.legend(fontsize=7.8, loc="center right")
    print(f"[图 45-p2-3] 发热最大 {pk:.4f} W（公式 {pd_se_max(VS, RL):.4f} W），在输出 {sw['pl'][i]:.3f} W；空载 {VS*IQ*1e3:.1f} mW")
    save(fig, "45_p2_3_dissipation.png")


# ---------- 图 45-p2-4：PAM8403 的 BTL 输出：两端都在 2.5 V 附近跳 ----------
def p2_4():
    fig, ax = fs.diagram(11.6, 5.0)
    vdd = fs.box(ax, 1.2, 3.8, "+5 V", w=1.1, h=0.5, fc="#fde0d6")
    b1 = fs.box(ax, 3.4, 2.7, "半桥 A\n（上管 + 下管）", w=1.9, h=0.9)
    b2 = fs.box(ax, 3.4, 1.1, "半桥 B\n（上管 + 下管）", w=1.9, h=0.9)
    ax.plot([1.2, 1.2, 2.45], [3.55, 2.7, 2.7], "k", lw=1.2)
    ax.plot([1.2, 1.2, 2.45], [2.7, 1.1, 1.1], "k", lw=1.2)
    ax.text(1.3, 1.9, "两个半桥都接\n5 V 和 GND", fontsize=8, ha="left", va="center")
    for y, nm in ((2.7, "OUT+"), (1.1, "OUT−")):
        ax.plot([4.35, 6.4], [y, y], color=fs.C["vout"], lw=1.6)
        ax.text(4.45, y + 0.12, nm, fontsize=8.5)
    ax.add_patch(Rectangle((6.25, 1.35), 0.3, 1.1, fc="#f6e3b4", ec="0.2"))
    ax.plot([6.4, 6.4], [2.7, 2.45], "k"); ax.plot([6.4, 6.4], [1.35, 1.1], "k")
    ax.text(6.7, 1.9, "10 Ω + 8 Ω 喇叭\n（两端都不接地）", fontsize=8.5, va="center")
    ax.plot([5.4, 5.4], [1.1, 0.25], color=fs.C["bad"], lw=1.4, ls="--")
    ax.text(5.5, 0.35, "×", color=fs.C["bad"], fontsize=16, fontweight="bold", va="center")
    ax.text(5.85, 0.35, "任何一端接 GND = 短路", color=fs.C["bad"], fontsize=8.5, va="center")
    # 小波形（示意，参照 TI SLOA145 §2 的无滤波调制）：每路都是以开关周期中心对称的脉冲
    t = np.linspace(0, 3, 1200)
    ph = t % 1

    def pulse(duty, shift=0.0):
        return (np.abs((ph - shift) % 1 - 0.5) < duty / 2).astype(float)

    cases = ((9.0, "没有输入：两路几乎同相", 0.5, 0.5, 0.035),
             (13.3, "有输入：一宽一窄（示例）", 0.65, 0.35, 0.0))
    res = []
    for x0, ttl, dp, dm, sh in cases:
        w = 3.3
        ax.text(x0, 4.45, ttl, fontsize=8.5, fontweight="bold")
        up, um = pulse(dp), pulse(dm, sh)
        for y0, sq, nm, avg in ((3.25, up, "OUT+ 对 GND", 5 * dp), (1.95, um, "OUT− 对 GND", 5 * dm)):
            ax.plot(x0 + w * t / 3, y0 + 0.7 * sq, color=fs.C["vout"], lw=1.0)
            ax.plot([x0, x0 + w], [y0 + 0.7 * avg / 5, y0 + 0.7 * avg / 5], **fs.LS["ref"])
            ax.text(x0 + w + 0.08, y0 + 0.7 * avg / 5, f"平均 {avg:.2f} V", fontsize=7.5, va="center", color="0.35")
            ax.text(x0, y0 + 0.8, f"{nm}（占空比 {sq.mean()*100:.0f} %）", fontsize=7.5)
        df = up - um
        ax.plot(x0 + w * t / 3, 0.35 + 0.45 * df, color=fs.C["bad"], lw=1.0)
        ax.plot([x0, x0 + w], [0.35, 0.35], color="0.6", lw=0.6)
        ax.text(x0, 1.0, "喇叭两端 = OUT+ − OUT−", fontsize=7.5, color=fs.C["bad"])
        ax.text(x0 + w + 0.08, 0.35, f"平均 {5*df.mean():.2f} V", fontsize=7.5, va="center", color=fs.C["bad"])
        res.append((up.mean(), um.mean(), 5 * up.mean(), 5 * um.mean(), 5 * df.mean()))
    ax.set_xlim(-0.2, 17.6); ax.set_ylim(-0.3, 4.8)
    (a1, b1_, A1, B1, D1), (a2, b2_, A2, B2, D2) = res
    assert abs(A1 - 2.5) < 0.02 and abs(B1 - 2.5) < 0.02 and abs(D1) < 0.02
    assert abs(A2 - 3.25) < 0.02 and abs(B2 - 1.75) < 0.02 and abs(D2 - 1.5) < 0.02
    print(f"[图 45-p2-4] 无输入：占空比 {a1*100:.1f}/{b1_*100:.1f} %，平均 {A1:.2f}/{B1:.2f} V，差 {D1:.3f} V（只剩窄尖峰）；"
          f"有输入示例：{a2*100:.1f}/{b2_*100:.1f} %，平均 {A2:.2f}/{B2:.2f} V，差 {D2:.2f} V")
    save(fig, "45_p2_4_pam_btl.png")



# =============================== page3 ===============================
# ---------- 图 45-p3-1：同一个手机信号，增益 20 和增益 200（SPICE） ----------
def p3_1():
    ph = csv("phone.csv")
    t = (ph["t"] - ph["t"][0]) * 1e3
    fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    ax = axs[0]
    vph = 1.48 * np.sin(2 * np.pi * 1e3 * ph["t"])      # SPICE 信号源 SIN(0 1.48 1k)
    ax.plot(t, vph, **fs.LS["vin"], label="手机输出（满音量，峰值 1.48 V）")
    ax.plot(t, ph["vin"], **fs.LS["fb"], label=f"分压后到 3 脚（峰值 {ph['vin'].max():.3f} V）")
    ax.axhspan(-0.4, 0.4, color=fs.C["hi"], alpha=0.35, lw=0)
    ax.text(2.95, 0.42, "LM386 输入允许范围 ±0.4 V", fontsize=8, ha="right", va="bottom")
    ax.set_xlim(0, 3); ax.set_ylim(-2.7, 1.9)
    fs.axlabels(ax, "时间", "ms", "电压", "V")
    ax.legend(fontsize=7.6, loc="lower center", ncol=1)
    ax.set_title("先经过 10 kΩ / 1 kΩ 分压再进 3 脚", fontsize=10)
    ax = axs[1]
    ax.plot(t, ph["out"], **fs.LS["vout"], label="增益 20：5 脚")
    ax.plot(t, ph["outb"], color=fs.C["bad"], lw=1.4, label="增益 200：5 脚（削顶）")
    for y, txt in ((9, "9 V"), (NUM["增益 200 削顶上沿"], f"{NUM['增益 200 削顶上沿']:.2f} V"),
                   (NUM["增益 200 削顶下沿"], f"{NUM['增益 200 削顶下沿']:.2f} V"), (0, "0 V")):
        ax.axhline(y, **fs.LS["ref"])
        ax.text(3.02, y, txt, fontsize=7.8, va="center", color="0.35")
    ax.set_xlim(0, 3); ax.set_ylim(-0.5, 12.2)
    fs.axlabels(ax, "时间", "ms", "对 GND 的电压", "V")
    ax.legend(fontsize=7.6, loc="upper center", ncol=2)
    ax.set_title("同样输入，增益 200 被电源轨削平", fontsize=10)
    a20 = (ph["out"].max() - ph["out"].min()) / 2
    print(f"[图 45-p3-1] 手机峰值 1.48 V → 3 脚峰值 {ph['vin'].max():.3f} V；增益 20 输出峰值 {a20:.2f} V（中心 {(ph['out'].max()+ph['out'].min())/2:.2f} V）；"
          f"增益 200 削在 {ph['outb'].max():.2f} / {ph['outb'].min():.2f} V")
    assert abs(ph["outb"].max() - 7.85) < 0.03 and abs(ph["outb"].min() - 1.15) < 0.03
    save(fig, "45_p3_1_clipping.png")


# ---------- 图 45-p3-2：三颗芯片出事时怎么办（保护功能对照） ----------
def p3_2():
    fig, ax = fs.diagram(10, 3.9)
    cols = [("LM386", 1.6, "数据手册没写\n过热、短路保护\n\n只能靠你：\n限流电源 + 10 Ω\n+ 控制温升", fs.C["fill2"]),
            ("PAM8403", 5.0, "输出短路 → 立即关输出\n短路去掉后自动恢复\n\n过温 140 °C → 关输出\n降 30 °C 后自动恢复\n\n欠压 ≤ 2.0 V → 关输出", fs.C["fill"]),
            ("TPA3116D2", 8.4, "过流 7.5 A → 输出高阻、锁住\n过温 150 °C → 锁住\n直流检测 → 锁住\n欠压 / 过压 → 自动恢复\n\nFAULTZ 接 SDZ\n→ 锁住后自动重启", "#efe3f0")]
    for nm, x, txt, fc in cols:
        fs.box(ax, x, 3.45, nm, w=2.8, h=0.55, fc=fc, fs=11)
        ax.add_patch(FancyBboxPatch((x - 1.6, 0.15), 3.2, 2.75, boxstyle="round,pad=0.05", fc="w", ec=fs.C["edge"], lw=1.0))
        ax.text(x, 1.52, txt, ha="center", va="center", fontsize=10, linespacing=1.3)
        fs.arrow(ax, (x, 3.17), (x, 2.97))
    ax.set_xlim(-0.2, 10.2); ax.set_ylim(0, 3.85)
    print("[图 45-p3-2] LM386 无保护说明；PAM8403 短路自恢复、OTP 140 °C（回差 30 °C）、UVLO 2.0 V；"
          "TPA3116D2 过流 7.5 A / 过温 150 °C / 直流检测锁存，UVLO/OVP 自恢复")
    save(fig, "45_p3_2_protection.png")


# ---------- 图 45-p3-3：温升 = 发热 × 热阻 ----------
def p3_3():
    rows = []
    for k, v, r in PD_ROWS:
        rows.append((f"LM386 DIP\n{k}", PD[k], TH_PDIP, PD_PDIP))
        rows.append((f"LM386 SOIC\n{k.replace('（本实验）', '（同电路换 SOIC）')}", PD[k], TH_SOIC, PD_SOIC))
    rows.append(("PAM8403\n5 V、18 Ω 单声道", PD_PAM_FULL, TH_PAM, None))
    rows.append(("PAM8403\n5 V、8 Ω 双声道", PD_PAM8, TH_PAM, None))
    rows.append(("LM7805（不加散热片）\n给满幅 PAM8403 供电", PD_7805, TH_7805, None))
    fig, ax = plt.subplots(figsize=(7.6, 4.9))
    y = np.arange(len(rows))[::-1]
    dts = np.array([p * th for _, p, th, _ in rows])
    over = np.array([lim is not None and p > lim for _, p, _, lim in rows])
    cols = [fs.C["bad"] if o or d > 100 else (fs.C["vout"] if d > 40 else fs.C["vin"]) for d, o in zip(dts, over)]
    ax.barh(y, dts, color=cols, height=0.62)
    for yi, (nm, p, th, lim), d, o in zip(y, rows, dts, over):
        t = f"{p:.2f} W × {th:g} °C/W = {d:.0f} °C"
        if o:
            t += f"　× 超过封装上限 {lim} W"
        ax.text(d + 1.5, yi, t, va="center", fontsize=7.8, color=fs.C["bad"] if o else "k")
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=7.6)
    ax.axvline(45, **fs.LS["ref"])
    ax.text(45, len(rows) - 0.35, "环境 25 °C 时芯片约 70 °C", fontsize=7.8, color="0.35", ha="center")
    ax.set_xlim(0, 230)
    fs.axlabels(ax, "温升（比环境高多少）", "°C", None, None)
    for (nm, p, th, lim), d in zip(rows, dts):
        print(f"[图 45-p3-3] {nm.replace(chr(10), ' ')}：{p:.3f} W × {th} = {d:.1f} °C" + (f"（封装上限 {lim} W）" if lim else ""))
    save(fig, "45_p3_3_temp_rise.png")



# =============================== page4 动手实验篇 ===============================
# 面包板工具（与 44_figs.py 同一套画法，复制过来，不 import 别的节点脚本）
BB_Y = {r: 5.6 - i for i, r in enumerate("abcde")}
BB_Y.update({r: -1.4 - i for i, r in enumerate("fghij")})
BB_Y.update({"T+": 8.6, "T-": 7.7, "B-": -6.7, "B+": -7.6})
WIRE = dict(pos=(fs.C["bad"], "正电源"), gnd=("#000000", "地（0 V）"), neg=(fs.C["third"], "负电源"),
            sig=(fs.C["vin"], "输入信号"), out=(fs.C["vout"], "输出"), fb=(fs.C["fb"], "反馈 / 其他连线"))


class Breadboard:
    def __init__(self, ncol=30, title=None, size=(10, 6.4), rails=("+", "−", "−", "+")):
        self.ncol, self.used = ncol, set()
        self.fig, self.ax = plt.subplots(figsize=size)
        ax = self.ax
        ax.add_patch(FancyBboxPatch((0.2, -8.3), ncol + 0.6, 17.6, boxstyle="round,pad=0.1",
                                    fc="#f7f5ef", ec="0.55", lw=1.0))
        ax.add_patch(Rectangle((0.4, -0.55), ncol + 0.2, 0.7, fc="#e4e0d6", ec="none"))   # 中间凹槽
        for key, lab in zip(("T+", "T-", "B-", "B+"), rails):
            y = BB_Y[key]
            col = fs.C["third"] if lab == "+5 V" else fs.C["bad"] if lab.startswith("+") else ("#000000" if lab in ("−", "GND", "0 V") else fs.C["third"])
            ax.plot([0.6, ncol + 0.4], [y + 0.42, y + 0.42], color=col, lw=1.0)
            ax.text(0.0, y, lab, ha="right", va="center", fontsize=10, color=col, fontweight="bold")
            for c in range(1, ncol + 1):
                if c % 6:
                    ax.add_patch(Circle((c, y), 0.12, fc="0.72", ec="none"))
        for r in "abcdefghij":
            y = BB_Y[r]
            ax.text(0.15, y, r, ha="right", va="center", fontsize=8, color="0.35")
            ax.text(ncol + 0.85, y, r, ha="left", va="center", fontsize=8, color="0.35")
            for c in range(1, ncol + 1):
                ax.add_patch(Circle((c, y), 0.12, fc="0.72", ec="none"))
        for c in range(1, ncol + 1):
            if c == 1 or c % 5 == 0:
                ax.text(c, 6.35, str(c), ha="center", va="bottom", fontsize=7.5, color="0.35")
                ax.text(c, -6.15, str(c), ha="center", va="top", fontsize=7.5, color="0.35")
        ax.set_xlim(-3.4, ncol + 4.8)
        ax.set_ylim(-11.2, 11.6)
        ax.set_aspect("equal")
        ax.axis("off")
        if title:
            ax.set_title(title, fontsize=11)

    def xy(self, h):
        """'e10' → 第 10 列 e 排；'T+3' / 'B-7' → 上（T）/ 下（B）电源轨第 3 / 7 列。"""
        if h[0] in "TB" and h[1] in "+-":
            c = int(h[2:])
            assert 1 <= c <= self.ncol and c % 6 != 0, f"电源轨孔 {h} 不存在（第 6、12、18、24 列是轨的分组空档）"
            return float(c), BB_Y[h[:2]]
        return float(h[1:]), BB_Y[h[0]]

    def _hole(self, p):
        x, y = self.xy(p) if isinstance(p, str) else p
        if isinstance(p, str):
            self.ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=4))
        return x, y

    def wire(self, a, b, kind="fb", via=None):
        """导线：a、b 为孔名或 (x, y)；via 为中间拐点列表。颜色按 kind 取（见 WIRE）。"""
        self.used.add(kind)
        pts = [self._hole(a)] + list(via or []) + [self._hole(b)]
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=WIRE[kind][0], lw=2.4, solid_capstyle="round", zorder=5)

    def part(self, a, b, label, kind="R", lab_side=1):
        """两脚元件：R 电阻、C 电容、E 电解电容（+ 脚在 a）、D 二极管（a 阳 b 阴）、L LED（a 阳）、
        S 按钮、P 小灯泡。画成方框简化符号，标签写在旁边。"""
        (x1, y1), (x2, y2) = self._hole(a), self._hole(b)
        ax = self.ax
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.plot([x1, x2], [y1, y2], color="0.35", lw=1.2, zorder=5)
        fc = dict(R="#d9c7a3", C="#f2d27a", E="#6d8fb5", D="#555555", L="#ffffff", S="#bbbbbb",
                  P="#fff7c2")[kind]
        horiz = abs(x2 - x1) >= abs(y2 - y1)
        w, h = (0.9, 0.5) if horiz else (0.5, 0.9)
        if kind in "LP":
            ax.add_patch(Circle((mx, my), 0.42, fc=fc, ec="0.2", lw=1.0, zorder=6))
        else:
            ax.add_patch(FancyBboxPatch((mx - w / 2, my - h / 2), w, h, boxstyle="round,pad=0.05",
                                        fc=fc, ec="0.2", lw=1.0, zorder=6))
        if kind in "EDL":
            ax.text(x1 + (0.25 if horiz else 0.25), y1 + (0.3 if horiz else 0), "+", fontsize=8,
                    ha="center", va="center", zorder=7, color=fs.C["bad"])
        if lab_side == "r":
            ax.text(max(x1, x2) + 0.3, my, label, ha="left", va="center", fontsize=8.5, zorder=7)
        elif horiz:
            ax.text(mx, my + 0.55 * lab_side, label, ha="center", va="bottom" if lab_side > 0 else "top",
                    fontsize=8.5, zorder=7)
        else:
            ax.text(mx + 0.45 * lab_side, my, label, ha="left" if lab_side > 0 else "right",
                    va="center", fontsize=8.5, zorder=7)

    def chip(self, col, label, npin=8, names=None):
        """DIP 芯片跨在中间凹槽上：第 1 脚在 f 排第 col 列（左下，缺口朝左），逆时针数，
        第 npin 脚在 e 排第 col 列。脚号和脚名写在芯片体上。"""
        half = npin // 2
        ax = self.ax
        y0, y1 = BB_Y["f"] + 0.22, BB_Y["e"] - 0.22
        ax.add_patch(Rectangle((col - 0.5, y0), half, y1 - y0, fc="#2b2b2b", ec="k", zorder=6))
        ax.add_patch(Circle((col - 0.5, (y0 + y1) / 2), 0.28, fc="#f7f5ef", ec="none", zorder=7))
        ax.text(col + (half - 1) / 2, (y0 + y1) / 2, label, color="w", ha="center",
                va="center", fontsize=9, zorder=8)
        for i in range(half):
            for p, row in ((i + 1, "f"), (npin - i, "e")):
                x, y = col + i, BB_Y[row]
                ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=7))
                txt = str(p) + ("\n" + names[p] if names and p in names else "")
                ax.text(x, y0 + 0.08 if row == "f" else y1 - 0.08, txt, ha="center",
                        va="bottom" if row == "f" else "top", fontsize=6, color="w", zorder=8,
                        linespacing=0.9)

    def module(self, x, y, w, h, label, fc="#e6f0f8"):
        """面包板外的模块（电池、信号源、继电器模块等），返回方框中心。"""
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec="0.3",
                                         lw=1.0, zorder=6))
        self.ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8.5, zorder=7)
        return x + w / 2, y + h / 2

    def note(self, x, y, text, **kw):
        kw.setdefault("fontsize", 8)
        kw.setdefault("zorder", 8)
        self.ax.text(x, y, text, **kw)

    def legend(self, loc="lower center"):
        from matplotlib.lines import Line2D
        cname = {fs.C["bad"]: "红", "#000000": "黑", fs.C["third"]: "紫", fs.C["vin"]: "蓝",
                 fs.C["vout"]: "橙", fs.C["fb"]: "绿", fs.C["cur"]: "天蓝"}
        def lab(c, t):                                # 图例写成「用途（色名）」；用途里已有括号时并进同一对括号
            return t[:-1] + f"，{cname[c]}）" if t.endswith("）") else f"{t}（{cname[c]}）"
        hs = [Line2D([], [], color=WIRE[k][0], lw=2.4, label=lab(*WIRE[k])) for k in WIRE if k in self.used]
        self.ax.legend(handles=hs, loc=loc, ncol=len(hs), fontsize=8.5, frameon=False,
                       bbox_to_anchor=(0.5, -0.01))

    def save(self, prefix, name):
        return fs.save(self.fig, prefix, name)

YEL = fs.C["hi"]


def bbp(bb, hole, text, edge="k"):
    """面包板上的测量点：黄色圆圈写编号，红边 = 红表笔插这里，黑边 = 黑表笔插这里。"""
    x, y = bb.xy(hole) if isinstance(hole, str) else hole
    bb.ax.add_patch(Circle((x, y), 0.36, fc=YEL, ec=edge, lw=1.6, zorder=9))
    bb.ax.text(x, y, text, ha="center", va="center", fontsize=8.5, zorder=10)



WIRE.clear()
WIRE.update(pos=(fs.C["bad"], "+9 V"), gnd=("#000000", "GND"), sig=(fs.C["vin"], "音频输入"),
            out=(fs.C["vout"], "功率输出"), fb=(fs.C["fb"], "其他连线"))


# ---------- 图 45-p4-1：面包板 ----------
def p4_1():
    bb = Breadboard(24, "LM386 功放面包板：U1 LM386N（DIP-8）在第 10–13 列；电源、信号源、10 Ω + 喇叭在板外",
                    size=(11.0, 7.4), rails=("+9 V", "GND", "GND", "不用"))
    ax = bb.ax
    ax.set_xlim(-6.2, 37.0)
    ax.set_ylim(-18.6, 13.2)

    def P(a, b, kind, t):
        bb.part(a, b, "", kind)
        (x1, y1), (x2, y2) = bb.xy(a), bb.xy(b)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, t, ha="center", va="center", fontsize=6, zorder=8,
                color="w" if kind == "E" else "k")

    names = {1: "G", 2: "−", 3: "+", 4: "GND", 5: "OUT", 6: "VS", 7: "BYP", 8: "G"}
    bb.chip(10, "U1 LM386", 8, names=names)
    bb.wire("a12", "T+13", "pos", via=[(12, 8.15), (13, 8.15)])   # 6 脚 VS（T+12 是轨的空档，没有孔，所以拐到 T+13）
    P("T+7", "T-7", "E", "C1")                          # 100 µF（+ 接 +9 V）
    P("T+8", "T-8", "C", "C2")                          # 0.1 µF
    P("a11", "T-11", "E", "C3")                         # 7 脚 BYPASS 10 µF（+ 接 7 脚）
    bb.wire("c10", "c9", "fb")                          # 8 脚 → 第 9 列上半
    bb.wire("h10", "h9", "fb")                          # 1 脚 → 第 9 列下半
    P("g9", "d9", "E", "C5")                            # 1–8 脚 10 µF（+ 接 1 脚一侧）：拔掉 = 增益 20
    bb.wire("j11", "B-11", "gnd")                       # 2 脚 −IN 接地
    bb.wire("j13", "B-13", "gnd")                       # 4 脚 GND
    P("b13", "b18", "E", "C4")                          # 输出 220 µF（+ 接 5 脚）
    P("d13", "d15", "R", "Rz")                          # 吸收网络 10 Ω
    P("a15", "T-15", "C", "Cz")                         # 47 nF 到 GND
    # 输入：10 kΩ / 1 kΩ 分压 + 10 kΩ 电位器（三个脚插 f6、f7、f8）
    P("g2", "g5", "R", "Ra")
    P("j5", "B-5", "R", "Rb")
    bb.wire("h5", "h6", "sig")
    ax.add_patch(FancyBboxPatch((5.55, -1.05), 2.9, 1.0, boxstyle="round,pad=0.05", fc="#7da7c9", ec="0.2", zorder=6))
    ax.text(7.0, -0.55, "RP 10 kΩ", ha="center", va="center", fontsize=6.5, zorder=8)
    for c in (6, 7, 8):
        bb._hole(f"f{c}")
        ax.plot([c, c], [-1.05, BB_Y["f"]], color="0.3", lw=1.4, zorder=5)
    bb.wire("i7", "i12", "sig", via=[(7, -3.9), (12, -3.9)])   # 滑动端 → 3 脚
    bb.wire("j8", "B-8", "gnd")
    # 板外：电源 + 电流表
    bb.module(13.0, 9.9, 9.4, 2.0, "9 V 直流电源（限流 0.2 A）", fc="#e6f0f8")
    bb.module(24.5, 9.9, 5.2, 2.0, "电流表\n（直流 mA 档）", fc="#dff0fb")
    bb.wire((22.4, 10.9), (24.5, 10.9), "pos")
    bb.wire((29.7, 10.9), "T+23", "pos", via=[(30.6, 10.9), (30.6, 9.2), (23, 9.2)])
    bb.wire((14.0, 9.9), "T-14", "gnd")
    # 板外：信号源
    bb.module(-6.0, -12.6, 7.4, 2.4, "信号源（手机 / 信号发生器）\n先把音量调到 0", fc="#e6f0f8")
    bb.wire((-1.0, -10.2), "h2", "sig", via=[(-1.0, -3.4)])     # 信号线插 h2（g2 留给 Ra，一孔一线）
    bb.wire((0.6, -10.2), "B-1", "gnd", via=[(0.6, -6.7)])
    # 板外：10 Ω 电阻 + 喇叭
    bb.module(26.2, -0.8, 9.6, 5.0, "10 Ω / 2 W 电阻\n↓\n8 Ω 喇叭\n↓\nGND", fc="#fdeccf")
    bb.wire("a18", (26.2, 3.4), "out", via=[(18, 6.6), (25.0, 6.6), (25.0, 3.4)])
    bb.wire((26.2, 0.0), "T-23", "gnd", via=[(24.6, 0.0), (24.6, 7.25), (23, 7.25)])   # T−24 是空档，接 T−23
    # 上下两条 GND 轨默认不通：这根黑线把 T− 和 B− 连起来（绕到板外右侧，不压别的线）
    bb.wire("T-22", "B-22", "gnd", via=[(22, 8.15), (36.4, 8.15), (36.4, -7.15), (22, -7.15)])
    bb.note(36.2, -4.6, "⑤ 黑线：上下两条\nGND 轨连通\n（T−22 ↔ B−22）", ha="right", va="center", fontsize=7.5)
    # 测量点
    bbp(bb, "a13", "①")
    bbp(bb, "b11", "②")
    bbp(bb, "j12", "③")
    bbp(bb, (31.0, -1.3), "④")
    parts = ("元件表：C1 100 µF/16 V 电解（+ 接 +9 V）　C2 0.1 µF　C3 10 µF 电解（+ 接 7 脚）　C4 220 µF/16 V 电解（+ 接 5 脚）\n"
             "C5 10 µF 电解（+ 接 1 脚，g9 → d9 跨凹槽，c10–c9、h10–h9 两根短线把它接到 8 脚、1 脚）：插上 = 增益 200，拔掉 = 增益 20　Rz 10 Ω + Cz 47 nF（吸收网络）\n"
             "Ra 10 kΩ　Rb 1 kΩ　RP 10 kΩ 电位器（三个脚 f6 / f7 滑动端 / f8）\n"
             "测量点（黑表笔接 GND）：① 5 脚输出　② 7 脚　③ 3 脚输入　④ 10 Ω 和喇叭之间（喇叭上的电压）\n"
             "⑤ 轨间黑线 T−22 → B−22：没有它，4 脚、2 脚和输入分压都和电源负极断开，芯片不上电")
    ax.text(-5.6, -13.6, parts, ha="left", va="top", fontsize=7.4, linespacing=1.6)
    bb.legend()
    print("[图 45-p4-1] U1 第 10 列起；6 脚 a12 → T+13 接 +9 V；轨间黑线 T−22 → B−22；喇叭回线 T−23；信号线 h2；C3 第 11 列；C4 第 13→18 列；Rz/Cz 第 15 列；"
          "分压 Ra 第 2→5 列、Rb 第 5 列；RP f6/f7/f8；滑动端 → 第 12 列下半（3 脚）")
    bb.save(N, "45_p4_1_breadboard.png")



# ---------- LM386 实验电路（page2 图 45-p2-1 分块版、page4 图 45-p4-2 孔位版共用） ----------
def _lm386_schem(d, holes=False, blocks=False):
    """画实验电路。holes=True：在每个节点旁用灰色小字标面包板孔位（与图 45-p4-1 一致）；
    blocks=True：用虚线框把电路分成 5 块（输入分压 / 退耦 / 增益电容 / 输出电容 / 吸收网络）。"""
    def H(xy, text, loc="right", ofst=0.15):
        if holes:
            colnote(d, xy, text, loc=loc, ofst=ofst)
    # 输入：信号源 → Ra → A 点；Rb 到 GND；RP 跨 A 点与 GND，滑动端 → 3 脚
    d += elm.SourceSin().endpoints((0.4, -1.6), (0.4, 1.0)).label("信号源\n（手机）", loc="bottom", fontsize=9)
    d += elm.Ground().at((0.4, -1.6))
    d += elm.Line().at((0.4, 1.0)).to((0.4, 2.0))
    d += elm.Resistor().endpoints((0.4, 2.0), (3.4, 2.0)).label("Ra 10 kΩ", loc="top", fontsize=9)
    H((0.4, 2.0), "h2 → g2", "left")
    H((0.4, -1.75), "地线 → B−1", "left", 0.35)
    d += elm.Dot().at((3.4, 2.0))
    d += elm.Resistor().endpoints((3.4, 2.0), (3.4, -1.6)).label("Rb\n1 kΩ", loc="bottom", fontsize=9)
    d += elm.Ground().at((3.4, -1.6))
    H((3.4, -1.75), "j5 → B−5", "right", 0.2)
    H((3.4, 2.0), "g5 / h5", "top", 0.45)
    d += elm.Line().at((3.4, 2.0)).to((5.4, 2.0))
    d += elm.Line().at((5.4, 2.0)).to((5.4, 1.3))
    H((5.4, 2.0), "h6 / f6", "top", 0.15)
    pot = elm.Potentiometer().endpoints((5.4, 1.3), (5.4, -1.3))
    d += pot
    lab(d, (4.9, -0.9), "RP 10 kΩ\n（音量）", ha="right", fs_=9)
    d += elm.Line().at((5.4, -1.3)).to((5.4, -1.6))
    d += elm.Ground().at((5.4, -1.6))
    H((5.4, -1.75), "f8 / j8 → B−8", "right", 0.2)
    u = elm.Opamp(leads=True).right().at((9.0, 1.25)).anchor("in1").label("U1\nLM386", loc="center", ofst=(0.25, 0), fontsize=9)
    d += u
    d += elm.Line().at(pot.tap).to(u.in2)
    H((pot.tap[0] + 0.05, pot.tap[1]), "f7 / i7", "top", 0.12)
    H((8.2, 0.0), "i12 / f12", "bottom", 0.12)
    lab(d, (8.75, -0.3), "3", ha="center", fs_=8)
    lab(d, (8.75, 1.55), "2", ha="center", fs_=8)
    d += elm.Line().at(u.in1).to((8.4, 1.25))
    d += elm.Ground().at((8.4, 1.25))
    H((8.2, 0.85), "2 脚接地：f11 / j11 → B−11", "left", 0.1)   # 紧贴 2 脚地符号，避开 C2 的地
    # 6 脚电源 + C1、C2
    vx = u.vd[0]
    d += elm.Line().at(u.vd).to((vx, 3.6))
    d += elm.Vdd().at((vx, 3.6)).label("+9 V（限流 0.2 A，串电流表）", fontsize=9)
    H((vx, 3.75), "e12 / a12 → T+13", "right", 0.12)
    lab(d, (vx + 0.15, 1.85), "6", ha="left", fs_=8)
    d += elm.Dot().at((vx, 3.0))
    d += elm.Line().at((vx, 3.0)).to((6.4, 3.0))
    for x, t in ((6.4, "C1\n100 µF"), (7.6, "C2\n0.1 µF")):
        d += elm.Dot().at((x, 3.0)) if x != 6.4 else elm.Line().at((x, 3.0)).to((x, 3.0))
        d += elm.Capacitor(polar=(x == 6.4)).endpoints((x, 3.0), (x, 2.1)).label(t, loc="bottom", fontsize=8.5)
        d += elm.Ground().at((x, 2.1))
    H((6.4, 3.0), "T+7 / T−7", "top", 0.12)
    H((7.6, 3.0), "T+8 / T−8", "top", 0.12)
    # 4 脚 GND
    d += elm.Line().at(u.vs).to((u.vs[0], -1.6))
    d += elm.Ground().at((u.vs[0], -1.6))
    lab(d, (u.vs[0] - 0.15, -0.75), "4", ha="right", fs_=8)
    H((u.vs[0] - 0.1, -1.3), "f13 / j13\n→ B−13", "left", 0.12)
    # 7 脚 BYPASS → C3
    d += elm.Line().at(u.n1).to((u.n1[0], -0.9))
    d += elm.Capacitor(polar=True).endpoints((u.n1[0], -0.9), (u.n1[0], -2.1)).label("C3 10 µF", loc="bottom", fontsize=8.5)
    d += elm.Ground().at((u.n1[0], -2.1))
    lab(d, (u.n1[0] + 0.15, -0.35), "7", ha="left", fs_=8)
    H((u.n1[0] + 0.1, -2.05), "e11 / a11 → T−11", "right", 0.25)
    # 1、8 脚 GAIN → C5
    d += elm.Line().at(u.n2).to((u.n2[0], 2.4))
    d += elm.Line().at(u.n2a).to((u.n2a[0], 1.6))
    d += elm.Line().at((u.n2a[0], 1.6)).to((12.6, 1.6))
    d += elm.Line().at((12.6, 1.6)).to((12.6, 2.4))
    d += elm.Capacitor(polar=True).endpoints((u.n2[0], 2.4), (12.6, 2.4))
    lab(d, (12.9, 2.75 if not holes else 3.05), "C5 10 µF\n（拔掉 = 增益 20）", ha="left", fs_=8.5)
    lab(d, (u.n2[0] - 0.15, 2.0), "1", ha="right", fs_=8)
    lab(d, (12.75, 2.0), "8", ha="left", fs_=8)
    H((13.1, 2.15), "C5 左端（1 脚）f10 / h10 → h9 / g9", "right", 0.0)
    H((12.6, 1.6), "8 脚 e10 / c10 → c9 / d9", "right", 0.12)
    # 5 脚输出 → 吸收网络、C4、10 Ω、喇叭
    d += elm.Line().at(u.out).to((13.6, u.out[1]))
    yo = u.out[1]
    lab(d, (u.out[0] + 0.1, yo + 0.3), "5", ha="left", fs_=8)
    d += elm.Dot().at((13.6, yo))
    d += elm.Resistor().endpoints((13.6, yo), (13.6, -0.9)).label("Rz\n10 Ω", loc="bottom", fontsize=8.5)
    d += elm.Capacitor().endpoints((13.6, -0.9), (13.6, -2.1)).label("Cz\n47 nF", loc="bottom", fontsize=8.5)
    d += elm.Ground().at((13.6, -2.1))
    H((15.15, yo - 0.9), "← 5 脚 e13 / a13 / b13 / d13", "right", 0.0)
    H((13.6, -0.9), "d15 / a15", "left", 0.12)
    H((13.6, -2.35), "Cz → T−15", "left", 0.3)
    d += elm.Capacitor(polar=True).endpoints((13.6, yo), (16.0, yo)).label("C4 220 µF", loc="top", fontsize=8.5)
    H((16.0, yo), "b18 / a18", "bottom", 0.15)
    d += elm.Resistor().endpoints((16.0, yo), (18.6, yo)).label("10 Ω / 2 W", loc="top", fontsize=8.5)
    d += elm.Dot().at((18.6, yo))
    d += elm.Line().at((18.6, yo)).to((19.4, yo))
    sp = elm.Speaker().right().at((19.4, yo)).anchor("in1").label("8 Ω 喇叭", loc="right", fontsize=9)
    d += sp
    d += elm.Line().at(sp.in2).to((19.4, -1.6))
    d += elm.Ground().at((19.4, -1.6))
    H((19.4, -1.75), "回线 → T−23", "right", 0.2)
    if holes:
        probe(d, (14.0, yo), "①", dx=0.8, dy=-0.9)
        probe(d, (u.n1[0], -0.6), "②", dx=0.8, dy=0.0)
        probe(d, (8.0, 0.0), "③", dx=0.0, dy=-1.1)
        probe(d, (18.6, yo), "④", dx=0.0, dy=1.2)
    if blocks:
        def blk(x0, y0, x1, y1, t, tx, ty, ha="left"):
            for a_, b_ in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
                d.add(elm.Line().endpoints(a_, b_).color(fs.C["vin"]).linestyle("--").linewidth(0.9))
            lab(d, (tx, ty), t, ha=ha, fs_=9.5, color=fs.C["vin"])
        blk(-0.9, -2.6, 5.75, 3.0, "块 1　输入分压 + 音量", -0.8, 3.3)
        blk(5.9, 1.55, 8.1, 4.7, "块 2　电源退耦", 6.0, 5.0)
        blk(10.7, 1.35, 12.75, 3.3, "块 3　增益电容", 10.75, 3.6)
        blk(12.95, -3.1, 14.55, 0.25, "块 5　吸收网络", 14.65, -2.9)
        blk(14.7, 0.15, 18.0, 1.75, "块 4　输出电容", 14.75, 2.05)
    return u


# ---------- 图 45-p2-1（page2）：完整外围电路，分 5 块 ----------
def p2_0():
    with drawing(fontsize=10) as d:
        _lm386_schem(d, blocks=True)
        note(d, (0.0, -3.9), "块 1：10 kΩ / 1 kΩ 分压（手机 1.48 V 峰值 → 0.121 V），再经 RP 调音量　"
                             "块 2：C1 100 µF + C2 0.1 µF 稳住 6 脚电源；C3 10 µF 是 7 脚旁路")
        note(d, (0.0, -4.5), "块 3：C5 10 µF，插上 = 增益 200，拔掉 = 增益 20　"
                             "块 4：C4 220 µF 挡住 5 脚 4.5 V 直流，10 Ω 限流　块 5：Rz 10 Ω + Cz 47 nF 防自激")
        save_schem(d, N, "45_p2_0_full_schem.png")
    _shrink("45_p2_0_full_schem.png")
    print("[图 45-p2-0→页面图 45-p2-1] 完整外围电路：块 1 输入分压、块 2 退耦、块 3 增益电容、块 4 输出电容、块 5 吸收网络")


# ---------- 图 45-p4-2：实验电路图（标面包板孔位，与图 45-p4-1 一一对应） ----------
def p4_2():
    with drawing(fontsize=10) as d:
        _lm386_schem(d, holes=True)
        note(d, (0.0, -3.4), "灰色小字 = 面包板孔位（与图 45-p4-1 相同）。所有 GND 符号最后都要回到电源负极：上轨 T−、下轨 B− "
                             "靠轨间黑线 T−22 → B−22 连通。")
        note(d, (0.0, -3.95), "测量点都对 GND 量：① 5 脚输出（静态约 4.5 V）　② 7 脚　③ 3 脚输入　④ 喇叭上的电压。"
                              "C1、C3、C4、C5 都是电解电容，+ 端按图接。")
        save_schem(d, N, "45_p4_2_schem_lab.png")
    _shrink("45_p4_2_schem_lab.png")
    print("[图 45-p4-2] 原理图标孔位：6 脚 a12 → T+13；3 脚 i12；4 脚 j13 → B−13；5 脚 a13/b13/d13；C4− b18；Zobel 中点 a15；RP f6/f7/f8；Ra/Rb 中点 g5/h5 → h6")



# ---------- 图 45-p4-3：示波器上应该看到什么（SPICE，手机满音量，增益 20） ----------
def p4_3():
    ph = csv("phone.csv")
    t = (ph["t"] - ph["t"][0]) * 1e3
    fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    o_mid = (ph["out"].max() + ph["out"].min()) / 2
    o_pk = (ph["out"].max() - ph["out"].min()) / 2
    s_pk = (ph["sp2"].max() - ph["sp2"].min()) / 2
    ax = axs[0]
    ax.plot(t, ph["out"], **fs.LS["vout"], label="① 5 脚（DC 耦合）")
    ax.axhline(o_mid, **fs.LS["ref"])
    ax.text(0.03, o_mid + 0.25, f"中心 {o_mid:.2f} V", fontsize=8, color="0.35")
    ax.set_xlim(0, 3); ax.set_ylim(0, 9)
    fs.axlabels(ax, "时间", "ms", "对 GND 的电压", "V")
    ax.legend(fontsize=7.8, loc="upper right")
    ax.set_title(f"① 骑在 4.5 V 上，峰值 {o_pk:.2f} V", fontsize=10)
    ax = axs[1]
    ax.plot(t, ph["sp2"], **fs.LS["third"], label="④ 喇叭上（C4 后）")
    ax.axhline(0, **fs.LS["ref"])
    ax.set_xlim(0, 3); ax.set_ylim(-2.2, 2.2)
    fs.axlabels(ax, "时间", "ms", "对 GND 的电压", "V")
    ax.legend(fontsize=7.8, loc="upper right")
    ax.set_title(f"④ 围绕 0 V，峰值 {s_pk:.2f} V", fontsize=10)
    print(f"[图 45-p4-3] ① 中心 {o_mid:.2f} V、峰值 {o_pk:.3f} V；④ 峰值 {s_pk:.3f} V（比例 {s_pk/o_pk:.3f}，"
          f"理论 8/(8+10+0.064 Ω 容抗忽略) = {8/18:.3f}）")
    save(fig, "45_p4_3_expected.png")


# ---------- 图 45-p4-4：选做 D 的接线原理图（PAM8403 模块 + 7805，标模块端子） ----------
def p4_4():
    RED = fs.C["bad"]
    with drawing(fontsize=10) as d:
        # 9 V 电源 → 电流表 → 7805
        d += elm.SourceV().endpoints((0, 0.6), (0, 3.0)).label("9 V 直流\n限流 0.3 A", loc="bottom", fontsize=9)
        d += elm.Ground().at((0, 0.6))
        d += elm.Line().at((0, 3.0)).to((0, 4.0))
        d += elm.MeterA().endpoints((0, 4.0), (2.4, 4.0)).label("电流表\n400 mA 档或 10 A 孔", loc="top", fontsize=8.5)
        d += elm.Line().at((2.4, 4.0)).to((3.6, 4.0))
        d += elm.Dot().at((3.0, 4.0))
        d += elm.Capacitor().endpoints((3.0, 4.0), (3.0, 2.6)).label("0.33 µF", loc="bottom", fontsize=8.5)
        d += elm.Ground().at((3.0, 2.6))
        for a_, b_ in (((3.6, 3.5), (5.6, 3.5)), ((5.6, 3.5), (5.6, 4.7)), ((5.6, 4.7), (3.6, 4.7)), ((3.6, 4.7), (3.6, 3.5))):
            d += elm.Line().endpoints(a_, b_)
        lab(d, (4.6, 4.25), "LM7805", ha="center", fs_=9.5)
        lab(d, (4.6, 3.85), "＋散热片", ha="center", fs_=8)
        lab(d, (3.7, 4.0), "1 IN", fs_=7.5)
        lab(d, (5.45, 4.0), "OUT 3", ha="right", fs_=7.5)
        lab(d, (4.7, 3.3), "2 GND", fs_=7.5)
        d += elm.Line().at((4.6, 3.5)).to((4.6, 2.6))
        d += elm.Ground().at((4.6, 2.6))
        lab(d, (4.6, 5.25), "TO-220 正面（字朝自己）从左到右：IN – GND – OUT", ha="center", fs_=8, color=GRAY)
        d += elm.Line().at((5.6, 4.0)).to((9.0, 4.0))
        for x, t, pol in ((6.1, "1 µF", False), (7.5, "22 µF", True)):
            d += elm.Dot().at((x, 4.0))
            d += elm.Capacitor(polar=pol).endpoints((x, 4.0), (x, 2.6)).label(t, loc="bottom", fontsize=8.5)
            d += elm.Ground().at((x, 2.6))
        lab(d, (6.8, 4.3), "5 V（就近接）", ha="center", fs_=8)
        # PAM8403 模块
        for a_, b_ in (((9.0, -1.3), (12.2, -1.3)), ((12.2, -1.3), (12.2, 4.6)), ((12.2, 4.6), (9.0, 4.6)), ((9.0, 4.6), (9.0, -1.3))):
            d += elm.Line().endpoints(a_, b_).color("#2e7d32")
        lab(d, (10.6, 1.9), "PAM8403\n模块", ha="center", fs_=10)
        for y, t in ((4.0, "5V"), (3.2, "GND"), (0.8, "L"), (0.0, "G"), (-0.7, "R（不接）")):
            lab(d, (9.15, y), t, fs_=8)
        for y, t in ((3.4, "L+"), (1.6, "L−"), (-0.2, "R+ / R−（不接）")):
            lab(d, (12.05, y), t, ha="right", fs_=8)
        d += elm.Line().at((9.0, 3.2)).to((8.6, 3.2))
        d += elm.Line().at((8.6, 3.2)).to((8.6, 2.6))
        d += elm.Ground().at((8.6, 2.6))
        # 手机 → 10 kΩ / 1 kΩ 分压 + RP → 模块 L；手机地 → 模块 G
        d += elm.SourceSin().endpoints((0, -3.6), (0, -1.6)).label("手机\n耳机口 L", loc="bottom", fontsize=9)
        d += elm.Line().at((0, -1.6)).to((0, -1.0))
        d += elm.Resistor().endpoints((0, -1.0), (3.0, -1.0)).label("10 kΩ", loc="top", fontsize=8.5)
        d += elm.Dot().at((3.0, -1.0))
        d += elm.Resistor().endpoints((3.0, -1.0), (3.0, -3.6)).label("1 kΩ", loc="bottom", fontsize=8.5)
        d += elm.Line().at((3.0, -1.0)).to((5.0, -1.0))
        pot = elm.Potentiometer().endpoints((5.0, -1.0), (5.0, -3.6))
        d += pot
        lab(d, (4.5, -3.3), "RP 10 kΩ", ha="right", fs_=8.5)
        d += elm.Line().at(pot.tap).to((7.8, pot.tap[1]))
        d += elm.Line().at((7.8, pot.tap[1])).to((7.8, 0.8))
        d += elm.Line().at((7.8, 0.8)).to((9.0, 0.8))
        d += elm.Line().at((0, -3.6)).to((8.4, -3.6))
        d += elm.Line().at((8.4, -3.6)).to((8.4, 0.0))
        d += elm.Line().at((8.4, 0.0)).to((9.0, 0.0))
        for x in (3.0, 5.0):
            d += elm.Dot().at((x, -3.6))
        lab(d, (4.0, -4.0), "手机 GND（线的根部那一节）→ 模块 G", ha="center", fs_=8)
        # 输出：L+ → 10 Ω → 喇叭 → L−，两端都不接地
        d += elm.Line().at((12.2, 3.4)).to((12.8, 3.4))
        d += elm.Dot().at((12.8, 3.4))
        d += elm.Resistor().endpoints((12.8, 3.4), (15.2, 3.4)).label("10 Ω / 1 W", loc="top", fontsize=8.5)
        sp = elm.Speaker().right().at((15.2, 3.4)).anchor("in1").label("8 Ω 喇叭\n≥ 0.5 W", loc="right", fontsize=8.5)
        d += sp
        d += elm.Line().at(sp.in2).to((sp.in2[0], 1.6))
        d += elm.Line().at((sp.in2[0], 1.6)).to((12.2, 1.6))
        d += elm.Dot().at((12.8, 1.6))
        lab(d, (13.3, 0.7), "L− 不接 GND！\n（BTL：L+、L− 都在 2.5 V 附近跳）", fs_=8.5, color=RED)
        probe(d, (12.8, 3.4), "①", dx=0.0, dy=0.9)
        probe(d, (12.8, 1.6), "②", dx=0.0, dy=-0.9)
        note(d, (-0.6, -5.0), "电压表（另一块表，DC 20 V 档）：黑表笔接模块 GND，红表笔点 ① L+、② L−；"
                              "再红 ①、黑 ② 量喇叭两端。")
        note(d, (-0.6, -5.6), "插在 mA / 10 A 孔的那块表只当电流表，不许拿去量电压。"
                              f"带 10 kΩ / 1 kΩ 分压时，手机满音量喇叭约 {PSPK_D*1e3:.0f} mW。")
        save_schem(d, N, "45_p4_4_schem_lab.png")
    _shrink("45_p4_4_schem_lab.png")
    print(f"[图 45-p4-4] 选做 D 接线：7805 IN–GND–OUT，输入 0.33 µF，输出 1 µF + 22 µF；手机经分压 → L、G；"
          f"L+ → 10 Ω → 喇叭 → L−（不接地）；满音量喇叭 {PSPK_D*1e3:.1f} mW")


if __name__ == "__main__":
    import sys as _s
    only = _s.argv[1:]
    for fn in [v for k, v in sorted(globals().items()) if k[:2] in ("p1", "p2", "p3", "p4") and k[2] == "_" and callable(v)]:
        if only and fn.__name__ not in only:
            continue
        fn()
