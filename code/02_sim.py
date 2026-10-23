import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
# 02 同相放大最小仿真：信号源内阻 R_s 从 100 Ω 增大到 1 MΩ 时，比较反相放大和同相放大的实际倍数。
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

R1, Rf = 10e3, 20e3                                # 两种电路都用 R1 = 10 kΩ、Rf = 20 kΩ
G_inv = Rf / R1                                    # 反相放大：|A_v| = Rf/R1 = 2
G_non = 1 + Rf / R1                                # 同相放大：A_v = 1 + Rf/R1 = 3
Rs = np.logspace(2, 6, 300)                        # 信号源内阻从 100 Ω 扫到 1 MΩ

inv = Rf / (Rs + R1)                               # 反相：内阻和 R1 串联，倍数变成 Rf/(Rs+R1)
non = np.full_like(Rs, G_non)                      # 同相：输入端几乎不取电流，内阻上没有压降，倍数不变

fig, ax = plt.subplots(figsize=fs.SIZE["single"])  # 一张图
ax.axhline(G_inv, **fs.LS["ref"])                  # 灰色点线：反相放大的设计值 2
ax.semilogx(Rs, inv, **fs.LS["third"], label="反相放大（设计 $|A_v|$ = 2）")   # 红紫色点划线
ax.semilogx(Rs, non, **fs.LS["vout"], label="同相放大（设计 $A_v$ = 3）")      # 橙色实线
for r in (1e3, 100e3):                             # 在内阻 1 kΩ 和 100 kΩ 处标数
    g = Rf / (r + R1)                              # 这一点反相放大的实际倍数
    print(f"内阻 {r/1e3:g} kΩ：反相放大实际 |A_v| = {g:.2f}，同相放大仍为 {G_non:.0f}")
    fs.mark(ax, r, g, fmt="{:.2f}", dx=6, dy=-12)  # 黑点 + 数值
fs.mark(ax, 1e3, G_non, fmt="{:.0f}", dx=6, dy=4)  # 同相放大的倍数 3
assert abs(Rf / (100e3 + R1) - 0.18) < 0.01        # 内阻 100 kΩ 时反相只剩约 0.18 倍
assert np.all(non == 3)                            # 同相放大不受内阻影响
fs.axlabels(ax, "信号源内阻 $R_s$", "Ω", "放大倍数", None)                    # 轴标签
ax.set_ylim(0, 3.5); ax.legend(loc="center right", fontsize=8)             # 纵轴范围和图例
fs.save(fig, "02", "02_p2_2_source_compare.png")   # 保存到 02-noninverting-amp/img/
