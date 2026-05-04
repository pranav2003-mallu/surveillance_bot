#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
import serial
import math
from tf2_ros import TransformBroadcaster
from rcl_interfaces.msg import SetParametersResult

class PicoBridge(Node):
    def __init__(self):
        super().__init__('pico_bridge')
        
        # ==========================================
        #        HARDWARE TUNING THRESHOLDS 
        # ==========================================
        # Extracted directly from surveillance_bot.xacro
        self.WHEEL_RADIUS = 0.065  # Meters (Z-offset of wheel joints)
        self.WHEEL_BASE = 0.317    # Meters (Distance between left and right wheels)
        self.TICKS_PER_REV = 330.0 # Encoder ticks per revolution (Adjust if needed)
        self.PID_RATE = 30.0       # Hz (Must match Pico firmware)
        
        self.KP = 10
        self.KD = 5
        self.KI = 0
        self.KO = 50
        # ==========================================

        # GUI-Editable Parameters
        self.declare_parameter('port_name', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)
        self.port_name = self.get_parameter('port_name').value
        self.baud_rate = self.get_parameter('baud_rate').value

        # Listen for GUI Parameter Changes
        self.add_on_set_parameters_callback(self.parameter_callback)

        self.ser = None
        self.connect_serial()
        self.send_command(f"u {self.KP}:{self.KD}:{self.KI}:{self.KO}\r")

        # ROS 2 Interfaces
        self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.imu_pub = self.create_publisher(Imu, '/imu/data_raw', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Odometry Request Loop
        self.create_timer(1.0 / self.PID_RATE, self.odom_loop)
        self.get_logger().info(f"✅ Pico Bridge Started on {self.port_name} with URDF tuned dimensions.")

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'port_name':
                self.get_logger().info(f"🔄 GUI changed port to: {param.value}")
                self.port_name = param.value
                if self.ser and self.ser.is_open:
                    self.ser.close()
                self.connect_serial()
        return SetParametersResult(successful=True)

    def connect_serial(self):
        try:
            self.ser = serial.Serial(self.port_name, self.baud_rate, timeout=0.1)
            self.get_logger().info(f"🔌 Serial Connected: {self.port_name}")
        except Exception as e:
            self.get_logger().error(f"❌ Serial Failure: {e}")

    def send_command(self, cmd_str):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(cmd_str.encode('utf-8'))
            except Exception:
                pass

    def cmd_cb(self, msg):
        v = msg.linear.x
        w = msg.angular.z
        
        v_left = v - (w * self.WHEEL_BASE / 2.0)
        v_right = v + (w * self.WHEEL_BASE / 2.0)

        meters_per_tick = (2.0 * math.pi * self.WHEEL_RADIUS) / self.TICKS_PER_REV
        
        left_ticks_per_sec = v_left / meters_per_tick
        right_ticks_per_sec = v_right / meters_per_tick

        left_ticks_per_frame = round(left_ticks_per_sec / self.PID_RATE)
        right_ticks_per_frame = round(right_ticks_per_sec / self.PID_RATE)

        # Send 'm' command (MOTOR_SPEEDS)
        self.send_command(f"m {left_ticks_per_frame} {right_ticks_per_frame}\r")

    def odom_loop(self):
        if not (self.ser and self.ser.is_open):
            return

        # Request both Odom and IMU
        self.send_command("q\r")
        self.send_command("i\r")
        
        # Read the next two responses regardless of order
        for _ in range(2):
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if not line or line == "ERR":
                    continue
                
                parts = line.split()
                if len(parts) == 5:
                    x = float(parts[0])
                    y = float(parts[1])
                    th = float(parts[2])
                    v_x = float(parts[3])
                    v_th = float(parts[4])
                    self.publish_odometry(x, y, th, v_x, v_th)
                elif len(parts) == 6:
                    ax = float(parts[0])
                    ay = float(parts[1])
                    az = float(parts[2])
                    gx = float(parts[3])
                    gy = float(parts[4])
                    gz = float(parts[5])
                    self.publish_imu(ax, ay, az, gx, gy, gz)
            except Exception:
                pass

    def publish_odometry(self, x, y, th, v_x, v_th):
        current_time = self.get_clock().now()
        
        q_z = math.sin(th / 2.0)
        q_w = math.cos(th / 2.0)

        # TF Broadcast (odom -> base_footprint)
        t = TransformStamped()
        t.header.stamp = current_time.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = x
        t.transform.translation.y = y
        t.transform.rotation.z = q_z
        t.transform.rotation.w = q_w
        self.tf_broadcaster.sendTransform(t)

        # Odometry Message
        odom = Odometry()
        odom.header.stamp = current_time.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_footprint'
        odom.pose.pose.position.x = x
        odom.pose.pose.position.y = y
        odom.pose.pose.orientation.z = q_z
        odom.pose.pose.orientation.w = q_w
        odom.twist.twist.linear.x = v_x
        odom.twist.twist.angular.z = v_th
        self.odom_pub.publish(odom)

    def publish_imu(self, ax, ay, az, gx, gy, gz):
        imu_msg = Imu()
        imu_msg.header.stamp = self.get_clock().now().to_msg()
        imu_msg.header.frame_id = 'base_link'
        
        # MPU6050 Acceleration is in G's. Convert to m/s^2
        imu_msg.linear_acceleration.x = ax * 9.80665
        imu_msg.linear_acceleration.y = ay * 9.80665
        imu_msg.linear_acceleration.z = az * 9.80665
        
        # Gyro is in deg/sec. Convert to rad/sec
        imu_msg.angular_velocity.x = gx * 0.0174533
        imu_msg.angular_velocity.y = gy * 0.0174533
        imu_msg.angular_velocity.z = gz * 0.0174533
        
        # Orientation not provided directly by MPU6050 (unless DMP is used)
        imu_msg.orientation_covariance[0] = -1.0 
        
        self.imu_pub.publish(imu_msg)

def main():
    rclpy.init()
    node = PicoBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
