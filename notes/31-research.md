# 31 跨阻放大器 TIA · 调研笔记（作者 A）

## 理论
- TI SBOA055A《Compensate Transimpedance Amplifiers Intuitively》https://www.ti.com/lit/an/sboa055a/sboa055a.pdf （已打开）：
  - 反馈电容 C_F = (1/(4π·R_F·GBW))·(1 + √(1 + 8π·R_F·C_D·GBW))；
  - 不补偿时的振铃频率 f_P = √(GBW/(2π·R_F·C_D))。
- TI SBOA268A（TIA 电路手册）https://www.ti.com/lit/an/sboa268a/sboa268a.pdf （已打开）：例子 R_F = 100 kΩ，C_D 150 pF。
- TI OPA380 数据手册 https://www.ti.com/lit/ds/symlink/opa380.pdf （已打开）：专用 TIA 运放（变体介绍用）。
- Vishay BPW34 https://www.vishay.com/docs/81521/bpw34.pdf （已打开）：结电容 70 pF（0 V）、25 pF（3 V 反偏）；1 klx 时反向光电流约 70 µA。
- TI LMC6482 https://www.ti.com/lit/ds/symlink/lmc6482.pdf （已打开）：输入偏置电流 20 fA（典型），GBW 1.5 MHz，轨到轨。
- TI TL072 https://www.ti.com/lit/ds/symlink/tl072.pdf （已打开）：GBW 5.25 MHz（JFET 输入）。

## 推导链
1. 虚地：反相端电压 0 → 二极管两端电压不变，C_D 不充放电（这是 TIA 比“电阻转电压”快的原因）。
2. 电流全部流过 R_F：V_out = −I·R_F（方向按二极管接法）。
3. C_D 与 R_F 形成噪声增益零点 → 相位裕度不够 → 振铃；加 C_F 产生极点抵消。
4. 加 C_F 后带宽约 1/(2π·R_F·C_F)。
5. 偏置电流误差 = I_B·R_F：LM358 等双极输入运放 nA 级 I_B 会淹没 nA 信号，CMOS/JFET 才适用。

## 算例（calc.py 已复核）
- TL072、R_F = 1 MΩ、C_D = 70 pF：C_F = 1.47 pF，f_P = 109 kHz。
- LMC6482、R_F = 100 kΩ、C_D = 25 pF：C_F = 5.7 pF，带宽约 279 kHz。
- BPW34 在 1 klx 下 70 µA × 47 kΩ = 3.29 V（5 V 单电源可用）。
- 测试电流：1 V / 10 MΩ = 100 nA，在 R_F = 1 MΩ 上得到 0.1 V。

## 常见错误
- 不加 C_F，输出振荡（图示 f_P）。
- 用 LM358（双极输入，I_B 大）测 nA 级电流。
- C_F 取太大，带宽被压得很低，闪光脉冲被“抹平”。
- 光电二极管极性接反（光伏/光导模式混淆）。
- 单电源下输出要往正方向走，二极管方向必须让电流从输出流向反相端，否则输出顶在 0 V。

## 图与原理图计划
- 图 31-p1-1 “电阻转电压” vs TIA 对比；图 31-p2-1 TIA 原理图（schem.py）；图 31-p2-2 有/无 C_F 阶跃响应（31_figs.py 用二阶模型）；图 31-p3-1 I_B 误差对比柱状图。
- 图 31-p4-1 面包板 + 31_p4_k_schem_lab.png。

## SPICE 计划（spice/31/）
- 31_tia_tl072.cir：R_F 1 MΩ、C_D 70 pF，C_F = 0 / 1.5 pF，电流阶跃，看振铃与 f_P。
- 31_tia_lmc6482.cir：R_F 100 kΩ、C_D 25 pF、C_F 5.6 pF（E12 值），AC 扫描找 −3 dB 点（期望约 280 kHz 附近）。
- 若无 LMC6482 模型，用通用运放宏模型设 GBW 1.5 MHz，并在 review/spice/31.md 写明。

## page4 实验
- LMC6482 5 V 单电源，反相端接虚地 2.5 V 或直接 0 V（选择需 SPICE 确认）；BPW34（或红色 LED 反接）；R_F 47 kΩ / 1 MΩ 可换，C_F 并联。
- 校准：1 V 经 10 MΩ 注入 100 nA → 1 MΩ 上 0.1 V。
- 用 Arduino 点亮 LED 方波闪烁，用 Arduino ADC 或示波器看上升沿，有/无 C_F 对比。

## 未用·待核实
- 无。
