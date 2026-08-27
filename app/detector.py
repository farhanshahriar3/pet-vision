from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO


@dataclass
class Detection:
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]

    @property
    def center(self) -> tuple[int, int]:
        x1, y1, x2, y2 = self.bbox
        return (
            int((x1 + x2) / 2),
            int((y1 + y2) / 2),
        )

    @property
    def width(self) -> int:
        x1, _, x2, _ = self.bbox
        return x2 - x1

    @property
    def height(self) -> int:
        _, y1, _, y2 = self.bbox
        return y2 - y1


class AnimalDetector:
    def __init__(
        self,
        model_name: str,
        confidence_threshold: float = 0.60,
        target_classes: list[str] | None = None,
        device: str = "auto",
        inference_size: int = 640,
    ):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.target_classes = set(
            target_classes or ["dog", "cat"]
        )
        self.device = self._resolve_device(device)
        self.inference_size = inference_size

        self.model = YOLO(model_name)

    @staticmethod
    def _resolve_device(device: str) -> str:
        if device.lower() == "auto":
            return "cpu"

        return device

    def detect(self, frame: np.ndarray) -> list[Detection]:
        results = self.model.predict(
            source=frame,
            conf=self.confidence_threshold,
            imgsz=self.inference_size,
            device=self.device,
            verbose=False,
        )

        detections: list[Detection] = []

        if not results:
            return detections

        result = results[0]

        if result.boxes is None:
            return detections

        names: dict[int, str] = result.names

        for box in result.boxes:
            cls_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())

            class_name = names.get(cls_id, str(cls_id))

            if class_name not in self.target_classes:
                continue

            if confidence < self.confidence_threshold:
                continue

            xyxy = box.xyxy[0].cpu().numpy().astype(int)

            x1, y1, x2, y2 = map(int, xyxy)

            detections.append(
                Detection(
                    class_name=class_name,
                    confidence=confidence,
                    bbox=(x1, y1, x2, y2),
                )
            )

        return detections

    def draw(
        self,
        frame: np.ndarray,
        detections: list[Detection],
        show_boxes: bool = True,
        show_confidence: bool = True,
    ) -> np.ndarray:

        output = frame.copy()

        colors: dict[str, tuple[int, int, int]] = {
            "dog": (255, 100, 50),
            "cat": (50, 220, 100),
        }

        for detection in detections:
            x1, y1, x2, y2 = detection.bbox

            color = colors.get(
                detection.class_name,
                (255, 255, 255),
            )

            if show_boxes:
                cv2.rectangle(
                    output,
                    (x1, y1),
                    (x2, y2),
                    color,
                    2,
                )

            if show_confidence:
                label = (
                    f"{detection.class_name.upper()} "
                    f"{detection.confidence * 100:.0f}%"
                )

                cv2.putText(
                    output,
                    label,
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2,
                    cv2.LINE_AA,
                )

        return output