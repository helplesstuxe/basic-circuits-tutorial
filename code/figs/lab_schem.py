"""各节点 page4（动手实验篇）面包板图配套的电路原理图。

用法（仓库根目录）：
    python code/figs/lab_schem.py            # 画全部已登记节点
    python code/figs/lab_schem.py 01 09      # 只画指定节点（键名见 NODES）
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
# 01 元件速成：图 01-p4-1（01_p4_1_breadboard.png）→ 图 01-p4-3（A 分压 / B RC 充放电 / C 继电器）
# 面包板连线依据 code/figs/01_figs.py 的 p4_1_breadboard()：
#   A：+5 V→a3；R1 b3–b7；R2 c7–c11；a11→GND；RL e7–e11（后插）；① 第 7 列
#   B：SW c13(充)/c14(公共)/c15(放)；+5 V→a13；a15→GND；R e14–e18；C b18(+)–b19；a19→GND；② 第 18 列
#   C：+5 V→j18；SB i18–i21；KA 线圈+ g21、线圈− g24、COM g26、NO g28；1N4007 阴极 f21、阳极 f24；j24→GND；
#      +5 V→j26；LED i28(长脚)→i30；1k j30→GND；③ 第 21 列
# ======================================================================================
def node_01():
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
    print("[图 01-p4-3] A：+5 V–R1 10k–①(第 7 列)–R2 10k–GND，RL 并在 R2 上；B：SW 充→+5 V、放→GND、公共→R 10k→②(第 18 列)→C 100μF(+)→GND；"
          "C：+5 V→SB→③(第 21 列，线圈+)→KA 线圈→线圈−(第 24 列)→GND，1N4007 阴极第 21 列/阳极第 24 列；+5 V→COM→NO→LED→1k→GND")
    save_schem(d, "01", "01_p4_3_schem_lab.png")


# ======================================================================================
# 03 半导体入门：图 03-p4-1（03_p4_1_breadboard.png）→ 图 03-p4-3（A 二极管 / B 三极管开关 + 电位器 / C 稳压管）
# 面包板连线依据 code/figs/03_figs.py 的 p4_1_breadboard()：
#   电源：T1 +5 V、T2 GND；B1 +9 V（电池）、B2 GND；只有 T2-2↔B2-2 一根黑线，+5 V 与 +9 V 不相连
#   A：+5 V→a3；1k b3–b7；1N4148 阳极 c7、阴极 c10；a10→GND；① 第 7 列
#   B：蓝色控制线 a13→+5 V（改插 GND = 关）；RB 10k b13–b17；2N3904 E d16 / B d17 / C d18；a16→GND；
#      RC 220 c18–c22；LED 阳极 b25、阴极 b22；+5 V→a25；② 第 17 列、③ 第 18 列
#   电位器 10k：+ c27（+5 V→a27）、滑 c28、− c29（a29→GND）；④ 第 28 列
#   C：+9 V→j20；R 560 i20–i24；1N4733A 阴极 h24、阳极 h27；j27→GND；RL（后插）f24–f29、j29→GND；⑤ 第 24 列
# ======================================================================================
def node_03():
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
        lab(d, (xn2 + 0.1, yb + 0.3), "B 基极", fs_=8.5, color=GRAY)
        lab(d, (xc + 0.15, pc[1] + 0.25), "C 集电极", fs_=8.5, color=GRAY)
        lab(d, (xc + 0.15, pe[1] - 0.25), "E 发射极", fs_=8.5, color=GRAY)
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
    print("[图 03-p4-3] A：+5 V–1k–①(第 7 列)–1N4148–GND；B：蓝线(+5 V/GND)–RB 10k–②基极(第 17 列)，2N3904 E→GND，"
          "③集电极(第 18 列)–RC 220–LED–+5 V；电位器 +5 V/④滑动端(第 28 列)/GND；C：+9 V–R 560–⑤(第 24 列)–1N4733A(阴极朝上)–GND，RL 并联后插")
    save_schem(d, "03", "03_p4_3_schem_lab.png")
    node_03_amp()


# 03 实验二：共射放大（图 03-p4-4 → 图 03-p4-5），面包板连线依据 03_figs.py 的 p4_4_breadboard_amp()：
#   B 区改接：+5 V→a22；RC 1k c18–c22；22k d22–d27；电位器 + c27、滑 c28、− c29（a29→GND）；
#   蓝线 a13→b28；RB 10k b13–b17；2N3904 E d16 / B d17 / C d18；a16→GND；② 第 17 列、③ 第 18 列、④ 第 28 列
def node_03_amp():
    top, bot = 5.4, -1.8
    cur = dict(color=C["cur"])
    with drawing(fontsize=11) as d:
        title(d, (4.6, top + 1.6), "实验二：共射放大（B 区改接后，第 13～29 列）")
        # 电位器一列：+5 V（第 22 列）→ 22k → 电位器 +（第 27 列）… −（第 29 列）→ GND
        xp = 0.0
        d += elm.Vdd().at((xp, top)).label("+5 V")
        colnote(d, (xp, top - 0.25), "第 22 列", "left")
        y27 = 2.4
        d += elm.Resistor().endpoints((xp, top), (xp, y27))
        lab(d, (xp - 0.45, (top + y27) / 2), "22k\n（新加）", ha="right", fs_=10)
        d += (pot := elm.Potentiometer().endpoints((xp, y27), (xp, bot + 0.6)))
        d += elm.Line().at((xp, bot + 0.6)).to((xp, bot))
        d += elm.Ground().at((xp, bot)).label("GND", "bottom")
        lab(d, (xp - 0.45, (y27 + bot) / 2 + 0.3), "电位器\n10k", ha="right", fs_=10)
        colnote(d, (xp, y27 - 0.2), "+ 第 27 列", "left")
        colnote(d, (xp, bot + 0.45), "− 第 29 列", "left")
        tp = pot.absanchors["tap"]
        yb = tp[1]
        n4 = (tp[0] + 1.0, yb)
        d += elm.Line().at(tp).to(n4)
        d += elm.Dot().at(n4)
        probe(d, n4, "④", dx=0.0, dy=-1.0)
        colnote(d, (n4[0] + 0.4, yb - 1.0), "滑 第 28 列", "right", ofst=0.0)
        # 蓝线：第 28 列 → 第 13 列，再经 RB 10k 到基极 ②（第 17 列）
        x13 = n4[0] + 2.4
        d += elm.Line().at(n4).to((x13, yb)).color("#0072B2")
        lab(d, ((n4[0] + x13) / 2, yb + 0.35), "蓝线", ha="center", fs_=9, color="#0072B2")
        colnote(d, (x13, yb + 0.15), "第 13 列", "top", ofst=0.0)
        xn2 = x13 + 3.0
        d += elm.Resistor().at((x13, yb)).to((xn2, yb))
        lab(d, ((x13 + xn2) / 2, yb + 0.6), "RB 10k", ha="center")
        d += elm.Arrow().at((x13 + 0.6, yb - 0.45)).to((xn2 - 0.6, yb - 0.45)).color(C["cur"]).linewidth(1.2)
        lab(d, ((x13 + xn2) / 2, yb - 0.8), "$I_B$ = (④ − ②) ÷ 10k", ha="center", fs_=9, **cur)
        d += elm.Dot().at((xn2, yb))
        d += (q := elm.BjtNpn(circle=True).theta(0).anchor("base").at((xn2 + 0.6, yb)))
        d += elm.Line().at((xn2, yb)).to(q.absanchors["base"])
        pc, pe = q.absanchors["collector"], q.absanchors["emitter"]
        xc = pc[0]
        lab(d, (xc + 0.5, yb + 0.15), "2N3904", fs_=10)
        lab(d, (xn2 + 0.1, yb + 0.3), "B 基极", fs_=8.5, color=GRAY)
        lab(d, (xc + 0.15, pc[1] + 0.25), "C 集电极", fs_=8.5, color=GRAY)
        lab(d, (xc + 0.15, pe[1] - 0.25), "E 发射极", fs_=8.5, color=GRAY)
        probe(d, (xn2, yb), "②", dx=0.0, dy=-1.6)
        colnote(d, (xn2 + 0.4, yb - 1.6), "第 17 列", "right", ofst=0.0)
        d += elm.Line().at(pe).to((xc, bot))
        d += elm.Ground().at((xc, bot)).label("GND", "bottom")
        colnote(d, (xc, bot + 0.35), "第 16 列", "right")
        # 集电极 ③（第 18 列）→ RC 1k → +5 V（第 22 列）
        y3 = pc[1] + 0.5
        d += elm.Line().at(pc).to((xc, y3))
        d += elm.Dot().at((xc, y3))
        probe(d, (xc, y3), "③", dx=-1.0)
        colnote(d, (xc - 1.3, y3 + 0.4), "第 18 列", "top", ofst=0.0)
        d += elm.Resistor().endpoints((xc, top), (xc, y3))
        lab(d, (xc - 0.45, (y3 + top) / 2), "RC 1k\n（换）", ha="right", fs_=10)
        d += elm.Vdd().at((xc, top)).label("+5 V")
        colnote(d, (xc, top - 0.25), "第 22 列", "right")
        d += elm.Arrow().at((xc + 0.6, top - 0.6)).to((xc + 0.6, y3 + 0.4)).color(C["cur"]).linewidth(1.2)
        lab(d, (xc + 0.8, (top + y3) / 2), "$I_C$ = (5 − ③) ÷ 1k", fs_=9, **cur)
        for k, line in enumerate((
                "读图：两个 +5 V 符号是同一个点（第 22 列），所以 RC 和 22k 的上端接在一起；黄色圆圈②③④ = 测量点（黑表笔接 GND）。",
                "22k 串在电位器上面，把④的范围限制在 0～约 1.56 V：基极电流最多不到 0.1 mA，集电极电流最多不到 5 mA，管子不会过热。",
                "放大的证据：④ 变 0.1 V，③ 反方向变约 1.1 V；同时② 只变几十 mV（基极–发射极之间像一只导通的二极管）。")):
            note(d, (-2.4, bot - 1.6 - 0.6 * k), line)
    print("[图 03-p4-5] +5 V(第 22 列)–22k–电位器(+第 27 列/④滑第 28 列/−第 29 列→GND)；④–蓝线–第 13 列–RB 10k–②基极(第 17 列)，"
          "2N3904 E(第 16 列)→GND，③集电极(第 18 列)–RC 1k–+5 V(第 22 列)")
    save_schem(d, "03", "03_p4_5_schem_lab.png")


# ======================================================================================
# 02 / 05 / 08 共用：LM358 放大电路 + 另一半跟随器 + 三种电源接法（原理图里 M = 中点地，V+ / V− = 电源轨）
# 三个节点的面包板是同一套布局（code/figs/02_figs.py、05_figs.py、08_figs.py 的 p4_1_breadboard()）：
#   LM358 1～4 脚 f14～f17、8～5 脚 e14～e17；8 脚 a14→V+，4 脚 j17→V−；另一半 7、6 脚 c15–c16 短接，5 脚 a17→M
#   电位器 g3（端）/ g4（滑）/ g5（端，j5→M）；1.5 V 电池盒 + → j3、− → M；滑动端 i4→i9（蓝线）；① 第 9 列
#   反相（02、05）：Rin/R1 h9–h12；j12→j15 接 2 脚；Rf i12–i14；3 脚 j16→M；② 第 12 列，③ 第 14 列
#   同相（08）：g9→g16 接 3 脚；R1 h10–h12、j10→M；j12→j15 接 2 脚；Rf i12–i14；② 第 12 列，③ 第 14 列
#   灰框（单 9 V）：a21→V+；Rm1 b21–b24；a24→M；Rm2 c24–c27；47μF d24(+)–d27；e27→V−（B1 第 29 列）
# ======================================================================================
BLUE, TEAL = "#0072B2", "#009E73"


def _pin(d, xy, n, dx=0.0, dy=0.22):
    """LM358 引脚号（小号深灰字）。"""
    d += elm.Label().at((xy[0] + dx, xy[1] + dy)).label(n, fontsize=9, color="#333333", halign="center", valign="center")


def _lm358_amp(d, kind, r_in, r_f, wire_note, ttl):
    """kind = "inv"（反相，02/05）或 "non"（同相，08）。原点附近画放大电路，返回右边界 x。"""
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
        lab(d, ((x2 + xop) / 2 - 0.05, y_in - 0.55), "绿线\nj12→j15", ha="center", fs_=8, color=TEAL)
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
    lab(d, ((pm[0] + po[0]) / 2, pm[1] + 1.35), "绿短线 c15–c16", ha="center", fs_=8, color=TEAL)
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


def node_02():
    _opamp_node("02", "inv", "Rin 10k", "Rf 100k", "蓝线 i4→i9", "反相 ×10（第 3～17 列）", None,
                _OP_NOTES + ("放大电路的第 12 列（②）就是 2 脚：面包板上它们隔了两列，靠底下那根绿线 j12→j15 连成一个节点。",),
                "02_p4_3_schem_lab.png",
                "[图 02-p4-3] 电池盒+电位器→滑动端→蓝线→①(第 9 列)→Rin 10k→②(第 12 列)→2 脚；Rf 100k ②↔③(第 14 列，1 脚)；3 脚→M；8 脚 V+，4 脚 V−；"
                "B 半边 7-6 短接、5→M；电源：两节 9 V / 一节 9 V + Rm1、Rm2 1k + 47μF")


def node_05():
    _opamp_node("05", "inv", "R1 10k", "Rf 100k（47k / 10k）", "蓝线 i4→i9（第 10 步换 Rs 10k）", "反相放大（第 3～17 列）",
                "错误接法（第 16、17 步）",
                _OP_NOTES + ("Rf 先用 100 kΩ，第 7、8 步换 47 kΩ、10 kΩ；第 10 步把滑动端到①的蓝线换成 Rs 10k。错误接法：拔掉灰框，黑线把 M 轨直接接到 V− 轨。",),
                "05_p4_3_schem_lab.png",
                "[图 05-p4-3] 同 02 反相接法，R1 10k、Rf 100k(47k/10k)，蓝线 i4→i9 第 10 步换 Rs；电源三种：双 9 V / 单 9 V 分压 / 错误接法 M 接 V−")


def node_08():
    _opamp_node("08", "non", "R1 10k", "Rf 20k（39k / 导线 / 100k）", "蓝线 i4→i9（第 10 步换 Rs 100k）", "同相放大（第 3～17 列）",
                "M 直接接电池负极（第 16～18 步）",
                _OP_NOTES + ("Rf 先用 20 kΩ，后面换 39 kΩ、导线、100 kΩ；第 10 步把滑动端到①的蓝线换成 Rs 100k。最后一种接法：拔掉灰框，黑线把 M 轨接到 V− 轨（例如 B2、B1 第 28 列）。",),
                "08_p4_3_schem_lab.png",
                "[图 08-p4-3] ①(第 9 列)→蓝线 g9→g16→3 脚；R1 10k 第 12 列→第 10 列→M；②(第 12 列)→2 脚；Rf 20k ②↔③(第 14 列，1 脚)；电源三种：双 9 V / 单 9 V 分压 / M 接 V−")


# ======================================================================================
# 12 电压跟随器：图 12-p4-1（12_p4_1_breadboard.png）→ 图 12-p4-3
# 依据 code/figs/12_figs.py 的 p4_1_breadboard()：T1 = V+，T2、B2 = M，B1 = V−；T2-1↔B2-1 黑线
#   分压：T1-6→a6；Rd1 10k b6–b10；Rd2 10k c10–c12；a12→M；① 第 10 列
#   e10→f10、g10→g16 蓝线 → 3 脚；a14→V+（8 脚）；j17→V−（4 脚）；h14→h15 绿短线（1 脚→2 脚）；③ 第 14 列
#   B 半边：c15–c16、a17→M；RL 1k h22–h25，j25→M；负载线 j22→j14（或改插 j10）
#   灰框：B2-28↔B1-28 黑线（只在一节 9 V 时插）
# ======================================================================================
def _vplus(d, xy, text="V+"):
    d += elm.Vdd().at(xy).label(text)


def node_12():
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
        # 1 脚 → 2 脚：绿短线 h14→h15（从下面绕回来）
        x3 = po[0] + 0.8
        d += elm.Line().at(po).to((x3, po[1]))
        d += elm.Dot().at((x3, po[1]))
        yf = bot_pin[1] - 1.9                            # 绕到 V− 符号下面，不和 4 脚的线交叉
        for a, b in (((x3, po[1]), (x3, yf)), ((x3, yf), (p_m[0] - 0.4, yf)), ((p_m[0] - 0.4, yf), (p_m[0] - 0.4, p_m[1])),
                     ((p_m[0] - 0.4, p_m[1]), p_m)):
            d += elm.Line().at(a).to(b).color(TEAL).linewidth(1.6)
        lab(d, ((p_m[0] + x3) / 2, yf - 0.35), "绿短线 h14→h15（1 脚接 2 脚）", ha="center", fs_=8.5, color=TEAL)
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
    print("[图 12-p4-3] V+→Rd1 10k→①(第 10 列)→Rd2 10k→M；①→蓝线→3 脚；1 脚→h14→h15→2 脚；③(第 14 列)→负载线→RL 1k(j22–j25)→M；或负载线改插 j10")
    save_schem(d, "12", "12_p4_3_schem_lab.png")


# ======================================================================================
# 16 差分放大：图 16-p4-1（16_p4_1_breadboard.png）→ 图 16-p4-3
# 依据 code/figs/16_figs.py 的面包板图：T1 = V+，T2、B2 = M，B1 = V−；LM358 在第 14～17 列（同 05）
#   1.5 V 电池盒：+ → j3，− → B2-2（M）；电位器 A g3/g4（滑）/g5，j5→M；e3→f3 橙线；电位器 B c3/c4（滑）/c5，a5→M
#   A 滑片 i4→i9 蓝线 → ①（第 9 列）→ R1 10k h9–h12 → 第 12 列 → j12→j15 绿线 → 2 脚；R2 100k i12–i14 → ③（第 14 列，1 脚）
#   B 滑片 d4→d20 蓝线，e20→f20 → ②（第 20 列）→ R3 10k g16–g20 → ④（第 16 列，3 脚）→ R4 100k i16–i19 → j19→M（第 13、14 步换 10k）
#   灰框（单 9 V）同 05
# ======================================================================================
def node_16():
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
        colnote(d, (top_pin[0] + 0.5, top_pin[1] + 0.25), "a14", "right", ofst=0.0)
        d += elm.Line().at(bot_pin).to((bot_pin[0], bot_pin[1] - 0.5))
        d += elm.Vss().at((bot_pin[0], bot_pin[1] - 0.5)).label("V−", "bottom")
        _pin(d, bot_pin, "4", dx=0.25, dy=-0.25)
        colnote(d, (bot_pin[0] + 0.5, bot_pin[1] - 0.25), "j17", "right", ofst=0.0)
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
    print("[图 16-p4-3] 1.5 V→电位器 A/B；A 滑片→①(第 9 列)→R1 10k→第 12 列→2 脚，R2 100k→③(第 14 列)；B 滑片→②(第 20 列)→R3 10k→④(第 16 列，3 脚)→R4 100k→j19→M")
    save_schem(d, "16", "16_p4_3_schem_lab.png")


# ======================================================================================
# 09 精密整流（LM741）：图 09-p4-1 → 图 09-p4-3（基本型），图 09-p4-2 → 图 09-p4-4（改进型）
# 依据 code/figs/09_figs.py 的 bb05()：tp = +9 V，tn = 0 V，bp = 0 V，bn = −9 V；tn29↔bp29
#   LM741 在第 12～15 列：a13→+9 V（7 脚），j15→−9 V（4 脚）；RA 8.2k g5–g9，h5→+9 V（改进型 / 输入为负：→ −9 V）
#   RB 100 j9→bp9；Vi 第 9 列下半区；g13（2 脚）→e8；D1 阳极 c14（6 脚）、阴极 c11；RL 10k a11→tn11；Vo 第 11 列上半区
#   基本型：i9→i14（→3 脚），b8→b11；改进型：g14→bp14，R1 10k h9–h13，D2 阳极 d8、阴极 d14，Rf 20k b8–b11
# ======================================================================================
PURPLE = C["third"]


class Ring(Element):
    """紫色空心圆圈：面包板图里 bb.probe 的测量点（Vi、Vo、6 脚、V_B …），旁边写名字。"""
    def __init__(self, r=0.17, **kw):
        super().__init__(**kw)
        self.segments.append(SegmentCircle((0, 0), r, fill="white", color=PURPLE, lw=1.6))
        self.anchors["center"] = (0, 0)


def ring(d, node_xy, text, dx=-0.8, dy=0.0, ha=None):
    """测量点：从节点拉一根细线到紫色圆圈，圆圈旁写名字（与面包板图一致）。"""
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
    "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（与面包板图同名，黑表笔接 0 V）；灰色小字 = 面包板列号或孔位；小黑字 = LM741 引脚号（1、5、8 脚不接）。",
    "二极管符号的三角形指向阴极（竖杠 = 实物上的色环）；所有 0 V 符号是同一个地（两条 0 V 轨连通），+9 V、−9 V 符号分别是同一条电源轨。",
)


def node_09():
    # ---------------- 图 09-p4-3：基本型 ----------------
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
        lab(d, ((x0 + xop) / 2 + 0.4, y1 + 0.35), "绿线 i9→i14", ha="center", fs_=8.5, color=TEAL)
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
        lab(d, ((xo + x8) / 2, yf - 0.35), "绿线 b11→b8", ha="center", fs_=8.5, color=TEAL)
        lab(d, ((x8 + p_m[0]) / 2 - 0.3, yf - 0.35), "绿线 e8→g13", ha="center", fs_=8.5, color=TEAL)
        colnote(d, (x8, yf + 0.15), "第 8 列上半", "top", ofst=0.0)
        _bat_pm9(d, 1.5, -7.6)
        note(d, (6.6, -8.4), "反馈线从 D1 的阴极（Vo）引回 2 脚：二极管在反馈环里，")
        note(d, (6.6, -9.0), "它的 0.6～0.7 V 压降由运放自动补上，所以 Vo ≈ Vi。")
        note(d, (6.6, -10.0), "测量表第 6、7 步（输入为负）：只把 h5 那根线从 +9 V 轨改插 −9 V 轨，")
        note(d, (6.6, -10.6), "D1 截止，Vo ≈ 0，6 脚掉到约 −8 V。")
        for k, line in enumerate(_N05):
            note(d, (-3.0, -14.0 - 0.6 * k), line)
    print("[图 09-p4-3] +9 V→RA 8.2k→Vi(第 9 列)→RB 100→0 V；Vi→i9→i14→3 脚；6 脚→D1(阳 c14、阴 c11)→Vo(第 11 列)→RL 10k→0 V；Vo→b11→b8→e8→g13→2 脚")
    save_schem(d, "09", "09_p4_3_schem_lab.png")

    # ---------------- 图 09-p4-4：改进型 ----------------
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
        # 虚地：第 13 列下半（2 脚）→ 绿线 g13→e8 → 第 8 列上半；D2、Rf 都从这里出发
        yD, yR = y1 + 2.7, y1 + 4.3
        d += elm.Line().at((xg, y1)).to((xg, yD)).color(TEAL).linewidth(1.8)
        lab(d, (xg - 0.15, (y1 + yD) / 2), "绿线\ng13→e8", ha="right", fs_=8.5, color=TEAL)
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
    print("[图 09-p4-4] −9 V→RA→Vi→RB→0 V；Vi→R1 10k→2 脚(虚地，g13→e8 到第 8 列)；3 脚→0 V；D2 阳 d8、阴 d14；6 脚→D1→Vo→RL；Rf 20k Vo↔虚地")
    save_schem(d, "09", "09_p4_4_schem_lab.png")


# ======================================================================================
# 13 桥式整流：图 13-p4-1（13_p4_1_bb_bridge.png）→ 图 13-p4-2
# 依据 code/figs/13_figs.py 的 bb06()：tp = 直流 +，tn = 直流 −（下方两条轨不用）
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


def node_13():
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
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（与面包板图同名）；灰色小字 = 面包板列号或孔位；天蓝色箭头 = 电流方向。",
            "第 12 列的上半区（~1）和下半区（~2）隔着凹槽，不相连；第 8 列（−）、第 16 列（+）分别靠 e8–f8、e16–f16 两根短跳线把上下两半连成一个节点。",
            "量 V+、V− 时表笔接直流 + 轨和直流 − 轨（也就是第 22、26 列）；直流 − 不是大地，交流输入两根线可以互换。",
        )):
            note(d, (-5.5, -7.8 - 0.6 * kk), line)
    print("[图 13-p4-2] ~1(a12)、~2(j12)；D1 ~1→+、D2 ~2→+、D3 −→~1、D4 −→~2；+ 第 16 列→直流 + 轨→a22；− 第 8 列→直流 − 轨→a26；C1(+ b22)、RL d22–d26")
    save_schem(d, "13", "13_p4_2_schem_lab.png")


# ======================================================================================
# 19 射极跟随器：图 19-p4-1（19_p4_1_bb_follower.png）→ 图 19-p4-3；图 19-p4-2（19_p4_2_bb_direct.png）→ 图 19-p4-4
# 依据 code/figs/19_figs.py 的 bb07()：tp = +9 V，tn = 0 V（下方两条轨不用）；电池正极 → tp1，负极 → tn2
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
                "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（与面包板图同名，黑表笔接 0 V 轨）；灰色小字 = 面包板列号或孔位；天蓝色箭头 = 电流方向。",
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
                "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（黑表笔接 0 V 轨）；灰色小字 = 面包板列号或孔位；天蓝色箭头 = 电流方向。",
                "220 Ω 和电位器下段（约 556 Ω）并联，滑片电压从 5 V 掉到约 2.36 V；电流只在电位器上段和 220 Ω 之间分配，没有三极管帮忙。",
            )
        for k, line in enumerate(notes):
            note(d, (xb - 2.4, yN - 1.7 - 0.6 * k), line)
    return d


def node_19():
    d = _ef07("follower")
    print("[图 19-p4-3] 9 V：+ → tp1、− → tn2；RP 端 1 e3(a3→+9 V)、W e4、端 3 e5(a5→0 V)；W→绿线 c4→c14→B；C e15→a15→+9 V；E e13→RL a13→0 V")
    save_schem(d, "19", "19_p4_3_schem_lab.png")
    d = _ef07("direct")
    print("[图 19-p4-4] RP 同上；RX 220 Ω a4→0 V 轨；测量点 滑片 c4")
    save_schem(d, "19", "19_p4_4_schem_lab.png")


# ======================================================================================
# 21 线性稳压：图 21-p4-1（21_p4_1_bb_regulator.png）→ 图 21-p4-2
# 面包板连线依据 code/figs/21_figs.py 的 bb08()：
#   12 V +→bn1（下方外侧轨）、−→bp2（下方内侧轨）；bn28→tp28、bp29→tn29；LM358 1～4 脚 f13～f16、8～5 脚 e13～e16
#   a13→+12 V（8 脚）；j16→0 V（4 脚）；c14–c15（7 接 6）；a16→0 V（5 脚）；TIP31 B f8、C f9、E f10；j9→+12 V；g8→g13
#   Rf i10–i14；R1 j14→0 V；j17→+12 V；RZ i17–i19；1N4733A 阴极 g19、阳极 g20；j20→0 V；h15→h19；负载 j10 / bp5（板外）
# ======================================================================================
def node_21():
    POS, SIG = C["vout"], TEAL
    yP, yN = 4.6, -5.2
    with drawing(fontsize=11) as d:
        title(d, (3.6, yP + 1.7), "分立线性稳压：1N4733A 基准 + LM358 误差放大 + TIP31 调整管（12 V 直流输入）")
        # ---- 12 V 电源 ----
        xs = -7.2
        d += elm.Battery().endpoints((xs, yN), (xs, yP)).reverse()
        lab(d, (xs - 0.55, -0.3), "12 V 直流电源\n（适配器或\n可调稳压电源）", ha="right", fs_=10)
        colnote(d, (xs + 0.2, yP - 0.4), "+ → 下方外侧轨 bn1", "right", ofst=0.0)
        colnote(d, (xs + 0.2, yN + 0.4), "− → 下方内侧轨 bp2", "right", ofst=0.0)
        # ---- 两条轨 ----
        xq = 0.0                                   # TIP31 基极 x
        d += elm.Line().at((xs, yP)).to((xq - 0.7, yP + 0.0)).color(POS).linewidth(2.0)
        xR = 13.4
        d += elm.Line().at((xs, yN)).to((xR, yN)).linewidth(2.0)
        lab(d, (xR + 0.2, yN), "0 V 轨", fs_=10)
        lab(d, (-2.9, yP + 0.42), "+12 V 轨", ha="center", fs_=10, color=POS)
        # ---- 基准：RZ + 1N4733A ----
        xz, yr = -4.6, -2.6
        d += elm.Dot().at((xz, yP))
        d += elm.Resistor().endpoints((xz, yP), (xz, yr))
        lab(d, (xz + 0.5, 1.4), "RZ 1k", fs_=10)
        colnote(d, (xz + 0.5, 0.85), "i17–i19", "right", ofst=0.0)
        colnote(d, (xz + 0.5, 0.35), "橙线 j17 → +12 V", "right", ofst=0.0)
        d += elm.Dot().at((xz, yr))
        d += elm.Zener().at((xz, yN)).to((xz, yr))
        d += elm.Dot().at((xz, yN))
        lab(d, (xz - 0.5, (yr + yN) / 2 + 0.25), "1N4733A\n5.1 V", ha="right", fs_=10)
        colnote(d, (xz - 0.5, yr - 0.15), "阴极（色环）g19", "left", ofst=0.0)
        colnote(d, (xz + 0.5, yN + 0.45), "阳极 g20，黑线 j20 → 0 V", "right", ofst=0.0)
        _par_arrow(d, (xz, yP - 0.4), (xz, yr + 0.4), (-0.45, 0.0))
        lab(d, (xz - 0.6, 2.2), "I_Z ≈ 7 mA", ha="right", fs_=9, color=C["cur"])
        # ---- LM358 A 半边（输出朝左，输入在右） ----
        d += (op := elm.Opamp(leads=True).theta(180).flip().anchor("out").at((xq + 1.2, 0.0)))
        po, pm, pp = op.absanchors["out"], op.absanchors["in1"], op.absanchors["in2"]
        cx = op.absanchors["center"][0]
        lab(d, (cx - 0.2, 1.45), "LM358 A 半边", ha="right", fs_=10)
        _pin(d, po, "1", dx=0.3, dy=0.22)
        _pin(d, pm, "2", dx=-0.3, dy=0.22)
        _pin(d, pp, "3", dx=-0.3, dy=-0.22)
        vd, vs = op.absanchors["vd"], op.absanchors["vs"]
        d += elm.Line().at(vd).to((vd[0], vd[1] + 0.5))
        d += elm.Vdd().at((vd[0], vd[1] + 0.5)).label("+12 V")
        _pin(d, vd, "8", dx=0.25, dy=0.25)
        colnote(d, (vd[0] + 0.5, vd[1] + 0.25), "a13", "right", ofst=0.0)
        d += elm.Line().at(vs).to((vs[0], vs[1] - 0.5))
        d += elm.Ground().at((vs[0], vs[1] - 0.5))
        _pin(d, vs, "4", dx=0.25, dy=-0.25)
        colnote(d, (vs[0] + 0.5, vs[1] - 0.25), "j16 → 0 V", "right", ofst=0.0)
        # 运放 1 脚 → 基极
        d += elm.Line().at(po).to((xq, po[1])).color(SIG).linewidth(1.8)
        d += (q := elm.BjtNpn(circle=True).theta(90).anchor("base").at((xq, 3.0)))
        d += elm.Line().at((xq, po[1])).to((xq, 3.0)).color(SIG).linewidth(1.8)
        lab(d, (xq - 0.3, 1.7), "绿线\ng8 → g13", ha="right", fs_=9, color=SIG)
        xc, yc = q.collector
        xe, ye = q.emitter
        lab(d, (xq, yc + 1.0), "Q1 TIP31", ha="center", fs_=10)
        lab(d, (xc - 0.05, yc + 0.35), "C", ha="right", fs_=10)
        lab(d, (xe + 0.05, ye + 0.35), "E", fs_=10)
        lab(d, (xq - 0.3, 2.85), "B", ha="right", fs_=10)
        d += elm.Line().at((xq - 0.7, yP)).to((xc, yc)).color(POS).linewidth(2.0) if abs(yc - yP) > 1e-6 else elm.Line().at((xc, yc)).to((xc, yc))
        colnote(d, (xc - 0.3, yc - 0.45), "C：f9，橙线 j9 → +12 V", "left", ofst=0.0)
        colnote(d, (xq + 0.25, 2.45), "B：f8", "right", ofst=0.0)
        # ---- 输出 V_o（第 10 列） ----
        xf, xl = 7.6, 11.6
        d += elm.Line().at((xe, ye)).to((xl, ye))
        colnote(d, (xe + 0.3, ye + 0.35), "E：f10（第 10 列 = V_o）", "right", ofst=0.0)
        d += elm.Dot().at((xf, ye))
        # 反馈分压 Rf / R1
        yfb = pm[1]
        d += elm.Resistor().endpoints((xf, ye), (xf, yfb))
        lab(d, (xf + 0.5, (ye + yfb) / 2 + 0.25), "Rf 3.9k", fs_=10)
        colnote(d, (xf + 0.5, (ye + yfb) / 2 - 0.3), "i10–i14", "right", ofst=0.0)
        d += elm.Dot().at((xf, yfb))
        d += elm.Line().at((xf, yfb)).to(pm)
        d += elm.Resistor().endpoints((xf, yfb), (xf, yN))
        d += elm.Dot().at((xf, yN))
        lab(d, (xf + 0.5, (yfb + yN) / 2 + 0.25), "R1 5.1k", fs_=10)
        colnote(d, (xf + 0.5, (yfb + yN) / 2 - 0.3), "j14 → 0 V 轨", "right", ofst=0.0)
        # 负载（板外）
        d += elm.Dot().at((xl, ye))
        d += elm.Resistor().endpoints((xl, ye), (xl, yN))
        d += elm.Dot().at((xl, yN))
        lab(d, (xl + 0.5, 0.3), "RL（板外）\n180 Ω 轻载\n18 Ω 重载", fs_=10)
        colnote(d, (xl + 0.5, -1.3), "一端接 j10，\n另一端接 0 V 轨第 5 列", "right", ofst=0.0)
        # 基准 → 3 脚：绿线 h15→h19，从运放下面绕到右边
        xin = pp[0] + 0.7
        d += elm.Line().at((xz, yr)).to((xin, yr)).color(SIG).linewidth(1.8)
        d += elm.Line().at((xin, yr)).to((xin, pp[1])).color(SIG).linewidth(1.8)
        d += elm.Line().at((xin, pp[1])).to(pp)
        lab(d, ((xz + xin) / 2 + 0.6, yr - 0.35), "绿线 h15 → h19（基准送到 3 脚）", ha="center", fs_=9, color=SIG)
        colnote(d, (pm[0] + 0.2, yfb + 0.3), "第 14 列", "right", ofst=0.0)
        # ---- 测量点 ----
        ring(d, (xz, yr), "V_ref（f19）", dx=1.0, dy=0.9)
        ring(d, (xf, yfb), "反相端（g14）", dx=0.9, dy=-0.9)
        ring(d, (xq + 0.45, po[1]), "运放输出（h13）", dx=0.0, dy=-1.0, ha="center")
        ring(d, (xf - 1.0, ye), "V_o（h10）", dx=0.0, dy=0.9, ha="center")
        # ---- 电流方向 ----
        _par_arrow(d, (xe + 0.3, ye), (xf - 0.2, ye), (0.0, -0.45))
        d += elm.Arrow().at((xl + 2.8, ye - 0.6)).to((xl + 2.8, yN + 1.2)).color(C["cur"]).linewidth(1.3)
        lab(d, (xl + 0.5, -3.1), "负载电流\n180 Ω：约 49 mA\n18 Ω：约 0.49 A", fs_=9, color=C["cur"])
        # ---- LM358 另一半 ----
        xb0, yb0 = 2.2, yN - 3.2
        
        d += (ob := elm.Opamp(leads=True).theta(0).anchor("in2").at((xb0 + 0.6, yb0)))
        bm, bp_, bo = ob.absanchors["in1"], ob.absanchors["in2"], ob.absanchors["out"]
        d += elm.Line().at(bp_).to((xb0, bp_[1]))
        d += elm.Ground().at((xb0, bp_[1]))
        colnote(d, (xb0 - 0.15, bp_[1] + 0.3), "黑线 a16 → 0 V", "left", ofst=0.0)
        d += elm.Line().at(bo).to((bo[0] + 0.4, bo[1]))
        for a_, b_ in (((bo[0] + 0.4, bo[1]), (bo[0] + 0.4, bm[1] + 0.9)),
                       ((bo[0] + 0.4, bm[1] + 0.9), (bm[0] - 0.3, bm[1] + 0.9)),
                       ((bm[0] - 0.3, bm[1] + 0.9), (bm[0] - 0.3, bm[1]))):
            d += elm.Line().at(a_).to(b_).color(SIG).linewidth(1.6)
        d += elm.Line().at((bm[0] - 0.3, bm[1])).to(bm)
        lab(d, ((bm[0] + bo[0]) / 2, bm[1] + 1.2), "绿色短线 c14 → c15", ha="center", fs_=8.5, color=SIG)
        _pin(d, bm, "6", dx=0.3)
        _pin(d, bp_, "5", dx=0.3, dy=-0.22)
        _pin(d, bo, "7", dx=-0.3)
        lab(d, (bo[0] + 0.9, bo[1] + 0.35), "LM358 另一半（不用，接成跟随器）", fs_=10.5)
        lab(d, (bo[0] + 0.9, bo[1] - 0.3), "8、4 脚和 A 半边共用", fs_=8.5, color=GRAY)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（与面包板图同名，黑表笔接 0 V 轨）；灰色小字 = 面包板列号或孔位；小黑字 = LM358 引脚号；天蓝色箭头 = 电流方向。",
            "稳压管符号的三角形指向阴极（竖杠 = 色环），阴极朝上接 RZ 和 3 脚；TIP31 印字面朝自己、脚朝下，从左到右 B、C、E → 第 8、9、10 列，带箭头的脚是 E。",
            "电源轨：下方外侧 = +12 V，下方内侧 = 0 V；上方两条轨经第 28 列橙线、第 29 列黑线和下方相连（上方最外侧 +12 V，第二条 0 V）。输出电容 C_o 不接（见正文）。",
        )
        for k, line in enumerate(notes):
            note(d, (xs - 2.6, yb0 - 1.8 - 0.6 * k), line)
    print("[图 21-p4-2] 12 V：+→bn1、−→bp2；RZ i17–i19(j17→+12 V)；DZ 阴极 g19、阳极 g20(j20→0 V)；h15→h19→3 脚；1 脚 g13→g8→B；C f9(j9→+12 V)；E f10→Rf i10–i14→2 脚，R1 j14→0 V；RL j10/bp5")
    save_schem(d, "21", "21_p4_2_schem_lab.png")

# ======================================================================================
# 25 开关电源：图 25-p4-1（25_p4_1_bb_buck.png）→ 图 25-p4-2
# 面包板连线依据 code/figs/25_figs.py 的 bb09()：
#   12 V +→tp1（+12 V 输入轨）、−→tn2（0 V）；tn28→bp28（上下 0 V 轨相连）；模块 IN+ e4、IN− f4、OUT+ e20、OUT− f20
#   a4→+12 V 轨；j4→bp4；j20→bp20；a20→板外 RL；RL 另一端→bp16；测量点 V_in c4、V_o c20
# ======================================================================================
def _dbox(d, x0, y0, x1, y1, color=GRAY):
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        d += elm.Line().endpoints(a, b).color(color).linestyle("--").linewidth(1.2)


def node_25():
    POS, SIG, IN = C["vout"], TEAL, "#7a7a7a"
    yP, yG, yt, yb = 3.8, -3.8, 1.2, -1.2
    with drawing(fontsize=11) as d:
        title(d, (3.0, yP + 1.7), "现成降压模块：12 V 直流进、5 V 出（负载在板外）")
        xs = -9.0
        d += elm.Battery().endpoints((xs, yG), (xs, yP)).reverse()
        lab(d, (xs - 0.55, 0.0), "12 V 直流电源\n（可调稳压电源\n或适配器）", ha="right", fs_=10)
        colnote(d, (xs + 0.2, yP - 0.4), "+ → tp1（上方最外侧轨）", "right", ofst=0.0)
        colnote(d, (xs + 0.2, yG + 0.4), "− → tn2（上方第二条轨）", "right", ofst=0.0)
        xa, xbL, xbR = -4.2, -1.5, 7.5
        d += elm.Line().at((xs, yP)).to((xa, yP)).color(POS).linewidth(2.0)
        lab(d, ((xs + xa) / 2, yP + 0.9), "+12 V 输入轨", ha="center", fs_=10, color=POS)
        xR = 13.6
        d += elm.Line().at((xs, yG)).to((xR, yG)).linewidth(2.0)
        lab(d, (xR + 0.2, yG), "0 V", fs_=10)
        lab(d, (3.0, yG - 0.5), "上方 0 V 轨（tn）和下方内侧 0 V 轨（bp）经第 28 列黑线相连，原理图里画成同一条 0 V 线", ha="center", fs_=8.5, color=GRAY)
        # IN+：橙线 a4
        d += elm.Dot().at((xa, yP))
        d += elm.Line().at((xa, yP)).to((xa, yt)).color(POS).linewidth(1.8)
        d += elm.Line().at((xa, yt)).to((xbL, yt))
        colnote(d, (xa + 0.2, (yP + yt) / 2 + 0.2), "橙线 a4 → +12 V 轨", "right", ofst=0.0)
        # IN−：黑线 j4
        d += elm.Line().at((xbL, yb)).to((xa, yb))
        d += elm.Line().at((xa, yb)).to((xa, yG)).linewidth(1.8)
        d += elm.Dot().at((xa, yG))
        colnote(d, (xa + 0.2, (yb + yG) / 2 - 0.3), "黑线 j4 →\n下方 0 V 轨", "right", ofst=0.0)
        # ---- 模块方框 ----
        _dbox(d, xbL, yG + 1.3, xbR, yP - 0.9)
        lab(d, ((xbL + xbR) / 2, yP - 1.3), "降压模块（例如 LM2596），电位器调输出", ha="center", fs_=10)
        for (x, y, t, cn, side) in ((xbL, yt, "IN+", "e4（第 4 列上半）", "top"), (xbL, yb, "IN−", "f4（第 4 列下半）", "bottom"),
                                   (xbR, yt, "OUT+", "e20（第 20 列上半）", "top"), (xbR, yb, "OUT−", "f20（第 20 列下半）", "bottom")):
            d += elm.Dot(open=True).at((x, y))
            ha = "left" if x == xbL else "right"
            lab(d, (x + (0.25 if x == xbL else -0.25), y + (0.35 if y > 0 else -0.35)), t, ha=ha, fs_=10.5)
            colnote(d, (x + (-1.35 if x == xbL else 1.35), y + (0.3 if y > 0 else -0.3)), cn, "top" if y > 0 else "bottom", ofst=0.0)
        # 模块内部（灰色示意）
        x1, xsw, xl2, xc = -0.6, 1.9, 4.6, 5.6
        d += elm.Line().at((xbL, yt)).to((x1, yt)).color(IN)
        d += elm.Switch().endpoints((x1, yt), (xsw - 0.4, yt)).color(IN)
        d += elm.Line().at((xsw - 0.4, yt)).to((xsw, yt)).color(IN)
        lab(d, ((x1 + xsw) / 2 - 0.2, yt - 0.55), "开关管", ha="center", fs_=9, color=IN)
        d += elm.Dot().at((xsw, yt)).color(IN)
        d += elm.Schottky().at((xsw, yb)).to((xsw, yt)).color(IN)
        lab(d, (xsw + 0.45, -0.25), "续流\n二极管", fs_=9, color=IN)
        d += elm.Inductor2().endpoints((xsw, yt), (xl2, yt)).color(IN)
        lab(d, ((xsw + xl2) / 2, yt + 0.55), "电感", ha="center", fs_=9, color=IN)
        d += elm.Line().at((xl2, yt)).to((xbR, yt)).color(IN)
        d += elm.Dot().at((xc, yt)).color(IN)
        d += elm.Capacitor(polar=True).endpoints((xc, yt), (xc, yb)).color(IN)
        lab(d, (xc + 0.45, -0.1), "输出\n电容", fs_=9, color=IN)
        d += elm.Line().at((xbL, yb)).to((xbR, yb)).color(IN)
        for x in (xsw, xc):
            d += elm.Dot().at((x, yb)).color(IN)
        lab(d, (xsw - 0.25, yt + 0.55), "开关节点", ha="right", fs_=8.5, color=IN)
        lab(d, ((xbL + xbR) / 2, yG + 1.75), "虚线框内 = 模块板上已焊好的电路（示意）", ha="center", fs_=8.5, color=IN)
        # ---- 输出 ----
        xo, xl = 10.7, 12.2
        d += elm.Line().at((xbR, yt)).to((xl, yt)).color(SIG).linewidth(1.8)
        lab(d, ((xbR + xl) / 2 + 0.3, yt - 0.4), "绿线 a20 → 负载（板外）", ha="center", fs_=9, color=SIG)
        d += elm.Resistor().endpoints((xl, yt), (xl, yG))
        d += elm.Dot().at((xl, yG))
        lab(d, (xl + 0.5, -0.6), "RL（板外）\n10 Ω → 5 Ω\n10 W 以上", fs_=10)
        colnote(d, (xl + 0.5, -2.2), "另一端 → 下方 0 V 轨第 16 列", "right", ofst=0.0)
        xo2 = xbR + 2.8
        d += elm.Line().at((xbR, yb)).to((xo2, yb))
        d += elm.Line().at((xo2, yb)).to((xo2, yG)).linewidth(1.8)
        d += elm.Dot().at((xo2, yG))
        colnote(d, (xo2 - 0.2, (yb + yG) / 2 - 0.3), "黑线 j20 → 0 V", "left", ofst=0.0)
        # ---- 测量点 ----
        ring(d, ((xa + xbL) / 2, yt), "V_in（c4）", dx=0.0, dy=-0.9, ha="center")
        ring(d, (xo, yt), "V_o（c20）", dx=0.0, dy=1.1, ha="center")
        # ---- 电流方向 ----
        _par_arrow(d, (xs + 0.4, yP), (xa - 0.2, yP), (0.0, 0.4))
        lab(d, ((xs + xa) / 2 + 0.5, yP - 1.5), "I_in：10 Ω 时 0.22～0.26 A\n5 Ω 时 0.44～0.52 A", ha="center", fs_=9, color=C["cur"])
        d += elm.Arrow().at((xl + 2.6, yt - 0.2)).to((xl + 2.6, yG + 1.5)).color(C["cur"]).linewidth(1.3)
        lab(d, (xl + 2.8, yt - 0.6), "I_o：\n10 Ω 时 0.50 A\n5 Ω 时 1.00 A", fs_=9, color=C["cur"])
        notes = (
            "读图：一条线 = 一个节点；紫色圆圈 = 测量点（与面包板图同名，黑表笔接 0 V 轨）；灰色小字 = 面包板孔位；空心圆 = 模块的四个排针；天蓝色箭头 = 电流方向。",
            "测输入电流：断电，拔掉 a4 的橙线，电流表红笔接 +12 V 轨、黑笔接 b4，电表就串在 +12 V 轨和 IN+ 之间。模块里的控制芯片按 OUT 电压让开关管通断。",
            "模块跨在凹槽上：「+」脚在上半区（e 行）、「−」脚在下半区（f 行），所以 IN+ 和 IN− 虽同在第 4 列却不相通；IN 和 OUT 千万不要接反。",
            "输出电流约是输入电流的两倍多：电压从 12 V 降到 5 V，电流就升上去，输入功率只比输出功率多一点损耗。",
        )
        for k, line in enumerate(notes):
            note(d, (xs - 2.8, yG - 1.3 - 0.6 * k), line)
    print("[图 25-p4-2] 12 V：+→tp1、−→tn2；tn28→bp28；IN+ e4(a4→+12 V)、IN− f4(j4→0 V)；OUT+ e20(a20→RL)、OUT− f20(j20→0 V)；RL→bp16")
    save_schem(d, "25", "25_p4_2_schem_lab.png")

# ======================================================================================
# 17 稳压管稳压：图 17-p4-1（17_p4_1_bb_zener.png）→ 图 17-p4-2
# 面包板连线依据 code/figs/17_figs.py 的 bb10()：
#   电源 +→tp1（+V_in 9～12 V）、−→tn2（0 V）；a3→tp3；R 180 Ω c3–c7；1N4733A 阴极 b7、阳极 b10；a10→0 V；RL d7–d13；a13→0 V
#   测量点 V_in b3、V_o e7
# ======================================================================================
def node_17():
    POS = C["vout"]
    yP, yo, ym, yG = 3.4, 1.2, -1.6, -3.8
    with drawing(fontsize=11) as d:
        title(d, (2.6, yP + 1.5), "稳压管并联稳压：R 180 Ω + 1N4733A（5.1 V）")
        xs = -4.2
        d += elm.Battery().endpoints((xs, yG), (xs, yP)).reverse()
        lab(d, (xs - 0.55, -0.2), "9 V 电池\n或 ≤12 V\n可调直流电源", ha="right", fs_=10)
        colnote(d, (xs + 0.2, yP - 0.4), "+ → tp1", "right", ofst=0.0)
        colnote(d, (xs + 0.2, yG + 0.4), "− → tn2", "right", ofst=0.0)
        xi, xo, xz, xl, xR = -0.6, 3.6, 3.6, 9.0, 10.8
        d += elm.Line().at((xs, yP)).to((xR, yP)).color(POS).linewidth(2.0)
        lab(d, (xR + 0.2, yP), "+V_in 轨（9～12 V）\n上方最外侧", fs_=10, color=POS)
        d += elm.Line().at((xs, yG)).to((xR, yG)).linewidth(2.0)
        lab(d, (xR + 0.2, yG), "0 V 轨\n上方第二条", fs_=10)
        # 第 3 列：橙线 a3
        d += elm.Dot().at((xi, yP))
        d += elm.Line().at((xi, yP)).to((xi, yo)).color(POS).linewidth(1.8)
        colnote(d, (xi - 0.2, (yP + yo) / 2), "橙线 a3 → +V_in 轨", "left", ofst=0.0)
        d += elm.Dot().at((xi, yo))
        colnote(d, (xi - 0.2, yo + 0.3), "第 3 列", "left", ofst=0.0)
        d += elm.Resistor().endpoints((xi, yo), (xo, yo))
        lab(d, ((xi + xo) / 2, yo - 0.5), "R 180 Ω 1 W", ha="center", fs_=10)
        colnote(d, ((xi + xo) / 2, yo - 0.95), "c3–c7", "bottom", ofst=0.0)
        # 第 7 列 = 输出节点
        d += elm.Dot().at((xo, yo))
        d += elm.Line().at((xo, yo)).to((xl, yo))
        d += elm.Dot().at((xl, yo))
        colnote(d, ((xo + xl) / 2 + 0.3, yo + 0.3), "第 7 列 = 输出节点", "top", ofst=0.0)
        # 稳压管：阴极 b7 在上，阳极 b10 在下
        d += elm.Zener().at((xz, ym)).to((xz, yo))
        lab(d, (xz + 0.45, (yo + ym) / 2 - 0.1), "1N4733A 5.1 V", fs_=10)
        colnote(d, (xz + 0.35, yo - 0.45), "阴极（色环）b7", "right", ofst=0.0)
        colnote(d, (xz + 0.35, ym + 0.35), "阳极 b10", "right", ofst=0.0)
        d += elm.Dot().at((xz, ym))
        d += elm.Line().at((xz, ym)).to((xz, yG)).linewidth(1.8)
        d += elm.Dot().at((xz, yG))
        colnote(d, (xz + 0.2, (ym + yG) / 2 - 0.1), "黑线 a10 → 0 V\n（测 I_Z：换成电流表，\n红笔插 c10）", "right", ofst=0.0)
        # 负载 RL：d7–d13
        d += elm.Resistor().endpoints((xl, yo), (xl, ym))
        lab(d, (xl + 0.5, (yo + ym) / 2 + 0.25), "RL\n1k / 510 / 255 Ω", fs_=10)
        colnote(d, (xl + 0.5, (yo + ym) / 2 - 0.55), "d7–d13（先空载）", "right", ofst=0.0)
        d += elm.Dot().at((xl, ym))
        d += elm.Line().at((xl, ym)).to((xl, yG)).linewidth(1.8)
        d += elm.Dot().at((xl, yG))
        colnote(d, (xl + 0.2, (ym + yG) / 2 - 0.1), "黑线 a13 → 0 V\n（测 I_L：换成电流表，\n红笔插 c13）", "right", ofst=0.0)
        # 测量点
        ring(d, (xi, yo), "V_in（b3）", dx=-1.0, dy=-1.0, ha="center")
        ring(d, (xl - 2.3, yo), "V_o（e7）", dx=0.0, dy=-1.0, ha="center")
        # 电流
        _par_arrow(d, (xi + 0.3, yo), (xo - 0.3, yo), (0.0, 0.6))
        lab(d, ((xi + xo) / 2, yo + 1.0), "I_R ≈ 21.9 mA（9 V）", ha="center", fs_=9, color=C["cur"])
        _par_arrow(d, (xz, yo - 0.2), (xz, ym + 0.2), (-0.9, 0.0))
        lab(d, (xz - 1.1, (yo + ym) / 2 - 0.1), "I_Z", ha="right", fs_=9, color=C["cur"])
        _par_arrow(d, (xl, yo - 0.2), (xl, ym + 0.2), (-0.5, 0.0))
        lab(d, (xl - 0.7, (yo + ym) / 2 - 0.1), "I_L", ha="right", fs_=9, color=C["cur"])
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（与面包板图同名，黑表笔接 0 V 轨）；灰色小字 = 面包板列号或孔位；天蓝色箭头 = 电流方向。",
            "稳压管符号的三角形指向阴极（竖杠 = 色环），阴极朝上接输出节点，这样它才是反向击穿、钉住 5.1 V；插反了输出只有约 0.7 V。",
            "I_R = I_Z + I_L：空载时 I_Z ≈ 22 mA；RL = 1k 时 17.0 / 5.0 mA，510 Ω 时 12.3 / 9.8 mA，255 Ω 时 3.1 / 19.4 mA（9 V 输入）。",
        )
        for k, line in enumerate(notes):
            note(d, (xs - 2.4, yG - 1.0 - 0.6 * k), line)
    print("[图 17-p4-2] 电源 +→tp1、−→tn2；a3→+V_in；R c3–c7；DZ 阴极 b7、阳极 b10(a10→0 V)；RL d7–d13(a13→0 V)；V_in b3、V_o e7")
    save_schem(d, "17", "17_p4_2_schem_lab.png")

# ======================================================================================
# 22 过载保护：图 22-p4-1（22_p4_1_bb_protect.png）→ 图 22-p4-2
# 面包板连线依据 code/figs/22_figs.py 的 bb11()：
#   12 V +→bn1、−→bp2；tn1–bp1；7805 IN f2(j2→bn2)、GND f3(j3→bp3)、OUT f4(g4→tp8)；Cin h2–h3、Cout i3–i4
#   LM393 第 20～23 列：8 脚 a20→tp20，4 脚 j23→0 V，2、3 脚 j21、j22→0 V；RPU b17–b21(a17→+5 V)；RH a21–a23；
#   RA b23–b27(a27→+5 V)；RB d23–d25(a25→0 V)；IRLZ44N S f13、D f14、G f15；c21→g15；c22→g16；
#   RS j13→bp13；RF i13–i16；CF j16(+)→bp16；h14→h8；RN j8→bn8；LED 阳极 g10、阴极 g8；RLED j10→bn10；RO i8→bn5
# ======================================================================================
def node_22():
    POS, SIG = C["vout"], TEAL
    y12, y5, yG, ydn, ys = 7.0, 5.0, -5.0, 3.0, -2.2
    xs, xE = -13.0, 17.2
    with drawing(fontsize=11) as d:
        title(d, (2.0, y12 + 1.4), "低压慢动作过载保护：7805 供 5 V，LM393 比较，IRLZ44N 开关")
        d += elm.Battery().endpoints((xs, yG), (xs, y12)).reverse()
        lab(d, (xs - 0.55, 1.0), "12 V 直流\n电源", ha="right", fs_=10)
        colnote(d, (xs + 0.2, y12 - 0.4), "+ → bn1", "right", ofst=0.0)
        colnote(d, (xs + 0.2, yG + 0.4), "− → bp2", "right", ofst=0.0)
        d += elm.Line().at((xs, y12)).to((xE, y12)).color(POS).linewidth(2.0)
        lab(d, (xE + 0.2, y12), "+12 V 轨\n（下方最外侧）", fs_=10, color=POS)
        d += elm.Line().at((xs, yG)).to((xE, yG)).linewidth(2.0)
        lab(d, (xE + 0.2, yG), "0 V 轨（上下两条\n由 tn1–bp1 黑线相连）", fs_=10)
        # ---- 7805 ----
        ic = elm.Ic(pins=[elm.IcPin(name="IN", pin="1", side="left"), elm.IcPin(name="GND", pin="2", side="bottom"),
                          elm.IcPin(name="OUT", pin="3", side="right")], size=(2.4, 1.4)).right().anchor("IN").at((-9.0, 2.0))
        d += ic
        pin_in, pin_g, pin_o = ic.absanchors["IN"], ic.absanchors["GND"], ic.absanchors["OUT"]
        lab(d, ((pin_in[0] + pin_o[0]) / 2, pin_in[1] + 1.15), "7805", ha="center", fs_=11)
        xci, xco = -10.4, -4.5
        d += elm.Dot().at((xci, y12))
        d += elm.Line().at((xci, y12)).to((xci, pin_in[1])).color(POS).linewidth(1.8)
        colnote(d, (xci - 0.2, (y12 + pin_in[1]) / 2 + 0.4), "橙线 j2 → +12 V 轨", "left", ofst=0.0)
        d += elm.Dot().at((xci, pin_in[1]))
        d += elm.Line().at((xci, pin_in[1])).to(pin_in)
        colnote(d, ((xci + pin_in[0]) / 2, pin_in[1] + 0.3), "IN f2", "top", ofst=0.0)
        d += elm.Capacitor().endpoints((xci, pin_in[1]), (xci, yG))
        lab(d, (xci - 0.55, (pin_in[1] + yG) / 2), "0.33 μF\n（h2–h3）", ha="right", fs_=9.5)
        d += elm.Dot().at((xci, yG))
        d += elm.Line().at(pin_g).to((pin_g[0], yG)).linewidth(1.8)
        d += elm.Dot().at((pin_g[0], yG))
        colnote(d, (pin_g[0] + 0.2, (pin_g[1] + yG) / 2 + 0.6), "GND f3\n黑线 j3 → 0 V", "right", ofst=0.0)
        d += elm.Line().at(pin_o).to((xco, pin_o[1]))
        colnote(d, ((pin_o[0] + xco) / 2, pin_o[1] - 0.3), "OUT f4", "bottom", ofst=0.0)
        d += elm.Dot().at((xco, pin_o[1]))
        d += elm.Capacitor().endpoints((xco, pin_o[1]), (xco, yG))
        lab(d, (xco + 0.55, (pin_o[1] + yG) / 2 - 0.6), "0.1 μF\n（i3–i4）", fs_=9.5)
        d += elm.Dot().at((xco, yG))
        d += elm.Line().at((xco, pin_o[1])).to((xco, y5)).color(POS).linewidth(1.8)
        colnote(d, (xco + 0.2, (pin_o[1] + y5) / 2 + 0.1), "橙线 g4 → tp8", "right", ofst=0.0)
        ring(d, (xco, pin_o[1] + 0.9), "5 V（h4）", dx=-0.9, dy=0.0)
        # ---- +5 V 轨与比较器 ----
        op = elm.Opamp(leads=True).right().flip().anchor("in2").at((1.5, 1.0))
        d += op
        a = op.absanchors
        xo = 5.6
        d += elm.Line().at((xco, y5)).to((xo, y5)).color(POS).linewidth(2.0)
        lab(d, (xco - 0.2, y5 + 0.45), "+5 V 轨（上方最外侧，7805 输出）", fs_=10, color=POS)
        lab(d, (a["in2"][0] + 0.9, a["out"][1] - 0.05), "LM393\nB 组", fs_=9)
        _pin(d, a["in2"], "5", dx=-0.25, dy=0.22)
        _pin(d, a["in1"], "6", dx=-0.25, dy=-0.25)
        _pin(d, a["out"], "7", dx=0.15, dy=0.25)
        top, bot = a["vs"], a["vd"]
        d += elm.Line().at(top).to((top[0], top[1] + 0.45))
        lab(d, (top[0] + 0.15, top[1] + 0.5), "8 → +5 V（a20）", fs_=9)
        d += elm.Line().at(bot).to((bot[0], bot[1] - 0.45))
        lab(d, (bot[0] + 0.15, bot[1] - 0.55), "4 → 0 V（j23）", fs_=9)
        # 同相端：RA / RB 分压，RH 回差
        xa = 0.0
        d += elm.Line().at(a["in2"]).to((xa, a["in2"][1]))
        d += elm.Dot().at((xa, a["in2"][1]))
        d += elm.Dot().at((xa, y5))
        d += elm.Resistor().endpoints((xa, y5), (xa, a["in2"][1]))
        lab(d, (xa - 0.5, (y5 + 1.0) / 2 + 0.2), "R_A 33k\nb23–b27\na27 → +5 V", ha="right", fs_=9.5)
        d += elm.Resistor().endpoints((xa, a["in2"][1]), (xa, yG))
        d += elm.Dot().at((xa, yG))
        lab(d, (xa - 0.5, (1.0 + yG) / 2 - 0.6), "R_B 1k\nd23–d25\na25 → 0 V", ha="right", fs_=9.5)
        colnote(d, (xa - 0.15, a["in2"][1] + 0.3), "第 23 列", "left", ofst=0.0)
        xh, yh = 0.8, 2.8
        d += elm.Dot().at((xh, a["in2"][1]))
        d += elm.Line().at((xh, a["in2"][1])).to((xh, yh))
        d += elm.Resistor().endpoints((xo, yh), (xh, yh))
        lab(d, ((xh + xo) / 2, yh + 0.55), "R_H 100k（a21–a23）", ha="center", fs_=9.5)
        d += elm.Line().at(a["out"]).to((xo, a["out"][1]))
        d += elm.Dot().at((xo, a["out"][1]))
        d += elm.Line().at((xo, a["out"][1])).to((xo, yh))
        d += elm.Dot().at((xo, yh))
        d += elm.Resistor().endpoints((xo, yh), (xo, y5))
        d += elm.Dot().at((xo, y5))
        lab(d, (xo + 0.5, (yh + y5) / 2), "R_PU 2.2k\nb17–b21\na17 → +5 V", fs_=9.5)
        colnote(d, (xo + 0.15, yh - 0.7), "第 21 列", "right", ofst=0.0)
        ring(d, (xa, a["in2"][1]), "V_+（c23）", dx=-1.0, dy=-0.8)
        # ---- MOS 管 ----
        xg = 8.0
        fet = elm.NFet().right().reverse().anchor("gate").at((xg, a["out"][1]))
        d += fet
        f = fet.absanchors
        d += elm.Line().at((xo, a["out"][1])).to(f["gate"]).color(SIG).linewidth(1.8)
        colnote(d, ((xo + xg) / 2 + 0.3, a["out"][1] - 0.3), "绿线 c21 → g15", "bottom", ofst=0.0)
        ring(d, (xo + 0.8, a["out"][1]), "V_G（d21）", dx=0.0, dy=1.0)
        lab(d, (f["gate"][0] - 0.1, f["gate"][1] + 0.35), "G f15", ha="right", fs_=9, color=GRAY)
        lab(d, (f["drain"][0] + 0.2, f["drain"][1] + 0.1), "D f14", fs_=9, color=GRAY)
        lab(d, (f["source"][0] + 0.2, f["source"][1] - 0.1), "S f13", fs_=9, color=GRAY)
        lab(d, (f["gate"][0] + 1.65, f["gate"][1] + 0.1), "IRLZ44N", fs_=10)
        xm = f["drain"][0]
        d += elm.Line().at(f["drain"]).to((xm, ydn))
        d += elm.Dot().at((xm, ydn))
        ring(d, (xm, ydn - 0.8), "V_D（g14）", dx=0.9, dy=0.0)
        xn, xled, xro = 11.6, 13.9, 16.2
        d += elm.Line().at((xm, ydn)).to((xro, ydn)).color(SIG).linewidth(1.8)
        colnote(d, ((xm + xn) / 2, ydn + 0.3), "绿线 h14 → h8", "top", ofst=0.0)
        colnote(d, ((xn + xled) / 2, ydn - 0.3), "第 8 列 = 漏极", "bottom", ofst=0.0)
        # 负载
        for x in (xn, xled, xro):
            d += elm.Dot().at((x, y12))
        d += elm.Dot().at((xn, ydn)); d += elm.Dot().at((xled, ydn))
        d += elm.Resistor().endpoints((xn, y12), (xn, ydn))
        lab(d, (xn + 0.5, (y12 + ydn) / 2), "RN 1.5k\nj8 → bn8", fs_=9.5)
        ymid = 5.0
        d += elm.Resistor().endpoints((xled, y12), (xled, ymid))
        lab(d, (xled + 0.5, (y12 + ymid) / 2), "2.2k\nj10 → bn10", fs_=9.5)
        d += elm.Dot().at((xled, ymid))
        d += elm.LED().at((xled, ymid)).to((xled, ydn))
        lab(d, (xled + 0.85, (ymid + ydn) / 2), "LED\n阳极 g10\n阴极 g8", fs_=9.5)
        d += elm.Resistor().endpoints((xro, y12), (xro, ydn)).color(PURPLE)
        lab(d, (xro + 0.5, (y12 + ydn) / 2), "RO 1k / 470 Ω\n过载时插上\ni8 → bn5", fs_=9.5, color=PURPLE)
        _par_arrow(d, (xn, y12 - 0.3), (xn, ydn + 0.3), (-0.55, 0.0))
        # ---- 采样与滤波 ----
        d += elm.Line().at(f["source"]).to((xm, ys))
        d += elm.Dot().at((xm, ys))
        colnote(d, (xm + 0.2, ys + 0.3), "第 13 列", "right", ofst=0.0)
        d += elm.Resistor().endpoints((xm, ys), (xm, yG))
        d += elm.Dot().at((xm, yG))
        lab(d, (xm + 0.5, (ys + yG) / 2 - 0.1), "R_S 10 Ω\nj13 → bp13", fs_=9.5)
        _par_arrow(d, (xm, ys - 0.2), (xm, yG + 0.2), (2.6, 0.0))
        lab(d, (xm + 2.8, (ys + yG) / 2 - 0.1), "I = V_S ÷ 10 Ω\n正常 12.4 mA\n跳闸 19.3 mA", fs_=9, color=C["cur"])
        ring(d, (xm, ys), "V_S（g13）", dx=1.2, dy=0.8)
        xf = 6.8
        d += elm.Resistor().endpoints((xm, ys), (xf, ys))
        lab(d, ((xm + xf) / 2, ys - 0.6), "R_F 10k（i13–i16）", ha="center", fs_=9.5)
        d += elm.Dot().at((xf, ys))
        d += elm.Capacitor(polar=True).endpoints((xf, ys), (xf, yG))
        d += elm.Dot().at((xf, yG))
        lab(d, (xf + 0.55, (ys + yG) / 2 - 0.2), "C_F 470 μF\n+ 脚 j16\n− 脚 → bp16", fs_=9.5)
        colnote(d, (xf - 0.2, ys + 0.3), "第 16 列", "left", ofst=0.0)
        xw = 1.0
        d += elm.Line().at((xf, ys)).to((xw, ys)).color(SIG).linewidth(1.8)
        d += elm.Line().at((xw, ys)).to((xw, a["in1"][1])).color(SIG).linewidth(1.8)
        d += elm.Line().at((xw, a["in1"][1])).to(a["in1"]).color(SIG).linewidth(1.8)
        colnote(d, ((xw + xf) / 2 - 0.6, ys - 0.3), "绿线 c22 → g16（滤波电压 → 6 脚）", "bottom", ofst=0.0)
        ring(d, (xf, ys), "V_−（h16）", dx=0.0, dy=1.2, ha="center")
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（黑表笔接 0 V 轨）；灰色小字 = 面包板孔位；绿色线 = 面包板上的绿色信号线；紫色 = 过载时才插的 RO；天蓝色箭头 = 电流方向。",
            "引脚：7805 正面朝你从左到右 1 IN、2 GND、3 OUT（f2、f3、f4）；IRLZ44N 背面（金属片）朝你从左到右 S、D、G（f13、f14、f15）。",
            "LM393 只用 B 组：5 脚 IN+、6 脚 IN−、7 脚 OUT（集电极开路，靠 R_PU 上拉到 5 V）；A 组 2、3 脚由 j21、j22 接地，1 脚空着。",
            "三条电源轨互不相连：+12 V 只给负载和 7805 的 IN，+5 V 只来自 7805 的 OUT。门限 V_+ 正常 0.193 V、跳闸后 0.147 V。",
        )
        for k, line in enumerate(notes):
            note(d, (xs - 2.2, yG - 1.0 - 0.6 * k), line)
    print("[图 22-p4-2] 7805 IN f2/GND f3/OUT f4；LM393 5/6/7/8/4；IRLZ44N S f13 D f14 G f15；RS j13、RF i13–i16、CF j16；负载 RN/LED/RLED/RO 在 +12 V 与第 8 列之间")
    save_schem(d, "22", "22_p4_2_schem_lab.png")

# ======================================================================================
# 14 积分电路：图 14-p4-1（14_p4_1_bb_integrator.png）→ 图 14-p4-2
# 面包板连线依据 code/figs/14_figs.py 的 bb12()：
#   电池 A + → tp1（+9 V），A− 与 B+ → tn2（0 V），B − → bn1（−9 V）；tn3–bp3
#   a5→+9 V，R1 82k b5–b9，R2 1k c9–c11，a11→0 V；j5→−9 V，R3 82k i5–i9，R4 1k h9–h11，j11→0 V
#   LM358 1 脚 f16：a16→+9 V（8 脚），j19→−9 V（4 脚），d17–d18（7–6），a19→0 V（5 脚）
#   R 1M i13–i17，C 1µF g16–g17，RP 1M j18→bp17，清零线 j16–j17，输入线 f13→e9（或 f9 / 0 V 轨）
# ======================================================================================
def node_14():
    SIG = TEAL
    with drawing(fontsize=11) as d:
        title(d, (-2.0, 6.9), "慢动作积分器：R = 1 MΩ、C = 1 μF（RC = 1 s），LM358 A 组，±9 V")
        # ---- 电源 ----
        x, yt, yb = -17.5, 5.0, 0.4
        ym = (yt + yb) / 2
        d += elm.Vdd().at((x, yt)).label("+9 V")
        d += elm.Battery().endpoints((x, ym), (x, yt)).reverse()
        lab(d, (x - 0.5, (ym + yt) / 2), "电池 A\n9 V", ha="right", fs_=10)
        d += elm.Dot().at((x, ym))
        d += elm.Battery().endpoints((x, yb), (x, ym)).reverse()
        lab(d, (x - 0.5, (ym + yb) / 2), "电池 B\n9 V", ha="right", fs_=10)
        d += elm.Vss().at((x, yb)).label("−9 V", "bottom")
        d += elm.Line().at((x, ym)).to((x + 1.3, ym))
        d += elm.Ground().at((x + 1.3, ym))
        colnote(d, (x + 0.15, yt - 0.3), "A 的 + → tp1（+9 V 轨）", "right", ofst=0.0)
        colnote(d, (x + 1.5, ym + 0.05), "A 的 − 与 B 的 + → tn2（0 V 轨）", "right", ofst=0.0)
        colnote(d, (x + 0.15, yb + 0.3), "B 的 − → bn1（−9 V 轨）", "right", ofst=0.0)
        lab(d, (x - 1.2, yb - 1.3), "上、下两条 0 V 轨", fs_=9, color=GRAY)
        lab(d, (x - 1.2, yb - 1.75), "由第 3 列黑线 tn3–bp3 连通", fs_=9, color=GRAY)
        # ---- 正输入分压（第 9 列上半） ----
        xp, ypn = -8.0, 2.6
        d += elm.Vdd().at((xp, 5.4)).label("+9 V")
        colnote(d, (xp + 0.2, 5.1), "橙线 a5", "right", ofst=0.0)
        d += elm.Resistor().endpoints((xp, 5.4), (xp, ypn))
        lab(d, (xp - 0.5, (5.4 + ypn) / 2), "R1 82k\nb5–b9", ha="right", fs_=9.5)
        d += elm.Dot().at((xp, ypn))
        d += elm.Resistor().endpoints((xp, ypn), (xp, 0.4))
        lab(d, (xp - 0.5, (ypn + 0.4) / 2), "R2 1k\nc9–c11", ha="right", fs_=9.5)
        d += elm.Ground().at((xp, 0.4))
        colnote(d, (xp + 0.2, 0.55), "黑线 a11", "right", ofst=0.0)
        ring(d, (xp, ypn), "+0.108 V（d9）", dx=-1.3, dy=0.0)
        # ---- 负输入分压（第 9 列下半） ----
        xq, yqn, yq0 = -5.6, -2.6, -0.6
        d += elm.Vss().at((xq, -5.4)).label("−9 V", "bottom")
        colnote(d, (xq + 0.2, -5.1), "蓝线 j5", "right", ofst=0.0)
        d += elm.Resistor().endpoints((xq, -5.4), (xq, yqn))
        lab(d, (xq - 0.5, (-5.4 + yqn) / 2), "R3 82k\ni5–i9", ha="right", fs_=9.5)
        d += elm.Dot().at((xq, yqn))
        d += elm.Resistor().endpoints((xq, yqn), (xq, yq0))
        lab(d, (xq - 0.5, (yqn + yq0) / 2 - 0.25), "R4 1k\nh9–h11", ha="right", fs_=9.5)
        d += elm.Line().at((xq, yq0)).to((xq - 1.0, yq0))
        d += elm.Ground().at((xq - 1.0, yq0))
        colnote(d, (xq - 1.0, yq0 + 0.45), "黑线 j11", "top", ofst=0.0)
        ring(d, (xq, yqn), "−0.108 V（g9）", dx=-1.3, dy=-0.6)
        # ---- 输入线（f13 的另一端） ----
        xi, xsel = -1.6, -3.4
        d += elm.Dot().at((xi, 0.0))
        d += elm.Line().at((xi, 0.0)).to((xsel, 0.0)).color(SIG).linewidth(1.8)
        d += elm.Line().at((xsel, 0.0)).to((xsel, ypn)).color(SIG).linewidth(1.8)
        d += elm.Line().at((xsel, ypn)).to((xp, ypn)).color(SIG).linewidth(1.8)
        colnote(d, ((xsel + xp) / 2 + 0.6, ypn + 0.3), "输入线 f13 → e9（现在：正输入）", "top", ofst=0.0)
        d += elm.Line().at((xsel, 0.0)).to((xsel, yqn)).color(SIG).linestyle("--").linewidth(1.4)
        d += elm.Line().at((xsel, yqn)).to((xq, yqn)).color(SIG).linestyle("--").linewidth(1.4)
        colnote(d, ((xsel + xq) / 2, yqn - 0.3), "改插 f9", "bottom", ofst=0.0)
        d += elm.Line().at((xsel, 0.0)).to((xsel - 0.9, -1.0)).color(SIG).linestyle("--").linewidth(1.4)
        d += elm.Ground().at((xsel - 0.9, -1.0))
        colnote(d, (xsel - 0.9, -1.75), "改插 0 V 轨", "bottom", ofst=0.0)
        ring(d, (xi, 0.0), "V_i（g13，第 13 列）", dx=0.0, dy=1.0, ha="center")
        # ---- 积分器（A 组） ----
        xn = 1.2
        d += elm.Resistor().endpoints((xi, 0.0), (xn, 0.0))
        lab(d, ((xi + xn) / 2, -0.6), "R 1M（i13–i17）", ha="center", fs_=10)
        _par_arrow(d, (xi + 0.2, 0.0), (xn - 0.2, 0.0), (0.0, 0.5))
        op = elm.Opamp(leads=True).right().anchor("in1").at((xn + 0.5, 0.0))
        d += op
        a = op.absanchors
        d += elm.Dot().at((xn, 0.0))
        d += elm.Line().at((xn, 0.0)).to(a["in1"])
        _pin(d, a["in1"], "2", dx=-0.2, dy=0.25)
        _pin(d, a["in2"], "3", dx=-0.2, dy=-0.25)
        _pin(d, a["out"], "1", dx=0.15, dy=0.25)
        lab(d, (a["in1"][0] + 0.85, a["out"][1]), "LM358\nA 组", fs_=9)
        colnote(d, (xn - 0.15, 2.1), "第 17 列（虚地）", "left", ofst=0.0)
        xo = a["out"][0] + 0.9
        yo = a["out"][1]
        d += elm.Line().at(a["out"]).to((xo, yo))
        d += elm.Dot().at((xo, yo))
        yc, yz = 3.0, 4.4
        d += elm.Line().at((xn, 0.0)).to((xn, yz))
        d += elm.Dot().at((xn, yc))
        d += elm.Capacitor().endpoints((xn, yc), (xo, yc))
        lab(d, ((xn + xo) / 2, yc + 0.6), "C 1 μF 薄膜（g16–g17）", ha="center", fs_=10)
        d += elm.Line().at((xo, yo)).to((xo, yz))
        d += elm.Dot().at((xo, yc))
        d += elm.Line().at((xn, yz)).to((xo, yz)).color(SIG).linewidth(1.8)
        lab(d, ((xn + xo) / 2, yz + 0.55), "清零线 j16–j17（拔掉 = 开始积分；第 10 步换成 10 MΩ = R_f）", ha="center", fs_=9, color=SIG)
        _par_arrow(d, (xn, yc), (xo, yc), (0.0, -0.55))
        lab(d, ((xn + xo) / 2, yc - 0.95), "I = V_i ÷ R ≈ 0.108 μA", ha="center", fs_=9, color=C["cur"])
        d += elm.Line().at((xo, yo)).to((xo + 1.6, yo))
        d += elm.Dot(open=True).at((xo + 1.6, yo))
        lab(d, (xo + 1.8, yo), "V_o\n第 16 列", fs_=10)
        ring(d, (xo + 0.8, yo), "V_o（h16）", dx=0.0, dy=-1.1, ha="center")
        colnote(d, (xo + 0.15, yo - 0.3), "1 脚 f16", "right", ofst=0.0)
        top, bot = a["vd"], a["vs"]
        d += elm.Line().at(top).to((top[0], top[1] + 0.5))
        d += elm.Vdd().at((top[0], top[1] + 0.5)).label("+9 V")
        _pin(d, top, "8", dx=0.25, dy=0.22)
        colnote(d, (top[0] - 0.15, top[1] + 0.35), "a16", "left", ofst=0.0)
        d += elm.Line().at(bot).to((bot[0], bot[1] - 0.5))
        d += elm.Vss().at((bot[0], bot[1] - 0.5)).label("−9 V", "bottom")
        _pin(d, bot, "4", dx=0.25, dy=-0.22)
        colnote(d, (bot[0] + 0.25, bot[1] - 0.6), "j19", "right", ofst=0.0)
        xr = a["in2"][0] - 0.8
        d += elm.Line().at(a["in2"]).to((xr, a["in2"][1]))
        d += elm.Dot().at((xr, a["in2"][1]))
        d += elm.Resistor().endpoints((xr, a["in2"][1]), (xr, -4.6))
        d += elm.Ground().at((xr, -4.6))
        lab(d, (xr - 0.5, (a["in2"][1] - 4.6) / 2), "R_P 1M\nj18 → 0 V 轨", ha="right", fs_=9.5)
        ring(d, (xr, a["in2"][1]), "V_+（h18）", dx=-1.1, dy=-0.5)
        # ---- B 组：接成跟随器、输入接地 ----
        bx, by = 11.0, -3.0
        title(d, (bx + 1.8, by + 2.7), "不用的 B 组（同一片 LM358）")
        opb = elm.Opamp(leads=True).right().anchor("in1").at((bx, by))
        d += opb
        b = opb.absanchors
        _pin(d, b["in1"], "6", dx=-0.2, dy=0.25)
        _pin(d, b["in2"], "5", dx=-0.2, dy=-0.25)
        _pin(d, b["out"], "7", dx=0.15, dy=0.25)
        d += elm.Line().at(b["in1"]).to((b["in1"][0] - 0.5, b["in1"][1])).color(SIG).linewidth(1.8)
        d += elm.Line().at((b["in1"][0] - 0.5, b["in1"][1])).to((b["in1"][0] - 0.5, b["in1"][1] + 1.0)).color(SIG).linewidth(1.8)
        d += elm.Line().at((b["in1"][0] - 0.5, b["in1"][1] + 1.0)).to((b["out"][0] + 0.5, b["in1"][1] + 1.0)).color(SIG).linewidth(1.8)
        d += elm.Line().at((b["out"][0] + 0.5, b["in1"][1] + 1.0)).to((b["out"][0] + 0.5, b["out"][1])).color(SIG).linewidth(1.8)
        d += elm.Line().at(b["out"]).to((b["out"][0] + 0.5, b["out"][1])).color(SIG).linewidth(1.8)
        colnote(d, ((b["in1"][0] + b["out"][0]) / 2, b["in1"][1] + 1.3), "绿短线 d17–d18（7 脚接 6 脚）", "top", ofst=0.0)
        d += elm.Line().at(b["in2"]).to((b["in2"][0] - 0.6, b["in2"][1]))
        d += elm.Ground().at((b["in2"][0] - 0.6, b["in2"][1]))
        colnote(d, (b["in2"][0] - 0.8, b["in2"][1] + 0.3), "黑线 a19", "left", ofst=0.0)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（与面包板图同名，黑表笔接 0 V）；灰色小字 = 面包板孔位；小黑字 = LM358 引脚号；绿色 = 面包板上的绿色信号线，虚线 = 输入线的另两种插法；天蓝色箭头 = 电流方向。",
            "所有 +9 V、−9 V、0 V 符号分别是同一条电源轨；8 脚（e16）、4 脚（f19）同时给 A、B 两组供电。A 组：1 脚 OUT f16、2 脚 IN− f17、3 脚 IN+ f18；B 组：7 脚 e17、6 脚 e18、5 脚 e19。",
            "电流 I 从输入经 R 流到虚地，再全部流进电容，输出以每秒 −V_i ÷ RC ≈ −0.108 V 的速度爬；1 μF 用薄膜电容，没有正负极。",
        )
        for k, line in enumerate(notes):
            note(d, (-16.0, -6.6 - 0.6 * k), line)
    print("[图 14-p4-2] ±9 V；+0.108 V 分压 b5–b9/c9–c11，−0.108 V 分压 i5–i9/h9–h11；R i13–i17、C g16–g17、清零线 j16–j17、RP j18→0 V；LM358 8/4/1/2/3，B 组 5/6/7")
    save_schem(d, "14", "14_p4_2_schem_lab.png")

# ---------------- 13 以后共用的小工具 ----------------
def _bat2(d, x, yt, yb, n_top, n_mid, n_bot, n_gnd, gname="GND", t1="电池 A", t2="电池 B"):
    """两节 9 V 串联（±9 V）。n_* 是灰色孔位小字（照抄面包板图），gname 是地线名。"""
    ym = (yt + yb) / 2
    d += elm.Vdd().at((x, yt)).label("+9 V")
    d += elm.Battery().endpoints((x, ym), (x, yt)).reverse()
    lab(d, (x - 0.5, (ym + yt) / 2), t1 + "\n9 V", ha="right", fs_=10)
    d += elm.Dot().at((x, ym))
    d += elm.Battery().endpoints((x, yb), (x, ym)).reverse()
    lab(d, (x - 0.5, (ym + yb) / 2), t2 + "\n9 V", ha="right", fs_=10)
    d += elm.Vss().at((x, yb)).label("−9 V", "bottom")
    d += elm.Line().at((x, ym)).to((x + 1.3, ym))
    d += elm.Ground().at((x + 1.3, ym)).label(gname, "bottom")
    colnote(d, (x + 0.15, yt - 0.3), n_top, "right", ofst=0.0)
    colnote(d, (x + 1.5, ym + 0.05), n_mid, "right", ofst=0.0)
    colnote(d, (x + 0.15, yb + 0.3), n_bot, "right", ofst=0.0)
    lab(d, (x - 1.2, yb - 1.4), n_gnd, fs_=9, color=GRAY)


def _opa_pwr(d, op, top=("8", "+9 V", "a14"), bot=("4", "−9 V", "j17"), flip=False):
    """运放电源脚（vd 在上、vs 在下；flip=True 时运放已 .flip()，vs 在上）：(引脚号, 电源名, 孔位)。"""
    a = op.absanchors
    t, b = (a["vs"], a["vd"]) if flip else (a["vd"], a["vs"])
    d += elm.Line().at(t).to((t[0], t[1] + 0.5))
    d += elm.Vdd().at((t[0], t[1] + 0.5)).label(top[1])
    _pin(d, t, top[0], dx=0.25, dy=0.22)
    colnote(d, (t[0] - 0.15, t[1] + 0.35), top[2], "left", ofst=0.0)
    d += elm.Line().at(b).to((b[0], b[1] - 0.5))
    if bot[1].startswith("−"):
        d += elm.Vss().at((b[0], b[1] - 0.5)).label(bot[1], "bottom")
    else:
        d += elm.Ground().at((b[0], b[1] - 0.5)).label(bot[1], "bottom")
    _pin(d, b, bot[0], dx=0.25, dy=-0.22)
    colnote(d, (b[0] + 0.25, b[1] - 0.6), bot[2], "right", ofst=0.0)


def _follower_b(d, bx, by, short_note, gnd_note, gname="GND", ttl="不用的 B 组（同一片 LM358）", pins=("6", "5", "7")):
    """LM358 B 组接成跟随器：7 脚接 6 脚，5 脚接地。(bx, by) 是 6 脚（反相端）位置。"""
    title(d, (bx + 1.8, by + 2.7), ttl)
    opb = elm.Opamp(leads=True).right().anchor("in1").at((bx, by))
    d += opb
    b = opb.absanchors
    _pin(d, b["in1"], pins[0], dx=-0.2, dy=0.25)
    _pin(d, b["in2"], pins[1], dx=-0.2, dy=-0.25)
    _pin(d, b["out"], pins[2], dx=0.15, dy=0.25)
    xl, xr, yt = b["in1"][0] - 0.5, b["out"][0] + 0.5, b["in1"][1] + 1.0
    for p, q in (((b["in1"]), (xl, b["in1"][1])), ((xl, b["in1"][1]), (xl, yt)), ((xl, yt), (xr, yt)),
                 ((xr, yt), (xr, b["out"][1])), ((xr, b["out"][1]), b["out"])):
        d += elm.Line().at(p).to(q).color(TEAL).linewidth(1.8)
    colnote(d, ((xl + xr) / 2, yt + 0.3), short_note, "top", ofst=0.0)
    d += elm.Line().at(b["in2"]).to((b["in2"][0] - 0.6, b["in2"][1]))
    d += elm.Ground().at((b["in2"][0] - 0.6, b["in2"][1])).label(gname, "bottom")
    colnote(d, (b["in2"][0] - 0.8, b["in2"][1] + 0.3), gnd_note, "left", ofst=0.0)
    lab(d, (b["in1"][0] + 1.2, b["in2"][1] - 1.1), "8、4 脚和 A 组共用", ha="center", fs_=8.5, color=GRAY)


# ======================================================================================
# 18 微分电路：图 18-p4-1（18_p4_1_breadboard.png）→ 图 18-p4-3
# 面包板连线依据 code/figs/18_figs.py：LM358 1–4 脚 f14–f17、8–5 脚 e14–e17；a14→+9 V，j17→−9 V，j16→GND，
#   a17→GND，c15–c16；R1 h4–h8，C i8–i12，j12–j15，h15–h20，Rf i20–i24，Cf j20–j24，g14–g24；T-28–B-28；
#   信号源 → j4，地 → B-2；电池 + → T+1，中点 → T-3，− → B+1
# ======================================================================================
def node_18():
    SIG, OUT, INP = TEAL, C["vout"], BLUE
    with drawing(fontsize=11) as d:
        title(d, (-2.0, 6.9), "实用微分器：R1 1 kΩ + C 100 nF 输入，Rf 10 kΩ ∥ Cf 10 nF 反馈，LM358 A 组，±9 V")
        _bat2(d, -17.0, 5.0, 0.4, "第一节 + → 上边 +9 V 轨（第 1 列）", "中点 → 上边 GND 轨（第 3 列）",
              "第二节 − → 下边 −9 V 轨（第 1 列）", "上、下两条 GND 轨\n在第 28 列用黑线连通", t1="第一节", t2="第二节")
        # ---- 信号源与输入支路 ----
        xs, xj4, x8, x12, x15 = -10.0, -8.4, -5.6, -2.8, -0.4
        d += elm.SourceSin().endpoints((xs, -2.2), (xs, 0.0))
        lab(d, (xs - 0.6, -1.1), "信号源\n手机 / 电位器", ha="right", fs_=10)
        d += elm.Ground().at((xs, -2.2)).label("GND", "bottom")
        colnote(d, (xs + 0.2, -2.45), "地线 → 下边 GND 轨（第 2 列）", "right", ofst=0.0)
        d += elm.Line().at((xs, 0.0)).to((xj4, 0.0)).color(INP).linewidth(1.8)
        colnote(d, ((xs + xj4) / 2, 0.3), "蓝线 → j4", "top", ofst=0.0)
        d += elm.Dot().at((xj4, 0.0))
        ring(d, (xj4, 0.0), "V_in（j4）", dx=0.0, dy=-1.1, ha="center")
        d += elm.Resistor().endpoints((xj4, 0.0), (x8, 0.0))
        lab(d, ((xj4 + x8) / 2, 0.65), "R1 1 kΩ（h4–h8）", ha="center", fs_=10)
        d += elm.Dot().at((x8, 0.0))
        colnote(d, (x8, -0.3), "第 8 列", "bottom", ofst=0.0)
        d += elm.Capacitor().endpoints((x8, 0.0), (x12, 0.0))
        lab(d, ((x8 + x12) / 2, 0.65), "C 100 nF（i8–i12）", ha="center", fs_=10)
        _par_arrow(d, (xj4, 0.0), (x12, 0.0), (0.0, -0.55))
        lab(d, ((xj4 + x12) / 2 + 0.3, -1.05), "i = C × dV_in/dt", ha="left", fs_=9, color=C["cur"])
        d += elm.Line().at((x12, 0.0)).to((x15, 0.0)).color(SIG).linewidth(1.8)
        colnote(d, ((x12 + x15) / 2, -0.3), "绿线 j12 → j15", "bottom", ofst=0.0)
        d += elm.Dot().at((x15, 0.0))
        # ---- 运放 A 组 ----
        op = elm.Opamp(leads=True).right().anchor("in1").at((x15 + 0.7, 0.0))
        d += op
        a = op.absanchors
        d += elm.Line().at((x15, 0.0)).to(a["in1"])
        _pin(d, a["in1"], "2", dx=-0.2, dy=0.25)
        _pin(d, a["in2"], "3", dx=-0.2, dy=-0.25)
        _pin(d, a["out"], "1", dx=0.15, dy=0.25)
        lab(d, (a["in1"][0] + 0.85, a["out"][1]), "LM358\nA 组", fs_=9)
        ring(d, (x15, 0.0), "虚地（h15）", dx=-0.9, dy=1.2)
        _opa_pwr(d, op)
        xg = a["in2"][0] - 0.6
        d += elm.Line().at(a["in2"]).to((xg, a["in2"][1]))
        d += elm.Ground().at((xg, a["in2"][1])).label("GND", "bottom")
        colnote(d, (xg - 0.2, a["in2"][1] - 0.3), "黑线 j16", "left", ofst=0.0)
        # ---- 反馈 Rf ∥ Cf（第 20 列 ↔ 第 24 列） ----
        x20, x24, yr, ycf = x15 + 1.4, a["out"][0] + 1.0, 2.7, 4.1
        yo = a["out"][1]
        d += elm.Line().at((x15, 0.0)).to((x15, yr)).color(SIG).linewidth(1.8)
        d += elm.Line().at((x15, yr)).to((x20, yr)).color(SIG).linewidth(1.8)
        colnote(d, (x15 - 0.3, yr - 0.4), "绿线\nh15 → h20", "left", ofst=0.0)
        d += elm.Dot().at((x20, yr))
        d += elm.Line().at((x20, yr)).to((x20, ycf))
        d += elm.Resistor().endpoints((x20, yr), (x24, yr))
        lab(d, ((x20 + x24) / 2, yr - 0.6), "Rf 10 kΩ（i20–i24）", ha="center", fs_=10)
        d += elm.Capacitor().endpoints((x20, ycf), (x24, ycf))
        lab(d, ((x20 + x24) / 2, ycf + 0.6), "Cf 10 nF（j20–j24）", ha="center", fs_=10)
        colnote(d, (x20, ycf + 0.3), "第 20 列", "top", ofst=0.0)
        colnote(d, (x24, ycf + 0.3), "第 24 列", "top", ofst=0.0)
        d += elm.Line().at(a["out"]).to((x24, yo)).color(OUT).linewidth(1.8)
        colnote(d, ((a["out"][0] + x24) / 2 + 0.1, yo - 0.3), "橙线 g14 → g24", "bottom", ofst=0.0)
        d += elm.Line().at((x24, yo)).to((x24, ycf))
        d += elm.Dot().at((x24, yr))
        d += elm.Dot().at((x24, yo))
        d += elm.Line().at((x24, yo)).to((x24 + 1.6, yo))
        d += elm.Dot(open=True).at((x24 + 1.6, yo))
        lab(d, (x24 + 1.8, yo), "V_o", fs_=11)
        ring(d, (x24 + 0.8, yo), "V_o（h24）", dx=0.0, dy=-1.1, ha="center")
        # ---- B 组 ----
        _follower_b(d, 12.0, 2.6, "绿短线 c15–c16（6、7 脚短接）", "黑线 a17")
        # ---- 慢速实验换件 ----
        bx0, by0, bx1, by1 = 8.6, -6.9, 16.6, -0.8
        _dbox(d, bx0, by0, bx1, by1)
        lab(d, (bx0 + 0.2, by1 - 0.4), "第④步慢速实验换件（虚线框内）：", fs_=9.5)
        xp = bx0 + 1.4
        d += elm.Vdd().at((xp, by1 - 1.6)).label("+9 V")
        d += elm.Resistor(scale=0.7).endpoints((xp, by1 - 1.6), (xp, by1 - 3.0))
        lab(d, (xp + 0.45, by1 - 2.3), "82 kΩ", fs_=9)
        pot = elm.Potentiometer(scale=0.8).endpoints((xp, by1 - 3.0), (xp, by0 + 0.9))
        d += pot
        lab(d, (xp - 0.5, (by1 - 3.0 + by0 + 0.9) / 2), "10 kΩ\n电位器", ha="right", fs_=9)
        d += elm.Ground().at((xp, by0 + 0.9))
        d += elm.Line().at(pot.tap).to((xp + 1.2, pot.tap[1])).color(INP).linewidth(1.6)
        lab(d, (xp + 1.3, pot.tap[1]), "滑动端 → j4", fs_=9)
        xt = bx0 + 3.9
        lab(d, (xt, by1 - 1.2), "C → 100 μF 电解：", fs_=9)
        d += elm.Capacitor(polar=True, scale=0.7).endpoints((xt + 0.4, by1 - 1.85), (xt + 2.2, by1 - 1.85))
        lab(d, (xt, by1 - 2.5), "+ 脚插 i8（朝 R1 / 输入）", fs_=9)
        lab(d, (xt, by1 - 3.1), "Rf → 100 kΩ（R_f C = 10 s）", fs_=9)
        lab(d, (xt, by0 + 0.45), "对比振铃：R1 换导线、拔掉 Cf", fs_=9)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（黑表笔接 GND）；灰色小字 = 面包板孔位；小黑字 = LM358 引脚号；蓝色 = 输入信号线，橙色 = 输出线，绿色 = 反馈 / 其他连线；天蓝色箭头 = 电流方向。",
            "所有 +9 V、−9 V、GND 符号分别是同一条电源轨；8 脚（e14 → a14）、4 脚（f17 → j17）同时给 A、B 两组供电。A 组：1 脚 OUT f14、2 脚 IN− f15、3 脚 IN+ f16；B 组：7 脚 e15、6 脚 e16、5 脚 e17。",
            "输出节点是整个第 24 列（g24 橙线、i24 Rf、j24 Cf）；空着的 f24、h24 可以插表笔，面包板图右侧小字「测输出：红表笔 h24」就插在这一列。",
        )
        for k, line in enumerate(notes):
            note(d, (-19.0, -7.4 - 0.6 * k), line)
    print("[图 18-p4-3] ±9 V；R1 h4–h8、C i8–i12、j12–j15 → 2 脚；Rf i20–i24 ∥ Cf j20–j24；g14–g24；3 脚 j16 → GND；B 组 c15–c16、a17")
    save_schem(d, "18", "18_p4_3_schem_lab.png")

# ======================================================================================
# 10 电压比较器：图 10-p4-1（10_p4_1_breadboard.png）→ 图 10-p4-2
# 面包板连线依据 code/figs/10_figs.py：LM393 1–4 脚 f12–f15、8–5 脚 e12–e15；a12→+5 V，g15→GND；
#   R2 g12–g14，R3 h8–h12 + j8→+5 V，h13–h22，R1 i14–i18，Ra i22–i26 + j26→+5 V，Rb g22–g28 + j28→GND；
#   f22→d14，j12→b15（橙），a4→+5 V，R4 b4–b8，LED c8(+)–c13；T+30–B+30，T-29–B-29；电源 + T+1、− T-3；电位器滑动端→j18
# ======================================================================================
def node_10():
    SIG, OUT, INP = TEAL, C["vout"], BLUE
    with drawing(fontsize=11) as d:
        title(d, (0.0, 6.4), "施密特比较器 + LED 指示：LM393 A 组做比较、B 组点 LED，5 V 单电源")
        # ---- 电源 ----
        x, yt, yb = -16.0, 3.6, -0.6
        d += elm.Vdd().at((x, yt)).label("+5 V")
        d += elm.Battery().endpoints((x, yb), (x, yt)).reverse()
        lab(d, (x - 0.5, (yt + yb) / 2), "5 V\n直流电源", ha="right", fs_=10)
        d += elm.Ground().at((x, yb)).label("GND", "bottom")
        colnote(d, (x + 0.15, yt - 0.3), "+ → 上边 +5 V 轨（第 1 列）", "right", ofst=0.0)
        colnote(d, (x + 0.3, yb + 0.3), "− → 上边 GND 轨（第 3 列）", "right", ofst=0.0)
        lab(d, (x - 1.2, yb - 1.6), "上下两条 +5 V 轨在第 30 列、", fs_=9, color=GRAY)
        lab(d, (x - 1.2, yb - 2.05), "两条 GND 轨在第 29 列连通", fs_=9, color=GRAY)
        # ---- 电位器 → 第 18 列 → R1 → 第 14 列 ----
        xpt, x18, x14 = -10.5, -7.6, -4.0
        d += elm.Vdd().at((xpt, 2.0)).label("+5 V")
        pot = elm.Potentiometer().endpoints((xpt, 2.0), (xpt, -2.0))
        d += pot
        lab(d, (xpt - 0.5, 0.0), "电位器\n10 kΩ", ha="right", fs_=10)
        d += elm.Ground().at((xpt, -2.0)).label("GND", "bottom")
        d += elm.Line().at(pot.tap).to((x18, 0.0)).color(INP).linewidth(1.8)
        colnote(d, ((pot.tap[0] + x18) / 2, 0.3), "蓝线 → j18", "top", ofst=0.0)
        d += elm.Dot().at((x18, 0.0))
        ring(d, (x18, 0.0), "输入（j18）", dx=0.0, dy=-0.9, ha="center")
        d += elm.Resistor().endpoints((x18, 0.0), (x14, 0.0))
        lab(d, ((x18 + x14) / 2, 0.65), "R1 10 kΩ（i14–i18）", ha="center", fs_=10)
        d += elm.Dot().at((x14, 0.0))
        # ---- A 组 ----
        opa = elm.Opamp(leads=True).right().flip().anchor("in2").at((x14 + 1.2, 0.0))
        d += opa
        a = opa.absanchors
        d += elm.Line().at((x14, 0.0)).to(a["in2"])
        _pin(d, a["in2"], "3", dx=-0.2, dy=0.25)
        _pin(d, a["in1"], "2", dx=-0.2, dy=-0.25)
        _pin(d, a["out"], "1", dx=0.15, dy=0.25)
        lab(d, (a["in2"][0] + 0.8, a["out"][1]), "LM393\nA 组", fs_=9)
        ring(d, (x14, 0.0), "同相端（g14）", dx=-0.7, dy=1.1)
        t, b = a["vs"], a["vd"]
        d += elm.Line().at(t).to((t[0], t[1] + 0.5))
        d += elm.Vdd().at((t[0], t[1] + 0.5)).label("+5 V")
        _pin(d, t, "8", dx=0.25, dy=0.22)
        colnote(d, (t[0] + 0.25, t[1] + 0.6), "红线 a12", "right", ofst=0.0)
        d += elm.Line().at(b).to((b[0], b[1] - 0.5))
        d += elm.Ground().at((b[0], b[1] - 0.5)).label("GND", "bottom")
        _pin(d, b, "4", dx=0.25, dy=-0.22)
        colnote(d, (b[0] + 0.25, b[1] - 0.7), "黑线 g15", "right", ofst=0.0)
        x12 = a["out"][0] + 0.9
        yo = a["out"][1]
        d += elm.Line().at(a["out"]).to((x12, yo))
        d += elm.Dot().at((x12, yo))
        # R2 正反馈（g12–g14），从上方绕回同相端
        yr2 = 2.6
        d += elm.Line().at((x14, 0.0)).to((x14, yr2))
        d += elm.Resistor().endpoints((x14, yr2), (x12, yr2))
        lab(d, ((x14 + x12) / 2, yr2 + 0.65), "R2 100 kΩ（g12–g14）", ha="center", fs_=10)
        d += elm.Line().at((x12, yr2)).to((x12, yo))
        # R3 上拉（h8–h12），j8 → +5 V
        x3 = x12 + 1.3
        d += elm.Line().at((x12, yo)).to((x3, yo))
        d += elm.Dot().at((x3, yo))
        d += elm.Resistor().endpoints((x3, yo), (x3, yo + 3.2))
        d += elm.Vdd().at((x3, yo + 3.2)).label("+5 V")
        lab(d, (x3 + 0.45, yo + 1.6), "R3 2.2 kΩ\nh8–h12\n（红线 j8）", fs_=9.5)
        ring(d, (x12, yo), "输出（h12）", dx=0.0, dy=-1.3, ha="center")
        colnote(d, (x12 + 0.15, yo - 0.35), "第 12 列", "right", ofst=0.0)
        # ---- 2.5 V 基准（第 22 列） ----
        x22, yref = x14 - 0.2, -3.6
        d += elm.Vdd().at((x22 - 4.4, yref)).label("+5 V")
        d += elm.Resistor().endpoints((x22 - 4.4, yref), (x22, yref))
        lab(d, (x22 - 2.0, yref - 0.65), "Ra 10 kΩ（i22–i26，红线 j26）", ha="center", fs_=9.5)
        d += elm.Dot().at((x22, yref))
        d += elm.Resistor().endpoints((x22, yref), (x22, yref - 2.6))
        lab(d, (x22 - 0.5, yref - 1.3), "Rb 10 kΩ\ng22–g28\n（黑线 j28）", ha="right", fs_=9.5)
        d += elm.Ground().at((x22, yref - 2.6)).label("GND", "bottom")
        ring(d, (x22, a["in1"][1] - 0.9), "基准 2.5 V（h13）", dx=-1.2, dy=0.0)
        colnote(d, (x22 + 0.2, yref - 0.3), "第 22 列", "right", ofst=0.0)
        yin1 = a["in1"][1]
        d += elm.Line().at((x22, yref)).to((x22, yin1)).color(SIG).linewidth(1.8)
        d += elm.Line().at((x22, yin1)).to(a["in1"]).color(SIG).linewidth(1.8)
        colnote(d, (x22 + 0.15, (yref + yin1) / 2 + 0.3), "绿线 h13 → h22", "right", ofst=0.0)
        # ---- B 组：LED 驱动 ----
        bx = x3 + 3.0
        opb = elm.Opamp(leads=True).right().flip().anchor("in2").at((bx, yo))
        d += opb
        bb_ = opb.absanchors
        d += elm.Line().at((x3, yo)).to(bb_["in2"]).color(OUT).linewidth(1.8)
        colnote(d, ((x3 + bx) / 2, yo + 0.3), "橙线 j12 → b15", "top", ofst=0.0)
        _pin(d, bb_["in2"], "5", dx=-0.2, dy=0.25)
        _pin(d, bb_["in1"], "6", dx=-0.2, dy=-0.25)
        _pin(d, bb_["out"], "7", dx=0.15, dy=0.25)
        lab(d, (bb_["in2"][0] + 0.8, bb_["out"][1]), "LM393\nB 组", fs_=9)
        lab(d, (bb_["vd"][0], bb_["vd"][1] - 0.5), "8、4 脚和 A 组共用", ha="center", fs_=8.5, color=GRAY)
        xb6 = bx - 0.7
        d += elm.Line().at((x22, yref)).to((xb6, yref)).color(SIG).linewidth(1.8)
        d += elm.Line().at((xb6, yref)).to((xb6, bb_["in1"][1])).color(SIG).linewidth(1.8)
        d += elm.Line().at((xb6, bb_["in1"][1])).to(bb_["in1"]).color(SIG).linewidth(1.8)
        colnote(d, ((x22 + xb6) / 2 + 1.0, yref - 0.3), "绿线 f22 → d14（基准 → 6 脚）", "bottom", ofst=0.0)
        d += elm.Dot().at((x22, yref))
        xl = bb_["out"][0] + 0.8
        yb7 = bb_["out"][1]
        d += elm.Line().at(bb_["out"]).to((xl, yb7))
        d += elm.LED().at((xl, yb7 + 2.2)).to((xl, yb7))
        lab(d, (xl + 1.0, yb7 + 1.1), "LED\n长脚 c8（+）\n短脚 c13（7 脚）", fs_=9.5)
        d += elm.Resistor().endpoints((xl, yb7 + 4.6), (xl, yb7 + 2.2))
        lab(d, (xl + 0.5, yb7 + 3.4), "R4 1 kΩ（b4–b8）", fs_=9.5)
        d += elm.Vdd().at((xl, yb7 + 4.6)).label("+5 V")
        colnote(d, (xl + 0.2, yb7 + 4.9), "红线 a4", "right", ofst=0.0)
        d += elm.Arrow().at((xl - 0.45, yb7 + 4.0)).to((xl - 0.45, yb7 + 0.4)).color(C["cur"]).linewidth(1.2)
        lab(d, (xl - 0.95, yb7 + 2.2), "约 3 mA\n（A 路输出低时）", ha="right", fs_=8.5, color=C["cur"])
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（黑表笔接 GND）；灰色小字 = 面包板孔位；小黑字 = LM393 引脚号；蓝色 = 电位器送来的输入，橙色 = A 路输出，绿色 = 基准和其他连线；天蓝色箭头 = LED 电流。",
            "所有 +5 V、GND 符号分别是同一条电源轨。LM393：1 脚 OUTA f12、2 脚 IN−A f13、3 脚 IN+A f14、4 脚 GND f15；8 脚 VCC e12、7 脚 OUTB e13、6 脚 IN−B e14、5 脚 IN+B e15。两组都是开集电极输出，A 组靠 R3 上拉，B 组直接拉 LED 的阴极。",
            "基本比较器对照：拔掉 R2，同相端就等于输入，只剩一个 2.5 V 门限。LED 亮 = A 路输出低（输入低于门限）。",
        )
        for k, line in enumerate(notes):
            note(d, (-18.0, -8.0 - 0.6 * k), line)
    print("[图 10-p4-2] 5 V；R1 i14–i18、R2 g12–g14、R3 h8–h12；Ra/Rb 第 22 列 → h13–h22、f22–d14；j12–b15；R4 b4–b8、LED c8–c13")
    save_schem(d, "10", "10_p4_2_schem_lab.png")

# ======================================================================================
# 20 有源滤波：图 20-p4-1（20_p4_1_breadboard.png）→ 图 20-p4-3
# 面包板连线依据 code/figs/20_figs.py：LM358 1–4 脚 f14–f17、8–5 脚 e14–e17；a14→+9 V，j17→−9 V；
#   a17→GND，c15–c16；g14–g15；g16–g20；R h20–h24；C j20–B-20；h14–h8；R 1 kΩ i8–i4；T-28–B-28；
#   耳机 → j4、地 → B-2；手机 → j24、地 → B-29；电池 + → T+1，中点 → T-3，− → B+1
# ======================================================================================
def node_20():
    SIG, OUT, INP = TEAL, C["vout"], BLUE
    with drawing(fontsize=11) as d:
        title(d, (-2.0, 7.0), "一阶有源低通：R 16 kΩ + C 10 nF，LM358 A 组接成跟随器，±9 V（fc ≈ 995 Hz）")
        _bat2(d, -19.0, 5.0, 0.4, "第一节 + → 上边 +9 V 轨（第 1 列）", "中点 → 上边 GND 轨（第 3 列）",
              "第二节 − → 下边 −9 V 轨（第 1 列）", "上、下两条 GND 轨\n在第 28 列用黑线连通", t1="第一节", t2="第二节")
        # ---- 手机 → 第 24 列 → R → 第 20 列 ----
        xs, x24, x20, xd = -13.6, -11.6, -7.6, -5.6
        d += elm.SourceSin().endpoints((xs, -2.2), (xs, 0.0))
        lab(d, (xs - 0.6, -1.1), "手机\n音频输出\nL 脚", ha="right", fs_=10)
        d += elm.Ground().at((xs, -2.2)).label("GND", "bottom")
        colnote(d, (xs + 0.2, -2.45), "地脚 → 下边 GND 轨（第 29 列）", "right", ofst=0.0)
        d += elm.Line().at((xs, 0.0)).to((x24, 0.0)).color(INP).linewidth(1.8)
        colnote(d, ((xs + x24) / 2, 0.3), "蓝线 → j24", "top", ofst=0.0)
        d += elm.Dot().at((x24, 0.0))
        ring(d, (x24, 0.0), "输入（g24）", dx=0.0, dy=1.2, ha="center")
        d += elm.Resistor().endpoints((x24, 0.0), (x20, 0.0))
        lab(d, ((x24 + x20) / 2, -0.65), "R 16 kΩ（h20–h24）", ha="center", fs_=10)
        d += elm.Dot().at((x20, 0.0))
        d += elm.Capacitor().endpoints((x20, 0.0), (x20, -2.6))
        lab(d, (x20 - 0.5, -1.3), "C 10 nF\n（标 103）\nj20 → 下边 GND 轨", ha="right", fs_=9.5)
        d += elm.Ground().at((x20, -2.6)).label("GND", "bottom")
        ring(d, (x20, 0.0), "滤波节点（f20）", dx=0.0, dy=1.2, ha="center")
        colnote(d, (x20 + 0.15, 0.3), "第 20 列", "right", ofst=0.0)
        # 对照实验：1 kΩ 并在 C 上（虚线）
        d += elm.Line().at((x20, 0.0)).to((xd, 0.0))
        d += elm.Dot().at((xd, 0.0))
        d += elm.Resistor().endpoints((xd, 0.0), (xd, -2.6)).linestyle("--").color(GRAY)
        d += elm.Ground().at((xd, -2.6)).color(GRAY)
        lab(d, (xd, -3.6), "⑥ 对照：1 kΩ 并在 C 上\n（i20 到地，虚线）", ha="center", fs_=8.5, color=GRAY)
        # ---- A 组跟随器 ----
        opa = elm.Opamp(leads=True).right().flip().anchor("in2").at((xd + 2.6, 0.0))
        d += opa
        a = opa.absanchors
        d += elm.Line().at((xd, 0.0)).to(a["in2"]).color(SIG).linewidth(1.8)
        colnote(d, ((xd + a["in2"][0]) / 2 - 0.2, 0.3), "绿线 g16 → g20", "top", ofst=0.0)
        _pin(d, a["in2"], "3", dx=-0.2, dy=0.25)
        _pin(d, a["in1"], "2", dx=-0.2, dy=-0.25)
        _pin(d, a["out"], "1", dx=0.15, dy=0.25)
        lab(d, (a["in2"][0] + 0.8, a["out"][1]), "LM358\nA 组", fs_=9)
        _opa_pwr(d, opa, flip=True)
        x14, yo = a["out"][0] + 0.9, a["out"][1]
        d += elm.Line().at(a["out"]).to((x14, yo))
        d += elm.Dot().at((x14, yo))
        xl, yl = a["in1"][0] - 0.6, -3.7
        for p, q in ((a["in1"], (xl, a["in1"][1])), ((xl, a["in1"][1]), (xl, yl)), ((xl, yl), (x14, yl)), ((x14, yl), (x14, yo))):
            d += elm.Line().at(p).to(q).color(SIG).linewidth(1.8)
        colnote(d, ((xl + x14) / 2, yl - 0.3), "绿短线 g14–g15（1 脚接 2 脚）", "bottom", ofst=0.0)
        # ---- 输出 → 第 8 列 → 1 kΩ → 耳机 ----
        x8, x4 = x14 + 2.6, x14 + 6.0
        d += elm.Line().at((x14, yo)).to((x8, yo)).color(OUT).linewidth(1.8)
        colnote(d, ((x14 + x8) / 2, yo + 0.3), "橙线 h14 → h8", "top", ofst=0.0)
        d += elm.Dot().at((x8, yo))
        ring(d, (x8, yo), "输出（g8）", dx=0.0, dy=1.3, ha="center")
        d += elm.Resistor().endpoints((x8, yo), (x4, yo))
        lab(d, ((x8 + x4) / 2, yo - 0.65), "R 1 kΩ（i8–i4）\n耳机限流", ha="center", fs_=9.5)
        sp = elm.Speaker().right().at((x4 + 0.8, yo + 0.25))
        d += elm.Line().at((x4, yo)).to((x4 + 0.8, yo + 0.25))
        d += sp
        s_ = sp.absanchors
        d += elm.Line().at(s_["in2"]).to((s_["in2"][0], yo - 1.8))
        d += elm.Ground().at((s_["in2"][0], yo - 1.8)).label("GND", "bottom")
        lab(d, (x4 + 2.3, yo + 0.7), "耳机（约 32 Ω）\n3.5 mm 转接板", fs_=9.5)
        colnote(d, (x4 + 0.6, yo + 1.1), "信号脚（L、R 并联）→ j4", "top", ofst=0.0)
        colnote(d, (s_["in2"][0] + 0.2, yo - 1.3), "地脚 → 下边 GND 轨（第 2 列）", "right", ofst=0.0)
        # ⑤ 负载对照（虚线）
        d += elm.Resistor().endpoints((x8, yo), (x8, yl)).linestyle("--").color(GRAY)
        d += elm.Ground().at((x8, yl)).color(GRAY)
        lab(d, (x8 + 0.75, yo - 1.9), "⑤ 负载：拔掉耳机，\n1 kΩ 插 j8 到下边 GND 轨\n（虚线，表笔仍在 g8）", fs_=8.5, color=GRAY)
        # ---- B 组闲置 ----
        _follower_b(d, x14 + 7.4, 4.0, "绿短线 c15–c16（7 脚接 6 脚）", "黑线 a17")
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（黑表笔接 GND）；灰色小字 = 面包板孔位；小黑字 = LM358 引脚号；蓝色 = 手机送来的输入，橙色 = 运放输出，绿色 = 芯片周围的短接和连线；灰色虚线 = 后面对照实验才接的 1 kΩ。",
            "所有 +9 V、−9 V、GND 符号分别是同一条电源轨。LM358：1 脚 OUT f14、2 脚 IN− f15、3 脚 IN+ f16、4 脚 V− f17；8 脚 V+ e14、7 脚 e15、6 脚 e16、5 脚 e17（B 组）。",
            "⑦ 慢速版：C 换 100 µF 电解电容（+ 脚插 j20，− 脚接地），手机换成一节 1.5 V 电池（正极朝 j24），τ = 16 kΩ × 100 µF = 1.6 s。",
        )
        for k, line in enumerate(notes):
            note(d, (-20.0, -6.6 - 0.6 * k), line)
    print("[图 20-p4-3] ±9 V；R h20–h24、C j20–GND、g16–g20、g14–g15、h14–h8、1 kΩ i8–i4；耳机 j4、手机 j24")
    save_schem(d, "20", "20_p4_3_schem_lab.png")

# ======================================================================================
# 24 振荡器：图 24-p4-1（24_p4_1_breadboard.png）→ 图 24-p4-3
# 面包板连线依据 code/figs/24_figs.py：LM358 1–4 脚 f14–f17、8–5 脚 e14–e17；a14→+5 V，j17→GND；a17→GND，c15–c16；
#   g14–g11（橙）；R h11–h15；C j15–B-15；Rc i11–i16；Ra h16–h20 + j20→+5 V；g16–g22；Rb h22–h26 + j26→GND；
#   10 µF j11(+)–j7；1 kΩ i7–i3；T-29–B-29，T+30–B+30；电源 + → T+1，GND → T-3；耳机 → j3，地 → B-1
# ======================================================================================
def node_24():
    SIG, OUT = TEAL, C["vout"]
    with drawing(fontsize=11) as d:
        title(d, (0.0, 6.6), "弛张振荡器：R 10 kΩ + C 100 nF 定时，Ra、Rb、Rc 三只 10 kΩ 定门限，LM358 A 组，5 V 单电源")
        # ---- 电源 ----
        x, yt, yb = -12.5, 3.6, -0.6
        d += elm.Vdd().at((x, yt)).label("+5 V")
        d += elm.Battery().endpoints((x, yb), (x, yt)).reverse()
        lab(d, (x - 0.5, (yt + yb) / 2), "5 V\n电源模块", ha="right", fs_=10)
        d += elm.Ground().at((x, yb)).label("GND", "bottom")
        colnote(d, (x + 0.15, yt - 0.3), "+5 V → 上边 +5 V 轨（第 1 列）", "right", ofst=0.0)
        colnote(d, (x + 0.3, yb + 0.3), "GND → 上边 GND 轨（第 3 列）", "right", ofst=0.0)
        lab(d, (x - 1.2, yb - 1.6), "上下两条 GND 轨在第 29 列、", fs_=9, color=GRAY)
        lab(d, (x - 1.2, yb - 2.05), "两条 +5 V 轨在第 30 列连通", fs_=9, color=GRAY)
        # ---- A 组（同相端在上） ----
        opa = elm.Opamp(leads=True).right().flip().anchor("in2").at((0.0, 0.0))
        d += opa
        a = opa.absanchors
        _pin(d, a["in2"], "3", dx=-0.2, dy=0.25)
        _pin(d, a["in1"], "2", dx=-0.2, dy=-0.25)
        _pin(d, a["out"], "1", dx=0.15, dy=0.25)
        lab(d, (a["in2"][0] + 0.8, a["out"][1]), "LM358\nA 组", fs_=9)
        _opa_pwr(d, opa, top=("8", "+5 V", "a14"), bot=("4", "GND", "j17（黑线）"), flip=True)
        yo = a["out"][1]
        x14, x11 = a["out"][0] + 0.6, a["out"][0] + 2.6
        d += elm.Line().at(a["out"]).to((x14, yo))
        d += elm.Dot().at((x14, yo))
        d += elm.Line().at((x14, yo)).to((x11, yo)).color(OUT).linewidth(1.8)
        colnote(d, ((x14 + x11) / 2, yo + 0.3), "橙线 g14 → g11", "top", ofst=0.0)
        d += elm.Dot().at((x11, yo))
        ring(d, (x11, yo), "输出（f11）", dx=0.8, dy=-1.0)
        # ---- 门限：同相端第 16 列 ----
        x16, xa, x22 = -1.8, -3.4, -5.2
        d += elm.Line().at(a["in2"]).to((xa, 0.0))
        d += elm.Dot().at((x16, 0.0))
        d += elm.Dot().at((xa, 0.0))
        ring(d, (x16, 1.7), "同相端（j16）", dx=0.6, dy=0.0)
        yrc = 3.0
        d += elm.Line().at((x11, yo)).to((x11, yrc))
        d += elm.Resistor().endpoints((x11, yrc), (x16, yrc))
        lab(d, ((x11 + x16) / 2 + 1.2, yrc + 0.65), "Rc 10 kΩ（i11–i16，正反馈）", ha="center", fs_=10)
        d += elm.Line().at((x16, yrc)).to((x16, 0.0))
        d += elm.Resistor().endpoints((xa, 0.0), (xa, 2.4))
        d += elm.Vdd().at((xa, 2.4)).label("+5 V")
        lab(d, (xa - 0.45, 1.2), "Ra 10 kΩ\nh16–h20\n（红线 j20）", ha="right", fs_=9.5)
        d += elm.Line().at((xa, 0.0)).to((x22, 0.0)).color(SIG).linewidth(1.8)
        colnote(d, ((xa + x22) / 2, -0.3), "绿线 g16 → g22", "bottom", ofst=0.0)
        d += elm.Resistor().endpoints((x22, 0.0), (x22, -2.6))
        d += elm.Ground().at((x22, -2.6)).label("GND", "bottom")
        lab(d, (x22 - 0.45, -1.3), "Rb 10 kΩ\nh22–h26\n（黑线 j26）", ha="right", fs_=9.5)
        # ---- 定时：反相端第 15 列 ----
        x15, yk = -1.2, -4.1
        d += elm.Line().at(a["in1"]).to((x15, a["in1"][1]))
        d += elm.Line().at((x15, a["in1"][1])).to((x15, yk))
        d += elm.Dot().at((x15, yk))
        d += elm.Resistor().endpoints((x11, yk), (x15, yk))
        d += elm.Line().at((x11, yo)).to((x11, yk))
        lab(d, ((x11 + x15) / 2, yk + 0.6), "R 10 kΩ（h11–h15，定时）", ha="center", fs_=10)
        d += elm.Arrow().at((x11 - 0.8, yk - 0.5)).to((x15 + 0.8, yk - 0.5)).color(C["cur"]).linewidth(1.2)
        lab(d, ((x11 + x15) / 2, yk - 0.95), "输出高时给 C 充电（输出低时电流反向、C 放电）", ha="center", fs_=8.5, color=C["cur"])
        d += elm.Capacitor().endpoints((x15, yk), (x15, yk - 2.6))
        d += elm.Ground().at((x15, yk - 2.6)).label("GND", "bottom")
        lab(d, (x15 - 0.5, yk - 1.6), "C 100 nF（标 104）\nj15 → 下边 GND 轨", ha="right", fs_=9.5)
        ring(d, (x15, yk), "电容（i15）", dx=-1.0, dy=0.0)
        colnote(d, (x15 + 0.15, yk + 0.3), "第 15 列", "right", ofst=0.0)
        # ---- 耳机：10 µF 隔直 + 1 kΩ ----
        x7, x3 = x11 + 3.0, x11 + 5.8
        d += elm.Line().at((x11, yo)).to((x11 + 0.6, yo))
        d += elm.Capacitor(polar=True).endpoints((x11 + 0.6, yo), (x7, yo))
        lab(d, ((x11 + 0.6 + x7) / 2, yo + 0.85), "10 µF 电解\n+ 脚 j11，− 脚 j7", ha="center", fs_=9.5)
        d += elm.Resistor().endpoints((x7, yo), (x3, yo))
        lab(d, ((x7 + x3) / 2, yo - 0.65), "R 1 kΩ（i7–i3）", ha="center", fs_=9.5)
        sp = elm.Speaker().right().at((x3 + 0.8, yo + 0.25))
        d += elm.Line().at((x3, yo)).to((x3 + 0.8, yo + 0.25))
        d += sp
        s_ = sp.absanchors
        d += elm.Line().at(s_["in2"]).to((s_["in2"][0], yo - 1.8))
        d += elm.Ground().at((s_["in2"][0], yo - 1.8)).label("GND", "bottom")
        lab(d, (x3 + 2.3, yo + 0.7), "耳机\n3.5 mm 转接板", fs_=9.5)
        colnote(d, (x3 + 0.6, yo + 1.1), "信号脚（L、R 并联）→ j3", "top", ofst=0.0)
        colnote(d, (s_["in2"][0] + 0.2, yo - 1.3), "地脚 → 下边 GND 轨（第 1 列）", "right", ofst=0.0)
        # ---- B 组闲置 ----
        _follower_b(d, x7 + 0.6, 4.3, "绿短线 c15–c16（7 脚接 6 脚）", "黑线 a17")
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（黑表笔接 GND）；灰色小字 = 面包板孔位；小黑字 = LM358 引脚号；橙色 = 运放输出，绿色 = 同相端和 B 组的连线；天蓝色箭头 = 定时电流。",
            "所有 +5 V、GND 符号分别是同一条电源轨。LM358：1 脚 OUT f14、2 脚 IN− f15、3 脚 IN+ f16、4 脚 GND f17；8 脚 V+ e14、7 脚 e15、6 脚 e16、5 脚 e17（B 组）。",
            "同相端第 16 列上汇着 Ra（接 +5 V）、Rb（经 g16 → g22 接地）和 Rc（接输出）三只 10 kΩ；⑥ 慢速版：R 换 75 kΩ，C 换 10 µF 电解（+ 脚插 j15，− 脚接地）。",
        )
        for k, line in enumerate(notes):
            note(d, (-15.0, -8.6 - 0.6 * k), line)
    print("[图 24-p4-3] 5 V；g14–g11、R h11–h15、C j15–GND、Rc i11–i16、Ra h16–h20、g16–g22、Rb h22–h26；10 µF j11–j7、1 kΩ i7–i3、耳机 j3")
    save_schem(d, "24", "24_p4_3_schem_lab.png")

# ======================================================================================
# 04 自锁：图 04-p4-1（04_p4_1_breadboard.png）→ 图 04-p4-3
# 面包板连线依据 code/figs/04_figs.py：继电器 1 COM1 f12、2 NO1 f13、3 线圈+ f14、4 NC1 f15；8 线圈− e12、7 COM2 e13、6 NO2 e14、5 NC2 e15；
#   a12→0 V；g13–g14；1N4007 B-14(阳)–j14(阴)；HL1 h14–h19 + j19→0 V；a13→+12 V；M c14–c19 + a19→0 V；HL2 b15–b24 + a24→0 V；
#   B+3 → SB1 → i12；SB2 j12–j13；T+29–B+29，T-30–B-30；电源 + → T+1，− → T-3
# ======================================================================================
def node_04():
    SIG, POS = TEAL, "#D55E00"
    yT, yB = 5.0, -5.0
    with drawing(fontsize=11) as d:
        title(d, (0.0, 6.6), "自锁低压版：12 V 继电器 KA 代替接触器 KM，SB1 停止（常闭）、SB2 启动（常开），三只 12 V 小灯泡")
        # ---- 电源与两条轨 ----
        xb, xr = -11.0, 11.4
        d += elm.Battery().endpoints((xb, yB), (xb, yT)).reverse()
        lab(d, (xb - 0.5, 0.0), "12 V\n直流电源", ha="right", fs_=10)
        d += elm.Line().at((xb, yT)).to((xr, yT))
        d += elm.Line().at((xb, yB)).to((xr, yB))
        lab(d, (xr + 0.2, yT), "+12 V", fs_=10.5)
        lab(d, (xr + 0.2, yB), "0 V", fs_=10.5)
        colnote(d, (xb + 0.15, yT - 0.35), "+ → 上边 +12 V 轨（第 1 列）", "right", ofst=0.0)
        colnote(d, (xb + 0.15, yB + 0.35), "− → 上边 0 V 轨（第 3 列）", "right", ofst=0.0)
        lab(d, (xb - 1.4, yB - 0.9), "上下两条 +12 V 轨在第 29 列、两条 0 V 轨在第 30 列连通；横线 = 电源轨", fs_=9, color=GRAY)
        # ---- 控制回路：SB1 → COM1 → (SB2 ∥ KA-1) → NO1 → 线圈 ----
        xs, xk1, yc, yn, y14 = -6.0, -3.6, 2.4, 0.0, -1.0
        d += elm.Dot().at((xs, yT))
        d += PushNC().endpoints((xs, yT), (xs, 3.3))
        lab(d, (xs - 0.6, 4.15), "SB1 停止\n（常闭，红）", ha="right", fs_=10)
        colnote(d, (xs + 0.15, yT - 0.35), "B+3", "right", ofst=0.0)
        d += elm.Line().at((xs, 3.3)).to((xs, yc)).color(SIG).linewidth(1.8)
        d += elm.Line().at((xs, yc)).to((xk1, yc)).color(SIG).linewidth(1.8)
        colnote(d, (xs + 0.15, 2.85), "绿线 → i12", "right", ofst=0.0)
        d += elm.Dot().at((xs, yc))
        d += elm.Dot().at((xk1, yc))
        d += PushNO().endpoints((xs, yc), (xs, yn))
        lab(d, (xs - 0.6, 1.2), "SB2 启动\n（常开，绿）\nj12–j13", ha="right", fs_=10)
        ka1 = ContactNO().endpoints((xk1, yc), (xk1, yn))
        d += ka1
        lab(d, (xk1 + 0.5, 1.75), "KA 常开（自锁）", fs_=9.5)
        colnote(d, (xk1 + 0.15, yc + 0.3), "1 脚 COM1 f12", "right", ofst=0.0)
        colnote(d, (xk1 + 0.15, yn - 0.3), "2 脚 NO1 f13", "right", ofst=0.0)
        d += elm.Line().at((xs, yn)).to((xk1, yn))
        d += elm.Dot().at((xs, yn))
        d += elm.Dot().at((xk1, yn))
        ring(d, (xs, 2.85), "COM1（i12）", dx=-1.0, dy=0.0)
        ring(d, (xs, yn), "NO1（j13）", dx=-1.0, dy=0.0)
        d += elm.Line().at((xk1, yn)).to((xk1, y14)).color(SIG).linewidth(1.8)
        colnote(d, (xk1 - 0.15, (yn + y14) / 2 - 0.1), "绿短线 g13–g14", "left", ofst=0.0)
        # ---- 线圈正端第 14 列：1N4007、HL1、线圈 ----
        xd, xh, xc = -2.2, 0.9, 3.8
        d += elm.Line().at((xk1, y14)).to((xc, y14))
        d += elm.Dot().at((xd, y14))
        d += elm.Dot().at((xh, y14))
        d += elm.Diode().endpoints((xd, yB), (xd, y14))
        d += elm.Dot().at((xd, yB))
        lab(d, (xd - 0.45, -2.6), "1N4007\n阴极（白圈）j14\n阳极 → 下边 0 V 轨", ha="right", fs_=9.5)
        d += LampX().endpoints((xh, y14), (xh, yB))
        d += elm.Dot().at((xh, yB))
        lab(d, (xh + 0.65, -2.6), "HL1 运行灯\nh14–h19\n（黑线 j19）", fs_=9.5)
        d += Coil().endpoints((xc, y14), (xc, yB))
        d += elm.Dot().at((xc, yB))
        lab(d, (xc + 0.5, -1.95), "KA 线圈\n3 脚 线圈+ f14\n8 脚 线圈− e12\n（黑线 a12）", fs_=9.5)
        ring(d, (-0.65, y14), "线圈正端（j14）", dx=0.0, dy=-0.95, ha="center")
        d += elm.Arrow().at((-1.4, y14 + 0.35)).to((xc - 0.5, y14 + 0.35)).color(C["cur"]).linewidth(1.2)
        lab(d, ((xc - 1.4) / 2 - 0.2, y14 + 0.7), "线圈电流（吸合后经 SB1 → 自锁触点）", ha="center", fs_=8.5, color=C["cur"])
        # ---- 负载回路：+12 V → COM2 → NO2 → M、NC2 → HL2 ----
        xm, xn = 7.4, 10.2
        d += elm.Dot().at((xm, yT))
        d += elm.Line().at((xm, yT)).to((xm, yc)).color(POS).linewidth(1.8)
        colnote(d, (xm + 0.15, 3.9), "红线 a13", "right", ofst=0.0)
        colnote(d, (xm + 0.15, yc + 0.3), "7 脚 COM2 e13", "right", ofst=0.0)
        d += elm.Line().at((xm, yc)).to((xn, yc))
        d += elm.Dot().at((xm, yc))
        d += ContactNO().endpoints((xm, yc), (xm, yn))
        d += ContactNC().endpoints((xn, yc), (xn, yn))
        colnote(d, (xm + 0.15, yn - 0.3), "6 脚 NO2 e14", "right", ofst=0.0)
        colnote(d, (xn + 0.15, yn - 0.3), "5 脚 NC2 e15", "right", ofst=0.0)
        lab(d, (xm - 0.5, 1.75), "KA 常开", ha="right", fs_=9.5)
        lab(d, (xn + 0.5, 1.75), "KA 常闭", fs_=9.5)
        d += LampX().endpoints((xm, yn), (xm, yB))
        d += elm.Dot().at((xm, yB))
        lab(d, (xm + 0.5, -2.6), "M「电机」灯\nc14–c19\n（黑线 a19）", fs_=9.5)
        d += LampX().endpoints((xn, yn), (xn, yB))
        d += elm.Dot().at((xn, yB))
        lab(d, (xn + 0.5, -2.6), "HL2 停止灯\nb15–b24\n（黑线 a24）", fs_=9.5)
        # ---- 磁力联动：线圈 → 三组触点（点线，不是导线） ----
        ylk, xlk = 1.2, 6.45
        GR = "#737373"
        d += elm.Line().at((xc + 0.25, -3.3)).to((xlk, -3.3)).linestyle(":").color(GR)
        d += elm.Line().at((xlk, -3.3)).to((xlk, ylk)).linestyle(":").color(GR)
        d += elm.Line().at((xk1 + 0.25, ylk)).to((xn + 0.25, ylk)).linestyle(":").color(GR)
        lab(d, (1.2, ylk + 0.3), "磁力带动（不是导线）", ha="center", fs_=8.5, color=GRAY)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（黑表笔接 0 V）；灰色小字 = 面包板孔位和继电器引脚；绿色 = 按钮、触点之间的连线，红色 = 接 +12 V 的导线；",
            "天蓝色箭头 = 线圈电流；灰色点线表示线圈靠磁力同时带动三组触点（自锁常开、负载常开、负载常闭），线圈和触点之间没有导线。触点画的是线圈不通电时的状态。",
            "继电器引脚排列以手册为准（本图按面包板图的示意排列）：1 COM1 f12、2 NO1 f13、3 线圈+ f14、4 NC1 f15（不用）；8 线圈− e12、7 COM2 e13、6 NO2 e14、5 NC2 e15。",
        )
        for k, line in enumerate(notes):
            note(d, (-14.0, -6.9 - 0.6 * k), line)
    print("[图 04-p4-3] +12 V→SB1(B+3→i12)→COM1→SB2(j12–j13)∥KA NO1→g13–g14→线圈+(f14)→线圈−(e12)→a12→0 V；1N4007、HL1 并在线圈；a13→COM2→NO2→M、NC2→HL2")
    save_schem(d, "04", "04_p4_3_schem_lab.png")

# ======================================================================================
# 11 互锁：图 11-p4-1（11_p4_1_breadboard.png）→ 图 11-p4-3
# 面包板连线依据 code/figs/11_figs.py：KA1 第 6 列（f6 COM1、f7 NO1、f8 线圈+、f9 NC1；e6 线圈−、e7 COM2、e8 NO2、e9 NC2），KA2 第 30 列同理；
#   a6、a30→0 V；j6、j30→下边「+12 V 经 SB1」；SB2 i6–i7，SB3 i30–i31；VD1 B-8(阳)–j8(阴)，VD2 B-32–j32；HL1 h8–h3 + j3→0 V，HL2 g32–g37 + j37→0 V；
#   KA1 回路（蓝）g7→g12→d12→c12→c33（KA2 NC2）…b31（KA2 COM2）→b14→d14→f14→i14→i8；
#   KA2 回路（紫）g31→g26→d26→a26→a9（KA1 NC2）…b7（KA1 COM2）→b10→d10→f10→h10→h32；
#   电源 − → T-3，+ → SB1 → T+11；T+39–B+39，T-40–B-40
# ======================================================================================
def node_11():
    POS, MAG, GR = "#D55E00", PURPLE, "#737373"
    yT, yB, yc, yn, y14 = 5.6, -5.6, 3.4, 1.2, -2.4
    with drawing(fontsize=11) as d:
        title(d, (0.0, 7.4), "互锁低压版：KA1（正转）、KA2（反转）两只 12 V 继电器，每只线圈前串着对方的常闭触点")
        # ---- 电源、SB1、两条轨 ----
        xb, xr = -14.0, 12.6
        d += elm.Battery().endpoints((xb, yB), (xb, yT)).reverse()
        lab(d, (xb - 0.5, 0.0), "12 V\n直流电源", ha="right", fs_=10)
        d += elm.Line().at((xb, yT)).to((-12.6, yT)).color(POS).linewidth(1.8)
        d += PushNC().endpoints((-12.6, yT), (-11.2, yT))
        lab(d, (-11.9, yT + 1.0), "SB1 停止（常闭，红）", ha="center", fs_=10)
        d += elm.Line().at((-11.2, yT)).to((xr, yT))
        d += elm.Line().at((xb, yB)).to((xr, yB))
        lab(d, (xr + 0.2, yT), "+12 V\n经 SB1", fs_=10.5)
        lab(d, (xr + 0.2, yB), "0 V", fs_=10.5)
        colnote(d, (-11.0, yT - 0.35), "→ 上边外侧轨 T+11", "right", ofst=0.0)
        colnote(d, (xb + 0.15, yB + 0.35), "− → 上边 0 V 轨（第 3 列）", "right", ofst=0.0)
        lab(d, (xb - 1.4, yB - 0.9), "上下两条「+12 V 经 SB1」轨在第 39 列、两条 0 V 轨在第 40 列连通；横线 = 电源轨", fs_=9, color=GRAY)

        def branch(s, me, other, cols, wcol, wname, sb, hl, nc_mid):
            """s = −1 左（KA1），+1 右（KA2）。cols：(COM1, NO1, 线圈+, 线圈−, 灯另一端)。"""
            nonlocal d
            xk, xs, xh, xc, xdt = 7.6 * s, 10.2 * s, 4.9 * s, 2.0 * s, 0.25 * s
            out_ha, in_ha = ("right", "left") if s < 0 else ("left", "right")
            com1, no1, cp, cm, lampj, lampend = cols
            down = (lambda a, b: (a, b)) if s < 0 else (lambda a, b: (b, a))
            # COM1 ← +12 V 经 SB1（红线）
            d += elm.Dot().at((xk, yT))
            d += elm.Line().at((xk, yT)).to((xk, yc)).color(POS).linewidth(1.8)
            colnote(d, (xk - 0.15 * s, 4.5), f"红线 j{com1}", out_ha, ofst=0.0)
            # SB ∥ 自锁常开
            d += elm.Line().at((xs, yc)).to((xk, yc)); d += elm.Line().at((xs, yn)).to((xk, yn))
            for p in ((xs, yc), (xk, yc), (xs, yn), (xk, yn)):
                d += elm.Dot().at(p)
            d += PushNO().endpoints(*down((xs, yc), (xs, yn)))
            lab(d, (xs + (0.6 if s < 0 else 1.5) * s, 2.3), sb, ha=out_ha, fs_=10)
            d += ContactNO().endpoints(*down((xk, yc), (xk, yn)))
            colnote(d, (xk + 0.15 * (-s), yc + 0.3), f"1 脚 COM1 f{com1}", in_ha if s > 0 else "right", ofst=0.0)
            colnote(d, (xk + 0.15 * (-s), yn - 0.3), f"2 脚 NO1 f{no1}", in_ha if s > 0 else "right", ofst=0.0)
            # 对方的常闭（互锁）
            nt, nb = nc_mid + 1.0, nc_mid - 1.0
            d += elm.Line().at((xk, yn)).to((xk, nt)).color(wcol).linewidth(1.8)
            d += ContactNC().endpoints(*down((xk, nt), (xk, nb)))
            d += elm.Line().at((xk, nb)).to((xk, y14)).color(wcol).linewidth(1.8)
            return xk, xs, xh, xc, xdt, out_ha, in_ha, nt, nb

        # 左：KA1
        L = branch(-1, "KA1", "KA2", (6, 7, 8, 6, 3, 3), BLUE, "蓝线", "SB2 正转\n（常开）\ni6–i7", None, -0.4)
        R = branch(+1, "KA2", "KA1", (30, 31, 32, 30, 37, 37), MAG, "紫线", "SB3 反转\n（常开）\ni30–i31", None, -0.9)
        # 互锁触点的孔位
        xk, nt, nb = L[0], L[7], L[8]
        ring(d, (xk, nt), "c33", dx=-1.0, dy=0.0)
        ring(d, (xk, nb), "b31", dx=-1.0, dy=0.0)
        lab(d, (xk - 2.6, nt - 0.0), "KA2 5 脚 NC2", ha="right", fs_=9, color=GRAY)
        lab(d, (xk - 2.6, nb), "KA2 7 脚 COM2", ha="right", fs_=9, color=GRAY)
        lab(d, (xk - 1.0, (nt + nb) / 2), "KA2 常闭\n（互锁）", ha="right", fs_=9.5)
        xk2, nt2, nb2 = R[0], R[7], R[8]
        ring(d, (xk2, nt2), "a9", dx=1.0, dy=0.0)
        ring(d, (xk2, nb2), "b7", dx=1.0, dy=0.0)
        lab(d, (xk2 + 2.3, nt2), "KA1 5 脚 NC2", fs_=9, color=GRAY)
        lab(d, (xk2 + 2.3, nb2), "KA1 7 脚 COM2", fs_=9, color=GRAY)
        lab(d, (xk2 + 1.0, (nt2 + nb2) / 2), "KA1 常闭\n（互锁）", fs_=9.5)

        # ---- 线圈正端：二极管、灯、线圈 ----
        def coil_group(s, name, cp, cm, vd, hl):
            nonlocal d
            xk, xh, xc = 7.6 * s, 4.9 * s, 2.0 * s
            out_ha, in_ha = ("right", "left") if s < 0 else ("left", "right")
            d += elm.Line().at((xk, y14)).to((xc, y14))
            for x in (xk, xh):
                d += elm.Dot().at((x, y14))
            d += elm.Diode().endpoints((xk, yB), (xk, y14))
            d += LampX().endpoints((xh, y14), (xh, yB))
            d += Coil().endpoints((xc, y14), (xc, yB))
            for x in (xk, xh, xc):
                d += elm.Dot().at((x, yB))
            lab(d, (xk + 0.45 * s, -4.0), vd, ha=out_ha, fs_=9.5)
            lab(d, (xh + 0.6 * (-s), -4.0), hl, ha=in_ha, fs_=9.5)
            lab(d, (xc + 0.45 * (-s), -3.0), f"{name} 线圈\n3 脚 f{cp}\n8 脚 e{cm}\n黑线 a{cm}", ha=in_ha, fs_=9.5)
            ring(d, ((xh + xc) / 2, y14), f"线圈正端 j{cp}", dx=0.0, dy=0.75, ha="center")
        coil_group(-1, "KA1", 8, 6, "VD1 1N4007\n阴极（白圈）j8\n阳极 → 下边 0 V 轨", "HL1 正转灯\nh8–h3\n（黑线 j3）")
        coil_group(+1, "KA2", 32, 30, "VD2 1N4007\n阴极（白圈）j32\n阳极 → 下边 0 V 轨", "HL2 反转灯\ng32–g37\n（黑线 j37）")

        # ---- 磁力联动（点线，不是导线）----
        yb1 = -4.6
        # KA1：线圈 → 自己的自锁常开（左上）和右边支路里的 KA1 常闭
        d += elm.Line().at((-2.0 + 0.25, yb1)).to((-0.25, yb1)).linestyle(":").color(GR)
        d += elm.Line().at((-0.25, yb1)).to((-0.25, 2.3)).linestyle(":").color(GR)
        d += elm.Line().at((-0.25, 2.3)).to((-7.6 + 0.25, 2.3)).linestyle(":").color(GR)
        d += elm.Line().at((-0.25, -0.9)).to((7.6 - 0.25, -0.9)).linestyle(":").color(GR)
        # KA2：线圈 → 自己的自锁常开（右上）和左边支路里的 KA2 常闭
        d += elm.Line().at((2.0 - 0.25, yb1)).to((0.25, yb1)).linestyle(":").color(GR)
        d += elm.Line().at((0.25, yb1)).to((0.25, 2.3)).linestyle(":").color(GR)
        d += elm.Line().at((0.25, 2.3)).to((7.6 - 0.25, 2.3)).linestyle(":").color(GR)
        d += elm.Line().at((0.25, -0.4)).to((-7.6 + 0.25, -0.4)).linestyle(":").color(GR)
        lab(d, (-3.9, 2.6), "KA1 磁力带动（不是导线）", ha="center", fs_=8.5, color=GRAY)
        lab(d, (3.9, 2.6), "KA2 磁力带动（不是导线）", ha="center", fs_=8.5, color=GRAY)
        lab(d, (-3.9, -0.1), "KA2 磁力带动", ha="center", fs_=8.5, color=GRAY)
        lab(d, (3.9, -0.6), "KA1 磁力带动", ha="center", fs_=8.5, color=GRAY)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（与测量表同名，黑表笔接 0 V 轨）；灰色小字 = 面包板孔位和继电器引脚；红色 = 接「+12 V 经 SB1」的导线，",
            "蓝色 = KA1 线圈回路里经过 KA2 常闭的长跳线，紫色 = KA2 线圈回路里经过 KA1 常闭的长跳线；灰色点线 = 线圈靠磁力带动自己的触点，不是导线。触点都画成线圈不通电时的状态。",
            "蓝线：g7→g12、f12→d12、c12→c33，b31→b14、d14→f14、i14→i8；紫线：g31→g26、f26→d26、a26→a9，b7→b10、d10→f10、h10→h32（长跳线从别的孔上方跨过）。",
            "继电器引脚按面包板图的示意排列，以手册为准：1 COM1、2 NO1、3 线圈+、4 NC1（不用）在 f 排；8 线圈−、7 COM2、6 NO2（不用）、5 NC2 在 e 排。KA1 从第 6 列起，KA2 从第 30 列起。",
        )
        for k, line in enumerate(notes):
            note(d, (-15.5, -7.3 - 0.6 * k), line)
    print("[图 11-p4-3] +12 V 经 SB1 → COM1 → (SB2∥KA1 NO1) → KA2 NC2(c33…b31) → KA1 线圈+(j8)；KA2 同理经 KA1 NC2(a9…b7) → j32")
    save_schem(d, "11", "11_p4_3_schem_lab.png")

# ======================================================================================
# 15 星三角：图 15-p4-1（15_p4_1_breadboard.png）→ 图 15-p4-3
# 面包板连线依据 code/figs/15_figs.py：KM 第 8 列、KM△ 第 18 列、KMY 第 32 列（下排 COM1、NO1、线圈+、NC1，上排 线圈−、COM2、NO2、NC2）；
#   a8、a18、a32→0 V；j8→「+12 V 经 SB1」；SB2 i8–i9；g9–g10；公共点 C：i10→i13、f13→d13、a13→上边外侧轨；
#   KM△ COM1：h18→h15、f15→d15、a15→C；COM2：a19→C；X = KM△ NC2（第 21 列上）= KT V+ a21 = KT COM a22（b21–b22）；KT V−→0 V；
#   Y：KT NO a28→d28…f28，g19→g28，i28→i32（KMY COM1）；Z：h35（KMY NC1）→h20（KM△ 线圈+）；W：KT NC a36→d36…f36→i36→i34（KMY 线圈+）；
#   VD1 j10、VD2 j20、VD3 j34；HL1 h10–h5、HL3 i20–i25、HL2 g34–g39；电源 −→B-12，+→SB1→B+17；T-40–B-40
# ======================================================================================
def node_15():
    RED, MAG, ORG, GR = "#D55E00", PURPLE, C["vout"], "#737373"
    yT, yB, yc, yC, yX, yY, yZ = 7.0, -7.5, 5.4, 3.2, 1.0, -1.4, -3.6
    fsl = 9

    def dline(d, a, b):
        d += elm.Line().at(a).to(b).linestyle(":").color(GR)

    def wire(d, a, b, col, lw=1.8):
        d += elm.Line().at(a).to(b).color(col).linewidth(lw)

    def dots(d, *ps):
        for p in ps:
            d += elm.Dot().at(p)

    with drawing(fontsize=11) as d:
        title(d, (1.0, 8.8), "星三角低压版：KM、KM△、KMY 三只 12 V 继电器 + KT 通电延时模块，灯泡并在线圈上当指示")
        xb, xr = -17.0, 19.6
        d += elm.Battery().endpoints((xb, yB), (xb, yT)).reverse()
        lab(d, (xb - 0.5, 0.0), "12 V\n直流电源", ha="right", fs_=10)
        wire(d, (xb, yT), (-15.6, yT), RED)
        d += PushNC().endpoints((-15.6, yT), (-14.2, yT))
        lab(d, (-14.9, yT + 1.0), "SB1 停止（常闭）", ha="center", fs_=10)
        d += elm.Line().at((-14.2, yT)).to((xr, yT))
        d += elm.Line().at((xb, yB)).to((xr, yB))
        lab(d, (xr + 0.2, yT), "+12 V\n经 SB1", fs_=10.5)
        lab(d, (xr + 0.2, yB), "0 V", fs_=10.5)
        colnote(d, (-14.0, yT - 0.35), "→ 下边外侧轨 B+17", "right", ofst=0.0)
        colnote(d, (xb + 0.15, yB + 0.35), "− → 下边 0 V 轨（第 12 列）", "right", ofst=0.0)

        # ---- KM：COM1 ← 红线 j8；SB2 ∥ NO1；输出 = 公共点 C ----
        xk, xs = -11.5, -9.0
        dots(d, (xk, yT), (xk, yc), (xs, yc), (xs, yC), (xk, yC))
        wire(d, (xk, yT), (xk, yc), RED)
        colnote(d, (xk + 0.15, 6.2), "红线 j8", "right", ofst=0.0)
        d += elm.Line().at((xk, yc)).to((xs, yc))
        d += ContactNO().endpoints((xk, yC), (xk, yc))          # 自下而上：动触片朝左，点线从左边连到线圈
        d += PushNO().endpoints((xs, yc), (xs, yC))
        lab(d, (xs + 1.5, 4.3), "SB2 启动\n（常开）\ni8–i9", fs_=fsl)
        colnote(d, (xk + 0.15, yc - 0.3), "1 脚 COM1 f8", "right", ofst=0.0)
        colnote(d, (xk + 0.15, yC + 0.3), "2 脚 NO1 f9", "right", ofst=0.0)
        xC1 = 10.5
        wire(d, (xk, yC), (xC1, yC), MAG)
        ring(d, (0.0, yC), "公共点 C（上边外侧轨）", dx=0.0, dy=0.9, ha="center")
        # KM 线圈、VD1、HL1
        xd1, xh1 = -9.0, -6.5
        dots(d, (xd1, yC), (xh1, yC))
        d += Coil().endpoints((xk, yC), (xk, yB))
        d += elm.Diode().endpoints((xd1, yB), (xd1, yC))
        d += LampX().endpoints((xh1, yC), (xh1, yB))
        dots(d, (xk, yB), (xd1, yB), (xh1, yB))
        lab(d, (xk - 1.3, -2.2), "KM 线圈\n3 脚 f10\n8 脚 e8\n黑线 a8", ha="right", fs_=fsl)
        lab(d, (xd1 + 0.4, -5.6), "VD1\n白圈 j10", fs_=fsl)
        lab(d, (xh1 + 0.6, -5.4), "HL1 主灯\nh10–h5\n黑线 j5", fs_=fsl)
        dline(d, (xk - 0.25, -2.4), (xk - 0.9, -2.4)); dline(d, (xk - 0.9, -2.4), (xk - 0.9, 4.3)); dline(d, (xk - 0.9, 4.3), (xk - 0.2, 4.3))
        lab(d, (xk - 1.0, 4.75), "KM 磁力带动", ha="right", fs_=8.5, color=GRAY)

        # ---- KM△ 常闭 NC2：C → X ----
        xn2 = -4.0
        d += elm.Dot().at((xn2, yC))
        d += ContactNC().endpoints((xn2, yC), (xn2, yX))
        colnote(d, (xn2 + 0.15, yC - 0.3), "7 脚 COM2 e19（紫线 a19）", "right", ofst=0.0)
        colnote(d, (xn2 + 0.6, yX + 0.35), "5 脚 NC2 e21 = X", "right", ofst=0.0)
        lab(d, (xn2 - 0.3, 2.1), "KM△ 常闭", ha="right", fs_=fsl)
        # X 节点（橙）：KT 电源 V+ 与 KT 公共端 COM
        xkt, xtn, xto = -2.0, 0.5, 8.0
        wire(d, (xn2, yX), (xto, yX), ORG)
        dots(d, (xkt, yX), (xtn, yX), (xto, yX))
        ring(d, (-3.0, yX), "a21（X）", dx=0.0, dy=-0.9, ha="center")
        d += Coil().endpoints((xkt, yX), (xkt, yB))
        d += elm.Dot().at((xkt, yB))
        lab(d, (xkt - 0.45, -4.2), "KT 模块\nV+ a21\nV− → 0 V\n（第 25 列）", ha="right", fs_=fsl)
        colnote(d, (2.6, yX + 0.3), "KT COM a22（橙短线 b21–b22）", "right", ofst=0.0)
        d += TimerNC().endpoints((xtn, yY), (xtn, yX))
        d += TimerNO().endpoints((xto, yY), (xto, yX))
        colnote(d, (xtn + 0.15, yY - 0.3), "KT NC a36（W）", "right", ofst=0.0)
        colnote(d, (xto + 0.15, yY - 0.3), "KT NO a28（Y）", "right", ofst=0.0)
        # KMY 线圈组（W，橙）
        xd3, xh2, xky = 0.5, 3.0, 5.5
        wire(d, (xtn, yY), (xky, yY), ORG)
        d += elm.Dot().at((xh2, yY))
        d += elm.Diode().endpoints((xd3, yB), (xd3, yY))
        d += LampX().endpoints((xh2, yY), (xh2, yB))
        d += Coil().endpoints((xky, yY), (xky, yB))
        dots(d, (xd3, yB), (xh2, yB), (xky, yB))
        lab(d, (xd3 + 0.4, -5.6), "VD3\n白圈 j34", fs_=fsl)
        lab(d, (xh2 + 0.55, -5.4), "HL2\n星形灯\ng34–g39\n黑线 j39", fs_=fsl)
        lab(d, (xky + 0.45, -3.4), "KMY 线圈\n3 脚 f34\n8 脚 e32\n黑线 a32", fs_=fsl)
        ring(d, (4.25, yY), "j34", dx=0.0, dy=-0.9, ha="center")
        # KT 延时联动
        dline(d, (xkt + 0.25, -3.2), (-1.0, -3.2)); dline(d, (-1.0, -3.2), (-1.0, -0.2)); dline(d, (-1.0, -0.2), (xto - 0.6, -0.2))
        lab(d, (4.3, 0.2), "KT 延时带动（到时：NC 断开、NO 闭合）", ha="center", fs_=8.5, color=GRAY)

        # ---- Y：KT NO ∥ KM△ NO1 → KMY 常闭 NC1 → Z（蓝）----
        xy = 10.5
        d += elm.Dot().at((xy, yC))
        d += ContactNO().endpoints((xy, yC), (xy, yY))
        colnote(d, (xy + 0.15, yC + 0.3), "1 脚 COM1 f18（紫线 h18→h15、f15→d15、a15）", "right", ofst=0.0)
        colnote(d, (xy + 0.15, yY + 0.45), "2 脚 NO1 f19（蓝线 g19→g28）", "right", ofst=0.0)
        lab(d, (xy + 0.7, 1.5), "KM△ 常开（自锁）", fs_=fsl)
        wire(d, (xto, yY), (xy, yY), BLUE)
        d += elm.Dot().at((xy, yY))
        ring(d, (9.25, yY), "i32（Y）", dx=0.0, dy=0.7, ha="center")
        d += ContactNC().endpoints((xy, yZ), (xy, yY))          # 自下而上：动触片朝左
        lab(d, (xy + 0.3, -2.2), "KMY 常闭（互锁）\n1 脚 COM1 f32", fs_=8.5)
        colnote(d, (xy + 0.15, yZ - 0.3), "4 脚 NC1 f35（Z）", "right", ofst=0.0)
        # Z：KM△ 线圈组
        xd2, xh3, xkd = 10.5, 13.0, 15.5
        wire(d, (xy, yZ), (xkd, yZ), BLUE)
        d += elm.Dot().at((xh3, yZ))
        d += elm.Diode().endpoints((xd2, yB), (xd2, yZ))
        d += LampX().endpoints((xh3, yZ), (xh3, yB))
        d += Coil().endpoints((xkd, yZ), (xkd, yB))
        dots(d, (xd2, yB), (xh3, yB), (xkd, yB))
        lab(d, (xd2 + 0.4, -6.1), "VD2\n白圈 j20", fs_=fsl)
        lab(d, (xh3 + 0.55, -5.9), "HL3\n三角形灯\ni20–i25\n黑线 j25", fs_=fsl)
        lab(d, (xkd + 0.45, -4.7), "KM△ 线圈\n3 脚 f20\n8 脚 e18\n黑线 a18", fs_=fsl)
        ring(d, (14.25, yZ), "j20 = h35（Z）", dx=0.0, dy=0.8, ha="center")
        # KM△ 磁力联动：自锁常开 + 常闭 NC2；KMY 磁力联动：KMY 常闭
        xv = 18.6
        dline(d, (xkd + 0.25, -6.6), (xv, -6.6)); dline(d, (xv, -6.6), (xv, 2.1))
        dline(d, (xv, 0.4), (xy + 0.3, 0.4))
        dline(d, (xv, 2.1), (xn2 + 0.3, 2.1))
        lab(d, (16.0, 0.75), "KM△ 磁力带动", ha="center", fs_=8.5, color=GRAY)
        lab(d, (4.3, 2.45), "KM△ 磁力带动（不是导线）", ha="center", fs_=8.5, color=GRAY)
        dline(d, (xky + 0.25, -6.0), (8.8, -6.0)); dline(d, (8.8, -6.0), (8.8, -2.5)); dline(d, (8.8, -2.5), (xy - 0.3, -2.5))
        lab(d, (8.7, -6.4), "KMY 磁力带动", ha="center", fs_=8.5, color=GRAY)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 测量点（黑表笔接 0 V 轨）；灰色小字 = 面包板孔位和继电器、模块引脚；灰色点线 = 线圈或延时模块带动自己的触点，不是导线；触点都画成不通电时的状态。",
            "导线颜色与面包板图一致：红 = 「+12 V 经 SB1」；紫 = 公共点 C（g9–g10，i10→i13、f13→d13、a13 → 上边外侧轨）；橙 = KT 和 KMY 支路（X：b21–b22；W：a36、d36→f36、i36→i34）；",
            "蓝 = KM△ 支路（Y：a28、d28→f28、g19→g28、i28→i32；Z：h35→h20）。1N4007 阴极（白圈）朝线圈正端，阳极接 0 V；上下两条 0 V 轨在第 40 列连通；上边外侧轨不接电源，就是公共点 C。",
            "继电器、模块引脚按面包板图的示意排列，以手册为准：下排 1 COM1、2 NO1、3 线圈+、4 NC1，上排 8 线圈−、7 COM2、6 NO2、5 NC2；KM 从第 8 列、KM△ 从第 18 列、KMY 从第 32 列起。",
        )
        for k, line in enumerate(notes):
            note(d, (-18.5, -8.9 - 0.6 * k), line)
    print("[图 15-p4-3] SB1→COM1(j8)→SB2∥KM NO1→C；C→KM△ NC2→X→KT(V+、COM)；KT NC→W→KMY；KT NO∥KM△ NO1→Y→KMY NC1→Z→KM△")
    save_schem(d, "15", "15_p4_3_schem_lab.png")

# ======================================================================================
# 27 双控开关：图 27-p4-1（27_p4_1_breadboard.png）→ 图 27-p4-3
# 面包板连线依据 code/figs/27_figs.py：S1 f5(1)、f6(COM)、f7(2)；S2 f15(1)、f16(COM)、f17(2)；
#   跨线 A g5→g17（蓝）；跨线 B h7→h15（绿）；j6→B+（+9 V，红）；R1 i16–i21；LED h21(+)–h24；j24→B−（黑）
# ======================================================================================
def node_27():
    RED, GRN, MAG = "#D55E00", TEAL, PURPLE

    with drawing(fontsize=11) as d:
        title(d, (7.5, 4.6), "两地控制（低压版）：9 V 电池、两只三脚拨动开关、1 kΩ + 红 LED")
        yT, yB = 1.0, -3.4
        # 电池与 +9 V 线
        d += elm.Battery().endpoints((0, yB), (0, yT)).reverse()
        lab(d, (-0.5, -1.2), "9 V\n电池", ha="right", fs_=10)
        d += elm.Line().at((0, yT)).to((3.0, yT)).color(RED).linewidth(1.8)
        lab(d, (1.5, yT + 0.35), "+9 V", ha="center", fs_=10, color=RED)
        colnote(d, (0.2, yT - 0.35), "红线 j6 → 下边 +9 V 轨", "right", ofst=0.0)
        # S1：COM 在左，1（上）、2（下）在右
        com1, t11, t12 = (3.0, yT), (4.6, 2.0), (4.6, 0.0)
        d += elm.Dot().at(com1)
        d += elm.Dot(open=True).at(t11)
        d += elm.Dot(open=True).at(t12)
        d += elm.Line().at(com1).to((4.5, 1.9)).linewidth(2.0)          # 画的是 S1 拨到 1
        lab(d, (3.6, 2.5), "S1", ha="center", fs_=11)
        colnote(d, (3.0, yT - 0.35), "COM f6", "right", ofst=0.0)
        colnote(d, (4.6, 2.4), "1 · f5", "right", ofst=0.0)
        colnote(d, (4.6, -0.4), "2 · f7", "right", ofst=0.0)
        # S2：COM 在右，2（上）、1（下）在左，这样两根跨线都不交叉
        com2, t22, t21 = (10.6, yT), (9.0, 2.0), (9.0, 0.0)
        d += elm.Dot().at(com2)
        d += elm.Dot(open=True).at(t22)
        d += elm.Dot(open=True).at(t21)
        d += elm.Line().at(com2).to((9.1, 1.9)).linewidth(2.0)          # 画的是 S2 拨到 2
        lab(d, (10.0, 2.5), "S2", ha="center", fs_=11)
        colnote(d, (10.6, yT - 0.35), "COM f16", "left", ofst=0.0)
        colnote(d, (9.0, 2.4), "f17 · 2", "left", ofst=0.0)
        colnote(d, (9.0, -0.4), "f15 · 1", "left", ofst=0.0)
        # 跨线 A（蓝）、跨线 B（绿）
        d += elm.Line().at(t11).to(t22).color(BLUE).linewidth(1.8)
        d += elm.Line().at(t12).to(t21).color(GRN).linewidth(1.8)
        lab(d, (6.8, 1.6), "跨线 A：蓝线 g5 → g17", ha="center", fs_=9.5, color=BLUE)
        lab(d, (6.8, 0.4), "跨线 B：绿线 h7 → h15", ha="center", fs_=9.5, color=GRN)
        # S2 COM → R1 → M → LED → 0 V
        d += elm.Line().at(com2).to((11.6, yT))
        d += elm.Resistor().at((11.6, yT)).to((14.4, yT)).label("R1 1 kΩ", loc="top")
        colnote(d, (11.7, yT - 0.35), "i16", "right", ofst=0.0)
        colnote(d, (14.3, yT - 0.35), "i21", "left", ofst=0.0)
        M = (15.4, yT)
        d += elm.Line().at((14.4, yT)).to(M)
        d += elm.Dot().at(M)
        ring(d, M, "M（第 21 列）", dx=0.0, dy=0.9, ha="center")
        d += elm.LED().endpoints(M, (M[0], yB))
        lab(d, (M[0] + 0.55, -0.6), "LED（红）\n长脚 + h21\n短脚 − h24", fs_=9.5)
        colnote(d, (M[0] + 0.15, yB + 0.35), "黑线 j24 → 0 V 轨", "right", ofst=0.0)
        d += elm.Line().at((M[0], yB)).to((0, yB))
        lab(d, (7.5, yB - 0.4), "0 V（电池负极，下边 0 V 轨）", ha="center", fs_=10)
        # 电流方向（S1 在 1、S2 在 2：经跨线 A，LED 亮）
        d += elm.Arrow().at((5.8, 2.8)).to((7.8, 2.8)).color(C["cur"]).linewidth(1.2)
        d += elm.Arrow().at((11.9, 2.0)).to((13.9, 2.0)).color(C["cur"]).linewidth(1.2)
        lab(d, (12.9, 2.3), "约 7 mA", ha="center", fs_=9, color=C["cur"])
        lab(d, (6.8, 3.15), "电流", ha="center", fs_=9, color=C["cur"])
        notes = (
            "读图：画的是 S1 拨到 1、S2 拨到 2 的一种组合：电流经跨线 A 走通，LED 亮。任拨一只，S2 的 COM 就接到没电的那根跨线上，LED 灭；再拨另一只又亮——这就是异或。",
            "S2 的 2 画在上面、1 画在下面，是为了让两根跨线都不交叉；面包板上 S2 的三只脚仍是 f15（1）、f16（COM）、f17（2）。拨动开关哪只脚是 COM 以蜂鸣挡实测为准。",
            "导线颜色与面包板图一致：红 = +9 V，黑 = 0 V，蓝 = 跨线 A，绿 = 跨线 B；紫色圆圈 = 测量点 M（黑表笔接 0 V 轨）；天蓝色箭头 = 电流方向；灰色小字 = 面包板孔位。",
        )
        for k, line in enumerate(notes):
            note(d, (-1.5, -4.6 - 0.6 * k), line)
    print("[图 27-p4-3] +9 V→S1 COM(f6)；S1 1(f5)─A─S2 2(f17)，S1 2(f7)─B─S2 1(f15)；S2 COM(f16)→R1→M(第21列)→LED→0 V")
    save_schem(d, "27", "27_p4_3_schem_lab.png")
    # ---------------- 图 27-p4-4：三地控制扩展（27_p4_2_three_way.png）----------------
    # 依据 27_figs.py：S1 f5(1)、f6(COM)、f7(2)；跨线 A g5→g14（入1），B h7→h16（入2）；中途开关引线 j14 入1、j16 入2、j20 出1、j22 出2（紫）；
    #   跨线 C g20→g31（出1→S3 的 2），D h22→h29（出2→S3 的 1）；S3 f29(1)、f30(COM)、f31(2)；R1 i30–i34；LED h34(+)–h37；j37→0 V；j6→+9 V
    with drawing(fontsize=11) as d:
        title(d, (10.0, 4.8), "三地控制（低压版）：S1、S3 两只三脚拨动开关，中间加中途开关 S2")
        yT, yB = 1.0, -3.6
        d += elm.Battery().endpoints((0, yB), (0, yT)).reverse()
        lab(d, (-0.5, -1.3), "9 V\n电池", ha="right", fs_=10)
        d += elm.Line().at((0, yT)).to((2.6, yT)).color(RED).linewidth(1.8)
        lab(d, (1.3, yT + 0.35), "+9 V", ha="center", fs_=10, color=RED)
        colnote(d, (0.2, yT - 0.35), "红线 j6 → +9 V 轨", "right", ofst=0.0)
        # S1
        com1, t11, t12 = (2.6, yT), (4.2, 2.0), (4.2, 0.0)
        d += elm.Dot().at(com1); d += elm.Dot(open=True).at(t11); d += elm.Dot(open=True).at(t12)
        d += elm.Line().at(com1).to((4.1, 1.9)).linewidth(2.0)
        lab(d, (3.2, 2.5), "S1", ha="center")
        colnote(d, (2.6, yT - 0.35), "COM f6", "right", ofst=0.0)
        colnote(d, (4.2, 2.4), "1 · f5", "right", ofst=0.0)
        colnote(d, (4.2, -0.4), "2 · f7", "right", ofst=0.0)
        # 中途开关 S2：入1（上）、入2（下）在左，出1（上）、出2（下）在右
        i1, i2, o1, o2 = (8.6, 2.0), (8.6, 0.0), (11.4, 2.0), (11.4, 0.0)
        d += elm.Line().at(t11).to(i1).color(BLUE).linewidth(1.8)
        d += elm.Line().at(t12).to(i2).color(GRN).linewidth(1.8)
        lab(d, (6.4, 1.6), "跨线 A：蓝线 g5 → g14", ha="center", fs_=9.5, color=BLUE)
        lab(d, (6.4, 0.4), "跨线 B：绿线 h7 → h16", ha="center", fs_=9.5, color=GRN)
        d += elm.Line().at((8.1, -0.9)).to((11.9, -0.9)).linestyle("--").color(GRAY)
        d += elm.Line().at((11.9, -0.9)).to((11.9, 2.9)).linestyle("--").color(GRAY)
        d += elm.Line().at((11.9, 2.9)).to((8.1, 2.9)).linestyle("--").color(GRAY)
        d += elm.Line().at((8.1, 2.9)).to((8.1, -0.9)).linestyle("--").color(GRAY)
        lab(d, (10.0, 3.25), "S2 中途开关（六脚双刀双掷改）", ha="center", fs_=10)
        for p in (i1, i2, o1, o2):
            d += elm.Dot(open=True).at(p).color(MAG)
        d += elm.Line().at(i1).to(o1).linewidth(2.0)                        # 画的是「直通」位置
        d += elm.Line().at(i2).to(o2).linewidth(2.0)
        d += elm.Line().at((8.75, 1.85)).to((11.25, 0.15)).linestyle(":").color(GRAY)
        d += elm.Line().at((8.75, 0.15)).to((11.25, 1.85)).linestyle(":").color(GRAY)
        lab(d, (10.0, -1.3), "实线 = 直通；点线 = 拨到另一边时交叉", ha="center", fs_=8.5, color=GRAY)
        colnote(d, (8.7, 2.3), "入1 j14", "right", ofst=0.0)
        colnote(d, (8.7, -0.3), "入2 j16", "right", ofst=0.0)
        colnote(d, (11.3, 2.3), "出1 j20", "left", ofst=0.0)
        colnote(d, (11.3, -0.3), "出2 j22", "left", ofst=0.0)
        lab(d, (10.0, -1.9), "四根紫色引线 → j14、j16、j20、j22", ha="center", fs_=9, color=MAG)
        # S3：2（上）、1（下）在左，COM 在右
        com3, t32, t31 = (17.4, yT), (15.8, 2.0), (15.8, 0.0)
        d += elm.Line().at(o1).to(t32).color(BLUE).linewidth(1.8)
        d += elm.Line().at(o2).to(t31).color(GRN).linewidth(1.8)
        lab(d, (13.6, 1.6), "跨线 C：蓝线 g20 → g31", ha="center", fs_=9.5, color=BLUE)
        lab(d, (13.6, 0.4), "跨线 D：绿线 h22 → h29", ha="center", fs_=9.5, color=GRN)
        d += elm.Dot().at(com3); d += elm.Dot(open=True).at(t32); d += elm.Dot(open=True).at(t31)
        d += elm.Line().at(com3).to((15.9, 1.9)).linewidth(2.0)
        lab(d, (16.8, 2.5), "S3", ha="center")
        colnote(d, (15.8, 2.4), "f31 · 2", "left", ofst=0.0)
        colnote(d, (15.8, -0.4), "f29 · 1", "left", ofst=0.0)
        colnote(d, (17.4, yT - 0.35), "COM f30", "left", ofst=0.0)
        d += elm.Line().at(com3).to((18.2, yT))
        d += elm.Resistor().at((18.2, yT)).to((20.8, yT)).label("R1 1 kΩ", loc="top")
        colnote(d, (18.3, yT - 0.35), "i30", "right", ofst=0.0)
        colnote(d, (20.7, yT - 0.35), "i34", "left", ofst=0.0)
        xl = 21.8
        d += elm.Line().at((20.8, yT)).to((xl, yT))
        d += elm.LED().endpoints((xl, yT), (xl, yB))
        lab(d, (xl + 0.55, -0.7), "LED（红）\n长脚 + h34\n短脚 − h37", fs_=9.5)
        colnote(d, (xl + 0.15, yB + 0.35), "黑线 j37 → 0 V 轨", "right", ofst=0.0)
        d += elm.Line().at((xl, yB)).to((0, yB))
        lab(d, (11.0, yB - 0.4), "0 V（电池负极，下边 0 V 轨）", ha="center", fs_=10)
        d += elm.Arrow().at((5.4, 2.8)).to((7.4, 2.8)).color(C["cur"]).linewidth(1.2)
        lab(d, (6.4, 3.15), "电流", ha="center", fs_=9, color=C["cur"])
        d += elm.Arrow().at((18.5, 2.0)).to((20.5, 2.0)).color(C["cur"]).linewidth(1.2)
        lab(d, (19.5, 2.3), "约 7 mA", ha="center", fs_=9, color=C["cur"])
        notes = (
            "读图：画的是 S1 拨到 1、S2 直通、S3 拨到 2：电流走 A → 入1 → 出1 → C，LED 亮。中途开关一拨，入1 改接出2、入2 改接出1，S3 的 COM 就换到没电的那根跨线上，LED 灭。",
            "S3 的 2 画在上面、1 画在下面，是为了让跨线不交叉；面包板上 S3 仍是 f29（1）、f30（COM）、f31（2）。中途开关内部的对角交叉线在开关上，不在面包板上。",
            "导线颜色与面包板图一致：红 = +9 V，黑 = 0 V，紫 = 中途开关引线，蓝 = 跨线 A、C，绿 = 跨线 B、D；天蓝色箭头 = 电流方向；灰色小字 = 面包板孔位。",
        )
        for k, line in enumerate(notes):
            note(d, (-1.5, -4.8 - 0.6 * k), line)
    print("[图 27-p4-4] +9 V→S1 COM；A、B→中途开关入1、入2；出1、出2→C、D→S3 的 2、1；S3 COM→R1→LED→0 V")
    save_schem(d, "27", "27_p4_4_schem_lab.png")

# ======================================================================================
# 06 MOS 管开关：图 06-p4-1（06_p4_1_breadboard.png）→ 图 06-p4-3
# 面包板连线依据 code/figs/06_figs.py fig_p4_1：IRLZ44N G a15、D a16、S a17；R_G b11–b15；R_GS e15–f15，j15→GND；e17→GND；
#   LED 阳极 d21、阴极 d16；220 Ω a21–上边 +5 V 轨；电位器 f5(1)、f6(滑臂)、f7(3)，j5→+5 V，j7→GND，蓝线 i6→c11
# ======================================================================================
def node_06():
    RED = "#D55E00"
    yP, yN = 6.4, -4.2
    with drawing(fontsize=11) as d:
        title(d, (6.0, 7.8), "低边 MOS 管开关（低压版）：5 V、红 LED + 220 Ω 当负载，电位器代替单片机引脚")
        x0, x1 = -1.0, 13.2
        d += elm.Line().at((x0, yP)).to((x1, yP)).color(RED).linewidth(1.8)
        d += elm.Line().at((x0, yN)).to((x1, yN))
        lab(d, (x1 + 0.2, yP), "+5 V 轨", fs_=10.5, color=RED)
        lab(d, (x1 + 0.2, yN), "GND 轨", fs_=10.5)
        lab(d, (x0 - 0.2, yP), "5 V 电源 +", ha="right", fs_=10)
        lab(d, (x0 - 0.2, yN), "5 V 电源 −", ha="right", fs_=10)
        # 电位器
        xp = 0.6
        d += elm.Dot().at((xp, yP)); d += elm.Dot().at((xp, yN))
        d += elm.Line().at((xp, yP)).to((xp, 3.0)).color(RED).linewidth(1.8)
        d += (pot := elm.Potentiometer().endpoints((xp, 3.0), (xp, -2.0)))
        d += elm.Line().at((xp, -2.0)).to((xp, yN))
        lab(d, (xp - 0.6, 0.5), "电位器\n10 kΩ\n（代替单片机\n引脚）", ha="right", fs_=9.5)
        colnote(d, (xp + 0.15, 3.6), "1 脚 f5，红线 j5 → +5 V", "right", ofst=0.0)
        colnote(d, (xp + 0.15, -2.6), "3 脚 f7，黑线 j7 → GND", "right", ofst=0.0)
        tx, ty = pot.tap
        d += elm.Dot().at((tx, ty))
        colnote(d, (tx + 0.2, ty - 0.35), "滑臂 f6", "right", ofst=0.0)
        # 蓝线 → 驱动点（第 11 列）→ R_G → G（第 15 列）
        xdrv, xG = 3.6, 6.4
        d += elm.Line().at((tx, ty)).to((xdrv, ty)).color(BLUE).linewidth(1.8)
        lab(d, ((tx + xdrv) / 2, ty + 0.3), "蓝线 i6 → c11", ha="center", fs_=9, color=BLUE)
        d += elm.Dot().at((xdrv, ty))
        ring(d, (xdrv, ty), "驱动（第 11 列）", dx=0.0, dy=-1.0, ha="center")
        d += elm.Resistor().at((xdrv, ty)).to((xG, ty)).label("R_G 100 Ω\nb11–b15", loc="top")
        d += elm.Dot().at((xG, ty))
        ring(d, (xG + 0.9, ty), "G（第 15 列）", dx=0.0, dy=-0.8, ha="center")
        d += elm.Resistor().endpoints((xG, ty), (xG, yN)).label("R_GS 10 kΩ\ne15–f15\n黑线 j15", loc="bottom", ofst=0.2)
        d += elm.Dot().at((xG, yN))
        # MOS 管
        q = elm.NFet().theta(0).reverse().anchor("gate").at((xG + 1.4, ty))
        d += q
        d += elm.Line().at((xG, ty)).to(q.gate)
        xq = q.drain[0]
        lab(d, (xq + 0.5, ty + 0.1), "Q1 IRLZ44N\n（印字面朝你，\n左起 G、D、S）", fs_=9.5)
        lab(d, (q.gate[0] - 0.05, ty + 0.3), "G · a15", ha="right", fs_=9, color=GRAY)
        # 漏极 D（第 16 列）→ LED → A（第 21 列）→ 220 Ω → +5 V
        yD, yA = q.drain[1] + 1.2, q.drain[1] + 3.3
        d += elm.Line().at(q.drain).to((xq, yD))
        d += elm.Dot().at((xq, yD))
        lab(d, (xq + 0.25, q.drain[1] + 0.2), "D · a16", fs_=9, color=GRAY)
        ring(d, (xq, yD), "D（第 16 列）", dx=-1.3, dy=0.0, ha="right")
        d += elm.LED().endpoints((xq, yA), (xq, yD)).label("红 LED\n长脚 + d21\n短脚 − d16", loc="bottom", ofst=0.25)
        d += elm.Dot().at((xq, yA))
        ring(d, (xq, yA), "A（第 21 列）", dx=-1.3, dy=0.0, ha="right")
        d += elm.Resistor().endpoints((xq, yP), (xq, yA)).label("220 Ω\na21 → +5 V 轨", loc="bottom", ofst=0.25)
        d += elm.Dot().at((xq, yP))
        d += elm.Line().at(q.source).to((xq, yN))
        d += elm.Dot().at((xq, yN))
        lab(d, (xq + 0.25, q.source[1] - 0.25), "S · a17\n黑线 e17 → GND", fs_=9, color=GRAY)
        # 电流方向
        xa = xq + 2.6
        d += elm.Arrow().at((xa, yP - 0.5)).to((xa, yN + 0.6)).color(C["cur"]).linewidth(1.2)
        lab(d, (xa + 0.2, (yP + yN) / 2), "开通时\n约 13.4 mA\n+5 V → 220 Ω\n→ LED → D → S\n→ GND", fs_=9, color=C["cur"])
        # 步骤 10 的慢放电元件（灰色虚线框提示）
        lab(d, (3.2, -3.5), "步骤 10：R_GS 换 1 MΩ，\n再在 d15 与 GND 间并 10 µF", ha="center", fs_=8.5, color=GRAY)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 下红表笔的列（黑表笔一律插 GND 轨）；灰色小字 = 面包板孔位；天蓝色箭头 = 开通时的电流方向。",
            "导线颜色与面包板图一致：红 = 正电源（+5 V），黑 = 地（GND），蓝 = 输入信号（滑臂 → 驱动点）。源极接在 GND 上，所以 G、D 对 GND 的读数就是 V_GS 和 V_DS。",
            "上下两组电源轨在右边用一根红线、一根黑线连通；图中只画成一条 +5 V 轨和一条 GND 轨。",
        )
        for k, line in enumerate(notes):
            note(d, (-3.0, -5.4 - 0.6 * k), line)
    print("[图 06-p4-3] 滑臂(f6)→蓝线→驱动(第11列)→R_G→G(a15)；R_GS→GND；+5 V→220 Ω→A(第21列)→LED→D(a16)；S(a17)→GND")
    save_schem(d, "06", "06_p4_3_schem_lab.png")

# ======================================================================================
# 07 三极管驱动继电器：图 07-p4-1（07_p4_1_breadboard.png）→ 图 07-p4-2
# 面包板连线依据 code/figs/07_figs.py fig_p4_1：2N3904 E a15、B a16、C a17；e15→GND；R_B b11–b16；D1 阳极 d17、阴极 d22；
#   a22→+5 V 轨；线圈 1 ← c22、线圈 2 ← e17（绿线）；电位器 f5/f6/f7，j5→+5 V，j7→GND，蓝线 i6→c11；
#   触点侧（橙线，板外）：12 V+ → 小灯泡 → NO，COM → 12 V−，NC 悬空
# ======================================================================================
def node_07():
    RED, ORG = "#D55E00", C["vout"]
    yP, yN = 7.8, -4.2
    with drawing(fontsize=11) as d:
        title(d, (8.0, 9.2), "三极管驱动继电器（低压版）：线圈侧 5 V，触点侧只接 12 V 小灯泡，电位器代替单片机引脚")
        # 电位器 → 蓝线 → 驱动点（第 11 列）→ R_B → B（第 16 列）
        xp = 0.6
        d += (pot := elm.Potentiometer().endpoints((xp, 3.0), (xp, -2.0)))
        tx, ty = pot.tap
        xdrv, xB = 3.6, 6.4
        q = elm.BjtNpn(circle=True).right().anchor("base").at((xB + 2.4, ty))
        d += q
        xq = q.collector[0]
        x0, x1 = -1.0, xq + 1.6
        d += elm.Line().at((x0, yP)).to((x1, yP)).color(RED).linewidth(1.8)
        d += elm.Line().at((x0, yN)).to((x1, yN))
        lab(d, (x0 - 0.2, yP), "+5 V 轨", ha="right", fs_=10.5, color=RED)
        lab(d, (x0 - 0.2, yN), "GND 轨", ha="right", fs_=10.5)
        d += elm.Dot().at((xp, yP)); d += elm.Dot().at((xp, yN))
        d += elm.Line().at((xp, yP)).to((xp, 3.0)).color(RED).linewidth(1.8)
        d += elm.Line().at((xp, -2.0)).to((xp, yN))
        lab(d, (xp - 0.6, 0.5), "电位器\n10 kΩ\n（代替单片机\n引脚）", ha="right", fs_=9.5)
        colnote(d, (xp - 0.15, 3.6), "1 脚 f5，红线 j5 → +5 V", "left", ofst=0.0)
        colnote(d, (xp - 0.15, -2.6), "3 脚 f7，黑线 j7 → GND", "left", ofst=0.0)
        d += elm.Dot().at((tx, ty))
        colnote(d, (tx + 0.2, ty - 0.35), "滑臂 f6", "right", ofst=0.0)
        d += elm.Line().at((tx, ty)).to((xdrv, ty)).color(BLUE).linewidth(1.8)
        lab(d, ((tx + xdrv) / 2, ty + 0.3), "蓝线 i6 → c11", ha="center", fs_=9, color=BLUE)
        d += elm.Dot().at((xdrv, ty))
        ring(d, (xdrv, ty), "驱动（第 11 列）", dx=-0.5, dy=-1.0, ha="center")
        d += elm.Resistor().at((xdrv, ty)).to((xB, ty)).label("R_B 680 Ω\nb11–b16", loc="bottom")
        d += elm.Arrow().at((xdrv + 0.5, ty + 0.75)).to((xB - 0.5, ty + 0.75)).color(C["cur"]).linewidth(1.2)
        lab(d, ((xdrv + xB) / 2, ty + 1.1), "I_B ≈ 6.1 mA", ha="center", fs_=9, color=C["cur"])
        d += elm.Dot().at((xB, ty))
        ring(d, (xB, ty), "B（第 16 列）", dx=0.0, dy=-1.2, ha="center")
        d += elm.Line().at((xB, ty)).to(q.base)
        lab(d, (q.base[0] - 0.1, ty + 0.3), "B · a16", ha="right", fs_=9, color=GRAY)
        lab(d, (q.center[0] + 0.55, q.center[1] + 0.05), "Q1 2N3904\n（平面朝你，\n左起 E、B、C）", fs_=9.5)
        # 发射极 E → GND
        d += elm.Line().at(q.emitter).to((xq, yN))
        d += elm.Dot().at((xq, yN))
        lab(d, (xq + 0.2, q.emitter[1] - 1.2), "E · a15\n黑线 e15 → GND", fs_=9, color=GRAY)
        # 集电极 C（第 17 列）→ 线圈 → +5（第 22 列）→ 红线 a22 → +5 V 轨
        yC = q.collector[1] + 0.9
        y5 = yP - 1.3
        d += elm.Line().at(q.collector).to((xq, yC))
        lab(d, (xq + 0.2, q.collector[1] + 0.25), "C · a17", fs_=9, color=GRAY)
        d += elm.Dot().at((xq, yC))
        d += elm.Line().at((xq, yP)).to((xq, y5)).color(RED).linewidth(1.8)
        lab(d, (xq + 0.2, (yP + y5) / 2), "红线 a22", fs_=9, color=RED)
        d += elm.Dot().at((xq, yP))
        d += elm.Dot().at((xq, y5))
        yc_t, yc_b = y5 - 0.6, yC + 0.6
        d += elm.Line().at((xq, y5)).to((xq, yc_t)).color(TEAL).linewidth(1.8)
        d += Coil().endpoints((xq, yc_t), (xq, yc_b))
        d += elm.Line().at((xq, yc_b)).to((xq, yC)).color(TEAL).linewidth(1.8)
        ym = (yc_t + yc_b) / 2
        lab(d, (xq + 0.45, ym + 0.75), "继电器线圈\nSRD-05VDC 70 Ω", fs_=9.5)
        colnote(d, (xq + 0.1, yc_t + 0.3), "线圈 1 ← 绿线 c22", "right", ofst=0.05)
        colnote(d, (xq + 0.1, yc_b - 0.3), "线圈 2 ← 绿线 e17", "right", ofst=0.05)
        # 续流二极管：阳极 d17（C 列），阴极 d22（+5 列）
        xd = xq - 2.6
        d += elm.Line().at((xq, y5)).to((xd, y5))
        d += elm.Line().at((xq, yC)).to((xd, yC))
        d += elm.Diode().endpoints((xd, yC), (xd, y5))
        lab(d, (xd - 0.4, ym + 0.35), "D1 1N4148", ha="right", fs_=10)
        lab(d, (xd - 0.4, ym - 0.35), "阴极（色环）d22\n阳极 d17", ha="right", fs_=8.5, color=GRAY)
        ring(d, ((xd + xq) / 2, y5), "+5（第 22 列）", dx=0.0, dy=0.55, ha="center")
        ring(d, ((xd + xq) / 2, yC), "C（第 17 列）", dx=0.0, dy=0.55, ha="center")
        # 线圈电流
        d += elm.Arrow().at((xq - 0.55, yc_t - 0.1)).to((xq - 0.55, yc_b + 0.1)).color(C["cur"]).linewidth(1.2)
        lab(d, (xq - 0.75, ym), "约\n67.6 mA", ha="right", fs_=9.5, color=C["cur"])
        # 触点侧：12 V+ → 小灯泡 → NO；COM → 12 V−（橙线，鳄鱼夹线，不经过面包板）
        xs, xb = xq + 6.4, xq + 11.4
        yno, ycom = ym + 1.0, ym - 1.0
        yt, yb = ym + 3.0, ym - 3.2
        d += ContactNO().endpoints((xs, yno), (xs, ycom))
        lab(d, (xs + 0.6, ym + 0.1), "K1 常开触点", fs_=10)
        colnote(d, (xs - 0.1, yno + 0.15), "NO", "left", ofst=0.0)
        colnote(d, (xs - 0.1, ycom - 0.1), "COM", "left", ofst=0.0)
        lab(d, (xs + 0.6, ym - 0.55), "NC 悬空不接", fs_=8.5, color=GRAY)
        d += elm.Line().at((xs, yno)).to((xs, yt)).color(ORG).linewidth(1.8)
        xl0, xl1 = (xs + xb) / 2 - 0.9, (xs + xb) / 2 + 0.9
        d += elm.Line().at((xs, yt)).to((xl0, yt)).color(ORG).linewidth(1.8)
        d += LampX().endpoints((xl0, yt), (xl1, yt))
        d += elm.Line().at((xl1, yt)).to((xb, yt)).color(ORG).linewidth(1.8)
        lab(d, ((xs + xb) / 2, yt + 0.75), "12 V 小灯泡", ha="center", fs_=10)
        d += elm.Line().at((xs, ycom)).to((xs, yb)).color(ORG).linewidth(1.8)
        d += elm.Line().at((xs, yb)).to((xb, yb)).color(ORG).linewidth(1.8)
        yb0, yb1 = ym - 1.0, ym + 0.8
        d += elm.Line().at((xb, yt)).to((xb, yb1)).color(ORG).linewidth(1.8)
        d += elm.Battery().endpoints((xb, yb0), (xb, yb1)).reverse()
        d += elm.Line().at((xb, yb0)).to((xb, yb)).color(ORG).linewidth(1.8)
        lab(d, (xb + 0.5, ym + 0.3), "12 V 直流\n电源（适配器）", fs_=10)
        lab(d, (xb - 0.45, ym + 0.55), "+", ha="right", fs_=11, color=RED)
        lab(d, (xb - 0.45, ym - 0.75), "−", ha="right", fs_=11)
        d += elm.Arrow().at((xb - 1.2, yt - 0.45)).to((xs + 1.2, yt - 0.45)).color(C["cur"]).linewidth(1.2)
        lab(d, ((xs + xb) / 2, yt - 0.85), "吸合时灯泡电流", ha="center", fs_=8.5, color=C["cur"])
        lab(d, ((xs + xb) / 2, yb - 0.5), "橙线 = 触点侧 12 V 回路（鳄鱼夹线，板外）", ha="center", fs_=8.5, color=ORG)
        # 线圈与触点之间只有磁力联系
        d += elm.Line().at((xq + 0.35, ym)).to((xs - 0.35, ym)).linestyle(":").color("#737373")
        lab(d, ((xq + xs) / 2 + 0.6, ym - 0.35), "磁力带动（不是导线）", ha="center", fs_=8.5, color=GRAY)
        lab(d, ((xs + xb) / 2, yb - 1.1), "触点侧和线圈侧没有任何导线相连，也不共地", ha="center", fs_=9, color=GRAY)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 下红表笔的列（黑表笔一般插 GND 轨）；灰色小字 = 面包板孔位；天蓝色箭头 = 吸合时的电流方向。",
            "导线颜色与面包板图一致：红 = 正电源（+5 V），黑 = 地（GND），蓝 = 输入信号（滑臂 → 驱动点），绿 = 接继电器线圈，橙 = 触点侧 12 V 回路。",
            "上下两组电源轨在右边用一根红线、一根黑线连通；图中只画成一条 +5 V 轨和一条 GND 轨。步骤 5 把 R_B 换成 10 kΩ，位置不变（b11–b16）。",
        )
        for k, line in enumerate(notes):
            note(d, (-3.0, -5.4 - 0.6 * k), line)
    print("[图 07-p4-2] 滑臂(f6)→蓝线→驱动(第11列)→R_B→B(a16)；E(a15)→GND；+5 V→a22→+5(第22列)→线圈→C(a17)；D1 阳极 d17、阴极 d22；12 V+→灯泡→NO，COM→12 V−")
    save_schem(d, "07", "07_p4_2_schem_lab.png")

# ======================================================================================
# 23 光耦隔离（PC817）：图 23-p4-1 → 图 23-p4-3
# 依据 code/figs/23_figs.py 的 fig_p4_1()：上方两条轨 = +5 V / GND（输出侧），下方两条轨 = 电池− / +9 V（输入侧），两组轨不相连
#   PC817 1 脚 A f20、2 脚 K f21、3 脚 E e21、4 脚 C e20；+9 V→j5，按钮 h5–h9，R_in 1 kΩ i9–i14，红色 LED g14(+)–g19，蓝线 h19→h20，紫线 j21→电池−
#   R_L d20–d26，红线 a26→+5 V，黑线 a21→GND，C 470 μF b20(+)–b23，黑线 a23→GND，橙线 c20→表笔；测量点 OUT a20、P j9、Q j14、A j20
# ======================================================================================
def node_23():
    RED, ORG = C["bad"], C["vout"]
    yT = 0.0                     # 输入回路上沿 / 输出节点高度
    yB1 = -4.2                   # 输入侧「电池−」轨
    yP5, yG2 = 3.6, -3.2         # 输出侧 +5 V 轨、GND 轨
    with drawing(fontsize=11) as d:
        title(d, (-2.0, 5.6), "PC817 上拉电阻与上升时间实验：输入侧 9 V 电池（下半区），输出侧 5 V（上半区），两个地不相连")
        d += (oc := elm.Optocoupler().at((0, 0)))
        lab(d, (0.75, 0.75), "PC817", ha="center", fs_=10.5)
        ax_, ay = oc.anode
        kx, ky = oc.cathode
        cx, cy = oc.collector
        ex, ey = oc.emitter
        lab(d, (ax_ - 0.1, ay + 0.3), "1 脚 A · f20", ha="right", fs_=9, color=GRAY)
        lab(d, (kx - 0.3, ky - 0.3), "2 脚 K · f21", ha="right", fs_=9, color=GRAY)
        lab(d, (cx + 0.12, cy + 0.3), "4 脚 C · e20", fs_=9, color=GRAY)
        lab(d, (ex + 0.25, ey - 0.3), "3 脚 E · e21", fs_=9, color=GRAY)
        # ---------------- 输入侧：+9 V → 按钮 → P → R_in → Q → 红色 LED → 蓝线 → A（1 脚）；2 脚 → 紫线 → 电池− ----------------
        xbat, xs0, xs1, xr1, xl1, xA = -14.0, -12.6, -10.6, -7.4, -4.8, -1.6
        d += elm.Line().at((xbat, yB1)).to((kx, yB1)).color(PURPLE).linewidth(1.8)
        lab(d, (xbat + 0.2, yB1 - 0.45), "「电池−」轨（输入侧地 = 9 V 电池负极，不接 GND）", fs_=9.5, color=PURPLE)
        yb0, yb1 = -2.9, -1.1
        d += elm.Line().at((xbat, yB1)).to((xbat, yb0)).color(PURPLE).linewidth(1.8)
        d += elm.Battery().endpoints((xbat, yb0), (xbat, yb1)).reverse()
        d += elm.Line().at((xbat, yb1)).to((xbat, yT)).color(RED).linewidth(1.8)
        lab(d, (xbat - 0.5, (yb0 + yb1) / 2 + 0.2), "9 V 电池\n（输入侧电源）", ha="right", fs_=10)
        lab(d, (xbat - 0.45, yb1 - 0.05), "+", ha="right", fs_=11, color=RED)
        lab(d, (xbat - 0.45, yb0 + 0.05), "−", ha="right", fs_=11)
        d += elm.Line().at((xbat, yT)).to((xs0, yT)).color(RED).linewidth(1.8)
        lab(d, ((xbat + xs0) / 2, yT + 0.35), "+9 V 轨\n红线 j5", ha="center", fs_=9, color=RED)
        d += elm.Button().endpoints((xs0, yT), (xs1, yT))
        lab(d, ((xs0 + xs1) / 2, yT + 1.0), "按钮 S\nh5–h9", ha="center", fs_=9.5)
        d += elm.Dot().at((xs1, yT))
        ring(d, (xs1, yT), "P（第 9 列）", dx=0.0, dy=-1.2, ha="center")
        d += elm.Resistor().endpoints((xs1, yT), (xr1, yT)).label("R_in 1 kΩ\ni9–i14", loc="top")
        d += elm.Dot().at((xr1, yT))
        ring(d, (xr1, yT), "Q（第 14 列）", dx=0.0, dy=-1.2, ha="center")
        d += elm.LED().endpoints((xr1, yT), (xl1, yT))
        lab(d, ((xr1 + xl1) / 2, yT + 1.0), "红色指示 LED\n长脚（+）g14，短脚 g19", ha="center", fs_=9)
        d += elm.Line().at((xl1, yT)).to((xA, yT)).color(BLUE).linewidth(1.8)
        lab(d, ((xl1 + xA) / 2, yT + 0.35), "蓝线 h19→h20", ha="center", fs_=9, color=BLUE)
        d += elm.Dot().at((xA, yT))
        d += elm.Line().at((xA, yT)).to(oc.anode)
        ring(d, (xA, yT), "A（第 20 列下半区）", dx=0.0, dy=1.1, ha="center")
        d += elm.Line().at(oc.cathode).to((kx, yB1)).color(PURPLE).linewidth(1.8)
        d += elm.Dot().at((kx, yB1))
        lab(d, (kx - 0.15, (ky + yB1) / 2), "紫线 j21\n→「电池−」轨", ha="right", fs_=9, color=PURPLE)
        d += elm.Arrow().at((xs1 + 0.3, yT + 2.8)).to((xA - 1.6, yT + 2.8)).color(C["cur"]).linewidth(1.2)
        lab(d, ((xs1 + xA) / 2 - 0.8, yT + 3.15), "按住按钮：I_F ≈ 6.0 mA（R_in 两端约 6.0 V）", ha="center", fs_=9, color=C["cur"])
        # ---------------- 输出侧：+5 V → 红线 a26 → R_L → 第 20 列（4 脚 C）→ 光敏三极管 → 3 脚 E → 黑线 a21 → GND ----------------
        xn, xc, xo, xsup = 3.4, 6.2, 9.0, 11.6
        d += elm.Line().at((2.0, yP5)).to((xsup, yP5)).color(RED).linewidth(1.8)
        d += elm.Line().at((ex, yG2)).to((xsup, yG2))
        lab(d, (xsup + 0.25, yP5 + 0.35), "+5 V 轨", fs_=10, color=RED)
        lab(d, (xsup + 0.25, yG2 - 0.4), "GND 轨（输出侧地）", fs_=10)
        d += elm.Line().at(oc.collector).to((xn, cy))
        d += elm.Dot().at((xn, cy))
        d += elm.Resistor().endpoints((xn, cy), (xn, yP5 - 0.8))
        d += elm.Line().at((xn, yP5 - 0.8)).to((xn, yP5)).color(RED).linewidth(1.8)
        d += elm.Dot().at((xn, yP5))
        lab(d, (xn - 0.45, (cy + yP5) / 2 - 0.1), "R_L d20–d26\n2.2 k / 4.7 k /\n10 k / 47 k", ha="right", fs_=9)
        lab(d, (xn + 0.15, yP5 - 0.45), "红线 a26", fs_=8.5, color=RED)
        ring(d, (xn, cy), "OUT（第 20 列上半区）", dx=1.2, dy=-1.6, ha="center")
        d += elm.Line().at((xn, cy)).to((xc, cy))
        d += elm.Dot().at((xc, cy))
        d += elm.Capacitor(polar=True).endpoints((xc, cy), (xc, yG2 + 0.7)).linestyle("--")
        d += elm.Line().at((xc, yG2 + 0.7)).to((xc, yG2)).linestyle("--")
        d += elm.Dot().at((xc, yG2))
        lab(d, (xc + 0.45, cy - 1.3), "C 470 μF\n+ b20，− b23\n黑线 a23→GND\n（第 8 步才插，虚线）", fs_=8.5)
        d += elm.Line().at((xc, cy)).to((xo, cy)).color(ORG).linewidth(1.8)
        d += elm.Dot(open=True).at((xo, cy))
        lab(d, (xo, cy + 0.75), "橙线 c20 →\n万用表红表笔\n或示波器探头", ha="center", fs_=8.5, color=ORG)
        d += elm.Line().at(oc.emitter).to((ex, yG2))
        d += elm.Dot().at((ex, yG2))
        lab(d, (ex + 0.12, (ey + yG2) / 2 - 0.2), "黑线 a21", fs_=8.5)
        d += elm.SourceV().endpoints((xsup, yG2), (xsup, yP5))
        lab(d, (xsup + 0.6, 0.2), "5 V 电源\n（USB 稳压模块，\n输出侧电源）", fs_=10)
        d += elm.Arrow().at((xn + 0.5, yP5 - 1.0)).to((xn + 0.5, cy + 0.9)).color(C["cur"]).linewidth(1.2)
        lab(d, (xn + 0.65, 2.1), "按住时 I_C\n（不按 = 0，OUT ≈ 5 V）", fs_=8.5, color=C["cur"])
        # ---------------- 隔离带 ----------------
        barrier(d, 0.75, yB1 - 0.4, 4.3, text="隔离带：没有任何导线跨过（光是唯一的通路）")
        lab(d, (-7.0, 4.3), "输入侧（面包板下半区）", ha="center", fs_=11, color=PURPLE)
        lab(d, (6.5, 4.6), "输出侧（面包板上半区）", ha="center", fs_=11)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 下红表笔的列；灰色小字 = PC817 引脚号和面包板孔位；天蓝色箭头 = 按住按钮时的电流方向。",
            "两个地不是同一个：OUT 对 GND 轨量；P、Q、A 对「电池−」轨量。断电时两轨之间应是开路（测量表步骤 1）。",
            "导线颜色与面包板图一致：红 = 正电源（+9 V、+5 V），黑 = 地（0 V），紫 = 输入侧地（电池负极，不接 GND），蓝 = 输入信号，橙 = 输出（4 脚）。",
        )
        for k, line in enumerate(notes):
            note(d, (-15.5, -5.6 - 0.6 * k), line)
    print("[图 23-p4-3] +9 V→j5→按钮 h5–h9→P(第9列)→R_in 1k i9–i14→Q(第14列)→红LED g14–g19→蓝线 h19→h20→1 脚 A f20；2 脚 K f21→紫线 j21→电池−；"
          "+5 V→a26→R_L d20–d26→第20列(4 脚 C e20，OUT)→3 脚 E e21→a21→GND；C 470μF b20(+)–b23→a23→GND；橙线 c20→表笔")
    save_schem(d, "23", "23_p4_3_schem_lab.png")


# ======================================================================================
# 28 隔离电源（B0505S）：图 28-p4-1 → 图 28-p4-3
# 依据 code/figs/28_figs.py 的 fig_p4_1()：上两条轨 = +5 V / GND（输入侧），下两条轨 = 0V / +Vo（隔离侧），上下两组轨不相连
#   B0505S 1 脚 GND c8、2 脚 Vin c9、3 脚 0V c10、4 脚 +Vo c11；黑线 a8→GND 轨，红线 a9→+5 V 轨；C_in 4.7 μF 第 4 列（两条上方轨之间）
#   紫线 e10→f10、j10→0V 轨；绿线 e11→f11、j11→+Vo 轨；C_out 10 μF 第 14 列、R_L 第 20 列（两条下方轨之间）；A/B 在上方轨第 13 列，C/D 在下方轨第 26 列
# ======================================================================================
def node_28():
    RED, GRN = C["bad"], C["fb"]
    yP, yN = 4.6, -2.2
    with drawing(fontsize=11) as d:
        title(d, (1.5, 6.9), "B0505S 隔离模块实验：左边输入侧（上两条轨），右边隔离侧（下两条轨），两个地不相连")
        d += (m := module("B0505S", left=("Vin", "GND"), right=("+Vo", "0V"), w=3.0).at((0, 0)))
        A = m.absanchors
        vin, gnd, vo, ov = A["Vin"], A["GND"], A["+Vo"], A["0V"]
        lab(d, (vin[0] - 0.05, vin[1] + 0.25), "2 脚 Vin · c9", ha="right", fs_=9, color=GRAY)
        lab(d, (gnd[0] - 0.05, gnd[1] - 0.25), "1 脚 GND · c8", ha="right", fs_=9, color=GRAY)
        lab(d, (vo[0] + 0.05, vo[1] + 0.25), "4 脚 +Vo · c11", fs_=9, color=GRAY)
        lab(d, (ov[0] + 0.05, ov[1] - 0.25), "3 脚 0V · c10", fs_=9, color=GRAY)
        lab(d, (1.5, -0.45), "1 W，不稳压", ha="center", fs_=9, color=GRAY)
        # ---------------- 输入侧 ----------------
        xl, xv, xg = -11.0, -1.6, -2.8
        d += elm.Line().at((xl, yP)).to((xv, yP)).color(RED).linewidth(1.8)
        d += elm.Line().at((xl, yN)).to((xg, yN))
        lab(d, (xl - 0.2, yP), "+5 V 轨", ha="right", fs_=10.5, color=RED)
        lab(d, (xl - 0.2, yN), "GND 轨\n（输入侧地）", ha="right", fs_=10.5)
        d += elm.Line().at(vin).to((xv, vin[1])).color(RED).linewidth(1.8)
        d += elm.Line().at((xv, vin[1])).to((xv, yP)).color(RED).linewidth(1.8)
        d += elm.Dot().at((xv, yP))
        lab(d, (xv + 0.15, (vin[1] + yP) / 2), "红线 a9", fs_=9, color=RED)
        d += elm.Line().at(gnd).to((xg, gnd[1]))
        d += elm.Line().at((xg, gnd[1])).to((xg, yN))
        d += elm.Dot().at((xg, yN))
        lab(d, (xg - 0.15, (gnd[1] + yN) / 2), "黑线 a8", ha="right", fs_=9)
        xs, xc = -10.0, -7.4
        d += elm.SourceV().endpoints((xs, yN), (xs, yP))
        d += elm.Dot().at((xs, yP)); d += elm.Dot().at((xs, yN))
        lab(d, (xs + 0.6, 1.6), "5 V 电源\n（USB 电源\n模块）", fs_=9.5)
        d += elm.Capacitor(polar=True).endpoints((xc, yP), (xc, yN))
        d += elm.Dot().at((xc, yP)); d += elm.Dot().at((xc, yN))
        lab(d, (xc + 0.45, 1.2), "C_in 4.7 μF\n第 4 列\n（长脚 +5 V 轨）", fs_=9)
        ring(d, (-4.6, yP), "B（+5 V 轨）", dx=0.0, dy=0.7, ha="center")
        ring(d, (-4.6, yN), "A（GND 轨）", dx=0.0, dy=-0.7, ha="center")
        d += elm.Dot().at((-4.6, yP)); d += elm.Dot().at((-4.6, yN))
        d += elm.Arrow().at((xv - 0.4, yP - 0.4)).to((xv - 0.4, vin[1] + 0.6)).color(C["cur"]).linewidth(1.2)
        lab(d, (xv - 0.55, (yP + vin[1]) / 2 + 0.1), "输入电流\n满载约 244 mA", ha="right", fs_=8.5, color=C["cur"])
        # ---------------- 隔离侧 ----------------
        xo, xz, xr = 4.6, 5.8, 13.6
        d += elm.Line().at((xo, yP)).to((xr + 0.4, yP)).color(GRN).linewidth(1.8)
        d += elm.Line().at((xz, yN)).to((xr + 0.4, yN)).color(PURPLE).linewidth(1.8)
        lab(d, (xr + 0.6, yP), "+Vo 轨（面包板最下面\n一条，隔离侧正）", fs_=10, color=GRN)
        lab(d, (xr + 0.6, yN), "0V 轨（隔离侧地，\n不是 GND）", fs_=10, color=PURPLE)
        d += elm.Line().at(vo).to((xo, vo[1])).color(GRN).linewidth(1.8)
        d += elm.Line().at((xo, vo[1])).to((xo, yP)).color(GRN).linewidth(1.8)
        d += elm.Dot().at((xo, yP))
        lab(d, (xo + 0.15, (vo[1] + yP) / 2 + 0.2), "绿线 e11→f11，\nj11→+Vo 轨", fs_=8.5, color=GRN)
        d += elm.Line().at(ov).to((xz, ov[1])).color(PURPLE).linewidth(1.8)
        d += elm.Line().at((xz, ov[1])).to((xz, yN)).color(PURPLE).linewidth(1.8)
        d += elm.Dot().at((xz, yN))
        lab(d, (xz + 0.15, (ov[1] + yN) / 2), "紫线 e10→f10，\nj10→0V 轨", fs_=8.5, color=PURPLE)
        xco, xrl = 8.4, 11.0
        d += elm.Capacitor(polar=True).endpoints((xco, yP), (xco, yN))
        d += elm.Dot().at((xco, yP)); d += elm.Dot().at((xco, yN))
        lab(d, (xco + 0.45, 1.2), "C_out 10 μF\n第 14 列\n（长脚 +Vo 轨）", fs_=9)
        d += elm.Resistor().endpoints((xrl, yP), (xrl, yN))
        d += elm.Dot().at((xrl, yP)); d += elm.Dot().at((xrl, yN))
        lab(d, (xrl + 0.45, 1.2), "R_L 第 20 列\n空 / 240 Ω /\n51 Ω / 25 Ω", fs_=9)
        d += elm.Arrow().at((xrl - 0.45, yP - 1.0)).to((xrl - 0.45, yN + 1.0)).color(C["cur"]).linewidth(1.2)
        ring(d, (xr, yP), "D（+Vo 轨）", dx=0.0, dy=0.7, ha="center")
        ring(d, (xr, yN), "C（0V 轨）", dx=0.0, dy=-0.7, ha="center")
        d += elm.Dot().at((xr, yP)); d += elm.Dot().at((xr, yN))
        # ---------------- 隔离带 ----------------
        barrier(d, 1.5, yN - 0.8, 5.6, text="隔离带（在模块里面：能量只经变压器过去）")
        lab(d, (-6.0, 6.1), "输入侧（面包板上两条轨）", ha="center", fs_=11)
        lab(d, (9.0, 6.1), "隔离侧（面包板下两条轨）", ha="center", fs_=11, color=PURPLE)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 下表笔的位置（A、B 在上方轨第 13 列，C、D 在下方轨第 26 列，插轨上任一空孔都行）；灰色小字 = B0505S 引脚号和孔位。",
            "GND 轨和 0V 轨是两个不同的地：断电时 A、B 对 C、D 都应开路（测量表步骤 1～4）；第 5 步临时加的短接线就是把这两条线连起来，量完马上拔掉。",
            "导线颜色与面包板图一致：红 = 正电源（+5 V），黑 = 地（0 V，输入侧），绿 = 隔离侧 +Vo（4 脚），紫 = 隔离侧 0V（3 脚）。天蓝色箭头 = 电流方向。",
        )
        for k, line in enumerate(notes):
            note(d, (-13.5, -4.0 - 0.6 * k), line)
    print("[图 28-p4-3] +5 V 轨→红线 a9→2 脚 Vin c9；1 脚 GND c8→黑线 a8→GND 轨；C_in 第 4 列；4 脚 +Vo c11→绿线 e11/f11/j11→+Vo 轨；"
          "3 脚 0V c10→紫线 e10/f10/j10→0V 轨；C_out 第 14 列、R_L 第 20 列；A/B 第 13 列，C/D 第 26 列")
    save_schem(d, "28", "28_p4_3_schem_lab.png")


def node_26():
    RED, BLU, ORG = C["bad"], C["vin"], C["vout"]
    yP, yG, yB = 7.5, -2.5, -4.5
    with drawing(fontsize=11) as d:
        title(d, (8.0, 9.3), "H 桥实验（图中为正转：ENA = 1、IN1 = 1、IN2 = 0）：面包板只切换三根控制线，电机电流不经过面包板")
        d += (m := module("L298N 模块", left=("ENA", "IN1", "IN2", "+5V"), right=("OUT1", "OUT2", "+12V", "GND"), w=4.0).at((13.0, 0)))
        A = m.absanchors
        for k, n in (("ENA", "6"), ("IN1", "5"), ("IN2", "7"), ("+5V", "9")):
            lab(d, (A[k][0] + 0.3, A[k][1] + 0.22), n, ha="center", fs_=8.5, color=GRAY)
        for k, n in (("OUT1", "2"), ("OUT2", "3"), ("+12V", "4"), ("GND", "8")):
            lab(d, (A[k][0] - 0.3, A[k][1] + 0.22), n, ha="center", fs_=8.5, color=GRAY)
        lab(d, (15.0, -0.45), "5V-EN、ENA 跳线帽都已拔掉", ha="center", fs_=9, color=GRAY)
        # ---------- 面包板：三根控制线 ----------
        xE, xI1, xI2 = 0.0, 4.0, 8.0
        d += elm.Line().at((-3.0, yP)).to((xI1, yP)).color(RED).linewidth(1.8)
        lab(d, (-3.2, yP), "+5 V 轨\n（面包板下方）", ha="right", fs_=10.5, color=RED)
        d += elm.Line().at((-2.0, yG)).to((xI2, yG))
        lab(d, (-2.2, yG + 0.05), "GND 轨", ha="right", fs_=10.5)
        # ENA：第 6 列
        d += elm.Line().at((xE, 4.0)).to((xE, yP)).color(RED).linewidth(1.8)
        d += elm.Dot().at((xE, yP))
        lab(d, (xE + 0.15, 6.0), "i6 → +5 V 轨\n第 7 列：ENA = 1", fs_=8.5, color=RED)
        d += elm.Line().at((xE, 4.0)).to((xI1 - 0.25, 4.0)).color(BLU).linewidth(1.8)
        d += Hop().at((xI1, 4.0)).theta(0).color(BLU).linewidth(1.8)
        d += elm.Line().at((xI1 + 0.25, 4.0)).to(A["ENA"]).color(BLU).linewidth(1.8)
        lab(d, (xE + 0.3, 4.25), "蓝线 f6 → ENA", fs_=8.5, color=BLU)
        # IN1：第 12 列
        d += elm.Line().at((xI1, 3.0)).to((xI1, yP)).color(RED).linewidth(1.8)
        d += elm.Dot().at((xI1, yP))
        lab(d, (xI1 + 0.15, 6.0), "i12 → +5 V 轨\n第 13 列：IN1 = 1", fs_=8.5, color=RED)
        d += elm.Line().at((xI1, 3.0)).to(A["IN1"]).color(BLU).linewidth(1.8)
        lab(d, (xI1 + 0.3, 3.25), "蓝线 f12 → IN1", fs_=8.5, color=BLU)
        # IN2：第 18 列
        d += elm.Line().at((xI2, 2.0)).to((xI2, 1.25)).linewidth(1.8)
        d += elm.Line().at((xI2, 0.75)).to((xI2, yG)).linewidth(1.8)
        d += elm.Dot().at((xI2, yG))
        lab(d, (xI2 + 0.15, -0.9), "i18 → GND 轨\n第 19 列：IN2 = 0", fs_=8.5)
        d += elm.Line().at((xI2, 2.0)).to(A["IN2"]).color(BLU).linewidth(1.8)
        lab(d, (xI2 + 0.3, 2.25), "蓝线 f18 → IN2", fs_=8.5, color=BLU)
        for (x, y), t in (((xE, 4.0), "第 6 列\n（f6 · i6）"), ((xI1, 3.0), "第 12 列\n（f12 · i12）"), ((xI2, 2.0), "第 18 列\n（f18 · i18）")):
            d += elm.Dot().at((x, y))
            lab(d, (x - 0.15, y - 0.55), t, ha="right", fs_=8.5, color=GRAY)
        # ---------- Arduino ----------
        _dbox(d, -7.5, -1.5, -4.5, 2.0)
        lab(d, (-6.0, 0.5), "Arduino UNO\n（只用 5V、GND、D9）", ha="center", fs_=9)
        lab(d, (-4.6, 1.25), "5V", ha="right", fs_=8.5, color=GRAY)
        lab(d, (-4.6, -0.25), "GND", ha="right", fs_=8.5, color=GRAY)
        lab(d, (-6.0, -1.3), "GND", ha="center", fs_=8.5, color=GRAY)
        d += elm.Line().at((-4.5, 1.0)).to((-3.0, 1.0)).color(RED).linewidth(1.8)
        d += elm.Dot().at((-3.0, 1.0))
        d += elm.Line().at((-3.0, 1.0)).to((-3.0, yP)).color(RED).linewidth(1.8)
        lab(d, (-3.15, 4.6), "红线 Arduino 5V\n→ +5 V 轨第 26 列", ha="right", fs_=8.5, color=RED)
        d += elm.Line().at((-3.0, 1.0)).to((xI2 - 0.25, 1.0)).color(RED).linewidth(1.8)
        d += Hop().at((xI2, 1.0)).theta(0).color(RED).linewidth(1.8)
        d += elm.Line().at((xI2 + 0.25, 1.0)).to(A["+5V"]).color(RED).linewidth(1.8)
        lab(d, (xI2 + 0.4, 0.75), "红线 → 模块 +5V 端子", fs_=8.5, color=RED)
        d += elm.Line().at((-4.5, -0.5)).to((-2.0, -0.5)).linewidth(1.8)
        d += elm.Line().at((-2.0, -0.5)).to((-2.0, yG)).linewidth(1.8)
        lab(d, (-1.85, -1.3), "黑线 → GND\n轨第 25 列", fs_=8.5)
        d += elm.Line().at((-6.0, -1.5)).to((-6.0, yB)).linewidth(1.8)
        d += elm.Line().at((-6.0, yB)).to((19.0, yB)).linewidth(1.8)
        lab(d, (6.5, yB + 0.25), "黑线 Arduino GND → 模块 GND 端子", ha="center", fs_=8.5)
        # ---------- 模块右侧：电机与 6 V 电池 ----------
        d += elm.Line().at(A["GND"]).to((19.0, A["GND"][1])).linewidth(1.8)
        d += elm.Line().at((19.0, A["GND"][1])).to((19.0, yB)).linewidth(1.8)
        d += elm.Dot().at((19.0, yB))
        xb = 22.0
        d += elm.Battery().endpoints((xb, -2.5), (xb, 0.8)).reverse()
        lab(d, (xb + 0.6, -0.85), "6 V 电池盒\n（4 节 AA）", fs_=9.5)
        lab(d, (xb - 0.45, 0.45), "+", ha="center", fs_=11, color=RED)
        lab(d, (xb - 0.45, -2.15), "−", ha="center", fs_=11)
        d += elm.Line().at((xb, 0.8)).to((xb, 2.0)).color(RED).linewidth(1.8)
        d += elm.Line().at((xb, 2.0)).to(A["+12V"]).color(RED).linewidth(1.8)
        lab(d, (19.8, 2.25), "+12V 端子（接 6 V）", ha="center", fs_=8.5, color=RED)
        d += elm.Line().at((xb, -2.5)).to((xb, -3.5)).linewidth(1.8)
        d += elm.Line().at((xb, -3.5)).to((19.0, -3.5)).linewidth(1.8)
        d += elm.Dot().at((19.0, -3.5))
        lab(d, (20.5, -3.85), "电池负极 → GND 端子", ha="center", fs_=8.5)
        xm = 21.5
        d += elm.Line().at(A["OUT1"]).to((19.0, 4.0)).color(ORG).linewidth(1.8)
        d += elm.Line().at((19.0, 4.0)).to((19.0, 7.0)).color(ORG).linewidth(1.8)
        d += elm.Line().at((19.0, 7.0)).to((xm, 7.0)).color(ORG).linewidth(1.8)
        d += elm.Motor().endpoints((xm, 7.0), (xm, 3.0))
        d += elm.Line().at(A["OUT2"]).to((xm, 3.0)).color(ORG).linewidth(1.8)
        lab(d, (xm + 0.75, 5.0), "M 小直流电机\n（6 V）", fs_=9.5)
        lab(d, (19.15, 5.5), "橙线\nOUT1", fs_=8.5, color=ORG)
        lab(d, (19.6, 2.75), "橙线 OUT2", ha="center", fs_=8.5, color=ORG)
        d += elm.Arrow().at((xm + 0.55, 4.6)).to((xm + 0.55, 3.4)).color(C["cur"]).linewidth(1.2)
        lab(d, (xm + 0.75, 3.9), "正转电流：\nOUT1 → M → OUT2", fs_=8.5, color=C["cur"])
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；半圆跨线弯 = 两线交叉但不相连；模块边上的灰色小数字 = 板上 L298 芯片（Multiwatt15 封装）的引脚号。",
            "改状态只挪 i 排那一根跳线：接 +5 V 轨 = 1，接 GND 轨 = 0；PWM 时拔掉 i12 的跳线，把 Arduino D9 接到第 12 列。",
            "三处地（电池负极、Arduino GND、面包板 GND 轨）连在一起，是同一个公共地，这一节没有隔离。",
            "导线颜色与面包板图一致：红 = +5 V（逻辑）/ +6 V（电机电源），黑 = GND（公共地），蓝 = 控制信号 ENA / IN1 / IN2，橙 = 电机线 OUT1 / OUT2。天蓝色箭头 = 电流方向。",
        )
        for k, line in enumerate(notes):
            note(d, (-7.5, -5.6 - 0.6 * k), line)
    print("[图 26-p4-3] f6/f12/f18 → ENA/IN1/IN2（6/5/7 脚）；i6、i12 → +5 V 轨，i18 → GND 轨；Arduino 5V → +5 V 轨与 +5V 端子；"
          "GND 三处共地；6 V 电池 → +12V/GND 端子；OUT1/OUT2 → 电机")
    save_schem(d, "26", "26_p4_3_schem_lab.png")


def node_29():
    import schemdraw.logic as _lg
    ORG, BLU, GRN = C["vout"], C["vin"], C["fb"]
    # ================= 图 29-p4-3：慢动作去抖（对应 29-p4-1） =================
    yP, yG = 6.0, -3.0
    with drawing(fontsize=11) as d:
        title(d, (6.5, 7.6), "慢动作去抖：5 V 经 R1 到 A 点，按键从 A 接地；A 经 R2 到 B 点，B 点对地接 C1 并送进 74HC14 的 1 脚")
        xr = 17.5
        d += elm.Line().at((-4.0, yP)).to((xr, yP)).color(ORG).linewidth(1.8)
        lab(d, (-4.2, yP), "+5 V 轨\n（上方最外侧）", ha="right", fs_=10.5, color=ORG)
        d += elm.Line().at((-4.0, yG)).to((xr, yG))
        lab(d, (-4.2, yG), "0 V 轨\n（上下两条由\ntn3 → bp3 连通）", ha="right", fs_=10.5)
        # R1、K1、A 点
        xA = -1.0
        d += elm.Resistor().endpoints((xA, yP), (xA, 2.0))
        d += elm.Dot().at((xA, yP))
        lab(d, (xA - 1.0, 4.4), "R1 10 kΩ\n5 V 轨第 8 列\n→ a9", ha="right", fs_=9.5)
        d += elm.Arrow().at((xA + 0.45, 5.6)).to((xA + 0.45, 4.4)).color(C["cur"]).linewidth(1.2)
        lab(d, (xA + 0.6, 5.1), "按住时 0.5 mA", fs_=8.5, color=C["cur"])
        xk = -2.5
        d += elm.Line().at((xA, 2.0)).to((xk, 2.0))
        d += PushNO().endpoints((xk, 2.0), (xk, yG))
        d += elm.Dot().at((xk, yG))
        lab(d, (xk - 0.55, -0.5), "K1\nc7、c9\n（黑线 a7\n→ 0 V 轨）", ha="right", fs_=9.5)
        d += elm.Line().at((xA, 2.0)).to((0.0, 2.0))
        d += elm.Dot().at((xA, 2.0)); d += elm.Dot().at((0.0, 2.0))
        ring(d, (xA, 2.0), "A（d9）", dx=0.0, dy=-0.9, ha="center")
        # R2、C1、B 点
        xB = 3.5
        d += elm.Resistor().endpoints((0.0, 2.0), (3.0, 2.0))
        lab(d, (1.5, 2.6), "R2 10 kΩ g9–g13", ha="center", fs_=9.5)
        d += elm.Line().at((3.0, 2.0)).to((xB, 2.0))
        d += elm.Capacitor(polar=True).endpoints((xB, 2.0), (xB, yG))
        d += elm.Dot().at((xB, 2.0)); d += elm.Dot().at((xB, yG))
        lab(d, (xB - 0.45, -0.75), "C1 100 μF\n（第 8 步换 470 μF）\n长脚 + j13 · 短脚 0 V 轨", ha="right", fs_=9)
        ring(d, (xB, 2.0), "B（h13）", dx=0.0, dy=0.9, ha="center")
        # U1：两个施密特反相器
        _dbox(d, 4.6, 1.2, 8.0, 5.0)
        lab(d, (5.9, 5.3), "U1 74HC14", ha="center", fs_=9.5)
        d += elm.Line().at((xB, 2.0)).to((5.0, 2.0)).color(GRN).linewidth(1.8)
        d += _lg.SchmittNot().at((5.0, 2.0)).right()
        d += elm.Line().at((0.0, 2.0)).to((0.0, 4.0)).color(GRN).linewidth(1.8)
        d += elm.Line().at((0.0, 4.0)).to((5.0, 4.0)).color(GRN).linewidth(1.8)
        lab(d, (0.2, 4.25), "绿线 i9 → i15（A 点直接进 3 脚，不经 RC）", fs_=8.5, color=GRN)
        d += _lg.SchmittNot().at((5.0, 4.0)).right()
        for x, y, t in ((5.25, 2.25, "1"), (7.25, 2.25, "2"), (5.25, 4.25, "3"), (7.25, 4.25, "4")):
            lab(d, (x, y), t, ha="center", fs_=8.5, color=GRAY)
        x14, x7, xu = 7.6, 5.2, 7.0
        d += elm.Line().at((x14, 5.0)).to((x14, yP)).color(ORG).linewidth(1.8)
        d += elm.Dot().at((x14, yP))
        lab(d, (x14 + 0.15, 5.5), "14 脚 VCC（e13，橙线 a13）", fs_=8.5, color=ORG)
        d += elm.Line().at((x7, 1.2)).to((x7, yG)).linewidth(1.8)
        d += elm.Dot().at((x7, yG))
        lab(d, (x7 + 0.12, -1.6), "7 脚 GND\n（黑线 j19）", fs_=8.5)
        d += elm.Line().at((xu, 1.2)).to((xu, yG)).linewidth(1.8)
        d += elm.Dot().at((xu, yG))
        lab(d, (xu + 0.12, -0.3), "5、9、11、13 脚\n（不用的输入）\n接 0 V；6、8、\n10、12 脚空着", fs_=8.5)
        # 两路输出：Y1（去抖后）、Y2（没去抖）
        xY, xL1, xL2 = 8.5, 11.5, 14.5
        d += elm.Line().at((7.5, 2.0)).to((xY, 2.0)).color(GRN).linewidth(1.8)
        d += elm.Line().at((xY, 2.0)).to((9.0, 2.0)).color(GRN).linewidth(1.8)
        d += elm.Resistor().endpoints((9.0, 2.0), (xL1, 2.0))
        lab(d, ((9.0 + xL1) / 2, 2.6), "R3 1 kΩ g21–g25", ha="center", fs_=9)
        d += elm.LED().endpoints((xL1, 2.0), (xL1, yG))
        d += elm.Dot().at((xL1, yG))
        lab(d, (xL1 + 0.95, -0.6), "LED1\n长脚 j25\n（去抖后）", fs_=9)
        d += elm.Arrow().at((9.3, 1.55)).to((11.1, 1.55)).color(C["cur"]).linewidth(1.2)
        lab(d, (10.2, 1.2), "约 3.1 mA", ha="center", fs_=8.5, color=C["cur"])
        d += elm.Line().at((7.5, 4.0)).to((9.5, 4.0)).color(GRN).linewidth(1.8)
        d += elm.Resistor().endpoints((9.5, 4.0), (12.0, 4.0))
        lab(d, (10.75, 4.6), "R4 1 kΩ h27–h29", ha="center", fs_=9)
        d += elm.Line().at((12.0, 4.0)).to((xL2, 4.0))
        d += elm.LED().endpoints((xL2, 4.0), (xL2, yG))
        d += elm.Dot().at((xL2, yG))
        lab(d, (xL2 + 0.95, 0.6), "LED2\n长脚 j29\n（没去抖）", fs_=9)
        d += elm.Dot().at((xY, 2.0)); d += elm.Dot().at((xY, 4.0))
        ring(d, (xY, 2.0), "Y1（j14）", dx=0.0, dy=-0.95, ha="center")
        ring(d, (xY, 4.0), "Y2（j16）", dx=0.0, dy=-0.85, ha="center")
        d += elm.Capacitor().endpoints((xr - 0.5, yP), (xr - 0.5, yG))
        d += elm.Dot().at((xr - 0.5, yP)); d += elm.Dot().at((xr - 0.5, yG))
        lab(d, (xr, 1.5), "C0 100 nF\nb13 → 上方\n0 V 轨\n（贴着 14 脚）", fs_=9)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 红表笔的位置（与面包板图同名，黑表笔都在 0 V 轨）；灰色小数字 = 74HC14 引脚号。",
            "U1 缺口朝左，1 脚在 f13、14 脚在 e13。A 点 = 第 9 列（e9–f9 绿短线把上下两半连成一列）；B 点 = 第 13 列下半 = 1 脚；Y1 = 2 脚（第 14 列下半），Y2 = 4 脚（第 16 列下半）。",
            "导线颜色与面包板图一致：橙 = +5 V 线，黑 = 0 V 地线，绿 = 信号线。天蓝色箭头 = 电流方向。",
        )
        for k, line in enumerate(notes):
            note(d, (-7.0, -4.4 - 0.6 * k), line)
    print("[图 29-p4-3] R1 tp8–a9；K1 c7–c9、a7→0 V；A=第 9 列；R2 g9–g13；C1 j13(+)–0 V；1 脚 f13=B；i9→i15 到 3 脚；"
          "2 脚→h14→h21→R3→LED1 j25；4 脚→i16→i27→R4→LED2 j29；14 脚 a13→5 V，7 脚 j19→0 V，5/9/11/13 脚接地")
    save_schem(d, "29", "29_p4_3_schem_lab.png")

    # ================= 图 29-p4-4：BSS138 电平转换（对应 29-p4-2） =================
    yP, yG = 6.0, -3.0
    with drawing(fontsize=11) as d:
        title(d, (5.0, 7.6), "BSS138 双向电平转换：栅极接 3.3 V，源极接 L 线（3.3 V 侧），漏极接 H 线（5 V 侧）")
        xD, yF = 6.5, 1.5
        d += (q := elm.NFet().theta(-90).reverse().at((xD, yF)))
        S, D_, G = q.absanchors["source"], q.absanchors["drain"], q.absanchors["gate"]
        lab(d, (S[0] - 0.1, S[1] - 0.45), "S · 2 脚\ne14", ha="center", fs_=9, color=GRAY)
        lab(d, (D_[0] + 0.1, D_[1] - 0.45), "D · 3 脚\ne15", ha="center", fs_=9, color=GRAY)
        lab(d, (G[0] + 0.15, G[1] + 0.05), "G · 1 脚 · e13", fs_=9, color=GRAY)
        lab(d, ((S[0] + D_[0]) / 2, yF - 1.25), "Q1 BSS138", ha="center", fs_=10)
        xg = G[0]
        d += elm.Line().at((-4.0, yP)).to((xg, yP)).color(BLU).linewidth(1.8)
        lab(d, (-4.2, yP), "+3.3 V 轨\n（上方最外侧）", ha="right", fs_=10.5, color=BLU)
        d += elm.Line().at(G).to((xg, yP)).color(BLU).linewidth(1.8)
        d += elm.Dot().at((xg, yP))
        lab(d, (xg + 0.15, 4.9), "蓝线 a13 → 3.3 V 轨", fs_=8.5, color=BLU)
        d += elm.Dot().at((xg, 3.9))
        ring(d, (xg, 3.9), "G（b13）", dx=-0.9, dy=0.0)
        xH, xr = 10.5, 14.0
        d += elm.Line().at((8.5, yP)).to((xr, yP)).color(ORG).linewidth(1.8)
        lab(d, (xr + 0.2, yP), "+5 V 轨\n（下方最外侧）", fs_=10.5, color=ORG)
        d += elm.Line().at((-4.0, yG)).to((xr, yG))
        lab(d, (-4.2, yG), "0 V 轨\n（两条由 tn28 →\nbp28 连通）", ha="right", fs_=10.5)
        # 3.3 V 侧
        xL = 1.0
        d += elm.Resistor().endpoints((xL, yP), (xL, yF))
        d += elm.Dot().at((xL, yP))
        lab(d, (xL - 0.55, 4.0), "RPL 10 kΩ\nb2–b6\n（第 2 列经\n蓝线 a2 接\n3.3 V 轨）", ha="right", fs_=9)
        d += elm.Line().at((xL, yF)).to(S).color(GRN).linewidth(1.8)
        lab(d, (xL + 0.2, yF + 0.25), "绿线 d6 → d14", fs_=8.5, color=GRN)
        d += elm.Dot().at((xL, yF))
        ring(d, (xL, yF), "L（e6）", dx=-0.9, dy=0.0)
        d += elm.Line().at((xL, yF)).to((xL, 0.5)).color(GRN).linewidth(1.8)
        d += elm.Switch().endpoints((xL, 0.5), (xL, -1.8)).color(GRN)
        d += elm.Line().at((xL, -1.8)).to((xL, yG)).linewidth(1.8)
        d += elm.Dot().at((xL, yG))
        lab(d, (xL + 0.45, -0.7), "L 拉低线 a6\n平时悬空，要拉低时\n插 0 V 轨", fs_=8.5)
        # 5 V 侧
        d += elm.Resistor().endpoints((xH, yP), (xH, yF))
        d += elm.Dot().at((xH, yP))
        lab(d, (xH + 0.55, 4.0), "RPH 10 kΩ\nh19–h23\n（第 23 列经\n橙线 j23 接\n5 V 轨）", fs_=9)
        d += elm.Arrow().at((xH - 0.45, 5.0)).to((xH - 0.45, 2.6)).color(C["cur"]).linewidth(1.2)
        lab(d, (xH - 0.8, 3.4), "L 拉低时\n约 0.5 mA", ha="right", fs_=8.5, color=C["cur"])
        d += elm.Line().at(D_).to((xH, yF)).color(GRN).linewidth(1.8)
        lab(d, (D_[0] + 0.35, yF + 0.25), "绿线 c15 → g19", fs_=8.5, color=GRN)
        d += elm.Dot().at((xH, yF))
        ring(d, (xH, yF), "H（i19）", dx=0.9, dy=0.0)
        d += elm.Line().at((xH, yF)).to((xH, 0.5)).color(GRN).linewidth(1.8)
        d += elm.Switch().endpoints((xH, 0.5), (xH, -1.8)).color(GRN)
        d += elm.Line().at((xH, -1.8)).to((xH, yG)).linewidth(1.8)
        d += elm.Dot().at((xH, yG))
        lab(d, (xH + 0.45, -0.7), "H 拉低线 j19\n平时悬空，要拉低时\n插 0 V 轨", fs_=8.5)
        notes = (
            "读图：一条线 = 一个节点；实心圆点 = 导线相连；紫色圆圈 = 红表笔的位置（与面包板图同名）；灰色小字 = BSS138 转接板的引脚号和孔位。",
            "L 线 = 第 6 列上半；H 线 = 第 19 列下半；3.3 V 轨和 5 V 轨互不相连，两侧只经过 Q1 联系，0 V 是共用的。",
            "第三部分（接反）：d14 那头改插 d15、c15 那头改插 c14，L 线接到 D、H 线接到 S，栅极仍接 3.3 V。",
            "导线颜色与面包板图一致：蓝 = +3.3 V 线，橙 = +5 V 线，黑 = 0 V 地线，绿 = 信号线。天蓝色箭头 = 电流方向。",
        )
        for k, line in enumerate(notes):
            note(d, (-7.0, -4.4 - 0.6 * k), line)
    print("[图 29-p4-4] G e13←a13←3.3 V；S e14←d14←d6=L；D e15→c15→g19=H；RPL b2–b6（a2→3.3 V）；RPH h19–h23（j23→5 V）；拉低线 a6、j19")
    save_schem(d, "29", "29_p4_4_schem_lab.png")


def node_30():
    """30 的 page4 原理图（30_p4_2_schem_vground、30_p4_4_schem_lab、30_p4_6_ref_divider）画在 code/figs/30_figs.py 里
    （它只借用本文件的 lab / probe / colnote 等小工具），这里登记一个转调入口，保持「lab_schem.py NN」可重画。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("figs30", os.path.join(os.path.dirname(os.path.abspath(__file__)), "30_figs.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    for f in ("p4_2", "p4_4", "p4_6"):
        getattr(m, f)()


def _part2_node(nn, funcs):
    """第二部分节点的 page4 原理图画在各自的 code/figs/NN_figs.py 里，这里只登记转调入口，保持「lab_schem.py NN」可重画。"""
    def run():
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"figs{nn}", os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{nn}_figs.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        for f in funcs:
            getattr(m, f)()
    run.__name__ = f"node_{nn}"
    return run


node_35 = _part2_node("35", ("p4_2_schem_lab", "p4_3_ac_inject"))
node_40 = _part2_node("40", ("p4_2_schem_lab", "p4_4_schem_lab"))
node_41 = _part2_node("41", ("p4_2_schem_lab",))


# ---------------- 登记表：键 = 节点编号（与 save_schem 的 prefix 相同） ----------------
NODES = {
    "01": node_01,
    "03": node_03,
    "02": node_02,
    "05": node_05,
    "08": node_08,
    "12": node_12,
    "16": node_16,
    "09": node_09,
    "13": node_13,
    "19": node_19,
    "21": node_21,
    "25": node_25,
    "17": node_17,
    "22": node_22,
    "14": node_14,
    "18": node_18,
    "10": node_10,
    "20": node_20,
    "24": node_24,
    "04": node_04,
    "11": node_11,
    "15": node_15,
    "27": node_27,
    "06": node_06,
    "07": node_07,
    "23": node_23,
    "28": node_28,
    "26": node_26,
    "29": node_29,
    "30": node_30,   # 第二部分：转调 code/figs/30_figs.py
    "35": node_35,   # 转调 code/figs/35_figs.py
    "40": node_40,   # 转调 code/figs/40_figs.py
    "41": node_41,   # 转调 code/figs/41_figs.py
}


if __name__ == "__main__":
    keys = sys.argv[1:] or list(NODES)
    bad = [k for k in keys if k not in NODES]
    if bad:
        sys.exit(f"未登记的节点：{' '.join(bad)}；已登记：{' '.join(NODES)}")
    for k in keys:
        NODES[k]()
