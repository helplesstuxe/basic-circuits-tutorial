# 28 隔离电源与数字隔离器 · 调研笔记

以下链接都已实际打开阅读（2026-10-23）。

- Wikipedia，Isolation transformer：https://en.wikipedia.org/wiki/Isolation_transformer
  - 电气隔离（galvanic isolation）：两组绕组之间没有导电通路，隔断直流。
  - 绕组之间存在电容，交流和共模干扰仍会少量耦合；可加接地的法拉第屏蔽层。
  - 给被隔离电路接上示波器、台式万用表等测试仪器，可能使它重新接地；被隔离设备内部的元件之间仍可能有危险电压。
- Wikipedia，Flyback converter：https://en.wikipedia.org/wiki/Flyback_converter
  - 相当于把升降压变换器的电感拆成变压器，从而得到隔离。
  - 开关导通时能量存入变压器、副边二极管反偏、输出电容供电；断开时二极管导通，能量送到电容和负载。
  - 反馈方式：副边光耦、辅助绕组、初级侧检测（需要最小负载）；用于手机充电器、电脑待机电源等。
- TI，ISO772x 数据手册 SLLSEP3G（2016-11，2024-05 修订）：https://www.ti.com/lit/ds/symlink/iso7721.pdf
  - 5 V 时传输延时最小 6 / 典型 11 / 最大 17 ns；最高 100 Mbps；SiO₂ 隔离层。
  - ISO7720 两路同方向，ISO7721 两路方向相反；输入掉电或信号丢失时默认输出高（无 F 后缀型号）。
  - 每侧电源推荐 2.25 V 到 5.5 V，绝对最大 6 V；1 Mbps 时每通道典型约 1.7 mA。
  - $V_{ISO}$ ：DW / DWV 封装 5000 VRMS，D 封装 3000 VRMS；60 秒鉴定测试，量产 1.2 倍、1 秒。
  - 最大工作隔离电压（TDDB）：DW 封装 1500 VRMS，D 封装 450 VRMS；爬电距离 DW 8 mm、D 4 mm；有加强绝缘与基本绝缘（ISO7721B）两种等级。
  - CMTI 最小 85、典型 100 kV/µs。
- TI，SLLA526D《Replacing Optocouplers with Digital Isolators》白皮书：https://www.ti.com/lit/wp/slla526d/slla526d.pdf
  - 通用光耦：上拉 100 Ω 时 tPHL / tPLH 约 3 / 3 µs；上拉 1.9 kΩ 时 0.5 / 40 µs。高速光耦约 33 / 27 ns；ISO6441 约 6.2 ns。
  - 最高数据率估算：位宽约为 4 倍最大传输延时。
  - 隔离方式：SiO₂ 电容耦合或线圈磁耦合；SiO₂ 耐压约 500 VRMS/µm。
  - 光耦 LED 老化、CTR 下降；光耦输入需 >2 mA（常 >10 mA），数字隔离器 CMOS 输入最大约 ±10 µA。
  - CMTI：典型高速光耦最小约 ±20 kV/µs，ISO6441 最小 ±150 kV/µs。
- Murata，DCAN-68 隔离 DC-DC 模块应用笔记：https://www.murata.com/-/media/webrenewal/products/power/appnote/dcan-68.pdf
  - 第 17 节：不稳压小功率隔离模块可能没有主动限压，需要最小负载（一般为满载 10%），否则输出超出规格。
  - 补救：并假负载电阻（永远占用约 10% 功率），或稳压管 + 串联电阻钳位（例：15 V 输出、220 Ω，负载超过约 60% 后稳压管不再导通）。
  - 负载调整率从最小负载量到 100%；不稳压模块在最小负载以下电压可能显著升高。
- Murata，NME 系列数据手册（经 DiGi 镜像打开）：https://pdf.digi-electronics.com/pdf/1732/NME0505SC-datasheet.pdf
  - NME0505SC：5 V 进、5 V 200 mA 出，1 W 不稳压；负载调整率典型 12%、最大 14%；纹波典型 16、最大 40 mV p-p；效率 69%。
  - NME0512SC：12 V 83 mA，负载调整率典型 6.5%、最大 7.5%。
  - 线性调整率典型 1.0、最大 1.2 %/%；最小负载 10%，低于 5% 负载输出可能升到约两倍；5 V 输入型号开关频率约 110 kHz；环形隔离变压器。
  - 出厂 1 kVDC、1 秒耐压测试；UL 仅认证为功能隔离，两侧应保持在 SELV 范围内（峰值 42.4 V 或直流 60 V 以下），不能用作安全隔离系统的元件；反复耐压测试会劣化绝缘，复测时电压降低 20%。

## 本节自定的示意量（非引用）

- 电网 ±10% 波动；现场侧传感器 3 mA；不稳压模块的电压—负载模型（按手册 12% 负载调整率与"低于 5% 负载升到约两倍"拼成）；光耦回升的 RC 形状。
