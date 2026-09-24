"""Dijkstra and A* search on an 8-connected occupancy grid."""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np

GridCell = Tuple[int, int]


class PathNotFound(RuntimeError):
    pass


@dataclass(frozen=True)
class SearchResult:
    path: List[GridCell]
    cost: float
    expanded: int


@dataclass(frozen=True)
class GridMap:
    occupied: np.ndarray
    allow_diagonal: bool = True

    def __post_init__(self) -> None:
        grid = np.asarray(self.occupied, dtype=bool)
        if grid.ndim != 2:
            raise ValueError("occupied must be a 2-D array")
        object.__setattr__(self, "occupied", grid)

    @property
    def shape(self) -> Tuple[int, int]:
        return self.occupied.shape

    def is_free(self, cell: GridCell) -> bool:
        row, col = cell
        return (
            0 <= row < self.occupied.shape[0]
            and 0 <= col < self.occupied.shape[1]
            and not self.occupied[row, col]
        )

    def neighbors(self, cell: GridCell) -> Iterable[Tuple[GridCell, float]]:
        row, col = cell
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if self.allow_diagonal:
            moves += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for delta_row, delta_col in moves:
            next_cell = (row + delta_row, col + delta_col)
            if not self.is_free(next_cell):
                continue
            if delta_row and delta_col:
                # Prevent squeezing diagonally through the corners of two obstacles.
                if not self.is_free((row + delta_row, col)):
                    continue
                if not self.is_free((row, col + delta_col)):
                    continue
                yield next_cell, math.sqrt(2.0)
            else:
                yield next_cell, 1.0


def _heuristic(cell: GridCell, goal: GridCell, diagonal: bool) -> float:
    delta_row = abs(cell[0] - goal[0])
    delta_col = abs(cell[1] - goal[1])
    if not diagonal:
        return float(delta_row + delta_col)
    smaller = min(delta_row, delta_col)
    larger = max(delta_row, delta_col)
    return float(larger + (math.sqrt(2.0) - 1.0) * smaller)


def shortest_path(
    grid: GridMap,
    start: GridCell,
    goal: GridCell,
    algorithm: str = "astar",
) -> SearchResult:
    """Find a lowest-cost path using A* or Dijkstra."""
    if algorithm not in {"astar", "dijkstra"}:
        raise ValueError("algorithm must be 'astar' or 'dijkstra'")
    if not grid.is_free(start):
        raise ValueError("start must be a free cell inside the grid")
    if not grid.is_free(goal):
        raise ValueError("goal must be a free cell inside the grid")

    frontier = [(0.0, 0, start)]
    came_from: Dict[GridCell, GridCell] = {}
    cost_so_far: Dict[GridCell, float] = {start: 0.0}
    closed = set()
    sequence = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in closed:
            continue
        closed.add(current)
        if current == goal:
            break

        for neighbor, move_cost in grid.neighbors(current):
            new_cost = cost_so_far[current] + move_cost
            if new_cost >= cost_so_far.get(neighbor, math.inf):
                continue
            cost_so_far[neighbor] = new_cost
            came_from[neighbor] = current
            estimate = 0.0
            if algorithm == "astar":
                estimate = _heuristic(neighbor, goal, grid.allow_diagonal)
            sequence += 1
            heapq.heappush(frontier, (new_cost + estimate, sequence, neighbor))

    if goal not in cost_so_far:
        raise PathNotFound(f"no path from {start} to {goal}")

    path = [goal]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return SearchResult(path=path, cost=cost_so_far[goal], expanded=len(closed))
