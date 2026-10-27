#!/usr/bin/env python3
"""43 推挽功放：ngspice + TL072（TI）/ BD139、BD140（通用模型，见 spice/models/BD139_BD140_generic.lib）/ 1N4148（Nexperia）复核页面数值。
从仓库根运行：python spice/43/run.py（约 1 分钟）。
默认所有仿真输出（*_vg.txt 和抽稀的 CSV）都写到临时目录，不覆盖仓库里的文件；
维护者要更新 code/figs/43_figs.py 画图用的小 CSV 时才加 --update：python spice/43/run.py --update"""
# ---- 通用小工具：调用 ngspice -b，解析 .control 里 echo 出来的 "RES 名字 数值" ----
import subprocess, re, sys, pathlib, math, shutil, tempfile
HERE = pathlib.Path(__file__).resolve().parent
# 在临时目录里跑 ngspice（网表里的 ../models 用符号链接指回仓库），原始波形 txt 写在那里
WORK = pathlib.Path(tempfile.mkdtemp(prefix="spice43_")) / "43"
WORK.mkdir()
(WORK.parent / "models").symlink_to(HERE.parent / "models")
for f in list(HERE.glob("*.cir")) + list(HERE.glob("*.inc")) + list(HERE.glob(".spiceinit")):
    shutil.copy(f, WORK)
# 低 hFE 版本（按数据手册最坏 hFE ≈ 25 @0.5 A）：只把 BF 按比例缩小，其余参数不变；生成在临时目录，不改共享模型文件
#   BD139：BF 244.9 × 25 / 140.5（典型模型 @0.5 A 的 hFE）≈ 43.6；BD140：201.4 × 25 / 123.0 ≈ 40.9
_lib = (HERE.parent / "models" / "BD139_BD140_generic.lib").read_text(encoding="utf-8")
assert "BF=244.9" in _lib and "BF=201.4" in _lib
(WORK / "BD139_BD140_lowbeta.lib").write_text(_lib.replace("BF=244.9", "BF=43.6").replace("BF=201.4", "BF=40.9"), encoding="utf-8")
_com = (WORK / "common.inc").read_text(encoding="utf-8")
assert "../models/BD139_BD140_generic.lib" in _com
(WORK / "common_lowb.inc").write_text(_com.replace("../models/BD139_BD140_generic.lib", "BD139_BD140_lowbeta.lib"), encoding="utf-8")
(WORK / "chk_lowb.cir").write_text((WORK / "chk_models.cir").read_text(encoding="utf-8").replace("../models/BD139_BD140_generic.lib", "BD139_BD140_lowbeta.lib").replace("RES chk_", "RES lowchk_"), encoding="utf-8")
OUT = HERE if "--update" in sys.argv else WORK          # 小 CSV 的去处
ROWS = []

def ngspice(cir, need=()):
    """在本目录下以 batch 模式运行 cir，返回 {名字: 数值}；缺值或出错就报错退出。"""
    r = subprocess.run(["ngspice", "-b", cir], cwd=WORK, capture_output=True, text=True, timeout=900)
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

import numpy as np

# 页面上写的数值（第一次跑时为空，跑完照 SPICE 和手算结果写进页面后再填回这里）
class _P(dict):
    def __missing__(self, k):
        return None
P = _P({'iq': 33.0, 'vbias': 1.56, 'iccs': 23.7, 'pq3': 0.11, 'ps0': 0.396, 'pd0': 0.198, 'iq_re1': 75.8, 'mis33_20': 35.3, 'mis33_80': 42.3, 'mis33_160': 52.0, 'mis1_20': 82.1, 'mis1_80': 101, 'mis1_160': 128, 'inc33': 28.4, 'inc1': 33.5, 'lowb_ccs_0': 2.01, 'lowb_ccs_1': 2.89, 'lowb_ccs_0_io': 8.2, 'lowb_ccs_1_io': 12.8, 'lowb_rb470_0': 1.64, 'lowb_rb470_1': 1.64, 'lowb_rb470_0_io': 20.6, 'lowb_rb470_1_io': 20.6, 'typ_rb470_0': 2.01, 'typ_rb470_1': 2.85, 'typ_rb470_0_io': 14.1, 'typ_rb470_1_io': 20.5, 'r1': 0.46, 'r2': 0.31, 'r3': 0.02, 'r4': 0.91, 'r5': 0.63, 'r6': 21.0, 'r7': 19.2, 'r8': 1.84, 'r9': 1.44, 'r10': 0.071, 'r11': 0.0086, 'r12': 2.0, 'r13': 9.62, 'r14': 26.5, 'r15': 0.25, 'r16': 0.955, 'r17': 0.99, 'r18': 82.5, 'r19': 1.42, 'r20': 25.5, 'r21': 1.9, 'r22': 3.0, 'r23': 38.9, 'r24': 39.3, 'r25': 0.88, 'r26': 0.56, 'r27': 3.11, 'r28': 3.19, 'r29': 0.7, 'r30': 19.9, 'r31': 42.3, 'r32': 3.0, 'c_vd56': 1.30, 'c_veb3': 0.65, 'c_vrx3': 0.64, 'b2_vre1': 274, 'b2_icmax': 0.25, 'c3_jump': 1.02, 'c3_o100': 0.30, 'c3_m100': 0.84, 'ls_B_open_vp': 0.30, 'ls_B_open_thd': 45, 'ls_AB_open_vp': 0.89, 'ls_AB_open_thd': 0.085, 'ls_B_loop_vp': 1.0, 'ls_B_loop_thd': 0.054, 'ls_AB_loop_vp': 1.0, 'ls_AB_loop_thd': 0.0057})

# ===================== 页面上的手算 / 脚本值（与 code/figs/43_figs.py 同一组公式） =====================
VS, VCC, RL = 12.0, 6.0, 8.0                   # 单 12 V；等效 V_CC = 6 V；8 Ω 功率电阻
GAIN = 1 + 20e3 / 10e3                          # 同相放大 1 + RF/RG = 3

def ideal_b(vp):
    """理想乙类（单电源 + 耦合电容，等效 V_CC = 6 V）：返回 P_L、P_S、η。"""
    pl = vp ** 2 / (2 * RL)
    ps = VS * (vp / RL) / math.pi              # Q1 电流是半波，平均 I_p/π；全部来自 +12 V
    return pl, ps, pl / ps

def thd(name, f0, t0, t1):
    """读 *_vg.txt（列：t, sig, m, out, ld, i_Vam），对 [t0, t1) 内整数个周期做 FFT，返回 (基波峰值, THD%, 2～10 次谐波相对值%)。"""
    a = np.loadtxt(WORK / name)
    t, ld = a[:, 0], a[:, 4]
    sel = (t >= t0 - 1e-12) & (t < t1 - 1e-12)
    x = ld[sel]
    n_per = round((t1 - t0) * f0)
    X = np.abs(np.fft.rfft(x)) / len(x) * 2
    h = np.array([X[n_per * k] for k in range(1, 11)])
    return h[0], 100 * np.sqrt(np.sum(h[1:] ** 2)) / h[0], 100 * h[1:] / h[0]

def wave(name, t0, t1, n, out, cols, header):
    """把 *_vg.txt 抽稀成小 CSV 给画图脚本用（原始文件大，被 .gitignore 忽略）。"""
    a = np.loadtxt(WORK / name)
    tt = np.linspace(t0, t1, n)
    vals = [np.interp(tt, a[:, 0], a[:, c]) for c in cols]
    np.savetxt(OUT / out, np.column_stack([tt] + vals), delimiter=",", fmt="%.6g", header=header, comments="")

# ---------- 模型核对（spice/models/BD139_BD140_generic.lib 与 ST 数据手册） ----------
m = ngspice("chk_models.cir", need=[f"chk_{q}_{i}_{k}" for q in ("BD139", "BD140") for i in ("0p01", "0p15", "0p5") for k in ("vbe", "hfe")])
for q in ("BD139", "BD140"):
    row("[模型核对]", f"{q} hFE @150 mA（手册 40～250）", None, m[f"chk_{q}_0p15_hfe"], "", "落在范围内" if 40 <= m[f"chk_{q}_0p15_hfe"] <= 250 else "超出范围！")
    row("[模型核对]", f"{q} hFE @0.5 A（手册 ≥ 25）", None, m[f"chk_{q}_0p5_hfe"], "", "满足" if m[f"chk_{q}_0p5_hfe"] >= 25 else "不满足！")
    row("[模型核对]", f"{q} V_BE @0.5 A（手册 ≤ 1 V）", None, m[f"chk_{q}_0p5_vbe"], "V", "满足" if m[f"chk_{q}_0p5_vbe"] <= 1 else "不满足！")
    row("[模型核对]", f"{q} V_BE @10 mA", 0.65, m[f"chk_{q}_0p01_vbe"], "V", "页面按「约 0.6～0.7 V」")
    assert 40 <= m[f"chk_{q}_0p15_hfe"] <= 250 and m[f"chk_{q}_0p5_hfe"] >= 25 and m[f"chk_{q}_0p5_vbe"] <= 1

# ---------- 静态电流 I_q ----------
q = ngspice("iq_op.cir", need=["iq_RE3p3_dv0_Iq", "iq_RE1_dv0_Iq", "iq_ccs_top", "iq_ccs_bot"])
row("p2 §三 / p4 测量表", "甲乙类静态电流 I_q（R_E 3.3 Ω）", P["iq"], q["iq_RE3p3_dv0_Iq"] * 1e3, "mA")
row("p2 §三", "两只 1N4148 垫出的偏置电压", P["vbias"], q["iq_RE3p3_dv0_vbias"], "V")
row("p2 §一", "上恒流源电流（流进 b1）", P["iccs"], q["iq_ccs_top"] * 1e3, "mA", "要求 ≥ 22 mA")
row("p2 §一", "下恒流源电流（从 b2 抽走）", P["iccs"], q["iq_ccs_bot"] * 1e3, "mA", "要求 ≥ 22 mA")
row("p2 §一", "恒流源 Q3 静态管耗", P["pq3"], q["iq_q3_pd"], "W", "不用散热片（手册无散热片 1.25 W）")
row("p2 §三", "静态时功放管电源功率 12 V × I_q", P["ps0"], 12 * q["iq_RE3p3_dv0_Iq"], "W")
row("p2 §三", "静态时每只功放管管耗 6 V × I_q", P["pd0"], 6 * q["iq_RE3p3_dv0_Iq"], "W")
row("p3 §二", "R_E 1 Ω 时 I_q", P["iq_re1"], q["iq_RE1_dv0_Iq"] * 1e3, "mA")
for dv in (20, 80, 160):
    row("p3 失配图", f"R_E 3.3 Ω，失配 {dv} mV 时 I_q", P[f"mis33_{dv}"], q[f"iq_RE3p3_dv{dv}_Iq"] * 1e3, "mA")
    row("p3 失配图", f"R_E 1 Ω，失配 {dv} mV 时 I_q", P[f"mis1_{dv}"], q[f"iq_RE1_dv{dv}_Iq"] * 1e3, "mA")
row("p3 §二", "R_E 3.3 Ω：失配 80 mV 时 I_q 增幅", P["inc33"], (q["iq_RE3p3_dv80_Iq"] / q["iq_RE3p3_dv0_Iq"] - 1) * 100, "%")
row("p3 §二", "R_E 1 Ω：失配 80 mV 时 I_q 增幅", P["inc1"], (q["iq_RE1_dv80_Iq"] / q["iq_RE1_dv0_Iq"] - 1) * 100, "%")
with open(OUT / "iq.csv", "w") as f:      # 给失配图用
    f.write("dv_mV,iq_RE3p3_mA,iq_RE1_mA\n")
    for dv in (0, 20, 80, 160):
        f.write(f"{dv},{q[f'iq_RE3p3_dv{dv}_Iq']*1e3:.4g},{q[f'iq_RE1_dv{dv}_Iq']*1e3:.4g}\n")

# ---------- hFE 按最坏 25：恒流源偏置 vs 旧做法 R_B 470 Ω ----------
lm = ngspice("chk_lowb.cir", need=["lowchk_BD139_0p5_hfe", "lowchk_BD140_0p5_hfe"])
for qn in ("BD139", "BD140"):
    row("[低 hFE 模型]", f"{qn} hFE @0.5 A（目标 ≈ 25）", None, lm[f"lowchk_{qn}_0p5_hfe"], "", "")
    row("[低 hFE 模型]", f"{qn} hFE @150 mA", None, lm[f"lowchk_{qn}_0p15_hfe"], "", "")
lb = {}
for nm in ("lowb_ccs", "lowb_rb470", "typ_rb470"):
    lb.update(ngspice(f"{nm}.cir", need=[f"{nm}_1_vmax"]))
vpk = lambda nm, k: (lb[f"{nm}_{k}_vmax"] - lb[f"{nm}_{k}_vmin"]) / 2
iok = lambda nm, k: max(lb[f"{nm}_{k}_imo_max"], -lb[f"{nm}_{k}_imo_min"]) * 1e3
for nm, lab in (("lowb_ccs", "hFE≈25，恒流源"), ("lowb_rb470", "hFE≈25，R_B 470 Ω"), ("typ_rb470", "典型 hFE，R_B 470 Ω")):
    for k, tgt in ((0, 2), (1, 3)):
        row("p3 偏置对比图", f"{lab}：目标 {tgt} V 时实际 V_p", P[f"{nm}_{k}"], vpk(nm, k), "V")
        row("p3 偏置对比图", f"{lab}：目标 {tgt} V 时运放电流峰值", P[f"{nm}_{k}_io"], iok(nm, k), "mA", "TL072 短路电流 26 mA")
with open(OUT / "starve.csv", "w") as f:
    f.write("case_id,vp_2,vp_3,io_2,io_3\n")          # case_id：0 典型 hFE + R_B 470 Ω，1 hFE≈25 + R_B 470 Ω，2 hFE≈25 + 恒流源
    for i, nm in enumerate(("typ_rb470", "lowb_rb470", "lowb_ccs")):
        f.write(f"{i},{vpk(nm,0):.4g},{vpk(nm,1):.4g},{iok(nm,0):.4g},{iok(nm,1):.4g}\n")

# ---------- 直流转移（没有示波器的做法）：死区宽度 ----------
for b in ("B", "AB"):
    dc = ngspice(f"dc_{b}_open.cir", need=[f"dc_{b}_mlo", f"dc_{b}_mhi"])
    if b == "B":
        row("p4 没有示波器 / 图43-p2-4", "乙类：out 离开 6 V ±10 mV 前，m 下限 − 6 V", -0.46, dc["dc_B_mlo"] - 6, "V")
        row("p4 没有示波器 / 图43-p2-4", "乙类：同上，m 上限 − 6 V", P["r1"], dc["dc_B_mhi"] - 6, "V")
        row("p4 没有示波器", "乙类：对应的输入 inp 宽度", P["r2"], dc["dc_B_vxhi"] - dc["dc_B_vxlo"], "V", "= m 宽度 ÷ 3")
    else:
        row("p4 没有示波器 / 图43-p2-4", "甲乙类：m 的「死区」总宽", P["r3"], dc["dc_AB_mhi"] - dc["dc_AB_mlo"], "V", "已基本没有死区")
    wave(f"dc_{b}_open_vg.txt", 5.0, 7.0, 801, f"dc_{b}.csv", [1, 3, 5], "vx_sweep,vx,v_m,v_out")

# ---------- 瞬态：四种接法，1 kHz ----------
res = {}
for name in ("B_open", "B_loop", "AB_open", "AB_loop"):
    t = ngspice(f"tran_{name}.cir", need=[f"{name}_0_vrms"])
    res[name] = t
    f1, th, hs = thd(f"{name}_vg.txt", 1e3, 20e-3, 30e-3)
    res[name + "_thd"] = (f1, th, hs)
    wave(f"{name}_vg.txt", 27e-3, 29e-3, 801, f"w_{name}.csv", [1, 2, 3, 4, 5], "t_s,v_sig,v_m,v_out,v_ld,i_q1")
    np.savetxt(OUT / f"h_{name}.csv", hs[None, :], delimiter=",", fmt="%.6g", header=",".join(f"h{k}" for k in range(2, 11)), comments="")
    # 死区：|v_ld| < 20 mV 时 m 偏离 6 V 的范围
    a = np.loadtxt(WORK / f"{name}_vg.txt")
    sel = (a[:, 0] >= 20e-3) & (np.abs(a[:, 4]) < 0.02)
    res[name + "_dz"] = (a[sel, 2].min() - 6, a[sel, 2].max() - 6)

rB, rBL, rAB, rABL = res["B_open"], res["B_loop"], res["AB_open"], res["AB_loop"]
row("p1 图43-p1-3", "乙类开环：负载电压峰值（理想 2 V）", P["r4"], rB["B_open_0_vmax"], "V")
row("p1 图43-p1-3", "乙类开环：死区内 m 下限 − 6 V", -0.62, res["B_open_dz"][0], "V", "|v_L|<20 mV 判据")
row("p1 图43-p1-3", "乙类开环：死区内 m 上限 − 6 V", P["r5"], res["B_open_dz"][1], "V")
row("p3 图43-p3-5", "乙类开环 THD", P["r6"], res["B_open_thd"][1], "%")
row("p3 图43-p3-5", "乙类开环 3 次谐波", P["r7"], res["B_open_thd"][2][1], "%")
row("p3 图43-p3-5", "甲乙类开环 THD", P["r8"], res["AB_open_thd"][1], "%")
row("p2 §三", "甲乙类开环：负载峰值（R_E 分压后理想 2×8/11.3 = 1.42 V）", P["r9"], rAB["AB_open_0_vmax"], "V")
row("p3 图43-p3-5", "乙类环内 THD", P["r10"], res["B_loop_thd"][1], "%")
row("p3 图43-p3-5", "甲乙类环内 THD", P["r11"], res["AB_loop_thd"][1], "%")
row("p2 §四", "乙类环内：负载峰值", P["r12"], rBL["B_loop_0_vmax"], "V")
row("p2 §四 / 图43-p2-5", "乙类环内：运放输出 m 最高", P["r13"], rBL["B_loop_0_mmax"], "V", "2 V + 0.7 V + R_E 压降")
row("p2 §四", "乙类环内：1 kHz 效率 P_L/P_S", P["r14"], (rBL["B_loop_0_vrms"] ** 2 / RL) / (VS * rBL["B_loop_0_iavg"]) * 100, "%")
pl, ps, eta = ideal_b(2.0)
row("p2 §二", "理想乙类 V_p=2 V：P_L", P["r15"], pl, "W", "公式本身")
row("p2 §二", "理想乙类 V_p=2 V：P_S", P["r16"], ps, "W", "公式本身")
row("p2 §二 vs SPICE", "甲乙类环内 V_p=2 V：P_S", P["r17"], VS * rABL["AB_loop_7_iavg"], "W", "多出来的是 I_q")
row("p4 测量表", "甲乙类环内 V_p=2 V：电流表读数", P["r18"], rABL["AB_loop_7_iavg"] * 1e3, "mA")
row("p4 测量表", "甲乙类环内 V_p=2 V：负载 V_rms", P["r19"], rABL["AB_loop_7_vrms"], "V")
row("p4 测量表", "甲乙类环内 V_p=2 V：效率", P["r20"], (rABL["AB_loop_7_vrms"] ** 2 / RL) / (VS * rABL["AB_loop_7_iavg"]) * 100, "%")
row("p2 §五", "V_p=2 V 时运放输出电流峰值（TL072 短路电流 26 mA）", P["r21"], max(rABL["AB_loop_7_imo_max"], -rABL["AB_loop_7_imo_min"]) * 1e3, "mA")

# 效率曲线（图 43-p1-4）：甲乙类环内扫幅度
pts = []
for k in range(14):
    vp = (rABL[f"AB_loop_{k}_vmax"] - rABL[f"AB_loop_{k}_vmin"]) / 2
    plk = rABL[f"AB_loop_{k}_vrms"] ** 2 / RL
    psk = VS * rABL[f"AB_loop_{k}_iavg"]
    pts.append((rABL[f"AB_loop_{k}_amp"], vp, plk, psk, plk / psk, max(rABL[f"AB_loop_{k}_imo_max"], -rABL[f"AB_loop_{k}_imo_min"])))
np.savetxt(OUT / "eff.csv", np.array(pts), delimiter=",", fmt="%.6g", header="vin_pk,vp,pl,ps,eta,iop_max", comments="")
vp3 = [p for p in pts if abs(p[0] - 1.0) < 1e-9][0]
row("p1 图43-p1-4 / p2 §二", "削顶前最大 V_p（输入 1.0 V 峰值）", P["r22"], vp3[1], "V")
row("p1 图43-p1-4 / p2 §二", "V_p≈3 V 时效率", P["r23"], vp3[4] * 100, "%")
row("p2 §二", "理想乙类 V_p=3 V 效率 π·3/24", P["r24"], vp3[4] * 100, "%", "SPICE 含 I_q 和管压降")
row("p2 §二", "V_p≈3 V 时两管合计管耗 P_S − P_L", P["r25"], vp3[3] - vp3[2], "W")
row("p2 §二", "V_p≈3 V 时 P_L", P["r26"], vp3[2], "W")
top = pts[-1]
row("p2 §二", "输入再加大（1.2 V）：V_p 被恒流源余量卡住", P["r27"], top[1], "V", "正负略不对称")
row("p2 §五", "运放输出电流最大（削顶时）", P["r28"], top[5] * 1e3, "mA", "< 26 mA")

# 10 kHz 环内乙类：残留尖刺
t10 = ngspice("tran_B_loop10k.cir", need=["B_loop10k_0_vrms"])
f1, th10, _ = thd("B_loop10k_vg.txt", 10e3, 2e-3, 3e-3)
row("p3 §三", "乙类环内 10 kHz THD", P["r29"], th10, "%", "比 1 kHz 的 0.071% 大")
wave("B_loop10k_vg.txt", 2.8e-3, 2.9e-3, 2001, "w_B_loop10k.csv", [1, 2, 3, 4], "t_s,v_sig,v_m,v_out,v_ld")

# ---------- 耦合电容的低频角 ----------
a = ngspice("ac_cout.cir", need=["ac_1000u_f3", "ac_470u_f3"])
row("p2 §一 / 图43-p2-1", "1000 µF + 8 Ω 低频角", P["r30"], a["ac_1000u_f3"], "Hz")
row("p2 §一", "470 µF + 8 Ω 低频角", P["r31"], a["ac_470u_f3"], "Hz")
row("p2 §一", "中频增益", P["r32"], a["ac_1000u_gmid"], "")
for nm in ("1000u", "470u"):
    raw = np.loadtxt(WORK / f"ac_{nm}_vg.txt")
    np.savetxt(OUT / f"ac_{nm}.csv", raw[::5, :2], delimiter=",", fmt="%.6g", header="f_hz,gain", comments="")

# ---------- 教师复核后补充：恒流源算式、实验 B 的 R_E1 读数、实验 C3（环内乙类慢扫）、实验 D（试听三连比） ----------
c = ngspice("ccs_op.cir", need=["ccs_vd56", "ccs_veb3", "ccs_vrx3"])
row("p2 §一 / 图43-p2-6", "D5+D6 两端", P["c_vd56"], c["ccs_vd56"], "V")
row("p2 §一 / 图43-p2-6", "Q3 发射结 V_EB", P["c_veb3"], c["ccs_veb3"], "V")
row("p2 §一 / 图43-p2-6", "Rx3 两端", P["c_vrx3"], c["ccs_vrx3"], "V", "÷ 27 Ω = 恒流源电流")
row("p2 §一 / 图43-p2-6", "Rx3 两端 ÷ 27 Ω", P["iccs"], c["ccs_vrx3"] / 27 * 1e3, "mA")
b2 = ngspice("tran_AB_B2.cir", need=["b2_iavg", "b2_vre1avg"])
row("p4 测量表 B2", "400 Hz、负载峰值 2 V：电流表平均", P["r18"], b2["b2_iavg"] * 1e3, "mA", "与 1 kHz 那次一致")
row("p4 测量表 B2′", "同上：RE1 两端直流平均", P["b2_vre1"], b2["b2_vre1avg"] * 1e3, "mV", "≈ 电流表 × 3.3 Ω")
row("p4 测量表 B2", "同上：Q1 集电极电流瞬时最大", P["b2_icmax"], b2["b2_icmax"], "A", "所以电流表用 10 A 插孔")
dl = ngspice("dc_B_loop.cir", need=["dcl_B_m_m10", "dcl_B_m_p10", "dcl_B_o_p100"])
row("p4 实验 C3", "环内乙类：inp 从 −10 mV 到 +10 mV，m 跳变", P["c3_jump"], dl["dcl_B_m_p10"] - dl["dcl_B_m_m10"], "V")
row("p4 实验 C3", "环内乙类：inp − 6 V = +0.1 V 时 OUT − 6 V", P["c3_o100"], dl["dcl_B_o_p100"] - 6, "V", "斜率约 3，没有平台")
row("p4 实验 C3", "环内乙类：inp − 6 V = −0.1 V 时 OUT − 6 V", -P["c3_o100"] if P["c3_o100"] else None, dl["dcl_B_o_m100"] - 6, "V")
row("p4 实验 C3", "环内乙类：inp − 6 V = +0.1 V 时 m − 6 V", P["c3_m100"], dl["dcl_B_m_p100"] - 6, "V")
wave("dc_B_loop_vg.txt", 5.0, 7.0, 801, "dc_B_loop.csv", [1, 3, 5], "vx_sweep,vx,v_m,v_out")
for nm in ("B_open", "AB_open", "B_loop", "AB_loop"):
    ls = ngspice(f"listen_{nm}.cir", need=[f"ls_{nm}_vmax"])
    f1, thl, _ = thd(f"listen_{nm}_vg.txt", 400, 35e-3, 60e-3)
    row("p4 实验 D", f"试听 {nm}：负载位置（喇叭+10 Ω）峰值", P[f"ls_{nm}_vp"], (ls[f"ls_{nm}_vmax"] - ls[f"ls_{nm}_vmin"]) / 2, "V", "输入 0.333 V 峰值、400 Hz")
    row("p4 实验 D", f"试听 {nm}：THD", P[f"ls_{nm}_thd"], thl, "%")

report("43 推挽功放")
