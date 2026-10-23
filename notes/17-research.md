# 17 自锁 · 资料笔记（作者 D）

以下网页/手册均已实际打开阅读。

1. EEPower《Understanding Three-Wire Control》https://eepower.com/technical-articles/understanding-three-wire-control/
   - 三线控制：常闭停止按钮与常开启动按钮串联；接触器的常开辅助触点并联在启动按钮两端，称 seal-in / hold-in / memory circuit。
   - 按住停止按钮时再按启动按钮无效（locked-stop）。
2. Open Textbook《Basic Motor Control — Manual Circuits》https://opentextbc.ca/basicmotorcontrol/chapter/manual-circuit/
   - 与启动按钮并联的常开触点使电路具有低电压保护（LVP）；停电后接触器释放，来电不会自行启动。
   - 实际中自锁触点在手指离开按钮之前就已闭合（"a fraction of a second"）。
   - 过载继电器常闭触点串联在线圈回路中。
3. 电工天下《接触器自锁正转控制线路的作用》https://www.dgjs123.com/jcq/12029.htm
   - 中文术语：自锁（自保）触头；欠电压保护（一般降到 85% 额定电压以下释放）；失压（零压）保护。
   - 注意：该文 SB1 为启动、SB2 为停止；本教程按 schem.py 约定 SB1 停止、SB2 启动，页面中说明不同书编号不同。
4. 技成培训网《自锁正转控制线路实现欠电压和失电压保护》https://www.jcpeixun.com/knowledge/detail/23610.html
   - 控制电路取 L1、L2 两相（380V 线电压）供线圈；热继电器 FR 发热元件串主电路、常闭触头串控制电路；热继电器不能做短路保护。
5. Schneider TeSys D 目录（LC1D09–LC1D25 控制电路特性）https://nanologicautomation.com/pdf/switch-gears/contractors/Schneider-Contactors-TesysD-Nano-Logic-Automation.pdf
   - 50/60 Hz 线圈：工作电压 0.85–1.1 Vc（50 或 60 Hz 线圈 0.8–1.1 Vc），释放电压 0.3–0.6 Vc。
   - 闭合时间 12–22 ms（LC1D25 为 15–24 ms），断开时间 4–19 ms。
6. ABB B6/B7 迷你接触器技术数据 https://www.ourdoconline.com/lpcp/1SBC100192C02/files/basic-html/page109.html
   - 按 IEC 60947-4-1：交流线圈工作范围 0.85–1.1 Uc；释放电压 0.20–0.75 Uc。
7. Kuphaldt, LibreTexts 6.4 Motor Control Circuits https://workforce.libretexts.org/Bookshelves/Electronics_Technology/Electric_Circuits_IV_-_Digital_Circuitry_(Kuphaldt)/06%3A_Ladder_Logic/6.04%3A_Motor_Control_Circuits
   - seal-in 触点的"latch"含义；停止按钮用常闭触点。
8. Kuphaldt, LibreTexts 6.5 Fail-safe Design https://workforce.libretexts.org/Bookshelves/Electronics_Technology/Electric_Circuits_IV_-_Digital_Circuitry_(Kuphaldt)/06%3A_Ladder_Logic/6.05%3A_Fail-safe_Design
   - 导线、触点最常见的故障是断开；应设计成断线时进入最安全的状态 → 停止用常闭、串联。

仿真采用的示意参数：吸合门限 85% Uc、释放门限 45% Uc（落在 0.3–0.6 之间）、吸合时间 20 ms（落在 12–22 ms 之间）。
9. IEC 60028 摘录（cabledatasheet.com）https://www.cabledatasheet.com/general-cable-information/notes-from-iec-60028/
   - 20°C 标准退火铜体积电阻率 1/58 = 0.017241 Ω·mm²/m。用于 page3 控制线长度估算。
   - 线圈启动（吸合）与保持功率：TeSys D LC1D09–D25 50/60 Hz 线圈吸合 70 VA、保持 7 VA（见第 5 条同一页）。
