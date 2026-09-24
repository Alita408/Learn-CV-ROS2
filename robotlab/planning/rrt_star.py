"""A compact RRT* implementation for 2-D motion-planning experiments."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np


@dataclass(frozen=True)
class CircleObstacle:
    x: float
    y: float
    radius: float


@dataclass(frozen=True)
class RRTStarResult:
    path: List[Tuple[float, float]]
    nodes: np.ndarray
    parents: np.ndarray
    cost: float
    iterations: int


def _segment_is_free(
    start: np.ndarray,
    end: np.ndarray,
    obstacles: Sequence[CircleObstacle],
    robot_radius: float,
) -> bool:
    segment = end - start
    denominator = float(np.dot(segment, segment))
    for obstacle in obstacles:
        center = np.array([obstacle.x, obstacle.y], dtype=float)
        if denominator == 0.0:
            distance = float(np.linalg.norm(center - start))
        else:
            fraction = float(np.dot(center - start, segment) / denominator)
            closest = start + np.clip(fraction, 0.0, 1.0) * segment
            distance = float(np.linalg.norm(center - closest))
        if distance <= obstacle.radius + robot_radius:
            return False
    return True


def rrt_star(
    start: Tuple[float, float],
    goal: Tuple[float, float],
    bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    obstacles: Sequence[CircleObstacle],
    *,
    max_iterations: int = 1200,
    step_size: float = 0.45,
    goal_radius: float = 0.6,
    goal_sample_rate: float = 0.12,
    rewire_radius: float = 1.2,
    robot_radius: float = 0.0,
    seed: int = 7,
) -> RRTStarResult:
    """Plan a collision-free path; returns an empty path when no solution is found."""
    if max_iterations < 1 or step_size <= 0.0 or rewire_radius <= 0.0:
        raise ValueError("iteration count and distance parameters must be positive")
    if not 0.0 <= goal_sample_rate <= 1.0:
        raise ValueError("goal_sample_rate must be between 0 and 1")

    start_point = np.asarray(start, dtype=float)
    goal_point = np.asarray(goal, dtype=float)
    nodes = [start_point]
    parents = [-1]
    costs = [0.0]
    children = [set()]
    rng = np.random.default_rng(seed)

    def update_descendant_costs(root_index: int) -> None:
        pending = [root_index]
        while pending:
            parent = pending.pop()
            for child in children[parent]:
                costs[child] = costs[parent] + float(
                    np.linalg.norm(nodes[child] - nodes[parent])
                )
                pending.append(child)

    for iteration in range(1, max_iterations + 1):
        if rng.random() < goal_sample_rate:
            sample = goal_point
        else:
            sample = np.array(
                [
                    rng.uniform(bounds[0][0], bounds[0][1]),
                    rng.uniform(bounds[1][0], bounds[1][1]),
                ]
            )

        node_array = np.asarray(nodes)
        nearest_index = int(np.argmin(np.linalg.norm(node_array - sample, axis=1)))
        direction = sample - nodes[nearest_index]
        distance = float(np.linalg.norm(direction))
        if distance < 1e-12:
            continue
        new_node = nodes[nearest_index] + direction / distance * min(step_size, distance)
        if not _segment_is_free(nodes[nearest_index], new_node, obstacles, robot_radius):
            continue

        distances = np.linalg.norm(node_array - new_node, axis=1)
        near_indices = np.flatnonzero(distances <= rewire_radius).tolist()
        best_parent = nearest_index
        best_cost = costs[nearest_index] + float(np.linalg.norm(new_node - nodes[nearest_index]))
        for candidate in near_indices:
            candidate_cost = costs[candidate] + float(np.linalg.norm(new_node - nodes[candidate]))
            if candidate_cost < best_cost and _segment_is_free(
                nodes[candidate], new_node, obstacles, robot_radius
            ):
                best_parent = candidate
                best_cost = candidate_cost

        new_index = len(nodes)
        nodes.append(new_node)
        parents.append(best_parent)
        costs.append(best_cost)
        children.append(set())
        children[best_parent].add(new_index)

        for candidate in near_indices:
            through_new = best_cost + float(np.linalg.norm(nodes[candidate] - new_node))
            if through_new < costs[candidate] and _segment_is_free(
                new_node, nodes[candidate], obstacles, robot_radius
            ):
                old_parent = parents[candidate]
                children[old_parent].discard(candidate)
                parents[candidate] = new_index
                costs[candidate] = through_new
                children[new_index].add(candidate)
                update_descendant_costs(candidate)

    goal_candidates = [
        index
        for index, node in enumerate(nodes)
        if np.linalg.norm(node - goal_point) <= goal_radius
        and _segment_is_free(node, goal_point, obstacles, robot_radius)
    ]
    if not goal_candidates:
        node_array = np.asarray(nodes)
        parent_array = np.asarray(parents, dtype=int)
        return RRTStarResult([], node_array, parent_array, math.inf, max_iterations)

    goal_parent = min(
        goal_candidates,
        key=lambda index: costs[index] + float(np.linalg.norm(nodes[index] - goal_point)),
    )
    if np.linalg.norm(nodes[goal_parent] - goal_point) < 1e-12:
        goal_index = goal_parent
    else:
        goal_index = len(nodes)
        nodes.append(goal_point.copy())
        parents.append(goal_parent)
        costs.append(
            costs[goal_parent] + float(np.linalg.norm(goal_point - nodes[goal_parent]))
        )
        children.append(set())
        children[goal_parent].add(goal_index)

    node_array = np.asarray(nodes)
    parent_array = np.asarray(parents, dtype=int)

    path = []
    current = goal_index
    while current >= 0:
        path.append(tuple(float(value) for value in nodes[current]))
        current = parents[current]
    path.reverse()
    path_array = np.asarray(path)
    path_cost = float(np.linalg.norm(np.diff(path_array, axis=0), axis=1).sum())
    return RRTStarResult(path, node_array, parent_array, path_cost, max_iterations)
