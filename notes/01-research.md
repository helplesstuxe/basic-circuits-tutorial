# 01 反相放大 · 研究笔记（作者 A）

## 理论
- TI SBOA270 反相放大电路手册 https://www.ti.com/lit/pdf/sboa270 ：设计例 −2 V/V（R1=10 kΩ、R2=20 kΩ）；输入阻抗由 R1 决定，应远大于信号源内阻；避免直接驱动容性负载。
- TI SBOA272 反相加法器电路手册 https://www.ti.com/lit/pdf/sboa272 ：多路输入各经电阻接到虚地，输出为加权和取负。
- TI SLAA068B https://www.ti.com/lit/an/slaa068b/slaa068b.pdf ：理想运放假设（与 P3 一致）。
- TI LM358B 数据手册 https://www.ti.com/lit/ds/symlink/lm358.pdf ：GBW 1.2 MHz、SR 0.5 V/μs、输出摆幅（正 −1.35~1.5 V，负 +0.1 V）。

## 实战代码
- 本节仿真直接用 numpy：V_o = clip(−Rf/R1·V_i, 下限, 上限)，见 code/01_sim.py。
- 带宽曲线只用幅值公式 |A_v|/√(1+(f/f_c)²)、f_c ≈ GBW/(1+|A_v|)（一阶近似，与 GBW 定义一致；不讲复数）。
- PySpice 运放示例（参考，未采用）https://pyspice.fabrice-salvaire.fr/releases/v1.5/examples/operational-amplifier/operational-amplifier.html

## 常见误区
- 忘了输出反相（示波器上看着「不对」）。
- 以为输入电阻很大：反相放大的输入电阻 ≈ R1，信号源内阻会吃掉增益（图 01-p3-1）。
- 输出削顶：倍数 × 输入超过摆幅。
- 增益设得太大导致高频不够（GBW）。
- 同相端浮空或单电源未偏置。
