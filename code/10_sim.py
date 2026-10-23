"""10 稳压管稳压：静态与时域计算，生成 10-zener-regulator/img/ 里的曲线图。
运行：/workspace/circuits-venv/bin/python code/10_sim.py
稳压管模型与 P2 page2 相同：反向电压没到 V_Z 时不导电；到了以后 V = V_Z + r_Z·I_Z（1N4733A：V_Z = 5.1 V，r_Z = 7 Ω）。
这个折线模型没有画出拐点附近「变软」的部分（见 P2 page2），所以 I_Z 很小时的结果偏乐观。
三极管（变体）用 P2 的估算规则：V_BE = 0.7 V，I_C = β·I_B，β 取 60（假设值，按 P2 page3 里 2N3904 的最小 β）。
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "10"
VZ, RZ = 5.1, 7.0            # 1N4733A（P2 page2）
PZ_MAX = 1.3                 # 额定功率 1.3 W
R = 180.0                    # 主例的限流电阻
VIN_MIN, VIN_NOM, VIN_MAX = 10.0, 12.0, 14.0
IL_MAX = 0.020               # 负载最大 20 mA
IZ_MIN = 0.005               # 设计要求稳压管至少 5 mA
VBE, BETA = 0.7, 60


def node(vin, r, il=0.0, rl=np.inf):
    """限流电阻 r 从 vin 供电，节点上并联稳压管、电阻负载 rl 和恒流负载 il。返回 (V_o, I_Z)。"""
    g = 1 / r + (0 if np.isinf(rl) else 1 / rl)
    v_off = (vin / r - il) / g                       # 稳压管不导通时的节点电压
    if v_off <= VZ:
        return max(v_off, 0.0), 0.0
    v = (vin / r + VZ / RZ - il) / (g + 1 / RZ)      # 稳压管导通
    return v, (v - VZ) / RZ


def follower(vin, r, il):
    """稳压管 + 射极跟随器：限流电阻 r 供给稳压管和基极电流 I_B = I_L/(β+1)。返回 (V_o, I_Z)。"""
    vb, iz = node(vin, r, il=il / (BETA + 1))
    return max(vb - VBE, 0.0), iz


# ---------- 图 10-p1-2 输入从 0 涨到 15 V：有 / 没有稳压管 ----------
RL = VZ / IL_MAX                                      # 255 Ω：5.1 V 时正好 20 mA
vin = np.linspace(0, 15, 601)
vo = np.array([node(v, R, rl=RL)[0] for v in vin])
vdiv = vin * RL / (R + RL)
v10, v14 = node(VIN_MIN, R, rl=RL)[0], node(VIN_MAX, R, rl=RL)[0]
von = VZ * (R + RL) / RL
print(f"[数值] R = {R:.0f} Ω、R_L = {RL:.0f} Ω：输入超过 {von:.2f} V 稳压管开始导通")
print(f"[数值] 输入 10 V → 输出 {v10:.3f} V；输入 14 V → 输出 {v14:.3f} V；输入变 4 V，输出只变 {(v14-v10)*1e3:.0f} mV")
print(f"[数值] 没有稳压管：输入 10 V → {10*RL/(R+RL):.2f} V，14 V → {14*RL/(R+RL):.2f} V")
assert (v14 - v10) < 0.2 and 14 * RL / (R + RL) - 10 * RL / (R + RL) > 2
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(vin, vdiv, **fs.LS["bad"], label="只有电阻分压（不接稳压管）")
ax.plot(vin, vo, **fs.LS["vout"], label="接上稳压管的输出 $V_o$")
ax.axvspan(VIN_MIN, VIN_MAX, color="0.9", zorder=0)
ax.text((VIN_MIN + VIN_MAX) / 2, 0.4, "输入的变化范围", ha="center", fontsize=9, color="0.3")
fs.ref_h(ax, VZ, "$V_Z$ = 5.1 V", x=0.02, ha="left")
fs.mark(ax, VIN_MIN, v10, fmt="{:.2f}", unit=" V", dx=4, dy=-14)
fs.mark(ax, VIN_MAX, v14, fmt="{:.2f}", unit=" V", dx=4, dy=-14)
fs.axlabels(ax, "输入 $V_i$", "V", "输出", "V")
ax.set_ylim(0, 9.5)
ax.legend(loc="upper left", fontsize=8)
fs.save(fig, N, "10_p1_2_line.png")


# ---------- 输入带纹波（模拟 06 的整流滤波输出）----------
def ripple_in(t, avg, pp, f=100.0, t_rise=2.4e-3):
    """锯齿状纹波：每 10 ms 里先用 t_rise 充上去，再直线放电下来（形状同 06 page2）。"""
    ph = np.mod(t, 1 / f)
    up = ph < t_rise
    lo, hi = avg - pp / 2, avg + pp / 2
    return np.where(up, lo + (hi - lo) * ph / t_rise, hi - (hi - lo) * (ph - t_rise) / (1 / f - t_rise))


t = np.arange(0, 0.03, 20e-6)
vi_t = ripple_in(t, VIN_NOM, 1.0)
vo_t = np.array([node(v, R, rl=RL)[0] for v in vi_t])
rip_in, rip_out = vi_t.max() - vi_t.min(), vo_t.max() - vo_t.min()
rp = RZ * RL / (RZ + RL)
print(f"[数值] 输入纹波 {rip_in:.2f} V → 输出纹波 {rip_out*1e3:.1f} mV（公式 r_Z∥R_L ÷ (R + r_Z∥R_L) = {rp/(R+rp):.4f}，× 1 V = {rp/(R+rp)*1e3:.1f} mV）")
assert abs(rip_out - rp / (R + rp)) < 1e-3
fig, (a1, a2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
a1.plot(t * 1e3, vi_t, **fs.LS["vin"], label="输入：12 V，纹波 1 V（峰峰）")
fs.axlabels(a1, None, None, "输入", "V")
a1.set_ylim(11, 13)
a1.legend(loc="upper right", fontsize=8)
a2.plot(t * 1e3, vo_t * 1e3 - 5000, **fs.LS["vout"], label=f"输出 $V_o$：纹波 {rip_out*1e3:.1f} mV")
fs.axlabels(a2, "时间", "ms", "输出 − 5 V", "mV")
lo_mv = np.floor(vo_t.min() * 1e3 / 10) * 10 - 20
hi_mv = lo_mv + 80
a2.set_ylim(lo_mv - 5000, hi_mv - 5000)
a2.legend(loc="upper right", fontsize=8)
a2.set_title(f"输出平均 {vo_t.mean():.3f} V（纵轴放大：只显示 {lo_mv/1e3:.2f}–{hi_mv/1e3:.2f} V）", fontsize=9, loc="left")
print(f"[数值] 输出平均 {vo_t.mean():.3f} V，纵轴 {lo_mv/1e3:.2f}–{hi_mv/1e3:.2f} V")
fs.save(fig, N, "10_p1_3_ripple.png")

# ---------- 图 10-p2-1 负载电流变化：电流在稳压管和负载之间「搬家」 ----------
il = np.linspace(0, 0.040, 401)
res = np.array([node(VIN_MIN, R, il=x) for x in il])
vo_l, iz_l = res[:, 0], res[:, 1]
ir_l = (VIN_MIN - vo_l) / R
i_lost = il[np.argmax(iz_l <= 0)]
print(f"[数值] 输入 10 V、R = 180 Ω：空载 I_Z = {iz_l[0]*1e3:.1f} mA；负载 20 mA 时 I_Z = {np.interp(0.02, il, iz_l)*1e3:.1f} mA、V_o = {np.interp(0.02, il, vo_l):.3f} V")
print(f"[数值] 负载超过 {i_lost*1e3:.1f} mA 时稳压管电流降到 0，失去稳压；负载 40 mA 时 V_o = {vo_l[-1]:.2f} V")
print(f"[数值] 0–20 mA 之间限流电阻电流从 {ir_l[0]*1e3:.1f} mA 变到 {np.interp(0.02, il, ir_l)*1e3:.1f} mA")
assert 26e-3 < i_lost < 28e-3 and np.interp(0.02, il, iz_l) > IZ_MIN
fig, (a1, a2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
a1.plot(il * 1e3, vo_l, **fs.LS["vout"], label="输出 $V_o$")
fs.ref_v(a1, i_lost * 1e3, f"{i_lost*1e3:.1f} mA", y=0.3)
fs.ref_h(a1, VZ, "$V_Z$", x=0.02, ha="left")
fs.axlabels(a1, None, None, "输出", "V")
a1.set_ylim(3, 6)
a1.legend(loc="lower left", fontsize=8)
a2.plot(il * 1e3, ir_l * 1e3, **fs.LS["vin"], label="限流电阻电流 $I_R$")
a2.plot(il * 1e3, iz_l * 1e3, **fs.LS["cur"], label="稳压管电流 $I_Z$")
a2.plot(il * 1e3, il * 1e3, **fs.LS["third"], label="负载电流 $I_L$")
fs.ref_v(a2, i_lost * 1e3)
fs.ref_h(a2, IZ_MIN * 1e3, "5 mA", x=0.02, ha="left")
fs.axlabels(a2, "负载电流 $I_L$", "mA", "电流", "mA")
a2.set_ylim(-2, 50)
a2.legend(loc="upper left", fontsize=8, ncol=3)
fs.save(fig, N, "10_p2_1_load.png")

# ---------- 图 10-p2-3 变体：加射极跟随器扩流 ----------
il2 = np.linspace(0, 0.100, 401)
plain = np.array([node(VIN_MIN, R, il=x)[0] for x in il2])
fol = np.array([follower(VIN_MIN, R, x) for x in il2])
vf0, vf100 = fol[0, 0], fol[-1, 0]
print(f"[数值] 跟随器：空载 V_o = {vf0:.3f} V，100 mA 时 {vf100:.3f} V（只降 {(vf0-vf100)*1e3:.1f} mV），稳压管电流 {fol[0,1]*1e3:.1f} → {fol[-1,1]*1e3:.1f} mA")
print(f"[数值] 100 mA 时基极电流 {0.1/(BETA+1)*1e3:.2f} mA；只用稳压管时 100 mA 输出 {plain[-1]:.2f} V")
p_q = (VIN_NOM - vf100) * 0.1
print(f"[数值] 输入 12 V、100 mA 时三极管功耗 ({VIN_NOM:.0f} − {vf100:.2f}) × 0.1 A = {p_q:.2f} W")
assert vf0 - vf100 < 0.02 and fol[-1, 1] > IZ_MIN
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(il2 * 1e3, plain, **fs.LS["bad"], label="只用稳压管（R = 180 Ω）")
ax.plot(il2 * 1e3, fol[:, 0], **fs.LS["vout"], label="稳压管 + 射极跟随器")
fs.ref_h(ax, VZ - VBE)
ax.text(98, VZ - VBE - 0.12, "参考线：$V_Z$ − 0.7 V = 4.4 V", ha="right", va="top", fontsize=9, color="0.3")
fs.mark(ax, 100, vf100, fmt="{:.3f}", unit=" V", dx=-40, dy=8)
fs.axlabels(ax, "负载电流 $I_L$", "mA", "输出", "V")
ax.set_ylim(0, 6)
ax.legend(loc="lower left", fontsize=8)
fs.save(fig, N, "10_p2_3_follower.png")

# ---------- 图 10-p3-1 限流电阻的取值窗口 ----------
rr = np.linspace(40, 400, 721)
izmin = np.array([node(VIN_MIN, r, il=IL_MAX)[1] for r in rr])
pz = np.array([(lambda v, i: v * i)(*node(VIN_MAX, r)) for r in rr])
r_hi = rr[np.argmax(izmin < IZ_MIN) - 1]   # 最后一个仍满足 I_Z ≥ 5 mA 的阻值
r_lo = rr[np.argmax(pz < PZ_MAX / 2)]
v180, i180 = node(VIN_MAX, R)
print(f"[数值] 最坏情况一（输入 10 V、负载 20 mA）：R ≤ {r_hi:.0f} Ω 才能保证 I_Z ≥ 5 mA")
print(f"[数值] 最坏情况二（输入 14 V、空载）：R ≥ {r_lo:.0f} Ω 才能让功耗 ≤ 0.65 W（额定 1.3 W 的一半）；R = 40 Ω 时功耗已达 {pz[0]:.2f} W")
print(f"[数值] 取 R = 180 Ω：最坏 I_Z = {node(VIN_MIN, R, il=IL_MAX)[1]*1e3:.1f} mA，最坏功耗 {v180*i180:.2f} W（I_Z = {i180*1e3:.1f} mA）")
print(f"[数值] R = 180 Ω 本身的最大功耗 ({VIN_MAX:.0f} − {v180:.2f})² ÷ 180 = {(VIN_MAX - v180)**2 / R:.2f} W")
assert r_lo < R < r_hi
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
for a in (a1, a2):
    a.axvspan(r_lo, r_hi, color="0.9", zorder=0)
    fs.ref_v(a, R, "180 Ω", y=0.98)
a1.plot(rr, izmin * 1e3, **fs.LS["cur"], label="最小 $I_Z$（10 V、20 mA）")
fs.ref_h(a1, IZ_MIN * 1e3, "5 mA", x=0.98)
fs.axlabels(a1, "限流电阻 R", "Ω", "稳压管电流", "mA")
a1.set_ylim(0, 60)
a1.legend(loc="upper right", fontsize=8)
a2.plot(rr, pz, **fs.LS["vout"], label="最大功耗（14 V、空载）")
fs.ref_h(a2, PZ_MAX / 2, "0.65 W（额定一半）", x=0.98)
fs.ref_h(a2, PZ_MAX, "1.3 W（额定）", x=0.98)
fs.axlabels(a2, "限流电阻 R", "Ω", "稳压管功耗", "W")
a2.set_ylim(0, 1.6)
a2.legend(loc="upper right", bbox_to_anchor=(1, 0.68), fontsize=8)
print(f"[数值] 灰色窗口 {r_lo:.0f}–{r_hi:.0f} Ω")
fs.save(fig, N, "10_p3_1_window.png")

# ---------- 图 10-p3-2 限流电阻过大：市电偏低时纹波漏到输出 ----------
t = np.arange(0, 0.03, 20e-6)
vi_low = ripple_in(t, 10.5, 1.0)
good = np.array([node(v, R, il=IL_MAX)[0] for v in vi_low])
bad = np.array([node(v, 270.0, il=IL_MAX)[0] for v in vi_low])
print(f"[数值] 输入 10.0–11.0 V、负载 20 mA：R = 180 Ω 输出纹波 {(good.max()-good.min())*1e3:.0f} mV；R = 270 Ω 输出 {bad.min():.2f}–{bad.max():.2f} V，纹波 {(bad.max()-bad.min())*1e3:.0f} mV")
ir270 = (10.0 - VZ) / 270
print(f"[数值] R = 270 Ω、输入 10 V 时最多只能供 {ir270*1e3:.1f} mA，小于 20 mA 负载")
assert bad.min() < 4.8 and good.max() - good.min() < 0.05
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi_low - 5, **fs.LS["vin"], label="输入 − 5 V（输入 10–11 V）")
ax.plot(t * 1e3, good, **fs.LS["vout"], label="R = 180 Ω：输出稳在 5.1 V 附近")
ax.plot(t * 1e3, bad, **fs.LS["bad"], label="R = 270 Ω：谷底失去稳压")
fs.mark(ax, t[np.argmin(bad)] * 1e3, bad.min(), fmt="{:.2f}", unit=" V", color=fs.C["bad"], dx=6, dy=-14)
fs.axlabels(ax, "时间", "ms", "电压", "V")
ax.set_ylim(3.5, 7.3)
ax.legend(loc="upper right", fontsize=8, ncol=1)
fs.save(fig, N, "10_p3_2_r_too_big.png")

# 效率（正文用）
vo_n, iz_n = node(VIN_NOM, R, il=IL_MAX)
pin = VIN_NOM * (VIN_NOM - vo_n) / R
print(f"[数值] 输入 12 V、负载 20 mA：从电源取 {(VIN_NOM - vo_n)/R*1e3:.1f} mA、{pin:.3f} W，负载得到 {vo_n*IL_MAX:.3f} W，效率 {vo_n*IL_MAX/pin*100:.0f}%")
print("10_sim OK")
