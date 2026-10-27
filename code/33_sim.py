"""33 带通与 50 Hz 陷波：页面里用到的全部数值都由本脚本算出（在仓库根目录运行：python code/33_sim.py）。
MFB（多重反馈）带通：R1 输入电阻、R3 对地（虚地）电阻、两只相等的电容 C、R2 反馈电阻。
双 T 陷波：R–R 两只电阻 + 中点 2C 对地；C–C 两只电容 + 中点 R/2 对地。
"""
import numpy as np

PI = np.pi


# ---------------- MFB 带通 ----------------
def mfb_design(f0, Q, A, C):
    """给定中心频率 f0、品质因数 Q、中心增益大小 A、电容 C，按设计公式算 R1、R2、R3。"""
    R1 = Q / (2 * PI * f0 * C * A)
    R2 = Q / (PI * f0 * C)
    R3 = Q / (2 * PI * f0 * C * (2 * Q ** 2 - A))
    return R1, R2, R3


def mfb_params(R1, R2, R3, C):
    """由元件值反算 f0、Q、中心增益大小 A0、带宽 BW（两只电容相等）。"""
    f0 = 1 / (2 * PI * C) * np.sqrt((R1 + R3) / (R1 * R2 * R3))
    Q = PI * f0 * R2 * C
    A0 = R2 / (2 * R1)
    return f0, Q, A0, f0 / Q


def bp_mag(f, f0, Q, A0):
    """二阶带通幅频（不用复数的写法）：|H| = A0 / sqrt(1 + Q²(f/f0 − f0/f)²)。"""
    f = np.asarray(f, float)
    return A0 / np.sqrt(1 + Q ** 2 * (f / f0 - f0 / f) ** 2)


def mfb_ode(f, R1, R2, R3, C, amp=1.0, ncyc=40, spc=400):
    """用「电容电流 = C × 电压变化率」一小步一小步算 MFB 带通（理想运放，反相端 = 虚地），返回稳态输出幅度。
    x1：C1（节点 A 到反相端）上的电压；x2：C2（节点 A 到输出）上的电压；输出 vo = x1 − x2。"""
    dt = 1 / (f * spc)
    n = ncyc * spc
    x1 = x2 = 0.0
    vo = np.empty(n)
    for k in range(n):
        vi = amp * np.sin(2 * PI * f * k * dt)
        i1 = (x2 - x1) / R2                 # 流过 C1 的电流 = 流过 R2 的电流（虚断）
        x1 += i1 / C * dt                   # 先更新 C1 的电压
        i1 = (x2 - x1) / R2                 # 用新的 x1 重算一次 i1（这样共振时不会越算越大）
        i2 = (vi - x1) / R1 - x1 / R3 - i1  # 节点 A：流进 = 流出，剩下的流进 C2
        x2 += i2 / C * dt
        vo[k] = x1 - x2
    tail = vo[-10 * spc:]
    return (tail.max() - tail.min()) / 2


def mfb_ode_wave(vi, dt, R1, R2, R3, C):
    """同 mfb_ode 的逐步算法，但输入是任意波形数组 vi（每 dt 秒一个点），返回输出波形数组。"""
    x1 = x2 = 0.0
    vo = np.empty(len(vi))
    for k, v in enumerate(vi):
        i1 = (x2 - x1) / R2
        x1 += i1 / C * dt
        i1 = (x2 - x1) / R2
        x2 += ((v - x1) / R1 - x1 / R3 - i1) / C * dt
        vo[k] = x1 - x2
    return vo


def mfb_nodal(f, R1, R2, R3, C1, C2, gbw=None, a0=2e5):
    """节点电压法（复数，只在脚本里用）：运放用单极点模型 A(f) = a0 / (1 + j f a0 / gbw)；gbw=None 为理想运放。
    返回输出 / 输入（复数）。未知量：节点 A 电压 va、反相端电压 vn；vo = −A·vn。"""
    w = 2 * PI * np.asarray(f, float)
    s = 1j * w
    if gbw is None:
        Aol = np.full_like(w, 1e12, dtype=complex)
    else:
        Aol = a0 / (1 + s * a0 / (2 * PI * gbw))
    out = []
    for k in range(len(w)):
        A = Aol[k]; sk = s[k]
        # 节点 A：(vi − va)/R1 = va/R3 + (va − vn) sC1 + (va − vo) sC2，vo = −A vn
        # 反相端：(va − vn) sC1 = (vn − vo)/R2
        M = np.array([[1 / R1 + 1 / R3 + sk * C1 + sk * C2, -sk * C1 + sk * C2 * A],
                      [sk * C1, -sk * C1 - (1 + A) / R2]], complex)
        b = np.array([1 / R1, 0], complex)
        va, vn = np.linalg.solve(M, b)
        out.append(-A * vn)
    return np.array(out)


# ---------------- 双 T 陷波 ----------------
def twint_f0(R, C):
    """双 T 陷波频率：f0 = 1 / (2πRC)。"""
    return 1 / (2 * PI * R * C)


def twint_mag(f, f0):
    """理想、对称、空载双 T 的幅频：|H| = |1 − x²| / sqrt((1 − x²)² + 16x²)，x = f/f0。"""
    x = np.asarray(f, float) / f0
    return np.abs(1 - x ** 2) / np.sqrt((1 - x ** 2) ** 2 + 16 * x ** 2)


def twint_nodal(f, Ra, Rb, Rc, Ca, Cb, Cc, RL=None, Rs=0.0):
    """双 T 节点电压法（复数）：Ra、Rb 串联，中点 M 经 Cc（2C）接地；Ca、Cb 串联，中点 N 经 Rc（R/2）接地。
    RL 为输出端负载（None = 空载），Rs 为信号源内阻。返回输出 / 源电压（复数）。"""
    w = 2 * PI * np.asarray(f, float)
    res = []
    for wk in w:
        s = 1j * wk
        gL = 0 if RL is None else 1 / RL
        # 未知量 [vin, vm, vn, vo]；源 1 V 经 Rs
        gs = 1e9 if Rs == 0 else 1 / Rs
        Y = np.array([
            [gs + 1 / Ra + s * Ca, -1 / Ra, -s * Ca, 0],
            [-1 / Ra, 1 / Ra + 1 / Rb + s * Cc, 0, -1 / Rb],
            [-s * Ca, 0, s * Ca + s * Cb + 1 / Rc, -s * Cb],
            [0, -1 / Rb, -s * Cb, 1 / Rb + s * Cb + gL]], complex)
        b = np.array([gs, 0, 0, 0], complex)
        res.append(np.linalg.solve(Y, b)[3])
    return np.array(res)


def twint_ode(f, R, C, amp=1.0, ncyc=20, spc=1000):
    """双 T 的逐步算法（输出空载）：状态是 2C 上的电压 vM、Ca 上的电压 ua（输入 − N）、Cb 上的电压 ub（N − 输出）。
    每一步：先由状态求出各节点电压，再按「流进 = 流出」求出各电容电流，电压变化 = 电流 × dt / 电容。返回稳态输出幅度。"""
    dt = 1 / (f * spc)
    vM = ua = ub = 0.0
    vo_tail = []
    n = ncyc * spc
    for k in range(n):
        vi = amp * np.sin(2 * PI * f * k * dt)
        vN = vi - ua
        vo = vN - ub
        i_b = (vo - vM) / R          # 输出端空载：经 Cb 流进输出端的电流，全部经 Rb 流到 M
        i_a = i_b + vN / (R / 2)     # N 点：Ca 送来的电流 = Cb 带走的 + R/2 流到地的
        i_M = (vi - vM) / R + (vo - vM) / R   # M 点：两只 R 送来的电流都流进 2C
        vM += i_M / (2 * C) * dt
        ua += i_a / C * dt
        ub += i_b / C * dt
        if k >= n - 2 * spc:
            vo_tail.append(vo)
    t = np.array(vo_tail)
    return (t.max() - t.min()) / 2


def db(x):
    return 20 * np.log10(np.abs(x))


def f3db(fs_, mag, peak):
    """在扫频结果里找幅度 = peak/√2 的上、下两个频率（线性插值）。"""
    lvl = peak / np.sqrt(2)
    i0 = int(np.argmax(mag))
    lo = np.interp(lvl, mag[:i0 + 1], fs_[:i0 + 1])
    hi = np.interp(-lvl, -mag[i0:], fs_[i0:])
    return lo, hi


# ---------------- 本节用到的元件值 ----------------
C_BP = 10e-9
R1_BP, R2_BP, R3_BP = 82e3, 160e3, 1.6e3          # E 系列实际值（实验用）
R_TT, C_TT = 33e3, 100e-9                          # 双 T：R/2 = 两只 33 kΩ 并联，2C = 两只 100 nF 并联


def main():
    R1, R2, R3 = mfb_design(1e3, 5, 1, C_BP)
    print(f"[数值] 设计 1 kHz、Q=5、A=1、C=10 nF：R1={R1/1e3:.1f} kΩ，R2={R2/1e3:.1f} kΩ，R3={R3/1e3:.3f} kΩ")
    assert abs(R1 - 79.6e3) < 0.1e3 and abs(R2 - 159.2e3) < 0.1e3 and abs(R3 - 1.624e3) < 0.002e3
    f0, Q, A0, BW = mfb_params(R1_BP, R2_BP, R3_BP, C_BP)
    print(f"[数值] 实验值 82k/160k/1.6k/10nF：f0={f0:.1f} Hz，Q={Q:.2f}，A0={A0:.3f}，BW={BW:.1f} Hz")
    for f in (50, 200, 500, 800, 900, 1000, 1100, 1200, 2000, 5000):
        print(f"[数值]   {f:>5d} Hz：|H| = {bp_mag(f, f0, Q, A0):.4f}（{db(bp_mag(f, f0, Q, A0)):+.1f} dB）")
    for f in (500, 1000, 2000):
        print(f"[数值]   逐步积分（Euler）{f} Hz：{mfb_ode(f, R1_BP, R2_BP, R3_BP, C_BP):.4f}")
    ft = twint_f0(R_TT, C_TT)
    print(f"[数值] 双 T 33 kΩ/100 nF：f0 = {ft:.2f} Hz")
    for f in (10, 20, 48.2, 50, 60, 100, 200, 1000):
        print(f"[数值]   双 T {f:>6g} Hz：{twint_mag(f, ft):.4f}（{db(twint_mag(f, ft) + 1e-12):+.1f} dB）")

    # 练习 4（page3）：1 kHz、Q值 = 10、A = 1 的 MFB，用 LM358B（GBW 1.2 MHz）与经典 LM358（0.7 MHz）
    r1, r2, r3 = mfb_design(1e3, 10, 1, C_BP)
    fx = np.linspace(800, 1200, 40001)
    for name, g in (("理想", None), ("LM358B 1.2 MHz", 1.2e6), ("LM358 0.7 MHz", 0.7e6)):
        m = np.abs(mfb_nodal(fx, r1, r2, r3, C_BP, C_BP, gbw=g))
        lo, hi = f3db(fx, m, m.max())
        print(f"[数值] 练习 4，{name}：峰值在 {fx[np.argmax(m)]:.1f} Hz，带宽 {hi-lo:.1f} Hz，1 kHz 处开环增益 {('—' if g is None else f'{g/1e3:.0f}')}")
    r1, r2, r3 = mfb_design(10e3, 10, 1, C_BP / 10)
    fx = np.linspace(7000, 12000, 50001)
    m = np.abs(mfb_nodal(fx, r1, r2, r3, C_BP / 10, C_BP / 10, gbw=1.2e6))
    print(f"[数值] 对比：10 kHz、Q值 = 10、LM358B：峰值在 {fx[np.argmax(m)]:.0f} Hz（偏 {(fx[np.argmax(m)]/1e4-1)*100:.1f}%）")
    # 电阻误差对中心频率的影响（page3 故障表旁）
    for q in (2, 5, 10, 20):
        r1, r2, r3 = mfb_design(1e3, q, 1, C_BP)
        base = mfb_params(r1, r2, r3, C_BP)[0]
        d1 = mfb_params(r1 * 1.01, r2, r3, C_BP)[0] / base - 1
        d2 = mfb_params(r1, r2 * 1.01, r3, C_BP)[0] / base - 1
        d3 = mfb_params(r1, r2, r3 * 1.01, C_BP)[0] / base - 1
        print(f"[数值] Q值 = {q}：R1/R2/R3 各偏大 1% → f0 偏 {d1*100:+.2f}% / {d2*100:+.2f}% / {d3*100:+.2f}%；"
              f"R2 偏 1% 的偏移 = 带宽的 {abs(d2)*q*100:.1f}%")


if __name__ == "__main__":
    main()


# ---------------- 审阅后补充的数值（教师必改-08/09/10/11、建议-03/04/06，工程笔记第 3 条） ----------------
def par(*rs):
    """几只电阻并联。"""
    return 1 / sum(1 / r for r in rs)


def null_scan(Ra, Rb, Rc, Ca, Cb, Cc, lo=30.0, hi=70.0, n=40001):
    """在 lo～hi Hz 细扫双 T，返回（坑底频率，坑底值）。"""
    f = np.linspace(lo, hi, n)
    m = np.abs(twint_nodal(f, Ra, Rb, Rc, Ca, Cb, Cc))
    i = int(np.argmin(m))
    return f[i], m[i]


def extra():
    out = {}
    # 必改-08：双 T 微调。Ra、Rb 各并 1 MΩ，R/2（R4∥R5）再并 470 kΩ
    ra = par(R_TT, 1e6); rc = par(R_TT / 2, 470e3)
    fn, mn = null_scan(ra, ra, rc, C_TT, C_TT, 2 * C_TT)
    h50 = abs(twint_nodal(np.array([50.0]), ra, ra, rc, C_TT, C_TT, 2 * C_TT)[0])
    h1k = abs(twint_nodal(np.array([1000.0]), ra, ra, rc, C_TT, C_TT, 2 * C_TT)[0])
    print(f"[数值] 双 T 微调：33k∥1M = {ra/1e3:.2f} kΩ，16.5k∥470k = {rc/1e3:.2f} kΩ → 坑底 {fn:.2f} Hz，50 Hz 处 {h50:.5f}，1 kHz 处 {h1k:.3f}")
    assert abs(fn - 49.85) < 0.1 and abs(h50 - 0.00157) < 0.0002 and abs(h1k - 0.981) < 0.002
    out.update(trim_f=fn, trim_50=h50, trim_1k=h1k)
    # 必改-08：R3 = 1 kΩ + 0～2 kΩ 电位器
    for r3, fe, qe in ((1e3, 1266, 6.36), (3e3, 740, 3.72)):
        f_, q_, _, _ = mfb_params(R1_BP, R2_BP, r3, C_BP)
        print(f"[数值] R3 = {r3/1e3:g} kΩ：f0 = {f_:.0f} Hz，Q值 = {q_:.2f}")
        assert abs(f_ - fe) < 1 and abs(q_ - qe) < 0.01
    # page3 第一节：f0 = 1/(2πC·sqrt(R2·(R1∥R3)))，与 mfb_params 一致
    f_th = 1 / (2 * np.pi * C_BP * np.sqrt(R2_BP * par(R1_BP, R3_BP)))
    print(f"[数值] 戴维南写法 f0 = {f_th:.1f} Hz（R1∥R3 = {par(R1_BP, R3_BP):.0f} Ω）")
    assert abs(f_th - mfb_params(R1_BP, R2_BP, R3_BP, C_BP)[0]) < 0.01
    # page3 第三节：三处并联后都减小约 3%
    k1, k2 = 1 - ra / R_TT, 1 - rc / (R_TT / 2)
    print(f"[数值] 微调比例：Ra/Rb 减小 {k1*100:.1f}%，R/2 减小 {k2*100:.1f}%")
    assert 0.025 < k1 < 0.035 and 0.025 < k2 < 0.035
    # 必改-09：练习 1，挪到 1200 Hz，只换 R3
    f_t = 1200.0
    r3 = 1 / (R2_BP * (2 * PI * C_BP * f_t) ** 2 - 1 / R1_BP)
    f0, q, a0, bw = mfb_params(R1_BP, R2_BP, 1.1e3, C_BP)
    print(f"[数值] 练习 1：R3 理论 {r3:.0f} Ω；取 1.1 kΩ → f0 = {f0:.0f} Hz，Q值 = {q:.2f}，BW = {bw:.1f} Hz，峰值 {a0:.3f}")
    assert abs(r3 - 1114) < 2 and abs(f0 - 1208) < 1 and abs(q - 6.07) < 0.01
    # 必改-10：练习 3，所有元件一起偏大 5%
    k = 1.05
    fn5, mn5 = null_scan(R_TT * k, R_TT * k, R_TT / 2 * k, C_TT * k, C_TT * k, 2 * C_TT * k)
    h50_5 = abs(twint_nodal(np.array([50.0]), R_TT * k, R_TT * k, R_TT / 2 * k, C_TT * k, C_TT * k, 2 * C_TT * k)[0])
    print(f"[数值] 练习 3：全部偏大 5% → 坑底 {fn5:.2f} Hz（48.23/1.05² = {twint_f0(R_TT, C_TT)/k**2:.2f}），坑底值 {mn5:.1e}，50 Hz 处 {h50_5:.3f}")
    assert abs(fn5 - 43.7) < 0.1 and abs(h50_5 - 0.067) < 0.003
    # 必改-11：新例 3，500 Hz、Q值 3、A 1、C 22 nF
    r1, r2, r3 = mfb_design(500, 3, 1, 22e-9)
    print(f"[数值] 例 3：R2 = {r2/1e3:.1f} kΩ，R1 = {r1/1e3:.1f} kΩ，R3 = {r3/1e3:.2f} kΩ")
    for r3s in (2.4e3, 2.7e3):
        f0, q, a0, bw = mfb_params(43e3, 91e3, r3s, 22e-9)
        print(f"[数值] 例 3 标准值 43k/91k/{r3s/1e3:g}k/22 nF：f0 = {f0:.0f} Hz，Q值 = {q:.2f}，峰值 {a0:.3f}，BW = {bw:.0f} Hz")
    f0, q, a0, bw = mfb_params(43e3, 91e3, 2.4e3, 22e-9)
    assert abs(r2 - 86.8e3) < 0.1e3 and abs(r3 - 2.55e3) < 0.01e3 and abs(f0 - 503) < 1 and abs(q - 3.16) < 0.01
    # 建议-06：思考题 2，R3 = 2.2 kΩ
    f0, q, a0, bw = mfb_params(R1_BP, R2_BP, 2.2e3, C_BP)
    print(f"[数值] 思考题 2：R3 = 2.2 kΩ → f0 = {f0:.0f} Hz，Q值 = {q:.2f}，峰值 {a0:.3f}，BW = {bw:.1f} Hz")
    # 建议-03：中心频率处反馈系数（输入接地，从输出经网络回到反相端）
    f0, q, a0, bw = mfb_params(R1_BP, R2_BP, R3_BP, C_BP)
    s = 2j * PI * f0
    za = 1 / (1 / R1_BP + 1 / R3_BP)                  # A 点经 R1∥R3 对地（输入短路）
    # 输出 → C2 → A；A → C1 → N；N → R2 → 输出。求 vN/vo（N 点无其他负载）
    # 节点 A：(vo − va) sC = va/za + (va − vn) sC；节点 N：(va − vn) sC = (vn − vo)/R2
    M = np.array([[1 / za + 2 * s * C_BP, -s * C_BP], [s * C_BP, -s * C_BP - 1 / R2_BP]], complex)
    b = np.array([s * C_BP, -1 / R2_BP], complex)
    va, vn = np.linalg.solve(M, b)
    print(f"[数值] 建议-03：f0 处反馈只剩 1/{1/abs(vn):.2f}（2Q² = {2*q*q:.1f}，2Q²+1 = {2*q*q+1:.1f}）")
    assert abs(1 / abs(vn) - 51.98) < 0.1
    # 工程笔记第 3 条：LM358（GBW 0.7 MHz）与 LM358B（1.2 MHz）下的峰值频率
    fx = np.linspace(900, 1100, 20001)
    for g in (0.7e6, 1.2e6):
        m = np.abs(mfb_nodal(fx, R1_BP, R2_BP, R3_BP, C_BP, C_BP, gbw=g))
        print(f"[数值] 实验电路，GBW {g/1e6:.1f} MHz：峰值在 {fx[np.argmax(m)]:.1f} Hz，峰值 {m.max():.4f}")
    # 建议-04：40 kHz、Q值 5、A 1，C = 1 nF，LM358B
    r1, r2, r3 = mfb_design(40e3, 5, 1, 1e-9)
    fx = np.linspace(20e3, 60e3, 40001)
    mi = np.abs(mfb_nodal(fx, r1, r2, r3, 1e-9, 1e-9))
    for g in (1.2e6, 10e6):
        m = np.abs(mfb_nodal(fx, r1, r2, r3, 1e-9, 1e-9, gbw=g))
        lo, hi = f3db(fx, m, m.max())
        print(f"[数值] 练习 5：40 kHz、Q值 5，GBW {g/1e6:g} MHz：开环增益 {g/40e3:.0f}，峰值 {m.max():.3f} 在 {fx[np.argmax(m)]/1e3:.1f} kHz，"
              f"BW {(hi-lo)/1e3:.2f} kHz（理想 {mi.max():.3f}、40.0 kHz、8.00 kHz）")
    # 学生必改-5：方波输出的交流挡读数（有效值）
    print(f"[数值] 方波 ±0.30 V 进带通，输出正弦幅度 0.373 V → 交流挡（有效值）约 {0.373/np.sqrt(2):.3f} V")
    # 测量表的比值（应读的输出/输入）
    for f in (500, 900, 1000, 1100, 2000, 200, 5000):
        print(f"[数值] 比值 {f} Hz：{bp_mag(f, f0, q, a0):.3f}")
    for f in (50, 100, 200, 1000):
        print(f"[数值] 双 T 比值 {f} Hz：{twint_mag(f, twint_f0(R_TT, C_TT)):.4f}")
    # 教师第 2 轮新建议-01：第 ⓪ 步「1 kHz 已偏小」时第 ⑨ 步改用 500 Hz
    h500 = twint_mag(500, twint_f0(R_TT, C_TT))
    print(f"[数值] 双 T 比值 500 Hz（第 ⑨ 步备用）：{h500:.3f}")
    assert abs(h500 - 0.932) < 0.001
    return out


if __name__ == "__main__":
    extra()
