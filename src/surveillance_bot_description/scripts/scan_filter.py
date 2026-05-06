#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class ScanFilter(Node):
    def __init__(self):
        super().__init__('scan_filter')
        
        # Input QoS: keep enough history to not drop lidar packets
        sub_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        # Output QoS: depth=1 — always deliver the LATEST scan, drop stale ones
        # This prevents the RViz/SLAM message queue from filling up over WiFi
        pub_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Input: Listen to the raw scan
        self.create_subscription(LaserScan, '/scan', self.scan_cb, sub_qos)
        
        # Output: Publish the filtered scan
        self.pub = self.create_publisher(LaserScan, '/scan_filtered', pub_qos)
        
        self.get_logger().info("✅ Scan Filter Active: /scan -> /scan_filtered (Reliability: BEST_EFFORT)")

    def scan_cb(self, msg):
        # Keep frame consistent
        msg.header.frame_id = "lidar_1"
        
        # YOUR LOGIC (From your working mapping file)
        # You stated this worked perfectly, so we keep it exactly as is.
        new_ranges = list(msg.ranges)
        for i in range(len(new_ranges)):
            angle = msg.angle_min + (i * msg.angle_increment)
            
            # Lidar faces backward: angle=0 → robot back, angle=±π → robot front
            # Mask the back arc, keep the front arc
            if -1.57 < angle < 1.57: 
                new_ranges[i] = float('inf') # Mask robot's back
        
        msg.ranges = new_ranges
        # Restamp to current time so SLAM/RViz TF lookup doesn't fail
        msg.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(msg)

def main():
    rclpy.init()
    rclpy.spin(ScanFilter())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
