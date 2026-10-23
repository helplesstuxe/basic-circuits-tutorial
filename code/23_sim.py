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
assert bad[0] < V_IL and bad[1] > V_IH             # 结论 1：省电流的设计，按恒定 CTR 算，CTR 高的那只能用，换一只最小 CTR 的就读成高电平
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

# ---------------- B 部分：上拉电阻越大，上升沿越慢（模型按 PC817 的 SPICE 结果标定） ----------------
# 光耦里的光敏三极管本身就慢，原因有两个：
#   ① LED 灭了以后，三极管基区里存着的电荷要慢慢放掉，集电极电流 i_C 不会立刻变 0，而是按时间常数 TAU_B 慢慢减小（LED 亮时也是慢慢增大）；
#   ② 集电极和基极之间的结电容只有十几 pF，但三极管会把它"放大"（米勒效应），在输出端看起来像一个几 nF 的电容 C_EQ。
TAU_B = 8e-6                                       # 标定值：基区电荷的时间常数 8 μs
C_EQ = 3.3e-9                                      # 标定值：输出端等效电容 3.3 nF（旧版示意值 1 nF 太小，上升时间少算 3～5 倍）
CTR_B, I_F_ON = 0.5, (V_IN - V_F) / 2.2e3          # B 部分用手册最小 CTR 50%、R_in = 2.2 kΩ（与 SPICE 核对时的条件相同）
SPICE_T3, SPICE_V47 = {4.7e3: 27.0, 10e3: 48.6}, 2.01   # PC817 SPICE 结果（review/spice/23.md）：升到 3.0 V 的时间 / μs；47 kΩ 熄灭 100 μs 后的电压 / V
f_sig, n_per = 5e3, 2                              # 5 kHz 方波，看两个周期
t = np.linspace(0, n_per / f_sig, 4001)            # 时间步长 0.1 μs
led_on = (t % (1 / f_sig)) < (0.5 / f_sig)         # 每个周期前一半 LED 亮
dt = t[1] - t[0]

def edge_wave(r_l):                                # 逐点计算：先算三极管电流，再算输出端电容的充放电
    v = np.empty_like(t); v[0] = VCC               # 开始时 LED 没亮过，输出在 5 V
    i_c, a = 0.0, np.exp(-dt / TAU_B)              # i_c：三极管此刻能导通的电流
    for k in range(1, len(t)):
        i_goal = CTR_B * I_F_ON if led_on[k] else 0.0   # LED 亮时"目标"是 CTR·I_F，灭时是 0
        i_c = i_goal + (i_c - i_goal) * a          # 但 i_c 只能按 TAU_B 慢慢追过去
        i_cap = (VCC - v[k - 1]) / r_l - i_c       # 上拉电阻送来的电流减去三极管拿走的，剩下的给电容充电
        v[k] = min(VCC, max(VCE_SAT, v[k - 1] + i_cap / C_EQ * dt))   # 输出夹在 0.2 V 和 5 V 之间
    return v

RLS = [1e3, 4.7e3, 10e3, 47e3]
waves = {r: edge_wave(r) for r in RLS}
off = (t >= 1 / f_sig / 2) & (t < 1 / f_sig)       # 第一次熄灭的那半个周期（100 μs 到 200 μs）
t_off, res_b = t[off] - t[off][0], {}
for r in RLS:
    v = waves[r][off]
    t3 = t_off[np.argmax(v >= V_IH)] if v.max() >= V_IH else float("nan")   # 熄灭后升到 3.0 V 的时间
    res_b[r] = (v[0], t3, v[-1])
    t3s = f"{t3*1e6:.1f} μs" if t3 == t3 else "半个周期内没升到"
    print(f"[B] R_L = {r/1e3:>4.1f} kΩ：LED 亮时输出 {v[0]:.2f} V；熄灭后升到 3.0 V 要 {t3s}；熄灭 100 μs 后 {v[-1]:.2f} V")
on2 = (t >= 1 / f_sig) & (t < 1.5 / f_sig)         # 第二次点亮：看下降沿
for r in (4.7e3, 10e3):
    print(f"[B] R_L = {r/1e3:>4.1f} kΩ：LED 点亮后降到 1.5 V 要 {t[on2][np.argmax(waves[r][on2] <= V_IL)]*1e6 - 200:.1f} μs")
assert 2.0 < res_b[1e3][0] < 3.0                   # 结论 4：1 kΩ 配 4.91 mA、CTR 50%，三极管给的电流不够，低电平只到 2.5 V 左右
for r, s3 in SPICE_T3.items():                     # 结论 5：标定模型和 SPICE 的差别在 15% 以内
    assert abs(res_b[r][1] * 1e6 / s3 - 1) < 0.15
assert abs(res_b[47e3][2] / SPICE_V47 - 1) < 0.15
assert res_b[47e3][2] < V_IH                       # 结论 6：47 kΩ 在半个周期内连 3.0 V 都升不到

fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.fill_between(t * 1e6, 0, 5.5, where=led_on, color=fs.C["ref"], alpha=0.12, lw=0, label="LED 亮")
for r, st in zip(RLS, ["vin", "vout", "fb", "bad"]):
    ax.plot(t * 1e6, waves[r], **fs.LS[st], label=f"$R_L$ = {r/1e3:g} kΩ")
fs.ref_h(ax, V_IH, "3.0 V", x=0.99, ha="right")
fs.mark(ax, 199.9, res_b[47e3][2], "{:.2f}", " V", dx=-44, dy=6)
fs.axlabels(ax, "时间", "μs", "输出电压", "V"); ax.set_ylim(0, 6.2)
ax.legend(loc="upper center", fontsize=7.5, ncol=5)
fs.save(fig, "23", "23_p2_3_rise.png")
