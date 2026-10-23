# P3 最小仿真：开环增益 A 有限时，反相放大器的闭环放大倍数和反相端电压 V- 各是多少。
# 思路：运放只做一件事 V_o = A·(V+ − V-)；反相端节点满足「流进 = 流出」（输入电流为 0），
#      两式联立就能解出 V_o，不需要任何「虚短」假设。看 A 越大，结果越接近 −R_f/R_1、V- 越接近 0。
import sys, os                                     # 下一行让 Python 找到 code/figs 里的共享画图样式
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

R1, Rf = 10e3, 100e3                               # 输入电阻 R1 = 10 kΩ，反馈电阻 Rf = 100 kΩ
V_i = 0.5                                          # 输入电压 0.5 V（直流，便于看清数字）

def solve(A):                                      # 给定开环增益 A，解出闭环放大倍数和 V-
    # 联立 ① V_o = A·(0 − V-)  ② (V_i − V-)/R1 = (V- − V_o)/Rf，消去 V- 得：
    V_o = -(Rf / R1) * V_i / (1 + (1 + Rf / R1) / A)   # 有限 A 下的输出电压
    return V_o / V_i, -V_o / A                     # 放大倍数 A_v = V_o/V_i；V- 由 ① 倒推 = −V_o/A

A = np.logspace(1, 6, 200)                         # 开环增益从 10 扫到 100 万（对数均匀取 200 个点）
gain, V_minus = solve(A)                           # 一次算出 200 个点
at = solve                                         # 打印单个点时也用同一个函数

for a in (1e2, 1e3, 1e5):                          # 打印几个典型值（正文引用的数字都来自这里）
    g, vm = at(a)
    print(f"A = {a:>8.0f}: A_v = {g:.4f}，V- = {vm*1e3:.4f} mV")
g5, vm5 = at(1e5)
assert abs(g5 - (-10)) < 0.002                     # A = 10 万时，放大倍数和理想值 −10 相差不到 0.002
assert abs(vm5) < 1e-4                             # A = 10 万时，V- 不到 0.1 mV：几乎就是 0 V（虚短）

fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a1.semilogx(A, -gain, **fs.LS["vout"], label="闭环放大倍数 $|A_v|$")      # 橙色：仿真结果
a1.axhline(Rf / R1, **fs.LS["good"], label="理想值 $R_f/R_1$ = 10")      # 黑色虚线：理想值
fs.mark(a1, 1e2, -at(1e2)[0], dx=4, dy=-12)                               # 标出 A = 100 时的值
fs.mark(a1, 1e5, -at(1e5)[0], fmt="{:.4f}", dx=-30, dy=-14)              # 标出 A = 10 万时的值
fs.axlabels(a1, "开环增益 A", None, "放大倍数", None); a1.set_ylim(0, 11); a1.legend(loc="lower right")
a2.loglog(A, abs(V_minus) * 1e3, **fs.LS["fb"], label="反相端电压 $|V_-|$")  # 蓝绿色虚线：V-
fs.mark(a2, 1e5, abs(vm5) * 1e3, fmt="{:.4f}", unit=" mV", dx=-60, dy=6)
fs.axlabels(a2, "开环增益 A", None, "$|V_-|$", "mV"); a2.legend(loc="upper right")
fs.save(fig, "P3", "P3_p2_2_gain_vs_A.png")        # 保存到 P3-opamp-basics/img/
