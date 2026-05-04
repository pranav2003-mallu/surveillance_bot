# PicoRosBridge for Skid-Steer Mobile Robot

This firmware is a complete adaptation of the ROS Arduino Bridge for the Raspberry Pi Pico, specially modified for a 4-wheel skid-steer robot using two BTS7960 motor drivers (with motors wired in parallel).

## Hardware Configuration
This code handles:
* **4 x L-shape Waveshare 12V gear motors**
* **2 x BTS7960 motor drivers** (Motors wired in parallel per side)
* **2 rear wheel encoders**
* **Communication via Serial over USB** to ROS 2 Humble.

### Pi Pico Pin Mapping

#### Motors (BTS7960 x 2)
The Pico controls the left and right sides independently. You will connect both left motors to the Left Driver, and both right motors to the Right Driver.

**Left-Side BTS7960 (Controls LF & LR Motors):**
- `EN` (R_EN/L_EN): Pin 2
- `RPWM` (Forward): Pin 3
- `LPWM` (Reverse): Pin 4

**Right-Side BTS7960 (Controls RF & RR Motors):**
- `EN` (R_EN/L_EN): Pin 5
- `RPWM` (Forward): Pin 6
- `LPWM` (Reverse): Pin 7

#### Encoders
Encoders use hardware interrupts for high-speed tracking.
- **Left Rear Encoder**
  - Channel A: Pin 2
  - Channel B: Pin 3
- **Right Rear Encoder**
  - Channel A: Pin 4
  - Channel B: Pin 5
  *(Note: The firmware automatically handles the inverted counting on the right side based on your requirement)*.

## ROS 2 Integration Parameters
You provided specific hardware values:
* Left rear count: **~ 562**
* Right rear count: **~ -560** (Inverted; handled automatically by firmware now)
* Wheel diameter: **130 mm (0.13 meters)**
* Track width (Distance between wheels): **24.5 cm (0.245 meters)**

In your ROS 2 bridge Python parameter file (usually `my_robot_params.yaml`), make sure to configure these settings:

```yaml
base_controller:
  ros__parameters:
    # 24.5 cm track width
    base_width: 0.245
    # Ticks per meter = encoder ticks per rev / (pi * wheel diameter)
    # Using 562 ticks per revolution: 562 / (3.14159 * 0.13) = ~1376.1
    ticks_meter: 1376 
    
    # Optional PID Tuning
    Kp: 20
    Kd: 12
    Ki: 0
    Ko: 50
```

## How to Flash in Arduino IDE
1. Open the Arduino IDE.
2. Ensure you have installed the **rp2040 (Raspberry Pi Pico)** board support in the Boards Manager.
3. Open `PicoRosBridge.ino`
4. Select board: `Raspberry Pi Pico`
5. Compile and Upload to the Pico.

The Pico will now act as the `ros_arduino_bridge` brain, receiving velocity commands from ROS 2 and publishing accurate odometry back!
