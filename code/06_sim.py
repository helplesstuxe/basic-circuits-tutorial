"""06 桥式整流：时域仿真（二极管桥 + 电容滤波），生成 06-bridge-rectifier/img/ 里的波形图。
运行：/workspace/circuits-venv/bin/python code/06_sim.py
模型：变压器次级看成「正弦电动势 + 串联电阻 R_s」（R_s 把绕组电阻和二极管导通电阻合在一起，是假设值）；
      二极管用折线模型：导通压降 0.7 V（同 P2）。显式欧拉法，步长 10 µs。
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "06"
VD = 0.7          # 每个二极管导通压降（V）
F = 50.0          # 市电频率（Hz）
DT = 10e-6        # 仿真步长（s）


def bridge(vp, C, RL, Rs, T=0.5, f=F, miswire=False, phase=0.0):
    """二极管桥 + 电容 C（C=0 表示不加电容）+ 负载 RL。
    vp：次级电动势峰值；Rs：源内阻（绕组 + 二极管电阻）。
    miswire=True：示波器地夹接在桥的输出负端，把输出负端和电源的一端（b）连在一起。
    返回 t、电源电动势 e、电源端口电压 v_ab、输出电压 vo（+ 对 −）、电源电流 i。"""
    t = np.arange(0, T, DT)
    e = vp * np.sin(2 * np.pi * f * t + phase)     # phase：合闸时刻的相位
    vo = np.zeros_like(t); vab = np.zeros_like(t); i = np.zeros_like(t)
    v = 0.0
    for k in range(len(t)):
        ek = e[k]
        if not miswire:
            drop, short = 2 * VD, False          # 两个二极管串联导通
        elif ek > 0:
            drop, short = VD, False              # 正半周：D4 被地线短接，只剩 D1 一个压降
        else:
            drop, short = VD, True               # 负半周：b → 地线 → 输出负端 → D3 → a，电源直接被短路
        if short:
            ik = (abs(ek) - VD) / Rs if abs(ek) > VD else 0.0
            i[k] = -ik
            vab[k] = ek + ik * Rs                # 端口电压被钳在 −0.7 V 附近
            charge = 0.0
        else:
            if C == 0:
                ik = max(abs(ek) - drop, 0.0) / (Rs + RL)
                v = ik * RL
            else:
                ik = max(abs(ek) - drop - v, 0.0) / Rs
            i[k] = np.sign(ek) * ik
            vab[k] = ek - np.sign(ek) * ik * Rs
            charge = ik
        if C > 0:
            v += (charge - v / RL) * DT / C
        vo[k] = v
    return t, e, vab, vo, i


def steady(t, vo, i, f=F, cycles=2):
    """取最后 cycles 个周期，返回平均值、峰峰纹波、最大值、最小值、每个半周的导通时间、峰值电流。"""
    m = t >= t[-1] - cycles / f
    v = vo[m]
    on = np.abs(i[m]) > 1e-6
    t_on = on.sum() * DT / (2 * cycles)
    return v.mean(), v.max() - v.min(), v.max(), v.min(), t_on, np.abs(i[m]).max()


# ===================== 主例：12 V 交流次级、2200 µF、75 Ω =====================
VRMS, RS, CM, RLM = 12.0, 1.0, 2200e-6, 75.0
VP = VRMS * np.sqrt(2)
print(f"[数值] 次级 {VRMS:.0f} V 有效值 → 峰值 {VP:.2f} V；减两个二极管压降 → {VP - 2*VD:.2f} V")

# ---------- 图 06-p1-2 不加电容：桥式输出 = |输入| − 1.4 V ----------
t, e, vab, vo0, i0 = bridge(VP, 0, RLM, RS, T=0.04)
pk0 = vo0.max()
print(f"[数值] 不加电容：输出峰值 {pk0:.2f} V（比输入峰值低 {VP - pk0:.2f} V）")
assert 1.4 < VP - pk0 < 1.7, "没有电容时，输出峰值比输入低两个二极管压降（再加一点内阻压降）"
assert vo0.min() >= 0, "两个半周输出都是正的"
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, e, **fs.LS["vin"], label="输入：变压器次级电压")
ax.plot(t * 1e3, np.abs(e), **fs.LS["good"], label="理想：输入取绝对值")
ax.plot(t * 1e3, vo0, **fs.LS["vout"], label="桥式整流输出 $V_o$")
fs.ref_h(ax, 0)
fs.mark(ax, 5, VP, fmt="{:.1f}", unit=" V", dx=6, dy=-2)
fs.mark(ax, 15, pk0, fmt="{:.1f}", unit=" V", dx=10, dy=-24)
fs.axlabels(ax, "时间", "ms", "电压", "V")
ax.set_ylim(-20, 27)
ax.legend(loc="upper right", fontsize=8, ncol=3)
fs.save(fig, N, "06_p1_2_bridge_wave.png")

# ---------- 图 06-p1-3 加电容以后：凸起变成「锯齿」 ----------
t, e, vab, voc, ic = bridge(VP, CM, RLM, RS, T=0.5)
avg, rip, vmax, vmin, t_on, ipk = steady(t, voc, ic)
I = avg / RLM
dv_formula = I / (2 * F * CM)
print(f"[数值] 加 2200 µF：平均 {avg:.2f} V，最高 {vmax:.2f} V，最低 {vmin:.2f} V，纹波（峰峰）{rip:.2f} V")
print(f"[数值] 负载电流 {I*1e3:.0f} mA；公式 I/(2fC) = {dv_formula:.2f} V")
print(f"[数值] 每个半周二极管只导通 {t_on*1e3:.2f} ms（半周 10 ms），电流尖峰 {ipk:.2f} A，是平均电流的 {ipk/I:.1f} 倍")
assert rip < dv_formula and rip > 0.7 * dv_formula, "仿真纹波略小于公式估计，但量级一致"
assert t_on < 0.3 / (2 * F), "二极管只在峰值附近导通一小段"
m = t >= t[-1] - 0.04
tt = (t[m] - t[m][0]) * 1e3
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(tt, np.abs(e[m]) - 2 * VD, **fs.LS["third"], label="不加电容的输出（凸起）")
ax.plot(tt, voc[m], **fs.LS["vout"], label="加 2200 µF 电容的输出 $V_o$")
fs.ref_h(ax, 0)
k = np.argmin(voc[m][:2000])
fs.mark(ax, tt[np.argmax(voc[m][:1000])], vmax, fmt="{:.2f}", unit=" V", dx=4, dy=4)
fs.mark(ax, tt[k], vmin, fmt="{:.2f}", unit=" V", dx=4, dy=-14)
ax.annotate("", xy=(37, vmax), xytext=(37, vmin), arrowprops=dict(arrowstyle="<->", lw=1.1))
ax.text(37.5, (vmax + vmin) / 2, f"纹波\n{rip:.2f} V", fontsize=9, va="center")
print(f"[数值] 图上纹波标注 {rip:.2f} V")
fs.axlabels(ax, "时间", "ms", "电压", "V")
ax.set_xlim(0, 42); ax.set_ylim(-1, 21)
ax.legend(loc="upper left", fontsize=8, ncol=2)
fs.save(fig, N, "06_p1_3_with_cap.png")

# ---------- 图 06-p2-2 稳态放大：放电斜线 + 充电电流尖峰 ----------
m = t >= t[-1] - 0.03
tt = (t[m] - t[m][0]) * 1e3
fig, (a1, a2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
a1.plot(tt, np.abs(e[m]) - 2 * VD, **fs.LS["third"], label="|次级电压| − 1.4 V")
a1.plot(tt, voc[m], **fs.LS["vout"], label="输出 $V_o$（电容电压）")
slope = I / CM
print(f"[数值] 放电斜率 I/C = {slope:.1f} V/s = {slope/1e3:.3f} V/ms")
a1.set_ylim(vmin - 2.5, vmax + 1.5)
a1.legend(loc="lower right", fontsize=8, ncol=2)
fs.axlabels(a1, None, None, "电压", "V")
a1.set_title(f"纹波（峰峰）{rip:.2f} V，公式 I/(2fC) 估计 {dv_formula:.2f} V", fontsize=9, loc="left")
a2.plot(tt, np.abs(ic[m]), **fs.LS["cur"], label="流过二极管的充电电流")
fs.ref_h(a2, I, f"负载电流 {I:.2f} A", x=0.98)
a2.set_title(f"每个半周只导通 {t_on*1e3:.2f} ms，尖峰 {ipk:.1f} A", fontsize=9, loc="left")
fs.axlabels(a2, "时间", "ms", "电流", "A")
a2.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "06_p2_2_steady.png")

# 上电瞬间：电容是空的，第一个半周电流最大（浪涌）
t5, e5, _, vo5, i5 = bridge(VP, CM, RLM, RS, T=0.04)
inrush = np.abs(i5).max()
print(f"[数值] 上电第一个周期最大电流（浪涌）{inrush:.1f} A，约为稳态尖峰的 {inrush/ipk:.1f} 倍")
_, _, _, _, i6 = bridge(VP, CM, RLM, RS, T=0.04, phase=np.pi / 2)
inrush_pk = np.abs(i6).max()
print(f"[数值] 恰好在峰值时刻合闸：浪涌 {inrush_pk:.1f} A（≈ (峰值 − 1.4 V) ÷ R_s = {(VP - 2*VD)/RS:.1f} A）")
assert inrush > ipk and inrush_pk > 2 * inrush

# ---------- 图 06-p3-1 纹波和电容大小：仿真 vs 公式 ----------
Cs = np.array([470, 1000, 2200, 4700, 10000]) * 1e-6
sim, frm = [], []
for Cx in Cs:
    t, e, _, vx, ix = bridge(VP, Cx, RLM, RS, T=0.6)
    a, r, *_ = steady(t, vx, ix)
    sim.append(r); frm.append(a / RLM / (2 * F * Cx))
sim, frm = np.array(sim), np.array(frm)
print("[数值] 纹波（仿真 / 公式）：" + "，".join(f"{c*1e6:.0f} µF {s:.2f}/{q:.2f} V" for c, s, q in zip(Cs, sim, frm)))
assert np.all(np.diff(sim) < 0), "电容越大纹波越小"
assert abs(sim[3] / sim[2] - 2200 / 4700) < 0.06, "电容翻倍，纹波约减半"
assert np.all(sim < frm), "公式偏保守（估大一点）"
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.loglog(Cs * 1e6, frm, **fs.LS["good"], label="公式 $I/(2fC)$")
ax.loglog(Cs * 1e6, sim, **{**fs.LS["vout"], "marker": "o"}, label="仿真")
for c, s in zip(Cs, sim):
    fs.mark(ax, c * 1e6, s, fmt="{:.2f}", unit=" V", dx=4, dy=-12)
fs.ref_h(ax, 1.0, "1 V", x=0.06, ha="left")
fs.axlabels(ax, "滤波电容 C", "µF", "纹波（峰峰）", "V")
ax.legend(loc="upper right", fontsize=8)
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
ax.xaxis.set_major_locator(FixedLocator([470, 1000, 2200, 4700, 10000]))
ax.xaxis.set_major_formatter(FixedFormatter(["470", "1000", "2200", "4700", "10000"]))
ax.yaxis.set_major_locator(FixedLocator([0.1, 0.2, 0.5, 1, 2, 5]))
ax.yaxis.set_major_formatter(FixedFormatter(["0.1", "0.2", "0.5", "1", "2", "5"]))
for a_ in (ax.xaxis, ax.yaxis):
    a_.set_minor_locator(NullLocator())
fs.save(fig, N, "06_p3_1_ripple_vs_c.png")

# ---------- 图 06-p3-2 低压实验里示波器地夹接错 ----------
VPX, RSX, CX, RLX = 5.0, 50.0, 100e-6, 1e3     # 信号发生器 50 Hz、峰值 5 V、输出电阻 50 Ω；100 µF；1 kΩ
t, e, vab_ok, vo_ok, i_ok = bridge(VPX, CX, RLX, RSX, T=0.6)
_, _, vab_bad, vo_bad, i_bad = bridge(VPX, CX, RLX, RSX, T=0.6, miswire=True)
a_ok, r_ok, *_ = steady(t, vo_ok, i_ok)
a_bad, r_bad, *_ = steady(t, vo_bad, i_bad)
ishort = np.abs(i_bad[t > 0.5][vab_bad[t > 0.5] < 0]).max()
print(f"[数值] 低压实验（5 V 峰值、50 Ω、100 µF、1 kΩ）：正确接法平均 {a_ok:.2f} V、纹波 {r_ok:.2f} V")
print(f"[数值] 地夹接错：平均 {a_bad:.2f} V、纹波 {r_bad:.2f} V；负半周发生器端口被钳在 {vab_bad[t>0.5].min():.2f} V，短路电流 {ishort*1e3:.0f} mA")
assert r_bad > 1.5 * r_ok, "接错后变成半波，纹波明显变大"
assert vab_bad[t > 0.5].min() > -0.8, "负半周电源被一个二极管短路"
m = t >= t[-1] - 0.04
tt = (t[m] - t[m][0]) * 1e3
fig, (a1, a2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
a1.plot(tt, vab_ok[m], **fs.LS["vin"], label="正确接法：发生器输出")
a1.plot(tt, vab_bad[m], **fs.LS["bad"], label="地夹接错：负半周被削平")
fs.mark(a1, tt[np.argmin(vab_bad[m])], vab_bad[m].min(), fmt="{:.2f}", unit=" V", dx=6, dy=-12, color=fs.C["bad"])
fs.ref_h(a1, 0)
fs.axlabels(a1, None, None, "发生器端口", "V")
a1.set_ylim(-6.5, 7.5)
a1.legend(loc="upper right", fontsize=8, ncol=2)
a2.plot(tt, vo_ok[m], **fs.LS["vout"], label=f"正确接法 $V_o$：纹波 {r_ok:.2f} V")
a2.plot(tt, vo_bad[m], **fs.LS["bad"], label=f"地夹接错：纹波 {r_bad:.2f} V")
fs.axlabels(a2, "时间", "ms", "输出", "V")
a2.set_ylim(0, 6)
a2.legend(loc="lower right", fontsize=8, ncol=2)
fs.save(fig, N, "06_p3_2_scope_ground.png")

print("06_sim OK")
