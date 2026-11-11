import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
# 20 阻抗：R = 16 kΩ 和 C = 10 nF 串联、并联时，「电压幅度 ÷ 电流幅度」随频率怎么变，电流和电压错开多少。
# 不用复数：串联时两段电压错开 90°，并联时两路电流错开 90°，都按直角三角形（勾股定理）合成。
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

R, C = 16e3, 10e-9                                 # 电阻 16 kΩ，电容 10 nF
fc = 1 / (2 * np.pi * R * C)                       # 容抗等于 R 的频率 ≈ 995 Hz

f = np.logspace(1, 5, 800)                         # 频率从 10 Hz 扫到 100 kHz
Xc = 1 / (2 * np.pi * f * C)                       # 容抗 X_C = 1/(2πfC)：频率每乘 10，容抗除以 10
Zs = np.sqrt(R ** 2 + Xc ** 2)                     # 串联：同一个电流，两段电压按勾股定理合成
Zp = R * Xc / np.sqrt(R ** 2 + Xc ** 2)            # 并联：同一个电压，两路电流按勾股定理合成
ph_s = np.degrees(np.arctan(Xc / R))               # 串联：电流比总电压早的角度，tanφ = X_C/R
ph_p = np.degrees(np.arctan(R / Xc))               # 并联：总电流比电压早的角度，tanφ = R/X_C

assert np.allclose(Zs, R * np.sqrt(1 + (fc / f) ** 2))     # 串联阻抗 = R·√(1 + (fc/f)²)
assert np.allclose(Zp, R / np.sqrt(1 + (f / fc) ** 2))     # 并联阻抗 = R/√(1 + (f/fc)²)，形状和低通一样
assert np.all(Zs >= np.maximum(R, Xc)) and np.all(Zp <= np.minimum(R, Xc))  # 串联比大的还大，并联比小的还小

k = lambda z: f"{z/1e3:8.2f} kΩ" if z >= 1e3 else f"{z:8.1f} Ω "
print(f"fc = {fc:.0f} Hz（这里 X_C = R）")
print("   频率   |   X_C       |  串联 |Z|   φ    |  并联 |Z|   φ")
for fx in (10, 100, fc, 1e3, 1e4, 1e5):            # 几个代表频率
    x = 1 / (2 * np.pi * fx * C)
    zs, zp = np.sqrt(R ** 2 + x ** 2), R * x / np.sqrt(R ** 2 + x ** 2)
    print(f" {fx:8.0f} | {k(x)} | {k(zs)} {np.degrees(np.arctan(x/R)):5.1f}° | {k(zp)} {np.degrees(np.arctan(R/x)):5.1f}°")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)  # 上：阻抗大小；下：错开的角度
ax1.loglog(f, np.full_like(f, R), **fs.LS["vin"], label="电阻 R（不随频率变）")    # 蓝色
ax1.loglog(f, Xc, **fs.LS["fb"], label="容抗 $X_C$（每十倍频率降十倍）")            # 蓝绿色虚线
ax1.loglog(f, Zs, **fs.LS["vout"], label="R、C 串联")                              # 橙色
ax1.loglog(f, Zp, **fs.LS["third"], label="R、C 并联")                             # 红紫色点划线
fs.ref_v(ax1, fc)                                  # 灰色点线：X_C = R 的频率
fs.mark(ax1, fc, np.sqrt(2) * R, fmt="{:.0f}", unit=" Ω", dx=6, dy=2)            # 串联：√2·R ≈ 22.6 kΩ
fs.mark(ax1, fc, R / np.sqrt(2), fmt="{:.0f}", unit=" Ω", dx=6, dy=-12)          # 并联：R/√2 ≈ 11.3 kΩ
fs.axlabels(ax1, None, None, "阻抗大小 |Z|", "Ω")
ax1.set_ylim(80, 3e6); ax1.legend(loc="lower left", fontsize=8, ncol=2)

ax2.semilogx(f, ph_s, **fs.LS["vout"], label="串联：电流比总电压早")             # 橙色
ax2.semilogx(f, ph_p, **fs.LS["third"], label="并联：总电流比电压早")            # 红紫色点划线
fs.ref_v(ax2, fc, f"fc ≈ {fc:.0f} Hz")
fs.ref_h(ax2, 45)
fs.mark(ax2, fc, 45.0, fmt="{:.0f}", unit="°", dx=6, dy=-12)
fs.axlabels(ax2, "频率", "Hz", "电流超前电压", "°")
ax2.set_yticks([0, 45, 90]); ax2.set_ylim(-5, 100); ax2.legend(loc="center right", fontsize=8)
ax2.set_xticks([10, 100, 1e3, 1e4, 1e5]); ax2.set_xticklabels(["10", "100", "1 k", "10 k", "100 k"])
fs.save(fig, "20", "20_p2_11_rc_impedance.png")    # 保存到 20-active-filter/img/
