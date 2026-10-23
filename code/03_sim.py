# 03 电压跟随器最小仿真：10 V 经两个 10 kΩ 分压得到 5 V，比较「直接接负载」和「经跟随器接负载」时负载上的电压。
import sys, os                                     # 下一行让 Python 找到 code/figs 里的共享画图样式
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

V_s, Ra, Rb = 10.0, 10e3, 10e3                     # 电源 10 V，上下两个分压电阻都是 10 kΩ
V_open = V_s * Rb / (Ra + Rb)                      # 不接负载时分压点 5 V
RL = np.logspace(3, 6, 300)                        # 负载电阻从 1 kΩ 扫到 1 MΩ

def par(a, b):                                     # 两个电阻并联
    return a * b / (a + b)

V_direct = V_s * par(Rb, RL) / (Ra + par(Rb, RL))  # 直接接：负载和下臂并联，分压点被拉低
V_buffer = np.full_like(RL, V_open)                # 经跟随器：分压点只接同相端（不取电流），输出 = 5 V

fig, ax = plt.subplots(figsize=fs.SIZE["single"])  # 一张图
ax.semilogx(RL, V_buffer, **fs.LS["vout"], label="经跟随器接负载")       # 橙色：跟随器输出
ax.semilogx(RL, V_direct, **fs.LS["bad"], label="直接接负载")           # 朱红色带 ×：问题做法
for r in (1e3, 10e3, 100e3):                       # 标出三个负载值下直接接法的电压
    v = V_s * par(Rb, r) / (Ra + par(Rb, r))       # 这一点的负载电压
    print(f"负载 {r/1e3:g} kΩ：直接接 {v:.2f} V，经跟随器 {V_open:.2f} V")
    fs.mark(ax, r, v, fmt="{:.2f}", unit=" V", dx=6, dy=-12)
fs.ref_h(ax, V_open, f"{V_open:.0f} V（空载分压值）", x=0.02, ha="left")   # 灰色点线：设计值
assert abs(V_s * par(Rb, 1e3) / (Ra + par(Rb, 1e3)) - 0.83) < 0.01        # 1 kΩ 负载直接接只剩 0.83 V
assert np.all(V_buffer == 5.0)                     # 跟随器后负载电压不变
fs.axlabels(ax, "负载电阻 $R_L$", "Ω", "负载上的电压", "V")              # 轴标签
ax.set_ylim(0, 6); ax.legend(loc="lower right", fontsize=8)               # 纵轴范围和图例
fs.save(fig, "03", "03_p2_2_buffer_vs_direct.png")  # 保存到 03-voltage-follower/img/
