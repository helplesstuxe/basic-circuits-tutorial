#!/usr/bin/env python3
"""31 跨阻放大器：ngspice + TI LMC648x / LMx58 模型复核页面数值。从仓库根运行：python spice/31/run.py
页面值全部来自 code/31_sim.py（单极点运放模型的 Python 计算）；这里用厂家宏模型逐项对照。
网表副本写在临时目录（include 改成绝对路径），不往仓库里写文件。"""
import subprocess, re, sys, pathlib, math, tempfile
from concurrent.futures import ThreadPoolExecutor
HERE = pathlib.Path(__file__).resolve().parent
MODELS = (HERE.parent / "models").resolve()
ROWS = []


def ng(text, control, need=()):
    text = text.replace(".include ../models/", f".include {MODELS}/")
    text = re.sub(r"(?ms)^\.control.*?^\.endc\s*$", "", text)
    text = re.sub(r"(?m)^\.(tran|ac)\b.*$", "", text)
    text = text.replace("\n.end\n", f"\n.control\n{control}\n.endc\n.end\n")
    with tempfile.TemporaryDirectory() as td:
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
    if r.returncode != 0 or miss or re.search(r"(?im)fatal error|error on line|aborted|timestep too small", out):
        print(out[-3000:])
        sys.exit(f"ngspice 运行失败（返回码 {r.returncode}，缺少 {miss}）")
    return vals


def row(loc, item, page, spice, unit="", note=""):
    dev = None if (page in (None, 0) or spice is None) else (spice - page) / abs(page) * 100
    ROWS.append((loc, item, page, spice, unit, dev, note))


def fmt(x):
    return "—" if x is None else ("0" if x == 0 else f"{x:.4g}")


TIA = (HERE / "tia.cir").read_text()
STEP = (HERE / "step.cir").read_text()
OPC = 'op\necho "RES vb $&v(vb)"\necho "RES vout $&v(out)"\necho "RES vinm $&v(inm)"'


DCC = ("tran 10u 30m 0 10u uic\n"
       "meas tran vb avg v(vb) from=25m to=30m\nmeas tran vout avg v(out) from=25m to=30m\n"
       "meas tran vinm avg v(inm) from=25m to=30m\nmeas tran pk max v(out) from=25m to=30m\nmeas tran mn min v(out) from=25m to=30m\n"
       'echo "RES vb $&vb"\necho "RES vout $&vout"\necho "RES vinm $&vinm"\necho "RES pp $&pk"\necho "RES mn $&mn"')


def dc(rcalto, op="LMC648x", rf="1Meg", cf="4.7p"):
    """page4 第 3–5 步：C_F 4.7 pF 从一开始就装着。用 30 ms 瞬态（uic 起步）取 25–30 ms 平均，并检查是否在振荡。"""
    t = TIA.replace(".param rcalto=0 rf=1Meg cf=1p", f".param rcalto={rcalto} rf={rf} cf={cf}")
    if op != "LMC648x":
        t = t.replace("XU1 vb inm vcc 0 out LMC648x", "XU1 vb inm vcc 0 out LMX58_LM2904")
    v = ng(t, DCC, need=["vb", "vout", "vinm", "pp", "mn"])
    assert v["pp"] - v["mn"] < 1e-3, f"直流点在振荡：{v}"
    return v


def slow():
    t = TIA.replace(".param rcalto=0 rf=1Meg cf=1p", ".param rf=1Meg cf=1u").replace(".ic v(vb)=0.9 v(inm)=0.9 v(out)=0.95\n", "")
    t = t.replace("VRC rc 0 DC {rcalto}", "VRC rc 0 PULSE(0 5 2 1m 1m 100 200)")
    ctl = ("tran 2m 8 0 2m\n"
           "meas tran v0 find v(out) at=1.99\nmeas tran v1 find v(out) at=3.0\nmeas tran v5 find v(out) at=7.0\n"
           'echo "RES v0 $&v0"\necho "RES v1 $&v1"\necho "RES v5 $&v5"')
    return ng(t, ctl, need=["v0", "v1", "v5"])


def stepr(rf, cf, cd="70p", tr="20n"):
    """tr = 光电流从 0 升到满的时间：20 ns 当理想阶跃；10.5u 模拟 page4 第 9 步 LED 电流的斜坡（见 led()）。"""
    t = STEP.replace(".param rf=1Meg cf=0 cd=70p", f".param rf={rf} cf={cf} cd={cd}")
    t = t.replace("IPH inm 0 PULSE(0 {iph} 50u 20n 20n 1 2)", f"IPH inm 0 PULSE(0 {{iph}} 50u {tr} 20n 1 2)")
    ctl = ("tran 10n 400u 0 10n\n"
           "meas tran vi find v(out) at=45u\nmeas tran vmax max v(out) from=50u to=400u\nmeas tran vf avg v(out) from=330u to=400u\n"
           "meas tran vmin min v(out) from=300u to=400u\nmeas tran vmax2 max v(out) from=300u to=400u\n"
           'echo "RES vi $&vi"\necho "RES vmax $&vmax"\necho "RES vf $&vf"\necho "RES pp $&vmax2"\necho "RES mn $&vmin"')
    v = ng(t, ctl, need=["vi", "vmax", "vf", "pp", "mn"])
    span = v["vf"] - v["vi"]
    assert 0.9 < span / (1e-6 * {"1Meg": 1e6, "47k": 47e3}[rf]) < 1.1, f"阶跃幅度不对：{v}"
    return dict(ov=(v["vmax"] - v["vf"]) / span * 100, late_pp=(v["pp"] - v["mn"]) * 1e3, span=span)


LED = (HERE / "led.cir").read_text()


def led(rt="10k", ct="100n", tstep="1u", tstop="9m", t0="4m"):
    """page4 第 8、9 步：24 节弛张振荡器（LM358 B 半边）+ 跟随器（A 半边）+ 1 kΩ + 红色 LED。
    返回振荡器高/低、跟随器高/低、LED 电流高、周期（取 3 个周期平均）、LED 电流 10–90% 上升时间。"""
    t = LED.replace(".param rt=10k ct=100n", f".param rt={rt} ct={ct}")
    ctl = (f"tran {tstep} {tstop} 0 {tstep} uic\nlet id=(v(f)-v(a))/1k\n"
           f"meas tran ohi max v(o) from={t0} to={tstop}\nmeas tran olo min v(o) from={t0} to={tstop}\n"
           f"meas tran fhi max v(f) from={t0} to={tstop}\nmeas tran flo min v(f) from={t0} to={tstop}\n"
           f"meas tran ihi max id from={t0} to={tstop}\n"
           "meas tran t1 when v(o)=2.2 rise=2\nmeas tran t2 when v(o)=2.2 rise=5\n"
           "meas tran r10 when id=1.72e-4 rise=3\nmeas tran r90 when id=1.548e-3 rise=3\n"
           + "\n".join(f'echo "RES {k} $&{k}"' for k in ("ohi", "olo", "fhi", "flo", "ihi", "t1", "t2", "r10", "r90")))
    v = ng(t, ctl, need=["ohi", "olo", "fhi", "flo", "ihi", "t1", "t2", "r10", "r90"])
    v["per"] = (v["t2"] - v["t1"]) / 3
    v["rise"] = v["r90"] - v["r10"]
    return v


def ac_bw(rf, cf, cd="70p"):
    t = STEP.replace(".param rf=1Meg cf=0 cd=70p", f".param rf={rf} cf={cf} cd={cd}")
    t = t.replace("IPH inm 0 PULSE(0 {iph} 50u 20n 20n 1 2)", "IPH inm 0 DC 0 AC 1u")
    ctl = ("ac dec 100 10 10Meg\nlet g = mag(v(out))/1u\nlet g0 = g[0]\n"
           "let gn = g/g0\nmeas ac f3 when gn=0.70711 fall=last\nmeas ac gpk max g\n"
           'echo "RES f3 $&f3"\necho "RES g0 $&g0"\necho "RES gpk $&gpk"')
    return ng(t, ctl, need=["f3", "g0", "gpk"])


def sboa():
    t = (HERE / "sboa268.cir").read_text()
    ctl = ("ac dec 100 10 10Meg\nlet g = mag(v(out))/1u\nlet g0 = g[0]\nlet gn = g/g0\nmeas ac f3 when gn=0.70711\n"
           'echo "RES f3 $&f3"\necho "RES g0 $&g0"')
    return ng(t, ctl, need=["f3", "g0"])


def _wave(rf, cf, iph, tstop, step="10n"):
    """跑一次阶跃瞬态，把 v(out) 写到临时目录（不在仓库里留文件），返回 (t, v)。"""
    import numpy as np
    t = STEP.replace(".param rf=1Meg cf=0 cd=70p iph=1u", f".param rf={rf} cf={cf} cd=70p iph={iph}")
    with tempfile.TemporaryDirectory() as td:
        fn = pathlib.Path(td) / "w.txt"
        ng(t, f'tran {step} {tstop} 0 {step}\nwrdata {fn} v(out)\necho "RES ok 1"', need=["ok"])
        d = np.loadtxt(fn)
    return d[:, 0], d[:, 1]


def ring(rf, cf, iph="5u"):
    """理想光电流阶跃（50 µs 时 20 ns 内升满）：过冲、前几个振铃周期的频率、进入 ±5% 的时间。page4 第 10 步按钮那一段用。"""
    import numpy as np
    tt, v = _wave(rf, cf, iph, "300u")
    vi = v[(tt > 40e-6) & (tt < 49e-6)].mean(); vf = v[tt > tt[-1] * 0.95].mean(); span = vf - vi
    s = tt > 50e-6; ts = tt[s]; e = np.abs(v[s] - vf) / abs(span)
    out = ts[e > 0.05]
    x = v[s] - vf; c = np.where((x[:-1] < 0) & (x[1:] >= 0))[0][:6]
    f = (len(c) - 1) / (ts[c[-1]] - ts[c[0]]) if len(c) > 2 else 0.0
    return dict(ov=(v[s].max() - vf) / span * 100, f=f, settle=(out[-1] - 50e-6) if len(out) else 0.0, span=span)


def decay():
    """1M、C_F 0、1 µA 阶跃：振铃峰峰值随时间怎么变（page2 §四）。返回 {时刻 ms: (峰峰值 mV, 频率 kHz)}。"""
    import numpy as np
    tt, v = _wave("1Meg", "1e-18", "1u", "3m", "20n")
    res = {}
    for a in (0.3e-3, 1e-3, 2.9e-3):
        s = (tt > a) & (tt < a + 0.1e-3); w = v[s]; ts = tt[s]
        mid = (w.max() + w.min()) / 2; c = np.where((w[:-1] < mid) & (w[1:] >= mid))[0]
        res[a * 1e3] = ((w.max() - w.min()) * 1e3, (len(c) - 1) / (ts[c[-1]] - ts[c[0]]) / 1e3)
    return res


def button_led():
    """按钮直接把 +5 V 经 RLED 1 kΩ 加到红色 LED 上（page4 第 10 步）。"""
    t = ("* 按钮按下：5 V → 1k → LED\n.include ../models/LED_red_ltspice.lib\nV1 vcc 0 5\nRLED vcc a 1k\nDLED a 0 APT1608SURCK\n.end\n")
    v = ng(t, 'op\necho "RES va $&v(a)"\necho "RES i $&@RLED[i]"', need=["va", "i"])
    return v


if __name__ == "__main__":
    jobs = dict(c1=lambda: dc(0), c2=lambda: dc(5), l1=lambda: dc(0, "LM358"), l2=lambda: dc(5, "LM358"),
                sl=slow, s0=lambda: stepr("1Meg", "1e-18"), s22=lambda: stepr("1Meg", "2.2p"),
                s47=lambda: stepr("1Meg", "4.7p"), k0=lambda: stepr("47k", "1e-18"), k27=lambda: stepr("47k", "27p"),
                a47=lambda: ac_bw("1Meg", "4.7p"), sb=sboa,
                k0r=lambda: stepr("47k", "1e-18", tr="10.5u"), k27r=lambda: stepr("47k", "27p", tr="10.5u"),
                led=led, leds=lambda: led("75k", "10u", "200u", "5", "2"),
                r0=lambda: ring("47k", "1e-18"), r27=lambda: ring("47k", "27p"), r20=lambda: ring("47k", "1e-18", "20u"),
                dk=decay, bl=button_led)
    with ThreadPoolExecutor(6) as ex:
        R = {k: f.result() for k, f in {k: ex.submit(fn) for k, fn in jobs.items()}.items()}
    c1, c2, l1, l2 = R["c1"], R["c2"], R["l1"], R["l2"]
    row("p4 第 2 步", "偏置 V_B（测点 A）", 0.9016, c1["vb"], "V")
    row("p4 第 3 步", "校准①：C − A（10 MΩ 接 0 V）", 90.16, (c1["vout"] - c1["vb"]) * 1e3, "mV")
    row("p4 第 3 步", "校准①：输出 C", 0.9918, c1["vout"], "V")
    row("p4 第 3 步", "反相端 − 同相端（虚短，页面写“几 mV 以内”）", None, (c1["vinm"] - c1["vb"]) * 1e3, "mV", "模型 V_OS")
    row("p4 第 4 步", "校准②：C − A（10 MΩ 接 5 V）", -409.84, (c2["vout"] - c2["vb"]) * 1e3, "mV")
    row("p4 第 4 步", "校准②：输出 C", 0.4918, c2["vout"], "V")
    row("p4 第 5 步", "换 LM358：校准① C − A（页面按典型 I_B 20 nA）", 70.2, (l1["vout"] - l1["vb"]) * 1e3, "mV",
        "差值来自模型的 I_B，页面写“以实测为准”")
    row("p4 第 5 步", "换 LM358：偏置电流误差 = 校准① 差值", -20.0, ((l1["vout"] - l1["vb"]) - (c1["vout"] - c1["vb"])) * 1e3, "mV")
    row("p4 第 5 步", "换 LM358：校准② C − A", -409.84 - 20.0, (l2["vout"] - l2["vb"]) * 1e3, "mV")
    s = R["sl"]
    row("p4 第 6 步", "慢速演示：拨开关前 C", 0.9918, s["v0"], "V")
    row("p4 第 6 步", "慢速演示：拨开关后 1 s 的 C", 0.6757, s["v1"], "V")
    row("p4 第 6 步", "慢速演示：拨开关后 5 s 的 C", 0.4952, s["v5"], "V")
    row("p2 §四", "1M、C_F 0：过冲（单极点模型 92.9%）", 92.9, R["s0"]["ov"], "%", "TI 模型")
    dk = R["dk"]
    for tm, page in ((0.3, 1261), (1.0, 356), (2.9, 11.5)):
        row("p2 §四", f"1M、C_F 0、1 µA 阶跃：{tm:g} ms 处振铃峰峰值", page, dk[tm][0], "mV", f"频率 {dk[tm][1]:.1f} kHz（估算式 46.7 kHz）")
    row("p2 §四", "1M、C_F 2.2 pF：过冲", 32.0, R["s22"]["ov"], "%")
    row("p2 §四", "1M、C_F 4.7 pF：过冲", 5.0, R["s47"]["ov"], "%")
    row("p3", "47k、C_F 0：理想阶跃过冲（单极点模型）", 71.2, R["k0"]["ov"], "%", "TI 模型多出的延迟让过冲更大")
    row("p2 例2", "47k、C_F 27 pF：理想阶跃过冲（单极点模型 1.0%）", 1.0, R["k27"]["ov"], "%", "TI 模型")
    L, Ls = R["led"], R["leds"]
    row("p4 第 9 步", "振荡器输出高电平（24 节 3.79 V）", 3.79, L["ohi"], "V")
    row("p4 第 9 步", "振荡器输出低电平（24 节 0.63 V）", 0.63, L["olo"], "V")
    row("p4 第 9 步", "跟随器输出高电平（测点 G）", 3.51, L["fhi"], "V", "LM358 输入接近 V+ − 1.5 V，跟随器跟不满")
    row("p4 第 9 步", "跟随器输出低电平（测点 G）", 0.62, L["flo"], "V", "低于 LED 导通电压，LED 灭")
    row("p4 第 9 步", "LED 电流（亮）", 1.73, L["ihi"] * 1e3, "mA")
    row("p4 第 9 步", "慢速版 75k/10µF：周期（24 节约 1.06 s）", 1.06, Ls["per"], "s")
    row("p4 第 9 步", "慢速版：LED 电流（亮）", 1.73, Ls["ihi"] * 1e3, "mA")
    row("p4 第 10 步①", "快速版 10k/100n：周期", 1.48, L["per"] * 1e3, "ms")
    row("p4 第 10 步①", "LED 电流 10–90% 上升时间", 10.28, L["rise"] * 1e6, "µs", "1 µs 步长，±1 µs")
    row("p4 第 10 步②", "47k、C_F 0：LED 那样 10.5 µs 的慢边沿 → 过冲（页面“几乎不振”）", 1.9, R["k0r"]["ov"], "%")
    row("p4 第 10 步②", "47k、C_F 27 pF：10.5 µs 慢边沿 → 过冲", None, R["k27r"]["ov"], "%")
    bl = R["bl"]
    row("p4 第 10 步③", "按钮直接点亮 LED：电流", 3.18, bl["i"] * 1e3, "mA", f"LED 两端 {bl['va']:.3f} V")
    r0, r27, r20 = R["r0"], R["r27"], R["r20"]
    row("p4 第 10 步③", "47k、C_F 0、快边沿（5 µA）：过冲", 95.3, r0["ov"], "%")
    row("p4 第 10 步③", "47k、C_F 0：振铃频率（估算式 215.4 kHz）", 290.5, r0["f"] / 1e3, "kHz", "估算只给数量级")
    row("p4 第 10 步③", "47k、C_F 0：进入 ±5% 的时间", 106.9, r0["settle"] * 1e6, "µs")
    row("p4 第 10 步③", "47k、C_F 0、20 µA：过冲（检查线性）", 95.3, r20["ov"], "%")
    row("p4 第 10 步④", "47k、C_F 27 pF、快边沿：过冲", 0, r27["ov"], "%", "页面写“几乎不过冲”")
    row("p4 第 10 步④", "47k、C_F 27 pF：进入 ±5% 的时间", 3.3, r27["settle"] * 1e6, "µs")
    row("p2 §五", "1M、C_F 4.7 pF：−3 dB 带宽", 46.3, R["a47"]["f3"] / 1e3, "kHz")
    row("p2 §五", "1M、C_F 4.7 pF：低频跨阻", 1.0, R["a47"]["g0"] / 1e6, "MΩ")
    row("p2 例3 答案", "SBOA268 原例：100k ∥ 150p 的 −3 dB 带宽", 10.61, R["sb"]["f3"] / 1e3, "kHz")
    print("==== 31 跨阻放大器：页面值 / SPICE 值 / 偏差% ====")
    w = max(len(r[0]) + len(r[1]) for r in ROWS) + 3
    for loc, item, page, spice, unit, dev, note in ROWS:
        d = "   —  " if dev is None else f"{dev:+7.2f}%"
        print(f"{(loc + ' ' + item):<{w}} 页面 {fmt(page):>9} {unit:<3} | SPICE {fmt(spice):>9} {unit:<3} | {d}  {note}")
    print(f"共 {len(ROWS)} 项。")
