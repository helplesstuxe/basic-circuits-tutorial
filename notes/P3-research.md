# P3 运放入门 · 研究笔记（作者 A）

## 理论
- TI SLAA068B《Understanding Basic Analog – Ideal Op Amps》https://www.ti.com/lit/an/slaa068b/slaa068b.pdf ：理想运放假设（输入电流 0、增益无穷、两输入端电压差 0、输出阻抗 0、频响平坦）；饱和时假设失效；低频下理想分析准确。
- TI SLOA011《Understanding Op Amp Specifications》https://www.ti.com/lit/pdf/sloa011 ：参数定义（AOL、GBW、SR、输出摆幅）。
- TI SBOA270 反相放大电路手册 https://www.ti.com/lit/pdf/sboa270 ：增益由电阻比决定；输入阻抗 ≈ R1。
- TI SLVA051 https://www.ti.com/lit/an/slva051/slva051.pdf ：闭环增益 A/(1+Aβ)（只在搜索摘要中看到该式，正文未逐页核对）。

## 数据手册（数值来源）
- TI LM358B https://www.ti.com/lit/ds/symlink/lm358.pdf ：AOL 典型 140 V/mV（最小 70）；GBW 1.2 MHz；SR 0.5 V/μs；正摆幅距 V+ 约 1.35–1.5 V；负摆幅距 V− 约 100 mV（轻载）；差分输入阻抗 10 MΩ；电源 3–36 V；VCM ≤ V+ − 1.5 V。

## 实战代码
- 本节仿真不依赖 SPICE：联立 Vo=A(V+−V−) 与 KCL 解析求解，见 code/P3_sim.py。
- PySpice 运放示例（参考，未采用）https://pyspice.fabrice-salvaire.fr/releases/v1.5/examples/operational-amplifier/operational-amplifier.html
- schemdraw 模拟电路图库 https://schemdraw.readthedocs.io/en/stable/gallery/analog.html

## 常见误区
- 开环（比较器）时套用虚短 → 见 page1/page2 图 P3-p2-3。
- 忘记输出摆幅受电源限制、单电源无负输出 → page3 图 P3-p3-1、练习 3。
- 以为 A 有限会让增益严重偏离 → page3 图 P3-p3-2（误差 ≈ (1+G)/A）。
- TI E2E 论坛相关帖子 WebFetch/curl 均 403，未引用。
