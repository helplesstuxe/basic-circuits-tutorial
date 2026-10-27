"""37 过零检测与超声波时差：全部配图。
运行（仓库根目录）：/workspace/circuits-venv/bin/python code/figs/37_figs.py
图上的每个数字都由本脚本打印；关键结论用 assert 检查。数值函数在 code/37_sim.py，面包板小工具在 code/33_bbkit.py。
SPICE 对照值取自 spice/37/results.json（review/spice/37.md）。实验原理图（带孔位）也画在本文件里。
"""
import os, sys, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schem import *            # noqa: F401,F403
import lab_schem as ls
import figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle


def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, "..", fn))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


sim = _load("sim37", "37_sim.py")
bbk = _load("bbkit", "33_bbkit.py")
N = "37"
C, LS = fs.C, fs.LS
SP = {r["desc"]: r["spice"] for r in json.load(open(os.path.join(HERE, "..", "..", "spice", "37", "results.json"), encoding="utf-8"))}
US = 1e6


def axl(ax, xl, yl):
    ax.set_xlabel(xl)
    if yl:
        ax.set_ylabel(yl)


# =====================================================================
# 图 37-p1-1 顺流、逆流：同一段路，声音顺风快、逆风慢
# =====================================================================
def p1_1():
    fig, ax = fs.diagram(9.0, 3.6)
    ax.add_patch(Rectangle((0.6, 1.2), 7.8, 1.2, fc="#eef5fb", ec=C["edge"], lw=1.2))
    for x in np.linspace(1.6, 7.0, 4):
        fs.arrow(ax, (x, 1.8), (x + 0.8, 1.8), color=C["cur"], lw=1.4)
    ax.text(4.5, 2.15, "风（或水流）速度 v →", ha="center", fontsize=9, color=C["cur"])
    for x, t in ((0.9, "探头 A"), (8.1, "探头 B")):
        ax.add_patch(Rectangle((x - 0.25, 1.35), 0.5, 0.9, fc="#d9d9d9", ec="0.2", lw=1.0))
        ax.text(x, 1.0, t, ha="center", fontsize=9)
    fs.arrow(ax, (1.2, 2.75), (7.8, 2.75), color=C["vin"], lw=1.6)
    fs.arrow(ax, (7.8, 0.55), (1.2, 0.55), color=C["vout"], lw=1.6)
    t1, t2 = sim.T1 * US, sim.T2 * US
    ax.text(4.5, 2.9, f"顺流 A→B：速度 c + v，用时 t1 = L/(c+v) ≈ {t1:.2f} µs", ha="center", fontsize=9, color=C["vin"])
    ax.text(4.5, 0.2, f"逆流 B→A：速度 c − v，用时 t2 = L/(c−v) ≈ {t2:.2f} µs", ha="center", fontsize=9, color=C["vout"])
    fs.span(ax, 0.9, 8.1, 3.35, f"L = {sim.L0*100:.0f} cm", fs=9)
    ax.set_ylim(0, 3.7)
    ax.set_title(f"图 37-p1-1 20 °C、v = {sim.V_FAN:.0f} m/s：两个方向差 Δt = {sim.DT*US:.2f} µs", fontsize=10.5)
    fs.save(fig, N, "37_p1_1_up_down.png")
    print(f"[数值] 图 37-p1-1：t1 = {t1:.2f}，t2 = {t2:.2f}，Δt = {sim.DT*US:.2f} µs")
    assert abs(sim.DT * US - 10.19) < 0.01


# =====================================================================
# 图 37-p1-2 幅度门限 vs 先武装再过零：回波大一点小一点时，「到达时刻」各挪多少
# =====================================================================
def p1_2():
    g_lo, g_hi = 0.9, 1.1
    t = sim.T_AX * US
    s_lo, s_hi = sim.echo(gain=g_lo, spread=False), sim.echo(gain=g_hi, spread=False)
    vth = sim.V_TH
    ta_lo, ta_hi = sim.thr_time(s_lo, vth) * US, sim.thr_time(s_hi, vth) * US
    tz_lo, tz_hi = sim.T_ZC_09 * US, sim.T_ZC_11 * US
    fig, axs = plt.subplots(2, 1, figsize=(7.4, 6.0))
    ax = axs[0]
    ax.plot(t, s_hi, color=C["vin"], lw=1.3, label=f"回波 ×{g_hi}")
    ax.plot(t, s_lo, color=C["vout"], lw=1.3, ls="--", label=f"回波 ×{g_lo}")
    ax.axhline(vth, color=C["fb"], ls="--", lw=1.1)
    ax.text(575, vth + 0.03, f"门限 V_TH（比 V_MID 高 {vth*1e3:.0f} mV）", fontsize=8.5, color=C["fb"], ha="left")
    ax.axhline(0, **LS["ref"])
    ax.set_xlim(570, 1000); ax.set_ylim(-0.62, 0.68)
    ax.legend(loc="lower right", fontsize=8.5)
    axl(ax, "时间 / µs（从发射开始算）", "放大输出 − V_MID / V")
    ax.set_title("整段回波：先慢慢长大（约 10 个周期），再慢慢变小", fontsize=10)
    ax = axs[1]
    ax.plot(t, s_hi, color=C["vin"], lw=1.6, label=f"回波 ×{g_hi}")
    ax.plot(t, s_lo, color=C["vout"], lw=1.6, ls="--", label=f"回波 ×{g_lo}")
    ax.axhline(vth, color=C["fb"], ls="--", lw=1.1)
    ax.axhline(0, **LS["ref"])
    for x, col in ((ta_hi, C["vin"]), (ta_lo, C["vout"])):
        ax.plot([x], [vth], "o", color=col, ms=7, zorder=5)
    for x, col in ((tz_hi, C["vin"]), (tz_lo, C["vout"])):
        ax.plot([x], [sim.ZC_UP], "s", color=col, ms=7, mfc="none", mew=1.8, zorder=5)
    ax.annotate(f"① 过门限：两条差 {sim.T_THR_SHIFT * US:.2f} µs", (ta_lo, vth), xytext=(689.5, 0.34), fontsize=9,
                arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.annotate(f"② 接着的过零点：两条只差 {abs(tz_lo-tz_hi)*1e3:.0f} ns", (tz_hi, sim.ZC_UP), xytext=(698, -0.33), fontsize=9,
                arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.set_xlim(680, 712); ax.set_ylim(-0.42, 0.46)
    ax.legend(loc="lower left", fontsize=8.5)
    axl(ax, "时间 / µs（放大看第 5 个周期附近）", "放大输出 − V_MID / V")
    fig.suptitle("图 37-p1-2 门限只用来「武装」，真正的计时点取它后面的那个过零点", fontsize=10.5)
    fs.save(fig, N, "37_p1_2_thr_vs_zc.png")
    print(f"[数值] 图 37-p1-2：×0.9/×1.1 过门限 {ta_lo:.2f}/{ta_hi:.2f} µs（差 {sim.T_THR_SHIFT * US:.2f}），过零 {tz_lo:.3f}/{tz_hi:.3f} µs（差 {abs(tz_lo-tz_hi)*1e3:.0f} ns）")
    assert abs(abs(ta_lo - ta_hi) - sim.T_THR_SHIFT * US) < 1e-9 and abs(tz_lo - tz_hi) < 0.1
    # 图上的差和正文一致：687.62 − 686.25 = 1.37（真值 1.37499…，四舍五入是 1.37）
    assert f"{sim.T_THR_SHIFT * US:.2f}" == "1.37" and abs(round(ta_lo, 2) - round(ta_hi, 2) - 1.37) < 1e-9


# =====================================================================
# 图 37-p2-1 Δt 和风速成正比
# =====================================================================
def p2_1():
    v = np.linspace(0, 5, 101)
    dt = [(sim.tof(sim.L0, sim.C0, x)[1] - sim.tof(sim.L0, sim.C0, x)[0]) * US for x in v]
    fig, ax = plt.subplots(figsize=(7, 4.0))
    ax.plot(v, dt, color=C["vin"], lw=1.8, label=f"L = {sim.L0*100:.0f} cm，20 °C（c = {sim.C0:.2f} m/s）")
    for x, y in sim.DT_TABLE.items():
        ax.plot([x], [y], "o", color=C["vout"], ms=6)
        ax.annotate(f"{y:.2f} µs", (x, y), textcoords="offset points", xytext=(-48, 6), fontsize=9)
    ax.set_xlim(0, 5.3); ax.set_ylim(0, 19)
    ax.legend(loc="upper left", fontsize=9)
    axl(ax, "风速 v / (m/s)", "Δt = t2 − t1 / µs")
    ax.set_title("图 37-p2-1 每 1 m/s 只多出约 3.4 µs：要分得清 0.1 µs 才算量得准", fontsize=10.5)
    fs.save(fig, N, "37_p2_1_dt_vs_v.png")
    print("[数值] 图 37-p2-1：" + "，".join(f"{k} m/s→{d:.2f} µs" for k, d in sim.DT_TABLE.items()))
    assert abs(dt[-1] - 16.98) < 0.01


# =====================================================================
# 图 37-p2-3 时序图：猝发、清零/盲区、放大输出、武装、Q1、过零、Q2
# =====================================================================
def _logic_traces():
    t = sim.T_AX
    s = sim.echo()
    vth = sim.V_TH
    clr = (t >= sim.T_BLANK).astype(float)                          # D4：0～350 µs 为低（清零 + 盲区）
    arm = np.where(s > vth, 0.0, 1.0)                               # LM393 A：放大输出高过 V_TH 时拉低
    zc = np.zeros_like(s); hi = False                               # LM393 B：带回差
    for i, x in enumerate(s):
        hi = (x > sim.ZC_DN) if hi else (x > sim.ZC_UP)
        zc[i] = hi
    q1 = np.zeros_like(s); q2 = np.zeros_like(s)
    for i in range(1, len(s)):
        if clr[i] == 0:
            q1[i] = q2[i] = 0
            continue
        q1[i] = 1 if arm[i] == 0 else q1[i - 1]
        q2[i] = q1[i - 1] if (zc[i] == 1 and zc[i - 1] == 0) else q2[i - 1]
    burst = np.where(t < sim.T_BURST, np.sign(np.sin(2 * np.pi * sim.F_TX * t + 1e-9)), 0.0)
    return t * US, s, clr, arm, zc, q1, q2, burst


def p2_3():
    t, s, clr, arm, zc, q1, q2, burst = _logic_traces()
    tq = t[np.argmax(q2 > 0.5)]
    rows = [("D3−D11\n（发射）", burst, C["third"]), ("D4 = /CLR\n（清零/盲区）", clr, C["fb"]),
            ("放大输出\n− V_MID", s, C["vin"]), ("武装\n（LM393 A）", arm, C["vout"]), ("Q1", q1, C["vout"]),
            ("过零\n（LM393 B）", zc, C["cur"]), ("Q2 → D8", q2, C["bad"]), ("/Q2\n（万用表）", 1 - q2, "#4d4d4d")]
    fig, axs = plt.subplots(len(rows), 2, figsize=(8.4, 8.2), sharex="col", gridspec_kw=dict(width_ratios=(1, 1.6)))
    for k, (name, y, col) in enumerate(rows):
        for j, (x0, x1) in enumerate(((0, 380), (655, 722))):
            ax = axs[k, j]
            m = (t >= x0) & (t <= x1)
            ax.plot(t[m], y[m], color=col, lw=1.2)
            if k == 2:
                ax.axhline(sim.V_TH, color=C["fb"], ls="--", lw=0.9)
                ax.axhline(0, **LS["ref"])
                ax.set_ylim(-0.6, 0.6)
            else:
                ax.set_ylim(-1.3 if k == 0 else -0.2, 1.3)
            ax.set_yticks([])
            ax.set_xlim(x0, x1)
            for sp_ in ("top", "right", "left"):
                ax.spines[sp_].set_visible(False)
            if j == 1:
                ax.axvline(tq, color=C["bad"], ls=":", lw=1.0)
        axs[k, 0].set_ylabel(name, rotation=0, ha="right", va="center", fontsize=8.5)
    axs[2, 1].text(721, sim.V_TH + 0.04, "V_TH", fontsize=8, color=C["fb"], ha="right")
    axs[1, 0].text(sim.T_BLANK * US + 4, 0.25, f"{sim.T_BLANK*US:.0f} µs 后才放开", fontsize=8)
    axs[0, 0].text(sim.T_BURST * US + 4, 0.25, f"8 个周期，{sim.T_BURST*US:.0f} µs", fontsize=8)
    axs[6, 1].text(tq + 0.5, 0.35, "Q2 升高 = 捕获时刻", fontsize=8, color=C["bad"])
    axs[-1, 0].set_xlabel("时间 / µs（左：发射和盲区）")
    axs[-1, 1].set_xlabel("时间 / µs（右：回波到来，放大看）")
    fig.suptitle("图 37-p2-3 时序：先过门限把 Q1 置 1（武装），下一个过零上升沿才把 Q2 打成 1", fontsize=10.5)
    fs.save(fig, N, "37_p2_3_timing.png")
    print(f"[数值] 图 37-p2-3：Q2 升高时刻 {tq:.2f} µs（sim T_ZC {sim.T_ZC_NOM*US:.2f}）")
    assert abs(tq - sim.T_ZC_NOM * US) < 0.2


# =====================================================================
# 图 37-p2-4 Timer1 一轮 80000 个滴答：几个关键的数
# =====================================================================
def p2_4():
    tick = np.arange(0, sim.REP_TICKS + 1, 50)
    tcnt = tick % 65536
    icr = round(sim.T_ZC_NOM * sim.F_CPU)
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(tick / sim.F_CPU * 1e3, tcnt, color=C["vin"], lw=1.6, label="TCNT1（每 62.5 ns 加 1）")
    marks = ((sim.N_CYC * 2 * sim.HALF_TICKS, "3200：8 个周期发完", 0.75),
             (sim.BLANK_TICKS, "5600：盲区结束，D4 拉高", 0.62),
             (icr, "ICR1 = ?：Q2 上升沿拍下的数（例 1 揭晓）", 0.49))
    for x, txt, yy in marks:
        ax.axvline(x / sim.F_CPU * 1e3, color=C["vout"], ls="--", lw=1.0)
        ax.text(x / sim.F_CPU * 1e3 + 0.05, 65536 * yy, txt, fontsize=8.5, color=C["vout"])
    ax.axvline(sim.OVF * 1e3, color=C["bad"], ls=":", lw=1.0)
    ax.text(sim.OVF * 1e3 - 0.05, 65536 * 0.95, "65536：溢出（TOV1）", fontsize=8.5, color=C["bad"], ha="right")
    ax.text(sim.OVF * 1e3 + 0.05, 65536 * 0.25, f"再等 {sim.REP_TICKS-65536} 个\n凑满 {sim.REP_TICKS}\n= {sim.T_REP*1e3:.0f} ms", fontsize=8.5)
    ax.set_xlim(0, 5.05); ax.set_ylim(0, 70000)
    ax.legend(loc="upper left", fontsize=8.5)
    axl(ax, "时间 / ms（一轮）", "TCNT1 的值")
    ax.set_title("图 37-p2-4 Timer1 不分频：一轮里先发射、再盲区、再等捕获、最后凑满 5 ms", fontsize=10.5)
    fs.save(fig, N, "37_p2_4_timer1.png")
    print(f"[数值] 图 37-p2-4：ICR1 ≈ {icr}（{sim.T_ZC_NOM*US:.2f} µs × 16）")
    assert icr == 11325


# =====================================================================
# 图 37-p3-1 拧门限：t 一台阶一台阶地跳，每级正好 25 µs
# =====================================================================
def p3_1():
    v = sim.VTH_SCAN
    tt = sim.T_SCAN * US
    pk = sim.PK * sim.A_NOM
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.step(v * 1e3, tt, where="mid", color=C["vin"], lw=1.8, label="武装 + 过零：测到的 t")
    for k in range(3, 10):
        ax.axvline(pk[k] * 1e3, **LS["ref"])
        ax.text(pk[k] * 1e3, 652, f"第{k+1}峰", fontsize=7.5, rotation=90, ha="right", va="bottom", color="0.4")
    ax.axvline(sim.V_TH * 1e3, color=C["fb"], ls="--", lw=1.1)
    ax.text(sim.V_TH * 1e3 + 3, 830, f"本实验调到 {sim.V_TH*1e3:.0f} mV\n（第 4、5 峰中间）", fontsize=8.5, color=C["fb"])
    ax.set_xlim(30, 510); ax.set_ylim(645, 845)
    ax.legend(loc="upper left", fontsize=8.5)
    axl(ax, "门限 V_TH − V_MID / mV", "测到的时间 t / µs")
    ax.set_title("图 37-p3-1 门限每越过一个峰，t 就整整晚一个周期（25 µs）", fontsize=10.5)
    fs.save(fig, N, "37_p3_1_vth_staircase.png")
    lv = sorted(set(float(x) for x in np.round(tt[~np.isnan(tt)], 1)))
    print(f"[数值] 图 37-p3-1：台阶 {lv}；峰值 mV " + " ".join(f"{p*1e3:.0f}" for p in pk[3:10]))
    assert len(lv) == 8 and np.isnan(tt[-1])


# =====================================================================
# 图 37-p3-2 回波幅度变化：幅度门限法连续漂，武装 + 过零法整周期跳
# =====================================================================
def p3_2():
    g = np.round(np.arange(0.5, 2.001, 0.02), 3)
    ta = np.array([sim.thr_time(sim.echo(gain=x, spread=False), sim.V_TH) for x in g]) * US
    tz = np.array([sim.armed_zc(sim.echo(gain=x, spread=False), sim.V_TH) for x in g]) * US
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.plot(g, ta, color=C["vout"], lw=1.6, label="只用幅度门限（过门限就计时）")
    ax.plot(g, tz, color=C["vin"], lw=1.8, label="武装 + 过零（本节电路）")
    spg = {0.7: "武装+过零 t（幅度 ×0.7）", 1.0: "武装+过零 t（幅度 ×1.0）", 1.4: "武装+过零 t（幅度 ×1.4）",
           2.0: "武装+过零 t（幅度 ×2.0）", 0.5: "武装+过零 t（幅度 ×0.5）"}
    for x, k in spg.items():
        ax.plot([x], [SP[k]], "x", color=C["bad"], ms=9, mew=2, label="SPICE（含 LM393 约 0.9 µs 延迟）" if x == 0.7 else None)
    ax.annotate(f"SPICE ×0.5：{SP[spg[0.5]]:.1f} µs\n第 7 峰只高出门限 {(sim.PK[6]*0.5*sim.A_NOM-sim.V_TH)*1e3:.1f} mV，\nLM393 没翻，又晚一个周期", (0.5, SP[spg[0.5]]),
                xytext=(0.62, 774), fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.axvspan(sim.LO_OK, sim.HI_OK, color=C["hi"], alpha=0.35, lw=0)
    ax.text((sim.LO_OK + sim.HI_OK) / 2, 650, f"×{sim.LO_OK:.2f}～×{sim.HI_OK:.2f}\n不跳周期", ha="center", fontsize=8.5)
    ax.set_ylim(640, 795)
    ax.legend(loc="upper right", fontsize=8.5)
    axl(ax, "回波幅度（以本实验的 ×1 为准）", "测到的时间 t / µs")
    ax.set_title("图 37-p3-2 过零法在黄色范围里几乎是一条平线；出了范围就整 25 µs 地跳", fontsize=10.5)
    fs.save(fig, N, "37_p3_2_t_vs_amp.png")
    i09, i11 = list(g).index(0.9), list(g).index(1.1)
    print(f"[数值] 图 37-p3-2：×0.9→×1.1 幅度门限 {ta[i09]:.2f}→{ta[i11]:.2f}，过零 {tz[i09]:.3f}→{tz[i11]:.3f}")
    assert abs(tz[i09] - tz[i11]) < 0.1 and abs(ta[i09] - ta[i11]) > 1.2


# =====================================================================
# 图 37-p3-3 改间距：斜率就是 1/c；改太多就会跳周期
# =====================================================================
def p3_3():
    L = np.array(sim.L_SET) * 1e3
    fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.9), gridspec_kw=dict(width_ratios=(1.3, 1)))
    ax = axs[0]
    ax.plot(L, sim.T_L * US, "o", color=C["vin"], ms=7, label="模型「测到」的 t")
    xx = np.linspace(160, 240, 10)
    ax.plot(xx, np.polyval(sim.FIT, xx), color=C["good"], ls="--", lw=1.2,
            label=f"拟合：斜率 {sim.FIT[0]:.4f} µs/mm，截距 {sim.FIT[1]:.1f} µs")
    ax.legend(loc="upper left", fontsize=8.2)
    axl(ax, "两探头间距 L / mm", "t / µs")
    ax.set_title(f"斜率倒过来：c ≈ {sim.C_FROM_SLOPE:.1f} m/s", fontsize=10)
    ax = axs[1]
    Lw = np.array(list(sim.RES_WIDE)) * 100
    r = np.array(list(sim.RES_WIDE.values()))
    ax.bar(Lw, r, width=1.6, color=[C["bad"] if abs(x) > 1 else C["fb"] for x in r])
    for x, y in zip(Lw, r):
        ax.text(x, y + (1.5 if y >= 0 else -4), f"{y:+.1f}", ha="center", fontsize=8.5)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylim(-32, 32)
    axl(ax, "间距 / cm（一次改很多）", "比直线多/少的时间 / µs")
    ax.set_title("差出 ±25 µs = 跳了一个周期", fontsize=10)
    fig.suptitle("图 37-p3-3 左：17～23 cm 四个点排成直线；右：一下改到 10 cm 或 30 cm，回波大小变太多就跳周期", fontsize=10.5)
    fs.save(fig, N, "37_p3_3_spacing.png")
    print(f"[数值] 图 37-p3-3：斜率 {sim.FIT[0]:.4f}，截距 {sim.FIT[1]:.1f}，c {sim.C_FROM_SLOPE:.1f}；残差 " + " ".join(f"{x:.0f}cm {y:+.1f}" for x, y in zip(Lw, r)))
    assert abs(sim.C_FROM_SLOPE - 342.9) < 0.1


# =====================================================================
# 图 37-p3-5 发射电流：每次翻转一个尖峰，串电阻把它限在 40 mA 以下
# =====================================================================
def p3_5():
    t = np.linspace(0, 40e-6, 4001)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    sps = {150: "发射 150 Ω：引脚峰值电流", 100: "发射 100 Ω：峰值电流（超 40 mA）", 220: "发射 220 Ω：峰值电流"}
    cols = {150: C["vin"], 100: C["bad"], 220: C["fb"]}
    half = 1 / sim.F_TX / 2
    for rs in (100, 150, 220):
        ipk, tau, _ = sim.drive(rs)
        k = np.floor(t / half)
        i = ipk * np.exp(-(t - k * half) / tau) * np.where(k % 2 == 0, 1, -1)
        ax.plot(t * US, i * 1e3, color=cols[rs], lw=1.4, label=f"每只 {rs} Ω：峰值 {ipk*1e3:.1f} mA（SPICE {SP[sps[rs]]:.1f}）")
    ax.axhline(40, color=C["bad"], ls="--", lw=1.0); ax.axhline(-40, color=C["bad"], ls="--", lw=1.0)
    ax.text(39.5, 41.5, "ATmega 引脚上限 40 mA", fontsize=8.5, color=C["bad"], ha="right")
    ax.set_xlim(0, 40); ax.set_ylim(-58, 58)
    ax.legend(loc="lower right", fontsize=8.5)
    axl(ax, "时间 / µs（前 1.6 个周期）", "D3 引脚电流 / mA")
    ax.set_title(f"图 37-p3-5 探头像一只 {sim.C_TR*1e12:.0f} pF 电容：每翻一次充一次电，τ = 2R × C 很短", fontsize=10.5)
    fs.save(fig, N, "37_p3_5_tx_current.png")
    print(f"[数值] 图 37-p3-5：峰值 100/150/220 Ω = {sim.drive(100)[0]*1e3:.1f}/{sim.drive(150)[0]*1e3:.1f}/{sim.drive(220)[0]*1e3:.1f} mA，τ150 = {sim.TAU150*US:.2f} µs")
    assert SP[sps[150]] < 40 and SP[sps[100]] > 40


# =====================================================================
# 原理图（图 37-p2-2）与带孔位的实验原理图（图 37-p4-2）共用
# =====================================================================
def _vmid(d, xy, ha="left", hole=""):
    """同名网络标记：所有标 V_MID 的点都连在一起。"""
    d += elm.Dot(open=True).at(xy)
    ls.lab(d, (xy[0] + (0.2 if ha == "left" else -0.2), xy[1]), "V_MID" + hole, ha=ha, fs_=9, color=C["fb"])


def _schem(d, holes=False):
    H = (lambda s: s) if holes else (lambda s: "")
    SIG, OUT, VM = C["vin"], C["vout"], C["fb"]
    # ---------------- 发射：D3 → 150 Ω → MA40S4S → 150 Ω → D11
    yt = 11.0
    d += elm.Dot(open=True).at((0, yt))
    ls.lab(d, (-0.25, yt), "D3" + H("\n→ j50"), ha="right", fs_=9.5, color=C["third"])
    d += elm.Resistor().endpoints((0, yt), (2.6, yt))
    ls.lab(d, (1.3, yt + 0.6), "Rtx1 150 Ω" + H("（h50–h53）"), ha="center", fs_=9)
    d += elm.Crystal().endpoints((2.6, yt), (5.4, yt))
    ls.lab(d, (4.0, yt + 0.75), "MA40S4S 发射" + H("\n两脚接 f53、f56"), ha="center", fs_=9)
    d += elm.Resistor().endpoints((5.4, yt), (8.0, yt))
    ls.lab(d, (6.7, yt + 0.6), "Rtx2 150 Ω" + H("（i52–i56）"), ha="center", fs_=9)
    d += elm.Dot(open=True).at((8.0, yt))
    ls.lab(d, (8.25, yt), "D11" + H("\n→ j52"), fs_=9.5, color=C["third"])
    ls.lab(d, (4.0, yt - 0.9), "D3、D11 反相翻转：探头两端 ±5 V，8 个周期", ha="center", fs_=8.5, color="0.35")
    # ---------------- V_MID：12 V 一分为二 + TL072 A 跟随
    d += elm.Vdd().at((0, 5.4)).label("+12 V")
    d += elm.Resistor().endpoints((0, 5.4), (0, 2.8))
    ls.lab(d, (-0.4, 4.1), "R1 10 kΩ" + H("\ng3←+12 V，h3–h5"), ha="right", fs_=9)
    d += elm.Dot().at((0, 2.8))
    d += elm.Resistor().endpoints((0, 2.8), (0, 0.2))
    d += elm.Ground().at((0, 0.2))
    ls.lab(d, (-0.4, 1.5), "R2 10 kΩ" + H("\ni5→GND"), ha="right", fs_=9)
    d += elm.Line().at((0, 2.8)).to((1.4, 2.8))
    d += elm.Dot().at((1.4, 2.8))
    d += elm.Capacitor(polar=True).endpoints((1.4, 2.8), (1.4, 0.2))
    d += elm.Ground().at((1.4, 0.2))
    ls.lab(d, (1.75, 1.5), "Cm 10 µF" + H("\nj6→GND"), fs_=9)
    opa = elm.Opamp(leads=True).right().flip().anchor("in2").at((3.7, 2.8))
    d += opa
    a = opa.absanchors
    d += elm.Line().at((1.4, 2.8)).to(a["in2"])
    ls._pin(d, a["in2"], "3", dx=-0.2, dy=0.25); ls._pin(d, a["in1"], "2", dx=-0.2, dy=-0.25); ls._pin(d, a["out"], "1", dx=0.15, dy=0.25)
    ls.lab(d, (a["in2"][0] + 0.75, a["out"][1]), "TL072\nA", fs_=8.5)
    xvo = a["out"][0] + 0.6
    d += elm.Line().at(a["out"]).to((xvo, a["out"][1])).color(VM).linewidth(1.6)
    d += elm.Line().at((xvo, a["out"][1])).to((xvo, a["in1"][1] - 0.9)).color(VM).linewidth(1.6)
    d += elm.Line().at((xvo, a["in1"][1] - 0.9)).to((a["in1"][0] - 0.4, a["in1"][1] - 0.9)).color(VM).linewidth(1.6)
    d += elm.Line().at((a["in1"][0] - 0.4, a["in1"][1] - 0.9)).to((a["in1"][0] - 0.4, a["in1"][1])).color(VM).linewidth(1.6)
    d += elm.Line().at((a["in1"][0] - 0.4, a["in1"][1])).to(a["in1"]).color(VM).linewidth(1.6)
    t_, b_ = a["vs"], a["vd"]
    d += elm.Line().at(t_).to((t_[0], t_[1] + 0.4)); d += elm.Vdd().at((t_[0], t_[1] + 0.4)).label("+12 V", fontsize=9)
    ls._pin(d, t_, "8", dx=0.25, dy=0.2)
    d += elm.Line().at(b_).to((b_[0], b_[1] - 0.4)); d += elm.Ground().at((b_[0], b_[1] - 0.4))
    ls._pin(d, b_, "4", dx=0.25, dy=-0.2)
    ym = a["out"][1]
    d += elm.Dot().at((xvo, ym))
    xbus = xvo + 2.0
    d += elm.Line().at((xvo, ym)).to((xbus, ym)).color(VM).linewidth(1.6)
    _vmid(d, (xbus, ym), hole=H("（第 20 列）"))
    ls.probe(d, (xvo + 1.0, ym), "③", dx=0.0, dy=-1.0)
    ls.lab(d, (xvo - 1.2, ym - 2.4), f"V_MID = {sim.V_MID:.1f} V\n（中点参考）", ha="center", fs_=9, color=VM)
    # ---------------- 接收放大：MA40S4R + TL072 B，同相 11 倍
    xr, yp = 11.0, 6.0
    _vmid(d, (xr, 1.6), ha="right")
    d += elm.Crystal().endpoints((xr, 1.6), (xr, yp))
    ls.lab(d, (xr - 0.55, 3.8), "MA40S4R\n接收" + H("\n脚→a11、a20"), ha="right", fs_=9)
    d += elm.Dot().at((xr, yp))
    d += elm.Line().at((xr, yp)).to((xr + 1.4, yp))
    d += elm.Dot().at((xr + 1.4, yp))
    d += elm.Resistor().endpoints((xr + 1.4, yp), (xr + 1.4, 3.2))
    ls.lab(d, (xr + 1.8, 3.9), "Rb 100 kΩ" + H("\nb11–b20"), fs_=9)
    _vmid(d, (xr + 1.4, 3.2), ha="right")
    opb = elm.Opamp(leads=True).right().flip().anchor("in2").at((xr + 3.2, yp))
    d += opb
    b = opb.absanchors
    d += elm.Line().at((xr + 1.4, yp)).to(b["in2"])
    ls._pin(d, b["in2"], "5", dx=-0.2, dy=0.25); ls._pin(d, b["in1"], "6", dx=-0.2, dy=-0.25); ls._pin(d, b["out"], "7", dx=0.15, dy=0.25)
    ls.lab(d, (b["in2"][0] + 0.75, b["out"][1]), "TL072\nB", fs_=8.5)
    xn = b["in1"][0] - 0.4
    yf = b["in1"][1] - 1.4
    d += elm.Line().at(b["in1"]).to((xn, b["in1"][1]))
    d += elm.Line().at((xn, b["in1"][1])).to((xn, yf))
    d += elm.Dot().at((xn, yf))
    xo = b["out"][0] + 0.8
    yo = b["out"][1]
    d += elm.Resistor().endpoints((xn, yf), (xo, yf))
    ls.lab(d, ((xn + xo) / 2, yf - 0.65), "Rf 100 kΩ" + H("（c9–c13）"), ha="center", fs_=9)
    d += elm.Line().at((xo, yf)).to((xo, yo))
    d += elm.Resistor().endpoints((xn, yf), (xn, yf - 2.2))
    ls.lab(d, (xn - 0.4, yf - 1.1), "Rg 10 kΩ" + H("\nd13–d17"), ha="right", fs_=9)
    d += elm.Capacitor().endpoints((xn, yf - 2.2), (xn, yf - 3.6))
    ls.lab(d, (xn + 0.4, yf - 2.9), "Cg 100 nF" + H("（c17–c20）"), fs_=9)
    _vmid(d, (xn, yf - 3.6), ha="left")
    d += elm.Line().at(b["out"]).to((xo, yo)).color(SIG).linewidth(1.8)
    d += elm.Dot().at((xo, yo))
    ls.probe(d, (xo, yo), "①", dx=0.0, dy=1.1)
    ls.lab(d, (xo - 0.2, yo - 3.3), f"放大输出\n= V_MID + 回波×{sim.GAIN:.0f}" + H("\n（第 22 列）"), ha="center", fs_=8.5, color=SIG)
    # ---------------- 比较器：LM393 A 武装、LM393 B 过零
    xa_ = xo + 1.6
    yA, yB = 9.0, 2.6
    d += elm.Line().at((xo, yo)).to((xa_, yo)).color(SIG).linewidth(1.8)
    d += elm.Dot().at((xa_, yo))
    cA = elm.Opamp(leads=True).right().flip().anchor("in2").at((xa_ + 3.4, yA))
    d += cA
    A = cA.absanchors
    d += elm.Line().at((xa_, yo)).to((xa_, A["in1"][1])).color(SIG).linewidth(1.8)
    d += elm.Line().at((xa_, A["in1"][1])).to(A["in1"]).color(SIG).linewidth(1.8)
    ls._pin(d, A["in2"], "3", dx=-0.25, dy=0.25); ls._pin(d, A["in1"], "2", dx=-0.25, dy=-0.25); ls._pin(d, A["out"], "1", dx=0.15, dy=0.25)
    ls.lab(d, (A["in2"][0] + 1.25, A["out"][1] - 0.1), "LM393\nA", fs_=8)
    # V_TH：12 V–100k–电位器 10k–V_MID
    xw = xa_ + 2.3
    xpp = xw - 0.6
    d += elm.Line().at(A["in2"]).to((xw, yA)).color(VM)
    d += elm.Dot().at((xw, yA))
    ls.probe(d, (xw, yA), "②", dx=0.2, dy=-0.75)
    pot = elm.Potentiometer().endpoints((xpp, yA + 3.4), (xpp, yA + 0.5))
    d += pot
    tap = pot.absanchors["tap"]
    d += elm.Line().at(tap).to((xw, tap[1])).color(VM)
    d += elm.Line().at((xw, tap[1])).to((xw, yA)).color(VM)
    d += elm.Resistor().endpoints((xpp, yA + 3.4), (xpp, yA + 5.8))
    d += elm.Vdd().at((xpp, yA + 5.8)).label("+12 V", fontsize=9)
    ls.lab(d, (xpp - 0.45, yA + 4.6), "100 kΩ" + H("\ng33–g36\n+12 V→f36"), ha="right", fs_=9)
    ls.lab(d, (xpp - 0.45, yA + 2.2), "电位器 10 kΩ" + H("\nh31·h32·h33"), ha="right", fs_=9)
    _vmid(d, (xpp, yA + 0.5), ha="right", hole=H("（h20→i31）"))
    ls.lab(d, (xw + 0.2, yA + 0.35), "V_TH", fs_=9, color=VM)
    ls.lab(d, (xw + 0.15, tap[1] + 0.4), H("中间脚 i32→i26"), fs_=8.5)
    # LM393 B 过零
    cB = elm.Opamp(leads=True).right().flip().anchor("in2").at((xa_ + 3.0, yB))
    d += cB
    B = cB.absanchors
    ls._pin(d, B["in2"], "5", dx=-0.25, dy=0.25); ls._pin(d, B["in1"], "6", dx=-0.25, dy=-0.25); ls._pin(d, B["out"], "7", dx=0.15, dy=0.25)
    ls.lab(d, (B["in2"][0] + 1.25, B["out"][1] - 0.1), "LM393\nB", fs_=8)
    xj = B["in2"][0] - 0.5
    d += elm.Line().at((xa_, yo)).to((xa_, yB)).color(SIG).linewidth(1.8)
    d += elm.Resistor().endpoints((xa_, yB), (xj, yB))
    ls.lab(d, ((xa_ + xj) / 2, yB + 0.6), "10 kΩ" + H("（c22–c27）"), ha="center", fs_=9)
    d += elm.Dot().at((xj, yB))
    d += elm.Line().at((xj, yB)).to(B["in2"])
    d += elm.Resistor().endpoints((xa_ + 0.2, B["in1"][1]), (B["in1"][0], B["in1"][1]))
    _vmid(d, (xa_ + 0.2, B["in1"][1]), ha="right")
    ls.lab(d, ((xa_ + B["in1"][0]) / 2, B["in1"][1] - 0.65), "10 kΩ" + H("（d20–d26）"), ha="center", fs_=9)
    xbo = B["out"][0] + 0.7
    yhy = yB + 1.6
    d += elm.Line().at((xj, yB)).to((xj, yhy))
    d += elm.Resistor().endpoints((xj, yhy), (xbo, yhy))
    ls.lab(d, ((xj + xbo) / 2, yhy + 0.6), "R_HY 4.7 MΩ" + H("（a25–a27）"), ha="center", fs_=9)
    d += elm.Line().at((xbo, yhy)).to((xbo, B["out"][1]))
    # 电源脚（只画一次，两组同一片）
    t_, b_ = A["vs"], A["vd"]
    d += elm.Line().at(t_).to((t_[0], t_[1] + 0.4)); d += elm.Vdd().at((t_[0], t_[1] + 0.4)).label("+12 V", fontsize=9)
    ls._pin(d, t_, "8", dx=0.25, dy=0.2)
    t2_, b2_ = B["vs"], B["vd"]
    d += elm.Line().at(b2_).to((b2_[0], b2_[1] - 0.4)); d += elm.Ground().at((b2_[0], b2_[1] - 0.4))
    ls._pin(d, b2_, "4", dx=0.25, dy=-0.2)
    # 两个输出都上拉到 Arduino 5 V
    outs = {}
    for nm, P, yy, col in (("arm", A, yA - 0.5, OUT), ("zc", B, yB - 0.5, C["cur"])):
        x1 = P["out"][0] + 0.7
        x2 = x1 + 1.2
        d += elm.Line().at(P["out"]).to((x2, P["out"][1])).color(col).linewidth(1.8)
        d += elm.Dot().at((x2, P["out"][1]))
        d += elm.Resistor().endpoints((x2, P["out"][1]), (x2, P["out"][1] + 2.0))
        d += elm.Vdd().at((x2, P["out"][1] + 2.0)).label("+5 V（Arduino）", fontsize=8.5)
        ls.lab(d, (x2 + 0.35, P["out"][1] + 1.0), "2.2 kΩ" + H("\nj24→+5 V" if nm == "arm" else "\nj29→+5 V"), fs_=8.5)
        outs[nm] = (x2, P["out"][1])
    ls.lab(d, ((B["out"][0] + outs["zc"][0]) / 2, B["out"][1] - 0.75), H("b25→b29\ne29–f29"), ha="center", fs_=8.5)
    # ---------------- 74HC74：FF1 记「武装过了」，FF2 在下一个过零上升沿把 Q2 打成 1
    xf = outs["arm"][0] + 2.6
    ff1 = module("FF1（74HC74 前半）", left=("/PRE1 ④", "D1 ②", "CLK1 ③", "/CLR1 ①"), right=("Q1 ⑤",), w=3.4).right().anchor("/PRE1 ④").at((xf, outs["arm"][1] + 1.6))
    d += ff1
    F1 = ff1.absanchors
    xj1 = xf - 1.0
    d += elm.Line().at(outs["arm"]).to((xj1, outs["arm"][1])).color(OUT).linewidth(1.8)
    d += elm.Line().at((xj1, outs["arm"][1])).to((xj1, F1["/PRE1 ④"][1])).color(OUT).linewidth(1.8)
    d += elm.Line().at((xj1, F1["/PRE1 ④"][1])).to(F1["/PRE1 ④"]).color(OUT).linewidth(1.8)
    for k in ("D1 ②", "CLK1 ③"):
        d += elm.Line().at(F1[k]).to((F1[k][0] - 0.4, F1[k][1]))
    d += elm.Line().at((F1["D1 ②"][0] - 0.4, F1["D1 ②"][1])).to((F1["D1 ②"][0] - 0.4, F1["CLK1 ③"][1] - 0.0))
    d += elm.Ground().at((F1["CLK1 ③"][0] - 0.4, F1["CLK1 ③"][1]))
    yclr = F1["/CLR1 ①"][1]
    ff2 = module("FF2（74HC74 后半）", left=("/PRE2 ⑩", "D2 ⑫", "CLK2 ⑪", "/CLR2 ⑬"), right=("Q2 ⑨", "/Q2 ⑧"), w=3.4).right().anchor("CLK2 ⑪").at((xf, outs["zc"][1]))
    d += ff2
    F2 = ff2.absanchors
    d += elm.Line().at(outs["zc"]).to(F2["CLK2 ⑪"]).color(C["cur"]).linewidth(1.8)
    # Q1 → D2
    xq = F1["Q1 ⑤"][0] + 0.6
    xl = F2["D2 ⑫"][0] - 0.5
    ymid = (F1["/CLR1 ①"][1] + F2["/PRE2 ⑩"][1]) / 2 + 0.2
    d += elm.Line().at(F1["Q1 ⑤"]).to((xq, F1["Q1 ⑤"][1]))
    d += elm.Line().at((xq, F1["Q1 ⑤"][1])).to((xq, ymid))
    d += elm.Line().at((xq, ymid)).to((xl, ymid))
    d += elm.Line().at((xl, ymid)).to((xl, F2["D2 ⑫"][1]))
    d += elm.Line().at((xl, F2["D2 ⑫"][1])).to(F2["D2 ⑫"])
    # /PRE2 → 5 V
    d += elm.Line().at(F2["/PRE2 ⑩"]).to((F2["/PRE2 ⑩"][0] - 1.3, F2["/PRE2 ⑩"][1]))
    d += elm.Vdd().at((F2["/PRE2 ⑩"][0] - 1.3, F2["/PRE2 ⑩"][1])).label("+5 V", fontsize=8.5)
    # /CLR ← D4
    xc = xf - 1.6
    d += elm.Line().at(F1["/CLR1 ①"]).to((xc, yclr)).color(C["fb"])
    d += elm.Line().at(F2["/CLR2 ⑬"]).to((xc, F2["/CLR2 ⑬"][1])).color(C["fb"])
    d += elm.Line().at((xc, yclr)).to((xc, F2["/CLR2 ⑬"][1] - 1.0)).color(C["fb"])
    d += elm.Dot().at((xc, F2["/CLR2 ⑬"][1]))
    d += elm.Dot(open=True).at((xc, F2["/CLR2 ⑬"][1] - 1.0))
    ls.lab(d, (xc, F2["/CLR2 ⑬"][1] - 1.35), "D4（清零 + 盲区）" + H("\n→ j39"), ha="center", fs_=9, color=C["fb"])
    # Q2 → D8，/Q2 → 万用表
    xq2 = F2["Q2 ⑨"][0] + 1.6
    d += elm.Line().at(F2["Q2 ⑨"]).to((xq2, F2["Q2 ⑨"][1])).color(C["bad"]).linewidth(1.8)
    d += elm.Dot(open=True).at((xq2, F2["Q2 ⑨"][1]))
    ls.lab(d, (xq2 + 0.2, F2["Q2 ⑨"][1]), "→ D8（ICP1）" + H("\na45 → D8"), fs_=9, color=C["bad"])
    d += elm.Line().at(F2["/Q2 ⑧"]).to((xq2, F2["/Q2 ⑧"][1]))
    d += elm.Dot(open=True).at((xq2, F2["/Q2 ⑧"][1]))
    ls.probe(d, (xq2, F2["/Q2 ⑧"][1]), "④", dx=0.0, dy=-0.9)
    ls.lab(d, (xq2 + 0.2, F2["/Q2 ⑧"][1] - 0.1), "/Q2：万用表" + H("\n（b46）"), fs_=9)
    ls.lab(d, (xf + 4.2, F2["/CLR2 ⑬"][1] - 1.6), "74HC74：14 脚 +5 V，7 脚 GND\n（圈里数字是引脚号）", ha="center", fs_=8.5, color="0.35")
    return dict(xmax=xq2 + 3.5)


def p2_2():
    d = drawing(fontsize=10)
    r = _schem(d)
    ls.note(d, (-3.0, -4.2), "所有标「V_MID」的空心点连在一起（中点参考，6.0 V）；+12 V 只给 TL072、LM393 和 V_TH 分压；两个 2.2 kΩ 上拉、74HC74 只接 Arduino 的 5 V。所有 GND 连在一起。")
    ls.note(d, (-3.0, -4.9), "① 放大输出　② 门限 V_TH　③ V_MID　④ /Q2（万用表直流挡测平均值）")
    save_schem(d, N, "37_p2_2_schem.png")
    print("[图 37-p2-2] 原理图：D3/D11–150Ω×2–MA40S4S；12V–10k/10k–TL072A=V_MID；MA40S4R→TL072B ×11；LM393A 武装、B 过零（R_HY 4.7M）；2.2k→5V；74HC74 FF1/FF2；Q2→D8")


# =====================================================================
# 图 37-p4-1 面包板
# =====================================================================
TL_NAMES = {1: "OUTA", 2: "IN−A", 3: "IN+A", 4: "V−", 5: "IN+B", 6: "IN−B", 7: "OUTB", 8: "V+"}
LM_NAMES = {1: "OUTA", 2: "IN−A", 3: "IN+A", 4: "GND", 5: "IN+B", 6: "IN−B", 7: "OUTB", 8: "VCC"}
HC_NAMES = {1: "/CLR1", 2: "D1", 3: "CLK1", 4: "/PRE1", 5: "Q1", 6: "/Q1", 7: "GND",
            8: "/Q2", 9: "Q2", 10: "/PRE2", 11: "CLK2", 12: "D2", 13: "/CLR2", 14: "VCC"}


def p3_4():
    """图 37-p3-4：参数篇对照用的原理图（与图 37-p2-2 同一张，注释改成本页关心的器件）。"""
    d = drawing(fontsize=10)
    _schem(d)
    ls.note(d, (-3.0, -4.2), "发射：D3、D11 各经 Rtx 150 Ω 接 MA40S4S（第四节）；+12 V 只给 TL072（8 脚）、LM393（8 脚）和 V_TH 分压，V_MID = 6.0 V（第五节）。")
    ls.note(d, (-3.0, -4.9), "两只 LM393 输出的 2.2 kΩ 上拉和 74HC74（14 脚）只接 Arduino 5 V，Q2 直接接 D8。① 放大输出　② V_TH　③ V_MID　④ /Q2")
    save_schem(d, N, "37_p3_4_schem.png")


def p4_1():
    nc = 57
    bb = bbk.Breadboard(nc, "图 37-p4-1 面包板：上方两条轨是 12 V 电源，下方两条轨是 Arduino 5 V；74HC74 的 14 脚单独用跳线接 5 V",
                        size=(17, 11.5), rails=("+12 V", "GND", "GND", "+5 V"))
    ax = bb.ax
    # 电源与地
    bb.module(-3.4, 9.4, 3.6, 1.4, "12 V 适配器")
    bb.wire((0.2, 10.4), "T+1", "pos", via=[(1, 10.4)])
    bb.wire((0.2, 9.7), "T-2", "gnd", via=[(2, 9.7)])
    bb.wire("T-1", "B-1", "gnd", via=[(0.3, 7.7), (0.3, -6.7)])
    # V_MID 分压 + TL072 A 跟随
    bb.wire("T+3", "g3", "pos", via=[(3.0, 8.6), (2.6, 7.2), (2.6, -2.4)])
    bb.part("h3", "h5", "R1 10k", "R", lab_side=-1, fs_=7)
    bb.part("i5", "B-5", "", "R"); bb.note(4.6, -5.95, "R2 10k", fontsize=7, ha="right", va="center")
    bb.part("j6", "B-6", "", "E"); bb.note(6.4, -5.95, "Cm 10µ", fontsize=7, ha="left", va="center")
    bb.wire("g5", "g6", "fb")
    bb.route("h6", "g10", "fb", dy=0.5)
    bb.chip(8, "TL072", names=TL_NAMES)
    bb.wire("a8", "T+8", "pos")
    bb.part("b8", "T-7", "", "C"); bb.note(6.8, 4.9, "Cd 100n", fontsize=7, ha="right", va="center")
    bb.wire("j11", "B-11", "gnd")
    bb.wire("h8", "h9", "fb")
    bb.route("i9", "i20", "fb", dy=0.5)
    # 接收放大（上半）
    bb.module(9.6, 9.9, 11.8, 1.1, "MA40S4R 接收探头（引线约 30 cm，绞在一起）", fc="#e8f3e8", fs_=8)
    bb.wire((11, 9.9), "a11", "sig")
    bb.wire((20, 9.9), "a20", "fb")
    # a9→a22 要横穿 a11、a20 两根探头引线：交叉处画小拱（跨线弯），表示两线不相连
    _xa, _ya = bb.xy("a9"); _xb, _ = bb.xy("a22"); _yr = _ya + 0.5
    _via = [(_xa, _yr)]
    for _c in ("a11", "a20"):
        _xc = bb.xy(_c)[0]
        _via += [(_xc - 0.22, _yr), (_xc - 0.16, _yr + 0.16), (_xc, _yr + 0.24), (_xc + 0.16, _yr + 0.16), (_xc + 0.22, _yr)]
    _via += [(_xb, _yr)]
    bb.wire("a9", "a22", "sig", via=_via)
    bb.part("c9", "c13", "Rf 100k", "R", lab_side=-1, fs_=6.5)
    bb.route("d10", "e13", "fb", dy=-0.5)
    bb.part("d13", "d17", "Rg 10k", "R", lab_side=-1, fs_=6.5)
    bb.part("c17", "c20", "Cg 100n", "C", lab_side=1, fs_=6.5)
    bb.part("b11", "b20", "Rb 100k", "R", lab_side=1, fs_=6.5)
    bb.wire("e20", "f20", "fb")
    bb.part("d20", "d26", "10k（IN−B）", "R", lab_side=-1, fs_=6.5)
    bb.wire("e22", "f22", "sig")
    bb.part("c22", "c27", "10k（IN+B）", "R", lab_side=1, fs_=6.5)
    bb.route("g22", "g25", "sig", dy=0.5)
    # LM393
    bb.chip(24, "LM393", names=LM_NAMES)
    bb.wire("a24", "T+24", "pos")
    bb.part("b24", "T-23", "", "C"); bb.note(22.8, 4.9, "Cd 100n", fontsize=7, ha="right", va="center")
    bb.part("a25", "a27", "R_HY 4.7M", "R", lab_side=1, fs_=6.5)
    bb.route("b25", "b29", "clk", dy=0.5)
    bb.wire("j27", "B-27", "gnd")
    bb.part("j24", "B+24", "", "R"); bb.note(23.6, -6.0, "2.2k", fontsize=7, ha="right", va="center")
    bb.wire("e29", "f29", "clk")
    bb.part("j29", "B+29", "", "R"); bb.note(29.4, -6.0, "2.2k", fontsize=7, ha="left", va="center")
    bb.route("c29", "c43", "clk", dy=0.5)
    # 门限：V_MID–电位器–100k–12 V
    bb.wire("h20", "i31", "fb", via=[(20, -2.9), (30.55, -2.9), (30.55, -4.4)])
    # 电位器：本体画成半透明，三只脚 h31·h32·h33 单独标出来，看得见插在哪
    ax.add_patch(Rectangle((30.6, -4.05), 2.8, 1.25, fc="#9ecae1", ec="0.2", zorder=6, alpha=0.35))
    for col_ in (31, 32, 33):
        ax.add_patch(Circle((col_, -3.4), 0.2, fc="#08519c", ec="white", lw=0.8, zorder=8))
    bb.note(33.65, -3.4, "电位器 10k\n脚 h31·h32·h33", fontsize=6.5, ha="left", va="center")
    bb.part("g33", "g36", "100k", "R", lab_side=1, fs_=6.5)
    bb.wire("T+37", "f36", "pos", via=[(37, 8.6), (37, 0.2), (36, 0.2)])   # 红跳线：上方 +12 V 轨第 37 列 → f36
    bb.route("i32", "i26", "fb", dy=0.5)
    bb.route("i24", "i43", "out", dy=-0.5)
    # 74HC74
    bb.chip(40, "74HC74", npin=14, names=HC_NAMES)
    bb.wire("a40", "B+38", "pos", via=[(40, 6.35), (38.5, 6.35), (38.5, -7.6)])
    bb.part("c40", "T-39", "", "C"); bb.note(39.6, 7.2, "Cd 100n", fontsize=7, ha="right", va="center")
    bb.route("b44", "b40", "pos", dy=0.5)
    bb.route("d41", "d39", "fb", dy=-0.5)
    bb.wire("e39", "f39", "fb"); bb.wire("g39", "g40", "fb")
    bb.wire("j41", "B-41", "gnd"); bb.wire("j42", "B-42", "gnd"); bb.wire("j46", "B-46", "gnd")
    bb.wire("g44", "a42", "sig", via=[(44, -1.9), (47.6, -1.9), (47.6, 6.25), (42, 6.25)])
    # 发射
    bb.part("h50", "h53", "Rtx1 150", "R", lab_side=1, fs_=6.5)
    bb.part("i52", "i56", "Rtx2 150", "R", lab_side=-1, fs_=6.5)
    bb.module(58.2, -1.4, 3.4, 2.4, "MA40S4S\n发射探头\n（30 cm 引线）", fc="#fbe3d6", fs_=7.5)
    bb.wire("f53", (58.2, 0.5), "out", via=[(53, 0.5)])
    bb.wire("f56", (58.2, -0.4), "out", via=[(56, -0.4)])
    # Arduino
    ym = -11.9
    bb.module(0.4, ym - 1.6, 53.0, 1.6, "Arduino Uno（USB 接电脑；GND 和 12 V 电源的 GND 连在一起）", fs_=9)
    p5 = bb.pin(1.0, ym, "5V", va="top", dy=0.25)
    pg = bb.pin(2.5, ym, "GND", va="top", dy=0.25)
    p4 = bb.pin(39.0, ym, "D4", va="top", dy=0.25)
    p8 = bb.pin(48.6, ym, "D8", va="top", dy=0.25)
    p3 = bb.pin(50.0, ym, "D3", va="top", dy=0.25)
    p11 = bb.pin(52.0, ym, "D11", va="top", dy=0.25)
    bb.wire("B+1", p5, "pos")
    bb.wire("B-2", pg, "gnd", via=[(2, -7.15), (2.5, -7.15)])
    bb.wire("j39", p4, "fb")
    bb.wire("a45", p8, "out", via=[(45, 6.75), (48.6, 6.75)])
    bb.wire("j50", p3, "out")
    bb.wire("j52", p11, "out")
    bb.probe("h22", "①", dx=0.0, dy=-1.1)
    bb.probe("g26", "②", dx=1.2, dy=-0.9)
    bb.probe("g20", "③", dx=-1.0, dy=-0.9)
    bb.probe("b46", "④", dx=1.0, dy=0.9)
    ax.set_ylim(-18.4, 11.6)
    ax.set_xlim(-3.8, nc + 5.0)
    notes = ["① 第 22 列 = 放大输出；② 第 26 列（下半）= 门限 V_TH；③ 第 20 列 = V_MID；④ 第 46 列（上半）= /Q2；黑表笔插 GND 轨",
             "TL072 在第 8–11 列，LM393 在第 24–27 列，74HC74 在第 40–46 列：1 脚都在 f 排（左下），逆时针数",
             "74HC74 的 14 脚（a40）用红色跳线接到下方 +5 V 轨，千万别插上方 +12 V 轨；10 脚 /PRE2（b44）也接到 14 脚",
             "电阻、电容横跨多个孔时，只有两端插的孔算连接，元件身子下面压着的孔不算；两组 GND 轨在最左边连通"]
    for k, t in enumerate(notes):
        bb.note(0.0, -14.6 - 0.8 * k, t, ha="left")
    bb.legend(y=-0.03)
    bb.save(N, "37_p4_1_breadboard.png")
    print("[图 37-p4-1] TL072 第 8–11 列；LM393 第 24–27 列；74HC74 第 40–46 列；V_MID 第 20 列；放大输出第 22 列；D3→j50，D11→j52，D4→j39，a45→D8")


def p4_2():
    d = drawing(fontsize=10)
    _schem(d, holes=True)
    ls.note(d, (-3.0, -4.2), "对照图 37-p4-1：灰色小字是孔位。TL072 第 8–11 列，LM393 第 24–27 列，74HC74 第 40–46 列（1 脚都在 f 排）。")
    ls.note(d, (-3.0, -4.9), "V_MID 全在第 20 列（上下两半用 e20–f20 连通）；TL072 8 脚 a8、LM393 8 脚 a24 接 +12 V 轨；74HC74 14 脚 a40 用跳线接下方 +5 V 轨。")
    ls.note(d, (-3.0, -5.6), "74HC74：1 脚、13 脚（/CLR）都接 D4（j39）；2、3 脚 j41、j42 → GND；5 脚 Q1 → 12 脚 D2；10 脚 /PRE2 → 14 脚；7 脚 j46 → GND。")
    save_schem(d, N, "37_p4_2_schem_lab.png")
    print("[图 37-p4-2] 带孔位的原理图，与图 37-p4-1 一一对应")


# =====================================================================
# 图 37-p4-3 风扇实验的摆法（俯视）
# =====================================================================
def p4_3():
    fig, ax = fs.diagram(9.0, 4.4)
    SC = 0.2                                     # 按比例画：1 cm = 0.2 格；风扇离发射探头背面 10 cm（正文写 10～15 cm）
    T_PR, W_PR = 0.7 * SC, 1.0 * SC              # 探头实物约 0.7 cm 厚（沿连线）× 1.0 cm 宽（俯视）
    xa = 2.8                                     # 发射探头正面
    xb = xa + 20 * SC                            # 接收探头正面
    ax.add_patch(Rectangle((xa - T_PR - 0.15, 1.6), 20 * SC + 2 * T_PR + 0.3, 0.35, fc="#f5e6c8", ec="0.4"))
    ticks = {}
    for k in range(0, 21, 5):
        x = xa + k * SC
        ticks[k] = x
        ax.plot([x, x], [1.6, 1.8], color="0.3", lw=0.8)
        ax.text(x, 1.83, f"{k}", ha="center", va="bottom", fontsize=6.5, color="0.3")
    ax.text((xa + xb) / 2, 1.25, "直尺（两只探头正面之间正好 20.0 cm，用胶带把探头固定在木条上）", ha="center", fontsize=8.5)
    # 两个正面在 xa、xb，方块向外侧画
    probes = ((xa - T_PR, xa, "MA40S4S\n发射", C["vout"]), (xb, xb + T_PR, "MA40S4R\n接收", C["vin"]))
    for x0, x1, t, col in probes:
        ax.add_patch(Rectangle((x0, 2.5 - W_PR / 2), x1 - x0, W_PR, fc="#d9d9d9", ec=col, lw=1.4))
        ax.text((x0 + x1) / 2, 2.95, t, ha="center", va="bottom", fontsize=8.5, color=col)
    face_a, face_b = probes[0][1], probes[1][0]
    back_a = probes[0][0]
    fs.arrow(ax, (face_a + 0.1, 2.5), (face_b - 0.1, 2.5), color=C["third"], lw=1.4)
    for x in (face_a, face_b):
        ax.plot([x, x], [0.75, 1.6], color="0.5", lw=0.6, ls=":")
    fs.span(ax, face_a, face_b, 0.75, "L = 20.0 cm（量探头正面到正面）", fs=8.5)
    assert abs((face_b - face_a) / SC - 20.0) < 1e-9                  # 正面间距 == 20.0 cm
    assert abs(ticks[0] - face_a) < 1e-9 and abs(ticks[20] - face_b) < 1e-9   # 刻度 0/20 对准两个正面
    assert abs((probes[0][1] - probes[0][0]) / SC - 0.7) < 1e-9 and abs(W_PR / SC - 1.0) < 1e-9
    xf = back_a - 10 * SC                        # 风扇出风面，量到发射探头背面
    assert abs((back_a - xf) / SC - 10) < 1e-9
    ax.add_patch(Rectangle((xf - 0.35, 2.0), 0.35, 1.0, fc="#cfe0ee", ec=C["edge"]))
    ax.text(xf - 0.17, 3.15, "风扇\n（带网罩）", ha="center", fontsize=8.5)
    for y in (2.2, 2.5, 2.8):
        fs.arrow(ax, (xf + 0.1, y), (back_a - 0.08, y), color=C["cur"], lw=1.1)
    fs.span(ax, xf, back_a, 3.55, "10 cm（10～15 cm 都行）\n量到发射探头背面", fs=8.5, dy=0.08)
    print(f"[断言 37-p4-3] 正面间距 {(face_b - face_a) / SC:.1f} cm；刻度 0/20 x = {ticks[0]:.2f}/{ticks[20]:.2f} = 正面 {face_a:.2f}/{face_b:.2f}；"
          f"探头 {T_PR / SC:.1f}×{W_PR / SC:.1f} cm；风扇到背面 {(back_a - xf) / SC:.1f} cm")
    ax.text(xb + T_PR + 0.4, 2.4, "顺风：风扇在发射\n探头后面吹\n逆风：整根木条水平\n转 180°（风扇、\n接线都不动）\n每个方向：关、开、关", fontsize=8.2, va="center")
    ax.set_title("图 37-p4-3 俯视图：探头正对着、同一高度；风沿两只探头的连线吹", fontsize=10.5)
    fs.save(fig, N, "37_p4_3_fan_setup.png")
    print("[图 37-p4-3] 摆法示意（按比例，1 cm = 0.2 格）：L = 20.0 cm，风扇离发射探头 10 cm，风沿连线吹；木条转 180° = 逆风；每个方向关/开/关")


# =====================================================================
# 图 37-p4-4 预期读数：/Q2 平均电压随间距、随风向
# =====================================================================
def p4_4():
    L = np.array(sim.L_SET) * 100
    vq = np.array([sim.vq_avg(t) for t in sim.T_L])
    fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.9), gridspec_kw=dict(width_ratios=(1.2, 1)))
    ax = axs[0]
    ax.plot(L, vq * 1e3, "o-", color=C["vin"], ms=7, lw=1.4)
    for x, y in zip(L, vq * 1e3):
        ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(-14, 7), fontsize=8.5)
    axl(ax, "间距 L / cm", "/Q2 平均电压 / mV")
    ax.set_ylim(600, 820)
    ax.set_title(f"每多 1 mm 多 {sim.VQ_PER_MM*1e3:.3f} mV", fontsize=10)
    ax = axs[1]
    names = ("顺风向\n关", "顺风向\n开", "逆风向\n关", "逆风向\n开")
    ts = (sim.T_OFF, sim.T_DOWN, sim.T_OFF, sim.T_UP)
    v = [sim.vq_avg(t) * 1e3 for t in ts]
    ax.bar(range(4), v, color=[C["ref"], C["vin"], C["ref"], C["vout"]], width=0.6)
    ax.set_xticks(range(4)); ax.set_xticklabels(names, fontsize=8.5)
    for k, (x, tt) in enumerate(zip(v, ts)):
        ax.text(k, x + 1.0, f"{x:.2f}\nmV", ha="center", fontsize=8)
    dd, du = v[1] - v[0], v[3] - v[2]
    ax.set_ylim(690, 724)
    axl(ax, None, "/Q2 平均电压 / mV")
    ax.set_title(f"开−关：顺 {dd:+.2f}、逆 {du:+.2f} mV\n相减 {du-dd:.2f} mV ≈ {sim.DT_MEAS*US:.2f} µs", fontsize=9.5)
    assert abs((du - dd) - sim.DT_MEAS * US) < 0.01
    fig.suptitle(f"图 37-p4-4 预期读数（V5 = {sim.V5:.2f} V、一轮 {sim.T_REP*1e3:.0f} ms 时；1 mV 对应 1 µs）", fontsize=10.5)
    fs.save(fig, N, "37_p4_4_expected.png")
    print(f"[数值] 图 37-p4-4：间距 mV " + " ".join(f"{x:.1f}" for x in vq * 1e3) + "；风 µs " + " ".join(f"{x:.2f}" for x in v))
    assert abs(v[0] - sim.VQ_NOM * 1e3) < 0.01 and abs(sim.MV_PER_US - 1.0) < 1e-9


if __name__ == "__main__":
    if sys.argv[1:]:
        for name in sys.argv[1:]:
            globals()[name]()
        sys.exit(0)
    for fn in (p1_1, p1_2, p2_1, p2_2, p2_3, p2_4, p3_1, p3_2, p3_3, p3_4, p3_5, p4_1, p4_2, p4_3, p4_4):
        fn()
