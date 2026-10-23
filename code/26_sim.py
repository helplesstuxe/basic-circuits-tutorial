"""26 仿真：上拉/下拉电阻与电平转换——悬空输入、按键抖动与 RC + 施密特去抖、上拉电阻与上升时间、
N 沟道 MOS 管双向电平转换。
运行：/workspace/circuits-venv/bin/python code/26_sim.py   → 26-pullup-level-shift/img/26_p2_2_debounce.png
同时打印电平转换模型的关键数字；code/figs/26_figs.py 会调用这里的函数（包括 level_shifter）画其余的图。
数据来源：
- 施密特门限：TI SN74HC14 数据手册，VCC = 4.5 V 一行典型值 VT+ 2.5 V、VT− 1.6 V（5 V 系统近似使用）。
- 单片机输入门限：Microchip ATmega328P 数据手册 VIL ≤ 0.3·VCC、VIH ≥ 0.6·VCC，内部上拉 20–50 kΩ。
- 按键抖动时长：Ganssle《A Guide to Debouncing》第 1 部分，平均约 1.5 ms、多数不超过 6.2 ms。
  本脚本的抖动波形是按这个量级随机生成的示意波形，不是实测数据。
- 电平转换 MOS 管：onsemi BSS138，VGS(th) 典型 1.3 V，VGS = 4.5 V 时 RDS(on) 典型 1.0 Ω。
- I²C 上升时间：TI SLVA689A，tr = 0.8473·Rp·Cb。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np

VCC = 5.0
VT_P, VT_M = 2.5, 1.6            # SN74HC14 正向 / 负向门限典型值（V）
V_MID = 2.5                      # 没有回差的输入：近似为一个 VCC/2 的单门限
VIL, VIH = 0.3 * VCC, 0.6 * VCC  # ATmega328P 保证读成 0 / 1 的电压

# ---------------- 按键抖动（示意波形） ----------------
def bounce_state(t, t_press, t_release, bounce_press=2e-3, bounce_release=1e-3, seed=1):
    """返回布尔数组：True = 触点接通。按下、松开后各有一段随机抖动：
    在抖动时间里，触点在「接通」「断开」之间来回跳，每一段持续 20 µs 到抖动时间的 1/5。"""
    rng = np.random.default_rng(seed)
    closed = (t >= t_press) & (t < t_release)
    for t0, dur, final in [(t_press, bounce_press, True), (t_release, bounce_release, False)]:
        tt, state = t0, final
        while tt < t0 + dur:
            seg = rng.uniform(20e-6, dur / 5)
            m = (t >= tt) & (t < min(tt + seg, t0 + dur))
            closed[m] = state
            tt += seg
            state = not state
    return closed


def count_edges(b):
    """数一个 0/1 序列翻转了几次。"""
    b = np.asarray(b, dtype=int)
    return int(np.count_nonzero(np.diff(b)))


# ---------------- RC 去抖（图 26-p2-1 的电路） ----------------
def rc_debounce(closed, dt, r1, r2, c, v0=VCC):
    """VCC—R1—A—R2—电容；按键接在 A 与地之间。按下：电容经 R2 放电；松开：经 R1+R2 充电。
    每一步用指数的精确解，不怕步长大。返回电容电压。"""
    vc = np.empty(len(closed))
    v = v0
    k_dis = np.exp(-dt / (r2 * c))
    k_chg = np.exp(-dt / ((r1 + r2) * c))
    for i, s in enumerate(closed):
        if s:
            v = v * k_dis                     # 向 0 V 放电
        else:
            v = VCC + (v - VCC) * k_chg       # 向 VCC 充电
        vc[i] = v
    return vc


def schmitt(v, vtp=VT_P, vtm=VT_M, init_high=True):
    """施密特输入：高于 VT+ 才认作 1，低于 VT− 才认作 0，中间保持。返回输入被认成的逻辑值。"""
    out = np.empty(len(v), dtype=bool)
    s = init_high
    for i, x in enumerate(v):
        if s and x < vtm:
            s = False
        elif (not s) and x > vtp:
            s = True
        out[i] = s
    return out


def plain_input(v, vth=V_MID):
    """没有回差的输入：只有一个门限。"""
    return np.asarray(v) > vth


# ---------------- 上拉电阻与上升时间 ----------------
def rise_time(rp, cb):
    """SLVA689A 式 (5)：从 0.3·VCC 升到 0.7·VCC 的时间。"""
    return np.log(0.7 / 0.3) * rp * cb       # ln(0.7/0.3) = 0.8473


def rp_min(vcc, vol=0.4, iol=3e-3):
    """SLVA689A 式 (1)：上拉太小，输出管拉不到 VOL 以下。"""
    return (vcc - vol) / iol


def rp_max(tr, cb):
    """SLVA689A 式 (6)：上拉太大，上升沿超过规范。"""
    return tr / (np.log(0.7 / 0.3) * cb)


# ---------------- N 沟道 MOS 管双向电平转换（AN10441 电路） ----------------
VTH, KP = 1.3, 1.0 / (1.0 * (4.5 - 1.3))   # BSS138：门限 1.3 V；由 RDS(on) = 1 Ω @ VGS 4.5 V 反推（A/V²）
VDIODE, RDIODE = 0.6, 50.0                  # 体二极管：0.6 V 以上导通，串 50 Ω（示意）


def mos_current(vg, vd, vs):
    """沟道电流（从漏极流向源极为正）。两端谁低谁当源极（MOS 管沟道是对称的）。"""
    lo = min(vd, vs)
    vov = vg - lo - VTH
    if vov <= 0:
        return 0.0
    vds = vd - vs
    a = min(abs(vds), vov)
    return np.sign(vds) * KP * (vov * a - a * a / 2)


def diode_current(vs, vd):
    """体二极管：衬底接源极，正极在源极、负极在漏极。返回从源极流向漏极的电流。"""
    x = vs - vd - VDIODE
    return x / RDIODE if x > 0 else 0.0


def level_shifter(t, pull_lo, pull_hi, v_lo=3.3, v_hi=5.0, rp=10e3, c=50e-12, r_drv=100.0, swapped=False):
    """pull_lo / pull_hi：布尔数组，True 表示低压侧 / 高压侧有器件把线拉低（开漏输出，导通电阻 r_drv）。
    swapped=False：AN10441 的正确接法，源极接低压侧、漏极接高压侧、栅极接低压电源。
    swapped=True：源极和漏极接反（源极到了 5 V 侧）。
    用隐式欧拉法 + 牛顿迭代求两条线的电压（MOS 管导通时方程很「硬」，显式法会发散）。"""
    dt = t[1] - t[0]
    vl, vh = v_lo, v_hi
    VL, VH = np.empty(len(t)), np.empty(len(t))

    def f(x, k):
        a, b = x                                       # a：低压侧线电压，b：高压侧线电压
        vd, vs = (b, a) if not swapped else (a, b)
        i_ds = mos_current(v_lo, vd, vs) - diode_current(vs, vd)   # 漏极→源极的总电流
        i_into_a = i_ds if not swapped else -i_ds      # 流入低压侧节点的电流
        lo_on = k >= 0 and pull_lo[k]
        hi_on = k >= 0 and pull_hi[k]
        ia = (v_lo - a) / rp - (a / r_drv if lo_on else 0.0) + i_into_a
        ib = (v_hi - b) / rp - (b / r_drv if hi_on else 0.0) - i_into_a
        return np.array([ia / c, ib / c])

    x = np.array([vl, vh])
    n_pre = 2000                                       # 先空跑 2000 步，让两条线停在空闲时的稳态
    for k in list(range(-n_pre, 0)) + list(range(len(t))):
        y = x.copy()
        for _ in range(8):                             # 牛顿迭代解 y = x + dt·f(y)
            g = y - x - dt * f(y, k)
            jac = np.eye(2)
            for j in range(2):
                e = np.zeros(2); e[j] = 1e-6
                jac[:, j] = e / 1e-6 - dt * (f(y + e, k) - f(y, k)) / 1e-6
            step = np.linalg.solve(jac, g)
            y = y - step
            if np.max(np.abs(step)) < 1e-7:
                break
        x = y
        if k >= 0:
            VL[k], VH[k] = x
    return VL, VH


# ---------------- 主程序：图 26-p2-2 去抖仿真 ----------------
R1, R2, C1 = 10e3, 10e3, 1e-6        # 本节的去抖电路取值

def debounce_demo():
    dt = 2e-6
    t = np.arange(0, 60e-3, dt)
    closed = bounce_state(t, 5e-3, 35e-3, 2e-3, 1e-3, seed=3)
    raw = np.where(closed, 0.0, VCC)              # 只接上拉电阻：按下为 0 V，松开为 5 V
    vc = rc_debounce(closed, dt, R1, R2, C1)
    logic = schmitt(vc)
    return t, closed, raw, vc, logic


if __name__ == "__main__":
    import figstyle as fs
    import matplotlib.pyplot as plt

    t, closed, raw, vc, logic = debounce_demo()
    n_raw = count_edges(raw > V_MID)
    n_out = count_edges(logic)
    i_fall = np.argmax(~logic)                    # 施密特输入第一次认成 0 的时刻
    i_rise = i_fall + np.argmax(logic[i_fall:])
    d_press = t[i_fall] - 5e-3
    d_release = t[i_rise] - 35e-3
    print(f"只有上拉：引脚翻转 {n_raw} 次；RC + 施密特：翻转 {n_out} 次")
    print(f"按下后 {d_press*1e3:.1f} ms 认成按下（估算 R2·C·ln(5/1.6) = {R2*C1*np.log(5/1.6)*1e3:.1f} ms）")
    print(f"松开后 {d_release*1e3:.1f} ms 认成松开（估算 (R1+R2)·C·ln(5/2.5) = {(R1+R2)*C1*np.log(2)*1e3:.1f} ms）")
    assert n_out == 2 and n_raw > 6

    # 电平转换：和图 26-p2-3 同样的激励（图由 code/figs/26_figs.py 调用 level_shifter 画出）
    dt_ls = 2e-9
    t_ls = np.arange(0, 40e-6, dt_ls)
    pl = (t_ls > 5e-6) & (t_ls < 15e-6)          # 3.3 V 侧在 5～15 μs 拉低
    ph = (t_ls > 22e-6) & (t_ls < 32e-6)         # 5 V 侧在 22～32 μs 拉低
    VL, VH = level_shifter(t_ls, pl, ph)
    VLs, VHs = level_shifter(t_ls, pl, ph, swapped=True)
    kk = lambda tt: int(round(tt / dt_ls))
    i0 = kk(15e-6)
    ii = i0 + np.argmax(VH[i0:] - VL[i0:] > 0.05)  # 松手后两边开始分开的时刻
    print(f"电平转换：3.3 V 侧拉低时两边 {VL[kk(10e-6)]:.2f} / {VH[kk(10e-6)]:.2f} V；5 V 侧拉低时 {VL[kk(27e-6)]:.2f} / {VH[kk(27e-6)]:.2f} V")
    print(f"电平转换：松手后 {(t_ls[ii]-15e-6)*1e9:.0f} ns 两边在 {VL[ii]:.2f} V 处分开")
    print(f"电平转换：源漏接反时，空闲的 3.3 V 侧被抬到 {VLs[kk(3e-6)]:.2f} V")
    assert VL[kk(10e-6)] < 0.15 and VH[kk(10e-6)] < 0.15 and VLs[kk(3e-6)] > 3.5

    fig, axs = plt.subplots(3, 1, figsize=(7, 5.4), sharex=True)
    ms = t * 1e3
    axs[0].plot(ms, raw, **fs.LS["bad"], label=f"只有上拉电阻的引脚电压：翻转 {n_raw} 次")
    fs.ref_h(axs[0], V_MID, "单门限 2.5 V", x=0.99)
    axs[0].set_ylim(-0.5, 6.2)
    axs[0].legend(loc="center right", fontsize=9)
    axs[1].plot(ms, vc, **fs.LS["vout"], label="电容电压（R1 = R2 = 10 kΩ，C = 1 μF）")
    fs.ref_h(axs[1], VT_P, "VT+ 2.5 V", x=0.2)
    fs.ref_h(axs[1], VT_M, "VT− 1.6 V", x=0.2)
    axs[1].set_ylim(-0.3, 5.6)
    axs[1].legend(loc="lower right", fontsize=9)
    axs[2].plot(ms, logic.astype(float), **fs.LS["vin"], label=f"施密特输入认出的电平：翻转 {n_out} 次")
    axs[2].set_ylim(-0.2, 1.35)
    axs[2].set_yticks([0, 1])
    axs[2].legend(loc="center right", fontsize=9)
    fs.axlabels(axs[0], "", None, "电压", "V")
    fs.axlabels(axs[1], "", None, "电压", "V")
    fs.axlabels(axs[2], "时间", "ms", "逻辑电平")
    axs[0].set_title("按键在 5 ms 按下、35 ms 松开（抖动为示意波形）", fontsize=10)
    fs.save(fig, "26", "26_p2_2_debounce.png")
