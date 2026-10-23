"""09 开关电源：降压（Buck）电路的时域仿真与效率估算，生成 09-switching-power-supply/img/ 里的曲线图。
运行：/workspace/circuits-venv/bin/python code/09_sim.py
主例（见 09 page2）：V_in = 12 V → V_o = 5 V，负载 5 Ω（1 A），开关频率 200 kHz，L = 47 µH，C = 47 µF。
异步降压：上管 MOSFET 导通电阻 50 mΩ、续流肖特基二极管压降 0.4 V、电感直流电阻 50 mΩ（均为示意值）。
所有仿真都是低压直流电路，不涉及市电。图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "09"
VIN, VO_SET, R_LOAD = 12.0, 5.0, 5.0
IO = VO_SET / R_LOAD
FSW = 200e3
T = 1 / FSW
L0, C0 = 47e-6, 47e-6
RDS, VF, DCR = 0.05, 0.4, 0.05            # 上管导通电阻、肖特基压降、电感直流电阻（示意值）
TSW = 20e-9                               # 每次开关的过渡时间之和（上升 + 下降，示意值）
I_CTL = 0.005                             # 控制芯片自身耗电 5 mA（示意值）
STEPS = 200                               # 每个开关周期的计算步数


def buck(D, vin=VIN, L=L0, periods=600, ideal=False, Lfun=None, keep=3, il0=None, vc0=None):
    """异步降压的逐步仿真。ideal=True 时开关、二极管、电感都没有损耗。
    返回最后 keep 个周期的 (t, 开关节点电压, 电感电流, 输出电压)，以及全程的平均输出。"""
    rds, vf, dcr = (0.0, 0.0, 0.0) if ideal else (RDS, VF, DCR)
    dt = T / STEPS
    il = IO if il0 is None else il0
    vc = D * vin if vc0 is None else vc0
    n = periods * STEPS
    rec = keep * STEPS
    ts, vs, is_, vo = (np.zeros(rec) for _ in range(4))
    k0 = n - rec
    def sub(il, vc, on, h):
        if on:
            vsw = vin - il * rds
        else:
            vsw = -vf if il > 0 else vc            # 电流降到 0 后二极管截止（断续模式）
        Lk = Lfun(il) if Lfun else L
        il_new = il + (vsw - vc - il * dcr) / Lk * h
        if not on and il_new < 0:
            il_new = 0.0
        vc = vc + (il - vc / R_LOAD) / C0 * h
        return il_new, vc, vsw

    for k in range(n):
        j = k % STEPS
        fon = min(max(D * STEPS - j, 0.0), 1.0)    # 这一步里上管导通的比例（开关边沿落在步内时拆成两段）
        vsw = 0.0
        if fon > 0:
            il, vc, v1 = sub(il, vc, True, fon * dt)
            vsw += v1 * fon
        if fon < 1:
            il, vc, v2 = sub(il, vc, False, (1 - fon) * dt)
            vsw += v2 * (1 - fon)
        if k >= k0:
            r = k - k0
            ts[r], vs[r], is_[r], vo[r] = k * dt, vsw, il, vc
    return ts - ts[0], vs, is_, vo


def duty_real(vin, io=IO, vo=VO_SET):
    """考虑损耗后实际需要的占空比：D(V_in − I·R_DS) − (1 − D)V_F = V_o + I·DCR。"""
    return (vo + io * DCR + VF) / (vin - io * RDS + VF)


def losses(vin, io=IO, vo=VO_SET, sync=False):
    D = duty_real(vin, io, vo) if not sync else (vo + io * DCR) / (vin - 0 * io)   # 同步：下管压降很小，近似用理想式
    p = dict(
        上管导通=io ** 2 * RDS * D,
        续流元件=(io ** 2 * RDS * (1 - D)) if sync else VF * io * (1 - D),
        电感铜损=io ** 2 * DCR,
        开关过渡=0.5 * vin * io * TSW * FSW,
        控制芯片=vin * I_CTL,
    )
    return D, p


# ---------- 主例数值 ----------
D_ideal = VO_SET / VIN
D_r = duty_real(VIN)
dIL = (VIN - VO_SET) * D_ideal / (FSW * L0)
dVO = dIL / (8 * FSW * C0)
print(f"[数值] 理想占空比 D = V_o/V_in = {D_ideal:.3f}（{D_ideal*100:.1f}%）；考虑损耗后 D = {D_r:.3f}（{D_r*100:.1f}%）")
print(f"[数值] 电感电流纹波 ΔI_L = (V_in − V_o)·D/(f·L) = {dIL:.3f} A（输出电流的 {dIL/IO*100:.0f}%）；输出纹波 ΔI_L/(8fC) = {dVO*1e3:.1f} mV")
t, vs, il, vo = buck(D_r)
for _ in range(2):                          # 真实电源靠反馈自动微调占空比；这里用两次修正代替
    D_r += (VO_SET - vo.mean()) / (VIN + VF)
    t, vs, il, vo = buck(D_r)
print(f"[数值] 反馈微调后占空比 D = {D_r:.3f}（{D_r*100:.1f}%）")
il_pk, il_min = il.max(), il.min()
vo_avg, vo_pp = vo.mean(), vo.max() - vo.min()
print(f"[数值] 仿真：V_o 平均 {vo_avg:.3f} V，纹波 {vo_pp*1e3:.1f} mV；电感电流 {il_min:.3f}–{il_pk:.3f} A（峰峰 {il_pk-il_min:.3f} A，平均 {il.mean():.3f} A）")
assert abs(vo_avg - 5.0) < 0.05
assert abs((il_pk - il_min) - dIL) < 0.05
# 斜率
s_on = (VIN - VO_SET) / L0
s_off = -VO_SET / L0
print(f"[数值] 斜率：开关导通 (12 − 5)/L = {s_on/1e3:.0f} A/ms ；断开 −5/L = {s_off/1e3:.0f} A/ms")

# ---------- 图 09-p1-2 开关节点、电感电流、输出（三个周期） ----------
fig, axs = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
tu = t * 1e6
axs[0].plot(tu, vs, **fs.LS["vin"], label="开关节点电压（电感左端）")
axs[0].plot(tu, vo, **fs.LS["vout"], label="输出电压 $V_o$")
axs[0].text(tu[-1], 6.3, f"开关节点平均 ≈ {vs.mean():.2f} V", ha="right", fontsize=9)
print(f"[数值] 开关节点平均 ≈ {vs.mean():.2f} V")
axs[0].set_ylim(-2, 14.5)
axs[0].legend(loc="upper right", fontsize=8, ncol=2)
fs.axlabels(axs[0], "时间", "µs", "电压", "V")
axs[1].plot(tu, il, **fs.LS["cur"], label="电感电流")
fs.ref_h(axs[1], IO, f"负载电流 {IO:.1f} A", x=0.99)
fs.mark(axs[1], tu[np.argmax(il)], il_pk, "{:.2f}", " A", dx=4, dy=2)
fs.mark(axs[1], tu[np.argmin(il)], il_min, "{:.2f}", " A", dx=4, dy=-10)
axs[1].set_ylim(0.7, 1.3)
axs[1].legend(loc="upper left", fontsize=8)
fs.axlabels(axs[1], "时间", "µs", "电流", "A")
fs.save(fig, N, "09_p1_2_waveforms.png")

# ---------- 图 09-p1-3 效率对比 ----------
vins = np.linspace(7, 24, 69)
eta_lin = VO_SET * IO / (vins * (IO + 0.0042))            # 7805 静态电流 4.2 mA（TI uA78xx 手册典型值）
eta_buck = np.array([VO_SET * IO / (VO_SET * IO + sum(losses(v)[1].values())) for v in vins])
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(vins, eta_buck * 100, **fs.LS["vout"], label="开关降压（Buck）")
ax.plot(vins, eta_lin * 100, **fs.LS["bad"], label="线性稳压（7805）")
for v in (12.0, 24.0):
    i = np.argmin(abs(vins - v))
    fs.mark(ax, v, eta_buck[i] * 100, "{:.0f}", " %", dx=-8, dy=-14)
    fs.mark(ax, v, eta_lin[i] * 100, "{:.0f}", " %", dx=4, dy=4)
ax.set_ylim(0, 100)
ax.legend(loc="center right", fontsize=8)
fs.axlabels(ax, "输入电压", "V", "效率", "%")
fs.save(fig, N, "09_p1_3_efficiency.png")
e12 = eta_buck[np.argmin(abs(vins - 12))]
l12 = eta_lin[np.argmin(abs(vins - 12))]
print(f"[数值] 12 V → 5 V、1 A：线性 {l12*100:.1f}%（发热 {(12-5)*1:.1f} W），开关 {e12*100:.1f}%（损耗 {5/e12-5:.2f} W）")
assert e12 > 0.88 and l12 < 0.45
assert eta_buck.min() > 0.88

# ---------- 图 09-p2-2 一个周期内的斜率（放大） ----------
fig, axs = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
m = tu <= 2 * T * 1e6
axs[0].plot(tu[m], vs[m], **fs.LS["vin"], label="开关节点电压")
fs.ref_h(axs[0], VIN, "12 V（上管导通）", x=0.99)
fs.ref_h(axs[0], -VF, "−0.4 V（二极管续流）", x=0.99)
axs[0].set_ylim(-3, 15)
axs[0].legend(loc="center right", fontsize=8)
fs.axlabels(axs[0], "时间", "µs", "电压", "V")
axs[1].plot(tu[m], il[m], **fs.LS["cur"], label="电感电流")
fs.ref_v(axs[1], D_r * T * 1e6, f"D·T = {D_r*T*1e6:.2f} µs", y=0.98)
print(f"[数值] D·T = {D_r*T*1e6:.2f} µs，T = {T*1e6:.1f} µs")
axs[1].text(D_r * T * 1e6 * 0.5, 0.82, f"上升 {s_on/1e3:.0f} A/ms", ha="center", fontsize=9)
axs[1].text(D_r * T * 1e6 + (1 - D_r) * T * 1e6 * 0.5, 0.82, f"下降 {abs(s_off)/1e3:.0f} A/ms", ha="center", fontsize=9)
axs[1].set_ylim(0.75, 1.25)
axs[1].legend(loc="upper right", fontsize=8)
fs.axlabels(axs[1], "时间", "µs", "电流", "A")
fs.save(fig, N, "09_p2_2_slopes.png")

# ---------- 图 09-p2-3 占空比与输出 ----------
Ds = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
vo_ideal, vo_loss = [], []
for D in Ds:
    _, _, _, v1 = buck(D, ideal=True, periods=500, il0=D * VIN / R_LOAD)
    _, _, _, v2 = buck(D, periods=500, il0=D * VIN / R_LOAD)
    vo_ideal.append(v1.mean()); vo_loss.append(v2.mean())
vo_ideal, vo_loss = np.array(vo_ideal), np.array(vo_loss)
for D, a, b in zip(Ds, vo_ideal, vo_loss):
    print(f"[数值] D = {D:.1f}：D·V_in = {D*VIN:.2f} V，理想元件仿真 {a:.2f} V，含损耗 {b:.2f} V")
assert np.all(abs(vo_ideal - Ds * VIN) < 0.05)
assert np.all(vo_loss < vo_ideal)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
dd = np.linspace(0, 1, 11)
ax.plot(dd, dd * VIN, **fs.LS["good"], label="公式 $V_o = D \\cdot V_{in}$")
ax.plot(Ds, vo_ideal, "o", color=fs.C["vout"], label="仿真：理想元件")
ax.plot(Ds, vo_loss, **fs.LS["third"], marker="s", ms=4, label="仿真：含二极管压降等损耗")
fs.mark(ax, D_r, VO_SET, "{:.1f}", " V", dx=-38, dy=6)
fs.ref_v(ax, D_r, f"D = {D_r:.2f}", y=0.15)
ax.set_xlim(0, 1); ax.set_ylim(0, 12.5)
ax.legend(loc="upper left", fontsize=8)
fs.axlabels(ax, "占空比 D", None, "输出电压", "V")
fs.save(fig, N, "09_p2_3_duty.png")

# ---------- 图 09-p3-1 电感饱和 ----------
def Lsat(isat):
    ik = isat / (0.4286 ** (1 / 6))           # L 在 I_sat 处降到 70%（下降 30%）
    return lambda i: max(L0 / (1 + min(abs(i) / ik, 10.0) ** 6), 0.2 * L0)   # 最低降到标称的 20%

for isat in (2.0, 0.8):
    print(f"[数值] 饱和电流 {isat:.1f} A 的电感：在 {isat:.1f} A 处电感量 {Lsat(isat)(isat)*1e6:.1f} µH（标称 {L0*1e6:.0f} µH）")
_, _, ig, _ = buck(D_r, Lfun=Lsat(2.0), periods=600)
tb, _, ib, vb = buck(D_r, Lfun=Lsat(0.8), periods=600)
print(f"[数值] 合适电感（I_sat 2.0 A）：峰值 {ig.max():.2f} A，峰峰 {ig.max()-ig.min():.2f} A")
print(f"[数值] 偏小电感（I_sat 0.8 A）：峰值 {ib.max():.2f} A，峰峰 {ib.max()-ib.min():.2f} A")
assert ib.max() > ig.max() + 0.1
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
tbu = tb * 1e6
ax.plot(tbu, ig, **fs.LS["cur"], label="电感饱和电流 2.0 A：三角波")
ax.plot(tbu, ib, **fs.LS["bad"], label="电感饱和电流 0.8 A：尖峰")
fs.ref_h(ax, 1.0, "1.0 A", x=0.99)
fs.mark(ax, tbu[np.argmax(ig)], ig.max(), "{:.2f}", " A", dx=4, dy=0)
fs.mark(ax, tbu[np.argmax(ib)], ib.max(), "{:.2f}", " A", dx=4, dy=0)
ax.set_ylim(0.4, max(1.9, ib.max() + 0.2))
ax.legend(loc="upper left", fontsize=8, ncol=2)
fs.axlabels(ax, "时间", "µs", "电感电流", "A")
fs.save(fig, N, "09_p3_1_saturation.png")

# ---------- 图 09-p3-2 损耗分布：异步 vs 同步 ----------
Da, pa = losses(VIN)
Ds_, ps = losses(VIN, sync=True)
names = list(pa.keys())
for k in names:
    print(f"[数值] {k}：异步 {pa[k]:.3f} W，同步 {ps[k]:.3f} W")
ta, tsy = sum(pa.values()), sum(ps.values())
ea, es = 5 / (5 + ta), 5 / (5 + tsy)
print(f"[数值] 总损耗：异步 {ta:.2f} W（效率 {ea*100:.1f}%），同步 {tsy:.2f} W（效率 {es*100:.1f}%）")
assert pa["续流元件"] > 5 * ps["续流元件"] and es > ea
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
x = np.arange(len(names))
ax.bar(x - 0.2, [pa[k] for k in names], 0.4, color=fs.C["bad"], label=f"异步（二极管续流），共 {ta:.2f} W")
ax.bar(x + 0.2, [ps[k] for k in names], 0.4, color=fs.C["vout"], label=f"同步（下管续流），共 {tsy:.2f} W")
for i, k in enumerate(names):
    ax.text(i - 0.2, pa[k] + 0.004, f"{pa[k]:.3f}", ha="center", fontsize=8)
    ax.text(i + 0.2, ps[k] + 0.004, f"{ps[k]:.3f}", ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(names)
ax.set_ylim(0, 0.28)
ax.legend(loc="upper right", fontsize=8)
fs.axlabels(ax, "损耗来源", None, "功率", "W")
fs.save(fig, N, "09_p3_2_losses.png")
print("[完成] 09_sim.py 全部断言通过")
