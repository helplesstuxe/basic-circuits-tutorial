#!/usr/bin/env python3
"""02 运放入门：ngspice + TI LM358B 官方 PSpice 模型核对页面数值。从仓库根运行：python spice/02/run.py
本目录 .spiceinit 打开 PSpice 兼容（set ngbehavior=psa），TI 模型需要它。"""
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

o = ngspice("openloop.cir", need=["a0", "fu", "gbw", "vos", "vhi15", "vlo15", "vhi5", "vlo5", "vhis", "vlos"])
row("p1 §二 / p3 参数表", "开环增益 A(典型14万,最小7万)", 140000, o["a0"], "", "TI 模型≈7.5万")
row("p3 参数表", "GBW", 1.2, o["gbw"] / 1e6, "MHz", "|G|×f @10kHz")
row("p3 参数表", "单位增益频率", 1.2, o["fu"] / 1e6, "MHz")
row("p3 参数表", "正摆幅 余量(±15V,10k)", 1.35, 15 - o["vhi15"], "V", "页面 1.35~1.5")
row("p3 参数表", "负摆幅 余量(±15V,10k接地)", 0.1, o["vlo15"] + 15, "V", "要吸收约1.4mA")
row("p3 图02-p3-1", "±5V 上限(10k)", 3.5, o["vhi5"], "V")
row("p3 图02-p3-1", "±5V 下限(10k接地)", -4.9, o["vlo5"], "V")
row("p3 图02-p3-1", "5V单电源 上限(10k)", 3.5, o["vhis"], "V")
row("p3 图02-p3-1", "5V单电源 下限(10k接地)", 0.1, o["vlos"], "V")
row("(参考) 手册 VOS 典型±0.3mV", "模型失调", 0.3, o["vos"] * 1e3, "mV")

s = ngspice("slew.cir", need=["sr", "srf"])
row("p3 参数表", "压摆率 SR 上升", 0.5, s["sr"], "V/µs")
row("p3 参数表", "压摆率 SR 下降", 0.5, s["srf"], "V/µs")

i = ngspice("invamp.cir", need=["vo", "vm", "voa", "vob", "voc", "vod", "vos", "vms"])
row("p2 图02-p2-1 LM358B", "Vo(10k/100k,0.5V)", -4.99945, i["vo"], "V")
row("p2 图02-p2-1 LM358B", "Av", -9.9989, i["vo"] / 0.5, "")
row("p2 图02-p2-1 LM358B", "V-(虚短残差)", 0.050, i["vm"] * 1e3, "mV", "实际由失调电压主导")
row("p2 图02-p2-1 E源A=1e5", "Vo", -4.99945, i["voa"], "V")
row("p2 图02-p2-1 E源A=1e5", "V-", 0.050, i["vma"] * 1e3, "mV")
row("p2 仿真打印 A=100", "Av", -9.0090, i["vob"] / 0.5, "")
row("p2 仿真打印 A=100", "V-", 45.045, i["vmb"] * 1e3, "mV")
row("p2 仿真打印 A=1000", "Av", -9.8912, i["voc"] / 0.5, "")
row("p2 仿真打印 A=1000", "V-", 4.9456, i["vmc"] * 1e3, "mV")
row("p2 例2 A=1e4", "Vo(10k/200k,0.1V)", -1.9958, i["vod"], "V")
row("p2 例2 A=1e4", "V-", 0.20, i["vmd"] * 1e3, "mV")
row("p2 例3 5V单电源", "输出(贴底)", 0.1, i["vos"], "V", "手册:5mV典型/20mV最大(轻载)")
row("p2 例3 5V单电源", "V-", 0.46, i["vms"], "V")

g = ngspice("gainerr.cir", need=["ea", "eb", "ec", "gc12k", "f3c"])
row("p3 图02-p3-2", "G=1 误差(A=14万)", 0.0014, g["ea"], "%", "模型A≈7.5万")
row("p3 图02-p3-2", "G=10 误差", 0.0079, g["eb"], "%")
row("p3 图02-p3-2", "G=100 误差", 0.072, g["ec"], "%")
row("p3 练习3", "G=100 误差(A=7万最小)", 0.14, g["ec"], "%", "模型A接近手册最小值")
row("p3 参数表 GBW", "G=100 时 -3dB 频率", 12, g["f3c"] / 1e3, "kHz", "页面:12kHz附近明显不足")
row("p3 参数表 GBW", "G=100 在12kHz的实际倍数", None, g["gc12k"], "倍")

def tr(cir):
    return ngspice(cir, need=["omax", "omin"])
t = tr("sine_fb.cir")
row("p2 图02-p2-3 负反馈", "输出峰值(正)", 5.0, t["omax"], "V")
row("p2 图02-p2-3 负反馈", "输出峰值(负)", -5.0, t["omin"], "V")
t = tr("sine_ol.cir")
row("p2 图02-p2-3 开环", "方波上限", 13.5, t["omax"], "V")
row("p2 图02-p2-3 开环", "方波下限", -13.5, t["omin"], "V", "LM358B 负侧只差约0.1V")
row("p1 图02-p1-2 开环", "上限(±15V)", 13.5, t["omax"], "V")
t = tr("sine_ex2.cir")
row("p3 练习2(b)", "输出峰值", 1.0, t["omax"], "V")
t = tr("clip15.cir")
row("p3 图02-p3-1 ±15V", "输出峰值(+)", 8.0, t["omax"], "V", "不削顶")
row("p3 图02-p3-1 ±15V", "输出峰值(-)", -8.0, t["omin"], "V")
t = tr("clip5.cir")
row("p3 图02-p3-1 ±5V 10k负载", "削顶上限", 3.5, t["omax"], "V")
row("p3 图02-p3-1 ±5V 10k负载", "削底下限", -4.9, t["omin"], "V", "带载吸电流时负侧余量变大")
t = tr("clip5nl.cir")
row("p3 图02-p3-1 ±5V 无负载", "削顶上限", 3.5, t["omax"], "V")
row("p3 图02-p3-1 ±5V 无负载", "削底下限", -4.9, t["omin"], "V")
t = tr("clipss.cir")
row("p3 图02-p3-1 5V单电源", "上限", 3.5, t["omax"], "V")
row("p3 图02-p3-1 5V单电源", "下限(趴在约0.1V)", 0.1, t["omin"], "V")
t = tr("mid25.cir")
row("p3 练习4(1) 中点2.5V 0.10V峰", "输出最高(理想3.5)", 3.5, t["omax"], "V", "不削顶")
row("p3 练习4(1) 中点2.5V 0.10V峰", "输出最低(理想1.5)", 1.5, t["omin"], "V")
t = tr("mid18.cir")
row("p3 练习4(2) 中点1.8V 0.17V峰", "输出最高(理想3.5)", 3.5, t["omax"], "V", "不削顶")
row("p3 练习4(2) 中点1.8V 0.17V峰", "输出最低(理想0.1)", 0.1, t["omin"], "V")
t = tr("mid25b.cir")
row("p3 练习4 对照 中点2.5V 0.17V峰", "输出最高(被削)", 3.5, t["omax"], "V", "理想应到4.2V，被摆幅限制")
row("p3 练习4 对照", "输出最低(理想0.8)", 0.8, t["omin"], "V")
# 以 SPICE 摆幅（5V 单电源、10k 负载）重算练习4
hi, lo = o["vhis"], o["vlos"]
row("p3 练习4(1)", "中点2.5V 最大输入峰值", 0.10, min(hi - 2.5, 2.5 - lo) / 10, "V", "按SPICE摆幅")
row("p3 练习4(2)", "最佳中点", 1.8, (hi + lo) / 2, "V", "按SPICE摆幅")
row("p3 练习4(2)", "最佳中点最大输入峰值", 0.17, (hi - lo) / 2 / 10, "V", "按SPICE摆幅")

report("02 运放入门")
