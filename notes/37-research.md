# 37 过零检测与超声波时差 · 调研笔记（作者 B）

## 理论
- TI SNIA020（超声波水表/热量表应用笔记）https://www.ti.com/lit/an/snia020/snia020.pdf （已打开）：
  - 顺流/逆流传播时间差 ΔT·(c² − v²) = 2Lv，v ≪ c 时 ΔT·c² ≈ 2Lv；
  - 用 TDC7200（picosecond-accuracy stopwatch）测时间；文中“Measurement Accuracy Considerations”一节说，加阻抗匹配电路后，两只换能器的 ΔTOF 偏移温漂可降到约 25 ps 或更小（STOP 脉冲 1 和 5）。注意这是温漂，不是分辨率。
- TI SLAAES9（超声波流量计设计指南）https://www.ti.com/lit/an/slaaes9/slaaes9.pdf （已打开）：式 1–4：T12 = L/(c + v)，T21 = L/(c − v)，Δt = T21 − T12，消去 c 得 v = (L/2)·(1/T12 − 1/T21) = L·Δt/(2·T21·T12)（L 为沿流动方向的声程；PDF 文本层公式排版错乱，作者需看原 PDF 式 4 核对）。
- TI TDC7200 https://www.ti.com/lit/ds/symlink/tdc7200.pdf （已打开）：分辨率 55 ps。
- TI TDC1000 https://www.ti.com/lit/ds/symlink/tdc1000.pdf （已打开）：超声前端，激励频率 31.25 kHz–4 MHz，集成 PGA、门限比较器与过零比较器。
- Murata MA40S4S 数据手册 https://www.murata.com/~/media/webrenewal/products/sensor/ultrasonic/open/datasheet_maopn.ashx?la=en （已打开）：中心频率 40.0 kHz；声压 120 ± 3 dB（10 Vrms，30 cm）；灵敏度 −63 ± 3 dB；电容 2550 pF ± 20%；最大驱动 20 Vp-p。
- Wikipedia《Speed of sound》https://en.wikipedia.org/wiki/Speed_of_sound （已打开）：20 °C 空气 343 m/s，20 °C 淡水 1481 m/s。

## 推导链
1. 顺流 t1 = L/(c + v)，逆流 t2 = L/(c − v)。
2. Δt = t2 − t1 = 2Lv/(c² − v²) ≈ 2Lv/c²。
3. 用 t1、t2 反算（消去 c）：1/t1 − 1/t2 = 2v/L → v = (L/2)·(1/t1 − 1/t2) = L·Δt/(2·t1·t2)，与 SLAAES9 式 4 一致；好处是不需要知道声速，温度影响被消掉。
4. 为什么要过零：回波是包络 × 载波；幅度门限触发的时刻随幅度变化而移动，而载波过零点时刻不随幅度变。
5. 两级检测：先“武装”（幅度超过门限，说明回波到了），再在下一个过零沿触发。
6. 跳周期：门限设得不当，一会触发在第 n 个周期、一会第 n+1 个，误差 = 一个载波周期。

## 算例（calc.py 已复核）
- 水：L = 0.1 m、c = 1481 m/s：v = 1 m/s → Δt = 91.2 ns；v = 1 cm/s → 0.91 ns（说明为何要 ps 级 TDC）。
- 空气：L = 0.2 m、c = 343 m/s：t = 583 µs；每 1 mm 声程 2.92 µs；v = 3 m/s → Δt = 10.2 µs（Arduino 62.5 ns 分辨率足够）。
- 40 kHz 周期 25 µs → 跳一个周期就是 25 µs 误差（比 3 m/s 的 Δt 还大）。

## 常见错误
- 跳周期，读数忽大忽小 25 µs。
- 发射时的电串扰/机械串扰被当成回波（需要“盲区”时间窗）。
- 忽略温度对声速的影响（空气中 c 随温度变化，用 SLAAES9 的两时间法可消去 c）。
- 超过换能器 20 Vp-p 上限驱动。
- 把 Δt 当成单程传播时间。

## 图与原理图计划
- 图 37-p1-1 顺流/逆流示意；图 37-p1-2 回波包络 + 幅度门限 vs 过零触发（37_figs.py）；图 37-p2-1 接收链原理图（带通 + 放大 + 门限比较 + 过零比较 + 与门/D 触发器）；图 37-p3-1 跳周期示意。
- 图 37-p4-1 面包板 + 37_p4_k_schem_lab.png。

## SPICE 计划（spice/37/）
- 37_zc.cir：用 B 源生成 40 kHz 猝发（包络上升），两个比较器 + 逻辑，幅度 ×0.5 / ×1 / ×2 时比较输出边沿时刻：幅度门限漂移、过零边沿不漂移。

## page4 实验
- 两只 40 kHz 换能器（MA40S4S 或同类）在一根 PVC 管两端相对放置，间距约 0.2 m。
- 发射：Arduino 两个引脚反相输出 8 个周期 40 kHz（5 V 推挽得 10 Vp-p，低于 20 Vp-p 上限）。
- 接收：TL072 带通/放大（40 kHz 附近）→ LM393 门限 + LM393 过零 → D 触发器（或 Arduino 软件逻辑）→ Timer1 输入捕获。
- 测：改间距验证 2.92 µs/mm；USB 风扇从一端吹，交换收发方向测 Δt（约 10 µs 级）。
- 安全：全部 ≤ 5 V/12 V。

## 未用·待核实
- 无（SNIA020 的 25 ps 已核对上下文：是 ΔTOF 偏移温漂，见上）。

## 定稿补记（作者 B，写完 page1–4 后）
### 来源核对（全部重新打开过）
- SLAAES9 实际标题「Ultrasonic Sensing Solution (USS) Guide」，作者 Hao Mengzhen（pdftotext 核对）。§2.2「TDC approach (zero-crossing…)」讲过零 + TDC；absTOF 给出整周期差。Figure 2-5 / 2-6 是互相关滑移 1、5 个周期的示意，**不是**跳周期示意（page3 参考文献已按此改写）。
- SNIA020 实际标题「Ultrasonic Sensing for Water Flow Meters and Heat Meters」（Bahram Mirshab，2015 年 4 月）；Figure 2 有「Qualifying threshold setting」（武装门限）。
- SN74HC74 https://www.ti.com/lit/ds/symlink/sn74hc74.pdf （SCLS094F）：4.5 V 时建立时间 20 ns，VIH 3.15 V，VIL 1.35 V；推荐 VCC 2–6 V。
- TL072 https://www.ti.com/lit/ds/symlink/tl072.pdf ：共模输入下限约 V− + 4 V → 至少 10 V 供电（本节用 12 V 适配器）。
- LM393 https://www.ti.com/lit/ds/symlink/lm393.pdf ：输入 < VCC − 1.5 V（全温度 VCC − 2 V）。
- ATmega328P（Microchip，downloads/en/DeviceDoc 版数据手册）：引脚最大 VCC + 0.5 V、40 mA；Timer1 输入捕获 ICP1 = D8。
- 接收头用 MA40S4R，发射用 MA40S4S（Murata，电容 2550 pF、20 Vp-p 上限）。
- 上面「算例」里的 2.92 µs/mm、583 µs 是初稿粗算；定稿用 37_sim：c(20 °C) = 343.24 m/s，2.913 µs/mm，L = 0.2 m → 582.69 µs = 9323 格。

### 设计偏离（与上面计划相比）
1. 发射不用 Timer2 OC 硬件翻转，改为 Timer1 同步的软件写 PIND/PINB 翻转（避免 Timer2 翻转奇偶不定）；OCR2A = 199 的方案在 page2 作为变体保留。
2. 过零比较器回差电阻用 4.7 MΩ（门限 +12.6 / +2.1 mV），不用 1 MΩ（59.0 / 10.0 mV 太大，作为 page2 例 2）。
3. 37_sim.py 增加了练习题一节（所有练习答案都由它算出并 assert）。
4. 无示波器时用万用表量 /Q2 平均电压：每轮 5 ms，V = 5 V·t/5 ms，即 1 mV/µs；核心结论（斜率 → 声速、风扇顺逆差约 10 mV）只看差值。
5. 74HC74 由 Arduino 5 V（B+ 跳线）供电，上拉只接 5 V。

### 定稿图表（14 张，code/figs/37_figs.py）
p1-1 up_down，p1-2 thr_vs_zc；p2-1 dt_vs_v，p2-2 schem，p2-3 timing，p2-4 timer1；p3-1 vth_staircase，p3-2 t_vs_amp，p3-3 spacing，p3-4 tx_current；p4-1 breadboard，p4-2 schem_lab，p4-3 fan_setup，p4-4 expected。

### SPICE
spice/37/（amp、tx、vth、zc 四个网表），29 项：✅ 22、⚠️ 1（×0.5 幅度时 LM393 过驱不足多跳一周期，783.78 vs 757.87 µs，page3 已写明）、ℹ️ 6，❌ 0。详见 review/spice/37.md。
