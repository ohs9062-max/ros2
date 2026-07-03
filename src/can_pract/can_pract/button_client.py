#!/usr/bin/env python3

import sys

import rclpy
from rclpy.node import Node

from can_interfaces.srv import Cmd


COMMAND_MAP = { 
    "start": 1,
    "stop": 2,
    "pause": 3,
    "resume": 4,
    "home": 5,
}


class ButtonClient(Node): #
    def __init__(self):
        super().__init__("button_client")

        self.client = self.create_client(
            Cmd,
              "/cmd_service"
              )

        self.get_logger().info("Waiting for /cmd_service service...")
        self.client.wait_for_service()
        self.get_logger().info("/cmd_service service connected")

    def send_cmd(self, cmd: int, node_id: int = 2, port: int = 1): 
        request = Cmd.Request()
        request.cmd = cmd
        request.node_id = node_id
        request.port = port

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        response = future.result()

        if response is None:
            self.get_logger().error("Service call failed")
            return

        self.get_logger().info(
            f"success={response.success}, message={response.message}" 
        )


def main(args=None): # 메인실행 
    rclpy.init(args=args) 

    if len(sys.argv) < 2: 
        print("Usage: ros2 run can_pract button_client [start|stop|pause|resume|home]")
        rclpy.shutdown()
        return

    command_name = sys.argv[1].lower() 

    if command_name not in COMMAND_MAP: 
        print(f"Unknown command: {command_name}")
        print("Available commands: start, stop, pause, resume, home")
        rclpy.shutdown()
        return

    node = ButtonClient()
    node.send_cmd(COMMAND_MAP[command_name]) 

    node.destroy_node() 
    rclpy.shutdown()


if __name__ == "__main__":
    main()
