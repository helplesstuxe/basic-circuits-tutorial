# 06 MOS 管开关 · 调研笔记（作者 C）

## 理论
- TI SLUA618《Fundamentals of MOSFET and IGBT Gate Driver Circuits》 https://www.ti.com/lit/pdf/slua618
  - 2.5/2.6 开通、关断四段；米勒平台；2.7 式 (9) P_GATE = V_DRV·Q_G·f，式 (11)–(14) 开关损耗线性近似 P_SW = V·I/2·(t2+t3)/T。
  - 2.8 源极寄生电感与 C_ISS 谐振；R_GATE 小→过冲但快，大→拖慢开关。
  - 5.1 P 沟道高边；5.2 高边 N 沟道需把栅极驱动到电源以上（自举等）。
## 器件数据（均已打开核对）
- IRLZ44N https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlz44n-datasheet-en.pdf ：55 V；R_DS(on) max 22/25/35 mΩ @10/5/4 V；V_GS(th) 1.0–2.0 V；Qg 48 nC、Qgs 8.6 nC、Qgd 25 nC（V_DS 44 V、V_GS 5 V）；±16 V；RθJA 62 °C/W；T_J max 175 °C；图 4 导通电阻随温度上升。
- IRF540N https://www.infineon.com/assets/row/public/documents/24/49/infineon-irf540n-datasheet-en.pdf ：100 V；44 mΩ 仅 @10 V；V_GS(th) 2.0–4.0 V。
- AO3400A https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf ：30 V；R_DS(on) max 26.5/32/48 mΩ @10/4.5/2.5 V；Qg 6 nC、Qgd 1.8 nC；±12 V；RθJA 稳态 100 典型 / 125 最大 °C/W（1 in² 铜皮）。
## 实践代码 / 教程
- Espruino MOSFETs https://www.espruino.com/mosfets ：栅极悬空、10 kΩ 下拉、门限≠完全导通、续流二极管。
## 常见误区（写进 page3 排查表）
- 以门限电压判断能否开到底（应看 R_DS(on) 的测试栅压）。
- 栅极电阻越大越安全（实际开关损耗成倍上升）。
- PWM 频率随意调高（开关损耗正比于 f）。
- 感性负载不加续流二极管；高边用 N 沟道却没有自举驱动。
## 模型说明
- code/06_sim.py 为栅极电荷示意模型：V_TH 1.5 V、平台 2.8 V、Q_GS 8.6 nC、Q_GD 12 nC（只切换 12 V，小于手册 44 V 条件下的 25 nC，示意取值）。
