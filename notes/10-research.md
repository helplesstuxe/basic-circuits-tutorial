# 10 稳压管稳压 · 调研笔记

只记结论和出处；所有链接都已实际打开（2026-10-23）。

## 器件参数

- Vishay 1N4728A–1N4761A 数据手册（Doc 85816，Rev 2.7，07-Nov-2024）：https://www.vishay.com/docs/85816/1n4728a.pdf
  - 功率 P_tot 1300 mW；稳压值容差 ±5%；结到环境热阻 R_thJA 110 K/W。
  - 1N4733A：V_Z 5.1 V（测试电流 I_ZT 49 mA）；动态电阻 Z_ZT 7 Ω（49 mA 时）、Z_ZK 550 Ω（1 mA 时，即拐点附近）；最大稳压电流 I_ZM 178 mA；浪涌电流 890 mA。
  - 1N4742A：V_Z 12 V（I_ZT 21 mA），Z_ZT 9 Ω，I_ZM 76 mA。
  - 1N4740A：V_Z 10 V，I_ZM 91 mA。1N4735A：V_Z 6.2 V，Z_ZT 2 Ω。1N4732A：V_Z 4.7 V，I_ZM 193 mA。

## 原理与设计经验

- Wikipedia「Zener diode」：https://en.wikipedia.org/wiki/Zener_diode
  - 并联稳压（shunt regulator）：电阻电流 I = (U_in − U_out)/R。
  - R 要足够小，使稳压管在负载最大时仍处于击穿区（文中举 BZX79C5V6 推荐 5 mA）；R 又要足够大，使 I_D·V_B 不超过稳压管的额定功率。
  - 并联稳压浪费电，只适合小负载。
  - 温度系数：约 5.6 V 以下为负、以上为正，5.6 V 附近两种机理接近抵消；4.7 V 稳压管约 −2 mV/°C，和三极管 V_BE 相当，因此「4.7 V 稳压管 + NPN 发射极」得到约 4 V、温漂很小的电压。
  - 5.6 V 以下的稳压管拐点更「圆」（击穿不那么陡）。
- Rod Elliott（ESP）「Voltage And Current Regulators」：https://sound-au.com/articles/vi-regulators.html
  - 稳压管电流宜取最大值（I = P/V）的 10%–50%；例：15 V 1 W 稳压管最大约 66.7 mA，工作电流取 7–33 mA；负载 20 mA 时算出 113 Ω，取 120 Ω。
  - 负载断开时稳压管会非常烫，不要在没有负载时这样用。
  - 仿真例：19.4 V 直流输入带 300 mVpp 纹波，输出 15.1 V、纹波 16 mVpp（约 25 dB 抑制）。
  - 负载电流变化超过几个百分点的场合不推荐单用稳压管；输出电容必不可少。
  - 下一步是加串联调整管（series regulator）；V_BE 温度系数约 −2 mV/°C。
  - 市电电压波动按 +10%/−15% 考虑。
  - 把 R1 分成两段、中间接一只电容，可以进一步减小纹波。

- Wikipedia「Linear regulator」：https://en.wikipedia.org/wiki/Linear_regulator
  - 简单并联稳压：R1 = (V_S − V_Z)/(I_Z + I_R2)；算好 R1 后若去掉负载，全部电流流过稳压管，可能超过其最大电流。
  - 在并联稳压后加一级射极跟随器就成了简单的串联稳压：基极电流 I_B = I_L/h_FE(min) 是稳压管很轻的负载；R1 = (V_S − V_Z)/(I_Z + K·I_B)，K 取 1.2–2；输出比稳压管低约 0.65 V（V_BE）。
  - 这种电路仍对负载和输入变化敏感，加负反馈可以改善；它常作为更高级串联稳压电路的「预稳压」。

## 与前置节点的衔接

- P2 page2：稳压管模型 V = V_Z + r_Z·I_Z，1N4733A 取 V_Z = 5.1 V、r_Z = 7 Ω；I_ZK 1 mA、I_ZM 178 mA、P_Z 1.3 W，「实际功耗 V_Z·I_Z 留一半余量」；三极管 V_BE ≈ 0.7 V、I_C = β·I_B。
- P2 page3：2N3904 在 50 mA 时 β 最小 60；onsemi 2N3904 手册（https://www.onsemi.com/pdf/datasheet/2n3904-d.pdf，2026-10-23 核对）：I_C = 100 mA、V_CE = 1 V 时 h_FE 最小 30，额定功耗 625 mW。本节变体（100 mA）按 β = 30 估算。
- 06 page2：桥式整流滤波输出带 100 Hz 纹波，纹波 ΔV ≈ I/(2fC)。
