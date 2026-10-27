#!/usr/bin/env python3
"""41 4–20 mA 电流环：ngspice 复核页面数值（TI LM358 官方模型 + onsemi 2N3904 / 2N7000 模型）。
从仓库根运行：/workspace/circuits-venv/bin/python spice/41/run.py
ngspice 只在本目录读 .cir、不写任何文件（结果用 echo 打到标准输出再解析）。
页面值来自 code/41_sim.py 的公式/简化模型；SPICE 值是器件模型仿真。"""
import subprocess, re, sys, pathlib, math, importlib.util
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ROWS = []

spec = importlib.util.spec_from_file_location("sim41", ROOT / "code" / "41_sim.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


def ngspice(cir):
    """batch 运行 cir，解析形如 "RES k1=v1 k2=v2 …" 的行，返回 [dict, …]。"""
    r = subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=900)
    out = r.stdout + r.stderr
    recs = []
    for line in re.findall(r"^RES\s+(.*)$", out, re.M):
        d = {}
        for k, v in re.findall(r"(\w+)=(\S+)", line):
            try:
                d[k] = float(v)
            except ValueError:
                d[k] = v
        recs.append(d)
    if r.returncode != 0 or not recs or re.search(r"(?im)fatal error|error on line|aborted|timestep too small|op failed|no such variable", out):
        print(out[-3000:])
        sys.exit(f"ngspice 运行 {cir} 失败（返回码 {r.returncode}）")
    return recs


def pick(recs, **kw):
    for d in recs:
        if all(isinstance(d.get(k), float) and abs(d[k] - v) <= 1e-6 * max(1, abs(v)) for k, v in kw.items()):
            return d
    sys.exit(f"找不到 {kw}")


def row(loc, item, page, spice, unit="", note="", tol=None):
    dev = None if (page in (None, 0) or spice is None) else (spice - page) / abs(page) * 100
    if tol is None:
        mark = "✅"
    else:
        mark = "✅" if (dev is not None and abs(dev) <= tol) or (dev is None and spice is not None) else "⚠️"
    ROWS.append((loc, item, page, spice, unit, dev, note, mark))


def fmt(x):
    if x is None:
        return "—"
    return f"{x:.4g}"


def report(title):
    print(f"==== {title}：页面值 / SPICE 值 / 偏差% ====")
    w = max(len(r[0]) + len(r[1]) for r in ROWS) + 3
    for loc, item, page, spice, unit, dev, note, mark in ROWS:
        d = "   —  " if dev is None else f"{dev:+7.2f}%"
        print(f"{mark} {(loc + ' ' + item):<{w}} 页面 {fmt(page):>9} {unit:<4} | SPICE {fmt(spice):>9} {unit:<4} | {d}  {note}")
    n = {m: sum(1 for r in ROWS if r[7] == m) for m in ("✅", "⚠️", "❌")}
    print(f"共 {len(ROWS)} 项：✅ {n['✅']}，⚠️ {n['⚠️']}，❌ {n['❌']}。")


# ① V→I 工作点（2N3904）
R = ngspice("vi_dc.cir")
OPEN = 1e9
for rx in (0.001, 100, 220, 470):
    for vs in (0.4, 1.2, 2.0):
        d = pick(R, rx=rx, vs=vs)
        m = S.sender(vs, 0.0 if rx < 1 else float(rx))
        tag = f"R_x={0 if rx < 1 else int(rx)} Ω, {vs * 10:.0f} mA"
        row("p2/p4 表", f"{tag} 回路电流", m["ic"] * 1e3, d["irx"] * 1e3, "mA", tol=1.0)
        row("p2/p4 表", f"{tag} A0 侧 I_E", m["ie"] * 1e3, d["ie"] * 1e3, "mA", tol=0.5)
        row("p3/p4", f"{tag} 余量 V_O−V_E", m["h"], d["hd"], "V", tol=10.0)
d = pick(R, rx=220, vs=2.1)
m = S.sender(2.1, 220.0)
row("p3 §一", "R_x=220 Ω, 21 mA 回路电流", m["ic"] * 1e3, d["irx"] * 1e3, "mA", "简化模型按硬饱和算；SPICE 软饱和，页面引用 SPICE 值 20.58", tol=1.0)
row("p3 §一", "R_x=220 Ω, 21 mA 余量", m["h"], d["hd"], "V", "同上；页面引用 SPICE 值 1.20 V", tol=10.0)
for vs in (0.4, 1.2, 2.0):
    d = pick(R, rx=OPEN, vs=vs)
    m = S.sender(vs, math.inf)
    row("p3 §二/p4", f"断线 V_SET={vs} V：A0 侧 I_E", m["ie"] * 1e3, d["ie"] * 1e3, "mA", tol=1.0)
    row("p3 §二/p4", f"断线 V_SET={vs} V：余量", m["h"], d["hd"], "V", tol=3.0)
    row("p3 §二/p4", f"断线 V_SET={vs} V：A1 电压", m["vo"] * S.DIV_A1, d["va1"], "V", tol=3.0)
d = pick(R, rx=0.001, vs=2.0)
row("p2 §三", "β 误差（20 mA，1−I_C/I_E）", 100 / (S.BETA + 1), (1 - d["irx"] / d["ie"]) * 100, "%", "模型 20 mA 时 β≈98", tol=5.0)
row("p3 §四", "晶体管功耗 20 mA、R_x=0", S.p_transistor(0.020) * 1e3, d["pq"] * 1e3, "mW", tol=2.0)
d = pick(R, rx=0.001, vs=1.2)
row("p3 §四", "晶体管功耗 12 mA、R_x=0", S.p_transistor(0.012) * 1e3, d["pq"] * 1e3, "mW", tol=2.0)
d = pick(R, rx=0.001, vs=2.27273)
row("p4 报警", "analogWrite(255) 回路电流", S.vset_of(255) / S.R_S * S.BETA / (S.BETA + 1) * 1e3, d["irx"] * 1e3, "mA", tol=0.5)
d = pick(R, rx=0.001, vs=0.33868)
row("p4 报警", "analogWrite(38) 回路电流", S.vset_of(38) / S.R_S * S.BETA / (S.BETA + 1) * 1e3, d["irx"] * 1e3, "mA", "小电流时模型 β 比 100 大；页面写 SPICE 值 3.38 mA，两者都 < 3.6 mA", tol=0.5)
d = pick(R, rx=0.001, vs=5.0)
m = S.sender(5.0, 0.0)
row("p2 §四", "不分压、V_SET=5 V 时回路电流", m["ic"] * 1e3, d["irx"] * 1e3, "mA", tol=5.0)
row("p2 §四", "同上 250 Ω 功耗", m["ic"] ** 2 * 250 * 1e3, d["irx"] ** 2 * 250 * 1e3, "mW", tol=10.0)

# ①b 慢扫 R_x（sweep.cir，作图 41-p3-1/2 用）与逐点工作点（vi_dc.cir）互相印证
W = ngspice("sweep.cir")[0]
d = pick(R, rx=470, vs=2.0)
row("p3 图41-p3-1", "慢扫 R_x=470 Ω, 20 mA 回路电流（与逐点仿真比）", d["irx"] * 1e3, W["ib470"] * 1e3, "mA", "两种仿真方法互相核对", tol=0.5)
row("p3 图41-p3-2", "慢扫 R_x=470 Ω, 20 mA 余量", d["hd"], W["hb470"], "V", tol=1.0)
d = pick(R, rx=220, vs=2.1)
row("p3 图41-p3-1", "慢扫 R_x=220 Ω, 21 mA 回路电流", d["irx"] * 1e3, W["ic220"] * 1e3, "mA", tol=0.5)
row("p3 图41-p3-2", "慢扫 R_x=220 Ω, 21 mA 余量", d["hd"], W["hc220"], "V", tol=2.0)

# ② 2N7000
F = ngspice("fet.cir")
d = pick(F, rx=0.001, vs=2.0)
row("p3 §一", "2N7000 20 mA 回路电流", 20.0, d["irx"] * 1e3, "mA", "没有 β 误差", tol=0.5)
row("p3 §一", "2N7000 回路/采样电流比", 1.0, d["irx"] / d["ie"], "", tol=0.01)
d = pick(F, rx=470, vs=2.0)
row("p3 §一", "2N7000 R_x=470 Ω 20 mA 回路电流", S.VS / (S.R_RX + 470 + S.R_S) * 1e3, d["irx"] * 1e3, "mA", "MOSFET 全导通，算式按 R_DS(on)≈0", tol=3.0)
row("p3 §一", "2N7000 R_x=470 Ω A0 侧电流", S.VS / (S.R_RX + 470 + S.R_S) * 1e3, d["ie"] * 1e3, "mA", "没有基极支路，A0 读到的就是回路电流", tol=3.0)

# ③ PWM 纹波（整条回路一起仿真）
P = ngspice("pwm.cir")
for code in (45, 135, 224):
    d = pick(P, d=round(code / 255, 6))
    pp, _ = S.ripple(S.V5 * S.K_DIV, code / 255, S.F_PWM, S.R_TH, S.C_F)
    row("p3 §三", f"12k/10k code {code} 平均设定电压", S.vset_of(code), d["vavg"], "V", tol=1.0)
    row("p3 §三", f"12k/10k code {code} 纹波", pp * 1e3, d["vpp"] * 1e3, "mVpp", tol=5.0)
    row("p3 §三", f"12k/10k code {code} 回路电流纹波", pp / S.R_S * 1e6, d["ipp"] * 1e6, "µApp", tol=5.0)
for D in (0.08, 0.24, 0.40):
    d = pick(P, d=D)
    pp, _ = S.ripple(5, D, S.F_PWM, 10e3, S.C_F)
    row("p3 §三", f"不分压 10k D={D} 纹波", pp * 1e3, d["vpp"] * 1e3, "mVpp", tol=5.0)

# ③b 作图用的并排波形（wave.cir）：稳态平均值
V = ngspice("wave.cir")[0]
row("p3 图41-p3-5", "12k/10k code 224 稳态回路电流", S.vset_of(224) / S.R_S * S.BETA / (S.BETA + 1) * 1e3, V["a1"] * 1e3, "mA", tol=0.5)
row("p3 图41-p3-5", "不分压 D=0.40 稳态回路电流", 2.0 / S.R_S * S.BETA / (S.BETA + 1) * 1e3, V["a2"] * 1e3, "mA", tol=0.5)

# ④ 阶跃
T = ngspice("step.cir")
d = [x for x in T if "t99" in x][0]
row("p3 §三", "45→224 建立到 99 %", S.TAU * math.log(100), d["t99"], "s", "公式 τ·ln100 偏保守（跳变后 99 % 带按终值算）；页面写“约 0.24–0.25 s”", tol=5.0)
for cl in ("1p", "100n"):
    d = [x for x in T if x.get("cl") == cl][0]
    row("p3 §五", f"理想阶跃 0.4→2.0 V 过冲（接收端并 {cl}）", None, d["ov_pct"], "%", "页面只说“无振荡、过冲 < 1 %”")

# ⑤ 坏例：集电极（250 Ω 下端）多接一根地线（wrong_gnd.cir，page3「七」、page4 表 5）
G = ngspice("wrong_gnd.cir")
i_hand = S.VS / (S.R_RX + 470)
for vs in (0.4, 2.0):
    d = pick(G, vs=vs)
    row("p3 §七/p4 表5", f"错接地 V_SET={vs} V：250 Ω 电流", i_hand * 1e3, d["irx"] * 1e3, "mA", "手算 12/(470+250)，与设定无关", tol=1.0)
    row("p3 §七/p4 表5", f"错接地 V_SET={vs} V：250 Ω 两端", i_hand * 250, d["v250"], "V", tol=1.0)
d = pick(G, vs=2.0)
row("p3 §七", "错接地：250 Ω 功耗", i_hand ** 2 * 250 * 1e3, d["p250"] * 1e3, "mW", tol=1.0)
row("p3 §七", "错接地：R_x 470 Ω 功耗", i_hand ** 2 * 470 * 1e3, d["prx"] * 1e3, "mW", tol=1.0)
row("p3 §七", "错接地：运放输出（顶到上限）", S.V_OH, d["vout"], "V", tol=1.0)
row("p3 §七", "错接地：A0 侧 I_E", None, d["ie"] * 1e3, "mA", "发射极只剩 0.165 V，A0 显示约 1.6 mA（故障低）")
row("p3 §七", "错接地：基极电流（R_B 上）", None, d["ib"] * 1e3, "mA", "R_B 1 kΩ 功耗 ≈ 93 mW，1/4 W 内")
row("p3 §七", "错接地：余量 H", None, d["hd"], "V", "远超 1.3 V，程序报警")

report("41 4–20 mA 电流环")
