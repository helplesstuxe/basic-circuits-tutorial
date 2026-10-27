"""32 电荷放大器：页面上所有数字的来源。
运行：/workspace/circuits-venv/bin/python code/32_sim.py
只用 numpy；不写任何文件。SPICE 复核见 spice/32/run.py。

模型说明：
- 传感器（压电片 / 注入电容 C_S）= 电荷源 Q 并一只电容；电缆 = 并在输入端的电容 C_C。
- 电压模式：传感器直接接跟随器，V = Q / (C_S + C_C + C_IN)（电荷在几只电容之间分）。
- 电荷模式：反相端 N 被反馈钉在 V_MID，V_out − V_MID = −Q / C_F（有限增益修正见 gain_err）。
- 下限 f_L = 1/(2π R_F C_F)，上限 f_H = 1/(2π R_I (C_p + C_C))（TI SLOA033A §3.2）。
"""
import numpy as np

TW = 2 * np.pi
# ---------------- 实验参数（page4） ----------------
VCC = 9.0                    # 一节 9 V 叠层电池
VMID = VCC / 2               # RM1 = RM2 = 10 kΩ 分压，再经 U1B 跟随器缓冲
C_IN = 3e-12                 # LMC6482 输入电容（与 31 节同一取值）
GBW = 1.5e6                  # LMC6482 增益带宽积（手册电气特性表）
CS = 1e-9                    # 阶段一注入电容 1 nF C0G
CF1 = 10e-9                  # 阶段一反馈电容 10 nF（C0G / 薄膜）
RF = 10e6                    # 可拔的 10 MΩ
CC_LIST = (0.0, 10e-9, 100e-9)   # 「假电缆」：不接 / 10 nF / 100 nF
CS_SLOW, CF_SLOW = 100e-9, 1e-6  # 慢速演示：100 nF 注入，1 µF 反馈（τ = 10 s）
CF2 = 100e-9                 # 阶段二（压电片）反馈电容 100 nF 薄膜
RI = 10e3                    # 压电片串联 10 kΩ
CP_LIST = (10e-9, 20e-9, 30e-9)  # 压电片电容的「假设范围」（页面要求实测）

# 输入偏置电流（典型 / 最大，出处见 page3 参考资料）
IB_TYP = {"LMC6482": 0.02e-12, "TL072": 65e-12, "LM358B": 10e-9, "LM358": 20e-9}
IB_MAX = {"LMC6482": 4e-12, "TL072": 200e-12, "LM358B": 35e-9, "LM358": 250e-9}
D_LEAK_MAX = 25e-9           # 1N4148 反向漏电上限（20 V，25 °C，Vishay 81857）
DMM_R = 10e6                 # 万用表电压挡输入电阻（常见值）


def charge_mode(dv_s, cs=CS, cf=CF1):
    """注入电容远端跳变 dv_s，输出相对 V_MID 的变化（理想运放）。"""
    return -cs * dv_s / cf


def voltage_mode(dv_s, cs=CS, cc=0.0, cin=C_IN):
    """电压模式（跟随器）：同一个跳变，输入节点只分到 cs/(cs+cc+cin)。"""
    return dv_s * cs / (cs + cc + cin)


def gain_err(cin_total, cf, f):
    """电荷模式有限增益误差（%）：1/(1 + (C_F + C_in)/(A·C_F))，A = GBW/f。"""
    a = GBW / f
    return (1 - 1 / (1 + (cf + cin_total) / (a * cf))) * 100


def f_l(rf, cf):
    return 1 / (TW * rf * cf)


def f_h(ri, cp, cc=0.0):
    return 1 / (TW * ri * (cp + cc))


def decay(v0, tau, t):
    return v0 * np.exp(-np.asarray(t) / tau)


def drift(ib, cf):
    """保持模式（拔掉 R_F）下的漂移速度 V/s。"""
    return ib / cf


def pickup(v_mains, c_stray, cf):
    """杂散电容 c_stray 从市电耦合进 N 点：输出幅度 = V·C_stray/C_F（与频率无关）。"""
    return v_mains * c_stray / cf


def noise_gain(cin_total, cf):
    return 1 + cin_total / cf


def mag(f, cs, cf, rf, ri, cp):
    """压电片 → 电荷放大器的幅频（相对中频 C_S/C_F 归一化）：高通 f_L × 低通 f_H。"""
    s = 1j * TW * np.asarray(f)
    hp = s * rf * cf / (1 + s * rf * cf)
    lp = 1 / (1 + s * ri * cp)
    return np.abs(hp * lp)


def report():
    print("== 1) page1：Q = 100 pC，C_p = 1 nF，电缆 0.1 / 1 / 10 nF ==")
    for cc in (0.1e-9, 1e-9, 10e-9):
        print(f"  电压模式 V = Q/(C_p+C_c) = {100e-12/(1e-9+cc)*1e3:6.2f} mV   电荷模式 (C_F 1 nF) = {100e-12/1e-9*1e3:.1f} mV")
    print("\n== 2) 阶段一（保持模式）：C_S 1 nF，C_F 10 nF，V_MID = %.2f V ==" % VMID)
    print(f"  S: V_MID→0 V  ΔV = {-VMID:+.2f} V → B−A = {charge_mode(-VMID):+.4f} V；注入电荷 {CS*VMID*1e9:.2f} nC")
    print(f"  S: V_MID→+9 V ΔV = {VCC-VMID:+.2f} V → B−A = {charge_mode(VCC-VMID):+.4f} V")
    for cc in CC_LIST:
        ge = gain_err(CS + cc + C_IN, CF1, 1.0)
        print(f"  C_C = {cc*1e9:5.0f} nF: 电荷模式 {charge_mode(-VMID):+.4f} V（1 Hz 有限增益误差 {ge:.5f} %）；"
              f"电压模式 {voltage_mode(-VMID, cc=cc):+.4f} V；噪声增益 {noise_gain(CS+cc+C_IN, CF1):.1f}")
    for cc in CC_LIST:
        print(f"  1 kHz 有限增益误差 C_C={cc*1e9:.0f} nF：{gain_err(CS+cc+C_IN, CF1, 1e3):.3f} %")
    print("\n== 3) 插上 R_F 10 MΩ（C_F 10 nF）：τ、f_L、剩余 ==")
    tau1 = RF * CF1
    print(f"  τ = {tau1*1e3:.0f} ms，f_L = {f_l(RF, CF1):.3f} Hz；0.45 V 在 0.1/0.3/1 s 后剩 "
          + " / ".join(f"{decay(0.45, tau1, t)*1e3:.4g} mV" for t in (0.1, 0.3, 1.0)))
    print("\n== 4) 慢速演示：C_S 100 nF，C_F 1 µF，R_F 10 MΩ ==")
    taus = RF * CF_SLOW
    v0 = CS_SLOW * VMID / CF_SLOW
    print(f"  峰值 {v0:.4f} V，τ = {taus:.0f} s；5/10/20/30 s：" + " / ".join(f"{decay(v0, taus, t):.4f} V" for t in (5, 10, 20, 30)))
    print("\n== 5) 阶段二：C_F 100 nF + R_F 10 MΩ；R_I 10 kΩ ==")
    print(f"  τ = {RF*CF2:.1f} s，f_L = {f_l(RF, CF2):.4f} Hz；3 s 后剩 {np.exp(-3):.4f}")
    for cp in CP_LIST:
        print(f"  C_p = {cp*1e9:.0f} nF：f_H = {f_h(RI, cp):7.1f} Hz，噪声增益 1+C_p/C_F = {noise_gain(cp, CF2):.2f}（C_F 100 nF）/ {noise_gain(cp, 1e-9):.0f}（C_F 1 nF）")
    print(f"  输出能装下的电荷（±4.4 V）：C_F 100 nF → {4.4*CF2*1e9:.0f} nC；C_F 1 nF → {4.4*1e-9*1e9:.1f} nC")
    print("\n== 6) 偏置电流：R_F 10 MΩ 上的偏移 / 保持模式漂移（C_F 10 nF） ==")
    for k in IB_TYP:
        print(f"  {k:8s} 偏移 {IB_TYP[k]*RF*1e3:9.4g} / {IB_MAX[k]*RF*1e3:9.4g} mV   漂移 {drift(IB_TYP[k], CF1)*1e3:9.4g} / {drift(IB_MAX[k], CF1)*1e3:9.4g} mV/s"
              f"   顶到轨（4.4 V）用时 {4.4/drift(IB_TYP[k], CF1):9.3g} s（典型）")
    crit = 0.01 * 0.45 / 10
    print(f"  判据：10 s 内漂移不超过 0.45 V 的 1 %（4.5 mV）→ 漂移 ≤ {crit*1e3:.2f} mV/s")
    print("\n== 7) 钳位二极管漏电 × R_F ==")
    print(f"  钳到电源轨：25 nA × 10 MΩ = {D_LEAK_MAX*RF:.2f} V（上限）；× 100 MΩ = {D_LEAK_MAX*100e6:.1f} V")
    print("\n== 8) 万用表（10 MΩ）碰 N 点到 0 V ==")
    i = VMID / DMM_R
    print(f"  电流 {i*1e6:.2f} µA；保持模式漂移 {i/CF1:.0f} V/s；有 R_F 10 MΩ 时输出想移 {i*RF:.2f} V")
    print("\n== 9) 市电耦合：杂散 0.1 pF ==")
    for vm, nm in ((120, "美国 120 V 60 Hz"), (230, "230 V 50 Hz")):
        print(f"  {nm}：C_F 1 nF → {pickup(vm, 0.1e-12, 1e-9)*1e3:.1f} mV，10 nF → {pickup(vm, 0.1e-12, 10e-9)*1e3:.2f} mV，100 nF → {pickup(vm, 0.1e-12, 100e-9)*1e3:.3f} mV")
    print("\n== 10) SBOA287 参考设计复算 ==")
    print(f"  f_L = 1/(2π·240 MΩ·68 pF) = {f_l(240e6, 68e-12):.2f} Hz；f_H = 1/(2π·39.2 kΩ·390 pF) = {f_h(39.2e3, 390e-12)/1e3:.2f} kHz；"
          f"0.35 pC/68 pF = {0.35e-12/68e-12*1e3:.3f} mV/G")
    print("\n== 11) 涡街：流速 ×10 ==")
    print("  频率 ×10，电荷 ∝ v² → ×100；输出 0.01 V 的信号变成 1 V")
    print("\n== 12) 补充（page4 测量表、思考题） ==")
    print(f"  第 5 步 B 对 0 V = {VMID + charge_mode(-VMID):.2f} V；第 6 步 B 对 0 V = {VMID + charge_mode(VCC - VMID):.2f} V")
    print(f"  思考题 2：S1 在①（0 V）时按 SB 复位，起点 B−A = 0；拨到②（+9 V），ΔV = {VCC:+.1f} V → "
          f"B−A = {charge_mode(VCC):+.2f} V，B 对 0 V = {VMID + charge_mode(VCC):.2f} V")
    print(f"  思考题 3：C_F 1 nF + R_F 10 MΩ：f_L = {f_l(RF, 1e-9):.2f} Hz，τ = {RF*1e-9*1e3:.0f} ms；灵敏度是 100 nF 时的 {CF2/1e-9:.0f} 倍")
    print(f"  R_I·C_S：阶段一 {RI*CS*1e6:.0f} µs；慢速演示 {RI*CS_SLOW*1e3:.0f} ms（都远小于读数时间）")
    print("\n== 13) 不加 R_I 时运放输出推的电容（LMC6482 手册：单位增益约只能直接带 100 pF） ==")
    ser = lambda a, b: a * b / (a + b)
    c1 = ser(CF1, CS)
    print(f"  阶段一 C_F 10 nF 串 C_S 1 nF = {c1*1e9:.3f} nF，是 100 pF 的 {c1/100e-12:.1f} 倍；按住 SB 时直接推 C_S 1 nF（{CS/100e-12:.0f} 倍）")
    for cp in CP_LIST:
        c2 = ser(CF2, cp)
        print(f"  阶段二 C_F 100 nF 串 C_p {cp*1e9:.0f} nF = {c2*1e9:.2f} nF，是 100 pF 的 {c2/100e-12:.0f} 倍；按住 SB 时直接推 C_p（{cp/100e-12:.0f} 倍）")


if __name__ == "__main__":
    report()
