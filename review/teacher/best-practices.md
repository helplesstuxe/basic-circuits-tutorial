# 面向初学者的教学实践：审读依据（资深教师）

本文件列出本次审读用到的六条教学原则，每条都注明出处（下列链接审读时都实际打开过），并说明它在本教程里对应检查什么。读者假定只学过高中物理的电路部分。

## 1. 控制认知负荷（cognitive load）

- **要点**：初学者的工作记忆容量很小。应当把新材料拆成小步，去掉与学习目标无关的负荷，例如图和文字分开放、读者要来回对照（split-attention），或者同一信息重复呈现（redundancy）。随着学生水平提高，样例的帮助会变成负担（expertise reversal），所以讲解的详略要随章节推进而调整。
- **出处**：
  - NSW CESE，*Cognitive load theory: Research that teachers really need to understand*（2017）：https://education.nsw.gov.au/about-us/education-data-and-research/cese/publications/literature-reviews/cognitive-load-theory 　PDF：https://education.nsw.gov.au/content/dam/main-education/about-us/educational-data/cese/2017-cognitive-load-theory.pdf
  - Rosenshine，*Principles of Instruction*，American Educator，2012 年春季号（"Present new material in small steps"）：https://www.aft.org/ae/spring2012/rosenshine
- **本教程检查**：
  - 第一次出现的、超出高中范围的术语，要在原处解释，或者给出明确的链接，例如三相、体二极管、0.707、去耦、占空比。
  - 一页只承担本页该做的事：直觉篇不堆公式，参数与调试篇不重新推导。
  - 图题和正文里的颜色词必须与图一致，否则读者要来回对照，这属于额外负荷。

## 2. 样例与渐隐样例（worked / faded examples）

- **要点**：
  - 先给出完整的示范解答，再给部分留空的"完成题"，最后让学生独立解题，比直接做题更有效。
  - IES 实践指南建议把样例解答和练习题交替安排。
- **出处**：
  - Pashler 等，*Organizing Instruction and Study to Improve Student Learning*，IES Practice Guide NCER 2007-2004（建议 2："Interleave worked example solutions with problem-solving exercises"）：https://ies.ed.gov/ncee/wwc/Docs/PracticeGuide/20072004.pdf
  - NSW CESE 2017（worked example effect、completion problems）：链接同上。
  - Rosenshine 2012（"Provide models"，"Provide scaffolds for difficult tasks"）：链接同上。
- **本教程检查**：
  - page2 是否按"例 1 完整示范 → 例 2 填空 → 例 3 变体迁移"递进。
  - page3 是否至少有 3 道练习、由易到难，且最后一道是"变体迁移"题。这是 AUTHOR_GUIDE L32 的要求，00-design L36 的写法同样是"变体迁移"。
  - 各节标签写法是否统一。

## 3. 提取练习（retrieval practice）与间隔复习

- **要点**：
  - 让学生从记忆里把知识"提取"出来（做小测、自问自答），比重读更能巩固记忆。
  - 复习要隔开时间，并且以后反复回顾。
- **出处**：
  - Pashler 等 2007（建议 1：Space learning over time；建议 5：Use quizzing to promote learning）：链接同上。
  - The Learning Scientists，*Retrieval practice* 博文（2016-06-23）：https://www.learningscientists.org/blog/2016/6/23-1
  - RetrievalPractice.org：https://www.retrievalpractice.org/
  - Rosenshine 2012（"Begin a lesson with a short review"，"Engage students in weekly and monthly review"）：链接同上。
- **本教程检查**：
  - 每节 page2 开头的"用到的旧知识"是否回指正确的节点和页，例如 17 回指 P1 就是错的。
  - 练习是否考到了本节的关键结论，而不只是代一个公式。
  - 后续节点是否回扣前面的概念（例如 24 回扣 23 的光耦、26 回扣 14 的回差）。

## 4. 图文双编码（dual coding）

- **要点**：把文字讲解与图示结合起来，并让两者表达同一件事，学生可以从两条通路理解和记忆。
- **出处**：
  - Pashler 等 2007（建议 3："Combine graphics with verbal descriptions"）：链接同上。
  - The Learning Scientists，*Dual coding* 博文（2016-09-01）：https://www.learningscientists.org/blog/2016/9/1-1
- **本教程检查**：
  - 每张图都要在正文里用"图 NN-pX-k"引用，颜色词要与全书约定一致：蓝色输入、橙色输出、红紫色点划线、蓝绿色虚线、天蓝色电流、朱红色带 ×、黑色虚线、灰色点线。
  - 不能用约定以外的颜色名（例如"红色"）去指代某条曲线。

## 5. 先处理误区（misconceptions first）

- **要点**：
  - 物理教育研究长期记录了学生关于电路的常见错误想法，相关工作见 McDermott & Shaffer 关于入门电学课程开发的研究（Am. J. Phys.）。这里只按下面这篇 2024 年论文的参考文献列表转引，审读时没有打开原文。
  - Bauman 等 2024 年的论文进一步主张：不仅要找出误区，还要识别学生已有的、可以发展的直觉（"资源"），并在此基础上建构。
- **出处**：
  - *Student conceptual resources for understanding electric circuits*，Phys. Rev. Phys. Educ. Res. 20, 020128（2024）：https://journals.aps.org/prper/pdf/10.1103/PhysRevPhysEducRes.20.020128
  - Pashler 等 2007（建议 7："Ask deep explanatory questions"）：链接同上。
- **本教程检查**：
  - 直觉篇的痛点和误区是否先于公式出现，例如 13 的误区先行、25 的"IN1 占空比 70%"误区、26 的"RC 接无回差引脚"。
  - 本教程自己有没有制造新的误区，例如 19 的"串了两段"会让读者推出 ÷2，P3 把 14 也列入"用虚短的节点"。

## 6. 由具体到抽象（concrete to abstract）

- **要点**：把抽象表示（公式、符号）与具体表示（实物、类比、数值例子）明确联系起来，并逐步过渡到抽象。
- **出处**：
  - Pashler 等 2007（建议 4："Connect and integrate abstract and concrete representations of concepts"）：链接同上。
  - Rosenshine 2012（"Provide models"）：链接同上。
- **本教程检查**：
  - 是否按"类比 → 低压仿真/动手 → 公式 → 参数"的顺序展开。
  - 公式后面是否有"中文意思"和具体数值，26 的每个推导都做到了。
  - 有安全风险的"具体体验"必须改成仪表测量，例如 07 的"用手碰三极管"和 08 的"散热片不烫手"。

## 附：与本教程直接相关的工程参考

- TI 应用笔记 SLAA067。本审读只用它核对 P1 page2 引用的"约 10% 误差"原文：https://www.ti.com/lit/an/slaa067/slaa067.pdf
