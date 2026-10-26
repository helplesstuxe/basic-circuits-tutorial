# 19 射极跟随器最小仿真：运放（输出电流有限）直接带 50 Ω 负载，和"运放 → NPN 射极跟随器 → 负载"对比。
# 三极管用指数模型 I_C = I_S·e^(V_BE/V_T)（与 03 相同的思路），β 取 50；运放按 LM358 典型拉电流 30 mA 限流。
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

VT, IS, BETA = 0.02585, 1e-13, 50.0                # 热电压 25.85 mV；I_S 示意值；β 示意值（TIP31 在 1 A 时 ≥ 25）
VCC, I_LIM = 12.0, 0.030                           # 集电极电源 12 V；LM358 在 15 V 供电时典型拉电流 30 mA
V_OH = 12.0 - 1.5                                  # 运放输出最高约到正电源下 1.5 V（按 12 V 供电估）

def direct(vi, rl):                                # 运放直接接负载：电流不超过 I_LIM 时输出 = V_i，否则被限流
    return np.minimum(vi, I_LIM * rl)              # 负载电压 = min(想要的电压, 限流 × 负载电阻)

def follower(vb, rl):                              # 射极跟随器：已知基极电压 vb，二分法解出发射极电压 V_o
    lo, hi = 0.0, vb                               # V_o 一定在 0 和 vb 之间
    for _ in range(60):                            # 二分 60 次，精度远小于 1 μV
        vo = (lo + hi) / 2                         # 猜一个 V_o
        ic = vo / rl * BETA / (BETA + 1)           # 负载电流就是发射极电流 I_E，其中 β/(β+1) 是 I_C
        vbe = VT * np.log(ic / IS + 1)             # 管子流这么多电流需要的 V_BE
        lo, hi = (vo, hi) if vb - vo > vbe else (lo, vo)   # 基极—发射极电压还有富余，说明 V_o 可以更高
    return vo, vbe, vo / rl                        # 返回 V_o、V_BE、I_E

# ---------- ① 正弦输入：V_i = 5 V ± 2 V，50 Hz，负载 50 Ω ----------
R_L = 50.0
t = np.linspace(0, 0.04, 801)                      # 0 ~ 40 ms，两个周期
vi = fs.sine(t, 50, amp=2.0, offset=5.0)           # 输入正弦
res = np.array([follower(v, R_L) for v in vi])     # 每一点解一次
vo, vbe, ie = res[:, 0], res[:, 1], res[:, 2]
vd = direct(vi, R_L)                               # 运放直接带 50 Ω
gain = (vo.max() - vo.min()) / (vi.max() - vi.min())
print(f"[正弦] 输入 {vi.min():.1f}~{vi.max():.1f} V；跟随器输出 {vo.min():.2f}~{vo.max():.2f} V；V_BE {vbe.min():.3f}~{vbe.max():.3f} V；交流增益 {gain:.3f}")
print(f"[正弦] 运放直接带 50 Ω：输出被限在 {vd.max():.2f} V（30 mA × 50 Ω）")
assert 0.6 < vbe.min() and vbe.max() < 0.8         # 结论 1：输出比输入低 0.6~0.8 V，即一个 V_BE
assert gain > 0.98                                 # 结论 2：交流增益约等于 1
assert vd.max() < 0.35 * vi.max()                  # 结论 3：直接带负载时输出被限流压扁

fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi, **fs.LS["vin"], label="输入 $V_i$（基极）")
ax.plot(t * 1e3, vo, **fs.LS["vout"], label="跟随器输出 $V_o$（发射极）")
ax.plot(t * 1e3, vd, **fs.LS["bad"], label="运放直接带 50 Ω")
k = np.argmax(vi)                                  # 在输入最高点标出两条线的差
fs.mark(ax, t[k] * 1e3, vi[k], "{:.2f}", " V", dx=6, dy=2)
fs.mark(ax, t[k] * 1e3, vo[k], "{:.2f}", " V", dx=6, dy=-12)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(0, 8.5)
ax.legend(loc="upper right", fontsize=8, ncol=3)
fs.save(fig, "19", "19_p2_2_sine.png")

# ---------- ② 负载扫描：V_i = 5 V，R_L 从 10 Ω 到 1 kΩ ----------
RL = np.logspace(1, 3, 200)
v_dir = direct(5.0, RL)                            # 运放直接带
v_fol = np.array([follower(5.0, r)[0] for r in RL])   # 运放 → 跟随器（反馈只取运放自己的输出）
v_loop = np.full_like(RL, 5.0)                     # 反馈取自发射极：运放自动多给一个 V_BE，V_o = V_i
for r in (1000, 100, 50, 20):
    vf, vb_, ie_ = follower(5.0, r)
    p = (VCC - vf) * ie_ * BETA / (BETA + 1)       # 管子功耗 = V_CE × I_C
    print(f"[负载] R_L = {r:>4} Ω：直接 {float(direct(5.0, r)):.2f} V；跟随器 {vf:.2f} V（I_E {ie_*1e3:.0f} mA，I_B {ie_/(BETA+1)*1e3:.2f} mA，管耗 {p:.2f} W）")
vf50, vbe50, ie50 = follower(5.0, 50.0)
p50 = (VCC - vf50) * ie50 * BETA / (BETA + 1)
vf20 = follower(5.0, 20.0)[0]; vf1k = follower(5.0, 1000.0)[0]
print(f"[负载] 直接接法要 R_L ≥ {5.0 / I_LIM:.0f} Ω（电流 ≤ 30 mA）才不被限流")
print(f"[负载] 负载从 1 kΩ 变到 20 Ω（电流变 50 倍），跟随器输出只变 {(vf1k - vf20)*1e3:.0f} mV")
print(f"[反馈] 反馈取自发射极时，50 Ω 负载下运放输出 = {5.0 + vbe50:.2f} V（低于上限 {V_OH:.1f} V），基极电流 {ie50/(BETA+1)*1e3:.2f} mA（低于 30 mA）")
assert vf1k - vf20 < 0.2                           # 结论 4：负载变 50 倍，输出只变一百多毫伏
assert ie50 / (BETA + 1) < I_LIM and 5.0 + vbe50 < V_OH   # 结论 5：反馈接发射极时运放完全带得动
P_3904, RTH_3904 = 0.625, 200.0                   # onsemi 2N3904（TO-92）：环境 25 °C 时额定 625 mW；结到环境热阻 200 °C/W
print(f"[功耗] 50 Ω 时管耗 {p50:.2f} W，超过 2N3904 额定 {P_3904 * 1e3:.0f} mW（25 °C）；温升 {p50:.2f} × {RTH_3904:.0f} = {p50 * RTH_3904:.0f} °C，25 °C 环境下结温约 {25 + p50 * RTH_3904:.0f} °C，超过 150 °C 上限")
assert P_3904 < p50 < 2.0 and 25 + p50 * RTH_3904 > 150   # 结论 6：管耗超过 2N3904 的额定值，但在 TIP31 不加散热片的 2 W 以内

fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.semilogx(RL, v_dir, **fs.LS["bad"], label="运放直接带负载")
ax.semilogx(RL, v_fol, **fs.LS["vout"], label="运放 → 跟随器")
ax.semilogx(RL, v_loop, **fs.LS["fb"], label="反馈取自发射极")
fs.ref_h(ax, 5.0 - 0.7, "比 5 V 低 0.7 V", x=0.02, ha="left")
fs.mark(ax, 50, vf50, "{:.2f}", " V", dx=4, dy=-12)
fs.mark(ax, 50, float(direct(5.0, 50)), "{:.2f}", " V", dx=8, dy=-10)
fs.axlabels(ax, "负载电阻 $R_L$", "Ω", "负载电压", "V"); ax.set_ylim(0, 6)
ax.legend(loc="lower right", fontsize=8)
fs.save(fig, "19", "19_p2_3_load.png")
