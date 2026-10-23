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
