#include <Wire.h>

const int MPU_ADDR = 0x68; // I2C address of the MPU-6050

float gyroXoffset = 0, gyroYoffset = 0, gyroZoffset = 0;

void initIMU() {
  Wire1.setSDA(14);
  Wire1.setSCL(15);
  Wire1.begin();

  // Reset the MPU6050
  Wire1.beginTransmission(MPU_ADDR);
  Wire1.write(0x6B); // PWR_MGMT_1 register
  Wire1.write(0x80); // Set reset bit
  Wire1.endTransmission(true);
  delay(100); // Wait for reset

  // Wake up the MPU6050
  Wire1.beginTransmission(MPU_ADDR);
  Wire1.write(0x6B); // PWR_MGMT_1 register
  Wire1.write(0x00); // Clear sleep bit
  Wire1.endTransmission(true);
  delay(100); // Wait for wake up

  // Configure to specific ranges to be absolutely sure
  Wire1.beginTransmission(MPU_ADDR);
  Wire1.write(0x1B); // GYRO_CONFIG
  Wire1.write(0x00); // +/- 250 deg/s
  Wire1.endTransmission(true);

  // Calibrate Gyro on boot (Must keep robot completely still!)
  long gxSum = 0, gySum = 0, gzSum = 0;
  for(int i=0; i<200; i++) {
    Wire1.beginTransmission(MPU_ADDR);
    Wire1.write(0x43);
    Wire1.endTransmission(false);
    Wire1.requestFrom(MPU_ADDR, 6, true);
    gxSum += (int16_t)(Wire1.read() << 8 | Wire1.read());
    gySum += (int16_t)(Wire1.read() << 8 | Wire1.read());
    gzSum += (int16_t)(Wire1.read() << 8 | Wire1.read());
    delay(3);
  }
  gyroXoffset = gxSum / 200.0;
  gyroYoffset = gySum / 200.0;
  gyroZoffset = gzSum / 200.0;
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
  
  *gx = (gyroX - gyroXoffset) / 131.0;
  *gy = (gyroY - gyroYoffset) / 131.0;
  *gz = (gyroZ - gyroZoffset) / 131.0;
  
  return true;
}
