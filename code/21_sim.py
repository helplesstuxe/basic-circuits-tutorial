"""21 仿真：低边 N 沟道 MOS 管开关的栅极充放电（栅极电荷示意模型）和开关损耗。
运行：/workspace/circuits-venv/bin/python code/21_sim.py   → 21-mosfet-switch/img/21_p2_1_gate_charge.png
page2 里的代码块是本文件的精简版（只借用 figstyle 的中文字体设置）；code/figs/21_figs.py 会调用这里的 simulate()。
模型参数是「示意值」，量级参考 IRLZ44N 数据手册（Q_gs = 8.6 nC、R_DS(on) = 25 mΩ @ V_GS = 5 V、V_GS(th) 1.0–2.0 V），
不代表某个型号的精确波形。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np

# ---- 示意模型参数 ----
V_TH = 1.5        # 门限电压 V_GS(th)：电流从这里开始出现（V）
V_PL = 2.8        # 「米勒平台」电压：负载电流全部流过时的 V_GS（V）
Q_GS = 8.6e-9     # 栅极充到平台所需电荷（C）
Q_GD = 12e-9      # 平台期间要搬走的电荷（栅漏电容放电，C）
C_TAIL = 6e-9     # 平台之后的等效栅极电容（F）
R_ON = 0.025      # 完全导通时的 R_DS(on)（Ω，5 V 驱动）
V_DD = 12.0       # 负载电源（V）
I_L = 3.0         # 负载电流（A）


def vgs_of_q(q):
    """栅极电荷 → 栅源电压：先线性上升到平台，平台上不动，之后再线性上升。"""
    q = np.asarray(q, dtype=float)
    return np.where(q < Q_GS, q / Q_GS * V_PL,
                    np.where(q < Q_GS + Q_GD, V_PL, V_PL + (q - Q_GS - Q_GD) / C_TAIL))


def simulate(r_g=100.0, v_drv=5.0, t_on=10e-6, t_end=20e-6, dt=1e-9):
    """驱动电压在 0..t_on 为 v_drv、之后为 0；逐步计算栅极电荷，返回各波形和一次开、关的开关能量。"""
    t = np.arange(0, t_end, dt)
    vd = np.where(t < t_on, v_drv, 0.0)                    # 驱动电压（单片机引脚）
    q = np.zeros_like(t)
    for k in range(1, len(t)):
        ig = (vd[k - 1] - vgs_of_q(q[k - 1])) / r_g        # 栅极电流 = 栅极电阻两端电压 / R_G
        q[k] = max(q[k - 1] + ig * dt, 0.0)                # 电荷累加（不会小于 0）
    vgs = vgs_of_q(q)
    i_d = I_L * np.clip((vgs - V_TH) / (V_PL - V_TH), 0, 1)              # 门限到平台之间电流线性上升
    frac = np.clip((q - Q_GS) / Q_GD, 0, 1)                               # 平台走了多少
    v_ds = np.maximum(V_DD * (1 - frac), i_d * R_ON)                      # 平台期间 V_DS 从 12 V 降到接近 0
    p = v_ds * i_d                                                        # MOS 管瞬时发热功率
    sw = v_ds > 2 * I_L * R_ON                                            # 「没开到底」的时刻
    e_on = float(np.sum(p[sw & (t < t_on)]) * dt)                         # 开通一次的开关能量
    e_off = float(np.sum(p[sw & (t >= t_on)]) * dt)                       # 关断一次的开关能量

    def cross(mask):
        idx = np.flatnonzero(mask)
        return float(t[idx[0]]) if len(idx) else float("nan")
    # 开关时间：从驱动跳变到 V_DS 走完 90%
    t_sw_on = cross((t < t_on) & (v_ds < 0.1 * V_DD))
    t_sw_off = cross((t >= t_on) & (v_ds > 0.9 * V_DD)) - t_on
    # 电流爬升时间 t_ri（开通时漏极电流从 0 升到 3 A）、电流下降时间 t_fi（关断时从 3 A 降到 0）
    on, off = t < t_on, t >= t_on
    t_ri = cross(on & (i_d >= I_L * 0.999)) - cross(on & (i_d > 0))
    t_fi = cross(off & (i_d <= 0)) - cross(off & (i_d < I_L * 0.999))
    return dict(t=t, vd=vd, vgs=vgs, i_d=i_d, v_ds=v_ds, p=p, e_on=e_on, e_off=e_off,
                t_sw_on=t_sw_on, t_sw_off=t_sw_off, t_ri=t_ri, t_fi=t_fi)


def losses(f, e_sw, duty=0.5):
    """PWM 频率 f 下的导通损耗、开关损耗（W）。"""
    p_cond = I_L ** 2 * R_ON * duty
    return p_cond, e_sw * f


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import figstyle as fs
    s = simulate(r_g=100.0)
    us = s["t"] * 1e6
    print(f"[数值] R_G = 100 Ω：开通 {s['t_sw_on']*1e6:.2f} μs，关断 {s['t_sw_off']*1e6:.2f} μs；"
          f"E_on = {s['e_on']*1e6:.1f} μJ，E_off = {s['e_off']*1e6:.1f} μJ")
    print(f"[数值] 栅极峰值电流 = 5 V / 100 Ω = {5/100*1e3:.0f} mA")
    # 手算 t_ri、t_fi：门限 1.5 V → 平台 2.8 V 要搬的电荷 = (2.8 − 1.5)/2.8 × Q_GS
    dq = (V_PL - V_TH) / V_PL * Q_GS
    i_on = (5.0 - (V_TH + V_PL) / 2) / 100.0                 # 开通：平均栅极电流 = (5 V − 平均 V_GS) / R_G
    i_off = ((V_TH + V_PL) / 2) / 100.0                      # 关断：平均放电电流 = 平均 V_GS / R_G（驱动已是 0 V）
    print(f"[数值] 门限→平台的电荷 = {dq*1e9:.2f} nC；手算 t_ri = {dq/i_on*1e6:.2f} μs（平均 {i_on*1e3:.1f} mA），"
          f"t_fi = {dq/i_off*1e6:.2f} μs（平均 {i_off*1e3:.1f} mA）")
    print(f"[数值] 仿真 t_ri = {s['t_ri']*1e6:.2f} μs，t_fi = {s['t_fi']*1e6:.2f} μs")
    v_spike = 1e-3 * I_L / s["t_fi"]
    print(f"[数值] 无续流二极管、L = 1 mH、3 A 在 t_fi 内降到 0：L·ΔI/Δt ≈ {v_spike:.0f} V")
    assert abs(s["t_ri"] - 0.14e-6) < 0.02e-6 and abs(s["t_fi"] - 0.19e-6) < 0.02e-6
    assert abs(dq / i_on - s["t_ri"]) < 0.02e-6 and abs(dq / i_off - s["t_fi"]) < 0.02e-6
    assert v_spike > 10 * 55, "尖峰远超 IRLZ44N 的 55 V 耐压"
    assert 0.5e-6 < s["t_sw_on"] < 1.5e-6, "100 Ω 时开通不到 1 μs"
    assert abs(s["vgs"][int(9e-6 / 1e-9)] - 5.0) < 0.05, "开通 9 μs 后 V_GS 已充到驱动电压 5 V"

    fig, axs = plt.subplots(2, 2, figsize=fs.SIZE["grid"], sharey="row")
    on90 = s["t_sw_on"] * 1e6
    off90 = 10 + s["t_sw_off"] * 1e6
    for col, (x0, x1, title, tx) in enumerate([(-0.2, 2.0, "开通（驱动 0 → 5 V）", on90),
                                                (9.8, 12.0, "关断（驱动 5 → 0 V）", off90)]):
        a1, a2 = axs[0, col], axs[1, col]
        a1.plot(us, s["vd"], **fs.LS["vin"], label="驱动电压")
        a1.plot(us, s["vgs"], **fs.LS["vout"], label="$V_{GS}$")
        fs.ref_h(a1, V_PL, f"平台 {V_PL:.1f} V", x=0.98)
        fs.ref_h(a1, V_TH, f"门限 {V_TH:.1f} V", x=0.98)
        a1.set_title(title, fontsize=10); a1.set_ylim(-0.3, 6.2)
        a2.plot(us, s["v_ds"], **fs.LS["third"], label="$V_{DS}$")
        a2b = a2.twinx()
        a2b.plot(us, s["i_d"], **fs.LS["cur"], label="漏极电流 $I$")
        a2b.set_ylim(-0.125, 3.6)
        if col == 1:
            a2b.set_ylabel(fs.qlabel("电流", "A"))
        else:
            a2b.set_yticklabels([])
        fs.ref_v(a2, tx, f"{tx:.2f} μs")
        a2.set_ylim(-0.5, 14.4)
        for a in (a1, a2):
            a.set_xlim(x0, x1)
        if col == 0:
            fs.axlabels(a2, "时间", "μs", "电压", "V")
        else:
            a2.set_xlabel(fs.qlabel("时间", "μs"))
        if col == 0:
            fs.axlabels(a1, "", None, "电压", "V")
            a1.legend(loc="lower right", fontsize=8)
            h1, l1 = a2.get_legend_handles_labels(); h2, l2 = a2b.get_legend_handles_labels()
            a2.legend(h1 + h2, l1 + l2, loc="center right", fontsize=8)
    print(f"[参考线] 平台 {V_PL:.1f} V，门限 {V_TH:.1f} V，V_DS 走完 90% 的时刻 {on90:.2f} μs、{off90:.2f} μs")
    fs.save(fig, "21", "21_p2_1_gate_charge.png")
