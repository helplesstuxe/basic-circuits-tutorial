import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
# 20 无源 RC 低通与高通：同一对 R = 16 kΩ、C = 10 nF，输出取电容是低通，取电阻是高通。
# 按幅度公式和相位公式扫频，打印关键频率处的数值，画出幅频、相频曲线和渐近线。
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

R, C = 16e3, 10e-9                                 # 电阻 16 kΩ，电容 10 nF
tau = R * C                                        # 时间常数 τ = RC = 0.16 ms
fc = 1 / (2 * np.pi * tau)                         # 截止频率 fc = 1/(2πRC) ≈ 995 Hz

f = np.logspace(1, 5, 800)                         # 频率从 10 Hz 扫到 100 kHz
x = f / fc                                         # 频率比 f/fc，也等于 R/X_C
lp = 1 / np.sqrt(1 + x ** 2)                       # 低通（输出取电容）：Vo/Vi = 1/√(1+x²)
hp = x / np.sqrt(1 + x ** 2)                       # 高通（输出取电阻）：Vo/Vi = x/√(1+x²)
ph_lp = -np.degrees(np.arctan(x))                  # 低通相位：输出比输入晚 arctan(x)，记成负角度
ph_hp = 90 - np.degrees(np.arctan(x))              # 高通相位：输出比输入早 90° − arctan(x)
dB = lambda h: 20 * np.log10(h)                    # 倍数换成分贝

assert np.allclose(lp ** 2 + hp ** 2, 1)           # 直角三角形：两条直角边的平方和等于斜边的平方
assert np.allclose(ph_hp - ph_lp, 90)              # 电阻电压永远比电容电压早四分之一周期（90°）

print(f"τ = {tau*1e3:.2f} ms，fc = {fc:.0f} Hz")
print(" f/fc | 低通 倍数  dB    相位  | 高通 倍数  dB    相位")
for k in (0.1, 0.5, 1, 2, 10):                     # 关键频率点：0.1、0.5、1、2、10 倍 fc
    a, b = 1 / np.sqrt(1 + k * k), k / np.sqrt(1 + k * k)
    pa, pb = -np.degrees(np.arctan(k)), 90 - np.degrees(np.arctan(k))
    print(f" {k:4g} | {a:.3f} {dB(a):5.1f} {pa:6.1f}° | {b:.3f} {dB(b):5.1f} {pb:+6.1f}°")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)  # 上：幅度；下：相位
ax1.semilogx(f, dB(lp), **fs.LS["vout"], label="低通（输出取电容）")       # 橙色
ax1.semilogx(f, dB(hp), **fs.LS["third"], label="高通（输出取电阻）")      # 红紫色点划线
ax1.semilogx(f, np.minimum(0, -20 * np.log10(x)), **fs.LS["good"], label="渐近线（两段直线）")  # 低通渐近线
ax1.semilogx(f, np.minimum(0, 20 * np.log10(x)), **fs.LS["good"])         # 高通渐近线
fs.ref_h(ax1, -3)                                  # 灰色点线：−3 dB
fs.ref_v(ax1, fc)                                  # 灰色点线：截止频率
fs.mark(ax1, fc, dB(1 / np.sqrt(2)), fmt="{:.1f}", unit=" dB", dx=6, dy=-14)
fs.mark(ax1, 10 * fc, dB(1 / np.sqrt(101)), fmt="{:.1f}", unit=" dB", dx=6, dy=2)  # 低通 10 fc 处 −20 dB
fs.mark(ax1, fc / 10, dB(0.1 / np.sqrt(1.01)), fmt="{:.1f}", unit=" dB", dx=6, dy=2)  # 高通 0.1 fc 处 −20 dB
fs.axlabels(ax1, None, None, "输出/输入 幅度", "dB")
ax1.set_ylim(-45, 6); ax1.legend(loc="lower center", fontsize=8, ncol=3)

ax2.semilogx(f, ph_lp, **fs.LS["vout"], label="低通：输出落后")           # 橙色
ax2.semilogx(f, ph_hp, **fs.LS["third"], label="高通：输出超前")          # 红紫色点划线
fs.ref_h(ax2, 0, None)                             # 0° 参考线
fs.ref_v(ax2, fc, f"fc ≈ {fc:.0f} Hz")              # 截止频率（标签写在下图顶端）
fs.mark(ax2, fc, -45.0, fmt="{:.0f}", unit="°", dx=6, dy=-12)
fs.mark(ax2, fc, 45.0, fmt="{:+.0f}", unit="°", dx=6, dy=2)
fs.axlabels(ax2, "频率", "Hz", "相位（输出相对输入）", "°")
ax2.set_yticks([-90, -45, 0, 45, 90]); ax2.set_ylim(-100, 100); ax2.legend(loc="center right", fontsize=8)
ax2.set_xticks([10, 100, 1e3, 1e4, 1e5]); ax2.set_xticklabels(["10", "100", "1 k", "10 k", "100 k"])
fs.save(fig, "20", "20_p2_6_rc_bode.png")          # 保存到 20-active-filter/img/
