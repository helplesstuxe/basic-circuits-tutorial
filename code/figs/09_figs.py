"""09 开关电源：电路图（schemdraw）。运行：/workspace/circuits-venv/bin/python code/figs/09_figs.py
图上的数字与 code/09_sim.py 一致（12 V → 5 V、1 A、200 kHz、47 µH、47 µF、占空比约 44%），本脚本也会打印它们。
全部是低压直流电路；变体二（反激副边）的初级接市电，图上只画成方框并写明危险。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schem
from schem import elm

P = "09"
VIN, VO, IO, FSW, L_uH, C_uF = 12.0, 5.0, 1.0, 200e3, 47, 47
D = (VO + IO * 0.05 + 0.4) / (VIN - IO * 0.05 + 0.4)
print(f"[数值] V_in {VIN:.0f} V，V_o {VO:.0f} V，I_o {IO:.0f} A，f {FSW/1e3:.0f} kHz，L {L_uH} µH，C {C_uF} µF，D ≈ {D*100:.0f}%")
assert 0.43 < D < 0.45


def output_stage(d, x, top, detail, lab_c="$C_o$", lab_r="负载"):
    """从 (x, top) 开始画电感右边的输出电容、负载和输出端子；返回地线右端 x。"""
    d += elm.Dot().at((x, top))
    d += elm.Capacitor().endpoints((x, top), (x, 0)).label(f"{lab_c}\n{C_uF} µF" if detail else lab_c, "bottom")
    d += elm.Dot().at((x, 0))
    d += elm.Line().endpoints((x, top), (x + 3.0, top))
    d += elm.Resistor().endpoints((x + 3.0, top), (x + 3.0, 0)).label(f"{lab_r}\n5 Ω（1 A）" if detail else lab_r, "bottom")
    d += elm.Dot().at((x + 3.0, top))
    d += elm.Line().endpoints((x + 3.0, top), (x + 4.2, top))
    d += elm.Dot(open=True).at((x + 4.2, top)).label(f"$V_o$\n{VO:.0f} V" if detail else "$V_o$\n平稳的直流", "right")
    d += elm.Line().endpoints((x + 3.0, 0), (x + 4.2, 0))
    d += elm.Dot(open=True).at((x + 4.2, 0)).label("0 V", "right")
    return x + 4.2


def p1_1():
    """直觉版：开关 + 续流二极管 + 电感 + 电容。"""
    top = 4.0
    with schem.drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((0, top)).label("$V_{in}$\n12 V", "left")
        sw = elm.Switch().endpoints((0, top), (3.0, top)).label("开关：每秒通断 20 万次", "top")
        d += sw
        d += elm.Dot().at((3.0, top))
        d += elm.Schottky().endpoints((3.0, 0), (3.0, top)).label("续流二极管\n开关断开时\n给电流让路", "bottom")
        d += elm.Inductor2().endpoints((3.0, top), (6.0, top)).label("电感：保持电流", "top")
        output_stage(d, 6.0, top, False, lab_c="电容：攒住电压")
        d += elm.Line().endpoints((0, 0), (6.0, 0))
        d += elm.Dot(open=True).at((0, 0)).label("0 V", "left")
        d += elm.Dot().at((3.0, 0))
    schem.save_schem(d, P, "09_p1_1_concept.png")


def high_side(d, x0, top, label):
    """上管 N 沟道 MOSFET：漏极在左（接输入）、源极在右（接开关节点）。返回 (MOSFET, 源极 x)。"""
    q = elm.NFet().theta(90).reverse().anchor("drain").at((x0, top))
    d += q
    d += elm.Label().at((x0 + 0.75, top + 0.75)).label(label, loc="center")
    return q, x0 + 1.5


def p2_1():
    """异步降压：上管 MOSFET + 肖特基续流 + L + C，带元件值与反馈。"""
    top = 4.0
    with schem.drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((-1.2, top)).label(f"$V_{{in}}$\n{VIN:.0f} V", "left")
        d += elm.Line().endpoints((-1.2, top), (0.6, top))
        d += elm.Dot().at((0, top))
        d += elm.Capacitor().endpoints((0, top), (0, 0)).label("$C_{in}$\n10 µF", "top")
        q, sx = high_side(d, 0.6, top, "上管 MOSFET")
        nx = sx + 1.0
        d += elm.Line().endpoints((sx, top), (nx, top))
        d += elm.Dot().at((nx, top))
        d += elm.Label().at((nx + 0.3, top - 0.45)).label("开关节点", loc="center")
        d += elm.Schottky().endpoints((nx, 0), (nx, top)).label("肖特基\n二极管\n0.4 V", "bottom")
        d += elm.Inductor2().endpoints((nx, top), (nx + 3.0, top)).label(f"$L$　{L_uH} µH", "top")
        right = output_stage(d, nx + 3.0, top, True)
        d += elm.Line().endpoints((-1.2, 0), (nx + 3.0, 0))
        d += elm.Dot(open=True).at((-1.2, 0)).label("0 V", "left")
        d += elm.Dot().at((0, 0)); d += elm.Dot().at((nx, 0))
        # 控制器与反馈
        gx, gy = q.absanchors["gate"]
        bx, by = gx + 1.6, -1.6
        d += elm.Line().endpoints((gx, gy), (gx, by + 0.4))
        W = 2.9
        d += elm.Line().endpoints((bx - W, by + 0.4), (bx + W, by + 0.4))
        d += elm.Line().endpoints((bx + W, by + 0.4), (bx + W, by - 0.4))
        d += elm.Line().endpoints((bx + W, by - 0.4), (bx - W, by - 0.4))
        d += elm.Line().endpoints((bx - W, by - 0.4), (bx - W, by + 0.4))
        d += elm.Label().at((bx, by)).label(f"PWM 控制器（{FSW/1e3:.0f} kHz，D ≈ {D*100:.0f}%）", loc="center")
        d += elm.Line().endpoints((right, top), (right, by)).linestyle("--")
        d += elm.Line().endpoints((right, by), (bx + W, by)).linestyle("--")
        d += elm.Label().at(((right + bx + W) / 2, by - 0.35)).label("反馈：测输出，调占空比", loc="center")
    schem.save_schem(d, P, "09_p2_1_async.png")


def p2_4():
    """同步降压：下管 MOSFET 代替二极管。"""
    top = 4.0
    with schem.drawing(fontsize=11) as d:
        d += elm.Dot(open=True).at((-1.2, top)).label(f"$V_{{in}}$\n{VIN:.0f} V", "left")
        d += elm.Line().endpoints((-1.2, top), (0.6, top))
        d += elm.Dot().at((0, top))
        d += elm.Capacitor().endpoints((0, top), (0, 0)).label("$C_{in}$", "bottom")
        q, sx = high_side(d, 0.6, top, "上管")
        nx = sx + 1.2
        d += elm.Line().endpoints((sx, top), (nx, top))
        d += elm.Dot().at((nx, top))
        q2 = elm.NFet().theta(0).anchor("drain").at((nx, top - 1.0))
        d += elm.Line().endpoints((nx, top), (nx, top - 1.0))
        d += q2
        d += elm.Line().endpoints(q2.absanchors["source"], (nx, 0))
        g2 = q2.absanchors["gate"]
        d += elm.Label().at((g2[0] + 0.3, g2[1] + 1.0)).label("下管", loc="center")
        g1 = q.absanchors["gate"]
        d += elm.Line().endpoints(g1, (g1[0], g1[1] - 0.4))
        d += elm.Label().at((g1[0], g1[1] - 0.7)).label("驱动 A", loc="center")
        d += elm.Line().endpoints(g2, (g2[0] + 0.4, g2[1]))
        d += elm.Label().at((g2[0] + 0.9, g2[1] - 0.4)).label("驱动 B", loc="center")
        d += elm.Inductor2().endpoints((nx, top), (nx + 3.6, top)).label("$L$", "top")
        output_stage(d, nx + 3.6, top, False)
        d += elm.Line().endpoints((-1.2, 0), (nx + 3.6, 0))
        d += elm.Dot(open=True).at((-1.2, 0)).label("0 V", "left")
        d += elm.Dot().at((0, 0)); d += elm.Dot().at((nx, 0))
        d += elm.Label().at((nx + 1.5, -0.9)).label("两管轮流导通，中间留「死区」，绝不能同时导通", loc="center")
    schem.save_schem(d, P, "09_p2_4_sync.png")


def p2_5():
    """反激电源副边输出级（附图那一格的实用画法）。"""
    with schem.drawing(fontsize=11) as d:
        t = elm.Transformer(t1=4, t2=4).anchor("p1")
        d += t.at((0, 4.0))
        # 初级侧（只画成方框说明）
        d += elm.Line().endpoints(t.p1, (t.p1[0] - 0.8, t.p1[1]))
        d += elm.Line().endpoints(t.p2, (t.p2[0] - 0.8, t.p2[1]))
        bx = t.p1[0] - 2.6
        y0, y1 = t.p2[1] - 0.3, t.p1[1] + 0.3
        for a, b in (((bx - 1.8, y0), (bx + 1.8, y0)), ((bx + 1.8, y0), (bx + 1.8, y1)),
                     ((bx + 1.8, y1), (bx - 1.8, y1)), ((bx - 1.8, y1), (bx - 1.8, y0))):
            d += elm.Line().endpoints(a, b)
        d += elm.Line().endpoints((bx + 1.8, t.p1[1]), (t.p1[0] - 0.8, t.p1[1]))
        d += elm.Line().endpoints((bx + 1.8, t.p2[1]), (t.p2[0] - 0.8, t.p2[1]))
        d += elm.Label().at((bx, (y0 + y1) / 2)).label("初级（接市电！）\n整流后约 311 V 直流\n+ MOSFET 开关", loc="center")
        # 副边：串联二极管 → 电容 ∥ 稳压管
        top, bot = t.s1[1], t.s2[1]
        x = t.s1[0]
        d += elm.Diode().endpoints((x, top), (x + 2.5, top)).label("整流二极管", "top")
        d += elm.Dot().at((x + 2.5, top))
        d += elm.Capacitor().endpoints((x + 2.5, top), (x + 2.5, bot)).label("$C_o$", "bottom")
        d += elm.Line().endpoints((x + 2.5, top), (x + 4.3, top))
        d += elm.Dot().at((x + 4.3, top))
        d += elm.Zener().endpoints((x + 4.3, bot), (x + 4.3, top)).label("稳压管\n（附图画法，\n实际多为反馈）", "bottom")
        d += elm.Line().endpoints((x + 4.3, top), (x + 5.3, top))
        d += elm.Dot(open=True).at((x + 5.3, top)).label("$V_o$", "right")
        d += elm.Line().endpoints((x, bot), (x + 5.3, bot))
        d += elm.Dot(open=True).at((x + 5.3, bot)).label("0 V", "right")
        d += elm.Dot().at((x + 2.5, bot)); d += elm.Dot().at((x + 4.3, bot))
        d += elm.Label().at(((t.p1[0] + t.s1[0]) / 2, top + 1.0)).label("变压器：隔离", loc="center")
        d += elm.Label().at((x + 1.5, bot - 0.8)).label("副边：脉冲 → 二极管整流 → 电容滤波（同 06）", loc="center")
    schem.save_schem(d, P, "09_p2_5_flyback.png")


p1_1(); p2_1(); p2_4(); p2_5()
print("[完成] 09_figs.py")
