# 01 元件速成 · 调研笔记（作者 D）

## 原理出处（都已打开核对）
- TI SLAA067《Understanding Basic Analog — Circuit Equations》（Ron Mancini）：https://www.ti.com/lit/an/slaa067/slaa067.pdf
  - 分压公式只在输出端「不接负载」时成立；接了负载要把负载和下电阻并联后再算。
  - 常见错误：以为负载比电阻大 10 倍就可以忽略，结果仍有约 10% 的误差。
  - 戴维南等效：分压器的输出电阻 = R1∥R2。
- ADI StudentZone 2018-04（ADALM1000 Topic 4：RC 电路）：https://www.analog.com/en/resources/analog-dialogue/studentzone/studentzone-april-2018.html
  - 充电百分比表：τ 63.2%、2τ 86.5%、3τ 95.0%、4τ 98.2%、5τ 99.3%；理论上永远到不了 100%，工程上 5τ 视为充满。
  - 方波激励：脉宽远大于 τ 时输出接近方波，脉宽等于 τ 时输出变成「锯齿状」的指数段。
- UBC Okanagan（J. Bobowski）Python ODE 教程：https://cmps-people.ok.ubc.ca/jbobowsk/Python/html/Jupyter%20ODEs.html
  - 用 dq/dt = V0/R − q/(RC) 数值求解电容充电，并验证 V_C + V_R = V0（基尔霍夫电压定律）。本节点改用更直白的逐步（欧拉）算法，并与公式对照。
- TE Connectivity《Relay Coil Suppression with DC Relays》：https://www.te.com/en/products/relays-and-contactors/electromechanical-relays/intersection/relay-coil-suppression-dc-relays.html
  - 12 V 直流继电器线圈断电时可能产生 1000–1500 V 的反向尖峰。
  - 抑制办法：二极管、二极管+稳压管、电阻、压敏电阻、TVS；只并二极管会让释放变慢，可能导致触点粘连。
- Omron 定时器分类说明：https://www.ia.omron.com/support/guide/13/classifications.html
  - 通电延时（ON-delay）：通电后经过设定时间才动作；断电延时（OFF-delay）：断电后经过设定时间才复位。
- Schneider Electric FAQ FA142452：https://www.se.com/uk/en/faqs/FA142452/
  - 接触器由主触点（极）、辅助触点、线圈组成；线圈电压常与主触点电压不同。
- 电工天下《时间继电器通电延时与断电延时的触点图形符号》：https://dgjs123.com/jdq/19870.htm
  - 规则：延时触点上半圆弧的「开口方向」就是触点延时动作的方向；时间继电器文字符号 KT。

## 典型错误（写进正文）
1. 把电容当电阻算（用 V = IR 去算电容，或以为电容"有一个固定阻值"）。
2. 以为电容瞬间充满（实际 1τ 只到 63%，5τ 才到 99%）。
3. 继电器触点和线圈画在同一个回路里（线圈与触点之间只有磁力/机械联系，没有电线相连）。
4. 分压器接了负载还用空载公式（SLAA067）。
5. 电感（继电器线圈）断电不加续流二极管（TE 白皮书）。

## 未能核实
- （本轮已解决）铝电解电容容差 ±20%：Nichicon UVR 系列手册 https://www.nichicon.co.jp/english/series_items/catalog_pdf/e-uvr.pdf （已下载打开）"Capacitance Tolerance ±20% at 120Hz, 20˚C"；额定电压挡 6.3/10/16/25/35/50… V。
- （本轮已解决）耐压 1.5 倍：没有厂家把 1.5 倍写成规定，正文改为"经验余量"并给出理由。CDE 铝电解电容应用指南 https://www.cde.com/resources/catalogs/AEappGuide.pdf （已打开）：Rated DC Voltage 是"包括纹波在内可长期施加的最高峰值电压"；寿命电压乘数 Mv = 4.3 − 3.3·VA/VR（降额 10% 时 Mv = 1.33）。按 1.5 倍选时 VA/VR = 2/3，Mv ≈ 2.1。
- （本轮已解决）继电器线圈电感：Omron G5V-1 数据手册 https://xonstorage.z8.web.core.windows.net/pdf/Omron/4226465XON.pdf （已打开，备用 https://app.mectronic.com/dsheet/G5V12DC12_Omron.pdf ）线圈电感参考值：3 V 0.05/0.11 H，12 V 0.85/1.63 H（960 Ω），24 V 3.48/6.61 H（衔铁 OFF/ON）。12 V 款 τ = 0.89～1.70 ms。
- 以上数字均由 code/figs/01_figs.py 的 p3_datasheet_numbers() 打印并断言。
