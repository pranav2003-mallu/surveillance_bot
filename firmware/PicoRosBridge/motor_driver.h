#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

// Left Motors (Front and Rear wired in parallel)
#define LEFT_EN 2   // R_EN and L_EN tied together
#define LEFT_RPWM 3 // R_PWM (Forward)
#define LEFT_LPWM 4 // L_PWM (Reverse)

// Right Motors (Front and Rear wired in parallel)
#define RIGHT_EN 5   // R_EN and L_EN tied together
#define RIGHT_RPWM 6 // R_PWM (Forward)
#define RIGHT_LPWM 9 // L_PWM (Reverse) - Moved to Pin 9 due to dead pin/wire on 7

void initMotorController();
void setMotorSpeed(int i, int spd);
void setMotorSpeeds(int leftSpeed, int rightSpeed);

#endif
