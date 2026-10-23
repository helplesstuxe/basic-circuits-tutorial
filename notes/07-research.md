# 07 射极跟随器 · 资料笔记（作者 D）

以下每条都打开过原网页。

## 原理（厂家应用笔记 / 数据手册）

1. ADI 大学课程 Chapter 9 Single Transistor Amplifier Stages，9.4 Voltage followers <https://wiki.analog.com/university/courses/electronics/text/chapter-9>
   - 射极跟随器 = 共集电极：输入阻抗远高于输出阻抗，叫"缓冲"。
   - 增益总小于 1（r_E 与 R_L 分压）；输入输出之间差一个 V_BE，约 0.65 V。
   - 作用是电流 / 功率增益和阻抗匹配，不是电压增益；基极电流约是发射极电流的 1/β（约 1/100）。
   - 例题：V_in 5.6 V、V_BE 按 0.6 V 估，V_out 5 V；R_L 1 kΩ → I_E 5 mA、r_E 5 Ω。
2. TI LM358 数据手册 SLOS068AB（2024-10 修订）<https://www.ti.com/lit/ds/symlink/lm358.pdf>
   - LM358（5.7 节表）：V_S = 15 V、V_O = 0 V 时输出拉电流（Source）最小 20 mA、典型 30 mA；短路电流典型 ±40 mA、最大 ±60 mA。
   - LM358B（5.5 节表）：输出高电平离正电源 1.4 V（1 mA，典型）。
3. TI AN-272 Op Amp Booster Designs <https://www.ti.com/lit/an/snoa600b/snoa600b.pdf>
   - IC 工艺限制运放输出功率，需要"助推级"；通常把助推级放进运放的反馈环里，以保住低漂移和稳定的增益。
   - 助推级有自己的相移，要注意振荡。互补射极跟随器用 D2、D3 补偿两管 V_BE，避免交越失真。
4. TI AN-4 Monolithic Op Amp—The Universal Linear Component <https://www.ti.com/lit/an/snoa650b/snoa650b.pdf>
   - 不在反馈环里的射极跟随器接长电缆时常常振荡；接在运放输出后也可能振荡，常用磁珠串在跟随器与电缆之间解决。
   - 50 mA 的缓冲器至少要 0.1 μF 的电源旁路电容。
5. Central Semiconductor TIP31 系列数据手册（Mouser 托管）<https://www.mouser.com/datasheet/2/68/tip31-845511.pdf>
   - I_C 连续 3 A；P_D 40 W（管壳 25 °C，需散热片）、2.0 W（环境 25 °C，不加散热片）；θ_JA 62.5 °C/W；T_J 最高 150 °C。
   - h_FE ≥ 25（V_CE 4 V、I_C 1 A），10–50（3 A）；V_BE(on) ≤ 1.8 V（3 A）。
6. Semelab 2N3904 数据手册（Farnell 托管）<https://www.farnell.com/datasheets/1686115.pdf>
   - I_C 200 mA；P_D 350 mW（T_A 25 °C）；h_FE 100–300（V_CE 1 V、I_C 10 mA）。
   - 注意：不同厂家的 2N3904 功耗额定不同。全书统一采用 onsemi 2N3903/2N3904 手册：TO-92、环境 25 °C 时 625 mW（每升高 1 °C 减 5 mW），θ_JA 200 °C/W；h_FE 最小值 10 mA 时 100、50 mA 时 60、100 mA 时 30（https://www.onsemi.com/download/data-sheet/pdf/2n3903-d.pdf）。本节点页面按 onsemi 625 mW 举例，Semelab 的 350 mW 只作对比记录。

## 推导 / 教程

7. Wikipedia Common collector <https://en.wikipedia.org/wiki/Common_collector>
   - 可看成"全部输出串联负反馈"：V_BE = V_in − V_out，晶体管自动调整让发射极 = 输入 − 近似恒定的 V_BE。
   - A_v ≈ 1；r_in ≈ β·R_E；r_out ≈ R_source/β（R_E 大时）；电流增益 β + 1。
   - 共集电极常用作 B 类、AB 类输出级。
8. Electronics Tutorials Common Collector Amplifier <https://www.electronics-tutorials.ws/amplifier/common-collector-amplifier.html>
   - 输出比基极低约 0.7 V，同相；r'_e = 25 mV / I_e；输出幅度一般是输入的 98%–99%；电流增益 γ = I_E/I_B = β + 1。
9. Electronics Tutorials Crossover Distortion <https://www.electronics-tutorials.ws/amplifier/amp_7.html>
   - 推挽（B 类）在过零附近两管都不导通，出现"平台 / 死区"，因为硅管 V_BE 要到约 0.7 V 才导通；小信号时更严重。
   - 用两只二极管给两管预偏置（AB 类）可大大减小。

## 代码

10. PySpice 1.5 例子 Bipolar Transistor <https://pyspice.fabrice-salvaire.fr/releases/v1.5/examples/transistor/transistor.html>
    - 用 SPICE 模型（2n2222a）做 DC 扫描画 I_B–V_BE 曲线，0.65 V 处画参考线；本节点没有用 SPICE，而是在 code/07_sim.py 里用指数模型 I_C = I_S·e^(V_BE/V_T) 自己解，思路相同。

## 常见错误（汇总）

- 忘记 V_BE：想要 5 V，实际只有约 4.3 V（ADI 例题、Electronics Tutorials）。解决：把运放反馈取自发射极（AN-272）。
- 管子功耗过大：P = V_CE × I_C；小管子 2N3904 只有 625 mW（onsemi，环境 25 °C；Semelab 版只有 350 mW），要换 TIP31 这类功率管并估算温升（θ_JA）。
- 单电源下输入低于约 0.7 V 时管子截止，输出削到 0（Wikipedia：输出只能从 V_BE 跟到 V+）。
- 跟随器接长线 / 容性负载振荡（AN-4），加磁珠或基极串小电阻。基极电阻阻值已核实：AN-4（SNOA650B）第 6 页图 8 High Current Output Buffer 中 LM101 输出经 R1 = 470 Ω 接 2N2222/2N2905 互补管基极，正文 "R1 is included to eliminate parasitic oscillations from the output transistors"；同段建议集电极各串 50 Ω 限流。正文 page3 按此取 470 Ω，压降数字由 code/figs/07_figs.py 的 rout_rin_rb() 打印。
