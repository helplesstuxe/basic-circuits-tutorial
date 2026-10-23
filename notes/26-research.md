# 26 上拉/下拉电阻与电平转换 · 调研笔记（作者 C）

## 已打开并引用的资料

- TI SLVA689A https://www.ti.com/lit/an/slva689/slva689.pdf （本地 /workspace/authorC/refs/slva689.pdf.txt）：Rp(min) = (VCC − VOL(max)) / IOL；tr = 0.8473·Rp·Cb（0.3→0.7 VCC）；Rp(max) = tr / (0.8473·Cb)；标准/快速/快速+ 的 tr 1000/300/120 ns，Cb 400/400/550 pF，VOL 0.4 V @ 3 mA；例：快速模式、200 pF、3.3 V → Rp 966.7 Ω～1.77 kΩ。
- Nexperia AN10441 Rev. 2 https://assets.nexperia.com/documents/application-note/AN10441.pdf （WebFetch 打开；nxp.com 旧地址 404）：单 N 沟道 MOS 管双向电平转换，栅极接 VDD1（低压）、源极接低压侧、漏极接高压侧，两侧各自上拉；三种状态（无人拉低 / 低压侧拉低 / 高压侧拉低经漏-衬底二极管）；支持线与；适用标准和快速模式。
- onsemi BSS138 https://www.onsemi.com/pdf/datasheet/bss138-d.pdf ：50 V、0.22 A；VGS(th) 0.8/1.3/1.5 V；RDS(on) 4.5 V 时 1.0/6.0 Ω；Ciss 27 pF；体二极管 VSD 典型 0.8 V。
- TI SN74HC14 https://www.ti.com/lit/ds/symlink/sn74hc14.pdf （本地 sn74hc14.txt）：4.5 V 时 VT+ 1.55/2.5/3.13 V，VT− 0.9/1.6/2.45 V，ΔVT 0.4/0.9/2.1 V；II ±1 µA。
- Microchip ATmega328P 汽车级数据手册 7810D https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf （本地 atmega328p.txt）：VIL ≤ 0.3 VCC，VIH ≥ 0.6 VCC，RPU 20–50 kΩ，漏电 1 µA；§13.2.6 未用引脚建议开内部上拉。
- Ganssle 第 1 部分 https://www.ganssle.com/debouncing.htm ：18 种开关，去掉两个异常值后平均 1557 µs、最长 6200 µs；开关 E 断开时抖 157 ms；建议留余量。
- Ganssle 第 2 部分 https://www.ganssle.com/debouncing-pt2.htm ：R1/R2/C + 施密特去抖电路；「Never run the cap directly to the input on a microprocessor」；按 20 ms 设计；50 ms 感觉不到、100 ms 明显；电容误差 +80/−20%（电解）、±30%（陶瓷）；不要把未去抖开关接中断/触发器时钟；软件每 1–5 ms 采样。

## 设计取值

- 去抖：R1 = R2 = 10 kΩ，C = 1 µF，74HC14 门限按 4.5 V 典型值 2.5 / 1.6 V（5 V 系统近似）。
- 电平转换：BSS138 门限 1.3 V，K 由 RDS(on) = 1 Ω @ 4.5 V 反推（0.3125 A/V²）；体二极管 0.6 V + 50 Ω（示意）；两侧 10 kΩ、50 pF；开漏驱动 100 Ω。
- I²C 扫描：3.3 V、200 pF、400 kHz；1.5 / 4.7 / 10 kΩ。
- 悬空引脚示意：20 V 50 Hz 人体感应、0.5 pF 耦合、10 pF 输入电容（全部为示意值）。

## 仿真结果（code/26_sim.py、code/figs/26_figs.py 打印）

- 去抖：只上拉翻转 22 次；RC + 施密特 2 次；按下 12.3 ms（公式 11.4 ms）、松开 13.2 ms（公式 13.9 ms）。
- 抖动示意：一次按下 7 个下降沿。
- 悬空：耦合幅度 0.95 V，50% 时间在 1.5～3.0 V；10 kΩ 上拉时 31 µV。
- 电平转换：正确接法两侧拉低均约 0.08 V；松手后约 2.02 V（+328 ns）分开；接反时空闲 3.85 / 4.45 V。
- I²C：Rp min 967 Ω，快速模式 max 1770 Ω，标准模式 max 5901 Ω；tr 254 / 796 / 1695 ns，半周期末 3.25 / 2.43 / 1.53 V。
- τ 扫描（20 次按键、抖动 0.5–6.2 ms 示意）：施密特多翻次数 12.5 / 7.5 / 3.5 / 0.6 / 0 …（τ ≥ 2.2 ms 为 0）；单门限 + 20 mV 低通噪声最低 2.2（τ = 1 ms），47 ms 时 76.9；最长延迟 10 ms → 17.5 ms，47 ms → 66.9 ms。

## 未用·待核实

- 74HC14 没有 5 V 一行数据，正文明确写了按 4.5 V 典型值估算。
- 练习 2 的 220 mAh 电池容量标为示意值。
- 正文无 [待核实]。
