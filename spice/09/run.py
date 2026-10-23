#!/usr/bin/env python3
"""09 开关电源：异步/同步降压（12 V 低压侧）复核；反激初级接市电，不仿真。"""
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

K = ["vo", "vpp", "ilmin", "ilmax", "vswlo", "vswhi", "sup", "sdn", "pd", "idav", "pin", "pout", "pq"]
run = lambda f: ngspice(f, need=K)
a = run("b_async.cir")
a417 = run("b_async417.cir")
i01, i05, i09 = run("b_ideal01.cir"), run("b_ideal05.cir"), run("b_ideal09.cir")
l01, l05, l09 = run("b_loss01.cir"), run("b_loss05.cir"), run("b_loss09.cir")
sy = run("b_sync.cir")
e2 = run("b_ex2.cir")
e3d, e3s = run("b_ex3d.cir"), run("b_ex3s.cir")
si = run("b_p1si.cir")
p47, p375 = run("b_p3_47.cir"), run("b_p3_375.cir")

PX = 0.024 + 0.060      # 页面示意的开关过渡 + 控制芯片损耗（SPICE 里没有这两项，按页面值加上）
dcr = lambda d: d["pin"] - d["pout"] - d["pd"] - d["pq"]
# ---- 主例：12 V -> 5 V、1 A，D = 0.441 ----
row("p1 图09-p1-2 / p2 §六", "V_o 平均（D=0.441）", 5.01, a["vo"], "V")
row("p1 图09-p1-2 / p2 §六", "输出纹波峰峰", 4.3, a["vpp"] * 1e3, "mV", "p2 公式 4.1 mV；p1 写“约 4 mV”")
row("p1 图09-p1-2 / p2 §六", "电感电流最小", 0.84, a["ilmin"], "A")
row("p1 图09-p1-2 / p2 §六 / p3 表", "电感电流最大（峰值）", 1.16, a["ilmax"], "A")
row("p1 图09-p1-2", "开关节点高电平", 12, a["vswhi"], "V")
row("p1 §二 / p2 图09-p2-2", "开关节点低电平（二极管压降）", -0.4, a["vswlo"], "V", "Vishay 1N5822 在约 1 A 时")
row("p2 §三 / §六", "含损耗上升斜率", 147, a["sup"], "A/ms")
row("p2 §三 / §六", "含损耗下降斜率", 116, a["sdn"], "A/ms")
row("p2 §六", "一个周期升降量", 0.324, a["ilmax"] - a["ilmin"], "A")
row("p2 例1", "电感电流范围下限（0.85～1.15 A）", 0.85, a["ilmin"], "A", "页面按理想 D 算 ΔI_L 0.310 A")
row("p1 §四 / p2 §六", "用理想占空比 0.417 时 V_o", 4.71, a417["vo"], "V")
# ---- 占空比扫描 ----
row("p2 图09-p2-3", "理想元件 D=0.5", 6.00, i05["vo"], "V")
row("p2 图09-p2-3", "理想元件 D=0.9", 10.80, i09["vo"], "V")
row("p2 图09-p2-3", "含损耗 D=0.5", 5.71, l05["vo"], "V")
row("p2 图09-p2-3", "含损耗比公式低（D=0.1）", 0.3, 1.2 - l01["vo"], "V", f"D=0.9 时低 {10.8 - l09['vo']:.2f} V")
# ---- 损耗拆分 ----
row("p2 §七 / p3 表 / 图09-p3-2", "肖特基续流损耗", 0.223, a["pd"], "W", "p2 写 0.22 W")
row("p3 表", "二极管平均电流", 0.56, a["idav"], "A")
row("p3 图09-p3-2", "上管导通损耗", 0.022, a["pq"], "W", "SPICE 理想开关几乎没有过渡损耗")
row("p3 图09-p3-2", "电感铜损", 0.050, dcr(a), "W")
row("p3 图09-p3-2", "异步总损耗（SPICE 导通损耗 + 页面过渡/芯片 0.084 W）", 0.38, a["pin"] - a["pout"] + PX, "W")
row("p1 §三 / p3 §五", "异步效率", 92.9, a["pout"] / (a["pin"] + PX) * 100, "%", f"只算 SPICE 导通损耗时 {a['pout'] / a['pin'] * 100:.1f}%")
row("p2 §七 / p3 图09-p3-2", "同步下管损耗", 0.029, sy["pd"], "W", "含 2×20 ns 死区里体二极管（1N5822 代）的约 3 mW")
row("p3 图09-p3-2", "同步总损耗（同上加 0.084 W）", 0.18, sy["pin"] - sy["pout"] + PX, "W")
row("p3 §五", "同步效率", 96.5, sy["pout"] / (sy["pin"] + PX) * 100, "%")
# ---- 例题、练习 ----
row("p2 例2", "24 V 时 ΔI_L", 0.42, e2["ilmax"] - e2["ilmin"], "A")
row("p2 例3", "3.3 V/2 A 肖特基续流损耗", 0.58, e3d["pd"], "W", f"V_o {e3d['vo']:.2f} V，1N5822 在 2 A 时压降 {-e3d['vswlo']:.2f} V")
row("p2 例3", "3.3 V/2 A 下管损耗", 0.145, e3s["pd"], "W", f"V_o {e3s['vo']:.2f} V，含死区体二极管")
row("p2 例3", "同步省下的损耗", 0.44, e3d["pd"] - e3s["pd"], "W")
row("p3 练习3", "24→5 V、2 A、33 µH：ΔI_L", 0.6, p47["ilmax"] - p47["ilmin"], "A")
row("p3 练习3", "电感电流峰值", 2.3, p47["ilmax"], "A")
row("p3 练习3", "C=37.5 µF 时输出纹波", 10, p375["vpp"] * 1e3, "mV")
row("p3 练习3", "取 47 µF 时输出纹波（≤10 mV）", None, p47["vpp"] * 1e3, "mV")
row("p3 练习1", "换硅二极管后多出的损耗（题设 0.7 V、关断够快）", 0.17, (si["pin"] - si["pout"]) - (a["pin"] - a["pout"]), "W",
    f"1N4007 模型（TT 4.32 µs）：输入 {si['pin']:.2f} W，输出掉到 {si['vo']:.2f} V，正向压降 {-si['vswlo']:.2f} V")
report("09 开关电源（12 V 低压侧）")
