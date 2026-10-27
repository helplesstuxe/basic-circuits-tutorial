"""30 仪表放大器与电桥：页面里用到的全部数值（理想运放 + 电阻公式），逐条打印。
运行：/workspace/circuits-venv/bin/python code/30_sim.py
SPICE 复核：在仓库根目录运行 python spice/30/run.py（约 4 分钟，需要 spice/models）。
"""
import math

# ---------- 1. 电桥 ----------
def bridge(vex, r, dr):
    """四臂都是 r 的惠斯通电桥，右下臂变成 r + dr：返回精确差压 Vb − Va 与近似 vex·dr/(4r)。"""
    va = vex * r / (r + r)
    vb = vex * (r + dr) / (r + r + dr)
    return vb - va, vex * dr / (4 * r)

VEX, R = 9.0, 10e3
print("== 电桥（9 V 激励，四臂 10 kΩ，右下臂串 RX）==")
BR = {}
for rx in (100, 220, 470, 1000):
    ex, ap = bridge(VEX, R, rx)
    BR[rx] = ex
    print(f"RX = {rx:4d} Ω：精确 {ex*1e3:7.3f} mV，近似 {ap*1e3:7.3f} mV，近似偏大 {(ap/ex-1)*100:+.2f}%")
ex5, ap5 = bridge(5.0, 1e3, 10)   # 5 V、1 kΩ 桥、1% 变化（压力传感器量级）
print(f"5 V 激励、ΔR/R = 1%：精确 {ex5*1e3:.2f} mV，近似 {ap5*1e3:.2f} mV")
# 比例测量：激励从 9 V 掉到 8 V，差压同比例变小
print(f"激励 8 V、RX 100 Ω：{bridge(8.0, R, 100)[0]*1e3:.2f} mV（9 V 时 {BR[100]*1e3:.2f} mV，比值 {bridge(8.0,R,100)[0]/BR[100]:.4f}）")

# ---------- 2. 三运放仪表放大器 ----------
def g1(rf, rg):
    return 1 + 2 * rf / rg

G1 = g1(10e3, 1e3)
print("\n== 仪表放大器（R = 10 kΩ，RG = 1 kΩ，差分级倍数 1）==")
print(f"第一级倍数 1 + 2R/RG = {G1:.0f}")
for rx in (100, 220, 470):
    vd = BR[rx]
    i = vd / 1e3
    a1 = 4.5 - i * 10e3
    a2 = 4.5 + vd + i * 10e3
    print(f"RX = {rx}：Vd {vd*1e3:.2f} mV，RG 电流 {i*1e6:.2f} μA，A1 出 {a1:.4f} V，A2 出 {a2:.4f} V，Vo−V_MID = {G1*vd:.4f} V")
print(f"拔掉 RG（倍数 1）、RX 470：Vo−V_MID = {BR[470]:.4f} V")
for rg in (2.2e3, 470, 100):
    print(f"RG = {rg:g} Ω：倍数 {g1(10e3, rg):.2f}")
print(f"INA333：RG = 1 kΩ → G = 1 + 100k/RG = {1+100e3/1e3:.0f}；要 G = 21 → RG = {100e3/20:.0f} Ω")
print(f"INA126：G = 5 + 80k/RG；RG = 5 kΩ → {5+80e3/5e3:.0f}；不接 RG → 5")

# ---------- 3. 共模抑制：先打印 MT-061 的近似式（只作对照，页面不用），再打印页面用的精确式 ----------
def cmr_diff(kr, gdiff=1.0):
    """差分级（倍数 gdiff）电阻最坏失配 Kr（四只合计按 4Kr）时的 CMR，dB。MT-061：20lg((1+G)/(4Kr))。"""
    return 20 * math.log10((1 + gdiff) / (4 * kr))

print("\n== 共模抑制比 ==")
print("（下面 4 行是 MT-061 近似式 20lg((1+G)/(4Kr))，只作对照；页面和图 30-p2-3 用的是后面 acm_exact 的精确值）")
cases = [("一只电阻 +0.1%", 0.001 / 4), ("一只电阻 +1%", 0.01 / 4), ("四只 1% 最坏", 0.01), ("四只 5% 最坏", 0.05)]
for name, kr in cases:
    c = cmr_diff(kr)
    print(f"[近似] 差分级（倍数 1）{name}：CMR {c:.1f} dB，共模倍数 {10**(-c/20):.5f}；前面加 G1 = 21：{c + 20*math.log10(G1):.1f} dB")
print(f"G1 = 21 相当于多 {20*math.log10(G1):.1f} dB")
# 面包板共模测试：J2 短接两中点，RC 4.7k 下拉/上拉
rth = 2.5e3                        # 四只 10k 并在一起（J2 短接后）的戴维南电阻
vlo = 4.5 * 4.7e3 / (rth + 4.7e3)
vhi = 9 - vlo
print(f"共模测试：RC 下拉 {vlo:.3f} V，上拉 {vhi:.3f} V，相差 {vhi-vlo:.3f} V")
def acm_exact(r1, r2, r3, r4):
    """四电阻差分级（R1 输入→反相端，R2 反馈，R3 输入→同相端，R4 同相端→参考）的精确共模倍数。"""
    return r4 / (r3 + r4) * (1 + r2 / r1) - r2 / r1

for name, rr in [("R10 串 100 Ω（一只 +1%）", (10e3, 10e3, 10e3, 10.1e3)),
                 ("四只 1% 最坏", (10.1e3, 9.9e3, 9.9e3, 10.1e3)),
                 ("四只 5% 最坏", (10.5e3, 9.5e3, 9.5e3, 10.5e3))]:
    acm = acm_exact(*rr)
    print(f"  {name}：精确共模倍数 {acm:.5f}，输出变化 {acm*(vhi-vlo)*1e3:.1f} mV，"
          f"差分级 CMR {20*math.log10(1/acm):.1f} dB，整机（G1 = 21）{20*math.log10(G1/acm):.1f} dB")

# ---------- 4. 电磁流量计 ----------
print("\n== 电磁流量计电极（ADI 文章数值）==")
print(f"100 dB 抑制：0.3 V 共模 → {0.3/10**(100/20)*1e6:.1f} μV")
print(f"灵敏度 150～200 μV/(m/s)：1 m/s 时 {150}～{200} μV")
# 第一级余量：9 V 单电源，V_MID = 4.5 V，LM358 输出最高约 7.5 V（9 V − 1.5 V），最低取 0.1 V（带 10k 负载）
for vdc in (0.1, 0.2, 0.5, 1.0, 2.0):
    gmax = 2 * (7.5 - 4.5) / vdc
    print(f"电极直流差 {vdc} V：第一级最多 {gmax:.1f} 倍（输出不碰 7.5 V）")

# ---------- 5. 差压流量计开方 ----------
print("\n== 差压流量计 Q_V ∝ √ΔP（Q_V：体积流量）==")
for q in (1.0, 0.5, 0.1):
    print(f"流量 {q*100:.0f}% → 差压 {q*q*100:.1f}%")
dp_err = 0.001             # 差压测量误差 0.1% 满量程
for q in (1.0, 0.3, 0.1):
    rel = 0.5 * dp_err / (q * q)
    print(f"流量 {q*100:.0f}%：差压误差 0.1% 满量程 → 流量相对误差 {rel*100:.2f}%")

# ---------- 6. 典型错误：16 节的单运放差分（倍数 10）直接接电桥 ----------
print("\n== 单运放差分放大直接接电桥（Ra=Rc=10k 输入，Rb=Rd=100k，参考 V_MID=4.5 V，理想运放）==")
def single_diff(vex, dr, ra, rb, rc, rd, vcm_shift=0.0, vref=4.5, r=10e3):
    """电桥两中点看成戴维南源（电压 + 内阻），再接四电阻差分放大；返回 Vo − V_MID。"""
    vta, rta = vex / 2 + vcm_shift, r / 2                       # 左中点：4.5 V，内阻 10k∥10k
    vtb = vex * (r + dr) / (2 * r + dr) + vcm_shift             # 右中点
    rtb = r * (r + dr) / (2 * r + dr)
    vp = (vtb * rd + vref * (rtb + rc)) / (rtb + rc + rd)       # 同相端：分压
    vo = vp + (vp - vta) * rb / (rta + ra)                      # 反相端虚短，电流 (vp − vta)/(rta+ra)
    return vo - vref
d100 = 9.0 * 100 / (2 * 20100)
v = single_diff(9.0, 100, 10e3, 100e3, 10e3, 100e3)
print(f"ΔR=100 Ω：设计想要 10 × {d100*1e3:.2f} mV = {10*d100*1e3:.1f} mV，实际 {v*1e3:.1f} mV（倍数只剩 {v/d100:.2f}）")
w = (10.1e3, 99e3, 9.9e3, 101e3)                                 # 四只 1% 最坏
v0 = single_diff(9.0, 0, *w)
v1 = single_diff(9.0, 0, *w, vcm_shift=1.5625)
print(f"四只 1% 最坏、电桥平衡：两中点一起从 4.5 V 升到 6.06 V，输出漂 {(v1-v0)*1e3:.1f} mV；"
      f"折合输入 {(v1-v0)/(v/d100)*1e3:.2f} mV，是 ΔR=100 Ω 信号的 {(v1-v0)/v*100:.0f}%")
acm = acm_exact(10.1e3, 9.9e3, 9.9e3, 10.1e3)
print(f"对比：三运放（G1=21，差分级四只 1% 最坏）同样 1.56 V 共模变化，输出漂 {acm*1.5625*1e3:.1f} mV，"
      f"折合输入 {acm*1.5625/21*1e3:.2f} mV")

# ---------- 7. 中点参考：分压 + 跟随器 ----------
print("\n== 中点参考 V_MID ==")
rl = 1e3
par = rl * 10e3 / (rl + 10e3)
print(f"只用分压（10k/10k）接 1 kΩ 负载：{9*par/(10e3+par):.2f} V；加跟随器后理想仍是 4.50 V，跟随器输出电流 {4.5/rl*1e3:.1f} mA")

# ---------- 8. 比例测量 ----------
print("\n== 比例测量：模数转换参考取自激励的一半 ==")
for vex in (9.0, 8.0):
    vo = 21 * vex * 100 / (2 * 20100)
    print(f"激励 {vex} V：INA 输出（对 V_MID）{vo:.4f} V，参考 {vex/2:.2f} V，比值 {vo/(vex/2):.5f}")

# ---------- 9. page2 例1：RG = 2 kΩ，RX = 220 Ω ----------
print("\n== 例1：RG = 2 kΩ（倍数 11），RX = 220 Ω ==")
g = 1 + 2 * 10e3 / 2e3
vd = 9.0 * 220 / (2 * (20e3 + 220))
i = vd / 2e3
print(f"倍数 {g:.0f}，差压 {vd*1e3:.3f} mV，RG 电流 {i*1e6:.2f} μA，"
      f"A1 {4.5 - i*10e3:.4f} V，A2 {4.5 + vd + i*10e3:.4f} V，Vo−V_MID {g*vd:.4f} V")

# ---------- 10. REF（R10 下端）不用跟随器、直接接分压点会怎样（page4 思考题 3）----------
print("\n== REF 源内阻串进 R10 ==")
for rs in (5e3, 50.0):
    a = acm_exact(10e3, 10e3, 10e3, 10e3 + rs)
    print(f"REF 源内阻 {rs:g} Ω：差分级共模倍数 {a:.4f}，差分级 CMRR {20*math.log10(1/abs(a)):.1f} dB")
print(f"第 15 步 R10 串 100 Ω：共模变化 3.125 V → ΔVo {acm_exact(10e3,10e3,10e3,10.1e3)*3.125*1e3:.1f} mV")

# ---------- 11. 运放失调（page3 故障排查补充）----------
print("\n== LM358 失调经第一级放大 ==")
vos_max = 7e-3            # 经典 LM358 手册 V_OS 最大 7 mV（25 °C）
print(f"A1、A2 失调最坏相差 {2*vos_max*1e3:.0f} mV，乘 G1 = 21 → 输出偏 {2*vos_max*21:.3f} V；"
      f"对比 RX = 100 Ω 的信号 {21*9.0*100/(2*20100):.3f} V")

# ---------- 12. RG 错接到 0 V（page3 第一节，图 30-p3-1）----------
print("\n== RG 错接：A1 反相端经 RG 到 0 V ==")
va_m = 4.5
g_bad = 1 + 10e3 / 1e3
print(f"A1 变成同相放大 {g_bad:.0f} 倍（对 0 V）：想要 {g_bad*va_m:.1f} V，9 V 单电源 LM358 最高约 {9.0-1.5:.1f} V，顶死；A2 变跟随器")
assert abs(g_bad * va_m - 49.5) < 1e-9

# ---------- 13. R5 偏大 1%（page3 练习 5）----------
print("\n== R5 偏大 1% ==")
g_r5 = 1 + (10.1e3 + 10e3) / 1e3
print(f"差模倍数 1 + (R5 + R6)/RG = {g_r5:.1f}（原来 21）；共模时 RG 上无电流，第一级共模倍数仍是 1")
assert abs(g_r5 - 21.1) < 1e-9

# ---------- 14. 电子秤：称重传感器电桥 + INA333（page3 练习 6）----------
print("\n== 电子秤：350 Ω 全桥，5 V 激励，满量程 10 mV ==")
def ina333_rg(g):
    return 100e3 / (g - 1)
fs_mv, vexc = 10e-3, 5.0
g_want = 2.0 / fs_mv
rg_ideal = ina333_rg(g_want)
rg_std = 499.0                      # E96 系列里最接近 502.5 Ω 的值
g_real = 1 + 100e3 / rg_std
print(f"想要 ±2 V 摆幅：G = {g_want:.0f}，RG = 100k/{g_want-1:.0f} = {rg_ideal:.1f} Ω → 取 {rg_std:.0f} Ω，G = {g_real:.1f}")
print(f"满量程输出 {g_real*fs_mv:.3f} V（对 REF 2.5 V），即 {2.5+g_real*fs_mv:.3f} V 对地；输入共模 {vexc/2:.2f} V")
fs48 = fs_mv * 4.8 / 5.0
print(f"激励掉到 4.8 V：满量程 {fs48*1e3:.1f} mV，G = 200 时输出 {200*fs48:.2f} V（掉 4%）；比例测量 {200*fs48/(4.8/2):.3f} = {200*fs_mv/(5.0/2):.3f} 不变")
assert round(rg_ideal) == 503 and abs(g_real - 201.4) < 0.05 and abs(200 * fs48 - 1.92) < 1e-9
# 留空题：同一传感器，满量程想要 1 V
g2 = 1.0 / fs_mv
print(f"留空题：G = {g2:.0f}，RG = {ina333_rg(g2):.1f} Ω → 取 1.00 kΩ，G = {1+100e3/1e3:.0f}，满量程 {(1+100)*fs_mv:.3f} V")
# 变体：3.3 V 激励，2 mV/V，REF 1.65 V，想要 ±1.5 V
fs3 = 2e-3 * 3.3
g3 = 1.5 / fs3
rg3 = ina333_rg(g3)
g3r = 1 + 100e3 / 442
print(f"变体：满量程 {fs3*1e3:.1f} mV，G = {g3:.1f}，RG = {rg3:.1f} Ω → 取 442 Ω，G = {g3r:.1f}，满量程 {g3r*fs3:.3f} V（REF 1.65 V，对地 {1.65+g3r*fs3:.3f} V）")
