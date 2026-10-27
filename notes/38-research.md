# 38 同步检波（电磁流量计） · 调研笔记（作者 A）

## 理论
- ADI Analog Dialogue《Electromagnetic Flow Meters》https://www.analog.com/en/resources/analog-dialogue/articles/electromagnetic-flow-meters.html （curl 自盒子超时，WebFetch 可打开）：
  - 法拉第定律 E = k·B·D·v（D 为管径）。
  - 灵敏度 150–200 µV/(m/s)；0.5–15 m/s 对应 75 µV 到 4–6 mV。
  - 电极极化电压几百 mV 到 ±2 V。
  - 第一级 INA 增益 ≤ 10；100 dB CMRR 把 0.3 V 共模压到 3 µV。
  - 传统链路为 INA → 三/四阶带通 → 采样保持 → ADC。
  - 励磁频率取工频的整数分之一。
  - 数字同步检波：按励磁相位把样本分成两组，各自过 30 Hz FIR 低通后相减。
  - 文中结果：6.25 Hz 励磁下 0.5–2 m/s 精度 ±0.2%。
- Embien 博客《Electromagnetic flow meters design & development》https://www.embien.com/blog/electromagnetic-flow-meters-design-development （已打开）：励磁频率为工频的 1/16、1/10、1/8、1/4 或 1/2；MOSFET H 桥 + 恒流吸收电路；线圈电流约 150 mA 到 1 A 以上。
- Armstrong 电磁流量计手册 https://armstronginternational.com/wp-content/uploads/IOM_ElectromagneticFlowMeter_476_EN_20190101.pdf （已打开）：励磁类型 1/16、1/20、1/25（Type 1/2/3，零点不稳时换类型）。
- TI CD4053B https://www.ti.com/lit/ds/symlink/cd4053b.pdf （已打开）：SPDT 开关，用来实现 ±1 增益切换。

## 推导链
1. 励磁方波 +B / −B → 电极信号 +E / −E；而极化直流 V_dc 和缓慢漂移不随励磁翻转。
2. 乘以同步的 ±1 参考：E·(±1)·(±1) = +E（始终为正）；V_dc·(±1) 在一个周期内正负各半 → 平均为 0。
3. 输出 = 低通平均 → 只剩 E。
4. 正弦输入、相位差 φ 时：⟨A sin(ωt + φ)·sgn(sin ωt)⟩ = (2/π)·A·cos φ ≈ 0.637·A·cos φ（同步检波 = 有参考的全波整流，回指 09 节）。
5. 50 Hz 抑制：若每个励磁半周期正好包含整数个 50 Hz 周期，工频在积分中相消。励磁 50/8 = 6.25 Hz 时每半周期 80 ms = 4 个工频周期。
6. 线圈换向后电流有 L/R 过渡（39 节），只在电流稳定后的后半段采样。

## 算例（calc.py 已复核）
- ±1 乘正弦的平均值 = (2/π)A = 0.637A（再乘 cos φ）。
- 6.25 Hz = 50/8；3.125 Hz = 50/16。

## 常见错误
- 参考相位差 90°，cos φ ≈ 0，读数接近 0。
- 在换向瞬间采样，混入线圈过渡与尖峰。
- 积分时间不是工频周期的整数倍，50 Hz 漏过来。
- INA 增益太大，被极化电压推到饱和。
- 把“同步检波”和“普通整流”混为一谈（普通整流会把噪声也整流成直流）。

## 图与原理图计划
- 图 38-p1-1 电极信号 = 翻转的小信号 + 大直流 + 50 Hz（38_figs.py）；图 38-p1-2 乘 ±1 后的波形；图 38-p2-1 CD4053 ±1 放大原理图；图 38-p2-2 平均值随相位 φ（cos 曲线）；图 38-p3-1 励磁 6.25 Hz 与 50 Hz 整数倍关系；图 38-p3-2 数字分组平均框图。
- 图 38-p4-1 面包板 + 38_p4_k_schem_lab.png。

## SPICE 计划（spice/38/）
- 38_demod.cir：B 源产生 1 mV 方波（6.25 Hz）+ 1 V 直流 + 50 Hz 10 mV；INA（G = 10）→ CD4053（理想开关 + 125 Ω）在 +1 / −1 两路运放之间切换 → RC 低通（τ ≈ 1 s）。验证输出约 10 mV 且直流被消掉。

## page4 实验
- Arduino D9 输出 6.25 Hz 方波当“励磁/参考”；用这个方波经 1 MΩ/1 kΩ 分压得到约 ±5 mV 的“电极信号”（作者按实际分压比重算），叠加电位器给的 1 V 直流。
- 50 Hz 干扰：在输入线旁边放一根接在小变压器低压次级上的导线（只用成品插头式变压器；不接市电裸线）。
- 链路：INA（30 节电路，G = 10）→ CD4053 ±1 → RC 低通 → 万用表。
- 对比：Arduino ADC 直接采样，按参考相位分两组平均后相减（ADI 文章的数字方法）。

## 未用·待核实
- 「[待核实]」横河励磁频率页面 https://www.yokogawa.com/ （curl 返回 200，但内容是 JS 验证页，6.25 Hz 说法未能读到原文；本节 6.25 Hz 改引 ADI 文章）。
- 「[待核实]」E+H 电磁流量计学习页面（返回 JS/验证码页，未能打开）。
- 「[待核实]」ADI AD630 平衡调制/解调器数据手册（curl 超时，未用 WebFetch 打开，正文不引用其参数）。
