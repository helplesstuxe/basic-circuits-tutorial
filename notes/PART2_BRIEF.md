# 第二部分作者简报（节点 30–45）

写任何一页之前，依次读完下面三份文件：

1. [AUTHOR_GUIDE.md](AUTHOR_GUIDE.md)：硬性规则，第二部分全部沿用。
2. [00-design-part2.md](00-design-part2.md)：DAG、每节摘要、安全总则。
3. 你负责节点的 `notes/NN-research.md`：来源、算例、SPICE 与实验计划。

本简报只写第二部分新增或需要特别强调的内容。节点名称照抄 00-design-part2 §5.1，例如写「30 仪表放大器与电桥」。

## 1. 四页结构与字数

| 页 | 篇名 | 最少汉字 | 要点 |
|---|---|---|---|
| page1 | 直觉篇 | 500 | 从流量计或音响的真实痛点引入，配生活类比和示意图 |
| page2 | 原理与实现篇 | 500 | 推导链见 research 笔记的「推导链」；每个公式都要先说中文意思，再代数算一遍；带逐行注释的最小 Python 仿真；渐隐式例题 |
| page3 | 参数与调试篇 | 500 | 参数扫描图；故障排查表（现象 / 原因 / 怎么查 / 怎么改）；至少 3 道练习，答案折叠 |
| page4 | 动手实验篇 | 1500 | AUTHOR_GUIDE §1 规定的固定十部分 |

- 字数检查：`tools/count_cjk.py`。代码、公式和图注不计入字数。
- 第二部分的读者已经学完 01–29。凡是第一部分没讲过的东西，都要先补最小必要知识。目前已知的有：
  - NE555；
  - Arduino 定时器 / 输入捕获；
  - 分贝；
  - 品质因数 Q；
  - 锁相 / 同步检波；
  - 电流环。
- 回指第一部分时，写全名并加链接。各节对应的前置节点，请对照 00-design-part2 §5.2 的边表（已按第一部分的实际内容核对过）。

## 2. 图

- 命名规则：
  - 文件名 `NN_pX_k_含义.png`，图号「图 NN-pX-k」；
  - 由 `code/figs/NN_figs.py` 生成，每张 ≤ 200 KB；
  - 图上每个数字都要由脚本打印，关键结论加 `assert`。
- **讲到电路连接就要配原理图**：每一处讲电路结构的文字旁边，都要有用 `code/figs/schem.py` 画的原理图。
- **page4**：
  - 每张面包板图「图 NN-p4-k」后面紧跟一张用 `code/figs/lab_schem.py` 画的原理图 `NN_p4_k_schem_lab.png`，节点旁标出面包板孔位；
  - 再写一段以「对照看」开头的文字，把孔位、导线和原理图里的元件、节点一一对上；
  - `lab_schem.py` 的 NODES 条目由协调人追加（见第 7 节）。
- 原理图里会用到第一部分没用过的元件：
  - CD4053 / CD4051 用 `schem.module` 画成带引脚名的方框；
  - DRV8871、PAM8403、XTR115 模块同样处理；
  - 超声换能器、压电片用 `schem.module` 或带标签的电容符号表示，并在图后讲解里说明。
- 颜色词照抄 AUTHOR_GUIDE §2 的表格。图注里不写公式。

## 3. GitHub 公式规则（摘要，完整版见 AUTHOR_GUIDE §5）

- 开头的 `$` 前面紧跟中文或全角标点时，要补一个空格。
- 公式里不写 `<` `>`，改用 `\lt` `\gt`。
- `%` 放到公式外面，写成 `$…$%`。
- 不写 `\,`（改用 `\thinspace`）。
- `<details>` 里不写 `$$` 块公式。
- 第二部分常用的写法：
  - 开方写 `$\sqrt{\Delta P}$`；
  - 分贝写 `$20\log_{10}(\ldots)$`；
  - 平均值写 `$\overline{v}$`，不要用尖括号 ⟨⟩，因为 GitHub 上会被当成 HTML 标签吞掉。
- research 笔记里的公式是纯文本，写正文时要改成 `$…$`，然后运行：
  1. `tools/fix_inline_math_spacing.py`；
  2. `tools/fix_inline_math_spacing.py --check`；
  3. `tools/check_github_math.py`。

## 4. SPICE

- 网表放 `spice/NN/`：`*.cir` 加 `run.py`，格式照抄 `spice/05/`。
- 核对表放 `review/spice/NN.md`，内容包括万用表应读范围、仿真值和页面值的对照。
- page4 测量表里的「应该读到」只取 `review/spice/NN.md`，或 `code/NN_sim.py` / `spice/NN/run.py` 实际算出来的数，不准编造。
- 第二部分可能缺的模型由协调人统一补充：LMC6482、CD4053 / CD4051、BD139 / BD140。补齐之前，开关先用理想开关加 R_on = 125 Ω（CD4051B / CD4053B 典型值）代替。
- 需要用行为模型代替真实芯片时（例如 LM386、TDC），要在 `review/spice/NN.md` 中写明是行为模型。

## 5. 实验安全（第二部分）

- 所有实验 ≤ 12 V 直流，不接市电。第二部分没有市电节点，不需要放市电警示框，但 page4 的安全须知照常写。
- 50 Hz 干扰源只用电线感应，或用成品插头式小变压器的低压次级。
- 发热元件可能超过 60 °C，只用温度计或 NTC 测温，不要用手摸：
  - 39 节的 MOSFET；
  - 40 节的加热电阻；
  - 43 节的 BD139 / BD140；
  - 44 节的 DRV8871 与电感；
  - 45 节的功放芯片。
- 喇叭先串 10 Ω 限流，不要让直流长期流过喇叭。BTL 输出（44 节的 DRV8871、45 节的 PAM8403）两端都不能接地，示波器地夹也不能夹在输出上。
- 压电片敲击会产生尖峰，进运放前要串 10 kΩ 并加两只 1N4148 钳位（数值在 SPICE 中确认）。
- 用两组电池得到 ±6 V（或 ±9 V）时，要提醒两轨之间的实际电压差。

## 6. 写作队列与轮次

| 队列 | 节点（按阅读顺序） |
|---|---|
| 作者 A | 30, 31, 32, 38 |
| 作者 B | 33, 34, 36, 37 |
| 作者 C | 35, 40, 41, 42 |
| 作者 D | 39, 43, 44, 45 |

| 轮次 | A | B | C | D |
|---|---|---|---|---|
| 1 | 30 | 33 | 35 | 39 |
| 2 | 31 | 34 | 40 | 43 |
| 3 | 32 | 36 | 41 | 44 |
| 4 | 38 | 37 | （准备 42 的资料，起草协调改动） | 45 |
| 5 | — | — | 42 | — |

每一轮的前置节点都已在更早的轮次完成（p2refs/sched.py 模拟结果）。42 依赖 30–41 的全部节点，所以最少需要 5 轮。

## 7. 协调人改动清单（作者不要自己改）

1. `notes/AUTHOR_GUIDE.md`：
   - §1 导航规则：全书最后一页从「29 page4」改为「45 page4」；
   - §8：「NN 一律是两位数字 01–29」改为「01–45」；
   - 名称来源：加上「30–45 见 00-design-part2 §5.1」。
2. `29-pullup-level-shift/page4.md`：导航的下一页从 README 改为 `[下一页：30 仪表放大器与电桥 · 直觉篇](../30-instrumentation-amp/page1.md)`。
3. `code/figs/00_figs.py`：NODES / EDGES / QUEUES 追加 30–45；新线索的颜色待定。
4. `README.md`：目录表追加 30–45；质量表的行等节点完成后再加。
5. `code/figs/lab_schem.py`：NODES 追加 30–45 的 page4 原理图条目。
6. `spice/models`：补充 LMC6482、CD4053 / CD4051、BD139 / BD140（IRLZ44N 已有）。

## 8. 自查命令

```bash
PY=/workspace/circuits-venv/bin/python
$PY code/figs/NN_figs.py
$PY tools/count_cjk.py NN-slug/page*.md --min 500
$PY tools/count_cjk.py NN-slug/page4.md --min 1500
$PY tools/run_blocks.py NN-slug/page*.md
$PY tools/run_blocks.py --scripts code/NN_sim.py code/figs/NN_figs.py
$PY tools/check_figs.py NN-slug/page*.md
$PY tools/fix_inline_math_spacing.py NN-slug/page*.md
$PY tools/fix_inline_math_spacing.py --check NN-slug/page*.md
$PY tools/check_github_math.py NN-slug/page*.md notes/NN-research.md
```

作者不运行任何 git 命令，由总纲提交。

## 9. 「[待核实]」清单（正文不得引用这些来源里的具体数值）

**ADI 资料（从盒子用 curl 访问超时，也没有用 WebFetch 打开）**

- AD630 数据手册；
- AD623 数据手册；
- Analog Dialogue 的 D 类放大器文章；
- MT-065。

**其他来源**

- ST L298、BD135 / 137 / 139 数据手册：st.com 用 curl 访问超时。
- TI SLOA088、SLOA023：均返回 404。
- tomarok VY 涡街 PDF：需要验证码。
- 横河励磁频率页面：只返回 JS 验证页。6.25 Hz 改引 ADI 文章。
- E+H 学习中心各页面：只返回验证页。
- electronics-tutorials.ws 功放页面（amp_5 / amp_6 / class-AB）：访问超时。
- NAMUR NE43 原文：需要会员下载。数值改引 Beckhoff、WAGO 页面。

**没有找到来源的内容**

- King 定律的具体公式形式：已打开的 Sierra 资料只给出名称和年份。
- MFB 带通「开环增益远大于 2Q²」的经验条件：作者要用 SPICE 验证，不要写成引用。
- 压电蜂鸣片的 pC/N 灵敏度：page4 以实测为准。

**说明**：以下 analog.com 页面从盒子用 curl 访问超时，但用 WebFetch 能打开，已按「WebFetch 可打开」引用：

- MT-061、MT-062；
- AD8331 数据手册；
- MAX7400 产品页；
- Analog Dialogue 的电磁流量计文章。

## 10. 协调者拍板（2026-10-27，取代 00-design-part2.md §9 的待定项）
1. 31 跨阻放大和 32 电荷放大**不合并**，32 建立在 31 之上。36 施密特整形和 37 过零/时差**不合并**。
2. Arduino（Uno/Nano）**可以用**，但第一次出现的节点（按阅读顺序最早用到它的那节）要放一个「最小必要知识」框：怎么装 Arduino IDE、怎么上传、引脚编号怎么看，并给出可直接复制的完整 sketch。每个实验的核心结论必须还能用万用表（或文中给出的无 Arduino 替代做法）验证。
3. 电源统一用**单电源 9–12 V 直流**（电池组或适配器），需要双极性信号时用「分压 + 电压跟随器（12 节）」做虚地，正文第一次用到时配原理图讲清。不用 ±6 V 双电池。全部 ≤12 V。
4. 预算：只用常见便宜元件，不写价格（没有可靠来源就不写数字）。
5. DAG 图颜色和 00_figs.py、README、AUTHOR_GUIDE、29 page4 的下一页链接、lab_schem.py 的 NODES 由协调者统一改，**作者不要改这些共享文件**。
6. 「[待核实]」信源：不得作为任何数字的出处。King 定律写成「经验公式」的一般形式并说明系数要靠标定；MFB 带通「开环增益要远大于 2Q²」用 SPICE 仿真演示，不当作引用结论。NE43 数值用 Beckhoff/WAGO 页面作出处。
7. 555：34、36 可以用 555，第一次出现时给引脚图、原理图和一句话工作原理（明确说明这是新器件，24 节讲的是 LM358 张弛振荡器）；能用 24 节的 LM358 振荡器替代的地方优先用它。
8. 文件边界：每个作者只写自己节点的 NN-slug/、code/NN_*.py、code/figs/NN_figs.py（节点专用原理图辅助函数写在自己的脚本里，不改 schem.py / lab_schem.py / figstyle.py）、spice/NN/、review/spice/NN.md。新器件 SPICE 模型放 spice/models/ 下新文件，文件名不得覆盖已有模型。不运行 git。

## 11. 给 42 capstone 的待办（理论专家 E1，协调者确认）
- 风扇实验的带通：1 kHz、Q=5 对风扇转速频率衰减 22–32 dB，不可用。改宽带，或 f₀≈250 Hz、Q≤1（按实测风扇频率定）。
- 风扇转速信号上拉到 Arduino 5 V，不得上拉到 9–12 V。
- 4–20 mA 输出继承 41 的接法：A0 读低边 100 Ω 采样电阻，250 Ω 只用万用表测。

## 12. 统一规则补充（协调者，2026-10-27 05:55，来源：工程实战派汇总）
- 电平安全：比较器和测速线的上拉电阻一律接 Arduino 5 V，不能接 9–12 V。凡是可能超过 5 V 的节点，都不能直接接 Arduino 引脚，必须先分压或经比较器做电平转换。5 V 器件（PAM8403 绝对最大 6 V；35 节的 LM358 和 CD4051 用 5 V 供电）不能接 9–12 V 主电源。
- 定时器：Timer1 输入捕获与 D9/D10 的 analogWrite 不能同时用；改动 Timer2 会让 D3/D11 的 tone() 和 PWM 失效。37 节放一个「定时器捕获」知识框；31 节提前放「Arduino 最小必要知识」框（第一次上传仍在 35 节 page4）。
- 正文里的代码块不得在仓库根目录写文件。图片保存到本节 figs 目录或临时目录，SPICE 脚本不得覆盖仓库里已有的 txt 和 csv（输出到临时目录或加参数）。
- 状态日志里作者的 done 行统一写成「NN-xxx done (author X)」，审阅修改完成写成「NN-xxx fix done (author X)」。
- 动手实验里不得用手去试温度，一律用测温探头、NTC 或万用表测温档。
- 术语（取代 §10 的「虚地」叫法）：单电源的电源中点（分压电阻加跟随器）统一叫「中点参考」，记作 V_MID（不用 V_M，44 节的 V_M 指电源电压），第一次出现在 30 节，讲清它和 05 节「虚地」（运放反相端被反馈拉到地电位）不是一回事。30–45 正文不再用「虚地」指电源中点，图上标签也统一成 V_MID。
- 回指规则：引用后面才学到的节点时，只能写成「预告」，不能把它当前置知识；要用到的前置知识回指前面的节，并用一句话回顾。
