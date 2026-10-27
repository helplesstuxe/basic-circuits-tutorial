# 42 流量计信号链综合（capstone） · 调研笔记（作者 C）

## 理论（六条信号链，每条都回指前面的节点）
1. 电磁：线圈恒流换向（39）→ 电极 → INA，增益 ≤ 10（30）→ 带通 / 数字 FIR（33）→ 同步检波（38）→ 4–20 mA（41）。
   - 来源：ADI《Electromagnetic Flow Meters》https://www.analog.com/en/resources/analog-dialogue/articles/electromagnetic-flow-meters.html （curl 自盒子超时，WebFetch 可打开）。
   - 文中数据：
     - 灵敏度 150–200 µV/(m/s)；
     - 第一级 INA 增益 ≤ ×10；
     - 6.25 Hz 励磁，0.5–2 m/s 范围内误差 ±0.2%（DN25 传感器）；
     - 线圈几十到几百 mH，串联电阻 50–100 Ω；
     - 励磁电流从小口径的 50 mA 到大口径的 500 mA–1 A。
2. 超声时差：40 kHz 换能器 → TIA 或电荷放大（31/32）→ 带通（33）→ PGA/AGC（35）→ 过零比较（36/37）→ TDC / 计时器（37）。
   - 来源：TI SLAAES9、SNIA020、TDC1000、TDC7200（见 37-research）。
3. 涡街：漩涡压电片 → 电荷放大（32）→ 跟踪滤波 / 开关电容（34）→ 施密特整形（36）→ 计频。
   - 来源：Emerson 8800 技术说明 https://www.emerson.com/documents/automation/technical-note-vortex-adaptive-digital-signal-processing-8800-series-rosemount-en-76500.pdf （已打开）。
   - 漩涡频率与流速成正比（F ∝ k·V）。
   - Strouhal 数由发生体尺寸和形状决定；选好发生体后，它在很宽的范围内保持不变。
   - Qv = F/K，K 系数（pulses per volume）由流量实验室标定。
4. 涡轮：磁电或霍尔拾取 → 施密特整形（36）→ 计数 → 用 K 系数换算。
   - 来源：FLOMEC《Turbine Flow Meter Frequency and K-Factor》https://flomecmeters.com/blogs/did-you-know/turbine-flow-meter-frequency-and-k-factor （已打开）。
     - 例：500 Hz、K = 100 pulses/gal → 500 × 60/100 = 300 gpm；
     - 校准报告给出不同流量下的多个 K 系数。
   - 来源：Omega 涡轮/叶轮参考资料 https://br.omega.com/omegaFiles/Green/pdf/TURBINE_PADDLE_REF.pdf （已打开）。
5. 热式：RTD 恒温差（40）→ 电桥 + INA（30）→ 4–20 mA（41）。
   - 来源：Sierra 资料（见 40-research）。
6. 差压：孔板 → 差压变送器 → 开方 → 4–20 mA（41）。
   - Rosemount 405 手册 https://www.emerson.com/is/content/emerson/en/measurement-instrumentation/technical/products/dp-flow/documents/dl-rmt-00821-0100-4810.pdf （已打开）：流量与 DP 的关系式，Q 与 K、DP、ρ 有关（原文公式为图片，正文写“Q 与 √(DP/ρ) 成正比”，作者在 page2 注明这是伯努利关系的标准形式）。
   - Rosemount 3051S 手册 https://www.emerson.com/is/content/emerson/en/measurement-instrumentation/technical/products/pressure/documents/doc-rosemount-3051s-00809-0100-4801.pdf （已打开）：
     - 有 Linear 和 Square Root 两种输出；
     - 接近零时自动切到线性：0–0.6% 斜率为 1，0.6–0.8% 斜率为 42；
     - 原文警告：两处都设为开方 “would cause the square root function to be performed twice”。

## 推导链
- 每条链路都按“传感器给出什么量（电压 / 电荷 / 电流 / 频率 / 时间 / 电阻）→ 哪一节的电路把它变成什么 → 最后输出什么”来串。
- 关键是认出信号的种类：
  - 幅度信号（电磁、热式、差压）怕漂移和共模；
  - 频率信号（涡街、涡轮）怕丢脉冲和多计脉冲；
  - 时间信号（超声）怕触发点随幅度漂移。

## 算例（calc.py 已复核）
- 涡轮：500 Hz × 60 / 100 = 300 gpm（FLOMEC 原例）。
- 差压开方：DP 为满量程的 25% → 流量为满量程的 50%；DP 为 1% → 流量为 10%。
- 电磁：175 µV/(m/s) × 1 m/s × G10 = 1.75 mV。

## 常见错误
- 把开方做两次（3051S 原文警告）。
- 用同一个 K 系数覆盖全量程（FLOMEC 指出 K 系数随流量变化）。
- 把电磁流量计的输入当成普通直流放大来做（极化电压）。

## 图与原理图计划
- 图 42-p1-1 六条链路总图（42_figs.py，节点编号着色）；
- 图 42-p2-1 / 42-p2-2 / 42-p3-1 / 42-p3-2：每条链路的方框图 + 关键原理图；
- 图 42-p3-3 开方曲线与小信号切除；
- 图 42-p4-1 面包板 + 42_p4_k_schem_lab.png。

## SPICE 计划（spice/42/）
- 42_vortex_chain.cir：压电等效（电压源 + 1 nF）→ 电荷放大 → 带通 → 施密特，输入 50–500 Hz 正弦，加噪声，检查不丢脉冲。
- 42_dp_sqrt.cir：用 B 源算 √x，并与“开方两次”的输出对比。

## page4 实验（与 00-design-part2 第 6 节一致）
- 主方案：风扇扇叶 + 红外 LED / 光电二极管对射 → TIA（31）→ 带通（33）→ 施密特（36）→ Arduino 测频 → 按 K 系数换算“流量”。再经 PWM + RC → V→I（41）输出 4–20 mA，接收端 250 Ω 读回；拔线测试断线报警。
- 备选（零件不全时）：3 线电脑风扇的测速线直接接施密特整形（36），跳过 TIA 和带通。
- 安全：全部 ≤ 12 V；风扇叶片加罩。

## 未用·待核实
- 「[待核实]」E+H 涡街 / 超声 / 电磁学习页面（JS 验证页）。
- 「[待核实]」tomarok VY 涡街 PDF（验证码）。
