/* ==========================================
 * Developed by Humynex Robotics
 * We make your ideas into reality
 * ========================================== */
#define USE_BASE

// PID and communications config
#define BAUDRATE 115200 // Faster for ROS 2 Serial
#define MAX_PWM 255
#define PID_RATE 30 // Hz

// Status LEDs
#define ONBOARD_LED LED_BUILTIN
#define EXTRA_LED 28
unsigned long last_blink_time = 0;
bool led_state = false;

// 2-Channel Relay Module Pins
#define RELAY1_PIN 26
#define RELAY2_PIN 27

#include "commands.h"
#include "imu_driver.h"
#include "sensors.h"

// Define core functions before including the implementations
long readEncoder(int i);
void resetEncoder(int i);
void resetEncoders();
void updatePID();
typedef struct SetPointInfo SetPointInfo;
void doPID(SetPointInfo *p);
void initMotorController();
void setMotorSpeed(int i, int spd);
void setMotorSpeeds(int leftSpeed, int rightSpeed);

#ifdef USE_BASE
#include "diff_controller.h"
#include "encoder_driver.h"
#include "motor_driver.h"

const int PID_INTERVAL = 1000 / PID_RATE;
unsigned long lastPID = 0;
#define AUTO_STOP_INTERVAL 2000
long lastMotorCommand = AUTO_STOP_INTERVAL;
#endif

// Serial command parsing vars
int arg = 0;
int index_vars = 0;
char chr;
char cmd;
char argv1[32];
char argv2[32];
long arg1;
long arg2;

void resetCommand() {
  cmd = '\0';
  memset(argv1, 0, sizeof(argv1));
  memset(argv2, 0, sizeof(argv2));
  arg1 = 0;
  arg2 = 0;
  arg = 0;
  index_vars = 0;
}

void runCommand() {
  int i = 0;
  char *p = argv1;
  char *str;
  int pid_args[4];
  arg1 = atoi(argv1);
  arg2 = atoi(argv2);

  switch (cmd) {
  case GET_BAUDRATE:
    Serial.println(BAUDRATE);
    break;
  case ANALOG_READ:
    Serial.println(analogRead(arg1));
    break;
  case DIGITAL_READ:
    Serial.println(digitalRead(arg1));
    break;
  case ANALOG_WRITE:
    analogWrite(arg1, arg2);
    Serial.println("OK");
    break;
  case DIGITAL_WRITE:
    if (arg2 == 0)
      digitalWrite(arg1, LOW);
    else if (arg2 == 1)
      digitalWrite(arg1, HIGH);
    Serial.println("OK");
    break;
  case PIN_MODE:
    if (arg2 == 0)
      pinMode(arg1, INPUT);
    else if (arg2 == 1)
      pinMode(arg1, OUTPUT);
    Serial.println("OK");
    break;
  case PING:
    Serial.println(Ping(arg1));
    break;
  case READ_IMU: {
    float ax, ay, az, gx, gy, gz;
    if (readIMU(&ax, &ay, &az, &gx, &gy, &gz)) {
      Serial.print(ax, 4);
      Serial.print(" ");
      Serial.print(ay, 4);
      Serial.print(" ");
      Serial.print(az, 4);
      Serial.print(" ");
      Serial.print(gx, 4);
      Serial.print(" ");
      Serial.print(gy, 4);
      Serial.print(" ");
      Serial.println(gz, 4);
    } else {
      Serial.println("ERR");
    }
  } break;
#ifdef USE_BASE
  case READ_ENCODERS:
    Serial.print(readEncoder(LEFT));
    Serial.print(" ");
    Serial.println(readEncoder(RIGHT));
    break;
  case RESET_ENCODERS:
    resetEncoders();
    resetPID();
    lastOdomLeft = 0;
    lastOdomRight = 0;
    odom_x = 0;
    odom_y = 0;
    odom_theta = 0;
    Serial.println("OK");
    break;
  case 'q': // READ_ODOM
    Serial.print(odom_x, 4);
    Serial.print(" ");
    Serial.print(odom_y, 4);
    Serial.print(" ");
    Serial.print(odom_theta, 4);
    Serial.print(" ");
    Serial.print(odom_vx, 4);
    Serial.print(" ");
    Serial.println(odom_vth, 4);
    break;
  case MOTOR_SPEEDS:
    lastMotorCommand = millis();
    if (arg1 == 0 && arg2 == 0) {
      setMotorSpeeds(0, 0);
      resetPID();
      moving = 0;
    } else
      moving = 1;
    leftPID.TargetTicksPerFrame = arg1;
    rightPID.TargetTicksPerFrame = arg2;
    Serial.println("OK");
    break;
  case MOTOR_RAW_PWM:
    lastMotorCommand = millis();
    resetPID();
    moving = 0;
    setMotorSpeeds(arg1, arg2);
    Serial.println("OK");
    break;
  case UPDATE_PID: {
    char *saveptr;
    str = strtok_r(argv1, ":", &saveptr);
    while (str != NULL && i < 4) {
      pid_args[i] = atoi(str);
      i++;
      str = strtok_r(NULL, ":", &saveptr);
    }
    Kp = pid_args[0];
    Kd = pid_args[1];
    Ki = pid_args[2];
    Ko = pid_args[3];
    Serial.println("OK");
  } break;
#endif
  default:
    Serial.println("Invalid Command");
    break;
  }
}

void setup() {
  Serial.begin(BAUDRATE);

  // Initialize LED pins
  pinMode(ONBOARD_LED, OUTPUT);
  pinMode(EXTRA_LED, OUTPUT);

  // Initialize Relay pins
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);
  digitalWrite(RELAY1_PIN, LOW); // Start with relays OFF
  digitalWrite(RELAY2_PIN, LOW);

  initIMU();

#ifdef USE_BASE
  initEncoders();
  initMotorController();
  resetPID();
#endif
}

void loop() {
  // Heartbeat LED indication (toggles every 500ms)
  if (millis() - last_blink_time >= 500) {
    led_state = !led_state;
    digitalWrite(ONBOARD_LED, led_state);
    digitalWrite(EXTRA_LED, led_state);
    last_blink_time += 500;
  }

  while (Serial.available() > 0) {
    chr = Serial.read();
    if (chr == 13) {
      if (arg == 1)
        argv1[index_vars] = 0;
      else if (arg == 2)
        argv2[index_vars] = 0;
      runCommand();
      resetCommand();
    } else if (chr == ' ') {
      if (arg == 0)
        arg = 1;
      else if (arg == 1) {
        argv1[index_vars] = 0;
        arg = 2;
        index_vars = 0;
      }
      continue;
    } else {
      if (arg == 0) {
        cmd = chr;
      } else if (arg == 1) {
        if (index_vars < (sizeof(argv1) - 1)) {
          argv1[index_vars] = chr;
          index_vars++;
        }
      } else if (arg == 2) {
        if (index_vars < (sizeof(argv2) - 1)) {
          argv2[index_vars] = chr;
          index_vars++;
        }
      }
    }
  }

#ifdef USE_BASE
  if (millis() - lastPID >= PID_INTERVAL) {
    updatePID();
    lastPID += PID_INTERVAL;
  }

  if ((millis() - lastMotorCommand) > AUTO_STOP_INTERVAL) {
    setMotorSpeeds(0, 0);
    moving = 0;
  }
#endif
}
