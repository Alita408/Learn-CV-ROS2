"""Project 04: RRT* sampling-based planning around circular obstacles."""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

from robotlab.planning import CircleObstacle, rrt_star

from ._plotting import finish_figure


def run(output: str, show: bool = False) -> None:
    obstacles = [
        CircleObstacle(2.8, 2.7, 1.0),
        CircleObstacle(5.2, 4.8, 1.15),
        CircleObstacle(3.0, 6.8, 0.9),
        CircleObstacle(7.3, 7.0, 1.0),
    ]
    result = rrt_star(
        (0.6, 0.6),
        (9.2, 9.0),
        ((0.0, 10.0), (0.0, 10.0)),
        obstacles,
        max_iterations=2200,
        robot_radius=0.16,
        seed=12,
    )
    if not result.path:
        raise RuntimeError("RRT* failed to find a path; increase max_iterations")

    figure, axis = plt.subplots(figsize=(7, 7))
    for index in range(1, len(result.nodes)):
        parent = result.parents[index]
        if parent >= 0:
            axis.plot(
                [result.nodes[index, 0], result.nodes[parent, 0]],
                [result.nodes[index, 1], result.nodes[parent, 1]],
                color="#9aa0a6",
                linewidth=0.35,
                alpha=0.5,
            )
    for obstacle in obstacles:
        axis.add_patch(Circle((obstacle.x, obstacle.y), obstacle.radius, color="#ef476f"))
    path = np.asarray(result.path)
    axis.plot(path[:, 0], path[:, 1], color="#073b4c", linewidth=3, label="RRT* path")
    axis.scatter(path[[0, -1], 0], path[[0, -1], 1], c=["lime", "blue"], s=70)
    axis.set(xlim=(0, 10), ylim=(0, 10), aspect="equal")
    axis.set_title(
        f"RRT*: cost={result.cost:.2f}, nodes={len(result.nodes)}, "
        f"iterations={result.iterations}"
    )
    axis.legend()
    finish_figure(figure, output, show)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="outputs/p04_rrt_star.png")
    parser.add_argument("--show", action="store_true")
    arguments = parser.parse_args()
    run(arguments.output, arguments.show)


if __name__ == "__main__":
    main()
