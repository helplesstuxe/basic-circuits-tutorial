"""10 稳压管稳压：电路图（schemdraw）。运行：/workspace/circuits-venv/bin/python code/figs/10_figs.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem
from schem import elm

P = "10"


def p1_1():
    """并联稳压：限流电阻 R + 稳压管 + 负载，标出 I_R = I_Z + I_L。"""
    with schem.drawing(fontsize=11) as d:
        d += elm.SourceV().endpoints((0, 0), (0, 3)).label("$V_i$\n10–14 V\n（06 的输出）", loc="bottom")
        r = elm.Resistor().endpoints((0, 3), (3.5, 3)).label("R  180 Ω", loc="top")
        d += r
        d += elm.CurrentLabelInline(direction="in").at(r).label("$I_R$", loc="bottom")
        d += elm.Dot().at((3.5, 3))
        z = elm.Zener().endpoints((3.5, 0), (3.5, 3)).label("1N4733A\n$V_Z$ = 5.1 V", loc="bottom")
        d += z
        d += elm.Line().endpoints((3.5, 3), (6.5, 3))
        d += elm.Dot().at((6.5, 3))
        d += elm.Resistor().endpoints((6.5, 3), (6.5, 0)).label("$R_L$\n负载", loc="bottom")
        d += elm.Line().endpoints((6.5, 3), (8.5, 3))
        d += elm.Dot(open=True).at((8.5, 3)).label("$V_o$ ≈ 5 V", loc="right")
        d += elm.Line().endpoints((0, 0), (8.5, 0))
        d += elm.Dot().at((3.5, 0))
        d += elm.Dot().at((6.5, 0))
        d += elm.Dot(open=True).at((8.5, 0)).label("0 V", loc="right")
        d += elm.Label().at((2.6, 1.5)).label("↓$I_Z$", loc="center")
        d += elm.Label().at((5.7, 1.5)).label("↓$I_L$", loc="center")
        d += elm.Label().at((4.2, -0.9)).label("$I_R$ = $I_Z$ + $I_L$：负载少拿多少，稳压管就多吃多少")
    schem.save_schem(d, P, "10_p1_1_shunt.png")


def p2_2():
    """变体：稳压管给三极管基极定电压，发射极输出 V_Z − 0.7 V。"""
    with schem.drawing(fontsize=11) as d:
        d += elm.SourceV().endpoints((0, 0), (0, 4.5)).label("$V_i$\n10–14 V", loc="bottom")
        d += elm.Resistor().endpoints((2.5, 4.5), (2.5, 2)).label("R\n180 Ω", loc="bottom")
        d += elm.Dot().at((2.5, 2))
        d += elm.Zener().endpoints((2.5, 0), (2.5, 2)).label("$V_Z$\n5.1 V", loc="bottom")
        q = elm.BjtNpn().theta(0).anchor("base").at((5.5, 2))
        d += q
        d += elm.Line().endpoints((2.5, 2), q.base)
        d += elm.Label().at((4.0, 2.4)).label("$I_B$ = $I_L$/(β+1)", loc="center")
        cx = q.collector[0]
        d += elm.Line().endpoints((0, 4.5), (cx, 4.5))
        d += elm.Dot().at((2.5, 4.5))
        d += elm.Line().endpoints(q.collector, (cx, 4.5))
        ex = q.emitter[0]
        d += elm.Line().endpoints(q.emitter, (ex, 1.0))
        d += elm.Line().endpoints((ex, 1.0), (8, 1.0))
        d += elm.Dot().at((8, 1.0))
        d += elm.Resistor().endpoints((8, 1.0), (8, 0)).label("$R_L$", loc="bottom")
        d += elm.Line().endpoints((8, 1.0), (9.5, 1.0))
        d += elm.Dot(open=True).at((9.5, 1.0)).label("$V_o$ ≈ $V_Z$ − 0.7 V", loc="right")
        d += elm.Line().endpoints((0, 0), (9.5, 0))
        d += elm.Dot().at((2.5, 0))
        d += elm.Dot().at((8, 0))
        d += elm.Dot(open=True).at((9.5, 0)).label("0 V", loc="right")
        d += elm.Label().at((cx + 1.9, 3.4)).label("NPN 三极管\n（大电流走 C→E）", loc="center")
    schem.save_schem(d, P, "10_p2_2_follower_schem.png")


if __name__ == "__main__":
    p1_1()
    p2_2()
    print("10_figs OK")
