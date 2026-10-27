# 30 仪表放大器与电桥 · 调研笔记（作者 A）

## 理论
- 第一部分回指：16-differential-amp/page2.md 已有三运放 INA 例题（R = 10 kΩ、R_g = 1 kΩ，G = 1 + 20 = 21；V1 = 2.00 V、V2 = 2.01 V 时输出差 0.21 V）。本节从这个例题出发，不重复推导差分级。
- ADI MT-061《Instrumentation Amplifier (In-Amp) Basics》https://www.analog.com/media/en/training-seminars/tutorials/MT-061.pdf （curl 自盒子超时，WebFetch 可打开）：
  - 单运放差分放大器的 CMR 主要由电阻比匹配决定：最坏 CMR(dB) = 20·lg((1 + R2/R1)/(4·Kr))（Kr 为单只电阻容差）；用电阻网络时为 20·lg((1 + R2/R1)/Kr)（Kr 为净比值失配）。
  - 数值（R1 = R2）：净比值失配 0.1% → 约 66 dB；其中一只电阻偏 1% → 只剩 46 dB；四只未挑选的 1% 电阻最坏 → 不超过 34 dB。
  - 集成 INA 典型 CMR 70 到 100 dB 以上，且增益越高 CMR 越好；50/60 Hz 共模干扰是工业现场最常见的干扰。
- ADI MT-062《Basic Two Op Amp In-Amp Configuration》https://www.analog.com/media/en/training-seminars/tutorials/MT-062.pdf （curl 自盒子超时，WebFetch 可打开）：两运放 INA，G = 1 + R2/R1 + 2R2/R_G，CMR ≤ 20·lg(G × 100/%失配)；单电源 5 V、G = 2 时 V1 只能在 1.3–2.4 V 之间（共模范围与增益互相制约），可作 page3 “变体”。
- TI INA126 数据手册 https://www.ti.com/lit/ds/symlink/ina126.pdf （已打开）：G = 5 + 80 kΩ/R_G。
- TI INA333 数据手册 https://www.ti.com/lit/ds/symlink/ina333.pdf （已打开）：G = 1 + 100 kΩ/R_G。
- ADI Analog Dialogue《Electromagnetic Flow Meters》https://www.analog.com/en/resources/analog-dialogue/articles/electromagnetic-flow-meters.html （curl 超时，WebFetch 可打开）：电极信号 75 µV 到 4–6 mV（0.5–15 m/s，灵敏度 150–200 µV/(m/s)），极化电压几百 mV 到 ±2 V；所以 INA 第一级增益一般 ≤ 10，否则共模/极化电压会让输出饱和；100 dB CMRR 能把 0.3 V 共模压到 3 µV。
- Emerson Rosemount 405 https://www.emerson.com/is/content/emerson/en/measurement-instrumentation/technical/products/dp-flow/documents/dl-rmt-00821-0100-4810.pdf （已打开）：差压 ∝ v²（差压流量计原理）。
- Emerson Rosemount 3051S 手册 https://www.emerson.com/is/content/emerson/en/measurement-instrumentation/technical/products/pressure/documents/doc-rosemount-3051s-00809-0100-4801.pdf （已打开）：变送器有 Linear / Square Root 两种输出，开方时有低流量切除（Cutoff Mode）。

## 推导链（page2 用）
1. 电桥：上下两臂各一个分压器，V_out = V_ex·(R2/(R1+R2) − R4/(R3+R4))。四个 10 kΩ 中一只变化 ΔR，精确式 V_out = V_ex·ΔR/(2(2R+ΔR))，近似式 V_ex·ΔR/(4R)。
2. 比例测量：V_out ∝ V_ex，若 ADC 参考也取 V_ex，读数与 V_ex 无关（激励电源漂移被消掉）。
3. 三运放 INA：第一级 G1 = 1 + 2R/R_G 只放大差模；第二级差分放大减去共模。
4. CMR（dB）= 20·lg(G_dm/G_cm)；电阻失配 → G_cm ≠ 0。
5. 差压流量：Q = k·√ΔP；流量从 100% 到 10%，差压从 100% 到 1%（量程比被平方压缩），这就是开方器和低流量切除存在的原因。

## 算例（p2refs/calc.py 已复核）
- INA G = 21（与 16 节相同）。
- 4×10 kΩ 电桥，5 V 激励，ΔR = 1%（100 Ω）：精确 12.44 mV，近似 12.5 mV；经 G = 21 → 约 0.261 V。
- 差压：10% 流量 → 1% 满量程差压。

## 常见错误
- 只用一个差分放大器 + 四只未挑选的 1% 电阻，以为 CMR 很高（MT-061：最坏不超过 34 dB）。
- R_G 接在第一级两个反相端之间以外的地方，增益公式失效。
- 第一级增益过大，共模/极化电压让第一级饱和（ADI EM 文章：≤10）。
- 电桥激励与 ADC 参考分别取自两个电源，失去比例测量的好处。
- 差压信号当成线性流量；或开方做两次（推论，见 00-design-part2）。

## 图与原理图计划
- 图 30-p1-1 电桥 + INA 框图；图 30-p1-2 共模/差模示意（同一根线上的 2 V 与 10 mV）。
- 图 30-p2-1 三运放 INA 原理图（schem.py）；图 30-p2-2 CMR vs 电阻失配（30_figs.py，用算出的曲线，标注 MT-061 三个点）。
- 图 30-p3-1 差压 vs 流量平方关系、开方后曲线与低流量切除。
- 图 30-p4-1 面包板图 + 30_p4_k_schem_lab.png（lab_schem.py NODES[30]）。

## SPICE 计划（spice/30/）
- 30_ina.cir：TL072 宏模型三运放 INA，R = 10 k、R_G = 1 k；.op 验证 G = 21。
- 30_cmr.cir：共模 1 V 正弦，差分级一只电阻偏 0.1% / 1%，测输出算 CMR，与 MT-061 的 66 / 46 dB 对比（注意 66 dB 对应净比值失配 0.1%）。
- 30_bridge.cir：电桥 + INA，ΔR 扫描，验证 12.44 mV × 21。

## page4 实验
- TL072×2（或 LM358×2），±6 V（或 12 V + 虚地）；4×10 kΩ 电桥中一臂串 1 kΩ 电位器微调；R_G 1 kΩ。
- 步骤：测 G；两输入并联接 1 V 测共模输出算 CMR；换 1% 电阻与配对电阻对比。

## 未用·待核实
- 无。（MT-061/MT-062 只能用 WebFetch 打开，盒子 curl 超时；引用时注明。）
