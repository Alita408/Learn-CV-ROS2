"""Occupancy-grid utilities."""

from __future__ import annotations

import numpy as np


def inflate_obstacles(occupancy: np.ndarray, radius_cells: int) -> np.ndarray:
    """Inflate occupied cells by a circular robot radius."""
    grid = np.asarray(occupancy, dtype=bool)
    if grid.ndim != 2:
        raise ValueError("occupancy must be a 2-D array")
    if radius_cells < 0:
        raise ValueError("radius_cells must be >= 0")
    if radius_cells == 0:
        return grid.copy()

    height, width = grid.shape
    inflated = grid.copy()
    occupied_rows, occupied_cols = np.nonzero(grid)
    for delta_row in range(-radius_cells, radius_cells + 1):
        for delta_col in range(-radius_cells, radius_cells + 1):
            if delta_row * delta_row + delta_col * delta_col > radius_cells * radius_cells:
                continue
            rows = occupied_rows + delta_row
            cols = occupied_cols + delta_col
            valid = (rows >= 0) & (rows < height) & (cols >= 0) & (cols < width)
            inflated[rows[valid], cols[valid]] = True
    return inflated
