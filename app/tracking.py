from dataclasses import dataclass
from typing import Optional

from .detector import Detection


@dataclass
class TrackedDetection:
    object_id: int
    detection: Detection


class SimpleTracker:
    """
    Lightweight nearest-center tracker.

    This is intentionally simple and optional.
    """

    def __init__(self, max_distance: float = 100.0):
        self.max_distance = max_distance
        self.next_id = 1

        self.previous: list[TrackedDetection] = []

    def update(
        self,
        detections: list[Detection],
    ) -> list[TrackedDetection]:

        results: list[TrackedDetection] = []

        for detection in detections:
            best: Optional[TrackedDetection] = None
            best_distance = float("inf")

            cx, cy = detection.center

            for previous in self.previous:
                if (
                    previous.detection.class_name
                    != detection.class_name
                ):
                    continue

                px, py = previous.detection.center

                distance = (
                    (cx - px) ** 2
                    + (cy - py) ** 2
                ) ** 0.5

                if (
                    distance < self.max_distance
                    and distance < best_distance
                ):
                    best = previous
                    best_distance = distance

            if best is None:
                tracked = TrackedDetection(
                    object_id=self.next_id,
                    detection=detection,
                )
                self.next_id += 1

            else:
                tracked = TrackedDetection(
                    object_id=best.object_id,
                    detection=detection,
                )

            results.append(tracked)

        self.previous = results

        return results