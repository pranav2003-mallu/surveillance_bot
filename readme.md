# Surveillance Bot ROS 2 Workspace 🤖

This workspace contains the complete ROS 2 software stack for a 4-wheeled, skid-steer surveillance robot. It includes hardware bridging for a Raspberry Pi Pico, RPLidar integration, SLAM (Mapping), and Nav2 (Navigation).

## 🛠️ 1. Workspace Setup & Build

This workspace comes pre-configured. You just need to extract it, build it, and source it!

1. **Extract the Workspace:**
   Extract the provided ZIP file directly into your Home directory (`~`). 

 ## 2.Navigate to the Workspace:
 ***
   cd ~/surveillance_bot
 ***
Build the Packages:
Make sure you have all the necessary ROS 2 dependencies installed, then run:

***
colcon build --symlink-install
***
Source the Workspace:
You must run this command in every new terminal you open, or add it to your .bashrc:

***
source install/setup.bash
***
🔌 2. Hardware Connections & Permissions
Before launching anything, plug in your hardware and grant read/write permissions to the USB ports:

Raspberry Pi Pico (Motor Controller): Plugs into /dev/ttyACM0

RPLidar: Plugs into /dev/ttyUSB0

Run these commands to grant access (you will need to do this every time you reboot, or you can set up udev rules):

***
sudo chmod a+rw /dev/ttyACM0
sudo chmod a+rw /dev/ttyUSB0
***
🗺️ 3. How to Create and Save a Map

To navigate autonomous bots, we first need to drive them around manually to map the area using mapping.launch.py.

Step A: Launch the Mapping Node
Open a terminal, source the workspace, and run:

***
ros2 launch surveillance_bot_description mapping.launch.py
***
*if the teleop keyboard is not launched then,
Step B: Launch the Teleop Keyboard
Open a second terminal, source the workspace, and run:

***
ros2 run teleop_twist_keyboard teleop_twist_keyboard
***
Use the I, J, K, L, , keys to drive the robot around your environment until you have a complete map.

Step C: Save the Map
Once your map looks complete in RViz, open a third terminal, source the workspace, and run the map saver:

***
ros2 run nav2_map_server map_saver_cli -f my_room_map
***
This will generate two files in your current directory: my_room_map.yaml and my_room_map.pgm.
*** 
usually it will be in you home directory...look for them and move them to the maps folder in your package - surveillance_bot_description
***

🧭 4. Autonomous Navigation
Now that you have a map, you can use Nav2 to send the robot to specific locations autonomously using navigation.launch.py.

Open a terminal, source the workspace, and launch the navigation stack while pointing it to the map you just saved:

***
ros2 launch surveillance_bot_description navigation.launch.py map:=/home/$USER/surveillance_bot/src/surveillance_bot_description/maps/my_room_map.yaml
***
👁️ 5. RViz2 Setup Guide
The launch files attempt to open a saved RViz config. If RViz opens but looks empty, click the "Add" button in the bottom left and add the following displays:

For Mapping & General View:
RobotModel: Set the "Description Topic" to /robot_description. This shows your 3D robot.

TF: Check this to see the transform tree (links between wheels, lidar, and base).

LaserScan: Set the "Topic" to /scan_filtered and the "Size" to 0.05m. This shows the red dots from your RPLidar.

Map: Set the "Topic" to /map. This shows the floorplan being generated.

For Navigation (Add these extra displays):
Map (Global Costmap): Add a second Map display and set the topic to /global_costmap/costmap. Change the "Color Scheme" to costmap.

Map (Local Costmap): Add a third Map display and set the topic to /local_costmap/costmap.

Path: Set the topic to /plan. This shows the calculated line the robot intends to follow.

To set a destination:

Click the "2D Pose Estimate" button at the top of RViz and click/drag on the map to tell the robot where it currently is.

Click the "Nav2 Goal" button at the top of RViz and click/drag on the map to tell the robot where to drive!


