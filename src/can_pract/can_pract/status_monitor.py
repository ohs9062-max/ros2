#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from can_interfaces.msg import CanStatus


class StatusMonitor(Node):
    def __init__(self):
        super().__init__("status_monitor")

        self.subscription = self.create_subscription(
            CanStatus,
            "/can_status",
            self.status_callback,
            10,
        )

        self.get_logger().info("status_monitor started")
        self.get_logger().info("listening topic: /can_status")

    def status_callback(self, msg):
        self.get_logger().info(
            f"CAN STATUS "
            f"success={msg.success}, "
            f"node_id={msg.node_id}, "
            f"port={msg.port}, "
            f"message={msg.message}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = StatusMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
