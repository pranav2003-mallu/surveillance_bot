# 🤖 Surveillance Bot (Description Package)

This package contains the core ROS 2 (Humble) configuration, launch files, 3D models (URDF), and maps for the autonomous 4-wheeled skid-steer surveillance robot. 

This guide covers everything from hardware setup to fully autonomous navigation using Nav2 and SLAM.

---

## 🛠️ 1. Hardware Connections & Permissions

Before launching anything, plug in your hardware and grant read/write permissions to the USB ports.

- **Raspberry Pi Pico (Motor Controller):** Plugs into `/dev/ttyACM0`
- **RPLidar:** Plugs into `/dev/ttyUSB0`

Run these commands to grant serial access:
```bash
sudo chmod a+rw /dev/ttyACM0
sudo chmod a+rw /dev/ttyUSB0
```
*(Tip: You can set up `udev` rules so you don't have to do this every time you reboot!)*

---

## 🏗️ 2. How to Build the Workspace

If you just cloned or extracted the project, you need to build it first.

1. **Navigate to your workspace root:**
   ```bash
   cd ~/surveillance_bot
   ```
2. **Build the packages:**
   ```bash
   colcon build --symlink-install
   ```
3. **Source the workspace:**
   *(You must run this in every new terminal you open!)*
   ```bash
   source install/setup.bash
   ```

---

## 🗺️ 3. How to Create a New Map (SLAM)

To navigate autonomously, the robot first needs to drive around and scan the room to create a 2D map.

### Step A: Launch Mapping Node
Open a terminal, source the workspace, and run:
```bash
ros2 launch surveillance_bot_description mapping.launch.py
```
*This will start the Lidar, the robot's base model, robot state publisher, RViz, and the SLAM toolbox.*

### Step B: Launch Telekeyboard to Drive
Open a **second terminal**, source the workspace, and run the teleop node:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
Use the `I`, `J`, `K`, `L`, and `,` keys to drive the robot around your environment. Drive slowly and ensure all walls and obstacles are scanned. You will see the map generating dynamically in RViz!

---

## 💾 4. Saving the Map

Once your map looks complete and enclosed in RViz, you need to save it.
Open a **third terminal**, source the workspace, and navigate to the maps folder in this package:

```bash
cd ~/surveillance_bot/src/surveillance_bot_description/maps/
```
Run the map saver command:
```bash
ros2 run nav2_map_server map_saver_cli -f my_room_map
```
This will generate two files in the `maps/` directory: 
- `my_room_map.yaml` (Metadata)
- `my_room_map.pgm` (The image file of the map)

---

## 🧭 5. Autonomous Navigation (Nav2)

Now that you have your saved map, you can use ROS 2 Nav2 to make the robot drive autonomously!

1. Open a terminal and source your workspace.
2. Launch the navigation stack, providing the exact path to your newly saved map:

```bash
ros2 launch surveillance_bot_description navigation.launch.py map:=/home/$USER/surveillance_bot/src/surveillance_bot_description/maps/my_room_map.yaml
```

### How to command the robot in RViz:
When RViz opens:
1. **Set Initial Pose:** Click the **"2D Pose Estimate"** button at the top of RViz. Click and drag on the map exactly where the physical robot is currently located and facing.
2. **Set a Destination:** Click the **"Nav2 Goal"** button at the top. Click and drag on the map where you want the robot to go. It will calculate a path and drive there completely autonomously!

---

## 👁️ 6. RViz2 Display Troubleshooting

If your RViz opens but looks blank, ensure you have added the correct displays by clicking "Add" in the bottom left corner:

- **RobotModel:** Set "Description Topic" to `/robot_description`.
- **TF:** Check this to view the transform tree (links between base and lidar).
- **LaserScan:** Set "Topic" to `/scan_filtered` and "Size" to `0.05m`.
- **Map:** Set "Topic" to `/map`.

**For Navigation**, add these additional Map Displays:
- **Global Costmap:** Add a Map display, set topic to `/global_costmap/costmap`, change "Color Scheme" to `costmap`.
- **Local Costmap:** Add a Map display, set topic to `/local_costmap/costmap`, change "Color Scheme" to `costmap`.
- **Path:** Set topic to `/plan` to see the line the robot intends to follow.
