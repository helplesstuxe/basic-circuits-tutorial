#!/usr/bin/env python3
"""02 同相放大：ngspice + TI LM358B 官方模型复核页面数值。从仓库根运行：python spice/02/run.py"""
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

d = ngspice("dc_noninv.cir", need=["voa", "vma", "vob", "voc", "voe", "vor", "vok", "voq"])
r = ngspice("dc_ramp.cir", need=["vod", "voh", "vom"])
i = ngspice("dc_inv.cir", need=["vof", "von", "voi"])
s = ngspice("dc_sum.cir", need=["vpl", "vol"])
g = ngspice("dc_ol.cir", need=["vog"])
row("p1 §二", "0.5 V 输入 → 输出", 1.5, d["voa"], "V")
row("p1 §二", "−0.2 V 输入 → 输出", -0.6, d["vob"], "V")
row("p2 §一 第二步", "反相端 = 输出 × 1/3", d["voa"] / 3, d["vma"], "V", "页面值取 SPICE 输出 ÷ 3")
row("p1 §四 第2步", "Rf=40k 倍数", 5.0, d["voc"] / 0.5, "")
row("p1 §四 第2步", "Rf=0 倍数", 1.0, r["vod"] / 0.5, "")
row("p1 §四 第3步", "串 100k 后输出（不变）", 1.5, d["voe"], "V")
row("p1 §四 第3步", "对照 01 反相串 100k：10/110×0.5", -0.4545, i["vof"], "V")
row("p1 §四 第5步", "拔掉 Rf 输出贴电源", None, g["vog"], "V", "页面定性：贴到电源边")
row("p2 图02-p2-3", "同一对电阻 反相倍数", -2.0, i["voi"] / 0.5, "")
row("p2 例1", "内阻 20k 10k/91k 0.5 V → 输出", 5.05, r["voh"], "V")
row("p2 例2", "10k/30k 0.3 V → 输出", 1.2, d["vok"], "V")
row("p2 例3", "同相端", 0.35, s["vpl"], "V")
row("p2 例3", "输出", 0.7, s["vol"], "V")
row("p3 练习1", "2k/18k 0.25 V → 输出", 2.5, r["vom"], "V")
row("p3 练习2", "反相 内阻 50k → 输出", -0.333, i["von"], "V")
row("p3 练习2", "同相 内阻 50k → 输出", 3.0, d["voq"], "V")
row("补充", "内阻 1 MΩ 同相 0.5 V → 输出", 1.5, d["vor"], "V", "IB 流过 1 MΩ 的影响")

a = ngspice("ac.cir", need=["ga", "gb", "gc", "gd", "gh", "bwe", "bwf", "bwg", "bwh", "bwk", "gl", "zl"])
row("p2 仿真/图02-p2-2", "内阻 1k 反相倍数", 1.82, a["ga"], "")
row("p2 仿真/图02-p2-2", "内阻 100k 反相倍数", 0.18, a["gb"], "")
row("p2 图02-p2-2", "内阻 100 Ω 同相倍数", 3.0, a["gc"], "")
row("p2 图02-p2-2", "内阻 1 MΩ 同相倍数", 3.0, a["gd"], "")
row("p2 例1", "倍数（10k/91k）", 10.1, a["gh"], "")
row("p3 图02-p3-2", "2 倍带宽", 600e3 / 1e3, a["bwe"] / 1e3, "kHz", "模型 GBW 偏大且低增益时更快")
row("p3 图02-p3-2 / §2", "10 倍带宽", 120, a["bwf"] / 1e3, "kHz", "页面估算偏保守")
row("p3 图02-p3-2", "100 倍带宽", 12, a["bwg"] / 1e3, "kHz", "页面估算偏保守")
row("p2 例1 第4步", "带宽", 120, a["bwh"] / 1e3, "kHz", "页面估算偏保守")
row("p3 练习3(3)", "4 倍带宽", 300, a["bwk"] / 1e3, "kHz", "页面估算偏保守")
row("p3 §一.3 交流耦合", "1 kHz 倍数", 3.0, a["gl"], "")
row("p3 §一.3 交流耦合", "信号源看到的输入电阻", 100, a["zl"] / 1e3, "kΩ")

t = ngspice("t_scope.cir", need=["omax", "omin", "tpk", "omax40"])
row("p1 §四 第1步/图02-p1-3", "0.5 V 峰值 → 输出峰值", 1.5, t["omax"], "V")
row("p1 §四 第1步/图02-p1-3", "输出最低", -1.5, t["omin"], "V")
row("p1 图02-p1-3", "输出到顶时刻（第2周期）", 1.25, t["tpk"] * 1e3, "ms", "与输入同时到顶")
row("p1 §四 第2步", "Rf=40k 输出峰值", 2.5, t["omax40"], "V")
t = ngspice("t_ss3.cir", need=["omax", "vclip"])
row("p1 §四 第4步", "单 5 V、3 倍：输出不动的电平", 3.5, t["omax"], "V", "手册 V+−1.35～1.5 V")
row("p1 §四 第4步", "单 5 V、3 倍：开始不动的输入", 1.17, t["vclip"], "V")
t = ngspice("t_ss2.cir", need=["omax", "vclip"])
row("p3 §1/图02-p3-1", "单 5 V 输出上限", 3.5, t["omax"], "V", "手册 V+−1.35～1.5 V")
row("p3 §1/图02-p3-1", "2 倍开始削顶的输入", 1.75, t["vclip"], "V")
t = ngspice("t_cm.cir", need=["omax", "vfail"])
row("p3 §1 共模上限", "跟随器输出最高", 3.5, t["omax"], "V")
row("p3 §1 共模上限", "跟随失效时的输入", 3.5, t["vfail"], "V")
t = ngspice("t_ex3.cir", need=["vo08", "omax"])
row("p3 练习3(1)", "0.8 V → 输出", 3.2, t["vo08"], "V")
row("p3 练习3(2)", "削顶上限（余量 = 上限 − 3.2）", 3.5, t["omax"], "V", "余量页面 0.3 V")
t = ngspice("t_ex4g2.cir", need=["omax", "omin", "pmax", "bavg"])
row("p3 练习4", "偏置点", 2.5, t["bavg"], "V")
row("p3 练习4", "2 倍：理想最高 4.5 V → 实际（削顶）", 3.5, t["omax"], "V", "确实削顶")
row("p3 练习4", "2 倍：最低", 0.5, t["omin"], "V")
row("p3 练习4", "同相端最高", 3.5, t["pmax"], "V")
t = ngspice("t_ex4g1.cir", need=["omax", "omin"])
row("p3 练习4 改法", "1 倍：输出最高", 3.5, t["omax"], "V")
row("p3 练习4 改法", "1 倍：输出最低", 1.5, t["omin"], "V")

report("02 同相放大")
