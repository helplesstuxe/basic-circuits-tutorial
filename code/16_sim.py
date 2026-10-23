# 16 振荡器最小仿真：文氏桥正弦振荡器的起振过程，比较「增益不足」「增益过大」「有稳幅」三种情况。
import sys, os                                     # 下一行让 Python 找到 code/figs 里的共享画图样式
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

R, C = 10e3, 10e-9                                 # 文氏桥：两个 R = 10 kΩ，两个 C = 10 nF
f0 = 1 / (2 * np.pi * R * C)                       # 振荡频率 f0 = 1/(2πRC) ≈ 1.59 kHz
Rg, VMAX = 10e3, 4.0                               # 反相端接地电阻 10 kΩ；假设运放输出最大 ±4 V
dt, T = 0.2e-6, 20e-3                              # 每 0.2 µs 算一步，共算 20 ms
t = np.arange(0, T, dt)                            # 时间轴

def vo_fixed(vx, Rf):                              # 普通同相放大：Vo = (1 + Rf/Rg)·V+，超出 ±4 V 就被削平
    return np.clip((1 + Rf / Rg) * vx, -VMAX, VMAX)

def vo_diode(vx):                                  # 有稳幅：Rf = 12 kΩ + (10 kΩ 并一对反向并联二极管)
    i = vx / Rg                                    # 虚短：反相端电压 = V+，流过 Rg 和 Rf 的电流 = V+/Rg
    vb = 0.6 * np.tanh(i * 10e3 / 0.6)             # 10 kΩ 两端电压：小时按欧姆定律，大时被二极管限在约 0.6 V（近似模型）
    return np.clip(vx + i * 12e3 + vb, -VMAX, VMAX)  # 输出 = 反相端电压 + 两段反馈电阻上的压降

def run(amp):                                      # 给定放大规律，数值求解文氏桥电路
    vc, vx = 0.0, 0.01                             # 串联电容电压 0；同相端有 10 mV 的初始扰动（模拟噪声）
    out = np.empty_like(t)
    for k in range(len(t)):
        vo = amp(vx)                               # 运放输出
        i = (vo - vx - vc) / R                     # 串联支路（R 与 C 串联）里的电流
        vc += i / C * dt                           # 串联电容充电
        vx += (i - vx / R) / C * dt                # 并联支路：电流一部分走 R 到地，其余给并联 C 充电
        out[k] = vo
    return out

cases = [("增益 2.9（$R_f$ = 19 kΩ）：不起振", run(lambda v: vo_fixed(v, 19e3)), "bad"),
         ("增益 3.2（$R_f$ = 22 kΩ）：起振后削顶", run(lambda v: vo_fixed(v, 22e3)), "third"),
         ("二极管稳幅（小信号增益同为 3.2）", run(vo_diode), "vout")]
late = t > 15e-3                                   # 取最后 5 ms 看稳定后的幅度
for name, y, _ in cases:
    print(f"{name}：最后 5 ms 峰值 {np.max(np.abs(y[late])):.2f} V")
assert np.max(np.abs(cases[0][1][late])) < 0.01    # 增益不足：振荡衰减到几乎为零
assert np.max(np.abs(cases[1][1][late])) > 3.99    # 增益过大：顶到 ±4 V 被削平
assert 1.0 < np.max(np.abs(cases[2][1][late])) < 3.9  # 稳幅：幅度停在削顶以下
mid = (t > 10e-3) & (t < 15e-3)                    # 再取 10～15 ms 比较，确认幅度已经稳定
assert abs(np.max(np.abs(cases[2][1][mid])) - np.max(np.abs(cases[2][1][late]))) < 0.05
n = np.sum(np.diff(np.sign(cases[2][1][late])) > 0)   # 数最后 5 ms 里有几次向上过零
print(f"振荡频率 理论 {f0:.0f} Hz，仿真约 {n / 5e-3:.0f} Hz")
assert abs(n / 5e-3 - f0) < 0.1 * f0

fig, axs = plt.subplots(3, 1, figsize=fs.SIZE["tall"], sharex=True)  # 三行，共用时间轴
for ax, (name, y, ls) in zip(axs, cases):
    ax.plot(t * 1e3, y, **{**fs.LS[ls], "lw": 0.9})  # 输出电压波形
    ax.set_title(name, fontsize=9, loc="left")     # 每行标题说明是哪种情况
    ax.set_ylim(-5, 5); ax.set_ylabel("$V_o$ / V")
    fs.ref_h(ax, VMAX, "±4 V（输出极限）", x=0.99)   # 灰色点线：输出极限
    fs.ref_h(ax, -VMAX)
fs.axlabels(axs[2], "时间", "ms")                   # 横轴标签
fs.save(fig, "16", "16_p2_3_wien_startup.png")     # 保存到 16-oscillator/img/
