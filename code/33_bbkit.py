"""作者 B（33、34、36、37 节）共用的面包板俯视图小工具。
内容照抄 code/figs/20_figs.py 的 Breadboard 类，另加：
  * 「vg」中点参考导线（紫）、「clk」时钟导线（天蓝）两种颜色；
  * route()：在两排孔之间走线，避免导线压在不相干的孔上；
  * module_pins()：面包板外模块（Arduino、手机、电池）上的引脚小点。
用法（在 code/figs/NN_figs.py 里）：
    import importlib.util, os
    _sp = importlib.util.spec_from_file_location("bbkit", os.path.join(<code 目录>, "33_bbkit.py"))
    bbk = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(bbk)
本文件只定义类和函数，直接运行时什么都不画。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
import figstyle as fs
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

BB_Y = {r: 5.6 - i for i, r in enumerate("abcde")}
BB_Y.update({r: -1.4 - i for i, r in enumerate("fghij")})
BB_Y.update({"T+": 8.6, "T-": 7.7, "B-": -6.7, "B+": -7.6})
RED = "#d0101e"   # 正电源用纯红，和输出的橙色分得开
WIRE = dict(pos=(RED, "正电源"), gnd=("#000000", "地（0 V）"), vg=(fs.C["third"], "中点参考 V_MID"),
            sig=(fs.C["vin"], "输入信号"), out=(fs.C["vout"], "输出"), fb=(fs.C["fb"], "反馈 / 其他连线"),
            clk=(fs.C["cur"], "时钟 / 数字信号"))
CNAME = {RED: "红", "#000000": "黑", fs.C["third"]: "紫", fs.C["vin"]: "蓝",
         fs.C["vout"]: "橙", fs.C["fb"]: "绿", fs.C["cur"]: "天蓝"}


class Breadboard:
    """rails = (上外, 上内, 下内, 下外) 四条电源轨的名字；名字以 + 开头画红，GND 画黑，其余（如 V_MID）画紫。"""
    def __init__(self, ncol=30, title=None, size=(10, 6.4), rails=("+", "−", "−", "+")):
        self.ncol, self.used = ncol, set()
        self.fig, self.ax = plt.subplots(figsize=size)
        ax = self.ax
        ax.add_patch(FancyBboxPatch((0.2, -8.3), ncol + 0.6, 17.6, boxstyle="round,pad=0.1",
                                    fc="#f7f5ef", ec="0.55", lw=1.0))
        ax.add_patch(Rectangle((0.4, -0.55), ncol + 0.2, 0.7, fc="#e4e0d6", ec="none"))
        for key, lab in zip(("T+", "T-", "B-", "B+"), rails):
            y = BB_Y[key]
            if lab in ("", None, "—"):
                continue
            col = RED if lab.startswith("+") else ("#000000" if lab in ("−", "GND", "0 V") or lab.startswith("GND") or lab.endswith("地") else fs.C["third"])
            ax.plot([0.6, ncol + 0.4], [y + 0.42, y + 0.42], color=col, lw=1.0)
            ax.text(0.0, y, lab, ha="right", va="center", fontsize=9.5, color=col, fontweight="bold")
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

    def wire(self, a, b, kind="fb", via=None, ls="-"):
        """导线：a、b 为孔名或 (x, y)；via 为中间拐点列表。颜色按 kind 取（见 WIRE）。"""
        self.used.add(kind)
        pts = [self._hole(a)] + list(via or []) + [self._hole(b)]
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=WIRE[kind][0], lw=2.4, solid_capstyle="round", zorder=5, ls=ls)

    def route(self, a, b, kind="fb", dy=-0.5, ls="-"):
        """从孔 a 先竖着走 dy（落到两排孔之间），横走到 b 的列，再竖着进孔 b。"""
        xa, ya = self.xy(a)
        xb, yb = self.xy(b)
        self.wire(a, b, kind, via=[(xa, ya + dy), (xb, ya + dy)], ls=ls)

    def part(self, a, b, label, kind="R", lab_side=1, fs_=8.5, dashed=False):
        """两脚元件：R 电阻、C 电容、E 电解电容（+ 脚在 a）、D 二极管（a 阳 b 阴）、L LED（a 阳）、
        S 按钮、P 小灯泡、X 晶振/压电片。画成方框简化符号，标签写在旁边。lab_side：1 上/右，-1 下/左，"r" 右侧。"""
        (x1, y1), (x2, y2) = self._hole(a), self._hole(b)
        ax = self.ax
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.plot([x1, x2], [y1, y2], color="0.35", lw=1.2, zorder=5, ls="--" if dashed else "-")
        al = 0.45 if dashed else 1.0   # dashed=True：「后面某一步才插」的元件画成虚线、半透明
        fc = dict(R="#d9c7a3", C="#f2d27a", E="#6d8fb5", D="#555555", L="#ffffff", S="#bbbbbb",
                  P="#fff7c2", X="#c9d6c2")[kind]
        horiz = abs(x2 - x1) >= abs(y2 - y1)
        w, h = (0.9, 0.5) if horiz else (0.5, 0.9)
        if kind in "LP":
            ax.add_patch(Circle((mx, my), 0.42, fc=fc, ec="0.2", lw=1.0, zorder=6))
        else:
            ax.add_patch(FancyBboxPatch((mx - w / 2, my - h / 2), w, h, boxstyle="round,pad=0.05",
                                        fc=fc, ec="0.2", lw=1.0, zorder=6, alpha=al, ls="--" if dashed else "-"))
        if kind in "EDL":
            ax.text(x1 + 0.25 * (1 if x2 >= x1 else -1) if horiz else x1 + 0.3, y1 + (0.3 if horiz else 0), "+",
                    fontsize=8, ha="center", va="center", zorder=7, color=fs.C["bad"])
        if lab_side == "r":
            ax.text(max(x1, x2) + 0.3, my, label, ha="left", va="center", fontsize=fs_, zorder=7)
        elif lab_side == "l":
            ax.text(min(x1, x2) - 0.3, my, label, ha="right", va="center", fontsize=fs_, zorder=7)
        elif horiz:
            ax.text(mx, my + 0.45 * lab_side, label, ha="center", va="bottom" if lab_side > 0 else "top",
                    fontsize=fs_, zorder=7)
        else:
            ax.text(mx + 0.45 * lab_side, my, label, ha="left" if lab_side > 0 else "right",
                    va="center", fontsize=fs_, zorder=7)

    def chip(self, col, label, npin=8, names=None):
        """DIP 芯片跨在中间凹槽上：第 1 脚在 f 排第 col 列（左下，缺口朝左），逆时针数，
        第 npin 脚在 e 排第 col 列。脚号和脚名写在芯片体上。"""
        half = npin // 2
        ax = self.ax
        y0, y1 = BB_Y["f"] + 0.22, BB_Y["e"] - 0.22
        ax.add_patch(Rectangle((col - 0.5, y0), half, y1 - y0, fc="#2b2b2b", ec="k", zorder=6))
        ax.add_patch(Circle((col - 0.5, (y0 + y1) / 2), 0.28, fc="#f7f5ef", ec="none", zorder=7))
        ax.text(col + (half - 1) / 2, (y0 + y1) / 2, label, color="w", ha="center",
                va="center", fontsize=8.5, zorder=8)
        for i in range(half):
            for p, row in ((i + 1, "f"), (npin - i, "e")):
                x, y = col + i, BB_Y[row]
                ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=7))
                txt = str(p) + ("\n" + names[p] if names and p in names else "")
                ax.text(x, y0 + 0.06 if row == "f" else y1 - 0.06, txt, ha="center",
                        va="bottom" if row == "f" else "top", fontsize=5.5, color="w", zorder=8,
                        linespacing=0.85)

    def module(self, x, y, w, h, label, fc="#e6f0f8", fs_=8.5):
        """面包板外的模块（电池、信号源、Arduino 等），返回方框中心。"""
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec="0.3",
                                         lw=1.0, zorder=6))
        self.ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs_, zorder=7)
        return x + w / 2, y + h / 2

    def pin(self, x, y, text, ha="center", va="bottom", dy=0.15):
        """模块上的引脚：小黑点 + 引脚名。返回 (x, y)。"""
        self.ax.add_patch(Circle((x, y), 0.15, fc="0.15", ec="none", zorder=8))
        self.ax.text(x, y + dy if va == "bottom" else y - dy, text, ha=ha, va=va, fontsize=7, zorder=8)
        return x, y

    def probe(self, hole, text, dx=0.0, dy=0.9):
        """测量点：黄色圆圈写 ①②③，用细线指向孔。"""
        x, y = self.xy(hole)
        self.ax.plot([x, x + dx], [y, y + dy], color="0.35", lw=0.7, zorder=8)
        self.ax.add_patch(Circle((x + dx, y + dy), 0.36, fc=fs.C["hi"], ec="0.2", lw=0.7, zorder=9))
        self.ax.text(x + dx, y + dy, text, ha="center", va="center", fontsize=8, zorder=10)

    def note(self, x, y, text, **kw):
        kw.setdefault("fontsize", 8)
        self.ax.text(x, y, text, zorder=8, **kw)

    def legend(self, loc="lower center", y=-0.01):
        from matplotlib.lines import Line2D
        def lab(c, t):
            return t[:-1] + f"，{CNAME[c]}）" if t.endswith("）") else f"{t}（{CNAME[c]}）"
        hs = [Line2D([], [], color=WIRE[k][0], lw=2.4, label=lab(*WIRE[k])) for k in WIRE if k in self.used]
        self.ax.legend(handles=hs, loc=loc, ncol=len(hs), fontsize=8, frameon=False,
                       bbox_to_anchor=(0.5, y))

    def save(self, prefix, name):
        return fs.save(self.fig, prefix, name)
