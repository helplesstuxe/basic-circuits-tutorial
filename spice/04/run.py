#!/usr/bin/env python3
"""04 差分放大：ngspice + TI LM358B 官方模型复核页面数值。从仓库根运行：python spice/04/run.py"""
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

d = ngspice("dc.cir", need=["o_p1a", "o_p1b", "o_p2d", "p_p2d", "o_e1b", "p_e1b", "o_e2", "p_e2", "o_x1", "o_bal", "o_x4", "p_x4", "o_z0"])
row("p1 §二 代数", "2.01/2.00 V → 输出", 0.1, d["o_p1a"], "V", "含失调 ×11 ≈ 3.3 mV")
row("p1 §二 / p2 例1①", "3.01/3.00 V → 输出", 0.1, d["o_p1b"], "V")
row("p2 例1②", "5.01/5.00 V → 输出", 0.1, d["o_e1b"], "V")
row("p2 例1 第4步", "同相端电压", 4.55, d["p_e1b"], "V")
row("p2 §一 第一步", "V2=2.2 V 同相端", 2.0, d["p_p2d"], "V")
row("p2 §一 第三步", "V1=2.1 V 输出", 1.0, d["o_p2d"], "V")
row("p2 例2", "20k/60k 同相端", 1.125, d["p_e2"], "V")
row("p2 例2", "输出", 0.9, d["o_e2"], "V")
row("p3 练习1", "5k/50k 0.82/0.80 → 输出", 0.2, d["o_x1"], "V")
row("p1 平衡线", "四只 10k，1.3 与 −0.7 相减", 2.0, d["o_bal"], "V")
row("p3 练习4", "共模 12 V 差 0.2 V → 输出（±15 V）", 2.0, d["o_x4"], "V")
row("p3 练习4", "同相端", 10.9, d["p_x4"], "V")
row("补充", "零输入输出偏移", None, d["o_z0"] * 1e3, "mV", "失调 ×(1+R2/R1)")

a = ngspice("ac_cmrr.cir")
def cm(n):
    A1 = complex(a["a1r_" + n], a["a1i_" + n]); A2 = complex(a["a2r_" + n], a["a2i_" + n])
    ad = (A2 - A1).real / 2; acm = abs(A1 + A2)
    return ad, acm, 20 * math.log10(abs(ad) / acm)
for n in ["m", "r4a", "r4b", "wa", "wb", "ga", "gb", "s100", "s1k", "s200"]:
    if "a1r_" + n not in a:
        sys.exit(f"ac_cmrr.cir 缺少 {n}")
m = cm("m"); r4a = cm("r4a"); r4b = cm("r4b"); wa = cm("wa"); wb = cm("wb"); ga = cm("ga"); gb = cm("gb")
s100 = cm("s100"); s1k = cm("s1k"); s200 = cm("s200")
row("补充", "四只匹配：运放自身 CMRR", None, m[2], "dB")
row("p2 §一", "R4 偏 1%：共模倍数", 0.009, r4a[1], "")
row("p2 §一 / p3 §一", "R4 偏 1%：CMRR", 61, r4a[2], "dB")
row("p2 §一", "R4 偏 1%：共模 2 V 漏出", 18, r4a[1] * 2 * 1e3, "mV")
row("p3 图04-p3-1", "只 R4 偏 0.1%：CMRR", 81, r4b[2], "dB", "运放自身 CMRR 开始起作用")
row("p3 图04-p3-1", "四只 1% 最坏：CMRR", 49, wa[2], "dB")
row("p3 图04-p3-1", "四只 0.1% 最坏：CMRR", 69, wb[2], "dB")
row("p3 §二 TI 例", "倍数 1，1% 最坏：CMRR", 34, ga[2], "dB")
row("p3 §二 TI 例", "倍数 1，0.1% 最坏：CMRR", 54, gb[2], "dB")
row("p3 图04-p3-2", "内阻 100 Ω：CMRR", 61, s100[2], "dB")
row("p3 图04-p3-2", "内阻 1 kΩ：CMRR", 41, s1k[2], "dB")
row("p3 图04-p3-2", "内阻 1 kΩ：差分倍数", 9.13, s1k[0], "")
row("p3 练习3", "内阻 200 Ω：差分倍数", 9.81, s200[0], "")
row("p3 练习3", "内阻 200 Ω：共模倍数", 0.018, s200[1], "")
row("p3 练习3", "内阻 200 Ω：2 V 共模残留", 36, s200[1] * 2 * 1e3, "mV")
row("p3 练习4", "1% 最坏 12 V 共模残留", 0.43, wa[1] * 12, "V")
row("p3 练习4", "0.1% 最坏 12 V 共模残留", 0.04, wb[1] * 12, "V")
row("p3 练习4", "0.1% 最坏 共模抑制倍数", 2800, abs(wb[0]) / wb[1], "")

t = ngspice("t_mis.cir", need=["okmax", "bdmax", "shbmax", "shbmin", "shmax", "shmin"])
row("p2 图04-p2-2", "匹配 输出峰值", 100, t["okmax"] * 1e3, "mV", "含失调 3.3 mV")
row("p2 图04-p2-2", "R4 偏 1% 输出峰值", 118, t["bdmax"] * 1e3, "mV")
row("p1 §四 第4步 / p2", "输入短接 R4 偏 1%：50 Hz 残留幅度", 18, (t["shbmax"] - t["shbmin"]) / 2 * 1e3, "mV")
row("p1 §四 第5步", "输入短接 匹配：50 Hz 残留幅度", None, (t["shmax"] - t["shmin"]) / 2 * 1e3, "mV", "理想 0；另有 3.3 mV 直流偏移")

i = ngspice("dc_ina.cir", need=["a1", "a2", "vo", "vrg"])
row("p2 例3", "A2 输出", 2.11, i["a2"], "V")
row("p2 例3", "A1 输出", 1.90, i["a1"], "V")
row("p2 例3", "Rg 电流", 10, i["vrg"] / 1e3 * 1e6, "µA")
row("p2 例3", "Vo（21 倍 × 10 mV）", 0.21, i["vo"], "V")

s = ngspice("t_ss5.cir", need=["o5", "p5", "o3"])
row("p2 例1 第4步", "5 V 单电源 5.01/5.00：输出（应 0.1 V）", None, s["o5"], "V", "共模 4.55 V 超限，输出错误，页面结论成立")
row("对照", "5 V 单电源 3.01/3.00：输出", 0.1, s["o3"], "V")

report("04 差分放大")
