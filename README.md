# 常见标准电路教案（高中电路基础起步）

这是一套面向**只有高中物理电路基础**的学习者的中文教案，用浅显但严谨的方式讲透 20 种常见标准电路，并扩展讲解 MOS 管开关、继电器驱动、光耦与隔离等常用功能电路；全部内容是 Markdown 加 Python 生成的图片。

题目来源是一张「20种常见标准电路」图（[specs/source-20-circuits.jpg](specs/source-20-circuits.jpg)），任务说明见 [specs/task-spec.md](specs/task-spec.md)，教学设计见 [notes/00-design.md](notes/00-design.md)。

## 怎么读

每个知识点 3 页：page1「直觉篇」讲为什么需要它、它像什么；page2「原理与实现篇」讲推导并附可运行的 Python 仿真；page3「参数与调试篇」讲怎么选元件、出了故障怎么查，最后有练习题。建议先读前置知识 P1–P3，再按下面依赖图的箭头顺序往后读。标 ⚠ 的知识点涉及 220V/380V 市电，**只在低压下做仿真和实验**。

![图 00-1 知识点依赖图](img/00_dag.png)

*图 00-1　知识点依赖图：箭头从前置指向后继，颜色区分线索。由 [code/figs/00_figs.py](code/figs/00_figs.py) 生成。*

一条不会遇到「没学过的概念」的阅读顺序：

P1 → P3 → P2 → 17 → 01 → 21 → 22 → 02 → 05 → 14 → 18 → 03 → 06 → 12 → 19 → 04 → 10 → 13 → 07 → 15 → 08 → 11 → 23 → 16 → 09 → 25 → 20 → 24 → 26

## 目录

### 前置知识与 20 个标准电路

| 编号 | 知识点 | 文件夹 | 市电安全 | 作者 | 状态 |
|---|---|---|---|---|---|
| P1 | 元件速成 | [P1-components-basics](P1-components-basics/) |  | 作者 D | 待写 |
| P2 | 半导体入门 | [P2-semiconductor-basics](P2-semiconductor-basics/) |  | 作者 B | 待写 |
| P3 | 运放入门 | [P3-opamp-basics](P3-opamp-basics/) |  | 作者 A | 待写 |
| 01 | 反相放大 | [01-inverting-amp](01-inverting-amp/) |  | 作者 A | 待写 |
| 02 | 同相放大 | [02-noninverting-amp](02-noninverting-amp/) |  | 作者 A | 待写 |
| 03 | 电压跟随器 | [03-voltage-follower](03-voltage-follower/) |  | 作者 A | 待写 |
| 04 | 差分放大 | [04-differential-amp](04-differential-amp/) |  | 作者 A | 待写 |
| 05 | 精密整流 | [05-precision-rectifier](05-precision-rectifier/) |  | 作者 B | 待写 |
| 06 | 桥式整流（二极管桥 + 运放全波） | [06-bridge-rectifier](06-bridge-rectifier/) | ⚠ | 作者 B | 待写 |
| 07 | 射极跟随器 | [07-emitter-follower](07-emitter-follower/) |  | 作者 D | 待写 |
| 08 | 线性稳压 | [08-linear-regulator](08-linear-regulator/) |  | 作者 B | 待写 |
| 09 | 开关电源（两种拓扑） | [09-switching-power-supply](09-switching-power-supply/) | ⚠ | 作者 B | 待写 |
| 10 | 稳压管稳压 | [10-zener-regulator](10-zener-regulator/) |  | 作者 B | 待写 |
| 11 | 过载保护 | [11-overload-protection](11-overload-protection/) |  | 作者 C | 待写 |
| 12 | 积分电路 | [12-integrator](12-integrator/) |  | 作者 C | 待写 |
| 13 | 微分电路（理想 + 实用） | [13-differentiator](13-differentiator/) |  | 作者 C | 待写 |
| 14 | 电压比较器 | [14-voltage-comparator](14-voltage-comparator/) |  | 作者 C | 待写 |
| 15 | 有源滤波 | [15-active-filter](15-active-filter/) |  | 作者 A | 待写 |
| 16 | 振荡器（文氏桥 + 方波） | [16-oscillator](16-oscillator/) |  | 作者 A | 待写 |
| 17 | 自锁 | [17-self-locking](17-self-locking/) | ⚠ | 作者 D | 待写 |
| 18 | 互锁 | [18-interlock](18-interlock/) | ⚠ | 作者 D | 待写 |
| 19 | 星三角降压启动 | [19-star-delta-start](19-star-delta-start/) | ⚠ | 作者 D | 待写 |
| 20 | 双控开关 | [20-two-way-switch](20-two-way-switch/) | ⚠ | 作者 D | 待写 |

### 扩展篇

扩展篇讲电子制作中最常用的开关、驱动与隔离电路，标准与前面相同。

| 编号 | 知识点 | 文件夹 | 市电安全 | 作者 | 状态 |
|---|---|---|---|---|---|
| 21 | MOS 管开关 | [21-mosfet-switch](21-mosfet-switch/) |  | 作者 C | 待写 |
| 22 | 三极管开关与继电器驱动 | [22-bjt-relay-driver](22-bjt-relay-driver/) | ⚠ | 作者 D | 待写 |
| 23 | 光耦隔离 | [23-optocoupler](23-optocoupler/) | ⚠ | 作者 D | 待写 |
| 24 | 隔离电源与数字隔离器 | [24-isolated-power](24-isolated-power/) | ⚠ | 作者 B | 待写 |
| 25 | H 桥电机驱动 | [25-h-bridge](25-h-bridge/) |  | 作者 C | 待写 |
| 26 | 上拉/下拉电阻与电平转换 | [26-pullup-level-shift](26-pullup-level-shift/) |  | 作者 C | 待写 |

## 怎么运行代码

需要 Python 3.10 以上。在仓库根目录：

```bash
python3 -m venv /workspace/circuits-venv                 # 也可以换成你自己的路径
/workspace/circuits-venv/bin/pip install numpy matplotlib scipy schemdraw
/workspace/circuits-venv/bin/python code/figs/00_figs.py # 重画依赖图 img/00_dag.png
/workspace/circuits-venv/bin/python code/figs/schem.py --demo    # 预览全部电路元件
/workspace/circuits-venv/bin/python tools/run_blocks.py --scripts  # 运行 code/ 里全部仿真和画图脚本
```

图中的中文需要系统装有中文字体（本仓库在 Noto Sans CJK SC 下测试；Windows 的微软雅黑、macOS 的苹方也可以）。各页面里的代码块可以单独复制运行。

仓库结构：

- `P1-…`、`01-…` 等：每个知识点一个文件夹，内含 page1–3 和 `img/`。
- `code/`：各节点的仿真和画图脚本；`code/figs/` 是共用的配色字体模块 `figstyle.py` 和电路图模块 `schem.py`。
- `tools/`：检查工具（汉字数、代码块运行、配图、GitHub 公式渲染）。
- `notes/`：教学设计与作者指南；`specs/`：任务说明与原始附图。

## 编写团队

| 名称 | 角色 | 阶段 | 负责内容 | 状态 |
|---|---|---|---|---|
| 总纲 | 协调者、唯一提交者 | 阶段 1 设计；全程复核与提交 | 教学设计、依赖图、作者指南、复核合并 | 设计已完成 |
| 作者 A | 作者（串行队列） | 阶段 2 写作 | P3 → 01 → 02 → 03 → 04 → 15 → 16 | 待开始 |
| 作者 B | 作者（串行队列） | 阶段 2 写作 | P2 → 05 → 06 → 10 → 08 → 09 → 24 | 待开始 |
| 作者 C | 作者（串行队列） | 阶段 2 写作 | 21 → 14 → 12 → 13 → 11 → 25 → 26 | 待开始 |
| 作者 D | 作者（串行队列） | 阶段 2 写作 | P1 → 17 → 22 → 18 → 19 → 07 → 23 → 20 | 待开始 |
| 资深教师 | 审稿 | 阶段 3 审阅 | 严谨性、教学法、安全提醒 | 待加入 |
| 模拟学生 1 | 试读 | 阶段 3 审阅 | 按高中水平试读，标出看不懂的地方 | 待加入 |
| 模拟学生 2 | 试读 | 阶段 3 审阅 | 运行全部代码，做练习题 | 待加入 |
