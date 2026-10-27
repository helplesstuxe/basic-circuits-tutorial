# 40 热式流量与 RTD 恒温差 · 调研笔记（作者 C）

## 理论
- TI SBAA275A（RTD 测量基础）https://www.ti.com/lit/an/sbaa275a/sbaa275a.pdf （已打开）：
  - Callendar–Van Dusen 系数 A = 3.9083e-3、B = −5.775e-7（0 °C 以上 R = R0(1 + A·T + B·T²)）；
  - 激励电流一般 < 1 mA，因为自热；
  - 自热温升 = P/E，E 为自热系数（mW/°C），小薄膜元件约 2.5 mW/°C，大元件约 65 mW/°C；
  - 2/3/4 线制。
- Sierra Instruments《Thermal Mass Flow Measurement of Fluid》https://www.sierrainstruments.com/prnews/Thermal%20Mass%20Flow%20Measurement%20of%20Fluid%2010.15.08.pdf （已打开）：King（1914）热线定律；一支加热 RTD + 一支参考 RTD 测流体温度；电流注入 T1 RTD。
- Sierra《Advances in thermal dispersion, part 1》（同站点 PDF，已打开）：恒温差/恒功率两种工作方式的背景。
- E+H t-mass 技术资料 https://bdih-download.endress.com/file/e292859ee90650142d47885eac156518/TI01502DEN_0323-00.pdf （已打开）：工业热式质量流量计实例（只作“真实产品”插图说明，不引用具体数值，除非作者另行核对）。

## 推导链
1. RTD：R(T) = R0(1 + A·T + B·T²)；PT100 在 100 °C 时为 138.5 Ω。
2. 自热：P = I²R；ΔT_self = P/E。
3. 热式原理：加热元件把热量交给流体，流速越大带走越多；热损失与流速的关系由 King 定律描述（具体式子见待核实，正文只写“随流速增大，但不是线性”）。
4. CMA（恒功率）：加热功率固定，测加热元件与流体的温差，温差随流速减小。
5. CTA（恒温差）：控制回路调加热功率，让温差保持不变，所需功率就是流量信号；响应更快（加热体温度不变，热容不用充放电）。
6. 两支 RTD 的作用：参考 RTD 测流体温度，抵消环境温度变化。

## 算例（calc.py 已复核）
- PT100 @ 100 °C = 138.5 Ω。
- 1 mA 激励：P = (1 mA)² × 100 Ω = 0.1 mW。
- 47 Ω 加热电阻 @ 5 V：P = 25/47 = 0.53 W。

## 常见错误
- 激励电流太大，RTD 自己把自己加热。
- 没有参考 RTD，环境温度一变就以为流量变了。
- 把 CTA 输出的“功率”当成线性流量。
- 加热电阻功率等级不够或手摸烫伤。
- 2 线制 RTD 忽略导线电阻。

## 图与原理图计划
- 图 40-p1-1 “风吹手指”类比；图 40-p2-1 RTD 电桥 + INA 原理图；图 40-p2-2 CMA 与 CTA 框图；图 40-p3-1 热模型阶跃响应（CTA 快、CMA 慢，40_figs.py 一阶热模型，参数为示意值并标明）。
- 图 40-p4-1 面包板 + 40_p4_k_schem_lab.png。

## SPICE 计划（spice/40/）
- 40_rtd_bridge.cir：PT100 用 100–138.5 Ω 的 .step 电阻，电桥 + INA 输出。
- 热模型用 RC 电路比拟（热容 ↔ C，热阻 ↔ R，功率 ↔ 电流），CTA 环路用运放 PI 控制，说明“电热类比”。

## page4 实验
- 47 Ω/2 W 电阻作加热器（5 V，约 0.53 W），用导热胶贴一只 10 kΩ NTC；另一只 NTC 放在上游测空气温度。
- Arduino：PWM D3 → IRLZ44N → 加热器；两只 NTC 分压 → A0/A1。
- CMA：固定 PWM，USB 风扇三档，记录温差；CTA：PI 控制温差 = 10 °C，记录 PWM。
- 安全：加热器可达较高温度，固定在木板/陶瓷上，不要手摸。

## 未用·待核实
- 「[待核实]」King 定律的具体公式形式（Nu 或 P 与 √v 的关系）：已打开的 Sierra 资料只给出名称与年份，没有给出可直接引用的式子。
- 「[待核实]」E+H 热式流量学习中心页面（JS 验证页，未打开）。
