# Surveillance Bot - Autonomous Navigation Stack

---

## 🏢 About Humynex Robotics

**Humynex Robotics** is dedicated to pioneering solutions in Robotics, Automation, AI, and Embedded Systems. We specialize in robust, production-ready software architectures designed to solve complex real-world challenges. 

📧 **Contact us:** [humynexrobotics@gmail.com](mailto:humynexrobotics@gmail.com)  
📞 **Phone:** +91 8714358646  
🌐 **Domain:** Robotics • Automation • AI • Embedded Systems • ROS2  

> *We make your ideas into reality.*

---

## 📖 About the Project

This workspace contains the complete production-level ROS 2 (Humble) software stack for a 4-wheeled, skid-steer autonomous surveillance robot. The architecture utilizes a **Raspberry Pi Pico** as a low-level hardware bridge (managing PID motor control, odometry, and relay switches) and an **RPLidar** for high-fidelity environment scanning. 

### ✨ Features
- **LiDAR-based SLAM** (Simultaneous Localization and Mapping)
- **Autonomous Navigation** (Nav2 Stack)
- **Differential Drive Kinematics**
- **Relay Control** for external LED lighting or modular payloads

### 🛠️ Tech Stack
- **Framework:** ROS 2 (Humble)
- **Hardware Layer:** Raspberry Pi Pico (C/C++ via Arduino Framework)
- **High-level Control:** Python 3, C++
- **Sensing:** RPLidar A1/A2, Hall-Effect Encoders
- **Navigation:** Nav2, SLAM Toolbox

### 📦 Included Packages
- `surveillance_bot_description`: Contains the robot's URDF, meshes, launch files, and the Pico python bridge.
- `rplidar_ros`: The official ROS 2 driver package for the RPLidar, responsible for publishing `/scan` data for mapping.

---

## 🚀 Setup Instructions

### 1. Build the Workspace
Make sure you have all the necessary ROS 2 dependencies installed, then run from the workspace root:

```bash
cd ~/surveillance_bot
colcon build --symlink-install
```

### 2. Source the Workspace
You must run this command in every new terminal you open, or add it to your `.bashrc`:

```bash
source install/setup.bash
```

### 3. Grant USB Permissions
Before launching anything, plug in your hardware and grant read/write permissions to the USB ports:

- **Raspberry Pi Pico (Motor Controller):** Plugs into `/dev/ttyACM0`
- **RPLidar:** Plugs into `/dev/ttyUSB0`

Run these commands to grant access (you will need to do this every time you reboot, or you can set up `udev` rules):
```bash
sudo chmod a+rw /dev/ttyACM0
sudo chmod a+rw /dev/ttyUSB0
```

---

## 🗺️ Execution Pipeline

### Step 1: Mapping the Environment (SLAM)

To map a room, the robot uses the LiDAR to scan walls while you manually drive it around.

**1. Launch the Mapping Node:**
Open Terminal 1 and run the SLAM mapping code:
```bash
ros2 launch surveillance_bot_description mapping.launch.py
```

**2. Launch the Teleop Keyboard (To Drive):**
Open Terminal 2 and run the teleoperation node:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
Use `I`, `J`, `K`, `L`, and `,` keys to drive the robot around. You will see a 2D floorplan generating in real-time in RViz2.

**3. Save the Map:**
Once your entire room is mapped, you must save it to a file. 
Open Terminal 3 and run:
```bash
cd ~/surveillance_bot/src/surveillance_bot_description/maps/
ros2 run nav2_map_server map_saver_cli -f my_room_map
```

### Step 2: Autonomous Navigation

Once you have saved your map, you can load it into the Nav2 stack for full autonomous driving.

**1. Launch Navigation and Load the Map:**
Open a terminal, source your workspace, and launch the Navigation script, passing in the exact file path to your saved `.yaml` map file:

```bash
ros2 launch surveillance_bot_description navigation.launch.py map:=/home/mallu/surveillance_bot/src/surveillance_bot_description/maps/my_room_map.yaml
```

**2. Initialize Pose & Set Goal:**
- Click the **"2D Pose Estimate"** button at the top of RViz and drag an arrow to initialize the robot's location.
- Click the **"Nav2 Goal"** button and drag an arrow to your desired destination. The software will calculate a safe path and drive the robot autonomously!

---

## 🔌 Hardware Reference Layout

### 1. Motor Drivers (L298N/MDD20A)
* **Left Front (LF)**   👉 `EN/PWM`: 2 | `IN1`: 3 | `IN2`: 4
* **Left Rear (LR)**    👉 `EN/PWM`: 5 | `IN1`: 6 | `IN2`: 7
* **Right Front (RF)**  👉 `EN/PWM`: 8 | `IN1`: 9 | `IN2`: 10
* **Right Rear (RR)**   👉 `EN/PWM`: 11 | `IN1`: 12 | `IN2`: 13

### 2. Encoders
* **Left Front (LF)**   👉 `A`: 14 | `B`: 15
* **Left Rear (LR)**    👉 `A`: 16 | `B`: 17
* **Right Front (RF)**  👉 `A`: 18 | `B`: 19
* **Right Rear (RR)**   👉 `A`: 20 | `B`: 21

### 3. Relay Module (Lighting / Payloads)
* **Relay Channel 1** 👉 Pin `26` (via `/relay1` ROS topic)
* **Relay Channel 2** 👉 Pin `27` (via `/relay2` ROS topic)
