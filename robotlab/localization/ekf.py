"""Extended Kalman filter for planar range-bearing localization."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np


def normalize_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


@dataclass
class ExtendedKalmanFilter:
    state: np.ndarray
    covariance: np.ndarray
    process_covariance: np.ndarray
    measurement_covariance: np.ndarray

    def __post_init__(self) -> None:
        self.state = np.asarray(self.state, dtype=float).reshape(3)
        self.covariance = np.asarray(self.covariance, dtype=float).reshape(3, 3)
        self.process_covariance = np.asarray(self.process_covariance, dtype=float).reshape(3, 3)
        self.measurement_covariance = np.asarray(
            self.measurement_covariance, dtype=float
        ).reshape(2, 2)

    def predict(self, control: Tuple[float, float], dt: float) -> np.ndarray:
        velocity, yaw_rate = control
        x, y, yaw = self.state
        self.state = np.array(
            [
                x + velocity * math.cos(yaw) * dt,
                y + velocity * math.sin(yaw) * dt,
                normalize_angle(yaw + yaw_rate * dt),
            ]
        )
        jacobian = np.array(
            [
                [1.0, 0.0, -velocity * math.sin(yaw) * dt],
                [0.0, 1.0, velocity * math.cos(yaw) * dt],
                [0.0, 0.0, 1.0],
            ]
        )
        self.covariance = (
            jacobian @ self.covariance @ jacobian.T + self.process_covariance
        )
        return self.state.copy()

    def update_range_bearing(
        self,
        measurement: Tuple[float, float],
        landmark_xy: Tuple[float, float],
    ) -> np.ndarray:
        landmark = np.asarray(landmark_xy, dtype=float)
        delta = landmark - self.state[:2]
        squared_range = float(np.dot(delta, delta))
        if squared_range < 1e-12:
            raise ValueError("robot state coincides with the landmark")
        expected_range = math.sqrt(squared_range)
        expected_bearing = normalize_angle(math.atan2(delta[1], delta[0]) - self.state[2])
        jacobian = np.array(
            [
                [-delta[0] / expected_range, -delta[1] / expected_range, 0.0],
                [delta[1] / squared_range, -delta[0] / squared_range, -1.0],
            ]
        )
        innovation = np.asarray(measurement, dtype=float) - np.array(
            [expected_range, expected_bearing]
        )
        innovation[1] = normalize_angle(float(innovation[1]))
        innovation_covariance = (
            jacobian @ self.covariance @ jacobian.T + self.measurement_covariance
        )
        kalman_gain = self.covariance @ jacobian.T @ np.linalg.inv(innovation_covariance)
        self.state = self.state + kalman_gain @ innovation
        self.state[2] = normalize_angle(float(self.state[2]))
        identity = np.eye(3)
        correction = identity - kalman_gain @ jacobian
        self.covariance = (
            correction @ self.covariance @ correction.T
            + kalman_gain @ self.measurement_covariance @ kalman_gain.T
        )
        return self.state.copy()
