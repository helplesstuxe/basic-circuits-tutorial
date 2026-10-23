"""16 振荡器：全部配图（图 16-p2-3 由 code/16_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/16_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "16"

def relax(d):
    d += (op := elm.Opamp(leads=True, flip=True).right())
    P = (op.out.x + 0.8, 0)
    d += elm.Line().endpoints(op.out, P); d += elm.Dot().at(P)
    d += elm.Line().right().at(P).length(0.8); d += elm.Dot(open=True).label("$V_o$", "right")
    # + 端：三个电阻
    B = (-1.6, op.in2.y); J = (-0.5, op.in2.y)
    d += elm.Line().endpoints(op.in2, B); d += elm.Dot().at(B); d += elm.Dot().at(J)
    d += elm.Resistor().up().at(B).length(2.0).label("$R_a$ 10 kΩ", "top")
    d += elm.Vdd().label("+5 V")
    d += elm.Line().endpoints(B, (-3.6, op.in2.y))
    d += elm.Resistor().down().length(2.0).label("$R_b$ 10 kΩ", "top"); d += elm.Ground()
    d += elm.Line().up().at(P).toy(2.0)
    d += elm.Resistor().left().tox(J[0]).label("$R_c$ 10 kΩ")
    d += elm.Line().down().toy(op.in2.y)
    # − 端：R 和 C
    A = (-1.3, op.in1.y); K = (-0.4, op.in1.y)
    d += elm.Line().endpoints(op.in1, A); d += elm.Dot().at(K)
    d += elm.Capacitor().down().at(A).length(1.8).label("$C$ 100 nF", "top"); d += elm.Ground()
    d += elm.Dot().at(A).label("$V_C$", "left")
    d += elm.Line().down().at(P).toy(-2.0)
    d += elm.Resistor().left().tox(K[0]).label("$R$ 10 kΩ", "bottom")
    d += elm.Line().up().toy(op.in1.y)
    return op

def wien(d, rf="$R_f$ 22 kΩ"):
    d += (op := elm.Opamp(leads=True, flip=True).right())
    P = (op.out.x + 0.8, 0)
    d += elm.Line().endpoints(op.out, P); d += elm.Dot().at(P)
    d += elm.Line().right().at(P).length(0.8); d += elm.Dot(open=True).label("$V_o$", "right")
    y2 = op.in2.y
    B = (-1.6, y2); J = (-0.6, y2); Cx = -4.0
    d += elm.Line().endpoints(op.in2, (Cx, y2)); d += elm.Dot().at(B); d += elm.Dot().at(J)
    d += elm.Resistor().down().at(B).length(1.6).label("$R$ 10 kΩ", "top"); d += elm.Ground()
    d += elm.Capacitor().down().at((Cx, y2)).length(1.6).label("$C$ 10 nF", "top"); d += elm.Ground()
    d += elm.Line().up().at(J).toy(2.0)
    d += elm.Capacitor().right().length(1.8).label("$C$ 10 nF")
    d += elm.Resistor().right().tox(P[0]).label("$R$ 10 kΩ")
    d += elm.Line().down().toy(0)
    y1 = op.in1.y; K = (-0.4, -2.4)
    d += elm.Line().endpoints(op.in1, (-0.4, y1)); d += elm.Line().endpoints((-0.4, y1), K); d += elm.Dot().at(K)
    d += elm.Resistor().right().at(K).tox(P[0]).label(rf, "bottom")
    d += elm.Line().up().toy(0)
    d += elm.Resistor().left().at(K).length(2.0).label("$R_g$ 10 kΩ", "bottom"); d += elm.Ground()
    return op


def relax_sim(vh, vl, R=10e3, C=100e-9, vcc=5.0, T=6e-3):
    """弛张振荡器：输出只有 vh、vl 两种；同相端门限 = (vcc + 0 + Vo)/3（三个等值电阻）。"""
    dt = R * C / 2000
    t = np.arange(0, T, dt)
    vc, high = 0.0, True
    VC, VO, edges = np.empty_like(t), np.empty_like(t), []
    for k in range(len(t)):
        vo = vh if high else vl
        th = (vcc + vo) / 3                           # 当前门限
        if high and vc >= th:                         # 电容涨到上门限 → 输出翻低
            high = False; edges.append(t[k])
        elif not high and vc <= th:                   # 电容降到下门限 → 输出翻高
            high = True; edges.append(t[k])
        vo = vh if high else vl
        vc += (vo - vc) / (R * C) * dt                # 电容经 R 向输出电压充放电
        VC[k], VO[k] = vc, vo
    e = np.array(edges[1:])                           # 去掉第一次（从 0 V 起步）
    t_high = np.mean(e[1::2] - e[0::2][:len(e[1::2])])   # 低→高 到 高→低：这里 e[0] 是翻高时刻
    period = np.mean(np.diff(e[0::2]))
    return t, VC, VO, period, t_high


# ---------- 图 16-p1-1 弛张方波振荡器 ----------
with drawing() as d:
    relax(d)
save_schem(d, N, "16_p1_1_relaxation.png")

# ---------- 图 16-p1-2 电容电压与输出方波 ----------
t, VC, VO, T, th = relax_sim(5.0, 0.0)
vH, vL = 10 / 3, 5 / 3
print(f"理想输出 0/5 V：门限 {vL:.2f} V 与 {vH:.2f} V；周期 {T*1e3:.2f} ms（{1/T:.0f} Hz），高电平占 {th/T*100:.0f}%")
assert abs(T - 2 * np.log(2) * 10e3 * 100e-9) < 0.02e-3   # T = 2 ln2 · RC ≈ 1.39RC
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, VO, **fs.LS["vout"], label="$V_o$ 输出方波")
ax.plot(t * 1e3, VC, **fs.LS["third"], label="$V_C$ 电容电压")
fs.ref_h(ax, vH, f"上门限 {vH:.2f} V", x=0.99)
fs.ref_h(ax, vL, f"下门限 {vL:.2f} V", x=0.99)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-0.3, 6.3); ax.set_xlim(-0.2, 7.4)
ax.legend(loc="upper left", fontsize=8, ncol=2)
fs.save(fig, N, "16_p1_2_relax_wave.png")

# ---------- 图 16-p2-1 文氏桥振荡器 ----------
with drawing() as d:
    wien(d)
save_schem(d, N, "16_p2_1_wien.png")

# ---------- 图 16-p2-2 文氏桥网络的选频 ----------
R, C = 10e3, 10e-9
f0 = 1 / (2 * np.pi * R * C)
f = np.logspace(2, np.log10(2e4), 600)
beta = 1 / np.sqrt(9 + (f / f0 - f0 / f) ** 2)
print(f"文氏桥 f0 = {f0:.0f} Hz，网络在 f0 处 V+/Vo = {1/3:.3f}；在 f0/10 和 10f0 处约 {1/np.sqrt(9 + 9.9**2):.3f}")
assert abs(beta.max() - 1 / 3) < 1e-4
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.semilogx(f, beta, **fs.LS["fb"], label="文氏桥网络 $V_+/V_o$")
fs.mark(ax, f0, 1 / 3, fmt="{:.3f}", dx=8, dy=4)
fs.ref_v(ax, f0, f"{f0:.0f} Hz", y=0.12)
fs.axlabels(ax, "频率", "Hz", "同相端/输出 幅度", None)
ax.set_xticks([100, 1e3, 1e4]); ax.set_xticklabels(["100", "1 k", "10 k"])
ax.set_ylim(0, 0.4); ax.legend(loc="upper left", fontsize=8)
fs.save(fig, N, "16_p2_2_wien_select.png")


# ---------- 文氏桥数值仿真（与 code/16_sim.py 相同的模型）----------
Rg, VMAX, dt = 10e3, 4.0, 0.2e-6
tw = np.arange(0, 20e-3, dt)
def run(amp):
    vc, vx = 0.0, 0.01
    out = np.empty_like(tw)
    for k in range(len(tw)):
        vo = amp(vx); i = (vo - vx - vc) / R
        vc += i / C * dt; vx += (i - vx / R) / C * dt; out[k] = vo
    return out
clip = run(lambda v: np.clip(3.2 * v, -VMAX, VMAX))
diode = run(lambda v: np.clip(v + v / Rg * 12e3 + 0.6 * np.tanh(v / Rg * 10e3 / 0.6), -VMAX, VMAX))

# ---------- 图 16-p2-4 正弦变方波：接一个比较器 ----------
w = tw > 17e-3
ts, vs = tw[w], diode[w]
sq = np.where(vs > 0, 4.0, -4.0)                      # 比较器：同相端接正弦，反相端接 0 V，输出 ±4 V
print(f"整形：正弦峰值 {vs.max():.2f} V → 比较器（门限 0 V）输出 ±4.0 V 方波")
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot((ts - ts[0]) * 1e3, vs, **fs.LS["vin"], label="$V_i$ 文氏桥正弦（送进比较器）")
ax.plot((ts - ts[0]) * 1e3, sq, **fs.LS["vout"], label="$V_o$ 比较器输出方波")
fs.ref_h(ax, 0, "门限 0 V", x=0.99)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-5, 6.2)
ax.legend(loc="upper left", fontsize=8, ncol=2)
fs.save(fig, N, "16_p2_4_shaping.png")


# ---------- 图 16-p3-1 削顶与稳幅的波形对比 ----------
def distortion(y, tt):
    """在 1400～1800 Hz 里逐个试频率，用最小二乘拟合基波正弦，返回（拟合曲线，偏离正弦的比例，频率）。"""
    best = None
    for fz in np.arange(1400, 1801, 1.0):
        M = np.column_stack([np.sin(2 * np.pi * fz * tt), np.cos(2 * np.pi * fz * tt), np.ones_like(tt)])
        coef, *_ = np.linalg.lstsq(M, y, rcond=None)
        fit = M @ coef
        r = np.sqrt(np.mean((y - fit) ** 2) / np.mean((fit - coef[2]) ** 2))
        if best is None or r < best[1]:
            best = (fit, r, fz)
    return best
w = tw > 15e-3
tt = tw[w]
fit_c, d_c, f_c = distortion(clip[w], tt)
fit_d, d_d, f_d = distortion(diode[w], tt)
print(f"偏离正弦的比例：削顶 {d_c*100:.1f}%（{f_c:.0f} Hz），二极管稳幅 {d_d*100:.1f}%（{f_d:.0f} Hz）")
assert d_c > 2.5 * d_d
k = tt < 15e-3 + 1.5e-3
fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"], sharey=True)
x = (tt[k] - tt[0]) * 1e3
axs[0].plot(x, fit_c[k], **fs.LS["good"], label="理想正弦")
axs[0].plot(x, clip[w][k], **fs.LS["bad"], label="增益 3.2 无稳幅")
axs[0].set_title(f"削顶：偏离正弦 {d_c*100:.1f}%", fontsize=9)
axs[1].plot(x, fit_d[k], **fs.LS["good"], label="理想正弦")
axs[1].plot(x, diode[w][k], **fs.LS["vout"], label="二极管稳幅")
axs[1].set_title(f"稳幅：偏离正弦 {d_d*100:.1f}%", fontsize=9)
for ax in axs:
    fs.axlabels(ax, "时间", "ms"); ax.legend(loc="lower left", fontsize=7)
axs[0].set_ylabel("$V_o$ / V"); axs[0].set_ylim(-6.5, 5.5)
fs.save(fig, N, "16_p3_1_distortion.png")

# ---------- 图 16-p3-2 运放输出不到电源轨：占空比变歪 ----------
fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"], sharey=True)
for ax, (vh, vl, name) in zip(axs, [(5.0, 0.0, "理想：输出 0～5 V"), (3.5, 0.1, "LM358B：输出 0.1～3.5 V")]):
    t, VC, VO, T, th = relax_sim(vh, vl)
    up, dn = (5 + vh) / 3, (5 + vl) / 3
    print(f"{name}：门限 {dn:.2f}/{up:.2f} V，周期 {T*1e3:.2f} ms，高电平占 {th/T*100:.0f}%")
    ax.plot(t * 1e3, VO, **(fs.LS["vout"] if vh == 5 else fs.LS["bad"]), label="$V_o$")
    ax.plot(t * 1e3, VC, **fs.LS["third"], label="$V_C$")
    fs.ref_h(ax, up); fs.ref_h(ax, dn)
    ax.set_title(f"{name}，高电平占 {th/T*100:.0f}%", fontsize=9)
    fs.axlabels(ax, "时间", "ms"); ax.legend(loc="upper right", fontsize=7, ncol=2)
    if vh == 3.5:
        assert th / T > 0.6
axs[0].set_ylabel("电压 / V"); axs[0].set_ylim(-0.3, 6.5)
fs.save(fig, N, "16_p3_2_lm358_duty.png")

# ---------- 正文里的其余数字（只打印 + 断言） ----------
# 文氏桥在 f0 处：容抗 = R，串联支路与并联支路的"总阻碍"之比 2:1，相位相同，所以分到 1/3
Rw, Cw = 10e3, 10e-9
f0w = 1 / (2 * np.pi * Rw * Cw)
Xc = 1 / (2 * np.pi * f0w * Cw)
Zs = Rw - 1j * Xc                                    # 串联 R + C
Zp = 1 / (1 / Rw + 1j * 2 * np.pi * f0w * Cw)        # 并联 R ∥ C
print(f"f0 = {f0w:.0f} Hz：容抗 {Xc/1e3:.1f} kΩ；串联 |Z| = {abs(Zs)/Rw:.3f} R，并联 |Z| = {abs(Zp)/Rw:.3f} R，之比 {abs(Zs)/abs(Zp):.2f}")
print(f"两支路相位 {np.degrees(np.angle(Zs)):.0f}° 和 {np.degrees(np.angle(Zp)):.0f}°，分压比 {abs(Zp/(Zs+Zp)):.4f}")
assert abs(abs(Zs) / abs(Zp) - 2) < 1e-9 and abs(abs(Zp / (Zs + Zp)) - 1 / 3) < 1e-9


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

# ---------- 图 16-p4-1：弛张振荡器的面包板接线（LM358，5 V 单电源） ----------
bb = Breadboard(30, "弛张振荡器面包板俯视图（LM358，5 V 单电源）", rails=("+5 V", "GND", "GND", "+5 V"))
bb.chip(14, "LM358", names={1: "OUT", 2: "IN−", 3: "IN+", 4: "GND", 8: "V+"})
bb.wire("a14", "T+14", "pos")                      # 第 8 脚 → +5 V
bb.wire("j17", "B-17", "gnd")                      # 第 4 脚 → 地
bb.wire("a17", "T-17", "gnd")                      # B 路同相端接地
bb.wire("c15", "c16", "fb")                        # B 路接成跟随器
bb.wire("g14", "g11", "out")                       # 输出引到第 11 列
bb.part("h11", "h15", "R 10 kΩ", "R", lab_side=1)  # 定时电阻：输出 → 反相端
bb.part("j15", "B-15", "C 100 nF", "C", lab_side=-1)  # 定时电容：反相端 → 地
bb.part("i11", "i16", "Rc 10 kΩ", "R", lab_side=-1)   # 正反馈：输出 → 同相端
bb.part("h16", "h20", "Ra 10 kΩ", "R", lab_side=1)
bb.wire("j20", "B+20", "pos")
bb.wire("g16", "g22", "fb")
bb.part("h22", "h26", "Rb 10 kΩ", "R", lab_side=1)
bb.wire("j26", "B-26", "gnd")
bb.part("j11", "j7", "10 µF", "E", lab_side=-1)    # 隔直电容：+ 脚朝输出（输出平均约 2.4 V）
bb.part("i7", "i3", "R 1 kΩ", "R", lab_side=-1)
bb.wire("T-29", "B-29", "gnd")
bb.wire("T+30", "B+30", "pos")
bb.module(-3.2, 9.4, 4.0, 1.4, "5 V 电源模块")
bb.wire((0.8, 10.1), "T+1", "pos")
bb.wire((0.2, 9.4), "T-3", "gnd")
bb.module(-3.2, -4.4, 3.0, 1.6, "耳机\n3.5 mm 转接板")
bb.wire((-0.2, -3.6), "j3", "out")
bb.wire((-1.5, -4.4), "B-1", "gnd", via=[(-1.5, -6.7)])
bb.note(8.5, -0.3, "测输出：f11", va="center")
bb.note(20.0, -0.3, "测电容：i15　测同相端：j16", va="center")
bb.note(0.5, -9.6, "慢速版：R 10 kΩ 换 75 kΩ，C 换 10 µF 电解（+ 脚插 j15）", ha="left")
bb.legend()
bb.save(N, "16_p4_1_breadboard.png")

# ---------- 门限、周期（用 review/spice/16.md 的 LM358B 高低电平） ----------
VCC, VOH, VOL = 5.0, 3.79, 0.63
def thr(vo, ra=10e3, rb=10e3, rc=10e3, vcc=VCC):
    return (vcc / ra + vo / rc) / (1 / ra + 1 / rb + 1 / rc)
VTH, VTL = thr(VOH), thr(VOL)
k_up = np.log((VOH - VTL) / (VOH - VTH))           # 充电半周 / RC
k_dn = np.log((VTH - VOL) / (VTL - VOL))           # 放电半周 / RC
k = k_up + k_dn
print(f"[数值] 门限 {VTL:.2f} V / {VTH:.2f} V；周期 {k:.3f}·RC，占空比 {k_up/k*100:.0f}%")
print(f"[数值] 10 kΩ × 100 nF：{1/(k*1e-3):.0f} Hz（未计压摆率；SPICE 670 Hz，理想 721 Hz）")
T_SLOW = k * 75e3 * 10e-6
print(f"[数值] 慢速版 75 kΩ × 10 µF：周期 {T_SLOW:.2f} s，高 {k_up*0.75:.2f} s、低 {k_dn*0.75:.2f} s")
assert abs(VTH - 2.93) < 0.01 and abs(VTL - 1.88) < 0.01 and abs(k_up / k - 0.57) < 0.01
assert abs(1 / (k * 1e-3) - 708) < 2

# ---------- 图 16-p4-2：慢速版的读数和拍频 ----------
RC = 0.75
ts = np.linspace(0, 4, 4001)
vc, vo = np.empty_like(ts), np.empty_like(ts)
c, o = VTL, VOH
for i, t_ in enumerate(ts):
    vc[i], vo[i] = c, o
    c += (o - c) / RC * (ts[1] - ts[0])
    if o == VOH and c >= VTH: o = VOL
    elif o == VOL and c <= VTL: o = VOH
F_OSC, F_PHONE = 670.0, 660.0
tb = np.linspace(0, 0.3, 30001)
mix = np.sin(2 * np.pi * F_OSC * tb) + np.sin(2 * np.pi * F_PHONE * tb)
env = 2 * np.abs(np.cos(np.pi * (F_OSC - F_PHONE) * tb))
print(f"[数值] 拍频：{F_OSC:.0f} Hz 与 {F_PHONE:.0f} Hz 一起响，每秒忽大忽小 {F_OSC-F_PHONE:.0f} 次")
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a1.plot(ts, vo, label="输出（1 脚）", **fs.LS["vout"])
a1.plot(ts, vc, label="电容（2 脚）", **fs.LS["vin"])
fs.ref_h(a1, VTH, f"{VTH:.2f} V"); fs.ref_h(a1, VTL, f"{VTL:.2f} V")
a1.set_ylim(0, 4.6); a1.legend(loc="upper right", fontsize=8, ncol=2)
fs.axlabels(a1, "时间", "s", "电压", "V")
a1.set_title(f"慢速版：约 {T_SLOW:.2f} s 一个来回，万用表跟得上", fontsize=10)
a2.plot(tb * 1e3, mix, color=fs.C["vin"], lw=0.5, label="两个音叠加")
a2.plot(tb * 1e3, env, label="响度包络", **fs.LS["vout"])
a2.set_ylim(-2.4, 3.0); a2.legend(loc="upper right", fontsize=8, ncol=2)
fs.axlabels(a2, "时间", "ms", "声音（相对）", None)
a2.set_title("拍频：670 Hz 与 660 Hz 一起响，每秒忽大忽小 10 次", fontsize=10)
fs.save(fig, N, "16_p4_2_no_scope.png")


# ======================= 补充原理图（图 16-p2-5 起） =======================
ACC = fs.C["bad"]


def wien_at(d, ox=0.0, oy=0.0, fb="plain", bias=False, out_label="$V_o$", out_dot=True):
    """文氏桥（与 wien() 同尺寸），整体平移 (ox, oy)。fb="diode" 时 R_f = 12 kΩ + (10 kΩ ∥ 反向并联二极管)；
    bias=True 时把 R_g、并联 RC 的「地」改接 2.5 V 偏置点。新增部分用朱红色。"""
    p = lambda x, y: (x + ox, y + oy)
    d += (op := elm.Opamp(leads=True, flip=True).right().anchor("in1").at(p(0, -0.625)))
    P = p(op.out.x - ox + 0.8, 0)
    d += elm.Line().endpoints(op.out, P); d += elm.Dot().at(P)
    if out_dot:
        d += elm.Line().right().at(P).length(0.8); d += elm.Dot(open=True).label(out_label, "right")
    y2 = 0.625; B = p(-1.6, y2); J = p(-0.6, y2); Cx = -4.0
    d += elm.Line().endpoints(op.in2, p(Cx, y2)); d += elm.Dot().at(B); d += elm.Dot().at(J)
    d += elm.Resistor().down().at(B).length(1.6).label("$R$ 10 kΩ", "top")
    if not bias:
        d += elm.Ground()
    d += elm.Capacitor().down().at(p(Cx, y2)).length(1.6).label("$C$ 10 nF", "top")
    if not bias:
        d += elm.Ground()
    d += elm.Line().up().at(J).toy(oy + 2.0)
    d += elm.Capacitor().right().length(1.8).label("$C$ 10 nF")
    d += elm.Resistor().right().tox(P[0]).label("$R$ 10 kΩ")
    d += elm.Line().down().toy(oy)
    K = p(-0.4, -2.4)
    d += elm.Line().endpoints(op.in1, p(-0.4, -0.625)); d += elm.Line().endpoints(p(-0.4, -0.625), K); d += elm.Dot().at(K)
    if fb == "plain":
        d += elm.Resistor().right().at(K).tox(P[0]).label("$R_f$ 22 kΩ", "bottom")
        d += elm.Line().up().toy(oy)
    else:
        d += elm.Resistor().right().at(K).length(1.5).label("12 kΩ", "bottom").color(ACC)
        d += (n1 := elm.Dot().color(ACC))
        d += elm.Resistor().right().length(2.2).label("10 kΩ", "top").color(ACC)
        d += (n2 := elm.Dot().color(ACC))
        d += elm.Line().right().tox(P[0]).color(ACC)
        d += elm.Line().up().toy(oy).color(ACC)
        a1 = (n1.center[0], n1.center[1] - 0.9); b1 = (n2.center[0], n2.center[1] - 0.9)
        a2 = (n1.center[0], n1.center[1] - 1.8); b2 = (n2.center[0], n2.center[1] - 1.8)
        d += elm.Line().endpoints(n1.center, a2).color(ACC); d += elm.Line().endpoints(n2.center, b2).color(ACC)
        d += elm.Dot().at(a1).color(ACC); d += elm.Dot().at(b1).color(ACC)
        d += elm.Diode().right().at(a1).to(b1).color(ACC).label("$D_1$", "top")
        d += elm.Diode().left().at(b2).to(a2).color(ACC).label("$D_2$", "bottom")
        d += elm.Label().at(p(1.9, -5.3)).label("$R_f$ = 12 kΩ + （10 kΩ ∥ $D_1$、$D_2$）", color=ACC)
    d += elm.Resistor().left().at(K).length(2.0).label("$R_g$ 10 kΩ", "bottom")
    if not bias:
        d += elm.Ground()
    else:
        yb = -3.1
        d += elm.Line().down().toy(oy + yb).color(ACC)
        d += elm.Line().endpoints(p(-1.6, y2 - 1.6), p(Cx, y2 - 1.6)).color(ACC)
        d += elm.Dot().at(p(Cx, y2 - 1.6)).color(ACC)
        d += elm.Line().endpoints(p(Cx, y2 - 1.6), p(Cx, yb)).color(ACC)
        d += elm.Line().endpoints(p(Cx - 0.6, yb), p(-2.4, yb)).color(ACC)
        d += elm.Dot().at(p(Cx, yb)).color(ACC)
        d += elm.Dot(open=True).at(p(Cx - 0.6, yb)).color(ACC).label("2.5 V 偏置点", "left", color=ACC)
    return op, P


# ---------- 图 16-p2-5 双电源与单电源（2.5 V 偏置点）两种接法 ----------
with drawing() as d:
    wien_at(d, 0, 0)
    d += elm.Label().at((-1.0, 3.6)).label("（a）±5 V 双电源：下端接地")
    wien_at(d, 11.5, 0, bias=True)
    d += elm.Label().at((10.5, 3.6)).label("（b）只有 5 V 单电源：下端改接 2.5 V 偏置点")
save_schem(d, N, "16_p2_5_supply_variants.png")


# ---------- 图 16-p2-6 二极管稳幅的文氏桥 ----------
with drawing() as d:
    wien_at(d, 0, 0, fb="diode")
save_schem(d, N, "16_p2_6_diode_agc.png")

# ---------- 图 16-p2-7 文氏桥 + 过零比较器 ----------
with drawing() as d:
    op1, P = wien_at(d, 0, 0, fb="diode", out_dot=False)
    d += elm.Line().right().at(P).length(1.2)
    d += (vi := elm.Dot().label("$V_i$（正弦）", "top"))
    d += (cmp_ := elm.Opamp(leads=True, flip=True).right().anchor("in2").at((P[0] + 2.4, 0)).color(ACC))
    d += elm.Line().endpoints(vi.center, cmp_.in2)
    d += elm.Line().left().at(cmp_.in1).length(0.6).color(ACC)
    d += elm.Line().down().length(0.7).color(ACC); d += elm.Ground().color(ACC)
    d += elm.Label().at((cmp_.in1.x - 1.3, cmp_.in1.y - 0.9)).label("0 V", color=ACC)
    d += elm.Line().right().at(cmp_.out).length(0.8).color(ACC)
    d += elm.Dot(open=True).label("$V_o$（方波）", "right")
    d += elm.Label().at((cmp_.out.x - 1.6, 1.9)).label("比较器（14 节）", color=ACC)
save_schem(d, N, "16_p2_7_comparator.png")


# ---------- 图 16-p3-3 削顶与稳幅：两种 R_f ----------
with drawing() as d:
    wien_at(d, 0, 0)
    d += elm.Label().at((-0.5, 3.6)).label("（a）只用 $R_f$ 22 kΩ，没有稳幅")
    wien_at(d, 11.5, 0, fb="diode")
    d += elm.Label().at((11.0, 3.6)).label("（b）二极管稳幅")
save_schem(d, N, "16_p3_3_stab_variants.png")


def relax_led(d):
    """直觉篇弛张振荡器换成 75 kΩ / 10 µF，输出端串限流电阻和 LED 到地（新增部分朱红色）。"""
    d += (op := elm.Opamp(leads=True, flip=True).right())
    P = (op.out.x + 0.8, 0)
    d += elm.Line().endpoints(op.out, P); d += elm.Dot().at(P)
    d += elm.Line().right().at(P).length(1.2); d += (vo := elm.Dot().label("$V_o$", "top"))
    d += elm.Resistor().down().at(vo.center).length(1.8).label("限流电阻", "bottom").color(ACC)
    d += elm.LED().down().length(1.6).label("LED", "bottom").color(ACC)
    d += elm.Ground().color(ACC)
    B = (-1.6, op.in2.y); J = (-0.5, op.in2.y)
    d += elm.Line().endpoints(op.in2, B); d += elm.Dot().at(B); d += elm.Dot().at(J)
    d += elm.Resistor().up().at(B).length(2.0).label("$R_a$ 10 kΩ", "top")
    d += elm.Vdd().label("+5 V")
    d += elm.Line().endpoints(B, (-3.6, op.in2.y))
    d += elm.Resistor().down().length(2.0).label("$R_b$ 10 kΩ", "top"); d += elm.Ground()
    d += elm.Line().up().at(P).toy(2.0)
    d += elm.Resistor().left().tox(J[0]).label("$R_c$ 10 kΩ")
    d += elm.Line().down().toy(op.in2.y)
    A = (-1.3, op.in1.y); K = (-0.4, op.in1.y)
    d += elm.Line().endpoints(op.in1, A); d += elm.Dot().at(K)
    d += elm.Capacitor().down().at(A).length(1.8).label("$C$ 10 µF", "top").color(ACC); d += elm.Ground()
    d += elm.Dot().at(A).label("$V_C$", "left")
    d += elm.Line().down().at(P).toy(-2.0)
    d += elm.Resistor().left().tox(K[0]).label("$R$ 75 kΩ", "bottom").color(ACC)
    d += elm.Line().up().toy(op.in1.y)


# ---------- 图 16-p3-4 练习 4：1 Hz LED 闪烁 ----------
T_led = 1.39 * 75e3 * 10e-6
print(f"练习 4：R = 75 kΩ、C = 10 µF，T ≈ {T_led:.2f} s（{1/T_led:.2f} Hz）")
with drawing() as d:
    relax_led(d)
save_schem(d, N, "16_p3_4_led_1hz.png")
