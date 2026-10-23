# 18 互锁 · 资料笔记（作者 D）

以下网页均已实际打开阅读。

1. BCcampus Open Textbook《Basic Motor Control》第 36 章 Forward/Reverse Control Circuits https://pressbooks.bccampus.ca/basicmotorcontrol/chapter/forward-reverse-control-circuits/
   - 交换三根进线中的任意两根即可反转；正转接触器 L1→T1、L2→T2、L3→T3，反转接触器 L1→T3、L2→T2、L3→T1。
   - 两只接触器必须电气互锁 + 机械互锁；同时得电会短路，后果危险。
   - 电气互锁：一个方向线圈的常闭触点串在另一方向线圈回路里；正转时按反转无效，必须先按停止。
   - 机械互锁是"最后一道防线"：即使两个线圈都得电，也只有一个衔铁能吸到底，被挡住的那只会剧烈抖动（chattering）。
   - 按钮互锁需要四触点（常开 + 常闭）复合按钮；可不按停止直接反转，但这种突然反转（反接，plugging）对电机冲击大；仍然需要电气互锁。
2. 电工天下《交流接触器连锁电动机正反转控制原理图与故障处理》https://www.dgjs123.com/diandongji/1573.html
   - 中文术语：接触器互锁、按钮互锁、双重互锁；KM1、KM2 同时吸合造成相间短路。
   - 同时按下两个复合按钮，两只接触器线圈都不能通电。
   - 调试：接触器上口接线保持一致，在下口调相；通电试验时先断开电动机接线。
   - 故障："叭哒"一下吸不住——互锁常闭接点接成了"自己锁自己"；一抬手就断开——自锁接点接错。
3. 规范网《按钮、接触器双重联锁控制线路优缺点》https://www.guifan.net/zhishi/2022/64180.html
   - 接触器联锁可靠但必须先按停止；按钮联锁操作方便，但 KM1 主触头熔焊或被异物卡住时，即使线圈失电主触头也不分断，此时按 SB2 会造成相间短路。
   - 双重联锁兼具两者优点，缺点是线路复杂、容易接错。
   - 检查方法：断开主电路，用万用表测控制回路，按下按钮应读到线圈直流电阻；手动压下另一接触器应变为断路。
4. Schneider Electric FAQ FA109542（LAD9R1 换向组件构成）https://www.se.com/uk/en/faqs/FA109542/
   - LAD9R1 = 机械互锁 LAD9V2 + 上口连接排 LAD9V5 + 下口（换相）连接排 LAD9V6；LAD9R1V 另含电气互锁接线件 LAD9V1。
5. GT-Engineering《Power Contactors》https://www.gt-engineering.it/en/insights/electrical-hazard-and-arc-flash-mitigation/contactors-used-in-safety-applications/power-contactors/
   - 引 IEC 60947-4-1 附录 F：镜像触点（mirror contact）是不能和常开主触点同时处于闭合位置的常闭辅助触点。→ 主触点熔焊时常闭辅助触点保持断开，接触器互锁仍有效。
6. 沿用 17 的资料：Schneider TeSys D 目录（闭合时间 12–22 ms，断开时间 4–19 ms；释放电压 0.3–0.6 Uc）https://nanologicautomation.com/pdf/switch-gears/contractors/Schneider-Contactors-TesysD-Nano-Logic-Automation.pdf

仿真用的示意参数：吸合 20 ms（12–22 ms 之内）、释放 10 ms（4–19 ms 之内）。
7. （本轮补）西门子 3RT2037-1AR60 数据表 https://support.industry.siemens.com/teddatasheet/?caller=SIOS&format=pdf&language=en&mlfbs=3RT2037-1AR60 （已打开）
   - closing delay at AC 10…80 ms；opening delay at AC 10…18 ms；arcing time 10…20 ms；带 IEC 60947-4-1 镜像触点。
   - 与 TeSys D 不是同一型号，page3 只借用量级并注明。
8. （本轮补）ABB Technical Application Papers No. 26 https://library.e.abb.com/public/619009ca06434972a40b3479a1ed3c69/AP_Apparecchi-manovra-MT(EN)C_1VCP000735.pdf （已下载打开）
   - 触点分开后电弧使电流继续流一段时间；断路器在交流电流自然过零时熄弧；交流电流每周期过零两次。→ 50 Hz 半周期 10 ms，与燃弧 10～20 ms 一致。
原核实标记（电弧持续时间）已据第 7、8 条解决并删除；18_sim.py 打印并断言 10 ms 半周期和"20 ms 空档 − 20 ms 燃弧 = 0 ms"。
