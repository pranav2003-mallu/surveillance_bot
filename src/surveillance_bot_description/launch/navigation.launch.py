import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch.conditions import IfCondition
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_share = get_package_share_directory('surveillance_bot_description')
    rplidar_pkg = get_package_share_directory('rplidar_ros')
    nav2_launch_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')

    # Arguments
    map_yaml = LaunchConfiguration('map')  
    lidar_port = LaunchConfiguration('lidar_port')
    pico_port = LaunchConfiguration('pico_port')
    use_rviz = LaunchConfiguration('use_rviz')

    xacro_file = os.path.join(pkg_share, 'urdf', 'surveillance_bot.xacro')
    nav2_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'rviz.rviz')

    # The Jazzy Fix: Strict string typing for the URDF
    robot_desc = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('map', description='Full path to map yaml file to load'),
        DeclareLaunchArgument('lidar_port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('pico_port', default_value='/dev/ttyACM0'),
        DeclareLaunchArgument('use_rviz', default_value='True', description='Launch RViz?'),

        # 1. Robot State, Joints, & Transforms
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_link']
        ),

        # 2. Hardware Bridge (Pico)
        Node(
            package='surveillance_bot_description',
            executable='pico_bridge.py',
            parameters=[{'port_name': pico_port}]
        ),

        # 3. RPLidar
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(rplidar_pkg, 'launch', 'rplidar_a1_launch.py')),
            launch_arguments={'serial_port': lidar_port, 'frame_id': 'lidar_1'}.items()
        ),

        # 3.5 IMU Filter (Calculates 3D orientation from raw MPU6050 data)
        Node(
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            name='imu_filter',
            parameters=[
                {'use_mag': False},
                {'publish_tf': False},
                {'world_frame': 'enu'}
            ]
        ),

        # 4. Scan Filter (180 Crop)
        Node(
            package='surveillance_bot_description',
            executable='scan_filter.py',
            name='scan_filter'
        ),

        # 5. Nav2 Bringup
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'bringup_launch.py')),
            launch_arguments={
                'map': map_yaml,
                'use_sim_time': 'False',
                'params_file': nav2_params,
                'autostart': 'True'
            }.items()
        ),

        # 6. RViz2 (GUI Controllable)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_path],
            condition=IfCondition(use_rviz)
        )
    ])
