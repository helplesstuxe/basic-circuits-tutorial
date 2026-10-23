# 01 反相放大最小仿真：V_o = −(R_f/R_1)·V_i，再加上「输出不能超出电源」这条限制，看正常放大和削顶。
import sys, os                                     # 下一行让 Python 找到 code/figs 里的共享画图样式
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

R1, Rf = 10e3, 100e3                               # 输入电阻 R1 = 10 kΩ，反馈电阻 Rf = 100 kΩ
A_v = -Rf / R1                                     # 放大倍数 A_v = −Rf/R1 = −10（负号表示反相）
V_CC, V_EE = 15.0, -15.0                           # 正负电源 ±15 V
V_HI, V_LO = V_CC - 1.5, V_EE + 0.1                # 输出能到的最高 / 最低电压（LM358B 典型值，见 P3 page3）
t = np.linspace(0, 2e-3, 2001)                     # 时间：0 到 2 ms，取 2001 个点

fig, axes = plt.subplots(1, 2, figsize=fs.SIZE["pair"], sharey=True)  # 左右两张小图，共用纵轴
for ax, amp in zip(axes, (0.5, 1.5)):              # 左图输入峰值 0.5 V，右图 1.5 V
    V_i = fs.sine(t, 1e3, amp=amp)                 # 1 kHz 正弦输入
    V_o = np.clip(A_v * V_i, V_LO, V_HI)           # 理想输出乘 −10，再被限制在输出范围内
    print(f"输入峰值 {amp} V：理想输出峰值 {abs(A_v)*amp:.1f} V，"   # 打印图上的数字
          f"实际最高 {V_o.max():.2f} V、最低 {V_o.min():.2f} V")
    ax.plot(t * 1e3, V_i, **fs.LS["vin"], label="$V_i$ 输入")            # 蓝色：输入
    ax.plot(t * 1e3, V_o, **fs.LS["vout"], label="$V_o$ 输出")           # 橙色：输出
    if amp > 1:                                                           # 右图再画理想输出作对照
        ax.plot(t * 1e3, A_v * V_i, **fs.LS["good"], label="理想 $V_o$")  # 黑色虚线：不受电源限制时
        ax.legend(loc="lower left", fontsize=8)                           # 右图图例
    fs.ref_h(ax, V_HI, f"{V_HI} V"); fs.ref_h(ax, V_LO, f"{V_LO} V")      # 灰色点线：输出上下限
    k = np.argmax(V_o)                                                    # 输出最高点
    fs.mark(ax, t[k] * 1e3, V_o[k], fmt="{:.1f}", unit=" V", dx=8, dy=-12)  # 标出最高点数值
    ax.set_title(f"输入峰值 {amp} V", fontsize=10)                          # 小图标题
    fs.axlabels(ax, "时间", "ms", "电压", "V")                              # 轴标签：量（单位）
axes[0].legend(loc="lower left", fontsize=8)                              # 左图图例
V_o_small = A_v * fs.sine(t, 1e3, amp=0.5)                               # 小输入时的理想输出
assert abs(V_o_small.max() - 5.0) < 1e-3 and V_o_small.max() < V_HI   # 0.5 V × 10 = 5 V，没有削顶
assert np.clip(A_v * fs.sine(t, 1e3, amp=1.5), V_LO, V_HI).max() == V_HI  # 1.5 V × 10 = 15 V，被削在 13.5 V
fs.save(fig, "01", "01_p2_2_sine_clip.png")       # 保存到 01-inverting-amp/img/
