import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
# 20 有源滤波最小仿真：截止频率都约 1 kHz 的一阶有源低通和二阶 Sallen-Key 低通，比较幅频特性（输出幅度 / 输入幅度）。
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

f = np.logspace(1, 5, 800)                         # 频率从 10 Hz 扫到 100 kHz
w = 2 * np.pi * f                                  # 角频率 ω = 2πf（公式里要用）

R, C = 16e3, 10e-9                                 # 一阶：R = 16 kΩ，C = 10 nF
fc1 = 1 / (2 * np.pi * R * C)                      # 截止频率 fc = 1/(2πRC) ≈ 995 Hz
H1 = 1 / np.sqrt(1 + (f / fc1) ** 2)               # 一阶低通的幅值（运放接成跟随器，倍数 1）

R1, R2 = 4.22e3, 18.4e3                            # 二阶 Sallen-Key（TI SLOA049 表 10-1 巴特沃斯，fc = 1 kHz）
C1, C2 = 10e-9, 33e-9                              # C1 接地，C2 接到输出（反馈电容）
a = 1 - w ** 2 * R1 * R2 * C1 * C2                 # 幅值公式分母里的第一项
b = w * C1 * (R1 + R2)                             # 幅值公式分母里的第二项
H2 = 1 / np.sqrt(a ** 2 + b ** 2)                  # 二阶 Sallen-Key 低通的幅值（倍数 1）

dB = lambda h: 20 * np.log10(h)                    # 幅值换成分贝：每 20 dB 等于 10 倍
for fx in (1e3, 10e3):                             # 打印 1 kHz 和 10 kHz 处的衰减
    h1 = 1 / np.sqrt(1 + (fx / fc1) ** 2)
    wx = 2 * np.pi * fx
    h2 = 1 / np.sqrt((1 - wx ** 2 * R1 * R2 * C1 * C2) ** 2 + (wx * C1 * (R1 + R2)) ** 2)
    print(f"{fx/1e3:g} kHz：一阶 {h1:.3f} 倍（{dB(h1):.0f} dB），二阶 {h2:.3f} 倍（{dB(h2):.0f} dB）")
print(f"一阶截止频率 {fc1:.0f} Hz")
assert abs(fc1 - 995) < 1                          # 1/(2π × 16 kΩ × 10 nF) ≈ 995 Hz
assert abs(dB(1 / np.sqrt((1 - (2e4*np.pi) ** 2 * R1*R2*C1*C2) ** 2 + (2e4*np.pi*C1*(R1+R2)) ** 2)) + 40) < 1  # 10 kHz 处二阶约 −40 dB

fig, ax = plt.subplots(figsize=fs.SIZE["single"])  # 一张图
ax.semilogx(f, dB(H1), **fs.LS["third"], label="一阶有源低通")             # 红紫色点划线
ax.semilogx(f, dB(H2), **fs.LS["vout"], label="二阶 Sallen-Key 低通")      # 橙色
fs.ref_h(ax, -3, "−3 dB（0.707 倍）", x=0.62, ha="left")                 # 灰色点线：截止频率处的幅值
fs.ref_v(ax, 1e3, "1 kHz")                         # 灰色点线：截止频率
for fx in (10e3,):                                 # 标出 10 kHz 处两条曲线的数值
    fs.mark(ax, fx, dB(1 / np.sqrt(1 + (fx / fc1) ** 2)), fmt="{:.0f}", unit=" dB", dx=6, dy=4)
    wx = 2 * np.pi * fx
    fs.mark(ax, fx, dB(1 / np.sqrt((1 - wx**2*R1*R2*C1*C2) ** 2 + (wx*C1*(R1+R2)) ** 2)), fmt="{:.0f}", unit=" dB", dx=6, dy=-12)
fs.axlabels(ax, "频率", "Hz", "输出/输入 幅度", "dB")                    # 轴标签
ax.set_xticks([10, 100, 1e3, 1e4, 1e5]); ax.set_xticklabels(["10", "100", "1 k", "10 k", "100 k"])
ax.set_ylim(-80, 8); ax.legend(loc="lower left", fontsize=8)              # 纵轴范围和图例
fs.save(fig, "20", "20_p2_2_freq_response.png")    # 保存到 20-active-filter/img/
