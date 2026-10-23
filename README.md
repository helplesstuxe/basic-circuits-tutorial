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
| P1 | 元件速成 | [P1-components-basics](P1-components-basics/) |  | 作者 D | 已完成 |
| P2 | 半导体入门 | [P2-semiconductor-basics](P2-semiconductor-basics/) |  | 作者 B | 已完成 |
| P3 | 运放入门 | [P3-opamp-basics](P3-opamp-basics/) |  | 作者 A | 已完成 |
| 01 | 反相放大 | [01-inverting-amp](01-inverting-amp/) |  | 作者 A | 已完成 |
| 02 | 同相放大 | [02-noninverting-amp](02-noninverting-amp/) |  | 作者 A | 已完成 |
| 03 | 电压跟随器 | [03-voltage-follower](03-voltage-follower/) |  | 作者 A | 已完成 |
| 04 | 差分放大 | [04-differential-amp](04-differential-amp/) |  | 作者 A | 已完成 |
| 05 | 精密整流 | [05-precision-rectifier](05-precision-rectifier/) |  | 作者 B | 已完成 |
| 06 | 桥式整流 | [06-bridge-rectifier](06-bridge-rectifier/) | ⚠ | 作者 B | 已完成 |
| 07 | 射极跟随器 | [07-emitter-follower](07-emitter-follower/) |  | 作者 D | 已完成 |
| 08 | 线性稳压 | [08-linear-regulator](08-linear-regulator/) |  | 作者 B | 已完成 |
| 09 | 开关电源 | [09-switching-power-supply](09-switching-power-supply/) | ⚠ | 作者 B | 已完成 |
| 10 | 稳压管稳压 | [10-zener-regulator](10-zener-regulator/) |  | 作者 B | 已完成 |
| 11 | 过载保护 | [11-overload-protection](11-overload-protection/) |  | 作者 C | 已完成 |
| 12 | 积分电路 | [12-integrator](12-integrator/) |  | 作者 C | 已完成 |
| 13 | 微分电路 | [13-differentiator](13-differentiator/) |  | 作者 C | 已完成 |
| 14 | 电压比较器 | [14-voltage-comparator](14-voltage-comparator/) |  | 作者 C | 已完成 |
| 15 | 有源滤波 | [15-active-filter](15-active-filter/) |  | 作者 A | 已完成 |
| 16 | 振荡器 | [16-oscillator](16-oscillator/) |  | 作者 A | 已完成 |
| 17 | 自锁 | [17-self-locking](17-self-locking/) | ⚠ | 作者 D | 已完成 |
| 18 | 互锁 | [18-interlock](18-interlock/) | ⚠ | 作者 D | 已完成 |
| 19 | 星三角降压启动 | [19-star-delta-start](19-star-delta-start/) | ⚠ | 作者 D | 已完成 |
| 20 | 双控开关 | [20-two-way-switch](20-two-way-switch/) | ⚠ | 作者 D | 已完成 |

### 扩展篇

扩展篇讲电子制作中最常用的开关、驱动与隔离电路，标准与前面相同。

| 编号 | 知识点 | 文件夹 | 市电安全 | 作者 | 状态 |
|---|---|---|---|---|---|
| 21 | MOS 管开关 | [21-mosfet-switch](21-mosfet-switch/) |  | 作者 C | 已完成 |
| 22 | 三极管开关与继电器驱动 | [22-bjt-relay-driver](22-bjt-relay-driver/) | ⚠ | 作者 D | 已完成 |
| 23 | 光耦隔离 | [23-optocoupler](23-optocoupler/) | ⚠ | 作者 D | 已完成 |
| 24 | 隔离电源与数字隔离器 | [24-isolated-power](24-isolated-power/) | ⚠ | 作者 B | 已完成 |
| 25 | H 桥电机驱动 | [25-h-bridge](25-h-bridge/) |  | 作者 C | 已完成 |
| 26 | 上拉/下拉电阻与电平转换 | [26-pullup-level-shift](26-pullup-level-shift/) |  | 作者 C | 已完成 |

## 怎么运行代码

1. **建虚拟环境，装这几个包**（需要 Python 3.10 以上；本仓库在下面的版本上测试过）：

   ```bash
   python3 -m venv circuits-venv                 # 路径随意，下面都用这个名字
   circuits-venv/bin/pip install numpy matplotlib scipy schemdraw markdown-it-py
   # 测试版本：numpy 2.5.4、matplotlib 3.11.2、scipy 1.18.1、schemdraw 0.23、markdown-it-py 4.2.0
   ```

   图中的中文需要系统装有中文字体（本仓库在 Noto Sans CJK SC 下测试；Windows 的微软雅黑、macOS 的苹方也可以）。

2. **一律在仓库根目录运行**。脚本和页面里的代码块都按「当前目录 = 仓库根目录」找 `code/figs/figstyle.py` 和各节点的 `img/`；在别的目录运行会报找不到 `figstyle`。

   ```bash
   cd basic-circuits-tutorial
   circuits-venv/bin/python code/22_sim.py                 # 运行一个节点的仿真
   circuits-venv/bin/python code/figs/22_figs.py           # 重画这个节点的配图
   circuits-venv/bin/python tools/run_blocks.py --scripts  # 运行 code/ 里全部仿真和画图脚本
   ```

   页面里的代码块可以单独复制运行：复制成一个 .py 文件，同样在仓库根目录运行。用到 `figstyle` 的代码块开头都有两行 `sys.path.insert(...)`，不要删。

3. **`fs.save` 会覆盖 `img/` 里的图**。`code/` 里的仿真和画图脚本都用 `fs.save(fig, "NN", "NN_pX_k_含义.png")` 保存图，它把图写回对应节点的 `img/` 文件夹（不管你复制到哪里运行，写的都是仓库里那个 `img/`），页面引用的就是这些文件。改了参数再运行，页面上的图也跟着变。

4. **想改脚本做实验，先复制一份**，例如 `cp code/22_sim.py my_22.py`，改副本，并把副本里的 `fs.save(...)` 换成 `plt.show()` 或 `fig.savefig("my_test.png")`。否则一运行就会把 `img/` 里的正式配图换掉，页面上的数字和图就对不上了；万一改坏了，用 `git checkout -- code/ NN-slug/img/` 恢复。

仓库结构：

- `P1-…`、`01-…` 等：每个知识点一个文件夹，内含 page1–3 和 `img/`。
- `code/`：各节点的仿真和画图脚本；`code/figs/` 是共用的配色字体模块 `figstyle.py` 和电路图模块 `schem.py`。
- `tools/`：检查工具（汉字数、代码块运行、配图、GitHub 公式渲染）。
- `notes/`：教学设计与作者指南；`specs/`：任务说明与原始附图。

## 完成情况

下表是复核修改全部合并后的实测值（2026-10-23）。

- 每页汉字：`tools/count_cjk.py` 统计正文汉字，依次是 page1 / page2 / page3，每页下限 500。
- 图数：三页实际引用的配图张数，和 `img/` 里的文件数一一对应。
- 代码已运行：页面代码块（`tools/run_blocks.py`，每块也单独复制到 .py 运行过）加 `code/` 里的仿真和画图脚本，全部运行通过。01–04 和 P3 各有 1 个留空让读者填写的练习块，按设计不运行。
- GitHub 公式：`tools/check_github_math.py` 调用 GitHub 渲染接口，渲染出的公式数 / 源文件公式数。
- 复核通过：资深教师和两位模拟学生报告里的「必改」「卡住」「吃力」全部改完记 ✅。
- 待补项：有意没有照改的条目及理由。报告原文和逐条修改记录见 `review/` 与 `notes/progress-log.md`。

| 知识点 | 页数 | 每页汉字 | 图数 | 代码已运行 | GitHub 公式 | 复核通过 | 待补项 |
|---|---|---|---|---|---|---|---|
| [P1 元件速成](P1-components-basics/page1.md) | 3 | 1937 / 3915 / 2688 | 14 | ✅ 1 块 + 2 脚本 | ✅ 90/90 | ✅ | — |
| [P2 半导体入门](P2-semiconductor-basics/page1.md) | 3 | 2115 / 3007 / 2965 | 10 | ✅ 1 块 + 2 脚本 | ✅ 149/149 | ✅ | 教师 #6 未采纳：说「全书没有开关电源节点」与事实不符（09 就是），改为在 page1 标出各应用的节号 |
| [P3 运放入门](P3-opamp-basics/page1.md) | 3 | 1898 / 2309 / 2690 | 8 | ✅ 1 块 + 2 脚本（另 1 个填空块不运行） | ✅ 94/94 | ✅ | — |
| [01 反相放大](01-inverting-amp/page1.md) | 3 | 1992 / 1720 / 2407 | 9 | ✅ 1 块 + 2 脚本（另 1 个填空块不运行） | ✅ 130/130 | ✅ | — |
| [02 同相放大](02-noninverting-amp/page1.md) | 3 | 1749 / 1614 / 2061 | 8 | ✅ 1 块 + 2 脚本（另 1 个填空块不运行） | ✅ 110/110 | ✅ | — |
| [03 电压跟随器](03-voltage-follower/page1.md) | 3 | 1652 / 1673 / 2499 | 8 | ✅ 1 块 + 2 脚本（另 1 个填空块不运行） | ✅ 41/41 | ✅ | — |
| [04 差分放大](04-differential-amp/page1.md) | 3 | 1679 / 1693 / 2229 | 7 | ✅ 1 块 + 2 脚本（另 1 个填空块不运行） | ✅ 149/149 | ✅ | — |
| [05 精密整流](05-precision-rectifier/page1.md) | 3 | 1697 / 2817 / 3085 | 9 | ✅ 1 块 + 2 脚本 | ✅ 136/136 | ✅ | — |
| [06 桥式整流](06-bridge-rectifier/page1.md) | 3 | 1883 / 3170 / 2983 | 9 | ✅ 1 块 + 2 脚本 | ✅ 76/76 | ✅ | — |
| [07 射极跟随器](07-emitter-follower/page1.md) | 3 | 1874 / 2477 / 2161 | 9 | ✅ 1 块 + 2 脚本 | ✅ 150/150 | ✅ | — |
| [08 线性稳压](08-linear-regulator/page1.md) | 3 | 1578 / 2184 / 2925 | 8 | ✅ 1 块 + 2 脚本 | ✅ 101/101 | ✅ | — |
| [09 开关电源](09-switching-power-supply/page1.md) | 3 | 2210 / 3109 / 3224 | 10 | ✅ 1 块 + 2 脚本 | ✅ 78/78 | ✅ | — |
| [10 稳压管稳压](10-zener-regulator/page1.md) | 3 | 1754 / 2555 / 2454 | 8 | ✅ 1 块 + 2 脚本 | ✅ 115/115 | ✅ | — |
| [11 过载保护](11-overload-protection/page1.md) | 3 | 1512 / 2252 / 2648 | 6 | ✅ 2 块 + 2 脚本 | ✅ 96/96 | ✅ | — |
| [12 积分电路](12-integrator/page1.md) | 3 | 1957 / 1806 / 2232 | 8 | ✅ 1 块 + 2 脚本 | ✅ 93/93 | ✅ | — |
| [13 微分电路](13-differentiator/page1.md) | 3 | 2718 / 2092 / 1908 | 10 | ✅ 1 块 + 2 脚本 | ✅ 142/142 | ✅ | — |
| [14 电压比较器](14-voltage-comparator/page1.md) | 3 | 1991 / 2177 / 2429 | 8 | ✅ 1 块 + 2 脚本 | ✅ 146/146 | ✅ | 教师 #3 未照改：0.72 V 计入 2.2 kΩ 上拉后是对的（0.724 V），保留并注明来由 |
| [15 有源滤波](15-active-filter/page1.md) | 3 | 1546 / 1854 / 2370 | 7 | ✅ 1 块 + 2 脚本 | ✅ 155/155 | ✅ | 小问题「X7R/C0G 体积对比」未补：正文已有括注 |
| [16 振荡器](16-oscillator/page1.md) | 3 | 1624 / 1995 / 2245 | 8 | ✅ 1 块 + 2 脚本 | ✅ 122/122 | ✅ | — |
| [17 自锁](17-self-locking/page1.md) | 3 | 1920 / 2669 / 2291 | 10 | ✅ 1 块 + 2 脚本 | ✅ 58/58 | ✅ | — |
| [18 互锁](18-interlock/page1.md) | 3 | 1845 / 3279 / 2596 | 8 | ✅ 1 块 + 2 脚本 | ✅ 58/58 | ✅ | — |
| [19 星三角降压启动](19-star-delta-start/page1.md) | 3 | 1959 / 3597 / 2594 | 10 | ✅ 1 块 + 2 脚本 | ✅ 32/32 | ✅ | — |
| [20 双控开关](20-two-way-switch/page1.md) | 3 | 1550 / 2479 / 2007 | 8 | ✅ 1 块 + 2 脚本 | ✅ 37/37 | ✅ | — |
| [21 MOS 管开关](21-mosfet-switch/page1.md) | 3 | 1883 / 2738 / 2825 | 8 | ✅ 1 块 + 2 脚本 | ✅ 143/143 | ✅ | — |
| [22 三极管开关与继电器驱动](22-bjt-relay-driver/page1.md) | 3 | 1662 / 3015 / 2572 | 9 | ✅ 1 块 + 2 脚本 | ✅ 103/103 | ✅ | — |
| [23 光耦隔离](23-optocoupler/page1.md) | 3 | 1532 / 2181 / 2890 | 8 | ✅ 1 块 + 2 脚本 | ✅ 104/104 | ✅ | — |
| [24 隔离电源与数字隔离器](24-isolated-power/page1.md) | 3 | 1967 / 3562 / 4287 | 8 | ✅ 1 块 + 2 脚本 | ✅ 41/41 | ✅ | — |
| [25 H 桥电机驱动](25-h-bridge/page1.md) | 3 | 1569 / 2591 / 2677 | 8 | ✅ 1 块 + 2 脚本 | ✅ 90/90 | ✅ | — |
| [26 上拉/下拉电阻与电平转换](26-pullup-level-shift/page1.md) | 3 | 1610 / 2500 / 2964 | 8 | ✅ 1 块 + 2 脚本 | ✅ 104/104 | ✅ | R6（调整阅读顺序）未采纳，26 仍是最后一节 |
| **合计 29 个** | 87 | 共 201799 | 249 | ✅ 88 个 | ✅ 2943/2943 | 29/29 | 4 项（见上） |

另：跨章节报告 S2 写的「100 mA 时 β 约 60」有误（onsemi 2N3904 手册 100 mA 时 h_FE 最小 30），页面没有沿用这个数字，报告原文保留未改。

## 编写团队

| 名称 | 角色 | 阶段 | 负责内容 | 状态 |
|---|---|---|---|---|
| 总纲 | 协调者、唯一提交者 | 阶段 1 设计；全程复核与提交 | 教学设计、依赖图、作者指南、复核合并 | 设计已完成 |
| 作者 A | 作者（串行队列） | 阶段 2 写作 | 已写 7 个节点：P3 运放入门、01 反相放大、02 同相放大、03 电压跟随器、04 差分放大、15 有源滤波、16 振荡器 | 已完成 |
| 作者 B | 作者（串行队列） | 阶段 2 写作 | 已写 7 个节点：P2 半导体入门、05 精密整流、06 桥式整流、10 稳压管稳压、08 线性稳压、09 开关电源、24 隔离电源与数字隔离器 | 已完成 |
| 作者 C | 作者（串行队列） | 阶段 2 写作 | 已写 7 个节点：21 MOS 管开关、14 电压比较器、12 积分电路、13 微分电路、11 过载保护、25 H 桥电机驱动、26 上拉/下拉电阻与电平转换 | 已完成 |
| 作者 D | 作者（串行队列） | 阶段 2 写作 | 已写 8 个节点：P1 元件速成、17 自锁、22 三极管开关与继电器驱动、18 互锁、19 星三角降压启动、07 射极跟随器、23 光耦隔离、20 双控开关 | 已完成 |
| 资深教师 | 审稿 | 阶段 3 审阅 | 严谨性、教学法、安全提醒 | 已完成（报告见 `review/`） |
| 模拟学生 1 | 试读 | 阶段 3 审阅 | 按高中水平试读，标出看不懂的地方 | 已完成（报告见 `review/`） |
| 模拟学生 2 | 试读 | 阶段 3 审阅 | 运行全部代码，做练习题 | 已完成（报告见 `review/`） |
