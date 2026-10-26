"""18 微分电路：用 ngspice + TI LM358B 官方模型核对页面数值。在仓库根目录运行：python spice/18/run.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check

def wave(r, fname="out.txt"):
    d = np.loadtxt(pathlib.Path(r["_dir"]) / fname)
    return d[:, 0], d[:, 1]

def npp(cir, flat=False, **p):
    """与 code/18_sim.py 的 noise_pp 相同：同一电路有/无干扰两次结果相减，取 t>1 ms 的峰峰值。"""
    r0 = ng.run(cir, dict(p, AN=0)); r1 = ng.run(cir, dict(p, AN="10m"))
    t0, v0 = wave(r0); t1, v1 = wave(r1)
    tg = np.arange(1e-3, 8e-3, 0.2e-6)
    d = np.interp(tg, t1, v1) - np.interp(tg, t0, v0)
    if flat:   # 只看平顶（每个拐角后 0.5 ms 到下一个拐角前），避开拐角处 LM358B 输出级交越
        ph = (tg % 1e-3) / 1e-3
        d = d[(ph > 0.5) & (ph < 0.98)]
    return float(d.max() - d.min())

print("== 18 微分电路 ==")
# --- page1 图18-p1-3 / page2 结论一：±0.5 V 500 Hz 三角波 -> ±1 V 方波 ---
# 实用微分器（R1=1k, Cf=10n）在平顶后段的值
r = ng.run("diff_tri.cir", dict(R1="1k", CF="10n"))
t, v = wave(r)
hi = v[(t > 5.6e-3) & (t < 6.0e-3)].mean()   # 输入下降段 -> 输出 +1 V
lo = v[(t > 6.6e-3) & (t < 7.0e-3)].mean()   # 输入上升段 -> 输出 -1 V
check("p1 图18-p1-3", "实用微分器 输入下降段输出", 1.0, hi, "V")
check("p1 图18-p1-3", "实用微分器 输入上升段输出", -1.0, lo, "V")
s = (t > 4e-3)
vrms = np.sqrt(np.mean(v[s] ** 2))
check("面包板", "实用版输出 真有效值(参考)", None, vrms, "V")
# 理想微分器（无 R1/Cf）+ LM358B：平顶均值、拐角过冲、振铃频率（page3 图18-p3-1）
r = ng.run("diff_tri.cir")
t, v = wave(r)
s = (t > 1e-3) & (t < 2e-3)
check("p3 图18-p3-1", "理想微分器拐角后过冲峰值", 2.80, v[s].max(), "V", "LM358B 宏模型", v="⚠️")
x = v[s] - v[s].mean(); tt = t[s]
zc = tt[1:][np.diff(np.sign(x)) != 0]
fring = 1 / (2 * np.mean(np.diff(zc)))
check("p3 图18-p3-1", "理想微分器振铃频率", 13.8e3, fring, "Hz")
s2 = (t > 1.7e-3) & (t < 2.0e-3)
check("p1 示波器第1步", "理想版(无R1/Cf)平顶上叠加的振铃峰峰", 0.0, np.ptp(v[s2]), "V", "页面说通道2是±1 V方波", v="❌")

# --- page2 图18-p2-3 / 代码输出：10 mV 20 kHz 干扰（有/无干扰相减） ---
check("p2 图18-p2-3", "理想微分器干扰峰峰(理想运放)", 2.51, npp("diff_tri_idealop.cir"), "V")
check("p2 图18-p2-3", "理想微分器干扰峰峰(LM358B)", 2.51, npp("diff_tri.cir"), "V", "20 kHz 靠近 14.6 kHz 谐振峰", v="⚠️")
check("p2 代码输出", "只串 R1=1k 干扰峰峰(理想运放)", 0.21, npp("diff_tri_idealop.cir", R1="1k"), "V")
check("p2 代码输出", "只串 R1=1k 干扰峰峰(LM358B)", 0.21, npp("diff_tri.cir", R1="1k"), "V", v="⚠️")
check("p2 图18-p2-3", "实用微分器(R1+Cf)干扰峰峰(理想运放)", 0.016, npp("diff_tri_idealop.cir", R1="1k", CF="10n"), "V")
check("p2 图18-p2-3", "实用微分器(R1+Cf)干扰峰峰(LM358B, 平顶段)", 0.016, npp("diff_tri.cir", True, R1="1k", CF="10n"), "V", v="⚠️")
check("p2 图18-p2-3", "实用微分器(R1+Cf)干扰峰峰(LM358B, 含拐角)", 0.016, npp("diff_tri.cir", R1="1k", CF="10n"), "V", "拐角输出过零处交越失真", v="ℹ️")

# --- page3 扫描图二：R1 扫描（理想运放，无 Cf） ---
table = {"100": (1.573, 0.02e-3), "300": (0.645, 0.07e-3), "1k": (0.199, 0.23e-3), "3k": (0.067, 0.69e-3)}
for r1, (pp, t90) in table.items():
    check("p3 R1 扫描表", f"R1={r1} 干扰峰峰", pp * 1e3, npp("diff_tri_idealop.cir", R1=r1) * 1e3, "mV")
    r = ng.run("diff_tri_idealop.cir", dict(R1=r1))
    t, v = wave(r)
    k = (t > 3e-3) & (v > 0.8)        # 3 ms 拐角后输出 -1 -> +1，到 0.8 V 即 90%
    check("p3 R1 扫描表", f"R1={r1} 边沿 90% 用时", t90 * 1e3, (t[k][0] - 3e-3) * 1e3, "ms", tol=20)

# --- page2 结论二 / page1 示波器第 3 步：正弦增益（AC，LM358B） ---
r = ng.run("ac_gain.cir")
check("p2 结论二", "理想微分器 159 Hz 增益", 1.0, r["g159"], "倍")
check("p2 结论二", "理想微分器 1.59 kHz 增益", 10.0, r["g1590"], "倍")
check("p2 结论二", "理想微分器 20 kHz 增益", 126, r["g20k"], "倍", "接近 LM358B 谐振峰", v="⚠️")
check("p2 结论二", "理想微分器 AC 增益峰值(谐振)", None, r["gpk"], "倍", "≈14.6 kHz 处")
check("p1 示波器第3步", "159 Hz 0.5 V 正弦输出幅度(理想版瞬态)", 0.5, r["tran_amp"], "V", "叠加了持续振铃", v="❌")
r = ng.run("ac_gain.cir", dict(R1="1k", CF="10n"))
check("p1 示波器第3步", "同上，实用版(R1+Cf)", 0.5, r["tran_amp"], "V")
r = ng.run("ac_gain.cir", dict(R1="1k"))
check("p3 练习2", "只串 R1=1k 时 50 kHz 增益(LM358B)", 10.0, r["g50k"], "倍", "页面：封顶约 Rf/R1=10")
check("p3 练习2", "5 mV 50 kHz 干扰输出幅度(只串R1)", 50, 5 * r["g50k"], "mV", "页面：不超过约 50 mV")

# --- page1 图18-p1-5：三种接法 ---
r = ng.run("three_circuits.cir")
d = np.loadtxt(pathlib.Path(r["_dir"]) / "three.txt"); t = d[:, 0]
s = (t > 6e-3) & (t < 10e-3)
check("p1 图18-p1-5", "积分电路三角波峰峰", 0.45, np.ptp(d[s, 3]), "V")
check("p1 图18-p1-5", "微分电路边沿脉冲正峰(LM358B)", 5.0, d[s, 5].max(), "V", "理想运放才是 5 V", v="⚠️")
check("p1 图18-p1-5", "微分电路边沿脉冲负峰(LM358B)", -5.0, d[s, 5].min(), "V", v="⚠️")
check("p1 图18-p1-5", "电容–电容接法 高电平", 0.0, d[s, 7].max(), "V")
check("p1 图18-p1-5", "电容–电容接法 低电平", -2.0, d[s, 7].min(), "V")

# --- page1 偏置电流漂移 ---
r = ng.run("capcap_drift.cir")
check("p1 附图第二格", "电容–电容接法漂移速度 |dVo/dt|", 0.40, abs(r["slope"]), "V/s", "页面 20 nA 示意值；TI 模型 Ib≈10 nA", v="⚠️")
t, v = wave(r, "drift.txt")
i = np.argmax(np.abs(v) > 13.5)
check("p1 附图第二格", "漂到 13.5 V 用时", 34, t[i], "s", v="⚠️")
check("p1 附图第二格", "最终饱和电压(负向)", -13.5, v[-1], "V", "LM358 输出可接近负轨", v="⚠️")

# --- page3 练习1：Rf·C=1 ms，±2 V 三角波 ---
r = ng.run("diff_tri_idealop.cir", dict(VM=2, FT=1000, TSTOP="6m"))
t, v = wave(r)
check("p3 练习1", "±2 V 1 kHz：输出方波 +幅度(理想运放)", 8.0, v[(t > 4.8e-3) & (t < 4.95e-3)].mean(), "V")
check("p3 练习1", "±2 V 1 kHz：输出方波 −幅度(理想运放)", -8.0, v[(t > 4.3e-3) & (t < 4.45e-3)].mean(), "V")
r = ng.run("diff_tri.cir", dict(VM=2, FT=1000, R1="100", TSTOP="6m"))
t, v = wave(r)
check("p3 练习1", "±2 V 1 kHz：+幅度(LM358B, 加 R1=100Ω 抑振)", 8.0, v[(t > 4.8e-3) & (t < 4.95e-3)].mean(), "V", "假设：R1=100Ω 仅为消除振铃")
r = ng.run("diff_tri.cir", dict(VM=2, FT=2000, R1="100", TSTOP="6m"))
t, v = wave(r); s = t > 3e-3
check("p3 练习1", "±2 V 2 kHz：正向削顶电平(LM358B)", 13.5, v[s].max(), "V")
check("p3 练习1", "±2 V 2 kHz：负向削顶电平(LM358B)", -13.5, v[s].min(), "V")
ng.save()
