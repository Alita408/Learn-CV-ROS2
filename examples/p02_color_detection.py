"""Project 02: interpretable color segmentation and connected components."""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from robotlab.perception import detect_components, dominant_color_mask
from robotlab.scenes import make_rgb_obstacle_scene

from ._plotting import finish_figure


def run(output: str, show: bool = False) -> None:
    image, _, _ = make_rgb_obstacle_scene()
    mask = dominant_color_mask(image, "red")
    detections = detect_components(mask, label="obstacle", min_area=30)

    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].imshow(image)
    axes[0].set_title(f"Synthetic camera image: {len(detections)} objects")
    for detection in detections:
        left, top, right, bottom = detection.bbox_xyxy
        axes[0].add_patch(
            Rectangle(
                (left, top),
                right - left,
                bottom - top,
                fill=False,
                edgecolor="yellow",
                linewidth=2,
            )
        )
        axes[0].text(left, max(0, top - 2), str(detection.area), color="yellow")
    axes[1].imshow(mask, cmap="gray")
    axes[1].set_title("Dominant-red binary mask")
    for axis in axes:
        axis.set_axis_off()
    finish_figure(figure, output, show)
    for detection in detections:
        print(detection)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="outputs/p02_color_detection.png")
    parser.add_argument("--show", action="store_true")
    arguments = parser.parse_args()
    run(arguments.output, arguments.show)


if __name__ == "__main__":
    main()
