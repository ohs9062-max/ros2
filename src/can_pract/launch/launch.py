from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="can_pract",
            executable="action_server",
            name="action_server",
            output="screen",
        ),

        Node(
            package="can_pract",
            executable="service_server",
            name="service_server",
            output="screen",
        ),

        Node(
            package="can_pract",
            executable="status_monitor",
            name="status_monitor",
            output="screen",
        ),
    ])