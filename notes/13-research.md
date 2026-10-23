# 13 微分电路 · 调研笔记（作者 C）

## 已打开并引用的资料
- TI SBOA276C *Differentiator Circuit*：https://www.ti.com/lit/an/sboa276c/sboa276c.pdf（本地 /workspace/authorC/refs/sboa276c.pdf）
  - "The ideal differentiator circuit is fundamentally unstable and requires the addition of an input resistor, a feedback capacitor, or both, to be stable. The components required for stability limit the bandwidth..."
  - Vout = −R2·C1·dVin/dt；示例 R2 499 kΩ、C1 15 nF、R1 1 kΩ、TLV9061（10 MHz），5 V 单电源，R3 = R4 = 100 kΩ 给出 2.5 V 参考；fMin 100 Hz、fMax 2.5 kHz。
  - Design notes：R2 取大以免 C1 过大；R2 并电容滤高频噪声，从其截止频率约半个数量级（≈3.5 倍）处开始削弱微分作用；同相端加参考电压可单电源工作；保持在线性输出摆幅内。
  - Design steps：最低微分频率比最低工作频率低至少半个数量级（C1 ≥ 11.1 nF → 15 nF）；上限截止频率比最高工作频率高至少半个数量级（R1 ≤ 1.2 kΩ → 1 kΩ）；GBP > (R1+R2)/(2π·R1²·C1) > 5.3 MHz；fc = 1/(2π·R2·CF)。
- LM358B GBW 约 1.2 MHz 沿用 P3 页。

## 设计取值（本节）
C 100 nF、Rf 10 kΩ（Rf·C 1 ms，与 12 节三角波斜率 ±1 V/ms 配合得到 ±1 V 方波）；实用版 R1 1 kΩ、Cf 10 nF（R1·C = Rf·Cf = 0.1 ms，f_H ≈ 1.59 kHz，高频增益封顶 Rf/R1 = 10）。干扰 10 mV、20 kHz。本例 GBP 条件 ≈ 17.5 kHz。
教学取值优先波形可读，未完整套用 TI「半个数量级」流程，page3 已说明。

## 仿真结果（code/13_sim.py、code/figs/13_figs.py）
- 斜率图：+2 / 0 / −0.5 V/ms → −2.0 / 0.0 / +0.5 V。三角波 → ±1.00 V 方波。
- 噪声：理想微分器干扰峰峰 2.51 V（理论 2·2π·20k·1ms·10mV）；实用版 16 mV；实用版上升段 −1.00 V。
- 1.2 MHz GBW 运放模型：理想微分器拐角后冲到 2.80 V、振铃 13.8 kHz（估算 √(GBW/(2π·Rf·C)) = 13.8 kHz，ζ≈0.006）；实用版最高 1.00 V、无振铃。
- R1 扫描（理想运放、无 Cf）：100/300/1k/3k Ω → 干扰 1573/645/199/67 mV，边沿 90% 用时 0.02/0.07/0.23/0.69 ms（≈2.3·R1·C）。
- page2 代码块（只串 R1、Euler）：平顶（1.5–2 ms）波动理想 2.51 V、串 R1 0.21 V。

## 附图说明
source-20-circuits 附图中一格「微分电路」画成输入 R、反馈 C，实为积分器拓扑；page1 已用提示框说明，并指出实用微分器反馈中的电容只是与 Rf 并联的小 Cf。

## 未用 / 待核实
无「待核实」标记。
