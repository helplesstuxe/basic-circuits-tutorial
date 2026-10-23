# 25 H 桥电机驱动 · 调研笔记（作者 C）

## 已打开并引用的资料

- TI DRV8871 数据手册 https://www.ti.com/lit/ds/symlink/drv8871.pdf （本地文本 /workspace/authorC/refs/drv8871.pdf.txt）：四只 N 沟道 MOS 管 H 桥；VM 6.5–45 V；Rds(on) HS+LS 典型 565 mΩ（307 + 258），24 V/1 A 时最大 360 + 320 mΩ；Ipeak 3.6 A；输入脉宽 ≥ 800 ns；tDEAD 220 ns；VILIM 59/64/69 kV，I_TRIP = 64 kV / RILIM，RILIM ≥ 15 kΩ；tOFF 25 µs；IOCP 3.7/4.5/6.4 A；tRETRY 3 ms；真值表 00 滑行、01 反转、10 正转、11 刹车；「When using PWM, it typically works best to switch between driving and braking」；储能电容章节（大小、耐压、布局）。
- TI SLVA321A https://www.ti.com/lit/an/slva321a/slva321a.pdf （本地 slva321a.txt）：快/慢衰减、直通与死区、电感电流必须有续流路径。
- TI SLUA618 https://www.ti.com/lit/pdf/slua618 第 5.2 节：高边 NFET 需要高于电源的栅压、自举（21 节已打开引用）。
- Infineon IRLZ44N 数据手册（21 节已打开）：Rds(on) 25 mΩ，用作直通模型的导通电阻。

## 设计取值

- 电机：VM 12 V，R 2 Ω，L 1 mH，Ke 0.02 V·s/rad，J 1e-5 kg·m²，b 1e-5；桥臂电阻取 DRV8871 典型值。
- 直通模型：每管过渡 200 ns（示意），回路电感 20 nH，回路电阻 10 mΩ。
- PWM 20 kHz，「驱动—刹车」方式；dt 0.5 µs（每周期 100 步）。
- 限流：RILIM 32 kΩ → 2 A（1.84–2.16 A）。

## 仿真结果

- code/25_sim.py：25/50/75% → 1346/2690/4034 rpm（平均模型 1347/2694/4039），纹波 0.113/0.150/0.113 A。
- code/figs/25_figs.py：全速 5377 rpm，起动峰值 4.56 A；刹车 136 ms 到 10%（τ = 59 ms 理论吻合），滑行 2 s 后 14%；直通峰值 0/50/100/150 ns 死区 → 59.7/45.2/30.4/15.3 A，≥ 200 ns 为 0；纹波 0.5k–50k Hz 4.06 → 0.060 A。

## 未用·待核实

- 无 [待核实] 标记。页面中的 200 ns 过渡时间和直通模型标注为示意。
- 未使用：其他厂商（ST L298 等）资料，未打开故未引用。
