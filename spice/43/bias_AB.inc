* 甲乙类：两只 1N4148（D1、D2）垫出约 2×0.7 V 偏置；
* 偏置电流不用电阻供给，而用两个恒流源（按 hFE 最坏 25 设计，要 ≥ 22 mA）：
*   上恒流源 Q3（BD140）：D5、D6 把基极钉在 +12 V 下面约 1.3 V，R_X3 27 Ω 定电流，约 24 mA 流进 b1
*   下恒流源 Q4（BD139）：D7、D8 把基极钉在 GND 上面约 1.3 V，R_X4 27 Ω 定电流，约 24 mA 从 b2 抽走
Rx3 vcc e3 27
Q3 b1 bq3 e3 BD140
XD5 vcc d5 1N4148
XD6 d5 bq3 1N4148
Rk3 bq3 0 4.7k
XD1 b1 m 1N4148
XD2 m b2 1N4148
Q4 b2 bq4 e4 BD139
Rx4 e4 0 27
XD7 bq4 d7 1N4148
XD8 d7 0 1N4148
Rk4 vcc bq4 4.7k
