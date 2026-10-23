# 03 电压跟随器 · 研究笔记（作者 A）

## 理论
- TI SBOA269 缓冲器（跟随器）电路手册 https://www.ti.com/lit/pdf/sboa269 ：增益 1，输入阻抗高、输出阻抗低，用于隔离信号源与负载。
- TI SLAA068B https://www.ti.com/lit/an/slaa068b/slaa068b.pdf ：跟随器是同相放大 Rf = 0、R1 开路的特例。
- LM358B 数据手册 https://www.ti.com/lit/ds/symlink/lm358.pdf ：输入共模上限 V+ − 1.5 V；输出最低约 V− + 0.1 V；GBW 1.2 MHz。

## 实战代码 / 容性负载
- TI TIDU032C（容性负载驱动参考设计）https://www.ti.com/lit/pdf/tidu032 ：用隔离电阻 RISO（例 6.2 Ω）驱动 0.1 μF，设计相位裕度 45°、过冲约 23%（其运放并非 LM358B）。
- TI SSZT999（容性负载稳定性博客）https://www.ti.com/lit/pdf/sszt999 、SBOA418 https://www.ti.com/lit/pdf/sboa418 ：容性负载与运放输出电阻形成额外极点，相位裕度下降，阶跃出现振铃；串小电阻隔离。
- 本节容性负载图用一阶运放模型（GBW 1.2 MHz）+ 开环输出电阻 + 0.1 μF，scipy.signal.step 求阶跃响应。
- （本轮更正）开环输出电阻原用 50 Ω 假设值（原有核实标记，现已删除）；现已在 LM358B 数据手册 https://www.ti.com/lit/ds/symlink/lm358.pdf （LM358B/LM358BA 电气特性表，已下载打开）查到：RO open-loop output resistance 300 Ω（f = 1 MHz，IO = 0 A）；CLOAD capacitive load drive 100 pF。模型改用 300 Ω（按固定值处理，属简化）。
- 新结果（03_figs.py 打印并断言）：直接接 0.1 μF 最高 0.190 V、过冲 90%，60 μs 内不稳定；串 10 Ω 过冲 40%；串 33 Ω 最高 0.101 V、过冲 1.2%、8.2 μs 进入 ±2%；0.1 μF / 100 pF = 1000 倍；1 mA × 33 Ω = 33 mV。

## 常见误区
- 以为 1 倍没用（作用是阻抗变换/隔离）。
- 直接驱动大电容、长电缆导致振荡。
- 单电源下以为能 0～5 V 满幅跟随（LM358B 只有约 0.1～3.5 V）。
