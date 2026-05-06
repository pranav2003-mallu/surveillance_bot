import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('surveillance_bot_description')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'rviz.rviz')

    return LaunchDescription([
        # RViz only — SLAM + all hardware runs on the Pi via mapping.launch.py
        # This avoids all Pi↔Laptop clock skew issues.
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_path]
        )
    ])
