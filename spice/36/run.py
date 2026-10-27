"""36 施密特整形与频率/脉冲计数：SPICE 核对。运行：/workspace/circuits-venv/bin/python spice/36/run.py
页面数值写在 PAGE 里（来自 code/36_sim.py），每项与 SPICE 比，偏差 ≤10% 记 ✅。"""
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ng

TWIN = 0.2      # 数上升沿的窗口：0.1 s 到 0.3 s
PAGE = dict(
    vh=2.6107, vl=2.3887, dv=0.2220, voh=4.948, vol=0.065,
    vh150=2.6623, vl150=2.3384,
    pp_sig=0.541, pp_noise=0.1253, pp_noise1k=0.2746,
    n_none=175, n220=100, n47=0, n_clean=100, n220_off=100, n100_off=0,
    n220_rn1k=100, n330_rn1k=175, n220_rn470=650, n68_rn470=100, n220_10k_off=0,
)

CASES = {
    "th220": ("thresh.cir", dict(R2="220k")),
    "th150": ("thresh.cir", dict(R2="150k")),
    "vol": ("vol.cir", {}),
    "amp_sig": ("amp.cir", dict(SRC="d7", NSRC="d5d")),
    "amp_noise": ("amp.cir", dict(SRC="d7d", NSRC="d5")),
    "amp_noise1k": ("amp.cir", dict(SRC="d7d", NSRC="d5", RN="1k")),
    "cnt_none": ("count.cir", dict(R2="1e12")),
    "cnt220": ("count.cir", dict(R2="220k")),
    "cnt47": ("count.cir", dict(R2="47k")),
    "cnt_clean": ("count.cir", dict(R2="1e12", RN="1e12")),
    "cnt220_off": ("count.cir", dict(R2="220k", RN="1e12")),
    "cnt100_off": ("count.cir", dict(R2="100k", RN="1e12")),
    "cnt220_rn1k": ("count.cir", dict(R2="220k", RN="1k")),
    "cnt330_rn1k": ("count.cir", dict(R2="330k", RN="1k")),
    "cnt220_rn470": ("count.cir", dict(R2="220k", RN="470")),
    "cnt68_rn470": ("count.cir", dict(R2="68k", RN="470")),
    "cnt220_10k_off": ("count.cir", dict(R2="220k", RN="1e12", RS="10k", CC="470n")),
    "pu5": ("pullup.cir", dict(VPU=5)),
    "pu9": ("pullup.cir", dict(VPU=9)),
    "cm25": ("cm.cir", dict(VB=5, VR=2.5)),
    "cm38": ("cm.cir", dict(VB=5, VR=3.8)),
    "cm9": ("cm.cir", dict(VB=9, VR=2.5)),
}


def edges(dirname, t0=0.1, t1=0.3, th=2.5):
    d = ng.load_wrdata(Path(dirname) / "out.txt")
    t, v = d[:, 0], d[:, 1]
    n, hi = 0, None
    for ti, vi in zip(t, v):
        h = vi > th
        if hi is not None and h and not hi and t0 <= ti <= t1:
            n += 1
        hi = h
    return n


def job(k):
    cir, p = CASES[k]
    r = ng.run(cir, p)
    if cir == "count.cir":
        r["edges"] = edges(r["_dir"])
        r["rate"] = r["edges"] / TWIN
    return k, r


if __name__ == "__main__":
    with ProcessPoolExecutor() as ex:
        R = dict(ex.map(job, CASES))
    for k, v in R.items():
        print(k, {a: b for a, b in v.items() if a != "_dir"})
    P = PAGE
    c = ng.check
    c("page2 §二 / 图2-2", "上门限 VH（R2 = 220k）", P["vh"], R["th220"]["vh"], "V")
    c("page2 §二 / 图2-2", "下门限 VL（R2 = 220k）", P["vl"], R["th220"]["vl"], "V")
    c("page2 §二", "回差 ΔV（R2 = 220k）", P["dv"], R["th220"]["vh"] - R["th220"]["vl"], "V")
    c("page2 §二", "输出高电平 VOH（R3 与 R2 分压）", P["voh"], R["th220"]["voh"], "V")
    c("page2 §二 / 36_sim", "输出低电平 VOL（吸约 1 mA）", P["vol"], R["vol"]["vo"], "V")
    c("page2 §六 例1", "上门限 VH（R2 = 150k）", P["vh150"], R["th150"]["vh"], "V")
    c("page2 §六 例1", "下门限 VL（R2 = 150k）", P["vl150"], R["th150"]["vl"], "V")
    c("page2 §三", "n2 上信号峰峰值（Rn = 2.2k）", P["pp_sig"], R["amp_sig"]["pp"], "V")
    c("page2 §三", "n2 上干扰峰峰值（Rn = 2.2k）", P["pp_noise"], R["amp_noise"]["pp"], "V")
    c("page3 §一 / 练习1", "n2 上干扰峰峰值（Rn = 1k）", P["pp_noise1k"], R["amp_noise1k"]["pp"], "V")
    c("page1 / page2 §三 / page4 测量表4", "不接 R2、有干扰：每秒上升沿", P["n_none"], R["cnt_none"]["rate"], "个/s")
    c("page4 第3步（测量表3）", "不接 R2、拔掉干扰：每秒上升沿", P["n_clean"], R["cnt_clean"]["rate"], "个/s")
    c("page4 第5步（测量表5）", "R2 = 220k、有干扰：每秒上升沿", P["n220"], R["cnt220"]["rate"], "个/s")
    c("page4 第6步（测量表8）", "R2 = 220k、拔掉干扰：每秒上升沿", P["n220_off"], R["cnt220_off"]["rate"], "个/s")
    c("page3 §一 / page4 第7步（测量表9）", "R2 = 47k（回差太大）：每秒上升沿", P["n47"], R["cnt47"]["rate"], "个/s")
    c("page3 §一", "R2 = 100k、拔掉干扰（回差偏大）", P["n100_off"], R["cnt100_off"]["rate"], "个/s")
    c("page3 §一 / 练习1", "Rn = 1k、R2 = 220k：每秒上升沿", P["n220_rn1k"], R["cnt220_rn1k"]["rate"], "个/s")
    c("page3 §一 / 练习1", "Rn = 1k、R2 = 330k（回差偏小）", P["n330_rn1k"], R["cnt330_rn1k"]["rate"], "个/s",
      note="多数多少取决于干扰与信号的相位；SPICE 只数了 0.2 s", tol=35)
    c("page3 §一 / 变体1", "Rn = 470、R2 = 220k（干扰太强）", P["n220_rn470"], R["cnt220_rn470"]["rate"], "个/s",
      note="同上；结论（远多于 100）一致即可", tol=35)
    c("page3 §一 / 变体1", "Rn = 470、R2 = 68k：每秒上升沿", P["n68_rn470"], R["cnt68_rn470"]["rate"], "个/s")
    c("page3 §二", "10k/470n 网络、R2 = 220k、无干扰（被回差电流拉偏）", P["n220_10k_off"], R["cnt220_10k_off"]["rate"], "个/s")
    c("page4 第5步（测量表7）", "万用表直流挡量输出（平均值，约一半时间为高）", None, R["cnt220"]["oavg"], "V")
    c("page4 安全须知", "上拉接 Arduino 5 V：D8 上的高电平", 4.95, R["pu5"]["vo"], "V",
      note="≤ 5.5 V（ATmega328P 上限 VCC+0.5 V）")
    c("page4 安全须知", "上拉错接 9 V：D8 上的高电平", None, R["pu9"]["vo"], "V",
      note="超过 5.5 V 的绝对最大值（真实芯片里保护二极管导通，电流灌进 5 V）", v="ℹ️")
    c("page2 §一 / page3 §三", "LM393 9 V 供电、IN− = 2.5 V 时翻转点", 2.5, R["cm9"]["vsw"], "V")
    c("page3 §三 / 练习2", "LM393 5 V 供电、IN− = 2.5 V 时翻转点", 2.5, R["cm25"]["vsw"], "V")
    c("page3 §三 / 练习2", "LM393 5 V 供电、IN− = 3.8 V（超出 VCC−1.5）时翻转点", None, R["cm38"]["vsw"], "V",
      note="模型照样翻转，但数据手册不保证这个区间；正文以数据手册为准", v="ℹ️")
    ng.save()
