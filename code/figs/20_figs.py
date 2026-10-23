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


# ======================= page1–3 补充原理图（schem.py 国标元件） =======================
from schem import *
ACC = fs.C["bad"]
TY = 0.6                     # 两个触点 / 两根跨线离中线的高度


def spdt_at(d, com, side, up, color="black", label=None, lab_up=True):
    """单刀双掷开关：公共端 com，触点在 side 方向（+1 右、-1 左）1.2 处，上下各一；up=True 刀搭上触点。"""
    cx, cy = com
    tx = cx + 1.2 * side
    d += elm.Dot().at(com).color(color)
    d += elm.Dot(open=True).at((tx, cy + TY)).color(color)
    d += elm.Dot(open=True).at((tx, cy - TY)).color(color)
    ty = cy + (TY if up else -TY)
    d += elm.Line().at(com).to((tx - 0.12 * side, ty)).color(color)
    if label:
        d += elm.Label().at((cx + 0.6 * side, cy + (1.25 if lab_up else -1.25))).label(label, color=color)
    return (tx, cy + TY), (tx, cy - TY)


def two_way_sch(d, ox, oy, s1_up=True, s2_up=False, mode="ok", title=None):
    """双控电路原理图。mode："ok"；"swap" 跨线在 S2 端对调；"com" S2 公共端与下触点接反；
    "neutral" 开关在零线一侧；"broken" 跨线 A 断了。"""
    if title:
        d += elm.Label().at((ox - 0.8, oy + 2.1)).label(title, halign="left", fontsize=11)
    xL, x1, x2, xN = ox, ox + 1.2, ox + 7.2, ox + 11.4
    d += elm.Dot(open=True).at((xL, oy)).label("L", "left")
    if mode == "neutral":
        d += elm.Line().at((xL, oy)).right(0.3)
        d += LampX().right(2.0).label("灯", ofst=0.3)
        x1 = d.here[0] + 0.3
        x2 = x1 + 6.0
        d += elm.Line().right().tox(x1)
    else:
        d += elm.Line().at((xL, oy)).to((x1, oy))
    a1, b1 = spdt_at(d, (x1, oy), +1, s1_up, label="S1")
    cs = ACC if mode == "com" else "black"
    a2, b2 = spdt_at(d, (x2, oy), -1, s2_up, label="S2", color=cs)
    # 跨线
    if mode == "swap":
        xm = (a1[0] + a2[0]) / 2
        d += elm.Line().at(a1).to((xm - 0.4, a1[1]))
        d += elm.Line().to((xm + 0.4, b2[1])).color(ACC)
        d += elm.Line().to(b2).color(ACC)
        d += elm.Line().at(b1).to((xm - 0.4, b1[1]))
        d += elm.Line().to((xm + 0.4, a2[1])).color(ACC)
        d += elm.Line().to(a2).color(ACC)
        d += elm.Label().at((xm - 1.4, a1[1] + 0.35)).label("跨线 A", fontsize=9)
        d += elm.Label().at((xm - 1.4, b1[1] - 0.35)).label("跨线 B", fontsize=9)
        d += elm.Label().at((xm + 0.4, oy + 1.25)).label("在 S2 端对调", color=ACC, fontsize=9)
    elif mode == "com":
        d += elm.Line().at(a1).to(a2)
        d += elm.Label().at(((a1[0] + a2[0]) / 2, a1[1] + 0.35)).label("跨线 A", fontsize=9)
        xm = (b1[0] + b2[0]) / 2
        d += elm.Line().at(b1).to((xm, b1[1]))
        d += elm.Label().at((xm - 1.0, b1[1] - 0.35)).label("跨线 B", fontsize=9)
        d += elm.Line().at((xm, b1[1])).to((xm, oy - 1.5)).color(ACC)
        d += elm.Line().to((x2 + 0.5, oy - 1.5)).color(ACC)
        d += elm.Line().to((x2 + 0.5, oy)).color(ACC)
        d += elm.Line().to((x2, oy)).color(ACC)
        d += elm.Line().at(b2).to((b2[0], oy - 2.1)).color(ACC)
        d += elm.Line().to((x2 + 1.1, oy - 2.1)).color(ACC)
        d += elm.Line().to((x2 + 1.1, oy)).color(ACC)
        d += elm.Label().at((x2 + 1.2, oy - 2.5)).label("灯线接到了触点上，跨线 B 接到了公共端", color=ACC, fontsize=9)
    elif mode == "broken":
        xm = (a1[0] + a2[0]) / 2
        d += elm.Line().at(a1).to((xm - 0.25, a1[1]))
        d += elm.Line().at((xm + 0.25, a2[1])).to(a2)
        d += elm.Label().at((xm, a1[1])).label("×", color=ACC, fontsize=14)
        d += elm.Label().at((xm, a1[1] + 0.45)).label("跨线 A 断了", color=ACC, fontsize=9)
        d += elm.Line().at(b1).to(b2)
        d += elm.Label().at((xm, b1[1] - 0.35)).label("跨线 B", fontsize=9)
    else:
        d += elm.Line().at(a1).to(a2)
        d += elm.Line().at(b1).to(b2)
        d += elm.Label().at(((a1[0] + a2[0]) / 2, a1[1] + 0.35)).label("跨线 A", fontsize=9)
        d += elm.Label().at(((b1[0] + b2[0]) / 2, b1[1] - 0.35)).label("跨线 B", fontsize=9)
    # 右端
    xr = x2 + (1.1 if mode == "com" else 0.0)
    if mode == "neutral":
        d += elm.Line().at((x2, oy)).right().tox(x2 + 0.8)
        d += elm.Dot(open=True).label("N", "right")
        d += elm.Label().at((x2 + 1.0, oy - 0.9)).label("开关断的是零线", color=ACC, fontsize=9)
    else:
        d += elm.Line().at((xr, oy)).right(0.4)
        d += LampX().right(2.0).label("灯", ofst=0.3)
        d += elm.Line().right(0.4)
        d += elm.Dot(open=True).label("N", "right")


def two_switches():
    """图 20-p1-4：两个普通开关（a）串联（b）并联控制一盏灯。"""
    with drawing(fontsize=10) as d:
        d += elm.Label().at((-0.6, 1.8)).label("（a）串联：两个都合上灯才亮", halign="left", fontsize=11)
        d += elm.Dot(open=True).at((0, 0)).label("L", "left")
        d += elm.Line().right(0.4)
        d += elm.Switch().right().label("楼下开关", ofst=0.3)
        d += elm.Line().right(0.6)
        d += elm.Switch().right().label("楼上开关", ofst=0.3)
        d += elm.Line().right(0.6)
        d += LampX().right(2.0).label("灯", ofst=0.3)
        d += elm.Line().right(0.4)
        d += elm.Dot(open=True).label("N", "right")
        oy = -4.0
        d += elm.Label().at((-0.6, oy + 1.8)).label("（b）并联：只要一个合着灯就亮", halign="left", fontsize=11)
        d += elm.Dot(open=True).at((0, oy)).label("L", "left")
        d += elm.Line().right(0.6)
        a = d.here
        d += elm.Dot()
        d += elm.Switch().right().label("楼下开关", ofst=0.3)
        b = d.here
        d += elm.Dot()
        d += elm.Line().at(a).down(1.4)
        d += elm.Switch().right().label("楼上开关", "bottom", ofst=0.3)
        d += elm.Line().up(1.4)
        d += elm.Line().at(b).right(0.6)
        d += LampX().right(2.0).label("灯", ofst=0.3)
        d += elm.Line().right(0.4)
        d += elm.Dot(open=True).label("N", "right")
    print("[图 20-p1-4] 两个普通开关串联 / 并联")
    save_schem(d, P, "20_p1_4_two_switches.png")


def mistakes_sch():
    """图 20-p2-4：三种接错的原理图（开关都在出厂位置：S1 搭跨线 A，S2 搭跨线 B）。"""
    with drawing(fontsize=10) as d:
        two_way_sch(d, 0, 0, mode="swap", title="（a）跨线一端对调")
        two_way_sch(d, 0, -5.0, mode="com", title="（b）公共端接错：S2 的公共端和一个触点接反")
        two_way_sch(d, 0, -10.6, mode="neutral", title="（c）开关接在零线：灯在火线一侧")
    print("[图 20-p2-4] 三种接错：跨线对调、公共端接错、开关接在零线")
    save_schem(d, P, "20_p2_4_mistakes.png")


def lab_sch():
    """图 20-p2-5：低压实验。（a）第 2 步正确接法；（b）第 6 步模拟开关接在零线。标出红表笔测量点。"""
    def sw_pair(d, x1, oy, up1, up2):
        a1, b1 = spdt_at(d, (x1, oy), +1, up1, label="S1")
        a2, b2 = spdt_at(d, (x1 + 5.0, oy), -1, up2, label="S2")
        d += elm.Line().at(a1).to(a2); d += elm.Line().at(b1).to(b2)
        d += elm.Label().at(((a1[0] + a2[0]) / 2, a1[1] + 0.35)).label("跨线", fontsize=9)
        d += elm.Label().at(((b1[0] + b2[0]) / 2, b1[1] - 0.35)).label("跨线", fontsize=9)
        return x1 + 5.0
    with drawing(fontsize=10) as d:
        d += elm.Label().at((-1.2, 2.1)).label("（a）第 2 步：正确接法（开关在正极一侧）", halign="left", fontsize=11)
        d += elm.Dot(open=True).at((0, 0)).label("9 V 正极", "left")
        x2 = sw_pair(d, 0, 0, True, False)
        d += elm.Line().at((x2, 0)).right(0.4)
        d += elm.Resistor().right(1.8).label("1 kΩ", ofst=0.2)
        p = d.here
        d += elm.LED().right(1.8).label("LED", ofst=0.2)
        d += elm.Line().right(0.4)
        d += elm.Dot(open=True).label("9 V 负极", "right")
        d += elm.Dot().at(p).color(ACC)
        d += elm.Label().at((p[0], p[1] - 1.15)).label("测量点：LED 灭时接近 0 V", color=ACC, fontsize=9)
        oy = -4.6
        d += elm.Label().at((-1.2, oy + 2.1)).label("（b）第 6 步：模拟开关接在零线（开关在负极一侧）", halign="left", fontsize=11)
        d += elm.Dot(open=True).at((0, oy)).label("9 V 正极", "left")
        d += elm.Line().right(0.4)
        d += elm.Resistor().right(1.8).label("1 kΩ", ofst=0.2)
        p = d.here
        d += elm.LED().right(1.8).label("LED", ofst=0.2)
        d += elm.Line().right(0.4)
        x1 = d.here[0]
        x2 = sw_pair(d, x1, oy, True, False)
        d += elm.Line().at((x2, oy)).right(0.6)
        d += elm.Dot(open=True).label("9 V 负极", "right")
        d += elm.Dot().at(p).color(ACC)
        d += elm.Label().at((p[0], p[1] - 1.15)).label("测量点：LED 灭时接近 9 V", color=ACC, fontsize=9)
    print("[图 20-p2-5] 实验第 2 步与第 6 步；测量点 LED 灭时接近 0 V / 约 9 V（模型估算）")
    save_schem(d, P, "20_p2_5_lab.png")


def broken_sch():
    """图 20-p3-3：跨线 A 断了。只有两把刀都搭在跨线 B 上时灯才亮。"""
    with drawing(fontsize=10) as d:
        two_way_sch(d, 0, 0, s1_up=False, s2_up=False, mode="broken")
    print("[图 20-p3-3] 跨线 A 断：只有两把刀都在 B 上才亮")
    save_schem(d, P, "20_p3_3_broken.png")


def five_way_sch():
    """图 20-p3-4：练习 3 五地控制：两只双控开关在两头，中间三只中途开关（画在直通位置）。"""
    with drawing(fontsize=10) as d:
        d += elm.Dot(open=True).at((0, 0)).label("L", "left")
        d += elm.Line().right(0.8)
        a, b = spdt_at(d, (0.8, 0), +1, True, label="S1 双控")
        x = a[0]
        for k in range(3):
            d += elm.Line().at((x, TY)).right(0.8); d += elm.Line().at((x, -TY)).right(0.8)
            xa = x + 0.8; xb = xa + 1.4
            for yy in (TY, -TY):
                d += elm.Dot(open=True).at((xa, yy)).color(ACC); d += elm.Dot(open=True).at((xb, yy)).color(ACC)
                d += elm.Line().at((xa, yy)).to((xb, yy)).color(ACC)
            d += elm.Line().at((xa, TY)).to((xb, -TY)).color(ACC).linestyle(":")
            d += elm.Line().at((xa, -TY)).to((xb, TY)).color(ACC).linestyle(":")
            d += elm.Label().at(((xa + xb) / 2, 1.25)).label(f"S{k + 2} 中途", color=ACC)
            x = xb
        d += elm.Line().at((x, TY)).right(0.8); d += elm.Line().at((x, -TY)).right(0.8)
        a2, b2 = spdt_at(d, (x + 2.0, 0), -1, False, label="S5 双控")
        d += elm.Line().at((x + 2.0, 0)).right(0.4)
        d += LampX().right(2.0).label("灯", ofst=0.3)
        d += elm.Line().right(0.4)
        d += elm.Dot(open=True).label("N", "right")
        d += elm.Label().at((6.0, -1.5)).label("中途开关：实线 = 直通，点线 = 拨一下后的交叉", color=ACC, fontsize=9)
    print("[图 20-p3-4] 五地控制：2 只双控 + 3 只中途开关")
    save_schem(d, P, "20_p3_4_five_way.png")


two_switches()
mistakes_sch()
lab_sch()
broken_sch()
five_way_sch()
