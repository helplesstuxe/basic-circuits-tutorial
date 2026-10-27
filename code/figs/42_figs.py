"""42 流量计信号链总览：全部配图。
运行：/workspace/circuits-venv/bin/python code/figs/42_figs.py
数值全部来自 code/42_sim.py（必要时现算并打印），图上的每个数字都在终端打印。
图片输出到 42-flowmeter-signal-chains/img/，不写仓库根目录，不写 txt/csv。
"""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import figstyle as fs; from figstyle import C, LS
import schem; from schem import elm
import lab_schem as L


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


S = _load("sim42", "code/42_sim.py")
F35 = _load("figs35", "code/figs/35_figs.py")
Breadboard, BB_RAIL_Y, BB_WIRE = F35.Breadboard, F35.BB_RAIL_Y, F35.BB_WIRE
BB_WIRE["p5"] = "#d62728"          # 只在本脚本内存里加一种颜色：Arduino +5 V 轨用红线（不改 35_figs.py）
N = "42"
GRAY = "#555555"
LABD = {r["f"]: r for r in S.LAB}
LAB483 = {r["f"]: r for r in S.LAB_483}

# ======================================================================
# page1
# ======================================================================
CHAINS = [
    ("电磁", "amp", [("线圈恒流换向", "39"), ("电极 + 仪表放大\n增益 ≤ 10", "30"), ("带通", "33"),
                    ("同步检波", "38"), ("ADC + 4–20 mA", "41")]),
    ("超声时差", "time", [("猝发激励\n40 kHz", ""), ("接收放大", "31/32"), ("带通", "33"),
                       ("程控增益 / AGC", "35"), ("门限 + 过零\n计时", "37")]),
    ("涡街", "freq", [("压电片\n（电荷）", ""), ("电荷放大", "32"), ("跟踪滤波", "34"),
                    ("AGC", "35"), ("施密特 + 计数", "36")]),
    ("涡轮", "freq", [("磁电 / 霍尔\n拾取", ""), ("施密特整形", "36"), ("计数", "36"),
                    ("÷ K 系数", ""), ("4–20 mA", "41")]),
    ("热式", "amp", [("RTD 恒流", "39"), ("电桥 + 仪表放大", "30"), ("恒温差控制", "40"),
                    ("加热功率 → 流量", "40"), ("4–20 mA", "41")]),
    ("差压", "amp", [("孔板差压", ""), ("电桥 + 仪表放大", "30"), ("ADC", ""),
                    ("开方", "本节"), ("4–20 mA", "41")]),
]
KIND_FC = dict(amp=C["fill"], freq=C["fill2"], time="#e5f4ec")
KIND_NAME = dict(amp="幅度型（怕漂移、怕共模）", freq="频率型（怕丢脉冲、多计脉冲）", time="时间型（怕触发点漂）")


def p1_1():
    fig, ax = fs.diagram(13.2, 7.4)
    xs = [3.1, 5.3, 7.5, 9.7, 11.9]
    for i, (name, kind, blocks) in enumerate(CHAINS):
        y = 6.55 - i * 1.12
        ax.text(0.15, y, name, ha="left", va="center", fontsize=11, weight="bold")
        ax.text(0.15, y - 0.36, KIND_NAME[kind].split("（")[0], ha="left", va="center", fontsize=8, color=GRAY)
        prev = None
        for x, (txt, node) in zip(xs, blocks):
            b = fs.box(ax, x, y, txt, w=1.95, h=0.78, fc=KIND_FC[kind], fs=8.5)
            if node:
                ax.text(x + 0.92, y + 0.36, node, ha="right", va="top", fontsize=7.5, color=C["vin"], weight="bold")
            if prev:
                fs.arrow(ax, prev["r"], b["l"])
            prev = b
        ax.plot([1.45, xs[0] - 0.98], [y, y], color=C["edge"], lw=1.0)
    hs = [plt.Rectangle((0, 0), 1, 1, fc=KIND_FC[k], ec=C["edge"]) for k in ("amp", "freq", "time")]
    ax.legend(hs, [KIND_NAME[k] for k in ("amp", "freq", "time")], loc="lower center", bbox_to_anchor=(0.5, -0.06),
              ncol=3, fontsize=8.5, frameon=False)
    ax.text(13.1, 7.25, "方框右上角蓝字 = 前面讲过它的节点编号", ha="right", fontsize=8.5, color=C["vin"])
    fs.save(fig, N, "42_p1_1_six_chains.png")
    print("[图 42-p1-1] 六条信号链，节点编号：", [[b[1] for b in c[2]] for c in CHAINS])


def p1_2():
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.3))
    # 幅度：电磁流量计电极信号（灵敏度 175 µV/(m/s)，峰峰值 = 2 × 峰值？用 sim 的 em_signal）
    vs = (0.5, 1.0, 15.0)
    pp = [S.em_signal(v, 175e-6) * 1e3 for v in vs]
    ax = axs[0]
    ax.bar([f"{v:g} m/s" for v in vs], pp, color=C["vin"])
    for i, p in enumerate(pp):
        ax.text(i, p * 1.15, f"{p:.3g} mV", ha="center", fontsize=8.5)
        print(f"  电磁电极信号（未放大，峰峰值） {vs[i]} m/s → {p:.3g} mV")
    ax.set_yscale("log"); ax.set_ylim(0.05, 30)
    ax.set_title("幅度型：电磁电极信号", fontsize=10)
    fs.axlabels(ax, "流速", "", "峰峰值", "mV")
    # 频率：涡街
    ax = axs[1]
    v = np.linspace(0, 3.2, 50)
    ax.plot(v, S.VX_ST * v / S.VX_D, **LS["vout"])
    for vv, ff in zip(S.VX_V, S.VX_F):
        fs.mark(ax, vv, ff, f"{ff:.0f} Hz", dy=4)
    ax.set_title("频率型：涡街（St = 0.2，d = 10 mm）", fontsize=10)
    fs.axlabels(ax, "流速", "m/s", "漩涡频率", "Hz")
    # 时间：超声
    ax = axs[2]
    t1, dt = S.US_T1 * 1e6, S.US_DT * 1e6
    ax.barh(["单程飞行时间", "顺逆流时间差 Δt"], [t1, dt], color=[C["fb"], C["bad"]])
    ax.text(t1 * 0.5, 0, f"{t1:.0f} µs", ha="center", va="center", color="white", fontsize=9)
    ax.text(dt + 15, 1, f"{dt:.2f} µs", ha="left", va="center", fontsize=9)
    ax.set_xlim(0, 700)
    ax.set_title("时间型：空气超声（L = 0.2 m，3 m/s）", fontsize=10)
    fs.axlabels(ax, "时间", "µs", "", "")
    print(f"  超声 单程 {t1:.0f} µs，Δt {dt:.2f} µs")
    fig.tight_layout()
    fs.save(fig, N, "42_p1_2_three_kinds.png")


def p1_3():
    fig, ax = fs.diagram(13, 3.0)
    fig.set_size_inches(10.4, 2.4)
    y = 2.0
    items = [("12 V 电脑风扇\n（扇叶 = 涡轮）", C["fill2"]), ("测速线\n开集电极", C["fill2"]),
             ("宽带通\n0.78–3108 Hz", C["fill"]), ("LM393 施密特\n（36 节）", C["fill"]),
             ("Arduino D2\n测周期 → 流量", "#e5f4ec"), ("41 节发送板\nV→I", C["fill"]),
             ("250 Ω\n万用表读数", "#e5f4ec")]
    xs = np.linspace(1.0, 12.0, len(items))
    prev = None
    for x, (t, fc) in zip(xs, items):
        b = fs.box(ax, x, y, t, w=1.66, h=1.05, fc=fc, fs=9)
        if prev:
            fs.arrow(ax, prev["r"], b["l"])
        prev = b
    vals = ["每转 2 个脉冲", "0 / 5 V 方波", "中点参考 V_MID 2.5 V", "门限 2.61 / 2.38 V",
            f"{S.F_FS:.0f} Hz → 20 mA", "回路电流", f"20 mA → {LABD[100.0]['v250']:.2f} V"]
    for x, t in zip(xs, vals):
        ax.text(x, y - 0.85, t, ha="center", va="top", fontsize=8.5, color=C["vin"])
    ax.text(6.5, 0.35, "page4 的实验：用风扇转速当「流量」，走一遍「频率型」流量计的整条信号链",
            ha="center", fontsize=10.5, color=GRAY)
    fs.save(fig, N, "42_p1_3_lab_preview.png")
    print("[图 42-p1-3] 标注：", vals)


# ======================================================================
# page2
# ======================================================================
def p2_1():
    """电磁链：信号在每一级的峰峰值（15 m/s 与 0.5 m/s）。"""
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    stages = ["电极", "仪表放大 ×10", f"第二级 ×{S.EM_G2:.1f}"]
    hi = [S.em_signal(15) * 1e3, S.em_signal(15) * S.EM_G1 * 1e3, S.em_signal(15) * S.EM_G1 * S.EM_G2 * 1e3]
    lo = [S.em_signal(0.5) * 1e3, S.em_signal(0.5) * S.EM_G1 * 1e3, S.em_signal(0.5) * S.EM_G1 * S.EM_G2 * 1e3]
    x = np.arange(3)
    ax.plot(x, hi, **LS["vout"], marker="o", label="15 m/s（满量程）")
    ax.plot(x, lo, **LS["vin"], marker="s", label="0.5 m/s（小流量）")
    for i in range(3):
        fs.mark(ax, i, hi[i], (f"{hi[i]:.0f} mV" if hi[i] > 100 else f"{hi[i]:.3g} mV"), dx=6, dy=6)
        fs.mark(ax, i, lo[i], f"{lo[i]:.3g} mV", dx=6, dy=-13)
    fs.ref_h(ax, 2000, "ADC 想要的 2.0 V 峰峰值", x=0.02, ha="left")
    ax.set_yscale("log"); ax.set_ylim(0.05, 8000); ax.set_xticks(x, stages); ax.set_xlim(-0.3, 2.6)
    fs.axlabels(ax, "信号链的级", "", "峰峰值", "mV")
    ax.legend(loc="center right", fontsize=8.5)
    assert abs(hi[2] - 2000) < 1 and abs(S.EM_G2 - 38.1) < 0.05
    fs.save(fig, N, "42_p2_1_em_levels.png")


def p2_2():
    fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    ax = axs[0]
    dp = np.linspace(0, 10000, 400)
    q = [S.dp_flow(p)[0] * 1e3 for p in dp]
    ax.plot(dp, q, **LS["vout"], label="流量 ∝ √差压")
    ax.plot(dp, dp / 10000 * S.DP_Q[2], **LS["bad"], label="错把它当直线")
    for p, qq in zip(S.DP_PTS, S.DP_Q):
        fs.mark(ax, p, qq, f"{p} Pa → {qq:.3g} L/s", dy=0.0)
    fs.axlabels(ax, "差压", "Pa", "流量", "L/s"); ax.legend(fontsize=8, loc="lower right")
    ax.set_title("孔板：D = 50 mm、β = 0.5、水", fontsize=9.5)
    ax = axs[1]
    x = np.linspace(0, 1, 400)
    ax.plot(x * 100, np.sqrt(x) * 100, **LS["good"], label="正确：开方一次")
    ax.plot(x * 100, x ** 0.25 * 100, **LS["bad"], label="错误：开方两次")
    for p, (a, b) in S.DBL.items():
        if p in (0.10, 0.25):
            fs.mark(ax, p * 100, a * 100, f"{a*100:.1f} %", dy=0.0)
            fs.mark(ax, p * 100, b * 100, f"{b*100:.1f} %", dy=0.0)
    fs.axlabels(ax, "差压", "% 满量程", "显示流量", "% 满量程"); ax.legend(fontsize=8, loc="lower right")
    ax.set_title("同一路信号开方一次与两次", fontsize=9.5)
    fig.tight_layout()
    fs.save(fig, N, "42_p2_2_dp_sqrt.png")


def _frontend(d, holes=False, x0=0.0, y0=0.0):
    """风扇测速线 → 上拉 → 宽带通 → LM393 施密特 → D2。holes=True 时标面包板孔位。返回关键节点坐标。"""
    H = (lambda s: s) if holes else (lambda s: "")
    P = lambda x, y: (x0 + x, y0 + y)
    # 风扇内部：开集电极 NPN（虚线框）
    q = elm.BjtNpn(circle=True).theta(0).anchor("collector").at(P(0, 0))
    d += q
    qa = q.absanchors
    L.lab(d, (qa["collector"][0] + 0.15, qa["collector"][1] + 0.25), "C", fs_=9, color=GRAY)
    L.lab(d, (qa["base"][0] - 0.2, qa["base"][1] + 0.3), "B", ha="right", fs_=9, color=GRAY)
    L.lab(d, (qa["emitter"][0] + 0.15, qa["emitter"][1] - 0.2), "E", fs_=9, color=GRAY)
    d += elm.Line().at(qa["base"]).to((qa["base"][0] - 0.9, qa["base"][1]))
    L.lab(d, (qa["base"][0] - 1.1, qa["base"][1] - 1.1), "霍尔驱动\n每转 2 次导通", ha="center", fs_=8.5)
    d += elm.Line().at(qa["emitter"]).to((qa["emitter"][0], P(0, -2.6)[1]))
    d += elm.Ground().at((qa["emitter"][0], P(0, -2.6)[1]))
    L._dbox(d, *P(-3.4, -2.2), *P(0.5, 0.9))
    L.lab(d, P(-3.3, 1.25), "风扇内部（看不见）", fs_=8.5, color=GRAY)
    L.lab(d, P(0.15, -2.9), "黑线 1 脚" + H("\n→ tn10"), fs_=8.5)
    # TACH 节点
    T = P(2.2, 0)
    d += elm.Line().at(P(0, 0)).to(T)
    L.lab(d, P(1.1, -0.35), "测速线 3 脚" + H("\nb12→f14"), ha="center", fs_=8.5, color=C["vin"])
    d += elm.Dot().at(T)
    d += elm.Resistor().endpoints(T, (T[0], T[1] + 2.6))
    d += elm.Vdd().at((T[0], T[1] + 2.6)).label("+5 V（Arduino）", fontsize=9)
    L.lab(d, (T[0] + 0.35, T[1] + 1.3), "R_PU 10 kΩ" + H("\nj14→+5 V 轨"), fs_=8.5)
    # R_IN、C_HP → NB
    a = (T[0] + 3.0, T[1])
    d += elm.Resistor().endpoints(T, a)
    L.lab(d, ((T[0] + a[0]) / 2, T[1] - 0.6), "R_IN 100 kΩ" + H("\ng14–g18"), ha="center", fs_=8.5)
    NB = (a[0] + 2.6, a[1])
    d += elm.Capacitor().endpoints(a, NB)
    L.lab(d, ((a[0] + NB[0]) / 2, a[1] + 0.65), "C_HP 1 µF 无极性" + H("\nf18–f22"), ha="center", fs_=8.5)
    d += elm.Dot().at(NB)
    d += elm.Capacitor().endpoints(NB, (NB[0], NB[1] - 2.2))
    d += elm.Ground().at((NB[0], NB[1] - 2.2))
    L.lab(d, (NB[0] - 0.3, NB[1] - 1.1), "C_LP 1 nF" + H("\nj22→0 V"), ha="right", fs_=8.5)
    # R_HP → V_MID
    xh = NB[0] + 1.5
    d += elm.Line().at(NB).to((xh, NB[1]))
    d += elm.Dot().at((xh, NB[1]))
    M = (xh, NB[1] - 3.2)
    d += elm.Resistor().endpoints((xh, NB[1]), M)
    L.lab(d, (xh + 0.35, NB[1] - 1.6), "R_HP 100 kΩ" + H("\ng22–g26"), fs_=8.5)
    d += elm.Dot().at(M)
    d += elm.Resistor().endpoints(M, (M[0] - 2.8, M[1]))
    d += elm.Vdd().at((M[0] - 2.8, M[1])).label("+5 V", fontsize=9)
    L.lab(d, (M[0] - 1.4, M[1] - 0.6), "RM1 10 kΩ" + H("（i26→+5 V）"), ha="center", fs_=8.5)
    d += elm.Resistor().endpoints(M, (M[0], M[1] - 2.4))
    d += elm.Ground().at((M[0], M[1] - 2.4))
    L.lab(d, (M[0] - 0.35, M[1] - 1.2), "RM2 10 kΩ" + H("\nj26→0 V"), ha="right", fs_=8.5)
    L.lab(d, (M[0] + 0.35, M[1] + 0.35), "中点参考 V_MID 2.5 V", fs_=8.5, color=C["fb"])
    # LM393：IN− 接 NB，IN+ 接 REF（反相施密特）
    xo = xh + 5.0
    op = elm.Opamp(leads=True).theta(0).anchor("in1").at((xo, NB[1]))
    d += op
    o = op.absanchors
    d += elm.Line().at((xh, NB[1])).to(o["in1"])
    L._pin(d, o["in1"], "2", dx=-0.2, dy=0.25)
    L._pin(d, o["in2"], "3", dx=-0.2, dy=-0.25)
    L._pin(d, o["out"], "1", dx=0.15, dy=0.25)
    L.lab(d, (o["in1"][0] + 0.75, (o["in1"][1] + o["in2"][1]) / 2), "LM393\nA 组", fs_=8.5)
    top, bot = (o["vd"], o["vs"]) if o["vd"][1] > o["vs"][1] else (o["vs"], o["vd"])
    d += elm.Line().at(top).to((top[0], top[1] + 0.6))
    d += elm.Vdd().at((top[0], top[1] + 0.6)).label("+12 V", fontsize=9)
    L._pin(d, top, "8", dx=0.25, dy=0.25)
    d += elm.Line().at(bot).to((bot[0], bot[1] - 0.5))
    d += elm.Ground().at((bot[0], bot[1] - 0.5))
    L._pin(d, bot, "4", dx=0.25, dy=-0.25)
    if holes:
        L.colnote(d, (top[0] + 0.45, top[1] + 0.35), "a30→+12 V\nb30–tn31 100 nF", "right", ofst=0.0)
        L.colnote(d, (bot[0] + 0.45, bot[1] - 0.45), "j33→0 V", "right", ofst=0.0)
    # REF：RR1/RR2 分 5 V，R_H 从输出拉回
    yin2 = o["in2"][1]
    R = (o["in2"][0] - 0.6, yin2 - 3.4)
    d += elm.Line().at(o["in2"]).to((R[0], yin2))
    d += elm.Line().at((R[0], yin2)).to(R)
    d += elm.Dot().at(R)
    d += elm.Resistor().endpoints(R, (R[0], R[1] - 2.4))
    d += elm.Ground().at((R[0], R[1] - 2.4))
    L.lab(d, (R[0] - 0.35, R[1] - 1.2), "RR2 10 kΩ" + H("\nj36→0 V"), ha="right", fs_=8.5)
    d += elm.Resistor().endpoints(R, (R[0] - 2.6, R[1]))
    d += elm.Vdd().at((R[0] - 2.6, R[1])).label("+5 V", fontsize=9)
    L.lab(d, (R[0] - 1.3, R[1] + 0.6), "RR1 10 kΩ" + H("（i36）"), ha="center", fs_=8.5)
    # 输出节点
    X = (o["out"][0] + 1.0, o["out"][1])
    d += elm.Line().at(o["out"]).to(X)
    d += elm.Dot().at(X)
    d += elm.Line().at(R).to((X[0], R[1]))
    d += elm.Resistor().endpoints((X[0], R[1]), X).label("", "top")
    L.lab(d, (X[0] + 0.35, (R[1] + X[1]) / 2), "R_H 100 kΩ" + H("\nh30–h36"), fs_=8.5)
    L.lab(d, (R[0] + 0.2, R[1] - 0.45), "门限 REF", fs_=8.5, color=C["fb"])
    Y = (X[0] + 1.6, X[1])
    d += elm.Line().at(X).to(Y).color(C["vout"]).linewidth(1.8)
    d += elm.Dot().at(Y)
    d += elm.Resistor().endpoints(Y, (Y[0], Y[1] + 2.6))
    d += elm.Vdd().at((Y[0], Y[1] + 2.6)).label("+5 V", fontsize=9)
    L.lab(d, (Y[0] + 0.35, Y[1] + 1.3), "R_OUT 4.7 kΩ" + H("\nj30→+5 V"), fs_=8.5)
    Z = (Y[0] + 1.6, Y[1])
    d += elm.Line().at(Y).to(Z).color(C["vout"]).linewidth(1.8)
    d += elm.Dot(open=True).at(Z)
    L.lab(d, (Z[0] + 0.2, Z[1]), "→ Arduino D2" + H("\n绿线 g30→D2"), fs_=9, color=C["vout"])
    if holes:
        L.colnote(d, (NB[0] + 0.1, NB[1] + 0.35), "第 22 列", "top", ofst=0.0)
        L.colnote(d, (T[0] - 0.1, T[1] - 0.45), "第 14 列", "bottom", ofst=0.0)
        L.colnote(d, (X[0] + 0.1, X[1] + 0.35), "第 30 列", "top", ofst=0.0)
        L.colnote(d, (o["in1"][0] - 0.6, o["in1"][1] + 0.55), "h22→g31", "top", ofst=0.0)
    return dict(T=T, NB=NB, M=M, R=R, X=X, Y=Y)


def p2_3():
    d = schem.drawing(fontsize=10)
    _frontend(d)
    schem.save_schem(d, N, "42_p2_3_frontend_schem.png")
    print("[图 42-p2-3] 前端原理图：R_PU 10k，R_IN 100k，C_HP 1µF，R_HP 100k，C_LP 1nF，RM 10k/10k，RR 10k/10k，R_H 100k，R_OUT 4.7k")


def p2_4():
    r = S.frontend(60.0, 0.5, 0.4, 2e-6, S.V5, keep_from=0.35)
    t = (r["t"] - r["t"][0]) * 1e3
    fig, axs = plt.subplots(2, 1, figsize=fs.SIZE["tall"], sharex=True)
    ax = axs[0]
    ax.plot(t, r["tach"], **LS["vin"], label="测速线（R_PU 上拉后）")
    ax.plot(t, r["nb"], **LS["vout"], label="带通后 NB")
    hi, lo, voh = S.schmitt_th()
    fs.ref_h(ax, hi, f"上门限 {hi:.2f} V"); fs.ref_h(ax, lo, f"下门限 {lo:.2f} V", x=0.55)
    fs.mark(ax, t[np.argmax(r["nb"])], r["nb_max"], f"{r['nb_max']:.2f} V", dy=0.25)
    fs.mark(ax, t[np.argmin(r["nb"])], r["nb_min"], f"{r['nb_min']:.2f} V", dy=-0.45)
    fs.axlabels(ax, "", "", "电压", "V"); ax.set_ylim(-0.4, 6.2)
    ax.legend(fontsize=8, loc="upper right", ncol=2)
    ax = axs[1]
    ax.plot(t, r["out"], **LS["third"], label="LM393 输出 → D2")
    fs.ref_h(ax, voh, f"高电平 {voh:.2f} V")
    fs.axlabels(ax, "时间", "ms", "电压", "V"); ax.set_ylim(-0.4, 6.2)
    ax.legend(fontsize=8, loc="center right")
    print(f"  60 Hz：NB {r['nb_min']:.2f}–{r['nb_max']:.2f} V，门限 {hi:.3f}/{lo:.3f} V，输出高 {voh:.3f} V")
    assert 1.1 < r["nb_min"] < lo and hi < r["nb_max"] < 3.9
    fig.tight_layout()
    fs.save(fig, N, "42_p2_4_frontend_wave.png")


# ======================================================================
# page3
# ======================================================================
def p3_1():
    fig, axs = plt.subplots(1, 2, figsize=fs.SIZE["pair"])
    ax = axs[0]
    p = np.linspace(0.006, 1, 400)
    e = [S.dp_err(x)[1] for x in p]
    ax.plot(p * 100, e, **LS["bad"], label="流量误差（% 读数）")
    for x, (efs, er) in S.DP_ERR.items():
        if x in (1.0, 0.25, 0.04, 0.01):
            fs.mark(ax, x * 100, er, f"{er:.2f} %", dy=0.0)
    ax.set_xscale("log"); ax.set_yscale("log")
    fs.axlabels(ax, "差压", "% 满量程", "流量误差", "% 读数")
    ax.set_title("差压误差固定 0.1 % 满量程时", fontsize=9.5); ax.legend(fontsize=8)
    ax = axs[1]
    x = np.linspace(0, 0.02, 400)
    ax.plot(x * 100, np.sqrt(x) * 100, **LS["bad"], label="纯开方")
    ax.plot(x * 100, S.s3051(x) * 100, **LS["vout"], label="3051S 低流量处理")
    fs.ref_v(ax, 0.6, "0.6 %"); fs.ref_v(ax, 0.8, "0.8 %")
    ax.text(1.0, 3.0, f"过渡段斜率 {S.S3051_SLOPE:.1f}", fontsize=8.5)
    fs.axlabels(ax, "差压", "% 满量程", "输出", "% 满量程"); ax.legend(fontsize=8, loc="lower right")
    ax.set_title("零点附近：开方曲线太陡", fontsize=9.5)
    print(f"  3051S 过渡段斜率 {S.S3051_SLOPE:.1f}")
    fig.tight_layout()
    fs.save(fig, N, "42_p3_1_dp_error.png")


def p3_3():
    f = np.logspace(-1, 4, 400)
    H = np.abs(S.bp_H(f))
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.semilogx(f, H, **LS["vout"], label="宽带通 |H|")
    g, fl, fh, f0, q = float(H.max()), S.BP_FL, S.BP_FH, S.BP_F0, S.BP_Q
    fs.ref_h(ax, g / np.sqrt(2), f"−3 dB：{g/np.sqrt(2):.3f}")
    fs.ref_v(ax, fl, f"{fl:.2f} Hz"); fs.ref_v(ax, fh, f"{fh:.0f} Hz")
    for x in (5, 60, 1000):
        fs.mark(ax, x, abs(S.bp_H(x)), f"{abs(S.bp_H(x)):.3f}", dy=0.05)
    ax.axvspan(10, 100, color=C["hi"], alpha=0.35, lw=0)
    ax.text(31, 0.12, "风扇 10–100 Hz", ha="center", fontsize=8.5)
    fs.axlabels(ax, "频率", "Hz", "增益", ""); ax.set_ylim(0, 0.65); ax.legend(fontsize=8, loc="lower center")
    assert abs(g - 0.512) < 0.001 and abs(fl - 0.78) < 0.01 and abs(fh - 3108) < 2
    fs.save(fig, N, "42_p3_3_bp_sweep.png")


def p3_4():
    f = np.linspace(0, 130, 1301)
    ma = [S.ma_of(x) for x in f]
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ax.plot(f, ma, **{**LS["cur"], "lw": 3.2}, label="程序设定的回路电流")
    ax.plot(f, 4 + 16 * np.clip(f, 0, None) / S.F_FS, **LS["good"], label="不切除、不限幅的直线")
    fs.ref_v(ax, S.F_CUT, f"切除 {S.F_CUT:.0f} Hz"); fs.ref_v(ax, S.F_FS, f"满量程 {S.F_FS:.0f} Hz")
    for x in (30, 50, 80):
        fs.mark(ax, x, S.ma_of(x), f"{S.ma_of(x):.1f} mA", dy=-1.6)
    ax.set_xlim(0, 130); ax.set_ylim(0, 27)
    fs.axlabels(ax, "测速频率", "Hz", "电流", "mA"); ax.legend(fontsize=8, loc="lower right")
    assert S.ma_of(3) == 4.0 and S.ma_of(120) == 20.0
    fs.save(fig, N, "42_p3_4_cutoff.png")


# ======================================================================
# page4
# ======================================================================
def _legend(bb, y=0.03):
    names = dict(pos="+12 V 线（橙）", p5="Arduino +5 V 线（红）", gnd="0 V 地线（黑）", sig="信号线（绿）")
    hs = [Line2D([], [], color=BB_WIRE[k], lw=2.4, label=names[k]) for k in ("pos", "p5", "gnd", "sig")]
    bb.ax.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, y), ncol=4, fontsize=8, frameon=False)


def bb42():
    bb = Breadboard(ncol=42, rails=dict(tp=("tp：+12 V", "pos"), tn=("tn：0 V", "gnd"), bp=("bp：0 V", "gnd"), bn=("bn：+5 V（Arduino）", "p5")),
                    figsize=(13, 7.0))
    bb.ax.set_ylim(-7.0, 15.4)
    bb.ax.set_xlim(-8.5, 48.5)
    HOP_T = [BB_RAIL_Y["tn"] - 0.32]
    HOP_B = [BB_RAIL_Y["bp"] + 0.32, BB_RAIL_Y["bn"] - 0.32]
    ax = bb.ax
    # 电源进线
    bb.wire(bb.ext((-2.4, 12.4), "+12 V（来自 2 号板 tp3）", "pos"), "tp1", "pos")
    bb.wire(bb.ext((-2.4, 10.0), "0 V（来自 2 号板 tn3）", "gnd"), "tn1", "gnd")
    bb.wire(bb.ext((-2.4, -2.0), "Arduino GND", "gnd"), "bp1", "gnd")
    bb.wire(bb.ext((-2.4, -4.4), "Arduino 5V", "p5"), "bn1", "p5")
    bb.wire("tn41", "bp41", "gnd")                                   # 上下 0 V 轨连通
    # LM317 调风扇电压
    def _pinfix(n0):                                                 # 插头引脚字：居中、缩小，免得挤在一起
        for t in ax.texts[n0 + 1:]:
            x, y = t.get_position()
            t.set_position((x - 0.18, y)); t.set_ha("center"); t.set_fontsize(6.0)
            t.set_bbox(dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.9))
    n0 = len(ax.texts)
    bb.multi("RV", {"1": "c1", "W": "c2", "3": "c3"}, "RV 2k", w=2.6, h=0.7, at=(2.0, 6.0))
    _pinfix(n0)
    bb.wire("a2", "tn2", "gnd")                                      # 滑动端接 0 V
    bb.wire("b3", "b5", "sig")                                       # 3 端 → ADJ
    n0 = len(ax.texts)
    bb.multi("U1", {"ADJ": "e5", "OUT": "e6", "IN": "e7"}, "LM317", w=2.8, h=0.75, at=(6.0, 4.0))
    _pinfix(n0)
    bb.wire("a7", "tp7", "pos", hops=HOP_T)
    bb.two("CIN", "c7", "c9", "C", "100n")
    bb.wire("a9", "tn9", "gnd")
    bb.two("RA", "c5", "c6", "R", "240")
    bb.wire("b6", "b11", "pos", bend=0.9)                            # OUT → 风扇 +V
    # 风扇插头
    n0 = len(ax.texts)
    bb.multi("FAN", {"GND": "e10", "+V": "e11", "TACH": "e12"}, "风扇 1-2-3 脚", w=3.0, h=0.75, at=(11.0, 4.0))
    _pinfix(n0)
    bb.wire("a10", "tn10", "gnd", hops=HOP_T)
    bb.two("CF", "c11", "c10", "CE", "100µ")
    bb.two("CF2", "d11", "d10", "C", "100n")
    bb.wire("b12", "f14", "sig", via=[(12.5, 8.5), (12.5, 2.5), (13.5, 2.5)])
    # 前端：上拉、宽带通
    bb.two("RPU", "j14", "bn14", "R", "10k", lpos=(-0.85, 0))
    bb.two("RIN", "g14", "g18", "R", "100k")
    bb.two("CHP", "f18", "f22", "C", "1µ")
    bb.two("RHP", "g22", "g26", "R", "100k")
    bb.two("RM1", "i26", "bn27", "R")
    bb.two("RM2", "j26", "bp25", "R")
    bb.two("CLP", "j22", "bp22", "C", "1n")
    bb.wire("h22", "g31", "sig", via=[(22.5, 1.5), (22.5, 2.5), (31.0, 2.5)])   # NB → g31（不走 h 行，让出 R_H）
    # LM393
    bb.dip8("U2", 30, "LM393")
    bb.wire("a30", "tp29", "pos")
    bb.two("CD", "b30", "tn31", "C", "100n")
    bb.wire("a32", "tn32", "gnd"); bb.wire("a33", "tn33", "gnd")       # B 组 6、5 脚接 0 V
    bb.wire("j33", "bp33", "gnd")
    bb.wire("g32", "g36", "sig", via=[(32.5, 2.5), (35.5, 2.5)])
    bb.two("RR1", "i36", "bn37", "R")
    bb.two("RR2", "j36", "bp35", "R")
    # 两对 10k 的标签挪到板子下方，用细线指回电阻本体，免得挤在一起
    for h1, h2, txt, xt in (("j26", "bp25", "RM2 10k", 24.2), ("i26", "bn27", "RM1 10k", 27.0),
                            ("j36", "bp35", "RR2 10k", 34.2), ("i36", "bn37", "RR1 10k", 37.0)):
        (xa, ya), (xb, yb) = bb.xy(h1), bb.xy(h2)
        ax.annotate(txt, xy=((xa + xb) / 2, (ya + yb) / 2), xytext=(xt, -5.0), fontsize=7.5, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", color="0.45", lw=0.7), zorder=9,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.9))
    bb.two("RH", "h30", "h36", "R", "100k")
    bb.two("ROUT", "j30", "bn31", "R", "4.7k")
    bb.wire("g30", bb.ext((29.5, -6.2), "→ Arduino D2", "sig", dx=-0.45), "sig", via=[(29.5, 2.0)], hops=HOP_B)
    # LM4040 → AREF
    bb.two("RZ", "j39", "bn39", "R", "1k", lpos=(-0.75, 0))
    bb.multi("U3", {"1": "f38", "K": "f39", "A": "f40"}, "LM4040", w=2.4, h=0.6, at=(39.0, 4.0))
    ax.plot([37.85, 40.15], [3.66, 3.66], color="white", lw=2.2, zorder=7)          # TO-92 平面（朝下方 = 朝自己）
    ax.annotate("TO-92 平面朝自己\n（朝图下方）", xy=(40.2, 3.7), xytext=(42.3, 6.6), fontsize=7.5, ha="left",
                arrowprops=dict(arrowstyle="->", color="0.3", lw=0.8), zorder=9,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.9))
    bb.wire("j40", "bp40", "gnd")
    bb.wire("g39", bb.ext((39.5, -6.2), "→ Arduino AREF", "sig", dx=0.45, ha="left"), "sig", via=[(39.5, 2.0)], hops=HOP_B)
    ax.text(39.0, 2.28, "g39", fontsize=6.5, ha="center", va="bottom", color=BB_WIRE["sig"], zorder=9,
            bbox=dict(boxstyle="round,pad=0.05", fc="white", ec="none", alpha=0.85))
    # 断言
    c = bb.connected
    assert c("RV.3", "U1.ADJ", "c5") and c("RV.W", "tn1")
    assert c("U1.IN", "tp1", "c7") and c("U1.OUT", "e11", "FAN.+V", "c11")
    assert c("FAN.GND", "tn1", "bp1", "f33")
    assert c("FAN.TACH", "j14", "g14") and c("bn14", "bn1", "bn27")
    assert c("f22", "g22", "g31", "f31", "j22")          # NB → 2 脚
    assert c("g26", "i26", "j26")                                              # V_MID
    assert c("f32", "g36", "i36", "j36") and c("f30", "j30", "g30")           # REF 与输出
    assert c("e30", "tp1") and c("e32", "e33", "tn1")                          # 8 脚 12 V，B 组 5、6 脚 0 V
    assert c("f39", "g39", "j39", "i39", "U3.K") and c("U3.A", "j40") and c("U3.A", "bp1") and not c("U3.1", "bp1") and not c("U3.1", "bn1")
    # 安全：+5 V 轨与 12 V、风扇电压、测速线互不相连；送 Arduino 的点不碰 12 V
    for a in ("bn1",):
        for b in ("tp1", "e11", "e12", "e5"):
            assert not c(a, b), f"{a} 与 {b} 短路"
    for a in ("g30", "g39"):
        for b in ("tp1", "e11", "e12", "f22", "bn1", "tn1"):
            assert not c(a, b), f"{a} 与 {b} 短路"
    pins = ["e5", "e6", "e7", "e10", "e11", "e12", "f30", "f31", "f32", "f33", "e30", "e31", "e32", "e33"]
    for i, a in enumerate(pins):
        for b in pins[i + 1:]:
            if any({a, b} <= g for g in ({"e6", "e11"}, {"e7", "e30"}, {"e10", "f33", "e32", "e33"})):
                continue
            assert not c(a, b), f"芯片引脚 {a} 与 {b} 短路"
    print("[图 42-p4-1] 面包板连线断言全部通过（+5 V 轨不碰 12 V；D2、AREF 不碰 12 V 和测速线）")
    # 测量点
    bb.probe("a11", "① 风扇电压", dy=0.3)
    bb.probe("h14", "② 测速线", dx=-0.3, dy=-0.9, ha="right")
    bb.probe("i22", "③ NB", dx=0.3, dy=-0.85)
    bb.probe("h26", "④ V_MID", dx=0.3, dy=-0.85)
    bb.probe("i30", "⑤ 输出", dx=-0.65, dy=-0.25, ha="right")
    bb.probe("i32", "⑥ REF", dx=0.3, dy=-0.85)
    bb.probe("i39", "⑦ AREF", dx=-0.3, dy=0.25, ha="right")
    bb.note(-7.8, 14.6, "1 号板（新搭）：LM317 调风扇电压 + 测速前端 + LM4040 基准；4–20 mA 发送部分仍用 41 节的 2 号板", fontsize=8.5)
    bb.note(-7.8, 13.7, "LM317 引脚（字面朝自己）：1 ADJ、2 OUT（散热片）、3 IN；风扇插头以 1-2-3 脚标记为准；C_HP 用无极性电容", fontsize=8.5)
    _legend(bb, y=0.035)
    fs.save(bb.fig, N, "42_p4_1_breadboard.png")
    return bb


def _lm317(d, holes=False, x0=0.0, y0=0.0):
    H = (lambda s: s) if holes else (lambda s: "")
    P = lambda x, y: (x0 + x, y0 + y)
    d += elm.Vdd().at(P(0, 0)).label("+12 V", fontsize=9)
    d += elm.Line().at(P(0, 0)).to(P(1.6, 0))
    d += elm.Dot().at(P(0.8, 0))
    d += elm.Capacitor().endpoints(P(0.8, 0), P(0.8, -2.0))
    d += elm.Ground().at(P(0.8, -2.0))
    L.lab(d, P(0.45, -1.0), "CIN\n100 nF" + H("\nc7–c9"), ha="right", fs_=8.5)
    u = schem.module("LM317", left=("IN",), right=("OUT",), w=2.4).theta(0).anchor("IN").at(P(1.6, 0))
    d += u
    ua = u.absanchors
    out = ua["OUT"]
    L.lab(d, (ua["IN"][0] + 0.15, ua["IN"][1] - 0.45), "3", fs_=8.5, color=GRAY)
    L.lab(d, (out[0] - 0.35, out[1] - 0.45), "2", fs_=8.5, color=GRAY)
    xadj = (ua["IN"][0] + out[0]) / 2
    yb = out[1] - 1.0
    adj = (xadj, yb)
    L.lab(d, (xadj + 0.15, yb + 0.3), "ADJ 1", fs_=8.5, color=GRAY)
    A = (xadj, yb - 1.2)
    d += elm.Line().at(adj).to(A)
    d += elm.Dot().at(A)
    xo = out[0] + 1.2
    d += elm.Line().at(out).to((xo, out[1]))
    d += elm.Dot().at((xo, out[1]))
    d += elm.Resistor().endpoints((xo, out[1]), (xo, A[1]))
    d += elm.Line().at((xo, A[1])).to(A)
    L.lab(d, (xo + 0.35, (out[1] + A[1]) / 2), "R_A 240 Ω" + H("\nc5–c6"), fs_=8.5)
    d += elm.Potentiometer().endpoints(A, (A[0], A[1] - 3.0))
    d += elm.Ground().at((A[0], A[1] - 3.0))
    L.lab(d, (A[0] - 0.55, A[1] - 1.5), "R_ADJ\n2 kΩ 电位器" + H("\nc3、c2；a2→0 V"), ha="right", fs_=8.5)
    F = (xo + 2.4, out[1])
    d += elm.Line().at((xo, out[1])).to(F).color(C["vout"]).linewidth(1.8)
    d += elm.Dot().at(F)
    d += elm.Capacitor(polar=True).endpoints(F, (F[0], F[1] - 2.2))
    d += elm.Ground().at((F[0], F[1] - 2.2))
    L.lab(d, (F[0] + 0.35, F[1] - 1.1), "CF 100 µF\n+ 100 nF" + H("\nc11(+)–c10"), fs_=8.5)
    L.lab(d, (F[0] + 0.2, F[1] + 0.4), "风扇 +V（2 脚）" + H("  b6→b11"), fs_=8.5, color=C["vout"])
    L.probe(d, F, "①", dx=1.6, dy=-0.6)
    return F


def p4_2(name="42_p4_2_schem_lab.png", holes=True, notes=None, tag="图 42-p4-2"):
    """holes=False 时不标孔位（直觉篇 / 参数篇对照用）。"""
    H = (lambda t: t) if holes else (lambda t: "")
    d = schem.drawing(fontsize=10)
    _lm317(d, holes=holes, x0=0, y0=4.2)
    L.title(d, (4.5, 6.4), "① 风扇电源：LM317 可调稳压（直流，不用 PWM）")
    r = _frontend(d, holes=holes, x0=3.0, y0=-5.0)
    L.title(d, (12.0, -1.6), "② 测速前端：上拉 → 宽带通 → LM393 施密特")
    L.probe(d, r["T"], "②", dx=-0.2, dy=1.2)
    L.probe(d, r["NB"], "③", dx=0.0, dy=1.1)
    L.probe(d, r["M"], "④", dx=0.8, dy=-0.7)
    L.probe(d, r["X"], "⑤", dx=0.0, dy=1.1)
    L.probe(d, r["R"], "⑥", dx=0.9, dy=-0.7)
    # LM4040
    x4, y4 = 26.5, 3.0
    d += elm.Vdd().at((x4, y4 + 2.4)).label("+5 V", fontsize=9)
    d += elm.Resistor().endpoints((x4, y4 + 2.4), (x4, y4))
    L.lab(d, (x4 + 0.35, y4 + 1.2), "R_Z 1 kΩ" + H("\nj39→+5 V"), fs_=8.5)
    d += elm.Dot().at((x4, y4))
    d += elm.Zener().endpoints((x4, y4 - 2.4), (x4, y4))
    d += elm.Ground().at((x4, y4 - 2.4))
    for k, t in enumerate((("LM4040 2.5 V（TO-92 平面朝自己）", "阴极 2 脚 f39", "阳极 3 脚 f40，j40 → 0 V", "1 脚 f38 悬空") if holes else ("LM4040 2.5 V（TO-92）", "阴极 2 脚 → R_Z、AREF", "阳极 3 脚 → 0 V", "1 脚悬空"))):
        L.lab(d, (x4 + 0.5, y4 - 0.6 - 0.45 * k), t, fs_=8.5)
    d += elm.Line().at((x4, y4)).to((x4 + 1.8, y4)).color(C["fb"]).linewidth(1.6)
    d += elm.Dot(open=True).at((x4 + 1.8, y4))
    L.lab(d, (x4 + 2.0, y4), "→ AREF" + H("\ng39"), fs_=9, color=C["fb"])
    L.probe(d, (x4, y4), "⑦", dx=-0.9, dy=0.6)
    L.title(d, (x4 + 0.8, 6.6), "③ ADC 基准 2.5 V")
    if notes is None:
        L.note(d, (-2.5, -14.2), "对照图 42-p4-1：灰色小字是孔位。+12 V 只接 LM317 输入（a7）和 LM393 的 8 脚（a30）；其余「+5 V」全是下方那条 Arduino 5 V 轨。")
        L.note(d, (-2.5, -14.9), "LM393 的 B 组不用：6、5 脚 a32、a33 → 0 V，7 脚空着。测速线绝不直接接 Arduino，只经过 LM393 再到 D2。")
        L.note(d, (-2.5, -15.6), "测量点：① 风扇电压　② 测速线　③ NB　④ V_MID　⑤ 输出　⑥ REF　⑦ AREF；黑表笔插 0 V 轨。")
    else:
        for n_, t in enumerate(notes):
            L.note(d, (-2.5, -14.2 - 0.7 * n_), t)
    schem.save_schem(d, N, name)
    print(f"[{tag}] " + ("带孔位的原理图，与图 42-p4-1 一一对应" if holes else "不标孔位的整机原理图"))


def p1_4():
    p4_2("42_p1_4_schem.png", holes=False, tag="图 42-p1-4", notes=(
        "+12 V 只接 LM317 输入和 LM393 的 8 脚；其余「+5 V」都来自 Arduino 的 5V 引脚。LM393 输出经 R_OUT 上拉到 5 V，再进 D2。",
        "D2 测出频率 → 程序换算成码 → D9 PWM 送到 41 节的发送板（图中未画），输出 4–20 mA。",
        "圆圈 ①～⑦ 是动手实验篇要量的点：① 风扇电压　② 测速线　③ NB　④ V_MID　⑤ 输出　⑥ REF　⑦ AREF。"))


def p3_2():
    p4_2("42_p3_2_schem.png", holes=False, tag="图 42-p3-2", notes=(
        "参数表里的元件：R_PU、R_IN、C_HP、R_HP、C_LP 在测速前端左半；RM1/RM2 给 V_MID 2.5 V；RR1/RR2 给门限 REF；R_H 是回差电阻。",
        "排查表里的点：① LM317 输出（风扇电压）、② 测速线、⑦ AREF；LM393 的 8 脚接 +12 V，4 脚接 0 V；LM4040 阴极接 R_Z 和 AREF。",
        "LM393 的 B 组不用：5、6 脚接 0 V，7 脚空着。测速线不直接接 Arduino，只经过 LM393 再到 D2。"))


def p4_3():
    """两块板 + Arduino 的系统连线。"""
    fig, ax = fs.diagram(12, 4.6)
    b1 = fs.box(ax, 2.0, 2.4, "1 号板（新搭）\nLM317 + 风扇\n测速前端 + LM4040", w=3.2, h=1.9, fs=9)
    ar = fs.box(ax, 6.0, 2.4, "Arduino Uno\nD2 测周期\n算流量 → 码\nD9 PWM", w=2.6, h=1.9, fc="#e5f4ec", fs=9)
    b2 = fs.box(ax, 10.0, 2.4, "2 号板（41 节原样）\nRC 滤波 → V→I\n250 Ω 接收电阻", w=3.2, h=1.9, fs=9)
    def ln(p, q, col, txt, dy):
        ax.annotate("", q, p, arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8))
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, txt, ha="center", fontsize=8.5, color=col)
    ln((3.6, 3.0), (4.7, 3.0), BB_WIRE["sig"], "LM393 输出 → D2", 0.12)
    ln((4.7, 2.5), (3.6, 2.5), BB_WIRE["sig"], "AREF ← LM4040", 0.12)
    ln((4.7, 1.9), (3.6, 1.9), BB_WIRE["p5"], "5V → bn1", 0.12)
    ln((7.3, 3.0), (8.4, 3.0), BB_WIRE["sig"], "D9 → j1", 0.12)
    ln((8.4, 2.5), (7.3, 2.5), BB_WIRE["sig"], "A0 ← j27", 0.12)
    ax.plot([0.4, 11.6], [0.55, 0.55], color="black", lw=2.0)
    ax.text(6.0, 0.15, "三处 0 V 必须连在一起：1 号板 bp1 ← Arduino GND → 2 号板 bp25；1 号板 tn1 ← 2 号板 tn3", ha="center", fontsize=8.5)
    for x in (2.0, 6.0, 10.0):
        ax.plot([x, x], [1.45, 0.55], color="black", lw=1.4)
    ax.annotate("", (1.2, 3.35), (8.8, 3.35), arrowprops=dict(arrowstyle="-|>", color=BB_WIRE["pos"], lw=1.8,
                connectionstyle="arc3,rad=0.25"))
    ax.text(5.0, 4.35, "+12 V：2 号板 tp3 → 1 号板 tp1（同一台 12 V 电源）", ha="center", fontsize=8.5, color=BB_WIRE["pos"])
    fs.save(fig, N, "42_p4_3_system.png")
    print("[图 42-p4-3] 两块板 + Arduino：D2、AREF、5V、D9、A0、+12 V、0 V")


def p4_4():
    """读者应读到的数：频率 → 回路电流 → 250 Ω 电压；以及 V5 写错时。"""
    fig, ax = plt.subplots(figsize=fs.SIZE["single"])
    ff = np.linspace(0, 120, 241)
    ax.plot(ff, [S.chain(x, S.V5, S.V5)["v250"] for x in ff], **LS["vout"], label="V5 = 5.00 V（程序与实际一致）")
    ax.plot(ff, [S.chain(x, S.V5, S.V5_EX)["v250"] for x in ff], **LS["bad"], label="实际 4.83 V，程序仍写 5.00")
    for x in (0.0, 50.0, 100.0):
        v = LABD[x]["v250"]
        fs.mark(ax, x, v, f"{v:.2f} V", dx=-34, dy=7)
    for x in (50.0, 100.0):
        v = LAB483[x]["v250"]
        fs.mark(ax, x, v, f"{v:.2f} V", dx=6, dy=-14)
    fs.ref_v(ax, S.F_CUT, "5 Hz 切除")
    ax.set_ylim(0, 5.8)
    fs.axlabels(ax, "测速频率", "Hz", "250 Ω 上的电压", "V"); ax.legend(fontsize=8, loc="lower right")
    fs.save(fig, N, "42_p4_4_expect.png")


# ---------- 图 42-p3-5：例 1 涡轮流量计前端（LM358 同相 ×34 + 高通 + 低通） ----------
def p3_5():
    """例 1 的电路：数值按 page3 例 1（1 + 33k/1k = 34，27k/1µF 高通 5.89 Hz，6.8k/10nF 低通 2341 Hz）。
    中点 4.5 V 用 15 kΩ / 9.1 kΩ 分 12 V（≈ 4.53 V），经 LM358 B 组跟随后低阻输出。"""
    fhp = 1 / (2 * np.pi * 27e3 * 1e-6); flp = 1 / (2 * np.pi * 6.8e3 * 10e-9); vmid = 12 * 9.1 / (15 + 9.1)
    G = 1 + 33 / 1
    # 施密特门限：本节 schmitt_th 的同一套方程，只把戴维南电压 2.5 V 换成 V_MID（内阻仍是 10k∥10k = 5 kΩ）
    rth = S.R_R1 * S.R_R2 / (S.R_R1 + S.R_R2)
    voh = (S.V5 / S.R_OUT + vmid / (S.R_H + rth)) / (1 / S.R_OUT + 1 / (S.R_H + rth))
    vu = (vmid / rth + voh / S.R_H) / (1 / rth + 1 / S.R_H)
    vl = (vmid / rth + S.VOL / S.R_H) / (1 / rth + 1 / S.R_H)
    vpk = G * 0.020                                     # 2 L/min 时的最小峰值（放大后）
    assert vmid - vpk < vl and vmid + vpk > vu          # 最小信号也能越过两条门限
    d = schem.drawing(fontsize=10)
    VM = C["fb"]
    # 拾取线圈（信号源）
    d += elm.SourceSin().endpoints((0, -2.6), (0, 0)).label("涡轮拾取线圈\n20–300 mV 峰\n30–450 Hz", loc="bottom", fontsize=9)
    d += elm.Ground().at((0, -2.6))
    # 高通：C_HP 串联，R_HP 拉到 V_MID
    A = (3.6, 0)
    d += elm.Capacitor().endpoints((0, 0), A)
    L.lab(d, (1.8, 0.65), "C_HP 1 µF", ha="center", fs_=9)
    d += elm.Dot().at(A)
    d += elm.Resistor().endpoints(A, (A[0], -2.6))
    L.lab(d, (A[0] + 0.35, -1.3), "R_HP 27 kΩ", fs_=9)
    d += elm.Line().at((A[0], -2.6)).to((A[0], -3.1)).color(VM)
    L.lab(d, (A[0], -3.45), "V_MID", ha="center", fs_=9, color=VM)
    # LM358 A 同相放大
    op = elm.Opamp(leads=True).theta(0).anchor("in2").at((5.6, 0))
    d += op
    o = op.absanchors
    d += elm.Line().at(A).to(o["in2"])
    L._pin(d, o["in2"], "3", dx=-0.2, dy=-0.25)
    L._pin(d, o["in1"], "2", dx=-0.2, dy=0.25)
    L._pin(d, o["out"], "1", dx=0.15, dy=0.25)
    L.lab(d, (o["in1"][0] + 0.75, (o["in1"][1] + o["in2"][1]) / 2), "LM358\nA 组", fs_=8.5)
    top, bot = (o["vd"], o["vs"]) if o["vd"][1] > o["vs"][1] else (o["vs"], o["vd"])
    L.lab(d, (top[0] + 0.2, top[1] + 0.3), "8 → +12 V", fs_=8, color=GRAY)
    L.lab(d, (bot[0] + 0.2, bot[1] - 0.3), "4 → GND", fs_=8, color=GRAY)
    # 反馈：RF 33k 从输出回 2 脚；RG 1k 从 2 脚到 V_MID
    xi = o["in1"][0] - 0.5; yi = o["in1"][1]; yf = yi + 1.8
    X = (o["out"][0] + 0.8, o["out"][1])
    d += elm.Line().at(o["in1"]).to((xi, yi))
    d += elm.Dot().at((xi, yi))
    d += elm.Line().at((xi, yi)).to((xi, yf))
    d += elm.Resistor().endpoints((xi, yf), (X[0], yf))
    L.lab(d, ((xi + X[0]) / 2, yf + 0.6), "R_F 33 kΩ", ha="center", fs_=9)
    d += elm.Line().at(o["out"]).to(X)
    d += elm.Dot().at(X)
    d += elm.Line().at(X).to((X[0], yf))
    d += elm.Resistor().endpoints((xi, yi), (xi - 2.4, yi))
    L.lab(d, (xi - 1.2, yi + 0.55), "R_G 1 kΩ", ha="center", fs_=9)
    d += elm.Line().at((xi - 2.4, yi)).to((xi - 2.4, yi + 0.6)).color(VM)
    L.lab(d, (xi - 2.4, yi + 0.95), "V_MID", ha="center", fs_=9, color=VM)
    # 低通：R_LP 6.8k 串联，C_LP 10 nF 到地
    B = (X[0] + 3.0, X[1])
    d += elm.Resistor().endpoints(X, B)
    L.lab(d, ((X[0] + B[0]) / 2, X[1] + 0.6), "R_LP 6.8 kΩ", ha="center", fs_=9)
    d += elm.Dot().at(B)
    d += elm.Capacitor().endpoints(B, (B[0], B[1] - 2.2))
    d += elm.Ground().at((B[0], B[1] - 2.2))
    L.lab(d, (B[0] - 0.35, B[1] - 1.3), "C_LP\n10 nF", ha="right", fs_=9)
    # 施密特（LM393 反相接法）：门限分压两端都改接 V_MID（10k∥10k = 5 kΩ），R_H 100 kΩ 正反馈
    cp = elm.Opamp(leads=True).theta(0).anchor("in1").at((B[0] + 4.2, B[1]))
    d += cp
    k = cp.absanchors
    d += elm.Line().at(B).to(k["in1"]).color(C["vout"]).linewidth(1.8)
    L._pin(d, k["in1"], "2", dx=-0.2, dy=0.25)
    L._pin(d, k["in2"], "3", dx=-0.2, dy=-0.25)
    L._pin(d, k["out"], "1", dx=0.15, dy=0.25)
    L.lab(d, (k["in1"][0] + 0.75, (k["in1"][1] + k["in2"][1]) / 2), "LM393", fs_=8.5)
    ktop, kbot = (k["vd"], k["vs"]) if k["vd"][1] > k["vs"][1] else (k["vs"], k["vd"])
    L.lab(d, (ktop[0] + 0.2, ktop[1] + 0.3), "8 → +12 V", fs_=8, color=GRAY)
    L.lab(d, (kbot[0] + 0.25, kbot[1] - 0.25), "4 → GND", fs_=8, color=GRAY)
    P = (k["in2"][0] - 0.8, k["in2"][1])
    d += elm.Line().at(k["in2"]).to(P)
    d += elm.Dot().at(P)
    xT = B[0] + 1.0
    d += elm.Resistor().endpoints(P, (xT, P[1]))
    L.lab(d, ((P[0] + xT) / 2, P[1] + 0.55), "R_T 5 kΩ", ha="center", fs_=9)
    d += elm.Line().at((xT, P[1])).to((xT, P[1] - 0.6)).color(VM)
    L.lab(d, (xT, P[1] - 0.95), "V_MID", ha="center", fs_=9, color=VM)
    O2 = (k["out"][0] + 0.9, k["out"][1]); yh = P[1] - 2.0
    d += elm.Line().at(k["out"]).to(O2)
    d += elm.Dot().at(O2)
    d += elm.Line().at(P).to((P[0], yh))
    d += elm.Resistor().endpoints((P[0], yh), (O2[0], yh))
    L.lab(d, ((P[0] + O2[0]) / 2, yh - 0.6), "R_H 100 kΩ", ha="center", fs_=9)
    d += elm.Line().at((O2[0], yh)).to(O2)
    d += elm.Resistor().endpoints(O2, (O2[0], O2[1] + 2.2))
    d += elm.Vdd().at((O2[0], O2[1] + 2.2)).label("+5 V", fontsize=9)
    L.lab(d, (O2[0] + 0.55, O2[1] + 1.1), "R_OUT 4.7 kΩ", fs_=9)
    Z = (O2[0] + 1.4, O2[1])
    d += elm.Line().at(O2).to(Z)
    d += elm.Dot(open=True).at(Z)
    L.lab(d, (Z[0] + 0.2, Z[1]), "→ Arduino D2", fs_=9)
    # 中点参考：15k / 9.1k 分 12 V，LM358 B 组跟随
    y0 = -7.6; xr = 0.0
    d += elm.Vdd().at((xr, y0 + 2.2)).label("+12 V", fontsize=9)
    d += elm.Resistor().endpoints((xr, y0 + 2.2), (xr, y0))
    L.lab(d, (xr - 0.55, y0 + 1.1), "R1 15 kΩ", ha="right", fs_=9)
    d += elm.Resistor().endpoints((xr, y0), (xr, y0 - 2.2))
    L.lab(d, (xr - 0.55, y0 - 1.1), "R2 9.1 kΩ", ha="right", fs_=9)
    d += elm.Ground().at((xr, y0 - 2.2))
    d += elm.Dot().at((xr, y0))
    d += elm.Line().at((xr, y0)).to((1.4, y0))
    d += elm.Dot().at((1.4, y0))
    d += elm.Capacitor(polar=True).endpoints((1.4, y0), (1.4, y0 - 2.2))
    L.lab(d, (1.75, y0 - 1.1), "10 µF", fs_=9)
    d += elm.Ground().at((1.4, y0 - 2.2))
    ob = elm.Opamp(leads=True).theta(0).anchor("in2").at((3.2, y0))
    d += ob
    b = ob.absanchors
    d += elm.Line().at((1.4, y0)).to(b["in2"])
    L._pin(d, b["in2"], "5", dx=-0.2, dy=-0.25)
    L._pin(d, b["in1"], "6", dx=-0.2, dy=0.25)
    L._pin(d, b["out"], "7", dx=0.15, dy=0.25)
    L.lab(d, (b["in1"][0] + 0.75, (b["in1"][1] + b["in2"][1]) / 2), "LM358\nB 组", fs_=8.5)
    yl = b["in1"][1] + 1.0; xo = b["out"][0] + 0.6
    d += elm.Line().at(b["in1"]).to((b["in1"][0] - 0.3, b["in1"][1]))
    d += elm.Line().at((b["in1"][0] - 0.3, b["in1"][1])).to((b["in1"][0] - 0.3, yl))
    d += elm.Line().at((b["in1"][0] - 0.3, yl)).to((xo, yl))
    d += elm.Line().at((xo, yl)).to((xo, b["out"][1]))
    d += elm.Line().at(b["out"]).to((xo + 1.0, b["out"][1])).color(VM)
    d += elm.Dot().at((xo, b["out"][1]))
    L.lab(d, (xo + 1.1, b["out"][1]), "V_MID ≈ 4.5 V\n（送到上面两个 V_MID）", fs_=9, color=VM)
    L.note(d, (-1.6, y0 - 4.4),
           f"增益 1 + R_F/R_G = 1 + 33k/1k = {G:.0f}；高通 1/(2π·27k·1µF) = {fhp:.2f} Hz；低通 1/(2π·6.8k·10nF) = {flp:.0f} Hz。\n"
           f"中点：12 V × 9.1/(15 + 9.1) = {vmid:.2f} V（示意取值），经 B 组跟随器输出，R_G、R_HP、R_T 接它不会把中点拉偏。\n"
           f"施密特：门限以 V_MID 为中心（本节 10k/10k 两端都改接 V_MID，即 R_T = 10k∥10k = 5 kΩ），上门限 {vu:.3f} V、下门限 {vl:.3f} V、回差 {vu - vl:.3f} V；\n"
           f"最小信号 {vmid:.2f} ± {vpk:.2f} V（{vmid - vpk:.2f}–{vmid + vpk:.2f} V）两条门限都越过。若照本节门限 2.614/2.384 V，比较器永不翻转。")
    schem.save_schem(d, N, "42_p3_5_ex1_schem.png")
    print(f"[图 42-p3-5] 例 1 前端：G = {G:.0f}，f_HP = {fhp:.2f} Hz，f_LP = {flp:.0f} Hz，V_MID = {vmid:.2f} V；施密特 {vu:.3f}/{vl:.3f} V，回差 {vu - vl:.3f} V，高电平 {voh:.3f} V；最小信号 {vmid - vpk:.3f}–{vmid + vpk:.3f} V")


if __name__ == "__main__":
    import sys as _sys
    _all = (p1_1, p1_2, p1_3, p1_4, p2_1, p2_2, p2_3, p2_4, p3_1, p3_2, p3_3, p3_4, p3_5, bb42, p4_2, p4_3, p4_4)
    for fn in _all:
        if len(_sys.argv) == 1 or fn.__name__ in _sys.argv[1:]:
            fn()
    print("42_figs OK")
