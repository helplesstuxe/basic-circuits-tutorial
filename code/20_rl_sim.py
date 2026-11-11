import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
# 20 RL 低通与高通：R = 100 Ω、L = 16 mH，时间常数 L/R = 0.16 ms，和 16 kΩ + 10 nF 的 RC 一样。
# 理想电感时 RL 和 RC 的频响完全相同；真实电感有直流电阻（这里假设 20 Ω），低频端会走样。
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

R, L = 100.0, 16e-3                                # 电阻 100 Ω，电感 16 mH
Rd = 20.0                                          # 假设的电感直流电阻（线圈铜线的电阻）20 Ω
fc = R / (2 * np.pi * L)                           # 感抗等于 R 的频率：fc = R/(2πL) ≈ 995 Hz
f = np.logspace(1, 5, 800)                         # 10 Hz ～ 100 kHz
XL = 2 * np.pi * f * L                             # 感抗 X_L = 2πfL：频率乘 10，感抗乘 10

lp = R / np.sqrt(R ** 2 + XL ** 2)                 # 低通（电感串在路上，输出取 R）：V_R / V_i
hp = XL / np.sqrt(R ** 2 + XL ** 2)                # 高通（电感接地，输出取电感两端）：V_L / V_i
rc_lp = 1 / np.sqrt(1 + (2 * np.pi * f * 16e3 * 10e-9) ** 2)   # 对照：16 kΩ + 10 nF 的 RC 低通
assert np.allclose(lp, rc_lp)                      # 时间常数相同，RL 低通和 RC 低通的曲线完全重合
assert np.allclose(lp ** 2 + hp ** 2, 1)           # 同样满足勾股定理

lp_d = R / np.sqrt((R + Rd) ** 2 + XL ** 2)        # 带直流电阻的低通：Rd 和 R 一起分压
hp_d = np.sqrt(Rd ** 2 + XL ** 2) / np.sqrt((R + Rd) ** 2 + XL ** 2)  # 带直流电阻的高通：输出是 Rd 加感抗
dB = lambda h: 20 * np.log10(h)

print(f"fc = R/(2πL) = {fc:.0f} Hz，τ = L/R = {L/R*1e3:.2f} ms（与 16 kΩ、10 nF 的 RC 相同）")
for fx in (10, 100, fc, 1e4):                      # 几个代表频率
    x = 2 * np.pi * fx * L
    print(f"{fx:7.0f} Hz：X_L = {x:8.1f} Ω；低通 {R/np.hypot(R, x):.3f}，高通 {x/np.hypot(R, x):.3f}；"
          f"带 20 Ω 直流电阻：低通 {R/np.hypot(R+Rd, x):.3f}，高通 {np.hypot(Rd, x)/np.hypot(R+Rd, x):.3f}")
print(f"直流电阻的影响：低通直流只剩 {R/(R+Rd):.3f} 倍（{dB(R/(R+Rd)):.1f} dB），−3 dB 点移到约 {(R+Rd)/(2*np.pi*L):.0f} Hz；"
      f"高通低频不再趋于 0，而是停在 {Rd/(R+Rd):.3f} 倍（{dB(Rd/(R+Rd)):.1f} dB）")

fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"], sharey=True)
a1.semilogx(f, dB(lp), **fs.LS["vout"], label="RL 低通（理想电感）")
a1.semilogx(f[::40], dB(rc_lp[::40]), ls="none", marker="o", ms=4, color=fs.C["good"], label="RC 低通（τ 相同）")
a1.semilogx(f, dB(lp_d), **fs.LS["bad"], label="电感有 20 Ω 直流电阻")
fs.mark(a1, 10, dB(R / np.hypot(R + Rd, 2 * np.pi * 10 * L)), fmt="{:.1f}", unit=" dB", dx=4, dy=-14, color=fs.C["bad"])
a1.set_title("（a）低通：电感串在路上，输出取 R", fontsize=10)
a2.semilogx(f, dB(hp), **fs.LS["third"], label="RL 高通（理想电感）")
a2.semilogx(f, dB(hp_d), **fs.LS["bad"], label="电感有 20 Ω 直流电阻")
fs.mark(a2, 10, dB(np.hypot(Rd, 2 * np.pi * 10 * L) / np.hypot(R + Rd, 2 * np.pi * 10 * L)), fmt="{:.1f}", unit=" dB", dx=4, dy=4, color=fs.C["bad"])
a2.set_title("（b）高通：电感接地，输出取电感", fontsize=10)
for ax in (a1, a2):
    fs.ref_v(ax, fc, f"fc ≈ {fc:.0f} Hz", y=0.15); fs.ref_h(ax, -3)
    ax.set_xticks([10, 100, 1e3, 1e4, 1e5]); ax.set_xticklabels(["10", "100", "1 k", "10 k", "100 k"])
    fs.axlabels(ax, "频率", "Hz", "输出/输入" if ax is a1 else None, "dB")
    ax.set_ylim(-45, 4); ax.legend(loc="lower left" if ax is a1 else "lower right", fontsize=8)
fs.save(fig, "20", "20_p2_19_rl_response.png")    # 保存到 20-active-filter/img/
