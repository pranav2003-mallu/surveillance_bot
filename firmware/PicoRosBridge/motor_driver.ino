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
      analogWrite(LEFT_RPWM, pwm); analogWrite(LEFT_LPWM, 0);
    } else {
      analogWrite(LEFT_RPWM, 0); analogWrite(LEFT_LPWM, pwm);
    }
  } else {
    // RIGHT
    if (spd >= 0) {
      analogWrite(RIGHT_RPWM, pwm); analogWrite(RIGHT_LPWM, 0);
    } else {
      analogWrite(RIGHT_RPWM, 0); analogWrite(RIGHT_LPWM, pwm);
    }
  }
}

void setMotorSpeeds(int leftSpeed, int rightSpeed) {
  setMotorSpeed(LEFT, leftSpeed);
  setMotorSpeed(RIGHT, rightSpeed);
}

#endif
