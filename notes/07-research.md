# 07 三极管开关与继电器驱动 · 资料笔记（作者 D）

下面每条都是作者真的打开过的来源；没找到出处的数值在正文标「[待核实]」或写明「示意值」。

1. **onsemi 2N3904 数据手册** https://www.onsemi.com/download/data-sheet/pdf/2n3904-d.pdf
   - $V_{CEO}$ 40 V； $I_C$ 连续 200 mA；功耗 625 mW（TO-92，环境 25 °C，每升高 1 °C 减 5 mW）；结到环境热阻 $\theta_{JA}$ 200 °C/W（与 19 一致）；"useful dynamic range extends to 100 mA as a switch"。
   - $h_{FE}$ 最小：0.1 mA 时 40、1 mA 时 70、10 mA 时 100（最大 300）、50 mA 时 60、100 mA 时 30。
   - $V_{CE(sat)}$ ≤ 0.2 V（10 mA / 1 mA）、≤ 0.3 V（50 mA / 5 mA），即强制 β = 10 的测试条件； $V_{BE(sat)}$ 0.65–0.85 V（10 mA）、≤ 0.95 V（50 mA）。
2. **松乐 SRD 系列继电器数据手册**（alldatasheet 镜像）https://www.alldatasheet.com/html-pdf/1132639/SONGLERELAY/SRD-05VDC-SL-C/1713/2/SRD-05VDC-SL-C.html
   - 高灵敏型 5 V：71.4 mA、70 Ω ±10%、0.36 W；12 V：30 mA、400 Ω。标准型 5 V：89.3 mA、55 Ω、0.45 W。
   - 吸合电压最大 75%、释放电压最小 10%、最大允许电压 120%（标准型 110%）。
   - 触点 10 A 250 VAC / 10 A 28 VDC；吸合时间最大 10 ms、释放时间最大 5 ms。
   - 绝缘耐压：线圈与触点之间 1500 VAC，触点之间 1000 VAC。寿命：机械 10^7 次，电气 10^5 次。
   - 手册**没有给线圈电感**，仿真里的 0.1 H 是示意值。
3. **TI ULN2003A 数据手册** https://www.ti.com/lit/ds/symlink/uln2003a.pdf
   - 7 路达林顿；每路 500 mA；输出耐压 50 V；内置钳位二极管，COM 端接线圈电源。
   - 每路输入串了 2.7 kΩ 基极电阻，可直接接 5 V TTL / CMOS（3.3 V 也可用）。
   - $V_{CE(sat)}$ 典型 / 最大：100 mA 时 0.9 / 1.1 V、200 mA 时 1.0 / 1.3 V、350 mA 时 1.2 / 1.6 V。
   - 应用示例： $I_{COIL} = (V_{SUP} - V_{CE(SAT)})/R_{COIL}$ ，12–48 V 线圈、20–300 mA。
4. **TE Connectivity：线圈抑制与继电器寿命** https://www.te.com/en/products/relays-and-contactors/electromechanical-relays/intersection/coil-suppression-relay-life.html
   - 不加抑制时线圈感应电压可达数百甚至上千伏。
   - 只并二极管能把电压钳到二极管压降，但电流衰减慢，衔铁释放变慢，触点粘连、熔焊的风险变大。
   - 二极管串稳压管（齐纳管）衰减更快，稳压值按开关器件的耐压选。继电器的参数是在不加抑制时测的。
5. **Microchip ATmega48A/88A/168A/328/328P 数据手册** https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega48A-PA-88A-PA-168A-PA-328-P-DS-DS40002061B.pdf
   - 绝对最大额定值：每个 I/O 引脚 DC 电流 40.0 mA；VCC、GND 引脚 200.0 mA。
   - $V_{OH}$ 的测试条件： $I_{OH}$ = −20 mA、VCC = 5 V（85 °C 时最小 4.2 V）； $I_{OH}$ = −10 mA、VCC = 3 V（85 °C 时最小 2.3 V）。正文里「建议 20 mA」指这个测试条件。
6. **Finder 62 系列功率继电器样本** https://cdn.findernet.com/app/uploads/S62EN.pdf
   - "Reinforced insulation between coil and contacts according to EN 60335-1, with 6 mm clearance & 8 mm creepage distance"。用来说明：线圈侧到触点侧要留几毫米的电气间隙和爬电距离。

7. **欧姆龙 G5V-1 数据手册** https://xonstorage.z8.web.core.windows.net/pdf/Omron/4226465XON.pdf （本轮下载打开）
   - Coil Data 表（参考值）：5 V 款 167 Ω、30 mA，线圈电感 0.15 H（Armature OFF）/ 0.29 H（Armature ON）。page2 用它说明仿真取 0.1 H 与真实 5 V 小继电器同一量级。
8. **TI SLUAAR5《Circuit Board Insulation Design According to IEC60664 for Motor Drive Applications》** https://www.ti.com/lit/wp/sluaar5/sluaar5.pdf （本轮下载打开）
   - Clearance：按包括瞬态在内的最大峰值电压（overvoltage category [OVC] level）确定，污染等级、温度、湿度有影响。
   - Creepage：与 RMS/DC 电压有关，取决于污染等级和绝缘材料的 CTI。

## 原「待核实」项处理结果
- 线圈电感：仍用 0.1 H 示意值，正文改为引用 G5V-1 的 5 V 款 0.15～0.29 H 作量级依据；杂散电容 100 pF 在正文写明是示意值。
- 自制 PCB 上 220V 与低压走线的间距：正文引用 TI SLUAAR5 说明 IEC 60664-1 按哪些条件确定间距，明确本页不给具体毫米数。
