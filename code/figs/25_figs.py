"""25 H 桥电机驱动：全部配图（图 25-p2-2 由 code/25_sim.py 生成）。
运行：/workspace/circuits-venv/bin/python code/figs/25_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。
"""
import os, sys
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt

N = "25"
_spec = importlib.util.spec_from_file_location("sim25", os.path.join(HERE, "..", "25_sim.py"))
sim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sim)
RPM = 60 / (2 * np.pi)
ON = fs.LS["vout"]["color"]      # 电流路径：橙色
BAD = fs.LS["bad"]["color"]      # 短路路径：朱红色
OFF = "#8c8c8c"


def bridge(d, x0, closed, title, path, color=ON, motor_label="M"):
    """画一个四开关 H 桥。closed：闭合的开关名集合；path：要涂色的支路名集合。"""
    xl, xr = x0, x0 + 4.0
    col = lambda k: color if k in path else "black"
    d += elm.Line().endpoints((x0 + 2, 6.0), (xl, 6.0)).color(col("topL"))
    d += elm.Line().endpoints((x0 + 2, 6.0), (xr, 6.0)).color(col("topR"))
    d += elm.Vdd().at((x0 + 2, 6.0)).label("+12 V")
    d += elm.Line().endpoints((xl, 0.0), (x0 + 2, 0.0)).color(col("botL"))
    d += elm.Line().endpoints((xr, 0.0), (x0 + 2, 0.0)).color(col("botR"))
    d += elm.Ground().at((x0 + 2, 0.0))
    for name, x, y1, y0, side in [("S1", xl, 6.0, 3.0, "left"), ("S3", xl, 3.0, 0.0, "left"),
                                  ("S2", xr, 6.0, 3.0, "right"), ("S4", xr, 3.0, 0.0, "right")]:
        c = col(name)
        d += elm.Line().endpoints((x, y1), (x, y1 - 0.5)).color(c)
        if name in closed:
            d += elm.Line().endpoints((x, y1 - 0.5), (x, y0 + 0.5)).color(c)
            d += elm.Dot(radius=0.08).at((x, y1 - 0.5)).color(c)
            d += elm.Dot(radius=0.08).at((x, y0 + 0.5)).color(c)
        else:
            d += elm.Switch().endpoints((x, y1 - 0.5), (x, y0 + 0.5)).color(OFF)
        txt = f"{name}\n{'闭合' if name in closed else '断开'}"
        dx = -0.45 if side == "left" else 0.45
        d += elm.Label().at((x + dx, (y1 + y0) / 2)).label(txt, halign="right" if side == "left" else "left",
                                                          color=c if name in closed else OFF)
        d += elm.Line().endpoints((x, y0 + 0.5), (x, y0)).color(c)
    d += elm.Dot().at((xl, 3.0)).label("A", loc="left", ofst=0.1)
    d += elm.Dot().at((xr, 3.0)).label("B", loc="right", ofst=0.1)
    d += elm.Motor().endpoints((xl, 3.0), (xr, 3.0)).color(col("motor")).label(motor_label, loc="top")
    d += elm.Label().at((x0 + 2, -1.3)).label(title)


def fig_p1_1():
    with drawing(fontsize=11) as d:
        bridge(d, 0, {"S1", "S4"}, "(a) 正转：S1、S4 闭合\n电流 +12 V → A → M → B → 地",
               {"topL", "S1", "motor", "S4", "botR"}, motor_label="M　电流 →")
        bridge(d, 7.5, {"S2", "S3"}, "(b) 反转：S2、S3 闭合\n电流 +12 V → B → M → A → 地",
               {"topR", "S2", "motor", "S3", "botL"}, motor_label="M　← 电流")
        save_schem(d, N, "25_p1_1_paths.png")


def fig_p1_2():
    with drawing(fontsize=11) as d:
        bridge(d, 0, {"S3", "S4"}, "(a) 刹车：S3、S4 闭合\n电机两端被短接",
               {"S3", "S4", "motor", "botL", "botR"}, motor_label="M（发电）")
        bridge(d, 7.5, {"S1", "S3"}, "(b) 直通：S1、S3 同时闭合\n电源被直接短路（禁止！）",
               {"topL", "S1", "S3", "botL"}, color=BAD, motor_label="M")
        save_schem(d, N, "25_p1_2_brake_short.png")


def fig_p1_3():
    """正转 → 滑行 → 正转 → 刹车 → 反转 的转速与电流（全电压，不调速）。"""
    seq = [(0.0, "F"), (0.4, "C"), (0.7, "F"), (1.1, "B"), (1.3, "R")]
    def sched(t):
        s = "F"
        for t0, st in seq:
            if t >= t0:
                s = st
        return s
    t, I, W, V = sim.run(sched, 1.8, dt=5e-6)
    def at(tt):
        return W[np.searchsorted(t, tt)] * RPM
    w_full = at(0.399); w_coast = at(0.699); w_brake = at(1.299)
    i_start = I[t < 0.05].max(); i_rev = I[t > 1.3].min(); i_brake = I[(t > 1.1) & (t < 1.3)].min()
    print(f"[数值] 正转稳定 {w_full:.0f} rpm；滑行 0.3 s 后还剩 {w_coast:.0f} rpm；刹车 0.2 s 后剩 {w_brake:.0f} rpm；"
          f"起动电流峰值 {i_start:.2f} A；刹车瞬间电流 {i_brake:.2f} A；刹车后反转电流 {i_rev:.2f} A；最终 {W[-1]*RPM:.0f} rpm")
    assert w_coast > 0.6 * w_full and abs(w_brake) < 0.1 * w_full
    fig, ax = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
    names = {"F": "正转", "C": "滑行", "B": "刹车", "R": "反转"}
    ends = [s[0] for s in seq[1:]] + [1.8]
    for a in ax:
        for (t0, st), t1 in zip(seq, ends):
            if st in "CB":
                a.axvspan(t0, t1, color="0.92", zorder=0)
    for (t0, st), t1 in zip(seq, ends):
        ax[0].text((t0 + t1) / 2, 1.02, names[st], transform=ax[0].get_xaxis_transform(), ha="center", va="bottom", fontsize=9)
    ax[0].plot(t, W * RPM, **fs.LS["vout"], label="转速")
    fs.ref_h(ax[0], 0)
    fs.axlabels(ax[0], "时间", "s", "转速", "rpm"); ax[0].set_xlabel("")
    ax[1].plot(t, I, **fs.LS["cur"], label="电机电流（A→B 方向为正）")
    fs.ref_h(ax[1], 0)
    ax[1].legend(loc="lower left", fontsize=8)
    fs.axlabels(ax[1], "时间", "s", "电流", "A")
    fs.save(fig, N, "25_p1_3_sequence.png")
    return w_full, w_coast, w_brake, i_start, i_rev


def fig_p2_1():
    """分立 H 桥：四只 N 沟道 MOS 管（含体二极管）、储能电容、采样电阻。"""
    with drawing(fontsize=11) as d:
        xl, xr = 0.0, 6.0
        d += elm.Line().endpoints((xl, 8.0), (xr, 8.0))
        d += elm.Vdd().at((3.0, 8.0)).label("$V_M$ = +12 V")
        d += elm.Line().endpoints((xr, 8.0), (10.5, 8.0))
        d += elm.Capacitor(polar=True).endpoints((10.5, 8.0), (10.5, 0.0)).label("$C_B$\n470 µF\n储能", loc="bottom", ofst=0.2)
        d += elm.Line().endpoints((xl, 0.0), (10.5, 0.0))
        d += elm.Resistor().endpoints((3.0, 0.0), (3.0, -2.0)).label("$R_S$ 0.1 Ω\n电流采样\n（接 11 节）", loc="bottom", ofst=0.2)
        d += elm.Ground().at((3.0, -2.0))
        fets = {}
        for name, x, ytop, gate_side, gl in [("Q1", xl, 8.0, "L", "AH"), ("Q3", xl, 4.0, "L", "AL"),
                                             ("Q2", xr, 8.0, "R", "BH"), ("Q4", xr, 4.0, "R", "BL")]:
            q = elm.NFet().theta(0).anchor("drain").at((x, ytop - 0.4))
            q = q.reverse() if gate_side == "L" else q
            d += elm.Line().endpoints((x, ytop), (x, ytop - 0.4))
            d += q
            d += elm.Line().endpoints(q.source, (x, ytop - 4.0))
            fets[name] = q
            gx = q.gate[0] + (-0.8 if gate_side == "L" else 0.8)
            d += elm.Line().endpoints(q.gate, (gx, q.gate[1]))
            d += elm.Dot(open=True).at((gx, q.gate[1]))
            d += elm.Label().at((gx + (-0.2 if gate_side == "L" else 0.2), q.gate[1])).label(
                f"{name}\n栅极 {gl}", halign="right" if gate_side == "L" else "left")
            dx = 1.1 if gate_side == "L" else -1.1
            yd0, yd1 = ytop - 0.4, q.source[1]
            d += elm.Line().endpoints((x, yd0 - 0.0), (x + dx, yd0))
            d += elm.Diode().endpoints((x + dx, yd1), (x + dx, yd0)).color("#666666")
            d += elm.Line().endpoints((x + dx, yd1), (x, yd1))
        d += elm.Dot().at((xl, 4.0)).label("A", loc="left", ofst=(-0.1, 0.3))
        d += elm.Dot().at((xr, 4.0)).label("B", loc="right", ofst=(0.1, 0.3))
        d += elm.Motor().endpoints((xl, 4.0), (xr, 4.0)).label("M", loc="top")
        d += elm.Line().endpoints((-4.6, 4.0), (-4.55, 4.0)).color("white")   # 留出左侧标签的位置
        save_schem(d, N, "25_p2_1_discrete.png")


def fig_p2_3():
    """全速正转后分别「刹车」和「滑行」：转速和电流。"""
    w0 = sim.avg_speed(1.0)[0]
    i0 = sim.B * w0 / sim.KE
    fig, ax = plt.subplots(2, 1, figsize=fs.SIZE["tall"])
    res = {}
    for st, key, name in [("B", "vout", "刹车（S3、S4 闭合，慢衰减）"), ("C", "vin", "滑行（四管全断，快衰减）")]:
        t, I, W, V = sim.run(lambda tt, st=st: st, 2.0, dt=5e-6, i0=i0, w0=w0)
        k = np.argmax(W < 0.1 * w0) if (W < 0.1 * w0).any() else None
        t10 = t[k] if k is not None else float("nan")
        res[st] = (t10, W[np.searchsorted(t, 0.5)] * RPM, I.min(), I.max())
        lab = f"{name}：降到 10% 用 {t10*1e3:.0f} ms" if k is not None else f"{name}：2 s 后仍有 {W[-1]/w0:.0%}"
        ax[0].plot(t, W * RPM, **fs.LS[key], label=lab)
    print(f"[数值] 初速 {w0*RPM:.0f} rpm；刹车降到 10% 用 {res['B'][0]*1e3:.0f} ms，0.5 s 时 {res['B'][1]:.0f} rpm，电流最低 {res['B'][2]:.2f} A；"
          f"滑行 0.5 s 时 {res['C'][1]:.0f} rpm，电流范围 {res['C'][2]:.3f}～{res['C'][3]:.3f} A")
    assert res["B"][0] < 0.3 and res["C"][1] > 0.5 * w0 * RPM
    fs.ref_h(ax[0], 0)
    ax[0].legend(loc="upper right", fontsize=8)
    fs.axlabels(ax[0], "时间", "s", "转速", "rpm")
    ax1 = ax[1]
    for st, key, name in [("B", "vout", "刹车"), ("C", "vin", "滑行")]:
        t, I, W, V = sim.run(lambda tt, st=st: st, 0.02, dt=1e-6, i0=i0, w0=w0)
        ax1.plot(t * 1e3, I, **fs.LS[key], label=name)
        if st == "C":
            k0 = np.argmax(I <= 0)
            print(f"[数值] 滑行：电流经体二极管回灌电源，{t[k0]*1e6:.0f} µs 内降到 0")
    fs.ref_h(ax1, 0)
    ax1.legend(loc="lower right", fontsize=8)
    ax1.set_title("断电后前 20 ms 的电机电流（放大）", fontsize=9)
    fs.axlabels(ax1, "时间", "ms", "电流", "A")
    fs.save(fig, N, "25_p2_3_brake_coast.png")
    return w0, res


def fig_p3_1():
    """死区时间与直通电流。"""
    deads = [0, 50, 100, 150, 200, 250, 300, 400]
    out = []
    for td in deads:
        t, i, pk, e = sim.shoot_through(td * 1e-9)
        out.append((td, pk, e))
    print("[数值] 死区 / ns → 直通峰值 / A、每次能量 / µJ、20 kHz 下每桥臂功率 / W：")
    for td, pk, e in out:
        print(f"    {td:4d} ns：{pk:7.1f} A  {e*1e6:7.2f} µJ  {2*e*20e3:6.2f} W")
    assert out[0][1] > 20 and all(pk < 0.01 for td, pk, e in out if td >= sim.T_SW * 1e9)
    fig, axes = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    ax = axes[0]
    for td, key in [(0, "bad"), (100, "vin"), (250, "good")]:
        t, i, pk, e = sim.shoot_through(td * 1e-9)
        st = fs.LS[key] if key != "bad" else {**fs.LS["bad"], "marker": None}
        ax.plot(t * 1e9, i, **st, label=f"死区 {td} ns：峰值 {pk:.0f} A")
    ax.set_xlim(0, 500)
    fs.axlabels(ax, "时间", "ns", "直通电流", "A")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title(f"(a) 每只管子开/关过渡 {sim.T_SW*1e9:.0f} ns", fontsize=9)
    ax = axes[1]
    ax.plot([o[0] for o in out], [o[1] for o in out], **fs.LS["bad"], label="直通电流峰值")
    fs.ref_v(ax, sim.T_SW * 1e9, f"死区 = 过渡时间 {sim.T_SW*1e9:.0f} ns")
    fs.axlabels(ax, "死区时间", "ns", "直通峰值", "A")
    ax.legend(loc="center right", fontsize=8)
    ax.set_title("(b) 死区越长，直通越小；≥ 过渡时间就为 0", fontsize=9)
    fs.save(fig, N, "25_p3_1_deadtime.png")
    return out


def fig_p3_2():
    """PWM 频率：电流纹波与可听范围。"""
    d = 0.5
    fs_list = [500, 1e3, 2e3, 5e3, 10e3, 20e3, 50e3]
    w0 = sim.avg_speed(d)[0]; i0 = sim.B * w0 / sim.KE
    rip = []
    fig, axes = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    for f in fs_list:
        n_per = 200
        t, I, W, V = sim.run(sim.pwm_schedule(d, f), max(20 / f, 3e-3), dt=1 / f / n_per, i0=i0, w0=w0)
        seg = I[-5 * n_per:]
        rip.append(np.ptp(seg))
        if f in (1e3, 20e3):
            key = "bad" if f == 1e3 else "good"
            st = {**fs.LS[key], "marker": None, "lw": 1.2} if key == "bad" else fs.LS[key]
            m = t >= t[-1] - 2e-3
            axes[0].plot((t[m] - t[m][0]) * 1e3, I[m], **st, label=f"{f/1e3:.0f} kHz：纹波 {np.ptp(seg):.2f} A")
    print("[数值] 占空比 50% 时电流峰峰纹波：" + "，".join(f"{f/1e3:g} kHz {r:.3f} A（近似式 {sim.ripple_pp(d, f):.3f}）" for f, r in zip(fs_list, rip)))
    assert rip[0] > 5 * rip[-2]
    fs.axlabels(axes[0], "时间", "ms", "电机电流", "A")
    axes[0].set_ylim(-1.6, 2.5)
    axes[0].legend(loc="upper center", ncol=2, fontsize=8)
    axes[0].set_title("(a) 占空比 50%、最后 2 ms 的电流", fontsize=9)
    ax = axes[1]
    ax.axvspan(20, 20e3, color="0.92", zorder=0)
    ax.text(2.5e3, 0.93, "灰色：人耳可听范围（约 20 Hz～20 kHz）", transform=ax.get_xaxis_transform(), ha="center", fontsize=8, color="0.3")
    ax.loglog(fs_list, rip, **fs.LS["vout"], marker="o", label="仿真")
    ff = np.logspace(np.log10(400), np.log10(60e3), 50)
    ax.loglog(ff, sim.ripple_pp(d, ff), **fs.LS["ref"], label="近似式 $V_M D(1-D)/(Lf)$")
    ax.set_xlim(300, 8e4)
    fs.axlabels(ax, "PWM 频率", "Hz", "电流纹波（峰峰）", "A")
    ax.legend(loc="lower left", fontsize=8)
    ax.set_title("(b) 频率每高 10 倍，纹波小 10 倍", fontsize=9)
    fs.save(fig, N, "25_p3_2_pwm_freq.png")
    return dict(zip(fs_list, rip))


if __name__ == "__main__":
    fig_p1_1(); fig_p1_2(); fig_p1_3(); fig_p2_1(); fig_p2_3(); fig_p3_1(); fig_p3_2()
    print("[数值] DRV8871 限流 I_TRIP = 64 kV / R_ILIM：" + "，".join(f"{r} kΩ → {64/r:.2f} A" for r in (15, 20, 24, 32, 43, 64)))


# ======================= page4 动手实验篇：面包板接线图 =======================
# 面包板俯视图小工具（各节点脚本各带一份，互不依赖）。
# 坐标：列号 1…ncol 从左到右；上半区 a–e、下半区 f–j（同一列的 a–e 五个孔互相连通，f–j 也连通）；
# 上下各有两条电源轨：靠外的一条标「+」，靠里的一条标「−」，整条横向连通。
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

BB_Y = {r: 5.6 - i for i, r in enumerate("abcde")}
BB_Y.update({r: -1.4 - i for i, r in enumerate("fghij")})
BB_Y.update({"T+": 8.6, "T-": 7.7, "B-": -6.7, "B+": -7.6})
WIRE = dict(pos=(fs.C["bad"], "正电源"), gnd=("#000000", "地（0 V）"), neg=(fs.C["third"], "负电源"),
            sig=(fs.C["vin"], "输入信号"), out=(fs.C["vout"], "输出"), fb=(fs.C["fb"], "反馈 / 其他连线"))


class Breadboard:
    def __init__(self, ncol=30, title=None, size=(10, 6.4), rails=("+", "−", "−", "+")):
        self.ncol, self.used = ncol, set()
        self.fig, self.ax = plt.subplots(figsize=size)
        ax = self.ax
        ax.add_patch(FancyBboxPatch((0.2, -8.3), ncol + 0.6, 17.6, boxstyle="round,pad=0.1",
                                    fc="#f7f5ef", ec="0.55", lw=1.0))
        ax.add_patch(Rectangle((0.4, -0.55), ncol + 0.2, 0.7, fc="#e4e0d6", ec="none"))   # 中间凹槽
        for key, lab in zip(("T+", "T-", "B-", "B+"), rails):
            y = BB_Y[key]
            col = fs.C["bad"] if lab.startswith("+") else ("#000000" if lab in ("−", "GND", "0 V") else fs.C["third"])
            ax.plot([0.6, ncol + 0.4], [y + 0.42, y + 0.42], color=col, lw=1.0)
            ax.text(0.0, y, lab, ha="right", va="center", fontsize=10, color=col, fontweight="bold")
            for c in range(1, ncol + 1):
                if c % 6:
                    ax.add_patch(Circle((c, y), 0.12, fc="0.72", ec="none"))
        for r in "abcdefghij":
            y = BB_Y[r]
            ax.text(0.15, y, r, ha="right", va="center", fontsize=8, color="0.35")
            ax.text(ncol + 0.85, y, r, ha="left", va="center", fontsize=8, color="0.35")
            for c in range(1, ncol + 1):
                ax.add_patch(Circle((c, y), 0.12, fc="0.72", ec="none"))
        for c in range(1, ncol + 1):
            if c == 1 or c % 5 == 0:
                ax.text(c, 6.35, str(c), ha="center", va="bottom", fontsize=7.5, color="0.35")
                ax.text(c, -6.15, str(c), ha="center", va="top", fontsize=7.5, color="0.35")
        ax.set_xlim(-3.4, ncol + 4.8)
        ax.set_ylim(-11.2, 11.6)
        ax.set_aspect("equal")
        ax.axis("off")
        if title:
            ax.set_title(title, fontsize=11)

    def xy(self, h):
        """'e10' → 第 10 列 e 排；'T+3' / 'B-7' → 上（T）/ 下（B）电源轨第 3 / 7 列。"""
        if h[0] in "TB" and h[1] in "+-":
            return float(h[2:]), BB_Y[h[:2]]
        return float(h[1:]), BB_Y[h[0]]

    def _hole(self, p):
        x, y = self.xy(p) if isinstance(p, str) else p
        if isinstance(p, str):
            self.ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=4))
        return x, y

    def wire(self, a, b, kind="fb", via=None):
        """导线：a、b 为孔名或 (x, y)；via 为中间拐点列表。颜色按 kind 取（见 WIRE）。"""
        self.used.add(kind)
        pts = [self._hole(a)] + list(via or []) + [self._hole(b)]
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=WIRE[kind][0], lw=2.4, solid_capstyle="round", zorder=5)

    def part(self, a, b, label, kind="R", lab_side=1):
        """两脚元件：R 电阻、C 电容、E 电解电容（+ 脚在 a）、D 二极管（a 阳 b 阴）、L LED（a 阳）、
        S 按钮、P 小灯泡。画成方框简化符号，标签写在旁边。"""
        (x1, y1), (x2, y2) = self._hole(a), self._hole(b)
        ax = self.ax
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.plot([x1, x2], [y1, y2], color="0.35", lw=1.2, zorder=5)
        fc = dict(R="#d9c7a3", C="#f2d27a", E="#6d8fb5", D="#555555", L="#ffffff", S="#bbbbbb",
                  P="#fff7c2")[kind]
        horiz = abs(x2 - x1) >= abs(y2 - y1)
        w, h = (0.9, 0.5) if horiz else (0.5, 0.9)
        if kind in "LP":
            ax.add_patch(Circle((mx, my), 0.42, fc=fc, ec="0.2", lw=1.0, zorder=6))
        else:
            ax.add_patch(FancyBboxPatch((mx - w / 2, my - h / 2), w, h, boxstyle="round,pad=0.05",
                                        fc=fc, ec="0.2", lw=1.0, zorder=6))
        if kind in "EDL":
            ax.text(x1 + (0.25 if horiz else 0.25), y1 + (0.3 if horiz else 0), "+", fontsize=8,
                    ha="center", va="center", zorder=7, color=fs.C["bad"])
        if lab_side == "r":
            ax.text(max(x1, x2) + 0.3, my, label, ha="left", va="center", fontsize=8.5, zorder=7)
        elif horiz:
            ax.text(mx, my + 0.55 * lab_side, label, ha="center", va="bottom" if lab_side > 0 else "top",
                    fontsize=8.5, zorder=7)
        else:
            ax.text(mx + 0.45 * lab_side, my, label, ha="left" if lab_side > 0 else "right",
                    va="center", fontsize=8.5, zorder=7)

    def chip(self, col, label, npin=8, names=None):
        """DIP 芯片跨在中间凹槽上：第 1 脚在 f 排第 col 列（左下，缺口朝左），逆时针数，
        第 npin 脚在 e 排第 col 列。脚号和脚名写在芯片体上。"""
        half = npin // 2
        ax = self.ax
        y0, y1 = BB_Y["f"] + 0.22, BB_Y["e"] - 0.22
        ax.add_patch(Rectangle((col - 0.5, y0), half, y1 - y0, fc="#2b2b2b", ec="k", zorder=6))
        ax.add_patch(Circle((col - 0.5, (y0 + y1) / 2), 0.28, fc="#f7f5ef", ec="none", zorder=7))
        ax.text(col + (half - 1) / 2, (y0 + y1) / 2, label, color="w", ha="center",
                va="center", fontsize=9, zorder=8)
        for i in range(half):
            for p, row in ((i + 1, "f"), (npin - i, "e")):
                x, y = col + i, BB_Y[row]
                ax.add_patch(Circle((x, y), 0.17, fc="0.15", ec="none", zorder=7))
                txt = str(p) + ("\n" + names[p] if names and p in names else "")
                ax.text(x, y0 + 0.08 if row == "f" else y1 - 0.08, txt, ha="center",
                        va="bottom" if row == "f" else "top", fontsize=6, color="w", zorder=8,
                        linespacing=0.9)

    def module(self, x, y, w, h, label, fc="#e6f0f8"):
        """面包板外的模块（电池、信号源、继电器模块等），返回方框中心。"""
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec="0.3",
                                         lw=1.0, zorder=6))
        self.ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8.5, zorder=7)
        return x + w / 2, y + h / 2

    def note(self, x, y, text, **kw):
        self.ax.text(x, y, text, fontsize=8, zorder=8, **kw)

    def legend(self, loc="lower center"):
        from matplotlib.lines import Line2D
        hs = [Line2D([], [], color=WIRE[k][0], lw=2.4, label=WIRE[k][1]) for k in WIRE if k in self.used]
        self.ax.legend(handles=hs, loc=loc, ncol=len(hs), fontsize=8.5, frameon=False,
                       bbox_to_anchor=(0.5, -0.01))

    def save(self, prefix, name):
        return fs.save(self.fig, prefix, name)

# ---------- page4 动手实验篇：6 V 小电机 + L298N 模块 ----------
from matplotlib.patches import Circle as _Circ

V_S = 6.0                                           # 电机电源（4 节 AA 电池或 6 V 直流电源）
VSAT_H = (0.95, 1.35, 1.7)                          # L298 手册：IL = 1 A 时上管（source）饱和压降 min/typ/max，V
VSAT_L = (0.85, 1.2, 1.6)                           # 下管（sink）饱和压降，V
VTOT = (1.80, 3.2)                                  # 总压降 min/max，V
VSS_MIN, REG_HEADROOM, DRV_VM_MIN = 4.5, 2.0, 6.5   # L298 逻辑电源下限；78M05 约需 2 V 余量；DRV8871 VM 下限
OUT1_F = (V_S - VSAT_H[2], V_S - VSAT_H[0])
OUT2_F = (VSAT_L[0], VSAT_L[2])
VMOT_F = (V_S - VTOT[1], V_S - VTOT[0])
print(f"[数值] 6 V、1 A 手册值：正转 OUT1 对地 {OUT1_F[0]:.2f}–{OUT1_F[1]:.2f} V，OUT2 对地 {OUT2_F[0]:.2f}–{OUT2_F[1]:.2f} V，"
      f"电机两端 {VMOT_F[0]:.2f}–{VMOT_F[1]:.2f} V")
assert abs(OUT1_F[0] - 4.30) < 1e-9 and abs(OUT1_F[1] - 5.05) < 1e-9 and abs(VMOT_F[0] - 2.8) < 1e-9 and abs(VMOT_F[1] - 4.2) < 1e-9
print(f"[数值] 板载 78M05 在 6 V 下只能给约 {V_S - REG_HEADROOM:.1f} V（< L298 逻辑下限 {VSS_MIN} V）；"
      f"DRV8871 下限 {DRV_VM_MIN} V > {V_S:.0f} V")
assert V_S - REG_HEADROOM < VSS_MIN and V_S < DRV_VM_MIN
DUTY = [v / 255 for v in (64, 128, 192)]            # Arduino analogWrite 的三个值
print("[数值] analogWrite 64/128/192 → 占空比 " + "、".join(f"{d:.1%}" for d in DUTY))
assert [round(d * 1000) for d in DUTY] == [251, 502, 753]


def _truth(en, in1, in2):
    """L298 手册真值表：EN=H 时 C=H,D=L 正转；C=L,D=H 反转；C=D 快速停车；EN=L 自由滑行。"""
    if not en:
        return "滑行"
    return {(1, 0): "正转", (0, 1): "反转"}.get((in1, in2), "刹车")
assert [_truth(*s) for s in ((1, 1, 0), (1, 0, 1), (1, 0, 0), (1, 1, 1), (0, 1, 0))] == ["正转", "反转", "刹车", "刹车", "滑行"]

# ---------- 图 25-p4-1：面包板 + L298N 模块接线 ----------
WIRE["pos"] = (fs.C["bad"], "+5 V（逻辑）/ +6 V（电机电源）")
WIRE["gnd"] = ("#000000", "GND（公共地）")
WIRE["sig"] = (fs.C["vin"], "控制信号 ENA / IN1 / IN2")
WIRE["out"] = (fs.C["vout"], "电机线 OUT1 / OUT2")
bb = Breadboard(26, "H 桥实验接线俯视图（6 V 电池 + L298N 模块 + 小直流电机；图中为正转：ENA=1、IN1=1、IN2=0）",
                size=(10, 8.6), rails=("（未用）", "（未用）", "GND", "+5 V"))
for t in bb.ax.texts:
    if t.get_text() == "（未用）":
        t.set_color("0.6"); t.set_fontweight("normal"); t.set_fontsize(8.5)
for ln in bb.ax.lines:
    ys = ln.get_ydata()
    if len(ys) == 2 and ys[0] == ys[1] and ys[0] in (BB_Y["T+"] + 0.42, BB_Y["T-"] + 0.42):
        ln.set_color("0.75")
bb.ax.set_ylim(-19.5, 11.6)
COLS = dict(ENA=6, IN1=12, IN2=18)
STATE = dict(ENA=1, IN1=1, IN2=0)                   # 正转
for name, c in COLS.items():
    bb.wire(f"i{c}", f"B+{c + 1}" if STATE[name] else f"B-{c + 1}", "pos" if STATE[name] else "gnd")
    bb.wire(f"f{c}", (c, -11.0), "sig", via=[(c - 0.5, -1.9), (c - 0.5, -9.0), (c, -9.6)])
    bb.ax.text(c + 0.3, -3.0, name, ha="left", va="center", fontsize=9, color=fs.C["vin"], fontweight="bold", zorder=9)
assert _truth(STATE["ENA"], STATE["IN1"], STATE["IN2"]) == "正转"
mx0, my0 = 3.0, -15.6
bb.module(mx0, my0, 20.0, 4.6, "", fc="#e8eef5")
bb.ax.text(13.0, -13.3, "L298N 模块\n（5V-EN 跳线帽拔掉；ENA 跳线帽拔掉，改由第 6 列控制）", ha="center", va="center", fontsize=8.5, zorder=8)
for name, c in COLS.items():
    bb.ax.add_patch(_Circ((c, -11.0), 0.22, fc="0.15", ec="none", zorder=8))
    bb.ax.text(c, -11.45, name, ha="center", va="top", fontsize=7.5, zorder=8)
TERM = {"OUT1": (3.0, -12.4), "OUT2": (3.0, -14.4), "+12V": (9.0, -15.6), "GND": (13.0, -15.6), "+5V": (17.0, -15.6)}
for k, (x, y) in TERM.items():
    bb.ax.add_patch(Rectangle((x - 0.35, y - 0.35), 0.7, 0.7, fc="#3a7d44", ec="k", zorder=8))
    if k.startswith("OUT"):
        bb.ax.text(x + 0.55, y, k, ha="left", va="center", fontsize=7.5, zorder=8)
    else:
        bb.ax.text(x, y + 0.55, k if k != "+12V" else "+12V（接 6 V）", ha="center", va="bottom", fontsize=7.5, zorder=8)
bb.ax.add_patch(_Circ((-1.4, -13.4), 1.1, fc="#f3e3c3", ec="0.2", lw=1.2, zorder=7))
bb.ax.text(-1.4, -13.4, "M", ha="center", va="center", fontsize=11, fontweight="bold", zorder=8)
bb.wire((-0.6, -12.6), TERM["OUT1"], "out")
bb.wire((-0.6, -14.2), TERM["OUT2"], "out")
bb.module(4.0, -19.0, 5.6, 1.5, "6 V 电池盒（4 节 AA）", fc="#e6f0f8")
bb.wire((8.6, -17.5), TERM["+12V"], "pos", via=[(8.6, -16.6), (9.0, -16.6)])
bb.wire((5.2, -17.5), TERM["GND"], "gnd", via=[(5.2, -16.9), (13.0, -16.9)])
bb.module(19.5, -19.0, 9.0, 1.5, "Arduino UNO（只用 5V、GND、D9）", fc="#efe6f3")
bb.wire((21.0, -17.5), TERM["+5V"], "pos", via=[(21.0, -16.6), (17.0, -16.6)])
bb.wire((23.0, -17.5), TERM["GND"], "gnd", via=[(23.0, -16.9), (13.0, -16.9)])
bb.wire((27.5, -17.5), "B+26", "pos", via=[(27.5, -7.6)])
bb.wire((28.5, -17.5), "B-25", "gnd", via=[(28.5, -6.0), (25.0, -6.0)])
bb.note(1.0, 3.6, "上半区不用。每个控制列在 i 排插一根跳线：\n斜向接 +5 V 轨 = 1，接 GND 轨 = 0（图中 ENA=1、IN1=1、IN2=0）", va="center",
        bbox=dict(fc="#f7f5ef", ec="none", pad=1.5))
bb.legend()
_lg = bb.ax.get_legend(); _lg.set_loc("upper center"); _lg.set_bbox_to_anchor((0.5, 0.995)); _lg.set_ncols(2)
bb.save(N, "25_p4_1_breadboard.png")

# ---------- 图 25-p4-2：PWM 下电机两端的真实波形与万用表读数 ----------
F_PWM = 490.0                                       # Arduino UNO D9 的 analogWrite 频率
fig, axes = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
t = np.linspace(0, 3 / F_PWM, 3000, endpoint=False)
keys = ("third", "vin", "vout")
for d, k, off in zip(DUTY, keys, (0.0, 1.25, 2.5)):
    v = (((t * F_PWM) % 1.0) < d).astype(float)
    assert abs(v.mean() - d) < 2e-3
    axes[0].plot(t * 1e3, v + off, color=fs.C[k], lw=1.4)
    axes[0].plot([0, t[-1] * 1e3], [d + off] * 2, color=fs.C[k], ls="--", lw=1.0)
    axes[0].text(t[-1] * 1e3 + 0.1, d + off, f"平均 {d:.1%}", va="center", fontsize=8, color=fs.C[k])
axes[0].set_xlim(0, 7.4)
axes[0].set_yticks([0, 1, 1.25, 2.25, 2.5, 3.5]); axes[0].set_yticklabels(["0", "V_F", "0", "V_F", "0", "V_F"])
axes[0].set_xlabel("时间 / ms"); axes[0].set_ylabel("电机两端电压")
axes[0].set_title("(a) 示波器看到的：490 Hz 方波（实线），虚线是平均值", fontsize=9)
dd = np.linspace(0, 1, 11)
axes[1].plot(dd * 100, dd, **fs.LS["ref"], label="平均值 = 占空比 × V_F")
for d, k in zip(DUTY, keys):
    axes[1].plot(d * 100, d, "o", color=fs.C[k], ms=7)
    axes[1].annotate(f"{d:.1%}", (d * 100, d), xytext=(8, -12), textcoords="offset points", fontsize=8, color=fs.C[k])
axes[1].set_xlabel("占空比 / %"); axes[1].set_ylabel("万用表直流挡读数 / V_F")
axes[1].set_xlim(0, 100); axes[1].set_ylim(0, 1.05)
axes[1].legend(loc="upper left", fontsize=8)
axes[1].set_title("(b) 万用表直流挡读到的：平均值", fontsize=9)
fs.save(fig, N, "25_p4_2_pwm_average.png")
print(f"[数值] PWM {F_PWM:.0f} Hz，一个周期 {1e3 / F_PWM:.2f} ms")


# ======================= 第 8 轮补电路图（page1–page3：凡正文讲具体电路连接处，附近都要有电路图） =======================
from schem import C as _C
EMPH = _C["third"]      # 强调色（红紫）：新加的元件、PWM 开关


def _hb(d, x0, sw, title, path, color=ON, motor_label="M", names=("S1", "S2", "S3", "S4"), diodes=(), vtxt="+12 V"):
    """H 桥（同 bridge()，但每个开关可单独写状态）。sw：名字 → "on" / "off" / "pwm"；diodes：画出体二极管并涂色的开关。"""
    xl, xr = x0, x0 + 4.0
    col = lambda k: color if k in path else "black"
    d += elm.Line().endpoints((x0 + 2, 6.0), (xl, 6.0)).color(col("topL"))
    d += elm.Line().endpoints((x0 + 2, 6.0), (xr, 6.0)).color(col("topR"))
    d += elm.Vdd().at((x0 + 2, 6.0)).label(vtxt)
    d += elm.Line().endpoints((xl, 0.0), (x0 + 2, 0.0)).color(col("botL"))
    d += elm.Line().endpoints((xr, 0.0), (x0 + 2, 0.0)).color(col("botR"))
    d += elm.Ground().at((x0 + 2, 0.0))
    txt = {"on": "导通", "off": "断开", "pwm": "PWM\n20 kHz"}
    for name, x, y1, y0, side in [(names[0], xl, 6.0, 3.0, "left"), (names[2], xl, 3.0, 0.0, "left"),
                                  (names[1], xr, 6.0, 3.0, "right"), (names[3], xr, 3.0, 0.0, "right")]:
        st = sw.get(name, "off")
        c = col(name)
        d += elm.Line().endpoints((x, y1), (x, y1 - 0.5)).color(c)
        if st == "on":
            d += elm.Line().endpoints((x, y1 - 0.5), (x, y0 + 0.5)).color(c)
            d += elm.Dot(radius=0.08).at((x, y1 - 0.5)).color(c)
            d += elm.Dot(radius=0.08).at((x, y0 + 0.5)).color(c)
        elif st == "pwm":
            d += elm.Switch().endpoints((x, y1 - 0.5), (x, y0 + 0.5)).color(EMPH)
        else:
            d += elm.Switch().endpoints((x, y1 - 0.5), (x, y0 + 0.5)).color(OFF)
        d += elm.Line().endpoints((x, y0 + 0.5), (x, y0)).color(c)
        dx = -0.45 if side == "left" else 0.45
        if name in diodes:
            xd = x + (-1.0 if side == "left" else 1.0)
            d += elm.Line().endpoints((x, y1 - 0.25), (xd, y1 - 0.25)).color(color)
            d += elm.Diode().endpoints((xd, y0 + 0.25), (xd, y1 - 0.25)).color(color)
            d += elm.Line().endpoints((xd, y0 + 0.25), (x, y0 + 0.25)).color(color)
            dx = -1.4 if side == "left" else 1.4
        tc = EMPH if st == "pwm" else (c if st == "on" else OFF)
        lab = f"{name}\n{txt[st]}" if name not in diodes else f"{name} 断开\n体二极管导通"
        d += elm.Label().at((x + dx, (y1 + y0) / 2)).label(lab, halign="right" if side == "left" else "left",
                                                          color=color if name in diodes else tc, fontsize=10)
    d += elm.Dot().at((xl, 3.0)).label("A", loc="left", ofst=0.1)
    d += elm.Dot().at((xr, 3.0)).label("B", loc="right", ofst=0.1)
    d += elm.Motor().endpoints((xl, 3.0), (xr, 3.0)).color(col("motor")).label(motor_label, loc="top")
    d += elm.Label().at((x0 + 2, -1.3)).label(title)


def fig_p1_4():
    """图 25-p1-4：调速：S1 以 20 kHz 开合（PWM），S4 一直闭合，S2、S3 断开。"""
    with drawing(fontsize=11) as d:
        _hb(d, 0, {"S1": "pwm", "S4": "on"}, "S1 做 PWM（每秒开合两万次），S4 一直闭合\n电机感受到的是平均电压",
            {"topL", "motor", "S4", "botR"}, motor_label="M　电流 →")
    save_schem(d, N, "25_p1_4_pwm.png")


def _drv(d, x0=0.0, ilim=None, in1="IN1", in2="IN2"):
    """DRV8871 接法：IN1、IN2 接单片机；VM 接 +12 V 并 0.1 µF 与储能电容 C_B；OUT1、OUT2 接电机；ILIM 经 R_ILIM 接地。"""
    ic = elm.Ic(pins=[elm.IcPin(name="IN2", side="left"), elm.IcPin(name="IN1", side="left"),
                      elm.IcPin(name="OUT2", side="right"), elm.IcPin(name="OUT1", side="right"),
                      elm.IcPin(name="VM", side="top"),
                      elm.IcPin(name="GND", side="bottom"), elm.IcPin(name="ILIM", side="bottom")],
                pinspacing=1.2, edgepadW=1.0, size=(4.2, 3.4)).label("DRV8871", "center", fontsize=12, ofst=(0, -0.6)).right().at((x0, 0))
    d += ic
    A = ic.absanchors
    xr = A["OUT1"][0] + 1.6
    d += elm.Line().endpoints(A["OUT1"], (xr, A["OUT1"][1]))
    d += elm.Line().endpoints(A["OUT2"], (xr, A["OUT2"][1]))
    d += elm.Motor().endpoints((xr, A["OUT1"][1]), (xr, A["OUT2"][1])).label("M", "right")
    yt = A["VM"][1] + 1.2
    yb = A["GND"][1] - 2.6
    xc1, xc2 = xr + 2.0, xr + 3.8
    d += elm.Line().endpoints(A["VM"], (A["VM"][0], yt))
    d += elm.Line().endpoints((A["VM"][0], yt), (xc2, yt))
    d += elm.Vdd().at((A["VM"][0], yt)).label("+12 V（VM）")
    d += elm.Dot().at((xc1, yt)); d += elm.Dot().at((xc1, yb))
    d += elm.Capacitor().endpoints((xc1, yt), (xc1, yb))
    d += elm.Label().at((xc1 - 0.55, (yt + yb) / 2)).label("0.1 µF", halign="right", fontsize=10)
    d += elm.Capacitor(polar=True).endpoints((xc2, yt), (xc2, yb))
    d += elm.Label().at((xc2 + 0.45, (yt + yb) / 2)).label("$C_B$\n储能", halign="left", fontsize=10)
    d += elm.Line().endpoints(A["GND"], (A["GND"][0], yb))
    d += elm.Line().endpoints((A["GND"][0], yb), (xc2, yb))
    d += elm.Ground().at((A["GND"][0], yb))
    ri = ilim or ("$R_{ILIM}$", "black")
    d += elm.Resistor().endpoints(A["ILIM"], (A["ILIM"][0], yb)).color(ri[1])
    d += elm.Dot().at((A["ILIM"][0], yb))
    d += elm.Label().at((A["ILIM"][0] + 0.4, (A["ILIM"][1] + yb) / 2)).label(ri[0], halign="left", color=ri[1], fontsize=10)
    xl = A["IN1"][0] - 1.8
    for k, t in (("IN1", in1), ("IN2", in2)):
        d += elm.Line().endpoints((xl, A[k][1]), A[k])
        d += elm.Dot(open=True).at((xl, A[k][1])).label(t, "left")
    d += elm.Label().at((xl - 0.3, A["IN1"][1] + 0.8)).label("来自单片机", halign="right", fontsize=10)
    return A


def fig_p2_4():
    """图 25-p2-4：DRV8871 的接法。"""
    with drawing(fontsize=11) as d:
        _drv(d)
    save_schem(d, N, "25_p2_4_drv8871.png")


def fig_p2_5():
    """图 25-p2-5：驱动、刹车、滑行三种状态的电流路径（Q 记号同图 25-p2-1）。"""
    q = ("Q1", "Q2", "Q3", "Q4")
    with drawing(fontsize=11) as d:
        _hb(d, 0, {"Q1": "on", "Q4": "on"}, "(a) 驱动：Q1、Q4 导通\n电机两端为 $V_M$",
            {"topL", "Q1", "motor", "Q4", "botR"}, names=q, motor_label="M　电流 →")
        _hb(d, 8.5, {"Q3": "on", "Q4": "on"}, "(b) 刹车：Q3、Q4 导通\n电机两端被短接（慢衰减）",
            {"Q3", "Q4", "motor", "botL", "botR"}, names=q, motor_label="M　电流 →")
        _hb(d, 18.0, {}, "(c) 滑行：四管全关\n电流经 Q3、Q2 体二极管回灌电源（快衰减）",
            {"topR", "motor", "botL"}, names=q, diodes=("Q2", "Q3"), motor_label="M　电流 →")
    save_schem(d, N, "25_p2_5_drive_brake_coast.png")


def fig_p3_3():
    """图 25-p3-3：DRV8871 的 ILIM 引脚经 R_ILIM（32 kΩ，典型 2 A）接地。"""
    print(f"[数值] R_ILIM = 32 kΩ → I_TRIP 典型 {64/32:.2f} A")
    with drawing(fontsize=11) as d:
        _drv(d, ilim=("$R_{ILIM}$\n32 kΩ\n（约 2 A）", EMPH))
    save_schem(d, N, "25_p3_3_ilim.png")


def fig_p3_4():
    """图 25-p3-4：死区扫描的示意模型：同一侧上下两只管子 + 走线电感 20 nH，直通电流的路径。"""
    with drawing(fontsize=11) as d:
        x = 0.0
        d += elm.Vdd().at((x, 9.0)).label(f"{sim.VM:.0f} V")
        d += elm.Inductor2().endpoints((x, 9.0), (x, 7.4)).color(BAD)
        d += elm.Label().at((x - 0.5, 8.2)).label(f"走线电感\n{sim.L_S*1e9:.0f} nH", halign="right", fontsize=10)
        d += elm.Resistor().endpoints((x, 7.4), (x, 5.8)).color(BAD)
        d += elm.Label().at((x - 0.5, 6.6)).label(f"走线与电源内阻\n{sim.R_S*1e3:.0f} mΩ", halign="right", fontsize=10)
        d += elm.Switch().endpoints((x, 5.8), (x, 3.6)).color(BAD)
        d += elm.Label().at((x - 0.5, 4.7)).label("上管（IRLZ44N，25 mΩ）\nt = 0 开始关断", halign="right", fontsize=10)
        d += elm.Dot().at((x, 3.6))
        d += elm.Line().endpoints((x, 3.6), (x + 2.4, 3.6)).linestyle("--").color(OFF)
        d += elm.Label().at((x + 2.6, 3.6)).label("接电机（模型里不算）", halign="left", color=OFF, fontsize=10)
        d += elm.Switch().endpoints((x, 3.6), (x, 1.4)).color(BAD)
        d += elm.Label().at((x - 0.5, 2.5)).label("下管（IRLZ44N，25 mΩ）\n等一个死区再开始导通", halign="right", fontsize=10)
        d += elm.Line().endpoints((x, 1.4), (x, 0.8)).color(BAD)
        d += elm.Ground().at((x, 0.8))
        d += elm.Label().at((x + 0.5, 6.6)).label("直通电流 ↓", halign="left", color=BAD, fontsize=11)
        d += elm.Label().at((x, -0.6)).label(f"每只管子开 / 关过渡 {sim.T_SW*1e9:.0f} ns；两只管子同时半通时电流从电源直接流到地", fontsize=10)
    save_schem(d, N, "25_p3_4_shoot_model.png")


def fig_p3_5():
    """图 25-p3-5：防反接二极管串在电源入口，回灌电流无处可去；补救：加大 C_B、在 V_M 上并 TVS 管。"""
    with drawing(fontsize=11) as d:
        d += elm.SourceV().endpoints((0, 0), (0, 3.0))
        d += elm.Label().at((-0.7, 1.5)).label("电源", halign="right")
        d += elm.Diode().endpoints((0, 3.0), (3.0, 3.0)).label("防反接二极管", "top")
        d += elm.Line().endpoints((3.0, 3.0), (9.6, 3.0))
        d += elm.Dot().at((4.6, 3.0)).label("$V_M$", "top")
        for xx, e_, lab in ((4.6, elm.Capacitor(polar=True), "$C_B$\n加大、耐压留余量"), (8.0, elm.Zener(), "TVS 管")):
            d += elm.Dot().at((xx, 0))
            if xx == 8.0:
                d += elm.Dot().at((xx, 3.0))
                d += e_.endpoints((xx, 0), (xx, 3.0)).color(EMPH)
            else:
                d += e_.endpoints((xx, 3.0), (xx, 0)).color(EMPH)
            d += elm.Label().at((xx + 0.85, 1.5)).label(lab, halign="left", color=EMPH, fontsize=10)
        d += (hb := module("H 桥 + 电机", ("VM", "GND"), (), w=2.6).right().anchor("VM").at((11.2, 3.0)))
        d += elm.Line().endpoints((9.6, 3.0), hb.absanchors["VM"])
        g = hb.absanchors["GND"]
        d += elm.Line().endpoints(g, (10.2, g[1])); d += elm.Line().endpoints((10.2, g[1]), (10.2, 0))
        d += elm.Line().endpoints((0, 0), (10.2, 0))
        d += elm.Ground().at((2.0, 0))
        d += elm.Label().at((7.0, 4.3)).label("← 滑行时的回灌电流", color=BAD, fontsize=10)
        d += elm.Label().at((1.5, 4.3)).label("二极管挡住，回不到电源", color=BAD, fontsize=10)
    save_schem(d, N, "25_p3_5_backfeed.png")


def fig_p3_6():
    """图 25-p3-6：练习 4：24 V、8 A 电机用分立 H 桥时要自己补的部分（框图）。"""
    with drawing(fontsize=11) as d:
        d += (u := module("半桥驱动芯片\n（带自举）×2", ("PWM", "关断"), ("AH", "AL", "BH", "BL"), w=3.0).right().at((0, 0)))
        U = u.absanchors
        hb = elm.Ic(pins=[elm.IcPin(name=n, side="left") for n in ("BL", "BH", "AL", "AH")]
                    + [elm.IcPin(name="B", side="right"), elm.IcPin(name="A", side="right"),
                       elm.IcPin(name="VM", side="top"), elm.IcPin(name="低边", side="bottom")],
                    pinspacing=1.0, edgepadW=1.2, size=(3.6, 5.0)).label("分立 H 桥\nQ1–Q4", "center", fontsize=11).right().anchor("AH").at((U["AH"][0] + 2.0, U["AH"][1]))
        d += hb
        H = hb.absanchors
        for k in ("AH", "AL", "BH", "BL"):
            d += elm.Line().endpoints(U[k], H[k])
        d += elm.Line().endpoints(H["A"], (H["A"][0] + 1.2, H["A"][1]))
        d += elm.Line().endpoints(H["B"], (H["B"][0] + 1.2, H["B"][1]))
        d += elm.Motor().endpoints((H["A"][0] + 1.2, H["A"][1]), (H["A"][0] + 1.2, H["B"][1])).label("M\n8 A", "right")
        yt = H["VM"][1] + 1.0
        d += elm.Line().endpoints(H["VM"], (H["VM"][0], yt))
        d += elm.Vdd().at((H["VM"][0], yt)).label("24 V")
        xc = H["A"][0] + 4.0
        d += elm.Line().endpoints((H["VM"][0], yt), (xc, yt))
        ys = H["低边"][1] - 1.0
        yg = ys - 2.6
        d += elm.Line().endpoints(H["低边"], (H["低边"][0], ys))
        d += elm.Dot().at((H["低边"][0], ys))
        d += elm.Resistor().endpoints((H["低边"][0], ys), (H["低边"][0], yg)).color(EMPH)
        d += elm.Label().at((H["低边"][0] + 0.4, ys - 1.0)).label("采样电阻", halign="left", color=EMPH, fontsize=10)
        d += elm.Ground().at((H["低边"][0], yg))
        d += elm.Capacitor(polar=True).endpoints((xc, yt), (xc, yg)).color(EMPH)
        d += elm.Line().endpoints((H["低边"][0], yg), (xc, yg))
        d += elm.Label().at((xc + 0.45, (yt + yg) / 2)).label("储能电容\n（更大、更靠近桥）", halign="left", color=EMPH, fontsize=10)
        xs = H["低边"][0]
        d += (op := elm.Opamp(leads=True).left().anchor("in2").at((xs - 1.2, ys)).color(EMPH))
        d += elm.Line().endpoints((xs, ys), op.in2).color(EMPH)
        d += elm.Line().endpoints(op.in1, (op.in1[0] + 0.4, op.in1[1])).color(EMPH)
        d += elm.Line().endpoints((op.in1[0] + 0.4, op.in1[1]), (op.in1[0] + 0.4, op.in1[1] - 1.0)).color(EMPH)
        d += elm.Dot(open=True).at((op.in1[0] + 0.4, op.in1[1] - 1.0)).color(EMPH)
        d += elm.Label().at((op.in1[0] + 0.4, op.in1[1] - 1.45)).label("门限电压", color=EMPH, fontsize=10)
        xk = U["关断"][0] - 0.7
        d += elm.Line().endpoints(op.out, (xk, op.out[1])).color(EMPH)
        d += elm.Line().endpoints((xk, op.out[1]), (xk, U["关断"][1])).color(EMPH)
        d += elm.Line().endpoints((xk, U["关断"][1]), U["关断"]).color(EMPH)
        d += elm.Label().at((op.center[0], op.center[1] - 1.5)).label("比较器：超限就关断", color=EMPH, fontsize=10)
        d += elm.Line().endpoints((U["PWM"][0] - 2.0, U["PWM"][1]), U["PWM"])
        d += elm.Dot(open=True).at((U["PWM"][0] - 2.0, U["PWM"][1])).label("单片机 PWM", "left")
        d += elm.Label().at((U["AH"][0] + 1.0, U["AH"][1] + 0.4)).label("栅极（含死区）", fontsize=9)
    save_schem(d, N, "25_p3_6_ex4_discrete.png")


if __name__ == "__main__":
    fig_p1_4(); fig_p2_4(); fig_p2_5(); fig_p3_3(); fig_p3_4(); fig_p3_5(); fig_p3_6()
