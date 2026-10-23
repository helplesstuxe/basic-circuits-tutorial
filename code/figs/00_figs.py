"""画首页的知识点依赖图 img/00_dag.png，并校验 DAG、拓扑写作顺序和 4 条写作队列。

DAG 的唯一数据源就是本文件的 NODES / EDGES / QUEUES；notes/00-design.md 和 README.md 里的表必须与这里一致。
运行：/workspace/circuits-venv/bin/python code/figs/00_figs.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *  # noqa: F401,F403
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# 节点：编号 → (中文名, 所属线索)。线索决定方框颜色：pre 前置、op 运放线、pw 半导体与电源线、ctl 继电控制线
NODES = {
    "P1": ("元件速成", "pre"), "P2": ("半导体入门", "pre"), "P3": ("运放入门", "pre"),
    "01": ("反相放大", "op"), "02": ("同相放大", "op"), "03": ("电压跟随器", "op"), "04": ("差分放大", "op"),
    "05": ("精密整流", "op"), "06": ("桥式整流", "pw"), "07": ("射极跟随器", "pw"), "08": ("线性稳压", "pw"),
    "09": ("开关电源", "pw"), "10": ("稳压管稳压", "pw"), "11": ("过载保护", "op"), "12": ("积分电路", "op"),
    "13": ("微分电路", "op"), "14": ("电压比较器", "op"), "15": ("有源滤波", "op"), "16": ("振荡器", "op"),
    "17": ("自锁", "ctl"), "18": ("互锁", "ctl"), "19": ("星三角降压启动", "ctl"), "20": ("双控开关", "ctl"),
    # 扩展篇（2026-10-22 22:21 追加要求）
    "21": ("MOS 管开关", "ext"), "22": ("三极管继电器驱动", "ext"), "23": ("光耦隔离", "ext"),
    "24": ("隔离电源与数字隔离", "ext"), "25": ("H 桥电机驱动", "ext"), "26": ("上下拉与电平转换", "ext"),
}
# 边：前置 → 后继。理由写在 notes/00-design.md 的边表里（同样的顺序）
EDGES = [
    ("P1", "P2"), ("P1", "P3"), ("P3", "01"), ("01", "02"), ("02", "03"), ("01", "04"), ("02", "04"),
    ("01", "05"), ("P2", "05"), ("P1", "06"), ("P2", "06"), ("05", "06"), ("P2", "07"), ("03", "07"),
    ("P2", "10"), ("06", "10"), ("07", "08"), ("10", "08"), ("02", "08"), ("P1", "09"), ("P2", "09"),
    ("06", "09"), ("08", "09"), ("P1", "11"), ("P2", "11"), ("14", "11"), ("P1", "12"), ("01", "12"),
    ("P1", "13"), ("12", "13"), ("P3", "14"), ("P1", "15"), ("02", "15"), ("03", "15"), ("14", "16"),
    ("15", "16"), ("P1", "17"), ("17", "18"), ("P1", "19"), ("18", "19"), ("P1", "20"),
    # 扩展篇
    ("P1", "21"), ("P2", "21"), ("P1", "22"), ("P2", "22"), ("P2", "23"), ("22", "23"), ("06", "24"),
    ("09", "24"), ("23", "24"), ("21", "25"), ("22", "25"), ("P1", "26"), ("14", "26"), ("21", "26"),
]
# 4 名作者各自串行的写作队列（按拓扑序；每人写完一个节点回报一次）
QUEUES = {
    "作者 A": ["P3", "01", "02", "03", "04", "15", "16"],
    "作者 B": ["P2", "05", "06", "10", "08", "09", "24"],
    "作者 C": ["21", "14", "12", "13", "11", "25", "26"],
    "作者 D": ["P1", "17", "22", "18", "19", "07", "23", "20"],
}


def preds(n):
    return [a for a, b in EDGES if b == n]


def depth():
    """最长前置链长度（P1 = 0），用作 DAG 图的列号。"""
    memo = {}
    def f(n):
        if n not in memo:
            memo[n] = 0 if not preds(n) else 1 + max(f(p) for p in preds(n))
        return memo[n]
    return {n: f(n) for n in NODES}


def schedule():
    """模拟写作：每个节点占 1 个时间段；一个节点要等它所有前置节点在更早的时间段写完才能开工；
    每名作者按自己队列的顺序串行写。返回 {节点: 时间段}（从 1 开始）。"""
    done, slot, pos, t = {}, {}, {k: 0 for k in QUEUES}, 0
    while len(done) < len(NODES):
        t += 1
        assert t < 50, "队列死锁：某个节点的前置节点排在它后面"
        started = []
        for who, q in QUEUES.items():
            if pos[who] < len(q):
                n = q[pos[who]]
                if all(p in done for p in preds(n)):
                    started.append(n); pos[who] += 1
        for n in started:
            done[n] = t; slot[n] = t
    return slot


def checks():
    assert all(a in NODES and b in NODES for a, b in EDGES)
    assert len(set(EDGES)) == len(EDGES), "边重复"
    qn = [n for q in QUEUES.values() for n in q]
    assert sorted(qn) == sorted(NODES), "队列必须恰好覆盖全部节点各一次"
    d = depth()
    slot = schedule()
    order = sorted(NODES, key=lambda n: (slot[n], list(QUEUES).index(next(k for k, q in QUEUES.items() if n in q))))
    seen = set()
    for n in order:                      # 拓扑序校验：每个节点的前置都已出现
        assert all(p in seen for p in preds(n)), n
        seen.add(n)
    print(f"[数值] 节点 {len(NODES)} 个，边 {len(EDGES)} 条，最长前置链 {max(d.values()) + 1} 个节点")
    print("[数值] 拓扑写作顺序：", " → ".join(order))
    print(f"[数值] 4 人并行共需 {max(slot.values())} 个时间段")
    for who, q in QUEUES.items():
        print(f"  {who}（{len(q)} 个）：", "  ".join(f"{n}@t{slot[n]}" for n in q))
    return d, slot, order


FILL = {"pre": "#F0E442", "op": "#cfe3f2", "pw": "#fbe3b3", "ctl": "#c9eadf", "ext": "#f3dbe8"}   # 黄 前置、浅蓝 运放线、浅橙 电源线、浅绿 控制线、浅红紫 扩展篇
EDGEC = {"pre": "0.45", "op": C["vin"], "pw": C["vout"], "ctl": C["fb"], "ext": C["third"]}
TRACK = {"pre": "前置知识（增补）", "op": "运放与信号处理", "pw": "半导体与电源", "ctl": "继电-接触器控制与照明", "ext": "扩展篇（开关、驱动与隔离）"}


def draw(d):
    # 每列按线索排序后自上而下排；列间距 2.3，行间距 0.9
    cols = {}
    for n in NODES:
        cols.setdefault(d[n], []).append(n)
    order_track = ["pre", "op", "pw", "ctl", "ext"]
    pos = {}
    for c, ns in cols.items():
        ns.sort(key=lambda n: (order_track.index(NODES[n][1]), n))
        for i, n in enumerate(ns):
            pos[n] = (c * 2.3, -(i - (len(ns) - 1) / 2) * 0.95)
    W, H = 1.8, 0.7
    fig, ax = plt.subplots(figsize=(14, 5.6))
    ax.axis("off"); ax.grid(False); ax.set_aspect("equal")
    for a, b in EDGES:
        (x0, y0), (x1, y1) = pos[a], pos[b]
        far = d[b] - d[a] >= 3          # 跨 3 层以上的远程依赖（多来自 P1/P2）画成灰色细点线，减少视觉干扰
        ax.add_patch(FancyArrowPatch((x0 + W / 2, y0), (x1 - W / 2, y1), arrowstyle="-|>", mutation_scale=9,
                                     lw=0.7 if far else 0.9, color="0.65" if far else EDGEC[NODES[b][1]],
                                     ls=":" if far else "-", alpha=0.9, shrinkA=1, shrinkB=1,
                                     connectionstyle="arc3,rad=0.08", zorder=1))
    for n, (x, y) in pos.items():
        name, tr = NODES[n]
        ax.add_patch(FancyBboxPatch((x - W / 2, y - H / 2), W, H, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    fc=FILL[tr], ec=C["edge"], lw=1.0, zorder=2))
        ax.text(x, y, f"{n} {name}" if len(name) < 6 else f"{n}\n{name}", ha="center", va="center",
                fontsize=9.5 if len(name) < 6 else 8.5, linespacing=1.1, zorder=3)
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 1.1, max(xs) + 1.1); ax.set_ylim(min(ys) - 0.9, max(ys) + 0.6)
    for c in sorted(cols):
        ax.text(c * 2.3, max(ys) + 0.45, f"第 {c} 层", ha="center", va="bottom", fontsize=8, color="0.4")
    handles = [FancyBboxPatch((0, 0), 1, 1, fc=FILL[k], ec=C["edge"]) for k in order_track]
    ax.legend(handles, [TRACK[k] for k in order_track], loc="lower center", ncol=5, fontsize=9,
              bbox_to_anchor=(0.5, -0.04), frameon=False)
    ax.set_title("知识点依赖图（箭头：前置 → 后继，颜色随后继节点的线索；灰色点线 = 跨 3 层以上的远程依赖；列 = 最长前置链深度）", fontsize=10)
    return save(fig, "00", "00_dag.png")


if __name__ == "__main__":
    d, slot, order = checks()
    assert max(slot.values()) == 9, "队列调度应在 9 个时间段内完成（24 的前置链最长，9 段是下限）"
    draw(d)
