# 32 电荷放大器 · 调研笔记（作者 A）

## 理论
- TI SLOA033A《Signal Conditioning Piezoelectric Sensors》https://www.ti.com/lit/an/sloa033a/sloa033a.pdf （已打开）：
  - 电荷模式 V_o = −Q/C_f；
  - 下限频率 f_L = 1/(2π·R_f·C_f)；
  - 电荷模式下电缆电容不影响增益（电缆两端都在虚地上）；电压模式下电缆电容与传感器电容分压。
- 横河 YEWFLO 涡街技术报告 https://web-material3.yokogawa.com/rd-tr-r00027-004.pdf （已打开）：
  - f = K_T·Q（频率正比流量）；
  - 压电元件电荷 q ∝ 应力 σ ∝ 升力 F ∝ C_L·ρ·v²；
  - 两片压电元件差动以抵消管道振动；信号经电荷转换器。
- Emerson Rosemount 8800 涡街 ADSP 技术说明 https://www.emerson.com/documents/automation/technical-note-vortex-adaptive-digital-signal-processing-8800-series-rosemount-en-76500.pdf （已打开）：斯特劳哈尔常数、K 系数，自适应数字滤波（与 34/35 节衔接）。
- TI LMC6482（20 fA）、TL072（JFET）数据手册见 31-research。

## 推导链
1. 压电片 = 电荷源 Q 并联电容 C_p。电压模式开路电压 V = Q/(C_p + C_cable)：电缆一长读数就变。
2. 电荷放大器：反相端虚地，C_p 和电缆两端电压都约为 0，Q 全部转移到 C_f → V_o = −Q/C_f。
3. 没有 R_f 时偏置电流会把 C_f 充满；加 R_f → 一阶高通 f_L = 1/(2πR_fC_f)，所以不能测静力。
4. 涡街：信号幅度 ∝ ρv²，频率 ∝ v（为 35 节 AGC 埋伏笔）。

## 算例（calc.py 已复核）
- C_f = 1 nF、R_f = 100 MΩ：f_L = 1.59 Hz。
- 测试注入：100 pF 串联电容 + 1 V 阶跃 → Q = 100 pC → V_o = −0.1 V（C_f = 1 nF）。

## 常见错误
- 不加 R_f → 输出慢慢漂到电源轨。
- 用 LM358（I_B 在 R_f = 100 MΩ 上产生大偏移）。
- 以为可以测静压/静力（f_L 限制）。
- 压电片敲击尖峰直接进运放输入（需要串联电阻 + 钳位，见 00-design-part2 安全节）。
- 把电荷灵敏度单位 pC 与 pF 混淆。

## 图与原理图计划
- 图 32-p1-1 电压模式 vs 电荷模式（电缆电容变化时的输出对比，32_figs.py）。
- 图 32-p2-1 电荷放大器原理图（含压电等效电路）；图 32-p2-2 f_L 波特图。
- 图 32-p3-1 涡街原理示意（旋涡交替脱落 → 压电片受力）。
- 图 32-p4-1 面包板 + 32_p4_k_schem_lab.png。

## SPICE 计划（spice/32/）
- 32_charge.cir：100 pF 串联注入 1 V 阶跃，C_f 1 nF、R_f 100 MΩ，验证 −0.1 V 与 1.59 Hz 衰减（τ = 0.1 s）。
- 32_cable.cir：电缆电容 100 pF / 1 nF / 10 nF，电压模式与电荷模式输出对比。

## page4 实验
- TL072（或 LMC6482）±6 V 或 12 V + 虚地；C_f 1 nF，R_f 100 MΩ（买不到可用 10 MΩ，f_L = 15.9 Hz，需作者确认文字）。
- 先用 100 pF + 1 V 阶跃校准，再接压电蜂鸣片（串 10 kΩ + 两个 1N4148 钳位），手指敲击看输出。
- 在输入端并联 1 nF 模拟“长电缆”，证明输出幅度基本不变。

## 未用·待核实
- 压电蜂鸣片的电荷灵敏度没有找到可靠数据手册数值，正文不给具体 pC/N 数字。
