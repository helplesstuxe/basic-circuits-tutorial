# 作者指南

写任何一页之前，先读完 [00-design.md](00-design.md)，找到你负责的节点的内容提要和它的前置节点。本指南是硬性规则；与本指南冲突时以 [specs/task-spec.md](../specs/task-spec.md) 为准。

## 1. 文件与页面结构

每个知识点一个文件夹，例如 `01-inverting-amp/`，里面只放三个页面和一个图片文件夹：

```text
01-inverting-amp/
├── page1.md      直觉篇
├── page2.md      原理与实现篇
├── page3.md      参数与调试篇
└── img/          本节点的全部 PNG（由脚本生成，不手工放图）
```

画图和仿真脚本放在 `code/`，文件名以节点编号开头，仿真脚本放 `code/NN_*.py`（例如 `code/01_sim.py`），画图脚本放 `code/figs/NN_figs.py`（例如 `code/figs/01_figs.py`）；共用模块 `figstyle.py`、`schem.py` 也在 `code/figs/`。

每页的固定结构：

- 第一行是一级标题，格式为「NN 电路名 · 直觉篇」（或「原理与实现篇」「参数与调试篇」）。
- 标题下面一行写导航：上一页、本节点其余两页、下一页，以及前置节点的链接。
- 跨节点链接一律写全名加篇名，格式 `[NN 名称 · 篇名](../NN-slug/pageN.md)`，例如 `[P3 运放入门 · 直觉篇](../P3-opamp-basics/page1.md)`、`[下一页：17 自锁 · 直觉篇](../17-self-locking/page1.md)`。名称照抄 00-design §5.1（写「17 自锁」，不写「17 自锁电路」「自锁控制」），链接指向具体的 pageN.md，不指向文件夹。
- **page1 直觉篇**：痛点引入（读者在什么场景下会需要这个电路）→ 生活类比 → 示意图或电路图 → 用一句话说出这个电路「做了什么」。
- **page2 原理与实现篇**：先补最小必要知识（或链接到前置节点）→ 推导，每一步都先用中文说意思再写公式，并代一组数算一遍 → 一段逐行注释的最小可运行 Python 仿真 → 仿真输出图和讲解 → 渐隐式例题（完整示例 → 关键步骤留空 → 变体迁移）。
- **page3 参数与调试篇**：每个元件参数的物理含义、常用取值范围，改变它以后波形或效果怎么变（最好配一张参数扫描图）→ 故障排查表 → 练习题。
- 故障排查表固定四列：

  | 现象 | 原因 | 怎么查 | 怎么改 |
  |---|---|---|---|

- 练习题至少 3 道，由易到难，最后一道是变体迁移题；答案放在 `<details><summary>答案</summary> … </details>` 里，`<summary>` 后空一行再写 Markdown。
- **每页正文不少于 500 汉字**，代码、公式、图注不计入。用 `tools/count_cjk.py` 检查。
- 有两个变体的节点（06、09、13、16）两种变体都要讲，见 00-design 的内容提要。

## 2. 图的规则

- 电路图用 schemdraw（通过 `code/figs/schem.py`），波形和曲线用 matplotlib（通过 `code/figs/figstyle.py`），全部输出 PNG。**禁止** ASCII 图、手工截图和 Mermaid。
- 图片由 `code/figs/NN_figs.py` 生成，存到 `NN-slug/img/`，文件名写成 `NN_pX_k_含义.png`，例如 `01_p2_1_waveform.png`。每张不超过 200 KB（`figstyle.save` 会自动压缩并检查）。
- 图号写成「图 NN-pX-k」：NN 是节点编号，X 是页码，k 是本页第几张图，从 1 开始连续。例如 `01-inverting-amp/page2.md` 里的第 2 张图是「图 01-p2-2」。
- 每张图三件套：
  1. **引导句**：图前一句话告诉读者要看什么，例如「请看图 01-p2-1 里橙色曲线的峰值」。
  2. **图注**：图下一行，格式为 `*图 01-p2-1　反相放大的输入与输出波形*`。
  3. **图后讲解**：至少两三句，说明图里的现象和它说明了什么。
- **颜色词必须与图一致**。figstyle 的固定配色（Okabe-Ito 色盲友好色板）如下，正文里照抄这些颜色词：

  | 用途 | figstyle 键 | 颜色词 |
  |---|---|---|
  | 输入电压 $V_i$ | `vin` | 蓝色 |
  | 输出电压 $V_o$ | `vout` | 橙色 |
  | 第三条曲线 | `third` | 红紫色（点划线） |
  | 反馈、基准电压 | `fb` | 蓝绿色（虚线） |
  | 电流 | `cur` | 天蓝色 |
  | 故障、错误情形 | `bad` | 朱红色（带 × 标记） |
  | 理想值 | `good` | 黑色虚线 |
  | 参考线、门限、0V、电源边界 | `ref` | 灰色点线 |

- 坐标轴标签一律写成「量 / 单位」，例如「电压 / V」「时间 / ms」，用 `figstyle.axlabels(ax, "时间", "ms", "电压", "V")`。
- 参考线（0V、 $V_{CC}$ 、门限、t = τ 等）用 `figstyle.ref_h` / `ref_v`，统一为灰色点线。
- **图上的每一个数字都必须由脚本打印到终端**（`figstyle.mark` 会自动打印），正文引用的数值要与打印结果一致，不许凭估计写。
- **关键结论要用 `assert` 断言**，例如 `assert abs(gain - (-10)) < 0.05`，这样参数被改错时脚本会直接报错。
- 正文只提本页的图号。`tools/check_figs.py` 会把「图 NN-pY-k」这种指向别的页的图号判为错误；要引用别页的图，写成链接加文字描述，例如「见 [01 反相放大 · 原理与实现篇](../01-inverting-amp/page2.md) 的波形图」。
- **答案图放在揭晓之后**：练习题的答案图只能出现在 `<details>` 里面，或者出现在正文揭晓答案的那句话之后。
- 用法示例：

```python
# 不运行（示意：figstyle 和 schem 的典型用法）
import numpy as np, matplotlib.pyplot as plt
import figstyle as fs                      # 配色、字体、保存
import schem                               # schemdraw 设置 + 自定义元件
import schemdraw.elements as elm

t = np.linspace(0, 2e-3, 2000)             # 时间轴：0 到 2 ms
vi = fs.sine(t, 1e3, amp=0.5)              # 1 kHz、幅值 0.5 V 的输入
fig, ax = plt.subplots(figsize=fs.SIZE["single"])
ax.plot(t * 1e3, vi, **fs.LS["vin"], label="$V_i$")
fs.ref_h(ax, 0, "0 V")                     # 灰色点线参考线
fs.axlabels(ax, "时间", "ms", "电压", "V") # 轴标签「量 / 单位」
fs.save(fig, "01", "01_p2_1_waveform.png") # 存到 01-inverting-amp/img/

with schem.drawing() as d:                 # 电路图
    d += elm.Resistor().label("$R_1$")
    d += (op := elm.Opamp().anchor("in1"))
schem.save_schem(d, "01", "01_p1_1_circuit.png")
```

- schemdraw 自带元件可以直接用：运放、二极管、稳压管、LED、整流桥、NPN/PNP 三极管、N/P 沟道 MOS 管、电阻、电容、电感、电位器、变压器、光耦、肖特基二极管、熔断器、开关、单刀双掷开关、按钮、继电器、正弦/方波/直流源、电池、灯、直流电机、地。继电-接触器控制图要用国标画法，请用 `schem.py` 里的自定义元件：`Coil`（线圈方框）、`ContactNO` / `ContactNC`（常开/常闭触点）、`PushNO` / `PushNC`（按钮）、`TimerNO` / `TimerNC`（时间继电器延时触点）、`ThermalHeater` / `ThermalNC`（热继电器）、`Motor3`（三相电机）、`LampX`（指示灯）。隔离电路用 `schem.barrier`（隔离带虚线）和 `schem.module`（带引脚名的模块方框）。运行 `python code/figs/schem.py --demo` 可以看到全部元件。

### schemdraw 0.23 注意事项

- 施密特反相器是 `schemdraw.logic.SchmittNot`（在 `logic` 模块里，`schemdraw.elements` 里没有）。
- `elm.NFet` / `elm.PFet` 不画体二极管，需要时自己加一个 `elm.Diode`；而且一定要显式写方向 `.theta(…)`，否则它会沿用上一个元件的方向，画歪。
- 横着串在电源线上的 MOS 管（比如 LDO 调整管、高边开关）用 `elm.NFet().theta(-90).reverse()`：源极在左、漏极在右、栅极朝上。
- `schem.module(...)` 画方框模块时要接 `.theta(0)`，否则会沿用前一个元件的方向。
- 读元件引脚坐标用 `.absanchors['gate']` 这类绝对坐标，不要用 `.anchors`（那是元件自身坐标系，旋转后就不对了）。
- `elm.Opamp` 也会继承上一个元件的方向；放运放前先 `.theta(0)` 或者在 `d.add` 之前把方向调回来。

## 3. 代码规则

- 一律 Python 3 + NumPy + matplotlib，必要时加 SciPy；用教程虚拟环境 `/workspace/circuits-venv` 运行。
- page2 里的仿真代码块必须**最小、可直接复制运行**，并且**逐行加中文注释**。代码块语言标为 `python`。
- 需要保存图片时用 `figstyle.save(fig, "NN", "文件名.png")`，图片输出到 `NN-slug/img/`。
- 代码块分三类：
  - 正常代码块：`tools/run_blocks.py` 会真的运行它，必须通过。
  - 示意片段：第一行写 `# 不运行`。
  - 学生填空：含 `____`，工具会自动跳过。
  - 确实无法运行的代码（例如需要硬件）：第一行写 `# 未经运行验证`，正文里也要说明。
- 正文里引用的数值必须来自脚本打印的结果。

## 4. 写作风格

- 读者只有高中电路水平。凡是用到他们「不会的」知识，必须先补最小必要知识或链接到前置节点。
- 积分、微分从「面积」「斜率」讲起；频率响应不讲复数。
- 符号严格按 00-design 第 4 节的符号表；每个符号在本页首次出现时用一句中文解释。
- 每个公式：先说中文意思 → 写公式 → 代一组数算一遍。
- 页面之间多用相对链接，例如 `[虚短](../P3-opamp-basics/page2.md)`。

### 加粗的标点规则

- 句末标点（。，、；：！？）和全角括号放在 `**` 外面：写 `**例 1：给 LED 选限流电阻**。`、`**练习 1**：`，不写 `**……。**`、`**练习 1：**`。原因：闭合的 `**` 前面是标点、后面紧跟汉字时，GitHub 不认它是闭合符，页面上会露出 `**`（`**朱红色带×**的` 这种以符号结尾的也一样，要改写成以文字结尾）。
- 闭合 `**` 前面不能有空格，开头 `**` 后面也不能有空格：写 `**重点**`，不写 `**重点 **`、`** 重点**`。

## 5. GitHub 公式规则

md 要能直接在 github.com 上正常显示公式：

- 行内公式用 `$…$`，块公式用 `$$…$$`。
- 开头的 `$` 紧跟中文、全角标点、字母或 `-` 时 GitHub 不渲染，前面要补一个空格（紧跟 `(` 或 `**` 时不用补）。**全角标点后面也要补**：写 `电压， $V_o$`，不写 `电压，$V_o$`。写完运行 `tools/fix_inline_math_spacing.py 文件…`（不带 `--check` 就是修复模式，直接改文件），再用 `--check` 确认没有遗漏。
- GitHub 会吃掉 Markdown 转义，要改成 KaTeX 和 MathJax 都认识的写法：
  - `\,` `\!` `\;` `\:` 改成 `\thinspace` `\negthinspace` `\thickspace` `\medspace`；
  - `\{` `\}` 改成 `\lbrace` `\rbrace`，`\|` 改成 `\Vert`，矩阵里的 `\\` 改成 `\cr`；
  - `<` `>` `*` 改成 `\lt` `\gt` `\ast`；
  - 公式末尾的 `\%` 移到公式外面，写成 `$…$%`。
- 含 `\begin…` 的整行 `$$…$$` 要单独成段，前后各留一个空行。
- 用 `tools/check_github_math.py` 检查：它会调用 GitHub 的渲染接口，统计源文件里的公式数和渲染出来的公式数，两者相等才算通过。加 `--fix` 会做上面那些等价替换。
- 行内公式里的 `<` `>` 一律写成 `\lt` `\gt`，例如 `$R_f \lt 2R_g$`、`$V_i \gt 0$`（直接写 `<` 会被当成 HTML 标签吞掉）。
- `tools/check_github_math.py` 会直接判失败的写法：公式里的 `\%`、`\!`、`\,`（分别改成公式外的 `%`、`\negthinspace`、`\thinspace`），以及开头 `$` 前缺空格（包括紧跟全角标点的情况）。
- `<details>` 答案里不写 `$$…$$` 块公式（GitHub 在折叠块里渲染不稳定），改用行内 `$…$`，或者把式子拆成几行行内公式。
- 图注里不写任何公式（`$…$` 都不要），公式放正文：图注只写「图 NN-pX-k　这张图是什么」，要讲的关系式写在图前引导句或图后讲解里。
- GitHub 手机 App 不渲染公式，这是平台限制，不用处理。

## 6. 安全提醒

涉及 220V/380V 市电的节点（06、09、17、18、19、20，以及扩展篇的 22、23、24）必须在 page1 开头和每个实验或接线环节放安全警示框：

```markdown
> [!WARNING]
> **市电危险**：本电路的实际版本接 220V/380V 市电，触电可能致命。本页的仿真和动手实验只在 12V 以下的低压电源上进行；任何接线、改线都必须在断电并验电后操作，由持证电工完成。
```

警示框里要写清楚本节点具体的危险点，例如整流电路的滤波电容断电后仍然带电、星三角启动的两个接触器同时吸合会相间短路。

## 7. 诚实规则

- 链接和引文必须真实可访问：只引用自己实际打开过的网页或手册，写出完整 URL。无法确认时写「[待核实]」，**禁止编造**书名、页码、网址或数据。
- 器件参数（例如某型号的耐压、 $V_{GS(th)}$ ）优先引用数据手册；拿不准就写「典型值」并标「[待核实]」。
- 代码没有真正跑通的，必须标「未经运行验证」。

## 8. 自查命令（交稿前全部通过）

在仓库根目录运行，把 `NN-slug` 换成你的文件夹：

```bash
PY=/workspace/circuits-venv/bin/python
$PY code/figs/NN_figs.py                              # 重新生成本节点全部图片，检查 assert 和打印的数值
$PY tools/count_cjk.py NN-slug/page*.md --min 500     # 每页正文汉字数 ≥ 500
$PY tools/run_blocks.py NN-slug/page*.md              # 页面里的代码块逐块运行
$PY tools/run_blocks.py --scripts code/NN_sim.py code/figs/NN_figs.py  # 本节点脚本逐个运行
$PY tools/check_figs.py NN-slug/page*.md              # 图片存在、PNG、< 200 KB，图号连续且被引用
$PY tools/fix_inline_math_spacing.py NN-slug/page*.md # 修复模式：直接补公式前的空格
$PY tools/fix_inline_math_spacing.py --check NN-slug/page*.md  # 确认没有遗漏
$PY tools/check_github_math.py NN-slug/page*.md notes/NN-research.md  # GitHub 渲染公式数与源文件一致
```

- 画图脚本的路径是 `code/figs/NN_figs.py`（不是 `code/NN_figs.py`），仿真脚本是 `code/NN_sim.py`；P1–P3 的 NN 就写 `P1` `P2` `P3`。
- 给工具传**文件**，不要传文件夹：写 `NN-slug/page*.md`，不写 `NN-slug/`。有的工具收到文件夹会去扫整个子目录甚至全仓库，有的直接不认。
- 上面几个工具不检查加粗标点和跨节点链接格式，这两条（§4「加粗的标点规则」、§1 链接格式）交稿前自己搜一遍 `**` 和 `](../`。

## 9. 提交规则

- **作者不运行任何 git 命令**（不 add、不 commit、不 push、不切分支）。写完、自查通过后，向总纲报告改动的文件清单和自查结果。
- 总纲是唯一的提交者，负责复核、提交和推送。
- 只修改自己负责的节点文件夹和对应的 `code/NN_*.py`、`code/figs/NN_figs.py`。需要改 `code/figs/` 里的共用模块或 `tools/` 时，先告诉总纲。
