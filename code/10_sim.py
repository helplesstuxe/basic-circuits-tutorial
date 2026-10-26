"""10 仿真：带噪声的慢变输入分别送进「普通比较器」和「施密特比较器（同相回差）」，比较输出翻转次数。
运行：/workspace/circuits-venv/bin/python code/10_sim.py   → 10-voltage-comparator/img/10_p2_2_noise_compare.png
page2 的代码块是本文件的精简版（不依赖 figstyle）；code/figs/10_figs.py 会调用这里的函数。
电路：5 V 单电源，开集电极比较器（如 LM393）+ 上拉电阻 R3；V_ref = 2.5 V 接反相端；
      输入经 R1 接同相端，R2 从输出接回同相端（正反馈）。温度传感器按示意值 0.1 V/°C（25 °C 对应 2.5 V）。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np

VCC = 5.0          # 电源与上拉电压（V）
VREF = 2.5         # 反相端基准电压（V）
R1 = 10e3          # 输入电阻（Ω）
R2 = 100e3         # 正反馈电阻（Ω）
R3 = 2.2e3         # 上拉电阻（Ω），输出为高时与 R2 串联


def thresholds(vref=VREF, r1=R1, r2=R2, vpu=VCC, r3=R3):
    """同相施密特比较器的上、下门限（输出低电平按 0 V）。
    上门限 V_H：输出为低（0 V）时，输入要把同相端抬到 V_ref： V_H = V_ref (R1 + R2) / R2
    下门限 V_L：输出为高时，R2 + R3 这一路接到 V_pu，用叠加原理解出 V_L。"""
    v_h = vref * (r1 + r2) / r2
    r2h = r2 + r3
    v_l = (vref * (r1 + r2h) - vpu * r1) / r2h
    return v_h, v_l


def make_input(sigma=0.04, seed=1, t_end=20.0, dt=1e-2):
    """慢慢升温再降温的传感器电压（2.0 V → 3.0 V → 2.0 V，三角形）加上高斯噪声。"""
    t = np.arange(0, t_end, dt)
    clean = 2.0 + 1.0 * (1 - np.abs(t - t_end / 2) / (t_end / 2))
    rng = np.random.default_rng(seed)
    return t, clean, clean + sigma * rng.standard_normal(len(t))


def comp_plain(vin, vref=VREF):
    """普通比较器（开环）：V+ > V− 输出高（5 V），否则输出低（0 V）。"""
    return np.where(vin > vref, VCC, 0.0)


def comp_schmitt(vin, v_h, v_l, start_high=False):
    """施密特比较器：输出为低时要超过 V_H 才翻高；输出为高时要低于 V_L 才翻低。"""
    out = np.empty_like(vin)
    high = start_high
    for k, v in enumerate(vin):
        if not high and v > v_h:
            high = True
        elif high and v < v_l:
            high = False
        out[k] = VCC if high else 0.0
    return out


def edges(out):
    """输出跳变次数。"""
    return int(np.count_nonzero(np.diff(out) != 0))


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import figstyle as fs
    v_h, v_l = thresholds()
    t, clean, vin = make_input()
    o1 = comp_plain(vin)
    o2 = comp_schmitt(vin, v_h, v_l)
    n1, n2 = edges(o1), edges(o2)
    print(f"[数值] 上门限 V_H = {v_h:.3f} V，下门限 V_L = {v_l:.3f} V，回差 = {v_h - v_l:.3f} V")
    print(f"[数值] 噪声 σ = 40 mV：普通比较器翻转 {n1} 次，施密特比较器翻转 {n2} 次")
    assert abs(v_h - 2.75) < 1e-9
    assert n2 == 2, "施密特比较器一升一降只翻转两次"
    assert n1 > 20, "普通比较器在门限附近反复抖动"
    fig, axs = plt.subplots(3, 1, figsize=fs.SIZE["tall"], sharex=True,
                            gridspec_kw=dict(height_ratios=[1.6, 1, 1]))
    a0, a1, a2 = axs
    a0.plot(t, vin, **fs.LS["vin"], label="传感器电压 $V_{in}$（含噪声）")
    a0.plot(t, clean, **fs.LS["good"], label="无噪声时")
    fs.ref_h(a0, VREF, f"$V_{{ref}}$ {VREF:.1f} V", x=0.01, ha="left")
    fs.ref_h(a0, v_h, f"$V_H$ {v_h:.2f} V", x=0.01, ha="left")
    fs.ref_h(a0, v_l, f"$V_L$ {v_l:.2f} V", x=0.01, ha="left")
    a0.set_ylabel(fs.qlabel("电压", "V")); a0.legend(loc="upper right", fontsize=8)
    a1.plot(t, o1, **fs.LS["bad"], label=f"普通比较器：翻转 {n1} 次")
    a1.set_ylabel(fs.qlabel("输出", "V")); a1.legend(loc="center right", fontsize=8); a1.set_ylim(-0.6, 5.9)
    a2.plot(t, o2, **fs.LS["vout"], label=f"施密特比较器：翻转 {n2} 次")
    a2.set_ylabel(fs.qlabel("输出", "V")); a2.legend(loc="center right", fontsize=8); a2.set_ylim(-0.6, 5.9)
    a2.set_xlabel(fs.qlabel("时间", "s"))
    up = t[np.flatnonzero(np.diff(o2) > 0)[0]]; dn = t[np.flatnonzero(np.diff(o2) < 0)[0]]
    fs.ref_v(a2, up, f"{up:.2f} s"); fs.ref_v(a2, dn, f"{dn:.2f} s")
    print(f"[参考线] 施密特输出翻高 {up:.2f} s，翻低 {dn:.2f} s")
    fs.save(fig, "10", "10_p2_2_noise_compare.png")
