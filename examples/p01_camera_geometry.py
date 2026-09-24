"""Project 01: pinhole projection and depth-image unprojection."""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np

from robotlab.perception import CameraIntrinsics, depth_to_points, project_points

from ._plotting import finish_figure


def build_depth_image(height: int = 80, width: int = 120) -> np.ndarray:
    rows, cols = np.mgrid[:height, :width]
    depth = 3.2 + 0.003 * cols + 0.002 * rows
    depth[24:58, 43:77] = 1.45
    depth[8:22, 88:108] = 2.15
    return depth


def run(output: str, show: bool = False) -> None:
    depth = build_depth_image()
    camera = CameraIntrinsics(fx=105.0, fy=105.0, cx=59.5, cy=39.5)
    points = depth_to_points(depth, camera, stride=2)
    pixels = project_points(points, camera)

    figure = plt.figure(figsize=(11, 4.5))
    image_axis = figure.add_subplot(1, 2, 1)
    image = image_axis.imshow(depth, cmap="viridis")
    image_axis.set_title("Metric depth image")
    image_axis.set_xlabel("u [pixel]")
    image_axis.set_ylabel("v [pixel]")
    figure.colorbar(image, ax=image_axis, label="depth [m]")

    cloud_axis = figure.add_subplot(1, 2, 2, projection="3d")
    cloud_axis.scatter(points[:, 0], points[:, 2], -points[:, 1], c=points[:, 2], s=2)
    cloud_axis.set_title("Unprojected point cloud")
    cloud_axis.set_xlabel("x [m]")
    cloud_axis.set_ylabel("z [m]")
    cloud_axis.set_zlabel("-y [m]")
    cloud_axis.view_init(elev=24, azim=-65)
    figure.suptitle(
        f"{len(points)} points; reprojected u=[{pixels[:, 0].min():.1f}, "
        f"{pixels[:, 0].max():.1f}]"
    )
    finish_figure(figure, output, show)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="outputs/p01_camera_geometry.png")
    parser.add_argument("--show", action="store_true")
    arguments = parser.parse_args()
    run(arguments.output, arguments.show)


if __name__ == "__main__":
    main()
