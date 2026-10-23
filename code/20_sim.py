# 20 双控开关的最小仿真：把开关和导线看成"谁和谁连通"，算出每种开关位置下灯亮不亮。
# A：正确接法的真值表；B：四种状态的状态图；C：三种常见接错；D：三地控制（加一只中途开关）。
import sys, os                                     # 下一行让 Python 找到 code/figs 里的共享画图样式
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))  # 把 code/figs 加进搜索路径
import itertools                                   # 列出所有开关组合
import matplotlib.pyplot as plt                    # 画图
import figstyle as fs                              # 全书统一的颜色、保存函数

def groups(wires):                                 # 输入"哪两个点连在一起"的列表，输出连通的点集合
    parent = {}                                    # 并查集：每个点记一个"代表"
    def find(x):                                   # 找 x 的代表
        parent.setdefault(x, x)                    # 第一次见到的点，代表就是它自己
        while parent[x] != x:                      # 一直往上找
            x = parent[x]
        return x
    for a, b in wires:                             # 每根导线或闭合的触点
        parent[find(a)] = find(b)                  # 把两边合并成一组
    return find                                    # 返回"找代表"的函数，代表相同就是连通

def spdt(name, pos):                               # 单刀双掷开关：公共端 COM 接到 1 号或 2 号触点
    return [(f"{name}.COM", f"{name}.{1 + pos}")]  # pos = 0 接 1 号，pos = 1 接 2 号

def lamp_state(wires):                             # 灯的两端一端通火线 L、一端通零线 N，灯就亮
    find = groups(wires)                           # 算连通关系
    top, bot = find("灯.上"), find("灯.下")          # 灯两端各属于哪一组
    on = {top, bot} == {find("L"), find("N")}      # 一端是 L 组、另一端是 N 组 → 有电流 → 亮
    live = find("L") in (top, bot)                 # 灯头有没有哪一端连着火线（灯灭时这就是触电隐患）
    return on, live                                # 返回（亮不亮，灯头带不带电）

def correct(s1, s2):                               # 正确接法：火线进 S1 公共端，S2 公共端出来去灯
    w = [("L", "S1.COM"), ("S2.COM", "灯.上"), ("灯.下", "N")]   # 火线、灯线、零线
    w += [("S1.1", "S2.2"), ("S1.2", "S2.1")]      # 两根跨线：A 连 S1.1 和 S2.2，B 连 S1.2 和 S2.1
    return w + spdt("S1", s1) + spdt("S2", s2)     # 加上两只开关此刻闭合的那一路

def swapped_travelers(s1, s2):                     # 接错 1：跨线在一端对调（A、B 互换）
    w = [("L", "S1.COM"), ("S2.COM", "灯.上"), ("灯.下", "N")]
    w += [("S1.1", "S2.1"), ("S1.2", "S2.2")]      # 跨线变成 1 对 1、2 对 2
    return w + spdt("S1", s1) + spdt("S2", s2)

def wrong_common(s1, s2):                          # 接错 2：S2 的公共端和一个触点接反了
    w = [("L", "S1.COM"), ("S2.1", "灯.上"), ("灯.下", "N")]     # 去灯的线错接在 S2.1 上
    w += [("S1.1", "S2.2"), ("S1.2", "S2.COM")]    # 跨线 B 错接在 S2 的公共端上
    return w + spdt("S1", s1) + spdt("S2", s2)

def switch_on_neutral(s1, s2):                     # 接错 3：火线直接进灯，开关串在零线一侧
    w = [("L", "灯.上"), ("灯.下", "S1.COM"), ("S2.COM", "N")]   # 开关断的是零线
    w += [("S1.1", "S2.2"), ("S1.2", "S2.1")]      # 跨线照常
    return w + spdt("S1", s1) + spdt("S2", s2)

STATES = list(itertools.product((0, 1), repeat=2)) # 四种组合 (0,0) (0,1) (1,0) (1,1)

print("[A] 正确接法真值表（0/1 = 开关在出厂位置/被拨过）")
for s1, s2 in STATES:                              # 逐个组合
    on, _ = lamp_state(correct(s1, s2))
    print(f"    S1={s1} S2={s2} → 灯{'亮' if on else '灭'}")
    assert on == bool(s1 ^ s2)                     # 检查：灯 = S1 异或 S2

def flips(wiring):                                 # 数一数：从每个状态拨一只开关，有几次灯会变
    n = 0
    for s1, s2 in STATES:
        now = lamp_state(wiring(s1, s2))[0]
        n += lamp_state(wiring(1 - s1, s2))[0] != now   # 拨 S1
        n += lamp_state(wiring(s1, 1 - s2))[0] != now   # 拨 S2
    return n                                       # 满分 8 次（4 个状态 × 2 只开关）

print(f"[B] 正确接法：拨一只开关灯就变的次数 = {flips(correct)} / 8")
assert flips(correct) == 8                         # 任何时候拨任何一只都管用

fig, ax = fs.diagram(6, 3.4)                       # 状态图：四个方框是四种状态，连线是"拨一只开关"
pos = {(0, 0): (1.4, 2.6), (1, 0): (4.6, 2.6), (0, 1): (1.4, 0.8), (1, 1): (4.6, 0.8)}
for (s1, s2), (x, y) in pos.items():               # 画四个方框，亮的状态填黄色
    on = lamp_state(correct(s1, s2))[0]
    fs.box(ax, x, y, f"S1={s1}  S2={s2}\n灯{'亮' if on else '灭'}", w=1.8, h=0.8,
           fc="#fff2a8" if on else "#e8e8e8")
fs.arrow(ax, (2.3, 2.7), (3.7, 2.7), "拨 S1"); fs.arrow(ax, (3.7, 2.5), (2.3, 2.5))
fs.arrow(ax, (2.3, 0.9), (3.7, 0.9), "拨 S1"); fs.arrow(ax, (3.7, 0.7), (2.3, 0.7))
fs.arrow(ax, (1.3, 2.2), (1.3, 1.2)); fs.arrow(ax, (1.5, 1.2), (1.5, 2.2))
fs.arrow(ax, (4.5, 2.2), (4.5, 1.2)); fs.arrow(ax, (4.7, 1.2), (4.7, 2.2))
ax.text(1.75, 1.7, "拨 S2", fontsize=9, va="center"); ax.text(4.85, 1.7, "拨 S2", fontsize=9, va="center")
fs.save(fig, "20", "20_p2_2_states.png")

print("[C] 三种接错")
rows = [("正确接法", correct), ("跨线一端对调", swapped_travelers),
        ("公共端接错", wrong_common), ("开关接在零线", switch_on_neutral)]
table = {}                                         # 记下每种接法、每个状态的结果，画图用
for name, wiring in rows:
    res = [lamp_state(wiring(s1, s2)) for s1, s2 in STATES]
    table[name] = res
    lit = sum(on for on, _ in res)                 # 四个状态里亮了几个
    danger = sum((not on) and live for on, live in res)  # 灯灭但灯头连着火线的状态数
    print(f"    {name}：亮 {lit}/4，拨开关有效 {flips(wiring)}/8，灯灭时灯头带电 {danger}/4")
assert flips(swapped_travelers) == 8               # 跨线对调：照样两地都能控制，只是亮灭位置反了
assert flips(wrong_common) < 8                     # 公共端接错：有时候拨开关不管用
assert flips(switch_on_neutral) == 8               # 开关接在零线：功能看起来完全正常……
assert sum((not on) and live for on, live in table["开关接在零线"]) == 2   # ……但灯灭时灯头仍带电

fig, ax = plt.subplots(figsize=(7, 2.8))           # 画成表格：行是接法，列是开关状态
ax.set_xlim(0, 4); ax.set_ylim(0, 4); ax.invert_yaxis(); ax.grid(False)
for j, (name, res) in enumerate(table.items()):
    for i, (on, live) in enumerate(res):
        bad = (not on) and live                    # 灯灭但带电，用朱红色框出来
        ax.add_patch(plt.Rectangle((i + 0.05, j + 0.08), 0.9, 0.84, fc="#fff2a8" if on else "#e8e8e8",
                                   ec=fs.C["bad"] if bad else "0.6", lw=2.2 if bad else 0.8))
        ax.text(i + 0.5, j + 0.5, ("亮" if on else "灭") + ("（灯头带电）" if bad else ""),
                ha="center", va="center", fontsize=9, color=fs.C["bad"] if bad else "k")
ax.set_xticks([0.5, 1.5, 2.5, 3.5], [f"S1={a} S2={b}" for a, b in STATES])
ax.set_yticks([0.5, 1.5, 2.5, 3.5], list(table))
ax.tick_params(length=0); [s.set_visible(False) for s in ax.spines.values()]
ax.xaxis.tick_top()
fs.save(fig, "20", "20_p2_3_mistakes.png")

def three_way(s1, s2, s3):                         # 三地控制：S1、S3 是双控开关，S2 是中途开关
    w = [("L", "S1.COM"), ("S3.COM", "灯.上"), ("灯.下", "N")]
    w += [("S1.1", "M.a1"), ("S1.2", "M.b1")]      # S1 的两个触点接中途开关的入口 a1、b1
    w += [("M.a2", "S3.2"), ("M.b2", "S3.1")]      # 中途开关的出口 a2、b2 接 S3
    w += [("M.a1", "M.a2"), ("M.b1", "M.b2")] if s2 == 0 else [("M.a1", "M.b2"), ("M.b1", "M.a2")]  # 直通或交叉
    return w + spdt("S1", s1) + spdt("S3", s3)

print("[D] 三地控制真值表")
for s in itertools.product((0, 1), repeat=3):     # 八种组合
    on, _ = lamp_state(three_way(*s))
    print(f"    S1={s[0]} 中途={s[1]} S3={s[2]} → 灯{'亮' if on else '灭'}")
    assert on == bool(s[0] ^ s[1] ^ s[2])          # 灯 = 三只开关的异或：拨任何一只都翻转
