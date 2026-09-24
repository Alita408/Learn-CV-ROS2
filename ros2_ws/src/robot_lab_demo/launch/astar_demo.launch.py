from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="robot_lab_demo",
                executable="astar_publisher",
                name="astar_publisher",
                output="screen",
                parameters=[{"resolution": 0.2}],
            )
        ]
    )
