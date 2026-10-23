# 18 正反转互锁的最小仿真：沿用 17 的写法，时间切成 1 ms 一小段，两只接触器 KM1（正转）、KM2（反转）各算各的。
# KM1 回路：SB1 停止（常闭）→ [SB2 正转（常开） 并联 KM1 自锁触点] →（按钮互锁时串 SB3 常闭）→（接触器互锁时串 KM2 常闭辅助触点）→ KM1 线圈
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

dt = 1e-3                                          # 每一小段 1 ms
t = np.arange(0, 9, dt)                            # 一共仿真 9 s
T_PICK, T_DROP = 0.020, 0.010                      # 线圈通电后 20 ms 才吸合到位；断电后 10 ms 才释放到位

def pressed(t0, t1):                               # 生成"在 t0 到 t1 秒之间按住"的按钮信号
    return (t >= t0) & (t < t1)                    # 返回一串 True/False

sb2 = pressed(1.0, 1.3) | pressed(5.000, 5.300)    # SB2 正转按钮：1 s 按一次；5.000 s 和 SB3 几乎同时按
sb3 = pressed(2.0, 2.3) | pressed(4.0, 4.3) | pressed(5.005, 5.305)  # SB3 反转按钮：2 s 在正转时按；4 s 停机后按；5.005 s 晚 5 ms 按
sb1 = pressed(3.0, 3.3) | pressed(4.6, 4.9) | pressed(7.0, 7.3)       # SB1 停止按钮

def run(mode):                                     # mode："none" 不互锁、"elec" 接触器互锁、"double" 按钮 + 接触器双重互锁
    km1 = np.zeros_like(t, dtype=bool)             # KM1 衔铁状态：True = 吸合（主触点闭合、常闭辅助触点断开）
    km2 = np.zeros_like(t, dtype=bool)             # KM2 衔铁状态
    coil1 = np.zeros_like(t, dtype=bool)           # KM1 线圈有没有通电（用来看"白白通电"的那十几毫秒）
    coil2 = np.zeros_like(t, dtype=bool)           # KM2 线圈有没有通电
    n1 = n2 = 0.0                                  # 两只线圈各自的计时器：通电（或断电）已经持续了多久
    for k in range(1, len(t)):                     # 一小段一小段往前推
        n1 = n1 + dt if coil1[k - 1] != km1[k - 1] else 0.0  # 第一步：衔铁跟着线圈走——"线圈和衔铁不一致"持续了多久
        n2 = n2 + dt if coil2[k - 1] != km2[k - 1] else 0.0  # 同上，给 KM2
        km1[k] = (not km1[k - 1] and n1 >= T_PICK - 1e-9) or (km1[k - 1] and n1 < T_DROP - 1e-9)  # 通电够 20 ms 才吸合；断电不到 10 ms 仍吸着
        km2[k] = (not km2[k - 1] and n2 >= T_PICK - 1e-9) or (km2[k - 1] and n2 < T_DROP - 1e-9)  # 同上，给 KM2
        a1, a2 = km1[k], km2[k]                    # 第二步：辅助触点跟着衔铁走，再判断两个线圈回路通不通
        stop_ok = not sb1[k]                       # 停止按钮没被按，公共部分才通
        p1 = stop_ok and (sb2[k] or a1)            # KM1 回路：启动按钮或自锁触点（和 17 一样）
        p2 = stop_ok and (sb3[k] or a2)            # KM2 回路：同理
        if mode == "double":                       # 按钮互锁：复合按钮的常闭触点串在对方回路里
            p1 = p1 and not sb3[k]                 # 按着 SB3 时，KM1 回路被 SB3 常闭断开
            p2 = p2 and not sb2[k]                 # 按着 SB2 时，KM2 回路被 SB2 常闭断开
        if mode in ("elec", "double"):             # 接触器互锁：对方的常闭辅助触点串在自己回路里
            p1 = p1 and not a2                     # KM2 吸着，KM2 常闭辅助触点就是断开的
            p2 = p2 and not a1                     # KM1 吸着，KM1 常闭辅助触点就是断开的
        coil1[k], coil2[k] = p1, p2                # 记下这一刻两只线圈有没有电
    return km1, km2, coil1, coil2                  # 返回四条波形

def at(x, arr):                                    # 查表：t = x 秒时 arr 的值
    return bool(arr[int(round(x / dt))])           # 秒换成下标

res = {m: run(m) for m in ("none", "elec", "double")}  # 三种接法跑同一套按键
for m, name in [("none", "不互锁"), ("elec", "接触器互锁"), ("double", "双重互锁")]:
    k1, k2, c1, c2 = res[m]                        # 取出这一种接法的结果
    short = k1 & k2                                # 两只同时吸合 = 两相被主触点直接接通 = 相间短路
    print(f"[{name}] 两只接触器同时吸合的总时长 {short.sum() * dt * 1e3:.0f} ms")  # 打印短路时长
    for x in (1.5, 2.5, 3.5, 4.4, 5.5):            # 五个检查时刻
        print(f"   t = {x:.1f} s：KM1 {'吸' if at(x, k1) else '放'}  KM2 {'吸' if at(x, k2) else '放'}")  # 打印状态

k1, k2, c1, c2 = res["elec"]                       # 下面细看接触器互锁这一种
assert not (k1 & k2).any()                         # 结论 1：接触器互锁时，任何时刻都不会两只同时吸合
assert at(2.5, k1) and not at(2.5, k2)             # 结论 2：正转时按反转，什么也不发生
assert at(4.4, k2) and at(5.5, k1) and not at(5.5, k2)  # 结论 3：停机后能反转；两个按钮相差 5 ms 按下，只有先按的 KM1 吸合
assert (res["none"][0] & res["none"][1]).sum() > 0 # 结论 4：不互锁时会出现同时吸合
d1, d2 = res["double"][0], res["double"][1]        # 双重互锁的两条衔铁波形
assert not (d1 & d2).any() and at(2.5, d2) and not at(5.5, d1) and not at(5.5, d2)  # 结论 5：双重互锁能直接反转；两个一起按则谁也不吸

on1 = np.argmax(k1[4900:]) + 4900                  # 5 s 附近 KM1 吸合的下标
w2 = c2[5000:5100].sum()                           # 5.0~5.1 s 之间 KM2 线圈一共通电了几毫秒
print(f"[竞赛] SB2 在 5.000 s、SB3 在 5.005 s 按下：KM1 在 {t[on1]:.3f} s 吸合，KM2 线圈白白通电 {w2:.0f} ms 后被切断")  # 打印竞赛过程
assert w2 == 15                                    # 20 ms − 5 ms = 15 ms
sw = np.argmax(d2[2000:]) + 2000                   # 双重互锁：2 s 按 SB3 后 KM2 吸合的下标
off = np.argmin(d1[2000:]) + 2000                  # 双重互锁：KM1 释放的下标
print(f"[双重互锁] 2.000 s 按 SB3：KM1 在 {t[off]:.3f} s 释放，KM2 在 {t[sw]:.3f} s 吸合，中间空档 {(t[sw] - t[off]) * 1e3:.0f} ms")  # 打印换向空档
assert t[sw] > t[off]                              # 先断后通
gap_ms = (t[sw] - t[off]) * 1e3                    # 双重互锁的换向空档（ms）
half = 1 / (2 * 50) * 1e3                          # 50 Hz 交流电相邻两次过零的间隔（ms）
ARC_MIN, ARC_MAX = 10, 20                          # 西门子 3RT2037-1AR60 数据表：燃弧时间 10～20 ms
print(f"[燃弧] 50 Hz 每 {half:.0f} ms 过零一次；空档 {gap_ms:.0f} ms 扣掉燃弧 {ARC_MIN}～{ARC_MAX} ms，剩 {gap_ms - ARC_MAX:.0f}～{gap_ms - ARC_MIN:.0f} ms")
assert round(half) == 10 and round(gap_ms) == 20 and round(gap_ms - ARC_MAX) == 0

fig, axs = plt.subplots(4, 1, figsize=(9.5, 5.6), sharex=True)  # 四行：按钮、不互锁、接触器互锁、双重互锁
axs[0].plot(t, sb2 * 0.8 + 2.0, **fs.LS["fb"], label="SB2 正转")       # 正转按钮
axs[0].plot(t, sb3 * 0.8 + 1.0, **fs.LS["third"], label="SB3 反转")    # 反转按钮
axs[0].plot(t, sb1 * 0.8 + 0.0, color="0.3", lw=1.0, label="SB1 停止")  # 停止按钮（灰色细实线）
axs[0].set_yticks([0.4, 1.4, 2.4]); axs[0].set_yticklabels(["SB1", "SB3", "SB2"]); axs[0].set_ylim(-0.2, 3.0)  # 纵轴标注
axs[0].legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)  # 图例放到图外右侧
for ax, m, name in [(axs[1], "none", "不互锁"), (axs[2], "elec", "接触器互锁"), (axs[3], "double", "双重互锁")]:
    a, b = res[m][0], res[m][1]                    # 这一种接法的 KM1、KM2
    ax.plot(t, a * 0.8 + 1.0, **fs.LS["vout"], label="KM1 正转")       # KM1 画在上面
    ax.plot(t, b * 0.8 + 0.0, **fs.LS["vin"], label="KM2 反转")        # KM2 画在下面
    s = a & b                                      # 同时吸合的时段
    if s.any():                                    # 有短路就用朱红色 × 标出来
        ax.fill_between(t, -0.2, 2.5, where=s, color=fs.C["bad"], alpha=0.15, lw=0)  # 短路时段衬一层淡底色
        ax.plot(t[s][::200], np.full(s.sum(), 2.1)[::200], color=fs.C["bad"], ls="none", marker="x", label="同时吸合 = 相间短路")  # 朱红色 ×
    ax.set_yticks([0.4, 1.4]); ax.set_yticklabels(["KM2", "KM1"]); ax.set_ylim(-0.2, 2.5)  # 纵轴标注
    ax.set_title(name, fontsize=9, loc="left")     # 子图标题
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)  # 图例放到图外右侧
for x, s in [(1.0, "①"), (2.0, "②"), (3.0, "③"), (4.0, "④"), (5.0, "⑤")]:
    axs[0].text(x, 2.85, s, ha="center", fontsize=9)  # 五个事件的编号，正文逐一讲解
fs.axlabels(axs[3], "时间", "s")                    # 横轴
fs.save(fig, "18", "18_p2_2_sim.png")              # 保存

z = slice(4990, 5060)                              # 放大 4.990~5.060 s
fig, ax = plt.subplots(figsize=fs.SIZE["tall"])    # 竞赛放大图
tm = (t[z] - 5.0) * 1e3                            # 横轴换成"从 5.000 s 起的毫秒数"
ax.plot(tm, sb2[z] * 0.8 + 6, drawstyle="steps-post", **fs.LS["fb"], label="SB2 正转按钮")       # 正转按钮
ax.plot(tm, sb3[z] * 0.8 + 4.5, drawstyle="steps-post", **fs.LS["third"], label="SB3 反转按钮")  # 反转按钮
ax.plot(tm, c1[z] * 0.8 + 3, drawstyle="steps-post", **fs.LS["cur"], label="KM1 线圈有电")      # KM1 线圈
ax.plot(tm, k1[z] * 0.8 + 3, drawstyle="steps-post", **fs.LS["vout"], label="KM1 衔铁吸合")     # KM1 衔铁
ax.plot(tm, c2[z] * 0.8 + 1.5, drawstyle="steps-post", **{**fs.LS["cur"], "alpha": 0.6}, label=f"KM2 线圈有电（{w2:.0f} ms）")       # KM2 线圈
ax.plot(tm, k2[z] * 0.8 + 1.5, drawstyle="steps-post", **fs.LS["vin"], label="KM2 衔铁（始终没吸合）")  # KM2 衔铁
fs.ref_v(ax, 20, "KM1 吸合到位，常闭辅助触点断开", y=0.25)                    # 20 ms 的竖线
ax.set_yticks([1.9, 3.4, 4.9, 6.4]); ax.set_yticklabels(["KM2", "KM1", "SB3", "SB2"])  # 纵轴
ax.set_ylim(1.0, 8.4); fs.axlabels(ax, "从 SB2 按下起的时间", "ms")       # 坐标
ax.legend(loc="upper right", fontsize=8, ncol=2)                          # 图例（右上角空着）
fs.save(fig, "18", "18_p2_3_race.png")             # 保存
