# 23 光耦隔离最小仿真：A 部分看 CTR 和 LED 电流 I_F 能不能把输出拉低；B 部分看上拉电阻 R_L 对上升沿的影响。
# 电路：输入侧 12 V 信号 → 限流电阻 R_in → 光耦 LED → GND1；输出侧 +5 V → 上拉 R_L → 光敏三极管集电极（= 输出）→ 发射极 → GND2。
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

V_IN, V_F = 12.0, 1.2                              # 输入侧信号 12 V；PC817 的 LED 压降典型 1.2 V
VCC, VCE_SAT = 5.0, 0.2                            # 输出侧 5 V；光敏三极管饱和压降按手册最大 0.2 V
V_IL, V_IH = 0.3 * VCC, 0.6 * VCC                  # 5 V 单片机（ATmega328P）：低于 1.5 V 读 0，高于 3.0 V 读 1

def v_out(i_f, ctr, r_l):                          # 输出电压：光敏三极管最多给 CTR·I_F，饱和后停在 V_CE(sat)
    i_c = ctr * i_f                                # 光敏三极管"想要"导通的电流
    return np.maximum(VCE_SAT, VCC - i_c * r_l)    # 上拉电阻上的压降不可能超过 VCC − V_CE(sat)

# ---------------- A 部分：CTR 与 I_F 决定输出能不能被拉低（R_L = 4.7 kΩ） ----------------
R_L = 4700.0
I_need = (VCC - VCE_SAT) / R_L                     # 拉到饱和需要的集电极电流
print(f"[A] R_L = 4.7 kΩ：拉到饱和需要 I_C ≥ {I_need*1e3:.2f} mA；读成低电平（< {V_IL:.1f} V）需要 I_C ≥ {(VCC-V_IL)/R_L*1e3:.2f} mA")
CTRS = {"新器件、CTR 偏高 200%": 2.0, "新器件、手册最小 50%": 0.5, "最小值老化 5 年后 25%": 0.25}
i_f = np.linspace(0, 6e-3, 601)                    # LED 电流从 0 扫到 6 mA
curves = {k: v_out(i_f, c, R_L) for k, c in CTRS.items()}
for k, c in CTRS.items():
    print(f"[A] {k}：要读成低电平至少需要 I_F = {(VCC-V_IL)/R_L/c*1e3:.2f} mA，要饱和需要 {I_need/c*1e3:.2f} mA")

designs = {"R_in = 22 kΩ": 22e3, "R_in = 2.2 kΩ": 2.2e3}   # 两种设计：电流省着用 vs 按老化后的 CTR 留余量
res = {}
for name, r in designs.items():
    i = (V_IN - V_F) / r                           # LED 电流 I_F = (V_in − V_F)/R_in
    res[name] = (i, [float(v_out(i, c, R_L)) for c in CTRS.values()])
    vs = "、".join(f"{v:.2f} V" for v in res[name][1])
    print(f"[A] {name}：I_F = {i*1e3:.2f} mA；三种 CTR 下输出低电平 = {vs}")
bad, good = res["R_in = 22 kΩ"][1], res["R_in = 2.2 kΩ"][1]
assert bad[0] < V_IL and bad[1] > V_IH             # 结论 1：省电流的设计，桌上那只 CTR 高的能用，换一只最小 CTR 的就读成高电平
assert max(good) < 0.25                            # 结论 2：按老化后 25% 留余量的设计，三种 CTR 都稳稳饱和
i_min_aged = I_need / 0.25
assert 3.5e-3 < i_min_aged < res["R_in = 2.2 kΩ"][0]   # 结论 3：2.2 kΩ 给的 I_F 超过"老化后仍饱和"所需的电流

fig, ax = plt.subplots(figsize=fs.SIZE["single"])
for (k, v), st in zip(curves.items(), ["vin", "vout", "bad"]):
    ax.plot(i_f * 1e3, v, **fs.LS[st], label=k)
fs.ref_h(ax, V_IL, "1.5 V 以下读成 0", x=0.98, ha="right")
fs.ref_h(ax, V_IH, "3.0 V 以上读成 1", x=0.98, ha="right")
for name, st in (("R_in = 22 kΩ", "third"), ("R_in = 2.2 kΩ", "good")):
    ax.axvline(res[name][0] * 1e3, **fs.LS[st], label=f"{name.replace('R_in', '$R_{in}$')}：$I_F$ = {res[name][0]*1e3:.2f} mA")
fs.mark(ax, res["R_in = 22 kΩ"][0] * 1e3, bad[1], "{:.2f}", " V", dx=6, dy=4)
fs.mark(ax, res["R_in = 22 kΩ"][0] * 1e3, bad[0], "{:.2f}", " V", dx=6, dy=4)
fs.axlabels(ax, "LED 电流 $I_F$", "mA", "输出电压", "V"); ax.set_ylim(0, 7.4)
ax.legend(loc="upper right", fontsize=7.5, ncol=2)
fs.save(fig, "23", "23_p2_2_ctr.png")

# ---------------- B 部分：上拉电阻越大，上升沿越慢 ----------------
C_EFF = 1e-9                                       # 示意值：把光敏三极管自身的结电容和导线电容合成 1 nF
TAU_FALL = 2e-6                                    # 示意值：LED 一亮，输出约 2 μs 内被拉低（下降沿快）
f_sig, n_per = 5e3, 2                              # 5 kHz 方波，看两个周期
t = np.linspace(0, n_per / f_sig, 4001)
led_on = (t % (1 / f_sig)) < (0.5 / f_sig)         # 每个周期前一半 LED 亮
dt = t[1] - t[0]

def edge_wave(r_l):                                # 逐点积分：LED 亮时向 V_CE(sat) 放电，灭时经 R_L 向 VCC 充电
    v = np.empty_like(t); v[0] = VCC
    for k in range(1, len(t)):
        target, tau = (VCE_SAT, TAU_FALL) if led_on[k] else (VCC, r_l * C_EFF)
        v[k] = target + (v[k - 1] - target) * np.exp(-dt / tau)
    return v

RLS = [1e3, 4.7e3, 10e3, 47e3]
waves = {r: edge_wave(r) for r in RLS}
for r in RLS:
    tau = r * C_EFF
    t_ih = tau * np.log((VCC - VCE_SAT) / (VCC - V_IH))   # 从 0.2 V 充到 3.0 V 所需时间
    t_r = 2.2 * tau                                # 10%→90% 上升时间 ≈ 2.2τ
    print(f"[B] R_L = {r/1e3:>4.1f} kΩ：τ = {tau*1e6:.1f} μs，升到 3.0 V 要 {t_ih*1e6:.1f} μs，10%→90% 上升时间 {t_r*1e6:.1f} μs，要饱和需 I_C ≥ {(VCC-VCE_SAT)/r*1e3:.2f} mA")
v47_end = waves[47e3][np.argmax(t >= 1 / f_sig) - 1]   # 第一个周期结束（LED 再次点亮）前一刻的电压
print(f"[B] 47 kΩ（相当于单片机内部上拉）：LED 熄灭 100 μs 后输出只升到 {v47_end:.2f} V")
assert waves[1e3][np.argmax(t >= 0.6 / f_sig)] > 0.98 * VCC    # 结论 4：1 kΩ 在熄灭 20 μs 后已基本到 5 V
assert 3.0 < v47_end < 0.95 * VCC                  # 结论 5：47 kΩ 在半个周期内都没升满

fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.fill_between(t * 1e6, 0, 5.5, where=led_on, color=fs.C["ref"], alpha=0.12, lw=0, label="LED 亮")
for r, st in zip(RLS, ["vin", "vout", "fb", "bad"]):
    ax.plot(t * 1e6, waves[r], **fs.LS[st], label=f"$R_L$ = {r/1e3:g} kΩ")
fs.ref_h(ax, V_IH, "3.0 V", x=0.99, ha="right")
fs.mark(ax, 199.9, v47_end, "{:.2f}", " V", dx=6, dy=-24)
fs.axlabels(ax, "时间", "μs", "输出电压", "V"); ax.set_ylim(0, 6.2)
ax.legend(loc="upper center", fontsize=7.5, ncol=5)
fs.save(fig, "23", "23_p2_3_rise.png")
