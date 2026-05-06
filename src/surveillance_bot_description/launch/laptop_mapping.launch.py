import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('surveillance_bot_description')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'rviz.rviz')

    return LaunchDescription([
        # RViz only — SLAM, TF, and all hardware nodes run on the Pi via mapping.launch.py.
        # We removed robot_state_publisher and static_transform_publisher here
        # to prevent network TF conflicts with the Raspberry Pi.
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_path]
        )
    ])