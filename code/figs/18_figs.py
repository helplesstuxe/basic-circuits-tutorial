"""18 互锁：除 18_sim.py 那两张以外的所有配图，以及正文、练习要用到的数字。运行：python code/figs/18_figs.py
图上出现的每个数字都由本脚本打印（fs.mark 自动打印；其余用 print）。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from schem import *
import figstyle as fs

P = "18"


def main_circuit():
    """图 18-p1-1：正反转主电路。KM1 上下口一一对应；KM2 上口一致、下口把 L1、L3 对调。"""
    with drawing(fontsize=11) as d:
        X1 = [0, 1.5, 3.0]                 # KM1 三列
        X2 = [5.0, 6.5, 8.0]               # KM2 三列
        tap_y = [-2.6, -2.2, -1.8]         # L1、L2、L3 引到 KM2 的三条横线高度（错开，避免假交点）
        for i, x in enumerate(X1):
            d += elm.Dot(open=True).at((x, 0)).label(f"L{i + 1}", "top")
            d += elm.Fuse().down().length(1.4)
            d += elm.Line().down().toy(tap_y[i])
            d += elm.Dot()
            d += elm.Line().right().tox(X2[i])
            d += elm.Line().down().toy(-2.8)
            d += ContactNO().down().length(1.6)
            d += elm.Line().at((x, tap_y[i])).down().toy(-2.8)
            d += ContactNO().down().length(1.6)
            d += elm.Line().down().toy(-5.8)
        # KM2 下口调相：L1 列 → T3，L2 列 → T2，L3 列 → T1（三条横线错开高度）
        for x2, xt, y in [(X2[0], X1[2], -5.4), (X2[1], X1[1], -4.8), (X2[2], X1[0], -5.1)]:
            d += elm.Line().at((x2, -4.4)).down().toy(y)
            d += elm.Line().left().tox(xt)
            d += elm.Dot()
        for x2, tname in [(X2[0], "去 T3"), (X2[1], "去 T2"), (X2[2], "去 T1")]:   # 给 KM2 下口每根线标去向
            d += elm.Label().at((x2 + 0.45, -4.55)).label(tname, fontsize=9)
        for i, x in enumerate(X1):
            d += ThermalHeater().at((x, -5.8)).down().length(1.4)
            d += elm.Line().down(0.3)
            d += elm.Label().at((x + 0.4, -6.95)).label(f"T{i + 1}", fontsize=10)
        d += elm.Line().at((X1[1], -7.5)).down(0.4)
        d += (m := Motor3().down().length(1.0))
        d += elm.Line().at((X1[0], -7.5)).right().tox(X1[1] - 0.35)
        d += elm.Line().to((X1[1] - 0.35, -8.2))
        d += elm.Line().at((X1[2], -7.5)).left().tox(X1[1] + 0.35)
        d += elm.Line().to((X1[1] + 0.35, -8.2))
        for xs, txt in [(X1, "KM1 正转"), (X2, "KM2 反转")]:
            y_c = -2.8 - 0.8 - 0.05
            d += elm.Line().at((xs[0] + 0.25, y_c)).to((xs[2] + 0.25, y_c)).linestyle("--").color("#808080")
            d += elm.Label().at(((xs[0] - 1.3) if xs is X1 else (xs[2] + 1.3), -3.6)).label(txt.replace(" ", "\n"), fontsize=10)
        d += elm.Label().at((10.6, -5.1)).label("KM2 下口调相：\nL1 → T3，L3 → T1\nL2 不动", fontsize=9, color="#4d4d4d")
        d += elm.Label().at((m.center[0] + 1.6, m.center[1])).label("电动机 M", fontsize=11)
        d += elm.Label().at((-1.3, -0.7)).label("熔断器\nFU1", fontsize=10)
        d += elm.Label().at((-1.3, -6.5)).label("热继电器\nFR", fontsize=10)
    print("[图 18-p1-1] 主电路：KM1 L1→T1、L2→T2、L3→T3；KM2 L1→T3、L2→T2、L3→T1")
    save_schem(d, P, "18_p1_1_main.png")


def rung(d, y, items, x0, x1):
    """在高度 y 上从 x0 起依次画 items = [(元件类, 标签)]，最后连到 x1。'||' 开头表示并联块。"""
    d += elm.Line().at((x0, y)).right(0.4)
    for E, lab in items:
        if E == "par":                      # 并联块：上面一个元件，下面一个元件
            (E1, l1), (E2, l2) = lab
            a = d.here
            d += E1().right().label(l1, ofst=0.6)
            b = d.here
            d += elm.Line().at(a).down(1.5)
            d += E2().right().tox(b[0]).label(l2, "bottom", ofst=0.25)
            d += elm.Line().up(1.5)
            d += elm.Dot().at(a); d += elm.Dot().at(b)
            d += elm.Line().at(b).right(0.4)
        else:
            d += E().right().label(lab, ofst=0.6 if E is not Coil else 0.4)
            d += elm.Line().right(0.4)
    d += elm.Line().right().tox(x1)


def control(name, double=False):
    """控制回路。double=False：接触器互锁（图 18-p1-2）；True：按钮 + 接触器双重互锁（图 18-p2-1）。"""
    with drawing(fontsize=10) as d:
        d += elm.Dot(open=True).at((-7.0, 0)).label("L", "left")
        d += elm.Line().right(0.4)
        d += PushNC().right().label("SB1 停止", ofst=0.6)
        d += elm.Line().right(0.4)
        d += ThermalNC().right().label("FR", ofst=0.6)
        d += elm.Line().right().tox(0)
        d += elm.Dot()
        X1 = 15.5 if double else 12.0
        r1 = [("par", ((PushNO, "SB2 正转"), (ContactNO, "KM1 自锁")))]
        r2 = [("par", ((PushNO, "SB3 反转"), (ContactNO, "KM2 自锁")))]
        if double:
            r1 = [(PushNC, "SB3 常闭")] + r1
            r2 = [(PushNC, "SB2 常闭")] + r2
        r1 += [(ContactNC, "KM2 常闭"), (Coil, "KM1 线圈")]
        r2 += [(ContactNC, "KM1 常闭"), (Coil, "KM2 线圈")]
        rung(d, 0, r1, 0, X1)
        d += elm.Line().at((0, 0)).down(4.4)
        rung(d, -4.4, r2, 0, X1)
        d += elm.Line().at((X1, 0)).down(4.4)
        d += elm.Dot().at((X1, 0))
        d += elm.Line().at((X1, -4.4)).right(0.6)
        d += elm.Dot(open=True).label("N", "right")
    print(f"[图] {name}：控制回路" + ("（双重互锁）" if double else "（接触器互锁）"))
    save_schem(d, P, name)


# ---------------- 简化逻辑（不计吸合 / 释放延时），给直觉篇的时序图 ----------------
t = np.arange(0, 6, 0.001)
def pressed(a, b):
    return (t >= a) & (t < b)


def logic(sb2, sb3, sb1, elec):
    k1 = np.zeros_like(t, dtype=bool); k2 = np.zeros_like(t, dtype=bool)
    for k in range(1, len(t)):
        p1 = (not sb1[k]) and (sb2[k] or k1[k - 1]) and (not (elec and k2[k - 1]))
        p2 = (not sb1[k]) and (sb3[k] or k2[k - 1]) and (not (elec and k1[k - 1]))
        k1[k], k2[k] = p1, p2
    return k1, k2


def timeline_intuition():
    """图 18-p1-3：正转运行中误按反转——不互锁 vs 接触器互锁。"""
    sb2 = pressed(1, 1.3); sb3 = pressed(2.5, 2.8); sb1 = pressed(4.5, 4.8)
    n1, n2 = logic(sb2, sb3, sb1, False); e1, e2 = logic(sb2, sb3, sb1, True)
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.plot(t, sb2 * 0.6 + 8.4, **fs.LS["fb"], label="SB2 正转按钮")
    ax.plot(t, sb3 * 0.6 + 7.4, **fs.LS["third"], label="SB3 反转按钮")
    ax.plot(t, n1 * 0.6 + 5.2, **fs.LS["vout"], label="KM1 正转")
    ax.plot(t, n2 * 0.6 + 4.2, **fs.LS["vin"], label="KM2 反转")
    s = n1 & n2
    ax.plot(t[s][::120], np.full(s.sum(), 6.1)[::120], color=fs.C["bad"], ls="none", marker="x", label="两只同时吸合 = 相间短路")
    ax.plot(t, e1 * 0.6 + 1.6, **fs.LS["vout"])
    ax.plot(t, e2 * 0.6 + 0.6, **fs.LS["vin"])
    fs.ref_v(ax, 2.5, "误按反转", y=0.99)
    ax.text(0.05, 6.5, "不互锁", fontsize=10); ax.text(0.05, 2.5, "接触器互锁", fontsize=10)
    assert s.sum() > 0 and not (e1 & e2).any() and e1[np.searchsorted(t, 3.5)] and not e2[np.searchsorted(t, 3.5)]
    print(f"[图 18-p1-3] 1 s 按正转、2.5 s 误按反转、4.5 s 按停止：不互锁时同时吸合 {s.sum() / 1000:.1f} s；接触器互锁时 KM2 始终不吸合")
    ax.set_yticks([0.9, 1.9, 4.5, 5.5, 7.7, 8.7]); ax.set_yticklabels(["KM2", "KM1", "KM2", "KM1", "SB3", "SB2"])
    ax.set_ylim(0.2, 9.8); fs.axlabels(ax, "时间", "s")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)
    fs.save(fig, P, "18_p1_3_timeline.png")


def phase_check():
    """换相：一种接法 = 三根进线 L1/L2/L3 分别接到电动机哪个端子。相序方向 = 置换的奇偶性。"""
    def direction(perm):                    # perm[i] = 第 i 根进线接到的端子编号（0、1、2）
        inv = sum(1 for i in range(3) for j in range(i + 1, 3) if perm[i] > perm[j])
        return "正转" if inv % 2 == 0 else "反转"
    def name(perm):
        return "、".join(f"L{i + 1}→T{p + 1}" for i, p in enumerate(perm))
    cases = [("KM1 正转", (0, 1, 2)), ("KM2 对调 L1、L3", (2, 1, 0)), ("对调 L1、L2", (1, 0, 2)),
             ("三根轮换一格", (1, 2, 0)), ("三根轮换两格", (2, 0, 1))]
    out = {}
    for lab, p in cases:
        out[lab] = direction(p)
        print(f"[换相] {lab}：{name(p)} → {out[lab]}")
    assert out["KM2 对调 L1、L3"] == "反转" and out["三根轮换一格"] == "正转" and out["三根轮换两格"] == "正转"
    fwd, rev = (0, 1, 2), (2, 1, 0)
    pairs = [f"L{i + 1}–L{rev.index(fwd[i]) + 1}" for i in range(3) if rev[i] != fwd[i]]
    print(f"[短路] KM1、KM2 同时闭合：端子 T1 同时接 L1 和 L3 → 被短接的两相：{pairs[0]}")
    U, Z = 380.0, 0.1
    print(f"[短路] 示意：线电压 {U:.0f} V，整个短路回路阻抗只有 {Z} Ω（示意值）时，电流 ≈ {U / Z:.0f} A")


# ---------------- 带延时的状态机（同 18_sim.py 的写法），给参数与调试篇 ----------------
def machine(t_pick, t_drop, mode, t_end=0.6, weld_at=None, ev=None):
    """mode: 'button' 只做按钮互锁；'double' 双重互锁。返回 KM1/KM2 主触点、KM1 线圈。
    ev = dict(sb2=(a,b), sb3=(a,b), sb1=(a,b))，weld_at：KM1 主触点在此刻之后熔焊（不再释放）。"""
    dt = 1e-3; tt = np.arange(0, t_end, dt)
    pr = lambda ab: (tt >= ab[0]) & (tt < ab[1]) if ab else np.zeros_like(tt, dtype=bool)
    sb2, sb3, sb1 = pr(ev.get("sb2")), pr(ev.get("sb3")), pr(ev.get("sb1"))
    k1 = np.zeros_like(tt, dtype=bool); k2 = k1.copy(); c1 = k1.copy(); c2 = k1.copy()
    n1 = n2 = 0.0
    for k in range(1, len(tt)):
        n1 = n1 + dt if c1[k - 1] != k1[k - 1] else 0.0
        n2 = n2 + dt if c2[k - 1] != k2[k - 1] else 0.0
        k1[k] = (not k1[k - 1] and n1 >= t_pick - 1e-9) or (k1[k - 1] and n1 < t_drop - 1e-9)
        if weld_at is not None and tt[k] >= weld_at and k1[k - 1]:
            k1[k] = True                       # 主触点焊死：衔铁回不去，常闭辅助触点也保持断开（镜像触点）
        k2[k] = (not k2[k - 1] and n2 >= t_pick - 1e-9) or (k2[k - 1] and n2 < t_drop - 1e-9)
        p1 = (not sb1[k]) and (sb2[k] or k1[k]) and not sb3[k]
        p2 = (not sb1[k]) and (sb3[k] or k2[k]) and not sb2[k]
        if mode == "double":
            p1 = p1 and not k2[k]; p2 = p2 and not k1[k]
        c1[k], c2[k] = p1, p2
    return tt, k1, k2, c1


def gap_sweep():
    """图 18-p3-1：直接反转时，'KM1 主触点断开' 到 'KM2 主触点闭合' 之间的空档（负数 = 重叠 = 短路）。"""
    td = np.arange(4, 20, 1)                    # KM1 释放时间 4~19 ms（TeSys D 手册范围）
    ev = dict(sb2=(0.05, 0.10), sb3=(0.30, 0.45))
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.axhspan(-12, 0, color=fs.C["bad"], alpha=0.10, lw=0)
    for tp, ls in [(12, "bad"), (17, "third"), (22, "fb")]:
        gaps = []
        for x in td:
            tt, k1, k2, _ = machine(tp / 1e3, x / 1e3, "button", ev=ev)
            off = tt[np.flatnonzero(k1)[-1] + 1]; on = tt[np.argmax(k2)]
            gaps.append((on - off) * 1e3)
            assert abs(gaps[-1] - (tp - x)) < 1.01      # 状态机结果 = 吸合时间 − 释放时间
        sty = {**fs.LS[ls], **({"markevery": 3} if ls == "bad" else {})}
        ax.plot(td, gaps, **sty, label=f"只做按钮互锁，KM2 吸合 {tp} ms")
        print(f"[图 18-p3-1] 按钮互锁、KM2 吸合 {tp} ms：空档从 {gaps[0]:.0f} ms（KM1 释放 4 ms）到 {gaps[-1]:.0f} ms（释放 19 ms）")
    worst = 12 - 19
    fs.mark(ax, 19, worst, fmt="{:.0f}", unit=" ms", dx=-48, dy=-4, color=fs.C["bad"])
    tt, k1, k2, _ = machine(0.012, 0.019, "double", ev=ev)
    gd = (tt[np.argmax(k2)] - tt[np.flatnonzero(k1)[-1] + 1]) * 1e3
    ax.axhline(gd, **fs.LS["good"], label=f"双重互锁（最快的 KM2）：空档 = 吸合时间")
    print(f"[图 18-p3-1] 双重互锁、最快 KM2（12 ms）、最慢 KM1（19 ms）：空档 {gd:.0f} ms，与 KM1 释放时间无关")
    assert gd >= 11.99 and worst < 0
    fs.ref_h(ax, 0, "0：再往下就是两只同时闭合", x=0.02, ha="left")
    ax.set_ylim(-12, 22); fs.axlabels(ax, "KM1 释放时间", "ms", "换向空档", "ms")
    ax.legend(loc="upper right", fontsize=8)
    fs.save(fig, P, "18_p3_1_gap.png")


def welded():
    """图 18-p3-2：KM1 主触点熔焊后按反转——只做按钮互锁 vs 双重互锁。"""
    ev = dict(sb2=(0.2, 0.4), sb1=(1.0, 1.2), sb3=(1.6, 1.9))
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    rows = []
    for j, mode in enumerate(["button", "double"]):
        tt, k1, k2, c1 = machine(0.020, 0.010, mode, t_end=2.5, weld_at=0.8, ev=ev)
        y0 = 4.6 if mode == "button" else 0.4
        ax.plot(tt, c1 * 0.6 + y0 + 2.0, **fs.LS["cur"], label="KM1 线圈有电" if j == 0 else None)
        ax.plot(tt, k1 * 0.6 + y0 + 1.0, **fs.LS["vout"], label="KM1 主触点闭合" if j == 0 else None)
        ax.plot(tt, k2 * 0.6 + y0, **fs.LS["vin"], label="KM2 主触点闭合" if j == 0 else None)
        s = k1 & k2
        if s.any():
            ax.plot(tt[s][::80], np.full(s.sum(), y0 + 3.0)[::80], color=fs.C["bad"], ls="none", marker="x", label="相间短路")
        rows.append((mode, s.sum() / 1000))
        print(f"[图 18-p3-2] KM1 熔焊、1.0 s 按停止、1.6 s 按反转：{'只做按钮互锁' if mode == 'button' else '双重互锁'} → 同时闭合 {s.sum() / 1000:.2f} s")
    assert rows[0][1] > 0 and rows[1][1] == 0
    fs.ref_v(ax, 1.0, "按停止", y=0.99); fs.ref_v(ax, 1.6, "按反转", y=0.99)
    ax.text(0.02, 8.1, "只做按钮互锁", fontsize=10); ax.text(0.02, 3.6, "双重互锁", fontsize=10)
    ax.set_yticks([0.7, 1.7, 2.7, 4.9, 5.9, 6.9]); ax.set_yticklabels(["KM2", "KM1 主", "KM1 线圈"] * 2)
    ax.set_ylim(0, 9.2); fs.axlabels(ax, "时间", "s")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8)
    fs.save(fig, P, "18_p3_2_welded.png")


def exercises():
    """练习用数字。"""
    tp, tdr = 15, 18
    print(f"[练习 1] 按钮互锁：KM2 吸合 {tp} ms、KM1 释放 {tdr} ms → 空档 {tp - tdr} ms（重叠 {tdr - tp} ms）；双重互锁 → 空档 {tp} ms")
    tt, k1, k2, _ = machine(tp / 1e3, tdr / 1e3, "button", ev=dict(sb2=(0.05, 0.1), sb3=(0.3, 0.45)))
    ov = (k1 & k2).sum()
    print(f"[练习 1] 状态机核对：同时闭合 {ov} ms")
    assert ov == tdr - tp


if __name__ == "__main__":
    main_circuit()
    control("18_p1_2_control.png", double=False)
    timeline_intuition()
    control("18_p2_1_double.png", double=True)
    phase_check()
    gap_sweep()
    welded()
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
        hs = [Line2D([], [], color=WIRE[k][0], lw=2.4, label=WIRE[k][1]) for k in WIRE if k in self.used]
        self.ax.legend(handles=hs, loc=loc, ncol=len(hs), fontsize=8.5, frameon=False,
                       bbox_to_anchor=(0.5, -0.01))

    def save(self, prefix, name):
        return fs.save(self.fig, prefix, name)

# ---------- 图 18-p4-1：12 V 低压互锁实验的面包板接线 ----------
WIRE["sig"] = (fs.C["vin"], "KA1 线圈回路（经 KA2 常闭）")
WIRE["neg"] = (fs.C["third"], "KA2 线圈回路（经 KA1 常闭）")
WIRE["fb"] = (fs.C["fb"], "按钮引线")
bb = Breadboard(40, "互锁低压版面包板俯视图（12 V 直流，两只 12 V 继电器代替正反转接触器）",
                size=(12, 6.8), rails=("+12 V 经SB1", "0 V", "0 V", "+12 V 经SB1"))
pins = {1: "COM1", 2: "NO1", 3: "线圈+", 4: "NC1", 8: "线圈−", 7: "COM2", 6: "NO2", 5: "NC2"}
bb.chip(6, "KA1 正转", npin=8, names=pins)
bb.chip(30, "KA2 反转", npin=8, names=pins)
for c in (6, 30):
    bb.wire(f"a{c}", f"T-{c}", "gnd")             # 线圈− → 0 V
    bb.wire(f"j{c}", f"B+{c}", "pos")             # COM1 → SB1 之后的 +12 V
bb.part("B-8", "j8", "VD1", "D", lab_side="r")    # 续流二极管：阳极 0 V，阴极线圈+
bb.part("B-32", "j32", "VD2", "D", lab_side="r")
bb.part("h8", "h3", "HL1", "P", lab_side=1)
bb.wire("j3", "B-3", "gnd")
bb.part("g32", "g37", "HL2", "P", lab_side=1)
bb.wire("j37", "B-37", "gnd")
# KA1 回路：NO1（第 7 列下）→ KA2 的 NC2（第 33 列上）→ KA2 的 COM2（第 31 列上）→ KA1 线圈+（第 8 列下）
bb.wire("g7", "g12", "sig"); bb.wire("f12", "d12", "sig"); bb.wire("c12", "c33", "sig")
bb.wire("b31", "b14", "sig"); bb.wire("d14", "f14", "sig"); bb.wire("i14", "i8", "sig")
# KA2 回路：NO1（第 31 列下）→ KA1 的 NC2（第 9 列上）→ KA1 的 COM2（第 7 列上）→ KA2 线圈+（第 32 列下）
bb.wire("g31", "g26", "neg"); bb.wire("f26", "d26", "neg"); bb.wire("a26", "a9", "neg")
bb.wire("b7", "b10", "neg"); bb.wire("d10", "f10", "neg"); bb.wire("h10", "h32", "neg")
bb.wire("T+39", "B+39", "pos")
bb.wire("T-40", "B-40", "gnd")
bb.module(-3.2, 9.4, 4.4, 1.4, "12 V 直流电源")
bb.wire((0.4, 9.4), "T-3", "gnd")
bb.module(4.0, 9.5, 5.0, 1.2, "SB1 停止（常闭，红）", fc="#f6dede")
bb.wire((1.2, 10.1), (4.0, 10.1), "pos")
bb.wire((9.0, 10.1), "T+11", "pos", via=[(11.0, 10.1)])
bb.module(4.4, -9.8, 3.6, 1.2, "SB2 正转（常开）", fc="#def0de")
bb.wire((6.0, -8.6), "i6", "fb"); bb.wire((7.0, -8.6), "i7", "fb")
bb.module(28.4, -9.8, 3.6, 1.2, "SB3 反转（常开）", fc="#def0de")
bb.wire((30.0, -8.6), "i30", "fb"); bb.wire((31.0, -8.6), "i31", "fb")
bb.note(14.5, 10.0, "引脚排列以继电器手册为准（本图为示意）", va="center")
bb.legend()
bb.save(P, "18_p4_1_breadboard.png")


# ---------- 图 18-p4-2：按实验顺序推演两只继电器的状态 ----------
def interlock_steps(seq, bypass=False):
    """seq：每步 (S1, S2, S3)；按 K1' = 非S1·(S2+K1)·非K2、K2' = 非S1·(S3+K2)·非K1 迭代到稳定。
    bypass=True 表示两只互锁常闭都被跳线短接（式子里去掉 非K2、非K1）。"""
    k1 = k2 = 0
    out = []
    for s1, s2, s3 in seq:
        for _ in range(4):
            n1 = int((not s1) and (s2 or k1) and (bypass or not k2))
            n2 = int((not s1) and (s3 or k2) and (bypass or not k1))
            k1, k2 = n1, n2
        out.append((k1, k2))
    return out


steps = ["上电", "按住 SB2", "松开 SB2", "按住 SB3", "松开 SB3", "按住 SB1", "松开 SB1",
         "按住 SB3", "松开 SB3", "按住 SB2", "按 SB1 停", "短接后按 SB2", "再按 SB3", "按 SB1 停"]
seq = [(0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 0, 0), (1, 0, 0), (0, 0, 0),
       (0, 0, 1), (0, 0, 0), (0, 1, 0), (1, 0, 0)]
seq_b = [(0, 1, 0), (0, 0, 1), (1, 0, 0)]
res = interlock_steps(seq) + interlock_steps(seq_b, bypass=True)
k1s = [a for a, _ in res]; k2s = [b for _, b in res]
print("[数值] 推演结果（KA1 KA2）：" + "，".join(f"{s} {a}{b}" for s, a, b in zip(steps, k1s, k2s)))
assert k1s == [0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0]
assert k2s == [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0]
allseq = seq + seq_b
fig, ax = plt.subplots(figsize=(10.4, 3.2))
rows = [("SB1 按下", [s[0] for s in allseq], fs.C["bad"]), ("SB2 按下", [s[1] for s in allseq], fs.C["vin"]),
        ("SB3 按下", [s[2] for s in allseq], fs.C["third"]),
        ("KA1 吸合 / HL1 亮", k1s, fs.C["vout"]), ("KA2 吸合 / HL2 亮", k2s, fs.C["fb"])]
for r, (name, v, c) in enumerate(rows[::-1]):
    for i, x in enumerate(v):
        ax.add_patch(plt.Rectangle((i + 0.08, r + 0.15), 0.84, 0.7, fc=c if x else "white", ec=c, lw=1.0))
        if x and r < 2:
            ax.text(i + 0.5, r + 0.5, "亮", ha="center", va="center", fontsize=8, color="w")
    ax.text(-0.1, r + 0.5, name, ha="right", va="center", fontsize=9)
ax.axvline(len(seq), color="0.3", ls="--", lw=1.0)
ax.text(len(seq) + 0.15, len(rows) + 0.15, "断电后短接两只互锁常闭", ha="left", va="bottom", fontsize=8.5,
        color=fs.C["bad"])
ax.text(len(seq) / 2, len(rows) + 0.15, "正常互锁", ha="center", va="bottom", fontsize=8.5)
ax.set_xlim(-3.4, len(steps)); ax.set_ylim(0, len(rows) + 0.8)
ax.set_xticks(np.arange(len(steps)) + 0.5); ax.set_xticklabels(steps, fontsize=8, rotation=30, ha="right")
ax.set_yticks([]); [ax.spines[s].set_visible(False) for s in ("left", "top", "right")]
fs.save(fig, P, "18_p4_2_sequence.png")

# ---------- 测量表里的计算值 ----------
V, RC, P_LAMP = 12.0, 400.0, 1.0
i_coil = V / RC * 1000
i_lamp = P_LAMP / V * 1000
print(f"[数值] 线圈电流 {V:.0f} V ÷ {RC:.0f} Ω = {i_coil:.0f} mA；1 W 灯泡电流约 {i_lamp:.0f} mA；"
      f"一路合计约 {i_coil + i_lamp:.0f} mA；短接实验两路同时吸合约 {2 * (i_coil + i_lamp):.0f} mA")
assert round(i_coil) == 30 and round(i_lamp) == 83


# ======================= page1–3 补充原理图（国标元件） =======================
ACC = fs.C["bad"]


def rung_c(d, y, items, x0, x1, gap=0.4):
    """rung 的带颜色版：items 里每项 (类, 标签[, 颜色])，或 ("par", (类, 标签[, 颜色]), (类, 标签[, 颜色]))。"""
    def put(E, lab, c=None, **kw):
        e = E().right(**kw)
        if c:
            e = e.color(c)
        return e.label(lab, ofst=0.6 if E is not Coil else 0.4, color=c or "black")
    d += elm.Line().at((x0, y)).right(gap)
    for it in items:
        if it[0] == "par":
            t1, t2 = it[1], it[2]
            a = d.here
            d += put(*t1)
            b = d.here
            c2 = t2[2] if len(t2) > 2 else None
            d += elm.Line().at(a).down(1.5).color(c2 or "black")
            e = t2[0]().right().tox(b[0])
            if c2:
                e = e.color(c2)
            d += e.label(t2[1], "bottom", ofst=0.25, color=c2 or "black")
            d += elm.Line().up(1.5).color(c2 or "black")
            d += elm.Dot().at(a); d += elm.Dot().at(b)
            d += elm.Line().at(b).right(gap)
        else:
            d += put(*it)
            d += elm.Line().right(gap)
    if x1 is not None:
        d += elm.Line().right().tox(x1)


def lowvolt_interlock():
    """图 18-p2-4：12 V 低压互锁实验。继电器线圈两端各并 1 kΩ + LED 和反并的 1N4007。"""
    XN = 17.6
    with drawing(fontsize=10) as d:
        d += elm.Dot(open=True).at((-1.0, 2.2)).label("+12 V（代替 L）", "top")
        d += elm.Line().down().toy(-10.6)
        d += elm.Dot(open=True).at((XN, 2.2)).label("−（代替 N）", "top")
        d += elm.Line().down().toy(-10.6)
        d += elm.Dot().at((-1.0, 0))
        d += elm.Line().at((-1.0, 0)).right(0.6)
        d += PushNC().right().label("SB1 停止（常闭）", ofst=0.6)
        d += elm.Line().right(0.4)
        d += elm.Dot()
        xs = d.here[0]
        for k, (y, sb, me, other) in enumerate([(0, "SB2 正转", "KM1", "KM2"), (-5.6, "SB3 反转", "KM2", "KM1")]):
            if k:
                d += elm.Line().at((xs, 0)).down().toy(y)
            items = [("par", (PushNO, sb + "（常开）"), (ContactNO, me + " 第一组常开（自锁）")),
                     (ContactNC, other + " 第二组常闭（互锁）")]
            d += elm.Line().at((xs, y)).right(0.4)
            rung_c(d, y, items, xs, None, gap=0.4)
            d += elm.Line().right().tox(11.0)
            # 线圈 + 两条并联支路
            a = d.here
            d += (c := Coil().right(4.2).label(me + " 线圈 12 V", ofst=0.4))
            b = d.here
            d += elm.Dot().at(a); d += elm.Dot().at(b)
            d += elm.Line().at(b).right().tox(XN)
            d += elm.Dot()
            d += elm.Line().at(a).down(1.4).color(ACC)
            d += elm.Line().right(0.4).color(ACC)
            d += elm.Resistor().right(1.6).color(ACC).label("1 kΩ", "bottom", ofst=0.2, color=ACC)
            d += elm.LED().right(2.2).color(ACC).label("LED", "bottom", ofst=0.2, color=ACC)
            d += elm.Line().up(1.4).color(ACC)
            d += elm.Line().at((a[0], y - 1.4)).down(1.4).color(ACC)
            d += elm.Diode().at((b[0], y - 2.8)).to((a[0], y - 2.8)).color(ACC)   # 阴极朝 + 端：反并
            d += elm.Line().at((b[0], y - 1.4)).down(1.4).color(ACC)
            d += elm.Label().at(((a[0] + b[0]) / 2, y - 3.35)).label("1N4007", color=ACC)
            d += elm.Dot().at((a[0], y - 1.4)).color(ACC); d += elm.Dot().at((b[0], y - 1.4)).color(ACC)
    print("[图 18-p2-4] 12 V 互锁实验：LED 串 1 kΩ 并在线圈两端，1N4007 反并在线圈两端，FR 省略")
    save_schem(d, P, "18_p2_4_lowvolt.png")


def control_at(d, oy, items1, items2, X1=13.5, title=None):
    """在高度 oy 画一套两行控制回路：L — SB1 — FR — 分两路 — N。"""
    if title:
        d += elm.Label().at((-7.0, oy + 2.6)).label(title, halign="left", fontsize=11)
    d += elm.Dot(open=True).at((-7.0, oy)).label("L", "left")
    d += elm.Line().right(0.4)
    d += PushNC().right().label("SB1 停止", ofst=0.6)
    d += elm.Line().right(0.4)
    d += ThermalNC().right().label("FR", ofst=0.6)
    d += elm.Line().right().tox(0)
    d += elm.Dot()
    rung_c(d, oy, items1, 0, X1)
    d += elm.Line().at((0, oy)).down(4.4)
    rung_c(d, oy - 4.4, items2, 0, X1)
    d += elm.Line().at((X1, oy)).down(4.4)
    d += elm.Dot().at((X1, oy))
    d += elm.Line().at((X1, oy - 4.4)).right(0.6)
    d += elm.Dot(open=True).label("N", "right")


def button_only_vs_double():
    """图 18-p3-3：（a）只做按钮互锁（没有接触器常闭）；（b）双重互锁。"""
    with drawing(fontsize=10) as d:
        p1 = ("par", (PushNO, "SB2 正转"), (ContactNO, "KM1 自锁"))
        p2 = ("par", (PushNO, "SB3 反转"), (ContactNO, "KM2 自锁"))
        control_at(d, 0, [(PushNC, "SB3 常闭"), p1, (Coil, "KM1 线圈")],
                   [(PushNC, "SB2 常闭"), p2, (Coil, "KM2 线圈")], X1=13.5,
                   title="（a）只做按钮互锁：线圈前面没有对方接触器的常闭触点")
        control_at(d, -9.2, [(PushNC, "SB3 常闭"), p1, (ContactNC, "KM2 常闭", ACC), (Coil, "KM1 线圈")],
                   [(PushNC, "SB2 常闭"), p2, (ContactNC, "KM1 常闭", ACC), (Coil, "KM2 线圈")], X1=13.5,
                   title="（b）双重互锁：再串入对方接触器的常闭辅助触点")
    print("[图 18-p3-3] （a）只做按钮互锁 （b）双重互锁")
    save_schem(d, P, "18_p3_3_button_only.png")


def self_lock_nc():
    """图 18-p3-4：练习 2。（a）KM1 回路误串自己的常闭；（b）正确：串 KM2 常闭。"""
    with drawing(fontsize=10) as d:
        for k, (oy, nc, c, t) in enumerate([(0, "KM1 常闭（接错：自己的）", ACC, "（a）错误：KM1 线圈回路里串的是 KM1 自己的常闭触点"),
                                             (-5.4, "KM2 常闭（对方的）", None, "（b）正确：串 KM2 的常闭辅助触点")]):
            d += elm.Label().at((0, oy + 2.4)).label(t, halign="left", fontsize=11)
            d += elm.Dot(open=True).at((0, oy)).label("L", "left")
            item = (ContactNC, nc, c) if c else (ContactNC, nc)
            rung_c(d, oy, [(PushNC, "SB1 停止"), ("par", (PushNO, "SB2 正转"), (ContactNO, "KM1 自锁")),
                           item, (Coil, "KM1 线圈")], 0, 16.5)
            d += elm.Dot(open=True).label("N", "right")
    print("[图 18-p3-4] 练习 2：自己锁自己 vs 正确互锁")
    save_schem(d, P, "18_p3_4_self_nc.png")


def phase_swap_vs_rotate():
    """图 18-p3-5：练习 3。KM2 下口（a）对调 L1、L3；（b）轮换一格 L1→T2、L2→T3、L3→T1。"""
    with drawing(fontsize=10) as d:
        for ox, perm, t in [(0, (2, 1, 0), "（a）对调两相：L1→T3，L3→T1\n（反转）"),
                            (8.0, (1, 2, 0), "（b）轮换一格：L1→T2，L2→T3，L3→T1\n（仍是正转）")]:
            X = [ox + 0, ox + 1.5, ox + 3.0]
            d += elm.Label().at((ox + 1.8, 1.7)).label(t, fontsize=10)
            for i, x in enumerate(X):
                d += elm.Dot(open=True).at((x, 0)).label(f"L{i + 1}", "top")
                d += ContactNO().at((x, -0.3)).down().length(1.6)
                d += elm.Line().at((x, 0)).down(0.3)
            yc = -0.3 - 0.8 - 0.05
            d += elm.Line().at((X[0] + 0.25, yc)).to((X[2] + 0.25, yc)).linestyle("--").color("#808080")
            d += elm.Label().at((ox + 3.9, -1.1)).label("KM2", fontsize=10)
            hs = [-2.4, -2.9, -3.4]
            XT = [x + 0.6 for x in X]
            for i, x in enumerate(X):
                t_ = perm[i]
                c = ACC if t_ != i else "black"
                d += elm.Line().at((x, -1.9)).to((x, hs[i])).color(c)
                d += elm.Line().to((XT[t_], hs[i])).color(c)
                d += elm.Line().to((XT[t_], -4.5)).color(c)
            for i, x in enumerate(XT):
                d += elm.Label().at((x + 0.4, -4.2)).label(f"T{i + 1}", fontsize=10)
            X = XT
            d += elm.Line().at((X[1], -4.5)).down(0.4)
            d += (m := Motor3().down().length(1.0))
            d += elm.Line().at((X[0], -4.5)).right().tox(X[1] - 0.35)
            d += elm.Line().to((X[1] - 0.35, -5.2))
            d += elm.Line().at((X[2], -4.5)).left().tox(X[1] + 0.35)
            d += elm.Line().to((X[1] + 0.35, -5.2))
    print("[图 18-p3-5] 练习 3：对调两相（反转） vs 轮换一格（正转）")
    save_schem(d, P, "18_p3_5_phase.png")


def sequence_control():
    """图 18-p3-6：练习 4 顺序控制。KM2 线圈回路串 KM1 常开辅助触点。"""
    XN = 17.0
    with drawing(fontsize=10) as d:
        d += elm.Dot(open=True).at((0, 1.4)).label("L", "top")
        d += elm.Line().down().toy(-6.6)
        d += elm.Dot(open=True).at((XN, 1.4)).label("N", "top")
        d += elm.Line().down().toy(-6.6)
        d += elm.Dot().at((0, 0))
        rung_c(d, 0, [(PushNC, "SB1 停止 M1"), ("par", (PushNO, "SB2 启动 M1"), (ContactNO, "KM1 自锁")),
                      (Coil, "KM1 线圈")], 0, XN)
        d += elm.Dot()
        d += elm.Dot().at((0, -4.2))
        rung_c(d, -4.2, [(PushNC, "SB3 停止 M2"), ("par", (PushNO, "SB4 启动 M2"), (ContactNO, "KM2 自锁")),
                         (ContactNO, "KM1 常开（顺序）", ACC), (Coil, "KM2 线圈")], 0, XN)
        d += elm.Dot()
    print("[图 18-p3-6] 练习 4：KM2 回路串 KM1 常开 → K2' = S3' (S4 + K2) K1")
    save_schem(d, P, "18_p3_6_sequence.png")


lowvolt_interlock()
button_only_vs_double()
self_lock_nc()
phase_swap_vs_rotate()
sequence_control()
