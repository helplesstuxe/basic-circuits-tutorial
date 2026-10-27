# 36 施密特整形与频率/脉冲计数 · 调研笔记（作者 B）

## 理论
- 第一部分回指：10-voltage-comparator/page1.md 的 LM393 施密特，上门限约 2.75 V、下门限约 2.26 V（含上拉电阻修正）。
- TI LM393 https://www.ti.com/lit/ds/symlink/lm393.pdf （已打开）：开集电极输出，响应时间约 1–1.3 µs。
- Omega《Turbine & Paddle Wheel Flowmeter Reference》https://br.omega.com/omegaFiles/Green/pdf/TURBINE_PADDLE_REF.pdf （已打开）：K 系数 = 每加仑脉冲数；频率 f（脉冲/秒）；GPM = f·60/K；在线性范围内 K 近似常数。
- Flomec 博客《Turbine flow meter frequency and K-factor》https://www.flomecmeters.com/blogs/did-you-know/turbine-flow-meter-frequency-and-k-factor （已打开）：频率与 K 系数关系的通俗解释。
- 横河 YEWFLO 技术报告（见 32-research）：涡街 f = K_T·Q。
- ~~NE555 当实验信号源~~（已弃用：协调者决定第二部分实验不加 555；本节改用 Arduino 自己的 `tone()`/`analogWrite()` 当信号和干扰，见下「page4 实验」）。
- Arduino `tone()` https://docs.arduino.cc/language-reference/en/functions/advanced-io/tone/ 与 ArduinoCore-avr Tone.cpp https://github.com/arduino/ArduinoCore-avr/blob/master/cores/arduino/Tone.cpp （已打开）：Uno 上用 Timer2；100 Hz → 预分频 1024、OCR2A 77 → 实际 100.160 Hz。
- Arduino `analogWrite()` https://docs.arduino.cc/language-reference/en/functions/analog-io/analogWrite/ （已打开）：D5/D6 约 980 Hz（Timer0，16 MHz/64/256 = 976.5625 Hz）。
- Arduino Uno Rev3 原理图 https://docs.arduino.cc/resources/schematics/A000066-schematics.pdf （已打开）：16 MHz 陶瓷谐振器 CSTCE16M0V53-R0；D8 = PB0 = ICP1。
- Murata CSTCE16M0V53-R0 https://www.murata.com/en-us/products/productdetail?partno=CSTCE16M0V53-R0 ；陶瓷谐振器 vs 晶振对比 https://www.murata.com/~/media/webrenewal/products/timingdevice/ceralock/nem/comparison/dr-e17-0030.ashx?la=en （已打开）：初始误差最大 ±0.5%（温度 ±0.3%、老化 ±0.2% 另计）。36_sim.TIMEBASE = 5e-3。
- Microchip ATmega328P 数据手册 https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/ATmega48A-PA-88A-PA-168A-PA-328-P-DS-DS40002061B.pdf （已打开）29.1 绝对最大额定值：除 RESET 外任一引脚 −0.5 V 到 VCC + 0.5 V；每个 I/O 脚直流 40 mA。→ 上拉只能接 5 V（魔鬼代言人补查）。
- LM393 共模范围：0 到 VCC − 1.5 V（25 °C），全温度 VCC − 2 V（数据手册）→ 本节 LM393 用 9 V 供电，输入最高 2.92 V。
- Arduino attachInterrupt https://docs.arduino.cc/language-reference/en/functions/external-interrupts/attachInterrupt/ （已打开）：RISING/FALLING/CHANGE。

## 推导链
1. 带噪声的正弦过零附近会被单门限比较器多次触发 → 一个周期数出几个脉冲。
2. 回差 V_H = V_TH+ − V_TL−；条件：回差 > 噪声峰峰值，且回差 < 信号峰峰值。
3. 门限要以信号中点为中心（交流耦合 + 偏置，或用信号的平均值作参考）。
4. 频率 → 流量：Q = f/K；累计体积 = 脉冲数/K。
5. 门控计数（数 1 s 内的脉冲）有 ±1 个脉冲误差 → 相对误差 1/(f·T_gate)；低频时很大。
6. 倒数计数（测一个周期内的时钟数）：误差 ±1 个时钟 → f/f_CLK；Arduino Timer1 ÷8 = 2 MHz（0.5 µs），16 位不溢出要求 f > 30.52 Hz。分辨率 ≠ 准确度：时基 ±0.5%。

## 算例（calc.py 已复核）
- 100 Hz、1 s 门控：±1 个 → ±1%。
- 100 Hz 信号用 16 MHz 倒数计数：一个周期 160000 个时钟 → 6.25 ppm，但 16 位会溢出，所以页面用 ÷8：20000 个 → 0.005%。
- 涡轮 K = 100 脉冲/加仑、f = 500 Hz → 500 × 60/100 = 300 GPM。

## 常见错误
- 回差小于噪声，仍然多计数。
- LM393 不接上拉电阻，输出“没有高电平”。
- 门限没有以信号中点为中心，占空比歪、低幅度时丢脉冲。
- 低频流量用门控计数，±1 误差大。
- 把 K 系数单位（脉冲/加仑 vs 脉冲/升）混用。

## 图（最终，36_figs.py）
- page1：36-p1-1 单门限 vs 施密特（30 ms：6 次 vs 3 次）；36-p1-2 流量计 → 整形 → 计数 → Q = f×60/K。
- page2：36-p2-1 原理图（①②③）；36-p2-2 回差曲线（SPICE 2.605/2.389）；36-p2-3 n2 信号与干扰；36-p2-4 门控 vs 倒数（时基 ±0.5% 虚线）；36-p2-5 Timer1 输入捕获。
- page3：36-p3-1 R2 扫描窗口；36-p3-2 源内阻 1k/4.7µ vs 10k/470n。
- page4：36-p4-1 面包板；36-p4-2 带孔位原理图。

## SPICE（spice/36/，见 review/spice/36.md）
- thresh/vol/amp/count/pullup/cm 六个网表，LM393A 官方模型；24 ✅ 3 ℹ️。

## page4 实验（最终）
- D7 `tone(7,100)` → Rs1 1k/C1 4.7µ/Rs2 1k/C2 4.7µ → n2；D5 `analogWrite(5,128)` 经 Rn 2.2k 注入 n2 当干扰。
- n2 → R1 10k → LM393 IN+，R2 220k 回差，IN− = 2.5 V（Ra/Rb 10k 从 Arduino 5 V），LM393 9 V 电池供电，R3 4.7k 上拉到 Arduino 5 V → D8（ICP1）。
- 步骤：3 无 Rn 无 R2（100）→ 4 插 Rn（约 175）→ 5 插 R2（100，period 19968，60.10 GPM）→ 6 拔 Rn（100）→ 7 R2 换 47k（0）。全程断电改线（先拔电池再拔 USB；先接 USB 再接电池）。
- 草图（未经运行验证）：Timer1 普通模式、ICES1 + CS11、ISR(TIMER1_CAPT_vect) 无符号减法、1 s 门控 + 2 s 零流量超时。

## 未用·待核实
- 无。草图未在真实 Arduino 上运行（页面已标注）。
