"""26 H 桥电机驱动。在仓库根目录运行：python spice/26/run.py
- DRV8871 没有 SPICE 模型（TI 只在 DRV8871-Q1 产品页挂了 DRV8876-Q1 的 PSpice 模型 SLVMCQ2A，不是同一颗芯片，未使用）。
  桥臂用 ngspice 理想开关（Ron 取页面的 DRV8871 典型值 0.307/0.258 Ω）+ 通用体二极管；电机用页面参数的等效电路。
- 死区扫描：页面自己的示意模型原样搬进 SPICE（shoot.cir）；另用 Infineon IRLZ44N 官方模型搭真实半桥（halfbr.cir）核对“1 µs 量级”。"""
import pathlib, sys, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ng
from ng import check

print("== 26 H 桥电机驱动 ==")
NAN = float("nan")
RPM = 60 / (2 * math.pi)
VM, R, L, KE, J, B, RHS, RLS = 12.0, 2.0, 1e-3, 0.02, 1e-5, 1e-5, 0.307, 0.258
SW = "理想开关 + 通用体二极管（无 DRV8871 模型），电机参数同页面"

# ---------- page1 图26-p1-3 ----------
r = ng.run("seq.cir")
check("p1 图26-p1-3 第1条", "正转稳定转速", 5377, r["WFULL"], "rpm", SW)
check("p1 图26-p1-3 第1条", "起动电流峰值", 4.56, r["ISTART"], "A")
check("p1 图26-p1-3 第1条", "约 0.25 s 后稳定（升到 98%）", 0.25, r["T98"], "s", "SPICE 0.23 s 到 98%，“约 0.25 s”合理", tol=15)
check("p1 图26-p1-3 第2条", "滑行 0.3 s 后转速", 3988, r["WCOAST"], "rpm")
check("p1 图26-p1-3 第2条", "刹车 0.2 s 后转速", 184, r["WBRAKE"], "rpm")
check("p1 图26-p1-3 第2条", "刹车电流", -4.36, r["IBRAKE"], "A",
      "SPICE 里电流大时体二极管和下管并联分流，回路电阻略小，电流大 2%")
check("p1 图26-p1-3 第3条", "刹车后反转的电流峰值", -4.71, r["IREV"], "A")
check("p1 图26-p1-3 第3条", "反转最终转速", -5383, r["WEND"], "rpm")

# ---------- page2 PWM ----------
def avg_model(d):
    rr = R + d * (RHS + RLS) + (1 - d) * 2 * RLS
    w = KE * d * VM / (rr * B + KE ** 2)
    return w, B * w / KE
pw = {}
for d, rpm, rip in ((0.25, 1346, 0.113), (0.5, 2690, 0.150), (0.75, 4034, 0.113)):
    pw[d] = q = ng.run("pwm.cir", {"D": d, "EXTRA": ""})
    check("p2 图26-p2-2 第1条", f"20 kHz、占空比 {d:.0%} 稳定转速", rpm, q["WAVG"], "rpm", SW)
    check("p2 图26-p2-2 / 推导二", f"占空比 {d:.0%} 电流纹波（峰峰）", rip, q["IMAX"] - q["IMIN"], "A")
for d, p in ((0.25, 1347), (0.5, 2694), (0.75, 4039)):
    check("p2 图26-p2-2 第1条", f"平均模型 {d:.0%}（对照 SPICE PWM 结果）", p, pw[d]["WAVG"], "rpm",
          "SPICE 逐周期开关的结果和页面平均模型差 0.2% 以内")
check("p2 推导二 / 例1", "50% 时电机两端平均电压（A−B）", 6.0, pw[0.5]["VAVG"], "V",
      "SPICE 量的是 A、B 两点，含一点开关导通压降；电机反电动势平均值和页面一致")
check("p2 例1", "50% 时稳定电流", 0.144, pw[0.5]["IAVG"], "A")
check("p2 例2", "75% 时平均电压", 9.0, pw[0.75]["VAVG"], "V")
check("p2 例2", "75% 时稳定电流（0.216 A）", 0.216, pw[0.75]["IAVG"], "A")
check("p2 推导一", "12 V 全速约 563 rad/s", 563, r["WFULL"] / RPM, "rad/s")

# ---------- page2 图26-p2-3 刹车 / 滑行 ----------
w0, i0 = avg_model(1.0)
check("p2 图26-p2-3", "全速初值", 5384, w0 * RPM, "rpm", "页面平均模型 D=1，SPICE 以此为初值")
br = ng.run("stop.cir", {"MODE": 1, "W0": f"{w0:.5g}", "I0": f"{i0:.5g}"})
co = ng.run("stop.cir", {"MODE": 0, "W0": f"{w0:.5g}", "I0": f"{i0:.5g}"})
check("p2 推导三 / 图26-p2-3", "刹车降到 10% 的时间", 136, br["T10"] * 1e3, "ms")
check("p2 推导三", "刹车时间常数 τ（= 降到 10% 时间 / 2.3）", 59, br["T10"] / math.log(10) * 1e3, "ms")
check("p2 图26-p2-3", "刹车电流峰值", -4.36, br["IMIN"], "A", "同 p1：体二极管分流，大 2%")
check("p2 图26-p2-3", "刹车电流约 2 ms 达到峰值", 2.0, br["TMIN"] * 1e3, "ms")
check("p2 图26-p2-3", "滑行 2 s 后剩余转速比例", 14, co["WEND"] / w0 * 100, "%")
check("p2 推导三 / 图26-p2-3", "滑行时电流经体二极管降到 0（快衰减）", 11, co["TZERO"] * 1e6, "µs",
      "通用二极管电流变小时压降低于 0.8 V，下降略慢；页面写“约”，数量级正确", tol=15)

# ---------- page3 扫描二：频率 ----------
wi, ii = avg_model(0.5)
for f, p in ((500, 4.06), (1e3, 2.67), (2e3, 1.46), (5e3, 0.60), (10e3, 0.30), (20e3, 0.15), (50e3, 0.060)):
    T = 0.06
    q = ng.run("pwm.cir", {"F": f, "D": 0.5, "TSTOP": T, "TA": T - 5 / f, "W0": f"{wi:.5g}", "I0": f"{ii:.5g}",
                           "MAXSTEP": f"{1/f/400:.3g}", "EXTRA": ""})
    check("p3 扫描二 频率表", f"{f/1e3:g} kHz、50% 电流纹波", p, q["IMAX"] - q["IMIN"], "A")
    if f == 1e3:
        check("p3 图26-p3-2 第1条", "1 kHz 电流最低点", -1.2, q["IMIN"], "A")
        check("p3 图26-p3-2 第1条", "1 kHz 电流最高点", 1.5, q["IMAX"], "A")
        check("p3 图26-p3-2 第1条", "1 kHz 平均电流", 0.14, q["IAVG"], "A")

# ---------- page3 扫描一：死区 ----------
SN = "页面示意模型（200 ns 线性过渡、25 mΩ、20 nH）原样搬进 SPICE，只核对页面算得对不对"
for td, ip, e in ((0, 59.7, 91.5), (50, 45.2, 51.9), (100, 30.4, 23.3), (150, 15.3, 5.95)):
    q = ng.run("shoot.cir", {"TDEAD": f"{td}n"})
    check("p3 扫描一 死区表", f"死区 {td} ns 直通峰值", ip, q["IPK"], "A", SN)
    check("p3 扫描一 死区表", f"死区 {td} ns 每次能量", e, q["E"] * 1e6, "µJ")
    pw_ = {0: 3.66, 50: 2.08, 100: 0.93, 150: 0.24}[td]
    check("p3 扫描一 死区表 / 练习2", f"死区 {td} ns、20 kHz 每半桥功率", pw_, q["E"] * 2 * 20e3, "W")
for td in (200, 250):
    q = ng.run("shoot.cir", {"TDEAD": f"{td}n"})
    check("p3 扫描一 死区表 / 练习2", f"死区 {td} ns 直通峰值", 0, q["IPK"], "A")
hb = {td: ng.run("halfbr.cir", {"TDEAD": f"{td}u"}) for td in (0, 0.5, 1.0, 1.5)}
check("p3 扫描一 文字", "IRLZ44N 半桥、100 Ω 栅阻：死区 1 µs 时直通峰值", None, hb[1.0]["IPK"], "A",
      f"官方模型：死区 0 / 0.5 / 1.0 / 1.5 µs 时峰值 {hb[0]['IPK']:.0f} / {hb[0.5]['IPK']:.1f} / {hb[1.0]['IPK']:.1f} / {hb[1.5]['IPK']:.2f} A；"
      "“死区要留到 1 µs 量级”成立（要到约 1.5 µs 才基本消失）", v="✅")

# ---------- 只做算术 / 无模型 ----------
check("p3 限流电阻", "起动电流 12/2.565", 4.7, 12 / 2.565, "A", "算术；SPICE 起动峰值 4.56 A（电感限制了上升）")
check("p3 参数表", "DRV8871 VM、Ipeak、tDEAD、ILIM、IOCP 等手册值", None, NAN, "", "无 DRV8871 SPICE 模型，手册数值不仿真", v="ℹ️")
check("p3 限流表 / 练习1", "R_ILIM = 64 kV / I_TRIP 各列", None, NAN, "", "纯算术（15k→4.27 A … 43k→1.49 A，核算无误）", v="ℹ️")
check("p3 练习3", "0.5 mH、0.2 A 纹波所需频率 30 kHz", None, 12 * 0.25 / (0.5e-3 * 0.2) / 1e3, "kHz", "纯算术", v="ℹ️")
ng.save()
