# 39 恒流源与线圈励磁驱动 · 调研笔记（作者 D）

## 理论
- TI SNOA474A（AN-1515《A Comprehensive Study of the Howland Current Pump》）https://www.ti.com/lit/an/snoa474a/snoa474a.pdf （已打开）：Howland 电流泵要求 R1/R2 = R3/R4，失配会让输出阻抗下降（电流随负载变化）。
- TI SBOA046（XTR110 电压-电流转换与电流泵）https://www.ti.com/lit/an/sboa046/sboa046.pdf （已打开）：电压控制电流源结构。
- TI DRV8871 https://www.ti.com/lit/ds/symlink/drv8871.pdf （已打开）：6.5–45 V，PWM ≤ 200 kHz，内置电流限制；真值表中 IN1 = IN2 = 1 为 “Brake; low-side slow decay”；数据手册说明续流经高边或低边 FET 的体二极管。
- EM（见 38-research）：线圈几十到几百 mH + 50–100 Ω；小口径励磁电流可到 50 mA，大口径 500 mA–1 A。
- Embien 博客（见 38-research）：MOSFET H 桥 + 恒流吸收电路，约 150 mA 到 1 A 以上。
- 第一部分回指：21 节线性稳压（运放 + 调整管 + 反馈，与恒流源同构）；06 节 MOS 管开关；26 节 H 桥与死区。

## 推导链
1. 运放 + MOSFET + 采样电阻 R_s：运放使 R_s 上电压 = V_ref → I = V_ref/R_s，与负载无关（只要 MOSFET 还在线性区）。
2. 顺从电压：V_supply ≥ I·R_load + I·R_s + V_DS(min)。超出后电流开始下降。
3. MOSFET 管耗：P = V_DS·I = (V_supply − I·R_load − I·R_s)·I；负载越小管耗越大。
4. 换向：恒流源串在 H 桥下面（或 H 桥 + 电流检测闭环）；线圈电流 i(t) 按 τ = L/R 指数趋近设定值。如果驱动电压更高，恒流源就能更快“推”到设定值（高压快速换向的原理，只讲概念）。
5. Howland：一个运放 + 四只电阻，可以输出双向电流；电阻比匹配决定输出阻抗。

## 算例（calc.py 已复核）
- 12 V、100 mA、负载 47 Ω + 采样 10 Ω：V_DS = 12 − 4.7 − 1.0 = 6.3 V，P = 0.63 W。
- 线圈 100 mH / 75 Ω：τ = 1.33 ms；6.25 Hz 半周期 80 ms ≈ 60τ，稳定充分。

## 常见错误
- 采样电阻放在负载高端，运放输入共模超出范围。
- 不算管耗，MOSFET（无散热片）烫手。
- 运放驱动 MOSFET 栅极时振荡：栅极串 100 Ω 左右、反馈加小电容（作者用 SPICE 确认数值）。
- 感性负载断开时没有续流通路（分立 H 桥必须加二极管；DRV8871 依靠 FET 体二极管）。
- 用 LM358 输出接 IRLZ44N 时忽略 LM358 输出上限（约 V+ − 1.5 V），12 V 供电下够用，5 V 供电下要算。

## 图与原理图计划
- 图 39-p1-1 恒压源 vs 恒流源（负载变化时）；图 39-p2-1 运放 + MOSFET 恒流源原理图；图 39-p2-2 电流 vs 负载电阻（顺从极限，39_figs.py）；图 39-p2-3 Howland 原理图；图 39-p3-1 线圈换向电流波形（τ = 1.33 ms）。
- 图 39-p4-1 面包板 + 39_p4_k_schem_lab.png（两张：恒流源、H 桥励磁）。

## SPICE 计划（spice/39/）
- 39_ccs.cir：LM358 + IRLZ44N + 10 Ω，V_ref 1 V，负载 0–120 Ω .step，画 I 与 V_DS、P。
- 39_coil.cir：DRV8871 用理想开关 H 桥代替 + 100 mH/75 Ω，6.25 Hz 换向，看电流波形与 τ。
- 39_howland.cir：四电阻 10 k，失配 1% 时输出阻抗。

## page4 实验
- 12 V，LM358 + IRLZ44N + 10 Ω（1 W）采样电阻，V_ref 由 5 V 分压得 1 V → 100 mA。负载 10/22/47/68/100 Ω（功率足够），测电流和 MOSFET 温度。
- 第二部分：DRV8871 模块（VM = 12 V）+ 线圈（继电器线圈或自绕线圈 + 串联电阻）+ 1 Ω 采样，Arduino 以 6.25 Hz 换向，Arduino ADC 或示波器看采样电阻电压。
- 安全：MOSFET 可能超过 60 °C，不要用手摸。

## 未用·待核实
- 「[待核实]」ST L298 数据手册（st.com curl 超时，未打开，不用）。
