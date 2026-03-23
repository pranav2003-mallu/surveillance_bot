# Surveillance Bot ROS 2 Workspace 🤖

## 📖 About
This workspace contains the complete ROS 2 (Humble) software stack for a 4-wheeled, skid-steer autonomous surveillance robot. The robot utilizes a **Raspberry Pi Pico** as a low-level hardware bridge (managing PID motor control, odometry, and relay switches) and an **RPLidar** for high-level environment scanning. 

Features include:
- **LiDAR-based SLAM** (Simultaneous Localization and Mapping)
- **Autonomous Navigation** (Nav2 Stack)
- **Differential Drive Kinematics**
- **Relay Control** for external LED lighting or payloads

### Included Packages
- `surveillance_bot_description`: Contains the robot's URDF, meshes, launch files, and the Pico python bridge.
- `rplidar_ros`: The official ROS 2 driver package for the RPLidar. Responsible for publishing `/scan` data for mapping.

---

## 🔌 Hardware Connections (Raspberry Pi Pico)

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

### 3. Relay Module (For LED Headlights / Payloads)
* **Relay Channel 1** 👉 Pin `26` (Controlled via `/relay1` ROS topic)
* **Relay Channel 2** 👉 Pin `27` (Controlled via `/relay2` ROS topic)

---

## 🛠️ Workspace Setup & Build

This workspace comes pre-configured. You just need to extract it, build it, and source it!

### 1. Build the Packages:
Make sure you have all the necessary ROS 2 dependencies installed, then run from the workspace root:

```bash
cd ~/surveillance_bot
colcon build --symlink-install
```

### 2. Source the Workspace:
You must run this command in every new terminal you open, or add it to your `.bashrc`:

```bash
source install/setup.bash
```

---

## 🔋 USB Permissions & LiDAR
Before launching anything, plug in your hardware and grant read/write permissions to the USB ports:

- **Raspberry Pi Pico (Motor Controller):** Plugs into `/dev/ttyACM0`
- **RPLidar:** Plugs into `/dev/ttyUSB0`

Run these commands to grant access (you will need to do this every time you reboot, or you can set up `udev` rules):
```bash
sudo chmod a+rw /dev/ttyACM0
sudo chmod a+rw /dev/ttyUSB0
```

---

## 🗺️ How to Create and Save a Map

To navigate autonomously, we first need to drive the bot around manually to map the area.

1. **Launch the Mapping Node:**
   ```bash
   ros2 launch surveillance_bot_description mapping.launch.py
   ```
   *(This script automatically launches the `rplidar_ros` node to begin scanning the room).*

2. **Launch the Teleop Keyboard:**
   In a second terminal:
   ```bash
   ros2 run teleop_twist_keyboard teleop_twist_keyboard
   ```
   Use the `I`, `J`, `K`, `L`, `,` keys to drive the robot around your environment until you have a complete map shown in RViz.

3. **Save the Map:**
   Once your map looks complete, open a third terminal and run the map saver:
   ```bash
   ros2 run nav2_map_server map_saver_cli -f my_room_map
   ```
   This generates `my_room_map.yaml` and `my_room_map.pgm`. Move these files into your `maps` folder inside the `surveillance_bot_description` package!

---

## 🧭 Autonomous Navigation
Now that you have a map, you can use Nav2 to send the robot to specific locations autonomously.

Launch the navigation stack while pointing it to the map you just saved:
```bash
ros2 launch surveillance_bot_description navigation.launch.py map:=/home/$USER/surveillance_bot/src/surveillance_bot_description/maps/my_room_map.yaml
```

**Using RViz to drive:**
1. Click the **"2D Pose Estimate"** button at the top of RViz and click/drag on the map to tell the robot where it currently is.
2. Click the **"Nav2 Goal"** button and click/drag on the map to tell the robot exactly where to drive autonomously!
