"""19 星三角降压启动：除 19_sim.py 那两张以外的所有配图，以及正文、练习要用到的数字。运行：python code/figs/19_figs.py
图上出现的每个数字都由本脚本打印（fs.mark 自动打印；其余用 print）。电动机模型与 19_sim.py 相同（示意值）。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from schem import *
import figstyle as fs

P = "19"
U_LINE = 380.0
U_PH_Y = U_LINE / np.sqrt(3)

# ---------------- 与 19_sim.py 相同的示意电动机 ----------------
R1, R2, X, XM = 0.03, 0.03, 0.16, 3.0
S_N, J = 0.03, 2.0
def i_rotor(s): return 1 / (R1 + R2 / s + 1j * X)
def i_line(s): return abs(1 / (1j * XM) + i_rotor(s))
def torque(s): return abs(i_rotor(s)) ** 2 * R2 / s
I_N, T_N = i_line(S_N), torque(S_N)
def load(w): return 0.1 + 0.75 * w ** 2
DT = 1e-3


def run(t_star, gap, t_end=None):
    """理想切换：0 ~ t_star 星形，空档 gap 秒（<0 表示重叠，按短路处理，不算电动机），之后三角形。
    返回 (切换前电流, 切换后尖峰, 切换时转速, 空档内转速下降量)。"""
    t_end = t_end or t_star + max(gap, 0) + 1.0
    w = 0.0; n = int(round(t_end / DT)); I = np.zeros(n); W = np.zeros(n)
    for k in range(n):
        tk = k * DT; s = max(1 - w, 1e-4)
        f = 1 / 3 if tk < t_star else (0.0 if tk < t_star + max(gap, 0) else 1.0)
        I[k] = f * i_line(s) / I_N
        w = max(w + (f * torque(s) / T_N - load(w)) / J * DT, 0.0)
        W[k] = w
    ks = int(round(t_star / DT)); kd = int(round((t_star + max(gap, 0)) / DT))
    return I[ks - 1], I[kd:kd + 200].max(), W[ks - 1], W[ks - 1] - W[kd - 1]


def windings():
    """图 19-p1-1：三相绕组的星形接法与三角形接法。每段绕组画成一个小方框。"""
    fig, ax = fs.diagram(w=8.6, h=3.6, xlim=(0, 10), ylim=(-0.2, 4.4))
    def wind(p, q, lab, ends):
        p, q = np.array(p), np.array(q); m = (p + q) / 2; d = q - p; L = np.hypot(*d); u = d / L
        a = m - u * 0.45; b = m + u * 0.45
        ax.plot(*zip(p, a), color="k", lw=1.3); ax.plot(*zip(b, q), color="k", lw=1.3)
        ang = np.degrees(np.arctan2(d[1], d[0]))
        r = Rectangle(a - np.array([-u[1], u[0]]) * 0.14, 0.9, 0.28, angle=ang, rotation_point=(a[0] - (-u[1]) * 0.14, a[1] - u[0] * 0.14),
                      fc="white", ec="k", lw=1.3)
        ax.add_patch(r)
        nrm = np.array([-u[1], u[0]])
        ax.text(*(m + nrm * 0.42), lab, ha="center", va="center", fontsize=9, color="#4d4d4d")
        for pt, e in zip((p, q), ends):
            if e:
                ax.text(*(pt + (pt - m) / np.linalg.norm(pt - m) * 0.32), e, ha="center", va="center", fontsize=9)
    # 星形：尾端 U2 V2 W2 接在一起
    c = np.array([2.3, 1.6]); R = 1.5
    pts = [c + R * np.array([np.cos(a), np.sin(a)]) for a in np.radians([90, 210, 330])]
    for p, nm, e in zip(pts, "UVW", ["U", "V", "W"]):
        wind(p, c, f"{U_PH_Y:.0f} V", (f"{e}1", None))
    ax.plot(*c, "ko", ms=4)
    ax.annotate("星点：尾端 U2 V2 W2 接在一起", xy=c, xytext=(2.3, 0.05), ha="center", fontsize=8, color="#4d4d4d",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#808080"))
    for p, L in zip(pts, ["L1", "L2", "L3"]):
        ax.plot(*p, "ko", ms=4, mfc="white")
    ax.text(2.3, 4.15, f"星形（Y）：每段绕组 {U_PH_Y:.0f} V（常说 220 V）", ha="center", fontsize=10)
    # 三角形：首尾相接
    tri = [np.array([7.5, 3.4]), np.array([5.9, 0.6]), np.array([9.1, 0.6])]
    wind(tri[0], tri[1], f"{U_LINE:.0f} V", (None, None)); wind(tri[1], tri[2], f"{U_LINE:.0f} V", (None, None))
    wind(tri[2], tri[0], f"{U_LINE:.0f} V", (None, None))
    ax.text(7.5, 3.6, "U1 W2", ha="center", fontsize=9); ax.text(5.5, 0.35, "V1 U2", ha="center", fontsize=9); ax.text(9.5, 0.35, "W1 V2", ha="center", fontsize=9)
    for p in tri:
        ax.plot(*p, "ko", ms=4, mfc="white")
    ax.text(7.5, 4.15, "三角形（△）：每段绕组 380 V", ha="center", fontsize=10)
    ax.text(7.5, -0.1, "两种接法接的都是线电压 380 V 的三相电源", ha="center", fontsize=9, color="#4d4d4d")
    print(f"[图 19-p1-1] 线电压 {U_LINE:.0f} V；星形每段绕组 {U_LINE:.0f}/√3 = {U_PH_Y:.1f} V ≈ {U_PH_Y:.0f} V；三角形每段 {U_LINE:.0f} V；比值 {U_PH_Y / U_LINE:.3f}")
    assert abs(U_PH_Y - 219.4) < 0.1
    fs.save(fig, P, "19_p1_1_windings.png")


def bars():
    """图 19-p1-2：直接启动与星形启动的启动电流、启动转矩（示意电动机，额定值的倍数）。"""
    i_d = i_line(1.0) / I_N; t_d = torque(1.0) / T_N
    vals = [(i_d, i_d / 3), (t_d, t_d / 3)]
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    xs = np.array([0, 1])
    ax.bar(xs - 0.18, [vals[0][0], vals[1][0]], 0.34, color=fs.C["third"], label="直接启动（三角形）")
    ax.bar(xs + 0.18, [vals[0][1], vals[1][1]], 0.34, color=fs.C["cur"], label="星形启动")
    for x, (a, b) in zip(xs, vals):
        fs.mark(ax, x - 0.18, a, "{:.1f}", "倍", dy=4, marker="")
        fs.mark(ax, x + 0.18, b, "{:.1f}", "倍", dy=4, marker="")
    fs.ref_h(ax, 1.0, "额定值", x=0.99)
    ax.set_xticks(xs); ax.set_xticklabels(["启动电流", "启动转矩"])
    ax.set_ylabel("额定值的倍数"); ax.set_ylim(0, 7)
    ax.legend(loc="upper right", fontsize=8)
    print(f"[图 19-p1-2] 示意电动机：直接启动电流 {i_d:.1f} 倍、星形 {i_d / 3:.1f} 倍；直接启动转矩 {t_d:.2f} 倍、星形 {t_d / 3:.2f} 倍（都是 1/3）")
    assert 5 <= i_d <= 7                         # 落在资料给的 5～7 倍范围里
    fs.save(fig, P, "19_p1_2_bars.png")


def relay():
    """图 19-p1-3：三只接触器像接力一样分工（示意，不按比例）。"""
    fig, ax = fs.diagram(w=8.6, h=2.8, xlim=(-1.6, 10.4), ylim=(-0.4, 3.6))
    rows = [("KM 主接触器", 2.7, [(0.5, 10.0)], fs.C["vout"]), ("KMY 星形", 1.8, [(0.5, 5.0)], fs.C["vin"]),
            ("KM△ 三角形", 0.9, [(5.6, 10.0)], fs.C["fb"]), ("KT 计时", 0.0, [(0.5, 5.0)], "#9e9e9e")]
    for name, y, segs, col in rows:
        ax.text(0.3, y + 0.15, name, ha="right", va="center", fontsize=9)
        for a, b in segs:
            ax.add_patch(Rectangle((a, y), b - a, 0.32, fc=col, ec="none", alpha=0.85))
    ax.text(2.75, 1.3, "星形降压启动", ha="center", fontsize=9)
    ax.text(7.8, 0.4, "三角形全压运行", ha="center", fontsize=9)
    ax.annotate("", xy=(5.6, 1.45), xytext=(5.0, 1.45), arrowprops=dict(arrowstyle="<->", lw=1))
    ax.text(5.3, 1.55, "空档", ha="center", fontsize=8)
    ax.text(0.5, -0.35, "按启动", ha="center", fontsize=8); ax.text(5.0, -0.35, "延时到", ha="center", fontsize=8)
    print("[图 19-p1-3] 示意：KM 全程吸合；KMY 从按启动到延时到；KM△ 在空档之后接上")
    fs.save(fig, P, "19_p1_3_relay.png")


def main_circuit():
    """图 19-p2-1：星三角主电路。三段绕组单独画出：上端 U1 V1 W1，下端 U2 V2 W2。"""
    with drawing(fontsize=10) as d:
        XS = [0, 1.8, 3.6]; XD = [6.0, 7.4, 8.8]
        tap = [-5.0, -5.4, -5.8]
        for i, x in enumerate(XS):
            d += elm.Dot(open=True).at((x, 0)).label(f"L{i + 1}", "top")
            d += elm.Fuse().down().length(1.3)
            d += elm.Line().down(0.2)
            d += ContactNO().down().length(1.5)
            d += elm.Line().down(0.2)
            d += ThermalHeater().down().length(1.3)
            d += elm.Line().down().toy(tap[i])
            d += elm.Dot()
            d += elm.Line().right().tox(XD[i])
            d += elm.Line().at((x, tap[i])).down().toy(-6.6)
            d += elm.Dot(open=True).label(["U1", "V1", "W1"][i], "left")
            d += elm.Inductor2(loops=3).down().length(1.6)
            d += elm.Dot(open=True).label(["U2", "V2", "W2"][i], "left")
            d += elm.Line().down().toy(-9.4)
            d += ContactNO().down().length(1.5)
        d += elm.Line().at((XS[0], -10.9)).right().tox(XS[2])
        d += elm.Label().at((XS[1], -11.3)).label("星点（KMY 闭合时三个尾端接在一起）", fontsize=9, color="#4d4d4d")
        # KM△：L1 列 → W2，L2 列 → U2，L3 列 → V2（三条横线错开高度）
        for xd, xt, y in [(XD[0], XS[2], -8.7), (XD[1], XS[0], -9.1), (XD[2], XS[1], -8.9)]:
            d += elm.Line().at((xd, -5.0 if xd == XD[0] else (-5.4 if xd == XD[1] else -5.8))).down().toy(-6.4)
            d += ContactNO().down().length(1.5)
            d += elm.Line().down().toy(y)
            d += elm.Line().left().tox(xt)
            d += elm.Dot()
        for xs, txt, yc in [(XS, "KM 主", -2.25), (XD, "KM△", -7.15), (XS, "KMY", -10.15)]:
            d += elm.Line().at((xs[0] + 0.25, yc)).to((xs[2] + 0.25, yc)).linestyle("--").color("#808080")
        d += elm.Label().at((-1.6, -2.3)).label("KM\n主接触器", fontsize=9)
        d += elm.Label().at((-1.6, -4.0)).label("热继电器\nFR", fontsize=9)
        d += elm.Label().at((-1.6, -0.8)).label("熔断器\nFU1", fontsize=9)
        d += elm.Label().at((-1.6, -7.4)).label("电动机\n三段绕组", fontsize=9)
        d += elm.Label().at((-1.6, -10.2)).label("KMY\n星形", fontsize=9)
        d += elm.Label().at((10.4, -7.2)).label("KM△\n三角形", fontsize=9)
        d += elm.Label().at((10.6, -9.6)).label("KM△ 下口：\nL1 列 → W2\nL2 列 → U2\nL3 列 → V2", fontsize=8, color="#4d4d4d")
    print("[图 19-p2-1] 主电路：KM△ 闭合时 U1–W2、V1–U2、W1–V2 相连（三角形）；KMY 闭合时 U2、V2、W2 相连（星形）")
    save_schem(d, P, "19_p2_1_main.png")


def rung(d, y, items, x0, x1):
    """在高度 y 上从 x0 起依次画 items = [(元件类, 标签)]，('par', ((E1,l1),(E2,l2))) 表示并联块，最后连到 x1。"""
    d += elm.Line().at((x0, y)).right(0.4)
    for E, lab in items:
        if E == "par":
            (E1, l1), (E2, l2) = lab
            a = d.here
            d += E1().right().label(l1, ofst=0.6)
            b = d.here
            d += elm.Line().at(a).down(1.4)
            d += E2().right().tox(b[0]).label(l2, "bottom", ofst=0.25)
            d += elm.Line().up(1.4)
            d += elm.Dot().at(a); d += elm.Dot().at(b)
            d += elm.Line().at(b).right(0.4)
        else:
            d += E().right().label(lab, ofst=0.6 if E is not Coil else 0.4)
            d += elm.Line().right(0.4)
    d += elm.Line().right().tox(x1)


def control():
    """图 19-p2-2：星三角控制回路（四条支路：KM、KT、KMY、KM△）。"""
    with drawing(fontsize=10) as d:
        d += elm.Dot(open=True).at((-9.6, 0)).label("L", "left")
        d += elm.Line().right(0.4)
        d += PushNC().right().label("SB1 停止", ofst=0.6)
        d += elm.Line().right(0.4)
        d += ThermalNC().right().label("FR", ofst=0.6)
        d += elm.Line().right(0.4)
        a = d.here
        d += PushNO().right().label("SB2 启动", ofst=0.6)
        b = d.here
        d += elm.Line().at(a).down(1.4)
        d += ContactNO().right().tox(b[0]).label("KM 自锁", "bottom", ofst=0.25)
        d += elm.Line().up(1.4)
        d += elm.Dot().at(a); d += elm.Dot().at(b)
        d += elm.Line().at(b).right().tox(0)
        d += elm.Dot()
        X1 = 9.5; ys = [0, -2.6, -5.2, -7.8]
        rung(d, ys[0], [(Coil, "KM 线圈")], 0, X1)
        rung(d, ys[1], [(ContactNC, "KM△ 常闭"), (Coil, "KT 线圈")], 0, X1)
        rung(d, ys[2], [(TimerNC, "KT 延时断开"), (ContactNC, "KM△ 常闭"), (Coil, "KMY 线圈")], 0, X1)
        rung(d, ys[3], [("par", ((TimerNO, "KT 延时闭合"), (ContactNO, "KM△ 自锁"))), (ContactNC, "KMY 常闭"), (Coil, "KM△ 线圈")], 0, X1)
        d += elm.Line().at((0, 0)).down(-ys[3])
        d += elm.Line().at((X1, 0)).down(-ys[3])
        for y in ys[1:3]:
            d += elm.Dot().at((0, y)); d += elm.Dot().at((X1, y))
        d += elm.Dot().at((X1, 0))
        d += elm.Line().at((X1, ys[3])).right(0.6)
        d += elm.Dot(open=True).label("N", "right")
    print("[图 19-p2-2] 控制回路：KM 自锁；KT 经 KM△ 常闭；KMY 经 KT 延时断开 + KM△ 常闭；KM△ 经 KT 延时闭合（并 KM△ 自锁）+ KMY 常闭")
    save_schem(d, P, "19_p2_2_control.png")


def delay_sweep():
    """图 19-p3-1：星形时间 T 从 1 s 到 12 s，切换瞬间的电流尖峰和切换时的转速。"""
    Ts = np.arange(1, 13, 1.0)
    res = [run(T, 0.020) for T in Ts]
    spike = np.array([r[1] for r in res]); wsw = np.array([r[2] for r in res]) * 100; ibefore = np.array([r[0] for r in res])
    i_dol = i_line(1.0) / I_N
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(Ts, spike, **fs.LS["cur"], marker="o", ms=3, label="切换到三角形瞬间的电流")
    ax.plot(Ts, ibefore, **fs.LS["vin"], marker="s", ms=3, label="切换前（星形）的电流")
    fs.ref_h(ax, i_dol, f"直接启动的峰值", x=0.99)
    fs.ref_h(ax, 1.0, "额定电流", x=0.99)
    k_flat = int(np.argmax(np.abs(np.diff(ibefore)) < 0.02))   # 星形电流"不再下降"的第一个点（它和下一个点几乎一样）
    fs.mark(ax, Ts[k_flat], spike[k_flat], "{:.1f}", "倍", dx=8, dy=6)
    fs.mark(ax, Ts[0], spike[0], "{:.1f}", "倍", dx=8, dy=0)
    ax.axvspan(Ts[k_flat], Ts[-1], color=fs.C["good"], alpha=0.06, lw=0)
    ax.text(Ts[k_flat] + 0.2, 4.1, "星形电流已不再下降：\n这一段切换都可以", fontsize=8, color="#4d4d4d")
    ax.set_ylim(0, 6.6); ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)
    fs.axlabels(ax, "星形启动时间 T", "s", "线电流 / 额定电流", None)
    for T, s, w, ib in zip(Ts, spike, wsw, ibefore):
        print(f"[图 19-p3-1] T = {T:.0f} s：切换前 {ib:.2f} 倍，转速 {w:.0f}%，切换尖峰 {s:.1f} 倍")
    print(f"[图 19-p3-1] 星形电流从 T = {Ts[k_flat]:.0f} s 起不再明显下降（相邻两点相差 < 0.02 倍）；直接启动峰值 {i_dol:.1f} 倍")
    assert spike[0] > 0.9 * i_dol and spike[-1] < spike[0] / 2
    fs.save(fig, P, "19_p3_1_delay.png")
    return Ts[k_flat]


def gap_sweep():
    """图 19-p3-2：切换空档从 0 到 400 ms：空档里转速下降多少、接上三角形时电流尖峰多大。负空档 = 重叠 = 短路。"""
    gaps = np.array([0, 20, 40, 60, 100, 150, 200, 300, 400])
    res = [run(6.0, g / 1e3) for g in gaps]
    spike = np.array([r[1] for r in res]); drop = np.array([r[3] for r in res]) * 100
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.axvspan(-90, 0, color=fs.C["bad"], alpha=0.10, lw=0)
    ax.text(-86, 4.6, "空档 < 0：\nKMY 还没断开\nKM△ 已闭合\n= 三相短路", fontsize=8, color=fs.C["bad"])
    ax.plot(gaps, spike, **fs.LS["cur"], marker="o", ms=3, label="接上三角形瞬间的电流")
    fs.ref_h(ax, i_line(1.0) / I_N, "直接启动的峰值", x=0.99)
    fs.ref_v(ax, 20, "本页电路 20 ms", y=0.55)
    fs.ref_v(ax, 40, None)
    ax.text(44, 0.5, "施耐德延时模块\n40 ms ± 15 ms", fontsize=8, color="#4d4d4d")
    fs.mark(ax, 400, spike[-1], "{:.1f}", "倍", dx=-34, dy=6)
    fs.mark(ax, 20, spike[1], "{:.1f}", "倍", dx=6, dy=-14)
    ax.set_xlim(-90, 420); ax.set_ylim(0, 6.6); ax.legend(loc="upper center", fontsize=8)
    fs.axlabels(ax, "切换空档", "ms", "线电流 / 额定电流", None)
    for g, s, dr in zip(gaps, spike, drop):
        print(f"[图 19-p3-2] 空档 {g:.0f} ms：空档里转速下降 {dr:.1f} 个百分点，接上三角形尖峰 {s:.1f} 倍")
    assert spike[-1] > spike[1] and drop[-1] > drop[1]
    fs.save(fig, P, "19_p3_2_gap.png")


def exercises():
    """练习和正文用数字。"""
    I_rated = 30.0; k = 6
    print(f"[练习 1] 额定电流 {I_rated:.0f} A、直接启动按 {k} 倍算：直接启动 {I_rated * k:.0f} A；星形启动 {I_rated * k / 3:.0f} A")
    tp, tdr = 12, 19
    print(f"[练习 3] KM△ 线圈不经 KMY 常闭、只靠 KT 同时切换：KM△ 吸合 {tp} ms、KMY 释放 {tdr} ms → 空档 {tp - tdr} ms（重叠 {tdr - tp} ms，三相短路）；"
          f"有 KMY 常闭互锁 → 空档 = {tp} ms")
    print(f"[练习 4] 铭牌 380 V 星形接法的电动机：每段绕组额定 {U_PH_Y:.0f} V；若接成三角形，每段要承受 {U_LINE:.0f} V，是额定的 {U_LINE / U_PH_Y:.2f} 倍")
    assert abs(U_LINE / U_PH_Y - np.sqrt(3)) < 1e-9
    for tag, Ir, kk in [("例题 1", 20.0, 7), ("例题 2", 16.0, 5)]:
        print(f"[{tag}] 额定 {Ir:.0f} A、直接启动 {kk} 倍：直接启动 {Ir * kk:.0f} A；星形 {Ir * kk / 3:.1f} A；"
              f"星形相电流 = 线电流 = {Ir * kk / 3:.1f} A，三角形相电流 = {Ir * kk / np.sqrt(3):.1f} A")
    td, need = 1.8, 0.7
    print(f"[例题 3] 直接启动转矩 {td} 倍额定、负载起步要 {need} 倍：星形只有 {td / 3:.1f} 倍 < {need} 倍，推不动")
    assert td / 3 < need


if __name__ == "__main__":
    windings()
    bars()
    relay()
    main_circuit()
    control()
    delay_sweep()
    gap_sweep()
    exercises()
