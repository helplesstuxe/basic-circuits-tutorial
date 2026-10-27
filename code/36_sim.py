"""36 施密特整形与频率/脉冲计数：本节所有数值的出处。
运行（仓库根目录）：/workspace/circuits-venv/bin/python code/36_sim.py
页面上的每个数字都由本脚本打印，关键结论用 assert 检查。图由 code/figs/36_figs.py 画，它会 import 本文件。

实验电路（page4，图 36-p2-1）：
  Arduino D7 用 tone(7, 100) 输出方波 → Rs1 1k → 节点 n1（C1 4.7 µF 到地）→ Rs2 1k → 节点 n2（C2 4.7 µF 到地）
  Arduino D5 用 analogWrite(5, 128) 输出 976.6 Hz 方波 → Rn 2.2k → n2（人为注入的「干扰」）
  n2 → R1 10k → LM393 同相端 IN+；R2（回差电阻，220k）从输出接回 IN+；反相端 IN− = 5 V 经 10k/10k 分压 = 2.5 V
  LM393 由 9 V 电池供电；输出经 R3 4.7k 上拉到 Arduino 的 5 V（不是 9 V！），接 D8（Timer1 输入捕获）
"""
import math

# ---------------------------------------------------------------- Arduino 时钟与两路方波
F_CPU = 16_000_000          # Uno 的系统时钟（标称；实际是陶瓷谐振器，误差见 TIMEBASE）


def tone_freq(f):
    """照抄 ArduinoCore-avr Tone.cpp 里 Timer2 的选预分频规则（整数除法），返回实际输出频率。"""
    for p in (1, 8, 32, 64, 128, 256, 1024):
        ocr = F_CPU // f // 2 // p - 1
        if ocr <= 255:
            return F_CPU / (2 * p * (ocr + 1)), p, ocr
    raise ValueError


F_SIG, TONE_P, TONE_OCR = tone_freq(100)
F_NOISE = F_CPU / 64 / 256      # Timer0 快速 PWM：D5、D6 的 analogWrite 频率
assert TONE_P == 1024 and TONE_OCR == 77
assert abs(F_SIG - 100.16) < 0.005 and abs(F_NOISE - 976.5625) < 1e-9

# ---------------------------------------------------------------- 元件
VA = 5.0                 # Arduino 5 V（上拉、分压、两路方波的高电平）
VB = 9.0                 # LM393 的电源（9 V 电池）
RS, C1, C2 = 1e3, 4.7e-6, 4.7e-6
RN = 2.2e3
R1, R2, R3 = 10e3, 220e3, 4.7e3
VREF = VA * 10 / 20      # 10k/10k 分压
VOL = 0.065              # LM393 吸 1 mA 时的输出低电平（spice/36 的 SPICE 结果，见 review/spice/36.md）
CM_MAX_25C = VB - 1.5    # LM393 共模上限（数据手册：25 °C 为 VCC−1.5 V，全温度范围 VCC−2 V）
CM_MAX_FULL = VB - 2.0
PIN_MAX = VA + 0.5       # ATmega328P 任意引脚绝对最大值 VCC+0.5 V


def thresholds(r1=R1, r2=R2, r3=R3, vref=VREF, vol=VOL, vpull=VA):
    """理想信号源（内阻 0）时的上门限 VH、下门限 VL 和输出高电平 VOH（含 R3 与 R2 的分压）。"""
    b = 1 / r1 + 1 / r2
    vh = r1 * (vref * b - vol / r2)
    voh = (vpull / r3 + vref / r2) / (1 / r3 + 1 / r2)
    vl = r1 * (vref * b - voh / r2)
    return vh, vl, voh


VH, VL, VOH = thresholds()
DV = VH - VL
VH_SIMPLE = VREF * (R1 + R2) / R2                 # 10 节的简化式（VOL≈0、VOH≈VCC）
VL_SIMPLE = (VREF * (R1 + R2) - VA * R1) / R2
assert abs(VH - 2.6107) < 1e-3 and abs(VL - 2.3887) < 1e-3 and abs(DV - 0.2220) < 1e-3
assert abs(VOH - 4.948) < 1e-3
assert abs(VH_SIMPLE - 2.6136) < 1e-3 and abs(VL_SIMPLE - 2.3864) < 1e-3
assert abs((VH + VL) / 2 - VREF) < 0.003          # 两门限以 2.5 V 为中心（差约 2 mV）

# ---------------------------------------------------------------- 时域仿真（显式欧拉，步长 1 µs）


def simulate(r2=R2, rn=None, rs=None, c=None, t_end=1.1, t_cnt=0.1, dt=1e-6, sig=True, noise=True, keep=None, fsig=None, times=None):
    """返回 (上升沿个数（t_cnt 之后）, n2 峰峰值, 记录的波形 dict 或 None)。
    r2=None 表示拔掉回差电阻（普通比较器）；noise=False 表示 D5 不接（干扰源换成 2.5 V 直流，等于只去掉交流部分）。
    keep=(t0, t1)：记录这段时间的 t、vs、v2、vout。times：传入一个 list，记下每个上升沿的时刻（Timer1 捕获）。"""
    fs_ = F_SIG if fsig is None else fsig
    rn = RN if rn is None else rn
    rs = RS if rs is None else rs
    c1 = C1 if c is None else c
    c2 = C2 if c is None else c
    v1 = v2 = 2.5
    high = False
    edges = 0
    vmax, vmin = -1e9, 1e9
    rec = dict(t=[], v2=[], vo=[], vp=[]) if keep else None
    n = int(round(t_end / dt))
    g1 = 1 / R1
    if r2 is not None:
        g2 = 1 / r2
        a = 1 / R3 + g2
        b = g1 + g2
        det = a * b - g2 * g2
    for i in range(n):
        t = i * dt
        vs = (VA if (t * fs_) % 1.0 < 0.5 else 0.0) if sig else 2.5
        vn = (VA if (t * F_NOISE) % 1.0 < 0.5 else 0.0) if noise else 2.5
        if r2 is None:
            vp, ip, vo = v2, 0.0, (VA if high else VOL)
        else:
            if high:
                vo = (VA / R3 * b + g2 * v2 * g1) / det
                vp = (a * v2 * g1 + g2 * VA / R3) / det
            else:
                vo = VOL
                vp = (v2 * g1 + vo * g2) / b
            ip = (vp - v2) * g1
        i1 = (vs - v1) / rs - (v1 - v2) / rs
        i2 = (v1 - v2) / rs + (vn - v2) / rn + ip
        v1 += i1 * dt / c1
        v2 += i2 * dt / c2
        nh = vp > VREF
        if nh and not high and t >= t_cnt:
            edges += 1
            if times is not None:
                times.append(t)
        high = nh
        if t >= t_cnt:
            vmax = max(vmax, v2); vmin = min(vmin, v2)
        if keep and keep[0] <= t <= keep[1] and i % 5 == 0:
            rec["t"].append(t); rec["v2"].append(v2); rec["vo"].append(vo); rec["vp"].append(vp)
    return edges, vmax - vmin, rec


R2_SWEEP = (47e3, 56e3, 68e3, 82e3, 100e3, 150e3, 220e3, 330e3, 470e3, 680e3, 1e6)
RN_SET = (2.2e3, 1e3, 470)       # 干扰注入电阻：越小干扰越强


def amplitudes(rn=RN):
    """n2 上信号、干扰各自的峰峰值（不接 R2；叠加原理：一次只开一路）。"""
    _, pp_sig, _ = simulate(r2=None, rn=rn, noise=False, t_end=0.3)
    _, pp_noise, _ = simulate(r2=None, rn=rn, sig=False, t_end=0.3)
    return pp_sig, pp_noise


def sweep(rn=RN, r2s=R2_SWEEP):
    """返回 [(R2, 回差 ΔV, 1 s 计数)]。"""
    out = []
    for r2 in r2s:
        vh, vl, _ = thresholds(r2=r2)
        out.append((r2, vh - vl, simulate(r2=r2, rn=rn)[0]))
    return out


def ideal_count(f=F_SIG, t=1.0):
    return f * t


# ---------------------------------------------------------------- 计数误差
TIMEBASE = 5e-3          # Uno R3 的 16 MHz 陶瓷谐振器 CSTCE16M0V53-R0：初始误差 ±0.5 % max（Murata 规格表，见 page2 参考资料）


def gate_err(f, tg=1.0):
    """门控计数：±1 个脉冲 → 相对误差 1/(f·Tg)。"""
    return 1 / (f * tg)


def recip_err(f, fclk=F_CPU / 8):
    """倒数计数（测一个周期）：±1 个时钟 → 相对误差 f/fclk。"""
    return f / fclk


def timer1_counts(f, presc):
    return F_CPU / presc / f


def timer1_fmin(presc):
    return F_CPU / presc / 65536


def gpm(f, k):
    """涡轮流量计：Q（加仑/分钟）= f·60/K，K 为每加仑脉冲数（Omega 资料）。"""
    return f * 60 / k


def gate_probs(f, tg=1.0):
    """1 s 门控时读数是 floor(f·Tg) 还是 +1：两者的概率（门的起点相对脉冲随机）。"""
    x = f * tg
    lo = math.floor(x)
    return lo, 1 - (x - lo), lo + 1, x - lo


def main():
    print(f"[数值] tone(7, 100)：Timer2 预分频 {TONE_P}、OCR2A = {TONE_OCR} → 实际 {F_SIG:.3f} Hz")
    print(f"[数值] analogWrite(5, 128)：16 MHz/64/256 = {F_NOISE:.4f} Hz")
    print(f"[数值] 门限（理想源）：VH = {VH:.4f} V，VL = {VL:.4f} V，回差 {DV*1000:.1f} mV，VOH = {VOH:.3f} V；"
          f"10 节简化式 {VH_SIMPLE:.4f} / {VL_SIMPLE:.4f} V；中心 {(VH+VL)/2:.4f} V")
    print(f"[数值] 共模上限：VB = {VB} V 时 25 °C {CM_MAX_25C} V、全温度 {CM_MAX_FULL} V；5 V 供电时 3.5 / 3.0 V")
    print(f"[数值] Arduino 引脚上限 {PIN_MAX} V；上拉到 9 V 时输出高 ≈ 9 V，超出 {9 - PIN_MAX:.1f} V；上拉到 12 V 超出 {12 - PIN_MAX:.1f} V")
    assert 3.0 < CM_MAX_FULL + 0 and VH < 3.0          # 9 V 供电时 2.6 V 的输入远低于 7 V

    # 干扰与信号各自的峰峰值
    pp_sig, pp_noise = amplitudes()
    _, pp_all, _ = simulate(r2=None, t_end=0.3)
    print(f"[数值] n2 峰峰值（Rn = 2.2k）：只有信号 {pp_sig:.3f} V，只有干扰 {pp_noise*1000:.1f} mV，两者叠加 {pp_all:.3f} V")
    assert 0.53 < pp_sig < 0.55 and 0.12 < pp_noise < 0.13 and 0.64 < pp_all < 0.68

    e_none = simulate(r2=None)[0]
    e_clean = simulate(r2=None, noise=False)[0]
    print(f"[数值] 1 s 内上升沿：不接 R2、有干扰 → {e_none} 个（应为 {ideal_count():.2f}），多数了 {e_none/ideal_count():.2f} 倍；"
          f"不接 R2、没有干扰 → {e_clean} 个")
    assert 150 < e_none < 200 and e_clean in (100, 101)
    res = {r2: (dv, e) for r2, dv, e in sweep()}
    for r2, (dv, e) in res.items():
        print(f"[数值] Rn = 2.2k，R2 = {r2/1e3:>4.0f}k：回差 {dv*1000:6.1f} mV → 1 s 计 {e} 个")
    good = [r2 for r2, (dv, e) in res.items() if e in (100, 101)]
    print(f"[数值] 计数正确的 R2：{good[0]/1e3:.0f}k–{good[-1]/1e3:.0f}k，回差 {res[good[-1]][0]*1000:.0f}–{res[good[0]][0]*1000:.0f} mV"
          f"（干扰峰峰值 {pp_noise*1000:.0f} mV，总峰峰值 {pp_all*1000:.0f} mV）")
    assert good == [82e3, 100e3, 150e3, 220e3, 330e3, 470e3, 680e3, 1e6]
    assert res[47e3][1] == 0
    off = {r2: simulate(r2=r2, rn=1e12, noise=False)[0] for r2 in R2_SWEEP}
    ok_off = [r2 for r2, e in off.items() if e in (100, 101)]
    print(f"[数值] 拔掉干扰（Rn 断开）时计数正确的 R2：{ok_off[0]/1e3:.0f}k 以上（100k 时 {off[100e3]} 个）；"
          f"只有信号时 n2 峰峰值 {simulate(r2=None, rn=1e12, noise=False, t_end=0.3)[1]:.3f} V")
    assert ok_off == [150e3, 220e3, 330e3, 470e3, 680e3, 1e6]
    rn1 = {r2: simulate(r2=r2, rn=1e3)[0] for r2 in (220e3, 330e3)}
    rn470 = {r2: simulate(r2=r2, rn=470)[0] for r2 in (68e3, 220e3)}
    print(f"[数值] Rn = 1k（干扰 275 mV）：R2 = 220k 计 {rn1[220e3]}，330k 计 {rn1[330e3]}；"
          f"Rn = 470（干扰 579 mV）：R2 = 220k 计 {rn470[220e3]}，68k 计 {rn470[68e3]}")
    assert rn1[220e3] == 100 and rn1[330e3] > 150 and rn470[220e3] > 500 and rn470[68e3] == 100
    print(f"[数值] R2 = 220k：回差 {DV*1000:.0f} mV 是干扰峰峰值的 {DV/pp_noise:.2f} 倍、只有信号时峰峰值的 {DV/pp_sig:.2f} 倍")

    # 信号源内阻：把整个网络换成 10k / 470 nF（波形几乎一样），R1、R2 的回差电流把 n2 拉偏
    e10 = simulate(rs=10e3, c=470e-9, rn=1e12, noise=False)[0]
    e1 = simulate(rn=1e12, noise=False)[0]
    shift10 = (VREF - VOL) / (R1 + R2) * 20e3
    shift1 = (VREF - VOL) / (R1 + R2) * 2e3
    print(f"[数值] 去掉干扰（Rn 断开）、R2 = 220k：1k/4.7 µF 网络计 {e1} 个；10k/470 nF 网络计 {e10} 个。"
          f"回差电流 {(VREF-VOL)/(R1+R2)*1e6:.1f} µA 流过 20 kΩ 把 n2 拉偏 {shift10*1000:.0f} mV，流过 2 kΩ 只拉偏 {shift1*1000:.0f} mV")
    assert e1 in (100, 101) and e10 == 0

    # 门控 vs 倒数计数
    for f in (1, 10, 100, 1000, 10000):
        print(f"[数值] f = {f:>5} Hz：1 s 门控 ±{gate_err(f)*100:.4g} %，倒数计数（2 MHz）±{recip_err(f)*100:.4g} %")
    assert abs(gate_err(100) - 0.01) < 1e-12 and abs(recip_err(100) - 50e-6) < 1e-12
    fx = math.sqrt(F_CPU / 8 / 1.0)
    print(f"[数值] 两条误差线交点 {fx:.0f} Hz（误差 {gate_err(fx)*100:.3f} %）；倒数计数误差低于时基 ±{TIMEBASE*100:g} % 的上限频率 {TIMEBASE*F_CPU/8:.0f} Hz；"
          f"门控误差低于 ±{TIMEBASE*100:g} % 需 f > {1/TIMEBASE:.0f} Hz")
    assert TIMEBASE * F_CPU / 8 == 10000 and abs(1 / TIMEBASE - 200) < 1e-9
    assert abs(fx - 1414.2) < 0.1

    # Timer1
    for p in (1, 8, 64):
        print(f"[数值] Timer1 ÷{p}：100 Hz 一个周期 {timer1_counts(100, p):.0f} 个计数；"
              f"不溢出的最低频率 {timer1_fmin(p):.2f} Hz；一个计数 {p/F_CPU*1e6:.4g} µs")
    assert timer1_counts(100, 1) > 65535 and timer1_counts(100, 8) == 20000
    assert abs(timer1_fmin(1) - 244.14) < 0.01 and abs(timer1_fmin(8) - 30.52) < 0.01
    print(f"[数值] 100.16 Hz、÷8：{timer1_counts(F_SIG, 8):.1f} 个计数 → 读数整数 {round(timer1_counts(F_SIG, 8))} "
          f"→ {F_CPU/8/round(timer1_counts(F_SIG, 8)):.3f} Hz")
    assert round(timer1_counts(F_SIG, 8)) == 19968

    lo, plo, hi, phi = gate_probs(F_SIG)
    print(f"[数值] 1 s 门控读 100.16 Hz：读 {lo} 的概率 {plo*100:.0f} %，读 {hi} 的概率 {phi*100:.0f} %")
    assert lo == 100 and abs(phi - 0.16) < 0.001

    # K 系数
    print(f"[数值] K = 100、500 Hz → {gpm(500, 100):.0f} GPM = {gpm(500, 100)*3.785:.1f} L/min；"
          f"本实验 {F_SIG:.2f} Hz 冒充 K = 100 的流量计 → {gpm(F_SIG, 100):.2f} GPM；1000 个脉冲 = {1000/100:.0f} 加仑")
    assert gpm(500, 100) == 300
    print(f"[数值] CHANGE 模式每周期 2 次中断：1 s 读 {2*F_SIG:.1f}；零流量超时 2 s → 最低可报 {1/2:.1f} Hz")
    extras()
    return res


def extras():
    """页面例题、练习、预测题用到的其余数字。"""
    dv_s = VH_SIMPLE - VL_SIMPLE
    print(f"[数值] 简化式回差 VA·R1/R2 = {dv_s*1000:.1f} mV（精确 {DV*1000:.1f} mV）；信号周期 {1e3/F_SIG:.3f} ms")
    assert abs(dv_s - VA * R1 / R2) < 1e-12 and abs(dv_s - 0.2273) < 1e-4
    # 例 1：R2 = 150k
    vh, vl, _ = thresholds(r2=150e3)
    vhs, vls = VREF * (R1 + 150e3) / 150e3, (VREF * (R1 + 150e3) - VA * R1) / 150e3
    print(f"[数值] 例 1 R2 = 150k：简化 {vhs:.4f} / {vls:.4f} V（回差 {(vhs-vls)*1000:.1f} mV）；精确 {vh:.4f} / {vl:.4f} V（回差 {(vh-vl)*1000:.1f} mV）")
    assert abs(vh - 2.6623) < 1e-3 and abs(vl - 2.3384) < 1e-3 and abs(vhs - 2.6667) < 1e-3
    # 例 2：K 系数（脉冲/升）
    lpm = 60 * 60 / 450
    print(f"[数值] 例 2 变体：K = 450 个/升、f = 60 Hz → {lpm:.1f} L/min；1 分钟 {60*60} 个脉冲")
    assert lpm == 8.0
    # 例 3：10 Hz 测周期
    print(f"[数值] 例 3：10 Hz ÷8 → {timer1_counts(10, 8):.0f} 个计数（超过 65535）；÷64 → {timer1_counts(10, 64):.0f} 个，"
          f"±1 个计数 = {100/timer1_counts(10, 64):.4f} %；1 s 门控 ±{gate_err(10)*100:.0f} %")
    assert timer1_counts(10, 8) > 65535 and timer1_counts(10, 64) == 25000
    # 练习 3：1 Hz
    print(f"[数值] 练习 3：1 Hz ÷64 → {timer1_counts(1, 64):.0f}（溢出）；÷256 → {timer1_counts(1, 256):.0f} 个，"
          f"±{100/timer1_counts(1, 256):.4f} %；÷256 最低 {timer1_fmin(256):.3f} Hz")
    assert timer1_counts(1, 256) == 62500 and timer1_fmin(256) < 1
    # 练习 5：风扇
    rpm = 350 / 7 * 60
    print(f"[数值] 练习 5：7 片扇叶、350 Hz → {rpm:.0f} 转/分")
    assert rpm == 3000
    # 输入最高电压与共模余量
    _, _, r = simulate(t_end=0.131, keep=(0.1, 0.13))
    vmax = max(max(r["vp"]), max(r["v2"]))
    print(f"[数值] 实验电路比较器输入最高 {vmax:.2f} V；9 V 供电共模上限（全温度）{CM_MAX_FULL} V，余量 {CM_MAX_FULL - vmax:.1f} V；"
          f"5 V 供电上限 3.0 V，余量只有 {3.0 - vmax:.2f} V")
    assert vmax < 3.0
    v2m = sum(r["v2"]) / len(r["v2"])
    print(f"[数值] n2（① 第 11 列）平均值 {v2m:.3f} V；读错 175 个时的流量 {F_SIG*60/100*1.75:.1f} GPM（真值 {F_SIG*60/100:.2f}）")
    assert abs(v2m - 2.5) < 0.05
    fc = 1 / (2 * math.pi * 1e3 * 4.7e-6)
    print(f"[数值] 每级 RC（1k、4.7 µF）转折频率 {fc:.1f} Hz")
    assert abs(fc - 33.9) < 0.05
    # 回差与信号、干扰的关系（page3 窗口）
    print(f"[数值] 回差窗口（Rn = 2.2k）：下限要大于 0（单门限 175 个），上限约在 585–702 mV 之间（信号+干扰峰峰值 663 mV）")
    teacher_fix()


def teacher_fix():
    """首审修改新增的数字（page3 有效回差、练习、page4 周期抖动等）。"""
    dvo = VOH - VOL
    # 有效回差：源内阻 Rs 和 R1 串联，回差 ≈ VA·(R1 + Rs)/R2
    def eff(r2, rs):
        return dvo * (R1 + rs) / r2
    e100, e220_1k, e220_10k = eff(100e3, 2e3), eff(220e3, 2e3), eff(220e3, 20e3)
    _, pp_off, _ = simulate(r2=None, rn=1e12, noise=False, t_end=0.3)
    print(f"[数值] 有效回差 VA(R1+Rs)/R2（VA = VOH−VOL = {dvo:.3f} V）：R2 100k、Rs 2k → {e100:.3f} V，"
          f"拔掉 Rn 时信号峰峰值 {pp_off:.3f} V，回差反而大了 {(e100 - pp_off)*1000:.0f} mV（约 {(e100 - pp_off)/e100*100:.0f} %）；"
          f"R2 150k → {eff(150e3, 2e3):.3f} V；"
          f"R2 220k：1k 网络 {e220_1k:.3f} V，10k 网络 {e220_10k:.3f} V")
    assert abs(e100 - 0.586) < 0.002 and abs(e220_1k - 0.266) < 0.002 and abs(e220_10k - 0.666) < 0.002
    assert e100 > pp_off and (e100 - pp_off) / e100 < 0.06
    # 经验式：回差 / 只有信号时的峰峰值
    print(f"[数值] 回差 {DV*1000:.0f} mV 是只有信号（拔掉 Rn）峰峰值 {pp_off*1000:.0f} mV 的 {DV/pp_off:.2f} 倍")
    assert abs(DV / pp_off - 0.40) < 0.005
    # 10k/470n 网络带着 Rn 2.2k
    e10n, _, _ = simulate(rs=10e3, c=470e-9)
    _, pn10, _ = simulate(r2=None, rs=10e3, c=470e-9, sig=False, t_end=0.3)
    print(f"[数值] 10k/470n 网络插着 Rn 2.2k：干扰峰峰值 {pn10:.2f} V，1 s 数到 {e10n} 个")
    assert e10n == 976 and abs(pn10 - 1.21) < 0.02
    # 练习 1：Rn = 680
    _, pn680 = amplitudes(680)
    sw680 = {r2: e for r2, _, e in sweep(rn=680)}
    print(f"[数值] 练习 1 Rn = 680 Ω：干扰峰峰值 {pn680*1000:.0f} mV；R2 扫描 " + "、".join(f"{r2/1e3:.0f}k→{e}" for r2, e in sw680.items()))
    assert sw680[220e3] > 101 and sw680[100e3] == 100 and sw680[68e3] == 100 and sw680[56e3] == 0 and sw680[330e3] > 101
    assert abs(pn680 - 0.403) < 0.005
    # 变体 1：Rn = 1.5k
    _, pn15 = amplitudes(1.5e3)
    sw15 = {r2: e for r2, _, e in sweep(rn=1.5e3)}
    ok15 = [r2 for r2, e in sw15.items() if e in (100, 101)]
    print(f"[数值] 变体 1 Rn = 1.5k：干扰峰峰值 {pn15*1000:.0f} mV；数对的 R2：" + "、".join(f"{r2/1e3:.0f}k" for r2 in ok15)
          + f"；680k → {sw15[680e3]}，68k → {sw15[68e3]}")
    assert ok15 == [82e3, 100e3, 150e3, 220e3, 330e3, 470e3] and abs(pn15 - 0.184) < 0.005
    print(f"[数值] 变体 1 经验式：1.5～2 倍干扰 = {1.5*pn15:.2f}～{2*pn15:.2f} V；信号一半 = {pp_off/2:.2f} V；"
          f"练习 1：100k 回差 / 680 Ω 干扰 = {(thresholds(r2=100e3)[0] - thresholds(r2=100e3)[1])/pn680:.1f} 倍")
    assert abs(1.5 * pn15 - 0.28) < 0.005 and abs(2 * pn15 - 0.37) < 0.005 and abs(pp_off / 2 - 0.28) < 0.005
    # 正文：Rn = 470 时 56k–82k 都数对
    sw470 = {r2: e for r2, _, e in sweep(rn=470)}
    print(f"[数值] Rn = 470 Ω：56k→{sw470[56e3]}、68k→{sw470[68e3]}、82k→{sw470[82e3]}、100k→{sw470[100e3]}、47k→{sw470[47e3]}")
    print("[数值] 回差：" + "、".join(f"{int(r/1e3)}k {(thresholds(r2=r)[0]-thresholds(r2=r)[1])*1e3:.0f} mV" for r in (47e3, 56e3, 68e3, 82e3, 100e3, 150e3, 330e3)))
    assert sw470[56e3] == sw470[68e3] == sw470[82e3] == 100 and sw470[47e3] == 0 and sw470[100e3] > 101
    # 练习 4（新）：÷64 却按 2 MHz 换算
    n64 = round(timer1_counts(F_SIG, 64))
    f_bad = 2e6 / n64
    print(f"[数值] 练习 4：÷64 时一个周期 {n64} 个计数，误按 2 MHz 换算 → {f_bad:.1f} Hz（真值 {F_SIG:.2f} Hz 的 {f_bad/F_SIG:.0f} 倍）")
    assert n64 == 2496 and abs(f_bad - 801.3) < 0.1
    # 分频表补 ÷256、÷1024
    for div in (256, 1024):
        print(f"[数值] Timer1 ÷{div}：一个滴答 {div/16:.0f} µs，100 Hz 一个周期 {timer1_counts(100, div):.2f} 个，最低 {timer1_fmin(div):.3f} Hz")
    assert timer1_counts(100, 256) == 625 and abs(timer1_fmin(1024) - 0.238) < 0.001
    # page2：为什么用比较器而不用运放（数据手册典型值）
    t393, sr358 = 1.3e-6, 0.3e6
    t358 = VOH / sr358
    print(f"[数值] LM393 响应时间 {t393*1e6:.1f} µs；LM358 压摆率 {sr358/1e6:.1f} V/µs，摆 {VOH:.2f} V 要 {t358*1e6:.1f} µs")
    assert 10e-6 < t358 < 20e-6
    # page4 安全须知：R3 错接 9 V 时，D8 被内部保护二极管钳在约 VCC + 0.5 V，电流倒灌进 5 V
    i_back = (9.0 - 5.5) / R3
    print(f"[数值] R3 错接 9 V：D8 被钳在约 5.5 V，经 R3 倒灌约 {i_back*1e3:.2f} mA 进 5 V 轨")
    assert abs(i_back - 0.74e-3) < 0.01e-3
    # page4 想一想 1：干扰与信号的频率比
    ratio = F_NOISE / F_SIG
    print(f"[数值] 干扰 / 信号频率比 {ratio:.4f}（≈ 9.75 = 39/4：每 4 个信号周期图样重复一次）")
    assert abs(ratio - 9.75) < 0.002
    # page4：带着 Rn 时单个周期的捕获值会跳；1 s 平均很稳
    for rn, tag in ((None, "插着 Rn"), (1e12, "拔掉 Rn")):
        T = []
        simulate(rn=rn, noise=rn is None, times=T)
        k = [round(t * 2e6) for t in T]
        d = [b - a for a, b in zip(k, k[1:])]
        avg = (k[-1] - k[0]) / (len(k) - 1)
        print(f"[数值] page4 {tag}、R2 220k：单个周期 {min(d)}～{max(d)} 个滴答，1 s 平均 {avg:.1f}（{2e6/avg:.3f} Hz）")
        if rn is None:
            assert min(d) < 19100 and max(d) > 20200 and abs(avg - 19968) < 10 and sum(d[:4]) in range(79860, 79890)
        else:
            assert 19960 <= min(d) and max(d) <= 19976 and abs(avg - 19968) < 2


if __name__ == "__main__":
    main()
