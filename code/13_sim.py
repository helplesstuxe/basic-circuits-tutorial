"""13 仿真：反相微分器。三角波输入 → 方波输出；输入混入一点高频干扰时，理想微分器把它放大得很厉害，
实用微分器（输入串 R1、反馈 R_f 旁并 C_f）则基本把它压住。另外用「有限带宽运放」模型演示理想微分器的振铃。
运行：/workspace/circuits-venv/bin/python code/13_sim.py   → 13-differentiator/img/13_p2_3_noise.png
lm358() 调用 ngspice 和 TI 的 LM358B 模型（spice/models/），给 page1 图 13-p1-6 和示波器读数用。
page2 的代码块是本文件的精简版（不依赖 figstyle）；code/figs/13_figs.py 会调用这里的函数。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np

C = 100e-9         # 输入电容（F）
RF = 10e3          # 反馈电阻（Ω）→ R_f·C = 1 ms
R1 = 1e3           # 实用微分器输入串联电阻（Ω）
CF = 10e-9         # 实用微分器反馈并联电容（F），R_f·C_f = R1·C = 0.1 ms
GBW = 1.2e6        # 运放增益带宽积（Hz），LM358B 数量级（见 P3）
VSAT = 13.5        # 输出上下限（V）
F_TRI = 500.0      # 三角波频率（Hz）
A_TRI = 0.5        # 三角波幅度（V）：−0.5 ↔ +0.5 V，斜率 ±1 V/ms
F_N, A_N = 20e3, 0.01   # 高频干扰：20 kHz、10 mV


def triangle(t, f=F_TRI, amp=A_TRI):
    """从 −amp 开始先上升的三角波。"""
    ph = (t * f) % 1.0
    return np.where(ph < 0.5, -amp + 4 * amp * ph, 3 * amp - 4 * amp * ph)


def noise(t, a=A_N, f=F_N):
    return a * np.sin(2 * np.pi * f * t)


def ideal(t, vin, rf=RF, c=C):
    """理想运放 + 理想微分器：V_o = −R_f·C·（输入斜率）。"""
    return np.clip(-rf * c * np.gradient(vin, t), -VSAT, VSAT)


def simulate(t, vin, r1=0.0, cf=0.0, gbw=None, rf=RF, c=C):
    """逐小段（四阶龙格-库塔）计算微分器输出。
    状态：q = 输入电容电压，p = C_f 电压（= V− − V_o），vo = 输出。
    gbw=None 表示理想运放（V− 恒为 0）；否则运放按 dV_o/dt = −2π·GBW·V− 工作。"""
    dt = t[1] - t[0]
    wt = None if gbw is None else 2 * np.pi * gbw
    q, p, vo = float(vin[0]), 0.0, 0.0     # 假设电容早已充到输入的初值（电路已稳定工作）
    out = np.empty_like(vin)

    def deriv(q, p, vo, u):
        if wt is None:                       # 理想运放：V− = 0
            vn = 0.0
            if cf > 0:
                i1 = (u - q) / r1
                return i1 / c, (i1 - p / rf) / cf, 0.0
            i1 = (u - q) / r1                # 只加 R1：V_o = −R_f·i1 直接算出
            return i1 / c, 0.0, 0.0
        if r1 == 0:                          # 理想微分器 + 有限带宽运放
            vn = u - q
            return (vn - vo) / (rf * c), 0.0, -wt * vn
        if cf > 0:
            vn = p + vo
            i1 = (u - q - vn) / r1
            return i1 / c, (i1 - p / rf) / cf, -wt * vn
        i1 = (u - q - vo) / (r1 + rf)
        vn = vo + rf * i1
        return i1 / c, 0.0, -wt * vn

    for k in range(len(t)):
        u = vin[k]
        if wt is None:
            out[k] = -p if cf > 0 else -rf * (u - q) / r1
        else:
            out[k] = vo
        k1 = deriv(q, p, vo, u)
        k2 = deriv(q + k1[0] * dt / 2, p + k1[1] * dt / 2, vo + k1[2] * dt / 2, u)
        k3 = deriv(q + k2[0] * dt / 2, p + k2[1] * dt / 2, vo + k2[2] * dt / 2, u)
        k4 = deriv(q + k3[0] * dt, p + k3[1] * dt, vo + k3[2] * dt, u)
        q += (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) * dt / 6
        p += (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) * dt / 6
        vo += (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]) * dt / 6
        vo = min(max(vo, -VSAT), VSAT)
    return np.clip(out, -VSAT, VSAT)


ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LM358_LIB = os.path.abspath(os.path.join(ROOT, "spice", "models", "LMx58B_LM2904B.lib"))  # TI 官方 LM358B 模型（只读）


def lm358(src, r1=None, cf=None, tstop=6e-3, tstep=0.5e-6, vs=15):
    """用 ngspice + TI LM358B 官方模型（SLOM472C）跑一次 ±15 V 反相微分器的瞬态仿真。
    src：输入源的 SPICE 写法，如 "PULSE(-0.5 0.5 0 1m 1m 1n 2m)"（±0.5 V、500 Hz 三角波）；
    r1 / cf 为 None 表示不加（理想微分器：只有 C 和 R_f）；vs 为正负电源电压（默认 ±15 V，page4 用 ±9 V）。返回 (t, v_out)。
    网表写在临时目录里，跑完即删，不在仓库里留文件。"""
    import shutil, subprocess, tempfile
    ng = shutil.which("ngspice") or "/usr/bin/ngspice"
    r1_txt = f"{r1:g}" if r1 else "1m"            # 1 mΩ ≈ 不加 R1
    cf_txt = f"{cf:g}" if cf else "1e-18"         # 1e-18 F ≈ 不加 C_f
    cir = f"""* 13 微分器 + LM358B
.include {LM358_LIB}
VP vp 0 {vs:g}
VN vn 0 {-vs:g}
VI in 0 {src}
R1 in a {r1_txt}
C1 a m {C:g}
RF m out {RF:g}
CF m out {cf_txt}
XU 0 m vp vn out LMX58B_LM2904B
.control
tran {tstep:g} {tstop:g} 0 {tstep:g}
wrdata out.txt v(out)
.endc
.end
"""
    tmp = tempfile.mkdtemp(prefix="d13_")
    try:
        with open(os.path.join(tmp, ".spiceinit"), "w") as f:
            f.write("set ngbehavior=psa\nset num_threads=1\n")   # 读入 PSpice 格式的厂家模型
        with open(os.path.join(tmp, "d.cir"), "w", encoding="utf-8") as f:
            f.write(cir)
        subprocess.run([ng, "-b", "d.cir"], cwd=tmp, capture_output=True, text=True, timeout=600, check=True)
        d = np.loadtxt(os.path.join(tmp, "out.txt"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return d[:, 0], d[:, 1]


def noise_pp(t, y_noisy, y_clean, t0):
    """干扰在输出端造成的峰峰值（同一电路有/无干扰两次结果相减）。"""
    k = t > t0
    d = y_noisy[k] - y_clean[k]
    return float(d.max() - d.min())


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import figstyle as fs
    t = np.arange(0, 8e-3, 1e-7)
    clean = triangle(t)
    vin = clean + noise(t)
    vo_i, vo_i0 = ideal(t, vin), ideal(t, clean)
    vo_p = simulate(t, vin, r1=R1, cf=CF)
    vo_p0 = simulate(t, clean, r1=R1, cf=CF)
    n_i = noise_pp(t, vo_i, vo_i0, 1e-3)
    n_p = noise_pp(t, vo_p, vo_p0, 1e-3)
    lvl = vo_p0[(t > 6.8e-3) & (t < 7.0e-3)].mean()
    print(f"[数值] R_f·C = {RF*C*1e3:.1f} ms，三角波 ±{A_TRI} V {F_TRI:.0f} Hz（斜率 ±{4*A_TRI*F_TRI/1e3:.0f} V/ms），干扰 {A_N*1e3:.0f} mV {F_N/1e3:.0f} kHz")
    print(f"[数值] 理想微分器：方波 ±{RF*C*4*A_TRI*F_TRI:.1f} V，干扰造成输出峰峰 {n_i:.2f} V（理论 2×10 mV×2π×20 kHz×1 ms = {2*A_N*2*np.pi*F_N*RF*C:.2f} V）")
    print(f"[数值] 实用微分器（R1 {R1/1e3:.0f} kΩ，C_f {CF*1e9:.0f} nF）：干扰造成输出峰峰 {n_p:.3f} V；上升段（6.8–7.0 ms）输出 {lvl:.2f} V")
    assert abs(n_i - 2.51) < 0.05 and n_p < 0.05 and abs(lvl + 1.0) < 0.01
    fig, axs = plt.subplots(3, 1, figsize=fs.SIZE["tall"], sharex=True)
    tm = t * 1e3
    axs[0].plot(tm, vin, **fs.LS["vin"], label="输入：±0.5 V 三角波 + 10 mV、20 kHz 干扰")
    axs[0].set_ylabel(fs.qlabel("输入", "V")); axs[0].set_ylim(-0.8, 1.0); axs[0].legend(loc="upper right", fontsize=8)
    axs[1].plot(tm, vo_i, **{**fs.LS["bad"], "lw": 0.8, "marker": None}, label=f"理想微分器：干扰被放大到峰峰 {n_i:.2f} V")
    axs[1].set_ylabel(fs.qlabel("输出", "V")); axs[1].set_ylim(-3, 4); axs[1].legend(loc="upper right", fontsize=8)
    axs[2].plot(tm, vo_p, **fs.LS["vout"], label=f"实用微分器（串 $R_1$、并 $C_f$）：干扰只剩 {n_p*1e3:.0f} mV")
    fs.ref_h(axs[2], 1.0, "+1 V", x=0.01, ha="left"); fs.ref_h(axs[2], -1.0, "−1 V", x=0.01, ha="left")
    axs[2].set_ylabel(fs.qlabel("输出", "V")); axs[2].set_ylim(-2, 2.6); axs[2].legend(loc="upper right", fontsize=8)
    axs[2].set_xlabel(fs.qlabel("时间", "ms"))
    print(f"[参考线] ±1 V；图例：{n_i:.2f} V、{n_p*1e3:.0f} mV")
    fig.tight_layout()
    fs.save(fig, "13", "13_p2_3_noise.png")
