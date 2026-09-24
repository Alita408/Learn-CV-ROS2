"""Publish a synthetic occupancy grid and the A* path through it."""

from __future__ import annotations

import numpy as np
import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid, Path
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from robotlab.planning import GridMap, shortest_path


class AStarPublisher(Node):
    def __init__(self) -> None:
        super().__init__("astar_publisher")
        self.declare_parameter("resolution", 0.2)
        self.resolution = float(self.get_parameter("resolution").value)
        qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE,
        )
        self.map_publisher = self.create_publisher(OccupancyGrid, "demo_map", qos)
        self.path_publisher = self.create_publisher(Path, "demo_path", qos)
        self.occupancy, self.result = self._plan()
        self.timer = self.create_timer(1.0, self.publish_messages)
        self.get_logger().info(
            f"A* ready: {len(self.result.path)} cells, cost={self.result.cost:.3f}, "
            f"expanded={self.result.expanded}"
        )

    @staticmethod
    def _plan():
        occupancy = np.zeros((30, 45), dtype=bool)
        occupancy[3:25, 12:15] = True
        occupancy[13:17, 12:15] = False
        occupancy[8:11, 22:41] = True
        occupancy[8:11, 29:34] = False
        occupancy[20:23, 21:45] = True
        occupancy[20:23, 36:40] = False
        result = shortest_path(GridMap(occupancy), (27, 2), (2, 42), "astar")
        return occupancy, result

    def publish_messages(self) -> None:
        now = self.get_clock().now().to_msg()
        height, width = self.occupancy.shape

        grid = OccupancyGrid()
        grid.header.stamp = now
        grid.header.frame_id = "map"
        grid.info.map_load_time = now
        grid.info.resolution = self.resolution
        grid.info.width = width
        grid.info.height = height
        grid.info.origin.orientation.w = 1.0
        grid.data = [100 if value else 0 for value in self.occupancy.ravel()]

        path = Path()
        path.header = grid.header
        for row, col in self.result.path:
            pose = PoseStamped()
            pose.header = grid.header
            pose.pose.position.x = (col + 0.5) * self.resolution
            pose.pose.position.y = (row + 0.5) * self.resolution
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)

        self.map_publisher.publish(grid)
        self.path_publisher.publish(path)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = AStarPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
