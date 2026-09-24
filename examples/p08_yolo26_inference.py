"""Optional project 08: run a current real-time detector (downloads weights/image once)."""

from __future__ import annotations

import argparse
from pathlib import Path


def run(source: str, output: str, model_name: str = "yolo26n.pt") -> None:
    try:
        from ultralytics import YOLO
    except ImportError as error:
        raise SystemExit(
            "This optional project needs modern-vision dependencies. Run: "
            "python -m pip install -e \".[modern-vision]\""
        ) from error

    model = YOLO(model_name)
    result = model.predict(source=source, imgsz=640, conf=0.25, verbose=False)[0]
    path = Path(output).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    result.save(filename=str(path))
    count = 0 if result.boxes is None else len(result.boxes)
    print(f"model={model_name} detections={count} saved={path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="https://ultralytics.com/images/bus.jpg")
    parser.add_argument("--model", default="yolo26n.pt")
    parser.add_argument("--output", default="outputs/p08_yolo26_inference.jpg")
    arguments = parser.parse_args()
    run(arguments.source, arguments.output, arguments.model)


if __name__ == "__main__":
    main()
