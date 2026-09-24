from __future__ import annotations

import math
import unittest

import numpy as np

from robotlab.localization import ExtendedKalmanFilter
from robotlab.mapping import inflate_obstacles
from robotlab.perception import (
    CameraIntrinsics,
    depth_to_points,
    detect_components,
    dominant_color_mask,
    project_points,
)
from robotlab.planning import (
    CircleObstacle,
    DWAConfig,
    GridMap,
    RobotState,
    dwa_control,
    rrt_star,
    shortest_path,
)


class PerceptionTests(unittest.TestCase):
    def test_projection_round_trip(self) -> None:
        camera = CameraIntrinsics(100.0, 105.0, 3.0, 2.0)
        depth = np.full((5, 7), 2.0)
        points = depth_to_points(depth, camera)
        pixels = project_points(points, camera)
        self.assertEqual(points.shape, (35, 3))
        self.assertAlmostEqual(float(pixels[:, 0].min()), 0.0)
        self.assertAlmostEqual(float(pixels[:, 0].max()), 6.0)
        self.assertAlmostEqual(float(pixels[:, 1].min()), 0.0)
        self.assertAlmostEqual(float(pixels[:, 1].max()), 4.0)

    def test_color_components(self) -> None:
        image = np.zeros((20, 30, 3), dtype=np.uint8)
        image[2:7, 3:9] = [220, 20, 10]
        image[12:18, 19:27] = [230, 30, 20]
        mask = dominant_color_mask(image, "red")
        detections = detect_components(mask, min_area=10)
        self.assertEqual([d.area for d in detections], [48, 30])


class MappingAndPlanningTests(unittest.TestCase):
    def test_inflation_is_circular(self) -> None:
        grid = np.zeros((7, 7), dtype=bool)
        grid[3, 3] = True
        inflated = inflate_obstacles(grid, 2)
        self.assertTrue(inflated[3, 5])
        self.assertFalse(inflated[1, 1])

    def test_astar_matches_dijkstra_and_expands_less(self) -> None:
        occupancy = np.zeros((30, 30), dtype=bool)
        occupancy[4:27, 14] = True
        occupancy[16:19, 14] = False
        grid = GridMap(occupancy)
        astar = shortest_path(grid, (27, 2), (2, 27), "astar")
        dijkstra = shortest_path(grid, (27, 2), (2, 27), "dijkstra")
        self.assertAlmostEqual(astar.cost, dijkstra.cost)
        self.assertLess(astar.expanded, dijkstra.expanded)

    def test_rrt_star_finds_a_route(self) -> None:
        result = rrt_star(
            (0.0, 0.0),
            (5.0, 5.0),
            ((0.0, 5.5), (0.0, 5.5)),
            [CircleObstacle(2.5, 2.5, 0.8)],
            max_iterations=1500,
            seed=3,
        )
        self.assertTrue(result.path)
        np.testing.assert_allclose(result.path[0], (0.0, 0.0))
        np.testing.assert_allclose(result.path[-1], (5.0, 5.0))
        path = np.asarray(result.path)
        measured_cost = float(np.linalg.norm(np.diff(path, axis=0), axis=1).sum())
        self.assertAlmostEqual(result.cost, measured_cost)

        obstacle = np.array([2.5, 2.5])
        for segment_start, segment_end in zip(path[:-1], path[1:]):
            segment = segment_end - segment_start
            fraction = float(
                np.clip(
                    np.dot(obstacle - segment_start, segment)
                    / np.dot(segment, segment),
                    0.0,
                    1.0,
                )
            )
            closest = segment_start + fraction * segment
            self.assertGreater(float(np.linalg.norm(closest - obstacle)), 0.8)

    def test_dwa_trajectory_is_collision_free(self) -> None:
        config = DWAConfig(robot_radius=0.3)
        obstacles = np.array([[1.0, 0.0], [2.0, 1.0]])
        _, trajectory = dwa_control(RobotState(0.0, 0.0, 0.0), (4.0, 2.0), obstacles, config)
        distances = np.linalg.norm(trajectory[:, None, :2] - obstacles[None, :, :], axis=2)
        self.assertGreater(float(distances.min()), config.robot_radius)

    def test_dwa_rejects_invalid_timing(self) -> None:
        with self.assertRaises(ValueError):
            dwa_control(RobotState(0.0, 0.0, 0.0), (1.0, 0.0), np.empty((0, 2)), DWAConfig(dt=0.0))

    def test_dwa_reports_when_no_control_is_safe(self) -> None:
        with self.assertRaises(RuntimeError):
            dwa_control(
                RobotState(0.0, 0.0, 0.0),
                (1.0, 0.0),
                np.array([[0.0, 0.0]]),
                DWAConfig(robot_radius=0.5),
            )


class LocalizationTests(unittest.TestCase):
    def test_landmark_update_reduces_position_error(self) -> None:
        ekf = ExtendedKalmanFilter(
            state=np.array([0.8, 0.2, 0.0]),
            covariance=np.diag([1.0, 1.0, 0.2]),
            process_covariance=np.eye(3) * 0.01,
            measurement_covariance=np.diag([0.05**2, math.radians(1.0) ** 2]),
        )
        before = float(np.linalg.norm(ekf.state[:2]))
        ekf.update_range_bearing((5.0, 0.0), (5.0, 0.0))
        after = float(np.linalg.norm(ekf.state[:2]))
        self.assertLess(after, before)


if __name__ == "__main__":
    unittest.main()
