#ifndef ENCODER_DRIVER_H
#define ENCODER_DRIVER_H
// Front encoders are removed (Pins 14/15 used by IMU I2C)

#define LR_ENC_PIN_A 16
#define LR_ENC_PIN_B 17

#define RR_ENC_PIN_A 20
#define RR_ENC_PIN_B 21

long readEncoder(int i);
void resetEncoder(int i);
void resetEncoders();
void initEncoders();

#endif
