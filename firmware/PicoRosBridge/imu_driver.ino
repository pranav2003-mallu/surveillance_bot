#include <Wire.h>

const int MPU_ADDR = 0x68; // I2C address of the MPU-6050

void initIMU() {
  Wire1.setSDA(14);
  Wire1.setSCL(15);
  Wire1.begin();
  Wire1.beginTransmission(MPU_ADDR);
  Wire1.write(0x6B); // PWR_MGMT_1 register
  Wire1.write(0);    // Set to zero (wakes up the MPU-6050)
  Wire1.endTransmission(true);
}

bool readIMU(float* ax, float* ay, float* az, float* gx, float* gy, float* gz) {
  Wire1.beginTransmission(MPU_ADDR);
  Wire1.write(0x3B); // Starting with register 0x3B (ACCEL_XOUT_H)
  if (Wire1.endTransmission(false) != 0) {
    return false; // I2C error
  }
  
  Wire1.requestFrom(MPU_ADDR, 14, true); // Request a total of 14 registers
  if (Wire1.available() < 14) return false;
  
  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)    
  int16_t accelX = Wire1.read() << 8 | Wire1.read(); 
  int16_t accelY = Wire1.read() << 8 | Wire1.read(); 
  int16_t accelZ = Wire1.read() << 8 | Wire1.read(); 
  
  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  int16_t temp = Wire1.read() << 8 | Wire1.read(); 
  
  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  int16_t gyroX = Wire1.read() << 8 | Wire1.read(); 
  int16_t gyroY = Wire1.read() << 8 | Wire1.read(); 
  int16_t gyroZ = Wire1.read() << 8 | Wire1.read(); 
  
  // Convert to g and degrees/sec
  // Assuming default scale ranges: +/- 2g and +/- 250 deg/s
  *ax = accelX / 16384.0;
  *ay = accelY / 16384.0;
  *az = accelZ / 16384.0;
  
  *gx = gyroX / 131.0;
  *gy = gyroY / 131.0;
  *gz = gyroZ / 131.0;
  
  return true;
}
