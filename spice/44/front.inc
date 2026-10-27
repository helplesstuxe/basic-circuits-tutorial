* 44 D 类功放前级：单 12 V；TL072 缓冲出中点参考 V_MID 6 V；TL072 施密特 + 积分器出三角波（公式 53 kHz，TL072 退饱和慢，实际更低，见 run.py）；
* 三角波经 100 nF / 100 kΩ 交流耦合到 V_MID（中心自动对准 V_MID）
* 名字对照（网表里的实例名 → 页面原理图图 44-p4-2 / 面包板图 44-p4-1 里的名字）：
*   XU1A（中点参考缓冲）= 图上 U2B；XU1B（积分器）= 图上 U1A；XU2A（施密特触发器）= 图上 U1B
*   网表只是按搭建顺序编号，元件和连接与图上完全相同
.include ../models/TL072.lib
.include ../models/LM393A.lib
VCC vcc 0 12
V5 v5 0 5
* 中点参考 V_MID
R1 vcc div 10k
R2 div 0 10k
Cd div 0 10u
XU1A div vmid vcc 0 vmid TL072
* 积分器（U1B）：R 4.7 kΩ、C 2.2 nF
Rint sq ni 4.7k
Cint ni tri 2.2n
XU1B vmid ni vcc 0 tri TL072
* 施密特触发器（U2A）：R1 10 kΩ（接三角波）、R2 22 kΩ（接方波）
Rs1 tri sp 10k
Rs2 sq sp 22k
XU2A sp vmid vcc 0 sq TL072
* 三角波交流耦合
Ct tri t 100n
Rt t vmid 100k
* 输入：信号源 → 4.7 kΩ → 1 µF → s，s 经 10 kΩ 接 V_MID（中频增益 10/14.7 ≈ 0.68）
Rin1 sig a 4.7k
Cin a s 1u
Rin2 s vmid 10k
