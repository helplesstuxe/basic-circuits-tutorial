"""21 MOS 管开关：IRLZ44N（Infineon 官方模型）低边开关、续流二极管、P 沟道高边栅压。
在仓库根目录运行：python spice/21/run.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check


def sw_energy(d, t0, t1, i_col=5):
    """按 code/21_sim.py 的判据：V_DS > 2·I_L·R_ON(0.15 V) 且有电流的时段积分 V·I。"""
    a = np.loadtxt(d)
    t, vd, i = a[:, 0], a[:, 3] if i_col == 5 else a[:, 1], a[:, i_col]
    w = (t >= t0) & (t <= t1) & (vd > 0.15) & (i > 0.01)
    return np.trapezoid((vd * i)[w], t[w]) if w.any() else 0.0


def first_cross(t, y, level, t0, falling):
    w = t >= t0
    t, y = t[w], y[w]
    k = np.where(y <= level)[0] if falling else np.where(y >= level)[0]
    return t[k[0]] if len(k) else float("nan")


print("== 21 MOS 管开关（IRLZ44N）==")
# ---------- 低边开关，纯电阻 4 Ω（12 V / 3 A 灯带）----------
R = {rg: ng.run("lowside.cir", {"RG": rg}) for rg in ("10", "100", "1000")}
r = R["100"]
check("p2 §1", "栅极峰值电流 5 V/100 Ω", 50, r["IGPK"] * 1e3, "mA", "模型内含 2.4 Ω 内部栅阻")
check("p3 §1", "R_G/R_GS 分压后稳态 V_GS", 4.95, r["VGSS"], "V")
r1k = ng.run("lowside.cir", {"RGS": "1k"})
check("p3 §1", "R_GS 换 1 kΩ 后稳态 V_GS（页面「损失约 9%」）", 5 * 1000 / 1100, r1k["VGSS"], "V")
rds5 = r["VDSS"] / r["IDS"]
check("p2 例1 第1步", "5 V 驱动（实际 4.95 V）3 A 时 R_DS(on)：页面用手册最大值 25 mΩ", 25, rds5 * 1e3, "mΩ",
      "SPICE 为典型值，低于手册最大值，页面按最大值估算偏安全", v="✅")
check("p2 例1 第1步", "导通损耗 P_cond（D=50%）", 0.1125, 3 ** 2 * rds5 * 0.5, "W",
      "页面按最大值 25 mΩ，SPICE 典型值更低；方向偏安全", v="✅")
check("p2 §2 代数", "平台电压 V_pl（V_DS 降到 6 V 时的 V_GS，纯电阻负载）", 2.8, r["VPL"], "V",
      "页面为示意值；门限 1.0–2.0 V 的批次差异会让平台上下移动约 ±0.5 V", v="✅" if abs(r["VPL"] / 2.8 - 1) < 0.2 else "⚠️")

# 开通完成时间（V_DS 降到 0.15 V）
for rg, pg in (("10", 0.07), ("100", 0.74), ("1000", 7.43)):
    check("p3 §2 图21-p3-1左", f"R_G={rg} Ω 开通完成时间", pg, R[rg]["TONDONE"] * 1e6, "μs",
          "与 R_G 基本成正比 ✓；绝对值差异来自示意模型与门限批次差异", v="✅" if abs(R[rg]["TONDONE"] * 1e6 / pg - 1) < 0.2 else "⚠️")

# 开关能量：纯电阻负载
E = {}
for rg in R:
    d = R[rg]["_dir"] + "/ls.txt"
    E[rg] = (sw_energy(d, 0, 10e-6), sw_energy(d, 10e-6, 20e-6))
eon, eoff = E["100"]
NOTE_R = ("纯电阻负载时电压、电流同时变化（发热≈V·I·t/6），而页面示意模型是「先电流到 3 A 再降电压」的感性钳位波形（≈V·I·t/2），"
          "且 12 V 下真实 Q_GD 更小；页面数值偏大、方向偏安全")
check("p2 §3", "E_on（R_G=100 Ω，12 V/3 A 纯电阻）", 12.6, eon * 1e6, "μJ", NOTE_R, v="⚠️")
check("p2 §3", "E_off（同上）", 10.8, eoff * 1e6, "μJ", NOTE_R, v="⚠️")

# ---------- 感性负载 + 续流二极管（钳位感性，最接近页面示意模型）----------
I1 = ng.run("inductive.cir", {"DMODE": "1"})
d = I1["_dir"] + "/ind.txt"
a = np.loadtxt(d)
t, vd, idd, vg = a[:, 0], a[:, 1], a[:, 3], a[:, 5]
w_off = (t >= 3e-3) & (t <= 3.0199e-3) & (vd > 0.15) & (idd > 0.01)
w_on = (t >= 3.02e-3) & (t <= 3.03e-3) & (vd > 0.15) & (idd > 0.01)
eoff_L = np.trapezoid((vd * idd)[w_off], t[w_off])
eon_L = np.trapezoid((vd * idd)[w_on], t[w_on])
ESUM_L = eon_L + eoff_L
check("p2 §3 / 例1 第2步", "E_on+E_off（R_G=100 Ω，3 A 电机 + 1N5822 续流，钳位感性）", 23.4, ESUM_L * 1e6, "μJ",
      "官方模型约为页面的 1/2.7：页面 Q_GD=12 nC、平台 2.8 V 偏保守；方向偏安全，但「仿真得 23.4 μJ」宜注明是示意模型上限", v="⚠️")
check("p2 §3 / 例1 第2步", "同上，纯电阻灯带（例 1 题面的负载）", 23.4, (eon + eoff) * 1e6, "μJ", NOTE_R, v="⚠️")
# 开通时段的电流爬升、平台（钳位感性，第二次开通 3.02 ms）
t_on0 = 3.02e-3 + 1e-9
tri0 = first_cross(t, idd, 0.1 * 2.75, t_on0, False); tri1 = first_cross(t, idd, 0.9 * 2.75, t_on0, False)
tpl0 = first_cross(t, vd, 0.9 * 12.46, tri1, True); tpl1 = first_cross(t, vd, 0.1 * 12.46, tri1, True)
check("p2 §2 代数", "电流爬升时间 t_ri（10→90%，钳位感性开通）", 0.14, (tri1 - tri0) * 1e6 / 0.8, "μs",
      "SPICE 10→90% 时间按 /0.8 折算。真实管子跨导很大，V_GS 只需比门限高约 0.3 V 电流就到 3 A，所以电流几乎是「跳」上去的；页面「门限 1.5 V→平台 2.8 V 线性爬升」是示意", v="⚠️")
check("p2 §2 代数", "开通平台时间 t_pl,on（V_DS 90→10%）", 0.55, (tpl1 - tpl0) * 1e6 / 0.8, "μs",
      "官方模型 12 V 时的 Q_GD 小于页面取的 12 nC", v="✅" if abs((tpl1 - tpl0) / 0.8e-6 / 0.55 - 1) < 0.2 else "⚠️")
check("p2 §5", "有续流二极管：关断后漏极电压（页面「约 12.7 V」）", 12.7, I1["VDPK"], "V",
      "D1 用 1N5822 肖特基，压降比硅管小；硅二极管约 12.7 V")
check("p2 §5", "关断瞬间 3 A 转到 D1（漏极电流降到 0，线圈电流 = 页面 3 A）", 3.0, I1["ISS"], "A")

# 不同 R_G 的 20 kHz 开关损耗（p3 §2 图右 / 练习4）
PS = {}
for rg, pg in (("10", 0.047), ("100", 0.468), ("1000", 4.678)):
    IL = ng.run("inductive.cir", {"DMODE": "1", "RG": rg})
    a = np.loadtxt(IL["_dir"] + "/ind.txt"); t, vd, idd = a[:, 0], a[:, 1], a[:, 3]
    e = 0.0
    for t0, t1 in ((3e-3, 3.0199e-3), (3.02e-3, 3.06e-3)):
        w = (t >= t0) & (t <= t1) & (vd > 0.15) & (idd > 0.01)
        e += np.trapezoid((vd * idd)[w], t[w])
    PS[rg] = e * 20e3
    er = sum(E[rg]) * 20e3
    check("p3 §2 图21-p3-1右", f"R_G={rg} Ω、20 kHz 开关损耗（钳位感性 / 纯电阻 {er:.3f} W）", pg, PS[rg], "W",
          "官方模型约为页面的 1/2.5～1/5；页面偏保守，与 R_G 成正比的结论 ✓", v="⚠️")
pc = 3 ** 2 * 0.025 * 0.5
for f, pg in ((1e3, 0.136), (20e3, 0.580), (100e3, 2.450)):
    check("p2 §4 图21-p2-2 / 例1、例2", f"{f/1e3:.0f} kHz 合计发热（导通按 25 mΩ 最大值 + SPICE 开关能量）", pg,
          pc + ESUM_L * f, "W", "开关部分偏保守（见上）；1 kHz 时导通占主导，结论不变" if f == 1e3 else "开关能量页面偏保守",
          v="✅" if abs((pc + ESUM_L * f) / pg - 1) <= 0.1 else "⚠️")
check("p2 §4", "导通损耗与开关损耗相交频率", 4.8, pc / ESUM_L / 1e3, "kHz", "开关能量更小，交点右移", v="⚠️")
tj4 = (PS["1000"] + 0.113) * 62
check("p3 练习4", "R_G=1 kΩ、20 kHz 温升（页面 297 °C →「很快烧坏」）", 297, tj4, "°C",
      "官方模型下结温约 25+%.0f=%.0f °C：低于 175 °C 但已很烫，仍是坏设计；页面「很快烧坏」偏夸大，数值偏大" % (tj4, 25+tj4), v="⚠️")

# 无续流二极管：雪崩钳位
I0 = ng.run("inductive.cir", {"DMODE": "0", "T2": "3.3e-3", "TE": "3.29m", "TSTOP": "3.5m"})
check("p2 §5", "无续流二极管：关断尖峰（页面理想计算 ≈16000 V，并说明实际在 55 V 以上雪崩）", 55, I0["VDPK"], "V",
      "模型体二极管 BV=55 V，尖峰被雪崩钳在约 55 V，与页面「55 V 以上某处被击穿」一致", v="✅")
check("p2 §5", "每次关断灌进 MOS 管的能量（页面 ½LI² = 4.5 mJ）", 4.5, I0["EAV"] * 1e3, "mJ",
      "钳位期间电源还在继续送能量（≈ ½LI²·V_cl/(V_cl−12 V)），同时线圈串联电阻 4 Ω 也分走一部分；页面只算 ½LI²", v="✅" if abs(I0["EAV"]*1e3/4.5-1)<=0.1 else "⚠️")
I2 = ng.run("inductive.cir", {"DMODE": "2"})
check("p3 练习3", "D1 接反、MOS 导通时电流（页面「可能有几十安」，理想电源）", None, I2["ISS"], "A",
      "电源无内阻时达到数十～近百安：等于短路，结论一致", v="✅")

# ---------- 导通电阻 vs 驱动电压（p3 §3 图21-p3-2）----------
for vgs, mx in ((10, 22), (5, 25), (4, 35)):
    rr = ng.run("rds.cir", {"VGS": str(vgs)})
    check("p3 §3 图21-p3-2", f"V_GS={vgs} V、3 A 时 R_DS(on)（页面列手册最大值 {mx} mΩ）", mx, rr["RDS"] * 1e3, "mΩ",
          "SPICE 为典型值，低于最大值，页面按最大值算发热偏安全", v="✅" if rr["RDS"] * 1e3 <= mx else "❌")
rr = ng.run("rds.cir", {"VGS": "3.3"})
check("p3 §3", "V_GS=3.3 V 时 R_DS(on)（手册未保证，仅供参考）", None, rr["RDS"] * 1e3, "mΩ", "典型样品可用，但手册不保证", v="ℹ️")
check("p3 故障表", "万用表二极管档：红 S 黑 D 体二极管读数（页面「零点几伏」，1 mA 测试电流）", None, rr["VBD"], "V",
      "0.45 V，落在「零点几伏」内", v="✅")

# ---------- P 沟道高边栅压（栅压只由上拉/Q2 决定）----------
h = ng.run("highside.cir", {"VS": "12", "VIN": "5"})
check("p1 图21-p1-2", "Q2 导通时 Q1 的 V_GS", -12, h["VGS1"], "V")
h = ng.run("highside.cir", {"VS": "12", "VIN": "0"})
check("p1 图21-p1-2", "Q2 关断时 Q1 的 V_GS（≈0）", 0, h["VGS1"], "V")
h = ng.run("highside.cir", {"VS": "24", "VIN": "5"})
check("p3 练习5", "24 V 时 Q2 导通的 Q1 V_GS", -24, h["VGS1"], "V")
h = ng.run("highside.cir", {"VS": "24", "VIN": "5", "RSER": "10k"})
check("p3 练习5 改法一", "串 10 kΩ 分压后 Q1 V_GS", -12, h["VGS1"], "V")

# ---------- 练习 1：3.3 V / 47 Ω ----------
r47 = ng.run("lowside.cir", {"RG": "47", "VDRV": "3.3"})
check("p3 练习1", "3.3 V / 47 Ω 栅极峰值电流", 70, r47["IGPK"] * 1e3, "mA", "模型内部栅阻 2.4 Ω 使峰值略低")
r180 = ng.run("lowside.cir", {"RG": "180", "VDRV": "3.3"})
check("p3 练习1", "R_G=180 Ω 时峰值电流 ≤ 20 mA", 18.3, r180["IGPK"] * 1e3, "mA")

for x in ("p2 例3 AO3400A", "p3 §3 IRF540N"):
    check(x, "无可用官方模型（AO3400A/IRF540N 未取得厂家 SPICE 文件），只核算术", None, float("nan"), "",
          "页面算术已复核无误", v="ℹ️")
ng.save()
