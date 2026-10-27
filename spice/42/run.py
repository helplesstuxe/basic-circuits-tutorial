#!/usr/bin/env python3
"""42 流量计信号链总览：ngspice 复核页面数值。
从仓库根运行：/workspace/circuits-venv/bin/python spice/42/run.py
ngspice 只在本目录读 .cir、不写任何文件（结果用 echo 打到标准输出再解析）。
页面值来自 code/42_sim.py（公式 + 逐步仿真）；SPICE 值来自器件模型（TI LM393A、TI LM358、onsemi 2N3904、TI LM317 行为模型）
和少量行为元件（测速线开关 S1、风扇等效电阻、开方 B 源），行为元件在 review/spice/42.md 里逐一声明。"""
import subprocess, re, sys, pathlib, importlib.util
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ROWS = []

spec = importlib.util.spec_from_file_location("sim42", ROOT / "code" / "42_sim.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


def ngspice(cir):
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
        if all((d.get(k) == v) if isinstance(v, str) else (isinstance(d.get(k), float) and abs(d[k] - v) <= 1e-6 * max(1, abs(v)))
               for k, v in kw.items()):
            return d
    sys.exit(f"找不到 {kw}")


def row(loc, item, page, spice, unit="", note="", tol=None):
    dev = None if (page in (None, 0) or spice is None) else (spice - page) / abs(page) * 100
    mark = "✅" if tol is None or (dev is not None and abs(dev) <= tol) else "⚠️"
    ROWS.append((loc, item, page, spice, unit, dev, note, mark))


def fmt(x):
    return "—" if x is None else f"{x:.4g}"


def report(title):
    print(f"==== {title}：页面值 / SPICE 值 / 偏差% ====")
    w = max(len(r[0]) + len(r[1]) for r in ROWS) + 3
    for loc, item, page, spice, unit, dev, note, mark in ROWS:
        d = "   —  " if dev is None else f"{dev:+7.2f}%"
        print(f"{mark} {(loc + ' ' + item):<{w}} 页面 {fmt(page):>9} {unit:<4} | SPICE {fmt(spice):>9} {unit:<4} | {d}  {note}")
    n = {m: sum(1 for r in ROWS if r[7] == m) for m in ("✅", "⚠️", "❌")}
    print(f"共 {len(ROWS)} 项：✅ {n['✅']}，⚠️ {n['⚠️']}，❌ {n['❌']}。")


# ① 宽带通 + 施密特（LM393A 模型）
FE = ngspice("frontend.cir")
for f in (10.0, 60.0, 100.0):
    d = pick(FE, f=f)
    q = S.frontend(f, t_end=0.8, keep_from=0.4)
    row("p4 第 2 级", f"{f:.0f} Hz 输出频率（相邻上升沿）", f, d["fm"], "Hz", "不多数、不漏数", tol=0.1)
    row("p4 第 2 级", f"{f:.0f} Hz NB 最高", q["nb_max"], d["nbmax"], "V", tol=3.0)
    row("p4 第 2 级", f"{f:.0f} Hz NB 最低", q["nb_min"], d["nbmin"], "V", tol=3.0)
    row("p4 测量表", f"{f:.0f} Hz 测速线直流平均（万用表）", q["avg_tach"], d["avt"], "V", tol=2.0)
    row("p4 测量表", f"{f:.0f} Hz NB 直流平均", q["avg_nb"], d["avnb"], "V", tol=2.0)
    row("p4 测量表", f"{f:.0f} Hz D2 直流平均", q["avg_out"], d["avout"], "V", tol=3.0)
d = pick(FE, f=60.0)
row("p2/p4", "施密特上门限（IN+ 最高）", S.VU, d["vup"], "V", tol=1.0)
row("p2/p4", "施密特下门限（IN+ 最低）", S.VL, d["vdn"], "V", tol=1.0)
row("p2/p4", "输出高电平", S.VOH, d["omax"], "V", "模型输出级漏电比手算小", tol=2.0)
row("p2/p4", "输出低电平", S.VOL, d["omin"], "V", "沿用 36 节 SPICE 值", tol=3.0)
row("p4 第 2 级", "停转后 0.35 s 内输出摆动", None, d["stopswing"], "V", "≈0：没有脉冲，D2 不再翻转")
C = ngspice("count.cir")[0]
row("p4 第 2 级", "60 Hz：第 1 到第 61 个上升沿的间隔", 1.0, C["dt"], "s", "1 s 恰好 60 个周期", tol=0.01)

# ② LM317 风扇电源
L = ngspice("lm317.cir")
for r, v in ((0.001, 0.0), (528, 528.0), (1104, 1104.0), (1680, 1680.0)):
    d = pick(L, r=r)
    row("p4 第 1 级", f"R_ADJ = {v:.0f} Ω 输出", S.lm317_v(v), d["vo"], "V", tol=1.0)
d = pick(L, r=2000)
row("p4 第 1 级", "R_ADJ = 2 kΩ 输出", S.lm317_v(2000), d["vo"], "V", "模型压差固定 0.5 V；真片压差更大，页面写“实测最高值”", tol=None)
for v, r in ((4.0, 528), (7.0, 1104), (10.0, 1680)):
    d = pick(L, r=r)
    row("p4 安全", f"风扇 {v:.0f} V 时 LM317 功耗（80 Ω 负载）", (12 - v) * v / 80, d["pz"], "W", "页面按标签 0.15 A 估算，见 review", tol=2.0)

# ③ 41 发送器（V5 = 5.00 与 4.83）
SN = ngspice("sender.cir")
for f in (0.0, 30.0, 50.0, 80.0, 100.0):
    m = S.chain(f)
    d = pick(SN, cfg="s5", code=float(m["code"]))
    row("p4 预期表", f"f={f:.0f} Hz 码 {m['code']} 回路电流", m["ic"] * 1e3, d["irx"] * 1e3, "mA", tol=1.0)
    row("p4 预期表", f"f={f:.0f} Hz 250 Ω 电压", m["v250"], d["v250"], "V", tol=1.0)
    row("p4 预期表", f"f={f:.0f} Hz A0 处 V_E", m["ie"] * 100, d["ve"], "V", tol=1.0)
for m in S.LAB_483 + S.LAB_483_OK:
    d = pick(SN, cfg="s483", code=float(m["code"]))
    row("p4 V5 实验", f"V5=4.83 码 {m['code']} 回路电流", m["ic"] * 1e3, d["irx"] * 1e3, "mA", tol=1.0)
    row("p4 V5 实验", f"V5=4.83 码 {m['code']} A0 处 V_E", m["ie"] * 100, d["ve"], "V", tol=1.0)

# ④ 开方（行为 B 源，核对 Python 表）
D = ngspice("dp.cir")
for p in (0.01, 0.1, 0.25, 0.5):
    d = pick(D, p=p)
    row("p3 §一", f"差压 {p*100:.0f} %：开一次", S.DBL[p][0] if p in S.DBL else p ** 0.5, d["q1"], "", tol=0.1)
    row("p3 §二", f"差压 {p*100:.0f} %：开两次", p ** 0.25, d["q2"], "", tol=0.1)
d = pick(D, p=0.007)
row("p3 §一", "差压 0.7 %：3051S 过渡段输出", float(S.s3051(0.007)), d["q3"], "", "斜率 41.7 的直线段", tol=0.1)

report("42 流量计信号链")
