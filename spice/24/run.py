"""24 隔离电源与数字隔离器。在仓库根目录运行：python spice/24/run.py
- 变压器方案只仿真次级低压侧（初级接 220 V 市电，不仿真）；二极管用 Diodes Inc. 1N4007 官方模型。
- NME0505SC：Murata 没有 SPICE 模型，模块用页面同一个示意公式（行为源）；稳压管钳位用 Diodes Inc. 1N4733A 官方模型。
- ISO7721：TI 官方 PSpice Transient Model（SLLM474）。
- 光耦对照：页面数字来自 TI 白皮书的“通用光耦”，这里用 PC817（LTspice 库模型）作参照。"""
import pathlib, sys, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check

print("== 24 隔离电源与数字隔离器 ==")
NAN = float("nan")

# ---------- A 变压器次级 + 桥式整流 ----------
N = 220 / 12
def bridge(vrms, **kw):
    q = {"VRMS": f"{vrms:.5f}"}; q.update(kw)
    return ng.run("bridge.cir", q)
r = bridge(12)
check("p2 §一 第2条", "12 V 有效值次级的峰值", 16.97, r["VPK"], "V")
NOTE_D = "1N4007 在 10 kΩ 轻载、1000 μF 下每只压降约 0.74 V，和页面取 0.7 V 一致"
check("p2 §二 图24-p2-1 / 图24-p2-2", "N1/N2=18.33、电网正常：整流滤波后最高电压", 15.57, r["VMAX"], "V", NOTE_D)
r = bridge(12 * 0.9)
check("p2 §二 图24-p2-2", "电网低 10%：整流后", 13.87, r["VMAX"], "V")
r = bridge(12 * 1.1)
check("p2 §二 图24-p2-2", "电网高 10%：整流后", 17.27, r["VMAX"], "V")
r = bridge(12, RLOAD="150")
check("p2 §二（补充）", "同一电路带 100 mA 负载（150 Ω）：最高 / 最低电压", None, r["VMAX"], "V",
      f"带载后二极管峰值电流大、压降变大，并出现纹波（最低 {r['VMIN']:.2f} V）；页面说“最高电压”，按轻载理解没问题", v="ℹ️")
n1 = math.sqrt(2) * 220 / 10.4
r = bridge(220 / n1)
check("p2 例1", f"N1/N2≈{n1:.1f}（次级 {220/n1:.2f} V）：整流后", 9.0, r["VMAX"], "V")
r = bridge(242 / n1)
check("p2 例1", "电网高 10%：整流后", 10.0, r["VMAX"], "V")
for v, p, d in ((9, 11.33, "额定"), (8.1, 10.06, "电网低 10%"), (9.9, 12.60, "电网高 10%")):
    r = bridge(v)
    check("p3 练习4", f"9 V 次级、{d}：整流后", p, r["VMAX"], "V")
check("p2 图24-p2-1 初级", "220 V 市电初级、保险丝：不仿真", None, NAN, "", "市电部分，按任务要求跳过", v="ℹ️")

# ---------- B 不稳压模块 + 假负载 / 稳压管 ----------
def mod(mode, iuser, vin=5):
    return ng.run("module.cir", {"MODE": mode, "IUSER": f"{iuser:.6g}", "VIN": vin})
MNOTE = "模块是页面自己的示意模型（Murata 无 SPICE 模型），这一行只核对页面的解是否算对"
check("p2 §五 B / 图24-p2-4", "满载 200 mA 输出", 5.00, mod(0, 0.2)["VOUT"], "V", MNOTE)
check("p2 §五 B / 图24-p2-4", "10% 负载 20 mA 输出", 5.61, mod(0, 0.02)["VOUT"], "V", MNOTE)
check("p2 §三 / 图24-p2-4", "只用 4.7 mA、不处理", 10.05, mod(0, 4.7e-3)["VOUT"], "V", MNOTE)
check("p3 参数表 线性调整率", "输入 5.5 V、空载", 11.25, mod(0, 0, vin=5.5)["VOUT"], "V", MNOTE)
r = mod(1, 4.7e-3)
check("p2 §三 假负载 / p3 图24-p3-2", "4.7 mA + 270 Ω：输出", 5.58, r["VOUT"], "V", MNOTE)
check("p2 §三 假负载", "270 Ω 功耗", 115, r["VOUT"] ** 2 / 270 * 1e3, "mW")
check("p3 §四 第2条", "4.7 mA 时假负载电流", 20.7, r["IDUM"] * 1e3, "mA")
check("p2 §三 假负载", "留给现场侧的电流（200 mA − 假负载）", 179, (0.2 - r["IDUM"]) * 1e3, "mA")
r = mod(1, 0.1)
check("p3 §四 第3条 / 练习3", "100 mA + 270 Ω：输出", 5.27, r["VOUT"], "V", MNOTE)
check("p3 §四 第3条 / 练习3", "100 mA 时假负载电流", 19.5, r["IDUM"] * 1e3, "mA")
ZN = "1N4733A 官方模型在 5.0～5.3 V 的拐点区比页面线性化（4.76 V + 7 Ω）电流小：电压几乎不变，但支路电流少 17%～54%，稳压管方案比页面说的更省电"
r = mod(2, 4.7e-3)
check("p3 §四 第2条 / 图24-p3-2", "4.7 mA + 36 Ω + 1N4733A：输出", 5.59, r["VOUT"], "V")
check("p3 §四 第2条 / 练习3", "4.7 mA 时稳压管支路电流", 19.3, r["IZ"] * 1e3, "mA", ZN, v="⚠️")
r = mod(2, 0.1)
check("p3 §四 第3条 / 图24-p3-2", "100 mA + 稳压管：输出", 5.29, r["VOUT"], "V")
check("p3 §四 第3条 / 练习3", "100 mA 时稳压管支路电流", 12.4, r["IZ"] * 1e3, "mA", ZN, v="⚠️")
r = mod(2, 0.18)
check("p3 §四 第3条", "180 mA + 稳压管：输出", 5.04, r["VOUT"], "V")
check("p3 §四 第3条", "180 mA 时稳压管支路电流", 6.7, r["IZ"] * 1e3, "mA", ZN, v="⚠️")

# ---------- C ISO7721 ----------
r = ng.run("iso.cir")
INOTE = "TI 官方模型；在手册 6～17 ns 范围内（典型 11 ns）"
check("p3 参数表 传输延时", "ISO7721 t_PLH（5 V、15 pF）", 11, r["TPLH"] * 1e9, "ns", INOTE,
      v="✅" if 6e-9 <= r["TPLH"] <= 17e-9 else "❌")
check("p3 参数表 传输延时", "ISO7721 t_PHL（5 V、15 pF）", 11, r["TPHL"] * 1e9, "ns", INOTE,
      v="✅" if 6e-9 <= r["TPHL"] <= 17e-9 else "❌")
check("p1 图24-p1-2", "5 kHz 方波经 ISO7721：输出高电平", 5.0, r["VHI"], "V", "与输入几乎重合")

# ---------- D 光耦对照（PC817 代替白皮书的“通用光耦”）----------
lo, hi = 1e-6, 1e-1
for _ in range(40):
    g = math.sqrt(lo * hi)
    c = ng.run("ctrcal.cir", {"IGAIN": f"{g:.6e}"})["CTR"]
    lo, hi = (g, hi) if c < 1.0 else (lo, g)
G100 = math.sqrt(lo * hi)
ONOTE = "页面数字取自 TI 白皮书的“通用光耦”，型号、I_F 都没给；这里用 PC817、I_F≈5 mA、CTR 100% 作参照，只作量级参考；PC817 在这个条件下比白皮书的数字快，页面“光耦跟不上 115200”的结论不受影响"
def opto(rl):
    rr = ng.run("rise.cir", {"VIN": "5", "RIN": "790", "RL": rl, "IGAIN": f"{G100:.6e}"})
    a = np.loadtxt(rr["_dir"] + "/rise.dat"); t, v = a[:, 0], a[:, 1]
    w = t > 100e-6; tr = t[w][np.argmax(v[w] >= 2.5)] - 100e-6
    w = t > 200e-6; tf = t[w][np.argmax(v[w] <= 2.5)] - 200e-6
    return tr, tf, np.interp(199.9e-6, t, v)
tr, tf, v200 = opto("1.9k")
check("p1 §四 图24-p1-2", "通用光耦 1.9 kΩ 上拉：输出拉低（过 2.5 V）", 0.5, tf * 1e6, "μs", ONOTE, v="ℹ️")
check("p1 §四 图24-p1-2", "通用光耦 1.9 kΩ 上拉：回升过 2.5 V", 40, tr * 1e6, "μs", ONOTE, v="ℹ️")
check("p1 §四 图24-p1-2", "熄灭 100 μs 后（下一个脉冲前）的电压", 4.07, v200, "V", ONOTE, v="ℹ️")
check("p3 故障表 115200 行", "白皮书“100 Ω 上拉时约 3 µs”", None, NAN, "", "白皮书条件下的数字（I_F 远大于 5 mA），本轮不另设电路复核", v="ℹ️")

# ---------- 只做算术的行 ----------
check("p1 §四 / p2 §五 C", "最高数据率：光耦 1/(4×40 μs)、ISO7721 1/(4×17 ns)", None, NAN, "",
      "6.25 kbps、14.7 Mbps 算术无误；不是电路量", v="ℹ️")
check("p2 例2", "NME0512SC 假负载 1.5 kΩ：8.52 mA、0.109 W", None, NAN, "", "算术无误（无 NME0512SC 模型）", v="ℹ️")

ng.save()
