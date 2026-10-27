#!/usr/bin/env python3
"""32 电荷放大器：ngspice + TI LMC648x / LM358 / TL072 / Nexperia 1N4148 模型复核页面数值。
从仓库根运行：python spice/32/run.py
页面值全部来自 code/32_sim.py（理想运放 + 公式）；这里用厂家宏模型逐项对照。
网表副本写在临时目录（include 改成绝对路径），不往仓库里写文件。

vmode_cf_left.cir 是 page4 第 8 步排错表「C_F 忘拔」一行的用例（C_F 10 nF 没拔、短线也没插），
本脚本把它当作一项检查（cf_left），期望 B−A ≈ −0.0437 V（断言偏差 < 0.5 mV）。
也可单独运行：cd spice/32 && ngspice -b vmode_cf_left.cir"""
import subprocess, re, sys, pathlib, math, tempfile, importlib.util
from concurrent.futures import ThreadPoolExecutor
HERE = pathlib.Path(__file__).resolve().parent
MODELS = (HERE.parent / "models").resolve()
sp = importlib.util.spec_from_file_location("sim32", HERE.parent.parent / "code" / "32_sim.py")
sim = importlib.util.module_from_spec(sp); sp.loader.exec_module(sim)
ROWS = []


def ng(text, control, need=(), params=None):
    text = text.replace(".include ../models/", f".include {MODELS}/")
    for k, v in (params or {}).items():
        text = re.sub(rf"(?m)^(\.param .*?\b{k}=)\S+", rf"\g<1>{v}", text)
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


HOLD = (HERE / "hold.cir").read_text()
VMODE = (HERE / "vmode.cir").read_text()
PIEZO = (HERE / "piezo.cir").read_text()
CF_LEFT = re.sub(r"(?s)\n\.control\n.*?\n\.endc\n", "\n", (HERE / "vmode_cf_left.cir").read_text())
AC = (HERE / "ac.cir").read_text()


def meas(pairs):
    s = ""
    for name, expr in pairs:
        s += f"meas tran {name} {expr}\n"
    s += "\n".join(f'echo "RES {n} ${"&"}{n}"' for n, _ in pairs)
    return s


def hold(op="LMC648x", **p):
    """保持模式：20 ms 松开复位按钮，30 ms 把 S1 从①拨到②，读 50 ms（tback 时拨回① V_MID，读 90 ms 看是否回到 0）。漂移用 30–130 ms。"""
    t = HOLD
    if op != "LMC648x":
        t = t.replace("XU1A vmid n vcc 0 out LMC648x", f"XU1A vmid n vcc 0 out {op}")
    if op == "TL072":   # 1989 年的 TL072 宏模型从 out=n=4.5 V 起算会卡住，只给分压点和输入点初值
        t = t.replace(".ic v(vd)=4.5 v(vmid)=4.5 v(n)=4.5 v(out)=4.5 v(si)=4.5", ".ic v(vd)=4.5 v(vmid)=4.5 v(si)=4.5")
    gear = p.pop("gear", False)
    if gear:   # C_C 10/100 nF 挂在 V_MID 缓冲输出上，默认梯形积分在 t≈0 卡住
        t = t.replace("\n.end\n", "\n.option method=gear\n.end\n")
    ctl = ("tran 20u 0.13 0 50u uic\n" +
           meas([("vm", "find v(vmid) at=28m"), ("b0", "find v(out) at=28m"), ("b1", "find v(out) at=50m"),
                 ("b2", "find v(out) at=90m"), ("d1", "find v(out) at=30m"), ("d2", "find v(out) at=130m")]))
    return ng(t, ctl, need=["vm", "b0", "b1", "b2"], params=p)


def drift(op="LMC648x"):
    """长时间漂移：松开复位按钮后不动 S1，读 1.5 s 和 9.5 s 两点（避开刚松开复位的几十毫秒恢复）。"""
    t = HOLD
    if op != "LMC648x":
        t = t.replace("XU1A vmid n vcc 0 out LMC648x", f"XU1A vmid n vcc 0 out {op}")
    if op == "TL072":
        t = t.replace(".ic v(vd)=4.5 v(vmid)=4.5 v(n)=4.5 v(out)=4.5 v(si)=4.5", ".ic v(vd)=4.5 v(vmid)=4.5 v(si)=4.5")
    ctl = "tran 1m 9.6 0 2m uic\n" + meas([("vm", "find v(vmid) at=1"), ("d1", "find v(out) at=1.5"), ("d2", "find v(out) at=9.5")])
    v = ng(t, ctl, need=["vm", "d1", "d2"], params=dict(tstep=100, tback=200))
    v["rate"] = (v["d2"] - v["d1"]) / 8.0
    return v


def vmode(cc):
    ctl = "tran 20u 60m 0 50u uic\n" + meas([("vm", "find v(vmid) at=28m"), ("o", "find v(out) at=50m")])
    v = ng(VMODE, ctl, need=["vm", "o"], params={"cc": cc})
    return v["o"] - v["vm"], v["vm"]


def cf_left():
    """page4 第 8 步排错：C_F 忘拔、短线没插（2 脚只经 C_F 接 1 脚），C_C 100 nF；读 55–59 ms 平均。"""
    ctl = ("tran 10u 60m 0 10u uic\n" +
           meas([("vb1", "avg v(out) from=55m to=59m"), ("va1", "avg v(vmid) from=55m to=59m")]))
    v = ng(CF_LEFT, ctl, need=["vb1", "va1"])
    return v["vb1"] - v["va1"]


def slow():
    ctl = ("tran 1m 30.1 0 10m uic\n" +
           meas([("vm", "find v(vmid) at=28m"), ("p", "max v(out) from=30m to=40m"),
                 ("t5", "find v(out) at=5.03"), ("t10", "find v(out) at=10.03"), ("t20", "find v(out) at=20.03"),
                 ("t30", "find v(out) at=30.03")]))
    return ng(HOLD, ctl, need=["vm", "p", "t10"], params=dict(cs="100n", cf="1u", rf="10Meg", tback=100))


def rf10():
    ctl = ("tran 20u 1.05 0 100u uic\n" +
           meas([("vm", "find v(vmid) at=28m"), ("p", "max v(out) from=30m to=40m"), ("t1", "find v(out) at=130m"),
                 ("t3", "find v(out) at=330m"), ("t10", "find v(out) at=1.03")]))
    return ng(HOLD, ctl, need=["vm", "p", "t1"], params=dict(rf="10Meg", tback=100))


def piezo(rf):
    ctl = ("tran 50u 3.04 0 1m uic\n" +
           meas([("vm", "find v(vmid) at=28m"), ("p", "min v(out) from=30m to=60m"), ("t1", "find v(out) at=1.035"),
                 ("t3", "find v(out) at=3.035"), ("nmax", "max v(n) from=30m to=60m"), ("nmin", "min v(n) from=30m to=60m")]))
    return ng(PIEZO, ctl, need=["vm", "p", "t1", "t3", "nmax", "nmin"], params={"rf": rf})


def tap():
    """敲一下：100 nC 在 0.1 ms 内进来（快 50 倍），看 N 点是否被钳位、钳位管电流。"""
    ctl = ("tran 1u 40m 0 2u uic\n" +
           meas([("vm", "find v(vmid) at=28m"), ("p", "min v(out) from=30m to=40m"), ("nmax", "max v(n) from=30m to=40m"),
                 ("nmin", "min v(n) from=30m to=40m")]))
    return ng(PIEZO, ctl, need=["vm", "p", "nmax", "nmin"], params={"tr": "0.1m", "rf": "10Meg"})


def acsweep(cp):
    ctl = ("ac dec 50 0.001 100k\n"
           "let qv = abs(v(out))*2*pi*frequency\n"
           "meas ac mid find qv at=10\n"
           "let rel = qv/mid\n"
           "meas ac fl when rel=0.70711 rise=1\n"
           "meas ac fh when rel=0.70711 fall=1\n"
           'echo "RES mid $&mid"\necho "RES fl $&fl"\necho "RES fh $&fh"')
    return ng(AC, ctl, need=["mid", "fl", "fh"], params={"cp": cp})


def mains(cf):
    t = AC.replace("IQ vmid p DC 0 AC 1", "IQ vmid p DC 0").replace("VM m 0 DC 0 AC 0", "VM m 0 DC 0 AC 120")
    ctl = 'ac lin 3 59 61\nlet a = abs(v(out))\nmeas ac o find a at=60\necho "RES o $&o"'
    return ng(t, ctl, need=["o"], params={"cf": cf})


def dmm():
    t = HOLD.replace("CC si 0 {cc}", "CC si 0 {cc}\nRDMM n 0 10Meg")
    ctl = "tran 50u 0.8 0 200u uic\n" + meas([("vm", "find v(vmid) at=28m"), ("o", "find v(out) at=0.8")])
    return ng(t, ctl, need=["vm", "o"], params=dict(rf="10Meg"))


def nori():
    """拿掉 R_I（C_S 直接接 N）：U1A 输出经 C_F、C_S 看到约 0.9 nF 容性负载，看会不会振荡。"""
    t = HOLD.replace("RI si n {ri}", "RI si n 1m")
    ctl = ("tran 20n 5m 0 20n uic\n" +
           meas([("omax", "max v(out) from=4m to=5m"), ("omin", "min v(out) from=4m to=5m"),
                 ("per", "trig v(out) val=4.5 rise=1 td=4m targ v(out) val=4.5 rise=11 td=4m")]))
    return ng(t, ctl, need=["omax", "omin"])


def nori2():
    """拿掉 R_I，松开复位按钮之后（C_F 10 nF 串 C_S 1 nF 当负载）是否还振荡：读 25–26 ms。约 2 分钟。"""
    t = HOLD.replace("RI si n {ri}", "RI si n 1m")
    ctl = ("tran 20n 26m 0 20n uic\n" +
           meas([("omax", "max v(out) from=25m to=26m"), ("omin", "min v(out) from=25m to=26m"),
                 ("per", "trig v(out) val=4.5 rise=1 td=25m targ v(out) val=4.5 rise=11 td=25m")]))
    return ng(t, ctl, need=["omax", "omin"])


def withri():
    ctl = "tran 20n 5m 0 20n uic\n" + meas([("omax", "max v(out) from=4m to=5m"), ("omin", "min v(out) from=4m to=5m")])
    return ng(HOLD, ctl, need=["omax", "omin"])


def make_jobs():
    return {
        "h_dn": lambda: hold(), "h_up": lambda: hold(tgt=1),
        "h_back": lambda: hold(tback="60m"),
        "h_c10": lambda: hold(cc="10n"), "h_c100": lambda: hold(cc="100n"),
        "v0": lambda: vmode("1f"), "v10": lambda: vmode("10n"), "v100": lambda: vmode("100n"),
        "cf_left": cf_left,
        "slow": slow, "rf10": rf10, "pz_hold": lambda: piezo("1e15"), "pz_rf": lambda: piezo("10Meg"), "tap": tap,
        "ac10": lambda: acsweep("10n"), "ac20": lambda: acsweep("20n"), "ac30": lambda: acsweep("30n"),
        "m1": lambda: mains("1n"), "m10": lambda: mains("10n"), "m100": lambda: mains("100n"),
        "lm358": lambda: hold(op="LMX58_LM2904", tstep=10, tback=20), "tl072": lambda: drift("TL072"),
        "lmc": lambda: drift(), "dmm": dmm, "nori": nori, "nori2": nori2, "withri": withri,
    }


def main():
    jobs = make_jobs()
    with ThreadPoolExecutor(8) as ex:   # nori2 最慢（约 2 分钟）
        fut = {k: ex.submit(f) for k, f in jobs.items()}
        R = {k: f.result() for k, f in fut.items()}

    VM = sim.VMID
    h = R["h_dn"]
    row("p4 第 5 步", "S1 ①→②（V_MID→0 V），B−A", sim.charge_mode(-VM), h["b1"] - h["vm"], "V", f"SPICE V_MID = {h['vm']:.4f} V")
    row("p4 第 5 步", "复位后 B−A（零点）", 0.0, h["b0"] - h["vm"], "V", "页面写「约 0」")
    hb = R["h_back"]
    row("p4 第 5 步", "S1 拨回①（V_MID），B−A", 0.0, hb["b2"] - hb["vm"], "V", "页面写「回到约 0」")
    hu = R["h_up"]
    row("p4 第 6 步", "S1 ①→②（②断电改接 +9 V），B−A", sim.charge_mode(sim.VCC - VM), hu["b1"] - hu["vm"], "V")
    for k, cc in (("h_c10", 10e-9), ("h_c100", 100e-9)):
        row("p4 第 7 步", f"电荷模式 + C_C {cc*1e9:.0f} nF，B−A", sim.charge_mode(-VM), R[k]["b1"] - R[k]["vm"], "V")
    for k, cc in (("v0", 0.0), ("v10", 10e-9), ("v100", 100e-9)):
        o, vm = R[k]
        row("p4 第 8 步", f"电压模式 C_C {cc*1e9:.0f} nF，B−A", sim.voltage_mode(-VM, cc=cc), o, "V",
            "输出贴近 0 V 轨" if cc == 0 else "")
    cl = R["cf_left"]
    row("p4 第 8 步", "电压模式 C_F 忘拔（无短线），B−A", -0.0437, cl, "V", "page4 排错行写的 SPICE 值")
    assert abs(cl - (-0.0437)) < 0.5e-3, f"cf_left B−A = {cl:.5f} V，偏离页面 −0.0437 V"
    r = R["rf10"]
    row("p4 第 9 步", "断电插上 R_F 后：峰值 B−A", sim.charge_mode(-VM), r["p"] - r["vm"], "V", "DMM 看不到，SPICE 才看得到")
    row("p4 第 9 步", "断电插上 R_F 后：0.1 s 后", 0.45 * math.exp(-1), r["t1"] - r["vm"], "V")
    row("p4 第 9 步", "断电插上 R_F 后：1 s 后", float(sim.decay(0.45, 0.1, 1.0)), r["t10"] - r["vm"], "V", "页面写「约 0」")
    s = R["slow"]
    row("p4 第 10 步", "慢速演示峰值", 0.45, s["p"] - s["vm"], "V")
    for tt in (5, 10, 20, 30):
        row("p4 第 10 步", f"慢速演示 {tt} s", float(sim.decay(0.45, 10, tt)), s[f"t{tt}"] - s["vm"], "V")
    for k, rf, nm in (("pz_hold", None, "保持"), ("pz_rf", 10e6, "R_F 10 MΩ")):
        p = R[k]
        row("p4 第 12 步", f"压电 100 nC（{nm}）峰值 B−A", -1.0, p["p"] - p["vm"], "V", "100 nC 为假设电荷")
        if rf is None:
            row("p4 第 12 步", "保持模式 3 s 后（按住不放）", -1.0, p["t3"] - p["vm"], "V")
        else:
            row("p4 第 13 步", "R_F 10 MΩ：1 s 后（按住不放）", -math.exp(-1), p["t1"] - p["vm"], "V", "τ = 1 s")
            row("p4 第 13 步", "R_F 10 MΩ：3 s 后（按住不放）", -math.exp(-3), p["t3"] - p["vm"], "V")
        row("p4 第 12/13 步", f"N 点偏离 V_MID 最大（{nm}）", None, max(abs(p["nmax"] - p["vm"]), abs(p["nmin"] - p["vm"])) * 1e3, "mV", "钳位管不导通")
    tp = R["tap"]
    row("p3 / p4", "快敲（0.1 ms）峰值 B−A", -1.0, tp["p"] - tp["vm"], "V")
    row("p3 / p4", "快敲时 N 点偏离 V_MID 最大", None, max(abs(tp["nmax"] - tp["vm"]), abs(tp["nmin"] - tp["vm"])) * 1e3, "mV", "< 0.4 V 即钳位管未导通")
    for k, cp in (("ac10", 10e-9), ("ac20", 20e-9), ("ac30", 30e-9)):
        a = R[k]
        row("p2 第四节", f"f_H（C_p {cp*1e9:.0f} nF，R_I 10 kΩ）", sim.f_h(sim.RI, cp), a["fh"], "Hz")
        if cp == 20e-9:
            row("p2 第三节", "f_L（R_F 10 MΩ，C_F 100 nF）", sim.f_l(sim.RF, sim.CF2), a["fl"], "Hz")
            row("p2 第二节", "中频 |V/Q|", 1 / sim.CF2, a["mid"], "V/C")
    for k, cf in (("m1", 1e-9), ("m10", 10e-9), ("m100", 100e-9)):
        row("p3 第五节", f"120 V 60 Hz 经 0.1 pF，C_F {cf*1e9:g} nF", sim.pickup(120, 0.1e-12, cf) * 1e3, R[k]["o"] * 1e3, "mV",
            "R_F 10 MΩ 并联" if cf != 100e-9 else "")
    for k, nm in (("lmc", "LMC6482"), ("tl072", "TL072"), ("lm358", "LM358")):
        d = R[k]
        rate = d["rate"] if "rate" in d else (d["d2"] - d["d1"]) / 0.1
        row("p3 第一节", f"{nm} 保持模式漂移（C_F 10 nF）", sim.drift(sim.IB_TYP[nm], sim.CF1) * 1e3, rate * 1e3, "mV/s",
            "页面为手册典型值 I_B/C_F；符号随 I_B 方向")
    d = R["dmm"]
    row("p4 思考题 1", "万用表 10 MΩ 碰 N（有 R_F）：B 对 0 V", None, d["o"], "V", "页面答案：顶到 +9 V 轨附近")

    a, b = R["nori"], R["withri"]
    row("p3 误区", "拿掉 R_I：输出振荡峰峰值（复位中）", None, (a["omax"] - a["omin"]) * 1e3, "mV",
        f"振荡频率约 {10 / a['per'] / 1e3:.0f} kHz" if a.get("per") and a["per"] == a["per"] else "")
    c = R["nori2"]
    row("p3 误区", "拿掉 R_I：松开复位后峰峰值", None, (c["omax"] - c["omin"]) * 1e3, "mV",
        f"振荡频率约 {10 / c['per'] / 1e3:.0f} kHz")
    row("p3 误区", "有 R_I 10 kΩ：输出峰峰值（复位中）", None, (b["omax"] - b["omin"]) * 1e3, "mV", "不振荡")
    print(f"{'位置':10s} {'项目':34s} {'页面':>10s} {'SPICE':>10s} {'单位':6s} {'偏差%':>8s}  备注")
    for loc, item, page, sp_, unit, dev, note in ROWS:
        print(f"{loc:10s} {item:34s} {fmt(page):>10s} {fmt(sp_):>10s} {unit:6s} {('—' if dev is None else f'{dev:+.2f}'):>8s}  {note}")


if __name__ == "__main__":
    main()
