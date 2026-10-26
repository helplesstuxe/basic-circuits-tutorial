"""08 同相放大：全部配图（图 08-p2-2 由 code/08_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/08_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "08"


def noninverting(d, r1="$R_1$ 10 kΩ", rf="$R_f$ 20 kΩ", vminus=None, vplus=None):
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    d += elm.Resistor().left().label(r1)
    d += elm.Ground().right()                          # R1 另一端接地
    up = elm.Line().up().at(j.center).length(2.3 if vminus else 1.5)
    if vminus:
        up.label(vminus, "bottom", fontsize=11)
    d += up
    d += elm.Resistor().right().label(rf).tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    pl = elm.Line().left().at(op.in2).length(3.5)
    if vplus:
        pl.label(vplus, "bottom", fontsize=11)
    d += pl
    d += elm.Dot(open=True).label("$V_i$ 输入", "left")
    d += elm.Line().right().at(op.out).length(1.25)
    d += elm.Dot(open=True).label("$V_o$ 输出", "right")
    return op


# ---------- 图 08-p1-1 同相放大电路 ----------
with drawing() as d:
    noninverting(d)
save_schem(d, N, "08_p1_1_circuit.png")

# ---------- 图 08-p1-2 电压「杠杆」：从地沿 R1、Rf 到输出 ----------
R1, Rf, Vi = 10e3, 20e3, 0.5
Vo = (1 + Rf / R1) * Vi
x = np.array([0, R1, R1 + Rf]) / 1e3                 # 从地算起经过的电阻（kΩ）：地 0，反相端 10，输出 30
v = np.array([0.0, Vi, Vo])
print(f"地 0 V，反相端 {Vi} V（= 输入，虚短），输出端 {Vo} V")
assert abs((Vi - 0) / R1 - (Vo - Vi) / Rf) < 1e-12     # 同一电流流过 R1 和 Rf（虚断）
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(x, v, **fs.LS["third"], label="沿 地 → $R_1$ → $R_f$ 的电压")
ax.axvspan(0, 10, color=fs.C["fill"], alpha=0.8, lw=0)
ax.axvspan(10, 30, color=fs.C["fill2"], alpha=0.8, lw=0)
ax.text(5, 1.6, "$R_1$\n10 kΩ", ha="center", fontsize=9)
ax.text(20, 1.6, "$R_f$　20 kΩ", ha="center", fontsize=9)
ax.plot([0], [0], "^", color="k", ms=9, zorder=6)
ax.plot([10], [Vi], "o", color=fs.C["vin"], ms=6, zorder=6)
ax.plot([30], [Vo], "o", color=fs.C["vout"], ms=6, zorder=6)
fs.mark(ax, 10, Vi, fmt="{:.1f}", unit=" V", dx=6, dy=-12)
fs.mark(ax, 30, Vo, fmt="{:.1f}", unit=" V", dx=-36, dy=4)
ax.annotate("地 0 V（支点）", (0, 0), (3, -0.35), fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))
fs.axlabels(ax, "从地算起经过的电阻", "kΩ", "电压", "V")
ax.set_xlim(-1.5, 32); ax.set_ylim(-0.5, 2.0); ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "08_p1_2_lever.png")

# ---------- 图 08-p1-3 输入与输出：同方向放大 ----------
t = np.linspace(0, 2e-3, 1001)
vi = fs.sine(t, 1e3, amp=0.5)
vo = 3 * vi
print(f"放大 3 倍同相：输入峰值 0.5 V → 输出峰值 {vo.max():.1f} V，0.25 ms 时输入 {vi[125]:.1f} V、输出 {vo[125]:.1f} V")
assert abs(vo[125] - 1.5) < 1e-9
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi, **fs.LS["vin"], label="$V_i$ 输入")
ax.plot(t * 1e3, vo, **fs.LS["vout"], label="$V_o$ 输出（3 倍）")
fs.ref_h(ax, 0, "0 V")
fs.mark(ax, 0.25, vi[125], fmt="{:.1f}", unit=" V", dx=6, dy=-12)
fs.mark(ax, 0.25, vo[125], fmt="{:.1f}", unit=" V", dx=6, dy=2)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.legend(loc="upper right", fontsize=8)
fs.save(fig, N, "08_p1_3_inphase_wave.png")

# ---------- 图 08-p2-1 分析图 ----------
with drawing() as d:
    noninverting(d, vminus="$V_- \\approx V_i$（虚短）", vplus="$I \\approx 0$（虚断）")
save_schem(d, N, "08_p2_1_analysis.png")

# ---------- 图 08-p2-3 两种接法的倍数对比 ----------
k = np.linspace(0, 10, 101)                           # 电阻比 Rf/R1
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(k, 1 + k, **fs.LS["vout"], label="同相：$1 + R_f/R_1$")
ax.plot(k, k, **fs.LS["third"], label="反相：$R_f/R_1$（取绝对值）")
fs.ref_h(ax, 1, "1 倍")
for kk in (0, 2):
    fs.mark(ax, kk, 1 + kk, fmt="{:.0f}", dx=-4, dy=8)
print("电阻比 0 时同相倍数 1（跟随器），电阻比 2 时同相 3 倍、反相 2 倍")
assert (1 + k).min() == 1
fs.axlabels(ax, "电阻比 $R_f/R_1$", None, "放大倍数", None); ax.legend(loc="upper left", fontsize=8)
fs.save(fig, N, "08_p2_3_gain_compare.png")

# ---------- 图 08-p3-1 单电源 5 V：输入太大就削顶 ----------
VCC, V_HI = 5.0, 5.0 - 1.5                            # LM358B 正向摆幅约 V+ − 1.5 V
vin = np.linspace(0, 2.5, 251)
vout = np.clip(2 * vin, 0.0, V_HI)                    # 2 倍同相放大，输出不超过 3.5 V（低端约 0 V，此处忽略 0.1 V）
v_knee = V_HI / 2
print(f"单电源 5 V、2 倍：输出最高 {V_HI} V，输入超过 {v_knee:.2f} V 开始削顶")
assert abs(v_knee - 1.75) < 1e-9
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(vin, 2 * vin, **fs.LS["good"], label="理想 $V_o = 2V_i$")
ax.plot(vin, vout, **fs.LS["vout"], label="实际 $V_o$")
fs.ref_h(ax, V_HI, f"{V_HI} V（摆幅上限）", x=0.05, ha="left")
fs.ref_v(ax, v_knee, f"{v_knee:.2f} V", y=0.4)
fs.mark(ax, v_knee, V_HI, fmt="{:.1f}", unit=" V", dx=6, dy=-14)
fs.axlabels(ax, "输入 $V_i$", "V", "输出 $V_o$", "V"); ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "08_p3_1_single_supply_clip.png")

# ---------- 图 08-p3-2 带宽：同相 f_c ≈ GBW / A_v ----------
GBW = 1.2e6
f = np.logspace(2, 7, 400)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
for G, key in ((2, "vout"), (10, "third"), (100, "fb")):
    fc = GBW / G                                      # 同相放大：带宽 ≈ GBW / A_v
    mag = G / np.sqrt(1 + (f / fc) ** 2)
    ax.loglog(f, mag, **fs.LS[key], label=f"$A_v$ = {G}：$f_c$ ≈ {fc/1e3:.0f} kHz")
    fs.mark(ax, fc, G / np.sqrt(2), fmt="{:.2g}", dx=5, dy=4)
    print(f"A_v = {G}: 带宽 f_c ≈ {fc/1e3:.1f} kHz，此处倍数 {G/np.sqrt(2):.2f}")
assert abs(GBW / 10 - 120e3) < 1
fs.axlabels(ax, "频率", "Hz", "放大倍数", None); ax.legend(loc="lower left", fontsize=8)
fs.save(fig, N, "08_p3_2_bandwidth.png")

# ---------- 正文与练习里的其余数字（只打印 + 断言） ----------
IB = 10e-9                                            # LM358B 输入偏置电流典型值 10 nA（最大 35 nA，TI 手册）
for Rsrc in (100e6,):
    print(f"输入电流 {IB*1e9:g} nA 流过 {Rsrc/1e6:g} MΩ 内阻，误差电压 {IB*Rsrc:.1f} V（最大 35 nA 时 {35e-9*Rsrc:.1f} V）")
assert abs(IB * 100e6 - 1.0) < 1e-9
Rs, R1, Rf, Vs = 50e3, 10e3, 20e3, 1.0                 # 新练习 2：内阻 50 kΩ 的分压器输出 1 V
v_inv = -Rf / (Rs + R1) * Vs
v_non = (1 + Rf / R1) * Vs
print(f"练习 2：反相 {v_inv:.3f} V（只有理想 -2 V 的 {v_inv/-2*100:.0f}%），同相 {v_non:.1f} V")
assert abs(v_inv + 0.333) < 0.001 and v_non == 3.0
print(f"带宽两种写法：反馈分压比 R1/(R1+Rf)，同相 10 倍 → {1.2e6/10/1e3:.0f} kHz，反相 10 倍 → {1.2e6/11/1e3:.0f} kHz")


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


def p4_non(v, rf=20e3, rs=0.0, mode="dual"):
    """同相放大接 9 V 电池，输入相对 M。rf=None 表示拔掉 Rf（开环），rf=0 表示 Rf 换成导线。
    mode：dual = 两节 9 V（M = A− 与 B+ 的连接点）；single = 一节 9 V、M 由 1k/1k 分压；gnd = 一节 9 V、M 就是电池负极（只放大正信号）。
    rs：电位器滑动端和 3 脚之间串的电阻（模拟高内阻信号源）。输入从 0 V 用 1 ms 升到 v，读稳定值。"""
    if mode == "dual":
        body = ["VP vp 0 9", "VN vn 0 -9", "RZ m 0 1m"]
    elif mode == "single":
        body = ["VP vp 0 9", "VN vn 0 0", "RM1 vp m 1k", "RM2 m 0 1k"]
    else:
        body = ["VP vp 0 9", "VN vn 0 0", "RZ m 0 1m"]
    body += [f"VI w m PWL(0 0 1m {v})", f"RS w in {max(rs, 1e-3):g}", "R1 s m 10k", "XU in s vp vn o LMX58B_LM2904B"]
    if rf is not None:
        body.append(f"R2 s o {max(rf, 1e-3):g}")
    ex = ["v(o)-v(m)", "v(s)-v(m)", "v(s)-v(in)", "v(o)-v(s)", "v(in)-v(m)", "v(w)-v(in)", "v(m)"]
    r = bb_ng_settle("\n".join(body), ex, ["LMx58B_LM2904B.lib"])
    return dict(out=r[ex[0]], vm_=r[ex[1]], dvin=r[ex[2]], vrf=r[ex[3]], vin=r[ex[4]], vrs=r[ex[5]], m=r[ex[6]])


def _rng_non(rf, r1, vin):
    """5% 电阻时同相放大输出范围：倍数 1 + Rf/R1。"""
    return (1 + rf * 0.95 / (r1 * 1.05)) * vin, (1 + rf * 1.05 / (r1 * 0.95)) * vin


def p4_numbers():
    r = {}
    a = r["a"] = p4_non(0.5)
    print(f"[08 page4] ±9 V，输入 +0.50 V：输出 {a['out']:+.3f} V，反相端 {a['vm_']:+.4f} V，反相端−同相端 {a['dvin'] * 1e3:+.2f} mV，"
          f"Rf 两端 {a['vrf']:.3f} V，R1 电流 {a['vm_'] / 10e3 * 1e3:.4f} mA，Rf 电流 {a['vrf'] / 20e3 * 1e3:.4f} mA")
    lo, hi = _rng_non(20e3, 10e3, 0.5)
    print(f"[08 page4] 5% 电阻：输入 0.5 V 时输出 {lo:.3f}～{hi:.3f} V")
    assert abs(a["out"] - 1.5) < 0.01 and abs(a["dvin"]) < 3e-3 and abs(a["vrf"] - 1.0) < 0.01
    assert (round(lo, 2), round(hi, 2)) == (1.4, 1.61)
    x = r["neg"] = p4_non(-0.2)
    print(f"[08 page4] 输入 −0.20 V：输出 {x['out']:+.3f} V（5% 范围 {_rng_non(20e3, 10e3, -0.2)[1]:+.3f}～{_rng_non(20e3, 10e3, -0.2)[0]:+.3f} V）")
    assert abs(x["out"] + 0.6) < 0.01
    x = r[39e3] = p4_non(0.5, rf=39e3)
    lo, hi = _rng_non(39e3, 10e3, 0.5)
    print(f"[08 page4] Rf = 39 kΩ，输入 +0.50 V：输出 {x['out']:+.3f} V（5% 范围 {lo:.2f}～{hi:.2f} V）")
    assert abs(x["out"] - 2.45) < 0.01 and (round(lo, 2), round(hi, 2)) == (2.26, 2.66)
    x = r[0] = p4_non(0.5, rf=0)
    print(f"[08 page4] Rf 换导线，输入 +0.50 V：输出 {x['out']:+.4f} V")
    assert abs(x["out"] - 0.5) < 0.003
    x = r["rs"] = p4_non(0.5, rs=100e3)
    print(f"[08 page4] 串 Rs = 100 kΩ，滑动端 +0.50 V：3 脚 {x['vin']:.4f} V，Rs 两端 {x['vrs'] * 1e3:+.2f} mV，输出 {x['out']:+.3f} V")
    assert abs(x["out"] - 1.5) < 0.015 and abs(x["vrs"]) < 5e-3
    x = r["ol"] = p4_non(0.5, rf=None)
    print(f"[08 page4] 拔掉 Rf，输入 +0.50 V：输出 {x['out']:+.2f} V（贴 V+）")
    assert 7.5 < x["out"] < 8.2
    for v in (0.5, -0.5):
        x = r[("s", v)] = p4_non(v, mode="single")
        print(f"[08 page4] 单 9 V（分压中点），输入 {v:+.2f} V：输出对 M {x['out']:+.3f} V，M 对 0 V {x['m']:.3f} V")
    assert abs(r[("s", 0.5)]["out"] - 1.5) < 0.01 and abs(r[("s", -0.5)]["out"] + 1.5) < 0.01
    for v in (0.5, 1.0, -0.2):
        x = r[("g", v)] = p4_non(v, rf=100e3, mode="gnd")
        print(f"[08 page4] 单 9 V、M = 电池负极，Rf = 100 kΩ，输入 {v:+.2f} V：输出对 0 V {x['out']:+.3f} V")
    lo, hi = _rng_non(100e3, 10e3, 0.5)
    print(f"[08 page4] 5% 电阻：11 倍、输入 0.5 V 时输出 {lo:.2f}～{hi:.2f} V")
    assert abs(r[("g", 0.5)]["out"] - 5.5) < 0.02 and 7.3 < r[("g", 1.0)]["out"] < 8.0 and 0 < r[("g", -0.2)]["out"] < 0.05
    fam = {
        "dual": np.array([p4_non(v, rf=100e3)["out"] for v in P4_SWEEP]),
        # M = 电池负极时，输入不能比 4 脚（0 V）低 0.3 V 以上（LM358 绝对最大额定值），所以只测到 −0.25 V
        "gnd": np.array([p4_non(v, rf=100e3, mode="gnd")["out"] for v in P4_SWEEP if v >= -0.25]),
    }
    return r, fam


# ---------------- 图 08-p4-1：面包板接线图（双 9 V 与单 9 V 共用一张，单电源才插的元件在左上角灰框里） ----------------
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
    # 输入 → 3 脚：g9→g16 画成拱形跳线，从 g10～g15（含测点② 的 g12）上方跨过，不接触中间各列
    _arc_x = np.linspace(9, 16, 29)
    _arc = [(x, 2.0 + 0.62 * (1 - ((x - 12.5) / 3.5) ** 2) ** 0.5) for x in _arc_x[1:-1]]
    bb_wire(ax, "g9", "g16", "sig", via=_arc)
    # 反相 ×10
    bb_block(ax, ["g3", "g4", "g5"], "", pins=["端", "滑", "端"], fc="#d7ccc8")
    _bb_label(ax, 4, 3.05, "电位器 10k")
    bb_wire(ax, "j5", "B2-5", "gnd")
    bb_wire(ax, "i4", "i9", "sig")
    _bb_label(ax, 6.5, -0.45, "第 10 步换成 Rs 100k")
    bb_res(ax, "h10", "h12", "R1 10k")
    bb_wire(ax, "j10", "B2-10", "gnd")                     # R1 下端接 M
    bb_wire(ax, "j12", "j15", "fb", via=[(12.0, -1.45), (15.0, -1.45)])
    bb_res(ax, "i12", "i14", "Rf 20k（39k/导线/100k）", dy=-0.55)
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
    bb_probe(ax, "h9", "①", dx=-0.6, dy=0.9)
    bb_probe(ax, "g12", "②", dx=0.55, dy=-0.5)     # 放在孔下方，引线不与上方拱形跳线交叉
    bb_probe(ax, "h14", "③", dx=0.75, dy=0.55)
    bb_legend(ax, [("pos", "红：V+"), ("neg", "紫：V−"), ("gnd", "黑：M"), ("sig", "蓝：输入"), ("fb", "绿：反馈/短接")],
              x=5.4, y=-5.0)
    print("[图 08-p4-1] LM358 同相放大：1～4 脚 f14～f17、8～5 脚 e14～e17；8 脚→V+，4 脚→V−；另一半 7、6 脚短接、5 脚→M；"
          "电位器 g3/g4/g5，滑动端 i4→i9（第 10 步换 Rs 100k）；g9→g16 接 3 脚；R1 h10–h12、j10→M；j12→j15 接 2 脚；Rf i12–i14；"
          "单电源：a21 接 V+，Rm1 b21–b24、a24 接 M，Rm2 c24–c27、47 μF d24(+)–d27，e27→V−；测点① 第 9 列、② 第 12 列、③ 第 14 列")
    fs.save(fig, N, "08_p4_1_breadboard.png")


# ---------------- 图 08-p4-2：没有示波器时，逐点测 11 倍同相放大（双 9 V 与"M = 电池负极"的单 9 V） ----------------
def p4_2_transfer(fam):
    fig, ax = plt.subplots(figsize=fs.SIZE["tall"])
    x = np.array(P4_SWEEP)
    ax.plot(x, 11 * x, **fs.LS["good"], label="理想 +11 倍")
    ax.plot(x, fam["dual"], color=fs.C["vout"], marker="o", ms=5, lw=1.5, label="两节 9 V（输出对 M）")
    xg = np.array([v for v in P4_SWEEP if v >= -0.25])
    ax.plot(xg, fam["gnd"], color=fs.C["third"], marker="s", ms=5, lw=1.3, ls="-.", label="一节 9 V、M = 电池负极（输出对 0 V）")
    hi_d, lo_d, hi_g, lo_g = fam["dual"].max(), fam["dual"].min(), fam["gnd"].max(), fam["gnd"].min()
    print(f"[数值] 11 倍：双 9 V 削平在 {hi_d:+.2f} / {lo_d:+.2f} V；单 9 V（M = 负极）削平在 {hi_g:+.2f} / {lo_g:+.3f} V")
    ax.annotate(f"{hi_d:.2f} V", (1.5, hi_d), (1.05, 10.0), fontsize=9, arrowprops=dict(arrowstyle="-", color="0.4", lw=0.7))
    ax.annotate(f"{lo_d:.2f} V", (-1.5, lo_d), (-1.45, -6.4), fontsize=9, arrowprops=dict(arrowstyle="-", color="0.4", lw=0.7))
    ax.annotate(f"贴底 {lo_g:.2f} V（不能再往负调）", (-0.25, lo_g), (-1.55, 2.2), fontsize=9, arrowprops=dict(arrowstyle="-", color="0.4", lw=0.7))
    fs.ref_h(ax, 0, "M")
    ax.set_xlim(-1.65, 1.65); ax.set_ylim(-11, 11)
    fs.axlabels(ax, "输入（3 脚对 M）", "V", "输出", "V")
    ax.legend(loc="lower right", fontsize=8.5)
    assert 7.5 < hi_d < 8.2 and -9 < lo_d < -8.3 and 7.3 < hi_g < 8.0 and 0 < lo_g < 0.05
    fs.save(fig, N, "08_p4_2_transfer.png")


if __name__ == "__main__":
    _r, _fam = p4_numbers()
    p4_1_breadboard(); p4_2_transfer(_fam)


# ====================== 第 8 轮补电路图（page1–3） ======================
EMPH = fs.C["third"]          # 新出现的元件用强调色
BAD = fs.C["bad"]


def _vres(d, p, q, text, side="right", color="black"):
    """竖直电阻，标签放在电阻中部的左侧或右侧。"""
    d += elm.Resistor().endpoints(p, q).color(color)
    x = p[0] + (0.45 if side == "right" else -0.45)
    d += elm.Label().at((x, (p[1] + q[1]) / 2)).label(text, halign="left" if side == "right" else "right", fontsize=11, color=color)


def _non_core(d, r1="$R_1$", rf="$R_f$", r1_bottom=None):
    """同相放大主体（+ 在上、− 在下）。R1 从反馈节点竖直向下；r1_bottom=None 时接地。
    返回 (op, 同相端引线左端坐标, R1 下端坐标)。"""
    op = elm.Opamp(leads=True).flip().at((0, 0)).anchor("in2")
    d += op
    j = (op.in1[0] - 0.5, op.in1[1])
    m = (j[0], j[1] - 1.3)
    xo = op.out[0] + 0.5
    d += elm.Line().endpoints(op.in1, j)
    d += elm.Line().endpoints(j, m)
    d += elm.Dot().at(m)
    d += elm.Resistor().endpoints(m, (xo, m[1])).label(rf, "bottom")
    d += elm.Line().endpoints((xo, m[1]), (xo, op.out[1]))
    d += elm.Dot().at((xo, op.out[1]))
    yb = m[1] - 2.0 if r1_bottom is None else r1_bottom
    _vres(d, m, (m[0], yb), r1, "right")
    if r1_bottom is None:
        d += elm.Ground().at((m[0], yb))
    d += elm.Line().endpoints(op.out, (op.out[0] + 1.25, op.out[1]))
    d += elm.Dot(open=True).at((op.out[0] + 1.25, op.out[1])).label("$V_o$", "right")
    return op, op.in2, (m[0], yb)


# ---------- 图 08-p2-4 例 3：同相加法器 ----------
with drawing() as d:
    op, p_in, _ = _non_core(d, "$R_1$ 10 kΩ", "$R_f$ 10 kΩ")
    P = (p_in[0] - 1.0, p_in[1])
    d += elm.Line().endpoints(P, p_in)
    d += elm.Dot().at(P)
    d += elm.Label().at((P[0] + 0.15, P[1] + 0.45)).label("同相端 = $(V_1+V_2)/2$", halign="center", fontsize=10)
    d += elm.Resistor().endpoints((P[0] - 3.0, P[1]), P).label("10 kΩ", "bottom").color(EMPH)
    d += elm.Dot(open=True).at((P[0] - 3.0, P[1])).label("$V_1$", "left")
    d += elm.Line().endpoints(P, (P[0], P[1] - 2.0)).color(EMPH)
    d += elm.Resistor().endpoints((P[0] - 3.0, P[1] - 2.0), (P[0], P[1] - 2.0)).label("10 kΩ", "bottom").color(EMPH)
    d += elm.Dot(open=True).at((P[0] - 3.0, P[1] - 2.0)).label("$V_2$", "left")
save_schem(d, N, "08_p2_4_noninv_summer.png")

# ---------- 图 08-p3-3 交流耦合：同相端要有直流通路 ----------
with drawing() as d:
    for k, x0 in enumerate([0.0, 13.0]):
        with d.hold():
            d.move(x0, 0)
            op = elm.Opamp(leads=True).flip().at((x0, 0)).anchor("in2")
            d += op
            j = (op.in1[0] - 0.5, op.in1[1]); m = (j[0], j[1] - 1.3); xo = op.out[0] + 0.5
            d += elm.Line().endpoints(op.in1, j); d += elm.Line().endpoints(j, m); d += elm.Dot().at(m)
            d += elm.Resistor().endpoints(m, (xo, m[1])).label("$R_f$", "bottom")
            d += elm.Line().endpoints((xo, m[1]), (xo, op.out[1])); d += elm.Dot().at((xo, op.out[1]))
            _vres(d, m, (m[0], m[1] - 2.0), "$R_1$", "right")
            d += elm.Ground().at((m[0], m[1] - 2.0))
            d += elm.Line().endpoints(op.out, (op.out[0] + 1.0, op.out[1]))
            d += elm.Dot(open=True).at((op.out[0] + 1.0, op.out[1])).label("$V_o$", "right")
            P = (op.in2[0] - 1.4, op.in2[1])
            d += elm.Line().endpoints(P, op.in2)
            d += elm.Capacitor().endpoints((P[0] - 2.4, P[1]), P).label("隔直电容")
            d += elm.Dot(open=True).at((P[0] - 2.4, P[1])).label("$V_i$", "left")
            if k == 0:
                d += elm.Dot().at(P).color(BAD)
                d += elm.Label().at((P[0] - 1.4, P[1] - 1.6)).label("同相端没有直流通路：\n电压慢慢漂，输出贴轨", fontsize=10, color=BAD)
                d += elm.Label().at((x0 + 1.0, m[1] - 3.4)).label("(a) 只串电容", fontsize=11, color=BAD)
            else:
                d += elm.Dot().at(P)
                _vres(d, P, (P[0], P[1] - 3.0), "100 kΩ", "left", EMPH)
                d += elm.Ground().at((P[0], P[1] - 3.0)).color(EMPH)
                d += elm.Label().at((x0 + 1.0, m[1] - 3.4)).label("(b) 加 100 kΩ 接地，给出直流通路", fontsize=11)
save_schem(d, N, "08_p3_3_ac_coupling.png")

# ---------- 图 08-p3-4 练习 4：单电源 2.5 V 偏置的同相放大 ----------
with drawing() as d:
    yB = -5.0                                            # 2.5 V 偏置点所在的横线
    op, p_in, r1b = _non_core(d, "$R_1$", "$R_f$", r1_bottom=yB)
    P = (p_in[0] - 1.4, p_in[1])
    d += elm.Line().endpoints(P, p_in)
    d += elm.Dot().at(P)
    d += elm.Capacitor().endpoints((P[0] - 2.6, P[1]), P).label("$C$")
    d += elm.Dot(open=True).at((P[0] - 2.6, P[1])).label("$V_i$", "left")
    _vres(d, P, (P[0], yB), "100 kΩ", "left")
    xd = P[0] - 4.2                                      # 两个相等电阻从 5 V 分出 2.5 V
    d += elm.Line().endpoints((xd, yB), r1b).color(EMPH)
    d += elm.Dot().at((P[0], yB)); d += elm.Dot().at((xd, yB))
    _vres(d, (xd, yB + 2.4), (xd, yB), "$R$", "left", EMPH)
    d += elm.Label().at((xd, yB + 2.75)).label("+5 V", fontsize=10)
    _vres(d, (xd, yB), (xd, yB - 2.2), "$R$", "left", EMPH)
    d += elm.Ground().at((xd, yB - 2.2))
    d += elm.Dot().at((xd + 1.4, yB))
    d += elm.Capacitor().endpoints((xd + 1.4, yB), (xd + 1.4, yB - 1.6)).color(EMPH)
    d += elm.Label().at((xd + 1.85, yB - 0.8)).label("稳压电容", halign="left", fontsize=10, color=EMPH)
    d += elm.Ground().at((xd + 1.4, yB - 1.6))
    d += elm.Label().at(((P[0] + r1b[0]) / 2, yB - 0.45)).label("2.5 V 偏置点", fontsize=10, color=EMPH)
save_schem(d, N, "08_p3_4_bias_exercise.png")
