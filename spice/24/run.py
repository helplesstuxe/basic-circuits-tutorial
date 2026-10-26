"""24 振荡器：ngspice + TI LM358B / Nexperia 1N4148 官方模型核对。在仓库根目录运行：python spice/24/run.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check


def load(r, name):
    return np.loadtxt(pathlib.Path(r["_dir"]) / name)


def edges(t, y, level, rising=True):
    s = y > level
    idx = np.where((~s[:-1] & s[1:]) if rising else (s[:-1] & ~s[1:]))[0]
    return t[idx] + (level - y[idx]) / (y[idx + 1] - y[idx]) * (t[idx + 1] - t[idx])


def square_stats(t, y, t0):
    k = t > t0
    t, y = t[k], y[k]
    hi, lo = np.percentile(y, 95), np.percentile(y, 5)
    mid = (hi + lo) / 2
    ru, fa = edges(t, y, mid, True), edges(t, y, mid, False)
    T = np.mean(np.diff(ru))
    fa = fa[fa > ru[0]][: len(ru) - 1]
    duty = np.mean(fa - ru[: len(fa)]) / T
    return hi, lo, T, duty


def sine_stats(t, y, t0, t1):
    k = (t > t0) & (t < t1)
    t, y = t[k], y[k]
    zc = edges(t, y, 0.0, True)
    f = (len(zc) - 1) / (zc[-1] - zc[0])
    # 同频率、最小二乘拟合的理想正弦，差值均方根 ÷ 正弦均方根（page3 图24-p3-1 的定义）
    tt = np.linspace(t[0], t[-1], 20000); yy = np.interp(tt, t, y)
    A = np.c_[np.sin(2 * np.pi * f * tt), np.cos(2 * np.pi * f * tt), np.ones_like(tt)]
    c, *_ = np.linalg.lstsq(A, yy, rcond=None)
    fit = A @ c
    dist = np.sqrt(np.mean((yy - fit) ** 2)) / np.sqrt(np.mean((fit - c[2]) ** 2))
    # 另一种读法：理想正弦取「同峰值」振幅（相位同上）
    ph = np.arctan2(c[1], c[0]); pk = (yy.max() - yy.min()) / 2
    ref = pk * np.sin(2 * np.pi * f * tt + ph) + (yy.max() + yy.min()) / 2
    dist2 = np.sqrt(np.mean((yy - ref) ** 2)) / (pk / np.sqrt(2))
    SINE2[0] = dist2
    return np.max(np.abs(y)), y.max(), y.min(), f, dist


SINE2 = [0.0]


print("== 24 振荡器 ==")
# ---- 弛张振荡器 R=10k C=100n
r = ng.run("relax.cir")
d = load(r, "relax.txt"); t = d[:, 0]
hiI, loI, TI, dI = square_stats(t, d[:, 7], 6e-3)
k = t > 6e-3
check("p1 图24-p1-2", "理想运放：上门限(电容最高)", 3.33, d[k, 9].max(), "V")
check("p1 图24-p1-2", "理想运放：下门限(电容最低)", 1.67, d[k, 9].min(), "V")
check("p1/p2 代数", "理想运放：周期 T≈1.39RC", 1.39, TI * 1e3, "ms")
check("p1 图24-p1-2", "理想运放：频率", 721, 1 / TI, "Hz")
check("p1 图24-p1-2", "理想运放：高电平占比", 50, dI * 100, "%")
e = edges(t, d[:, 7], 2.5, False)
check("p1 示波器第1步", "第一次翻转时刻(从 0 V 充到 3.33 V，RC·ln3)", None, e[0] * 1e3, "ms",
      "比稳定后的半周期 0.69 ms 长，与页面描述一致")
hiL, loL, TL, dL = square_stats(t, d[:, 1], 6e-3)
check("p1 示波器第5步 / p3 §LM358B", "LM358B 5 V 单电源：输出高电平", 3.5, hiL, "V")
check("p3 §LM358B", "LM358B：输出低电平", 0.1, loL, "V",
      "输出要吸收约 0.3 mA(电容放电 + 门限电阻)，LM358B 吸电流超过几十 µA 时低电平停在约 0.6 V", v="⚠️")
check("p3 §LM358B", "LM358B：上门限", 2.83, d[k, 3].max(), "V")
check("p3 §LM358B", "LM358B：下门限", 1.70, d[k, 3].min(), "V")
check("p3 图24-p3-2", "LM358B：周期", 1.53, TL * 1e3, "ms")
check("p3 图24-p3-2", "LM358B：高电平占比", 65, dL * 100, "%",
      "低电平不是 0.1 V 而是约 0.6 V，放电变慢，占空比只偏到约 57%；方向正确", v="⚠️")
# ---- R=20k（示波器第 3 步）
r = ng.run("relax.cir", {"R": "20k"})
d = load(r, "relax.txt"); t = d[:, 0]
_, _, T20, _ = square_stats(t, d[:, 7], 8e-3)
check("p1 示波器第3步", "R 换 20k：周期(理想运放)", 2.8, T20 * 1e3, "ms")
_, _, T20L, _ = square_stats(t, d[:, 1], 8e-3)
check("p1 示波器第3步", "R 换 20k：周期(LM358B)", None, T20L * 1e3, "ms", "仍约为 10k 时的 2 倍")
# ---- 例 2：R=10k C=1µF
r = ng.run("relax.cir", {"C": "1u", "TSTOP": "120m", "TSTEP": "5u"})
d = load(r, "relax.txt"); t = d[:, 0]
_, _, T2, _ = square_stats(t, d[:, 7], 40e-3)
check("p2 例2", "R=10k C=1µF 周期(理想)", 13.9, T2 * 1e3, "ms")
check("p2 例2", "R=10k C=1µF 频率(理想)", 72, 1 / T2, "Hz")
# ---- 练习 4：R=75k C=10µF
r = ng.run("relax.cir", {"R": "75k", "C": "10u", "TSTOP": "8", "TSTEP": "200u"})
d = load(r, "relax.txt"); t = d[:, 0]
_, _, T4, _ = square_stats(t, d[:, 7], 2.5)
check("p3 练习4", "R=75k C=10µF 周期(理想)", 1.04, T4, "s")
_, _, T4L, d4L = square_stats(t, d[:, 1], 2.5)
check("p3 练习4", "同上，LM358B 周期", 1.15, T4L, "s")
check("p3 练习4", "同上，LM358B LED 亮的时间占比", 65, d4L * 100, "%",
      "同图24-p3-2", v="⚠️")

# ---- 文氏桥
r = ng.run("wien.cir")
d = load(r, "wien.txt"); t = d[:, 0]
late = (t > 35e-3)
check("p2 代码输出", "Rf=19k(倍数 2.9)：最后 5 ms 峰值", 0.0, np.max(np.abs(d[late, 1])), "V",
      "只剩约 1 mV 失调直流", v="✅")
pkB, hB, lB, fB, distB = sine_stats(t, d[:, 3], 25e-3, 40e-3)
check("p2 图24-p2-3 第2行", "Rf=22k：削顶正峰", 4.0, hB, "V")
check("p2 图24-p2-3 第2行", "Rf=22k：削顶负峰", -4.0, lB, "V")
dist2B = SINE2[0]
pkD, hD, lD, fD, distD = sine_stats(t, d[:, 5], 25e-3, 40e-3)
dist2D = SINE2[0]
check("p2 代码输出 / 图24-p2-3 第3行", "二极管稳幅：稳定峰值", 1.85, pkD, "V",
      "页面用 0.6·tanh 近似二极管；真实 1N4148 在约 0.5 V 就开始导通，幅度更小", v="⚠️")
check("p2 代码输出", "二极管稳幅：振荡频率(理论 1592 Hz，仿真约 1600)", 1592, fD, "Hz")
check("p3 图24-p3-1 左", "无稳幅削顶：频率", 1562, fB, "Hz")
check("p3 图24-p3-1 左", "无稳幅削顶：偏离正弦(最小二乘拟合正弦)", 8.6, distB * 100, "%",
      "LM358B ±5 V 下削顶不对称(+3.8/−4.4 V)，比 ±4 V 对称削顶更难看；趋势与页面一致", v="⚠️")
check("p3 图24-p3-1 左", "无稳幅削顶：偏离正弦(同峰值正弦)", None, dist2B * 100, "%")
check("p3 图24-p3-1 右", "二极管稳幅：偏离正弦(最小二乘拟合正弦)", 2.9, distD * 100, "%",
      "真实二极管 + LM358B 交越失真；仍比削顶小约 4 倍", v="⚠️")
check("p3 图24-p3-1 右", "二极管稳幅：偏离正弦(同峰值正弦)", None, dist2D * 100, "%")
check("p3 图24-p3-1 右", "二极管稳幅：频率", 1589, fD, "Hz")
# 起振时间：第 2 行「大约 4 ms 就长到 ±4 V」
env = np.abs(d[:, 3]); tc = t[np.argmax(env > 0.95 * hB)]
check("p2 图24-p2-3 第2行", "Rf=22k：长到削顶所需时间", 4.0, tc * 1e3, "ms",
      "页面写「大约 4 ms」", v="✅")
# 练习 2：Rf=18k
r = ng.run("wien.cir", {"RFA": "18k"})
d = load(r, "wien.txt"); t = d[:, 0]
check("p3 练习2", "Rf=18k(倍数 2.8)：最后 5 ms 峰值", 0.0, np.max(np.abs(d[t > 35e-3, 1])), "V",
      "不起振", v="✅")
# 练习 1：R=4.7k（三个电路都换 R）
r = ng.run("wien.cir", {"R": "4.7k", "TSTOP": "25m"})
d = load(r, "wien.txt"); t = d[:, 0]
_, _, _, f1, _ = sine_stats(t, d[:, 5], 15e-3, 25e-3)
check("p3 练习1", "R=4.7k：频率(二极管稳幅版)", 3386, f1, "Hz",
      "公式值正确；LM358B 相位延迟使实际频率偏低近 10%，页面练习 3 已提到此现象", v="✅")
ng.save()
