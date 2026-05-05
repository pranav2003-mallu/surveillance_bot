#ifdef USE_BASE

void initMotorController() {
  pinMode(LEFT_EN, OUTPUT); pinMode(LEFT_RPWM, OUTPUT); pinMode(LEFT_LPWM, OUTPUT);
  pinMode(RIGHT_EN, OUTPUT); pinMode(RIGHT_RPWM, OUTPUT); pinMode(RIGHT_LPWM, OUTPUT);
  
  // Enable motor drivers
  digitalWrite(LEFT_EN, HIGH);
  digitalWrite(RIGHT_EN, HIGH);
}

void setMotorSpeed(int i, int spd) {
  int pwm = abs(spd);
  // limit max PWM to MAX_PWM for Pico's default 8-bit analogWrite
  if (pwm > MAX_PWM) pwm = MAX_PWM;
  
  if (i == LEFT) {
    if (spd >= 0) {
      pinMode(LEFT_LPWM, OUTPUT);
      digitalWrite(LEFT_LPWM, LOW);
      analogWrite(LEFT_RPWM, pwm);
    } else {
      pinMode(LEFT_RPWM, OUTPUT);
      digitalWrite(LEFT_RPWM, LOW);
      analogWrite(LEFT_LPWM, pwm);
    }
  } else {
    // RIGHT (Not inverted, wiring matches left)
    if (spd >= 0) {
      pinMode(RIGHT_LPWM, OUTPUT);
      digitalWrite(RIGHT_LPWM, LOW);
      analogWrite(RIGHT_RPWM, pwm);
    } else {
      pinMode(RIGHT_RPWM, OUTPUT);
      digitalWrite(RIGHT_RPWM, LOW);
      analogWrite(RIGHT_LPWM, pwm);
    }
  }
}

void setMotorSpeeds(int leftSpeed, int rightSpeed) {
  setMotorSpeed(LEFT, leftSpeed);
  setMotorSpeed(RIGHT, rightSpeed);
}

#endif
