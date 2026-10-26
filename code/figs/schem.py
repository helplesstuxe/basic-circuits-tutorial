"""全教程共用的电路图（schemdraw）风格与自定义元件。

用法（code/figs/NN_figs.py 或 code/NN_*.py 里）：
    from schem import *                      # 同时导入 figstyle 的 C、save 等
    with drawing() as d:                     # 统一线宽、字号、中文字体
        d += elm.SourceSin().up().label("$V_i$")
        d += elm.Resistor().right().label("$R_1$ 10 kΩ")
        ...
    save_schem(d, "05", "05_p1_1_inverting.png")   # → 05-inverting-amp/img/，≤ 200 KB
**只由总纲（协调者）修改本文件**；需要新元件时向总纲提出。

schemdraw 自带并已验证可用（见 `python schem.py --demo`）：
    elm.Opamp(leads=True)  运放      elm.Diode / elm.Zener / elm.LED / elm.Rectifier（二极管桥）
    elm.BjtNpn / BjtPnp     三极管     elm.NFet / elm.PFet / elm.NMos（MOSFET）
    elm.Resistor / Capacitor / Inductor2 / Potentiometer / Transformer / Fuse / FuseIEC
    elm.Switch / SwitchSpdt / SwitchSpdt2（双控开关）/ Button / Relay（继电器：线圈 + 触点）
    elm.Optocoupler（光耦：LED + 光敏三极管，扩展篇 23）/ elm.Transformer（变压器，13、28）/ elm.Schottky（续流、H 桥）
    elm.SourceV / SourceSin / SourceSquare / Battery / Ground / Vdd / Vss / Dot / Line / Lamp（白炽灯）
本文件补充的国标（GB/T 4728，与 IEC 60617 一致）风格元件，用于继电-接触器控制电路（04、11、15）、过载保护（22）、双控开关（27）：
    Coil(label="KM1")             接触器 / 继电器 / 时间继电器线圈（矩形框）
    ContactNO / ContactNC         常开 / 常闭触点（主触点、辅助触点都用它，标签写 KM1 等）
    PushNO / PushNC               常开按钮（启动 SB2）/ 常闭按钮（停止 SB1），带虚线推杆
    TimerNO / TimerNC             时间继电器延时闭合常开 / 延时断开常闭触点（带「降落伞」弧）
    ThermalHeater                 热继电器发热元件 FR（主电路）
    ThermalNC                     热继电器常闭触点 FR（控制电路）
    Motor3(text="M\\n3~")          三相（或单相）电动机：圆圈内写 M 3~
    LampX                         指示灯 / 照明灯（圆圈加 ×，国标画法）
辅助函数（扩展篇 23、28 隔离电路用）：
    barrier(d, x, y0, y1)         画一条竖直灰色虚线「隔离带」，两侧的地要分别标 GND1 / GND2
    module(name, left, right)     画一个带引脚名的方框模块（隔离 DC-DC、数字隔离器、单片机等），返回 elm.Ic
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *          # noqa: F401,F403  C、save、FONT、shrink_png、ROOT …
from figstyle import FONT, DPI, ROOT, node_dir, shrink_png
import schemdraw
import schemdraw.elements as elm
from schemdraw.elements import Element2Term
from schemdraw.segments import Segment, SegmentCircle, SegmentArc, SegmentText, SegmentPoly

schemdraw.use("matplotlib")
schemdraw.config(font=FONT or "sans-serif", fontsize=12, lw=1.4, unit=2.5, inches_per_unit=0.5, margin=0.3)

GAP = (float("nan"), float("nan"))   # schemdraw 的「抬笔」记号：线段里遇到它就断开，两端自动接引线


def drawing(**kw):
    """返回统一风格的 schemdraw.Drawing（可用 with 语句）。kw 透传给 Drawing.config，如 fontsize=11。"""
    d = schemdraw.Drawing(show=False)
    if kw:
        d.config(**kw)
    return d


def save_schem(d, prefix, name):
    """把电路图保存为 PNG 到 NN-slug/img/name（dpi 150，≤ 200 KB），打印路径和大小。"""
    path = os.path.join(node_dir(prefix), name)
    d.save(path, dpi=DPI)
    kb = shrink_png(path)
    print(f"[电路图] {os.path.relpath(path, ROOT)}  {kb:.0f} KB")
    return path


# ---------------- 自定义元件（国标 / IEC 风格；元件主体在 x∈[0,1]，两端引线由 schemdraw 自动补齐） ----------------
class Coil(Element2Term):
    """线圈（接触器 KM、中间继电器 KA、时间继电器 KT）：矩形框。label 写在框旁，如 Coil().label("KM1")。"""
    def __init__(self, w=1.0, h=0.5, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), GAP, (w, 0)]))
        self.segments.append(SegmentPoly([(0, -h / 2), (w, -h / 2), (w, h / 2), (0, h / 2)], fill="bg"))


class ContactNO(Element2Term):
    """常开触点（国标画法：动触片斜着抬起，不碰右端）。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (0.85, 0.42), GAP, (1, 0)]))


class ContactNC(Element2Term):
    """常闭触点（动触片越过右端，右端有一根竖直的「挡头」）。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (1.12, 0.42), GAP, (1, 0)]))
        self.segments.append(Segment([(1, 0), (1, 0.5)]))


def _pushrod(seg_list, x, y0, top=0.95):
    """按钮推杆：从动触片中点 (x, y0) 引一条虚线到上方，顶端画一个「E」形按钮头的横杠。"""
    seg_list.append(Segment([(x, y0), (x, top)], ls="--"))
    seg_list.append(Segment([(x - 0.18, top - 0.1), (x - 0.18, top), (x + 0.18, top), (x + 0.18, top - 0.1)]))


class PushNO(Element2Term):
    """常开按钮（如启动按钮 SB2）：常开触点 + 虚线推杆。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (0.85, 0.42), GAP, (1, 0)]))
        _pushrod(self.segments, 0.45, 0.22)


class PushNC(Element2Term):
    """常闭按钮（如停止按钮 SB1）：常闭触点 + 虚线推杆。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (1.12, 0.42), GAP, (1, 0)]))
        self.segments.append(Segment([(1, 0), (1, 0.5)]))
        _pushrod(self.segments, 0.5, 0.19)


class TimerNO(Element2Term):
    """时间继电器「通电延时闭合」常开触点：常开触点 + 动触片上的半圆弧（降落伞，表示延时）。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (0.85, 0.42), GAP, (1, 0)]))
        self.segments.append(Segment([(0.45, 0.22), (0.45, 0.62)]))
        self.segments.append(SegmentArc((0.45, 0.78), width=0.5, height=0.32, theta1=180, theta2=360))


class TimerNC(Element2Term):
    """时间继电器「通电延时断开」常闭触点：常闭触点 + 半圆弧。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (1.12, 0.42), GAP, (1, 0)]))
        self.segments.append(Segment([(1, 0), (1, 0.5)]))
        self.segments.append(Segment([(0.5, 0.19), (0.5, 0.62)]))
        self.segments.append(SegmentArc((0.5, 0.78), width=0.5, height=0.32, theta1=180, theta2=360))


class ThermalHeater(Element2Term):
    """热继电器发热元件 FR（串在主电路里）：矩形框内一条台阶折线。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        h = 0.25
        # 第一个线段必须是 Segment（schemdraw 用它确定引线起点），所以先画折线再画矩形框
        self.segments.append(Segment([(0, 0), (0.3, 0), (0.3, 0.12), (0.7, 0.12), (0.7, 0), (1, 0)], zorder=4))
        self.segments.append(SegmentPoly([(0, -h), (1, -h), (1, h), (0, h)], fill="bg"))


class ThermalNC(Element2Term):
    """热继电器常闭触点 FR（串在控制电路里）：常闭触点 + 虚线连到一个小台阶符号（表示由热元件推动）。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.segments.append(Segment([(0, 0), (1.12, 0.42), GAP, (1, 0)]))
        self.segments.append(Segment([(1, 0), (1, 0.5)]))
        self.segments.append(Segment([(0.5, 0.19), (0.5, 0.7)], ls="--"))
        self.segments.append(Segment([(0.3, 0.7), (0.4, 0.7), (0.4, 0.85), (0.6, 0.85), (0.6, 0.7), (0.7, 0.7)]))


class Motor3(Element2Term):
    """电动机：圆圈内写文字（默认「M 3~」= 三相交流电动机；单相写 "M\\n1~"，直流写 "M"）。"""
    def __init__(self, text="M\n3~", **kw):
        super().__init__(**kw)
        r = 0.5
        self.segments.append(Segment([(0, 0), GAP, (1, 0)]))
        self.segments.append(SegmentCircle((0.5, 0), r, fill="bg"))
        self.segments.append(SegmentText((0.5, 0), text, fontsize=10, align=("center", "center")))  # 文字始终保持正立


class LampX(Element2Term):
    """灯（国标画法：圆圈加 ×）。用于照明灯（双控开关）和指示灯。"""
    def __init__(self, **kw):
        super().__init__(**kw)
        r = 0.35
        k = r * 0.7071
        self.segments.append(Segment([(0, 0), GAP, (2 * r, 0)]))
        self.segments.append(SegmentCircle((r, 0), r, fill="bg"))
        self.segments.append(Segment([(r - k, -k), (r + k, k)]))
        self.segments.append(Segment([(r - k, k), (r + k, -k)]))


def barrier(d, x, y0, y1, text="隔离带"):
    """在 x 处从 y0 到 y1 画灰色虚线隔离带，顶端写 text。"""
    d += elm.Line().at((x, y0)).to((x, y1)).linestyle("--").color("#808080")
    d += elm.Label().at((x, y1 + 0.35)).label(text, fontsize=10, color="#4d4d4d")


def module(name, left=(), right=(), w=3.0):
    """方框模块：left / right 是引脚名列表（如 ("VIN", "GND1")、("VOUT", "GND2")），引脚锚点名同引脚名。"""
    pins = ([elm.IcPin(name=n, side="left") for n in reversed(left)]      # Ic 引脚自下而上排，这里反转成「从上往下写」
            + [elm.IcPin(name=n, side="right") for n in reversed(right)])
    return elm.Ic(pins=pins, edgepadW=w - 1.5, pinspacing=1.0, size=(w, max(len(left), len(right), 1) + 1)).label(name, "top", fontsize=11)


CUSTOM = [Coil, ContactNO, ContactNC, PushNO, PushNC, TimerNO, TimerNC, ThermalHeater, ThermalNC, Motor3, LampX]
BUILTIN = ["Opamp", "Diode", "Zener", "LED", "Rectifier", "BjtNpn", "BjtPnp", "NFet", "PFet", "NMos",
           "Resistor", "Capacitor", "Inductor2", "Potentiometer", "Transformer", "FuseIEC", "Switch",
           "SwitchSpdt2", "Button", "Relay", "Optocoupler", "Schottky", "SourceSin", "SourceSquare", "SourceV", "Battery", "Lamp", "Motor", "Ground"]


def _demo(out="/tmp/schem_demo"):
    """画三张验证图到 /tmp（不进仓库）：①反相放大器（含中文标注）②全部自定义元件 ③常用自带元件。"""
    os.makedirs(out, exist_ok=True)
    # ① 反相放大器：检查运放引脚锚点、中文标签、mathtext 下标
    with drawing() as d:
        d += (op := elm.Opamp(leads=True))                      # 先放运放，才能引用它的 in1 / in2 / out 锚点
        d += elm.Line().left().at(op.in1).length(0.5)
        d += (j := elm.Dot())
        d += (r1 := elm.Resistor().left().label("$R_1$ 10 kΩ"))
        d += elm.Dot(open=True).label("$V_i$ 输入", "left")
        d += elm.Line().up().at(j.center).length(1.5)
        d += elm.Resistor().right().label("$R_f$ 100 kΩ 反馈电阻").tox(op.out.x + 0.5)
        d += elm.Line().down().toy(op.out)
        d += elm.Dot()
        d += elm.Line().left().at(op.in2).length(0.5)
        d += elm.Line().down().length(0.5)
        d += elm.Ground()
        d += elm.Line().right().at(op.out).length(0.5)
        d += elm.Line().right().length(0.75)
        d += elm.Dot(open=True).label("$V_o$ 输出", "right")
    p1 = f"{out}/inverting.png"; d.save(p1, dpi=DPI); print(p1, f"{shrink_png(p1):.0f} KB")
    # ② 自定义元件一字排开（竖着画，模拟控制电路的支路）
    with drawing(fontsize=11) as d:
        x = 0
        for cls, lab in zip(CUSTOM, ["KM 线圈", "KM 常开", "KM 常闭", "SB2 启动", "SB1 停止", "KT 延时合",
                                     "KT 延时断", "FR 热元件", "FR 常闭", "电动机", "灯 EL"]):
            d += elm.Line().at((x, 0)).down().length(0.4)
            d += cls().down().label(lab, "bottom", fontsize=10, ofst=0.25)
            d += elm.Line().down().length(0.4)
            x += 3.0
    p2 = f"{out}/custom.png"; d.save(p2, dpi=DPI); print(p2, f"{shrink_png(p2):.0f} KB")
    # ③ 自带元件：每个画一次，确认能实例化并渲染
    with drawing(fontsize=10) as d:
        x, y = 0, 0
        for i, name in enumerate(BUILTIN):
            e = getattr(elm, name)
            if name in ("Opamp", "BjtNpn", "BjtPnp", "NFet", "PFet", "NMos", "Transformer", "Rectifier", "Relay", "Optocoupler", "Ground"):
                d += e().at((x - 1, y))                       # 多端元件：放在格子里即可
            else:
                d += e().at((x - 1.25, y)).right()            # 两端元件：横着画一段
            d += elm.Label().at((x, y - 1.9)).label(name)
            x += 4.0
            if i % 7 == 6:
                x, y = 0, y - 4.0
    p3 = f"{out}/builtin.png"; d.save(p3, dpi=DPI); print(p3, f"{shrink_png(p3):.0f} KB")
    # ④ 隔离：光耦 + 隔离带 + 隔离 DC-DC 模块
    with drawing(fontsize=11) as d:
        d += (oc := elm.Optocoupler().at((0, 0)))
        d += module("隔离 DC-DC 模块", ("VIN", "GND1"), ("VOUT", "GND2")).at((5, 0)).anchor("VIN")
        barrier(d, 1.4, -2.5, 1.2)
    p3 = f"{out}/isolation.png"; d.save(p3, dpi=DPI); print(p3, f"{shrink_png(p3):.0f} KB")
    print("字体:", FONT, " 自定义元件:", ", ".join(c.__name__ for c in CUSTOM), " 自带元件:", len(BUILTIN), "个 OK")


if __name__ == "__main__" and "--demo" in sys.argv:
    _demo()
