# 09 开关电源 · 调研笔记

以下链接都已实际打开阅读（2026-10-23）。

- Wikipedia，Buck converter：https://en.wikipedia.org/wiki/Buck_converter
  - 效率常超过 90%；导通时 $V_L = V_i - V_o$ ，断开时 $V_L = -V_o$ ，伏秒平衡得 $D = V_o/V_i$ 。
  - 输出纹波 $\Delta V = \Delta I \cdot T/(8C)$ ；轻载进入断续模式。
  - 同步整流：二极管损耗 $V_D(1-D)I_o$ ；5 V → 3.3 V、10 A 例子中二极管 2.38 W、MOSFET 0.51 W；直通（shoot-through）与死区（non-overlap time），死区内靠下管体二极管导通，常并肖特基辅助。
  - 反向恢复损耗约 Qrr·VR·f；肖特基约 0.4 V，硅管约 0.7 V。
- TI SLVA477B，Basic Calculation of a Buck Converter's Power Stage：https://www.ti.com/lit/an/slva477b/slva477b.pdf
  - $\Delta I_L = (V_{in} - V_o) D/(f L)$ ，建议取输出电流的 20%～40%；峰值开关电流 $\Delta I_L/2 + I_o$ 。
  - 肖特基平均电流 $I_o(1-D)$ ，功耗乘 $V_F$ ；输出电容最小值 $\Delta I_L/(8 f \Delta V)$ ，ESR 纹波 $ESR \cdot \Delta I_L$ 。
  - 注意：正文式 1 写 $D = V_o/(V_{in}\eta)$ ，附录写成 $V_o \eta / V_{in}$ ，两处不一致。
- TI SSZTAV7，Waveform audit: is your inductor saturated?：https://www.ti.com/lit/ta/ssztav7/ssztav7.pdf
  - 饱和电流一般定义为电感量下降 30% 的直流电流，定义带随意性；硬饱和与软饱和；饱和后电流斜率变陡、纹波和损耗增大、尖峰可能损坏器件；饱和电流随温度下降。
- Coilcraft，Selecting the Best Inductor for Your DC-DC Converter：https://www.coilcraft.com/en-us/resources/application-notes/selecting-the-best-inductor-for-your-dc-dc-convert/
  - Isat（峰值、电感量下降）与 Irms（温升）两个额定值；饱和定义 10%～20% 常见。
- TI AN-2155（SNVA638A），Layout Tips for EMI Reduction in DC/DC Converters：https://www.ti.com/lit/an/snva638a/snva638a.pdf
  - 辐射场强 E = 263e-16·f²·A·I/r：与频率平方、回路面积、电流成正比。
  - 回路 1（输入电容 → 上管 → 电感 → 输出电容）与回路 2（关断期间）不重合的部分是高 di/dt 区；输入旁路电容要贴近；开关节点既容性耦合又辐射；地平面减小回路面积。
  - 带宽 ≈ 0.35 / 上升时间，10 ns 对应 35 MHz。
- Wikipedia，Flyback converter：https://en.wikipedia.org/wiki/Flyback_converter
  - 由 buck-boost 把电感拆成变压器而来，提供隔离；导通时储能、副边二极管反偏、输出电容供电；关断时二极管导通把能量送到电容和负载；反馈可用光耦。

本节仿真的损耗参数（ $R_{DS(on)}$ 0.05 Ω、DCR 0.05 Ω、开关过渡 20 ns、控制芯片 5 mA）均为示意值，页面中已注明。
