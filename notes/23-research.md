# 23 光耦隔离 · 资料笔记（作者 D）

以下每条都打开过原网页或 PDF。

## 原理（厂家应用笔记 / 数据手册）

1. Sharp PC817XxNSZ1B 系列数据手册 <https://global.sharp/products/device/lineup/data/pdf/datasheet/PC817XxNSZ1B_e.pdf>
   - CTR 50%–400%（I_F 5 mA、V_CE 5 V、25 °C）；分档 A/B/C/D：I_C 4.0–8.0 / 6.5–13 / 10–20 / 15–30 mA（I_F 5 mA）。
   - V_F 典型 1.2 V、最大 1.4 V（I_F 20 mA）；V_CE(sat) 典型 0.1 V、最大 0.2 V（I_F 20 mA、I_C 1 mA）；V_CEO 80 V；I_F 最大 50 mA。
   - 隔离电压 5 kV rms；响应时间 t_r 典型 4 μs、t_f 典型 3 μs（V_CE 2 V、I_C 2 mA、R_L 100 Ω），最大 18 μs。
   - 设计提示：I_F < 1 mA 时 CTR 离散变大；红外 LED 发光会衰减，长期使用按「5 年衰减 50%」考虑。
2. Vishay AN45 How to Use Optocoupler Normalized Curves <https://www.vishay.com/doc/?83706=>
   - CTR = I_C / I_F × 100%；分非饱和 CTR（V_CE 5 V）和饱和 CTR（V_CE 0.4 V），开关用要看饱和 CTR。
   - 负载电阻 R_L ≥ (V_CC − V_CE(sat)) / (I_F · CTR_sat)；例：5 V、5 mA、CTR_sat 75% → ≥ 1.22 kΩ。
   - 例 2：CTR_sat = CTR_min × NCTR × 老化 × 公差 = 100% × 0.71 × 0.8 × 0.75 = 42.6%（10 年寿命按老化 20%、公差 −25%）。
3. Vishay AN04 Impact of CTR on switching times <https://www.vishay.com/docs/80579/an04_impactcurrenttransferratiooptocouplers.pdf>
   - CTR 高 → 开通快、关断慢（饱和时存储电荷多）；CTR 低 → 关断快。
4. Vishay Faster Switching from Standard Couplers <https://www.vishay.com/docs/83590/fastswit.pdf>
   - 影响速度的因素按重要性：负载电阻、R_BE、h_FE、结电容、米勒效应、LED 速度；LED 本身 < 100 ns，可忽略，瓶颈是光敏三极管。
   - 关断时间随负载电阻增大（负载电流减小）而增大；随 CTR 增大而增大。
5. Vishay 4N25 数据手册 <https://www.vishay.com/docs/83725/4n25.pdf>
   - CTR ≥ 20%（I_F 10 mA、V_CE 10 V）；V_F 典型 1.3 V（50 mA）；隔离测试电压 5000 V rms；t_r、t_f 2 μs（R_L 100 Ω）；有「传输延时随集电极负载电阻变化」曲线。
6. Vishay 6N137 数据手册 <https://www.vishay.com/docs/84732/6n137.pdf>
   - 高速光耦：10 MBd，内部是光电二极管 + 逻辑 IC，输出侧要 4.5–5.5 V 电源；t_PLH 典型 48 ns、最大 75 ns。
7. Microchip ATmega328P 数据手册 <https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf>
   - V_IL 最大 0.3 V_CC、V_IH 最小 0.6 V_CC（V_CC 2.7–5.5 V）；I/O 内部上拉 20–50 kΩ。
8. Vishay Application Examples（AC 输入光耦）<https://www.vishay.com/docs/83741/83741.pdf>
   - AC 输入光耦内部两只 LED 反向并联，交流正负半周都发光；10 年寿命 CTR 再留约 20% 老化余量。

## 实战代码

9. ArduinoGetStarted：Arduino – PC817 Optocoupler <https://arduinogetstarted.com/tutorials/arduino-pc817-optocoupler-monitor-12v-24v-dc-input-signal>
   - `pinMode(2, INPUT_PULLUP)` + `digitalRead`，有信号时读到 LOW（反相）；R = (V_in − 1.2)/0.01，12 V 配 1 kΩ。
   - 明确写：不要把 12 V/24 V 电路的地接到 Arduino GND，接了模块照样工作，但隔离就没了。
   - 漏电流（PLC、可控硅输出）会让 LED 微亮，并 4.7–10 kΩ 泄放电阻。
10. 本节点 code/23_sim.py 不用 SPICE，直接按「CTR × I_F 与上拉电阻能给的电流取小者」和 RC 充电算。

## 常见错误

11. Shutdown Circuit：Optocoupler Isolated Digital Signal <https://shutdowncircuit.com/blocks/optocoupler/>
    - 输入、输出两侧的地绝不能连（走线、电阻、旁路电容都不行）。
    - CTR 随寿命和高温下降，室温新器件刚好能用的设计会在现场失效，CTR 至少留 2 倍余量。
    - PC817 / 4N25 类只适合几 kHz 以下；PWM、编码器、串口用 6N137 类高速光耦；6N137 忘接输出侧电源是常见错误。
    - 输出相对输入是反相的。
12. 汇总
    - 两侧地接在一起（9、11）。
    - I_F 太小：新器件能拉低，老化（Sharp：5 年 50%）后拉不低（1、2、11）。
    - 普通光耦传高速信号：边沿被拖成斜坡，上拉越大越慢（4、5、11）。
    - 用单片机内部上拉（20–50 kΩ）当光耦上拉：省元件，但上升沿最慢（7、9 + 本节点仿真）。
    - [待核实]：市电过零检测里输入电阻的具体取值和功耗，本节点只作原理示意，不给可照抄的电路。
