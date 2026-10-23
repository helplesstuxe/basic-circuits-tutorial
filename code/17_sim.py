# 17 自锁电路的最小仿真：把时间切成 1 ms 一小段，每一段都按"控制回路通不通 → 线圈电压够不够 → 衔铁吸没吸"推一步。
# 控制回路：电源 → SB1 停止按钮（常闭）→ [SB2 启动按钮（常开） 并联 KM 自锁触点（常开）] → KM 线圈 → 电源另一端
import sys, os                                     # 下一行让 Python 找到 code/figs 里的共享画图样式
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

dt = 1e-3                                          # 每一小段 1 ms
t = np.arange(0, 10, dt)                           # 一共仿真 10 s
PICK, DROP = 0.85, 0.45                            # 吸合门限 85%、释放门限 45%（相对额定电压 Uc）
T_PICK = 0.020                                     # 线圈电压够了以后，衔铁还要 20 ms 才能吸合到位

def pressed(t0, t1):                               # 生成"在 t0 到 t1 秒之间按住"的按钮信号
    return (t >= t0) & (t < t1)

sb2 = pressed(1.0, 1.3) | pressed(4.0, 4.3) | pressed(8.0, 8.3) | pressed(9.0, 9.3)  # 启动按钮被按下的时段
sb1 = pressed(3.0, 3.3) | pressed(9.0, 9.3)                                          # 停止按钮被按下的时段（9 s 时两个一起按）
supply = np.ones_like(t)                           # 电源电压，用额定值的倍数表示：1 就是 100%
supply[pressed(5.0, 5.4)] = 0.70                   # 5.0 s：电压跌到 70%（还在释放门限以上）
supply[pressed(6.0, 6.5)] = 0.30                   # 6.0 s：电压跌到 30%（低于释放门限，相当于"停电"）

km = np.zeros_like(t, dtype=bool)                  # KM 衔铁状态：True = 吸合（主触点、自锁触点都闭合）
timer = 0.0                                        # 记录"线圈电压已经够了"持续了多久
for k in range(1, len(t)):
    aux = km[k - 1]                                # 自锁触点跟着衔铁走：上一刻吸合，这一刻就是闭合的
    path = (not sb1[k]) and (sb2[k] or aux)        # 回路通 = 停止按钮没被按 并且（启动按钮按着 或者 自锁触点闭合）
    v_coil = supply[k] if path else 0.0            # 回路通，线圈就拿到电源电压；不通就是 0
    if not km[k - 1]:                              # 原来没吸合：要电压 ≥ 85% 并且坚持 20 ms 才吸得上
        timer = timer + dt if v_coil >= PICK else 0.0
        km[k] = timer >= T_PICK
    else:                                          # 原来已吸合：只要电压不低于 45% 就继续吸着（这就是"回差"）
        km[k] = v_coil >= DROP
        timer = 0.0

def km_at(x):                                      # 查表：t = x 秒时 KM 是否吸合
    return bool(km[int(round(x / dt))])

t_on = t[np.argmax(km)]                            # 第一次吸合的时刻
print(f"第一次吸合：t = {t_on:.3f} s（按下启动按钮后 {(t_on - 1.0) * 1e3:.0f} ms）")
for x, want, why in [(2.0, True, "松开启动按钮后仍吸合（自锁）"), (3.5, False, "按停止后释放"),
                     (5.2, True, "电压跌到 70% 仍吸合"), (6.2, False, "电压跌到 30% 释放"),
                     (7.5, False, "来电后不会自己再启动（失压保护）"), (8.5, True, "重新按启动"),
                     (9.5, False, "启动、停止一起按：停止优先")]:
    print(f"t = {x:.1f} s：KM {'吸合' if km_at(x) else '释放'} —— {why}")
    assert km_at(x) == want                        # 每条结论都断言一遍，参数改错会直接报错
assert abs(t_on - 1.020) < 0.002                   # 吸合比按下晚 20 ms
press = 0.4                                        # 图 17-p1-4 里按住启动按钮 0.4 s（1.0～1.4 s）
print(f"[直觉篇] 按住 {press:.1f} s，是吸合时间 {T_PICK * 1e3:.0f} ms 的 {press / T_PICK:.0f} 倍")
assert round(press / T_PICK) == 20

fig, axs = plt.subplots(3, 1, figsize=(8, 5.2), sharex=True)
axs[0].plot(t, supply * 100, **fs.LS["vin"], label="电源电压")
fs.ref_h(axs[0], PICK * 100, "吸合门限 85%", x=0.995)
fs.ref_h(axs[0], DROP * 100, "释放门限 45%", x=0.995)
axs[0].set_ylim(0, 120); axs[0].set_ylabel("电压 / %Uc"); axs[0].legend(loc="lower left", fontsize=8)
axs[1].plot(t, sb2 * 1.0 + 1.5, **fs.LS["fb"], label="SB2 启动按钮（按下 = 高）")
axs[1].plot(t, sb1 * 1.0, **fs.LS["third"], label="SB1 停止按钮（按下 = 高）")
axs[1].set_yticks([0.5, 2.0]); axs[1].set_yticklabels(["SB1", "SB2"]); axs[1].set_ylim(-0.3, 3.9)
axs[1].legend(loc="upper center", fontsize=8, ncol=2)
axs[2].plot(t, km * 1.0, **fs.LS["vout"], label="KM 吸合 = 电机运转")
axs[2].set_yticks([0, 1]); axs[2].set_yticklabels(["释放", "吸合"]); axs[2].set_ylim(-0.3, 1.5)
axs[2].legend(loc="center right", fontsize=8)
for x, s in [(1.0, "①"), (3.0, "②"), (4.0, "③"), (5.0, "④"), (6.0, "⑤"), (8.0, "⑥"), (9.0, "⑦")]:
    axs[2].text(x, 1.2, s, ha="center", fontsize=10)  # 七个事件的编号，正文逐一讲解
fs.axlabels(axs[2], "时间", "s")
fs.save(fig, "17", "17_p2_2_sim.png")

# ---- 回差的来历（欧姆龙技术指南：F = μ0·S/2 ·(N·I/g)²）：吸力相同时，所需电流与气隙 g 成正比 ----
def current_for_same_force(g_ratio):               # g_ratio = 新气隙 / 原气隙
    return g_ratio                                  # (N·I/g)² 不变 ⇒ I ∝ g
print(f"[回差] 气隙缩小到 1/2：维持同样吸力的电流（电压）只要原来的 {current_for_same_force(0.5):.1f} 倍")
assert current_for_same_force(0.5) == 0.5
print(f"[回差] 欧姆龙 MY4：吸合 ≤ 80%，释放 ≥ 10%；本仿真 {PICK:.0%} / {DROP:.0%}，在 TeSys D 范围（吸合 ≥ 85%，释放 30%～60%）内")
assert PICK >= 0.85 and 0.30 <= DROP <= 0.60

