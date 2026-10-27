* DRV8871 模块（行为模型）
* DRV8871 行为模型：真值表 10→OUT1 高/OUT2 低，01→反过来，11→两路都低（刹车），00→两路都关（滑行）
* 高边 0.307 Ω、低边 0.258 Ω（数据手册典型值，合计 0.565 Ω）；未建模 0.7 µs 传播延迟和 220 ns 死区，带体二极管；电流表 Vam 串在 VM 线上（大电容在表后面）
Vam vcc vm 0
Cb1 vm 0 100u
Cb2 vm 0 100n
Rq vm 0 4k
.func hi(x) {0.5*(1+tanh(40*(x-1.5)))}
* 高边只在「另一路已明确为低（< 1.0 V）」时导通：1.0～1.5 V 之间两管都关，相当于死区，防止上下管同时导通
.func lo(x) {0.5*(1-tanh(40*(x-1.0)))}
Bh1 vm o1 I = (V(vm)-V(o1))*(hi(V(in1))*lo(V(in2))/0.307 + 1e-6)
Bl1 o1 0 I = V(o1)*(hi(V(in2))/0.258 + 1e-6)
Bh2 vm o2 I = (V(vm)-V(o2))*(hi(V(in2))*lo(V(in1))/0.307 + 1e-6)
Bl2 o2 0 I = V(o2)*(hi(V(in1))/0.258 + 1e-6)
Dh1 o1 vm dbody
Dl1 0 o1 dbody
Dh2 o2 vm dbody
Dl2 0 o2 dbody
Co1 o1 0 200p
Co2 o2 0 200p
.model dbody d is=1e-12 n=1.5 rs=0.05 cjo=100p
