#!/usr/bin/env python3
"""22 过载保护：ngspice + TI LM393A、Infineon IRLZ44N、Vishay 1N5822 官方模型复核页面数值。从仓库根运行：python spice/22/run.py"""
# ---- 通用小工具：调用 ngspice -b，解析 .control 里 echo 出来的 "RES 名字 数值" ----
import subprocess, re, sys, pathlib, math
HERE = pathlib.Path(__file__).resolve().parent
ROWS = []

def ngspice(cir, need=()):
    """在本目录下以 batch 模式运行 cir，返回 {名字: 数值}；缺值或出错就报错退出。"""
    r = subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=900)
    out = r.stdout + r.stderr
    vals = {}
    for k, v in re.findall(r"^RES\s+(\S+)\s+(\S+)", out, re.M):
        try:
            vals[k] = float(v)
        except ValueError:
            vals[k] = float("nan")
    miss = [n for n in need if n not in vals or math.isnan(vals[n])]
    if r.returncode != 0 or miss or re.search(r"(?im)fatal error|error on line|aborted|timestep too small|op failed|failed!\s*$", out):
        print(out[-3000:])
        sys.exit(f"ngspice 运行 {cir} 失败（返回码 {r.returncode}，缺少 {miss}）")
    return vals

def row(loc, item, page, spice, unit="", note=""):
    """记录一行：页面位置 / 项目 / 页面值 / SPICE 值 / 偏差%。page 可为 None（页面只给定性描述）。"""
    dev = None if (page in (None, 0) or spice is None) else (spice - page) / abs(page) * 100
    ROWS.append((loc, item, page, spice, unit, dev, note))

def fmt(x):
    if x is None:
        return "—"
    a = abs(x)
    if a == 0:
        return "0"
    if a >= 1000 or a < 0.01:
        return f"{x:.4g}"
    return f"{x:.4g}"

def report(title):
    print(f"==== {title}：页面值 / SPICE 值 / 偏差% ====")
    w = max(len(r[0]) + len(r[1]) for r in ROWS) + 3
    for loc, item, page, spice, unit, dev, note in ROWS:
        d = "   —  " if dev is None else f"{dev:+7.2f}%"
        print(f"{(loc + ' ' + item):<{w}} 页面 {fmt(page):>9} {unit:<3} | SPICE {fmt(spice):>9} {unit:<3} | {d}  {note}")
    print(f"共 {len(ROWS)} 项。")
# ---- 工具结束 ----

import numpy as np

# ---- 图 22-p2-2 的负载：完全照页面代码（同一算法、同一随机种子 3）生成，写成 PWL 给 SPICE ----
def lowpass(x, dt, tau, y0):
    y = np.empty_like(x); v = y0
    for k in range(len(x)):
        v += (x[k] - v) * dt / tau; y[k] = v
    return y

dt = 1e-3
t = np.arange(0, 12, dt)
base = np.interp(t, [0, 1, 6, 11, 12], [1.0, 1.0, 2.6, 1.0, 1.0])
rng = np.random.default_rng(3)
w = lowpass(rng.normal(0, 1, len(t)), dt, 0.01, 0.0)
i_load = base + w * 0.15 / w.std()
with open(HERE / "noise_pwl.inc", "w") as f:
    f.write("* 由 run.py 按 22 原理与实现篇 图 22-p2-2 的页面代码生成：采样电压 = i_load × 0.1 Ω\nVS s 0 PWL(\n")
    for a, b in zip(t, i_load * 0.1):
        f.write(f"+ {a:.4f} {b:.6f}\n")
    f.write("+ )\n")

def flips(fname, t0=None, t1=None):
    d = np.loadtxt(HERE / fname); tt, v = d[:, 0], d[:, 1]
    m = np.ones(len(tt), bool)
    if t0 is not None: m &= tt >= t0
    if t1 is not None: m &= tt <= t1
    tt, v = tt[m], v[m]
    idx = np.nonzero(np.diff((v > 2.5).astype(int)))[0]
    return len(idx), tt[idx]

th = ngspice("th_sweep.cir", need=["vh", "vl", "vh2", "voh", "vol", "ib"])
inv = ngspice("inv_time.cir", need=["a10_5", "a10_20", "a47_5", "a47_20", "a100_5", "a100_20", "ex3"])
sf = ngspice("start_filter.cir", need=["raw", "p10", "p47", "p100", "q47", "q100", "tq47", "i2t"])
st = ngspice("cl_stall.cir", need=["ttrip", "toff", "tper", "ton", "ipk", "irun", "iavg", "vfmax", "vfmin"])
st47 = ngspice("cl_stall47.cir", need=["ttrip", "toff", "tper"])
c3 = ngspice("cl_3a.cir", need=["ttrip", "i3"])
nh = ngspice("cl_nohyst.cir", need=["ttrip", "iavg", "irsavg", "pmos", "vgmin", "vgmax"])
s10 = ngspice("cl_start10.cir", need=["vgmin", "vfpk"])
s47 = ngspice("cl_start47.cir", need=["vgmin", "vfpk"])
dm = ngspice("dmm.cir", need=["run_s", "run_f", "run_p", "run_g", "run_d", "off_s", "off_f", "off_p", "off_g", "off_d"])
ngspice("n_hyst.cir", need=["vgend"]); ngspice("n_nohyst.cir", need=["vgend"])
n_h, t_h = flips("n_hyst_vg.txt")
n_p, t_p = flips("n_nohyst_vg.txt")
n_cl, _ = flips("nohyst_vg.txt", 0.1, 0.5)

VH, VL = th["vh"], th["vl"]
# 直觉篇
row("p1 图22-p1-1", "堵转电流（电机建模前提）", 5, st["ipk"], "A", "电机模型按 5 A 堵转标定")
row("p1 图22-p1-1", "堵转后切断时间", 26, st["ttrip"] * 1e3, "ms", "闭环全电路")
row("p1 §三 图22-p1-2 说明", "1 A 时采样电压", 0.1, dm["run_s"], "V", "闭环电路正常运行")
row("p2 前置知识", "IRLZ44N 导通电阻（栅 5 V，最大）", 25, (dm["run_d"] - dm["run_s"]) / 1.0 * 1e3, "mΩ", "1 A 时 V_DS ÷ 1 A；页面给的是最大值")
# 原理与实现篇
row("p2 推导一", "跳闸门限 V_H", 193, VH * 1e3, "mV", "三角波慢扫")
row("p2 推导一", "恢复门限 V_L", 146, VL * 1e3, "mV", f"LM393 输出低 {th['vol']*1e3:.0f} mV 抬高了 V_L")
row("p2 推导一", "回差", 47, (VH - VL) * 1e3, "mV")
row("p2 推导一", "跳闸电流 V_H/0.1Ω", 1.93, VH / 0.1, "A")
row("p2 推导一", "恢复电流 V_L/0.1Ω", 1.46, VL / 0.1, "A")
row("p2 推导二", "堵转 5 A 切断时间（τ=0.1 s）", 26, inv["a100_5"] * 1e3, "ms", "电流源阶跃，开环判")
row("p2 图22-p2-2", "无回差翻转次数", 10, n_p, "次", "翻转时刻 " + " ".join(f"{x:.2f}" for x in t_p))
row("p2 图22-p2-2", "有回差翻转次数", 2, n_h, "次")
row("p2 图22-p2-2", "有回差跳低时刻", 3.95, t_h[0], "s")
row("p2 图22-p2-2", "有回差恢复时刻", 9.65, t_h[1], "s", "对 V_L 很敏感：V_L 高 2 mV → 提前 0.24 s")
row("p2 例题1(2)", "1 A→3 A 跳闸时间", 62, c3["ttrip"] * 1e3, "ms", f"闭环，3 A 实测 {c3['i3']:.2f} A")
row("p2 例题2", "R_S 0.05 Ω 跳闸电流", 3.86, VH / 0.05, "A", "SPICE 门限 ÷ R_S")
row("p2 例题2", "R_S 0.05 Ω 恢复电流", 2.92, VL / 0.05, "A")
row("p2 例题3", "R_S 0.2 Ω 跳闸电流", 0.96, VH / 0.2, "A")
row("p2 例题3", "R_S 0.2 Ω 恢复电流", 0.73, VL / 0.2, "A")
row("p2 例题3", "0.5 A→3 A 切断时间", 20, inv["ex3"] * 1e3, "ms", "R_S 0.2 Ω，电流源阶跃")
# 参数与调试篇
row("p3 §一 读表", "R_F 10k 上偏置电流压降（最大）", 2.5, (th["vh2"] - VH) * 1e3, "mV", f"模型为典型偏置（总 {th['ib']*1e9:.0f} nA）；页面写的是最大值")
row("p3 图22-p3-1 第一行", "无回差首次切断", 26, nh["ttrip"] * 1e3, "ms")
row("p3 图22-p3-1 第一行", "0.4 s 内翻转次数", 28803, n_cl, "次", f"栅极在 {nh['vgmin']:.2f}～{nh['vgmax']:.2f} V 间摆动")
row("p3 图22-p3-1 第一行", "平均（采样）电流", 1.93, nh["irsavg"], "A", f"电机电流含续流 {nh['iavg']:.2f} A")
row("p3 图22-p3-1 第一行", "MOS 管平均功耗", None, nh["pmos"], "W", "页面只说“发热”")
row("p3 图22-p3-1 第二行", "打嗝断开时间", 28, st["toff"] * 1e3, "ms")
row("p3 图22-p3-1 第二行", "打嗝导通时间", 14, st["ton"] * 1e3, "ms")
row("p3 图22-p3-1 第二行", "打嗝周期", 42, st["tper"] * 1e3, "ms")
row("p3 图22-p3-1 第二行", "导通占比", 34, st["ton"] / st["tper"] * 100, "%")
row("p3 图22-p3-1 第二行", "平均电流", 1.73, st["iavg"], "A")
row("p3 图22-p3-1 第二行", "打嗝中滤波电压上沿", 193, st["vfmax"] * 1e3, "mV")
row("p3 图22-p3-1 第二行", "打嗝中滤波电压下沿", 146, st["vfmin"] * 1e3, "mV")
for tau, k in ((10, "a10"), (47, "a47"), (100, "a100")):
    pg = {10: (2.6, 0.50), 47: (12.4, 2.35), 100: (26.4, 5.00)}[tau]
    row("p3 图22-p3-2(a)", f"τ={tau} ms 5 A 切断", pg[0], inv[k + "_5"] * 1e3, "ms")
    row("p3 图22-p3-2(a)", f"τ={tau} ms 20 A 切断", pg[1], inv[k + "_20"] * 1e3, "ms")
row("p3 图22-p3-2(b)", "未滤波尖峰", 500, sf["raw"] * 1e3, "mV")
row("p3 图22-p3-2(b)", "τ=10 ms 滤波峰值", 278, sf["p10"] * 1e3, "mV")
row("p3 图22-p3-2(b)", "τ=47 ms 滤波峰值", 144, sf["p47"] * 1e3, "mV")
row("p3 图22-p3-2(b)", "τ=100 ms 滤波峰值", 100, sf["p100"] * 1e3, "mV")
row("p3 图22-p3-2(b) 闭环", "τ=10 ms 启动误跳（栅极最低）", None, s10["vgmin"], "V", f"会跳闸，滤波电压被切在 {s10['vfpk']*1e3:.0f} mV")
row("p3 图22-p3-2(b) 闭环", "τ=47 ms 启动峰值", 144, s47["vfpk"] * 1e3, "mV", f"不跳，栅极最低 {s47['vgmin']:.2f} V")
row("p3 练习1", "τ=47 ms 打嗝断开时间", 13, st47["toff"] * 1e3, "ms", f"周期 {st47['tper']*1e3:.1f} ms")
row("p3 练习2", "τ=47 ms 峰值（50 ms 衰减）", 220, sf["q47"] * 1e3, "mV")
row("p3 练习2", "峰值出现时刻", 60, sf["tq47"] * 1e3, "ms")
row("p3 练习2", "τ=100 ms 峰值", 156, sf["q100"] * 1e3, "mV")
row("p3 练习3", "R_S 0.033 Ω 跳闸电流", 5.84, VH / 0.033, "A")
row("p3 练习4", "启动冲击多出的 I²t", 0.32, sf["i2t"], "A²s", "ngspice 积分")
report("22 过载保护")
