"""05 反相放大：全部配图（图 05-p2-2 由 code/05_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/05_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "05"
R1, Rf = 10e3, 100e3


def inverting(d, r1="$R_1$ 10 kΩ", rf="$R_f$ 100 kΩ", vin="$V_i$ 输入", vminus=None, cur=False):
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    r = elm.Resistor().left().label(r1)
    if cur:
        r.label("$I \\rightarrow$", "bottom")      # 电流方向
    d += r
    d += elm.Dot(open=True).label(vin, "left")
    up = elm.Line().up().at(j.center).length(2.3 if vminus else 1.5)
    if vminus:
        up.label(vminus, "bottom", fontsize=11)      # 标在竖线右侧
    d += up
    rr = elm.Resistor().right().label(rf).tox(op.out.x + 0.5)
    if cur:
        rr.label("$I \\rightarrow$", "bottom")
    d += rr
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(0.5)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$ 输出", "right")
    return op


# ---------- 图 05-p1-1 反相放大电路 ----------
with drawing() as d:
    inverting(d)
save_schem(d, N, "05_p1_1_circuit.png")

# ---------- 图 05-p1-2 电压「跷跷板」：沿 R1、Rf 的电压分布 ----------
Vi = 0.5
Vo = -Rf / R1 * Vi
x = np.array([0, R1, R1 + Rf]) / 1e3                 # 沿电阻链累计的电阻（kΩ）：输入端 0，反相端 10，输出端 110
v = np.array([Vi, 0.0, Vo])
print(f"输入端 {Vi} V，反相端（虚地）0 V，输出端 {Vo} V；斜率每 kΩ {(Vo - Vi) / 110:.3f} V")
assert abs((Vi - 0) / R1 - (0 - Vo) / Rf) < 1e-12      # 两段电阻上的电流相等（虚断）
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(x, v, **fs.LS["third"], label="沿 $R_1$ → $R_f$ 的电压")
ax.axvspan(0, 10, color=fs.C["fill"], alpha=0.8, lw=0)
ax.axvspan(10, 110, color=fs.C["fill2"], alpha=0.8, lw=0)
ax.text(5, -4.2, "$R_1$\n10 kΩ", ha="center", fontsize=9)
ax.text(60, -4.2, "$R_f$　100 kΩ", ha="center", fontsize=9)
ax.plot([0], [Vi], "o", color=fs.C["vin"], ms=6, zorder=6)
ax.plot([110], [Vo], "o", color=fs.C["vout"], ms=6, zorder=6)
ax.plot([10], [0], "^", color="k", ms=9, zorder=6)
fs.mark(ax, 0, Vi, fmt="{:.1f}", unit=" V", dx=6, dy=4)
fs.mark(ax, 110, Vo, fmt="{:.1f}", unit=" V", dx=-34, dy=-12)
ax.annotate("虚地 0 V（支点）", (10, 0), (25, 1.2), fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))
fs.ref_h(ax, 0, "0 V")
fs.axlabels(ax, "从输入端算起经过的电阻", "kΩ", "电压", "V")
ax.set_xlim(-3, 113); ax.set_ylim(-6, 2); ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "05_p1_2_seesaw.png")

# ---------- 图 05-p1-3 输入与输出：倒过来、放大 ----------
t = np.linspace(0, 2e-3, 1001)
vi = fs.sine(t, 1e3, amp=0.5)
vo = -2 * vi                                          # 取 Rf/R1 = 2，便于和输入放在同一坐标里看
print(f"放大 2 倍反相：输入峰值 0.5 V → 输出峰值 {vo.max():.1f} V，输入最高时（0.25 ms）输出 {vo[125]:.1f} V")
assert abs(vo[125] + 1.0) < 1e-9
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi, **fs.LS["vin"], label="$V_i$ 输入")
ax.plot(t * 1e3, vo, **fs.LS["vout"], label="$V_o$ 输出（$R_f/R_1$ = 2）")
fs.ref_h(ax, 0, "0 V")
fs.mark(ax, 0.25, vi[125], fmt="{:.1f}", unit=" V", dx=6, dy=2)
fs.mark(ax, 0.25, vo[125], fmt="{:.1f}", unit=" V", dx=6, dy=-10)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "05_p1_3_invert_wave.png")

# ---------- 图 05-p2-1 虚短虚断分析图 ----------
with drawing() as d:
    inverting(d, vminus="虚地 $V_-$ ≈ 0 V", cur=True)
save_schem(d, N, "05_p2_1_analysis.png")

# ---------- 图 05-p2-3 反相加法器 ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot().label("虚地", "bottom", ofst=0.15))
    d += elm.Line().left().length(0.5)
    d += (k := elm.Dot())
    d += elm.Resistor().left().label("$R_1$ 10 kΩ")
    d += elm.Dot(open=True).label("$V_1$", "left")
    d += elm.Line().up().at(k.center).length(1.4)
    d += elm.Resistor().left().label("$R_2$ 10 kΩ")
    d += elm.Dot(open=True).label("$V_2$", "left")
    d += elm.Line().up().at(j.center).length(2.6)
    d += elm.Resistor().right().label("$R_f$ 10 kΩ").tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(0.5)
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$", "right")
save_schem(d, N, "05_p2_3_summer.png")

# ---------- 图 05-p2-4 加法器波形：两个信号混在一起 ----------
t = np.linspace(0, 2e-3, 2001)
v1 = fs.sine(t, 1e3, amp=0.5)
v2 = fs.sine(t, 5e3, amp=0.2)
vo = -(v1 + v2)                                       # R1 = R2 = Rf，所以 V_o = −(V_1 + V_2)
print(f"加法器：V1 峰值 0.5 V（1 kHz），V2 峰值 0.2 V（5 kHz），输出最低 {vo.min():.2f} V、最高 {vo.max():.2f} V")
assert abs(vo.max() - 0.7) < 0.01
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, v1, **fs.LS["vin"], label="$V_1$（1 kHz）")
ax.plot(t * 1e3, v2, **fs.LS["third"], label="$V_2$（5 kHz）")
ax.plot(t * 1e3, vo, **fs.LS["vout"], label="$V_o = -(V_1 + V_2)$")
k = np.argmax(vo)
fs.mark(ax, t[k] * 1e3, vo[k], fmt="{:.2f}", unit=" V", dx=6, dy=2)
fs.ref_h(ax, 0, "0 V")
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8)
fs.save(fig, N, "05_p2_4_summer_wave.png")

# ---------- 图 05-p3-1 信号源内阻的影响：R1 不能太小 ----------
R1s = np.logspace(2, 6, 200)                          # R1 从 100 Ω 扫到 1 MΩ，始终保持 Rf = 10·R1
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.axhline(10, **fs.LS["good"], label="理想 $|A_v|$ = 10")
for Rs, key in ((1e3, "vout"), (100, "third")):
    g = 10 * R1s / (R1s + Rs)                         # 源内阻和 R1 串联：|A_v| = Rf / (Rs + R1)
    ax.semilogx(R1s, g, **fs.LS[key], label=f"信号源内阻 {Rs:g} Ω")
    for r in (1e3, 10e3):
        gv = 10 * r / (r + Rs)
        fs.mark(ax, r, gv, fmt="{:.2f}", dx=4, dy=-12 if key == "vout" else 4)
g1k = 10 * 10e3 / (10e3 + 1e3)
print(f"内阻 1 kΩ、R1 = 10 kΩ 时 |A_v| = {g1k:.2f}；R1 = 1 kΩ 时只有 {10*1e3/2e3:.2f}")
assert abs(g1k - 9.09) < 0.01
fs.axlabels(ax, "输入电阻 $R_1$（$R_f$ 始终取 10 $R_1$）", "Ω", "放大倍数 $|A_v|$", None)
ax.set_ylim(0, 11); ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "05_p3_1_source_loading.png")

# ---------- 图 05-p3-2 放大倍数随频率下降（增益带宽积 GBW） ----------
GBW = 1.2e6                                           # LM358B 典型增益带宽积 1.2 MHz
f = np.logspace(2, 7, 400)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
for G, key in ((1, "vout"), (10, "third"), (100, "fb")):
    fc = GBW / (1 + G)                                # 闭环带宽 ≈ GBW / (1 + |A_v|)
    mag = G / np.sqrt(1 + (f / fc) ** 2)              # 只用幅值公式：频率到 fc 时倍数降到 0.707 倍
    ax.loglog(f, mag, **fs.LS[key], label=f"$|A_v|$ = {G}：$f_c$ ≈ {fc/1e3:.0f} kHz")
    fs.mark(ax, fc, G / np.sqrt(2), fmt="{:.2g}", dx=5, dy=4)
    print(f"|A_v| = {G}: 带宽 f_c ≈ {fc/1e3:.1f} kHz，此处倍数 {G/np.sqrt(2):.2f}")
assert abs(GBW / 11 - 109.1e3) < 100
fs.axlabels(ax, "频率", "Hz", "放大倍数 $|A_v|$", None); ax.legend(loc="lower left", fontsize=8)
fs.save(fig, N, "05_p3_2_bandwidth.png")

# ---------- page3 正文与练习里的其余数字（只打印 + 断言，不画图） ----------
k = 1 / np.sqrt(2)
print(f"0.707 的来历：1/√2 = {k:.4f}；倍数降到 1/√2 时输出功率 ∝ 电压² 降到 {k**2:.2f} 倍（一半）")
assert abs(k - 0.7071) < 1e-4 and abs(k**2 - 0.5) < 1e-12
print(f"放大 1000 倍拆两级：每级 √1000 = {np.sqrt(1000):.1f} 倍，32 × 32 = {32*32}")
assert abs(np.sqrt(1000) - 31.6) < 0.1
SR, Vp = 0.5e6, 10.0                                  # 压摆率 0.5 V/μs = 0.5e6 V/s；输出峰值 10 V
f_sr = SR / (2 * np.pi * Vp)                          # 正弦最大斜率 2πf·Vp ≤ SR
print(f"压摆率限制：峰值 {Vp:g} V 的正弦，频率不超过 {f_sr:.0f} Hz（约 8 kHz）")
assert 7900 < f_sr < 8000
Rs = 500
g_ideal, g_1M, g_1M_rs = 20, 1e6 / 51e3, 1e6 / (51e3 + Rs)
print(f"练习 2(1)：1 MΩ/51 kΩ = {g_1M:.2f}（取整误差 {100*(1-g_1M/20):.1f}%），计入 500 Ω 内阻后 {g_1M_rs:.2f}（总误差 {100*(1-g_1M_rs/20):.1f}%）")
assert abs(g_1M_rs - 19.42) < 0.01 and 2.8 < 100 * (1 - g_1M_rs / 20) < 3.0
print(f"练习 2(2)：最大输入峰值 10.5/20 = {10.5/20:.3f} V；(3) 带宽 1.2 MHz/21 = {GBW/21/1e3:.1f} kHz")
assert abs(10.5 / 20 - 0.525) < 1e-12 and abs(GBW / 21 - 57.1e3) < 100
Vi_pk, Vo_sat = 2.0, -14.9                            # 练习 3：输入峰值 2 V，−10 倍，输出卡在 −14.9 V
Vm = (Vi_pk * 100e3 + Vo_sat * 10e3) / 110e3          # 反相端电压 = 两端电压按 R1、Rf 分压
print(f"练习 3：输入 +{Vi_pk:g} V、输出卡在 {Vo_sat} V 时，反相端电压 {Vm:.3f} V；R1 电流 {(Vi_pk-Vm)/10:.3f} mA，Rf 电流 {(Vm-Vo_sat)/100:.3f} mA")
assert abs(Vm - 0.464) < 0.001

# 练习 3 补充：LM358B 输出经 R_f 吸电流时负侧下限约 −14.39 V（review/spice/05.md 的 SPICE 值），反相端随之变化
Vo_sat_load = -14.39
Vm2 = (Vi_pk * 100e3 + Vo_sat_load * 10e3) / 110e3
print(f"练习 3（带载下限）：输出卡在 {Vo_sat_load} V 时，反相端电压 {Vm2:.2f} V；电流 {(Vi_pk-Vm2)/10:.3f} mA")
assert abs(Vm2 - 0.51) < 0.005

# ---------- page2 第一节：1.2 kHz 时 A ≈ 1000，但输出幅度几乎不变（第 7 轮按 SPICE 更正） ----------
# 高频时运放自身的 A 落后 90°，可写成 A = −j·1000；代入 V_o = −(R_f/R_1)·V_i / (1 + 11/A)
A_12k = GBW / 1.2e3                                   # 1.2 MHz ÷ 1.2 kHz = 1000
den = 1 + 11 / (-1j * A_12k)                          # 修正分母 = 1 + j·0.011（两项成直角）
Vo_12k = -10 * 0.5 / den                              # 输入峰值 0.5 V
err_12k = 100 * (1 - abs(Vo_12k) / 5)
lag_12k = np.degrees(np.angle(den))                   # 多落后的角度
print(f"page2：1.2 kHz 时 A = {A_12k:.0f}，|分母| = √(1 + 0.011²) = {abs(den):.5f}，|V_o| = {abs(Vo_12k):.3f} V，幅度误差 {err_12k:.3f}%，多落后 {lag_12k:.1f}°；反相端 ≈ 5 V ÷ A = {5/A_12k*1e3:.0f} mV")
assert abs(A_12k - 1000) < 1e-9 and abs(abs(den) - 1.00006) < 1e-5 and err_12k < 0.01 and abs(lag_12k - 0.6) < 0.05
fc10 = GBW / 11
g50k = 10 / np.sqrt(1 + (50e3 / fc10) ** 2)           # 10 倍电路在 50 kHz 时的倍数
print(f"page2：10 倍电路带宽 {fc10/1e3:.0f} kHz，50 kHz 时倍数 {g50k:.2f}，下降 {100*(1-g50k/10):.0f}%")
assert abs(g50k - 9.09) < 0.01


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
P4_SWEEP = [round(-1.5 + 0.25 * k, 2) for k in range(13)]


def p4_inv(v, rf=100e3, rs=0.0, mode="dual"):
    """反相放大接 9 V 电池，输入相对 M（mode="gnd" 时 M 就是 0 V）。
    mode：dual = 两节 9 V（M = A− 与 B+ 的连接点）；single = 一节 9 V、M 由 1k/1k 分压；gnd = 一节 9 V、不造中点（错误接法）。
    rs：电位器滑动端和 R1 之间串的电阻（模拟信号源内阻）。输入从 0 V 用 1 ms 升到 v，读稳定值。"""
    if mode == "dual":
        body = ["VP vp 0 9", "VN vn 0 -9", "RZ m 0 1m"]
    elif mode == "single":
        body = ["VP vp 0 9", "VN vn 0 0", "RM1 vp m 1k", "RM2 m 0 1k"]
    else:
        body = ["VP vp 0 9", "VN vn 0 0", "RZ m 0 1m"]
    body += [f"VI w m PWL(0 0 1m {v})", f"RS w in {max(rs, 1e-3):g}", "R1 in s 10k", f"R2 s o {rf:g}",
             "XU m s vp vn o LMX58B_LM2904B"]
    ex = ["v(o)-v(m)", "v(s)-v(m)", "v(in)-v(s)", "v(s)-v(o)", "v(in)-v(m)", "v(m)"]
    r = bb_ng_settle("\n".join(body), ex, ["LMx58B_LM2904B.lib"])
    return dict(out=r[ex[0]], vm_=r[ex[1]], vr1=r[ex[2]], vrf=r[ex[3]], vin=r[ex[4]], m=r[ex[5]])


def _rng(g_nom_num, g_nom_den, vin):
    """5% 电阻时输出范围：倍数 = 分子/分母，分子取 ±5%，分母（可能是两只电阻之和）取 ∓5%。"""
    lo = g_nom_num * 0.95 / (g_nom_den * 1.05) * vin
    hi = g_nom_num * 1.05 / (g_nom_den * 0.95) * vin
    return -hi, -lo


def p4_numbers():
    r = {}
    r["a"] = p4_inv(0.5)
    a = r["a"]
    print(f"[05 page4] ±9 V，输入 +0.50 V：输出 {a['out']:+.3f} V，反相端 {a['vm_'] * 1e3:+.2f} mV，"
          f"R1 两端 {a['vr1']:.3f} V，Rf 两端 {a['vrf']:.3f} V，电流 {a['vr1'] / 10e3 * 1e3:.4f} mA")
    assert abs(a["out"] + 5.0) < 0.01 and abs(a["vm_"]) < 3e-3 and abs(a["vr1"] - 0.5) < 0.002 and abs(a["vrf"] - 5.0) < 0.01
    for rf in (47e3, 10e3):
        x = p4_inv(0.5, rf=rf)
        lo, hi = _rng(rf, 10e3, 0.5)
        r[rf] = x
        print(f"[05 page4] Rf = {rf / 1e3:.0f} kΩ，输入 +0.50 V：输出 {x['out']:+.3f} V（5% 电阻范围 {lo:+.2f}～{hi:+.2f} V）")
    assert abs(r[47e3]["out"] + 2.35) < 0.01 and abs(r[10e3]["out"] + 0.5) < 0.005
    assert [round(v, 2) for v in _rng(47e3, 10e3, 0.5)] == [-2.6, -2.13] and [round(v, 2) for v in _rng(10e3, 10e3, 0.5)] == [-0.55, -0.45]
    x = p4_inv(-0.2)
    print(f"[05 page4] 输入 −0.20 V：输出 {x['out']:+.3f} V")
    assert abs(x["out"] - 2.0) < 0.01
    x = p4_inv(0.5, rs=10e3)
    lo, hi = _rng(100e3, 20e3, 0.5)
    r["rs"] = x
    print(f"[05 page4] 串 Rs = 10 kΩ，滑动端 +0.50 V：R1 左端 {x['vin']:.3f} V，输出 {x['out']:+.3f} V（5% 范围 {lo:+.2f}～{hi:+.2f} V）")
    assert abs(x["vin"] - 0.25) < 0.002 and abs(x["out"] + 2.5) < 0.01
    assert [round(v, 2) for v in (lo, hi)] == [-2.76, -2.26]
    for v in (-1.5, 1.5):
        x = p4_inv(v)
        r[v] = x
        print(f"[05 page4] ±9 V，输入 {v:+.1f} V：输出 {x['out']:+.2f} V（削平），反相端 {x['vm_']:+.3f} V")
    assert abs(r[-1.5]["out"] - 7.81) < 0.03 and abs(r[1.5]["out"] + 8.42) < 0.03 and r[1.5]["vm_"] > 0.1
    for v in (0.25, -0.25):
        x = p4_inv(v, mode="single")
        r[("s", v)] = x
        print(f"[05 page4] 单 9 V（分压中点），输入 {v:+.2f} V：输出对 M {x['out']:+.3f} V，M 对 0 V {x['m']:.3f} V")
    assert abs(r[("s", 0.25)]["out"] + 2.5) < 0.01 and abs(r[("s", -0.25)]["out"] - 2.5) < 0.01
    for v in (0.25, -0.25):
        x = p4_inv(v, mode="gnd")
        r[("g", v)] = x
        print(f"[05 page4] 单 9 V 不造中点（错误接法），输入 {v:+.2f} V：输出对 0 V {x['out']:+.3f} V，反相端 {x['vm_']:+.3f} V")
    assert 0 < r[("g", 0.25)]["out"] < 0.05 and abs(r[("g", -0.25)]["out"] - 2.5) < 0.01
    fam = {rf: np.array([p4_inv(v, rf=rf)["out"] for v in P4_SWEEP]) for rf in (10e3, 47e3, 100e3)}
    return r, fam


# ---------------- 图 05-p4-1：面包板接线图（双 9 V 与单 9 V 共用一张，单电源才插的元件在左上角灰框里） ----------------
def p4_1_breadboard():
    rails = {"T1": ("V+ = +9 V", BB_WIRE["pos"]), "T2": ("M（地，中点）", BB_WIRE["gnd"]),
             "B1": ("V−（−9 V 或 0 V）", BB_WIRE["neg"]), "B2": ("M（地，中点）", BB_WIRE["gnd"])}
    fig, ax = bb_board(30, rails, figsize=(10.6, 6.6))
    bb_wire(ax, "T2-1", "B2-1", "gnd", via=[(-0.4, 10.8), (-0.4, -3.6)])
    # 单电源才插（右上角灰框）：1 kΩ / 1 kΩ 分压 + 47 μF，造出中点 M
    ax.add_patch(_BbRect((20.4, 5.45), 8.2, 4.35, fc="0.86", ec="0.45", ls="--", lw=0.9, zorder=0.5))
    bb_wire(ax, "T1-21", "a21", "pos")
    bb_res(ax, "b21", "b24", "Rm1 1k")
    bb_wire(ax, "a24", "T2-24", "gnd")
    bb_res(ax, "c24", "c27", "Rm2 1k")
    bb_part2(ax, "d24", "d27", "C 47μF", kind="cap", dy=-0.55)
    bb_wire(ax, "e27", "B1-29", "neg", via=[(27.0, 4.0), (29.0, 4.0)])
    _bb_label(ax, 23.6, 4.0, "灰框：只在单 9 V 时插")
    # LM358：1～4 脚 f14～f17，8～5 脚 e14～e17
    bb_dip8(ax, 14)
    bb_wire(ax, "a14", "T1-14", "pos")                      # 8 脚 V+
    bb_wire(ax, "c15", "c16", "fb")                         # 另一半：7 脚接 6 脚
    bb_wire(ax, "a17", "T2-17", "gnd")                      # 另一半：5 脚接 M
    bb_wire(ax, "j17", "B1-17", "neg")                      # 4 脚 V−
    bb_wire(ax, "j16", "B2-16", "gnd")                      # 3 脚接 M
    # 反相 ×10
    bb_block(ax, ["g3", "g4", "g5"], "", pins=["端", "滑", "端"], fc="#d7ccc8")
    _bb_label(ax, 4, 3.05, "电位器 10k")
    bb_wire(ax, "j5", "B2-5", "gnd")
    bb_wire(ax, "i4", "i9", "sig")
    _bb_label(ax, 6.5, -0.45, "第 10 步换成 Rs 10k")
    bb_res(ax, "h9", "h12", "R1 10k")
    bb_wire(ax, "j12", "j15", "fb", via=[(12.0, -1.45), (15.0, -1.45)])
    bb_res(ax, "i12", "i14", "Rf 100k（47k/10k）", dy=-0.55)
    # 1.5 V 电池盒画在板子外
    ax.add_patch(_BbRect((0.8, -5.0), 3.4, 0.75, fc="#ffe082", ec="0.3", lw=0.8, zorder=5))
    ax.text(2.5, -4.62, "1.5 V 电池盒", ha="center", va="center", fontsize=7.5, zorder=6)
    ax.plot([3.0, 3.0], [-4.25, -1.0], color=BB_WIRE["pos"], lw=2.0, zorder=3)          # 电池 + → j3（电位器一端）
    ax.plot(3, -1, "o", ms=4, color=BB_WIRE["pos"], zorder=4)
    ax.plot([2.0, 2.0], [-4.25, -3.6], color=BB_WIRE["gnd"], lw=2.0, zorder=3)          # 电池 − → M 轨
    ax.plot(2.0, -3.6, "o", ms=4, color=BB_WIRE["gnd"], zorder=4)
    ax.set_ylim(-5.5, 14.2)
    ax.text(0.2, 13.55, "两节 9 V：A 的 + 接 V+ 轨；A 的 − 与 B 的 + 拧在一起接 M 轨；B 的 − 接 V− 轨（灰框不插）",
            ha="left", va="center", fontsize=8)
    ax.text(0.2, 12.85, "一节 9 V：+ 接 V+ 轨，− 接 V− 轨（此时 V− 就是 0 V）；M 轨只接灰框里分压出来的中点，不接电池",
            ha="left", va="center", fontsize=8)
    bb_probe(ax, "g9", "①", dx=0.0, dy=0.95)
    bb_probe(ax, "g12", "②", dx=0.0, dy=0.95)
    bb_probe(ax, "h14", "③", dx=-0.75, dy=0.6)
    bb_legend(ax, [("pos", "红：V+"), ("neg", "紫：V−"), ("gnd", "黑：M"), ("sig", "蓝：输入"), ("fb", "绿：反馈/短接")],
              x=5.4, y=-5.0)
    print("[图 05-p4-1] 与 02 同一块板；第 7、8 步 Rf 换 47k/10k，第 10 步 i4–i9 换 Rs 10k；LM358 1～4 脚 f14～f17、8～5 脚 e14～e17；8 脚→V+，4 脚→V−，3 脚→M；"
          "另一半 7、6 脚短接、5 脚→M；电位器 g3/g4/g5，滑动端 i4→i9；R1 h9–h12；j12→j15 接 2 脚；Rf i12–i14；"
          "单电源：a21 接 V+，Rm1 b21–b24、a24 接 M，Rm2 c24–c27、47 μF d24(+)–d27，e27→V−；测点① 第 9 列、② 第 12 列、③ 第 14 列")
    fs.save(fig, N, "05_p4_1_breadboard.png")


# ---------------- 图 05-p4-2：没有示波器时，逐点测三种 Rf 的传输特性 ----------------
def p4_2_family(fam):
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    x = np.array(P4_SWEEP)
    sty = {10e3: dict(color=fs.C["vin"], marker="^", ls="-"), 47e3: dict(color=fs.C["third"], marker="s", ls="-."),
           100e3: dict(color=fs.C["vout"], marker="o", ls="-")}
    for rf, y in fam.items():
        ax.plot(x, y, ms=5, lw=1.4, label=f"Rf = {rf / 1e3:.0f} kΩ（理想 −{rf / 10e3:g} 倍）", **sty[rf])
        k = P4_SWEEP.index(0.5)
        print(f"[数值] Rf = {rf / 1e3:.0f} kΩ：输入 0.5 V → {y[k]:+.2f} V；两端 {y[0]:+.2f} / {y[-1]:+.2f} V")
    ax.plot(x, -10 * x, **fs.LS["good"], label="理想 −10 倍（不受电源限制）")
    k = P4_SWEEP.index(0.5)
    for rf, (tx, ty) in {100e3: (0.75, -2.6), 47e3: (0.95, -0.6), 10e3: (0.9, 1.4)}.items():
        ax.annotate(f"{fam[rf][k]:.2f} V", (0.5, fam[rf][k]), (tx, ty), fontsize=9,
                    arrowprops=dict(arrowstyle="-", color="0.4", lw=0.7))
    fs.ref_h(ax, 0, "M")
    ax.set_xlim(-1.65, 1.65); ax.set_ylim(-11, 11)
    fs.axlabels(ax, "输入（R1 左端对 M）", "V", "输出对 M", "V")
    ax.legend(loc="upper right", fontsize=8.5)
    assert abs(fam[47e3][k] + 2.35) < 0.01 and abs(fam[10e3][-1] + 1.5) < 0.01 and abs(fam[100e3][0] - 7.81) < 0.03
    fs.save(fig, N, "05_p4_2_gain_family.png")


if __name__ == "__main__":
    _r, _fam = p4_numbers()
    p4_1_breadboard(); p4_2_family(_fam)


# ====================== 第 8 轮补电路图（page1–3） ======================
EMPH = fs.C["third"]          # 新出现的元件用强调色


def _inv_core(d, x0, r1_txt, rf_txt):
    """以 (x0, 0) 为 R1 左端画反相放大主体，返回 (R1 左端坐标, op)。"""
    op = elm.Opamp(leads=True).at((x0 + 4.2, -0.6)).anchor("in1")
    d += op
    j = (op.in1[0] - 0.5, op.in1[1])
    d += elm.Line().endpoints(op.in1, j)
    d += elm.Dot().at(j)
    d += elm.Resistor().endpoints((x0, j[1]), j).label(r1_txt)
    top = j[1] + 1.6
    xo = op.out[0] + 0.5
    d += elm.Line().endpoints(j, (j[0], top))
    d += elm.Resistor().endpoints((j[0], top), (xo, top)).label(rf_txt)
    d += elm.Line().endpoints((xo, top), (xo, op.out[1]))
    d += elm.Dot().at((xo, op.out[1]))
    g = (op.in2[0] - 0.5, op.in2[1])
    d += elm.Line().endpoints(op.in2, g)
    d += elm.Line().endpoints(g, (g[0], g[1] - 0.5))
    d += elm.Ground().at((g[0], g[1] - 0.5))
    d += elm.Line().endpoints(op.out, (op.out[0] + 1.25, op.out[1]))
    d += elm.Dot(open=True).at((op.out[0] + 1.25, op.out[1])).label("$V_o$", "right")
    return (x0, j[1]), op


# ---------- 图 05-p3-3 信号源内阻与 R1 串联 ----------
with drawing() as d:
    a, op = _inv_core(d, 0.0, "$R_1$ 10 kΩ", "$R_f$ 100 kΩ")
    y = a[1]
    xs = -4.4                                            # 信号源内部：理想电压源 + 内阻
    d += elm.SourceSin().endpoints((xs, y - 2.2), (xs, y))
    d += elm.Label().at((xs - 0.75, y - 1.1)).label("$V_i$", halign="right")
    d += elm.Resistor().endpoints((xs, y), (xs + 2.6, y)).label("$R_s$ 1 kΩ").color(EMPH)
    d += elm.Line().endpoints((xs + 2.6, y), a)
    d += elm.Dot(open=True).at((xs + 2.9, y))                 # 信号源输出端子
    d += elm.Ground().at((xs, y - 2.2))
    import matplotlib.patches as _mp                     # 虚线框标出「信号源」这一整块
    box = dict(x0=xs - 1.1, y0=y - 2.75, x1=xs + 2.75, y1=y + 1.05)
    for p, q in [((box["x0"], box["y0"]), (box["x1"], box["y0"])), ((box["x1"], box["y0"]), (box["x1"], box["y1"])),
                 ((box["x1"], box["y1"]), (box["x0"], box["y1"])), ((box["x0"], box["y1"]), (box["x0"], box["y0"]))]:
        d += elm.Line().endpoints(p, q).linestyle("--").color(EMPH).linewidth(1)
    d += elm.Label().at((xs + 0.8, y - 3.15)).label("信号源（内部串着 $R_s$）", fontsize=10, color=EMPH)
    d += elm.Label().at((-0.2, y - 1.25)).label("电流 $V_i/(R_s+R_1)$ →", fontsize=10, halign="left")
save_schem(d, N, "05_p3_3_source_resistance.png")

# ---------- 图 05-p3-4 练习 4：两路加权混音 ----------
with drawing() as d:
    a, op = _inv_core(d, 0.0, "$R_1$ = ?", "$R_f$ 50 kΩ")
    y = a[1]
    d += elm.Dot(open=True).at(a).label("$V_1$ 话筒", "left")
    jx = op.in1[0] - 0.5
    yb = y - 1.9                                         # 第二路接到虚地点左边、和 R1 同一个节点
    d += elm.Line().endpoints((jx - 0.9, y), (jx - 0.9, yb)).color(EMPH)
    d += elm.Dot().at((jx - 0.9, y))
    d += elm.Resistor().endpoints((a[0], yb), (jx - 0.9, yb)).label("$R_2$ = ?", "bottom").color(EMPH)
    d += elm.Dot(open=True).at((a[0], yb)).label("$V_2$ 伴奏", "left").color(EMPH)
save_schem(d, N, "05_p3_4_mixer_exercise.png")
