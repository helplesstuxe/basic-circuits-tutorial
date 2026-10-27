#!/usr/bin/env python3
"""38 同步检波（电磁流量计）：页面上所有数字的来源。从仓库根目录运行：python code/38_sim.py
只打印，不写文件。各节编号与页面引用一致（例如「code/38_sim.py 第 3 节」）。"""
import numpy as np

VCC, VMID, VIO = 9.0, 4.5, 5.0          # 模拟板 9 V 电池；中点参考 V_MID；Arduino 引脚高电平
G = 21.0                                # 沿用 30 节：RG = 1 kΩ，G = 1 + 2×10k/1k
F_CPU = 16_000_000


def par(*rs):
    return 1.0 / sum(1.0 / r for r in rs)


# ---------------------------------------------------------------- 1. 模拟电极（测试夹具）
# 节点 P（INA 的 + 输入）：RS1 1 MΩ 接 D9，RS2 1 kΩ 接 V_MID，RN 100 kΩ 接 D5（50 Hz 干扰），
# （RN 前面串 CN 10 µF 隔直），RD 100 kΩ 接 10 kΩ 电位器 RP 的滑动端（模拟电极之间的直流）。INA 的 − 输入直接接 V_MID。
RS1, RS2, RN, RD, RPOT = 1e6, 1e3, 100e3, 100e3, 10e3


def node_p(v_d9, d5_ac, wiper_frac):
    """节点 P 对 V_MID 的电压（V）。d5_ac：D5 方波减去它自己的平均值（±2.5 V 或 0）——
    RN 前面串了 CN 10 µF，直流过不去，只有交流部分进来。wiper_frac：电位器滑动端位置，0 = 0 V 端，1 = 9 V 端。"""
    vw = VCC * wiper_frac
    rw = RPOT * wiper_frac * (1 - wiper_frac)          # 电位器滑动端的戴维南内阻
    g = 1 / RS1 + 1 / RS2 + 1 / RN + 1 / (RD + rw)
    gdc = 1 / RS1 + 1 / RS2 + 1 / (RD + rw)             # 直流时 CN 断开
    vdc = (2.5 / RS1 + VMID / RS2 + vw / (RD + rw)) / gdc   # D9 平均 2.5 V
    return vdc + (v_d9 - 2.5) / RS1 / g + d5_ac / RN / g - VMID


print("== 1. 测试夹具（电位器居中，D5 不发声）==")
hi, lo = node_p(VIO, 0, 0.5), node_p(0, 0, 0.5)
E = (hi - lo) / 2
print(f"D9 高：P−V_MID = {hi*1e3:+.4f} mV；D9 低：{lo*1e3:+.4f} mV；峰峰 {2*E*1e3:.4f} mV，E = {E*1e3:.4f} mV，"
      f"直流部分 {(hi+lo)/2*1e3:+.4f} mV")
print(f"只接 RS1、RS2 时：E = {VIO/2*RS2/(RS1+RS2)*1e3:.4f} mV（RN、RD 并在 RS2 上，让它小 {(1-E/(VIO/2*RS2/(RS1+RS2)))*100:.2f}%）")
for w in (0.0, 1.0):
    print(f"电位器拧到 {'0 V' if w == 0 else '9 V'} 端：直流部分 {(node_p(VIO,0,w)+node_p(0,0,w))/2*1e3:+.2f} mV，"
          f"E = {(node_p(VIO,0,w)-node_p(0,0,w))/2*1e3:.4f} mV")
e5 = (node_p(0, 2.5, 0.5) - node_p(0, 0, 0.5))
print(f"D5 的 50 Hz 方波在 P 点：±{e5*1e3:.4f} mV（是信号的 {e5/E:.1f} 倍）")
EMID = E

def node_p_static(v_d9, wiper_frac=0.5):
    """D9 停在高或低（串口命令 h / l）几秒以后：CN 充满、相当于断开，RN 不起作用。"""
    vw = VCC * wiper_frac; rw = RPOT * wiper_frac * (1 - wiper_frac)
    gdc = 1 / RS1 + 1 / RS2 + 1 / (RD + rw)
    return (v_d9 / RS1 + VMID / RS2 + vw / (RD + rw)) / gdc - VMID
shi, slo = node_p_static(VIO), node_p_static(0)
print(f"静态（D9 停住，CN 断开）：P−V_MID 高 {shi*1e3:+.4f} mV、低 {slo*1e3:+.4f} mV，差 {(shi-slo)*1e3:.4f} mV；"
      f"×21 后 INA 输出对 V_MID：高 {G*shi*1e3:+.2f} mV、低 {G*slo*1e3:+.2f} mV，差 {G*(shi-slo)*1e3:.2f} mV（另加 INA 自己的失调，相减后消掉）")

print("\n== 2. INA 输出余量（G = 21）==")
dcmax = max(abs((node_p(VIO, 0, w) + node_p(0, 0, w)) / 2) for w in (0.0, 1.0))
vo_hi = G * (dcmax + EMID + e5)
print(f"最坏：直流 {dcmax*1e3:.2f} mV + 信号 {EMID*1e3:.3f} mV + 干扰 {e5*1e3:.3f} mV，×21 = {vo_hi:.3f} V（对 V_MID）")
print(f"LM358 9 V 单电源输出上限约 V+ − 1.5 V = 7.5 V，对 V_MID 只剩 +3.0 V；允许的差模直流 ≤ {3.0/G*1e3:.0f} mV")
print(f"错误示范：差模直流 1 V × 21 = 21 V，远超 3 V 余量；就算 G = 10 也是 10 V")
print(f"A0 分压 10k/10k：INA 输出 0～9 V 对应 A0 0～4.5 V；V_MID 4.5 V → A0 2.25 V")

print("\n== 3. tone() 实际频率（Tone.cpp 的整数算法，Timer2 预分频 1024）==")
def tone_f(f):
    for pre in (1, 8, 32, 64, 128, 256, 1024):
        ocr = F_CPU // f // 2 // pre - 1
        if ocr <= 255:
            return F_CPU / (2 * pre * (ocr + 1)), pre, ocr
for f in (50, 51):
    fa, pre, ocr = tone_f(f)
    print(f"tone({f})：预分频 {pre}，OCR2A = {ocr}，实际 {fa:.4f} Hz")
F50, F51 = tone_f(50)[0], tone_f(51)[0]
TOP, PRE1 = 4999, 256
FEXC = F_CPU / PRE1 / (TOP + 1) / 2
print(f"Timer1：预分频 {PRE1}，TOP = {TOP}，D9 翻转一次 = {(TOP+1)*PRE1/F_CPU*1e3:.1f} ms，励磁 {FEXC:.4f} Hz，"
      f"1 个计数 = {180/(TOP+1):.3f}°")
for ph in (45, 90):
    k = round(ph / (180 / (TOP + 1)))
    print(f"相位 {ph}°：D10 比 D9 早 {k} 个计数，OCR1B = {TOP - k}")

print("\n== 4. 方波参考 × 方波信号：相位定律 ==")
def demod_avg(phi_deg, n=200000):
    t = (np.arange(n) + 0.5) / n                          # 一个周期
    s = np.sign(np.sin(2 * np.pi * t))
    r = np.sign(np.sin(2 * np.pi * t + np.radians(phi_deg)))
    return np.mean(s * r)
for ph in (0, 30, 45, 60, 90, 135, 180):
    print(f"φ = {ph:3d}°：平均 = {demod_avg(ph):+.4f}，三角形定律 1 − 2φ/π（0～180°）= {1 - 2*ph/180:+.4f}")
print(f"正弦信号 × 方波参考，φ = 0 时平均 = 2/π = {2/np.pi:.4f}（与 09 节 0.637 同一个数）")

print("\n== 5. 50 Hz 落在参考的奇次还是偶次谐波（长时间平均后剩多少）==")
def interf_left(fexc, fint=50.0, T=20.0, n=2_000_000, theta=0.3):
    t = np.linspace(0, T, n, endpoint=False)
    r = np.sign(np.sin(2 * np.pi * fexc * t + 1e-9))
    return np.mean(r * np.sin(2 * np.pi * fint * t + theta))
for name, fe in (("50/8 = 6.25", 6.25), ("50/7 ≈ 7.143", 50 / 7), ("50/6 ≈ 8.333", 50 / 6), ("50/3 ≈ 16.67", 50 / 3), ("5", 5.0)):
    worst = max(abs(interf_left(fe, theta=th)) for th in np.linspace(0, np.pi, 7))
    print(f"励磁 {name:>13} Hz：50 Hz 是第 {50/fe:.2f} 次谐波，长时间平均后最多剩 {worst*100:6.3f}% 的干扰幅度")

print("\n== 6. 数字法（Arduino）：每 1 ms 读一次 A0，按 D10 状态加减 ==")
VREF, LSB = 5.0, 5.0 / 1024


def arduino_run(phi_deg=0.0, tone=None, periods=12, blank=True, flip=False, noise_lsb=0.0, seed=1, t0=0.000137):
    rng = np.random.default_rng(seed)
    T = 1 / FEXC
    res = []
    for p in range(periods):
        t = t0 + p * T + np.arange(160) * 1e-3
        ph_t = (t * FEXC) % 1.0                          # 信号（D9）的相位，0～1
        sig = np.where(ph_t < 0.5, 1.0, -1.0)
        ph_r = (ph_t + phi_deg / 360 + (0.5 if flip else 0)) % 1.0
        ref = np.where(ph_r < 0.5, 1.0, -1.0)
        v = G * EMID * sig
        if tone:
            v = v + G * e5 * np.sign(np.sin(2 * np.pi * tone * t + 0.4))
        a0 = (VMID + v) / 2 + rng.normal(0, noise_lsb * LSB, t.size)
        code = np.clip(np.floor(a0 / LSB), 0, 1023)
        keep = np.ones_like(ph_r, bool)
        if blank:                                          # 每个半周期只要后一半（参考换向 40 ms 以后）
            keep = (ph_r % 0.5) >= 0.25
        sp = code[keep & (ref > 0)].mean(); sm = code[keep & (ref < 0)].mean()
        res.append((sp - sm) / 2 * LSB * 2 / G * 1e3)      # 折算回 P 点，mV
    return np.array(res)

print(f"A0 上的信号幅度 = {G*EMID/2*1e3:.2f} mV = {G*EMID/2/LSB:.2f} LSB（1 LSB = {LSB*1e3:.2f} mV）")
for lab, kw in (("无干扰，无噪声", {}), ("无干扰，噪声 0.5 LSB", dict(noise_lsb=0.5)),
                ("tone(50) 实际 50.08 Hz", dict(tone=F50, noise_lsb=0.5)), ("tone(51) 实际 51.06 Hz", dict(tone=F51, noise_lsb=0.5)),
                ("相位 180°（翻转）", dict(flip=True, noise_lsb=0.5))):
    r = arduino_run(**kw)
    print(f"{lab:<28} 每周期读数 平均 {r.mean():+.3f} mV，最小 {r.min():+.3f}，最大 {r.max():+.3f}（真值 E = {EMID*1e3:.3f} mV）")
r_all = np.array([arduino_run(noise_lsb=0.0, t0=x).mean() for x in np.linspace(0, 1e-3, 21)])
for ph in (0, 45, 90, 135, 180):
    r_b = arduino_run(phi_deg=ph, noise_lsb=0.5); r_n = arduino_run(phi_deg=ph, noise_lsb=0.5, blank=False)
    print(f"数字法 相位 {ph:3d}°：只采后半段 {r_b.mean():+.3f} mV，整段都采 {r_n.mean():+.3f} mV")
print(f"无噪声时，不同采样起点下平均值 {r_all.min():.3f}～{r_all.max():.3f} mV：只靠量化，误差可到 "
      f"{max(abs(r_all-EMID*1e3))/(EMID*1e3)*100:.1f}%")

print("\n== 7. 模拟链：交流耦合 → 跟随 → ±1 → RC → 万用表 ==")
CHP, RHP, R11, R12, RF, CF, RMETER = 10e-6, 100e3, 10e3, 10e3, 100e3, 10e-6, 10e6
print(f"交流耦合 f_c = {1/(2*np.pi*RHP*CHP):.3f} Hz，τ_HP = {RHP*CHP:.1f} s；半周期 80 ms 内方波下垂 {(1-np.exp(-0.08/(RHP*CHP)))*100:.1f}%")
print(f"RC 低通 τ = {RF*CF:.1f} s，f_c = {1/(2*np.pi*RF*CF):.3f} Hz；万用表 10 MΩ 让读数变成 {RMETER/(RMETER+RF):.4f} 倍")


def chain(phi_deg=0.0, tcf=1.0, T=30.0, dt=50e-6, eps=0.0, vdc=0.0, tone=None, ac=True, flip_at=None, tau_hp=1.0):
    """返回 (t, 输出对 V_MID)。理想运放；eps = R2/R1 − 1；vdc：INA 输出上的直流（V，带符号：正 = 高于 V_MID）。
    第 7 节用 +976 mV（最坏情况的绝对值）；第 9 步实际是电位器拧到 0 V 端，vdc = −935 mV，见第 8 节。"""
    n = int(T / dt); t = np.arange(n) * dt
    ph = (t * FEXC) % 1.0
    vin = G * EMID * np.where(ph < 0.5, 1.0, -1.0) + vdc
    if tone:
        vin = vin + G * e5 * np.sign(np.sin(2 * np.pi * tone * t + 0.4))
    phr = (ph + phi_deg / 360) % 1.0
    if flip_at is not None:
        phr = np.where(t >= flip_at, (phr + 0.5) % 1.0, phr)
    ref = np.where(phr < 0.5, 1.0, -1.0)
    y = np.empty(n); hp = 0.0; vc = 0.0; xprev = vin[0]
    a_hp = tau_hp / (tau_hp + dt)
    k = RMETER / (RMETER + RF); tau = RF * CF * k        # 戴维南：表头分压、τ 也略小
    a_lp = dt / tau
    for i in range(n):
        x = vin[i]
        hp = a_hp * (hp + x - xprev) if ac else x; xprev = x
        u = hp if ref[i] > 0 else -(1 + eps) * hp
        vc += (k * u - vc) * a_lp
        y[i] = vc
    return t, y

def tail_stats(t, y, last=2.0):
    m = t >= t[-1] - last
    return y[m].mean(), y[m].max() - y[m].min()

t, y = chain()
ideal = G * EMID
m0, rp = tail_stats(t, y)
print(f"相位 0：稳定后 {m0*1e3:.2f} mV（理想 G·E = {ideal*1e3:.2f} mV，差 {(m0/ideal-1)*100:+.2f}%），纹波峰峰 {rp*1e3:.2f} mV")
for ph in (45, 90, 180):
    t, y = chain(phi_deg=ph); m, _ = tail_stats(t, y)
    print(f"相位 {ph}°：{m*1e3:+.2f} mV（相位 0 的 {m/m0*100:+.1f}%）")
t, y = chain(T=20, flip_at=8.0)
fin = tail_stats(t, y)[0]
i1 = np.argmax((t > 8.0) & (np.abs(y - fin) < 0.01 * abs(fin)) & np.r_[True, True][0])
# 进入 ±1% 后不再出来的时间
bad = np.where((t > 8.0) & (np.abs(y - fin) > 0.01 * abs(fin) + 0.5 * rp))[0]
ts1 = t[bad[-1]] - 8.0 if bad.size else 0.0
t, y = chain(T=80, flip_at=10.0, tcf=10.0)
print(f"翻转 180° 后：τ = 1 s 时约 {ts1:.1f} s 才稳定到 ±1%（理论 τ·ln200 = {np.log(200):.1f} s）")
# τ = 10 s：把 CF 换成 100 µF
CF_save = CF; CF = 100e-6
t, y = chain(T=90, flip_at=10.0)
fin = tail_stats(t, y)[0]; _, rp10 = tail_stats(t, y)
bad = np.where((t > 10.0) & (np.abs(y - fin) > 0.01 * abs(fin) + 0.5 * rp10))[0]
print(f"CF 换 100 µF（τ = 10 s）：纹波 {rp10*1e3:.3f} mV（τ = 1 s 时 {rp*1e3:.2f} mV），稳定要 {t[bad[-1]]-10.0:.0f} s")
CF = CF_save
for lab, f in (("tone 50.08 Hz", F50), ("tone 51.06 Hz", F51)):
    t, y = chain(tone=f, T=20); m, r = tail_stats(t, y, last=6.0)
    print(f"{lab}：平均 {m*1e3:.2f} mV（无干扰 {m0*1e3:.2f}），纹波峰峰 {r*1e3:.2f} mV（T = 20 s、取末 6 s；第 8 节用 T = 30 s、取 10 s 以后，所以峰峰值略有不同）")
vdc = G * dcmax
print(f"\n直流泄漏（INA 输出直流取 +{vdc*1e3:.0f} mV，只看大小；电位器拧到 0 V 端时实际是 −976 mV、泄漏为正，见下面「最坏情况」两行；−1 路电阻失配 ε = 2%）：")
for ac in (False, True):
    t, y = chain(eps=0.02, vdc=vdc, ac=ac, T=12); m, _ = tail_stats(t, y)
    t2, y2 = chain(eps=0.02, vdc=0.0, ac=ac, T=12); m2, _ = tail_stats(t2, y2)
    print(f"  {'有' if ac else '无'}交流耦合：直流引起的读数变化 {(m-m2)*1e3:+.2f} mV（公式 −V_DC·ε/2 = {-vdc*0.02/2*1e3:.2f} mV，V_DC 是 INA 输出上的直流 {vdc*1e3:.0f} mV）")
print(f"占空比偏 δ = 1% 时的泄漏（公式 2δ·V_DC）= {2*0.01*vdc*1e3:.2f} mV")
print(f"U3B 失调最大 7 mV，两种状态下都被放大 1 + R12/R11 = 2 倍，在 RC 上变成最多 {2*7:.0f} mV 的固定偏移（U3A 的失调在交流耦合之后，会被 ±1 平均掉），用「翻转相减」(V0 − V180)/2 消掉")
print(f"CD4053 导通电阻 r_ON（VDD = 10 V 时典型 180 Ω、最大 400 Ω）只串在 U3B 同相端，同相端几乎没有电流，压降 ≈ 0")

print("\n== 8. 补充核算：直流泄漏的符号、50 Hz 纹波到底从哪来、avg8 的真实行为 ==")
# (a) 第 9 步：电位器从「D 对 B ≈ 0」（滑动端 4.5 V）拧到 0 V 端，P 点直流变化多少、仪放输出直流变化多少
def p_dc(w):
    return (node_p(VIO, 0, w) + node_p(0, 0, w)) / 2
dP = p_dc(0.0) - p_dc(0.5)
vdc9 = G * dP
t, y = chain(eps=0.02, vdc=vdc9, ac=False, T=12); m, _ = tail_stats(t, y)
t2, y2 = chain(eps=0.02, vdc=0.0, ac=False, T=12); m2, _ = tail_stats(t2, y2)
print(f"第 9 步：P 点直流变化 {dP*1e3:+.2f} mV，仪放输出直流变化 {vdc9*1e3:+.0f} mV；"
      f"ε = 2% 泄漏公式 −V_DC·ε/2 = {-vdc9*0.02/2*1e3:+.2f} mV，含万用表 0.9901 倍 = {-vdc9*0.02/2*1e3*RMETER/(RMETER+RF):+.2f} mV，"
      f"模拟（无交流耦合）{(m-m2)*1e3:+.2f} mV")
for lab, w in (("0 V 端", 0.0), ("9 V 端", 1.0)):   # 两头不对称，与 page3 第 35 行一致
    v = G * p_dc(w)
    print(f"最坏情况（电位器拧到{lab}）：P 点直流 {p_dc(w)*1e3:+.2f} mV，仪放输出直流 {v*1e3:+.0f} mV，泄漏 {-v*0.02/2*1e3:+.2f} mV")

# (b) 50 Hz 纹波：CF 上的瞬时纹波、万用表（按 0.1 s 积分一次）看到的跳动、按一个励磁周期滑动平均后剩下的慢晃
def mov(y, n):
    c = np.cumsum(np.r_[0.0, y]); return (c[n:] - c[:-n]) / n
dt = 50e-6
for lab, f in (("恰好 50.00 Hz", 50.0), ("tone 50.08 Hz", F50), ("tone 51.06 Hz", F51)):
    t, y = chain(tone=f, T=30, dt=dt)
    keep = t >= 10.0
    yy = y[keep]
    inst = yy.max() - yy.min()
    mp = []
    for win in (0.1, 0.2):
        nm = int(win / dt); meter = yy[: (yy.size // nm) * nm].reshape(-1, nm).mean(axis=1)
        mp.append((meter.max() - meter.min()) * 1e3)
    slow = mov(yy, int(round(1 / FEXC / dt)))
    print(f"{lab}：平均 {yy.mean()*1e3:.2f} mV；CF 上瞬时纹波峰峰 {inst*1e3:.2f} mV；"
          f"万用表读数跳动峰峰（0.1 s / 0.2 s 一读）{mp[0]:.2f} / {mp[1]:.2f} mV；按 160 ms 滑动平均后的慢晃峰峰 {(slow.max()-slow.min())*1e3:.2f} mV")
# 6.25 Hz 分量被 RC（τ = 1 s）衰减多少
tau_k = RF * CF * RMETER / (RMETER + RF)
print(f"τ = {tau_k:.3f} s 的 RC 对 6.25 Hz 衰减 {np.hypot(1, 2*np.pi*FEXC*tau_k):.1f} 倍")

# (c) avg8：nAvg 封顶 8 的递推 avg8 += (eP − avg8)/nAvg
def avg8_run(seq):
    a, n, out = 0.0, 0, []
    for e in seq:
        n = n + 1 if n < 8 else 8; a += (e - a) / n; out.append(a)
    return np.array(out)
old, new = 1.0, -1.0
o = avg8_run([old] * 50 + [new] * 60)[50:]                # 不清零时：参考翻转，avg8 从 +1 走向 −1
rem = (o - new) / (old - new)
k1 = int(np.argmax(rem < 0.01)) + 1
print(f"avg8 不清零：翻转后第 8 个读数时旧值还剩 {rem[7]*100:.1f}%（(7/8)^8 = {(7/8)**8*100:.1f}%）；"
      f"第 {k1} 个读数才降到 1% 以下 = {k1/FEXC:.2f} s（公式 ln0.01/ln(7/8) = {np.log(0.01)/np.log(7/8):.1f} 个）")
rng = np.random.default_rng(3); z = avg8_run(rng.normal(0, 1, 200000))[100:]
print(f"avg8 稳态噪声：单个读数标准差 1 → avg8 标准差 {z.std():.3f}，缩小 {1/z.std():.2f} 倍（公式 √((2−α)/α) = √15 = {np.sqrt(15):.2f}；不是 √8 = {np.sqrt(8):.2f}）")
print("发 f：startTimer1() 把 avg8、nAvg 清零，下一个输出只用翻转后的数据；D10 下一个上升沿且正负两半都采到样才出数，"
      f"即翻转后 {1/FEXC:.2f}～{1.5/FEXC:.2f} s 出第一个新读数")

# (d) 举一反三：60 Hz 电网
for fe, name in ((FEXC, "6.25 Hz"), (7.5, "7.5 Hz"), (5.0, "5 Hz")):
    print(f"励磁 {name}：50 Hz 是 {50/fe:.2f} 倍，60 Hz 是 {60/fe:.2f} 倍")
top75 = round(F_CPU / PRE1 / 2 / 7.5) - 1
print(f"7.5 Hz：TOP = 16 MHz ÷ 256 ÷ 2 ÷ 7.5 − 1 ≈ {top75}，实际 {F_CPU/PRE1/2/(top75+1):.4f} Hz；半周期 {(top75+1)*PRE1/F_CPU*1e3:.2f} ms = 60 Hz 周期的 {(top75+1)*PRE1/F_CPU*60:.3f} 倍")

# (e) 程序里跟 TOP 挂钩的常数（page4 程序已改成全部由 TOP 算出）
for top, name in ((TOP, "6.25 Hz"), (top75, "7.5 Hz（60 Hz 电网）"), (6249, "5 Hz")):
    half_ms = (top + 1) * PRE1 / F_CPU * 1e3
    print(f"{name}：TOP = {top}，半周期 {half_ms:.2f} ms，BLANK_US = (TOP+1)×8 = {(top+1)*8} µs，"
          f"45° = (TOP+1)/4 = {(top+1)//4} 计数，90° = (TOP+1)/2 = {(top+1)//2} 计数，1 计数 = {180/(top+1):.4f}°")
lead = 6249 - 4999
ph = lead * 180 / 6250
print(f"5 Hz 若 OCR1B 仍写死 4999：D10 比 D9 早 {lead} 计数 = {ph:.1f}°，CD4053 那路读数只剩 1 − 2×{ph:.0f}/180 = {(1-2*ph/180)*100:.0f}%")
print(f"7.5 Hz 若 OCR1B 仍写死 4999 > TOP {top75}：CTC 计到 TOP 就清零，OCR1B 永远比较不到，D10 不翻转")
