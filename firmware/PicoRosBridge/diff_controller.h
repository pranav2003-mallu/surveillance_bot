#ifndef DIFF_CONTROLLER_H
#define DIFF_CONTROLLER_H

typedef struct SetPointInfo {
  double TargetTicksPerFrame;
  long Encoder;
  long PrevEnc;
  int PrevInput;
  int ITerm;
  long output;
} SetPointInfo;

SetPointInfo leftPID, rightPID;

/* PID Parameters. Can be tuned dynamically via command 'u' */
int Kp = 20;
int Kd = 12;
int Ki = 0;
int Ko = 50;

unsigned char moving = 0;

// Odometry variables
float odom_x = 0.0;
float odom_y = 0.0;
float odom_theta = 0.0;
float odom_vx = 0.0;
float odom_vth = 0.0;
long lastOdomLeft = 0;
long lastOdomRight = 0;

const float WHEEL_RADIUS = 0.065;
const float WHEEL_BASE = 0.317;
const float TICKS_PER_REV = 330.0;
const float METERS_PER_TICK = (2.0 * PI * WHEEL_RADIUS) / TICKS_PER_REV;

void resetPID(){
   leftPID.TargetTicksPerFrame = 0.0;
   leftPID.Encoder = readEncoder(LEFT);
   leftPID.PrevEnc = leftPID.Encoder;
   leftPID.output = 0;
   leftPID.PrevInput = 0;
   leftPID.ITerm = 0;

   rightPID.TargetTicksPerFrame = 0.0;
   rightPID.Encoder = readEncoder(RIGHT);
   rightPID.PrevEnc = rightPID.Encoder;
   rightPID.output = 0;
   rightPID.PrevInput = 0;
   rightPID.ITerm = 0;
}

void doPID(SetPointInfo * p) {
  long Perror;
  long output;
  int input;

  input = p->Encoder - p->PrevEnc;
  Perror = p->TargetTicksPerFrame - input;

  output = (Kp * Perror - Kd * (input - p->PrevInput) + p->ITerm) / Ko;
  p->PrevEnc = p->Encoder;

  output += p->output;
  if (output >= MAX_PWM)
    output = MAX_PWM;
  else if (output <= -MAX_PWM)
    output = -MAX_PWM;
  else
    p->ITerm += Ki * Perror;

  p->output = output;
  p->PrevInput = input;
}

void updatePID() {
  long curr_left = readEncoder(LEFT);
  long curr_right = readEncoder(RIGHT);

  leftPID.Encoder = curr_left;
  rightPID.Encoder = curr_right;

  // ODOMETRY CALCULATION
  long delta_left = curr_left - lastOdomLeft;
  long delta_right = curr_right - lastOdomRight;
  lastOdomLeft = curr_left;
  lastOdomRight = curr_right;

  float d_left = delta_left * METERS_PER_TICK;
  float d_right = delta_right * METERS_PER_TICK;
  float d_center = (d_left + d_right) / 2.0;
  float d_theta = (d_right - d_left) / WHEEL_BASE;

  if (d_center != 0.0) {
    odom_x += d_center * cos(odom_theta + (d_theta / 2.0));
    odom_y += d_center * sin(odom_theta + (d_theta / 2.0));
  }
  odom_theta += d_theta;

  float dt = 1.0 / PID_RATE;
  odom_vx = d_center / dt;
  odom_vth = d_theta / dt;

  if (!moving){
    if (leftPID.PrevInput != 0 || rightPID.PrevInput != 0) resetPID();
    return;
  }

  doPID(&rightPID);
  doPID(&leftPID);

  setMotorSpeeds(leftPID.output, rightPID.output);
}

#endif
