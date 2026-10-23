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
    U_phase = 220.0                                   # 相电压：相线对零线
    U_line = U_phase * np.sqrt(3)                     # 线电压：两根相线之间 = 相电压 × √3（结论，推导见 19）
    print(f"[三相] 相电压 {U_phase:.0f} V × √3 = {U_line:.0f} V ≈ 380 V（线电压）；比值 {380 / 220:.2f}")
    assert abs(U_line - 380) < 2
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
    ax.plot(t, wp * 0.8 + 0, **{**fs.LS["bad"], "markevery": 400})   # 两条错误线同色同标记，直接在行旁写字区分
    ax.plot(t, sn * 0.8 - 2, **{**fs.LS["bad"], "markevery": 400})
    ax.text(4.2, 1.15, "错误①：自锁触点并到了 SB1 外面 → 按停止也停不下来", fontsize=8.5, color=fs.LS["bad"]["color"])
    ax.text(4.2, -0.85, "错误②：停止按钮用了常开 → 永远启动不了", fontsize=8.5, color=fs.LS["bad"]["color"])
    fs.ref_v(ax, 3.5, "按停止", y=0.80)
    assert ok[np.searchsorted(t, 4.5)] == 0 and wp[np.searchsorted(t, 4.5)] == 1 and not sn.any()
    print("[图 17-p2-3] 1 s、5.5 s 按启动，3.5 s 按停止；错误①停不下来，错误②永远启动不了")
    ax.set_yticks([-1.6, 0.4, 2.4, 4.4, 6.4]); ax.set_yticklabels(["错误②", "错误①", "正确", "SB1", "SB2"])
    ax.set_ylim(-2.4, 9.8); fs.axlabels(ax, "时间", "s")
    ax.legend(loc="upper center", fontsize=8, ncol=3)
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

# ---------- 图 17-p4-1：12 V 低压自锁实验的面包板接线 ----------
bb = Breadboard(30, "自锁低压版面包板俯视图（12 V 直流，12 V 继电器代替接触器）",
                rails=("+12 V", "0 V", "0 V", "+12 V"))
bb.chip(12, "继电器", npin=8,
        names={1: "COM1", 2: "NO1", 3: "线圈+", 4: "NC1", 8: "线圈−", 7: "COM2", 6: "NO2", 5: "NC2"})
bb.wire("a12", "T-12", "gnd")                     # 线圈− → 0 V
bb.wire("g13", "g14", "fb")                       # NO1 = 线圈+（节点 B）
bb.part("B-14", "j14", "1N4007", "D", lab_side="r")   # 续流二极管：阳极接 0 V，阴极接线圈+
bb.part("h14", "h19", "HL1 运行灯", "P", lab_side=1)
bb.wire("j19", "B-19", "gnd")
bb.wire("a13", "T+13", "pos")                     # COM2 → +12 V
bb.part("c14", "c19", "M「电机」灯", "P", lab_side=1)
bb.wire("a19", "T-19", "gnd")
bb.part("b15", "b24", "HL2 停止灯", "P", lab_side=1)
bb.wire("a24", "T-24", "gnd")
bb.module(1.0, -9.8, 4.6, 1.2, "SB1 停止（常闭，红）", fc="#f6dede")
bb.wire((3.3, -8.6), "B+3", "pos")
bb.wire((5.6, -9.2), "i12", "fb", via=[(8.0, -9.2), (8.0, -4.4)])
bb.module(10.6, -9.8, 3.8, 1.2, "SB2 启动（常开，绿）", fc="#def0de")
bb.wire((12.0, -8.6), "j12", "fb")
bb.wire((13.0, -8.6), "j13", "fb")
bb.wire("T+29", "B+29", "pos")
bb.wire("T-30", "B-30", "gnd")
bb.module(-3.2, 9.4, 4.4, 1.4, "12 V 直流电源\n（适配器或可调电源）")
bb.wire((1.2, 10.1), "T+1", "pos")
bb.wire((0.4, 9.4), "T-3", "gnd")
bb.note(20.5, -1.2, "引脚排列以继电器手册为准（本图为示意）", va="center")
bb.note(20.5, -2.0, "两只面板按钮用鳄鱼夹线接入", va="center")
bb.legend()
bb.save(P, "17_p4_1_breadboard.png")

# ---------- 图 17-p4-2：按实验顺序推演三只灯的状态 ----------
steps = ["上电", "按住 SB2", "松开 SB2", "按住 SB1", "松开 SB1", "按住 SB2", "松开 SB2",
         "拔掉电源", "插回电源"]
s1 = [0, 0, 0, 1, 0, 0, 0, 0, 0]        # 1 = 按下停止（常闭断开）
s2 = [0, 1, 0, 0, 0, 1, 0, 0, 0]
pw = [1, 1, 1, 1, 1, 1, 1, 0, 1]
k, ks = 0, []
for a, b, p in zip(s1, s2, pw):
    k = int(p and (not a) and (b or k))  # K' = 电源 · 非S1 · (S2 + K)
    ks.append(k)
hl1 = ks
hl2 = [int(p and not kk) for p, kk in zip(pw, ks)]
print("[数值] 推演结果（KM / HL1 = M 灯 / HL2）：" + "，".join(f"{s} {kk}{h2}" for s, kk, h2 in zip(steps, ks, hl2)))
assert ks == [0, 1, 1, 0, 0, 1, 1, 0, 0] and hl2 == [1, 0, 0, 1, 1, 0, 0, 0, 1]
fig, ax = plt.subplots(figsize=(8.8, 3.0))
rows = [("SB1 按下", s1, fs.C["bad"]), ("SB2 按下", s2, fs.C["vin"]), ("电源", pw, "0.3"),
        ("继电器吸合 / HL1 / M 灯", ks, fs.C["vout"]), ("HL2 停止灯", hl2, fs.C["third"])]
for r, (name, v, c) in enumerate(rows[::-1]):
    for i, x in enumerate(v):
        ax.add_patch(plt.Rectangle((i + 0.08, r + 0.15), 0.84, 0.7, fc=c if x else "white", ec=c, lw=1.0))
        ax.text(i + 0.5, r + 0.5, "亮" if (x and r < 2) else ("" if not x else "是"),
                ha="center", va="center", fontsize=8, color="w")
    ax.text(-0.1, r + 0.5, name, ha="right", va="center", fontsize=9)
ax.set_xlim(-3.2, len(steps)); ax.set_ylim(0, len(rows) + 0.1)
ax.set_xticks(np.arange(len(steps)) + 0.5); ax.set_xticklabels(steps, fontsize=8.5)
ax.set_yticks([]); [ax.spines[s].set_visible(False) for s in ("left", "top", "right")]
ax.set_title("实验操作顺序（从左到右）与应有状态：实心 = 是 / 亮", fontsize=10)
fs.save(fig, P, "17_p4_2_sequence.png")


# ======================= 补充原理图（图 17-p2-4 起） =======================
ACC = fs.C["bad"]


def rung_variant(d, y, mode="ok"):
    """在高度 y 画一条自锁控制回路（与 rung_selflock 同样的元件顺序）。
    mode="ok" 正确；"bypass" 自锁触点并在 SB1+SB2 整体两端（错误①）；"no_stop" 停止按钮用了常开（错误②）。"""
    d += (l0 := elm.Dot(open=True).at((0, y)).label("L", "left"))
    d += elm.Line().right(0.6)
    d += (a0 := elm.Dot())
    if mode == "no_stop":
        d += PushNO().right().label("SB1 停止（误用常开）", ofst=0.6, color=ACC).color(ACC)
    else:
        d += PushNC().right().label("SB1 停止", ofst=0.6)
    d += elm.Line().right(0.6)
    d += (a := elm.Dot())
    d += PushNO().right().label("SB2 启动", ofst=0.6)
    d += (b := elm.Dot())
    d += elm.Line().right(0.6)
    d += ThermalNC().right().label("FR", ofst=0.6)
    d += elm.Line().right(0.6)
    d += Coil().right().label("KM 线圈", ofst=0.4)
    d += elm.Line().right(0.6)
    d += elm.Dot(open=True).label("N", "right")
    if mode == "bypass":
        d += elm.Line().down(1.9).at(a0.center).color(ACC)
        d += ContactNO().right().tox(b.center).label("KM 自锁触点（并到了 SB1 外面）", "bottom", ofst=0.25, color=ACC).color(ACC)
        d += elm.Line().up(1.9).color(ACC)
    else:
        d += elm.Line().down(1.9).at(a.center)
        d += ContactNO().right().tox(b.center).label("KM 自锁触点", "bottom", ofst=0.25)
        d += elm.Line().up(1.9)


# ---------- 图 17-p2-4 正确接法与两种错误接法 ----------
with drawing(fontsize=11) as d:
    for i, (mode, title) in enumerate([("ok", "（a）正确：自锁触点只并在 SB2 两端，SB1 用常闭"),
                                       ("bypass", "（b）错误①：自锁触点并在 SB1 和 SB2 串联的两端"),
                                       ("no_stop", "（c）错误②：停止按钮用了常开触点")]):
        y = -6.0 * i
        d += elm.Label().at((-0.6, y + 2.3)).label(title, halign="left")
        rung_variant(d, y, mode)
save_schem(d, P, "17_p2_4_wrong_wiring.png")


# ---------- 图 17-p2-5 例 3：运行指示灯 HL1 与停机指示灯 HL2 ----------
with drawing(fontsize=11) as d:
    XN = 13.0
    d += elm.Dot(open=True).at((0, 1.2)).label("L", "top")
    d += elm.Line().down().toy(-5.2)
    d += elm.Dot(open=True).at((XN, 1.2)).label("N", "top")
    d += elm.Line().down().toy(-5.2)
    d += elm.Dot().at((0, 0))
    d += elm.Line().at((0, 0)).right(0.6)
    d += PushNC().right().label("SB1 停止", ofst=0.6)
    d += elm.Line().right(0.6)
    d += (a := elm.Dot())
    d += PushNO().right().label("SB2 启动", ofst=0.6)
    d += (b := elm.Dot())
    d += elm.Line().right(0.6)
    d += ThermalNC().right().label("FR", ofst=0.6)
    d += elm.Line().right(0.6)
    d += (c1 := elm.Dot())
    d += Coil().right().label("KM 线圈", ofst=0.4)
    d += (c2 := elm.Dot())
    d += elm.Line().right().tox(XN)
    d += elm.Dot()
    d += elm.Line().down(1.9).at(a.center)
    d += ContactNO().right().tox(b.center).label("KM 自锁触点", "bottom", ofst=0.25)
    d += elm.Line().up(1.9)
    d += elm.Line().down(1.6).at(c1.center).color(ACC)
    d += LampX().right().tox(c2.center).label("HL1 运行", "bottom", ofst=0.3, color=ACC).color(ACC)
    d += elm.Line().up(1.6).color(ACC)
    d += elm.Dot().at((0, -4.4)).color(ACC)
    d += elm.Line().at((0, -4.4)).right(3.0).color(ACC)
    d += ContactNC().right().label("KM 常闭辅助触点", "bottom", ofst=0.3, color=ACC).color(ACC)
    d += elm.Line().right(3.0).color(ACC)
    d += LampX().right().label("HL2 停机", "bottom", ofst=0.3, color=ACC).color(ACC)
    d += elm.Line().right().tox(XN).color(ACC)
    d += elm.Dot().color(ACC)
save_schem(d, P, "17_p2_5_lamps.png")


# ---------- 图 17-p2-6 12 V 低压实验接线（原理图） ----------
with drawing(fontsize=11) as d:
    XN = 14.0
    d += elm.Dot(open=True).at((0, 2.0)).label("+12 V（代替 L）", "top")
    d += elm.Line().down().toy(-5.4)
    d += elm.Dot(open=True).at((XN, 2.0)).label("−（代替 N）", "top")
    d += elm.Line().down().toy(-5.4)
    d += elm.Dot().at((0, 0))
    d += elm.Line().at((0, 0)).right(0.6)
    d += PushNC().right().label("停止按钮（常闭）", ofst=0.6)
    d += elm.Line().right(0.6)
    d += (a := elm.Dot())
    d += PushNO().right().label("启动按钮（常开）", ofst=0.6)
    d += (b := elm.Dot())
    d += elm.Line().right(1.2)
    d += (c1 := elm.Dot())
    d += Coil().right().label("继电器线圈 12 V", ofst=0.4)
    d += (c2 := elm.Dot())
    d += elm.Line().right().tox(XN)
    d += elm.Dot()
    d += elm.Line().down(1.9).at(a.center)
    d += ContactNO().right().tox(b.center).label("第一组常开触点（自锁）", "bottom", ofst=0.25)
    d += elm.Line().up(1.9)
    d += elm.Line().down(1.6).at(c1.center).color(ACC)
    d += elm.Diode().left().at((c2.center[0], c2.center[1] - 1.6)).to((c1.center[0], c1.center[1] - 1.6)).label("1N4007", "bottom", color=ACC).color(ACC)
    d += elm.Line().up(1.6).at((c2.center[0], c2.center[1] - 1.6)).color(ACC)
    d += elm.Dot().at((0, -4.6))
    d += elm.Line().at((0, -4.6)).right(2.4)
    d += ContactNO().right().label("第二组常开触点", "bottom", ofst=0.3)
    d += elm.Line().right(1.2)
    d += elm.Resistor().right().label("1 kΩ")
    d += elm.Line().right(0.8)
    d += elm.LED().right().label("LED（代替电动机）", ofst=0.4)
    d += elm.Line().right().tox(XN)
    d += elm.Dot()
save_schem(d, P, "17_p2_6_lowvolt.png")


# ---------- 图 17-p3-4 二线控制与三线控制 ----------
with drawing(fontsize=11) as d:
    d += elm.Label().at((-0.6, 2.4)).label("（a）二线控制：旋钮 / 拨动开关不会自己弹回，来电即转", halign="left")
    d += elm.Dot(open=True).at((0, 0)).label("L", "left")
    d += elm.Line().right(0.6)
    d += elm.Switch().right().length(2.4).label("旋钮 / 拨动开关（不复位）", ofst=0.4, color=ACC).color(ACC)
    d += elm.Line().right(2.5)
    d += ThermalNC().right().label("FR", ofst=0.6)
    d += elm.Line().right(0.6)
    d += Coil().right().label("KM 线圈", ofst=0.4)
    d += elm.Line().right(0.6)
    d += elm.Dot(open=True).label("N", "right")
    d += elm.Label().at((-0.6, -2.4)).label("（b）三线控制：会弹回的按钮 + KM 自锁触点，有失压保护", halign="left")
    rung_variant(d, -5.2, "ok")
save_schem(d, P, "17_p3_4_two_three_wire.png")


# ---------- 图 17-p3-5 控制线压降的等效电路 ----------
rho, dist, r_coil = 0.01724, 42.0, 8.2
r_w = rho * dist / 1.0
v_coil = 24 * r_coil / (r_coil + 2 * r_w)
print(f"[图 17-p3-5] 1 mm² 铜线 {dist:.0f} m：单根 {r_w:.2f} Ω，去回共 {2*r_w:.2f} Ω；线圈电压 {v_coil:.1f} V = {v_coil/24*100:.0f}%")
assert abs(v_coil / 24 - 0.85) < 0.01
with drawing(fontsize=11) as d:
    d += (src := elm.SourceSin().up().length(3.0))
    d += elm.Label().at((-0.6, 1.5)).label("24 V\n控制电源", halign="right")
    d += elm.Line().right(0.8)
    d += elm.Resistor().right().length(2.6).label("去线电阻", color=ACC).color(ACC)
    d += elm.Line().right(0.8)
    d += PushNO().right().label("SB2（远处按钮盒）", ofst=0.6)
    d += elm.Line().right(0.6)
    d += elm.Line().down(1.5)
    d += (kc := Coil().down().length(1.5))
    d += elm.Label().at((kc.center[0] + 0.5, kc.center[1])).label("KM 线圈\n（吸合瞬间约 8.2 Ω）", halign="left")
    d += elm.Line().left().tox(src.start[0] + 4.2)
    d += elm.Resistor().left().length(2.6).label("回线电阻", "bottom", color=ACC).color(ACC)
    d += elm.Line().left().tox(src.start[0])
    d += elm.Label().at((src.start[0] + 4.6, -1.5)).label(f"1 mm² 铜线，{dist:.0f} m：每根约 {r_w:.2f} Ω", color=ACC)
save_schem(d, P, "17_p3_5_wire_loop.png")
