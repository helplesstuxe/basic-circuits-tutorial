* 43 推挽功放公共部分：单 12 V、TL072 缓冲出中点参考 V_MID 6 V（只给输入和运放偏置，不走喇叭电流）、TL072 同相放大 ×3、BD139/BD140 推挽、R_E 3.3 Ω、1000 µF 耦合电容接真地、8 Ω 功率电阻
.include ../models/TL072.lib
.include ../models/BD139_BD140_generic.lib
.include ../models/1N4148_nexperia.lib
VCC vcc 0 12
* 电流表 Vam：串在 +12 V 和 Q1 集电极之间（只量功放管电流）
Vam vcc cq 0
R1 vcc div 10k
R2 div 0 10k
Cd div 0 10u
XUA div vm vcc 0 vm TL072
Cin sig inp 10u
Rbias inp vm 100k
XUB inp fb vcc 0 mo TL072
* Vmo：0 V 源，用来读运放输出电流
Vmo mo m 0
RG fb vm 10k
* 基极阻尼电阻 22 Ω（紧贴管脚，防 MHz 级寄生振荡；常用 22～47 Ω）
Rbs1 b1 bq1 22
Rbs2 b2 bq2 22
Q1 cq bq1 e1 BD139
Q2 0 bq2 e2 BD140
RE1 e1 out 3.3
RE2 e2 out 3.3
* Zobel 网络：10 Ω + 100 nF 从推挽输出到真地（高频时给输出一个电阻性负载）
Rz out zb 10
Cz zb 0 100n
* 输出耦合电容：正极接 out，负极经负载接真地（不是接 V_MID）
Cout out ld 1000u
RL ld 0 8
