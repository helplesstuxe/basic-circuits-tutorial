"""P2 仿真：① 二极管串电阻电路的工作点；② NPN 三极管开关的「输入电压 → 输出电压」曲线。
运行：/workspace/circuits-venv/bin/python code/P2_sim.py   → P2-semiconductor-basics/img/P2_p2_5_bjt_transfer.png
page2 里的代码块是本文件的精简版（不依赖 figstyle）。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np
import matplotlib.pyplot as plt
import figstyle as fs

VT = 0.02585                     # 热电压，室温约 25.85 mV
IS = 1e-14                       # 二极管反向饱和电流（示意值）


def diode_point(vs, r):
    """电源 vs 串电阻 r 再串一只二极管：二分法解 vs = I·r + V_D，且 I = IS·(e^(V_D/VT) − 1)。"""
    lo, hi = 0.0, min(vs, 1.0)
    for _ in range(60):
        vd = (lo + hi) / 2
        i_diode = IS * (np.exp(vd / VT) - 1)      # 二极管在这个电压下想流的电流
        i_res = (vs - vd) / r                     # 电阻在这个电压下能给的电流
        lo, hi = (vd, hi) if i_diode < i_res else (lo, vd)
    return vd, (vs - vd) / r


def bjt_switch(vin, rb=10e3, rc=1e3, vcc=5.0, beta=100.0, vbe=0.7, vcesat=0.2):
    """NPN 开关的分段模型：返回 (I_B, I_C, V_CE)。"""
    ib = max(0.0, (vin - vbe) / rb)              # 基极电流：V_in 超过 0.7 V 才有
    ic = min(beta * ib, (vcc - vcesat) / rc)     # 放大区 β·I_B，但最多到「饱和」上限
    return ib, ic, vcc - ic * rc


if __name__ == "__main__":
    # ① 二极管：电源从 2 V 变到 12 V，二极管压降几乎不变
    res = []
    for vs in [2.0, 5.0, 12.0]:
        vd, i = diode_point(vs, 1e3)
        res.append((vs, vd, i))
        print(f"[数值] 电源 {vs:.0f} V、R = 1 kΩ：V_D = {vd:.3f} V，I = {i*1e3:.2f} mA")
    assert res[-1][1] - res[0][1] < 0.06, "电源变 6 倍、电流变 8 倍多，二极管压降只变约 0.05 V"
    assert abs(res[1][2] - (5 - 0.7) / 1e3) < 0.1e-3, "0.7 V 模型的估算误差小于 0.1 mA"

    # ② 三极管开关：V_in 从 0 扫到 5 V
    vin = np.linspace(0, 5, 501)
    out = np.array([bjt_switch(v) for v in vin])
    ib, ic, vce = out[:, 0], out[:, 1], out[:, 2]
    v_on = 0.7                                         # 开始导通
    v_sat = 0.7 + (5.0 - 0.2) / 1e3 / 100 * 10e3       # 刚好饱和时的 V_in
    print(f"[数值] V_in < {v_on:.1f} V 截止；{v_on:.1f}–{v_sat:.2f} V 放大；> {v_sat:.2f} V 饱和")
    fig, (a1, a2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
    a1.plot(vin, vce, **fs.LS["vout"], label="输出 $V_o$ = $V_{CE}$")
    for a in (a1, a2):
        fs.ref_v(a, v_on, f"{v_on:.1f} V" if a is a1 else None)
        fs.ref_v(a, v_sat, f"{v_sat:.2f} V" if a is a1 else None)
    a1.text(0.35, 2.5, "截止", ha="center"); a1.text((v_on + v_sat) / 2, 2.5, "放大", ha="center")
    a1.text(3.8, 2.5, "饱和", ha="center")
    fs.mark(a1, 5.0, float(vce[-1]), fmt="{:.1f}", unit=" V", dx=-30, dy=6)
    fs.axlabels(a1, "", None, "电压", "V"); a1.legend(loc="upper right")
    a2.plot(vin, ic * 1e3, **fs.LS["cur"], label="集电极电流 $I_C$")
    fs.mark(a2, 5.0, float(ic[-1] * 1e3), fmt="{:.1f}", unit=" mA", dx=-40, dy=-14)
    fs.axlabels(a2, "输入电压 $V_i$", "V", "电流", "mA"); a2.legend(loc="center right")
    assert abs(vce[-1] - 0.2) < 1e-9 and abs(ic[-1] - 4.8e-3) < 1e-9, "5 V 输入时饱和：V_CE = 0.2 V、I_C = 4.8 mA"
    assert vce[0] == 5.0, "0 V 输入时截止：V_CE = V_CC"
    fs.save(fig, "P2", "P2_p2_5_bjt_transfer.png")
    print("P2_sim OK")
