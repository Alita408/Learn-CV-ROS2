"""Pinhole-camera projection and RGB-D unprojection."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CameraIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float

    def __post_init__(self) -> None:
        if self.fx <= 0.0 or self.fy <= 0.0:
            raise ValueError("fx and fy must be positive")

    @property
    def matrix(self) -> np.ndarray:
        return np.array(
            [[self.fx, 0.0, self.cx], [0.0, self.fy, self.cy], [0.0, 0.0, 1.0]],
            dtype=float,
        )


def project_points(points_xyz: np.ndarray, camera: CameraIntrinsics) -> np.ndarray:
    """Project Nx3 camera-frame points to Nx2 pixel coordinates."""
    points = np.asarray(points_xyz, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points_xyz must have shape (N, 3)")
    if np.any(points[:, 2] <= 0.0):
        raise ValueError("all projected points must have positive z")
    u = camera.fx * points[:, 0] / points[:, 2] + camera.cx
    v = camera.fy * points[:, 1] / points[:, 2] + camera.cy
    return np.column_stack((u, v))


def depth_to_points(
    depth: np.ndarray,
    camera: CameraIntrinsics,
    stride: int = 1,
) -> np.ndarray:
    """Unproject a metric depth image into an Nx3 camera-frame point cloud."""
    image = np.asarray(depth, dtype=float)
    if image.ndim != 2:
        raise ValueError("depth must be a 2-D array")
    if stride < 1:
        raise ValueError("stride must be >= 1")

    v, u = np.mgrid[0 : image.shape[0] : stride, 0 : image.shape[1] : stride]
    z = image[::stride, ::stride]
    valid = np.isfinite(z) & (z > 0.0)
    x = (u - camera.cx) * z / camera.fx
    y = (v - camera.cy) * z / camera.fy
    return np.column_stack((x[valid], y[valid], z[valid]))
