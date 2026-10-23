"""04 差分放大：全部配图（图 04-p2-2 由 code/04_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/04_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "04"


def diffamp(d, labs=("$R_1$ 10 kΩ", "$R_2$ 100 kΩ", "$R_3$ 10 kΩ", "$R_4$ 100 kΩ"),
            v1="$V_1$", v2="$V_2$", vo="$V_o$ 输出", note_minus=None, note_plus=None, at=None, r4side="bottom"):
    """四电阻差分放大。返回 (op, 左端 V1 点, 左端 V2 点)。"""
    op = elm.Opamp(leads=True).right()
    if at is not None:
        op.at(at).anchor("in1")
    d += op
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j1 := elm.Dot())
    d += elm.Resistor().left().label(labs[0], "top")
    p1 = d.here
    if v1:
        d += elm.Dot(open=True).label(v1, "left")
    up = elm.Line().up().at(j1.center).length(1.5)
    d += up
    d += elm.Resistor().right().label(labs[1]).tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(0.5)
    d += (j2 := elm.Dot())
    d += elm.Resistor().left().label(labs[2], "bottom")
    p2 = d.here
    if v2:
        d += elm.Dot(open=True).label(v2, "left")
    d += elm.Resistor().down().at(j2.center).label(labs[3], r4side)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    if vo:
        d += elm.Dot(open=True).label(vo, "right")
    if note_minus:
        d += elm.Label().at((j1.center[0] + 0.15, j1.center[1] + 0.9)).label(note_minus, halign="left", fontsize=11)
    if note_plus:
        d += elm.Label().at((j2.center[0] + 0.5, j2.center[1] - 1.5)).label(note_plus, halign="left", fontsize=11)
    return op, p1, p2


# ---------- 图 04-p1-2 差分放大电路 ----------
with drawing() as d:
    diffamp(d, v1="$V_1$ 输入 1", v2="$V_2$ 输入 2")
save_schem(d, N, "04_p1_2_circuit.png")
print("差分倍数 R2/R1 = 100 kΩ / 10 kΩ = 10，R4/R3 = 10（两组比例相同）")

# ---------- 图 04-p1-1 两根线上同样的干扰，相减后只剩差值 ----------
t = np.linspace(0, 0.2, 4001)
vd = fs.sine(t, 10, amp=0.5)                          # 为了看得见，这里差分信号取 0.5 V
vcm = fs.sine(t, 50, amp=2.0)
V1, V2 = vcm - vd / 2, vcm + vd / 2
vo = 1.0 * (V2 - V1)                                  # 取倍数 1，只看「相减」
print(f"两根线都带 2 V、50 Hz 干扰；差值峰值 {vd.max():.1f} V；相减后输出峰值 {vo.max():.1f} V")
assert np.allclose(vo, vd)
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"], sharey=True)
a1.plot(t * 1e3, V1, **fs.LS["vin"], label="$V_1$")
a1.plot(t * 1e3, V2, **fs.LS["third"], label="$V_2$")
fs.axlabels(a1, "时间", "ms", "电压", "V"); a1.set_title("两根输入线（都带 50 Hz 干扰）", fontsize=10)
a1.legend(loc="lower right", fontsize=8, ncol=2)
a2.plot(t * 1e3, vo, **fs.LS["vout"], label="$V_2$ − $V_1$")
fs.mark(a2, 25, 0.5, fmt="{:.1f}", unit=" V", dx=6, dy=2)
fs.axlabels(a2, "时间", "ms", None, None); a2.set_title("相减之后（干扰抵消）", fontsize=10)
a2.legend(loc="lower right", fontsize=8)
for a in (a1, a2):
    a.set_ylim(-3, 3)
fs.save(fig, N, "04_p1_1_subtract.png")

# ---------- 图 04-p2-1 推导用的差分放大 ----------
with drawing() as d:
    diffamp(d, v1="$V_1$", v2="$V_2$",
            note_minus="$V_- = V_+$（虚短）",
            note_plus="$V_+ = V_2 \\cdot R_4/(R_3+R_4)$", r4side="top")
save_schem(d, N, "04_p2_1_analysis.png")

# ---------- 图 04-p2-3 三运放仪表放大器 ----------
with drawing() as d:
    d.config(fontsize=11)
    d += (a1 := elm.Opamp(leads=True).flip().label("A1", "center", fontsize=10))
    d += elm.Line().left().at(a1.in2).length(0.8)
    d += elm.Dot(open=True).label("$V_1$", "left")
    d += elm.Line().left().at(a1.in1).length(0.5)
    d += (n1 := elm.Dot())
    d += elm.Line().down().length(1.8)
    d += elm.Resistor().down().label("$R_g$ 1 kΩ", "top")
    d += elm.Line().down().length(1.8)
    d += (n2 := elm.Dot())
    d += elm.Line().right().length(0.5)
    d += (a2 := elm.Opamp(leads=True).anchor("in1").label("A2", "center", fontsize=10))
    d += elm.Line().left().at(a2.in2).length(0.8)
    d += elm.Dot(open=True).label("$V_2$", "left")
    xo = a1.out[0] + 0.6
    # A1 反馈：n1 → 向下 → 电阻 R → 上到 A1 输出
    d += elm.Line().at(n1.center).to((n1.center[0], n1.center[1] - 1.5))
    d += elm.Resistor().right().label("$R$ 10 kΩ", "bottom").tox(xo)
    d += elm.Line().up().toy(a1.out)
    d += elm.Dot()
    d += elm.Line().left().tox(a1.out)
    d += elm.Line().at(n2.center).to((n2.center[0], n2.center[1] + 1.5))
    d += elm.Resistor().right().label("$R$ 10 kΩ", "top").tox(xo)
    d += elm.Line().down().toy(a2.out)
    d += elm.Dot()
    d += elm.Line().left().tox(a2.out)
    # 后级：四个 10 kΩ 的差分放大（倍数 1）
    ymid = (a1.out[1] + a2.out[1]) / 2
    op, p1, p2 = diffamp(d, labs=("10 kΩ", "10 kΩ", "10 kΩ", "10 kΩ"), v1=None, v2=None,
                         vo="$V_o$", at=(xo + 4.6, ymid + 0.6))
    d += elm.Line().at((xo, a1.out[1])).to((p1[0] - 0.5, a1.out[1]))
    d += elm.Line().down().toy(p1[1])
    d += elm.Line().right().tox(p1[0])
    d += elm.Line().at((xo, a2.out[1])).to((p2[0] - 0.5, a2.out[1]))
    d += elm.Line().up().toy(p2[1])
    d += elm.Line().right().tox(p2[0])
save_schem(d, N, "04_p2_3_ina.png")
R, Rg = 10e3, 1e3
G = 1 + 2 * R / Rg
print(f"仪表放大器：倍数 = 1 + 2R/Rg = 1 + 2 × 10 kΩ / 1 kΩ = {G:.0f}（后级 4 个 10 kΩ，倍数 1）")
assert G == 21


def gains(R1, R2, R3, R4):
    """返回 (差分倍数, 共模倍数)。"""
    a = R4 / (R3 + R4) * (1 + R2 / R1)                  # V2 到输出的倍数
    b = R2 / R1                                         # V1 到输出的倍数（取负号）
    return (a + b) / 2, a - b


# ---------- 图 04-p3-1 电阻误差与共模抑制比 ----------
eps = np.logspace(-4, np.log10(0.05), 300)              # 电阻误差 0.01% ～ 5%
one = np.array([20 * np.log10(abs(g[0] / g[1])) for g in (gains(10e3, 100e3, 10e3, 100e3 * (1 + e)) for e in eps)])
worst = np.array([20 * np.log10(abs(g[0] / g[1])) for g in
                  (gains(10e3 * (1 + e), 100e3 * (1 - e), 10e3 * (1 - e), 100e3 * (1 + e)) for e in eps)])
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.semilogx(eps * 100, one, **fs.LS["third"], label="只有 $R_4$ 偏差")
ax.semilogx(eps * 100, worst, **fs.LS["bad"], label="四只电阻都按最坏方向偏差")
for e in (0.001, 0.01):
    g1 = gains(10e3, 100e3, 10e3, 100e3 * (1 + e)); c1 = 20 * np.log10(abs(g1[0] / g1[1]))
    g4 = gains(10e3 * (1 + e), 100e3 * (1 - e), 10e3 * (1 - e), 100e3 * (1 + e)); c4 = 20 * np.log10(abs(g4[0] / g4[1]))
    print(f"电阻误差 {e*100:g}%：只偏一只 CMRR {c1:.0f} dB，四只最坏 {c4:.0f} dB")
    fs.mark(ax, e * 100, c1, fmt="{:.0f}", unit=" dB", dx=6, dy=4)
    fs.mark(ax, e * 100, c4, fmt="{:.0f}", unit=" dB", dx=-40, dy=-14)
g = gains(10e3 * 1.01, 100e3 * 0.99, 10e3 * 0.99, 100e3 * 1.01)
assert 40 < 20 * np.log10(abs(g[0] / g[1])) < 50                 # 1% 电阻最坏只有 40 多 dB
fs.axlabels(ax, "电阻误差", "%", "共模抑制比 CMRR", "dB")
ax.set_ylim(20, 110); ax.legend(loc="upper right", fontsize=8)
ax.set_xticks([0.01, 0.1, 1]); ax.set_xticklabels(["0.01", "0.1", "1"])
fs.save(fig, N, "04_p3_1_cmrr_tolerance.png")

# ---------- 图 04-p3-2 信号源内阻（只在 V1 一侧）破坏平衡 ----------
Rs = np.logspace(0, 4, 300)                              # 1 Ω ～ 10 kΩ
cm = np.array([20 * np.log10(abs(g[0] / g[1])) for g in (gains(10e3 + r, 100e3, 10e3, 100e3) for r in Rs)])
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.semilogx(Rs, cm, **fs.LS["bad"], label="$V_1$ 一侧串入内阻 $R_s$")
for r in (100, 1000):
    gg = gains(10e3 + r, 100e3, 10e3, 100e3); c = 20 * np.log10(abs(gg[0] / gg[1]))
    print(f"内阻 {r} Ω：CMRR 降到 {c:.0f} dB，差分倍数 {gg[0]:.2f}")
    fs.mark(ax, r, c, fmt="{:.0f}", unit=" dB", dx=6, dy=4)
fs.ref_h(ax, 61, "61 dB（1% 电阻只偏一只）", x=0.02, ha="left")
assert 20 * np.log10(abs(gains(11e3, 100e3, 10e3, 100e3)[0] / gains(11e3, 100e3, 10e3, 100e3)[1])) < 45
fs.axlabels(ax, "信号源内阻 $R_s$", "Ω", "共模抑制比 CMRR", "dB")
ax.set_ylim(20, 110); ax.legend(loc="upper right", fontsize=8)
ax.set_xticks([1, 10, 100, 1e3, 1e4]); ax.set_xticklabels(["1", "10", "100", "1 k", "10 k"])
fs.save(fig, N, "04_p3_2_source_resistance.png")

# ---------- 正文里的其余数字（只打印 + 断言） ----------
for k in (10, 1):                                         # 倍数 10（本节）和倍数 1（TI 手册的例子）
    for e in (0.01, 0.001):
        g = gains(10e3 * (1 + e), k * 10e3 * (1 - e), 10e3 * (1 - e), k * 10e3 * (1 + e))
        c = 20 * np.log10(abs(g[0] / g[1])); c_est = 20 * np.log10((1 + k) / (4 * e))
        print(f"倍数 {k}、误差 {e*100:g}%：四只最坏 CMRR {c:.1f} dB，估算 (1+k)/(4ε) 给 {c_est:.1f} dB")
        assert abs(c - c_est) < 0.5
assert round(20 * np.log10(2 / 0.04)) == 34 and round(20 * np.log10(2 / 0.004)) == 54
g = gains(10.2e3, 100e3, 10e3, 100e3)                     # 练习 3：V1 一侧 200 Ω 内阻
print(f"200 Ω 内阻：V2 路 {g[0]+g[1]/2:.2f}、V1 路 {g[0]-g[1]/2:.2f}，差分倍数（平均）{g[0]:.2f}，共模倍数（差）{g[1]:.3f}")
assert abs(g[0] - 9.81) < 0.01 and abs(g[1] - 0.018) < 0.001


# ======================================================================================
# 动手实验篇（page4）用的面包板俯视图小工具。
# 各节点 figs 脚本里各带一份同样的代码（共享模块只由总纲修改）；以后可以挪进 code/figs/ 的共享模块。
# 坐标：列号 1～30 从左到右；a～e 行在上半块，f～j 行在下半块，中间是隔离槽；
# 上下各有两条电源轨，名字用 "T1"（最上）、"T2"、"B1"、"B2"（最下）加列号，例如 "T1-5"。
# 同一列的 a～e 五个孔是连通的，f～j 五个孔是连通的；同一条电源轨整条连通。
# ======================================================================================
import matplotlib.pyplot as _bb_plt
from matplotlib.patches import Rectangle as _BbRect, Polygon as _BbPoly, Wedge as _BbWedge

BB_ROWY = {r: y for r, y in zip("abcdefghij", [9, 8, 7, 6, 5, 3, 2, 1, 0, -1])}
BB_RAILY = {"T1": 11.6, "T2": 10.8, "B1": -2.8, "B2": -3.6}
BB_WIRE = dict(pos="#CC0000", gnd="#000000", neg=fs.C["third"], sig=fs.C["vin"], out=fs.C["vout"], fb=fs.C["fb"])


def bb_xy(h):
    """孔名 → 坐标：'a5' → (5, 9)；'T1-5' → (5, 11.6)。"""
    if h[:2] in BB_RAILY:
        return float(h.split("-")[1]), BB_RAILY[h[:2]]
    return float(h[1:]), float(BB_ROWY[h[0]])


def bb_board(cols=30, rails=None, figsize=(10, 5.6)):
    """画空白面包板。rails = {"T1": ("+9 V", 颜色), ...}，只画给出的电源轨。返回 (fig, ax)。"""
    rails = rails or {}
    fig, ax = _bb_plt.subplots(figsize=figsize)
    ax.set_xlim(-1.6, cols + 4.2); ax.set_ylim(-5.5, 12.7)
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(_BbRect((0.2, -4.2), cols + 0.6, 16.4, fc="#f4f1ea", ec="0.6", lw=0.8, zorder=0))
    ax.add_patch(_BbRect((0.2, 3.65), cols + 0.6, 0.7, fc="#e4e0d6", ec="none", zorder=0))   # 中间隔离槽
    for c in range(1, cols + 1):
        for r, y in BB_ROWY.items():
            ax.plot(c, y, "s", ms=2.6, color="0.55", zorder=1)
        if c == 1 or c % 5 == 0:
            ax.text(c, 9.65, str(c), ha="center", va="bottom", fontsize=7, color="0.3")
            ax.text(c, -1.75, str(c), ha="center", va="top", fontsize=7, color="0.3")
    for r, y in BB_ROWY.items():
        ax.text(0.45, y, r, ha="center", va="center", fontsize=7, color="0.3")
        ax.text(cols + 0.55, y, r, ha="center", va="center", fontsize=7, color="0.3")
    for name, y in BB_RAILY.items():
        if name not in rails:
            continue
        text, col = rails[name]
        ax.plot([0.7, cols + 0.3], [y + 0.32, y + 0.32], color=col, lw=0.9, zorder=1)
        for c in range(1, cols + 1):
            ax.plot(c, y, "s", ms=2.6, color="0.55", zorder=1)
        ax.text(cols + 1.0, y, text, ha="left", va="center", fontsize=8, color=col)
    return fig, ax


def bb_wire(ax, a, b, kind="sig", via=()):
    """跳线：kind 取 pos/gnd/neg/sig/out（红/黑/紫/蓝/橙）。via=[(x, y), ...] 时按这些拐点折线走，避免压住元件。"""
    pts = [bb_xy(a)] + list(via) + [bb_xy(b)]
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=BB_WIRE[kind], lw=2.4, solid_capstyle="round", zorder=3)
    ax.plot([xs[0], xs[-1]], [ys[0], ys[-1]], "o", ms=4, color=BB_WIRE[kind], zorder=4)


def _bb_label(ax, x, y, text, fs_=7.5):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs_, zorder=6,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))


def bb_res(ax, a, b, text, dy=0.55):
    """电阻：两条引脚 + 中间米色小方块，标签写在方块旁边。"""
    (x0, y0), (x1, y1) = bb_xy(a), bb_xy(b)
    ax.plot([x0, x1], [y0, y1], color="0.25", lw=1.2, zorder=4)
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    horiz = abs(x1 - x0) >= abs(y1 - y0)
    w, h = (0.9, 0.36) if horiz else (0.36, 0.9)
    ax.add_patch(_BbRect((xm - w / 2, ym - h / 2), w, h, fc="#e8cf9c", ec="0.25", lw=0.8, zorder=5))
    if horiz:
        _bb_label(ax, xm, ym + dy, text)
    else:
        _bb_label(ax, xm + (0.85 if dy > 0 else -0.85), ym, text)
    for x, y in ((x0, y0), (x1, y1)):
        ax.plot(x, y, "o", ms=3, color="0.25", zorder=5)


def bb_part2(ax, a, b, text, kind="diode", dy=0.55, fc="white"):
    """两脚元件：kind = diode（a 脚是阳极，b 脚是阴极，画竖杠）、led（同上，填色）、cap（电解电容，a 脚是正极）、box。"""
    (x0, y0), (x1, y1) = bb_xy(a), bb_xy(b)
    ax.plot([x0, x1], [y0, y1], color="0.25", lw=1.2, zorder=4)
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    L = max(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5, 1e-9)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L          # 从 a 指向 b 的单位向量
    nx, ny = -uy, ux
    s = 0.32
    if kind in ("diode", "led"):
        tri = [(xm - ux * s + nx * s, ym - uy * s + ny * s), (xm - ux * s - nx * s, ym - uy * s - ny * s),
               (xm + ux * s, ym + uy * s)]
        ax.add_patch(_BbPoly(tri, closed=True, fc=(fc if kind == "led" else "0.25"), ec="0.2", lw=0.8, zorder=5))
        ax.plot([xm + ux * s + nx * s, xm + ux * s - nx * s], [ym + uy * s + ny * s, ym + uy * s - ny * s],
                color="0.1", lw=1.6, zorder=5)
    elif kind == "cap":
        ax.add_patch(_BbRect((xm - 0.32, ym - 0.32), 0.64, 0.64, fc="#3b5b92", ec="0.2", lw=0.8, zorder=5))
        _bb_label(ax, x0 + ux * 0.35 + nx * 0.35, y0 + uy * 0.35 + ny * 0.35, "+", fs_=8)
    else:
        ax.add_patch(_BbRect((xm - 0.4, ym - 0.3), 0.8, 0.6, fc=fc, ec="0.2", lw=0.8, zorder=5))
    if abs(x1 - x0) >= abs(y1 - y0):
        _bb_label(ax, xm, ym + dy, text)
    else:
        _bb_label(ax, xm + (0.85 if dy > 0 else -0.85), ym, text)
    for x, y in ((x0, y0), (x1, y1)):
        ax.plot(x, y, "o", ms=3, color="0.25", zorder=5)


def bb_block(ax, holes, text, pins=None, fc="white", pad=0.38, fs_=7.5, tdy=0.0):
    """多脚元件（三极管、继电器、电位器、按钮、电池盒等）：画一个盖住这些孔的方块，pins 给每只脚的小字。
    tdy ≠ 0 时把元件名挪到方块上方（tdy > 0）或下方（tdy < 0），免得压住引脚。"""
    pts = [bb_xy(h) for h in holes]
    xs, ys = zip(*pts)
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    ax.add_patch(_BbRect((x0, y0), x1 - x0, y1 - y0, fc=fc, ec="0.2", lw=0.9, alpha=0.92, zorder=5))
    if tdy:
        _bb_label(ax, (x0 + x1) / 2, (y1 + tdy) if tdy > 0 else (y0 + tdy), text, fs_=fs_)
    else:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center", fontsize=fs_, zorder=6)
    for i, (x, y) in enumerate(pts):
        ax.plot(x, y, "o", ms=3, color="0.2", zorder=6)
        if pins:
            ax.text(x, y - 0.42, pins[i], ha="center", va="top", fontsize=6, color="0.15", zorder=6)


def bb_dip8(ax, col, text="LM358"):
    """8 脚芯片跨在隔离槽上：1～4 脚在 f 行第 col～col+3 列，8～5 脚在 e 行第 col～col+3 列，缺口朝左。"""
    ax.add_patch(_BbRect((col - 0.45, 3.25), 3.9, 2.15, fc="0.18", ec="0.1", zorder=5))
    ax.add_patch(_BbWedge((col - 0.45, 4.3), 0.3, -90, 90, fc="#f4f1ea", ec="none", zorder=6))
    ax.text(col + 1.5, 4.3, text, ha="center", va="center", fontsize=8, color="white", zorder=6)
    for k in range(4):
        ax.text(col + k, 3.55, str(k + 1), ha="center", va="center", fontsize=6.5, color="white", zorder=6)
        ax.text(col + k, 5.05, str(8 - k), ha="center", va="center", fontsize=6.5, color="white", zorder=6)


def bb_probe(ax, h, text, dx=0.0, dy=0.9):
    """测量点：朱红色以外的黑框圆圈 + 编号，指向某个孔。"""
    x, y = bb_xy(h)
    ax.annotate(text, (x, y), (x + dx, y + dy), ha="center", va="center", fontsize=7.5, zorder=7,
                bbox=dict(boxstyle="circle,pad=0.15", fc=fs.C["hi"], ec="0.2", lw=0.7),
                arrowprops=dict(arrowstyle="-", color="0.2", lw=0.7))


def bb_legend(ax, items, x=1.0, y=-5.0):
    """底部图例：items = [(kind, 文字), ...]。"""
    for i, (kind, text) in enumerate(items):
        xx = x + i * 6.2
        ax.plot([xx, xx + 1.0], [y, y], color=BB_WIRE[kind], lw=2.4)
        ax.text(xx + 1.25, y, text, ha="left", va="center", fontsize=7.5)


def bb_ng_op(body, exprs, includes=()):
    """用 ngspice 跑一次直流工作点（.op），返回 {表达式: 数值}。body 是网表正文，exprs 如 ["v(out)", "i(v1)"]；
    includes 是 spice/models/ 下的模型文件名。网表写在临时目录，跑完即删，仓库里不留文件。"""
    import os as _os, re as _re, shutil as _sh, subprocess as _sp, tempfile as _tf
    models = _os.path.abspath(_os.path.join(_os.path.dirname(fs.__file__), "..", "..", "spice", "models"))
    inc = "\n".join(f".include {_os.path.join(models, m)}" for m in includes)
    prints = "\n".join(f"print {e}" for e in exprs)
    cir = f"* page4 工作点\n{inc}\n{body}\n.control\nop\n{prints}\n.endc\n.end\n"
    tmp = _tf.mkdtemp(prefix="p4op_")
    try:
        with open(_os.path.join(tmp, ".spiceinit"), "w") as f:
            f.write("set ngbehavior=psa\nset num_threads=1\n")      # 读入 PSpice 格式的厂家模型
        with open(_os.path.join(tmp, "op.cir"), "w", encoding="utf-8") as f:
            f.write(cir)
        r = _sp.run([_sh.which("ngspice") or "/usr/bin/ngspice", "-b", "op.cir"], cwd=tmp,
                    capture_output=True, text=True, timeout=300)
    finally:
        _sh.rmtree(tmp, ignore_errors=True)
    vals = {k.lower(): float(v) for k, v in _re.findall(r"^\s*(\S+)\s*=\s*([-+0-9.eE]+)\s*$", r.stdout, _re.M)}
    out = {e: vals.get(e.lower()) for e in exprs}
    assert r.returncode == 0 and None not in out.values(), f"ngspice 失败：{r.stdout[-800:]}{r.stderr[-800:]}"
    return out


def bb_ng_settle(body, exprs, includes=(), tstop=2e-3):
    """含运放、输出可能顶到电源的电路，.op 常常不收敛；改用瞬态：信号源写成 PWL 从 0 慢慢升到目标值（1 ms），
    电源保持恒定，读 tstop 前 0.1 ms 的稳定值。返回 {表达式: 数值}。网表写在临时目录，跑完即删。"""
    import os as _os, re as _re, shutil as _sh, subprocess as _sp, tempfile as _tf
    models = _os.path.abspath(_os.path.join(_os.path.dirname(fs.__file__), "..", "..", "spice", "models"))
    inc = "\n".join(f".include {_os.path.join(models, m)}" for m in includes)
    ctl = "\n".join(f"let e{k} = {e}\nmeas tran e{k}r find e{k} at={tstop - 1e-4:g}" for k, e in enumerate(exprs))
    cir = f"* page4 稳态值\n{inc}\n{body}\n.control\ntran 1u {tstop:g} 0 1u\n{ctl}\n.endc\n.end\n"
    tmp = _tf.mkdtemp(prefix="p4tr_")
    try:
        with open(_os.path.join(tmp, ".spiceinit"), "w") as f:
            f.write("set ngbehavior=psa\nset num_threads=1\n")
        with open(_os.path.join(tmp, "tr.cir"), "w", encoding="utf-8") as f:
            f.write(cir)
        r = _sp.run([_sh.which("ngspice") or "/usr/bin/ngspice", "-b", "tr.cir"], cwd=tmp,
                    capture_output=True, text=True, timeout=300)
    finally:
        _sh.rmtree(tmp, ignore_errors=True)
    vals = dict(_re.findall(r"^\s*(e\d+r)\s*=\s*([-+0-9.eE]+)", r.stdout, _re.M))
    out = {e: (float(vals[f"e{k}r"]) if f"e{k}r" in vals else None) for k, e in enumerate(exprs)}
    assert None not in out.values(), f"ngspice 失败：{r.stdout[-800:]}{r.stderr[-800:]}"
    return out


# ---------------- 动手实验篇（page4）：LM358 + 9 V 电池，ngspice + TI LM358B 模型现算读数 ----------------
P4_CM = [-9.0, -6.0, -3.0, 0.0, 1.5, 3.0, 6.0, 7.0, 7.5, 8.0, 8.5, 9.0]


def p4_diff(v1, v2, r4x=0.0, mode="dual", src=None):
    """四电阻差分放大（R1 = R3 = 10k，R2 = R4 = 100k）接 9 V 电池，读数都相对 M。
    v1、v2：两路输入对 M 的电压（理想源，1 ms 从 0 升到目标值）；src = "vp"/"vn" 表示两路输入一起接 V+ 轨或 V− 轨。
    r4x：R4 下端和 M 之间串的电阻（0 表示导线）。
    mode：dual = 两节 9 V，M = A− 与 B+ 的连接点；single = 一节 9 V，M 由 1k/1k 分压（不接电池）。"""
    if mode == "dual":
        body = ["VP vp 0 9", "VN vn 0 -9", "RZ m 0 1m"]
    else:
        body = ["VP vp 0 9", "RVN vn 0 1m", "RM1 vp m 1k", "RM2 m 0 1k"]
    if src is None:
        body += [f"VA a m PWL(0 0 1m {v1})", f"VB b m PWL(0 0 1m {v2})"]
        na, nb = "a", "b"
    else:   # 两路输入一起接到电源轨：用一只从 M 附近慢慢挪到轨上的 PWL 源，最后正好等于轨电压
        d = 9.0 if mode == "dual" else 4.5
        body += [f"VA a {src} PWL(0 {-d if src == 'vp' else d} 1m 0)"]
        na = nb = "a"
    body += [f"R1 {na} s 10k", "R2 s o 100k", f"R3 {nb} p 10k", "R4 p x 100k", f"RX x m {max(r4x, 1e-3):g}",
             "XU p s vp vn o LMX58B_LM2904B"]
    ex = ["v(o)-v(m)", "v(p)-v(m)", "v(s)-v(p)", f"v({na})-v(m)", f"v({nb})-v(m)", "v(m)", "v(p)", "v(o)"]
    r = bb_ng_settle("\n".join(body), ex, ["LMx58B_LM2904B.lib"])
    return dict(out=r[ex[0]], vp_=r[ex[1]], dvin=r[ex[2]], v1=r[ex[3]], v2=r[ex[4]], m=r[ex[5]], p_abs=r[ex[6]], o_abs=r[ex[7]])


def _ideal_diff(v1, v2, r1, r2, r3, r4):
    return v2 * r4 / (r3 + r4) * (1 + r2 / r1) - v1 * r2 / r1


def _rng_diff(v1, v2, tol=0.05):
    vals = []
    for k1 in (1 - tol, 1 + tol):
        for k2 in (1 - tol, 1 + tol):
            for k3 in (1 - tol, 1 + tol):
                for k4 in (1 - tol, 1 + tol):
                    vals.append(_ideal_diff(v1, v2, 10e3 * k1, 100e3 * k2, 10e3 * k3, 100e3 * k4))
    return min(vals), max(vals)


def _rng_mis(vcm, tol=0.05, extra=10e3):
    """第 13、14 步：R4 下面串 10k 以后，输出比串之前多出多少（两次都接同一个共模电压），5% 电阻的范围。"""
    vals = []
    for k1 in (1 - tol, 1 + tol):
        for k2 in (1 - tol, 1 + tol):
            for k3 in (1 - tol, 1 + tol):
                for k4 in (1 - tol, 1 + tol):
                    for k5 in (1 - tol, 1 + tol):
                        a = (10e3 * k1, 100e3 * k2, 10e3 * k3)
                        vals.append(_ideal_diff(vcm, vcm, *a, 100e3 * k4 + extra * k5) - _ideal_diff(vcm, vcm, *a, 100e3 * k4))
    return min(vals), max(vals)


P4_CM_S = [-4.5, -3.0, -1.5, 0.0, 1.5, 3.0, 3.5, 4.0, 4.5]


def p4_numbers():
    r = {}
    q = lambda key, *a, **k: r.setdefault(key, p4_diff(*a, **k))
    for key, args in {"d56": (0.5, 0.6), "d54": (0.5, 0.4), "d1011": (1.0, 1.1), "c0": (0.0, 0.0), "c15": (1.5, 1.5)}.items():
        x = q(key, *args)
        lo, hi = _rng_diff(*args)
        print(f"[04 page4] 两节 9 V，① {args[0]:.2f} V、② {args[1]:.2f} V：③ {x['out']:+.4f} V（5% 电阻、理想运放范围 {lo:+.3f}～{hi:+.3f} V），④ {x['vp_']:.3f} V")
    assert abs(r["d56"]["out"] - 1.0) < 0.01 and abs(r["d54"]["out"] + 1.0) < 0.01 and abs(r["d1011"]["out"] - 1.0) < 0.01
    assert abs(r["c0"]["out"]) < 0.01 and abs(r["c15"]["out"]) < 0.01
    for s in ("vn", "vp"):
        x = q(("rail", s), 0, 0, src=s)
        print(f"[04 page4] 两节 9 V，两路一起接 {'V− 轨' if s == 'vn' else 'V+ 轨'}：④ {x['vp_']:+.3f} V，③ {x['out']:+.3f} V，2、3 脚之差 {x['dvin']:+.3f} V")
    lo, hi = _rng_diff(-9, -9)
    print(f"[04 page4] 共模 −9 V 时 5% 电阻的漏出范围 {lo:+.2f}～{hi:+.2f} V")
    assert abs(r[("rail", "vn")]["out"]) < 0.01 and r[("rail", "vp")]["out"] < -3 and abs(r[("rail", "vp")]["vp_"] - 8.18) < 0.01
    m15 = q("m15", 1.5, 1.5, r4x=10e3); m9 = q("m9", 0, 0, r4x=10e3, src="vn"); m0 = q("m0", 0, 0, r4x=10e3)
    lo, hi = _rng_mis(1.5)
    print(f"[04 page4] R4 串 10k：共模 1.5 V ③ {m15['out']:+.4f} V（比匹配时多 {m15['out'] - r['c15']['out']:+.4f}，5% 范围 {lo:+.3f}～{hi:+.3f}），"
          f"接 V− 轨 ③ {m9['out']:+.3f} V，接 M ③ {m0['out']:+.4f} V；理想 1.5×(110/120×11−10) = {1.5 * (110 / 120 * 11 - 10):.3f}")
    assert abs(m15["out"] - r["c15"]["out"] - 0.125) < 0.005 and abs(m9["out"] + 0.75) < 0.01 and abs(m0["out"]) < 0.01
    # 单 9 V：M 由 1k/1k 分压
    for key, args in {"s56": (0.5, 0.6), "s54": (0.5, 0.4)}.items():
        x = q(key, *args, mode="single")
        print(f"[04 page4] 一节 9 V（M 由分压造），① {args[0]:.2f}、② {args[1]:.2f}：③ {x['out']:+.4f} V，M 对 V− 轨 {x['m']:.3f} V")
    for s in ("vn", "vp"):
        x = q(("srail", s), 0, 0, src=s, mode="single")
        print(f"[04 page4] 一节 9 V，两路一起接 {'V− 轨（0 V）' if s == 'vn' else 'V+ 轨'}：输入对 M {x['v1']:+.3f} V，④ 对 M {x['vp_']:+.3f}（对 V− 轨 {x['p_abs']:.3f}），"
              f"③ 对 M {x['out']:+.3f} V（对 V− 轨 {x['o_abs']:.3f}），M {x['m']:.3f} V")
    assert abs(r["s56"]["out"] - 1.0) < 0.01 and abs(r["s54"]["out"] + 1.0) < 0.01
    assert abs(r[("srail", "vn")]["out"]) < 0.01 and r[("srail", "vp")]["out"] < -3
    cm_d = [p4_diff(v, v)["out"] for v in P4_CM]
    cm_dm = [p4_diff(v, v, r4x=10e3)["out"] for v in P4_CM]
    cm_s = [p4_diff(v, v, mode="single")["out"] for v in P4_CM_S]
    for v, a, b in zip(P4_CM, cm_d, cm_dm):
        print(f"[04 page4] 两节 9 V 共模 {v:+.1f} V：匹配 ③ {a:+.4f} V，R4 串 10k ③ {b:+.4f} V")
    for v, a in zip(P4_CM_S, cm_s):
        print(f"[04 page4] 一节 9 V 共模（对 M）{v:+.1f} V：③ {a:+.4f} V")
    return r, dict(d=cm_d, dm=cm_dm, s=cm_s)


# ---------------- 图 04-p4-1：面包板俯视图 ----------------
def p4_1_breadboard():
    rails = {"T1": ("V+ = +9 V", BB_WIRE["pos"]), "T2": ("M（地，中点）", BB_WIRE["gnd"]),
             "B1": ("V−（−9 V 或 0 V）", BB_WIRE["neg"]), "B2": ("M（地，中点）", BB_WIRE["gnd"])}
    fig, ax = bb_board(30, rails, figsize=(10.6, 6.9))
    bb_wire(ax, "T2-1", "B2-1", "gnd", via=[(-0.4, 10.8), (-0.4, -3.6)])
    # 单电源才插（右上角灰框）：1 kΩ / 1 kΩ 分压 + 47 μF，造出中点 M
    ax.add_patch(_BbRect((20.4, 5.45), 8.2, 4.35, fc="0.86", ec="0.45", ls="--", lw=0.9, zorder=0.5))
    bb_wire(ax, "T1-21", "a21", "pos")
    bb_res(ax, "b21", "b24", "Rm1 1k")
    bb_wire(ax, "a24", "T2-24", "gnd")
    bb_res(ax, "c24", "c27", "Rm2 1k")
    bb_part2(ax, "d24", "d27", "C 47μF", kind="cap", dy=-0.55)
    bb_wire(ax, "e27", "B1-29", "neg", via=[(27.0, 4.0), (29.0, 4.0)])
    _bb_label(ax, 24.6, 4.0, "灰框：只在单 9 V 时插")
    # LM358
    bb_dip8(ax, 14)
    bb_wire(ax, "a14", "T1-14", "pos")                      # 8 脚 V+
    bb_wire(ax, "c15", "c16", "fb")                         # 另一半：7 脚接 6 脚
    bb_wire(ax, "a17", "T2-17", "gnd")                      # 另一半：5 脚接 M
    bb_wire(ax, "j17", "B1-17", "neg")                      # 4 脚 V−
    # V1 一路：电位器 A（下半块），R1、R2
    bb_block(ax, ["g3", "g4", "g5"], "", pins=["端", "滑", "端"], fc="#d7ccc8")
    _bb_label(ax, 4, 3.05, "电位器 A")
    bb_wire(ax, "j5", "B2-5", "gnd")
    bb_wire(ax, "i4", "i9", "sig")
    bb_res(ax, "h9", "h12", "R1 10k")
    bb_wire(ax, "j12", "j15", "fb", via=[(12.0, -1.45), (15.0, -1.45)])
    bb_res(ax, "i12", "i14", "R2 100k", dy=-0.55)
    # V2 一路：电位器 B（上半块），R3、R4
    bb_block(ax, ["c3", "c4", "c5"], "", pins=["端", "滑", "端"], fc="#d7ccc8")
    _bb_label(ax, 4, 8.05, "电位器 B")
    bb_wire(ax, "e3", "f3", "out")                          # 1.5 V 送到电位器 B 的一端
    bb_wire(ax, "a5", "T2-5", "gnd")
    bb_wire(ax, "d4", "d20", "sig", via=[(4.0, 6.5), (20.0, 6.5)])
    bb_wire(ax, "e20", "f20", "sig")
    bb_res(ax, "g16", "g20", "R3 10k")
    bb_res(ax, "i16", "i19", "R4 100k", dy=-0.55)
    bb_wire(ax, "j19", "B2-19", "gnd")
    _bb_label(ax, 23.2, -2.15, "j19→M 第 13、14 步换成 10k")
    # 1.5 V 电池盒画在板子外
    ax.add_patch(_BbRect((0.8, -5.0), 3.4, 0.75, fc="#ffe082", ec="0.3", lw=0.8, zorder=5))
    ax.text(2.5, -4.62, "1.5 V 电池盒", ha="center", va="center", fontsize=7.5, zorder=6)
    ax.plot([3.0, 3.0], [-4.25, -1.0], color=BB_WIRE["pos"], lw=2.0, zorder=3)          # 电池 + → j3
    ax.plot(3, -1, "o", ms=4, color=BB_WIRE["pos"], zorder=4)
    ax.plot([2.0, 2.0], [-4.25, -3.6], color=BB_WIRE["gnd"], lw=2.0, zorder=3)          # 电池 − → M 轨
    ax.plot(2.0, -3.6, "o", ms=4, color=BB_WIRE["gnd"], zorder=4)
    ax.set_ylim(-5.9, 14.2)
    ax.text(0.2, 13.55, "两节 9 V：A 的 + 接 V+ 轨；A 的 − 与 B 的 + 拧在一起接 M 轨；B 的 − 接 V− 轨（灰框不插）",
            ha="left", va="center", fontsize=8)
    ax.text(0.2, 12.85, "一节 9 V：+ 接 V+ 轨，− 接 V− 轨（此时 V− 就是 0 V）；M 轨只接灰框里分压出来的中点，不接电池",
            ha="left", va="center", fontsize=8)
    bb_probe(ax, "g9", "①", dx=0.0, dy=0.95)
    bb_probe(ax, "i20", "②", dx=0.75, dy=0.6)
    bb_probe(ax, "h14", "③", dx=-0.75, dy=0.6)
    bb_probe(ax, "h16", "④", dx=0.0, dy=0.95)
    bb_legend(ax, [("pos", "红：V+"), ("neg", "紫：V−"), ("gnd", "黑：M")], x=5.4, y=-4.7)
    bb_legend(ax, [("sig", "蓝：输入"), ("fb", "绿：反馈"), ("out", "橙：1.5 V")], x=5.4, y=-5.4)
    print("[图 04-p4-1] LM358 1～4 脚 f14～f17、8～5 脚 e14～e17；8 脚→V+，4 脚→V−；另一半 7、6 脚短接、5 脚→M；"
          "电位器 A g3/g4/g5（j3 接电池 +，j5→M），滑动端 i4→i9；R1 h9–h12；j12→j15 接 2 脚；R2 i12–i14；"
          "电位器 B c3/c4/c5（e3→f3 取 1.5 V，a5→M），滑动端 d4→d20、e20→f20；R3 g16–g20；R4 i16–i19；j19→M（第 13、14 步换 10k）；"
          "单电源灰框同 01；测点① 第 9 列、② 第 20 列、③ 第 14 列、④ 第 16 列（3 脚）")
    fs.save(fig, N, "04_p4_1_breadboard.png")


# ---------------- 图 04-p4-2：没有示波器时，逐点测“两路一起抬高”的输出 ----------------
def p4_2_common(cm):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.4))
    a1.plot(P4_CM, cm["d"], color=fs.C["vout"], marker="o", ms=5, lw=1.5, label="四只电阻配对（R4 = 100k）")
    a1.plot(P4_CM, cm["dm"], color=fs.C["third"], marker="s", ms=5, lw=1.3, ls="-.", label="R4 下面串 10k（110k）")
    a1.axhline(0, **fs.LS["good"], label="理想：0 V")
    a1.axvspan(8.25, 9.3, color="0.88", zorder=0)
    a1.text(8.75, 1.3, "禁区\n约 8.25 V\n以上", ha="center", va="center", fontsize=8)
    k = P4_CM.index(1.5)
    a1.annotate(f"{cm['dm'][k]:+.2f} V", (1.5, cm["dm"][k]), (2.5, 1.6), fontsize=9,
                arrowprops=dict(arrowstyle="-", color="0.4", lw=0.7))
    a1.annotate(f"{cm['dm'][0]:+.2f} V", (-9, cm["dm"][0]), (-8.0, -2.4), fontsize=9,
                arrowprops=dict(arrowstyle="-", color="0.4", lw=0.7))
    a1.set_xlim(-9.5, 9.3); a1.set_ylim(-8.2, 2.4)
    fs.axlabels(a1, "两路一起接的电压（对 M）", "V", "输出 ③（对 M）", "V")
    a1.legend(loc="lower left", fontsize=8)
    a1.set_title("两节 9 V", fontsize=10)
    a2.plot(P4_CM_S, cm["s"], color=fs.C["vout"], marker="o", ms=5, lw=1.5, label="四只电阻配对")
    a2.axhline(0, **fs.LS["good"], label="理想：0 V")
    a2.axvspan(3.3, 4.7, color="0.88", zorder=0)
    a2.text(4.0, 0.55, "禁区\n约 3.3 V 以上", ha="center", va="center", fontsize=8.5)
    a2.set_xlim(-4.8, 4.7); a2.set_ylim(-4.8, 1.2)
    fs.axlabels(a2, "两路一起接的电压（对 M）", "V", "输出 ③（对 M）", "V")
    a2.legend(loc="lower left", fontsize=8)
    a2.set_title("一节 9 V（M 由分压造）", fontsize=10)
    i8, i85 = P4_CM.index(8.0), P4_CM.index(8.5)
    print(f"[数值] 两节 9 V：共模 8.0 V ③ {cm['d'][i8]:+.3f} V、8.5 V ③ {cm['d'][i85]:+.2f} V；单 9 V：3.0 V ③ {cm['s'][P4_CM_S.index(3.0)]:+.3f}、"
          f"3.5 V ③ {cm['s'][P4_CM_S.index(3.5)]:+.2f} V")
    assert abs(cm["d"][i8]) < 0.02 and cm["d"][i85] < -1 and abs(cm["s"][P4_CM_S.index(3.0)]) < 0.02
    fs.save(fig, N, "04_p4_2_common_mode.png")


if __name__ == "__main__":
    _r, _cm = p4_numbers()
    p4_1_breadboard(); p4_2_common(_cm)


# ====================== 第 8 轮补电路图（page1–3） ======================
EMPH = fs.C["third"]          # 新出现的元件用强调色

# ---------- 图 04-p3-3 V1 一侧的信号源内阻 R_s 与 R1 串联 ----------
with drawing() as d:
    op, p1, p2 = diffamp(d, v1=None, v2="$V_2$")
    d += elm.Resistor().left().at(p1).label("$R_s$ 信号源内阻", "top").color(EMPH)
    d += elm.Dot(open=True).label("$V_1$", "left")
save_schem(d, N, "04_p3_3_rs_circuit.png")

# ---------- 图 04-p3-4 练习 4：0.1 Ω 采样电阻测电机电流 ----------
with drawing() as d:
    op, p1, p2 = diffamp(d, labs=("$R_1$", "$R_2$", "$R_3$", "$R_4$"), v1=None, v2=None, vo="$V_o$ 去单片机")
    xa = p1[0] - 0.8
    xs = xa - 1.8
    yT, yB = p1[1] + 1.0, p2[1] - 1.5
    d += elm.Line().endpoints(p1, (xa, p1[1]))
    d += elm.Line().endpoints((xa, p1[1]), (xa, yT))
    d += elm.Line().endpoints((xa, yT), (xs, yT))
    d += elm.Line().endpoints(p2, (xa, p2[1]))
    d += elm.Line().endpoints((xa, p2[1]), (xa, yB))
    d += elm.Line().endpoints((xa, yB), (xs, yB))
    d += elm.Dot().at((xs, yT)); d += elm.Dot().at((xs, yB))
    d += elm.Resistor().endpoints((xs, yB), (xs, yT)).color(EMPH)
    d += elm.Label().at((xs + 0.55, (yT + yB) / 2)).label("采样电阻\n0.1 Ω", halign="left", fontsize=11, color=EMPH)
    yg = yB - 3.0
    xb = xs - 1.6                                       # 12 V 电源：+ 端接采样电阻下端
    d += elm.Line().endpoints((xs, yB), (xb, yB))
    d += elm.SourceV().endpoints((xb, yg), (xb, yB))
    d += elm.Label().at((xb - 0.6, (yg + yB) / 2)).label("12 V", halign="right", fontsize=11)
    d += elm.Ground().at((xb, yg))
    xm = xs - 3.6                                       # 电机：接采样电阻上端
    d += elm.Line().endpoints((xs, yT), (xm, yT))
    d += elm.Motor().endpoints((xm, yT), (xm, yg))
    d += elm.Label().at((xm - 0.7, (yT + yg) / 2)).label("电机", halign="right", fontsize=11)
    d += elm.Ground().at((xm, yg))
save_schem(d, N, "04_p3_4_shunt_exercise.png")
print("练习 4：2 A × 0.1 Ω = 0.2 V，两端对地约 12 V")
