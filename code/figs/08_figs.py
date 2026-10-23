"""08 线性稳压：电路图（schemdraw）。运行：/workspace/circuits-venv/bin/python code/figs/08_figs.py
图上的数字与 code/08_sim.py 的打印一致（V_ref 5.16 V、V_o 9.11 V、运放输出 9.86 V），本脚本也会打印它们。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem
from schem import elm

P = "08"
VREF, RF, R1 = 5.162, 3900.0, 5100.0
VO = VREF * (1 + RF / R1)
VB = VO + 0.755


def regulator(d, detail):
    """画出「基准 + 误差放大 + 调整管」三块。detail=True 时标元件值和电压。"""
    top = 6.0
    d += elm.Dot(open=True).at((0, top)).label("$V_i$\n14 V（带纹波）" if detail else "$V_i$\n整流滤波后", "left")
        # 基准：R_Z + 稳压管
    d += elm.Dot().at((1.5, top))
    d += elm.Resistor().endpoints((1.5, top), (1.5, 3.0)).label("$R_Z$\n1 kΩ" if detail else "$R_Z$", "bottom")
    d += elm.Dot().at((1.5, 3.0))
    d += elm.Zener().endpoints((1.5, 0), (1.5, 3.0)).label("1N4733A\n5.1 V" if detail else "稳压管", "bottom")
    # 误差放大器
    op = elm.Opamp(leads=True).right().anchor("in2").at((3.2, 3.0))
    d += op
    d += elm.Line().endpoints((1.5, 3.0), op.in2)
    d += elm.Label().at((1.3, 3.0)).label(f"$V_{{ref}}$\n{VREF:.2f} V" if detail else "$V_{ref}$", loc="left")
    # 调整管
    q = elm.BjtNpn().theta(0).anchor("base").at((op.out[0] + 1.2, op.out[1]))
    d += q
    d += elm.Line().endpoints(op.out, q.base)
    if detail:
        d += elm.Label().at((op.out[0] + 0.55, op.out[1] + 0.35)).label(f"{VB:.2f} V", loc="center")
    cx = q.collector[0]
    d += elm.Line().endpoints((0, top), (cx, top))
    d += elm.Line().endpoints(q.collector, (cx, top))
    d += elm.Label().at((cx + 1.3, q.center[1] + 0.2)).label("调整管\nTIP31" if detail else "射极跟随器", loc="center")
    qx = q.emitter[0]
    ex = qx + 2.7          # 让 R_f 在发射极右边 1.2 处
    d += elm.Line().endpoints(q.emitter, (q.emitter[0], 1.9))
    d += elm.Line().endpoints((qx, 1.9), (ex + 2.0, 1.9))
    # 分压反馈：R_f、R_1
    d += elm.Dot().at((ex - 1.5, 1.9))
    d += elm.Resistor().endpoints((ex - 1.5, 1.9), (ex - 1.5, -0.3)).label("$R_f$ 3.9 kΩ" if detail else "$R_f$", "bottom")
    d += elm.Dot().at((ex - 1.5, -0.3))
    d += elm.Resistor().endpoints((ex - 1.5, -0.3), (ex - 1.5, -2.5)).label("$R_1$ 5.1 kΩ" if detail else "$R_1$", "bottom")
    # 反馈线回到运放反相端
    d += elm.Line().endpoints(op.in1, (op.in1[0] - 0.4, op.in1[1]))
    d += elm.Line().endpoints((op.in1[0] - 0.4, op.in1[1]), (op.in1[0] - 0.4, -0.3))
    d += elm.Line().endpoints((op.in1[0] - 0.4, -0.3), (ex - 1.5, -0.3))
    d += elm.Label().at((op.in1[0] - 0.2, -0.65)).label("反馈：把输出的一部分送回反相端", loc="right")
    if detail:
        d += elm.Capacitor().endpoints((ex + 0.4, 1.9), (ex + 0.4, -2.5)).label("$C_o$\n10 µF", "bottom")
        d += elm.Dot().at((ex + 0.4, 1.9))
        d += elm.Dot().at((ex + 0.4, -2.5))
        d += elm.Resistor().endpoints((ex + 2.0, 1.9), (ex + 2.0, -2.5)).label("负载\n0.5 A", "bottom")
    else:
        d += elm.Resistor().endpoints((ex + 2.0, 1.9), (ex + 2.0, -2.5)).label("负载", "bottom")
    d += elm.Line().endpoints((ex + 2.0, 1.9), (ex + 3.2, 1.9))
    d += elm.Dot(open=True).at((ex + 3.2, 1.9)).label(f"$V_o$\n{VO:.2f} V" if detail else "$V_o$\n稳定", "right")
    d += elm.Line().endpoints((1.5, 0), (1.5, -2.5))
    d += elm.Line().endpoints((1.5, -2.5), (ex + 3.2, -2.5))
    d += elm.Dot(open=True).at((ex + 3.2, -2.5)).label("0 V", "right")
    d += elm.Dot().at((ex - 1.5, -2.5))
    d += elm.Dot().at((ex + 2.0, -2.5))


def p1_1():
    with schem.drawing(fontsize=11) as d:
        regulator(d, detail=False)
        d += elm.Label().at((1.5, 6.6)).label("① 基准", loc="center")
        d += elm.Label().at((4.6, 4.9)).label("② 误差放大", loc="center")
        d += elm.Label().at((6.2, 6.6)).label("③ 调整管", loc="center")
    schem.save_schem(d, P, "08_p1_1_blocks.png")


def p2_1():
    with schem.drawing(fontsize=11) as d:
        regulator(d, detail=True)
        d += elm.Label().at((4.6, 4.9)).label("LM358（由 $V_i$ 供电）", loc="center")
    print(f"[图 08-p2-1] V_ref {VREF:.2f} V、运放输出 {VB:.2f} V、V_o {VO:.2f} V、R_Z 1 kΩ、R_f 3.9 kΩ、R_1 5.1 kΩ、C_o 10 µF、0.5 A")
    assert abs(VO - 9.11) < 0.005
    schem.save_schem(d, P, "08_p2_1_detail.png")


def p2_3():
    """变体：7805 三端稳压器的典型接法（TI uA78xx 手册的测试电路电容值）。"""
    with schem.drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, 3)).label("$V_i$\n7–25 V", "left")
        d += elm.Line().endpoints((0, 3), (3, 3))
        d += elm.Dot().at((1.5, 3))
        d += elm.Capacitor().endpoints((1.5, 3), (1.5, 0)).label("$C_i$\n0.33 µF", "bottom")
        for a, b in (((3, 2.2), (5.5, 2.2)), ((5.5, 2.2), (5.5, 3.8)), ((5.5, 3.8), (3, 3.8)), ((3, 3.8), (3, 2.2))):
            d += elm.Line().endpoints(a, b)
        d += elm.Label().at((4.25, 3.35)).label("7805", loc="center")
        d += elm.Label().at((3.15, 2.75)).label("IN", loc="right")
        d += elm.Label().at((5.35, 2.75)).label("OUT", loc="left")
        d += elm.Label().at((4.25, 2.45)).label("GND", loc="center")
        d += elm.Line().endpoints((5.5, 3), (8, 3))
        d += elm.Dot().at((6.5, 3))
        d += elm.Capacitor().endpoints((6.5, 3), (6.5, 0)).label("$C_o$\n0.1 µF", "bottom")
        d += elm.Dot(open=True).at((8, 3)).label("$V_o$\n5 V", "right")
        d += elm.Line().endpoints((4.25, 2.2), (4.25, 0))
        d += elm.Line().endpoints((0, 0), (8, 0))
        d += elm.Dot().at((1.5, 0)); d += elm.Dot().at((4.25, 0)); d += elm.Dot().at((6.5, 0))
        d += elm.Dot(open=True).at((0, 0)).label("0 V", "left")
        d += elm.Dot(open=True).at((8, 0)).label("0 V", "right")
        d += elm.Label().at((4.0, -0.8)).label("两只电容都要贴着芯片引脚焊", loc="center")
    print("[图 08-p2-3] 7805：V_i 7–25 V、C_i 0.33 µF、C_o 0.1 µF、V_o 5 V")
    schem.save_schem(d, P, "08_p2_3_7805.png")


if __name__ == "__main__":
    p1_1(); p2_1(); p2_3()
    print("08_figs OK")
