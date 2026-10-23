# P2 半导体入门 · 调研笔记

只记结论和出处；页面里引用的器件参数以这里为准。所有链接都已实际打开（2026-10-22）。

## 理论与器件参数（数据手册）

- Vishay 1N4148 数据手册：https://www.vishay.com/docs/81857/1n4148.pdf
  - V_F 最大 1 V（I_F = 10 mA）；V_RRM 100 V；I_F 连续 300 mA；t_rr 4 ns / 8 ns；结电容 4 pF。
  - 典型曲线：1–10 mA 时 V_F 约 0.6–0.7 V，温度升高 V_F 下降。
- Vishay 1N4728A–1N4764A 稳压管数据手册：https://www.vishay.com/docs/85816/1n4728a.pdf
  - 稳压值公差 ±5%，P_tot 1.3 W；正向 V_F 最大 1.2 V（200 mA）。
  - 1N4733A：V_Z = 5.1 V（I_ZT = 49 mA），Z_ZT 最大 7 Ω，I_ZM 178 mA；低压型号 I_ZK = 1 mA。
  - 1N4740A：10 V / 25 mA / 7 Ω，I_ZM 91 mA；1N4742A：12 V / 21 mA，I_ZM 76 mA。
- onsemi 2N3904 数据手册：https://www.onsemi.com/download/data-sheet/pdf/2n3904-d.pdf
  - V_CEO 40 V，I_C 200 mA，P_D 625 mW。
  - h_FE（即 β）：10 mA/1 V 时 100–300；1 mA 时最小 70；50 mA 时最小 60；100 mA 时最小 30。
  - V_CE(sat) 最大 0.2 V（I_C = 10 mA、I_B = 1 mA），0.3 V（50 mA、5 mA）；V_BE(sat) 0.65–0.85 V（10 mA）。
- onsemi 2N7000 / NDS7002A 数据手册：https://www.onsemi.com/download/data-sheet/pdf/nds7002a-d.pdf
  - V_DSS 60 V；V_GS(th) 0.8 / 2.1 / 3.0 V（最小/典型/最大，I_D = 1 mA）；I_D 200 mA；V_GSS ±20 V。
  - R_DS(on)：V_GS = 10 V、500 mA 时典型 1.2 Ω / 最大 5 Ω；V_GS = 4.5 V、75 mA 时典型 1.8 Ω / 最大 5.3 Ω。
  - C_iss 典型 20 pF；栅极漏电 10 nA 级。

## 入门讲解与常见错误

- SparkFun「Diodes」：https://learn.sparkfun.com/tutorials/diodes/all
  - 二极管是「电子世界的单向阀」；硅管 V_F 约 0.6–1 V，锗管约 0.3 V，肖特基 0.15–0.45 V。
  - LED 的 V_F 1.2–3 V，与颜色有关：超亮红色约 2.2 V，超亮蓝色约 3.3 V。
  - 稳压管反向电流足够时两端电压稳定在 V_Z；只适合小负载。反向保护二极管会损失一个压降。
- SparkFun「Transistors」：https://learn.sparkfun.com/tutorials/transistors/all
  - 水阀类比；截止、放大（I_C = β·I_B，β 常在 50–200）、饱和三种状态；饱和时 V_CE 约 0.05–0.2 V。
  - 常见错误：不加基极电阻；基极驱动 1–10 mA 一般够用。PNP 高边开关不能用 5 V 单片机直接关断 12 V。
- TI 应用笔记 SLPA021「Avoid Common Mistakes When Selecting And Designing With Power MOSFETs」：https://www.ti.com/lit/an/slpa021/slpa021.pdf
  - 第 4.2 节：V_GS ≥ V_GS(th) 不等于完全导通，要达到手册给 R_DS(on) 的那个 V_GS（例：CSD18541F5 阈值 1.75 V，R_DS(on) 在 4.5 V 下才给出，用 3.3 V 驱动出问题）。
  - 第 5.3 节：P 沟道 MOS 常做高边开关，栅极拉到地导通、拉到 V_IN 关断，注意 V_IN 不超过 V_GS 绝对最大值。
  - 第 6 节：栅极悬空会自己充电导致误导通甚至损坏，栅源之间加 10 kΩ–1 MΩ 电阻。

## 代码与仿真思路

- 二极管用肖克利方程 I = I_S·(e^(V/(n·V_T)) − 1)，取 I_S = 1e-14 A、n = 1：1 mA 时 0.655 V、10 mA 时 0.714 V，与 1N4148 典型曲线同一量级（示意，不是该型号的拟合）。
- 红色 LED 用 I_S = 1e-18 A、n = 2 的示意参数，10 mA 时约 1.90 V。
- 三极管用分段模型（V_BE = 0.7 V、β 恒定、V_CE(sat) = 0.2 V）；MOS 管用平方律示意模型（V_th = 2.1 V，k = 0.2 A/V²），只看曲线形状。
