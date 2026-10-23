"""12 仿真：反相积分器。方波输入 → 三角波输出；输入带一点直流偏置时，理想积分器慢慢漂到饱和，
并联 R_f 的实用积分器则停在一个固定的直流电平上。
运行：/workspace/circuits-venv/bin/python code/12_sim.py   → 12-integrator/img/12_p2_3_drift.png
page2 的代码块是本文件的精简版（不依赖 figstyle）；code/figs/12_figs.py 会调用这里的函数。
模型：理想运放（虚短、虚断），输出被限制在 ±13.5 V（±15 V 供电的示意值，见 P3）。
    电容电流 = 输入电流 − 流过 R_f 的电流： C·ΔV_o/Δt = −V_in/R − V_o/R_f
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np

R = 10e3           # 输入电阻（Ω）
C = 100e-9         # 反馈电容（F）→ RC = 1 ms
RF = 1e6           # 实用积分器并联在电容上的电阻（Ω）
VSAT = 13.5        # 输出上下限（V）
F_SQ = 500.0       # 方波频率（Hz），半周期 1 ms
OFFSET = 0.02      # 输入里混入的直流偏置（V）


def square(t, f=F_SQ, amp=1.0, offset=0.0):
    """±amp 的方波，先正后负，再加上直流偏置。"""
    return np.where((t * f) % 1.0 < 0.5, amp, -amp) + offset


def integrate(t, vin, r=R, c=C, rf=None, vsat=VSAT, v0=0.0):
    """逐小段计算积分器输出。rf=None 表示理想积分器（没有并联电阻）。"""
    dt = t[1] - t[0]
    vo = np.empty_like(vin)
    v = v0
    g = 0.0 if rf is None else 1.0 / rf
    for k in range(len(t)):
        vo[k] = v
        i_c = -vin[k] / r - v * g          # 流进电容（从虚地流向输出一侧）的电流
        v = v + i_c * dt / c               # 电压变化 = 电流 × 时间 ÷ 电容（小段面积 ÷ C）
        v = min(max(v, -vsat), vsat)       # 输出顶到电源附近就不能再变
    return vo


def time_to_sat(t, vo, vsat=VSAT):
    """输出第一次碰到饱和电压的时刻（s），没碰到返回 None。"""
    idx = np.flatnonzero(np.abs(vo) >= vsat - 1e-9)
    return None if len(idx) == 0 else float(t[idx[0]])


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import figstyle as fs
    t = np.arange(0, 1.0, 2e-6)
    vin = square(t, offset=OFFSET)
    vo_ideal = integrate(t, vin)
    vo_prac = integrate(t, vin, rf=RF)
    ts = time_to_sat(t, vo_ideal)
    last = t > 0.9                                   # 最后 0.1 s 已稳定
    mean_p = vo_prac[last].mean()
    pp_p = vo_prac[last].max() - vo_prac[last].min()
    print(f"[数值] RC = {R*C*1e3:.1f} ms，方波 ±1 V {F_SQ:.0f} Hz，直流偏置 {OFFSET*1e3:.0f} mV")
    print(f"[数值] 理想积分器漂移速度 ≈ {OFFSET/(R*C):.0f} V/s，{ts:.3f} s 撞到 −{VSAT} V")
    print(f"[数值] 并联 R_f = {RF/1e6:.0f} MΩ：稳定后平均 {mean_p:.2f} V，峰峰值 {pp_p:.2f} V；"
          f"直流理论值 −R_f/R × 偏置 = {-RF/R*OFFSET:.1f} V")
    assert ts is not None and 0.6 < ts < 0.75
    assert abs(pp_p - 1.0) < 0.02 and abs(mean_p - (-RF / R * OFFSET)) < 0.1
    fig, axs = plt.subplots(3, 1, figsize=fs.SIZE["tall"])
    z = t < 8e-3                                     # 第一行只放大前 8 ms，看清波形形状
    axs[0].plot(t[z] * 1e3, vin[z], **fs.LS["vin"], label="输入：±1 V 方波（+20 mV 偏置，肉眼看不出）")
    axs[0].plot(t[z] * 1e3, vo_ideal[z], **fs.LS["vout"], label="理想积分器输出：三角波")
    axs[0].set_ylabel(fs.qlabel("电压", "V")); axs[0].set_ylim(-1.6, 2.3)
    axs[0].legend(loc="upper right", fontsize=8, ncol=2); axs[0].set_xlabel(fs.qlabel("时间（放大前 8 ms）", "ms"))
    tm = t * 1e3
    axs[1].plot(tm, vo_ideal, **{**fs.LS["bad"], "lw": 0.6, "marker": None}, label="理想积分器（只有 C），1 s 全程")
    fs.ref_h(axs[1], -VSAT, f"−{VSAT} V 饱和", x=0.45)
    fs.ref_v(axs[1], ts * 1e3, f"{ts*1e3:.0f} ms 撞到饱和", y=0.6)
    axs[1].set_ylabel(fs.qlabel("输出", "V")); axs[1].set_ylim(-15, 2.5); axs[1].legend(loc="upper right", fontsize=8)
    axs[2].plot(tm, vo_prac, **{**fs.LS["vout"], "lw": 0.6}, label="实用积分器（C 旁并 $R_f$ = 1 MΩ），1 s 全程")
    fs.ref_h(axs[2], mean_p)
    axs[2].text(500, -3.5, f"三角波的中心稳定在 {mean_p:.2f} V（灰色点线）", ha="center", fontsize=9, color="0.3")
    axs[2].set_ylabel(fs.qlabel("输出", "V")); axs[2].set_ylim(-4, 1.5); axs[2].legend(loc="upper right", fontsize=8)
    axs[2].set_xlabel(fs.qlabel("时间", "ms"))
    print(f"[参考线] 饱和时刻 {ts*1e3:.0f} ms，实用积分器中心 {mean_p:.2f} V")
    fig.tight_layout()
    fs.save(fig, "12", "12_p2_3_drift.png")
