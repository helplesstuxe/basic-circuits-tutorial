#!/usr/bin/env python3
"""44 D 类功放：ngspice + TL072（TI 模型）三角波 / 中点参考 + 行为模型比较器（LM393 的理想化）+ 行为模型 DRV8871 H 桥
（R_DS(on) 307 / 258 mΩ、体二极管、3 mA 静态电流，按 TI 数据手册）+ 两只 220 µH（Bourns RLB0913-221K，DCR 0.453 Ω）+ 0.68 µF。
从仓库根运行：python spice/44/run.py（约 3 分钟）。
默认所有仿真输出（*_vg.txt 和抽稀的 CSV）都写到临时目录，不覆盖仓库里的文件；
维护者要更新 code/figs/44_figs.py 画图用的小 CSV 时才加 --update：python spice/44/run.py --update"""
# ---- 通用小工具：调用 ngspice -b，解析 .control 里 echo 出来的 "RES 名字 数值" ----
import subprocess, re, sys, pathlib, math, shutil, tempfile
HERE = pathlib.Path(__file__).resolve().parent
# 在临时目录里跑 ngspice（网表里的 ../models 用符号链接指回仓库），原始波形 txt 写在那里
WORK = pathlib.Path(tempfile.mkdtemp(prefix="spice44_")) / "44"
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
# 页面上写的数值（跑完照 SPICE 结果写进页面后填回这里）
P = _P({
    "f_formula": 53.19, "fsw": 38.56, "vtri": 2.732, "tav": 6.00, "sqmax": 10.476, "sqmin": 1.523, "gain": 4.393,
    "iidle": 6.146, "vdavg": -11.4, "vdrms": 0.6148, "pripple": 21, "in1avg": 2.50,
    "iripple_f": 0.1768, "iripple": 0.1837,
    "f0": 9.201, "q18": 0.7076, "h0": 0.9244, "f3": 8.78, "h20k": 0.2063, "hfs": 0.05685, "hnl": 16.68, "fnl": 9.12,
    "vpk_0p25": 0.6734, "pa_0p25": 0.0126, "pin_0p25": 0.08774, "eta_0p25": 14.4,
    "vpk_0p5": 1.345, "pa_0p5": 0.05024, "pin_0p5": 0.1268, "eta_0p5": 39.6,
    "vpk_1": 2.686, "pa_1": 0.2005, "pin_1": 0.2857, "eta_1": 70.2,
    "vpk_1p5": 4.03, "pa_1p5": 0.4511, "pin_1p5": 0.5528, "eta_1p5": 81.6, "il_1p5": 0.3843,
    "vpk_2": 5.377, "pa_2": 0.8031, "pin_2": 0.9292, "eta_2": 86.4,
    "vpk_2p5": 6.726, "pa_2p5": 1.257, "pin_2p5": 1.415, "eta_2p5": 88.8, "il_2p5": 0.4912,
    "vpk_fft": 2.687, "thd": 0.2188,
    "flt_vd": 2.094, "flt_p8": 0.116, "flt5_vd": -5.503, "flt5_p8": 0.75, "flt5_p10": 0.9375,
    "flt_i": 34.5, "flt5_i": 155, "hy_vd": -0.145,
    "nolc_p10": 4.134, "nolc_p8": 3.308, "nolc_i": 0.6429,
    "nl0_vd": 5.07, "nl9_vd": 9.865, "nl9_il": 0.5192,
    "eng_p": 414, "eng_i": 46.2,
    "ard0_vd": 0.9263, "ard0_i": 9.135, "ard40_vd": 2.614,
})

VS, RLOAD = 12.0, 18.0          # 单 12 V；负载 10 Ω + 8 Ω
L_LEG, C_F = 220e-6, 0.68e-6    # 每腿 220 µH，跨接 0.68 µF

# ---------- 1. 静音（无信号）：三角波、开关频率、电源电流、负载残留纹波 ----------
v = ngspice("idle.cir", need=["idle_tA", "idle_tB", "idle_iavg", "idle_vdrms"])
fsw = 100 / (v["idle_tB"] - v["idle_tA"])            # 第 40 到第 140 个上升沿 = 100 个周期
vtri = (v["idle_tmax"] - v["idle_tmin"]) / 2
f_formula = 22e3 / (4 * 10e3 * 4.7e3 * 2.2e-9)
row("p2 §一", "三角波频率公式 R2/(4·R1·R·C)", P["f_formula"], f_formula / 1e3, "kHz", "公式（假设方波 ±常数、运放理想）")
row("p2 §一 / p3", "三角波实际频率 f_sw（SPICE，TL072 模型）", P["fsw"], fsw / 1e3, "kHz", "比公式低：TL072 方波只摆到 1.5～10.5 V 且退饱和慢")
row("p2 §一", "三角波峰值 V_tri,p", P["vtri"], vtri, "V")
row("p2 §一", "三角波中心（交流耦合到 V_MID）", P["tav"], v["idle_tav"], "V")
row("p2 §一", "TL072 方波高电平", P["sqmax"], v["idle_sqmax"], "V")
row("p2 §一", "TL072 方波低电平", P["sqmin"], v["idle_sqmin"], "V")
row("p2 §二", "前级到差分输出的增益 V_S / V_tri,p", P["gain"], VS / vtri, "倍")
row("p4 测量表", "静音时 VM 线电流（DRV8871 + LC + 负载）", P["iidle"], v["idle_iavg"] * 1e3, "mA")
row("p4 测量表", "静音时负载两端直流（10 Ω + 8 Ω）", P["vdavg"], v["idle_vdavg"] * 1e3, "mV", "页面要求 < 50 mV")
row("p2 §三", "静音时负载上载波残余 RMS", P["vdrms"], v["idle_vdrms"], "V")
row("p2 §三", "静音时负载上载波残余功率", P["pripple"], v["idle_vdrms"] ** 2 / RLOAD * 1e3, "mW")
row("p4 测量表", "OUT1 对地直流平均", P["o1avg"], v["idle_o1avg"], "V")
row("p4 测量表", "IN1 对地直流平均（5 V 方波 50%）", P["in1avg"], v["idle_in1avg"], "V")
ripple_formula = VS / (8 * L_LEG * fsw)
row("p2 §三", "电感纹波电流公式 V_S/(8·L·f_sw)", P["iripple_f"], ripple_formula, "A")
row("p2 §三", "电感纹波电流峰值（SPICE）", P["iripple"], max(v["idle_ilmax"], -v["idle_ilmin"]), "A")

# ---------- 2. LC 频率响应 ----------
a = ngspice("ac_lc.cir", need=["ac18_f3", "acnl_hpk"])
f0 = 1 / (2 * math.pi * math.sqrt(2 * L_LEG * C_F))
q18 = RLOAD * math.sqrt(C_F / (2 * L_LEG))
row("p2 §三", "LC 谐振 f0 = 1/(2π√(2L·C))", P["f0"], f0 / 1e3, "kHz", "两只电感串联 440 µH")
row("p2 §三", "Q 值 = R√(C/2L)，18 Ω", P["q18"], q18, "")
row("p2 §三", "LC 直流增益（含 R_DS(on) 0.565 Ω、DCR）", P["h0"], a["ac18_h1k"], "")
row("p2 §三 / p3", "−3 dB 频率（18 Ω）", P["f3"], a["ac18_f3"] / 1e3, "kHz")
row("p3", "20 kHz 处增益（18 Ω）", P["h20k"], a["ac18_h20k"], "")
row("p2 §三", "载波 f_sw 处增益（18 Ω）", P["hfs"], a["ac18_hfs"], "")
acnl = np.loadtxt(WORK / "acnl_vg.txt")
ac18 = np.loadtxt(WORK / "ac18_vg.txt")
fpk = acnl[np.argmax(acnl[:, -1]), 0]
row("p3 §二", "空载谐振峰增益", P["hnl"], a["acnl_hpk"], "倍")
row("p3 §二", "空载谐振峰频率", P["fnl"], fpk / 1e3, "kHz")
np.savetxt(OUT / "ac.csv", np.column_stack([ac18[:, 0], ac18[:, -1], acnl[:, -1]]), delimiter=",", fmt="%.6g", header="f_Hz,h_18ohm,h_noload", comments="")

# ---------- 3. 加信号：400 Hz 幅度扫描，效率 ----------
s = ngspice("sig.cir", need=[f"sig_{k}_a1" for k in range(8)])
T = 2.5e-3                                              # 3～5.5 ms，正好 1 个 400 Hz 周期
eff = []
for k in range(8):
    amp = s[f"sig_{k}_amp"]
    vpk = 2 / T * math.hypot(s[f"sig_{k}_a1"], s[f"sig_{k}_b1"])     # 负载两端 400 Hz 基波峰值
    pa = vpk ** 2 / (2 * RLOAD)                          # 音频（基波）功率，10 Ω + 8 Ω 合计
    ptot = s[f"sig_{k}_vdrms"] ** 2 / RLOAD               # 负载总功率（含载波残余）
    pin = VS * s[f"sig_{k}_iavg"]
    ilpk = max(s[f"sig_{k}_ilmax"], -s[f"sig_{k}_ilmin"])
    eff.append((amp, vpk, pa, ptot, pin, pa / pin * 100, ilpk))
for amp, vpk, pa, ptot, pin, et, ilpk in eff:
    tag = f"{amp:g}".replace(".", "p")
    row("p2 §四 效率图", f"信号源 {amp:g} V：负载 400 Hz 峰值", P[f"vpk_{tag}"], vpk, "V")
    row("p2 §四 效率图", f"信号源 {amp:g} V：音频功率（18 Ω）", P[f"pa_{tag}"], pa, "W")
    row("p2 §四 效率图", f"信号源 {amp:g} V：电源功率 12 V × I", P[f"pin_{tag}"], pin, "W")
    row("p2 §四 效率图", f"信号源 {amp:g} V：效率 η", P[f"eta_{tag}"], et, "%")
    row("p3 电感", f"信号源 {amp:g} V：电感电流峰值", P[f"il_{tag}"], ilpk, "A", "RLB0913-221K I_sat 0.64 A")
with open(OUT / "eff.csv", "w") as f:
    f.write("amp_V,vpk_V,p_audio_W,p_load_total_W,p_in_W,eta_pct,il_pk_A\n")
    for r in eff:
        f.write(",".join(f"{x:.5g}" for x in r) + "\n")
# 1.0 V 实验点的波形与谐波
w = np.loadtxt(WORK / "sig_vg.txt")      # 列：t, sig, s, t(三角波), in1, o1, vd, iL
t0, t1 = 3e-3, 5.5e-3
n = 2 ** 16
tt = np.linspace(t0, t1, n, endpoint=False)
vd = np.interp(tt, w[:, 0], w[:, 6])
X = np.abs(np.fft.rfft(vd)) / n * 2
h = np.array([X[k] for k in range(1, 11)])             # 1 个周期 → 第 k 根谱线就是 k 次谐波
thd = 100 * np.sqrt(np.sum(h[1:] ** 2)) / h[0]
row("p2 §四", "1.0 V 实验点：负载 400 Hz 基波峰值（FFT）", P["vpk_fft"], h[0], "V")
row("p2 §四 / p3", "1.0 V 实验点：THD（2～10 次）", P["thd"], thd, "%")
with open(OUT / "harm.csv", "w") as f:
    f.write("k,rel_pct\n")
    for k in range(2, 11):
        f.write(f"{k},{100*h[k-1]/h[0]:.4g}\n")
# 抽稀：整个周期（音频）与一个载波窗口（看 PWM）
ta = np.linspace(t0, t1, 1500)
np.savetxt(OUT / "w_sig.csv", np.column_stack([ta] + [np.interp(ta, w[:, 0], w[:, c]) for c in (1, 2, 6, 7)]),
           delimiter=",", fmt="%.6g", header="t,sig,s,vd,iL", comments="")
tz0 = 3.0e-3 + 0.25 * T - 1.5 / fsw                     # 信号接近正峰附近的 3 个载波周期
tz = np.linspace(tz0, tz0 + 3 / fsw, 1200)
np.savetxt(OUT / "w_pwm.csv", np.column_stack([tz] + [np.interp(tz, w[:, 0], w[:, c]) for c in (2, 3, 4, 5)]),
           delimiter=",", fmt="%.6g", header="t,s,tri,in1,o1", comments="")
wi = np.loadtxt(WORK / "idle_vg.txt")    # 列：t, tri, sq, t, in1, in2, o1, o2, vd, iL
ti = np.linspace(3.0e-3, 3.0e-3 + 3 / fsw, 1200)
np.savetxt(OUT / "w_idle.csv", np.column_stack([ti] + [np.interp(ti, wi[:, 0], wi[:, c]) for c in (1, 2, 3, 4, 5, 6, 7, 8, 9)]),
           delimiter=",", fmt="%.6g", header="t,tri,sq,tt,in1,in2,o1,o2,vd,iL", comments="")

# ---------- 4. 故障与对照 ----------
fl = ngspice("fault_in2gnd.cir", need=["flt_vdavg", "flt5_vdavg"])
row("p3 排错表", "IN2 接地（00 = 滑行）：负载直流", P["flt_vd"], fl["flt_vdavg"], "V")
row("p3 排错表", "IN2 接地：8 Ω 喇叭上功率（含载波）", P["flt_p8"], fl["flt_p8"], "W")
row("p3 排错表", "IN2 接 5 V（11 = 刹车）：负载直流", P["flt5_vd"], fl["flt5_vdavg"], "V")
row("p3 排错表", "IN2 接 5 V：8 Ω 喇叭上直流功率", P["flt5_p8"], fl["flt5_p8"], "W")
row("p3 排错表", "IN2 接 5 V：10 Ω 电阻上直流功率", P["flt5_p10"], fl["flt5_p10"], "W")
row("p3 / p4 安全", "IN2 接地：静音 VM 平均电流", P["flt_i"], fl["flt_iavg"] * 1e3, "mA", "页面判据：静音超过 20 mA 就断电")
row("p3 / p4 安全", "IN2 接 5 V：静音 VM 平均电流", P["flt5_i"], fl["flt5_iavg"] * 1e3, "mA", "小于 0.2 A，限流不动作")
hy = ngspice("hyst.cir", need=["hy_vdavg"])
row("p3 排错表", "反例：IN1 接 1 MΩ 到 s，负载直流（30～40 ms 平均）", P["hy_vd"], hy["hy_vdavg"], "V", "超过 50 mV 门限，故页面不用此法")
nl = ngspice("nolc.cir", need=["nolc_p10", "nolc_iavg"])
row("p3 §二", "不加 LC：静音时 10 Ω 上功率", P["nolc_p10"], nl["nolc_p10"], "W")
row("p3 §二", "不加 LC：静音时 8 Ω 上功率", P["nolc_p8"], nl["nolc_p8"], "W")
row("p3 §二", "不加 LC：静音电源电流", P["nolc_i"], nl["nolc_iavg"], "A")
no = ngspice("noload.cir", need=["nl0_vdmax", "nl9_ilmax"])
row("p3 §二", "空载上电：电容两端最高电压", P["nl0_vd"], no["nl0_vdmax"], "V")
row("p3 §二", "空载 + 8.8 kHz 0.3 V 信号：电容两端峰值", P["nl9_vd"], no["nl9_vdmax"], "V")
row("p3 §二", "空载 + 8.8 kHz 0.3 V 信号：电感电流峰值", P["nl9_il"], max(no["nl9_ilmax"], -no["nl9_ilmin"]), "A")
en = ngspice("idle_eng.cir", need=["eng_vdrms"])
row("p3 §三", "LC 改 100 µH + 0.33 µF：静音载波残余 RMS", P["eng_vd"], en["eng_vdrms"], "V")
row("p3 §三", "LC 改 100 µH + 0.33 µF：静音载波残余功率", P["eng_p"], en["eng_vdrms"] ** 2 / RLOAD * 1e3, "mW")
row("p3 §三", "LC 改 100 µH + 0.33 µF：电感电流峰值", P["eng_il"], max(en["eng_ilmax"], -en["eng_ilmin"]), "A")
row("p3 §三", "LC 改 100 µH + 0.33 µF：静音电源电流", P["eng_i"], en["eng_iavg"] * 1e3, "mA")
ar = ngspice("arduino.cir", need=["ard40_vdrms", "ard0_vdrms"])
row("p4 Arduino", "Arduino 31.37 kHz 静音：负载载波残余 RMS", P["ard0_vd"], ar["ard0_vdrms"], "V")
row("p4 Arduino", "Arduino 31.37 kHz 静音：VM 电流", P["ard0_i"], ar["ard0_iavg"] * 1e3, "mA")
row("p4 Arduino", "Arduino 幅度 40：负载 RMS（含残余）", P["ard40_vd"], ar["ard40_vdrms"], "V")
with open(OUT / "compare.csv", "w") as f:       # 静音时：载波残余功率 mW、电源电流 mA
    f.write("case,p_ripple_mW,i_supply_mA\n")
    f.write(f"none,{(nl['nolc_p10']+nl['nolc_p8'])*1e3:.5g},{nl['nolc_iavg']*1e3:.5g}\n")
    f.write(f"eng100u,{en['eng_vdrms']**2/RLOAD*1e3:.5g},{en['eng_iavg']*1e3:.5g}\n")
    f.write(f"ours220u,{v['idle_vdrms']**2/RLOAD*1e3:.5g},{v['idle_iavg']*1e3:.5g}\n")
    f.write(f"arduino,{ar['ard0_vdrms']**2/RLOAD*1e3:.5g},{ar['ard0_iavg']*1e3:.5g}\n")
with open(OUT / "nums.csv", "w") as f:          # 画图脚本要用的单个数
    f.write("name,value\n")
    for k, val in (("fsw", fsw), ("vtri", vtri), ("f3", a["ac18_f3"]), ("fnl", fpk), ("hnl", a["acnl_hpk"]),
                   ("iidle", v["idle_iavg"]), ("vdavg", v["idle_vdavg"]), ("o1avg", v["idle_o1avg"]), ("in1avg", v["idle_in1avg"]),
                   ("flt_vd", fl["flt_vdavg"]), ("flt5_vd", fl["flt5_vdavg"]), ("thd", thd), ("hfs", a["ac18_hfs"])):
        f.write(f"{k},{val:.6g}\n")

report("44 D 类功放")
print(f"小 CSV 写到：{OUT}")
