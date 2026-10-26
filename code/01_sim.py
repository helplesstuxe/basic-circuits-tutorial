# 01 最小仿真：RC 电路先充电、再放电。思路：把时间切成很多 1 ms 的小段，每一段里
#   ① 用欧姆定律算流过电阻的电流；② 电流 × 时间 = 流进电容的电荷；③ 电荷 ÷ C = 电容电压涨了多少。
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

V_i = 5.0                 # 电源电压 5 V（蓝色曲线）
R = 10e3                  # 电阻 10 kΩ
C = 100e-6                # 电容 100 μF
tau = R * C               # 时间常数 τ = RC = 1 s
dt = 1e-3                 # 每一小段 1 ms，远小于 τ，算出来才准
t = np.arange(0, 10 * tau, dt)                     # 一共算 10 s
v_src = np.where(t < 5 * tau, V_i, 0.0)            # 前 5τ 接 5 V（充电），之后把输入接到 0 V（放电）
v_c = np.zeros_like(t)                             # 电容电压 V_C，一开始电容是空的：0 V
for k in range(1, len(t)):                         # 一小段一小段往前算
    i = (v_src[k - 1] - v_c[k - 1]) / R            # ① 电阻两端的电压差 ÷ R = 电流（放电时为负）
    v_c[k] = v_c[k - 1] + i * dt / C               # ②③ 电荷 i·dt 流进电容，电压上涨 i·dt/C

def v_at(x):                                       # 查表：取 t = x 秒时的 V_C
    return v_c[int(round(x / dt))]

exact = V_i * (1 - np.exp(-1))                     # 公式答案：t = τ 时应为 V_i·(1 − e^-1)
print(f"t = τ  : 仿真 {v_at(tau):.3f} V，公式 {exact:.3f} V，占 {v_at(tau)/V_i*100:.1f}%")
print(f"t = 5τ : 仿真 {v_at(5*tau - dt):.3f} V，占 {v_at(5*tau - dt)/V_i*100:.1f}%")
print(f"放电 1τ 后（t = 6τ）: {v_at(6*tau):.3f} V，剩 {v_at(6*tau)/v_at(5*tau)*100:.1f}%")
assert abs(v_at(tau) - exact) < 0.01               # 逐步算法和公式误差小于 10 mV
assert v_at(5 * tau - dt) > 0.99 * V_i              # 5τ 时已经超过 99%，工程上算「充满」
assert v_at(0.01) < 0.1                            # 刚接通 10 ms 时还不到 0.1 V：电容电压不能突变

fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t, v_src, **fs.LS["vin"], label="$V_i$ 输入")                 # 蓝色：输入
ax.plot(t, v_c, **fs.LS["vout"], label="$V_C$ 电容电压（输出）")       # 橙色：电容电压
fs.ref_v(ax, tau, "t = τ"); fs.ref_v(ax, 5 * tau, "t = 5τ"); fs.ref_v(ax, 6 * tau, "t = 6τ")
print("[参考线] t = τ = 1 s, 5τ = 5 s, 6τ = 6 s")
fs.mark(ax, tau, v_at(tau), unit=" V", dx=4, dy=-12)                   # 标出 1τ 时的电压（并打印）
fs.mark(ax, 5 * tau, v_at(5 * tau - dt), unit=" V", dx=-38, dy=-14)
fs.mark(ax, 6 * tau, v_at(6 * tau), unit=" V", dx=4, dy=4)
fs.axlabels(ax, "时间", "s", "电压", "V")
ax.set_ylim(-0.3, 6.2); ax.legend(loc="upper right")
fs.save(fig, "01", "01_p2_2_rc_charge.png")         # 保存到 01-components-basics/img/
