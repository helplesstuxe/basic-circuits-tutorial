"""11 仿真：电子式过载保护。
采样电阻 RS 把电机电流变成电压 → RC 滤波（延时，躲开启动电流）→ LM393 反相施密特比较器（带回差）
→ 输出经上拉电阻驱动 N 沟道 MOS 管栅极：正常时输出高、MOS 管导通；过载时输出低、切断电机。
本文件提供门限计算、滤波、比较器状态机和闭环（切断负载）仿真；
主程序画 11_p2_2_hysteresis.png：电流缓慢上升越过门限时，无回差与有回差比较器输出的对比（只看判断，不切断）。
运行：/workspace/circuits-venv/bin/python code/11_sim.py   → 11-overload-protection/img/11_p2_2_hysteresis.png
page2 的代码块是本文件的精简版（不依赖 figstyle）；code/figs/11_figs.py 会调用这里的函数。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np

VCC = 5.0          # 比较器电源（V）
RS = 0.1           # 采样电阻（Ω）：1 A → 100 mV
RA, RB = 33e3, 1e3 # 基准分压：+5 V —RA— 节点 —RB— 地
RH = 100e3         # 回差电阻：比较器输出 → 同相端
RPU = 2.2e3        # 开集电极输出上拉电阻
RF, CF = 10e3, 10e-6   # 采样滤波 RC → τ = 0.1 s
TAU = RF * CF
I_NORM = 1.0       # 电机正常电流（A）
I_STALL = 5.0      # 堵转电流（A）
TAU_START = 20e-3  # 启动电流衰减时间常数（s）


def thresholds(rh=RH, ra=RA, rb=RB):
    """返回 (跳闸门限 V_H, 恢复门限 V_L)，单位 V。rh=None 表示不接回差电阻（两门限相同）。
    同相端 = 基准（戴维南等效 V_T、R_T）与比较器输出之间的分压。"""
    v_t = VCC * rb / (ra + rb)
    r_t = ra * rb / (ra + rb)
    if rh is None:
        return v_t, v_t
    v_h = v_t + (VCC - v_t) * r_t / (r_t + rh + RPU)   # 输出高（经上拉到 5 V）时
    v_l = v_t * rh / (r_t + rh)                         # 输出低（≈0 V）时
    return v_h, v_l


def lowpass(x, dt, tau, y0=None):
    """一阶 RC 低通（欧拉法）：每一步 y += (x − y)·dt/τ。"""
    y = np.empty_like(x)
    v = x[0] if y0 is None else y0
    for k in range(len(x)):
        v += (x[k] - v) * dt / tau
        y[k] = v
    return y


def comparator(vs, v_h, v_l, on0=True):
    """反相施密特比较器状态机：返回 on（True = 输出高 = MOS 管导通）。
    导通状态下 vs > v_h 跳闸；跳闸状态下 vs < v_l 恢复。"""
    on = np.empty(len(vs), dtype=bool)
    s = on0
    for k, v in enumerate(vs):
        if s and v > v_h:
            s = False
        elif (not s) and v < v_l:
            s = True
        on[k] = s
    return on


def closed_loop(t, i_load, v_h, v_l, tau=TAU, latch=False):
    """闭环：比较器真的去切断电机。返回 (实际电流, 滤波后采样电压, on)。
    latch=True 表示跳闸后锁住，直到复位（断电）才恢复。"""
    dt = t[1] - t[0]
    i = np.empty_like(i_load); y = np.empty_like(i_load); on = np.empty(len(t), dtype=bool)
    v, s = i_load[0] * RS, True
    for k in range(len(t)):
        i[k] = i_load[k] if s else 0.0
        v += (i[k] * RS - v) * dt / tau
        if s and v > v_h:
            s = False
        elif (not s) and (not latch) and v < v_l:
            s = True
        y[k] = v; on[k] = s
    return i, y, on


def trip_time(i, i_trip, i0=I_NORM, tau=TAU):
    """电流从 i0 阶跃到 i 时的跳闸延时：t = τ·ln((i − i0)/(i − i_trip))；i ≤ i_trip 永不跳闸（返回 inf）。"""
    i = np.asarray(i, dtype=float)
    out = np.full(i.shape, np.inf)
    ok = i > i_trip
    out[ok] = tau * np.log((i[ok] - i0) / (i[ok] - i_trip))
    return out


def start_current(t, t0=0.0):
    """电机在 t0 时刻启动：电流先冲到堵转电流 5 A，再随转速升高衰减到 1 A。"""
    s = np.clip(t - t0, 0, None)
    return np.where(t >= t0, I_NORM + (I_STALL - I_NORM) * np.exp(-s / TAU_START), 0.0)


def slow_ramp(t, seed=3):
    """负载缓慢加重再减轻的电流：1 A → 2.6 A（0–6 s）→ 1 A（6–12 s），叠加机械负载的随机波动。"""
    base = np.interp(t, [0, 1, 6, 11, 12], [1.0, 1.0, 2.6, 1.0, 1.0])
    rng = np.random.default_rng(seed)
    w = rng.normal(0, 1, len(t))
    w = lowpass(w, t[1] - t[0], 0.01, 0.0)           # 约 16 Hz 以下的随机起伏
    w *= 0.15 / w.std()
    return base, base + w


def flips(on):
    return int(np.count_nonzero(np.diff(on.astype(int))))


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import figstyle as fs
    v_h, v_l = thresholds()
    print(f"[数值] 门限：跳闸 {v_h*1e3:.0f} mV（{v_h/RS:.2f} A），恢复 {v_l*1e3:.0f} mV（{v_l/RS:.2f} A），回差 {(v_h-v_l)*1e3:.0f} mV；τ = {TAU*1e3:.0f} ms")
    assert 1.85 < v_h / RS < 2.0 and 1.4 < v_l / RS < 1.5
    dt = 1e-3
    t = np.arange(0, 12, dt)
    base, i_load = slow_ramp(t)
    vs = lowpass(i_load * RS, dt, TAU)
    on_plain = comparator(vs, v_h, v_h)           # 无回差：门限同为 v_h
    on_hyst = comparator(vs, v_h, v_l)
    n_p, n_h = flips(on_plain), flips(on_hyst)
    print(f"[数值] 无回差比较器翻转 {n_p} 次；有回差比较器翻转 {n_h} 次")
    assert n_p > 6 and n_h == 2
    t_trip = t[np.argmax(~on_hyst)]
    t_back = t[len(t) - 1 - np.argmax(~on_hyst[::-1])] + dt
    print(f"[数值] 有回差：{t_trip:.2f} s 跳闸，{t_back:.2f} s 恢复")
    fig, ax = plt.subplots(3, 1, figsize=fs.SIZE["tall"], sharex=True, gridspec_kw=dict(height_ratios=[1.6, 1, 1]))
    ax[0].plot(t, i_load * RS * 1e3, **{**fs.LS["vin"], "lw": 0.6}, label="采样电压 $I \\cdot R_S$（含负载波动）")
    ax[0].plot(t, vs * 1e3, **fs.LS["vout"], label=f"RC 滤波后（τ = {TAU*1e3:.0f} ms），送比较器")
    for v, name, va in [(v_h, "跳闸", "bottom"), (v_l, "恢复", "top")]:   # 门限线，标签写在图框右侧外面，避免压住数据
        fs.ref_h(ax[0], v * 1e3)
        ax[0].text(1.01, v * 1e3, f"{name} {v*1e3:.0f} mV\n（{v/RS:.2f} A）", transform=ax[0].get_yaxis_transform(),
                   ha="left", va=va, fontsize=8, color="0.3")
    ax[0].set_ylim(50, 330); ax[0].set_ylabel(fs.qlabel("电压", "mV")); ax[0].legend(loc="upper right", fontsize=8)
    ax[1].plot(t, on_plain * 5.0, **{**fs.LS["bad"], "lw": 0.8, "marker": None}, label=f"无回差：翻转 {n_p} 次")
    ax[2].plot(t, on_hyst * 5.0, **fs.LS["good"], label=f"有回差：翻转 {n_h} 次")
    for a in ax[1:]:
        a.set_ylim(-0.8, 6.8); a.set_yticks([0, 5]); a.set_ylabel(fs.qlabel("输出", "V")); a.legend(loc="lower right", fontsize=8)
    ax[2].set_xlabel(fs.qlabel("时间", "s"))
    print(f"[参考线] {v_h*1e3:.0f} mV、{v_l*1e3:.0f} mV")
    fs.save(fig, "11", "11_p2_2_hysteresis.png")
