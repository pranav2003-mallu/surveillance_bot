#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

# Publish rate limit — RPLidar A1 runs at 10 Hz but RViz over WiFi
# can't keep up. Throttling to 5 Hz prevents the message filter queue
# from filling up while still giving SLAM enough scan data.
PUBLISH_RATE_HZ = 5.0

class ScanFilter(Node):
    def __init__(self):
        super().__init__('scan_filter')

        self._publish_interval = 1.0 / PUBLISH_RATE_HZ  # seconds
        self._last_pub_time = None  # will be set on first publish

        # Input QoS: keep enough history to not drop lidar packets
        sub_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        # Output QoS: depth=1 — always deliver the LATEST scan, drop stale ones
        pub_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.create_subscription(LaserScan, '/scan', self.scan_cb, sub_qos)
        self.pub = self.create_publisher(LaserScan, '/scan_filtered', pub_qos)

        self.get_logger().info(
            f"✅ Scan Filter Active: /scan -> /scan_filtered @ {PUBLISH_RATE_HZ} Hz"
        )

    def scan_cb(self, msg):
        # --- Rate limiter ---
        now = self.get_clock().now()
        if self._last_pub_time is not None:
            elapsed = (now - self._last_pub_time).nanoseconds * 1e-9
            if elapsed < self._publish_interval:
                return  # skip this scan, too soon
        self._last_pub_time = now

        # Keep frame consistent
        msg.header.frame_id = "lidar_1"

        # Lidar faces backward: angle=0 → robot back, angle=±π → robot front
        # Mask the back arc (-90° to +90°), keep the front arc
        new_ranges = list(msg.ranges)
        for i in range(len(new_ranges)):
            angle = msg.angle_min + (i * msg.angle_increment)
            if -1.57 < angle < 1.57:
                new_ranges[i] = float('inf')  # mask robot's back

        msg.ranges = new_ranges
        # Restamp to current time so SLAM/RViz TF lookup always succeeds
        msg.header.stamp = now.to_msg()
        self.pub.publish(msg)

def main():
    rclpy.init()
    rclpy.spin(ScanFilter())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
