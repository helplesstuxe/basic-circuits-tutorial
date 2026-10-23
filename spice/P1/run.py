"""P1 元件速成：用 ngspice 核对页面数值。在仓库根目录运行：python spice/P1/run.py"""
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
    if r.returncode != 0 or miss or re.search(r"(?i)fatal error|failed|error on line", out):
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

d = ngspice("divider.cir", need=["va", "vb", "vc", "isc"])
row("p1 图P1-p1-1", "12V 10k/10k 输出", 6.0, d["va"], "V")
row("p2 §1 图P1-p2-1", "RL=10k 时输出", 4.00, d["vb"], "V")
row("p2 §1 图P1-p2-1", "RL=100k 时输出", 5.71, d["vc"], "V")
row("p2 §1", "RL=1M 时输出(≈6V)", 6.0, d["vd"], "V", "页面说几乎不变")
row("p2 §7 戴维南", "短路电流", 1.20, d["isc"] * 1e3, "mA")
row("p2 §7 戴维南", "Rth=Voc/Isc", 5.00, d["va"] / d["isc"] / 1e3, "kΩ")
row("p2 §8 例1", "20k/10k 输出", 4.0, d["vf"], "V")
row("p3 图P1-p3-2", "1k+1k 带100k 输出", 6 * (1 - 0.005), d["vg"], "V", "页面:误差0.5%")
row("p3 图P1-p3-2", "1k+1k 电源电流", 6.0, d["ig1"] * 1e3, "mA")
row("p3 图P1-p3-2", "10k+10k 带100k 误差", 4.8, (6 - d["vh"]) / 6 * 100, "%")
row("p3 图P1-p3-2", "100k+100k 带100k 误差", 33.3, (6 - d["vi"]) / 6 * 100, "%")
row("p3 图P1-p3-2", "100k+100k 分压器电流", 0.06, 12 / 200e3 * 1e3, "mA", "页面指空载 12V/200k")
row("p3 练习1", "9V 20k/10k 输出", 3.0, d["vk"], "V")
row("p3 练习1", "电流", 0.3, d["ik"] * 1e3, "mA")
row("p3 练习3", "10k/10k 带10k", 4.0, d["vb"], "V")
row("p3 练习3", "1k/1k 带10k 输出", 5.71, d["vj"], "V")
row("p3 练习3", "10k/10k 空载电流", 0.6, d["ia1"] * 1e3, "mA")
row("p3 练习3", "1k/1k 带10k 上电阻电流", 6.0, d["ij1"] * 1e3, "mA", "页面指分压器自身(空载)电流 12V/2k")

r = ngspice("rc.cir", need=["v1t", "v5t", "v6t"])
row("p2 §3 图P1-p2-2", "1τ 电压", 3.161, r["v1t"], "V")
for k, p in zip(("v1t", "v2t", "v3t", "v4t", "v5t"), (63.2, 86.5, 95.0, 98.2, 99.3)):
    row("p2 §3 百分比表", f"{k[1]}τ 百分比", p, r[k] / 5 * 100, "%")
row("p2 §3", "5τ 电压", 4.966, r["v5t"], "V")
row("p2 §3", "断电后 1τ(t=6τ)", 1.826, r["v6t"], "V")
row("p3 图P1-p3-1", "4.7k: 2.35 s 时", 4.97, r["c47"], "V")
row("p3 图P1-p3-1", "10k: τ", 1.0, r["tau10"], "s")
row("p3 图P1-p3-1", "22k: τ", 2.2, r["tau22"], "s")
row("p3 图P1-p3-1", "22k: 11 s(5τ)时", 4.97, r["c22_11"], "V")
row("p3 练习2", "4.7 s 时(10 V 源)", 6.32, r["c3_47"], "V")
row("p3 练习2", "23.5 s(5τ)时", 9.93, r["c3_235"], "V", "页面只说 5τ=23.5s 基本充满")
row("p2 §8 例2", "47k·10µF τ", 0.47, r["tau4"], "s")

q = ngspice("square.cir", need=["amax", "bmax"])
row("p2 §4 图P1-p2-3", "半周期3τ 最高", 4.76, q["amax"], "V")
row("p2 §4 图P1-p2-3", "半周期3τ 最低", 0.24, q["amin"], "V")
row("p2 §4 图P1-p2-3", "半周期1τ 最高", 3.65, q["bmax"], "V")
row("p2 §4 图P1-p2-3", "半周期1τ 最低", 1.34, q["bmin"], "V")
row("p2 §4 图P1-p2-3", "半周期1τ 平均", 2.5, q["bavg"], "V")

f = ngspice("flyback.cir", need=["vpk1", "i2_1m", "t2_01ma"])
row("p2 §5 图P1-p2-4", "无二极管 开关尖峰", 1212, f["vpk1"], "V", "开关两端=I×10k")
row("p2 §5 图P1-p2-4", "无二极管 10µs 时电流(≈1/e)", 120 * 0.368, f["i1_10u"] * 1e3, "mA", "页面:约10µs降下来")
row("p2 §5 图P1-p2-4", "1N4007 续流 开关电压", 12.7, f["vsw2"], "V")
row("p2 §5 图P1-p2-4", "1N4007 断开后1ms电流", 39.7, f["i2_1m"] * 1e3, "mA")
row("p2 §5 图P1-p2-4", "1N4148 断开后1ms电流", 39.7, f["i3_1m"] * 1e3, "mA")
row("p2 §5 图P1-p2-4", "1N4007 降到0.1mA时刻", 2.90, (f["t2_01ma"] - 1e-3) * 1e3, "ms", "真实二极管无'突然到0'，取0.1mA")
row("p2 §5 图P1-p2-4", "1N4007 降到1mA时刻", 2.90, (f["t2_1ma"] - 1e-3) * 1e3, "ms")
row("p3 练习7", "接通后1ms电流", 75.9, f["i4_1"] * 1e3, "mA")
row("p3 练习7", "接通后5ms电流", 119.2, f["i4_5"] * 1e3, "mA")
row("p3 参数表 G5V-1", "0.85H/960Ω τ", 0.89, f["t5"] * 1e3, "ms")
row("p3 参数表 G5V-1", "1.63H/960Ω τ", 1.70, f["t6"] * 1e3, "ms")

b = ngspice("battery.cir", need=["vb", "vd", "vf"])
row("p2 §7 内阻例", "5V r=25Ω 接50Ω", 3.33, b["vb"], "V")
row("p2 §7 内阻例", "9V r=3.33Ω 接30Ω", 8.1, b["vf"], "V")
row("p2 §7 内阻例", "9V r=3.33Ω 接10Ω", 6.75, b["vd"], "V")

report("P1 元件速成")
