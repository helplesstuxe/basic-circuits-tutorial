#!/usr/bin/env python3
"""05 精密整流：ngspice + TI LM741 / TL072 官方模型 + Nexperia 1N4148 复核页面数值。从仓库根运行：python spice/05/run.py"""
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

IDEAL = 0.2 / math.pi          # 峰值 0.2 V 正弦半波整流理想平均值
def err(av):
    return (av / IDEAL - 1) * 100

p = ngspice("t_passive.cir", need=["p02", "p10"])
row("p1 图05-p1-1", "普通二极管 峰值 0.2 V → 输出峰值", 0, p["p02"] * 1e3, "mV", "页面'始终 0 V'；SPICE 2 mV，表上即 0")
row("p1 §一", "普通二极管 峰值 10 V → 输出峰值", 9.3, p["p10"], "V")

d = ngspice("dc_basic.cir", need=["o1", "a1", "o2", "a2", "o3", "o4"])
row("p2 §1 代数", "Vi=0.1 V：Vo", 0.1, d["o1"], "V")
row("p2 §1 代数", "Vi=0.1 V：误差 Vo−Vi", 0.008, (d["o1"] - 0.1) * 1e3, "mV", "LM741 模型失调 1 mV 主导")
row("p2 §1 代数", "Vi=0.1 V：运放脚", 0.8, d["a1"], "V", "1N4148 在 10 µA 只压降约 0.38 V")
row("p2 例1", "Vi=50 mV：运放脚", 0.75, d["a2"], "V")
row("p2 例1", "Vi=50 mV：误差", 0.0075, (d["o2"] - 0.05) * 1e3, "mV")
row("补充", "Vi=10 mV：Vo（门槛已被运放缩小）", 10, d["o4"] * 1e3, "mV")

w = ngspice("dc_wrong.cir", need=["o1", "a1", "o2"])
row("p3 练习4", "反馈接错 0.2 V：输出", 0, w["o1"] * 1e3, "mV", "页面 0")
row("p3 练习4", "反馈接错 0.2 V：运放脚", 0.2, w["a1"], "V")
row("p3 练习4", "反馈接错 2 V：输出", 1.3, w["o2"], "V")

b = ngspice("t_basic741.cir", need=[f"{k}_{f}" for k in ("av", "lo", "hi", "tr") for f in ("1k", "2k", "5k", "10k", "20k")])
row("p2 图05-p2-2", "基本型+741 1 kHz 平均值误差", -3.5, err(b["av_1k"]), "%")
row("p2 图05-p2-2", "过零后输出超过 10 mV 的时间", 60, (b["tr_1k"] - 1e-3) * 1e6, "µs")
row("p2 图05-p2-2", "运放脚负饱和", -13.5, b["lo_1k"], "V")
row("p2 图05-p2-2", "运放脚正半周最高", 0.9, b["hi_1k"], "V")
row("p3 图05-p3-2", "基本型+741 2 kHz 误差", None, err(b["av_2k"]), "%")
row("p3 图05-p3-2", "基本型+741 5 kHz 误差", None, err(b["av_5k"]), "%")
row("p3 图05-p3-1", "基本型+741 10 kHz 误差", -70.3, err(b["av_10k"]), "%")
row("p3 图05-p3-2", "基本型+741 20 kHz 误差", -100, err(b["av_20k"]), "%")

t = ngspice("t_basicTL.cir", need=[f"av_{f}" for f in ("1k", "2k", "5k", "10k", "20k")])
row("p3 §3", "基本型+TL072 1 kHz 误差（'刚好碰 1% 线'）", -1, err(t["av_1k"]), "%")
row("p3 图05-p3-1", "基本型+TL072 10 kHz 误差", -11.8, err(t["av_10k"]), "%")
row("p3 图05-p3-2", "基本型+TL072 20 kHz 误差", None, err(t["av_20k"]), "%")

m = ngspice("t_imp741.cir", need=[f"{k}_{f}" for k in ("av", "lo", "hi") for f in ("1k", "2k", "5k", "10k", "20k")])
row("p2 图05-p2-4", "改进型+741 1 kHz 误差", -0.5, err(m["av_1k"]), "%", "含失调 ×2 约 +1.6%")
row("p2 图05-p2-4", "运放脚最低", -0.70, m["lo_1k"], "V")
row("p2 图05-p2-4", "运放脚最高", 0.90, m["hi_1k"], "V")
row("p3 §3", "改进型+741 2 kHz 误差（'碰 1% 线'）", -1, err(m["av_2k"]), "%")
row("p3 图05-p3-1", "改进型+741 10 kHz 误差", -5.3, err(m["av_10k"]), "%")
row("p3 图05-p3-2", "改进型+741 20 kHz 误差", None, err(m["av_20k"]), "%")

i = ngspice("dc_imp.cir", need=["on", "an", "op", "ap", "o50", "o56", "o50n"])
row("p2 例2", "Vi=−0.1 V：Vo", 0.2, i["on"], "V")
row("p2 例2", "Vi=−0.1 V：运放脚", 0.9, i["an"], "V")
row("p2 例2", "Vi=+0.1 V：运放脚", -0.7, i["ap"], "V")
row("p2 例2", "Vi=+0.1 V：Vo", 0, i["op"] * 1e3, "mV", "页面 0")
row("p3 练习3", "Rf=50k、Rs=1k 增益", 4.55, i["o50"] / 0.1, "", "含失调和偏置电流")
row("p3 练习3", "Rs 引起的增益比例（有/无 Rs）", 10 / 11, i["o50"] / i["o50n"], "")
row("p3 练习3", "Rf=56k、Rs=1k 增益", 5.09, i["o56"] / 0.1, "")

q = ngspice("t_pulse.cir", need=["pmax", "sat", "trec"])
row("p3 练习1", "20 µs 正脉冲 输出最大", 0, q["pmax"] * 1e3, "mV", "页面'一直是 0'")
row("p3 练习1", "负饱和", -13.5, q["sat"], "V")
row("p3 练习1", "0.2 V 阶跃后输出超过 10 mV 的时间（≥28.4 µs）", 28.4, (q["trec"] - 1.0001e-3) * 1e6, "µs", "页面：按 SR 下限，实际更慢")

x = ngspice("t_x5.cir", need=["av"])
row("p3 练习5", "峰值 0.1 V 半波平均", 31.8, x["av"] * 1e3, "mV", "改进型实测，含失调")

report("05 精密整流")
