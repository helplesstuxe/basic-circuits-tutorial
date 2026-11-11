"""20 有源滤波：全部配图（图 20-p2-2 由 code/20_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/20_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

N = "20"
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


# ---------- 图 20-p1-1 带高频噪声的信号经过低通 ----------
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
fs.save(fig, N, "20_p1_1_denoise.png")

# ---------- 图 20-p1-2 一阶有源低通 ----------
with drawing() as d:
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R$ 16 kΩ")
    d += (n := elm.Dot())
    d += elm.Capacitor().down().label("$C$ 10 nF", "bottom")
    d += elm.Ground()
    follower_tail(d, n.center)
save_schem(d, N, "20_p1_2_first_order.png")
print(f"一阶低通 fc = 1/(2π × 16 kΩ × 10 nF) = {1 / (2 * np.pi * R * C):.0f} Hz")

# ---------- 图 20-p2-1 Sallen-Key 二阶低通 ----------
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
save_schem(d, N, "20_p2_1_sallen_key.png")
f0 = 1 / (2 * np.pi * np.sqrt(R1 * R2 * C1 * C2))
Q = np.sqrt(R1 * R2 * C1 * C2) / (C1 * (R1 + R2))
print(f"Sallen-Key：f0 = {f0:.0f} Hz，Q = {Q:.3f}")
assert abs(Q - 0.707) < 0.01 and abs(f0 - 1000) < 20

# ---------- 图 20-p2-3 一阶有源高通 ----------
with drawing() as d:
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Capacitor().right().label("$C$ 100 nF")
    d += (n := elm.Dot())
    d += elm.Resistor().down().label("$R$ 15.9 kΩ", "bottom")
    d += elm.Ground()
    follower_tail(d, n.center)
save_schem(d, N, "20_p2_3_highpass.png")
print(f"一阶高通 fc = 1/(2π × 15.9 kΩ × 100 nF) = {1 / (2 * np.pi * 15.9e3 * 100e-9):.0f} Hz")

# ---------- 图 20-p3-1 方波经过两种低通 ----------
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
fs.save(fig, N, "20_p3_1_square.png")

# ---------- 图 20-p3-2 漏了 2π：截止频率低了 6 倍多 ----------
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
fs.save(fig, N, "20_p3_2_missing_2pi.png")

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
        cname = {fs.C["bad"]: "红", "#000000": "黑", fs.C["third"]: "紫", fs.C["vin"]: "蓝",
                 fs.C["vout"]: "橙", fs.C["fb"]: "绿", fs.C["cur"]: "天蓝"}
        def lab(c, t):                                # 图例写成「用途（色名）」；用途里已有括号时并进同一对括号
            return t[:-1] + f"，{cname[c]}）" if t.endswith("）") else f"{t}（{cname[c]}）"
        hs = [Line2D([], [], color=WIRE[k][0], lw=2.4, label=lab(*WIRE[k])) for k in WIRE if k in self.used]
        self.ax.legend(handles=hs, loc=loc, ncol=len(hs), fontsize=8.5, frameon=False,
                       bbox_to_anchor=(0.5, -0.01))

    def save(self, prefix, name):
        return fs.save(self.fig, prefix, name)

# ---------- 图 20-p4-1：一阶有源低通的面包板接线（LM358，±9 V） ----------
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
bb.ax.set_ylim(-12.0, 11.6)                        # 底部多一行注记，往下多留一点（不动孔位）
bb.note(0.5, -9.4, "慢速实验：C 换 100 µF 电解（+ 脚插 j20，− 脚接地），输入换成一节 1.5 V 电池", ha="left")
bb.note(0.5, -10.2, "负载对照：拔掉耳机，1 kΩ 插 j8 到下边 GND 轨，红表笔仍插 g8", ha="left")
bb.note(0.5, -11.0, "对照实验：去掉运放的作用——把 1 kΩ 改并在 C 上（i20 到地），红表笔改插 f20", ha="left")
bb.legend()
bb.save(N, "20_p4_1_breadboard.png")

# ---------- 图 20-p4-2：没有示波器时——用耳朵听衰减，用秒级 RC 看充电 ----------
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
fs.save(fig, N, "20_p4_2_no_scope.png")


# ======================= 第 8 轮补图：正文讲到具体连接、附近却没有电路图的地方 =======================
ACC = fs.C["bad"]


def load_to_ground(d, at, label="1 kΩ 负载", color=ACC):
    """从 at 点往下接一只负载电阻到地（强调色），标签放在电阻右侧。"""
    d += (rl := elm.Resistor().down().at(at).color(color))
    d += elm.Ground().color(color)
    d += elm.Label().at((rl.center.x + 0.5, rl.center.y)).label(label, color=color, halign="left")


# ---------- 图 20-p1-3 1 kΩ 负载接在哪里：无源 RC 直接带负载 vs 有源（跟随器）带负载 ----------
with drawing(fontsize=11) as d:
    d += elm.Dot(open=True).at((0, 0)).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R$ 16 kΩ")
    d += (n := elm.Dot())
    d += elm.Capacitor().down().label("$C$ 10 nF", "bottom")
    d += elm.Ground()
    d += elm.Line().right().at(n.center).length(2.0)
    d += (m := elm.Dot())
    d += elm.Line().right().length(0.8)
    d += elm.Dot(open=True).label("$V_o$", "right")
    load_to_ground(d, m.center)
    d += elm.Label().at((-0.5, 3.4)).label("（a）无源 RC：负载直接并在电容上", fontsize=12, halign="left")
    d += elm.Dot(open=True).at((10.5, 0)).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R$ 16 kΩ")
    d += (n := elm.Dot())
    d += elm.Capacitor().down().label("$C$ 10 nF", "bottom")
    d += elm.Ground()
    op = follower_tail(d, n.center, out_len=1.8)
    load_to_ground(d, (op.out.x + 0.9, op.out.y))
    d += elm.Dot().at((op.out.x + 0.9, op.out.y))
    d += elm.Label().at((10.0, 3.4)).label("（b）有源：负载接在运放输出端", fontsize=12, halign="left")
save_schem(d, N, "20_p1_3_load_position.png")
print(f"[数值] 无源 RC 直接带 1 kΩ：低频输出只剩 1/(1 + 16) = {1 / 17:.2f} 倍；有源版不变")

# ---------- 图 20-p2-4 一阶低通推导用：同一个电流 I 流过 R 和 C ----------
with drawing(fontsize=11) as d:
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += (r := elm.Resistor().right().label("$R$ 16 kΩ"))
    d += (n := elm.Dot())
    d += (c := elm.Capacitor().down().label("$C$ 10 nF", "bottom"))
    d += elm.Ground()
    follower_tail(d, n.center)
    d += elm.Arrow().right().at((r.start.x + 0.4, r.start.y + 1.1)).length(2.2).color(ACC).label("$I$", "top", color=ACC)
    d += elm.Label().at((r.center.x, r.center.y - 0.6)).label("$V_R = I R$", color=ACC)
    d += elm.Label().at((c.center.x - 0.6, c.center.y)).label("$V_C = I X_C$", color=ACC, halign="right")
    d += elm.Label().at((n.center.x + 1.0, n.center.y - 1.9)).label("跟随器：$V_o = V_C$", halign="left", fontsize=10)
save_schem(d, N, "20_p2_4_first_order_derive.png")


# ---------- 图 20-p3-3 Sallen-Key：正确接法 vs 两个电容接反（排查表第三行） ----------
def sallen(d, x0, y0, c_gnd="10 nF", c_fb="33 nF", hl=False, title=None):
    col = ACC if hl else "black"
    d += elm.Dot(open=True).at((x0, y0)).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R_1$ 4.22 kΩ")
    d += (a := elm.Dot())
    d += elm.Resistor().right().label("$R_2$ 18.4 kΩ")
    d += (b := elm.Dot())
    d += elm.Capacitor().down().label(c_gnd, "bottom").color(col)
    d += elm.Ground()
    op = follower_tail(d, b.center, out_len=2.4)
    d += elm.Line().up().at(a.center).length(3.6)
    d += elm.Capacitor().right().label(c_fb).tox(op.out.x + 1.4).color(col)
    d += elm.Line().down().toy(op.out)
    d += elm.Dot()
    if title:
        d += elm.Label().at((x0 - 0.5, y0 + 4.6)).label(title, fontsize=12, halign="left")


with drawing(fontsize=11) as d:
    sallen(d, 0, 0, title="（a）正确：接地的是 10 nF，接输出的是 33 nF")
    sallen(d, 15, 0, c_gnd="33 nF", c_fb="10 nF", hl=True, title="（b）接反：接地的成了 33 nF，接输出的成了 10 nF")
save_schem(d, N, "20_p3_3_sk_caps_swapped.png")
Qs = np.sqrt(R1 * R2 * C1 * C2) / (C2 * (R1 + R2))
print(f"[数值] 电容接反：Q = {Qs:.2f}")

# ---------- 图 20-p3-4 练习 4 答案：一阶有源高通 + 2 倍同相放大 ----------
with drawing(fontsize=11) as d:
    d += elm.Dot(open=True).label("$V_i$", "left")
    d += elm.Capacitor().right().label("$C$ 100 nF")
    d += (n := elm.Dot())
    d += elm.Resistor().down().label("$R$ 15.9 kΩ", "bottom")
    d += elm.Ground()
    d += elm.Line().right().at(n.center).length(1.0)
    d += (op := elm.Opamp(leads=True).right().anchor("in2"))
    d += elm.Line().left().at(op.in1).length(0.4)
    d += elm.Line().up().length(1.4).color(ACC)
    d += (k2 := elm.Dot().color(ACC))
    d += elm.Resistor().right().label("$R_f$ 10 kΩ").tox(op.out.x + 0.6).color(ACC)
    d += elm.Line().down().toy(op.out).color(ACC)
    d += elm.Dot()
    d += elm.Resistor().left().at(k2.center).label("$R_1$ 10 kΩ").color(ACC)
    d += elm.Line().down().length(0.6).color(ACC)
    d += elm.Ground().color(ACC)
    d += elm.Line().right().at(op.out).length(1.2)
    d += elm.Dot(open=True).label("$V_o$（通带内约 2 倍）", "right")
save_schem(d, N, "20_p3_4_highpass_gain2.png")


# ======================= page2 第二节：无源 RC 低通与高通（补充） =======================
# 同一对 R = 16 kΩ、C = 10 nF：输出取电容 = 低通，输出取电阻 = 高通。图 20-p2-6 由 code/20_rc_sim.py 生成。
TAU = R * C
FC = 1 / (2 * np.pi * TAU)
lp1 = ([1.0], [TAU, 1.0])                               # 低通：1/(sτ + 1)
hp1 = ([TAU, 0.0], [TAU, 1.0])                          # 高通：sτ/(sτ + 1)

# ---------- 图 20-p2-5 两种接法：RC 低通 vs CR 高通 ----------
with drawing(fontsize=11) as d:
    d += elm.Dot(open=True).at((0, 0)).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R$ 16 kΩ")
    d += (n := elm.Dot())
    d += elm.Capacitor().down().label("$C$ 10 nF", "bottom")
    d += elm.Ground()
    d += elm.Line().right().at(n.center).length(1.6)
    d += elm.Dot(open=True).label("$V_o = V_C$", "right")
    d += elm.Label().at((-0.6, 2.0)).label("（a）低通：R 串在路上，C 接地，输出取电容", fontsize=12, halign="left")
    d += elm.Dot(open=True).at((11, 0)).label("$V_i$", "left")
    d += elm.Capacitor().right().label("$C$ 10 nF")
    d += (n := elm.Dot())
    d += elm.Resistor().down().label("$R$ 16 kΩ", "bottom")
    d += elm.Ground()
    d += elm.Line().right().at(n.center).length(1.6)
    d += elm.Dot(open=True).label("$V_o = V_R$", "right")
    d += elm.Label().at((10.4, 2.0)).label("（b）高通：C 串在路上，R 接地，输出取电阻", fontsize=12, halign="left")
save_schem(d, N, "20_p2_5_rc_lp_hp.png")
print(f"[数值] 无源 RC：τ = {TAU*1e3:.2f} ms，fc = {FC:.0f} Hz（低通、高通相同）")

# ---------- 图 20-p2-7 正弦在 fc 处：低通落后 45°、高通超前 45°、两者相加等于输入 ----------
t = np.linspace(0, 3 / FC, 3001)
vi = fs.sine(t, FC)                                     # 从 0 开始算会有开头的过渡过程，所以算 6 个周期、只画后 3 个
t6 = np.linspace(0, 6 / FC, 6001)
_, vc6, _ = signal.lsim(lp1, fs.sine(t6, FC), t6)
vc = vc6[3000:]; vr = vi - vc                           # 回路定律：V_R + V_C = V_i（任何时刻都成立）
amp_c, amp_r = vc.max(), vr.max()
k_i = np.argmax(vi[:1000]); k_c = np.argmax(vc[:1500])  # 第一个周期里输入和 V_C 的峰值位置
lag_c = (t[k_c] - t[k_i]) * FC * 360
print(f"[数值] f = fc 时：V_C 幅度 {amp_c:.3f}，V_R 幅度 {amp_r:.3f}；V_C 峰值比输入晚 {lag_c:.0f}°（= {(t[k_c]-t[k_i])*1e6:.0f} μs）")
assert abs(amp_c - 0.707) < 0.005 and abs(amp_r - 0.707) < 0.005 and abs(lag_c - 45) < 2
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi, **fs.LS["vin"], label="$V_i$ 输入")
ax.plot(t * 1e3, vc, **fs.LS["vout"], label="$V_C$ 低通输出（晚 45°）")
ax.plot(t * 1e3, vr, **fs.LS["third"], label="$V_R$ 高通输出（早 45°）")
ax.plot(t[::60] * 1e3, (vc + vr)[::60], ls="none", marker="o", ms=3, color=fs.C["good"], label="$V_C + V_R$")
fs.ref_h(ax, 0)
fs.ref_v(ax, t[k_i] * 1e3, "输入峰值", y=0.12)
fs.ref_v(ax, t[k_c] * 1e3, "$V_C$ 峰值", y=0.25)
fs.mark(ax, t[k_c] * 1e3, amp_c, fmt="{:.3f}", unit=" V", dx=4, dy=4)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-1.3, 1.6)
ax.legend(loc="upper right", fontsize=8, ncol=4)
fs.save(fig, N, "20_p2_7_rc_phase.png")

# ---------- 图 20-p2-8 方波经过同一对 RC：半周期分别是 31τ、3.1τ、0.31τ ----------
fig, axs = plt.subplots(3, 2, figsize=(9, 6.2), sharey="row")
for row, fsq in enumerate((100, 1e3, 10e3)):
    T = 1 / fsq
    n_pre = int(np.ceil(10 * TAU / T))                  # 先空跑 10τ 以上（整数个周期），让开头的过渡过程消失
    npt = int(max(2000, 400 * T / TAU))                 # 每周期的点数：步长不超过 τ/400，跳变后的尖峰才算得准
    tt = np.linspace(0, (n_pre + 4) * T, (n_pre + 4) * npt + 1)
    sq_all = fs.square(tt, fsq)                         # ±1 V 方波
    _, ylp, _ = signal.lsim(lp1, sq_all, tt)
    _, yhp, _ = signal.lsim(hp1, sq_all, tt)
    keep = tt >= n_pre * T - 1e-12                      # 只画最后 4 个周期（已是稳态）
    t, sq, ylp, yhp = tt[keep] - n_pre * T, sq_all[keep], ylp[keep], yhp[keep]
    ratio = (T / 2) / TAU
    a = np.exp(-ratio)                                  # 半个周期里，指数过程剩下的比例 e^(-半周期/τ)
    seg = t >= 0
    print(f"[数值] {fsq:g} Hz 方波（半周期 = {ratio:.2f}τ）：低通输出 {ylp[seg].min():+.2f}～{ylp[seg].max():+.2f} V；"
          f"高通输出 {yhp[seg].min():+.2f}～{yhp[seg].max():+.2f} V")
    for col, (y, ls, nm) in enumerate(((ylp, "vout", "低通"), (yhp, "third", "高通"))):
        ax = axs[row, col]
        ax.plot(t * 1e3, sq, **{**fs.LS["vin"], "lw": 1.0})
        ax.plot(t * 1e3, y, **fs.LS[ls])
        fs.ref_h(ax, 0)
        ax.set_title(f"{nm}：{fsq/1e3:g} kHz 方波，半周期 ≈ {ratio:.2g}τ", fontsize=10)
        ax.set_ylim(-2.3, 2.3)
        if row == 2:
            fs.axlabels(ax, "时间", "ms", "电压" if col == 0 else None, "V")
        elif col == 0:
            ax.set_ylabel("电压 / V")
    print(f"[数值]   半周期内指数过程剩 e^(−{ratio:.2f}) = {a:.3f}；稳态公式：高通峰值 2/(1+a) = {2/(1+a):.2f} V，"
          f"低通峰值 (1−a)/(1+a) = {(1-a)/(1+a):.2f} V")
    assert abs(yhp.max() - 2 / (1 + a)) < 0.03 and abs(ylp.max() - (1 - a) / (1 + a)) < 0.01  # 仿真与稳态公式一致
fig.legend([plt.Line2D([], [], **fs.LS["vin"]), plt.Line2D([], [], **fs.LS["vout"]), plt.Line2D([], [], **fs.LS["third"])],
           ["$V_i$ 方波 ±1 V", "低通输出 $V_C$", "高通输出 $V_R$"], loc="lower center", ncol=3, fontsize=9, frameon=False)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fs.save(fig, N, "20_p2_8_rc_square.png", tight=False)

# ---------- 图 20-p2-9 无源 RC 的「怕」：信号源内阻、负载、直接串两级 ----------
with drawing(fontsize=11) as d:
    d += elm.SourceSin().up().at((0, -2.5)).label("$V_s$", "left")
    d += elm.Resistor().right().label("$R_s$ 1 kΩ\n（信号源内阻）").color(ACC)
    d += elm.Resistor().right().label("$R$ 16 kΩ")
    d += (n := elm.Dot())
    d += elm.Capacitor().down().label("$C$ 10 nF", "bottom")
    d += elm.Line().left().tox(0)
    d += elm.Line().right().at(n.center).length(2.0)
    d += (m := elm.Dot())
    d += elm.Resistor().down().label("$R_L$ 负载", "bottom").color(ACC)
    d += elm.Line().left().tox(n.center.x)
    d += elm.Ground().at((n.center.x, -2.5))
    d += elm.Line().right().at(m.center).length(1.0)
    d += elm.Dot(open=True).label("$V_o$", "right")
    d += elm.Label().at((-0.6, 2.0)).label("（a）前面有内阻、后面有负载", fontsize=12, halign="left")
    d += elm.Dot(open=True).at((15, 0)).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R$ 16 kΩ")
    d += (a := elm.Dot())
    d += elm.Capacitor().down().label("$C$ 10 nF", "bottom")
    d += elm.Ground()
    d += elm.Resistor().right().at(a.center).label("$R$ 16 kΩ").color(ACC)
    d += (b := elm.Dot())
    d += elm.Capacitor().down().label("$C$ 10 nF", "bottom").color(ACC)
    d += elm.Ground()
    d += elm.Line().right().at(b.center).length(1.2)
    d += elm.Dot(open=True).label("$V_o$", "right")
    d += elm.Label().at((14.4, 2.0)).label("（b）两级一样的 RC 直接串联", fontsize=12, halign="left")
save_schem(d, N, "20_p2_9_rc_loading_schem.png")

f = np.logspace(1, 5, 1200); s = 2j * np.pi * f
ideal = np.abs(1 / (1 + s * TAU))
par = lambda a, b: a * b / (a + b)
withRs = np.abs(1 / (1 + s * (R + 1e3) * C))
RL = 16e3
withRL = np.abs(RL / (R + RL) / (1 + s * par(R, RL) * C))
casc = np.abs(1 / (1 + 3 * s * TAU + (s * TAU) ** 2))       # 两级直接串：1/(1 + 3sτ + s²τ²)
buf = ideal ** 2                                             # 中间隔一个跟随器：两级各自独立，倍数相乘
f3 = lambda h, ref=1.0: f[np.argmin(np.abs(h - ref / np.sqrt(2)))]
print(f"[数值] 前面加 Rs = 1 kΩ：fc 由 {FC:.0f} Hz 降到 {1/(2*np.pi*(R+1e3)*C):.0f} Hz")
print(f"[数值] 后面接 RL = 16 kΩ：低频只剩 {RL/(R+RL):.2f} 倍，fc 升到 {1/(2*np.pi*par(R, RL)*C):.0f} Hz")
print(f"[数值] RL = 1 kΩ：低频只剩 {1e3/(R+1e3):.3f} 倍（约 1/17），fc 升到 {1/(2*np.pi*par(R, 1e3)*C)/1e3:.1f} kHz")
print(f"[数值] 两级直接串：−3 dB 在 {f3(casc):.0f} Hz（{f3(casc)/FC:.2f} fc），fc 处只剩 {abs(1/(1+3j-1)):.3f} 倍；"
      f"隔跟随器：−3 dB 在 {f3(buf):.0f} Hz（{f3(buf)/FC:.2f} fc），fc 处 0.500 倍")
assert abs(f3(casc) / FC - 0.374) < 0.01 and abs(f3(buf) / FC - 0.644) < 0.01
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.semilogx(f, 20 * np.log10(ideal), **fs.LS["good"], label="单级、理想（空载、无内阻）")
ax.semilogx(f, 20 * np.log10(withRL), **fs.LS["third"], label="后面接 16 kΩ 负载")
ax.semilogx(f, 20 * np.log10(buf), **fs.LS["vout"], label="两级，中间隔跟随器")
ax.semilogx(f, 20 * np.log10(casc), **fs.LS["bad"], label="两级直接串联")
fs.ref_v(ax, FC, f"fc ≈ {FC:.0f} Hz", y=0.12)
fs.mark(ax, FC, 20 * np.log10(1 / 3), fmt="{:.1f}", unit=" dB", dx=6, dy=-12, color=fs.C["bad"])
fs.mark(ax, FC, 20 * np.log10(0.5), fmt="{:.1f}", unit=" dB", dx=6, dy=2)
fs.axlabels(ax, "频率", "Hz", "输出/输入 幅度", "dB")
ax.set_xticks([10, 100, 1e3, 1e4, 1e5]); ax.set_xticklabels(["10", "100", "1 k", "10 k", "100 k"])
ax.set_ylim(-60, 5); ax.legend(loc="lower left", fontsize=8)
fs.save(fig, N, "20_p2_10_rc_loading.png")


# ======================= page2 第二节：阻抗（容抗、RC 串联与并联、高低频等效） =======================
# 图 20-p2-11 由 code/20_z_sim.py 生成。
XC_FC = 1 / (2 * np.pi * FC * C)                        # fc 处容抗（= R）

# ---------- 图 20-p2-12 RC 串联与并联：谁相同、谁按勾股定理合成 ----------
with drawing(fontsize=11) as d:
    d += elm.SourceSin().up().at((0, -3)).label("$V$\n1 V", "left")
    d += elm.Resistor().right().label("$R$ 16 kΩ").label("$V_R = IR$", "bottom", color=ACC)
    d += elm.Capacitor().down().toy(-3).label("$C$ 10 nF").label("$V_C = I X_C$", "bottom", color=ACC)
    d += elm.Line().left().tox(0)
    d += elm.Arrow().right().at((0.6, 0.9)).length(1.8).color(ACC).label("$I$（同一个）", "top", color=ACC)
    d += elm.Label().at((-0.8, 2.1)).label("（a）串联：电流相同，两段电压错开 90°", fontsize=12, halign="left")
    x0 = 13
    d += elm.SourceSin().up().at((x0, -3)).label("$V$\n1 V", "left")
    d += elm.Line().right().length(2.5)
    d += (p1 := elm.Dot())
    d += elm.Resistor().down().toy(-3).label("$R$ 16 kΩ").label("$I_R = V/R$", "bottom", color=ACC)
    d += elm.Line().right().at(p1.center).length(4.5)
    d += elm.Capacitor().down().toy(-3).label("$C$ 10 nF").label("$I_C = V/X_C$", "bottom", color=ACC)
    d += elm.Line().left().tox(x0)
    d += elm.Arrow().right().at((x0 + 0.4, 0.7)).length(1.6).color(ACC).label("$I$", "top", color=ACC)
    d += elm.Label().at((x0 - 0.8, 2.1)).label("（b）并联：电压相同，两路电流错开 90°", fontsize=12, halign="left")
save_schem(d, N, "20_p2_12_series_parallel.png")

# ---------- 图 20-p2-13 f = fc 时的电压三角形（串联）和电流三角形（并联） ----------
I_s = 1 / np.sqrt(R ** 2 + XC_FC ** 2)                  # 串联电流幅度
VR, VC = I_s * R, I_s * XC_FC
IR, IC = 1 / R, 1 / XC_FC                               # 并联两路电流（电压 1 V）
I_p = np.hypot(IR, IC)
print(f"[数值] f = fc、电压 1 V：串联 |Z| = {1/I_s/1e3:.1f} kΩ，I = {I_s*1e6:.1f} μA，V_R = {VR:.3f} V，V_C = {VC:.3f} V")
print(f"[数值] f = fc、电压 1 V：并联 I_R = {IR*1e6:.1f} μA，I_C = {IC*1e6:.1f} μA，I = {I_p*1e6:.1f} μA，|Z| = {1/I_p/1e3:.1f} kΩ")
assert abs(VR - 0.707) < 0.001 and abs(1 / I_p - R / np.sqrt(2)) < 1
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
for ax, (h, v, hl, vl, hy) in ((a1, (VR, VC, f"$V_R$ = {VR:.3f} V", f"$V_C$ = {VC:.3f} V", "总电压 1 V")),
                               (a2, (IR * 1e6, IC * 1e6, f"$I_R$ = {IR*1e6:.1f} μA", f"$I_C$ = {IC*1e6:.1f} μA", f"总电流 {I_p*1e6:.1f} μA"))):
    ax.plot([0, h], [0, 0], color=fs.C["vin"], lw=2.2)
    ax.plot([h, h], [0, v], color=fs.C["fb"], lw=2.2, ls="--")
    ax.plot([0, h], [0, v], color=fs.C["vout"], lw=2.4)
    ax.plot([h - 0.06 * h, h - 0.06 * h, h], [0, 0.06 * h, 0.06 * h], color="k", lw=0.8)   # 直角记号
    ax.text(h / 2, -0.07 * h, hl, ha="center", va="top", fontsize=10)
    ax.text(h * 1.03, v / 2, vl, ha="left", va="center", fontsize=10)
    ax.text(h * 0.42, v * 0.58, hy, ha="right", va="bottom", fontsize=10, rotation=40)
    ax.text(0.16 * h, 0.035 * h, "45°", fontsize=9)
    ax.set_xlim(-0.1 * h, 1.75 * h); ax.set_ylim(-0.25 * h, 1.15 * v); ax.set_aspect("equal"); ax.axis("off")
a1.set_title("（a）串联：电压三角形", fontsize=11)
a2.set_title("（b）并联：电流三角形", fontsize=11)
fs.save(fig, N, "20_p2_13_triangles.png")

# ---------- 图 20-p2-14 低频、高频时电容的「极限画法」 ----------
def lim_panel(d, x0, kind, freq, title):
    """kind: 'lp' 或 'hp'；freq: 'low'（电容≈断开）或 'high'（电容≈导线）。"""
    open_c = freq == "low"
    d += elm.Dot(open=True).at((x0, 0)).label("$V_i$", "left")
    if kind == "lp":
        d += elm.Resistor().right().label("$R$")
        d += (n := elm.Dot())
        if open_c:
            d += elm.Line().down().length(0.9)
            d += elm.Gap().down().length(1.2).label("C≈断开", "right", color=ACC)
            d += elm.Line().down().length(0.9)
        else:
            d += elm.Line().down().length(3.0).color(ACC).label("C≈导线", "right", color=ACC)
        d += elm.Ground()
        out = "$V_o \\approx V_i$" if open_c else "$V_o \\approx 0$"
    else:
        if open_c:
            d += elm.Gap().right().length(3.0).label("C≈断开", color=ACC)
        else:
            d += elm.Line().right().length(3.0).color(ACC).label("C≈导线", color=ACC)
        d += (n := elm.Dot())
        d += elm.Resistor().down().label("$R$", "bottom")
        d += elm.Ground()
        out = "$V_o \\approx 0$" if open_c else "$V_o \\approx V_i$"
    d += elm.Line().right().at(n.center).length(1.4)
    d += elm.Dot(open=True).label(out, "right")
    d += elm.Label().at((x0 - 0.5, 1.6)).label(title, fontsize=11, halign="left")


with drawing(fontsize=11) as d:
    lim_panel(d, 0, "lp", "low", "（a）低通，频率很低")
    lim_panel(d, 9, "lp", "high", "（b）低通，频率很高")
    lim_panel(d, 18, "hp", "low", "（c）高通，频率很低")
    lim_panel(d, 27, "hp", "high", "（d）高通，频率很高")
save_schem(d, N, "20_p2_14_limits.png")

# ---------- 图 20-p2-15 同一条低通频响曲线：线性坐标 vs 对数坐标 ----------
fl = np.linspace(1, 20e3, 4000)
fg = np.logspace(1, 5, 800)
H = lambda fx: 1 / np.sqrt(1 + (fx / FC) ** 2)
fig, (a1, a2) = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
a1.plot(fl / 1e3, H(fl), **fs.LS["vout"])
fs.ref_v(a1, FC / 1e3); fs.ref_h(a1, 1 / np.sqrt(2))
fs.axlabels(a1, "频率", "kHz", "输出/输入 倍数")
a1.set_title("（a）线性坐标：1 kHz 以下挤成一团", fontsize=10); a1.set_ylim(0, 1.08)
a2.semilogx(fg, 20 * np.log10(H(fg)), **fs.LS["vout"])
fs.ref_v(a2, FC); fs.ref_h(a2, -3)
a2.axvspan(10, FC / 10, color=fs.C["fill"], zorder=0)
a2.axvspan(FC / 10, FC * 10, color=fs.C["fill2"], zorder=0)
a2.axvspan(FC * 10, 1e5, color="0.93", zorder=0)
for xx, tt in ((np.sqrt(10 * FC / 10), "通带"), (FC, "过渡带"), (np.sqrt(FC * 10 * 1e5), "阻带")):
    a2.text(xx, -36, tt, ha="center", fontsize=10)
fs.axlabels(a2, "频率", "Hz", "输出/输入", "dB")
a2.set_xticks([10, 100, 1e3, 1e4, 1e5]); a2.set_xticklabels(["10", "100", "1 k", "10 k", "100 k"])
a2.set_title("（b）对数坐标 + 分贝：每十倍一样宽", fontsize=10); a2.set_ylim(-42, 4)
fs.save(fig, N, "20_p2_15_lin_vs_log.png")
print(f"[数值] 线性坐标 0～20 kHz 里，0～{FC/1e3:.2f} kHz 只占横轴的 {FC/20e3*100:.0f}%")


# ======================= page2 第二节第 2 小节：「慢 90°」是什么意思 =======================
# ---------- 图 20-p2-16 电阻：电流和电压同步；电容：电流比电压早四分之一周期 ----------
T1 = 1e-3                                               # 1 kHz，周期 1 ms
t = np.linspace(0, 2 * T1, 2001)
v = np.sin(2 * np.pi * t / T1)                          # 电压（幅度 1）
i_c = np.cos(2 * np.pi * t / T1)                        # 电容电流（按幅度归一）：正比于电压斜率
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.2), sharey=True)
a1.plot(t * 1e3, v, **fs.LS["vin"], label="电压 $V$")
a1.plot(t * 1e3, 0.8 * v, **{**fs.LS["cur"], "ls": "--"}, label="电流 $I = V/R$")
fs.ref_h(a1, 0); fs.ref_v(a1, 0.25, "峰值同时到", y=0.12)
a1.set_title("（a）电阻：电流和电压同步（相差 0°）", fontsize=10)
fs.axlabels(a1, "时间", "ms", "幅度（归一）"); a1.legend(loc="upper right", fontsize=8)
a2.plot(t * 1e3, v, **fs.LS["vin"], label="电容电压 $V_C$")
a2.plot(t * 1e3, i_c, **{**fs.LS["cur"], "ls": "--"}, label="电容电流 $I_C$")
fs.ref_h(a2, 0)
for tk, txt, dy in ((0.0, "①", 8), (0.25, "②", 8), (0.5, "③", -16), (0.75, "④", -16)):
    vk = np.sin(2 * np.pi * tk); sk = np.cos(2 * np.pi * tk)          # 该时刻电压和斜率（归一）
    a2.plot([tk - 0.07, tk + 0.07], [vk - 0.07 * sk * 2 * np.pi, vk + 0.07 * sk * 2 * np.pi], color="k", lw=1.6)  # 斜率短线
    a2.annotate(txt, (tk, vk), xytext=(4, dy), textcoords="offset points", fontsize=10)
fs.span(a2, 1.0, 1.25, 1.12, "早 1/4 周期 = 90°")
a2.plot([1.0, 1.0], [0, 1.0], **fs.LS["ref"]); a2.plot([1.25, 1.25], [0, 1.0], **fs.LS["ref"])
a2.set_title("（b）电容：电流波峰比电压波峰早 1/4 周期", fontsize=10)
fs.axlabels(a2, "时间", "ms"); a2.set_ylim(-1.35, 1.45); a2.legend(loc="lower right", fontsize=8)
fs.save(fig, N, "20_p2_16_ninety_degrees.png")
print("[数值] 1 kHz：周期 1 ms，90° = 0.25 ms；50 Hz：周期 20 ms，90° = 5 ms")

# ---------- 图 20-p2-17 转动箭头：正弦 = 箭头的高度；错开 90° 的两个箭头相加 = 勾股定理 ----------
from matplotlib.patches import Circle as _Circle
th0 = np.radians(30)                                    # 画图时刻：电压箭头转到 30°
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(10.5, 3.4), gridspec_kw=dict(width_ratios=[1, 1.5, 1]))
a1.add_patch(_Circle((0, 0), 1, fill=False, color="0.7", lw=0.8))
for ang, col, lab in ((th0, fs.C["vin"], "$V_C$"), (th0 + np.pi / 2, fs.C["cur"], "$I_C$")):
    a1.annotate("", xy=(np.cos(ang), np.sin(ang)), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
    a1.text(1.12 * np.cos(ang), 1.12 * np.sin(ang), lab, color=col, ha="center", va="center", fontsize=11)
    a1.plot([np.cos(ang), 1.6], [np.sin(ang), np.sin(ang)], color=col, lw=0.8, ls=":")
a1.annotate("", xy=(0.45 * np.cos(th0 + 1.2), 0.45 * np.sin(th0 + 1.2)), xytext=(0.45 * np.cos(th0 + 0.3), 0.45 * np.sin(th0 + 0.3)),
            arrowprops=dict(arrowstyle="->", color="k", connectionstyle="arc3,rad=0.3"))
a1.text(0.12, 0.42, "90°", fontsize=9)
a1.annotate("", xy=(-0.55, -1.0), xytext=(0.55, -1.0), arrowprops=dict(arrowstyle="<-", color="0.4", connectionstyle="arc3,rad=-0.35"))
a1.text(0, -1.42, "逆时针转，每秒 f 圈", ha="center", fontsize=9)
a1.set_xlim(-1.4, 1.65); a1.set_ylim(-1.6, 1.4); a1.set_aspect("equal"); a1.axis("off")
a1.set_title("（a）两个一起转的箭头", fontsize=10)
ph = np.linspace(0, 2 * np.pi, 400)
a2.plot(np.degrees(ph), np.sin(ph), **fs.LS["vin"], label="$V_C$ 箭头的高度")
a2.plot(np.degrees(ph), np.cos(ph), **{**fs.LS["cur"], "ls": "--"}, label="$I_C$ 箭头的高度")
a2.axvline(np.degrees(th0), **fs.LS["ref"])
a2.plot([np.degrees(th0)] * 2, [np.sin(th0), np.cos(th0)], "o", color="k", ms=4)
fs.ref_h(a2, 0)
a2.set_xticks([0, 90, 180, 270, 360]); a2.set_xlabel("箭头转过的角度 / °")
a2.set_title("（b）把高度随转角画出来，就是两条正弦", fontsize=10); a2.legend(loc="lower left", fontsize=8)
a2.set_ylim(-1.3, 1.3)
VRv, VCv = 0.6, 0.8                                     # 例：串联时 V_R = 0.6、V_C = 0.8（单位：输入幅度）
a3.annotate("", xy=(VRv, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=fs.C["vin"], lw=2))
a3.annotate("", xy=(VRv, -VCv), xytext=(VRv, 0), arrowprops=dict(arrowstyle="-|>", color=fs.C["fb"], lw=2))
a3.annotate("", xy=(VRv, -VCv), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=fs.C["vout"], lw=2.2))
a3.text(VRv / 2, 0.06, "$V_R$ = 0.6", ha="center", va="bottom", fontsize=10)
a3.text(VRv + 0.05, -VCv / 2, "$V_C$ = 0.8", ha="left", va="center", fontsize=10)
a3.text(VRv / 2 - 0.12, -VCv / 2 + 0.05, "合起来 = 1.0", ha="right", va="center", fontsize=10, rotation=-53)
a3.set_xlim(-0.6, 1.3); a3.set_ylim(-1.05, 0.35); a3.set_aspect("equal"); a3.axis("off")
a3.set_title("（c）垂直的两个箭头首尾相接", fontsize=10)
amp = np.max(VRv * np.sin(ph) + VCv * np.sin(ph - np.pi / 2))
print(f"[数值] 0.6·sin(θ) + 0.8·sin(θ − 90°) 的最大值 = {amp:.3f}（= √(0.6² + 0.8²)）")
assert abs(amp - 1.0) < 1e-3
fs.save(fig, N, "20_p2_17_rotating_arrows.png")


# ======================= page2 第四节：RL 低通与高通 =======================
# 图 20-p2-19 由 code/20_rl_sim.py 生成。R = 100 Ω、L = 16 mH，τ = L/R = 0.16 ms，与前面的 RC 相同。
RLR, RLL = 100.0, 16e-3
TAU_L = RLL / RLR

# ---------- 图 20-p2-18 RL 低通与 RL 高通 ----------
with drawing(fontsize=11) as d:
    d += elm.Dot(open=True).at((0, 0)).label("$V_i$", "left")
    d += elm.Inductor2().right().label("$L$ 16 mH")
    d += (n := elm.Dot())
    d += elm.Resistor().down().label("$R$ 100 Ω", "bottom")
    d += elm.Ground()
    d += elm.Line().right().at(n.center).length(1.6)
    d += elm.Dot(open=True).label("$V_o = V_R$", "right")
    d += elm.Label().at((-0.6, 2.0)).label("（a）低通：L 串在路上，R 接地，输出取电阻", fontsize=12, halign="left")
    d += elm.Dot(open=True).at((11, 0)).label("$V_i$", "left")
    d += elm.Resistor().right().label("$R$ 100 Ω")
    d += (n := elm.Dot())
    d += elm.Inductor2().down().label("$L$ 16 mH", "bottom")
    d += elm.Ground()
    d += elm.Line().right().at(n.center).length(1.6)
    d += elm.Dot(open=True).label("$V_o = V_L$", "right")
    d += elm.Label().at((10.4, 2.0)).label("（b）高通：R 串在路上，L 接地，输出取电感", fontsize=12, halign="left")
save_schem(d, N, "20_p2_18_rl_lp_hp.png")
print(f"[数值] RL：τ = L/R = {TAU_L*1e3:.2f} ms，fc = R/(2πL) = {RLR/(2*np.pi*RLL):.0f} Hz")

# ---------- 图 20-p2-20 RL 的阶跃响应：1 V 脉冲（宽 1 ms ≈ 6τ） ----------
t = np.linspace(-0.2e-3, 2e-3, 4401)
vin = np.where((t >= 0) & (t < 1e-3), 1.0, 0.0)
on = np.clip(t, 0, 1e-3)
i_l = (1 - np.exp(-on / TAU_L)) / RLR                              # 电流：接通后按 1 − e^(−t/τ) 爬升
i_end = i_l[np.searchsorted(t, 1e-3) - 1]
i_l = np.where(t >= 1e-3, i_end * np.exp(-(t - 1e-3) / TAU_L), i_l)   # 输入回到 0 后按 e^(−t/τ) 衰减
v_r = i_l * RLR                                                    # 低通输出 = 电阻电压 = I·R
v_l = vin - v_r                                                    # 高通输出 = 电感电压 = 输入 − 电阻电压
k1 = np.searchsorted(t, TAU_L)
print(f"[数值] RL 脉冲：t = τ 时低通输出 {v_r[k1]:.3f} V（= 1 − e^-1），高通输出 {v_l[k1]:.3f} V（= e^-1）；"
      f"输入跳回 0 的瞬间高通输出 {v_l[np.searchsorted(t, 1e-3)]:.3f} V")
assert abs(v_r[k1] - 0.632) < 0.005 and v_l[np.searchsorted(t, 1e-3)] < -0.99
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vin, **fs.LS["vin"], label="$V_i$ 输入脉冲")
ax.plot(t * 1e3, v_r, **fs.LS["vout"], label="低通输出 $V_R$（= 电流 × R）")
ax.plot(t * 1e3, v_l, **fs.LS["third"], label="高通输出 $V_L$")
fs.ref_h(ax, 0); fs.ref_v(ax, TAU_L * 1e3, "t = τ = L/R", y=0.12)
fs.mark(ax, TAU_L * 1e3, v_r[k1], fmt="{:.3f}", unit=" V", dx=6, dy=-4)
fs.mark(ax, TAU_L * 1e3, v_l[k1], fmt="{:.3f}", unit=" V", dx=6, dy=2)
fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-1.25, 1.45)
ax.legend(loc="upper right", fontsize=8, ncol=3)
fs.save(fig, N, "20_p2_20_rl_step.png")

# ---------- 图 20-p2-21 二分频音箱：电感给低音、电容给高音 ----------
RSPK, FX = 8.0, 2000.0
Lx, Cx = RSPK / (2 * np.pi * FX), 1 / (2 * np.pi * FX * RSPK)
print(f"[数值] 分频点 2 kHz、喇叭按 8 Ω 纯电阻算：L = {Lx*1e3:.3f} mH，C = {Cx*1e6:.2f} μF")
with drawing(fontsize=11) as d:
    d += elm.SourceSin().up().at((0, -4)).label("功放\n输出", "left")
    d += elm.Line().up().length(1.0)
    d += elm.Line().right().length(1.5)
    d += (p := elm.Dot())
    d += elm.Inductor2().right().label(f"$L$ {Lx*1e3:.2f} mH")
    d += elm.Line().right().length(0.5)
    d += elm.Resistor().down().toy(-4).label("低音喇叭\n（按 8 Ω 算）", "bottom")
    d += elm.Line().up().at(p.center).length(2.5)
    d += elm.Capacitor().right().label(f"$C$ {Cx*1e6:.2f} μF")
    d += elm.Line().right().length(3.0)
    d += elm.Resistor().down().toy(-4).label("高音喇叭\n（按 8 Ω 算）", "bottom")
    d += elm.Line().left().tox(0)
    d += elm.Label().at((p.center.x + 0.3, p.center.y - 1.2)).label("低通：给低音", color=ACC, halign="left")
    d += elm.Label().at((p.center.x + 1.2, p.center.y + 1.6)).label("高通：给高音", color=ACC, halign="left")
save_schem(d, N, "20_p2_21_crossover.png")
