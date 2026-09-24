"""Project 05: closed-loop Dynamic Window Approach local control."""

from __future__ import annotations

import argparse
import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

from robotlab.planning import DWAConfig, RobotState, dwa_control, motion

from ._plotting import finish_figure


def run(output: str, show: bool = False) -> None:
    config = DWAConfig(predict_time=2.0, robot_radius=0.32)
    state = RobotState(0.0, 0.0, math.radians(15.0))
    goal = (8.5, 6.8)
    obstacles = np.array([[2.8, 1.5], [4.2, 3.0], [5.8, 4.0], [6.4, 6.0]])
    history = [[state.x, state.y]]

    for _ in range(900):
        control, _ = dwa_control(state, goal, obstacles, config)
        state = motion(state, control, config.dt)
        history.append([state.x, state.y])
        if np.linalg.norm(np.asarray(goal) - np.array([state.x, state.y])) < 0.35:
            break
    trajectory = np.asarray(history)

    figure, axis = plt.subplots(figsize=(8, 6))
    axis.plot(trajectory[:, 0], trajectory[:, 1], linewidth=2.5, label="closed-loop path")
    for x, y in obstacles:
        axis.add_patch(Circle((x, y), config.robot_radius, color="#ef476f", alpha=0.8))
    axis.scatter([history[0][0], goal[0]], [history[0][1], goal[1]], c=["lime", "blue"], s=70)
    axis.set_aspect("equal")
    axis.grid(alpha=0.25)
    final_error = float(np.linalg.norm(np.asarray(goal) - trajectory[-1]))
    if final_error >= 0.35:
        raise RuntimeError(f"DWA did not reach the goal; final error is {final_error:.3f} m")
    axis.set_title(f"DWA local control: steps={len(history)-1}, final error={final_error:.2f} m")
    axis.legend()
    finish_figure(figure, output, show)
    print(f"final state: {state}; goal error: {final_error:.3f} m")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="outputs/p05_dwa_local_planner.png")
    parser.add_argument("--show", action="store_true")
    arguments = parser.parse_args()
    run(arguments.output, arguments.show)


if __name__ == "__main__":
    main()
