"""17 自锁：除 17_sim.py 那张以外的所有配图。运行：python code/figs/17_figs.py
图上出现的每个数字都由本脚本打印（fs.mark 自动打印；其余用 print）。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from schem import *
import figstyle as fs

P = "17"


def rung_jog():
    """图 17-p1-1：点动控制回路（只有启动按钮和线圈）。"""
    with drawing() as d:
        d += elm.Dot(open=True).label("L", "left")
        d += elm.Line().right(0.8)
        d += PushNO().right().label("SB2 启动", ofst=0.6)
        d += elm.Line().right(0.8)
        d += Coil().right().label("KM 线圈", ofst=0.4)
        d += elm.Line().right(0.8)
        d += elm.Dot(open=True).label("N", "right")
    print("[图 17-p1-1] 点动控制回路：L → SB2 → KM 线圈 → N")
    save_schem(d, P, "17_p1_1_jog.png")


def rung_selflock(name, two_place=False):
    """自锁控制回路：L → SB1(常闭) → [SB2(常开) ∥ KM 自锁触点] → FR(常闭) → KM 线圈 → N。
    two_place=True 时画练习答案：两个停止按钮串联、两个启动按钮并联。"""
    with drawing() as d:
        d += elm.Dot(open=True).label("L", "left")
        d += elm.Line().right(0.6)
        d += PushNC().right().label("SB1 停止" if not two_place else "SB1 甲地停止", ofst=0.6)
        if two_place:
            d += PushNC().right().label("SB3 乙地停止", ofst=0.6)
        d += elm.Line().right(0.6)
        d += (a := elm.Dot())
        d += PushNO().right().label("SB2 启动" if not two_place else "SB2 甲地启动", ofst=0.6)
        d += (b := elm.Dot())
        d += elm.Line().right(0.6)
        d += ThermalNC().right().label("FR", ofst=0.6)
        d += elm.Line().right(0.6)
        d += Coil().right().label("KM 线圈", ofst=0.4)
        d += elm.Line().right(0.6)
        d += elm.Dot(open=True).label("N", "right")
        rows = [("KM 自锁触点", ContactNO)] if not two_place else [("SB4 乙地启动", PushNO), ("KM 自锁触点", ContactNO)]
        for i, (lab, E) in enumerate(rows):
            dy = 1.9 * (i + 1)
            d += elm.Line().down(dy).at(a.center)
            d += E().right().tox(b.center).label(lab, "bottom", ofst=0.25)
            d += elm.Line().up(dy)
    print(f"[图] {name}：自锁控制回路" + ("（两地控制）" if two_place else ""))
    save_schem(d, P, name)


def main_circuit():
    """图 17-p1-3：主电路（三相 380 V）：熔断器 FU1 → KM 主触点 → FR 发热元件 → 电动机。"""
    with drawing(fontsize=11) as d:
        xs = [0, 1.6, 3.2]
        ends = []
        for i, x in enumerate(xs):
            d += elm.Dot(open=True).at((x, 0)).label(f"L{i + 1}", "top")
            d += elm.Fuse().down().length(1.6)
            d += ContactNO().down().length(1.6)
            d += ThermalHeater().down().length(1.6)
            ends.append(d.here)
        m_y = ends[1][1] - 1.6
        d += elm.Line().at(ends[1]).down(0.6)
        d += (m := Motor3().down().length(1.0))
        d += elm.Line().at(ends[0]).down(0.6)
        d += elm.Line().right().tox(xs[1] - 0.35)
        d += elm.Line().to((xs[1] - 0.35, ends[1][1] - 0.75))
        d += elm.Line().at(ends[2]).down(0.6)
        d += elm.Line().left().tox(xs[1] + 0.35)
        d += elm.Line().to((xs[1] + 0.35, ends[1][1] - 0.75))
        # 三个主触点由同一个衔铁带动：灰色虚线（不是导线）
        y_c = -1.6 - 0.8 - 0.05
        d += elm.Line().at((xs[0] + 0.25, y_c)).to((xs[2] + 0.25, y_c)).linestyle("--").color("#808080")
        d += elm.Label().at((xs[2] + 1.9, y_c)).label("同一个 KM 衔铁带动\n（虚线≠导线）", fontsize=9, color="#4d4d4d")
        d += elm.Label().at((m.center[0] + 1.6, m.center[1])).label("电动机 M", fontsize=11)
        for y, lab in [(-0.8, "熔断器\nFU1"), (-2.4, "KM\n主触点"), (-4.0, "热继电器\n发热元件 FR")]:
            d += elm.Label().at((-1.3, y)).label(lab, fontsize=10)
    print("[图 17-p1-3] 主电路：三相 L1/L2/L3（线电压 380 V）")
    save_schem(d, P, "17_p1_3_main.png")


def logic(sb2, sb1, mode="ok"):
    """逐点计算 KM 状态（不考虑吸合延时）。mode:
    ok   = 正确：KM = (未按SB1) 且 (SB2 或 KM)
    jog  = 点动：KM = SB2
    wrongpos = 自锁触点并在 SB1+SB2 两端：KM = ((未按SB1) 且 SB2) 或 KM
    stopNO   = 停止按钮误用常开：KM = SB1 且 (SB2 或 KM)"""
    km = np.zeros_like(sb2, dtype=bool)
    for k in range(1, len(sb2)):
        prev = km[k - 1]
        if mode == "ok":
            km[k] = (not sb1[k]) and (sb2[k] or prev)
        elif mode == "jog":
            km[k] = sb2[k]
        elif mode == "wrongpos":
            km[k] = ((not sb1[k]) and sb2[k]) or prev
        elif mode == "stopNO":
            km[k] = sb1[k] and (sb2[k] or prev)
    return km


t = np.arange(0, 8, 0.001)
def pressed(a, b):
    return (t >= a) & (t < b)


def timeline_intuition():
    """图 17-p1-4：同样按一下启动、过一会按一下停止，点动电路和自锁电路的电机状态。"""
    sb2 = pressed(1, 1.4); sb1 = pressed(5, 5.4)
    jog = logic(sb2, sb1, "jog"); ok = logic(sb2, sb1, "ok")
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    ax.plot(t, sb2 * 0.8 + 6, **fs.LS["fb"], label="SB2 启动按钮（按下 = 高）")
    ax.plot(t, sb1 * 0.8 + 4, **fs.LS["third"], label="SB1 停止按钮（按下 = 高）")
    ax.plot(t, jog * 0.8 + 2, **{**fs.LS["bad"], "markevery": 400}, label="点动电路的电机（松手就停）")
    ax.plot(t, ok * 0.8 + 0, **fs.LS["vout"], label="自锁电路的电机")
    fs.ref_v(ax, 1.4, "松开启动按钮", y=0.80)
    fs.ref_v(ax, 5.0, "按停止按钮", y=0.80)
    assert jog[np.searchsorted(t, 2)] == 0 and ok[np.searchsorted(t, 2)] == 1 and ok[np.searchsorted(t, 6)] == 0
    print("[图 17-p1-4] 1–1.4 s 按启动，5–5.4 s 按停止；点动电路 1.4 s 停，自锁电路 5 s 停")
    ax.set_yticks([0.4, 2.4, 4.4, 6.4]); ax.set_yticklabels(["自锁\n电机", "点动\n电机", "SB1", "SB2"])
    ax.set_ylim(-0.4, 9.8); fs.axlabels(ax, "时间", "s")
    ax.legend(loc="upper center", fontsize=8, ncol=2)
    fs.save(fig, P, "17_p1_4_timeline.png")


def state_diagram():
    """图 17-p2-1：两个状态的状态图。"""
    fig, ax = fs.diagram(9, 3.4)
    s0 = fs.box(ax, 2.0, 1.7, "停\nKM 释放\n自锁触点断开", w=2.2, h=1.2)
    s1 = fs.box(ax, 7.0, 1.7, "转\nKM 吸合\n自锁触点闭合", w=2.2, h=1.2)
    fs.arrow(ax, (3.1, 2.05), (5.9, 2.05), None, bend=-0.25)
    ax.text(4.5, 2.75, "按下 SB2（且 SB1 没被按）", ha="center", fontsize=9)
    fs.arrow(ax, (5.9, 1.35), (3.1, 1.35), None, bend=-0.25)
    ax.text(4.5, 0.35, "按下 SB1 / FR 过载断开 / 电压太低", ha="center", fontsize=9)
    ax.text(2.0, 3.1, "松开 SB1、再来电：仍是「停」", ha="center", fontsize=9)
    ax.text(7.0, 3.1, "松开 SB2：仍是「转」", ha="center", fontsize=9)
    print("[图 17-p2-1] 状态图：停 ⇄ 转")
    fs.save(fig, P, "17_p2_1_states.png")


def wrong_wiring():
    """图 17-p2-3：两种典型接错与正确接法对比。"""
    sb2 = pressed(1, 1.4) | pressed(5.5, 5.9); sb1 = pressed(3.5, 3.9)
    ok = logic(sb2, sb1, "ok"); wp = logic(sb2, sb1, "wrongpos"); sn = logic(sb2, sb1, "stopNO")
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    ax.plot(t, sb2 * 0.8 + 6, **fs.LS["fb"], label="SB2 启动按钮（按下 = 高）")
    ax.plot(t, sb1 * 0.8 + 4, **fs.LS["third"], label="SB1 停止按钮（按下 = 高）")
    ax.plot(t, ok * 0.8 + 2, **fs.LS["good"], label="正确接法的 KM")
    ax.plot(t, wp * 0.8 + 0, **{**fs.LS["bad"], "markevery": 400}, label="错误①：自锁触点并到了 SB1 外面")
    ax.plot(t, sn * 0.8 - 2, **{**fs.LS["bad"], "markevery": 400}, label="错误②：停止按钮用了常开")
    fs.ref_v(ax, 3.5, "按停止", y=0.80)
    assert ok[np.searchsorted(t, 4.5)] == 0 and wp[np.searchsorted(t, 4.5)] == 1 and not sn.any()
    print("[图 17-p2-3] 1 s、5.5 s 按启动，3.5 s 按停止；错误①停不下来，错误②永远启动不了")
    ax.set_yticks([-1.6, 0.4, 2.4, 4.4, 6.4]); ax.set_yticklabels(["错误②", "错误①", "正确", "SB1", "SB2"])
    ax.set_ylim(-2.4, 9.8); fs.axlabels(ax, "时间", "s")
    ax.legend(loc="upper center", fontsize=8, ncol=2)
    fs.save(fig, P, "17_p2_3_wrong.png")


def hysteresis():
    """图 17-p3-1：电源电压慢慢升到 110% 再降回 0，KM 何时吸合、何时释放。"""
    PICK, DROP = 85, 45
    up = np.linspace(0, 110, 1101); dn = up[::-1]
    st_up = up >= PICK
    st_dn = dn >= DROP
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.axvspan(30, 60, color="0.9", zorder=0, label="手册释放电压范围 30%~60%")
    ax.plot(up, st_up * 1.0 + 0.03, **fs.LS["vin"], label="电压上升：85% 才吸合")
    ax.plot(dn, st_dn * 1.0 - 0.03, **fs.LS["vout"], label="电压下降：降到 45% 才释放")
    fs.ref_v(ax, PICK, "85%"); fs.ref_v(ax, DROP, "45%")
    print("[图 17-p3-1] 吸合门限 85%，释放门限 45%，阴影 30%~60%（TeSys D 手册释放范围）")
    ax.annotate("", xy=(PICK, 0.75), xytext=(PICK, 0.25), arrowprops=dict(arrowstyle="-|>", color=fs.C["vin"]))
    ax.annotate("", xy=(DROP, 0.25), xytext=(DROP, 0.75), arrowprops=dict(arrowstyle="-|>", color=fs.C["vout"]))
    assert st_up[np.searchsorted(up, 70)] == 0 and st_dn[np.argmin(abs(dn - 70))] == 1  # 70% 时取决于来历
    ax.set_yticks([0, 1]); ax.set_yticklabels(["释放", "吸合"]); ax.set_ylim(-0.3, 1.45)
    fs.axlabels(ax, "线圈电压（额定值的百分比）", "%")
    ax.legend(loc="center left", fontsize=8)
    fs.save(fig, P, "17_p3_1_hysteresis.png")


def wire_length():
    """图 17-p3-2：按钮盒离控制柜越远，线圈吸合瞬间拿到的电压越低（电阻粗略估算）。"""
    rho, A = 0.01724, 1.0                      # 铜电阻率 Ω·mm²/m，导线截面 1 mm²
    S_in = 70.0                                # 吸合瞬间视在功率 70 VA（TeSys D 手册）
    Lm = np.linspace(0, 400, 801)              # 按钮盒到控制柜的距离 / m
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    for U, key in [(24.0, "bad"), (220.0, "vout")]:
        Z = U ** 2 / S_in                      # 把吸合瞬间的线圈看成一个电阻 Z = U²/S
        Rw = rho * 2 * Lm / A                  # 来回两根线
        frac = Z / (Z + Rw) * 100
        ax.plot(Lm, frac, **{**fs.LS[key], **({"markevery": 100} if key == "bad" else {})}, label=f"控制电压 {U:g} V（吸合时线圈约 {Z:.1f} Ω）")
        L85 = (Z / 0.85 - Z) * A / (2 * rho)
        print(f"[图 17-p3-2] U = {U:g} V：Z = {Z:.2f} Ω，降到 85% 的距离 {L85:.0f} m")
        if L85 < 400:
            fs.mark(ax, L85, 85.0, fmt="{:.0f}", unit="%", dx=8, dy=4, color=fs.C[key])
            ax.text(L85 + 8, 70, f"约 {L85:.0f} m", color=fs.C[key], fontsize=9)
        else:
            fs.mark(ax, 400, frac[-1], fmt="{:.1f}", unit="%", dx=-30, dy=6, color=fs.C[key])
        if U == 24:
            assert 35 < L85 < 50
        else:
            assert L85 > 2000
    Z24 = 24.0 ** 2 / S_in
    print(f"[练习 3] 24 V、1.5 mm² 导线：降到 85% 的距离 {(Z24 / 0.85 - Z24) * 1.5 / (2 * rho):.0f} m")
    fs.ref_h(ax, 85, "吸合门限 85%", x=0.75)
    fs.axlabels(ax, "按钮盒到控制柜的距离", "m", "线圈吸合瞬间电压", "%")
    ax.set_ylim(40, 105); ax.legend(loc="lower left", fontsize=8)
    fs.save(fig, P, "17_p3_2_wire.png")


if __name__ == "__main__":
    rung_jog()
    rung_selflock("17_p1_2_selflock.png")
    main_circuit()
    timeline_intuition()
    state_diagram()
    wrong_wiring()
    hysteresis()
    wire_length()
    rung_selflock("17_p3_3_twoplace.png", two_place=True)
