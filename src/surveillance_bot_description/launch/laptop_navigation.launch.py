import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_share = get_package_share_directory('surveillance_bot_description')
    nav2_launch_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')

    # Default to the map you just saved!
    default_map_path = os.path.join(pkg_share, 'maps', 'my_first_map.yaml')
    map_yaml = LaunchConfiguration('map')  

    nav2_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'rviz.rviz')

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map_path, description='Full path to map yaml file to load'),

        # Nav2 Bringup
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'bringup_launch.py')),
            launch_arguments={
                'map': map_yaml,
                'use_sim_time': 'False',
                'params_file': nav2_params,
                'autostart': 'True'
            }.items()
        ),

        # RViz2 (GUI Controllable)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_path]
        )
    ])