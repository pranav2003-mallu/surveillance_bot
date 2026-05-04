#ifdef USE_BASE

volatile long l_enc_pos = 0L;
volatile long r_enc_pos = 0L;

// =====================================================
// SKID STEER: Only REAR encoders used for PID feedback
// Using all 4 encoders would double-count ticks and
// cause the PID to reduce PWM, stalling motors.
// Front encoder pins are completely removed from code.
// =====================================================

// Left Rear Encoder ISR (only rear left)
void lrEncoderISR() {
  if (digitalRead(LR_ENC_PIN_A) == digitalRead(LR_ENC_PIN_B)) l_enc_pos++; else l_enc_pos--;
}

// Right Rear Encoder ISR (only rear right)
void rrEncoderISR() {
  if (digitalRead(RR_ENC_PIN_A) == digitalRead(RR_ENC_PIN_B)) r_enc_pos--; else r_enc_pos++;
}

void initEncoders() {
  // Configure rear encoder pins only
  pinMode(LR_ENC_PIN_A, INPUT_PULLUP);
  pinMode(LR_ENC_PIN_B, INPUT_PULLUP);
  pinMode(RR_ENC_PIN_A, INPUT_PULLUP);
  pinMode(RR_ENC_PIN_B, INPUT_PULLUP);

  // Attach interrupts ONLY to rear encoders
  attachInterrupt(digitalPinToInterrupt(LR_ENC_PIN_A), lrEncoderISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(RR_ENC_PIN_A), rrEncoderISR, CHANGE);
}

long readEncoder(int i) {
  if (i == LEFT) return l_enc_pos;
  else return r_enc_pos;
}

void resetEncoder(int i) {
  if (i == LEFT) l_enc_pos = 0L;
  else r_enc_pos = 0L;
}

void resetEncoders() {
  resetEncoder(LEFT);
  resetEncoder(RIGHT);
}

#endif
