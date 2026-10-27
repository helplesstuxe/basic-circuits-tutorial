// 38 同步检波：Arduino Uno 既当「励磁源」又当「数字锁相」
// D9  = 励磁方波（Timer1 OC1A，6.25 Hz），经 RS1 1 MΩ 进夹具
// D10 = 参考方波（Timer1 OC1B，同频，相位可调），送 LM393 比较器 → CD4053，也给本程序当「加/减」依据
// D5  = tone() 发 50 Hz 干扰（Timer2；所以 D3、D11 的 PWM 这时不能用）
// A0  = INA 输出经 10k/10k 分压后的电压（0～9 V → 0～4.5 V）
// 串口 115200：0 = 相位 0°，4 = 45°，9 = 90°，f = 180°（翻转），t = 干扰 50 Hz，u = 干扰 51 Hz，n = 关干扰
// h / l = 停表，D9、D10 一起停在高 / 低电平（用万用表做静态检查）；再发 0 恢复
// 注意：Timer1 被占用，D9、D10 不能再用 analogWrite

const float VREF = 5.00;     // 用万用表量 Arduino 的 5V 脚，把实测值填在这里
const float GAIN = 21.0;     // 30 节仪表放大器：1 + 2×10k/1k
const float DIVIDER = 2.0;   // A0 前面的 10k/10k
const unsigned int TOP = 4999;          // 半周期 = (TOP+1) 个计数 × 16 µs = 80 ms（6.25 Hz）；改励磁频率只改这一行
const unsigned long BLANK_US = (TOP + 1UL) * 8UL;  // 每次换向后先等半个半周期（TOP = 4999 时 40 ms），前一半不用

long sumP = 0, sumN = 0;
unsigned int nP = 0, nN = 0;
bool lastRef = false;
unsigned long tEdge = 0, tSample = 0;
float avg8 = 0;
int nAvg = 0;

void startTimer1(unsigned int leadCounts, bool invert) {
  TCCR1B = 0;                                   // 先停表
  TCCR1A = _BV(COM1A0) | _BV(COM1B0);           // 比较匹配时翻转 OC1A（D9）、OC1B（D10）
  TCNT1 = 0;
  OCR1A = TOP;                                  // CTC 的 TOP：TOP+1 个计数 = 半周期（预分频 256）
  OCR1B = TOP - leadCounts;                     // D10 比 D9 早 leadCounts 个计数翻转，1 个计数 = 180°/(TOP+1)
  if (PINB & _BV(PB1)) TCCR1C = _BV(FOC1A);     // 强制把两路都放到低电平再起跑
  if (PINB & _BV(PB2)) TCCR1C = _BV(FOC1B);
  if (invert) TCCR1C = _BV(FOC1B);              // 180°：D10 再翻一次，和 D9 正好相反
  TCCR1B = _BV(WGM12) | _BV(CS12);              // CTC 模式 4，预分频 256，开始计数
  sumP = sumN = 0; nP = nN = 0; nAvg = 0; avg8 = 0;
}

void setup() {
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  Serial.begin(115200);
  startTimer1(0, false);
  Serial.println(F("38 lock-in: 0/4/9/f = phase 0/45/90/180, t/u/n = 50 Hz/51 Hz/off, h/l = hold"));
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '0') { startTimer1(0, false);    Serial.println(F("# phase 0")); }
    if (c == '4') { startTimer1((TOP + 1) / 4, false); Serial.println(F("# phase 45")); }
    if (c == '9') { startTimer1((TOP + 1) / 2, false); Serial.println(F("# phase 90")); }
    if (c == 'f') { startTimer1(0, true);     Serial.println(F("# phase 180")); }
    if (c == 't') { tone(5, 50);  Serial.println(F("# tone 50 Hz")); }
    if (c == 'u') { tone(5, 51);  Serial.println(F("# tone 51 Hz")); }
    if (c == 'n') { noTone(5);    Serial.println(F("# tone off")); }
    if (c == 'h' || c == 'l') {                 // 静态检查：停掉 Timer1，两只脚一起停在高或低
      TCCR1B = 0; TCCR1A = 0;                   // 断开 OC1A/OC1B，脚交还给 digitalWrite
      digitalWrite(9, c == 'h'); digitalWrite(10, c == 'h');
      Serial.println(c == 'h' ? F("# hold HIGH") : F("# hold LOW"));
    }
  }

  bool ref = PINB & _BV(PB2);                   // 直接读 D10 的引脚状态
  unsigned long now = micros();
  if (ref != lastRef) {                         // 参考换向
    tEdge = now;
    if (ref && nP > 0 && nN > 0) {              // 上升沿 = 一个完整周期结束，出一个结果
      float diffCounts = ((float)sumP / nP - (float)sumN / nN) / 2.0;
      float eP = diffCounts * VREF / 1024.0 * DIVIDER / GAIN * 1000.0;   // 折算回夹具 P 点，单位 mV
      nAvg = (nAvg < 8) ? nAvg + 1 : 8;
      avg8 += (eP - avg8) / nAvg;               // 前 8 个是累计平均，之后是 α = 1/8 的指数平均（发 0/4/9/f 时清零）
      Serial.print(F("E_mV=")); Serial.print(eP, 3);
      Serial.print(F("  avg8=")); Serial.println(avg8, 3);
      sumP = sumN = 0; nP = nN = 0;
    }
    lastRef = ref;
  }
  if (now - tSample >= 1000UL) {                // 每 1 ms 采一次
    tSample += 1000UL;
    if (now - tEdge >= BLANK_US) {              // 只要每个半周期的后一半
      int a = analogRead(A0);
      if (ref) { sumP += a; nP++; } else { sumN += a; nN++; }
    }
  }
}
