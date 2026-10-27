# 35 程控增益与 AGC · 调研笔记（作者 C）

## 理论
- TI PGA113 https://www.ti.com/lit/ds/symlink/pga113.pdf （已打开）：示波器式（1-2-5 档）增益 1、2、5、10、20、50、100、200；SPI 接口 10 MHz；应用列表中有 AGC。
- ADI AD8331 数据手册 https://www.analog.com/media/en/technical-documentation/data-sheets/AD8331_8332_8334.pdf （curl 超时，WebFetch 可打开）：线性 dB 可变增益，50 dB/V；LO 模式增益 −4.5 至 43.5 dB，GAIN(dB) = 50·V_GAIN − 6.5（LO 档）；面向超声接收链；应用列表含 “High performance automatic gain control (AGC)”；MODE 脚可把斜率反为 −50 dB/V，数据手册说这正适合 AGC（控制电压正比于输出幅度）。
- TI CD4051B https://www.ti.com/lit/ds/symlink/cd4051b.pdf （已打开）：8 选 1 模拟开关，导通电阻 125 Ω（典型）。
- TI LM358B https://www.ti.com/lit/ds/symlink/lm358b.pdf （已打开，GBW 1.2 MHz 见 20-research）。
- 横河 YEWFLO 技术报告（见 32-research）：压电电荷 ∝ ρv²，流速变 10 倍，信号幅度变 100 倍——这就是涡街需要 AGC 的理由。
- TI TDC1000（见 37-research）：超声前端集成了 PGA。

## 推导链
1. 同相放大 G = 1 + R_f/R_g；换 R_g 换增益。
2. 开关串在 R_g 里：G = 1 + R_f/(R_g + R_on)，R_g 越小（增益越高）R_on 的相对误差越大。
3. 解决：把开关放在不流过增益电流的地方（例如选通反馈电阻分压抽头、开关接在运放输入端高阻节点）——作者画两种接法对比。
4. dB：20·lg G；PGA113 的档位让相邻档约 2–2.5 倍，ADC 有效位数损失不超过约 1.3 位（作者自算并注明）。
5. AGC：峰值检测（09 节）→ 与目标比较 → 增益上调/下调；环路时间常数要远大于信号周期，否则把信号本身的调制“抹掉”。
6. 数字 AGC：MCU 读 ADC 峰值，超过 90% 满量程降档，低于 30% 升档，带回差避免来回跳（参数为本笔记设计值，作者在 Python 中模拟确认）。

## 算例（calc.py 已复核）
- R_f = 100 kΩ，R_g = 100 k / 24 k / 11 k / 5.1 k / 2 k / 1 k → G = 2 / 5.17 / 10.09 / 20.6 / 51 / 101。
- R_g = 1 kΩ 串 CD4051 的 125 Ω：G = 101 → 约 89.9（误差约 11%）。
- LM358 在 G = 100 时带宽约 1.2 MHz/100 = 12 kHz。
- AD8331 LO：−4.5 到 43.5 dB。

## 常见错误
- 开关串在 R_g 里，高增益档误差最大。
- 换档后立刻采样，没等放大器和耦合电容稳定。
- AGC 太快 → 信号幅度信息丢失；太慢 → 大信号来时饱和很久。
- 忘记 CD4051 的模拟信号电压必须在 VEE 到 VDD 之间。
- 用 dB 和倍数混算。

## 图与原理图计划
- 图 35-p1-1 小信号只占 ADC 一小段 vs 放大后占满；图 35-p2-1 CD4051 切换 R_g 的原理图（两种开关位置）；图 35-p2-2 R_on 误差 vs 增益；图 35-p3-1 数字 AGC 换档时序（35_figs.py 模拟）。
- 图 35-p4-1 面包板 + 35_p4_k_schem_lab.png。

## SPICE 计划（spice/35/）
- 35_pga.cir：LM358 同相放大，R_g 串 125 Ω 电阻模拟开关，.step 六档，验证增益与 89.9。
- 35_bw.cir：G = 100 时 AC 扫描，确认约 12 kHz。

## page4 实验
- LM358 5 V 单电源（输入偏置到 2.5 V 或用正弦叠加直流）；CD4051 由 Arduino D2–D4 选档；R_g 六档如上。
- 输入：Arduino tone 经 RC 衰减得到不同幅度。
- Arduino 程序：读 ADC 峰值 → 换档（数字 AGC），串口打印档位与换算后的“真实幅度”。

## 未用·待核实
- 无。
