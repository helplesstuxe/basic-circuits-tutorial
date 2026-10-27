#!/usr/bin/env python3
"""39 恒流源与线圈励磁驱动：ngspice + TI LM358B / Infineon IRLZ44N 官方模型复核页面数值。
从仓库根运行：python spice/39/run.py（约 15 s）。顺便把波形抽稀成小 CSV（coil_v.csv、coil_i.csv、coil_i_nosnub.csv、step.csv），
供 code/figs/39_figs.py 画图。
默认所有仿真输出（*_vg.txt 和 CSV）都写到临时目录，不覆盖仓库里已有的文件；
只有维护者要更新画图用的 CSV 时才加 --update：python spice/39/run.py --update"""
# ---- 通用小工具：调用 ngspice -b，解析 .control 里 echo 出来的 "RES 名字 数值" ----
import subprocess, re, sys, pathlib, math, shutil, tempfile
HERE = pathlib.Path(__file__).resolve().parent
# 在临时目录里跑 ngspice（网表里的 ../models 用符号链接指回仓库），原始波形 txt 写在那里
WORK = pathlib.Path(tempfile.mkdtemp(prefix="spice39_")) / "39"
WORK.mkdir()
(WORK.parent / "models").symlink_to(HERE.parent / "models")
for f in list(HERE.glob("*.cir")) + [HERE / ".spiceinit"]:
    shutil.copy(f, WORK)
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

def wave(name, cols, t0, t1, n, out, header):
    """读 wrdata 文件（时间/数值成对排列），在 [t0, t1] 上均匀重采样 n 点，写成小 CSV。"""
    d = np.loadtxt(WORK / name)
    t = d[:, 0]
    tt = np.linspace(t0, t1, n)
    vals = [np.interp(tt, t, d[:, 2 * c + 1]) for c in cols]
    np.savetxt(OUT / out, np.column_stack([tt] + vals), delimiter=",", fmt="%.6g", header=header, comments="")

# ---------- 1. 直流恒流：负载扫描（39_ccs.cir） ----------
c = ngspice("39_ccs.cir", need=["vref", "i_47", "vds_47", "i_100", "i_120", "i_vs115", "vg_47", "vg_120"])
row("p2 §二 第一步", "V_REF（R1 10k / R2 910 分压）", 1.0009, c["vref"], "V")
row("p2 §二 第二步", "I_SET = V_REF/R_S", 100.09, c["i_47"] * 1e3, "mA")
for r, vds in ((0.01, 10.999), (10, 9.999), (22, 8.799), (47, 6.296), (68, 4.194), (100, 0.990)):
    k = f"{r:g}"
    row("p2 §二 第三步 / 图39-p2-2", f"R_L={k} Ω 电流", 100.09, c[f"i_{k}"] * 1e3, "mA")
    row("p2 §二 第三步 / 图39-p2-2", f"R_L={k} Ω V_DS", vds, c[f"vds_{k}"], "V")
row("p2 §二 第四步", "R_L 上限（V_DS 留 0.5 V）105 Ω 时电流", 100.09, c["i_105"] * 1e3, "mA")
row("p2 §二 第四步 / p4 测量表", "R_L=120 Ω 掉出恒流区", 92.3, c["i_120"] * 1e3, "mA", "按 (12−0.0016)/(130) 估")
row("p2 图39-p2-2", "R_L=150 Ω 电流", 75.0, c["i_150"] * 1e3, "mA")
row("p4 测量表", "运放 1 脚（R_L=47 Ω）", 3.14, c["vg_47"], "V", "页面按 SPICE 给参考值")
row("p4 测量表 / p3 排查表", "运放 1 脚顶到上限（R_L=120 Ω）", 10.83, c["vg_120"], "V", "LM358B 12 V 供电输出上限")
row("p3 练习2", "电源掉到 11.5 V 时 V_REF（同一电源分压）", 0.959, c["vref_vs115"], "V")
row("p3 练习2", "电源掉到 11.5 V，R_L=47 Ω（恒流区内，设定电流跟着掉）", 95.9, c["i_vs115"] * 1e3, "mA")
row("p3 练习2", "电源掉到 11.5 V，R_L=110 Ω（超过上限 104.7 Ω，MOS 全开）", 95.8, c["i_vs115_110"] * 1e3, "mA", "按 11.5/(110+10) 估")

# ---------- 2. 阶跃响应：补偿 vs 不补偿（39_step.cir） ----------
s = ngspice("39_step.cir", need=["os_1", "os_0", "rip_0", "rip_1", "tr_1", "fosc_0"])
row("p3 图39-p3-2", "有补偿 过冲", 15.0, s["os_1"], "%")
row("p3 图39-p3-2", "有补偿 到 0.95 V 用时", 2.1, s["tr_1"], "µs")
row("p3 图39-p3-2", "有补偿 0.2 ms 后残余纹波", None, s["rip_1"] * 1e3, "mVpp", "页面写“没有持续振荡”")
row("p3 图39-p3-2", "无补偿 过冲", 28.7, s["os_0"], "%")
row("p3 图39-p3-2 / 排查表", "无补偿 持续振荡峰峰值", 54.5, s["rip_0"] * 1e3, "mVpp")
row("p3 图39-p3-2 / 排查表", "无补偿 振荡频率", 147.0, s["fosc_0"] / 1e3, "kHz")
wave("step_1_vg.txt", [0], 2.995e-3, 3.06e-3, 1300, "step.csv", "t_s,vs_comp")
d0 = np.loadtxt(WORK / "step_0_vg.txt")
st = np.loadtxt(OUT / "step.csv", delimiter=",", skiprows=1)
np.savetxt(OUT / "step.csv", np.column_stack([st, np.interp(st[:, 0], d0[:, 0], d0[:, 1])]), delimiter=",", fmt="%.6g",
           header="t_s,vs_comp,vs_nocomp", comments="")

# ---------- 3. 线圈换向：电压驱动（39_coil_v.cir） ----------
v = ngspice("39_coil_v.cir", need=["ipos_0", "ineg_0", "t99_0", "tz_0"])
row("p2 §四 / 图39-p2-5", "电压驱动 稳态电流 12/(75+0.565)", 158.8, v["ipos_0"] * 1e3, "mA")
row("p2 §四 / 图39-p2-5", "电压驱动 换向后过零 τ·ln2", 0.917, v["tz_0"], "ms")
row("p2 §四 / 图39-p2-5", "电压驱动 到 99%：τ·ln200", 7.01, v["t99_0"], "ms")
wave("coil_0_vg.txt", [0, 1, 2], 0.150, 0.250, 2001, "coil_v.csv", "t_s,i_A,v_o1,v_o2")

# ---------- 4. 线圈换向：恒流 + H 桥（39_coil_i.cir，有 / 无 RC 吸收） ----------
k = ngspice("39_coil_i.cir", need=["ipos_100n", "t99_100n", "tz_100n", "ipk_100n", "vds_100n", "botlo_1p", "bothi_1p", "ilo_1p", "ihi_1p"])
row("p2 §四 / 图39-p2-5", "恒流驱动 稳态电流", 100.09, k["ipos_100n"] * 1e3, "mA")
row("p2 §四 / 图39-p2-5", "恒流驱动 换向后过零", 0.63, k["tz_100n"], "ms")
row("p2 §四 / 图39-p2-5", "恒流驱动 到 99%", 2.06, k["t99_100n"], "ms")
row("p2 §四 / 图39-p2-5", "恒流驱动 换向后冲到", 119.1, k["ipk_100n"] * 1e3, "mA", "运放内部节点已限幅")
row("p2 §四", "恒流驱动 稳态 V_DS", 3.44, k["vds_100n"], "V")
row("p3 图39-p3-3 / 排查表", "无 RC 吸收：桥底电压最低", 1.01, k["botlo_1p"], "V")
row("p3 图39-p3-3 / 排查表", "无 RC 吸收：桥底电压最高", 12.54, k["bothi_1p"], "V")
row("p3 图39-p3-3", "无 RC 吸收：电流最低", 98.8, k["ilo_1p"] * 1e3, "mA")
row("p3 图39-p3-3", "无 RC 吸收：电流最高", 102.2, k["ihi_1p"] * 1e3, "mA")
row("p3 图39-p3-3", "有 RC 吸收：桥底电压（稳定）", 4.44, k["bothi_100n"], "V")
wave("coil_i_100n_vg.txt", [0, 3], 0.150, 0.250, 2001, "coil_i.csv", "t_s,i_A,v_bot")
wave("coil_i_1p_vg.txt", [0, 3], 0.2300, 0.2315, 1501, "coil_i_nosnub.csv", "t_s,i_A,v_bot")
w = np.loadtxt(WORK / "coil_i_100n_vg.txt")
_t, _i = w[:, 0], w[:, 1]
_bad = (_t > 0.160) & (_t < 0.239) & (np.abs(_i - k["ipos_100n"]) > 1e-3)
row("p2 §四 / 图39-p2-5", "恒流驱动 进入 100 mA ±1 mA（换向后）", 3.36, (_t[_bad].max() - 0.160) * 1e3, "ms")
_pk = (_t > 0.160) & (_t < 0.180)
row("p2 §四 / 图39-p2-5", "恒流驱动 过冲峰值时刻（换向后）", 2.84, (_t[_pk][np.argmax(_i[_pk])] - 0.160) * 1e3, "ms")
sel = (w[:, 0] > 0.2300) & (w[:, 0] < 0.2315)
assert np.ptp(w[sel, 7]) < 0.01, "有吸收时桥底电压应当平稳"
# 无吸收时的振荡周期（桥底电压上穿中线的平均间隔），和由它反推的等效电容（page3 N2 修订）
w1 = np.loadtxt(WORK / "coil_i_1p_vg.txt")
s1 = (w1[:, 0] > 0.2300) & (w1[:, 0] < 0.2315)
_tb, _vb = w1[s1, 0], w1[s1, 7]
_m = (_vb.max() + _vb.min()) / 2
_j = np.where((_vb[:-1] < _m) & (_vb[1:] >= _m))[0]
_tx = _tb[_j] + (_m - _vb[_j]) / (_vb[_j + 1] - _vb[_j]) * (_tb[_j + 1] - _tb[_j])
T_OSC = float(np.mean(np.diff(_tx)))
C_EQ = (T_OSC / (2 * np.pi)) ** 2 / 0.1
row("p3 图39-p3-3 / RC 吸收", "无 RC 吸收：振荡周期", 175, T_OSC * 1e6, "µs")
row("p3 RC 吸收", "反推等效电容 (T/2π)²/L", 7.8, C_EQ * 1e9, "nF", "L = 0.1 H")
row("p3 RC 吸收", "sqrt(L/C_eq)", 3.6, math.sqrt(0.1 / C_EQ) / 1e3, "kΩ")

# ---------- 5. 错误接法：采样电阻放高边（39_wrong.cir） ----------
wr = ngspice("39_wrong.cir", need=["w_i", "w_vx", "w_vo"])
row("p3 图39-p3-4 预测题", "高边接法：反馈点电压", 12.0, wr["w_vx"], "V")
row("p3 图39-p3-4 预测题", "高边接法：运放输出（被拉到底）", None, wr["w_vo"], "V", "页面写“约 0 V”")
row("p3 图39-p3-4 预测题", "高边接法：负载电流", None, wr["w_i"] * 1e3, "mA", "页面写“几乎为 0”")

report("39 恒流源与线圈励磁驱动")
