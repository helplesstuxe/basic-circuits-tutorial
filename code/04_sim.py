import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
# 04 差分放大最小仿真：10 mV 差分信号叠加 2 V、50 Hz 共模干扰，比较电阻完全匹配和一只电阻偏大 1% 时的输出。
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

t = np.linspace(0, 0.2, 4001)                      # 时间 0～200 ms
v_d = fs.sine(t, 10, amp=0.01)                     # 有用的差分信号：10 Hz、幅度 10 mV（V2 − V1）
v_cm = fs.sine(t, 50, amp=2.0)                     # 共模干扰：50 Hz、幅度 2 V，两根线上一模一样
V1 = v_cm - v_d / 2                                # 反相端那根线的电压
V2 = v_cm + v_d / 2                                # 同相端那根线的电压

def diff_amp(V1, V2, R1, R2, R3, R4):              # 四电阻差分放大的输出（理想运放，虚短虚断）
    Vp = V2 * R4 / (R3 + R4)                       # 同相端：V2 经 R3、R4 分压
    return Vp * (1 + R2 / R1) - V1 * R2 / R1       # 同相放大 Vp，再减去 V1 的反相放大

R1 = R3 = 10e3                                     # 输入电阻都是 10 kΩ
R2 = R4 = 100e3                                    # 反馈和接地电阻都是 100 kΩ，差分倍数 R2/R1 = 10
Vo_ok = diff_amp(V1, V2, R1, R2, R3, R4)           # 四只电阻完全成比例
Vo_bad = diff_amp(V1, V2, R1, R2, R3, R4 * 1.01)   # R4 偏大 1%，比例被破坏

leak = np.max(np.abs(Vo_bad - Vo_ok))              # 失配带来的共模泄漏幅度
print(f"匹配：输出最大 {Vo_ok.max()*1e3:.0f} mV（= 10 × 10 mV），共模 2 V 被完全抵消")
print(f"R4 偏大 1%：共模泄漏约 {leak*1e3:.0f} mV，占有用输出的 {leak/0.1*100:.0f}%")
assert abs(Vo_ok.max() - 0.1) < 1e-3               # 匹配时输出就是 10 × 差分信号
assert 0.015 < leak < 0.02                         # 失配 1% 时漏进约 18 mV 的 50 Hz 干扰

fig, ax = plt.subplots(figsize=fs.SIZE["single"])  # 一张图
ax.plot(t * 1e3, Vo_bad * 1e3, **fs.LS["bad"], label="$R_4$ 偏大 1%：混进 50 Hz 干扰")   # 朱红色带 ×
ax.plot(t * 1e3, Vo_ok * 1e3, **fs.LS["vout"], label="电阻匹配：$V_o$ = 10($V_2$ − $V_1$)")  # 橙色
k = np.argmax(Vo_bad)                              # 失配时输出最高的点
fs.mark(ax, t[k] * 1e3, Vo_bad[k] * 1e3, fmt="{:.0f}", unit=" mV", dx=6, dy=2)
fs.ref_h(ax, 100, "100 mV", x=0.02, ha="left")     # 灰色点线：匹配时的输出峰值
fs.axlabels(ax, "时间", "ms", "输出 $V_o$", "mV")  # 轴标签
ax.set_ylim(-150, 190); ax.legend(loc="upper center", ncol=2, fontsize=8)        # 纵轴范围和图例
fs.save(fig, "04", "04_p2_2_mismatch.png")         # 保存到 04-differential-amp/img/
