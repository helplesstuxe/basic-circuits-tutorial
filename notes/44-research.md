# 44 D 类放大与 PWM · 调研笔记（作者 D）

## 理论
- TI SLOA290A（白皮书）https://www.ti.com/lit/wp/sloa290a/sloa290a.pdf （已打开）：D 类放大器一般约 90% 效率，约 10% 的损耗变成热。
- TI SLAU508（TI Precision Designs《Analog Pulse Width Modulation》）https://www.ti.com/lit/pdf/slau508 （已打开）：
  - 5 V 供电，输出 5 Vp、500 kHz PWM；
  - 用比较器比较三角波和输入信号；
  - PWM 经低通滤波后得到平均电压：5 V × 75% = 3.75 V；
  - C1 = 100 pF 在 159 kHz 处形成一个极点。
- TI SLAA701B《LC Filter Design》https://www.ti.com/lit/an/slaa701b/slaa701b.pdf （已打开；旧链接 sloa119b 会重定向到这里）：
  - 一般 10 W 以上的 D 类放大器需要输出 LC 滤波；
  - Type-1 例子：L_BTL = 10 µH，C_BTL = 0.68 µF。
- TI SLOA145《LC Filter Design for Class-D》https://www.ti.com/lit/an/sloa145/sloa145.pdf （已打开）：说明为什么传统 D 类需要 LC 滤波器，以及 EMC 需要时用 LC 或磁珠。
- TI DRV8871（见 39-research）：可以当作“大号 H 桥”，演示 PWM 驱动。
- 回指：26 节 H 桥、10 节比较器、01 节 RC、25 节开关电源的电感滤波。

## 推导链
1. 三角波 + 比较器 → PWM 占空比 D 与输入电压成正比。
2. 平均值 = D × V_supply；滤掉载波之后就是放大的音频。
3. 开关管只在“全开”（压降小）和“全关”（电流为 0）两种状态之间切换，所以 P = V × I 很小，效率高。
4. LC 低通 f0 = 1/(2π√(LC))，要远低于载波、远高于 20 kHz。
5. BTL（桥接）：两路反相输出，负载两端摆幅加倍 → 同一电源下功率为单端的 4 倍。
6. “无滤波”D 类（PAM8403）依靠喇叭本身的电感和调制方式工作，导线长时有 EMI 风险（SLOA145）。

## 算例（calc.py 已复核）
- 5 V × 75% = 3.75 V（SLAU508 原例）。
- 10 µH / 0.68 µF：1/(2π√(LC)) = 61 kHz（作者按单节 LC 计算；BTL 等效以原文为准）。
- 实验用 LC：二阶巴特沃斯 L = R/(Q·ω0)、C = Q/(R·ω0)，R = 8 Ω、Q = 0.707、f0 = 30 kHz → 60 µH / 0.47 µF；反算 f0 = 30 kHz（calc.py：f0 = 1/(2π√(60e-6 × 0.47e-6)) ≈ 30.0 kHz）。
- 乙类对比：同样 5 W 输出，78.5% 效率时损耗约 1.4 W，90% 时约 0.56 W。

## 常见错误
- 载波频率太低（几 kHz），能听见“啸叫”。
- LC 截止频率选在 20 kHz 以下，高音被削弱。
- 用示波器地夹去测 BTL 的输出（两端都不是地，会短路）。
- 只看占空比，忽略死区，导致上下管直通。

## 图与原理图计划
- 图 44-p1-1 三角波比较 → PWM（44_figs.py）；
- 图 44-p1-2 PWM 的平均值；
- 图 44-p2-1 比较器 + 三角波发生器原理图（LM393 + TL072）；
- 图 44-p2-2 半桥 / H 桥 + LC；
- 图 44-p3-1 LC 滤波频响；
- 图 44-p3-2 BTL 摆幅示意；
- 图 44-p4-1 面包板 + 44_p4_k_schem_lab.png。

## SPICE 计划（spice/44/）
- 44_pwm.cir：三角波 20–50 kHz + LM393 比较 1 kHz 正弦 → 理想开关半桥 12 V → LC 60 µH / 0.47 µF → 8 Ω；用 .four 看 1 kHz 分量，并估算效率。
- 44_lc.cir：AC 扫描，带 8 Ω 负载与不带负载各一次，看 Q 峰。

## page4 实验
- TL072 方波 + 积分器做约 20–30 kHz 三角波 → LM393 比较 → 观察 PWM（Arduino 采样或 LED 亮度）；
- 输出接 DRV8871 模块（12 V）→ LC → 8 Ω 喇叭串 10 Ω；
- 对照：Arduino 自身 PWM（约 31 kHz 模式）+ RC 低通。
- 安全：≤ 12 V；电感和 MOSFET 可能发热。

## 未用·待核实
- 「[待核实]」ADI Analog Dialogue D 类放大器文章（curl 超时，未打开）。
