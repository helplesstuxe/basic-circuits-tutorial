* 45 实验电路的功放部分（page4 的接法）：LM386 + 脚7 10 µF + 输出 220 µF + 吸收网络 10 Ω/47 nF
* 负载：10 Ω 限流电阻串 8 Ω 喇叭（喇叭当 8 Ω 电阻），喇叭另一端接 GND（LM386 是单端输出，可以接地）
* 端口：in（脚3）、vs（脚6）、out（脚5）、spk（220 µF 之后）、sp2（10 Ω 与喇叭之间）、g1 g8（增益脚）
.subckt AMP in vs out spk sp2 g1 g8
X1 g1 0 in 0 out vs byp g8 LM386
Cbyp byp 0 10u
Cvs vs 0 100u
Co out spk 220u
Rlim spk sp2 10
Rspk sp2 0 8
Rz out z 10
Cz z 0 47n
.ends AMP
