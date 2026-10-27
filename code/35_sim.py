"""35 程控增益与 AGC：数字 AGC（自动换挡）与模拟 AGC（峰值检测 + 积分器 + 线性 dB 放大器）的 Python 模拟。
运行（仓库根目录）：/workspace/circuits-venv/bin/python code/35_sim.py
page2、page3 的数字都由本文件打印；code/figs/35_figs.py 也调用这里的函数画图。"""
import numpy as np

RF = 100e3
RG = [100e3, 24e3, 11e3, 5.1e3, 2e3, 1e3]          # X0…X5
RON = 470.0                                          # CD4051B 手册：VDD = 5 V 时典型 470 Ω
G_NOM = [1 + RF / r for r in RG]
G_REAL = [1 + RF / (r + RON) for r in RG]
VREF, NBIT = 5.0, 10                                 # Arduino Uno：10 位 ADC，参考 = 5 V
FS = 3.0                                             # 取的「满量程」：LM358 在 5 V 下最多约 3.8 V，留余量
DOWN, UP = 0.90, 0.30                                # 超过 90 % 降档、低于 30 % 升档
VCLIP = 3.83                                         # SPICE：LM358 5 V 供电输出上限


def adc(v):
    """理想 10 位 ADC：0…VREF → 0…1023（截断），返回读数。"""
    return int(np.clip(np.floor(v / VREF * 2 ** NBIT), 0, 2 ** NBIT - 1))


def digital_agc(vin, gains=G_REAL, down=DOWN, up=UP, k0=0):
    """vin：每个循环的输入电压序列。每循环：按当前档放大 → ADC → 判断 → 最多换一档。
    返回 (档位, 输出电压, 换算回来的输入) 三个数组。"""
    k = k0
    ks, vo, est = [], [], []
    for v in vin:
        out = min(gains[k] * v, VCLIP)
        n = adc(out)
        vout = n * VREF / 2 ** NBIT
        ks.append(k); vo.append(out); est.append(vout / gains[k])
        if vout > down * FS and k > 0:
            k -= 1
        elif vout < up * FS and k < len(gains) - 1:
            k += 1
    return np.array(ks), np.array(vo), np.array(est)


def demo_profile(dt=0.02):
    """10 s 的输入「幅度」：0–6 s 从 5 mV 按对数升到 1.2 V，7 s 处突然掉到 20 mV。"""
    t = np.arange(0, 10, dt)
    v = np.where(t < 6, 5e-3 * (1.2 / 5e-3) ** (t / 6), 1.2)
    v = np.where(t >= 7, 0.02, v)
    return t, v


TAUS = (1e-3, 5e-3, 50e-3)                           # 模拟 AGC 积分时间常数：快 / 中 / 慢


def analog_agc(tau_i, tau_d=20e-3, f=1e3, target=1.0, T=0.5, dt=5e-6, slope=50.0, g0_db=40.0):
    """模拟 AGC：y = G·x，G(dB) = g0_db − slope·vc（像 AD8331 反斜率模式）。
    检波：精密峰值检波，放电时间常数 tau_d；积分器：dvc/dt = (检波值 − 目标)/tau_i。
    输入：1 kHz 正弦，0–0.1 s 峰值 50 mV，0.1–0.3 s 峰值 0.5 V，0.3 s 后回到 50 mV。"""
    n = int(T / dt)
    t = np.arange(n) * dt
    A = np.where((t >= 0.1) & (t < 0.3), 0.5, 0.05)
    x = A * np.sin(2 * np.pi * f * t)
    vc, det = 0.0, 0.0
    y = np.empty(n); gdb = np.empty(n); dd = np.empty(n)
    kdec = np.exp(-dt / tau_d)
    for i in range(n):
        gdb[i] = g0_db - slope * vc
        y[i] = 10 ** (gdb[i] / 20) * x[i]
        det = max(det * kdec, abs(y[i]))
        dd[i] = det
        vc = float(np.clip(vc + dt * (det - target) / tau_i, 0.0, 1.0))
    return t, x, y, gdb, dd


def agc_metrics(t, y, gdb, f=1e3):
    """把输出按周期取峰值；返回（0.1 s 阶跃后回到目标 ±1 dB 所需时间，0.25–0.3 s 稳态增益起伏 dB 峰峰值，0.1 s 后第一个周期的峰值）。"""
    per = int(round(1 / f / (t[1] - t[0])))
    m = len(y) // per
    pk = np.abs(y[: m * per]).reshape(m, per).max(axis=1)
    tc = t[: m * per : per]
    after = (tc >= 0.1) & (tc < 0.3)
    ok = np.abs(20 * np.log10(pk[after] / 1.0)) < 1.0
    idx = np.where(~ok)[0]
    t_settle = (idx[-1] + 1) * (1 / f) if len(idx) else 0.0
    w = (t >= 0.25) & (t < 0.3)
    ripple = gdb[w].max() - gdb[w].min()
    first = pk[np.argmax(tc >= 0.1)]
    return t_settle, ripple, first


if __name__ == "__main__":
    print("档位  R_g      名义 G   串 470 Ω 实际 G   误差%   dB")
    for k, r in enumerate(RG):
        print(f"X{k}  {r/1e3:6.1f}k  {G_NOM[k]:7.3f}  {G_REAL[k]:8.3f}  {100*(G_REAL[k]/G_NOM[k]-1):7.2f}  {20*np.log10(G_REAL[k]):6.2f}")
    ratios = [G_REAL[i + 1] / G_REAL[i] for i in range(5)]
    print("相邻档实际倍数比：", [round(x, 3) for x in ratios], "最大", round(max(ratios), 3),
          "→ 升档后最高到", round(max(ratios) * UP * 100, 1), "% 满量程（< 90 %，不来回跳）")
    lsb = VREF / 2 ** NBIT
    print(f"ADC 1 LSB = {lsb*1e3:.3f} mV；满量程 {FS} V = {adc(FS)} 个字；30 % 处 = {adc(UP*FS)} 个字")
    print(f"固定 G≈2 时 30 mV 输入 → {G_REAL[0]*0.03*1e3:.1f} mV → {adc(G_REAL[0]*0.03)} 个字（分辨率 {100/adc(G_REAL[0]*0.03):.1f} %）")
    print(f"自动换挡 30 mV → X5 档 {G_REAL[5]*0.03:.3f} V → {adc(G_REAL[5]*0.03)} 个字（分辨率 {100/adc(G_REAL[5]*0.03):.2f} %）")
    t, v = demo_profile()
    ks, vo, est = digital_agc(v)
    err = np.abs(est / v - 1) * 100
    sat = vo >= VCLIP - 1e-9
    i7 = np.argmax(t >= 7)
    rec = np.argmax(ks[i7:] == 5)
    print(f"数字 AGC 演示：共 {len(t)} 个循环，换档 {int(np.sum(np.diff(ks) != 0))} 次，削顶循环 {int(sat.sum())} 个；"
          f"7 s 突降后 {rec} 个循环（{rec*0.02*1e3:.0f} ms）回到 X5")
    stay = np.append(ks[1:] == ks[:-1], True)          # 这一循环判定「不换档」，读数才算数
    good = (v >= UP * FS / G_REAL[5]) & ~sat & stay
    print(f"输入在量程内（≥ {UP*FS/G_REAL[5]*1e3:.1f} mV）、且本循环不换档的读数里，换算误差最大 {err[good].max():.2f} %"
          f"（只剩量化误差，增益表已校准；理论上限 1/{adc(UP*FS)} = {100/adc(UP*FS):.2f} %）")
    print(f"换档那一循环的读数误差最大 {err[~stay].max():.1f} %（所以换档后的读数要丢掉）")
    low = v < UP * FS / G_REAL[5]
    print(f"输入低于 {UP*FS/G_REAL[5]*1e3:.1f} mV 时（最高档也到不了 30 %），换算误差最大 {err[low].max():.2f} %")
    # 回差不够：升档门槛 45 %
    vin = np.full(12, 0.6)
    k1, _, _ = digital_agc(vin, up=0.45)
    k2, _, _ = digital_agc(vin)
    print("0.6 V 恒定输入，升档门槛 45 % 时档位：", k1.tolist())
    print("0.6 V 恒定输入，升档门槛 30 % 时档位：", k2.tolist())
    print(f"临界升档门槛 = 90 % / 最大档比 = {DOWN/max(ratios)*100:.1f} %")
    for ti in TAUS:
        tt, x, y, g, d = analog_agc(ti)
        ts, rp, first = agc_metrics(tt, y, g)
        print(f"模拟 AGC τ_i = {ti*1e3:g} ms：阶跃后第一个周期峰值 {first:.2f} V，回到 ±1 dB 用 {ts*1e3:.0f} ms，稳态增益起伏 {rp:.2f} dB 峰峰值")
