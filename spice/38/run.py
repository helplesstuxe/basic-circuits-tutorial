#!/usr/bin/env python3
"""38 同步检波（电磁流量计）：ngspice + TI LM358B / LM393A 模型复核页面数值。从仓库根运行：python spice/38/run.py
页面值全部来自 code/38_sim.py（理想元件的 Python 计算）；这里用厂家模型逐项对照。
chain.cir 的参数副本写在临时目录里（include 路径改成绝对路径），不往仓库里写文件。"""
import subprocess, re, sys, pathlib, math, tempfile
from concurrent.futures import ThreadPoolExecutor
HERE = pathlib.Path(__file__).resolve().parent
MODELS = (HERE.parent / "models").resolve()
ROWS = []

def ngspice_text(text, need=(), soft=False):
    """把网表文本写到临时目录，batch 运行，返回 {名字: 数值}。soft=True 时失败返回 None（由调用者换备用网表）。"""
    with tempfile.TemporaryDirectory() as td:
        text = text.replace(".include ../models/", f".include {MODELS}/")
        f = pathlib.Path(td) / "x.cir"
        f.write_text(text)
        (pathlib.Path(td) / ".spiceinit").write_text((HERE / ".spiceinit").read_text())
        r = subprocess.run(["ngspice", "-b", "x.cir"], cwd=td, capture_output=True, text=True, timeout=1500)
    out = r.stdout + r.stderr
    vals = {}
    for k, v in re.findall(r"^RES\s+(\S+)\s+(\S+)", out, re.M):
        try:
            vals[k] = float(v)
        except ValueError:
            vals[k] = float("nan")
    miss = [n for n in need if n not in vals or math.isnan(vals[n])]
    if r.returncode != 0 or miss or re.search(r"(?im)fatal error|error on line|aborted|timestep too small|op failed|failed!\s*$", out):
        if soft:
            return None
        print(out[-3000:])
        sys.exit(f"ngspice 运行失败（返回码 {r.returncode}，缺少 {miss}）")
    return vals

def row(loc, item, page, spice, unit="", note=""):
    dev = None if (page in (None, 0) or spice is None) else (spice - page) / abs(page) * 100
    ROWS.append((loc, item, page, spice, unit, dev, note))

def fmt(x):
    return "—" if x is None else ("0" if x == 0 else f"{x:.4g}")

def report(title):
    print(f"==== {title}：页面值 / SPICE 值 / 偏差% ====")
    w = max(len(r[0]) + len(r[1]) for r in ROWS) + 3
    for loc, item, page, spice, unit, dev, note in ROWS:
        d = "   —  " if dev is None else f"{dev:+7.2f}%"
        print(f"{(loc + ' ' + item):<{w}} 页面 {fmt(page):>9} {unit:<3} | SPICE {fmt(spice):>9} {unit:<3} | {d}  {note}")
    print(f"共 {len(ROWS)} 项。")

# ---- 1. 测试夹具（page2 例1、page4 第 3 步）----
j = ngspice_text((HERE / "jig.cir").read_text(), need=["thi", "tlo", "hi", "lo", "h2", "h3", "h4", "h5", "n50_mv"])
E = (j["thi"] - j["tlo"]) / 2 * 1e3
row("p2 例1 / p4 第 3 步", "夹具信号幅度 E（6.25 Hz 瞬态）", 2.4492, E, "mV")
row("p2 例1", "同上，按直流 .op 算（CN 断开）", 2.4734, (j["hi"] - j["lo"]) / 2 * 1e3, "mV", "页面说明 .op 会偏大约 1%")
row("p4 第 3 步", "电位器居中：直流部分", -1.979, (j["thi"] + j["tlo"]) / 2 * 1e3, "mV")
row("p4 第 3 步", "电位器拧到 9 V 端：直流部分", 42.53, (j["h2"] + j["h3"]) / 2 * 1e3, "mV")
row("p4 第 3 步", "电位器拧到 0 V 端：直流部分", -46.49, (j["h4"] + j["h5"]) / 2 * 1e3, "mV")
row("p4 第 7 步", "D5 50 Hz 干扰在 P 点的幅度", 24.49, j["n50_mv"], "mV")

# ---- 1b. U5 LM393 电平转换（page4 第 5 步）----
c = ngspice_text((HERE / "comp.cir").read_text(), need=["shi", "slo", "vthr", "tdel"])
row("p4 第 5 步", "U5 门限（RT1/RT2 分 Arduino 5 V）", 2.5, c["vthr"], "V")
row("p4 第 5 步", "D10 高 → 选择脚电压", 9.0, c["shi"], "V")
row("p4 第 5 步", "D10 低 → 选择脚电压（页面写“接近 0 V”）", None, c["slo"], "V", "低于 CD4053 在 9 V 下的低电平门限即可")
row("p4 第 5 步", "D10 上升沿 → 选择脚过 4.5 V 的延迟", None, c["tdel"] * 1e6, "µs", "相对 80 ms 半周期可忽略")

# ---- 2. 完整链路（page4 第 5～9 步，page2 §四 相位规律）----
base = (HERE / "chain.cir").read_text()
def variant(ph=0, tone=None, nosig=False, eps=False, noac=False, pot="mid"):
    t = base.replace(".param ph=0", f".param ph={ph}")
    if tone:
        per = 1 / tone
        t = t.replace("VD5 d5 0 DC 0", f"VD5 d5 0 PULSE(0 5 2m 10u 10u {per/2 - 10e-6:.9g} {per:.9g})")
    if nosig:
        t = t.replace("RS1 d9 p 1Meg", "RS1 d9 p 1e12")
    if eps:
        t = t.replace("R12 n5 dm 10k", "R12 n5 dm 10.2k")
    if noac:
        t = t.replace("CH vo h 10u", "CH vo h 10u\nRSHORT vo h 1m")
    if pot == "bot":
        t = t.replace("RPA vx w 5k", "RPA vx w 10k").replace("RPB w 0 5k", "RPB w 0 1m")
    return t
cases = {
    "ph0": variant(0), "ph45": variant(45), "ph90": variant(90), "ph180": variant(180),
    "nosig": variant(0, nosig=True), "t50": variant(0, tone=16e6 / 1024 / 2 / 156), "t51": variant(0, tone=16e6 / 1024 / 2 / 153),
    "e_ac_mid": variant(0, eps=True), "e_ac_bot": variant(0, eps=True, pot="bot"),
    "e_dc_mid": variant(0, eps=True, noac=True), "e_dc_bot": variant(0, eps=True, noac=True, pot="bot"),
}
need = ["vavg", "vmax", "vmin", "inahi", "inalo"]
IDEAL_INA = []          # 记录哪些情形连 INA 也换成了理想运放
IDEAL_U3B = []          # 记录哪些情形换成了理想 U3B


def run_case(item):
    """先用 LM358B 模型的 U3B 跑；ngspice 报 timestep too small 时，把 U3B 换成理想运放（增益 1e5）再跑一次。"""
    name, t = item
    v = ngspice_text(t, need, soft=True)
    if v is None:
        IDEAL_U3B.append(name)
        t = t.replace("XU3B com n5 vp 0 dm LMX58B_LM2904B", "EU3B dm 0 com n5 1e5")
        v = ngspice_text(t, need, soft=True)
    if v is None:
        # 第二级退路：50 Hz 干扰方波从 CN 直接打进 INA 时，三只 LM358B 模型一起在场仍不收敛，
        # 把 INA 的 A1~A3 也换成理想运放（只用在 tone 两个情形，看的是解调器对 50 Hz 的抑制）
        IDEAL_INA.append(name)
        t = (t.replace("XA1 vmid n1 vp 0 o1 LMX58B_LM2904B", "EA1 o1 0 vmid n1 1e5")
              .replace("XA2 p n2 vp 0 o2 LMX58B_LM2904B", "EA2 o2 0 p n2 1e5")
              .replace("XA3 n4 n3 vp 0 vo LMX58B_LM2904B", "EA3 vo 0 n4 n3 1e5"))
        v = ngspice_text(t, need)
    return v


with ThreadPoolExecutor(max_workers=6) as ex:
    res = dict(zip(cases, ex.map(run_case, cases.items())))
print("U3B 换成理想运放才收敛的情形：", sorted(IDEAL_U3B) or "无")
print("INA 也换成理想运放才收敛的情形：", sorted(IDEAL_INA) or "无")
mv = lambda k: res[k]["vavg"] * 1e3
r0 = res["ph0"]
row("p4 第 3 步", "INA 输出 G·E（D9 高、低半周后半段之差的一半）", 51.43, (r0["inahi"] - r0["inalo"]) / 2 * 1e3, "mV", "含 LM358B 模型")
row("p4 第 5 步", "相位 0：万用表读数", 50.89, mv("ph0"), "mV")
row("p4 第 5 步", "相位 0：纹波峰峰", 0.04, (r0["vmax"] - r0["vmin"]) * 1e3, "mV", "数值很小，看量级")
row("p2 §四 / p4 第 6 步", "相位 45°", 26.21, mv("ph45"), "mV")
row("p2 §四 / p4 第 6 步", "相位 90°", 1.02, mv("ph90"), "mV", "接近 0，看绝对值")
row("p2 §四 / p4 第 6 步", "相位 180°", -50.89, mv("ph180"), "mV")
row("p4 第 6 步", "翻转相减 (V0 − V180)/2", 50.89, (mv("ph0") - mv("ph180")) / 2, "mV")
row("p4 第 6 步", "(V0 + V180)/2 = 固定偏移", None, (mv("ph0") + mv("ph180")) / 2, "mV", "LM358B 模型失调造成")
row("p4 第 8 步", "拔掉 RS1（无信号）读数 = 零点", None, mv("nosig"), "mV", "理想元件为 0")
row("p4 第 7 步", "tone(50) 50.08 Hz：读数", 50.92, mv("t50"), "mV")
row("p4 第 7 步", "tone(50)：纹波峰峰", 10.36, (res["t50"]["vmax"] - res["t50"]["vmin"]) * 1e3, "mV")
row("p4 第 7 步", "tone(51) 51.06 Hz：读数", 50.94, mv("t51"), "mV")
row("p4 第 7 步", "tone(51)：纹波峰峰", 10.54, (res["t51"]["vmax"] - res["t51"]["vmin"]) * 1e3, "mV")
# 直流泄漏：R12 = 10.2k（ε = 2%），电位器从居中拧到 0 V 端，读数变化
dvdc = 21 * ((j["h4"] + j["h5"]) / 2 - (j["thi"] + j["tlo"]) / 2) * 1e3     # INA 输出直流的变化（mV）
pred = -0.01 * 0.9901 * dvdc
row("p4 第 9 步", "ε=2%、短接 CH：电位器居中→0 V 端 读数变化", round(pred, 2), mv("e_dc_bot") - mv("e_dc_mid"), "mV", "预测 = −(ε/2)×0.990×ΔV_DC")
row("p4 第 9 步", "ε=2%、保留 CH：同样拧电位器 读数变化", None, mv("e_ac_bot") - mv("e_ac_mid"), "mV", "理想为 0")
report("38 同步检波")
