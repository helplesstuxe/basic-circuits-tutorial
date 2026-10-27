"""40 热式流量与 RTD 恒温差：页面里所有数字的 Python 计算。运行（仓库根目录）：
    /workspace/circuits-venv/bin/python code/40_sim.py
内容：
  1. PT100 的 Callendar–Van Dusen 公式（系数来自 TI SBAA275A）、灵敏度、自热误差
  2. PT100 电桥 + 仪表放大器（2.5 V 激励、2.4 kΩ 上臂、G = 100）的输出与非线性（spice/40/bridge.cir 核对）
  3. 10 kΩ NTC（Vishay NTCLE100E3103，B25/85 = 3977 K，公式系数来自数据手册）分压读数、灵敏度、自热
  4. 实验加热器：9 V 加 560 Ω/2 W 金属膜电阻，功率与最高温升（R_th 75～115 K/W 来自 Vishay PR02 数据手册）
  5. 两节点热模型 + King 定律散热，比较恒功率（CP）和恒温差（CTA，Arduino 离散 PI）对风速台阶的响应
  6. King 定律两点标定、反算风速；不做环境补偿时环境温度变化造成的误读
  7. 设定温差、PI 增益的扫描（page3 用）
模型里标「假设」的参数（热容、耦合热导、风速系数）是示意值，实验时以实测为准。"""
import numpy as np

# ---------------------------------------------------------------- 1. PT100
A_CVD, B_CVD = 3.9083e-3, -5.775e-7          # SBAA275A，T ≥ 0 °C
R0_PT = 100.0


def pt100(T):
    return R0_PT * (1 + A_CVD * T + B_CVD * T ** 2)


def pt100_T(R):
    """CVD 反解（T ≥ 0 °C 的二次式）。"""
    return (-A_CVD + np.sqrt(A_CVD ** 2 - 4 * B_CVD * (1 - R / R0_PT))) / (2 * B_CVD)


def self_heat(I, R, delta):
    """自热温升 ΔT = I²R / δ，δ 为耗散常数，单位 W/K（手册常写 mW/°C）。"""
    return I ** 2 * R / delta


# ---------------------------------------------------------------- 2. 电桥
VEX, RTOP, RREF, G_INA = 2.5, 2400.0, 100.0, 100.0


def bridge(T):
    rt = pt100(T)
    vd = VEX * (rt / (RTOP + rt) - RREF / (RTOP + RREF))
    return vd, G_INA * vd


# ---------------------------------------------------------------- 3. NTC
NTC_R25, NTC_RS, NTC_VCC = 10e3, 10e3, 5.0
NTC_ABCD = (-14.6337, 4791.842, -115334.0, -3.730535e6)        # 数据手册「Mat A，B=3977」行，R(T)
NTC_A1D1 = (3.354016e-3, 2.569850e-4, 2.620131e-6, 6.383091e-8)  # 同一行，T(R)
NTC_DELTA = 7e-3     # 耗散常数 δ = 7 mW/K
NTC_TAU = 15.0       # 热时间常数 15 s（数据手册，仅供参考）


def ntc_R(Tc):
    T = np.asarray(Tc) + 273.15
    a, b, c, d = NTC_ABCD
    return NTC_R25 * np.exp(a + b / T + c / T ** 2 + d / T ** 3)


def ntc_T(R):
    x = np.log(np.asarray(R) / NTC_R25)
    a1, b1, c1, d1 = NTC_A1D1
    return 1.0 / (a1 + b1 * x + c1 * x ** 2 + d1 * x ** 3) - 273.15


def ntc_V(Tc):
    r = ntc_R(Tc)
    return NTC_VCC * r / (NTC_RS + r)


def ntc_adc(Tc):
    r = ntc_R(Tc)
    return 1024.0 * r / (NTC_RS + r)


def adc_to_T(cnt):
    cnt = np.clip(cnt, 1, 1022)
    r = NTC_RS * cnt / (1024.0 - cnt)
    return ntc_T(r)


# ---------------------------------------------------------------- 4. 加热器
V_H, R_H = 9.0, 560.0
P_MAX = V_H ** 2 / R_H
RTH_PR02 = (75.0, 115.0)     # K/W，PR02 数据手册（铜引线 / 铁铜引线，焊在板上）
T_CUTOFF = 45.0              # 软件切断温度
T_AMB_MAX = 25.0

# ---------------------------------------------------------------- 5. 热模型（假设值）
C_H = 0.4          # J/K，加热电阻本体热容（假设）
G_H0 = 1 / 100.0   # W/K，静止空气里加热电阻对环境的热导（假设：面包板上没有铜箔，取 100 K/W）
G_C = 0.02         # W/K，导热胶带把 NTC 贴在电阻上的耦合热导（假设）
C_N = NTC_TAU * NTC_DELTA   # 0.105 J/K，由数据手册 τ·δ 得到
K_KING, N_KING = 1.0, 0.45  # G(v) = G0·(1 + k·v^n)，n 取 0.45（METU AE547 讲义：0.45～0.5）；k 为假设


def kingG(G0, v):
    return G0 * (1 + K_KING * np.power(np.maximum(v, 0.0), N_KING))


def steady(P, v):
    """稳态：返回（加热电阻温升，NTC 温升）。"""
    gh, gn = kingG(G_H0, v), kingG(NTC_DELTA, v)
    # [gh+gc, -gc; -gc, gc+gn] [th; tn] = [P; 0]
    M = np.array([[gh + G_C, -G_C], [-G_C, G_C + gn]])
    th, tn = np.linalg.solve(M, [P, 0.0])
    return th, tn


def dTn_per_W(v):
    return steady(1.0, v)[1]


def flow_profile(t):
    return np.where(t < 120, 0.0, np.where(t < 300, 1.0, np.where(t < 480, 2.0, 0.0)))


def simulate(mode, t_end=660.0, duty_cp=0.6, dT_set=2.0, Kp=0.6, Ti=10.0, Ts=0.5, dt=0.05,
             Tamb=lambda t: 25.0, compensate=True, seed=1, vfun=flow_profile, noise=True, hyst=0.2):
    """mode = 'CP'（固定占空比）、'ONOFF'（带回差的开关控温，回差 ±hyst）或 'CTA'（PI 控温差）。返回 dict(t, v, Th, Tn, Ta, duty, dTmeas)。
    Arduino 每 Ts 秒读 A0（加热 NTC）、A1（环境 NTC）各 16 次取平均（带 ±0.5 LSB 量级噪声），算温差，PI 更新占空比。"""
    rng = np.random.default_rng(seed)
    n = int(round(t_end / dt))
    t = np.arange(n) * dt
    Th = np.empty(n); Tn = np.empty(n); duty = np.empty(n); dTm = np.empty(n); Ta = np.empty(n)
    th, tn = Tamb(0.0), Tamb(0.0)
    d, integ = (duty_cp if mode == "CP" else 0.0), 0.0
    dmeas = 0.0
    every = int(round(Ts / dt))
    Ta0 = Tamb(0.0)
    for k in range(n):
        ta = Tamb(t[k])
        v = float(vfun(t[k]))
        if k % every == 0:
            def rd(T):
                c = ntc_adc(T)
                if noise:
                    c = np.round(c + rng.normal(0, 0.5, 16)).mean()
                else:
                    c = np.round(c)
                return float(adc_to_T(c))
            Tn_m, Ta_m = rd(tn), rd(ta)
            dmeas = Tn_m - (Ta_m if compensate else Ta0)
            if mode == "ONOFF":
                if dmeas < dT_set - hyst:
                    d = 1.0
                elif dmeas > dT_set + hyst:
                    d = 0.0
            if mode == "CTA":
                e = dT_set - dmeas
                u = Kp * e + integ
                if 0.0 < u < 1.0 or (u >= 1.0 and e < 0) or (u <= 0.0 and e > 0):
                    integ += Kp * Ts / Ti * e
                d = float(np.clip(Kp * e + integ, 0.0, 1.0))
            if Tn_m > T_CUTOFF:
                d = 0.0
        P = d * P_MAX
        gh, gn = kingG(G_H0, v), kingG(NTC_DELTA, v)
        dth = (P - gh * (th - ta) - G_C * (th - tn)) / C_H
        dtn = (G_C * (th - tn) - gn * (tn - ta)) / C_N
        th += dth * dt; tn += dtn * dt
        Th[k], Tn[k], duty[k], dTm[k], Ta[k] = th, tn, d, dmeas, ta
    return dict(t=t, v=flow_profile(t) if vfun is flow_profile else np.array([vfun(x) for x in t]),
                Th=Th, Tn=Tn, Ta=Ta, duty=duty, dTm=dTm)


def steady_duty(v, dT=2.0):
    """恒温差 dT 时的稳态占空比（NTC 温升 = 占空 × P_MAX × 每瓦温升）。"""
    return dT / (P_MAX * dTn_per_W(v))


def movavg(t, y, win):
    """过去 win 秒的滑动平均（开关控温时用它把 0/1 的占空变成“平均占空比”）。"""
    n = max(1, int(round(win / (t[1] - t[0]))))
    c = np.cumsum(np.insert(y, 0, 0.0))
    out = np.empty_like(y)
    for i in range(len(y)):
        j = max(0, i + 1 - n)
        out[i] = (c[i + 1] - c[j]) / (i + 1 - j)
    return out


HYST = 0.2       # 开关控温的回差：温差低于 2.0−0.2 K 开、高于 2.0+0.2 K 关
NCYC = 3         # 平均占空比用最近 3 个完整开关周期


def cycle_duty(t, d, ncyc=NCYC):
    """开关控温的平均占空比：每次“关→开”时结算上一个完整周期，取最近 ncyc 个周期按时间加权平均。
    返回与 t 等长的数组（第一个周期结束前为 nan）和每个周期的 (结束时刻, 周期长度, 占空比) 列表。"""
    on = np.where((d[1:] > 0.5) & (d[:-1] < 0.5))[0] + 1
    out = np.full(len(d), np.nan)
    cyc, hist, val, k = [], [], np.nan, 0
    for i in range(len(d)):
        if k < len(on) and i == on[k]:
            if k > 0:
                a, b = on[k - 1], on[k]
                cyc.append((t[b], t[b] - t[a], d[a:b].mean()))
                hist = (hist + [(d[a:b].mean(), t[b] - t[a])])[-ncyc:]
                val = sum(x * w for x, w in hist) / sum(w for _, w in hist)
            k += 1
        out[i] = val
    return out, cyc


def t90(t, y, t0, t1, smooth=1):
    """t0 时刻发生台阶，找 y 走完 90 % 变化所需时间（用 t1 前 20 s 的平均作终值）。"""
    if smooth > 1:
        y = np.convolve(y, np.ones(smooth) / smooth, mode="same")
    i0 = np.searchsorted(t, t0)
    y0 = y[i0 - 1]
    yf = y[(t > t1 - 20) & (t < t1 - 1)].mean()
    tgt = y0 + 0.9 * (yf - y0)
    seg = y[i0:np.searchsorted(t, t1)]
    if yf > y0:
        j = np.argmax(seg >= tgt)
    else:
        j = np.argmax(seg <= tgt)
    return t[i0 + j] - t0, y0, yf


def king_fit(v_cal, G_cal):
    """两点标定：v=0 给 A，另一点给 B（n 固定 0.45）。G = P/ΔT。"""
    A = G_cal[0]
    B = (G_cal[1] - A) / v_cal[1] ** N_KING
    return A, B


def king_v(G, A, B):
    return np.power(np.maximum(G - A, 0) / B, 1 / N_KING)


def report():
    out = {}
    print("== 1. PT100 ==")
    for T in (0, 25, 50, 100):
        print(f"  R({T} °C) = {pt100(T):.3f} Ω")
    print(f"  0 °C 处灵敏度 R0·A = {R0_PT * A_CVD:.4f} Ω/K；0→100 °C 平均 {(pt100(100) - 100) / 100:.4f} Ω/K")
    lin = 100 + (pt100(100) - 100) * 50 / 100
    print(f"  50 °C 实际 {pt100(50):.3f} Ω，两端连直线给 {lin:.3f} Ω，差 {pt100(50) - lin:.3f} Ω = {(pt100(50) - lin) / ((pt100(100) - 100) / 100):.3f} K")
    for I in (0.1e-3, 0.5e-3, 1e-3, 2e-3, 5e-3):
        print(f"  I = {I * 1e3:.1f} mA：P = {I ** 2 * 100 * 1e3:.3f} mW，ΔT(δ=2.5 mW/K) = {self_heat(I, 100, 2.5e-3):.3f} K，"
              f"ΔT(δ=65 mW/K) = {self_heat(I, 100, 65e-3) * 1e3:.2f} mK，信号 {I * R0_PT * A_CVD * 1e3:.3f} mV/K")
    print("== 2. 电桥 ==")
    i_br = VEX / (RTOP + 100)
    print(f"  桥臂电流（0 °C）= {i_br * 1e3:.3f} mA，PT100 功耗 {i_br ** 2 * 100 * 1e3:.3f} mW，自热(2.5 mW/K) {self_heat(i_br, 100, 2.5e-3):.3f} K")
    for T in (0, 25, 50, 75, 100):
        vd, vo = bridge(T)
        print(f"  T={T:3d} °C：V_diff = {vd * 1e3:.3f} mV，V_out(G=100) = {vo:.4f} V")
    Ts_ = np.linspace(0, 100, 101)
    vo = np.array([bridge(T)[1] for T in Ts_])
    line = vo[0] + (vo[-1] - vo[0]) * Ts_ / 100
    k = (vo[-1] - vo[0]) / 100
    err = (vo - line) / k
    print(f"  平均灵敏度 {k * 1e3:.2f} mV/K；端点直线最大偏差 {err.max():.3f} K（在 {Ts_[np.argmax(err)]:.0f} °C）")
    out["bridge_k"] = k
    print("== 3. NTC ==")
    for T in (20, 25, 30, 35, 40, 45):
        print(f"  {T} °C：R = {ntc_R(T):.0f} Ω，V = {ntc_V(T):.3f} V，ADC ≈ {ntc_adc(T):.1f}")
    s = (ntc_V(25.5) - ntc_V(24.5))
    print(f"  25 °C 附近灵敏度 {s * 1e3:.2f} mV/K = {s / NTC_VCC * 1024:.2f} LSB/K → 1 LSB ≈ {1 / (s / NTC_VCC * 1024):.3f} K")
    s45 = ntc_V(45.5) - ntc_V(44.5)
    print(f"  45 °C 附近灵敏度 {s45 * 1e3:.2f} mV/K = {s45 / NTC_VCC * 1024:.2f} LSB/K")
    i_ntc = NTC_VCC / (NTC_RS + ntc_R(25))
    p_ntc = i_ntc ** 2 * ntc_R(25)
    print(f"  25 °C 时 NTC 电流 {i_ntc * 1e3:.3f} mA，功耗 {p_ntc * 1e3:.3f} mW，自热 {p_ntc / NTC_DELTA:.3f} K")
    print(f"  B 公式核对：T(R(37.0)) = {ntc_T(ntc_R(37.0)):.4f} °C")
    print("== 4. 加热器 ==")
    print(f"  I = {V_H / R_H * 1e3:.2f} mA，P_max = {P_MAX:.4f} W（额定 2 W 的 {P_MAX / 2 * 100:.1f} %）")
    for r in RTH_PR02:
        print(f"  R_th = {r:.0f} K/W：100 % 占空温升 {P_MAX * r:.1f} K → 环境 {T_AMB_MAX:.0f} °C 时 {T_AMB_MAX + P_MAX * r:.1f} °C")
    th, tn = steady(P_MAX, 0.0)
    print(f"  模型（静止空气，100 %）：电阻温升 {th:.2f} K，NTC 温升 {tn:.2f} K")
    out["Pmax"] = P_MAX
    for (v_s, r_s) in ((5.0, 47.0), (9.0, 47.0), (12.0, 47.0), (12.0, 560.0)):
        p_s = v_s ** 2 / r_s
        print(f"  对比：{v_s:.0f} V 加 {r_s:.0f} Ω：I = {v_s / r_s * 1e3:.1f} mA，P = {p_s:.3f} W，"
              f"按 75～115 K/W 温升 {p_s * 75:.0f}～{p_s * 115:.0f} K")
    print("== 4b. 有风 / 无风对比（固定 60 % 占空，从冷态开始）==")
    for v in (0.0, 1.0):
        r = simulate("CP", t_end=600.0, vfun=lambda x, v=v: v, noise=False)
        dT = r["Tn"] - r["Ta"]
        th_ss, tn_ss = steady(0.6 * P_MAX, v)
        i63 = np.argmax(dT >= 0.632 * tn_ss)
        print(f"  v={v:.0f} m/s：NTC 温差 60 s 时 {dT[r['t'] >= 60][0]:.2f} K，600 s 时 {dT[-1]:.2f} K（稳态 {tn_ss:.2f} K），"
              f"到 63 % 用 {r['t'][i63]:.0f} s")
        out[f"wind_{v:.0f}"] = r
    print(f"  稳态散热能力 δ_总 = P/ΔT：v=0 时 {0.6 * P_MAX / steady(0.6 * P_MAX, 0.0)[1] * 1e3:.1f} mW/K，"
          f"v=1 时 {0.6 * P_MAX / steady(0.6 * P_MAX, 1.0)[1] * 1e3:.1f} mW/K")
    print("== 4c. 体积流量 Q_V = v·A（20 mm × 20 mm 风道）==")
    A_duct = 0.02 * 0.02
    for v in (0.5, 1.0, 2.0):
        print(f"  v={v} m/s：Q_V = {v * A_duct * 1e6:.0f} cm³/s = {v * A_duct * 60e3:.1f} L/min")
    print("== 5. CP vs CTA ==")
    for v in (0.0, 1.0, 2.0, 3.0):
        th, tn = steady(1.0, v)
        print(f"  v={v:.0f} m/s：每瓦 NTC 温升 {tn:.1f} K/W，电阻 {th:.1f} K/W；G_h={kingG(G_H0, v) * 1e3:.2f} mW/K")
    cp = simulate("CP")
    cta = simulate("CTA")
    out["cp"], out["cta"] = cp, cta
    for (a, b, lab) in ((120, 300, "0→1 m/s"), (300, 480, "1→2 m/s"), (480, 660, "2→0 m/s")):
        tc, y0, yf = t90(cp["t"], cp["Tn"] - cp["Ta"], a, b)
        td, d0, df = t90(cta["t"], cta["duty"], a, b, smooth=int(2 / 0.05))
        print(f"  {lab}：CP ΔT {y0:.2f}→{yf:.2f} K，t90 = {tc:.1f} s；CTA 占空 {d0 * 100:.1f}→{df * 100:.1f} %，t90 = {td:.1f} s")
        out.setdefault("steps", []).append((lab, tc, y0, yf, td, d0, df))
    m = cta["t"] > 60
    print(f"  CTA 温差（60 s 后）测量值范围 {cta['dTm'][m].min():.2f}～{cta['dTm'][m].max():.2f} K")
    print(f"  CP/CTA 加热电阻最高 {cp['Th'].max():.2f} / {cta['Th'].max():.2f} °C；NTC 最高 {cp['Tn'].max():.2f} / {cta['Tn'].max():.2f} °C")
    print("== 5b. 开关控温（主实验，回差 ±0.2 K，最近 3 个周期平均）==")
    oo = simulate("ONOFF")
    oo["avg"], oo["cyc"] = cycle_duty(oo["t"], oo["duty"])
    out["onoff"] = oo
    t = oo["t"]
    for (a, b, lab) in ((120, 300, "0→1 m/s"), (300, 480, "1→2 m/s"), (480, 660, "2→0 m/s")):
        td, d0, df = t90(t, np.nan_to_num(oo["avg"]), a, b)
        per = [c[1] for c in oo["cyc"] if a + 60 < c[0] < b]
        m = (t > a + 60) & (t < b)
        print(f"  {lab}：平均占空 {d0 * 100:.1f}→{df * 100:.1f} %，t90 = {td:.1f} s；"
              f"稳态开关周期 {np.mean(per):.1f} s；温差测量值 {oo['dTm'][m].min():.2f}～{oo['dTm'][m].max():.2f} K")
        out.setdefault("oo_steps", []).append((lab, td, d0, df, np.mean(per)))
    print(f"  加热电阻最高 {oo['Th'].max():.2f} °C，NTC 最高 {oo['Tn'].max():.2f} °C（环境 25 °C）")
    # 恒定风速下的开关控温平均占空（标定用）
    oo_cal = {}
    for v in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        r = simulate("ONOFF", t_end=360.0, vfun=lambda x, v=v: v)
        a, _ = cycle_duty(r["t"], r["duty"])
        tail = a[r["t"] > 300]
        if np.all(np.isnan(tail)):
            frac_on = r["duty"][r["t"] > 300].mean()
            print(f"  v={v} m/s：最后 60 s 加热 {frac_on * 100:.0f} % 时间开着、一次也没关 → 超出量程（PI 稳态值 {steady_duty(v) * 100:.1f} %）")
            continue
        oo_cal[v] = float(np.nanmean(tail))
        print(f"  v={v} m/s：开关控温平均占空 {oo_cal[v] * 100:.1f} %（PI 稳态值 {steady_duty(v) * 100:.1f} %）")
    vc = np.array([0.0, 1.0, 2.0, 2.5])
    poly_oo = np.polyfit([oo_cal[v] for v in vc], vc, 3)
    for v in (0.5, 1.5):
        vv = np.polyval(poly_oo, oo_cal[v])
        print(f"   四点标定（占空→风速）：真值 {v} m/s → 反算 {vv:.3f} m/s（误差 {(vv - v) / v * 100:+.1f} %）")
    vc5 = np.array([0.0, 0.5, 1.0, 2.0, 2.5])
    poly5 = np.polyfit([oo_cal[v] for v in vc5], vc5, 3)
    for v in (1.5,):
        vv = np.polyval(poly5, oo_cal[v])
        print(f"   五点标定（多加 0.5 m/s）：真值 {v} m/s → 反算 {vv:.3f} m/s（误差 {(vv - v) / v * 100:+.1f} %）")
    for v in vc5:
        print(f"     五点拟合在标定点 {v} m/s 的残差 {np.polyval(poly5, oo_cal[v]) - v:+.3f} m/s")
    out["oo_cal"], out["poly_oo"], out["poly5"] = oo_cal, poly_oo, poly5
    print("== 6. King 标定与反算 ==")
    dT_set = 2.0
    G_of = {}
    for v in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        P = dT_set / dTn_per_W(v)
        G_of[v] = P / dT_set
        print(f"  v={v} m/s：稳态 P = {P * 1e3:.2f} mW（占空 {P / P_MAX * 100:.1f} %），G=P/ΔT = {G_of[v] * 1e3:.3f} mW/K")
    A, B = king_fit((0.0, 2.0), (G_of[0.0], G_of[2.0]))
    print(f"  两点（0、2 m/s）标定：a = {A * 1e3:.3f} mW/K，b = {B * 1e3:.3f} mW/K/(m/s)^0.45")
    for v in (0.5, 1.0, 1.5, 3.0):
        vv = king_v(G_of[v], A, B)
        print(f"   真值 {v} m/s → 反算 {vv:.3f} m/s（误差 {(vv - v) / v * 100:+.1f} %）")
    out["king"] = (A, B, G_of)
    # 多点标定：在 0、1、2、3 m/s 量 G，用 v 对 G 的三次多项式（热线标定常用多项式拟合，METU AE547 讲义）
    vc = np.array([0.0, 1.0, 2.0, 3.0])
    Gc = np.array([G_of[v] for v in vc])
    poly = np.polyfit(Gc, vc, 3)
    for v in (0.5, 1.5, 2.5):
        vv = np.polyval(poly, G_of[v])
        print(f"   四点多项式标定：真值 {v} m/s → 反算 {vv:.3f} m/s（误差 {(vv - v) / v * 100:+.1f} %）")
    out["poly"] = poly
    print("== 6b. 不做环境补偿 ==")
    step_amb = lambda t: 25.0 + (1.0 if t >= 300 else 0.0)
    vconst = lambda t: 1.0
    for comp in (True, False):
        r = simulate("CTA", t_end=600, Tamb=step_amb, compensate=comp, vfun=vconst)
        d_before = r["duty"][(r["t"] > 270) & (r["t"] < 299)].mean()
        d_after = r["duty"][(r["t"] > 570)].mean()
        G_after = d_after * P_MAX / dT_set
        v_read = np.polyval(poly, G_after)
        print(f"  补偿={comp}：环境 25→26 °C，占空 {d_before * 100:.1f}% → {d_after * 100:.1f}%，按 2 K 换算风速读成 {v_read:.2f} m/s（真值 1.00）")
        out[f"amb_{comp}"] = r
        r2 = simulate("ONOFF", t_end=600, Tamb=step_amb, compensate=comp, vfun=vconst)
        a2, _ = cycle_duty(r2["t"], r2["duty"])
        b2 = np.nanmean(a2[(r2["t"] > 240) & (r2["t"] < 299)])
        tail = a2[r2["t"] > 540]
        if np.all(np.isnan(tail)):
            print(f"    开关控温、补偿={comp}：环境升温后温差一直 > 2.2 K，加热一次也不开，平均占空无法结算（≈ 0 %）")
        else:
            print(f"    开关控温、补偿={comp}：平均占空 {b2 * 100:.1f}% → {np.nanmean(tail) * 100:.1f}%")
        out[f"amb_oo_{comp}"] = r2
    print("== 7. 设定温差扫描 ==")
    for dts in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0):        # 1.5、2.5 K 是 page3 练习 2、page4 思考题 2 用的
        vs = np.linspace(0, 5, 501)
        need = np.array([dts / dTn_per_W(v) for v in vs])
        if (need > P_MAX).any():                      # 在越过 P_MAX 的两个扫描点之间线性插值，不取格点
            i = int(np.argmax(need > P_MAX))
            vmax = vs[i - 1] + (P_MAX - need[i - 1]) / (need[i] - need[i - 1]) * (vs[i] - vs[i - 1])
        else:
            vmax = np.inf
        th0 = steady(dts / dTn_per_W(0.0), 0.0)[0]
        res = (1 / (ntc_adc(25.5) - ntc_adc(24.5)))
        vmax_s = f"v ≈ {vmax:.2f} m/s" if np.isfinite(vmax) else "v > 5 m/s（扫描上限）"
        print(f"  ΔT={dts:g} K：静止空气占空 {need[0] / P_MAX * 100:.1f} %，电阻温升 {th0:.2f} K；功率够用到 {vmax_s}；"
              f"1 LSB 相对误差 {abs(res) / dts * 100:.1f} %")
    print("== 7b. PI 增益扫描（0→1 m/s 台阶，ΔT=2 K）==")
    step1 = lambda t: 0.0 if t < 120 else 1.0
    for Kp, Ti in ((0.1, 10.0), (0.6, 10.0), (2.0, 10.0)):
        r = simulate("CTA", t_end=300, vfun=step1, Kp=Kp, Ti=Ti)
        m = r["t"] > 120
        err = r["dTm"][m] - dT_set
        td, d0, df = t90(r["t"], r["duty"], 120, 300, smooth=int(2 / 0.05))
        sw = np.abs(np.diff(r["duty"][m][::10])).mean()
        out[f"pi_{Kp}_{Ti}_t90"] = td
        print(f"  Kp={Kp}, Ti={Ti} s：占空 t90 = {td:.1f} s，温差最大偏离 {err.min():+.2f} K，稳态段占空平均跳动 {sw * 100:.2f} %/步")
        out[f"pi_{Kp}_{Ti}"] = r
    print("== 8. 例题与练习核算（page2 例 1～3、page3 练习 1～4、page2/page4 加热电阻替代方案）==")
    Ta, Tcut, rth = 25.0, 45.0, RTH_PR02[1]
    P_need0 = steady_duty(0.0) * P_MAX                     # 无风维持 2 K 需要的平均功率（PI 理想）
    print(f"  无风维持 2 K 需要平均功率 {P_need0 * 1e3:.1f} mW（占空 {steady_duty(0.0) * 100:.1f} %）")
    for V, R, dty in ((9.0, 560.0, 0.4), (9.0, 1000.0, None)):
        I, P = V / R, V ** 2 / R
        msg = f"  例：{V:.1f} V / {R:.0f} Ω：全开 {I * 1e3:.2f} mA、{P * 1e3:.1f} mW，最坏表面 {Ta + P * rth:.1f} °C"
        if dty is not None:
            msg += f"；占空 {dty * 100:.0f} % 平均 {dty * P * 1e3:.1f} mW"
        else:
            msg += f"；无风 2 K 需占空 {P_need0 / P * 100:.1f} %"
        print(msg)
    Pmax_ok = (Tcut - Ta) / rth
    print(f"  例 3：12 V、最坏不超过 45 °C：P ≤ {Pmax_ok:.3f} W，R_H ≥ {12 ** 2 / Pmax_ok:.0f} Ω；取 1 kΩ："
          f"{12 ** 2 / 1000:.3f} W，最坏 {Ta + 12 ** 2 / 1000 * rth:.1f} °C")
    for R in (470.0, 680.0, 1000.0):
        P = 9.0 ** 2 / R
        print(f"  替代方案 9 V / {R:.0f} Ω：{P:.3f} W，最坏表面 {Ta + P * rth:.1f} °C")
    P85 = 8.5 ** 2 / R_H
    print(f"  练习 1：8.5 V 全开 {P85 * 1e3:.1f} mW，无风占空 {P_need0 / P85 * 100:.1f} %（9.0 V 时 {steady_duty(0.0) * 100:.1f} %）")
    lsb = abs(1 / (ntc_adc(25.5) - ntc_adc(24.5)))
    print(f"  练习 2：1 字 {lsb:.3f} K，设定 3 K 时相对误差 {lsb / 3 * 100:.1f} %，无风占空 {steady_duty(0.0, 3.0) * 100:.1f} %")
    d1 = steady_duty(1.0)
    print(f"  练习 3：1 m/s 稳态占空（PI 理想）{d1 * 100:.1f} %；环境升 0.5 K 不补偿 → 真实温差 1.5 K，占空 {steady_duty(1.0, 1.5) * 100:.1f} %"
          f"（0.5 m/s 时 2 K 需 {steady_duty(0.5) * 100:.1f} %）")
    from scipy.optimize import brentq
    dT3 = P_MAX * dTn_per_W(3.0)
    v_pi = brentq(lambda v: P_MAX * dTn_per_W(v) - 2.0, 0.1, 10)
    v_oo = brentq(lambda v: P_MAX * dTn_per_W(v) - 2.2, 0.1, 10)
    print(f"  量程：全开时 3 m/s 温差只有 {dT3:.2f} K（PI 稳态占空 {steady_duty(3.0) * 100:.1f} %）；"
          f"PI 撑住 2.0 K 到 {v_pi:.2f} m/s，开关控温要碰到上门限 2.2 K 只到 {v_oo:.2f} m/s")
    Rf = 20.0 * (1 + 0.00385 * 20)
    print(f"  练习 4：热膜 +20 K 时 {Rf:.2f} Ω，R_C = 200 × {Rf:.2f} / 20 = {200 * Rf / 20:.1f} Ω")
    return out


if __name__ == "__main__":
    report()
