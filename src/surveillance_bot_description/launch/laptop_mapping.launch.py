import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_share = get_package_share_directory('surveillance_bot_description')
    slam_pkg = get_package_share_directory('slam_toolbox')

    slam_params = os.path.join(pkg_share, 'config', 'mapper_params_online_async.yaml')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'rviz.rviz')
    xacro_file = os.path.join(pkg_share, 'urdf', 'surveillance_bot.xacro')

    robot_desc = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    return LaunchDescription([
        # Run robot_state_publisher locally so fixed TFs (base_link→lidar_1)
        # are always in the laptop's TF cache — no network dependency.
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),

        # Static TF: base_footprint → base_link (fixed, can run locally)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_link']
        ),

        # SLAM Toolbox
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(slam_pkg, 'launch', 'online_async_launch.py')),
            launch_arguments={'slam_params_file': slam_params, 'use_sim_time': 'False'}.items()
        ),

        # RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_path]
        )
    ])
