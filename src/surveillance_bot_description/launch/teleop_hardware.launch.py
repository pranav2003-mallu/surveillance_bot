import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_share = get_package_share_directory('surveillance_bot_description')
    pico_port = LaunchConfiguration('pico_port')

    xacro_file = os.path.join(pkg_share, 'urdf', 'surveillance_bot.xacro')
    rviz_config = os.path.join(pkg_share, 'rviz', 'rviz.rviz')

    # Strict string typing for Jazzy URDF
    robot_desc = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('pico_port', default_value='/dev/ttyACM0', description='Pico Serial Port'),

        # 1. Robot State Publisher (Automatically handles base_footprint -> base_link)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}],
            output='screen'
        ),

        # 2. Joint State Publisher (Publishes the continuous wheel joints)
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            parameters=[{'robot_description': robot_desc}],
            output='screen'
        ),

        # 3. REAL HARDWARE BRIDGE (Replaces fake_odom)
        Node(
            package='surveillance_bot_description',
            executable='pico_bridge.py',
            parameters=[{'port_name': pico_port}],
            output='screen'
        ),

        # 4. Teleop Keyboard (Opens in a new terminal window)
        Node(
            package='teleop_twist_keyboard',
            executable='teleop_twist_keyboard',
            prefix='xterm -e',
            output='screen'
        ),

        # 5. RViz2 (For visualizing the physical movement)
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        ),
    ])
