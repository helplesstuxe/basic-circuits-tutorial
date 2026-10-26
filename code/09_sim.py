"""09 精密整流：时域仿真（图 09-p2-2、09-p2-4、09-p3-1、09-p3-2）。
运行：/workspace/circuits-venv/bin/python code/09_sim.py
模型是简化模型，只为看清趋势：
  运放 = 单极点（开环增益 A = 10 万、增益带宽积 GBW）+ 压摆率限幅 + 输出最多 ±13.5 V；
  二极管 = 折线模型（0.7 V 导通、导通电阻 10 Ω，与 03 的「0.7 V 规则」一致）。
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "09"
VON, RD, A0, RAIL = 0.7, 10.0, 1e5, 13.5
R1 = RF = RL = 10e3
OPAMPS = {   # 名称: (GBW / Hz, 压摆率 / (V/s))；数据见 notes/09-research.md
    "741 级": (1e6, 0.5e6),
    "TL072 级": (3e6, 8e6),
}


def basic_net(voa):
    """基本型：运放输出脚 → 二极管 → R_L。返回 V_o。"""
    return (voa - VON) * RL / (RL + RD) if voa > VON else 0.0


def improved_net(voa, vi):
    """改进型（反相型）：D1 运放脚 → V_o，D2 虚地点 → 运放脚。
    对 D1、D2 的四种通断组合各解一次两节点方程，返回自洽的 (V_-, V_o)。"""
    g = 1 / RD
    for a in (0, 1):
        for b in (0, 1):
            a11, a12, b1 = -1 / R1 - 1 / RF - b * g, 1 / RF, -vi / R1 - b * g * (voa + VON)
            a21, a22, b2 = 1 / RF, -a * g - 1 / RF - 1 / RL, -a * g * (voa - VON)
            det = a11 * a22 - a12 * a21
            vm = (b1 * a22 - a12 * b2) / det
            vo = (a11 * b2 - a21 * b1) / det
            if ((voa - vo - VON) > 0) == bool(a) and ((vm - voa - VON) > 0) == bool(b):
                return vm, vo
    raise RuntimeError("二极管状态无解")


def run(kind, f, vpk, opamp, cycles=2):
    gbw, sr = OPAMPS[opamp]
    dt = min(1 / (2 * math.pi * gbw) / 8, 1 / f / 2000)
    n = int(cycles / f / dt)
    wp = 2 * math.pi * gbw / A0
    t = np.arange(n) * dt
    vi = vpk * np.sin(2 * np.pi * f * t)
    voa = np.empty(n); vo = np.empty(n)
    x = vm = o = 0.0
    for k in range(n):
        v = float(vi[k])
        diff = (v - o) if kind == "basic" else (0.0 - vm)       # V_+ − V_-
        dv = wp * (A0 * diff - x)
        dv = max(-sr, min(sr, dv))                              # 压摆率限幅
        x = max(-RAIL, min(RAIL, x + dv * dt))                  # 电源限幅
        if kind == "basic":
            o = basic_net(x)
        else:
            vm, o = improved_net(x, v)
        voa[k] = x; vo[k] = o
    ideal = np.maximum(vi, 0) if kind == "basic" else np.maximum(-vi, 0)
    return t, vi, voa, vo, ideal


def avg_err(t, vo, ideal):
    m = t >= t[-1] / 2                                           # 只看第二个周期
    return (vo[m].mean() - ideal[m].mean()) / ideal[m].mean() * 100


def two_panel(t, vi, voa, vo, ideal, title_o, name, voa_ylim):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
    ms = t * 1e3
    a1.plot(ms, vi * 1e3, **fs.LS["vin"], label="输入 $V_i$")
    a1.plot(ms, ideal * 1e3, **fs.LS["good"], label="理想整流")
    a1.plot(ms, vo * 1e3, **fs.LS["vout"], label=title_o)
    fs.ref_h(a1, 0)
    a1.set_ylabel("电压 / mV")
    a1.set_ylim(-260, 330)
    a1.legend(loc="upper right", fontsize=8, ncol=3)
    a2.plot(ms, voa, **fs.LS["third"], label="运放输出脚电压")
    fs.ref_h(a2, 0)
    a2.set_ylim(*voa_ylim)
    fs.axlabels(a2, "时间", "ms", "运放输出脚", "V")
    a2.legend(loc="upper right", fontsize=8)
    return fig, a1, a2


# ---------- 图 09-p2-2 基本型 + 741 级运放，1 kHz、峰值 0.2 V ----------
t, vi, voa, vo, ideal = run("basic", 1e3, 0.2, "741 级")
e = avg_err(t, vo, ideal)
m2 = t >= 1e-3
k_up = np.argmax(m2 & (vo > 0.01))                               # 第二周期里输出第一次超过 10 mV
delay_us = (t[k_up] - 1e-3) * 1e6
print(f"[数值] 基本型 741 级 1 kHz：平均值误差 {e:.1f}%，运放脚最低 {voa.min():.1f} V、最高 {voa.max():.2f} V，"
      f"过零后 {delay_us:.0f} µs 输出才超过 10 mV")
assert voa.min() <= -RAIL + 0.01, "负半周运放脚一路冲到负饱和"
t_slew = (RAIL + VON) / OPAMPS["741 级"][1] * 1e6
print(f"[数值] 只按压摆率算，从 −{RAIL} V 爬到 +{VON} V 需要 {t_slew:.1f} µs")
assert delay_us > t_slew, "实际恢复比纯压摆率估算还慢（过零附近输入很小，运放「推力」不足）"
fig, a1, a2 = two_panel(t, vi, voa, vo, ideal, "基本型 $V_o$", "", (-15, 3))
fs.ref_h(a2, -RAIL, "负饱和", x=0.98)
fs.mark(a2, t[np.argmin(voa)] * 1e3, voa.min(), fmt="{:.1f}", unit=" V", dx=6, dy=4)
a1.set_title(f"平均值误差 {e:.1f}%", fontsize=9, loc="left")
fs.save(fig, N, "09_p2_2_basic_sim.png")

# ---------- 图 09-p2-4 改进型 + 741 级运放，1 kHz、峰值 0.2 V ----------
t, vi, voa, vo, ideal = run("improved", 1e3, 0.2, "741 级")
e_imp1k = avg_err(t, vo, ideal)
print(f"[数值] 改进型 741 级 1 kHz：平均值误差 {e_imp1k:.1f}%，运放脚最低 {voa.min():.2f} V、最高 {voa.max():.2f} V")
assert -1.0 < voa.min() < -0.6 and 0.6 < voa.max() < 1.0, "运放脚只在约 ±0.8 V 之间来回"
assert abs(e_imp1k) < abs(e), "改进型误差更小"
fig, a1, a2 = two_panel(t, vi, voa, vo, ideal, "改进型 $V_o$", "", (-1.5, 1.5))
fs.mark(a2, t[np.argmin(voa)] * 1e3, voa.min(), fmt="{:.2f}", unit=" V", dx=6, dy=-10)
fs.mark(a2, t[np.argmax(voa)] * 1e3, voa.max(), fmt="{:.2f}", unit=" V", dx=6, dy=2)
a1.set_title(f"平均值误差 {e_imp1k:.1f}%", fontsize=9, loc="left")
fs.save(fig, N, "09_p2_4_improved_sim.png")

# ---------- 图 09-p3-1 10 kHz 时三种组合的波形 ----------
cases = [("basic", "741 级", "基本型 + 741 级"), ("basic", "TL072 级", "基本型 + TL072 级"),
         ("improved", "741 级", "改进型 + 741 级")]
fig, axs = plt.subplots(3, 1, figsize=fs.SIZE["tall"], sharex=True)
err10 = {}
for ax, (kind, op, lab), sty in zip(axs, cases, ["bad", "vout", "third"]):
    t, vi, voa, vo, ideal = run(kind, 10e3, 0.2, op)
    err10[lab] = avg_err(t, vo, ideal)
    print(f"[数值] 10 kHz {lab}：平均值误差 {err10[lab]:.1f}%")
    ax.plot(t * 1e6, ideal * 1e3, **fs.LS["good"], label="理想")
    ax.plot(t * 1e6, vo * 1e3, **fs.LS[sty], label=f"{lab}（误差 {err10[lab]:.1f}%）")
    fs.ref_h(ax, 0)
    ax.set_ylim(-30, 290)
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.set_ylabel("$V_o$ / mV")
axs[-1].set_xlabel("时间 / µs")
assert err10["基本型 + 741 级"] < -50, "741 级基本型在 10 kHz 基本失效"
assert abs(err10["改进型 + 741 级"]) < abs(err10["基本型 + TL072 级"]) < abs(err10["基本型 + 741 级"])
fs.save(fig, N, "09_p3_1_10k_wave.png")

# ---------- 图 09-p3-2 平均值误差随频率 ----------
freqs = [1e3, 2e3, 5e3, 10e3, 20e3]
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
curves = {}
for (kind, op, lab), sty in zip(cases, ["bad", "vout", "third"]):
    errs = [avg_err(*[x for i, x in enumerate(run(kind, f, 0.2, op)) if i in (0, 3, 4)]) for f in freqs]
    curves[lab] = errs
    print(f"[数值] {lab}：" + "，".join(f"{f/1e3:g} kHz {x:.1f}%" for f, x in zip(freqs, errs)))
    ax.semilogx(np.array(freqs) / 1e3, np.abs(errs), **{"marker": "o", **fs.LS[sty], "markevery": 1}, label=lab)
for lab, errs in curves.items():
    fs.mark(ax, 10, abs(errs[3]), fmt="{:.0f}", unit="%", dx=-26, dy=4)
fs.ref_h(ax, 1, "1%", x=0.6, ha="left")
assert all(abs(a) <= abs(b) + 1e-9 for a, b in zip(curves["基本型 + 741 级"], curves["基本型 + 741 级"][1:])), "频率越高误差越大"
assert abs(curves["改进型 + 741 级"][0]) < 1, "改进型 1 kHz 时误差不到 1%"
ax.set_yscale("log")
ax.set_xticks([1, 2, 5, 10, 20]); ax.set_xticklabels(["1", "2", "5", "10", "20"])
fs.axlabels(ax, "信号频率", "kHz", "平均值误差（绝对值）", "%")
ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "09_p3_2_err_vs_f.png")
print("09_sim OK")
