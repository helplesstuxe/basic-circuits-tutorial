#!/usr/bin/env python3
"""45 集成功放芯片：ngspice + LM386 行为模型（作者依据 TI SNAS545D 搭建：内部 15k/150/1.35k 增益网络、
两路 50 kΩ 输入电阻、脚7 15k/15k 分压、离电源轨各 1.15 V 的摆幅、静态电流 + 输出电流的电源电流）。
实验电路与 page4 相同：9 V 单电源，脚6 100 µF，脚7 10 µF，输出 220 µF → 10 Ω 限流电阻 → 8 Ω 喇叭，吸收网络 10 Ω + 47 nF。
从仓库根运行：python spice/45/run.py（约 5 秒）。
默认所有仿真输出（*_vg.txt 和抽稀的 CSV）都写到临时目录，不覆盖仓库里的文件；
维护者要更新 code/figs/45_figs.py 画图用的小 CSV 时才加 --update：python spice/45/run.py --update
PAM8403、TPA3116D2、LM7805 没有建 SPICE 模型，相关数字是 code/figs/45_figs.py 里的 Python 计算（见 review/spice/45.md）。"""
# ---- 通用小工具：调用 ngspice -b，解析 .control 里 echo 出来的 "RES 名字 数值" ----
import subprocess, re, sys, pathlib, math, shutil, tempfile
HERE = pathlib.Path(__file__).resolve().parent
# 在临时目录里跑 ngspice（网表里的 ../models 用符号链接指回仓库），原始波形 txt 写在那里
WORK = pathlib.Path(tempfile.mkdtemp(prefix="spice45_")) / "45"
WORK.mkdir()
(WORK.parent / "models").symlink_to(HERE.parent / "models")
for f in list(HERE.glob("*.cir")) + list(HERE.glob("*.inc")):
    shutil.copy(f, WORK)
OUT = HERE if "--update" in sys.argv else WORK          # 小 CSV 的去处
ROWS = []

def ngspice(cir, need=()):
    """在临时目录下以 batch 模式运行 cir，返回 {名字: 数值}；缺值或出错就报错退出。"""
    r = subprocess.run(["ngspice", "-b", cir], cwd=WORK, capture_output=True, text=True, timeout=1500)
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
    if x == 0:
        return "0"
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

class _P(dict):
    def __missing__(self, k):
        return None
# 页面上写的数值（照 SPICE 结果写进页面后填回这里）
P = _P({
    "vout": 4.5, "vbyp": 4.5, "iq_mA": 4.3,
    "g20_1k": 20, "g200_1k": 199, "g200_200": 173, "g200_100": 130, "g200_20": 38.8,
    "bw20": 300e3, "bw200": 31.8e3, "fhp": 40.2,
    "vin_pk": 0.121, "vout_pk": 2.43, "vsp_pk": 1.08, "pin": 0.425, "pspk": 0.0725, "plim": 0.0907,
    "isup_mA": 47.2, "pchip": 0.261, "outb_max": 7.85, "outb_min": 1.15,
    "rip_cap_mV": 0.44, "rip_open_mV": 20.6,
    "vw_pk": 0.0121, "g200pot_pk": 2.41,
    "pc_max": 0.267, "a_pcmax": 0.14, "pl_max": 0.284, "pl_1": 0.00111, "pin_1": 0.0705,
})

# 1) 静态
v = ngspice("op.cir", ["vout", "vbyp", "iq_mA"])
row("p4 测量表", "脚5 静态直流", P["vout"], v["vout"], "V")
row("p4 测量表", "脚7 静态直流", P["vbyp"], v["vbyp"], "V", "模型按 15k/15k 分压")
row("p2/p4", "9 V 静态电流", P["iq_mA"], v["iq_mA"], "mA", "模型输入：手册图 9-4 读数")

# 2) 幅频
v = ngspice("ac.cir", ["g20_1k", "g200_1k", "g200_100", "g200_20", "g200_200", "bw20", "bw200", "fhp", "hp1k"])
row("p2 二", "增益 20 档 1 kHz", P["g20_1k"], v["g20_1k"])
row("p2 二/p3 参数", "增益 200 档 1 kHz", P["g200_1k"], v["g200_1k"])
row("p2 二", "增益 200 档 200 Hz", P["g200_200"], v["g200_200"])
row("p2 二", "增益 200 档 100 Hz", P["g200_100"], v["g200_100"])
row("p2 二", "增益 200 档 20 Hz", P["g200_20"], v["g200_20"])
row("p2 三/p3 参数", "增益 20 档上限 −3 dB", P["bw20"], v["bw20"], "Hz", "模型按手册 300 kHz 设 GBW")
row("p2 三/p3 参数", "增益 200 档上限 −3 dB", P["bw200"], v["bw200"], "Hz")
row("p2 三/p3 参数", "220 µF + 18 Ω 下限 −3 dB", P["fhp"], v["fhp"], "Hz")
row("—", "220 µF 在 1 kHz 的传输", None, v["hp1k"])
ac = np.loadtxt(WORK / "ac_vg.txt")        # 列：f, g20, f, g200, f, hp
np.savetxt(OUT / "ac.csv", np.column_stack([ac[:, 0], ac[:, 1], ac[:, 3], ac[:, 5]]), delimiter=",", fmt="%.6g",
           header="f_Hz,g20,g200,hp", comments="")

# 3) 手机满音量
v = ngspice("phone.cir", ["vin_pk", "vout_max", "vout_min", "vsp_max", "pin", "pspk", "plim", "isup_mA", "outb_max", "outb_min"])
row("p3 一/p4 测量表", "脚3 峰值（分压 + 电位器开满）", P["vin_pk"], v["vin_pk"], "V")
row("p4 测量表", "脚5 交流峰值", P["vout_pk"], v["vout_max"] - 4.5, "V")
row("p4 测量表", "喇叭两端峰值", P["vsp_pk"], v["vsp_max"], "V")
row("p3 参数", "电源功率", P["pin"], v["pin"], "W")
row("p3 参数", "喇叭功率", P["pspk"], v["pspk"], "W")
row("p3 参数/p4 实验 C", "10 Ω 电阻功率", P["plim"], v["plim"], "W")
row("p4 测量表", "电源电流平均", P["isup_mA"], v["isup_mA"], "mA")
row("p3 参数/p4 实验 C", "芯片发热（电源 − 喇叭 − 10 Ω）", P["pchip"], v["pin"] - v["pspk"] - v["plim"], "W", "吸收网络 1 kHz 时约 µW 级，忽略")
row("p3 一", "增益 200 削顶上沿", P["outb_max"], v["outb_max"], "V")
row("p3 一", "增益 200 削顶下沿", P["outb_min"], v["outb_min"], "V")
w = np.loadtxt(WORK / "phone_vg.txt")      # 列：t, nd, t, out, t, sp2, t, outb
tt = np.linspace(55e-3, 58e-3, 900)
np.savetxt(OUT / "phone.csv", np.column_stack([tt] + [np.interp(tt, w[:, 0], w[:, c]) for c in (1, 3, 5, 7)]),
           delimiter=",", fmt="%.6g", header="t,vin,out,sp2,outb", comments="")

# 4) 脚7 旁路
v = ngspice("psrr.cir", ["rip_cap_mV", "rip_open_mV"])
row("p3 排错", "脚7 接 10 µF：喇叭嗡声峰值", P["rip_cap_mV"], v["rip_cap_mV"], "mV", "行为模型，只看相对差别")
row("p3 排错", "脚7 悬空：喇叭嗡声峰值", P["rip_open_mV"], v["rip_open_mV"], "mV")

# 5) 增益 200 + 电位器 10 %
v = ngspice("g200pot.cir", ["vw_pk", "omax"])
row("p3 一/p4", "增益 200、电位器 10 %：脚3 峰值", P["vw_pk"], v["vw_pk"], "V")
row("p3 一/p4", "增益 200、电位器 10 %：输出峰值", P["g200pot_pk"], v["omax"] - 4.5, "V")

# 6) 功率扫描
v = ngspice("sweep.cir", [f"pc{k}" for k in range(25)])
S = np.array([[v[f"a{k}"], v[f"pin{k}"], v[f"pl{k}"], v[f"pc{k}"], v[f"vmax{k}"]] for k in range(25)])
np.savetxt(OUT / "sweep.csv", S, delimiter=",", fmt="%.6g", header="a,pin,pl,pc,vmax", comments="")
k = int(np.argmax(S[:, 3]))
row("p2 四/p3 参数", "芯片发热最大值（扫描）", P["pc_max"], S[k, 3], "W")
row("p2 四", "发热最大时输入峰值", P["a_pcmax"], S[k, 0], "V", "扫描步长 10 mV")
kk = int(np.argmin(abs(S[:, 0] - 0.16)))
row("p2 四/p3 参数", "刚削顶前（160 mV）18 Ω 功率", P["pl_max"], S[kk, 2], "W")
row("p1 效率图", "输入 10 mV 时 18 Ω 功率", P["pl_1"], S[0, 2], "W")
row("p1 效率图", "输入 10 mV 时电源功率", P["pin_1"], S[0, 1], "W")
pd_formula = 9 ** 2 / (2 * math.pi ** 2 * 18) + 9 * 4.3e-3
row("—", "公式 VS²/(2π²RL)+VS·IQ（对照）", P["pc_max"], pd_formula, "W", "公式，不是 SPICE")

with open(OUT / "nums.csv", "w") as f:
    f.write("name,value\n")
    for loc, item, page, sp, unit, dev, note in ROWS:
        f.write(f"{item},{sp:.6g}\n")
report("45 集成功放芯片")
bad = [r for r in ROWS if r[5] is not None and abs(r[5]) > 5]
print("超过 5 % 的项：", len(bad))
