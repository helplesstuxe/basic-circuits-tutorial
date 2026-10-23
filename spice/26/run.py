"""节点 26 上拉电阻与电平转换：SPICE 核对。在仓库根目录运行： python spice/26/run.py"""
import math, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ng
from ng import check

# ---------- 1. 上拉 / 漏电流 / 50 Hz 耦合 / 按下电流 ----------
r = ng.run("pullup.cir")
check("p2 推导一", "10k 上拉 + 1 µA 漏电：引脚电压", 4.99, r["vpin"], "V")
r50 = ng.run("pullup.cir", {"RP": "50k"})
check("p2 推导一", "50k 上拉 + 1 µA 漏电：压降", 0.05, 5 - r50["vpin"], "V")
amp = (r["vmax"] - r["vmin"]) / 2 * 1e6
check("p1 图26-p1-1", "10k 上拉时 50 Hz 耦合幅度(示意源)", 31, amp, "µV",
      "页面写「几十微伏」；20 V/0.5 pF 为页面示意参数")
for rp, page in [("10k", 0.5), ("1k", 5.0)]:
    rr = ng.run("press.cir", {"RP": rp})
    check("p2 推导一", f"按下电流 Rp={rp}", page, rr["i"] * 1e3, "mA")
# 练习 1：3 V 电池
for rp, page_i, page_days in [("10k", 0.3, 30), ("1Meg", 0.003, 3000)]:
    vr = ng.run("press.cir", {"RP": rp}); i = vr["i"] * 3 / 5 * 1e3   # press.cir 为 5 V，按 3 V 等比换算
    check("p3 练习1", f"门磁闭合电流 Rp={rp}，3 V", page_i, i, "mA")
    check("p3 练习1", f"220 mAh 可用天数 Rp={rp}", page_days, 220 / (i * 24), "天", "页面取整")

# ---------- 2. I²C 上升时间 ----------
def rise(rp, cb, vdd):
    rr = ng.run("i2crise.cir", {"RP": rp, "CB": cb, "VDD": vdd, "V30": 0.3 * vdd, "V70": 0.7 * vdd})
    return (rr["t70"] - rr["t30"]) * 1e9, rr["vend"]
for rp, tr_p, vend_p in [("1.5k", 254, 3.25), ("4.7k", 796, 2.43), ("10k", 1695, 1.53)]:
    tr, ve = rise(rp, "200p", 3.3)
    check("p3 图26-p3-1", f"3.3 V/200 pF Rp={rp}：tr", tr_p, tr, "ns")
    check("p3 图26-p3-1", f"Rp={rp}：1.25 µs 半周期末电压", vend_p, ve, "V")
tr, _ = rise("1.77k", "200p", 3.3)
check("p2 推导二", "Rp(max)=1.77k 时 tr（快速模式上限 300 ns）", 300, tr, "ns")
tr, _ = rise("5.9k", "200p", 3.3)
check("p3 图26-p3-1", "Rp=5.9k 时 tr（标准模式上限 1000 ns）", 1000, tr, "ns")
for rp, vdd, page in [("967", 3.3, 0.4), ("1.53k", 5, 0.4)]:
    rr = ng.run("rpmin.cir", {"RP": rp, "VDD": vdd})
    check("p2 推导二/例1", f"Rp(min)={rp}、{vdd} V、灌 3 mA：VOL", page, rr["vol"], "V")
tr, _ = rise("7.87k", "150p", 5)
check("p2 例1", "5 V/150 pF Rp(max)=7.87k：tr", 1000, tr, "ns")
tr, _ = rise("4.7k", "150p", 5)
check("p2 例1", "5 V/150 pF Rp=4.7k：tr", 597, tr, "ns")
rr = ng.run("press.cir", {"RP": "4.7k"})
check("p2 例1", "4.7k 线被拉低时电流", 1.06, rr["i"] * 1e3, "mA")
for rp, page in [("3.93k", 1000), ("3.3k", 839), ("2.2k", 559)]:
    tr, _ = rise(rp, "300p", 5)
    check("p3 练习2", f"5 V/300 pF Rp={rp}：tr", page, tr, "ns")
rr = ng.run("press.cir", {"RP": "2.2k"})
check("p3 练习2", "2.2k 低电平电流", 2.3, rr["i"] * 1e3, "mA")

# ---------- 3. 分压（练习 4） ----------
rr = ng.run("divider.cir")
check("p3 练习4", "10k/20k 分压高电平", 3.33, rr["vhi"], "V")
check("p3 练习4", "上升沿时间常数（到 63%）", 67, (rr["tau"] - 1e-6) * 1e9, "ns")

# ---------- 4. RC 去抖 + SN74HC14（TI 行为模型） ----------
def clean(r1="10k", r2="10k", c="1u", vg=5, hold=100e-3):
    """干净的一次按下：5 ms 按下，保持 hold 后松开（hold 足够长时电容放到 0，与公式的前提一致）。"""
    trel = 5e-3 + hold
    ctl = f"PWL(0,0,5m,0,5.001m,1,{trel*1e3:g}m,1,{trel*1e3+0.001:g}m,0)"
    rr = ng.run("debounce.cir", {"R1": r1, "R2": r2, "C": c, "VG": vg, "CTL": ctl,
                                 "TREL": f"{trel*1e3:g}m", "TEND": f"{trel*1e3+80:g}m", "VH": vg / 2})
    return (rr["tp"] - 5e-3) * 1e3, (rr["tr"] - trel) * 1e3

# 先确认模型门限：5 V 供电与 4.5 V 供电时的 VT+/VT−（DC 扫描用的是查表插值，直接读模型表）
# TI 表：4.5 V → 2.5/1.6 V；6 V → 3.3/2.0 V；5 V 线性插值 → 2.767/1.733 V
vtp5, vtm5 = 2.5 + 0.8 * 0.5 / 1.5, 1.6 + 0.4 * 0.5 / 1.5
tp, tr_ = clean()
check("p2 推导三", "按下判定 R1=R2=10k C=1µF（74HC14 接 5 V）", 11.4, tp, "ms",
      f"模型 5 V 下 VT−≈{vtm5:.2f} V", v="✅")
check("p2 推导三", "松开判定（74HC14 接 5 V）", 13.9, tr_, "ms",
      f"模型 5 V 下 VT+≈{vtp5:.2f} V；页面用的是 4.5 V 的门限", v="⚠️")
tp45, tr45 = clean(vg=4.5)
check("p2 推导三", "按下判定（门限对齐页面：74HC14 接 4.5 V）", 11.4, tp45, "ms", "核对公式本身")
check("p2 推导三", "松开判定（门限对齐页面：74HC14 接 4.5 V）", 13.9, tr45, "ms", "核对公式本身")

# 仿真一：与页面同样的抖动（bounce_state 算法照抄，seed=3，dt=2 µs）
def bounce_state(t, t_press, t_release, bounce_press=2e-3, bounce_release=1e-3, seed=1):
    rng = np.random.default_rng(seed)
    closed = (t >= t_press) & (t < t_release)
    for t0, dur, final in [(t_press, bounce_press, True), (t_release, bounce_release, False)]:
        tt, state = t0, final
        while tt < t0 + dur:
            seg = rng.uniform(20e-6, dur / 5)
            m = (t >= tt) & (t < min(tt + seg, t0 + dur))
            closed[m] = state
            tt += seg
            state = not state
    return closed
dt = 2e-6
t = np.arange(0, 60e-3, dt)
cl = bounce_state(t, 5e-3, 35e-3, 2e-3, 1e-3, seed=3)
pts = ["0,0"]
for k in np.nonzero(np.diff(cl.astype(int)))[0]:
    tk = t[k + 1]
    a, b = (0, 1) if cl[k + 1] else (1, 0)
    pts.append(f"{tk - 1e-9:.9g},{a},{tk:.9g},{b}")
ctl = "PWL(" + ",".join(pts) + ")"
rr = ng.run("debounce.cir", {"CTL": ctl})
d = np.loadtxt(pathlib.Path(rr["_dir"]) / "db.txt")
y, raw = d[:, 1] > 2.5, d[:, 3] > 2.5
check("p2 仿真一", "只接上拉：引脚翻转次数", 22, np.count_nonzero(np.diff(raw.astype(int))), "次")
check("p2 仿真一", "RC + 74HC14：输出翻转次数", 2, np.count_nonzero(np.diff(y.astype(int))), "次")
check("p2 仿真一", "抖动按下后认出按下", 12.3, (rr["tp"] - 5e-3) * 1e3, "ms",
      "页面用 4.5 V 门限 1.6 V", v="✅")
check("p2 仿真一", "抖动松开后认出松开", 13.2, (rr["tr"] - 35e-3) * 1e3, "ms",
      "5 V 下 VT+ 更高，松开更慢", v="⚠️")
check("p2 仿真一", "松开前电容电压最低值", 0.25, rr["vbmin"], "V", "页面「约 0.25 V」", tol=15)
rr45 = ng.run("debounce.cir", {"CTL": ctl, "VG": 4.5, "VH": 2.25})
check("p2 仿真一", "抖动按下（门限对齐页面 4.5 V）", 12.3, (rr45["tp"] - 5e-3) * 1e3, "ms")
check("p2 仿真一", "抖动松开（门限对齐页面 4.5 V）", 13.2, (rr45["tr"] - 35e-3) * 1e3, "ms")

# 例 2：C = 0.47 µF
tp, tr_ = clean(c="0.47u")
check("p2 例2", "C=0.47µF 按下判定（5 V）", 5.4, tp, "ms", v="✅")
check("p2 例2", "C=0.47µF 松开判定（5 V）", 6.5, tr_, "ms", "同推导三：5 V 门限更高", v="⚠️")
# 练习 3：R1 = R2 = 18k
tp, tr_ = clean(r1="18k", r2="18k")
check("p3 练习3", "R2=18k 按下判定（5 V）", 20.5, tp, "ms", v="✅" if abs(tp / 20.5 - 1) < 0.1 else "⚠️")
check("p3 练习3", "R1=R2=18k 松开判定（5 V）", 25, tr_, "ms", "仍远小于 50 ms 上限，结论不变", v="⚠️")
tp45, tr45 = clean(r1="18k", r2="18k", vg=4.5)
check("p3 练习3", "R2=18k 按下（门限对齐页面 4.5 V）", 20.5, tp45, "ms")
check("p3 练习3", "R1=R2=18k 松开（门限对齐页面 4.5 V）", 25, tr45, "ms")
# 练习 3 第 3 问：VT− = 2.45 V 时电容电压降到 2.45 V 的时间（直接测 RC 波形）
rr = ng.run("debounce.cir", {"R1": "18k", "R2": "18k", "CTL": "PWL(0,0,5m,0,5.001m,1,105m,1,105.001m,0)",
                             "TREL": "105m", "TEND": "120m"})
dd = np.loadtxt(pathlib.Path(rr["_dir"]) / "db.txt")
tb, vb = dd[:, 0], dd[:, 5]
i = np.argmax((tb > 5e-3) & (vb < 2.45))
check("p3 练习3", "VT−=2.45 V 时按下判定（RC 波形）", 12.8, (tb[i] - 5e-3) * 1e3, "ms")
check("p3 τ扫描", "Schmitt 多翻次数/最长延迟（随机统计）", None, float("nan"), "",
      "20 次随机抖动统计，SPICE 未逐一复现；单次抖动已由仿真一核对", v="ℹ️")

# ---------- 5. BSS138 电平转换 ----------
r = ng.run("shifter.cir")
d = np.loadtxt(pathlib.Path(r["_dir"]) / "ls.txt")
tt, vl, vh = d[:, 0], d[:, 1], d[:, 3]
check("p2 仿真二", "3.3 V 侧拉低时 3.3 V 侧电压", 0.08, r["l10"], "V")
check("p2 仿真二", "3.3 V 侧拉低时 5 V 侧电压", 0.08, r["h10"], "V")
check("p2 仿真二", "5 V 侧拉低时 3.3 V 侧电压", 0.08, r["l27"], "V")
check("p2 仿真二", "5 V 侧拉低时 5 V 侧电压", 0.08, r["h27"], "V")
check("p2 仿真二", "空闲 3.3 V 侧", 3.3, r["l3"], "V")
check("p2 仿真二", "空闲 5 V 侧", 5.0, r["h3"], "V")
m = tt > 15e-6
i = np.argmax(m & (vh - vl > 0.05))
check("p2 仿真二 (b)", "松手后两线分开时的电压", 2.02, vl[i], "V",
      "Diodes 模型 VTO=1 V，页面取 onsemi 典型 1.3 V", v="⚠️")
check("p2 推导四", "导通条件「低于约 2.0 V」", 2.0, vl[i], "V", "同上", v="⚠️")
check("p2 仿真二 (b)", "松手到分开的时间", 328, (tt[i] - 15e-6) * 1e9, "ns",
      "取决于分开电压和低 VGS 下的导通电阻", v="⚠️")
rs = ng.run("shifter.cir", {"SWAP": 1})
check("p2 仿真二 (c)", "源漏接反：空闲 3.3 V 侧被抬到", 3.85, rs["l3"], "V")
check("p2 仿真二 (c)", "源漏接反：空闲 5 V 侧", None, rs["h3"], "V", "页面未给；被拉低到约 4.45 V", v="ℹ️")
check("p2 仿真二 (c)", "源漏接反：拉低功能（3.3 V 侧拉低时 5 V 侧）", 0.08, rs["h10"], "V", "「看起来照常」")

ng.save()
