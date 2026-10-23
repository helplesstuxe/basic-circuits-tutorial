"""15 有源滤波：全部配图（图 15-p2-2 由 code/15_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/15_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

N = "15"
R, C = 16e3, 10e-9                                     # 一阶：fc ≈ 995 Hz
R1, R2, C1, C2 = 4.22e3, 18.4e3, 10e-9, 33e-9          # Sallen-Key 巴特沃斯 1 kHz（TI SLOA049 表 10-1）
first = ([1.0], [R * C, 1.0])                          # 一阶低通：1/(sRC + 1)
sk = ([1.0], [R1 * R2 * C1 * C2, C1 * (R1 + R2), 1.0])  # Sallen-Key：1/(s²R1R2C1C2 + sC1(R1+R2) + 1)


def follower_tail(d, node, out_len=1.0):
    """从 node 引线到运放同相端，运放接成跟随器，返回运放。"""
    d += elm.Line().right().at(node).length(1.0)
    d += (op := elm.Opamp(leads=True).right().anchor("in2"))
    d += elm.Line().left().at(op.in1).length(0.4)
    d += elm.Line().up().length(1.2)
    d += elm.Line().right().tox(op.out.x + 0.4)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    d += elm.Line().right().at(op.out).length(out_len)
    d += elm.Dot(open=True).label("$V_o$", "right")
    return op


# ---------- 图 15-p1-1 带高频噪声的信号经过低通 ----------
t = np.linspace(0, 40e-3, 40001)
clean = fs.sine(t, 50, amp=1.0)
noisy = clean + 0.3 * np.sin(2 * np.pi * 10e3 * t)
_, y, _ = signal.lsim(first, noisy, t)
ripple = np.max(np.abs(y[20000:] - signal.lsim(first, clean, t)[1][20000:]))
print(f"输入：50 Hz 1 V 信号 + 10 kHz 0.3 V 噪声；经 fc ≈ 995 Hz 一阶低通后噪声剩约 {ripple:.2f} V")
assert ripple < 0.04
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, noisy, **{**fs.LS["vin"], "lw": 0.8}, label="$V_i$ 输入（带 10 kHz 噪声）")
ax.plot(t * 1e3, y, **fs.LS["vout"], label="$V_o$ 低通输出")
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-1.8, 2.2)
ax.legend(loc="upper right", fontsize=8, ncol=2)
fs.save(fig, N, "15_p1_1_denoise.png")

# ---------- 图 15-p1-2 一阶有源低通 ----------
with drawing() as d:
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R$ 16 kΩ")
    d += (n := elm.Dot())
    d += elm.Capacitor().down().label("$C$ 10 nF", "bottom")
    d += elm.Ground()
    follower_tail(d, n.center)
save_schem(d, N, "15_p1_2_first_order.png")
print(f"一阶低通 fc = 1/(2π × 16 kΩ × 10 nF) = {1 / (2 * np.pi * R * C):.0f} Hz")

# ---------- 图 15-p2-1 Sallen-Key 二阶低通 ----------
with drawing() as d:
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R_1$ 4.22 kΩ")
    d += (a := elm.Dot())
    d += elm.Resistor().right().label("$R_2$ 18.4 kΩ")
    d += (b := elm.Dot())
    d += elm.Capacitor().down().label("$C_1$ 10 nF", "bottom")
    d += elm.Ground()
    op = follower_tail(d, b.center, out_len=2.4)
    d += elm.Line().up().at(a.center).length(3.6)
    d += elm.Capacitor().right().label("$C_2$ 33 nF").tox(op.out.x + 1.4)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
save_schem(d, N, "15_p2_1_sallen_key.png")
f0 = 1 / (2 * np.pi * np.sqrt(R1 * R2 * C1 * C2))
Q = np.sqrt(R1 * R2 * C1 * C2) / (C1 * (R1 + R2))
print(f"Sallen-Key：f0 = {f0:.0f} Hz，Q = {Q:.3f}")
assert abs(Q - 0.707) < 0.01 and abs(f0 - 1000) < 20

# ---------- 图 15-p2-3 一阶有源高通 ----------
with drawing() as d:
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Capacitor().right().label("$C$ 100 nF")
    d += (n := elm.Dot())
    d += elm.Resistor().down().label("$R$ 15.9 kΩ", "bottom")
    d += elm.Ground()
    follower_tail(d, n.center)
save_schem(d, N, "15_p2_3_highpass.png")
print(f"一阶高通 fc = 1/(2π × 15.9 kΩ × 100 nF) = {1 / (2 * np.pi * 15.9e3 * 100e-9):.0f} Hz")

# ---------- 图 15-p3-1 方波经过两种低通 ----------
t = np.linspace(0, 4e-3, 8001)
sq = fs.square(t, 500, amp=0.5, offset=0.5)            # 0～1 V、500 Hz 方波
_, y1, _ = signal.lsim(first, sq, t)
_, y2, _ = signal.lsim(sk, sq, t)
os2 = y2.max() - 1
print(f"500 Hz 方波（0～1 V）：一阶输出最高 {y1.max():.2f} V，二阶最高 {y2.max():.2f} V（过冲 {os2*100:.0f}%）")
assert 0.0 < os2 < 0.06
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, sq, **fs.LS["vin"], label="$V_i$ 方波 500 Hz")
ax.plot(t * 1e3, y1, **fs.LS["third"], label="一阶低通输出")
ax.plot(t * 1e3, y2, **fs.LS["vout"], label="二阶 Sallen-Key 输出")
k = np.argmax(y2)
fs.mark(ax, t[k] * 1e3, y2[k], fmt="{:.2f}", unit=" V", dx=6, dy=4)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-0.1, 1.45)
ax.legend(loc="upper right", fontsize=8, ncol=3)
fs.save(fig, N, "15_p3_1_square.png")

# ---------- 图 15-p3-2 漏了 2π：截止频率低了 6 倍多 ----------
f = np.logspace(1, 5, 600)
R_bad = 1 / (1e3 * C)                                   # 错误：R = 1/(fC) = 100 kΩ
fc_ok, fc_bad = 1 / (2 * np.pi * R * C), 1 / (2 * np.pi * R_bad * C)
h = lambda fx, fc: 20 * np.log10(1 / np.sqrt(1 + (fx / fc) ** 2))
print(f"漏了 2π：R 取成 {R_bad/1e3:.0f} kΩ，实际 fc = {fc_bad:.0f} Hz；1 kHz 处 {h(1e3, fc_bad):.0f} dB（应为 {h(1e3, fc_ok):.0f} dB）")
assert abs(fc_bad - 159) < 1
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.semilogx(f, h(f, fc_ok), **fs.LS["vout"], label="正确：R = 16 kΩ")
ax.semilogx(f, h(f, fc_bad), **fs.LS["bad"], label="漏了 2π：R = 100 kΩ")
fs.ref_v(ax, 1e3, "1 kHz（设计目标）")
fs.ref_v(ax, fc_bad, f"{fc_bad:.0f} Hz", y=0.12)
fs.mark(ax, 1e3, h(1e3, fc_bad), fmt="{:.0f}", unit=" dB", dx=-40, dy=-14)
fs.mark(ax, 1e3, h(1e3, fc_ok), fmt="{:.0f}", unit=" dB", dx=8, dy=-14)
fs.axlabels(ax, "频率", "Hz", "输出/输入 幅度", "dB")
ax.set_xticks([10, 100, 1e3, 1e4, 1e5]); ax.set_xticklabels(["10", "100", "1 k", "10 k", "100 k"])
ax.set_ylim(-60, 8); ax.legend(loc="lower left", fontsize=8)
fs.save(fig, N, "15_p3_2_missing_2pi.png")

# ---------- 参数与调试篇引用的经验数字（无图，只打印并断言） ----------
GBW_LM358 = 1.2e6                                       # LM358B 增益带宽积
need = lambda gain, fc: 100 * gain * fc                 # Microchip ADN003：Sallen-Key 要 GBW ≥ 100 × 倍数 × fc
n1, n2 = need(1, 1e3), need(10, 100e3)
print(f"GBW 经验要求：1 kHz 跟随型 {n1/1e3:.0f} kHz（LM358B {GBW_LM358/1e6:.1f} MHz 够用）；100 kHz × 10 倍 {n2/1e6:.0f} MHz（是 LM358B 的 {n2/GBW_LM358:.0f} 倍）")
assert n1 == 100e3 and n1 <= GBW_LM358 and n2 == 100e6 and round(n2 / GBW_LM358) == 83
drift = 30e-6 * 100                                     # C0G：±30 ppm/°C，温度变 100 °C
print(f"C0G 温度变 100 °C：容量最多变 {drift*100:.1f}%")
assert abs(drift - 0.003) < 1e-12
shift = 1 / np.sqrt(0.85 * 0.85) - 1                    # Sallen-Key：fc ∝ 1/√(C1·C2)，两只 X7R 都 −15%
print(f"两只电容都少 15%：截止频率高出 {shift*100:.1f}%")
assert abs(shift - 0.176) < 0.001



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

# ---------- 图 15-p4-1：一阶有源低通的面包板接线（LM358，±9 V） ----------
bb = Breadboard(30, "一阶有源低通面包板俯视图（LM358 跟随器，±9 V）", rails=("+9 V", "GND", "GND", "−9 V"))
bb.chip(14, "LM358", names={1: "OUT", 2: "IN−", 3: "IN+", 4: "V−", 8: "V+"})
bb.wire("a14", "T+14", "pos")                      # 第 8 脚 → +9 V
bb.wire("j17", "B+17", "neg")                      # 第 4 脚 → −9 V
bb.wire("a17", "T-17", "gnd")                      # 第 5 脚（B 路同相端）→ 地
bb.wire("c15", "c16", "fb")                        # 第 6、7 脚短接：B 路接成跟随器
bb.wire("g14", "g15", "fb")                        # 第 1、2 脚短接：A 路接成跟随器
bb.wire("g16", "g20", "fb")                        # 第 3 脚 → 第 20 列（滤波节点）
bb.part("h20", "h24", "R 16 kΩ", "R", lab_side=1)
bb.part("j20", "B-20", "C 10 nF", "C", lab_side=1)
bb.wire("h14", "h8", "out")                        # 输出 → 第 8 列
bb.part("i8", "i4", "R 1 kΩ（耳机限流）", "R", lab_side=-1)
bb.wire("T-28", "B-28", "gnd")
bb.module(-3.2, 9.4, 4.0, 1.4, "9 V 电池 ×2 串联\n中点 = GND")
bb.wire((1.4, 9.9), "T+1", "pos")
bb.wire((0.8, 9.6), "T-3", "gnd")
bb.wire((-3.2, 10.1), "B+1", "neg", via=[(-3.3, 10.1), (-3.3, -8.6), (1.0, -8.6)])
bb.module(-3.2, -4.4, 3.0, 1.6, "耳机\n3.5 mm 转接板")
bb.wire((-0.2, -3.6), "j4", "out")
bb.wire((-1.5, -4.4), "B-2", "gnd", via=[(-1.5, -6.7)])
bb.module(31.3, -4.4, 3.2, 1.6, "手机音频输出\n信号 / 地")
bb.wire((31.3, -4.0), "j24", "sig", via=[(25.0, -4.9)])
bb.wire((32.9, -4.4), "B-29", "gnd", via=[(32.9, -6.7)])
bb.note(9.0, -0.3, "测输出：g8", va="center")
bb.note(21.0, -0.3, "测输入：g24", va="center")
bb.note(0.5, -9.6, "慢速实验：C 换 100 µF 电解（+ 脚插 j20，− 脚接地），输入换成一节 1.5 V 电池", ha="left")
bb.note(0.5, -10.4, "对照实验：去掉运放的作用——把 1 kΩ 直接并在 C 上（j20 到地）", ha="left")
bb.legend()
bb.save(N, "15_p4_1_breadboard.png")

# ---------- 图 15-p4-2：没有示波器时——用耳朵听衰减，用秒级 RC 看充电 ----------
fc = 1 / (2 * np.pi * R * C)
tones = np.array([100, 200, 500, 1000, 2000, 5000, 10000])
h = 1 / np.sqrt(1 + (tones / fc) ** 2)
for f_, h_ in zip(tones, h):
    print(f"[数值] 一阶低通 {f_:>5d} Hz：输出/输入 {h_:.3f}，{20*np.log10(h_):+.1f} dB")
print(f"[数值] 截止频率 {fc:.0f} Hz；100 Hz 时 0.707 V 输入 → 输出 {0.707*h[0]:.3f} V；"
      f"1 kΩ 直接并在电容上（100 Hz）→ {0.707*1e3/np.hypot(R + 1e3, 2*np.pi*100*R*1e3*C):.3f} V")
assert abs(fc - 995) < 1 and abs(h[0] - 0.995) < 0.001 and abs(h[-1] - 0.099) < 0.001
TAU_S = R * 100e-6
VB = 1.5
ts = np.linspace(0, 10, 501)
vs_ = fs.rc_step(ts, TAU_S, 0.0, VB)
print(f"[数值] 慢速版 R·C = {TAU_S:.1f} s；1.5 V 电池接入后 1τ {VB*(1-np.exp(-1)):.2f} V、"
      f"3τ {VB*(1-np.exp(-3)):.2f} V、5τ {VB*(1-np.exp(-5)):.2f} V")
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a1.bar(range(len(tones)), 20 * np.log10(h), color=fs.C["vout"], width=0.6)
for i, h_ in enumerate(h):
    a1.text(i, 20 * np.log10(h_) - 0.6, f"{int(round(20*np.log10(h_)))} dB", ha="center", va="top", fontsize=8)
a1.set_xticks(range(len(tones)))
a1.set_xticklabels(["100", "200", "500", "1k", "2k", "5k", "10k"])
a1.set_ylim(-25, 2); fs.ref_h(a1, -3, "−3 dB", x=0.99, ha="right")
fs.axlabels(a1, "手机放的音调频率", "Hz", "输出比输入小多少", "dB")
a1.set_title("用耳朵听：每小 6 dB，幅度减一半", fontsize=10)
a2.plot(ts, np.full_like(ts, VB), label="输入：1.5 V 电池", **fs.LS["vin"])
a2.plot(ts, vs_, label="输出：16 kΩ × 100 µF", **fs.LS["vout"])
for k in (1, 3):
    fs.mark(a2, k * TAU_S, VB * (1 - np.exp(-k)), "{:.2f}", " V", dy=-0.15)
fs.ref_v(a2, TAU_S, "1τ = 1.6 s")
a2.set_ylim(0, 1.75); a2.legend(loc="lower right", fontsize=8)
fs.axlabels(a2, "时间", "s", "万用表直流读数", "V")
a2.set_title("用万用表看：电容慢慢充电", fontsize=10)
fs.save(fig, N, "15_p4_2_no_scope.png")
