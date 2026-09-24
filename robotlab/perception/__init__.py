"""Perception primitives."""

from .color import Detection, detect_components, dominant_color_mask
from .geometry import CameraIntrinsics, depth_to_points, project_points

__all__ = [
    "CameraIntrinsics",
    "Detection",
    "depth_to_points",
    "detect_components",
    "dominant_color_mask",
    "project_points",
]
