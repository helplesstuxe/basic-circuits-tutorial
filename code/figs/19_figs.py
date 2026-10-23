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


def three_phase():
    """图 19-p2-1：三相电压一个周期的波形，以及两相之差（线电压）为什么是相电压的 √3 倍。"""
    U_PH = 220.0                                   # 相电压有效值（V）
    UM = U_PH * np.sqrt(2)                         # 相电压峰值（V）：有效值 × √2
    t = np.linspace(0, 20e-3, 20001)               # 50 Hz 的一个周期 = 20 ms
    w = 2 * np.pi * 50
    u1 = UM * np.sin(w * t)                        # L1
    u2 = UM * np.sin(w * t - 2 * np.pi / 3)        # L2：比 L1 晚 1/3 个周期
    u3 = UM * np.sin(w * t - 4 * np.pi / 3)        # L3：比 L1 晚 2/3 个周期
    u12 = u1 - u2                                  # L1 与 L2 之间的电压（线电压）
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    ax.plot(t * 1e3, u1, **fs.LS["vin"], label="$u_1$（L1 对零线）")
    ax.plot(t * 1e3, u2, **fs.LS["vout"], label="$u_2$（L2 对零线）")
    ax.plot(t * 1e3, u3, **fs.LS["third"], label="$u_3$（L3 对零线）")
    ax.plot(t * 1e3, u12, **fs.LS["fb"], label="$u_1 - u_2$（L1 与 L2 之间）")
    fs.ref_h(ax, 0.0)
    k1 = np.argmax(u1); k12 = np.argmax(u12)
    fs.mark(ax, t[k1] * 1e3, u1[k1], "{:.0f}", "V", dy=6)
    fs.mark(ax, t[k12] * 1e3, u12[k12], "{:.0f}", "V", dy=6)
    fs.mark(ax, t[k1] * 1e3, u2[k1], "{:.0f}", "V", dy=-14)
    ax.set_ylim(-650, 750)
    fs.axlabels(ax, "时间", "ms", "电压", "V")
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ratio = u12.max() / u1.max()
    print(f"[图 19-p2-1] 相电压有效值 {U_PH:.0f} V，峰值 {UM:.0f} V；L2、L3 依次晚 1/3 个周期（{20 / 3:.2f} ms）")
    print(f"[图 19-p2-1] u1 在 {t[k1] * 1e3:.1f} ms 到最高 {u1[k1]:.0f} V，这一刻 u2 = {u2[k1]:.0f} V（不是 -{UM:.0f} V），所以两者之差不是 2 倍")
    print(f"[图 19-p2-1] u1 - u2 的最大值 {u12.max():.0f} V，出现在 {t[k12] * 1e3:.2f} ms；比值 {ratio:.3f} ≈ √3 = {np.sqrt(3):.3f}；有效值 {U_PH:.0f} × {ratio:.3f} = {U_PH * ratio:.0f} V ≈ 380 V")
    assert abs(ratio - np.sqrt(3)) < 1e-3 and abs(u2[k1] + UM / 2) < 1
    fs.save(fig, P, "19_p2_1_threephase.png")


def main_circuit():
    """图 19-p2-2：星三角主电路。三段绕组单独画出：上端 U1 V1 W1，下端 U2 V2 W2。"""
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
    print("[图 19-p2-2] 主电路：KM△ 闭合时 U1–W2、V1–U2、W1–V2 相连（三角形）；KMY 闭合时 U2、V2、W2 相连（星形）")
    save_schem(d, P, "19_p2_2_main.png")


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
    """图 19-p2-3：星三角控制回路（四条支路：KM、KT、KMY、KM△）。"""
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
    print("[图 19-p2-3] 控制回路：KM 自锁；KT 经 KM△ 常闭；KMY 经 KT 延时断开 + KM△ 常闭；KM△ 经 KT 延时闭合（并 KM△ 自锁）+ KMY 常闭")
    save_schem(d, P, "19_p2_3_control.png")


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
    three_phase()
    main_circuit()
    control()
    delay_sweep()
    gap_sweep()
    exercises()


# ======================= page4 动手实验篇：面包板接线图 =======================
# 面包板俯视图小工具（各节点脚本各带一份，互不依赖）。
# 坐标：列号 1…ncol 从左到右；上半区 a–e、下半区 f–j（同一列的 a–e 五个孔互相连通，f–j 也连通）；
# 上下各有两条电源轨：靠外的一条标「+」，靠里的一条标「−」，整条横向连通。
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

BB_Y = {r: 5.6 - i for i, r in enumerate("abcde")}
BB_Y.update({r: -1.4 - i for i, r in enumerate("fghij")})
BB_Y.update({"T+": 8.6, "T-": 7.7, "B-": -6.7, "B+": -7.6})
WIRE = dict(pos=(fs.C["bad"], "正电源"), gnd=("#000000", "地（0 V）"), neg=(fs.C["third"], "负电源"),
            sig=(fs.C["vin"], "输入信号"), out=(fs.C["vout"], "输出"), fb=(fs.C["fb"], "反馈 / 其他连线"))


class Breadboard:
    def __init__(self, ncol=30, title=None, size=(10, 6.4), rails=("+", "−", "−", "+")):
        self.ncol, self.used = ncol, set()
        self.fig, self.ax = plt.subplots(figsize=size)
        ax = self.ax
        ax.add_patch(FancyBboxPatch((0.2, -8.3), ncol + 0.6, 17.6, boxstyle="round,pad=0.1",
                                    fc="#f7f5ef", ec="0.55", lw=1.0))
        ax.add_patch(Rectangle((0.4, -0.55), ncol + 0.2, 0.7, fc="#e4e0d6", ec="none"))   # 中间凹槽
        for key, lab in zip(("T+", "T-", "B-", "B+"), rails):
            y = BB_Y[key]
            col = fs.C["bad"] if lab.startswith("+") else ("#000000" if lab in ("−", "GND", "0 V") else fs.C["third"])
            ax.plot([0.6, ncol + 0.4], [y + 0.42, y + 0.42], color=col, lw=1.0)
            ax.text(0.0, y, lab, ha="right", va="center", fontsize=10, color=col, fontweight="bold")
            for c in range(1, ncol + 1):
                if c % 6:
                    ax.add_patch(Circle((c, y), 0.12, fc="0.72", ec="none"))
        for r in "abcdefghij":
            y = BB_Y[r]
            ax.text(0.15, y, r, ha="right", va="center", fontsize=8, color="0.35")
            ax.text(ncol + 0.85, y, r, ha="left", va="center", fontsize=8, color="0.35")
            for c in range(1, ncol + 1):
                ax.add_patch(Circle((c, y), 0.12, fc="0.72", ec="none"))
        for c in range(1, ncol + 1):
            if c == 1 or c % 5 == 0:
                ax.text(c, 6.35, str(c), ha="center", va="bottom", fontsize=7.5, color="0.35")
                ax.text(c, -6.15, str(c), ha="center", va="top", fontsize=7.5, color="0.35")
        ax.set_xlim(-3.4, ncol + 4.8)
        ax.set_ylim(-11.2, 11.6)
        ax.set_aspect("equal")
        ax.axis("off")
        if title:
            ax.set_title(title, fontsize=11)

    def xy(self, h):
        """'e10' → 第 10 列 e 排；'T+3' / 'B-7' → 上（T）/ 下（B）电源轨第 3 / 7 列。"""
        if h[0] in "TB" and h[1] in "+-":
            return float(h[2:]), BB_Y[h[:2]]
        return float(h[1:]), BB_Y[h[0]]

    def _hole(self, p):
        x, y = self.xy(p) if isinstance(p, str) else p
        if isinstance(p, str):
            self.ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=4))
        return x, y

    def wire(self, a, b, kind="fb", via=None):
        """导线：a、b 为孔名或 (x, y)；via 为中间拐点列表。颜色按 kind 取（见 WIRE）。"""
        self.used.add(kind)
        pts = [self._hole(a)] + list(via or []) + [self._hole(b)]
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=WIRE[kind][0], lw=2.4, solid_capstyle="round", zorder=5)

    def part(self, a, b, label, kind="R", lab_side=1):
        """两脚元件：R 电阻、C 电容、E 电解电容（+ 脚在 a）、D 二极管（a 阳 b 阴）、L LED（a 阳）、
        S 按钮、P 小灯泡。画成方框简化符号，标签写在旁边。"""
        (x1, y1), (x2, y2) = self._hole(a), self._hole(b)
        ax = self.ax
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.plot([x1, x2], [y1, y2], color="0.35", lw=1.2, zorder=5)
        fc = dict(R="#d9c7a3", C="#f2d27a", E="#6d8fb5", D="#555555", L="#ffffff", S="#bbbbbb",
                  P="#fff7c2")[kind]
        horiz = abs(x2 - x1) >= abs(y2 - y1)
        w, h = (0.9, 0.5) if horiz else (0.5, 0.9)
        if kind in "LP":
            ax.add_patch(Circle((mx, my), 0.42, fc=fc, ec="0.2", lw=1.0, zorder=6))
        else:
            ax.add_patch(FancyBboxPatch((mx - w / 2, my - h / 2), w, h, boxstyle="round,pad=0.05",
                                        fc=fc, ec="0.2", lw=1.0, zorder=6))
        if kind in "EDL":
            ax.text(x1 + (0.25 if horiz else 0.25), y1 + (0.3 if horiz else 0), "+", fontsize=8,
                    ha="center", va="center", zorder=7, color=fs.C["bad"])
        if lab_side == "r":
            ax.text(max(x1, x2) + 0.3, my, label, ha="left", va="center", fontsize=8.5, zorder=7)
        elif horiz:
            ax.text(mx, my + 0.55 * lab_side, label, ha="center", va="bottom" if lab_side > 0 else "top",
                    fontsize=8.5, zorder=7)
        else:
            ax.text(mx + 0.45 * lab_side, my, label, ha="left" if lab_side > 0 else "right",
                    va="center", fontsize=8.5, zorder=7)

    def chip(self, col, label, npin=8, names=None):
        """DIP 芯片跨在中间凹槽上：第 1 脚在 f 排第 col 列（左下，缺口朝左），逆时针数，
        第 npin 脚在 e 排第 col 列。脚号和脚名写在芯片体上。"""
        half = npin // 2
        ax = self.ax
        y0, y1 = BB_Y["f"] + 0.22, BB_Y["e"] - 0.22
        ax.add_patch(Rectangle((col - 0.5, y0), half, y1 - y0, fc="#2b2b2b", ec="k", zorder=6))
        ax.add_patch(Circle((col - 0.5, (y0 + y1) / 2), 0.28, fc="#f7f5ef", ec="none", zorder=7))
        ax.text(col + (half - 1) / 2, (y0 + y1) / 2, label, color="w", ha="center",
                va="center", fontsize=9, zorder=8)
        for i in range(half):
            for p, row in ((i + 1, "f"), (npin - i, "e")):
                x, y = col + i, BB_Y[row]
                ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=7))
                txt = str(p) + ("\n" + names[p] if names and p in names else "")
                ax.text(x, y0 + 0.08 if row == "f" else y1 - 0.08, txt, ha="center",
                        va="bottom" if row == "f" else "top", fontsize=6, color="w", zorder=8,
                        linespacing=0.9)

    def module(self, x, y, w, h, label, fc="#e6f0f8"):
        """面包板外的模块（电池、信号源、继电器模块等），返回方框中心。"""
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec="0.3",
                                         lw=1.0, zorder=6))
        self.ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8.5, zorder=7)
        return x + w / 2, y + h / 2

    def note(self, x, y, text, **kw):
        self.ax.text(x, y, text, fontsize=8, zorder=8, **kw)

    def legend(self, loc="lower center"):
        from matplotlib.lines import Line2D
        cname = {fs.C["bad"]: "红", "#000000": "黑", fs.C["third"]: "紫", fs.C["vin"]: "蓝",
                 fs.C["vout"]: "橙", fs.C["fb"]: "绿", fs.C["cur"]: "天蓝"}
        def lab(c, t):                                # 图例写成「用途（色名）」；用途里已有括号时并进同一对括号
            return t[:-1] + f"，{cname[c]}）" if t.endswith("）") else f"{t}（{cname[c]}）"
        hs = [Line2D([], [], color=WIRE[k][0], lw=2.4, label=lab(*WIRE[k])) for k in WIRE if k in self.used]
        self.ax.legend(handles=hs, loc=loc, ncol=len(hs), fontsize=8.5, frameon=False,
                       bbox_to_anchor=(0.5, -0.01))

    def save(self, prefix, name):
        return fs.save(self.fig, prefix, name)

# ---------- 图 19-p4-1：12 V 低压星三角控制回路的面包板接线 ----------
WIRE["neg"] = (fs.C["third"], "公共点 C（KM 自锁之后）")
WIRE["sig"] = (fs.C["vin"], "KM△ 支路")
WIRE["out"] = (fs.C["vout"], "KT、KMY 支路")
WIRE["fb"] = (fs.C["fb"], "按钮引线")
bb = Breadboard(40, "星三角低压版面包板俯视图（12 V 直流，三只 12 V 继电器 + 延时模块）",
                size=(12, 6.8), rails=("公共点 C", "0 V", "0 V", "+12 V 经SB1"))
pins = {1: "COM1", 2: "NO1", 3: "线圈+", 4: "NC1", 8: "线圈−", 7: "COM2", 6: "NO2", 5: "NC2"}
bb.chip(8, "KM", npin=8, names=pins)
bb.chip(18, "KM△", npin=8, names=pins)
bb.chip(32, "KMY", npin=8, names=pins)
for c in (8, 18, 32):
    bb.wire(f"a{c}", f"T-{c}", "gnd")                  # 三只线圈负端 → 0 V
# KM：COM1 接「+12 V 经 SB1」，NO1 = 线圈+ = 公共点 C（自锁）
bb.wire("j8", "B+8", "pos")
bb.wire("g9", "g10", "neg")
bb.wire("i10", "i13", "neg"); bb.wire("f13", "d13", "neg"); bb.wire("a13", "T+13", "neg")
bb.part("B-10", "j10", "VD1", "D", lab_side="r")
bb.part("h10", "h5", "HL1", "P", lab_side=1); bb.wire("j5", "B-5", "gnd")
# KM△：COM1、COM2 接公共点；NO1 = Y；线圈+ = Z；NC2 = X
bb.wire("h18", "h15", "neg"); bb.wire("f15", "d15", "neg"); bb.wire("a15", "T+15", "neg")
bb.wire("a19", "T+19", "neg")
bb.part("B-20", "j20", "VD2", "D", lab_side="r")
bb.part("i20", "i25", "HL3", "P", lab_side=1); bb.wire("j25", "B-25", "gnd")
# Y：KT 常开 / KM△ NO1 → KMY COM1；Z：KMY NC1 → KM△ 线圈+
bb.wire("g19", "g28", "sig"); bb.wire("f28", "d28", "sig"); bb.wire("i28", "i32", "sig")
bb.wire("h20", "h35", "sig")
# X：KM△ NC2 → KT 模块 V+、COM；W：KT 常闭 → KMY 线圈+
bb.wire("b21", "b22", "out")
bb.wire("d36", "f36", "out"); bb.wire("i36", "i34", "out")
bb.part("B-34", "j34", "VD3", "D", lab_side="r")
bb.part("g34", "g39", "HL2", "P", lab_side=1); bb.wire("j39", "B-39", "gnd")
bb.wire("T-40", "B-40", "gnd")
# KT 延时模块（面包板外），五根引线垂直落到上半区
bb.module(20.3, 9.65, 16.4, 1.45, "", fc="#fdf1dc")
bb.ax.text(28.5, 10.75, "KT 通电延时模块（12 V，设成通电延时）", ha="center", va="center", fontsize=8.5, zorder=8)
for x, name, kind, dst in [(21, "V+", "out", "a21"), (22, "COM", "out", "a22"), (25, "V−", "gnd", "T-25"),
                           (28, "NO", "sig", "a28"), (36, "NC", "out", "a36")]:
    bb.ax.text(x, 9.95, name, ha="center", va="center", fontsize=6.5, zorder=8)
    bb.wire((x, 9.65), dst, kind)
# 电源、按钮
bb.module(11.2, -10.0, 3.0, 1.3, "12 V 电源")
bb.wire((12.2, -8.7), "B-12", "gnd")
bb.module(15.2, -10.0, 3.6, 1.3, "SB1 停止（常闭）", fc="#f6dede")
bb.wire((14.2, -9.35), (15.2, -9.35), "pos")
bb.wire((17.0, -8.7), "B+17", "pos")
bb.module(6.6, -10.0, 3.6, 1.3, "SB2 启动（常开）", fc="#def0de")
bb.wire((8.0, -8.7), "i8", "fb"); bb.wire((9.0, -8.7), "i9", "fb")
bb.note(0.8, 10.3, "继电器、模块引脚以手册为准（本图为示意）", va="center")
bb.legend()
bb.save(P, "19_p4_1_breadboard.png")


# ---------- 图 19-p4-2：按 0.01 s 一步推演指示灯的先后 ----------
def star_delta_lamps(t_set=5.0, t_sb2=(1.0, 1.3), t_sb1=(11.0, 11.3), t_end=13.0, dt=0.01):
    """不计继电器动作时间的理想逻辑（接线同 图 19-p4-1）：
    KM' = 非SB1·(SB2+KM)；X = KM'·非KM△（KT 线圈）；KMY' = X·非T；
    KM△' = KM'·(X·T + KM△)·非KMY。T 是 KT 已计满整定时间。"""
    km = kmy = kmd = 0; tk = 0.0
    tt, rec = np.arange(0, t_end, dt), []
    for t in tt:
        sb2 = t_sb2[0] <= t < t_sb2[1]; sb1 = t_sb1[0] <= t < t_sb1[1]
        km = int((not sb1) and (sb2 or km))
        x = int(km and not kmd)
        tk = tk + dt if x else 0.0
        T = tk >= t_set - 1e-9
        kmd_new = int(km and ((x and T) or kmd) and not kmy)
        kmy = int(x and not T)
        kmd = kmd_new
        rec.append((km, kmy, kmd, x))
    return tt, np.array(rec)


tt, rec = star_delta_lamps()
def first_on(k): return tt[np.argmax(rec[:, k] == 1)]
def last_on(k): return tt[np.nonzero(rec[:, k])[0][-1]] + 0.01
t_y_off, t_d_on = last_on(1), first_on(2)
print(f"[数值] 1.00 s 按 SB2：KM {first_on(0):.1f} s 亮，KMY {first_on(1):.1f} s 亮、{t_y_off:.1f} s 灭；"
      f"KM△ {t_d_on:.1f} s 亮；KT 线圈 {last_on(3):.1f} s 断电；11.00 s 按 SB1 全灭")
assert abs(t_y_off - 6.0) < 0.02 and abs(t_d_on - 6.0) < 0.03 and abs(last_on(3) - 6.0) < 0.03
assert not (rec[:, 1] & rec[:, 2]).any() and rec[-1].sum() == 0
fig, ax = plt.subplots(figsize=(8.8, 3.4))
names = ["HL1 / KM", "HL2 / KMY（星形）", "HL3 / KM△（三角形）", "KT 线圈"]
cols = [fs.C["vout"], fs.C["vin"], fs.C["fb"], "0.45"]
for r, (nm, c) in enumerate(zip(names, cols)):
    y0 = 3 - r
    ax.fill_between(tt, y0, y0 + 0.7 * rec[:, r], step="post", color=c, alpha=0.85, lw=0)
    ax.text(-0.2, y0 + 0.35, nm, ha="right", va="center", fontsize=9)
for t0, lab in [(1.0, "按 SB2"), (6.0, "KT 到时（整定 5 s）"), (11.0, "按 SB1")]:
    ax.axvline(t0, color="0.3", ls=":", lw=1.0)
    ax.text(t0 + 0.08, 4.05, lab, fontsize=8.5, va="bottom")
ax.set_xlim(0, 13); ax.set_ylim(-0.2, 4.6)
ax.set_yticks([]); [ax.spines[s].set_visible(False) for s in ("left", "top", "right")]
fs.axlabels(ax, "时间", "s")
fs.save(fig, P, "19_p4_2_sequence.png")

# ---------- 测量表里的计算值 ----------
V, RC, P_LAMP = 12.0, 400.0, 1.0
i_coil, i_lamp = V / RC * 1000, P_LAMP / V * 1000
print(f"[数值] 每只线圈 {i_coil:.0f} mA；三角形稳态（KM + KM△）线圈合计 {2 * i_coil:.0f} mA，"
      f"加两只 1 W 灯泡共约 {2 * (i_coil + i_lamp):.0f} mA")
assert round(2 * i_coil) == 60 and round(2 * (i_coil + i_lamp)) == 227


# ======================= page1–3 补充原理图（国标元件） =======================
ACC = fs.C["bad"]


def yd_branches(d, oy, mode, title):
    """从「公共点」画 KMY、KM△ 两条支路到 N。mode："ok" 正常；"short" KMY 常闭被跳线短接；"none" 去掉 KMY 常闭。"""
    X1 = 11.0
    d += elm.Label().at((-1.6, oy + 2.4)).label(title, halign="left", fontsize=11)
    d += elm.Dot(open=True).at((-0.8, oy)).label("公共点\n（KM 自锁之后）", "left")
    d += elm.Line().right(0.8)
    d += elm.Dot()
    rung(d, oy, [(TimerNC, "KT 延时断开"), (ContactNC, "KM△ 常闭"), (Coil, "KMY 线圈")], 0, X1)
    y2 = oy - 3.0
    d += elm.Line().at((0, oy)).down(3.0)
    d += elm.Line().at((0, y2)).right(0.4)
    a = d.here
    d += TimerNO().right().label("KT 延时闭合", ofst=0.6)
    b = d.here
    d += elm.Line().at(a).down(1.4)
    d += ContactNO().right().tox(b[0]).label("KM△ 自锁", "bottom", ofst=0.25)
    d += elm.Line().up(1.4)
    d += elm.Dot().at(a); d += elm.Dot().at(b)
    d += elm.Line().at(b).right(0.4)
    if mode == "none":
        d += elm.Line().right(1.6).linestyle("--").color(ACC).label("（KMY 常闭被去掉）", ofst=0.3, color=ACC)
        d += elm.Line().right(0.4)
    else:
        c0 = d.here
        col = ACC if mode == "ok_acc" else "black"
        d += ContactNC().right().color(col).label("KMY 常闭", ofst=0.6, color=col)
        c1 = d.here
        if mode == "short":
            d += elm.Dot().at(c0).color(ACC); d += elm.Dot().at(c1).color(ACC)
            d += elm.Wire("n", k=-1.0).at(c0).to(c1).color(ACC).linestyle("--")
            d += elm.Label().at(((c0[0] + c1[0]) / 2 + 0.6, y2 - 1.75)).label("跳线（短接 KMY 常闭）", color=ACC)
        d += elm.Line().at(c1).right(0.4)
    d += (c := Coil().right().label("KM△ 线圈", ofst=0.4))
    d += elm.Line().right().tox(X1)
    d += elm.Line().at((X1, oy)).down(3.0)
    d += elm.Dot().at((X1, oy))
    d += elm.Line().at((X1, y2)).right(0.6)
    d += elm.Dot(open=True).label("N", "right")


def lowvolt_lamps():
    """图 19-p2-6：12 V 实验。（a）三只指示灯各接在一组常开触点上；（b）每只继电器线圈反并 1N4007。"""
    XN = 9.0
    with drawing(fontsize=10) as d:
        d += elm.Label().at((-1.0, 3.0)).label("（a）指示灯：LED 串 1 kΩ，接在各自的一组常开触点上", halign="left", fontsize=11)
        d += elm.Dot(open=True).at((0, 1.6)).label("+12 V", "top")
        d += elm.Line().down().toy(-6.0)
        d += elm.Dot(open=True).at((XN, 1.6)).label("−", "top")
        d += elm.Line().down().toy(-6.0)
        for i, k in enumerate(["KM", "KMY", "KM△"]):
            y = -2.4 * i
            d += elm.Dot().at((0, y))
            d += elm.Line().at((0, y)).right(0.6)
            d += ContactNO().right().label(f"{k} 常开", ofst=0.5)
            d += elm.Line().right(0.4)
            d += elm.Resistor().right(1.6).label("1 kΩ", ofst=0.2)
            d += elm.Line().right(0.4)
            d += elm.LED().right(1.6).color(ACC).label(f"{k} 灯", ofst=0.2, color=ACC)
            d += elm.Line().right().tox(XN)
            d += elm.Dot()
        oy = -9.0
        d += elm.Label().at((-1.0, oy + 2.4)).label("（b）KM、KMY、KM△ 三只继电器线圈都这样反并一只 1N4007", halign="left", fontsize=11)
        d += elm.Dot(open=True).at((1.0, oy)).label("接 + 的一端", "left")
        d += elm.Line().right(1.0)
        a = d.here
        d += elm.Dot()
        d += Coil().right(3.0).label("继电器线圈 12 V", ofst=0.4)
        b = d.here
        d += elm.Dot()
        d += elm.Line().right(1.0)
        d += elm.Dot(open=True).label("接 − 的一端", "right")
        d += elm.Line().at(a).down(1.4).color(ACC)
        d += elm.Diode().at((b[0], oy - 1.4)).to((a[0], oy - 1.4)).color(ACC).label("1N4007（阴极朝 +）", "bottom", ofst=0.2, color=ACC)
        d += elm.Line().at(b).down(1.4).color(ACC)
    print("[图 19-p2-6] 12 V 实验：三只 LED 各串 1 kΩ 接在 KM、KMY、KM△ 常开上；线圈反并 1N4007")
    save_schem(d, P, "19_p2_6_lowvolt.png")


def short_test():
    """图 19-p2-7：实验第 4 步，KM△ 支路里的 KMY 常闭被跳线短接。"""
    with drawing(fontsize=10) as d:
        yd_branches(d, 0, "short", "实验第 4 步：只改 KM△ 线圈支路，其余照图 19-p2-3 不变")
    print("[图 19-p2-7] 实验第 4 步：跳线短接 KM△ 支路里的 KMY 常闭")
    save_schem(d, P, "19_p2_7_short.png")


def ex2_branches():
    """图 19-p3-3：练习 2。（a）去掉 KMY 常闭，只靠 KT 转换触点；（b）装回 KMY 常闭。"""
    with drawing(fontsize=10) as d:
        yd_branches(d, 0, "none", "（a）去掉 KMY 常闭：只靠 KT 的转换触点同时断 KMY、通 KM△")
        yd_branches(d, -8.0, "ok_acc", "（b）装回 KMY 常闭：KM△ 线圈要等 KMY 释放才通电")
    print("[图 19-p3-3] 练习 2：空档 (a) 12 - 19 = -7 ms，(b) 12 ms")
    save_schem(d, P, "19_p3_3_ex2.png")


lowvolt_lamps()
short_test()
ex2_branches()
