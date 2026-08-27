import threading
import time
from typing import Optional

import cv2
import numpy as np


class Camera:
    def __init__(
        self,
        index: int = 0,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
    ):
        self.index = index
        self.width = width
        self.height = height
        self.fps = fps

        self.cap: Optional[cv2.VideoCapture] = None

        self._latest_frame: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        self.connected = False

    def start(self) -> None:
        if self._running:
            return

        self.cap = cv2.VideoCapture(self.index)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Could not open webcam at index {self.index}."
            )

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        self._running = True
        self.connected = True

        self._thread = threading.Thread(
            target=self._capture_loop,
            daemon=True,
        )
        self._thread.start()

    def _capture_loop(self) -> None:
        while self._running and self.cap is not None:

            success, frame = self.cap.read()

            if not success:
                self.connected = False
                time.sleep(0.1)
                continue

            self.connected = True

            with self._lock:
                self._latest_frame = frame

    def get_frame(self) -> Optional[np.ndarray]:
        with self._lock:
            if self._latest_frame is None:
                return None

            return self._latest_frame.copy()

    def stop(self) -> None:
        self._running = False

        if self._thread is not None:
            self._thread.join(timeout=2.0)

        if self.cap is not None:
            self.cap.release()

        self.cap = None
        self.connected = False

    @property
    def running(self) -> bool:
        return self._running