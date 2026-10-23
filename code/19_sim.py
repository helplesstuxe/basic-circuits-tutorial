# 19 星三角降压启动的最小仿真：控制回路沿用 17、18 的逐毫秒推演，再接一个"示意"电动机模型，看启动电流和转速。
# 控制回路（L → SB1 停止 → [SB2 启动 并联 KM 自锁] 之后叫"公共点"）：
#   KM 线圈：公共点 → KM 线圈
#   KT 线圈：公共点 → KM△ 常闭 → KT 线圈（时间继电器，通电延时）
#   KMY 线圈：公共点 → KT 延时断开常闭 → KM△ 常闭（互锁）→ KMY 线圈
#   KM△ 线圈：公共点 → [KT 延时闭合常开 并联 KM△ 自锁] → KMY 常闭（互锁）→ KM△ 线圈
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

dt = 1e-3                                          # 每一小段 1 ms
t = np.arange(0, 10, dt)                           # 一共仿真 10 s
T_PICK, T_DROP = 0.020, 0.010                      # 接触器：线圈通电 20 ms 吸合到位，断电 10 ms 释放到位（同 18）
T_SET = 6.0                                        # 时间继电器 KT 的延时整定值：6 s（示意值）
sb2 = (t >= 0.5) & (t < 0.8)                       # 0.5 s 按下启动按钮 SB2，按 0.3 s
sb1 = np.zeros_like(t, dtype=bool)                 # 本次不按停止

# ---------- 示意电动机：每相"简化等效电路"，全部用标幺值（额定电流 = 1、额定转矩 = 1） ----------
R1, R2, X, XM = 0.03, 0.03, 0.16, 3.0              # 定子电阻、转子电阻、漏电抗、励磁电抗（示意值）
def i_rotor(s):                                    # 转子支路电流（三角形全压时），s 是转差率 = 1 − 转速
    return 1 / (R1 + R2 / s + 1j * X)              # 欧姆定律：电压 1 除以支路阻抗
def i_line(s):                                     # 三角形全压时的线电流（转子支路 + 励磁支路）
    return abs(1 / (1j * XM) + i_rotor(s))         # 两条支路的电流相加后取大小
def torque(s):                                     # 三角形全压时的电磁转矩
    return abs(i_rotor(s)) ** 2 * R2 / s           # 转子电阻上"等效功率"除以同步转速（标幺值）
S_N = 0.03                                         # 额定转差率 3%：额定转速 = 同步转速的 97%
I_N, T_N = i_line(S_N), torque(S_N)                # 额定电流、额定转矩，用来做标幺化
J = 2.0                                            # 转动惯量（示意值，单位已折算成标幺）
def load(w):                                       # 负载转矩：风机类，转得越快阻力越大
    return 0.1 + 0.75 * w ** 2                     # 静止时 0.1，额定转速附近约 0.8 倍额定转矩

def motor(conn):                                   # conn[k] = 0 断电、1 星形、2 三角形；返回线电流和转速
    w = 0.0; I = np.zeros_like(t); W = np.zeros_like(t)  # 从静止开始
    for k in range(len(t)):                        # 逐毫秒推演
        s = max(1 - w, 1e-4)                       # 转差率（避免除以 0）
        f = {0: 0.0, 1: 1 / 3, 2: 1.0}[conn[k]]    # 星形：线电流和转矩都是三角形的 1/3（推导见正文）
        I[k] = f * i_line(s) / I_N                 # 线电流（额定电流的倍数）
        Tm = f * torque(s) / T_N                   # 电动机转矩（额定转矩的倍数）
        w = max(w + (Tm - load(w)) / J * dt, 0.0)  # 牛顿第二定律：转矩差使转速变化
        W[k] = w                                   # 记录转速（同步转速的倍数）
    return I, W

# ---------- 控制回路状态机（写法同 18：先按上一刻的线圈状态更新衔铁，再按此刻的触点算线圈） ----------
names = ["KM", "KMY", "KMD"]                       # KMD 代表 KM△
arm = {n: np.zeros_like(t, dtype=bool) for n in names}   # 衔铁（主触点、辅助触点跟着它）
coil = {n: np.zeros_like(t, dtype=bool) for n in names}  # 线圈是否有电
cnt = {n: 0.0 for n in names}                      # 每只接触器"线圈与衔铁不一致"已经持续了多久
kt_coil = np.zeros_like(t, dtype=bool); kt_done = np.zeros_like(t, dtype=bool)  # KT 线圈、KT 延时是否已到
kt_cnt = 0.0                                       # KT 已经计了多久
for k in range(1, len(t)):                         # 逐毫秒推演
    for n in names:                                # 第一步：更新三只接触器的衔铁
        cnt[n] = cnt[n] + dt if coil[n][k - 1] != arm[n][k - 1] else 0.0  # 不一致就累加，一致就清零
        a = arm[n][k - 1]                          # 上一刻衔铁的位置
        arm[n][k] = (not a and cnt[n] >= T_PICK - 1e-9) or (a and cnt[n] < T_DROP - 1e-9)  # 够时间才动
    kt_cnt = kt_cnt + dt if kt_coil[k - 1] else 0.0  # KT：线圈有电就计时，断电立刻清零（通电延时型）
    kt_done[k] = kt_cnt >= T_SET - 1e-9            # 计满 T_SET：延时常闭断开、延时常开闭合
    node = (not sb1[k]) and (sb2[k] or arm["KM"][k])  # 公共点有没有电：停止没按，并且（启动按着或 KM 自锁）
    coil["KM"][k] = node                           # KM 线圈
    kt_coil[k] = node and not arm["KMD"][k]        # KT 线圈：KM△ 吸合后被它的常闭切断，KT 复位
    coil["KMY"][k] = node and not kt_done[k] and not arm["KMD"][k]  # KMY 线圈：KT 延时断开常闭 + KM△ 常闭互锁
    coil["KMD"][k] = node and (kt_done[k] or arm["KMD"][k]) and not arm["KMY"][k]  # KM△：KT 延时闭合或自锁，KMY 常闭互锁

conn = np.where(arm["KM"] & arm["KMY"] & ~arm["KMD"], 1, 0)   # KM 与 KMY 吸合：星形
conn = np.where(arm["KM"] & arm["KMD"] & ~arm["KMY"], 2, conn)  # KM 与 KM△ 吸合：三角形
short = arm["KMY"] & arm["KMD"]                    # KMY 与 KM△ 同时吸合 = 三相短路
assert not short.any()                             # 结论 1：互锁让 KMY、KM△ 永远不会同时吸合

dol = np.where(t >= 0.5 + T_PICK, 2, 0)            # 对照组：直接启动，0.5 s 按下后 KM 吸合就接成三角形
I_d, W_d = motor(dol)                              # 直接启动的电流和转速
I_y, W_y = motor(conn)                             # 星三角启动的电流和转速

def first(x):                                      # 某个布尔数组第一次为真的时刻
    return t[np.argmax(x)]
t_y_on = first(arm["KMY"]); t_y_off = first(~arm["KMY"] & (t > 1))   # KMY 吸合、释放的时刻
t_d_on = first(arm["KMD"]); t_kt_off = first(~kt_coil & (t > 1))    # KM△ 吸合、KT 线圈断电的时刻
print(f"[时序] KM、KMY 在 {first(arm['KM']):.3f} s 吸合（星形启动）；KT 在 {0.5 + T_SET:.3f} s 到时")  # 打印时序
print(f"[时序] KMY 在 {t_y_off:.3f} s 释放，KM△ 在 {t_d_on:.3f} s 吸合，中间空档 {(t_d_on - t_y_off) * 1e3:.0f} ms；KT 线圈在 {t_kt_off:.3f} s 断电复位")  # 打印切换
assert abs(t_d_on - t_y_off - T_PICK) < 1.5e-3     # 空档 = KM△ 的吸合时间（KMY 常闭复位后 KM△ 线圈才通电）

pk_d = I_d.max(); pk_y = I_y[t < 0.5 + T_SET].max()  # 直接启动峰值、星形阶段峰值
print(f"[电流] 直接启动峰值 {pk_d:.1f} 倍额定电流；星形启动峰值 {pk_y:.1f} 倍，是直接启动的 {pk_y / pk_d:.3f}")  # 1/3
assert abs(pk_y / pk_d - 1 / 3) < 0.01             # 结论 2：星形启动电流 = 直接启动的 1/3
k95 = np.argmax(W_d > 0.95 * W_d[-1])              # 直接启动转速到 95% 的时刻
print(f"[转速] 直接启动 {t[k95] - 0.5:.1f} s 转到最终转速的 95%；星三角在切换前转到同步转速的 {W_y[np.searchsorted(t, t_y_off)] * 100:.0f}%")  # 打印转速
k_sw = np.searchsorted(t, t_d_on)                  # 三角形接通的下标
pk_sw = I_y[k_sw:k_sw + 200].max()                 # 切换到三角形后的电流尖峰
print(f"[电流] 切换前 {I_y[np.searchsorted(t, t_y_off) - 1]:.2f} 倍；空档里 0；接成三角形瞬间 {pk_sw:.1f} 倍（稳态模型的示意值），最后稳定在 {I_y[-1]:.2f} 倍")  # 打印切换电流
assert pk_sw < pk_d and I_y[k_sw - 5] == 0         # 结论 3：切换尖峰比直接启动小；空档里电流为 0
ratio_sw = pk_sw / pk_d                             # 切换尖峰 ÷ 直接启动峰值（无残余电压的模型）
print(f"[电流] 切换尖峰 / 直接启动峰值 = {pk_sw:.1f} / {pk_d:.1f} = {ratio_sw:.2f}；西门子 24499345：℘ 理论最大 2，实测有利接法 0.8、不利接法 1.37")
assert abs(ratio_sw - 0.45) < 0.01 and ratio_sw < 0.8 < 1.37 < 2  # 模型值小于实测：因为模型里没有残余电压
assert abs(I_y[-1] - I_d[-1]) < 0.01               # 结论 4：最后两种启动方式的运行电流一样

fig, axs = plt.subplots(3, 1, figsize=(9.5, 6.0), sharex=True, gridspec_kw=dict(height_ratios=[1.1, 1.4, 1.0]))  # 三行
ax = axs[0]                                        # 第一行：接触器状态
ax.plot(t, arm["KM"] * 0.7 + 2.0, **fs.LS["vout"], label="KM 主接触器")     # KM 橙色
ax.plot(t, arm["KMY"] * 0.7 + 1.0, **fs.LS["vin"], label="KMY 星形接触器")   # KMY 蓝色
ax.plot(t, arm["KMD"] * 0.7 + 0.0, **fs.LS["fb"], label="KM△ 三角形接触器")  # KM△ 蓝绿色虚线
ax.set_yticks([0.35, 1.35, 2.35]); ax.set_yticklabels(["KM△", "KMY", "KM"]); ax.set_ylim(-0.3, 3.0)  # 纵轴
ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)      # 图例放到右侧
ax = axs[1]                                        # 第二行：线电流
ax.plot(t, I_d, **fs.LS["third"], label="直接启动（三角形）")              # 直接启动：红紫色点划线
ax.plot(t, I_y, **fs.LS["cur"], label="星三角启动")                       # 星三角：天蓝色
fs.mark(ax, t[np.argmax(I_d)], pk_d, "{:.1f}", "倍", dx=12, dy=-4)        # 标直接启动峰值
fs.mark(ax, t[np.argmax(I_y[t < 6])], pk_y, "{:.1f}", "倍", dx=12, dy=4)  # 标星形峰值
fs.mark(ax, t[k_sw + np.argmax(I_y[k_sw:k_sw + 200])], pk_sw, "{:.1f}", "倍", dx=10, dy=6)  # 标切换尖峰
fs.ref_h(ax, 1.0, "额定电流", x=0.99)                                      # 额定电流参考线
fs.axlabels(ax, None, None, "线电流 / 额定电流")                          # 纵轴
ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)      # 图例
ax = axs[2]                                        # 第三行：转速
ax.plot(t, W_d * 100, **fs.LS["third"], label="直接启动")                  # 直接启动转速
ax.plot(t, W_y * 100, **fs.LS["cur"], label="星三角启动")                  # 星三角转速
fs.ref_v(ax, t_d_on, "切换到三角形", y=0.3)                               # 切换时刻
fs.axlabels(ax, "时间", "s", "转速 / 同步转速", "%")                       # 坐标
ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)      # 图例
fs.save(fig, "19", "19_p2_4_sim.png")              # 保存

z = (t >= t_y_off - 0.03) & (t < t_d_on + 0.06)    # 放大切换前后约 0.1 s
tm = (t[z] - (0.5 + T_SET)) * 1e3                  # 横轴：从 KT 到时算起的毫秒数
fig, axs = plt.subplots(2, 1, figsize=(8.6, 4.4), sharex=True)  # 两行：状态、电流
ax = axs[0]                                        # 状态
ax.plot(tm, coil["KMY"][z] * 0.6 + 3.0, drawstyle="steps-post", **{**fs.LS["cur"], "alpha": 0.6}, label="KMY 线圈有电")  # KMY 线圈
ax.plot(tm, arm["KMY"][z] * 0.6 + 2.0, drawstyle="steps-post", **fs.LS["vin"], label="KMY 主触点闭合")   # KMY 主触点
ax.plot(tm, coil["KMD"][z] * 0.6 + 1.0, drawstyle="steps-post", **fs.LS["cur"], label="KM△ 线圈有电")    # KM△ 线圈
ax.plot(tm, arm["KMD"][z] * 0.6 + 0.0, drawstyle="steps-post", **fs.LS["fb"], label="KM△ 主触点闭合")    # KM△ 主触点
ax.set_yticks([0.3, 1.3, 2.3, 3.3]); ax.set_yticklabels(["KM△ 主", "KM△ 线圈", "KMY 主", "KMY 线圈"]); ax.set_ylim(-0.3, 4.0)  # 纵轴
ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)      # 图例
ax = axs[1]                                        # 电流
ax.plot(tm, I_y[z], drawstyle="steps-post", **fs.LS["cur"], label="星三角线电流")  # 电流
ax.axvspan((t_y_off - 0.5 - T_SET) * 1e3, (t_d_on - 0.5 - T_SET) * 1e3, color="0.85", lw=0, label="空档：两只都断开")  # 空档
fs.ref_v(axs[0], 0, "KT 到时", y=0.98)                                    # KT 到时的竖线
fs.ref_v(axs[1], (t_y_off - 0.5 - T_SET) * 1e3, "KMY 断开", y=0.98)        # KMY 主触点断开
fs.ref_v(axs[1], (t_d_on - 0.5 - T_SET) * 1e3, "KM△ 闭合", y=0.75)        # KM△ 主触点闭合
fs.axlabels(ax, "从 KT 到时起的时间", "ms", "线电流 / 额定电流", None)          # 坐标
ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)      # 图例
fs.save(fig, "19", "19_p2_5_switch.png")           # 保存
