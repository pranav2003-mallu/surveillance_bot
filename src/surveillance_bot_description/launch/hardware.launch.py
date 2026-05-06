import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_share = get_package_share_directory('surveillance_bot_description')
    rplidar_pkg = get_package_share_directory('rplidar_ros')

    lidar_port = LaunchConfiguration('lidar_port')
    pico_port = LaunchConfiguration('pico_port')

    xacro_file = os.path.join(pkg_share, 'urdf', 'surveillance_bot.xacro')
    ekf_config_path = os.path.join(pkg_share, 'config', 'ekf.yaml')

    robot_desc = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('lidar_port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('pico_port', default_value='/dev/ttyACM0'),

        Node(package='robot_state_publisher', executable='robot_state_publisher', parameters=[{'robot_description': robot_desc}]),
        Node(package='joint_state_publisher', executable='joint_state_publisher', name='joint_state_publisher', parameters=[{'robot_description': robot_desc}]),
        Node(package='tf2_ros', executable='static_transform_publisher', arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_link']),

        # Hardware Bridge (Pico)
        Node(package='surveillance_bot_description', executable='pico_bridge.py', parameters=[{'port_name': pico_port, 'publish_tf': False}]),

        # RPLidar
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(rplidar_pkg, 'launch', 'rplidar_a1_launch.py')),
            launch_arguments={'serial_port': lidar_port, 'frame_id': 'lidar_1'}.items()
        ),

        # IMU Filter - DISABLED (IMU drift causes phantom motion when static)
        # Node(
        #     package='imu_filter_madgwick',
        #     executable='imu_filter_madgwick_node',
        #     name='imu_filter',
        #     parameters=[{'use_mag': False}, {'publish_tf': False}, {'world_frame': 'enu'}]
        # ),

        # Scan Filter
        Node(package='surveillance_bot_description', executable='scan_filter.py', name='scan_filter'),

        # EKF Sensor Fusion - DISABLED (IMU drift causing issues, using odom-only)
        # Node(
        #     package='robot_localization',
        #     executable='ekf_node',
        #     name='ekf_filter_node',
        #     output='screen',
        #     parameters=[ekf_config_path]
        # ),
    ])
