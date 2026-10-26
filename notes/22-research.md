# 22 过载保护 · 调研笔记（作者 C）

## 已打开并引用的资料
- TI SBOA285A *Single-Supply, Low-Side, Unidirectional Current-Sensing Circuit*：https://www.ti.com/lit/an/sboa285a/sboa285a.pdf（本地 /workspace/authorC/refs/sboa285a.pdf）
  - 1 A 满量程、R1 = 250 mΩ 采样电阻（满量程 250 mV），增益 1 + R3/R2 = 19.6（715 Ω / 13.3 kΩ），输出 50 mV–4.9 V，TLV9062。
  - 采样电阻容差直接成为增益误差；小电流端失调电压的相对误差最大（Vos 0.3 mV 在 IiMin 10.2 mA 时约 12%）；R3 并电容可滤波。
- TI SBOA169B *Precision, low-side current measurement*：https://www.ti.com/lit/an/sboa169b/sboa169b.pdf
  - 高边 / 低边采样对比；低边共模电压接近地、电路简单；缺点是采样电阻压降使负载地相对电源地偏移，Rs 越小偏移越小。
- TI LM393 数据手册（SLCS005）：https://www.ti.com/lit/ds/symlink/lm393.pdf
  - 无后缀 LM393：VIO 典型 2 mV、25 °C 最大 5 mV；IIB 最大 250 nA；输入共模范围含地；开集电极输出。
- TI DRV8871 数据手册：https://www.ti.com/lit/ds/symlink/drv8871.pdf
  - OCP：电流超过 IOCP 持续 tOCP（1.5 μs）后关断全部 FET，tRETRY（3 ms）后自动重试，故障仍在则重复——打嗝式保护的实例。
- Infineon IRLZ44N 数据手册：https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlz44n-datasheet-en.pdf（Rds(on) 最大 25 mΩ @ VGS 5 V，沿用 06 节）
- ABB 热过载继电器手册：https://library.e.abb.com/public/a9cd1c3f07dc1870852573a300738595/1SXU106043B0201.pdf
  - 电机电流流过双金属片发热弯曲而脱扣；1.05 Ie 不脱扣、1.2 Ie 2 h 内脱扣；7.2 Ie 下 Class 10 为 4–10 s（10A/20/30 级另有规定）；手动 / 自动复位。
- Littelfuse *Fuseology Design Guide*：https://nationalfuse.com/wp-content/uploads/2023/03/Fuseology-Design-Guide.pdf
  - 正常负载不超过额定电流 75%（25 °C）；脉冲（启动冲击）I²t 不超过熔化 I²t 额定值的 20%；TCC 为平均曲线，规格给 135% / 200% 下最长熔断时间。
- 04 节 page3 引用的「热继电器不能做短路保护」出处，本节只转述并指回 04 节。

## 设计取值（本节）
12 V / 1 A 直流电机，堵转 5 A；低边 RS 0.1 Ω / 1 W；LM393 反相施密特：RA 33 kΩ（接 5 V）/ RB 1 kΩ，RH 100 kΩ，RPU 2.2 kΩ，输出直接驱动 IRLZ44N 栅极（正常 = 输出高 = 导通）；RF 10 kΩ、CF 10 μF，τ = 0.1 s。
门限：V_T = 0.147 V、R_T = 0.971 kΩ → V_H 193 mV（1.93 A）、V_L 146 mV（1.46 A），回差 47 mV。
启动模型：I = 1 + 4·e^(−t/20 ms) A。

## 仿真结果（code/22_sim.py、code/figs/22_figs.py）
- 开环慢变（1→2.6→1 A，σ 0.15 A 随机起伏，种子 3）：无回差翻转 10 次，有回差 2 次（3.95 s 跳、9.65 s 恢复）；page2 代码块结果相同。
- 堵转 5 A：26 ms 切断（公式 τ·ln((I−I0)/(I−Itrip)) 26.4 ms）。
- 闭环堵转：无回差每个 10 μs 步翻转（0.4 s 内 28803 次），平均电流 1.93 A；有回差打嗝：断 28.0 ms（= τ·ln(V_H/V_L)）、通 14.3 ms、占空比 34%、平均 1.73 A；锁存：1 次翻转，0 A。
- 反时限：τ = 10/47/100 ms → 5 A 堵转 2.6/12.4/26.4 ms，20 A 短路 0.50/2.35/5.00 ms。
- 启动（从 0 起）滤波后峰值：τ = 10/47/100 ms → 278/144/100 mV（10 ms 误跳）。
- RS 表（跳闸 1.93 A 不变）：0.01/0.05/0.1/0.5 Ω → 门限 19.3/96.4/192.7/963.6 mV，跳闸功耗 0.04/0.19/0.37/1.86 W，5 mV 失调占比 25.9/5.2/2.6/0.5%。
- LM393 IIB 250 nA × 10 kΩ = 2.5 mV。
- 练习 4：启动冲击超出稳态部分的 I²t = 16·τ_start = 0.32 A²s。

## 未用 / 待核实
无「待核实」标记。page3 提到「实际产品常再串保险丝作最后防线」「锁存可用 LM393 另一半 / 单片机 / 自锁继电器实现」为一般工程常识，未单独引用。
