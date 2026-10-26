# 07 三极管驱动继电器的最小仿真：A 部分扫基极电阻看三极管是否饱和；B 部分看线圈断电瞬间的电压尖峰。
# 电路：+5V → 继电器线圈（70 Ω）→ 三极管集电极；发射极接地；单片机引脚 → 基极电阻 R_B → 基极；线圈两端反并续流二极管。
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("code/figs").resolve()))  # 在仓库根目录运行
import numpy as np                                 # 数组运算
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、轴标签、保存函数

VCC = 5.0                                          # 线圈电源 5 V
R_COIL = 70.0                                      # 松乐 SRD-05VDC 高灵敏型线圈电阻 70 Ω（数据手册）
V_BE, V_SAT = 0.7, 0.2                             # 和 03 一致的简化模型：导通时 V_BE = 0.7 V，饱和时 V_CE = 0.2 V
PULL_IN = 0.75                                     # 吸合电压最大 75% 额定值（数据手册）：低于它不保证吸得上
I_MAX = (VCC - V_SAT) / R_COIL                     # 三极管完全导通（饱和）时线圈电流的上限
print(f"[A] 饱和时线圈电流 I_C(max) = {I_MAX*1e3:.1f} mA")  # 打印上限电流

def drive(v_pin, rb, beta):                        # 给定引脚电压、基极电阻、电流放大倍数，算三极管工作点
    ib = max(v_pin - V_BE, 0.0) / rb               # 基极电流：电阻两端电压 ÷ 电阻
    ic = min(beta * ib, I_MAX)                     # 放大区 I_C = β·I_B，但不可能超过线圈允许的最大值
    vce = VCC - ic * R_COIL                        # 集电极电压 = 电源 − 线圈上的压降
    sat = beta * ib >= I_MAX                       # β·I_B 够大（"想要的"电流超过上限）就进了饱和区
    if sat:                                        # 饱和时 V_CE 由饱和压降决定
        vce = V_SAT  # 饱和压降 0.2 V
    return ib, ic, vce, sat                        # 返回基极电流、集电极电流、V_CE、是否饱和

BETA_MIN = 30                                      # 2N3904 在 100 mA 时 h_FE 最小 30（数据手册），按最坏情况算
ib_need = I_MAX / BETA_MIN                         # 刚好饱和所需的最小基极电流
print(f"[A] 最小基极电流 I_C/β = {ib_need*1e3:.2f} mA，留 2 倍裕量 = {2*ib_need*1e3:.2f} mA，5 倍 = {5*ib_need*1e3:.2f} mA")  # 打印所需基极电流
print(f"[A] 5 V 引脚：R_B 在 {(5-V_BE)/(5*ib_need):.0f} Ω（5 倍）到 {(5-V_BE)/(2*ib_need):.0f} Ω（2 倍）之间")  # 由裕量反推基极电阻的范围
print(f"[A] 若 V_BE 按手册上限 0.95 V 算：680 Ω 给 {(5-0.95)/680*1e3:.2f} mA（{(5-0.95)/680/ib_need:.1f} 倍）")  # 换成更悲观的 V_BE 再检查一次
for v_pin, rb in [(5.0, 680), (3.3, 470)]:         # 两种单片机：5 V 引脚配 680 Ω，3.3 V 引脚配 470 Ω
    ib, ic, vce, sat = drive(v_pin, rb, BETA_MIN)  # 用最坏的 β 检查
    k = ib / ib_need                               # 实际基极电流是"刚好够"的几倍
    print(f"[A] 引脚 {v_pin} V、R_B = {rb} Ω：I_B = {ib*1e3:.2f} mA（裕量 {k:.1f} 倍），V_CE = {vce:.1f} V，饱和 = {sat}")  # 打印检查结果
    assert sat and 2 <= k <= 5                     # 关键结论：这两组取值在最坏 β 下也饱和，裕量落在 2 到 5 倍之间

print("[A] R_B = 10 kΩ（取大了）时：")  # 下面看基极电阻取大了的情况
for beta in (30, 100, 300):                        # 同一型号的三极管，β 可以差好几倍
    ib, ic, vce, sat = drive(5.0, 10e3, beta)      # 基极电阻取 10 kΩ
    v_coil = VCC - vce                             # 线圈两端实际拿到的电压
    p_q = vce * ic                                 # 三极管自己消耗的功率 = V_CE × I_C
    print(f"    β = {beta:3d}：I_C = {ic*1e3:5.1f} mA，V_CE = {vce:.2f} V，线圈 {v_coil/VCC*100:3.0f}% 额定，三极管 {p_q*1e3:4.1f} mW，饱和 = {sat}")  # 打印每种 β 的结果
    if beta == 100:                                # 关键结论：β = 100 时没饱和，线圈电压低于 75% 吸合门限
        assert (not sat) and v_coil / VCC < PULL_IN  # 不饱和，而且吸不上
ib, ic, vce, sat = drive(5.0, 680, BETA_MIN)       # 对照：正确取值时三极管的功耗
print(f"[A] 对照 R_B = 680 Ω：三极管 {vce*ic*1e3:.1f} mW，线圈 {(VCC-vce)/VCC*100:.0f}% 额定")  # 打印对照结果
print(f"[A] 半开（β = 100）的功耗是开到底的 {85.6/13.7:.1f} 倍")  # 两种状态的发热之比（数值取自上面两行）
print(f"[A] 放大区最坏功耗（V_CE = V_CC/2 时）= {VCC**2/(4*R_COIL)*1e3:.0f} mW")  # 放大区里三极管功耗最大的情况
v_scan = np.linspace(0, VCC, 501)                  # 验算：把 V_CE 从 0 扫到 V_CC，功耗 P = V_CE·(V_CC − V_CE)/R
p_scan = v_scan * (VCC - v_scan) / R_COIL          # 这是一条开口向下的抛物线
print(f"[A] 扫描验算：功耗最大在 V_CE = {v_scan[p_scan.argmax()]:.2f} V，为 {p_scan.max()*1e3:.0f} mW")  # 最高点在 V_CC/2
assert abs(v_scan[p_scan.argmax()] - VCC / 2) < 0.02 and abs(p_scan.max() - VCC**2 / (4 * R_COIL)) < 1e-4

# ---------------- B 部分：t = 0 时三极管关断，看集电极电压 ----------------
L = 0.1                                            # 线圈电感 0.1 H（示意值，SRD 数据手册没有给）
C_STRAY = 100e-12                                  # 集电极对地的杂散电容 100 pF（示意值）
I0 = I_MAX                                         # 关断前线圈电流 = 饱和电流
print(f"[B] 关断前线圈电流 {I0*1e3:.1f} mA，线圈储能 ½LI² = {0.5*L*I0**2*1e3:.3f} mJ，时间常数 L/R = {L/R_COIL*1e3:.2f} ms")  # 打印关断前的状态

dt = 1e-9                                          # 没有二极管时尖峰只有几微秒，步长要取 1 ns
t_a = np.arange(0, 9e-6, dt)                       # 仿真 9 μs（只看冲上去的那半个周期）
i, vc = I0, V_SAT                                  # 初值：线圈电流 I0，集电极电压 0.2 V
vc_a = np.empty_like(t_a)                          # 存集电极电压
for k in range(len(t_a)):                          # 线圈电流只能流进杂散电容，电容电压一路冲高
    vc_a[k] = vc                                   # 记下这一刻的集电极电压
    i += (VCC - vc - R_COIL * i) / L * dt          # 电感：L·di/dt = 线圈两端电压
    vc += i / C_STRAY * dt                         # 电容：C·dv/dt = 流进来的电流
peak = vc_a.max()                                  # 尖峰最高值
t_peak = t_a[vc_a.argmax()]                        # 尖峰出现的时刻
print(f"[B] 无二极管：集电极尖峰 {peak:.0f} V（t = {t_peak*1e6:.1f} μs），估算式 V_CC + I0·√(L/C) = {VCC + I0*np.sqrt(L/C_STRAY):.0f} V")  # 打印尖峰和估算值
assert peak > 1000                                 # 关键结论：尖峰上千伏，远超 2N3904 的 40 V 耐压

dt2 = 1e-6                                         # 有二极管时电流按毫秒衰减，步长 1 μs 足够
t_b = np.arange(0, 4e-3, dt2)                      # 仿真 4 ms
V_F, V_Z = 0.7, 24.0                               # 二极管正向压降 0.7 V；稳压管 24 V
def clamp_run(v_clamp):                            # 有钳位时：集电极电压被钳在 V_CC + 钳位电压，线圈电流自己衰减
    i = I0                                         # 初值
    out = np.empty_like(t_b)                       # 存线圈电流
    for k in range(len(t_b)):                      # 逐步推
        out[k] = i                                 # 记下电流
        i += (-v_clamp - R_COIL * i) / L * dt2     # 线圈两端被反向钳位：L·di/dt = −钳位电压 − R·i
        i = max(i, 0.0)                            # 二极管不让电流反向，到 0 就停
    return out                                     # 返回电流曲线
i_d = clamp_run(V_F)                               # 只有续流二极管
i_z = clamp_run(V_F + V_Z)                         # 二极管串 24 V 稳压管
I_REL = 0.1 * VCC / R_COIL                         # 释放电压最小 10%：电流低于额定值的 10% 时一定释放
t_d = t_b[np.argmax(i_d < I_REL)]                  # 只有二极管：电流掉到释放值的时刻
t_z = t_b[np.argmax(i_z < I_REL)]                  # 加稳压管：电流掉到释放值的时刻
print(f"[B] 只有二极管：集电极钳在 {VCC+V_F:.1f} V，电流降到 {I_REL*1e3:.2f} mA 用 {t_d*1e3:.2f} ms")  # 打印二极管方案
print(f"[B] 二极管 + 24 V 稳压管：集电极钳在 {VCC+V_F+V_Z:.1f} V，用 {t_z*1e3:.2f} ms（快 {t_d/t_z:.1f} 倍）")  # 打印稳压管方案
assert VCC + V_F + V_Z < 40 and t_d / t_z > 5      # 关键结论：稳压管方案仍低于 40 V 耐压，而且释放快 5 倍以上
tau = L / R_COIL                                   # 时间常数
t_pure = tau * np.log(I0 / I_REL)                  # 若不计二极管压降：纯 RL 指数衰减的时间
t_form = tau * np.log((I0 + V_F / R_COIL) / (I_REL + V_F / R_COIL))  # 计入 V_F：i = (I0 + V_F/R)·e^(−t/τ) − V_F/R
print(f"[B] 公式验算：不计 V_F 要 {t_pure*1e3:.2f} ms；计入 V_F 为 {t_form*1e3:.2f} ms，和仿真的 {t_d*1e3:.2f} ms 一致")  # 二极管压降让电流掉得更快
assert abs(t_form - t_d) < 2e-5 and t_pure > t_d

fig, ax = plt.subplots(figsize=fs.SIZE["single"])  # 图 07-p2-2：无二极管时的尖峰
ax.plot(t_a * 1e6, vc_a, **{**fs.LS["bad"], "markevery": 1000}, label="集电极电压（无二极管）")  # 朱红色×：无二极管的集电极电压
fs.ref_h(ax, 40, "2N3904 耐压 40 V", x=0.30)       # 耐压参考线（几乎贴着 0，可见尖峰比它高多少）
fs.mark(ax, t_peak * 1e6, peak, "{:.0f}", " V", dx=6, dy=-14)   # 标出尖峰值（同时打印）
fs.axlabels(ax, "关断后时间", "μs", "集电极电压", "V")  # 坐标轴标签
ax.legend(loc="lower right")  # 图例
fs.save(fig, "07", "07_p2_2_nodiode.png")  # 保存图片

fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])  # 图 07-p2-3：二极管 vs 二极管 + 稳压管
a1.plot(t_b * 1e3, i_d * 1e3, **fs.LS["cur"], label="只有二极管")  # 天蓝色：只有二极管时的线圈电流
a1.plot(t_b * 1e3, i_z * 1e3, **fs.LS["third"], label="二极管 + 24 V 稳压管")  # 红紫色点划线：加稳压管时的线圈电流
fs.ref_h(a1, I_REL * 1e3, "释放电流 10%", x=0.98)  # 灰色点线：释放电流
fs.ref_v(a1, t_d * 1e3, f"{t_d*1e3:.2f} ms")  # 二极管方案的释放时刻
fs.ref_v(a1, t_z * 1e3)                            # 稳压管方案的释放时刻
a1.annotate(f"{t_z*1e3:.2f} ms", (t_z * 1e3, 30), (0.55, 30), fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))  # 给稳压管方案的时刻加一个箭头标注
fs.axlabels(a1, "关断后时间", "ms", "线圈电流", "mA")  # 坐标轴标签
a1.legend(loc="center right", fontsize=8)  # 图例
vd = np.where(i_d > 0, VCC + V_F, VCC)             # 电流衰减完以后集电极回到 V_CC
vz = np.where(i_z > 0, VCC + V_F + V_Z, VCC)  # 稳压管方案的集电极电压
a2.plot(t_b * 1e3, vd, **fs.LS["cur"], label="只有二极管")  # 天蓝色：只有二极管
a2.plot(t_b * 1e3, vz, **fs.LS["third"], label="二极管 + 24 V 稳压管")  # 红紫色点划线：加稳压管
fs.ref_h(a2, 40, "耐压 40 V", x=0.98)  # 耐压参考线
fs.axlabels(a2, "关断后时间", "ms", "集电极电压", "V")  # 坐标轴标签
a2.set_ylim(0, 45)  # 纵轴范围
a2.legend(loc="center right", fontsize=8)  # 图例
fs.save(fig, "07", "07_p2_3_clamp.png")  # 保存图片

# ---------------- 例题与练习用到的数字（正文里引用的都从这里打印） ----------------
r_std = 55.0                                       # 例 3：SRD-05VDC 标准型线圈 55 Ω
ic3 = (VCC - V_SAT) / r_std                        # 饱和时线圈电流
ib3 = (5.0 - V_BE) / 560                           # 选 560 Ω 时的基极电流
print(f"[例 3] 55 Ω 线圈：I_C = {ic3*1e3:.1f} mA，I_C/30 = {ic3/30*1e3:.2f} mA，560 Ω 给 {ib3*1e3:.2f} mA（{ib3/(ic3/30):.1f} 倍）")  # 打印例 3
assert 2 <= ib3 / (ic3 / 30) <= 5                  # 裕量在 2 到 5 倍之间
print(f"[例 2] 3.3 V 引脚若仍用 680 Ω：I_B = {(3.3-V_BE)/680*1e3:.2f} mA")  # 例 2 答案里的对照
print(f"[例 3] 55 Ω 线圈仍用 680 Ω：裕量只有 {(5.0-V_BE)/680/(ic3/30):.1f} 倍")  # 例 3：旧电阻够不够
print(f"[参数表] 手册：55 Ω、89.3 mA；5 V ÷ 55 Ω = {5/55*1e3:.1f} mA，5 V ÷ 89.3 mA = {5/0.0893:.1f} Ω（手册取整差异）")  # 参数表的注

ic_e1 = (12.0 - V_SAT) / 400                       # 练习 2：SRD-12VDC 高灵敏型 400 Ω，3.3 V 单片机，β 最小按 60
ib_e1 = (3.3 - V_BE) / 1500                        # 选 1.5 kΩ
print(f"[练习 2] 12 V / 400 Ω：I_C = {ic_e1*1e3:.1f} mA，I_C/60 = {ic_e1/60*1e3:.2f} mA，1.5 kΩ 给 {ib_e1*1e3:.2f} mA（{ib_e1/(ic_e1/60):.1f} 倍）")  # 打印练习 2
assert 2 <= ib_e1 / (ic_e1 / 60) <= 5              # 裕量在 2 到 5 倍之间

vce_m = 1.99                                       # 练习 3：实测 V_CE = 1.99 V，R_B = 10 kΩ
ic_m = (VCC - vce_m) / R_COIL                      # 由线圈压降反推集电极电流
ib_m = (5.0 - V_BE) / 10e3                         # 基极电流
print(f"[练习 3] I_C = {ic_m*1e3:.1f} mA，I_B = {ib_m*1e3:.2f} mA，β ≈ {ic_m/ib_m:.0f}，线圈 {(VCC-vce_m)/VCC*100:.0f}%")  # 打印练习 3
print(f"[练习 3] 线圈压降 {VCC-vce_m:.2f} V")  # 线圈两端的电压

for vs, vsat in [(5.0, 0.9), (5.0, 1.1), (12.0, 1.1)]:  # 练习 5：ULN2003 的 V_CE(sat) 典型 0.9 V、最大 1.1 V（100 mA 时）
    print(f"[练习 5] {vs:.0f} V 继电器、V_CE(sat) = {vsat} V：线圈拿到 {vs-vsat:.1f} V = {(vs-vsat)/vs*100:.0f}% 额定")  # 打印练习 5
print(f"[练习 5] ULN2003 比单只三极管多压降 {0.9-V_SAT:.1f} V（典型）到 {1.1-V_SAT:.1f} V（最大）")  # 和 0.2 V 的饱和压降比

vz_max = 40.0 - 12.0 - V_F                         # 练习 4：12 V 线圈 + 2N3904（40 V），钳位 12 + V_F + V_Z 必须低于 40 V
print(f"[练习 4] 12 V 继电器：V_Z < 40 − 12 − {V_F} = {vz_max:.1f} V；取 24 V 时钳在 {12+V_F+24:.1f} V，留 {40-(12+V_F+24):.1f} V 余量")  # 打印练习 4
assert vz_max > 24 and 12 + V_F + 24 < 40
