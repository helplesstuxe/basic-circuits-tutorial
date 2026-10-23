# 14 电压比较器 · 资料笔记（作者 C）

## 已打开并引用的资料
- TI SBOA313A《Non-Inverting Comparator with Hysteresis Circuit》https://www.ti.com/lit/an/sboa313a/sboa313a.pdf
  - TLV7041 开漏输出需上拉；VH 1.7 V / VL 1.3 V / Vhys 400 mV，3 V 电源，R1 273k、R2 2M、R3 100k 上拉、R4 1.01M / R5 1M 分压出 VTH。
  - 设计步骤：输出低时 VTH = VH·R2/(R1+R2)；输出高时叠加法求 VL。与本节公式一致（3×273/2000 ≈ 0.41 V）。
  - 「噪声、信号变化或慢变信号在单一门限下会造成不希望的输出翻转」。
- TI SLOA067《Op Amp and Comparators – Don't Confuse Them!》https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/14/op-amp-vs-comparators.pdf
  - 比较器输出级为饱和工作优化；运放输出管是线性管，开环时在线性区停留久、沿慢；饱和恢复时间不可预测（微秒到几十毫秒），厂家不保证开环工作。
  - 回差可消除慢变输入的抖动；作者认为 1%～2% 足够（本节在 page3 说明为何取更大）。
- TI LM393 数据手册 SLCS005AH https://www.ti.com/lit/ds/symlink/lm393.pdf
  - 开集电极输出，可电平转换，多输出并联实现「与」；单电源 2～36 V；响应时间典型 1.3 μs（B 版 1 μs）；
  - 共模范围 25 °C 上限 (V+)−1.5 V，全温度 (V+)−2.0 V；注释：只要一个输入在范围内输出即正确；
  - VOL：ISINK ≤ 4 mA 时典型 110 mV、最大 400 mV；输入偏置电流典型 25 nA（B 版 3.5 nA）；
  - 上升时间 τR ≈ RPULLUP × CL；布线：加旁路电容，输出线远离反相输入。
- 本书 P3：LM358 输出高电平约比正电源低 1.5 V；开环饱和；无负反馈时虚短不成立。

## 仿真设计
- code/14_sim.py：5 V、Vref 2.5 V、R1 10k、R2 100k、R3 2.2k → V_H 2.750 V、V_L 2.255 V、回差 0.495 V；
  20 s 三角形输入 2→3→2 V，dt 10 ms，σ 40 mV，seed 1：普通 98 次、施密特 2 次（7.08 s 翻高、16.67 s 翻低）。
- 扫描：R2 1M…68k（回差 0.05…0.72 V），σ 20/40/80 mV → 达到 2 次所需回差 0.11/0.23/0.49 V（约 6σ，经验值，仅对本例高斯噪声）。
- 温度传感器 0.1 V/°C 为示意值，未对应具体型号。

## 待核实
- 无。
