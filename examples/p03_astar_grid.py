"""Project 03: compare Dijkstra and A* on the same occupancy grid."""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np

from robotlab.planning import GridMap, shortest_path
from robotlab.scenes import make_planning_grid

from ._plotting import finish_figure


def run(output: str, show: bool = False) -> None:
    occupancy = make_planning_grid()
    start = (55, 4)
    goal = (4, 75)
    grid = GridMap(occupancy)
    astar = shortest_path(grid, start, goal, "astar")
    dijkstra = shortest_path(grid, start, goal, "dijkstra")

    figure, axis = plt.subplots(figsize=(9, 6))
    axis.imshow(occupancy, cmap="gray_r", origin="upper")
    for result, label, color in (
        (dijkstra, "Dijkstra", "#ff9f1c"),
        (astar, "A*", "#2ec4b6"),
    ):
        path = np.asarray(result.path)
        axis.plot(path[:, 1], path[:, 0], color=color, linewidth=2, label=label)
    axis.scatter([start[1], goal[1]], [start[0], goal[0]], c=["lime", "blue"], s=60)
    axis.set_title(
        f"Equal optimal cost {astar.cost:.2f}; expanded A* {astar.expanded}, "
        f"Dijkstra {dijkstra.expanded}"
    )
    axis.legend()
    axis.set_xlabel("grid column")
    axis.set_ylabel("grid row")
    finish_figure(figure, output, show)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="outputs/p03_astar_grid.png")
    parser.add_argument("--show", action="store_true")
    arguments = parser.parse_args()
    run(arguments.output, arguments.show)


if __name__ == "__main__":
    main()
