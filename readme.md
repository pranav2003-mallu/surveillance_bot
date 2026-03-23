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

## 🗺️ Step 1: Mapping the Environment (SLAM)

To map a room, the robot uses the LiDAR to scan walls while you manually drive it around.

**1. Launch the Mapping Node:**
Open Terminal 1 and run the SLAM mapping code:
```bash
ros2 launch surveillance_bot_description mapping.launch.py
```
*(This automatically launches the RPLidar, RViz2, and the `slam_toolbox` mapping node).*

**2. Launch the Teleop Keyboard (To Drive):**
Open Terminal 2 and run the teleoperation node:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
Use `I`, `J`, `K`, `L`, and `,` keys to drive the robot around. As you drive, look at your RViz window. You will see a 2D floorplan generating in real-time as the LiDAR discovers new walls.

**3. Save the Map:**
Once your entire room is mapped and the walls are fully defined in RViz, you must save it to a file. 
Open Terminal 3 and run:
```bash
cd ~/surveillance_bot/src/surveillance_bot_description/maps/
ros2 run nav2_map_server map_saver_cli -f my_room_map
```
This generates two files: 
- `my_room_map.yaml` (The config file)
- `my_room_map.pgm` (The image footprint of the map)

---

## 🧭 Step 2: Loading the Map & Autonomous Navigation

Once you have saved your map, you can load it into the Nav2 stack to unleash autonomous driving!

**1. Launch Navigation and Load the Map:**
Open a terminal, source your workspace, and launch the Navigation script, passing in the exact file path to your saved `.yaml` map file:

```bash
ros2 launch surveillance_bot_description navigation.launch.py map:=/home/mallu/surveillance_bot/src/surveillance_bot_description/maps/my_room_map.yaml
```

**2. Tell the Robot Where It Is (2D Pose Estimate):**
When RViz opens, the robot doesn't know where it started on your map!
- Click the **"2D Pose Estimate"** button at the top of RViz.
- Click and drag an arrow on your map to place the 3D robot exactly where your physical robot is currently sitting, pointing in the same direction.

**3. Start Autonomous Driving (Nav2 Goal):**
Now it's time to set a waypoint!
- Click the **"Nav2 Goal"** button at the top of RViz.
- Click and drag a destination arrow anywhere on the map.
- The software will calculate a safe path (avoiding obstacles) and smoothly drive the robot to that spot!
