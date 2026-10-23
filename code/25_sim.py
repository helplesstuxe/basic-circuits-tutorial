"""25 仿真：H 桥驱动直流电机——正转/反转/刹车/滑行的电流与转速、PWM 占空比与平均电压、死区与直通电流。
运行：/workspace/circuits-venv/bin/python code/25_sim.py   → 25-h-bridge/img/25_p2_2_pwm.png
code/figs/25_figs.py 会调用这里的函数画其余的图。
电机参数是示意值（12 V 小型有刷直流电机的量级）；桥臂导通电阻取 TI DRV8871 数据手册典型值
（高边 307 mΩ + 低边 258 mΩ），死区仿真的分立 MOS 管导通电阻取 IRLZ44N 的 25 mΩ。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np

# ---- 电机与电源（示意值）----
VM = 12.0        # 电源电压（V）
R_M = 2.0        # 电枢电阻（Ω）
L_M = 1e-3       # 电枢电感（H）
KE = 0.02        # 反电动势常数 = 转矩常数（V·s/rad = N·m/A）
J = 1e-5         # 转子转动惯量（kg·m²）
B = 1e-5         # 摩擦系数（N·m·s/rad）
R_HS, R_LS = 0.307, 0.258   # DRV8871 高边、低边导通电阻典型值（Ω）
V_D = 0.8        # 体二极管压降（V，示意）

# 桥的四种状态：F 正转、R 反转、B 刹车（两个低边同时导通）、C 滑行（四管全关）
def step(i, w, state, dt):
    """前进一个时间步，返回新的电流 i（A）、角速度 w（rad/s）和电机两端电压 v（V）。"""
    e = KE * w                                    # 反电动势
    if state == "F":
        v, r = VM, R_M + R_HS + R_LS
    elif state == "R":
        v, r = -VM, R_M + R_HS + R_LS
    elif state == "B":
        v, r = 0.0, R_M + 2 * R_LS
    else:                                         # 滑行：电流只能经体二极管回灌电源（快衰减）
        if abs(i) < 1e-4:
            i = 0.0
            return i, w + dt * (-B * w) / J, e
        v, r = -np.sign(i) * (VM + 2 * V_D), R_M
    i_new = i + dt * (v - e - r * i) / L_M
    if state == "C" and np.sign(i_new) != np.sign(i):
        i_new = 0.0                               # 二极管不让电流反向
    w_new = w + dt * (KE * i - B * w) / J
    return i_new, w_new, v


def run(schedule, t_end, dt=2e-6, i0=0.0, w0=0.0):
    """schedule(t) 返回该时刻的状态字母；返回 t、i、w、v 数组。"""
    n = int(round(t_end / dt))
    t = np.arange(n) * dt
    I, W, V = np.empty(n), np.empty(n), np.empty(n)
    i, w = i0, w0
    for k in range(n):
        i, w, v = step(i, w, schedule(t[k]), dt)
        I[k], W[k], V[k] = i, w, v
    return t, I, W, V


def pwm_schedule(duty, f, on="F", off="B"):
    """PWM：每个周期前 duty 部分为 on 状态，其余为 off 状态（默认「驱动—刹车」交替）。"""
    T = 1.0 / f
    return lambda t: on if ((t / T + 1e-6) % 1.0) < duty else off   # 加 1e-6 防止浮点误差丢掉周期起点


def avg_speed(duty):
    """平均模型：平均电压 = 占空比 × VM 时的稳态转速（rad/s）与电流（A）。"""
    r = R_M + duty * (R_HS + R_LS) + (1 - duty) * 2 * R_LS   # 驱动/刹车交替时的平均电阻
    w = KE * duty * VM / (r * B + KE ** 2)
    return w, B * w / KE


def ripple_pp(duty, f):
    """小纹波近似：电流峰峰纹波 ≈ VM·D·(1−D)/(L·f)。"""
    return VM * duty * (1 - duty) / (L_M * f)


# ---- 死区与直通：同一桥臂高边关断、低边开通的交接过程 ----
R_ON_D = 0.025   # 分立 MOS 管导通电阻（Ω，IRLZ44N 5 V 驱动）
T_SW = 200e-9    # 每只管子从全通到全断（或反之）的过渡时间（s，示意值）
L_S = 20e-9      # 桥臂走线的杂散电感（H，示意值）
R_S = 0.01       # 走线与电源内阻（Ω，示意值）

def shoot_through(t_dead, t_end=800e-9, dt=0.1e-9):
    """高边在 t=0 开始关断，低边在 t=t_dead 开始开通；返回 t、直通电流、峰值（A）和一次交接的能量（J）。"""
    t = np.arange(0, t_end, dt)
    gH = 1 - np.clip(t / T_SW, 0, 1)                    # 高边导通程度 1→0
    gL = np.clip((t - t_dead) / T_SW, 0, 1)             # 低边导通程度 0→1
    i = np.zeros_like(t)
    for k in range(1, len(t)):
        if gH[k] <= 0 or gL[k] <= 0:
            r = 1e6
        else:
            r = R_ON_D / gH[k] + R_ON_D / gL[k] + R_S
        di = (VM - r * i[k - 1]) / L_S * dt
        i[k] = max(i[k - 1] + di, 0.0) if r < 1e5 else max(i[k - 1] - i[k - 1] * dt / 2e-9, 0.0)
    return t, i, i.max(), np.trapezoid(VM * i, t)


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs

    f = 20e3
    fig, axes = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=False)
    ax = axes[0]
    styles = [("ref", 0.25), ("vin", 0.50), ("vout", 0.75)]
    for key, d in styles:
        t, I, W, V = run(pwm_schedule(d, f), 0.4, dt=0.5e-6)   # 每个 PWM 周期正好 100 步
        ax.plot(t * 1e3, W * 60 / (2 * np.pi), **{**fs.LS[key], "lw": 1.3}, label=f"占空比 {d:.0%}：稳定在 {W[-20000:].mean()*60/2/np.pi:.0f} rpm")
        w_avg, _ = avg_speed(d)
        print(f"占空比 {d:.0%}：仿真末段转速 {W[-20000:].mean()*60/2/np.pi:.0f} rpm，平均模型 {w_avg*60/2/np.pi:.0f} rpm，"
              f"平均电流 {I[-20000:].mean():.3f} A，纹波 {np.ptp(I[-20000:]):.3f} A（近似式 {ripple_pp(d, f):.3f} A）")
        if d == 0.5:
            t50, I50, V50 = t, I, V
    fs.axlabels(ax, "时间", "ms", "转速", "rpm")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("(a) 20 kHz PWM、不同占空比下电机的起动与稳定转速", fontsize=9)
    ax = axes[1]
    m = (t50 >= 0.35) & (t50 < 0.35 + 3 / f)
    ax.plot((t50[m] - 0.35) * 1e6, V50[m], **fs.LS["vin"], label="电机两端电压（左轴）")
    ax2 = ax.twinx()
    ax2.plot((t50[m] - 0.35) * 1e6, I50[m], **fs.LS["vout"], label="电机电流（右轴）")
    fs.axlabels(ax, "时间", "µs", "电压", "V")
    ax2.set_ylabel(fs.qlabel("电流", "A"))
    ax.set_ylim(-1, 18)
    ax.axhline(6.0, **fs.LS["ref"], label="平均电压 6 V（= 50% × 12 V）")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper center", ncol=3, fontsize=7.5)
    ax2.set_ylim(0.0, 0.3)
    ax.set_title("(b) 占空比 50%：稳定后三个 PWM 周期的放大", fontsize=9)
    fig.tight_layout()
    fs.save(fig, 25, "25_p2_2_pwm.png")
