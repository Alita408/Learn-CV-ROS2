"""Project 07: segment obstacles, inflate a costmap, and plan an A* route."""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np

from robotlab.mapping import inflate_obstacles
from robotlab.perception import dominant_color_mask
from robotlab.planning import GridMap, shortest_path
from robotlab.scenes import make_rgb_obstacle_scene

from ._plotting import finish_figure


def run(output: str, show: bool = False) -> None:
    image, start, goal = make_rgb_obstacle_scene()
    raw_occupancy = dominant_color_mask(image, "red")
    occupancy = inflate_obstacles(raw_occupancy, radius_cells=3)
    result = shortest_path(GridMap(occupancy), start, goal, "astar")
    if not result.path or any(occupancy[cell] for cell in result.path):
        raise RuntimeError("A* did not produce a collision-free path")
    path = np.asarray(result.path)

    figure, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    axes[0].imshow(image)
    axes[0].set_title("1. Synthetic RGB observation")
    axes[1].imshow(raw_occupancy, cmap="gray_r")
    axes[1].set_title("2. Perception: obstacle mask")
    axes[2].imshow(occupancy, cmap="gray_r")
    axes[2].plot(path[:, 1], path[:, 0], color="#00d4ff", linewidth=2.2)
    axes[2].scatter([start[1], goal[1]], [start[0], goal[0]], c=["lime", "blue"], s=55)
    axes[2].set_title(f"3. Inflated costmap + A* ({result.expanded} expansions)")
    for axis in axes:
        axis.set_axis_off()
    finish_figure(figure, output, show)
    print(f"path cells={len(result.path)} cost={result.cost:.3f} expanded={result.expanded}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="outputs/p07_perception_to_planning.png")
    parser.add_argument("--show", action="store_true")
    arguments = parser.parse_args()
    run(arguments.output, arguments.show)


if __name__ == "__main__":
    main()
