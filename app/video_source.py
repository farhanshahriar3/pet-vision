
from pathlib import Path
from typing import Optional

import cv2
import numpy as np


class VideoSource:
    """
    Base interface for video/image sources.
    """

    def start(self) -> None:
        raise NotImplementedError

    def get_frame(self) -> Optional[np.ndarray]:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

    @property
    def connected(self) -> bool:
        raise NotImplementedError

    @property
    def running(self) -> bool:
        raise NotImplementedError


class VideoFileSource(VideoSource):
    """
    Reads frames from a local video file.

    The source loops when the video reaches the end unless
    loop=False is specified.
    """

    def __init__(
        self,
        path: str,
        loop: bool = True,
    ):
        self.path = Path(path)
        self.loop = loop

        self.cap: Optional[cv2.VideoCapture] = None

        self._running = False
        self._connected = False

    def start(self) -> None:

        if not self.path.exists():
            raise FileNotFoundError(
                f"Video file not found: {self.path}"
            )

        self.cap = cv2.VideoCapture(
            str(self.path)
        )

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Could not open video file: {self.path}"
            )

        self._running = True
        self._connected = True

    def get_frame(self) -> Optional[np.ndarray]:

        if not self._running or self.cap is None:
            return None

        success, frame = self.cap.read()

        if success:
            return frame

        # Video reached the end.
        if self.loop:
            self.cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                0,
            )

            success, frame = self.cap.read()

            if success:
                return frame

        self._connected = False
        self._running = False

        return None

    def stop(self) -> None:

        self._running = False

        if self.cap is not None:
            self.cap.release()

        self.cap = None
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def running(self) -> bool:
        return self._running


class ImageSource(VideoSource):
    """
    Displays a single image repeatedly.

    This is useful for testing YOLO detection without
    having a webcam or video file.
    """

    def __init__(
        self,
        path: str,
    ):
        self.path = Path(path)

        self._frame: Optional[np.ndarray] = None
        self._running = False
        self._connected = False

    def start(self) -> None:

        if not self.path.exists():
            raise FileNotFoundError(
                f"Image file not found: {self.path}"
            )

        frame = cv2.imread(
            str(self.path)
        )

        if frame is None:
            raise RuntimeError(
                f"Could not read image: {self.path}"
            )

        self._frame = frame
        self._running = True
        self._connected = True

    def get_frame(self) -> Optional[np.ndarray]:

        if not self._running:
            return None

        if self._frame is None:
            return None

        return self._frame.copy()

    def stop(self) -> None:

        self._running = False
        self._connected = False
        self._frame = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def running(self) -> bool:
        return self._running


def create_video_source(
    source_type: str,
    path: Optional[str] = None,
    camera_index: int = 0,
    width: int = 1280,
    height: int = 720,
    fps: int = 30,
):
    """
    Create the appropriate input source.

    source_type:
        camera
        video
        image
    """

    if source_type == "camera":

        # Import here to avoid circular imports.
        from .camera import Camera

        return Camera(
            index=camera_index,
            width=width,
            height=height,
            fps=fps,
        )

    if source_type == "video":

        if not path:
            raise ValueError(
                "A video path is required."
            )

        return VideoFileSource(
            path=path,
            loop=True,
        )

    if source_type == "image":

        if not path:
            raise ValueError(
                "An image path is required."
            )

        return ImageSource(
            path=path,
        )

    raise ValueError(
        f"Unknown source type: {source_type}"
    )

