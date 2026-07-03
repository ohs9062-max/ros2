#!/usr/bin/env python3

import subprocess

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from can_interfaces.action import CanControl
from can_interfaces.msg import CanStatus


class CanControlActionServer(Node):
    def __init__(self):
        super().__init__("action_server")

        self.action_server = ActionServer(
            self,
            CanControl,
            "/CanControl",
            self.execute_callback,
        )

        # /can_status Topic Publisher
        self.status_pub = self.create_publisher(
            CanStatus,
            "/can_status",
            10,
        )

        self.get_logger().info("/CanControl action server started")
        self.get_logger().info("/can_status topic publisher started")

    def publish_status(self, success: bool, node_id: int, port: int, message: str):
        status_msg = CanStatus()
        status_msg.success = success
        status_msg.node_id = node_id
        status_msg.port = port
        status_msg.message = message

        self.status_pub.publish(status_msg)

    def execute_callback(self, goal_handle):
        goal = goal_handle.request

        feedback = CanControl.Feedback()
        feedback.stage = "received_goal"
        feedback.attempt = 1
        feedback.detail = (
            f"Goal received: node_id={goal.node_id}, "
            f"port={goal.port}, value={goal.value}"
        )
        goal_handle.publish_feedback(feedback)

        can_id = 0x100 + goal.node_id
        data = f"{goal.port:02X}{goal.value:02X}"
        frame = f"{can_id:X}#{data}"

        feedback.stage = "building_can_frame"
        feedback.detail = f"CAN frame 생성 완료: {frame}"
        goal_handle.publish_feedback(feedback)

        self.get_logger().info(f"Sending CAN frame: {frame}")

        feedback.stage = "sending_can_frame"
        feedback.detail = "cansend 실행 중"
        goal_handle.publish_feedback(feedback)

        result = CanControl.Result()
        result.response_can_id = can_id
        result.ctrl_code = 0

        max_attempts = max(1, goal.retries)
        last_error = ""

        for attempt in range(1, max_attempts + 1):
            self.get_logger().info(
                f"cansend attempt {attempt}/{max_attempts}: {frame}"
            )

            feedback.stage = "sending_can_frame"
            feedback.attempt = attempt
            feedback.detail = f"cansend 실행 중 ({attempt}/{max_attempts})"
            goal_handle.publish_feedback(feedback)

            try:
                subprocess.run(
                    ["cansend", "can0", frame],
                    #["sleep", "2"], 
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=1.0,
                )

                self.get_logger().info(
                    f"cansend success on attempt {attempt}/{max_attempts}: {frame}"
                )

                result.success = True
                result.ctrl_code = 0
                result.message = f"Sent CAN frame: {frame}"
                goal_handle.succeed()

                self.publish_status(
                    True,
                    goal.node_id,
                    goal.port,
                    f"CAN send success: {frame}",
                )

                return result

            except subprocess.TimeoutExpired:
                last_error = "cansend timeout"

                self.get_logger().warn(
                    f"cansend timeout on attempt {attempt}/{max_attempts}"
                )

                feedback.stage = "retrying_can_frame"
                feedback.attempt = attempt
                feedback.detail = f"cansend timeout ({attempt}/{max_attempts})"
                goal_handle.publish_feedback(feedback)


            except subprocess.CalledProcessError as e:
                last_error = e.stderr.strip() if e.stderr else str(e)

                self.get_logger().warn(
                    f"cansend failed on attempt {attempt}/{max_attempts}: {last_error}"
                )

                feedback.stage = "retrying_can_frame"
                feedback.attempt = attempt
                feedback.detail = f"cansend 실패 ({attempt}/{max_attempts}): {last_error}"
                goal_handle.publish_feedback(feedback)

            except FileNotFoundError:
                result.success = False
                result.ctrl_code = 2
                result.message = "cansend command not found"
                goal_handle.abort()

                self.publish_status(
                    False,
                    goal.node_id,
                    goal.port,
                    "cansend command not found",
                )

                return result

        result.success = False
        result.ctrl_code = 1
        result.message = f"cansend failed after {max_attempts} attempts: {last_error}"
        goal_handle.abort()

        self.publish_status(
            False,
            goal.node_id,
            goal.port,
            result.message,
        )

        return result


def main(args=None):
    rclpy.init(args=args)

    node = CanControlActionServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()