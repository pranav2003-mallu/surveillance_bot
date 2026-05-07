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
        
        self.MAX_SPEED_MPS = 1.2  
        
        # Split Power Profiles: Overcome skid-steer friction!
        self.MIN_POWER_LINEAR = 90   # Power just to roll forward
        self.MIN_POWER_TURN = 150    # EXTRA POWER to force the wheels to scrub and turn

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
        self.get_logger().info(f"✅ Pico Bridge Started (SPLIT POWER TURN MODE).")

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'port_name':
                self.port_name = param.value
                if self.ser and self.ser.is_open:
                    self.ser.close()
                self.connect_serial()
        return SetParametersResult(successful=True)

    def connect_serial(self):
        try:
            self.ser = serial.Serial(self.port_name, self.baud_rate, timeout=0.1)
        except Exception:
            pass

    def send_command(self, cmd_str):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(cmd_str.encode('utf-8'))
            except Exception:
                pass

    def cmd_cb(self, msg):
        v = msg.linear.x
        w = msg.angular.z
        
        # Prevent micro-oscillations on straight paths
        if abs(v) > 0.05 and abs(w) < 0.05:
            w = 0.0

        # Match the MPPI predictive model
        v_left = v - (w * self.WHEEL_BASE / 2.0)
        v_right = v + (w * self.WHEEL_BASE / 2.0)

        # Calculate fraction of max speed
        frac_left = v_left / self.MAX_SPEED_MPS
        frac_right = v_right / self.MAX_SPEED_MPS

        # Detect if the controller is asking for a turn
        is_turning = abs(w) > 0.1

        def compute_pwm(frac):
            # Apply the higher minimum power if we are turning
            base_power = self.MIN_POWER_TURN if is_turning else self.MIN_POWER_LINEAR
            
            if frac > 0.01:
                return int(base_power + min(frac, 1.0) * (255 - base_power))
            elif frac < -0.01:
                return int(-base_power + max(frac, -1.0) * (255 - base_power))
            else:
                return 0

        left_pwm = compute_pwm(frac_left)
        right_pwm = compute_pwm(frac_right)

        # Send raw PWM commands to the Pico
        self.send_command(f"m {left_pwm} {right_pwm}\r")

    def serial_loop(self):
        if not (self.ser and self.ser.is_open):
            return
            
        self.send_command("q\r")
        self.send_command("i\r")
        
        # Read available lines without blocking the ROS executor
        while self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if not line or line == "ERR":
                    continue
                parts = line.split()
                if len(parts) == 6:
                    ax, ay, az, gx, gy, gz = map(float, parts)
                    self.publish_imu(ax, ay, az, gx, gy, gz)
            except Exception:
                pass

    def publish_imu(self, ax, ay, az, gx, gy, gz):
        imu_msg = Imu()
        imu_msg.header.stamp = self.get_clock().now().to_msg()
        imu_msg.header.frame_id = 'base_link'
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