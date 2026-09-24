"""Deterministic synthetic scenes used by the examples and tests."""

from __future__ import annotations

from typing import Tuple

import numpy as np


def make_rgb_obstacle_scene(
    height: int = 80,
    width: int = 120,
    seed: int = 4,
) -> Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]]:
    """Create an overhead RGB scene with red obstacles and free start/goal cells."""
    if height < 40 or width < 60:
        raise ValueError("scene must be at least 40x60")
    rng = np.random.default_rng(seed)
    image = np.full((height, width, 3), [42, 45, 52], dtype=np.uint8)
    image = np.clip(image + rng.integers(0, 9, image.shape, dtype=np.uint8), 0, 255)

    rectangles = [
        (int(0.18 * height), int(0.72 * height), int(0.22 * width), int(0.30 * width)),
        (0, int(0.42 * height), int(0.50 * width), int(0.58 * width)),
        (int(0.55 * height), height, int(0.68 * width), int(0.77 * width)),
    ]
    for top, bottom, left, right in rectangles:
        image[top:bottom, left:right] = [225, 35, 28]

    # Tiny red noise demonstrates why a minimum component area is useful.
    image[3:5, 8:10] = [210, 45, 35]
    start = (height - 6, 5)
    goal = (5, width - 6)
    image[start[0] - 2 : start[0] + 3, start[1] - 2 : start[1] + 3] = [30, 210, 70]
    image[goal[0] - 2 : goal[0] + 3, goal[1] - 2 : goal[1] + 3] = [45, 90, 230]
    return image, start, goal


def make_planning_grid(height: int = 60, width: int = 80) -> np.ndarray:
    grid = np.zeros((height, width), dtype=bool)
    grid[8:52, 22:25] = True
    grid[28:35, 22:25] = False
    grid[12:15, 24:64] = True
    grid[12:15, 43:49] = False
    grid[35:38, 40:80] = True
    grid[35:38, 67:73] = False
    grid[45:55, 50:54] = True
    return grid
