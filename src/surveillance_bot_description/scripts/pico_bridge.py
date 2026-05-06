#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
import serial
from rcl_interfaces.msg import SetParametersResult

class PicoBridge(Node):
    def __init__(self):
        super().__init__('pico_bridge')
        
        # ==========================================
        #        HARDWARE KINEMATICS & TUNING
        # ==========================================
        self.WHEEL_BASE = 0.317    # Meters (distance between wheels)
        
        # Top physical speed for 100% PWM power
        self.MAX_SPEED_MPS = 0.50  
        
        # Minimum PWM (0-255) to overcome motor friction. 
        # Increase this if the motors just hum without spinning.
        self.MIN_POWER = 75        
        
        self.PID_RATE = 30.0       # Hz
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

        # ROS 2 Interfaces
        self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)
        self.imu_pub = self.create_publisher(Imu, '/imu/data_raw', 10)
        
        # Serial Read Loop
        self.create_timer(1.0 / self.PID_RATE, self.serial_loop)
        self.get_logger().info(f"✅ Pico Bridge Started on {self.port_name} (OPEN-LOOP PWM MODE with DEADBAND).")

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
        
        # 1. Calculate target meters per second for each wheel
        v_left = v - (w * self.WHEEL_BASE / 2.0)
        v_right = v + (w * self.WHEEL_BASE / 2.0)

        # 2. Calculate raw proportional PWM (0-255 scale)
        raw_left = (v_left / self.MAX_SPEED_MPS) * 255.0
        raw_right = (v_right / self.MAX_SPEED_MPS) * 255.0

        # 3. Apply Minimum Power Deadband for Left Wheel
        if raw_left > 0.01:
            left_pwm = int(max(self.MIN_POWER, min(raw_left, 255)))
        elif raw_left < -0.01:
            left_pwm = int(min(-self.MIN_POWER, max(raw_left, -255)))
        else:
            left_pwm = 0

        # 4. Apply Minimum Power Deadband for Right Wheel
        if raw_right > 0.01:
            right_pwm = int(max(self.MIN_POWER, min(raw_right, 255)))
        elif raw_right < -0.01:
            right_pwm = int(min(-self.MIN_POWER, max(raw_right, -255)))
        else:
            right_pwm = 0

        # 5. Send raw PWM commands to the Pico
        self.send_command(f"m {left_pwm} {right_pwm}\r")

    def serial_loop(self):
        if not (self.ser and self.ser.is_open):
            return

        # Request data just to keep the Pico's serial buffer from overflowing
        self.send_command("q\r")
        self.send_command("i\r")
        
        for _ in range(2):
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if not line or line == "ERR":
                    continue
                
                parts = line.split()
                # Parse the IMU string if it matches expected length
                if len(parts) == 6:
                    ax, ay, az, gx, gy, gz = map(float, parts)
                    self.publish_imu(ax, ay, az, gx, gy, gz)
            except Exception:
                pass

    def publish_imu(self, ax, ay, az, gx, gy, gz):
        imu_msg = Imu()
        imu_msg.header.stamp = self.get_clock().now().to_msg()
        imu_msg.header.frame_id = 'base_link'
        
        # Convert raw IMU to ROS standard units
        imu_msg.linear_acceleration.x = ax * 9.80665
        imu_msg.linear_acceleration.y = ay * 9.80665
        imu_msg.linear_acceleration.z = az * 9.80665
        
        imu_msg.angular_velocity.x = gx * 0.0174533
        imu_msg.angular_velocity.y = gy * 0.0174533
        imu_msg.angular_velocity.z = gz * 0.0174533
        
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