* 两路互补比较（AD 调制）
* 两路比较器（U3，LM393）：行为模型（完整 TI 宏模型配开关桥会让 ngspice 步长崩溃，见 review/spice/44.md）；
* 输出 0/5 V（集电极开路 + 1 kΩ 上拉到 5 V 的效果），再经 1 kΩ/100 pF 给出约 0.1 µs 边沿
Bc1 c1 0 V = 5*0.5*(1+tanh(2000*(V(s)-V(t))))
Rc1 c1 in1 1k
Cc1 in1 0 100p
Bc2 c2 0 V = 5*0.5*(1+tanh(2000*(V(t)-V(s))))
Rc2 c2 in2 1k
Cc2 in2 0 100p
