#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from can_interfaces.srv import Cmd
from can_interfaces.action import CanControl


COMMAND_VALUE_MAP = {
    1: ("START", 1),
    2: ("STOP", 0),
    3: ("PAUSE", 2),
    4: ("RESUME", 3),
    5: ("HOME", 4),
}


class RobotCmdServer(Node):
    def __init__(self):
        super().__init__("cmd_server")

        self.service = self.create_service(
            Cmd,
            "/cmd_service",
            self.handle_cmd_request,
        )

        self.action_client = ActionClient(
            self,
            CanControl,
            "/CanControl",
        )

        self.get_logger().info("/cmd_service service server started")

    def handle_cmd_request(self, request, response):
        if request.cmd not in COMMAND_VALUE_MAP:
            response.success = False
            response.message = f"Unknown cmd: {request.cmd}"
            return response

        command_name, value = COMMAND_VALUE_MAP[request.cmd]

        goal_msg = CanControl.Goal()
        goal_msg.node_id = request.node_id
        goal_msg.port = request.port
        goal_msg.value = value
        goal_msg.retries = 3
        goal_msg.timeout_ms = 1000

        self.get_logger().info(
            f"Received {command_name}: "
            f"node_id={request.node_id}, port={request.port}, value={value}"
        )

        if not self.action_client.wait_for_server(timeout_sec=3.0):
            response.success = False
            response.message = "/CanControl action server not available"
            return response

        goal_future = self.action_client.send_goal_async(goal_msg)
        goal_future.add_done_callback(self.goal_response_callback)

        response.success = True
        response.message = f"{command_name} goal sent"
        return response

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if goal_handle is None:
            self.get_logger().error("CanControl goal response is None")
            return

        if not goal_handle.accepted:
            self.get_logger().error("CanControl goal rejected")
            return

        self.get_logger().info("CanControl goal accepted")

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result

        self.get_logger().info(
            f"CanControl result: success={result.success}, "
            f"message={result.message}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = RobotCmdServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
