"""Dynamic Window Approach (DWA) for a differential-drive robot."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass(frozen=True)
class RobotState:
    x: float
    y: float
    yaw: float
    velocity: float = 0.0
    yaw_rate: float = 0.0


@dataclass(frozen=True)
class DWAConfig:
    max_speed: float = 1.0
    min_speed: float = 0.0
    max_yaw_rate: float = math.radians(90.0)
    max_acceleration: float = 0.6
    max_yaw_acceleration: float = math.radians(120.0)
    velocity_resolution: float = 0.05
    yaw_rate_resolution: float = math.radians(6.0)
    dt: float = 0.1
    predict_time: float = 1.8
    robot_radius: float = 0.35
    goal_distance_gain: float = 1.0
    heading_gain: float = 0.45
    speed_gain: float = 0.35
    clearance_gain: float = 0.25


def _normalize_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def motion(state: RobotState, control: Tuple[float, float], dt: float) -> RobotState:
    velocity, yaw_rate = control
    yaw = _normalize_angle(state.yaw + yaw_rate * dt)
    return RobotState(
        x=state.x + velocity * math.cos(yaw) * dt,
        y=state.y + velocity * math.sin(yaw) * dt,
        yaw=yaw,
        velocity=velocity,
        yaw_rate=yaw_rate,
    )


def _trajectory(state: RobotState, control: Tuple[float, float], config: DWAConfig) -> np.ndarray:
    predicted = state
    rows = [[state.x, state.y, state.yaw, state.velocity, state.yaw_rate]]
    elapsed = 0.0
    while elapsed < config.predict_time - 1e-12:
        predicted = motion(predicted, control, config.dt)
        rows.append(
            [predicted.x, predicted.y, predicted.yaw, predicted.velocity, predicted.yaw_rate]
        )
        elapsed += config.dt
    return np.asarray(rows)


def _samples(low: float, high: float, resolution: float) -> np.ndarray:
    if high <= low + 1e-12:
        return np.array([low])
    count = max(2, int(math.ceil((high - low) / resolution)) + 1)
    return np.linspace(low, high, count)


def dwa_control(
    state: RobotState,
    goal_xy: Tuple[float, float],
    obstacles_xy: np.ndarray,
    config: DWAConfig = DWAConfig(),
) -> Tuple[Tuple[float, float], np.ndarray]:
    """Select velocity/yaw-rate and return the corresponding predicted trajectory."""
    if (
        config.dt <= 0.0
        or config.predict_time <= 0.0
        or config.velocity_resolution <= 0.0
        or config.yaw_rate_resolution <= 0.0
    ):
        raise ValueError("dt, predict_time, and sampling resolutions must be positive")
    obstacles = np.asarray(obstacles_xy, dtype=float)
    if obstacles.size == 0:
        obstacles = np.empty((0, 2), dtype=float)
    if obstacles.ndim != 2 or obstacles.shape[1] != 2:
        raise ValueError("obstacles_xy must have shape (N, 2)")

    velocity_low = max(config.min_speed, state.velocity - config.max_acceleration * config.dt)
    velocity_high = min(config.max_speed, state.velocity + config.max_acceleration * config.dt)
    yaw_low = max(
        -config.max_yaw_rate,
        state.yaw_rate - config.max_yaw_acceleration * config.dt,
    )
    yaw_high = min(
        config.max_yaw_rate,
        state.yaw_rate + config.max_yaw_acceleration * config.dt,
    )

    best_score = -math.inf
    best_control = (0.0, 0.0)
    best_trajectory = _trajectory(state, best_control, config)
    goal = np.asarray(goal_xy, dtype=float)

    for velocity in _samples(velocity_low, velocity_high, config.velocity_resolution):
        for yaw_rate in _samples(yaw_low, yaw_high, config.yaw_rate_resolution):
            trajectory = _trajectory(state, (float(velocity), float(yaw_rate)), config)
            end = trajectory[-1, :2]
            goal_distance = float(np.linalg.norm(goal - end))
            desired_heading = math.atan2(goal[1] - end[1], goal[0] - end[0])
            heading_error = abs(_normalize_angle(desired_heading - float(trajectory[-1, 2])))

            if obstacles.size:
                distances = np.linalg.norm(
                    trajectory[:, None, :2] - obstacles[None, :, :], axis=2
                )
                clearance = float(distances.min())
                if clearance <= config.robot_radius:
                    continue
            else:
                clearance = 3.0

            score = (
                -config.goal_distance_gain * goal_distance
                - config.heading_gain * heading_error
                + config.speed_gain * float(velocity)
                + config.clearance_gain * min(clearance, 3.0)
            )
            if score > best_score:
                best_score = score
                best_control = (float(velocity), float(yaw_rate))
                best_trajectory = trajectory

    if best_score == -math.inf:
        raise RuntimeError("no collision-free control is available in the dynamic window")
    return best_control, best_trajectory
