* 故障：IN2 直接接地，只有 IN1 收到 PWM（不要这样接！）
Bc1 c1 0 V = 5*0.5*(1+tanh(2000*(V(s)-V(t))))
Rc1 c1 in1 1k
Cc1 in1 0 100p
Vin2 in2 0 0
