"""电池符号的「+ / −」小字标注（长线 = 正极，短线 = 负极）。

schemdraw 0.23 的 elm.Battery() 从起点画到终点时，长线（+）在起点一端；竖着画、要 + 朝上时
写 endpoints(下, 上).reverse()。本函数在电池放好以后，直接读它变换后的极板几何：
最外侧那根长线 = +，最外侧那根短线 = −，在两根极板外侧各写一个小「+」「−」，
所以无论 .reverse() 写没写，标出来的正负号都和画出来的长短线一致；再用 plus_toward 断言 + 朝向哪个节点。

用法：
    d += (b := elm.Battery().endpoints((x, y0), (x, y1)).reverse())
    pm(d, b, plus_toward=(x, y1))          # + 应朝 (x, y1)；画反了就报错
"""
import math
import schemdraw.elements as elm

PM_COLOR = "#c0392b"


def _plates(e):
    """返回 [(中心点绝对坐标, 本地长度)]，按本地 x 排序（只取竖直的极板线段）。"""
    out = []
    for s in e.segments:
        p = getattr(s, "path", None)
        if not p or len(p) != 2:
            continue
        (x0, y0), (x1, y1) = p
        if any(map(math.isnan, (x0, y0, x1, y1))) or abs(x0 - x1) > 1e-9:
            continue
        c = e.transform.transform(((x0 + x1) / 2, (y0 + y1) / 2))
        out.append((x0, (c[0], c[1]), abs(y1 - y0)))
    out.sort()
    return out


def polarity(e):
    """返回 (+ 极板中心, − 极板中心) 的绝对坐标。"""
    pl = _plates(e)
    a, b = pl[0], pl[-1]
    plus, minus = (a, b) if a[2] > b[2] else (b, a)
    return plus[1], minus[1]


def pm(d, e, plus_toward=None, side=1, off=0.45, fs=13, color=PM_COLOR):
    """在电池 e 的两极板外侧写「+」「−」。side = +1 / −1 选写在电池轴线的哪一边；
    plus_toward：+ 应更靠近的点（如 R1、VCC 那端），给了就检查。"""
    P, M = polarity(e)
    ux, uy = P[0] - M[0], P[1] - M[1]
    L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
    nx, ny = -uy * side, ux * side
    if plus_toward is not None:
        dp = math.hypot(P[0] - plus_toward[0], P[1] - plus_toward[1])
        dm = math.hypot(M[0] - plus_toward[0], M[1] - plus_toward[1])
        assert dp < dm, f"电池画反了：+ 极板 {P} 比 − 极板 {M} 离 {plus_toward} 更远"
    k = 0.12
    d += elm.Label().at((P[0] + ux * k + nx * off, P[1] + uy * k + ny * off)).label("+", fontsize=fs, color=color, halign="center", valign="center")
    d += elm.Label().at((M[0] - ux * k + nx * off, M[1] - uy * k + ny * off)).label("−", fontsize=fs, color=color, halign="center", valign="center")
    return P, M
