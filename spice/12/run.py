#!/usr/bin/env python3
"""12 积分电路：ngspice + TI LM358B（LMx58B_LM2904B 官方模型）复核页面数值。从仓库根运行：python spice/12/run.py"""
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
from concurrent.futures import ThreadPoolExecutor

# 各网表互不依赖，并行跑（t_rfsweep 仿 2 s、t_p4 仿 3600 s，比较慢）
JOBS = {
    "area": ("t_area.cir", ["d2", "d3", "d5"]),
    "sq": ("t_square.cir", ["slope", "tp_s500", "tp_s250", "tp_s5k", "pp_s5k", "tp_ex1", "tp_ex2", "tp_p3", "tp_c5n", "mn_c5n", "tp_c1u", "pp_c1u"]),
    "ac": ("ac.cir", ["g159", "p159", "g0", "fc", "g318", "r16", "p16", "fc318", "fc31", "gbw"]),
    "ramp": ("t_ramp.cir", ["d10", "vmax", "dmax"]),
    "dr": ("t_drift.cir", ["vsat", "t135", "drift", "pend", "ppp", "p02", "tau"]),
    "rf": ("t_rfsweep.cir", ["c_r10k", "c_r100k", "c_r1m", "c_r10m", "bp_r10k", "bp_r100k", "bp_r1m"]),
    "p2": ("t_p2.cir", ["t135", "pfin"]),
    "p4": ("t_p4.cir", ["v10", "qr", "qend", "zr", "zend", "wend", "wsat"]),
    "dmm": ("dmm.cir", ["o0", "m0", "o5", "m5", "o20", "m20", "o250", "ivp"]),
}
with ThreadPoolExecutor(len(JOBS)) as ex:
    fut = {k: ex.submit(ngspice, c, n) for k, (c, n) in JOBS.items()}
    R = {k: f.result() for k, f in fut.items()}
a, sq, ac, rp, dr, rf, p2, p4 = (R[k] for k in ("area", "sq", "ac", "ramp", "dr", "rf", "p2", "p4"))

# 直觉篇
row("p1 图12-p1-1 ①", "2 ms 时输出", -2.0, a["d2"], "V", "+1 V 维持 2 ms，RC 1 ms")
row("p1 图12-p1-1 ②", "3 ms 时输出（记忆）", -2.0, a["d3"], "V", "输入 0 V 的 1 ms 内保持")
row("p1 图12-p1-1 ③", "5 ms 时输出", -1.0, a["d5"], "V", "−0.5 V 维持 2 ms 后")
row("p1 图12-p1-3/第1步", "±1 V 500 Hz 三角波峰峰值", 1.0, sq["tp_s500"], "V", "取边沿前 2 μs 的拐点相减")
row("p1 图12-p1-3 说明", "斜边斜率", 1.0, abs(sq["slope"]), "V/ms", "")
row("p1 第2步", "250 Hz 峰峰值", 2.0, sq["tp_s250"], "V", "")
row("p1 第2步", "5 kHz 三角波峰峰值（拐点）", 0.1, sq["tp_s5k"], "V", "")
row("p1 第2步", "5 kHz 示波器读到的峰峰值（含边沿尖刺）", 0.1, sq["pp_s5k"], "V", "方波每个边沿处有约 0.1 V 尖峰、随后约 6 μs 的台阶（LM358B 输出级交越）")
row("p1 第3步", "159 Hz 正弦增益", 1.0, ac["g159"], "倍", "并 R_f 1 MΩ 的实用积分器")
row("p1 第3步", "159 Hz 相位差（四分之一周期）", 90.0, ac["p159"], "°", "")
row("p1 第3步", "频率高一倍（318 Hz）增益减半", 0.5, ac["g318"], "倍", "")
row("p1 第4步", "20 mV 偏置撞到饱和的时间", 0.6, dr["t135"], "s", "下边沿首次过 −13.5 V")
row("p1 第4步", "饱和后贴住的电压", -13.5, dr["vsat"], "V", "LM358B 负向摆幅接近 −15 V")
row("p1 第5步", "并 1 MΩ 后中心", -2.0, dr["pend"], "V", "0.9–1 s 平均")
# 原理与实现篇
row("p2 结论三/读图 12-p2-3", "漂移速度", 20.0, abs(dr["drift"]), "V/s", "0.1–0.3 s 中心斜率")
row("p2 代码输出/读图 12-p2-3", "撞到 −13.5 V 的时间", 0.627, dr["t135"], "s", "")
row("p2 代码输出/读图 12-p2-3", "实用积分器平均输出", -2.00, dr["pend"], "V", "")
row("p2 读图 12-p2-3", "实用积分器三角波峰峰值", 1.00, dr["ppp"], "V", "拐点相减")
row("p2 读图 12-p2-3", "约 0.2 s 内下沉到 −2 V 附近（0.2 s 时中心）", None, dr["p02"], "V", "定性；0.2 s = 2τ")
row("p2 读图 12-p2-3", "下沉时间常数 R_fC", 0.1, dr["tau"], "s", "由 0.1 s/0.2 s 中心值反算")
row("p2 例题1", "±2 V 250 Hz 峰峰值", 4.0, sq["tp_ex1"], "V", "")
row("p2 例题2", "20 kΩ/47 nF 1 kHz 峰峰值", 0.53, sq["tp_ex2"], "V", "")
row("p2 例题3", "−0.5 V 输入到 +10 V 的时间", 20.0, rp["d10"] * 1e3, "ms", "")
row("p2 例题3", "斜坡最高电压", 13.5, rp["vmax"], "V", "页面按 ±13.5 V 估算")
row("p2 例题3", "最长计时", 27.0, rp["dmax"] * 1e3, "ms", "到最高电压−50 mV 的时间")
# 参数与调试篇
row("p3 §一/练习1", "转角频率 f_c（R_f 1 MΩ, C 100 nF）", 1.6, ac["fc"], "Hz", "")
row("p3 练习1", "直流放大倍数 R_f/R", 100.0, ac["g0"], "倍", "0.05 Hz 处")
row("p3 §一", "16 Hz 时增益 / 理想积分器", 1.0, ac["r16"], "", f"相位 {ac['p16']:.1f}°（理想 90°）")
row("p3 练习1", "R_f=318 kΩ 时 f_c（应 ≤5 Hz）", 5.0, ac["fc318"], "Hz", "")
row("p3 §二 两步法①", "R_f=31.8 kΩ 时 f_c（应 = 50 Hz）", 50.0, ac["fc31"], "Hz", "")
row("p3 §二 两步法②", "R_f=250 kΩ、20 mV 偏置时中心", -0.5, R["dmm"]["o250"], "V", "直流工作点")
row("p3 参数表", "LM358B GBW", 1.2e6, ac["gbw"], "Hz", "同相 101 倍的 −3 dB 频率 × 增益")
for n, pv in (("r10k", -0.02), ("r100k", -0.20), ("r1m", -2.00), ("r10m", -13.01)):
    row("p3 图12-p3-1(a)", f"R_f={n[1:]} 输出中心", pv, rf["c_" + n], "V", "±1 V 500 Hz + 20 mV，1.9–2 s 平均")
for n, pv in (("r10k", 0.93), ("r100k", 1.00), ("r1m", 1.00)):
    row("p3 图12-p3-1(b)", f"R_f={n[1:]} 三角波峰峰值", pv, rf["bp_" + n], "V", "无偏置，拐点相减")
row("p3 图12-p3-2", "C=5 nF 理论峰峰值", 20.0, sq["tp_c5n"], "V", "拐点相减")
row("p3 图12-p3-2", "C=5 nF 削平电压", -13.5, sq["mn_c5n"], "V", "")
row("p3 图12-p3-2", "C=1 μF 峰峰值", 0.10, sq["tp_c1u"], "V", f"含边沿尖刺读数 {sq['pp_c1u']:.3f} V")
row("p3 练习2", "5 mV 偏置漂到 −13.5 V 的时间", 27.0, p2["t135"], "s", "含模型自带失调/偏置电流")
row("p3 练习2", "并 1 MΩ 后最终偏移", -0.5, p2["pfin"], "V", "")
row("p3 练习3", "68 nF 时峰峰值", 3.68, sq["tp_p3"], "V", "")
row("p3 练习4", "1 A 持续 10 s 输出变化", -5.0, p4["v10"], "V", "页面“5 V（输出为负也行）”")
row("p3 练习4", "1 mV 失调单独造成的漂移", 5.0, abs(p4["qr"] - p4["zr"]) * 1e3, "mV/s", "加/不加 1 mV 两次相减")
row("p3 练习4", "LM358B 自身（不加 1 mV）漂移", None, p4["zr"] * 1e3, "mV/s", "偏置电流 ~10 nA 流过 1 μF")
row("p3 练习4", "1 h 后输出（不加 1 mV，仅模型自带）", None, p4["zend"], "V", "")
row("p3 练习4", "1 mV 失调 1 h 累计（漂移速度 × 3600 s）", 18.0, abs(p4["qr"] - p4["zr"]) * 3600, "V", "")
row("p3 练习4", "1 h 后输出（再串 +1 mV）", None, p4["qend"], "V", "两项方向相反部分抵消")
row("p3 练习4", "1 h 后输出（再串 −1 mV，与自身漂移同向；页面“早已饱和”）", None, p4["wend"], "V", f"{p4['wsat']:.0f} s 时过 −13.5 V，已饱和")
report("12 积分电路")
dm = R["dmm"]
print("---- 面包板万用表（直流档，黑表笔接地；R_f 1 MΩ 并在 C 上）----")
for k, txt in (("0", "输入接地"), ("5", "输入 +5 mV"), ("20", "输入 +20 mV")):
    print(f"{txt:<10} 输出(1 脚) {dm['o' + k]:+.4f} V   反相端(2 脚) {dm['m' + k] * 1e3:+.3f} mV")
print(f"R_f 换 250 kΩ、输入 +20 mV：输出(1 脚) {dm['o250']:+.4f} V")
print(f"+15 V 电源电流：每个运放单元约 {dm['ivp'] / 4 * 1e3:.3f} mA（dmm.cir 里 4 个单元合计 {dm['ivp'] * 1e3:.3f} mA）")
