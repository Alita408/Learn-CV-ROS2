"""A transparent baseline for segmentation and connected-component detection."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass(frozen=True)
class Detection:
    label: str
    bbox_xyxy: Tuple[int, int, int, int]
    area: int
    centroid_xy: Tuple[float, float]


_CHANNELS = {"red": 0, "green": 1, "blue": 2}


def dominant_color_mask(
    image_rgb: np.ndarray,
    color: str,
    min_intensity: int = 120,
    dominance: int = 45,
) -> np.ndarray:
    """Segment pixels whose selected RGB channel clearly dominates the others."""
    image = np.asarray(image_rgb)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image_rgb must have shape (H, W, 3)")
    if color not in _CHANNELS:
        raise ValueError("color must be one of: red, green, blue")

    selected = _CHANNELS[color]
    others = [index for index in range(3) if index != selected]
    values = image.astype(np.int16)
    primary = values[..., selected]
    return (
        (primary >= min_intensity)
        & (primary - values[..., others[0]] >= dominance)
        & (primary - values[..., others[1]] >= dominance)
    )


def detect_components(
    mask: np.ndarray,
    label: str = "object",
    min_area: int = 20,
) -> List[Detection]:
    """Return 4-connected components as detections, without OpenCV."""
    binary = np.asarray(mask, dtype=bool)
    if binary.ndim != 2:
        raise ValueError("mask must be a 2-D array")
    if min_area < 1:
        raise ValueError("min_area must be >= 1")

    height, width = binary.shape
    visited = np.zeros_like(binary, dtype=bool)
    detections: List[Detection] = []

    for row in range(height):
        for col in range(width):
            if not binary[row, col] or visited[row, col]:
                continue
            queue = deque([(row, col)])
            visited[row, col] = True
            pixels = []
            while queue:
                current_row, current_col = queue.popleft()
                pixels.append((current_row, current_col))
                for delta_row, delta_col in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    next_row = current_row + delta_row
                    next_col = current_col + delta_col
                    if (
                        0 <= next_row < height
                        and 0 <= next_col < width
                        and binary[next_row, next_col]
                        and not visited[next_row, next_col]
                    ):
                        visited[next_row, next_col] = True
                        queue.append((next_row, next_col))

            if len(pixels) < min_area:
                continue
            rows = np.fromiter((pixel[0] for pixel in pixels), dtype=int)
            cols = np.fromiter((pixel[1] for pixel in pixels), dtype=int)
            detections.append(
                Detection(
                    label=label,
                    bbox_xyxy=(
                        int(cols.min()),
                        int(rows.min()),
                        int(cols.max()) + 1,
                        int(rows.max()) + 1,
                    ),
                    area=len(pixels),
                    centroid_xy=(float(cols.mean()), float(rows.mean())),
                )
            )

    return sorted(detections, key=lambda detection: detection.area, reverse=True)
