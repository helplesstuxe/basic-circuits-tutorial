"""08 线性稳压：静态与时域计算，生成 08-linear-regulator/img/ 里的曲线图。
运行：/workspace/circuits-venv/bin/python code/08_sim.py
电路（见 08 page2）：稳压管基准（10 的 1N4733A 模型：V = V_Z + r_Z·(I_Z − I_ZT)，即 V = V_Z0 + r_Z·I_Z，V_Z0 ≈ 4.757 V；经 R_Z = 1 kΩ 从 V_i 供电）
→ 运放 LM358 接成同相放大（02 的公式，R_1 = 5.1 kΩ，R_f = 3.9 kΩ），输出推动 TIP31 射极跟随器（07 的指数模型）。
示意假设：运放开环增益 A = 1e5；运放输出最高到 V_i − 1.5 V（与 07 的估算相同）；β = 50；I_S = 1e-13 A。
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "08"
VZ, IZT, RZ_DYN, R_Z = 5.1, 0.049, 7.0, 1000.0   # 1N4733A（见 10 page2）：49 mA 时 5.1 V；限流电阻 1 kΩ
VZ0 = VZ - RZ_DYN * IZT                  # 击穿起点 ≈ 4.757 V
R1, RF = 5100.0, 3900.0                   # 同相放大：倍数 1 + RF/R1
A_OL = 1e5                                # 运放开环增益（示意值）
HEAD = 1.5                                # 运放输出最高 = V_i − 1.5 V（同 07）
VT, IS, BETA = 0.02585, 1e-13, 50.0       # 三极管模型（同 07）
I_OP = 0.020                              # LM358 最小拉电流 20 mA（见 07 page1）
K = R1 / (R1 + RF)                        # 分压比


def vref(vi):
    """稳压管基准：I_Z = (V_i − V_Z0)/(R_Z + r_Z)，V_ref = V_Z0 + r_Z·I_Z。"""
    iz = max(vi - VZ0, 0.0) / (R_Z + RZ_DYN)
    return VZ0 + RZ_DYN * iz, iz


def vbe(il):
    ic = il * BETA / (BETA + 1) + 1e-9
    return VT * np.log(ic / IS + 1)


def reg(vi, il):
    """返回 (V_o, 是否在稳压, V_BE)。il 为负载电流（不含分压电阻电流）。"""
    vr, _ = vref(vi)
    ie = il                                # 先忽略分压电阻的约 1 mA，循环里补上
    for _ in range(3):
        vb_ = vbe(ie)
        vo_set = (A_OL * vr - vb_) / (1 + A_OL * K)   # 闭环：V_B = A(V_ref − K·V_o)，V_o = V_B − V_BE
        vo_max = vi - HEAD - vb_
        vo = min(vo_set, vo_max)
        ie = il + vo / (R1 + RF)
    return vo, vo_set <= vo_max, vb_


def ripple_in(t, avg, pp, f=100.0, t_rise=2.4e-3):
    """锯齿状纹波（形状同 06 page2、10 page1）。"""
    ph = np.mod(t, 1 / f)
    lo, hi = avg - pp / 2, avg + pp / 2
    return np.where(ph < t_rise, lo + (hi - lo) * ph / t_rise, hi - (hi - lo) * (ph - t_rise) / (1 / f - t_rise))


IL = 0.5
vr14, iz14 = vref(14.0)
vo14, ok14, vbe14 = reg(14.0, IL)
ideal = vr14 * (1 + RF / R1)
drop = HEAD + vbe14
print(f"[数值] V_i = 14 V：I_Z = {iz14*1e3:.1f} mA，V_ref = {vr14:.3f} V，理想 V_o = V_ref·(1 + R_f/R_1) = {ideal:.3f} V，仿真 V_o = {vo14:.3f} V")
print(f"[数值] I_L = 0.5 A：V_BE = {vbe14:.3f} V，I_B = {IL/(BETA+1)*1e3:.1f} mA（< 20 mA），运放输出 = {vo14+vbe14:.2f} V")
print(f"[数值] 压差 = 1.5 V + V_BE = {drop:.3f} V，最低输入 = {vo14+drop:.2f} V")
assert abs(vo14 - ideal) < 1e-3 and ok14
assert IL / (BETA + 1) < I_OP

# ---------- 图 08-p1-2 带纹波的输入 vs 稳定的输出 ----------
t = np.arange(0, 0.03, 20e-6)
vi_t = ripple_in(t, 14.0, 2.0)
vo_t = np.array([reg(v, IL)[0] for v in vi_t])
rin, rout = vi_t.max() - vi_t.min(), vo_t.max() - vo_t.min()
rr_db = 20 * np.log10(rin / rout)
pred = rin * RZ_DYN / (R_Z + RZ_DYN) * (1 + RF / R1)
print(f"[纹波] 输入 {vi_t.min():.1f}~{vi_t.max():.1f} V（峰峰 {rin:.2f} V）→ 输出 {vo_t.mean():.3f} V，纹波 {rout*1e3:.1f} mV（公式 {pred*1e3:.1f} mV），抑制 {rr_db:.0f} dB")
assert abs(rout - pred) < 1e-3 and rr_db > 35
fig, (a1, a2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
a1.plot(t * 1e3, vi_t, **fs.LS["vin"], label="输入 $V_i$：平均 14 V，纹波 2 V（峰峰）")
a1.plot(t * 1e3, vo_t, **fs.LS["vout"], label="输出 $V_o$")
fs.axlabels(a1, None, None, "电压", "V"); a1.set_ylim(0, 17)
a1.legend(loc="lower right", fontsize=8)
VOFF = np.floor(vo_t.mean() * 10) / 10          # 放大看时减掉的整数部分
a2.plot(t * 1e3, (vo_t - VOFF) * 1e3, **fs.LS["vout"], label=f"输出 $V_o$ 放大看：纹波 {rout*1e3:.1f} mV")
lo_mv = np.floor((vo_t.min() - VOFF) * 1e3 / 10) * 10 - 10
fs.axlabels(a2, "时间", "ms", f"输出 − {VOFF:.1f} V", "mV"); a2.set_ylim(lo_mv, lo_mv + 60)
a2.legend(loc="upper right", fontsize=8)
a2.set_title(f"输出平均 {vo_t.mean():.3f} V（纵轴放大：只显示 {VOFF + lo_mv/1e3:.2f}–{VOFF + (lo_mv+60)/1e3:.2f} V）", fontsize=9, loc="left")
print(f"[数值] 纵轴 {VOFF + lo_mv/1e3:.2f}–{VOFF + (lo_mv+60)/1e3:.2f} V")
fs.save(fig, N, "08_p1_2_ripple.png")

# ---------- 图 08-p1-3 功率去哪了（V_i = 14 V，0.5 A）----------
p_in = 14.0 * (IL + iz14 + vo14 / (R1 + RF))
p_load = vo14 * IL
p_pass = (14.0 - vo14) * (IL + vo14 / (R1 + RF))
p_other = p_in - p_load - p_pass
eta = p_load / p_in
print(f"[功率] 输入 {p_in:.2f} W = 负载 {p_load:.2f} W + 调整管 {p_pass:.2f} W + 基准与分压 {p_other:.2f} W；效率 {eta*100:.0f}%")
assert 2.0 < p_pass < 3.0 and 0.55 < eta < 0.7
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
names = ["从输入拿走", "负载得到", "调整管发热", "基准与分压"]
vals = [p_in, p_load, p_pass, p_other]
cols = [fs.C["vin"], fs.C["vout"], fs.C["bad"], fs.C["ref"]]
bars = ax.bar(names, vals, color=cols)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.1, f"{v:.2f} W", ha="center", fontsize=9)
fs.axlabels(ax, None, None, "功率", "W"); ax.set_ylim(0, 8.5)
print("[数值] 柱高 " + "、".join(f"{v:.2f} W" for v in vals))
fs.save(fig, N, "08_p1_3_power.png")

# ---------- 图 08-p2-2 输入扫描：压差以下失去稳压 ----------
vis = np.linspace(6, 16, 501)
cur = {0.5: [], 0.05: []}
for il_ in cur:
    cur[il_] = np.array([reg(v, il_)[0] for v in vis])
vmin05 = vo14 + drop
vo_005, _, vbe005 = reg(14.0, 0.05)
vmin005 = vo_005 + HEAD + vbe005
o10 = reg(10.0, 0.5)[0]
print(f"[扫描] 0.5 A：最低输入 {vmin05:.2f} V；0.05 A：V_BE {vbe005:.3f} V，最低输入 {vmin005:.2f} V")
print(f"[扫描] V_i = 10 V、0.5 A：输出只有 {o10:.2f} V（= 10 − {drop:.2f}）")
assert vmin005 < vmin05 and abs(o10 - (10 - drop)) < 0.01
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(vis, vis, **fs.LS["vin"], label="输入 $V_i$ 本身")
ax.plot(vis, cur[0.5], **fs.LS["vout"], label="输出 $V_o$（负载 0.5 A）")
ax.plot(vis, cur[0.05], **fs.LS["third"], label="输出 $V_o$（负载 0.05 A）")
fs.ref_v(ax, vmin05, f"{vmin05:.2f} V", y=0.62)
fs.mark(ax, 10.0, o10, "{:.2f}", " V", dx=6, dy=-14)
fs.mark(ax, 14.0, vo14, "{:.2f}", " V", dx=-10, dy=-16)
ax.axvspan(6, vmin05, color="0.9", zorder=0)
ax.text(8.2, 13.5, "压差不够：\n输出跟着输入走", ha="center", fontsize=9, color="0.3")
fs.axlabels(ax, "输入 $V_i$", "V", "电压", "V"); ax.set_ylim(0, 16.5)
ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "08_p2_2_dropout.png")

# ---------- 图 08-p3-1 调整管功耗与效率随输入变化 ----------
vis2 = np.linspace(11.5, 20, 200)
pc = (vis2 - vo14) * IL
eff = vo14 * IL / (vis2 * (IL + np.array([vref(v)[1] for v in vis2]) + vo14 / (R1 + RF)))
# 市电偏高 10%：二极管压降（桥式两只约 1.4 V）不跟着涨。原峰值 15 V → 变压器峰值 16.4 V → ×1.1 → 减 1.4 V
vpk_hi = (14.0 + 1.0 + 1.4) * 1.1 - 1.4
v_hi = vpk_hi - 1.0                                    # 纹波仍按 2 V（峰峰）算，平均 = 峰值 − 1 V
print(f"[散热] 市电 +10%：整流峰值 {vpk_hi:.2f} V，平均约 {v_hi:.2f} V（若直接 14 × 1.1 = {14*1.1:.1f} V）")
assert abs(v_hi - 15.6) < 0.1
p156 = (15.6 - vo14) * IL
print(f"[散热] V_i = 14 V：P_C ≈ {(14-vo14)*IL:.2f} W；V_i = 15.6 V（市电 +10%）：P_C ≈ {p156:.2f} W；V_i = 20 V：{(20-vo14)*IL:.2f} W，效率 {eff[-1]*100:.0f}%")
for p in ((14 - vo14) * IL, p156):
    print(f"[散热] P = {p:.2f} W：不加散热片温升 {p*62.5:.0f} °C；总热阻需 ≤ {(150-40)/p:.1f} °C/W，减去结到管壳 3.1 °C/W，散热片 ≤ {(150-40)/p-3.125:.1f} °C/W")
assert (14 - vo14) * IL > 2.0                           # 超过 TIP31 不加散热片的 2 W
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(vis2, pc, **fs.LS["bad"], label="调整管功耗 $P_C$（左轴）")
fs.ref_h(ax, 2.0, "TIP31 不加散热片 2 W", x=0.98, ha="right")
fs.mark(ax, 14.0, (14 - vo14) * IL, "{:.2f}", " W", dx=6, dy=-14)
fs.mark(ax, 15.6, p156, "{:.2f}", " W", dx=4, dy=12)
fs.axlabels(ax, "输入 $V_i$", "V", "功耗", "W"); ax.set_ylim(0, 6)
ax2 = ax.twinx()
ax2.plot(vis2, eff * 100, **fs.LS["third"], label="效率（右轴）")
ax2.set_ylabel("效率 (%)"); ax2.set_ylim(0, 100)
e14 = vo14 * IL / (14 * (IL + iz14 + vo14 / (R1 + RF)))
fs.mark(ax2, 14.0, e14 * 100, "{:.0f}", " %", dx=6, dy=6)
fs.mark(ax2, 20.0, eff[-1] * 100, "{:.0f}", " %", dx=-30, dy=8)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper center", fontsize=8)
assert eff[-1] < 0.5 and e14 > 0.55
fs.save(fig, N, "08_p3_1_heat.png")

# ---------- 图 08-p3-2 压差不够：纹波谷底掉到门槛以下（平均 11.5 V）----------
vi_lo = ripple_in(t, 11.5, 2.0)
vo_lo = np.array([reg(v, IL)[0] for v in vi_lo])
dip = vo_lo.max() - vo_lo.min()
print(f"[压差] 输入平均 11.5 V、纹波 2 V：谷底 {vi_lo.min():.1f} V < {vmin05:.2f} V，输出最低 {vo_lo.min():.2f} V，纹波 {dip*1e3:.0f} mV（正常时 {rout*1e3:.1f} mV）")
assert dip > 5 * rout
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi_lo, **fs.LS["vin"], label="输入：平均 11.5 V，纹波 2 V")
ax.plot(t * 1e3, vo_lo, **fs.LS["vout"], label="输出 $V_o$")
ax.plot(t * 1e3, vi_lo - drop, **fs.LS["third"], label=f"输入 − {drop:.2f} V")
ax.axhline(vmin05, **fs.LS["ref"], label=f"最低输入 {vmin05:.2f} V")
k = np.argmin(vo_lo)
fs.mark(ax, t[k] * 1e3, vo_lo[k], "{:.2f}", " V", dx=6, dy=-14)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(6.5, 15)
ax.legend(loc="upper right", fontsize=8, ncol=2)
fs.save(fig, N, "08_p3_2_low_headroom.png")
print("08_sim OK")
