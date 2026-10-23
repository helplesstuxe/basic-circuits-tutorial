"""20 双控开关：除 20_sim.py 那两张以外的所有配图。运行：python code/figs/20_figs.py
开关模型与 code/20_sim.py 相同：位置 0 = 出厂位置，S1 在 0 时接上面的触点，S2 在 0 时接下面的触点。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import figstyle as fs

P = "20"
K = fs.C["edge"]          # 普通导线颜色
LIVE = fs.C["bad"]        # 带电（连着火线）的导线
CUR = fs.C["cur"]         # 电流路径


def wire(ax, pts, color=K, lw=1.4, ls="-", z=2):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="round")


def dot(ax, p, open_=True):
    ax.add_patch(Circle(p, 0.07, fc="white" if open_ else K, ec=K, lw=1.2, zorder=5))


def lamp(ax, c, r=0.3, color=K):
    """国标灯符号：圆圈加 ×。"""
    ax.add_patch(Circle(c, r, fc="white", ec=color, lw=1.4, zorder=4))
    d = r * 0.7
    wire(ax, [(c[0] - d, c[1] - d), (c[0] + d, c[1] + d)], color=color, z=5)
    wire(ax, [(c[0] - d, c[1] + d), (c[0] + d, c[1] - d)], color=color, z=5)


def spdt(ax, com, t_up, t_dn, up, color=K):
    """单刀双掷：公共端 com，两个触点；up=True 时刀接上面的触点。"""
    for p in (com, t_up, t_dn):
        dot(ax, p)
    wire(ax, [com, t_up if up else t_dn], color=color, lw=2.0, z=4)


def two_way(ax, ox, oy, s1, s2, show_path=False, title=None, labels=True):
    """正确接法的双控电路，左上角是火线 L。返回灯亮不亮。"""
    L, N = (ox, oy), (ox, oy - 2.2)
    c1, u1, d1 = (ox + 1.2, oy), (ox + 2.2, oy + 0.6), (ox + 2.2, oy - 0.6)
    u2, d2, c2 = (ox + 4.0, oy + 0.6), (ox + 4.0, oy - 0.6), (ox + 5.0, oy)
    lx = ox + 6.0
    up1, up2 = (s1 == 0), (s2 == 1)            # S1 在 0 接上面；S2 在 1 接上面
    on = up1 == up2                             # 两把刀指向同一根跨线才通
    if show_path and on:                        # 先画一条粗的天蓝色电流路径垫在下面
        t = oy + 0.6 if up1 else oy - 0.6
        wire(ax, [L, c1, (ox + 2.2, t), (ox + 4.0, t), c2, (lx, oy), (lx, oy - 2.2), N], color=CUR, lw=6, z=1)
    wire(ax, [L, c1]); wire(ax, [u1, u2]); wire(ax, [d1, d2])
    wire(ax, [c2, (lx, oy), (lx, oy - 0.95)]); wire(ax, [(lx, oy - 1.55), (lx, oy - 2.2), N])
    spdt(ax, c1, u1, d1, up1); spdt(ax, c2, u2, d2, up2)
    lamp(ax, (lx, oy - 1.25))
    dot(ax, L); dot(ax, N)
    if on:
        ax.add_patch(Circle((lx, oy - 1.25), 0.42, fc=fs.C["hi"], ec="none", alpha=0.6, zorder=3))
    if labels:
        ax.text(L[0] - 0.12, L[1], "L 火线", ha="right", va="center", fontsize=10)
        ax.text(N[0] - 0.12, N[1], "N 零线", ha="right", va="center", fontsize=10)
        ax.text(ox + 3.1, oy + 0.7, "跨线 A", ha="center", va="bottom", fontsize=9)
        ax.text(ox + 3.1, oy - 0.7, "跨线 B", ha="center", va="top", fontsize=9)
        ax.text(lx + 0.45, oy - 1.25, "灯", va="center", fontsize=10)
    ax.text(ox + 1.6, oy + 0.95, f"S1（楼下）" + (f" = {s1}" if title else ""), ha="center", fontsize=9)
    ax.text(ox + 4.6, oy + 0.95, f"S2（楼上）" + (f" = {s2}" if title else ""), ha="center", fontsize=9)
    if title:
        ax.text(ox + 3.0, oy - 2.55, title, ha="center", va="top", fontsize=10)
    return on


def problem():
    """图 20-p1-1：只有一个开关的楼梯 vs 两头各一个开关。"""
    fig, ax = fs.diagram(8.4, 3.4)
    for ox, txt, both in ((0.3, "① 普通开关只装在楼下", False), (4.5, "② 双控：楼上楼下各一个", True)):
        steps = [(ox, 0.4)]
        for i in range(6):                      # 画一段楼梯
            x, y = steps[-1]
            steps += [(x + 0.5, y), (x + 0.5, y + 0.38)]
        wire(ax, steps, lw=1.6)
        ax.text(ox + 1.8, 3.15, txt, ha="center", fontsize=10)
        lamp(ax, (ox + 1.9, 2.75), r=0.18)
        ax.add_patch(Circle((ox + 1.9, 2.75), 0.3, fc=fs.C["hi"], ec="none", alpha=0.6, zorder=3))
        ax.add_patch(Rectangle((ox + 0.05, 0.75), 0.22, 0.32, fc="white", ec=K, lw=1.2))
        ax.text(ox + 0.4, 0.9, "开关", va="center", fontsize=9)
        if both:
            ax.add_patch(Rectangle((ox + 3.05, 3.0 - 0.6), 0.22, 0.32, fc="white", ec=K, lw=1.2))
            ax.text(ox + 3.0, 2.56, "开关", ha="right", va="center", fontsize=9)
            ax.text(ox + 1.9, 0.15, "在哪头都能开、能关", ha="center", fontsize=9, color=fs.C["good"])
        else:
            ax.text(ox + 3.15, 2.45, "楼上：没开关", ha="center", va="center", fontsize=9, color=fs.C["bad"])
            ax.text(ox + 1.9, 0.15, "上楼后只能开着灯不管", ha="center", fontsize=9, color=fs.C["bad"])
    fs.save(fig, P, "20_p1_1_problem.png")


def railway():
    """图 20-p1-2：铁路道岔类比。两个道岔指向同一条轨道，火车才过得去。"""
    fig, ax = fs.diagram(8.4, 2.6)
    for row, (a, b) in enumerate(((True, True), (True, False))):
        oy = 1.85 - row * 1.3
        ok = a == b
        ax.text(0.1, oy, "进站", va="center", fontsize=9)
        wire(ax, [(0.7, oy), (1.4, oy)], lw=2.2)
        wire(ax, [(2.2, oy + 0.3), (5.4, oy + 0.3)], lw=2.2); wire(ax, [(2.2, oy - 0.3), (5.4, oy - 0.3)], lw=2.2)
        wire(ax, [(1.4, oy), (2.2, oy + 0.3 if a else oy - 0.3)], color=fs.C["third"], lw=3)
        wire(ax, [(5.4, oy + 0.3 if b else oy - 0.3), (6.2, oy)], color=fs.C["third"], lw=3)
        wire(ax, [(6.2, oy), (6.9, oy)], lw=2.2)
        ax.text(1.8, oy + 0.42, "道岔 1", ha="center", fontsize=8); ax.text(5.8, oy + 0.42, "道岔 2", ha="center", fontsize=8)
        ax.text(7.0, oy, "出站：" + ("通" if ok else "不通"), va="center", fontsize=10,
                color=fs.C["good"] if ok else fs.C["bad"])
        ax.text(3.8, oy + 0.38, "上轨", ha="center", fontsize=8); ax.text(3.8, oy - 0.22, "下轨", ha="center", fontsize=8)
    fs.save(fig, P, "20_p1_2_railway.png")


def circuit():
    """图 20-p1-3：双控电路，两只单刀双掷开关加两根跨线。"""
    fig, ax = fs.diagram(8.0, 3.4, xlim=(-1.2, 6.8), ylim=(-2.6, 0.8 + 0.4 + 0.2))
    two_way(ax, 0, 0, 0, 1)
    fs.save(fig, P, "20_p1_3_circuit.png")


def path():
    """图 20-p2-1：同一个电路的两种状态，天蓝色是电流路径。"""
    fig, ax = fs.diagram(9.6, 3.6, xlim=(-1.2, 14.4), ylim=(-3.2, 1.4))
    a = two_way(ax, 0, 0, 1, 0, show_path=True, title="S1=1，S2=0：两把刀都指向跨线 B，灯亮")
    b = two_way(ax, 8.0, 0, 1, 1, show_path=True, title="再拨 S2：刀离开跨线 B，灯灭", labels=False)
    print(f"[图 20-p2-1] 左图灯亮={a}，右图灯亮={b}")
    fs.save(fig, P, "20_p2_1_path.png")


def neutral():
    """图 20-p3-1：灯灭时，开关断火线（左）和开关断零线（右）的对比。朱红色是带电导线。"""
    fig, ax = fs.diagram(9.6, 3.6, xlim=(-1.2, 14.4), ylim=(-3.3, 1.4))
    # 左：正确接法，状态 (0,0)，灯灭；带电的只有 L → S1 → 跨线 A
    two_way(ax, 0, 0, 0, 0)
    wire(ax, [(0, 0), (1.2, 0), (2.2, 0.6), (4.0, 0.6)], color=LIVE, lw=2.4, z=4)
    ax.text(6.0 + 0.45, -1.75, "灯头约 0 V", fontsize=9, color=fs.C["good"])
    ax.text(3.0, -2.55, "① 开关断火线：灯灭时灯头不带电", ha="center", va="top", fontsize=10)
    # 右：开关接在零线一侧，火线直接到灯
    ox = 8.0
    L, N = (ox, 0), (ox, -2.2)
    lx = ox + 6.0
    wire(ax, [L, (lx, 0), (lx, -0.95)], color=LIVE, lw=2.4, z=3)
    wire(ax, [(lx, -1.55), (lx, -2.2), (ox + 5.0, -2.2)], color=LIVE, lw=2.4, z=3)
    c1, u1, d1 = (ox + 5.0, -2.2), (ox + 4.0, -1.6), (ox + 4.0, -2.8)
    u2, d2, c2 = (ox + 2.2, -1.6), (ox + 2.2, -2.8), (ox + 1.2, -2.2)
    wire(ax, [u1, u2], color=LIVE, lw=2.4, z=3); wire(ax, [d1, d2]); wire(ax, [c2, N])
    spdt(ax, c1, u1, d1, True, color=LIVE); spdt(ax, c2, u2, d2, False)
    lamp(ax, (lx, -1.25), color=LIVE)
    dot(ax, L); dot(ax, N)
    ax.text(L[0] - 0.12, 0, "L", ha="right", va="center", fontsize=10)
    ax.text(N[0] - 0.12, -2.2, "N", ha="right", va="center", fontsize=10)
    ax.text(lx + 0.45, -0.8, "灯头 220 V", fontsize=9, color=LIVE)
    ax.text(ox + 3.1, -1.5, "开关在零线一侧", ha="center", va="bottom", fontsize=9)
    ax.text(ox + 3.0, 0.9, "② 开关断零线：灯同样会灭，但灯头仍带电", ha="center", fontsize=10, color=LIVE)
    ax.text(11.0, -3.05, "朱红色 = 连着火线的导线（两图都处在灯灭状态）", ha="center", fontsize=9)
    fs.save(fig, P, "20_p3_1_neutral.png")


def three_way():
    """图 20-p3-2：三地控制，中间加一只中途开关（四个端子，直通或交叉）。"""
    fig, ax = fs.diagram(9.0, 3.3, xlim=(-1.2, 10.4), ylim=(-2.7, 1.55))
    L, N = (0, 0), (0, -2.2)
    c1, u1, d1 = (1.0, 0), (1.9, 0.6), (1.9, -0.6)
    a1, b1, a2, b2 = (3.4, 0.6), (3.4, -0.6), (5.4, 0.6), (5.4, -0.6)
    u3, d3, c3 = (6.9, 0.6), (6.9, -0.6), (7.8, 0)
    lx = 8.8
    wire(ax, [L, c1]); wire(ax, [u1, a1]); wire(ax, [d1, b1]); wire(ax, [a2, u3]); wire(ax, [b2, d3])
    wire(ax, [c3, (lx, 0), (lx, -0.95)]); wire(ax, [(lx, -1.55), (lx, -2.2), N])
    spdt(ax, c1, u1, d1, True); spdt(ax, c3, u3, d3, False)
    ax.add_patch(Rectangle((3.15, -0.95), 2.5, 1.9, fc="none", ec=K, ls="--", lw=1.0))
    for p in (a1, b1, a2, b2):
        dot(ax, p)
    wire(ax, [a1, b2], lw=2.0, z=4); wire(ax, [b1, a2], lw=2.0, z=4)            # 交叉位置（实线）
    wire(ax, [a1, a2], color=fs.C["ref"], ls=":", lw=1.6); wire(ax, [b1, b2], color=fs.C["ref"], ls=":", lw=1.6)  # 直通位置
    lamp(ax, (lx, -1.25))
    ax.add_patch(Circle((lx, -1.25), 0.42, fc=fs.C["hi"], ec="none", alpha=0.6, zorder=3))   # 此刻 S1=0、S2 交叉、S3 接下触点：灯亮
    dot(ax, L); dot(ax, N)
    ax.text(-0.12, 0, "L", ha="right", va="center", fontsize=10); ax.text(-0.12, -2.2, "N", ha="right", va="center", fontsize=10)
    ax.text(1.45, 0.95, "S1 双控", ha="center", fontsize=9); ax.text(7.35, 0.95, "S3 双控", ha="center", fontsize=9)
    ax.text(4.4, 1.1, "S2 中途开关", ha="center", fontsize=9)
    ax.text(4.4, -1.2, "实线：交叉　点线：直通", ha="center", va="top", fontsize=8)
    ax.text(lx + 0.45, -1.25, "灯", va="center", fontsize=10)
    fs.save(fig, P, "20_p3_2_three_way.png")


if __name__ == "__main__":
    problem(); railway(); circuit(); path(); neutral(); three_way()


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

# ---------- page4 动手实验篇：9 V 双控 / 三地控制面包板 ----------
import itertools as _it

V_BAT, R1, V_LED = 9.0, 1000.0, 1.868            # 电池、限流电阻；红 LED 压降取 review/spice/20.md 的 SPICE 值
I_LED = (V_BAT - V_LED) / R1
print(f"[数值] LED 电流 ({V_BAT:.0f} − {V_LED:.2f}) / {R1 / 1000:.0f} kΩ = {I_LED * 1000:.2f} mA，1 kΩ 两端 {I_LED * R1:.2f} V")
assert abs(I_LED * 1000 - 7.13) < 0.01            # 与 SPICE 7.131 mA 一致


def _find_factory(links):
    par = {}
    def f(x):
        par.setdefault(x, x)
        while par[x] != x:
            x = par[x]
        return x
    for a, b in links:
        par[f(a)] = f(b)
    return f


def _lit(links):
    f = _find_factory(links)
    return f("LED+") == f("+9V") and f("LED-") == f("0V")


def _slide(bb, c, label):
    """三脚单刀双掷拨动开关插在 f 排 c−1、c、c+1（中间是 COM，以实测为准）。"""
    ax = bb.ax
    ax.add_patch(FancyBboxPatch((c - 1.35, -1.05), 2.7, 0.7, boxstyle="round,pad=0.05",
                                fc="#cfd8e3", ec="0.25", lw=1.0, zorder=6))
    ax.add_patch(Rectangle((c - 0.85, -0.85), 0.6, 0.3, fc="0.3", ec="none", zorder=7))   # 拨杆
    ax.text(c + 0.35, -0.7, label, ha="left", va="center", fontsize=7.5, zorder=8)
    for x in (c - 1, c, c + 1):
        bb._hole(f"f{x}")
    ax.text(c - 1, -0.15, "1", ha="center", va="bottom", fontsize=7, color="0.25", zorder=8)
    ax.text(c, -0.15, "COM", ha="center", va="bottom", fontsize=7, color="0.25", zorder=8)
    ax.text(c + 1, -0.15, "2", ha="center", va="bottom", fontsize=7, color="0.25", zorder=8)


def _grey_unused(bb):
    for t in bb.ax.texts:
        if t.get_text() == "（未用）":
            t.set_color("0.6"); t.set_fontweight("normal"); t.set_fontsize(8.5)
    for ln in bb.ax.lines:
        ys = ln.get_ydata()
        if len(ys) == 2 and ys[0] == ys[1] and ys[0] in (BB_Y["T+"] + 0.42, BB_Y["T-"] + 0.42):
            ln.set_color("0.75")


WIRE["pos"] = (fs.C["bad"], "+9 V")
WIRE["gnd"] = ("#000000", "0 V（电池负极）")
WIRE["sig"] = (fs.C["vin"], "跨线 A")
WIRE["fb"] = (fs.C["fb"], "跨线 B")
WIRE["out"] = (fs.C["vout"], "S2 公共端 → 1 kΩ")

# ---------- 图 20-p4-1：两地控制（page2 第六节第 2 步的正确接法） ----------
bb = Breadboard(30, "双控开关面包板俯视图（9 V 电池、两只三脚拨动开关、1 kΩ + 红 LED）",
                size=(10, 6.4), rails=("（未用）", "（未用）", "0 V", "+9 V"))
_grey_unused(bb)
_slide(bb, 6, "S1")
_slide(bb, 16, "S2")
bb.wire("j6", "B+6", "pos")                        # +9 V → S1 公共端
bb.wire("g5", "g17", "sig")                        # 跨线 A：S1 的 1 → S2 的 2（与原理篇仿真的正确接法相同）
bb.wire("h7", "h15", "fb")                         # 跨线 B：S1 的 2 → S2 的 1
bb.part("i16", "i21", "R1 1 kΩ", "R", lab_side=-1)
bb.part("h21", "h24", "LED", "L", lab_side=1)      # 长脚（阳极）在第 21 列
bb.wire("j24", "B-24", "gnd")
bb.module(0.6, -10.4, 3.2, 1.3, "9 V 电池", fc="#e6f0f8")
bb.wire((3.2, -9.1), "B+3", "pos")
bb.wire((1.4, -9.1), "B-1", "gnd")
bb.note(1.0, 3.6, "上半区不用。开关引脚以蜂鸣挡实测为准；\n测量点 M：第 21 列（R1 与 LED 长脚相接处）", va="center",
        bbox=dict(fc="#f7f5ef", ec="none", pad=1.5))
bb.ax.text(21, BB_Y["g"], "M", ha="center", va="center", fontsize=9, color="k", fontweight="bold", zorder=9,
           bbox=dict(fc="w", ec="0.3", boxstyle="circle,pad=0.15"))
bb.legend()
bb.save(P, "20_p4_1_breadboard.png")

# 按图 20-p4-1 的插法逐个列出连通关系，核对真值表：两亮两灭、拨任一只都翻转
def board2(s1, s2):
    L = [("+9V", "S1.COM"), ("S1.1", "S2.2"), ("S1.2", "S2.1"), ("S2.COM", "R"), ("R", "LED+"), ("LED-", "0V")]
    L += [("S1.COM", f"S1.{1 + s1}"), ("S2.COM", f"S2.{1 + s2}")]
    return _lit(L)
tab2 = {s: board2(*s) for s in _it.product((0, 1), repeat=2)}
assert sum(tab2.values()) == 2 and all(tab2[s] == bool(s[0] ^ s[1]) for s in tab2)
print("[数值] 两地控制：", "，".join(f"S1={a} S2={b} {'亮' if v else '灭'}" for (a, b), v in tab2.items()))

# ---------- 图 20-p4-2：扩展——三地控制，中间加一只中途开关 ----------
WIRE["sig"] = (fs.C["vin"], "跨线 A / C")
WIRE["fb"] = (fs.C["fb"], "跨线 B / D")
WIRE["neg"] = (fs.C["third"], "中途开关引线")
bb = Breadboard(38, "三地控制扩展：S1、S3 两只三脚拨动开关 + 中途开关 S2（9 V）",
                size=(11.5, 6.6), rails=("（未用）", "（未用）", "0 V", "+9 V"))
_grey_unused(bb)
_slide(bb, 6, "S1")
_slide(bb, 30, "S3")
bb.wire("j6", "B+6", "pos")
bb.wire("g5", "g14", "sig")                        # 跨线 A：S1 的 1 → 中途开关入 1
bb.wire("h7", "h16", "fb")                         # 跨线 B：S1 的 2 → 中途开关入 2
bb.wire("g20", "g31", "sig")                       # 跨线 C：中途开关出 1 → S3 的 2
bb.wire("h22", "h29", "fb")                        # 跨线 D：中途开关出 2 → S3 的 1
bb.part("i30", "i34", "R1 1 kΩ", "R", lab_side=-1)
bb.part("h34", "h37", "LED", "L", lab_side=1)
bb.wire("j37", "B-37", "gnd")
bb.module(12.4, -10.6, 11.2, 1.0, "S2 中途开关（六脚双刀双掷，外侧四脚对角交叉）", fc="#efe6f3")
for c, name in ((14, "入1"), (16, "入2"), (20, "出1"), (22, "出2")):
    bb.wire((c, -9.5), f"j{c}", "neg")
    bb.ax.text(c + 0.15, -9.0, name, ha="left", va="center", fontsize=7, zorder=8)
bb.module(0.6, -10.4, 3.2, 1.3, "9 V 电池", fc="#e6f0f8")
bb.wire((3.2, -9.1), "B+3", "pos")
bb.wire((1.4, -9.1), "B-1", "gnd")
bb.note(1.0, 3.6, "上半区不用；中途开关的四根引线可用鳄鱼夹线或焊好的杜邦线", va="center",
        bbox=dict(fc="#f7f5ef", ec="none", pad=1.5))
bb.legend()
_lg = bb.ax.get_legend(); _lg.set_loc("upper center"); _lg.set_bbox_to_anchor((0.5, 0.995))
bb.save(P, "20_p4_2_three_way.png")

def board3(s1, s2, s3):
    L = [("+9V", "S1.COM"), ("S1.1", "M.入1"), ("S1.2", "M.入2"), ("M.出1", "S3.2"), ("M.出2", "S3.1"),
         ("S3.COM", "R"), ("R", "LED+"), ("LED-", "0V")]
    L += [("S1.COM", f"S1.{1 + s1}"), ("S3.COM", f"S3.{1 + s3}")]
    L += [("M.入1", "M.出1"), ("M.入2", "M.出2")] if s2 == 0 else [("M.入1", "M.出2"), ("M.入2", "M.出1")]
    return _lit(L)
tab3 = {s: board3(*s) for s in _it.product((0, 1), repeat=3)}
assert sum(tab3.values()) == 4 and all(tab3[s] == bool(s[0] ^ s[1] ^ s[2]) for s in tab3)
for s in tab3:                                     # 任拨一只，灯都翻转
    for k in range(3):
        t = list(s); t[k] ^= 1
        assert tab3[s] != tab3[tuple(t)]
print("[数值] 三地控制 8 种组合亮 4 种，任拨一只都翻转；全 0 时", "亮" if tab3[(0, 0, 0)] else "灭")
