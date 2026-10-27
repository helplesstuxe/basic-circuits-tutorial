* LM386 行为模型（教学用，作者 D 依据 TI SNAS545D 数据手册搭建，不是 TI 官方模型）
* 引脚：1 GAIN  2 IN-  3 IN+  4 GND  5 VOUT  6 VS  7 BYPASS  8 GAIN
* 1) 两个输入各 50 kΩ 到地（手册框图）
* 2) 增益：A = 2 x 15k / (150 + 1.35k || 外接 1-8)，用理想反相结构实现：
*    差分输入 -> 150 Ω -> 脚8 -> 1.35 kΩ -> 脚1（虚地），反馈 30 kΩ
*    运放开环 1e5、单极点，GBW 取 6.3 MHz，使增益 20 时带宽约 300 kHz（手册 BW 300 kHz）
* 3) 输出直流 = 脚7 电压；脚7 由 VS-15k-脚7-15k-GND 分压（约 VS/2），外接电容滤掉电源纹波
* 4) 摆幅：离两条电源轨各 1.15 V（由手册 LM386N-3 在 9 V/8 Ω 的 700 mW 反推，见 review/spice/45.md）
* 5) 电源电流 = 静态 IQ（参数 4.0 mA，加上脚7 分压电阻的 0.3 mA，9 V 时共约 4.3 mA，对应手册图 9-4 在 9 V 处的读数）+ 输出向外送出的电流（只算正半周）
.subckt LM386 g1 inm inp gnd out vs byp g8 params: IQ=4.0m VLOSS=1.15
Rinm inm gnd 50k
Rinp inp gnd 50k
Ediff nd gnd inp inm 1
Re1 nd g8 150
Re2 g8 g1 1.35k
* 理想运放：开环 1e5，极点 63 Hz -> GBW 6.3 MHz
Gop gnd x g1 gnd 1
Rop x gnd 1e5
Cop x gnd {1/(2*3.14159265*63*1e5)}
Eo y gnd gnd x 1
Rf y g1 30k
Rb1 vs byp 15k
Rb2 byp gnd 15k
Bu u gnd V = V(byp,gnd) - V(y,gnd)
Bclip oc gnd V = min(max(V(u,gnd), {VLOSS}), V(vs,gnd) - {VLOSS})
Vsense oc out 0
Biq vs gnd I = {IQ} + max(I(Vsense), 0)
.ends LM386
