"""Project 06: fuse noisy odometry with landmark range-bearing observations."""

from __future__ import annotations

import argparse
import math

import matplotlib.pyplot as plt
import numpy as np

from robotlab.localization import ExtendedKalmanFilter, normalize_angle

from ._plotting import finish_figure


def propagate(state: np.ndarray, control, dt: float) -> np.ndarray:
    velocity, yaw_rate = control
    return np.array(
        [
            state[0] + velocity * math.cos(state[2]) * dt,
            state[1] + velocity * math.sin(state[2]) * dt,
            normalize_angle(state[2] + yaw_rate * dt),
        ]
    )


def run(output: str, show: bool = False) -> None:
    rng = np.random.default_rng(18)
    landmarks = np.array([[0.0, 0.0], [8.0, 0.0], [8.0, 8.0], [0.0, 8.0]])
    true_state = np.array([1.0, 1.0, 0.2])
    dead_reckoning = true_state.copy()
    ekf = ExtendedKalmanFilter(
        state=np.array([0.6, 1.35, 0.05]),
        covariance=np.diag([0.5, 0.5, 0.2]),
        process_covariance=np.diag([0.012, 0.012, 0.004]),
        measurement_covariance=np.diag([0.10**2, math.radians(2.0) ** 2]),
    )
    true_history = [true_state.copy()]
    dead_history = [dead_reckoning.copy()]
    estimate_history = [ekf.state.copy()]
    dt = 0.1

    for step in range(260):
        control = (0.55, 0.18 + 0.05 * math.sin(step / 35.0))
        true_state = propagate(true_state, control, dt)
        odometry_control = (
            control[0] * 1.035 + rng.normal(0.0, 0.025),
            control[1] - 0.012 + rng.normal(0.0, 0.008),
        )
        dead_reckoning = propagate(dead_reckoning, odometry_control, dt)
        ekf.predict(odometry_control, dt)

        if step % 3 == 0:
            for landmark in landmarks:
                delta = landmark - true_state[:2]
                distance = float(np.linalg.norm(delta))
                if distance > 7.5:
                    continue
                bearing = normalize_angle(math.atan2(delta[1], delta[0]) - true_state[2])
                measurement = (
                    distance + rng.normal(0.0, 0.10),
                    bearing + rng.normal(0.0, math.radians(2.0)),
                )
                ekf.update_range_bearing(measurement, tuple(landmark))

        true_history.append(true_state.copy())
        dead_history.append(dead_reckoning.copy())
        estimate_history.append(ekf.state.copy())

    truth = np.asarray(true_history)
    dead = np.asarray(dead_history)
    estimate = np.asarray(estimate_history)
    dead_rmse = float(np.sqrt(np.mean(np.sum((dead[:, :2] - truth[:, :2]) ** 2, axis=1))))
    ekf_rmse = float(np.sqrt(np.mean(np.sum((estimate[:, :2] - truth[:, :2]) ** 2, axis=1))))
    if ekf_rmse >= dead_rmse:
        raise RuntimeError("EKF did not improve over odometry in the fixed benchmark")

    figure, axis = plt.subplots(figsize=(8, 7))
    axis.plot(truth[:, 0], truth[:, 1], label="ground truth", linewidth=2.5)
    axis.plot(dead[:, 0], dead[:, 1], label=f"odometry RMSE={dead_rmse:.2f} m", linestyle="--")
    axis.plot(estimate[:, 0], estimate[:, 1], label=f"EKF RMSE={ekf_rmse:.2f} m")
    axis.scatter(landmarks[:, 0], landmarks[:, 1], marker="*", s=130, label="landmarks")
    axis.set_aspect("equal")
    axis.grid(alpha=0.25)
    axis.set_title("EKF localization: odometry + range/bearing")
    axis.legend()
    finish_figure(figure, output, show)
    print(f"odometry RMSE={dead_rmse:.3f} m; EKF RMSE={ekf_rmse:.3f} m")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="outputs/p06_ekf_localization.png")
    parser.add_argument("--show", action="store_true")
    arguments = parser.parse_args()
    run(arguments.output, arguments.show)


if __name__ == "__main__":
    main()
