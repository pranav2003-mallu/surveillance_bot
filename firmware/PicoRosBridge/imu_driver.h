#ifndef IMU_DRIVER_H
#define IMU_DRIVER_H

void initIMU();
bool readIMU(float* ax, float* ay, float* az, float* gx, float* gy, float* gz);

#endif
