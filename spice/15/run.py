"""15 星三角：低压控制回路 + 低压等比例三相关系。在仓库根目录运行：python spice/15/run.py
380 V 主电路和电动机不仿真（市电）。"""
import math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check

TAU = 10e-3


def thr(tp, td):
    vp, vd = 1 - math.exp(-tp / TAU), math.exp(-td / TAU)
    return f"{(vp + vd) / 2:.5f}", f"{(vp - vd) / 2:.5f}"


def pwl(iv):
    pts = [(0, 0)]
    for t0, t1 in iv:
        pts += [(t0, 0), (t0 + 1e-5, 1), (t1, 1), (t1 + 1e-5, 0)]
    return " ".join(f"{a:.6g} {b:.6g}" for a, b in pts)


def run(p, tpD=20e-3, tdY=10e-3):
    full = dict(SB1="0 0", SB2=pwl([(0.5, 0.8)]), TSTOP="7.5", TSET="6", SHORTY="0")
    full["VTM"], full["VHM"] = thr(20e-3, 10e-3)
    full["VTY"], full["VHY"] = thr(20e-3, tdY)
    full["VTD"], full["VHD"] = thr(tpD, 10e-3)
    full.update(p)
    r = ng.run("stardelta.cir", full)
    d = np.loadtxt(pathlib.Path(r["_dir"]) / "sd.txt")
    t = d[:, 0]
    return t, dict(M=d[:, 1], Y=d[:, 3], D=d[:, 5], KT=d[:, 7], cY=d[:, 9], cD=d[:, 11])


def first(t, m):
    return float(t[np.argmax(m)]) if m.any() else float("nan")


def ovl(t, a, b):
    m = (a > 0.5) & (b > 0.5)
    return float(np.sum(np.diff(t)[m[:-1]]))


print("== 15 星三角（低压控制回路）==")
t, y = run({})
tM, tY = first(t, y["M"] > 0.5), first(t, y["Y"] > 0.5)
tYoff = first(t, (y["Y"] < 0.5) & (t > 1))
tD = first(t, y["D"] > 0.5)
tKT = first(t, (y["KT"] < 6) & (t > 1))
tKTdone = first(t, y["cY"] < 6) if False else first(t, (y["cY"] < 6) & (t > 1))
check("p2 §三 [时序]", "KM 吸合时刻", 0.520, tM, "s")
check("p2 §三 [时序]", "KMY 吸合时刻（星形启动）", 0.520, tY, "s")
check("p2 §三 [时序]", "KT 到时（KMY 线圈断电时刻）", 6.500, tKTdone, "s")
check("p2 §三 [时序] 图15-p2-5", "KMY 释放时刻", 6.510, tYoff, "s")
check("p2 §三 [时序] 图15-p2-5", "KM△ 吸合时刻", 6.530, tD, "s")
check("p2 §三 [时序] 图15-p2-5", "切换空档", 20, (tD - tYoff) * 1e3, "ms")
check("p2 §三 [时序]", "KT 线圈断电复位时刻", 6.530, tKT, "s")
o = ovl(t, y["Y"], y["D"])
check("p2 §三 结论1", "KMY、KM△ 同时吸合时长", 0, o * 1e3, "ms", v="✅" if o == 0 else "❌")
check("p3 关键参数表", "切换空档 = KM△ 吸合时间（仿真里 20 ms）", 20, (tD - tYoff) * 1e3, "ms")
# 步骤 3：按 SB1 全灭，KT 复位，再按 SB2 重复
t, y = run(dict(SB1=pwl([(7.5, 7.8)]), SB2=pwl([(0.5, 0.8), (8.5, 8.8)]), TSTOP="15"))
off = all(y[k][(t > 7.7) & (t < 8.4)].max() < 0.5 for k in "MYD")
check("p2 §五 步骤3", "按 SB1：三只全灭", None, float(off), "", "SPICE：" + ("全灭" if off else "未全灭"), v="✅" if off else "❌")
kt0 = y["KT"][(t > 7.7) & (t < 8.4)].max()
check("p2 §五 步骤3", "按 SB1 后 KT 线圈电压（复位）", 0, kt0, "V", v="✅" if kt0 < 0.1 else "❌")
tY2 = first(t, (y["Y"] < 0.5) & (t > 9))
tD2 = first(t, (y["D"] > 0.5) & (t > 9))
check("p2 §五 步骤3", "再按 SB2(8.5 s)：KMY 释放时刻 8.5+6+0.01", 14.510, tY2, "s")
check("p2 §五 步骤3", "再按 SB2：KM△ 吸合时刻", 14.530, tD2, "s")
# 动手实验第 4 步：短接 KMY 常闭（页面时间 20/10 ms）
t, y = run(dict(SHORTY="1"))
tYoff = first(t, (y["Y"] < 0.5) & (t > 1)); tD = first(t, y["D"] > 0.5)
o = ovl(t, y["Y"], y["D"])
check("p2 §五 步骤4", "短接 KMY 常闭（tpick 20 ms、tdrop 10 ms）：空档", None, (tD - tYoff) * 1e3, "ms",
      f"同时吸合 {o*1e3:.1f} ms：照页面的 20/10 ms 不会出现「一起亮」；只有吸合比释放快时才会重叠", v="⚠️")
# page3 练习 2：KM△ 吸合 12 ms、KMY 释放 19 ms
t, y = run(dict(SHORTY="1"), tpD=12e-3, tdY=19e-3)
tYoff = first(t, (y["Y"] < 0.5) & (t > 1)); tD = first(t, y["D"] > 0.5)
check("p3 练习2", "去掉 KMY 常闭：空档（负 = 重叠）", -7, (tD - tYoff) * 1e3, "ms",
      f"重叠 {ovl(t, y['Y'], y['D'])*1e3:.1f} ms")
t, y = run({}, tpD=12e-3, tdY=19e-3)
tYoff = first(t, (y["Y"] < 0.5) & (t > 1)); tD = first(t, y["D"] > 0.5)
check("p3 练习2", "装回 KMY 常闭：空档 = KM△ 吸合时间", 12, (tD - tYoff) * 1e3, "ms")

print("== 19 三相关系（相电压 12 V 等比例缩小）==")
r = ng.run("threephase.cir", {"VPH": "12"})
s3 = math.sqrt(3)
check("p1 图15-p1-1", "星形每段电压 / 线电压（页面 219/380）", 219 / 380, r["VPY"] / r["VLL"], "")
check("p1 图15-p1-1", "三角形每段电压 / 线电压（页面 380/380）", 1.0, r["VPD"] / r["VLL"], "")
check("p2 图15-p2-1", "相电压峰值 / 有效值（页面 311/220）", 311 / 220, r["VPA"] / 12, "")
check("p2 图15-p2-1", "两相之差峰值 / 单相峰值（√3）", s3, r["VPAB"] / r["VPA"], "")
dt = ((r["TB"] - r["TA"]) % 0.02) * 1e3
check("p2 图15-p2-1", "L2 比 L1 晚（50 Hz）", 6.67, dt, "ms")
check("p2 §二 推导", "I_L,Y / I_L,Δ", 1 / 3, r["ILY"] / r["ILD"], "")
check("p2 §二 推导", "I_L,Δ / I_ph,Δ", s3, r["ILD"] / r["IPD"], "")
check("p2 例题1", "星形绕组电流 / 三角形绕组电流（页面 46.7/80.8≈0.577）", 0.577, r["ILY"] / r["IPD"], "")
check("p2 例题1", "按比例换算星形启动线电流（直接启动 140 A）", 46.7, 140 * r["ILY"] / r["ILD"], "A")
check("p2 例题2", "按比例换算星形启动线电流（直接启动 80 A）", 26.7, 80 * r["ILY"] / r["ILD"], "A")
check("p3 练习1", "按比例换算星形启动线电流（直接启动 180 A）", 60, 180 * r["ILY"] / r["ILD"], "A")
check("p3 练习4", "Y 接法电机绕组额定电压 380/√3（按仿真比值）", 219, 380 * r["VPY"] / r["VLL"], "V")
check("p3 关键参数表", "星形时间经验公式 2√13.2+4（算术）", 11.3, 2 * math.sqrt(1.732 * 0.38 * 20) + 4, "s", "纯算术，非 SPICE")
check("p2 §三/p1 图15-p1-2", "示意电动机的 5.8 倍/1.9 倍/2.6 倍/0.83 倍、转速 91% 等", None, float("nan"), "",
      "未仿真：页面自己声明是参数编造的示意模型，且属于 380 V 电动机；1/3 比例已由上面的三相电路核对", v="ℹ️")
check("p3 图15-p3-1/15-p3-2", "T 扫描、空档扫描的尖峰倍数与转速", None, float("nan"), "", "未仿真：同上，示意电动机模型", v="ℹ️")
ng.save()
