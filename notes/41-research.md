# 41 4–20 mA 电流环 · 调研笔记（作者 C）

## 理论
- TI XTR115/XTR116 数据手册 https://www.ti.com/lit/ds/symlink/xtr115.pdf （已打开）：
  - 两线制 4–20 mA 发送器；I_O = 100·I_IN；
  - 内部基准 2.5 V（XTR115）/ 4.096 V（XTR116），5 V 稳压输出 V_REG 给外部电路供电；
  - 回路电源 7.5–36 V；静态电流 200 µA；
  - 下限 I_MIN 0.2 mA（典型），上限 I_LIM 32 mA。
- TI XTR111 https://www.ti.com/lit/ds/symlink/xtr111.pdf （已打开）、XTR110 https://www.ti.com/lit/ds/symlink/xtr110.pdf （已打开）：三线制电压-电流转换器（变体）。
- TI TIDUAO7（两线制 4–20 mA 参考设计）https://www.ti.com/lit/ug/tiduao7/tiduao7.pdf （已打开）：电源 ≤ 36 V；顺从电压 V_S − 12 V（表中另列 7.5 V，作者引用时说明是哪个条件）。
- TI DAC161S997 https://www.ti.com/lit/ds/symlink/dac161s997.pdf （已打开）：报警电流 3.375 mA / 21.75 mA。
- Beckhoff NAMUR 说明页 https://infosys.beckhoff.com/content/1033/ioanalogmanual/3904850187.html （已打开）：NE43（2003-02-03 版）：故障 ≤ 3.6 mA，测量 3.8–20.5 mA，故障 ≥ 21.0 mA。
- WAGO 750-492/040-001 手册 https://www.wago.com/wagoweb/documentation/750/eng_manu/modules/m07500492_00400001_0en.pdf （已打开）：测量范围 3.8–20.5 mA；≤ 3.6 mA 报错误/断线。
- NAMUR 新闻 https://www.namur.net/en/publications/news-archive/ne-43-has-been-revised.html （已打开）：NE43 于 2021-07-26 修订，增加了安全裕量。

## 推导链
1. 串联回路电流处处相等 → 导线电阻不改变电流（只要不超顺从极限）。
2. 4 mA 活零点：0% 对应 4 mA，0 mA 一定是故障（断线/掉电）；同时 4 mA 内两线制变送器还能“偷”电流给自己供电。
3. 接收：250 Ω → 1–5 V；100 Ω → 0.4–2.0 V。
4. 回路预算：R_loop,max = (V_supply − V_transmitter,min)/20 mA。
5. 两线制 XTR115：外部电路电流 + 静态电流都包含在回路电流中，所以外部电路必须 < 4 mA（减去余量）。
6. V→I：运放 + 晶体管 + R_s，I = V_in/R_s（39 节恒流源的应用）。

## 算例（calc.py 已复核）
- 24 V、变送器最低 7.5 V：(24 − 7.5)/0.02 = 825 Ω；12 V 时为 225 Ω。
- 250 Ω：4–20 mA → 1–5 V；100 Ω：0.4–2.0 V。
- XTR115：20 mA 需 I_IN = 200 µA；V_IN = 5 V 时 R_IN = 25 kΩ。

## 常见错误
- 接收电阻接错，电流根本没流过 250 Ω。
- 把 0 mA 当 0%。
- 回路电阻超过顺从极限，读数被“削顶”还以为正确。
- 两线制变送器的外围电路耗电超过 4 mA。
- 回路正负接反（有的变送器有反接保护，有的没有）。

## 图与原理图计划
- 图 41-p1-1 电压传输 vs 电流传输（导线压降）；图 41-p1-2 NE43 电流范围条（41_figs.py，数值按 Beckhoff 页面）；图 41-p2-1 V→I 原理图（LM358 + 2N3904 + 100 Ω）；图 41-p2-2 两线制 XTR115 框图；图 41-p3-1 回路电阻与顺从极限。
- 图 41-p4-1 面包板 + 41_p4_k_schem_lab.png。

## SPICE 计划（spice/41/）
- 41_vi.cir：12 V，LM358 + 2N3904 + 100 Ω，V_in 0.4–2.0 V，负载 250 Ω + 可变电阻 .step，找电流开始偏离的回路电阻（与 225 Ω 量级对比，注意本电路最低压降与 XTR115 不同，作者按仿真结果写）。

## page4 实验
- 12 V，LM358 + 2N3904（或 BD139）+ 100 Ω 采样电阻；Arduino PWM D9 + RC（10 kΩ/10 µF）给 0.4–2.0 V。
- 回路：12 V → 250 Ω 接收电阻（Arduino A0 读 1–5 V）→ 晶体管 → 100 Ω → 地。
- 测：设定 4/12/20 mA 读回；串联 100/220/470 Ω 找顺从极限；拔线看 0 mA，程序报“断线”。

## 未用·待核实
- 「[待核实]」NAMUR NE43 原文 PDF（会员/付费下载，未打开；数值引用 Beckhoff、WAGO）。
- 「[待核实]」ADI AD623 数据手册（curl 超时，未用）。
