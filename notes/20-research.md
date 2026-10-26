# 20 有源滤波 · 调研笔记（作者 A）

## 理论
- TI SLOA049《Active Low-Pass Filter Design》https://www.ti.com/lit/pdf/sloa049 （已打开，跳转到 sloa049b）：Sallen-Key 单位增益结构增益精度最好；MFB 灵敏度和高频特性更好；表 10-1 给出 fc = 1 kHz 巴特沃斯值 C1 = 10 nF、C2 = 33 nF、R1 = 4.22 kΩ、R2 = 18.4 kΩ（m = 0.229，n = 3.3，Q = 0.707）。本节仿真直接用这组值。
- TI SBOA293/SBOA294（低通滤波电路手册，已打开）：一阶/二阶低通设计流程与元件取值思路。
- TI SLOA024、SLOA093（已打开）：滤波器分类与阶数、巴特沃斯定义。

## 代码
- scipy.signal.lsim 文档（已打开）：用传递函数分子分母系数做时域仿真，本节 20_figs.py 用它算噪声滤除和方波响应。

## 常见错误
- 截止频率漏 2π：自己推导，R 会算大 2π 倍，fc 低到 159 Hz（图 20-p3-2）。
- 运放带宽不足：闭环带宽约 GBW/增益（08 节已核实 LM358B GBW 1.2 MHz）。
  - （本轮解决）经验法则出处改为 Microchip ADN003 https://ww1.microchip.com/downloads/en/DeviceDoc/adn003.pdf （已下载打开）：闭环带宽应至少为截止频率的 100 倍；Sallen-Key 增益 1：GBWP ≥ 100·fC；增益 > 1：GBWP ≥ 100·G·fC；MFB：GBWP ≥ 100·(−G + 1)·fC。
  - TI SBOA588 https://www.ti.com/lit/pdf/sboa588 （已打开）：许多滤波设计工具推荐 GBWP 100 倍；修正无源元件可降低余量；其例子 GBWP 仅为滤波带宽 2.5 倍时误差约 17%。
  - 20_figs.py 打印并断言 100 × 1 × 1 kHz = 100 kHz ≤ 1.2 MHz，100 × 10 × 100 kHz = 100 MHz。
- Sallen-Key 两个电容位置接反：Q 由 0.71 变成 0.21（自己计算）。
- （本轮解决）电容容差与材质影响 fc：
  - KEMET X7R 商用手册 https://media.digikey.com/pdf/Data%20Sheets/Kemet%20PDFs/X7R_Dielectric_Comm_Rev_2019.pdf ：−55～+125 °C 容量变化 ±15%；容差 ±5/±10/±20%；老化约 3%/十倍时间。
  - KEMET F3101（MIL-PRF-11015 引线 MLCC）https://content.kemet.com/datasheets/F3101_MIL-PRF-11015.pdf ：C0G 0 ± 30 ppm/°C，Class I 不受电压、频率、时间影响；X7R ±15%，Z5U +22/−56%；直流电压 > 5 V 时 Class II 容量下降；老化 C0G 无、X7R 2%/十倍时间。
  - TI SLOA049B 第 14 节 https://www.ti.com/lit/an/sloa049b/sloa049b.pdf ：电容避免 < 10 pF，用 C0G（NP0）、1%；电阻用低温漂金属膜 1%。
  - 页面删去未找到出处的"薄膜电容"；20_figs.py 打印并断言 30 ppm × 100 °C = 0.3%、两电容同时 −15% → fc +17.6%。
