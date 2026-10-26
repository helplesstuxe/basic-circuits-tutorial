"""02 运放入门：全部配图（电路图用 schemdraw，曲线用 matplotlib）。
运行：/workspace/circuits-venv/bin/python code/figs/02_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。（图 02-p2-2 由 code/02_sim.py 生成）
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403  drawing、save_schem、elm，以及 figstyle 的全部工具
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "02"

# ---------- 运放的「实际」参数（典型值，取自 TI LM358B 数据手册 SLOS068AB 的数量级）----------
A_OL = 1e5          # 开环增益：10 万倍（LM358B 典型 140 V/mV，这里取整数好算）
VCC, VEE = 15.0, -15.0
DROP = 1.5          # 输出离电源轨还差约 1.5 V（LM358B 正轨典型 1.35~1.5 V）
VOH, VOL = VCC - DROP, VEE + DROP


def opamp_out(vd, vcc=VCC, vee=VEE, drop=DROP, a=A_OL):
    """开环运放：V_o = A·(V+ − V-)，但被限制在 [V_EE + drop, V_CC − drop] 之间。"""
    return np.clip(a * vd, vee + drop, vcc - drop)


# ---------- 图 02-p1-1 运放符号与五个引脚 ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.8)
    d += elm.Dot(open=True).label("反相输入端 $V_-$", "left")
    d += elm.Line().left().at(op.in2).length(0.8)
    d += elm.Dot(open=True).label("同相输入端 $V_+$", "left")
    d += elm.Line().right().at(op.out).length(0.8)
    d += elm.Dot(open=True).label("输出 $V_o$", "right")
    d += elm.Line().up().at(op.vd).length(0.8)
    d += elm.Vdd().label("$V_{CC}$ 正电源（如 +15 V）", "right")
    d += elm.Line().down().at(op.vs).length(0.8)
    d += elm.Vss().label("$V_{EE}$ 负电源（如 −15 V）", "right")
save_schem(d, N, "02_p1_1_symbol.png")

# ---------- 图 02-p1-2 开环传输特性：差一点点就顶到头 ----------
vd = np.linspace(-400e-6, 400e-6, 801)          # 两输入端电压差 V+ − V-：±400 μV
vo = opamp_out(vd)
lin = VOH / A_OL                                 # 线性区半宽：13.5 V / 10 万 = 135 μV
print(f"开环增益 A = {A_OL:.0f}，输出上限 {VOH} V、下限 {VOL} V，线性区 ±{lin*1e6:.0f} μV")
assert abs(lin - 135e-6) < 1e-9
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(vd * 1e6, vo, **fs.LS["vout"], label="$V_o$ 输出（A = 10 万）")
fs.ref_h(ax, VOH, f"上限 {VOH} V", x=0.02, ha="left"); fs.ref_h(ax, VOL, f"下限 {VOL} V", x=0.98)
fs.ref_v(ax, lin * 1e6, f"+{lin*1e6:.0f} μV", y=0.5); fs.ref_v(ax, -lin * 1e6, f"−{lin*1e6:.0f} μV", y=0.5)
fs.mark(ax, 50, opamp_out(50e-6), fmt="{:.1f}", unit=" V", dx=6, dy=-4)    # 差 50 μV 时输出 5 V
fs.axlabels(ax, "两输入端电压差 $V_+ - V_-$", "μV", "输出电压", "V")
ax.set_ylim(-16, 16); ax.legend(loc="center left")
assert abs(opamp_out(50e-6) - 5.0) < 1e-9
fs.save(fig, N, "02_p1_2_openloop.png")

# ---------- 图 02-p1-3 负反馈环路方框图 ----------
fig, ax = fs.diagram(9, 3.0)
b_in = fs.box(ax, 0.8, 2.0, "输入 $V_i$", w=1.3)
cmp_ = fs.box(ax, 3.0, 2.0, "比较\n$V_+ - V_-$", w=1.5, h=0.8)
amp = fs.box(ax, 5.3, 2.0, "放大 ×A\n（A ≈ 10 万）", w=1.7, h=0.8, fc=fs.C["fill2"])
b_out = fs.box(ax, 7.9, 2.0, "输出 $V_o$", w=1.3)
fb = fs.box(ax, 5.3, 0.6, "反馈网络（电阻分压）\n送回一部分 $V_o$", w=2.8, h=0.75)
fs.arrow(ax, b_in["r"], cmp_["l"], "接 $V_+$")
fs.arrow(ax, cmp_["r"], amp["l"])
fs.arrow(ax, amp["r"], b_out["l"])
fs.arrow(ax, (7.9, 1.7), (7.9, 0.6), color=fs.C["fb"])
fs.arrow(ax, (7.9, 0.6), fb["r"], color=fs.C["fb"])
fs.arrow(ax, fb["l"], (3.0, 0.6), color=fs.C["fb"])
fs.arrow(ax, (3.0, 0.6), cmp_["b"], color=fs.C["fb"])
ax.text(2.55, 1.05, "接 $V_-$\n（负反馈）", fontsize=9, color=fs.C["fb"], ha="right")
fs.save(fig, N, "02_p1_3_feedback_loop.png")

# ---------- 图 02-p2-1 用来推导的电路：反相放大（A 有限） ----------
with drawing() as d:
    d += (op := elm.Opamp(leads=True).label("A", "center", fontsize=12))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot().label("$V_-$", "bottom", ofst=0.15))
    d += elm.Resistor().left().label("$R_1$ 10 kΩ").label("$I_1 \\rightarrow$", "bottom")
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Line().up().at(j.center).length(1.5)
    d += elm.Resistor().right().label("$R_f$ 100 kΩ").label("$I_f \\rightarrow$", "bottom").tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().left().at(op.in2).length(0.5)
    d += elm.Line().down().length(0.5)
    d += elm.Ground().label("$V_+$ = 0 V", "right")
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$", "right")
save_schem(d, N, "02_p2_1_inverting_finiteA.png")

# ---------- 图 02-p2-3 有负反馈 vs 没有负反馈 ----------
t = np.linspace(0, 2e-3, 2001)
vi = fs.sine(t, 1e3, amp=0.5)
v_closed = -(100e3 / 10e3) * vi                       # 负反馈：-10 倍，干干净净
v_open = opamp_out(vi - 0.0)                           # 不加反馈：输入接 V+，V- 接地
print(f"闭环输出峰值 {v_closed.max():.2f} V；开环输出在 {v_open.min()} V 与 {v_open.max()} V 之间来回跳")
assert abs(v_closed.max() - 5.0) < 1e-3 and v_open.max() == VOH and v_open.min() == VOL
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi, **fs.LS["vin"], label="$V_i$ 输入（峰值 0.5 V）")
ax.plot(t * 1e3, v_closed, **fs.LS["vout"], label="$V_o$ 有负反馈（−10 倍）")
ax.plot(t * 1e3, v_open, **{**fs.LS["bad"], "markevery": 0.05}, label="$V_o$ 没有反馈（开环）")
fs.ref_h(ax, 0, "0 V")
fs.mark(ax, 0.75, v_closed[750], fmt="{:.1f}", unit=" V", dx=6, dy=-2)
fs.mark(ax, 0.25, v_open[250], fmt="{:.1f}", unit=" V", dx=6, dy=-12)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-16, 16)
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1))
fs.save(fig, N, "02_p2_3_open_vs_closed.png")

# ---------- 图 02-p3-1 电源电压决定输出能摆多远 ----------
vi = fs.sine(t, 1e3, amp=0.8)
ideal = -10 * vi                                       # 理想：峰值 8 V
cases = [("±15 V 双电源", 15, -15, "vout"), ("±5 V 双电源", 5, -5, "third"), ("5 V 单电源", 5, 0, "bad")]
UP, DN = 1.5, 0.1                                      # LM358B：输出最高离正电源约 1.5 V，最低离负电源约 0.1 V
# 三种电源拆成上下三个子图，避免单电源曲线把 ±5 V 的削顶段盖住
fig, axs = plt.subplots(3, 1, figsize=(7, 6.2), sharex=True)
for ax, (lab, vcc, vee, key) in zip(axs, cases):
    lo, hi = vee + DN, vcc - UP
    v = np.clip(ideal, lo, hi)
    style = {**fs.LS[key], "markevery": 0.05} if key == "bad" else fs.LS[key]
    ax.plot(t * 1e3, ideal, **fs.LS["good"], zorder=5, label="理想 $V_o$ = −10 $V_i$")
    ax.plot(t * 1e3, v, **style, label=f"{lab}：{lo:g} ~ {hi:g} V")
    print(f"{lab}: 输出范围 {lo:g} V ~ {hi:g} V，实际峰值 {v.max():.2f} V / 谷值 {v.min():.2f} V")
    fs.ref_h(ax, 0, "0 V")
    fs.axlabels(ax, "时间" if ax is axs[-1] else None, "ms" if ax is axs[-1] else None, "电压", "V")
    ax.set_ylim(-9.5, 9.5); ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8)
assert np.clip(ideal, -14.9, 13.5).max() == ideal.max() and np.clip(ideal, -14.9, 13.5).min() == ideal.min()  # ±15 V 时 ±8 V 不削顶
fs.save(fig, N, "02_p3_1_supply_clip.png")

# ---------- 图 02-p3-2 开环增益不够时的增益误差 ----------
A = np.logspace(3, 7, 200)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
for G, key in ((1, "vout"), (10, "third"), (100, "fb")):
    err = 100 * (1 - 1 / (1 + (1 + G) / A))            # 反相放大：实际倍数比理想倍数小了百分之几
    ax.loglog(A, err, **fs.LS[key], label=f"目标倍数 {G}")
    e = 100 * (1 - 1 / (1 + (1 + G) / 1.4e5))
    fs.mark(ax, 1.4e5, e, fmt="{:.2g}", unit=" %", dx=6, dy=2)   # 统一保留两位有效数字：0.0014 / 0.0079 / 0.072
    print(f"目标倍数 {G}：A = 14 万时误差 {e:.2g} %")
fs.ref_v(ax, 1.4e5, "LM358B 典型 A = 14 万", y=0.98)
e100 = 100 * (1 - 1 / (1 + 101 / 1.4e5))
assert 0.07 < e100 < 0.075                              # 目标 100 倍时误差约 0.072 %
assert f"{100 * (1 - 1 / (1 + 2 / 1.4e5)):.2g}" == "0.0014"   # 目标 1 倍：2/140000 ≈ 0.0014 %
assert f"{100 * (1 - 1 / (1 + 11 / 1.4e5)):.2g}" == "0.0079"  # 目标 10 倍：11/140000 ≈ 0.0079 %
fs.axlabels(ax, "开环增益 A", None, "增益误差", "%"); ax.legend(loc="lower left")
fs.save(fig, N, "02_p3_2_gain_error.png")


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
P4_SWEEP = [round(-1.5 + 0.25 * k, 2) for k in range(13)]     # 逐点测量用的输入（相对中点 M）


def p4_inv(vins, single, rf="100k"):
    """反相 ×10（10 kΩ / 100 kΩ）接 9 V 电池：single=False 为两节 9 V（±9 V，M = 两节电池的连接点）；
    single=True 为一节 9 V，M 由 1 kΩ/1 kΩ 分压得到。rf=None 表示拔掉 Rf（开环）。
    每个输入值单独跑一次瞬态，输入从 0 V 用 1 ms 升到目标值后读稳定值（开环、削顶时 .op 不收敛）。
    返回 [(输出对 M, 反相端对 M), ...] 和单电源时 M 对 0 V 的电压（双电源时为 0）。"""
    pts, vm = [], 0.0
    for v in vins:
        if single:
            body = ["VP vp 0 9", "RM1 vp m 1k", "RM2 m 0 1k", f"VI in m PWL(0 0 1m {v})", "XU m s vp 0 o LMX58B_LM2904B"]
        else:
            body = ["VP vp 0 9", "VN vn 0 -9", f"VI in m PWL(0 0 1m {v})", "RZ m 0 1m", "XU m s vp vn o LMX58B_LM2904B"]
        body.append("R1 in s 10k")
        if rf:
            body.append(f"R2 s o {rf}")
        r = bb_ng_settle("\n".join(body), ["v(o)-v(m)", "v(s)-v(m)", "v(m)"], ["LMx58B_LM2904B.lib"])
        pts.append((r["v(o)-v(m)"], r["v(s)-v(m)"]))
        vm = r["v(m)"]
    return pts, vm


def p4_numbers():
    pts = [0.2, -0.2, 1.0, -1.0]
    res = {}
    for single in (False, True):
        name = "单 9 V" if single else "±9 V"
        out, vm = p4_inv(pts, single)
        ol, _ = p4_inv([0.2, -0.2], single, rf=None)
        res[single] = dict(out=out, ol=ol, vm=vm)
        if single:
            res[single]["vm_02"] = p4_inv([0.2], True)[1]
        print(f"[02 page4] {name}：输入 +0.2 V → 输出 {out[0][0]:+.3f} V，反相端 {out[0][1] * 1e3:+.2f} mV；"
              f"输入 −0.2 V → 输出 {out[1][0]:+.3f} V，反相端 {out[1][1] * 1e3:+.2f} mV（都相对 M）")
        print(f"[02 page4] {name}：输入 +1.0 V → 输出 {out[2][0]:+.2f} V，反相端 {out[2][1] * 1e3:+.1f} mV；"
              f"输入 −1.0 V → 输出 {out[3][0]:+.2f} V（被削平）")
        print(f"[02 page4] {name}：拔掉 Rf（开环），输入 +0.2 V → {ol[0][0]:+.2f} V，−0.2 V → {ol[1][0]:+.2f} V"
              )
        assert abs(out[0][0] + 2.0) < 0.01 and abs(out[1][0] - 2.0) < 0.01, "±0.2 V 输入在线性区：输出 ∓2.0 V"
        assert abs(out[0][1]) < 3e-3 and abs(out[1][1]) < 3e-3, "线性区反相端离 M 不到 3 mV（虚短）"
        assert out[2][1] > 0.05, "输出削平后反相端不再等于 M（虚短失效）"
    _, vm0 = p4_inv([0.0], True)
    print(f"[02 page4] 单 9 V：输入 0 V 时中点 M 对 0 V 为 {vm0:.3f} V；输入 +0.2 V 时 M 被拉到 {res[True]['vm_02']:.3f} V")
    d, s = res[False], res[True]
    s["vm"] = vm0
    assert abs(d["out"][2][0] + 8.52) < 0.03 and abs(d["out"][3][0] - 7.81) < 0.03
    assert abs(s["out"][2][0] + 4.47) < 0.03 and abs(s["out"][3][0] - 3.32) < 0.03 and abs(s["vm"] - 4.50) < 0.02
    assert abs(d["ol"][0][0] - d["out"][2][0]) < 0.6 and abs(d["ol"][1][0] - d["out"][3][0]) < 0.3
    # 5% 电阻：倍数 100k/10k 的范围
    g_lo, g_hi = 100 * 0.95 / (10 * 1.05), 100 * 1.05 / (10 * 0.95)
    print(f"[02 page4] 5% 电阻时倍数 {g_lo:.2f}～{g_hi:.2f}，输入 0.20 V 时输出 {-0.2 * g_hi:.2f}～{-0.2 * g_lo:.2f} V")
    assert (round(g_lo, 2), round(g_hi, 2)) == (9.05, 11.05)
    # 逐点测量的整条传输特性
    dual, _ = p4_inv(P4_SWEEP, False)
    sing, _ = p4_inv(P4_SWEEP, True)
    return res, np.array([o for o, _ in dual]), np.array([o for o, _ in sing])


# ---------------- 图 02-p4-1：面包板接线图（双 9 V 与单 9 V 共用一张，单电源才插的元件在左上角灰框里） ----------------
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
    bb_res(ax, "h9", "h12", "Rin 10k")
    bb_wire(ax, "j12", "j15", "fb", via=[(12.0, -1.45), (15.0, -1.45)])
    bb_res(ax, "i12", "i14", "Rf 100k", dy=-0.55)
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
    print("[图 02-p4-1] LM358 1～4 脚 f14～f17、8～5 脚 e14～e17；8 脚→V+，4 脚→V−，3 脚→M；"
          "另一半 7、6 脚短接、5 脚→M；电位器 g3/g4/g5，滑动端 i4→i9；Rin h9–h12；j12→j15 接 2 脚；Rf i12–i14；"
          "单电源：a21 接 V+，Rm1 b21–b24、a24 接 M，Rm2 c24–c27、47 μF d24(+)–d27，e27→V−；测点① 第 9 列、② 第 12 列、③ 第 14 列")
    fs.save(fig, N, "02_p4_1_breadboard.png")


# ---------------- 图 02-p4-2：没有示波器时，逐点测传输特性 ----------------
def p4_2_transfer(dual, sing):
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    x = np.array(P4_SWEEP)
    ax.plot(x, -10 * x, **fs.LS["good"], label="理想：输出 = −10 × 输入")
    ax.plot(x, dual, "o-", color=fs.C["vout"], ms=5, lw=1.4, label="两节 9 V（±9 V）")
    ax.plot(x, sing, "s-.", color=fs.C["third"], ms=5, lw=1.4, label="一节 9 V（中点 M 由分压得到）")
    for xx, yy, tx, ty in ((1.5, dual[-1], 1.12, -6.9), (-1.5, dual[0], -1.45, 9.3),
                           (1.5, sing[-1], 1.0, -3.0), (-1.5, sing[0], -1.45, 1.6)):
        ax.annotate(f"{yy:.2f} V", (xx, yy), (tx, ty), fontsize=9, arrowprops=dict(arrowstyle="-", color="0.4", lw=0.7))
        print(f"[数值] 输入 {xx:+.1f} V → 输出 {yy:+.2f} V")
    fs.ref_h(ax, 0, "M")
    ax.set_xlim(-1.65, 1.65); ax.set_ylim(-11, 11)
    fs.axlabels(ax, "输入（电位器滑动端对 M）", "V", "输出对 M", "V")
    ax.legend(loc="upper right")
    assert abs(dual[-1] + 8.5) < 0.1 and abs(sing[-1] + 4.47) < 0.05 and abs(sing[0] - 3.32) < 0.05
    fs.save(fig, N, "02_p4_2_transfer.png")


if __name__ == "__main__":
    _res, _dual, _sing = p4_numbers()
    p4_1_breadboard(); p4_2_transfer(_dual, _sing)


# ======================================================================================
# 第 8 轮补电路图（page1–page3）：正文/例题/练习里描述了具体接法、但附近没有电路图的地方
# ======================================================================================
EMPH = C["third"]      # 新出现、需要强调的连线/元件
BAD = C["bad"]         # 错误或不能用虚短的接法


def _op(d, x, y, flip=False, sup=None):
    """在 (x, y) 放一个运放（y 是两输入端的中线）；flip=True 时同相端在上。
    返回 (op, 上输入脚, 下输入脚)。sup=(上电源文字, 下电源文字) 时画出电源引线。"""
    op = elm.Opamp(leads=True)
    if flip:
        op = op.flip()
    op = op.anchor("center").at((x, y))
    d += op
    pins = sorted([op.in1, op.in2], key=lambda p: -p[1])
    if sup:
        top_txt, bot_txt = sup
        pt, pb = sorted([op.vd, op.vs], key=lambda p: -p[1])     # flip 以后电源脚上下也会对调
        d += elm.Line().at(pt).up().length(0.45)
        d += elm.Label().at((pt[0] + 0.25, pt[1] + 0.45)).label(top_txt, halign="left", fontsize=10)
        d += elm.Line().at(pb).down().length(0.45)
        if bot_txt == "GND":
            d += elm.Ground().at((pb[0], pb[1] - 0.45))
            d += elm.Label().at((pb[0] + 0.35, pb[1] - 0.3)).label("$V_{EE}$ 接地", halign="left", fontsize=10)
        else:
            d += elm.Label().at((pb[0] + 0.25, pb[1] - 0.45)).label(bot_txt, halign="left", fontsize=10)
    return op, pins[0], pins[1]


def _in(d, pin, text, r_txt=None, color="black", length=3.0):
    """从输入脚向左引出：可选串一只电阻，末端是开路圆点 + 文字。返回输入脚旁的节点坐标。"""
    node = (pin[0] - 0.5, pin[1])
    d += elm.Line().endpoints(pin, node).color(color)
    if r_txt:
        d += elm.Resistor().endpoints((node[0] - length, node[1]), node).color(color).label(r_txt, color=color)
        end = (node[0] - length, node[1])
    else:
        end = (node[0] - 1.5, node[1])
        d += elm.Line().endpoints(end, node).color(color)
    d += elm.Dot(open=True).at(end).label(text, "left")
    return node


def _gnd_pin(d, pin):
    """把（下面那只）输入脚接地。"""
    p = (pin[0] - 0.6, pin[1])
    d += elm.Line().endpoints(pin, p)
    d += elm.Ground().at(p)


def _fb(d, node, op, side, r_txt, color="black", dy=1.6, ext=0.6):
    """从输入节点经反馈电阻绕到输出端；side='top' 从上面绕，'bot' 从下面绕。"""
    y = node[1] + (dy if side == "top" else -dy)
    xo = op.out[0] + ext
    d += elm.Dot().at(node)
    d += elm.Line().endpoints(node, (node[0], y)).color(color)
    d += elm.Resistor().endpoints((node[0], y), (xo, y)).color(color).label(r_txt, "top" if side == "top" else "bottom", color=color)
    d += elm.Line().endpoints((xo, y), (xo, op.out[1])).color(color)
    d += elm.Dot().at((xo, op.out[1]))


def _out(d, op, text="$V_o$", length=1.4):
    d += elm.Line().endpoints(op.out, (op.out[0] + length, op.out[1]))
    d += elm.Dot(open=True).at((op.out[0] + length, op.out[1])).label(text, "right")


def _r_to_gnd(d, node, r_txt, color="black"):
    """分压电阻：从节点向左接一只电阻，再接地。"""
    p = (node[0] - 2.6, node[1])
    d += elm.Resistor().endpoints(node, p).color(color).label(r_txt, "bottom", color=color)
    d += elm.Ground().at(p)


# ---------- 图 02-p1-4 负反馈与正反馈的实际接法 ----------
print("[图 02-p1-4] (a) V_i 接同相端、输出经 R_f / R_1 分压送回反相端；(b) 分压送回同相端（正反馈）")
with drawing(fontsize=11) as d:
    op, top, bot = _op(d, 4.0, 0.0, flip=True)
    _in(d, top, "$V_i$")
    _fb(d, (bot[0] - 0.5, bot[1]), op, "bot", "$R_f$", color=C["fb"])
    d += elm.Line().endpoints(bot, (bot[0] - 0.5, bot[1]))
    _r_to_gnd(d, (bot[0] - 0.5, bot[1]), "$R_1$", color=C["fb"])
    _out(d, op)
    d += elm.Label().at((3.0, -3.4)).label("(a) 负反馈：分压送回反相端（−）\n虚短成立")
    op, top, bot = _op(d, 14.0, 0.0, flip=False)
    _in(d, top, "$V_i$")
    _fb(d, (bot[0] - 0.5, bot[1]), op, "bot", "$R_f$", color=BAD)
    d += elm.Line().endpoints(bot, (bot[0] - 0.5, bot[1]))
    _r_to_gnd(d, (bot[0] - 0.5, bot[1]), "$R_1$", color=BAD)
    _out(d, op)
    d += elm.Label().at((13.0, -3.4)).label("(b) 正反馈：同样的分压送回同相端（+）\n输出被推到电源，虚短不成立", color=BAD)
save_schem(d, N, "02_p1_4_feedback_circuits.png")

# ---------- 图 02-p2-4 有反馈（反相放大）与开环的接法 ----------
print("[图 02-p2-4] (a) 图 02-p2-1 的反相放大；(b) 拿掉 R_f，V_i 直接接同相端、反相端接地")
with drawing(fontsize=11) as d:
    op, top, bot = _op(d, 5.0, 0.0, sup=("+15 V", "−15 V"))
    n = _in(d, top, "$V_i$", "$R_1$ 10 kΩ")
    _fb(d, n, op, "top", "$R_f$ 100 kΩ", dy=2.4)
    _gnd_pin(d, bot)
    _out(d, op)
    d += elm.Label().at((4.0, -3.4)).label("(a) 有负反馈：反相放大 −10 倍")
    op, top, bot = _op(d, 15.0, 0.0, flip=True, sup=("+15 V", "−15 V"))
    _in(d, top, "$V_i$", color=BAD)
    _gnd_pin(d, bot)
    _out(d, op)
    d += elm.Label().at((14.0, -3.4)).label("(b) 开环：$R_f$ 拿掉，$V_i$ 接同相端，反相端接地", color=BAD)
save_schem(d, N, "02_p2_4_open_vs_closed_circuit.png")

# ---------- 图 02-p2-5 例 3：反相放大接 5 V 单电源 ----------
print("[图 02-p2-5] 例 3：R_1 = 10 kΩ、R_f = 100 kΩ，V_CC = 5 V、V_EE 接地，V_i = +0.5 V")
with drawing(fontsize=11) as d:
    op, top, bot = _op(d, 5.0, 0.0, sup=("$V_{CC}$ = 5 V", "GND"))
    n = _in(d, top, "$V_i$ = +0.5 V", "$R_1$ 10 kΩ")
    _fb(d, n, op, "top", "$R_f$ 100 kΩ", dy=2.4)
    _gnd_pin(d, bot)
    _out(d, op)
save_schem(d, N, "02_p2_5_single_supply.png")

# ---------- 图 02-p3-3 第二节：−10 倍反相放大接三种电源 ----------
print("[图 02-p3-3] −10 倍反相放大（R_f = 10 R_1），电源分别取 ±15 V、±5 V、5 V 单电源")
with drawing(fontsize=11) as d:
    op, top, bot = _op(d, 5.0, 0.0, sup=("$V_{CC}$：+15 V / +5 V / +5 V", "$V_{EE}$：−15 V / −5 V / 0 V（接地）"))
    n = _in(d, top, "$V_i$\n峰值 0.8 V", "$R_1$")
    _fb(d, n, op, "top", "$R_f = 10\\,R_1$", dy=2.4, ext=3.6)
    _gnd_pin(d, bot)
    _out(d, op, length=4.4)
save_schem(d, N, "02_p3_3_supply_circuit.png")

# ---------- 图 02-p3-4 练习 2 的三种接法 ----------
print("[图 02-p3-4] 练习 2：(a) 开环；(b) 负反馈反相放大；(c) 100 kΩ 接回同相端（正反馈）")
with drawing(fontsize=11) as d:
    op, top, bot = _op(d, 5.0, 0.0, flip=True)
    _in(d, top, "$V_i$", "10 kΩ")
    _gnd_pin(d, bot)
    _out(d, op)
    d += elm.Label().at((4.0, -3.6)).label("(a)")
    op, top, bot = _op(d, 16.0, 0.0)
    n = _in(d, top, "$V_i$", "10 kΩ")
    _fb(d, n, op, "top", "100 kΩ")
    _gnd_pin(d, bot)
    _out(d, op)
    d += elm.Label().at((15.0, -3.6)).label("(b)")
    op, top, bot = _op(d, 27.0, 0.0, flip=True)
    n = _in(d, top, "$V_i$", "10 kΩ")
    _fb(d, n, op, "top", "100 kΩ")
    _gnd_pin(d, bot)
    _out(d, op)
    d += elm.Label().at((26.0, -3.6)).label("(c)")
save_schem(d, N, "02_p3_4_three_configs.png")

# ---------- 图 02-p3-5 练习 4：单电源反相放大，同相端接中点电压 ----------
print("[图 02-p3-5] 练习 4：5 V 单电源 ×10 反相放大，同相端接中点电压 V_M")
with drawing(fontsize=11) as d:
    op, top, bot = _op(d, 5.0, 0.0, sup=("$V_{CC}$ = 5 V", "GND"))
    n = _in(d, top, "$V_i$（以 $V_M$ 为中心）", "$R_1$")
    _fb(d, n, op, "top", "$R_f = 10\\,R_1$", dy=2.4)
    _in(d, bot, "中点电压 $V_M$", color=EMPH)
    _out(d, op)
save_schem(d, N, "02_p3_5_midpoint_bias.png")
