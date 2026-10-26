# 13 桥式整流 · 调研笔记

只记结论和出处；所有链接都已实际打开（2026-10-22）。

## 器件参数

- Vishay 1N4001–1N4007 数据手册（Doc 88503，Rev 29-Apr-2020）：https://www.vishay.com/docs/88503/1n4001.pdf
  - 最大重复峰值反向电压 V_RRM：1N4001 50 V、1N4002 100 V、1N4003 200 V、1N4004 400 V、1N4005 600 V、1N4006 800 V、1N4007 1000 V。
  - 平均正向整流电流 I_F(AV) 1.0 A；峰值正向浪涌电流 I_FSM 30 A（8.3 ms 单个半正弦）。
  - 最大正向压降 V_F 1.1 V（1.0 A）。

## 原理与设计经验

- Rod Elliott（ESP）「Linear Power Supply Design」：https://sound-au.com/power-supplies.htm
  - 桥式整流里，每个半周有两只二极管串联导通；二极管反向耐压只要超过交流峰值即可。
  - 每只二极管压降约 0.7–0.9 V，两只串联，合计约 1.8 V 要从峰值里扣掉。
  - 二极管只在峰值附近很短的时间里导通，峰值电流可以超过直流输出电流的 5 倍。
  - 直流输出要从滤波电容的两端引出，而不是从整流桥引出。
  - 经验公式 C = (I/ΔV)·k·1000 µF，100 Hz 纹波时 k = 7；对 2 Vpp 纹波约为每安培 3500 µF。电容加倍，纹波减半。
  - 上电浪涌电流可能很大（文中给出浪涌电流表，实测市电内阻约 0.8 Ω）；市电电压有 ±10% 的波动，设计要留余量。
  - 泄放电阻：让电容在约 10 s 内放到约 37%（一个时间常数）。
  - 滤波电容是电源头号故障源：纹波电流、温度、ESR。
- Wikipedia「Diode bridge」：https://en.wikipedia.org/wiki/Diode_bridge
  - 四只二极管组成的桥，把交流的两个半周都变成同一极性；也可用作直流输入的反接保护。
- Wikipedia「Ripple (electrical)」：https://en.wikipedia.org/wiki/Ripple_(electrical)
  - 全波整流加电容滤波，峰峰纹波 V_pp ≈ I/(2fC)（半波为 I/(fC)）。
- Wikipedia「Aluminum electrolytic capacitor」：https://en.wikipedia.org/wiki/Aluminum_electrolytic_capacitor
  - 极性接反或加交流电压会使介质层损坏、内部短路，可能烧毁或爆裂（页面有炸开的电容照片）。

## 运放全波整流

- Fiore《Operational Amplifiers and Linear Integrated Circuits》7.2.2 Precision Full-Wave Rectifier（LibreTexts，链接同 notes/09-research.md）
  - 又叫绝对值电路；由反相精密半波整流和加权加法器组成，用两只运放；除一只外所有电阻取同一个值（那一只是 R/2）。

## 未采用

- electronics-tutorials 的整流页面下载失败（HTTP 000），未引用。
