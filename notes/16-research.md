# 16 差分放大 · 研究笔记（作者 A）

## 理论
- TI SBOA274 差分放大电路手册 https://www.ti.com/lit/pdf/sboa274 ：R2/R1 = R4/R3 时 Vo = (R2/R1)(V2 − V1)；CMRR 受电阻容差限制：1% 容差最坏约 34 dB、典型 55.6 dB；0.1% 容差 54 / 75.6 dB（该例增益为 1）。
- TI SLAA068B https://www.ti.com/lit/an/slaa068b/slaa068b.pdf ：差分放大 = 反相 + 同相叠加。
- TI SBOA281 / SBOA282 仪表放大器电路手册 https://www.ti.com/lit/pdf/sboa281 、https://www.ti.com/lit/pdf/sboa282 ：三运放结构，增益 1 + 2R/Rg，输入阻抗高、CMRR 不受源内阻影响。

## 实战代码
- 本节仿真直接用理想运放公式（虚短虚断）在 numpy 里算，无需 SPICE；参考 scipy/numpy 文档。

## 常见误区
- 四只电阻不成比例 → 共模泄漏（本节算得：增益 10、单只 1% 偏差 CMRR ≈ 61 dB；四只最坏 ≈ 49 dB）。
- 忽视信号源内阻：内阻串在 R1 上等于电阻失配，100 Ω 即相当于 1% 误差。
- 以为两输入端输入电阻相等（反相端 R1，同相端 R3 + R4），对源不平衡。
