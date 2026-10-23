"""18 互锁：低压（12 V 继电器）版正反转控制回路。在仓库根目录运行：python spice/18/run.py
380 V 主电路与电动机不仿真（市电）；「相间短路」= KM1、KM2 主触点同时闭合。"""
import math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check

TAU = 10e-3
COLS = ["N1", "N2", "E1", "E2", "D1", "D2", "B1", "B2", "Ec1", "Ec2", "Dc1", "Bc1", "Q1", "Q2"]


def pwl(iv):
    pts = [(0, 0)]
    for t0, t1 in iv:
        pts += [(t0, 0), (t0 + 1e-5, 1), (t1, 1), (t1 + 1e-5, 0)]
    return " ".join(f"{a:.6g} {b:.6g}" for a, b in pts)


def thr(tp, td):
    vp, vd = 1 - math.exp(-tp / TAU), math.exp(-td / TAU)
    return f"{(vp + vd) / 2:.5f}", f"{(vp - vd) / 2:.5f}"


def run(p, tp1=20e-3, td1=10e-3, tp2=20e-3, td2=10e-3):
    full = dict(SB1="0 0", SB2="0 0", SB3="0 0", SB4="0 0", WELD="0 0", TSTOP="9")
    full["VT1"], full["VH1"] = thr(tp1, td1)
    full["VT2"], full["VH2"] = thr(tp2, td2)
    full.update(p)
    r = ng.run("interlock.cir", full)
    d = np.loadtxt(pathlib.Path(r["_dir"]) / "il.txt")
    t = d[:, 0]
    return t, {n: d[:, 1 + 2 * i] for i, n in enumerate(COLS)}


def at(t, y, x):
    return np.interp(x, t, y) > 0.5


def overlap(t, a, b):
    m = (a > 0.5) & (b > 0.5)
    return float(np.sum(np.diff(t)[m[:-1]]))


def state(t, y, X, x):
    return ("吸" if at(t, y[X + "1"], x) else "放") + "/" + ("吸" if at(t, y[X + "2"], x) else "放")


print("== 18 互锁（低压 12 V 继电器版）==")
P = dict(SB2=pwl([(1.0, 1.3), (5.000, 5.300)]),
         SB3=pwl([(2.0, 2.3), (4.0, 4.3), (5.005, 5.305)]),
         SB1=pwl([(3.0, 3.3), (4.6, 4.9), (7.0, 7.3)]))
t, y = run(P)
page = {"N": ["吸/放", "吸/吸", "放/放", "放/吸", "吸/吸"],
        "E": ["吸/放", "吸/放", "放/放", "放/吸", "吸/放"],
        "D": ["吸/放", "放/吸", "放/放", "放/吸", "放/放"]}
names = {"N": "不互锁", "E": "接触器互锁", "D": "双重互锁"}
for X in "NED":
    for x, want in zip((1.5, 2.5, 3.5, 4.4, 5.5), page[X]):
        s = state(t, y, X, x)
        check("p2 代码输出 图18-p2-2", f"{names[X]} t={x} s KM1/KM2 页面「{want}」", None, 1.0 if s == want else 0.0, "",
              f"SPICE：{s}", v="✅" if s == want else "❌")
ov = {X: overlap(t, y[X + "1"], y[X + "2"]) * 1e3 for X in "NED"}
check("p2 代码输出", "不互锁：两只同时吸合总时长", 2975, ov["N"], "ms")
check("p2 代码输出", "接触器互锁：同时吸合总时长", 0, ov["E"], "ms", v="✅" if ov["E"] == 0 else "❌")
check("p2 代码输出", "双重互锁：同时吸合总时长", 0, ov["D"], "ms", v="✅" if ov["D"] == 0 else "❌")
# 竞赛（图18-p2-3）
k = (t > 4.99)
on1 = t[k][np.argmax(y["E1"][k] > 0.5)]
check("p2 图18-p2-3", "竞赛：KM1 吸合时刻", 5.020, on1, "s")
m = (t > 5.0) & (t < 5.1) & (y["Ec2"] > 6)
w2 = np.sum(np.diff(t)[m[:-1]]) * 1e3
check("p2 图18-p2-3", "竞赛：KM2 线圈白白通电时长", 15, w2, "ms")
# 双重互锁换向空档
k = t > 2.0
off = t[k][np.argmax(y["D1"][k] < 0.5)]
sw = t[k][np.argmax(y["D2"][k] > 0.5)]
check("p2 §双重互锁", "2 s 按 SB3：KM1 释放时刻", 2.010, off, "s")
check("p2 §双重互锁", "KM2 吸合时刻", 2.030, sw, "s")
check("p2 §双重互锁", "换向空档", 20, (sw - off) * 1e3, "ms")
check("p2 例1", "正转中按反转(接触器互锁)：KM1/KM2", None, 1.0, "", f"SPICE：{state(t, y, 'E', 2.2)}",
      v="✅" if state(t, y, "E", 2.2) == "吸/放" else "❌")

# ---- page3 §1：只做按钮互锁的换向空档（2 s 按 SB3）
P1 = dict(SB2=pwl([(1.0, 1.3)]), SB3=pwl([(2.0, 2.3)]), TSTOP="2.5")
for tp2, td1, pg in ((12e-3, 19e-3, -7), (17e-3, 19e-3, -2), (22e-3, 4e-3, 18), (15e-3, 18e-3, -3)):
    t, y = run(P1, td1=td1, tp2=tp2)
    k = t > 2.0
    off = t[k][np.argmax(y["B1"][k] < 0.5)]
    on = t[k][np.argmax(y["B2"][k] > 0.5)]
    where = "p3 练习1" if pg == -3 else "p3 图18-p3-1"
    check(where, f"按钮互锁：KM2 吸合 {tp2*1e3:.0f} ms、KM1 释放 {td1*1e3:.0f} ms 的空档", pg, (on - off) * 1e3, "ms",
          f"两只同时闭合 {overlap(t, y['B1'], y['B2'])*1e3:.1f} ms", tol=10)
    if pg == -3:
        tD = t[k][np.argmax(y["D2"][k] > 0.5)] - t[k][np.argmax(y["D1"][k] < 0.5)]
        check("p3 练习1", "改成双重互锁后的空档(=KM2 吸合时间)", 15, tD * 1e3, "ms")

# ---- page3 §2：KM1 0.8 s 熔焊，1.0 s 按停止，1.6 s 按反转
P2 = dict(SB2=pwl([(0.2, 0.5)]), WELD=pwl([(0.8, 3.0)]), SB1=pwl([(1.0, 1.3)]), SB3=pwl([(1.6, 1.9)]), TSTOP="2.5")
t, y = run(P2)
check("p3 图18-p3-2", "按钮互锁：熔焊后按反转，KM2 是否吸合(页面：吸合，短路)", None, 1.0, "",
      f"SPICE：KM2 {'吸合' if at(t, y['B2'], 2.2) else '释放'}，同时闭合 {overlap(t, y['B1'], y['B2']):.2f} s",
      v="✅" if at(t, y["B2"], 2.2) else "❌")
check("p3 图18-p3-2", "双重互锁：熔焊后按反转，KM2 是否吸合(页面：一直断开)", None, 0.0, "",
      f"SPICE：KM2 {'吸合' if at(t, y['D2'], 2.2) else '释放'}", v="✅" if not at(t, y["D2"], 2.2) else "❌")
reon = (y["Dc1"][(t > 1.35) & (t < 1.55)] > 6).any()
check("p3 图18-p3-2", "松开停止后 KM1 线圈重新通电(自锁触点也粘住)", None, 1.0 if reon else 0.0, "",
      "SPICE：" + ("重新通电" if reon else "未通电"), v="✅" if reon else "❌")

# ---- page3 练习4：顺序控制
P4 = dict(SB4=pwl([(0.5, 0.8)]), SB2=pwl([(1.0, 1.3)]), SB3=pwl([(2.0, 2.3)]))
P4["SB4"] = pwl([(0.5, 0.8), (2.5, 2.8)])
P4["SB1"] = pwl([(3.5, 3.8)])
P4["TSTOP"] = "4.2"
t, y = run(P4)
for x, want, why in [(0.7, 0, "KM1 未吸合时按 M2 启动：KM2 不吸"), (1.5, 0, "M1 启动后 M2 仍停（需再按 SB4）"),
                     (3.0, 1, "M1 运行中按 SB4：KM2 吸合"), (4.0, 0, "M1 停止：M2 跟着停")]:
    s = at(t, y["Q2"], x)
    check("p3 练习4", why, None, float(s), "", f"SPICE：KM2 {'吸' if s else '放'}", v="✅" if s == bool(want) else "❌")
ng.save()
