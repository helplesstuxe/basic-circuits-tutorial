"""37 过零检测与超声波时差：SPICE 核对。运行：/workspace/circuits-venv/bin/python spice/37/run.py
页面数值来自 code/37_sim.py（import 进来，不另抄一份），每项与 SPICE 比，偏差 ≤10% 记 ✅。
74HC74 的两级逻辑在 SPICE 里没有模型，由 flipflop() 对 arm、zc 两路波形做行为级判断。"""
import importlib.util, sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ng

_spec = importlib.util.spec_from_file_location("s37", HERE.parent.parent / "code" / "37_sim.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

A_NOM = S.V_TH / S.VTH_SPAN            # 电位器比例，使 V_TH − V_MID = 页面门限


def pwl(gain, L=S.L0):
    """放大器输出处的回波 ÷ 40 kHz 增益 = 接收头「源电压」；4 MHz 取样，0.3～1 ms。"""
    y = S.echo(L=L, gain=gain, spread=False) / S.H40K
    t = S.T_AX
    sel = (t >= 0.3e-3) & (t <= 1.0e-3)
    tt, yy = t[sel][::2], y[sel][::2]
    pts = [f"0 0 {tt[0]-1e-9:.9e} 0"] + [f"{a:.9e} {b:.6e}" for a, b in zip(tt, yy)]
    return " ".join(pts)


CASES = {
    "amp12": ("amp.cir", dict(VS=12)),
    "amp9": ("amp.cir", dict(VS=9)),
    "tx150": ("tx.cir", dict(RS=150)),
    "tx100": ("tx.cir", dict(RS=100)),
    "tx220": ("tx.cir", dict(RS=220)),
    "vth0": ("vth.cir", dict(A=0)),
    "vth1": ("vth.cir", dict(A=1)),
    "zc05": ("zc.cir", dict(PWL=pwl(0.5), A=f"{A_NOM:.5f}")),
    "zc1": ("zc.cir", dict(PWL=pwl(1.0), A=f"{A_NOM:.5f}")),
    "zc2": ("zc.cir", dict(PWL=pwl(2.0), A=f"{A_NOM:.5f}")),
    "zc07": ("zc.cir", dict(PWL=pwl(0.7), A=f"{A_NOM:.5f}")),
    "zc14": ("zc.cir", dict(PWL=pwl(1.4), A=f"{A_NOM:.5f}")),
    "zc09": ("zc.cir", dict(PWL=pwl(0.9), A=f"{A_NOM:.5f}")),
    "zc11": ("zc.cir", dict(PWL=pwl(1.1), A=f"{A_NOM:.5f}")),
}


def flipflop(dirname, t_blank=S.T_BLANK, th=2.5):
    """/CLR 在 t_blank 时松开；武装 = arm 第一次低于 2.5 V；Q2 = 武装之后 zc 第一个上升沿（插值到 2.5 V）。"""
    d = ng.load_wrdata(Path(dirname) / "out.txt")
    t, arm, zc, out = d[:, 0], d[:, 1], d[:, 3], d[:, 5]
    i0 = np.searchsorted(t, t_blank)
    ia = i0 + int(np.argmax(arm[i0:] < th))
    j = ia + 1
    while zc[j] > th:          # 武装时（正峰附近）过零输出为高，先等它变低
        j += 1
    while zc[j] < th:
        j += 1
    tq = t[j - 1] + (th - zc[j - 1]) / (zc[j] - zc[j - 1]) * (t[j] - t[j - 1])
    # 上升沿 10%→90% 时间
    sel = (t > t[ia] - 30e-6) & (t < t[ia] + 30e-6)
    return dict(t_arm=t[ia], tq=tq, omax=out[sel].max(), zc_max=zc.max(), zc_min=zc[i0:].min(),
                arm_min=arm[i0:].min())


def job(k):
    cir, p = CASES[k]
    r = ng.run(cir, p)
    if cir == "zc.cir":
        r.update(flipflop(r["_dir"]))
    return k, r


if __name__ == "__main__":
    with ProcessPoolExecutor() as ex:
        R = dict(ex.map(job, CASES))
    for k, v in R.items():
        print(k, {a: b for a, b in v.items() if a != "_dir"})
    c = ng.check
    c("page2 §二 / 图2-2", "V_MID（12 V 分压 + 跟随）", S.V_MID, R["amp12"]["vmid"], "V")
    c("page2 §二", "放大输出静态电平", S.V_MID, R["amp12"]["vout_dc"], "V")
    c("page2 §二 / page3 §五", "40 kHz 增益（含 GBW）", S.G40, R["amp12"]["g40"], "倍")
    c("page3 §五", "40 kHz 相位", None, R["amp12"]["ph40"], "°", note="sim 估 −8.3°（单极点近似）")
    c("page2 §二", "50 Hz 总增益", S.H50, R["amp12"]["g50"], "倍")
    c("page2 §二", "40 kHz 比 50 Hz 多放大", S.SUPPRESS_50, R["amp12"]["g40"] / R["amp12"]["g50"], "倍")
    c("page2 §二", "40 kHz 正弦输出峰值（输入 45.5 mV）", 0.5, (R["amp12"]["omax"] - R["amp12"]["omin"]) / 2, "V")
    c("page3 §五 / page4 安全", "9 V 供电时 V_MID", None, R["amp9"]["vmid"], "V",
      note="宏模型不模拟共模输入下限（V− + 4 V），9 V 只剩 0.5 V 余量这件事 SPICE 看不出")
    c("page3 §五", "9 V 供电时 40 kHz 增益", None, R["amp9"]["g40"], "倍", note="同上，仅供参考")
    c("page3 §四", "发射 150 Ω：引脚峰值电流", S.IPK150 * 1e3, R["tx150"]["ipk"] * 1e3, "mA")
    c("page3 §四", "发射 150 Ω：猝发时 |i| 平均", S.I_AVG * 1e3, R["tx150"]["iavg"] * 1e3, "mA", tol=15)
    c("page3 §四", "发射 100 Ω：峰值电流（超 40 mA）", S.IPK100 * 1e3, R["tx100"]["ipk"] * 1e3, "mA")
    c("page3 §四", "发射 220 Ω：峰值电流", 10 / 440 * 1e3, R["tx220"]["ipk"] * 1e3, "mA")
    c("page2 §二", "电位器拧到底：V_TH − V_MID", 0.0, R["vth0"]["dvth"], "V")
    c("page2 §二", "电位器拧到顶：V_TH − V_MID", S.VTH_SPAN, R["vth1"]["dvth"], "V")
    c("page3 §一", "示意门限 V_TH − V_MID", S.V_TH, R["zc1"]["vw"] - R["zc1"]["vmid"], "V")
    for k, g in (("zc07", 0.7), ("zc1", 1.0), ("zc14", 1.4), ("zc2", 2.0)):
        c("page3 §一 / 图3-1", f"武装+过零 t（幅度 ×{g}）", S.T_ZC[g] * 1e6, R[k]["tq"] * 1e6, "µs", tol=1)
    od05 = (S.PK[6] * 0.5 * S.A_NOM - S.V_TH) * 1e3
    c("page3 §一 / 图3-1", "武装+过零 t（幅度 ×0.5）", S.T_ZC[0.5] * 1e6, R["zc05"]["tq"] * 1e6, "µs", v="⚠️",
      note=f"理想比较器在第 7 个周期武装；第 7 峰只比门限高 {od05:.1f} mV，LM393 没翻，晚一个周期（page3 已写明）")
    d1 = (R["zc07"]["tq"] - R["zc1"]["tq"]) * 1e6
    d2 = (R["zc1"]["tq"] - R["zc14"]["tq"]) * 1e6
    c("page3 §一", "×0.7 比 ×1 晚（整周期）", (S.T_ZC[0.7] - S.T_ZC[1.0]) * 1e6, d1, "µs", tol=2)
    c("page3 §一", "×1 比 ×1.4 早（整周期）", (S.T_ZC[1.0] - S.T_ZC[1.4]) * 1e6, d2, "µs", tol=2)
    c("page3 §一", "×1.4 与 ×2 同一周期", 0.0, (R["zc14"]["tq"] - R["zc2"]["tq"]) * 1e6, "µs",
      v="✅" if abs(R["zc14"]["tq"] - R["zc2"]["tq"]) < 0.3e-6 else "?")
    sh = abs(R["zc09"]["tq"] - R["zc11"]["tq"]) * 1e9
    c("page3 §一", "×0.9 → ×1.1 过零时刻移动", S.ZC_SHIFT * 1e9, sh, "ns",
      v="✅" if sh < 300 else "⚠️", note="页面只说「不到 0.1 µs」量级；含 LM393 随过驱变的延迟")
    lag = (R["zc1"]["tq"] - S.T_ZC[1.0]) * 1e9
    c("page3 §一", "SPICE 比理想比较器晚（LM393 延迟等）", None, lag, "ns", note="固定偏移的一部分，四个间距一样，拟合截距吸收")
    c("page4 安全", "LM393 输入最高电压（放大输出峰）", None, R["zc2"]["omax"], "V", note="须低于 12 − 1.5 = 10.5 V")
    c("page2 §三", "过零输出高电平（上拉 5 V）", 5.0, R["zc1"]["zc_max"], "V")
    c("page2 §三", "过零输出低电平", None, R["zc1"]["zc_min"], "V", note="74HC74 VIL 1.35 V（4.5 V）")
    ng.save()
