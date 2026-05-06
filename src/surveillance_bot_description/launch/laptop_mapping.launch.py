import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_share = get_package_share_directory('surveillance_bot_description')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'rviz.rviz')
    xacro_file = os.path.join(pkg_share, 'urdf', 'surveillance_bot.xacro')

    robot_desc = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    return LaunchDescription([
        # Publish fixed joint TFs locally (base_link→lidar_1 etc.)
        # Without this, RViz can't render the robot model or place the scan.
        # Dynamic TFs (odom→base_footprint) still come from the Pi over the network.
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_link']
        ),

        # RViz only — SLAM + all hardware runs on the Pi via mapping.launch.py
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_path]
        )
    ])
