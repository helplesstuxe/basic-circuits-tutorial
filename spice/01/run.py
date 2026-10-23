#!/usr/bin/env python3
"""01 反相放大：ngspice + TI LM358B 官方模型复核页面数值。从仓库根运行：python spice/01/run.py"""
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

d = ngspice("dc.cir", need=["voa", "vma", "ia", "vob", "voc", "vod", "voe", "ie", "vof", "vog", "voh", "vok"])
row("p1 §一", "0.5 V 输入 → 输出", -5.0, d["voa"], "V")
row("p1 §一", "−0.2 V 输入 → 输出", 2.0, d["vob"], "V")
row("p1 §五 第2步", "Rf=47k 倍数", -4.7, d["voc"] / 0.5, "")
row("p1 §五 第2步", "Rf=10k 倍数（反相器）", -1.0, d["vod"] / 0.5, "")
row("p1 §五 第5步", "反相端对地（零点几毫伏）", None, d["vma"] * 1e3, "mV", "页面只给定性描述")
row("p2 §一 第二步", "I = Vi/R1", 0.05, d["ia"] * 1e3, "mA")
row("p2 §一 验算(P3)", "Vo（A=10万）", -4.99945, d["voa"], "V")
row("p2 §一 验算(P3)", "反相端约 50 µV", 0.050, d["vma"] * 1e3, "mV", "实测由失调电压主导")
row("p2 例1", "Vo", -2.0, d["voe"], "V")
row("p2 例1", "电流", 0.1, d["ie"] * 1e3, "mA")
row("p2 例2", "Vo", -1.5, d["vof"], "V")
row("p2 例3", "加法器 0.5+0.2", -0.7, d["vog"], "V")
row("p3 练习1", "Vo", 2.0, d["voh"], "V")
row("p3 练习4", "混音器 Vo", -0.8, d["vok"], "V")

a = ngspice("ac.cir", need=["ga", "gb", "gc", "gd", "gh", "bwe", "bwf", "bwg", "bwh", "a12", "vo12", "vm12", "g50"])
row("p3 图01-p3-1", "Rs=1k, R1=10k 倍数", 9.09, a["ga"], "")
row("p3 图01-p3-1", "Rs=1k, R1=1k 倍数", 5.00, a["gb"], "")
row("p3 图01-p3-1", "Rs=100, R1=1k 倍数", 9.09, a["gc"], "")
row("p3 图01-p3-1", "Rs=100, R1=10k 倍数", 9.90, a["gd"], "")
row("p3 图01-p3-2", "倍数1 带宽", 600, a["bwe"] / 1e3, "kHz", "页面按手册 GBW 1.2MHz")
row("p3 图01-p3-2 / §一.4", "倍数10 带宽", 109, a["bwf"] / 1e3, "kHz", "TI 模型 GBW 偏快")
row("p3 图01-p3-2", "倍数100 带宽", 11.9, a["bwg"] / 1e3, "kHz")
row("p2 §一 GBW", "1.2 kHz 时运放自身 A", 1000, a["a12"], "")
row("p2 §一 GBW", "1.2 kHz 时输出幅度", 4.946, a["vo12"], "V", "A 带 90° 相移，误差是二阶小量")
row("p2 §一 GBW", "1.2 kHz 时误差", 1.1, (1 - a["vo12"] / 5) * 100, "%")
row("p2 §一 GBW", "1.2 kHz 时反相端", 5.0, a["vm12"], "mV")
row("(补充)", "10 倍电路 50 kHz 倍数", 10 / (1 + (50 / 109) ** 2) ** 0.5, a["g50"], "", "按页面 fc=109k 公式")
row("p3 练习2(1)", "倍数（含 500 Ω 内阻）", 19.4, a["gh"], "")
row("p3 练习2(3)", "带宽", 57, a["bwh"] / 1e3, "kHz")

t = ngspice("t_sine.cir", need=["amax", "amin", "aat", "bat", "cmax"])
row("p1 §五 第1步 / p2 图01-p2-2 左", "输出峰值", 5.0, t["amax"], "V")
row("p1 §五 第1步 / p2 图01-p2-2 左", "0.25 ms 时输出（最低点）", -5.0, t["aat"], "V")
row("p1 图01-p1-3", "比值2，0.25 ms 时输出", -1.0, t["bat"], "V")
row("p1 §五 第2步", "Rf=47k 输出峰值", 2.35, t["cmax"], "V")
t = ngspice("t_ramp.cir", need=["vhi", "vlo", "vih", "vil"])
row("p1 §五 第3步", "正半周开始削平的输入峰值", 1.35, -t["vih"], "V")
row("p1 §五 第3步", "负半周开始削平的输入峰值", 1.49, t["vil"], "V")
row("p3 §一.3", "倍数10 最大输入峰值", 1.35, -t["vih"], "V")
t = ngspice("t_clip.cir", need=["omax", "omin"])
row("p2 仿真/图01-p2-2 右", "1.5 V 输入 削顶上限", 13.5, t["omax"], "V")
row("p2 仿真/图01-p2-2 右", "1.5 V 输入 削底下限", -14.9, t["omin"], "V", "输出经 Rf 吸约 0.15 mA")
t = ngspice("t_offs.cir", need=["omax", "omin"])
row("p1 §五 第4步", "加 0.2 V 偏移 输出最高", 3.0, t["omax"], "V")
row("p1 §五 第4步", "加 0.2 V 偏移 输出最低", -7.0, t["omin"], "V")
t = ngspice("t_sum.cir", need=["omax"])
row("p2 图01-p2-4", "加法器输出最高", 0.70, t["omax"], "V")
t = ngspice("t_ex3.cir", need=["omax", "omin", "vmpk", "vopk"])
row("p3 练习3(1)", "削顶上限", 13.5, t["omax"], "V")
row("p3 练习3(1)", "削底下限", -14.9, t["omin"], "V")
row("p3 练习3(2)", "+2 V 瞬间反相端", 0.46, t["vmpk"], "V", "按 −14.4 V 重算为 0.51 V")
t = ngspice("t_ex2.cir", need=["omax", "omin"])
row("p3 练习2", "±12 V 输出最高", 10.5, t["omax"], "V")
row("p3 练习2", "±12 V 输出最低", -11.9, t["omin"], "V")
row("p3 练习2(2)", "最大不削顶输入峰值", 0.53, t["omax"] / a["gh"], "V")
t = ngspice("t_sr.cir", need=["opp", "smax"])
row("p3 §一.4 压摆率", "8 kHz、10 V 峰值时输出峰峰值", 20.0, t["opp"], "Vpp", "未被压摆率拖垮")
row("p3 §一.4 压摆率", "所需最大斜率 2πfVp", 0.503, t["smax"], "V/µs")
t = ngspice("t_ss.cir", need=["omin"])
row("p3 排查表", "单电源负半周平在约 0.1 V", 0.1, t["omin"], "V", "同 P3 ⚠️")

report("01 反相放大")
