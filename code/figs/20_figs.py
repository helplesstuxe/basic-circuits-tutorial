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
