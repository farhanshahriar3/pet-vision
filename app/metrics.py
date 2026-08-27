import time


class Metrics:
    def __init__(self):
        self.total_frames = 0
        self.dogs_detected = 0
        self.cats_detected = 0
        self.total_detections = 0

        self._fps = 0.0
        self._fps_frame_count = 0
        self._fps_start_time = time.monotonic()

    def update(self, detections) -> None:
        self.total_frames += 1
        self._fps_frame_count += 1

        self.total_detections += len(detections)

        for detection in detections:
            if detection.class_name == "dog":
                self.dogs_detected += 1

            elif detection.class_name == "cat":
                self.cats_detected += 1

        now = time.monotonic()
        elapsed = now - self._fps_start_time

        if elapsed >= 1.0:
            self._fps = (
                self._fps_frame_count / elapsed
            )

            self._fps_frame_count = 0
            self._fps_start_time = now

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def frames_processed(self) -> int:
        return self.total_frames