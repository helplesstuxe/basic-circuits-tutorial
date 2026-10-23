"""23 光耦隔离：PC817（LTspice 库模型；Sharp/Everlight 均未提供官方 SPICE 模型）。
CTR 不是模型固定值，而是按页面的 200%/50%/25%（I_F=5 mA、V_CE=5 V）标定模型里的 Igain。
page3 图23-p3-2 过零检测接 220 V 市电，不仿真。在仓库根目录运行：python spice/23/run.py"""
import pathlib, sys, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check
LOWNOTE = "按 5 mA 标定的 CTR 在 0.5 mA 小电流下明显变小（真实 PC817 手册的 CTR–I_F 曲线也是小电流下降），页面按恒定 CTR 算偏乐观"

print("== 23 光耦（PC817）==")


def calib(ctr):
    lo, hi = 1e-6, 1e-1
    for _ in range(40):
        g = math.sqrt(lo * hi)
        c = ng.run("ctrcal.cir", {"IGAIN": f"{g:.6e}"})["CTR"]
        lo, hi = (g, hi) if c < ctr else (lo, g)
    return math.sqrt(lo * hi)


CTRS = {"200%": 2.0, "50%": 0.5, "25%": 0.25}
G = {k: calib(c) for k, c in CTRS.items()}
for k, g in G.items():
    c = ng.run("ctrcal.cir", {"IGAIN": f"{g:.6e}"})
    check("p2 §三 第四步", f"标定：I_F=5 mA、V_CE=5 V 时 CTR={k}", CTRS[k] * 100, c["CTR"] * 100, "%",
          f"Igain={g:.3e}（模型参数，按页面 CTR 标定）", v="ℹ️")
vf = c["VF"]
check("p3 参数表 / p2 §三 第一步", "LED 压降 V_F（5 mA）", 1.2, vf, "V",
      "LTspice 模型 V_F 偏低（手册典型 1.2 V）；只让 I_F 比页面大约 1%～3%", v="✅" if abs(vf / 1.2 - 1) < 0.15 else "⚠️")


def opt(k, **p):
    q = {kk: str(v) for kk, v in p.items()}
    q["IGAIN"] = f"{G[k]:.6e}"
    return ng.run("opto.cir", q)


# ---------- A 部分 ----------
r = opt("50%", RIN="2.2k")
check("p1 图23-p1-3 / p2 图23-p2-1", "12 V / 2.2 kΩ 的 I_F", 4.91, r["IF"] * 1e3, "mA", "模型 V_F 低 0.14 V")
check("p2 第三步", "R_L=4.7 kΩ 饱和需要 I_C=(5−0.2)/4.7k", 1.02, (5 - 0.2) / 4700 * 1e3, "mA", "算术", v="✅")
for k, pv in zip(CTRS, (0.20, 0.20, 0.20)):
    r = opt(k, RIN="2.2k")
    check("p2 A 部分 / p1 图23-p1-3", f"R_in=2.2 kΩ、CTR {k}：输出低电平", pv, r["VOUT"], "V",
          "PC817 手册 V_CE(sat) 典型 0.1 V、最大 0.2 V", v="✅" if r["VOUT"] <= 0.25 else "?")
for k, pv in zip(CTRS, (0.39, 3.85, 4.42)):
    r = opt(k, RIN="22k")
    check("p2 A 部分 / 图23-p2-2", f"R_in=22 kΩ（I_F≈0.49 mA）、CTR {k}：输出", pv, r["VOUT"], "V",
          LOWNOTE, v="✅" if abs(r["VOUT"] / pv - 1) <= 0.1 else "⚠️")
r = opt("50%", RIN="22k")
check("p2 A 部分", "R_in=22 kΩ 的 I_F", 0.49, r["IF"] * 1e3, "mA")

# 图23-p2-2：扫 I_F，读成低电平（<1.5 V）与饱和（≤0.25 V）所需 I_F
for k, (p_lo, p_sat) in zip(CTRS, ((0.37, 0.51), (1.49, 2.04), (2.98, 4.09))):
    c = ng.run("ctrcal.cir", {"IGAIN": f"{G[k]:.6e}"})
    a = np.loadtxt(c["_dir"] + "/sw.dat")
    i, v = a[:, 0], a[:, 1]
    i15 = i[np.argmax(v < 1.5)]
    isat = i[np.argmax(v < 0.25)]
    check("p2 A 部分 图23-p2-2", f"CTR {k}：读成低电平（<1.5 V）所需 I_F", p_lo, i15 * 1e3, "mA",
          "小电流下 CTR 变小，所需电流更大", v="✅" if abs(i15 * 1e3 / p_lo - 1) <= 0.1 else "⚠️")
    check("p2 A 部分 图23-p2-2", f"CTR {k}：降到底（≤0.25 V）所需 I_F", p_sat, isat * 1e3, "mA", "同上",
          v="✅" if abs(isat * 1e3 / p_sat - 1) <= 0.1 else "⚠️")

# ---------- 动手实验（9 V 电池）----------
r = opt("50%", VIN="9", RIN="2.2k")
check("p2 §六 步骤3", "9 V / 2.2 kΩ 的 I_F", 3.55, r["IF"] * 1e3, "mA")
check("p2 §六 步骤3", "按下按钮、CTR 50%：输出（万用表 20 V 档）", 0.2, r["VOUT"], "V", "", v="✅" if r["VOUT"] < 0.25 else "?")
r = opt("50%", VIN="9", RIN="22k")
check("p2 §六 步骤4", "9 V / 22 kΩ 的 I_F", 0.35, r["IF"] * 1e3, "mA")
check("p2 §六 步骤4", "22 kΩ、CTR 50%：输出（页面 4.17 V，拉不下来）", 4.17, r["VOUT"], "V", "结论相同：拉不下来", v="✅")
r = opt("200%", VIN="9", RIN="22k")
check("p2 §六 步骤4", "22 kΩ、CTR 200%：输出（页面 1.67 V）", 1.67, r["VOUT"], "V",
      "0.35 mA 下 CTR 只剩标定值的一半左右；按读数反推 CTR 会低估约一半", v="⚠️")

# ---------- 例题与练习 ----------
r = opt("25%", VIN="24", RIN="6.8k", RL="10k")
check("p2 例1", "24 V / 6.8 kΩ 的 I_F", 3.35, r["IF"] * 1e3, "mA")
check("p2 例1", "CTR 25%、R_L=10 kΩ：输出饱和", 0.2, r["VOUT"], "V", "", v="✅" if r["VOUT"] < 0.25 else "?")
check("p2 例1", "R_in 功耗 I_F²R", 76, r["IF"] ** 2 * 6800 * 1e3, "mW")
G40 = calib(0.4)
r = ng.run("opto.cir", {"VIN": "5", "RIN": "2.2k", "VCC": "3.3", "RL": "4.7k", "IGAIN": f"{G40:.6e}"})
check("p2 例3", "5 V / 2.2 kΩ、CTR 40%、3.3 V 侧：输出（门限 0.99 V）", None, r["VOUT"], "V",
      f"I_F={r['IF']*1e3:.2f} mA；低于 0.99 V 门限", v="✅" if r["VOUT"] < 0.99 else "❌")
r = opt("25%", VIN="12", RIN="2.2k", RL="4.7k")
check("p3 练习1", "I_F≈5 mA、CTR 25%、R_L=4.7 kΩ：输出饱和", 0.2, r["VOUT"], "V", "", v="✅" if r["VOUT"] < 0.25 else "?")
r = opt("25%", VIN="12", RIN="470")
check("p3 练习3", "12 V / 470 Ω 的 I_F", 23.0, r["IF"] * 1e3, "mA")
check("p3 练习3", "470 Ω 电阻功耗", 248, r["IF"] ** 2 * 470 * 1e3, "mW", "模型 V_F 低，电流略大", v=None)
# p3 §一：1 kΩ 上拉、I_F 10 mA、CTR 25% → 2.5 V
r = opt("25%", VIN="12", RIN=f"{(12 - 1.2) / 10e-3:.0f}", RL="1k")
check("p3 §一 第二条", "R_L=1 kΩ、I_F≈10 mA、CTR 25%：输出（页面 2.5 V，落在说不清区）", 2.5, r["VOUT"], "V",
      f"I_F={r['IF']*1e3:.2f} mA；模型 CTR 在 10 mA 比 5 mA 略高；仍落在 1.5～3.0 V 说不清区，结论一致", v="✅")
r = opt("25%", VIN="12", RIN=f"{(12 - 1.2) / 19.2e-3:.0f}", RL="1k")
check("p3 图23-p3-1", "R_L=1 kΩ、I_F=19.2 mA、CTR 25%：能否饱和", 0.2, r["VOUT"], "V", "", v="✅" if r["VOUT"] < 0.3 else "?")

# ---------- B 部分：上升沿 ----------
def rise(rl, k="50%", **p):
    q = {"RL": rl, "IGAIN": f"{G[k]:.6e}"}
    q.update(p)
    rr = ng.run("rise.cir", q)
    a = np.loadtxt(rr["_dir"] + "/rise.dat")
    t, v = a[:, 0], a[:, 1]
    w = t >= 100e-6                      # LED 在 100 μs 熄灭
    t1, v1 = t[w] - 100e-6, v[w]
    v1 = v1[t1 <= 100e-6]; t1 = t1[t1 <= 100e-6]
    vlow = np.interp(99e-6, t, v)         # 熄灭前低电平
    vhi = 5.0
    lv10, lv90 = vlow + 0.1 * (vhi - vlow), vlow + 0.9 * (vhi - vlow)
    def tc(level):
        k_ = np.argmax(v1 >= level)
        return t1[k_] if v1[k_] >= level else float("nan")
    return dict(t3=tc(3.0), tr=tc(lv90) - tc(lv10), v100=v1[-1], tf=None)


RN = ("页面用「1 nF 示意电容、τ=R_L·C」；SPICE 里光敏三极管的集电结电容经米勒效应放大、再加饱和存储时间，"
      "R_L 为几 kΩ 时上升沿慢 4～6 倍。模型在手册条件（R_L=100 Ω、I_C≈2 mA）下 t_r/t_f≈2.9/2.5 μs，比手册典型 4/3 μs 还快，所以真实器件只会更慢")
RISE = {}
for rl, p3, ptr in (("1k", 0.9, 2.2), ("4.7k", 4.1, 10.3), ("10k", 8.8, 22.0), ("47k", 41.1, 103.4)):
    RISE[rl] = rise(rl)
    x = RISE[rl]
    t3 = x["t3"] * 1e6 if x["t3"] == x["t3"] else 100.0
    check("p2 B 部分 图23-p2-3", f"R_L={rl}：LED 熄灭后升到 3.0 V" + ("（100 μs 内没升到，记 >100）" if x["t3"] != x["t3"] else ""),
          p3, t3, "μs", RN, v="⚠️" if rl == "1k" else "❌")
    if x["tr"] == x["tr"]:
        check("p3 图23-p3-1 / p2 B 部分", f"R_L={rl}：10%→90% 上升时间", ptr, x["tr"] * 1e6, "μs", RN + ("；1 kΩ 时 3.0 V 已很快越过，慢的是 90% 前的拖尾，对逻辑影响小" if rl == "1k" else ""), v="⚠️" if rl == "1k" else "❌")
check("p2 B 部分 图23-p2-3", "47 kΩ：熄灭 100 μs 后输出", 4.43, RISE["47k"]["v100"], "V",
      "SPICE 半个周期内连 3.0 V 都没到，5 kHz 下单片机读不到高电平", v="❌")
bit = 1 / 9600
check("p3 练习2", "10 kΩ 上拉：上升时间占 9600 波特一位的比例", 21, RISE["10k"]["tr"] / bit * 100, "%",
      "SPICE 上升时间约 83 μs，占一位的八成，9600 波特已很勉强", v="❌")
for k in ("25%", "200%"):
    x = rise("4.7k", k)
    check("p3 §一 CTR 与关断速度", f"R_L=4.7 kΩ、CTR {k}：升到 3.0 V（对照 CTR 50% 行）", None, x["t3"] * 1e6, "μs",
          "CTR 越高饱和越深、关断越慢，与页面引用 Vishay 应用笔记的说法一致", v="ℹ️")
G100 = calib(1.0)
dd = ng.run("rise.cir", {"VCC": "2", "RL": "100", "RIN": f"{(12 - vf) / 2e-3:.1f}", "IGAIN": f"{G100:.6e}"})
a = np.loadtxt(dd["_dir"] + "/rise.dat"); t, v = a[:, 0], a[:, 1]
vlo = np.interp(99e-6, t, v); sw = 2.0 - vlo
def cr(level, t0, rising):
    w = t > t0; tt, vv = t[w], v[w]
    return tt[np.argmax(vv >= level) if rising else np.argmax(vv <= level)]
t_icfall = cr(vlo + 0.9 * sw, 100e-6, True) - cr(vlo + 0.1 * sw, 100e-6, True)
t_icrise = cr(vlo + 0.1 * sw, 200e-6, False) - cr(vlo + 0.9 * sw, 200e-6, False)
check("p3 参数表 速度", "手册条件 R_L=100 Ω、I_C≈2 mA（CTR 100%）：模型 I_C 上升时间 t_r（手册典型 4 μs）", 4, t_icrise * 1e6, "μs",
      "模型比手册典型快，说明 R_L 几 kΩ 时的慢是电路本身造成的，不是模型夸大", v="ℹ️")
check("p3 参数表 速度", "同上：I_C 下降时间 t_f（手册典型 3 μs）", 3, t_icfall * 1e6, "μs", "同上", v="ℹ️")
check("p3 图23-p3-2", "过零检测接 220 V 市电，不仿真", None, float("nan"), "", "", v="ℹ️")
check("p3 练习5", "4N25：未取得厂家 SPICE 模型，只复核算术（1.06 kΩ、10.8 mA、117 mW）", None, float("nan"), "", "算术无误", v="ℹ️")
ng.save()
