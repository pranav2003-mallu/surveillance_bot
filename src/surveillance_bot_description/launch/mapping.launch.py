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
    slam_pkg = get_package_share_directory('slam_toolbox')

    # Arguments
    lidar_port = LaunchConfiguration('lidar_port')
    pico_port = LaunchConfiguration('pico_port')
    use_rviz = LaunchConfiguration('use_rviz')

    xacro_file = os.path.join(pkg_share, 'urdf', 'surveillance_bot.xacro')
    slam_params = os.path.join(pkg_share, 'config', 'mapper_params_online_async.yaml')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'rviz.rviz')

    # Strict string typing for the URDF
    robot_desc = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('lidar_port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('pico_port', default_value='/dev/ttyACM0'),
        DeclareLaunchArgument('use_rviz', default_value='False', description='Launch RViz? (Keep False on Pi)'),

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

        # 2. Hardware Bridge (Pico - Open Loop PWM)
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

        # 4. Laser Odometry (CRITICAL: Replaces wheel encoders, listens to raw /scan)
        Node(
            package='rf2o_laser_odometry',
            executable='rf2o_laser_odometry_node',
            name='rf2o_laser_odometry',
            output='screen',
            parameters=[{
                'laser_scan_topic': '/scan',  
                'odom_topic': '/odom',
                'publish_tf': True,
                'base_frame_id': 'base_footprint',
                'odom_frame_id': 'odom',
                'init_pose_from_topic': '',
                'freq': 10.0
            }]
        ),

        # 5. Scan Filter (Provides /scan_filtered for Costmaps)
        Node(
            package='surveillance_bot_description',
            executable='scan_filter.py',
            name='scan_filter'
        ),

        # 6. SLAM Toolbox
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(slam_pkg, 'launch', 'online_async_launch.py')),
            launch_arguments={'slam_params_file': slam_params, 'use_sim_time': 'False'}.items()
        ),
        
        # 7. RViz2 (GUI Controllable - Do not run on Pi)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_path],
            condition=IfCondition(use_rviz)
        )
    ])