"""各节点 page4（动手实验篇）面包板图配套的电路原理图。

用法（仓库根目录）：
    python code/figs/lab_schem.py            # 画全部已登记节点
    python code/figs/lab_schem.py P1 05      # 只画指定节点（键名见 NODES）
可重复运行：每次都覆盖同名 PNG，不动面包板图和其他图。

约定（后续节点照此添加）：
  * 每个节点写一个函数 node_NN()，里面画该节点 page4 每张面包板图对应的原理图，用 save_schem(d, "NN", "NN_p4_M_schem_xxx.png") 保存；
    M 接在该页已有 p4 图号最大值之后。然后在文件末尾的 NODES 字典里登记 "NN": node_NN。
  * 元件编号、数值、引脚名、测量点①②③、+5 V / GND（电池、轨道名）一律照抄面包板图（NN_figs.py 里 bb_* 调用的文字）；
    面包板图有多个分区时，在一张图里画成并排子图，每个子图上方写「A 区：…（第 x～y 列）」。
  * 通用小工具：lab() 元件名/数值、probe() 黄色测量点圆圈、colnote() 灰色「第 N 列」小字、title() 分区标题、note() 图底说明。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schem import *            # noqa: F401,F403  elm、drawing、save_schem、Coil、ContactNO、PushNO、C …
from schemdraw.elements import Element
from schemdraw.segments import SegmentCircle, SegmentText

GRAY = "#555555"


class Probe(Element):
    """测量点标记：黄色圆圈里写 ①②③（与面包板图 bb_probe 的样子一致）。用 .at(位置) 放置。"""
    def __init__(self, text="①", r=0.3, **kw):
        super().__init__(**kw)
        self.segments.append(SegmentCircle((0, 0), r, fill=C["hi"], lw=0.8))
        self.segments.append(SegmentText((0, 0), text, fontsize=11, align=("center", "center")))
        self.anchors["center"] = (0, 0)


def probe(d, node_xy, text, dx=-0.8, dy=0.0):
    """在节点 node_xy 旁画测量点圆圈，并用细线连到节点。"""
    x, y = node_xy
    d += elm.Line().at((x, y)).to((x + dx, y + dy)).color("#595959").linewidth(0.7)
    d += Probe(text).at((x + dx + (0.3 if dx > 0 else -0.3 if dx < 0 else 0), y + dy))


def colnote(d, xy, text, loc="right", ofst=0.15):
    """灰色小字，标出这根线在面包板上是哪一列（或哪一个孔）。"""
    x, y = xy
    ha = {"right": "left", "left": "right", "top": "center", "bottom": "center"}[loc]
    va = {"right": "center", "left": "center", "top": "bottom", "bottom": "top"}[loc]
    dx = {"right": ofst, "left": -ofst}.get(loc, 0)
    dy = {"top": ofst, "bottom": -ofst}.get(loc, 0)
    d += elm.Label().at((x + dx, y + dy)).label(text, fontsize=9, color=GRAY, halign=ha, valign=va)


def lab(d, xy, text, ha="left", fs_=11, color="black"):
    """元件名、数值：在 xy 处写字（ha 是水平对齐：left 写在右边，right 写在左边）。"""
    d += elm.Label().at(xy).label(text, fontsize=fs_, color=color, halign=ha, valign="center")


def title(d, xy, text):
    d += elm.Label().at(xy).label(text, fontsize=12, halign="center")


def note(d, xy, text):
    d += elm.Label().at(xy).label(text, fontsize=9.5, color="#333333", halign="left")


# ======================================================================================
# P1 元件速成：图 P1-p4-1（P1_p4_1_breadboard.png）→ 图 P1-p4-3（A 分压 / B RC 充放电 / C 继电器）
# 面包板连线依据 code/figs/P1_figs.py 的 p4_1_breadboard()：
#   A：+5 V→a3；R1 b3–b7；R2 c7–c11；a11→GND；RL e7–e11（后插）；① 第 7 列
#   B：SW c13(充)/c14(公共)/c15(放)；+5 V→a13；a15→GND；R e14–e18；C b18(+)–b19；a19→GND；② 第 18 列
#   C：+5 V→j18；SB i18–i21；KA 线圈+ g21、线圈− g24、COM g26、NO g28；1N4007 阴极 f21、阳极 f24；j24→GND；
#      +5 V→j26；LED i28(长脚)→i30；1k j30→GND；③ 第 21 列
# ======================================================================================
def node_P1():
    top, mid, bot = 4.0, 1.25, -1.5           # +5 V 线、中间节点、GND 线的 y
    with drawing(fontsize=11) as d:
        # ---------------- A 区：分压（第 3～11 列） ----------------
        xa = 0.0
        title(d, (xa + 1.2, top + 2.0), "A 区：分压（第 3～11 列）")
        d += elm.Vdd().at((xa, top)).label("+5 V")
        colnote(d, (xa, top - 0.2), "第 3 列", "left")
        d += elm.Resistor().endpoints((xa, top), (xa, mid))
        lab(d, (xa + 0.45, (top + mid) / 2), "R1 10k")
        d += elm.Dot().at((xa, mid))
        d += elm.Resistor().endpoints((xa, mid), (xa, bot))
        lab(d, (xa + 0.45, (mid + bot) / 2 - 0.3), "R2 10k")
        colnote(d, (xa, bot + 0.4), "第 11 列", "left")
        d += elm.Ground().at((xa, bot)).label("GND", "bottom")
        probe(d, (xa, mid), "①", dx=-0.9)
        colnote(d, (xa - 1.2, mid - 0.45), "第 7 列", "bottom", ofst=0.0)
        # RL：后插的负载，并在 R2 上（虚线表示「先不插」）
        xl = xa + 2.6
        d += elm.Line().endpoints((xa, mid), (xl, mid)).linestyle("--")
        d += elm.Resistor().endpoints((xl, mid), (xl, bot)).linestyle("--")
        lab(d, (xl + 0.45, (mid + bot) / 2), "RL\n（后插）")
        d += elm.Line().endpoints((xl, bot), (xa, bot)).linestyle("--")
        d += elm.Dot().at((xa, bot))

        # ---------------- B 区：RC 充放电（第 13～19 列） ----------------
        xb = 7.2
        title(d, (xb + 2.3, top + 2.0), "B 区：RC 充放电（第 13～19 列）")
        ys = mid + 0.6                                     # 开关公共端的高度
        d += (sw := elm.SwitchSpdt2().left().anchor("a").at((xb + 1.2, ys)))
        p_chg, p_dis, p_com = sw.absanchors["c"], sw.absanchors["b"], sw.absanchors["a"]
        lab(d, (xb + 0.35, ys + 1.15), "SW 拨动开关", fs_=10)
        # 「充」脚 → +5 V；「放」脚 → GND
        d += elm.Line().at(p_chg).to((xb, p_chg[1]))
        d += elm.Line().at((xb, p_chg[1])).to((xb, top))
        d += elm.Vdd().at((xb, top)).label("+5 V")
        d += elm.Line().at(p_dis).to((xb, p_dis[1]))
        d += elm.Line().at((xb, p_dis[1])).to((xb, bot))
        d += elm.Ground().at((xb, bot)).label("GND", "bottom")
        colnote(d, (xb, p_chg[1] + 0.25), "充\n第 13 列", "left")
        colnote(d, (xb, p_dis[1] - 0.35), "放\n第 15 列", "left")
        colnote(d, (p_com[0] + 0.05, ys - 0.3), "公共\n第 14 列", "bottom", ofst=0.0)
        # 公共端 → R → ② → C → GND
        xc = xb + 4.4
        d += elm.Resistor().at(p_com).to((xc, ys))
        lab(d, ((p_com[0] + xc) / 2, ys + 0.55), "R 10k", ha="center")
        d += elm.Dot().at((xc, ys))
        d += elm.Capacitor(polar=True).endpoints((xc, ys), (xc, bot))
        lab(d, (xc + 0.45, (ys + bot) / 2), "C 100μF")
        d += elm.Ground().at((xc, bot)).label("GND", "bottom")
        colnote(d, (xc + 0.15, bot + 0.3), "第 19 列", "right")
        probe(d, (xc, ys), "②", dx=0.9)
        colnote(d, (xc + 1.2, ys + 0.45), "第 18 列", "top", ofst=0.0)

        # ---------------- C 区：继电器（第 18～30 列） ----------------
        xk = 19.6                                          # 线圈那一竖列
        xd = xk - 2.9                                      # 续流二极管那一竖列
        xs = xk + 5.6                                      # 触点回路那一竖列
        title(d, (xk + 2.2, top + 2.0), "C 区：继电器（第 18～30 列）")
        d += elm.Vdd().at((xk, top + 0.6)).label("+5 V")
        colnote(d, (xk, top + 0.4), "第 18 列", "left")
        n3 = (xk, mid + 0.6)                               # ③：第 21 列 = 线圈+
        d += PushNO().endpoints((xk, top + 0.6), n3)
        lab(d, (xk - 0.35, (top + 0.6 + n3[1]) / 2 - 0.1), "SB 按钮", ha="right")
        d += elm.Dot().at(n3)
        d += Coil().endpoints(n3, (xk, bot))
        ym = (n3[1] + bot) / 2                             # 线圈中心高度
        lab(d, (xk + 0.45, ym + 0.55), "继电器 KA 线圈\n（G5V-1-DC5）", fs_=10)
        colnote(d, (xk + 0.05, n3[1] - 0.35), "线圈+", "right", ofst=0.05)
        colnote(d, (xk + 0.05, bot + 0.3), "线圈−", "right", ofst=0.05)
        d += elm.Dot().at((xk, bot))
        d += elm.Ground().at((xk, bot)).label("GND", "bottom")
        colnote(d, (xk + 0.35, bot - 0.4), "第 24 列", "right", ofst=0.0)
        # 1N4007 反向并在线圈上：阴极（竖杠）在第 21 列、阳极在第 24 列
        d += elm.Line().endpoints(n3, (xd, n3[1]))
        d += elm.Diode().endpoints((xd, bot), (xd, n3[1]))
        lab(d, (xd - 0.4, ym + 0.35), "1N4007", ha="right")
        lab(d, (xd - 0.4, ym - 0.25), "阴极朝上", ha="right", fs_=8.5, color=GRAY)
        d += elm.Line().endpoints((xd, bot), (xk, bot))
        # ③ 测量点
        d += elm.Line().at(n3).to((xk + 0.9, n3[1])).color("#595959").linewidth(0.7)
        d += Probe("③").at((xk + 1.2, n3[1]))
        colnote(d, (xk + 1.55, n3[1]), "第 21 列", "right", ofst=0.05)
        # 电流方向：按下时线圈电流向下；松开瞬间沿「线圈 → 第 24 列 → 1N4007 → 第 21 列」转圈
        d += elm.Arrow().at((xk - 0.4, n3[1] - 0.4)).to((xk - 0.4, bot + 0.4)).color(C["cur"]).linewidth(1.2)
        lab(d, (xk - 0.65, ym), "按下\n约 30 mA", ha="right", fs_=8.5, color=C["cur"])
        d += elm.Arrow().at((xd + 0.45, bot + 0.4)).to((xd + 0.45, n3[1] - 0.4)).color(C["cur"]).linewidth(1.2).linestyle("--")
        lab(d, (xd + 0.7, ym), "松开\n瞬间\n续流", ha="left", fs_=8.5, color=C["cur"])
        # 触点回路：+5 V → COM → NO → LED → 1k → GND（和线圈回路之间没有导线）
        yc1, yc2 = ym + 1.0, ym - 1.0                      # 触点上端（COM）、下端（NO）
        d += elm.Vdd().at((xs, top + 0.6)).label("+5 V")
        d += elm.Line().endpoints((xs, top + 0.6), (xs, yc1))
        d += ContactNO().endpoints((xs, yc1), (xs, yc2))
        lab(d, (xs + 0.6, ym + 0.1), "KA 常开触点", fs_=10)
        colnote(d, (xs - 0.1, yc1 + 0.1), "COM 第 26 列", "left", ofst=0.0)
        colnote(d, (xs - 0.1, yc2), "NO 第 28 列", "left", ofst=0.0)
        y_led = yc2 - 2.4
        d += elm.LED().endpoints((xs, yc2), (xs, y_led))
        lab(d, (xs + 1.0, (yc2 + y_led) / 2 - 0.1), "LED")
        colnote(d, (xs - 0.1, y_led), "第 30 列", "left", ofst=0.0)
        d += elm.Resistor().endpoints((xs, y_led), (xs, y_led - 2.2))
        lab(d, (xs + 0.45, y_led - 1.1), "1k")
        d += elm.Ground().at((xs, y_led - 2.2)).label("GND", "bottom")
        # 线圈与触点之间只有磁力联系（点线，不是导线）
        d += elm.Line().at((xk + 0.3, ym)).to((xs - 0.3, ym)).linestyle(":").color("#737373")
        lab(d, ((xk + xs) / 2 + 0.6, ym - 0.35), "磁力带动（不是导线）", ha="center", fs_=8.5, color=GRAY)

        for k, line in enumerate((
                "读图：一条线 = 一个节点（面包板上连通的一组孔）；实心圆点 = 导线在此相连；黄色圆圈①②③ = 测量点（黑表笔接 GND）。",
                "灰色小字 = 面包板列号。所有 +5 V 符号都是同一个 +5 V 轨，所有 GND 符号都是同一个 GND 轨。",
                "RL 画成虚线：先不插，量完空载再插。天蓝色箭头 = 电流方向；点线表示线圈靠磁力带动触点，两者之间没有导线。")):
            note(d, (-1.6, y_led - 3.3 - 0.6 * k), line)
    print("[图 P1-p4-3] A：+5 V–R1 10k–①(第 7 列)–R2 10k–GND，RL 并在 R2 上；B：SW 充→+5 V、放→GND、公共→R 10k→②(第 18 列)→C 100μF(+)→GND；"
          "C：+5 V→SB→③(第 21 列，线圈+)→KA 线圈→线圈−(第 24 列)→GND，1N4007 阴极第 21 列/阳极第 24 列；+5 V→COM→NO→LED→1k→GND")
    save_schem(d, "P1", "P1_p4_3_schem_lab.png")


# ======================================================================================
# P2 半导体入门：图 P2-p4-1（P2_p4_1_breadboard.png）→ 图 P2-p4-3（A 二极管 / B 三极管开关 + 电位器 / C 稳压管）
# 面包板连线依据 code/figs/P2_figs.py 的 p4_1_breadboard()：
#   电源：T1 +5 V、T2 GND；B1 +9 V（电池）、B2 GND；只有 T2-2↔B2-2 一根黑线，+5 V 与 +9 V 不相连
#   A：+5 V→a3；1k b3–b7；1N4148 阳极 c7、阴极 c10；a10→GND；① 第 7 列
#   B：蓝色控制线 a13→+5 V（改插 GND = 关）；RB 10k b13–b17；2N3904 E d16 / B d17 / C d18；a16→GND；
#      RC 220 c18–c22；LED 阳极 b25、阴极 b22；+5 V→a25；② 第 17 列、③ 第 18 列
#   电位器 10k：+ c27（+5 V→a27）、滑 c28、− c29（a29→GND）；④ 第 28 列
#   C：+9 V→j20；R 560 i20–i24；1N4733A 阴极 h24、阳极 h27；j27→GND；RL（后插）f24–f29、j29→GND；⑤ 第 24 列
# ======================================================================================
def node_P2():
    top, bot = 5.8, -1.5                       # 电源线、GND 线的 y
    ytl = top + 1.7                            # 分区标题的 y
    cur = dict(color=C["cur"])
    with drawing(fontsize=11) as d:
        # ---------------- A 区：二极管（第 3～10 列） ----------------
        xa, ya = 0.0, 2.0
        title(d, (xa + 0.6, ytl), "A 区：二极管（第 3～10 列）")
        d += elm.Vdd().at((xa, top)).label("+5 V")
        colnote(d, (xa, top - 0.25), "第 3 列", "left")
        d += elm.Resistor().endpoints((xa, top), (xa, ya))
        lab(d, (xa + 0.45, (top + ya) / 2), "1k")
        d += elm.Dot().at((xa, ya))
        d += elm.Diode().endpoints((xa, ya), (xa, bot))            # 阳极在上（第 7 列），阴极在下（第 10 列）
        lab(d, (xa + 0.45, (ya + bot) / 2 + 0.2), "1N4148")
        lab(d, (xa + 0.45, (ya + bot) / 2 - 0.4), "阴极朝下", fs_=8.5, color=GRAY)
        colnote(d, (xa, bot + 0.35), "第 10 列", "left")
        d += elm.Ground().at((xa, bot)).label("GND", "bottom")
        probe(d, (xa, ya), "①", dx=-0.9)
        colnote(d, (xa - 1.2, ya - 0.45), "第 7 列", "bottom", ofst=0.0)
        d += elm.Arrow().at((xa + 1.9, top - 0.6)).to((xa + 1.9, bot + 0.6)).color(C["cur"]).linewidth(1.2)
        lab(d, (xa + 2.1, (top + bot) / 2 + 1.2), "电流", fs_=8.5, **cur)

        # ---------------- B 区：三极管开关（第 13～25 列） ----------------
        xb = 5.6
        yb = 0.3                                                   # 基极高度
        title(d, (xb + 3.6, ytl), "B 区：三极管开关（第 13～25 列）")
        d += (sw := elm.SwitchSpdt2().left().anchor("a").at((xb + 1.0, yb)))
        p_on, p_off, p_com = sw.absanchors["c"], sw.absanchors["b"], sw.absanchors["a"]
        d += elm.Line().at(p_on).to((xb, p_on[1]))
        d += elm.Line().at((xb, p_on[1])).to((xb, top))
        d += elm.Vdd().at((xb, top)).label("+5 V")
        d += elm.Line().at(p_off).to((xb, p_off[1]))
        d += elm.Line().at((xb, p_off[1])).to((xb, bot))
        d += elm.Ground().at((xb, bot)).label("GND", "bottom")
        colnote(d, (xb, p_on[1] + 0.3), "开：插 +5 V", "left")
        colnote(d, (xb, p_off[1] - 0.3), "关：改插 GND", "left")
        lab(d, (xb - 0.3, yb + 2.3), "蓝色控制线\n（第 13 列）", ha="right", fs_=9.5, color="#0072B2")
        xn2 = p_com[0] + 3.0                                        # ② 基极节点（第 17 列）
        d += elm.Resistor().at(p_com).to((xn2, yb))
        lab(d, ((p_com[0] + xn2) / 2, yb + 0.55), "RB 10k", ha="center")
        d += elm.Dot().at((xn2, yb))
        d += (q := elm.BjtNpn(circle=True).anchor("base").at((xn2 + 0.6, yb)))
        d += elm.Line().at((xn2, yb)).to(q.absanchors["base"])
        pc, pe = q.absanchors["collector"], q.absanchors["emitter"]
        xc = pc[0]
        lab(d, (xc + 0.5, yb + 0.15), "2N3904", fs_=10)
        lab(d, (xn2 + 0.2, yb + 0.3), "B", fs_=8.5, color=GRAY)
        lab(d, (xc + 0.15, pc[1] + 0.25), "C", fs_=8.5, color=GRAY)
        lab(d, (xc + 0.15, pe[1] - 0.25), "E", fs_=8.5, color=GRAY)
        probe(d, (xn2, yb), "②", dx=0.0, dy=-1.0)
        colnote(d, (xn2 + 0.4, yb - 1.0), "第 17 列", "right", ofst=0.0)
        # 发射极 → GND（第 16 列）
        d += elm.Line().at(pe).to((xc, bot))
        d += elm.Ground().at((xc, bot)).label("GND", "bottom")
        colnote(d, (xc, bot + 0.35), "第 16 列", "right")
        # 集电极 ③（第 18 列）→ RC 220 → 第 22 列 → LED（阳极在上，第 25 列）→ +5 V
        y3, y22 = pc[1] + 0.4, pc[1] + 2.6
        d += elm.Line().at(pc).to((xc, y3))
        d += elm.Dot().at((xc, y3))
        probe(d, (xc, y3), "③", dx=-0.9)
        colnote(d, (xc - 1.2, y3 + 0.45), "第 18 列", "top", ofst=0.0)
        d += elm.Resistor().endpoints((xc, y22), (xc, y3))
        lab(d, (xc + 0.45, (y3 + y22) / 2), "RC 220")
        d += elm.LED().endpoints((xc, top), (xc, y22))
        lab(d, (xc + 1.0, (top + y22) / 2 - 0.1), "LED")
        colnote(d, (xc - 0.1, y22), "第 22 列", "left", ofst=0.05)
        d += elm.Vdd().at((xc, top)).label("+5 V")
        colnote(d, (xc, top - 0.25), "第 25 列", "left")
        d += elm.Arrow().at((xc + 1.9, top - 0.5)).to((xc + 1.9, pc[1])).color(C["cur"]).linewidth(1.2)
        lab(d, (xc + 2.05, top - 0.9), "开时\n电流", fs_=8.5, **cur)

        # ---------------- 电位器（第 27～29 列） ----------------
        xp = xc + 5.2
        title(d, (xp + 0.8, ytl), "电位器（第 27～29 列）")
        d += elm.Vdd().at((xp, top)).label("+5 V")
        d += elm.Line().at((xp, top)).to((xp, top - 1.0))
        d += (pot := elm.Potentiometer().endpoints((xp, top - 1.0), (xp, bot + 1.0)))
        d += elm.Line().at((xp, bot + 1.0)).to((xp, bot))
        d += elm.Ground().at((xp, bot)).label("GND", "bottom")
        lab(d, (xp - 0.45, (top + bot) / 2 + 0.6), "电位器\n10k", ha="right", fs_=10)
        colnote(d, (xp, top - 0.75), "+ 第 27 列", "left")
        colnote(d, (xp, bot + 0.75), "− 第 29 列", "left")
        tp = pot.absanchors["tap"]
        d += elm.Line().at(tp).to((tp[0] + 0.5, tp[1]))
        probe(d, (tp[0] + 0.5, tp[1]), "④", dx=0.6)
        colnote(d, (tp[0] + 1.2, tp[1] - 0.45), "滑 第 28 列", "bottom", ofst=0.0)

        # ---------------- C 区：稳压管（下半块第 20～29 列，9 V 电池） ----------------
        xz = xp + 5.6
        y5 = 2.0
        title(d, (xz + 1.0, ytl), "C 区：稳压管（下半块第 20～29 列）")
        d += elm.Vdd().at((xz, top)).label("+9 V（电池）")
        colnote(d, (xz, top - 0.25), "第 20 列", "left")
        d += elm.Resistor().endpoints((xz, top), (xz, y5))
        lab(d, (xz + 0.45, (top + y5) / 2), "R 560")
        d += elm.Dot().at((xz, y5))
        d += elm.Zener().endpoints((xz, bot), (xz, y5))              # 阴极在上（第 24 列），阳极在下（第 27 列）
        lab(d, (xz - 0.45, (y5 + bot) / 2 + 0.2), "1N4733A", ha="right")
        lab(d, (xz - 0.45, (y5 + bot) / 2 - 0.4), "阴极朝上", ha="right", fs_=8.5, color=GRAY)
        colnote(d, (xz, bot + 0.35), "第 27 列", "left")
        d += elm.Dot().at((xz, bot))
        d += elm.Ground().at((xz, bot)).label("GND", "bottom")
        probe(d, (xz, y5), "⑤", dx=-0.9)
        colnote(d, (xz - 1.2, y5 + 0.45), "第 24 列", "top", ofst=0.0)
        xl = xz + 2.6                                               # RL 后插：虚线
        d += elm.Line().endpoints((xz, y5), (xl, y5)).linestyle("--")
        d += elm.Resistor().endpoints((xl, y5), (xl, bot)).linestyle("--")
        lab(d, (xl + 0.45, (y5 + bot) / 2), "RL\n（后插）")
        colnote(d, (xl, bot + 0.35), "第 29 列", "right")
        d += elm.Line().endpoints((xl, bot), (xz, bot)).linestyle("--")
        d += elm.Arrow().at((xz + 0.45, top - 0.5)).to((xz + 0.45, y5 + 0.5)).color(C["cur"]).linewidth(1.2)
        lab(d, (xz + 0.6, top - 0.8), "电流", fs_=8.5, **cur)

        for k, line in enumerate((
                "读图：一条线 = 一个节点；实心圆点 = 导线相连；黄色圆圈①～⑤ = 测量点（黑表笔接 GND）；灰色小字 = 面包板列号。",
                "+5 V 来自电源模块（上面一组轨），+9 V 来自电池（下面一组轨），两者不相连；所有 GND 符号是同一个地（上下 GND 轨在第 2 列用黑线连通）。",
                "B 区的「开关」其实就是第 13 列那根蓝线换插 +5 V 或 GND；RL 画成虚线表示先不插。天蓝色箭头 = 电流方向。",
                "逐点测伏安特性时：拔掉 A 区 +5 V → 第 3 列的红线，改用蓝线把电位器滑动端④（第 28 列）接到第 3 列。")):
            note(d, (-1.6, bot - 2.2 - 0.6 * k), line)
    print("[图 P2-p4-3] A：+5 V–1k–①(第 7 列)–1N4148–GND；B：蓝线(+5 V/GND)–RB 10k–②基极(第 17 列)，2N3904 E→GND，"
          "③集电极(第 18 列)–RC 220–LED–+5 V；电位器 +5 V/④滑动端(第 28 列)/GND；C：+9 V–R 560–⑤(第 24 列)–1N4733A(阴极朝上)–GND，RL 并联后插")
    save_schem(d, "P2", "P2_p4_3_schem_lab.png")


# ======================================================================================
# P3 / 01 / 02 共用：LM358 放大电路 + 另一半跟随器 + 三种电源接法（原理图里 M = 中点地，V+ / V− = 电源轨）
# 三个节点的面包板是同一套布局（code/figs/P3_figs.py、01_figs.py、02_figs.py 的 p4_1_breadboard()）：
#   LM358 1～4 脚 f14～f17、8～5 脚 e14～e17；8 脚 a14→V+，4 脚 j17→V−；另一半 7、6 脚 c15–c16 短接，5 脚 a17→M
#   电位器 g3（端）/ g4（滑）/ g5（端，j5→M）；1.5 V 电池盒 + → j3、− → M；滑动端 i4→i9（蓝线）；① 第 9 列
#   反相（P3、01）：Rin/R1 h9–h12；j12→j15 接 2 脚；Rf i12–i14；3 脚 j16→M；② 第 12 列，③ 第 14 列
#   同相（02）：g9→g16 接 3 脚；R1 h10–h12、j10→M；j12→j15 接 2 脚；Rf i12–i14；② 第 12 列，③ 第 14 列
#   灰框（单 9 V）：a21→V+；Rm1 b21–b24；a24→M；Rm2 c24–c27；47μF d24(+)–d27；e27→V−（B1 第 29 列）
# ======================================================================================
BLUE, TEAL = "#0072B2", "#009E73"


def _pin(d, xy, n, dx=0.0, dy=0.22):
    """LM358 引脚号（小号深灰字）。"""
    d += elm.Label().at((xy[0] + dx, xy[1] + dy)).label(n, fontsize=9, color="#333333", halign="center", valign="center")


def _lm358_amp(d, kind, r_in, r_f, wire_note, ttl):
    """kind = "inv"（反相，P3/01）或 "non"（同相，02）。原点附近画放大电路，返回右边界 x。"""
    yM = -2.0                                         # 电位器、电池盒那一侧 M 的高度
    title(d, (6.5, 4.4), ttl)
    # 1.5 V 电池盒 + 电位器 10k（第 3～5 列）
    ytop = yM + 3.8
    d += elm.Battery().endpoints((0, yM), (0, ytop)).reverse()
    lab(d, (-0.45, (yM + ytop) / 2 + 0.3), "1.5 V\n电池盒", ha="right", fs_=10)
    lab(d, (0.3, (yM + ytop) / 2 + 0.75), "+", fs_=11)
    d += elm.Line().at((0, ytop)).to((2.0, ytop))
    colnote(d, (1.0, ytop), "第 3 列", "top")
    d += (pot := elm.Potentiometer().endpoints((2.0, ytop), (2.0, yM)))
    lab(d, (1.6, yM + 0.75), "电位器\n10k", ha="right", fs_=9.5)
    d += elm.Line().at((2.0, yM)).to((0, yM))
    d += elm.Dot().at((1.0, yM))
    d += elm.Ground().at((1.0, yM)).label("M", "bottom")
    colnote(d, (2.0, yM + 0.35), "第 5 列", "right")
    tp = pot.absanchors["tap"]
    y_in = tp[1]
    colnote(d, (tp[0] + 0.1, tp[1] - 0.3), "滑 第 4 列", "right", ofst=0.0)
    # 滑动端 → 蓝线（或 Rs）→ ① 第 9 列
    x1 = 5.6
    d += elm.Line().at(tp).to((x1, y_in)).color(BLUE).linewidth(2.0)
    lab(d, ((tp[0] + x1) / 2 + 0.3, y_in + 0.4), wire_note, ha="center", fs_=8.5, color=BLUE)
    d += elm.Dot().at((x1, y_in))
    probe(d, (x1, y_in), "①", dx=0.0, dy=-1.0)
    colnote(d, (x1 + 0.4, y_in - 1.0), "第 9 列", "right", ofst=0.0)
    xop = 10.0
    if kind == "inv":
        x2 = x1 + 3.0
        d += elm.Resistor().at((x1, y_in)).to((x2, y_in))
        lab(d, ((x1 + x2) / 2, y_in + 0.55), r_in, ha="center")
        d += (op := elm.Opamp(leads=True).theta(0).anchor("in1").at((xop, y_in)))
        p_m, p_p = op.absanchors["in1"], op.absanchors["in2"]
        d += elm.Line().at((x2, y_in)).to(p_m).color(TEAL).linewidth(1.6)
        lab(d, ((x2 + xop) / 2 - 0.05, y_in - 0.55), "蓝绿线\nj12→j15", ha="center", fs_=8, color=TEAL)
        # 3 脚（+）→ M（第 16 列）
        d += elm.Line().at(p_p).to((p_p[0] - 0.5, p_p[1]))
        d += elm.Ground().at((p_p[0] - 0.5, p_p[1])).label("M", "bottom")
        colnote(d, (p_p[0] - 0.75, p_p[1] - 0.3), "j16", "left", ofst=0.0)
        top_pin, bot_pin = op.absanchors["vd"], op.absanchors["vs"]
        yR = y_in + 2.6                                  # Rf 那一层（在上面）
    else:
        # 第 9 列 → 蓝线 g9→g16 → 3 脚（+，画在上面）
        d += (op := elm.Opamp(leads=True).theta(0).flip().anchor("in2").at((xop, y_in)))
        p_p, p_m = op.absanchors["in2"], op.absanchors["in1"]
        d += elm.Line().at((x1, y_in)).to(p_p).color(BLUE).linewidth(2.0)
        lab(d, ((x1 + xop) / 2 + 0.6, y_in + 0.35), "蓝线 g9→g16", ha="center", fs_=8.5, color=BLUE)
        x2 = xop - 1.4                                   # ② 第 12 列
        d += elm.Line().at(p_m).to((x2, p_m[1])).color(TEAL).linewidth(1.6)
        lab(d, ((x2 + xop) / 2 + 0.1, p_m[1] + 0.3), "j12→j15", ha="center", fs_=8, color=TEAL)
        top_pin, bot_pin = op.absanchors["vs"], op.absanchors["vd"]
        yR = p_m[1] - 2.8                                # Rf 那一层（在下面）
        # R1：第 12 列 → 第 10 列 → j10 → M
        xr1 = x2 - 1.6
        d += elm.Line().at((x2, p_m[1])).to((xr1, p_m[1]))
        d += elm.Resistor().endpoints((xr1, p_m[1]), (xr1, p_m[1] - 2.6))
        lab(d, (xr1 - 0.45, p_m[1] - 1.3), r_in, ha="right")
        d += elm.Ground().at((xr1, p_m[1] - 2.6)).label("M", "bottom")
        colnote(d, (xr1 + 0.1, p_m[1] - 2.35), "第 10 列", "right", ofst=0.05)
        y_in = p_m[1]                                    # 下面 ② 用
    d += elm.Dot().at((x2, y_in))
    if kind == "inv":
        probe(d, (x2, y_in), "②", dx=0.0, dy=-1.0)
        colnote(d, (x2 - 0.4, y_in - 1.0), "第 12 列", "left", ofst=0.0)
    else:
        probe(d, (x2, y_in), "②", dx=0.55, dy=-0.9)
        colnote(d, (x2 + 1.3, y_in - 1.2), "第 12 列", "right", ofst=0.0)
    # 电源脚：8 脚 → V+，4 脚 → V−
    d += elm.Line().at(top_pin).to((top_pin[0], top_pin[1] + 0.5))
    d += elm.Vdd().at((top_pin[0], top_pin[1] + 0.5)).label("V+")
    _pin(d, top_pin, "8", dx=0.25, dy=0.25)
    colnote(d, (top_pin[0] - 0.15, top_pin[1] + 0.35), "a14", "left", ofst=0.0)
    d += elm.Line().at(bot_pin).to((bot_pin[0], bot_pin[1] - 0.5))
    d += elm.Vss().at((bot_pin[0], bot_pin[1] - 0.5)).label("V−", "bottom")
    _pin(d, bot_pin, "4", dx=0.25, dy=-0.25)
    colnote(d, (bot_pin[0] - 0.15, bot_pin[1] - 0.35), "j17", "left", ofst=0.0)
    _pin(d, p_m, "2", dx=0.3, dy=0.22 if kind == "inv" else -0.22)
    _pin(d, p_p, "3", dx=0.3, dy=-0.22 if kind == "inv" else 0.22)
    po = op.absanchors["out"]
    _pin(d, po, "1", dx=-0.3, dy=0.22)
    lab(d, (po[0] - 0.4, po[1] + (0.9 if kind == "inv" else -0.9)), "LM358\nA 半边", ha="right", fs_=9)
    x3 = po[0] + 0.8
    d += elm.Line().at(po).to((x3, po[1]))
    d += elm.Dot().at((x3, po[1]))
    # Rf：第 12 列 ↔ 第 14 列（1 脚输出）
    d += elm.Line().at((x2, y_in)).to((x2, yR))
    d += elm.Resistor().at((x2, yR)).to((x3, yR))
    lab(d, ((x2 + x3) / 2, yR + (0.55 if kind == "inv" else -0.55)), r_f, ha="center")
    d += elm.Line().at((x3, yR)).to((x3, po[1]))
    d += elm.Line().at((x3, po[1])).to((x3 + 0.6, po[1]))
    probe(d, (x3 + 0.6, po[1]), "③", dx=0.7)
    colnote(d, (x3 + 1.6, po[1] - 0.45), "第 14 列", "bottom", ofst=0.0)
    return x3 + 2.4, yM


def _lm358_follower(d, x0, y0):
    """LM358 另一半（B 半边）：7 脚接 6 脚，5 脚接 M，接成跟随器免得乱跳。"""
    title(d, (x0 + 1.9, y0 + 4.0), "LM358 另一半（不用，接成跟随器）")
    d += (op := elm.Opamp(leads=True).theta(0).anchor("in2").at((x0 + 0.6, y0)))
    pm, pp, po = op.absanchors["in1"], op.absanchors["in2"], op.absanchors["out"]
    d += elm.Line().at(pp).to((x0, pp[1]))
    d += elm.Ground().at((x0, pp[1])).label("M", "bottom")
    colnote(d, (x0 - 0.15, pp[1] + 0.3), "a17", "left", ofst=0.0)
    d += elm.Line().at(po).to((po[0] + 0.4, po[1]))
    d += elm.Line().at((po[0] + 0.4, po[1])).to((po[0] + 0.4, pm[1] + 1.0)).color(TEAL).linewidth(1.6)
    d += elm.Line().at((po[0] + 0.4, pm[1] + 1.0)).to((pm[0] - 0.3, pm[1] + 1.0)).color(TEAL).linewidth(1.6)
    d += elm.Line().at((pm[0] - 0.3, pm[1] + 1.0)).to((pm[0] - 0.3, pm[1])).color(TEAL).linewidth(1.6)
    d += elm.Line().at((pm[0] - 0.3, pm[1])).to(pm)
    lab(d, ((pm[0] + po[0]) / 2, pm[1] + 1.35), "蓝绿短线 c15–c16", ha="center", fs_=8, color=TEAL)
    _pin(d, pm, "6", dx=0.3)
    _pin(d, pp, "5", dx=0.3, dy=-0.22)
    _pin(d, po, "7", dx=-0.3)
    lab(d, (op.absanchors["center"][0], pp[1] - 0.9), "8、4 脚和 A 半边共用", ha="center", fs_=8.5, color=GRAY)


def _supply(d, x, y, kind):
    """三种电源接法。kind = "dual" / "single" / "short"。(x, y) 是左上角附近。"""
    yt, yb = y, y - 4.4
    ym = (yt + yb) / 2
    if kind == "dual":
        title(d, (x + 1.6, yt + 1.6), "两节 9 V（双电源，灰框不插）")
        d += elm.Vdd().at((x, yt)).label("V+")
        d += elm.Battery().endpoints((x, ym), (x, yt)).reverse()
        lab(d, (x + 0.5, (ym + yt) / 2), "电池 A 9 V", fs_=10)
        d += elm.Dot().at((x, ym))
        d += elm.Battery().endpoints((x, yb), (x, ym)).reverse()
        lab(d, (x + 0.5, (ym + yb) / 2), "电池 B 9 V", fs_=10)
        d += elm.Vss().at((x, yb)).label("V−", "bottom")
        d += elm.Line().at((x, ym)).to((x - 1.4, ym))
        d += elm.Ground().at((x - 1.4, ym)).label("M", "bottom")
        lab(d, (x + 0.5, ym - 0.05), "A 的 − 与 B 的 + 拧在一起", fs_=8.5, color=GRAY)
        lab(d, (x + 0.5, yb - 1.1), "V+ 对 M = +9 V，V− 对 M = −9 V", fs_=8.5, color=GRAY)
        return
    d += elm.Vdd().at((x, yt)).label("V+")
    d += elm.Battery().endpoints((x, yb), (x, yt)).reverse()
    lab(d, (x - 0.5, ym), "9 V", ha="right", fs_=10)
    d += elm.Vss().at((x, yb)).label("V−（= 0 V）", "bottom")
    if kind == "single":
        title(d, (x + 2.6, yt + 1.6), "一节 9 V（插灰框，第 21～27 列）")
        xr, xc_ = x + 2.4, x + 4.6
        d += elm.Line().at((x, yt)).to((xr, yt))
        d += elm.Line().at((x, yb)).to((xc_, yb))
        d += elm.Resistor().endpoints((xr, yt), (xr, ym))
        lab(d, (xr + 0.45, (yt + ym) / 2), "Rm1 1k", fs_=10)
        colnote(d, (xr, yt), "第 21 列", "top")
        d += elm.Dot().at((xr, ym))
        d += elm.Resistor().endpoints((xr, ym), (xr, yb))
        lab(d, (xr + 0.45, (ym + yb) / 2), "Rm2 1k", fs_=10)
        colnote(d, (xr + 0.6, yb), "第 27 列", "bottom", ofst=0.1)
        d += elm.Dot().at((xr, yb))
        d += elm.Line().at((xr, ym)).to((xc_, ym))
        d += elm.Dot().at((xc_, ym))
        d += elm.Capacitor(polar=True).endpoints((xc_, ym), (xc_, yb))
        lab(d, (xc_ + 0.45, (ym + yb) / 2), "C 47μF", fs_=10)
        d += elm.Line().at((xc_, ym)).to((xc_ + 1.2, ym))
        d += elm.Ground().at((xc_ + 1.2, ym)).label("M", "bottom")
        colnote(d, ((xr + xc_) / 2, ym), "第 24 列", "top")
        lab(d, (x - 0.6, yb - 1.1), "M ≈ 4.5 V（对 V−），M 轨不接电池的任何一极", fs_=8.5, color=GRAY)
    else:
        xs_ = x + 2.4
        d += elm.Line().at((x, yb)).to((xs_, yb)).linewidth(2.2)
        d += elm.Line().at((xs_, yb)).to((xs_, ym)).linewidth(2.2)
        d += elm.Dot().at((xs_, ym))
        d += elm.Line().at((xs_, ym)).to((xs_ + 1.0, ym))
        d += elm.Ground().at((xs_ + 1.0, ym)).label("M", "bottom")
        lab(d, (xs_ + 0.3, (ym + yb) / 2 - 0.3), "黑线：M 轨 ↔ V− 轨", fs_=9)
    return


def _opamp_node(prefix, kind, r_in, r_f, wire_note, ttl, third, notes, fname, msg):
    with drawing(fontsize=11) as d:
        xr, yM = _lm358_amp(d, kind, r_in, r_f, wire_note, ttl)
        _lm358_follower(d, xr + 0.8, 0.4)
        ys = yM - (4.4 if kind == "inv" else 6.0)
        _supply(d, 1.5, ys, "dual")
        _supply(d, 9.5, ys, "single")
        if third:
            _supply(d, 19.0, ys, "short")
            title(d, (20.6, ys + 1.6), third)
        for k, line in enumerate(notes):
            note(d, (-2.0, ys - 6.4 - 0.6 * k), line)
    print(msg)
    save_schem(d, prefix, fname)


_OP_NOTES = (
    "读图：一条线 = 一个节点；实心圆点 = 导线相连；黄色圆圈①②③ = 测量点（黑表笔接 M）；灰色小字 = 面包板列号或孔位；小黑字 1～8 = LM358 引脚号。",
    "所有 M 符号都是同一个中点地（上下两条 M 轨在第 1 列用黑线连通），所有 V+、V− 符号分别是同一条电源轨；下面一排是给这三条轨供电的几种接法，每次只用一种。",
)


def node_P3():
    _opamp_node("P3", "inv", "Rin 10k", "Rf 100k", "蓝线 i4→i9", "反相 ×10（第 3～17 列）", None,
                _OP_NOTES + ("放大电路的第 12 列（②）就是 2 脚：面包板上它们隔了两列，靠底下那根蓝绿线 j12→j15 连成一个节点。",),
                "P3_p4_3_schem_lab.png",
                "[图 P3-p4-3] 电池盒+电位器→滑动端→蓝线→①(第 9 列)→Rin 10k→②(第 12 列)→2 脚；Rf 100k ②↔③(第 14 列，1 脚)；3 脚→M；8 脚 V+，4 脚 V−；"
                "B 半边 7-6 短接、5→M；电源：两节 9 V / 一节 9 V + Rm1、Rm2 1k + 47μF")


def node_01():
    _opamp_node("01", "inv", "R1 10k", "Rf 100k（47k / 10k）", "蓝线 i4→i9（第 10 步换 Rs 10k）", "反相放大（第 3～17 列）",
                "错误接法（第 16、17 步）",
                _OP_NOTES + ("Rf 先用 100 kΩ，第 7、8 步换 47 kΩ、10 kΩ；第 10 步把滑动端到①的蓝线换成 Rs 10k。错误接法：拔掉灰框，黑线把 M 轨直接接到 V− 轨。",),
                "01_p4_3_schem_lab.png",
                "[图 01-p4-3] 同 P3 反相接法，R1 10k、Rf 100k(47k/10k)，蓝线 i4→i9 第 10 步换 Rs；电源三种：双 9 V / 单 9 V 分压 / 错误接法 M 接 V−")


def node_02():
    _opamp_node("02", "non", "R1 10k", "Rf 20k（39k / 导线 / 100k）", "蓝线 i4→i9（第 10 步换 Rs 100k）", "同相放大（第 3～17 列）",
                "M 直接接电池负极（第 16～18 步）",
                _OP_NOTES + ("Rf 先用 20 kΩ，后面换 39 kΩ、导线、100 kΩ；第 10 步把滑动端到①的蓝线换成 Rs 100k。最后一种接法：拔掉灰框，黑线把 M 轨接到 V− 轨（例如 B2、B1 第 28 列）。",),
                "02_p4_3_schem_lab.png",
                "[图 02-p4-3] ①(第 9 列)→蓝线 g9→g16→3 脚；R1 10k 第 12 列→第 10 列→M；②(第 12 列)→2 脚；Rf 20k ②↔③(第 14 列，1 脚)；电源三种：双 9 V / 单 9 V 分压 / M 接 V−")


# ======================================================================================
# 03 电压跟随器：图 03-p4-1（03_p4_1_breadboard.png）→ 图 03-p4-3
# 依据 code/figs/03_figs.py 的 p4_1_breadboard()：T1 = V+，T2、B2 = M，B1 = V−；T2-1↔B2-1 黑线
#   分压：T1-6→a6；Rd1 10k b6–b10；Rd2 10k c10–c12；a12→M；① 第 10 列
#   e10→f10、g10→g16 蓝线 → 3 脚；a14→V+（8 脚）；j17→V−（4 脚）；h14→h15 蓝绿短线（1 脚→2 脚）；③ 第 14 列
#   B 半边：c15–c16、a17→M；RL 1k h22–h25，j25→M；负载线 j22→j14（或改插 j10）
#   灰框：B2-28↔B1-28 黑线（只在一节 9 V 时插）
# ======================================================================================
def _vplus(d, xy, text="V+"):
    d += elm.Vdd().at(xy).label(text)


def node_03():
    with drawing(fontsize=11) as d:
        title(d, (6.0, 5.6), "跟随器（第 6～25 列）")
        top, y1, bot = 3.6, 0.0, -3.0                     # V+ 线、① 节点、M 的 y
        x0 = 0.0
        _vplus(d, (x0, top))
        colnote(d, (x0 - 0.15, top - 0.25), "T1→a6（第 6 列）", "left", ofst=0.0)
        d += elm.Resistor().endpoints((x0, top), (x0, y1))
        lab(d, (x0 - 0.7, (top + y1) / 2), "Rd1 10k\n（47k / 拔掉）", ha="right", fs_=10)
        d += elm.Dot().at((x0, y1))
        d += elm.Resistor().endpoints((x0, y1), (x0, bot))
        lab(d, (x0 - 0.7, (y1 + bot) / 2), "Rd2 10k\n（47k / 100k / 拔掉）", ha="right", fs_=10)
        d += elm.Ground().at((x0, bot)).label("M", "bottom")
        colnote(d, (x0 + 0.15, bot + 0.3), "a12（第 12 列）", "right", ofst=0.0)
        probe(d, (x0, y1), "①", dx=-0.9)
        colnote(d, (x0 - 1.2, y1 - 0.45), "第 10 列", "bottom", ofst=0.0)
        # ① → 蓝线 → 3 脚（+，画在上面）
        xop = 5.0
        d += (op := elm.Opamp(leads=True).theta(0).flip().anchor("in2").at((xop, y1)))
        p_p, p_m, po = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
        d += elm.Line().at((x0, y1)).to(p_p).color(BLUE).linewidth(2.0)
        lab(d, ((x0 + xop) / 2 + 0.3, y1 + 0.35), "蓝线 e10→f10、g10→g16", ha="center", fs_=8.5, color=BLUE)
        top_pin, bot_pin = op.absanchors["vs"], op.absanchors["vd"]
        d += elm.Line().at(top_pin).to((top_pin[0], top_pin[1] + 0.5))
        _vplus(d, (top_pin[0], top_pin[1] + 0.5))
        _pin(d, top_pin, "8", dx=0.25, dy=0.25)
        colnote(d, (top_pin[0] - 0.15, top_pin[1] + 0.35), "a14", "left", ofst=0.0)
        d += elm.Line().at(bot_pin).to((bot_pin[0], bot_pin[1] - 0.5))
        d += elm.Vss().at((bot_pin[0], bot_pin[1] - 0.5)).label("V−", "bottom")
        _pin(d, bot_pin, "4", dx=0.25, dy=-0.25)
        colnote(d, (bot_pin[0] - 0.15, bot_pin[1] - 0.35), "j17", "left", ofst=0.0)
        _pin(d, p_p, "3", dx=0.3, dy=0.22)
        _pin(d, p_m, "2", dx=0.3, dy=-0.22)
        _pin(d, po, "1", dx=-0.3, dy=0.22)
        lab(d, (po[0] - 0.4, po[1] - 0.95), "LM358\nA 半边", ha="right", fs_=9)
        # 1 脚 → 2 脚：蓝绿短线 h14→h15（从下面绕回来）
        x3 = po[0] + 0.8
        d += elm.Line().at(po).to((x3, po[1]))
        d += elm.Dot().at((x3, po[1]))
        yf = bot_pin[1] - 1.9                            # 绕到 V− 符号下面，不和 4 脚的线交叉
        for a, b in (((x3, po[1]), (x3, yf)), ((x3, yf), (p_m[0] - 0.4, yf)), ((p_m[0] - 0.4, yf), (p_m[0] - 0.4, p_m[1])),
                     ((p_m[0] - 0.4, p_m[1]), p_m)):
            d += elm.Line().at(a).to(b).color(TEAL).linewidth(1.6)
        lab(d, ((p_m[0] + x3) / 2, yf - 0.35), "蓝绿短线 h14→h15（1 脚接 2 脚）", ha="center", fs_=8.5, color=TEAL)
        probe(d, (x3, po[1]), "③", dx=0.0, dy=1.0)
        colnote(d, (x3 + 0.4, po[1] + 1.0), "第 14 列", "right", ofst=0.0)
        # 负载：同一根负载线，一头固定在 j22（RL 上端），另一头插 j14 或 j10
        xL = x3 + 4.2
        d += elm.Line().at((x3, po[1])).to((xL, po[1])).color(BLUE).linewidth(2.0)
        lab(d, ((x3 + xL) / 2 - 0.4, po[1] - 0.75), "负载线插 j14\n（经跟随器）", ha="center", fs_=9, color=BLUE)
        yt = top + 0.9
        xt = 1.4
        d += elm.Dot().at((xt, y1))
        for a, b in (((xt, y1), (xt, yt)), ((xt, yt), (xL, yt)), ((xL, yt), (xL, po[1] + 0.05))):
            d += elm.Line().at(a).to(b).color(BLUE).linewidth(1.4).linestyle("--")
        lab(d, ((xt + xL) / 2 + 1.0, yt + 0.35), "或：负载线改插 j10（直接接分压点，不经跟随器）", ha="center", fs_=9, color=BLUE)
        d += elm.Dot().at((xL, po[1]))
        colnote(d, (xL + 0.15, po[1] + 0.3), "j22", "right", ofst=0.0)
        d += elm.Resistor().endpoints((xL, po[1]), (xL, bot))
        lab(d, (xL + 0.45, (po[1] + bot) / 2), "RL 1k（10k）\nh22–h25", fs_=10)
        d += elm.Ground().at((xL, bot)).label("M", "bottom")
        colnote(d, (xL + 0.15, bot + 0.3), "j25→M", "right", ofst=0.0)
        d += elm.Arrow().at((xL - 0.6, po[1] - 0.6)).to((xL - 0.6, bot + 0.7)).color(C["cur"]).linewidth(1.2)
        lab(d, (xL - 0.75, (po[1] + bot) / 2 - 0.6), "负载电流", ha="right", fs_=8.5, color=C["cur"])
        _lm358_follower(d, xL + 3.2, 0.4)
        ys = -6.6
        _supply(d, 1.5, ys, "dual")
        _supply(d, 11.0, ys, "short")
        title(d, (13.2, ys + 1.6), "一节 9 V（第 10～17 步，插灰框：B2–B1 第 28 列黑线）")
        for k, line in enumerate((
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；黄色圆圈①③ = 测量点（黑表笔接 M）；灰色小字 = 面包板列号或孔位；小黑字 1～8 = LM358 引脚号。",
            "所有 M 符号都是同一个中点地（T2、B2 两条 M 轨在第 1 列用黑线连通），所有 V+、V− 符号分别是同一条电源轨；下面一排是两种供电接法，每次只用一种。",
            "负载线只有一根：实线 = 插 j14（③，经跟随器），虚线 = 改插 j10（①，直接接分压点），两种插法不同时用。",
        )):
            note(d, (-3.0, ys - 6.4 - 0.6 * k), line)
    print("[图 03-p4-3] V+→Rd1 10k→①(第 10 列)→Rd2 10k→M；①→蓝线→3 脚；1 脚→h14→h15→2 脚；③(第 14 列)→负载线→RL 1k(j22–j25)→M；或负载线改插 j10")
    save_schem(d, "03", "03_p4_3_schem_lab.png")


# ======================================================================================
# 04 差分放大：图 04-p4-1（04_p4_1_breadboard.png）→ 图 04-p4-3
# 依据 code/figs/04_figs.py 的面包板图：T1 = V+，T2、B2 = M，B1 = V−；LM358 在第 14～17 列（同 01）
#   1.5 V 电池盒：+ → j3，− → B2-2（M）；电位器 A g3/g4（滑）/g5，j5→M；e3→f3 橙线；电位器 B c3/c4（滑）/c5，a5→M
#   A 滑片 i4→i9 蓝线 → ①（第 9 列）→ R1 10k h9–h12 → 第 12 列 → j12→j15 蓝绿线 → 2 脚；R2 100k i12–i14 → ③（第 14 列，1 脚）
#   B 滑片 d4→d20 蓝线，e20→f20 → ②（第 20 列）→ R3 10k g16–g20 → ④（第 16 列，3 脚）→ R4 100k i16–i19 → j19→M（第 13、14 步换 10k）
#   灰框（单 9 V）同 01
# ======================================================================================
def node_04():
    with drawing(fontsize=11) as d:
        title(d, (6.5, 6.6), "差分放大（第 3～20 列）")
        yMa = 1.2                                          # 电位器 A 下端 M 的高度
        xb, xp = -0.8, 2.0                                 # 电池盒、电位器那两竖列
        yt = 4.6
        d += elm.Battery().endpoints((xb, -3.9), (xb, yt)).reverse()
        lab(d, (xb - 0.45, 0.6), "1.5 V\n电池盒", ha="right", fs_=10)
        d += elm.Ground().at((xb, -3.9)).label("M", "bottom")
        colnote(d, (xb - 0.15, -3.6), "− → B2 第 2 列", "left", ofst=0.0)
        d += elm.Line().at((xb, yt)).to((xp, yt))
        colnote(d, (xb + 0.1, yt + 0.05), "+ → j3", "top")
        # 电位器 A（下半区 g3–g5）
        d += (pa := elm.Potentiometer().endpoints((xp, yt), (xp, yMa)))
        lab(d, (xp + 0.35, yt - 0.55), "电位器 A 10k", fs_=9.5)
        d += elm.Ground().at((xp, yMa)).label("M", "bottom")
        colnote(d, (xp + 0.15, yMa + 0.3), "j5→M", "right", ofst=0.0)
        # e3→f3 橙线：把 1.5 V 带到上半区，给电位器 B
        xo = 0.0
        d += elm.Dot().at((xo, yt))
        ybt, ybb = -0.8, -3.9
        d += elm.Line().at((xo, yt)).to((xo, ybt)).color(C["vout"]).linewidth(2.0)
        d += elm.Line().at((xo, ybt)).to((xp, ybt)).color(C["vout"]).linewidth(2.0)
        lab(d, ((xo + xp) / 2, ybt - 0.35), "橙线 e3→f3", ha="center", fs_=8.5, color=C["vout"])
        d += (pb := elm.Potentiometer().endpoints((xp, ybt), (xp, ybb)))
        lab(d, (xp + 0.35, ybt - 0.55), "电位器 B 10k", fs_=9.5)
        d += elm.Ground().at((xp, ybb)).label("M", "bottom")
        colnote(d, (xp + 0.15, ybb + 0.3), "a5→M", "right", ofst=0.0)
        ta, tb = pa.absanchors["tap"], pb.absanchors["tap"]
        colnote(d, (ta[0] + 0.1, ta[1] - 0.3), "滑 g4", "right", ofst=0.0)
        colnote(d, (tb[0] + 0.1, tb[1] - 0.3), "滑 c4", "right", ofst=0.0)
        # 运放：2 脚（−）在上
        xop = 11.0
        d += (op := elm.Opamp(leads=True).theta(0).anchor("in1").at((xop, ta[1])))
        p_m, p_p, po = op.absanchors["in1"], op.absanchors["in2"], op.absanchors["out"]
        y1 = ta[1]
        x1, x2 = 5.4, 8.4                                  # ① 第 9 列、第 12 列
        d += elm.Line().at(ta).to((x1, y1)).color(BLUE).linewidth(2.0)
        lab(d, ((ta[0] + x1) / 2 + 0.2, y1 + 0.35), "蓝线 i4→i9", ha="center", fs_=8.5, color=BLUE)
        d += elm.Dot().at((x1, y1))
        probe(d, (x1, y1), "①", dx=0.0, dy=-1.0)
        colnote(d, (x1 + 0.4, y1 - 1.0), "第 9 列", "right", ofst=0.0)
        d += elm.Resistor().at((x1, y1)).to((x2, y1))
        lab(d, ((x1 + x2) / 2, y1 + 0.55), "R1 10k", ha="center")
        d += elm.Dot().at((x2, y1))
        colnote(d, (x2, y1 - 0.2), "第 12 列", "bottom")
        d += elm.Line().at((x2, y1)).to(p_m).color(TEAL).linewidth(1.6)
        lab(d, ((x2 + xop) / 2 + 0.05, y1 + 0.3), "j12→j15", ha="center", fs_=8, color=TEAL)
        # R2：第 12 列 ↔ 第 14 列（1 脚）
        x3 = po[0] + 0.8
        yR = y1 + 1.9
        d += elm.Line().at((x2, y1)).to((x2, yR))
        d += elm.Resistor().at((x2, yR)).to((x3, yR))
        lab(d, ((x2 + x3) / 2, yR + 0.55), "R2 100k（i12–i14）", ha="center")
        d += elm.Line().at(po).to((x3, po[1]))
        d += elm.Line().at((x3, yR)).to((x3, po[1]))
        d += elm.Dot().at((x3, po[1]))
        d += elm.Line().at((x3, po[1])).to((x3 + 0.6, po[1]))
        probe(d, (x3 + 0.6, po[1]), "③", dx=0.7)
        colnote(d, (x3 + 1.6, po[1] - 0.45), "第 14 列", "bottom", ofst=0.0)
        # 电源脚
        top_pin, bot_pin = op.absanchors["vd"], op.absanchors["vs"]
        d += elm.Line().at(top_pin).to((top_pin[0], top_pin[1] + 0.5))
        d += elm.Vdd().at((top_pin[0], top_pin[1] + 0.5)).label("V+")
        _pin(d, top_pin, "8", dx=0.25, dy=0.25)
        colnote(d, (top_pin[0] - 0.15, top_pin[1] + 0.35), "a14", "left", ofst=0.0)
        d += elm.Line().at(bot_pin).to((bot_pin[0], bot_pin[1] - 0.5))
        d += elm.Vss().at((bot_pin[0], bot_pin[1] - 0.5)).label("V−", "bottom")
        _pin(d, bot_pin, "4", dx=0.25, dy=-0.25)
        colnote(d, (bot_pin[0] + 0.15, bot_pin[1] - 0.35), "j17", "right", ofst=0.0)
        _pin(d, p_m, "2", dx=0.3, dy=0.22)
        _pin(d, p_p, "3", dx=0.3, dy=-0.22)
        _pin(d, po, "1", dx=-0.3, dy=0.22)
        lab(d, (po[0] - 0.4, po[1] + 0.95), "LM358\nA 半边", ha="right", fs_=9)
        # B 滑片 → d4→d20 蓝线、e20→f20 → ② 第 20 列 → R3 10k → ④ 第 16 列 → 3 脚；R4 100k → j19 → M
        y2 = tb[1]
        x20, x16 = 5.4, 8.9
        d += elm.Line().at(tb).to((x20, y2)).color(BLUE).linewidth(2.0)
        lab(d, ((tb[0] + x20) / 2 + 0.3, y2 + 0.35), "蓝线 d4→d20\ne20→f20", ha="center", fs_=8.5, color=BLUE)
        d += elm.Dot().at((x20, y2))
        probe(d, (x20, y2), "②", dx=0.0, dy=-1.0)
        colnote(d, (x20 + 0.4, y2 - 1.0), "第 20 列", "right", ofst=0.0)
        d += elm.Resistor().at((x20, y2)).to((x16, y2))
        lab(d, ((x20 + x16) / 2, y2 + 0.55), "R3 10k（g16–g20）", ha="center", fs_=10)
        d += elm.Dot().at((x16, y2))
        d += elm.Line().at((x16, y2)).to((x16, p_p[1]))
        d += elm.Line().at((x16, p_p[1])).to(p_p)
        colnote(d, (x16 + 0.1, (y2 + p_p[1]) / 2), "第 16 列 = 3 脚", "right", ofst=0.0)
        probe(d, (x16, y2), "④", dx=1.0, dy=0.0)
        yb4 = y2 - 3.0
        d += elm.Resistor().endpoints((x16, y2), (x16, yb4))
        lab(d, (x16 - 0.45, (y2 + yb4) / 2), "R4 100k\n（i16–i19）", ha="right", fs_=10)
        d += elm.Line().at((x16, yb4)).to((x16, yb4 - 0.8)).linewidth(2.2)
        d += elm.Ground().at((x16, yb4 - 0.8)).label("M", "bottom")
        lab(d, (x16 + 0.3, yb4 - 0.35), "j19→M 黑线\n（第 13、14 步换成 10 kΩ）", fs_=8.5, color=GRAY)
        _lm358_follower(d, x3 + 4.2, 0.4)
        ys = -9.6
        _supply(d, 1.5, ys, "dual")
        _supply(d, 9.5, ys, "single")
        for k, line in enumerate((
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；黄色圆圈①～④ = 测量点（黑表笔接 M）；灰色小字 = 面包板列号或孔位；小黑字 1～8 = LM358 引脚号。",
            "所有 M 符号都是同一个中点地（上下两条 M 轨在第 1 列用黑线连通），所有 V+、V− 符号分别是同一条电源轨；下面一排是两种供电接法，每次只用一种。",
            "共模线（图中没画，第 8～14、18、19 步）：拔掉 i4–i9 和 e20–f20，插 j9→j20 把①②连成一点，再从 f20 拉一根长线到要加的共模电压。",
        )):
            note(d, (-3.0, ys - 6.4 - 0.6 * k), line)
    print("[图 04-p4-3] 1.5 V→电位器 A/B；A 滑片→①(第 9 列)→R1 10k→第 12 列→2 脚，R2 100k→③(第 14 列)；B 滑片→②(第 20 列)→R3 10k→④(第 16 列，3 脚)→R4 100k→j19→M")
    save_schem(d, "04", "04_p4_3_schem_lab.png")


# ======================================================================================
# 05 精密整流（LM741）：图 05-p4-1 → 图 05-p4-3（基本型），图 05-p4-2 → 图 05-p4-4（改进型）
# 依据 code/figs/05_figs.py 的 bb05()：tp = +9 V，tn = 0 V，bp = 0 V，bn = −9 V；tn29↔bp29
#   LM741 在第 12～15 列：a13→+9 V（7 脚），j15→−9 V（4 脚）；RA 8.2k g5–g9，h5→+9 V（改进型 / 输入为负：→ −9 V）
#   RB 100 j9→bp9；Vi 第 9 列下半区；g13（2 脚）→e8；D1 阳极 c14（6 脚）、阴极 c11；RL 10k a11→tn11；Vo 第 11 列上半区
#   基本型：i9→i14（→3 脚），b8→b11；改进型：g14→bp14，R1 10k h9–h13，D2 阳极 d8、阴极 d14，Rf 20k b8–b11
# ======================================================================================
PURPLE = C["third"]


class Ring(Element):
    """红紫色空心圆圈：面包板图里 bb.probe 的测量点（Vi、Vo、6 脚、V_B …），旁边写名字。"""
    def __init__(self, r=0.17, **kw):
        super().__init__(**kw)
        self.segments.append(SegmentCircle((0, 0), r, fill="white", color=PURPLE, lw=1.6))
        self.anchors["center"] = (0, 0)


def ring(d, node_xy, text, dx=-0.8, dy=0.0, ha=None):
    """测量点：从节点拉一根细线到红紫色圆圈，圆圈旁写名字（与面包板图一致）。"""
    x, y = node_xy
    cx, cy = x + dx, y + dy
    d += elm.Line().at((x, y)).to((cx, cy)).color("#595959").linewidth(0.7)
    d += Ring().at((cx, cy))
    if ha is None:
        ha = "right" if dx < 0 else "left"
    off = -0.3 if ha == "right" else 0.3
    if ha == "center":
        d += elm.Label().at((cx, cy + (0.42 if dy >= 0 else -0.42))).label(text, fontsize=10.5, color=PURPLE, halign="center", valign="center")
    else:
        d += elm.Label().at((cx + off, cy)).label(text, fontsize=10.5, color=PURPLE, halign=ha, valign="center")


def _bat_pm9(d, x, y):
    """两节 9 V 串联：电池① 正极 → +9 V 轨（tp1），相接处 → 0 V 轨（tn2），电池② 负极 → −9 V 轨（bn1）。"""
    yt, yb = y, y - 4.4
    ym = (yt + yb) / 2
    title(d, (x + 1.2, yt + 1.5), "电源：两节 9 V 串联")
    d += elm.Vdd().at((x, yt)).label("+9 V")
    d += elm.Battery().endpoints((x, ym), (x, yt)).reverse()
    lab(d, (x + 0.5, (ym + yt) / 2), "电池① 9 V", fs_=10)
    d += elm.Dot().at((x, ym))
    d += elm.Battery().endpoints((x, yb), (x, ym)).reverse()
    lab(d, (x + 0.5, (ym + yb) / 2), "电池② 9 V", fs_=10)
    d += elm.Vss().at((x, yb)).label("−9 V", "bottom")
    d += elm.Line().at((x, ym)).to((x - 1.4, ym))
    d += elm.Ground().at((x - 1.4, ym)).label("0 V", "bottom")
    colnote(d, (x + 0.15, yt - 0.3), "正极 → tp1（+9 V 轨）", "right", ofst=0.0)
    colnote(d, (x + 0.5, ym - 0.05), "相接处 → tn2（0 V 轨）", "right", ofst=0.0)
    colnote(d, (x + 0.15, yb + 0.3), "负极 → bn1（−9 V 轨）", "right", ofst=0.0)
    lab(d, (x - 1.0, yb - 1.2), "上、下两条 0 V 轨在第 29 列用黑线连通", fs_=8.5, color=GRAY)


def _lm741_pwr(d, op, top_is="vd"):
    """LM741 电源脚：7 脚 → +9 V（a13），4 脚 → −9 V（j15）。top_is 是画在上面的那个电源锚点名。"""
    top_pin = op.absanchors[top_is]
    bot_pin = op.absanchors["vs" if top_is == "vd" else "vd"]
    d += elm.Line().at(top_pin).to((top_pin[0], top_pin[1] + 0.5))
    d += elm.Vdd().at((top_pin[0], top_pin[1] + 0.5)).label("+9 V")
    _pin(d, top_pin, "7", dx=0.25, dy=0.25)
    colnote(d, (top_pin[0] - 0.15, top_pin[1] + 0.35), "a13", "left", ofst=0.0)
    d += elm.Line().at(bot_pin).to((bot_pin[0], bot_pin[1] - 0.5))
    d += elm.Vss().at((bot_pin[0], bot_pin[1] - 0.5)).label("−9 V", "bottom")
    _pin(d, bot_pin, "4", dx=0.25, dy=-0.25)
    colnote(d, (bot_pin[0] - 0.15, bot_pin[1] - 0.35), "j15", "left", ofst=0.0)
    return top_pin, bot_pin


_N05 = (
    "读图：一条线 = 一个节点；实心圆点 = 导线相连；红紫色圆圈 = 测量点（与面包板图同名，黑表笔接 0 V）；灰色小字 = 面包板列号或孔位；小黑字 = LM741 引脚号（1、5、8 脚不接）。",
    "二极管符号的三角形指向阴极（竖杠 = 实物上的色环）；所有 0 V 符号是同一个地（两条 0 V 轨连通），+9 V、−9 V 符号分别是同一条电源轨。",
)


def node_05():
    # ---------------- 图 05-p4-3：基本型 ----------------
    with drawing(fontsize=11) as d:
        title(d, (6.5, 5.8), "基本型精密整流（输入为正的接法）")
        top, y1, bot = 3.6, 0.0, -3.0
        x0 = 0.0
        d += elm.Vdd().at((x0, top)).label("+9 V")
        colnote(d, (x0 - 0.15, top - 0.3), "h5→+9 V 轨\n（输入改负：改插 −9 V 轨）", "left", ofst=0.0)
        d += elm.Resistor().endpoints((x0, top), (x0, y1))
        lab(d, (x0 + 0.45, (top + y1) / 2), "RA 8.2k\n（g5–g9）", fs_=10)
        d += elm.Dot().at((x0, y1))
        d += elm.Resistor().endpoints((x0, y1), (x0, bot))
        lab(d, (x0 + 0.45, (y1 + bot) / 2), "RB 100", fs_=10)
        d += elm.Ground().at((x0, bot)).label("0 V", "bottom")
        colnote(d, (x0 - 0.15, bot + 0.3), "j9→下方 0 V 轨", "left", ofst=0.0)
        ring(d, (x0, y1), "Vi", dx=-0.9)
        colnote(d, (x0 - 0.9, y1 - 0.3), "第 9 列下半", "bottom", ofst=0.0)
        xop = 5.0
        d += (op := elm.Opamp(leads=True).theta(0).flip().anchor("in2").at((xop, y1)))
        p_p, p_m, po = op.absanchors["in2"], op.absanchors["in1"], op.absanchors["out"]
        d += elm.Line().at((x0, y1)).to(p_p).color(TEAL).linewidth(1.8)
        lab(d, ((x0 + xop) / 2 + 0.4, y1 + 0.35), "蓝绿线 i9→i14", ha="center", fs_=8.5, color=TEAL)
        _, bot_pin = _lm741_pwr(d, op, "vs")
        _pin(d, p_p, "3", dx=0.3, dy=0.22)
        _pin(d, p_m, "2", dx=0.3, dy=-0.22)
        _pin(d, po, "6", dx=-0.3, dy=0.22)
        lab(d, (po[0] - 0.4, po[1] - 0.95), "LM741", ha="right", fs_=9.5)
        x6 = po[0] + 0.8
        xo = x6 + 3.4
        d += elm.Line().at(po).to((x6, po[1]))
        d += elm.Dot().at((x6, po[1]))
        ring(d, (x6, po[1]), "6 脚", dx=0.0, dy=1.0, ha="center")
        colnote(d, (x6 - 0.15, po[1] + 0.25), "第 14 列", "left", ofst=0.0)
        d += elm.Diode().at((x6, po[1])).to((xo, po[1]))
        lab(d, ((x6 + xo) / 2, po[1] + 0.6), "D1 1N4148", ha="center", fs_=10)
        lab(d, ((x6 + xo) / 2, po[1] - 0.55), "阳极 c14 → 阴极 c11\n（色环在第 11 列）", ha="center", fs_=8.5, color=GRAY)
        d += elm.Dot().at((xo, po[1]))
        ring(d, (xo, po[1]), "Vo", dx=0.0, dy=1.0, ha="center")
        colnote(d, (xo + 0.15, po[1] + 0.25), "第 11 列上半", "right", ofst=0.0)
        xr = xo + 2.6
        d += elm.Line().at((xo, po[1])).to((xr, po[1]))
        d += elm.Resistor().endpoints((xr, po[1]), (xr, bot))
        lab(d, (xr + 0.45, (po[1] + bot) / 2), "RL 10k", fs_=10)
        d += elm.Ground().at((xr, bot)).label("0 V", "bottom")
        colnote(d, (xr + 0.15, bot + 0.3), "a11→上方 0 V 轨", "right", ofst=0.0)
        d += elm.Arrow().at((xr - 0.55, po[1] - 0.5)).to((xr - 0.55, bot + 0.7)).color(C["cur"]).linewidth(1.2)
        lab(d, (xr - 1.0, bot + 1.0), "Vi 为正：\nD1 导通", ha="right", fs_=8.5, color=C["cur"])
        # 反馈：Vo（第 11 列）→ b8→b11 → 第 8 列 → e8→g13 → 2 脚。接在二极管「后面」
        yf = bot_pin[1] - 1.9
        x8 = (p_m[0] + xo) / 2 + 0.6
        path = [(xo, po[1]), (xo, yf), (p_m[0] - 0.5, yf), (p_m[0] - 0.5, p_m[1]), p_m]
        for a, b in zip(path[:-1], path[1:]):
            d += elm.Line().at(a).to(b).color(TEAL).linewidth(1.8)
        d += elm.Dot().at((x8, yf))
        lab(d, ((xo + x8) / 2, yf - 0.35), "蓝绿线 b11→b8", ha="center", fs_=8.5, color=TEAL)
        lab(d, ((x8 + p_m[0]) / 2 - 0.3, yf - 0.35), "蓝绿线 e8→g13", ha="center", fs_=8.5, color=TEAL)
        colnote(d, (x8, yf + 0.15), "第 8 列上半", "top", ofst=0.0)
        _bat_pm9(d, 1.5, -7.6)
        note(d, (6.6, -8.4), "反馈线从 D1 的阴极（Vo）引回 2 脚：二极管在反馈环里，")
        note(d, (6.6, -9.0), "它的 0.6～0.7 V 压降由运放自动补上，所以 Vo ≈ Vi。")
        note(d, (6.6, -10.0), "测量表第 6、7 步（输入为负）：只把 h5 那根线从 +9 V 轨改插 −9 V 轨，")
        note(d, (6.6, -10.6), "D1 截止，Vo ≈ 0，6 脚掉到约 −8 V。")
        for k, line in enumerate(_N05):
            note(d, (-3.0, -14.0 - 0.6 * k), line)
    print("[图 05-p4-3] +9 V→RA 8.2k→Vi(第 9 列)→RB 100→0 V；Vi→i9→i14→3 脚；6 脚→D1(阳 c14、阴 c11)→Vo(第 11 列)→RL 10k→0 V；Vo→b11→b8→e8→g13→2 脚")
    save_schem(d, "05", "05_p4_3_schem_lab.png")

    # ---------------- 图 05-p4-4：改进型 ----------------
    with drawing(fontsize=11) as d:
        title(d, (6.5, 6.6), "改进型精密整流（输入为负的接法）")
        top, y1, bot = 3.6, 0.0, -3.0
        x0 = 0.0
        d += elm.Vdd().at((x0, top)).label("−9 V")
        colnote(d, (x0 - 0.15, top - 0.3), "h5→−9 V 轨\n（下方最外一条）", "left", ofst=0.0)
        d += elm.Resistor().endpoints((x0, top), (x0, y1))
        lab(d, (x0 - 0.65, (top + y1) / 2 - 0.4), "RA 8.2k\n（g5–g9）", ha="right", fs_=10)
        d += elm.Dot().at((x0, y1))
        d += elm.Resistor().endpoints((x0, y1), (x0, bot))
        lab(d, (x0 + 0.45, (y1 + bot) / 2), "RB 100", fs_=10)
        d += elm.Ground().at((x0, bot)).label("0 V", "bottom")
        colnote(d, (x0 - 0.15, bot + 0.3), "j9→下方 0 V 轨", "left", ofst=0.0)
        ring(d, (x0, y1), "Vi", dx=-0.9)
        colnote(d, (x0 - 0.9, y1 - 0.3), "第 9 列下半", "bottom", ofst=0.0)
        xg, xop = 3.6, 5.2
        d += elm.Resistor().at((x0, y1)).to((xg, y1))
        lab(d, ((x0 + xg) / 2, y1 - 0.55), "R1 10k（h9–h13）", ha="center", fs_=10)
        d += elm.Dot().at((xg, y1))
        d += (op := elm.Opamp(leads=True).theta(0).anchor("in1").at((xop, y1)))
        p_m, p_p, po = op.absanchors["in1"], op.absanchors["in2"], op.absanchors["out"]
        d += elm.Line().at((xg, y1)).to(p_m)
        _lm741_pwr(d, op, "vd")
        _pin(d, p_m, "2", dx=0.3, dy=0.22)
        _pin(d, p_p, "3", dx=0.3, dy=-0.22)
        _pin(d, po, "6", dx=-0.3, dy=0.22)
        lab(d, (po[0] - 0.4, po[1] + 0.95), "LM741", ha="right", fs_=9.5)
        d += elm.Line().at(p_p).to((p_p[0] - 0.6, p_p[1]))
        d += elm.Line().at((p_p[0] - 0.6, p_p[1])).to((p_p[0] - 0.6, p_p[1] - 0.6)).linewidth(2.2)
        d += elm.Ground().at((p_p[0] - 0.6, p_p[1] - 0.6)).label("0 V", "bottom")
        colnote(d, (p_p[0] - 0.75, p_p[1] - 0.3), "g14→下方 0 V 轨", "left", ofst=0.0)
        # 虚地：第 13 列下半（2 脚）→ 蓝绿线 g13→e8 → 第 8 列上半；D2、Rf 都从这里出发
        yD, yR = y1 + 2.7, y1 + 4.3
        d += elm.Line().at((xg, y1)).to((xg, yD)).color(TEAL).linewidth(1.8)
        lab(d, (xg - 0.15, (y1 + yD) / 2), "蓝绿线\ng13→e8", ha="right", fs_=8.5, color=TEAL)
        d += elm.Dot().at((xg, yD))
        colnote(d, (xg - 0.15, yD + 0.2), "虚地：第 8 列上半", "left", ofst=0.0)
        x6 = po[0] + 0.8
        xo = x6 + 3.4
        d += elm.Line().at(po).to((x6, po[1]))
        d += elm.Dot().at((x6, po[1]))
        d += elm.Diode().at((xg, yD)).to((x6, yD))
        lab(d, ((xg + x6) / 2, yD + 0.55), "D2 1N4148：阳极 d8（虚地）→ 阴极 d14（6 脚）", ha="center", fs_=9.5)
        d += elm.Line().at((x6, yD)).to((x6, po[1]))
        d += elm.Line().at((xg, yD)).to((xg, yR))
        d += elm.Resistor().at((xg, yR)).to((xo, yR))
        lab(d, ((xg + xo) / 2, yR + 0.55), "Rf 20k（b8–b11）", ha="center", fs_=10)
        d += elm.Line().at((xo, yR)).to((xo, po[1]))
        ring(d, (x6, po[1]), "6 脚", dx=0.0, dy=-1.0, ha="center")
        colnote(d, (x6 - 0.15, po[1] - 0.3), "第 14 列", "left", ofst=0.0)
        d += elm.Diode().at((x6, po[1])).to((xo, po[1]))
        lab(d, ((x6 + xo) / 2, po[1] + 0.6), "D1 1N4148", ha="center", fs_=10)
        lab(d, ((x6 + xo) / 2, po[1] - 0.6), "阳极 c14 → 阴极 c11", ha="center", fs_=8.5, color=GRAY)
        d += elm.Dot().at((xo, po[1]))
        ring(d, (xo, po[1]), "Vo", dx=0.0, dy=-1.0, ha="center")
        colnote(d, (xo + 0.15, po[1] - 0.3), "第 11 列上半", "right", ofst=0.0)
        xr = xo + 2.6
        d += elm.Line().at((xo, po[1])).to((xr, po[1]))
        d += elm.Resistor().endpoints((xr, po[1]), (xr, bot))
        lab(d, (xr + 0.45, (po[1] + bot) / 2), "RL 10k", fs_=10)
        d += elm.Ground().at((xr, bot)).label("0 V", "bottom")
        colnote(d, (xr + 0.15, bot + 0.3), "a11→上方 0 V 轨", "right", ofst=0.0)
        d += elm.Arrow().at((xr - 0.55, po[1] - 0.5)).to((xr - 0.55, bot + 0.7)).color(C["cur"]).linewidth(1.2)
        lab(d, (xr - 1.0, bot + 1.0), "Vi 为负：\nD1 导通", ha="right", fs_=8.5, color=C["cur"])
        _bat_pm9(d, 1.5, -7.6)
        note(d, (6.6, -8.4), "Vi 为负：6 脚变正，D1 导通、D2 截止，Vo ≈ −(20k/10k)·Vi，是正的。")
        note(d, (6.6, -9.0), "Vi 为正（测量表第 12、13 步，h5 改插 +9 V 轨）：6 脚变负，D2 导通，")
        note(d, (6.6, -9.6), "把 6 脚钳在虚地下面约 0.4 V，D1 截止，Vo ≈ 0。")
        note(d, (6.6, -10.6), "3 脚直接接 0 V，所以 2 脚（虚地）也在 0 V 附近。")
        for k, line in enumerate(_N05):
            note(d, (-3.0, -14.0 - 0.6 * k), line)
    print("[图 05-p4-4] −9 V→RA→Vi→RB→0 V；Vi→R1 10k→2 脚(虚地，g13→e8 到第 8 列)；3 脚→0 V；D2 阳 d8、阴 d14；6 脚→D1→Vo→RL；Rf 20k Vo↔虚地")
    save_schem(d, "05", "05_p4_4_schem_lab.png")


# ======================================================================================
# 06 桥式整流：图 06-p4-1（06_p4_1_bb_bridge.png）→ 图 06-p4-2
# 依据 code/figs/06_figs.py 的 bb06()：tp = 直流 +，tn = 直流 −（下方两条轨不用）
#   ~1 → a12，~2 → j12；D3 c8→c12，D1 d12→d16，D4 g8→g12，D2 h12→h16（阳极→阴极，色环全朝右）
#   e8–f8 黑线（− 端），e16–f16 橙线（+ 端）；a16→直流 +，a8→直流 −；a22→直流 +，a26→直流 −
#   C1 b22(+)–b26（先不插，100 µF 后换 470 µF）；RL 470 Ω（方案 B 1 kΩ）d22–d26；测量点 ~1 b12、~2 i12、V+ e22、V− e26
# ======================================================================================
from schemdraw.segments import SegmentArc, Segment as _Seg


class Hop(Element):
    """横线上的「跨线弯」：两根线交叉但不相连。放在交叉点，横线在这里断开、向上拱一个半圆。"""
    def __init__(self, r=0.25, **kw):
        super().__init__(**kw)
        self.segments.append(SegmentArc((0, 0), 2 * r, 2 * r, theta1=0, theta2=180))
        self.anchors["top"], self.anchors["bot"] = (0, r), (0, -r)


def _par_arrow(d, a, b, off, dashed=False):
    """沿 a→b 方向、向外偏 off 画一支电流箭头（取中间一段）。"""
    import math
    (xa, ya), (xb, yb) = a, b
    L = math.hypot(xb - xa, yb - ya)
    ux, uy = (xb - xa) / L, (yb - ya) / L
    nx, ny = off[0], off[1]
    p0 = (xa + ux * L * 0.28 + nx, ya + uy * L * 0.28 + ny)
    p1 = (xa + ux * L * 0.72 + nx, ya + uy * L * 0.72 + ny)
    e = elm.Arrow().at(p0).to(p1).color(C["cur"]).linewidth(1.3)
    if dashed:
        e = e.linestyle("--")
    d += e


def node_06():
    POS, NEG, ACW = C["vout"], "black", TEAL
    with drawing(fontsize=11) as d:
        title(d, (4.5, 6.0), "桥式整流 + 电容滤波（第 8～26 列）")
        T, B, Lf, R = (3.2, 2.3), (3.2, -2.3), (0.9, 0.0), (5.5, 0.0)
        d += elm.Diode().at(T).to(R)           # D1：~1 → +
        d += elm.Diode().at(B).to(R)           # D2：~2 → +
        d += elm.Diode().at(Lf).to(T)          # D3：− → ~1
        d += elm.Diode().at(Lf).to(B)          # D4：− → ~2
        lab(d, (4.6, 1.75), "D1  d12→d16", fs_=10)
        lab(d, (4.6, -1.75), "D2  h12→h16", fs_=10)
        lab(d, (1.8, 1.75), "D3  c8→c12", ha="right", fs_=10)
        lab(d, (1.15, -2.75), "D4\ng8→g12", fs_=10)
        for p in (T, B, Lf, R):
            d += elm.Dot().at(p)
        # 交流输入（绿线）：~1 → a12（第 12 列上半），~2 → j12（第 12 列下半）
        xs, yT, yB = -2.8, 3.6, -3.6
        d += elm.SourceSin().endpoints((xs, -1.0), (xs, 1.0))
        lab(d, (xs - 0.6, 0.0), "交流输入\n适配器 9 V AC\n（或发生器）", ha="right", fs_=9.5)
        for a, b in (((xs, 1.0), (xs, yT)), ((xs, yT), (T[0], yT)), ((T[0], yT), T)):
            d += elm.Line().at(a).to(b).color(ACW).linewidth(1.8)
        for a, b in (((xs, -1.0), (xs, yB)), ((xs, yB), (Lf[0] - 0.25, yB)),
                     ((Lf[0] + 0.25, yB), (B[0], yB)), ((B[0], yB), B)):
            d += elm.Line().at(a).to(b).color(ACW).linewidth(1.8)
        d += Hop().at((Lf[0], yB)).theta(0).color(ACW).linewidth(1.8)
        lab(d, ((xs + T[0]) / 2, yT + 0.35), "绿线 ~1 → a12", ha="center", fs_=9, color=ACW)
        lab(d, ((xs + B[0]) / 2 - 0.6, yB + 0.35), "绿线 ~2 → j12", ha="center", fs_=9, color=ACW)
        colnote(d, (T[0] + 0.15, T[1] + 0.35), "~1：第 12 列上半", "right", ofst=0.0)
        colnote(d, (B[0] + 0.15, B[1] - 0.35), "~2：第 12 列下半", "right", ofst=0.0)
        ring(d, (T[0], yT), "~1", dx=0.0, dy=0.9, ha="left")
        ring(d, (-1.2, yB), "~2", dx=0.0, dy=-0.9, ha="left")
        # + 端：第 16 列（e16–f16 橙线连通上下）→ a16 → 直流 + 轨 → a22
        xC, xL = 10.0, 12.2
        yN = -5.0
        d += elm.Line().at(R).to((xL, 0.0)).color(POS).linewidth(1.8)
        lab(d, (R[0] + 0.15, 0.4), "+ 端：第 16 列", fs_=9.5)
        lab(d, ((R[0] + xC) / 2 + 0.3, -0.4), "橙线 a16→直流 + 轨→a22", ha="center", fs_=8.5, color=POS)
        # − 端：第 8 列（e8–f8 黑线连通上下）→ a8 → 直流 − 轨 → a26；跨过 ~2 的绿线（不相连）
        hx = Lf[0]
        d += elm.Line().at(Lf).to((hx, yN)).color(NEG).linewidth(1.8)
        d += elm.Line().at((hx, yN)).to((xL, yN)).color(NEG).linewidth(1.8)
        lab(d, (hx - 0.15, -1.0), "− 端：\n第 8 列", ha="right", fs_=9.5)
        lab(d, ((hx + xC) / 2, yN - 0.35), "黑线 a8→直流 − 轨→a26", ha="center", fs_=8.5)
        lab(d, (hx + 0.4, yB - 0.55), "绿线跨过，不相连", fs_=8, color=GRAY)
        # 负载
        for x in (xC, xL):
            d += elm.Dot().at((x, 0.0))
            d += elm.Dot().at((x, yN))
        d += elm.Capacitor(polar=True).endpoints((xC, 0.0), (xC, yN)).linestyle("--")
        lab(d, (xC - 0.45, -1.9), "C1\n100 µF\n→ 470 µF", ha="right", fs_=9.5)
        lab(d, (xC - 0.45, -3.6), "+ b22\n− b26\n（先不插）", ha="right", fs_=8.5, color=GRAY)
        d += elm.Resistor().endpoints((xL, 0.0), (xL, yN))
        lab(d, (xL + 0.45, -2.2), "RL 470 Ω\n（方案 B：1 kΩ）", fs_=10)
        colnote(d, (xL + 0.45, -3.3), "d22–d26", "right", ofst=0.0)
        ring(d, (xL, 0.0), "V+（第 22 列）", dx=0.9, dy=0.0)
        ring(d, (xL, yN), "V−（第 26 列）", dx=0.9, dy=0.0)
        d += elm.Arrow().at((xL - 0.6, -0.8)).to((xL - 0.6, yN + 0.9)).color(C["cur"]).linewidth(1.3)
        # 两个半周的电流路径
        k = 0.42
        _par_arrow(d, T, R, (-k, -k))                    # ~1 高：~1 → D1 → +
        _par_arrow(d, Lf, B, (k, k))                    # … → − → D4 → ~2
        _par_arrow(d, B, R, (-k, k), dashed=True)        # ~2 高：~2 → D2 → +
        _par_arrow(d, Lf, T, (k, -k), dashed=True)       # … → − → D3 → ~1
        lx = 8.0
        d += elm.Arrow().at((lx, 4.4)).to((lx + 0.9, 4.4)).color(C["cur"]).linewidth(1.3)
        lab(d, (lx + 1.1, 4.4), "~1 比 ~2 高的半周：~1 → D1 → + → RL → − → D4 → ~2", fs_=9, color=C["cur"])
        d += elm.Arrow().at((lx, 3.7)).to((lx + 0.9, 3.7)).color(C["cur"]).linewidth(1.3).linestyle("--")
        lab(d, (lx + 1.1, 3.7), "~2 比 ~1 高的半周：~2 → D2 → + → RL → − → D3 → ~1", fs_=9, color=C["cur"])
        lab(d, (lx + 1.1, 3.0), "两个半周流过 RL 的电流方向相同（从 + 到 −）", fs_=9, color=C["cur"])
        for kk, line in enumerate((
            "D1～D4 都是 1N4007：符号的三角形指向阴极，也就是实物上有灰色色环的一端；面包板上四只二极管的色环全部朝右。",
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；红紫色圆圈 = 测量点（与面包板图同名）；灰色小字 = 面包板列号或孔位；天蓝色箭头 = 电流方向。",
            "第 12 列的上半区（~1）和下半区（~2）隔着凹槽，不相连；第 8 列（−）、第 16 列（+）分别靠 e8–f8、e16–f16 两根短跳线把上下两半连成一个节点。",
            "量 V+、V− 时表笔接直流 + 轨和直流 − 轨（也就是第 22、26 列）；直流 − 不是大地，交流输入两根线可以互换。",
        )):
            note(d, (-5.5, -7.8 - 0.6 * kk), line)
    print("[图 06-p4-2] ~1(a12)、~2(j12)；D1 ~1→+、D2 ~2→+、D3 −→~1、D4 −→~2；+ 第 16 列→直流 + 轨→a22；− 第 8 列→直流 − 轨→a26；C1(+ b22)、RL d22–d26")
    save_schem(d, "06", "06_p4_2_schem_lab.png")


# ======================================================================================
# 07 射极跟随器：图 07-p4-1（07_p4_1_bb_follower.png）→ 图 07-p4-3；图 07-p4-2（07_p4_2_bb_direct.png）→ 图 07-p4-4
# 依据 code/figs/07_figs.py 的 bb07()：tp = +9 V，tn = 0 V（下方两条轨不用）；电池正极 → tp1，负极 → tn2
#   RP 1k：端 1 e3（a3 → +9 V），滑片 W e4，端 3 e5（a5 → 0 V）
#   follower：2N3904 平面朝自己 E e13、B e14、C e15；绿线 c4 → c14；橙线 a15 → +9 V；RL a13 → 0 V 轨；测量点 V_B b14、V_E b13、V_C c15
#   direct：拿掉三极管，220 Ω（RX）a4 → 0 V 轨；测量点「滑片」c4
# ======================================================================================
def _ef07(mode):
    POS, NEG, SIG = C["vout"], "black", TEAL
    yP, yN = 3.4, -4.4
    xb, xp = -3.4, 0.6
    with drawing(fontsize=11) as d:
        ttl = ("射极跟随器：电位器滑片推 2N3904 基极" if mode == "follower"
               else "对照组：220 Ω 直接挂在电位器滑片上")
        title(d, (3.2, yP + 1.6), ttl)
        # 两条电源轨
        xr = 9.6 if mode == "follower" else 6.0
        d += elm.Line().at((xb, yP)).to((xr, yP)).color(POS).linewidth(2.0)
        d += elm.Line().at((xb, yN)).to((xr, yN)).color(NEG).linewidth(2.0)
        lab(d, (xr + 0.2, yP), "+9 V 轨（上方第一条）", fs_=10, color=POS)
        lab(d, (xr + 0.2, yN), "0 V 轨（上方第二条）", fs_=10)
        # 9 V 电池
        d += elm.Battery().endpoints((xb, yN), (xb, yP)).reverse()
        lab(d, (xb - 0.55, -0.5), "9 V 电池\n红线 → tp1\n黑线 → tn2", ha="right", fs_=10)
        for x in (xb, xp):
            d += elm.Dot().at((x, yP))
            d += elm.Dot().at((x, yN))
        # 电位器：端 1 在上（+9 V），端 3 在下（0 V），滑片向右
        d += elm.Line().at((xp, yP)).to((xp, 2.0)).color(POS).linewidth(1.8)
        d += (pot := elm.Potentiometer().endpoints((xp, 2.0), (xp, -3.0)))
        d += elm.Line().at((xp, -3.0)).to((xp, yN)).color(NEG).linewidth(1.8)
        lab(d, (xp - 0.6, -0.5), "RP 1k", ha="right")
        colnote(d, (xp, 2.0), "端 1：e3，橙线 a3 → +9 V", "left", ofst=0.25)
        colnote(d, (xp, -3.0), "端 3：e5，黑线 a5 → 0 V", "left", ofst=0.25)
        tx, ty = pot.tap
        colnote(d, (tx + 0.25, ty + (0.35 if mode == "follower" else -0.35)), "滑片 W：e4（第 4 列）", "right", ofst=0.0)
        d += elm.Dot().at((tx, ty))
        if mode == "follower":
            xq = 6.4
            d += elm.Line().at((tx, ty)).to((xq - 0.6, ty)).color(SIG).linewidth(1.8)
            lab(d, ((tx + xq) / 2 - 0.2, ty - 0.35), "绿线 c4 → c14", ha="center", fs_=9, color=SIG)
            d += (q := elm.BjtNpn(circle=True).anchor("base").at((xq - 0.6, ty)))
            lab(d, (q.center[0] + 0.85, q.center[1] + 0.05), "Q1\n2N3904", fs_=10)
            xc, yc = q.collector
            xe, ye = q.emitter
            lab(d, (xc + 0.15, yc - 0.05), "C", fs_=10)
            lab(d, (xe + 0.15, ye + 0.1), "E", fs_=10)
            d += elm.Line().at((xc, yc)).to((xc, yP)).color(POS).linewidth(1.8)
            d += elm.Dot().at((xc, yP))
            colnote(d, (xc, (yc + yP) / 2 + 0.35), "C：e15，橙线 a15 → +9 V", "right", ofst=0.2)
            ye2 = ye - 0.6
            d += elm.Line().at((xe, ye)).to((xe, ye2))
            d += elm.Dot().at((xe, ye2))
            d += elm.Resistor().endpoints((xe, ye2), (xe, yN))
            d += elm.Dot().at((xe, yN))
            lab(d, (xe + 0.5, (ye2 + yN) / 2 + 0.2), "RL 1 kΩ\n（换 220 Ω）", fs_=10)
            colnote(d, (xe + 0.5, (ye2 + yN) / 2 - 0.75), "a13 → 0 V 轨", "right", ofst=0.0)
            colnote(d, (xe + 0.2, ye2 + 0.25), "E：e13", "right", ofst=0.0)
            colnote(d, (q.base[0] - 0.1, ty - 0.75), "B：e14", "left", ofst=0.0)
            ring(d, (xq - 0.9, ty), "V_B（b14）", dx=0.0, dy=1.5, ha="center")
            ring(d, (xe, ye2), "V_E（b13）", dx=-1.6, dy=0.0)
            ring(d, (xc, yc + 0.6), "V_C（c15）", dx=1.0, dy=0.0)
            # 电流方向
            xa = xe + 2.9
            d += elm.Arrow().at((xa, yc + 0.9)).to((xa, yN + 0.9)).color(C["cur"]).linewidth(1.3)
            lab(d, (xa + 0.2, 0.0), "I_E：+9 V → C → E → RL → 0 V\n1 kΩ 时约 4.3 mA，220 Ω 时约 19 mA", fs_=9, color=C["cur"])
            lab(d, (tx + 0.3, ty + 0.75), "I_B 很小（只有 I_E 的约 β 分之一）", fs_=8.5, color=C["cur"])
            lab(d, (q.center[0] - 0.7, yN - 0.8), "2N3904 印字面朝自己，三只脚从左到右 E、B、C → 第 13、14、15 列", ha="center", fs_=9, color=GRAY)
            notes = (
                "读图：一条线 = 一个节点；实心圆点 = 导线相连；红紫色圆圈 = 测量点（与面包板图同名，黑表笔接 0 V 轨）；灰色小字 = 面包板列号或孔位；天蓝色箭头 = 电流方向。",
                "三极管符号上带箭头的那只脚是发射极 E，箭头朝外表示 NPN；E 比 B 低一个 V_BE（约 0.7 V），所以 V_E 跟着滑片走、总比 V_B 低 0.7 V 左右。",
                "绿线从 c4 跨到 c14，中途经过第 13 列只是从上面越过，不插孔；第 9 步串电流表时把 RL 的 a13 脚改插 a11，表接在 b13 和 b11 之间。",
            )
        else:
            xr2 = tx + 2.4
            d += elm.Line().at((tx, ty)).to((xr2, ty))
            d += elm.Dot().at((xr2, ty))
            d += elm.Resistor().endpoints((xr2, ty), (xr2, yN))
            d += elm.Dot().at((xr2, yN))
            lab(d, (xr2 + 0.5, (ty + yN) / 2 + 0.2), "RX 220 Ω", fs_=10)
            colnote(d, (xr2 + 0.5, (ty + yN) / 2 - 0.4), "a4 → 0 V 轨", "right", ofst=0.0)
            ring(d, (tx + 1.2, ty), "滑片（c4）", dx=0.0, dy=1.2, ha="center")
            xa = xr2 - 0.55
            d += elm.Arrow().at((xa, ty - 0.8)).to((xa, yN + 0.6)).color(C["cur"]).linewidth(1.3)
            lab(d, (xr2 + 0.5, -3.6), "约 11 mA", fs_=9, color=C["cur"])
            lab(d, (2.0, yN - 0.8), "三极管、绿线、a15 的橙线和 RL 都已拔掉", ha="center", fs_=9, color=GRAY)
            notes = (
                "读图：一条线 = 一个节点；实心圆点 = 导线相连；红紫色圆圈 = 测量点（黑表笔接 0 V 轨）；灰色小字 = 面包板列号或孔位；天蓝色箭头 = 电流方向。",
                "220 Ω 和电位器下段（约 556 Ω）并联，滑片电压从 5 V 掉到约 2.36 V；电流只在电位器上段和 220 Ω 之间分配，没有三极管帮忙。",
            )
        for k, line in enumerate(notes):
            note(d, (xb - 2.4, yN - 1.7 - 0.6 * k), line)
    return d


def node_07():
    d = _ef07("follower")
    print("[图 07-p4-3] 9 V：+ → tp1、− → tn2；RP 端 1 e3(a3→+9 V)、W e4、端 3 e5(a5→0 V)；W→绿线 c4→c14→B；C e15→a15→+9 V；E e13→RL a13→0 V")
    save_schem(d, "07", "07_p4_3_schem_lab.png")
    d = _ef07("direct")
    print("[图 07-p4-4] RP 同上；RX 220 Ω a4→0 V 轨；测量点 滑片 c4")
    save_schem(d, "07", "07_p4_4_schem_lab.png")


# ---------------- 登记表：键 = 节点编号（与 save_schem 的 prefix 相同） ----------------
NODES = {
    "P1": node_P1,
    "P2": node_P2,
    "P3": node_P3,
    "01": node_01,
    "02": node_02,
    "03": node_03,
    "04": node_04,
    "05": node_05,
    "06": node_06,
    "07": node_07,
}


if __name__ == "__main__":
    keys = sys.argv[1:] or list(NODES)
    bad = [k for k in keys if k not in NODES]
    if bad:
        sys.exit(f"未登记的节点：{' '.join(bad)}；已登记：{' '.join(NODES)}")
    for k in keys:
        NODES[k]()
