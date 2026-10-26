"""07 三极管开关与继电器驱动：2N3904（onsemi）+ SRD-05VDC 线圈（70 Ω + 0.1 H 示意电感）+ 1N4148（Nexperia）/1N4749A（Diodes）。
220 V 触点侧不仿真（市电）。在仓库根目录运行：python spice/07/run.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check

print("== 07 三极管继电器驱动（2N3904）==")


def tran(params):
    r = ng.run("relay.cir", params)
    a = np.loadtxt(r["_dir"] + "/tr.dat")
    return r, a[:, 0], a[:, 1], a[:, 3]


T0 = 10e-3
# ---------- A 部分：饱和检查 ----------
r, t, il, vc = tran({"RB": "680", "DMODE": "1"})
check("p2 §2 第一步", "I_C(max) = 4.8/70（SPICE 为实际 I_C）", 68.6, r["IC"] * 1e3, "mA",
      "SPICE 的 V_CE(sat) 为 0.27 V，比 0.2 V 稍大，I_C 略小")
check("p2 例1 / A 部分", "5 V 引脚、R_B=680 Ω 的 I_B", 6.32, r["IB"] * 1e3, "mA", "模型 V_BE≈0.87 V（大电流饱和），比 0.7 V 高")
check("p2 动手 步骤2", "680 Ω 时 V_CE（万用表 20 V 档）", 0.2, r["VCE"], "V",
      "0.27 V 仍在手册 ≤0.3 V（50 mA/5 mA）内；页面写「0.2 V 左右」合适", v="✅")
check("p1 图07-p1-2", "开到底时线圈拿到的额定电压比例", 96, r["VCOIL"] / 5 * 100, "%")
check("p1 图07-p1-2 / A 部分", "开到底时三极管功耗 V_CE·I_C", 13.7, r["VCE"] * r["IC"] * 1e3, "mW",
      "SPICE V_CE(sat)=0.27 V（手册上限 0.3 V → 20.6 mW），在器件公差内；远小于 625 mW", v="✅")
check("p1 图07-p1-2 / A 部分", "另加基极功耗 I_B·V_BE 后的总功耗（页面未计）", None, r["PQ"] * 1e3, "mW", "基极再加约 5 mW，不影响结论", v="ℹ️")
check("p2 §2", "饱和裕量 β_forced 下 I_B/I_C(max)/30 倍数", 2.8, r["IB"] / (r["IC"] / 30), "倍")

r3 = ng.run("relay.cir", {"RB": "470", "VPIN": "3.3", "DMODE": "1", "TSTOP": "10.1m"})
check("p2 例2", "3.3 V 引脚、R_B=470 Ω 的 I_B", 5.53, r3["IB"] * 1e3, "mA")
check("p2 例2", "3.3 V、470 Ω 时 V_CE（饱和）", 0.2, r3["VCE"], "V", "在手册 ≤0.3 V 内", v="✅")
r3b = ng.run("relay.cir", {"RB": "680", "VPIN": "3.3", "DMODE": "1", "TSTOP": "10.1m"})
check("p2 例2", "3.3 V 引脚仍用 680 Ω 的 I_B", 3.82, r3b["IB"] * 1e3, "mA", "V_BE 比 0.7 V 高，实际更小", v=None, tol=15)

r10 = ng.run("relay.cir", {"RB": "10k", "DMODE": "1", "TSTOP": "10.1m"})
beta = r10["IC"] / r10["IB"]
check("p2 A 部分 / 动手 步骤3", "R_B=10 kΩ：SPICE 典型 2N3904 的等效 β", 100, beta, "",
      "页面说结果「看运气」，β 在 30～300 之间都可能；典型模型落在中间", v="ℹ️")
check("p2 A 部分 β=100 行", "R_B=10 kΩ 时 V_CE（页面 β=100 → 1.99 V）", 1.99, r10["VCE"], "V",
      "模型 β≈78，与页面 β=100 那一行同属「半开」，结论一致：线圈电压不够", v="✅")
check("p2 A 部分 β=100 行", "R_B=10 kΩ 时线圈电压比例（页面 60%，<75% 吸不上）", 60, r10["VCOIL"] / 5 * 100, "%",
      "同上，结论一致", v="✅")
check("p2 A 部分", "R_B=10 kΩ 半开时三极管功耗（页面 β=100 → 85.6 mW）", 85.6, r10["PQ"] * 1e3, "mW",
      "接近放大区最坏值 89 mW", v="✅")
check("p2 A 部分", "放大区最坏功耗 V_CC²/(4R)", 89.3, r10["PQ"] * 1e3, "mW", "SPICE 半开点 V_CE=2.7 V 正好接近 V_CC/2", v="✅")
check("p3 练习3", "10 kΩ 时 β≈100（SPICE 典型管 β 见上一行）", 100, beta, "", "练习是反推题，算术无误", v="ℹ️")

# ---------- 图07-p3-1 扫 R_B ----------
rbv = 100 * 10 ** (np.arange(121) / 40)
pct = np.array([ng.run("sweep.cir", {"RB": f"{x:.4g}"})["PCT"] for x in rbv])
k = np.where(pct < 75)[0][0]
rb75 = np.interp(75, [pct[k], pct[k - 1]], [rbv[k], rbv[k - 1]])
check("p3 图07-p3-1", "左端平台（饱和时线圈电压比例）", 96, pct[0], "%")
check("p3 图07-p3-1", "跌破 75% 的 R_B（SPICE 典型管；页面三条线 2.41/8.03/24.08 kΩ）", None, rb75 / 1e3, "kΩ",
      "典型管在 50 mA 附近 β≈60，拐点落在页面 β=30 与 β=100 两条线之间，图的结论成立", v="ℹ️")
check("p3 图07-p3-1", "680 Ω 离典型管拐点的倍数（页面「好几倍」）", None, rb75 / 680, "倍", "", v="✅")

# ---------- B 部分：关断 ----------
I0 = np.interp(T0 - 1e-6, t, il)
check("p2 B 部分", "关断前线圈电流", 68.6, I0 * 1e3, "mA")
check("p2 B 部分", "线圈储能 ½LI²", 0.235, 0.5 * 0.1 * I0 ** 2 * 1e3, "mJ", "L=0.1 H 为页面示意值")

r0 = ng.run("relay.cir", {"DMODE": "0", "TSTOP": "10.02m", "TMAX": "1n"})
a = np.loadtxt(r0["_dir"] + "/tr.dat")
t0, v0 = a[:, 0], a[:, 3]
check("p2 图07-p2-2", "无二极管：集电极尖峰（100 pF 杂散）", 2170, r0["VPK"], "V",
      "SPICE 的 Gummel-Poon 模型不含击穿，所以和页面一样“冲到两千多伏”；页面已说明真实电路会在 40 V 以上先击穿", v="✅")
tpk = t0[np.argmax(v0)] - T0
check("p2 图07-p2-2", "尖峰出现时刻", 5.0, tpk * 1e6, "μs", "2N3904 自身 C_ob 并在 100 pF 上，谐振稍慢")

for mode, vpage, tpage, name in (("1", 5.7, 2.17, "只有二极管 1N4148"), ("2", 29.7, 0.23, "二极管 + 24 V 稳压管 1N4749A")):
    rr, t, il, vc = tran({"DMODE": mode, "TSTOP": "16m"})
    w = (t > T0 + 2e-6) & (t < T0 + 50e-6)
    vcl = np.median(vc[w])
    check("p2 图07-p2-3 右", f"{name}：集电极钳位电压", vpage, vcl, "V",
          "1N4148 在 68 mA 时 V_F≈0.86 V（页面取 0.7 V）" if mode == "1" else "1N4749A 在 68 mA 时 V_Z 比标称 24 V 高")
    k = np.where((t > T0) & (il < 0.1 * 5 / 70))[0][0]
    trel = t[k] - T0
    check("p2 图07-p2-3 左", f"{name}：电流降到 7.14 mA 用时", tpage, trel * 1e3, "ms",
          "二极管压降比 0.7 V 大，电流掉得稍快" if mode == "1" else "")
    if mode == "1":
        t1 = trel
    else:
        check("p2 图07-p2-3", "加稳压管后快几倍", 9.7, t1 / trel, "倍")

# ---------- 例 3 / 练习 2 / 练习 4 ----------
e3 = ng.run("relay.cir", {"RCOIL": "55", "RB": "560", "DMODE": "1", "TSTOP": "10.1m"})
check("p2 例3", "55 Ω 线圈的 I_C(max)", 87.3, e3["IC"] * 1e3, "mA")
check("p2 例3", "560 Ω 给的 I_B", 7.68, e3["IB"] * 1e3, "mA", "V_BE 比 0.7 V 高")
check("p2 例3", "560 Ω 时 V_CE（饱和）", 0.2, e3["VCE"], "V", "87 mA 下仍饱和，在手册 ≤0.3 V（50 mA）附近", v="✅" if e3["VCE"] < 0.4 else "⚠️")
x2 = ng.run("relay.cir", {"VCC": "12", "RCOIL": "400", "RB": "1.5k", "VPIN": "3.3", "DMODE": "2", "TSTOP": "16m"}, )
check("p3 练习2", "12 V/400 Ω 的 I_C", 29.5, x2["IC"] * 1e3, "mA")
check("p3 练习2", "3.3 V、1.5 kΩ 给的 I_B", 1.73, x2["IB"] * 1e3, "mA", "V_BE 比 0.7 V 高")
check("p3 练习2", "V_CE（饱和）", 0.2, x2["VCE"], "V", "", v="✅" if x2["VCE"] < 0.3 else "⚠️")
check("p3 练习4", "12 V 继电器 + 24 V 稳压管关断钳位（≤40 V）", 36.7, x2["VPK"], "V",
      "电感沿用 0.1 H 示意值；钳位电压只取决于 V_CC+V_F+V_Z，与电感无关")
check("p3 练习5", "ULN2003A：TI 不提供 SPICE 模型，只核算术 82%/78%/91%", None, float("nan"), "",
      "算术复核无误", v="ℹ️")
ng.save()
