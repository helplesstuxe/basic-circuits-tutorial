# 08 线性稳压 · 调研笔记

只记结论和出处；所有链接都已实际打开（2026-10-23）。

## 三端稳压器

- TI uA78xx 系列数据手册 SLVS056P：https://www.ti.com/lit/ds/symlink/ua78.pdf
  - 输出电流到 1.5 A；内部有过热保护、短路限流、安全工作区保护；手册写明 "Output capacitor not needed for stability"。
  - 绝对最大输入 35 V；结温上限 150 °C。推荐输入：7805 为 7–25 V，7812 为 14.5–30 V。
  - 热阻 RθJA：TO-220（KC/KCS/KCT）19 °C/W，KTE 23 °C/W，KTT 25.3 °C/W。
  - 7805（V_I 10 V、I_O 500 mA）：输出 4.8/5/5.2 V（25 °C）；线性调整 3/100 mV（7–25 V）；纹波抑制 62/78 dB（8–12 V，120 Hz）；负载调整 15/100 mV（5 mA–1.5 A）；压差 2 V（1 A）；静态电流 4.2/8 mA；短路电流 750 mA。
  - 测试电路：输入 0.33 µF、输出 0.1 µF；输入电容要靠近芯片；输出高于约 7 V 时建议加反向保护二极管。
- TI LM317 数据手册 SLVS044Z：https://www.ti.com/lit/ds/symlink/lm317.pdf
  - 1.25–37 V 可调，1.5 A；V_REF 1.2/1.25/1.3 V；V_O = V_REF(1 + R2/R1) + I_ADJ·R2，I_ADJ 典型 50 µA。
  - NPN 达林顿输出；"C_O improves transient response, but is not needed for stability"。
  - 轻载时需要最小负载电流，否则输出偏高；C_ADJ 改善纹波抑制。

## 稳定性与 LDO

- TI SLVA115A "ESR, Stability, and the LDO Regulator"：https://www.ti.com/lit/an/slva115/slva115.pdf
  - PNP / PMOS 调整管的 LDO 有三个极点（误差放大、输出电容与负载、调整管），输出电容的 ESR 提供零点；必须用 ESR 合适的输出电容才能稳定。
  - 结论：00-design 的"输出不加电容引起振荡"适用于 LDO 和分立运放稳压；78xx / LM317 手册说输出电容不是稳定所必需的。

## 调整管与通用原理

- onsemi TIP31 系列数据手册 TIP31A/D：https://www.onsemi.com/download/data-sheet/pdf/tip31a-d.pdf
  - P_D 40 W（T_C 25 °C）、2 W（T_A 25 °C）；RθJA 62.5 °C/W，RθJC 3.125 °C/W；T_J 最高 150 °C。
- Wikipedia "Linear regulator"：https://en.wikipedia.org/wiki/Linear_regulator
  - 调整元件功耗 I·(V_in − V_out)；7805 需要约 7 V 输入（压差约 2 V）；LDO；串联与并联稳压；LM317 1.25 V 基准。
- Rod Elliott（ESP）"Voltage And Current Regulators"：https://sound-au.com/articles/vi-regulators.html
  - 市电波动按 +10% / −15% 考虑；稳压管之后的下一步是串联调整管。

## 本节取值来源

- 稳压管 1N4733A（V_Z 5.1 V，Z_ZT 7 Ω @ 49 mA）：见 notes/10-research.md。
- LM358 拉电流典型 30 mA / 最小 20 mA、输出到正电源下约 1.5 V：见 notes/07-research.md 与 07 page1、page2。
- 运放开环增益 1e5 为示意值，只用于说明 V_BE 被缩小 AK 倍。
- 输出电容 10 µF 为示意值，正文要求用负载跳变实验确认。
