# 05 精密整流 · 调研笔记

只记结论和出处；所有链接都已实际打开（2026-10-22）。

## 理论（教材 / 厂商应用笔记）

- Fiore《Operational Amplifiers and Linear Integrated Circuits》7.2 节 Precision Rectifiers（LibreTexts）：https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electronics/Operational_Amplifiers_and_Linear_Integrated_Circuits_-_Theory_and_Application_(Fiore)/07%3A_Nonlinear_Circuits/7.02%3A_Precision_Rectifiers
  - 0.5 V 峰值的信号用普通二极管整流根本整不出来（二极管要 0.6–0.7 V 才导通）。
  - 把二极管放进负反馈环，误差按环路增益缩小；输入为正时电路相当于电压跟随器，为负时二极管反偏、输出为 0。
  - 运放输出脚要比电路输出高 0.6–0.7 V 来补偿二极管压降；输入为负时运放进入负饱和。
  - 爬出饱和的时间由压摆率决定：741、±15 V 供电时从 −13 V 回到 0 约需 26 µs，20 µs 宽的正脉冲会完全丢失，50 µs 的只能部分跟上。快信号需要高单位增益带宽和高压摆率的运放。二极管调头即得负半波。
  - 7.2.2：反相型半波整流（反相放大器加两只二极管，一只钳住运放输出、使运放不饱和，因而更快；缺点是输入阻抗有限）；与原输入按 1 : 2 的权重送进反相加法器即得全波整流（绝对值电路）；两只二极管同时调头得负的全波。
- TI 模拟工程师电路手册 SBOA227B「Half-Wave Rectifier Circuit」：https://www.ti.com/lit/an/sboa227b/sboa227b.pdf
  - 反相型精密半波整流：只把输入的负半周反相后送到输出，增益 −R_f/R_1；示例 R_1 = R_f = 402 Ω，OPA323，±2.5 V，0.2 mVpp–4 Vpp，最高 50 kHz。
  - 设计要点：选高压摆率运放（过零时输出要跳过两个二极管压降）；选快速二极管，肖特基更快但反向漏电更大；电阻公差决定增益误差；电阻取小降低噪声。
  - OPA323：20 MHz、33 V/µs；替代运放要求 ≥10 MHz、≥5 V/µs。

- TI LM741 数据手册（SNOSC25）：https://www.ti.com/lit/ds/symlink/lm741.pdf
  - ±15 V 供电：压摆率典型 0.5 V/µs；输出摆幅典型 ±13 V（R_L ≥ 2 kΩ）、±14 V（R_L ≥ 10 kΩ）；LM741A 带宽 0.437–1.5 MHz。
- TI TL072 数据手册（SLOS080W）：https://www.ti.com/lit/ds/symlink/tl072.pdf
  - GBW 5.25 MHz（NS/PS 封装及 M 级为 3 MHz）；压摆率 C/I 级最小 8 V/µs、典型 20 V/µs。

## 入门讲解与常见错误

- Rod Elliott（ESP）AN001「Precision Rectifiers」：https://sound-au.com/appnotes/an001.htm
  - 运放两条规则：①通过反馈使两输入端电压相同；②做不到时输出取「更正的那个输入」的极性。
  - 基本型（二极管在反馈环里）：负半周无反馈，运放输出摆到负电源附近（±15 V 时约 −14 V），回来需要时间，20 mV、1 kHz 测试可见恢复延迟和振荡；只适合 10 kHz 以下、10 mV 以上。
  - 改进型加第二只二极管，运放输出不再摆到电源轨，2 mV 峰值也能较准确整流；代价是输入阻抗等于输入电阻，需要低阻信号源驱动。
  - TL072 约 3 MHz、13 V/µs，可用到约 150 kHz；肖特基/锗二极管改善小信号但漏电大；全波电路电阻要 1% 或更好。
  - 正弦波整流平均值 = 0.637 × 峰值。
- Wikipedia「Precision rectifier」（引 Horowitz & Hill《The Art of Electronics》）：https://en.wikipedia.org/wiki/Precision_rectifier
  - 实际门限 = 二极管门限 ÷ 运放增益；基本型负半周开环饱和、恢复引起振铃并限制频率响应；改进型运放不饱和，但过零时输出要变化两个二极管压降（约 1.2 V），压摆率和 GBW 仍限制高频，100 kHz 下可做到误差 <1%。

## 代码与仿真思路

- 二极管用折线模型（0.7 V 导通、导通电阻 10 Ω），与 P2 的「0.7 V 规则」一致。
- 运放用单极点 + 压摆率限制模型：dV/dt = clip(ω_p·(A·(V+ − V−) − V), ±SR)，A = 1e5，输出限幅 ±13.5 V（±15 V 供电）。
- 慢运放取 741 级（1 MHz、0.5 V/µs，与 LM741 手册和 Fiore 的 26 µs 例子一致）；快运放取 TL072 级，按手册最坏值取 3 MHz、8 V/µs（ESP 文中给的 13 V/µs 是旧版典型值）。
- 时间步长取闭环时间常数 1/(2π·GBW) 的 1/8，显式欧拉积分即可稳定。
