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
