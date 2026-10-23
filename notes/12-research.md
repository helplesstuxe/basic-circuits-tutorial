# 12 积分电路 · 调研笔记（作者 C）

## 已打开并引用的资料
- TI SBOA275B *Integrator Circuit*：https://www.ti.com/lit/an/sboa275b/sboa275b.pdf（本地 /workspace/authorC/refs/sboa275b.pdf）
  - 理想积分器会依输入失调电压极性饱和到电源轨，需要反馈电阻 R2 提供稳定直流工作点；R2 限制积分的最低频率。
  - Vout = −1/(R1C1)∫Vin dt；示例 R1 100 kΩ、C1 1.59 nF（f0dB 1 kHz）、R2 100 MΩ、TLV9002 ±2.5 V，仿真中设 Vos −740 μV。
  - Design notes：R2 尽量大；选 CMOS 运放减小偏置电流误差；GBP ≥ 10·fMax；必要时同相端接可调基准抵消失调；常放在更大的伺服环路里由外环提供直流反馈。
  - 第 3 步 "lower cutoff a decade less than the minimum operating frequency"。注意：该文档 R2 公式的数值（10 Hz vs 表中 fMin 100 Hz）前后不一致，教程只引用"低十倍"的原则和示例取值，没有照抄其公式。
- 运放输出摆幅 / GBW 数量级沿用 P3 页（LM358B 数据手册，P3 作者已引用）。

## 设计取值（本节）
R 10 kΩ、C 100 nF（RC 1 ms）、Rf 1 MΩ（Rf·C 0.1 s，f_c ≈ 1.6 Hz）；输出极限按 ±15 V 供电示意 ±13.5 V；±1 V 500 Hz 方波 + 20 mV 偏置。

## 仿真结果（code/12_sim.py、code/figs/12_figs.py）
- 方波 → 三角波峰峰 1.00 V；理想积分器 627 ms 撞 −13.5 V（漂移 20 V/s）；Rf 1 MΩ 时中心 −2.00 V。
- Rf 扫描：10k/100k/1M/10M → 中心 −0.02/−0.20/−2.00/−13.01 V（10 MΩ 已削顶）；500 Hz 下 Rf 10 kΩ 峰峰 0.93 V（变形），100 kΩ 与 1 MΩ 为 1.00 V。
- RC 扫描：0.05/1/10 ms → 峰峰 20.00（削平）/1.00/0.10 V。

## 未用 / 待核实
无「待核实」标记。
