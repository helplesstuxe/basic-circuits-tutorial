"""03 电压跟随器：全部配图（图 03-p2-2 由 code/03_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/03_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

N = "03"


def follower(d, vin="$V_i$ 输入", vout="$V_o$ 输出", lab_minus=None, lab_plus=None, out_len=1.25):
    """跟随器：输出直接接回反相端。返回 (op, 输入端点, 输出端点)。"""
    d += (op := elm.Opamp(leads=True))
    d += elm.Line().left().at(op.in1).length(0.5)
    d += (j := elm.Dot())
    up = elm.Line().up().at(j.center).length(1.6 if lab_minus else 1.2)
    if lab_minus:
        up.label(lab_minus, "bottom", fontsize=11)
    d += up
    d += elm.Line().right().tox(op.out.x + 0.5)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    pl = elm.Line().left().at(op.in2).length(3.2 if lab_plus else 1.5)
    if lab_plus:
        pl.label(lab_plus, "bottom", fontsize=11)
    d += pl
    if vin:
        d += elm.Dot(open=True).label(vin, "left")
    pin = d.here
    d += elm.Line().right().at(op.out).length(out_len)
    if vout:
        d += elm.Dot(open=True).label(vout, "right")
    pout = d.here
    return op, pin, pout


def divider(d, top="10 kΩ", bot="10 kΩ", vs="10 V"):
    """从当前位置向左画分压器：返回分压点。"""
    d += elm.Line().left().length(0.8)
    d += (mid := elm.Dot())
    d += elm.Resistor().up().label(top, "bottom")
    d += elm.Vdd().label(vs)
    d += elm.Resistor().down().at(mid.center).label(bot, "bottom")
    d += elm.Ground()
    return mid


# ---------- 图 03-p1-2 跟随器电路 ----------
with drawing() as d:
    follower(d)
save_schem(d, N, "03_p1_2_circuit.png")

# ---------- 图 03-p1-1 分压器直接接负载 ----------
with drawing() as d:
    d += (s := elm.Dot(open=True).label("分压点", "top"))
    d += elm.Line().right().at(s.center).length(1.5)
    d += elm.Resistor().down().label("$R_L$ 1 kΩ\n负载", "bottom")
    d += elm.Ground()
    d.here = s.center
    d += elm.Line().left().length(0.01)
    divider(d)
save_schem(d, N, "03_p1_1_direct.png")

# ---------- 图 03-p1-3 分压器经跟随器接负载 ----------
with drawing() as d:
    op, pin, pout = follower(d, vin=None, vout=None, out_len=0.8)
    d.here = pin
    divider(d)
    d += elm.Resistor().down().at(pout).label("$R_L$ 1 kΩ\n负载", "bottom")
    d += elm.Ground()
save_schem(d, N, "03_p1_3_buffered.png")
print("分压 10 V × 10/(10+10) = 5 V；直接接 1 kΩ 负载只剩 "
      f"{10 * (1e3 * 10e3 / 11e3) / (10e3 + 1e3 * 10e3 / 11e3):.2f} V，经跟随器仍为 5.00 V")

# ---------- 图 03-p2-1 分析图 ----------
with drawing() as d:
    follower(d, lab_minus="$V_- = V_o$（导线直连）", lab_plus="$I \\approx 0$，$V_+ = V_i$")
save_schem(d, N, "03_p2_1_analysis.png")

# ---------- 图 03-p2-3 基准电压缓冲 ----------
with drawing() as d:
    op, pin, pout = follower(d, vin=None, vout=None, out_len=4.4)
    d.here = pin
    d += elm.Line().left().length(0.8)
    d += (mid := elm.Dot())
    d += elm.Resistor().up().label("10 kΩ", "bottom")
    d += elm.Vdd().label("5 V")
    d += elm.Resistor().down().at(mid.center).label("10 kΩ", "bottom")
    d += elm.Ground()
    d += elm.Line().left().at(mid.center).length(1.6)
    d += elm.Capacitor().down().label("100 nF", "top")
    d += elm.Ground()
    for dx, txt in ((1.6, "去 ADC 参考端"), (4.4, "去比较器门限")):
        x = op.out.x + dx
        if dx < 4:
            d += elm.Dot().at((x, op.out.y))
        d += elm.Line().down().at((x, op.out.y)).length(1.0)
        d += elm.Dot(open=True).label(txt, "bottom")
    d += elm.Line().right().at(op.out).length(0.01).label("$V_{ref}$ = 2.5 V", "top", ofst=(2.0, 0.1))
save_schem(d, N, "03_p2_3_vref_buffer.png")

# ---------- 图 03-p3-1 容性负载：振铃与隔离电阻 ----------
wt = 2 * np.pi * 1.2e6                                 # LM358B 增益带宽积 1.2 MHz
Ro, CL = 300.0, 0.1e-6                                 # LM358B 手册：开环输出电阻 RO = 300 Ω（f = 1 MHz、IO = 0）；负载电容 0.1 μF
CLOAD_RATED = 100e-12                                  # LM358B 手册：容性负载驱动能力 100 pF
print(f"负载电容 0.1 μF 是手册容性负载能力 100 pF 的 {CL / CLOAD_RATED:.0f} 倍")
assert round(CL / CLOAD_RATED) == 1000
t = np.linspace(0, 60e-6, 6001)
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e6, np.where(t > 0, 1.0, 0.0) * 0.1, **fs.LS["vin"], label="$V_i$ 输入阶跃 0.1 V")
res, settle = {}, {}
for Riso, key, name in ((0.0, "bad", "直接接 0.1 μF"), (10.0, "third", "串 10 Ω"), (33.0, "vout", "串 33 Ω 隔离电阻")):
    T = (Ro + Riso) * CL
    # 负载电压 / 输入 = wt / (T s² + (1 + wt·Riso·CL) s + wt)（单极点运放 + 输出电阻 + 隔离电阻 + 电容）
    _, y = signal.step(([wt], [T, 1 + wt * Riso * CL, wt]), T=t)
    y = 0.1 * y
    k = np.argmax(y)
    os_pct = (y[k] / 0.1 - 1) * 100
    res[Riso] = os_pct
    out = np.abs(y - 0.1) > 0.002                      # 偏离 0.1 V 超过 2%
    settle[Riso] = t[np.nonzero(out)[0][-1]] if out[-1] == False else np.inf
    ax.plot(t * 1e6, y, **fs.LS[key], label=f"负载电压：{name}")
    if Riso != 10.0:
        fs.mark(ax, t[k] * 1e6, y[k], fmt="{:.3f}", unit=" V", dx=6, dy=4)
    print(f"{name}：最高 {y[k]:.3f} V，过冲 {os_pct:.1f}%，进入 ±2% 的时间 {settle[Riso] * 1e6:.1f} μs")
assert res[0.0] > 80 and 30 < res[10.0] < 50 and res[33.0] < 2
assert settle[0.0] == np.inf and settle[33.0] < 10e-6   # 直接接电容：60 μs 内都没稳住；33 Ω：10 μs 内稳住
print(f"1 mA 负载电流在 33 Ω 上的压降：{1e-3 * 33 * 1e3:.0f} mV")
fs.ref_h(ax, 0.1, "0.1 V")
fs.axlabels(ax, "时间", "μs", "电压", "V"); ax.legend(loc="upper right", fontsize=8, ncol=2)
ax.set_ylim(-0.01, 0.27)
fs.save(fig, N, "03_p3_1_cap_load.png")

# ---------- 图 03-p3-2 单电源 5 V 跟随器：两头都到不了 ----------
vin = np.linspace(0, 5, 501)
V_HI, V_LO = 5.0 - 1.5, 0.02                           # LM358B：输出最高约 V+ − 1.5 V；最低按 SPICE（TI 模型 0.024 V）取约 0.02 V（第 7 轮由 0.1 V 更正）
vout = np.clip(vin, V_LO, V_HI)
print(f"单电源 5 V 跟随器：输出范围 {V_LO} V ～ {V_HI} V")
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(vin, vin, **fs.LS["good"], label="理想 $V_o = V_i$")
ax.plot(vin, vout, **fs.LS["vout"], label="实际 $V_o$")
fs.ref_h(ax, V_HI, f"{V_HI} V", x=0.02, ha="left")
fs.ref_h(ax, V_LO, f"{V_LO} V", x=0.6, ha="left")
fs.mark(ax, V_HI, V_HI, fmt="{:.1f}", unit=" V", dx=6, dy=-14)
assert vout.max() == 3.5 and vout.min() == 0.02
fs.axlabels(ax, "输入 $V_i$", "V", "输出 $V_o$", "V"); ax.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "03_p3_2_single_supply.png")

# ---------- 正文与练习里的其余数字（只打印 + 断言） ----------
# 压摆率：不用求导，直接数值算正弦相邻两点的斜率，找最大值，和 2πfVp 对比
f, Vp = 1e3, 1.0
tt = np.linspace(0, 1 / f, 100001)
vv = Vp * np.sin(2 * np.pi * f * tt)
slope = np.max(np.abs(np.diff(vv) / np.diff(tt)))
print(f"1 kHz、峰值 1 V 正弦：数值最大斜率 {slope:.1f} V/s，2πfVp = {2*np.pi*f*Vp:.1f} V/s，平均斜率 4fVp = {4*f*Vp:.0f} V/s")
assert abs(slope / (2 * np.pi * f * Vp) - 1) < 1e-3
print(f"最大斜率 / 平均斜率 = {slope/(4*f*Vp):.3f}（π/2 = {np.pi/2:.3f}）")
# 分压器内阻：两只 10 kΩ 并联 5 kΩ，接 1 kΩ 负载
print(f"5 V × 1/(5+1) = {5*1/(5+1):.2f} V")
assert abs(5 / 6 - 0.83) < 0.01
# 诊断练习：隔离电阻 33 Ω、负载 0.5 mA 的压降
print(f"33 Ω × 0.5 mA = {33*0.5e-3*1e3:.1f} mV")
assert abs(33 * 0.5e-3 - 0.0165) < 1e-9


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
    """跳线：kind 取 pos/gnd/neg/sig/out（红/黑/红紫/蓝/橙）。via=[(x, y), ...] 时按这些拐点折线走，避免压住元件。"""
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
P4_LOADS = [1e3, 2.2e3, 4.7e3, 10e3, 22e3, 47e3, 100e3]


def p4_fol(rd1=10e3, rd2=10e3, rl=None, at="out", mode="dual"):
    """分压器（Rd1 接 V+、Rd2 接 M，None 表示拔掉）→ 跟随器 → 负载 RL（None 表示不接；at = "out" 接跟随器输出，"src" 直接接分压点）。
    mode：dual = 两节 9 V，M = A− 与 B+ 的连接点；single = 一节 9 V，M 就是电池负极（= V−）。
    读数都相对 M。分压器顶端用一个与 V+ 等值的 PWL 源从 0 V 用 1 ms 升到 9 V（电路上等同于接 V+），读稳定值。"""
    if mode == "dual":
        body = ["VP vp m 9", "VN m vn 9", "RZ m 0 1m"]
    else:  # 单电源：V− 就是 M；把 M 放在 SPICE 地以下 4.5 V，避开模型在"V− 接全局地 + 重负载"时的假解（见 review/spice/03.md）
        body = ["VP vp m 9", "VN vn m 0", "VG m 0 -4.5"]
    body.append("VD d m PWL(0 0 1m 9)")
    if rd1 is not None:
        body.append(f"RD1 d s {rd1:g}")
    if rd2 is not None:
        body.append(f"RD2 s m {rd2:g}")
    body.append("XU s o vp vn o LMX58B_LM2904B")
    if rl is not None:
        body.append(f"RL {'o' if at == 'out' else 's'} m {rl:g}")
    ex = ["v(s)-v(m)", "v(o)-v(m)", "v(o)-v(s)"]
    r = bb_ng_settle("\n".join(body), ex, ["LMx58B_LM2904B.lib"])
    return dict(src=r[ex[0]], out=r[ex[1]], d=r[ex[2]])


def _par(a, b):
    return a * b / (a + b)


def _rng_div(rd1, rd2, rl=None, v=9.0):
    """5% 电阻时分压点（可带负载 RL，RL 也按 5%）的范围；电源按 9 V 计。"""
    vals = []
    for k1 in (0.95, 1.05):
        for k2 in (0.95, 1.05):
            for k3 in (0.95, 1.05):
                lo = rd2 * k2 if rl is None else _par(rd2 * k2, rl * k3)
                vals.append(v * lo / (rd1 * k1 + lo))
    return min(vals), max(vals)


P4_PAIRS = [(None, 10e3), (47e3, 10e3), (22e3, 10e3), (10e3, 10e3), (10e3, 22e3), (10e3, 47e3), (10e3, 100e3), (10e3, None)]


def p4_numbers():
    r = {}
    a = r["a"] = p4_fol()
    lo, hi = _rng_div(10e3, 10e3)
    print(f"[03 page4] 两节 9 V，不接负载：分压点 ① {a['src']:.3f} V，跟随器输出 ③ {a['out']:.4f} V，③−① {a['d'] * 1e3:+.2f} mV；5% 电阻时 ① {lo:.2f}～{hi:.2f} V")
    assert abs(a["src"] - 4.5) < 0.005 and abs(a["d"]) < 3e-3 and (round(lo, 2), round(hi, 2)) == (4.28, 4.72)
    x = r["f1k"] = p4_fol(rl=1e3)
    print(f"[03 page4] 1 kΩ 接跟随器输出：① {x['src']:.3f} V，③ {x['out']:.4f} V，负载电流 {x['out'] / 1e3 * 1e3:.2f} mA")
    assert abs(x["src"] - 4.5) < 0.005 and abs(x["out"] - 4.5) < 0.005
    for rl in (1e3, 10e3):
        x = r[("d", rl)] = p4_fol(rl=rl, at="src")
        lo, hi = _rng_div(10e3, 10e3, rl)
        print(f"[03 page4] {rl / 1e3:g} kΩ 直接接分压点：① {x['src']:.3f} V（5% 范围 {lo:.2f}～{hi:.2f} V），③ {x['out']:.3f} V")
    assert abs(r[("d", 1e3)]["src"] - 0.75) < 0.005 and abs(r[("d", 10e3)]["src"] - 3.0) < 0.005
    assert abs(r[("d", 1e3)]["out"] - r[("d", 1e3)]["src"]) < 3e-3
    x = r["f10k"] = p4_fol(rl=10e3)
    print(f"[03 page4] 10 kΩ 接跟随器输出：③ {x['out']:.3f} V")
    assert abs(x["out"] - 4.5) < 0.005
    x = r["s1k"] = p4_fol(rl=1e3, mode="single")
    y = r["s0"] = p4_fol(mode="single")
    print(f"[03 page4] 一节 9 V（M = 电池负极）：不接负载 ① {y['src']:.3f} V、③ {y['out']:.3f} V；1 kΩ 接 ③：③ {x['out']:.3f} V")
    assert abs(x["out"] - 4.5) < 0.005 and abs(y["out"] - 4.5) < 0.005
    fam = []
    for rd1, rd2 in P4_PAIRS:
        x = r[("p", rd1, rd2)] = p4_fol(rd1, rd2, mode="single")
        fam.append((x["src"], x["out"]))
        n1 = "拔掉" if rd1 is None else f"{rd1 / 1e3:g}k"
        n2 = "拔掉" if rd2 is None else f"{rd2 / 1e3:g}k"
        print(f"[03 page4] 一节 9 V，Rd1 {n1}、Rd2 {n2}：① {x['src']:.3f} V，③ {x['out']:.3f} V，③−① {x['d']:+.3f} V")
    p = lambda a_, b_: r[("p", a_, b_)]
    assert abs(p(10e3, 47e3)["out"] - p(10e3, 47e3)["src"]) < 0.01           # 7.42 V 还跟得上
    assert 7.3 < p(10e3, 100e3)["out"] < 7.6 and p(10e3, 100e3)["src"] > 8.1  # 8.18 V 已进禁区，输出停在约 7.5 V
    assert 7.3 < p(10e3, None)["out"] < 7.6 and 0 < p(None, 10e3)["out"] < 0.05
    fam_l = {"src": [], "out": []}
    for rl in P4_LOADS:
        fam_l["src"].append(p4_fol(rl=rl, at="src")["src"])
        fam_l["out"].append(p4_fol(rl=rl)["out"])
    print("[03 page4] 负载扫描（两节 9 V）：" + "；".join(f"{rl / 1e3:g}k 直接 {s:.2f} V / 经跟随器 {o:.3f} V"
                                             for rl, s, o in zip(P4_LOADS, fam_l["src"], fam_l["out"])))
    return r, fam, fam_l


# ---------------- 图 03-p4-1：面包板接线（两节 9 V 与一节 9 V 共用一块板） ----------------
def p4_1_breadboard():
    rails = {"T1": ("V+ = +9 V", BB_WIRE["pos"]), "T2": ("M（地）", BB_WIRE["gnd"]),
             "B1": ("V−（两节：−9 V；一节：= M）", BB_WIRE["neg"]), "B2": ("M（地）", BB_WIRE["gnd"])}
    fig, ax = bb_board(30, rails, figsize=(10.6, 6.6))
    bb_wire(ax, "T2-1", "B2-1", "gnd", via=[(-0.4, 10.8), (-0.4, -3.6)])
    # 分压器：Rd1 接 V+，Rd2 接 M，分压点在第 10 列
    bb_wire(ax, "T1-6", "a6", "pos")
    bb_res(ax, "b6", "b10", "Rd1 10k（47k / 拔掉）")
    bb_res(ax, "c10", "c12", "Rd2 10k（47k/100k/拔掉）", dy=-0.55)
    bb_wire(ax, "a12", "T2-12", "gnd")
    bb_wire(ax, "e10", "f10", "sig")                        # 跨过中间槽
    bb_wire(ax, "g10", "g16", "sig")                        # 分压点 → 3 脚
    # LM358：1～4 脚 f14～f17，8～5 脚 e14～e17
    bb_dip8(ax, 14)
    bb_wire(ax, "a14", "T1-14", "pos")                      # 8 脚 V+
    bb_wire(ax, "c15", "c16", "fb")                         # 另一半：7 脚接 6 脚
    bb_wire(ax, "a17", "T2-17", "gnd")                      # 另一半：5 脚接 M
    bb_wire(ax, "j17", "B1-17", "neg")                      # 4 脚 V−
    bb_wire(ax, "h14", "h15", "fb")                         # 跟随器：1 脚（输出）接 2 脚（反相端）
    # 负载 RL：h22–h25，右端接 M；左端用负载线接到 ③（j14）或 ①（j10）
    bb_res(ax, "h22", "h25", "RL 1k（10k）")
    bb_wire(ax, "j25", "B2-25", "gnd")
    bb_wire(ax, "j14", "j22", "sig", via=[(14.0, -1.45), (22.0, -1.45)])
    _bb_label(ax, 18.0, -0.95, "负载线：插 j14 = 经跟随器；改插 j10 = 直接接分压点")
    # 单电源才插：M 轨与 V− 轨短接
    ax.add_patch(_BbRect((27.4, -4.25), 2.2, 1.2, fc="0.86", ec="0.45", ls="--", lw=0.9, zorder=0.5))
    bb_wire(ax, "B2-28", "B1-28", "gnd")
    _bb_label(ax, 26.5, -5.85, "灰框（右下角黑线）：只在一节 9 V 时插")
    ax.set_ylim(-6.3, 14.2)
    ax.text(0.2, 13.55, "两节 9 V：A 的 + 接 V+ 轨；A 的 − 与 B 的 + 拧在一起接 M 轨；B 的 − 接 V− 轨（灰框不插）",
            ha="left", va="center", fontsize=8)
    ax.text(0.2, 12.85, "一节 9 V：+ 接 V+ 轨，− 接 V− 轨，再插灰框里的黑线把 M 轨并到 V− 轨（M 就是电池负极 = 0 V）",
            ha="left", va="center", fontsize=8)
    bb_probe(ax, "h10", "①", dx=-0.6, dy=0.9)
    bb_probe(ax, "i14", "③", dx=-0.75, dy=0.6)
    bb_legend(ax, [("pos", "红：V+"), ("neg", "红紫：V−"), ("gnd", "黑：M"), ("sig", "蓝：信号/负载线"), ("fb", "蓝绿：反馈/短接")],
              x=0.6, y=-5.0)
    print("[图 03-p4-1] LM358 跟随器：1～4 脚 f14～f17、8～5 脚 e14～e17；8 脚→V+，4 脚→V−；另一半 7、6 脚短接、5 脚→M；"
          "a6 接 V+，Rd1 b6–b10，Rd2 c10–c12、a12 接 M；e10→f10、g10→g16 把分压点送到 3 脚；h14→h15 输出接反相端；"
          "RL h22–h25、j25→M，负载线 j14→j22（改插 j10 即直接接）；一节 9 V 时 M 轨与 V− 轨短接；测点① 第 10 列、③ 第 14 列")
    fs.save(fig, N, "03_p4_1_breadboard.png")


# ---------------- 图 03-p4-2：没有示波器时逐点测（左：负载扫描；右：一节 9 V 的输入禁区） ----------------
def p4_2_points(fam, fam_l):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.4))
    x = np.array(P4_LOADS) / 1e3
    a1.semilogx(x, fam_l["out"], color=fs.C["vout"], marker="o", ms=5, lw=1.5, label="经跟随器（③）")
    a1.semilogx(x, fam_l["src"], color=fs.C["third"], marker="s", ms=5, lw=1.3, ls="-.", label="直接接分压点（①）")
    a1.axhline(4.5, **fs.LS["good"], label="空载 4.5 V")
    a1.set_ylim(0, 5.2)
    fs.axlabels(a1, "负载 RL", "kΩ", "负载上的电压（对 M）", "V")
    a1.legend(loc="lower right", fontsize=8.5)
    a1.set_title("两节 9 V：换不同负载", fontsize=10)
    vi = np.array([p[0] for p in fam]); vo = np.array([p[1] for p in fam])
    a2.plot([0, 9.2], [0, 9.2], **fs.LS["good"], label="理想 输出 = 输入")
    a2.plot(vi, vo, color=fs.C["vout"], marker="o", ms=5, lw=1.5, label="实际（③ 对 ①）")
    a2.axvspan(7.5, 9.3, color="0.88", zorder=0)
    a2.text(8.35, 2.0, "禁区\n约 7.5 V 以上", ha="center", fontsize=9)
    a2.annotate(f"停在 {vo.max():.2f} V", (vi.max(), vo.max()), (5.0, 8.6), fontsize=9,
                arrowprops=dict(arrowstyle="-", color="0.4", lw=0.7))
    a2.annotate(f"最低 {vo.min():.3f} V", (vi.min(), vo.min()), (1.2, 0.6), fontsize=9,
                arrowprops=dict(arrowstyle="-", color="0.4", lw=0.7))
    a2.set_xlim(-0.2, 9.3); a2.set_ylim(-0.2, 9.3)
    fs.axlabels(a2, "输入 ①（对电池负极）", "V", "输出 ③", "V")
    a2.legend(loc="upper left", fontsize=8.5)
    a2.set_title("一节 9 V：换分压电阻", fontsize=10)
    print(f"[数值] 负载 1k：直接 {fam_l['src'][0]:.2f} V、经跟随器 {fam_l['out'][0]:.3f} V；单 9 V 输出 {vo.min():.3f}～{vo.max():.2f} V")
    assert 7.3 < vo.max() < 7.6 and 0 < vo.min() < 0.05 and min(fam_l["out"]) > 4.49
    fs.save(fig, N, "03_p4_2_points.png")


if __name__ == "__main__":
    _r, _fam, _fam_l = p4_numbers()
    p4_1_breadboard(); p4_2_points(_fam, _fam_l)
