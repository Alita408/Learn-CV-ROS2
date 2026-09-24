from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


def finish_figure(figure, output: str, show: bool) -> Path:
    path = Path(output).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=150, bbox_inches="tight")
    print(f"saved: {path}")
    if show:
        plt.show()
    plt.close(figure)
    return path
